import os
import json
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pymorphy3
import string

morph = pymorphy3.MorphAnalyzer()
russian_stopwords = stopwords.words('russian')

def process_text(text):
    tokens = word_tokenize(text.lower(), language='russian')
    processed = []
    for token in tokens:
        if token.isalpha() and token not in russian_stopwords:
            lemma = morph.parse(token)[0].normal_form
            processed.append(lemma)
    return processed

def build_inverted_index(input_dir='processed_pages'):
    inverted_index = defaultdict(list)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            doc_id = filename.split('_')[2].split('.')[0]  
            with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
                text = f.read()
                words = set(process_text(text))
                
                for word in words:
                    inverted_index[word].append(doc_id)
    
    sorted_index = dict(sorted(inverted_index.items()))
    return sorted_index

def save_index(index, filename='inverted_index.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

def load_index(filename='inverted_index.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def boolean_search(query, index):
    query = query.replace('И', '&').replace('ИЛИ', '|').replace('НЕ', '!')
    
    tokens = query.split()
    
    stack = []
    current_op = None
    
    for token in tokens:
        if token in ('&', '|'):
            current_op = token
        elif token == '!':
            current_op = token
        else:
            word = token.lower()
            docs = set(index.get(word, []))
            
            if current_op == '!':
                all_docs = set()
                for v in index.values():
                    all_docs.update(v)
                docs = all_docs - docs
                current_op = None
            
            stack.append(docs)
            
            if current_op and len(stack) >= 2:
                b = stack.pop()
                a = stack.pop()
                if current_op == '&':
                    stack.append(a & b)
                elif current_op == '|':
                    stack.append(a | b)
                current_op = None
    
    return sorted(stack[-1]) if stack else []

def main():
    if not os.path.exists('inverted_index.json'):
        print("Построение инвертированного индекса...")
        index = build_inverted_index()
        save_index(index)
        print("Индекс сохранен в inverted_index.json")
    
    index = load_index()
    
    while True:
        query = input("\nВведите поисковый запрос (или 'exit' для выхода): ")
        if query.lower() == 'exit':
            break
        
        result = boolean_search(query, index)
        print(f"\nРезультаты поиска для '{query}':")
        if result:
            print(f"Найдено в документах: {', '.join(result)}")
        else:
            print("Документы не найдены")

if __name__ == '__main__':
    main()
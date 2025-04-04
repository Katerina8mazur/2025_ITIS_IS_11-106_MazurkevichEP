import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from pymorphy3 import MorphAnalyzer

russian_stopwords = stopwords.words('russian')
morph = MorphAnalyzer()

def process_document(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    tokens = word_tokenize(text.lower(), language='russian')
    
    processed_words = []
    for token in tokens:
        if token.isalpha() and token not in russian_stopwords and len(token) > 2:
            lemma = morph.parse(token)[0].normal_form
            processed_words.append(lemma)
    
    return ' '.join(processed_words)

def process_all_documents(input_dir='pages', output_dir='processed_pages'):
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f'processed_{filename}')
            
            processed_text = process_document(input_path)
            
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(processed_text)
            
            print(f'Обработан: {filename}')

if __name__ == '__main__':
    process_all_documents()  
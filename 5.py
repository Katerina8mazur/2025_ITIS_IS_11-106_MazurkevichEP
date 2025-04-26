import math
import csv
from collections import defaultdict
from pymorphy3 import MorphAnalyzer

def load_index_files():
    index = {}
    with open("index.txt", 'r', encoding='utf-8') as f:
        for line in f:
            doc_id, url = line.strip().split('\t')
            index[doc_id] = url

    idf = {}
    with open('idf.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  
        for row in reader:
            idf[row[0]] = float(row[1])
    
    
    tfidf = defaultdict(dict)
    with open('tfidf.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        doc_ids = next(reader)[1:]  
        for row in reader:
            term = row[0]
            for doc_id, weight in zip(doc_ids, row[1:]):
                if float(weight) > 0:
                    tfidf[doc_id][term] = float(weight)
    
    return index, idf, tfidf

def process_query(query, morph, idf):
    tokens = query.lower().split()
    lemmas = [morph.parse(token)[0].normal_form for token in tokens]

    term_counts = defaultdict(int)
    for lemma in lemmas:
        term_counts[lemma] += 1

    query_vec = {}
    for lemma, count in term_counts.items():
        if lemma in idf:
            tf = count / len(lemmas)
            query_vec[lemma] = tf * idf[lemma]

    return query_vec

def cosine_similarity(query_vec, doc_vec):
    dot_product = sum(query_vec[term] * doc_vec.get(term, 0) for term in query_vec)
    query_norm = math.sqrt(sum(v**2 for v in query_vec.values()))
    doc_norm = math.sqrt(sum(v**2 for v in doc_vec.values()))

    if query_norm == 0 or doc_norm == 0:
        return 0
    return dot_product / (query_norm * doc_norm)

def search(query, tfidf, idf, morph):
    query_vec = process_query(query, morph, idf)
    if not query_vec:
        return []

    scores = []
    for doc_id, doc_vec in tfidf.items():
        score = cosine_similarity(query_vec, doc_vec)
        if (score > 0):
            scores.append((doc_id, score))

    return sorted(scores, key=lambda x: x[1], reverse=True)

def print_results(index, results):
    if not results:
        print("Ничего не найдено")
        return
    
    print("\nРезультаты поиска:")
    print("Вес      | №  | Ссылка")
    print("---------------------------")
    for (doc_id, score) in results:
        print(f"{score:.6f} | {doc_id:2} | {index[doc_id]}")

def main():
    morph = MorphAnalyzer()
    print("Загрузка поисковых индексов...")
    index, idf, tfidf = load_index_files()
    
    print(f"Индексы загружены. Документов: {len(index)}, Терминов: {len(tfidf)}")

    predefined_queries = [
        "цветок",
        "солнце",
        "ночь",
        "цветок солнце",
        "цветок солнце ночь"
    ]

    print("Примеры поисковых запросов:")
    for query in predefined_queries:
        print(f"\nЗапрос: {query}")
        results = search(query, tfidf, idf, morph)
        print_results(index, results)

    print("Введите поисковый запрос (или 'exit' для выхода):")
    
    
    while True:
        query = input("\n> ").strip()
        if query.lower() == 'exit':
            break
        
        results = search(query, tfidf, idf, morph)
        print_results(index, results)

if __name__ == '__main__':
    main()

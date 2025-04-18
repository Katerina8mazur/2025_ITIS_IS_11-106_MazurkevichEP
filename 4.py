import os
import math
import csv
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pymorphy3

morph = pymorphy3.MorphAnalyzer()

def build_stats(input_dir='processed_pages'):
    term_doc_counts = defaultdict(dict)  
    doc_lengths = {}  
    all_terms = set()
    all_docs = set()
    total_docs = 0

    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            total_docs += 1
            doc_id = filename.split('_')[2].split('.')[0]
            all_docs.add(doc_id)
            
            with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
                words = f.read().split()
                doc_lengths[doc_id] = len(words)
                
                term_counts = defaultdict(int)
                for word in words:
                    term_counts[word] += 1
                    all_terms.add(word)
                
                for word, count in term_counts.items():
                    term_doc_counts[word][doc_id] = count

    sorted_docs = sorted(all_docs, key=lambda x: int(x))
    sorted_terms = sorted(all_terms)
    
    return term_doc_counts, doc_lengths, sorted_terms, sorted_docs, total_docs

def calculate_metrics(term_doc_counts, doc_lengths, total_docs):
    idf = {
        term: math.log(total_docs / len(docs)) 
        for term, docs in term_doc_counts.items()
    }
    
    tf = defaultdict(dict)
    tfidf = defaultdict(dict)
    
    for term, docs in term_doc_counts.items():
        for doc_id, count in docs.items():
            tf[term][doc_id] = count / doc_lengths[doc_id]
            tfidf[term][doc_id] = tf[term][doc_id] * idf[term]
    
    return tf, idf, tfidf

def save_tf_tfidf(data, filename, columns):
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Term'] + columns)
        
        for term in sorted(data.keys()):
            row = [term]
            for doc_id in columns:
                row.append(f"{data[term].get(doc_id, 0):.6f}")
            writer.writerow(row)

def save_idf(idf_data, filename, terms):
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Term', 'IDF'])
        
        for term in terms:
            if term in idf_data:
                writer.writerow([term, f"{idf_data[term]:.6f}"])

def main():
    term_doc_counts, doc_lengths, all_terms, all_docs, total_docs = build_stats()
    
    tf, idf, tfidf = calculate_metrics(term_doc_counts, doc_lengths, total_docs)
    
    save_tf_tfidf(tf, 'tf.csv', all_docs)
    save_idf(idf, 'idf.csv', all_terms)
    save_tf_tfidf(tfidf, 'tfidf.csv', all_docs)
    
    print("Файлы успешно сохранены:")
    print(f"- tf.csv (документов: {len(all_docs)}, терминов: {len(all_terms)})")
    print(f"- idf.csv (терминов: {len(idf)})")
    print(f"- tfidf.csv")

if __name__ == '__main__':
    main()
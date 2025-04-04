import os
import argparse
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
import urllib3
from queue import Queue

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
RUSSIAN_LETTERS = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')

def is_russian(text):
    total_chars = len(text)
    if total_chars == 0:
        return False
    
    russian_count = len([char for char in text if char in RUSSIAN_LETTERS])
    return (russian_count / total_chars) > 0.5

def get_links(soup, url):
    links = set()
    for link in soup.find_all('a', href=True):
        full_url = urljoin(url, link['href'])
        parsed = urlparse(full_url)
        parsed = parsed._replace(query="", fragment="")
        clean_url = parsed.geturl()
        if is_valid(clean_url):
            links.add(clean_url)
    return links

def is_valid(url):
    parsed = urlparse(url)
    return parsed.scheme in ['http', 'https']

def clean_html(soup, html):
    for tag in soup(['script', 'style']):
        tag.decompose()
    return ' '.join(soup.stripped_strings)

def save_page(soup, url, num):
    os.makedirs("pages", exist_ok=True)

    text = clean_html(soup, url)
        
    if len(text.split()) >= 1000 and is_russian(text):
        with open(Path("pages") / f'page_{num}.txt', 'w', encoding='utf-8') as file:
            file.write(text)
        with open('index.txt', 'a', encoding='utf-8') as file:
            file.write(f'{num}\t{url}\n')
        print(f'Сохранено: page_{num}.txt - {url}')
        return True

def crawl(start_urls):
    visited = set() 
    queue = Queue() 
    count = 0

    for url in start_urls:
        queue.put(url)

    while queue and count < 100:
        url = unquote(queue.get()) 
        if url not in visited:
            visited.add(url)

            try:
                page = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=5, verify=False)
                soup = BeautifulSoup(page.text, 'html.parser')

                if save_page(soup, url, count+1):
                    count += 1
                
                for new_url in get_links(soup, url): 
                    queue.put(new_url)
            except:
                print(f'Не получилось загрузить: {url}')
    
    print(f'\nГотово! Скачано страниц: {count}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('urls', nargs="+")
    args = parser.parse_args()
    
    crawl(start_urls=args.urls)
import requests
from bs4 import BeautifulSoup
import json
import time
import os

BASE_URL = "https://indiankanoon.org"
ACT_URL = "https://indiankanoon.org/doc/789969/"
OUTPUT_FILE = "data_pipeline/raw_act.jsonl"

def fetch_act_links():
    print(f"Fetching Act TOC from {ACT_URL}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(ACT_URL, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching TOC: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    links = []
    
    # Indian Kanoon TOC usually has links in a specific div or list
    # We look for links that look like /doc/12345/ inside the main content
    # This is a heuristic; might need adjustment based on actual page structure
    for a in soup.find_all('a', href=True):
        href = a['href']
        if isinstance(href, list):
            href = href[0]
        if href.startswith('/doc/') and 'Income Tax Act' not in a.text: # Avoid self-links if any
             # We want section links. Usually they are like /doc/12345/
             # We can filter by text content to ensure it's a section
             if "Section" in a.text or "Article" in a.text or True: # Get all links for now
                 links.append({
                     'title': a.text.strip(),
                     'url': BASE_URL + href
                 })
    
    # Remove duplicates
    unique_links = {v['url']: v for v in links}.values()
    return list(unique_links)

def fetch_section_text(url):
    print(f"Fetching {url}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the main content. Indian Kanoon usually puts it in <div class="doc_content"> or similar
        # Inspecting typical Indian Kanoon pages: <div class="judgments"> or similar for acts
        # For statutes, it might be different. Let's try to get the main text.
        content_div = soup.find('div', {'class': 'doc_content'}) or soup.find('div', {'class': 'judgments'})
        
        if content_div:
            return content_div.get_text(separator="\n", strip=True)
        else:
            return soup.get_text(separator="\n", strip=True) # Fallback
            
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    links = fetch_act_links()
    print(f"Found {len(links)} potential section links.")
    
    # Limit to first 20 for testing/prototype to avoid hammering the server
    links = links[:20] 
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for link in links:
            text = fetch_section_text(link['url'])
            if text:
                record = {
                    'title': link['title'],
                    'url': link['url'],
                    'text': text
                }
                f.write(json.dumps(record) + "\n")
            time.sleep(1) # Polite delay

if __name__ == "__main__":
    if not os.path.exists("data_pipeline"):
        os.makedirs("data_pipeline")
    main()

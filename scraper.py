import time

import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import CharacterTextSplitter


def scrape_news(vectorstore, text_splitter):
    while True:
        try:
            response = requests.get('https://news.ycombinator.com')
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.select('.storylink')[:5]:  # Get top 5 stories
                title = item.text
                url = item['href']
                article_response = requests.get(url)
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                article_text = article_soup.get_text()
                
                # Process and add to vectorstore
                docs = text_splitter.split_text(article_text)
                vectorstore.add_texts(docs, metadatas=[{"source": url} for _ in docs])
            
            time.sleep(3600)  # Sleep for 1 hour before next scrape
        except Exception as e:
            print(f"Error in scraping: {e}")
            time.sleep(300)  # If error, wait 5 minutes before retrying
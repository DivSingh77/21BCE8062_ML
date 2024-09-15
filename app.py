import os
import threading
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

load_dotenv()

app = Flask(__name__)

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CHROMA_PERSIST_DIRECTORY = os.getenv('CHROMA_PERSIST_DIRECTORY', 'langchain_store')
RATE_LIMIT = int(os.getenv('RATE_LIMIT', 5))
CACHE_EXPIRATION = int(os.getenv('CACHE_EXPIRATION', 3600))  # 1 hour

# Initialize Chroma
embeddings = OpenAIEmbeddings(openai_api_key='OPENAI_API_KEY')
vectorstore = Chroma(CHROMA_PERSIST_DIRECTORY, embeddings)

# Initialize text splitter
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

def scrape_news():
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
                vectorstore.add_texts(docs, metadatas=[{"source": url, "type": "article"} for _ in docs])
            
            time.sleep(3600)  # Sleep for 1 hour before next scrape
        except Exception as e:
            print(f"Error in scraping: {e}")
            time.sleep(300)  # If error, wait 5 minutes before retrying

# Start scraping in background
scrape_thread = threading.Thread(target=scrape_news)
scrape_thread.start()

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/search', methods=['POST'])
def search():
    start_time = time.time()
    
    data = request.json
    user_id = data.get('user_id')
    text = data.get('text', '')
    top_k = data.get('top_k', 5)
    threshold = data.get('threshold', 0.5)
    
    # Check rate limit (using Chroma as storage)
    user_requests = vectorstore.get(f"user:{user_id}:requests")
    if not user_requests:
        user_requests = 0
    user_requests += 1
    if user_requests > RATE_LIMIT:
        return jsonify({"error": "Rate limit exceeded"}), 429
    vectorstore.add_texts([str(user_requests)], metadatas=[{"type": "user_requests"}], ids=[f"user:{user_id}:requests"])
    
    # Check cache (using Chroma as cache)
    cache_key = f"search:{text}:{top_k}:{threshold}"
    cached_result = vectorstore.get(cache_key)
    if cached_result:
        return jsonify({"results": cached_result[0], "cached": True})
    
    # Perform search
    results = vectorstore.similarity_search_with_score(text, k=top_k)
    filtered_results = [
        {"content": doc.page_content, "source": doc.metadata['source'], "score": score}
        for doc, score in results
        if score >= threshold and doc.metadata.get('type') == 'article'
    ]
    
    # Cache result
    vectorstore.add_texts([str(filtered_results)], metadatas=[{"type": "cache", "expiration": time.time() + CACHE_EXPIRATION}], ids=[cache_key])
    
    end_time = time.time()
    inference_time = end_time - start_time
    
    # Log the request
    app.logger.info(f"User {user_id} searched for '{text}'. Inference time: {inference_time:.2f}s")
    
    return jsonify({"results": filtered_results, "inference_time": inference_time})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

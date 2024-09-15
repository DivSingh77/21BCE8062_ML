import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    CHROMA_PERSIST_DIRECTORY = os.getenv('CHROMA_PERSIST_DIRECTORY', 'langchain_store')
    RATE_LIMIT = int(os.getenv('RATE_LIMIT', 5))
    CACHE_EXPIRATION = int(os.getenv('CACHE_EXPIRATION', 3600))  # 1 hour
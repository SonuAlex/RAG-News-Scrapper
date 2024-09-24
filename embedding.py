from dotenv import load_dotenv
import ollama
import pymongo
import os

load_dotenv()

# MongoDB client setup
client = pymongo.MongoClient(os.environ.get("MONGODB_STRING_CONNECTION"))
db = client['search_data']
collection = db['HT_scraper_data']

hf_token = os.environ.get("HF_TOKEN")
embedding_url = os.environ.get("HF_EMBEDDING_URL")

def generate_embedding(text : str) -> list[float]:
    response = ollama.embeddings(
        model='all-minilm',
        prompt=text,
    )
    
    embedding = response["embedding"]
    return embedding

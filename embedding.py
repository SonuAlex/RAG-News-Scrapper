from dotenv import load_dotenv
import pymongo
import requests
import os

load_dotenv()

# MongoDB client setup
client = pymongo.MongoClient(os.environ.get("MONGODB_STRING_CONNECTION"))
db = client['search_data']
collection = db['HT_scraper_data']

hf_token = os.environ.get("HF_TOKEN")
embedding_url = os.environ.get("HF_EMBEDDING_URL")

def generate_embedding(text : str) -> list[float]:
    response = requests.post(
        embedding_url,
        headers={'Authorization': f'Bearer {hf_token}'},
        json = {'inputs': text}
    )

    if response.status_code != 200:
        raise ValueError(f"Request failed with status code {response.status_code} : {response.text}")
    
    return response.json()
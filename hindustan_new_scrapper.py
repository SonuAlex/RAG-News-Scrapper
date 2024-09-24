from dotenv import load_dotenv
from bs4 import BeautifulSoup
import logging
import embedding
import pymongo
import requests
import os

load_dotenv()

logging.basicConfig(filename='scrapper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MongoDB client setup
client = pymongo.MongoClient(os.environ.get("MONGODB_STRING_CONNECTION"))
db = client['search_data']
collection = db['HT_scraper_data']
advancedCollection = db['HT_scraper_data_advanced']

def find_invalid_embeddings():
    # Aggregation pipeline to find documents where the embedding field does not have 768 elements
    pipeline = [
        {"$match": {"embedding": {"$exists": True}}},
        {"$project": {"embedding_length": {"$size": "$embedding"}}},
        {"$match": {"embedding_length": {"$ne": 768}}}
    ]

    invalid_embeddings = list(collection.aggregate(pipeline))

    if invalid_embeddings:
        print(f"Found {len(invalid_embeddings)} document(s) with invalid embedding length:")
        for doc in invalid_embeddings:
            print(f"Document ID: {doc['_id']}, Embedding Length: {doc['embedding_length']}")
    else:
        print("No documents found with invalid embedding length.")

def check_for_duplicates():
    # Field to check for duplicates
    field_to_check = "link"  # Change this to the field you want to check for duplicates

    # Aggregation pipeline to group by the field and count occurrences
    pipeline = [
        {"$group": {"_id": f"${field_to_check}", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ]

    duplicates = list(collection.aggregate(pipeline))

    if duplicates:
        print(f"Found {len(duplicates)} duplicate(s) based on the '{field_to_check}' field:")
        for duplicate in duplicates:
            print(f"Value: {duplicate['_id']}, Count: {duplicate['count']}")
    else:
        print(f"No duplicates found based on the '{field_to_check}' field.")

def embbed_news():
    a = 0
    print('Embedding news data...')
    logging.info('Embedding news data...')
    for news in collection.find():
        if "embedding" not in news:
            a += 1
            try:
                news_embedding = embedding.generate_embedding(news["title"])
            except Exception as e:
                logging.error(f"Failed to generate embedding for {news['title']}: {e}")
                # print(f"Failed to generate embedding for {news['title']}: {e}")
                continue
            collection.update_one(
                {"link": news["link"]},
                {"$set": {"embedding": news_embedding}}
            )
    print('Embedding news data completed.')
    print(f"Total news embedded: {a}")
    logging.info('Embedding news data completed.')
    logging.info(f"Total news embedded: {a}")

def update_embeddings():
    a = 0
    print('Embedding news data...')
    logging.info('Embedding news data...')
    for news in collection.find():
        a += 1
        try:
            news_embedding = embedding.generate_embedding(news["title"])
            collection.update_one(
                {'link': news['link']},  # Empty filter to match all documents
                {"$set": {"embedding": news_embedding}},  # Set the embedding data
                upsert=True  # Insert the document if it does not exist
            )
        except Exception as e:
            # print(f"Failed to generate embedding for {news['title']}: {e}")
            logging.error(f"Failed to generate embedding for {news['title']}: {e}")
            continue
    
    print('Embedding news data completed.')
    print(f"Total news embedded: {a}")
    logging.info('Embedding news data completed.')
    logging.info(f"Total news embedded: {a}")

def migrate_data():
    a = 0
    print('Migrating news data...')
    logging.info('Migrating news data...')
    for news in collection.find():
        a += 1
        try:
            advancedCollection.update_one(
                {'link': news['link']},  # Empty filter to match all documents
                {"$set": news},  # Set the embedding data
                upsert=True  # Insert the document if it does not exist
            )
        except Exception as e:
            print(f"Failed to migrate data for {news['title']}: {e}")
            logging.error(f"Failed to migrate data for {news['title']}: {e}")
            continue
    
    print('Migrating news data completed.')
    print(f"Total news migrated: {a}")
    logging.info('Migrating news data completed.')
    logging.info(f"Total news migrated: {a}")

def getNewsData():
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }
    response = requests.get(
        f"https://www.hindustantimes.com/latest-news", headers=headers
    )
    soup = BeautifulSoup(response.content, "html.parser")
    news_results = []

    print('Scraping Hindustan Times...')
    logging.info('Scraping Hindustan Times...')
    for el in soup.select("div.cartHolder"):
        news_item = {
                "link": "https://www.hindustantimes.com" + el.find("a")["href"],
                "title": el.select_one("h3.hdg3 a").get_text(),
                "date": el.select_one("div.dateTime").get_text(),
                "source": el.select_one(".secName a").get_text()
            }
        news_results.append(news_item)

        # Insert or update the data in MongoDB
        collection.update_one(
            {"link": news_item["link"]},    # Filter to find existing document
            {"$set": news_item},    # Update the document with new data
            upsert=True   # Insert a new document if no matching document found
        )
    logging.info('Scraping Hindustan Times completed.')
    print('Scraping Hindustan Times completed.')

    # os.system('ollama pull all-minilm')
    embbed_news()

getNewsData()
# find_invalid_embeddings()
# update_embeddings()
# migrate_data()
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import embedding
import pymongo
import requests
import os

load_dotenv()

# MongoDB client setup
client = pymongo.MongoClient(os.environ.get("MONGODB_STRING_CONNECTION"))
db = client['search_data']
collection = db['HT_scraper_data']

def embbed_news():
    print('Embedding news data...')
    for news in collection.find():
        if "embedding" not in news:
            try:
                news_embedding = embedding.generate_embedding(news["title"])
            except Exception as e:
                print(f"Failed to generate embedding for {news['title']}: {e}")
                continue
            collection.update_one(
                {"link": news["link"]},
                {"$set": {"embedding": news_embedding}}
            )
    print('Embedding news data completed.')
 
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
    print('Scraping Hindustan Times completed.')

    embbed_news()

getNewsData()
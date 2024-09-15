from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime
import logging
import embedding as em
import pymongo
import uvicorn
import os

load_dotenv()

# Configure logging
logging.basicConfig(filename='api.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MongoDB client setup
try:
    client = pymongo.MongoClient(os.environ.get("MONGODB_STRING_CONNECTION"))
    db = client["search_data"]
    search_collection = db["search_data"]
    collection = db["HT_scraper_data"]
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")
    raise

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})
    log_message = f"{request.method} {request.url} - Status: {response.status_code}"
    logging.info(log_message)
    return response

@app.get("/health", summary="Health Check", description="Returns the health status of the application.")
def API_Status():
    try:
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})
    
@app.get("/search")
def search(user_id: str, text: str, top_k: int, threshold: float):
    try:
        user_data = search_collection.find_one({"user_id": user_id})
        if user_data and user_data["search_count"] >= 5:
            log_message = f"Search limit exceeded - user_id: {user_id}"
            logging.warning(log_message)
            return {"message": "Search limit exceeded."}

        log_message = f"Search request - user_id: {user_id}, text: {text}, top_k: {top_k}, threshold: {threshold}"
        logging.info(log_message)

        # Update search data
        search_entry = {
            "text": text,
            "top_k": top_k,
            "threshold": threshold,
            "timestamp": datetime.now().isoformat()
        }

        if user_data:
            search_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"search_count": 1}, "$push": {"searches": search_entry}}
            )
        else:
            search_collection.insert_one({
                "user_id": user_id,
                "search_count": 1,
                "searches": [search_entry]
            })

        embedded_query = em.generate_embedding(text)
        results = collection.aggregate([
            {
                "$vectorSearch": {
                    "queryVector": embedded_query,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": top_k,
                    "index": "PlotSemanticSearch",
                }
            }
        ])
        res = []
        for result in results:
            res.append(
                {
                    "link": result["link"],
                    "title": result["title"],
                    "date": result["date"],
                    "source": result["source"]
                }
            )
        return res
    except Exception as e:
        logging.error(f"Error processing search request: {e}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

# Defining the search request model
class SearchRequest(BaseModel):
    user_id: str
    text: str
    top_k: int
    threshold: float

    
@app.post("/search")
def search_post(request: SearchRequest):
    try:
        # Checking user search limit
        user_data = search_collection.find_one({"user_id": request.user_id})
        if user_data and user_data["search_count"] >= 5:
            log_message = f"Search limit exceeded - user_id: {request.user_id}"
            logging.warning(log_message)
            return {"message": "Search limit exceeded."}

        # Logging the search request
        log_message = f"Search request - user_id: {request.user_id}, text: {request.text}, top_k: {request.top_k}, threshold: {request.threshold}"
        logging.info(log_message)

        # Update search data
        search_entry = {
            "text": request.text,
            "top_k": request.top_k,
            "threshold": request.threshold,
            "timestamp": datetime.now().isoformat()
        }

        # Insert or update the search data
        if user_data:
            search_collection.update_one(
                {"user_id": request.user_id},
                {"$inc": {"search_count": 1}, "$push": {"searches": search_entry}}
            )
        else:
            search_collection.insert_one({
                "user_id": request.user_id,
                "search_count": 1,
                "searches": [search_entry]
            })

        embedded_query = em.generate_embedding(request.text)
        results = collection.aggregate([
            {
                "$vectorSearch": {
                    "queryVector": embedded_query,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": request.top_k,
                    "index": "PlotSemanticSearch",
                }
            }
        ])
        res = []
        for result in results:
            res.append(
                {
                    "link": result["link"],
                    "title": result["title"],
                    "date": result["date"],
                    "source": result["source"]
                }
            )
        return res
    except Exception as e:
        logging.error(f"Error processing search request: {e}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
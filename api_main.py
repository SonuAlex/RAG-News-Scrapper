from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from pymongo import MongoClient
import logging
import uvicorn

# Configure logging
logging.basicConfig(filename='api.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MongoDB client setup
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["search_data"]
    search_collection = db["search_data"]
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

@app.get("/search&user_id={user_id}&text={text}&top_k={top_k}&threshold={threshold}")
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

        return {"user_id": user_id, "text": text, "top_k": top_k, "threshold": threshold}
    except Exception as e:
        logging.error(f"Error processing search request: {e}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
from fastapi import FastAPI, Request
import logging
import uvicorn

# Configure logging
logging.basicConfig(filename='api.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    log_message = f"{request.method} {request.url} - Status: {response.status_code}"
    logging.info(log_message)
    return response

@app.get("/health")
def API_Status():
    return "API is up and running"

@app.get("/search&user_id={user_id}&text={text}&top_k={top_k}&threshold={threshold}")
def search(user_id: str, text: str, top_k: int, threshold: float):
    log_message = f"Search request - user_id: {user_id}, text: {text}, top_k: {top_k}, threshold: {threshold}"
    logging.info(log_message)
    # Your search logic here
    return {"user_id": user_id, "text": text, "top_k": top_k, "threshold": threshold}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
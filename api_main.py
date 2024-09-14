from fastapi import FastAPI, Request
import logging
import uvicorn

app = FastAPI()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
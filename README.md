# AI Intern Task for Trademarkia
The task is to build a backend for efficient document retrieval. This project is coded in `Python`. In the backend, I have included all the required endpoints. The project is fully complete with a working database and embedding model.

## Features
- ### API:
    - It has a fully functional `health` and `search` endpoints. I have included both `GET` and `POST` for the `search` endpoint for flexible use of either one.
    - Added a **logging system** to keep record of the *inference time* and *requests*, also logs the *errors* that have occured through use of the API.
    - Implemented a NoSQL MongoDB Database to record the number of queries made by the user and to limit the number of requests to 5.
    - Handled all possible known errors with a `try...except` block and logs the errors when they have occurred.

- ### Embedding:
    - I have used a embedding model from **Hugging Face** called the `
all-MiniLM-L6-v2` using its Inference API.
    - The embedding model creates vector embeddings of dimension `384`
    - For quering the **promt** given, I have used `DotProduct` to find the similarity and `KNNVector` to find the results.
    - For this, I have taken the assistance of `MongoDB Atlas`

- ### Web Scraping:
    - I have taken the newsletters from `The Hindustan Times`
    - I have scraped data such as `Link`, `Headlines`, `Date`, and `Source`

- ### Database:
    - For the database, all the data is available in the MongoDB cloud database.
    - I have also used MongoDB's `Atlas Search` to **Fine-tune** the search results.

- ### Logging:
    - I have created a logging functionality to log all the requests and their inference time, including any errors that may have happened through the API
    - The logs are stored in the `api.log` file

## Installation
The libraries that are to be installed to run this are:
- `fastapi`
- `pymongo`
- `uvicorn`
- `pydantic`
- `beautifulsoup4`
- `requests`

## Usage
- The `api_main.py` has the api backend and it run using the `FastAPI` framework.
- The `hindustan_new_scrapper.py` does the scrapping and stores in the **MongoDB cloud**
- The `embedding.py` does the embedding process and the vectors are stored in the MongoDB cloud database in the same JSON file as the newsletter

## Note
All the API keys in this project is free-tiered and have a limit of queries that can be set to them. Please use them cautiously
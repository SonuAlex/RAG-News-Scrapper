# AI Intern Task for Trademarkia
The task is to build a backend for efficient document retrieval. This project is coded in `Python`. In the backend, I have included all the required endpoints.

## Features
- ### API:
    - It has a fully functional `health` and `search` endpoints. I have included both `GET` and `POST` for the `search` endpoint for flexible use of either one.
    - Added a **logging system** to keep record of the *inference time* and *requests*, also logs the *errors* that have occured through use of the API.
    - Implemented a NoSQL MongoDB Database to record the number of queries made by the user and to limit the number of requests to 5.
    - Handled all possible known errors with a `try...except` block and logs the errors when they have occurred.

- ### Embedding:
    - 
- ### Web Scraping:
    - 

## Installation
The libraries that are to be installed to run this are:
- `fastapi`
- `pymongo`
- `uvicorn`
- `pydantic`

## Usage
- Explain how to use your project and provide examples

## Contributing
- Guidelines for contributing to your project

## License
- Specify the license under which your project is distributed

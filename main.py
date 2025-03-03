from app.configurations.exception import CustomException
from app.configurations.logging import logging
import os, sys
import uvicorn
from fastapi import FastAPI
from app.api.v1 import api_router
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

app = FastAPI()

app.include_router(api_router, prefix="/api/v1")

# Initialize caching (InMemoryBackend for simplicity)
@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

if __name__ == "__main__":
    try:
        app.debug = True
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except CustomException as e:
        logging.Error(e)

from app.configurations.exception import CustomException
from app.configurations.logging import logging
import os,sys
import uvicorn
from fastapi import FastAPI
from app.api.v1 import api_router


app = FastAPI()

app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    app.debug = True
    uvicorn.run(app, host="0.0.0.0", port=8000)


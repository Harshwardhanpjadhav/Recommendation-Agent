import sys
from app.configurations.exception import CustomException
from app.configurations.logging import logging
from app.configurations.mongodb.connect import ConnectMongoDB
from app.constants.mongodb_constant import DATABASE_NAME, COLLECTION_NAME
from app.api.schemas.user_creation import *

from fastapi import APIRouter

router = APIRouter()


@router.get("/user-details")
async def signup():
    try:
        db = ConnectMongoDB(DATABASE_NAME)
        gym_collection = db.get_collection(COLLECTION_NAME)
        data = gym_collection.find({"gym_email":"harshwardhanpj2001@gmail.com"})
        return list(data)
    except Exception as e:
        raise CustomException(e,sys)

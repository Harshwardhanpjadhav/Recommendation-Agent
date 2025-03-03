import sys
from app.configurations.exception import CustomException
from app.configurations.logging import logging
from app.configurations.mongodb.connect import ConnectMongoDB
from app.api.schemas.user_details import *
from app.components.user_details import UsersDetail

from fastapi import APIRouter

router = APIRouter()


@router.post("/user-details")
async def signup(data:UserProfile):
    try:
        user_details = UsersDetail()
        response = user_details.add_users_details(data)
        return response
    except Exception as e:
        raise CustomException(e,sys)

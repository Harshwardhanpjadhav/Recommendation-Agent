from app.configurations.exception import CustomException
from app.configurations.logging import logging

from fastapi import APIRouter
from app.api.v1.routes import user_details


api_router = APIRouter()


api_router.include_router(user_details.router, prefix="/user", tags=['user details input'])


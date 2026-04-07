from fastapi import APIRouter
from app.api.v1.webhook import router as github_router
from app.core.config import settings

# This is the master router for the entire API
api_router = APIRouter()

# Include the webhook router under the /webhooks prefix
api_router.include_router(
    github_router, 
    prefix="/webhooks", 
    tags=["Webhooks"]
)


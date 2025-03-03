from app.components.recommendation import Recommendation

from fastapi import FastAPI, HTTPException

from fastapi import APIRouter

router = APIRouter()
recommendation_cache = {}


@router.get("/recommendations/")
def get_recommendations(user_id: str):
    """
    Endpoint to retrieve recommendations based on the user's profile.
    """
    rec =Recommendation(user_id)
    jobs,news = rec.get_recommendation()
    return {"user_id": user_id, "Jobs": jobs,"News": news}
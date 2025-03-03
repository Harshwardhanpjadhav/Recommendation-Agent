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
    rec =Recommendation()

    # Check for cached recommendations.
    if user_id in recommendation_cache:
        return {"user_id": user_id, "recommendations": recommendation_cache[user_id]}
    
    # profile = user_profiles[user_id]
    recommendations = rec.generate_recommendations()
    recommendation_cache[user_id] = recommendations
    return {"user_id": user_id, "recommendations": recommendations}
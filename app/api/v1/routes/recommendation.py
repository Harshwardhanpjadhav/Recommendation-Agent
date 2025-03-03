from app.components.recommendation import Recommendation
from fastapi import APIRouter, HTTPException, Request
from fastapi_cache.decorator import cache

router = APIRouter()

# Custom key builder: now accepts *args and **kwargs.
def recommendation_cache_key_builder(func, namespace: str, request: Request, response, *args, **kwargs):
    user_id = request.query_params.get("user_id", "default")
    return f"{namespace}:{user_id}"

@router.get("/recommendations/")
@cache(expire=60, key_builder=recommendation_cache_key_builder)
async def get_recommendations(user_id: str, request: Request):
    """
    Endpoint to retrieve recommendations based on the user's profile.
    The result is cached for 60 seconds per user.
    """
    try:
        rec = Recommendation(user_id)
        jobs, news = rec.get_recommendation()
        return {"user_id": user_id, "Jobs": jobs, "News": news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

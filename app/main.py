import uvicorn
from fastapi import FastAPI

from app.core.config import settings
from app.db.session import init_db
from app.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
)

# Include the main API router
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/health",tags=['Infrastructure'])
async def health_check():
    return {"status": "online", "mode": "Code Agent"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# app/db/session.py
import aiosqlite
from app.core.config import settings

async def get_db():
    """Dependency for FastAPI routes."""
    db = await aiosqlite.connect(settings.DATABASE_URL)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

async def init_db():
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        # We store the task, its current status, and the final generated code
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                description TEXT,
                plan TEXT,
                status TEXT DEFAULT 'pending',
                generated_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
# app/db/repository.py
from aiosqlite import Connection
from typing import Optional, List, Any

class TaskRepository:
    def __init__(self, db: Connection):
        self.db = db

    async def create_task(self, task_id: str, description: str):
        query = "INSERT OR IGNORE INTO tasks (id, description) VALUES (?, ?)"
        await self.db.execute(query, (task_id, description))
        await self.db.commit()

    async def update_task_status(self, task_id: str, status: str, plan: str = None):
        query = "UPDATE tasks SET status = ?, plan = ? WHERE id = ?"
        await self.db.execute(query, (status, plan, task_id))
        await self.db.commit()

    async def save_result(self, task_id: str, code: str):
        query = "UPDATE tasks SET status = 'completed', generated_code = ? WHERE id = ?"
        await self.db.execute(query, (code, task_id))
        await self.db.commit()

    async def get_task(self, task_id: str):
        query = "SELECT * FROM tasks WHERE id = ?"
        async with self.db.execute(query, (task_id,)) as cursor:
            return await cursor.fetchone()
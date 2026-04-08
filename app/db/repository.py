# app/db/repository.py
from aiosqlite import Connection
from typing import Optional, List, Any

class TaskRepository:
    def __init__(self, db: Connection):
        self.db = db

    async def create_task(self, task_id: str, description: str, project_id: str):
        # Good use of INSERT OR IGNORE
        query = "INSERT OR IGNORE INTO tasks (id, description, project_id, status) VALUES (?, ?, ?, ?)"
        await self.db.execute(query, (task_id, description, project_id, "pending"))
        await self.db.commit()

    async def update_task_status(self, task_id: str, status: str, plan: str = None):
        # FIX: We don't update project_id here. It's set at creation and shouldn't change.
        # This prevents accidental NULL overwrites.
        query = "UPDATE tasks SET status = ?, plan = ? WHERE id = ?"
        await self.db.execute(query, (status, plan, task_id))
        await self.db.commit()

    async def save_result(self, task_id: str, code: str):
        # FIX: Just update the code and status. Keep the original project_id intact.
        query = "UPDATE tasks SET status = 'completed', generated_code = ? WHERE id = ?"
        await self.db.execute(query, (code, task_id))
        await self.db.commit()

    async def get_task(self, task_id: str):
        # FIX: task_id should be unique. Searching by just ID is safer 
        # unless you have duplicate IDs across different projects.
        query = "SELECT * FROM tasks WHERE id = ?"
        async with self.db.execute(query, (task_id,)) as cursor:
            row = await cursor.fetchone()
            return row
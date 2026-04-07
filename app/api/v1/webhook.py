from fastapi import APIRouter, Depends, Header, BackgroundTasks, Response, status
from aiosqlite import Connection

from app.schemas.github import GitHubPayload
from app.db.session import get_db
from app.db.repository import TaskRepository
from app.services.github.github_service import gh_service
# Import your brain/graph entry point here
# from app.services.graph.workflow import app_brain 

router = APIRouter()

from app.services.graph.workflow import app_brain

async def process_bot_task(issue_number: int, task_id: str, description: str, db_conn: Connection):
    # 1. Post GitHub Comment
    await gh_service.post_comment(issue_number, f"🤖 **Bot** is starting work on `{task_id}`...")

    # 2. Trigger the LangGraph Brain
    initial_state = {
        "task_id": task_id,
        "issue_description": description,
        "plan": [],
        "status": "initialized"
    }
    
    # This runs through Planner -> Coder -> Writes File
    result = await app_brain.ainvoke(initial_state)
    
    # 3. Final GitHub Update
    await gh_service.post_comment(
        issue_number, 
        f"✅ **Work Complete!** Generated file: `{result['current_file']}`"
    )
    print(f"🏁 [BOT] Task {task_id} completed successfully.")


@router.post("/github", status_code=status.HTTP_202_ACCEPTED)
async def handle_github_webhook(
    payload: GitHubPayload, 
    background_tasks: BackgroundTasks,
    db: Connection = Depends(get_db),
    x_github_event: str = Header(None)
):
    # 1. Validation
    if x_github_event != "issues":
        return {"status": "ignored_event"}

    if payload.action not in ["opened", "edited", "labeled"]:
        return {"status": "ignored_action"}

    # 2. Title Prefix Check
    trigger_prefix = "[bot]"
    if not payload.issue.title.strip().startswith(trigger_prefix):
        return {"status": "ignored_no_prefix"}

    task_id = f"GH-{payload.issue.number}"
    description = f"{payload.issue.title}: {payload.issue.body or ''}"

    # 3. Persistence (Keep this in the main flow to ensure we don't lose the task)
    repo = TaskRepository(db)
    await repo.create_task(task_id, description)
    print(f"🎯 [bot] Target Acquired: {task_id}")

    # 4. Hand off the slow work to the Background
    background_tasks.add_task(process_bot_task, payload.issue.number, task_id, description, db)

    return {"status": "accepted", "task_id": task_id}
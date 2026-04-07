from fastapi import APIRouter, Depends, Header, BackgroundTasks
from aiosqlite import Connection


from app.schemas.github import GitHubPayload
from app.db.session import get_db
from app.db.repository import TaskRepository
from app.services.github.github_service import gh_service



router = APIRouter()

@router.post("/github")
async def handle_github_webhook(
    payload: GitHubPayload, 
    background_tasks: BackgroundTasks,
    db: Connection = Depends(get_db),
    x_github_event: str = Header(None)
):
    # 1. Check if it's an issue assignment
    if x_github_event != "issues":
        return {"status": "ignored"}

    if payload.action not in ["opened", "edited", "labeled"]:
        return {"status": "ignored_action"}

    # 3. THE TITLE GATEKEEPER
    trigger_prefix = "[bot]"
    
    if not payload.issue.title.strip().startswith(trigger_prefix):
        print(f"⏭️ Skipping: Issue '{payload.issue.title}' does not have the {trigger_prefix} prefix.")
        return {"status": "ignored_no_prefix"}

    task_id = f"GH-{payload.issue.number}"
    description = f"{payload.issue.title}: {payload.issue.body or ''}"

    repo = TaskRepository(db)
    await repo.create_task(task_id, description)

    # 4. Target Acquired
    print(f"🎯 [bot] Prefix detected! Starting work on {task_id}")

    # 2. Test Outbound Connection
    success = await gh_service.post_comment(
        payload.issue.number, 
        f"🚀 **Code Agent Engine** has initialized state for `{task_id}`. Starting reasoning flow..."
    )

    if success:
        print(f"💬 [GitHub] Comment posted successfully on Issue #{payload.issue.number}")
    else:
        print(f"❌ [GitHub] Failed to post comment. Check your GITHUB_TOKEN.")
    
    # ... Proceed to save to DB and trigger Brain ...
    return {"status": "accepted", "task_id": task_id}

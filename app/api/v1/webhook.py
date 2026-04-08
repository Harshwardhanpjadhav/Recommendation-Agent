from fastapi import APIRouter, Depends, Header, BackgroundTasks, Response, status,Request
from aiosqlite import Connection

from app.schemas.github import GitHubPayload
from app.db.session import get_db
from app.db.repository import TaskRepository
from app.services.github.github_service import gh_service

router = APIRouter()

from app.services.graph.workflow import app_brain

import docker
client = docker.from_env()

async def process_bot_task(issue_number, task_id, description, db_conn, payload):
    container_name = f"laminar_session_{task_id.lower()}"
    volume_name = f"laminar_volume_{payload.repository.name.lower()}"
    
    print(f"🐳 [BOT] Booting live session: {container_name}")
    
    # 1. Start the Live Container (detach=True keeps it running in the background)
    container = client.containers.run(
        image="python:3.10-slim",
        command="tail -f /dev/null", # 👈 The magic command to keep it awake forever
        name=container_name,
        volumes={volume_name: {'bind': '/workspace', 'mode': 'rw'}},
        working_dir="/workspace",
        detach=True
    )
    
    try:
        # Optional: Run a quick setup command to install git/pytest in the background
        container.exec_run("apt-get update && apt-get install -y git && pip install pytest fastapi httpx pydantic")

        # 2. Trigger the ReAct Loop
        initial_state = {
            "task_id": task_id,
            "project_id": payload.repository.name,
            "issue_description": description,
            "container_name": container_name,
            "messages": [] # The graph will fill this in
        }
        
        # The AI will now loop, running terminal commands until it finishes
        result = await app_brain.ainvoke(initial_state)
        
        # 3. Optional: Add Git Push logic here now that the AI is done!
        
    finally:
        # 4. ALWAYS clean up the live container, even if the AI crashes
        print(f"🧹 [BOT] Shutting down live session: {container_name}")
        container.stop()
        container.remove()

@router.post("/github", status_code=status.HTTP_202_ACCEPTED)
async def handle_github_webhook(
    request: Request, 
    background_tasks: BackgroundTasks,
    db: Connection = Depends(get_db),
    x_github_event: str = Header(None)
):
    if x_github_event != "issues":
        return {"status": "ignored_event"}

    data = await request.json()
    
    # 🚨 THE LOOP BREAKER: Ignore anything done by a Bot
    sender_type = data.get("sender", {}).get("type")
    if sender_type == "Bot":
        print("🤖 [WEBHOOK] Ignoring activity from another bot (or myself).")
        return {"status": "ignored_bot_activity"}

    try:
        payload = GitHubPayload(**data)
    except Exception as e:
        return {"status": "validation_failed"}

    # 🚨 RE-EVALUATE ACTIONS: 
    # Usually, you only want to start on 'opened'. 
    # 'edited' is dangerous because comments can trigger it.
    if payload.action not in ["opened", "reopened"]:
        return {"status": "ignored_action"}

    trigger_prefix = "[bot]"
    if not payload.issue.title.strip().startswith(trigger_prefix):
        return {"status": "ignored_no_prefix"}

    task_id = f"GH-{payload.issue.number}"
    description = f"{payload.issue.title}: {payload.issue.body or ''}"

    # 4. Persistence
    repo = TaskRepository(db)
    await repo.create_task(task_id, description, payload.repository.name)
    print(f"🎯 [bot] Target Acquired: {task_id}")

    # 5. Hand off to Background
    background_tasks.add_task(
        process_bot_task, 
        payload.issue.number, 
        task_id, 
        description, 
        db, 
        payload
    )

    return {"status": "accepted", "task_id": task_id}
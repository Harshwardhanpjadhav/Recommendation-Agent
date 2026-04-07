import os
from git import Repo
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# ONLY import from state, never from workflow
from app.services.graph.state import AgentState 
from app.core.config import settings
from app.services.file_manager.file_manager import FileManager
# Pointing to OpenRouter
llm = ChatOpenAI(
    model=settings.OPENROUTER_MODEL_NAME,
    openai_api_key=settings.OPENROUTER_API_KEY,
    openai_api_base=settings.OPENROUTER_BASE_URL,
    default_headers={
        "HTTP-Referer": "http://localhost:8000", # OpenRouter requirement
        "X-Title": "Bot Engine",
    }
)

async def planner_node(state: AgentState):
    print(f"🧠 [BOT] Brain (via OpenRouter) reasoning about: {state['task_id']}")
    
    prompt = f"Analyze this GitHub issue and provide a technical plan: {state['issue_description']}"
    
    # The call remains the same because OpenRouter is OpenAI-compatible
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    return {
        "plan": response.content.strip().split("\n"),
        "status": "planning_complete"
    }



from app.services.file_manager.file_manager import FileManager

file_manager = FileManager()

async def coder_node(state: AgentState):
    """
    Step 2: The 'Hands'. 
    The LLM writes actual code based on the plan created in Step 1.
    """
    print(f"💻 [BOT] Coder is writing implementation for: {state['task_id']}")

    coder_prompt = f"""
    You are an expert Python Developer. Based on the following plan, write the full Python code.
    PLAN: {state['plan']}
    ISSUE: {state['issue_description']}
    
    Return ONLY the raw code. No markdown, no triple backticks, no explanations.
    """

    response = await llm.ainvoke([HumanMessage(content=coder_prompt)])
    generated_code = response.content.strip()

    # Define a filename based on the task
    filename = f"generated_{state['task_id'].replace('-', '_').lower()}.py"
    
    # Write to disk
    file_manager.write_file(filename, generated_code)
    
    return {
        "code_snippet": generated_code,
        "current_file": filename,
        "status": "code_written"
    }


from git import Repo
import os
from app.core.config import settings

async def git_node(state: AgentState):
    """
    Step 4: The 'Delivery'. 
    Commits the code and pushes it to a new branch on GitHub.
    """
    print(f"🌿 [BOT] Starting Git delivery for {state['task_id']}...")
    
    # Path to your local repository
    repo_path = os.getcwd() 
    repo = Repo(repo_path)
    
    # Create a unique branch name
    branch_name = f"bot/fix-{state['task_id'].lower()}"
    
    try:
        # 1. Create and switch to new branch
        # If branch exists, we just switch to it
        if branch_name in repo.heads:
            repo.git.checkout(branch_name)
        else:
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
        
        # 2. Stage all changes (the files created by coder_node)
        repo.git.add(A=True)
        
        # 3. Commit
        repo.index.commit(f"🤖 [BOT] Implementation for {state['task_id']}")
        
        # 4. Push to GitHub (Requires GITHUB_TOKEN in your git remote)
        print(f"📤 [BOT] Pushing branch {branch_name} to origin...")
        origin = repo.remote(name='origin')
        
        # We ensure the remote URL has the token for authentication
        remote_url = f"https://{settings.GITHUB_TOKEN}@github.com/{settings.GITHUB_REPO_OWNER}/{settings.GITHUB_REPO_NAME}.git"
        origin.set_url(remote_url)
        
        origin.push(branch_name)
        
        return {
            "current_file": branch_name,
            "status": "pushed_to_github"
        }
        
    except Exception as e:
        print(f"❌ [BOT] Git Error: {str(e)}")
        return {"status": "git_failed"}


async def context_node(state: AgentState):
    """
    The 'Eyes' of the bot. Scans the local directory.
    """
    print(f"🔍 [BOT] Context Node: Scanning project structure...")
    
    # List all files in your current project (ignoring hidden folders)
    excluded = {'.git', '__pycache__', 'venv', '.env', 'laminar.db', 'bot_sandbox'}
    files_found = []
    
    for root, dirs, files in os.walk("."):
        # Modify dirs in-place to skip excluded folders
        dirs[:] = [d for d in dirs if d not in excluded]
        for file in files:
            files_found.append(os.path.relpath(os.path.join(root, file), "."))
            
    print(f"📂 [BOT] Found {len(files_found)} files for context.")
    
    return {
        "repo_files": files_found,
        "status": "context_retrieved"
    }
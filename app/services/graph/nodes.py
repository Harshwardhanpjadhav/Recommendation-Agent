import os
import docker
from git import Repo
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage,SystemMessage

from app.services.graph.state import AgentState 
from app.core.config import settings
from app.services.github.github_service import gh_service
from app.services.graph.tools import get_agent_tools


client = docker.from_env()

# Pointing to OpenRouter
llm = ChatOpenAI(
    model=settings.OPENROUTER_MODEL_NAME,
    openai_api_key=settings.OPENROUTER_API_KEY,
    # openai_api_base=settings.OPENROUTER_BASE_URL,
    # default_headers={
    #     "HTTP-Referer": "http://localhost:8000",
    #     "X-Title": "Bot Engine",
    # }
)


async def agent_node(state: AgentState):
    print("🧠 [BOT] Analyzing state and deciding next move...")
    
    # Generate the tools specifically for this task's container
    print("Container name: ", state["container_name"])
    tools = get_agent_tools(state["container_name"])
    llm_with_tools = llm.bind_tools(tools)
    
    messages = state.get("messages", [])

    print("Messages: ", messages)
    
    # Inject the system prompt if starting fresh
    if not any(isinstance(m, SystemMessage) for m in messages):
        sys_prompt = SystemMessage(content=f"""
        You are an elite Autonomous Software Engineer. 
        You are working inside a live Linux terminal container: {state['container_name']}
        
        YOUR TASK: {state['issue_description']}
        
        RULES & WORKFLOW:
        1. EXPLORE: Use `execute_shell` (e.g., `ls -la`, `pwd`) to understand the workspace.
        2. READ: Use `read_file_with_lines` to inspect existing code before changing it.
        3. WRITE/EDIT: 
           - Use `write_new_file` for brand new files.
           - Use `str_replace_editor` for surgical edits to existing files.
        4. TEST: Always use `execute_shell` to run tests (e.g., `pytest`, `python -m py_compile`).
        5. FIX: If tests fail, read the exact error output, adjust your code, and test again.
        6. FINISH: When everything works perfectly, output a final markdown summary of your fixes. Do NOT call a tool to finish.
        """)
        messages = [sys_prompt] + messages

    print("Messages: ", messages)

    response = await llm_with_tools.ainvoke(messages)
    print(response)
    return {"messages": [response]}

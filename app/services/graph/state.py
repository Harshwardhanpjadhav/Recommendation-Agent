from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    task_id: str
    project_id: str
    issue_description: str
    container_name: str 
    messages: Annotated[list, add_messages]
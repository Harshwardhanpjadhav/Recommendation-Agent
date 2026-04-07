from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    task_id: str
    issue_description: str
    plan: Annotated[List[str], operator.add]
    repo_files: List[str]
    current_file: str  # This will store the branch name after Git Node
    code_snippet: str
    status: str
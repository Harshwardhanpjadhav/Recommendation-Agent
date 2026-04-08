from pydantic import BaseModel, Field
from typing import Optional, Any

class GitHubIssue(BaseModel):
    number: int
    title: str
    body: Optional[str] = None  # Body can be null/empty

class Repository(BaseModel):
    name: str

    
class GitHubPayload(BaseModel):
    action: str
    issue: GitHubIssue
    repository: Repository
    # Add 'Extra' to ignore all the other fields GitHub sends (sender, repo, etc.)
    class Config:
        extra = "ignore"
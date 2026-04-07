from pydantic import BaseModel, Field
from typing import Optional, Any

class GitHubIssue(BaseModel):
    number: int
    title: str
    body: Optional[str] = None  # Body can be null/empty

class GitHubPayload(BaseModel):
    action: str
    issue: GitHubIssue
    # Add 'Extra' to ignore all the other fields GitHub sends (sender, repo, etc.)
    class Config:
        extra = "ignore"
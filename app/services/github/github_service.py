import httpx
from app.core.config import settings

class GitHubService:
    def __init__(self):
        self.headers = {
            "Authorization": f"token {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.base_url = f"https://api.github.com/repos/{settings.GITHUB_REPO_OWNER}/{settings.GITHUB_REPO_NAME}"

    async def get_issue_comments(self, issue_number: int):
        """Fetches comments to get more context if needed."""
        url = f"{self.base_url}/issues/{issue_number}/comments"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            return response.json()

    async def post_comment(self, issue_number: int, body: str):
        """Allows the agent to say 'I am working on this' on GitHub."""
        url = f"{self.base_url}/issues/{issue_number}/comments"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json={"body": body})
            return response.status_code == 201

    async def create_branch(self, branch_name: str):
        """Creates a new branch for the fix (Advanced)."""
        # We will implement this once we start coding!
        pass

    # In app/services/github/github_service.py
    async def create_pull_request(self, title: str, body: str, head: str, base: str = "main"):
        url = f"{self.base_url}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        async with httpx.AsyncClient() as client:
            # IMPORTANT: Ensure self.headers includes "Accept": "application/vnd.github+json"
            response = await client.post(url, headers=self.headers, json=data)
            return response.json()

gh_service = GitHubService()
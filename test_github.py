import httpx
import asyncio
from app.core.config import settings

async def test_connection():
    headers = {
        "Authorization": f"token {settings.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"https://api.github.com/repos/{settings.GITHUB_REPO_OWNER}/{settings.GITHUB_REPO_NAME}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            print(f"✅ Success! Connected to: {response.json()['full_name']}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.json())

if __name__ == "__main__":
    asyncio.run(test_connection())
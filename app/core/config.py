from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "code-agent"
    PROJECT_VERSION: str = "1.0.0"
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"


    OPENAI_API_KEY: str
    GITHUB_TOKEN: str
    DATABASE_URL: str

    # GitHub Credentials
    GITHUB_TOKEN: str
    GITHUB_REPO_OWNER: str
    GITHUB_REPO_NAME: str

    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL_NAME: str = "anthropic/claude-3.5-sonnet"
    

settings = Settings()
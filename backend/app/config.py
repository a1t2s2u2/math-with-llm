from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    openai_api_key: str
    workspace_root: Path = Path.cwd() / "workspace"
    llm_model: str = "gpt-5-mini"
    lean_timeout: int = 10
    git_timeout: int = 10
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()

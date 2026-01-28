from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: str
    data_dir: Path = Path("./data")
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-haiku-latest"

    frontend_origin: str = "http://localhost:5173"
    log_level: str = "INFO"

    max_text_length: int = 50_000
    max_url_length: int = 2048
    provider_timeout_seconds: int = 60

    fetch_connect_timeout: float = 10.0
    fetch_read_timeout: float = 15.0
    fetch_max_bytes: int = 5 * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()

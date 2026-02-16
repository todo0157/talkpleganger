from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings."""

    # OpenAI API
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_dalle_model: str = "dall-e-3"

    # App settings
    app_name: str = "톡플갱어 (Talk-pleganger)"
    debug: bool = True

    # Response settings
    max_response_tokens: int = 500
    temperature: float = 0.7

    # Database settings
    database_path: str = "talkpleganger.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

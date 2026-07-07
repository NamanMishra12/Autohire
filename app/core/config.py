from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AutoHire AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str

    LLM_PROVIDER: str = "grok"
    LLM_API_KEY: str
    LLM_BASE_URL: str
    LLM_MODEL: str
    RAPIDAPI_KEY: str = ""

    CHROMA_DB: str = "./chroma"

    UPLOAD_DIR: str = "uploads/resumes"
    GENERATED_DIR: str = "generated"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()

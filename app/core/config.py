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

    JWT_SECRET_KEY: str = "change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
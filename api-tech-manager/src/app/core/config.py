from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "API Tech Manager"
    APP_ENV: str = "dev"

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 dias
    ALLOWED_ORIGINS: List[str] = []

    DATABASE_URL: str = "sqlite:///./data.db"

    MAX_LOGIN_ATTEMPTS: int = 5
    LOCK_MINUTES: int = 15

    UPLOAD_BACKEND: str = "local"  # local | supabase
    UPLOAD_DIR: str = "./uploads"
    SUPABASE_URL: str | None = None
    SUPABASE_ANON_KEY: str | None = None
    SUPABASE_BUCKET: str | None = None

def get_settings() -> Settings:
    # Permite separar por vírgula no .env
    allowed = os.getenv("ALLOWED_ORIGINS")
    settings = Settings()
    if allowed:
        settings.ALLOWED_ORIGINS = [o.strip() for o in allowed.split(",") if o.strip()]
    return settings

settings = get_settings()

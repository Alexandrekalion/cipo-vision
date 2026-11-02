from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"

class Settings(BaseSettings):
    database_url: str = "sqlite:///./cipo_vision_dev.sqlite3"
    dev_auth_enabled: bool = True
    cookie_secure: bool = False
    model_config = SettingsConfigDict(env_file=str(BACKEND_ENV_FILE), extra="ignore")

settings = Settings()

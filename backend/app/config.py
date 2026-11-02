from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./cipo_vision_dev.sqlite3"
    dev_auth_enabled: bool = True
    cookie_secure: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

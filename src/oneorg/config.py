from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    # Database
    database_url: str = "sqlite+aiosqlite:///data/oneorg.db"
    
    # Auth
    secret_key: str = "dev-secret-change-in-production"
    access_token_expire_days: int = 7
    
    # App
    app_name: str = "OneEmployeeOrg Academy"
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

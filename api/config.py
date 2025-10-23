from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/events_cms"
    REDIS_URL: str = "redis://localhost:6379"
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    WP_BASE_URL: Optional[str] = None
    WP_USER: Optional[str] = None
    WP_APP_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()

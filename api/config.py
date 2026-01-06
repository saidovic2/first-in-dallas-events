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
    
    # API Keys
    eventbrite_api_token: Optional[str] = None
    ticketmaster_api_key: Optional[str] = None
    ticketmaster_affiliate_id: Optional[str] = None
    
    # Supabase
    supabase_url: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    
    # FTP
    ftp_host: Optional[str] = None
    ftp_port: Optional[str] = None
    ftp_user: Optional[str] = None
    ftp_password: Optional[str] = None
    ftp_remote_path: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env

settings = Settings()

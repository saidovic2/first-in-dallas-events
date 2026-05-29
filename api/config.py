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

    # Stripe — test keys until Section 4 go-live.
    # IMPORTANT: use price_... IDs (Price IDs), NOT prod_... IDs (Product IDs).
    # This repo tags every Stripe object with metadata product="fid_events" to
    # isolate from the directory's Stripe objects (product="first_in_dallas").
    STRIPE_SECRET_KEY: Optional[str] = None          # sk_test_... / sk_live_...
    STRIPE_WEBHOOK_SECRET: Optional[str] = None      # whsec_...  (separate from directory's)
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None     # pk_test_... / pk_live_...
    STRIPE_PRICE_SINGLE: Optional[str] = None        # price_... one-time $19 single submission
    STRIPE_PRICE_UNLIMITED: Optional[str] = None     # price_... recurring $49/mo subscription
    STRIPE_PRICE_FEATURED: Optional[str] = None      # price_... one-time $29 featured add-on

    # Hub origin — used for Stripe success/cancel redirect URLs
    HUB_URL: str = "http://localhost:3001"

    # fid-main cache revalidation — POST /api/revalidate on firstindallas.com
    # Set the same secret in fid-main's REVALIDATE_SECRET env var.
    FID_MAIN_URL: str = "https://firstindallas.com"
    REVALIDATE_SECRET: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env

settings = Settings()

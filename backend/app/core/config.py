"""
Application configuration and settings
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "BOS Solution"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS
    ALLOWED_HOSTS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "https://308a8c214f1d.ngrok-free.app"],
        env="ALLOWED_HOSTS"
    )
    
    # Database
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./dev.db", env="DATABASE_URL")
    SUPABASE_URL: str = Field(default="", env="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(default="", env="SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="", env="SUPABASE_SERVICE_ROLE_KEY")
    
    # API Keys for social media platforms (add as needed)
    INSTAGRAM_ACCESS_TOKEN: str = Field(default="", env="INSTAGRAM_ACCESS_TOKEN")
    TWITTER_BEARER_TOKEN: str = Field(default="", env="TWITTER_BEARER_TOKEN")
    FACEBOOK_ACCESS_TOKEN: str = Field(default="", env="FACEBOOK_ACCESS_TOKEN")
    LINKEDIN_ACCESS_TOKEN: str = Field(default="", env="LINKEDIN_ACCESS_TOKEN")
    
    # Google/YouTube API
    GOOGLE_API_KEY: str = Field(default="", env="GOOGLE_API_KEY")
    GOOGLE_CLIENT_ID: str = Field(default="", env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", env="GOOGLE_CLIENT_SECRET")
    
    # Monitoring settings
    DEFAULT_SCAN_FREQUENCY_MINUTES: int = Field(default=60, env="DEFAULT_SCAN_FREQUENCY")
    MAX_CONCURRENT_SCANS: int = Field(default=5, env="MAX_CONCURRENT_SCANS")
    
    # Redis (for background tasks)
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields instead of raising an error


# Global settings instance
settings = Settings()

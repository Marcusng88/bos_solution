"""
Configuration settings for the application
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "BOS Solution"
    APP_VERSION: str = "1.0.0"
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # CORS
    ALLOWED_HOSTS: List[str] = Field(
        default=[
            "http://localhost:3000", 
            "http://localhost:3001", 
            "http://127.0.0.1:3000", 
            "http://127.0.0.1:3001",
            "https://5d7a587ce8ba.ngrok-free.app",
            "https://bos-solution.onrender.com",
            "https://bos-solution.vercel.app"
        ],
        env="ALLOWED_HOSTS"
    )
    
    # Database - Using Supabase REST API only
    SUPABASE_URL: str = Field(default="", env="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(default="", env="SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="", env="SUPABASE_SERVICE_ROLE_KEY")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Additional CORS origins (backward compatibility)
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://bos-solution.vercel.app"
    ]
    
    # Social Media API Keys
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "your_instagram_access_token_here")
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "your_twitter_bearer_token_here")
    FACEBOOK_ACCESS_TOKEN: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "your_facebook_access_token_here")
    LINKEDIN_ACCESS_TOKEN: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "your_linkedin_access_token_here")
    
    # API Keys for LLMs and services
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")  # Backward compatibility
    YOUTUBE_API_KEY: Optional[str] = os.getenv("YOUTUBE_API_KEY")
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Google/YouTube API
    GOOGLE_CLIENT_ID: str = Field(default="", env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", env="GOOGLE_CLIENT_SECRET")
    
    # Monitoring settings
    DEFAULT_SCAN_FREQUENCY_MINUTES: int = int(os.getenv("DEFAULT_SCAN_FREQUENCY", "1440"))
    MAX_CONCURRENT_SCANS: int = int(os.getenv("MAX_CONCURRENT_SCANS", "5"))
    
    # Browser settings for browser-use
    BROWSER_HEADLESS: bool = os.getenv("BROWSER_HEADLESS", "True").lower() == "true"
    BROWSER_TIMEOUT: int = int(os.getenv("BROWSER_TIMEOUT", "600"))  # Increased to 10 minutes
    BROWSER_MAX_RETRIES: int = int(os.getenv("BROWSER_MAX_RETRIES", "3"))  # Increased retries
    BROWSER_RETRY_DELAY: int = int(os.getenv("BROWSER_RETRY_DELAY", "10"))  # Increased delay
    BROWSER_LAUNCH_TIMEOUT: int = int(os.getenv("BROWSER_LAUNCH_TIMEOUT", "60"))  # Browser launch timeout
    BROWSER_PAGE_TIMEOUT: int = int(os.getenv("BROWSER_PAGE_TIMEOUT", "60"))  # Page load timeout
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from environment variables
    
    @property
    def gemini_api_key(self) -> Optional[str]:
        """Get Google/Gemini API key with fallback"""
        return self.GOOGLE_API_KEY or self.GEMINI_API_KEY
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key"""
        return self.OPENAI_API_KEY
    
    @property
    def youtube_api_key(self) -> Optional[str]:
        """Get YouTube API key"""
        return self.YOUTUBE_API_KEY


settings = Settings()
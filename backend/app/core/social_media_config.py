"""
Social Media API Configuration
Load API keys from environment variables for secure access
"""

import os
from typing import Optional

class SocialMediaConfig:
    """Configuration for social media API integrations"""
    
    # Facebook/Instagram Configuration
    @staticmethod
    def get_facebook_config() -> dict:
        return {
            "app_id": os.getenv("FACEBOOK_APP_ID"),
            "app_secret": os.getenv("FACEBOOK_APP_SECRET"),
            "default_access_token": os.getenv("FACEBOOK_ACCESS_TOKEN"),
            "api_version": "v18.0"
        }
    
    # Twitter Configuration
    @staticmethod
    def get_twitter_config() -> dict:
        return {
            "api_key": os.getenv("TWITTER_API_KEY"),
            "api_secret": os.getenv("TWITTER_API_SECRET"),
            "bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
            "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
            "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        }
    
    # LinkedIn Configuration
    @staticmethod
    def get_linkedin_config() -> dict:
        return {
            "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
            "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
            "default_access_token": os.getenv("LINKEDIN_ACCESS_TOKEN")
        }
    
    # TikTok Configuration
    @staticmethod
    def get_tiktok_config() -> dict:
        return {
            "client_key": os.getenv("TIKTOK_CLIENT_KEY"),
            "client_secret": os.getenv("TIKTOK_CLIENT_SECRET"),
            "default_access_token": os.getenv("TIKTOK_ACCESS_TOKEN")
        }
    
    # YouTube Configuration
    @staticmethod
    def get_youtube_config() -> dict:
        return {
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET")
        }
    
    @staticmethod
    def validate_config(platform: str) -> bool:
        """Validate that required config exists for a platform"""
        if platform == "facebook" or platform == "instagram":
            config = SocialMediaConfig.get_facebook_config()
            # For testing, just check if we have any config at all
            return bool(config["app_id"] or config["app_secret"] or config["default_access_token"])
        elif platform == "twitter":
            config = SocialMediaConfig.get_twitter_config()
            return bool(config["bearer_token"])
        elif platform == "linkedin":
            config = SocialMediaConfig.get_linkedin_config()
            return bool(config["client_id"] and config["client_secret"])
        elif platform == "tiktok":
            config = SocialMediaConfig.get_tiktok_config()
            return bool(config["client_key"] and config["client_secret"])
        elif platform == "youtube":
            config = SocialMediaConfig.get_youtube_config()
            return bool(config["api_key"])
        return False

# Global instance
social_media_config = SocialMediaConfig()

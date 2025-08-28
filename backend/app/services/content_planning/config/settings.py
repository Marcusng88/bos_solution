"""
Configuration settings for AI Content Planning system
"""

import os
from typing import Dict, List, Any

class ContentPlanningSettings:
    """Configuration settings for content planning agents"""
    
    # Google AI Configuration
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # LLM Settings
    model_name: str = "gemini-2.5-flash-lite"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    
    # Content Generation Settings
    max_posts_per_request: int = 10
    default_hashtag_count: int = 10
    max_content_length: int = 2200
    
    # Vector Store Settings
    vector_store_path: str = "./data/chroma_db"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Industries Configuration
    supported_industries: List[str] = [
        "technology", "fashion_beauty", "food_beverage", "finance_fintech",
        "healthcare_wellness", "automotive", "travel_hospitality", 
        "fitness_sports", "education_elearning", "real_estate_construction"
    ]
    
    # Platform Configuration
    supported_platforms: List[str] = [
        "linkedin", "twitter", "instagram", "facebook", "tiktok", "youtube"
    ]
    
    # Content Types
    content_types: List[str] = [
        "product_announcement", "educational", "promotional", "behind_the_scenes",
        "user_generated", "trending_topic", "industry_news", "company_culture"
    ]
    
    # Tone Options
    tone_options: List[str] = [
        "professional", "casual", "humorous", "inspirational", "urgent",
        "friendly", "authoritative", "playful", "educational", "promotional"
    ]

# Platform-specific settings
PLATFORM_CONFIGS: Dict[str, Dict[str, Any]] = {
    "linkedin": {
        "max_length": 3000,
        "optimal_hashtags": 5,
        "best_times": ["Tuesday-Thursday, 9-11 AM"],
        "content_style": "professional"
    },
    "twitter": {
        "max_length": 280,
        "optimal_hashtags": 3,
        "best_times": ["Monday-Wednesday, 1-3 PM"],
        "content_style": "conversational"
    },
    "instagram": {
        "max_length": 2200,
        "optimal_hashtags": 12,
        "best_times": ["Wednesday-Friday, 6-8 PM"],
        "content_style": "visual_focused"
    },
    "facebook": {
        "max_length": 63206,
        "optimal_hashtags": 5,
        "best_times": ["Tuesday-Thursday, 1-3 PM"],
        "content_style": "community_focused"
    },
    "tiktok": {
        "max_length": 4000,
        "optimal_hashtags": 8,
        "best_times": ["Tuesday-Thursday, 6-10 PM"],
        "content_style": "trendy"
    },
    "youtube": {
        "max_length": 5000,
        "optimal_hashtags": 15,
        "best_times": ["Saturday-Sunday, 2-4 PM"],
        "content_style": "educational"
    }
}

# Industry-specific hashtag pools
INDUSTRY_HASHTAGS: Dict[str, List[str]] = {
    "technology": [
        "#TechInnovation", "#AI", "#CloudComputing", "#Cybersecurity", "#SaaS", 
        "#DigitalTransformation", "#TechNews", "#StartupLife", "#Innovation", 
        "#TechTrends", "#Automation", "#MachineLearning", "#DataScience", "#IoT"
    ],
    "fashion_beauty": [
        "#Fashion", "#Style", "#Beauty", "#OOTD", "#Sustainable", "#Luxury", 
        "#Trendy", "#MakeupTutorial", "#SkinCare", "#FashionWeek", "#Vintage",
        "#StreetStyle", "#BeautyTips", "#FashionTrends"
    ],
    "food_beverage": [
        "#FoodLove", "#Healthy", "#Recipe", "#Organic", "#Delicious", 
        "#FreshIngredients", "#Nutrition", "#Vegan", "#Foodie", "#Cooking",
        "#HealthyEating", "#FarmToTable", "#Sustainability", "#Culinary"
    ],
    "finance_fintech": [
        "#Finance", "#Investing", "#Cryptocurrency", "#FinTech", "#PersonalFinance", 
        "#WealthBuilding", "#Trading", "#Banking", "#Investment", "#Money",
        "#FinancialLiteracy", "#Blockchain", "#DeFi", "#DigitalPayments"
    ],
    "healthcare_wellness": [
        "#Health", "#Wellness", "#MedicalInnovation", "#Fitness", "#MentalHealth", 
        "#Healthcare", "#Nutrition", "#Mindfulness", "#HealthyLiving", "#Medicine",
        "#Telemedicine", "#WellnessTips", "#HealthTech", "#SelfCare"
    ]
}

settings = ContentPlanningSettings()

"""
Main API router - includes all endpoint routers
"""

from fastapi import APIRouter
from app.api.v1.endpoints import competitors, monitoring, users, auth, self_optimization, ai_insights, youtube, user_preferences, social_media

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(competitors.router, prefix="/competitors", tags=["competitors"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(self_optimization.router, prefix="/self-optimization", tags=["self-optimization"])
api_router.include_router(ai_insights.router, prefix="/ai-insights", tags=["ai-insights"])
api_router.include_router(youtube.router, prefix="/youtube", tags=["youtube"])
api_router.include_router(user_preferences.router, prefix="/user-preferences", tags=["user-preferences"])
api_router.include_router(social_media.router, prefix="/social-media", tags=["social-media"])

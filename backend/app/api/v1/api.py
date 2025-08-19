"""
Main API router - includes all endpoint routers
"""

from fastapi import APIRouter
from app.api.v1.endpoints import competitors, monitoring, users, auth, youtube, user_preferences, my_competitors, social_media

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(competitors.router, prefix="/competitors", tags=["competitors"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(youtube.router, prefix="/youtube", tags=["youtube"])
api_router.include_router(user_preferences.router, prefix="/user-preferences", tags=["user-preferences"])
api_router.include_router(my_competitors.router, prefix="/my-competitors", tags=["my-competitors"])
api_router.include_router(social_media.router, prefix="/social-media", tags=["social-media"])

"""
Main API router - includes all endpoint routers
"""

from fastapi import APIRouter
from app.api.v1.endpoints import competitors, monitoring, users, auth, youtube, user_preferences, social_media

api_router = APIRouter()

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Backend is running"}

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(competitors.router, prefix="/competitors", tags=["competitors"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(youtube.router, prefix="/youtube", tags=["youtube"])
api_router.include_router(user_preferences.router, prefix="/user-preferences", tags=["user-preferences"])
api_router.include_router(social_media.router, prefix="/social-media", tags=["social-media"])

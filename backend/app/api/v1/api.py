"""
Main API router - includes all endpoint routers
"""

from fastapi import APIRouter
from app.api.v1.endpoints import competitors, monitoring, users, auth, youtube, user_preferences, social_media, content_planning, self_optimization, ai_insights, roi, roi_updates, pdf_conversion, drafts

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
api_router.include_router(content_planning.router, prefix="/content-planning", tags=["content-planning"])
api_router.include_router(self_optimization.router, prefix="/self-optimization", tags=["self-optimization"])
api_router.include_router(ai_insights.router, prefix="/ai-insights", tags=["ai-insights"])
api_router.include_router(roi.router, prefix="/roi", tags=["roi"])
api_router.include_router(roi_updates.router, prefix="/roi-updates", tags=["roi-updates"])
api_router.include_router(pdf_conversion.router, prefix="/pdf", tags=["pdf"])
api_router.include_router(drafts.router, prefix="/drafts", tags=["drafts"])

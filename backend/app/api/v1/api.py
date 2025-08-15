"""
Main API router - includes all endpoint routers
"""

from fastapi import APIRouter
from app.api.v1.endpoints import competitors, monitoring, users, auth
from app.api.v1.dashboard import router as dashboard_router

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(competitors.router, prefix="/competitors", tags=["competitors"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(dashboard_router, tags=["dashboard"])

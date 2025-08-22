"""
BOS Solution - FastAPI Backend
Continuous Monitoring and Competitor Intelligence System
"""

import sys
import asyncio
import platform
import logging

# Import and setup Windows compatibility early
from app.core.windows_compatibility import setup_windows_compatibility
setup_windows_compatibility()

# Configure logging early - only show essential logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Reduce verbosity of third-party libraries
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path
import importlib.util

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import init_db, get_connection_mode


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    try:
        await init_db()
        connection_mode = get_connection_mode()
        print(f"Database initialized successfully in {connection_mode} mode")
        # Start ROI scheduler (dynamic import due to space in folder name)
        try:
            here = Path(__file__).resolve()
            scheduler_path = here.parent / "app" / "core" / "ROI backend" / "roi" / "services" / "scheduler.py"
            if scheduler_path.exists():
                spec = importlib.util.spec_from_file_location("roi_scheduler", str(scheduler_path))
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    import sys as _sys
                    if spec.name:
                        _sys.modules[spec.name] = mod
                    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
                    if hasattr(mod, "start_scheduler"):
                        mod.start_scheduler()
                        print("ROI scheduler started")
        except Exception as e:
            print(f"ROI scheduler failed to start: {e}")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("⚠️  Application will continue using available connection methods")
    yield
    # Shutdown
    try:
        from app.core.database import close_db
        await close_db()
        print("✅ Database cleanup completed")
    except Exception as e:
        print(f"⚠️  Database cleanup warning: {e}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Business Operations System - Continuous Monitoring and Competitor Intelligence API",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"🌐 Host: {settings.HOST}")
    print(f"🔌 Port: {settings.PORT}")
    print(f"🐛 Debug: {settings.DEBUG}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

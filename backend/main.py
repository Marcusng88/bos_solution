"""
BOS Solution - FastAPI Backend
Continuous Monitoring and Competitor Intelligence System
"""

import sys
import asyncio
import platform
import logging
import threading
import time

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

# Global variable to store the ROI scheduler thread
roi_scheduler_thread = None
roi_scheduler_running = False

def start_roi_scheduler():
    """Start the ROI scheduler in a separate thread"""
    global roi_scheduler_thread, roi_scheduler_running
    
    if roi_scheduler_running:
        print("🔄 ROI scheduler is already running")
        return
    
    try:
        print("🚀 Starting ROI scheduler...")
        
        # Import the ROI scheduler using importlib to handle spaces in folder names
        import importlib.util
        from pathlib import Path
        
        # Get the path to the scheduler file
        backend_path = Path(__file__).parent
        scheduler_path = backend_path / "app" / "core" / "ROI backend" / "roi" / "services" / "scheduler.py"
        
        if not scheduler_path.exists():
            raise ImportError(f"Scheduler file not found at: {scheduler_path}")
        
        # Load the scheduler module
        spec = importlib.util.spec_from_file_location("roi_scheduler", str(scheduler_path))
        if spec and spec.loader:
            scheduler_module = importlib.util.module_from_spec(spec)
            import sys
            if spec.name:
                sys.modules[spec.name] = scheduler_module
            spec.loader.exec_module(scheduler_module)
            
            # Now we can use the functions
            start_scheduler = getattr(scheduler_module, "start_scheduler")
            start_scheduler()
            roi_scheduler_running = True
            print("✅ ROI scheduler started successfully")
        else:
            raise ImportError("Failed to load scheduler module")
        
    except ImportError as e:
        print(f"❌ Failed to import ROI scheduler: {e}")
        print("   Make sure the ROI backend services are properly installed")
        print("   Path should be: app/core/ROI backend/roi/services/")
    except Exception as e:
        print(f"❌ Failed to start ROI scheduler: {e}")
        print("   ROI updates will not be available")

def stop_roi_scheduler():
    """Stop the ROI scheduler"""
    global roi_scheduler_running
    
    if roi_scheduler_running:
        try:
            # Import and stop the scheduler using the same approach
            import importlib.util
            from pathlib import Path
            
            backend_path = Path(__file__).parent
            scheduler_path = backend_path / "app" / "core" / "ROI backend" / "roi" / "services" / "scheduler.py"
            
            if scheduler_path.exists():
                spec = importlib.util.spec_from_file_location("roi_scheduler", str(scheduler_path))
                if spec and spec.loader:
                    scheduler_module = importlib.util.module_from_spec(spec)
                    import sys
                    if spec.name:
                        sys.modules[spec.name] = scheduler_module
                    spec.loader.exec_module(scheduler_module)
                    
                    stop_scheduler = getattr(scheduler_module, "stop_scheduler")
                    stop_scheduler()
                    roi_scheduler_running = False
                    print("🛑 ROI scheduler stopped")
                else:
                    print("⚠️  Could not load scheduler module for stopping")
            else:
                print("⚠️  Scheduler file not found for stopping")
                
        except Exception as e:
            print(f"⚠️  Warning: Could not stop ROI scheduler cleanly: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    try:
        await init_db()
        connection_mode = get_connection_mode()
        print(f"✅ Database initialized successfully in {connection_mode} mode")
        
        # Start ROI scheduler
        start_roi_scheduler()
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("⚠️  Application will continue using available connection methods")
    
    yield
    
    # Shutdown
    try:
        # Stop ROI scheduler
        stop_roi_scheduler()
        
        # Cleanup database
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
    print(f"📊 ROI Scheduler: Will start automatically")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

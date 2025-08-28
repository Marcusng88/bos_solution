"""
Database configuration and dependency injection for Supabase
Replaces SQLAlchemy with direct Supabase client usage
"""

from typing import AsyncGenerator
import logging
from app.core.supabase_client import SupabaseClient, supabase_client

logger = logging.getLogger(__name__)

async def get_db() -> AsyncGenerator[SupabaseClient, None]:
    """
    Database dependency that returns the Supabase client
    This replaces the SQLAlchemy session dependency
    """
    try:
        yield supabase_client
    except Exception as e:
        logger.error(f"Database dependency error: {e}")
        raise
    finally:
        # No cleanup needed for Supabase client
        pass

async def init_db():
    """Initialize database connection - no-op for Supabase"""
    logger.info("✅ Supabase client initialized - no database connection needed")
    return True

async def close_db():
    """Close database connection - no-op for Supabase"""
    logger.info("✅ Supabase client cleanup completed")
    return True

def get_connection_mode() -> str:
    """Get the current database connection mode"""
    return "supabase_rest_api"

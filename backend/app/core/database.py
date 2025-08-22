"""
Database configuration and connection management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import SQLAlchemyError
import logging
import os

logger = logging.getLogger(__name__)

# Base class for models - renamed to avoid conflict with SQLAlchemy's metadata
Base = declarative_base()

# Alias for compatibility with existing imports
ModelBase = Base

# Initialize engine and session factory as None initially
engine = None
AsyncSessionLocal = None


def get_database_url():
    """Get database URL with fallback to environment variable"""
    try:
        from app.core.config import settings
        database_url = settings.DATABASE_URL
        
        # If Supabase URL fails, use SQLite for development
        if "supabase.co" in database_url:
            logger.warning("Using Supabase URL. If connection fails, consider using SQLite for development.")
            
        return database_url
    except Exception as e:
        logger.warning(f"Could not load settings: {e}")
        # Fallback to environment variable
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            # Default to SQLite for development
            database_url = "sqlite+aiosqlite:///./dev.db"
            logger.warning("No DATABASE_URL found. Using SQLite for development.")
        return database_url


def create_engine():
    """Create the database engine"""
    global engine, AsyncSessionLocal
    
    try:
        database_url = get_database_url()
        
        # Handle different database types
        if database_url.startswith("sqlite"):
            async_database_url = database_url
        elif database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
            async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            async_database_url = database_url
        
        logger.info(f"Connecting to database: {async_database_url.split('@')[1] if '@' in async_database_url else async_database_url}")
        
        # Create async engine with appropriate settings for database type
        engine_kwargs = {
            "echo": os.getenv("DEBUG", "false").lower() == "true",
            "future": True,
        }
        
        if "sqlite" in async_database_url:
            # SQLite specific settings
            engine_kwargs["poolclass"] = NullPool
        else:
            # PostgreSQL specific settings
            engine_kwargs["poolclass"] = NullPool  # Disable connection pooling for serverless
            engine_kwargs["pool_pre_ping"] = True  # Verify connections before use
        
        engine = create_async_engine(async_database_url, **engine_kwargs)
        
        # Create async session factory
        AsyncSessionLocal = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        logger.info("Database engine created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


async def init_db():
    """Initialize database connection"""
    global engine
    
    if engine is None:
        create_engine()
    
    try:
        # Test database connection
        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    global AsyncSessionLocal
    
    if AsyncSessionLocal is None:
        create_engine()
    
    session = AsyncSessionLocal()
    try:
        yield session
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        await session.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()


async def close_db():
    """Close database connection"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")


# Create engine when module is imported (but don't fail if env vars are missing)
try:
    create_engine()
except Exception as e:
    logger.warning(f"Database engine not created during import: {e}")
    logger.info("Engine will be created when first database operation is performed")

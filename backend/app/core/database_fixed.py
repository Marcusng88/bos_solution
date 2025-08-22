"""
Enhanced database configuration that prioritizes Supabase REST API over direct PostgreSQL
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import SQLAlchemyError
import logging
import os
import asyncio
from app.core.supabase_client import supabase_client

logger = logging.getLogger(__name__)

# Base class for models
Base = declarative_base()

# Alias for compatibility with existing imports
ModelBase = Base

# Initialize engine and session factory as None initially
engine = None
AsyncSessionLocal = None
_connection_mode = "rest_api"  # Default to REST API mode

def get_database_url():
    """Get database URL with fallback options"""
    try:
        from app.core.config import settings
        database_url = settings.DATABASE_URL
        return database_url
    except Exception as e:
        logger.warning(f"Could not load settings: {e}")
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            # Create a dummy SQLite URL for compatibility
            database_url = "sqlite+aiosqlite:///./temp.db"
            logger.warning("Using dummy SQLite URL - will use REST API for actual operations")
        return database_url

async def test_postgresql_connection(database_url: str) -> bool:
    """Test if direct PostgreSQL connection is available"""
    try:
        if database_url.startswith("sqlite"):
            return False
            
        # Convert to async URL if needed
        if database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
            async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            async_database_url = database_url
            
        test_engine = create_async_engine(
            async_database_url,
            echo=False,
            pool_pre_ping=True,
            poolclass=NullPool
        )
        
        # Test connection with timeout
        try:
            async with test_engine.begin() as conn:
                await conn.run_sync(lambda _: None)
        except asyncio.TimeoutError:
            await test_engine.dispose()
            return False
        
        await test_engine.dispose()
        logger.info("Direct PostgreSQL connection successful")
        return True
        
    except Exception as e:
        logger.warning(f"Direct PostgreSQL connection failed: {e}")
        return False

async def test_supabase_rest_api() -> bool:
    """Test if Supabase REST API is available"""
    try:
        # Simple test - try to access users table
        import httpx
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            return False
            
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{supabase_url}/rest/v1/users?limit=1", headers=headers)
            if response.status_code == 200:
                logger.info("Supabase REST API connection successful")
                return True
                
        return False
        
    except Exception as e:
        logger.warning(f"Supabase REST API test failed: {e}")
        return False

def create_engine():
    """Create the database engine with fallback to REST API mode"""
    global engine, AsyncSessionLocal, _connection_mode
    
    try:
        database_url = get_database_url()
        
        # Handle different database types
        if database_url.startswith("sqlite"):
            async_database_url = database_url
        elif database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
            async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            async_database_url = database_url
        
        logger.info(f"Attempting to connect to database: {async_database_url.split('@')[1] if '@' in async_database_url else async_database_url}")
        
        # Create async engine with appropriate settings
        engine_kwargs = {
            "echo": os.getenv("DEBUG", "false").lower() == "true",
            "future": True,
            "poolclass": NullPool,
            "pool_pre_ping": True,
        }
        
        engine = create_async_engine(async_database_url, **engine_kwargs)
        
        # Create async session factory
        AsyncSessionLocal = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        _connection_mode = "postgresql"
        logger.info("Database engine created successfully")
        
    except Exception as e:
        logger.warning(f"Failed to create database engine: {e}")
        logger.info("Will use REST API mode for database operations")
        _connection_mode = "rest_api"
        
        # Create dummy engine for compatibility
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            poolclass=NullPool
        )
        
        AsyncSessionLocal = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

async def init_db():
    """Initialize database connection with automatic mode detection"""
    global engine, _connection_mode
    
    if engine is None:
        create_engine()
    
    # Test both connection methods
    database_url = get_database_url()
    
    if not database_url.startswith("sqlite"):
        # Test direct PostgreSQL connection
        pg_available = await test_postgresql_connection(database_url)
        
        # Test REST API connection
        rest_available = await test_supabase_rest_api()
        
        if pg_available:
            _connection_mode = "postgresql"
            logger.info("✅ Using direct PostgreSQL connection")
            try:
                async with engine.begin() as conn:
                    await conn.run_sync(lambda _: None)
                logger.info("Database connection established successfully")
            except Exception as e:
                logger.error(f"Failed to verify PostgreSQL connection: {e}")
                _connection_mode = "rest_api"
                
        elif rest_available:
            _connection_mode = "rest_api"
            logger.info("✅ Using Supabase REST API connection")
        else:
            logger.warning("⚠️  No database connection available")
            raise Exception("No database connection method available")
    
    logger.info(f"Database initialized in {_connection_mode} mode")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session - will use REST API if PostgreSQL is not available"""
    global AsyncSessionLocal, _connection_mode
    
    if AsyncSessionLocal is None:
        create_engine()
    
    if _connection_mode == "rest_api":
        # Return a mock session that uses REST API
        logger.debug("Using REST API mode - returning mock session")
        yield MockAsyncSession()
        return
    
    # Use regular PostgreSQL session
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

class MockAsyncSession:
    """Mock session for REST API operations"""
    
    def __init__(self):
        self.is_mock = True
    
    async def execute(self, stmt):
        logger.warning("Direct SQL execution not supported in REST API mode")
        raise NotImplementedError("Use Supabase client methods instead of raw SQL")
    
    async def commit(self):
        pass
    
    async def rollback(self):
        pass
    
    async def close(self):
        pass
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

def get_connection_mode():
    """Get current connection mode"""
    return _connection_mode

def is_using_rest_api():
    """Check if currently using REST API mode"""
    return _connection_mode == "rest_api"

async def close_db():
    """Close database connection"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")

# Helper function to get the appropriate client
def get_db_client():
    """Get the appropriate database client based on connection mode"""
    if _connection_mode == "rest_api":
        return supabase_client
    else:
        return None

# Create engine when module is imported (but don't fail if env vars are missing)
try:
    create_engine()
except Exception as e:
    logger.warning(f"Database engine not created during import: {e}")
    logger.info("Engine will be created when first database operation is performed")

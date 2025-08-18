"""
Database configuration and connection management for Supabase
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import SQLAlchemyError
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Base class for models
ModelBase = declarative_base()

# Initialize engine and session factory as None initially
engine = None
AsyncSessionLocal = None


def get_database_url():
    """Get Supabase database URL from environment"""
    try:
        from app.core.config import settings
        return settings.DATABASE_URL
    except Exception as e:
        logger.warning(f"Could not load settings: {e}")
        
    # Get from environment variables
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Get Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if supabase_url and supabase_key:
            # Extract project reference from Supabase URL
            project_ref = supabase_url.split('//')[1].split('.')[0]
            database_url = f"postgresql+asyncpg://postgres.{supabase_key}:{supabase_key}@aws-0-{project_ref}.pooler.supabase.com:6543/postgres"
            logger.info(f"Generated Supabase connection string for project: {project_ref}")
        else:
            raise ValueError("DATABASE_URL or SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY must be set")
    
    return database_url


def create_engine():
    """Create the Supabase database engine"""
    global engine, AsyncSessionLocal
    
    try:
        database_url = get_database_url()
        
        # Ensure we're using asyncpg for Supabase
        if database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
            async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            async_database_url = database_url
        
        logger.info(f"Connecting to Supabase database")
        
        # Create async engine for Supabase
        engine = create_async_engine(
            async_database_url,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            poolclass=NullPool,  # Disable connection pooling for serverless
            future=True,
            pool_pre_ping=True,  # Verify connections before use
        )
        
        # Create async session factory
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        logger.info("Supabase database engine created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create Supabase database engine: {e}")
        raise


async def init_db():
    """Initialize database connection to Supabase"""
    global engine
    
    if engine is None:
        create_engine()
    
    try:
        # Test database connection
        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)
        logger.info("Supabase database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Supabase database: {e}")
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for Supabase"""
    global AsyncSessionLocal
    
    if AsyncSessionLocal is None:
        create_engine()
    
    async with AsyncSessionLocal() as session:
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


async def close_db():
    """Close Supabase database connection"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Supabase database connection closed")


# Create engine when module is imported
try:
    create_engine()
except Exception as e:
    logger.warning(f"Database engine not created during import: {e}")
    logger.info("Engine will be created when first database operation is performed")

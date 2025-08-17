"""
Database setup and testing script
"""

import asyncio
import sys
import os

# Add the parent directory to sys.path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db, get_db, engine, ModelBase
from app.models.user import User
from app.core.config import settings


async def test_db_connection():
    """Test database connection and create tables"""
    try:
        print(f"Testing database connection...")
        print(f"Database URL: {settings.DATABASE_URL}")
        
        # Initialize database connection
        await init_db()
        print("✓ Database connection successful")
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(ModelBase.metadata.create_all)
        print("✓ Tables created successfully")
        
        # Test inserting a user
        async for session in get_db():
            try:
                test_user = User(
                    clerk_id="test_clerk_id_123",
                    email="test@example.com",
                    first_name="Test",
                    last_name="User",
                    is_active=True
                )
                session.add(test_user)
                await session.commit()
                await session.refresh(test_user)
                print(f"✓ Test user created with ID: {test_user.id}")
                
                # Clean up test user
                await session.delete(test_user)
                await session.commit()
                print("✓ Test user cleaned up")
                break
            except Exception as e:
                await session.rollback()
                raise e
        
        print("✅ Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_db_connection())
    sys.exit(0 if success else 1)

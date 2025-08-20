"""
Test script to check Supabase connection
"""

import asyncio
import os
import sys
import logging
from dotenv import load_dotenv
import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import asyncpg

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_supabase_http_connection():
    """Test HTTP connection to Supabase REST API"""
    print("\n=== Testing Supabase HTTP Connection ===")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env file")
        return False
    
    print(f"Supabase URL: {supabase_url}")
    print(f"Service Role Key: {supabase_key[:20]}...")
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Test basic connection to Supabase REST API
            response = await client.get(f"{supabase_url}/rest/v1/", headers=headers)
            print(f"HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Supabase HTTP connection successful")
                return True
            else:
                print(f"❌ Supabase HTTP connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ HTTP connection error: {e}")
        return False

async def test_postgresql_connection():
    """Test direct PostgreSQL connection"""
    print("\n=== Testing PostgreSQL Database Connection ===")
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ Missing DATABASE_URL in .env file")
        return False
    
    print(f"Database URL: {database_url.split('@')[1] if '@' in database_url else 'Local database'}")
    
    try:
        # Test with asyncpg (async PostgreSQL driver)
        # Parse the PostgreSQL URL
        if database_url.startswith("postgresql://"):
            # Extract connection parameters
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            
            print(f"Host: {parsed.hostname}")
            print(f"Port: {parsed.port}")
            print(f"Database: {parsed.path[1:]}")  # Remove leading /
            print(f"Username: {parsed.username}")
            
            # Test connection with asyncpg
            conn = await asyncpg.connect(database_url)
            
            # Test a simple query
            result = await conn.fetchrow("SELECT version()")
            print(f"PostgreSQL version: {result[0]}")
            
            await conn.close()
            print("✅ PostgreSQL connection successful")
            return True
            
    except Exception as e:
        print(f"❌ PostgreSQL connection error: {e}")
        return False

async def test_sqlalchemy_connection():
    """Test SQLAlchemy connection"""
    print("\n=== Testing SQLAlchemy Connection ===")
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ Missing DATABASE_URL in .env file")
        return False
    
    try:
        # Convert to async URL if needed
        if database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
            async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            async_database_url = database_url
        
        print(f"SQLAlchemy URL: {async_database_url.split('@')[1] if '@' in async_database_url else 'Local database'}")
        
        from sqlalchemy.ext.asyncio import create_async_engine
        
        engine = create_async_engine(
            async_database_url,
            echo=False,
            pool_pre_ping=True
        )
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()
            print(f"Database version: {version[0]}")
        
        await engine.dispose()
        print("✅ SQLAlchemy connection successful")
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy connection error: {e}")
        return False

async def test_supabase_tables():
    """Test if required tables exist"""
    print("\n=== Testing Supabase Tables ===")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase configuration")
        return False
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    # List of expected tables
    expected_tables = [
        "users",
        "user_preferences", 
        "my_competitors",
        "social_media_accounts",
        "content_uploads",
        "content_templates"
    ]
    
    try:
        async with httpx.AsyncClient() as client:
            for table in expected_tables:
                try:
                    response = await client.get(
                        f"{supabase_url}/rest/v1/{table}?limit=1", 
                        headers=headers
                    )
                    if response.status_code == 200:
                        print(f"✅ Table '{table}' exists and accessible")
                    else:
                        print(f"❌ Table '{table}' not accessible: {response.status_code}")
                except Exception as e:
                    print(f"❌ Error checking table '{table}': {e}")
                    
    except Exception as e:
        print(f"❌ Error testing tables: {e}")
        return False
    
    return True

async def main():
    """Run all connection tests"""
    print("🚀 Starting Supabase Connection Tests")
    print("=" * 50)
    
    # Test environment variables
    print("\n=== Checking Environment Variables ===")
    required_vars = ["DATABASE_URL", "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "key" in var.lower() or "secret" in var.lower():
                display_value = value[:20] + "..."
            elif "url" in var.lower():
                display_value = value.split('@')[1] if '@' in value else value
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not found")
    
    # Run tests
    tests = [
        test_supabase_http_connection(),
        test_postgresql_connection(),
        test_sqlalchemy_connection(),
        test_supabase_tables()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    print("\n" + "=" * 50)
    print("🎯 Test Results Summary:")
    
    passed = sum(1 for result in results if result is True)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Supabase connection is working.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())

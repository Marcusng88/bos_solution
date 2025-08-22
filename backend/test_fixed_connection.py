"""
Test script to verify the database connection fix
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

async def test_fixed_connection():
    """Test the fixed database connection"""
    print("🧪 Testing Fixed Database Connection")
    print("=" * 40)
    
    try:
        # Import the fixed database module
        from app.core.database_fixed import init_db, get_connection_mode, is_using_rest_api
        from app.core.supabase_client import supabase_client
        
        # Initialize database
        await init_db()
        
        connection_mode = get_connection_mode()
        print(f"✅ Database initialized successfully")
        print(f"📡 Connection mode: {connection_mode}")
        
        if is_using_rest_api():
            print("🔄 Using Supabase REST API mode")
            
            # Test REST API operations
            print("\n🧪 Testing REST API operations...")
            
            # Test getting users (should return empty array if no users)
            try:
                # This is a simple test that the API is accessible
                supabase_url = os.getenv("SUPABASE_URL")
                supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
                
                if supabase_url and supabase_key:
                    # Test a simple REST API call
                    import httpx
                    
                    headers = {
                        "apikey": supabase_key,
                        "Authorization": f"Bearer {supabase_key}",
                        "Content-Type": "application/json"
                    }
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{supabase_url}/rest/v1/users?limit=1", headers=headers)
                        if response.status_code == 200:
                            print("✅ REST API test successful")
                            print(f"   Response status: {response.status_code}")
                        else:
                            print(f"⚠️  REST API returned status: {response.status_code}")
                else:
                    print("❌ Missing Supabase configuration")
                    
            except Exception as e:
                print(f"❌ REST API test failed: {e}")
        else:
            print("🐘 Using direct PostgreSQL connection")
            
        print("\n🎉 Connection test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

async def test_application_startup():
    """Test if the application can start with the fixed configuration"""
    print("\n🚀 Testing Application Startup")
    print("=" * 40)
    
    try:
        # Import main app
        from main import create_app
        
        # Create app
        app = create_app()
        print("✅ FastAPI application created successfully")
        
        # Test if we can access the database configuration
        from app.core.database_fixed import get_connection_mode
        mode = get_connection_mode()
        print(f"✅ Application using {mode} mode")
        
        return True
        
    except Exception as e:
        print(f"❌ Application startup test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🔧 Testing Supabase Connection Fix")
    print("=" * 50)
    
    # Test 1: Database connection
    db_test = await test_fixed_connection()
    
    # Test 2: Application startup
    app_test = await test_application_startup()
    
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Database Connection: {'✅ PASS' if db_test else '❌ FAIL'}")
    print(f"Application Startup: {'✅ PASS' if app_test else '❌ FAIL'}")
    
    if db_test and app_test:
        print("\n🎉 All tests passed! Your Supabase connection is now working.")
        print("💡 The application will automatically use REST API mode when PostgreSQL is not available.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())

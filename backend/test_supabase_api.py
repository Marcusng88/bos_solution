"""
Test Supabase REST API connection
"""

import asyncio
import sys
import os

# Add the parent directory to sys.path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.supabase_client import supabase_client


async def test_supabase_connection():
    """Test Supabase REST API connection"""
    try:
        print("Testing Supabase REST API connection...")
        
        # Test data
        test_user_data = {
            "clerk_id": "test_clerk_123",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "profile_image_url": "https://example.com/avatar.jpg",
            "is_active": True
        }
        
        # Test upsert user
        result = await supabase_client.upsert_user(test_user_data)
        
        if result:
            print(f"✅ User upserted successfully: {result}")
            
            # Test get user
            user = await supabase_client.get_user_by_clerk_id("test_clerk_123")
            if user:
                print(f"✅ User retrieved successfully: {user}")
            else:
                print("❌ Failed to retrieve user")
            
            return True
        else:
            print("❌ Failed to upsert user")
            return False
            
    except Exception as e:
        print(f"❌ Supabase connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_supabase_connection())
    sys.exit(0 if success else 1)

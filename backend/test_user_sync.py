"""
Test script to verify the user sync endpoint
"""

import asyncio
import json
import sys
import os

# Add the parent directory to sys.path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.v1.endpoints.users import router
from app.schemas.user import ClerkUserData
from app.core.database import get_db
from app.models.user import User
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Create a test app
app = FastAPI()
app.include_router(router, prefix="/users")


def test_clerk_user_sync():
    """Test the Clerk user sync endpoint"""
    client = TestClient(app)
    
    # Sample Clerk user data
    clerk_data = {
        "id": "user_test123",
        "email_addresses": [
            {
                "id": "email_123",
                "email_address": "test@example.com"
            }
        ],
        "first_name": "John",
        "last_name": "Doe",
        "image_url": "https://example.com/avatar.jpg",
        "primary_email_address_id": "email_123"
    }
    
    print("Testing user sync endpoint...")
    print(f"Sending data: {json.dumps(clerk_data, indent=2)}")
    
    response = client.post("/users/sync", json=clerk_data)
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {json.dumps(response.json(), indent=2, default=str)}")
    
    if response.status_code == 200:
        print("✅ User sync test passed!")
        return True
    else:
        print("❌ User sync test failed!")
        return False


if __name__ == "__main__":
    success = test_clerk_user_sync()
    sys.exit(0 if success else 1)

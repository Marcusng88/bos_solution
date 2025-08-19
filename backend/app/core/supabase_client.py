"""
Supabase REST API client for database operations
"""

import httpx
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Client for Supabase REST API operations"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            # Ask Supabase to return inserted/updated rows to avoid 204 No Content
            "Prefer": "return=representation",
        }

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None):
        """Make HTTP request to Supabase REST API"""
        url = f"{self.supabase_url}/rest/v1/{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=self.headers, json=data)
                elif method.upper() == "PATCH":
                    response = await client.patch(url, headers=self.headers, json=data, params=params)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=self.headers, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                return response
            except Exception as e:
                raise Exception(f"Failed to make {method} request to {endpoint}: {str(e)}")

    # User management methods
    async def upsert_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert user - check if exists first, then create or update"""
        try:
            # Check if user exists
            existing_user = await self.get_user_by_clerk_id(user_data["clerk_id"])
            
            if existing_user:
                # User exists, update
                response = await self._make_request(
                    "PATCH", 
                    "users", 
                    user_data,
                    {"clerk_id": f"eq.{user_data['clerk_id']}"}
                )
                if response.status_code in [200, 204]:
                    return {"success": True, "user": existing_user, "action": "updated"}
                else:
                    raise Exception(f"Failed to update user: {response.status_code}")
            else:
                # User doesn't exist, create
                response = await self._make_request("POST", "users", user_data)
                if response.status_code in [200, 201, 204]:
                    return {"success": True, "action": "created"}
                else:
                    raise Exception(f"Failed to create user: {response.status_code}")
                    
        except Exception as e:
            raise Exception(f"Failed to upsert user: {str(e)}")

    async def get_user_by_clerk_id(self, clerk_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Clerk ID"""
        try:
            response = await self._make_request("GET", f"users?clerk_id=eq.{clerk_id}")
            if response.status_code == 200:
                users = response.json()
                return users[0] if users else None
            return None
        except Exception as e:
            raise Exception(f"Failed to get user by clerk_id: {str(e)}")

    # User preferences methods
    async def upsert_user_preferences(self, user_id: str, preferences_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert user preferences - check if exists first, then create or update"""
        try:
            # Check if preferences exist
            existing_prefs = await self.get_user_preferences(user_id)
            
            if existing_prefs:
                # Preferences exist, update
                response = await self._make_request(
                    "PATCH", 
                    "user_preferences", 
                    preferences_data,
                    {"user_id": f"eq.{user_id}"}
                )
                if response.status_code in [200, 204]:
                    return {"success": True, "action": "updated"}
                else:
                    error_detail = response.text if hasattr(response, 'text') else f"Status {response.status_code}"
                    raise Exception(f"Failed to update user preferences: {response.status_code} - {error_detail}")
            else:
                # Preferences don't exist, create
                response = await self._make_request("POST", "user_preferences", preferences_data)
                if response.status_code in [200, 201, 204]:
                    return {"success": True, "action": "created"}
                else:
                    error_detail = response.text if hasattr(response, 'text') else f"Status {response.status_code}"
                    if response.status_code == 409:
                        raise Exception(f"Failed to create user preferences: Foreign key constraint violation. User must exist in users table first. Details: {error_detail}")
                    else:
                        raise Exception(f"Failed to create user preferences: {response.status_code} - {error_detail}")
                    
        except Exception as e:
            raise Exception(f"Failed to upsert user preferences: {str(e)}")

    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences by user ID"""
        try:
            response = await self._make_request("GET", f"user_preferences?user_id=eq.{user_id}")
            if response.status_code == 200:
                prefs = response.json()
                return prefs[0] if prefs else None
            return None
        except Exception as e:
            raise Exception(f"Failed to get user preferences: {str(e)}")

    # Competitor methods
    async def create_competitor(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new competitor"""
        try:
            response = await self._make_request("POST", "my_competitors", competitor_data)
            if response.status_code in [200, 201]:
                try:
                    data = response.json() if response.content else None
                except Exception:
                    data = None
                return {"success": True, "data": data}
            if response.status_code == 204:
                # No content returned; treat as success without data
                return {"success": True, "data": None}
            else:
                raise Exception(f"Failed to create competitor: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to create competitor: {str(e)}")

    async def get_user_competitors(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all competitors for a user"""
        try:
            response = await self._make_request("GET", f"my_competitors?user_id=eq.{user_id}")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            raise Exception(f"Failed to get user competitors: {str(e)}")

    async def update_competitor(self, competitor_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a competitor"""
        try:
            response = await self._make_request("PATCH", f"my_competitors", update_data, {"id": f"eq.{competitor_id}"})
            if response.status_code in [200, 204]:
                return {"success": True}
            else:
                raise Exception(f"Failed to update competitor: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to update competitor: {str(e)}")

    async def delete_competitor(self, competitor_id: str) -> Dict[str, Any]:
        """Delete a competitor"""
        try:
            response = await self._make_request("DELETE", f"my_competitors", params={"id": f"eq.{competitor_id}"})
            if response.status_code in [200, 204]:
                return {"success": True}
            else:
                raise Exception(f"Failed to delete competitor: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to delete competitor: {str(e)}")

    # Social media account methods
    async def create_social_media_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new social media account connection"""
        try:
            response = await self._make_request("POST", "social_media_accounts", account_data)
            if response.status_code in [200, 201, 204]:
                return {"success": True, "data": response.json()}
            else:
                raise Exception(f"Failed to create social media account: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to create social media account: {str(e)}")

    async def get_user_social_accounts(self, user_id: str, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all social media accounts for a user, optionally filtered by platform"""
        try:
            endpoint = f"social_media_accounts?user_id=eq.{user_id}"
            if platform:
                endpoint += f"&platform=eq.{platform}"
            
            response = await self._make_request("GET", endpoint)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            raise Exception(f"Failed to get user social accounts: {str(e)}")

    async def update_social_media_account(self, account_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a social media account"""
        try:
            response = await self._make_request("PATCH", f"social_media_accounts", update_data, {"id": f"eq.{account_id}"})
            if response.status_code in [200, 204]:
                return {"success": True}
            else:
                raise Exception(f"Failed to update social media account: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to update social media account: {str(e)}")

    async def delete_social_media_account(self, account_id: str) -> Dict[str, Any]:
        """Delete a social media account connection"""
        try:
            response = await self._make_request("DELETE", f"social_media_accounts", params={"id": f"eq.{account_id}"})
            if response.status_code in [200, 204]:
                return {"success": True}
            else:
                raise Exception(f"Failed to delete social media account: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to delete social media account: {str(e)}")

    # Content upload methods
    async def create_content_upload(self, upload_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new content upload"""
        try:
            response = await self._make_request("POST", "content_uploads", upload_data)
            if response.status_code in [200, 201, 204]:
                return {"success": True, "data": response.json()}
            else:
                raise Exception(f"Failed to create content upload: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to create content upload: {str(e)}")

    async def get_user_content_uploads(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all content uploads for a user, optionally filtered by status"""
        try:
            endpoint = f"content_uploads?user_id=eq.{user_id}"
            if status:
                endpoint += f"&status=eq.{status}"
            
            response = await self._make_request("GET", endpoint)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            raise Exception(f"Failed to get user content uploads: {str(e)}")

    async def update_content_upload(self, upload_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a content upload"""
        try:
            response = await self._make_request("PATCH", f"content_uploads", update_data, {"id": f"eq.{upload_id}"})
            if response.status_code in [200, 204]:
                return {"success": True}
            else:
                raise Exception(f"Failed to update content upload: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to update content upload: {str(e)}")

    async def delete_content_upload(self, upload_id: str) -> Dict[str, Any]:
        """Delete a content upload"""
        try:
            response = await self._make_request("DELETE", f"content_uploads", params={"id": f"eq.{upload_id}"})
            if response.status_code in [200, 204]:
                return {"success": True}
            else:
                raise Exception(f"Failed to delete content upload: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to delete content upload: {str(e)}")

    # Content template methods
    async def create_content_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new content template"""
        try:
            response = await self._make_request("POST", "content_templates", template_data)
            if response.status_code in [200, 201, 204]:
                return {"success": True, "data": response.json()}
            else:
                raise Exception(f"Failed to create content template: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to create content template: {str(e)}")

    async def get_user_content_templates(self, user_id: str, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all content templates for a user, optionally filtered by platform"""
        try:
            endpoint = f"content_templates?user_id=eq.{user_id}"
            if platform:
                endpoint += f"&platforms=cs.{{{platform}}}"
            
            response = await self._make_request("GET", endpoint)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            raise Exception(f"Failed to get user content templates: {str(e)}")

    async def update_content_template(self, template_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a content template"""
        try:
            response = await self._make_request("PATCH", f"content_templates", update_data, {"id": f"eq.{template_id}"})
            if response.status_code in [200, 204]:
                return {"success": True}
            else:
                raise Exception(f"Failed to update content template: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to update content template: {str(e)}")

    async def delete_content_template(self, template_id: str) -> Dict[str, Any]:
        """Delete a content template"""
        try:
            response = await self._make_request("DELETE", f"content_templates", params={"id": f"eq.{template_id}"})
            if response.status_code in [200, 204]:
                return {"success": True}
            else:
                raise Exception(f"Failed to delete content template: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to delete content template: {str(e)}")

# Global instance
supabase_client = SupabaseClient()

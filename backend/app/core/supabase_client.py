"""
Supabase REST API client for database operations
"""

import httpx
import json
from typing import Optional, Dict, Any, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for Supabase REST API operations"""
    
    def __init__(self):
        self.base_url = settings.SUPABASE_URL
        self.anon_key = settings.SUPABASE_ANON_KEY
        self.service_key = settings.SUPABASE_SERVICE_ROLE_KEY
        
    def _get_headers(self, use_service_role: bool = False) -> Dict[str, str]:
        """Get headers for Supabase API calls"""
        key = self.service_key if use_service_role else self.anon_key
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a user in Supabase using REST API"""
        try:
            url = f"{self.base_url}/rest/v1/users"
            headers = self._get_headers(use_service_role=True)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=user_data, headers=headers)
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"User created successfully: {result[0]['id']}")
                    return result[0] if result else None
                elif response.status_code == 409:
                    # User already exists, try to update
                    logger.info("User already exists, attempting to update")
                    return await self.update_user_by_clerk_id(user_data["clerk_id"], user_data)
                else:
                    logger.error(f"Failed to create user: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def update_user_by_clerk_id(self, clerk_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user by clerk_id"""
        try:
            url = f"{self.base_url}/rest/v1/users"
            headers = self._get_headers(use_service_role=True)
            
            # Remove clerk_id from update data to avoid conflicts
            update_data = {k: v for k, v in user_data.items() if k != "clerk_id"}
            
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    url, 
                    json=update_data, 
                    headers=headers,
                    params={"clerk_id": f"eq.{clerk_id}"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"User updated successfully: {clerk_id}")
                    return result[0] if result else None
                else:
                    logger.error(f"Failed to update user: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None
    
    async def get_user_by_clerk_id(self, clerk_id: str) -> Optional[Dict[str, Any]]:
        """Get user by clerk_id"""
        try:
            url = f"{self.base_url}/rest/v1/users"
            headers = self._get_headers(use_service_role=True)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    params={"clerk_id": f"eq.{clerk_id}", "select": "*"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result[0] if result else None
                else:
                    logger.error(f"Failed to get user: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    async def upsert_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Upsert (create or update) user"""
        try:
            url = f"{self.base_url}/rest/v1/users"
            headers = self._get_headers(use_service_role=True)
            headers["Prefer"] = "resolution=merge-duplicates,return=representation"
            
            # Check if user already exists
            existing = await self.get_user_by_clerk_id(user_data.get("clerk_id"))
            
            if existing:
                # Update existing user
                url = f"{self.base_url}/rest/v1/users"
                params = {"clerk_id": f"eq.{user_data.get('clerk_id')}"}
                
                async with httpx.AsyncClient() as client:
                    response = await client.patch(url, json=user_data, headers=headers, params=params)
            else:
                # Create new user
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json=user_data, headers=headers)
            
            if response.status_code in [200, 201, 204]:
                if response.status_code == 204:  # PATCH returns 204 for success
                    return existing  # Return existing data for PATCH
                result = response.json()
                logger.info(f"User upserted successfully: {user_data.get('clerk_id')}")
                return result[0] if result else None
            else:
                logger.error(f"Failed to upsert user: {response.status_code} - {response.text}")
                return None
                    
        except Exception as e:
            logger.error(f"Error upserting user: {e}")
            return None

    async def upsert_user_preferences(self, preference_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Upsert (create or update) user preferences"""
        try:
            url = f"{self.base_url}/rest/v1/user_preferences"
            headers = self._get_headers(use_service_role=True)
            headers["Prefer"] = "resolution=merge-duplicates,return=representation"
            
            # Check if user preferences already exist
            existing = await self.get_user_preferences(preference_data.get("user_id"))
            
            if existing:
                # Update existing preferences
                url = f"{self.base_url}/rest/v1/user_preferences"
                params = {"user_id": f"eq.{preference_data.get('user_id')}"}
                
                async with httpx.AsyncClient() as client:
                    response = await client.patch(url, json=preference_data, headers=headers, params=params)
            else:
                # Create new preferences
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json=preference_data, headers=headers)
            
            if response.status_code in [200, 201, 204]:
                if response.status_code == 204:  # PATCH returns 204 for success
                    return existing  # Return existing data for PATCH
                result = response.json()
                logger.info(f"User preferences upserted successfully: {preference_data.get('user_id')}")
                return result[0] if result else None
            else:
                logger.error(f"Failed to upsert user preferences: {response.status_code} - {response.text}")
                return None
                    
        except Exception as e:
            logger.error(f"Error upserting user preferences: {e}")
            return None

    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences by user_id"""
        try:
            url = f"{self.base_url}/rest/v1/user_preferences"
            headers = self._get_headers(use_service_role=True)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    params={"user_id": f"eq.{user_id}", "select": "*"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result[0] if result else None
                else:
                    logger.error(f"Failed to get user preferences: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return None

    async def create_competitor(self, competitor_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new competitor entry"""
        try:
            url = f"{self.base_url}/rest/v1/my_competitors"
            headers = self._get_headers(use_service_role=True)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=competitor_data, headers=headers)
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"Competitor created successfully: {competitor_data.get('competitor_name')}")
                    return result[0] if result else None
                else:
                    logger.error(f"Failed to create competitor: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating competitor: {e}")
            return None

    async def get_user_competitors(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get all competitors for a user"""
        try:
            url = f"{self.base_url}/rest/v1/my_competitors"
            headers = self._get_headers(use_service_role=True)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    params={"user_id": f"eq.{user_id}", "select": "*"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result if result else []
                else:
                    logger.error(f"Failed to get competitors: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting competitors: {e}")
            return []

    async def update_competitor(self, competitor_id: str, competitor_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a competitor entry"""
        try:
            url = f"{self.base_url}/rest/v1/my_competitors"
            headers = self._get_headers(use_service_role=True)
            
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    url,
                    json=competitor_data,
                    headers=headers,
                    params={"id": f"eq.{competitor_id}"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result[0] if result else None
                else:
                    logger.error(f"Failed to update competitor: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error updating competitor: {e}")
            return None

    async def delete_competitor(self, competitor_id: str, user_id: str) -> bool:
        """Delete a competitor entry"""
        try:
            url = f"{self.base_url}/rest/v1/my_competitors"
            headers = self._get_headers(use_service_role=True)
            
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    url,
                    headers=headers,
                    params={"id": f"eq.{competitor_id}", "user_id": f"eq.{user_id}"}
                )
                
                if response.status_code == 204:
                    logger.info(f"Competitor deleted successfully: {competitor_id}")
                    return True
                else:
                    logger.error(f"Failed to delete competitor: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting competitor: {e}")
            return False


# Global instance
supabase_client = SupabaseClient()

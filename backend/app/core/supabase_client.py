"""
Enhanced Supabase REST API client for all database operations
Replaces SQLAlchemy models and provides direct database access
"""

import httpx
import json
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import os
import logging
import uuid
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Enhanced client for Supabase REST API operations"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
            
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            # Ask Supabase to return inserted/updated rows and merge duplicates for upsert semantics
            "Prefer": "resolution=merge-duplicates,return=representation",
            "Prefer": "return=representation",
        }

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None):
        """Make HTTP request to Supabase REST API"""
        url = f"{self.supabase_url}/rest/v1/{endpoint}"

        async with httpx.AsyncClient() as client:
            try:
                logger.debug(f"Making {method} request to: {url}")
                if data:
                    logger.debug(f"Request data: {data}")
                if params:
                    logger.debug(f"Request params: {params}")

                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=self.headers, json=data, params=params)
                elif method.upper() == "PATCH":
                    response = await client.patch(url, headers=self.headers, json=data, params=params)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=self.headers, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                logger.debug(f"Response status: {response.status_code}")
                
                if response.status_code == 422:
                    error_content = response.text
                    logger.error(f"422 Validation Error for {method} {endpoint}: {error_content}")
                    response.error_content = error_content
                elif response.status_code >= 400:
                    logger.error(f"HTTP Error {response.status_code} for {method} {endpoint}: {response.text}")

                return response
            except Exception as e:
                logger.error(f"Request failed: {e}")
                raise

    # User Operations
    async def get_user_by_clerk_id(self, clerk_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Clerk ID"""
        try:
            response = await self._make_request("GET", "users", params={"clerk_id": f"eq.{clerk_id}"})
            if response.status_code == 200 and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user by clerk_id: {e}")
            return None

    async def upsert_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create or update user"""
        try:
            # Check if user exists
            existing_user = await self.get_user_by_clerk_id(user_data["clerk_id"])
            
            if existing_user:
                # Update existing user
                response = await self._make_request(
                    "PATCH", 
                    f"users?id=eq.{existing_user['id']}", 
                    data=user_data
                )
            else:
                # Create new user
                user_data["id"] = str(uuid.uuid4())
                response = await self._make_request("POST", "users", data=user_data)
            
            if response.status_code in [200, 201] and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error upserting user: {e}")
            return None

    # Competitor Operations
    async def get_competitors_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all competitors for a user"""
        try:
            response = await self._make_request("GET", "competitors", params={"user_id": f"eq.{user_id}"})
            if response.status_code == 200:
                competitors = response.json()
                # Transform data back to frontend format
                return [self._transform_competitor_response(comp) for comp in competitors]
            return []
        except Exception as e:
            logger.error(f"Error getting competitors: {e}")
            return []

    async def get_competitor_by_id(self, competitor_id: str) -> Optional[Dict[str, Any]]:
        """Get competitor by ID"""
        try:
            response = await self._make_request("GET", f"competitors?id=eq.{competitor_id}")
            if response.status_code == 200 and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error getting competitor: {e}")
            return None

    async def create_competitor(self, competitor_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create new competitor"""
        try:
            competitor_data["id"] = str(uuid.uuid4())
            response = await self._make_request("POST", "competitors", data=competitor_data)
            if response.status_code == 201 and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error creating competitor: {e}")
            return None

    async def update_competitor(self, competitor_id: str, competitor_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update competitor"""
        try:
            response = await self._make_request(
                "PATCH", 
                f"competitors?id=eq.{competitor_id}", 
                data=competitor_data
            )
            if response.status_code == 200 and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error updating competitor: {e}")
            return None

    async def delete_competitor(self, competitor_id: str) -> bool:
        """Delete competitor"""
        try:
            response = await self._make_request("DELETE", f"competitors?id=eq.{competitor_id}")
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Error deleting competitor: {e}")
            return False

    # Monitoring Operations
    async def save_monitoring_data(self, monitoring_data: Dict[str, Any]) -> Optional[str]:
        """Save monitoring data"""
        try:
            monitoring_data["id"] = str(uuid.uuid4())
            response = await self._make_request("POST", "monitoring_data", data=monitoring_data)
            if response.status_code == 201 and response.json():
                return response.json()[0]["id"]
            return None
        except Exception as e:
            logger.error(f"Error saving monitoring data: {e}")
            return None

    async def get_monitoring_data_by_competitor(self, competitor_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get monitoring data for a competitor"""
        try:
            params = {
                "competitor_id": f"eq.{competitor_id}",
                "order": "detected_at.desc",
                "limit": str(limit)
            }
            response = await self._make_request("GET", "monitoring_data", params=params)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error getting monitoring data: {e}")
            return []

    async def create_monitoring_alert(self, alert_data: Dict[str, Any]) -> Optional[str]:
        """Create monitoring alert"""
        try:
            alert_data["id"] = str(uuid.uuid4())
            response = await self._make_request("POST", "monitoring_alerts", data=alert_data)
            if response.status_code == 201 and response.json():
                return response.json()[0]["id"]
            return None
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return None

    async def update_competitor_scan_time(self, competitor_id: str) -> bool:
        """Update competitor last scan time"""
        try:
            update_data = {"last_scan_at": datetime.utcnow().isoformat()}
            response = await self._make_request(
                "PATCH", 
                f"competitors?id=eq.{competitor_id}", 
                data=update_data
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error updating scan time: {e}")
            return False

    async def update_monitoring_data(self, data_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update monitoring data"""
        try:
            response = await self._make_request(
                "PATCH", 
                f"monitoring_data?id=eq.{data_id}", 
                data=update_data
            )
            if response.status_code == 200 and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error updating monitoring data: {e}")
            return None

    async def get_monitoring_data_by_id(self, data_id: str) -> Optional[Dict[str, Any]]:
        """Get monitoring data by ID"""
        try:
            response = await self._make_request("GET", f"monitoring_data?id=eq.{data_id}")
            if response.status_code == 200 and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error getting monitoring data by ID: {e}")
            return None

    # User Settings Operations
    async def get_user_monitoring_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user monitoring settings"""
        try:
            response = await self._make_request("GET", "user_monitoring_settings", params={"user_id": f"eq.{user_id}"})
            if response.status_code == 200 and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user settings: {e}")
            return None

    async def upsert_user_monitoring_settings(self, settings_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create or update user monitoring settings"""
        try:
            existing_settings = await self.get_user_monitoring_settings(settings_data["user_id"])
            
            if existing_settings:
                response = await self._make_request(
                    "PATCH", 
                    f"user_monitoring_settings?id=eq.{existing_settings['id']}", 
                    data=settings_data
                )
            else:
                settings_data["id"] = str(uuid.uuid4())
                response = await self._make_request("POST", "user_monitoring_settings", data=settings_data)
            
            if response.status_code in [200, 201] and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error upserting user settings: {e}")
            return None

    # User Preferences Operations
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences"""
        try:
            response = await self._make_request("GET", "user_preferences", params={"user_id": f"eq.{user_id}"})
            if response.status_code == 200 and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return None

    async def upsert_user_preferences(self, preferences_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create or update user preferences"""
        try:
            existing_preferences = await self.get_user_preferences(preferences_data["user_id"])
            
            if existing_preferences:
                response = await self._make_request(
                    "PATCH", 
                    f"user_preferences?id=eq.{existing_preferences['id']}", 
                    data=preferences_data
                )
            else:
                preferences_data["id"] = str(uuid.uuid4())
                response = await self._make_request("POST", "user_preferences", data=preferences_data)
            
            if response.status_code in [200, 201] and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error upserting user preferences: {e}")
            return None

    # Generic Operations
    async def execute_raw_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute raw SQL query (for complex operations)"""
        try:
            # Use Supabase's rpc endpoint for custom functions
            # This is a simplified approach - you might need to create stored procedures
            logger.warning("Raw SQL execution not fully implemented - consider using stored procedures")
            return []
        except Exception as e:
            logger.error(f"Error executing raw SQL: {e}")
            return []

# Global instance
supabase_client = SupabaseClient()

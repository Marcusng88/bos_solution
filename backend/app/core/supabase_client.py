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
        print("🔍 Initializing SupabaseClient...")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        print(f"🔍 Loaded SUPABASE_URL: {self.supabase_url}")
        print(f"🔍 Loaded SUPABASE_SERVICE_ROLE_KEY: {self.supabase_key[:20] if self.supabase_key else 'None'}...")
        
        if not self.supabase_url or not self.supabase_key:
            print("❌ Missing environment variables!")
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
            
        print("✅ Environment variables loaded successfully")
        
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            # Ask Supabase to return inserted/updated rows and merge duplicates for upsert semantics
            "Prefer": "resolution=merge-duplicates,return=representation",
            "Prefer": "return=representation",
        }
        
        print("✅ SupabaseClient initialized successfully")

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None):
        """Make HTTP request to Supabase REST API"""
        # Fix: Use correct Supabase REST API structure
        # For table queries, endpoint should be the table name directly
        url = f"{self.supabase_url}/rest/v1/{endpoint}"
        
        # Add debug logging to see what URL is being called
        logger.info(f"🔍 Making {method} request to: {url}")
        if data:
            logger.info(f"📤 Request data: {data}")
        if params:
            logger.info(f"🔍 Request params: {params}")

        async with httpx.AsyncClient() as client:
            try:
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

                logger.info(f"📥 Response status: {response.status_code}")
                
                if response.status_code == 422:
                    error_content = response.text
                    logger.error(f"❌ 422 Validation Error for {method} {endpoint}: {error_content}")
                    response.error_content = error_content
                elif response.status_code >= 400:
                    logger.error(f"❌ HTTP Error {response.status_code} for {method} {endpoint}: {response.text}")
                    # Add more detailed error logging
                    logger.error(f"❌ Full response: {response.text}")
                    logger.error(f"❌ Response headers: {response.headers}")

                return response
            except Exception as e:
                logger.error(f"❌ Request failed: {e}")
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
                # Return raw data without transformation
                return competitors
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
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error deleting competitor: {e}")
            return False

    async def delete_competitor_cascade(self, competitor_id: str) -> bool:
        """Delete competitor and all related records with proper cascade handling"""
        try:
            logger.info(f"Starting cascade deletion for competitor {competitor_id}")
            
            # Delete related records first (to avoid foreign key constraint violations)
            
            # 1. Delete monitoring alerts
            alerts_response = await self._make_request("DELETE", f"monitoring_alerts?competitor_id=eq.{competitor_id}")
            if alerts_response.status_code in [200, 204]:
                logger.info(f"Deleted monitoring alerts for competitor {competitor_id}")
            elif alerts_response.status_code != 404:
                logger.warning(f"Failed to delete monitoring alerts: {alerts_response.status_code}")
            
            # 2. Delete monitoring data
            data_response = await self._make_request("DELETE", f"monitoring_data?competitor_id=eq.{competitor_id}")
            if data_response.status_code in [200, 204]:
                logger.info(f"Deleted monitoring data for competitor {competitor_id}")
            elif data_response.status_code != 404:
                logger.warning(f"Failed to delete monitoring data: {data_response.status_code}")
            
            # 3. Delete competitor monitoring status
            status_response = await self._make_request("DELETE", f"competitor_monitoring_status?competitor_id=eq.{competitor_id}")
            if status_response.status_code in [200, 204]:
                logger.info(f"Deleted monitoring status for competitor {competitor_id}")
            elif status_response.status_code != 404:
                logger.warning(f"Failed to delete monitoring status: {status_response.status_code}")
            
            # 4. Finally delete the competitor itself
            competitor_response = await self._make_request("DELETE", f"competitors?id=eq.{competitor_id}")
            
            if competitor_response.status_code in [200, 204]:
                logger.info(f"Successfully completed cascade deletion for competitor {competitor_id}")
                return True
            else:
                logger.error(f"Failed to delete competitor {competitor_id}: {competitor_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error in cascade deletion for competitor {competitor_id}: {e}")
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

    async def get_monitoring_alert_by_id(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get monitoring alert by ID"""
        try:
            response = await self._make_request("GET", f"monitoring_alerts?id=eq.{alert_id}")
            if response.status_code == 200 and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error getting monitoring alert by ID: {e}")
            return None

    async def update_monitoring_alert(self, alert_id: str, update_data: Dict[str, Any]) -> bool:
        """Update monitoring alert"""
        try:
            response = await self._make_request(
                "PATCH", 
                f"monitoring_alerts?id=eq.{alert_id}", 
                data=update_data
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error updating monitoring alert: {e}")
            return False

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

    # Campaign Operations
    async def update_campaign_by_name_and_user(self, user_id: str, campaign_name: str, update_data: Dict[str, Any]) -> bool:
        """Update campaign data by campaign name and user ID"""
        try:
            logger.info(f"Updating campaign {campaign_name} for user {user_id} with data: {update_data}")
            
            # First, find the campaign by name (no user_id filtering for mock data)
            response = await self._make_request(
                "GET", 
                "campaign_data", 
                params={
                    "name": f"eq.{campaign_name}",
                    "select": "id"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to find campaign {campaign_name}")
                return False
            
            campaigns = response.json()
            if not campaigns:
                logger.error(f"No campaign found with name {campaign_name}")
                return False
            
            # Update the campaign using the first match (assuming unique names)
            campaign_id = campaigns[0]['id']
            update_response = await self._make_request(
                "PATCH",
                f"campaign_data?id=eq.{campaign_id}",
                data=update_data
            )
            
            if update_response.status_code in [200, 204]:
                logger.info(f"Successfully updated campaign {campaign_name}")
                return True
            else:
                logger.error(f"Failed to update campaign {campaign_name}: {update_response.status_code} - {update_response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating campaign {campaign_name}: {e}")
            return False

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

    # Content Upload methods
    async def get_user_content_uploads(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all content uploads for a user"""
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

    # Social Media Account methods
    async def get_user_social_accounts(self, user_id: str, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all social media accounts for a user"""
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

    async def create_social_media_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new social media account"""
        try:
            response = await self._make_request("POST", "social_media_accounts", account_data)
            if response.status_code in [200, 201, 204]:
                return {"success": True, "data": response.json()}
            else:
                raise Exception(f"Failed to create social media account: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to create social media account: {str(e)}")

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

    # Draft Operations
    async def create_draft(self, draft_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new draft"""
        try:
            response = await self._make_request("POST", "content_drafts", data=draft_data)
            if response.status_code == 201 and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error creating draft: {e}")
            return None

    async def get_user_drafts(self, user_id: str, status: Optional[str] = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get all drafts for a user with pagination"""
        try:
            params = {
                "user_id": f"eq.{user_id}",
                "order": "updated_at.desc"
            }
            
            if status:
                params["status"] = f"eq.{status}"
            
            # Calculate offset for pagination
            offset = (page - 1) * per_page
            params["offset"] = str(offset)
            params["limit"] = str(per_page)
            
            # Get drafts
            response = await self._make_request("GET", "content_drafts", params=params)
            
            if response.status_code != 200:
                return {"drafts": [], "total": 0}
            
            drafts = response.json()
            
            # Get total count for pagination
            count_params = {"user_id": f"eq.{user_id}", "select": "count"}
            if status:
                count_params["status"] = f"eq.{status}"
            
            count_response = await self._make_request("GET", "content_drafts", params=count_params)
            total = 0
            if count_response.status_code == 200:
                count_data = count_response.json()
                if count_data and isinstance(count_data, list) and len(count_data) > 0:
                    total = count_data[0].get("count", len(drafts))
                else:
                    total = len(drafts)
            
            return {"drafts": drafts, "total": total}
        except Exception as e:
            logger.error(f"Error getting user drafts: {e}")
            return {"drafts": [], "total": 0}

    async def get_draft_by_id(self, draft_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific draft by ID"""
        try:
            response = await self._make_request(
                "GET", 
                "content_drafts", 
                params={
                    "id": f"eq.{draft_id}",
                    "user_id": f"eq.{user_id}"
                }
            )
            if response.status_code == 200 and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error getting draft by ID: {e}")
            return None

    async def update_draft(self, draft_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a draft"""
        try:
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = await self._make_request(
                "PATCH", 
                f"content_drafts?id=eq.{draft_id}&user_id=eq.{user_id}", 
                data=update_data
            )
            if response.status_code == 200 and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error updating draft: {e}")
            return None

    async def delete_draft(self, draft_id: str, user_id: str) -> bool:
        """Delete a draft"""
        try:
            response = await self._make_request(
                "DELETE", 
                f"content_drafts?id=eq.{draft_id}&user_id=eq.{user_id}"
            )
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error deleting draft: {e}")
            return False

    async def get_draft_by_source_id(self, source_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get draft by source ID (e.g., from content planning)"""
        try:
            response = await self._make_request(
                "GET", 
                "content_drafts", 
                params={
                    "source_id": f"eq.{source_id}",
                    "user_id": f"eq.{user_id}"
                }
            )
            if response.status_code == 200 and response.json():
                return response.json()[0]
            return None
        except Exception as e:
            logger.error(f"Error getting draft by source ID: {e}")
            return None

# Global instance
supabase_client = SupabaseClient()

# Add test method to verify connection
async def test_supabase_connection():
    """Test method to verify Supabase connection and endpoints"""
    try:
        print(f"🔍 Testing Supabase connection...")
        print(f"🔍 Supabase URL: {supabase_client.supabase_url}")
        print(f"🔍 Supabase Key: {supabase_client.supabase_key[:10]}..." if supabase_client.supabase_key else "❌ No key")
        
        # Test basic connection
        test_url = f"{supabase_client.supabase_url}/rest/v1/roi_metrics"
        print(f"🔍 Test URL: {test_url}")
        
        print("🔍 About to make test request...")
        # Test with minimal query
        response = await supabase_client._make_request("GET", "roi_metrics", params={"limit": "1"})
        print(f"✅ Test successful - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Data returned: {len(data)} rows")
            if data:
                print(f"✅ Sample row: {data[0]}")
        else:
            print(f"❌ Test failed - Status: {response.status_code}")
            print(f"❌ Error: {response.text}")
            
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Full traceback:")
        traceback.print_exc()
        return False

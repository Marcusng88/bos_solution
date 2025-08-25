"""
ROI Hourly Writer Service

Reads the latest roi_metrics per user+platform and appends a new cumulative row
using the multiplier-based growth and financial calculations from data_generator.

Updated to use Supabase client instead of direct PostgreSQL connection.
"""

from __future__ import annotations

import os
import asyncio
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

# Import Supabase client instead of asyncpg
try:
    from app.core.supabase_client import supabase_client
except ImportError:
    # Fallback for direct script execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent.parent))
    from app.core.supabase_client import supabase_client

# Optional SSE publisher import
try:
    from app.api.v1.endpoints.roi_updates import publish_status  # type: ignore
except Exception:
    def publish_status(event: str, payload: dict):
        return None

try:
    # When executed as a module inside a package
    from .data_generator import DataGeneratorService, BaseMetrics
except Exception:
    # Fallback for direct script execution (no package context)
    import importlib.util
    from pathlib import Path
    here = Path(__file__).resolve().parent
    dg_path = here / "data_generator.py"
    spec = importlib.util.spec_from_file_location("roi_data_generator", str(dg_path))
    if spec and spec.loader:
        import sys as _sys
        dg_mod = importlib.util.module_from_spec(spec)
        # Ensure module is visible to dataclasses typing resolution
        if spec.name:
            _sys.modules[spec.name] = dg_mod
        spec.loader.exec_module(dg_mod)  # type: ignore[attr-defined]
        DataGeneratorService = dg_mod.DataGeneratorService  # type: ignore[attr-defined]
        BaseMetrics = dg_mod.BaseMetrics  # type: ignore[attr-defined]
    else:
        raise

# Platforms we support generating metrics for (used for seeding new users)
PLATFORMS: tuple[str, ...] = ("facebook", "instagram", "youtube")

async def get_latest_roi_metrics_all() -> List[Dict[str, Any]]:
    """Get latest ROI metrics for all users using Supabase"""
    try:
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "select": "id,user_id,platform,campaign_id,views,likes,comments,shares,clicks,update_timestamp",
                "order": "user_id,platform,update_timestamp.desc"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            # Group by user_id and platform, take the latest for each
            latest_metrics = {}
            for row in data:
                key = (row["user_id"], row["platform"])
                if key not in latest_metrics or row["update_timestamp"] > latest_metrics[key]["update_timestamp"]:
                    latest_metrics[key] = row
            return list(latest_metrics.values())
        return []
    except Exception as e:
        print(f"Error getting latest ROI metrics: {e}")
        return []

async def get_latest_roi_metrics_user(user_id: str) -> List[Dict[str, Any]]:
    """Get latest ROI metrics for a specific user using Supabase"""
    try:
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "user_id": f"eq.{user_id}",
                "select": "id,user_id,platform,campaign_id,views,likes,comments,shares,clicks,update_timestamp",
                "order": "user_id,platform,update_timestamp.desc"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            # Group by platform, take the latest for each
            latest_metrics = {}
            for row in data:
                platform = row["platform"]
                if platform not in latest_metrics or row["update_timestamp"] > latest_metrics[platform]["update_timestamp"]:
                    latest_metrics[platform] = row
            return list(latest_metrics.values())
        return []
    except Exception as e:
        print(f"Error getting latest ROI metrics for user {user_id}: {e}")
        return []

async def insert_roi_metric(
    user_id: str,
    platform: str,
    campaign_id: int | None,
    content_type: str,
    views: int,
    likes: int,
    comments: int,
    shares: int,
    clicks: int,
    ad_spend: float,
    revenue_generated: float,
    cost_per_click: float,
    cost_per_impression: float,
    roi_percentage: float,
    roas_ratio: float,
    update_timestamp: datetime
) -> int | None:
    """Insert a new ROI metric using Supabase"""
    try:
        data = {
            "user_id": user_id,
            "platform": platform,
            "campaign_id": campaign_id,
            "content_type": content_type,
            "content_category": "generic",
            "views": views,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": 1,
            "clicks": clicks,
            "ad_spend": ad_spend,
            "revenue_generated": revenue_generated,
            "cost_per_click": cost_per_click,
            "cost_per_impression": cost_per_impression,
            "roi_percentage": roi_percentage,
            "roas_ratio": roas_ratio,
            "update_timestamp": update_timestamp.isoformat()
        }
        
        response = await supabase_client._make_request("POST", "roi_metrics", data=data)
        
        if response.status_code == 201:
            result = response.json()
            return result[0]["id"] if result else None
        return None
    except Exception as e:
        print(f"Error inserting ROI metric: {e}")
        return None

async def get_most_recent_user() -> str | None:
    """Get the most recently active user using Supabase"""
    try:
        # First try to get the most recently active user (from ROI API calls)
        response = await supabase_client._make_request(
            "GET",
            "users",
            params={
                "select": "clerk_id",
                "order": "updated_at.desc.nulls_last",
                "limit": 1
            }
        )
        
        if response.status_code == 200 and response.json():
            return response.json()[0]["clerk_id"]
        
        # Fallback to connected accounts
        response = await supabase_client._make_request(
            "GET",
            "social_media_accounts",
            params={
                "is_active": "eq.true",
                "select": "user_id",
                "order": "updated_at.desc.nulls_last",
                "limit": 1
            }
        )
        
        if response.status_code == 200 and response.json():
            return response.json()[0]["user_id"]
        
        return None
    except Exception as e:
        print(f"Error getting most recent user: {e}")
        return None

async def execute_roi_update() -> int:
    """Execute ROI update using Supabase client - NOW USES LIVE 10-MINUTE UPDATE LOGIC"""
    try:
        # Resolve a single focus user from DB: prefer users with connected accounts.
        only_user: str | None = await get_most_recent_user()

        if not only_user:
            print("⚠️  No target user found, processing all users")
            # For now, use a default user if none found
            only_user = "user_31e00osZQfX9vuQiZyjTiuKAM0s"

        print(f"🎯 ROI Writer targeting user: {only_user}")
        print("🔄 Using NEW LIVE 10-MINUTE UPDATE LOGIC!")
        print("   📊 Fetches latest 3 rows (1 per platform)")
        print("   📈 Applies growth multipliers to existing values")
        print("   ⏰ Inserts 3 new rows every 10 minutes")
        
        # Use the new live update logic
        data_service = DataGeneratorService()
        next_updates = await data_service.generate_live_10min_update(supabase_client, only_user)
        
        inserted = 0
        
        # Insert the 3 new platform updates
        for update_record in next_updates:
            try:
                response = await supabase_client._make_request("POST", "roi_metrics", data=update_record)
                
                if response.status_code == 201:
                    inserted += 1
                    platform = update_record["platform"]
                    views = update_record["views"]
                    likes = update_record["likes"]
                    
                    print(f"✅ Inserted {platform}: views={views}, likes={likes}")
                    
                    # Publish status for real-time updates
                    publish_status("roi_update", {
                        "user_id": only_user,
                        "platform": platform,
                        "views": views,
                        "likes": likes,
                        "timestamp": update_record["update_timestamp"]
                    })
                    
                else:
                    print(f"❌ Failed to insert {update_record['platform']}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error inserting {update_record['platform']}: {e}")
                continue
        
        print(f"🎉 Live update completed: {inserted}/3 platform updates inserted")
        return inserted

    except Exception as e:
        print(f"Error in execute_roi_update: {e}")
        raise

if __name__ == "__main__":
    print("🧪 Testing NEW LIVE 10-MINUTE UPDATE LOGIC!")
    print("=" * 50)
    
    # Test the new logic
    asyncio.run(execute_roi_update())



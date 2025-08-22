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
    """Execute ROI update using Supabase client"""
    try:
        # Resolve a single focus user from DB: prefer users with connected accounts.
        only_user: str | None = await get_most_recent_user()

        # Fetch latest per user+platform scoped to the resolved user if available
        if only_user:
            print(f"🎯 ROI Writer targeting user: {only_user}")
            rows = await get_latest_roi_metrics_user(only_user)
        else:
            print("⚠️  No target user found, processing all users")
            rows = await get_latest_roi_metrics_all()

        # If there are no rows at all, or if some users/platforms have never been seeded,
        # create a single base row with default metrics to start the growth chain.
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        inserted = 0

        # Build a set of (user_id, platform) that already have at least one row
        existing_pairs = {(r["user_id"], r["platform"]) for r in rows}

        # Build seed list: only the resolved user (if any)
        user_rows = [{"clerk_id": only_user}] if only_user else []

        # Seed missing (user, platform) combinations with base values (all 1s) and zero finances
        for ur in user_rows:
            uid = ur["clerk_id"]
            for pf in PLATFORMS:
                if (uid, pf) in existing_pairs:
                    continue
                seed_content_type = "reel" if pf == "instagram" else ("video" if pf == "youtube" else "post")
                seed_id = await insert_roi_metric(
                    uid,
                    pf,
                    None,  # campaign_id
                    seed_content_type,
                    1,  # views
                    1,  # likes
                    1,  # comments
                    1,  # shares
                    1,  # clicks
                    0.0,  # ad_spend
                    0.0,  # revenue_generated
                    0.0,  # cost_per_click
                    0.0,  # cost_per_impression
                    0.0,  # roi_percentage
                    0.0,  # roas_ratio
                    now,
                )
                if seed_id:
                    inserted += 1
                    publish_status("roi_seed", {"user_id": uid, "platform": pf, "id": seed_id})
                    print("Following Lines are written:")
                    print({
                        "id": seed_id,
                        "user_id": uid,
                        "platform": pf,
                        "campaign_id": None,
                        "content_type": seed_content_type,
                        "views": 1,
                        "likes": 1,
                        "comments": 1,
                        "shares": 1,
                        "clicks": 1,
                        "ad_spend": 0.0,
                        "revenue_generated": 0.0,
                        "cost_per_click": 0.0,
                        "cost_per_impression": 0.0,
                        "roi_percentage": 0.0,
                        "roas_ratio": 0.0,
                        "update_timestamp": now.isoformat()
                    })

        # Process existing rows with growth calculations
        for row in rows:
            # Create base metrics from the row
            base_metrics = BaseMetrics(
                views=row["views"],
                likes=row["likes"],
                comments=row["comments"],
                shares=row["shares"],
                clicks=row["clicks"]
            )

            # Generate new metrics with growth
            data_service = DataGeneratorService()
            new_metrics = data_service.generate_metrics(base_metrics)

            # Insert new row with calculated metrics
            new_id = await insert_roi_metric(
                row["user_id"],
                row["platform"],
                row["campaign_id"],
                "post",  # Default content type
                new_metrics.views,
                new_metrics.likes,
                new_metrics.comments,
                new_metrics.shares,
                new_metrics.clicks,
                new_metrics.ad_spend,
                new_metrics.revenue_generated,
                new_metrics.cost_per_click,
                new_metrics.cost_per_impression,
                new_metrics.roi_percentage,
                new_metrics.roas_ratio,
                now
            )

            if new_id:
                inserted += 1
                publish_status("roi_update", {
                    "user_id": row["user_id"],
                    "platform": row["platform"],
                    "id": new_id,
                    "previous_id": row["id"]
                })

        return inserted

    except Exception as e:
        print(f"Error in execute_roi_update: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(execute_roi_update())



"""
ROI endpoints: trends series and campaigns-in-range markers.

SQL is stored under app/core/ROI backend/roi/sql per project convention.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta, timezone
import os
from app.core.database import get_db
from app.core.supabase_client import supabase_client
import importlib.util as _ils

# Check for critical dependencies
print("🔍 Checking critical dependencies...")
try:
    import psycopg2
    print("✅ psycopg2 available")
except ImportError:
    print("❌ psycopg2 NOT available - this could cause database issues")

try:
    import sqlalchemy
    print("✅ SQLAlchemy available")
except ImportError:
    print("❌ SQLAlchemy NOT available - this could cause database issues")

try:
    import supabase
    print("✅ Supabase Python client available")
except ImportError:
    print("❌ Supabase Python client NOT available - this could cause Supabase issues")

print(f"🔍 Current working directory: {os.getcwd()}")
print(f"🔍 Supabase client type: {type(supabase_client)}")

router = APIRouter()

@router.get("/test", tags=["roi"])
async def test_endpoint():
    """Simple test endpoint to verify basic functionality"""
    try:
        print("🧪 Test endpoint called")
        
        # Test basic imports
        print("✅ Basic imports working")
        
        # Test datetime functionality
        now = datetime.now(timezone.utc)
        print(f"✅ Datetime working: {now}")
        
        # Test Supabase client
        print(f"✅ Supabase client available: {type(supabase_client)}")
        
        # Test Supabase connection
        print("🔍 Testing Supabase connection...")
        from app.core.supabase_client import test_supabase_connection
        connection_success = await test_supabase_connection()
        
        return {
            "status": "success",
            "message": "Basic functionality working",
            "timestamp": now.isoformat(),
            "supabase_client_type": str(type(supabase_client)),
            "supabase_connection": "success" if connection_success else "failed"
        }
    except Exception as e:
        print(f"❌ Test endpoint failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }

# Dynamically import cache from 'ROI backend' (space in folder name)
try:
    _here = os.path.dirname(__file__)
    _cache_path = os.path.normpath(os.path.join(_here, "../../../core/ROI backend/roi/services/cache.py"))
    _spec = _ils.spec_from_file_location("roi_cache", _cache_path)
    if _spec and _spec.loader:
        _mod = _ils.module_from_spec(_spec)
        import sys as _sys
        if _spec.name:
            _sys.modules[_spec.name] = _mod
        _spec.loader.exec_module(_mod)  # type: ignore[attr-defined]
        cache = _mod.cache  # type: ignore[attr-defined]
    else:
        raise ImportError("cache module spec not loaded")
except Exception:
    # Fallback minimal in-memory cache
    class _FallbackCache:
        def __init__(self):
            self._s = {}
        def get(self, k):
            v = self._s.get(k)
            if not v: return None
            import time
            exp, val = v
            if time.time() > exp:
                self._s.pop(k, None)
                return None
            return val
        def set(self, k, v, ttl_seconds=120):
            import time
            self._s[k] = (time.time() + ttl_seconds, v)
    cache = _FallbackCache()


def _sql_path(filename: str) -> str:
    # endpoints/roi.py -> .../app/api/v1/endpoints
    here = os.path.dirname(__file__)
    sql_dir = os.path.normpath(os.path.join(here, "../../../core/ROI backend/roi/sql"))
    return os.path.join(sql_dir, filename)


async def _load_sql(filename: str) -> str:
    path = _sql_path(filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load SQL '{filename}': {e}")


# Remove the entire _resolve_range function since it's no longer needed
# The function was here but is now removed as we fetch all data and filter on frontend


async def _mark_user_active(db, user_id: str) -> None:
    try:
        # Update user's updated_at timestamp using Supabase
        await supabase_client._make_request(
            "PATCH",
            "users",
            data={"updated_at": datetime.now(timezone.utc).isoformat()},
            params={"clerk_id": f"eq.{user_id}"}
        )
    except Exception:
        # Non-fatal; writer will still function with fallbacks
        pass


@router.get("/trends", tags=["roi"])
async def get_roi_trends(
    user_id: str = Query(None, description="Clerk user id (optional for demo)"),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        print(f"🚀 ROI Trends endpoint called - fetching ALL data (no date filtering)")
        print(f"👤 User ID filter: {'Yes' if user_id else 'No (fetching all data)'}")
        
        # Build query params - include user_id filter only if provided
        query_params = {
            "order": "created_at.asc",
            "limit": "999999"  # Get all rows
        }
        
        # Add user_id filter only if provided
        if user_id:
            query_params["user_id"] = f"eq.{user_id}"
        
        # Use Supabase to query roi_metrics table - NO DATE FILTERING
        print(f"🔍 ROI Trends query params: {query_params}")
        print(f"📊 Fetching ALL data (frontend will handle date filtering)")
        
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params=query_params
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch ROI trends data")
            
        rows = response.json()
        print(f"📊 ROI Trends rows returned: {len(rows)} (ALL data)")
        
        # Return ALL data - frontend will handle filtering
        # This eliminates all timestamp parsing issues!
        return {"all_data": rows, "message": "Frontend will handle date filtering"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_roi_trends failed: {e}")


@router.get("/campaigns-in-range", tags=["roi"])
async def get_campaign_markers(
    user_id: str = Query(None, description="User ID (optional for demo)"),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        print(f"🚀 Campaigns endpoint called - fetching ALL data (no date filtering)")
        print(f"👤 User ID filter: {'Yes' if user_id else 'No (fetching all data)'}")
        
        # Build query params - include user_id filter only if provided
        query_params = {
            "order": "start_date.asc",
            "limit": "999999"  # Get all rows
        }
        
        # Add user_id filter only if provided
        if user_id:
            query_params["user_id"] = f"eq.{user_id}"
        
        # Use Supabase to query campaigns table - NO DATE FILTERING
        print(f"🔍 Campaigns query params: {query_params}")
        print(f"📊 Fetching ALL data (frontend will handle date filtering)")
        
        response = await supabase_client._make_request(
            "GET",
            "campaigns",
            params=query_params
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch campaigns data")
            
        rows = response.json()
        print(f"📊 Campaigns rows returned: {len(rows)} (ALL data)")
        
        # Return ALL data - frontend will handle filtering
        # This eliminates all timestamp parsing issues!
        return {"all_data": rows, "message": "Frontend will handle date filtering"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_campaign_markers failed: {e}")


@router.get("/overview", tags=["roi"])
async def get_overview(
    user_id: str = Query(None, description="Clerk user id (optional for demo)"),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        print(f"🚀 Overview endpoint called - fetching ALL data (no date filtering)")
        print(f"👤 User ID filter: {'Yes' if user_id else 'No (fetching all data)'}")
        
        # Create cache key - use 'all' if no user_id provided
        cache_user = user_id or "all"
        cache_key = f"overview:{cache_user}:all_data"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
            
        # Mark user as active only if user_id provided
        if user_id:
            await _mark_user_active(db, user_id)
        
        # Build query params - include user_id filter only if provided
        query_params = {
            "order": "created_at.desc",
            "limit": "999999"  # Get all rows
        }
        
        # Add user_id filter only if provided
        if user_id:
            query_params["user_id"] = f"eq.{user_id}"
        
        # Use Supabase to get overview data - NO DATE FILTERING
        print(f"🔍 Overview query params: {query_params}")
        print(f"📊 Fetching ALL data (frontend will handle date filtering)")
        
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params=query_params
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch overview data")
            
        rows = response.json()
        print(f"📊 Overview rows returned: {len(rows)} (ALL data)")
        
        # Return ALL data - frontend will handle filtering
        # This eliminates all timestamp parsing issues!
        result = {"all_data": rows, "message": "Frontend will handle date filtering"}
        
        cache.set(cache_key, result, ttl_seconds=2700)  # 45 minutes
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_overview failed: {e}")


@router.get("/revenue/by-source", tags=["roi"])
async def get_revenue_by_source(
    user_id: str = Query(None, description="User ID (optional for demo)"),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        print(f"🚀 Revenue by Source endpoint called - fetching ALL data (no date filtering)")
        print(f"👤 User ID filter: {'Yes' if user_id else 'No (fetching all data)'}")
        
        # Mark as active only if user_id provided
        if user_id:
            await _mark_user_active(db, user_id)
        
        # Build query params - include user_id filter only if provided
        query_params = {
            "select": "platform,revenue_generated,created_at",
            "order": "created_at.asc",
            "limit": "999999"  # Get all rows
        }
        
        # Add user_id filter only if provided
        if user_id:
            query_params["user_id"] = f"eq.{user_id}"
        
        # Use Supabase to get revenue by source data - NO DATE FILTERING
        print(f"🔍 Revenue by Source query params: {query_params}")
        print(f"📊 Fetching ALL data (frontend will handle date filtering)")
        
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params=query_params
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch revenue by source data")
            
        rows = response.json()
        print(f"📊 Revenue by Source rows returned: {len(rows)} (ALL data)")
        
        # Add detailed logging for debugging
        if len(rows) > 0:
            print(f"📊 Sample row data: {rows[0]}")
            print(f"📊 Platform values found: {list(set(row.get('platform', 'unknown') for row in rows))}")
        else:
            print("❌ No rows returned from Supabase query")
            print(f"🔍 Query params used: {query_params}")
        
        # Return ALL data - frontend will handle filtering
        # This eliminates all timestamp parsing issues!
        return {"all_data": rows, "message": "Frontend will handle date filtering"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_revenue_by_source failed: {e}")


@router.get("/revenue/trends", tags=["roi"])
async def get_revenue_trends(
    user_id: str = Query(None, description="User ID (optional for demo)"),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        print(f"🚀 Revenue Trends endpoint called - fetching ALL data (no date filtering)")
        print(f"👤 User ID filter: {'Yes' if user_id else 'No (fetching all data)'}")
        
        # Mark as active only if user_id provided
        if user_id:
            await _mark_user_active(db, user_id)
        
        # Build query params - include user_id filter only if provided
        query_params = {
            "select": "revenue_generated,created_at",
            "order": "created_at.asc",
            "limit": "999999"  # Get all rows
        }
        
        # Add user_id filter only if provided
        if user_id:
            query_params["user_id"] = f"eq.{user_id}"
        
        # Use Supabase to get revenue trends data - NO DATE FILTERING
        print(f"🔍 Revenue Trends query params: {query_params}")
        print(f"📊 Fetching ALL data (frontend will handle date filtering)")
        
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params=query_params
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch revenue trends data")
            
        rows = response.json()
        print(f"📊 Revenue Trends rows returned: {len(rows)} (ALL data)")
        
        # Return ALL data - frontend will handle filtering
        # This eliminates all timestamp parsing issues!
        return {"all_data": rows, "message": "Frontend will handle date filtering"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_revenue_trends failed: {e}")


@router.get("/cost/breakdown", tags=["roi"])
async def get_cost_breakdown(
    user_id: str = Query(None, description="User ID (optional for demo)"),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        print(f"🚀 Cost Breakdown endpoint called - fetching ALL data (no date filtering)")
        print(f"👤 User ID filter: {'Yes' if user_id else 'No (fetching all data)'}")
        
        # Build query params - include user_id filter only if provided
        query_params = {
            "select": "platform,ad_spend,created_at",
            "limit": "999999"  # Get all rows
        }
        
        # Add user_id filter only if provided
        if user_id:
            query_params["user_id"] = f"eq.{user_id}"
        
        # Use Supabase to get cost breakdown data - NO DATE FILTERING
        print(f"🔍 Cost Breakdown query params: {query_params}")
        print(f"📊 Fetching ALL data (frontend will handle date filtering)")
        
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params=query_params
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch cost breakdown data")
            
        rows = response.json()
        print(f"📊 Cost Breakdown rows returned: {len(rows)} (ALL data)")
        
        # Return ALL data - frontend will handle filtering
        # This eliminates all timestamp parsing issues!
        return {"all_data": rows, "message": "Frontend will handle date filtering"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_cost_breakdown failed: {e}")


@router.get("/cost/monthly-trends", tags=["roi"])
async def get_monthly_spend_trends(
    user_id: str = Query(...),
    year: int = Query(..., ge=2000, le=2100),
    db = Depends(get_db),
):
    try:
        start_date = f"{year}-01-01T00:00:00Z"
        end_date = f"{year}-12-31T23:59:59Z"
        
        # Use Supabase to get monthly spend trends data - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "created_at": f"gte.{start_date}",
                "created_at": f"lte.{end_date}",
                "select": "ad_spend,created_at",
                "order": "created_at.asc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch monthly spend trends data")
            
        rows = response.json()
        
        # Group by month and calculate monthly spend
        from collections import defaultdict
        monthly_spend = defaultdict(float)
        
        for row in rows:
            month_key = row["created_at"][:7]  # YYYY-MM
            spend = float(row.get("ad_spend", 0))
            monthly_spend[month_key] += spend
        
        # Convert to list format
        result_rows = [{"month": month, "spend": spend} for month, spend in sorted(monthly_spend.items())]
        
        return {"rows": result_rows}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_monthly_spend_trends failed: {e}")


@router.get("/profitability/clv", tags=["roi"])
async def get_clv(
    user_id: str = Query(None, description="User ID (optional for demo)"),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        print("🚀 CLV endpoint called - fetching ALL data (no date filtering)")
        print(f"👤 User ID filter: {'Yes' if user_id else 'No (fetching all data)'}")

        query_params = {
            "select": "revenue_generated,ad_spend,views,clicks",
            "limit": "999999",
        }
        if user_id:
            query_params["user_id"] = f"eq.{user_id}"

        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params=query_params,
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch CLV data")

        rows = response.json()
        print(f"📊 CLV rows returned: {len(rows)} (ALL data)")

        if rows:
            total_revenue = sum(float(r.get("revenue_generated", 0)) for r in rows)
            total_spend = sum(float(r.get("ad_spend", 0)) for r in rows)
            total_views = sum(int(r.get("views", 0)) for r in rows)
            total_clicks = sum(int(r.get("clicks", 0)) for r in rows)

            avg_order_value = total_revenue / len(rows) if rows else 0
            purchase_frequency = len(rows) / 30 if total_views > 0 else 0
            customer_lifespan = 12
            clv = avg_order_value * purchase_frequency * customer_lifespan

            result = {
                "clv": clv,
                "avg_order_value": avg_order_value,
                "purchase_frequency": purchase_frequency,
                "customer_lifespan": customer_lifespan,
                "total_revenue": total_revenue,
                "total_spend": total_spend,
                "total_views": total_views,
                "total_clicks": total_clicks,
            }
        else:
            result = {}

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_clv failed: {e}")


@router.get("/profitability/cac", tags=["roi"])
async def get_cac(
    user_id: str = Query(None, description="User ID (optional for demo)"),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        print("🚀 CAC endpoint called - fetching ALL data (no date filtering)")
        print(f"👤 User ID filter: {'Yes' if user_id else 'No (fetching all data)'}")

        query_params = {
            "select": "ad_spend,clicks,views",
            "limit": "999999",
        }
        if user_id:
            query_params["user_id"] = f"eq.{user_id}"

        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params=query_params,
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch CAC data")

        rows = response.json()
        print(f"📊 CAC rows returned: {len(rows)} (ALL data)")

        if rows:
            total_spend = sum(float(r.get("ad_spend", 0)) for r in rows)
            total_clicks = sum(int(r.get("clicks", 0)) for r in rows)
            total_views = sum(int(r.get("views", 0)) for r in rows)

            cac = total_spend / total_clicks if total_clicks > 0 else 0
            cpm = (total_spend / total_views) * 1000 if total_views > 0 else 0
            ctr = (total_clicks / total_views) * 100 if total_views > 0 else 0

            result = {
                "cac": cac,
                "cpm": cpm,
                "ctr": ctr,
                "total_spend": total_spend,
                "total_clicks": total_clicks,
                "total_views": total_views,
            }
        else:
            result = {}

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_cac failed: {e}")


@router.get("/roi/trends", tags=["roi"])
async def get_roi_trends(
    user_id: str = Query(None, description="Clerk user id (optional for demo)"),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        print(f"🚀 ROI Trends endpoint called - fetching ALL data (no date filtering)")
        print(f"👤 User ID filter: {'Yes' if user_id else 'No (fetching all data)'}")
        
        # Build query params - include user_id filter only if provided
        query_params = {
            "order": "created_at.asc",
            "limit": "999999"  # Get all rows
        }
        
        # Add user_id filter only if provided
        if user_id:
            query_params["user_id"] = f"eq.{user_id}"
        
        # Use Supabase to query roi_metrics table - NO DATE FILTERING
        print(f"🔍 ROI Trends query params: {query_params}")
        print(f"📊 Fetching ALL data (frontend will handle date filtering)")
        
        try:
            print("🔍 Attempting to make Supabase request...")
            response = await supabase_client._make_request(
                "GET",
                "roi_metrics",
                params=query_params
            )
            print(f"✅ Supabase request successful - status: {response.status_code}")
        except Exception as supabase_error:
            print(f"❌ Supabase request failed: {type(supabase_error).__name__}: {str(supabase_error)}")
            print(f"❌ Error details: {supabase_error}")
            raise HTTPException(status_code=500, detail=f"Supabase request failed: {str(supabase_error)}")
        
        if response.status_code != 200:
            print(f"❌ Supabase returned non-200 status: {response.status_code}")
            raise HTTPException(status_code=500, detail="Failed to fetch ROI trends data")
            
        try:
            rows = response.json()
            print(f"✅ Successfully parsed response JSON - rows type: {type(rows)}, length: {len(rows) if rows else 0}")
        except Exception as json_error:
            print(f"❌ Failed to parse response JSON: {type(json_error).__name__}: {str(json_error)}")
            print(f"❌ Response content: {response.text if hasattr(response, 'text') else 'No text attribute'}")
            raise HTTPException(status_code=500, detail=f"Failed to parse response: {str(json_error)}")
        
        print(f"📊 ROI Trends rows returned: {len(rows)} (ALL data)")
        
        # Return ALL data - frontend will handle filtering
        # This eliminates all timestamp parsing issues!
        return {"all_data": rows, "message": "Frontend will handle date filtering"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_roi_trends_daily failed: {e}")


@router.get("/channel/performance", tags=["roi"])
async def get_channel_performance(
    user_id: str = Query(None, description="User ID (optional for demo)"),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        print(f"🚀 Channel Performance endpoint called - fetching ALL data (no date filtering)")
        print(f"👤 User ID filter: {'Yes' if user_id else 'No (fetching all data)'}")
        
        # Build query params - include user_id filter only if provided
        query_params = {
            "select": "platform,views,likes,comments,shares,clicks,revenue_generated,ad_spend,roi_percentage,created_at",
            "order": "platform.asc",
            "limit": "999999"  # Get all rows
        }
        
        # Add user_id filter only if provided
        if user_id:
            query_params["user_id"] = f"eq.{user_id}"
        
        # Use Supabase to get channel performance data - NO DATE FILTERING
        print(f"🔍 Channel Performance query params: {query_params}")
        print(f"📊 Fetching ALL data (frontend will handle date filtering)")
        
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params=query_params
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch channel performance data")
            
        rows = response.json()
        print(f"📊 Channel Performance rows returned: {len(rows)} (ALL data)")
        
        # Return ALL data - frontend will handle filtering
        # This eliminates all timestamp parsing issues!
        return {"all_data": rows, "message": "Frontend will handle date filtering"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_channel_performance failed: {e}")

@router.get("/export/csv", tags=["roi"])
async def export_csv(
    user_id: str = Query(...),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        # start, end, _ = _resolve_range(range) # This line is removed
        # start_iso = start.isoformat()
        # end_iso = end.isoformat()
        
        # Use Supabase to get ROI metrics data - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "created_at": f"gte.{start_iso}", # This line is removed
                "created_at": f"lte.{end_iso}", # This line is removed
                "select": "platform,created_at,views,likes,comments,shares,clicks,ad_spend,revenue_generated,roi_percentage,roas_ratio",
                "order": "created_at.asc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch ROI metrics data for export")
            
        rows = response.json()
        
        def iter_csv():
            yield "platform,created_at,views,likes,comments,shares,clicks,ad_spend,revenue,roi,roas\n"
            for r in rows:
                yield f"{r.get('platform', '')},{r.get('created_at', '')},{r.get('views', 0)},{r.get('likes', 0)},{r.get('comments', 0)},{r.get('shares', 0)},{r.get('clicks', 0)},{r.get('ad_spend', 0)},{r.get('revenue_generated', 0)},{r.get('roi_percentage', 0)},{r.get('roas_ratio', 0)}\n"
        
        return StreamingResponse(iter_csv(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=roi_export.csv"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"export_csv failed: {e}")


@router.get("/export/pdf", tags=["roi"])
async def export_pdf(
    user_id: str = Query(...),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        # Minimal placeholder PDF export: return CSV content but with pdf header would be wrong; instead, construct simple PDF via PyMuPDF
        import fitz  # PyMuPDF
        # start, end, _ = _resolve_range(range) # This line is removed
        # start_iso = start.isoformat()
        # end_iso = end.isoformat()
        
        # Use Supabase to get ROI metrics data - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "created_at": f"gte.{start_iso}", # This line is removed
                "created_at": f"lte.{end_iso}", # This line is removed
                "select": "platform,revenue_generated,ad_spend,roi_percentage"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch ROI metrics data for PDF export")
            
        raw_rows = response.json()
        
        # Group by platform and calculate totals
        from collections import defaultdict
        platform_data = defaultdict(lambda: {"revenue": 0, "spend": 0, "roi_values": []})
        
        for row in raw_rows:
            platform = row.get("platform", "unknown")
            platform_data[platform]["revenue"] += float(row.get("revenue_generated", 0))
            platform_data[platform]["spend"] += float(row.get("ad_spend", 0))
            if row.get("roi_percentage") is not None:
                platform_data[platform]["roi_values"].append(float(row["roi_percentage"]))
        
        # Calculate averages and create final rows
        rows = []
        for platform, data in platform_data.items():
            avg_roi = sum(data["roi_values"]) / len(data["roi_values"]) if data["roi_values"] else 0
            rows.append({
                "platform": platform,
                "revenue": data["revenue"],
                "spend": data["spend"],
                "avg_roi": avg_roi
            })
        
        # Sort by revenue descending
        rows.sort(key=lambda x: x["revenue"], reverse=True)

        doc = fitz.open()
        page = doc.new_page()
        y = 50
        page.insert_text((50, y), f"ROI Report ({start.date()} to {end.date()})", fontsize=14)
        y += 30
        for r in rows:
            line = f"{r['platform']}: revenue ${float(r['revenue'] or 0):,.2f}, spend ${float(r['spend'] or 0):,.2f}, ROI {float(r['avg_roi'] or 0):.2f}%"
            page.insert_text((50, y), line, fontsize=11)
            y += 18

        pdf_bytes = doc.tobytes()
        doc.close()
        return StreamingResponse(iter([pdf_bytes]), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=roi_report.pdf"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"export_pdf failed: {e}")


@router.post("/generate-report", tags=["roi"])
async def generate_ai_report(
    user_id: str = Query(..., description="User ID (not used for data filtering)"),
    db = Depends(get_db),
):
    """
    Generate an AI-powered ROI report using Gemini.
    Retrieves ALL data from roi_metrics table, processes by platform,
    and generates a comprehensive report with insights and recommendations.
    Note: This endpoint accesses all data in roi_metrics table without user filtering or date restrictions.
    """
    try:
        # Try to import google.generativeai with better error handling
        try:
            import google.generativeai as genai
        except ImportError as e:
            print(f"Failed to import google.generativeai: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Google Generative AI library not installed. Please run: pip install google-generativeai"
            )
        
        import os
        from datetime import datetime, timedelta, timezone
        
        # Configure Gemini API
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        try:
            genai.configure(api_key=gemini_api_key)
            # Try gemini-1.5-flash first, fallback to gemini-pro
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                print("Using Gemini 1.5 Flash model")
            except Exception as flash_error:
                print(f"Gemini 1.5 Flash not available, trying Gemini Pro: {flash_error}")
                model = genai.GenerativeModel('gemini-pro')
                print("Using Gemini Pro model")
        except Exception as e:
            print(f"Failed to configure Gemini API: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to configure Gemini API: {str(e)}"
            )
        
        print("Fetching ALL data from roi_metrics table (no date or user filtering)...")
        
        # Fetch ALL data without date filtering
        all_data = await _fetch_all_roi_data()
        
        print(f"Total records retrieved: {len(all_data)}")
        
        if len(all_data) == 0:
            raise HTTPException(
                status_code=404,
                detail="No data found in roi_metrics table. Please ensure the table has data before generating reports."
            )
        
        # Process and summarize data by platform
        platform_summary = _summarize_data_by_platform(all_data)
        
        # Calculate overall totals
        overall_totals = _calculate_totals(platform_summary)
        
        # Prepare data for Gemini
        report_data = {
            "all_data": {
                "period": "All available data",
                "platforms": platform_summary,
                "totals": overall_totals,
                "total_records": len(all_data)
            }
        }
        
        # Generate report using Gemini
        prompt = _create_report_prompt_all_data(report_data)
        
        print("Generating report with Gemini...")
        try:
            response = model.generate_content(prompt)
            report_content = response.text
            
            if not report_content:
                raise HTTPException(
                    status_code=500, 
                    detail="Gemini API returned empty response"
                )
                
        except Exception as e:
            print(f"Failed to generate content with Gemini: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate report with Gemini: {str(e)}"
            )
        
        # Parse the report into structured sections
        structured_report = _parse_report_sections(report_content)
        
        return {
            "success": True,
            "report": structured_report,
            "raw_data": report_data,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in generate_ai_report: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"generate_ai_report failed: {str(e)}")


async def _fetch_all_roi_data() -> list:
    """Fetch ALL ROI metrics data without any filtering"""
    try:
        print("Fetching all data from roi_metrics table...")
        
        # Query all data without any filters
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "select": "platform,views,likes,comments,shares,clicks,ad_spend,revenue_generated,roi_percentage,content_type,content_category,created_at",
                "order": "platform.asc",
                "limit": "10000"  # Get up to 1000 records
            }
        )
        
        if response.status_code != 200:
            print(f"Query failed with status {response.status_code}")
            return []
        
        data = response.json()
        print(f"Retrieved {len(data)} records from roi_metrics")
        return data
        
    except Exception as e:
        print(f"Error in _fetch_all_roi_data: {str(e)}")
        return []


def _summarize_data_by_platform(data: list) -> dict:
    """Summarize ROI data by platform"""
    from collections import defaultdict
    
    platform_summary = defaultdict(lambda: {
        "total_views": 0,
        "total_likes": 0,
        "total_comments": 0,
        "total_shares": 0,
        "total_clicks": 0,
        "total_spend": 0.0,
        "total_revenue": 0.0,
        "roi_values": [],
        "content_types": defaultdict(int),
        "content_categories": defaultdict(int),
        "post_count": 0
    })
    
    for row in data:
        try:
            platform = row.get("platform", "unknown")
            summary = platform_summary[platform]
            
            # Safely convert values with error handling
            summary["total_views"] += int(row.get("views", 0) or 0)
            summary["total_likes"] += int(row.get("likes", 0) or 0)
            summary["total_comments"] += int(row.get("comments", 0) or 0)
            summary["total_shares"] += int(row.get("shares", 0) or 0)
            summary["total_clicks"] += int(row.get("clicks", 0) or 0)
            summary["total_spend"] += float(row.get("ad_spend", 0) or 0)
            summary["total_revenue"] += float(row.get("revenue_generated", 0) or 0)
            summary["post_count"] += 1
            
            if row.get("roi_percentage") is not None:
                try:
                    roi_value = float(row["roi_percentage"])
                    summary["roi_values"].append(roi_value)
                except (ValueError, TypeError):
                    pass  # Skip invalid ROI values
            
            content_type = row.get("content_type", "unknown")
            summary["content_types"][content_type] += 1
            
            content_category = row.get("content_category", "unknown")
            summary["content_categories"][content_category] += 1
            
        except Exception as e:
            print(f"Error processing row: {e}")
            continue
    
    # Calculate derived metrics
    result = {}
    for platform, summary in platform_summary.items():
        try:
            total_engagement = summary["total_likes"] + summary["total_comments"] + summary["total_shares"]
            total_impressions = summary["total_views"]
            
            avg_roi = sum(summary["roi_values"]) / len(summary["roi_values"]) if summary["roi_values"] else 0
            engagement_rate = (total_engagement / total_impressions * 100) if total_impressions > 0 else 0
            ctr = (summary["total_clicks"] / total_impressions * 100) if total_impressions > 0 else 0
            profit = summary["total_revenue"] - summary["total_spend"]
            profit_margin = (profit / summary["total_revenue"] * 100) if summary["total_revenue"] > 0 else 0
            
            result[platform] = {
                **summary,
                "avg_roi": avg_roi,
                "total_engagement": total_engagement,
                "engagement_rate": engagement_rate,
                "click_through_rate": ctr,
                "profit": profit,
                "profit_margin": profit_margin,
                "roas": summary["total_revenue"] / summary["total_spend"] if summary["total_spend"] > 0 else 0
            }
        except Exception as e:
            print(f"Error calculating metrics for platform {platform}: {e}")
            continue
    
    return result


def _calculate_totals(platform_summary: dict) -> dict:
    """Calculate totals across all platforms"""
    totals = {
        "total_views": 0,
        "total_engagement": 0,
        "total_clicks": 0,
        "total_spend": 0.0,
        "total_revenue": 0.0,
        "total_profit": 0.0,
        "post_count": 0
    }
    
    for platform_data in platform_summary.values():
        totals["total_views"] += platform_data["total_views"]
        totals["total_engagement"] += platform_data["total_engagement"]
        totals["total_clicks"] += platform_data["total_clicks"]
        totals["total_spend"] += platform_data["total_spend"]
        totals["total_revenue"] += platform_data["total_revenue"]
        totals["total_profit"] += platform_data["profit"]
        totals["post_count"] += platform_data["post_count"]
    
    if totals["total_spend"] > 0:
        totals["overall_roi"] = (totals["total_profit"] / totals["total_spend"]) * 100
        totals["overall_roas"] = totals["total_revenue"] / totals["total_spend"]
    else:
        totals["overall_roi"] = 0
        totals["overall_roas"] = 0
    
    if totals["total_views"] > 0:
        totals["overall_engagement_rate"] = (totals["total_engagement"] / totals["total_views"]) * 100
        totals["overall_ctr"] = (totals["total_clicks"] / totals["total_views"]) * 100
    else:
        totals["overall_engagement_rate"] = 0
        totals["overall_ctr"] = 0
    
    return totals


def _calculate_month_over_month_changes(current: dict, previous: dict) -> dict:
    """Calculate month-over-month changes"""
    changes = {}
    
    # Calculate changes for each platform
    all_platforms = set(current.keys()) | set(previous.keys())
    
    for platform in all_platforms:
        current_data = current.get(platform, {})
        previous_data = previous.get(platform, {})
        
        changes[platform] = {
            "revenue_change": _calculate_percentage_change(
                previous_data.get("total_revenue", 0),
                current_data.get("total_revenue", 0)
            ),
            "spend_change": _calculate_percentage_change(
                previous_data.get("total_spend", 0),
                current_data.get("total_spend", 0)
            ),
            "roi_change": _calculate_percentage_change(
                previous_data.get("avg_roi", 0),
                current_data.get("avg_roi", 0)
            ),
            "engagement_change": _calculate_percentage_change(
                previous_data.get("engagement_rate", 0),
                current_data.get("engagement_rate", 0)
            ),
            "views_change": _calculate_percentage_change(
                previous_data.get("total_views", 0),
                current_data.get("total_views", 0)
            )
        }
    
    # Calculate overall changes
    current_totals = _calculate_totals(current)
    previous_totals = _calculate_totals(previous)
    
    changes["overall"] = {
        "revenue_change": _calculate_percentage_change(
            previous_totals.get("total_revenue", 0),
            current_totals.get("total_revenue", 0)
        ),
        "spend_change": _calculate_percentage_change(
            previous_totals.get("total_spend", 0),
            current_totals.get("total_spend", 0)
        ),
        "roi_change": _calculate_percentage_change(
            previous_totals.get("overall_roi", 0),
            current_totals.get("overall_roi", 0)
        ),
        "engagement_change": _calculate_percentage_change(
            previous_totals.get("overall_engagement_rate", 0),
            current_totals.get("overall_engagement_rate", 0)
        )
    }
    
    return changes


def _calculate_percentage_change(previous: float, current: float) -> float:
    """Calculate percentage change between two values"""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - previous) / previous) * 100


def _create_report_prompt_all_data(data: dict) -> str:
    """Create a comprehensive prompt for Gemini to generate the report from all available data"""
    
    prompt = f"""
You are a marketing analytics expert. Generate a comprehensive ROI report based on ALL available data from the roi_metrics table.

REPORT DATA:
{data}

Please create a professional marketing ROI report with the following structure:

# Executive Summary
- Brief overview of overall performance
- Key highlights and achievements
- Total data analyzed and scope

# Performance Overview
- Total revenue, spend, and profit analysis
- Overall ROI and ROAS metrics
- Platform distribution and performance

# Platform Performance Analysis
For each platform, provide:
- Revenue and spend breakdown
- ROI and engagement metrics
- Performance insights and trends
- Content type and category analysis
- Post count and average performance

# Key Insights
- Top performing platforms
- Areas of concern or opportunity
- Notable trends and patterns
- Content performance insights
- Engagement rate analysis

# Recommendations
- Strategic recommendations for improvement
- Platform-specific optimization suggestions
- Budget allocation recommendations
- Content strategy suggestions
- Performance optimization opportunities

# Action Items
- Priority actions for improvement
- Specific metrics to focus on
- Testing opportunities
- Next steps for optimization

Please format the report professionally with clear sections, bullet points where appropriate, and actionable insights. Focus on providing valuable business intelligence that can drive decision-making. Since this is analyzing all available data, provide comprehensive insights across all platforms and content types.
"""
    
    return prompt


def _create_report_prompt(data: dict) -> str:
    """Create a comprehensive prompt for Gemini to generate the report"""
    
    prompt = f"""
You are a marketing analytics expert. Generate a comprehensive ROI report based on the following data.

REPORT DATA:
{data}

Please create a professional marketing ROI report with the following structure:

# Executive Summary
- Brief overview of performance
- Key highlights and achievements
- Overall ROI performance

# Performance Overview
- Total revenue, spend, and profit analysis
- Overall ROI and ROAS metrics
- Month-over-month performance comparison

# Platform Performance Analysis
For each platform, provide:
- Revenue and spend breakdown
- ROI and engagement metrics
- Performance trends and insights
- Content type and category analysis

# Key Insights
- Top performing platforms
- Areas of concern
- Notable trends and patterns
- Content performance insights

# Recommendations
- Strategic recommendations for improvement
- Platform-specific optimization suggestions
- Budget allocation recommendations
- Content strategy suggestions

# Action Items
- Priority actions for next month
- Specific metrics to focus on
- Testing opportunities

Please format the report professionally with clear sections, bullet points where appropriate, and actionable insights. Focus on providing valuable business intelligence that can drive decision-making.
"""
    
    return prompt


def _parse_report_sections(report_content: str) -> dict:
    """Parse the generated report into structured sections"""
    sections = {
        "executive_summary": "",
        "performance_overview": "",
        "platform_analysis": "",
        "key_insights": "",
        "recommendations": "",
        "action_items": ""
    }
    
    current_section = None
    lines = report_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect section headers
        if line.startswith('# Executive Summary'):
            current_section = "executive_summary"
            continue
        elif line.startswith('# Performance Overview'):
            current_section = "performance_overview"
            continue
        elif line.startswith('# Platform Performance Analysis'):
            current_section = "platform_analysis"
            continue
        elif line.startswith('# Key Insights'):
            current_section = "key_insights"
            continue
        elif line.startswith('# Recommendations'):
            current_section = "recommendations"
            continue
        elif line.startswith('# Action Items'):
            current_section = "action_items"
            continue
        
        # Add content to current section
        if current_section and current_section in sections:
            if sections[current_section]:
                sections[current_section] += "\n"
            sections[current_section] += line
    
    return sections


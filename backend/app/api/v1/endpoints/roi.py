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

router = APIRouter()

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


def _resolve_range(range_key: str) -> tuple[datetime, datetime, str]:
    now = datetime.now(timezone.utc)
    if range_key == "7d":
        start = now - timedelta(days=7)
        bucket = "day"
    elif range_key == "30d":
        start = now - timedelta(days=30)
        bucket = "day"
    elif range_key == "90d":
        start = now - timedelta(days=90)
        bucket = "day"
    elif range_key == "1y":
        start = now - timedelta(days=365)
        bucket = "day"
    else:
        # default to 7d
        start = now - timedelta(days=7)
        bucket = "day"
    return start, now, bucket


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
    user_id: str = Query(..., description="Clerk user id"),
    range: str = Query("7d", pattern="^(7d|30d|90d|1y)$"),
    db = Depends(get_db),
):
    try:
        start, end, bucket = _resolve_range(range)
        # Convert to ISO format for Supabase
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        
        # Use Supabase to query roi_metrics table - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "update_timestamp": f"gte.{start_iso}",
                "update_timestamp": f"lte.{end_iso}",
                "order": "update_timestamp.asc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch ROI trends data")
            
        rows = response.json()
        
        # Group by date and calculate average ROI
        from collections import defaultdict
        daily_roi = defaultdict(list)
        
        for row in rows:
            date_key = row["update_timestamp"][:10]  # YYYY-MM-DD
            if row.get("roi") is not None:
                daily_roi[date_key].append(float(row["roi"]))
        
        # Calculate average ROI per day
        series = []
        for date_key in sorted(daily_roi.keys()):
            avg_roi = sum(daily_roi[date_key]) / len(daily_roi[date_key])
            series.append({
                "ts": f"{date_key}T00:00:00Z",
                "roi": avg_roi
            })
        
        return {"series": series, "bucket": bucket}
    except HTTPException:
        raise
    except Exception as e:
        # surface error
        raise HTTPException(status_code=500, detail=f"get_roi_trends failed: {e}")


@router.get("/campaigns-in-range", tags=["roi"])
async def get_campaign_markers(
    user_id: str = Query(..., description="Clerk user id"),
    range: str = Query("7d", pattern="^(7d|30d|90d|1y)$"),
    db = Depends(get_db),
):
    try:
        start, end, _ = _resolve_range(range)
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        
        # Use Supabase to query campaigns table - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "campaigns",
            params={
                "start_date": f"gte.{start_iso}",
                "end_date": f"lte.{end_iso}",
                "order": "start_date.asc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch campaigns data")
            
        rows = response.json()
        markers = [{"id": r["id"], "name": r["name"], "date": r["start_date"]} for r in rows]
        return {"campaigns": markers}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_campaign_markers failed: {e}")


@router.get("/overview", tags=["roi"])
async def get_overview(
    user_id: str = Query(..., description="Clerk user id"),
    range: str = Query("7d", pattern="^(7d|30d|90d|1y)$"),
    db = Depends(get_db),
):
    try:
        start, end, _ = _resolve_range(range)
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        cache_key = f"overview:{user_id}:{start_iso}:{end_iso}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        # Mark this user as active so the writer prioritizes them from DB
        await _mark_user_active(db, user_id)
        
        # Use Supabase to get overview data - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "update_timestamp": f"gte.{start_iso}",
                "update_timestamp": f"lte.{end_iso}",
                "order": "update_timestamp.desc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch overview data")
            
        rows = response.json()
        
        # Calculate overview metrics from the data
        if rows:
            total_revenue = sum(float(r.get("revenue_generated", 0)) for r in rows)
            total_spend = sum(float(r.get("ad_spend", 0)) for r in rows)
            total_roi = (total_revenue - total_spend) / total_spend * 100 if total_spend > 0 else 0
            total_views = sum(int(r.get("views", 0)) for r in rows)
            total_engagement = sum(int(r.get("likes", 0) or 0) + int(r.get("comments", 0) or 0) + int(r.get("shares", 0) or 0) for r in rows)
            
            result = {
                "total_revenue": total_revenue,
                "total_spend": total_spend,
                "total_roi": total_roi,
                "total_views": total_views,
                "total_engagement": total_engagement,
                "period_start": start_iso,
                "period_end": end_iso
            }
        else:
            result = {}
            
        cache.set(cache_key, result, ttl_seconds=2700)  # 45 minutes
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_overview failed: {e}")


@router.get("/revenue/by-source", tags=["roi"])
async def get_revenue_by_source(
    user_id: str = Query(...),
    range: str = Query("7d", pattern="^(7d|30d|90d|1y)$"),
    db = Depends(get_db),
):
    try:
        start, end, _ = _resolve_range(range)
        # Mark as active so writer scopes to this user
        await _mark_user_active(db, user_id)
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        
        # Use Supabase to get revenue by source data - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "update_timestamp": f"gte.{start_iso}",
                "update_timestamp": f"lte.{end_iso}",
                "select": "platform,revenue_generated,update_timestamp"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch revenue by source data")
            
        rows = response.json()
        
        # Group by platform and calculate total revenue
        from collections import defaultdict
        revenue_by_platform = defaultdict(float)
        
        for row in rows:
            platform = row.get("platform", "unknown")
            revenue = float(row.get("revenue_generated", 0))
            revenue_by_platform[platform] += revenue
        
        # Convert to list format
        result_rows = [{"platform": platform, "revenue": revenue} for platform, revenue in revenue_by_platform.items()]
        
        return {"rows": result_rows}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_revenue_by_source failed: {e}")


@router.get("/revenue/trends", tags=["roi"])
async def get_revenue_trends(
    user_id: str = Query(...),
    range: str = Query("7d", pattern="^(7d|30d|90d|1y)$"),
    db = Depends(get_db),
):
    try:
        start, end, bucket = _resolve_range(range)
        # Mark as active so writer scopes to this user
        await _mark_user_active(db, user_id)
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        
        # Use Supabase to get revenue trends data - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "update_timestamp": f"gte.{start_iso}",
                "update_timestamp": f"lte.{end_iso}",
                "select": "revenue_generated,update_timestamp",
                "order": "update_timestamp.asc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch revenue trends data")
            
        rows = response.json()
        
        # Group by date and calculate daily revenue
        from collections import defaultdict
        daily_revenue = defaultdict(float)
        
        for row in rows:
            date_key = row["update_timestamp"][:10]  # YYYY-MM-DD
            revenue = float(row.get("revenue_generated", 0))
            daily_revenue[date_key] += revenue
        
        # Convert to list format
        result_rows = [{"date": date, "revenue": revenue} for date, revenue in sorted(daily_revenue.items())]
        
        return {"rows": result_rows, "bucket": bucket}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_revenue_trends failed: {e}")


@router.get("/cost/breakdown", tags=["roi"])
async def get_cost_breakdown(
    user_id: str = Query(...),
    range: str = Query("7d", pattern="^(7d|30d|90d|1y)$"),
    db = Depends(get_db),
):
    try:
        start, end, _ = _resolve_range(range)
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        
        # Use Supabase to get cost breakdown data - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "update_timestamp": f"gte.{start_iso}",
                "update_timestamp": f"lte.{end_iso}",
                "select": "platform,ad_spend,update_timestamp"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch cost breakdown data")
            
        rows = response.json()
        
        # Group by platform and calculate total spend
        from collections import defaultdict
        spend_by_platform = defaultdict(float)
        
        for row in rows:
            platform = row.get("platform", "unknown")
            spend = float(row.get("ad_spend", 0))
            spend_by_platform[platform] += spend
        
        # Convert to list format
        result_rows = [{"platform": platform, "spend": spend} for platform, spend in spend_by_platform.items()]
        
        return {"rows": result_rows}
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
                "update_timestamp": f"gte.{start_date}",
                "update_timestamp": f"lte.{end_date}",
                "select": "ad_spend,update_timestamp",
                "order": "update_timestamp.asc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch monthly spend trends data")
            
        rows = response.json()
        
        # Group by month and calculate monthly spend
        from collections import defaultdict
        monthly_spend = defaultdict(float)
        
        for row in rows:
            month_key = row["update_timestamp"][:7]  # YYYY-MM
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
    user_id: str = Query(...),
    range: str = Query("7d", pattern="^(7d|30d|90d|1y)$"),
    db = Depends(get_db),
):
    try:
        start, end, _ = _resolve_range(range)
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        
        # Use Supabase to get CLV data - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "update_timestamp": f"gte.{start_iso}",
                "update_timestamp": f"lte.{end_iso}",
                "select": "revenue_generated,ad_spend,views,clicks"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch CLV data")
            
        rows = response.json()
        
        # Calculate CLV metrics
        if rows:
            total_revenue = sum(float(r.get("revenue_generated", 0)) for r in rows)
            total_spend = sum(float(r.get("ad_spend", 0)) for r in rows)
            total_views = sum(int(r.get("views", 0)) for r in rows)
            total_clicks = sum(int(r.get("clicks", 0)) for r in rows)
            
            # Calculate CLV (Customer Lifetime Value)
            # This is a simplified calculation - you might want to adjust based on your business logic
            avg_order_value = total_revenue / len(rows) if rows else 0
            purchase_frequency = len(rows) / 30 if total_views > 0 else 0  # Assuming 30-day period
            customer_lifespan = 12  # Assuming 12 months average customer lifespan
            clv = avg_order_value * purchase_frequency * customer_lifespan
            
            result = {
                "clv": clv,
                "avg_order_value": avg_order_value,
                "purchase_frequency": purchase_frequency,
                "customer_lifespan": customer_lifespan,
                "total_revenue": total_revenue,
                "total_spend": total_spend,
                "total_views": total_views,
                "total_clicks": total_clicks
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
    user_id: str = Query(...),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        start, end, _ = _resolve_range(range)
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        
        # Use Supabase to get CAC data - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "update_timestamp": f"gte.{start_iso}",
                "update_timestamp": f"lte.{end_iso}",
                "select": "ad_spend,clicks,views"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch CAC data")
            
        rows = response.json()
        
        # Calculate CAC metrics
        if rows:
            total_spend = sum(float(r.get("ad_spend", 0)) for r in rows)
            total_clicks = sum(int(r.get("clicks", 0)) for r in rows)
            total_views = sum(int(r.get("views", 0)) for r in rows)
            
            # Calculate CAC (Customer Acquisition Cost)
            cac = total_spend / total_clicks if total_clicks > 0 else 0
            cpm = (total_spend / total_views) * 1000 if total_views > 0 else 0  # Cost per mille (thousand impressions)
            ctr = (total_clicks / total_views) * 100 if total_views > 0 else 0  # Click-through rate
            
            result = {
                "cac": cac,
                "cpm": cpm,
                "ctr": ctr,
                "total_spend": total_spend,
                "total_clicks": total_clicks,
                "total_views": total_views
            }
        else:
            result = {}
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_cac failed: {e}")


@router.get("/roi/trends", tags=["roi"])
async def get_roi_trends_daily(
    user_id: str = Query(...),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        start, end, _ = _resolve_range(range)
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        
        # Use Supabase to get ROI trends data - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "update_timestamp": f"gte.{start_iso}",
                "update_timestamp": f"lte.{end_iso}",
                "select": "roi_percentage,update_timestamp",
                "order": "update_timestamp.asc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch ROI trends data")
            
        rows = response.json()
        
        # Group by date and calculate average ROI
        from collections import defaultdict
        daily_roi = defaultdict(list)
        
        for row in rows:
            date_key = row["update_timestamp"][:10]  # YYYY-MM-DD
            if row.get("roi_percentage") is not None:
                daily_roi[date_key].append(float(row["roi_percentage"]))
        
        # Calculate average ROI per day
        result_rows = []
        for date_key in sorted(daily_roi.keys()):
            avg_roi = sum(daily_roi[date_key]) / len(daily_roi[date_key])
            result_rows.append({
                "date": date_key,
                "roi": avg_roi
            })
        
        return {"rows": result_rows}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_roi_trends_daily failed: {e}")


@router.get("/channel/performance", tags=["roi"])
async def get_channel_performance(
    user_id: str = Query(...),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),
    db = Depends(get_db),
):
    try:
        start, end, _ = _resolve_range(range)
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        
        # Use Supabase to get channel performance data - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "update_timestamp": f"gte.{start_iso}",
                "update_timestamp": f"lte.{end_iso}",
                "select": "platform,views,likes,comments,shares,clicks,revenue_generated,ad_spend,roi_percentage",
                "order": "platform.asc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch channel performance data")
            
        rows = response.json()
        
        # Group by platform and calculate metrics
        from collections import defaultdict
        platform_metrics = defaultdict(lambda: {
            "impressions": 0,
            "engagement": 0,
            "revenue": 0,
            "spend": 0,
            "clicks": 0,
            "roi_values": []
        })
        
        for row in rows:
            platform = row.get("platform", "unknown")
            platform_metrics[platform]["impressions"] += int(row.get("views", 0))
            platform_metrics[platform]["engagement"] += int(row.get("likes", 0) or 0) + int(row.get("comments", 0) or 0) + int(row.get("shares", 0) or 0)
            platform_metrics[platform]["revenue"] += float(row.get("revenue_generated", 0))
            platform_metrics[platform]["spend"] += float(row.get("ad_spend", 0))
            platform_metrics[platform]["clicks"] += int(row.get("clicks", 0))
            if row.get("roi_percentage") is not None:
                platform_metrics[platform]["roi_values"].append(float(row["roi_percentage"]))
        
        # Calculate derived metrics
        derived = []
        for platform, metrics in platform_metrics.items():
            impressions = float(metrics["impressions"])
            engagement = float(metrics["engagement"])
            revenue = float(metrics["revenue"])
            spend = float(metrics["spend"])
            clicks = float(metrics["clicks"])
            
            engagement_rate = (engagement / impressions) * 100 if impressions > 0 else 0
            ctr = (clicks / impressions) * 100 if impressions > 0 else 0
            profit = revenue - spend
            avg_roi = sum(metrics["roi_values"]) / len(metrics["roi_values"]) if metrics["roi_values"] else 0
            efficiency = avg_roi * (engagement / impressions) if impressions > 0 else 0
            
            derived.append({
                "platform": platform,
                "impressions": impressions,
                "engagement": engagement,
                "revenue": revenue,
                "spend": spend,
                "total_clicks": clicks,
                "avg_roi": avg_roi,
                "profit": profit,
                "engagement_rate": engagement_rate,
                "click_through_rate": ctr,
                "efficiency_score": efficiency
            })
        
        return {"rows": derived}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_channel_performance failed: {e}")

@router.get("/export/csv", tags=["roi"])
async def export_csv(
    user_id: str = Query(...),
    range: str = Query("7d", pattern="^(7d|30d|90d|1y)$"),
    db = Depends(get_db),
):
    try:
        start, end, _ = _resolve_range(range)
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        
        # Use Supabase to get ROI metrics data - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "update_timestamp": f"gte.{start_iso}",
                "update_timestamp": f"lte.{end_iso}",
                "select": "platform,update_timestamp,views,likes,comments,shares,clicks,ad_spend,revenue_generated,roi_percentage,roas_ratio",
                "order": "update_timestamp.asc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch ROI metrics data for export")
            
        rows = response.json()
        
        def iter_csv():
            yield "platform,update_timestamp,views,likes,comments,shares,clicks,ad_spend,revenue,roi,roas\n"
            for r in rows:
                yield f"{r.get('platform', '')},{r.get('update_timestamp', '')},{r.get('views', 0)},{r.get('likes', 0)},{r.get('comments', 0)},{r.get('shares', 0)},{r.get('clicks', 0)},{r.get('ad_spend', 0)},{r.get('revenue_generated', 0)},{r.get('roi_percentage', 0)},{r.get('roas_ratio', 0)}\n"
        
        return StreamingResponse(iter_csv(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=roi_export.csv"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"export_csv failed: {e}")


@router.get("/export/pdf", tags=["roi"])
async def export_pdf(
    user_id: str = Query(...),
    range: str = Query("7d", pattern="^(7d|30d|90d|1y)$"),
    db = Depends(get_db),
):
    try:
        # Minimal placeholder PDF export: return CSV content but with pdf header would be wrong; instead, construct simple PDF via PyMuPDF
        import fitz  # PyMuPDF
        start, end, _ = _resolve_range(range)
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        
        # Use Supabase to get ROI metrics data - removed user_id filtering
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "update_timestamp": f"gte.{start_iso}",
                "update_timestamp": f"lte.{end_iso}",
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


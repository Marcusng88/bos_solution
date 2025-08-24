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


@router.post("/generate-report", tags=["roi"])
async def generate_ai_report(
    user_id: str = Query(..., description="User ID (not used for data filtering)"),
    db = Depends(get_db),
):
    """
    Generate an AI-powered ROI report using Gemini with multiple formats (TXT, HTML, PDF).
    Retrieves ALL data from roi_metrics table, processes by platform,
    and generates a comprehensive report with insights and recommendations.
    Note: This endpoint accesses all data in roi_metrics table without user filtering or date restrictions.
    """
    try:
        # Import the report generation function from the standalone script
        import sys
        import os
        from pathlib import Path
        
        # Add the backend directory to the path to import the report generation module
        backend_dir = Path(__file__).parent.parent.parent.parent
        sys.path.append(str(backend_dir))
        
        try:
            from generate_roi_report import generate_roi_report
        except ImportError as e:
            print(f"Failed to import generate_roi_report: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Report generation module not available. Please ensure generate_roi_report.py is in the backend directory."
            )
        
        print("Generating comprehensive ROI report with multiple formats...")
        
        # Generate the report using the standalone function
        success = await generate_roi_report()
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate ROI report. Please check the logs for more details."
            )
        
        # Find the latest generated files
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Return success response with file information
        return {
            "success": True,
            "message": "ROI report generated successfully in multiple formats",
            "files": {
                "text": f"roi_report_{timestamp}.txt",
                "html": f"roi_report_{timestamp}.html", 
                "pdf": f"roi_report_{timestamp}.pdf",
                "json": f"roi_data_{timestamp}.json"
            },
            "generated_at": datetime.now().isoformat()
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
                "select": "platform,views,likes,comments,shares,clicks,ad_spend,revenue_generated,roi_percentage,content_type,content_category,update_timestamp",
                "order": "platform.asc",
                "limit": "1000"  # Get up to 1000 records
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


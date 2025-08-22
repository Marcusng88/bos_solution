"""
ROI Data Generation Scaffold (placeholders)
Implements multiplier-based growth and financial calculations per ROI_IMPLEMENTATION_PLAN.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Tuple
import math
import random

Platform = Literal["facebook", "instagram", "youtube"]


@dataclass
class BaseMetrics:
    views: int = 1
    likes: int = 1
    comments: int = 1
    shares: int = 1
    clicks: int = 1


PLATFORM_COST_MODELS: Dict[Platform, Dict[str, Dict[str, float] | float]] = {
    "facebook": {
        "cpc_range": {"min": 0.50, "max": 2.50},
        "cpm_range": {"min": 5.00, "max": 25.00},
        "engagement_multiplier": 1.2,
    },
    "instagram": {
        "cpc_range": {"min": 0.80, "max": 3.00},
        "cpm_range": {"min": 6.00, "max": 30.00},
        "engagement_multiplier": 1.5,
    },
    "youtube": {
        "cpc_range": {"min": 0.30, "max": 1.50},
        "cpm_range": {"min": 3.00, "max": 15.00},
        "engagement_multiplier": 1.0,
    },
}


def random_in_range(min_value: float, max_value: float) -> float:
    return random.random() * (max_value - min_value) + min_value


def _seasonal_multiplier(dt_minutes: int) -> float:
    # Simple weekly seasonality: peak mid-week, dip weekend
    # dt_minutes can be used to vary over time; keep simple here
    # Never go below 1.0 to prevent decreasing values
    # Reduced range for more stable ROI (1.0 to 1.05 instead of 1.0 to 1.1)
    return random_in_range(1.0, 1.05)


def _content_type_multiplier(content_type: str) -> Dict[str, float]:
    # Realistic content-type weights based on social media behavior
    mapping = {
        "video": {"views": 1.4, "likes": 1.2, "comments": 1.1, "shares": 1.3, "clicks": 1.4},     # Videos get more views AND clicks
        "post": {"views": 1.0, "likes": 1.0, "comments": 1.0, "shares": 1.0, "clicks": 1.0},      # Standard post baseline
        "story": {"views": 0.8, "likes": 0.7, "comments": 0.5, "shares": 0.3, "clicks": 0.9},      # Stories get less engagement but some clicks
        "reel": {"views": 1.6, "likes": 1.3, "comments": 1.05, "shares": 1.4, "clicks": 1.6},     # Reels get highest views AND clicks
    }
    return mapping.get(content_type, mapping["post"])


def generate_realistic_update(current: BaseMetrics, hours_elapsed: int = 1, *, content_type: str = "video") -> BaseMetrics:
    # Ensure minimum growth factor of 1.0 (no decrease)
    min_growth = 1.0
    
    # More stable growth ranges - smaller variance for consistent ROI
    base_growth = 1.15  # 15% base growth per hour instead of random 1.05-2.5
    max_growth = min(1.5, base_growth + (100 / max(current.views, 1)))  # Reduced from 2.5
    
    # Seasonal variation (but never below 1.0) - reduced range
    season = max(1.0, _seasonal_multiplier(hours_elapsed * 60))
    ctype = _content_type_multiplier(content_type)

    # Calculate growth factors with realistic social media patterns
    growth = {
        "views": max(min_growth, random_in_range(1.20, max_growth) * season * ctype["views"]),      # High growth (20%+)
        "likes": max(min_growth, random_in_range(1.08, 1.25) * season * ctype["likes"]),           # Moderate growth (8-25%)
        "comments": max(min_growth, random_in_range(1.03, 1.18) * season * ctype["comments"]),     # Low growth (3-18%)
        "shares": max(min_growth, random_in_range(1.05, 1.20) * season * ctype["shares"]),         # Low growth (5-20%)
        "clicks": max(min_growth, random_in_range(1.15, max_growth) * season * ctype["clicks"]),   # High growth like views (15%+)
    }

    # Ensure final values are never less than current values
    return BaseMetrics(
        views=max(current.views, min(int(round(current.views * growth["views"])), 1_000_000)),
        likes=max(current.likes, min(int(round(current.likes * growth["likes"])), 500_000)),
        comments=max(current.comments, min(int(round(current.comments * growth["comments"])), 100_000)),
        shares=max(current.shares, min(int(round(current.shares * growth["shares"])), 200_000)),
        clicks=max(current.clicks, min(int(round(current.clicks * growth["clicks"])), 300_000)),
    )


def calculate_financial_metrics(platform: Platform, m: BaseMetrics) -> Dict[str, float]:
    costs = PLATFORM_COST_MODELS[platform]
    
    # Use more stable cost ranges with smaller variance
    cpc_base = (costs["cpc_range"]["min"] + costs["cpc_range"]["max"]) / 2
    cpm_base = (costs["cpm_range"]["min"] + costs["cpm_range"]["max"]) / 2
    
    # Add small random variation (±10% instead of full range)
    cpc = cpc_base * random_in_range(0.9, 1.1)
    cpm = cpm_base * random_in_range(0.9, 1.1)

    ad_spend = (m.clicks * cpc) + (m.views * cpm / 1000)

    return {
        "ad_spend": round(ad_spend, 2),
        "cost_per_click": round(cpc, 2),
        "cost_per_impression": round(cpm / 1000, 4),
        "roi_percentage": 0.0,
        "roas_ratio": 0.0,
    }


def calculate_revenue(platform: Platform, m: BaseMetrics) -> Dict[str, int | float]:
    # More realistic conversion rates that scale with engagement
    base_conversion_rate = 0.08  # Reduced from 15% to 8% for more realistic ROI
    platform_multiplier = float(PLATFORM_COST_MODELS[platform]["engagement_multiplier"])  # type: ignore[index]
    
    # Calculate engagement rate (likes + comments + shares) / views
    engagement_rate = (m.likes + m.comments + m.shares) / max(m.views, 1)
    
    # More conservative engagement boost to prevent extreme ROI swings
    engagement_boost = min(1.5, 1 + (engagement_rate * 5))  # Cap at 2.5x boost instead of 3x
    
    # Calculate final conversion rate with realistic floor and ceiling
    adjusted_conversion_rate = max(0.02, min(0.25, base_conversion_rate * platform_multiplier * engagement_boost))

    avg_order_value = {
        "facebook": 45,
        "instagram": 65,
        "youtube": 80,
    }[platform]

    # Ensure conversions are realistic and don't cause extreme ROI
    conversions = max(0, int(round(m.clicks * adjusted_conversion_rate)))
    revenue = float(round(conversions * avg_order_value))
    
    return {"conversions": conversions, "revenue": revenue}


def finalize_roi(ad_spend: float, revenue: float, engagement_quality: float = 1.0) -> Tuple[float, float]:
    if ad_spend <= 0:
        return 0.0, 0.0
    
    # Base ROI calculation
    base_roi_pct = ((revenue - ad_spend) / ad_spend) * 100.0
    
    # Adjust ROI based on engagement quality to make it more realistic
    # Higher engagement = more stable, realistic ROI
    engagement_stability = min(2.0, max(0.5, engagement_quality))
    
    # Cap ROI to realistic ranges based on engagement
    if engagement_quality > 0.1:  # Good engagement
        # Cap ROI between -50% and +200% for realistic business performance
        adjusted_roi = max(-50.0, min(200.0, base_roi_pct))
    else:  # Poor engagement
        # Cap ROI between -80% and +100% for poor performing content
        adjusted_roi = max(-80.0, min(100.0, base_roi_pct))
    
    # Apply engagement stability factor
    final_roi = adjusted_roi * engagement_stability
    
    # Ensure ROI stays within realistic bounds
    final_roi = max(-100.0, min(300.0, final_roi))
    
    roas = (revenue / ad_spend)
    return round(final_roi, 2), round(roas, 2)


# Placeholder for integration layer: fetch active metrics, write rows, schedule
class DataGeneratorService:
    def __init__(self):
        pass

    def step(self, platform: Platform, current: BaseMetrics, hour: int) -> Dict[str, object]:
        updated = generate_realistic_update(current, hours_elapsed=hour)
        fin = calculate_financial_metrics(platform, updated)
        rev = calculate_revenue(platform, updated)
        
        # Calculate engagement quality for ROI stability
        engagement_quality = (updated.likes + updated.comments + updated.shares) / max(updated.views, 1)
        
        roi_pct, roas = finalize_roi(fin["ad_spend"], rev["revenue"], engagement_quality)  # type: ignore[arg-type]
        fin["roi_percentage"] = roi_pct
        fin["roas_ratio"] = roas

        return {
            "metrics": updated,
            "financial": fin,
            "revenue": rev,
        }

    def generate_metrics(self, base_metrics: BaseMetrics, platform: Platform = "youtube") -> BaseMetrics:
        """
        Generate new metrics based on base metrics with growth calculations.
        This method is used by the updated ROI writer.
        """
        # Generate updated metrics with 1 hour of growth
        updated = generate_realistic_update(base_metrics, hours_elapsed=1, content_type="video")
        
        # Calculate financial metrics
        fin = calculate_financial_metrics(platform, updated)
        rev = calculate_revenue(platform, updated)
        
        # Calculate engagement quality for ROI stability
        engagement_quality = (updated.likes + updated.comments + updated.shares) / max(updated.views, 1)
        
        roi_pct, roas = finalize_roi(fin["ad_spend"], rev["revenue"], engagement_quality)
        
        # Create a new BaseMetrics object with financial data attached
        # We'll extend BaseMetrics to include financial fields for the ROI writer
        class ExtendedMetrics(BaseMetrics):
            def __init__(self, base: BaseMetrics, financial: Dict[str, float], revenue: Dict[str, float]):
                super().__init__(
                    views=base.views,
                    likes=base.likes,
                    comments=base.comments,
                    shares=base.shares,
                    clicks=base.clicks
                )
                self.ad_spend = financial["ad_spend"]
                self.revenue_generated = revenue["revenue"]
                self.cost_per_click = financial["cost_per_click"]
                self.cost_per_impression = financial["cost_per_impression"]
                self.roi_percentage = financial["roi_percentage"]
                self.roas_ratio = financial["roas_ratio"]
        
        return ExtendedMetrics(updated, fin, rev)



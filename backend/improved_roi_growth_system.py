#!/usr/bin/env python3
"""
Improved ROI Growth System - Corrected Decay Logic
- Engagement metrics (views, likes, etc.) always increase (cumulative)
- Growth RATES decay over time
- Revenue conversion rates decline for older content
- Content age determines growth phase, not just view count
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple
from datetime import datetime, timezone
import random
import math

@dataclass
class ContentMetrics:
    """Current cumulative metrics for a piece of content"""
    views: int = 100
    likes: int = 8
    comments: int = 2
    shares: int = 5
    saves: int = 2
    clicks: int = 6
    
    # Financial metrics
    ad_spend: float = 0.0
    revenue_generated: float = 0.0
    
    # Metadata
    created_date: datetime = None
    last_updated: datetime = None

@dataclass 
class GrowthRates:
    """Growth rates per hour for different metrics"""
    new_views_per_hour: float = 10.0
    new_likes_per_hour: float = 1.0
    new_comments_per_hour: float = 0.2
    new_shares_per_hour: float = 0.5
    new_saves_per_hour: float = 0.3
    new_clicks_per_hour: float = 0.8
    
    # Conversion metrics
    click_through_rate: float = 0.04    # 4% of views become clicks
    conversion_rate: float = 0.025      # 2.5% of clicks become sales
    revenue_multiplier: float = 1.0     # Penalty for old content

def calculate_content_age_days(created_date: datetime) -> int:
    """Calculate how many days old the content is"""
    if not created_date:
        return 0
    
    now = datetime.now(timezone.utc)
    if created_date.tzinfo is None:
        created_date = created_date.replace(tzinfo=timezone.utc)
    
    age_delta = now - created_date
    return age_delta.days

def determine_growth_phase(age_days: int) -> str:
    """Determine growth phase based on content age"""
    if age_days <= 7:
        return "launch"
    elif age_days <= 30:
        return "growth"
    elif age_days <= 90:
        return "plateau"
    else:
        return "decay"

def get_growth_rates_for_phase(phase: str, platform: str = "instagram") -> GrowthRates:
    """Get realistic growth rates based on lifecycle phase"""
    
    # Platform multipliers
    platform_multipliers = {
        "facebook": {"views": 0.8, "engagement": 1.1, "conversion": 0.9},
        "instagram": {"views": 1.2, "engagement": 1.3, "conversion": 1.1}, 
        "youtube": {"views": 1.5, "engagement": 0.9, "conversion": 1.2},
    }
    
    mult = platform_multipliers.get(platform, platform_multipliers["instagram"])
    
    if phase == "launch":
        # High growth for new content (first week)
        return GrowthRates(
            new_views_per_hour=random.uniform(50, 200) * mult["views"],
            new_likes_per_hour=random.uniform(4, 20) * mult["engagement"],
            new_comments_per_hour=random.uniform(0.5, 4) * mult["engagement"],
            new_shares_per_hour=random.uniform(1, 8) * mult["engagement"],
            new_saves_per_hour=random.uniform(0.5, 3) * mult["engagement"],
            new_clicks_per_hour=random.uniform(2, 12) * mult["engagement"],
            click_through_rate=random.uniform(0.04, 0.08),
            conversion_rate=random.uniform(0.025, 0.035) * mult["conversion"],
            revenue_multiplier=1.0  # No penalty for fresh content
        )
        
    elif phase == "growth":
        # Moderate growth (week 2-4)
        return GrowthRates(
            new_views_per_hour=random.uniform(20, 80) * mult["views"],
            new_likes_per_hour=random.uniform(1.5, 8) * mult["engagement"],
            new_comments_per_hour=random.uniform(0.2, 2) * mult["engagement"],
            new_shares_per_hour=random.uniform(0.5, 4) * mult["engagement"],
            new_saves_per_hour=random.uniform(0.2, 1.5) * mult["engagement"],
            new_clicks_per_hour=random.uniform(1, 6) * mult["engagement"],
            click_through_rate=random.uniform(0.03, 0.06),
            conversion_rate=random.uniform(0.02, 0.03) * mult["conversion"],
            revenue_multiplier=0.95  # Small penalty
        )
        
    elif phase == "plateau":
        # Slow growth (month 2-3)
        return GrowthRates(
            new_views_per_hour=random.uniform(5, 25) * mult["views"],
            new_likes_per_hour=random.uniform(0.3, 3) * mult["engagement"],
            new_comments_per_hour=random.uniform(0.05, 0.8) * mult["engagement"],
            new_shares_per_hour=random.uniform(0.1, 1.5) * mult["engagement"],
            new_saves_per_hour=random.uniform(0.05, 0.6) * mult["engagement"],
            new_clicks_per_hour=random.uniform(0.2, 2) * mult["engagement"],
            click_through_rate=random.uniform(0.02, 0.04),
            conversion_rate=random.uniform(0.015, 0.025) * mult["conversion"],
            revenue_multiplier=0.85  # Moderate penalty
        )
        
    else:  # decay
        # Very slow growth (3+ months old)
        return GrowthRates(
            new_views_per_hour=random.uniform(1, 8) * mult["views"],
            new_likes_per_hour=random.uniform(0.05, 1) * mult["engagement"],
            new_comments_per_hour=random.uniform(0.01, 0.3) * mult["engagement"],
            new_shares_per_hour=random.uniform(0.02, 0.5) * mult["engagement"],
            new_saves_per_hour=random.uniform(0.01, 0.2) * mult["engagement"],
            new_clicks_per_hour=random.uniform(0.05, 0.8) * mult["engagement"],
            click_through_rate=random.uniform(0.01, 0.025),
            conversion_rate=random.uniform(0.01, 0.02) * mult["conversion"],
            revenue_multiplier=0.7  # Significant penalty for old content
        )

def apply_growth_to_content(current: ContentMetrics, platform: str = "instagram", hours_elapsed: int = 1) -> ContentMetrics:
    """
    Apply realistic growth to content metrics.
    Absolute metrics only increase, but growth rates depend on content age.
    """
    
    # Calculate content age
    age_days = calculate_content_age_days(current.created_date) if current.created_date else 0
    phase = determine_growth_phase(age_days)
    
    # Get growth rates for this phase
    rates = get_growth_rates_for_phase(phase, platform)
    
    # Calculate new metrics (always add, never subtract)
    new_views = max(0, int(rates.new_views_per_hour * hours_elapsed))
    new_likes = max(0, int(rates.new_likes_per_hour * hours_elapsed))
    new_comments = max(0, int(rates.new_comments_per_hour * hours_elapsed))
    new_shares = max(0, int(rates.new_shares_per_hour * hours_elapsed))
    new_saves = max(0, int(rates.new_saves_per_hour * hours_elapsed))
    
    # Calculate new clicks based on CTR of new views
    new_clicks = max(0, int(new_views * rates.click_through_rate))
    
    # Update cumulative metrics (always increasing)
    updated_metrics = ContentMetrics(
        views=current.views + new_views,
        likes=current.likes + new_likes,
        comments=current.comments + new_comments,
        shares=current.shares + new_shares,
        saves=current.saves + new_saves,
        clicks=current.clicks + new_clicks,
        created_date=current.created_date,
        last_updated=datetime.now(timezone.utc)
    )
    
    # Apply realistic caps (content can't grow infinitely)
    caps = {
        "views": 100_000,
        "likes": 8_000,
        "comments": 500,
        "shares": 2_000,
        "saves": 1_000,
        "clicks": 5_000,
    }
    
    updated_metrics.views = min(updated_metrics.views, caps["views"])
    updated_metrics.likes = min(updated_metrics.likes, caps["likes"])
    updated_metrics.comments = min(updated_metrics.comments, caps["comments"])
    updated_metrics.shares = min(updated_metrics.shares, caps["shares"])
    updated_metrics.saves = min(updated_metrics.saves, caps["saves"])
    updated_metrics.clicks = min(updated_metrics.clicks, caps["clicks"])
    
    return updated_metrics

def calculate_financial_metrics(metrics: ContentMetrics, platform: str = "instagram") -> Tuple[float, float, float]:
    """Calculate ad spend, revenue, and ROI based on current metrics"""
    
    # Platform-specific costs and conversion rates
    platform_data = {
        "facebook": {"cpc": 1.5, "cpm": 15, "aov": 45, "base_conversion": 0.02},
        "instagram": {"cpc": 2.0, "cpm": 18, "aov": 65, "base_conversion": 0.025},
        "youtube": {"cpc": 0.9, "cpm": 12, "aov": 80, "base_conversion": 0.03},
    }
    
    data = platform_data.get(platform, platform_data["instagram"])
    
    # Calculate ad spend
    ad_spend = (metrics.clicks * data["cpc"]) + (metrics.views * data["cpm"] / 1000)
    
    # Calculate revenue with age-based decay
    age_days = calculate_content_age_days(metrics.created_date) if metrics.created_date else 0
    phase = determine_growth_phase(age_days)
    rates = get_growth_rates_for_phase(phase, platform)
    
    # Revenue calculation with conversion decay
    conversions = metrics.clicks * rates.conversion_rate
    revenue = conversions * data["aov"] * rates.revenue_multiplier
    
    # Calculate ROI
    roi = ((revenue - ad_spend) / ad_spend * 100) if ad_spend > 0 else 0
    
    return round(ad_spend, 2), round(revenue, 2), round(roi, 2)

# Example usage and testing
if __name__ == "__main__":
    
    print("🧪 Testing Improved ROI Growth System")
    print("=" * 50)
    
    # Create initial content
    initial_content = ContentMetrics(
        views=150,
        likes=12,
        comments=3,
        shares=5,
        saves=2,
        clicks=8,
        created_date=datetime.now(timezone.utc)
    )
    
    current_content = initial_content
    
    # Simulate growth over time
    for day in [1, 7, 15, 30, 60, 120]:
        print(f"\n📅 Day {day}:")
        
        # Calculate age and phase
        age_days = day
        phase = determine_growth_phase(age_days)
        
        # Simulate content at this age
        test_content = ContentMetrics(
            views=initial_content.views,
            likes=initial_content.likes,
            comments=initial_content.comments,
            shares=initial_content.shares,
            saves=initial_content.saves,
            clicks=initial_content.clicks,
            created_date=datetime.now(timezone.utc) - timedelta(days=day)
        )
        
        # Apply growth for one day
        grown_content = apply_growth_to_content(test_content, "instagram", hours_elapsed=24)
        
        # Calculate financials
        ad_spend, revenue, roi = calculate_financial_metrics(grown_content, "instagram")
        
        print(f"   Phase: {phase.upper()}")
        print(f"   Views: {grown_content.views:,} (+{grown_content.views - test_content.views:,})")
        print(f"   Likes: {grown_content.likes:,} (+{grown_content.likes - test_content.likes:,})")
        print(f"   Clicks: {grown_content.clicks:,} (+{grown_content.clicks - test_content.clicks:,})")
        print(f"   Revenue: ${revenue:,.2f}")
        print(f"   Ad Spend: ${ad_spend:,.2f}")
        print(f"   ROI: {roi:.1f}%")
        
        from datetime import timedelta  # Import needed for the test
        
    print("\n✅ Growth system test completed!")
    print("\n💡 Key Insights:")
    print("   - Engagement metrics always increase (cumulative)")
    print("   - Growth RATES decrease over time")
    print("   - Revenue conversion declines for older content")
    print("   - ROI becomes less attractive as content ages")

"""
ROI Data Generation Service - IMPROVED THRESHOLD-BASED GROWTH SYSTEM
Implements realistic content lifecycle with plateau and decay mechanics per ROI_SYSTEM_IMPROVEMENT_PLAN.md

Key Features:
- Threshold-based growth phases (Launch, Growth, Plateau, Decay)
- Realistic metric caps based on performance level
- Platform-specific characteristics and conversion rates
- Age-based penalties for older content
- No hard limits - natural growth patterns
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Tuple, List
import math
import random
from datetime import datetime, timezone

Platform = Literal["facebook", "instagram", "youtube"]
PerformanceLevel = Literal["poor", "average", "good", "excellent", "viral"]

@dataclass
class BaseMetrics:
    views: int = 1
    likes: int = 1
    comments: int = 1
    shares: int = 1
    clicks: int = 1
    saves: int = 1

# Performance distribution (realistic content mix)
PERFORMANCE_DISTRIBUTION = [
    ("poor", 0.20),        # 20% underperforms
    ("average", 0.35),     # 35% average performance
    ("good", 0.25),        # 25% good performance
    ("excellent", 0.15),   # 15% excellent performance
    ("viral", 0.05),       # 5% viral content (rare!)
]

# Target ROI ranges by performance level
ROI_RANGES = {
    "poor": (-20, 15),
    "average": (15, 45),
    "good": (45, 85),
    "excellent": (85, 150),
    "viral": (150, 250),
}

# Platform-specific characteristics
PLATFORM_CHARACTERISTICS = {
    "facebook": {
        "strength": "comments",     # Facebook users comment more
        "multiplier": 1.0,         # Baseline platform
        "avg_order_value": 45,     # Lower AOV
        "conversion_rate": 0.02,   # 2% conversion
        "base_cpc": 1.2,           # Cost per click
        "base_cpm": 12,            # Cost per 1000 impressions
    },
    "instagram": {
        "strength": "likes",       # Instagram is visual/likes-focused
        "multiplier": 1.2,         # 20% boost for visual content
        "avg_order_value": 65,     # Medium AOV
        "conversion_rate": 0.025,  # 2.5% conversion
        "base_cpc": 1.8,           # Cost per click
        "base_cpm": 15,            # Cost per 1000 impressions
    },
    "youtube": {
        "strength": "views",       # YouTube optimized for watch time
        "multiplier": 1.5,         # 50% boost for video content
        "avg_order_value": 80,     # Higher AOV
        "conversion_rate": 0.03,   # 3% conversion
        "base_cpc": 0.8,           # Cost per click
        "base_cpm": 8,             # Cost per 1000 impressions
    }
}

def select_random_performance() -> PerformanceLevel:
    """Select performance level based on realistic distribution"""
    rand = random.random()
    cumulative = 0
    for performance, probability in PERFORMANCE_DISTRIBUTION:
        cumulative += probability
        if rand <= cumulative:
            return performance
    return "average"

def determine_lifecycle_phase(current_views: int, content_age_days: int) -> str:
    """Determine which growth phase content is in"""
    if content_age_days < 7:
        return "launch"
    elif current_views < 1_000:
        return "launch"
    elif current_views < 10_000:
        return "growth"
    elif current_views < 50_000:
        return "plateau"
    else:
        return "decay"

def get_growth_multipliers(phase: str, performance: PerformanceLevel) -> Dict[str, Tuple[float, float]]:
    """Get growth multipliers based on lifecycle phase and performance level"""
    
    # Base multipliers by phase (these are daily growth factors)
    base_multipliers = {
        "launch": {
            "views": (1.15, 1.40),      # 15-40% daily growth
            "likes": (1.20, 1.50),      # 20-50% daily growth  
            "comments": (1.10, 1.30),   # 10-30% daily growth
            "shares": (1.15, 1.35),     # 15-35% daily growth
            "clicks": (1.25, 1.45),     # 25-45% daily growth
            "saves": (1.30, 1.60),      # 30-60% daily growth
        },
        "growth": {
            "views": (1.05, 1.20),      # 5-20% daily growth
            "likes": (1.08, 1.25),      # 8-25% daily growth
            "comments": (1.05, 1.15),   # 5-15% daily growth
            "shares": (1.06, 1.18),     # 6-18% daily growth
            "clicks": (1.10, 1.22),     # 10-22% daily growth
            "saves": (1.12, 1.28),      # 12-28% daily growth
        },
        "plateau": {
            "views": (1.01, 1.08),      # 1-8% daily growth (can decrease slightly)
            "likes": (1.02, 1.10),      # 2-10% daily growth
            "comments": (1.01, 1.06),   # 1-6% daily growth
            "shares": (1.01, 1.08),     # 1-8% daily growth
            "clicks": (1.03, 1.12),     # 3-12% daily growth
            "saves": (1.04, 1.15),      # 4-15% daily growth
        },
        "decay": {
            "views": (1.001, 1.03),     # 0.1-3% daily growth (very slow)
            "likes": (1.002, 1.05),     # 0.2-5% daily growth
            "comments": (1.001, 1.02),  # 0.1-2% daily growth
            "shares": (1.001, 1.03),    # 0.1-3% daily growth
            "clicks": (1.002, 1.04),    # 0.2-4% daily growth
            "saves": (1.003, 1.06),     # 0.3-6% daily growth
        }
    }
    
    # Performance scaling factors
    performance_scaling = {
        "poor": 0.7,        # 70% of base growth
        "average": 1.0,     # 100% of base growth
        "good": 1.4,        # 140% of base growth
        "excellent": 1.8,   # 180% of base growth
        "viral": 2.5,       # 250% of base growth
    }
    
    scaling = performance_scaling[performance]
    base = base_multipliers[phase]
    
    # Apply performance scaling to all metrics
    scaled_multipliers = {}
    for metric, (min_val, max_val) in base.items():
        # Scale the growth factors
        scaled_min = 1.0 + (min_val - 1.0) * scaling
        scaled_max = 1.0 + (max_val - 1.0) * scaling
        
        # Ensure we don't go below 1.0 (no negative growth)
        scaled_min = max(1.001, scaled_min)
        scaled_max = max(1.002, scaled_max)
        
        scaled_multipliers[metric] = (scaled_min, scaled_max)
    
    return scaled_multipliers

def get_soft_caps(metric: str, performance: PerformanceLevel) -> int:
    """Get realistic soft caps for metrics based on performance level"""
    
    # More realistic caps that allow for 90 days of growth
    caps = {
        "poor": {
            "views": 15_000,      # Can reach 15K views over 90 days
            "likes": 1_200,       # Can reach 1.2K likes
            "comments": 150,      # Can reach 150 comments
            "shares": 300,        # Can reach 300 shares
            "clicks": 800,        # Can reach 800 clicks
            "saves": 400,         # Can reach 400 saves
        },
        "average": {
            "views": 50_000,      # Can reach 50K views over 90 days
            "likes": 4_000,       # Can reach 4K likes
            "comments": 500,      # Can reach 500 comments
            "shares": 1_000,      # Can reach 1K shares
            "clicks": 2_500,      # Can reach 2.5K clicks
            "saves": 1_200,       # Can reach 1.2K saves
        },
        "good": {
            "views": 150_000,     # Can reach 150K views over 90 days
            "likes": 12_000,      # Can reach 12K likes
            "comments": 1_500,    # Can reach 1.5K comments
            "shares": 3_000,      # Can reach 3K shares
            "clicks": 8_000,      # Can reach 8K clicks
            "saves": 4_000,       # Can reach 4K saves
        },
        "excellent": {
            "views": 400_000,     # Can reach 400K views over 90 days
            "likes": 35_000,      # Can reach 35K likes
            "comments": 4_500,    # Can reach 4.5K comments
            "shares": 9_000,      # Can reach 9K shares
            "clicks": 25_000,     # Can reach 25K clicks
            "saves": 12_000,      # Can reach 12K saves
        },
        "viral": {
            "views": 1_000_000,   # Can reach 1M views over 90 days
            "likes": 100_000,     # Can reach 100K likes
            "comments": 15_000,   # Can reach 15K comments
            "shares": 30_000,     # Can reach 30K shares
            "clicks": 80_000,     # Can reach 80K clicks
            "saves": 40_000,      # Can reach 40K saves
        }
    }
    
    return caps[performance][metric]

def random_in_range(min_value: float, max_value: float) -> float:
    """Generate random value within range"""
    return random.random() * (max_value - min_value) + min_value

def generate_initial_metrics(performance: PerformanceLevel, platform: Platform) -> BaseMetrics:
    """Generate realistic starting metrics based on performance level and platform"""
    
    # More realistic starting values that allow for 90 days of growth
    base_ranges = {
        "poor": {
            "views": (80, 200),      # Start with 80-200 views
            "likes": (8, 25),        # Start with 8-25 likes
            "comments": (2, 8),      # Start with 2-8 comments
            "shares": (3, 12),       # Start with 3-12 shares
            "clicks": (5, 18),       # Start with 5-18 clicks
            "saves": (2, 8),         # Start with 2-8 saves
        },
        "average": {
            "views": (200, 500),     # Start with 200-500 views
            "likes": (25, 60),       # Start with 25-60 likes
            "comments": (8, 20),     # Start with 8-20 comments
            "shares": (12, 30),      # Start with 12-30 shares
            "clicks": (18, 45),      # Start with 18-45 clicks
            "saves": (8, 20),        # Start with 8-20 saves
        },
        "good": {
            "views": (500, 1_200),   # Start with 500-1.2K views
            "likes": (60, 150),      # Start with 60-150 likes
            "comments": (20, 50),    # Start with 20-50 comments
            "shares": (30, 80),      # Start with 30-80 shares
            "clicks": (45, 120),     # Start with 45-120 clicks
            "saves": (20, 50),       # Start with 20-50 saves
        },
        "excellent": {
            "views": (1_200, 3_000), # Start with 1.2K-3K views
            "likes": (150, 400),     # Start with 150-400 likes
            "comments": (50, 120),   # Start with 50-120 comments
            "shares": (80, 200),     # Start with 80-200 shares
            "clicks": (120, 300),    # Start with 120-300 clicks
            "saves": (50, 120),      # Start with 50-120 saves
        },
        "viral": {
            "views": (3_000, 8_000), # Start with 3K-8K views
            "likes": (400, 1_200),   # Start with 400-1.2K likes
            "comments": (120, 300),  # Start with 120-300 comments
            "shares": (200, 500),    # Start with 200-500 shares
            "clicks": (300, 800),    # Start with 300-800 clicks
            "saves": (120, 300),     # Start with 120-300 saves
        }
    }
    
    # Platform-specific multipliers (some platforms naturally perform better)
    platform_multipliers = {
        "facebook": {
            "views": 0.9,    # Facebook gets slightly fewer views
            "likes": 1.2,    # But more engagement (likes, comments)
            "comments": 1.3, # Facebook is comment-heavy
            "shares": 1.1,   # Good for sharing
            "clicks": 0.95,  # Slightly fewer clicks
            "saves": 0.8,    # Fewer saves on Facebook
        },
        "instagram": {
            "views": 1.1,    # Instagram gets good views
            "likes": 1.4,    # Instagram is like-heavy
            "comments": 1.1, # Moderate comments
            "shares": 1.2,   # Good for sharing
            "clicks": 1.1,   # Good click-through
            "saves": 1.5,    # Instagram is save-heavy
        },
        "youtube": {
            "views": 1.3,    # YouTube gets the most views
            "likes": 0.9,    # But fewer likes relative to views
            "comments": 1.2, # Good for comments
            "shares": 1.0,   # Standard sharing
            "clicks": 1.2,   # Good for external clicks
            "saves": 0.7,    # Fewer saves on YouTube
        }
    }
    
    ranges = base_ranges[performance]
    mult = platform_multipliers[platform]
    
    # Generate metrics with platform adjustments
    views = int(random.randint(*ranges["views"]) * mult["views"])
    likes = int(random.randint(*ranges["likes"]) * mult["likes"])
    comments = int(random.randint(*ranges["comments"]) * mult["comments"])
    shares = int(random.randint(*ranges["shares"]) * mult["shares"])
    clicks = int(random.randint(*ranges["clicks"]) * mult["clicks"])
    saves = int(random.randint(*ranges["saves"]) * mult["saves"])
    
    # Ensure minimum values
    views = max(50, views)
    likes = max(5, likes)
    comments = max(1, comments)
    shares = max(1, shares)
    clicks = max(3, clicks)
    saves = max(1, saves)
    
    return BaseMetrics(
        views=views,
        likes=likes,
        comments=comments,
        shares=shares,
        clicks=clicks,
        saves=saves,
    )

def simulate_content_growth(initial_metrics: BaseMetrics, content_age_days: int, 
                            performance: PerformanceLevel, platform: Platform) -> BaseMetrics:
    """Simulate realistic growth over time with performance-based scaling"""
    
    current_metrics = BaseMetrics(
        views=initial_metrics.views,
        likes=initial_metrics.likes,
        comments=initial_metrics.comments,
        shares=initial_metrics.shares,
        clicks=initial_metrics.clicks,
        saves=initial_metrics.saves,
    )
    
    # Debug: Show initial state
    if content_age_days > 30:  # Only show for longer content
        print(f"      🚀 Starting growth simulation for {platform} ({performance}):")
        print(f"         Initial: views={current_metrics.views}, likes={current_metrics.likes}")
    
    # Simulate daily growth
    for day in range(content_age_days):
        phase = determine_lifecycle_phase(current_metrics.views, day)
        daily_growth = get_growth_multipliers(phase, performance)
        
        # Apply daily growth with diminishing returns
        for metric_name in ["views", "likes", "comments", "shares", "clicks", "saves"]:
            current_value = getattr(current_metrics, metric_name)
            min_growth, max_growth = daily_growth[metric_name]
            
            # Calculate growth factor for this day
            growth_factor = random_in_range(min_growth, max_growth)
            
            # Apply growth - CRITICAL: Always ensure positive growth
            new_value = int(current_value * growth_factor)
            
            # CRITICAL FIX: Ensure metrics NEVER go below previous value
            # At minimum, increase by 1, but prefer the calculated growth if it's higher
            new_value = max(current_value + 1, new_value)
            
            # Apply soft caps with exponential decay as we approach limits
            cap = get_soft_caps(metric_name, performance)
            if new_value > cap * 0.8:  # When we're at 80% of cap
                # Exponential decay as we approach cap
                excess = new_value - cap * 0.8
                decay_factor = 1 - (excess / (cap * 0.2))  # Decay over remaining 20%
                decay_factor = max(0.1, decay_factor)  # Never go below 10%
                new_value = int(cap * 0.8 + (excess * decay_factor))
                
                # CRITICAL: Even with decay, ensure we don't go backwards
                new_value = max(current_value + 1, new_value)
            
            # FINAL SAFETY CHECK: Ensure we never go backwards
            if new_value <= current_value:
                new_value = current_value + 1
                print(f"         ⚠️  Safety check: {metric_name} would have decreased, forcing +1")
            
            setattr(current_metrics, metric_name, new_value)
        
        # Debug: Show progress every 30 days for longer content
        if content_age_days > 30 and day % 30 == 0 and day > 0:
            print(f"         Day {day}: views={current_metrics.views}, likes={current_metrics.likes} (phase: {phase})")
    
    # Debug: Show final state
    if content_age_days > 30:
        print(f"         Final: views={current_metrics.views}, likes={current_metrics.likes}")
        print(f"         Growth: views +{current_metrics.views - initial_metrics.views}, likes +{current_metrics.likes - initial_metrics.likes}")
    
    return current_metrics

def calculate_realistic_financials(metrics: BaseMetrics, platform: Platform, 
                                 performance: PerformanceLevel, age_days: int) -> Dict[str, float]:
    """Calculate financial metrics targeting realistic ROI ranges"""
    
    platform_data = PLATFORM_CHARACTERISTICS[platform]
    
    # Add realistic variation to costs (±25%)
    cpc = platform_data["base_cpc"] * random.uniform(0.75, 1.25)
    cpm = platform_data["base_cpm"] * random.uniform(0.75, 1.25)
    aov = platform_data["avg_order_value"] * random.uniform(0.85, 1.15)
    
    # Calculate ad spend
    ad_spend = (metrics.clicks * cpc) + (metrics.views * cpm / 1000)
    
    # Target ROI based on performance level
    target_roi_ranges = ROI_RANGES[performance]
    
    # Pick a target ROI within the range for this performance level
    min_roi, max_roi = target_roi_ranges
    target_roi = random.uniform(min_roi, max_roi)
    
    # Age penalty (older content performs worse)
    age_penalty = max(0.5, 1 - (age_days * 0.005))  # 0.5% penalty per day, min 50%
    target_roi *= age_penalty
    
    # Calculate required revenue to hit target ROI
    # ROI = (revenue - ad_spend) / ad_spend * 100
    # target_roi = (revenue - ad_spend) / ad_spend * 100
    # revenue = ad_spend * (1 + target_roi/100)
    target_revenue = ad_spend * (1 + target_roi / 100)
    
    # Add some realistic variation (±15%) to prevent exact targeting
    actual_revenue = target_revenue * random.uniform(0.85, 1.15)
    
    # Calculate actual ROI
    actual_roi = ((actual_revenue - ad_spend) / ad_spend * 100) if ad_spend > 0 else 0
    
    # Calculate implied conversion rate (for realism check)
    implied_conversions = actual_revenue / aov
    implied_conversion_rate = implied_conversions / metrics.clicks if metrics.clicks > 0 else 0
    
    # If conversion rate is unrealistic (>10%), scale back revenue
    if implied_conversion_rate > 0.10:
        max_conversions = metrics.clicks * 0.10
        actual_revenue = max_conversions * aov
        actual_roi = ((actual_revenue - ad_spend) / ad_spend * 100) if ad_spend > 0 else 0
    
    # SAFETY CHECK: Prevent database overflow (max value: 99,999,999.99)
    max_safe_value = 99_999_999.99
    if ad_spend > max_safe_value:
        ad_spend = max_safe_value
        print(f"      ⚠️  Capped ad_spend at {max_safe_value} to prevent overflow")
    
    if actual_revenue > max_safe_value:
        actual_revenue = max_safe_value
        print(f"      ⚠️  Capped revenue at {max_safe_value} to prevent overflow")

    return {
        "ad_spend": round(ad_spend, 2),
        "revenue_generated": round(actual_revenue, 2),
        "roi_percentage": round(actual_roi, 2),
        "roas_ratio": round(actual_revenue / ad_spend, 2) if ad_spend > 0 else 0,
        "cost_per_click": round(cpc, 2),
        "cost_per_impression": round(cpm / 1000, 4),
        "implied_conversion_rate": round(implied_conversion_rate, 4),
    }

def generate_realistic_update(current: BaseMetrics, hours_elapsed: int = 1, 
                            *, content_type: str = "video", platform: Platform = "youtube") -> BaseMetrics:
    """
    Generate realistic update based on current metrics and time elapsed.
    This maintains backward compatibility with existing code.
    """
    # Determine performance level based on current engagement
    engagement_rate = (current.likes + current.comments + current.shares) / max(current.views, 1)
    
    if engagement_rate > 0.15:
        performance = "excellent"
    elif engagement_rate > 0.08:
        performance = "good"
    elif engagement_rate > 0.04:
        performance = "average"
    else:
        performance = "poor"
    
    # Simulate growth for the elapsed time
    age_days = hours_elapsed / 24.0
    updated_metrics = simulate_content_growth(current, int(age_days), performance, platform)
    
    return updated_metrics

def calculate_financial_metrics(platform: Platform, metrics: BaseMetrics) -> Dict[str, float]:
    """Calculate financial metrics for backward compatibility"""
    # Use default performance level for backward compatibility
    performance = "average"
    age_days = 1  # Assume 1 day old for backward compatibility
    
    return calculate_realistic_financials(metrics, platform, performance, age_days)

def calculate_revenue(platform: Platform, metrics: BaseMetrics) -> Dict[str, int | float]:
    """Calculate revenue for backward compatibility"""
    # Use default performance level for backward compatibility
    performance = "average"
    age_days = 1  # Assume 1 day old for backward compatibility
    
    financials = calculate_realistic_financials(metrics, platform, performance, age_days)
    
    return {
        "conversions": int(financials["revenue_generated"] / PLATFORM_CHARACTERISTICS[platform]["avg_order_value"]),
        "revenue": financials["revenue_generated"]
    }

def finalize_roi(ad_spend: float, revenue: float, engagement_quality: float = 1.0) -> Tuple[float, float]:
    """Finalize ROI calculation for backward compatibility"""
    if ad_spend <= 0:
        return 0.0, 0.0
    
    # Base ROI calculation
    base_roi_pct = ((revenue - ad_spend) / ad_spend) * 100.0
    
    # Adjust ROI based on engagement quality to make it more realistic
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

async def fetch_latest_platform_metrics(supabase_client, user_id: str) -> Dict[str, BaseMetrics]:
    """
    Fetch the latest metrics for each platform (YouTube, Facebook, Instagram) from the database.
    Returns a dict with platform as key and BaseMetrics as value.
    """
    platforms = ["youtube", "facebook", "instagram"]
    latest_metrics = {}
    
    print(f"      🔍 Fetching latest metrics for user: {user_id}")
    
    for platform in platforms:
        try:
            # Get the latest row for this platform and user (INCLUDING live_update content)
            response = await supabase_client._make_request(
                "GET", "roi_metrics",
                params={
                    "user_id": f"eq.{user_id}",
                    "platform": f"eq.{platform}",
                    "select": "views,likes,comments,shares,clicks,saves,ad_spend,revenue_generated,roi_percentage,roas_ratio,content_type,created_at",
                    "order": "created_at.desc",  # Use created_at to get the most recent entry
                    "limit": "1"
                }
            )
            
            print(f"         🔍 {platform} query response: {response.status_code}")
            
            if response.status_code == 200 and response.json():
                data = response.json()[0]
                print(f"         📊 {platform} raw data: {data}")
                
                # Create BaseMetrics object from database row
                metrics = BaseMetrics(
                    views=int(data.get("views", 100)),
                    likes=int(data.get("likes", 10)),
                    comments=int(data.get("comments", 5)),
                    shares=int(data.get("shares", 3)),
                    clicks=int(data.get("clicks", 8)),
                    saves=int(data.get("saves", 2))
                )
                
                latest_metrics[platform] = metrics
                print(f"         📊 {platform}: views={metrics.views}, likes={metrics.likes}, content_type={data.get('content_type', 'unknown')}")
                
            else:
                print(f"         ⚠️  No data found for {platform}, using realistic default metrics")
                print(f"         🔍 Response: {response.status_code} - {response.text if hasattr(response, 'text') else 'No text'}")
                # Use realistic default metrics if no data found
                # These will be used as starting points for new content
                if platform == "youtube":
                    default_metrics = BaseMetrics(views=150, likes=15, comments=8, shares=5, clicks=12, saves=3)
                elif platform == "facebook":
                    default_metrics = BaseMetrics(views=120, likes=20, comments=12, shares=8, clicks=15, saves=2)
                else:  # instagram
                    default_metrics = BaseMetrics(views=200, likes=25, comments=10, shares=15, clicks=18, saves=8)
                
                latest_metrics[platform] = default_metrics
                print(f"         🚀 {platform}: using defaults - views={default_metrics.views}, likes={default_metrics.likes}")
                
        except Exception as e:
            print(f"         ❌ Error fetching {platform} metrics: {e}")
            # Use realistic default metrics on error
            if platform == "youtube":
                default_metrics = BaseMetrics(views=150, likes=15, comments=8, shares=5, clicks=12, saves=3)
            elif platform == "facebook":
                default_metrics = BaseMetrics(views=120, likes=20, comments=12, shares=8, clicks=15, saves=2)
            else:  # instagram
                default_metrics = BaseMetrics(views=200, likes=25, comments=10, shares=15, clicks=18, saves=8)
            
            latest_metrics[platform] = default_metrics
            print(f"         🚀 {platform}: using fallback defaults - views={default_metrics.views}, likes={default_metrics.likes}")
    
    print(f"      ✅ Fetched metrics for {len(latest_metrics)} platforms")
    return latest_metrics

def apply_10min_growth(current_metrics: BaseMetrics, platform: Platform, 
                       performance: PerformanceLevel = "average", content_age_days: int = None) -> BaseMetrics:
    """
    Apply 10-minute growth to existing metrics using the same growth logic.
    This simulates what happens in 10 minutes (1/144th of a day).
    """
    # Determine lifecycle phase based on current views
    current_views = current_metrics.views
    
    # Use provided content_age_days or default to 1 if not provided
    if content_age_days is None:
        content_age_days = 1
        print(f"         ⚠️  No content age provided, using default: {content_age_days} day")
    
    phase = determine_lifecycle_phase(current_views, content_age_days)
    daily_growth = get_growth_multipliers(phase, performance)
    
    # Convert daily growth to 10-minute growth (10 min = 1/144 of a day)
    time_factor = 1 / 144  # 10 minutes out of 24 hours
    
    # Apply 10-minute growth to each metric
    new_metrics = BaseMetrics(
        views=current_metrics.views,
        likes=current_metrics.likes,
        comments=current_metrics.comments,
        shares=current_metrics.shares,
        clicks=current_metrics.clicks,
        saves=current_metrics.saves
    )
    
    for metric_name in ["views", "likes", "comments", "shares", "clicks", "saves"]:
        current_value = getattr(current_metrics, metric_name)
        min_growth, max_growth = daily_growth[metric_name]
        
        # Calculate 10-minute growth factor
        growth_factor = random_in_range(min_growth, max_growth)
        tenmin_growth = 1 + (growth_factor - 1) * time_factor
        
        # Apply growth - CRITICAL: Always ensure positive growth
        new_value = int(current_value * tenmin_growth)
        
        # CRITICAL: Ensure metrics NEVER go below previous value
        new_value = max(current_value + 1, new_value)
        
        # Apply soft caps if approaching limits
        cap = get_soft_caps(metric_name, performance)
        if new_value > cap * 0.9:  # When we're at 90% of cap
            # Gentle decay as we approach cap
            excess = new_value - cap * 0.9
            decay_factor = 1 - (excess / (cap * 0.1))  # Decay over remaining 10%
            decay_factor = max(0.5, decay_factor)  # Never go below 50%
            new_value = int(cap * 0.9 + (excess * decay_factor))
            
            # CRITICAL: Even with decay, ensure we don't go backwards
            new_value = max(current_value + 1, new_value)
        
        setattr(new_metrics, metric_name, new_value)
    
    return new_metrics

async def generate_next_10min_update(supabase_client, user_id: str) -> List[Dict]:
    """
    Generate the next 10-minute update by:
    1. Fetching latest metrics for each platform
    2. Applying 10-minute growth
    3. Calculating new financial metrics
    4. Returning 3 records ready for insertion
    """
    print(f"🔄 Generating next 10-minute update for user: {user_id}")
    
    # Fetch latest metrics from database
    latest_metrics = await fetch_latest_platform_metrics(supabase_client, user_id)
    
    next_updates = []
    
    for platform, current_metrics in latest_metrics.items():
        # Determine performance level based on current engagement
        engagement_rate = (current_metrics.likes + current_metrics.comments + current_metrics.shares) / max(current_metrics.views, 1)
        
        if engagement_rate > 0.15:
            performance = "excellent"
        elif engagement_rate > 0.08:
            performance = "good"
        elif engagement_rate > 0.04:
            performance = "average"
        else:
            performance = "poor"
        
        print(f"      📊 {platform.title()}: {performance} performance (engagement: {engagement_rate:.3f})")
        
        # Use default content age since we don't need precise calculation
        content_age_days = 1
        
        # Apply 10-minute growth to existing metrics using default age
        updated_metrics = apply_10min_growth(current_metrics, platform, performance, content_age_days)
        
        # Calculate financial metrics based on updated metrics and REAL content age
        financials = calculate_realistic_financials(updated_metrics, platform, performance, content_age_days)
        
        # Create record for insertion
        record = {
            "user_id": user_id,
            "platform": platform,
            "campaign_id": None,
            "post_id": f"{platform}_post_live",  # Generic post ID for live updates
            "content_type": "live_update",
            "content_category": "generic",
            "views": updated_metrics.views,
            "likes": updated_metrics.likes,
            "comments": updated_metrics.comments,
            "shares": updated_metrics.shares,
            "saves": updated_metrics.saves,
            "clicks": updated_metrics.clicks,
            "ad_spend": financials["ad_spend"],
            "revenue_generated": financials["revenue_generated"],
            "cost_per_click": financials["cost_per_click"],
            "cost_per_impression": financials["cost_per_impression"],
            "roi_percentage": financials["roi_percentage"],
            "roas_ratio": financials["roas_ratio"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "posted_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "update_timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        next_updates.append(record)
        
        print(f"         Growth: views {current_metrics.views} → {updated_metrics.views} (+{updated_metrics.views - current_metrics.views})")
        print(f"         Growth: likes {current_metrics.likes} → {updated_metrics.likes} (+{updated_metrics.likes - current_metrics.likes})")
    
    print(f"      ✅ Generated {len(next_updates)} platform updates")
    return next_updates

class DataGeneratorService:
    """Service class for generating ROI metrics with improved growth system"""
    
    def __init__(self):
        pass

    def step(self, platform: Platform, current: BaseMetrics, hour: int) -> Dict[str, object]:
        """Generate step update for backward compatibility"""
        updated = generate_realistic_update(current, hours_elapsed=hour, platform=platform)
        fin = calculate_financial_metrics(platform, updated)
        rev = calculate_revenue(platform, updated)
        
        engagement_quality = (updated.likes + updated.comments + updated.shares) / max(updated.views, 1)
        
        roi_pct, roas = finalize_roi(fin["ad_spend"], rev["revenue"], engagement_quality)
        fin["roi_percentage"] = roi_pct
        fin["roas_ratio"] = roas

        return {
            "metrics": updated,
            "financials": fin,
            "revenue": rev
        }

    def generate_metrics(self, base_metrics: BaseMetrics, platform: Platform = "youtube") -> BaseMetrics:
        """
        Generate new metrics based on base metrics with improved growth calculations.
        This method is used by the updated ROI writer.
        """
        # Determine performance level based on current engagement
        engagement_rate = (base_metrics.likes + base_metrics.comments + base_metrics.shares) / max(base_metrics.views, 1)
        
        if engagement_rate > 0.15:
            performance = "excellent"
        elif engagement_rate > 0.08:
            performance = "good"
        elif engagement_rate > 0.04:
            performance = "average"
        else:
            performance = "poor"
        
        # Simulate 1 hour of growth
        age_days = 1 / 24.0  # 1 hour
        updated_metrics = simulate_content_growth(base_metrics, int(age_days), performance, platform)
        
        # Calculate financial metrics
        fin = calculate_realistic_financials(updated_metrics, platform, performance, age_days)
        rev = calculate_revenue(platform, updated_metrics)
        
        # Create extended metrics object with financial data
        class ExtendedMetrics(BaseMetrics):
            def __init__(self, base: BaseMetrics, financial: Dict[str, float], revenue: Dict[str, float]):
                super().__init__(
                    views=base.views,
                    likes=base.likes,
                    comments=base.comments,
                    shares=base.shares,
                    clicks=base.clicks,
                    saves=base.saves
                )
                self.ad_spend = financial["ad_spend"]
                self.revenue_generated = financial["revenue_generated"]
                self.roi_percentage = financial["roi_percentage"]
                self.roas_ratio = financial["roas_ratio"]
        
        return ExtendedMetrics(updated_metrics, fin, rev)
    
    async def generate_live_10min_update(self, supabase_client, user_id: str) -> List[Dict]:
        """
        Generate live 10-minute update by fetching latest metrics and applying growth.
        This is the main method used by the live scheduler.
        """
        return await generate_next_10min_update(supabase_client, user_id)



#!/usr/bin/env python3
"""
Script to populate roi_metrics table with realistic sample data for beautiful dashboard visualization.
This creates comprehensive data across YouTube, Instagram, and Facebook platforms only.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import sys

# Add the backend directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.supabase_client import supabase_client

# Sample data configuration - Only YouTube, Instagram, and Facebook
PLATFORMS = ["YouTube", "Instagram", "Facebook"]
CONTENT_TYPES = ["video", "reel", "post"]
CONTENT_CATEGORIES = ["product", "lifestyle", "educational", "entertainment", "promotional", "user_generated"]

# Realistic ranges for different metrics
METRIC_RANGES = {
    "views": (100, 50000),
    "likes": (10, 5000),
    "comments": (5, 1000),
    "shares": (2, 500),
    "saves": (1, 200),
    "clicks": (5, 2000),
    "ad_spend": (10.0, 5000.0),
    "revenue_generated": (50.0, 15000.0),
    "cost_per_click": (0.5, 15.0),
    "cost_per_impression": (0.01, 2.0),
}

def generate_realistic_metric(base_range: tuple, platform: str, content_type: str) -> float:
    """Generate realistic metrics based on platform and content type performance patterns."""
    min_val, max_val = base_range
    
    # Platform-specific multipliers - Only YouTube, Instagram, Facebook
    platform_multipliers = {
        "YouTube": {"views": 3.0, "likes": 1.5, "comments": 2.0, "shares": 1.2, "revenue": 2.5},
        "Instagram": {"views": 1.8, "likes": 2.0, "comments": 1.8, "shares": 1.5, "revenue": 1.8},
        "Facebook": {"views": 1.0, "likes": 1.0, "comments": 1.0, "shares": 1.0, "revenue": 1.0},
    }
    
    # Content type multipliers
    content_multipliers = {
        "video": {"views": 2.0, "likes": 1.8, "comments": 1.5, "shares": 1.6, "revenue": 1.8},
        "reel": {"views": 2.5, "likes": 2.0, "comments": 1.8, "shares": 2.0, "revenue": 2.0},
        "post": {"views": 0.8, "likes": 0.9, "comments": 1.1, "shares": 1.2, "revenue": 0.9},
    }
    
    # Determine metric type for multiplier selection
    metric_type = "views"  # default
    if "like" in str(base_range):
        metric_type = "likes"
    elif "comment" in str(base_range):
        metric_type = "comments"
    elif "share" in str(base_range):
        metric_type = "shares"
    elif "revenue" in str(base_range):
        metric_type = "revenue"
    
    # Apply multipliers
    platform_mult = platform_multipliers.get(platform, {}).get(metric_type, 1.0)
    content_mult = content_multipliers.get(content_type, {}).get(metric_type, 1.0)
    
    # Add some randomness and seasonal variation
    base_value = random.uniform(min_val, max_val)
    seasonal_factor = 1.0 + 0.3 * random.uniform(-1, 1)  # ±30% seasonal variation
    
    final_value = base_value * platform_mult * content_mult * seasonal_factor
    
    # Ensure we stay within reasonable bounds
    return max(min_val * 0.1, min(max_val * 2, final_value))

def generate_roi_metrics(views: int, likes: int, comments: int, shares: int, 
                        ad_spend: float, revenue_generated: float) -> Dict[str, float]:
    """Calculate ROI metrics based on engagement and financial data."""
    clicks = int(views * random.uniform(0.02, 0.08))  # 2-8% click-through rate
    saves = int(likes * random.uniform(0.1, 0.3))  # 10-30% of likes are saves
    
    # Calculate derived metrics
    cost_per_click = ad_spend / clicks if clicks > 0 else 0
    cost_per_impression = ad_spend / views if views > 0 else 0
    
    # Calculate ROI percentage
    roi_percentage = ((revenue_generated - ad_spend) / ad_spend * 100) if ad_spend > 0 else 0
    
    # Calculate ROAS (Return on Ad Spend)
    roas_ratio = revenue_generated / ad_spend if ad_spend > 0 else 0
    
    return {
        "clicks": clicks,
        "saves": saves,
        "cost_per_click": round(cost_per_click, 2),
        "cost_per_impression": round(cost_per_impression, 4),
        "roi_percentage": round(roi_percentage, 2),
        "roas_ratio": round(roas_ratio, 2)
    }

async def create_sample_roi_data():
    """Create comprehensive sample ROI data for the dashboard - Only roi_metrics table."""
    print("🚀 Starting ROI sample data generation...")
    print("📊 Platforms: YouTube, Instagram, Facebook only")
    print("🎯 Target table: roi_metrics only")
    
    # Generate data for the last 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    # Create data points for each day
    current_date = start_date
    total_records = 0
    
    while current_date <= end_date:
        # Generate 5-12 records per day (more data for better visualization)
        daily_records = random.randint(5, 12)
        
        for _ in range(daily_records):
            # Random platform and content type
            platform = random.choice(PLATFORMS)
            content_type = random.choice(CONTENT_TYPES)
            content_category = random.choice(CONTENT_CATEGORIES)
            
            # Generate realistic metrics
            views = int(generate_realistic_metric(METRIC_RANGES["views"], platform, content_type))
            likes = int(generate_realistic_metric(METRIC_RANGES["likes"], platform, content_type))
            comments = int(generate_realistic_metric(METRIC_RANGES["comments"], platform, content_type))
            shares = int(generate_realistic_metric(METRIC_RANGES["shares"], platform, content_type))
            
            ad_spend = round(generate_realistic_metric(METRIC_RANGES["ad_spend"], platform, content_type), 2)
            revenue_generated = round(generate_realistic_metric(METRIC_RANGES["revenue_generated"], platform, content_type), 2)
            
            # Calculate ROI metrics
            roi_metrics = generate_roi_metrics(views, likes, comments, shares, ad_spend, revenue_generated)
            
            # Create the record
            record = {
                "user_id": "user_31VgZVmUnz3XYl4DnOB1NQG5TwP",  # Use valid user ID
                "platform": platform,
                "campaign_id": None,  # Set to NULL to avoid foreign key constraint issues
                "post_id": f"post_{random.randint(1000, 9999)}",
                "content_type": content_type,
                "content_category": content_category,
                "views": views,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "saves": roi_metrics["saves"],
                "clicks": roi_metrics["clicks"],
                "ad_spend": ad_spend,
                "revenue_generated": revenue_generated,
                "cost_per_click": roi_metrics["cost_per_click"],
                "cost_per_impression": roi_metrics["cost_per_impression"],
                "roi_percentage": roi_metrics["roi_percentage"],
                "roas_ratio": roi_metrics["roas_ratio"],
                "created_at": current_date.isoformat(),
                "posted_at": (current_date - timedelta(hours=random.randint(1, 24))).isoformat(),
                "updated_at": current_date.isoformat(),
                "update_timestamp": current_date.isoformat()
            }
            
            try:
                # Insert the record
                response = await supabase_client._make_request("POST", "roi_metrics", data=record)
                if response.status_code == 201:
                    total_records += 1
                    if total_records % 50 == 0:
                        print(f"✅ Created {total_records} records...")
                else:
                    print(f"❌ Failed to insert record: {response.status_code}")
            except Exception as e:
                print(f"❌ Error inserting record: {e}")
        
        current_date += timedelta(days=1)
    
    print(f"🎉 Successfully created {total_records} ROI metrics records!")
    return total_records

async def main():
    """Main function to populate ROI metrics data only."""
    print("🎯 Starting ROI sample data generation...")
    print("=" * 60)
    print("📊 Platforms: YouTube, Instagram, Facebook")
    print("🎯 Target: roi_metrics table only")
    print("📅 Time range: Last 90 days")
    print("=" * 60)
    
    try:
        # Create ROI metrics data only
        roi_count = await create_sample_roi_data()
        
        print()
        print("=" * 60)
        print("🎉 Sample data generation completed successfully!")
        print(f"📈 Total records created:")
        print(f"   • ROI Metrics: {roi_count}")
        print(f"   • Platforms: YouTube, Instagram, Facebook")
        print(f"   • Time range: 90 days")
        print()
        print("✨ Your ROI dashboard should now display beautiful, professional graphs!")
        print("🚀 You can now visit the ROI dashboard to see the enhanced visualizations.")
        print()
        print("💡 Platform-specific patterns:")
        print("   • YouTube: Higher views, moderate engagement, high revenue potential")
        print("   • Instagram: High engagement rates, strong visual content performance")
        print("   • Facebook: Balanced performance across all metrics")
        
    except Exception as e:
        print(f"❌ Error during sample data generation: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

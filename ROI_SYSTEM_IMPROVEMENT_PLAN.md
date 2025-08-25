# 🚀 ROI System Improvement Plan
## Advanced Threshold-Based Growth with Plateau & Decay Mechanics

---

## 📊 **Current Database Structure** 

Based on the `roi_metrics` table CSV analysis, our system tracks these key columns:

```sql
-- ROI Metrics Table Structure (from CSV analysis)
CREATE TABLE roi_metrics (
    id BIGINT PRIMARY KEY,
    user_id VARCHAR,                    -- User identifier (e.g., 'user_31VgZVmUnz3XYl4DnOB1NQG5TwP')
    platform VARCHAR,                  -- 'facebook', 'instagram', 'youtube'
    campaign_id VARCHAR,               -- Optional campaign reference
    post_id VARCHAR,                   -- Individual post identifier
    content_type VARCHAR,              -- 'video', 'post', 'reel', 'story'
    content_category VARCHAR,          -- 'generic', 'product', 'lifestyle', etc.
    
    -- Engagement Metrics
    views BIGINT,                      -- Total views/impressions
    likes BIGINT,                      -- Likes/reactions
    comments BIGINT,                   -- Comments count
    shares BIGINT,                     -- Shares/reposts
    saves BIGINT,                      -- Bookmarks/saves
    clicks BIGINT,                     -- Click-throughs
    
    -- Financial Metrics
    ad_spend DECIMAL(10,2),            -- Money spent on ads
    revenue_generated DECIMAL(10,2),   -- Revenue attributed to this content
    cost_per_click DECIMAL(6,4),       -- CPC rate
    cost_per_impression DECIMAL(8,6),  -- CPM rate (per 1000 impressions)
    roi_percentage DECIMAL(8,2),       -- ROI as percentage
    roas_ratio DECIMAL(8,2),           -- Return on Ad Spend ratio
    
    -- Timestamps
    created_at TIMESTAMP,
    posted_at TIMESTAMP,
    updated_at TIMESTAMP,
    update_timestamp TIMESTAMP         -- Primary timestamp for ordering
);
```

---

## 🎯 **Current Problems Identified**

### **1. Unrealistic Fixed Values**
```
Current CSV Data (BROKEN):
- views: Always 1,000,000 (hit hardcoded cap)
- likes: Always 500,000 (hit hardcoded cap)
- shares: Always 200,000 (hit hardcoded cap)
- clicks: Always 300,000 (hit hardcoded cap)
- revenue_generated: Always $2,880,000 (mathematical result of caps)
```

### **2. No User Filtering**
- Backend fetches ALL users' data instead of specific user
- Results in aggregated data from multiple users
- Causes "7 days" to show months of data

### **3. Infinite Growth Model**
- Current system only allows growth, never decline
- No realistic plateau or decay phases
- Creates unrealistic hockey-stick growth patterns

### **4. Over-Aggregation**
- Sums hundreds of records instead of focusing on latest state
- Should aggregate latest 3 rows (1 per platform) for current portfolio ROI

---

## 🌟 **Improved Threshold-Based Growth System**

### **Core Philosophy: Realistic Content Lifecycle**

Real social media content follows predictable patterns:

```
📈 Launch Phase    → 🚀 Growth Phase    → 📊 Plateau Phase    → 📉 Decay Phase
   (0-1K views)       (1K-10K views)       (10K-50K views)      (50K+ views)
   High Growth        Moderate Growth      Slow/Variable        Potential Decline
   15-40% per hour    5-20% per hour       -2% to +8%          -12% to +5%
```

---

## 🔧 **Implementation Strategy**

### **1. Threshold-Based Growth Mechanics**

#### **Phase 1: Launch (0 - 1,000 views)**
```python
# Quick growth for new content below threshold
def calculate_launch_growth(current_views: int) -> Dict[str, float]:
    """High growth potential for new content"""
    return {
        "views": random_in_range(1.15, 1.40),    # 15-40% growth
        "likes": random_in_range(1.10, 1.30),    # 10-30% growth  
        "comments": random_in_range(1.05, 1.25), # 5-25% growth
        "shares": random_in_range(1.08, 1.28),   # 8-28% growth
        "clicks": random_in_range(1.12, 1.35),   # 12-35% growth
    }
```

#### **Phase 2: Growth (1,000 - 10,000 views)**
```python
def calculate_growth_phase(current_views: int) -> Dict[str, float]:
    """Moderate sustained growth"""
    return {
        "views": random_in_range(1.05, 1.20),    # 5-20% growth
        "likes": random_in_range(1.03, 1.15),    # 3-15% growth
        "comments": random_in_range(1.01, 1.12), # 1-12% growth
        "shares": random_in_range(1.02, 1.18),   # 2-18% growth
        "clicks": random_in_range(1.04, 1.22),   # 4-22% growth
    }
```

#### **Phase 3: Plateau (10,000 - 50,000 views)**
```python
def calculate_plateau_phase(current_views: int) -> Dict[str, float]:
    """Slow growth with potential for small declines"""
    return {
        "views": random_in_range(1.01, 1.08),    # 1-8% growth
        "likes": random_in_range(0.98, 1.05),    # -2% to +5% (can decrease!)
        "comments": random_in_range(0.95, 1.08), # -5% to +8%
        "shares": random_in_range(0.97, 1.06),   # -3% to +6%
        "clicks": random_in_range(1.00, 1.10),   # 0-10% growth
    }
```

#### **Phase 4: Decay (30+ days old)**
```python
def calculate_decay_phase(content_age_days: int) -> Dict[str, float]:
    """Growth rates decay, but absolute metrics still increase"""
    return {
        "new_views_per_hour": random_in_range(1, 8),        # Very few new views
        "new_likes_per_hour": random_in_range(0, 2),        # Almost no new likes  
        "new_comments_per_hour": random_in_range(0, 0.5),   # Very rare comments
        "new_shares_per_hour": random_in_range(0, 1),       # Rare shares
        "new_clicks_per_hour": random_in_range(0, 3),       # Few new clicks
        "click_through_rate": random_in_range(0.01, 0.025), # Poor CTR 1-2.5%
        "conversion_rate": random_in_range(0.01, 0.02),     # Lower conversion
        "revenue_multiplier": 0.7,                          # 30% revenue penalty
    }
```

### **2. Realistic Metric Caps**

```python
# Much lower, realistic caps
METRIC_CAPS = {
    "views": 100_000,      # 100K max (down from 1M)
    "likes": 8_000,        # 8K max (down from 500K)  
    "comments": 500,       # 500 max (down from 100K)
    "shares": 2_000,       # 2K max (down from 200K)
    "clicks": 5_000,       # 5K max (down from 300K)
}
```

### **3. Platform-Specific Characteristics**

```python
PLATFORM_CHARACTERISTICS = {
    "facebook": {
        "strength": "comments",     # Facebook users comment more
        "multiplier": 1.0,         # Baseline platform
        "avg_order_value": 45,     # Lower AOV
        "conversion_rate": 0.02,   # 2% conversion
    },
    "instagram": {
        "strength": "likes",       # Instagram is visual/likes-focused
        "multiplier": 1.2,         # 20% boost for visual content
        "avg_order_value": 65,     # Medium AOV
        "conversion_rate": 0.025,  # 2.5% conversion
    },
    "youtube": {
        "strength": "views",       # YouTube optimized for watch time
        "multiplier": 1.5,         # 50% boost for video content
        "avg_order_value": 80,     # Higher AOV
        "conversion_rate": 0.03,   # 3% conversion
    }
}
```

---

## 📊 **New ROI Calculation Method**

### **Current Broken Method:**
```python
# ❌ BROKEN: Aggregates ALL rows in date range
total_revenue = sum(r["revenue_generated"] for r in all_rows_in_range)
total_spend = sum(r["ad_spend"] for r in all_rows_in_range)
total_roi = (total_revenue - total_spend) / total_spend * 100
```

### **New Improved Method:**
```python
# ✅ IMPROVED: Latest 3 rows portfolio approach
@router.get("/overview-improved", tags=["roi"])
async def get_portfolio_roi(user_id: str, range: str):
    """Get ROI from latest portfolio state (1 post per platform)"""
    
    platforms = ["facebook", "instagram", "youtube"]
    latest_posts = []
    
    # Get the LATEST post from each platform for this user
    for platform in platforms:
        response = await supabase_client._make_request(
            "GET", "roi_metrics",
            params={
                "user_id": f"eq.{user_id}",           # ✅ User filtering
                "platform": f"eq.{platform}",        # ✅ Platform filtering
                "order": "update_timestamp.desc",
                "limit": "1"                          # ✅ Only latest
            }
        )
        if response.status_code == 200 and response.json():
            latest_posts.extend(response.json())
    
    # Calculate portfolio ROI from latest 3 posts only
    if latest_posts:
        total_revenue = sum(float(post["revenue_generated"]) for post in latest_posts)
        total_spend = sum(float(post["ad_spend"]) for post in latest_posts)
        portfolio_roi = (total_revenue - total_spend) / total_spend * 100 if total_spend > 0 else 0
        
        return {
            "total_revenue": total_revenue,
            "total_spend": total_spend, 
            "total_roi": portfolio_roi,
            "active_posts": len(latest_posts),    # Should be 3
            "posts_breakdown": {
                post["platform"]: {
                    "revenue": post["revenue_generated"],
                    "spend": post["ad_spend"],
                    "views": post["views"],
                    "roi": post["roi_percentage"]
                }
                for post in latest_posts
            }
        }
```

---

## 🎮 **Example Growth Simulation**

### **Scenario: Instagram Reel Lifecycle**

```python
# Day 1: Launch Phase (100 views)
initial_metrics = {
    "views": 100,
    "likes": 8,
    "comments": 2,
    "shares": 3,
    "clicks": 5
}

# Day 2: Launch growth (15-40% boost)
growth_factor = 1.25  # 25% growth
day_2_metrics = {
    "views": 125,       # +25 views
    "likes": 10,        # +2 likes  
    "comments": 3,      # +1 comment
    "shares": 4,        # +1 share
    "clicks": 6         # +1 click
}

# Day 10: Growth phase (1,200 views)
day_10_metrics = {
    "views": 1_200,     # In growth phase
    "likes": 96,        # Good engagement
    "comments": 18,     # Moderate comments
    "shares": 24,       # Decent shares
    "clicks": 48        # Solid clicks
}

# Day 30: Plateau phase (12,000 views)  
day_30_metrics = {
    "views": 12_000,    # Plateau phase
    "likes": 840,       # Growth slowing
    "comments": 120,    # Slower comment growth
    "shares": 180,      # Share growth plateauing
    "clicks": 360       # Click growth steady
}

# Day 60: Decay phase (35,000 views)
day_60_metrics = {
    "views": 35_000,    # Still growing but slower
    "likes": 2_100,     # Might even decrease some days
    "comments": 210,    # Occasional decreases
    "shares": 420,      # Variable growth/decline
    "clicks": 1_050     # Steady but slow
}
```

### **Revenue Calculation Example:**

```python
# Day 30 Instagram Reel Revenue Calculation
platform = "instagram"
metrics = day_30_metrics

# Calculate revenue using realistic conversion rates
conversion_rate = 0.025  # 2.5% for Instagram
avg_order_value = 65     # $65 AOV for Instagram

conversions = metrics["clicks"] * conversion_rate  # 360 * 0.025 = 9 conversions
revenue = conversions * avg_order_value            # 9 * $65 = $585

# Calculate ad spend
cpc = 1.40  # Instagram CPC range
cpm = 18.00 # Instagram CPM range
ad_spend = (metrics["clicks"] * cpc) + (metrics["views"] * cpm / 1000)
ad_spend = (360 * 1.40) + (12000 * 18.00 / 1000) = $504 + $216 = $720

# Calculate ROI
roi_percentage = ((revenue - ad_spend) / ad_spend) * 100
roi_percentage = (($585 - $720) / $720) * 100 = -18.75%

# This is realistic! Not all content is profitable
```

---

## 🏗️ **Implementation Files**

### **1. Improved Data Generator**
```python
# File: bos_solution/backend/improved_roi_generator.py

class ImprovedROIGenerator:
    def __init__(self):
        self.metric_caps = {
            "views": 100_000,
            "likes": 8_000,
            "comments": 500,
            "shares": 2_000,
            "clicks": 5_000,
        }
    
    def calculate_lifecycle_phase(self, current_views: int) -> str:
        """Determine which growth phase content is in"""
        if current_views < 1_000:
            return "launch"
        elif current_views < 10_000:
            return "growth"  
        elif current_views < 50_000:
            return "plateau"
        else:
            return "decay"
    
    def get_growth_multipliers(self, phase: str) -> Dict[str, Tuple[float, float]]:
        """Get min/max growth multipliers for each phase"""
        multipliers = {
            "launch": {
                "views": (1.15, 1.40),
                "likes": (1.10, 1.30),
                "comments": (1.05, 1.25),
                "shares": (1.08, 1.28),
                "clicks": (1.12, 1.35),
            },
            "growth": {
                "views": (1.05, 1.20),
                "likes": (1.03, 1.15),
                "comments": (1.01, 1.12),
                "shares": (1.02, 1.18),
                "clicks": (1.04, 1.22),
            },
            "plateau": {
                "views": (1.01, 1.08),
                "likes": (0.98, 1.05),    # Can decrease!
                "comments": (0.95, 1.08),
                "shares": (0.97, 1.06),
                "clicks": (1.00, 1.10),
            },
            "decay": {
                "views": (0.95, 1.03),
                "likes": (0.92, 1.02),
                "comments": (0.90, 1.05),
                "shares": (0.88, 1.03),
                "clicks": (0.93, 1.04),
            }
        }
        return multipliers[phase]
```

### **2. Database Cleanup Script**
```python
# File: bos_solution/backend/cleanup_and_reset_roi.py

async def cleanup_roi_data():
    """Remove all existing ROI data and start fresh"""
    print("🧹 Cleaning up ROI data...")
    
    response = await supabase_client._make_request(
        "DELETE", "roi_metrics",
        params={"id": "gte.0"}  # Delete all rows
    )
    
    if response.status_code in [200, 204]:
        print("✅ All ROI data deleted")
        return True
    return False

async def seed_realistic_initial_data(user_id: str):
    """Create 1 realistic post per platform"""
    platforms = [
        {"name": "facebook", "type": "post"},
        {"name": "instagram", "type": "reel"},
        {"name": "youtube", "type": "video"}
    ]
    
    initial_data = {
        "facebook": {"views": 850, "likes": 45, "comments": 8, "shares": 12, "clicks": 25},
        "instagram": {"views": 1200, "likes": 95, "comments": 15, "shares": 28, "clicks": 42},
        "youtube": {"views": 1800, "likes": 85, "comments": 22, "shares": 35, "clicks": 65},
    }
    
    for platform_info in platforms:
        platform = platform_info["name"]
        metrics = initial_data[platform]
        
        # Calculate realistic financial metrics
        revenue = calculate_realistic_revenue(platform, metrics)
        ad_spend = calculate_realistic_ad_spend(platform, metrics)
        roi = ((revenue - ad_spend) / ad_spend) * 100 if ad_spend > 0 else 0
        
        record = {
            "user_id": user_id,
            "platform": platform,
            "content_type": platform_info["type"],
            "content_category": "generic",
            **metrics,
            "saves": metrics["likes"] // 4,
            "ad_spend": ad_spend,
            "revenue_generated": revenue,
            "roi_percentage": round(roi, 2),
            "roas_ratio": round(revenue / ad_spend, 2) if ad_spend > 0 else 0,
            "update_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await supabase_client._make_request("POST", "roi_metrics", data=record)
        print(f"✅ Seeded {platform}: {metrics['views']} views, ${revenue:.2f} revenue, {roi:.1f}% ROI")
```

### **3. Improved ROI Endpoint**
```python
# Add to: bos_solution/backend/app/api/v1/endpoints/roi.py

@router.get("/overview-improved", tags=["roi"])
async def get_improved_overview(
    user_id: str = Query(..., description="Clerk user id"),
    range: str = Query("7d", pattern="^(7d|30d|90d)$"),  # Removed 1y
):
    """
    Improved ROI overview that:
    - Gets latest 1 post per platform for the user
    - Calculates portfolio ROI from current state
    - Shows realistic growth patterns
    """
    try:
        cache_key = f"roi_improved:{user_id}:{range}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        platforms = ["facebook", "instagram", "youtube"]
        current_portfolio = []
        
        # Get latest post from each platform
        for platform in platforms:
            response = await supabase_client._make_request(
                "GET", "roi_metrics",
                params={
                    "user_id": f"eq.{user_id}",           # ✅ User filtering
                    "platform": f"eq.{platform}",
                    "order": "update_timestamp.desc",
                    "limit": "1"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    current_portfolio.extend(data)
        
        if current_portfolio:
            # Calculate portfolio metrics from latest posts
            total_revenue = sum(float(post["revenue_generated"]) for post in current_portfolio)
            total_spend = sum(float(post["ad_spend"]) for post in current_portfolio)
            total_views = sum(int(post["views"]) for post in current_portfolio)
            total_engagement = sum(
                int(post["likes"]) + int(post["comments"]) + int(post["shares"])
                for post in current_portfolio
            )
            
            portfolio_roi = (total_revenue - total_spend) / total_spend * 100 if total_spend > 0 else 0
            
            result = {
                "total_revenue": round(total_revenue, 2),
                "total_spend": round(total_spend, 2),
                "total_roi": round(portfolio_roi, 2),
                "total_views": total_views,
                "total_engagement": total_engagement,
                "active_posts": len(current_portfolio),
                "portfolio_breakdown": {
                    post["platform"]: {
                        "revenue": float(post["revenue_generated"]),
                        "spend": float(post["ad_spend"]),
                        "views": int(post["views"]),
                        "roi": float(post["roi_percentage"]),
                        "lifecycle_phase": determine_lifecycle_phase(int(post["views"]))
                    }
                    for post in current_portfolio
                }
            }
        else:
            result = {
                "total_revenue": 0,
                "total_spend": 0,
                "total_roi": 0,
                "total_views": 0,
                "total_engagement": 0,
                "active_posts": 0,
                "portfolio_breakdown": {}
            }
        
        cache.set(cache_key, result, ttl_seconds=1800)  # 30 min cache
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Improved overview failed: {e}")

def determine_lifecycle_phase(views: int) -> str:
    """Determine content lifecycle phase"""
    if views < 1_000:
        return "launch"
    elif views < 10_000:
        return "growth"
    elif views < 50_000:
        return "plateau"
    else:
        return "decay"
```

---

## 🎯 **Expected Results**

### **Before Implementation:**
```
❌ Current Broken Dashboard:
- Total ROI: 947% (unrealistic)
- Total Revenue: $288,000,000 (absurd)
- Total Ad Spend: $27,500,000 (impossible)
- Data Points: 100+ records (overwhelming)
- Shows: All users' data for months
```

### **After Implementation:**
```
✅ Improved Realistic Dashboard:
- Total ROI: 85% (realistic for good performance)
- Total Revenue: $1,847 (from 3 current posts)
- Total Ad Spend: $1,285 (reasonable ad spend)
- Data Points: 3 (clean portfolio view)
- Shows: Only your latest portfolio state

Portfolio Breakdown:
┌─────────────┬──────────┬──────────┬──────────┬─────────────────┐
│ Platform    │ Revenue  │ Ad Spend │ ROI      │ Lifecycle Phase │
├─────────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Facebook    │ $485     │ $365     │ 32.9%    │ Growth          │
│ Instagram   │ $672     │ $445     │ 51.0%    │ Plateau         │
│ YouTube     │ $690     │ $475     │ 45.3%    │ Growth          │
├─────────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Portfolio   │ $1,847   │ $1,285   │ 43.7%    │ Mixed           │
└─────────────┴──────────┴──────────┴──────────┴─────────────────┘
```

---

## 📝 **Implementation Checklist**

### **Phase 1: Foundation** ✅
- [ ] Stop background ROI scheduler 
- [ ] Clean up existing database data
- [ ] Implement improved data generator with lifecycle phases
- [ ] Seed realistic initial data (1 post per platform)

### **Phase 2: Backend** ✅
- [ ] Update ROI overview endpoint to use latest 3 rows
- [ ] Add proper user filtering
- [ ] Implement threshold-based growth mechanics
- [ ] Add lifecycle phase detection

### **Phase 3: Frontend** ✅
- [ ] Update frontend to use improved overview endpoint
- [ ] Add lifecycle phase indicators to dashboard
- [ ] Show portfolio breakdown by platform
- [ ] Remove 1y option (keep 7d, 30d, 90d)

### **Phase 4: Testing** ✅
- [ ] Test threshold-based growth across all phases
- [ ] Verify plateau and decay mechanics work
- [ ] Confirm user filtering works correctly
- [ ] Validate realistic ROI calculations

---

## 🚀 **Next Steps**

1. **Stop Current System**
   ```bash
   # Kill the current ROI scheduler
   tasklist | findstr python
   taskkill /F /PID [roi_scheduler_pid]
   ```

2. **Run Cleanup Script**
   ```bash
   cd bos_solution/backend  
   python cleanup_and_reset_roi.py
   ```

3. **Deploy Improved System**
   ```bash
   # Update data generator
   python improved_roi_generator.py
   
   # Test new endpoint
   python test_improved_overview.py
   ```

4. **Update Frontend**
   - Change API calls to use `/overview-improved` endpoint
   - Add lifecycle phase indicators
   - Remove 1y time range option

---

## 💡 **Key Benefits**

✅ **Realistic Growth**: Content follows natural lifecycle patterns  
✅ **Proper User Filtering**: Shows only your data, not everyone's  
✅ **Portfolio View**: Focus on current state, not historical aggregation  
✅ **Threshold-Based**: Quick growth below thresholds, natural plateaus above  
✅ **Platform-Specific**: Each platform has unique characteristics  
✅ **Financial Accuracy**: Realistic revenue/spend ratios and ROI calculations  
✅ **Lifecycle Awareness**: Dashboard shows which phase each post is in  

This improved system provides a much more accurate and actionable ROI dashboard that reflects real-world social media marketing performance! 🎯

---

## 📅 **90-Day Historical Data Generation - 3 CONSISTENT POSTS (1 PER PLATFORM)**

### **🎯 Key Innovation: 3 Consistent Posts That Grow Realistically Over Time**

Instead of creating new content every day, we use a **CONSISTENT POST STRATEGY**:
- **3 posts created at start**: 1 Facebook + 1 Instagram + 1 YouTube
- **Same post_id throughout**: Each post maintains its identity for 90 days
- **90 days ago → 7 days ago**: Daily updates of the same 3 posts
- **Last 7 days**: 10-minute interval updates of the same 3 posts
- **FORWARD TIMESTAMPS**: Starting from 90 days ago (May 26th 00:00) going to now (August 24th 11:00)
- **90%+ fewer database writes** while maintaining realistic growth patterns

### **📅 Timeline Breakdown:**
```
🚀 START: May 26th, 2024 at 00:00 (90 days ago)
📊 PHASE 1 (90d→7d ago): Daily updates of 3 consistent posts
   - Each day: Update same Facebook + Instagram + YouTube posts
   - Internal simulation: 144 ten-minute intervals of growth per day
   - Database writes: 249 rows (83 days × 3 platforms)
   - Post IDs remain constant throughout

⏰ PHASE 2 (Last 7 days): 10-minute interval updates of same 3 posts
   - Every 10 minutes: Update same 3 posts (1 per platform)
   - Total intervals: 1,008 (7 days × 144 intervals/day)
   - Database writes: 1,008 rows
   - Same post IDs continue

🎯 END: August 24th, 2024 at 11:00 (current time)
📊 TOTAL WRITES: ~1,257 rows vs 38,880 if all 10-minute intervals
🚀 EFFICIENCY: 96.8% fewer database writes!
🎯 CONTENT: 3 consistent posts that grow over 90 days
```

### **Balanced Growth Philosophy**

Instead of overly restrictive limits, we use **smart scaling factors** that:
- Allow for excellent performance (100-200% ROI is possible!)
- Prevent absurd numbers (no 800-900% ROI)
- Create natural variation over 90 days
- Respect content lifecycle patterns

### **Target ROI Ranges by Performance Level**

```python
# Realistic ROI ranges we want to achieve
ROI_PERFORMANCE_LEVELS = {
    "poor": (-20, 15),        # Some content loses money
    "average": (15, 45),      # Most content is modestly profitable  
    "good": (45, 85),         # Good content performs well
    "excellent": (85, 150),   # Exceptional content can be very profitable
    "viral": (150, 250),      # Rare viral content can be amazing
}
```

### **90-Day Data Generation Strategy - 10-Minute Intervals**

#### **Every 10 Minutes: Boosted Content Creation (FORWARD TIMELINE)**
```python
# Simulate your current 10-minute scheduler pattern
def generate_10min_interval_data():
    """Every 10 minutes, create 1-3 pieces of content"""
    
    # Calculate total intervals in 90 days
    total_minutes = 90 * 24 * 60  # 90 days * 24 hours * 60 minutes
    total_10min_intervals = total_minutes // 10  # = 12,960 intervals
    
    # Start from 90 days ago at 00:00
    start_date = datetime.now() - timedelta(days=90)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    for interval in range(total_10min_intervals):
        # Calculate timestamp for this interval (going FORWARD from start date)
        minutes_forward = interval * 10
        timestamp = start_date + timedelta(minutes=minutes_forward)
        
        # BOOST: Create 1-3 pieces of content per interval
        content_count = random.randint(1, 3)
        
        for content_idx in range(content_count):
            platform = random.choice(["facebook", "instagram", "youtube"])
            performance = select_random_performance()
            
            # FORWARD timestamps: starts from 90 days ago, goes to now
            record = {
                "created_at": timestamp.isoformat(),
                "posted_at": timestamp.isoformat(), 
                "updated_at": timestamp.isoformat(),
                "update_timestamp": timestamp.isoformat(),  # Key for ordering
                # ... other fields
            }
            
            # Insert into database (simulating your current scheduler)
            await insert_roi_record(record)
    
    print(f"✅ Generated {total_10min_intervals} intervals with boosted content")
    print(f"📊 Average: {total_content / total_10min_intervals:.1f} pieces per interval")
    print(f"📅 Timeline: {start_date.strftime('%Y-%m-%d %H:%M')} → {datetime.now().strftime('%Y-%m-%d %H:%M')}")
```

#### **What This Achieves:**
- **Maintains Pattern**: Same 10-minute insertion rhythm you're used to
- **Boosts Volume**: 1-3 pieces per interval instead of just 1
- **Forward Timestamps**: Starts from 90 days ago (May 26th 00:00) going to now (August 24th 11:00)
- **Realistic Data**: No more fixed $2.88M revenue or 1M views
- **User Filtering**: Only your data, not everyone's

#### **Content Performance Distribution**
```python
# Natural distribution of content performance (realistic!)
PERFORMANCE_DISTRIBUTION = {
    "poor": 0.20,        # 20% of content underperforms
    "average": 0.35,     # 35% is average performance  
    "good": 0.25,        # 25% performs well
    "excellent": 0.15,   # 15% is excellent
    "viral": 0.05,       # 5% goes viral (rare!)
}
```

### **Engagement Growth Curves**

#### **Launch Content (Age: 0-7 days)**
```python
def generate_launch_metrics(performance_level: str) -> Dict:
    """Generate realistic starting metrics based on expected performance"""
    
    base_metrics = {
        "poor": {"views": (50, 200), "likes": (3, 15), "clicks": (2, 8)},
        "average": {"views": (150, 500), "likes": (12, 40), "clicks": (6, 20)},
        "good": {"views": (400, 1200), "likes": (30, 90), "clicks": (16, 48)},
        "excellent": {"views": (800, 2500), "likes": (60, 200), "clicks": (32, 100)},
        "viral": {"views": (2000, 8000), "likes": (150, 600), "clicks": (80, 320)},
    }
    
    ranges = base_metrics[performance_level]
    return {
        "views": random.randint(*ranges["views"]),
        "likes": random.randint(*ranges["likes"]),
        "comments": random.randint(1, max(2, ranges["likes"][1] // 20)),
        "shares": random.randint(1, max(2, ranges["likes"][1] // 15)),
        "clicks": random.randint(*ranges["clicks"]),
        "saves": random.randint(0, max(1, ranges["likes"][1] // 25)),
    }
```

#### **Growth Simulation Over 90 Days**
```python
def simulate_content_growth(initial_metrics: Dict, content_age_days: int, performance_level: str) -> Dict:
    """Simulate realistic growth over time with performance-based scaling"""
    
    # Performance multipliers affect overall growth potential
    performance_multipliers = {
        "poor": 0.7,        # Slow growth, low engagement
        "average": 1.0,     # Standard growth
        "good": 1.4,        # Above average growth
        "excellent": 1.8,   # High growth potential
        "viral": 2.5,       # Explosive growth (but rare)
    }
    
    multiplier = performance_multipliers[performance_level]
    current_metrics = initial_metrics.copy()
    
    # Simulate daily growth
    for day in range(content_age_days):
        phase = determine_growth_phase(day)
        daily_growth = get_daily_growth_rates(phase, performance_level)
        
        # Apply daily growth with diminishing returns
        for metric in ["views", "likes", "comments", "shares", "clicks", "saves"]:
            daily_increase = max(0, int(current_metrics[metric] * daily_growth[metric] * multiplier))
            current_metrics[metric] += daily_increase
            
            # Apply soft caps (exponential decay as we approach limits)
            cap = get_soft_cap(metric, performance_level)
            if current_metrics[metric] > cap * 0.8:
                # Exponential decay as we approach cap
                reduction_factor = 1 - ((current_metrics[metric] - cap * 0.8) / (cap * 0.2))
                current_metrics[metric] = int(current_metrics[metric] * max(0.1, reduction_factor))
    
    return current_metrics

def get_soft_cap(metric: str, performance_level: str) -> int:
    """Get soft caps that vary by performance level (no hard limits!)"""
    base_caps = {
        "views": {"poor": 5_000, "average": 15_000, "good": 45_000, "excellent": 100_000, "viral": 250_000},
        "likes": {"poor": 300, "average": 1_200, "good": 3_500, "excellent": 8_000, "viral": 20_000},
        "comments": {"poor": 20, "average": 80, "good": 250, "excellent": 500, "viral": 1_200},
        "shares": {"poor": 50, "average": 200, "good": 600, "excellent": 1_500, "viral": 4_000},
        "clicks": {"poor": 100, "average": 400, "good": 1_200, "excellent": 3_000, "viral": 8_000},
        "saves": {"poor": 25, "average": 100, "good": 300, "excellent": 750, "viral": 2_000},
    }
    return base_caps[metric][performance_level]
```

### **Financial Calculation with Realistic ROI Targeting**

```python
def calculate_realistic_financials(metrics: Dict, platform: str, performance_level: str, age_days: int) -> Dict:
    """Calculate financial metrics targeting realistic ROI ranges"""
    
    # Platform-specific base rates
    platform_data = {
        "facebook": {"base_cpc": 1.2, "base_cpm": 12, "base_aov": 45},
        "instagram": {"base_cpc": 1.8, "base_cpm": 15, "base_aov": 65},
        "youtube": {"base_cpc": 0.8, "base_cpm": 8, "base_aov": 80},
    }
    
    data = platform_data[platform]
    
    # Add realistic variation to costs (±25%)
    cpc = data["base_cpc"] * random.uniform(0.75, 1.25)
    cpm = data["base_cpm"] * random.uniform(0.75, 1.25)
    aov = data["base_aov"] * random.uniform(0.85, 1.15)
    
    # Calculate ad spend
    ad_spend = (metrics["clicks"] * cpc) + (metrics["views"] * cpm / 1000)
    
    # Target ROI based on performance level
    target_roi_ranges = {
        "poor": (-20, 15),
        "average": (15, 45),
        "good": (45, 85),
        "excellent": (85, 150),
        "viral": (150, 250),
    }
    
    # Pick a target ROI within the range for this performance level
    min_roi, max_roi = target_roi_ranges[performance_level]
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
    implied_conversion_rate = implied_conversions / metrics["clicks"] if metrics["clicks"] > 0 else 0
    
    # If conversion rate is unrealistic (>10%), scale back revenue
    if implied_conversion_rate > 0.10:
        max_conversions = metrics["clicks"] * 0.10
        actual_revenue = max_conversions * aov
        actual_roi = ((actual_revenue - ad_spend) / ad_spend * 100) if ad_spend > 0 else 0
    
    return {
        "ad_spend": round(ad_spend, 2),
        "revenue_generated": round(actual_revenue, 2),
        "roi_percentage": round(actual_roi, 2),
        "roas_ratio": round(actual_revenue / ad_spend, 2) if ad_spend > 0 else 0,
        "cost_per_click": round(cpc, 2),
        "cost_per_impression": round(cpm / 1000, 4),
        "implied_conversion_rate": round(implied_conversion_rate, 4),
    }
```

---

## 🏗️ **90-Day Data Generation Script**

### **Complete Implementation**

```python
# File: bos_solution/backend/generate_90_day_roi_data.py

#!/usr/bin/env python3
"""
90-Day ROI Data Generator
- Creates realistic historical data for the last 90 days
- Balances performance (not too high, not too low)
- Simulates content lifecycle with natural variation
- Targets realistic ROI ranges: poor (-20% to 15%), excellent (85% to 150%)
"""

import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple

# Add backend to path
sys.path.append(str(Path(__file__).parent))
from app.core.supabase_client import supabase_client

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

def select_random_performance() -> str:
    """Select performance level based on realistic distribution"""
    rand = random.random()
    cumulative = 0
    for performance, probability in PERFORMANCE_DISTRIBUTION:
        cumulative += probability
        if rand <= cumulative:
            return performance
    return "average"

def generate_content_timeline(days: int = 90) -> List[Dict]:
    """Generate a realistic content posting timeline"""
    timeline = []
    platforms = ["facebook", "instagram", "youtube"]
    content_types = {
        "facebook": ["post", "video", "photo"],
        "instagram": ["post", "reel", "story", "carousel"],
        "youtube": ["video", "short"]
    }
    
    # Generate 2-4 posts per week (realistic posting frequency)
    posts_per_week = random.randint(2, 4)
    total_posts = (days // 7) * posts_per_week
    
    for i in range(total_posts):
        # Random day within the 90-day period
        age_days = random.randint(1, days)
        platform = random.choice(platforms)
        content_type = random.choice(content_types[platform])
        performance = select_random_performance()
        
        timeline.append({
            "age_days": age_days,
            "platform": platform,
            "content_type": content_type,
            "performance": performance,
            "post_date": datetime.now(timezone.utc) - timedelta(days=age_days)
        })
    
    # Sort by age (oldest first)
    timeline.sort(key=lambda x: x["age_days"], reverse=True)
    return timeline

async def cleanup_existing_data(user_id: str):
    """Clean up existing ROI data for the user"""
    print(f"🧹 Cleaning existing data for user: {user_id}")
    
    try:
        response = await supabase_client._make_request(
            "DELETE", "roi_metrics",
            params={"user_id": f"eq.{user_id}"}
        )
        
        if response.status_code in [200, 204]:
            print("✅ Existing data cleaned successfully")
            return True
        else:
            print(f"⚠️  Cleanup response: {response.status_code}")
            return True  # Continue anyway
    except Exception as e:
        print(f"⚠️  Cleanup error (continuing anyway): {e}")
        return True

async def generate_90_day_data(user_id: str = "user_31VgZVmUnz3XYl4DnOB1NQG5TwP"):
    """Generate 90 days of realistic ROI data"""
    
    print("🚀 Generating 90 days of realistic ROI data...")
    print("=" * 60)
    
    # Clean existing data
    await cleanup_existing_data(user_id)
    
    # Generate content timeline
    timeline = generate_content_timeline(90)
    
    print(f"📅 Generated {len(timeline)} pieces of content over 90 days")
    print(f"👤 User ID: {user_id}")
    print()
    
    total_inserted = 0
    performance_counts = {"poor": 0, "average": 0, "good": 0, "excellent": 0, "viral": 0}
    
    for i, content in enumerate(timeline):
        age_days = content["age_days"]
        platform = content["platform"] 
        content_type = content["content_type"]
        performance = content["performance"]
        post_date = content["post_date"]
        
        # Generate initial metrics based on performance level
        initial_metrics = generate_initial_metrics(performance, platform)
        
        # Simulate growth over the content's lifetime
        current_metrics = simulate_growth_over_time(initial_metrics, age_days, performance, platform)
        
        # Calculate financial metrics targeting realistic ROI
        financials = calculate_realistic_financials(current_metrics, platform, performance, age_days)
        
        # Create database record
        record = {
            "user_id": user_id,
            "platform": platform,
            "campaign_id": None,
            "post_id": f"post_{random.randint(10000, 99999)}",
            "content_type": content_type,
            "content_category": "generic",
            "views": current_metrics["views"],
            "likes": current_metrics["likes"],
            "comments": current_metrics["comments"],
            "shares": current_metrics["shares"],
            "saves": current_metrics["saves"],
            "clicks": current_metrics["clicks"],
            "ad_spend": financials["ad_spend"],
            "revenue_generated": financials["revenue_generated"],
            "cost_per_click": financials["cost_per_click"],
            "cost_per_impression": financials["cost_per_impression"],
            "roi_percentage": financials["roi_percentage"],
            "roas_ratio": financials["roas_ratio"],
            "created_at": post_date.isoformat(),
            "posted_at": post_date.isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "update_timestamp": post_date.isoformat(),
        }
        
        # Insert into database
        try:
            response = await supabase_client._make_request("POST", "roi_metrics", data=record)
            if response.status_code == 201:
                total_inserted += 1
                performance_counts[performance] += 1
                
                # Print progress every 10 records
                if total_inserted % 10 == 0:
                    print(f"✅ Inserted {total_inserted}/{len(timeline)} records...")
                    
            else:
                print(f"❌ Failed to insert {platform} {content_type}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error inserting record: {e}")
            continue
    
    print(f"\n🎉 Data generation completed!")
    print(f"📊 Inserted {total_inserted} total records")
    print(f"📈 Performance distribution:")
    for perf, count in performance_counts.items():
        percentage = (count / total_inserted * 100) if total_inserted > 0 else 0
        roi_range = ROI_RANGES[perf]
        print(f"   {perf.title()}: {count} records ({percentage:.1f}%) - ROI: {roi_range[0]}% to {roi_range[1]}%")
    
    return total_inserted

# Helper functions for metric generation
def generate_initial_metrics(performance: str, platform: str) -> Dict:
    """Generate realistic starting metrics"""
    base_ranges = {
        "poor": {"views": (50, 300), "likes": (3, 20), "clicks": (2, 12)},
        "average": {"views": (200, 800), "likes": (15, 60), "clicks": (8, 32)},
        "good": {"views": (600, 2000), "likes": (45, 150), "clicks": (24, 80)},
        "excellent": {"views": (1500, 5000), "likes": (120, 400), "clicks": (60, 200)},
        "viral": {"views": (4000, 15000), "likes": (300, 1200), "clicks": (160, 600)},
    }
    
    # Platform multipliers
    multipliers = {
        "facebook": {"views": 0.8, "likes": 1.1, "clicks": 0.9},
        "instagram": {"views": 1.2, "likes": 1.4, "clicks": 1.1},
        "youtube": {"views": 1.5, "likes": 0.9, "clicks": 1.3},
    }
    
    ranges = base_ranges[performance]
    mult = multipliers[platform]
    
    views = int(random.randint(*ranges["views"]) * mult["views"])
    likes = int(random.randint(*ranges["likes"]) * mult["likes"])
    clicks = int(random.randint(*ranges["clicks"]) * mult["clicks"])
    
    return {
        "views": views,
        "likes": likes,
        "comments": random.randint(1, max(2, likes // 20)),
        "shares": random.randint(1, max(2, likes // 15)),
        "saves": random.randint(0, max(1, likes // 25)),
        "clicks": clicks,
    }

def simulate_growth_over_time(initial: Dict, age_days: int, performance: str, platform: str) -> Dict:
    """Simulate realistic growth over content lifetime"""
    
    # Performance growth multipliers
    growth_multipliers = {
        "poor": 0.3,        # Slow growth
        "average": 1.0,     # Standard growth
        "good": 1.8,        # Good growth
        "excellent": 2.5,   # High growth
        "viral": 4.0,       # Explosive growth
    }
    
    multiplier = growth_multipliers[performance]
    current = initial.copy()
    
    # Simulate daily growth with diminishing returns
    for day in range(age_days):
        # Growth slows over time
        age_factor = max(0.1, 1 - (day * 0.01))  # 1% reduction per day
        daily_multiplier = multiplier * age_factor
        
        for metric in current.keys():
            daily_growth = random.uniform(0.02, 0.08) * daily_multiplier  # 2-8% base growth
            current[metric] += int(current[metric] * daily_growth)
    
    # Apply soft caps to prevent unrealistic numbers
    caps = get_performance_caps(performance)
    for metric, cap in caps.items():
        if current[metric] > cap:
            # Soft cap with exponential decay
            excess = current[metric] - cap
            current[metric] = cap + int(excess * 0.3)  # Keep 30% of excess
    
    return current

def get_performance_caps(performance: str) -> Dict:
    """Get realistic caps based on performance level"""
    caps = {
        "poor": {"views": 2_000, "likes": 150, "comments": 25, "shares": 50, "clicks": 80, "saves": 40},
        "average": {"views": 8_000, "likes": 600, "comments": 80, "shares": 200, "clicks": 320, "saves": 150},
        "good": {"views": 25_000, "likes": 2_000, "comments": 250, "shares": 600, "clicks": 1_000, "saves": 500},
        "excellent": {"views": 60_000, "likes": 5_000, "comments": 600, "shares": 1_500, "clicks": 2_400, "saves": 1_200},
        "viral": {"views": 150_000, "likes": 12_000, "comments": 1_500, "shares": 4_000, "clicks": 6_000, "saves": 3_000},
    }
    return caps[performance]

def calculate_realistic_financials(metrics: Dict, platform: str, performance: str, age_days: int) -> Dict:
    """Calculate financial metrics targeting realistic ROI ranges"""
    
    platform_data = {
        "facebook": {"base_cpc": 1.2, "base_cpm": 12, "base_aov": 45},
        "instagram": {"base_cpc": 1.8, "base_cpm": 15, "base_aov": 65},
        "youtube": {"base_cpc": 0.8, "base_cpm": 8, "base_aov": 80},
    }
    
    data = platform_data[platform]
    
    # Realistic cost variation
    cpc = data["base_cpc"] * random.uniform(0.75, 1.25)
    cpm = data["base_cpm"] * random.uniform(0.75, 1.25)
    aov = data["base_aov"] * random.uniform(0.85, 1.15)
    
    # Calculate ad spend
    ad_spend = (metrics["clicks"] * cpc) + (metrics["views"] * cpm / 1000)
    
    # Target ROI for this performance level
    roi_min, roi_max = ROI_RANGES[performance]
    target_roi = random.uniform(roi_min, roi_max)
    
    # Age penalty (older content performs worse)
    age_penalty = max(0.4, 1 - (age_days * 0.006))  # 0.6% penalty per day
    target_roi *= age_penalty
    
    # Calculate revenue to achieve target ROI
    target_revenue = ad_spend * (1 + target_roi / 100) if target_roi > -100 else ad_spend * 0.1
    
    # Add realistic variation
    actual_revenue = max(0, target_revenue * random.uniform(0.85, 1.15))
    
    # Calculate final metrics
    actual_roi = ((actual_revenue - ad_spend) / ad_spend * 100) if ad_spend > 0 else 0
    roas = actual_revenue / ad_spend if ad_spend > 0 else 0
    
    return {
        "ad_spend": round(ad_spend, 2),
        "revenue_generated": round(actual_revenue, 2),
        "roi_percentage": round(actual_roi, 2),
        "roas_ratio": round(roas, 2),
        "cost_per_click": round(cpc, 2),
        "cost_per_impression": round(cpm / 1000, 4),
    }

if __name__ == "__main__":
    asyncio.run(generate_90_day_data())
```

---

## 🎯 **Expected 90-Day Results - 3 CONSISTENT POSTS (1 PER PLATFORM)**

### **📊 Data Volume & Pattern**
```
⏰ Consistent Post Strategy Breakdown:
┌─────────────────┬─────────────┬─────────────────────┬─────────────────┐
│ Time Period     │ Update Freq │ Content Strategy   │ Database Writes │
├─────────────────┼─────────────┼─────────────────────┼─────────────────┤
│ 90d → 7d ago   │ Daily       │ Update same 3 posts│ 249 rows       │
│ Last 7 days    │ 10-min      │ Update same 3 posts│ 1,008 rows     │
│ Total          │ Hybrid      │ 3 posts grow over 90d│ 1,257 rows     │
└─────────────────┴─────────────┴─────────────────────┴─────────────────┘

🚀 EFFICIENCY: 96.8% fewer database writes vs full 10-minute intervals
📅 TIMELINE: May 26th 00:00 → August 24th 11:00 (FORWARD progression)
💾 DATABASE FRIENDLY: Only ~1,257 rows instead of 38,880!
🎯 CONTENT: 3 consistent posts (Facebook, Instagram, YouTube) that grow over time
```

### **Portfolio Performance Distribution**
```
📊 Content Performance Over 90 Days:
┌─────────────┬─────────┬─────────────┬─────────────────┐
│ Performance │ Count   │ ROI Range   │ Example Content │
├─────────────┼─────────┼─────────────┼─────────────────┤
│ Poor        │ ~2,600  │ -20% to 15% │ Underperforming │
│ Average     │ ~4,500  │ 15% to 45%  │ Standard posts  │
│ Good        │ ~3,200  │ 45% to 85%  │ Well-performing │
│ Excellent   │ ~1,900  │ 85% to 150% │ High engagement │
│ Viral       │ ~650    │ 150% to 250%│ Breakout hits   │
├─────────────┼─────────┼─────────────┼─────────────────┤
│ Total       │ ~12,960 │ Portfolio   │ Mixed content   │
└─────────────┴─────────┴─────────────┴─────────────────┘

🎯 Overall Portfolio ROI: 65-85% (realistic blend)
💰 Total Revenue: $150,000-250,000 (90 days)
💸 Total Ad Spend: $120,000-180,000 (90 days)
📈 Active Posts: 3 latest (for dashboard view)
📊 Historical Data: Rich 90-day timeline for trends
```

### **Benefits of This BOOSTED 10-Minute Approach**

✅ **Maintains Your Pattern**: Same 10-minute insertion rhythm you're used to  
✅ **Boosts Data Volume**: 1-3 pieces per interval instead of just 1  
✅ **Forward Timestamps**: Starts from 90 days ago (May 26th 00:00) going to now (August 24th 11:00)  
✅ **Realistic Variation**: Not too restrictive, not too crazy  
✅ **Natural Distribution**: Most content is average, some excellent, few viral  
✅ **Performance-Based**: Good content gets rewarded with higher ROI  
✅ **Age Awareness**: Older content performs worse (realistic!)  
✅ **Platform Differences**: Each platform has unique characteristics  
✅ **Portfolio View**: Dashboard shows latest state, trends show history  
✅ **Rich Historical Data**: 90 days of data for trend analysis  

This system **SIMULATES** your current scheduler behavior but with much more realistic data and proper user filtering! 🚀

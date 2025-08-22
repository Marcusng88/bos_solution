# ROI Dashboard Implementation Plan

## **Project Overview**
We are building a comprehensive marketing application that helps users manage multiple social media platforms (Facebook, Instagram, YouTube, TikTok) with centralized management. The ROI dashboard is a critical component that provides financial analytics and performance insights.

## **Current State Analysis**

### **What We Have:**
- ✅ Login system (Clerk integration)
- ✅ Data retrieval infrastructure
- ✅ Campaign table structure
- ✅ Basic ROI dashboard UI components
- ✅ Competitor analysis (handled by team)

### **What We Need:**
- ❌ Realistic ROI data for analysis
- ❌ Database tables for ROI metrics
- ❌ Automated data generation system
- ❌ Integration with existing campaign structure

## **Database Architecture**

### **Table Structure Overview**
- **`campaign_data`** - Existing table (handled by friend for optimization)
- **`campaign_with_user_id`** - New table with user_id added for ROI integration
- **`roi_metrics`** - New table for ROI analytics and performance tracking
- **`platform_metrics`** - New table for platform-specific metrics

### **User Relationship**
- **`user_id`** in all new tables references **`users.clerk_id`** from Clerk authentication
- This ensures proper data isolation between users while maintaining compatibility

### **1. Campaign Table with User ID (New)**
```sql
CREATE TABLE campaign_with_user_id (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,           -- References users.clerk_id
    name VARCHAR(255),
    date DATE,
    impressions INTEGER,
    clicks INTEGER,
    ctr DOUBLE PRECISION,
    cpc DOUBLE PRECISION,
    spend DOUBLE PRECISION,
    budget DOUBLE PRECISION,
    conversions INTEGER,
    net_profit DOUBLE PRECISION,
    ongoing VARCHAR(10),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_campaign_with_user_id_user_id ON campaign_with_user_id(user_id);
CREATE INDEX idx_campaign_with_user_id_date ON campaign_with_user_id(date);
```

### **2. Primary ROI Metrics Table (New)**
```sql
CREATE TABLE roi_metrics (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,           -- References users.clerk_id
    platform VARCHAR(50) NOT NULL,           -- 'facebook', 'instagram', 'youtube'
    campaign_id INTEGER,                     -- Optional reference, no FK constraint
    
    -- Content Performance
    post_id VARCHAR(255),
    content_type VARCHAR(50),                -- 'post', 'story', 'reel', 'video', 'ad'
    content_category VARCHAR(100),           -- 'product', 'lifestyle', 'tutorial', 'promotion'
    
    -- Core Metrics (start with 1 for multiplier calculations)
    views INTEGER DEFAULT 1,
    likes INTEGER DEFAULT 1,
    comments INTEGER DEFAULT 1,
    shares INTEGER DEFAULT 1,
    saves INTEGER DEFAULT 1,
    clicks INTEGER DEFAULT 1,
    
    -- Financial Metrics
    ad_spend DECIMAL(10,2) DEFAULT 0.00,
    revenue_generated DECIMAL(10,2) DEFAULT 0.00,
    cost_per_click DECIMAL(8,2) DEFAULT 0.00,
    cost_per_impression DECIMAL(8,4) DEFAULT 0.00,
    
    -- Calculated ROI
    roi_percentage DECIMAL(8,2) DEFAULT 0.00,
    roas_ratio DECIMAL(8,2) DEFAULT 0.00,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    posted_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_timestamp TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_roi_metrics_user_id ON roi_metrics(user_id);
CREATE INDEX idx_roi_metrics_platform ON roi_metrics(platform);
CREATE INDEX idx_roi_metrics_campaign_id ON roi_metrics(campaign_id);
CREATE INDEX idx_roi_metrics_timestamp ON roi_metrics(update_timestamp);
CREATE INDEX idx_roi_metrics_content_type ON roi_metrics(content_type);
```

### **2. Platform-Specific Metrics Table (Optimized)**
```sql
CREATE TABLE platform_metrics (
    id SERIAL PRIMARY KEY,
    roi_metric_id INTEGER,                    -- No FK constraint for flexibility
    platform VARCHAR(50) NOT NULL,
    update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Store platform-specific metrics as JSONB (no more NULL fields!)
    metrics JSONB NOT NULL DEFAULT '{}',
    
    -- Common calculated fields
    engagement_rate DECIMAL(5,2) DEFAULT 1.00,
    virality_score DECIMAL(5,2) DEFAULT 1.00
);

-- Example JSONB structure for different platforms:
-- YouTube: {"watch_time_minutes": 120, "subscribers_gained": 15, "average_view_duration": 2.5, "video_quality_score": 8.5}
-- Instagram: {"reach": 5000, "impressions": 8000, "profile_visits": 120, "story_views": 3000, "saved_count": 45}
-- Facebook: {"page_likes": 25, "post_reach": 3500, "page_views": 180, "link_clicks": 89}
-- TikTok: {"video_views": 12000, "followers_gained": 67, "play_count": 15000, "completion_rate": 0.75}
```

## **Mock Data Generation Strategy**

### **Core Philosophy**
Since we're not marketing experts and our content generates 0 views, we need to create realistic mock data that demonstrates the platform's analytical capabilities while maintaining believability.

### **How Data Actually Grows (NOT Fixed Values!)**
```javascript
// Example: A YouTube video over 4 hours
let videoMetrics = {
    views: 1,        // Start with 1
    likes: 1,
    comments: 1,
    shares: 1
};

// Hour 1: Apply random multiplier (1.00x to 2.50x)
videoMetrics = generateUpdate(videoMetrics);
// Result: views: 2, likes: 1, comments: 2, shares: 3
// (Random multipliers: 2.1x, 1.0x, 1.8x, 2.7x)

// Hour 2: Apply NEW random multiplier to CURRENT values
videoMetrics = generateUpdate(videoMetrics);
// Result: views: 4, likes: 2, comments: 3, shares: 6
// (Random multipliers: 2.0x, 1.8x, 1.5x, 2.0x)

// Hour 3: Apply NEW random multiplier to CURRENT values
videoMetrics = generateUpdate(videoMetrics);
// Result: views: 8, likes: 3, comments: 5, shares: 12
// (Random multipliers: 2.0x, 1.5x, 1.7x, 2.0x)

// This creates REAL exponential growth, not fake fixed data!
```

### **Growth Pattern: Multiplier-Based (Not Linear)**
```javascript
const hourlyGrowth = {
    views: randomInRange(1.00, 2.50),      // 0% to 150% growth (more realistic)
    likes: randomInRange(1.00, 1.80),      // 0% to 80% growth (more realistic)
    comments: randomInRange(1.00, 1.60),   // 0% to 60% growth (more realistic)
    shares: randomInRange(1.00, 2.20),     // 0% to 120% growth (more realistic)
    clicks: randomInRange(1.00, 1.90)      // 0% to 90% growth (more realistic)
};
```

### **Cost Calculation Models**
```javascript
const platformCostModels = {
    facebook: {
        cpc_range: { min: 0.50, max: 2.50 },
        cpm_range: { min: 5.00, max: 25.00 },
        engagement_multiplier: 1.2
    },
    instagram: {
        cpc_range: { min: 0.80, max: 3.00 },
        cpm_range: { min: 6.00, max: 30.00 },
        engagement_multiplier: 1.5
    },
    youtube: {
        cpc_range: { min: 0.30, max: 1.50 },
        cpm_range: { min: 3.00, max: 15.00 },
        engagement_multiplier: 1.0
    },
    
};

// MISSING: Revenue calculation logic
function calculateRevenue(metrics, platform) {
    // Conversion rate logic based on platform and engagement
    const baseConversionRate = 0.02; // 2% base conversion
    const platformMultiplier = platformCostModels[platform]?.engagement_multiplier || 1.0;
    
    // Higher engagement = higher conversion rate
    const engagementRate = (metrics.likes + metrics.comments + metrics.shares) / Math.max(metrics.views, 1);
    const adjustedConversionRate = baseConversionRate * platformMultiplier * (1 + engagementRate);
    
    // Average order value varies by platform
    const avgOrderValue = {
        facebook: 45,
        instagram: 65,
        youtube: 80
    }[platform] || 50;
    
    const conversions = Math.round(metrics.clicks * adjustedConversionRate);
    const revenue = Math.round(conversions * avgOrderValue);
    
    return { conversions, revenue };
}
```

### **Data Generation Logic**
```javascript
// Initial values should be 1 (not 0) so multipliers work properly
const initialValues = {
    views: 1,
    likes: 1,
    comments: 1,
    shares: 1,
    clicks: 1
};

// Apply REALISTIC multiplier growth with decay and bounds
function generateRealisticUpdate(currentMetrics, hoursElapsed = 1) {
    // Apply diminishing returns and maximum bounds
    const decayFactor = Math.max(0.1, 1 - (hoursElapsed * 0.02)); // Decay over time
    const maxGrowth = Math.min(2.5, 1 + (1000 / Math.max(currentMetrics.views, 1))); // Diminishing returns
    
    const growthMultiplier = {
        views: randomInRange(1.00, maxGrowth * decayFactor),
        likes: randomInRange(1.00, 1.80 * decayFactor),
        comments: randomInRange(1.00, 1.60 * decayFactor),
        shares: randomInRange(1.00, 2.20 * decayFactor),
        clicks: randomInRange(1.00, 1.90 * decayFactor)
    };
    
    return {
        views: Math.min(Math.round(currentMetrics.views * growthMultiplier.views), 1000000), // Hard limit
        likes: Math.min(Math.round(currentMetrics.likes * growthMultiplier.likes), 500000),
        comments: Math.min(Math.round(currentMetrics.comments * growthMultiplier.comments), 100000),
        shares: Math.min(Math.round(currentMetrics.shares * growthMultiplier.shares), 200000),
        clicks: Math.min(Math.round(currentMetrics.clicks * growthMultiplier.clicks), 300000)
    };
}
```

### **Platform-Specific Growth Patterns**
```javascript
// YouTube Metrics Growth
const youtubeGrowth = {
    watch_time_minutes: randomInRange(1.00, 2.20),      // 0% to 120% growth (more realistic)
    subscribers_gained: randomInRange(1.00, 1.80),      // 0% to 80% growth (more realistic)
    average_view_duration: randomInRange(1.00, 1.25),   // 0% to 25% growth (more realistic)
    video_quality_score: randomInRange(1.00, 1.15)      // 0% to 15% growth (more realistic)
};

// Instagram Metrics Growth
const instagramGrowth = {
    reach: randomInRange(1.00, 2.80),                   // 0% to 180% growth (more realistic)
    impressions: randomInRange(1.00, 2.50),             // 0% to 150% growth (more realistic)
    profile_visits: randomInRange(1.00, 1.90),          // 0% to 90% growth (more realistic)
    story_views: randomInRange(1.00, 2.20),             // 0% to 120% growth (more realistic)
    saved_count: randomInRange(1.00, 1.80)              // 0% to 80% growth (more realistic)
};

// Facebook Metrics Growth
const facebookGrowth = {
    page_likes: randomInRange(1.00, 1.60),              // 0% to 60% growth (more realistic)
    post_reach: randomInRange(1.00, 2.40),              // 0% to 140% growth (more realistic)
    page_views: randomInRange(1.00, 2.00),              // 0% to 100% growth (more realistic)
    link_clicks: randomInRange(1.00, 2.20)              // 0% to 120% growth (more realistic)
};

// TikTok removed from supported platforms

// Cross-Platform Calculated Metrics
function calculateCrossPlatformMetrics(metrics) {
    return {
        engagement_rate: Math.round((metrics.likes + metrics.comments + metrics.shares) / metrics.views * 100),
        virality_score: Math.round(metrics.shares / (metrics.views * 0.01)) // Shares per 100 views
    };
}
```

### **How Growth Works - Examples**

#### **Example 1: YouTube Video Performance**
```javascript
// Starting values (Hour 0)
let youtubeMetrics = {
    watch_time_minutes: 1,
    subscribers_gained: 1,
    average_view_duration: 1.00,
    video_quality_score: 1.00
};

// Hour 1: Apply growth multipliers
youtubeMetrics = {
    watch_time_minutes: Math.round(1 * 2.50),           // 1 → 3 minutes
    subscribers_gained: Math.round(1 * 1.80),           // 1 → 2 subscribers
    average_view_duration: Math.round(1.00 * 1.15),     // 1.00 → 1.15 minutes
    video_quality_score: Math.round(1.00 * 1.10)        // 1.00 → 1.10
};

// Hour 2: Continue growing
youtubeMetrics = {
    watch_time_minutes: Math.round(3 * 1.90),           // 3 → 6 minutes
    subscribers_gained: Math.round(2 * 2.20),           // 2 → 4 subscribers
    average_view_duration: Math.round(1.15 * 1.08),     // 1.15 → 1.24 minutes
    video_quality_score: Math.round(1.10 * 1.05)        // 1.10 → 1.16
};
```

#### **Example 2: Instagram Post Going Viral**
```javascript
// Starting values
let instagramMetrics = {
    reach: 1,
    impressions: 1,
    profile_visits: 1,
    story_views: 1,
    saved_count: 1
};

// Hour 1: Moderate growth
instagramMetrics = {
    reach: Math.round(1 * 2.00),                        // 1 → 2
    impressions: Math.round(1 * 1.80),                  // 1 → 2
    profile_visits: Math.round(1 * 1.50),               // 1 → 2
    story_views: Math.round(1 * 1.70),                  // 1 → 2
    saved_count: Math.round(1 * 1.30)                   // 1 → 1
};

// Hour 2: Viral explosion!
instagramMetrics = {
    reach: Math.round(2 * 5.50),                        // 2 → 11
    impressions: Math.round(2 * 4.80),                  // 2 → 10
    profile_visits: Math.round(2 * 2.90),               // 2 → 6
    story_views: Math.round(2 * 3.20),                  // 2 → 6
    saved_count: Math.round(2 * 2.40)                   // 2 → 5
};
```

#### **Growth Logic Summary**
- **All metrics start at 1** (not 0) so multipliers work properly
- **Each hour applies new random multipliers** to current values
- **Results are rounded to integers** using `Math.round()`
- **Growth is exponential** - each hour builds on the previous hour's results
- **Different platforms have different growth ranges** based on their characteristics
- **Viral content can show explosive growth** (5x-7x multipliers)
- **Steady content shows moderate growth** (1.2x-2x multipliers)

### **Database Insertion Process (Hourly Updates - Realistic)**

#### **1. Main Data Insertion Function (Hourly Intervals)**
```javascript
async function insertROIData() {
    try {
        // Get all active ROI metrics that need updates
        const activeMetrics = await getActiveROIMetrics();
        
        for (const metric of activeMetrics) {
            // Generate new data
            const newMetrics = generateUpdate(metric);
            const newPlatformMetrics = generatePlatformMetrics(metric.platform, newMetrics);
            
            // Insert into roi_metrics table
            await insertROIMetrics({
                user_id: metric.user_id,
                platform: metric.platform,
                campaign_id: metric.campaign_id,
                post_id: metric.post_id,
                content_type: metric.content_type,
                content_category: metric.content_category,
                ...newMetrics,
                update_timestamp: new Date()
            });
            
            // Insert into platform_metrics table
            await insertPlatformMetrics({
                roi_metric_id: metric.id,
                platform: metric.platform,
                ...newPlatformMetrics,
                update_timestamp: new Date()
            });
        }
        
        console.log(`Updated ${activeMetrics.length} ROI metrics at ${new Date()}`);
    } catch (error) {
        console.error('Error updating ROI data:', error);
    }
}
```

#### **2. Database Insert Functions**
```javascript
// Insert into roi_metrics table
async function insertROIMetrics(data) {
    const query = `
        INSERT INTO roi_metrics (
            user_id, platform, campaign_id, post_id, content_type, content_category,
            views, likes, comments, shares, saves, clicks,
            ad_spend, revenue_generated, cost_per_click, cost_per_impression,
            roi_percentage, roas_ratio, update_timestamp
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
        RETURNING id
    `;
    
    const values = [
        data.user_id, data.platform, data.campaign_id, data.post_id,
        data.content_type, data.content_category,
        data.views, data.likes, data.comments, data.shares, data.saves, data.clicks,
        data.ad_spend, data.revenue_generated, data.cost_per_click, data.cost_per_impression,
        data.roi_percentage, data.roas_ratio, data.update_timestamp
    ];
    
    const result = await db.query(query, values);
    return result.rows[0].id;
}

// Insert into platform_metrics table
async function insertPlatformMetrics(data) {
    const query = `
        INSERT INTO platform_metrics (
            roi_metric_id, platform, update_timestamp,
            watch_time_minutes, subscribers_gained, average_view_duration, video_quality_score,
            reach, impressions, profile_visits, story_views, saved_count,
            page_likes, post_reach, page_views, link_clicks,
            video_views, followers_gained, play_count, completion_rate,
            engagement_rate, virality_score
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)
    `;
    
    const values = [
        data.roi_metric_id, data.platform, data.update_timestamp,
        data.watch_time_minutes || 0, data.subscribers_gained || 0, 
        data.average_view_duration || 0, data.video_quality_score || 0,
        data.reach || 0, data.impressions || 0, data.profile_visits || 0,
        data.story_views || 0, data.saved_count || 0,
        data.page_likes || 0, data.post_reach || 0, data.page_views || 0,
        data.link_clicks || 0, data.video_views || 0, data.followers_gained || 0,
        data.play_count || 0, data.completion_rate || 0,
        data.engagement_rate || 0, data.virality_score || 0
    ];
    
    await db.query(query, values);
}
```

#### **3. Scheduler Setup (Node.js with node-cron)**
```javascript
import cron from 'node-cron';

// Run every 10 minutes for more reliable and frequent data updates
cron.schedule('*/10 * * * *', async () => {
    console.log('Starting 10-minute ROI data update...');
    await insertROIData();
});

// Alternative: Run every 5 minutes for real-time feel
cron.schedule('*/5 * * * *', async () => {
    console.log('Starting 5-minute ROI data update...');
    await insertROIData();
});

// Alternative: Run every 15 minutes for balanced performance
cron.schedule('*/15 * * * *', async () => {
    console.log('Starting 15-minute ROI data update...');
    await insertROIData();
});
```

#### **4. Python Alternative (with APScheduler)**
```python
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import asyncio

scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', hours=1)
def update_roi_data_hourly():
    print(f"Starting hourly ROI update at {datetime.now()}")
    asyncio.run(insert_roi_data())

@scheduler.scheduled_job('interval', hours=2)
def update_roi_data_2hourly():
    print(f"Starting 2-hour ROI update at {datetime.now()}")
    asyncio.run(insert_roi_data())

@scheduler.scheduled_job('interval', hours=4)
def update_roi_data_4hourly():
    print(f"Starting 4-hour ROI update at {datetime.now()}")
    asyncio.run(insert_roi_data())

if __name__ == '__main__':
    scheduler.start()
```

#### **5. Database Connection and Helper Functions**
```javascript
// Database connection (using your existing setup)
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

// Get active ROI metrics that need updates
async function getActiveROIMetrics() {
    const { data, error } = await supabase
        .from('roi_metrics')
        .select('*')
        .gte('update_timestamp', new Date(Date.now() - 10 * 60 * 1000)) // Last 10 minutes
        .order('update_timestamp', { ascending: false });
    
    if (error) throw error;
    return data || [];
}

// Generate platform-specific metrics using JSONB structure
function generatePlatformMetrics(platform, baseMetrics) {
    const commonMetrics = {
        engagement_rate: Math.round((baseMetrics.likes + baseMetrics.comments + baseMetrics.shares) / Math.max(baseMetrics.views, 1) * 100),
        virality_score: Math.round(baseMetrics.shares / Math.max(baseMetrics.views * 0.01, 1))
    };
    
    switch (platform) {
        case 'youtube':
            return {
                ...commonMetrics,
                metrics: {
                    watch_time_minutes: Math.round(baseMetrics.views * randomInRange(1.00, 4.00)),
                    subscribers_gained: Math.round(baseMetrics.views * 0.1 * randomInRange(1.00, 2.50)),
                    average_view_duration: Math.round(baseMetrics.views * 0.5 * randomInRange(1.00, 1.30)),
                    video_quality_score: randomInRange(1.00, 10.00) // 0-10 scale
                }
            };
        case 'instagram':
            return {
                ...commonMetrics,
                metrics: {
                    reach: Math.round(baseMetrics.views * randomInRange(1.00, 6.00)),
                    impressions: Math.round(baseMetrics.views * randomInRange(1.00, 5.00)),
                    profile_visits: Math.round(baseMetrics.views * 0.2 * randomInRange(1.00, 3.00)),
                    story_views: Math.round(baseMetrics.views * randomInRange(1.00, 4.00)),
                    saved_count: Math.round(baseMetrics.views * 0.1 * randomInRange(1.00, 2.50))
                }
            };
        case 'facebook':
            return {
                ...commonMetrics,
                metrics: {
                    page_likes: Math.round(baseMetrics.views * 0.1 * randomInRange(1.00, 2.00)),
                    post_reach: Math.round(baseMetrics.views * randomInRange(1.00, 3.00)),
                    page_views: Math.round(baseMetrics.views * randomInRange(1.00, 2.50)),
                    link_clicks: Math.round(baseMetrics.views * 0.3 * randomInRange(1.00, 2.50))
                }
            };
        // tiktok removed
        default:
            return { ...commonMetrics, metrics: {} };
    }
}

// MISSING: Financial calculation function
function calculateFinancialMetrics(platform, metrics) {
    const platformCosts = platformCostModels[platform];
    if (!platformCosts) return {};
    
    // Calculate costs based on engagement
    const cpc = randomInRange(platformCosts.cpc_range.min, platformCosts.cpc_range.max);
    const cpm = randomInRange(platformCosts.cpm_range.min, platformCosts.cpm_range.max);
    
    // Calculate ad spend based on clicks and impressions
    const adSpend = (metrics.clicks * cpc) + (metrics.views * cpm / 1000);
    
    return {
        ad_spend: Math.round(adSpend * 100) / 100, // Round to 2 decimal places
        cost_per_click: cpc,
        cost_per_impression: cpm / 1000,
        roi_percentage: 0, // Will be calculated after revenue
        roas_ratio: 0      // Will be calculated after revenue
    };
}
```

#### **6. Complete Hourly Update Flow**
```javascript
// Main execution flow
async function executeROIUpdate() {
    console.log(`=== Starting Hourly ROI Update at ${new Date()} ===`);
    
    try {
        // 1. Get active metrics
        const activeMetrics = await getActiveROIMetrics();
        console.log(`Found ${activeMetrics.length} active metrics to update`);
        
        // 2. Process each metric
        for (const metric of activeMetrics) {
            // Generate new data using REALISTIC multipliers with decay
            const newMetrics = generateRealisticUpdate(metric, hoursElapsed);
            const newPlatformMetrics = generatePlatformMetrics(metric.platform, newMetrics);
            
            // Calculate financial metrics based on new engagement data
            const financialMetrics = calculateFinancialMetrics(metric.platform, newMetrics);
            
            // Calculate revenue using the missing revenue logic
            const revenueData = calculateRevenue(newMetrics, metric.platform);
            financialMetrics.revenue_generated = revenueData.revenue;
            financialMetrics.conversions = revenueData.conversions;
            
            // Insert into database with NEW calculated values
            const newRoiId = await insertROIMetrics({
                ...metric,
                ...newMetrics,                    // ← NEW metrics with multipliers applied
                ...financialMetrics,              // ← NEW financial calculations
                update_timestamp: new Date()
            });
            
            await insertPlatformMetrics({
                roi_metric_id: newRoiId,
                platform: metric.platform,
                ...newPlatformMetrics,            // ← NEW platform metrics with multipliers
                update_timestamp: new Date()
            });
            
            console.log(`Updated metric ID ${metric.id} for ${metric.platform}`);
        }
        
        console.log(`=== Hourly Update Complete: ${activeMetrics.length} metrics updated ===`);
    } catch (error) {
        console.error('ROI update failed:', error);
        // Send alert/notification
    }
}

// How multipliers work in practice:
function demonstrateMultiplierFlow() {
    // Starting point (Hour 0)
    let currentMetrics = {
        views: 1,
        likes: 1,
        comments: 1,
        shares: 1,
        clicks: 1
    };
    
    console.log('Hour 0:', currentMetrics);
    
    // Hour 1: Apply first multiplier
    currentMetrics = generateUpdate(currentMetrics);
    console.log('Hour 1:', currentMetrics);
    
    // Hour 2: Apply second multiplier to NEW values
    currentMetrics = generateUpdate(currentMetrics);
    console.log('Hour 2:', currentMetrics);
    
    // Hour 3: Apply third multiplier to NEW values
    currentMetrics = generateUpdate(currentMetrics);
    console.log('Hour 3:', currentMetrics);
    
    // Each hour builds on the previous hour's results!
    // This creates exponential growth, not fixed data
}
```

## **ROI Dashboard READ Operations - Implementation Plan**

### **Core ROI Calculation Functions**

#### **1. Total ROI Overview (Main Dashboard)**
```typescript
// Main ROI calculation function
async function calculateTotalROI(userId: string, timeRange: TimeRange) {
    const metrics = await fetchROIMetrics(userId, timeRange);
    
    return {
        totalRevenue: metrics.reduce((sum, m) => sum + m.revenue_generated, 0),
        totalSpend: metrics.reduce((sum, m) => sum + m.ad_spend, 0),
        totalProfit: metrics.reduce((sum, m) => sum + (m.revenue_generated - m.ad_spend), 0),
        overallROI: calculateROIPercentage(metrics),
        totalImpressions: metrics.reduce((sum, m) => sum + m.views, 0),
        totalEngagement: metrics.reduce((sum, m) => sum + m.likes + m.comments + m.shares, 0),
        totalPosts: metrics.length
    };
}

// ROI Percentage Formula
function calculateROIPercentage(metrics: ROIMetric[]) {
    const totalRevenue = metrics.reduce((sum, m) => sum + m.revenue_generated, 0);
    const totalSpend = metrics.reduce((sum, m) => sum + m.ad_spend, 0);
    
    if (totalSpend === 0) return 0;
    return ((totalRevenue - totalSpend) / totalSpend) * 100;
}
```

#### **2. Revenue Overview Tab**
```typescript
// Revenue by Source (Platform breakdown)
async function getRevenueBySource(userId: string, timeRange: TimeRange) {
    const query = `
        SELECT 
            platform,
            SUM(revenue_generated) as total_revenue,
            COUNT(*) as post_count,
            AVG(revenue_generated) as avg_revenue_per_post,
            SUM(revenue_generated) / SUM(ad_spend) as revenue_multiplier
        FROM roi_metrics 
        WHERE user_id = $1 
        AND update_timestamp BETWEEN $2 AND $3
        GROUP BY platform
        ORDER BY total_revenue DESC
    `;
    
    const result = await db.query(query, [userId, timeRange.start, timeRange.end]);
    return result.rows;
}

// Revenue Trends (Time series)
async function getRevenueTrends(userId: string, timeRange: TimeRange, interval: 'hour' | 'day' | 'week') {
    const query = `
        SELECT 
            DATE_TRUNC($4, update_timestamp) as time_period,
            SUM(revenue_generated) as revenue,
            COUNT(*) as posts,
            AVG(roi_percentage) as avg_roi
        FROM roi_metrics 
        WHERE user_id = $1 
        AND update_timestamp BETWEEN $2 AND $3
        GROUP BY DATE_TRUNC($4, update_timestamp)
        ORDER BY time_period
    `;
    
    const result = await db.query(query, [userId, timeRange.start, timeRange.end, interval]);
    return result.rows;
}
```

#### **3. Cost Analysis Tab**
```typescript
// Cost Breakdown by Platform
async function getCostBreakdown(userId: string, timeRange: TimeRange) {
    const query = `
        SELECT 
            platform,
            SUM(ad_spend) as total_spend,
            AVG(cost_per_click) as avg_cpc,
            AVG(cost_per_impression) as avg_cpm,
            COUNT(*) as campaigns,
            SUM(ad_spend) / SUM(clicks) as effective_cpc
        FROM roi_metrics 
        WHERE user_id = $1 
        AND update_timestamp BETWEEN $2 AND $3
        GROUP BY platform
        ORDER BY total_spend DESC
    `;
    
    return await db.query(query, [userId, timeRange.start, timeRange.end]);
}

// Monthly Spend Trends
async function getMonthlySpendTrends(userId: string, year: number) {
    const query = `
        SELECT 
            EXTRACT(MONTH FROM update_timestamp) as month,
            platform,
            SUM(ad_spend) as spend,
            SUM(revenue_generated) as revenue,
            AVG(roi_percentage) as avg_roi
        FROM roi_metrics 
        WHERE user_id = $1 
        AND EXTRACT(YEAR FROM update_timestamp) = $2
        GROUP BY EXTRACT(MONTH FROM update_timestamp), platform
        ORDER BY month, platform
    `;
    
    return await db.query(query, [userId, year]);
}
```

#### **4. Profitability Metrics Tab**
```typescript
// Customer Lifetime Value (CLV)
async function calculateCLV(userId: string, timeRange: TimeRange) {
    const query = `
        SELECT 
            AVG(revenue_generated) as avg_revenue_per_customer,
            COUNT(DISTINCT post_id) as unique_customers,
            SUM(revenue_generated) / COUNT(DISTINCT post_id) as clv,
            SUM(revenue_generated) / SUM(ad_spend) as revenue_multiplier
        FROM roi_metrics 
        WHERE user_id = $1 
        AND update_timestamp BETWEEN $2 AND $3
        AND revenue_generated > 0
    `;
    
    return await db.query(query, [userId, timeRange.start, timeRange.end]);
}

// Customer Acquisition Cost (CAC)
async function calculateCAC(userId: string, timeRange: TimeRange) {
    const query = `
        SELECT 
            SUM(ad_spend) / COUNT(DISTINCT post_id) as cac,
            AVG(cost_per_click) as avg_cpc,
            AVG(cost_per_impression) as avg_cpm
        FROM roi_metrics 
        WHERE user_id = $1 
        AND update_timestamp BETWEEN $2 AND $3
        AND ad_spend > 0
    `;
    
    return await db.query(query, [userId, timeRange.start, timeRange.end]);
}

// Payback Period
function calculatePaybackPeriod(cac: number, clv: number) {
    if (clv === 0) return 0;
    return cac / clv; // In months typically
}
```

#### **5. ROI Trends Tab**
```typescript
// ROI Trends Over Time
async function getROITrends(userId: string, timeRange: TimeRange) {
    const query = `
        SELECT 
            DATE_TRUNC('day', update_timestamp) as date,
            AVG(roi_percentage) as avg_roi,
            COUNT(*) as data_points,
            SUM(revenue_generated) as daily_revenue,
            SUM(ad_spend) as daily_spend
        FROM roi_metrics 
        WHERE user_id = $1 
        AND update_timestamp BETWEEN $2 AND $3
        GROUP BY DATE_TRUNC('day', update_timestamp)
        ORDER BY date
    `;
    
    return await db.query(query, [userId, timeRange.start, timeRange.end]);
}

// Industry Benchmark Comparison
function compareToBenchmark(actualROI: number, industryBenchmark: number = 400) {
    return {
        actual: actualROI,
        benchmark: industryBenchmark,
        difference: actualROI - industryBenchmark,
        percentage: ((actualROI - industryBenchmark) / industryBenchmark) * 100,
        status: actualROI >= industryBenchmark ? 'above' : 'below'
    };
}
```

#### **6. Channel Performance Tab**
```typescript
// Channel Performance Analysis
async function getChannelPerformance(userId: string, timeRange: TimeRange) {
    const query = `
        SELECT 
            platform,
            SUM(revenue_generated) as revenue,
            SUM(ad_spend) as spend,
            AVG(roi_percentage) as avg_roi,
            AVG(roas_ratio) as avg_roas,
            SUM(views) as impressions,
            SUM(likes + comments + shares) as engagement,
            COUNT(*) as posts,
            SUM(clicks) as total_clicks
        FROM roi_metrics 
        WHERE user_id = $1 
        AND update_timestamp BETWEEN $2 AND $3
        GROUP BY platform
        ORDER BY avg_roi DESC
    `;
    
    const result = await db.query(query, [userId, timeRange.start, timeRange.end]);
    
    // Calculate additional metrics
    return result.rows.map(row => ({
        ...row,
        profit: row.revenue - row.spend,
        engagement_rate: row.impressions > 0 ? (row.engagement / row.impressions) * 100 : 0,
        click_through_rate: row.impressions > 0 ? (row.total_clicks / row.impressions) * 100 : 0,
        efficiency_score: row.avg_roi * (row.engagement / Math.max(row.impressions, 1))
    }));
}
```

### **Data Fetching Strategy & Performance**

#### **1. Time Range Handling**
```typescript
type TimeRange = {
    start: Date;
    end: Date;
    interval: 'hour' | 'day' | 'week' | 'month';
};

function getTimeRange(period: '7d' | '30d' | '90d' | '1y'): TimeRange {
    const end = new Date();
    const start = new Date();
    
    switch (period) {
        case '7d':
            start.setDate(end.getDate() - 7);
            break;
        case '30d':
            start.setDate(end.getDate() - 30);
            break;
        case '90d':
            start.setDate(end.getDate() - 90);
            break;
        case '1y':
            start.setFullYear(end.getFullYear() - 1);
            break;
    }
    
    return { start, end, interval: period === '7d' ? 'hour' : 'day' };
}
```

#### **2. Caching Strategy for Expensive Calculations**
```typescript
// Redis cache for expensive calculations with proper invalidation
async function getCachedROIData(userId: string, timeRange: TimeRange) {
    const cacheKey = `roi:${userId}:${timeRange.start.getTime()}:${timeRange.end.getTime()}`;
    
    // Try cache first
    const cached = await redis.get(cacheKey);
    if (cached) return JSON.parse(cached);
    
    // Calculate fresh data
    const data = await calculateTotalROI(userId, timeRange);
    
    // Cache for 45 minutes (since data updates every hour, not every 10 minutes)
    await redis.setex(cacheKey, 2700, JSON.stringify(data));
    
    return data;
}

// Cache invalidation when data updates
async function invalidateROICache(userId: string) {
    const pattern = `roi:${userId}:*`;
    const keys = await redis.keys(pattern);
    if (keys.length > 0) {
        await redis.del(...keys);
        console.log(`Invalidated ${keys.length} cache keys for user ${userId}`);
    }
}
```

#### **3. Database Query Optimization**
```typescript
// Batch fetch multiple metrics in single query
async function fetchAllROIMetrics(userId: string, timeRange: TimeRange) {
    const query = `
        SELECT 
            rm.*,
            pm.watch_time_minutes, pm.subscribers_gained, pm.reach, pm.impressions,
            pm.profile_visits, pm.story_views, pm.saved_count, pm.page_likes,
            pm.post_reach, pm.page_views, pm.link_clicks, pm.video_views,
            pm.followers_gained, pm.play_count, pm.completion_rate,
            pm.engagement_rate, pm.virality_score
        FROM roi_metrics rm
        LEFT JOIN platform_metrics pm ON rm.id = pm.roi_metric_id
        WHERE rm.user_id = $1 
        AND rm.update_timestamp BETWEEN $2 AND $3
        ORDER BY rm.update_timestamp DESC
    `;
    
    return await db.query(query, [userId, timeRange.start, timeRange.end]);
}
```

## **Implementation Phases**

### **Phase 1: Database Setup (Week 1)**
- [ ] Create `campaign_with_user_id` table with proper user_id
- [ ] Create `roi_metrics` table with all required fields
- [ ] Create `platform_metrics` table with platform-specific metrics
- [ ] Set up foreign key relationships between tables
- [ ] Create all necessary indexes for performance
- [ ] Test table structure and relationships

### **Phase 2: Data Generation Engine (Week 2)**
- [ ] Build mock data generator service with hourly update intervals
- [ ] Implement realistic multiplier-based growth algorithm with decay and bounds
- [ ] Create cost calculation engine with platform-specific models
- [ ] Set up hourly update scheduler (Node.js/Python)
- [ ] Generate initial dataset (1-2 months of historical data)
- [ ] Implement data validation and error handling
- [ ] Add proper revenue calculation logic

### **Phase 3: ROI Dashboard Integration (Week 3)**
- [ ] Implement all ROI calculation functions (6 main tabs)
- [ ] Connect ROI dashboard UI components to real database
- [ ] Implement time range filtering (7d, 30d, 90d, 1y)
- [ ] Add caching layer for expensive calculations
- [ ] Test data flow and ROI calculations accuracy
- [ ] Performance testing with large datasets

### **Phase 4: Advanced Analytics & Polish (Week 4)**
- [ ] Add more sophisticated growth patterns and seasonal variations
- [ ] Implement content type performance variations
- [ ] Create data export functionality (CSV, PDF reports)
- [ ] Add real-time data updates and notifications
- [ ] Final testing, documentation, and performance optimization

## **Database Migration & Setup**

### **Step-by-Step Database Creation**
```sql
-- 1. Create campaign_with_user_id table
CREATE TABLE campaign_with_user_id (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    date DATE,
    impressions INTEGER,
    clicks INTEGER,
    ctr DOUBLE PRECISION,
    cpc DOUBLE PRECISION,
    spend DOUBLE PRECISION,
    budget DOUBLE PRECISION,
    conversions INTEGER,
    net_profit DOUBLE PRECISION,
    ongoing VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create roi_metrics table
CREATE TABLE roi_metrics (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    campaign_id INTEGER REFERENCES campaign_with_user_id(id),
    post_id VARCHAR(255),
    content_type VARCHAR(50),
    content_category VARCHAR(100),
    views INTEGER DEFAULT 1,
    likes INTEGER DEFAULT 1,
    comments INTEGER DEFAULT 1,
    shares INTEGER DEFAULT 1,
    saves INTEGER DEFAULT 1,
    clicks INTEGER DEFAULT 1,
    ad_spend DECIMAL(10,2) DEFAULT 0.00,
    revenue_generated DECIMAL(10,2) DEFAULT 0.00,
    cost_per_click DECIMAL(8,2) DEFAULT 0.00,
    cost_per_impression DECIMAL(8,4) DEFAULT 0.00,
    roi_percentage DECIMAL(8,2) DEFAULT 0.00,
    roas_ratio DECIMAL(8,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    posted_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create platform_metrics table (Optimized with JSONB)
CREATE TABLE platform_metrics (
    id SERIAL PRIMARY KEY,
    roi_metric_id INTEGER,                    -- No FK constraint for flexibility
    user_id VARCHAR(255) NOT NULL,            -- Added for user isolation
    platform VARCHAR(50) NOT NULL,
    update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metrics JSONB NOT NULL DEFAULT '{}',      -- Store platform-specific metrics as JSON
    engagement_rate DECIMAL(5,2) DEFAULT 1.00,
    virality_score DECIMAL(5,2) DEFAULT 1.00
);

-- 4. Create all necessary indexes
CREATE INDEX idx_campaign_with_user_id_user_id ON campaign_with_user_id(user_id);
CREATE INDEX idx_campaign_with_user_id_date ON campaign_with_user_id(date);
CREATE INDEX idx_roi_metrics_user_id ON roi_metrics(user_id);
CREATE INDEX idx_roi_metrics_platform ON roi_metrics(platform);
CREATE INDEX idx_roi_metrics_campaign_id ON roi_metrics(campaign_id);
CREATE INDEX idx_roi_metrics_timestamp ON roi_metrics(update_timestamp);
CREATE INDEX idx_roi_metrics_content_type ON roi_metrics(content_type);
CREATE INDEX idx_platform_metrics_roi_id ON platform_metrics(roi_metric_id);
CREATE INDEX idx_platform_metrics_platform ON platform_metrics(platform);
CREATE INDEX idx_platform_metrics_timestamp ON platform_metrics(update_timestamp);

-- 5. Add foreign key constraints (only where needed)
-- Note: campaign_id is optional, no FK constraint for flexibility

-- 6. Add proper user isolation constraints
ALTER TABLE roi_metrics 
ADD CONSTRAINT fk_roi_metrics_user 
FOREIGN KEY (user_id) REFERENCES users(clerk_id) ON DELETE CASCADE;

ALTER TABLE campaign_with_user_id 
ADD CONSTRAINT fk_campaign_user 
FOREIGN KEY (user_id) REFERENCES users(clerk_id) ON DELETE CASCADE;

-- 7. Add user isolation to platform_metrics
ALTER TABLE platform_metrics 
ADD COLUMN user_id VARCHAR(255) NOT NULL,
ADD CONSTRAINT fk_platform_metrics_user 
FOREIGN KEY (user_id) REFERENCES users(clerk_id) ON DELETE CASCADE;

-- 6. Create composite indexes for common query patterns
CREATE INDEX idx_roi_metrics_user_platform_time ON roi_metrics(user_id, platform, update_timestamp);
CREATE INDEX idx_roi_metrics_user_time ON roi_metrics(user_id, update_timestamp);

-- 7. Add JSONB index for platform_metrics (critical for performance!)
CREATE INDEX idx_platform_metrics_jsonb ON platform_metrics USING GIN (metrics);
CREATE INDEX idx_platform_metrics_user_platform ON platform_metrics(user_id, platform);
CREATE INDEX idx_platform_metrics_timestamp ON platform_metrics(update_timestamp);
```

### **Data Population Strategy**
```sql
-- Insert sample campaign data for testing
INSERT INTO campaign_with_user_id (user_id, name, date, impressions, clicks, ctr, cpc, spend, budget, conversions, net_profit, ongoing)
VALUES 
('user_123', 'Summer Product Launch', '2024-01-15', 10000, 500, 5.0, 1.20, 600.00, 1000.00, 25, 1250.00, 'active'),
('user_123', 'Brand Awareness Campaign', '2024-01-20', 15000, 300, 2.0, 2.50, 750.00, 1500.00, 15, 450.00, 'active'),
('user_456', 'Holiday Promotion', '2024-01-10', 8000, 400, 5.0, 1.80, 720.00, 800.00, 20, 800.00, 'completed');
```

## **Technical Considerations**

### **Data Volume Management**
- **Initial Load**: Generate 1-2 months of historical data
- **Hourly Updates**: Add new data points every hour (realistic for social media)
- **Data Retention**: Keep 12 months of data, archive older records
- **Performance**: Use database partitioning for large datasets
- **Query Optimization**: All queries filter by user_id first for proper isolation
- **JSONB Storage**: Platform-specific metrics stored efficiently without NULL fields

### **Realism Factors**
- **Viral Posts**: 5-10% of posts should show explosive growth
- **Dying Posts**: 20-30% should show declining engagement
- **Steady Posts**: 60-70% should show moderate, consistent growth
- **Platform Variations**: Different platforms should have different performance patterns

### **Cost Realism**
- **Revenue Multiplier**: 2-5x the ad spend for good ROI
- **Platform Differences**: Instagram typically costs more than Facebook
- **Content Type Impact**: Video content costs more than static posts
- **Seasonal Variations**: Costs fluctuate based on competition

## **Success Metrics**

### **Dashboard Performance**
- [ ] ROI calculations are mathematically accurate
- [ ] Charts render smoothly with real-time data
- [ ] All tabs display meaningful information
- [ ] Export functionality works correctly

### **Data Quality**
- [ ] Growth patterns look realistic
- [ ] Cost structures match industry standards
- [ ] ROI ranges are believable (100-800%)
- [ ] Platform differences are apparent

### **User Experience**
- [ ] Dashboard loads in under 2 seconds
- [ ] Data updates are visible and meaningful
- [ ] Charts are interactive and informative
- [ ] Mobile responsiveness maintained

## **Risk Mitigation**

### **Technical Risks**
- **Database Performance**: Implement proper indexing and partitioning
- **Data Consistency**: Use transactions for related table updates
- **Memory Usage**: Optimize data generation algorithms
- **Scalability**: Design for multiple users and large datasets

### **Business Risks**
- **Data Credibility**: Ensure mock data looks realistic to marketing professionals
- **Platform Accuracy**: Research actual platform performance metrics
- **Cost Realism**: Validate against industry benchmarks
- **Growth Patterns**: Study real social media viral patterns

## **Future Enhancements**

### **Advanced Analytics**
- [ ] Predictive ROI modeling
- [ ] Competitor benchmarking integration
- [ ] A/B testing simulation
- [ ] Seasonal trend analysis

### **Data Sources**
- [ ] Integration with actual platform APIs
- [ ] Real campaign data import
- [ ] User-provided performance data
- [ ] Industry benchmark data

## **Dashboard Settings - Data Read Plan**

### Components in `dashboard -> settings`
- `SettingsWizard` (steps rendered inside):
  - `IndustryStep`
  - `GoalsStep`
  - `CompetitorStep`
- `ConnectedAccounts`

These are primarily form/read views (no charts). Below are the exact tables, columns, and read/write behaviors each uses.

### Tables required (Settings)

```sql
-- 1) User preferences (one row per user)
CREATE TABLE IF NOT EXISTS user_preferences (
  user_id VARCHAR(255) PRIMARY KEY REFERENCES users(clerk_id) ON DELETE CASCADE,
  industry TEXT NOT NULL,
  company_size TEXT NOT NULL,                 -- values: solo | small | medium | large | enterprise (mapped in UI)
  marketing_goals TEXT[] NOT NULL DEFAULT '{}',
  monthly_budget TEXT NOT NULL,               -- stored as label (e.g., "1000-5000"); UI maps to human labels
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- 2) User competitors (many per user)
CREATE TABLE IF NOT EXISTS user_competitors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR(255) NOT NULL REFERENCES users(clerk_id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  website_url TEXT,
  description TEXT,
  platforms TEXT[] NOT NULL DEFAULT '{}',     -- ["facebook","instagram","youtube",...]
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_user_competitors_user_id ON user_competitors(user_id);

-- 3) Connected accounts (per platform per user)
CREATE TABLE IF NOT EXISTS connected_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR(255) NOT NULL REFERENCES users(clerk_id) ON DELETE CASCADE,
  platform TEXT NOT NULL,                     -- "facebook" | "instagram" | "youtube" | "x" | "linkedin" | "gmail"
  username TEXT,
  display_name TEXT,
  is_connected BOOLEAN NOT NULL DEFAULT FALSE,
  permissions TEXT[] NOT NULL DEFAULT '{}',   -- e.g. ["read_insights","publish","ads"]
  last_sync_at TIMESTAMP,
  connected_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_connected_accounts_user_platform ON connected_accounts(user_id, platform);
CREATE INDEX IF NOT EXISTS idx_connected_accounts_user_id ON connected_accounts(user_id);
```

### SettingsWizard

- Loads and saves via `ApiClient` methods already used in `components/settings/settings-wizard.tsx`:
  - `getUserPreferences(clerkId)` ↔ table `user_preferences`
  - `saveUserPreferences(clerkId, { industry, companySize, goals, budget })` writes to `user_preferences`
  - `getUserCompetitors(clerkId)` ↔ table `user_competitors`
  - `saveCompetitor(clerkId, { name, website, description, platforms })` inserts into `user_competitors`
  - `updateCompetitor(clerkId, id, payload)` updates `user_competitors`
  - `deleteCompetitor(clerkId, id)` deletes from `user_competitors`

#### IndustryStep (Read/Write)
- Read from: `user_preferences(industry, company_size)`
- Write to: `user_preferences(industry, company_size)`
- UI mapping:
  - DB `company_size` ↔ UI values: `solo | small | medium | large | enterprise`

Example read:
```sql
SELECT industry, company_size
FROM user_preferences
WHERE user_id = $1;
```

#### GoalsStep (Read/Write)
- Read from: `user_preferences(marketing_goals, monthly_budget)`
- Write to: `user_preferences(marketing_goals, monthly_budget)`
- Types: `marketing_goals` is `TEXT[]`; `monthly_budget` stored as a code (e.g., `1000-5000`) and mapped to labels in UI.

Example read:
```sql
SELECT marketing_goals, monthly_budget
FROM user_preferences
WHERE user_id = $1;
```

#### CompetitorStep (Read/Write)
- Read from: `user_competitors(name, website_url, description, platforms)`
- Write to: `user_competitors` via create/update/delete per row

Example reads/writes:
```sql
-- Read list
SELECT id, name, website_url, description, platforms
FROM user_competitors
WHERE user_id = $1
ORDER BY created_at DESC;

-- Insert
INSERT INTO user_competitors(user_id, name, website_url, description, platforms)
VALUES ($1, $2, $3, $4, $5)
RETURNING id;

-- Update
UPDATE user_competitors
SET name = $3, website_url = $4, description = $5, platforms = $6, updated_at = NOW()
WHERE user_id = $1 AND id = $2;

-- Delete
DELETE FROM user_competitors
WHERE user_id = $1 AND id = $2;
```

### ConnectedAccounts (Read)

- Frontend fetches: `GET {API_BASE}/social-media/connected-accounts` with header `X-User-ID: {clerkId}`
- Backing table: `connected_accounts` (above)
- Response shape expected in UI (from `components/settings/connected-accounts.tsx`):
```json
{
  "accounts": [
    { "platform": "facebook", "username": "@brand", "displayName": "Brand", "isConnected": true, "permissions": ["read_insights"], "lastSync": "2025-08-20 09:00" },
    { "platform": "instagram", "username": "@brand.ig", "displayName": "Brand IG", "isConnected": false, "permissions": [] }
  ]
}
```

Example read:
```sql
SELECT platform, username, display_name, is_connected, permissions, last_sync_at
FROM connected_accounts
WHERE user_id = $1
ORDER BY platform ASC;
```

Notes:
- No charts in Settings; the UI renders badges, statuses, and action buttons.
- For performance, ensure indexes on `user_id` and unique `(user_id, platform)`.

---

## **Implementation Summary & Next Steps**

### **🎯 What We've Accomplished:**
1. **✅ Database Architecture**: Complete table structure with proper user isolation
2. **✅ Data Generation Strategy**: 10-minute updates with realistic multiplier-based growth
3. **✅ ROI Calculations**: All 6 dashboard tabs with specific formulas and queries
4. **✅ Performance Optimization**: Proper indexing, caching, and query strategies
5. **✅ Table Separation**: New tables won't interfere with friend's optimization work

### **🚀 Immediate Next Steps:**

#### **Week 1: Database Foundation**
```bash
# 1. Run the database creation scripts
psql -d your_database -f database_setup.sql

# 2. Verify table structure
\d campaign_with_user_id
\d roi_metrics  
\d platform_metrics

# 3. Test user isolation
INSERT INTO campaign_with_user_id (user_id, name, date) VALUES ('test_user', 'Test Campaign', '2024-01-01');
SELECT * FROM campaign_with_user_id WHERE user_id = 'test_user';
```

#### **Week 2: Data Generation Engine**
```bash
# 1. Set up your Node.js/Python environment
npm install node-cron @supabase/supabase-js
# or
pip install apscheduler supabase

# 2. Test the 10-minute scheduler
node test_scheduler.js
# or
python test_scheduler.py

# 3. Generate initial historical data
node generate_initial_data.js
```

#### **Week 3: ROI Dashboard Integration**
```bash
# 1. Connect your React components to the database
# 2. Implement time range filtering
# 3. Test all 6 dashboard tabs
# 4. Add caching layer
```

### **🔑 Key Success Factors:**
- **User Isolation**: Every query filters by `user_id` first
- **Realistic Data**: Multiplier-based growth with 10-minute updates
- **Performance**: Proper indexing and caching for smooth dashboard experience
- **Separation**: Your ROI system works independently of friend's optimization work

### **📊 Expected Results:**
- **Dashboard Load Time**: < 2 seconds with caching
- **Data Updates**: Every hour (realistic for social media)
- **User Experience**: Each user sees only their own data
- **ROI Calculations**: Accurate and meaningful insights across all platforms
- **Database Performance**: 24 entries per post per day (not 144!)
- **Data Realism**: Exponential growth with realistic bounds and decay

## **Conclusion**

This implementation plan provides a comprehensive roadmap for creating a realistic, data-driven ROI dashboard that will effectively demonstrate the platform's analytical capabilities. By focusing on realistic data generation and proper database architecture, we can create a compelling user experience that showcases the value of centralized social media management.

**The key success factor is balancing realism with demonstration value** - the data should look authentic enough that marketing professionals can see the potential, while being clearly mock data for development purposes.

**Your ROI dashboard will now have:**
- ✅ **Proper user isolation** with proper foreign key constraints
- ✅ **Realistic mock data** that updates every hour (not every 10 minutes!)
- ✅ **All 6 dashboard tabs** with accurate calculations and revenue logic
- ✅ **Performance optimization** with JSONB storage and proper indexing
- ✅ **Zero interference** with your friend's existing work
- ✅ **Realistic growth patterns** with decay and bounds (no more 16M views!)

**Ready to start building? Let's begin with Week 1 database setup! 🚀**

---

## **Operational Runner (run.py) - Logging and Exception Visibility**

Purpose: when you run `run.py`, you should clearly see which background jobs are running and any failures with stack traces.

### Suggested `run.py` structure
```python
import asyncio
import logging
import traceback
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Replace with your real implementations
# from services.roi.update import execute_roi_update, invalidate_cache_for_all_users

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("runner")

# Simple health status
last_status = {
    "roi_update": {"ok": None, "when": None, "error": None},
}

async def roi_update_job():
    job_name = "roi_update"
    logger.info(f"Starting job: {job_name}")
    try:
        # await execute_roi_update()  # do the hourly ROI write
        # Optionally: await invalidate_cache_for_all_users()
        await asyncio.sleep(0.1)  # placeholder
        last_status[job_name] = {"ok": True, "when": datetime.utcnow(), "error": None}
        logger.info(f"Job success: {job_name}")
    except Exception as e:
        err = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        last_status[job_name] = {"ok": False, "when": datetime.utcnow(), "error": err}
        logger.error(f"Job failed: {job_name} -> {err}")

async def heartbeat():
    while True:
        # Print a compact dashboard of what is running and last outcomes
        lines = ["\n=== Runner Heartbeat ==="]
        for name, status in last_status.items():
            ok = status["ok"]
            when = status["when"]
            err = status["error"]
            lines.append(f"- {name}: ok={ok} when={when}")
            if err:
                lines.append(f"  last_error: {err.splitlines()[-1]}")
        logger.info("\n".join(lines))
        await asyncio.sleep(60)

async def main():
    logger.info("Runner starting...")
    scheduler = AsyncIOScheduler(timezone="UTC")

    # Hourly ROI update at minute 0
    scheduler.add_job(roi_update_job, CronTrigger.from_crontab("0 * * * *"), id="roi_update")
    scheduler.start()

    # Continuous heartbeat
    await heartbeat()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Runner stopped by user")
    except Exception as e:
        logger.exception("Runner crashed: %s", e)
```

Notes:
- Each job logs start/success/failure; on failure, a full stack trace is printed.
- Heartbeat prints a concise status every minute.
- Use your actual `execute_roi_update()` implementation and cache invalidation.

---

## **One-Time 7-Day Mock Backfill (run after tables exist)**

Use this SQL only once after you’ve created the tables in Supabase. It inserts a realistic baseline for the last 7 days for Facebook, Instagram, and YouTube, plus two sample campaigns. Replace `USER_CLERK_ID_HERE` with a real Clerk user id.

```sql
DO $$
DECLARE
  uid TEXT := 'USER_CLERK_ID_HERE';
  d DATE;
  c1 INTEGER;
  c2 INTEGER;
  p TEXT;
  v INTEGER;
  l INTEGER;
  cm INTEGER;
  sh INTEGER;
  cl INTEGER;
  spend NUMERIC;
  rev NUMERIC;
BEGIN
  -- Create two campaigns in the last 7 days
  INSERT INTO campaign_with_user_id (user_id, name, date, impressions, clicks, ctr, cpc, spend, budget, conversions, net_profit, ongoing)
  VALUES (uid, 'Spring Promo', (CURRENT_DATE - 6), 0,0,0,0,0,0,0,0,'true')
  RETURNING id INTO c1;

  INSERT INTO campaign_with_user_id (user_id, name, date, impressions, clicks, ctr, cpc, spend, budget, conversions, net_profit, ongoing)
  VALUES (uid, 'Video Launch', (CURRENT_DATE - 3), 0,0,0,0,0,0,0,0,'true')
  RETURNING id INTO c2;

  -- For each of the last 7 days, insert one ROI snapshot per platform at noon
  FOR d IN SELECT generate_series(CURRENT_DATE - 6, CURRENT_DATE, '1 day')::date LOOP
    FOR p IN SELECT unnest(ARRAY['facebook','instagram','youtube']) LOOP
      v := 100 + (random()*900)::int;         -- views
      l := 10 + (random()*90)::int;           -- likes
      cm := 5 + (random()*45)::int;           -- comments
      sh := 2 + (random()*30)::int;           -- shares
      cl := 8 + (random()*70)::int;           -- clicks
      spend := round((5 + random()*45)::numeric, 2);
      rev := round((spend * (1.5 + random()*2.5))::numeric, 2);

      INSERT INTO roi_metrics (
        user_id, platform, campaign_id, post_id, content_type, content_category,
        views, likes, comments, shares, saves, clicks,
        ad_spend, revenue_generated, cost_per_click, cost_per_impression,
        roi_percentage, roas_ratio, update_timestamp
      )
      VALUES (
        uid, p, CASE WHEN d <= CURRENT_DATE - 3 THEN c1 ELSE c2 END, NULL, 'video', 'generic',
        v, l, cm, sh, 1, cl,
        spend, rev, NULL, NULL,
        CASE WHEN spend>0 THEN ((rev - spend)/spend)*100 ELSE 0 END,
        CASE WHEN spend>0 THEN (rev/spend) ELSE 0 END,
        (d + time '12:00')
      );
    END LOOP;
  END LOOP;
END$$;
```

What this provides:
- Two campaigns across the week, daily snapshots at noon for FB/IG/YouTube
- Reasonable randomized engagement and finance numbers
- Immediate data for charts (including ROI Trends + campaign star markers for the last 7 days)

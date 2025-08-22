# ROI Sample Data Generator

This tool populates the ROI dashboard with realistic sample data to create beautiful, professional-looking graphs and visualizations.

## 🎯 What It Does

The sample data generator creates comprehensive data across:

- **3 Social Media Platforms**: YouTube, Instagram, Facebook
- **3 Content Types**: Video, Reel, Post
- **6 Content Categories**: Product, Lifestyle, Educational, Entertainment, Promotional, User Generated
- **90 Days of Historical Data**: For beautiful trend visualization
- **Realistic Performance Patterns**: Platform-specific and content-type-specific metrics

## 📊 Data Generated

### ROI Metrics (~800-1200 records)
- Views, likes, comments, shares, saves, clicks
- Ad spend and revenue generated
- ROI percentage and ROAS ratio
- Cost per click and cost per impression
- Realistic engagement rates and conversion metrics
- **Only targets the `roi_metrics` table**

## 🚀 Quick Start

### Option 1: PowerShell (Recommended)
```powershell
# Navigate to backend directory
cd bos_solution/backend

# Run with confirmation prompts
.\run_sample_data.ps1

# Run without prompts
.\run_sample_data.ps1 -Force

# Show help
.\run_sample_data.ps1 -Help
```

### Option 2: Batch File (Windows)
```cmd
# Navigate to backend directory
cd bos_solution\backend

# Run the batch file
run_sample_data.bat
```

### Option 3: Direct Python
```bash
# Navigate to backend directory
cd bos_solution/backend

# Run the Python script directly
python populate_roi_sample_data.py
```

## 🔧 Prerequisites

1. **Python 3.8+** installed and in PATH
2. **Supabase Connection** configured with environment variables
3. **Database Tables** created (roi_metrics table must exist)
4. **Backend Environment** set up with proper .env file

## 📋 Environment Setup

Make sure your `.env` file contains the necessary Supabase credentials:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## 🎨 Dashboard Features Enhanced

After running the sample data generator, your ROI dashboard will display:

### 📈 Beautiful Trend Charts
- **ROI Trends**: Daily ROI percentage over time with industry benchmarks
- **Revenue Trends**: Revenue generation patterns across platforms
- **Cost Analysis**: Ad spend breakdown and monthly trends
- **Channel Performance**: Platform-specific performance comparisons

### 📊 Professional Metrics
- **Total ROI**: Aggregated return on investment
- **Revenue Generated**: Total revenue across all campaigns
- **Ad Spend**: Total advertising expenditure
- **Profit Margin**: Calculated profit margins

### 🔍 Detailed Analytics
- **Revenue by Source**: Platform-specific revenue breakdown
- **Cost Breakdown**: Platform-specific cost analysis
- **Profitability Metrics**: CLV and CAC calculations
- **Channel Performance**: Detailed platform comparisons

## 🎯 Realistic Data Patterns

The generated data includes:

### Platform-Specific Performance
- **YouTube**: Higher views (3x multiplier), moderate engagement, high revenue potential (2.5x multiplier)
- **Instagram**: High engagement rates (2x likes multiplier), strong visual content performance, good revenue (1.8x multiplier)
- **Facebook**: Balanced performance across all metrics (baseline 1x multiplier)

### Content Type Variations
- **Video**: High engagement and view rates (2x views, 1.8x likes, 1.8x revenue)
- **Reel**: Highest engagement and view rates (2.5x views, 2x likes, 2x revenue)
- **Post**: Text-based, moderate performance (0.8x views, 0.9x likes, 0.9x revenue)

### Seasonal Patterns
- **Weekend Peaks**: Higher engagement on weekends
- **Seasonal Variations**: ±30% variation to simulate real-world patterns
- **Growth Trends**: Gradual improvement over time

## 🔄 Data Refresh

To refresh or add more data:

```powershell
# Clear existing data (optional)
# Note: This will remove all existing ROI data

# Generate fresh data
.\run_sample_data.ps1 -Force
```

## 🛠️ Troubleshooting

### Common Issues

1. **Python Not Found**
   ```
   ❌ Python is not installed or not in PATH
   ```
   **Solution**: Install Python 3.8+ and ensure it's in your system PATH

2. **Environment Variables Missing**
   ```
   ⚠️ Warning: .env file not found
   ```
   **Solution**: Create a `.env` file with your Supabase credentials

3. **Database Connection Error**
   ```
   ❌ Error during sample data generation
   ```
   **Solution**: Check your Supabase URL and API keys

4. **Table Not Found**
   ```
   ❌ Failed to insert record: 404
   ```
   **Solution**: Ensure the roi_metrics table exists (run the schema scripts first)

### Verification

After running the script, verify the data was created:

```sql
-- Check ROI metrics
SELECT COUNT(*) FROM roi_metrics;

-- View sample data by platform
SELECT platform, COUNT(*) as count, AVG(roi_percentage) as avg_roi 
FROM roi_metrics 
GROUP BY platform;

-- Check data distribution
SELECT 
    platform,
    COUNT(*) as total_records,
    AVG(views) as avg_views,
    AVG(likes) as avg_likes,
    AVG(roi_percentage) as avg_roi,
    AVG(revenue_generated) as avg_revenue
FROM roi_metrics 
GROUP BY platform
ORDER BY avg_revenue DESC;
```

## 🎉 Results

After successful execution, you should see:

```
🎉 Sample data generation completed successfully!
📈 Total records created:
   • ~800-1200 ROI metrics records (90 days)
   • Platforms: YouTube, Instagram, Facebook only
   • Target table: roi_metrics only
   • 3 content types and 6 content categories

✨ Your ROI dashboard should now display beautiful, professional graphs!
🚀 You can now visit the ROI dashboard to see the enhanced visualizations.

💡 Platform-specific patterns:
   • YouTube: Higher views, moderate engagement, high revenue potential
   • Instagram: High engagement rates, strong visual content performance
   • Facebook: Balanced performance across all metrics
```

## 💡 Tips for Best Results

1. **Try Different Time Ranges**: Test 7d, 30d, 90d, and 1y views
2. **Explore All Tabs**: Check Overview, Revenue, Costs, Profitability, and Channels
3. **Compare Platforms**: Notice the realistic performance differences between YouTube, Instagram, and Facebook
4. **Export Data**: Use the CSV/PDF export features to see the data structure

## 🔧 Customization

To modify the data generation:

1. **Adjust Volume**: Change the `daily_records` range in the script (currently 5-12 per day)
2. **Modify Platforms**: The script is currently set to YouTube, Instagram, and Facebook only
3. **Change Metrics**: Adjust the `METRIC_RANGES` for different performance levels
4. **Add Content Types**: Extend the `CONTENT_TYPES` and `CONTENT_CATEGORIES` lists (currently video, reel, post)

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your environment setup
3. Ensure the roi_metrics table exists and is accessible
4. Check Supabase connection and permissions

---

**Happy Dashboarding! 🎉**

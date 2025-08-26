# ROI Dashboard Data Strategy

## Original Requirements Text from user
✅ Time range filtering is dynamic (updates every time you change dropdown)
✅ Live data keeps flowing in (every 10 minutes)
✅ Dashboard shows current data (not stale historical data)
✅ This is exactly what you want for a real-time ROI dashboard!

I mean yes i do want live update, but it only happens in a day form. Okay meraning, i want it to be if i choose 7 days, then today's data should be fetched, we just fetch until yesterday, like if today is 24 Aug, then i prolly will be fetching from 18 Aug to 24 Aug, but 24 Aug data is prolly not complete right, but its okay i have a plan, meaning like everyday, you will be calculating the ROI by DAY, like u sum up all today's revenue, (no matter what platform), also sums up ad spend, then fit into the formula, so the graph plotting is correct. and u dont care how many rows are there, u will just take ALL for that day, like if 23 august i will be taking ALL ROWS from 23 aug, no matter how many lines. Yes and thats the key idea of plotting the ROI trends graph, and it must be following the time range user selecteed in dropdown


## 🎯 **Core Concept: Daily Aggregation for Real-Time Trends**

The ROI dashboard should display **daily aggregated data** that updates in real-time, providing accurate trend visualization while maintaining data integrity.

## 📅 **Time Range Strategy**

### **Current Day Exclusion**
- **Today's data is fetched** for trend calculations
- **Reason**: Even Today is incomplete, u can still calculate the daily ROI percentage
What you need to do for the ROI trends table -> u just fetch all data for that specific range, and classify by days, and for ea
- **Example**: If today is August 24th, we fetch from August 18th to August 24rd (for 7-day view)


### **Time Range Mapping**
- **"7d"** → Fetch data from 7 days ago to yesterday
- **"30d"** → Fetch data from 30 days ago to yesterday  
- **"90d"** → Fetch data from 90 days ago to yesterday

### **Date Calculation Example**
```
Current Date: August 24th, 2024
User Selects: "7d"

Start Date: August 18th, 00:00:00
End Date: August 24rd, 23:59:59
Data Range: 7 complete days (excluding today)
```

## 📊 **Daily Data Aggregation**

### **Revenue Calculation (Per Day)**
- **Sum ALL revenue_generated** from ALL platforms for that specific day
- **Formula**: `daily_revenue = SUM(revenue_generated) WHERE DATE(created_at) = '2024-08-23'`
- **Platforms**: YouTube, Facebook, Instagram (all combined)

### **Ad Spend Calculation (Per Day)**
- **Sum ALL ad_spend** from ALL platforms for that specific day
- **Formula**: `daily_ad_spend = SUM(ad_spend) WHERE DATE(created_at) = '2024-08-23'`
- **Platforms**: YouTube, Facebook, Instagram (all combined)

### **ROI Calculation (Per Day)**
- **Formula**: `daily_roi = ((daily_revenue - daily_ad_spend) / daily_ad_spend) * 100`
- **Result**: One ROI percentage per day

## 🔄 **Live Update Integration**

### **Data Flow**
1. **Live Updates**: Every 10 minutes, new rows inserted with current timestamps
2. **Dashboard Refresh**: When user changes time range, recalculate daily aggregations
3. **Real-Time**: Today's live data flows in, but doesn't affect historical trends
4. **Consistency**: Historical trends remain stable while new data accumulates

### **Example Timeline**
```
August 23rd (Complete Day):
- 00:00-23:59: Live updates every 10 minutes
- Total: 144 rows (3 platforms × 144 intervals)
- Daily Revenue: Sum of all 144 revenue_generated values
- Daily Ad Spend: Sum of all 144 ad_spend values
- Daily ROI: Calculated from daily totals

August 24th (Current Day):
-  applies the same calculation logic as complete day even today's data is still incomplete
```

## 📈 **Graph Plotting Strategy**

### **ROI Trends Graph**
- **X-Axis**: Dates (excluding today)
- **Y-Axis**: Daily ROI percentages
- **Data Points**: One point per complete day
- **Update Frequency**: Every time user changes time range dropdown

### **Channel Performance**
- **Per Platform**: Show daily metrics per platform
- **Aggregation**: Sum all rows for each platform per day
- **Exclusion**: Today's incomplete data

## 🎛️ **User Experience**

### **Dropdown Behavior**
- **Immediate Response**: Changing dropdown instantly recalculates data
- **Visual Feedback**: Graphs update to show new time range
- **Data Consistency**: Historical trends remain accurate

### **Real-Time vs Historical**
- **Historical View**: Clean, complete daily trends
- **Live View**: Today's accumulating data (separate display)
- **No Confusion**: Clear separation between complete and incomplete data

## 🔧 **Technical Implementation Requirements**

### **Backend Changes Needed**
1. **Time Range Filtering**: Exclude current day from all queries
2. **Daily Aggregation**: Group by DATE(created_at) and sum metrics
3. **Platform Combination**: Aggregate across all platforms per day
4. **ROI Calculation**: Apply formula to daily totals

### **Database Queries**
```sql
-- Example for 7-day view (excluding today)
SELECT 
    DATE(created_at) as date,
    SUM(revenue_generated) as daily_revenue,
    SUM(ad_spend) as daily_ad_spend,
    ((SUM(revenue_generated) - SUM(ad_spend)) / SUM(ad_spend)) * 100 as daily_roi
FROM roi_metrics 
WHERE user_id = ? 
    AND created_at >= '2024-08-18 00:00:00'
    AND created_at < '2024-08-24 00:00:00'
GROUP BY DATE(created_at)
ORDER BY date ASC
```

### **Frontend Changes Needed**
1. **Time Range Handling**: Ensure dropdown triggers backend recalculation
2. **Data Visualization**: Update graphs with new daily aggregated data
3. **Loading States**: Show loading while recalculating
4. **Error Handling**: Handle cases where no data exists for range

## ✅ **Expected Results**

### **Before Implementation**
- ❌ Graphs don't update when changing dropdown
- ❌ Data appears inconsistent or stale
- ❌ Today's incomplete data skews trends

### **After Implementation**
- ✅ Immediate response to dropdown changes
- ✅ Accurate historical trends (excluding incomplete days)
- ✅ Real-time data accumulation for current day
- ✅ Clean, consistent graph visualization
- ✅ Proper daily ROI calculations

## 🎯 **Key Benefits**

1. **Data Accuracy**: Historical trends based on complete days only
2. **Real-Time Updates**: Live data flows in without affecting history
3. **User Control**: Immediate response to time range selection
4. **Consistent Visualization**: Clean graphs that make business sense
5. **Scalable**: Works with any number of daily rows


## Fixing mismatch of fetching datas from roi_metrics table
Example of the ROI table:
id,user_id,platform,campaign_id,post_id,content_type,content_category,views,likes,comments,shares,saves,clicks,ad_spend,revenue_generated,cost_per_click,cost_per_impression,roi_percentage,roas_ratio,created_at,posted_at,updated_at,update_timestamp
19743,user_31VgZVmUnz3XYl4DnOB1NQG5TwP,youtube,,youtube_post_26162,video,generic,42532,3448,452,890,1084,2181,2366.63,3044.47,0.95,0.0071,28.64,1.29,2025-08-24 00:17:14.400387,2025-08-24 00:17:14.400387,2025-08-24 00:17:14.400387,2025-08-24 00:17:14.400387
19744,user_31VgZVmUnz3XYl4DnOB1NQG5TwP,facebook,,facebook_post_65025,photo,generic,12780,1082,150,313,400,737,1018.69,912.17,1.14,0.0139,-10.46,0.90,2025-08-24 00:27:14.400387,2025-08-24 00:27:14.400387,2025-08-24 00:27:14.400387,2025-08-24 00:27:14.400387
(use for reference if unsure about the structure of table)

🔍 Issue #1: Pattern Mismatch in Backend
The backend endpoints have different pattern validations:
/roi/trends (line 556): pattern="^(7d|30d|90d)$" ✅ CORRECT
/channel/performance (line 600): pattern="^(7d|30d|90d)$" ✅ CORRECT
/overview (line 189): pattern="^(7d|30d|90d|1y)$" ❌ WRONG!
�� Issue #2: Frontend vs Backend Mismatch
Frontend TimeRange: '7d' | '30d' | '90d' (3 options)
Backend Overview: '7d' | '30d' | '90d' | '1y' (4 options)
Backend Trends/Channel: '7d' | '30d' | '90d' (3 options)
🔍 Issue #3: Data Filtering Problem
The backend is filtering by update_timestamp but your live update system is inserting with created_at timestamps. Even though you said they're the same, there might be a mismatch.
🔍 Issue #4: Missing User ID Filtering
The backend endpoints have removed user_id filtering (line 206 comment: "removed user_id filtering"), which means they're returning ALL data from the database, not just your user's data.
🎯 The Hidden Problems:
Overview endpoint still expects '1y' but frontend doesn't send it
No user_id filtering - returning all users' data
Timestamp column mismatch between filtering and insertion
Pattern validation inconsistencies across endpoints
💡 Why Dropdown Changes Don't Work:
When you change the dropdown:
✅ Frontend sends correct range (7d, 30d, 90d)
✅ Backend receives correct range
❌ But backend returns ALL data (no user filtering)
❌ Timestamp filtering might be wrong (update_timestamp vs created_at)
❌ Overview endpoint might reject the request due to pattern mismatch
🔧 To Fix This, We Need To:
Fix the pattern validation in overview endpoint
Restore user_id filtering in all endpoints
Ensure timestamp columns match between insertion and filtering
Add logging to see what data is actually being returned
Should I show you exactly which lines need to be fixed, or do you want to investigate further first?

## 🚨 **Critical Backend Issues Found (Why Dropdown Doesn't Work)**

### **🔍 Issue #1: Pattern Validation Mismatch**
The backend endpoints have **inconsistent pattern validations**:
- **`/roi/trends`**: `pattern="^(7d|30d|90d)$"` ✅ **CORRECT**
- **`/channel/performance`**: `pattern="^(7d|30d|90d)$"` ✅ **CORRECT**  
- **`/overview`**: `pattern="^(7d|30d|90d|1y)$"` ❌ **WRONG!** (expects '1y' but frontend doesn't send it)

### **🔍 Issue #2: Frontend vs Backend Mismatch**
- **Frontend TimeRange**: `'7d' | '30d' | '90d'` (3 options)
- **Backend Overview**: `'7d' | '30d' | '90d' | '1y'` (4 options)
- **Backend Trends/Channel**: `'7d' | '30d' | '90d'` (3 options)

### **🔍 Issue #3: Missing User ID Filtering**
- **Backend endpoints have removed user_id filtering** (line 206 comment: "removed user_id filtering")
- **This means they return ALL data from the database**, not just your user's data
- **Result**: Dashboard shows mixed data from multiple users

### **🔍 Issue #4: Timestamp Column Strategy**
- **Decision**: Use `created_at` column for all filtering (since it matches your live update system)
- **Current Problem**: Backend filters by `update_timestamp` but live updates insert with `created_at`
- **Solution**: Change all backend queries to filter by `created_at` instead

## 💡 **Why Your Dropdown Changes Don't Work:**

When you change the dropdown:
1. ✅ **Frontend sends correct range** (7d, 30d, 90d)
2. ✅ **Backend receives correct range**
3. ❌ **But backend returns ALL data** (no user filtering)
4. ❌ **Timestamp filtering is wrong** (update_timestamp vs created_at)
5. ❌ **Overview endpoint might reject request** due to pattern mismatch

## 🔧 **Exact Fixes Needed:**

### **1. Fix Pattern Validation in Overview Endpoint**
```python
# Change this line in /overview endpoint:
pattern="^(7d|30d|90d|1y)$"  # ❌ WRONG

# To this:
pattern="^(7d|30d|90d)$"     # ✅ CORRECT
```

### **2. Restore User ID Filtering in All Endpoints**
```python
# Add back user_id filtering in all endpoints:
params={
    "user_id": f"eq.{user_id}",  # ✅ RESTORE THIS
    "created_at": f"gte.{start_iso}",
    "created_at": f"lt.{end_iso}"
}
```

### **3. Change All Timestamp Filtering to created_at**
```python
# Change from update_timestamp to created_at:
params={
    "created_at": f"gte.{start_iso}",  # ✅ USE created_at
    "created_at": f"lt.{end_iso}"     # ✅ USE created_at
}
```

### **4. Add Debug Logging**
```python
# Add logging to see what data is actually returned:
print(f"🔍 Query params: {params}")
print(f"📊 Rows returned: {len(response.json())}")
print(f"📅 Date range: {start_iso} to {end_iso}")
```

## 🎯 **Expected Result After Fixes:**

1. ✅ **Dropdown changes work immediately** - graphs update instantly
2. ✅ **Only your user's data** is displayed (no more mixed data)
3. ✅ **Correct time range filtering** using created_at timestamps
4. ✅ **Daily aggregation works** as intended
5. ✅ **Real-time updates continue** without affecting historical trends

## 🚀 **Next Steps:**

1. **Fix the backend pattern validation** (remove '1y' from overview)
2. **Restore user_id filtering** in all endpoints
3. **Change timestamp filtering** to use created_at
4. **Add debug logging** to verify data flow
5. **Test dropdown changes** to confirm graphs update

This will solve the "hidden problem" that's been preventing your ROI dashboard from working properly! 🎯


🎯 What I Think About This:
🚨 The Root Cause is Clear:
Your ROI dashboard isn't working because of multiple backend mismatches that are preventing proper data flow:
Pattern validation mismatch - Overview endpoint expects '1y' but frontend doesn't send it
Missing user filtering - Backend returns ALL users' data instead of just yours - we are in testing phase, so this can be neglected first

Timestamp column mismatch - Backend filters by update_timestamp but live updates use created_at
💡 Why This Explains Everything:
Dropdown changes don't work because the backend is rejecting requests or returning wrong data
Graphs don't update because they're getting mixed data from multiple users
Data appears inconsistent because timestamp filtering is wrong
🔧 The Fix Strategy is Solid:
Standardize all endpoints to use the same pattern validation
Restore user filtering so you only see your data
Use created_at consistently since that's what your live update system uses
Add logging to verify the fix works
🚀 My Recommendation:
Let's fix these backend issues first before implementing the daily aggregation logic. Once the basic data flow works (dropdown changes trigger proper data fetching), then we can add the daily aggregation layer.
Should we start implementing these fixes now? I can show you exactly which lines to change in the backend files.

AI FIX
 Current ROI Trends Logic Analysis:
1. Data Fetching (Working ✅):
Your backend correctly fetches data for the selected time range (7d, 30d, 90d)
The created_at filtering is working properly
You're getting the right number of rows for each range
2. ROI Calculation Logic (The Problem ❌):
Looking at your /trends endpoint:
The issue: You're looking for row.get("roi") but your database column is actually called roi_percentage!
3. What Should Happen vs What's Happening:
✅ What Should Happen:
Fetch rows for selected time range
Extract roi_percentage from each row
Group by date (YYYY-MM-DD)
Calculate average ROI per day
Return daily averages for the graph
❌ What's Actually Happening:
Fetch rows for selected time range ✅
Look for row.get("roi") (which doesn't exist) ❌
Since roi is always None, no data gets added to daily_roi ❌
Empty daily_roi dictionary ❌
Return empty series array ❌
Graph shows no data ❌
4. The Fix Needed:
Change this line:
To this:
And change this line:
To this:
5. Why This Explains Your Behavior:
7d range: Probably has recent data with roi_percentage values, so some data shows up
30d/90d ranges: Older data might have different roi_percentage patterns, or the column name mismatch is more apparent
Graph updates: The range changes trigger new API calls, but the ROI calculation always fails due to wrong column name
6. Verification:
Check your database - the column should be roi_percentage, not roi. This mismatch is why your graphs aren't showing the expected daily ROI trends even though the time range filtering is working perfectly.
The fix is simple: Just change the column name from roi to roi_percentage in the trends endpoint, and your graphs should start showing proper daily ROI data! 🎯


for row in rows:
    date_key = row["created_at"][:10]  # YYYY-MM-DD
    if row.get("roi_percentage") is not None:
        daily_roi[date_key].append(float(row["roi_percentage"]))
This fetches ALL ROI_PERCENTAGE values for each day - meaning if you have multiple rows per day (like your 10-minute updates), you'll get multiple ROI values per day.
Example of What Happens:
If you have data like:
2024-08-24 10:00 → ROI: 25.5%
2024-08-24 10:10 → ROI: 26.1%
2024-08-24 10:20 → ROI: 25.8%
2024-08-24 11:00 → ROI: 26.3%
Your code will collect: [25.5, 26.1, 25.8, 26.3] for August 24th, then calculate the average: (25.5 + 26.1 + 25.8 + 26.3) / 4 = 25.9%
🎯 Best Approach Options:
Option 1: Daily Average (Current Logic - Recommended ✅)
KEEP THE CURRENT LOGIC ON THIS


📝 Updated ROI Dashboard Data Strategy
🔧 CRITICAL BACKEND ISSUES IDENTIFIED & FIXED:
1. ROI Trends Endpoint - Column Name Mismatch ✅ FIXED
Problem: Backend was looking for row.get("roi") but database column is roi_percentage
Fix Applied: Changed to row.get("roi_percentage") in /trends endpoint
Result: ROI Trends graph now shows daily average ROI data properly
2. Channel Performance Graph Issues - Multiple Problems ❌ NEEDS FIXING
Problem A: Frontend Platform Filtering Too Restrictive
Apply to ROI_DASHBOAR...
Problem B: Backend Data Aggregation Logic
Backend correctly aggregates data by platform
But frontend filtering might be too strict
Need to check if platform names in database match exactly
3. Data Flow Analysis for Channel Performance:
Backend Flow:
✅ Fetches data for selected time range (7d, 30d, 90d)
✅ Groups by platform and calculates metrics
✅ Returns aggregated data with avg_roi, impressions, engagement, etc.
Frontend Flow:
✅ Receives data from API
❌ FILTERS OUT DATA with overly strict platform matching
❌ Graph shows empty because filtered data is empty
🎯 IMMEDIATE FIXES NEEDED:
Fix 1: Relax Frontend Platform Filtering
Apply to ROI_DASHBOAR...
Fix 2: Add Debug Logging to Frontend
Apply to ROI_DASHBOAR...
📊 EXPECTED RESULTS AFTER FIXES:
ROI Trends Graph: ✅ Already working - shows daily average ROI
Channel Performance Bar Chart: ✅ Should show ROI bars for each platform
Time Range Changes: ✅ Both graphs should update when dropdown changes
# Testing Instructions for Campaign Performance Updates

## Overview
This document provides step-by-step instructions to test the implemented changes for campaign performance time periods and active spend calculations.

## Prerequisites
1. Backend server is running
2. Database is connected and accessible
3. Frontend is running and connected to backend

## Step 1: Insert Test Data
Run the SQL script `test_campaign_data.sql` in your database to insert sample campaign data:

```sql
-- Run this in your database
\i test_campaign_data.sql
```

This will create:
- 7 test campaigns with different dates and ongoing statuses
- 5 test alerts with different priorities
- 5 test risk patterns with different severities

## Step 2: Test Time Period Logic

### Expected Results for 7-day period (assuming today is 2025-08-17):

**Campaigns to be included:**
- ✅ **Test Campaign 1**: date = 2025-08-10, ongoing = Yes (within 7 days)
- ✅ **Test Campaign 2**: date = 2025-08-01, ongoing = Yes (ongoing, regardless of date)
- ✅ **Test Campaign 3**: date = 2025-08-12, ongoing = No (within 7 days)

**Campaigns to be excluded:**
- ❌ **Test Campaign 4**: date = 2025-08-03, ongoing = No (outside 7 days, not ongoing)
- ❌ **Test Campaign 5**: date = 2025-07-15, ongoing = Yes (outside 7 days, but ongoing - SHOULD be included)
- ❌ **Test Campaign 6**: date = 2025-08-15, ongoing = No (within 7 days, but not ongoing - SHOULD be included)
- ❌ **Test Campaign 7**: date = 2025-08-16, ongoing = Yes (within 7 days, ongoing - SHOULD be included)

**Expected Metrics:**
- Total campaigns: 7 (all campaigns that are either within 7 days OR ongoing)
- Total spend: $14,000 (2000 × 7 campaigns)
- Total conversions: 350 (50 × 7 campaigns)
- Active campaigns: 4 (Campaigns 1, 2, 5, 7)

## Step 3: Test Frontend Dashboard

1. **Navigate to Optimization Dashboard**
   - Go to `/dashboard/optimization`
   - Switch to "Self Optimization" mode

2. **Check Summary Cards**
   - **Active Spend**: Should show $8,000 (sum of ongoing campaigns: 2000 + 2000 + 2000 + 2000)
   - **Budget Utilization**: Should show percentage based on active spend vs active budget
   - **Active Alerts**: Should show 5 with breakdown (Critical: 1, High: 2, Medium: 1, Low: 1)
   - **Risk Patterns**: Should show 5 with breakdown (Critical: 1, High: 2, Medium: 1, Low: 1)

3. **Test Time Period Selection**
   - Go to "Campaign Performance" tab
   - Select different time periods:
     - **7d**: Should show data for campaigns within 7 days + all ongoing
     - **14d**: Should show data for campaigns within 14 days + all ongoing
     - **1m**: Should show data for campaigns within 30 days + all ongoing
     - **3m**: Should show data for campaigns within 90 days + all ongoing
     - **6m**: Should show data for campaigns within 180 days + all ongoing
     - **ytd**: Should show data for campaigns since Jan 1st + all ongoing

4. **Verify Data Changes**
   - Each time period should show different total spend, conversions, avg CTR, and avg CPC
   - The graph should update with different data points based on the selected period

## Step 4: Test Backend API

### Test Campaign Stats Endpoint:
```bash
curl -X GET "http://localhost:8000/api/v1/self-optimization/campaigns/stats?days=7" \
  -H "X-User-ID: your-user-id"
```

**Expected Response:**
```json
{
  "total_campaigns": 7,
  "active_campaigns": 4,
  "total_spend": 14000.0,
  "total_budget": 35000.0,
  "avg_ctr": 1.0,
  "avg_cpc": 1.0,
  "total_conversions": 350,
  "budget_utilization": 40.0
}
```

### Test Dashboard Metrics Endpoint:
```bash
curl -X GET "http://localhost:8000/api/v1/self-optimization/dashboard/metrics" \
  -H "X-User-ID: your-user-id"
```

**Expected Response:**
```json
{
  "spend_today": 8000.0,
  "budget_today": 20000.0,
  "alerts_count": 5,
  "risk_patterns_count": 5,
  "recommendations_count": 0,
  "budget_utilization_pct": 40.0
}
```

### Test Detailed Metrics Endpoint:
```bash
curl -X GET "http://localhost:8000/api/v1/self-optimization/dashboard/metrics/detailed" \
  -H "X-User-ID: your-user-id"
```

**Expected Response:**
```json
{
  "basic_metrics": { ... },
  "risk_breakdown": {
    "critical": 1,
    "high": 2,
    "medium": 1,
    "low": 1
  },
  "alert_breakdown": {
    "critical": 1,
    "high": 2,
    "medium": 1,
    "low": 1
  }
}
```

## Step 5: Debug Console Logs

Check the browser console for:
1. Time period conversion logs
2. API call logs
3. Data processing logs

Look for:
```
Selected time range: 7d, calculated days: 7
Fetching campaign stats for 7 days...
Campaign stats received: {...}
Generated 7 trend data points
```

## Step 6: Verify Graph Updates

1. **Change time period** from 7d to 30d
2. **Observe** that the graph data changes
3. **Check** that metrics (Total Spend, Conversions, Avg CTR, Avg CPC) update accordingly
4. **Verify** that the graph shows the correct number of data points

## Troubleshooting

### If Active Spend shows 0:
- Check if there are campaigns with `ongoing = 'Yes'` in the database
- Verify the SQL query in `get_dashboard_metrics()`

### If Alerts/Risk Patterns show 0:
- Check if there are records in `optimization_alerts` and `risk_patterns` tables
- Verify the `is_read = false` and `resolved = false` conditions

### If Time Period data doesn't change:
- Check the console logs for time period conversion
- Verify the API calls are being made with different `days` parameters
- Check the SQL query in `get_campaign_stats()`

### If Graph doesn't update:
- Check if `performanceTrends` state is being updated
- Verify the data structure matches the expected format
- Check for any JavaScript errors in the console

## Expected Final Results

After all tests, you should see:
- ✅ **Active Spend**: $8,000 (sum of all ongoing campaigns)
- ✅ **Active Alerts**: 5 with breakdown (1 Critical, 2 High, 1 Medium, 1 Low)
- ✅ **Risk Patterns**: 5 with breakdown (1 Critical, 2 High, 1 Medium, 1 Low)
- ✅ **Time Period Selection**: Different data for different periods
- ✅ **Graph Updates**: Chart data changes based on selected time period
- ✅ **API Responses**: Correct data returned for all endpoints

## Summary

The implementation should now correctly:
1. **Calculate Active Spend** from all ongoing campaigns
2. **Show Alert/Risk Breakdowns** with actual counts from the database
3. **Handle Time Periods** by including campaigns within the period OR ongoing campaigns
4. **Update Dashboard Metrics** in real-time when data changes
5. **Provide Consistent Experience** across all time period selections

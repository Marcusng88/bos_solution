# Debugging Guide - Fix Active Spend and Alerts Showing 0

## The Problem
Your dashboard is showing:
- **Active Spend**: $0.00 (should show sum of ongoing campaigns)
- **Budget Utilization**: 0.0% (should show percentage)
- **Active Alerts**: 0 (should show 5)
- **Risk Patterns**: 0 (should show 5)

## Root Causes
1. **No campaign data** in the `campaign_data` table
2. **Wrong user_id** in the test data (alerts and risks are filtered by user_id)
3. **Backend not running** or database connection issues

## Step-by-Step Debugging

### Step 1: Check Your Actual User ID
1. **Open your browser** and go to the dashboard
2. **Open Developer Tools** (F12 or right-click → Inspect)
3. **Go to Console tab**
4. **Look for logs** like:
   ```
   Fetching dashboard metrics for user: user_2abc123def456
   ```
5. **Copy your actual user ID** (it will look like `user_2abc123def456`)

### Step 2: Check Database Content
Run these SQL queries in your database:

```sql
-- Check if there are any campaigns
SELECT COUNT(*) FROM campaign_data;

-- Check ongoing campaigns
SELECT COUNT(*) FROM campaign_data WHERE ongoing = 'Yes';

-- Check alerts and risks
SELECT COUNT(*) FROM optimization_alerts;
SELECT COUNT(*) FROM risk_patterns;
```

### Step 3: Insert Test Data with Correct User ID
1. **Replace `test-user-123`** in `test_campaign_data.sql` with your actual user ID
2. **Run the script** in your database
3. **Restart your backend server**

### Step 4: Verify Data is Loaded
After running the test script, check:

```sql
-- Should show 7 campaigns
SELECT COUNT(*) FROM campaign_data WHERE name LIKE 'Test Campaign%';

-- Should show 4 ongoing campaigns
SELECT COUNT(*) FROM campaign_data WHERE name LIKE 'Test Campaign%' AND ongoing = 'Yes';

-- Should show 5 alerts
SELECT COUNT(*) FROM optimization_alerts WHERE user_id = 'YOUR_ACTUAL_USER_ID';

-- Should show 5 risk patterns
SELECT COUNT(*) FROM risk_patterns WHERE user_id = 'YOUR_ACTUAL_USER_ID';
```

## Expected Results After Fix

### Dashboard Metrics
- **Active Spend**: $8,000 (sum of ongoing campaigns: 2000 × 4)
- **Budget Utilization**: 40.0% (8000/20000 × 100)
- **Active Alerts**: 5
- **Risk Patterns**: 5

### Time Period Data
- **7 days**: Shows 7 data points with realistic values
- **14 days**: Shows 14 data points with realistic values
- **1 month**: Shows 30 data points with realistic values
- **3 months**: Shows 90 data points with realistic values
- **6 months**: Shows 180 data points with realistic values
- **Year to date**: Shows actual days since Jan 1st

## Common Issues and Solutions

### Issue: "No campaigns found"
**Solution**: Run the test data script with your correct user ID

### Issue: "User ID not found"
**Solution**: Check the browser console for the actual user ID being used

### Issue: "Database connection failed"
**Solution**: Ensure your backend server is running and database is accessible

### Issue: "Tables don't exist"
**Solution**: Run the table creation script first:
```bash
cd backend
python create_tables.py
```

## Quick Test Commands

```bash
# 1. Check backend is running
curl http://localhost:8000/health

# 2. Check database connection
cd backend
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"

# 3. Insert test data (replace USER_ID with your actual ID)
psql -d your_database -f test_campaign_data.sql
```

## Summary
The main issue is likely that:
1. **No campaign data exists** in your database, OR
2. **Wrong user ID** is being used in the test data

Fix this by:
1. Finding your actual Clerk user ID from the browser console
2. Updating the test data script with the correct user ID
3. Running the script and restarting the backend
4. Checking that the data appears in your dashboard

After these steps, you should see:
- ✅ Active Spend: $8,000
- ✅ Budget Utilization: 40.0%
- ✅ Active Alerts: 5
- ✅ Risk Patterns: 5
- ✅ Time periods showing different data
- ✅ Graphs displaying realistic values for all periods

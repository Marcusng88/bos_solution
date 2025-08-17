-- Test script to check active spend calculation
-- This will help debug why active spend is showing 0

-- 1. Check what's in the campaign_data table
SELECT 
    name,
    ongoing,
    spend,
    budget,
    date
FROM campaign_data 
ORDER BY date DESC;

-- 2. Check ongoing campaigns specifically
SELECT 
    COUNT(*) as total_ongoing_campaigns,
    COALESCE(SUM(spend), 0) as total_ongoing_spend,
    COALESCE(SUM(budget), 0) as total_ongoing_budget
FROM campaign_data 
WHERE ongoing = 'Yes';

-- 3. Check all campaigns regardless of status
SELECT 
    COUNT(*) as total_campaigns,
    COALESCE(SUM(spend), 0) as total_spend,
    COALESCE(SUM(budget), 0) as total_budget
FROM campaign_data;

-- 4. Check if there are any campaigns at all
SELECT COUNT(*) as total_records FROM campaign_data;

-- 5. Check the ongoing field values
SELECT DISTINCT ongoing, COUNT(*) as count
FROM campaign_data 
GROUP BY ongoing;

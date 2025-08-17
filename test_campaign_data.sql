-- Sample campaign data to test time period logic
-- This data represents the example scenario described by the user

-- Clear existing test data
DELETE FROM campaign_data WHERE name LIKE 'Test Campaign%';
DELETE FROM optimization_alerts WHERE campaign_name LIKE 'Test Campaign%';
DELETE FROM risk_patterns WHERE campaign_name LIKE 'Test Campaign%';

-- Insert test campaign data
INSERT INTO campaign_data (name, date, impressions, clicks, ctr, cpc, spend, budget, conversions, net_profit, ongoing) VALUES
-- Campaign 1: Started on 2025-08-10, ongoing = Yes (should be included in 7-day view)
('Test Campaign 1', '2025-08-10', 1000, 100, 1.0, 1.0, 2000.00, 5000.00, 50, 1000.00, 'Yes'),

-- Campaign 2: Started on 2025-08-01, ongoing = Yes (should be included in 7-day view because it's ongoing)
('Test Campaign 2', '2025-08-01', 1000, 100, 1.0, 1.0, 2000.00, 5000.00, 50, 1000.00, 'Yes'),

-- Campaign 3: Started on 2025-08-12, ongoing = No (should be included in 7-day view because date >= 2025-08-10)
('Test Campaign 3', '2025-08-12', 1000, 100, 1.0, 1.0, 2000.00, 5000.00, 50, 1000.00, 'No'),

-- Campaign 4: Started on 2025-08-03, ongoing = No (should NOT be included in 7-day view because date < 2025-08-10)
('Test Campaign 4', '2025-08-03', 1000, 100, 1.0, 1.0, 2000.00, 5000.00, 50, 1000.00, 'No'),

-- Additional campaigns for testing different time periods
('Test Campaign 5', '2025-07-15', 1000, 100, 1.0, 1.0, 2000.00, 5000.00, 50, 1000.00, 'Yes'), -- Ongoing but old
('Test Campaign 6', '2025-08-15', 1000, 100, 1.0, 1.0, 2000.00, 5000.00, 50, 1000.00, 'No'),  -- Recent but not ongoing
('Test Campaign 7', '2025-08-16', 1000, 100, 1.0, 1.0, 2000.00, 5000.00, 50, 1000.00, 'Yes'); -- Recent and ongoing

-- Insert some test alerts and risk patterns 
-- IMPORTANT: Replace 'test-user-123' with your actual Clerk user ID from the frontend
-- You can find this in the browser console or network tab when the app makes API calls
INSERT INTO optimization_alerts (id, user_id, campaign_name, alert_type, priority, title, message, is_read) VALUES
(gen_random_uuid(), 'test-user-123', 'Test Campaign 1', 'overspend', 'critical', 'Critical Overspend Alert', 'Campaign is overspending', false),
(gen_random_uuid(), 'test-user-123', 'Test Campaign 2', 'low_performance', 'high', 'High Priority Alert', 'Low performance detected', false),
(gen_random_uuid(), 'test-user-123', 'Test Campaign 3', 'budget_warning', 'medium', 'Medium Priority Alert', 'Budget utilization high', false),
(gen_random_uuid(), 'test-user-123', 'Test Campaign 4', 'ctr_drop', 'low', 'Low Priority Alert', 'CTR has dropped', false),
(gen_random_uuid(), 'test-user-123', 'Test Campaign 5', 'conversion_issue', 'high', 'High Priority Alert', 'Conversion rate low', false);

INSERT INTO risk_patterns (id, user_id, campaign_name, pattern_type, severity, detected_at, resolved) VALUES
(gen_random_uuid(), 'test-user-123', 'Test Campaign 1', 'spending_spike', 'critical', NOW(), false),
(gen_random_uuid(), 'test-user-123', 'Test Campaign 2', 'low_ctr', 'high', NOW(), false),
(gen_random_uuid(), 'test-user-123', 'Test Campaign 3', 'high_cpc', 'medium', NOW(), false),
(gen_random_uuid(), 'test-user-123', 'Test Campaign 4', 'budget_utilization', 'low', NOW(), false),
(gen_random_uuid(), 'test-user-123', 'Test Campaign 5', 'audience_shrink', 'high', NOW(), false);

-- Expected results for 7-day period (assuming today is 2025-08-17):
-- Total campaigns: 7 (all campaigns that are either within 7 days OR ongoing)
-- Total spend: $14,000 (2000 × 7 campaigns)
-- Total conversions: 350 (50 × 7 campaigns)
-- Active campaigns: 4 (Campaigns 1, 2, 5, 7)
-- Alerts: 5 unread
-- Risk patterns: 5 unresolved

-- IMPORTANT: After running this script, you need to:
-- 1. Replace 'test-user-123' with your actual Clerk user ID
-- 2. Restart your backend server to ensure the new data is loaded
-- 3. Check the browser console for the user ID being used in API calls

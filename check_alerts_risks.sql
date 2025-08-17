-- Check if there are any alerts or risk patterns in the database
-- This will help us understand why they're showing 0

-- Check if the tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('optimization_alerts', 'risk_patterns');

-- Check if there are any records in these tables
SELECT 'optimization_alerts' as table_name, COUNT(*) as record_count
FROM optimization_alerts
UNION ALL
SELECT 'risk_patterns' as table_name, COUNT(*) as record_count
FROM risk_patterns;

-- Check the structure of these tables if they exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'optimization_alerts'
ORDER BY ordinal_position;

SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'risk_patterns'
ORDER BY ordinal_position;

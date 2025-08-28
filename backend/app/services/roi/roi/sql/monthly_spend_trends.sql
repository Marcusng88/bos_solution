-- Monthly spend trends for a given year
-- params: :user_id, :year
SELECT 
  EXTRACT(MONTH FROM update_timestamp) AS month,
  platform,
  SUM(ad_spend)                         AS spend,
  SUM(revenue_generated)                AS revenue,
  AVG(roi_percentage)                   AS avg_roi
FROM roi_metrics
WHERE user_id = :user_id
  AND EXTRACT(YEAR FROM update_timestamp) = :year
GROUP BY EXTRACT(MONTH FROM update_timestamp), platform
ORDER BY month, platform;



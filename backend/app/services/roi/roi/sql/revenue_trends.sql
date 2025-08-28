-- Revenue trends per bucket for a user
-- params: :user_id, :start, :end, :bucket
SELECT 
  date_trunc(:bucket, update_timestamp) AS time_period,
  SUM(revenue_generated)                AS revenue,
  COUNT(*)                              AS posts,
  AVG(roi_percentage)                   AS avg_roi
FROM roi_metrics
WHERE user_id = :user_id
  AND update_timestamp BETWEEN :start AND :end
GROUP BY 1
ORDER BY 1;



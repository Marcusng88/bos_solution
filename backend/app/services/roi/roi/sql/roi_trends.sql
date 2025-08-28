-- ROI trends over days
-- params: :user_id, :start, :end
SELECT 
  DATE_TRUNC('day', update_timestamp) AS date,
  AVG(roi_percentage)                 AS avg_roi,
  COUNT(*)                            AS data_points,
  SUM(revenue_generated)              AS daily_revenue,
  SUM(ad_spend)                       AS daily_spend
FROM roi_metrics
WHERE user_id = :user_id
  AND update_timestamp BETWEEN :start AND :end
GROUP BY 1
ORDER BY 1;



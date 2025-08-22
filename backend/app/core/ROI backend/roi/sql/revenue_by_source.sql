-- Revenue by platform for a user within time range
-- params: :user_id, :start, :end
SELECT 
  platform,
  SUM(revenue_generated)                                AS total_revenue,
  COUNT(*)                                              AS post_count,
  AVG(revenue_generated)                                AS avg_revenue_per_post,
  CASE WHEN SUM(ad_spend) > 0 THEN SUM(revenue_generated) / SUM(ad_spend) ELSE 0 END AS revenue_multiplier
FROM roi_metrics
WHERE user_id = :user_id
  AND update_timestamp BETWEEN :start AND :end
GROUP BY platform
ORDER BY total_revenue DESC;



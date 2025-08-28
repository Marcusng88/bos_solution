-- Customer Lifetime Value approximation
-- params: :user_id, :start, :end
SELECT 
  AVG(revenue_generated)                                  AS avg_revenue_per_customer,
  COUNT(DISTINCT COALESCE(post_id, id::text))             AS unique_customers,
  CASE WHEN COUNT(DISTINCT COALESCE(post_id, id::text)) > 0
       THEN SUM(revenue_generated) / COUNT(DISTINCT COALESCE(post_id, id::text))
       ELSE 0 END                                         AS clv,
  CASE WHEN SUM(ad_spend) > 0 THEN SUM(revenue_generated) / SUM(ad_spend) ELSE 0 END AS revenue_multiplier
FROM roi_metrics
WHERE user_id = :user_id
  AND update_timestamp BETWEEN :start AND :end
  AND revenue_generated > 0;



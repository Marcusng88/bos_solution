-- Customer Acquisition Cost
-- params: :user_id, :start, :end
SELECT 
  CASE WHEN COUNT(DISTINCT COALESCE(post_id, id::text)) > 0
       THEN SUM(ad_spend) / COUNT(DISTINCT COALESCE(post_id, id::text))
       ELSE 0 END AS cac,
  AVG(cost_per_click)          AS avg_cpc,
  AVG(cost_per_impression)     AS avg_cpm
FROM roi_metrics
WHERE user_id = :user_id
  AND update_timestamp BETWEEN :start AND :end
  AND ad_spend > 0;



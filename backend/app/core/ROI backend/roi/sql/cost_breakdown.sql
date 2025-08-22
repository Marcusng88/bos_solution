-- Cost breakdown by platform for a user within time range
-- params: :user_id, :start, :end
SELECT 
  platform,
  SUM(ad_spend)                                   AS total_spend,
  AVG(cost_per_click)                             AS avg_cpc,
  AVG(cost_per_impression)                        AS avg_cpm,
  COUNT(*)                                        AS campaigns,
  CASE WHEN SUM(clicks) > 0 THEN SUM(ad_spend) / SUM(clicks) ELSE NULL END AS effective_cpc
FROM roi_metrics
WHERE user_id = :user_id
  AND update_timestamp BETWEEN :start AND :end
GROUP BY platform
ORDER BY total_spend DESC;



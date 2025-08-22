-- Channel performance by platform for a user
-- params: :user_id, :start, :end
SELECT 
  platform,
  SUM(revenue_generated)                            AS revenue,
  SUM(ad_spend)                                     AS spend,
  AVG(roi_percentage)                               AS avg_roi,
  AVG(roas_ratio)                                   AS avg_roas,
  SUM(views)                                        AS impressions,
  SUM(likes + comments + shares)                    AS engagement,
  COUNT(*)                                          AS posts,
  SUM(clicks)                                       AS total_clicks
FROM roi_metrics
WHERE user_id = :user_id
  AND update_timestamp BETWEEN :start AND :end
GROUP BY platform
ORDER BY avg_roi DESC;



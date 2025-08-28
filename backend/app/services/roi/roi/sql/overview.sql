-- Total ROI overview for a user within time range
-- params: :user_id, :start, :end
SELECT 
  COALESCE(SUM(revenue_generated), 0)               AS total_revenue,
  COALESCE(SUM(ad_spend), 0)                        AS total_spend,
  COALESCE(SUM(revenue_generated - ad_spend), 0)    AS total_profit,
  CASE WHEN SUM(ad_spend) > 0 
       THEN ((SUM(revenue_generated) - SUM(ad_spend)) / NULLIF(SUM(ad_spend),0)) * 100
       ELSE 0 END                                    AS overall_roi,
  COALESCE(SUM(views), 0)                           AS total_impressions,
  COALESCE(SUM(likes + comments + shares), 0)       AS total_engagement,
  COUNT(*)                                          AS total_posts
FROM roi_metrics
WHERE user_id = :user_id
  AND update_timestamp BETWEEN :start AND :end;



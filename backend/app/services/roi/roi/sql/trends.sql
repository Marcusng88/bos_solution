-- ROI trends per bucket
-- params: :user_id, :start, :end, :bucket ('hour'|'day')
SELECT
  date_trunc(:bucket, update_timestamp) AS ts,
  AVG(
    CASE WHEN ad_spend > 0
      THEN ((revenue_generated - ad_spend) / ad_spend) * 100
      ELSE NULL
    END
  ) AS roi
FROM roi_metrics
WHERE user_id = :user_id
  AND update_timestamp BETWEEN :start AND :end
GROUP BY 1
ORDER BY 1;



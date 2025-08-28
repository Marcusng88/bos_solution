-- Enforce monotonic non-decreasing metrics per user+platform over time

WITH ranked AS (
  SELECT
    id,
    MAX(views)    OVER (PARTITION BY user_id, platform ORDER BY update_timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS v_max,
    MAX(likes)    OVER (PARTITION BY user_id, platform ORDER BY update_timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS l_max,
    MAX(comments) OVER (PARTITION BY user_id, platform ORDER BY update_timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS c_max,
    MAX(shares)   OVER (PARTITION BY user_id, platform ORDER BY update_timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS s_max,
    MAX(clicks)   OVER (PARTITION BY user_id, platform ORDER BY update_timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS clk_max
  FROM roi_metrics
)
UPDATE roi_metrics m
SET views = r.v_max,
    likes = r.l_max,
    comments = r.c_max,
    shares = r.s_max,
    clicks = r.clk_max
FROM ranked r
WHERE m.id = r.id;



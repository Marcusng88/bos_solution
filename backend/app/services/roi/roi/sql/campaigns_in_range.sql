-- Campaign markers within date range
-- params: :user_id, :start (date), :end (date)
SELECT id, name, date
FROM campaign_with_user_id
WHERE user_id = :user_id
  AND date BETWEEN :start AND :end
ORDER BY date ASC;



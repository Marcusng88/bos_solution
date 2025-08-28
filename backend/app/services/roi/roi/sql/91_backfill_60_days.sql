-- Optional: 60-day historical backfill with cumulative growth
-- Behavior mirrors 90_backfill_7_days but over 60 days.
DO $$
DECLARE
  uid TEXT := COALESCE(current_setting('app.uid', true), 'USER_CLERK_ID_HERE');
  d DATE;
  c1 INTEGER;
  c2 INTEGER;
  p TEXT;
  v INTEGER;
  l INTEGER;
  cm INTEGER;
  sh INTEGER;
  cl INTEGER;
  spend NUMERIC;
  rev NUMERIC;
BEGIN
  IF uid = 'USER_CLERK_ID_HERE' THEN
    SELECT clerk_id INTO uid FROM users LIMIT 1;
    IF uid IS NULL THEN
      uid := 'demo_user';
    END IF;
  END IF;

  INSERT INTO users (clerk_id) VALUES (uid) ON CONFLICT (clerk_id) DO NOTHING;

  -- two campaigns within the last 60 days
  INSERT INTO campaign_with_user_id (user_id, name, date, impressions, clicks, ctr, cpc, spend, budget, conversions, net_profit, ongoing)
  VALUES (uid, 'Backfill Campaign A', (CURRENT_DATE - 45), 0,0,0,0,0,0,0,0,'true') RETURNING id INTO c1;

  INSERT INTO campaign_with_user_id (user_id, name, date, impressions, clicks, ctr, cpc, spend, budget, conversions, net_profit, ongoing)
  VALUES (uid, 'Backfill Campaign B', (CURRENT_DATE - 15), 0,0,0,0,0,0,0,0,'true') RETURNING id INTO c2;

  FOR p IN SELECT unnest(ARRAY['facebook','instagram','youtube']) LOOP
    v := 80; l := 8; cm := 4; sh := 2; cl := 6;
    FOR d IN SELECT generate_series(CURRENT_DATE - 59, CURRENT_DATE, '1 day')::date LOOP
      v := ceil(v * (1.05 + (random()*1.80)));
      l := ceil(l * (1.03 + (random()*0.70)));
      cm := ceil(cm * (1.02 + (random()*0.60)));
      sh := ceil(sh * (1.03 + (random()*1.00)));
      cl := ceil(cl * (1.03 + (random()*0.85)));

      spend := round(((cl * (0.5 + random()*2.5)) + (v * (3 + random()*12) / 1000))::numeric, 2);
      rev := round((spend * (1.5 + random()*2.5))::numeric, 2);

      INSERT INTO roi_metrics (
        user_id, platform, campaign_id, post_id, content_type, content_category,
        views, likes, comments, shares, saves, clicks,
        ad_spend, revenue_generated, cost_per_click, cost_per_impression,
        roi_percentage, roas_ratio, update_timestamp
      )
      VALUES (
        uid, p, CASE WHEN d <= CURRENT_DATE - 20 THEN c1 ELSE c2 END, NULL, 'video', 'generic',
        v, l, cm, sh, 1, cl,
        spend, rev,
        round((spend / NULLIF(cl,0))::numeric, 2),
        round(((spend / NULLIF(v,0)))::numeric, 4),
        CASE WHEN spend>0 THEN ((rev - spend)/spend)*100 ELSE 0 END,
        CASE WHEN spend>0 THEN (rev/spend) ELSE 0 END,
        (d + time '12:00')
      );
    END LOOP;
  END LOOP;
END$$;



-- One-Time 7-Day Mock Backfill
-- Replace USER_CLERK_ID_HERE before running, or set via psql variable: \set uid 'YOUR_ID'

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
  -- Resolve uid: if placeholder, try to pick any existing user; else create a demo user
  IF uid = 'USER_CLERK_ID_HERE' THEN
    SELECT clerk_id INTO uid FROM users LIMIT 1;
    IF uid IS NULL THEN
      uid := 'demo_user';
    END IF;
  END IF;

  -- Ensure the user exists to satisfy FK constraints
  INSERT INTO users (clerk_id)
  VALUES (uid)
  ON CONFLICT (clerk_id) DO NOTHING;

  -- Create two campaigns in the last 7 days
  INSERT INTO campaign_with_user_id (user_id, name, date, impressions, clicks, ctr, cpc, spend, budget, conversions, net_profit, ongoing)
  VALUES (uid, 'Spring Promo', (CURRENT_DATE - 6), 0,0,0,0,0,0,0,0,'true')
  RETURNING id INTO c1;

  INSERT INTO campaign_with_user_id (user_id, name, date, impressions, clicks, ctr, cpc, spend, budget, conversions, net_profit, ongoing)
  VALUES (uid, 'Video Launch', (CURRENT_DATE - 3), 0,0,0,0,0,0,0,0,'true')
  RETURNING id INTO c2;

  -- For each of the last 7 days, insert one ROI snapshot per platform at noon
  -- Use cumulative growth (non-decreasing) per platform
  FOR p IN SELECT unnest(ARRAY['facebook','instagram','youtube']) LOOP
    v := 100; l := 10; cm := 5; sh := 2; cl := 8; -- starting values per platform
    FOR d IN SELECT generate_series(CURRENT_DATE - 6, CURRENT_DATE, '1 day')::date LOOP
      -- multipliers: ensure >= 1.0 for non-decreasing
      v := ceil(v * (1.10 + (random()*1.20)));  -- 1.10x - 2.30x
      l := ceil(l * (1.05 + (random()*0.70)));  -- 1.05x - 1.75x
      cm := ceil(cm * (1.02 + (random()*0.60)));-- 1.02x - 1.62x
      sh := ceil(sh * (1.05 + (random()*1.00)));-- 1.05x - 2.05x
      cl := ceil(cl * (1.05 + (random()*0.85)));-- 1.05x - 1.90x

      -- basic costs; cpc/cpm vary by platform
      spend := round(((cl * (0.5 + random()*2.5)) + (v * (3 + random()*12) / 1000))::numeric, 2);
      rev := round((spend * (1.5 + random()*2.5))::numeric, 2);

      INSERT INTO roi_metrics (
        user_id, platform, campaign_id, post_id, content_type, content_category,
        views, likes, comments, shares, saves, clicks,
        ad_spend, revenue_generated, cost_per_click, cost_per_impression,
        roi_percentage, roas_ratio, update_timestamp
      )
      VALUES (
        uid, p, CASE WHEN d <= CURRENT_DATE - 3 THEN c1 ELSE c2 END, NULL, 'video', 'generic',
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



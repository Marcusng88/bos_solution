-- ROI Schema (campaign_with_user_id, roi_metrics, platform_metrics)
-- This file is generated per ROI_IMPLEMENTATION_PLAN.md Phase 1

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1) Campaign table with user_id
CREATE TABLE IF NOT EXISTS campaign_with_user_id (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    date DATE,
    impressions INTEGER,
    clicks INTEGER,
    ctr DOUBLE PRECISION,
    cpc DOUBLE PRECISION,
    spend DOUBLE PRECISION,
    budget DOUBLE PRECISION,
    conversions INTEGER,
    net_profit DOUBLE PRECISION,
    ongoing VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2) Primary ROI metrics table
CREATE TABLE IF NOT EXISTS roi_metrics (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    campaign_id INTEGER REFERENCES campaign_with_user_id(id),
    post_id VARCHAR(255),
    content_type VARCHAR(50),
    content_category VARCHAR(100),
    views INTEGER DEFAULT 1,
    likes INTEGER DEFAULT 1,
    comments INTEGER DEFAULT 1,
    shares INTEGER DEFAULT 1,
    saves INTEGER DEFAULT 1,
    clicks INTEGER DEFAULT 1,
    ad_spend DECIMAL(10,2) DEFAULT 0.00,
    revenue_generated DECIMAL(10,2) DEFAULT 0.00,
    cost_per_click DECIMAL(8,2) DEFAULT 0.00,
    cost_per_impression DECIMAL(8,4) DEFAULT 0.00,
    roi_percentage DECIMAL(8,2) DEFAULT 0.00,
    roas_ratio DECIMAL(8,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    posted_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3) Platform metrics table with JSONB metrics
CREATE TABLE IF NOT EXISTS platform_metrics (
    id SERIAL PRIMARY KEY,
    roi_metric_id INTEGER,
    user_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metrics JSONB NOT NULL DEFAULT '{}',
    engagement_rate DECIMAL(5,2) DEFAULT 1.00,
    virality_score DECIMAL(5,2) DEFAULT 1.00
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_campaign_with_user_id_user_id ON campaign_with_user_id(user_id);
CREATE INDEX IF NOT EXISTS idx_campaign_with_user_id_date ON campaign_with_user_id(date);
CREATE INDEX IF NOT EXISTS idx_roi_metrics_user_id ON roi_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_roi_metrics_platform ON roi_metrics(platform);
CREATE INDEX IF NOT EXISTS idx_roi_metrics_campaign_id ON roi_metrics(campaign_id);
CREATE INDEX IF NOT EXISTS idx_roi_metrics_timestamp ON roi_metrics(update_timestamp);
CREATE INDEX IF NOT EXISTS idx_roi_metrics_content_type ON roi_metrics(content_type);
CREATE INDEX IF NOT EXISTS idx_roi_metrics_user_platform_time ON roi_metrics(user_id, platform, update_timestamp);
CREATE INDEX IF NOT EXISTS idx_roi_metrics_user_time ON roi_metrics(user_id, update_timestamp);
CREATE INDEX IF NOT EXISTS idx_platform_metrics_roi_id ON platform_metrics(roi_metric_id);
CREATE INDEX IF NOT EXISTS idx_platform_metrics_platform ON platform_metrics(platform);
CREATE INDEX IF NOT EXISTS idx_platform_metrics_timestamp ON platform_metrics(update_timestamp);
CREATE INDEX IF NOT EXISTS idx_platform_metrics_jsonb ON platform_metrics USING GIN (metrics);
CREATE INDEX IF NOT EXISTS idx_platform_metrics_user_platform ON platform_metrics(user_id, platform);

-- Optional FKs to users by clerk_id (assumes public.users exists)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema='public' AND table_name='users' AND column_name='clerk_id'
    ) THEN
        -- ROI metrics -> users
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name='fk_roi_metrics_user' AND table_name='roi_metrics'
        ) THEN
            ALTER TABLE roi_metrics 
            ADD CONSTRAINT fk_roi_metrics_user FOREIGN KEY (user_id) REFERENCES users(clerk_id) ON DELETE CASCADE;
        END IF;

        -- Campaign -> users
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name='fk_campaign_user' AND table_name='campaign_with_user_id'
        ) THEN
            ALTER TABLE campaign_with_user_id 
            ADD CONSTRAINT fk_campaign_user FOREIGN KEY (user_id) REFERENCES users(clerk_id) ON DELETE CASCADE;
        END IF;

        -- Platform metrics -> users
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name='fk_platform_metrics_user' AND table_name='platform_metrics'
        ) THEN
            ALTER TABLE platform_metrics 
            ADD CONSTRAINT fk_platform_metrics_user FOREIGN KEY (user_id) REFERENCES users(clerk_id) ON DELETE CASCADE;
        END IF;
    END IF;
END $$;

-- Add comments for documentation
COMMENT ON TABLE campaign_with_user_id IS 'Campaign data with user isolation via user_id';
COMMENT ON TABLE roi_metrics IS 'Core ROI metrics per user, platform, and campaign';
COMMENT ON TABLE platform_metrics IS 'Extended platform-specific metrics with JSONB flexibility';
COMMENT ON COLUMN roi_metrics.user_id IS 'References users.clerk_id for user isolation';
COMMENT ON COLUMN roi_metrics.update_timestamp IS 'When this metric row was last updated (used for growth calculations)';
COMMENT ON COLUMN platform_metrics.metrics IS 'Flexible JSONB storage for platform-specific metrics';

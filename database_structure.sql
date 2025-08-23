-- =====================================================
-- BOS Solution Database Structure
-- Generated on: 2025-01-27
-- Project: bos_solution (zktakfluvzuxhwwvccqs)
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" SCHEMA extensions;
CREATE EXTENSION IF NOT EXISTS "pgcrypto" SCHEMA extensions;
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" SCHEMA extensions;
CREATE EXTENSION IF NOT EXISTS "pg_graphql" SCHEMA graphql;
CREATE EXTENSION IF NOT EXISTS "supabase_vault" SCHEMA vault;
CREATE EXTENSION IF NOT EXISTS "pg_trgm" SCHEMA public;

-- =====================================================
-- ENUM TYPES
-- =====================================================

-- Social media platform enum
CREATE TYPE social_media_platform AS ENUM (
    'instagram',
    'facebook',
    'twitter',
    'linkedin',
    'tiktok',
    'youtube',
    'other',
    'website',
    'browser'
);

-- Monitoring status enum
CREATE TYPE monitoring_status AS ENUM (
    'active',
    'paused',
    'error'
);

-- Alert priority enum
CREATE TYPE alert_priority AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

-- Risk severity enum
CREATE TYPE risk_severity AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

-- Recommendation priority enum
CREATE TYPE recommendation_priority AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

-- =====================================================
-- TABLES
-- =====================================================

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_id VARCHAR NOT NULL UNIQUE,
    email VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    profile_image_url VARCHAR,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    onboarding_complete BOOLEAN DEFAULT false
);

-- User preferences table
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR NOT NULL UNIQUE,
    industry VARCHAR NOT NULL,
    company_size VARCHAR NOT NULL CHECK (company_size IN ('1-10', '11-50', '51-200', '201-500', '500+')),
    marketing_goals TEXT[] NOT NULL,
    monthly_budget VARCHAR NOT NULL CHECK (monthly_budget IN ('$0 - $1,000', '$1,000 - $5,000', '$5,000 - $10,000', '$10,000 - $25,000', '$25,000+')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (user_id) REFERENCES users(clerk_id)
);

-- Social media accounts table
CREATE TABLE social_media_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR NOT NULL,
    platform social_media_platform NOT NULL,
    account_name VARCHAR NOT NULL,
    username VARCHAR,
    profile_picture_url TEXT,
    account_id VARCHAR,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    is_test_account BOOLEAN DEFAULT false,
    permissions JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (user_id) REFERENCES users(clerk_id)
);

-- Competitors table
CREATE TABLE competitors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL,
    description TEXT,
    website_url VARCHAR,
    social_media_handles JSONB,
    industry VARCHAR,
    status monitoring_status DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    last_scan_at TIMESTAMPTZ,
    scan_frequency_minutes INTEGER DEFAULT 1440 CHECK (scan_frequency_minutes >= 15),
    user_id VARCHAR NOT NULL,
    platforms TEXT[] DEFAULT '{}',
    FOREIGN KEY (user_id) REFERENCES users(clerk_id)
);

-- Monitoring data table
CREATE TABLE monitoring_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_id UUID NOT NULL,
    platform social_media_platform NOT NULL,
    post_id VARCHAR,
    post_url VARCHAR,
    content_text TEXT,
    content_hash VARCHAR,
    media_urls JSONB,
    engagement_metrics JSONB,
    author_username VARCHAR,
    author_display_name VARCHAR,
    author_avatar_url VARCHAR,
    post_type VARCHAR,
    language VARCHAR,
    sentiment_score NUMERIC CHECK (sentiment_score >= -1.0 AND sentiment_score <= 1.0),
    detected_at TIMESTAMPTZ DEFAULT now(),
    posted_at TIMESTAMPTZ,
    is_new_post BOOLEAN DEFAULT true,
    is_content_change BOOLEAN DEFAULT false,
    previous_content_hash VARCHAR,
    FOREIGN KEY (competitor_id) REFERENCES competitors(id)
);

-- User monitoring settings table
CREATE TABLE user_monitoring_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    global_monitoring_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    user_id_new UUID,
    user_id VARCHAR UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(clerk_id)
);

-- Monitoring alerts table
CREATE TABLE monitoring_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_id UUID,
    monitoring_data_id UUID,
    alert_type VARCHAR NOT NULL,
    priority alert_priority DEFAULT 'medium',
    title VARCHAR NOT NULL,
    message TEXT NOT NULL,
    alert_metadata JSONB,
    is_read BOOLEAN DEFAULT false,
    is_dismissed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    read_at TIMESTAMPTZ,
    dismissed_at TIMESTAMPTZ,
    user_id VARCHAR NOT NULL,
    FOREIGN KEY (competitor_id) REFERENCES competitors(id),
    FOREIGN KEY (monitoring_data_id) REFERENCES monitoring_data(id),
    FOREIGN KEY (user_id) REFERENCES users(clerk_id)
);

-- Competitor monitoring status table
CREATE TABLE competitor_monitoring_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_id UUID NOT NULL,
    last_successful_scan TIMESTAMPTZ,
    last_failed_scan TIMESTAMPTZ,
    scan_error_message TEXT,
    consecutive_failures INTEGER DEFAULT 0,
    is_scanning BOOLEAN DEFAULT false,
    scan_started_at TIMESTAMPTZ,
    next_scheduled_scan TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (competitor_id) REFERENCES competitors(id)
);

-- Campaign data table
CREATE TABLE campaign_data (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    date DATE,
    impressions INTEGER,
    clicks INTEGER,
    ctr DOUBLE PRECISION,
    cpc DOUBLE PRECISION,
    spend DOUBLE PRECISION,
    budget DOUBLE PRECISION,
    conversions INTEGER,
    net_profit DOUBLE PRECISION,
    ongoing VARCHAR
);

-- Optimization alerts table
CREATE TABLE optimization_alerts (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    campaign_name VARCHAR,
    alert_type VARCHAR NOT NULL,
    priority alert_priority,
    title VARCHAR NOT NULL,
    message TEXT NOT NULL,
    recommendation TEXT,
    alert_data TEXT,
    is_read BOOLEAN,
    is_dismissed BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT now(),
    read_at TIMESTAMPTZ,
    dismissed_at TIMESTAMPTZ
);

-- Risk patterns table
CREATE TABLE risk_patterns (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    campaign_name VARCHAR NOT NULL,
    pattern_type VARCHAR NOT NULL,
    severity risk_severity,
    detected_at TIMESTAMPTZ DEFAULT now(),
    pattern_data TEXT,
    resolved BOOLEAN,
    resolved_at TIMESTAMPTZ
);

-- Optimization recommendations table
CREATE TABLE optimization_recommendations (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    campaign_name VARCHAR,
    recommendation_type VARCHAR NOT NULL,
    priority recommendation_priority,
    title VARCHAR NOT NULL,
    description TEXT NOT NULL,
    action_items TEXT,
    potential_impact TEXT,
    confidence_score NUMERIC,
    is_applied BOOLEAN,
    applied_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Content uploads table
CREATE TABLE content_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR NOT NULL,
    file_name VARCHAR,
    file_url VARCHAR,
    file_size INTEGER,
    mime_type VARCHAR,
    platform VARCHAR,
    status VARCHAR DEFAULT 'pending',
    upload_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (user_id) REFERENCES users(clerk_id)
);

-- Content templates table
CREATE TABLE content_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    description TEXT,
    template_type VARCHAR,
    platforms TEXT[] DEFAULT '{}',
    template_data JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (user_id) REFERENCES users(clerk_id)
);

-- Channels table
CREATE TABLE channels (
    channel_id TEXT PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    channel_title TEXT NOT NULL,
    total_subscribers INTEGER DEFAULT 0,
    total_videos INTEGER DEFAULT 0,
    total_views BIGINT DEFAULT 0,
    channel_created TIMESTAMPTZ,
    estimated_monthly_revenue NUMERIC,
    estimated_annual_revenue NUMERIC,
    revenue_per_subscriber NUMERIC,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (user_id) REFERENCES users(clerk_id)
);

-- Videos table
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id TEXT NOT NULL UNIQUE,
    user_id VARCHAR NOT NULL,
    title TEXT,
    published_at TIMESTAMPTZ,
    views BIGINT,
    likes INTEGER,
    comments INTEGER,
    engagement_rate NUMERIC CHECK (engagement_rate IS NULL OR (engagement_rate >= 0 AND engagement_rate <= 1)),
    watch_time_hours NUMERIC,
    duration_seconds INTEGER,
    roi_score NUMERIC,
    tags TEXT[],
    channel_id TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (user_id) REFERENCES users(clerk_id),
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
);

-- ROI analytics table
CREATE TABLE roi_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR NOT NULL,
    channel_id TEXT NOT NULL,
    analysis_period TEXT NOT NULL,
    cutoff_time TIMESTAMPTZ,
    generated_at TIMESTAMPTZ DEFAULT now(),
    total_views_period BIGINT,
    total_likes_period BIGINT,
    total_comments_period BIGINT,
    avg_engagement_rate NUMERIC,
    optimal_video_length NUMERIC,
    best_performing_tags JSONB,
    recommendations JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (user_id) REFERENCES users(clerk_id),
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
);

-- User posts table
CREATE TABLE user_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR NOT NULL,
    title VARCHAR,
    content_text TEXT NOT NULL,
    media_files JSONB,
    hashtags TEXT[],
    mentions TEXT[],
    is_ai_generated BOOLEAN DEFAULT false,
    ai_prompt TEXT,
    ai_model_used VARCHAR,
    competitor_sources JSONB,
    ai_analysis_metadata JSONB,
    analyzed_competitors_data JSONB,
    content_themes TEXT[],
    suggested_improvements TEXT[],
    post_status VARCHAR DEFAULT 'draft' CHECK (post_status IN ('draft', 'ai_suggested', 'user_edited', 'scheduled', 'published', 'failed')),
    target_platforms TEXT[] NOT NULL CHECK (array_length(target_platforms, 1) > 0),
    scheduled_for TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    platform_post_ids JSONB,
    platform_urls JSONB,
    publishing_errors JSONB,
    user_edits_count INTEGER DEFAULT 0,
    user_feedback VARCHAR CHECK (user_feedback IS NULL OR user_feedback IN ('positive', 'negative', 'neutral')),
    user_rating INTEGER CHECK (user_rating IS NULL OR (user_rating >= 1 AND user_rating <= 5)),
    engagement_metrics JSONB,
    roi_metrics JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    edited_at TIMESTAMPTZ,
    FOREIGN KEY (user_id) REFERENCES users(clerk_id)
);

-- AI content suggestions table
CREATE TABLE ai_content_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_post_id UUID NOT NULL,
    user_id VARCHAR NOT NULL,
    suggestion_version INTEGER NOT NULL CHECK (suggestion_version > 0),
    suggested_content TEXT NOT NULL,
    suggested_hashtags TEXT[],
    suggested_media_types TEXT[],
    model_used VARCHAR NOT NULL,
    prompt_used TEXT NOT NULL,
    temperature NUMERIC CHECK (temperature IS NULL OR (temperature >= 0.0 AND temperature <= 2.0)),
    max_tokens INTEGER,
    competitor_analysis JSONB,
    content_strategy JSONB,
    predicted_engagement JSONB,
    was_accepted BOOLEAN,
    user_modifications TEXT,
    feedback_score INTEGER CHECK (feedback_score IS NULL OR (feedback_score >= 1 AND feedback_score <= 5)),
    created_at TIMESTAMPTZ DEFAULT now(),
    processing_time_ms INTEGER,
    FOREIGN KEY (user_post_id) REFERENCES user_posts(id),
    FOREIGN KEY (user_id) REFERENCES users(clerk_id)
);

-- Content generation prompts table
CREATE TABLE content_generation_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR,
    name VARCHAR NOT NULL,
    description TEXT,
    prompt_template TEXT NOT NULL,
    category VARCHAR,
    target_platforms TEXT[],
    industry_tags TEXT[],
    tone_tags TEXT[],
    usage_count INTEGER DEFAULT 0,
    success_rate NUMERIC DEFAULT 0.0 CHECK (success_rate >= 0.0 AND success_rate <= 100.0),
    avg_user_rating NUMERIC CHECK (avg_user_rating IS NULL OR (avg_user_rating >= 1.0 AND avg_user_rating <= 5.0)),
    is_active BOOLEAN DEFAULT true,
    is_system_prompt BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    last_used_at TIMESTAMPTZ,
    FOREIGN KEY (user_id) REFERENCES users(clerk_id)
);

-- Campaign with user ID table
CREATE TABLE campaign_with_user_id (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    name VARCHAR,
    date DATE,
    impressions INTEGER,
    clicks INTEGER,
    ctr DOUBLE PRECISION,
    cpc DOUBLE PRECISION,
    spend DOUBLE PRECISION,
    budget DOUBLE PRECISION,
    conversions INTEGER,
    net_profit DOUBLE PRECISION,
    ongoing VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(clerk_id)
);

-- ROI metrics table
CREATE TABLE roi_metrics (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    platform VARCHAR NOT NULL,
    campaign_id INTEGER,
    post_id VARCHAR,
    content_type VARCHAR,
    content_category VARCHAR,
    views INTEGER DEFAULT 1,
    likes INTEGER DEFAULT 1,
    comments INTEGER DEFAULT 1,
    shares INTEGER DEFAULT 1,
    saves INTEGER DEFAULT 1,
    clicks INTEGER DEFAULT 1,
    ad_spend NUMERIC DEFAULT 0.00,
    revenue_generated NUMERIC DEFAULT 0.00,
    cost_per_click NUMERIC DEFAULT 0.00,
    cost_per_impression NUMERIC DEFAULT 0.00,
    roi_percentage NUMERIC DEFAULT 0.00,
    roas_ratio NUMERIC DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    posted_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(clerk_id),
    FOREIGN KEY (campaign_id) REFERENCES campaign_with_user_id(id)
);

-- Platform metrics table
CREATE TABLE platform_metrics (
    id INTEGER PRIMARY KEY,
    roi_metric_id INTEGER,
    user_id VARCHAR NOT NULL,
    platform VARCHAR NOT NULL,
    update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metrics JSONB DEFAULT '{}',
    engagement_rate NUMERIC DEFAULT 1.00,
    virality_score NUMERIC DEFAULT 1.00,
    FOREIGN KEY (user_id) REFERENCES users(clerk_id)
);

-- =====================================================
-- INDEXES
-- =====================================================

-- Users table indexes
CREATE INDEX idx_users_clerk_id ON users(clerk_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Competitors table indexes
CREATE INDEX idx_competitors_user_id ON competitors(user_id);
CREATE INDEX idx_competitors_status ON competitors(status);
CREATE INDEX idx_competitors_industry ON competitors(industry);
CREATE INDEX idx_competitors_last_scan_at ON competitors(last_scan_at);

-- Monitoring data table indexes
CREATE INDEX idx_monitoring_data_competitor_id ON monitoring_data(competitor_id);
CREATE INDEX idx_monitoring_data_platform ON monitoring_data(platform);
CREATE INDEX idx_monitoring_data_detected_at ON monitoring_data(detected_at);
CREATE INDEX idx_monitoring_data_content_hash ON monitoring_data(content_hash);

-- Monitoring alerts table indexes
CREATE INDEX idx_monitoring_alerts_user_id ON monitoring_alerts(user_id);
CREATE INDEX idx_monitoring_alerts_competitor_id ON monitoring_alerts(competitor_id);
CREATE INDEX idx_monitoring_alerts_created_at ON monitoring_alerts(created_at);
CREATE INDEX idx_monitoring_alerts_is_read ON monitoring_alerts(is_read);

-- Social media accounts table indexes
CREATE INDEX idx_social_media_accounts_user_id ON social_media_accounts(user_id);
CREATE INDEX idx_social_media_accounts_platform ON social_media_accounts(platform);
CREATE INDEX idx_social_media_accounts_is_active ON social_media_accounts(is_active);

-- Videos table indexes
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_channel_id ON videos(channel_id);
CREATE INDEX idx_videos_published_at ON videos(published_at);
CREATE INDEX idx_videos_views ON videos(views);

-- User posts table indexes
CREATE INDEX idx_user_posts_user_id ON user_posts(user_id);
CREATE INDEX idx_user_posts_post_status ON user_posts(post_status);
CREATE INDEX idx_user_posts_created_at ON user_posts(created_at);
CREATE INDEX idx_user_posts_scheduled_for ON user_posts(scheduled_for);

-- ROI metrics table indexes
CREATE INDEX idx_roi_metrics_user_id ON roi_metrics(user_id);
CREATE INDEX idx_roi_metrics_platform ON roi_metrics(platform);
CREATE INDEX idx_roi_metrics_campaign_id ON roi_metrics(campaign_id);
CREATE INDEX idx_roi_metrics_created_at ON roi_metrics(created_at);

-- =====================================================
-- TRIGGERS AND FUNCTIONS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_competitors_updated_at BEFORE UPDATE ON competitors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_monitoring_data_updated_at BEFORE UPDATE ON monitoring_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_monitoring_settings_updated_at BEFORE UPDATE ON user_monitoring_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_competitor_monitoring_status_updated_at BEFORE UPDATE ON competitor_monitoring_status FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_social_media_accounts_updated_at BEFORE UPDATE ON social_media_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_uploads_updated_at BEFORE UPDATE ON content_uploads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_templates_updated_at BEFORE UPDATE ON content_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_channels_updated_at BEFORE UPDATE ON channels FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_roi_analytics_updated_at BEFORE UPDATE ON roi_analytics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_posts_updated_at BEFORE UPDATE ON user_posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_content_suggestions_updated_at BEFORE UPDATE ON ai_content_suggestions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_generation_prompts_updated_at BEFORE UPDATE ON content_generation_prompts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE users IS 'Main users table storing user account information';
COMMENT ON TABLE competitors IS 'Competitor companies being monitored by users';
COMMENT ON TABLE monitoring_data IS 'Data collected from monitoring competitors across various platforms';
COMMENT ON TABLE monitoring_alerts IS 'Alerts generated from monitoring activities';
COMMENT ON TABLE social_media_accounts IS 'Connected social media accounts for users';
COMMENT ON TABLE videos IS 'YouTube videos associated with user channels';
COMMENT ON TABLE roi_analytics IS 'ROI analysis data for YouTube channels';
COMMENT ON TABLE user_posts IS 'Content posts created by users with AI assistance';
COMMENT ON TABLE ai_content_suggestions IS 'AI-generated content suggestions for user posts';

-- =====================================================
-- END OF DATABASE STRUCTURE
-- =====================================================

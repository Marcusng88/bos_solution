-- BOS Solution Database Schema
-- Continuous Monitoring and Competitor Intelligence System

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
CREATE TYPE monitoring_status AS ENUM ('active', 'paused', 'error');
CREATE TYPE alert_priority AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE social_media_platform AS ENUM ('instagram', 'facebook', 'twitter', 'linkedin', 'tiktok', 'youtube', 'other');

-- Users table - stores user information from Clerk authentication
CREATE TABLE public.users (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    clerk_id VARCHAR(255) NOT NULL,
    email VARCHAR(255) NULL,
    first_name VARCHAR(100) NULL,
    last_name VARCHAR(100) NULL,
    profile_image_url VARCHAR(500) NULL,
    is_active BOOLEAN NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NOW(),
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_clerk_id_key UNIQUE (clerk_id)
) TABLESPACE pg_default;

-- Competitors table - stores competitor information
CREATE TABLE competitors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL, -- Clerk user ID
    name VARCHAR(255) NOT NULL,
    description TEXT,
    website_url VARCHAR(500),
    social_media_handles JSONB, -- Store platform:handle mappings
    industry VARCHAR(100),
    status monitoring_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_scan_at TIMESTAMP WITH TIME ZONE,
    scan_frequency_minutes INTEGER DEFAULT 60, -- How often to scan this competitor
    
    -- Constraints
    CONSTRAINT unique_user_competitor UNIQUE(user_id, name),
    CONSTRAINT valid_scan_frequency CHECK (scan_frequency_minutes >= 15) -- Minimum 15 minutes
);

-- Monitoring data table - stores social media posts and changes
CREATE TABLE monitoring_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_id UUID NOT NULL REFERENCES competitors(id) ON DELETE CASCADE,
    platform social_media_platform NOT NULL,
    post_id VARCHAR(255), -- Original post ID from the platform
    post_url VARCHAR(500),
    content_text TEXT,
    content_hash VARCHAR(64), -- Hash of content for change detection
    media_urls JSONB, -- Array of media URLs
    engagement_metrics JSONB, -- Likes, comments, shares, etc.
    author_username VARCHAR(255),
    author_display_name VARCHAR(255),
    author_avatar_url VARCHAR(500),
    post_type VARCHAR(50), -- post, story, reel, video, etc.
    language VARCHAR(10), -- ISO language code
    sentiment_score DECIMAL(3,2), -- -1.0 to 1.0
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    posted_at TIMESTAMP WITH TIME ZONE, -- When the post was originally posted
    is_new_post BOOLEAN DEFAULT true,
    is_content_change BOOLEAN DEFAULT false,
    previous_content_hash VARCHAR(64), -- For tracking content changes
    
    -- Constraints
    CONSTRAINT valid_sentiment_score CHECK (sentiment_score >= -1.0 AND sentiment_score <= 1.0)
);

-- User monitoring settings table - stores user preferences and configurations
CREATE TABLE user_monitoring_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL UNIQUE, -- Clerk user ID
    global_monitoring_enabled BOOLEAN DEFAULT true,
    default_scan_frequency_minutes INTEGER DEFAULT 60,
    alert_preferences JSONB DEFAULT '{
        "email_alerts": true,
        "push_notifications": true,
        "new_posts": true,
        "content_changes": true,
        "engagement_spikes": true,
        "sentiment_changes": true
    }',
    notification_schedule JSONB DEFAULT '{
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "08:00",
        "timezone": "UTC"
    }',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Monitoring alerts table - stores generated alerts for users
CREATE TABLE monitoring_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL, -- Clerk user ID
    competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,
    monitoring_data_id UUID REFERENCES monitoring_data(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL, -- new_post, content_change, engagement_spike, etc.
    priority alert_priority DEFAULT 'medium',
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    alert_metadata JSONB, -- Additional context about the alert
    is_read BOOLEAN DEFAULT false,
    is_dismissed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE,
    dismissed_at TIMESTAMP WITH TIME ZONE
);

-- Competitor monitoring status table - tracks real-time monitoring status
CREATE TABLE competitor_monitoring_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_id UUID NOT NULL REFERENCES competitors(id) ON DELETE CASCADE,
    last_successful_scan TIMESTAMP WITH TIME ZONE,
    last_failed_scan TIMESTAMP WITH TIME ZONE,
    scan_error_message TEXT,
    consecutive_failures INTEGER DEFAULT 0,
    is_scanning BOOLEAN DEFAULT false,
    scan_started_at TIMESTAMP WITH TIME ZONE,
    next_scheduled_scan TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_clerk_id ON public.users USING btree (clerk_id) TABLESPACE pg_default;
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users USING btree (email) TABLESPACE pg_default;
CREATE INDEX idx_competitors_user_id ON competitors(user_id);
CREATE INDEX idx_competitors_status ON competitors(status);
CREATE INDEX idx_monitoring_data_competitor_id ON monitoring_data(competitor_id);
CREATE INDEX idx_monitoring_data_platform ON monitoring_data(platform);
CREATE INDEX idx_monitoring_data_detected_at ON monitoring_data(detected_at);
CREATE INDEX idx_monitoring_data_content_hash ON monitoring_data(content_hash);
CREATE INDEX idx_monitoring_data_posted_at ON monitoring_data(posted_at);
CREATE INDEX idx_monitoring_alerts_user_id ON monitoring_alerts(user_id);
CREATE INDEX idx_monitoring_alerts_competitor_id ON monitoring_alerts(competitor_id);
CREATE INDEX idx_monitoring_alerts_created_at ON monitoring_alerts(created_at);
CREATE INDEX idx_monitoring_alerts_is_read ON monitoring_alerts(is_read);
CREATE INDEX idx_competitor_monitoring_status_competitor_id ON competitor_monitoring_status(competitor_id);

-- Create full-text search indexes
CREATE INDEX idx_monitoring_data_content_text_gin ON monitoring_data USING gin(to_tsvector('english', content_text));
CREATE INDEX idx_competitors_name_gin ON competitors USING gin(to_tsvector('english', name));

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitors_updated_at BEFORE UPDATE ON competitors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_monitoring_settings_updated_at BEFORE UPDATE ON user_monitoring_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitor_monitoring_status_updated_at BEFORE UPDATE ON competitor_monitoring_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to automatically create user settings when user is created
CREATE OR REPLACE FUNCTION create_user_monitoring_settings()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_monitoring_settings (user_id)
    VALUES (NEW.clerk_id)
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for automatic user settings creation
CREATE TRIGGER create_user_settings_trigger AFTER INSERT ON users
    FOR EACH ROW EXECUTE FUNCTION create_user_monitoring_settings();

-- Insert sample data for testing (optional)
-- Sample user
-- INSERT INTO users (
--     clerk_id, 
--     email, 
--     first_name, 
--     last_name
-- ) VALUES (
--     'user_2abc123def456ghi', 
--     'test@example.com', 
--     'John', 
--     'Doe'
-- );

-- Sample user settings and competitors (using existing table structure)
-- INSERT INTO user_monitoring_settings (user_id) VALUES ('user_2abc123def456ghi');
-- INSERT INTO competitors (user_id, name, description, industry) VALUES ('user_2abc123def456ghi', 'Nike', 'Athletic footwear and apparel', 'Sports');
-- INSERT INTO competitors (user_id, name, description, industry) VALUES ('user_2abc123def456ghi', 'Adidas', 'Sportswear manufacturer', 'Sports');

-- Grant necessary permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- ============================================================================
-- NEW TABLES FOR USER PREFERENCES AND COMPETITOR TRACKING
-- ============================================================================

-- User preferences table - stores onboarding preferences
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL UNIQUE, -- Clerk user ID
    industry VARCHAR(100) NOT NULL,
    company_size VARCHAR(50) NOT NULL,
    marketing_goals TEXT[] NOT NULL, -- Array of marketing objectives
    monthly_budget VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_company_size CHECK (company_size IN ('1-10', '11-50', '51-200', '201-500', '500+')),
    CONSTRAINT valid_budget CHECK (monthly_budget IN ('$0 - $1,000', '$1,000 - $5,000', '$5,000 - $10,000', '$10,000 - $25,000', '$25,000+')),
    
    -- Foreign key reference to users table
    CONSTRAINT fk_user_preferences_user_id FOREIGN KEY (user_id) REFERENCES users(clerk_id) ON DELETE CASCADE
);

-- My competitors table - stores user's competitor information
CREATE TABLE my_competitors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL, -- Clerk user ID
    competitor_name VARCHAR(255) NOT NULL,
    website_url VARCHAR(500),
    active_platforms TEXT[] NOT NULL, -- Array of platforms they're active on
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_platforms CHECK (array_length(active_platforms, 1) > 0),
    
    -- Foreign key reference to users table
    CONSTRAINT fk_my_competitors_user_id FOREIGN KEY (user_id) REFERENCES users(clerk_id) ON DELETE CASCADE,
    
    -- Unique constraint: one user can't have duplicate competitor names
    CONSTRAINT unique_user_competitor_name UNIQUE(user_id, competitor_name)
);

-- ============================================================================
-- NEW TABLES FOR SOCIAL MEDIA CONTENT UPLOAD
-- ============================================================================

-- Social media accounts table - stores connected social media accounts
CREATE TABLE social_media_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL, -- Clerk user ID
    platform social_media_platform NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    username VARCHAR(255),
    profile_picture_url TEXT,
    account_id VARCHAR(255), -- Platform-specific account ID
    access_token TEXT, -- Encrypted access token
    refresh_token TEXT, -- Encrypted refresh token
    token_expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    is_test_account BOOLEAN DEFAULT false, -- For safe testing
    permissions JSONB, -- What the app can do with this account
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_user_platform_account UNIQUE(user_id, platform, account_name),
    
    -- Foreign key reference to users table
    CONSTRAINT fk_social_media_accounts_user_id FOREIGN KEY (user_id) REFERENCES users(clerk_id) ON DELETE CASCADE
);

-- Content uploads table - stores content that users want to post
CREATE TABLE content_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL, -- Clerk user ID
    title VARCHAR(255),
    content_text TEXT,
    media_files JSONB, -- Array of media file info: [{"url": "...", "type": "image", "size": 1234}]
    scheduled_at TIMESTAMP WITH TIME ZONE, -- When to post (null for immediate)
    platform social_media_platform NOT NULL,
    account_id UUID REFERENCES social_media_accounts(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'draft', -- draft, scheduled, posted, failed, cancelled
    post_id VARCHAR(255), -- Platform-specific post ID after successful upload
    post_url VARCHAR(500), -- URL to the posted content
    error_message TEXT, -- If upload failed
    upload_attempts INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMP WITH TIME ZONE,
    is_test_post BOOLEAN DEFAULT false, -- For safe testing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('draft', 'scheduled', 'posted', 'failed', 'cancelled')),
    CONSTRAINT valid_upload_attempts CHECK (upload_attempts >= 0),
    
    -- Foreign key reference to users table
    CONSTRAINT fk_content_uploads_user_id FOREIGN KEY (user_id) REFERENCES users(clerk_id) ON DELETE CASCADE
);

-- Content templates table - reusable content templates for quick posting
CREATE TABLE content_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL, -- Clerk user ID
    name VARCHAR(255) NOT NULL,
    description TEXT,
    content_text TEXT,
    media_files JSONB, -- Default media files
    platforms TEXT[], -- Which platforms this template works for
    tags TEXT[], -- For organization
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_platforms CHECK (array_length(platforms, 1) > 0),
    
    -- Foreign key reference to users table
    CONSTRAINT fk_content_templates_user_id FOREIGN KEY (user_id) REFERENCES users(clerk_id) ON DELETE CASCADE
);

-- Create indexes for new tables
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_preferences_industry ON user_preferences(industry);
CREATE INDEX idx_user_preferences_company_size ON user_preferences(company_size);
CREATE INDEX idx_my_competitors_user_id ON my_competitors(user_id);
CREATE INDEX idx_my_competitors_competitor_name ON my_competitors(competitor_name);
CREATE INDEX idx_my_competitors_platforms ON my_competitors USING gin(active_platforms);

-- Social media content indexes
CREATE INDEX idx_social_media_accounts_user_id ON social_media_accounts(user_id);
CREATE INDEX idx_social_media_accounts_platform ON social_media_accounts(platform);
CREATE INDEX idx_social_media_accounts_is_test ON social_media_accounts(is_test_account);
CREATE INDEX idx_content_uploads_user_id ON content_uploads(user_id);
CREATE INDEX idx_content_uploads_status ON content_uploads(status);
CREATE INDEX idx_content_uploads_platform ON content_uploads(platform);
CREATE INDEX idx_content_uploads_scheduled_at ON content_uploads(scheduled_at);
CREATE INDEX idx_content_uploads_is_test ON content_uploads(is_test_post);
CREATE INDEX idx_content_templates_user_id ON content_templates(user_id);
CREATE INDEX idx_content_templates_platforms ON content_templates USING gin(platforms);
CREATE INDEX idx_content_templates_tags ON content_templates USING gin(tags);

-- Create triggers for updated_at on new tables
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_my_competitors_updated_at BEFORE UPDATE ON my_competitors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_social_media_accounts_updated_at BEFORE UPDATE ON social_media_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_uploads_updated_at BEFORE UPDATE ON content_uploads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_templates_updated_at BEFORE UPDATE ON content_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
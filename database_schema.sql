-- BOS Solution Database Schema
-- Continuous Monitoring and Competitor Intelligence System

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
CREATE TYPE monitoring_status AS ENUM ('active', 'paused', 'error');
CREATE TYPE alert_priority AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE social_media_platform AS ENUM ('instagram', 'facebook', 'twitter', 'linkedin', 'tiktok', 'youtube', 'other');
CREATE TYPE clerk_user_status AS ENUM ('active', 'inactive', 'banned', 'locked');

-- Clerk Users table - stores user information from Clerk authentication
CREATE TABLE clerk_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id VARCHAR(255) NOT NULL UNIQUE, -- Clerk's user ID
    email_address VARCHAR(320) NOT NULL, -- Primary email
    email_addresses JSONB, -- Array of all email addresses
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    username VARCHAR(100),
    profile_image_url VARCHAR(500),
    phone_number VARCHAR(50),
    phone_numbers JSONB, -- Array of all phone numbers
    status clerk_user_status DEFAULT 'active',
    created_at_clerk TIMESTAMP WITH TIME ZONE, -- When user was created in Clerk
    updated_at_clerk TIMESTAMP WITH TIME ZONE, -- Last updated in Clerk
    last_sign_in_at TIMESTAMP WITH TIME ZONE,
    last_active_at TIMESTAMP WITH TIME ZONE,
    banned BOOLEAN DEFAULT false,
    locked BOOLEAN DEFAULT false,
    two_factor_enabled BOOLEAN DEFAULT false,
    has_image BOOLEAN DEFAULT false,
    backup_code_enabled BOOLEAN DEFAULT false,
    totp_enabled BOOLEAN DEFAULT false,
    external_accounts JSONB, -- OAuth connections (Google, GitHub, etc.)
    public_metadata JSONB DEFAULT '{}', -- Public user metadata
    private_metadata JSONB DEFAULT '{}', -- Private user metadata
    unsafe_metadata JSONB DEFAULT '{}', -- Unsafe user metadata
    web3_wallets JSONB, -- Crypto wallet addresses
    password_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_email_format CHECK (email_address ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

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
CREATE INDEX idx_clerk_users_clerk_user_id ON clerk_users(clerk_user_id);
CREATE INDEX idx_clerk_users_email_address ON clerk_users(email_address);
CREATE INDEX idx_clerk_users_status ON clerk_users(status);
CREATE INDEX idx_clerk_users_created_at ON clerk_users(created_at);
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
CREATE TRIGGER update_clerk_users_updated_at BEFORE UPDATE ON clerk_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitors_updated_at BEFORE UPDATE ON competitors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_monitoring_settings_updated_at BEFORE UPDATE ON user_monitoring_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitor_monitoring_status_updated_at BEFORE UPDATE ON competitor_monitoring_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to automatically create user settings when competitor is added
CREATE OR REPLACE FUNCTION create_user_monitoring_settings()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_monitoring_settings (user_id)
    VALUES (NEW.user_id)
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for automatic user settings creation
CREATE TRIGGER create_user_settings_trigger AFTER INSERT ON competitors
    FOR EACH ROW EXECUTE FUNCTION create_user_monitoring_settings();

-- Insert sample data for testing (optional)
-- Sample Clerk user
-- INSERT INTO clerk_users (
--     clerk_user_id, 
--     email_address, 
--     first_name, 
--     last_name, 
--     username,
--     status
-- ) VALUES (
--     'user_2abc123def456ghi', 
--     'test@example.com', 
--     'John', 
--     'Doe', 
--     'johndoe',
--     'active'
-- );

-- Sample user settings and competitors (using existing table structure)
-- INSERT INTO user_monitoring_settings (user_id) VALUES ('user_2abc123def456ghi');
-- INSERT INTO competitors (user_id, name, description, industry) VALUES ('user_2abc123def456ghi', 'Nike', 'Athletic footwear and apparel', 'Sports');
-- INSERT INTO competitors (user_id, name, description, industry) VALUES ('user_2abc123def456ghi', 'Adidas', 'Sportswear manufacturer', 'Sports');

-- Grant necessary permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
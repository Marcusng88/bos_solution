-- BOS Solution Database Schema
-- Continuous Monitoring and Competitor Intelligence System

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Users table - stores basic user information from Clerk
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_id VARCHAR(255) NOT NULL UNIQUE, -- Clerk user ID
    email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    profile_image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for users table
CREATE INDEX idx_users_clerk_id ON users(clerk_id);
CREATE INDEX idx_users_email ON users(email);

-- Create custom types
CREATE TYPE monitoring_status AS ENUM ('active', 'paused', 'error');
CREATE TYPE alert_priority AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE social_media_platform AS ENUM ('instagram', 'facebook', 'twitter', 'linkedin', 'tiktok', 'youtube', 'other');

-- Competitors table - stores competitor information
CREATE TABLE competitors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- Reference to users table
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
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE, -- Reference to users table
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
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- Reference to users table
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

-- Create function to automatically create user settings when user is added
CREATE OR REPLACE FUNCTION create_user_monitoring_settings()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_monitoring_settings (user_id)
    VALUES (NEW.id)
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for automatic user settings creation
CREATE TRIGGER create_user_settings_trigger AFTER INSERT ON users
    FOR EACH ROW EXECUTE FUNCTION create_user_monitoring_settings();

-- Insert sample data for testing (optional)
-- INSERT INTO users (clerk_id, email, first_name, last_name) VALUES ('user_test_123', 'test@example.com', 'Test', 'User');
-- INSERT INTO competitors (user_id, name, description, industry) VALUES ((SELECT id FROM users WHERE clerk_id = 'user_test_123'), 'Nike', 'Athletic footwear and apparel', 'Sports');

-- Grant necessary permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

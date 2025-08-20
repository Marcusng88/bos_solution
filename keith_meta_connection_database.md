# Meta Connection Database Structure

## Overview
This document outlines the database schema for connecting and managing Meta (Facebook/Instagram) accounts in the BOS Solution platform.

## Database Tables

### 1. Social Media Connections Table
Stores user connections to various social media platforms.

```sql
CREATE TABLE social_media_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL, -- Clerk user ID
    platform VARCHAR(50) NOT NULL, -- 'instagram', 'facebook', 'twitter', 'linkedin', 'youtube'
    account_id VARCHAR(255), -- Platform's internal account ID
    account_username VARCHAR(255), -- @username or page name
    display_name VARCHAR(255), -- Human-readable account name
    profile_picture_url VARCHAR(500), -- Profile picture URL
    access_token TEXT NOT NULL, -- OAuth access token
    refresh_token TEXT, -- OAuth refresh token
    token_expires_at TIMESTAMP WITH TIME ZONE, -- When token expires
    permissions JSONB, -- Granted OAuth scopes
    metadata JSONB, -- Additional platform-specific data
    is_active BOOLEAN DEFAULT true, -- Connection status
    last_sync_at TIMESTAMP WITH TIME ZONE, -- Last successful data sync
    sync_frequency_minutes INTEGER DEFAULT 60, -- How often to sync
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_user_platform UNIQUE(user_id, platform),
    CONSTRAINT valid_platform CHECK (platform IN ('instagram', 'facebook', 'twitter', 'linkedin', 'youtube')),
    CONSTRAINT valid_sync_frequency CHECK (sync_frequency_minutes >= 15)
);
```

### 2. Social Media Content Table
Stores content fetched from connected social media accounts.

```sql
CREATE TABLE social_media_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connection_id UUID NOT NULL REFERENCES social_media_connections(id) ON DELETE CASCADE,
    platform_content_id VARCHAR(255), -- Original platform post ID
    content_type VARCHAR(50) NOT NULL, -- 'post', 'story', 'reel', 'video', 'ad'
    content_text TEXT, -- Text content
    media_urls JSONB, -- Array of media URLs
    engagement_metrics JSONB, -- Likes, comments, shares, etc.
    reach_metrics JSONB, -- Impressions, reach, views
    published_at TIMESTAMP WITH TIME ZONE, -- When content was published
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- When we fetched it
    is_competitor_content BOOLEAN DEFAULT false, -- Is this from competitor monitoring?
    competitor_id UUID REFERENCES competitors(id), -- If monitoring competitor
    content_hash VARCHAR(64), -- Hash for change detection
    
    -- Constraints
    CONSTRAINT valid_content_type CHECK (content_type IN ('post', 'story', 'reel', 'video', 'ad')),
    CONSTRAINT unique_platform_content UNIQUE(connection_id, platform_content_id)
);
```

### 3. Social Media Analytics Table
Stores aggregated analytics data from social media platforms.

```sql
CREATE TABLE social_media_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connection_id UUID NOT NULL REFERENCES social_media_connections(id) ON DELETE CASCADE,
    date DATE NOT NULL, -- Analytics date
    metric_type VARCHAR(50) NOT NULL, -- 'followers', 'engagement', 'reach', 'impressions'
    metric_value DECIMAL(10,2) NOT NULL, -- Numeric value
    metric_unit VARCHAR(20), -- 'count', 'percentage', 'currency'
    breakdown JSONB, -- Detailed breakdown (age, gender, location, etc.)
    
    -- Constraints
    CONSTRAINT unique_metric_date UNIQUE(connection_id, date, metric_type),
    CONSTRAINT valid_metric_type CHECK (metric_type IN ('followers', 'engagement', 'reach', 'impressions', 'clicks', 'conversions'))
);
```

### 4. OAuth Sessions Table
Tracks OAuth authentication sessions and state.

```sql
CREATE TABLE oauth_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL, -- Clerk user ID
    platform VARCHAR(50) NOT NULL, -- Platform being authenticated
    state_token VARCHAR(255) NOT NULL, -- OAuth state parameter
    code_verifier VARCHAR(255), -- PKCE code verifier
    redirect_uri VARCHAR(500) NOT NULL, -- OAuth redirect URI
    requested_scopes JSONB, -- Requested permissions
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL, -- Session expiry
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_platform CHECK (platform IN ('instagram', 'facebook', 'twitter', 'linkedin', 'youtube'))
);
```

## Indexes for Performance

```sql
-- Social media connections
CREATE INDEX idx_social_media_connections_user_id ON social_media_connections(user_id);
CREATE INDEX idx_social_media_connections_platform ON social_media_connections(platform);
CREATE INDEX idx_social_media_connections_active ON social_media_connections(is_active);

-- Social media content
CREATE INDEX idx_social_media_content_connection ON social_media_content(connection_id);
CREATE INDEX idx_social_media_content_published ON social_media_content(published_at);
CREATE INDEX idx_social_media_content_competitor ON social_media_content(competitor_id);

-- Social media analytics
CREATE INDEX idx_social_media_analytics_connection ON social_media_analytics(connection_id);
CREATE INDEX idx_social_media_analytics_date ON social_media_analytics(date);
CREATE INDEX idx_social_media_analytics_metric ON social_media_analytics(metric_type);

-- OAuth sessions
CREATE INDEX idx_oauth_sessions_user_platform ON oauth_sessions(user_id, platform);
CREATE INDEX idx_oauth_sessions_state ON oauth_sessions(state_token);
CREATE INDEX idx_oauth_sessions_expires ON oauth_sessions(expires_at);
```

## Triggers for Automatic Updates

```sql
-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to relevant tables
CREATE TRIGGER update_social_media_connections_updated_at 
    BEFORE UPDATE ON social_media_connections 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_social_media_content_updated_at 
    BEFORE UPDATE ON social_media_content 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Sample Data

### Social Media Connections
```sql
INSERT INTO social_media_connections (
    user_id, 
    platform, 
    account_username, 
    display_name, 
    access_token, 
    permissions
) VALUES (
    'user_123',
    'instagram',
    'mybusiness',
    'My Business',
    'IGQWR...',
    '["instagram_basic", "instagram_content_publish"]'
);
```

### Social Media Content
```sql
INSERT INTO social_media_content (
    connection_id,
    platform_content_id,
    content_type,
    content_text,
    engagement_metrics,
    published_at
) VALUES (
    'uuid-here',
    '17841405793087218',
    'post',
    'Check out our new product! 🚀',
    '{"likes": 45, "comments": 12, "shares": 8}',
    '2024-01-15 10:00:00+00'
);
```

## Environment Variables Needed

```bash
# Meta (Facebook/Instagram)
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
META_APP_VERSION=v18.0

# Instagram Basic Display
INSTAGRAM_APP_ID=your_instagram_app_id
INSTAGRAM_APP_SECRET=your_instagram_app_secret

# Facebook Pages
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# OAuth URLs
OAUTH_REDIRECT_BASE_URL=http://localhost:3000/auth/callback
OAUTH_SUCCESS_URL=http://localhost:3000/dashboard
OAUTH_ERROR_URL=http://localhost:3000/auth/error

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/bos_solution
```

## Next Steps

1. **Run the SQL schema** in your Supabase database
2. **Update environment variables** with your Meta app credentials
3. **Build OAuth flow components** in your frontend
4. **Create API endpoints** for handling OAuth callbacks
5. **Implement token management** and refresh logic
6. **Add data fetching** from Meta platforms
7. **Build analytics dashboard** for connected accounts

## Security Considerations

- **Store tokens encrypted** in production
- **Implement token refresh** before expiration
- **Validate OAuth state** to prevent CSRF attacks
- **Use HTTPS** for all OAuth redirects
- **Implement rate limiting** for API calls
- **Log authentication events** for security monitoring


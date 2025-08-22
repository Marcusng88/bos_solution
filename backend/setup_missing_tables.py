"""
Script to create missing tables in Supabase database
"""

import asyncio
import os
import sys
import logging
from dotenv import load_dotenv
import asyncpg

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# SQL to create missing tables
MISSING_TABLES_SQL = """
-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'social_media_platform') THEN
        CREATE TYPE social_media_platform AS ENUM ('instagram', 'facebook', 'twitter', 'linkedin', 'tiktok', 'youtube', 'other');
    END IF;
END $$;

-- Create the content_uploads table
CREATE TABLE IF NOT EXISTS content_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL, -- Clerk user ID
    title VARCHAR(255),
    content_text TEXT,
    media_files JSONB, -- Array of media file info
    scheduled_at TIMESTAMP WITH TIME ZONE, -- When to post (null for immediate)
    platform social_media_platform NOT NULL,
    account_id UUID, -- Will reference social_media_accounts(id)
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
    CONSTRAINT valid_upload_attempts CHECK (upload_attempts >= 0)
);

-- Create the content_templates table
CREATE TABLE IF NOT EXISTS content_templates (
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
    CONSTRAINT valid_platforms CHECK (array_length(platforms, 1) > 0)
);

-- Create indexes for new tables
CREATE INDEX IF NOT EXISTS idx_content_uploads_user_id ON content_uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_content_uploads_status ON content_uploads(status);
CREATE INDEX IF NOT EXISTS idx_content_uploads_platform ON content_uploads(platform);
CREATE INDEX IF NOT EXISTS idx_content_uploads_scheduled_at ON content_uploads(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_content_uploads_is_test ON content_uploads(is_test_post);
CREATE INDEX IF NOT EXISTS idx_content_templates_user_id ON content_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_content_templates_platforms ON content_templates USING gin(platforms);
CREATE INDEX IF NOT EXISTS idx_content_templates_tags ON content_templates USING gin(tags);

-- Create function to update updated_at timestamp if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at on new tables
DROP TRIGGER IF EXISTS update_content_uploads_updated_at ON content_uploads;
CREATE TRIGGER update_content_uploads_updated_at BEFORE UPDATE ON content_uploads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_content_templates_updated_at ON content_templates;
CREATE TRIGGER update_content_templates_updated_at BEFORE UPDATE ON content_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions for RLS (Row Level Security)
ALTER TABLE content_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_templates ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (users can only access their own data)
CREATE POLICY "Users can only access their own content uploads"
ON content_uploads FOR ALL 
USING (user_id = current_setting('request.jwt.claims', true)::json ->> 'sub');

CREATE POLICY "Users can only access their own content templates"
ON content_templates FOR ALL 
USING (user_id = current_setting('request.jwt.claims', true)::json ->> 'sub');
"""

async def create_missing_tables():
    """Create missing tables in Supabase"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ Missing DATABASE_URL in .env file")
        return False
    
    try:
        print("🔧 Creating missing tables in Supabase...")
        
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Execute the SQL
        await conn.execute(MISSING_TABLES_SQL)
        
        print("✅ Successfully created missing tables")
        
        # Test that tables exist now
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('content_uploads', 'content_templates')
        ORDER BY table_name;
        """
        
        tables = await conn.fetch(tables_query)
        print(f"📋 Created tables: {[table['table_name'] for table in tables]}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

async def test_dns_resolution():
    """Test DNS resolution for Supabase hostname"""
    import socket
    
    try:
        hostname = "db.zktakfluvzuxhwwvccqs.supabase.co"
        print(f"🌐 Testing DNS resolution for {hostname}")
        
        # Try to resolve the hostname
        ip_address = socket.gethostbyname(hostname)
        print(f"✅ DNS resolution successful: {hostname} -> {ip_address}")
        return True
        
    except Exception as e:
        print(f"❌ DNS resolution failed: {e}")
        print("   This might be a network connectivity issue.")
        print("   Try:")
        print("   1. Check your internet connection")
        print("   2. Try flushing DNS: ipconfig /flushdns")
        print("   3. Try using a different DNS server (8.8.8.8)")
        return False

async def main():
    """Main function"""
    print("🚀 Setting up missing Supabase tables and testing connection")
    print("=" * 60)
    
    # Test DNS first
    dns_ok = await test_dns_resolution()
    
    if not dns_ok:
        print("\n⚠️  DNS resolution failed. Cannot proceed with database operations.")
        print("   Your Supabase REST API will still work, but direct PostgreSQL connections won't.")
        return
    
    # Create missing tables
    tables_created = await create_missing_tables()
    
    if tables_created:
        print("\n🎉 Database setup completed successfully!")
        print("   You can now use both REST API and direct PostgreSQL connections.")
    else:
        print("\n❌ Failed to create tables. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())

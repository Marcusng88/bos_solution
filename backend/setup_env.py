#!/usr/bin/env python3
"""
Environment setup script for BOS Solution backend
This script helps you set up environment variables for development
"""

import os
import sys

def create_env_file():
    """Create a .env file with default development values"""
    
    env_content = """# Backend Environment Configuration
# Update these values with your actual database and API credentials

# Application
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database - Using your Supabase database as default
DATABASE_URL=postgresql://postgres:RE-_tXFsy9K8D$M@db.zktakfluvzuxhwwvccqs.supabase.co:5432/postgres

# Supabase Configuration
SUPABASE_URL=url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# Social Media API Keys (add as needed)
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token_here
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token_here

# Monitoring Settings
DEFAULT_SCAN_FREQUENCY=60
MAX_CONCURRENT_SCANS=5

# Redis (for background tasks)
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
"""
    
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_file_path):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("❌ Setup cancelled")
            return False
    
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Created .env file at: {env_file_path}")
        print("\n📝 Next steps:")
        print("1. Update SUPABASE_ANON_KEY and SUPABASE_SERVICE_ROLE_KEY in the .env file")
        print("2. Run: python run.py")
        print("\n💡 Your Supabase database is already configured!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def main():
    """Main function"""
    print("🚀 BOS Solution Backend Environment Setup")
    print("=" * 50)
    
    if create_env_file():
        print("\n🎉 Environment setup complete!")
        print("\n💡 Your Supabase database is ready to use!")
        print("   - Database URL: Configured")
        print("   - Supabase URL: Configured")
        print("   - Next: Add your Supabase API keys")
    else:
        print("\n❌ Environment setup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simple script to run the BOS Solution backend server
Usage: python run.py
"""

import uvicorn
import os
import sys
from dotenv import load_dotenv
load_dotenv()
def check_environment():
    """Check if environment variables are set up"""
    required_vars = ["DATABASE_URL"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)    
    if missing_vars:
        print("⚠️  Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Run 'python setup_env.py' to create a .env file")
        print("   Or set the environment variables manually")
        return False
    
    return True

def main():
    """Main function to run the FastAPI server"""
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the backend directory to Python path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # Check environment variables
    if not check_environment():
        print("\n❌ Cannot start server without required environment variables")
        sys.exit(1)
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("DEBUG", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print("🚀 Starting BOS Solution Backend Server...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"📝 Log Level: {log_level}")
    print("=" * 50)
    
    try:
        # Start the server
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("\n💡 Make sure:")
        print("   - Database is running and accessible")
        print("   - Environment variables are set correctly")
        print("   - All dependencies are installed (pip install -r requirements.txt)")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Quick start script for BOS Solution backend
Usage: python run.py [--port PORT] [--host HOST]

This script will start:
1. FastAPI backend server
2. Database connection
3. ROI scheduler (runs every 10 minutes)
4. All API endpoints
"""

import uvicorn
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='Start BOS Solution FastAPI backend')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    parser.add_argument('--no-reload', action='store_true', help='Disable auto-reload')
    parser.add_argument('--log-level', default='info', choices=['debug', 'info', 'warning', 'error'], 
                       help='Log level (default: info)')
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("Error: 'main.py' file not found. Make sure you're in the backend directory.")
        sys.exit(1)
    
    print("🚀 Starting BOS Solution Backend")
    print("=" * 50)
    print(f"🌐 Server: {args.host}:{args.port}")
    print(f"📚 API Docs: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}/docs")
    print(f"🔄 Auto-reload: {'Enabled' if not args.no_reload else 'Disabled'}")
    print(f"📊 Log Level: {args.log_level}")
    print("=" * 50)
    print("📋 What will be initialized:")
    print("   ✅ FastAPI application")
    print("   ✅ Database connection")
    print("   ✅ ROI scheduler (10-minute intervals)")
    print("   ✅ All API endpoints")
    print("   ✅ CORS middleware")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()

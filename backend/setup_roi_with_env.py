#!/usr/bin/env python3
"""
ROI Schema Setup with Environment Loading
"""

import asyncio
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Environment variables loaded from .env")
except ImportError:
    print("⚠ python-dotenv not available, using system environment")

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Import and run the setup
try:
    from app.core.ROI_backend.roi.setup_roi_schema import apply_roi_sql
    
    async def main():
        print("🚀 Starting ROI database schema setup...")
        success = await apply_roi_sql()
        if success:
            print("\n🎉 ROI schema setup completed successfully!")
            return 0
        else:
            print("\n❌ ROI schema setup failed!")
            return 1
    
    if __name__ == "__main__":
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
        
except ImportError as e:
    print(f"❌ Failed to import setup module: {e}")
    print("Trying alternative import path...")
    
    # Try direct import
    import importlib.util
    setup_path = Path(__file__).parent / "app" / "core" / "ROI backend" / "roi" / "setup_roi_schema.py"
    spec = importlib.util.spec_from_file_location("setup_roi_schema", setup_path)
    if spec and spec.loader:
        setup_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(setup_module)
        
        async def main():
            print("🚀 Starting ROI database schema setup (alternative import)...")
            success = await setup_module.apply_roi_sql()
            if success:
                print("\n🎉 ROI schema setup completed successfully!")
                return 0
            else:
                print("\n❌ ROI schema setup failed!")
                return 1
        
        if __name__ == "__main__":
            exit_code = asyncio.run(main())
            sys.exit(exit_code)
    else:
        print("❌ Could not load setup module")
        sys.exit(1)

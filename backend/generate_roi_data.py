#!/usr/bin/env python3
"""
Manual ROI Data Generation - for testing and initial data seeding
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

async def main():
    try:
        # Import the ROI writer
        import importlib.util
        writer_path = Path(__file__).parent / "app" / "core" / "ROI backend" / "roi" / "services" / "roi_writer.py"
        
        spec = importlib.util.spec_from_file_location("roi_writer", writer_path)
        if spec and spec.loader:
            writer_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(writer_module)
            
            print("🚀 Generating ROI data...")
            
            # Run the ROI update
            inserted_count = await writer_module.execute_roi_update()
            
            if inserted_count > 0:
                print(f"✅ Successfully generated {inserted_count} new ROI data points!")
                print(f"📊 Updated metrics for {inserted_count} platform/user combinations")
            else:
                print("ℹ️  No new data generated - this could mean:")
                print("   • No existing ROI metrics found (need initial seeding)")
                print("   • Database tables don't exist yet")
                print("   • No users in the system")
                
            return 0
        else:
            print("❌ Could not load ROI writer module")
            return 1
            
    except Exception as e:
        print(f"❌ ROI data generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    print(f"\n🏁 Process completed with exit code: {exit_code}")
    sys.exit(exit_code)

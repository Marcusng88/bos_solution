#!/usr/bin/env python3
"""
Start the ROI Scheduler - runs hourly updates for ROI data generation
"""

import asyncio
import logging
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Environment variables loaded from .env")
except ImportError:
    print("⚠ python-dotenv not available, using system environment")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("roi_scheduler")

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

async def main():
    try:
        # Import the scheduler
        import importlib.util
        scheduler_path = Path(__file__).parent / "app" / "core" / "ROI backend" / "roi" / "services" / "scheduler.py"
        
        spec = importlib.util.spec_from_file_location("roi_scheduler", scheduler_path)
        if spec and spec.loader:
            scheduler_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(scheduler_module)
            
            print("🚀 Starting ROI hourly scheduler...")
            scheduler = scheduler_module.start_scheduler()
            
            if hasattr(scheduler, 'start'):
                # APScheduler
                print("✓ APScheduler started - ROI updates will run every hour")
                print("📊 Next update: at the top of the next hour")
                print("⏹️  Press Ctrl+C to stop")
                
                # Keep the script running
                try:
                    while True:
                        await asyncio.sleep(60)  # Check every minute
                        logger.info("Scheduler status: Running")
                except KeyboardInterrupt:
                    print("\n🛑 Stopping scheduler...")
                    scheduler.shutdown()
                    
            else:
                # Fallback task
                print("✓ Fallback scheduler started - ROI updates will run every hour")
                print("📊 Running continuous update loop")
                print("⏹️  Press Ctrl+C to stop")
                
                try:
                    await scheduler  # This is the async task
                except KeyboardInterrupt:
                    print("\n🛑 Stopping scheduler...")
                    scheduler.cancel()
        else:
            print("❌ Could not load scheduler module")
            return 1
            
    except Exception as e:
        logger.exception("Scheduler failed to start: %s", e)
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Scheduler stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.exception("Scheduler crashed: %s", e)
        sys.exit(1)

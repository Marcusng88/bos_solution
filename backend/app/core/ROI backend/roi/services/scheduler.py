"""
ROI Scheduler - runs the ROI writer on a schedule.

Changed: run every 10 minutes and trigger one immediate run on startup.
Falls back to a simple loop if APScheduler is unavailable.
Updated to handle errors more gracefully.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
import logging
import os

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    HAS_APS = True
except Exception:
    HAS_APS = False

# Dynamically import roi_writer (relative import fails when loaded via importlib)
import importlib.util as _ils
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_WRITER_PATH = _HERE / "roi_writer.py"
_SPEC = _ils.spec_from_file_location("roi_writer", str(_WRITER_PATH))
if _SPEC and _SPEC.loader:
    _MOD = _ils.module_from_spec(_SPEC)
    import sys as _sys
    if _SPEC.name:
        _sys.modules[_SPEC.name] = _MOD
    _SPEC.loader.exec_module(_MOD)  # type: ignore[attr-defined]
    execute_roi_update = _MOD.execute_roi_update  # type: ignore[attr-defined]
else:
    raise ImportError("Failed to load roi_writer.py")

logger = logging.getLogger(__name__)

# Global scheduler instance for cleanup
_scheduler_instance = None
_fallback_task = None

async def run_roi_update_job():
    """Run the ROI update job with enhanced error handling"""
    try:
        logger.info("Starting ROI update job...")
        inserted = await execute_roi_update()
        logger.info(f"ROI job completed successfully, inserted={inserted} rows")
        return inserted
    except ImportError as e:
        logger.error(f"ROI job failed due to import error: {e}")
        logger.error("This might be due to missing dependencies or incorrect module paths")
    except Exception as e:
        logger.exception(f"ROI job failed with error: {e}")
        # Don't re-raise the exception to prevent scheduler from stopping
    return 0


def start_scheduler(loop=None):
    """Start the ROI scheduler with enhanced error handling"""
    global _scheduler_instance, _fallback_task
    
    try:
        if HAS_APS:
            scheduler = AsyncIOScheduler(timezone="UTC")
            # Every 10 minutes
            scheduler.add_job(
                run_roi_update_job, 
                CronTrigger.from_crontab("*/10 * * * *"), 
                id="roi_update",
                max_instances=1,  # Prevent overlapping jobs
                misfire_grace_time=300  # 5 minutes grace time
            )
            scheduler.start()
            _scheduler_instance = scheduler
            logger.info("ROI APScheduler started (every 10 minutes)")

            # Kick off an immediate run without waiting for the next tick
            try:
                asyncio.get_running_loop().create_task(run_roi_update_job())
            except RuntimeError:
                # No running loop (unlikely in FastAPI startup), fire-and-forget via ensure_future
                asyncio.ensure_future(run_roi_update_job())
            return scheduler
        else:
            async def fallback():
                logger.info("ROI fallback scheduler started (10-minute sleep loop)")
                while True:
                    try:
                        await run_roi_update_job()
                    except Exception as e:
                        logger.error(f"Fallback scheduler error: {e}")
                        # Continue running even if individual jobs fail
                    await asyncio.sleep(600)  # 10 minutes
            
            _fallback_task = asyncio.create_task(fallback())
            return _fallback_task
    except Exception as e:
        logger.error(f"Failed to start ROI scheduler: {e}")
        # Return None to indicate failure
        return None


def stop_scheduler():
    """Stop the ROI scheduler and cleanup resources"""
    global _scheduler_instance, _fallback_task
    
    try:
        if _scheduler_instance and HAS_APS:
            _scheduler_instance.shutdown(wait=False)
            _scheduler_instance = None
            logger.info("ROI APScheduler stopped")
            
        elif _fallback_task:
            _fallback_task.cancel()
            _fallback_task = None
            logger.info("ROI fallback scheduler stopped")
            
        else:
            logger.info("No ROI scheduler running")
            
    except Exception as e:
        logger.error(f"Error stopping ROI scheduler: {e}")


def is_scheduler_running():
    """Check if the ROI scheduler is currently running"""
    return _scheduler_instance is not None or _fallback_task is not None



"""
Monitoring Scheduler Service
Handles scheduling and triggering of continuous monitoring tasks
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import signal
import sys

from .orchestrator import SimpleMonitoringService
from .supabase_client import supabase_client

logger = logging.getLogger(__name__)


@dataclass
class SchedulerConfig:
    """Configuration for the monitoring scheduler"""
    daily_scan_interval_hours: int = 24  # Fixed daily monitoring
    max_concurrent_scans: int = 3
    retry_failed_after_minutes: int = 30
    max_consecutive_failures: int = 5
    cleanup_old_data_days: int = 30
    scheduler_loop_interval_seconds: int = 30


class MonitoringScheduler:
    """Scheduler for continuous monitoring operations"""
    
    def __init__(self, config: SchedulerConfig = None):
        self.config = config or SchedulerConfig()
        self.running = False
        self.current_tasks = set()
        self._shutdown_event = asyncio.Event()
        self.monitoring_service = SimpleMonitoringService()
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Start the monitoring scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        logger.info("Starting monitoring scheduler...")
        
        try:
            await self._run_scheduler_loop()
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")
        finally:
            self.running = False
    
    async def stop(self):
        """Stop the monitoring scheduler gracefully"""
        if not self.running:
            return
        
        logger.info("Stopping monitoring scheduler...")
        self.running = False
        self._shutdown_event.set()
        
        # Wait for current tasks to complete
        if self.current_tasks:
            logger.info(f"Waiting for {len(self.current_tasks)} tasks to complete...")
            await asyncio.gather(*self.current_tasks, return_exceptions=True)
        
        # Close monitoring service
        await self.monitoring_service.close()
        
        logger.info("Monitoring scheduler stopped")
    
    async def _run_scheduler_loop(self):
        """Main scheduler loop"""
        logger.info("Starting scheduler loop...")
        
        while self.running and not self._shutdown_event.is_set():
            try:
                # Check for competitors that need scanning
                await self._process_scheduled_scans()
                
                # Clean up completed tasks
                await self._cleanup_completed_tasks()
                
                # Perform maintenance tasks
                await self._perform_maintenance()
                
                # Wait before next iteration
                await asyncio.sleep(self.config.scheduler_loop_interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop iteration: {e}")
                await asyncio.sleep(self.config.scheduler_loop_interval_seconds)
    
    async def _process_scheduled_scans(self):
        """Process competitors that are due for scanning"""
        try:
            # Don't start new scans if we're at capacity
            if len(self.current_tasks) >= self.config.max_concurrent_scans:
                return
            
            # Get competitors that need scanning from Supabase
            due_competitors = await supabase_client.get_competitors_due_for_scan()
            
            for competitor in due_competitors:
                if len(self.current_tasks) >= self.config.max_concurrent_scans:
                    break
                
                # Start monitoring task
                task = asyncio.create_task(
                    self._run_competitor_monitoring(competitor['id'])
                )
                self.current_tasks.add(task)
                
                logger.info(f"Started monitoring task for competitor {competitor.get('name', 'Unknown')} ({competitor['id']})")
        
        except Exception as e:
            logger.error(f"Error in _process_scheduled_scans: {e}")
    
    async def _run_competitor_monitoring(self, competitor_id: str):
        """Run monitoring for a specific competitor"""
        try:
            logger.info(f"Running monitoring for competitor {competitor_id}")
            
            # Run monitoring using the monitoring service
            result = await self.monitoring_service.run_monitoring_for_competitor(competitor_id)
            
            logger.info(f"Completed monitoring for competitor {competitor_id}: {result['status']}")
            
        except Exception as e:
            logger.error(f"Error running monitoring for competitor {competitor_id}: {e}")
    
    async def _cleanup_completed_tasks(self):
        """Clean up completed monitoring tasks"""
        completed_tasks = {task for task in self.current_tasks if task.done()}
        
        for task in completed_tasks:
            try:
                # Get task result to handle any exceptions
                await task
            except Exception as e:
                logger.error(f"Error in completed monitoring task: {e}")
        
        self.current_tasks -= completed_tasks
    
    async def _perform_maintenance(self):
        """Perform periodic maintenance tasks"""
        try:
            # This could include:
            # - Cleaning up old monitoring data
            # - Resetting stuck scanning status
            # - Updating statistics
            # - Health checks
            
            current_time = datetime.utcnow()
            
            # For now, just log maintenance cycle
            logger.debug(f"Maintenance cycle completed at {current_time}")
            
        except Exception as e:
            logger.error(f"Error performing maintenance: {e}")
    
    async def trigger_immediate_scan(self, competitor_id: str) -> Dict[str, Any]:
        """Trigger an immediate scan for a specific competitor"""
        try:
            # Check if we're at capacity
            if len(self.current_tasks) >= self.config.max_concurrent_scans:
                return {
                    "success": False,
                    "message": "Scheduler is at maximum capacity"
                }
            
            # Start immediate monitoring task
            task = asyncio.create_task(
                self._run_competitor_monitoring(competitor_id)
            )
            self.current_tasks.add(task)
            
            return {
                "success": True,
                "message": f"Immediate scan started for competitor {competitor_id}"
            }
        
        except Exception as e:
            logger.error(f"Error in trigger_immediate_scan: {e}")
            return {
                "success": False,
                "message": f"Error starting scan: {str(e)}"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            "running": self.running,
            "active_tasks": len(self.current_tasks),
            "max_concurrent_scans": self.config.max_concurrent_scans,
            "scheduler_config": {
                "scan_interval_hours": self.config.daily_scan_interval_hours,
                "retry_after_minutes": self.config.retry_failed_after_minutes,
                "max_failures": self.config.max_consecutive_failures
            }
        }


# Global scheduler instance
monitoring_scheduler = MonitoringScheduler()


async def start_monitoring_scheduler():
    """Start the global monitoring scheduler"""
    await monitoring_scheduler.start()


async def stop_monitoring_scheduler():
    """Stop the global monitoring scheduler"""
    await monitoring_scheduler.stop()


if __name__ == "__main__":
    """Run the scheduler as a standalone service"""
    async def main():
        logger.info("Starting monitoring scheduler service...")
        try:
            await start_monitoring_scheduler()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            await stop_monitoring_scheduler()
    
    asyncio.run(main())

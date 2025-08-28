"""
Monitoring Scheduler Service
Handles scheduling and triggering of continuous monitoring tasks
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
import signal
import sys
import json

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
    daily_scan_time: str = "09:00"  # Default daily scan time (9 AM UTC)


class MonitoringScheduler:
    """Scheduler for continuous monitoring operations"""
    
    def __init__(self, config: SchedulerConfig = None):
        self.config = config or SchedulerConfig()
        self.running = False
        self.current_tasks = set()
        self._shutdown_event = asyncio.Event()
        self.monitoring_service = SimpleMonitoringService()
        self.daily_scan_task = None
        self.last_daily_scan = None
        
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
        
        # Check if supabase client is available
        if not supabase_client:
            logger.warning("⚠️ Supabase client not available - scheduler cannot start")
            return
        
        # Check if any users have monitoring enabled before starting
        users_with_monitoring = await self._get_users_with_monitoring_enabled()
        if not users_with_monitoring:
            logger.info("✅ No users have monitoring enabled - scheduler will run but won't scan competitors")
            logger.info("💡 Enable monitoring for users in user_monitoring_settings table to start automatic scanning")
        
        self.running = True
        logger.info("Starting monitoring scheduler...")
        
        try:
            # Start daily scan scheduler
            await self._start_daily_scan_scheduler()
            
            # Run the main scheduler loop
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
        
        # Cancel daily scan task
        if self.daily_scan_task and not self.daily_scan_task.done():
            self.daily_scan_task.cancel()
        
        # Wait for current tasks to complete
        if self.current_tasks:
            logger.info(f"Waiting for {len(self.current_tasks)} tasks to complete...")
            await asyncio.gather(*self.current_tasks, return_exceptions=True)
        
        # Close monitoring service
        await self.monitoring_service.close()
        
        logger.info("Monitoring scheduler stopped")
    
    async def _start_daily_scan_scheduler(self):
        """Start the daily scan scheduler"""
        logger.info("Starting daily scan scheduler...")
        
        async def daily_scan_loop():
            while self.running and not self._shutdown_event.is_set():
                try:
                    # Calculate next daily scan time
                    now = datetime.now(timezone.utc)
                    scan_time = datetime.strptime(self.config.daily_scan_time, "%H:%M").time()
                    next_scan = datetime.combine(now.date(), scan_time, tzinfo=timezone.utc)
                    
                    # If today's scan time has passed, schedule for tomorrow
                    if now.time() >= scan_time:
                        next_scan = next_scan + timedelta(days=1)
                    
                    # Wait until next scan time
                    wait_seconds = (next_scan - now).total_seconds()
                    logger.info(f"Next daily scan scheduled for {next_scan} (in {wait_seconds:.0f} seconds)")
                    
                    await asyncio.sleep(wait_seconds)
                    
                    if self.running and not self._shutdown_event.is_set():
                        # Run daily scan for all users with monitoring enabled
                        await self._run_daily_scan_for_all_users()
                        self.last_daily_scan = datetime.now(timezone.utc)
                        
                except asyncio.CancelledError:
                    logger.info("Daily scan scheduler cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error in daily scan scheduler: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes before retrying
        
        self.daily_scan_task = asyncio.create_task(daily_scan_loop())
    
    async def _run_daily_scan_for_all_users(self):
        """Run daily scan for all users with monitoring enabled"""
        try:
            logger.info("Starting daily scan for all users with monitoring enabled...")
            
            # Check if supabase client is available
            if not supabase_client:
                logger.warning("⚠️ Supabase client not available - skipping daily scan")
                return
            
            # Get all users with monitoring enabled
            users_with_monitoring = await self._get_users_with_monitoring_enabled()
            
            if not users_with_monitoring:
                logger.info("✅ No users have monitoring enabled - skipping daily scan")
                logger.info("💡 Enable monitoring for users in user_monitoring_settings table to start automatic scanning")
                return
            
            logger.info(f"✅ Found {len(users_with_monitoring)} users with monitoring enabled")
            
            # Run monitoring for each user's competitors
            for user_id in users_with_monitoring:
                try:
                    await self._run_daily_scan_for_user(user_id)
                except Exception as e:
                    logger.error(f"Error running daily scan for user {user_id}: {e}")
                    continue
            
            logger.info("✅ Daily scan completed for all users")
            
        except Exception as e:
            logger.error(f"Error in daily scan for all users: {e}")
    
    async def _get_users_with_monitoring_enabled(self) -> List[str]:
        """Get list of user IDs with monitoring enabled"""
        try:
            # Use the method from the supabase client
            if supabase_client:
                return await supabase_client._get_users_with_monitoring_enabled()
            else:
                logger.warning("⚠️ Supabase client not available")
                return []
            
        except Exception as e:
            logger.error(f"Error getting users with monitoring enabled: {e}")
            return []
    
    async def _run_daily_scan_for_user(self, user_id: str):
        """Run daily scan for a specific user's competitors"""
        try:
            logger.info(f"Running daily scan for user {user_id}")
            
            # Get all competitors for the user
            competitors = await supabase_client.get_competitors_by_user(user_id)
            
            if not competitors:
                logger.info(f"No competitors found for user {user_id}")
                return
            
            logger.info(f"Found {len(competitors)} competitors for user {user_id}")
            
            # Run monitoring for each competitor using core agents
            for competitor in competitors:
                try:
                    if len(self.current_tasks) >= self.config.max_concurrent_scans:
                        logger.info(f"At maximum capacity, waiting for tasks to complete...")
                        await asyncio.sleep(10)
                        continue
                    
                    # Start monitoring task for this competitor
                    task = asyncio.create_task(
                        self._run_competitor_monitoring(competitor['id'])
                    )
                    self.current_tasks.add(task)
                    
                    logger.info(f"Started daily monitoring for competitor {competitor.get('name', 'Unknown')} ({competitor['id']})")
                    
                except Exception as e:
                    logger.error(f"Error starting monitoring for competitor {competitor['id']}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error running daily scan for user {user_id}: {e}")
    
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
            
            # Check if supabase client is available
            if not supabase_client:
                logger.warning("⚠️ Supabase client not available - skipping scheduled scans")
                return
            
            # Get competitors that need scanning from Supabase
            due_competitors = await supabase_client.get_competitors_due_for_scan()
            
            if not due_competitors:
                # Log this only occasionally to avoid spam
                if not hasattr(self, '_last_no_competitors_log') or \
                   (datetime.now(timezone.utc) - getattr(self, '_last_no_competitors_log', datetime.min.replace(tzinfo=timezone.utc))).total_seconds() > 300:  # Log every 5 minutes
                    logger.info("✅ No competitors due for scanning (all users may have monitoring disabled)")
                    self._last_no_competitors_log = datetime.now(timezone.utc)
                return
            
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
            
            current_time = datetime.now(timezone.utc)
            
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
    
    async def trigger_immediate_scan_for_user(self, user_id: str) -> Dict[str, Any]:
        """Trigger an immediate scan for all competitors of a specific user"""
        try:
            logger.info(f"Triggering immediate scan for user {user_id}")
            
            # Get all competitors for the user
            competitors = await supabase_client.get_competitors_by_user(user_id)
            
            if not competitors:
                return {
                    "success": False,
                    "message": "No competitors found for this user"
                }
            
            # Check if we have capacity for all competitors
            if len(self.current_tasks) + len(competitors) > self.config.max_concurrent_scans:
                return {
                    "success": False,
                    "message": f"Insufficient capacity. Can only scan {self.config.max_concurrent_scans - len(self.current_tasks)} competitors at once."
                }
            
            # Start monitoring tasks for all competitors
            started_tasks = 0
            for competitor in competitors:
                try:
                    task = asyncio.create_task(
                        self._run_competitor_monitoring(competitor['id'])
                    )
                    self.current_tasks.add(task)
                    started_tasks += 1
                    
                    logger.info(f"Started immediate monitoring for competitor {competitor.get('name', 'Unknown')} ({competitor['id']})")
                    
                except Exception as e:
                    logger.error(f"Error starting monitoring for competitor {competitor['id']}: {e}")
                    continue
            
            return {
                "success": True,
                "message": f"Immediate scan started for {started_tasks} competitors",
                "competitors_scanned": started_tasks
            }
        
        except Exception as e:
            logger.error(f"Error in trigger_immediate_scan_for_user: {e}")
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
            "daily_scan_enabled": True,
            "daily_scan_time": self.config.daily_scan_time,
            "last_daily_scan": self.last_daily_scan.isoformat() if self.last_daily_scan else None,
            "next_daily_scan": self._calculate_next_daily_scan(),
            "scheduler_config": {
                "scan_interval_hours": self.config.daily_scan_interval_hours,
                "retry_after_minutes": self.config.retry_failed_after_minutes,
                "max_failures": self.config.max_consecutive_failures
            }
        }
    
    def _calculate_next_daily_scan(self) -> Optional[str]:
        """Calculate the next daily scan time"""
        try:
            now = datetime.now(timezone.utc)
            scan_time = datetime.strptime(self.config.daily_scan_time, "%H:%M").time()
            next_scan = datetime.combine(now.date(), scan_time, tzinfo=timezone.utc)
            
            # If today's scan time has passed, schedule for tomorrow
            if now.time() >= scan_time:
                next_scan = next_scan + timedelta(days=1)
            
            return next_scan.isoformat()
        except Exception as e:
            logger.error(f"Error calculating next daily scan: {e}")
            return None


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

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

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.competitor import Competitor
from app.models.monitoring import CompetitorMonitoringStatus
from .orchestrator import AgentMonitoringService
from app.core.database import get_db

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
            
            async for db in get_db():
                try:
                    # Get competitors that need scanning
                    due_competitors = await self._get_competitors_due_for_scan(db)
                    
                    for competitor in due_competitors:
                        if len(self.current_tasks) >= self.config.max_concurrent_scans:
                            break
                        
                        # Start monitoring task
                        task = asyncio.create_task(
                            self._run_competitor_monitoring(competitor.id, db)
                        )
                        self.current_tasks.add(task)
                        
                        logger.info(f"Started monitoring task for competitor {competitor.name} ({competitor.id})")
                    
                    break  # Exit the async generator loop
                    
                except Exception as e:
                    logger.error(f"Error processing scheduled scans: {e}")
                    await db.rollback()
        
        except Exception as e:
            logger.error(f"Error in _process_scheduled_scans: {e}")
    
    async def _get_competitors_due_for_scan(self, db: AsyncSession) -> List[Competitor]:
        """Get list of competitors that are due for scanning"""
        try:
            current_time = datetime.utcnow()
            
            # First get all active competitors with all attributes loaded
            query = select(Competitor).where(Competitor.status == 'active')
            result = await db.execute(query)
            all_competitors = result.scalars().all()
            
            # Ensure all competitors are properly loaded by accessing their attributes
            for comp in all_competitors:
                # Access key attributes to ensure they're loaded
                _ = comp.id, comp.scan_frequency_minutes, comp.last_scan_at
            
            # Filter competitors that need scanning based on Python logic
            competitors_due = []
            for competitor in all_competitors:
                try:
                    # Check if competitor is currently being scanned
                    status_query = await db.execute(
                        select(CompetitorMonitoringStatus).where(
                            CompetitorMonitoringStatus.competitor_id == competitor.id
                        )
                    )
                    status = status_query.scalar_one_or_none()
                    
                    if status and status.is_scanning:
                        continue  # Skip if currently being scanned
                    
                    if status and status.consecutive_failures and status.consecutive_failures >= self.config.max_consecutive_failures:
                        continue  # Skip if failed too many times
                    
                    # Check if due for scan (daily monitoring)
                    needs_scan = False
                    if not competitor.last_scan_at:
                        needs_scan = True
                    elif status and status.next_scheduled_scan and status.next_scheduled_scan <= current_time:
                        needs_scan = True
                    elif competitor.last_scan_at:
                        # Calculate if 24 hours have passed since last scan
                        next_scan_time = competitor.last_scan_at + timedelta(hours=self.config.daily_scan_interval_hours)
                        if next_scan_time <= current_time:
                            needs_scan = True
                    
                    if needs_scan:
                        competitors_due.append(competitor)
                        
                        if len(competitors_due) >= self.config.max_concurrent_scans:
                            break
                            
                except Exception as e:
                    logger.error(f"Error checking competitor {competitor.id} scan status: {e}")
                    continue
            
            return competitors_due
            
        except Exception as e:
            logger.error(f"Error getting competitors due for scan: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    async def _run_competitor_monitoring(self, competitor_id: str, db: AsyncSession):
        """Run monitoring for a specific competitor"""
        try:
            logger.info(f"Running monitoring for competitor {competitor_id}")
            
            # Create agent-based monitoring service
            monitoring_service = AgentMonitoringService(db)
            
            # Run monitoring
            result = await monitoring_service.run_monitoring_for_competitor(competitor_id)
            
            # Update next scheduled scan time
            await self._update_next_scan_time(competitor_id, db)
            
            logger.info(f"Completed monitoring for competitor {competitor_id}: {result['status']}")
            
        except Exception as e:
            logger.error(f"Error running monitoring for competitor {competitor_id}: {e}")
            # Update error status
            await self._handle_monitoring_error(competitor_id, str(e), db)
    
    async def _update_next_scan_time(self, competitor_id: str, db: AsyncSession):
        """Update the next scheduled scan time for a competitor"""
        try:
            # Get competitor scan frequency
            competitor_query = await db.execute(
                select(Competitor).where(Competitor.id == competitor_id)
            )
            competitor = competitor_query.scalar_one_or_none()
            
            if not competitor:
                return
            
            # Calculate next scan time (24 hours from now)
            next_scan_time = datetime.utcnow() + timedelta(hours=self.config.daily_scan_interval_hours)
            
            # Update monitoring status
            status_query = await db.execute(
                select(CompetitorMonitoringStatus).where(
                    CompetitorMonitoringStatus.competitor_id == competitor_id
                )
            )
            status = status_query.scalar_one_or_none()
            
            if status:
                status.next_scheduled_scan = next_scan_time
            else:
                # Create new status record
                status = CompetitorMonitoringStatus(
                    competitor_id=competitor_id,
                    next_scheduled_scan=next_scan_time
                )
                db.add(status)
            
            # Update competitor last scan time
            competitor.last_scan_at = datetime.utcnow()
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error updating next scan time for competitor {competitor_id}: {e}")
            await db.rollback()
    
    async def _handle_monitoring_error(self, competitor_id: str, error_message: str, db: AsyncSession):
        """Handle monitoring error for a competitor"""
        try:
            # Get or create monitoring status
            status_query = await db.execute(
                select(CompetitorMonitoringStatus).where(
                    CompetitorMonitoringStatus.competitor_id == competitor_id
                )
            )
            status = status_query.scalar_one_or_none()
            
            if not status:
                status = CompetitorMonitoringStatus(competitor_id=competitor_id)
                db.add(status)
            
            # Update error information
            status.last_failed_scan = datetime.utcnow()
            status.scan_error_message = error_message
            status.consecutive_failures = (status.consecutive_failures or 0) + 1
            status.is_scanning = False
            
            # Schedule retry (with backoff)
            retry_delay_minutes = min(
                self.config.retry_failed_after_minutes * status.consecutive_failures,
                self.config.retry_failed_after_minutes * 4  # Max 4x delay
            )
            status.next_scheduled_scan = datetime.utcnow() + timedelta(minutes=retry_delay_minutes)
            
            await db.commit()
            
            logger.warning(
                f"Monitoring error for competitor {competitor_id} "
                f"(failure #{status.consecutive_failures}): {error_message}"
            )
            
        except Exception as e:
            logger.error(f"Error handling monitoring error for competitor {competitor_id}: {e}")
            await db.rollback()
    
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
            
            # Reset scanning status for tasks that have been stuck too long (1 hour)
            async for db in get_db():
                try:
                    stuck_threshold = current_time - timedelta(hours=1)
                    
                    stuck_status_query = await db.execute(
                        select(CompetitorMonitoringStatus).where(
                            and_(
                                CompetitorMonitoringStatus.is_scanning == True,
                                CompetitorMonitoringStatus.scan_started_at < stuck_threshold
                            )
                        )
                    )
                    stuck_statuses = stuck_status_query.scalars().all()
                    
                    for status in stuck_statuses:
                        status.is_scanning = False
                        status.scan_error_message = "Scan timeout - reset by maintenance"
                        logger.warning(f"Reset stuck scanning status for competitor {status.competitor_id}")
                    
                    if stuck_statuses:
                        await db.commit()
                    
                    break  # Exit the async generator loop
                    
                except Exception as e:
                    logger.error(f"Error in maintenance tasks: {e}")
                    await db.rollback()
        
        except Exception as e:
            logger.error(f"Error performing maintenance: {e}")
    
    async def trigger_immediate_scan(self, competitor_id: str) -> Dict[str, Any]:
        """Trigger an immediate scan for a specific competitor"""
        try:
            async for db in get_db():
                try:
                    # Check if competitor exists and is not currently being scanned
                    status_query = await db.execute(
                        select(CompetitorMonitoringStatus).where(
                            CompetitorMonitoringStatus.competitor_id == competitor_id
                        )
                    )
                    status = status_query.scalar_one_or_none()
                    
                    if status and status.is_scanning:
                        return {
                            "success": False,
                            "message": "Competitor is already being scanned"
                        }
                    
                    # Start immediate monitoring task
                    task = asyncio.create_task(
                        self._run_competitor_monitoring(competitor_id, db)
                    )
                    self.current_tasks.add(task)
                    
                    return {
                        "success": True,
                        "message": f"Immediate scan started for competitor {competitor_id}"
                    }
                    
                except Exception as e:
                    logger.error(f"Error triggering immediate scan: {e}")
                    return {
                        "success": False,
                        "message": f"Error starting scan: {str(e)}"
                    }
        
        except Exception as e:
            logger.error(f"Error in trigger_immediate_scan: {e}")
            return {
                "success": False,
                "message": f"Database error: {str(e)}"
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

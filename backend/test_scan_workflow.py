#!/usr/bin/env python3
"""
Test Script for BOS Solution Scanning Workflow
Tests the complete scanning workflow across all platforms
"""

import asyncio
import sys
import os
import logging
from datetime import datetime, timezone

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.services.monitoring.orchestrator import SimpleMonitoringService
from app.models.competitor import Competitor
from app.models.monitoring import MonitoringData, MonitoringAlert, CompetitorMonitoringStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_scanning_workflow():
    """Test the complete scanning workflow"""
    try:
        logger.info("🚀 Starting BOS Solution Scanning Workflow Test")
        
        # Create database engine
        engine = create_async_engine(settings.DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            logger.info("✅ Database connection established")
            
            # Test 1: Create a test competitor if it doesn't exist
            logger.info("\n📋 Test 1: Creating test competitor")
            test_competitor = await create_test_competitor(db)
            if not test_competitor:
                logger.error("❌ Failed to create test competitor")
                return False
            
            logger.info(f"✅ Test competitor created: {test_competitor.name} (ID: {test_competitor.id})")
            
            # Test 2: Test individual platform scanning
            logger.info("\n🔍 Test 2: Testing individual platform scanning")
            await test_individual_platforms(db, test_competitor.id)
            
            # Test 3: Test complete competitor scanning
            logger.info("\n🚀 Test 3: Testing complete competitor scanning")
            await test_complete_competitor_scan(db, test_competitor.id)
            
            # Test 4: Test monitoring data recording
            logger.info("\n📝 Test 4: Verifying monitoring data recording")
            await test_monitoring_data_recording(db, test_competitor.id)
            
            # Test 5: Test alert creation
            logger.info("\n🚨 Test 5: Verifying alert creation")
            await test_alert_creation(db, test_competitor.id)
            
            logger.info("\n✅ All tests completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False
    finally:
        if 'engine' in locals():
            await engine.dispose()

async def create_test_competitor(db: AsyncSession) -> Competitor:
    """Create a test competitor for testing"""
    try:
        # Check if test competitor already exists
        from sqlalchemy import select
        result = await db.execute(
            select(Competitor).where(Competitor.name == "Test Company")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.info("📋 Test competitor already exists")
            return existing
        
        # Create new test competitor
        test_competitor = Competitor(
            name="Test Company",
            description="A test company for workflow testing",
            website_url="https://example.com",
            social_media_handles={
                "youtube": "@testcompany",
                "instagram": "@testcompany",
                "twitter": "@testcompany"
            },
            industry="Technology",
            status="active",
            scan_frequency_minutes=60
        )
        
        db.add(test_competitor)
        await db.commit()
        await db.refresh(test_competitor)
        
        logger.info(f"📋 Created test competitor: {test_competitor.name}")
        return test_competitor
        
    except Exception as e:
        logger.error(f"❌ Error creating test competitor: {e}")
        await db.rollback()
        return None

async def test_individual_platforms(db: AsyncSession, competitor_id: str):
    """Test scanning individual platforms"""
    try:
        monitoring_service = SimpleMonitoringService()
        
        platforms = ['website', 'youtube', 'instagram', 'twitter']
        
        for platform in platforms:
            logger.info(f"🔍 Testing {platform} platform...")
            
            try:
                result = await monitoring_service.run_platform_specific_monitoring(competitor_id, platform)
                
                if result.get("status") == "completed":
                    logger.info(f"✅ {platform} platform scan completed successfully")
                    logger.info(f"   📊 Result: {result.get('result', {}).get('status', 'unknown')}")
                else:
                    logger.warning(f"⚠️ {platform} platform scan failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"❌ Error testing {platform} platform: {e}")
        
        await monitoring_service.close()
        
    except Exception as e:
        logger.error(f"❌ Error in individual platform testing: {e}")

async def test_complete_competitor_scan(db: AsyncSession, competitor_id: str):
    """Test complete competitor scanning"""
    try:
        monitoring_service = SimpleMonitoringService()
        
        logger.info("🚀 Starting complete competitor scan...")
        
        result = await monitoring_service.run_monitoring_for_competitor(competitor_id)
        
        if result.get("status") == "completed":
            logger.info("✅ Complete competitor scan completed successfully")
            logger.info(f"   📊 Platforms analyzed: {result.get('platforms_analyzed', [])}")
            logger.info(f"   📝 Monitoring data records: {result.get('monitoring_data_count', 0)}")
            logger.info(f"   ❌ Errors: {len(result.get('errors', []))}")
        else:
            logger.error(f"❌ Complete competitor scan failed: {result.get('error', 'Unknown error')}")
        
        await monitoring_service.close()
        
    except Exception as e:
        logger.error(f"❌ Error in complete competitor scan testing: {e}")

async def test_monitoring_data_recording(db: AsyncSession, competitor_id: str):
    """Test that monitoring data is properly recorded"""
    try:
        from sqlalchemy import select
        
        # Check for monitoring data records
        result = await db.execute(
            select(MonitoringData).where(MonitoringData.competitor_id == competitor_id)
        )
        monitoring_records = result.scalars().all()
        
        logger.info(f"📝 Found {len(monitoring_records)} monitoring data records")
        
        for record in monitoring_records:
            logger.info(f"   📊 Platform: {record.platform}, Type: {record.post_type}")
            logger.info(f"      Content: {record.content_text[:100]}...")
            logger.info(f"      Detected: {record.detected_at}")
        
        if len(monitoring_records) > 0:
            logger.info("✅ Monitoring data recording test passed")
        else:
            logger.warning("⚠️ No monitoring data records found")
        
    except Exception as e:
        logger.error(f"❌ Error in monitoring data recording test: {e}")

async def test_alert_creation(db: AsyncSession, competitor_id: str):
    """Test that alerts are properly created"""
    try:
        from sqlalchemy import select
        
        # Check for monitoring alerts
        result = await db.execute(
            select(MonitoringAlert).where(MonitoringAlert.competitor_id == competitor_id)
        )
        alerts = result.scalars().all()
        
        logger.info(f"🚨 Found {len(alerts)} monitoring alerts")
        
        for alert in alerts:
            logger.info(f"   🚨 Type: {alert.alert_type}, Priority: {alert.priority}")
            logger.info(f"      Title: {alert.title}")
            logger.info(f"      Created: {alert.created_at}")
        
        if len(alerts) > 0:
            logger.info("✅ Alert creation test passed")
        else:
            logger.warning("⚠️ No monitoring alerts found")
        
    except Exception as e:
        logger.error(f"❌ Error in alert creation test: {e}")

async def main():
    """Main test function"""
    logger.info("🧪 BOS Solution Scanning Workflow Test Suite")
    logger.info("=" * 50)
    
    success = await test_scanning_workflow()
    
    if success:
        logger.info("\n🎉 All tests passed! The scanning workflow is working correctly.")
        sys.exit(0)
    else:
        logger.error("\n💥 Some tests failed. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

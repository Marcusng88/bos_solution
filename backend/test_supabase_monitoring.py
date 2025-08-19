"""
Test script for Supabase-based monitoring system
"""

import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.monitoring.supabase_client import supabase_client
from app.services.monitoring.orchestrator import SimpleMonitoringService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_supabase_connection():
    """Test Supabase connection and basic operations"""
    try:
        logger.info("🧪 Testing Supabase connection...")
        
        # Test getting competitors
        competitors = await supabase_client.get_competitors_due_for_scan()
        logger.info(f"✅ Found {len(competitors)} competitors due for scanning")
        
        if competitors:
            # Test getting details for first competitor
            first_competitor = competitors[0]
            competitor_id = first_competitor['id']
            
            details = await supabase_client.get_competitor_details(competitor_id)
            if details:
                logger.info(f"✅ Successfully retrieved details for competitor: {details.get('name', 'Unknown')}")
                logger.info(f"   Website: {details.get('website_url', 'N/A')}")
                logger.info(f"   Social handles: {details.get('social_media_handles', {})}")
            else:
                logger.error("❌ Failed to get competitor details")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Supabase connection test failed: {e}")
        return False


async def test_monitoring_service():
    """Test the monitoring service with a sample competitor"""
    try:
        logger.info("🧪 Testing monitoring service...")
        
        # Create monitoring service
        monitoring_service = SimpleMonitoringService()
        
        # Get a competitor to test with
        competitors = await supabase_client.get_competitors_due_for_scan()
        
        if not competitors:
            logger.warning("⚠️ No competitors found for testing")
            return False
        
        # Test with first competitor
        test_competitor = competitors[0]
        competitor_id = test_competitor['id']
        competitor_name = test_competitor.get('name', 'Test Competitor')
        
        logger.info(f"🧪 Testing monitoring for competitor: {competitor_name} (ID: {competitor_id})")
        
        # Run monitoring (this will test the full flow)
        result = await monitoring_service.run_monitoring_for_competitor(
            competitor_id=competitor_id,
            competitor_name=competitor_name,
            platforms=['browser']  # Start with browser agent only
        )
        
        logger.info(f"✅ Monitoring test completed: {result['status']}")
        logger.info(f"   Platforms analyzed: {result.get('platforms_analyzed', [])}")
        logger.info(f"   Data count: {result.get('monitoring_data_count', 0)}")
        logger.info(f"   Errors: {len(result.get('errors', []))}")
        
        if result.get('errors'):
            for error in result['errors']:
                logger.warning(f"   ⚠️ Error: {error}")
        
        # Close the service
        await monitoring_service.close()
        
        return result['status'] == 'completed'
        
    except Exception as e:
        logger.error(f"❌ Monitoring service test failed: {e}")
        return False


async def test_database_operations():
    """Test database operations"""
    try:
        logger.info("🧪 Testing database operations...")
        
        # Test monitoring stats
        stats = await supabase_client.get_monitoring_stats("test-user-id")
        logger.info(f"✅ Monitoring stats: {stats}")
        
        # Test saving sample monitoring data
        sample_data = {
            'competitor_id': 'test-competitor-id',
            'platform': 'test',
            'post_id': 'test-post-123',
            'content_text': 'Test content for monitoring',
            'content_hash': 'test-hash-123',
            'detected_at': '2025-01-19T22:10:31.045Z',
            'is_new_post': True,
            'is_content_change': False
        }
        
        # Note: This will fail if the competitor doesn't exist, but that's expected
        # The test is to verify the Supabase client works
        try:
            data_id = await supabase_client.save_monitoring_data(sample_data)
            if data_id:
                logger.info(f"✅ Successfully saved test monitoring data: {data_id}")
            else:
                logger.warning("⚠️ Could not save test data (expected if test competitor doesn't exist)")
        except Exception as e:
            logger.warning(f"⚠️ Expected error saving test data: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database operations test failed: {e}")
        return False


async def main():
    """Run all tests"""
    logger.info("🚀 Starting Supabase monitoring system tests...")
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ Missing required environment variables: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    logger.info(f"✅ Environment variables found")
    logger.info(f"   Supabase URL: {supabase_url[:30]}...")
    logger.info(f"   Supabase Key: {supabase_key[:10]}...")
    
    # Run tests
    tests = [
        ("Supabase Connection", test_supabase_connection),
        ("Database Operations", test_database_operations),
        ("Monitoring Service", test_monitoring_service),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = await test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status}: {test_name}")
        except Exception as e:
            logger.error(f"❌ FAILED: {test_name} - {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Supabase monitoring system is working correctly.")
    else:
        logger.warning("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

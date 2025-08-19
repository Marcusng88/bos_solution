"""
Test script to verify all agents work without SQLAlchemy dependencies
"""

import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.monitoring.agents.sub_agents.youtube_agent import YouTubeAgent
from app.services.monitoring.agents.sub_agents.website_agent import WebsiteAgent
from app.services.monitoring.agents.sub_agents.browser_agent import BrowserAgent
from app.services.monitoring.agents.sub_agents.instagram_agent import InstagramAgent
from app.services.monitoring.agents.sub_agents.twitter_agent import TwitterAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_youtube_agent():
    """Test YouTube agent without SQLAlchemy"""
    try:
        logger.info("🧪 Testing YouTube agent...")
        
        agent = YouTubeAgent()
        logger.info("✅ YouTube agent created successfully")
        
        # Test analysis with a sample competitor
        result = await agent.analyze_competitor(
            competitor_id="test-competitor-123",
            competitor_name="Test Company"
        )
        
        logger.info(f"✅ YouTube analysis completed: {result['status']}")
        logger.info(f"   Posts found: {len(result.get('posts', []))}")
        
        await agent.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ YouTube agent test failed: {e}")
        return False


async def test_website_agent():
    """Test Website agent without SQLAlchemy"""
    try:
        logger.info("🧪 Testing Website agent...")
        
        agent = WebsiteAgent()
        logger.info("✅ Website agent created successfully")
        
        # Test analysis with a sample URL
        result = await agent.analyze_competitor(
            competitor_id="test-competitor-123",
            url="https://example.com"
        )
        
        logger.info(f"✅ Website analysis completed: {result['status']}")
        logger.info(f"   Content items: {len(result.get('content', []))}")
        
        await agent.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Website agent test failed: {e}")
        return False


async def test_browser_agent():
    """Test Browser agent without SQLAlchemy"""
    try:
        logger.info("🧪 Testing Browser agent...")
        
        agent = BrowserAgent()
        logger.info("✅ Browser agent created successfully")
        
        # Test analysis with a sample competitor
        result = await agent.analyze_competitor(
            competitor_id="test-competitor-123",
            competitor_name="Test Company"
        )
        
        logger.info(f"✅ Browser analysis completed: {result['status']}")
        logger.info(f"   Content items: {len(result.get('content', []))}")
        
        await agent.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Browser agent test failed: {e}")
        return False


async def test_instagram_agent():
    """Test Instagram agent without SQLAlchemy"""
    try:
        logger.info("🧪 Testing Instagram agent...")
        
        agent = InstagramAgent()
        logger.info("✅ Instagram agent created successfully")
        
        # Test analysis with a sample handle
        result = await agent.analyze_competitor(
            competitor_id="test-competitor-123",
            instagram_handle="testcompany"
        )
        
        logger.info(f"✅ Instagram analysis completed: {result['status']}")
        logger.info(f"   Posts found: {len(result.get('posts', []))}")
        
        await agent.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Instagram agent test failed: {e}")
        return False


async def test_twitter_agent():
    """Test Twitter agent without SQLAlchemy"""
    try:
        logger.info("🧪 Testing Twitter agent...")
        
        agent = TwitterAgent()
        logger.info("✅ Twitter agent created successfully")
        
        # Test analysis with a sample handle
        result = await agent.analyze_competitor(
            competitor_id="test-competitor-123",
            twitter_handle="testcompany"
        )
        
        logger.info(f"✅ Twitter analysis completed: {result['status']}")
        logger.info(f"   Posts found: {len(result.get('posts', []))}")
        
        await agent.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Twitter agent test failed: {e}")
        return False


async def main():
    """Run all agent tests"""
    logger.info("🚀 Starting agent tests (no SQLAlchemy)...")
    
    # Run tests
    tests = [
        ("YouTube Agent", test_youtube_agent),
        ("Website Agent", test_website_agent),
        ("Browser Agent", test_browser_agent),
        ("Instagram Agent", test_instagram_agent),
        ("Twitter Agent", test_twitter_agent),
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
        logger.info("🎉 All agents work without SQLAlchemy! Supabase-based system is ready.")
    else:
        logger.warning("⚠️ Some agents failed. Check the logs above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

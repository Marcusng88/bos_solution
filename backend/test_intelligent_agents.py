#!/usr/bin/env python3
"""
Test script for intelligent AI agents
Verifies all agents can be initialized and run without SQLAlchemy dependencies
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import Windows compatibility
from app.core.windows_compatibility import setup_windows_compatibility

# Try to import the intelligent agents
try:
    from app.services.monitoring.agents.sub_agents.youtube_agent import YouTubeAgent
    from app.services.monitoring.agents.sub_agents.browser_agent import BrowserAgent
    from app.services.monitoring.agents.sub_agents.website_agent import WebsiteAgent
    from app.services.monitoring.agents.sub_agents.instagram_agent import InstagramAgent
    from app.services.monitoring.agents.sub_agents.twitter_agent import TwitterAgent
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Error importing agents: {e}")
    print("💡 Please install required packages: pip install -r requirements.txt")
    AGENTS_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


async def test_agent(agent_class, agent_name: str, competitor_id: str = "test-123", competitor_name: str = "TestCompany"):
    """Test an individual agent"""
    try:
        logger.info(f"\n🧪 Testing {agent_name}...")
        
        # Initialize agent
        agent = agent_class()
        logger.info(f"✅ {agent_name} initialized successfully")
        
        # Test analyze_competitor method
        result = await agent.analyze_competitor(competitor_id, competitor_name)
        
        # Validate result structure
        required_fields = ['platform', 'competitor_id', 'status', 'posts']
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            logger.error(f"❌ {agent_name} missing required fields: {missing_fields}")
            return False
        
        # Check status
        if result['status'] not in ['completed', 'failed']:
            logger.error(f"❌ {agent_name} returned invalid status: {result['status']}")
            return False
        
        logger.info(f"✅ {agent_name} analysis completed successfully")
        logger.info(f"   Platform: {result['platform']}")
        logger.info(f"   Status: {result['status']}")
        logger.info(f"   Posts found: {len(result.get('posts', []))}")
        logger.info(f"   Summary: {result.get('analysis_summary', 'No summary')[:100]}...")
        
        # Close agent
        await agent.close()
        logger.info(f"✅ {agent_name} closed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ {agent_name} test failed: {e}")
        return False


async def test_all_intelligent_agents():
    """Test all intelligent AI agents"""
    logger.info("🚀 Starting intelligent agents test...")
    logger.info(f"   Test started at: {datetime.now()}")
    
    # Setup Windows compatibility
    setup_windows_compatibility()
    
    # List of agents to test
    agents_to_test = [
        (YouTubeAgent, "Intelligent YouTubeAgent"),
        (BrowserAgent, "Intelligent BrowserAgent"),
        (WebsiteAgent, "Intelligent WebsiteAgent"),
        (InstagramAgent, "Intelligent InstagramAgent"),
        (TwitterAgent, "Intelligent TwitterAgent"),
    ]
    
    results = {}
    
    for agent_class, agent_name in agents_to_test:
        success = await test_agent(agent_class, agent_name)
        results[agent_name] = success
    
    # Summary
    logger.info(f"\n📊 Test Results Summary:")
    logger.info(f"   Total agents tested: {len(results)}")
    
    successful_agents = [name for name, success in results.items() if success]
    failed_agents = [name for name, success in results.items() if not success]
    
    logger.info(f"   ✅ Successful: {len(successful_agents)}")
    for agent in successful_agents:
        logger.info(f"      - {agent}")
    
    if failed_agents:
        logger.info(f"   ❌ Failed: {len(failed_agents)}")
        for agent in failed_agents:
            logger.info(f"      - {agent}")
    else:
        logger.info(f"   🎉 All agents passed!")
    
    # Environment check
    logger.info(f"\n🔧 Environment Check:")
    env_vars = ['GOOGLE_API_KEY', 'YOUTUBE_API_KEY', 'TAVILY_API_KEY', 'SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    for var in env_vars:
        value = os.getenv(var)
        status = "✅ Set" if value else "❌ Missing"
        logger.info(f"   {var}: {status}")
    
    logger.info(f"\n✨ Intelligent agents test completed at: {datetime.now()}")
    
    return len(failed_agents) == 0


async def main():
    """Main test function"""
    try:
        if not AGENTS_AVAILABLE:
            logger.error("❌ Cannot run tests - agents not available due to import errors")
            logger.info("💡 Please install required packages: pip install -r requirements.txt")
            sys.exit(1)
        
        success = await test_all_intelligent_agents()
        if success:
            logger.info("🎉 All intelligent agents tests passed!")
            sys.exit(0)
        else:
            logger.error("❌ Some intelligent agents tests failed!")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

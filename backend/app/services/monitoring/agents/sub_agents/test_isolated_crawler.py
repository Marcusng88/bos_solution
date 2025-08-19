#!/usr/bin/env python3
"""
Test script for isolated crawler
This script tests the isolated crawler functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from app.services.monitoring.agents.sub_agents.isolated_crawler import IsolatedCrawler, crawl_websites_isolated

async def test_isolated_crawler():
    """Test the isolated crawler with a simple website"""
    print("🧪 Testing isolated crawler...")
    
    # Test URLs
    test_urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json"
    ]
    
    try:
        # Test single crawler instance
        print("\n🔒 Testing single crawler instance...")
        crawler = IsolatedCrawler()
        
        results = await crawler.crawl_websites(test_urls)
        print(f"✅ Single crawler results: {len(results)} items")
        
        for result in results:
            print(f"   - {result['url']}: {result['status']}")
            if result['status'] == 'success':
                print(f"     Title: {result.get('title', 'N/A')[:50]}...")
                print(f"     Content length: {len(result.get('content', ''))}")
        
        crawler.cleanup()
        
        # Test convenience function
        print("\n🔒 Testing convenience function...")
        results = await crawl_websites_isolated(test_urls)
        print(f"✅ Convenience function results: {len(results)} items")
        
        for result in results:
            print(f"   - {result['url']}: {result['status']}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_with_extraction():
    """Test the isolated crawler with LLM extraction"""
    print("\n🧪 Testing isolated crawler with LLM extraction...")
    
    # Test URLs
    test_urls = ["https://httpbin.org/html"]
    
    # Mock extraction config (you'll need to provide real API key)
    extraction_config = {
        'use_llm': False,  # Set to False for testing without API key
        'api_key': 'test_key',
        'schema': {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "main_content": {"type": "string"}
            }
        }
    }
    
    try:
        results = await crawl_websites_isolated(test_urls, extraction_config)
        print(f"✅ Extraction test results: {len(results)} items")
        
        for result in results:
            print(f"   - {result['url']}: {result['status']}")
            if result['status'] == 'success':
                print(f"     Extracted data keys: {list(result.get('extracted_data', {}).keys())}")
        
        print("🎉 Extraction test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting isolated crawler tests...")
    
    # Check if we're in the right environment
    try:
        import crawl4ai
        print(f"✅ crawl4ai available: {crawl4ai.__version__}")
    except ImportError:
        print("❌ crawl4ai not available. Please install it first.")
        print("Run: pip install crawl4ai")
        sys.exit(1)
    
    # Run tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Basic test
        success1 = loop.run_until_complete(test_isolated_crawler())
        
        # Extraction test
        success2 = loop.run_until_complete(test_with_extraction())
        
        if success1 and success2:
            print("\n🎉 All tests passed! The isolated crawler is working correctly.")
        else:
            print("\n❌ Some tests failed. Please check the error messages above.")
            sys.exit(1)
            
    finally:
        loop.close()

if __name__ == "__main__":
    main()

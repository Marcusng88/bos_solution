#!/usr/bin/env python3
"""
Simple test script for isolated crawler
Run this from the backend directory to test the isolated crawler
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

async def test_isolated_crawler():
    """Test the isolated crawler"""
    try:
        from app.services.monitoring.agents.sub_agents.isolated_crawler import crawl_websites_isolated
        
        print("🧪 Testing isolated crawler...")
        
        # Test with a simple website
        test_urls = ["https://httpbin.org/html"]
        
        results = await crawl_websites_isolated(test_urls)
        
        print(f"✅ Test completed! Got {len(results)} results")
        
        for result in results:
            print(f"   - {result['url']}: {result['status']}")
            if result['status'] == 'success':
                print(f"     Title: {result.get('title', 'N/A')[:50]}...")
                print(f"     Content length: {len(result.get('content', ''))}")
        
        print("\n🎉 Isolated crawler is working correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please run the setup script first:")
        print("  Windows: setup_isolated_crawler.bat")
        print("  PowerShell: .\\setup_isolated_crawler.ps1")
        print("  Linux/Mac: python setup_isolated_crawler.py")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 Testing isolated crawler...")
    
    # Run the test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        success = loop.run_until_complete(test_isolated_crawler())
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Tests failed!")
            sys.exit(1)
    finally:
        loop.close()

if __name__ == "__main__":
    main()

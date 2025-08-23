#!/usr/bin/env python3
"""
Test script for content generation across all four platforms
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_four_platforms():
    """Test content generation for all four platforms"""
    try:
        from app.services.content_planning.core_service import ContentPlanningService
        
        # Initialize the service
        service = ContentPlanningService()
        
        print("🔧 Testing content generation for all four platforms...")
        
        # Test platforms
        platforms = ['twitter', 'instagram', 'facebook', 'linkedin']
        content_types = ['promotional', 'educational', 'entertaining', 'promotional']
        
        for i, platform in enumerate(platforms):
            content_type = content_types[i]
            print(f"\n📱 Testing {platform.upper()} with {content_type} content...")
            
            # Test content generation
            result = await service.generate_content(
                clerk_id="test_user_123",
                platform=platform,
                content_type=content_type,
                tone="professional",
                target_audience="professionals",
                industry="Technology & Software",
                custom_requirements=f"Create engaging {content_type} content for {platform} to promote our new AI tool"
            )
            
            if result.get("success"):
                content = result.get("content", {})
                print(f"✅ {platform.upper()} content generated successfully!")
                print(f"📝 Content: {content.get('post_content', 'No content')[:100]}...")
                print(f"🏷️ Hashtags: {content.get('hashtags', [])}")
                print(f"⏰ Optimal time: {content.get('optimal_posting_time', 'Not specified')}")
                print(f"📊 Quality score: {content.get('content_quality_score', 'Not specified')}")
            else:
                print(f"❌ {platform.upper()} content generation failed: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_four_platforms())

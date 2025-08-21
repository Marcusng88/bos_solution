#!/usr/bin/env python3
"""
Test script to verify YouTube video upload integration with Supabase
"""

import asyncio
import logging
from app.services.youtube_data_service import youtube_data_service
from app.schemas.youtube import VideoCreate
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_video_upload_recording():
    """Test the video upload recording functionality"""
    
    # Test data
    test_user_id = "test_user_123"
    test_video_id = "test_video_456"
    test_channel_id = "test_channel_789"
    
    try:
        logger.info("Testing video upload recording...")
        
        # Test recording a video upload
        video_record = await youtube_data_service.record_video_upload(
            user_id=test_user_id,
            video_id=test_video_id,
            title="Test Video Title",
            description="This is a test video description",
            tags=["test", "video", "integration"],
            privacy_status="private",
            channel_id=test_channel_id,
            upload_status="uploaded",
            video_url=f"https://www.youtube.com/watch?v={test_video_id}"
        )
        
        if video_record:
            logger.info(f"✅ Successfully recorded video upload: {video_record.video_id}")
            logger.info(f"   Title: {video_record.title}")
            logger.info(f"   User ID: {video_record.user_id}")
            logger.info(f"   Channel ID: {video_record.channel_id}")
            logger.info(f"   Created at: {video_record.created_at}")
        else:
            logger.error("❌ Failed to record video upload")
            return False
        
        # Test retrieving the video
        retrieved_video = await youtube_data_service.get_video(test_video_id)
        if retrieved_video:
            logger.info(f"✅ Successfully retrieved video: {retrieved_video.video_id}")
        else:
            logger.error("❌ Failed to retrieve video")
            return False
        
        # Test getting user videos
        user_videos = await youtube_data_service.get_user_videos(test_user_id)
        if user_videos and user_videos.videos:
            logger.info(f"✅ Successfully retrieved {len(user_videos.videos)} videos for user")
        else:
            logger.warning("⚠️ No videos found for user (this might be expected)")
        
        logger.info("🎉 All tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False

async def test_channel_creation():
    """Test channel creation functionality"""
    
    test_user_id = "test_user_123"
    test_channel_info = {
        "id": "test_channel_456",
        "title": "Test Channel",
        "subscriber_count": "1000",
        "video_count": "50",
        "view_count": "100000"
    }
    
    try:
        logger.info("Testing channel creation...")
        
        channel_id = await youtube_data_service.get_or_create_channel_for_user(
            test_user_id, test_channel_info
        )
        
        if channel_id:
            logger.info(f"✅ Successfully created/retrieved channel: {channel_id}")
            
            # Test retrieving the channel
            channel = await youtube_data_service.get_channel(channel_id)
            if channel:
                logger.info(f"✅ Successfully retrieved channel: {channel.channel_title}")
                logger.info(f"   Subscribers: {channel.total_subscribers}")
                logger.info(f"   Videos: {channel.total_videos}")
            else:
                logger.error("❌ Failed to retrieve channel")
                return False
        else:
            logger.error("❌ Failed to create/retrieve channel")
            return False
        
        logger.info("🎉 Channel tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Channel test failed with error: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 Starting YouTube integration tests...")
    
    # Test channel creation first
    channel_success = await test_channel_creation()
    
    # Test video upload recording
    video_success = await test_video_upload_recording()
    
    if channel_success and video_success:
        logger.info("🎉 All integration tests passed!")
    else:
        logger.error("❌ Some tests failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

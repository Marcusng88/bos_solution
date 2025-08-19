#!/usr/bin/env python3
"""
YouTube Debug Utilities - Test YouTube ROI Analytics with Real Data
Run this script to test YouTube integration with actual OAuth tokens
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class YouTubeDebugger:
    """Debug utility for YouTube API integration"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        
    async def test_connection(self) -> bool:
        """Test if the backend server is running"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health", timeout=5.0)
                if response.status_code == 200:
                    print("✅ Backend server is running")
                    return True
                else:
                    print(f"❌ Backend server responded with status: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Failed to connect to backend: {e}")
            return False
    
    async def get_auth_url(self) -> Optional[str]:
        """Get YouTube OAuth authorization URL"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/youtube/auth/url")
                
                if response.status_code == 200:
                    data = response.json()
                    auth_url = data.get("auth_url")
                    print(f"✅ Generated OAuth URL: {auth_url}")
                    return auth_url
                else:
                    print(f"❌ Failed to get auth URL: {response.text}")
                    return None
        except Exception as e:
            print(f"❌ Error getting auth URL: {e}")
            return None
    
    def set_access_token(self, token: str):
        """Set access token for API calls"""
        self.access_token = token
        print(f"✅ Access token set: {token[:20]}...")
    
    async def test_channel_info(self) -> Optional[Dict]:
        """Test basic channel information retrieval"""
        if not self.access_token:
            print("❌ No access token set. Use set_access_token() first.")
            return None
            
        try:
            # Use the YouTube Data API directly to test channel info
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/youtube/v3/channels",
                    params={
                        "part": "snippet,statistics",
                        "mine": "true"
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("items"):
                        channel = data["items"][0]
                        channel_info = {
                            "id": channel["id"],
                            "title": channel["snippet"]["title"],
                            "subscriber_count": channel["statistics"].get("subscriberCount", "0"),
                            "video_count": channel["statistics"].get("videoCount", "0"),
                            "view_count": channel["statistics"].get("viewCount", "0")
                        }
                        
                        print("✅ Channel Information:")
                        print(f"   Title: {channel_info['title']}")
                        print(f"   Subscribers: {int(channel_info['subscriber_count']):,}")
                        print(f"   Videos: {channel_info['video_count']}")
                        print(f"   Total Views: {int(channel_info['view_count']):,}")
                        
                        return channel_info
                    else:
                        print("❌ No channel found in response")
                        return None
                else:
                    print(f"❌ Failed to get channel info: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error testing channel info: {e}")
            return None
    
    async def test_recent_activity(self, hours_back: int = 24) -> Optional[Dict]:
        """Test the enhanced recent activity endpoint"""
        if not self.access_token:
            print("❌ No access token set")
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/youtube/recent-activity",
                    params={
                        "access_token": self.access_token,
                        "hours_back": hours_back
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    print(f"\n✅ Recent Activity (Last {hours_back} hours):")
                    print(f"   Total Activities: {data.get('total_activities', 0)}")
                    print(f"   Cutoff Time: {data.get('cutoff_time')}")
                    
                    # Display channel analytics
                    if 'channel_analytics' in data:
                        channel = data['channel_analytics']
                        print(f"\n📊 Channel Analytics:")
                        print(f"   Subscribers: {channel.get('total_subscribers', 0):,}")
                        print(f"   Total Videos: {channel.get('total_videos', 0)}")
                        print(f"   Total Views: {channel.get('total_views', 0):,}")
                    
                    # Display ROI summary
                    if 'roi_summary' in data:
                        roi = data['roi_summary']
                        print(f"\n💰 ROI Summary:")
                        print(f"   Recent Views: {roi.get('total_recent_views', 0):,}")
                        print(f"   Recent Likes: {roi.get('total_recent_likes', 0):,}")
                        print(f"   Recent Comments: {roi.get('total_recent_comments', 0):,}")
                        print(f"   Avg Engagement Rate: {roi.get('avg_engagement_rate', 0)}%")
                        print(f"   Videos Analyzed: {roi.get('videos_analyzed', 0)}")
                    
                    # Display individual activities
                    for i, activity in enumerate(data.get('recent_activity', []), 1):
                        print(f"\n🎬 Activity {i}: {activity.get('type')}")
                        print(f"   Title: {activity.get('title', 'N/A')[:60]}...")
                        print(f"   Video ID: {activity.get('video_id')}")
                        
                        if 'roi_metrics' in activity:
                            roi_metrics = activity['roi_metrics']
                            print(f"   📈 ROI Metrics:")
                            print(f"      Engagement Rate: {roi_metrics.get('engagement_rate', 0)}%")
                            print(f"      Likes per View: {roi_metrics.get('likes_per_view', 0)}%")
                            print(f"      Watch Time: {roi_metrics.get('estimated_watch_time_hours', 0):.1f} hours")
                        
                        if 'comment_analytics' in activity:
                            comments = activity['comment_analytics']
                            print(f"   💬 Comment Analytics:")
                            print(f"      Recent Comments: {comments.get('total_comments_in_timeframe', 0)}")
                            print(f"      Comment Likes: {comments.get('total_comment_likes', 0)}")
                            print(f"      Avg Length: {comments.get('avg_comment_length', 0)} chars")
                            
                            types = comments.get('engagement_types', {})
                            print(f"      Questions: {types.get('questions', 0)}")
                            print(f"      Compliments: {types.get('compliments', 0)}")
                            print(f"      Requests: {types.get('requests', 0)}")
                    
                    return data
                else:
                    print(f"❌ Recent activity failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error testing recent activity: {e}")
            return None
    
    async def test_roi_dashboard(self, days_back: int = 30) -> Optional[Dict]:
        """Test the comprehensive ROI dashboard endpoint"""
        if not self.access_token:
            print("❌ No access token set")
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/youtube/analytics/roi-dashboard",
                    params={
                        "access_token": self.access_token,
                        "days_back": days_back,
                        "include_estimated_revenue": True
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    roi_analytics = data.get('roi_analytics', {})
                    
                    print(f"\n🏆 ROI Dashboard (Last {days_back} days):")
                    print(f"   Analysis Period: {data.get('analysis_period')}")
                    print(f"   Generated: {data.get('generated_at')}")
                    
                    # Channel Overview
                    if 'channel_overview' in roi_analytics:
                        overview = roi_analytics['channel_overview']
                        print(f"\n🏢 Channel Overview:")
                        print(f"   Channel: {overview.get('channel_title', 'N/A')}")
                        print(f"   Subscribers: {overview.get('total_subscribers', 0):,}")
                        print(f"   Total Videos: {overview.get('total_videos', 0)}")
                        print(f"   Total Views: {overview.get('total_views', 0):,}")
                    
                    # Performance Metrics
                    if 'performance_metrics' in roi_analytics:
                        perf = roi_analytics['performance_metrics']
                        print(f"\n📊 Performance Metrics:")
                        print(f"   Period Views: {perf.get('total_views_period', 0):,}")
                        print(f"   Period Likes: {perf.get('total_likes_period', 0):,}")
                        print(f"   Period Comments: {perf.get('total_comments_period', 0):,}")
                        print(f"   Watch Time: {perf.get('total_watch_time_hours', 0):.1f} hours")
                        print(f"   Avg Engagement: {perf.get('avg_engagement_rate', 0)}%")
                        print(f"   Videos Analyzed: {perf.get('videos_analyzed', 0)}")
                        
                        if perf.get('top_performing_video'):
                            top_video = perf['top_performing_video']
                            print(f"\n🥇 Top Performing Video:")
                            print(f"      Title: {top_video.get('title', 'N/A')[:50]}...")
                            print(f"      ROI Score: {top_video.get('roi_score', 0):.1f}")
                            print(f"      Engagement: {top_video.get('engagement_rate', 0)}%")
                    
                    # Engagement Analytics
                    if 'engagement_analytics' in roi_analytics:
                        engagement = roi_analytics['engagement_analytics']
                        print(f"\n💡 Engagement Analytics:")
                        print(f"   Likes-to-Views: {engagement.get('likes_to_views_ratio', 0):.4f}%")
                        print(f"   Comments-to-Views: {engagement.get('comments_to_views_ratio', 0):.4f}%")
                    
                    # Revenue Estimates
                    if 'revenue_estimates' in roi_analytics and roi_analytics['revenue_estimates']:
                        revenue = roi_analytics['revenue_estimates']
                        print(f"\n💰 Revenue Estimates:")
                        print(f"   Monthly Revenue: ${revenue.get('estimated_monthly_revenue', 0):.2f}")
                        print(f"   Annual Revenue: ${revenue.get('estimated_annual_revenue', 0):.2f}")
                        print(f"   Revenue/Subscriber: ${revenue.get('revenue_per_subscriber', 0):.4f}")
                        print(f"   RPM: ${revenue.get('estimated_rpm', 0)}")
                    
                    # Content Insights
                    if 'content_insights' in roi_analytics:
                        content = roi_analytics['content_insights']
                        print(f"\n🎯 Content Insights:")
                        optimal_length = content.get('optimal_video_length', 0)
                        print(f"   Optimal Length: {int(optimal_length//60)}:{int(optimal_length%60):02d}")
                        
                        tags = content.get('best_performing_tags', [])
                        if tags:
                            print(f"   Top Tags: {', '.join([f'{tag['tag']}({tag['count']})' for tag in tags[:5]])}")
                    
                    # ROI Recommendations
                    if 'roi_recommendations' in roi_analytics:
                        recommendations = roi_analytics['roi_recommendations']
                        print(f"\n💡 ROI Recommendations:")
                        for i, rec in enumerate(recommendations, 1):
                            print(f"   {i}. [{rec.get('priority', 'Medium')} Priority] {rec.get('category', 'General')}")
                            print(f"      {rec.get('recommendation', 'No recommendation')}")
                            print(f"      Impact: {rec.get('expected_impact', 'Unknown')}")
                    
                    # Top Video Performances
                    video_performances = data.get('video_performances', [])
                    if video_performances:
                        print(f"\n🎬 Top Video Performances:")
                        for i, video in enumerate(video_performances[:5], 1):
                            print(f"   {i}. {video.get('title', 'Untitled')[:40]}...")
                            print(f"      Views: {video.get('views', 0):,} | Engagement: {video.get('engagement_rate', 0):.1f}%")
                            print(f"      ROI Score: {video.get('roi_score', 0):.1f}")
                    
                    return data
                else:
                    print(f"❌ ROI dashboard failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error testing ROI dashboard: {e}")
            return None
    
    async def run_full_debug_suite(self, hours_back: int = 24, days_back: int = 30):
        """Run complete debug suite"""
        print("🚀 Starting YouTube Debug Suite")
        print("=" * 60)
        
        # Test server connection
        if not await self.test_connection():
            print("❌ Cannot continue without backend connection")
            return
        
        # Get OAuth URL
        auth_url = await self.get_auth_url()
        if not auth_url:
            print("❌ Cannot get OAuth URL")
            return
        
        # Prompt for access token
        if not self.access_token:
            print(f"\n🔗 OAuth URL: {auth_url}")
            print("\n📝 INSTRUCTIONS:")
            print("1. Visit the OAuth URL above")
            print("2. Complete the authorization")
            print("3. Get your access token from the callback")
            print("4. Run this script with the access token")
            return
        
        # Run tests
        print(f"\n🧪 Testing with access token: {self.access_token[:20]}...")
        
        # Test basic channel info
        await self.test_channel_info()
        
        # Test recent activity
        await self.test_recent_activity(hours_back)
        
        # Test ROI dashboard
        await self.test_roi_dashboard(days_back)
        
        print("\n✅ Debug suite completed!")
        print("=" * 60)


async def main():
    """Main debug function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube ROI Debug Tool')
    parser.add_argument('--token', type=str, help='YouTube access token')
    parser.add_argument('--hours', type=int, default=24, help='Hours back for recent activity')
    parser.add_argument('--days', type=int, default=30, help='Days back for ROI dashboard')
    parser.add_argument('--server', type=str, default='http://localhost:8000', help='Backend server URL')
    
    args = parser.parse_args()
    
    debugger = YouTubeDebugger(args.server)
    
    if args.token:
        debugger.set_access_token(args.token)
    
    await debugger.run_full_debug_suite(args.hours, args.days)


if __name__ == "__main__":
    asyncio.run(main())

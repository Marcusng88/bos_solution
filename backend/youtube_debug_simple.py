#!/usr/bin/env python3
"""
Simple YouTube Debug Script - Test with real access token
Usage: python youtube_debug_simple.py YOUR_ACCESS_TOKEN
"""

import requests
import sys
import json
from datetime import datetime

class SimpleYouTubeDebugger:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
    
    def test_server(self):
        """Test if backend server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server is running")
                return True
            else:
                print(f"❌ Server error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            return False
    
    def set_token(self, token):
        """Set access token"""
        self.access_token = token
        print(f"✅ Token set: {token[:20]}...")
    
    def test_basic_channel(self):
        """Test basic channel info directly with Google API"""
        if not self.access_token:
            print("❌ No token set")
            return None
            
        try:
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part": "snippet,statistics",
                    "mine": "true"
                },
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    channel = data["items"][0]
                    print("\n✅ CHANNEL INFO:")
                    print(f"   📺 Title: {channel['snippet']['title']}")
                    print(f"   👥 Subscribers: {int(channel['statistics'].get('subscriberCount', '0')):,}")
                    print(f"   🎬 Videos: {channel['statistics'].get('videoCount', '0')}")
                    print(f"   👀 Total Views: {int(channel['statistics'].get('viewCount', '0')):,}")
                    return channel
                else:
                    print("❌ No channel found")
                    return None
            else:
                print(f"❌ Channel API error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Channel test error: {e}")
            return None
    
    def test_recent_activity(self, hours=24):
        """Test recent activity endpoint"""
        if not self.access_token:
            print("❌ No token set")
            return None
            
        try:
            print(f"\n🔍 Testing Recent Activity (last {hours} hours)...")
            response = requests.get(
                f"{self.base_url}/api/v1/youtube/recent-activity",
                params={
                    "access_token": self.access_token,
                    "hours_back": hours
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ RECENT ACTIVITY SUCCESS:")
                print(f"   📊 Total Activities: {data.get('total_activities', 0)}")
                print(f"   🕐 Cutoff Time: {data.get('cutoff_time', 'N/A')}")
                
                # Channel Analytics
                if 'channel_analytics' in data:
                    ch = data['channel_analytics']
                    print(f"\n📈 CHANNEL ANALYTICS:")
                    print(f"   👥 Subscribers: {ch.get('total_subscribers', 0):,}")
                    print(f"   🎬 Videos: {ch.get('total_videos', 0)}")
                    print(f"   👀 Views: {ch.get('total_views', 0):,}")
                
                # ROI Summary
                if 'roi_summary' in data:
                    roi = data['roi_summary']
                    print(f"\n💰 ROI SUMMARY:")
                    print(f"   🔥 Recent Views: {roi.get('total_recent_views', 0):,}")
                    print(f"   ❤️ Recent Likes: {roi.get('total_recent_likes', 0):,}")
                    print(f"   💬 Recent Comments: {roi.get('total_recent_comments', 0):,}")
                    print(f"   📊 Avg Engagement: {roi.get('avg_engagement_rate', 0):.1f}%")
                    print(f"   🎥 Videos Analyzed: {roi.get('videos_analyzed', 0)}")
                
                # Individual Activities
                activities = data.get('recent_activity', [])
                print(f"\n🎬 ACTIVITIES ({len(activities)}):")
                for i, activity in enumerate(activities[:3], 1):  # Show first 3
                    print(f"\n   {i}. {activity.get('type', 'unknown').upper()}")
                    print(f"      📝 Title: {activity.get('title', 'N/A')[:50]}...")
                    print(f"      🆔 Video ID: {activity.get('video_id', 'N/A')}")
                    
                    if 'roi_metrics' in activity:
                        roi = activity['roi_metrics']
                        print(f"      📊 Engagement: {roi.get('engagement_rate', 0):.1f}%")
                        print(f"      ⚡ Views/Hour: {roi.get('views_per_hour_since_publish', 0):.1f}")
                        print(f"      ⏱️ Watch Time: {roi.get('estimated_watch_time_hours', 0):.1f}h")
                    
                    if 'comment_analytics' in activity:
                        comm = activity['comment_analytics']
                        print(f"      💬 New Comments: {comm.get('total_comments_in_timeframe', 0)}")
                        print(f"      ❤️ Comment Likes: {comm.get('total_comment_likes', 0)}")
                        
                        types = comm.get('engagement_types', {})
                        if any(types.values()):
                            print(f"      🏷️ Types: Q:{types.get('questions',0)} C:{types.get('compliments',0)} R:{types.get('requests',0)}")
                
                return data
            else:
                print(f"❌ Recent Activity failed: {response.status_code}")
                print(f"Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Recent activity error: {e}")
            return None
    
    def test_roi_dashboard(self, days=7):
        """Test ROI dashboard endpoint"""
        if not self.access_token:
            print("❌ No token set")
            return None
            
        try:
            print(f"\n🏆 Testing ROI Dashboard (last {days} days)...")
            response = requests.get(
                f"{self.base_url}/api/v1/youtube/analytics/roi-dashboard",
                params={
                    "access_token": self.access_token,
                    "days_back": days,
                    "include_estimated_revenue": True
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                analytics = data.get('roi_analytics', {})
                
                print("✅ ROI DASHBOARD SUCCESS:")
                
                # Channel Overview
                if 'channel_overview' in analytics:
                    overview = analytics['channel_overview']
                    print(f"\n🏢 CHANNEL OVERVIEW:")
                    print(f"   📺 Channel: {overview.get('channel_title', 'N/A')}")
                    print(f"   👥 Subscribers: {overview.get('total_subscribers', 0):,}")
                    print(f"   🎬 Videos: {overview.get('total_videos', 0)}")
                    print(f"   👀 Total Views: {overview.get('total_views', 0):,}")
                
                # Performance Metrics
                if 'performance_metrics' in analytics:
                    perf = analytics['performance_metrics']
                    print(f"\n📊 PERFORMANCE ({days} days):")
                    print(f"   👀 Views: {perf.get('total_views_period', 0):,}")
                    print(f"   ❤️ Likes: {perf.get('total_likes_period', 0):,}")
                    print(f"   💬 Comments: {perf.get('total_comments_period', 0):,}")
                    print(f"   ⏱️ Watch Time: {perf.get('total_watch_time_hours', 0):.1f} hours")
                    print(f"   📈 Avg Engagement: {perf.get('avg_engagement_rate', 0):.1f}%")
                    print(f"   🎥 Videos Analyzed: {perf.get('videos_analyzed', 0)}")
                    
                    if perf.get('top_performing_video'):
                        top = perf['top_performing_video']
                        print(f"\n🥇 TOP VIDEO:")
                        print(f"      📝 {top.get('title', 'N/A')[:50]}...")
                        print(f"      🏆 ROI Score: {top.get('roi_score', 0):.1f}")
                        print(f"      📊 Engagement: {top.get('engagement_rate', 0):.1f}%")
                
                # Revenue Estimates
                if analytics.get('revenue_estimates'):
                    rev = analytics['revenue_estimates']
                    print(f"\n💰 REVENUE ESTIMATES:")
                    print(f"   💵 Monthly: ${rev.get('estimated_monthly_revenue', 0):.2f}")
                    print(f"   📅 Annual: ${rev.get('estimated_annual_revenue', 0):.2f}")
                    print(f"   👤 Per Subscriber: ${rev.get('revenue_per_subscriber', 0):.4f}")
                    print(f"   📊 RPM: ${rev.get('estimated_rpm', 0)}")
                
                # Content Insights
                if 'content_insights' in analytics:
                    content = analytics['content_insights']
                    length = content.get('optimal_video_length', 0)
                    print(f"\n🎯 CONTENT INSIGHTS:")
                    print(f"   ⏱️ Optimal Length: {int(length//60)}:{int(length%60):02d}")
                    
                    tags = content.get('best_performing_tags', [])[:5]
                    if tags:
                        tag_str = ', '.join([f"{t['tag']}({t['count']})" for t in tags])
                        print(f"   🏷️ Top Tags: {tag_str}")
                
                # Recommendations
                if analytics.get('roi_recommendations'):
                    print(f"\n💡 RECOMMENDATIONS:")
                    for i, rec in enumerate(analytics['roi_recommendations'][:3], 1):
                        print(f"   {i}. [{rec.get('priority')} Priority] {rec.get('category')}")
                        print(f"      💡 {rec.get('recommendation', 'No recommendation')}")
                        print(f"      🎯 Impact: {rec.get('expected_impact', 'Unknown')}")
                
                return data
            else:
                print(f"❌ ROI Dashboard failed: {response.status_code}")
                print(f"Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ ROI dashboard error: {e}")
            return None
    
    def run_debug(self, hours=24, days=7):
        """Run full debug sequence"""
        print("🚀 YOUTUBE ROI DEBUG SUITE")
        print("=" * 50)
        
        # Test server
        if not self.test_server():
            return False
        
        if not self.access_token:
            print("\n❌ No access token provided")
            print("Usage: python youtube_debug_simple.py YOUR_ACCESS_TOKEN")
            return False
        
        # Test basic channel info
        channel = self.test_basic_channel()
        if not channel:
            print("❌ Cannot proceed without channel access")
            return False
        
        # Test recent activity
        recent = self.test_recent_activity(hours)
        
        # Test ROI dashboard
        roi = self.test_roi_dashboard(days)
        
        print(f"\n✅ DEBUG COMPLETE!")
        print("=" * 50)
        return True


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python youtube_debug_simple.py YOUR_ACCESS_TOKEN [hours_back] [days_back]")
        print("Example: python youtube_debug_simple.py ya29.a0ARrdaM... 24 7")
        return
    
    access_token = sys.argv[1]
    hours_back = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    days_back = int(sys.argv[3]) if len(sys.argv) > 3 else 7
    
    debugger = SimpleYouTubeDebugger()
    debugger.set_token(access_token)
    debugger.run_debug(hours_back, days_back)


if __name__ == "__main__":
    main()

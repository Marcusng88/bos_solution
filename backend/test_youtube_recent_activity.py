#!/usr/bin/env python3
"""
Test script for YouTube recent activity, comments retrieval, and ROI analytics
"""

import requests
import json
import time
from datetime import datetime

def test_recent_activity():
    """Test the enhanced YouTube recent activity endpoint with ROI metrics"""
    print("Testing YouTube recent activity endpoint with ROI metrics...")
    
    # You'll need to replace this with a real access token from your YouTube OAuth flow
    access_token = "YOUR_YOUTUBE_ACCESS_TOKEN_HERE"
    
    url = "http://localhost:8000/api/v1/youtube/recent-activity"
    params = {
        "access_token": access_token,
        "hours_back": 1  # Get activity from last 1 hour
    }
    
    try:
        print(f"Making GET request to: {url}")
        print(f"Params: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Found {data.get('total_activities', 0)} recent activities")
            print(f"Cutoff time: {data.get('cutoff_time')}")
            
            # Display channel analytics
            if 'channel_analytics' in data:
                channel = data['channel_analytics']
                print(f"\n--- Channel Overview ---")
                print(f"Total Subscribers: {channel.get('total_subscribers', 0):,}")
                print(f"Total Videos: {channel.get('total_videos', 0)}")
                print(f"Total Views: {channel.get('total_views', 0):,}")
            
            # Display ROI summary
            if 'roi_summary' in data:
                roi = data['roi_summary']
                print(f"\n--- ROI Summary ---")
                print(f"Total Recent Views: {roi.get('total_recent_views', 0):,}")
                print(f"Total Recent Likes: {roi.get('total_recent_likes', 0):,}")
                print(f"Total Recent Comments: {roi.get('total_recent_comments', 0):,}")
                print(f"Average Engagement Rate: {roi.get('avg_engagement_rate', 0)}%")
                print(f"Videos Analyzed: {roi.get('videos_analyzed', 0)}")
            
            for i, activity in enumerate(data.get('recent_activity', []), 1):
                print(f"\n--- Activity {i} ---")
                print(f"Type: {activity.get('type')}")
                print(f"Video: {activity.get('title')}")
                print(f"Video ID: {activity.get('video_id')}")
                print(f"URL: {activity.get('video_url')}")
                
                # Display enhanced ROI metrics
                if 'roi_metrics' in activity:
                    roi = activity['roi_metrics']
                    print(f"  ROI Metrics:")
                    print(f"    Engagement Rate: {roi.get('engagement_rate', 0)}%")
                    print(f"    Likes per View: {roi.get('likes_per_view', 0)}%")
                    print(f"    Comments per View: {roi.get('comments_per_view', 0)}%")
                    print(f"    Views per Hour: {roi.get('views_per_hour_since_publish', 0)}")
                    print(f"    Est. Watch Time: {roi.get('estimated_watch_time_hours', 0)} hours")
                
                # Display content details
                if 'content_details' in activity:
                    content = activity['content_details']
                    print(f"  Content Details:")
                    print(f"    Duration: {content.get('duration', 'N/A')}")
                    print(f"    Tags: {len(content.get('tags', []))} tags")
                    print(f"    Category ID: {content.get('category_id', 'N/A')}")
                
                # Display comment analytics
                if 'comment_analytics' in activity:
                    comments = activity['comment_analytics']
                    print(f"  Comment Analytics:")
                    print(f"    Comments in Timeframe: {comments.get('total_comments_in_timeframe', 0)}")
                    print(f"    Total Comment Likes: {comments.get('total_comment_likes', 0)}")
                    print(f"    Avg Comment Length: {comments.get('avg_comment_length', 0)} chars")
                    
                    engagement_types = comments.get('engagement_types', {})
                    print(f"    Questions: {engagement_types.get('questions', 0)}")
                    print(f"    Compliments: {engagement_types.get('compliments', 0)}")
                    print(f"    Requests: {engagement_types.get('requests', 0)}")
                
                if 'recent_comments' in activity:
                    print(f"Recent Comments: {len(activity['recent_comments'])}")
                    for comment in activity['recent_comments'][:3]:  # Show first 3 comments
                        print(f"  - {comment.get('author')}: {comment.get('text')[:100]}...")
                        print(f"    Type: {comment.get('comment_type', 'other')}, Likes: {comment.get('like_count', 0)}")
                        
                if 'statistics' in activity:
                    stats = activity['statistics']
                    print(f"Stats - Views: {stats.get('view_count', 0):,}, Likes: {stats.get('like_count', 0):,}, Comments: {stats.get('comment_count', 0):,}")
        else:
            print(f"Error Response: {response.text}")
        
        return response
        
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        print("Make sure the backend server is running on localhost:8000")
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        
    return None

def test_roi_analytics():
    """Test the new ROI analytics dashboard endpoint"""
    print("\nTesting YouTube ROI Analytics endpoint...")
    
    # You'll need to replace this with a real access token
    access_token = "YOUR_YOUTUBE_ACCESS_TOKEN_HERE"
    
    url = "http://localhost:8000/api/v1/youtube/analytics/roi-dashboard"
    params = {
        "access_token": access_token,
        "days_back": 7,  # Analyze last 7 days
        "include_estimated_revenue": True
    }
    
    try:
        print(f"Making GET request to: {url}")
        print(f"Params: {params}")
        
        response = requests.get(url, params=params, timeout=60)  # Longer timeout for analytics
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! ROI Analytics generated")
            print(f"Analysis Period: {data.get('analysis_period')}")
            
            roi_analytics = data.get('roi_analytics', {})
            
            # Channel Overview
            if 'channel_overview' in roi_analytics:
                overview = roi_analytics['channel_overview']
                print(f"\n--- Channel Overview ---")
                print(f"Channel: {overview.get('channel_title', 'N/A')}")
                print(f"Subscribers: {overview.get('total_subscribers', 0):,}")
                print(f"Total Videos: {overview.get('total_videos', 0)}")
                print(f"Total Views: {overview.get('total_views', 0):,}")
            
            # Performance Metrics
            if 'performance_metrics' in roi_analytics:
                perf = roi_analytics['performance_metrics']
                print(f"\n--- Performance Metrics (Period) ---")
                print(f"Views: {perf.get('total_views_period', 0):,}")
                print(f"Likes: {perf.get('total_likes_period', 0):,}")
                print(f"Comments: {perf.get('total_comments_period', 0):,}")
                print(f"Watch Time: {perf.get('total_watch_time_hours', 0):.1f} hours")
                print(f"Avg Engagement Rate: {perf.get('avg_engagement_rate', 0)}%")
                print(f"Videos Analyzed: {perf.get('videos_analyzed', 0)}")
                
                if perf.get('top_performing_video'):
                    top_video = perf['top_performing_video']
                    print(f"Top Video: {top_video.get('title', 'N/A')[:50]}...")
                    print(f"  ROI Score: {top_video.get('roi_score', 0):.1f}")
                    print(f"  Engagement: {top_video.get('engagement_rate', 0)}%")
            
            # Engagement Analytics
            if 'engagement_analytics' in roi_analytics:
                engagement = roi_analytics['engagement_analytics']
                print(f"\n--- Engagement Analytics ---")
                print(f"Likes-to-Views Ratio: {engagement.get('likes_to_views_ratio', 0):.4f}%")
                print(f"Comments-to-Views Ratio: {engagement.get('comments_to_views_ratio', 0):.4f}%")
            
            # Revenue Estimates
            if 'revenue_estimates' in roi_analytics and roi_analytics['revenue_estimates']:
                revenue = roi_analytics['revenue_estimates']
                print(f"\n--- Revenue Estimates ---")
                print(f"Estimated Monthly Revenue: ${revenue.get('estimated_monthly_revenue', 0):.2f}")
                print(f"Estimated Annual Revenue: ${revenue.get('estimated_annual_revenue', 0):.2f}")
                print(f"Revenue per Subscriber: ${revenue.get('revenue_per_subscriber', 0):.4f}")
                print(f"RPM (Revenue per 1K views): ${revenue.get('estimated_rpm', 0)}")
            
            # Content Insights
            if 'content_insights' in roi_analytics:
                content = roi_analytics['content_insights']
                print(f"\n--- Content Insights ---")
                optimal_length = content.get('optimal_video_length', 0)
                print(f"Optimal Video Length: {int(optimal_length//60)}:{int(optimal_length%60):02d}")
                
                tags = content.get('best_performing_tags', [])
                if tags:
                    print(f"Top Tags: {', '.join([f'{tag['tag']} ({tag['count']})' for tag in tags[:5]])}")
            
            # ROI Recommendations
            if 'roi_recommendations' in roi_analytics:
                recommendations = roi_analytics['roi_recommendations']
                print(f"\n--- ROI Recommendations ---")
                for i, rec in enumerate(recommendations, 1):
                    print(f"{i}. [{rec.get('priority', 'Medium')} Priority] {rec.get('category', 'General')}")
                    print(f"   {rec.get('recommendation', 'No recommendation')}")
                    print(f"   Expected Impact: {rec.get('expected_impact', 'Unknown')}")
            
            # Video Performances
            video_performances = data.get('video_performances', [])
            if video_performances:
                print(f"\n--- Top Video Performances ---")
                for i, video in enumerate(video_performances[:5], 1):
                    print(f"{i}. {video.get('title', 'Untitled')[:50]}...")
                    print(f"   Views: {video.get('views', 0):,}, Likes: {video.get('likes', 0):,}")
                    print(f"   Engagement: {video.get('engagement_rate', 0):.1f}%, ROI Score: {video.get('roi_score', 0):.1f}")
        else:
            print(f"Error Response: {response.text}")
        
        return response
        
    except Exception as e:
        print(f"Error: {e}")
        
    return None

def test_video_comments():
    """Test the video comments endpoint"""
    print("\nTesting YouTube video comments endpoint...")
    
    # You'll need to replace these with real values
    access_token = "YOUR_YOUTUBE_ACCESS_TOKEN_HERE"
    video_id = "YOUR_VIDEO_ID_HERE"  # e.g., "dQw4w9WgXcQ"
    
    url = "http://localhost:8000/api/v1/youtube/video-comments"
    params = {
        "access_token": access_token,
        "video_id": video_id,
        "max_results": 10,
        "hours_back": 1  # Only get comments from last 1 hour
    }
    
    try:
        print(f"Making GET request to: {url}")
        print(f"Params: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Found {data.get('total_comments', 0)} recent comments")
            
            for i, comment in enumerate(data.get('comments', []), 1):
                print(f"\n--- Comment {i} ---")
                print(f"Author: {comment.get('author')}")
                print(f"Text: {comment.get('text')}")
                print(f"Published: {comment.get('published_at')}")
                print(f"Likes: {comment.get('like_count')}")
                
                if comment.get('replies'):
                    print(f"Replies: {len(comment['replies'])}")
                    for reply in comment['replies'][:2]:  # Show first 2 replies
                        print(f"  Reply by {reply.get('author')}: {reply.get('text')[:50]}...")
        else:
            print(f"Error Response: {response.text}")
        
        return response
        
    except Exception as e:
        print(f"Error: {e}")
        
    return None

def get_auth_url():
    """Get the YouTube auth URL for testing"""
    print("Getting YouTube auth URL...")
    
    try:
        response = requests.get("http://localhost:8000/api/v1/youtube/auth/url")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Auth URL: {data.get('auth_url')}")
            print("\nTo test with real data:")
            print("1. Visit the auth URL above")
            print("2. Complete the OAuth flow")
            print("3. Extract the access token from the callback")
            print("4. Replace 'YOUR_YOUTUBE_ACCESS_TOKEN_HERE' in this script")
            print("5. Run the tests again")
        else:
            print(f"Error getting auth URL: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("YouTube Enhanced Analytics Test Script")
    print("=" * 60)
    
    # First, show how to get auth URL
    get_auth_url()
    
    print("\n" + "=" * 60)
    
    # Test the enhanced endpoints (will fail without valid token)
    test_recent_activity()
    test_video_comments()
    test_roi_analytics()
    
    print("\n" + "=" * 60)
    print("ENHANCED FEATURES SUMMARY:")
    print("✅ Recent Activity with ROI Metrics")
    print("   - Engagement rates, watch time estimates")
    print("   - Comment analytics and sentiment analysis")
    print("   - Content performance indicators")
    print("")
    print("✅ Comprehensive ROI Dashboard")
    print("   - Revenue projections and RPM calculations")
    print("   - Performance benchmarking")
    print("   - Content optimization recommendations")
    print("   - Engagement analytics and trends")
    print("")
    print("✅ Advanced Comment Analysis")
    print("   - Comment categorization (questions, compliments, requests)")
    print("   - Intent scoring for purchase/engagement signals")
    print("   - Author engagement tracking")
    print("")
    print("NOTE: To get real results with all enhanced metrics, you need to:")
    print("1. Complete YouTube OAuth authentication")
    print("2. Replace the placeholder access token with a real one")
    print("3. Replace the placeholder video ID with a real one")
    print("4. Ensure your YouTube channel has recent videos/comments")
    print("5. Have sufficient video data for meaningful ROI calculations")

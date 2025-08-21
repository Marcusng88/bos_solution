from fastapi import APIRouter, HTTPException, Depends, Query, File, UploadFile, Form
from fastapi.responses import RedirectResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import httpx
import os
from urllib.parse import urlencode, parse_qs, urlparse
import json
import logging
from datetime import datetime, timedelta

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings
from app.services.youtube_service import youtube_service
from app.core.auth_utils import get_user_id_from_header

router = APIRouter()
logger = logging.getLogger(__name__)

# Request models
class YouTubeCallbackRequest(BaseModel):
    code: str

class VideoUploadRequest(BaseModel):
    access_token: str
    title: str
    description: str
    tags: Optional[List[str]] = None
    privacy_status: str = "private"

class TokenRefreshRequest(BaseModel):
    refresh_token: str

# Google OAuth and YouTube API configuration - load from environment
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "326775019777-v43jhcbs891rtv00p5vevif0ss57gc0r.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "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")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyAYn7IgfCjD8kHE70Sc_or2HS1zKIl6so8")
REDIRECT_URI = "http://localhost:3000/auth/callback/youtube"

# OAuth scopes for YouTube
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

@router.get("/debug")
async def debug_config():
    """Debug configuration"""
    return {
        "google_client_id": GOOGLE_CLIENT_ID[:10] + "..." if GOOGLE_CLIENT_ID else "Not set",
        "google_client_secret": "Set" if GOOGLE_CLIENT_SECRET else "Not set",
        "google_api_key": "Set" if GOOGLE_API_KEY else "Not set",
        "settings_google_client_id": settings.GOOGLE_CLIENT_ID[:10] + "..." if settings.GOOGLE_CLIENT_ID else "Not set"
    }

@router.get("/auth/url")
async def get_youtube_auth_url():
    """Generate YouTube OAuth authorization URL"""
    logger.info(f"Google Client ID: {GOOGLE_CLIENT_ID}")
    logger.info(f"Google Client Secret: {'*' * len(GOOGLE_CLIENT_SECRET) if GOOGLE_CLIENT_SECRET else 'Not set'}")
    logger.info(f"Redirect URI: {REDIRECT_URI}")
    
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google Client ID not configured")
    
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(YOUTUBE_SCOPES),
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    logger.info(f"Generated OAuth URL: {auth_url}")
    return {"auth_url": auth_url}

@router.post("/auth/callback")
async def youtube_auth_callback(request: YouTubeCallbackRequest):
    """Handle YouTube OAuth callback and exchange code for tokens"""
    if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET]):
        raise HTTPException(status_code=500, detail="Google OAuth credentials not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": request.code,
                    "grant_type": "authorization_code",
                    "redirect_uri": REDIRECT_URI,
                }
            )
            
            if token_response.status_code != 200:
                logger.error(f"Token exchange failed: {token_response.text}")
                raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
            
            tokens = token_response.json()
            
            # Get user's YouTube channel info
            channel_info = await get_channel_info(tokens["access_token"])
            
            return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens.get("refresh_token"),
                "expires_in": tokens.get("expires_in", 3600),
                "channel_info": channel_info
            }
            
    except Exception as e:
        logger.error(f"YouTube auth callback error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

async def get_channel_info(access_token: str) -> Dict[str, Any]:
    """Get YouTube channel information"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part": "snippet,statistics",
                    "mine": "true"
                },
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    channel = data["items"][0]
                    return {
                        "id": channel["id"],
                        "title": channel["snippet"]["title"],
                        "description": channel["snippet"]["description"],
                        "thumbnail": channel["snippet"]["thumbnails"]["default"]["url"],
                        "subscriber_count": channel["statistics"].get("subscriberCount", "0"),
                        "video_count": channel["statistics"].get("videoCount", "0"),
                        "view_count": channel["statistics"].get("viewCount", "0")
                    }
            
            return {"error": "No channel found"}
            
    except Exception as e:
        logger.error(f"Error getting channel info: {str(e)}")
        return {"error": str(e)}

@router.post("/upload")
async def upload_video(request: VideoUploadRequest):
    """Upload video to YouTube"""
    if not request.access_token:
        raise HTTPException(status_code=401, detail="Access token required")
    
    try:
        # This is a simplified endpoint - in a real implementation,
        # you would handle file upload and use YouTube's resumable upload API
        video_metadata = {
            "snippet": {
                "title": request.title,
                "description": request.description,
                "tags": request.tags or [],
                "categoryId": "22"  # People & Blogs
            },
            "status": {
                "privacyStatus": request.privacy_status
            }
        }
        
        # For now, return the metadata that would be used for upload
        return {
            "status": "ready_for_upload",
            "metadata": video_metadata,
            "message": "Video metadata prepared. File upload would happen here."
        }
        
    except Exception as e:
        logger.error(f"Video upload preparation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload preparation failed: {str(e)}")

@router.post("/upload-file")
async def upload_video_file(
    video_file: UploadFile = File(...),
    access_token: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    privacy_status: str = Form(default="private"),
    tags: Optional[str] = Form(default=None),
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Upload video file to YouTube"""
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token required")
    
    try:
        # Validate file type
        if not video_file.content_type or not video_file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Only video files are allowed.")
        
        # Parse tags if provided
        video_tags = []
        if tags:
            try:
                video_tags = json.loads(tags)
            except:
                video_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Read file content
        file_content = await video_file.read()
        
        # Upload to YouTube using the service with user_id for database recording
        result = await youtube_service.upload_video_from_file(
            access_token=access_token,
            video_content=file_content,
            title=title,
            description=description,
            tags=video_tags,
            privacy_status=privacy_status,
            content_type=video_file.content_type,
            user_id=current_user_id
        )
        
        if result.get("success"):
            return {
                "status": "success",
                "video_id": result.get("video_id"),
                "title": result.get("title"),
                "video_url": result.get("video_url"),
                "upload_status": result.get("upload_status"),
                "privacy_status": result.get("privacy_status")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Upload failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video file upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/videos")
async def get_user_videos(access_token: str, max_results: int = 10):
    """Get user's YouTube videos"""
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token required")
    
    try:
        async with httpx.AsyncClient() as client:
            # Get channel ID first
            channel_response = await client.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part": "contentDetails",
                    "mine": "true"
                },
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if channel_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get channel info")
            
            channel_data = channel_response.json()
            if not channel_data.get("items"):
                return {"videos": [], "total": 0}
            
            uploads_playlist_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # Get videos from uploads playlist
            videos_response = await client.get(
                "https://www.googleapis.com/youtube/v3/playlistItems",
                params={
                    "part": "snippet",
                    "playlistId": uploads_playlist_id,
                    "maxResults": max_results
                },
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if videos_response.status_code == 200:
                videos_data = videos_response.json()
                videos = []
                
                for item in videos_data.get("items", []):
                    snippet = item["snippet"]
                    videos.append({
                        "id": snippet["resourceId"]["videoId"],
                        "title": snippet["title"],
                        "description": snippet["description"],
                        "thumbnail": snippet["thumbnails"]["default"]["url"],
                        "published_at": snippet["publishedAt"]
                    })
                
                return {
                    "videos": videos,
                    "total": len(videos)
                }
            else:
                raise HTTPException(status_code=400, detail="Failed to fetch videos")
                
    except Exception as e:
        logger.error(f"Error fetching videos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch videos: {str(e)}")

@router.get("/recent-activity")
async def get_recent_youtube_activity(
    access_token: str,
    hours_back: int = Query(default=1, description="Number of hours to look back for recent activity")
):
    """Get recent YouTube activity with comprehensive ROI metrics including videos and comments from the last N hours"""
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token required")
    
    try:
        # Calculate the time cutoff
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        cutoff_iso = cutoff_time.isoformat() + "Z"
        
        async with httpx.AsyncClient() as client:
            # Get channel ID and analytics first
            channel_response = await client.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part": "contentDetails,statistics,snippet,brandingSettings",
                    "mine": "true"
                },
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if channel_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get channel info")
            
            channel_data = channel_response.json()
            if not channel_data.get("items"):
                return {"error": "No channel found", "recent_activity": []}
            
            channel_info = channel_data["items"][0]
            uploads_playlist_id = channel_info["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # Extract channel analytics for ROI dashboard
            channel_stats = channel_info.get("statistics", {})
            channel_analytics = {
                "total_subscribers": int(channel_stats.get("subscriberCount", "0")),
                "total_videos": int(channel_stats.get("videoCount", "0")),
                "total_views": int(channel_stats.get("viewCount", "0")),
                "channel_created": channel_info["snippet"]["publishedAt"]
            }
            
            # Get recent videos (up to 50 to check for recent ones)
            videos_response = await client.get(
                "https://www.googleapis.com/youtube/v3/playlistItems",
                params={
                    "part": "snippet",
                    "playlistId": uploads_playlist_id,
                    "maxResults": 50  # Get more videos to find recent ones
                },
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            recent_activity = []
            total_roi_metrics = {
                "total_recent_views": 0,
                "total_recent_likes": 0,
                "total_recent_comments": 0,
                "total_recent_shares": 0,
                "total_engagement_rate": 0,
                "videos_analyzed": 0
            }
            
            if videos_response.status_code == 200:
                videos_data = videos_response.json()
                
                for item in videos_data.get("items", []):
                    snippet = item["snippet"]
                    published_at = datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))
                    
                    # Check if video was published in the time range
                    if published_at >= cutoff_time.replace(tzinfo=published_at.tzinfo):
                        video_id = snippet["resourceId"]["videoId"]
                        
                        # Get comprehensive video statistics and content details
                        video_details_response = await client.get(
                            "https://www.googleapis.com/youtube/v3/videos",
                            params={
                                "part": "statistics,snippet,contentDetails,status",
                                "id": video_id
                            },
                            headers={"Authorization": f"Bearer {access_token}"}
                        )
                        
                        video_stats = {}
                        roi_metrics = {}
                        content_details = {}
                        
                        if video_details_response.status_code == 200:
                            video_data = video_details_response.json()
                            if video_data.get("items"):
                                video_item = video_data["items"][0]
                                stats = video_item.get("statistics", {})
                                content = video_item.get("contentDetails", {})
                                video_snippet = video_item.get("snippet", {})
                                
                                # Basic statistics
                                view_count = int(stats.get("viewCount", "0"))
                                like_count = int(stats.get("likeCount", "0"))
                                comment_count = int(stats.get("commentCount", "0"))
                                
                                video_stats = {
                                    "view_count": view_count,
                                    "like_count": like_count,
                                    "dislike_count": int(stats.get("dislikeCount", "0")),  # Note: Often not available
                                    "comment_count": comment_count,
                                    "favorite_count": int(stats.get("favoriteCount", "0"))
                                }
                                
                                # ROI and engagement metrics
                                engagement_actions = like_count + comment_count
                                engagement_rate = (engagement_actions / view_count * 100) if view_count > 0 else 0
                                
                                roi_metrics = {
                                    "engagement_rate": round(engagement_rate, 2),
                                    "likes_per_view": round((like_count / view_count * 100), 4) if view_count > 0 else 0,
                                    "comments_per_view": round((comment_count / view_count * 100), 4) if view_count > 0 else 0,
                                    "views_per_hour_since_publish": round(view_count / max(1, (datetime.now() - published_at.replace(tzinfo=None)).total_seconds() / 3600), 2),
                                    "estimated_watch_time_hours": 0,  # We'll calculate this if duration is available
                                    "click_through_rate_estimate": 0,  # Would need Analytics API for real CTR
                                    "audience_retention_estimate": round(engagement_rate * 0.1, 2)  # Rough estimate based on engagement
                                }
                                
                                # Content details for ROI analysis
                                duration_str = content.get("duration", "PT0S")
                                # Parse ISO 8601 duration (PT4M13S -> 253 seconds)
                                import re
                                duration_match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
                                if duration_match:
                                    hours = int(duration_match.group(1) or 0)
                                    minutes = int(duration_match.group(2) or 0)
                                    seconds = int(duration_match.group(3) or 0)
                                    total_seconds = hours * 3600 + minutes * 60 + seconds
                                    
                                    # Estimate total watch time (views * duration * estimated retention rate)
                                    estimated_retention_rate = min(0.6, engagement_rate / 100)  # Max 60% retention
                                    estimated_watch_time_seconds = view_count * total_seconds * estimated_retention_rate
                                    roi_metrics["estimated_watch_time_hours"] = round(estimated_watch_time_seconds / 3600, 2)
                                    
                                content_details = {
                                    "duration": duration_str,
                                    "duration_seconds": total_seconds if 'total_seconds' in locals() else 0,
                                    "definition": content.get("definition", "hd"),
                                    "caption": content.get("caption", "false"),
                                    "licensed_content": content.get("licensedContent", False),
                                    "tags": video_snippet.get("tags", []),
                                    "category_id": video_snippet.get("categoryId", ""),
                                    "default_language": video_snippet.get("defaultLanguage", ""),
                                    "live_broadcast_content": video_snippet.get("liveBroadcastContent", "none")
                                }
                                
                                # Update totals for dashboard
                                total_roi_metrics["total_recent_views"] += view_count
                                total_roi_metrics["total_recent_likes"] += like_count
                                total_roi_metrics["total_recent_comments"] += comment_count
                                total_roi_metrics["total_engagement_rate"] += engagement_rate
                                total_roi_metrics["videos_analyzed"] += 1
                        
                        # Get recent comments on this video with engagement metrics
                        comments_response = await client.get(
                            "https://www.googleapis.com/youtube/v3/commentThreads",
                            params={
                                "part": "snippet,replies",
                                "videoId": video_id,
                                "maxResults": 20,
                                "order": "time"  # Get most recent comments
                            },
                            headers={"Authorization": f"Bearer {access_token}"}
                        )
                        
                        recent_comments = []
                        comment_analytics = {
                            "total_comments_in_timeframe": 0,
                            "total_comment_likes": 0,
                            "total_replies": 0,
                            "avg_comment_length": 0,
                            "engagement_types": {"questions": 0, "compliments": 0, "requests": 0, "other": 0}
                        }
                        
                        if comments_response.status_code == 200:
                            comments_data = comments_response.json()
                            comment_texts = []
                            
                            for comment_item in comments_data.get("items", []):
                                comment_snippet = comment_item["snippet"]["topLevelComment"]["snippet"]
                                comment_published = datetime.fromisoformat(comment_snippet["publishedAt"].replace("Z", "+00:00"))
                                
                                # Only include comments from the specified time range
                                if comment_published >= cutoff_time.replace(tzinfo=comment_published.tzinfo):
                                    comment_text = comment_snippet["textDisplay"]
                                    comment_likes = comment_snippet.get("likeCount", 0)
                                    
                                    # Analyze comment type for ROI insights
                                    comment_type = "other"
                                    text_lower = comment_text.lower()
                                    if any(word in text_lower for word in ["?", "how", "what", "when", "where", "why"]):
                                        comment_type = "questions"
                                    elif any(word in text_lower for word in ["great", "amazing", "love", "awesome", "fantastic"]):
                                        comment_type = "compliments"
                                    elif any(word in text_lower for word in ["please", "can you", "could you", "tutorial", "more"]):
                                        comment_type = "requests"
                                    
                                    comment_analytics["engagement_types"][comment_type] += 1
                                    comment_analytics["total_comments_in_timeframe"] += 1
                                    comment_analytics["total_comment_likes"] += comment_likes
                                    comment_texts.append(comment_text)
                                    
                                    # Count replies
                                    reply_count = 0
                                    if comment_item.get("replies"):
                                        for reply_item in comment_item["replies"]["comments"]:
                                            reply_snippet = reply_item["snippet"]
                                            reply_published = datetime.fromisoformat(reply_snippet["publishedAt"].replace("Z", "+00:00"))
                                            if reply_published >= cutoff_time.replace(tzinfo=reply_published.tzinfo):
                                                reply_count += 1
                                    
                                    recent_comments.append({
                                        "comment_id": comment_item["id"],
                                        "text": comment_text,
                                        "author": comment_snippet["authorDisplayName"],
                                        "author_channel_id": comment_snippet.get("authorChannelId", {}).get("value"),
                                        "published_at": comment_snippet["publishedAt"],
                                        "updated_at": comment_snippet.get("updatedAt", comment_snippet["publishedAt"]),
                                        "like_count": comment_likes,
                                        "reply_count": reply_count,
                                        "comment_type": comment_type,
                                        "parent_id": comment_snippet.get("parentId")
                                    })
                            
                            # Calculate average comment length
                            if comment_texts:
                                comment_analytics["avg_comment_length"] = round(sum(len(text) for text in comment_texts) / len(comment_texts), 1)
                            comment_analytics["total_replies"] = sum(c["reply_count"] for c in recent_comments)
                        
                        recent_activity.append({
                            "type": "video",
                            "video_id": video_id,
                            "title": snippet["title"],
                            "description": snippet["description"],
                            "thumbnail": snippet["thumbnails"]["default"]["url"],
                            "published_at": snippet["publishedAt"],
                            "video_url": f"https://www.youtube.com/watch?v={video_id}",
                            "statistics": video_stats,
                            "roi_metrics": roi_metrics,
                            "content_details": content_details,
                            "recent_comments": recent_comments,
                            "comment_analytics": comment_analytics
                        })
            
            # Get recent comments across all videos (not just newly published ones)
            search_response = await client.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "snippet",
                    "forMine": "true",
                    "type": "video",
                    "maxResults": 20,
                    "order": "date"
                },
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                for search_item in search_data.get("items", []):
                    video_id = search_item["id"]["videoId"]
                    
                    # Skip if we already processed this video
                    if any(activity["video_id"] == video_id for activity in recent_activity):
                        continue
                    
                    # Get recent comments on this video with analytics
                    comments_response = await client.get(
                        "https://www.googleapis.com/youtube/v3/commentThreads",
                        params={
                            "part": "snippet,replies",
                            "videoId": video_id,
                            "maxResults": 15,
                            "order": "time"
                        },
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
                    
                    if comments_response.status_code == 200:
                        comments_data = comments_response.json()
                        recent_comments_on_old_video = []
                        
                        for comment_item in comments_data.get("items", []):
                            comment_snippet = comment_item["snippet"]["topLevelComment"]["snippet"]
                            comment_published = datetime.fromisoformat(comment_snippet["publishedAt"].replace("Z", "+00:00"))
                            
                            # Only include comments from the specified time range
                            if comment_published >= cutoff_time.replace(tzinfo=comment_published.tzinfo):
                                comment_text = comment_snippet["textDisplay"]
                                
                                # Determine comment intent for ROI analysis
                                text_lower = comment_text.lower()
                                intent_score = 0
                                if any(word in text_lower for word in ["buy", "purchase", "link", "where to get"]):
                                    intent_score = 3  # High purchase intent
                                elif any(word in text_lower for word in ["tutorial", "how to", "learn more"]):
                                    intent_score = 2  # Educational intent
                                elif any(word in text_lower for word in ["subscribe", "follow", "notifications"]):
                                    intent_score = 1  # Engagement intent
                                
                                recent_comments_on_old_video.append({
                                    "comment_id": comment_item["id"],
                                    "text": comment_text,
                                    "author": comment_snippet["authorDisplayName"],
                                    "published_at": comment_snippet["publishedAt"],
                                    "like_count": comment_snippet.get("likeCount", 0),
                                    "intent_score": intent_score,
                                    "reply_count": len(comment_item.get("replies", {}).get("comments", []))
                                })
                        
                        # Only add this video if it has recent comments
                        if recent_comments_on_old_video:
                            recent_activity.append({
                                "type": "comments_on_existing_video",
                                "video_id": video_id,
                                "title": search_item["snippet"]["title"],
                                "thumbnail": search_item["snippet"]["thumbnails"]["default"]["url"],
                                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                                "recent_comments": recent_comments_on_old_video,
                                "comment_engagement_score": sum(c["intent_score"] + c["like_count"] for c in recent_comments_on_old_video)
                            })
            
            # Calculate final ROI metrics
            if total_roi_metrics["videos_analyzed"] > 0:
                total_roi_metrics["avg_engagement_rate"] = round(
                    total_roi_metrics["total_engagement_rate"] / total_roi_metrics["videos_analyzed"], 2
                )
            
            return {
                "success": True,
                "hours_back": hours_back,
                "cutoff_time": cutoff_iso,
                "total_activities": len(recent_activity),
                "channel_analytics": channel_analytics,
                "roi_summary": total_roi_metrics,
                "recent_activity": recent_activity
            }
                
    except Exception as e:
        logger.error(f"Error fetching recent YouTube activity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent activity: {str(e)}")

@router.get("/analytics/roi-dashboard")
async def get_youtube_roi_analytics(
    access_token: str,
    days_back: int = Query(default=7, description="Number of days to analyze for ROI metrics"),
    include_estimated_revenue: bool = Query(default=True, description="Include estimated revenue calculations")
):
    """Get comprehensive YouTube analytics for ROI dashboard with performance metrics, engagement data, and revenue estimates"""
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token required")
    
    try:
        # Calculate the time cutoff
        cutoff_time = datetime.now() - timedelta(days=days_back)
        cutoff_iso = cutoff_time.isoformat() + "Z"
        
        async with httpx.AsyncClient() as client:
            # Get comprehensive channel information
            channel_response = await client.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part": "snippet,statistics,contentDetails,brandingSettings",
                    "mine": "true"
                },
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if channel_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get channel info")
            
            channel_data = channel_response.json()
            if not channel_data.get("items"):
                return {"error": "No channel found"}
            
            channel_info = channel_data["items"][0]
            channel_stats = channel_info.get("statistics", {})
            uploads_playlist_id = channel_info["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # Get recent videos for analysis (up to 50 videos within the timeframe)
            videos_response = await client.get(
                "https://www.googleapis.com/youtube/v3/playlistItems",
                params={
                    "part": "snippet",
                    "playlistId": uploads_playlist_id,
                    "maxResults": 50
                },
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            roi_analytics = {
                "channel_overview": {
                    "channel_title": channel_info["snippet"]["title"],
                    "total_subscribers": int(channel_stats.get("subscriberCount", "0")),
                    "total_videos": int(channel_stats.get("videoCount", "0")),
                    "total_views": int(channel_stats.get("viewCount", "0")),
                    "channel_created": channel_info["snippet"]["publishedAt"],
                    "subscriber_growth_rate": 0  # Would need historical data for accurate calculation
                },
                "performance_metrics": {
                    "total_views_period": 0,
                    "total_likes_period": 0,
                    "total_comments_period": 0,
                    "total_shares_period": 0,
                    "total_watch_time_hours": 0,
                    "average_view_duration": 0,
                    "videos_analyzed": 0,
                    "avg_engagement_rate": 0,
                    "avg_ctr_estimate": 0,
                    "top_performing_video": None
                },
                "engagement_analytics": {
                    "likes_to_views_ratio": 0,
                    "comments_to_views_ratio": 0,
                    "subscriber_conversion_rate": 0,
                    "engagement_by_video_type": {},
                    "peak_engagement_times": [],
                    "audience_sentiment": {"positive": 0, "neutral": 0, "negative": 0}
                },
                "content_insights": {
                    "most_engaging_topics": [],
                    "optimal_video_length": 0,
                    "best_performing_tags": [],
                    "upload_frequency_impact": 0
                },
                "revenue_estimates": {
                    "estimated_rpm": 2.5,  # Revenue per mille (industry average)
                    "estimated_monthly_revenue": 0,
                    "estimated_annual_revenue": 0,
                    "revenue_per_subscriber": 0,
                    "monetization_efficiency": 0
                } if include_estimated_revenue else None,
                "roi_recommendations": []
            }
            
            video_performances = []
            total_engagement_score = 0
            all_tags = []
            video_durations = []
            
            if videos_response.status_code == 200:
                videos_data = videos_response.json()
                
                for item in videos_data.get("items", []):
                    snippet = item["snippet"]
                    published_at = datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))
                    
                    # Only analyze videos from the specified time period
                    if published_at >= cutoff_time.replace(tzinfo=published_at.tzinfo):
                        video_id = snippet["resourceId"]["videoId"]
                        
                        # Get detailed video statistics
                        video_details_response = await client.get(
                            "https://www.googleapis.com/youtube/v3/videos",
                            params={
                                "part": "statistics,snippet,contentDetails,status,topicDetails",
                                "id": video_id
                            },
                            headers={"Authorization": f"Bearer {access_token}"}
                        )
                        
                        if video_details_response.status_code == 200:
                            video_data = video_details_response.json()
                            if video_data.get("items"):
                                video_item = video_data["items"][0]
                                stats = video_item.get("statistics", {})
                                content = video_item.get("contentDetails", {})
                                video_snippet = video_item.get("snippet", {})
                                
                                # Extract metrics
                                view_count = int(stats.get("viewCount", "0"))
                                like_count = int(stats.get("likeCount", "0"))
                                comment_count = int(stats.get("commentCount", "0"))
                                
                                # Calculate engagement metrics
                                engagement_actions = like_count + comment_count
                                engagement_rate = (engagement_actions / view_count * 100) if view_count > 0 else 0
                                
                                # Parse video duration
                                duration_str = content.get("duration", "PT0S")
                                import re
                                duration_match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
                                duration_seconds = 0
                                if duration_match:
                                    hours = int(duration_match.group(1) or 0)
                                    minutes = int(duration_match.group(2) or 0)
                                    seconds = int(duration_match.group(3) or 0)
                                    duration_seconds = hours * 3600 + minutes * 60 + seconds
                                    video_durations.append(duration_seconds)
                                
                                # Estimate watch time
                                estimated_retention = min(0.6, engagement_rate / 100)
                                estimated_watch_time = view_count * duration_seconds * estimated_retention / 3600
                                
                                # Track tags for content insights
                                video_tags = video_snippet.get("tags", [])
                                all_tags.extend(video_tags)
                                
                                video_performance = {
                                    "video_id": video_id,
                                    "title": snippet["title"],
                                    "views": view_count,
                                    "likes": like_count,
                                    "comments": comment_count,
                                    "engagement_rate": engagement_rate,
                                    "watch_time_hours": estimated_watch_time,
                                    "duration_seconds": duration_seconds,
                                    "published_at": snippet["publishedAt"],
                                    "tags": video_tags,
                                    "roi_score": (engagement_rate * view_count) / 1000  # Simple ROI score
                                }
                                
                                video_performances.append(video_performance)
                                
                                # Update totals
                                roi_analytics["performance_metrics"]["total_views_period"] += view_count
                                roi_analytics["performance_metrics"]["total_likes_period"] += like_count
                                roi_analytics["performance_metrics"]["total_comments_period"] += comment_count
                                roi_analytics["performance_metrics"]["total_watch_time_hours"] += estimated_watch_time
                                roi_analytics["performance_metrics"]["videos_analyzed"] += 1
                                total_engagement_score += engagement_rate
            
            # Calculate derived metrics
            videos_count = roi_analytics["performance_metrics"]["videos_analyzed"]
            if videos_count > 0:
                total_views = roi_analytics["performance_metrics"]["total_views_period"]
                total_likes = roi_analytics["performance_metrics"]["total_likes_period"]
                total_comments = roi_analytics["performance_metrics"]["total_comments_period"]
                
                roi_analytics["performance_metrics"]["avg_engagement_rate"] = round(total_engagement_score / videos_count, 2)
                roi_analytics["engagement_analytics"]["likes_to_views_ratio"] = round((total_likes / total_views * 100), 4) if total_views > 0 else 0
                roi_analytics["engagement_analytics"]["comments_to_views_ratio"] = round((total_comments / total_views * 100), 4) if total_views > 0 else 0
                
                # Find top performing video
                if video_performances:
                    top_video = max(video_performances, key=lambda x: x["roi_score"])
                    roi_analytics["performance_metrics"]["top_performing_video"] = {
                        "title": top_video["title"],
                        "video_id": top_video["video_id"],
                        "roi_score": top_video["roi_score"],
                        "engagement_rate": top_video["engagement_rate"]
                    }
                
                # Content insights
                if video_durations:
                    roi_analytics["content_insights"]["optimal_video_length"] = round(sum(video_durations) / len(video_durations), 0)
                
                # Tag analysis
                from collections import Counter
                tag_counts = Counter(all_tags)
                roi_analytics["content_insights"]["best_performing_tags"] = [
                    {"tag": tag, "count": count} for tag, count in tag_counts.most_common(10)
                ]
                
                # Revenue estimates (if requested)
                if include_estimated_revenue and roi_analytics["revenue_estimates"]:
                    rpm = roi_analytics["revenue_estimates"]["estimated_rpm"]
                    monthly_revenue = (total_views / 1000) * rpm * (30 / days_back)
                    annual_revenue = monthly_revenue * 12
                    
                    roi_analytics["revenue_estimates"]["estimated_monthly_revenue"] = round(monthly_revenue, 2)
                    roi_analytics["revenue_estimates"]["estimated_annual_revenue"] = round(annual_revenue, 2)
                    
                    total_subscribers = roi_analytics["channel_overview"]["total_subscribers"]
                    if total_subscribers > 0:
                        roi_analytics["revenue_estimates"]["revenue_per_subscriber"] = round(annual_revenue / total_subscribers, 4)
                
                # Generate ROI recommendations
                recommendations = []
                avg_engagement = roi_analytics["performance_metrics"]["avg_engagement_rate"]
                
                if avg_engagement < 2:
                    recommendations.append({
                        "priority": "High",
                        "category": "Engagement",
                        "recommendation": "Focus on improving video thumbnails and titles to increase engagement",
                        "expected_impact": "20-50% engagement increase"
                    })
                
                if video_durations and sum(video_durations) / len(video_durations) < 300:
                    recommendations.append({
                        "priority": "Medium",
                        "category": "Content Length",
                        "recommendation": "Consider creating longer-form content (5-10 minutes) for better retention",
                        "expected_impact": "15-30% watch time increase"
                    })
                
                if videos_count < (days_back / 3):
                    recommendations.append({
                        "priority": "Medium",
                        "category": "Upload Frequency",
                        "recommendation": "Increase upload frequency to 2-3 videos per week for better channel growth",
                        "expected_impact": "25-40% view growth"
                    })
                
                roi_analytics["roi_recommendations"] = recommendations
            
            return {
                "success": True,
                "analysis_period": f"{days_back} days",
                "cutoff_time": cutoff_iso,
                "generated_at": datetime.now().isoformat(),
                "roi_analytics": roi_analytics,
                "video_performances": video_performances[:10]  # Top 10 videos
            }
                
    except Exception as e:
        logger.error(f"Error fetching YouTube ROI analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ROI analytics: {str(e)}")

@router.get("/video-comments")
async def get_video_comments(
    access_token: str,
    video_id: str,
    max_results: int = Query(default=20, description="Maximum number of comments to retrieve"),
    hours_back: Optional[int] = Query(default=None, description="Only get comments from the last N hours")
):
    """Get comments for a specific video, optionally filtered by time"""
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token required")
    
    try:
        async with httpx.AsyncClient() as client:
            comments_response = await client.get(
                "https://www.googleapis.com/youtube/v3/commentThreads",
                params={
                    "part": "snippet,replies",
                    "videoId": video_id,
                    "maxResults": max_results,
                    "order": "time"
                },
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if comments_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch comments")
            
            comments_data = comments_response.json()
            comments = []
            
            # Calculate time cutoff if specified
            cutoff_time = None
            if hours_back:
                cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            for comment_item in comments_data.get("items", []):
                comment_snippet = comment_item["snippet"]["topLevelComment"]["snippet"]
                comment_published = datetime.fromisoformat(comment_snippet["publishedAt"].replace("Z", "+00:00"))
                
                # Skip if outside time range
                if cutoff_time and comment_published < cutoff_time.replace(tzinfo=comment_published.tzinfo):
                    continue
                
                comment_data = {
                    "comment_id": comment_item["id"],
                    "text": comment_snippet["textDisplay"],
                    "author": comment_snippet["authorDisplayName"],
                    "author_channel_id": comment_snippet.get("authorChannelId", {}).get("value"),
                    "published_at": comment_snippet["publishedAt"],
                    "updated_at": comment_snippet.get("updatedAt", comment_snippet["publishedAt"]),
                    "like_count": comment_snippet.get("likeCount", 0),
                    "replies": []
                }
                
                # Get replies if they exist
                if comment_item.get("replies"):
                    for reply_item in comment_item["replies"]["comments"]:
                        reply_snippet = reply_item["snippet"]
                        reply_published = datetime.fromisoformat(reply_snippet["publishedAt"].replace("Z", "+00:00"))
                        
                        # Skip reply if outside time range
                        if cutoff_time and reply_published < cutoff_time.replace(tzinfo=reply_published.tzinfo):
                            continue
                            
                        comment_data["replies"].append({
                            "reply_id": reply_item["id"],
                            "text": reply_snippet["textDisplay"],
                            "author": reply_snippet["authorDisplayName"],
                            "published_at": reply_snippet["publishedAt"],
                            "like_count": reply_snippet.get("likeCount", 0)
                        })
                
                comments.append(comment_data)
            
            return {
                "success": True,
                "video_id": video_id,
                "total_comments": len(comments),
                "comments": comments
            }
                
    except Exception as e:
        logger.error(f"Error fetching video comments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch comments: {str(e)}")

@router.post("/refresh-token")
async def refresh_youtube_token(request: TokenRefreshRequest):
    """Refresh YouTube access token"""
    if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET]):
        raise HTTPException(status_code=500, detail="Google OAuth credentials not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "refresh_token": request.refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=400, detail="Failed to refresh token")
                
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")

@router.get("/debug/full-test")
async def debug_full_youtube_test(
    access_token: str = Query(..., description="YouTube access token"),
    hours_back: int = Query(24, description="Hours back for recent activity"),
    days_back: int = Query(7, description="Days back for ROI analytics"),
    include_revenue: bool = Query(True, description="Include revenue estimates")
):
    """
    Comprehensive debug endpoint for YouTube ROI system
    Tests all major functionality with detailed console output
    """
    debug_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "access_token_preview": f"{access_token[:20]}..." if len(access_token) > 20 else access_token,
        "parameters": {
            "hours_back": hours_back,
            "days_back": days_back,
            "include_revenue": include_revenue
        },
        "tests": {}
    }
    
    try:
        # Test 1: Basic Channel Info
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/youtube/v3/channels",
                    params={
                        "part": "snippet,statistics,brandingSettings",
                        "mine": "true"
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    channel_data = response.json()
                    if channel_data.get("items"):
                        channel = channel_data["items"][0]
                        debug_results["tests"]["channel_info"] = {
                            "status": "SUCCESS",
                            "data": {
                                "channel_id": channel["id"],
                                "title": channel["snippet"]["title"],
                                "subscribers": int(channel["statistics"].get("subscriberCount", "0")),
                                "total_videos": channel["statistics"].get("videoCount", "0"),
                                "total_views": int(channel["statistics"].get("viewCount", "0")),
                                "description": channel["snippet"]["description"][:100] + "..." if len(channel["snippet"]["description"]) > 100 else channel["snippet"]["description"]
                            }
                        }
                    else:
                        debug_results["tests"]["channel_info"] = {
                            "status": "ERROR",
                            "error": "No channel found"
                        }
                else:
                    debug_results["tests"]["channel_info"] = {
                        "status": "ERROR",
                        "error": f"API Error: {response.status_code}",
                        "response": response.text[:500]
                    }
        except Exception as e:
            debug_results["tests"]["channel_info"] = {
                "status": "EXCEPTION",
                "error": str(e)
            }
        
        # Test 2: Recent Activity Endpoint
        try:
            from fastapi import Request
            from unittest.mock import Mock
            
            # Create mock request
            mock_request = Mock()
            mock_request.url.scheme = "http"
            mock_request.url.hostname = "localhost"
            mock_request.url.port = 8000
            
            # Call the actual endpoint function
            recent_activity_result = await get_recent_youtube_activity(
                access_token=access_token,
                hours_back=hours_back
            )
            
            debug_results["tests"]["recent_activity"] = {
                "status": "SUCCESS",
                "summary": {
                    "total_activities": recent_activity_result.get("total_activities", 0),
                    "videos_analyzed": len(recent_activity_result.get("recent_activity", [])),
                    "roi_summary": recent_activity_result.get("roi_summary", {}),
                    "channel_analytics": recent_activity_result.get("channel_analytics", {})
                },
                "sample_activities": recent_activity_result.get("recent_activity", [])[:2]  # First 2 activities
            }
            
        except Exception as e:
            debug_results["tests"]["recent_activity"] = {
                "status": "EXCEPTION",
                "error": str(e)
            }
        
        # Test 3: ROI Dashboard Endpoint
        try:
            roi_dashboard_result = await get_youtube_roi_analytics(
                access_token=access_token,
                days_back=days_back,
                include_estimated_revenue=include_revenue
            )
            
            debug_results["tests"]["roi_dashboard"] = {
                "status": "SUCCESS",
                "summary": {
                    "channel_overview": roi_dashboard_result["roi_analytics"].get("channel_overview", {}),
                    "performance_metrics": {
                        k: v for k, v in roi_dashboard_result["roi_analytics"].get("performance_metrics", {}).items()
                        if k in ["total_views_period", "total_likes_period", "avg_engagement_rate", "videos_analyzed"]
                    },
                    "revenue_estimates": roi_dashboard_result["roi_analytics"].get("revenue_estimates", {}),
                    "recommendations_count": len(roi_dashboard_result["roi_analytics"].get("roi_recommendations", []))
                }
            }
            
        except Exception as e:
            debug_results["tests"]["roi_dashboard"] = {
                "status": "EXCEPTION",
                "error": str(e)
            }
        
        # Test 4: Direct API Call to YouTube Data API
        try:
            async with httpx.AsyncClient() as client:
                # Get recent uploads
                response = await client.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params={
                        "part": "snippet",
                        "forMine": "true",
                        "type": "video",
                        "order": "date",
                        "maxResults": 5,
                        "publishedAfter": (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    search_data = response.json()
                    debug_results["tests"]["direct_api_search"] = {
                        "status": "SUCCESS",
                        "videos_found": len(search_data.get("items", [])),
                        "sample_videos": [
                            {
                                "title": item["snippet"]["title"],
                                "video_id": item["id"]["videoId"],
                                "published_at": item["snippet"]["publishedAt"]
                            }
                            for item in search_data.get("items", [])[:3]
                        ]
                    }
                else:
                    debug_results["tests"]["direct_api_search"] = {
                        "status": "ERROR",
                        "error": f"API Error: {response.status_code}",
                        "response": response.text[:500]
                    }
                    
        except Exception as e:
            debug_results["tests"]["direct_api_search"] = {
                "status": "EXCEPTION",
                "error": str(e)
            }
        
        # Overall Status
        successful_tests = sum(1 for test in debug_results["tests"].values() if test["status"] == "SUCCESS")
        total_tests = len(debug_results["tests"])
        
        debug_results["overall_status"] = {
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "success_rate": f"{(successful_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
            "all_passed": successful_tests == total_tests
        }
        
        return debug_results
        
    except Exception as e:
        logger.error(f"Debug endpoint error: {str(e)}")
        debug_results["fatal_error"] = str(e)
        return debug_results

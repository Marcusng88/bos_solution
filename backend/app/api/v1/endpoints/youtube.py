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

# Google OAuth and YouTube API configuration - use the provided credentials directly
GOOGLE_CLIENT_ID = "326775019777-v43jhcbs891rtv00p5vevif0ss57gc0r.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_API_KEY = "AIzaSyAYn7IgfCjD8kHE70Sc_or2HS1zKIl6so8"
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
    tags: Optional[str] = Form(default=None)
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
        
        # Create video metadata
        video_metadata = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": video_tags,
                "categoryId": "22"  # People & Blogs category
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout for large uploads
            # Create multipart boundary
            boundary = "----formdata-fastapi-" + os.urandom(16).hex()
            
            # Build multipart body manually for YouTube API
            multipart_body = []
            
            # Add metadata part
            multipart_body.append(f'--{boundary}'.encode())
            multipart_body.append(b'Content-Type: application/json; charset=UTF-8')
            multipart_body.append(b'')
            multipart_body.append(json.dumps(video_metadata).encode())
            
            # Add media part
            multipart_body.append(f'--{boundary}'.encode())
            multipart_body.append(f'Content-Type: {video_file.content_type}'.encode())
            multipart_body.append(b'')
            multipart_body.append(file_content)
            multipart_body.append(f'--{boundary}--'.encode())
            
            body = b'\r\n'.join(multipart_body)
            
            upload_response = await client.post(
                "https://www.googleapis.com/upload/youtube/v3/videos",
                params={
                    "part": "snippet,status",
                    "uploadType": "multipart"
                },
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": f"multipart/related; boundary={boundary}"
                },
                content=body
            )
            
            if upload_response.status_code not in [200, 201]:
                error_detail = upload_response.text
                logger.error(f"YouTube video upload failed: {error_detail}")
                raise HTTPException(status_code=400, detail=f"Failed to upload video to YouTube: {error_detail}")
            
            upload_data = upload_response.json()
            
            return {
                "status": "success",
                "video_id": upload_data.get("id"),
                "title": upload_data.get("snippet", {}).get("title"),
                "video_url": f"https://www.youtube.com/watch?v={upload_data.get('id')}",
                "upload_status": upload_data.get("status", {}).get("uploadStatus"),
                "privacy_status": upload_data.get("status", {}).get("privacyStatus")
            }
        
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

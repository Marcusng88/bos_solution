"""
YouTube Service - Handles YouTube video uploads and API interactions
"""

import httpx
import json
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class YouTubeService:
    """Service for YouTube API operations"""
    
    def __init__(self):
        self.api_base_url = "https://www.googleapis.com/youtube/v3"
        self.upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"
    
    async def upload_video_from_file(
        self,
        access_token: str,
        video_content: bytes,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        privacy_status: str = "private",
        content_type: str = "video/mp4"
    ) -> Dict[str, Any]:
        """
        Upload a video to YouTube using the YouTube Data API v3
        
        Args:
            access_token: OAuth access token for YouTube API
            video_content: Video file content as bytes
            title: Video title
            description: Video description
            tags: List of tags for the video
            privacy_status: Privacy setting (private, unlisted, public)
            content_type: MIME type of the video file
            
        Returns:
            Dictionary with upload result including video_id, url, etc.
        """
        try:
            video_metadata = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags or [],
                    "categoryId": "22"  # People & Blogs category
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": False
                }
            }
            
            async with httpx.AsyncClient(timeout=600.0) as client:  # 10 minute timeout for large uploads
                # Create multipart boundary
                boundary = "----formdata-youtube-" + os.urandom(16).hex()
                
                # Build multipart body manually for YouTube API
                multipart_body = []
                
                # Add metadata part
                multipart_body.append(f'--{boundary}'.encode())
                multipart_body.append(b'Content-Type: application/json; charset=UTF-8')
                multipart_body.append(b'')
                multipart_body.append(json.dumps(video_metadata).encode())
                
                # Add media part
                multipart_body.append(f'--{boundary}'.encode())
                multipart_body.append(f'Content-Type: {content_type}'.encode())
                multipart_body.append(b'')
                multipart_body.append(video_content)
                multipart_body.append(f'--{boundary}--'.encode())
                
                body = b'\r\n'.join(multipart_body)
                
                upload_response = await client.post(
                    self.upload_url,
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
                    raise Exception(f"Failed to upload video to YouTube: {error_detail}")
                
                upload_data = upload_response.json()
                
                return {
                    "success": True,
                    "video_id": upload_data.get("id"),
                    "title": upload_data.get("snippet", {}).get("title"),
                    "video_url": f"https://www.youtube.com/watch?v={upload_data.get('id')}",
                    "upload_status": upload_data.get("status", {}).get("uploadStatus"),
                    "privacy_status": upload_data.get("status", {}).get("privacyStatus"),
                    "upload_data": upload_data
                }
                
        except Exception as e:
            logger.error(f"YouTube upload error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def upload_video_from_url(
        self,
        access_token: str,
        video_url: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        privacy_status: str = "private"
    ) -> Dict[str, Any]:
        """
        Download a video from URL and upload to YouTube
        
        Args:
            access_token: OAuth access token for YouTube API
            video_url: URL of the video to download and upload
            title: Video title
            description: Video description
            tags: List of tags for the video
            privacy_status: Privacy setting (private, unlisted, public)
            
        Returns:
            Dictionary with upload result
        """
        try:
            # Download video from URL
            async with httpx.AsyncClient(timeout=300.0) as client:
                download_response = await client.get(video_url)
                
                if download_response.status_code != 200:
                    raise Exception(f"Failed to download video from URL: {video_url}")
                
                video_content = download_response.content
                content_type = download_response.headers.get("content-type", "video/mp4")
                
                # Upload to YouTube
                return await self.upload_video_from_file(
                    access_token=access_token,
                    video_content=video_content,
                    title=title,
                    description=description,
                    tags=tags,
                    privacy_status=privacy_status,
                    content_type=content_type
                )
                
        except Exception as e:
            logger.error(f"YouTube upload from URL error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_channel_info(self, access_token: str) -> Dict[str, Any]:
        """Get YouTube channel information"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/channels",
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
                            "success": True,
                            "channel": {
                                "id": channel["id"],
                                "title": channel["snippet"]["title"],
                                "description": channel["snippet"]["description"],
                                "thumbnail": channel["snippet"]["thumbnails"]["default"]["url"],
                                "subscriber_count": channel["statistics"].get("subscriberCount", "0"),
                                "video_count": channel["statistics"].get("videoCount", "0"),
                                "view_count": channel["statistics"].get("viewCount", "0")
                            }
                        }
                
                return {"success": False, "error": "No channel found"}
                
        except Exception as e:
            logger.error(f"Error getting channel info: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_video_status(self, access_token: str, video_id: str) -> Dict[str, Any]:
        """Get the processing status of an uploaded video"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/videos",
                    params={
                        "part": "status,processingDetails",
                        "id": video_id
                    },
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("items"):
                        video = data["items"][0]
                        return {
                            "success": True,
                            "status": video.get("status", {}),
                            "processing": video.get("processingDetails", {})
                        }
                
                return {"success": False, "error": "Video not found"}
                
        except Exception as e:
            logger.error(f"Error getting video status: {str(e)}")
            return {"success": False, "error": str(e)}

# Global instance
youtube_service = YouTubeService()


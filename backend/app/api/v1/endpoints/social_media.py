from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from app.core.supabase_client import supabase_client
from app.schemas.social_media import (
    SocialMediaAccountCreate, SocialMediaAccountUpdate, SocialMediaAccountResponse,
    ContentUploadCreate, ContentUploadUpdate, ContentUploadResponse,
    ContentTemplateCreate, ContentTemplateUpdate, ContentTemplateResponse,
    UploadPreview, BulkUploadRequest, UploadAnalytics
)
from app.core.auth_utils import get_user_id_from_header
from app.core.social_media_config import social_media_config
import json
import os
import httpx
import time
from pydantic import BaseModel
from app.core.social_media_config import SocialMediaConfig
from app.services.youtube_service import youtube_service

router = APIRouter()

# ============================================================================
# SOCIAL MEDIA POSTING FUNCTIONS
# ============================================================================

async def post_to_social_media(upload_data: dict, account_data: dict) -> dict:
    """Post content to actual social media platforms"""
    platform = upload_data.get("platform")
    
    if platform == "facebook":
        return await post_to_facebook(upload_data, account_data)
    elif platform == "instagram":
        return await post_to_instagram(upload_data, account_data)
    elif platform == "twitter":
        return await post_to_twitter(upload_data, account_data)
    elif platform == "linkedin":
        return await post_to_linkedin(upload_data, account_data)
    elif platform == "youtube":
        return await post_to_youtube(upload_data, account_data)
    else:
        raise Exception(f"Platform {platform} not yet implemented")


async def _get_facebook_permissions(access_token: str) -> dict:
    """Fetch user/page permissions from Facebook Graph API and normalize."""
    granted: list = []
    declined: list = []
    page_perms: dict = {}

    async with httpx.AsyncClient() as client:
        try:
            # User-level permissions (granted/declined)
            perms_resp = await client.get(
                "https://graph.facebook.com/me/permissions",
                params={"access_token": access_token},
            )
            if perms_resp.status_code == 200:
                for item in perms_resp.json().get("data", []):
                    if item.get("status") == "granted":
                        granted.append(item.get("permission"))
                    elif item.get("status") == "declined":
                        declined.append(item.get("permission"))
        except Exception:
            pass

        try:
            # Page-level permissions for pages the user manages
            pages_resp = await client.get(
                "https://graph.facebook.com/me/accounts",
                params={"access_token": access_token, "fields": "name,perms,id"},
            )
            if pages_resp.status_code == 200:
                for page in pages_resp.json().get("data", []):
                    page_perms[page.get("id")] = page.get("perms", [])
        except Exception:
            pass

    return {"granted": sorted(list(set(granted))), "declined": sorted(list(set(declined))), "page_perms": page_perms}

async def post_to_facebook(upload_data: dict, account_data: dict) -> dict:
    """Post to Facebook using Graph API"""
    try:
        access_token = account_data.get("access_token")
        page_id = account_data.get("account_id")
        
        # Check if we have real credentials
        if access_token and page_id:
            # Real Facebook Graph API endpoint
            url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
            
            post_data = {
                "message": upload_data.get("content_text", ""),
                "access_token": access_token
            }
            
            # Add title if present
            if upload_data.get("title"):
                post_data["name"] = upload_data["title"]
            
            # Add media if present
            if upload_data.get("media_files"):
                # For now, just add media URLs as links
                # TODO: Implement actual media upload to Facebook
                media_links = [f"Media: {media.get('url', '')}" for media in upload_data["media_files"]]
                post_data["message"] += "\n\n" + "\n".join(media_links)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=post_data)
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "post_id": result.get("id"),
                        "post_url": f"https://facebook.com/{result.get('id')}"
                    }
                else:
                    raise Exception(f"Facebook API error: {response.text}")
        else:
            # Test mode - simulate successful posting
            print(f"🧪 TEST MODE: Would post to Facebook: {upload_data.get('content_text', '')[:50]}...")
            return {
                "post_id": f"test_fb_{int(time.time())}",
                "post_url": "https://facebook.com/test_post",
                "test_mode": True
            }
                
    except Exception as e:
        raise Exception(f"Failed to post to Facebook: {str(e)}")

async def post_to_instagram(upload_data: dict, account_data: dict) -> dict:
    """Post to Instagram using Graph API"""
    try:
        access_token = account_data.get("access_token")
        instagram_account_id = account_data.get("account_id")
        
        # Check if we have real credentials
        if access_token and instagram_account_id:
            # Instagram requires media, so we'll create a simple text post for now
            # TODO: Implement media upload to Instagram
            url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media"
            
            post_data = {
                "caption": upload_data.get("content_text", ""),
                "access_token": access_token
            }
            
            # For now, create a simple text post
            # Instagram requires media, so we'll use a placeholder
            post_data["media_type"] = "CAROUSEL_ALBUM"
            post_data["children"] = json.dumps(["https://via.placeholder.com/1080x1080/000000/FFFFFF?text=Post"])
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=post_data)
                
                if response.status_code == 200:
                    result = response.json()
                    # Publish the media
                    publish_url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media_publish"
                    publish_data = {
                        "creation_id": result.get("id"),
                        "access_token": access_token
                    }
                    
                    publish_response = await client.post(publish_url, data=publish_data)
                    if publish_response.status_code == 200:
                        publish_result = publish_response.json()
                        return {
                            "post_id": publish_result.get("id"),
                            "post_url": f"https://instagram.com/p/{publish_result.get('id')}"
                        }
                    else:
                        raise Exception(f"Failed to publish Instagram post: {publish_response.text}")
                else:
                    raise Exception(f"Instagram API error: {response.text}")
        else:
            # Test mode - simulate successful posting
            print(f"🧪 TEST MODE: Would post to Instagram: {upload_data.get('content_text', '')[:50]}...")
            return {
                "post_id": f"test_ig_{int(time.time())}",
                "post_url": "https://instagram.com/p/test_post",
                "test_mode": True
            }
                
    except Exception as e:
        raise Exception(f"Failed to post to Instagram: {str(e)}")

async def post_to_twitter(upload_data: dict, account_data: dict) -> dict:
    """Post to Twitter using Twitter API v2"""
    try:
        bearer_token = account_data.get("access_token")
        
        if not bearer_token:
            raise Exception("Missing Twitter bearer token")
        
        # Twitter API v2 endpoint
        url = "https://api.twitter.com/2/tweets"
        
        post_data = {
            "text": upload_data.get("content_text", "")
        }
        
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=post_data, headers=headers)
            
            if response.status_code == 201:
                result = response.json()
                return {
                    "post_id": result["data"]["id"],
                    "post_url": f"https://twitter.com/user/status/{result['data']['id']}"
                }
            else:
                raise Exception(f"Twitter API error: {response.text}")
                
    except Exception as e:
        raise Exception(f"Failed to post to Twitter: {str(e)}")

async def post_to_linkedin(upload_data: dict, account_data: dict) -> dict:
    """Post to LinkedIn using LinkedIn API"""
    try:
        access_token = account_data.get("access_token")
        
        if not access_token:
            raise Exception("Missing LinkedIn access token")
        
        # LinkedIn API endpoint
        url = "https://api.linkedin.com/v2/ugcPosts"
        
        post_data = {
            "author": f"urn:li:person:{account_data.get('account_id')}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": upload_data.get("content_text", "")
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=post_data, headers=headers)
            
            if response.status_code == 201:
                result = response.json()
                return {
                    "post_id": result.get("id"),
                    "post_url": f"https://linkedin.com/feed/update/{result.get('id')}"
                }
            else:
                raise Exception(f"LinkedIn API error: {response.text}")
                
    except Exception as e:
        raise Exception(f"Failed to post to LinkedIn: {str(e)}")

async def post_to_youtube(upload_data: dict, account_data: dict) -> dict:
    """Post video to YouTube using YouTube Data API"""
    try:
        access_token = account_data.get("access_token")
        
        if not access_token:
            raise Exception("Missing YouTube access token")
        
        # Extract video content and metadata
        content_text = upload_data.get("content_text", "")
        title = upload_data.get("title", content_text[:100] if content_text else "Untitled Video")
        description = content_text
        tags = upload_data.get("tags", [])
        privacy_status = upload_data.get("privacy_status", "private")
        
        # Handle media files (video upload)
        media_files = upload_data.get("media_files", [])
        if not media_files:
            raise Exception("YouTube posts require a video file")
        
        video_file = media_files[0]  # Take the first video file
        if not video_file.get("type", "").startswith("video"):
            raise Exception("YouTube posts require video content")
        
        # Check if we have a URL or file content
        video_url = video_file.get("url")
        if video_url:
            # Upload from URL
            result = await youtube_service.upload_video_from_url(
                access_token=access_token,
                video_url=video_url,
                title=title,
                description=description,
                tags=tags,
                privacy_status=privacy_status
            )
        else:
            # For direct file uploads, we would need the file content
            # This would be handled differently in a real implementation
            # where files are uploaded and stored temporarily
            raise Exception("Direct file upload not implemented yet. Please provide video URL.")
        
        if result.get("success"):
            return {
                "post_id": result.get("video_id"),
                "post_url": result.get("video_url"),
                "upload_status": result.get("upload_status", "uploaded"),
                "privacy_status": result.get("privacy_status"),
                "message": "Video uploaded successfully to YouTube!"
            }
        else:
            raise Exception(result.get("error", "Unknown upload error"))
        
    except Exception as e:
        raise Exception(f"Failed to post to YouTube: {str(e)}")

# ============================================================================
# SOCIAL MEDIA ACCOUNT MANAGEMENT
# ============================================================================

@router.post("/accounts", response_model=dict)
async def create_social_media_account(
    account_data: SocialMediaAccountCreate,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Create a new social media account connection"""
    try:
        # Validate platform configuration
        if not social_media_config.validate_config(account_data.platform):
            raise HTTPException(
                status_code=400, 
                detail=f"Platform {account_data.platform} is not configured. Please add required API keys to environment variables."
            )
        
        # Add user_id to account data
        account_data_dict = account_data.dict()
        account_data_dict["user_id"] = current_user_id
        
        result = await supabase_client.create_social_media_account(account_data_dict)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create social media account: {str(e)}")

@router.get("/accounts", response_model=List[SocialMediaAccountResponse])
async def get_social_media_accounts(
    platform: Optional[str] = None,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Get all social media accounts for the current user"""
    try:
        accounts = await supabase_client.get_user_social_accounts(current_user_id, platform)
        return accounts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get social media accounts: {str(e)}")

@router.put("/accounts/{account_id}", response_model=dict)
async def update_social_media_account(
    account_id: str,
    account_data: SocialMediaAccountUpdate,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Update a social media account"""
    try:
        # Verify ownership
        accounts = await supabase_client.get_user_social_accounts(current_user_id)
        account_ids = [acc["id"] for acc in accounts]
        if account_id not in account_ids:
            raise HTTPException(status_code=403, detail="Access denied to this account")
        
        result = await supabase_client.update_social_media_account(account_id, account_data.dict(exclude_unset=True))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update social media account: {str(e)}")

@router.delete("/accounts/{account_id}", response_model=dict)
async def delete_social_media_account(
    account_id: str,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Delete a social media account connection"""
    try:
        # Verify ownership
        accounts = await supabase_client.get_user_social_accounts(current_user_id)
        account_ids = [acc["id"] for acc in accounts]
        if account_id not in account_ids:
            raise HTTPException(status_code=403, detail="Access denied to this account")
        
        result = await supabase_client.delete_social_media_account(account_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete social media account: {str(e)}")

# ============================================================================
# CONTENT UPLOAD MANAGEMENT
# ============================================================================

@router.post("/uploads", response_model=dict)
async def create_content_upload(
    upload_data: ContentUploadCreate,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Create a new content upload"""
    try:
        # Add user_id to upload data
        upload_data_dict = upload_data.dict()
        upload_data_dict["user_id"] = current_user_id
        
        # Verify account ownership
        accounts = await supabase_client.get_user_social_accounts(current_user_id)
        account_ids = [acc["id"] for acc in accounts]
        if upload_data.account_id not in account_ids:
            raise HTTPException(status_code=403, detail="Access denied to this account")
        
        result = await supabase_client.create_content_upload(upload_data_dict)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create content upload: {str(e)}")

@router.get("/uploads", response_model=List[ContentUploadResponse])
async def get_content_uploads(
    status: Optional[str] = None,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Get all content uploads for the current user"""
    try:
        uploads = await supabase_client.get_user_content_uploads(current_user_id, status)
        return uploads
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content uploads: {str(e)}")

@router.put("/uploads/{upload_id}", response_model=dict)
async def update_content_upload(
    upload_id: str,
    upload_data: ContentUploadUpdate,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Update a content upload"""
    try:
        # Verify ownership
        uploads = await supabase_client.get_user_content_uploads(current_user_id)
        upload_ids = [up["id"] for up in uploads]
        if upload_id not in upload_ids:
            raise HTTPException(status_code=403, detail="Access denied to this upload")
        
        result = await supabase_client.update_content_upload(upload_id, upload_data.dict(exclude_unset=True))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update content upload: {str(e)}")

@router.delete("/uploads/{upload_id}", response_model=dict)
async def delete_content_upload(
    upload_id: str,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Delete a content upload"""
    try:
        # Verify ownership
        uploads = await supabase_client.get_user_content_uploads(current_user_id)
        upload_ids = [up["id"] for up in uploads]
        if upload_id not in upload_ids:
            raise HTTPException(status_code=403, detail="Access denied to this upload")
        
        result = await supabase_client.delete_content_upload(upload_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete content upload: {str(e)}")

@router.post("/uploads/{upload_id}/post", response_model=dict)
async def post_content_now(
    upload_id: str,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Post content immediately (for testing or immediate posting)"""
    try:
        # Verify ownership
        uploads = await supabase_client.get_user_content_uploads(current_user_id)
        upload_ids = [up["id"] for up in uploads]
        if upload_id not in upload_ids:
            raise HTTPException(status_code=403, detail="Access denied to this upload")
        
        # Get upload details
        upload = next((up for up in uploads if up["id"] == upload_id), None)
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Get account details for posting
        accounts = await supabase_client.get_user_social_accounts(current_user_id)
        account = next((acc for acc in accounts if acc["id"] == upload["account_id"]), None)
        
        if not account:
            raise HTTPException(status_code=400, detail="Account not found")
        
        # Post to actual social media platform
        try:
            post_result = await post_to_social_media(upload, account)
            update_data = {
                "status": "posted",
                "post_id": post_result.get("post_id"),
                "post_url": post_result.get("post_url"),
                "error_message": None
            }
        except Exception as e:
            update_data = {
                "status": "failed",
                "error_message": str(e)
            }
        
        result = await supabase_client.update_content_upload(upload_id, update_data)
        return {"success": True, "message": "Content posted successfully!", "data": result}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post content: {str(e)}")

# ============================================================================
# CONTENT TEMPLATE MANAGEMENT
# ============================================================================

@router.post("/templates", response_model=dict)
async def create_content_template(
    template_data: ContentTemplateCreate,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Create a new content template"""
    try:
        # Add user_id to template data
        template_data_dict = template_data.dict()
        template_data_dict["user_id"] = current_user_id
        
        result = await supabase_client.create_content_template(template_data_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create content template: {str(e)}")

@router.get("/templates", response_model=List[ContentTemplateResponse])
async def get_content_templates(
    platform: Optional[str] = None,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Get all content templates for the current user"""
    try:
        templates = await supabase_client.get_user_content_templates(current_user_id, platform)
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content templates: {str(e)}")

@router.put("/templates/{template_id}", response_model=dict)
async def update_content_template(
    template_id: str,
    template_data: ContentTemplateUpdate,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Update a content template"""
    try:
        # Verify ownership
        templates = await supabase_client.get_user_content_templates(current_user_id)
        template_ids = [tmpl["id"] for tmpl in templates]
        if template_id not in template_ids:
            raise HTTPException(status_code=403, detail="Access denied to this template")
        
        result = await supabase_client.update_content_template(template_id, template_data.dict(exclude_unset=True))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update content template: {str(e)}")

@router.delete("/templates/{template_id}", response_model=dict)
async def delete_content_template(
    template_id: str,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Delete a content template"""
    try:
        # Verify ownership
        templates = await supabase_client.get_user_content_templates(current_user_id)
        template_ids = [tmpl["id"] for tmpl in templates]
        if template_id not in template_ids:
            raise HTTPException(status_code=403, detail="Access denied to this template")
        
        result = await supabase_client.delete_content_template(template_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete content template: {str(e)}")

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.post("/preview", response_model=List[UploadPreview])
async def preview_content(
    content_text: str = Form(...),
    platform: str = Form(...),
    media_count: int = Form(0)
):
    """Preview how content will look on different platforms"""
    try:
        # TODO: Implement platform-specific preview logic
        # For now, return basic preview
        previews = []
        
        if platform == "instagram":
            previews.append(UploadPreview(
                platform="instagram",
                preview_text=content_text[:2200] + "..." if len(content_text) > 2200 else content_text,
                character_count=len(content_text),
                media_count=media_count,
                warnings=["Content exceeds Instagram's 2200 character limit"] if len(content_text) > 2200 else [],
                suggestions=["Add relevant hashtags", "Include a call-to-action"] if len(content_text) < 100 else []
            ))
        elif platform == "facebook":
            previews.append(UploadPreview(
                platform="facebook",
                preview_text=content_text[:63206] + "..." if len(content_text) > 63206 else content_text,
                character_count=len(content_text),
                media_count=media_count,
                warnings=[],
                suggestions=["Engage with your audience", "Ask questions to encourage comments"]
            ))
        elif platform == "twitter":
            previews.append(UploadPreview(
                platform="twitter",
                preview_text=content_text[:280] + "..." if len(content_text) > 280 else content_text,
                character_count=len(content_text),
                media_count=media_count,
                warnings=["Content exceeds Twitter's 280 character limit"] if len(content_text) > 280 else [],
                suggestions=["Use relevant hashtags", "Keep it concise and engaging"]
            ))
        
        return previews
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")

@router.post("/bulk-upload", response_model=dict)
async def bulk_upload_content(
    bulk_request: BulkUploadRequest,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Upload the same content to multiple platforms"""
    try:
        # TODO: Implement bulk upload logic
        # For now, just create individual uploads
        uploads_created = []
        
        for platform in bulk_request.platforms:
            # Get user's account for this platform
            accounts = await supabase_client.get_user_social_accounts(current_user_id, platform)
            if not accounts:
                continue
            
            account = accounts[0]  # Use first account for this platform
            
            upload_data = bulk_request.content.dict()
            upload_data["user_id"] = current_user_id
            upload_data["platform"] = platform
            upload_data["account_id"] = account["id"]
            
            result = await supabase_client.create_content_upload(upload_data)
            if result.get("success"):
                uploads_created.append({"platform": platform, "status": "created"})
            else:
                uploads_created.append({"platform": platform, "status": "failed"})
        
        return {
            "success": True,
            "message": f"Bulk upload initiated for {len(bulk_request.platforms)} platforms",
            "uploads": uploads_created
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate bulk upload: {str(e)}")

@router.post("/youtube/upload-from-file", response_model=dict)
async def upload_youtube_video_file(
    video_file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    tags: Optional[str] = Form(default=None),
    privacy_status: str = Form(default="private"),
    current_user_id: str = Depends(get_user_id_from_header)
):
    """Upload video file directly to YouTube (requires YouTube account connection)"""
    try:
        # Get user's YouTube account
        accounts = await supabase_client.get_user_social_accounts(current_user_id)
        youtube_account = next((acc for acc in accounts if acc["platform"] == "youtube"), None)
        
        if not youtube_account:
            raise HTTPException(status_code=400, detail="No YouTube account connected")
        
        access_token = youtube_account.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="YouTube account not properly authenticated")
        
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
        
        # Upload to YouTube using the service
        result = await youtube_service.upload_video_from_file(
            access_token=access_token,
            video_content=file_content,
            title=title,
            description=description,
            tags=video_tags,
            privacy_status=privacy_status,
            content_type=video_file.content_type
        )
        
        if result.get("success"):
            return {
                "success": True,
                "video_id": result.get("video_id"),
                "video_url": result.get("video_url"),
                "upload_status": result.get("upload_status"),
                "privacy_status": result.get("privacy_status"),
                "message": "Video uploaded successfully to YouTube!"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Upload failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/youtube/channel-info", response_model=dict)
async def get_youtube_channel_info(current_user_id: str = Depends(get_user_id_from_header)):
    """Get YouTube channel information for connected account"""
    try:
        # Get user's YouTube account
        accounts = await supabase_client.get_user_social_accounts(current_user_id)
        youtube_account = next((acc for acc in accounts if acc["platform"] == "youtube"), None)
        
        if not youtube_account:
            raise HTTPException(status_code=400, detail="No YouTube account connected")
        
        access_token = youtube_account.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="YouTube account not properly authenticated")
        
        result = await youtube_service.get_channel_info(access_token)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to get channel info"))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get channel info: {str(e)}")

@router.get("/platform-status", response_model=dict)
async def get_platform_status():
    """Get status of social media platform configurations"""
    try:
        platforms = ["facebook", "instagram", "twitter", "linkedin", "tiktok", "youtube"]
        status = {}
        
        for platform in platforms:
            status[platform] = {
                "configured": social_media_config.validate_config(platform),
                "ready": social_media_config.validate_config(platform)
            }
        
        return {
            "success": True,
            "platforms": status,
            "message": "Platform configuration status retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get platform status: {str(e)}")

@router.get("/account-info/{platform}")
async def get_account_info(
    platform: str,
    user_id: str = Depends(get_user_id_from_header)
):
    """Get real account information from Facebook/Instagram APIs"""
    try:
        if platform not in ['facebook', 'instagram']:
            raise HTTPException(status_code=400, detail="Platform must be facebook or instagram")
        
        # Get access token from backend env (never set globally; pass per request)
        if platform == 'facebook':
            access_token = SocialMediaConfig.get_facebook_config().get('default_access_token')
            if not access_token:
                raise HTTPException(status_code=400, detail="Facebook access token not configured")
            
            # Get Facebook account info
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://graph.facebook.com/me",
                    params={
                        "access_token": access_token,
                        "fields": "id,name,username,picture"
                    }
                )
                
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail="Failed to fetch Facebook account info")
                
                data = response.json()
                return {
                    "platform": "facebook",
                    "accountId": data.get("id"),
                    "accountName": data.get("name"),
                    "username": data.get("username") or data.get("name"),
                    "profilePicture": data.get("picture", {}).get("data", {}).get("url") if data.get("picture") else None,
                    "isConnected": True
                }
        
        elif platform == 'instagram':
            access_token = SocialMediaConfig.get_facebook_config().get('default_access_token')
            if not access_token:
                raise HTTPException(status_code=400, detail="Instagram access token not configured")
            
            # Get Instagram account info (using Facebook Graph API)
            async with httpx.AsyncClient() as client:
                # First get Instagram business account ID
                response = await client.get(
                    f"https://graph.facebook.com/me/accounts",
                    params={
                        "access_token": access_token,
                        "fields": "instagram_business_account{id,username,profile_picture_url,name}"
                    }
                )
                
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail="Failed to fetch Instagram account info")
                
                data = response.json()
                accounts = data.get("data", [])
                
                if not accounts:
                    raise HTTPException(status_code=400, detail="No Instagram business account found")
                
                # Get the first Instagram account
                instagram_account = accounts[0].get("instagram_business_account")
                if not instagram_account:
                    raise HTTPException(status_code=400, detail="No Instagram business account linked")
                
                return {
                    "platform": "instagram",
                    "accountId": instagram_account.get("id"),
                    "accountName": instagram_account.get("name") or instagram_account.get("username"),
                    "username": instagram_account.get("username"),
                    "profilePicture": instagram_account.get("profile_picture_url"),
                    "isConnected": True
                }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting {platform} account info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get {platform} account info")

@router.get("/connected-accounts")
async def get_connected_accounts(
    user_id: str = Depends(get_user_id_from_header)
):
    """Get all connected social media accounts with real info from DB, fallback to env."""
    try:
        sanitized_accounts = []

        # First, load any per-user saved connections
        try:
            saved_accounts = await supabase_client.get_user_social_accounts(user_id)
        except Exception as e:
            saved_accounts = []

        for acc in saved_accounts:
            sanitized_accounts.append({
                "platform": acc.get("platform"),
                "accountId": acc.get("account_id"),
                "accountName": acc.get("account_name"),
                "username": acc.get("username"),
                "profilePicture": acc.get("profile_picture_url"),
                "isConnected": bool(acc.get("is_active", True)),
            })

        # If nothing saved yet, try env-based fallback (read-only), then persist
        if not sanitized_accounts:
            for platform in ["facebook", "instagram", "youtube"]:
                try:
                    info = await get_account_info(platform, user_id)
                    sanitized_accounts.append(info)
                except Exception:
                    pass

            # Persist fallback info to DB so it remains connected next time
            if sanitized_accounts:
                for info in sanitized_accounts:
                    try:
                        # Avoid duplicate insert if concurrently created
                        existing = await supabase_client.get_user_social_accounts(user_id, info["platform"])
                        if existing:
                            continue
                    except Exception:
                        existing = []

                    # Ensure user row exists to satisfy FK
                    try:
                        await supabase_client.upsert_user({"clerk_id": user_id})
                    except Exception as e:
                        print(f"Upsert user failed before account insert: {e}")

                    payload = {
                        "user_id": user_id,
                        "platform": info["platform"],
                        "account_id": info.get("accountId"),
                        "account_name": info.get("accountName"),
                        "username": info.get("username"),
                        "profile_picture_url": info.get("profilePicture"),
                        "access_token": SocialMediaConfig.get_facebook_config().get("default_access_token"),
                        "refresh_token": None,
                        "token_expires_at": None,
                        "is_active": True,
                        "is_test_account": False,
                        "permissions": {},
                    }
                    try:
                        await supabase_client.create_social_media_account(payload)
                    except Exception:
                        # If insert fails due to unique constraint, ignore
                        pass

        return {"accounts": sanitized_accounts, "total": len(sanitized_accounts)}
    except Exception as e:
        print(f"Error getting connected accounts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get connected accounts")


class ConnectRequest(BaseModel):
    access_token: Optional[str] = None


@router.post("/connect/{platform}")
async def connect_platform(
    platform: str,
    payload: ConnectRequest,
    user_id: str = Depends(get_user_id_from_header)
):
    """Persist a social connection for the user by validating the token and storing account info.

    Tokens are stored server-side only and are never returned to the client.
    """
    try:
        print(f"Connecting platform: {platform}, User ID: {user_id}")
        print(f"Payload: {payload}")
        
        platform = platform.lower()
        if platform not in ["facebook", "instagram", "youtube"]:
            raise HTTPException(status_code=400, detail="Unsupported platform")

        # Choose token precedence: provided > env default
        env_token = SocialMediaConfig.get_facebook_config().get("default_access_token")
        access_token = payload.access_token or env_token
        print(f"Access token present: {bool(access_token)}")
        if not access_token:
            raise HTTPException(status_code=400, detail=f"No access token available for {platform}")

        # Ensure user exists to satisfy FK
        try:
            await supabase_client.upsert_user({"clerk_id": user_id})
        except Exception as e:
            print(f"Upsert user failed before connect: {e}")
            # Continue anyway - user might already exist

        async with httpx.AsyncClient() as client:
            if platform == "facebook":
                print("Making request to Facebook Graph API...")
                me = await client.get(
                    "https://graph.facebook.com/me",
                    params={
                        "access_token": access_token,
                        "fields": "id,name,picture"
                    },
                )
                print(f"Facebook API response status: {me.status_code}")
                print(f"Facebook API response: {me.text}")
                
                if me.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"Token validation failed: {me.text}")
                data = me.json()
                print(f"Facebook user data: {data}")

                account_payload = {
                    "user_id": user_id,
                    "platform": "facebook",
                    "account_id": data.get("id"),
                    "account_name": data.get("name"),
                    "username": data.get("name"),  # Use name instead of deprecated username field
                    "profile_picture_url": data.get("picture", {}).get("data", {}).get("url") if data.get("picture") else None,
                    "access_token": access_token,
                    "refresh_token": None,
                    "token_expires_at": None,
                    "is_active": True,
                    "is_test_account": False,
                    "permissions": await _get_facebook_permissions(access_token),
                }
                
                print(f"Saving account payload to database...")
                try:
                    result = await supabase_client.create_social_media_account(account_payload)
                    print(f"Save successful: {result}")
                except Exception as save_error:
                    print(f"Save error: {save_error}")
                    # Try to handle duplicate accounts by updating existing one
                    try:
                        existing_accounts = await supabase_client.get_user_social_accounts(user_id, "facebook")
                        if existing_accounts:
                            print("Account already exists, updating instead...")
                            result = await supabase_client.update_social_media_account(existing_accounts[0]["id"], account_payload)
                            print(f"Update successful: {result}")
                        else:
                            raise save_error
                    except Exception as fallback_error:
                        print(f"Fallback also failed: {fallback_error}")
                        raise HTTPException(status_code=500, detail=f"Failed to save Facebook account: {str(save_error)}")

            elif platform == "instagram":
                pages = await client.get(
                    "https://graph.facebook.com/me/accounts",
                    params={
                        "access_token": access_token,
                        "fields": "instagram_business_account{id,username,profile_picture_url,name}"
                    },
                )
                if pages.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"Token validation failed: {pages.text}")
                pdata = pages.json()
                accounts = pdata.get("data", [])
                if not accounts or not accounts[0].get("instagram_business_account"):
                    raise HTTPException(status_code=400, detail="No Instagram business account linked")
                ig = accounts[0]["instagram_business_account"]

                account_payload = {
                    "user_id": user_id,
                    "platform": "instagram",
                    "account_id": ig.get("id"),
                    "account_name": ig.get("name") or ig.get("username"),
                    "username": ig.get("username"),
                    "profile_picture_url": ig.get("profile_picture_url"),
                    "access_token": access_token,
                    "refresh_token": None,
                    "token_expires_at": None,
                    "is_active": True,
                    "is_test_account": False,
                    "permissions": await _get_facebook_permissions(access_token),
                }
                await supabase_client.create_social_media_account(account_payload)

            elif platform == "youtube":
                # For YouTube, we expect the access_token to be a YouTube OAuth token
                # Validate the token by fetching channel info
                youtube_api_response = await client.get(
                    "https://www.googleapis.com/youtube/v3/channels",
                    params={
                        "part": "snippet,statistics",
                        "mine": "true",
                        "access_token": access_token
                    }
                )
                
                if youtube_api_response.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"YouTube token validation failed: {youtube_api_response.text}")
                
                channel_data = youtube_api_response.json()
                items = channel_data.get("items", [])
                
                if not items:
                    raise HTTPException(status_code=400, detail="No YouTube channel found for this account")
                
                channel = items[0]
                snippet = channel.get("snippet", {})
                statistics = channel.get("statistics", {})
                
                account_payload = {
                    "user_id": user_id,
                    "platform": "youtube",
                    "account_id": channel.get("id"),
                    "account_name": snippet.get("title", "YouTube Channel"),
                    "username": snippet.get("customUrl", "").replace("@", "") if snippet.get("customUrl") else None,
                    "profile_picture_url": snippet.get("thumbnails", {}).get("default", {}).get("url"),
                    "access_token": access_token,
                    "refresh_token": None,  # Will be set if provided separately
                    "token_expires_at": None,  # Will be calculated if expires_in provided
                    "is_active": True,
                    "is_test_account": False,
                    "permissions": {
                        "upload": True,
                        "read": True,
                        "subscriber_count": statistics.get("subscriberCount", "0"),
                        "video_count": statistics.get("videoCount", "0"),
                        "view_count": statistics.get("viewCount", "0")
                    },
                }
                
                print(f"Saving YouTube account payload to database...")
                try:
                    result = await supabase_client.create_social_media_account(account_payload)
                    print(f"YouTube save successful: {result}")
                except Exception as save_error:
                    print(f"YouTube save error: {save_error}")
                    # Try to handle duplicate accounts by updating existing one
                    try:
                        existing_accounts = await supabase_client.get_user_social_accounts(user_id, "youtube")
                        if existing_accounts:
                            print("YouTube account already exists, updating instead...")
                            result = await supabase_client.update_social_media_account(existing_accounts[0]["id"], account_payload)
                            print(f"YouTube update successful: {result}")
                        else:
                            raise save_error
                    except Exception as fallback_error:
                        print(f"YouTube fallback also failed: {fallback_error}")
                        raise HTTPException(status_code=500, detail=f"Failed to save YouTube account: {str(save_error)}")

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error connecting {platform}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect {platform}")


class FacebookCallbackRequest(BaseModel):
    code: str
    redirect_uri: str


@router.post("/facebook/auth/callback")
async def facebook_auth_callback(
    payload: FacebookCallbackRequest,
    user_id: str = Depends(get_user_id_from_header)
):
    """Exchange Facebook OAuth code for an access token and persist the account.

    This moves token handling server-side and stores the connection in `social_media_accounts`.
    """
    try:
        fb_config = SocialMediaConfig.get_facebook_config()
        app_id = fb_config.get("app_id")
        app_secret = fb_config.get("app_secret")
        if not app_id or not app_secret:
            raise HTTPException(status_code=500, detail="Facebook app credentials not configured")

        # Exchange code for short-lived access token
        async with httpx.AsyncClient() as client:
            token_resp = await client.get(
                "https://graph.facebook.com/v18.0/oauth/access_token",
                params={
                    "client_id": app_id,
                    "client_secret": app_secret,
                    "redirect_uri": payload.redirect_uri,
                    "code": payload.code,
                },
            )
            if token_resp.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_resp.text}")
            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="No access token returned by Facebook")

        # Ensure user exists
        try:
            await supabase_client.upsert_user({"clerk_id": user_id})
        except Exception as e:
            print(f"Upsert user failed before FB save: {e}")

        # Fetch user profile and save connection
        async with httpx.AsyncClient() as client:
            me = await client.get(
                "https://graph.facebook.com/me",
                params={
                    "access_token": access_token,
                    "fields": "id,name,picture",
                },
            )
            if me.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Token validation failed: {me.text}")
            data = me.json()

        account_payload = {
            "user_id": user_id,
            "platform": "facebook",
            "account_id": data.get("id"),
            "account_name": data.get("name"),
            "username": data.get("name"),  # Use name instead of deprecated username field
            "profile_picture_url": data.get("picture", {}).get("data", {}).get("url") if data.get("picture") else None,
            "access_token": access_token,
            "refresh_token": None,
            "token_expires_at": None,
            "is_active": True,
            "is_test_account": False,
            "permissions": await _get_facebook_permissions(access_token),
        }

        try:
            await supabase_client.create_social_media_account(account_payload)
        except Exception:
            # If duplicate due to unique constraint, try update instead
            try:
                # Find existing account by user and platform
                existing = await supabase_client.get_user_social_accounts(user_id, "facebook")
                if existing:
                    await supabase_client.update_social_media_account(existing[0]["id"], account_payload)
            except Exception:
                pass

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Facebook auth callback error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")
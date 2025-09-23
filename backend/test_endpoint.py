"""
Simple test endpoint to isolate the publishing issue
"""
from fastapi import APIRouter, Form
from typing import Optional
import httpx
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

router = APIRouter()

@router.post("/test-publish")
async def test_publish(
    content_text: str = Form(...),
    platform: str = Form(default="facebook")
):
    """Simple test publish endpoint"""
    try:
        # Get credentials from environment
        access_token = os.getenv("META_PAGE_ACCESS_TOKEN")
        page_id = os.getenv("META_PAGE_ID") 
        api_version = os.getenv("META_APP_VERSION", "v23.0")
        
        if not access_token or not page_id:
            return {
                "success": False,
                "error": "Missing credentials",
                "access_token_present": bool(access_token),
                "page_id_present": bool(page_id)
            }
        
        # Test Facebook API directly
        url = f"https://graph.facebook.com/{api_version}/{page_id}/feed"
        data = {
            "message": content_text,
            "access_token": access_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            
            if response.status_code in (200, 201):
                result = response.json()
                return {
                    "success": True,
                    "message": "Posted successfully!",
                    "post_id": result.get("id"),
                    "facebook_response": result
                }
            else:
                return {
                    "success": False,
                    "error": f"Facebook API error: {response.status_code}",
                    "response": response.text
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
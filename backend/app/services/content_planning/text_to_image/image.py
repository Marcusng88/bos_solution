"""
Image Generation Service using Stability AI
Generates realistic product-focused images based on text content
"""

import requests
import base64
import logging
import re
import json
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class ImageGenerationService:
    """Service for generating images using Stability AI"""
    
    def __init__(self):
        self.api_key = settings.stability_ai_api_key
        self.engine_id = "stable-diffusion-xl-1024-v1-0"
        self.base_url = "https://api.stability.ai/v1/generation"
        
        if not self.api_key:
            logger.warning("⚠️ STABILITY_AI_API_KEY not found in environment variables")
    
    async def _extract_product_with_llm(self, text_content: str, industry: str = "") -> Dict[str, str]:
        """
        Use LLM to extract product information from text content
        """
        try:
            # Check if we have Google API key
            if not settings.gemini_api_key:
                logger.warning("⚠️ Google/Gemini API key not found, falling back to simple extraction")
                return self._extract_product_simple_fallback(text_content, industry)
            
            # Prepare the prompt for LLM
            prompt = f"""Extract the main product from this text for image generation:

Text: "{text_content}"

Respond with JSON format:
{{
    "main_product": "the primary product name",
    "product_type": "category like footwear, electronics, automotive, food",
    "photography_style": "recommended photography style"
}}

Example: For "Nike Air Force shoes" respond with {{"main_product": "Nike Air Force shoes", "product_type": "footwear", "photography_style": "product photography"}}"""

            # Make request to Google Gemini
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 200
                }
            }
            
            response = requests.post(
                f"{url}?key={settings.gemini_api_key}",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    
                    # Try to parse JSON from the response
                    try:
                        # Clean the response (remove markdown formatting if present)
                        clean_content = content.strip()
                        if clean_content.startswith("```json"):
                            clean_content = clean_content.replace("```json", "").replace("```", "").strip()
                        elif clean_content.startswith("```"):
                            clean_content = clean_content.replace("```", "").strip()
                            
                        product_info = json.loads(clean_content)
                        
                        logger.info(f"🤖 LLM extracted product: {product_info.get('main_product', 'unknown')}")
                        return product_info
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ Failed to parse LLM JSON response: {e}")
                        logger.warning(f"Raw response: {content}")
                        
            else:
                # Log the full error response for debugging
                try:
                    error_response = response.json()
                    logger.warning(f"⚠️ LLM API request failed: {response.status_code} - {error_response}")
                except:
                    logger.warning(f"⚠️ LLM API request failed: {response.status_code} - {response.text}")
            
            logger.warning(f"⚠️ LLM API request failed: {response.status_code}")
            
        except Exception as e:
            logger.warning(f"⚠️ LLM extraction failed: {str(e)}")
        
        # Fallback to simple extraction
        return self._extract_product_simple_fallback(text_content, industry)
    
    def _extract_product_simple_fallback(self, text_content: str, industry: str = "") -> Dict[str, str]:
        """
        Simple fallback product extraction when LLM is not available
        """
        # Clean text and split into words
        clean_text = re.sub(r'[^\w\s]', ' ', text_content)
        words = clean_text.split()
        
        # Look for capitalized words (potential brand/product names)
        capitalized_words = [word for word in words if word[0].isupper() and len(word) > 2]
        
        # Common product indicators
        product_words = []
        for word in words:
            if word.lower() in ['nike', 'adidas', 'apple', 'samsung', 'iphone', 'macbook', 'shoes', 'sneakers', 'phone', 'laptop']:
                product_words.append(word)
        
        if product_words:
            main_product = ' '.join(product_words[:3])
        elif capitalized_words:
            main_product = ' '.join(capitalized_words[:2])
        elif industry:
            main_product = f"{industry} product"
        else:
            main_product = "product"
            
        return {
            "main_product": main_product,
            "product_type": "general",
            "photography_style": "product photography",
            "key_features": "high quality, professional"
        }
    
    async def _create_realistic_prompt(self, text_content: str, platform: str, content_type: str, industry: str = "") -> str:
        """
        Create a realistic, product-focused image prompt based on text content using LLM
        """
        # Use LLM to extract product information
        product_info = await self._extract_product_with_llm(text_content, industry)
        
        main_product = product_info.get("main_product", "product")
        product_type = product_info.get("product_type", "general")
        photography_style = product_info.get("photography_style", "product photography")
        key_features = product_info.get("key_features", "high quality")
        
        # Platform-specific style adjustments
        platform_styles = {
            'instagram': 'square format, bright natural lighting, lifestyle photography',
            'facebook': 'high quality, engaging, community-focused',
            'twitter': 'clean, minimalist, eye-catching',
            'linkedin': 'professional, business-focused, corporate style'
        }
        
        # Industry-specific elements
        industry_styles = {
            'technology': 'modern, sleek, digital, high-tech',
            'fashion': 'stylish, trendy, aesthetic, fashion photography',
            'food': 'appetizing, fresh, restaurant-quality, food photography',
            'fitness': 'energetic, active, healthy lifestyle, fitness photography',
            'business': 'professional, corporate, office setting',
            'travel': 'beautiful destinations, adventure, wanderlust',
            'beauty': 'glamorous, elegant, beauty product photography'
        }
        
        # Build the prompt using LLM-extracted information
        base_prompt = f"{photography_style} of {main_product}"
        
        # Add specific styling based on product type
        if product_type == "footwear" or "shoe" in main_product.lower():
            base_prompt += ", studio lighting, clean white background"
        elif product_type == "electronics" or any(tech in main_product.lower() for tech in ["phone", "laptop", "tablet"]):
            base_prompt += ", sleek design, modern aesthetic"
        elif product_type == "food":
            base_prompt += ", appetizing presentation, natural lighting"
        elif product_type == "clothing" or "fashion" in product_type:
            base_prompt += ", fashion photography, model styling"
        
        logger.info(f"🔍 LLM extracted: '{main_product}' (Type: {product_type})")
        logger.info(f"📸 Base prompt: '{base_prompt}'")
        
        # Add platform style
        if platform.lower() in platform_styles:
            base_prompt += f", {platform_styles[platform.lower()]}"
        
        # Add industry style  
        if industry.lower() in industry_styles:
            base_prompt += f", {industry_styles[industry.lower()]}"
        
        # Add realism enhancers
        realism_elements = [
            "photorealistic",
            "high resolution",
            "natural lighting",
            "real world setting",
            "commercial photography",
            "professional quality",
            "detailed textures",
            "realistic materials"
        ]
        
        final_prompt = f"{base_prompt}, {', '.join(realism_elements[:4])}"
        
        # Ensure prompt isn't too long (Stability AI has limits)
        if len(final_prompt) > 200:
            final_prompt = final_prompt[:200].rsplit(',', 1)[0]
        
        return final_prompt

    async def generate_image(
        self, 
        text_content: str, 
        platform: str = "instagram", 
        content_type: str = "promotional",
        industry: str = "",
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an image based on text content
        
        Args:
            text_content: The generated text content to base the image on
            platform: Social media platform (for style adjustments)
            content_type: Type of content (promotional, educational, etc.)
            industry: Industry context for better image generation
            custom_prompt: Optional custom prompt override
            
        Returns:
            Dict containing success status, base64 image data, and metadata
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Stability AI API key not configured",
                "image_data": None
            }
        
        try:
            # Create the image prompt using LLM
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = await self._create_realistic_prompt(text_content, platform, content_type, industry)
            
            logger.info(f"🎨 Generating image with prompt: {prompt[:100]}...")
            
            # Prepare the API request
            url = f"{self.base_url}/{self.engine_id}/text-to-image"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1.0
                    }
                ],
                "cfg_scale": 7,  # How strictly to follow the prompt
                "height": 1024,
                "width": 1024,
                "samples": 1,  # Number of images to generate
                "steps": 30,  # Quality vs speed tradeoff
                "style_preset": "photographic"  # More realistic style
            }
            
            # Make the API request
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                if "artifacts" in result and len(result["artifacts"]) > 0:
                    image_base64 = result["artifacts"][0]["base64"]
                    
                    logger.info("✅ Image generated successfully")
                    
                    return {
                        "success": True,
                        "image_data": image_base64,
                        "prompt_used": prompt,
                        "metadata": {
                            "engine": self.engine_id,
                            "platform": platform,
                            "content_type": content_type,
                            "industry": industry,
                            "dimensions": "1024x1024"
                        }
                    }
                else:
                    logger.error("❌ No image artifacts in response")
                    return {
                        "success": False,
                        "error": "No image generated",
                        "image_data": None
                    }
            else:
                error_detail = response.json() if response.content else {"message": "Unknown error"}
                logger.error(f"❌ Stability AI API error: {response.status_code} - {error_detail}")
                
                return {
                    "success": False,
                    "error": f"API error: {response.status_code} - {error_detail.get('message', 'Unknown error')}",
                    "image_data": None
                }
                
        except requests.exceptions.Timeout:
            logger.error("❌ Image generation timeout")
            return {
                "success": False,
                "error": "Image generation timed out",
                "image_data": None
            }
        except Exception as e:
            logger.error(f"❌ Image generation error: {str(e)}")
            return {
                "success": False,
                "error": f"Image generation failed: {str(e)}",
                "image_data": None
            }

# Singleton instance
image_service = ImageGenerationService()
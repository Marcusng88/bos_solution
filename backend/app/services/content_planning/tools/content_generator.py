"""
Content Generator Tool - Generates optimized social media content using AI
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import os
from langchain_google_genai import ChatGoogleGenerativeAI

from ..config.settings import settings, PLATFORM_CONFIGS
from ..config.prompts import CONTENT_GENERATION_PROMPT


class ContentGenerationInput(BaseModel):
    """Input schema for content generation"""
    industry: str = Field(description="Target industry sector")
    platform: str = Field(description="Social media platform")
    content_type: str = Field(description="Type of content to generate")
    tone: str = Field(description="Tone of voice for the content")
    target_audience: str = Field(description="Target audience description")
    competitor_insights: str = Field(description="Insights from competitor analysis")
    custom_requirements: Optional[str] = Field(description="Any custom requirements", default=None)


class ContentGenerator:
    """
    Tool for generating optimized social media content
    based on competitor analysis and platform best practices.
    """
    
    def __init__(self):
        self.llm = None  # Initialize lazily
    
    def _get_llm(self):
        """Lazy initialization of LLM"""
        if self.llm is None:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    model=settings.model_name,
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens,
                    top_p=settings.top_p,
                    google_api_key=os.getenv("GOOGLE_API_KEY")
                )
            except Exception as e:
                print(f"Warning: Could not initialize Google AI LLM: {e}")
                self.llm = "mock"  # Use mock mode
        return self.llm
    
    def _run(
        self,
        industry: str,
        platform: str,
        content_type: str,
        tone: str,
        target_audience: str,
        competitor_insights: str,
        custom_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate content based on inputs"""
        
        try:
            # Get platform-specific configuration
            platform_config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["linkedin"])
            max_length = platform_config["max_length"]
            hashtag_count = platform_config["optimal_hashtags"]
            
            # Prepare the prompt
            prompt = CONTENT_GENERATION_PROMPT.format(
                industry=industry,
                competitor_insights=competitor_insights,
                platform=platform,
                content_type=content_type,
                tone=tone,
                target_audience=target_audience,
                max_length=max_length,
                hashtag_count=hashtag_count
            )
            
            # Add custom requirements if provided
            if custom_requirements:
                prompt += f"\n\nADDITIONAL REQUIREMENTS:\n{custom_requirements}"
            
            # Generate content using LLM
            llm = self._get_llm()
            if llm == "mock":
                # Use mock content generation
                content_text = self._generate_mock_content(industry, platform, content_type, tone)
            else:
                try:
                    response = llm.invoke(prompt)
                    content_text = response.content if hasattr(response, 'content') else str(response)
                except Exception as e:
                    # Fallback to mock content generation for demo
                    print(f"LLM generation failed, using mock: {e}")
                    content_text = self._generate_mock_content(industry, platform, content_type, tone)
            
            # Parse the response
            content_result = self._parse_llm_response(content_text)
            
            # Add metadata
            content_result.update({
                "platform": platform,
                "industry": industry,
                "content_type": content_type,
                "tone": tone,
                "target_audience": target_audience,
                "platform_config": platform_config,
                "generation_timestamp": "2025-08-21T00:00:00Z"
            })
            
            return content_result
            
        except Exception as e:
            return {
                "error": f"Content generation failed: {str(e)}",
                "success": False
            }
    
    def _generate_mock_content(self, industry: str, platform: str, content_type: str, tone: str) -> str:
        """Generate mock content for demo purposes"""
        
        mock_templates = {
            "technology": {
                "product_announcement": "🚀 Exciting news! We're revolutionizing {industry} with our latest innovation. Transform your workflow and boost productivity by 80%. Ready to lead the digital transformation? #Innovation #TechLeadership #DigitalTransformation #Productivity #AI #Future #Technology #Growth #Success #Business",
                "educational": "💡 Tech Tip Tuesday: Here's how to optimize your {platform} strategy for maximum impact. Our data shows 3x better engagement with these proven techniques. What's your experience? #TechTips #Strategy #Growth #Learning #BestPractices #Digital #Innovation #Optimization #Productivity #Success",
                "promotional": "🎯 Limited time offer! Experience the future of {industry} technology. Join thousands of satisfied customers who've already made the switch. Get started today! #SpecialOffer #Technology #Innovation #Growth #Business #Productivity #Future #Leadership #Success #Transformation"
            },
            "fashion_beauty": {
                "product_announcement": "✨ Introducing our newest collection! Sustainable fashion meets timeless style. Every piece crafted with care for you and the planet. Shop now! #SustainableFashion #NewCollection #EcoFriendly #Style #Fashion #Conscious #Beauty #Trendy #Sustainable #Love",
                "educational": "💄 Beauty tips that actually work! Here are 5 game-changing techniques for a flawless look that lasts all day. Save this post! #BeautyTips #Makeup #Skincare #Beauty #Tutorial #Tips #Glam #Natural #Confidence #Style",
                "promotional": "🌟 Flash sale! 30% off our best-selling beauty essentials. Transform your routine with premium, cruelty-free products. Limited time only! #FlashSale #Beauty #Skincare #Makeup #CrueltyFree #Premium #Sale #Glow #Confidence #Love"
            }
        }
        
        industry_templates = mock_templates.get(industry, mock_templates["technology"])
        template = industry_templates.get(content_type, industry_templates["promotional"])
        
        return template.format(industry=industry, platform=platform)
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured format"""
        
        lines = response.strip().split('\n')
        result = {
            "success": True,
            "post_content": "",
            "hashtags": [],
            "character_count": 0,
            "estimated_engagement": "Medium",
            "call_to_action": "",
            "visual_suggestion": ""
        }
        
        current_section = None
        content_lines = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("Post Content:"):
                current_section = "content"
                content_text = line.replace("Post Content:", "").strip()
                if content_text:
                    content_lines.append(content_text)
            elif line.startswith("Hashtags:"):
                current_section = "hashtags"
                hashtag_text = line.replace("Hashtags:", "").strip()
                if hashtag_text:
                    result["hashtags"] = [tag.strip() for tag in hashtag_text.split(',')]
            elif line.startswith("Character Count:"):
                char_count_text = line.replace("Character Count:", "").strip()
                try:
                    result["character_count"] = int(char_count_text.split()[0])
                except:
                    result["character_count"] = len(result["post_content"])
            elif line.startswith("Estimated Engagement:"):
                result["estimated_engagement"] = line.replace("Estimated Engagement:", "").strip()
            elif current_section == "content" and line:
                content_lines.append(line)
            elif line.startswith("#") and current_section != "hashtags":
                # Extract hashtags from content
                hashtags = [tag.strip() for tag in line.split() if tag.startswith("#")]
                result["hashtags"].extend(hashtags)
        
        # Join content lines
        result["post_content"] = " ".join(content_lines)
        
        # Calculate character count if not provided
        if result["character_count"] == 0:
            result["character_count"] = len(result["post_content"])
        
        # Extract call-to-action (usually the last sentence)
        sentences = result["post_content"].split('.')
        if sentences:
            potential_cta = sentences[-1].strip()
            if any(word in potential_cta.lower() for word in ['visit', 'book', 'shop', 'learn', 'start', 'get', 'join', 'try']):
                result["call_to_action"] = potential_cta
        
        return result
    
    async def _arun(self, *args, **kwargs) -> Dict[str, Any]:
        """Async version of the tool"""
        return self._run(*args, **kwargs)


def generate_content_variations(
    base_content: Dict[str, Any],
    variation_count: int = 3
) -> List[Dict[str, Any]]:
    """
    Generate multiple variations of content for A/B testing
    """
    
    variations = []
    generator = ContentGenerator()
    
    # Create variations with different tones
    tones = ["professional", "casual", "enthusiastic"]
    
    for i, tone in enumerate(tones[:variation_count]):
        variation = generator._run(
            industry=base_content.get("industry", "technology"),
            platform=base_content.get("platform", "linkedin"),
            content_type=base_content.get("content_type", "promotional"),
            tone=tone,
            target_audience=base_content.get("target_audience", "professionals"),
            competitor_insights=base_content.get("competitor_insights", "")
        )
        
        variation["variation_id"] = f"var_{i+1}"
        variation["variation_type"] = f"tone_{tone}"
        variations.append(variation)
    
    return variations


def optimize_content_for_platform(
    content: str,
    source_platform: str,
    target_platform: str
) -> Dict[str, Any]:
    """
    Optimize content from one platform for another platform
    """
    
    source_config = PLATFORM_CONFIGS.get(source_platform, {})
    target_config = PLATFORM_CONFIGS.get(target_platform, {})
    
    # Basic optimization rules
    optimized_content = content
    
    # Adjust length
    if target_config.get("max_length", 1000) < len(content):
        # Truncate content intelligently
        sentences = content.split('.')
        optimized_content = ""
        for sentence in sentences:
            if len(optimized_content + sentence) < target_config["max_length"] - 50:
                optimized_content += sentence + "."
            else:
                break
    
    # Adjust hashtag count
    hashtags = [word for word in content.split() if word.startswith("#")]
    target_hashtag_count = target_config.get("optimal_hashtags", 5)
    
    if len(hashtags) > target_hashtag_count:
        hashtags = hashtags[:target_hashtag_count]
    
    return {
        "optimized_content": optimized_content,
        "hashtags": hashtags,
        "platform": target_platform,
        "character_count": len(optimized_content),
        "optimization_notes": f"Optimized from {source_platform} to {target_platform}"
    }

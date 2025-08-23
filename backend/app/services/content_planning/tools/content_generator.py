"""
Content Generator Tool - Generates optimized social media content using AI
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import os
import logging
from datetime import datetime, timezone

from ..config.settings import settings, PLATFORM_CONFIGS
from ..config.prompts import CONTENT_GENERATION_PROMPT

logger = logging.getLogger(__name__)

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
        self.data_source = "mock"  # Track data source for competitor insights
        self.last_analysis_check = None
    
    def _get_llm(self):
        """Lazy initialization of LLM"""
        if self.llm is None:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                google_api_key = os.getenv("GOOGLE_API_KEY")
                if not google_api_key:
                    logger.warning("⚠️ No GOOGLE_API_KEY found, using mock mode")
                    self.llm = "mock"
                else:
                    self.llm = ChatGoogleGenerativeAI(
                        model=settings.model_name,
                        temperature=settings.temperature,
                        max_tokens=settings.max_tokens,
                        top_p=settings.top_p,
                        google_api_key=google_api_key
                    )
                    logger.info("✅ Google AI LLM initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize Google AI LLM: {e}")
                self.llm = "mock"  # Use mock mode
        return self.llm
    
    async def _run(
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
            # Validate required parameters
            if not industry or not platform or not content_type or not tone or not target_audience:
                missing_params = []
                if not industry: missing_params.append("industry")
                if not platform: missing_params.append("platform")
                if not content_type: missing_params.append("content_type")
                if not tone: missing_params.append("tone")
                if not target_audience: missing_params.append("target_audience")
                
                logger.error(f"❌ Missing required parameters: {missing_params}")
                return {
                    "success": False,
                    "error": f"Missing required parameters: {missing_params}"
                }
            
            # Track data source from competitor insights
            self._update_data_source_from_insights(competitor_insights)
            
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
            
            # Log the prompt for debugging (truncated for readability)
            logger.info(f"🔧 Generated prompt for {platform} content (truncated): {prompt[:200]}...")
            logger.info(f"🔧 Competitor insights length: {len(competitor_insights)} characters")
            
            # Add custom requirements if provided
            if custom_requirements:
                prompt += f"\n\nADDITIONAL REQUIREMENTS:\n{custom_requirements}"
                logger.info(f"🔧 Added custom requirements: {custom_requirements}")
            
            # Generate content using LLM
            llm = self._get_llm()
            if llm == "mock":
                # Use mock content generation
                content_text = self._generate_mock_content(industry, platform, content_type, tone)
                logger.info(f"🔧 Using mock content generation for {platform}")
            else:
                try:
                    # Try to generate content with retry logic
                    max_retries = 2
                    content_text = None
                    
                    for attempt in range(max_retries):
                        try:
                            response = llm.invoke(prompt)
                            content_text = response.content if hasattr(response, 'content') else str(response)
                            
                            # Validate that the response contains actual content, not just requests for more data
                            if any(phrase in content_text.lower() for phrase in [
                                "please provide", "looking forward to receiving", "once you provide", 
                                "competitor analysis data", "placeholder", "{}", "competitor analysis"
                            ]):
                                logger.warning(f"⚠️ Attempt {attempt + 1}: LLM returned request for more data, retrying...")
                                if attempt < max_retries - 1:
                                    # Add more specific instructions for retry
                                    retry_prompt = prompt + "\n\nCRITICAL: You must generate actual content now. Do not ask for more data. Generate the post content immediately."
                                    response = llm.invoke(retry_prompt)
                                    content_text = response.content if hasattr(response, 'content') else str(response)
                                else:
                                    logger.warning(f"⚠️ All attempts failed, using mock fallback")
                                    content_text = self._generate_mock_content(industry, platform, content_type, tone)
                                break
                            else:
                                logger.info(f"✅ LLM generated content successfully for {platform} on attempt {attempt + 1}")
                                break
                                
                        except Exception as e:
                            logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")
                            if attempt == max_retries - 1:
                                logger.warning(f"⚠️ All attempts failed, using mock fallback")
                                content_text = self._generate_mock_content(industry, platform, content_type, tone)
                    
                    if not content_text:
                        content_text = self._generate_mock_content(industry, platform, content_type, tone)
                        
                except Exception as e:
                    # Fallback to mock content generation for demo
                    logger.warning(f"⚠️ LLM generation failed, using mock: {e}")
                    content_text = self._generate_mock_content(industry, platform, content_type, tone)
            
            # Parse the response - now expecting JSON format
            content_result = self._parse_llm_response(content_text, platform)
            
            # Add metadata
            content_result.update({
                "industry": industry,
                "platform": platform,
                "content_type": content_type,
                "tone": tone,
                "target_audience": target_audience,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "data_source": self.data_source,
                "data_freshness": self.last_analysis_check.isoformat() if self.last_analysis_check else None
            })
            
            return content_result
            
        except Exception as e:
            logger.error(f"❌ Content generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Content generation failed: {str(e)}",
                "data_source": self.data_source
            }
    
    def _update_data_source_from_insights(self, competitor_insights: str):
        """Update data source tracking based on competitor insights"""
        try:
            # Check if insights contain data source information
            if "data_source" in competitor_insights:
                if "supabase" in competitor_insights.lower():
                    self.data_source = "supabase"
                    self.last_analysis_check = datetime.now(timezone.utc)
                elif "mock" in competitor_insights.lower():
                    self.data_source = "mock"
            else:
                # Default to mock if no source specified
                self.data_source = "mock"
        except Exception as e:
            logger.warning(f"⚠️ Could not parse data source from insights: {e}")
            self.data_source = "mock"
    
    def _parse_llm_response(self, content_text: str, platform: str) -> Dict[str, Any]:
        """Parse LLM response to extract structured content from JSON"""
        try:
            # First, try to parse as JSON (expected format)
            import json
            
            # Clean the response text - remove any markdown formatting or extra text
            cleaned_text = content_text.strip()
            
            # Try to find JSON content if it's wrapped in other text
            if cleaned_text.startswith('```json'):
                # Extract content between ```json and ```
                start = cleaned_text.find('```json') + 7
                end = cleaned_text.find('```', start)
                if end != -1:
                    cleaned_text = cleaned_text[start:end].strip()
            elif cleaned_text.startswith('```'):
                # Extract content between ``` and ```
                start = cleaned_text.find('```') + 3
                end = cleaned_text.find('```', start)
                if end != -1:
                    cleaned_text = cleaned_text[start:end].strip()
            
            # Try to parse as JSON
            try:
                parsed_content = json.loads(cleaned_text)
                
                # Validate required fields
                required_fields = ["post_content", "hashtags"]
                missing_fields = [field for field in required_fields if field not in parsed_content]
                
                if missing_fields:
                    logger.warning(f"⚠️ JSON response missing required fields: {missing_fields}")
                    raise ValueError(f"Missing required fields: {missing_fields}")
                
                # Ensure hashtags is a list
                hashtags = parsed_content.get("hashtags", [])
                if isinstance(hashtags, str):
                    # If hashtags is a string, split it
                    hashtags = [tag.strip() for tag in hashtags.split() if tag.strip().startswith("#")]
                elif not isinstance(hashtags, list):
                    hashtags = []
                
                # Build the result
                result = {
                    "success": True,
                    "post_content": parsed_content.get("post_content", ""),
                    "hashtags": hashtags,
                    "character_count": parsed_content.get("character_count", len(parsed_content.get("post_content", ""))),
                    "estimated_engagement": parsed_content.get("estimated_engagement", "Medium"),
                    "optimal_posting_time": parsed_content.get("optimal_posting_time", self._get_optimal_posting_time(platform)),
                    "content_quality_score": parsed_content.get("content_quality_score", 0.8),
                    "platform_optimization_notes": parsed_content.get("platform_optimization_notes", "")
                }
                
                logger.info(f"✅ Successfully parsed JSON response with {len(hashtags)} hashtags")
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Failed to parse JSON response: {e}")
                # Fall through to legacy parsing
                
        except Exception as e:
            logger.warning(f"⚠️ Error in JSON parsing: {e}")
        
        # Fallback: try legacy parsing for backward compatibility
        try:
            # Try to parse structured response (old format)
            if "Post Content:" in content_text and "Hashtags:" in content_text:
                # Extract post content
                content_start = content_text.find("Post Content:") + len("Post Content:")
                content_end = content_text.find("Hashtags:")
                post_content = content_text[content_start:content_end].strip()
                
                # Extract hashtags
                hashtags_start = content_text.find("Hashtags:") + len("Hashtags:")
                hashtags_end = content_text.find("Character Count:") if "Character Count:" in content_text else len(content_text)
                hashtags_text = content_text[hashtags_start:hashtags_end].strip()
                
                # Parse hashtags
                hashtags = []
                if hashtags_text:
                    # Extract hashtags from text
                    words = hashtags_text.split()
                    hashtags = [word for word in words if word.startswith("#")]
                
                # Extract character count
                char_count = len(post_content)
                
                # Extract engagement estimate
                engagement_estimate = "Medium"
                if "Estimated Engagement:" in content_text:
                    engagement_start = content_text.find("Estimated Engagement:") + len("Estimated Engagement:")
                    engagement_end = content_text.find("\n", engagement_start) if "\n" in content_text[engagement_start:] else len(content_text)
                    engagement_text = content_text[engagement_start:engagement_end].strip()
                    if engagement_text:
                        engagement_estimate = engagement_text
                
                return {
                    "success": True,
                    "post_content": post_content,
                    "hashtags": hashtags,
                    "character_count": char_count,
                    "estimated_engagement": engagement_estimate,
                    "optimal_posting_time": self._get_optimal_posting_time(platform),
                    "content_quality_score": self._calculate_content_quality_score(post_content, hashtags)
                }
            else:
                # Fallback: treat entire response as content
                hashtags = [word for word in content_text.split() if word.startswith("#")]
                return {
                    "success": True,
                    "post_content": content_text,
                    "hashtags": hashtags,
                    "character_count": len(content_text),
                    "estimated_engagement": "Medium",
                    "optimal_posting_time": self._get_optimal_posting_time(platform),
                    "content_quality_score": self._calculate_content_quality_score(content_text, hashtags)
                }
                
        except Exception as e:
            logger.error(f"❌ Error parsing LLM response: {e}")
            # Return fallback content
            return {
                "success": True,
                "post_content": content_text,
                "hashtags": [],
                "character_count": len(content_text),
                "estimated_engagement": "Medium",
                "optimal_posting_time": self._get_optimal_posting_time(platform),
                "content_quality_score": 0.7
            }
    
    def _generate_mock_content(self, industry: str, platform: str, content_type: str, tone: str) -> str:
        """Generate mock content when LLM is unavailable"""
        
        # Industry-specific content templates with better structure
        industry_templates = {
            "technology": {
                "educational": f"🚀 {tone.title()} Tech Tip: Discover how {industry} innovations are transforming the digital landscape. Stay ahead of the curve with cutting-edge insights! #TechInnovation #{industry.title()} #DigitalTransformation #Innovation #TechTrends",
                "promotional": f"💡 Exciting news from the {industry} world! Our latest breakthrough is setting new industry standards. Experience the future today! #TechNews #{industry.title()} #Innovation #Breakthrough #FutureTech",
                "entertaining": f"🔧 Behind the scenes at our {industry} lab! Watch our team push boundaries and create tomorrow's solutions. Innovation never sleeps! #TechLife #{industry.title()} #Innovation #TeamWork #TechDevelopment"
            },
            "Technology & Software": {
                "educational": f"💼 {tone.title()} Business Insight: Learn how {industry} companies are leveraging technology to gain competitive advantages. Key strategies that drive success! #BusinessTech #{industry.title()} #DigitalStrategy #Innovation #Growth",
                "promotional": f"🌟 Transform your business with {industry} solutions! Join industry leaders who are already seeing 3x productivity gains. Ready to scale? #BusinessGrowth #{industry.title()} #Productivity #Scale #Success",
                "entertaining": f"🎯 The future of {industry} is here! See how AI and automation are reshaping business processes. Are you ready for the revolution? #FutureOfWork #{industry.title()} #AI #Automation #Innovation"
            },
            "fashion_beauty": {
                "educational": f"✨ {tone.title()} Style Guide: Master the latest {industry} trends with our expert tips. Elevate your look with confidence! #StyleTips #{industry.title()} #FashionGuide #BeautyTips #Trendy",
                "promotional": f"🌟 New {industry} collection alert! Discover pieces that define your unique style. Limited edition - don't miss out! #NewCollection #{industry.title()} #Fashion #Style #LimitedEdition",
                "entertaining": f"📸 Sneak peek into our {industry} design studio! See creativity in action as we craft tomorrow's trends! #DesignProcess #{industry.title()} #Creative #FashionDesign #BehindTheScenes"
            },
            "food_beverage": {
                "educational": f"🍽️ {tone.title()} Cooking Tip: Master the art of {industry} cuisine with our expert techniques. Turn every meal into a masterpiece! #CookingTips #{industry.title()} #FoodGuide #Culinary #ChefTips",
                "promotional": f"🎉 New {industry} menu launch! Experience flavors that tell a story. Book your table for an unforgettable dining journey! #NewMenu #{industry.title()} #Foodie #Dining #CulinaryExperience",
                "entertaining": f"👨‍🍳 Kitchen confidential! Watch our {industry} chefs create magic behind the scenes. Passion meets perfection! #KitchenLife #{industry.title()} #ChefLife #Culinary #BehindTheScenes"
            }
        }
        
        # Get template for industry and content type
        industry_content = industry_templates.get(industry, industry_templates["Technology & Software"])
        template = industry_content.get(content_type, industry_content["educational"])
        
        # Customize based on platform
        if platform == "linkedin":
            template = template.replace("🚀", "💼").replace("✨", "💼").replace("🍽️", "💼")
            template = template.replace("🌟", "💼").replace("🎯", "💼")
            template = template.replace("🔧", "💼").replace("📸", "💼")
        elif platform == "instagram":
            template = template.replace("🚀", "📸").replace("💡", "📸").replace("🔧", "📸")
            template = template.replace("💼", "📸").replace("🌟", "📸").replace("🎯", "📸")
            template = template.replace("✨", "📸").replace("🍽️", "📸").replace("👨‍🍳", "📸")
        elif platform == "facebook":
            template = template.replace("🚀", "👥").replace("💡", "👥").replace("🔧", "👥")
            template = template.replace("💼", "👥").replace("🌟", "👥").replace("🎯", "👥")
            template = template.replace("✨", "👥").replace("🍽️", "👥").replace("📸", "👥")
            template = template.replace("👨‍🍳", "👥")
        elif platform == "twitter":
            template = template.replace("🚀", "🐦").replace("💡", "🐦").replace("🔧", "🐦")
            template = template.replace("💼", "🐦").replace("🌟", "🐦").replace("🎯", "🐦")
            template = template.replace("✨", "🐦").replace("🍽️", "🐦").replace("📸", "🐦")
            template = template.replace("👨‍🍳", "🐦").replace("👥", "🐦")
        
        # Return as JSON string to match expected format
        import json
        
        # Extract hashtags from the template
        hashtags = [word for word in template.split() if word.startswith("#")]
        
        mock_response = {
            "post_content": template,
            "hashtags": hashtags,
            "character_count": len(template),
            "estimated_engagement": "High",
            "content_quality_score": 0.85,
            "optimal_posting_time": self._get_optimal_posting_time(platform),
            "platform_optimization_notes": f"Content optimized for {platform} with {len(hashtags)} relevant hashtags"
        }
        
        return json.dumps(mock_response)
    
    def _get_optimal_posting_time(self, platform: str = None) -> str:
        """Get optimal posting time based on platform and current data"""
        if platform:
            platform_times = {
                "linkedin": "Tuesday-Thursday, 9-11 AM",
                "twitter": "Monday-Wednesday, 1-3 PM", 
                "instagram": "Wednesday-Friday, 6-8 PM",
                "facebook": "Tuesday-Thursday, 1-3 PM"
            }
            return platform_times.get(platform, "Tuesday-Thursday, 9-11 AM")
        
        # Default fallback
        return "Tuesday-Thursday, 9-11 AM"
    
    def _calculate_content_quality_score(self, content: str, hashtags: List[str]) -> float:
        """Calculate content quality score based on various factors"""
        try:
            score = 0.0
            
            # Content length score (optimal: 150-300 characters)
            content_length = len(content)
            if 150 <= content_length <= 300:
                score += 0.3
            elif 100 <= content_length <= 400:
                score += 0.2
            else:
                score += 0.1
            
            # Hashtag score (optimal: 3-7 hashtags)
            hashtag_count = len(hashtags)
            if 3 <= hashtag_count <= 7:
                score += 0.3
            elif 1 <= hashtag_count <= 10:
                score += 0.2
            else:
                score += 0.1
            
            # Engagement elements score
            engagement_words = ["tip", "guide", "how", "discover", "learn", "exclusive", "new", "launch", "behind", "sneak"]
            engagement_count = sum(1 for word in engagement_words if word.lower() in content.lower())
            score += min(engagement_count * 0.1, 0.2)
            
            # Emoji score
            emoji_count = sum(1 for char in content if char in "😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏😒😞😔😟😕🙁☹️😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😱😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😯😦😧😮😲🥱😴🤤😪😵🤐🥴🤢🤮🤧😷🤒🤕🤑🤠💩👻💀☠️👽👾🤖😈👿👹👺")
            score += min(emoji_count * 0.05, 0.2)
            
            return round(score, 2)
            
        except Exception as e:
            logger.warning(f"⚠️ Error calculating content quality score: {e}")
            return 0.7  # Default score
    
    async def _arun(self, *args, **kwargs) -> Dict[str, Any]:
        """Async version of the tool"""
        try:
            # Filter out clerk_id as it's not needed for content generation
            if 'clerk_id' in kwargs:
                del kwargs['clerk_id']
            
            # Ensure all required parameters are present
            required_params = ['industry', 'platform', 'content_type', 'tone', 'target_audience', 'competitor_insights']
            missing_params = [param for param in required_params if param not in kwargs]
            
            if missing_params:
                logger.error(f"❌ Missing required parameters: {missing_params}")
                return {
                    "success": False,
                    "error": f"Missing required parameters: {missing_params}"
                }
            
            # Call _run with the correct parameters
            return await self._run(
                industry=kwargs['industry'],
                platform=kwargs['platform'],
                content_type=kwargs['content_type'],
                tone=kwargs['tone'],
                target_audience=kwargs['target_audience'],
                competitor_insights=kwargs['competitor_insights'],
                custom_requirements=kwargs.get('custom_requirements')
            )
            
        except Exception as e:
            logger.error(f"❌ Error in _arun: {str(e)}")
            return {
                "success": False,
                "error": f"Content generation failed: {str(e)}"
            }


async def generate_content_variations(
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
        variation = await generator._run(
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

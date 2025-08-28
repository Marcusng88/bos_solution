"""
Prompt templates for AI content generation
"""

from typing import Dict, Any

class PromptTemplate:
    """Simple prompt template class"""
    def __init__(self, input_variables: list, template: str):
        self.input_variables = input_variables
        self.template = template
    
    def format(self, **kwargs) -> str:
        return self.template.format(**kwargs)

# Content Generation Prompt with Structured JSON Output
CONTENT_GENERATION_PROMPT = PromptTemplate(
    input_variables=[
        "industry", "competitor_insights", "platform", "content_type", 
        "tone", "target_audience", "max_length", "hashtag_count"
    ],
    template="""You are an expert social media content creator and marketing strategist. Your task is to generate engaging, original content based on competitor analysis and industry best practices.

CONTEXT:
- Industry: {industry}
- Target Platform: {platform}
- Content Type: {content_type}
- Tone: {tone}
- Target Audience: {target_audience}
- Max Length: {max_length} characters
- Hashtag Count: {hashtag_count}

COMPETITOR ANALYSIS INSIGHTS:
{competitor_insights}

TASK:
Generate a compelling social media post that:
1. Captures attention with a strong hook
2. Delivers value to the target audience
3. Aligns with the specified tone and content type
4. Includes relevant hashtags for discoverability
5. Stays within the character limit
6. Incorporates insights from competitor analysis

IMPORTANT: You MUST respond with ONLY a valid JSON object in the following format. Do not include any other text, explanations, or requests for more data.

{{
    "post_content": "Your generated post content here. Make it engaging, relevant, and optimized for the platform. Include the main message, value proposition, and call-to-action if appropriate.",
    "hashtags": ["#Hashtag1", "#Hashtag2", "#Hashtag3", "#Hashtag4", "#Hashtag5"],
    "character_count": 0,
    "estimated_engagement": "High|Medium|Low",
    "content_quality_score": 0.0,
    "optimal_posting_time": "Tuesday-Thursday, 9-11 AM",
    "platform_optimization_notes": "Brief notes on how this content is optimized for the specific platform"
}}

RULES:
- Generate actual content, not requests for more data
- Use the competitor insights to inform your content strategy
- Ensure the tone matches the specified requirement
- Include exactly {hashtag_count} relevant hashtags
- Keep content under {max_length} characters
- Make content engaging and actionable
- Focus on providing value to the target audience

Remember: Respond with ONLY the JSON object, no other text."""
)

# Competitor Analysis Prompt
COMPETITOR_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["industry", "competitor_data", "analysis_type", "time_period"],
    template="""You are a competitive intelligence analyst specializing in social media strategy.

ANALYSIS REQUEST:
- Industry: {industry}
- Analysis Type: {analysis_type}
- Time Period: {time_period}

COMPETITOR DATA:
{competitor_data}

TASK:
Analyze the competitor data and provide insights on:

1. CONTENT TRENDS:
   - Most successful content types
   - Common themes and topics
   - Posting frequency patterns
   - Engagement drivers

2. HASHTAG ANALYSIS:
   - Top performing hashtags
   - Emerging hashtag trends
   - Hashtag usage patterns
   - Niche vs broad hashtag mix

3. TIMING INSIGHTS:
   - Optimal posting times
   - Day-of-week patterns
   - Seasonal trends

4. TONE & VOICE:
   - Dominant communication styles
   - Brand personality traits
   - Audience engagement approaches

5. CONTENT GAPS:
   - Underserved topics
   - Missed opportunities
   - Whitespace analysis

6. STRATEGIC RECOMMENDATIONS:
   - Differentiation opportunities
   - Best practice adoption
   - Competitive advantages

Provide actionable insights with specific examples and data points."""
)

# Hashtag Research Prompt
HASHTAG_RESEARCH_PROMPT = PromptTemplate(
    input_variables=["industry", "content_type", "platform", "trending_data"],
    template="""You are a hashtag strategy expert specializing in social media optimization.

RESEARCH REQUEST:
- Industry: {industry}
- Content Type: {content_type}
- Platform: {platform}

TRENDING DATA:
{trending_data}

TASK:
Research and recommend optimal hashtags by analyzing:

1. HASHTAG CATEGORIES:
   - Broad industry hashtags (high reach)
   - Niche specific hashtags (high engagement)
   - Trending hashtags (current relevance)
   - Brand/campaign specific hashtags

2. PERFORMANCE METRICS:
   - Estimated reach potential
   - Competition level
   - Engagement probability
   - Trend momentum

3. STRATEGIC MIX:
   - 40% broad industry hashtags
   - 30% niche specific hashtags  
   - 20% trending hashtags
   - 10% branded hashtags

4. PLATFORM OPTIMIZATION:
   - Platform-specific hashtag best practices
   - Optimal hashtag count
   - Formatting requirements

OUTPUT:
Provide a ranked list of recommended hashtags with:
- Hashtag
- Category (broad/niche/trending/branded)
- Estimated reach
- Competition level
- Reasoning for inclusion"""
)

# Content Gap Analysis Prompt
CONTENT_GAP_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["user_content", "competitor_content", "industry"],
    template="""You are a content strategy analyst identifying competitive opportunities.

YOUR CONTENT ANALYSIS:
{user_content}

COMPETITOR CONTENT ANALYSIS:
{competitor_content}

INDUSTRY: {industry}

TASK:
Identify content gaps and opportunities where you can outperform competitors:

1. TOPIC GAPS:
   - Topics competitors are covering well
   - Topics competitors are missing
   - Emerging topics with low competition

2. FORMAT GAPS:
   - Content formats competitors use heavily
   - Underutilized content formats
   - Platform-specific format opportunities

3. AUDIENCE GAPS:
   - Audience segments competitors target
   - Underserved audience segments
   - Niche audience opportunities

4. TIMING GAPS:
   - When competitors post most
   - Underutilized posting times
   - Seasonal content opportunities

5. ENGAGEMENT GAPS:
   - High-engagement content types competitors miss
   - Low-competition high-value topics
   - Viral content opportunities

6. STRATEGIC RECOMMENDATIONS:
   - Immediate opportunities (quick wins)
   - Medium-term content strategies
   - Long-term competitive advantages

Prioritize recommendations by impact and feasibility."""
)

# Visual Content Description Prompt
VISUAL_CONTENT_PROMPT = PromptTemplate(
    input_variables=["content_text", "platform", "industry", "tone"],
    template="""You are a visual content strategist creating compelling image descriptions.

CONTENT TEXT:
{content_text}

PLATFORM: {platform}
INDUSTRY: {industry}
TONE: {tone}

TASK:
Create a detailed visual content description that:

1. COMPLEMENTS THE TEXT:
   - Enhances the message
   - Supports the call-to-action
   - Matches the tone

2. PLATFORM OPTIMIZATION:
   - Follows platform visual best practices
   - Considers optimal dimensions
   - Maximizes engagement potential

3. VISUAL ELEMENTS:
   - Color palette suggestions
   - Composition guidelines
   - Key visual elements
   - Text overlay recommendations

4. BRAND ALIGNMENT:
   - Professional imagery style
   - Consistent visual identity
   - Industry-appropriate aesthetics

OUTPUT FORMAT:
Primary Visual: [Main image description]
Color Palette: [Suggested colors]
Composition: [Layout and framing]
Text Overlay: [Any text to include]
Props/Elements: [Specific items to include]
Lighting/Mood: [Atmosphere description]
Style Notes: [Overall aesthetic direction]"""
)

"""
Utility functions for content planning system
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib


def clean_content_text(text: str) -> str:
    """Clean and sanitize content text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Fix common formatting issues
    text = text.replace(' .', '.')
    text = text.replace(' ,', ',')
    text = text.replace(' !', '!')
    text = text.replace(' ?', '?')
    
    return text


def extract_hashtags_from_text(text: str) -> List[str]:
    """Extract hashtags from text content"""
    hashtag_pattern = r'#[A-Za-z0-9_]+'
    hashtags = re.findall(hashtag_pattern, text)
    return list(set(hashtags))  # Remove duplicates


def validate_hashtag(hashtag: str) -> bool:
    """Validate hashtag format"""
    if not hashtag.startswith('#'):
        return False
    
    # Remove # and check if remaining text is valid
    tag_content = hashtag[1:]
    
    # Must contain only letters, numbers, and underscores
    if not re.match(r'^[A-Za-z0-9_]+$', tag_content):
        return False
    
    # Must be between 2 and 30 characters
    if len(tag_content) < 2 or len(tag_content) > 30:
        return False
    
    return True


def format_hashtags(hashtags: List[str]) -> List[str]:
    """Format and validate hashtags"""
    formatted = []
    
    for hashtag in hashtags:
        if not hashtag.startswith('#'):
            hashtag = f"#{hashtag}"
        
        # Clean the hashtag
        hashtag = re.sub(r'[^#A-Za-z0-9_]', '', hashtag)
        
        if validate_hashtag(hashtag):
            formatted.append(hashtag)
    
    return formatted


def calculate_content_score(content: Dict[str, Any]) -> float:
    """Calculate content quality score"""
    score = 0.0
    
    # Content length score (0-3 points)
    content_length = content.get("character_count", 0)
    if 100 <= content_length <= 300:
        score += 3.0
    elif 50 <= content_length < 100 or 300 < content_length <= 500:
        score += 2.0
    elif content_length > 0:
        score += 1.0
    
    # Hashtag score (0-2 points)
    hashtag_count = len(content.get("hashtags", []))
    if 5 <= hashtag_count <= 12:
        score += 2.0
    elif 1 <= hashtag_count < 5 or 12 < hashtag_count <= 20:
        score += 1.0
    
    # Call-to-action score (0-2 points)
    if content.get("call_to_action"):
        score += 2.0
    
    # Engagement prediction score (0-3 points)
    engagement = content.get("estimated_engagement", "Medium").lower()
    if engagement == "high":
        score += 3.0
    elif engagement == "medium":
        score += 2.0
    elif engagement == "low":
        score += 1.0
    
    return round(score, 1)


def generate_content_variations_by_length(
    base_content: str,
    target_lengths: List[int]
) -> List[str]:
    """Generate content variations for different platforms based on length"""
    variations = []
    
    for target_length in target_lengths:
        if len(base_content) <= target_length:
            variations.append(base_content)
        else:
            # Truncate intelligently
            sentences = base_content.split('.')
            truncated = ""
            
            for sentence in sentences:
                if len(truncated + sentence + ".") <= target_length - 10:  # Leave space for "..."
                    truncated += sentence + "."
                else:
                    break
            
            if truncated:
                variations.append(truncated.strip())
            else:
                # If even first sentence is too long, truncate it
                variations.append(base_content[:target_length-3] + "...")
    
    return variations


def extract_keywords_from_content(content: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from content for analysis"""
    # Remove hashtags and clean text
    clean_text = re.sub(r'#\w+', '', content)
    clean_text = re.sub(r'[^\w\s]', ' ', clean_text)
    
    # Split into words and filter
    words = clean_text.lower().split()
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'hers', 'its', 'our', 'their'
    }
    
    # Filter words
    keywords = [word for word in words if len(word) > 3 and word not in stop_words]
    
    # Count frequency and return most common
    from collections import Counter
    word_counts = Counter(keywords)
    
    return [word for word, count in word_counts.most_common(max_keywords)]


def calculate_optimal_posting_time(
    platform: str,
    target_timezone: str = "UTC"
) -> Dict[str, Any]:
    """Calculate optimal posting time for platform and timezone"""
    
    # Base optimal hours for different platforms (UTC)
    optimal_hours = {
        "linkedin": [8, 9, 10, 17, 18],  # Business hours
        "twitter": [12, 13, 14, 15],     # Lunch and afternoon
        "instagram": [18, 19, 20, 21],   # Evening
        "facebook": [13, 14, 15],        # Afternoon
        "tiktok": [18, 19, 20, 21, 22],  # Evening/Night
        "youtube": [14, 15, 16, 17]      # Afternoon
    }
    
    platform_hours = optimal_hours.get(platform, [12, 13, 14])
    
    # For now, assuming UTC. In production, would handle timezone conversion
    optimal_times = []
    for hour in platform_hours:
        optimal_times.append({
            "hour": hour,
            "time_string": f"{hour:02d}:00",
            "engagement_probability": "High" if hour in platform_hours[:2] else "Medium"
        })
    
    return {
        "platform": platform,
        "timezone": target_timezone,
        "optimal_times": optimal_times,
        "best_days": ["Tuesday", "Wednesday", "Thursday"],  # Generally best performing days
        "avoid_times": ["Early morning (5-7 AM)", "Late night (11 PM - 1 AM)"]
    }


def format_content_for_platform(
    content: str,
    platform: str,
    hashtags: List[str] = None
) -> Dict[str, Any]:
    """Format content for specific platform requirements"""
    
    platform_configs = {
        "linkedin": {"max_length": 3000, "hashtag_limit": 5, "professional": True},
        "twitter": {"max_length": 280, "hashtag_limit": 3, "professional": False},
        "instagram": {"max_length": 2200, "hashtag_limit": 12, "professional": False},
        "facebook": {"max_length": 63206, "hashtag_limit": 5, "professional": False},
        "tiktok": {"max_length": 4000, "hashtag_limit": 8, "professional": False},
        "youtube": {"max_length": 5000, "hashtag_limit": 15, "professional": False}
    }
    
    config = platform_configs.get(platform, platform_configs["linkedin"])
    
    # Truncate content if necessary
    formatted_content = content
    if len(content) > config["max_length"]:
        formatted_content = content[:config["max_length"]-3] + "..."
    
    # Limit hashtags
    formatted_hashtags = hashtags[:config["hashtag_limit"]] if hashtags else []
    
    # Platform-specific formatting
    if platform == "twitter":
        # Twitter prefers more concise content
        if len(formatted_content) > 200:
            formatted_content = content[:200-3] + "..."
    
    elif platform == "linkedin":
        # LinkedIn prefers professional tone
        if not config["professional"]:
            # Would apply professional tone adjustments here
            pass
    
    return {
        "formatted_content": formatted_content,
        "hashtags": formatted_hashtags,
        "character_count": len(formatted_content),
        "platform": platform,
        "within_limits": len(formatted_content) <= config["max_length"]
    }


def generate_content_analytics(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate analytics for content performance prediction"""
    
    analytics = {
        "readability_score": calculate_readability_score(content_data.get("post_content", "")),
        "engagement_factors": analyze_engagement_factors(content_data),
        "hashtag_effectiveness": analyze_hashtag_effectiveness(content_data.get("hashtags", [])),
        "optimal_timing": calculate_optimal_posting_time(content_data.get("platform", "linkedin")),
        "content_score": calculate_content_score(content_data),
        "improvement_suggestions": generate_improvement_suggestions(content_data)
    }
    
    return analytics


def calculate_readability_score(text: str) -> float:
    """Calculate simple readability score"""
    if not text:
        return 0.0
    
    # Simple readability based on sentence and word length
    sentences = text.split('.')
    words = text.split()
    
    if not sentences or not words:
        return 0.0
    
    avg_sentence_length = len(words) / len(sentences)
    avg_word_length = sum(len(word) for word in words) / len(words)
    
    # Higher score = more readable (scale 0-10)
    score = 10 - (avg_sentence_length * 0.1) - (avg_word_length * 0.5)
    return max(0.0, min(10.0, round(score, 1)))


def analyze_engagement_factors(content_data: Dict[str, Any]) -> List[str]:
    """Analyze factors that could impact engagement"""
    factors = []
    
    content = content_data.get("post_content", "")
    hashtags = content_data.get("hashtags", [])
    
    # Check for engaging elements
    if "?" in content:
        factors.append("Contains question - encourages interaction")
    
    if any(emoji in content for emoji in ["🚀", "💡", "🎯", "✨", "💪"]):
        factors.append("Uses engaging emojis")
    
    if content_data.get("call_to_action"):
        factors.append("Has clear call-to-action")
    
    if len(hashtags) >= 3:
        factors.append("Good hashtag usage for discoverability")
    
    if 100 <= len(content) <= 300:
        factors.append("Optimal content length")
    
    return factors


def analyze_hashtag_effectiveness(hashtags: List[str]) -> Dict[str, Any]:
    """Analyze hashtag effectiveness"""
    if not hashtags:
        return {"score": 0, "analysis": "No hashtags provided"}
    
    analysis = {
        "total_hashtags": len(hashtags),
        "effectiveness_score": 0,
        "insights": []
    }
    
    # Check hashtag diversity
    hashtag_lengths = [len(tag) for tag in hashtags]
    avg_length = sum(hashtag_lengths) / len(hashtag_lengths)
    
    if 8 <= avg_length <= 15:
        analysis["effectiveness_score"] += 3
        analysis["insights"].append("Good average hashtag length")
    
    # Check for mix of popular and niche hashtags
    if len(hashtags) >= 5:
        analysis["effectiveness_score"] += 2
        analysis["insights"].append("Good hashtag quantity")
    
    # Check for branded hashtags
    if any(len(tag) > 15 for tag in hashtags):
        analysis["insights"].append("Contains specific/branded hashtags")
    
    analysis["effectiveness_score"] = min(10, analysis["effectiveness_score"])
    
    return analysis


def generate_improvement_suggestions(content_data: Dict[str, Any]) -> List[str]:
    """Generate suggestions for content improvement"""
    suggestions = []
    
    content = content_data.get("post_content", "")
    hashtags = content_data.get("hashtags", [])
    
    # Content length suggestions
    if len(content) < 50:
        suggestions.append("Consider expanding content for better engagement")
    elif len(content) > 500:
        suggestions.append("Consider shortening content for better readability")
    
    # Hashtag suggestions
    if len(hashtags) < 3:
        suggestions.append("Add more hashtags to increase discoverability")
    elif len(hashtags) > 15:
        suggestions.append("Consider reducing hashtag count to avoid spam appearance")
    
    # Engagement suggestions
    if "?" not in content:
        suggestions.append("Consider adding a question to encourage interaction")
    
    if not content_data.get("call_to_action"):
        suggestions.append("Add a clear call-to-action to drive engagement")
    
    return suggestions


def create_content_hash(content: str) -> str:
    """Create unique hash for content to prevent duplicates"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()[:12]


def validate_content_data(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate content data structure and completeness"""
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    required_fields = ["post_content", "platform", "industry"]
    
    for field in required_fields:
        if field not in content_data or not content_data[field]:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Missing required field: {field}")
    
    # Validate hashtags format
    hashtags = content_data.get("hashtags", [])
    invalid_hashtags = [tag for tag in hashtags if not validate_hashtag(tag)]
    
    if invalid_hashtags:
        validation_result["warnings"].append(f"Invalid hashtags found: {invalid_hashtags}")
    
    # Validate platform
    valid_platforms = ["linkedin", "twitter", "instagram", "facebook", "tiktok", "youtube"]
    if content_data.get("platform") not in valid_platforms:
        validation_result["warnings"].append(f"Platform should be one of: {valid_platforms}")
    
    return validation_result

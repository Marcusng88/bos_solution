"""
AI Competitor Content Analysis & Post Generation System

This module provides LangChain-based AI agents for analyzing competitor content
and generating optimized social media posts with relevant hashtags.
"""

# Import main components for external use
# Note: These are imported lazily to avoid initialization issues

__all__ = [
    "ContentPlanningAgent",
    "ContentGenerator", 
    "CompetitorAnalyzer",
    "HashtagResearcher"
]

def get_content_planning_agent():
    """Get ContentPlanningAgent instance"""
    from .agents.main_agent import ContentPlanningAgent
    return ContentPlanningAgent()

def get_content_generator():
    """Get ContentGenerator instance"""
    from .tools.content_generator import ContentGenerator
    return ContentGenerator()

def get_competitor_analyzer():
    """Get CompetitorAnalyzer instance"""
    from .tools.competitor_analyzer import CompetitorAnalyzer
    return CompetitorAnalyzer()

def get_hashtag_researcher():
    """Get HashtagResearcher instance"""
    from .tools.hashtag_researcher import HashtagResearcher
    return HashtagResearcher()

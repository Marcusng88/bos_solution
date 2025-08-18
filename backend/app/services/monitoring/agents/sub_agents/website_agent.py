"""
Website Sub-Agent for Competitor Analysis
Uses Crawl4AI to crawl and analyze competitor websites for strategic insights
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import langchain dependencies conditionally
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.tools import tool
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"LangChain dependencies not available: {e}")
    LANGCHAIN_AVAILABLE = False

# Import Crawl4AI dependencies conditionally
try:
    from crawl4ai import Crawl4AI
    from crawl4ai.web_crawler import WebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"Crawl4AI dependencies not available: {e}")
    CRAWL4AI_AVAILABLE = False

from app.models.competitor import Competitor
from app.core.config import settings
from ...core_service import MonitoringService

logger = logging.getLogger(__name__)


class WebsiteAgent:
    """Website crawling agent for competitor analysis using Crawl4AI"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.monitoring_service = MonitoringService(db)

        self.llm = None
        if LANGCHAIN_AVAILABLE:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash-lite",
                    api_key=settings.GOOGLE_API_KEY,
                    temperature=0.1
                )
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}")

        self.crawler = None
        if CRAWL4AI_AVAILABLE and self.llm:
            try:
                self.crawler = Crawl4AI(
                    llm=self.llm,
                    max_requests_per_minute=20,
                    smart_threading=True,
                    allow_backtracking=False
                )
                logger.info("Crawl4AI crawler initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Crawl4AI: {e}")
        elif not CRAWL4AI_AVAILABLE:
            logger.warning("Crawl4AI not available - website analysis will be limited")

    @tool
    def get_sitemap(self, url: str) -> List[str]:
        """
        Extracts URLs from a website's sitemap.

        Args:
            url (str): The base URL of the website.

        Returns:
            List[str]: A list of URLs found in the sitemap.
        """
        try:
            sitemap_url = url.rstrip('/') + '/sitemap.xml'
            logger.info(f"Attempting to fetch sitemap from: {sitemap_url}")

            # Use WebCrawler to fetch and parse sitemap
            sitemap_crawler = WebCrawler()
            sitemap_content = sitemap_crawler.fetch_url(sitemap_url)

            if not sitemap_content:
                logger.warning(f"Could not fetch sitemap from {sitemap_url}")
                return []

            # Extract URLs from XML content
            urls = re.findall(r'<loc>(.*?)</loc>', sitemap_content)
            logger.info(f"Found {len(urls)} URLs in sitemap for {url}")
            return urls[:50] # Limit to 50 URLs to avoid excessive crawling

        except Exception as e:
            logger.error(f"Error extracting sitemap for {url}: {e}")
            return []

    async def analyze_competitor(self, competitor_id: str, url: str) -> Dict[str, Any]:
        """
        Analyze a competitor's website using Crawl4AI

        Args:
            competitor_id: Database ID of the competitor
            url: URL of the competitor's website to analyze

        Returns:
            Dict containing analysis results and extracted content
        """
        if not self.crawler:
            logger.error("Crawl4AI is not initialized, cannot analyze website.")
            return {"platform": "website", "content": [], "error": "Crawl4AI not available"}

        try:
            logger.info(f"Starting website analysis for competitor {competitor_id}, URL: {url}")

            competitor = await self._get_competitor(competitor_id)
            if not competitor:
                logger.error(f"Competitor {competitor_id} not found in database")
                return {"platform": "website", "content": [], "error": "Competitor not found"}

            analysis_prompt = self._build_analysis_prompt(competitor)

            # Use Crawl4AI to crawl and extract information
            logger.info(f"Running Crawl4AI on {url} with prompt...")
            result = await self.crawler.run_async(url=url, user_prompt=analysis_prompt)

            if not result or not result.extracted_data:
                logger.warning(f"Crawl4AI did not extract any data for {url}")
                return {"platform": "website", "content": [], "status": "completed", "analysis_summary": "No data extracted"}

            logger.info(f"Crawl4AI extracted {len(result.extracted_data)} data points.")

            # Process the extracted data
            processed_content = await self._process_extracted_data(competitor_id, result.extracted_data)

            return {
                "platform": "website",
                "content": processed_content,
                "status": "completed",
                "analysis_summary": f"Extracted {len(processed_content)} significant findings."
            }

        except Exception as e:
            logger.error(f"Error in website analysis for competitor {competitor_id}: {e}")
            return {"platform": "website", "content": [], "error": str(e)}

    def _build_analysis_prompt(self, competitor: Competitor) -> str:
        """Build the analysis prompt for Crawl4AI"""
        return f"""
        Analyze the website of competitor "{competitor.name}" in the {competitor.industry} industry.
        Focus on content updated in the last 24-48 hours if possible.

        Extract the following information:
        1.  **Product Launches & Updates**: Identify any new products, services, or significant updates to existing ones. Look for phrases like "new", "introducing", "updated", "version 2.0".
        2.  **Pricing Changes & Promotions**: Find any changes in pricing, new subscription plans, special offers, or discounts. Look for pages like "pricing", "plans", "sale", "offers".
        3.  **New Features & Capabilities**: Detail any newly announced features or capabilities of their products/services.
        4.  **Brand Messaging & Positioning**: Analyze the key marketing messages on the homepage and about page. What is their value proposition?
        5.  **Customer Testimonials & Case Studies**: Extract any new customer testimonials or case studies that showcase their success.
        6.  **Content & SEO**: Extract meta tags (title, description), keywords, and H1 tags from key pages like the homepage and product pages.

        For each finding, provide the extracted text, the source URL, and a brief summary of its significance.
        """

    async def _process_extracted_data(self, competitor_id: str, extracted_data: List[Dict]) -> List[Dict]:
        """Process data extracted by Crawl4AI and create alerts for significant findings."""
        processed_content = []
        for item in extracted_data:
            try:
                # Assess if the finding is significant enough for an alert
                alert_assessment = await self._assess_finding_for_alert(item)

                if alert_assessment.get("create_alert"):
                    await self._create_website_alert(competitor_id, item, alert_assessment)

                    processed_item = {
                        "type": "website_finding",
                        "alert_created": True,
                        "priority": alert_assessment.get('priority', 'medium'),
                        "summary": alert_assessment.get('summary'),
                        "data": item
                    }
                    processed_content.append(processed_item)

            except Exception as e:
                logger.error(f"Error processing extracted website data item: {e}")

        logger.info(f"Processed {len(extracted_data)} extracted items, created {len(processed_content)} alerts.")
        return processed_content

    async def _assess_finding_for_alert(self, finding: Dict) -> Dict:
        """Use AI to assess if a website finding warrants an alert."""

        prompt = f"""
        Analyze this extracted website content for competitor analysis and determine if it warrants creating an alert.

        EXTRACTED CONTENT:
        {json.dumps(finding, indent=2)}

        ASSESSMENT CRITERIA:
        Determine if the content indicates any of the following alert-worthy events:
        - A new product or service launch.
        - Significant changes to pricing or plans.
        - A major new feature announcement.
        - A strategic shift in brand messaging.
        - A high-profile customer case study.

        RESPONSE FORMAT:
        Provide a JSON response with:
        {{
            "create_alert": true/false,
            "priority": "low/medium/high",
            "summary": "Brief summary of why an alert is or isn't needed",
            "alert_type": "product_launch/pricing_change/new_feature/messaging_shift/case_study/other"
        }}

        Be selective - only recommend alerts for truly significant competitive events. A minor blog post or a small text change is not alert-worthy.
        """

        if not self.llm:
            return {"create_alert": False, "summary": "LLM not available for assessment"}

        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content.strip()

            # Extract JSON from response
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                json_str = match.group(0)
                return json.loads(json_str)
            else:
                logger.error(f"Failed to parse AI response as JSON: {content}")
                return {"create_alter": False, "summary": "AI response parsing failed"}

        except Exception as e:
            logger.error(f"Error assessing content for alerts: {e}")
            return {"create_alert": False, "summary": f"Assessment error: {e}"}

    async def _create_website_alert(self, competitor_id: str, finding: Dict, alert_assessment: Dict) -> None:
        """Create an alert record for a significant website finding."""
        try:
            competitor = await self._get_competitor(competitor_id)
            if not competitor:
                logger.error(f"Cannot create alert: competitor {competitor_id} not found")
                return

            alert_type = f"website_{alert_assessment.get('alert_type', 'finding')}"
            priority = alert_assessment.get('priority', 'medium')
            title = f"Website Intelligence: {alert_assessment.get('alert_type', 'Significant Finding').replace('_', ' ').title()}"
            message = alert_assessment.get('summary', 'AI analysis detected a significant change on the competitor website.')

            alert_metadata = {
                "platform": "website",
                "source_url": finding.get("source_url"),
                "extracted_data": finding,
                "ai_assessment": alert_assessment,
            }

            await self.monitoring_service.create_alert(
                user_id=competitor.user_id,
                competitor_id=competitor_id,
                alert_type=alert_type,
                title=title,
                message=message,
                priority=priority,
                alert_metadata=alert_metadata
            )
            logger.info(f"🚨 Created website intelligence alert: {alert_type}")

        except Exception as e:
            logger.error(f"Error creating website alert: {e}")

    async def _get_competitor(self, competitor_id: str) -> Optional[Competitor]:
        """Get competitor from database"""
        try:
            result = await self.db.execute(
                select(Competitor).where(Competitor.id == competitor_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting competitor {competitor_id}: {e}")
            return None

    async def close(self):
        """Close any resources"""
        logger.info("WebsiteAgent closed")
        pass

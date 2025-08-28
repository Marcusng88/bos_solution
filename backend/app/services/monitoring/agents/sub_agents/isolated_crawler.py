"""
Simple Isolated Crawler Service for Website Intelligence
Runs crawl4ai in a separate asyncio event loop to avoid conflicts with FastAPI
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import os
import sys
import concurrent.futures
import threading

logger = logging.getLogger(__name__)


class SimpleIsolatedCrawler:
    """Simple isolated crawler that runs crawl4ai in a separate asyncio event loop"""
    
    def __init__(self):
        """Initialize the simple isolated crawler"""
        logger.info("🔒 Simple isolated crawler initialized")
    
    async def crawl_websites(self, urls: List[str], extraction_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Crawl websites using isolated asyncio event loop
        
        Args:
            urls: List of URLs to crawl
            extraction_config: Configuration for LLM extraction if available
            
        Returns:
            List of crawling results
        """
        try:
            logger.info(f"🔒 Starting simple isolated crawling for {len(urls)} URLs")
            
            # Use asyncio.create_task to run in isolated context
            results = await self._crawl_in_isolated_context(urls, extraction_config)
            logger.info(f"✅ Simple isolated crawling completed successfully with {len(results)} results")
            return results
                
        except Exception as e:
            logger.error(f"❌ Error in simple isolated crawling: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return []
    
    async def _crawl_in_isolated_context(self, urls: List[str], extraction_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Crawl websites in an isolated context"""
        try:
            # Import crawl4ai in the isolated environment
            try:
                from crawl4ai import AsyncWebCrawler
                from crawl4ai.extraction_strategy import LLMExtractionStrategy
                from crawl4ai import LLMConfig
                logger.info("✅ Successfully imported crawl4ai in isolated context")
            except ImportError as e:
                logger.error(f"❌ Failed to import crawl4ai: {e}")
                return [{
                    'url': url,
                    'status': 'error',
                    'error': f'crawl4ai import failed: {e}'
                } for url in urls]
            
            results = []
            for url in urls:
                try:
                    logger.info(f"🕷️ Crawling: {url}")
                    
                    # Create a new crawler instance for each URL to ensure isolation
                    async with AsyncWebCrawler(verbose=False) as crawler:
                        # Set up extraction strategy if provided
                        extraction_strategy = None
                        if extraction_config and extraction_config.get('use_llm'):
                            try:
                                # Create LLM extraction strategy with enhanced configuration
                                # Allow customization through extraction_config
                                provider = extraction_config.get('provider', 'google')
                                temperature = extraction_config.get('temperature', 0.1)
                                max_tokens = extraction_config.get('max_tokens', 1000)
                                chunk_threshold = extraction_config.get('chunk_token_threshold', 1200)
                                overlap = extraction_config.get('overlap_rate', 0.1)
                                input_fmt = extraction_config.get('input_format', 'markdown')
                                
                                extraction_strategy = LLMExtractionStrategy(
                                    llm_config=LLMConfig(
                                        provider=provider,
                                        api_token=extraction_config.get('api_key')
                                    ),
                                    schema=extraction_config.get('schema'),
                                    extraction_type="schema",
                                    instruction=extraction_config.get('instruction', "Extract structured information from the website content"),
                                    chunk_token_threshold=chunk_threshold,
                                    overlap_rate=overlap,
                                    apply_chunking=extraction_config.get('apply_chunking', True),
                                    input_format=input_fmt,
                                    verbose=extraction_config.get('verbose', True),
                                    extra_args={
                                        "temperature": temperature,
                                        "max_tokens": max_tokens
                                    }
                                )
                                logger.info(f"✅ Successfully created LLM extraction strategy for {url} using {provider}")
                            except Exception as e:
                                logger.warning(f"❌ Failed to create LLM extraction strategy: {e}")
                                logger.warning(f"   Extraction config: {extraction_config}")
                                extraction_strategy = None
                        
                        # Crawl the website
                        result = await crawler.arun(
                            url=url,
                            extraction_strategy=extraction_strategy,
                            bypass_cache=True,
                            user_agent="Mozilla/5.0 (compatible; CompetitorBot/1.0)"
                        )
                        
                        if result.success:
                            content_item = {
                                'url': url,
                                'title': result.extracted_content.get('title', '') if result.extracted_content else '',
                                'content': result.markdown[:2000] if result.markdown else '',
                                'extracted_data': result.extracted_content if result.extracted_content else {},
                                'crawled_at': datetime.now(timezone.utc).isoformat(),
                                'content_hash': hashlib.md5((result.markdown or '').encode()).hexdigest(),
                                'status': 'success'
                            }
                            results.append(content_item)
                            logger.info(f"   ✅ Extracted content from {url}")
                        else:
                            results.append({
                                'url': url,
                                'status': 'failed',
                                'error': result.error_message
                            })
                            logger.warning(f"   ❌ Failed to crawl {url}: {result.error_message}")
                
                except Exception as e:
                    logger.error(f"❌ Error crawling {url}: {e}")
                    results.append({
                        'url': url,
                        'status': 'error',
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in crawl loop: {e}")
            return [{
                'url': url,
                'status': 'error',
                'error': str(e)
            } for url in urls]
    
    async def crawl_single_website(self, url: str, extraction_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Crawl a single website using isolated context
        
        Args:
            url: URL to crawl
            extraction_config: Configuration for LLM extraction if available
            
        Returns:
            Crawling result
        """
        results = await self.crawl_websites([url], extraction_config)
        return results[0] if results else {'url': url, 'status': 'failed', 'error': 'No results returned'}


class SimpleIsolatedCrawlerManager:
    """Manager for multiple simple isolated crawler instances"""
    
    def __init__(self, max_concurrent: int = 3):
        """
        Initialize the crawler manager
        
        Args:
            max_concurrent: Maximum number of concurrent crawler instances
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        logger.info(f"🔒 Simple isolated crawler manager initialized with max {max_concurrent} concurrent instances")
    
    async def crawl_with_semaphore(self, urls: List[str], extraction_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Crawl websites with concurrency control"""
        async with self.semaphore:
            crawler = SimpleIsolatedCrawler()
            return await crawler.crawl_websites(urls, extraction_config)
    
    async def crawl_multiple_batches(self, url_batches: List[List[str]], extraction_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Crawl multiple batches of URLs concurrently
        
        Args:
            url_batches: List of URL batches to crawl
            extraction_config: Configuration for LLM extraction if available
            
        Returns:
            Combined crawling results
        """
        try:
            logger.info(f"🔒 Starting batch crawling for {len(url_batches)} batches")
            
            # Create tasks for each batch
            tasks = []
            for batch in url_batches:
                task = self.crawl_with_semaphore(batch, extraction_config)
                tasks.append(task)
            
            # Wait for all batches to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results and handle exceptions
            all_results = []
            for i, batch_result in enumerate(batch_results):
                if isinstance(batch_result, Exception):
                    logger.error(f"❌ Batch {i} failed: {batch_result}")
                    # Create error results for this batch
                    batch_urls = url_batches[i] if i < len(url_batches) else []
                    error_results = [{
                        'url': url,
                        'status': 'error',
                        'error': f'Batch processing failed: {batch_result}'
                    } for url in batch_urls]
                    all_results.extend(error_results)
                else:
                    all_results.extend(batch_result)
            
            logger.info(f"✅ Completed {len(url_batches)} batches with {len(all_results)} total results")
            return all_results
            
        except Exception as e:
            logger.error(f"❌ Error in batch crawling: {e}")
            return []


async def crawl_websites_isolated(urls: List[str], extraction_config: Dict[str, Any] = None, max_concurrent: int = 3) -> List[Dict[str, Any]]:
    """
    Convenience function to crawl websites in isolated environment
    
    Args:
        urls: List of URLs to crawl
        extraction_config: Configuration for LLM extraction if available
        max_concurrent: Maximum number of concurrent crawler instances
        
    Returns:
        List of crawling results
    """
    try:
        # Split URLs into batches for better concurrency control
        batch_size = max(1, len(urls) // max_concurrent)
        url_batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
        
        manager = SimpleIsolatedCrawlerManager(max_concurrent)
        return await manager.crawl_multiple_batches(url_batches, extraction_config)
        
    except Exception as e:
        logger.error(f"❌ Error in isolated crawling: {e}")
        return [{
            'url': url,
            'status': 'error',
            'error': str(e)
        } for url in urls]

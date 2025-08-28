"""
Multiprocessing Crawler Service for Website Intelligence
Runs crawl4ai in separate Python processes to avoid FastAPI async runtime conflicts
"""

import multiprocessing
import logging
import json
import hashlib
import pickle
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

logger = logging.getLogger(__name__)


def _crawl_single_url_worker(url: str, extraction_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Worker function that runs in a separate process to crawl a single URL
    
    This function runs in complete isolation from the main FastAPI process
    """
    try:
        # Import crawl4ai in the worker process
        from crawl4ai import AsyncWebCrawler
        from crawl4ai.extraction_strategy import LLMExtractionStrategy
        from crawl4ai import LLMConfig
        
        # Create a new event loop for this process
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        except RuntimeError:
            # Loop already exists
            pass
        
        async def _crawl_url():
            try:
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
                            print(f"✅ Successfully created LLM extraction strategy for {url} using {provider}")
                        except Exception as e:
                            print(f"❌ Failed to create LLM extraction strategy: {e}")
                            print(f"   Extraction config: {extraction_config}")
                            extraction_strategy = None
                    
                    # Crawl the website
                    result = await crawler.arun(
                        url=url,
                        extraction_strategy=extraction_strategy,
                        bypass_cache=True,
                        user_agent="Mozilla/5.0 (compatible; CompetitorBot/1.0)"
                    )
                    
                    if result.success:
                        return {
                            'url': url,
                            'title': result.extracted_content.get('title', '') if result.extracted_content else '',
                            'content': result.markdown[:2000] if result.markdown else '',
                            'extracted_data': result.extracted_content if result.extracted_content else {},
                            'crawled_at': datetime.now(timezone.utc).isoformat(),
                            'content_hash': hashlib.md5((result.markdown or '').encode()).hexdigest(),
                            'status': 'success'
                        }
                    else:
                        return {
                            'url': url,
                            'status': 'failed',
                            'error': result.error_message
                        }
            except Exception as e:
                return {
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                }
        
        # Run the async crawling function
        result = loop.run_until_complete(_crawl_url())
        loop.close()
        return result
        
    except ImportError as e:
        return {
            'url': url,
            'status': 'error',
            'error': f'crawl4ai import failed: {e}'
        }
    except Exception as e:
        return {
            'url': url,
            'status': 'error',
            'error': str(e)
        }


def _crawl_batch_worker(urls: List[str], extraction_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Worker function that runs in a separate process to crawl a batch of URLs
    """
    results = []
    for url in urls:
        try:
            result = _crawl_single_url_worker(url, extraction_config)
            results.append(result)
            # Small delay between URLs in the same batch
            time.sleep(0.5)
        except Exception as e:
            results.append({
                'url': url,
                'status': 'error',
                'error': str(e)
            })
    return results


class MultiprocessingCrawler:
    """Multiprocessing crawler that runs crawl4ai in separate Python processes"""
    
    def __init__(self, max_workers: int = None):
        """
        Initialize the multiprocessing crawler
        
        Args:
            max_workers: Maximum number of worker processes (defaults to CPU count)
        """
        if max_workers is None:
            max_workers = min(multiprocessing.cpu_count(), 4)  # Cap at 4 to avoid overwhelming
        
        self.max_workers = max_workers
        logger.info(f"🔒 Multiprocessing crawler initialized with {self.max_workers} workers")
    
    def crawl_websites(self, urls: List[str], extraction_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Crawl websites using separate processes
        
        Args:
            urls: List of URLs to crawl
            extraction_config: Configuration for LLM extraction if available
            
        Returns:
            List of crawling results
        """
        try:
            logger.info(f"🔒 Starting multiprocessing crawling for {len(urls)} URLs")
            
            # Use ProcessPoolExecutor to run crawling in separate processes
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all URLs as individual tasks
                future_to_url = {
                    executor.submit(_crawl_single_url_worker, url, extraction_config): url 
                    for url in urls
                }
                
                results = []
                for future in as_completed(future_to_url):
                    try:
                        result = future.result()
                        results.append(result)
                        logger.info(f"   ✅ Completed crawling: {result['url']}")
                    except Exception as e:
                        url = future_to_url[future]
                        logger.error(f"   ❌ Error crawling {url}: {e}")
                        results.append({
                            'url': url,
                            'status': 'error',
                            'error': str(e)
                        })
            
            logger.info(f"✅ Multiprocessing crawling completed with {len(results)} results")
            return results
                
        except Exception as e:
            logger.error(f"❌ Error in multiprocessing crawling: {e}")
            return [{
                'url': url,
                'status': 'error',
                'error': str(e)
            } for url in urls]
    
    def crawl_websites_batched(self, urls: List[str], extraction_config: Dict[str, Any] = None, batch_size: int = 2) -> List[Dict[str, Any]]:
        """
        Crawl websites in batches using separate processes
        
        Args:
            urls: List of URLs to crawl
            extraction_config: Configuration for LLM extraction if available
            batch_size: Number of URLs per batch
            
        Returns:
            List of crawling results
        """
        try:
            logger.info(f"🔒 Starting batched multiprocessing crawling for {len(urls)} URLs (batch size: {batch_size})")
            
            # Split URLs into batches
            url_batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
            
            all_results = []
            
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit batch tasks
                future_to_batch = {
                    executor.submit(_crawl_batch_worker, batch, extraction_config): batch 
                    for batch in url_batches
                }
                
                for future in as_completed(future_to_batch):
                    try:
                        batch_results = future.result()
                        all_results.extend(batch_results)
                        batch = future_to_batch[future]
                        logger.info(f"   ✅ Completed batch with {len(batch)} URLs")
                    except Exception as e:
                        batch = future_to_batch[future]
                        logger.error(f"   ❌ Error in batch processing: {e}")
                        # Create error results for this batch
                        error_results = [{
                            'url': url,
                            'status': 'error',
                            'error': f'Batch processing failed: {e}'
                        } for url in batch]
                        all_results.extend(error_results)
            
            logger.info(f"✅ Batched multiprocessing crawling completed with {len(all_results)} total results")
            return all_results
                
        except Exception as e:
            logger.error(f"❌ Error in batched multiprocessing crawling: {e}")
            return [{
                'url': url,
                'status': 'error',
                'error': str(e)
            } for url in urls]


class MultiprocessingCrawlerManager:
    """Manager for multiprocessing crawler instances with advanced features"""
    
    def __init__(self, max_workers: int = None, batch_size: int = 2):
        """
        Initialize the crawler manager
        
        Args:
            max_workers: Maximum number of worker processes
            batch_size: Number of URLs per batch
        """
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.crawler = MultiprocessingCrawler(max_workers)
        logger.info(f"🔒 Multiprocessing crawler manager initialized with {max_workers} workers, batch size {batch_size}")
    
    def crawl_with_strategy(self, urls: List[str], strategy: str = "batch", extraction_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Crawl websites using the specified strategy
        
        Args:
            urls: List of URLs to crawl
            strategy: Crawling strategy - "individual", "batch", or "adaptive"
            extraction_config: Configuration for LLM extraction if available
            
        Returns:
            List of crawling results
        """
        try:
            if strategy == "individual":
                return self.crawler.crawl_websites(urls, extraction_config)
            elif strategy == "batch":
                return self.crawler.crawl_websites_batched(urls, extraction_config, self.batch_size)
            elif strategy == "adaptive":
                # Choose strategy based on number of URLs
                if len(urls) <= 3:
                    return self.crawler.crawl_websites(urls, extraction_config)
                else:
                    return self.crawler.crawl_websites_batched(urls, extraction_config, self.batch_size)
            else:
                logger.warning(f"Unknown strategy '{strategy}', using 'batch'")
                return self.crawler.crawl_websites_batched(urls, extraction_config, self.batch_size)
                
        except Exception as e:
            logger.error(f"❌ Error in strategy-based crawling: {e}")
            return [{
                'url': url,
                'status': 'error',
                'error': str(e)
            } for url in urls]


# Convenience functions for easy use
def crawl_websites_multiprocessing(urls: List[str], extraction_config: Dict[str, Any] = None, max_workers: int = None) -> List[Dict[str, Any]]:
    """
    Convenience function to crawl websites using multiprocessing
    
    Args:
        urls: List of URLs to crawl
        extraction_config: Configuration for LLM extraction if available
        max_workers: Maximum number of worker processes
        
    Returns:
        List of crawling results
    """
    try:
        crawler = MultiprocessingCrawler(max_workers)
        return crawler.crawl_websites(urls, extraction_config)
    except Exception as e:
        logger.error(f"❌ Error in multiprocessing crawling: {e}")
        return [{
            'url': url,
            'status': 'error',
            'error': str(e)
        } for url in urls]


def crawl_websites_multiprocessing_batched(urls: List[str], extraction_config: Dict[str, Any] = None, max_workers: int = None, batch_size: int = 2) -> List[Dict[str, Any]]:
    """
    Convenience function to crawl websites using batched multiprocessing
    
    Args:
        urls: List of URLs to crawl
        extraction_config: Configuration for LLM extraction if available
        max_workers: Maximum number of worker processes
        batch_size: Number of URLs per batch
        
    Returns:
        List of crawling results
    """
    try:
        crawler = MultiprocessingCrawler(max_workers)
        return crawler.crawl_websites_batched(urls, extraction_config, batch_size)
    except Exception as e:
        logger.error(f"❌ Error in batched multiprocessing crawling: {e}")
        return [{
            'url': url,
            'status': 'error',
            'error': str(e)
        } for url in urls]

"""
Isolated Crawler Service for Website Intelligence
Runs crawl4ai in a separate isolated environment to avoid conflicts with FastAPI
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import subprocess
import tempfile
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class IsolatedCrawler:
    """Isolated crawler that runs crawl4ai in a separate Python process"""
    
    def __init__(self, python_executable: str = None):
        """
        Initialize the isolated crawler
        
        Args:
            python_executable: Path to Python executable to use for isolated environment
        """
        self.python_executable = python_executable or sys.executable
        self.crawler_script_path = self._create_crawler_script()
        logger.info(f"🔒 Isolated crawler initialized with Python: {self.python_executable}")
    
    def _create_crawler_script(self) -> str:
        """Create the isolated crawler script file"""
        script_content = '''
import asyncio
import json
import sys
import traceback
from datetime import datetime, timezone
import hashlib

async def crawl_website(url, extraction_config=None):
    """Crawl a single website using crawl4ai"""
    try:
        # Import crawl4ai in isolated environment
        from crawl4ai import AsyncWebCrawler
        from crawl4ai.extraction_strategy import LLMExtractionStrategy
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            # Set up extraction strategy if provided
            extraction_strategy = None
            if extraction_config and extraction_config.get('use_llm'):
                try:
                    extraction_strategy = LLMExtractionStrategy(
                        provider="google",
                        api_token=extraction_config.get('api_key'),
                        schema=extraction_config.get('schema'),
                        extraction_type="schema"
                    )
                except Exception as e:
                    print(f"Failed to create LLM extraction strategy: {e}", file=sys.stderr)
            
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
                return content_item
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
            'error': str(e),
            'traceback': traceback.format_exc()
        }

async def crawl_multiple_websites(urls, extraction_config=None):
    """Crawl multiple websites"""
    results = []
    for url in urls:
        try:
            result = await crawl_website(url, extraction_config)
            results.append(result)
        except Exception as e:
            results.append({
                'url': url,
                'status': 'error',
                'error': str(e)
            })
    return results

def main():
    """Main entry point for isolated crawler"""
    try:
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())
        urls = input_data.get('urls', [])
        extraction_config = input_data.get('extraction_config')
        
        # Run crawling
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(crawl_multiple_websites(urls, extraction_config))
        loop.close()
        
        # Output results to stdout
        print(json.dumps(results, default=str))
        
    except Exception as e:
        error_result = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        print(json.dumps(error_result, default=str))
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        # Create temporary script file
        script_dir = Path(__file__).parent
        script_path = script_dir / "isolated_crawler_script.py"
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(f"📝 Created isolated crawler script at: {script_path}")
        return str(script_path)
    
    async def crawl_websites(self, urls: List[str], extraction_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Crawl websites using isolated Python process
        
        Args:
            urls: List of URLs to crawl
            extraction_config: Configuration for LLM extraction if available
            
        Returns:
            List of crawling results
        """
        try:
            logger.info(f"🔒 Starting isolated crawling for {len(urls)} URLs")
            
            # Prepare input data
            input_data = {
                'urls': urls,
                'extraction_config': extraction_config
            }
            
            # Convert to JSON string
            input_json = json.dumps(input_data)
            
            # Run isolated crawler process
            process = await asyncio.create_subprocess_exec(
                self.python_executable,
                self.crawler_script_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send input and get output
            stdout, stderr = await process.communicate(input=input_json.encode())
            
            if process.returncode != 0:
                logger.error(f"❌ Isolated crawler failed with return code: {process.returncode}")
                if stderr:
                    logger.error(f"Stderr: {stderr.decode()}")
                return []
            
            # Parse results
            try:
                results = json.loads(stdout.decode())
                logger.info(f"✅ Isolated crawling completed successfully")
                return results
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse crawler results: {e}")
                if stdout:
                    logger.error(f"Raw stdout: {stdout.decode()}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error in isolated crawling: {e}")
            return []
    
    async def crawl_single_website(self, url: str, extraction_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Crawl a single website using isolated process
        
        Args:
            url: URL to crawl
            extraction_config: Configuration for LLM extraction if available
            
        Returns:
            Crawling result
        """
        results = await self.crawl_websites([url], extraction_config)
        return results[0] if results else {'url': url, 'status': 'failed', 'error': 'No results returned'}
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if os.path.exists(self.crawler_script_path):
                os.remove(self.crawler_script_path)
                logger.info("🧹 Cleaned up isolated crawler script")
        except Exception as e:
            logger.warning(f"⚠️  Failed to cleanup crawler script: {e}")


class IsolatedCrawlerManager:
    """Manager for multiple isolated crawler instances"""
    
    def __init__(self, max_concurrent: int = 3):
        """
        Initialize the crawler manager
        
        Args:
            max_concurrent: Maximum number of concurrent crawler processes
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.crawlers = []
        logger.info(f"🔒 Isolated crawler manager initialized with max {max_concurrent} concurrent processes")
    
    async def crawl_with_semaphore(self, urls: List[str], extraction_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Crawl websites with concurrency control"""
        async with self.semaphore:
            crawler = IsolatedCrawler()
            try:
                return await crawler.crawl_websites(urls, extraction_config)
            finally:
                crawler.cleanup()
    
    async def crawl_multiple_batches(self, url_batches: List[List[str]], extraction_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Crawl multiple batches of URLs concurrently
        
        Args:
            url_batches: List of URL batches to crawl
            extraction_config: Configuration for LLM extraction if available
            
        Returns:
            Combined results from all batches
        """
        tasks = []
        for batch in url_batches:
            if batch:  # Only create tasks for non-empty batches
                task = self.crawl_with_semaphore(batch, extraction_config)
                tasks.append(task)
        
        if not tasks:
            return []
        
        # Execute all batches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results and handle exceptions
        combined_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Batch {i} failed: {result}")
                # Add error results for failed batches
                for url in url_batches[i]:
                    combined_results.append({
                        'url': url,
                        'status': 'error',
                        'error': str(result)
                    })
            else:
                combined_results.extend(result)
        
        logger.info(f"✅ Completed {len(url_batches)} batches with {len(combined_results)} total results")
        return combined_results
    
    def cleanup(self):
        """Clean up all crawler instances"""
        for crawler in self.crawlers:
            try:
                crawler.cleanup()
            except Exception as e:
                logger.warning(f"⚠️  Failed to cleanup crawler: {e}")
        self.crawlers.clear()
        logger.info("🧹 Cleaned up all crawler instances")


# Convenience function for easy usage
async def crawl_websites_isolated(urls: List[str], extraction_config: Dict[str, Any] = None, max_concurrent: int = 3) -> List[Dict[str, Any]]:
    """
    Convenience function to crawl websites in isolated environment
    
    Args:
        urls: List of URLs to crawl
        extraction_config: Configuration for LLM extraction if available
        max_concurrent: Maximum number of concurrent crawler processes
        
    Returns:
        List of crawling results
    """
    manager = IsolatedCrawlerManager(max_concurrent)
    try:
        return await manager.crawl_multiple_batches([urls], extraction_config)
    finally:
        manager.cleanup()

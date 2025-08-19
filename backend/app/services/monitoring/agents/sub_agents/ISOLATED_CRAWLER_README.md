# Isolated Crawler for Website Intelligence

## Overview

The isolated crawler is a solution to prevent conflicts between crawl4ai and the FastAPI environment. It runs crawl4ai in a separate isolated Python process and communicates results back to the main application.

## Why Isolated Crawler?

The `NotImplementedError` you encountered is typically caused by:
- Event loop conflicts between crawl4ai and FastAPI
- Subprocess transport issues on Windows
- Async context conflicts

The isolated crawler solves these issues by:
1. **Process Isolation**: Runs crawl4ai in a separate Python process
2. **Clean Environment**: Each crawler process has its own event loop
3. **Communication**: Uses JSON over stdin/stdout for data exchange
4. **Fallback Support**: Falls back to direct crawling if isolated mode fails

## Architecture

```
FastAPI App (Main Process)
    ↓
Website Agent
    ↓
Isolated Crawler Manager
    ↓
Isolated Crawler Process (Separate Python process)
    ↓
crawl4ai (in isolated environment)
    ↓
Results returned via JSON
```

## Files

- `isolated_crawler.py` - Main isolated crawler implementation
- `isolated_crawler_requirements.txt` - Dependencies for isolated environment
- `setup_isolated_crawler.py` - Setup script for isolated environment
- `test_isolated_crawler.py` - Test script to verify functionality

## Setup

### 1. Install Dependencies

```bash
cd backend/app/services/monitoring/agents/sub_agents/
python setup_isolated_crawler.py
```

### 2. Verify Installation

```bash
python test_isolated_crawler.py
```

## Usage

### Basic Usage

```python
from app.services.monitoring.agents.sub_agents.isolated_crawler import crawl_websites_isolated

# Simple crawling
results = await crawl_websites_isolated([
    "https://example.com",
    "https://example.org"
])

# With LLM extraction
extraction_config = {
    'use_llm': True,
    'api_key': 'your_google_api_key',
    'schema': {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "main_content": {"type": "string"}
        }
    }
}

results = await crawl_websites_isolated(
    urls=["https://example.com"],
    extraction_config=extraction_config
)
```

### Advanced Usage

```python
from app.services.monitoring.agents.sub_agents.isolated_crawler import IsolatedCrawlerManager

# Create manager with concurrency control
manager = IsolatedCrawlerManager(max_concurrent=5)

# Crawl multiple batches
url_batches = [
    ["https://site1.com", "https://site2.com"],
    ["https://site3.com", "https://site4.com"]
]

results = await manager.crawl_multiple_batches(url_batches)

# Clean up
manager.cleanup()
```

## Configuration

### Environment Variables

- `GOOGLE_API_KEY` - For LLM extraction (optional)
- `MAX_CONCURRENT_CRAWLERS` - Maximum concurrent crawler processes (default: 3)

### Crawler Settings

- **Max Concurrent**: Control how many isolated processes run simultaneously
- **Timeout**: Each crawler process has its own timeout
- **Retry Logic**: Failed crawls are logged but don't stop the process

## Error Handling

The isolated crawler includes comprehensive error handling:

1. **Process Failures**: If isolated crawler fails, falls back to direct crawling
2. **Communication Errors**: JSON parsing errors are caught and logged
3. **Resource Cleanup**: Temporary files and processes are cleaned up automatically
4. **Graceful Degradation**: Continues working even if some crawls fail

## Performance

- **Concurrent Processing**: Multiple URLs can be crawled simultaneously
- **Resource Management**: Each crawler process is isolated and cleaned up
- **Memory Efficiency**: Results are streamed via JSON, not kept in memory
- **Scalability**: Can handle hundreds of URLs with proper batching

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure crawl4ai is installed in the isolated environment
2. **Permission Errors**: Check file permissions for script creation
3. **Memory Issues**: Reduce `max_concurrent` if running out of memory
4. **Timeout Issues**: Some websites may take longer to crawl

### Debug Mode

Enable debug logging to see detailed information:

```python
import logging
logging.getLogger('app.services.monitoring.agents.sub_agents.isolated_crawler').setLevel(logging.DEBUG)
```

### Testing

Run the test script to verify everything works:

```bash
python test_isolated_crawler.py
```

## Integration with Website Agent

The website agent automatically uses the isolated crawler:

1. **Primary Method**: Uses isolated crawler for all website crawling
2. **Fallback**: Falls back to direct crawling if isolated method fails
3. **Seamless**: No changes needed in your existing code
4. **Transparent**: Results format remains the same

## Benefits

✅ **No More NotImplementedError**: Eliminates event loop conflicts
✅ **Better Stability**: Isolated processes prevent crashes
✅ **Improved Performance**: Concurrent crawling with resource isolation
✅ **Easy Maintenance**: Clean separation of concerns
✅ **Fallback Support**: Graceful degradation if isolated mode fails
✅ **Windows Compatible**: Works on all platforms including Windows

## Future Enhancements

- **Docker Support**: Containerized isolated environments
- **Load Balancing**: Distribute crawling across multiple machines
- **Caching**: Persistent cache for crawled content
- **Metrics**: Detailed performance and success rate tracking
- **Custom Extractors**: Support for custom extraction strategies

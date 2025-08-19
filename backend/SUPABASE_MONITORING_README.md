# Supabase-Based Monitoring System

## Overview

The continuous monitoring system has been revised to use **direct Supabase queries** instead of SQLAlchemy database sessions. This solves the issue where agents couldn't access competitor details from the database.

**✅ ALL AI AGENTS UPDATED**: All monitoring agents have been updated to remove SQLAlchemy dependencies and work with the new Supabase-based system.

## Problem Solved

**Previous Issue:**
```
2025-08-19 22:10:31,045 - WARNING - ⚠️ No database session available - cannot fetch competitor details as the agents cannot get the information from database for current competitor all
```

**Solution:**
- Agents now use direct Supabase client to access database
- No dependency on SQLAlchemy sessions
- Independent database operations for each agent
- All 5 AI agents updated and tested

## Architecture Changes

### 1. New Supabase Client (`supabase_client.py`)
- Direct database operations without SQLAlchemy sessions
- Methods for getting competitor details, saving monitoring data, creating alerts
- Independent database access for each agent

### 2. Updated Orchestrator (`orchestrator.py`)
- Now fetches competitor details from Supabase before running agents
- Processes and saves monitoring data directly to database
- Creates alerts for new posts and content changes
- No longer requires database sessions

### 3. Updated Scheduler (`scheduler.py`)
- Uses Supabase client to get competitors due for scanning
- Simplified architecture without session dependencies
- Better error handling and task management

### 4. Updated AI Agents (All 5 Agents)
All monitoring agents have been updated to remove SQLAlchemy dependencies:

#### ✅ **YouTube Agent** (`youtube_agent.py`)
- Removed SQLAlchemy imports and database session requirements
- Simplified to use YouTube Data API directly
- No more `MonitoringService` dependency

#### ✅ **Website Agent** (`website_agent.py`)
- Removed SQLAlchemy imports and database session requirements
- Simplified to use Crawl4AI directly
- No more `MonitoringService` dependency

#### ✅ **Browser Agent** (`browser_agent.py`)
- Removed SQLAlchemy imports and database session requirements
- Simplified to use Tavily search API directly
- No more `MonitoringService` dependency

#### ✅ **Instagram Agent** (`instagram_agent.py`)
- Removed SQLAlchemy imports and database session requirements
- Simplified to work without database dependencies
- Ready for Instagram API integration

#### ✅ **Twitter Agent** (`twitter_agent.py`)
- Removed SQLAlchemy imports and database session requirements
- Simplified to work without database dependencies
- Ready for Twitter API integration

## Key Benefits

### ✅ **Database Access**
- Agents can now access competitor details directly
- No session dependency issues
- Real-time database queries

### ✅ **Independent Operations**
- Each agent operates independently
- No shared database session requirements
- Better error isolation

### ✅ **Direct Supabase Integration**
- Uses Supabase client directly
- Leverages Supabase features (real-time, auth, etc.)
- Simplified database operations

### ✅ **Better Error Handling**
- Clear error messages when competitors not found
- Graceful fallbacks for missing data
- Detailed logging for debugging

### ✅ **Agent Independence**
- All agents can be initialized without database sessions
- Each agent handles its own API calls and data processing
- No more "No database session available" errors

## Database Operations

### Competitor Data Access
```python
# Get competitor details
competitor = await supabase_client.get_competitor_details(competitor_id)
if competitor:
    name = competitor.get('name')
    website = competitor.get('website_url')
    social_handles = competitor.get('social_media_handles', {})
```

### Monitoring Data Storage
```python
# Save new monitoring data
data_id = await supabase_client.save_monitoring_data({
    'competitor_id': competitor_id,
    'platform': 'instagram',
    'content_text': 'Post content...',
    'content_hash': 'abc123...',
    # ... other fields
})
```

### Alert Creation
```python
# Create monitoring alerts
alert_id = await supabase_client.create_alert({
    'user_id': user_id,
    'competitor_id': competitor_id,
    'alert_type': 'new_post',
    'title': 'New Post Detected',
    # ... other fields
})
```

## Environment Variables

Make sure these are set in your `.env` file:

```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## Testing

### Test the Supabase System
```bash
cd backend
python test_supabase_monitoring.py
```

### Test All Agents (No SQLAlchemy)
```bash
cd backend
python test_agents_no_sqlalchemy.py
```

This will test:
- ✅ Supabase connection
- ✅ Database operations
- ✅ All 5 AI agents without SQLAlchemy
- ✅ Monitoring service integration

## Migration from SQLAlchemy

### What Changed
1. **Database Access**: Direct Supabase queries instead of SQLAlchemy sessions
2. **Agent Independence**: Each agent can access database independently
3. **Error Handling**: Better error messages and fallbacks
4. **Data Processing**: Direct database operations for monitoring data
5. **Agent Architecture**: All agents updated to remove SQLAlchemy dependencies

### What Remains the Same
1. **Agent Logic**: Individual agent implementations unchanged
2. **Database Schema**: Same tables and relationships
3. **API Endpoints**: Frontend integration unchanged
4. **Monitoring Flow**: Same monitoring workflow

## Usage Example

```python
from app.services.monitoring.orchestrator import SimpleMonitoringService

# Create monitoring service
monitoring_service = SimpleMonitoringService()

# Run monitoring for a competitor
result = await monitoring_service.run_monitoring_for_competitor(
    competitor_id="competitor-uuid",
    platforms=['instagram', 'twitter', 'website']
)

# Check results
if result['status'] == 'completed':
    print(f"Analyzed {len(result['platforms_analyzed'])} platforms")
    print(f"Found {result['monitoring_data_count']} new posts")
```

## Agent Status

| Agent | Status | SQLAlchemy Removed | API Integration |
|-------|--------|-------------------|-----------------|
| YouTube | ✅ Updated | ✅ Yes | ✅ YouTube Data API |
| Website | ✅ Updated | ✅ Yes | ✅ Crawl4AI |
| Browser | ✅ Updated | ✅ Yes | ✅ Tavily Search |
| Instagram | ✅ Updated | ✅ Yes | ⏳ Ready for API |
| Twitter | ✅ Updated | ✅ Yes | ⏳ Ready for API |

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   ```
   Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set
   ```
   **Solution**: Check your `.env` file

2. **Competitor Not Found**
   ```
   Warning: No competitor found with ID: xxx
   ```
   **Solution**: Verify competitor exists in database

3. **Supabase Connection Issues**
   ```
   Error: Failed to connect to Supabase
   ```
   **Solution**: Check network and credentials

4. **Agent Initialization Errors**
   ```
   Error: Failed to create [Agent] agent
   ```
   **Solution**: Check API keys and dependencies for specific agent

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger('app.services.monitoring').setLevel(logging.DEBUG)
```

## Performance Considerations

- **Connection Pooling**: Supabase handles connection management
- **Rate Limiting**: Respect Supabase rate limits
- **Batch Operations**: Consider batching for large datasets
- **Caching**: Implement caching for frequently accessed data
- **Agent Independence**: Each agent operates independently for better scalability

## Future Enhancements

1. **Real-time Updates**: Leverage Supabase real-time features
2. **Batch Processing**: Optimize for large-scale monitoring
3. **Caching Layer**: Add Redis/Memory caching
4. **Advanced Analytics**: Use Supabase analytics features
5. **API Integration**: Complete Instagram and Twitter API integrations
6. **Agent Scaling**: Scale agents horizontally for large competitor lists

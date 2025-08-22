# Content Planning Agent Supabase Integration Plan

## Overview
This document outlines the plan to migrate the content planning agent from using mock data to real-time data from Supabase, while maintaining the current agent flow and adding user-controlled invocation.

## Current State Analysis

### Existing Architecture
- **Content Planning Service**: Uses mock data from JSON files
- **Competitor Analyzer**: Loads data from `competitors_dataset.json`
- **Dashboard Data**: Hardcoded mock values for analytics
- **Data Flow**: Static file-based data → AI agent analysis → Mock results

### Current Data Sources
- `backend/app/services/content_planning/data/mock_datasets/competitors_dataset.json`
- Hardcoded dashboard metrics in `core_service.py`
- Static competitor analysis results

### Current Limitations
- No real-time competitor data
- Static market insights
- Mock performance metrics
- No user control over agent execution

## Target State

### Desired Architecture
- **Real-time Data**: Live competitor data from Supabase
- **Dynamic Analytics**: Real dashboard metrics from database
- **User Control**: Agent only runs when explicitly requested
- **Scalable**: Database-driven instead of file-based

### Key Benefits
- Live competitor insights and market trends
- Actual engagement metrics and ROI data
- User-controlled agent invocation
- Unified data source across features
- Improved scalability and performance

## Implementation Plan

### Phase 1: Data Source Migration

#### 1.1 Update Competitor Analyzer Tool
**File**: `backend/app/services/content_planning/tools/competitor_analyzer.py`

**Changes Required**:
- Replace `_load_competitor_data()` method with Supabase integration
- Create Supabase client for competitor data fetching
- Map Supabase competitor table fields to existing data structure
- Maintain backward compatibility with existing analysis methods

**Supabase Data Sources**:
- `competitors` table: Company info, industry, platforms
- `monitoring_data` table: Recent competitor posts and engagement
- `monitoring_alerts` table: Competitor activity alerts

#### 1.2 Update Dashboard Data Generation
**File**: `backend/app/services/content_planning/core_service.py`

**Changes Required**:
- Replace hardcoded mock data with real Supabase queries
- Use `user_posts` table for content statistics
- Use `ai_content_suggestions` table for AI-generated content data
- Use `roi_metrics` table for performance metrics

### Phase 2: Agent Invocation Control

#### 2.1 Modify Content Planning Endpoints
**File**: `backend/app/api/v1/endpoints/content_planning.py`

**Changes Required**:
- Add new endpoint for manual content generation trigger
- Update existing endpoints to not auto-run agent
- Add user authentication checks for agent invocation
- Implement conditional agent execution

#### 2.2 Frontend Integration
**Files**: Frontend dashboard components

**Changes Required**:
- Add "Create Content" button to content planning dashboard
- Only show agent results after button click
- Display loading states during agent execution
- Implement user-controlled workflow

### Phase 3: Data Integration Details

#### 3.1 Competitor Data Sources
| Supabase Table | Purpose | Key Fields |
|----------------|---------|------------|
| `competitors` | Company information | name, industry, platforms, social_media_handles |
| `monitoring_data` | Recent competitor posts | content_text, engagement_metrics, hashtags |
| `monitoring_alerts` | Competitor activity | alert_type, priority, message |

#### 3.2 Content Planning Data Sources
| Supabase Table | Purpose | Key Fields |
|----------------|---------|------------|
| `user_posts` | User's planned/published content | content_text, target_platforms, post_status |
| `ai_content_suggestions` | AI-generated recommendations | suggested_content, competitor_analysis |
| `content_generation_prompts` | User's custom prompts | prompt_template, industry_tags |
| `roi_metrics` | Performance data | engagement_metrics, roi_percentage |

#### 3.3 Dashboard Analytics Sources
| Metric | Data Source | Real-time Status |
|--------|-------------|------------------|
| Competitor Count | `competitors` table | ✅ Live |
| Content Gaps | `user_posts` vs competitor analysis | ✅ Dynamic |
| Engagement Metrics | `roi_metrics` table | ✅ Live |
| Hashtag Trends | `monitoring_data` table | ✅ Live |

### Phase 4: Database Schema Updates

#### 4.1 New Tables (If Needed)
```sql
-- Content planning sessions tracking
CREATE TABLE content_planning_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR NOT NULL,
    session_type VARCHAR NOT NULL,
    agent_parameters JSONB,
    execution_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Content calendar for scheduled content
CREATE TABLE content_calendar (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR NOT NULL,
    planned_date DATE NOT NULL,
    content_data JSONB,
    platform VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'planned'
);

-- Long-term content strategy
CREATE TABLE content_strategy (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR NOT NULL,
    strategy_name VARCHAR NOT NULL,
    strategy_data JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

#### 4.2 Existing Table Updates
- Add content planning metadata to `user_posts`
- Link AI suggestions to competitor analysis results
- Enhance `ai_content_suggestions` with execution tracking

### Phase 5: API Endpoint Updates

#### 5.1 New Endpoints
```python
# Manual trigger for content planning agent
POST /content-planning/generate-content
{
    "industry": "technology",
    "platform": "linkedin",
    "content_type": "post",
    "tone": "professional",
    "target_audience": "B2B decision makers"
}

# Real competitor data endpoint
GET /content-planning/competitor-data?industry=technology

# Real dashboard metrics
GET /content-planning/analytics?user_id={user_id}
```

#### 5.2 Updated Endpoints
```python
# Updated dashboard data with real sources
GET /content-planning/dashboard-data?industry=technology

# Real-time competitor analysis
POST /content-planning/analyze-competitors
{
    "industry": "technology",
    "analysis_type": "trend_analysis"
}
```

### Phase 6: Error Handling & Fallbacks

#### 6.1 Graceful Degradation
- Fallback to mock data if Supabase connection fails
- Cache competitor data to reduce API calls
- Handle empty data scenarios gracefully
- Implement retry mechanisms for transient failures

#### 6.2 User Experience
- Clear loading states during data fetching
- Informative error messages for failed operations
- Progress indicators for long-running operations
- Offline mode with cached data

## Technical Implementation Details

### Supabase Client Integration
```python
# Example integration structure
from app.core.supabase_client import get_supabase_client

class CompetitorAnalyzer:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def _fetch_competitor_data(self, industry: str):
        response = await self.supabase.table('competitors').select('*').eq('industry', industry).execute()
        return response.data
```

### Data Mapping Strategy
```python
# Map Supabase data to existing structure
def _map_supabase_to_competitor_data(self, supabase_data):
    mapped_data = {
        "competitors": [],
        "trending_hashtags": {},
        "content_insights": {}
    }
    
    for competitor in supabase_data:
        mapped_competitor = {
            "competitor_id": competitor["id"],
            "company_name": competitor["name"],
            "industry_sector": competitor["industry"],
            "posts": self._fetch_competitor_posts(competitor["id"])
        }
        mapped_data["competitors"].append(mapped_competitor)
    
    return mapped_data
```

### Performance Optimization
- Implement Redis caching for frequently accessed data
- Batch database queries where possible
- Use database indexes for common query patterns
- Implement pagination for large datasets

## Testing Strategy

### Unit Tests
- Test data mapping functions
- Test fallback mechanisms
- Test error handling scenarios
- Test agent invocation control

### Integration Tests
- Test Supabase data fetching
- Test end-to-end content planning flow
- Test dashboard data generation
- Test user authentication and permissions

### Performance Tests
- Measure response times with real data
- Test concurrent user scenarios
- Validate caching effectiveness
- Monitor database query performance

## Deployment Plan

### Phase 1: Development & Testing
- Implement data source migration
- Test with development Supabase instance
- Validate all existing functionality
- Performance testing and optimization

### Phase 2: Staging Deployment
- Deploy to staging environment
- Integration testing with real data
- User acceptance testing
- Performance validation

### Phase 3: Production Rollout
- Gradual rollout to production
- Monitor system performance
- User feedback collection
- Iterative improvements

## Success Criteria

### Functional Requirements
- ✅ Content planning agent uses real Supabase competitor data
- ✅ Dashboard shows live analytics from database
- ✅ Agent only executes on user request
- ✅ All existing functionality preserved
- ✅ Performance maintained or improved

### Non-Functional Requirements
- Response time < 2 seconds for dashboard data
- 99.9% uptime for content planning features
- Graceful handling of database connection issues
- Secure user authentication and data access

### User Experience Metrics
- Reduced time to generate content
- Improved accuracy of competitor insights
- Better user satisfaction with real-time data
- Increased user engagement with planning features

## Risk Assessment & Mitigation

### High Risk Items
| Risk | Impact | Mitigation |
|------|--------|------------|
| Database performance degradation | High | Implement caching, optimize queries |
| Data migration failures | High | Comprehensive testing, rollback plan |
| User experience disruption | Medium | Gradual rollout, fallback options |

### Medium Risk Items
| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limiting | Medium | Implement request throttling |
| Data consistency issues | Medium | Transaction management, validation |
| Cache invalidation complexity | Medium | Clear cache strategy, monitoring |

### Low Risk Items
| Risk | Impact | Mitigation |
|------|--------|------------|
| Minor UI changes | Low | User communication, documentation |
| Temporary data unavailability | Low | Fallback mechanisms, user notifications |

## Timeline & Milestones

### Week 1-2: Foundation
- Set up Supabase client integration
- Create data mapping functions
- Implement basic competitor data fetching

### Week 3-4: Core Implementation
- Update competitor analyzer tool
- Implement dashboard data integration
- Add agent invocation control

### Week 5-6: Testing & Optimization
- Comprehensive testing
- Performance optimization
- Error handling implementation

### Week 7-8: Deployment
- Staging deployment
- Production rollout
- Monitoring and feedback collection

## Conclusion

This integration plan provides a comprehensive roadmap for migrating the content planning agent from mock data to real-time Supabase integration. The phased approach ensures minimal disruption to existing functionality while delivering significant improvements in data accuracy and user experience.

The key success factors are:
1. **Maintaining existing functionality** during the transition
2. **Implementing robust error handling** and fallback mechanisms
3. **Ensuring performance** with real-time data
4. **Providing user control** over agent execution
5. **Comprehensive testing** at each phase

By following this plan, we will achieve a more robust, scalable, and user-friendly content planning system that leverages real-time data for better decision-making and content optimization.

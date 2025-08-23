# ROI Report Generator

## Overview

The ROI Report Generator is an AI-powered feature that automatically generates comprehensive marketing ROI reports using Google Gemini Pro. It analyzes data from the `roi_metrics` table for the previous and current month, processes it by platform, and generates actionable insights and recommendations.

## Features

- **AI-Powered Analysis**: Uses Google Gemini Pro for intelligent report generation
- **Comprehensive Coverage**: Analyzes data across all platforms and metrics
- **Month-over-Month Comparison**: Compares current month performance with previous month
- **Structured Reports**: Generates reports with clear sections:
  - Executive Summary
  - Performance Overview
  - Platform Performance Analysis
  - Key Insights
  - Strategic Recommendations
  - Action Items
- **Downloadable Reports**: Export reports as text files
- **Real-time Data**: Uses live data from Supabase `roi_metrics` table

## Setup Instructions

### 1. Environment Configuration

Add the following environment variable to your `.env` file:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key and add it to your environment variables

### 3. Backend Dependencies

The required dependencies are already included in `requirements.txt`:
- `google-genai==1.29.0`

### 4. Database Requirements

Ensure your `roi_metrics` table has the following structure (already implemented):

```sql
CREATE TABLE IF NOT EXISTS roi_metrics (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    campaign_id INTEGER REFERENCES campaign_with_user_id(id),
    post_id VARCHAR(255),
    content_type VARCHAR(50),
    content_category VARCHAR(100),
    views INTEGER DEFAULT 1,
    likes INTEGER DEFAULT 1,
    comments INTEGER DEFAULT 1,
    shares INTEGER DEFAULT 1,
    saves INTEGER DEFAULT 1,
    clicks INTEGER DEFAULT 1,
    ad_spend DECIMAL(10,2) DEFAULT 0.00,
    revenue_generated DECIMAL(10,2) DEFAULT 0.00,
    cost_per_click DECIMAL(8,2) DEFAULT 0.00,
    cost_per_impression DECIMAL(8,4) DEFAULT 0.00,
    roi_percentage DECIMAL(8,2) DEFAULT 0.00,
    roas_ratio DECIMAL(8,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    posted_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Usage

### 1. From ROI Dashboard

1. Navigate to the ROI Dashboard (`/dashboard/roi`)
2. Click the "Generate Report" button in the top-right corner
3. The report generator will appear below the metrics overview
4. Click "Generate Report" to create an AI-powered analysis
5. View the report in the structured tabs
6. Download the report using the "Download" button

### 2. From Dedicated Reports Page

1. Navigate to the dedicated reports page (`/dashboard/roi/reports`)
2. Click "Generate Report" to start the analysis
3. View and interact with the comprehensive report interface

### 3. API Endpoint

You can also generate reports programmatically using the API:

```bash
POST /api/v1/roi/generate-report?user_id=your_user_id
```

## Technical Implementation

### Backend Architecture

#### 1. Data Processing Pipeline

```python
# 1. Fetch monthly data
current_month_data = await _fetch_monthly_roi_data(current_month_start, now)
previous_month_data = await _fetch_monthly_roi_data(previous_month_start, previous_month_end)

# 2. Summarize by platform
current_summary = _summarize_data_by_platform(current_month_data)
previous_summary = _summarize_data_by_platform(previous_month_data)

# 3. Calculate month-over-month changes
mom_changes = _calculate_month_over_month_changes(current_summary, previous_summary)

# 4. Generate AI report
prompt = _create_report_prompt(report_data)
response = model.generate_content(prompt)
```

#### 2. Data Aggregation

The system aggregates data by platform and calculates:

- **Revenue Metrics**: Total revenue, revenue per platform
- **Cost Metrics**: Total ad spend, cost per platform
- **Engagement Metrics**: Views, likes, comments, shares, clicks
- **Performance Metrics**: ROI, ROAS, engagement rate, CTR
- **Content Analysis**: Content types and categories distribution

#### 3. AI Prompt Engineering

The system creates comprehensive prompts for Gemini that include:

- Structured data from both months
- Month-over-month comparison data
- Platform-specific performance metrics
- Content analysis data

### Frontend Components

#### 1. ReportGenerator Component

Located at: `frontend/components/roi/report-generator.tsx`

Features:
- Report generation interface
- Loading states and error handling
- Structured report display with tabs
- Download functionality
- Responsive design

#### 2. API Integration

Located at: `frontend/lib/api-client.ts`

```typescript
export const roiApi = {
  // ... other methods
  generateReport: (userId: string) => {
    const url = new URL(`${API_BASE}/roi/generate-report`)
    url.searchParams.set('user_id', userId)
    return fetch(url.toString(), { 
      method: 'POST',
      cache: 'no-store' 
    }).then(res => {
      if (!res.ok) throw new Error(`POST /roi/generate-report failed: ${res.status}`)
      return res.json()
    })
  },
}
```

## Report Structure

### 1. Executive Summary
- High-level performance overview
- Key achievements and highlights
- Overall ROI performance summary

### 2. Performance Overview
- Total revenue, spend, and profit analysis
- Overall ROI and ROAS metrics
- Month-over-month performance comparison

### 3. Platform Performance Analysis
- Platform-specific breakdowns
- Revenue and spend by platform
- ROI and engagement metrics per platform
- Content type and category analysis

### 4. Key Insights
- Top performing platforms
- Areas of concern
- Notable trends and patterns
- Content performance insights

### 5. Strategic Recommendations
- Platform-specific optimization suggestions
- Budget allocation recommendations
- Content strategy suggestions
- Performance improvement strategies

### 6. Action Items
- Priority actions for next month
- Specific metrics to focus on
- Testing opportunities
- Implementation timeline

## Data Processing Details

### Platform Aggregation

For each platform, the system calculates:

```python
platform_summary = {
    "total_views": sum(views),
    "total_engagement": sum(likes + comments + shares),
    "total_revenue": sum(revenue_generated),
    "total_spend": sum(ad_spend),
    "avg_roi": average(roi_percentage),
    "engagement_rate": (total_engagement / total_views) * 100,
    "click_through_rate": (total_clicks / total_views) * 100,
    "profit": total_revenue - total_spend,
    "profit_margin": (profit / total_revenue) * 100,
    "roas": total_revenue / total_spend
}
```

### Month-over-Month Calculations

```python
def _calculate_percentage_change(previous: float, current: float) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - previous) / previous) * 100
```

## Error Handling

### Common Issues and Solutions

1. **Gemini API Key Not Configured**
   - Error: "Gemini API key not configured"
   - Solution: Add `GEMINI_API_KEY` to environment variables

2. **No Data Available**
   - Error: "Failed to fetch ROI metrics data"
   - Solution: Ensure `roi_metrics` table has data for the specified time period

3. **API Rate Limits**
   - Error: Gemini API rate limit exceeded
   - Solution: Implement retry logic or upgrade API plan

4. **Network Issues**
   - Error: Connection timeout
   - Solution: Check network connectivity and API endpoint availability

## Performance Considerations

### 1. Caching
- Report generation is not cached to ensure fresh data
- Consider implementing caching for frequently requested reports

### 2. Data Volume
- Large datasets may impact generation time
- Consider implementing pagination for very large datasets

### 3. API Costs
- Gemini API calls incur costs
- Monitor usage and implement rate limiting if needed

## Security Considerations

### 1. API Key Security
- Store Gemini API key in environment variables
- Never expose API keys in client-side code

### 2. Data Privacy
- Ensure user data is properly isolated
- Implement proper authentication and authorization

### 3. Input Validation
- Validate user input before processing
- Sanitize data before sending to AI APIs

## Future Enhancements

### 1. Report Templates
- Customizable report templates
- Industry-specific analysis
- Brand-specific recommendations

### 2. Advanced Analytics
- Predictive analytics
- Trend forecasting
- Anomaly detection

### 3. Integration Features
- Email report delivery
- Scheduled report generation
- Integration with external tools

### 4. Enhanced AI Features
- Multi-language support
- Custom AI models
- Advanced prompt engineering

## Troubleshooting

### Debug Mode

Enable debug logging by setting:

```bash
LOG_LEVEL=DEBUG
```

### Common Debug Steps

1. **Check API Key**: Verify Gemini API key is correctly set
2. **Verify Data**: Ensure `roi_metrics` table has data
3. **Check Network**: Verify API endpoints are accessible
4. **Review Logs**: Check application logs for detailed error messages

### Support

For technical support or feature requests, please refer to the project documentation or create an issue in the repository.

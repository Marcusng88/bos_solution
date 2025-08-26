# Enhanced PDF Conversion Agent with YouTube and Instagram Data Integration

## Overview

The Enhanced PDF Conversion Agent has been upgraded to include comprehensive YouTube and Instagram data from Supabase in the generated ROI reports. This enhancement provides a complete view of social media performance across all platforms.

## Features

### 🎯 Enhanced Data Integration
- **YouTube Analytics**: Video performance, channel metrics, and ROI data
- **Instagram Monitoring**: Content monitoring, engagement metrics, and social account data
- **Cross-Platform ROI**: Comprehensive analysis across Facebook, Instagram, YouTube, and other platforms
- **Real-time Data**: Live data fetching from Supabase database

### 📊 Report Sections
1. **Executive Summary**: Overview of all platform performance
2. **Platform Performance**: Revenue, cost, and ROI breakdown by platform
3. **YouTube Performance Analytics**:
   - Channel overview with subscriber counts and revenue estimates
   - Recent video performance with engagement metrics
   - YouTube ROI metrics and trends
4. **Instagram Performance Analytics**:
   - Instagram ROI metrics and performance data
   - Connected Instagram accounts
   - Content monitoring and engagement data
5. **Campaign Details**: Individual campaign performance across platforms
6. **Summary Metrics**: Consolidated performance indicators

## Database Integration

### YouTube Data Sources
- `videos` table: Video performance metrics, views, likes, comments
- `channels` table: Channel information, subscriber counts, revenue estimates
- `roi_metrics` table: YouTube-specific ROI performance data

### Instagram Data Sources
- `monitoring_data` table: Instagram content monitoring and engagement
- `roi_metrics` table: Instagram-specific ROI performance data
- `social_media_accounts` table: Connected Instagram accounts

### ROI Data Sources
- `roi_metrics` table: Platform-specific ROI metrics
- `campaign_with_user_id` table: Campaign performance data
- `platform_metrics` table: Platform-specific performance indicators

## API Endpoints

### Enhanced ROI Report Generation
```http
POST /pdf/enhanced-roi-report-to-pdf
Content-Type: application/json

{
  "user_id": "user_clerk_id",
  "report_data": {
    "platforms": {
      "Facebook": {
        "total_revenue": 12500.50,
        "total_cost": 5000.00,
        "total_roi": 7500.50
      },
      "Instagram": {
        "total_revenue": 21000.75,
        "total_cost": 8000.00,
        "total_roi": 13000.75
      },
      "YouTube": {
        "total_revenue": 34500.25,
        "total_cost": 12000.00,
        "total_roi": 22500.25
      }
    },
    "campaigns": [
      {
        "date": "2024-01-15",
        "platform": "Facebook",
        "campaign_name": "Winter Sale Campaign",
        "revenue": 1250.00,
        "cost": 500.00
      }
    ]
  },
  "filename": "enhanced_roi_report.pdf"
}
```

### Standard PDF Endpoints (Still Available)
- `POST /pdf/convert-html-to-pdf` - Convert HTML to PDF
- `POST /pdf/convert-json-to-pdf` - Convert JSON to PDF using AI
- `POST /pdf/roi-report-to-pdf` - Basic ROI report generation
- `GET /pdf/health` - Health check endpoint

## Usage Examples

### Python Usage
```python
from app.services.pdf_conversion_agent import create_enhanced_roi_pdf_async

# Generate enhanced ROI PDF with YouTube and Instagram data
roi_data = {
    "platforms": {
        "Facebook": {"total_revenue": 12500.50, "total_cost": 5000.00},
        "Instagram": {"total_revenue": 21000.75, "total_cost": 8000.00},
        "YouTube": {"total_revenue": 34500.25, "total_cost": 12000.00}
    },
    "campaigns": [...]
}

pdf_bytes, filename = await create_enhanced_roi_pdf_async(
    user_id="user_clerk_id",
    roi_data=roi_data,
    output_path="enhanced_roi_report.pdf"
)
```

### JavaScript/TypeScript Usage
```javascript
// Generate enhanced ROI PDF
const response = await fetch('/pdf/enhanced-roi-report-to-pdf', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: 'user_clerk_id',
    report_data: {
      platforms: {
        Facebook: { total_revenue: 12500.50, total_cost: 5000.00 },
        Instagram: { total_revenue: 21000.75, total_cost: 8000.00 },
        YouTube: { total_revenue: 34500.25, total_cost: 12000.00 }
      },
      campaigns: [...]
    },
    filename: 'enhanced_roi_report.pdf'
  })
});

const pdfBlob = await response.blob();
const url = window.URL.createObjectURL(pdfBlob);
const a = document.createElement('a');
a.href = url;
a.download = 'enhanced_roi_report.pdf';
a.click();
```

## Data Fetching Methods

### YouTube Data Fetching
```python
# Fetch YouTube data for a user
youtube_data = await pdf_agent.fetch_youtube_data(user_id)

# Returns:
{
  "videos": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Video Title",
      "views": 1000,
      "likes": 50,
      "comments": 10,
      "engagement_rate": 0.06,
      "roi_score": 85.5
    }
  ],
  "channels": [
    {
      "channel_id": "UC...",
      "channel_title": "Channel Name",
      "total_subscribers": 1000,
      "total_videos": 50,
      "estimated_monthly_revenue": 500.00
    }
  ],
  "roi_metrics": [
    {
      "update_timestamp": "2024-01-15T10:00:00Z",
      "views": 5000,
      "revenue_generated": 250.00,
      "ad_spend": 100.00,
      "roi_percentage": 150.0
    }
  ]
}
```

### Instagram Data Fetching
```python
# Fetch Instagram data for a user
instagram_data = await pdf_agent.fetch_instagram_data(user_id)

# Returns:
{
  "monitoring_data": [
    {
      "author_username": "@username",
      "post_type": "image",
      "engagement_metrics": {"like_count": 100, "comment_count": 20},
      "sentiment_score": 0.8,
      "detected_at": "2024-01-15T10:00:00Z"
    }
  ],
  "roi_metrics": [
    {
      "update_timestamp": "2024-01-15T10:00:00Z",
      "views": 2000,
      "likes": 150,
      "comments": 30,
      "revenue_generated": 300.00,
      "ad_spend": 120.00,
      "roi_percentage": 150.0
    }
  ],
  "social_accounts": [
    {
      "account_name": "Brand Account",
      "username": "@brand.ig",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## Configuration

### Environment Variables
```bash
# Required for Supabase integration
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Optional for AI-powered features
GOOGLE_API_KEY=your_gemini_api_key
```

### Dependencies
```bash
# Core dependencies
pip install xhtml2pdf httpx python-dotenv

# Optional AI dependencies
pip install google-generativeai langchain-google-genai
```

## Testing

### Run Enhanced PDF Tests
```bash
# Test the enhanced PDF conversion agent
python test_enhanced_pdf_agent.py
```

### Test Output Files
- `test_enhanced_roi_report.pdf` - Basic HTML to PDF conversion
- `enhanced_roi_report.pdf` - Enhanced ROI with platform data
- `enhanced_sync_test.pdf` - Enhanced synchronous conversion
- `ai_enhanced_roi_report.pdf` - AI-powered generation (if Gemini available)

## Error Handling

### Common Issues
1. **Supabase Connection**: Ensure `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
2. **Data Availability**: YouTube and Instagram data will be empty if no data exists in the database
3. **User ID**: Ensure the user ID exists in the database
4. **Permissions**: Ensure the service role key has read access to all required tables

### Error Responses
```json
{
  "detail": "Enhanced ROI PDF conversion failed: Supabase not available"
}
```

## Performance Considerations

### Data Fetching Optimization
- YouTube and Instagram data is fetched in parallel
- Data is limited to recent records (last 50-100 entries)
- Caching can be implemented for frequently accessed data

### PDF Generation
- Large datasets are paginated in the PDF
- Images and media are optimized for PDF output
- Font sizes are adjusted for readability

## Future Enhancements

### Planned Features
- **Real-time Data Updates**: Live data fetching during report generation
- **Custom Templates**: User-defined PDF templates
- **Scheduled Reports**: Automated report generation
- **Data Export**: CSV/Excel export options
- **Interactive Charts**: Embeddable charts in PDFs

### Integration Opportunities
- **Email Integration**: Automated report delivery
- **Cloud Storage**: Direct upload to Google Drive, Dropbox
- **Analytics Dashboard**: Web-based report viewer
- **Mobile App**: PDF viewing on mobile devices

## Support

For issues or questions regarding the Enhanced PDF Conversion Agent:

1. Check the test output for specific error messages
2. Verify Supabase credentials and table structure
3. Ensure all required dependencies are installed
4. Review the database schema for required tables

## Changelog

### Version 2.0.0 (Enhanced)
- ✅ Added YouTube data integration
- ✅ Added Instagram data integration
- ✅ Enhanced PDF templates with platform-specific sections
- ✅ New `/enhanced-roi-report-to-pdf` endpoint
- ✅ Improved error handling and logging
- ✅ Added comprehensive testing suite

### Version 1.0.0 (Original)
- ✅ Basic HTML to PDF conversion
- ✅ Simple ROI report generation
- ✅ AI-powered JSON to PDF conversion
- ✅ Basic PDF endpoints

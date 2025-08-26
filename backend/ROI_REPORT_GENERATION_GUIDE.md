# ROI Report Generation System

## Overview

The ROI Report Generation System creates professional reports in multiple formats from your marketing campaign data. The system generates reports in **Text (.txt)**, **HTML (.html)**, and **PDF (.pdf)** formats, each optimized for different use cases.

## Features

### 📄 Multiple Output Formats

1. **Text Report (.txt)**
   - Simple, readable format
   - Easy to copy/paste
   - Works in any text editor
   - Small file size
   - Perfect for quick reading

2. **HTML Report (.html)**
   - Professional, modern design
   - Interactive elements and hover effects
   - Responsive layout
   - Print-friendly styling
   - Can be opened in any web browser
   - Beautiful visual presentation

3. **PDF Report (.pdf)**
   - Professional document format
   - Consistent appearance across devices
   - Easy to share and archive
   - Print-ready
   - Professional tables and formatting

4. **JSON Data (.json)**
   - Raw data for further analysis
   - Machine-readable format
   - Can be imported into other tools
   - Contains all metrics and calculations

### 🎨 Professional Design

- **Modern UI**: Clean, professional design with gradients and shadows
- **Responsive Layout**: Adapts to different screen sizes
- **Color-coded Metrics**: ROI status indicators with appropriate colors
- **Platform Icons**: Visual indicators for different social media platforms
- **Interactive Elements**: Hover effects and visual feedback
- **Print Optimization**: CSS media queries for print-friendly output

### 📊 Comprehensive Analytics

- **Financial Metrics**: Revenue, spend, profit, ROI percentage
- **Performance Indicators**: ROAS, engagement rates, CTR
- **Platform Breakdown**: Detailed analysis by social media platform
- **Trend Analysis**: Performance over time
- **AI-Generated Insights**: Intelligent analysis and recommendations

## Installation

### Prerequisites

```bash
# Install required packages
pip install -r requirements.txt
```

### Required Dependencies

- `google-generativeai` - For AI-powered report generation
- `weasyprint` - For HTML to PDF conversion (optional)
- `reportlab` - For PDF generation fallback
- `supabase` - For database connectivity

## Usage

### Basic Report Generation

```bash
# Generate report in all formats
python generate_roi_report.py
```

### Demo Script

```bash
# Run the demo to see all formats
python demo_report_formats.py
```

### Programmatic Usage

```python
import asyncio
from generate_roi_report import generate_roi_report

# Generate report
success = await generate_roi_report()
if success:
    print("Report generated successfully!")
```

## Generated Files

Each report generation creates the following files:

```
roi_report_YYYY-MM-DD_HH-MM-SS.txt    # Text report
roi_report_YYYY-MM-DD_HH-MM-SS.html   # HTML report  
roi_report_YYYY-MM-DD_HH-MM-SS.pdf    # PDF report
roi_data_YYYY-MM-DD_HH-MM-SS.json     # Raw data
```

## Report Content

### Executive Summary
- AI-generated analysis of overall performance
- Key insights and recommendations
- Performance highlights and areas for improvement

### Key Metrics Dashboard
- **Total Revenue**: Overall revenue generated
- **Total Spend**: Total advertising spend
- **Total Profit**: Net profit/loss
- **ROI Percentage**: Return on investment percentage
- **ROI Status**: Excellent/Good/Moderate/Poor indicators

### Platform Performance Breakdown
- Detailed analysis by social media platform
- Platform-specific metrics
- Performance comparisons
- Platform icons and visual indicators

### Financial Analysis
- Revenue trends
- Spend analysis
- Profit margins
- Cost per acquisition metrics

## Design Features

### HTML Report Design

- **Header**: Gradient background with professional typography
- **Metrics Grid**: Card-based layout with hover effects
- **Color Coding**: 
  - Excellent ROI: Green (#059669)
  - Good ROI: Light Green (#10b981)
  - Moderate ROI: Orange (#f59e0b)
  - Poor ROI: Red (#dc2626)
- **Platform Icons**: 
  - YouTube: 📺
  - Instagram: 📷
  - Facebook: 📘
  - Twitter: 🐦
  - TikTok: 🎵
  - LinkedIn: 💼
  - Google: 🔍
  - Other: 🌐

### PDF Report Design

- **Professional Layout**: Clean, business-ready formatting
- **Tables**: Structured data presentation
- **Typography**: Professional fonts and spacing
- **Page Breaks**: Optimized for printing
- **Headers/Footers**: Page numbers and document info

## Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Database (if using Supabase)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

### Customization

You can customize the report generation by modifying:

1. **HTML Template**: Edit `create_html_template()` function
2. **PDF Styling**: Modify ReportLab styles in the PDF generation section
3. **Metrics Calculation**: Adjust ROI calculations in the data processing section
4. **Platform Icons**: Update the platform icon mapping

## Troubleshooting

### WeasyPrint Issues (Windows)

If you encounter WeasyPrint installation issues on Windows:

1. **Use ReportLab Fallback**: The system automatically falls back to ReportLab
2. **Install GTK**: Follow WeasyPrint installation guide for Windows
3. **Use WSL**: Run on Windows Subsystem for Linux

### PDF Generation Issues

```bash
# Install ReportLab as fallback
pip install reportlab==4.0.4

# Check if PDF generation works
python generate_roi_report.py
```

### Database Connection Issues

```bash
# Check environment variables
python -c "import os; print('GEMINI_API_KEY:', bool(os.getenv('GEMINI_API_KEY')))"

# Test database connection
python test_roi_data_retrieval.py
```

## Best Practices

### For HTML Reports
- Open in modern browsers (Chrome, Firefox, Safari, Edge)
- Use for screen viewing and presentations
- Print using browser print function for best results

### For PDF Reports
- Use for official documents and sharing
- Print directly from PDF viewer
- Archive for long-term storage

### For Text Reports
- Use for quick reference
- Copy/paste into other documents
- Share via email or messaging

### For JSON Data
- Import into data analysis tools
- Use for custom reporting
- Integrate with other systems

## API Integration

The report generation can be integrated into your application:

```python
from app.api.v1.endpoints.roi import generate_roi_report_endpoint

# Generate report via API
response = await generate_roi_report_endpoint()
```

## Performance

- **Generation Time**: ~5-10 seconds for full report
- **File Sizes**: 
  - Text: ~5KB
  - HTML: ~18KB
  - PDF: ~8KB
  - JSON: ~19KB
- **Memory Usage**: Minimal, optimized for efficiency

## Future Enhancements

- [ ] Email integration for automatic report delivery
- [ ] Scheduled report generation
- [ ] Custom report templates
- [ ] Interactive charts and graphs
- [ ] Multi-language support
- [ ] Advanced filtering options
- [ ] Report comparison features

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the generated error logs
3. Test with the demo script
4. Verify environment variables are set correctly

---

**Generated by BOS Solution ROI Analytics System**



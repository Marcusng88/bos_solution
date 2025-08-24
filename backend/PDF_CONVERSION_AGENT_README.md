# PDF Conversion Agent

A comprehensive PDF conversion agent that uses `xhtml2pdf` to convert HTML reports to professional PDF format. This agent is specifically designed for ROI reports and integrates seamlessly with the existing BOS Solution ROI system.

## Features

- **HTML to PDF Conversion**: Convert any HTML content to PDF using xhtml2pdf
- **AI-Powered Generation**: Use Google Gemini to convert JSON data to HTML, then to PDF
- **ROI-Specific Templates**: Pre-built templates optimized for ROI reports
- **Professional Styling**: CSS optimized for PDF output with proper table handling
- **Multiple Output Options**: Download, preview, or save PDFs locally
- **Async/Sync Support**: Both asynchronous and synchronous conversion methods
- **Error Handling**: Comprehensive error handling and logging

## Installation

### 1. Install Dependencies

The PDF conversion agent requires `xhtml2pdf` which has been added to the requirements:

```bash
pip install xhtml2pdf==0.2.13
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Ensure you have the following environment variables set (optional for AI features):

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage

### Basic HTML to PDF Conversion

```python
from app.services.pdf_conversion_agent import convert_html_to_pdf_async

# Simple HTML content
html_content = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: Arial; font-size: 12pt; }
</style>
</head>
<body>
<h1>My Report</h1>
<p>This is a test report.</p>
</body>
</html>
"""

# Convert to PDF
pdf_bytes, filename = await convert_html_to_pdf_async(html_content, "my_report.pdf")
```

### AI-Powered JSON to PDF Conversion

```python
from app.services.pdf_conversion_agent import generate_pdf_from_json_async

# JSON data
json_data = {
    "report_title": "ROI Performance Report",
    "summary": "Monthly performance summary",
    "metrics": {
        "total_revenue": 50000,
        "total_cost": 20000,
        "roi": 30000
    }
}

# Convert JSON to PDF using AI
pdf_bytes, filename = await generate_pdf_from_json_async(json_data, "roi_report.pdf")
```

### ROI-Specific PDF Generation

```python
from app.services.pdf_conversion_agent import pdf_agent

# ROI data structure
roi_data = {
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
        }
    },
    "campaigns": [
        {
            "date": "2024-01-15",
            "platform": "Facebook",
            "campaign_name": "Winter Sale",
            "revenue": 1250.00,
            "cost": 500.00
        }
    ]
}

# Generate ROI PDF
pdf_bytes, filename = await pdf_agent.create_simple_roi_pdf(roi_data, "roi_report.pdf")
```

## API Endpoints

The PDF conversion agent provides several REST API endpoints:

### 1. Convert HTML to PDF
```http
POST /api/pdf/convert-html-to-pdf
Content-Type: application/json

{
  "html_content": "<html>...</html>",
  "filename": "optional_filename.pdf"
}
```

### 2. Convert JSON to PDF (AI-powered)
```http
POST /api/pdf/convert-json-to-pdf
Content-Type: application/json

{
  "json_data": {
    "report_title": "My Report",
    "data": "..."
  },
  "filename": "optional_filename.pdf"
}
```

### 3. ROI Report to PDF
```http
POST /api/pdf/roi-report-to-pdf
Content-Type: application/json

{
  "report_data": {
    "platforms": {...},
    "campaigns": [...]
  },
  "filename": "optional_filename.pdf"
}
```

### 4. Upload HTML File and Convert
```http
POST /api/pdf/upload-html-and-convert
Content-Type: multipart/form-data

html_file: [file upload]
filename: "optional_filename.pdf"
```

### 5. Health Check
```http
GET /api/pdf/health
```

## Frontend Integration

### React Components

The PDF conversion agent includes React components for easy frontend integration:

```tsx
import { PDFDownloadButton, PDFPreviewButton } from "@/components/roi/pdf-download-button";

// Download PDF
<PDFDownloadButton
  htmlContent={generatedHtml}
  reportType="html"
  filename="roi_report.pdf"
/>

// Preview PDF
<PDFPreviewButton
  jsonData={roiData}
  reportType="roi"
  filename="roi_report.pdf"
/>
```

### Usage in ROI Dashboard

```tsx
import { PDFDownloadButton } from "@/components/roi/pdf-download-button";

export function ROIDashboard() {
  const [reportData, setReportData] = useState(null);
  const [generatedHtml, setGeneratedHtml] = useState("");

  return (
    <div>
      {/* Your ROI dashboard content */}
      
      {/* PDF Download Button */}
      <PDFDownloadButton
        htmlContent={generatedHtml}
        jsonData={reportData}
        reportType="roi"
        filename={`roi_report_${new Date().toISOString().slice(0, 10)}.pdf`}
        className="mt-4"
      />
    </div>
  );
}
```

## CSS Guidelines for PDF

The PDF conversion agent uses xhtml2pdf, which has specific CSS requirements:

### Supported CSS Properties

```css
/* Typography */
font-family: "Arial", "Helvetica", sans-serif;
font-size: 10pt; /* Use pt for PDF, not px */
font-weight: normal | bold;
line-height: 1.2;

/* Layout */
width: 100pt; /* pt, px only - NO %, vw, vh */
height: 50pt;
padding: 5pt;
margin: 5pt;

/* Tables */
table-layout: fixed; /* Essential for tables */
border-collapse: collapse;
word-wrap: break-word;

/* PDF-specific */
page-break-before: auto | always;
page-break-after: auto | always;
page-break-inside: avoid;
```

### Table Best Practices

```css
.data-table {
    width: 500pt;
    table-layout: fixed;
    border-collapse: collapse;
    margin: 5pt 0;
    font-size: 8pt;
}

.data-table th {
    background-color: #f0f0f0;
    padding: 3pt;
    border: 1pt solid #000;
    font-weight: bold;
    text-align: center;
}

.data-table td {
    padding: 3pt;
    border: 1pt solid #ccc;
    word-wrap: break-word;
    vertical-align: top;
}
```

## Testing

Run the test script to verify the PDF conversion agent:

```bash
python test_pdf_conversion_agent.py
```

This will:
- Test basic HTML to PDF conversion
- Test simple ROI PDF generation
- Test AI-powered PDF generation (if Gemini API key is available)
- Test synchronous conversion methods
- Generate sample PDF files for verification

## Error Handling

The PDF conversion agent includes comprehensive error handling:

```python
try:
    pdf_bytes, filename = await convert_html_to_pdf_async(html_content)
except ImportError as e:
    print("xhtml2pdf not installed")
except Exception as e:
    print(f"PDF conversion failed: {e}")
```

## Performance Considerations

- **Memory Usage**: Large HTML files may consume significant memory during conversion
- **Processing Time**: Complex HTML with many tables may take longer to process
- **File Size**: Generated PDFs are typically smaller than the original HTML
- **Caching**: Consider caching generated PDFs for frequently accessed reports

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure xhtml2pdf is installed
   ```bash
   pip install xhtml2pdf==0.2.13
   ```

2. **Table Overflow**: Use `table-layout: fixed` and set explicit column widths
   ```css
   table { table-layout: fixed; width: 500pt; }
   ```

3. **Font Issues**: Use web-safe fonts or ensure fonts are available
   ```css
   font-family: "Arial", "Helvetica", sans-serif;
   ```

4. **Page Breaks**: Use PDF-specific page break properties
   ```css
   .page-break { page-break-before: always; }
   ```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Existing ROI System

The PDF conversion agent integrates seamlessly with the existing ROI system:

1. **Data Flow**: ROI data → HTML generation → PDF conversion
2. **API Integration**: Uses existing FastAPI structure
3. **Frontend Integration**: React components for easy UI integration
4. **Error Handling**: Consistent with existing error handling patterns

## Future Enhancements

- [ ] Support for charts and graphs in PDF
- [ ] Custom PDF templates
- [ ] Batch PDF generation
- [ ] PDF compression options
- [ ] Watermark support
- [ ] Digital signature support

## Support

For issues or questions about the PDF conversion agent:

1. Check the troubleshooting section above
2. Run the test script to verify functionality
3. Check the logs for detailed error messages
4. Ensure all dependencies are properly installed

## License

This PDF conversion agent is part of the BOS Solution project and follows the same licensing terms.

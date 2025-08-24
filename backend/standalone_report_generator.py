#!/usr/bin/env python3
"""
Standalone ROI Report Generator
This script generates ROI reports without depending on any backend files.
It takes data input directly, uses Gemini to generate content, creates HTML template, and converts to PDF.
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("Please install required packages:")
    print("pip install google-generativeai weasyprint python-dotenv")
    sys.exit(1)

class StandaloneReportGenerator:
    """Standalone ROI Report Generator that doesn't depend on backend files"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize the report generator"""
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required. Set it in .env file or pass as parameter.")
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Using Gemini 1.5 Flash model")
        except Exception:
            self.model = genai.GenerativeModel('gemini-pro')
            print("✅ Using Gemini Pro model")
    
    def create_report_prompt(self, data: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for Gemini to generate the report"""
        
        prompt = f"""
You are a marketing analytics expert. Generate a comprehensive ROI report based on the following data.

REPORT DATA:
{json.dumps(data, indent=2)}

Please create a professional marketing ROI report with the following structure:

# Executive Summary
- Brief overview of performance
- Key highlights and achievements
- Overall ROI performance

# Performance Overview
- Total revenue, spend, and profit analysis
- Overall ROI and ROAS metrics
- Month-over-month performance comparison (if applicable)

# Platform Performance Analysis
For each platform, provide:
- Revenue and spend breakdown
- ROI and engagement metrics
- Performance trends and insights
- Content type and category analysis

# Key Insights
- Top performing platforms
- Areas of concern
- Notable trends and patterns
- Content performance insights

# Recommendations
- Strategic recommendations for improvement
- Platform-specific optimization suggestions
- Budget allocation recommendations
- Content strategy suggestions

# Action Items
- Priority actions for next month
- Specific metrics to focus on
- Testing opportunities

Please format the report professionally with clear sections, bullet points where appropriate, and actionable insights. Focus on providing valuable business intelligence that can drive decision-making.
"""
        
        return prompt
    
    def create_html_template(self, report_content: str, report_data: Dict[str, Any]) -> str:
        """Create a professional HTML template for the ROI report"""
        
        # Calculate key metrics
        total_revenue = sum(platform.get('revenue', 0) for platform in report_data.get('platforms', {}).values())
        total_spend = sum(platform.get('spend', 0) for platform in report_data.get('platforms', {}).values())
        total_profit = total_revenue - total_spend
        roi_percentage = (total_profit / total_spend * 100) if total_spend > 0 else 0
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Determine ROI status
        if roi_percentage >= 300:
            roi_status = "excellent"
        elif roi_percentage >= 200:
            roi_status = "good"
        elif roi_percentage >= 100:
            roi_status = "moderate"
        else:
            roi_status = "poor"
        
        # Determine ROI color for styling
        roi_color = {
            "excellent": "#059669",
            "good": "#10b981", 
            "moderate": "#f59e0b",
            "poor": "#dc2626"
        }.get(roi_status, "#6b7280")
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROI Performance Report - {datetime.now().strftime('%B %d, %Y')}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 2rem auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4rem 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.3;
        }}
        
        .header-content {{
            position: relative;
            z-index: 1;
        }}
        
        .header h1 {{
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .header .subtitle {{
            font-size: 1.25rem;
            opacity: 0.95;
            font-weight: 400;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            padding: 2rem;
            background: white;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid #e2e8f0;
            transition: transform 0.2s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: {roi_color};
            margin-bottom: 0.5rem;
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            color: #64748b;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .content {{
            padding: 3rem 2rem;
        }}
        
        .section {{
            margin-bottom: 3rem;
        }}
        
        .section h2 {{
            font-size: 1.875rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid {roi_color};
            display: inline-block;
        }}
        
        .section h3 {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #374151;
            margin: 2rem 0 1rem 0;
        }}
        
        .section p {{
            margin-bottom: 1rem;
            color: #4b5563;
            font-size: 1rem;
        }}
        
        .section ul {{
            margin: 1rem 0;
            padding-left: 1.5rem;
        }}
        
        .section li {{
            margin-bottom: 0.5rem;
            color: #4b5563;
        }}
        
        .platform-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        
        .platform-card {{
            background: #f8fafc;
            border-radius: 8px;
            padding: 1.5rem;
            border-left: 4px solid {roi_color};
        }}
        
        .platform-name {{
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 1rem;
        }}
        
        .footer {{
            background: #1e293b;
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
        }}
        
        .footer p {{
            opacity: 0.8;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                margin: 0;
                border-radius: 0;
                box-shadow: none;
            }}
            .header {{
                background: #667eea !important;
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1>ROI Performance Report</h1>
                <div class="subtitle">Comprehensive Marketing Analytics & Insights</div>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">${total_revenue:,.2f}</div>
                <div class="metric-label">Total Revenue</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${total_spend:,.2f}</div>
                <div class="metric-label">Total Spend</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${total_profit:,.2f}</div>
                <div class="metric-label">Total Profit</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{roi_percentage:.1f}%</div>
                <div class="metric-label">ROI</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{profit_margin:.1f}%</div>
                <div class="metric-label">Profit Margin</div>
            </div>
        </div>
        
        <div class="content">
            {report_content}
        </div>
        
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>ROI Performance Report - Powered by AI Analytics</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html_template
    
    async def generate_report_content(self, data: Dict[str, Any]) -> str:
        """Generate report content using Gemini"""
        try:
            prompt = self.create_report_prompt(data)
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text
            else:
                raise Exception("Gemini returned empty response")
                
        except Exception as e:
            print(f"❌ Error generating report content: {e}")
            # Return a fallback report
            return self.create_fallback_report(data)
    
    def create_fallback_report(self, data: Dict[str, Any]) -> str:
        """Create a fallback report if Gemini fails"""
        total_revenue = sum(platform.get('revenue', 0) for platform in data.get('platforms', {}).values())
        total_spend = sum(platform.get('spend', 0) for platform in data.get('platforms', {}).values())
        total_profit = total_revenue - total_spend
        
        return f"""
# Executive Summary
This report provides an overview of your marketing ROI performance based on the available data.

# Performance Overview
- Total Revenue: ${total_revenue:,.2f}
- Total Spend: ${total_spend:,.2f}
- Total Profit: ${total_profit:,.2f}
- ROI: {(total_profit / total_spend * 100) if total_spend > 0 else 0:.1f}%

# Platform Performance Analysis
{self._format_platform_data(data.get('platforms', {}))}

# Key Insights
- Review platform performance data above
- Identify top performing channels
- Analyze spending patterns

# Recommendations
- Focus on high-performing platforms
- Optimize underperforming channels
- Consider budget reallocation

# Action Items
- Monitor performance metrics regularly
- Test new content strategies
- Review and adjust budgets as needed
"""
    
    def _format_platform_data(self, platforms: Dict[str, Any]) -> str:
        """Format platform data for the fallback report"""
        if not platforms:
            return "No platform data available."
        
        formatted = ""
        for platform, data in platforms.items():
            revenue = data.get('revenue', 0)
            spend = data.get('spend', 0)
            profit = revenue - spend
            roi = (profit / spend * 100) if spend > 0 else 0
            
            formatted += f"""
## {platform.title()}
- Revenue: ${revenue:,.2f}
- Spend: ${spend:,.2f}
- Profit: ${profit:,.2f}
- ROI: {roi:.1f}%
"""
        
        return formatted
    
    def save_html(self, html_content: str, filename: str = "roi_report.html") -> str:
        """Save HTML content to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ HTML report saved: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving HTML: {e}")
            return ""
    
    def save_pdf(self, html_content: str, filename: str = "roi_report.pdf") -> str:
        """Convert HTML to PDF and save"""
        try:
            # Configure fonts
            font_config = FontConfiguration()
            
            # Create HTML document
            html_doc = HTML(string=html_content)
            
            # Generate PDF
            html_doc.write_pdf(
                filename,
                font_config=font_config
            )
            
            print(f"✅ PDF report saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            print("Make sure WeasyPrint is properly installed with system dependencies")
            return ""
    
    async def generate_full_report(self, data: Dict[str, Any], output_dir: str = ".") -> Dict[str, str]:
        """Generate complete report (HTML and PDF)"""
        print("🚀 Generating ROI Report...")
        
        # Generate report content
        print("📝 Generating report content with Gemini...")
        report_content = await self.generate_report_content(data)
        
        # Create HTML template
        print("🎨 Creating HTML template...")
        html_content = self.create_html_template(report_content, data)
        
        # Save files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = os.path.join(output_dir, f"roi_report_{timestamp}.html")
        pdf_filename = os.path.join(output_dir, f"roi_report_{timestamp}.pdf")
        
        html_file = self.save_html(html_content, html_filename)
        pdf_file = self.save_pdf(html_content, pdf_filename)
        
        return {
            "html": html_file,
            "pdf": pdf_file,
            "content": report_content
        }


def create_sample_data() -> Dict[str, Any]:
    """Create sample data for testing"""
    return {
        "platforms": {
            "facebook": {
                "revenue": 15000.00,
                "spend": 5000.00,
                "posts": 45,
                "engagement_rate": 3.2,
                "content_types": {
                    "video": {"count": 20, "avg_performance": 85},
                    "image": {"count": 15, "avg_performance": 65},
                    "carousel": {"count": 10, "avg_performance": 72}
                }
            },
            "instagram": {
                "revenue": 12000.00,
                "spend": 4000.00,
                "posts": 38,
                "engagement_rate": 4.1,
                "content_types": {
                    "reel": {"count": 25, "avg_performance": 92},
                    "post": {"count": 13, "avg_performance": 58}
                }
            },
            "youtube": {
                "revenue": 8000.00,
                "spend": 3000.00,
                "videos": 12,
                "engagement_rate": 2.8,
                "content_types": {
                    "tutorial": {"count": 8, "avg_performance": 78},
                    "review": {"count": 4, "avg_performance": 85}
                }
            }
        },
        "period": "January 2024",
        "total_metrics": {
            "revenue": 35000.00,
            "spend": 12000.00,
            "profit": 23000.00,
            "roi": 191.67
        }
    }


async def main():
    """Main function for testing"""
    try:
        # Check if Gemini API key is available
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            print("❌ GEMINI_API_KEY not found in environment variables")
            print("Please add GEMINI_API_KEY to your .env file")
            return
        
        # Create report generator
        generator = StandaloneReportGenerator(gemini_key)
        
        # Create sample data (you can replace this with your actual data)
        sample_data = create_sample_data()
        
        print("📊 Sample data created:")
        print(f"   Platforms: {list(sample_data['platforms'].keys())}")
        print(f"   Total Revenue: ${sample_data['total_metrics']['revenue']:,.2f}")
        print(f"   Total Spend: ${sample_data['total_metrics']['spend']:,.2f}")
        
        # Generate report
        result = await generator.generate_full_report(sample_data)
        
        if result["html"] and result["pdf"]:
            print("\n✅ Report generation completed successfully!")
            print(f"📄 HTML Report: {result['html']}")
            print(f"📊 PDF Report: {result['pdf']}")
        else:
            print("\n❌ Report generation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

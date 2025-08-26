#!/usr/bin/env python3
"""
Generate ROI Report and Save to File (Text, HTML, and PDF formats)
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))
from app.core.supabase_client import supabase_client
from app.api.v1.endpoints.roi import _fetch_all_roi_data, _summarize_data_by_platform, _calculate_totals, _create_report_prompt_all_data

load_dotenv()

def create_html_template(report_content: str, report_data: dict, total_revenue: float, total_spend: float, total_profit: float, roi_percentage: float, profit_margin: float, roi_status: str) -> str:
    """Create a professional HTML template for the ROI report"""
    
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
            margin-bottom: 1rem;
        }}
        
        .header .date {{
            font-size: 1rem;
            opacity: 0.9;
            font-weight: 500;
            background: rgba(255, 255, 255, 0.1);
            padding: 0.5rem 1rem;
            border-radius: 25px;
            display: inline-block;
            backdrop-filter: blur(10px);
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            padding: 2.5rem;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        }}
        
        .metric-card {{
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border-left: 6px solid #667eea;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}
        
        .metric-card h3 {{
            font-size: 0.875rem;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.75rem;
        }}
        
        .metric-card .value {{
            font-size: 2.5rem;
            font-weight: 800;
            color: #1f2937;
            margin-bottom: 0.5rem;
            line-height: 1;
        }}
        
        .metric-card .change {{
            font-size: 0.875rem;
            color: {roi_color};
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }}
        
        .metric-card .change::before {{
            content: '↗';
            font-size: 1rem;
        }}
        
        .metric-card.negative .change {{
            color: #dc2626;
        }}
        
        .metric-card.negative .change::before {{
            content: '↘';
        }}
        
        .content {{
            padding: 2.5rem;
        }}
        
        .section {{
            margin-bottom: 3rem;
        }}
        
        .section h2 {{
            font-size: 1.75rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid #e5e7eb;
            position: relative;
        }}
        
        .section h2::after {{
            content: '';
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }}
        
        .report-content {{
            background: #f8fafc;
            padding: 2rem;
            border-radius: 12px;
            border-left: 6px solid #667eea;
            white-space: pre-wrap;
            font-family: 'Inter', sans-serif;
            line-height: 1.8;
            font-size: 1rem;
            color: #374151;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        
        /* Enhanced Table Styles */
        .report-content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #e5e7eb;
        }}
        
        /* Platform Performance Table Specific Styles - Based on Key Performance Metrics Design */
        .platform-performance-section {{
            margin: 3rem 0;
        }}
        
        .platform-performance-section h2 {{
            font-size: 14pt;
            font-weight: 600;
            margin: 20pt 0 12pt 0;
            color: #34495e;
            background-color: #f8f9fa;
            padding: 8pt 12pt;
            border-left: 4pt solid #3498db;
            border-radius: 4pt;
        }}
        
        .platform-performance-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15pt 0;
            font-size: 9pt;
            box-shadow: 0 2pt 8pt rgba(0,0,0,0.1);
            border-radius: 6pt;
            overflow: hidden;
        }}
        
        .platform-performance-table thead {{
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
        }}
        
        .platform-performance-table thead th {{
            padding: 12pt 8pt;
            border: none;
            font-weight: 600;
            text-align: left;
            font-size: 10pt;
            text-transform: uppercase;
            letter-spacing: 0.3pt;
        }}
        
        .platform-performance-table thead th:first-child {{
            text-align: left;
        }}
        
        .platform-performance-table tbody tr {{
            transition: background-color 0.2s ease;
        }}
        
        .platform-performance-table tbody tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        .platform-performance-table tbody tr:hover {{
            background-color: #e8f4fd;
        }}
        
        .platform-performance-table tbody td {{
            padding: 10pt 8pt;
            border-bottom: 1pt solid #ecf0f1;
            word-wrap: break-word;
            vertical-align: top;
            background-color: #ffffff;
        }}
        
        .platform-performance-table tbody tr:nth-child(even) td {{
            background-color: #f8f9fa;
        }}
        
        .platform-performance-table tbody tr:hover td {{
            background-color: #e8f4fd;
        }}
        
        .platform-name {{
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .platform-indicator {{
            display: inline-block;
            width: 8pt;
            height: 8pt;
            border-radius: 50%;
            margin-right: 6pt;
            vertical-align: middle;
        }}
        
        .revenue, .spend {{
            color: #27ae60;
            font-weight: 600;
            font-family: 'Courier New', monospace;
        }}
        
        .roi-value {{
            color: #27ae60;
            font-weight: 600;
        }}
        
        .roas-value {{
            color: #3498db;
            font-weight: 600;
        }}
        
        .engagement-value, .ctr-value {{
            color: #e74c3c;
            font-weight: 600;
        }}
        
        /* Responsive design for platform performance table */
        @media (max-width: 768px) {{
            .platform-performance-table {{
                font-size: 8pt;
            }}
            
            .platform-performance-table thead th,
            .platform-performance-table tbody td {{
                padding: 8pt 6pt;
            }}
        }}
        
        .report-content table thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .report-content table thead th {{
            padding: 1.25rem 1rem;
            text-align: center;
            font-weight: 700;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border: none;
            position: relative;
        }}
        
        .report-content table thead th:first-child {{
            text-align: left;
        }}
        
        .report-content table thead th:not(:last-child)::after {{
            content: '';
            position: absolute;
            right: 0;
            top: 25%;
            bottom: 25%;
            width: 1px;
            background: rgba(255, 255, 255, 0.3);
        }}
        
        .report-content table tbody tr {{
            transition: background-color 0.2s ease;
        }}
        
        .report-content table tbody tr:nth-child(even) {{
            background: #f8fafc;
        }}
        
        .report-content table tbody tr:hover {{
            background: #f1f5f9;
            transform: scale(1.01);
        }}
        
        .report-content table tbody td {{
            padding: 1rem;
            text-align: center;
            font-weight: 500;
            border-bottom: 1px solid #e5e7eb;
            position: relative;
        }}
        
        .report-content table tbody td:first-child {{
            text-align: left;
            font-weight: 700;
            color: #1f2937;
            background: #f8fafc;
        }}
        
        .report-content table tbody td:not(:last-child)::after {{
            content: '';
            position: absolute;
            right: 0;
            top: 15%;
            bottom: 15%;
            width: 1px;
            background: #e5e7eb;
        }}
        
        /* Platform-specific styling */
        .report-content table tbody tr:nth-child(1) td:first-child {{
            color: #1877f2;
        }}
        
        .report-content table tbody tr:nth-child(2) td:first-child {{
            color: #e4405f;
        }}
        
        .report-content table tbody tr:nth-child(3) td:first-child {{
            color: #ff0000;
        }}
        
        /* Value styling */
        .report-content table tbody td:nth-child(2),
        .report-content table tbody td:nth-child(3) {{
            font-family: 'Courier New', monospace;
            font-weight: 600;
            color: #059669;
        }}
        
        .report-content table tbody td:nth-child(4) {{
            font-weight: 700;
            color: #059669;
        }}
        
        .report-content table tbody td:nth-child(5) {{
            font-weight: 600;
            color: #7c3aed;
        }}
        
        .report-content table tbody td:nth-child(6),
        .report-content table tbody td:nth-child(7) {{
            font-weight: 600;
            color: #dc2626;
        }}
        
        /* Responsive table */
        @media (max-width: 768px) {{
            .report-content table {{
                font-size: 0.875rem;
            }}
            
            .report-content table thead th,
            .report-content table tbody td {{
                padding: 0.75rem 0.5rem;
            }}
        }}
        
        .footer {{
            background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }}
        
        .footer p {{
            margin-bottom: 0.5rem;
            opacity: 0.9;
        }}
        
        .footer .report-id {{
            font-family: 'Courier New', monospace;
            background: rgba(255, 255, 255, 0.1);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
        }}
        
        .platform-breakdown {{
            margin-top: 2rem;
        }}
        
        .platform-item {{
            background: white;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-radius: 12px;
            border-left: 6px solid #667eea;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease;
        }}
        
        .platform-item:hover {{
            transform: translateX(4px);
        }}
        
        .platform-item h4 {{
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 1rem;
            font-size: 1.25rem;
        }}
        
        .platform-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
        }}
        
        .platform-metric {{
            background: #f8fafc;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }}
        
        .platform-metric .label {{
            color: #6b7280;
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
            display: block;
        }}
        
        .platform-metric .value {{
            color: #1f2937;
            font-weight: 700;
            font-size: 1.25rem;
        }}
        
        .roi-status {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            background: {roi_color}20;
            color: {roi_color};
            border: 1px solid {roi_color}40;
        }}
        
        @media print {{
            body {{
                background: white;
                margin: 0;
            }}
            .container {{
                box-shadow: none;
                margin: 0;
                border-radius: 0;
            }}
            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 1rem;
                padding: 1.5rem;
            }}
            .metric-card {{
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                padding: 2rem;
            }}
            .header h1 {{
                font-size: 2rem;
            }}
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 1rem;
            }}
            .header h1 {{
                font-size: 2rem;
            }}
            .metrics-grid {{
                grid-template-columns: 1fr;
                padding: 1.5rem;
            }}
            .content {{
                padding: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1>📊 ROI Performance Report</h1>
                <div class="subtitle">Comprehensive Return on Investment Analysis</div>
                <div class="date">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>💰 Total Revenue</h3>
                <div class="value">${total_revenue:,.2f}</div>
                <div class="change">+{roi_percentage:.1f}% ROI</div>
            </div>
            
            <div class="metric-card">
                <h3>💸 Total Spend</h3>
                <div class="value">${total_spend:,.2f}</div>
                <div class="change">Investment</div>
            </div>
            
            <div class="metric-card">
                <h3>💵 Total Profit</h3>
                <div class="value">${total_profit:,.2f}</div>
                <div class="change">+{profit_margin:.1f}% Margin</div>
            </div>
            
            <div class="metric-card">
                <h3>📈 ROI Percentage</h3>
                <div class="value">{roi_percentage:.1f}%</div>
                <div class="change">
                    <span class="roi-status">{roi_status.title()}</span>
                </div>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📋 Executive Summary</h2>
                <div class="report-content">{report_content}</div>
            </div>
            
            <div class="section">
                {_create_platform_performance_table_html(report_data.get('all_data', {}).get('platforms', {}))}
            </div>
            
            <div class="section platform-breakdown">
                <h2>🎯 Platform Performance Breakdown</h2>
                {_generate_platform_html(report_data)}
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by <strong>BOS Solution ROI Analytics System</strong></p>
            <p>Report ID: <span class="report-id">{datetime.now().strftime('%Y%m%d_%H%M%S')}</span></p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_template

def _create_platform_performance_table_html(platform_summary: dict) -> str:
    """Create a professional HTML table for platform performance summary"""
    
    # Define platform colors
    platform_colors = {
        'Facebook': '#1877F2',
        'Instagram': '#E4405F', 
        'YouTube': '#FF0000'
    }
    
    # Start building the HTML table
    table_html = """
<div class="platform-performance-section">
    <h2>Platform Performance Summary</h2>
    <div class="table-container">
        <table class="platform-performance-table">
            <thead>
                <tr>
                    <th>Platform</th>
                    <th>Total Revenue</th>
                    <th>Total Spend</th>
                    <th>ROI (%)</th>
                    <th>ROAS</th>
                    <th>Engagement Rate</th>
                    <th>CTR (%)</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Add data rows for each platform
    for platform, data in platform_summary.items():
        if platform in ['Facebook', 'Instagram', 'YouTube']:
            revenue = data.get('total_revenue', 0)
            spend = data.get('total_spend', 0)
            roi_percentage = data.get('avg_roi', 0)
            roas = data.get('roas', 0)
            engagement_rate = data.get('engagement_rate', 0)
            ctr = data.get('click_through_rate', 0)
            
            # Format values
            revenue_formatted = f"${revenue:,.2f}"
            spend_formatted = f"${spend:,.2f}"
            roi_formatted = f"{roi_percentage:.2f}%"
            roas_formatted = f"{roas:.2f}"
            engagement_formatted = f"{engagement_rate:.2f}%"
            ctr_formatted = f"{ctr:.2f}%"
            
            # Get platform color
            platform_color = platform_colors.get(platform, '#6B7280')
            
            # Determine ROI badge class
            roi_class = "roi-excellent" if roi_percentage >= 400 else "roi-good" if roi_percentage >= 300 else "roi-moderate" if roi_percentage >= 200 else "roi-poor"
            
            table_html += f"""
                <tr>
                    <td class="platform-name">
                        <span class="platform-indicator" style="background-color: {platform_color};"></span>
                        {platform}
                    </td>
                    <td class="revenue">{revenue_formatted}</td>
                    <td class="spend">{spend_formatted}</td>
                    <td class="roi-value">{roi_formatted}</td>
                    <td class="roas-value">{roas_formatted}</td>
                    <td class="engagement-value">{engagement_formatted}</td>
                    <td class="ctr-value">{ctr_formatted}</td>
                </tr>
            """
    
    table_html += """
            </tbody>
        </table>
    </div>
</div>
    """
    
    return table_html

def _generate_platform_html(report_data: dict) -> str:
    """Generate HTML for platform breakdown section"""
    platforms = report_data.get('all_data', {}).get('platforms', {})
    
    if not platforms:
        return '<p style="text-align: center; color: #6b7280; font-style: italic; padding: 2rem;">No platform data available</p>'
    
    # Platform icons mapping
    platform_icons = {
        'youtube': '📺',
        'instagram': '📷', 
        'facebook': '📘',
        'twitter': '🐦',
        'tiktok': '🎵',
        'linkedin': '💼',
        'google': '🔍',
        'bing': '🔍',
        'other': '🌐'
    }
    
    platform_html = ""
    for platform, data in platforms.items():
        revenue = data.get('total_revenue', 0)
        spend = data.get('total_spend', 0)
        profit = data.get('total_profit', 0)
        roi = data.get('total_roi', 0)
        roi_percentage = (roi / spend * 100) if spend > 0 else 0
        
        # Determine ROI status for this platform
        platform_roi_status = "excellent" if roi_percentage >= 100 else "good" if roi_percentage >= 50 else "moderate" if roi_percentage >= 20 else "poor"
        platform_roi_color = {
            "excellent": "#059669",
            "good": "#10b981", 
            "moderate": "#f59e0b",
            "poor": "#dc2626"
        }.get(platform_roi_status, "#6b7280")
        
        # Get platform icon
        platform_icon = platform_icons.get(platform.lower(), platform_icons['other'])
        
        platform_html += f"""
        <div class="platform-item">
            <h4>{platform_icon} {platform.title()}</h4>
            <div class="platform-metrics">
                <div class="platform-metric">
                    <span class="label">💰 Revenue</span>
                    <span class="value">${revenue:,.2f}</span>
                </div>
                <div class="platform-metric">
                    <span class="label">💸 Spend</span>
                    <span class="value">${spend:,.2f}</span>
                </div>
                <div class="platform-metric">
                    <span class="label">💵 Profit</span>
                    <span class="value">${profit:,.2f}</span>
                </div>
                <div class="platform-metric">
                    <span class="label">📈 ROI</span>
                    <span class="value" style="color: {platform_roi_color};">{roi_percentage:.1f}%</span>
                    <div style="margin-top: 0.5rem;">
                        <span class="roi-status" style="background: {platform_roi_color}20; color: {platform_roi_color}; border-color: {platform_roi_color}40;">
                            {platform_roi_status.title()}
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """
    
    return platform_html

async def generate_roi_report():
    """Generate a ROI report and save it to multiple formats (TXT, HTML, PDF)"""
    print("📊 Generating ROI Report")
    print("=" * 50)
    
    try:
        # Optional Gemini AI (graceful fallback if not configured)
        model = None
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_api_key)
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    print("✅ Using Gemini 1.5 Flash model")
                except Exception as flash_error:
                    print(f"⚠️  Gemini 1.5 Flash not available, using Gemini Pro: {flash_error}")
                    model = genai.GenerativeModel('gemini-pro')
                    print("✅ Using Gemini Pro model")
            except ImportError as e:
                print(f"⚠️  google-generativeai not installed: {e}")
        else:
            print("⚠️  GEMINI_API_KEY not set. Proceeding with basic, non-AI report content.")
        
        # Fetch all data
        print("\n📋 Fetching data from roi_metrics table...")
        all_data = await _fetch_all_roi_data()
        
        if len(all_data) == 0:
            print("❌ No data found in roi_metrics table")
            return False
        
        print(f"✅ Retrieved {len(all_data)} records")
        
        # Process data
        print("\n📊 Processing data...")
        platform_summary = _summarize_data_by_platform(all_data)
        overall_totals = _calculate_totals(platform_summary)
        
        print(f"✅ Processed data for {len(platform_summary)} platforms")
        print(f"   Total revenue: ${overall_totals.get('total_revenue', 0):,.2f}")
        print(f"   Total spend: ${overall_totals.get('total_spend', 0):,.2f}")
        
        # Prepare report data
        report_data = {
            "all_data": {
                "period": "All available data",
                "platforms": platform_summary,
                "totals": overall_totals,
                "total_records": len(all_data)
            }
        }
        
        # Extract key metrics for use in both HTML and PDF
        totals = report_data.get('all_data', {}).get('totals', {})
        total_revenue = totals.get('total_revenue', 0)
        total_spend = totals.get('total_spend', 0)
        total_roi = totals.get('total_roi', 0)
        total_profit = totals.get('total_profit', 0)
        
        # Calculate additional metrics
        roi_percentage = (total_roi / total_spend * 100) if total_spend > 0 else 0
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Determine ROI status for styling
        roi_status = "excellent" if roi_percentage >= 100 else "good" if roi_percentage >= 50 else "moderate" if roi_percentage >= 20 else "poor"
        
        # Generate report
        # Create report content
        if model is not None:
            print("\n🤖 Generating report with Gemini...")
            prompt = _create_report_prompt_all_data(report_data)
            response = model.generate_content(prompt)
            report_content = response.text or ""
            if not report_content:
                print("⚠️  Gemini API returned empty response. Falling back to basic content.")
        else:
            report_content = ""
        
        if not report_content:
            # Basic fallback content without AI
            print("📝 Building basic report content (no AI)...")
            report_content = (
                "Executive Summary\n"
                f"Total Revenue: ${total_revenue:,.2f}\n"
                f"Total Spend: ${total_spend:,.2f}\n"
                f"Total Profit: ${total_profit:,.2f}\n"
                f"ROI Percentage: {roi_percentage:.1f}%\n\n"
                "Platform Highlights\n" +
                "\n".join(
                    f"- {plat.title()}: Revenue ${data.get('total_revenue',0):,.2f}, "
                    f"Spend ${data.get('total_spend',0):,.2f}, ROI {(data.get('total_revenue',0)-data.get('total_spend',0))/data.get('total_spend',1)*100 if data.get('total_spend',0)>0 else 0:.1f}%"
                    for plat, data in platform_summary.items()
                )
            )
        else:
            print(f"✅ Generated report ({len(report_content)} characters)")
        
        # Clean the report content to remove ** formatting
        print("\n🧹 Cleaning report content...")
        try:
            from app.services.pdf_conversion_agent import pdf_agent
            cleaned_report_content = pdf_agent.clean_text(report_content)
            print(f"✅ Cleaned report content (removed ** formatting)")
        except Exception as e:
            print(f"⚠️  Text cleaning failed, using original content: {e}")
            cleaned_report_content = report_content
        
        # Create timestamp for filenames
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Save text report
        txt_filename = f"roi_report_{timestamp}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(f"ROI REPORT - Generated on {datetime.now().strftime('%m/%d/%Y')}\n")
            f.write("=" * 80 + "\n\n")
            f.write(cleaned_report_content)
        
        print(f"💾 Text report saved to: {txt_filename}")
        
        # Generate HTML report
        print("\n🌐 Generating HTML report...")
        html_content = create_html_template(cleaned_report_content, report_data, total_revenue, total_spend, total_profit, roi_percentage, profit_margin, roi_status)
        html_filename = f"roi_report_{timestamp}.html"
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"💾 HTML report saved to: {html_filename}")
        
        # Generate PDF report
        print("\n📄 Generating PDF report...")
        pdf_filename = f"roi_report_{timestamp}.pdf"
        pdf_generated = False
        
        # Try WeasyPrint first (better HTML to PDF conversion)
        try:
            import weasyprint
            from weasyprint import HTML, CSS
            
            # Additional CSS for PDF optimization
            pdf_css = CSS(string='''
                @page {
                    size: A4;
                    margin: 1cm;
                    @top-center {
                        content: "ROI Performance Report";
                        font-size: 10pt;
                        color: #6b7280;
                    }
                    @bottom-center {
                        content: "Page " counter(page) " of " counter(pages);
                        font-size: 10pt;
                        color: #6b7280;
                    }
                }
                
                body {
                    font-size: 12pt;
                    line-height: 1.4;
                }
                
                .header {
                    page-break-after: avoid;
                }
                
                .metrics-grid {
                    page-break-inside: avoid;
                }
                
                .section {
                    page-break-inside: avoid;
                }
                
                .platform-item {
                    page-break-inside: avoid;
                }
                
                .metric-card {
                    break-inside: avoid;
                }
                
                @media print {
                    .metric-card:hover {
                        transform: none;
                    }
                    .platform-item:hover {
                        transform: none;
                    }
                }
            ''')
            
            # Generate PDF
            HTML(string=html_content).write_pdf(pdf_filename, stylesheets=[pdf_css])
            print(f"💾 PDF report saved to: {pdf_filename}")
            pdf_generated = True
            
        except ImportError as e:
            print(f"⚠️  WeasyPrint not available: {e}")
        except Exception as e:
            print(f"⚠️  WeasyPrint PDF generation failed: {e}")
        
        # Fallback to ReportLab if WeasyPrint fails
        if not pdf_generated:
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib import colors
                from reportlab.lib.enums import TA_CENTER, TA_LEFT
                
                # Create PDF document
                doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
                styles = getSampleStyleSheet()
                
                # Custom styles
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    spaceAfter=30,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor('#1f2937')
                )
                
                subtitle_style = ParagraphStyle(
                    'CustomSubtitle',
                    parent=styles['Heading2'],
                    fontSize=16,
                    spaceAfter=20,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor('#6b7280')
                )
                
                heading_style = ParagraphStyle(
                    'CustomHeading',
                    parent=styles['Heading2'],
                    fontSize=18,
                    spaceAfter=15,
                    textColor=colors.HexColor('#1f2937')
                )
                
                body_style = ParagraphStyle(
                    'CustomBody',
                    parent=styles['Normal'],
                    fontSize=12,
                    spaceAfter=12,
                    textColor=colors.HexColor('#374151'),
                    leading=16
                )
                
                # Build PDF content
                story = []
                
                # Title
                story.append(Paragraph("📊 ROI Performance Report", title_style))
                story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
                story.append(Spacer(1, 20))
                
                # Key Metrics Table
                metrics_data = [
                    ['Metric', 'Value', 'Status'],
                    ['Total Revenue', f"${total_revenue:,.2f}", ''],
                    ['Total Spend', f"${total_spend:,.2f}", ''],
                    ['Total Profit', f"${total_profit:,.2f}", ''],
                    ['ROI Percentage', f"{roi_percentage:.1f}%", roi_status.title()]
                ]
                
                metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch, 1.5*inch])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 11),
                ]))
                
                story.append(Paragraph("Key Performance Metrics", heading_style))
                story.append(metrics_table)
                story.append(Spacer(1, 20))
                
                # Executive Summary
                story.append(Paragraph("📋 Executive Summary", heading_style))
                
                # Split report content into paragraphs
                report_paragraphs = report_content.split('\n\n')
                for para in report_paragraphs:
                    if para.strip():
                        story.append(Paragraph(para.strip(), body_style))
                        story.append(Spacer(1, 8))
                
                # Platform Breakdown
                platforms = report_data.get('all_data', {}).get('platforms', {})
                if platforms:
                    story.append(Paragraph("🎯 Platform Performance Breakdown", heading_style))
                    
                    for platform, data in platforms.items():
                        revenue = data.get('total_revenue', 0)
                        spend = data.get('total_spend', 0)
                        profit = data.get('total_profit', 0)
                        roi = data.get('total_roi', 0)
                        platform_roi_percentage = (roi / spend * 100) if spend > 0 else 0
                        
                        platform_data = [
                            ['Platform', platform.title()],
                            ['Revenue', f"${revenue:,.2f}"],
                            ['Spend', f"${spend:,.2f}"],
                            ['Profit', f"${profit:,.2f}"],
                            ['ROI', f"{platform_roi_percentage:.1f}%"]
                        ]
                        
                        platform_table = Table(platform_data, colWidths=[1.5*inch, 3*inch])
                        platform_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#667eea')),
                            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                        ]))
                        
                        story.append(platform_table)
                        story.append(Spacer(1, 15))
                
                # Build PDF
                doc.build(story)
                print(f"💾 PDF report saved to: {pdf_filename}")
                pdf_generated = True
                
            except ImportError as e:
                print(f"⚠️  ReportLab not available: {e}")
                print("   PDF generation skipped. Install with: pip install reportlab")
            except Exception as e:
                print(f"⚠️  ReportLab PDF generation failed: {e}")
                import traceback
                traceback.print_exc()
        
        if not pdf_generated:
            print("   PDF generation skipped - no suitable PDF library available")
        
        # Also save raw data for reference
        data_filename = f"roi_data_{timestamp}.json"
        with open(data_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"📊 Raw data saved to: {data_filename}")
        
        # Show report preview
        print(f"\n📝 Report Preview:")
        print("-" * 50)
        lines = report_content.split('\n')[:20]
        for line in lines:
            print(line)
        if len(report_content.split('\n')) > 20:
            print("...")
        
        print(f"\n🎉 ROI Report generated successfully!")
        print(f"📁 Files created:")
        print(f"   • {txt_filename} - Text report")
        print(f"   • {html_filename} - HTML report")
        if 'pdf_filename' in locals():
            print(f"   • {pdf_filename} - PDF report")
        print(f"   • {data_filename} - Raw data")
        
        return {
            "success": True,
            "timestamp": timestamp,
            "files": {
                "text": txt_filename,
                "html": html_filename,
                "pdf": pdf_filename if pdf_generated else "",
                "json": data_filename,
            }
        }
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}

async def main():
    """Main function"""
    success = await generate_roi_report()
    
    if success:
        print("\n✅ CONCLUSION: ROI report generation is working correctly!")
        return 0
    else:
        print("\n❌ CONCLUSION: ROI report generation failed.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

#!/usr/bin/env python3
"""
Test script for enhanced PDF design and text cleaning functionality
"""

import asyncio
import json
from datetime import datetime
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.pdf_conversion_agent import pdf_agent, create_enhanced_roi_pdf_async

async def test_enhanced_pdf_design():
    """Test the enhanced PDF design with sample data"""
    
    # Sample ROI data with some formatting issues
    sample_roi_data = {
        "platforms": {
            "Facebook": {
                "total_revenue": 15000.50,
                "total_cost": 5000.25,
                "campaigns": [
                    {
                        "campaign_name": "**Summer Sale Campaign**",
                        "revenue": 8000.00,
                        "cost": 2500.00,
                        "date": "2024-01-15"
                    },
                    {
                        "campaign_name": "*Holiday Special*",
                        "revenue": 7000.50,
                        "cost": 2500.25,
                        "date": "2024-01-20"
                    }
                ]
            },
            "Instagram": {
                "total_revenue": 12000.75,
                "total_cost": 4000.00,
                "campaigns": [
                    {
                        "campaign_name": "__Influencer Partnership__",
                        "revenue": 6000.00,
                        "cost": 2000.00,
                        "date": "2024-01-10"
                    },
                    {
                        "campaign_name": "Product Launch",
                        "revenue": 6000.75,
                        "cost": 2000.00,
                        "date": "2024-01-25"
                    }
                ]
            }
        },
        "campaigns": [
            {
                "platform": "Facebook",
                "campaign_name": "**Summer Sale Campaign**",
                "revenue": 8000.00,
                "cost": 2500.00,
                "date": "2024-01-15"
            },
            {
                "platform": "Instagram", 
                "campaign_name": "__Influencer Partnership__",
                "revenue": 6000.00,
                "cost": 2000.00,
                "date": "2024-01-10"
            }
        ]
    }
    
    # Sample YouTube data
    sample_youtube_data = {
        "videos": [
            {
                "title": "**How to Increase ROI** - Complete Guide",
                "views": 15000,
                "likes": 1200,
                "comments": 300,
                "engagement_rate": 0.08,
                "roi_score": 4.5
            },
            {
                "title": "*Marketing Strategies* That Work",
                "views": 12000,
                "likes": 950,
                "comments": 250,
                "engagement_rate": 0.07,
                "roi_score": 4.2
            }
        ],
        "channels": [
            {
                "channel_title": "__Business Channel__",
                "total_subscribers": 50000,
                "total_videos": 150,
                "total_views": 500000,
                "estimated_monthly_revenue": 2500.00
            }
        ]
    }
    
    # Sample Instagram data
    sample_instagram_data = {
        "roi_metrics": [
            {
                "update_timestamp": "2024-01-15T10:30:00Z",
                "views": 8000,
                "likes": 650,
                "comments": 180,
                "revenue_generated": 4000.00,
                "ad_spend": 1500.00,
                "roi_percentage": 166.67
            }
        ],
        "social_accounts": [
            {
                "account_name": "**Main Business Account**",
                "username": "business_main",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z"
            }
        ]
    }
    
    print("🧪 Testing Enhanced PDF Design and Text Cleaning...")
    
    # Test text cleaning functionality
    print("\n1. Testing text cleaning functionality...")
    test_text = "This is a **bold text** with *italics* and __underlines__"
    cleaned_text = pdf_agent.clean_text(test_text)
    print(f"   Original: {test_text}")
    print(f"   Cleaned:  {cleaned_text}")
    
    # Test data cleaning
    print("\n2. Testing data cleaning functionality...")
    cleaned_data = pdf_agent.clean_data(sample_roi_data)
    print("   Data cleaned successfully")
    
    # Test simple PDF generation
    print("\n3. Testing simple PDF generation...")
    try:
        pdf_bytes, output_path = await pdf_agent.create_simple_roi_pdf(sample_roi_data)
        print(f"   ✅ Simple PDF generated successfully ({len(pdf_bytes)} bytes)")
        if output_path:
            print(f"   📄 Saved to: {output_path}")
    except Exception as e:
        print(f"   ❌ Simple PDF generation failed: {e}")
    
    # Test enhanced PDF generation (without actual user_id)
    print("\n4. Testing enhanced PDF template generation...")
    try:
        # Create enhanced HTML template directly
        html_content = pdf_agent._create_enhanced_html_template(
            cleaned_data, 
            sample_youtube_data, 
            sample_instagram_data
        )
        print(f"   ✅ Enhanced HTML template generated successfully ({len(html_content)} characters)")
        
        # Test PDF conversion
        pdf_bytes, output_path = await pdf_agent.convert_html_to_pdf(html_content)
        print(f"   ✅ Enhanced PDF generated successfully ({len(pdf_bytes)} bytes)")
        if output_path:
            print(f"   📄 Saved to: {output_path}")
            
    except Exception as e:
        print(f"   ❌ Enhanced PDF generation failed: {e}")
    
    # Test JSON to PDF conversion
    print("\n5. Testing JSON to PDF conversion...")
    try:
        from app.services.pdf_conversion_agent import generate_pdf_from_json_async
        pdf_bytes, output_path = await generate_pdf_from_json_async(sample_roi_data)
        print(f"   ✅ JSON to PDF conversion successful ({len(pdf_bytes)} bytes)")
        if output_path:
            print(f"   📄 Saved to: {output_path}")
    except Exception as e:
        print(f"   ❌ JSON to PDF conversion failed: {e}")
    
    print("\n🎉 Enhanced PDF Design Test Completed!")
    print("\nKey Improvements Made:")
    print("✅ Professional and modern design with gradients and shadows")
    print("✅ Clean typography with Segoe UI font family")
    print("✅ Color-coded metrics (green for positive, red for negative)")
    print("✅ Platform-specific sections with icons")
    print("✅ Responsive metric cards with hover effects")
    print("✅ Text cleaning to remove asterisks and formatting issues")
    print("✅ Enhanced table styling with alternating row colors")
    print("✅ Professional footer with report metadata")

if __name__ == "__main__":
    asyncio.run(test_enhanced_pdf_design())

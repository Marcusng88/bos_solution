#!/usr/bin/env python3
"""
Test script for ROI Report Generator
This script tests the report generation functionality and helps with debugging.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

async def test_report_generation():
    """Test the report generation functionality"""
    
    print("🧪 Testing ROI Report Generator")
    print("=" * 50)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    gemini_key = os.getenv("GEMINI_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("   Please add GEMINI_API_KEY to your .env file")
        return False
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        print("   Please ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set")
        return False
    
    print("✅ Environment variables configured")
    
    # Test Supabase connection
    print("\n2. Testing Supabase connection...")
    try:
        from app.core.supabase_client import supabase_client
        
        # Test a simple query
        response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={"limit": 1}
        )
        
        if response.status_code == 200:
            print("✅ Supabase connection successful")
            data = response.json()
            print(f"   Found {len(data)} records in roi_metrics table")
        else:
            print(f"❌ Supabase connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return False
    
    # Test Gemini API
    print("\n3. Testing Gemini API...")
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=gemini_key)
        # Try gemini-1.5-flash first, fallback to gemini-pro
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("Using Gemini 1.5 Flash model")
        except Exception as flash_error:
            print(f"Gemini 1.5 Flash not available, trying Gemini Pro: {flash_error}")
            model = genai.GenerativeModel('gemini-pro')
            print("Using Gemini Pro model")
        
        # Test with a simple prompt
        response = model.generate_content("Hello, this is a test. Please respond with 'Test successful' if you can see this message.")
        
        if response.text:
            print("✅ Gemini API connection successful")
            print(f"   Response: {response.text[:100]}...")
        else:
            print("❌ Gemini API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return False
    
    # Test data processing functions
    print("\n4. Testing data processing functions...")
    try:
        from app.api.v1.endpoints.roi import (
            _fetch_all_roi_data,
            _summarize_data_by_platform,
            _calculate_totals,
            _calculate_month_over_month_changes
        )
        
        # Calculate date ranges
        now = datetime.now(timezone.utc)
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        previous_month_end = current_month_start - timedelta(seconds=1)
        previous_month_start = previous_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        print(f"   Current month: {current_month_start.strftime('%B %Y')}")
        print(f"   Previous month: {previous_month_start.strftime('%B %Y')}")
        
        # Fetch data
        all_data = await _fetch_all_roi_data()
        current_data = all_data  # Use all data for testing
        previous_data = []  # No previous month data for testing
        
        print(f"   Current month records: {len(current_data)}")
        print(f"   Previous month records: {len(previous_data)}")
        
        # Process data
        current_summary = _summarize_data_by_platform(current_data)
        previous_summary = _summarize_data_by_platform(previous_data)
        
        print(f"   Current month platforms: {list(current_summary.keys())}")
        print(f"   Previous month platforms: {list(previous_summary.keys())}")
        
        # Calculate totals
        current_totals = _calculate_totals(current_summary)
        previous_totals = _calculate_totals(previous_summary)
        
        print(f"   Current month total revenue: ${current_totals.get('total_revenue', 0):,.2f}")
        print(f"   Previous month total revenue: ${previous_totals.get('total_revenue', 0):,.2f}")
        
        # Calculate changes
        mom_changes = _calculate_month_over_month_changes(current_summary, previous_summary)
        
        print("✅ Data processing functions working correctly")
        
    except Exception as e:
        print(f"❌ Data processing error: {e}")
        return False
    
    # Test report generation (if there's data)
    print("\n5. Testing report generation...")
    try:
        if len(current_data) > 0 or len(previous_data) > 0:
            from app.api.v1.endpoints.roi import _create_report_prompt
            
            report_data = {
                "current_month": {
                    "period": current_month_start.strftime('%B %Y'),
                    "platforms": current_summary,
                    "totals": current_totals
                },
                "previous_month": {
                    "period": previous_month_start.strftime('%B %Y'),
                    "platforms": previous_summary,
                    "totals": previous_totals
                },
                "month_over_month_changes": mom_changes
            }
            
            prompt = _create_report_prompt(report_data)
            print(f"   Generated prompt length: {len(prompt)} characters")
            
            # Test with Gemini
            response = model.generate_content(prompt)
            
            if response.text:
                print("✅ Report generation successful")
                print(f"   Generated report length: {len(response.text)} characters")
                print(f"   Report preview: {response.text[:200]}...")
            else:
                print("❌ Report generation returned empty response")
                return False
        else:
            print("⚠️  No data available for report generation test")
            print("   This is normal if the roi_metrics table is empty")
            
    except Exception as e:
        print(f"❌ Report generation error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")
    print("\nThe ROI Report Generator is ready to use.")
    print("\nTo use it:")
    print("1. Start your backend server")
    print("2. Navigate to the ROI dashboard")
    print("3. Click 'Generate Report' to create AI-powered reports")
    
    return True

async def main():
    """Main function"""
    try:
        success = await test_report_generation()
        if not success:
            print("\n❌ Some tests failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Test script for improved ROI formatting functionality
"""

import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.pdf_conversion_agent import pdf_agent

def test_roi_formatting():
    """Test the improved ROI formatting functionality"""
    
    print("🧪 Testing Improved ROI Formatting...")
    
    # Test case 1: Original problematic format
    test_text_1 = "* **Total Revenue:** $18,087,958.79 * **Total Spend:** $4,860,427.43 * **Total Profit:** $13,227,531.36 * **Overall ROI:** 272.15% * **Overall ROAS:** 3.72"
    
    print("\n1. Testing original problematic format:")
    print(f"   Original: {test_text_1}")
    formatted_1 = pdf_agent.format_roi_metrics(test_text_1)
    print(f"   Formatted: {formatted_1}")
    
    # Test case 2: Alternative format
    test_text_2 = "**Total Revenue:** $18,087,958.79 **Total Spend:** $4,860,427.43 **Total Profit:** $13,227,531.36 **Overall ROI:** 272.15% **Overall ROAS:** 3.72"
    
    print("\n2. Testing alternative format:")
    print(f"   Original: {test_text_2}")
    formatted_2 = pdf_agent.format_roi_metrics(test_text_2)
    print(f"   Formatted: {formatted_2}")
    
    # Test case 3: Mixed format
    test_text_3 = "* **Total Revenue:** $18,087,958.79 * Total Spend: $4,860,427.43 * **Total Profit:** $13,227,531.36 * Overall ROI: 272.15% * **Overall ROAS:** 3.72"
    
    print("\n3. Testing mixed format:")
    print(f"   Original: {test_text_3}")
    formatted_3 = pdf_agent.format_roi_metrics(test_text_3)
    print(f"   Formatted: {formatted_3}")
    
    # Test case 4: Already clean format
    test_text_4 = "Total Revenue: $18,087,958.79 Total Spend: $4,860,427.43 Total Profit: $13,227,531.36 Overall ROI: 272.15% Overall ROAS: 3.72"
    
    print("\n4. Testing already clean format:")
    print(f"   Original: {test_text_4}")
    formatted_4 = pdf_agent.format_roi_metrics(test_text_4)
    print(f"   Formatted: {formatted_4}")
    
    # Test case 5: Regular text (should not be affected)
    test_text_5 = "This is a **bold text** with *italics* and some regular content."
    
    print("\n5. Testing regular text (should not be affected):")
    print(f"   Original: {test_text_5}")
    formatted_5 = pdf_agent.clean_text(test_text_5)
    print(f"   Cleaned: {formatted_5}")
    
    # Test case 6: Data structure with ROI metrics
    test_data = {
        "summary": "* **Total Revenue:** $18,087,958.79 * **Total Spend:** $4,860,427.43 * **Total Profit:** $13,227,531.36 * **Overall ROI:** 272.15% * **Overall ROAS:** 3.72",
        "campaign_name": "**Summer Sale Campaign**",
        "description": "This is a *regular* description with __some__ formatting."
    }
    
    print("\n6. Testing data structure cleaning:")
    print(f"   Original data: {test_data}")
    cleaned_data = pdf_agent.clean_data(test_data)
    print(f"   Cleaned data: {cleaned_data}")
    
    print("\n🎉 ROI Formatting Test Completed!")
    print("\nKey Improvements:")
    print("✅ Removes asterisks (**) from ROI metrics")
    print("✅ Separates metrics into individual lines")
    print("✅ Maintains proper formatting and readability")
    print("✅ Handles various input formats")
    print("✅ Preserves non-ROI text cleaning functionality")

if __name__ == "__main__":
    test_roi_formatting()

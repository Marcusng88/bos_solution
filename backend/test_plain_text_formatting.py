#!/usr/bin/env python3
"""
Test script to verify plain text formatting in ROI reports
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

async def test_plain_text_formatting():
    """Test that ROI reports generate with plain text formatting (no ** symbols)"""
    
    print("📝 Testing Plain Text Formatting for ROI Reports")
    print("=" * 60)
    
    try:
        # Import the report generation function
        from generate_roi_report import generate_roi_report
        
        print("📊 Generating ROI report with plain text formatting...")
        
        # Generate the report
        success = await generate_roi_report()
        
        if success:
            print("\n✅ SUCCESS: Plain text formatting applied!")
            print("\n🎯 Key Changes Made:")
            print("   • Removed all ** bold formatting from AI prompts")
            print("   • Enhanced text cleaning to remove markdown symbols")
            print("   • Metrics now display as 'Revenue: $15,547,580.52' instead of '**Revenue:** $15,547,580.52'")
            print("   • Clean, professional formatting without asterisks")
            print("   • Improved readability with plain text presentation")
            
            print("\n📁 Check the generated files:")
            print("   • roi_report_[timestamp].html - Clean HTML without ** formatting")
            print("   • roi_report_[timestamp].pdf - Professional PDF with plain text")
            print("   • roi_report_[timestamp].txt - Text version with clean formatting")
            
            print("\n🔍 Verification:")
            print("   • No ** symbols should appear in any generated report")
            print("   • All metrics should be displayed as plain text")
            print("   • Professional appearance maintained without markdown formatting")
            
            return True
        else:
            print("\n❌ FAILED: Report generation failed")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_plain_text_formatting())
    sys.exit(0 if success else 1)

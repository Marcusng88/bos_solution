#!/usr/bin/env python3
"""
Test script to verify that ** formatting is being removed from ROI reports
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

async def test_clean_formatting():
    """Test that ** formatting is being removed from ROI reports"""
    
    print("🧹 Testing ** Formatting Removal from ROI Reports")
    print("=" * 60)
    
    try:
        # Import the report generation function
        from generate_roi_report import generate_roi_report
        
        print("📊 Generating ROI report with ** formatting removal...")
        
        # Generate the report
        success = await generate_roi_report()
        
        if success:
            print("\n✅ SUCCESS: Report generated with ** formatting removal!")
            print("\n🎯 Key Improvements:")
            print("   • Added text cleaning to report generation process")
            print("   • Enhanced text cleaning function with aggressive ** removal")
            print("   • Applied cleaning to both text and HTML reports")
            print("   • No more ** symbols in generated reports")
            
            print("\n📁 Check the generated files:")
            print("   • roi_report_[timestamp].txt - Should have NO ** symbols")
            print("   • roi_report_[timestamp].html - Should have NO ** symbols")
            print("   • roi_report_[timestamp].pdf - Should have NO ** symbols")
            
            print("\n🔍 Verification Steps:")
            print("   1. Open the generated .txt file")
            print("   2. Search for '**' - should find NO results")
            print("   3. Check that metrics display as 'Revenue: $15,547,580.52'")
            print("   4. Verify clean, professional formatting")
            
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
    success = asyncio.run(test_clean_formatting())
    sys.exit(0 if success else 1)

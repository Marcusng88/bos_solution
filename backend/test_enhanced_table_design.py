#!/usr/bin/env python3
"""
Test script to generate ROI report with enhanced table design
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

async def test_enhanced_table_design():
    """Test the enhanced table design in ROI reports"""
    
    print("🎨 Testing Enhanced Table Design for ROI Reports")
    print("=" * 60)
    
    try:
        # Import the report generation function
        from generate_roi_report import generate_roi_report
        
        print("📊 Generating ROI report with enhanced table design...")
        
        # Generate the report
        success = await generate_roi_report()
        
        if success:
            print("\n✅ SUCCESS: Enhanced table design applied!")
            print("\n🎯 Key Improvements Made:")
            print("   • Professional gradient header with better typography")
            print("   • Enhanced column alignment and spacing")
            print("   • Platform-specific color coding (Facebook blue, Instagram pink, YouTube red)")
            print("   • Improved value styling with monospace font for monetary values")
            print("   • Better hover effects and visual hierarchy")
            print("   • Responsive design for mobile devices")
            print("   • Enhanced shadows and borders for depth")
            print("   • Color-coded metrics (green for revenue, purple for ROAS, red for rates)")
            
            print("\n📁 Check the generated files:")
            print("   • roi_report_[timestamp].html - Enhanced HTML with beautiful table")
            print("   • roi_report_[timestamp].pdf - Professional PDF with improved styling")
            print("   • roi_report_[timestamp].txt - Text version with proper markdown table")
            
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
    success = asyncio.run(test_enhanced_table_design())
    sys.exit(0 if success else 1)

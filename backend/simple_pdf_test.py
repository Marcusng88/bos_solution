#!/usr/bin/env python3
"""
Simple PDF test
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

print("Testing direct xhtml2pdf import...")

try:
    from xhtml2pdf import pisa
    print("✅ Direct pisa import successful")
except ImportError as e:
    print(f"❌ Direct pisa import failed: {e}")

print("\nTesting through the module...")

try:
    # Import the module directly
    import app.services.pdf_conversion_agent as pdf_module
    print(f"✅ Module import successful")
    print(f"XHTML2PDF_AVAILABLE: {pdf_module.XHTML2PDF_AVAILABLE}")
    print(f"pisa available: {pdf_module.pisa is not None}")
except Exception as e:
    print(f"❌ Module import failed: {e}")
    import traceback
    traceback.print_exc()

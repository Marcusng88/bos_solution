#!/usr/bin/env python3
"""
Test module reload
"""

import sys
import os
import importlib

print("Testing module reload...")

# Add path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Test 1: Import the module
try:
    import app.services.pdf_conversion_agent
    print("✅ Module import successful")
except Exception as e:
    print(f"❌ Module import failed: {e}")

# Test 2: Check the module's attributes
try:
    module = sys.modules['app.services.pdf_conversion_agent']
    print(f"✅ Module found in sys.modules")
    print(f"XHTML2PDF_AVAILABLE: {getattr(module, 'XHTML2PDF_AVAILABLE', 'Not found')}")
    print(f"pisa available: {getattr(module, 'pisa', 'Not found') is not None}")
except Exception as e:
    print(f"❌ Module attribute check failed: {e}")

# Test 3: Reload the module
try:
    importlib.reload(sys.modules['app.services.pdf_conversion_agent'])
    print("✅ Module reload successful")
    module = sys.modules['app.services.pdf_conversion_agent']
    print(f"XHTML2PDF_AVAILABLE after reload: {getattr(module, 'XHTML2PDF_AVAILABLE', 'Not found')}")
except Exception as e:
    print(f"❌ Module reload failed: {e}")

# Test 4: Try importing with a different approach
try:
    # Remove the module from sys.modules
    if 'app.services.pdf_conversion_agent' in sys.modules:
        del sys.modules['app.services.pdf_conversion_agent']
    print("✅ Module removed from sys.modules")
    
    # Import again
    import app.services.pdf_conversion_agent
    print("✅ Module re-import successful")
    print(f"XHTML2PDF_AVAILABLE: {app.services.pdf_conversion_agent.XHTML2PDF_AVAILABLE}")
except Exception as e:
    print(f"❌ Module re-import failed: {e}")

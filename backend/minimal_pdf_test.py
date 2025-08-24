#!/usr/bin/env python3
"""
Minimal PDF test
"""

import sys
import os

print("Step 1: Testing basic xhtml2pdf import...")
try:
    import xhtml2pdf
    print("✅ xhtml2pdf imported")
except ImportError as e:
    print(f"❌ xhtml2pdf import failed: {e}")

print("\nStep 2: Testing pisa import...")
try:
    from xhtml2pdf import pisa
    print("✅ pisa imported")
except ImportError as e:
    print(f"❌ pisa import failed: {e}")

print("\nStep 3: Testing with path modification...")
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from xhtml2pdf import pisa
    print("✅ pisa imported after path modification")
except ImportError as e:
    print(f"❌ pisa import failed after path modification: {e}")

print("\nStep 4: Testing module-level import...")
try:
    # Create a simple test module
    test_code = '''
import sys
import os

try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
    print("✅ xhtml2pdf available in test module")
except ImportError:
    XHTML2PDF_AVAILABLE = False
    print("❌ xhtml2pdf not available in test module")
'''
    
    # Execute the test code
    exec(test_code)
    
except Exception as e:
    print(f"❌ Test module execution failed: {e}")

#!/usr/bin/env python3
"""
Isolated PDF test
"""

import sys
import os

print("Testing isolated import...")

# Test 1: Direct import
try:
    from xhtml2pdf import pisa
    print("✅ Direct import successful")
except ImportError as e:
    print(f"❌ Direct import failed: {e}")

# Test 2: Import with path modification
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from xhtml2pdf import pisa
    print("✅ Import with path modification successful")
except ImportError as e:
    print(f"❌ Import with path modification failed: {e}")

# Test 3: Import the specific module and check what happens
print("\nTesting module import step by step...")

try:
    # Import just the basic imports first
    import os
    import sys
    print("✅ Basic imports successful")
    
    # Add path
    sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
    print("✅ Path modification successful")
    
    # Try xhtml2pdf import
    try:
        from xhtml2pdf import pisa
        print("✅ xhtml2pdf import successful in isolated context")
    except ImportError as e:
        print(f"❌ xhtml2pdf import failed in isolated context: {e}")
    
    # Try other imports that might interfere
    try:
        from datetime import datetime
        from io import BytesIO
        from typing import Dict, Any, Optional, Tuple
        import json
        import logging
        print("✅ Standard library imports successful")
    except ImportError as e:
        print(f"❌ Standard library imports failed: {e}")
    
    # Try Google imports
    try:
        import google.generativeai as genai
        print("✅ Google GenAI import successful")
    except ImportError as e:
        print(f"⚠️  Google GenAI import failed (expected): {e}")
    
    # Now try the xhtml2pdf import again
    try:
        from xhtml2pdf import pisa
        print("✅ xhtml2pdf import successful after other imports")
    except ImportError as e:
        print(f"❌ xhtml2pdf import failed after other imports: {e}")
        
except Exception as e:
    print(f"❌ Module import failed: {e}")
    import traceback
    traceback.print_exc()

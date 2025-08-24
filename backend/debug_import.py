#!/usr/bin/env python3
"""
Debug import process
"""

import sys
import os

print("Debugging import process...")

# Add path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

print("Testing xhtml2pdf import directly...")
try:
    from xhtml2pdf import pisa
    print("✅ Direct xhtml2pdf import successful")
except Exception as e:
    print(f"❌ Direct xhtml2pdf import failed: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting import with the same structure as the module...")
try:
    # Simulate the exact import structure from the module
    import os
    import sys
    
    # Add the app directory to the Python path for imports
    sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
    
    try:
        from xhtml2pdf import pisa
        from xhtml2pdf.default import DEFAULT_FONT_CONFIG
        from xhtml2pdf.util import getColor
        XHTML2PDF_AVAILABLE = True
        print("✅ xhtml2pdf import successful in simulated module structure")
        print(f"XHTML2PDF_AVAILABLE: {XHTML2PDF_AVAILABLE}")
    except ImportError:
        XHTML2PDF_AVAILABLE = False
        pisa = None
        print("❌ xhtml2pdf import failed in simulated module structure")
        print(f"XHTML2PDF_AVAILABLE: {XHTML2PDF_AVAILABLE}")
        
except Exception as e:
    print(f"❌ Simulated module structure failed: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting the actual module file...")
try:
    # Read the module file and execute it line by line
    module_path = os.path.join(os.path.dirname(__file__), 'app', 'services', 'pdf_conversion_agent.py')
    
    with open(module_path, 'r') as f:
        lines = f.readlines()
    
    print(f"Module has {len(lines)} lines")
    
    # Execute the imports section
    exec_lines = []
    for i, line in enumerate(lines[:30]):  # First 30 lines
        if line.strip() and not line.strip().startswith('#'):
            exec_lines.append(line)
            if 'from xhtml2pdf import pisa' in line:
                print(f"Found xhtml2pdf import at line {i+1}")
                break
    
    # Execute the import section
    exec(''.join(exec_lines))
    print("✅ Module import section executed successfully")
    
except Exception as e:
    print(f"❌ Module file execution failed: {e}")
    import traceback
    traceback.print_exc()

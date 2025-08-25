#!/usr/bin/env python3
"""
Simple test to verify the new importlib approach works
"""

import importlib.util
from pathlib import Path

def test_simple_import():
    """Test if we can import the scheduler using importlib"""
    print("🧪 Testing simple importlib import...")
    
    try:
        # Get the path to the scheduler file
        backend_path = Path(__file__).parent
        scheduler_path = backend_path / "app" / "core" / "ROI backend" / "roi" / "services" / "scheduler.py"
        
        print(f"   Looking for scheduler at: {scheduler_path}")
        
        if not scheduler_path.exists():
            print(f"   ❌ Scheduler file not found!")
            return False
        
        print(f"   ✅ Scheduler file found!")
        
        # Load the module
        spec = importlib.util.spec_from_file_location("roi_scheduler", str(scheduler_path))
        if spec and spec.loader:
            print(f"   ✅ Spec created successfully")
            
            module = importlib.util.module_from_spec(spec)
            print(f"   ✅ Module created successfully")
            
            # Execute the module
            spec.loader.exec_module(module)
            print(f"   ✅ Module executed successfully")
            
            # Check if functions exist
            if hasattr(module, "start_scheduler"):
                print(f"   ✅ Found start_scheduler function")
            else:
                print(f"   ❌ Missing start_scheduler function")
                return False
                
            if hasattr(module, "stop_scheduler"):
                print(f"   ✅ Found stop_scheduler function")
            else:
                print(f"   ❌ Missing stop_scheduler function")
                return False
            
            print("🎉 Importlib import test passed!")
            return True
            
        else:
            print(f"   ❌ Failed to create spec")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_simple_import()

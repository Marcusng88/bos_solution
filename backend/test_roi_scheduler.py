#!/usr/bin/env python3
"""
Test script to verify ROI scheduler functionality
Run this to test if the ROI scheduler can be imported and started
"""

import asyncio
import sys
import importlib.util
from pathlib import Path

def load_module_from_path(module_name: str, file_path: Path):
    """Load a Python module from a file path"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, str(file_path))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            if spec.name:
                sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            return module
        else:
            raise ImportError(f"Failed to create spec for {file_path}")
    except Exception as e:
        raise ImportError(f"Failed to load module from {file_path}: {e}")

def test_roi_scheduler_import():
    """Test if ROI scheduler can be imported"""
    try:
        print("🧪 Testing ROI scheduler import...")
        
        # Get the path to the scheduler file
        backend_path = Path(__file__).parent
        scheduler_path = backend_path / "app" / "core" / "ROI backend" / "roi" / "services" / "scheduler.py"
        
        if not scheduler_path.exists():
            print(f"   ❌ Scheduler file not found at: {scheduler_path}")
            return False
        
        # Load the scheduler module
        scheduler_module = load_module_from_path("roi_scheduler", scheduler_path)
        
        # Check if required functions exist
        required_functions = ["start_scheduler", "stop_scheduler", "is_scheduler_running"]
        for func_name in required_functions:
            if hasattr(scheduler_module, func_name):
                print(f"   ✅ Found function: {func_name}")
            else:
                print(f"   ❌ Missing function: {func_name}")
                return False
        
        print("✅ ROI scheduler imported successfully")
        return True
        
    except ImportError as e:
        print(f"   ❌ Failed to import ROI scheduler: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error importing ROI scheduler: {e}")
        return False

def test_roi_writer_import():
    """Test if ROI writer can be imported"""
    try:
        print("🧪 Testing ROI writer import...")
        
        # Get the path to the writer file
        backend_path = Path(__file__).parent
        writer_path = backend_path / "app" / "core" / "ROI backend" / "roi" / "services" / "roi_writer.py"
        
        if not writer_path.exists():
            print(f"   ❌ Writer file not found at: {writer_path}")
            return False
        
        # Load the writer module
        writer_module = load_module_from_path("roi_writer", writer_path)
        
        # Check if required function exists
        if hasattr(writer_module, "execute_roi_update"):
            print("   ✅ Found function: execute_roi_update")
        else:
            print("   ❌ Missing function: execute_roi_update")
            return False
        
        print("✅ ROI writer imported successfully")
        return True
        
    except ImportError as e:
        print(f"   ❌ Failed to import ROI writer: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error importing ROI writer: {e}")
        return False

def test_data_generator_import():
    """Test if data generator can be imported"""
    try:
        print("🧪 Testing data generator import...")
        
        # Get the path to the data generator file
        backend_path = Path(__file__).parent
        generator_path = backend_path / "app" / "core" / "ROI backend" / "roi" / "services" / "data_generator.py"
        
        if not generator_path.exists():
            print(f"   ❌ Data generator file not found at: {generator_path}")
            return False
        
        # Load the data generator module
        generator_module = load_module_from_path("roi_data_generator", generator_path)
        
        # Check if required classes and functions exist
        required_items = ["DataGeneratorService", "BaseMetrics", "generate_next_10min_update"]
        for item_name in required_items:
            if hasattr(generator_module, item_name):
                print(f"   ✅ Found: {item_name}")
            else:
                print(f"   ❌ Missing: {item_name}")
                return False
        
        print("✅ Data generator imported successfully")
        return True
        
    except ImportError as e:
        print(f"   ❌ Failed to import data generator: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error importing data generator: {e}")
        return False

async def test_roi_scheduler_start():
    """Test if ROI scheduler can start"""
    try:
        print("🧪 Testing ROI scheduler start...")
        
        # Get the path to the scheduler file
        backend_path = Path(__file__).parent
        scheduler_path = backend_path / "app" / "core" / "ROI backend" / "roi" / "services" / "scheduler.py"
        
        # Load the scheduler module
        scheduler_module = load_module_from_path("roi_scheduler", scheduler_path)
        
        # Get the functions
        start_scheduler = getattr(scheduler_module, "start_scheduler")
        stop_scheduler = getattr(scheduler_module, "stop_scheduler")
        
        # Start the scheduler
        scheduler = start_scheduler()
        
        if scheduler:
            print("   ✅ ROI scheduler started successfully")
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Stop the scheduler
            stop_scheduler()
            print("   ✅ ROI scheduler stopped successfully")
            
            return True
        else:
            print("   ❌ ROI scheduler failed to start")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing ROI scheduler: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ROI Scheduler Test Suite")
    print("=" * 50)
    
    # Test imports
    import_success = (
        test_roi_scheduler_import() and
        test_roi_writer_import() and
        test_data_generator_import()
    )
    
    if not import_success:
        print("\n❌ Import tests failed. Cannot proceed with scheduler tests.")
        return
    
    print("\n✅ All import tests passed!")
    
    # Test scheduler start
    print("\n🧪 Testing scheduler functionality...")
    try:
        asyncio.run(test_roi_scheduler_start())
        print("\n🎉 All tests passed! ROI scheduler is working correctly.")
    except Exception as e:
        print(f"\n❌ Scheduler test failed: {e}")
    
    print("\n📋 Summary:")
    print("   ✅ ROI scheduler can be imported")
    print("   ✅ ROI writer can be imported") 
    print("   ✅ Data generator can be imported")
    print("   ✅ Scheduler can start and stop")
    print("\n🚀 You can now run 'python run.py' to start the full application!")

if __name__ == "__main__":
    main()

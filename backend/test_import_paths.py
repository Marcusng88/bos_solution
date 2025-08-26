#!/usr/bin/env python3
"""
Test script to verify import paths and directory structure
"""

import sys
from pathlib import Path

def test_directory_structure():
    """Test if the directory structure is correct"""
    print("🧪 Testing directory structure...")
    
    backend_path = Path(__file__).parent
    app_path = backend_path / "app"
    core_path = app_path / "core"
    roi_backend_path = core_path / "ROI backend"
    roi_path = roi_backend_path / "roi"
    services_path = roi_path / "services"
    
    print(f"   Backend path: {backend_path}")
    print(f"   App path: {app_path}")
    print(f"   Core path: {core_path}")
    print(f"   ROI backend path: {roi_backend_path}")
    print(f"   ROI path: {roi_path}")
    print(f"   Services path: {services_path}")
    
    # Check if directories exist
    paths_to_check = [
        ("app", app_path),
        ("core", core_path),
        ("ROI backend", roi_backend_path),
        ("roi", roi_path),
        ("services", services_path)
    ]
    
    all_exist = True
    for name, path in paths_to_check:
        if path.exists():
            print(f"   ✅ {name}: {path}")
        else:
            print(f"   ❌ {name}: {path} (MISSING)")
            all_exist = False
    
    return all_exist

def test_python_path():
    """Test Python path manipulation"""
    print("\n🧪 Testing Python path manipulation...")
    
    backend_path = Path(__file__).parent
    app_path = backend_path / "app"
    
    print(f"   Current Python path:")
    for i, path in enumerate(sys.path[:5]):  # Show first 5
        print(f"      {i}: {path}")
    
    print(f"   Adding app path: {app_path}")
    sys.path.insert(0, str(app_path))
    
    print(f"   Updated Python path:")
    for i, path in enumerate(sys.path[:5]):  # Show first 5
        print(f"      {i}: {path}")
    
    return True

def test_import_attempt():
    """Test if we can import the ROI modules"""
    print("\n🧪 Testing import attempt...")
    
    try:
        # Try to import the scheduler
        from core.ROI_backend.roi.services.scheduler import start_scheduler
        print("   ✅ Successfully imported start_scheduler")
        
        from core.ROI_backend.roi.services.roi_writer import execute_roi_update
        print("   ✅ Successfully imported execute_roi_update")
        
        from core.ROI_backend.roi.services.data_generator import DataGeneratorService
        print("   ✅ Successfully imported DataGeneratorService")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Import Path Test Suite")
    print("=" * 50)
    
    # Test directory structure
    if not test_directory_structure():
        print("\n❌ Directory structure test failed!")
        return
    
    # Test Python path manipulation
    test_python_path()
    
    # Test import attempt
    if test_import_attempt():
        print("\n🎉 All tests passed! Import paths are working correctly.")
        print("\n🚀 You can now run the main application!")
    else:
        print("\n❌ Import test failed. Check the error messages above.")

if __name__ == "__main__":
    main()

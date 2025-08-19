#!/usr/bin/env python3
"""
Setup script for isolated crawler environment
This script sets up the necessary dependencies for the isolated crawler to work
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install requirements for isolated crawler"""
    try:
        # Get the directory of this script
        script_dir = Path(__file__).parent
        requirements_file = script_dir / "isolated_crawler_requirements.txt"
        
        if not requirements_file.exists():
            print(f"❌ Requirements file not found: {requirements_file}")
            return False
        
        print("🔧 Installing isolated crawler requirements...")
        
        # Install requirements
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Isolated crawler requirements installed successfully")
            return True
        else:
            print(f"❌ Failed to install requirements: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        print("🔍 Checking isolated crawler dependencies...")
        
        # Check crawl4ai
        try:
            import crawl4ai
            print(f"✅ crawl4ai: {crawl4ai.__version__}")
        except ImportError:
            print("❌ crawl4ai not available")
            return False
        
        # Check aiohttp
        try:
            import aiohttp
            print(f"✅ aiohttp: {aiohttp.__version__}")
        except ImportError:
            print("❌ aiohttp not available")
            return False
        
        # Check beautifulsoup4
        try:
            import bs4
            print(f"✅ beautifulsoup4: {bs4.__version__}")
        except ImportError:
            print("❌ beautifulsoup4 not available")
            return False
        
        print("✅ All required dependencies are available")
        return True
        
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up isolated crawler environment...")
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed during requirements installation")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Setup failed during dependency check")
        sys.exit(1)
    
    print("🎉 Isolated crawler environment setup completed successfully!")
    print("\nThe isolated crawler is now ready to use.")
    print("It will run crawl4ai in a separate Python process to avoid conflicts.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script to install AI dependencies for the BOS Solution backend
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Installing AI Dependencies for BOS Solution Backend")
    print("=" * 60)
    
    # Check if we're in the backend directory
    if not os.path.exists("requirements.txt"):
        print("❌ Error: Please run this script from the backend directory")
        sys.exit(1)
    
    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Warning: Failed to upgrade pip, continuing anyway...")
    
    # Install core packages first (without version conflicts)
    core_packages = [
        "fastapi",
        "uvicorn", 
        "sqlalchemy",
        "pydantic",
        "python-dotenv",
        "httpx",
        "asyncpg"
    ]
    
    print("\n📦 Installing core packages...")
    for package in core_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: Failed to install {package}, continuing...")
    
    # Install AI packages with compatible versions
    print("\n🤖 Installing AI packages...")
    ai_packages = [
        "langchain==0.2.16",
        "langchain-community==0.2.16",
        "google-generativeai==0.8.3"
    ]
    
    for package in ai_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"❌ Failed to install {package}")
            sys.exit(1)
    
    # Try to install langchain-google-genai separately
    print("\n🔧 Installing langchain-google-genai...")
    if not run_command("pip install langchain-google-genai", "Installing langchain-google-genai"):
        print("⚠️  Warning: Failed to install langchain-google-genai with specific version")
        print("🔄 Trying to install latest compatible version...")
        if not run_command("pip install langchain-google-genai --no-deps", "Installing langchain-google-genai (no deps)"):
            print("❌ Failed to install langchain-google-genai")
            print("💡 This might be due to version conflicts. The AI functionality may still work with google-generativeai directly.")
    
    # Install remaining packages from requirements.txt (skip AI packages)
    print("\n📋 Installing remaining packages...")
    try:
        with open("requirements.txt", "r") as f:
            lines = f.readlines()
        
        # Filter out AI packages we already installed
        ai_package_names = ["langchain", "langchain-google-genai", "langchain-community", "google-generativeai"]
        remaining_packages = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                # Check if this is an AI package
                is_ai_package = any(ai_name in line for ai_name in ai_package_names)
                if not is_ai_package:
                    remaining_packages.append(line)
        
        # Install remaining packages
        for package in remaining_packages:
            try:
                if not run_command(f"pip install {package}", f"Installing {package}"):
                    print(f"⚠️  Warning: Failed to install {package}, continuing...")
            except Exception as e:
                print(f"⚠️  Warning: Failed to install {package}: {e}")
                continue
                
    except Exception as e:
        print(f"⚠️  Warning: Could not read requirements.txt: {e}")
    
    print("\n" + "=" * 60)
    print("✅ AI Dependencies Installation Complete!")
    print("\n📋 Next steps:")
    print("1. Make sure your .env file has GEMINI_API_KEY set")
    print("2. Run: python run.py")
    print("3. Test the AI endpoints at http://localhost:8000/docs")
    
    print("\n🔍 Verification:")
    print("Checking installed packages...")
    run_command("pip list | grep -E '(langchain|google-generativeai)'", "Checking AI packages")

if __name__ == "__main__":
    main()

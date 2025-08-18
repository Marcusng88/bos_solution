#!/usr/bin/env python3
"""
Script to install LangChain dependencies for the BOS Solution backend
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
    print("🚀 Installing LangChain Dependencies for BOS Solution Backend")
    print("=" * 60)
    
    # Check if we're in the backend directory
    if not os.path.exists("requirements.txt"):
        print("❌ Error: Please run this script from the backend directory")
        sys.exit(1)
    
    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Warning: Failed to upgrade pip, continuing anyway...")
    
    # Step 1: Install core packages first
    print("\n📦 Step 1: Installing core packages...")
    core_packages = [
        "fastapi",
        "uvicorn", 
        "sqlalchemy",
        "pydantic",
        "python-dotenv",
        "httpx",
        "asyncpg"
    ]
    
    for package in core_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: Failed to install {package}, continuing...")
    
    # Step 2: Install Google Generative AI first (required by langchain-google-genai)
    print("\n🤖 Step 2: Installing Google Generative AI...")
    if not run_command("pip install google-generativeai==0.8.3", "Installing google-generativeai"):
        print("❌ Failed to install google-generativeai")
        sys.exit(1)
    
    # Step 3: Install LangChain packages in specific order
    print("\n🔗 Step 3: Installing LangChain packages...")
    
    # Install langchain-community first
    if not run_command("pip install langchain-community==0.0.10", "Installing langchain-community"):
        print("❌ Failed to install langchain-community")
        sys.exit(1)
    
    # Install langchain core
    if not run_command("pip install langchain==0.1.0", "Installing langchain"):
        print("❌ Failed to install langchain")
        sys.exit(1)
    
    # Install langchain-google-genai last
    if not run_command("pip install langchain-google-genai==0.0.11", "Installing langchain-google-genai"):
        print("❌ Failed to install langchain-google-genai")
        print("🔄 Trying alternative approach...")
        
        # Try installing without dependencies
        if not run_command("pip install langchain-google-genai==0.0.11 --no-deps", "Installing langchain-google-genai (no deps)"):
            print("❌ Failed to install langchain-google-genai even without deps")
            print("💡 This might be due to version conflicts. Trying latest version...")
            
            # Try latest version
            if not run_command("pip install langchain-google-genai", "Installing latest langchain-google-genai"):
                print("❌ Failed to install langchain-google-genai")
                sys.exit(1)
    
    # Step 4: Install remaining packages
    print("\n📋 Step 4: Installing remaining packages...")
    remaining_packages = [
        "alembic",
        "python-jose",
        "python-multipart", 
        "passlib",
        "bcrypt",
        "pytest",
        "pytest-asyncio"
    ]
    
    for package in remaining_packages:
        try:
            if not run_command(f"pip install {package}", f"Installing {package}"):
                print(f"⚠️  Warning: Failed to install {package}, continuing...")
        except Exception as e:
            print(f"⚠️  Warning: Failed to install {package}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print("✅ LangChain Dependencies Installation Complete!")
    print("\n📋 Next steps:")
    print("1. Make sure your .env file has GEMINI_API_KEY set")
    print("2. Run: python run.py")
    print("3. Test the AI endpoints at http://localhost:8000/docs")
    
    print("\n🔍 Verification:")
    print("Checking installed packages...")
    run_command("pip list | grep -E '(langchain|google-generativeai)'", "Checking LangChain packages")
    
    print("\n🧪 Testing LangChain import...")
    try:
        import langchain
        import langchain_google_genai
        import langchain_community
        print("✅ All LangChain packages imported successfully!")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Some packages may not be installed correctly")

if __name__ == "__main__":
    main()

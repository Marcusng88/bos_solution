#!/usr/bin/env python3
"""
Setup script for Gemini API key configuration
"""

import os
from pathlib import Path

def setup_gemini():
    """Setup Gemini API key in .env file"""
    
    print("🔧 Setting up Gemini API Key")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    env_example_file = Path("env.example")
    
    if not env_example_file.exists():
        print("❌ env.example file not found!")
        return False
    
    # Read env.example
    with open(env_example_file, 'r') as f:
        env_content = f.read()
    
    # Check if .env already exists
    if env_file.exists():
        print("⚠️  .env file already exists")
        with open(env_file, 'r') as f:
            current_env = f.read()
        
        if "GEMINI_API_KEY=your_gemini_api_key_here" in current_env or "GEMINI_API_KEY=" not in current_env:
            print("📝 Updating existing .env file with Gemini API key...")
            
            # Replace the placeholder
            if "GEMINI_API_KEY=your_gemini_api_key_here" in current_env:
                current_env = current_env.replace("GEMINI_API_KEY=your_gemini_api_key_here", "GEMINI_API_KEY=YOUR_ACTUAL_API_KEY_HERE")
            else:
                # Add the line if it doesn't exist
                lines = current_env.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith("# API Keys for LLMs and services"):
                        lines.insert(i + 1, "GEMINI_API_KEY=YOUR_ACTUAL_API_KEY_HERE")
                        break
                current_env = '\n'.join(lines)
            
            with open(env_file, 'w') as f:
                f.write(current_env)
        else:
            print("✅ Gemini API key already configured in .env file")
            return True
    else:
        print("📝 Creating new .env file...")
        # Replace the placeholder in env.example content
        env_content = env_content.replace("GEMINI_API_KEY=your_gemini_api_key_here", "GEMINI_API_KEY=YOUR_ACTUAL_API_KEY_HERE")
        
        with open(env_file, 'w') as f:
            f.write(env_content)
    
    print("\n📋 Next Steps:")
    print("1. Get your Gemini API key from: https://makersuite.google.com/app/apikey")
    print("2. Open the .env file and replace 'YOUR_ACTUAL_API_KEY_HERE' with your actual API key")
    print("3. Restart your backend server")
    print("\nExample .env line:")
    print("GEMINI_API_KEY=AIzaSyC...your_actual_key_here...")
    
    return True

if __name__ == "__main__":
    setup_gemini()

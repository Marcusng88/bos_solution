#!/usr/bin/env python3
"""
Script to update Gemini API key in .env file
"""

import os
import sys

def update_gemini_key():
    """Update Gemini API key in .env file"""
    
    print("🔑 Gemini API Key Updater")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return False
    
    # Read current .env file
    with open('.env', 'r') as f:
        content = f.read()
    
    # Get new API key from user
    print("\n📋 Please enter your new Gemini API key:")
    print("(Get it from: https://makersuite.google.com/app/apikey)")
    print("(The key should start with 'AIzaSy...')")
    
    new_key = input("\nEnter your Gemini API key: ").strip()
    
    if not new_key:
        print("❌ No API key provided!")
        return False
    
    if not new_key.startswith('AIzaSy'):
        print("❌ Invalid API key format! Should start with 'AIzaSy...'")
        return False
    
    # Replace the old key
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('GEMINI_API_KEY='):
            updated_lines.append(f'GEMINI_API_KEY={new_key}')
        else:
            updated_lines.append(line)
    
    # Write back to .env file
    with open('.env', 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"\n✅ Gemini API key updated successfully!")
    print(f"New key: {new_key[:20]}...")
    print("\n🔄 Please restart your backend server for changes to take effect.")
    
    return True

if __name__ == "__main__":
    update_gemini_key()

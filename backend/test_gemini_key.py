#!/usr/bin/env python3
"""
Test script to verify Gemini API key is working
"""

import os
import sys

def test_gemini_key():
    """Test if Gemini API key is valid"""
    
    print("🧪 Testing Gemini API Key")
    print("=" * 30)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ No GEMINI_API_KEY found in .env file")
        return False
    
    print(f"🔑 Found API key: {api_key[:20]}...")
    
    # Try to import and configure Gemini
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import google.generativeai: {e}")
        print("Please install: pip install google-generativeai")
        return False
    
    # Configure Gemini
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini configured successfully")
    except Exception as e:
        print(f"❌ Failed to configure Gemini: {e}")
        return False
    
    # Test with a simple request
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini model loaded successfully")
        
        # Simple test prompt
        response = model.generate_content("Hello, this is a test. Please respond with 'API key is working!'")
        
        if response.text:
            print("✅ API key is working! Test response received.")
            print(f"Response: {response.text}")
            return True
        else:
            print("❌ No response received from Gemini")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test Gemini API: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_key()
    if success:
        print("\n🎉 Gemini API key is valid and working!")
    else:
        print("\n💥 Gemini API key test failed. Please check your key.")

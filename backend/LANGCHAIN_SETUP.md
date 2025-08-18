# LangChain Setup Guide

This guide will help you install LangChain with the correct versions to avoid dependency conflicts.

## 🚨 The Problem

The issue you encountered was due to version incompatibilities between:
- `langchain==0.2.16` (too new)
- `langchain-google-genai==2.1.9` (too new)
- `langchain-community==0.2.16` (too new)

These newer versions have breaking changes and dependency conflicts.

## ✅ The Solution

We're using compatible older versions that work together:
- `langchain==0.1.0`
- `langchain-google-genai==0.0.11`
- `langchain-community==0.0.10`
- `google-generativeai==0.8.3`

## 🚀 Installation Methods

### Method 1: Use the LangChain Installation Script (Recommended)

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux

# Run the LangChain installation script
python install_langchain.py
```

### Method 2: Manual Installation

If the script doesn't work, install packages manually in this specific order:

```bash
# Step 1: Install core packages
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv httpx asyncpg

# Step 2: Install Google Generative AI first
pip install google-generativeai==0.8.3

# Step 3: Install LangChain packages in order
pip install langchain-community==0.0.10
pip install langchain==0.1.0
pip install langchain-google-genai==0.0.11

# Step 4: Install remaining packages
pip install alembic python-jose python-multipart passlib bcrypt pytest pytest-asyncio
```

### Method 3: Clean Install (If you have conflicts)

```bash
# Deactivate and remove virtual environment
deactivate
rm -rf venv  # or delete venv folder manually

# Create new virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux

# Upgrade pip
pip install --upgrade pip

# Then follow Method 1 or 2
```

## 🔍 Verification

After installation, verify everything works:

```bash
# Check installed packages
pip list | grep -E "(langchain|google-generativeai)"

# Test imports
python -c "
import langchain
import langchain_google_genai
import langchain_community
print('✅ All LangChain packages imported successfully!')
"
```

## 🚀 Start the Backend

```bash
# Start the backend
python run.py
```

You should see:
```
🚀 Starting BOS Solution Backend Server...
📍 Host: 0.0.0.0
🔌 Port: 8000
🔄 Reload: False
✅ Server started successfully!
```

## 🧪 Test LangChain Functionality

1. **Start Frontend**: `cd frontend && npm run dev`
2. **Open Browser**: Go to `http://localhost:3000`
3. **Sign In**: Use Clerk authentication
4. **Test AI**: Go to Optimization → AI Insights
5. **Test Chat**: Use the floating AI chat widget

## 📋 What's Different with LangChain

The AI service now uses LangChain's features:

- **ChatGoogleGenerativeAI**: LangChain's wrapper for Gemini
- **SystemMessage & HumanMessage**: LangChain's message types
- **ainvoke()**: Async invocation for better performance
- **Structured prompts**: Using LangChain's prompt templates

## 🔧 Troubleshooting

### If you get import errors:

```bash
# Check what's installed
pip list | grep langchain

# If versions are wrong, uninstall and reinstall
pip uninstall langchain langchain-google-genai langchain-community
pip install langchain==0.1.0 langchain-google-genai==0.0.11 langchain-community==0.0.10
```

### If you get dependency conflicts:

```bash
# Try installing with --no-deps
pip install langchain-google-genai==0.0.11 --no-deps

# Or try the latest compatible version
pip install langchain-google-genai
```

### If the backend won't start:

```bash
# Check the error message
python run.py

# Common issues:
# 1. Missing GEMINI_API_KEY in .env file
# 2. Wrong package versions
# 3. Import errors in ai_service.py
```

## 📚 LangChain Features Used

1. **ChatGoogleGenerativeAI**: Wrapper for Gemini API
2. **SystemMessage & HumanMessage**: Structured message types
3. **Async support**: Using `ainvoke()` for better performance
4. **Error handling**: LangChain's built-in error handling
5. **Temperature control**: Configurable creativity levels
6. **Token limits**: Configurable response length

## 🎯 Expected Results

After successful installation:

- ✅ Backend starts without errors
- ✅ LangChain imports work correctly
- ✅ AI chat widget responds using LangChain
- ✅ AI insights panel works with LangChain
- ✅ All existing features still work
- ✅ Better error handling and performance

## 🆘 Still Having Issues?

If you're still experiencing problems:

1. **Check Python version**: Make sure you're using Python 3.8+
2. **Check pip version**: `pip --version`
3. **Check virtual environment**: Make sure it's activated
4. **Check API key**: Verify your `.env` file has `GEMINI_API_KEY`
5. **Check package versions**: `pip list | grep langchain`

Run this to test everything:
```bash
python -c "
try:
    import langchain
    import langchain_google_genai
    import langchain_community
    from langchain_google_genai import ChatGoogleGenerativeAI
    print('✅ All LangChain components work!')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

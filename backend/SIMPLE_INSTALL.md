# Simple Installation Guide - No Dependency Conflicts

This guide will help you install the AI dependencies without conflicts.

## 🚀 Quick Fix - Manual Installation

### Step 1: Install Core Dependencies

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux

# Install core packages first
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv httpx asyncpg
```

### Step 2: Install AI Dependencies

```bash
# Install Google Generative AI (this is what we actually need)
pip install google-generativeai==0.8.3

# Install LangChain packages (optional, for future use)
pip install langchain==0.2.16
pip install langchain-community==0.2.16
```

### Step 3: Install Remaining Packages

```bash
# Install other packages individually to avoid conflicts
pip install alembic
pip install python-jose
pip install python-multipart
pip install passlib
pip install bcrypt
pip install pytest
pip install pytest-asyncio
```

### Step 4: Verify Installation

```bash
# Check if key packages are installed
pip list | grep -E "(google-generativeai|fastapi|uvicorn)"
```

You should see:
- google-generativeai
- fastapi
- uvicorn

## 🎯 What's Changed

1. **Removed LangChain dependency**: The AI service now uses `google-generativeai` directly
2. **No more version conflicts**: We avoid the problematic `langchain-google-genai` package
3. **Simpler installation**: Install packages individually instead of using requirements.txt

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

## 🧪 Test the AI Functionality

1. **Start Frontend**: `cd frontend && npm run dev`
2. **Open Browser**: Go to `http://localhost:3000`
3. **Sign In**: Use Clerk authentication
4. **Test AI**: Go to Optimization → AI Insights

## 🔧 If You Still Get Errors

### Option 1: Clean Install
```bash
# Remove virtual environment and recreate
deactivate
rm -rf venv  # or delete venv folder manually
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
```

Then follow the steps above.

### Option 2: Use Only Google Generative AI
If you still get conflicts, you can use just the Google Generative AI package:

```bash
pip install google-generativeai==0.8.3
```

The AI service has been updated to work with just this package.

## 📋 What Works Now

- ✅ Backend starts without import errors
- ✅ AI service uses Google Generative AI directly
- ✅ No dependency conflicts
- ✅ AI chat and insights functionality
- ✅ All existing features still work

## 🆘 Still Having Issues?

If you're still experiencing problems:

1. **Check Python version**: Make sure you're using Python 3.8+
2. **Check pip version**: `pip --version`
3. **Check virtual environment**: Make sure it's activated
4. **Check API key**: Verify your `.env` file has `GEMINI_API_KEY`

Run this to test:
```bash
python -c "import google.generativeai; print('✅ Google Generative AI works!')"
```

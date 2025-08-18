# Quick Setup Guide - Fix All Issues

This guide will help you resolve all the current errors and get the AI functionality working.

## 🚨 Current Issues Fixed:

1. ✅ **Backend Import Error**: Added missing `get_current_user_id` function
2. ✅ **Package Version Error**: Fixed `langchain-google-genai` version
3. ✅ **Frontend Authentication Error**: Made AI components conditional on auth
4. ✅ **Missing Dependencies**: Added `google-generativeai` package

## 🚀 Step-by-Step Fix:

### Step 1: Install Dependencies Properly

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if not already activated)
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux

# Run the installation script
python install_ai_deps.py
```

### Step 2: Verify Environment Variables

Make sure your `backend/.env` file has:

```bash
# AI Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### Step 3: Start Backend

```bash
# Always use this command to start the backend
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

### Step 4: Start Frontend

In a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Start the development server
npm run dev
```

### Step 5: Test the Application

1. **Open Browser**: Go to `http://localhost:3000`
2. **Sign In**: Use Clerk authentication
3. **Navigate to Optimization**: Go to the Optimization section
4. **Test AI Insights**: Click on "AI Insights" tab
5. **Test AI Chat**: Look for the floating chat button (bottom-right)

## 🔧 Troubleshooting

### If Backend Still Won't Start:

```bash
# Check if all packages are installed
pip list | grep langchain

# Should show:
# langchain
# langchain-google-genai
# langchain-community
# google-generativeai
```

### If Frontend Shows Authentication Error:

1. Make sure you're signed in with Clerk
2. Check browser console for any remaining errors
3. The AI chat widget will only appear when signed in

### If AI Endpoints Don't Work:

1. Verify your Gemini API key is correct
2. Test the API directly: `http://localhost:8000/docs`
3. Check backend logs for any errors

## 🧪 Test Commands

### Test Backend API:

```bash
# Test AI analysis endpoint
curl -X POST "http://localhost:8000/api/v1/ai-insights/analyze" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test_user" \
  -d '{"include_competitors": true, "include_monitoring": true}'

# Test AI chat endpoint
curl -X POST "http://localhost:8000/api/v1/ai-insights/chat" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test_user" \
  -d '{"message": "How are my campaigns performing?"}'
```

## 📋 What's Fixed:

1. **Backend Import Error**: ✅ Added `get_current_user_id` function
2. **Package Version**: ✅ Updated to `langchain-google-genai==2.1.9`
3. **Frontend Auth**: ✅ AI components now check authentication
4. **Missing Dependencies**: ✅ Added `google-generativeai==0.8.3`
5. **Installation Script**: ✅ Created `install_ai_deps.py` for easy setup

## 🎯 Expected Results:

After following this guide:

- ✅ Backend starts without errors
- ✅ Frontend loads without authentication errors
- ✅ AI chat widget appears when signed in
- ✅ AI insights panel works in Optimization section
- ✅ AI scan button shows progress and results

## 🆘 Still Having Issues?

If you're still experiencing problems:

1. **Check Logs**: Look at both backend and frontend console logs
2. **Verify API Key**: Make sure your Gemini API key is valid
3. **Database**: Ensure your database is running and accessible
4. **Network**: Check if ports 3000 and 8000 are available

Run these commands to get more information:

```bash
# Backend logs
python run.py

# Frontend logs (in another terminal)
cd frontend && npm run dev
```

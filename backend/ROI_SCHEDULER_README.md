# ROI Scheduler Integration

## 🎯 Overview

The ROI scheduler is now fully integrated into your main FastAPI application. When you run `python run.py`, everything starts together:

1. **FastAPI Backend Server** - Your main API
2. **Database Connection** - Supabase connection
3. **ROI Scheduler** - Runs every 10 minutes automatically
4. **All API Endpoints** - Including ROI endpoints

## 🚀 How to Start Everything

### Option 1: Use run.py (Recommended)
```bash
cd bos_solution/backend
python run.py
```

This will:
- Start the FastAPI server on port 8000
- Initialize the database connection
- Start the ROI scheduler automatically
- Show you what's being initialized

### Option 2: Use main.py directly
```bash
cd bos_solution/backend
python main.py
```

## 📊 What the ROI Scheduler Does

### Every 10 Minutes:
1. **Fetches latest 3 rows** from your database (1 YouTube + 1 Facebook + 1 Instagram)
2. **Applies growth multipliers** to existing metrics (views, likes, comments, etc.)
3. **Calculates new financial metrics** (ROI, revenue, ad spend)
4. **Inserts 3 new rows** with updated metrics

### Example Growth:
- **YouTube**: views 1000 → 1002 (+2), likes 150 → 151 (+1)
- **Facebook**: views 800 → 801 (+1), likes 200 → 201 (+1)  
- **Instagram**: views 1200 → 1203 (+3), likes 300 → 302 (+2)

## 🧪 Testing the Integration

Before running the full application, you can test if everything works:

```bash
cd bos_solution/backend
python test_roi_scheduler.py
```

This will verify:
- ✅ ROI scheduler can be imported
- ✅ ROI writer can be imported
- ✅ Data generator can be imported
- ✅ Scheduler can start and stop

## 📁 File Structure

```
backend/
├── main.py                    # Main FastAPI app + ROI scheduler integration
├── run.py                     # Quick start script
├── test_roi_scheduler.py      # Test script for ROI components
├── app/
│   └── core/
│       └── ROI backend/       # ROI system
│           └── roi/
│               └── services/
│                   ├── scheduler.py      # 10-minute scheduler
│                   ├── roi_writer.py     # Live update logic
│                   └── data_generator.py # Growth calculations
```

## 🔧 Configuration

The ROI scheduler runs automatically with these settings:
- **Interval**: Every 10 minutes
- **User**: Automatically detects the most recent user
- **Platforms**: YouTube, Facebook, Instagram
- **Growth**: Realistic multipliers based on content lifecycle

## 📈 What You'll See

When you start the application, you'll see:

```
🚀 Starting BOS Solution Backend
==================================================
🌐 Server: 0.0.0.0:8000
📚 API Docs: http://localhost:8000/docs
🔄 Auto-reload: Enabled
📊 Log Level: info
==================================================
📋 What will be initialized:
   ✅ FastAPI application
   ✅ Database connection
   ✅ ROI scheduler (10-minute intervals)
   ✅ All API endpoints
   ✅ CORS middleware
==================================================
🚀 Starting BOS Solution v1.0.0
🌐 Host: 0.0.0.0
🔌 Port: 8000
🐛 Debug: True
📊 ROI Scheduler: Will start automatically
✅ Database initialized successfully in supabase mode
🚀 Starting ROI scheduler...
✅ ROI scheduler started successfully
```

## 🚨 Troubleshooting

### If ROI scheduler fails to start:
1. Check if you have the required dependencies:
   ```bash
   pip install apscheduler
   ```

2. Verify the file paths are correct:
   ```
   app/core/ROI backend/roi/services/
   ```

3. Run the test script to identify issues:
   ```bash
   python test_roi_scheduler.py
   ```

### If you see import errors:
- Make sure you're in the `backend` directory
- Check that all ROI files exist in the correct locations
- Verify Python path includes the `app` directory

## 🎉 Benefits of Integration

1. **Single Command**: `python run.py` starts everything
2. **Automatic Startup**: ROI scheduler starts with your app
3. **Proper Cleanup**: Scheduler stops when app shuts down
4. **Error Handling**: Graceful fallbacks if scheduler fails
5. **Logging**: Integrated logging with your main application

## 📝 Next Steps

1. **Test the integration**: `python test_roi_scheduler.py`
2. **Start the full app**: `python run.py`
3. **Monitor the logs** to see ROI updates every 10 minutes
4. **Check your database** to see the continuous metric growth

Your ROI system is now fully integrated and will run automatically! 🚀

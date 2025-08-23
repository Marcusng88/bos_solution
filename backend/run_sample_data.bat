@echo off
echo 🎯 Starting ROI Sample Data Generation...
echo.

cd /d "%~dp0"

echo 📋 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found
echo.

echo 🚀 Running sample data generation script...
python populate_roi_sample_data.py

echo.
echo ✅ Sample data generation completed!
echo 🎉 Your ROI dashboard should now have beautiful data to display
echo.
pause


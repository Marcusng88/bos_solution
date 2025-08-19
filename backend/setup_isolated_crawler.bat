@echo off
echo Setting up isolated crawler environment...
echo.

cd /d "%~dp0app\services\monitoring\agents\sub_agents"

echo Installing isolated crawler requirements...
python setup_isolated_crawler.py

echo.
echo Setup completed! You can now test the isolated crawler.
echo.
pause

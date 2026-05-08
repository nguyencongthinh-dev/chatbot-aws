@echo off
echo ========================================
echo Starting GeekBrain AI Servers
echo ========================================
echo.

cd data_package\scripts

echo [1/2] Starting Monitoring API on port 8000...
start "Monitoring API" cmd /k "uv run python monitoring_api.py"
timeout /t 3 /nobreak >nul

echo [2/2] Starting Web App on port 3002...
start "Web App" cmd /k "uv run uvicorn web_app:app --reload --port 3002"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Servers started successfully!
echo ========================================
echo.
echo Monitoring API: http://localhost:8000
echo Web App:        http://localhost:3002
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul

start http://localhost:3002

echo.
echo Press any key to stop all servers...
pause >nul

echo.
echo Stopping servers...
taskkill /FI "WindowTitle eq Monitoring API*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Web App*" /T /F >nul 2>&1

echo Done!

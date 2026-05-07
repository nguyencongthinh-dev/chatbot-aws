@echo off
echo ========================================
echo RESTARTING GeekBrain AI App
echo ========================================
echo.

echo [1/3] Stopping old processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq web_app*" 2>nul
taskkill /F /IM uvicorn.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/3] Starting monitoring API (port 8000)...
cd data_package\scripts
start "Monitoring API" cmd /k "python monitoring_api.py"
timeout /t 3 /nobreak >nul

echo [3/3] Starting web app (port 3002)...
start "GeekBrain Web App" cmd /k "python web_app.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo ✅ DONE! App restarted successfully
echo ========================================
echo.
echo Web App: http://localhost:3002
echo Monitoring API: http://localhost:8000
echo.
echo Press any key to close this window...
pause >nul

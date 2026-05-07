@echo off
echo ╔══════════════════════════════════════════════════════════════╗
echo ║         GeekBrain AI - Automated Test Runner                 ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if web server is running
curl -s http://localhost:3002 >nul 2>&1
if errorlevel 1 (
    echo ❌ Web server not running!
    echo.
    echo Start server first:
    echo   cd data_package\scripts
    echo   uv run uvicorn web_app:app --port 3002
    echo.
    pause
    exit /b 1
)

REM Check if monitoring API is running
curl -s http://localhost:8000/services >nul 2>&1
if errorlevel 1 (
    echo ⚠️  WARNING: Monitoring API not running on port 8000
    echo    L3 tests may fail. Start with:
    echo    cd data_package\scripts
    echo    uv run uvicorn monitoring_api:app --port 8000
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
)

echo ✓ Web server running on port 3002
echo ✓ Starting automated tests...
echo.

cd data_package\scripts
uv run python test_all_levels.py

echo.
echo ═══════════════════════════════════════════════════════════════
echo Test complete! Review results above.
echo ═══════════════════════════════════════════════════════════════
pause

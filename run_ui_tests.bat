@echo off
echo ╔══════════════════════════════════════════════════════════════╗
echo ║         GeekBrain AI - UI Test Runner                        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if Selenium is installed
python -c "import selenium" 2>nul
if errorlevel 1 (
    echo [INFO] Selenium not installed. Installing...
    pip install selenium webdriver-manager
    if errorlevel 1 (
        echo [ERROR] Failed to install Selenium
        pause
        exit /b 1
    )
)

REM Check if Chrome is installed
where chrome >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Chrome browser not found
    echo Please install Google Chrome to run UI tests
    echo Download from: https://www.google.com/chrome/
    pause
    exit /b 1
)

REM Check if web server is running
curl -s http://localhost:3002 >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Web server not running on port 3002
    echo Start with: uv run uvicorn web_app:app --port 3002
    pause
    exit /b 1
)

echo [OK] Prerequisites met
echo.
echo Starting UI tests...
echo.

cd data_package\scripts
python test_ui.py

echo.
echo ═══════════════════════════════════════════════════════════════
echo UI tests complete!
echo Check screenshots/ directory for captured images
echo ═══════════════════════════════════════════════════════════════
pause

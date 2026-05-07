#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         GeekBrain AI - Automated Test Runner                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if web server is running
if ! curl -s http://localhost:3002 > /dev/null 2>&1; then
    echo "❌ Web server not running!"
    echo ""
    echo "Start server first:"
    echo "  cd data_package/scripts"
    echo "  uv run uvicorn web_app:app --port 3002"
    echo ""
    exit 1
fi

# Check if monitoring API is running
if ! curl -s http://localhost:8000/services > /dev/null 2>&1; then
    echo "⚠️  WARNING: Monitoring API not running on port 8000"
    echo "   L3 tests may fail. Start with:"
    echo "   cd data_package/scripts"
    echo "   uv run uvicorn monitoring_api:app --port 8000"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✓ Web server running on port 3002"
echo "✓ Starting automated tests..."
echo ""

cd data_package/scripts
uv run python test_all_levels.py

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Test complete! Review results above."
echo "═══════════════════════════════════════════════════════════════"

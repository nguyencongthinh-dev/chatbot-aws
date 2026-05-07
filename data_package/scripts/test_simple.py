"""Simple test without websocket - just check if system works"""
import sys

print("="*60)
print("SIMPLE SYSTEM CHECK")
print("="*60)

# Test 1: Check files exist
print("\n[1] Checking files...")
import os
files_ok = all([
    os.path.exists('web_app.py'),
    os.path.exists('geekbrain.db'),
    os.path.exists('../knowledge_base')
])
print(f"   Files: {'OK' if files_ok else 'MISSING'}")

# Test 2: Check database
print("\n[2] Checking database...")
import sqlite3
try:
    conn = sqlite3.connect('geekbrain.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM monthly_costs")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"   Database: OK ({count} rows in monthly_costs)")
except Exception as e:
    print(f"   Database: FAIL - {e}")
    sys.exit(1)

# Test 3: Check server
print("\n[3] Checking web server...")
import requests
try:
    r = requests.get('http://localhost:3002', timeout=5)
    print(f"   Web server: OK (status {r.status_code})")
except:
    print("   Web server: NOT RUNNING")
    print("   Start with: uv run uvicorn web_app:app --port 3002")
    sys.exit(1)

# Test 4: Check monitoring API
print("\n[4] Checking monitoring API...")
try:
    r = requests.get('http://localhost:8000/services', timeout=5)
    print(f"   Monitoring API: OK (status {r.status_code})")
except:
    print("   Monitoring API: NOT RUNNING (L3 will fail)")

print("\n" + "="*60)
print("SYSTEM READY FOR MANUAL TESTING")
print("="*60)
print("\nOpen http://localhost:3002 and test these questions:")
print("\nL1: Who is the Team Platform lead?")
print("L2: What is the current API rate limit for PaymentGW?")
print("L3: What was PaymentGW's total cost in Q1 2026?")
print("L4: (4-turn conversation)")
print("    1. Which service had highest cost March 2026?")
print("    2. Why did its costs spike?")
print("    3. Which team is responsible for it?")
print("    4. What was their most recent incident?")
print("L5: Investigate PaymentGW performance issues")
print("\n" + "="*60)

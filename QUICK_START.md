# 🚀 Quick Start Guide

## Start Application

```bash
start_servers.bat
```

Opens:
- Web App: http://localhost:3002
- Monitoring API: http://localhost:8000

## Restart Application

```bash
restart_app.bat
```

Or manually:
```bash
taskkill /F /IM python.exe /IM uvicorn.exe
start_servers.bat
```

## After Code Changes

1. Restart server: `restart_app.bat`
2. Hard refresh browser: `Ctrl + Shift + R`

## Test Questions

- "What is PaymentGW?"
- "When was the last security incident?"
- "Show me Q2 2026 capacity planning"

## Features

✅ AI Chat with RAG
✅ Beautiful Markdown Rendering
✅ Inline Citations [1], [2], [3]
✅ Citation Cards (click to see full doc)
✅ View Trace (debug info)
✅ Chat History (auto-save)

## Troubleshooting

**Port in use?**
```bash
netstat -ano | findstr :3002
taskkill /F /PID <PID>
```

**Markdown not rendering?**
```bash
restart_app.bat
# Then: Ctrl + Shift + R
```

---

See **README.md** for full documentation.
See **TESTING.md** for test guide.

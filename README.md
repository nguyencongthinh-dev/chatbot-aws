# GeekBrain AI - Complete Guide

## 🚀 Quick Start

### Performance Note ⚡
**NEW in v1.3.0**: Phase 1 + Phase 2 + Phase 3 optimizations!
- **125x faster** RAG search (500ms → 4ms)
- **11.7x faster** investigations (200ms → 17ms)
- **1500x faster** repeated questions (1500ms → 0.134ms)
- **3-5000x faster** total response time (depending on cache hit)
- **50-70% fewer** API calls

**6 optimizations implemented:**
1. ✅ KB Cache (memory)
2. ✅ RAG Cache (LRU)
3. ✅ Smart Rewriting
4. ✅ DB Connection Pool
5. ✅ Parallel Execution
6. ✅ Response Caching

See `PERFORMANCE_OPTIMIZATION.md`, `PHASE2_RESULTS.md`, and `PHASE3_RESULTS.md` for details.

### 1. Setup environment variables
```bash
# Copy example file
cp .env.example .env

# Edit .env and fill in your AWS credentials:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - AWS_SESSION_TOKEN (optional, for temporary credentials)
# - KNOWLEDGE_BASE_ID
```

See `.env.example` for detailed instructions on getting AWS credentials.

### 3. Start the application
```bash
start_servers.bat
```

This starts:
- Monitoring API on port 8000
- Web App on port 3002

### 4. Open in browser
```
http://localhost:3002
```

### 5. Ask questions
Try these examples:
- "What is PaymentGW?"
- "When was the last security incident?"
- "Show me Q2 2026 capacity planning"

---

## ✨ Features

### 1. **AI Chat with RAG**
- Powered by AWS Bedrock (Claude)
- Retrieves context from knowledge base
- Uses 3 tools: database query, service metrics, incident investigation

### 2. **Beautiful Markdown Rendering**
- Message bubbles render markdown beautifully
- Citation modals show formatted documents
- Supports: headers, bold, italic, code, tables, lists, links, blockquotes

### 3. **Inline Citations**
- AI adds [1], [2], [3] inline in answers
- Different documents get different numbers
- Click citation cards to see full document

### 4. **Citation Cards**
- Green cards with document name, confidence, snippet
- Click to open modal with full formatted content
- Hover effects and smooth animations

### 5. **View Trace**
- Debug panel showing:
  - Model ID
  - Query rewriting status
  - RAG retrieval status
  - Tool calls made
  - Citations found

### 6. **Chat History**
- Auto-saves to localStorage
- 24-hour expiry
- "New Chat" button to clear
- History sidebar to view past conversations

### 7. **Question Sidebar**
- 5 levels of questions (L1-L5)
- Click to auto-fill question
- Organized by difficulty

---

## 🏗️ Architecture

### Backend (`web_app.py`)
- FastAPI server
- WebSocket for real-time chat
- AWS Bedrock integration
- RAG with local fallback
- 3 tools: query_database, get_service_metrics, investigate_incident

### Frontend (`index.html`)
- Vanilla JavaScript
- WebSocket client
- Markdown parser (parseMarkdown, formatMarkdown)
- LocalStorage for chat history
- Responsive design

### Database (`geekbrain.db`)
- SQLite database
- Tables: incidents, monthly_costs, sla_targets, daily_metrics

### Knowledge Base (`data_package/knowledge_base/`)
- 35+ markdown files
- Services, policies, postmortems, team info
- YAML frontmatter support

---

## 🧪 Testing

### Manual Testing
See `TESTING.md` for comprehensive test guide.

Quick tests:
1. **L1 Questions**: Basic facts
2. **L2 Questions**: Comparisons
3. **L3 Questions**: Analysis
4. **L4 Questions**: Conversations
5. **L5 Questions**: Investigations

### Automated Testing
```bash
# Run all tests
python data_package/scripts/test_all_levels.py

# Quick test
python data_package/scripts/test_quick.py
```

---

## 🔧 Troubleshooting

### Issue: ExpiredTokenException ⚠️
**Error**: `The security token included in the request is expired`

**Solution**:
```bash
# 1. Check credentials status
python check_aws_credentials.py

# 2. Update .env with new credentials (see FIX_EXPIRED_TOKEN.md)
notepad .env

# 3. Restart server
restart_app.bat
```

**Note**: AWS Academy credentials expire after 3-4 hours. You need to refresh them for each session.

See `FIX_EXPIRED_TOKEN.md` for detailed guide.

### Issue: Server won't start
**Solution**: Kill existing processes
```bash
taskkill /F /IM python.exe /IM uvicorn.exe
start_servers.bat
```

### Issue: Markdown not rendering
**Solution**: Restart server + hard refresh
```bash
restart_app.bat
# Then in browser: Ctrl + Shift + R
```

### Issue: Citations not showing
**Solution**: Check AWS credentials in `.env`
```
AWS_DEFAULT_REGION=us-east-1
KNOWLEDGE_BASE_ID=your_kb_id
```

### Issue: Database errors
**Solution**: Check database exists
```bash
python data_package/scripts/seed_data.py
```

---

## 📁 Project Structure

```
.
├── data_package/
│   ├── knowledge_base/          # 35+ markdown files
│   ├── scripts/
│   │   ├── web_app.py          # FastAPI backend
│   │   ├── index.html          # Frontend UI
│   │   ├── monitoring_api.py   # Mock metrics API
│   │   ├── geekbrain.db        # SQLite database
│   │   └── test_*.py           # Test scripts
│   └── structured_data/         # CSV data files
├── questions/student/           # Question sets L1-L5
├── .env                         # AWS credentials
├── start_servers.bat            # Start script
├── restart_app.bat              # Restart script
├── TESTING.md                   # Test guide
└── README.md                    # This file
```

---

## 🎨 Design System

### Colors
- Primary: `#7c83fd` (purple)
- Success: `#22c55e` (green)
- Warning: `#fcd34d` (yellow)
- Error: `#ef4444` (red)
- Text: `#1f2937` (dark gray)
- Background: `#f9fafb` (light gray)

### Typography
- Font: Plus Jakarta Sans
- Sizes: 12px - 25.6px
- Weights: 400 (regular), 600 (semibold), 700 (bold)

### Components
- Message bubbles with avatars
- Citation cards with hover effects
- Modal with dark overlay
- Sidebar with tabs
- Level selector buttons

---

## 🔑 Key Features Implementation

### Markdown Rendering
- **Function**: `parseMarkdown()` for citation modal
- **Function**: `formatMarkdown()` for message bubbles
- **Features**: Headers, bold, italic, code, tables, lists, links, blockquotes
- **YAML**: Automatically removes YAML frontmatter

### Citations
- **Backend**: Extracts snippets from retrieved documents
- **Frontend**: Displays as green cards with confidence scores
- **Modal**: Click to see full formatted document
- **Inline**: AI adds [1], [2], [3] in answer text

### Chat History
- **Storage**: localStorage with 24-hour expiry
- **Auto-save**: On each message
- **Restore**: On page refresh
- **Conversations**: Saved separately in history sidebar

### Tools
1. **query_database**: Execute SQL on SQLite
2. **get_service_metrics**: Get live metrics from API
3. **investigate_incident**: Comprehensive service investigation

---

## 📚 Documentation

### User Documentation
- **README.md** - Complete guide (this file)
- **QUICK_START.md** - Quick reference
- **SETUP.md** - Setup instructions

### System Documentation
- **SYSTEM_FLOW.md** - Detailed system flow & architecture (English)
- **LUONG_HOAT_DONG.md** - System flow explanation (Vietnamese)
- **PROJECT_SUMMARY.md** - Project overview

### Developer Documentation
- **DESIGN_SYSTEM.md** - Design reference
- **TESTING.md** - Test guide
- Code comments in source files

### Learner Documentation
- **W4_learner_guide.md** - English
- **W4_learner_guide_vi.md** - Vietnamese
- **W4_project_announcement.md** - English
- **W4_project_announcement_vi.md** - Vietnamese

---

## 🆘 Support

### Common Issues

1. **Port already in use**
   ```bash
   netstat -ano | findstr :3002
   taskkill /F /PID <PID>
   ```

2. **AWS credentials error**
   - Check `.env` file exists
   - Verify credentials are correct
   - Test with: `aws bedrock list-foundation-models`

3. **Database not found**
   ```bash
   python data_package/scripts/seed_data.py
   ```

4. **Markdown not rendering**
   - Restart server: `restart_app.bat`
   - Hard refresh: `Ctrl + Shift + R`

---

## 🎯 Learning Objectives

This project demonstrates:
- ✅ RAG (Retrieval Augmented Generation)
- ✅ Tool use with LLMs
- ✅ WebSocket real-time communication
- ✅ Markdown parsing and rendering
- ✅ LocalStorage for persistence
- ✅ Responsive UI design
- ✅ Error handling and debugging

---

## 📝 Notes

- **Model**: Claude Haiku 4.5 (fast, cost-effective)
- **Region**: us-east-1
- **Database**: SQLite (local, no setup needed)
- **Knowledge Base**: Local markdown files with AWS Bedrock fallback

---

## 🚀 Next Steps

1. Start the app: `start_servers.bat`
2. Open browser: `http://localhost:3002`
3. Try questions from sidebar
4. Click citations to see formatted docs
5. Check "View trace" for debugging
6. Explore chat history

---

**Enjoy GeekBrain AI! 🤖**

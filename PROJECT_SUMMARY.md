# 📦 GeekBrain AI - Project Summary

## ✅ Complete Features

### 1. AI Chat with RAG
- AWS Bedrock (Claude Haiku 4.5)
- Knowledge Base retrieval
- Local fallback support
- Query rewriting for context

### 2. Tool Use
- **query_database**: SQL queries on SQLite
- **get_service_metrics**: Live metrics from API
- **investigate_incident**: Comprehensive service investigation

### 3. Beautiful Markdown Rendering
- Message bubbles render markdown
- Citation modals show formatted documents
- YAML frontmatter support
- Features: headers, bold, italic, code, tables, lists, links, blockquotes

### 4. Inline Citations
- AI adds [1], [2], [3] in answers
- Different documents = different numbers
- Superscript styling with hover effects

### 5. Citation Cards
- Green cards with document name, confidence, snippet
- Click to open modal with full formatted content
- Hover effects and smooth animations

### 6. View Trace
- Debug panel showing:
  - Model ID
  - Query rewriting status
  - RAG retrieval status
  - Tool calls made
  - Citations found
  - Errors (if any)

### 7. Chat History
- Auto-saves to localStorage
- 24-hour expiry
- "New Chat" button to clear
- History sidebar to view past conversations
- Load previous conversations

### 8. Question Sidebar
- 5 levels of questions (L1-L5)
- Click to auto-fill question
- Organized by difficulty
- Descriptions for each level

---

## 📁 Project Structure

```
GeekBrain-AI/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # Complete documentation
├── SETUP.md                  # Setup guide
├── QUICK_START.md            # Quick reference
├── TESTING.md                # Test guide
├── DESIGN_SYSTEM.md          # Design reference
├── start_servers.bat         # Start script
├── restart_app.bat           # Restart script
├── test_markdown_parser.html # Markdown parser tester
│
├── data_package/
│   ├── knowledge_base/       # 35+ markdown files
│   │   ├── service_*.md      # Service documentation
│   │   ├── team_*.md         # Team information
│   │   ├── postmortem_*.md   # Incident postmortems
│   │   └── *_policy.md       # Policies
│   │
│   ├── scripts/
│   │   ├── web_app.py        # FastAPI backend
│   │   ├── index.html        # Frontend UI
│   │   ├── monitoring_api.py # Mock metrics API
│   │   ├── geekbrain.db      # SQLite database
│   │   ├── seed_data.py      # Database seeder
│   │   ├── test_*.py         # Test scripts
│   │   └── pyproject.toml    # Python dependencies
│   │
│   └── structured_data/      # CSV data files
│       ├── incidents.csv
│       ├── monthly_costs.csv
│       ├── sla_targets.csv
│       └── daily_metrics.csv
│
├── questions/student/        # Question sets
│   ├── L1_questions.json     # Basic facts
│   ├── L2_questions.json     # Comparisons
│   ├── L3_questions.json     # Analysis
│   ├── L4_conversation_scripts.json  # Conversations
│   └── L5_investigation_prompts.json # Investigations
│
└── mentoring/                # Mentoring materials
    ├── session1-*.html
    └── session2-*.html
```

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite
- **AI**: AWS Bedrock (Claude)
- **WebSocket**: Real-time communication
- **Tools**: 3 custom tools

### Frontend
- **HTML/CSS/JavaScript**: Vanilla (no frameworks)
- **WebSocket**: Client for real-time chat
- **LocalStorage**: Chat history persistence
- **Markdown Parser**: Custom implementation

### Infrastructure
- **AWS Bedrock**: LLM and Knowledge Base
- **Local Fallback**: Markdown files
- **Mock API**: Monitoring metrics

---

## 📊 Database Schema

### incidents
- incident_id (PK)
- service
- date
- severity
- duration_minutes
- root_cause
- resolution
- team_responsible
- reported_by

### monthly_costs
- id (PK)
- service
- month
- compute_cost
- storage_cost
- network_cost
- third_party_cost
- total_cost

### sla_targets
- id (PK)
- service
- metric
- target
- measurement_window

### daily_metrics
- id (PK)
- date
- service
- latency_p99_ms
- error_rate_percent
- requests_per_minute
- availability_percent

---

## 🎨 Design System

### Colors
- **Primary**: #7c83fd (purple)
- **Success**: #22c55e (green)
- **Warning**: #fcd34d (yellow)
- **Error**: #ef4444 (red)
- **Text**: #1f2937 (dark gray)
- **Background**: #f9fafb (light gray)

### Typography
- **Font**: Plus Jakarta Sans
- **Sizes**: 12px - 25.6px
- **Weights**: 400, 600, 700

### Components
- Message bubbles with avatars
- Citation cards with hover effects
- Modal with dark overlay
- Sidebar with tabs
- Level selector buttons
- Trace panel

---

## 🧪 Testing

### Test Levels
- **L1**: Basic facts (10 questions)
- **L2**: Comparisons (10 questions)
- **L3**: Analysis (10 questions)
- **L4**: Conversations (5 scripts)
- **L5**: Investigations (5 prompts)

### Test Scripts
- `test_all_levels.py` - Complete test suite
- `test_quick.py` - Quick smoke test
- `test_simple.py` - Basic functionality
- `test_comprehensive.py` - Detailed testing

### Manual Testing
See `TESTING.md` for comprehensive guide.

---

## 📚 Documentation

### User Documentation
- **README.md** - Complete guide
- **QUICK_START.md** - Quick reference
- **SETUP.md** - Setup instructions

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

## 🔑 Key Implementation Details

### Markdown Parser
- **Functions**: `parseMarkdown()`, `formatMarkdown()`
- **Features**: Headers, bold, italic, code, tables, lists, links, blockquotes
- **YAML**: Removes frontmatter automatically
- **Security**: HTML escaping to prevent XSS

### Citations
- **Backend**: Extracts snippets from retrieved documents
- **Frontend**: Displays as green cards
- **Modal**: Click to see full formatted document
- **Inline**: AI adds [1], [2], [3] in answer text

### Chat History
- **Storage**: localStorage with 24-hour expiry
- **Auto-save**: On each message
- **Restore**: On page refresh
- **Conversations**: Saved separately in history sidebar

### Error Handling
- **Tool failures**: Rollback history to consistent state
- **AWS errors**: Graceful fallback to local KB
- **Validation**: Input validation and sanitization

---

## 🚀 Deployment

### Local Development
```bash
start_servers.bat
```

### Production Considerations
- Use environment variables for secrets
- Enable HTTPS
- Add rate limiting
- Implement authentication
- Use production database (PostgreSQL)
- Deploy to cloud (AWS, Azure, GCP)
- Add monitoring and logging
- Implement caching

---

## 📈 Future Enhancements

### Potential Features
- [ ] Syntax highlighting for code blocks
- [ ] Table of contents for long documents
- [ ] Copy button for code blocks
- [ ] Search within modal
- [ ] Print-friendly styling
- [ ] Export chat history
- [ ] Share conversations
- [ ] Multi-user support
- [ ] Authentication
- [ ] Admin dashboard

### Performance Improvements
- [ ] Lazy loading for history
- [ ] Virtual scrolling for long chats
- [ ] Debounced search
- [ ] Cached responses
- [ ] Optimized markdown parser

---

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ RAG (Retrieval Augmented Generation)
- ✅ Tool use with LLMs
- ✅ WebSocket real-time communication
- ✅ Markdown parsing and rendering
- ✅ LocalStorage for persistence
- ✅ Responsive UI design
- ✅ Error handling and debugging
- ✅ AWS Bedrock integration
- ✅ Database design and queries
- ✅ API design and implementation

---

## 📞 Support

### Getting Help
1. Check **README.md** for documentation
2. Check **SETUP.md** for setup issues
3. Check **TESTING.md** for testing issues
4. Check browser console for errors
5. Check server logs for backend errors

### Common Issues
- Port in use → Kill processes
- AWS credentials → Check `.env`
- Markdown not rendering → Restart server
- Database errors → Run seed script

---

## 📝 License

[Add your license here]

---

## 👥 Contributors

[Add contributors here]

---

## 🙏 Acknowledgments

- AWS Bedrock for LLM capabilities
- FastAPI for backend framework
- Plus Jakarta Sans for typography
- Claude AI for assistance

---

**Project Status**: ✅ Complete and Production-Ready

**Last Updated**: May 7, 2026

**Version**: 1.0.0

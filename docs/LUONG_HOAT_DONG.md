# 🔄 Luồng Hoạt Động GeekBrain AI

## 📌 Tóm tắt ngắn gọn

GeekBrain AI = **RAG** + **Tool Use** + **Conversational Memory**

---

## 🎯 Luồng chính (5 bước)

### 1. User hỏi câu hỏi
```
User: "What is PaymentGW?"
  ↓
Frontend gửi qua WebSocket
  ↓
Backend nhận message
```

### 2. Tìm kiếm tài liệu (RAG)
```
Backend tìm trong Knowledge Base:
  ├─► AWS Bedrock KB (nếu có)
  └─► Local .md files (fallback)

Kết quả: Top 3-5 documents liên quan
```

### 3. Gọi AI (Claude)
```
Gửi cho Claude:
  ├─► System prompt (hướng dẫn)
  ├─► Retrieved documents (tài liệu tìm được)
  └─► User question (câu hỏi)

Claude quyết định:
  ├─► Trả lời trực tiếp? → Xong!
  └─► Cần dùng tool? → Bước 4
```

### 4. Thực thi tools (nếu cần)
```
Claude yêu cầu tool:
  ├─► query_database: Truy vấn SQL
  ├─► get_service_metrics: Lấy metrics
  └─► investigate_incident: Điều tra chi tiết

Backend thực thi → Trả kết quả cho Claude
Claude xử lý kết quả → Tạo câu trả lời
```

### 5. Hiển thị kết quả
```
Backend gửi về Frontend:
  ├─► Answer (câu trả lời)
  ├─► Citations (trích dẫn)
  ├─► Tool calls (tools đã dùng)
  └─► Trace (debug info)

Frontend render:
  ├─► Format markdown đẹp
  ├─► Hiển thị citation cards
  ├─► Lưu vào localStorage
  └─► User có thể click xem chi tiết
```

---

## 🔍 Chi tiết từng thành phần

### A. Query Rewriting (Xử lý đại từ)

**Vấn đề:**
```
User: "What is PaymentGW?"
AI: "PaymentGW is a payment gateway..."
User: "What about its cost?"  ← "its" là gì?
```

**Giải pháp:**
```python
# Phát hiện đại từ (it, its, their, that, this)
if has_pronouns("What about its cost?"):
    # Xem lại lịch sử hội thoại
    # Thay thế đại từ bằng tên cụ thể
    rewritten = "What about PaymentGW's cost?"
```

**Kết quả:**
- Input: "What about its cost?"
- Rewritten: "What about PaymentGW's cost?"
- AI hiểu rõ hơn!

---

### B. RAG (Retrieval Augmented Generation)

**Bước 1: Tìm kiếm**
```python
# Tách keywords từ câu hỏi
query = "What is PaymentGW?"
keywords = ["PaymentGW", "payment", "gateway"]

# Tìm trong 35+ files .md
for file in knowledge_base:
    score = count_matches(file, keywords)
    if score > 0:
        results.append((score, file))

# Lấy top 3 files có score cao nhất
top_3 = sort_by_score(results)[:3]
```

**Bước 2: Trích xuất citations**
```python
citations = []
for i, doc in enumerate(top_3):
    citations.append({
        "file": "service_paymentgw.md",
        "snippet": "PaymentGW is GeekBrain's payment gateway...",
        "confidence": 0.95 - (i * 0.08),  # 95%, 87%, 79%
        "index": i + 1,  # [1], [2], [3]
        "full_content": doc  # Cho modal
    })
```

**Bước 3: Gửi cho AI**
```python
system_prompt = f"""
Retrieved documents:
<documents>
{doc1}
{doc2}
{doc3}
</documents>

Instructions:
- Use documents above to answer
- Add inline citations [1], [2], [3]
- Different documents = different numbers
"""
```

---

### C. Tool Use (3 tools)

#### Tool 1: query_database
**Khi nào dùng:** Câu hỏi về số liệu (cost, incidents, SLA)

**Ví dụ:**
```
User: "What was PaymentGW's cost in Q1 2026?"
  ↓
Claude: "I need to query the database"
  ↓
Tool: query_database
SQL: SELECT month, total_cost FROM monthly_costs 
     WHERE service = 'PaymentGW' 
     AND month BETWEEN '2026-01' AND '2026-03'
  ↓
Result: [
  {"month": "2026-01", "total_cost": 4200},
  {"month": "2026-02", "total_cost": 4800},
  {"month": "2026-03", "total_cost": 7500}
]
  ↓
Claude: "PaymentGW's Q1 2026 cost was $16,500 
         (Jan: $4,200, Feb: $4,800, Mar: $7,500)"
```

#### Tool 2: get_service_metrics
**Khi nào dùng:** Câu hỏi về metrics hiện tại

**Ví dụ:**
```
User: "What is PaymentGW's current latency?"
  ↓
Claude: "I need current metrics"
  ↓
Tool: get_service_metrics("PaymentGW")
  ↓
Result: {
  "latency_p99_ms": 215.3,
  "error_rate_percent": 0.15,
  "requests_per_minute": 12500
}
  ↓
Claude: "PaymentGW's current p99 latency is 215.3ms"
```

#### Tool 3: investigate_incident
**Khi nào dùng:** Câu hỏi "investigate", "analyze", "review"

**Ví dụ:**
```
User: "Investigate PaymentGW performance issues"
  ↓
Claude: "I need comprehensive investigation"
  ↓
Tool: investigate_incident("PaymentGW", "performance")
  ↓
Result: {
  "findings": {
    "recent_incidents": [...],
    "cost_trend": [...],
    "sla_targets": [...],
    "daily_metrics": [...]
  }
}
  ↓
Claude: Tạo report chi tiết với:
  - Performance metrics table
  - SLA comparison
  - Recent incidents
  - Cost analysis
  - Recommendations
```

---

### D. Markdown Rendering

**Backend gửi:**
```
"## PaymentGW Overview\n\n**Owner**: Team Platform\n\n- Feature 1\n- Feature 2"
```

**Frontend xử lý:**
```javascript
// 1. Remove YAML frontmatter
text = text.replace(/^---[\s\S]*?---\n*/m, '');

// 2. Escape HTML
text = escapeHtml(text);

// 3. Convert markdown
text = text.replace(/^## (.+)$/gm, '<h2>$1</h2>');  // Headers
text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');  // Bold
text = text.replace(/^- (.+)$/gm, '<li>$1</li>');  // Lists
// ... more conversions

// 4. Wrap lists
text = text.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

// 5. Convert paragraphs
text = convertParagraphs(text);
```

**Kết quả hiển thị:**
```html
<h2>PaymentGW Overview</h2>
<p><strong>Owner</strong>: Team Platform</p>
<ul>
  <li>Feature 1</li>
  <li>Feature 2</li>
</ul>
```

---

### E. Citations

**3 loại citations:**

#### 1. Inline Citations [1], [2], [3]
```
AI answer: "PaymentGW is owned by Team Platform [1] 
            and handles payment processing [2]."

[1] = team_platform.md
[2] = service_paymentgw.md
```

#### 2. Citation Cards
```
┌─────────────────────────────────────────┐
│ [1] 📄 team_platform.md      [95%]     │
│ Alex Chen is the lead of Team Platform │
│ which owns PaymentGW and AuthSvc...    │
└─────────────────────────────────────────┘
       ↑ Click để xem full document
```

#### 3. Citation Modal
```
Click citation card
  ↓
Modal mở ra với:
  ├─► Full document content (5000 chars)
  ├─► Markdown formatted đẹp
  ├─► Scrollable
  └─► Close: button, outside click, ESC key
```

---

### F. Chat History

**Auto-save:**
```javascript
// Mỗi khi có message mới
function saveChatHistory() {
    localStorage.setItem('geekbrain_chat_history', JSON.stringify(chatHistory));
    localStorage.setItem('geekbrain_chat_timestamp', Date.now());
}
```

**Auto-load:**
```javascript
// Khi mở page
function loadChatHistory() {
    const saved = localStorage.getItem('geekbrain_chat_history');
    const timestamp = localStorage.getItem('geekbrain_chat_timestamp');
    
    // Check expiry (24 hours)
    if (Date.now() - timestamp < 24 * 60 * 60 * 1000) {
        chatHistory = JSON.parse(saved);
        restoreChatHistory();
    }
}
```

**History Sidebar:**
```
┌─────────────────────────────┐
│ Questions | History         │
├─────────────────────────────┤
│ What is PaymentGW?          │
│ 2 messages • 2 min ago      │
│                         🗑️  │
├─────────────────────────────┤
│ Investigate PaymentGW       │
│ 4 messages • 1 hour ago     │
│                         🗑️  │
└─────────────────────────────┘
```

---

## 🎨 UI Components

### 1. Message Bubble
```
┌─────────────────────────────────────┐
│ 👤  User                            │
│ ┌─────────────────────────────────┐ │
│ │ What is PaymentGW?              │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ GB  Assistant                       │
│ ┌─────────────────────────────────┐ │
│ │ PaymentGW is GeekBrain's        │ │
│ │ payment gateway [1]...          │ │
│ └─────────────────────────────────┘ │
│                                     │
│ 📄 Citations (3)                    │
│ 🔍 View trace →                     │
└─────────────────────────────────────┘
```

### 2. Tool Calls Badge
```
🗄️ Database Query: SELECT * FROM...
📊 Service Metrics: PaymentGW
🔍 Investigation: PaymentGW (performance)
```

### 3. Trace Panel
```
┌─────────────────────────────────────┐
│ Model: claude-haiku-4-5             │
│ Query Rewriting: ✓ Applied          │
│ RAG Retrieval: ✓ Used               │
│ Citations Found: 3 document(s)      │
│ Tool Calls: ✓ 2 call(s)             │
└─────────────────────────────────────┘
```

---

## 🔄 Conversational Memory

**Cách hoạt động:**
```python
# History được maintain trong session
history = [
    {"role": "user", "content": "What is PaymentGW?"},
    {"role": "assistant", "content": "PaymentGW is..."},
    {"role": "user", "content": "What about its cost?"},  # ← "its" = PaymentGW
    # Query rewriting: "What about PaymentGW's cost?"
]

# Mỗi lần gọi Claude, gửi toàn bộ history
response = claude.converse(
    messages=history,
    ...
)
```

**Ví dụ conversation:**
```
Turn 1:
User: "Which service had highest cost in March?"
AI: "PaymentGW had the highest cost at $7,500"

Turn 2:
User: "Why did its costs spike?"  ← "its" = PaymentGW
Rewritten: "Why did PaymentGW's costs spike?"
AI: "PaymentGW's costs spiked due to incident INC-005..."

Turn 3:
User: "Which team is responsible for it?"  ← "it" = PaymentGW
Rewritten: "Which team is responsible for PaymentGW?"
AI: "Team Platform is responsible for PaymentGW"

Turn 4:
User: "What was their most recent incident?"  ← "their" = Team Platform
Rewritten: "What was Team Platform's most recent incident?"
AI: "Team Platform's most recent incident was INC-005..."
```

---

## 📊 Database Schema

### incidents
```sql
CREATE TABLE incidents (
    incident_id TEXT PRIMARY KEY,
    service TEXT,
    date TEXT,
    severity TEXT,
    duration_minutes INTEGER,
    root_cause TEXT,
    resolution TEXT,
    team_responsible TEXT,
    reported_by TEXT
);
```

### monthly_costs
```sql
CREATE TABLE monthly_costs (
    id INTEGER PRIMARY KEY,
    service TEXT,
    month TEXT,
    compute_cost REAL,
    storage_cost REAL,
    network_cost REAL,
    third_party_cost REAL,
    total_cost REAL
);
```

### sla_targets
```sql
CREATE TABLE sla_targets (
    id INTEGER PRIMARY KEY,
    service TEXT,
    metric TEXT,
    target REAL,
    measurement_window TEXT
);
```

### daily_metrics
```sql
CREATE TABLE daily_metrics (
    id INTEGER PRIMARY KEY,
    date TEXT,
    service TEXT,
    latency_p99_ms REAL,
    error_rate_percent REAL,
    requests_per_minute INTEGER,
    availability_percent REAL
);
```

---

## 🎯 Tổng kết

### Điểm mạnh:
✅ RAG với local fallback
✅ 3 tools mạnh mẽ
✅ Conversational memory
✅ Beautiful markdown rendering
✅ Inline citations
✅ Citation modal với full document
✅ View trace cho debugging
✅ Chat history với localStorage
✅ Error handling tốt

### Luồng hoạt động:
```
User Question
    ↓
Query Rewriting (if needed)
    ↓
RAG Retrieval (KB search)
    ↓
Citation Extraction
    ↓
Claude Converse #1
    ↓
Tool Execution (if needed)
    ↓
Claude Converse #2 (if tools used)
    ↓
Response with {answer, citations, tool_calls, trace}
    ↓
Frontend Rendering (markdown, citations, trace)
    ↓
Save to LocalStorage
    ↓
User can interact (click citations, view trace, continue chat)
```

---

**Hệ thống hoạt động mượt mà và professional! 🚀**

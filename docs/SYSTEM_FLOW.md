# 🔄 GeekBrain AI - System Flow & Architecture

## Tổng quan / Overview

GeekBrain AI là một hệ thống RAG (Retrieval Augmented Generation) với tool use, sử dụng AWS Bedrock Claude để trả lời câu hỏi về infrastructure, services, và incidents.

---

## 🏗️ Kiến trúc tổng thể / Overall Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │◄───────►│  Web Server  │◄───────►│ AWS Bedrock │
│  (Frontend) │ WebSocket│  (FastAPI)   │  HTTP   │   (Claude)  │
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               ├──────► SQLite Database
                               │
                               ├──────► Knowledge Base (Local .md files)
                               │
                               └──────► Monitoring API (Mock)
```

---

## 📊 Luồng hoạt động chi tiết / Detailed Flow

### 1️⃣ Khởi động hệ thống / System Startup

```
User runs: start_servers.bat
    │
    ├──► Start Monitoring API (port 8000)
    │    └─► Mock API trả về metrics giả lập
    │
    └──► Start Web App (port 3002)
         ├─► Load .env (AWS credentials)
         ├─► Connect to SQLite database
         ├─► Initialize AWS Bedrock client
         ├─► Load question sets (L1-L5)
         └─► Start FastAPI + WebSocket server
```

### 2️⃣ User mở browser / User Opens Browser

```
Browser: http://localhost:3002
    │
    ├──► GET / → Server trả về index.html
    │
    └──► JavaScript khởi động:
         ├─► POST /api/session → Tạo session_id
         ├─► WebSocket connect: ws://localhost:3002/ws/{session_id}
         ├─► Load questions từ /api/questions
         ├─► Load chat history từ localStorage
         └─► Render UI (sidebar, chat area, input)
```

### 3️⃣ User gửi câu hỏi / User Sends Question

```
User types: "What is PaymentGW?"
    │
    ├──► Frontend: Capture input
    │    ├─► Add user message to chat UI
    │    ├─► Show typing indicator
    │    └─► Send via WebSocket: {"message": "What is PaymentGW?"}
    │
    └──► Backend receives message via WebSocket
```

---

## 🔄 Backend Processing Flow

### Step 1: Query Rewriting (Nếu cần / If needed)

```python
# Check if query has pronouns (it, its, their, that, this)
if has_pronouns(user_input) and len(history) > 0:
    # Rewrite query using conversation history
    rewritten_query = rewrite_with_context(user_input, history)
    # Example: "What about its cost?" → "What about PaymentGW's cost?"
else:
    rewritten_query = user_input
```

**Ví dụ:**
- Input: "What about its cost?"
- History: Previous question about PaymentGW
- Output: "What about PaymentGW's cost?"

---

### Step 2: RAG - Knowledge Base Retrieval

```python
# Try AWS Bedrock Knowledge Base first
if KB_ID and KB_ID != "ABCDEF1234":
    try:
        # Call AWS Bedrock Agent Runtime
        response = bedrock_agent_client.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={'text': rewritten_query},
            retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': 5}}
        )
        # Extract documents from response
        retrieved_docs = extract_documents(response)
    except:
        # Fallback to local
        retrieved_docs = search_local_kb(rewritten_query)
else:
    # Use local knowledge base
    retrieved_docs = search_local_kb(rewritten_query)
```

**Local KB Search:**
```python
def search_knowledge_base_local(query):
    # Extract keywords from query
    keywords = [w.lower() for w in query.split() if len(w) > 2]
    
    # Search all .md files in knowledge_base/
    results = []
    for file in knowledge_base_files:
        content = read_file(file)
        score = count_keyword_matches(content, keywords)
        if score > 0:
            results.append((score, file, content))
    
    # Return top 3 most relevant files
    return top_3_results
```

---

### Step 3: Extract Citations

```python
# Parse retrieved documents
citations = []
for i, doc in enumerate(retrieved_docs):
    # Extract filename
    filename = extract_filename(doc)
    
    # Extract snippet (first 150 chars)
    snippet = doc[:150] + "..."
    
    # Calculate confidence score
    confidence = 0.95 - (i * 0.08)
    
    # Create citation object
    citations.append({
        "file": filename,
        "confidence": confidence,
        "snippet": snippet,
        "index": i + 1,
        "full_content": doc[:5000]  # For modal display
    })
```

**Ví dụ:**
```json
{
  "file": "service_paymentgw.md",
  "confidence": 0.95,
  "snippet": "PaymentGW is GeekBrain's payment gateway. It processes credit card transactions...",
  "index": 1,
  "full_content": "# PaymentGW — Service Reference\n\n## Purpose\n..."
}
```

---

### Step 4: Build System Prompt

```python
system_prompt = f"""You are GeekBrain's internal system assistant.

Retrieved documents:
<documents>
{retrieved_docs}
</documents>

CRITICAL INSTRUCTIONS:
1. For policy questions: Use documents above and cite file names
2. For numerical questions: MUST use Tools
3. For SLA compliance: Compare metrics vs targets
4. INLINE CITATIONS: Add [1], [2], [3] in answer
   - Different documents = different numbers
5. FORMATTING: Use markdown (bold, tables, lists, headers)
6. INVESTIGATION RESULTS: Use structured format with sections
7. Always be specific with names, numbers, and sources
"""
```

---

### Step 5: First Converse Call (Initial Response)

```python
# Call AWS Bedrock Converse API
response = bedrock_client.converse(
    modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    messages=history + [{"role": "user", "content": [{"text": user_input}]}],
    system=[{"text": system_prompt}],
    toolConfig=tool_config  # Define available tools
)

# Check response
output_message = response["output"]["message"]
```

**Có 2 trường hợp:**

#### Case A: AI trả lời trực tiếp (No tool use)
```python
if no_tool_use_in_response:
    # Extract answer text
    answer = output_message["content"][0]["text"]
    
    # Return to frontend
    return {
        "answer": answer,
        "tool_calls": [],
        "citations": citations,
        "trace": {...}
    }
```

#### Case B: AI muốn dùng tool
```python
if tool_use_in_response:
    # Extract tool calls
    tool_uses = [block for block in output_message['content'] if 'toolUse' in block]
    
    # Execute each tool
    for tool_use in tool_uses:
        tool_name = tool_use['name']
        tool_inputs = tool_use['input']
        tool_use_id = tool_use['toolUseId']
        
        # Execute tool
        if tool_name == 'query_database':
            result = query_database(tool_inputs['sql'])
        elif tool_name == 'get_service_metrics':
            result = get_service_metrics(tool_inputs['service_name'])
        elif tool_name == 'investigate_incident':
            result = investigate_incident(tool_inputs['service_name'], 
                                         tool_inputs['investigation_type'])
        
        # Collect tool results
        tool_results.append({
            "toolResult": {
                "toolUseId": tool_use_id,
                "content": [{"json": result}]
            }
        })
    
    # Continue to Step 6
```

---

### Step 6: Tool Execution Details

#### Tool 1: query_database
```python
def query_database(sql: str):
    """Execute SQL on SQLite database"""
    conn = sqlite3.connect('geekbrain.db')
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    
    # Return as list of dicts
    return [dict(row) for row in rows]
```

**Ví dụ:**
```sql
SELECT month, total_cost 
FROM monthly_costs 
WHERE service = 'PaymentGW' 
ORDER BY month DESC 
LIMIT 3
```

**Result:**
```json
[
  {"month": "2026-03", "total_cost": 7500},
  {"month": "2026-02", "total_cost": 4800},
  {"month": "2026-01", "total_cost": 4200}
]
```

#### Tool 2: get_service_metrics
```python
def get_service_metrics(service_name: str):
    """Get live metrics from monitoring API"""
    response = requests.get(f"http://localhost:8000/metrics/{service_name}")
    return response.json()
```

**Result:**
```json
{
  "service": "PaymentGW",
  "latency_p99_ms": 215.3,
  "error_rate_percent": 0.15,
  "requests_per_minute": 12500,
  "timestamp": "2026-05-07T23:00:00Z"
}
```

#### Tool 3: investigate_incident
```python
def investigate_incident(service_name: str, investigation_type: str):
    """Comprehensive investigation combining DB, API, and KB data"""
    result = {
        "service": service_name,
        "investigation_type": investigation_type,
        "findings": {}
    }
    
    # Get incidents from DB
    incidents = query_db("SELECT * FROM incidents WHERE service = ?", service_name)
    result["findings"]["recent_incidents"] = incidents
    
    # Get cost trend
    costs = query_db("SELECT * FROM monthly_costs WHERE service = ?", service_name)
    result["findings"]["cost_trend"] = costs
    
    # Get SLA targets
    sla = query_db("SELECT * FROM sla_targets WHERE service = ?", service_name)
    result["findings"]["sla_targets"] = sla
    
    # Get daily metrics
    daily = query_db("SELECT * FROM daily_metrics WHERE service = ?", service_name)
    result["findings"]["daily_metrics"] = daily
    
    return result
```

---

### Step 7: Second Converse Call (Final Response)

```python
# Add assistant message with tool use
history.append(output_message)

# Add user message with tool results
history.append({
    "role": "user",
    "content": tool_results  # All tool results
})

# Call Bedrock again with tool results
final_response = bedrock_client.converse(
    modelId=MODEL_ID,
    messages=history,
    system=system_param,
    toolConfig=tool_config
)

# Extract final answer
final_message = final_response["output"]["message"]
answer = final_message["content"][0]["text"]

# Return to frontend
return {
    "answer": answer,
    "tool_calls": tool_calls,
    "citations": citations,
    "trace": {...}
}
```

---

## 🎨 Frontend Rendering Flow

### Step 1: Receive Response from Backend

```javascript
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    // data = {answer, tool_calls, citations, trace}
    
    // Remove typing indicator
    removeTypingIndicator();
    
    // Render assistant message
    renderAssistantMessage(data);
}
```

### Step 2: Render Assistant Message

```javascript
function renderAssistantMessage(data) {
    // 1. Create message container
    const msgDiv = document.createElement('div');
    msgDiv.className = 'msg assistant';
    
    // 2. Add avatar
    msgDiv.innerHTML = `
        <div class="msg-avatar">GB</div>
        <div class="msg-body">
            ${renderToolCalls(data.tool_calls)}
            <div class="msg-bubble">${formatMarkdown(data.answer)}</div>
            ${renderCitations(data.citations)}
            <span class="view-trace" onclick="toggleTrace(this)">View trace →</span>
            ${renderTrace(data.trace)}
        </div>
    `;
    
    // 3. Append to messages container
    document.getElementById('messages').appendChild(msgDiv);
    
    // 4. Scroll to bottom
    scrollToBottom();
    
    // 5. Save to chat history
    saveChatHistory();
}
```

### Step 3: Format Markdown

```javascript
function formatMarkdown(text) {
    let html = text;
    
    // Remove YAML frontmatter
    html = html.replace(/^---[\s\S]*?---\n*/m, '');
    
    // Escape HTML
    html = escapeHtml(html);
    
    // Convert inline citations [1] to superscript
    html = html.replace(/\[(\d+)\]/g, '<sup>[$1]</sup>');
    
    // Convert headers
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    
    // Convert bold, italic
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // Convert code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/```[\s\S]*?```/g, function(match) {
        const code = match.replace(/```(\w*)\n?/, '').replace(/```$/, '');
        return '<pre><code>' + code + '</code></pre>';
    });
    
    // Convert tables
    html = convertTables(html);
    
    // Convert lists
    html = convertLists(html);
    
    // Convert paragraphs
    html = convertParagraphs(html);
    
    return html;
}
```

### Step 4: Render Citations

```javascript
function renderCitations(citations) {
    if (!citations || citations.length === 0) return '';
    
    let html = '<div class="citations">';
    
    citations.forEach((cit, idx) => {
        // Store citation data in window object for modal
        const citId = `citation_${Date.now()}_${idx}`;
        window[citId] = cit;
        
        html += `
            <div class="citation-item collapsed" onclick="showCitationModal('${citId}')">
                <div class="citation-header">
                    <div class="citation-source">
                        <span class="citation-index">[${cit.index}]</span>
                        📄 ${cit.file}
                    </div>
                    <span class="citation-confidence">[${(cit.confidence * 100).toFixed(0)}%]</span>
                </div>
                <div class="citation-snippet">${cit.snippet}</div>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}
```

### Step 5: Citation Modal

```javascript
function showCitationModal(citId) {
    const citationData = window[citId];
    
    // Parse markdown content
    const parsedContent = parseMarkdown(citationData.full_content);
    
    // Set modal content
    document.getElementById('modalFileName').textContent = citationData.file;
    document.getElementById('modalContent').innerHTML = parsedContent;
    document.getElementById('modalContent').className = 'markdown-content';
    document.getElementById('modalConfidence').textContent = 
        `Confidence: ${(citationData.confidence * 100).toFixed(0)}% | Retrieved from knowledge base`;
    
    // Show modal
    document.getElementById('citationModal').classList.add('active');
    document.body.style.overflow = 'hidden';
}
```

---

## 💾 Chat History Management

### Save to LocalStorage

```javascript
function saveChatHistory() {
    const historyData = {
        messages: chatHistory,  // Array of {role, content, citations, tool_calls, trace}
        timestamp: Date.now(),
        sessionId: sessionId
    };
    
    // Save current chat
    localStorage.setItem('geekbrain_chat_history', JSON.stringify(chatHistory));
    localStorage.setItem('geekbrain_chat_timestamp', Date.now().toString());
    
    // Save to conversations list
    saveCurrentConversation();
}

function saveCurrentConversation() {
    // Get all conversations
    let conversations = JSON.parse(localStorage.getItem('geekbrain_conversations') || '[]');
    
    // Create conversation object
    const conversation = {
        id: currentConversationId || generateId(),
        title: chatHistory[0]?.content.substring(0, 60) || 'New Chat',
        timestamp: Date.now(),
        messageCount: chatHistory.length,
        messages: chatHistory
    };
    
    // Update or add conversation
    const index = conversations.findIndex(c => c.id === conversation.id);
    if (index >= 0) {
        conversations[index] = conversation;
    } else {
        conversations.push(conversation);
    }
    
    // Save back to localStorage
    localStorage.setItem('geekbrain_conversations', JSON.stringify(conversations));
}
```

### Load from LocalStorage

```javascript
function loadChatHistory() {
    try {
        const saved = localStorage.getItem('geekbrain_chat_history');
        const timestamp = localStorage.getItem('geekbrain_chat_timestamp');
        
        if (saved && timestamp) {
            const age = Date.now() - parseInt(timestamp);
            const maxAge = 24 * 60 * 60 * 1000; // 24 hours
            
            if (age < maxAge) {
                chatHistory = JSON.parse(saved);
                restoreChatHistory();
            } else {
                // Expired, clear
                localStorage.removeItem('geekbrain_chat_history');
                localStorage.removeItem('geekbrain_chat_timestamp');
            }
        }
    } catch (e) {
        console.error('Failed to load chat history:', e);
    }
}
```

---

## 🔍 View Trace Feature

```javascript
function renderTrace(trace) {
    if (!trace) return '';
    
    return `
        <div class="trace-panel" style="display:none;">
            <div class="trace-row">
                <span class="trace-label">Model:</span>
                <span class="trace-value highlight">${trace.model}</span>
            </div>
            <div class="trace-row">
                <span class="trace-label">Query Rewriting:</span>
                <span class="trace-value">${trace.query_rewritten ? '✓ Applied' : '✗ Not needed'}</span>
            </div>
            ${trace.rewritten_query ? `
                <div class="trace-row">
                    <span class="trace-label">Original Query:</span>
                    <span class="trace-value">${trace.original_query}</span>
                </div>
                <div class="trace-row">
                    <span class="trace-label">Rewritten Query:</span>
                    <span class="trace-value highlight">${trace.rewritten_query}</span>
                </div>
            ` : ''}
            <div class="trace-row">
                <span class="trace-label">RAG Retrieval:</span>
                <span class="trace-value">${trace.rag_used ? '✓ Used' : '✗ Not used'}</span>
            </div>
            <div class="trace-row">
                <span class="trace-label">Citations Found:</span>
                <span class="trace-value">${trace.num_citations} document(s)</span>
            </div>
            <div class="trace-row">
                <span class="trace-label">Tool Calls:</span>
                <span class="trace-value">${trace.tool_calls_made > 0 ? `✓ ${trace.tool_calls_made} call(s)` : '✗ None'}</span>
            </div>
            ${trace.error ? `
                <div class="trace-row">
                    <span class="trace-label">Error:</span>
                    <span class="trace-value" style="color: #ef4444;">${trace.error}</span>
                </div>
            ` : ''}
        </div>
    `;
}
```

---

## 🎯 Tóm tắt luồng hoàn chỉnh / Complete Flow Summary

```
1. User sends question
   ↓
2. Backend: Query rewriting (if needed)
   ↓
3. Backend: RAG - Retrieve documents from KB
   ↓
4. Backend: Extract citations with snippets
   ↓
5. Backend: Build system prompt with retrieved docs
   ↓
6. Backend: First Converse call to Claude
   ↓
7a. If no tool use → Return answer directly
   ↓
7b. If tool use → Execute tools
   ↓
8. Backend: Second Converse call with tool results
   ↓
9. Backend: Return {answer, tool_calls, citations, trace}
   ↓
10. Frontend: Receive via WebSocket
   ↓
11. Frontend: Format markdown
   ↓
12. Frontend: Render message with citations
   ↓
13. Frontend: Save to localStorage
   ↓
14. User can:
    - Click citation → Open modal with formatted doc
    - Click "View trace" → See debug info
    - Continue conversation → Context maintained
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INPUT                          │
│                  "What is PaymentGW?"                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    QUERY REWRITING                          │
│  Check pronouns → Rewrite with context (if needed)         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAG RETRIEVAL                            │
│  AWS Bedrock KB (or Local) → Top 3-5 documents             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  CITATION EXTRACTION                        │
│  Extract: filename, snippet, confidence, full_content      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   CLAUDE CONVERSE #1                        │
│  System prompt + Retrieved docs + User question            │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │         │
                    ▼         ▼
        ┌──────────────┐  ┌──────────────┐
        │  No Tool Use │  │   Tool Use   │
        └──────┬───────┘  └──────┬───────┘
               │                 │
               │                 ▼
               │         ┌──────────────────┐
               │         │  Execute Tools   │
               │         │  - query_database│
               │         │  - get_metrics   │
               │         │  - investigate   │
               │         └──────┬───────────┘
               │                │
               │                ▼
               │         ┌──────────────────┐
               │         │ CLAUDE CONVERSE #2│
               │         │ With tool results│
               │         └──────┬───────────┘
               │                │
               └────────┬───────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    FINAL RESPONSE                           │
│  {answer, tool_calls, citations, trace}                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FRONTEND RENDERING                         │
│  - Format markdown                                          │
│  - Render citations                                         │
│  - Show trace (optional)                                    │
│  - Save to localStorage                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Error Handling Flow

```
Try:
    Execute normal flow
Catch Error:
    ├─► Rollback history to consistent state
    ├─► Log error
    └─► Return error message to user

Tool Execution Error:
    ├─► Catch exception
    ├─► Return {"error": "message"}
    └─► Claude handles gracefully

WebSocket Error:
    ├─► Reconnect automatically
    └─► Show connection status to user

LocalStorage Error:
    ├─► Catch and log
    └─► Continue without history
```

---

**Hệ thống hoạt động hoàn chỉnh với error handling tốt! 🚀**

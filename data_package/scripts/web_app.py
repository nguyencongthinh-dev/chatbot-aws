import sqlite3
import requests
import boto3
import json
import sys
import uuid
import os
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# ==========================================
# 1. CONFIGURATION
# ==========================================

REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
KB_ID = os.getenv('KNOWLEDGE_BASE_ID')
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

DB_PATH = Path(__file__).parent / "geekbrain.db"
KB_DIR = Path(__file__).parent.parent / "knowledge_base"

# ==========================================
# 2. TOOLS
# ==========================================

def query_database(sql: str):
    print(f"\n  [TOOL] Running SQL: {sql}")
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        return {"error": str(e)}

def get_service_metrics(service_name: str):
    print(f"\n  [TOOL] Getting metrics for: {service_name}")
    try:
        response = requests.get(f"http://localhost:8000/metrics/{service_name}", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"error": "Cannot connect to monitoring API on port 8000."}

def investigate_incident(service_name: str, investigation_type: str):
    """Structured investigation combining DB, API, and KB data."""
    print(f"\n  [TOOL] Investigating {service_name} ({investigation_type})")
    
    result = {
        "service": service_name,
        "investigation_type": investigation_type,
        "timestamp": "2026-05-07",
        "summary": f"Comprehensive {investigation_type} investigation for {service_name}",
        "findings": {}
    }
    
    try:
        # Try to get current metrics (optional)
        try:
            metrics_response = requests.get(f"http://localhost:8000/metrics/{service_name}", timeout=2)
            if metrics_response.status_code == 200:
                metrics = metrics_response.json()
                result["findings"]["current_metrics"] = {
                    "latency_p99_ms": metrics.get("latency_p99_ms"),
                    "error_rate_percent": metrics.get("error_rate_percent"),
                    "requests_per_minute": metrics.get("requests_per_minute"),
                    "status": "Retrieved successfully"
                }
        except:
            result["findings"]["current_metrics"] = {
                "status": "Monitoring API unavailable - using historical data only"
            }
        
        # Get incidents from DB
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incidents WHERE service = ? ORDER BY date DESC LIMIT 3", (service_name,))
        incidents = [dict(row) for row in cursor.fetchall()]
        result["findings"]["recent_incidents"] = {
            "count": len(incidents),
            "incidents": incidents
        }
        
        # Get cost trend
        cursor.execute("SELECT month, total_cost FROM monthly_costs WHERE service = ? ORDER BY month DESC LIMIT 6", (service_name,))
        costs = [dict(row) for row in cursor.fetchall()]
        result["findings"]["cost_trend"] = {
            "months": len(costs),
            "data": costs
        }
        
        # Get SLA targets
        cursor.execute("SELECT * FROM sla_targets WHERE service = ?", (service_name,))
        sla = [dict(row) for row in cursor.fetchall()]
        result["findings"]["sla_targets"] = {
            "count": len(sla),
            "targets": sla
        }
        
        # Get recent daily metrics
        cursor.execute("SELECT * FROM daily_metrics WHERE service = ? ORDER BY date DESC LIMIT 7", (service_name,))
        daily = [dict(row) for row in cursor.fetchall()]
        result["findings"]["daily_metrics"] = {
            "days": len(daily),
            "data": daily
        }
        
        conn.close()
        
        # Add comprehensive summary
        result["summary"] = f"Investigation complete for {service_name}: Found {len(incidents)} recent incidents, {len(costs)} months of cost data, {len(sla)} SLA targets, and {len(daily)} days of performance metrics."
        
        return result
    except Exception as e:
        return {"error": str(e), "service": service_name}

tool_config = {
    "tools": [
        {
            "toolSpec": {
                "name": "query_database",
                "description": """Execute SQL on SQLite database. 
Tables and schemas:
- monthly_costs: service, month, compute_cost, storage_cost, network_cost, third_party_cost, total_cost
- incidents: incident_id (PK), service, date, severity, duration_minutes, root_cause, resolution, team_responsible, reported_by
- sla_targets: service, metric, target, measurement_window
- daily_metrics: date, service, latency_p99_ms, error_rate_percent, requests_per_minute, availability_percent

Use for historical costs, SLA targets, incidents, daily metrics.""",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "sql": {"type": "string", "description": "SQLite query to run."}
                        },
                        "required": ["sql"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "get_service_metrics",
                "description": "Get live metrics (latency, error rate, requests) for a service.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "service_name": {"type": "string", "description": "Service name e.g. PaymentGW, NotificationSvc"}
                        },
                        "required": ["service_name"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "investigate_incident",
                "description": "Perform comprehensive structured investigation of a service. Use when asked to 'investigate', 'analyze', or 'review' a service. Returns detailed JSON with current metrics, recent incidents, cost trends, and SLA targets.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "service_name": {"type": "string", "description": "Service to investigate (e.g., PaymentGW, NotificationSvc)"},
                            "investigation_type": {"type": "string", "enum": ["performance", "cost", "incident", "general"], "description": "Type of investigation"}
                        },
                        "required": ["service_name", "investigation_type"]
                    }
                }
            }
        }
    ]
}

# ==========================================
# 3. RAG - KNOWLEDGE BASE SEARCH
# ==========================================

def search_knowledge_base_local(query: str) -> str:
    """Search local knowledge base using keyword matching."""
    print(f"\n  [RAG LOCAL] Searching knowledge_base/ for: '{query}'")
    keywords = [w.lower() for w in query.split() if len(w) > 2]
    results = []
    try:
        for fname in os.listdir(KB_DIR):
            if not fname.endswith('.md'):
                continue
            fpath = KB_DIR / fname
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            content_lower = content.lower()
            score = sum(content_lower.count(kw) for kw in keywords)
            if score > 0:
                results.append((score, fname, content))
        # Get top 3 most relevant files
        results.sort(key=lambda x: x[0], reverse=True)
        contexts = []
        for score, fname, content in results[:3]:
            # Take first 3000 chars to avoid too long context
            contexts.append(f"--- Source: {fname} ---\n{content[:3000]}")
        return "\n\n".join(contexts)
    except Exception as e:
        print(f"  [RAG Local Error]: {e}")
        return ""

def search_knowledge_base(query):
    # Try AWS Bedrock KB first if available
    if KB_ID and KB_ID != "ABCDEF1234":
        print(f"\n  [RAG AWS] Searching Bedrock Knowledge Base for: '{query}'")
        try:
            bedrock_agent_client = boto3.client('bedrock-agent-runtime', region_name=REGION)
            response = bedrock_agent_client.retrieve(
                knowledgeBaseId=KB_ID,
                retrievalQuery={'text': query},
                retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': 5}}
            )
            contexts = []
            for result in response.get('retrievalResults', []):
                source = result.get('location', {}).get('s3Location', {}).get('uri', 'Unknown')
                text = result.get('content', {}).get('text', '')
                contexts.append(f"--- Source: {source} ---\n{text}")
            if contexts:
                return "\n\n".join(contexts)
        except Exception as e:
            print(f"  [AWS KB unavailable, fallback to local]: {e}")
    # Fallback: search local knowledge_base/
    return search_knowledge_base_local(query)

# ==========================================
# 4. BEDROCK CLIENT
# ==========================================

try:
    bedrock_client = boto3.client("bedrock-runtime", region_name=REGION)
except Exception as e:
    print(f"AWS Boto3 init error: {e}")
    bedrock_client = None

# ==========================================
# 5. SESSION MANAGEMENT
# ==========================================

sessions = {}

def get_or_create_session(session_id: str):
    if session_id not in sessions:
        sessions[session_id] = []
    return sessions[session_id]

def chat_with_claude(user_input: str, session_id: str):
    history = get_or_create_session(session_id)
    
    # Query rewriting for follow-up questions
    rewritten_query = user_input
    if len(history) > 0:
        # Check if query has pronouns that need context
        if any(word in user_input.lower() for word in ['it', 'its', 'their', 'that', 'this', 'they', 'them']):
            print(f"\n  [REWRITE] Detected pronoun, rewriting query...")
            try:
                rewrite_prompt = """Given the conversation history, rewrite the user's latest question to be self-contained. Replace pronouns (it, its, their, that, this) with specific service/team names from context. Output ONLY the rewritten question, nothing else."""
                
                # Use only text content from history, no tool blocks
                rewrite_history = []
                for msg in history[-6:]:
                    if msg['role'] == 'user':
                        # Extract only text content, skip tool results
                        text_content = []
                        for block in msg['content']:
                            if 'text' in block:
                                text_content.append(block)
                        if text_content:
                            rewrite_history.append({"role": "user", "content": text_content})
                    elif msg['role'] == 'assistant':
                        # Extract only text content, skip tool use
                        text_content = []
                        for block in msg['content']:
                            if 'text' in block:
                                text_content.append(block)
                        if text_content:
                            rewrite_history.append({"role": "assistant", "content": text_content})
                
                rewrite_history.append({"role": "user", "content": [{"text": f"Rewrite this question: {user_input}"}]})
                
                rewrite_response = bedrock_client.converse(
                    modelId=MODEL_ID,
                    messages=rewrite_history,
                    system=[{"text": rewrite_prompt}]
                )
                rewritten_query = rewrite_response["output"]["message"]["content"][0]["text"].strip()
                print(f"  [REWRITE] '{user_input}' → '{rewritten_query}'")
            except Exception as e:
                print(f"  [REWRITE] Failed: {e}, using original query")
    
    # RAG: Search knowledge base with rewritten query
    retrieved_docs = search_knowledge_base(rewritten_query)
    
    # Extract citations from retrieved docs with text snippets
    citations = []
    full_docs = {}  # Store full documents for modal display
    if retrieved_docs:
        # Parse sources and their content
        import re
        # Split by source markers
        doc_sections = re.split(r'--- Source: (.+?) ---', retrieved_docs)
        
        # Process pairs of (source_name, content)
        seen = set()
        citation_index = 0
        for i in range(1, len(doc_sections), 2):
            if i + 1 < len(doc_sections):
                source = doc_sections[i]
                content = doc_sections[i + 1].strip()
                
                if source not in seen:
                    # Extract just filename without path
                    filename = source.split('/')[-1] if '/' in source else source
                    
                    # Store full content for modal
                    full_docs[filename] = content
                    
                    # Extract first meaningful sentence or paragraph (max 150 chars)
                    snippet = content[:150].strip()
                    if len(content) > 150:
                        # Try to end at sentence boundary
                        last_period = snippet.rfind('.')
                        last_newline = snippet.rfind('\n')
                        cut_point = max(last_period, last_newline)
                        if cut_point > 50:  # Only cut if we have enough text
                            snippet = snippet[:cut_point + 1]
                        snippet += "..."
                    
                    # Clean up snippet (remove markdown headers, extra whitespace)
                    snippet = re.sub(r'^#+\s+', '', snippet)  # Remove markdown headers
                    snippet = re.sub(r'\n+', ' ', snippet)    # Replace newlines with spaces
                    snippet = re.sub(r'\s+', ' ', snippet)    # Normalize whitespace
                    
                    confidence = round(0.95 - (citation_index * 0.08), 2)
                    
                    # Create citation object with snippet and full content
                    citations.append({
                        "file": filename,
                        "confidence": confidence,
                        "snippet": snippet,
                        "index": citation_index + 1,
                        "full_content": content[:5000]  # Limit to 5000 chars for performance
                    })
                    
                    seen.add(source)
                    citation_index += 1
    
    system_prompt = f"""You are GeekBrain's internal system assistant.
    Retrieved documents:
    <documents>
    {retrieved_docs}
    </documents>
    
    CRITICAL INSTRUCTIONS:
    1. For policy questions: Use documents above and cite file names. When documents conflict, explicitly state which version is current (v2) and which is archived (v1).
    
    2. For questions about overrides/exceptions: Always mention the specific approval authority (e.g., "VP Mark Sullivan") and the specific condition (e.g., "P1 severity").
    
    3. For numerical questions (costs, metrics, SLA): MUST use Tools. Never estimate.
    
    4. For SLA compliance questions: Compare current metrics vs targets and explicitly state "exceeds target" or "breaches target" or "meets target".
    
    5. For "highest/lowest/most" questions: MUST use database query tool to sort and find the answer. Never answer from memory.
    
    6. INLINE CITATIONS - VERY IMPORTANT:
       - When using information from documents, add citation numbers [1], [2], [3] inline
       - Each DIFFERENT document gets a DIFFERENT number
       - Same document = same number throughout the answer
       - Number them in order of first appearance
       
       Example with 3 different documents:
       "Alex Chen is the lead of Team Platform [1]. The team owns PaymentGW [2] which handles payment processing [2]. The current rate limit is 1,000 requests per minute [3]."
       
       Where:
       [1] = team_platform.md (first document)
       [2] = service_paymentgw.md (second document, used twice)
       [3] = api_reference_v2.md (third document)
       
       WRONG: Using [1] for everything
       RIGHT: Different documents = different numbers
    
    7. FORMATTING - Use markdown for better readability:
       - Use **bold** for important terms
       - Use tables for structured data (services, costs, metrics, comparisons)
       - Use bullet lists for multiple items
       - Use headers (##) for sections
       
       Example table format:
       | Column 1 | Column 2 | Column 3 |
       |----------|----------|----------|
       | Data 1   | Data 2   | Data 3   |
       | Data 4   | Data 5   | Data 6   |
    
    8. INVESTIGATION RESULTS - When investigate_incident tool returns data:
       - Start with "## Investigation Results for [ServiceName]"
       - Use section headers: "### Findings", "### Recent Incidents", "### Cost Trend", "### SLA Targets"
       - Format incidents as bullet list with date, severity, root cause
       - Present cost data as table or bullet list
       - Summarize key findings at the end
       - Always include the word "investigation" and "findings" in your response
    
    9. Always be specific with names, numbers, and sources."""
    system_param = [{"text": system_prompt}]
    
    # Track original history length for rollback
    original_length = len(history)
    
    history.append({"role": "user", "content": [{"text": user_input}]})
    
    tool_calls = []

    try:
        response = bedrock_client.converse(
            modelId=MODEL_ID,
            messages=history,
            system=system_param,
            toolConfig=tool_config
        )

        output_message = response["output"]["message"]
        
        # Check for tool calls (can be multiple)
        tool_uses = [block for block in output_message['content'] if 'toolUse' in block]
        
        if tool_uses:
            # Execute all tools
            tool_results_content = []
            for tool_block in tool_uses:
                tool_use = tool_block['toolUse']
                tool_name = tool_use['name']
                tool_inputs = tool_use['input']
                tool_use_id = tool_use['toolUseId']
                
                print(f"\n  [EXECUTING] {tool_name} with ID {tool_use_id}")
                
                if tool_name == 'query_database':
                    tool_result = query_database(tool_inputs['sql'])
                    tool_calls.append({"tool": "Database Query", "input": tool_inputs["sql"]})
                elif tool_name == 'get_service_metrics':
                    tool_result = get_service_metrics(tool_inputs['service_name'])
                    tool_calls.append({"tool": "Service Metrics API", "input": tool_inputs["service_name"]})
                elif tool_name == 'investigate_incident':
                    tool_result = investigate_incident(tool_inputs['service_name'], tool_inputs['investigation_type'])
                    tool_calls.append({"tool": "Incident Investigation", "input": f"{tool_inputs['service_name']} ({tool_inputs['investigation_type']})"})
                else:
                    tool_result = {"error": f"Unknown tool: {tool_name}"}
                    
                print(f"  [RESULT] {str(tool_result)[:80]}...")
                
                # Wrap tool result in object if it's a list
                if isinstance(tool_result, list):
                    tool_result_wrapped = {"results": tool_result, "count": len(tool_result)}
                else:
                    tool_result_wrapped = tool_result
                
                tool_results_content.append({
                    "toolResult": {
                        "toolUseId": tool_use_id,
                        "content": [{"json": tool_result_wrapped}]
                    }
                })
            
            # Append assistant message with tool calls
            history.append(output_message)
            # Append user message with all tool results
            history.append({
                "role": "user",
                "content": tool_results_content
            })
            
            try:
                final_response = bedrock_client.converse(
                    modelId=MODEL_ID,
                    messages=history,
                    system=system_param,
                    toolConfig=tool_config
                )
                final_message = final_response["output"]["message"]
                history.append(final_message)

                return {
                    "answer": final_message["content"][0]["text"],
                    "tool_calls": tool_calls,
                    "citations": citations,
                    "trace": {
                        "query_rewritten": rewritten_query != user_input,
                        "original_query": user_input,
                        "rewritten_query": rewritten_query if rewritten_query != user_input else None,
                        "rag_used": bool(retrieved_docs),
                        "num_citations": len(citations),
                        "tool_calls_made": len(tool_calls),
                        "model": MODEL_ID
                    }
                }
            except Exception as final_error:
                # If final converse fails, rollback the tool result messages
                print(f"  [ERROR] Final converse failed: {final_error}")
                # Remove the tool result message and assistant message
                history.pop()  # Remove tool results
                history.pop()  # Remove assistant message with tool use
                raise final_error  # Re-raise to be caught by outer try-except

        history.append(output_message)
        return {
            "answer": output_message["content"][0]["text"],
            "tool_calls": tool_calls,
            "citations": citations,
            "trace": {
                "query_rewritten": rewritten_query != user_input,
                "original_query": user_input,
                "rewritten_query": rewritten_query if rewritten_query != user_input else None,
                "rag_used": bool(retrieved_docs),
                "num_citations": len(citations),
                "tool_calls_made": 0,
                "model": MODEL_ID
            }
        }

    except Exception as e:
        # Rollback to original state - remove ALL messages added in this turn
        while len(history) > original_length:
            history.pop()
        print(f"  [ERROR] Rolled back to history length {original_length}")
        return {
            "answer": f"Error from AWS Bedrock: {e}",
            "tool_calls": [],
            "citations": [],
            "trace": {
                "query_rewritten": False,
                "original_query": user_input,
                "rewritten_query": None,
                "rag_used": False,
                "num_citations": 0,
                "tool_calls_made": 0,
                "model": MODEL_ID,
                "error": str(e)
            }
        }

# ==========================================
# 6. LOAD QUESTIONS
# ==========================================

QUESTIONS_DIR = Path(__file__).parent.parent.parent / "questions" / "student"

def load_questions():
    questions_by_level = {}
    files = {
        1: "L1_questions.json",
        2: "L2_questions.json",
        3: "L3_questions.json",
        4: "L4_conversation_scripts.json",
        5: "L5_investigation_prompts.json",
    }
    for level, fname in files.items():
        fpath = QUESTIONS_DIR / fname
        if fpath.exists():
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            items = []
            if level <= 3:
                for q in data.get("questions", []):
                    items.append({"id": q["id"], "text": q["question"], "hint": q.get("grading_notes", "")})
            elif level == 4:
                for c in data.get("conversations", []):
                    first_turn = c["turns"][0]["user"]
                    items.append({"id": c["id"], "text": first_turn, "hint": c.get("title", "")})
            else:
                for inv in data.get("investigations", []):
                    items.append({"id": inv["id"], "text": inv["prompt"], "hint": ""})
            questions_by_level[level] = {"description": data.get("description", ""), "items": items}
    return questions_by_level

ALL_QUESTIONS = load_questions()

# ==========================================
# 7. API ROUTES
# ==========================================

@app.get("/api/questions")
def get_questions():
    return ALL_QUESTIONS

@app.post("/api/session")
def create_session():
    session_id = str(uuid.uuid4())[:8]
    sessions[session_id] = []
    return {"session_id": session_id}

@app.delete("/api/session/{session_id}")
def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        return {"status": "deleted"}
    return {"status": "not_found"}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_msg = payload.get("message", "")
            if not user_msg.strip():
                continue
            result = chat_with_claude(user_msg, session_id)
            await websocket.send_text(json.dumps(result))
    except WebSocketDisconnect:
        pass

# ==========================================
# 8. SERVE HTML
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>index.html not found</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002, reload=False)

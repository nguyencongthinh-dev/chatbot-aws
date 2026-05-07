import sqlite3
import requests
import boto3
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# CẤU HÌNH CƠ BẢN
# ==========================================
REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
KB_ID = os.getenv('KNOWLEDGE_BASE_ID')
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# Tìm đúng đường dẫn tới database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'geekbrain.db')

try:
    bedrock_client = boto3.client('bedrock-runtime', region_name=REGION)
    bedrock_agent_client = boto3.client('bedrock-agent-runtime', region_name=REGION)
except Exception as e:
    print(f"Lỗi khởi tạo AWS Boto3: {e}")
    sys.exit(1)

# ==========================================
# TOOLS & RAG
# ==========================================
def query_database(sql: str):
    print(f"\n  [🛠️ TOOL] Đang chạy SQL: {sql}")
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        return {"error": str(e)}

def get_service_metrics(service_name: str):
    print(f"\n  [🛠️ TOOL] Đang gọi API lấy metrics cho: {service_name}")
    try:
        response = requests.get(f"http://localhost:8000/metrics/{service_name}")
        if response.status_code == 200:
            return response.json()
        return {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"error": "Không thể kết nối đến API."}

tool_config = {
    "tools": [
        {
            "toolSpec": {
                "name": "query_database",
                "description": """Thực thi câu lệnh SQL vào SQLite.
Bảng và schema:
- monthly_costs: id, service, month, compute_cost, storage_cost, network_cost, third_party_cost, total_cost
- incidents: id, incident_id, service, date, severity, duration_minutes, root_cause, resolution
- sla_targets: id, service, metric, target, measurement_window
- daily_metrics: id, date, service, latency_p99_ms, error_rate_percent, requests_per_minute, availability_percent

Dùng cho chi phí lịch sử, SLA targets, incidents, metrics hàng ngày.""",
                "inputSchema": {
                    "json": {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]}
                }
            }
        },
        {
            "toolSpec": {
                "name": "get_service_metrics",
                "description": "Lấy dữ liệu TRỰC TIẾP (latency, error rate) hiện tại của một service.",
                "inputSchema": {
                    "json": {"type": "object", "properties": {"service_name": {"type": "string"}}, "required": ["service_name"]}
                }
            }
        }
    ]
}

KB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'knowledge_base')

def search_knowledge_base_local(query: str) -> str:
    """Tìm kiếm trong local knowledge base bằng keyword matching."""
    print(f"\n  [📚 RAG LOCAL] Đang tìm trong knowledge_base/ cho: '{query}'")
    keywords = [w.lower() for w in query.split() if len(w) > 2]
    results = []
    try:
        for fname in os.listdir(KB_DIR):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(KB_DIR, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            content_lower = content.lower()
            score = sum(content_lower.count(kw) for kw in keywords)
            if score > 0:
                results.append((score, fname, content))
        # Lấy top 3 file liên quan nhất
        results.sort(key=lambda x: x[0], reverse=True)
        contexts = []
        for score, fname, content in results[:3]:
            # Chỉ lấy 3000 ký tự đầu mỗi file để tránh quá dài
            contexts.append(f"--- Nguồn: {fname} ---\n{content[:3000]}")
        return "\n\n".join(contexts)
    except Exception as e:
        print(f"  [Lỗi RAG Local]: {e}")
        return ""

def search_knowledge_base(query):
    # Thử AWS Bedrock KB trước nếu có KB_ID hợp lệ
    if KB_ID and KB_ID != "ABCDEF1234":
        print(f"\n  [📚 RAG AWS] Đang quét Bedrock Knowledge Base cho: '{query}'")
        try:
            response = bedrock_agent_client.retrieve(
                knowledgeBaseId=KB_ID,
                retrievalQuery={'text': query},
                retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': 5}}
            )
            contexts = []
            for result in response.get('retrievalResults', []):
                source = result.get('location', {}).get('s3Location', {}).get('uri', 'Unknown')
                text = result.get('content', {}).get('text', '')
                contexts.append(f"--- Nguồn: {source} ---\n{text}")
            if contexts:
                return "\n\n".join(contexts)
        except Exception as e:
            print(f"  [AWS KB không khả dụng, fallback local]: {e}")
    # Fallback: tìm trong local knowledge_base/
    return search_knowledge_base_local(query)

# ==========================================
# XỬ LÝ LLM (ĐÃ FIX LỖI TOOLCONFIG)
# ==========================================
conversation_history = []

def chat_with_claude(user_input):
    global conversation_history
    
    # Track original history length for rollback
    original_length = len(conversation_history)
    
    retrieved_docs = search_knowledge_base(user_input)
    
    system_prompt = f"""Bạn là trợ lý hệ thống nội bộ GeekBrain.
    Tài liệu trích xuất:
    <documents>
    {retrieved_docs}
    </documents>
    Nếu hỏi quy định/chính sách/rate limit: Dùng tài liệu trên và trích dẫn tên file.
    Nếu có xung đột, ưu tiên bản mới (v2).
    Nếu hỏi số liệu lịch sử/chi phí/hiện tại: Bắt buộc dùng Tools.
    """
    system_param = [{"text": system_prompt}]
    
    conversation_history.append({"role": "user", "content": [{"text": user_input}]})
    
    try:
        response = bedrock_client.converse(
            modelId=MODEL_ID,
            messages=conversation_history,
            system=system_param,
            toolConfig=tool_config
        )
        
        output_message = response['output']['message']
        
        # Kiểm tra xem có tool calls không (có thể có nhiều tool calls cùng lúc)
        tool_uses = [block for block in output_message['content'] if 'toolUse' in block]
        
        if tool_uses:
            # Thực thi tất cả tools
            tool_results_content = []
            for tool_block in tool_uses:
                tool_use = tool_block['toolUse']
                tool_name = tool_use['name']
                tool_inputs = tool_use['input']
                tool_use_id = tool_use['toolUseId']
                
                print(f"\n  [🛠️ EXECUTING] {tool_name} with ID {tool_use_id}")
                
                if tool_name == 'query_database':
                    tool_result = query_database(tool_inputs['sql'])
                elif tool_name == 'get_service_metrics':
                    tool_result = get_service_metrics(tool_inputs['service_name'])
                else:
                    tool_result = {"error": f"Unknown tool: {tool_name}"}
                    
                print(f"  [📥 KẾT QUẢ] {str(tool_result)[:80]}...")
                
                # Wrap tool result trong object nếu là list
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
            
            # Append assistant message với tool calls
            conversation_history.append(output_message)
            # Append user message với tất cả tool results
            conversation_history.append({
                "role": "user",
                "content": tool_results_content
            })
            
            final_response = bedrock_client.converse(
                modelId=MODEL_ID,
                messages=conversation_history,
                system=system_param,
                toolConfig=tool_config 
            )
            
            final_message = final_response['output']['message']
            conversation_history.append(final_message)
            return final_message['content'][0]['text']
        
        conversation_history.append(output_message)
        return output_message['content'][0]['text']
        
    except Exception as e:
        # Rollback to original state
        while len(conversation_history) > original_length:
            conversation_history.pop()
        print(f"  [LỖI] Rolled back to history length {original_length}")
        return f"Lỗi từ AWS Bedrock: {e}"

if __name__ == "__main__":
    print("="*60)
    print("🚀 ĐANG CHẠY BẢN APP_CUOI.PY (ĐÃ FIX LỖI TOOLCONFIG)")
    print("="*60)
    
    while True:
        user_msg = input("\n👤 Bạn: ")
        if user_msg.lower() in ['exit', 'quit']: break
        if not user_msg.strip(): continue
            
        print("🤖 Claude đang suy nghĩ...")
        print(f"\n🤖 System: {chat_with_claude(user_msg)}")
import json
import sqlite3
import os

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    
    # Lấy thông tin từ Bedrock Agent
    actionGroup = event.get('actionGroup', '')
    function = event.get('function', '')
    parameters = event.get('parameters', [])
    
    # Trích xuất câu lệnh SQL từ tham số Bedrock truyền vào
    sql_query = ""
    for param in parameters:
        if param['name'] == 'sql':
            sql_query = param['value']
            
    if not sql_query:
        return create_response(actionGroup, function, "Error: Missing 'sql' parameter")

    # Chỉ cho phép lệnh SELECT (Read-only) để đảm bảo an toàn
    if not sql_query.strip().upper().startswith("SELECT"):
        return create_response(actionGroup, function, "Error: Only SELECT queries are allowed.")

    try:
        # Kết nối tới file SQLite nằm cùng thư mục với code Lambda
        db_path = os.path.join(os.environ.get('LAMBDA_TASK_ROOT', '.'), 'geekbrain.db')
        conn = sqlite3.connect(db_path)
        
        # Để lấy kết quả dưới dạng dictionary thay vì tuple
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        # Chuyển đổi dữ liệu thành list of dicts
        result_data = [dict(row) for row in rows]
        conn.close()
        
        return create_response(actionGroup, function, json.dumps(result_data))
        
    except Exception as e:
        return create_response(actionGroup, function, f"Database Error: {str(e)}")

def create_response(actionGroup, function, response_string):
    """Hàm phụ trợ để đóng gói response theo chuẩn của Bedrock Agent"""
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": actionGroup,
            "function": function,
            "functionResponse": {
                "responseBody": {
                    "TEXT": {
                        "body": response_string
                    }
                }
            }
        }
    }
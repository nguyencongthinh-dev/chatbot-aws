# 🔧 Refactoring Hard Code - Đề Xuất Cải Thiện

## 📊 Tổng Quan Hard Code

### Mức Độ Ưu Tiên
- 🔴 **HIGH** - Nên fix ngay (URLs, ports)
- 🟡 **MEDIUM** - Nên fix khi có thời gian (cache config, model ID)
- 🟢 **LOW** - OK để giữ nguyên (business logic, relative paths)

---

## 🔴 Priority 1: URLs và Ports

### Vấn đề hiện tại:
```python
# web_app.py
response = requests.get(f"http://localhost:8000/metrics/{service_name}")
uvicorn.run(app, host="0.0.0.0", port=3002)

# test_all_levels.py
BASE_URL = "http://localhost:3002"
```

### ✅ Giải pháp:

#### 1. Thêm vào `.env`:
```bash
# Server Configuration
WEB_APP_HOST=0.0.0.0
WEB_APP_PORT=3002
MONITORING_API_HOST=127.0.0.1
MONITORING_API_PORT=8000

# URLs (for testing)
WEB_APP_URL=http://localhost:3002
MONITORING_API_URL=http://localhost:8000
```

#### 2. Sửa `web_app.py`:
```python
# Configuration
WEB_APP_HOST = os.getenv('WEB_APP_HOST', '0.0.0.0')
WEB_APP_PORT = int(os.getenv('WEB_APP_PORT', '3002'))
MONITORING_API_URL = os.getenv('MONITORING_API_URL', 'http://localhost:8000')

# Tool functions
def get_service_metrics(service_name: str):
    response = requests.get(f"{MONITORING_API_URL}/metrics/{service_name}", timeout=5)
    # ...

# Main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=WEB_APP_HOST, port=WEB_APP_PORT, reload=False)
```

#### 3. Sửa `test_all_levels.py`:
```python
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv('WEB_APP_URL', 'http://localhost:3002')
MONITORING_URL = os.getenv('MONITORING_API_URL', 'http://localhost:8000')
```

---

## 🟡 Priority 2: Cache Configuration

### Vấn đề hiện tại:
```python
# Hard coded cache sizes
@lru_cache(maxsize=100)
response_cache = ResponseCache(max_size=50, ttl=3600)
db_pool = DBConnectionPool(pool_size=5)
```

### ✅ Giải pháp:

#### 1. Thêm vào `.env`:
```bash
# Cache Configuration
RAG_CACHE_SIZE=100
RESPONSE_CACHE_SIZE=50
RESPONSE_CACHE_TTL=3600
DB_POOL_SIZE=5
```

#### 2. Sửa `web_app.py`:
```python
# Configuration
RAG_CACHE_SIZE = int(os.getenv('RAG_CACHE_SIZE', '100'))
RESPONSE_CACHE_SIZE = int(os.getenv('RESPONSE_CACHE_SIZE', '50'))
RESPONSE_CACHE_TTL = int(os.getenv('RESPONSE_CACHE_TTL', '3600'))
DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '5'))

# Apply configuration
@lru_cache(maxsize=RAG_CACHE_SIZE)
def search_knowledge_base_local(query: str) -> str:
    # ...

response_cache = ResponseCache(max_size=RESPONSE_CACHE_SIZE, ttl=RESPONSE_CACHE_TTL)
db_pool = DBConnectionPool(pool_size=DB_POOL_SIZE)
```

---

## 🟡 Priority 3: Model Configuration

### Vấn đề hiện tại:
```python
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
```

### ✅ Giải pháp:

#### 1. Thêm vào `.env`:
```bash
# AI Model Configuration
BEDROCK_MODEL_ID=us.anthropic.claude-haiku-4-5-20251001-v1:0
```

#### 2. Sửa `web_app.py`:
```python
MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')
```

**Lợi ích:** Dễ dàng chuyển sang model khác (Sonnet, Opus) mà không cần sửa code.

---

## 🟢 Priority 4: Business Logic (Giữ nguyên)

### Các hard code này là OK:

#### 1. Service/Team Names trong Smart Rewriting:
```python
entities = [
    'paymentgw', 'authsvc', 'notificationsvc', 'ordersvc', 'frauddetector', 'reportingsvc',
    'platform', 'commerce', 'engagement', 'data',
    'alex', 'sarah', 'mike', 'emily', 'david', 'mark'
]
```
**Lý do:** Đây là business logic, cần hard code để detect entities chính xác.

**Nếu muốn flexible hơn:** Có thể load từ file JSON:
```python
# entities.json
{
  "services": ["paymentgw", "authsvc", ...],
  "teams": ["platform", "commerce", ...],
  "people": ["alex", "sarah", ...]
}
```

#### 2. Tool Descriptions:
```python
"service_name": {"type": "string", "description": "Service name e.g. PaymentGW, NotificationSvc"}
```
**Lý do:** Documentation cho Claude, cần examples cụ thể.

#### 3. File Paths:
```python
DB_PATH = Path(__file__).parent / "geekbrain.db"
KB_DIR = Path(__file__).parent.parent / "knowledge_base"
```
**Lý do:** Relative paths, tự động adapt theo project structure.

---

## 📝 Implementation Plan

### Phase 1: Critical (1-2 hours)
1. ✅ Tạo `.env.example` với tất cả config mới
2. ✅ Refactor URLs và ports trong `web_app.py`
3. ✅ Refactor URLs trong test files
4. ✅ Test lại toàn bộ L1-L5

### Phase 2: Nice-to-have (30 mins)
1. ✅ Refactor cache configuration
2. ✅ Refactor model ID
3. ✅ Update documentation

### Phase 3: Optional (1 hour)
1. ⚪ Extract entities to JSON file
2. ⚪ Create config validator
3. ⚪ Add config hot-reload

---

## 🎯 Kết Quả Sau Refactoring

### Before:
```python
# Hard coded everywhere
response = requests.get(f"http://localhost:8000/metrics/{service_name}")
uvicorn.run(app, host="0.0.0.0", port=3002)
response_cache = ResponseCache(max_size=50, ttl=3600)
```

### After:
```python
# Centralized configuration
response = requests.get(f"{MONITORING_API_URL}/metrics/{service_name}")
uvicorn.run(app, host=WEB_APP_HOST, port=WEB_APP_PORT)
response_cache = ResponseCache(max_size=RESPONSE_CACHE_SIZE, ttl=RESPONSE_CACHE_TTL)
```

### Benefits:
- ✅ Dễ deploy lên nhiều môi trường (dev, staging, prod)
- ✅ Dễ test với ports khác nhau
- ✅ Dễ tune performance (cache sizes)
- ✅ Dễ switch models
- ✅ Không cần sửa code khi thay đổi config

---

## 📄 File `.env.example` Hoàn Chỉnh

```bash
# ==========================================
# AWS Configuration
# ==========================================
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_SESSION_TOKEN=your_session_token_here
AWS_DEFAULT_REGION=us-east-1
KNOWLEDGE_BASE_ID=your_kb_id_here

# ==========================================
# AI Model Configuration
# ==========================================
BEDROCK_MODEL_ID=us.anthropic.claude-haiku-4-5-20251001-v1:0

# ==========================================
# Server Configuration
# ==========================================
WEB_APP_HOST=0.0.0.0
WEB_APP_PORT=3002
MONITORING_API_HOST=127.0.0.1
MONITORING_API_PORT=8000

# URLs (for testing and internal calls)
WEB_APP_URL=http://localhost:3002
MONITORING_API_URL=http://localhost:8000

# ==========================================
# Performance Configuration
# ==========================================
# RAG Cache (LRU cache for search results)
RAG_CACHE_SIZE=100

# Response Cache (cache complete responses)
RESPONSE_CACHE_SIZE=50
RESPONSE_CACHE_TTL=3600

# Database Connection Pool
DB_POOL_SIZE=5

# ==========================================
# Feature Flags (optional)
# ==========================================
ENABLE_AWS_KB=true
ENABLE_RESPONSE_CACHE=true
ENABLE_SMART_REWRITING=true
ENABLE_PARALLEL_EXECUTION=true
```

---

## 🧪 Testing After Refactoring

### 1. Test với default values:
```bash
# Không cần .env, dùng defaults
python data_package/scripts/web_app.py
```

### 2. Test với custom ports:
```bash
# .env
WEB_APP_PORT=8080
MONITORING_API_PORT=9000

python data_package/scripts/web_app.py
# Should run on port 8080
```

### 3. Test với different cache sizes:
```bash
# .env
RESPONSE_CACHE_SIZE=100
RAG_CACHE_SIZE=200

python test_phase3.py
# Should use new cache sizes
```

---

## 📊 Impact Analysis

### Files cần sửa:
1. ✅ `data_package/scripts/web_app.py` - Main refactoring
2. ✅ `data_package/scripts/monitoring_api.py` - Port config
3. ✅ `data_package/scripts/test_all_levels.py` - URL config
4. ✅ `data_package/scripts/test_comprehensive.py` - URL config
5. ✅ `.env.example` - Add new variables
6. ✅ `README.md` - Update documentation

### Files KHÔNG cần sửa:
- ❌ Test data files (L1-L5 questions)
- ❌ Knowledge base files
- ❌ Database schema
- ❌ Frontend HTML/JS (gets URLs from backend)

---

## ⚠️ Breaking Changes

### Sau khi refactor:
1. **Cần update `.env`** với các biến mới (hoặc dùng defaults)
2. **Test scripts** cần load `.env` nếu chưa có
3. **Documentation** cần update với config mới

### Backward Compatibility:
- ✅ Tất cả có default values
- ✅ Không break existing deployments
- ✅ Chỉ cần update `.env` khi muốn customize

---

## 🎓 Best Practices Learned

### ❌ Bad:
```python
# Magic numbers everywhere
response = requests.get("http://localhost:8000/metrics/...")
cache = ResponseCache(max_size=50, ttl=3600)
```

### ✅ Good:
```python
# Centralized configuration
MONITORING_API_URL = os.getenv('MONITORING_API_URL', 'http://localhost:8000')
CACHE_SIZE = int(os.getenv('RESPONSE_CACHE_SIZE', '50'))

response = requests.get(f"{MONITORING_API_URL}/metrics/...")
cache = ResponseCache(max_size=CACHE_SIZE, ttl=CACHE_TTL)
```

### 🌟 Best:
```python
# Configuration class with validation
class Config:
    def __init__(self):
        self.monitoring_url = os.getenv('MONITORING_API_URL', 'http://localhost:8000')
        self.cache_size = int(os.getenv('RESPONSE_CACHE_SIZE', '50'))
        self.validate()
    
    def validate(self):
        if not self.monitoring_url.startswith('http'):
            raise ValueError("Invalid monitoring URL")
        if self.cache_size < 1:
            raise ValueError("Cache size must be positive")

config = Config()
```

---

**Tổng kết:** Dự án có khá nhiều hard code, nhưng hầu hết có thể refactor dễ dàng bằng cách:
1. Move sang environment variables
2. Giữ default values để backward compatible
3. Validate configuration at startup
4. Document tất cả config options

Bạn có muốn tôi implement refactoring này không? 🚀

# 🔧 Fix: ExpiredTokenException

## ❌ Vấn đề
```
[AWS KB unavailable, fallback to local]: An error occurred (ExpiredTokenException) 
when calling the Retrieve operation: The security token included in the request is expired
```

## ✅ Giải pháp

### Bước 1: Check credentials
```bash
python check_aws_credentials.py
```

### Bước 2: Refresh AWS credentials

#### Option A: AWS Academy Learner Lab
1. Mở AWS Academy Learner Lab
2. Click **AWS Details**
3. Click **Show** bên cạnh "AWS CLI"
4. Copy toàn bộ credentials:
   ```
   [default]
   aws_access_key_id=ASIA...
   aws_secret_access_key=...
   aws_session_token=...
   ```

#### Option B: AWS Console (IAM User)
1. Đăng nhập AWS Console
2. Vào **IAM** → **Users** → Your user
3. Tab **Security credentials**
4. Click **Create access key**
5. Copy Access Key ID và Secret Access Key

#### Option C: AWS CLI
```bash
aws configure
# Nhập Access Key ID
# Nhập Secret Access Key
# Region: us-east-1
```

### Bước 3: Update .env file

Mở file `.env` và update:

```env
# AWS Credentials (REQUIRED)
AWS_ACCESS_KEY_ID=ASIA...your_new_key...
AWS_SECRET_ACCESS_KEY=...your_new_secret...
AWS_SESSION_TOKEN=...your_new_token...  # Nếu dùng temporary credentials

# AWS Configuration
AWS_DEFAULT_REGION=us-east-1

# Knowledge Base ID (optional)
KNOWLEDGE_BASE_ID=ABCDEF1234  # Hoặc KB ID thật nếu có
```

### Bước 4: Restart server
```bash
restart_app.bat
```

### Bước 5: Verify
```bash
python check_aws_credentials.py
```

Nên thấy:
```
✅ SUCCESS: AWS Bedrock is accessible!
✓ Model: us.anthropic.claude-haiku-4-5-20251001-v1:0
✓ Response received: XX chars
```

---

## 🔍 Troubleshooting

### Vẫn lỗi sau khi update?

#### 1. Check .env file location
```bash
# .env phải ở root folder, cùng cấp với web_app.py
dir .env
```

#### 2. Check credentials format
- Không có dấu ngoặc kép
- Không có khoảng trắng thừa
- Mỗi dòng một biến

**ĐÚNG:**
```env
AWS_ACCESS_KEY_ID=ASIAXXX123
AWS_SECRET_ACCESS_KEY=abc123xyz
```

**SAI:**
```env
AWS_ACCESS_KEY_ID = "ASIAXXX123"  # Có dấu ngoặc và khoảng trắng
AWS_SECRET_ACCESS_KEY= abc123xyz  # Khoảng trắng sau =
```

#### 3. Restart lại server
```bash
# Kill tất cả processes
taskkill /F /IM python.exe

# Start lại
start_servers.bat
```

#### 4. Check console logs
Khi start server, nên thấy:
```
[STARTUP] ✓ AWS Bedrock client initialized
[STARTUP] ✓ Loaded 36 KB files into memory (168 KB)
```

Nếu thấy:
```
[STARTUP] ✗ AWS Bedrock client init failed: ...
[STARTUP] ⚠ App will work with local KB only (no Claude)
```

→ Credentials vẫn chưa đúng

---

## 💡 Lưu ý

### Temporary Credentials (AWS Academy)
- **Expire sau**: 3-4 giờ
- **Cần refresh**: Mỗi session học
- **Bao gồm**: Access Key + Secret Key + Session Token

### Permanent Credentials (IAM User)
- **Expire**: Không (trừ khi bạn xóa)
- **Không cần**: Session Token
- **Chỉ cần**: Access Key + Secret Key

### Local Fallback
Nếu AWS không available:
- ✅ App vẫn chạy được
- ✅ RAG search vẫn hoạt động (local KB)
- ❌ Không có Claude AI (không trả lời được)

---

## 🚀 Quick Commands

```bash
# Check credentials
python check_aws_credentials.py

# Restart server
restart_app.bat

# Kill all Python processes
taskkill /F /IM python.exe

# View .env file
type .env

# Edit .env file
notepad .env
```

---

## 📞 Vẫn không được?

1. Check file `.env` có tồn tại không:
   ```bash
   dir .env
   ```

2. Check credentials có đúng format không:
   ```bash
   type .env
   ```

3. Check server logs khi start:
   ```bash
   start_servers.bat
   # Xem console output
   ```

4. Test credentials trực tiếp:
   ```bash
   python check_aws_credentials.py
   ```

---

**Lưu ý**: Credentials từ AWS Academy expire sau 3-4 giờ. Bạn cần refresh mỗi khi bắt đầu session học mới.

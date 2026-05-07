# 🔧 Setup Guide

## Prerequisites

- Python 3.11+
- AWS Account with Bedrock access
- Git (optional)

---

## Step 1: Clone/Download Project

```bash
git clone <repository-url>
cd <project-folder>
```

Or download and extract ZIP file.

---

## Step 2: Setup Environment Variables

### Copy example file
```bash
cp .env.example .env
```

### Edit .env file
Open `.env` in text editor and fill in:

```env
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_SESSION_TOKEN=your_session_token_here  # Optional
KNOWLEDGE_BASE_ID=your_kb_id_here
```

### Get AWS Credentials

#### Option A: IAM User (Recommended)
1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Create new user or use existing
3. Attach policy: `AmazonBedrockFullAccess`
4. Create access key
5. Copy Access Key ID and Secret Access Key
6. No session token needed

#### Option B: AWS SSO
1. Run: `aws sso login`
2. Run: `aws configure export-credentials --profile your-profile`
3. Copy all three values (including session token)
4. Note: Session token expires (1-12 hours)

#### Option C: AWS CLI
1. Run: `aws configure`
2. Enter credentials
3. App will use `~/.aws/credentials` automatically

### Get Knowledge Base ID

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to **Knowledge Bases**
3. Create new or use existing Knowledge Base
4. Copy the Knowledge Base ID (10 characters)

**Or use local fallback:**
- Set `KNOWLEDGE_BASE_ID=ABCDEF1234` (dummy value)
- App will use local markdown files from `data_package/knowledge_base/`

---

## Step 3: Install Dependencies

### Option A: Using uv (Recommended)
```bash
cd data_package/scripts
uv sync
```

### Option B: Using pip
```bash
cd data_package/scripts
pip install -r requirements.txt
```

### Option C: Using virtual environment
```bash
cd data_package/scripts
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

---

## Step 4: Setup Database

```bash
cd data_package/scripts
python seed_data.py
```

This creates `geekbrain.db` with sample data.

---

## Step 5: Start Application

```bash
# From project root
start_servers.bat
```

This starts:
- Monitoring API on port 8000
- Web App on port 3002

---

## Step 6: Open in Browser

```
http://localhost:3002
```

---

## Verify Setup

### Test 1: Check servers are running
```bash
# Check processes
tasklist | findstr python
tasklist | findstr uvicorn
```

### Test 2: Test monitoring API
```
http://localhost:8000/metrics/PaymentGW
```

Should return JSON with metrics.

### Test 3: Test web app
```
http://localhost:3002
```

Should show GeekBrain AI interface.

### Test 4: Ask a question
Type: "What is PaymentGW?"

Should get answer with citations.

---

## Troubleshooting

### Issue: "Unable to locate credentials"
**Solution**: Check `.env` file has correct AWS credentials

### Issue: "ExpiredToken"
**Solution**: Refresh `AWS_SESSION_TOKEN` (if using temporary credentials)

### Issue: "AccessDeniedException"
**Solution**: Add `AmazonBedrockFullAccess` policy to IAM user

### Issue: "Port already in use"
**Solution**: Kill existing processes
```bash
taskkill /F /IM python.exe /IM uvicorn.exe
```

### Issue: "Module not found"
**Solution**: Install dependencies
```bash
cd data_package/scripts
pip install -r requirements.txt
```

### Issue: "Database not found"
**Solution**: Run seed script
```bash
cd data_package/scripts
python seed_data.py
```

---

## Test AWS Connection

```bash
# Test AWS credentials
aws bedrock list-foundation-models --region us-east-1

# Test Knowledge Base
aws bedrock-agent-runtime retrieve \
  --knowledge-base-id YOUR_KB_ID \
  --retrieval-query text="test" \
  --region us-east-1
```

---

## Next Steps

1. ✅ Setup complete
2. 📖 Read [README.md](README.md) for features
3. 🧪 Read [TESTING.md](TESTING.md) for testing
4. 🚀 Start building!

---

## Quick Commands

```bash
# Start
start_servers.bat

# Restart
restart_app.bat

# Stop
taskkill /F /IM python.exe /IM uvicorn.exe

# Test
cd data_package/scripts
python test_all_levels.py
```

---

**Setup complete! Enjoy GeekBrain AI! 🤖**

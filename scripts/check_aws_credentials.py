#!/usr/bin/env python3
"""
Check AWS credentials status and provide guidance
"""
import os
import boto3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("🔐 AWS CREDENTIALS CHECK")
print("=" * 70)

# Check if credentials are set
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
session_token = os.getenv('AWS_SESSION_TOKEN')
region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
kb_id = os.getenv('KNOWLEDGE_BASE_ID')

print("\n[1] Environment Variables:")
print("-" * 70)
print(f"✓ AWS_ACCESS_KEY_ID: {'Set' if access_key else '✗ NOT SET'}")
print(f"✓ AWS_SECRET_ACCESS_KEY: {'Set' if secret_key else '✗ NOT SET'}")
print(f"✓ AWS_SESSION_TOKEN: {'Set' if session_token else '✗ NOT SET (optional)'}")
print(f"✓ AWS_DEFAULT_REGION: {region}")
print(f"✓ KNOWLEDGE_BASE_ID: {kb_id if kb_id else '✗ NOT SET'}")

if not access_key or not secret_key:
    print("\n❌ ERROR: AWS credentials not found in .env file!")
    print("\nPlease add to .env:")
    print("  AWS_ACCESS_KEY_ID=your_access_key")
    print("  AWS_SECRET_ACCESS_KEY=your_secret_key")
    print("  AWS_SESSION_TOKEN=your_session_token  # If using temporary credentials")
    exit(1)

# Test Bedrock connection
print("\n[2] Testing AWS Bedrock Connection:")
print("-" * 70)
try:
    bedrock = boto3.client('bedrock-runtime', region_name=region)
    
    # Try a simple call to check if credentials work
    response = bedrock.converse(
        modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        messages=[{"role": "user", "content": [{"text": "Hi"}]}]
    )
    
    print("✅ SUCCESS: AWS Bedrock is accessible!")
    print(f"✓ Model: us.anthropic.claude-haiku-4-5-20251001-v1:0")
    print(f"✓ Response received: {len(response['output']['message']['content'][0]['text'])} chars")
    
except Exception as e:
    error_type = type(e).__name__
    error_msg = str(e)
    
    print(f"❌ ERROR: {error_type}")
    print(f"   {error_msg}")
    
    if "ExpiredToken" in error_type or "expired" in error_msg.lower():
        print("\n⚠️  YOUR AWS CREDENTIALS HAVE EXPIRED!")
        print("\nTo fix this:")
        print("1. Go to AWS Console")
        print("2. Get new temporary credentials")
        print("3. Update .env file with new credentials:")
        print("   - AWS_ACCESS_KEY_ID")
        print("   - AWS_SECRET_ACCESS_KEY")
        print("   - AWS_SESSION_TOKEN")
        print("4. Restart the server: restart_app.bat")
        
    elif "AccessDenied" in error_type or "access denied" in error_msg.lower():
        print("\n⚠️  ACCESS DENIED!")
        print("\nYour credentials don't have permission to use Bedrock.")
        print("Please check IAM permissions.")
        
    elif "InvalidSignature" in error_type:
        print("\n⚠️  INVALID CREDENTIALS!")
        print("\nYour AWS credentials are incorrect.")
        print("Please check .env file.")
    
    else:
        print("\n⚠️  UNKNOWN ERROR!")
        print("\nPlease check:")
        print("1. AWS credentials are correct")
        print("2. Region is correct (us-east-1)")
        print("3. Internet connection is working")

# Test Knowledge Base (if ID is set)
if kb_id and kb_id != "ABCDEF1234":
    print("\n[3] Testing Knowledge Base Connection:")
    print("-" * 70)
    try:
        bedrock_agent = boto3.client('bedrock-agent-runtime', region_name=region)
        response = bedrock_agent.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={'text': 'test'},
            retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': 1}}
        )
        print(f"✅ SUCCESS: Knowledge Base is accessible!")
        print(f"✓ KB ID: {kb_id}")
        print(f"✓ Results: {len(response.get('retrievalResults', []))} documents")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        print("\n⚠️  Knowledge Base not accessible, but local fallback will work.")
else:
    print("\n[3] Knowledge Base:")
    print("-" * 70)
    print("⚠️  KB ID not set or using placeholder")
    print("✓ Local fallback will be used (35+ markdown files)")

print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)

if access_key and secret_key:
    print("✅ Credentials are configured")
    print("✅ Local KB fallback available (35+ files)")
    print("\n💡 If you see 'ExpiredToken' errors:")
    print("   1. Refresh AWS credentials in .env")
    print("   2. Run: restart_app.bat")
else:
    print("❌ Credentials not configured")
    print("⚠️  App will not work without AWS credentials")

print("=" * 70)

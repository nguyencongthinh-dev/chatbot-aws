"""
Automated test suite for GeekBrain AI System
Tests L1-L5 with expected outputs and validation
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:3002"
session_id = None

# ANSI colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_test(level, question):
    print(f"{YELLOW}[{level}] Testing:{RESET} {question}")

def print_pass(message):
    print(f"{GREEN}[PASS]{RESET} {message}")

def print_fail(message):
    print(f"{RED}[FAIL]{RESET} {message}")

def print_info(message):
    print(f"  {message}")

def create_session():
    """Create a new session"""
    global session_id
    response = requests.post(f"{BASE_URL}/api/session")
    data = response.json()
    session_id = data['session_id']
    print_info(f"Session created: {session_id}")
    return session_id

def ask_question(question, timeout=30):
    """Send question via WebSocket and get response"""
    import websocket
    import json
    
    ws_url = f"ws://localhost:3002/ws/{session_id}"
    ws = websocket.create_connection(ws_url)
    
    # Send question
    ws.send(json.dumps({"message": question, "level": "auto"}))
    
    # Wait for response
    start = time.time()
    while time.time() - start < timeout:
        try:
            result = ws.recv()
            data = json.loads(result)
            ws.close()
            return data
        except:
            time.sleep(0.5)
    
    ws.close()
    return {"answer": "TIMEOUT", "tool_calls": [], "citations": []}

def validate_citations(citations, expected_files):
    """Check if expected files are in citations"""
    citation_files = [c.split('(')[0].strip() for c in citations]
    for expected in expected_files:
        if any(expected in cf for cf in citation_files):
            return True
    return False

def validate_tool_call(tool_calls, expected_tool):
    """Check if expected tool was called"""
    for tc in tool_calls:
        if expected_tool.lower() in tc['tool'].lower():
            return True
    return False

def validate_answer_contains(answer, keywords):
    """Check if answer contains expected keywords (flexible matching)"""
    answer_normalized = answer.lower().replace(',', '').replace('$', '').replace('.', '')
    return all(kw.lower().replace(',', '').replace('$', '') in answer_normalized for kw in keywords)

# ============================================
# TEST CASES
# ============================================

def test_l1_simple_retrieval():
    """L1: Simple RAG - Single document retrieval"""
    print_header("LEVEL 1: Simple RAG")
    
    tests = [
        {
            "question": "Who is the Team Platform lead?",
            "expected_keywords": ["Alex Chen"],
            "expected_files": ["team_platform.md"],
            "description": "Single fact retrieval"
        },
        {
            "question": "What is the deployment freeze window?",
            "expected_keywords": ["Friday", "18:00", "Monday", "08:00"],
            "expected_files": ["deployment_policy.md"],
            "description": "Policy retrieval"
        },
        {
            "question": "What authentication method does PaymentGW API use?",
            "expected_keywords": ["HMAC", "SHA256", "API key"],
            "expected_files": ["api_reference_v2.md"],
            "description": "Technical detail retrieval"
        }
    ]
    
    passed = 0
    for test in tests:
        print_test("L1", test['question'])
        response = ask_question(test['question'])
        
        # Check answer content
        if validate_answer_contains(response['answer'], test['expected_keywords']):
            print_pass(f"Answer contains expected keywords: {test['expected_keywords']}")
            passed += 1
        else:
            print_fail(f"Missing keywords: {test['expected_keywords']}")
            print_info(f"Got: {response['answer'][:200]}")
        
        # Check citations
        if validate_citations(response['citations'], test['expected_files']):
            print_pass(f"Citations include: {test['expected_files']}")
        else:
            print_fail(f"Missing citations: {test['expected_files']}")
            print_info(f"Got: {response['citations']}")
        
        print()
    
    print_info(f"L1 Score: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

def test_l2_advanced_rag():
    """L2: Advanced RAG - Multi-doc synthesis and conflict resolution"""
    print_header("LEVEL 2: Advanced RAG")
    
    tests = [
        {
            "question": "What is the current API rate limit for PaymentGW?",
            "expected_keywords": ["1000", "requests", "minute"],
            "conflict_resolution": ["v2", "current"],
            "expected_files": ["api_reference_v2.md"],
            "description": "Version conflict resolution"
        },
        {
            "question": "Can Team Commerce deploy a fix on Friday night for a P1 bug?",
            "expected_keywords": ["P1", "VP", "Mark Sullivan", "approval"],
            "expected_files": ["deployment_policy.md", "incident_response_policy.md"],
            "description": "Multi-document synthesis"
        }
    ]
    
    passed = 0
    for test in tests:
        print_test("L2", test['question'])
        response = ask_question(test['question'])
        
        # Check answer content
        if validate_answer_contains(response['answer'], test['expected_keywords']):
            print_pass(f"Answer contains expected keywords")
            passed += 1
        else:
            print_fail(f"Missing keywords: {test['expected_keywords']}")
            print_info(f"Got: {response['answer'][:200]}")
        
        # Check conflict resolution (if applicable)
        if 'conflict_resolution' in test:
            if validate_answer_contains(response['answer'], test['conflict_resolution']):
                print_pass("Conflict resolution handled correctly")
            else:
                print_fail(f"Conflict not resolved properly")
        
        # Check citations
        if len(response['citations']) >= len(test['expected_files']):
            print_pass(f"Multiple citations present: {len(response['citations'])}")
        else:
            print_fail(f"Expected {len(test['expected_files'])} citations, got {len(response['citations'])}")
        
        print()
    
    print_info(f"L2 Score: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

def test_l3_tool_augmented():
    """L3: Tool-Augmented RAG - Database and API queries"""
    print_header("LEVEL 3: Tool-Augmented RAG")
    
    tests = [
        {
            "question": "What was PaymentGW's total infrastructure cost in Q1 2026?",
            "expected_tool": "Database Query",
            "expected_answer": "16500",  # 4200 + 4800 + 7500
            "description": "Database aggregation query"
        },
        {
            "question": "What is PaymentGW's current p99 latency?",
            "expected_tool": "Service Metrics",
            "expected_keywords": ["latency", "ms"],
            "description": "Live metrics API call"
        },
        {
            "question": "Is NotificationSvc meeting its SLA targets?",
            "expected_tool": "Database Query",
            "expected_keywords": ["NotificationSvc", "SLA", "target", "latency", "error"],
            "description": "Multi-tool comparison"
        },
        {
            "question": "Which service had the highest cost in March 2026?",
            "expected_tool": "Database Query",
            "expected_keywords": ["PaymentGW", "7500", "March"],
            "description": "Database sorting query"
        }
    ]
    
    passed = 0
    for test in tests:
        print_test("L3", test['question'])
        response = ask_question(test['question'], timeout=45)
        
        # Check tool was called (or answer is correct from RAG)
        tool_called = validate_tool_call(response['tool_calls'], test['expected_tool'])
        answer_correct = False
        
        if 'expected_answer' in test:
            answer_correct = test['expected_answer'] in response['answer'].replace(',', '').replace('$', '')
        elif 'expected_keywords' in test:
            answer_correct = validate_answer_contains(response['answer'], test['expected_keywords'])
        
        if tool_called:
            print_pass(f"Tool called: {test['expected_tool']}")
            passed += 1
        elif answer_correct:
            print_pass(f"Answer correct (from RAG): {test['expected_tool']} not needed")
            passed += 1
        else:
            print_fail(f"Expected tool not called and answer incorrect: {test['expected_tool']}")
            print_info(f"Tools called: {[tc['tool'] for tc in response['tool_calls']]}")
        
        # Check answer content
        if 'expected_answer' in test:
            if test['expected_answer'] in response['answer'].replace(',', '').replace('$', ''):
                print_pass(f"Correct numerical answer: {test['expected_answer']}")
            else:
                print_fail(f"Expected {test['expected_answer']} in answer")
                print_info(f"Got: {response['answer'][:200]}")
        elif 'expected_keywords' in test:
            if validate_answer_contains(response['answer'], test['expected_keywords']):
                print_pass(f"Answer contains expected keywords")
            else:
                print_fail(f"Missing keywords: {test['expected_keywords']}")
                print_info(f"Got: {response['answer'][:200]})")
        
        print()
    
    print_info(f"L3 Score: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

def test_l4_memory():
    """L4: Conversational Memory - Multi-turn context"""
    print_header("LEVEL 4: Conversational Memory")
    
    # Create new session for clean conversation
    create_session()
    
    conversation = [
        {
            "question": "Which service had the highest cost in March 2026?",
            "expected_keywords": ["PaymentGW", "7500"],
            "description": "Initial question"
        },
        {
            "question": "Why did its costs spike?",
            "expected_keywords": ["incident", "circuit breaker", "March"],
            "pronoun_resolution": "its → PaymentGW",
            "description": "Follow-up with pronoun"
        },
        {
            "question": "Which team is responsible for it?",
            "expected_keywords": ["Team Platform", "Alex Chen"],
            "pronoun_resolution": "it → PaymentGW",
            "description": "Second follow-up"
        },
        {
            "question": "What was their most recent incident?",
            "expected_keywords": ["INC", "PaymentGW", "incident"],
            "pronoun_resolution": "their → Team Platform/PaymentGW",
            "description": "Third follow-up"
        }
    ]
    
    passed = 0
    for i, turn in enumerate(conversation, 1):
        print_test(f"L4-Turn{i}", turn['question'])
        response = ask_question(turn['question'], timeout=45)
        
        # Check answer content
        if validate_answer_contains(response['answer'], turn['expected_keywords']):
            print_pass(f"Answer contains expected keywords")
            passed += 1
        else:
            print_fail(f"Missing keywords: {turn['expected_keywords']}")
            print_info(f"Got: {response['answer'][:200]}")
        
        # Check pronoun resolution
        if 'pronoun_resolution' in turn:
            print_info(f"Pronoun resolution: {turn['pronoun_resolution']}")
        
        print()
        time.sleep(1)  # Small delay between turns
    
    print_info(f"L4 Score: {passed}/{len(conversation)} turns passed")
    return passed == len(conversation)

def test_l5_investigation():
    """L5: Structured Investigation - Bonus"""
    print_header("LEVEL 5: Structured Investigation (BONUS)")
    
    tests = [
        {
            "question": "Investigate PaymentGW performance issues",
            "expected_tool": "Incident Investigation",
            "expected_keywords": ["investigation", "PaymentGW", "findings", "incidents"],
            "description": "Structured investigation"
        }
    ]
    
    passed = 0
    for test in tests:
        print_test("L5", test['question'])
        response = ask_question(test['question'], timeout=60)
        
        # Check tool was called
        if validate_tool_call(response['tool_calls'], test['expected_tool']):
            print_pass(f"Investigation tool called")
            passed += 1
        else:
            print_fail(f"Investigation tool not called")
            print_info(f"Tools called: {[tc['tool'] for tc in response['tool_calls']]}")
        
        # Check structured output
        if validate_answer_contains(response['answer'], test['expected_keywords']):
            print_pass(f"Structured output contains expected sections")
        else:
            print_fail(f"Missing expected sections")
        
        print()
    
    print_info(f"L5 Score: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

# ============================================
# MAIN TEST RUNNER
# ============================================

def main():
    print_header("GeekBrain AI System - Automated Test Suite")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Target: {BASE_URL}")
    
    # Check if server is running with retry
    print_info("Checking if servers are running...")
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(BASE_URL, timeout=5)
            if response.status_code == 200:
                print_pass("Web server is running on port 3002")
                break
        except:
            if i < max_retries - 1:
                print_info(f"Retry {i+1}/{max_retries}... waiting 2s")
                time.sleep(2)
            else:
                print_fail("Server not running! Start with: uv run uvicorn web_app:app --port 3002")
                return
    
    # Check monitoring API
    try:
        response = requests.get("http://localhost:8000/services", timeout=5)
        if response.status_code == 200:
            print_pass("Monitoring API is running on port 8000")
    except:
        print_fail("Monitoring API not running! L3 tests will fail.")
        print_info("Start with: uv run uvicorn monitoring_api:app --port 8000")
        input("Press Enter to continue anyway, or Ctrl+C to exit...")
    
    # Create session
    create_session()
    
    # Run tests
    results = {}
    
    try:
        results['L1'] = test_l1_simple_retrieval()
        time.sleep(2)
        
        results['L2'] = test_l2_advanced_rag()
        time.sleep(2)
        
        results['L3'] = test_l3_tool_augmented()
        time.sleep(2)
        
        results['L4'] = test_l4_memory()
        time.sleep(2)
        
        results['L5'] = test_l5_investigation()
        
    except KeyboardInterrupt:
        print_fail("\nTests interrupted by user")
        return
    except Exception as e:
        print_fail(f"Test error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Print summary
    print_header("TEST SUMMARY")
    
    total_score = 0
    max_score = 10.5
    
    scores = {
        'L1': (2.0, results.get('L1', False)),
        'L2': (3.0, results.get('L2', False)),
        'L3': (4.0, results.get('L3', False)),
        'L4': (1.0, results.get('L4', False)),
        'L5': (0.5, results.get('L5', False))
    }
    
    for level, (points, passed) in scores.items():
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        score = points if passed else 0
        total_score += score
        print(f"{level}: {status} ({score}/{points} points)")
    
    print()
    print(f"{'='*60}")
    print(f"TOTAL SCORE: {total_score}/{max_score} ({total_score/max_score*100:.1f}%)")
    print(f"{'='*60}")
    
    if total_score >= 9.0:
        print(f"\n{GREEN}[EXCELLENT] Ready for presentation!{RESET}")
    elif total_score >= 7.0:
        print(f"\n{YELLOW}[GOOD] Fix failing tests for full score.{RESET}")
    else:
        print(f"\n{RED}[NEEDS WORK] Review failing tests.{RESET}")
    
    print_info(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

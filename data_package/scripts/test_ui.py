"""
UI Testing with Selenium - Tests actual web interface
Requires: pip install selenium
"""

import time
import json
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
except ImportError:
    print("ERROR: Selenium not installed!")
    print("Install with: pip install selenium")
    exit(1)

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_test(level, question):
    print(f"{YELLOW}[{level}]{RESET} Testing: {question[:60]}...")

def print_pass(message=""):
    print(f"  {GREEN}✓ PASS{RESET} {message}")

def print_fail(message):
    print(f"  {RED}✗ FAIL{RESET} {message}")

def print_info(message):
    print(f"  → {message}")

class GeekBrainUITester:
    def __init__(self):
        print("Initializing Chrome WebDriver...")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 30)
            print(f"{GREEN}✓ WebDriver initialized{RESET}\n")
        except Exception as e:
            print(f"{RED}✗ Failed to initialize WebDriver: {e}{RESET}")
            print("\nTroubleshooting:")
            print("1. Install Chrome browser")
            print("2. Install ChromeDriver: pip install webdriver-manager")
            print("3. Or download from: https://chromedriver.chromium.org/")
            raise
    
    def open_app(self):
        """Open the web application"""
        print("Opening http://localhost:3002...")
        self.driver.get("http://localhost:3002")
        time.sleep(2)
        
        # Check if page loaded
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "userInput")))
            print(f"{GREEN}✓ App loaded successfully{RESET}\n")
            return True
        except:
            print(f"{RED}✗ App failed to load{RESET}")
            return False
    
    def send_message(self, question):
        """Send a message and wait for response"""
        try:
            # Find input box
            input_box = self.driver.find_element(By.ID, "userInput")
            input_box.clear()
            input_box.send_keys(question)
            
            # Click send button
            send_btn = self.driver.find_element(By.ID, "sendBtn")
            send_btn.click()
            
            # Wait for response (look for new message)
            time.sleep(3)  # Give time for LLM to respond
            
            # Wait for typing indicator to disappear
            max_wait = 60  # 60 seconds max
            start = time.time()
            while time.time() - start < max_wait:
                try:
                    typing = self.driver.find_element(By.ID, "typingIndicator")
                    if typing:
                        time.sleep(1)
                        continue
                except:
                    break  # Typing indicator gone
            
            # Get last assistant message
            messages = self.driver.find_elements(By.CSS_SELECTOR, ".msg.assistant")
            if messages:
                last_msg = messages[-1]
                answer = last_msg.find_element(By.CSS_SELECTOR, ".msg-bubble").text
                
                # Get citations
                citations = []
                try:
                    citation_elements = last_msg.find_elements(By.CSS_SELECTOR, ".citation-chip")
                    citations = [c.text for c in citation_elements]
                except:
                    pass
                
                # Get tool calls
                tool_calls = []
                try:
                    tool_elements = last_msg.find_elements(By.CSS_SELECTOR, ".tool-badge")
                    tool_calls = [t.text for t in tool_elements]
                except:
                    pass
                
                return {
                    "answer": answer,
                    "citations": citations,
                    "tool_calls": tool_calls
                }
            else:
                return {"answer": "", "citations": [], "tool_calls": []}
                
        except Exception as e:
            print(f"  {RED}Error sending message: {e}{RESET}")
            return None
    
    def new_chat(self):
        """Click New Chat button to reset conversation"""
        try:
            new_chat_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'New Chat')]")
            new_chat_btn.click()
            time.sleep(1)
            return True
        except:
            return False
    
    def take_screenshot(self, filename):
        """Take screenshot of current page"""
        try:
            self.driver.save_screenshot(filename)
            print(f"  📸 Screenshot saved: {filename}")
            return True
        except Exception as e:
            print(f"  {RED}Screenshot failed: {e}{RESET}")
            return False
    
    def close(self):
        """Close the browser"""
        self.driver.quit()

def test_l1_ui(tester):
    """Test L1 on UI"""
    print_header("LEVEL 1: Simple RAG - UI Test")
    
    tests = [
        {
            "question": "Who is the Team Platform lead?",
            "expected_keywords": ["Alex Chen"],
            "expected_citations": ["team_platform.md"]
        },
        {
            "question": "What is the deployment freeze window?",
            "expected_keywords": ["Friday", "18:00", "Monday", "08:00"],
            "expected_citations": ["deployment_policy.md"]
        },
        {
            "question": "What authentication method does PaymentGW API use?",
            "expected_keywords": ["HMAC", "SHA256"],
            "expected_citations": ["api_reference"]
        }
    ]
    
    passed = 0
    for i, test in enumerate(tests, 1):
        print_test(f"L1.{i}", test['question'])
        
        response = tester.send_message(test['question'])
        if not response:
            print_fail("No response received")
            continue
        
        # Check keywords
        answer_lower = response['answer'].lower()
        keywords_found = all(kw.lower() in answer_lower for kw in test['expected_keywords'])
        
        if keywords_found:
            print_pass(f"Keywords found: {test['expected_keywords']}")
            passed += 1
        else:
            print_fail(f"Missing keywords: {test['expected_keywords']}")
            print_info(f"Answer: {response['answer'][:100]}...")
        
        # Check citations
        if response['citations']:
            print_info(f"Citations: {response['citations']}")
        else:
            print_info("No citations displayed")
        
        time.sleep(2)
    
    print(f"\n{GREEN if passed == len(tests) else YELLOW}L1 Score: {passed}/{len(tests)}{RESET}")
    return passed == len(tests)

def test_l3_ui(tester):
    """Test L3 on UI"""
    print_header("LEVEL 3: Tool-Augmented RAG - UI Test")
    
    tests = [
        {
            "question": "What was PaymentGW's total infrastructure cost in Q1 2026?",
            "expected_answer": "16500",
            "expected_tool": "Database Query"
        },
        {
            "question": "What is PaymentGW's current p99 latency?",
            "expected_keywords": ["latency", "ms"],
            "expected_tool": "Service Metrics"
        },
        {
            "question": "Which service had the highest cost in March 2026?",
            "expected_keywords": ["PaymentGW", "7500"],
            "expected_tool": "Database Query"
        }
    ]
    
    passed = 0
    for i, test in enumerate(tests, 1):
        print_test(f"L3.{i}", test['question'])
        
        response = tester.send_message(test['question'])
        if not response:
            print_fail("No response received")
            continue
        
        # Check tool was called
        if response['tool_calls']:
            print_info(f"Tools called: {response['tool_calls']}")
            if any(test['expected_tool'].lower() in tc.lower() for tc in response['tool_calls']):
                print_pass(f"Tool called: {test['expected_tool']}")
                passed += 1
            else:
                print_fail(f"Expected tool not called: {test['expected_tool']}")
        else:
            print_fail("No tools called")
        
        # Check answer
        answer_normalized = response['answer'].replace(',', '').replace('$', '')
        if 'expected_answer' in test:
            if test['expected_answer'] in answer_normalized:
                print_info(f"✓ Correct answer: {test['expected_answer']}")
            else:
                print_info(f"Answer: {response['answer'][:100]}...")
        
        time.sleep(2)
    
    print(f"\n{GREEN if passed == len(tests) else YELLOW}L3 Score: {passed}/{len(tests)}{RESET}")
    return passed == len(tests)

def test_l4_ui(tester):
    """Test L4 conversation on UI"""
    print_header("LEVEL 4: Conversational Memory - UI Test")
    
    # Start new conversation
    tester.new_chat()
    time.sleep(1)
    
    conversation = [
        ("Which service had the highest cost in March 2026?", ["PaymentGW", "7500"]),
        ("Why did its costs spike?", ["incident", "March"]),
        ("Which team is responsible for it?", ["Team Platform", "Alex Chen"]),
        ("What was their most recent incident?", ["INC", "PaymentGW"])
    ]
    
    passed = 0
    for i, (question, keywords) in enumerate(conversation, 1):
        print_test(f"L4.{i}", question)
        
        response = tester.send_message(question)
        if not response:
            print_fail("No response received")
            continue
        
        # Check keywords
        answer_lower = response['answer'].lower().replace(',', '').replace('$', '')
        keywords_found = any(kw.lower() in answer_lower for kw in keywords)
        
        if keywords_found:
            print_pass(f"Context maintained")
            passed += 1
        else:
            print_fail(f"Context lost - expected: {keywords}")
            print_info(f"Answer: {response['answer'][:100]}...")
        
        time.sleep(2)
    
    print(f"\n{GREEN if passed == len(conversation) else YELLOW}L4 Score: {passed}/{len(conversation)}{RESET}")
    return passed == len(conversation)

def test_l5_ui(tester):
    """Test L5 investigation on UI"""
    print_header("LEVEL 5: Structured Investigation - UI Test")
    
    tester.new_chat()
    time.sleep(1)
    
    print_test("L5", "Investigate PaymentGW performance issues")
    
    response = tester.send_message("Investigate PaymentGW performance issues")
    if not response:
        print_fail("No response received")
        return False
    
    # Check tool was called
    if response['tool_calls']:
        if any("investigation" in tc.lower() or "incident" in tc.lower() for tc in response['tool_calls']):
            print_pass("Investigation tool called")
            print_info(f"Tools: {response['tool_calls']}")
            
            # Check for structured output keywords
            keywords = ["investigation", "findings", "metrics", "incidents"]
            found = sum(1 for kw in keywords if kw.lower() in response['answer'].lower())
            
            if found >= 2:
                print_pass(f"Structured output detected ({found}/4 keywords)")
                return True
            else:
                print_fail(f"Insufficient structure ({found}/4 keywords)")
                return False
        else:
            print_fail("Investigation tool not called")
            return False
    else:
        print_fail("No tools called")
        return False

def main():
    print_header("GeekBrain AI - UI Testing Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize tester
    try:
        tester = GeekBrainUITester()
    except:
        print(f"\n{RED}Cannot initialize WebDriver. Exiting.{RESET}")
        return
    
    try:
        # Open app
        if not tester.open_app():
            print(f"{RED}Cannot open app. Make sure server is running on port 3002{RESET}")
            return
        
        # Take initial screenshot
        tester.take_screenshot("screenshots/00_initial.png")
        
        # Run tests
        results = {}
        
        results['L1'] = test_l1_ui(tester)
        tester.take_screenshot("screenshots/01_l1_complete.png")
        time.sleep(2)
        
        results['L3'] = test_l3_ui(tester)
        tester.take_screenshot("screenshots/02_l3_complete.png")
        time.sleep(2)
        
        results['L4'] = test_l4_ui(tester)
        tester.take_screenshot("screenshots/03_l4_complete.png")
        time.sleep(2)
        
        results['L5'] = test_l5_ui(tester)
        tester.take_screenshot("screenshots/04_l5_complete.png")
        
        # Summary
        print_header("UI TEST SUMMARY")
        
        total_passed = sum(1 for v in results.values() if v)
        total_tests = len(results)
        
        for level, passed in results.items():
            status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
            print(f"{level}: {status}")
        
        print(f"\n{'='*70}")
        print(f"TOTAL: {total_passed}/{total_tests} levels passed")
        print(f"{'='*70}")
        
        if total_passed == total_tests:
            print(f"\n{GREEN}[EXCELLENT] All UI tests passed!{RESET}")
            print(f"Screenshots saved in screenshots/ directory")
        else:
            print(f"\n{YELLOW}[PARTIAL] Some tests failed{RESET}")
            print(f"Review screenshots for details")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    finally:
        # Cleanup
        print("\nClosing browser...")
        tester.close()
        print(f"{GREEN}✓ Browser closed{RESET}")

if __name__ == "__main__":
    # Create screenshots directory
    import os
    os.makedirs("screenshots", exist_ok=True)
    
    main()

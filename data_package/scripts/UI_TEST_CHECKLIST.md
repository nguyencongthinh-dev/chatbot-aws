# GeekBrain AI - UI Testing Checklist

## 🎯 Manual UI Testing Guide

Open http://localhost:3002 and follow this checklist.

---

## ✅ Pre-Test Setup

- [ ] Web server running on port 3002
- [ ] Monitoring API running on port 8000
- [ ] Browser opened to http://localhost:3002
- [ ] Page loaded successfully (see GeekBrain AI logo)

---

## 📋 LEVEL 1: Simple RAG (2.0 points)

### Test 1.1: Team Lead Question
**Question:** `Who is the Team Platform lead?`

**Expected:**
- Answer: "Alex Chen"
- Citations visible: `team_platform.md (0.95)` or similar
- No tool badges

**Check:**
- [ ] Answer contains "Alex Chen"
- [ ] Citation chip visible at bottom
- [ ] Citation shows confidence score
- [ ] Answer is accurate

**Screenshot:** `L1_test1_team_lead.png`

---

### Test 1.2: Policy Question
**Question:** `What is the deployment freeze window?`

**Expected:**
- Answer: "Friday 18:00 to Monday 08:00"
- Citations: `deployment_policy.md`

**Check:**
- [ ] Answer mentions Friday 18:00
- [ ] Answer mentions Monday 08:00
- [ ] Citation present
- [ ] Answer is clear

**Screenshot:** `L1_test2_policy.png`

---

### Test 1.3: Technical Detail
**Question:** `What authentication method does PaymentGW API use?`

**Expected:**
- Answer: "API key + HMAC-SHA256 signature"
- Citations: `api_reference_v2.md`

**Check:**
- [ ] Answer mentions HMAC-SHA256
- [ ] Answer mentions API key
- [ ] Citation present
- [ ] Technical details accurate

**Screenshot:** `L1_test3_auth.png`

---

## 📋 LEVEL 2: Advanced RAG (3.0 points)

### Test 2.1: Version Conflict
**Question:** `What is the current API rate limit for PaymentGW?`

**Expected:**
- Answer: "1,000 requests per minute (v2)"
- Should mention v1 had 500 (archived)
- Citations: Both `api_reference_v2.md` and `api_reference_v1_archived.md`

**Check:**
- [ ] Answer says 1,000 req/min
- [ ] Mentions v2 is current
- [ ] Acknowledges v1 was 500
- [ ] Multiple citations visible
- [ ] Conflict resolved correctly

**Screenshot:** `L2_test1_conflict.png`

---

### Test 2.2: Multi-Document Synthesis
**Question:** `Can Team Commerce deploy a fix on Friday night for a P1 bug?`

**Expected:**
- Answer: "Yes, with VP approval (Mark Sullivan)"
- Should synthesize: deployment freeze + P1 override + team info
- Citations: Multiple docs

**Check:**
- [ ] Answer says "Yes" or "can deploy"
- [ ] Mentions P1 override
- [ ] Mentions VP approval
- [ ] Mentions Mark Sullivan
- [ ] Multiple citations (3+)

**Screenshot:** `L2_test2_synthesis.png`

---

## 📋 LEVEL 3: Tool-Augmented RAG (4.0 points)

### Test 3.1: Database Aggregation
**Question:** `What was PaymentGW's total infrastructure cost in Q1 2026?`

**Expected:**
- Answer: "$16,500" (exact)
- Tool badge: 🗄️ Database Query
- Should show SQL in tool badge

**Check:**
- [ ] Answer is exactly $16,500
- [ ] Tool badge visible (yellow/gold color)
- [ ] Badge says "Database Query"
- [ ] Badge shows SQL snippet
- [ ] Number is exact, not estimated

**Screenshot:** `L3_test1_cost_q1.png`

---

### Test 3.2: Live API Call
**Question:** `What is PaymentGW's current p99 latency?`

**Expected:**
- Answer: "~185ms" (varies slightly)
- Tool badge: 📡 Service Metrics API

**Check:**
- [ ] Answer has latency number
- [ ] Tool badge visible
- [ ] Badge says "Service Metrics"
- [ ] Number is reasonable (150-200ms range)

**Screenshot:** `L3_test2_live_metrics.png`

---

### Test 3.3: Database Sorting
**Question:** `Which service had the highest cost in March 2026?`

**Expected:**
- Answer: "PaymentGW at $7,500"
- Tool badge: Database Query

**Check:**
- [ ] Answer says PaymentGW
- [ ] Answer says $7,500
- [ ] Tool badge visible
- [ ] Exact numbers, not estimates

**Screenshot:** `L3_test3_highest_cost.png`

---

### Test 3.4: Multi-Tool Comparison
**Question:** `Is NotificationSvc meeting its SLA targets?`

**Expected:**
- Answer: "No" - breaching targets
- Should compare: current metrics vs SLA targets
- Tool badges: Both Database + API

**Check:**
- [ ] Answer says "No" or "breaching"
- [ ] Mentions latency: 3200ms vs 2000ms target
- [ ] Mentions error rate: 2.1% vs 1.0% target
- [ ] Multiple tool badges visible
- [ ] Comparison is clear

**Screenshot:** `L3_test4_sla_check.png`

---

## 📋 LEVEL 4: Conversational Memory (1.0 point)

**IMPORTANT:** Do NOT refresh page between questions!

### Turn 1
**Question:** `Which service had the highest cost in March 2026?`

**Expected:** "PaymentGW at $7,500"

**Check:**
- [ ] Answer correct
- [ ] Tool badge visible

---

### Turn 2
**Question:** `Why did its costs spike?`

**Expected:** Should understand "its" = PaymentGW
- Mentions INC-005
- Mentions circuit breaker incident
- Mentions March 2026

**Check:**
- [ ] Does NOT ask "which service?"
- [ ] Resolves "its" to PaymentGW
- [ ] Mentions incident
- [ ] Context maintained

---

### Turn 3
**Question:** `Which team is responsible for it?`

**Expected:** "Team Platform, led by Alex Chen"

**Check:**
- [ ] Still talking about PaymentGW
- [ ] Says Team Platform
- [ ] Mentions Alex Chen
- [ ] Context maintained

---

### Turn 4
**Question:** `What was their most recent incident?`

**Expected:** INC-005 in March 2026

**Check:**
- [ ] Resolves "their" correctly
- [ ] Mentions INC-005
- [ ] Mentions March 2026
- [ ] Full conversation context maintained

**Screenshot:** `L4_full_conversation.png` (capture all 4 turns)

---

## 📋 LEVEL 5: Structured Investigation (0.5 bonus)

### Test 5.1: Investigation
**Question:** `Investigate PaymentGW performance issues`

**Expected:**
- Tool badge: 🔍 Incident Investigation
- Structured output with sections:
  - Current metrics
  - Recent incidents
  - Cost trend
  - SLA targets

**Check:**
- [ ] Investigation tool badge visible
- [ ] Answer has structured sections
- [ ] Mentions current metrics
- [ ] Mentions incidents
- [ ] Mentions cost data
- [ ] Mentions SLA targets
- [ ] Output is organized/structured

**Screenshot:** `L5_investigation.png`

---

## 📊 UI Feature Checks

### Visual Elements
- [ ] Citations display with confidence scores
- [ ] Tool badges display with icons
- [ ] Tool badges show input preview
- [ ] "View trace" link visible
- [ ] Messages have proper styling
- [ ] User messages right-aligned (blue)
- [ ] Assistant messages left-aligned (white)
- [ ] Typing indicator shows while waiting

### Functionality
- [ ] Input box accepts text
- [ ] Send button works
- [ ] Enter key sends message
- [ ] Shift+Enter adds new line
- [ ] New Chat button resets conversation
- [ ] Session ID displayed in header
- [ ] Sidebar shows example questions
- [ ] Level selector buttons work

### Performance
- [ ] Page loads in < 3 seconds
- [ ] Responses arrive in < 30 seconds
- [ ] No console errors (F12 to check)
- [ ] Smooth scrolling
- [ ] No UI freezing

---

## 📸 Screenshot Checklist

Required screenshots for Evidence Pack:

1. [ ] `L1_citation_example.png` - Any L1 question with citation visible
2. [ ] `L2_conflict_resolution.png` - Rate limit question showing v1 vs v2
3. [ ] `L3_tool_badge.png` - Cost question with tool badge + exact number
4. [ ] `L4_conversation.png` - Full 4-turn conversation visible
5. [ ] `L5_investigation.png` - Investigation output
6. [ ] `architecture_diagram.png` - Your system architecture (draw separately)

---

## ✅ Final Scoring

| Level | Tests | Points | Status |
|-------|-------|--------|--------|
| L1 | 3/3 | 2.0 | [ ] |
| L2 | 2/2 | 3.0 | [ ] |
| L3 | 4/4 | 4.0 | [ ] |
| L4 | 4/4 | 1.0 | [ ] |
| L5 | 1/1 | 0.5 | [ ] |
| **Total** | **14/14** | **10.5** | [ ] |

---

## 🐛 Common Issues

### Citations not showing
- Check browser console (F12) for errors
- Verify RAG is working (check server logs)
- Refresh page and try again

### Tool badges not showing
- Check monitoring API is running (port 8000)
- Verify database is seeded
- Check server logs for tool execution

### L4 context lost
- Make sure you didn't refresh page
- Check session ID didn't change
- Try "New Chat" and start over

### Slow responses
- Normal for LLM calls (15-30 seconds)
- Check AWS credentials are valid
- Check network connection

---

## 🎯 Pass Criteria

**Minimum to pass:** L1-L3 working = 9.0/10 points

**Target:** All levels = 10.5/10 points

**Current system:** Should achieve 10.5/10 ✅

---

Good luck with testing! 🚀

"""
Quick manual test script - Copy/paste questions into web UI
"""

print("""
╔══════════════════════════════════════════════════════════════╗
║         GeekBrain AI - Quick Test Questions                  ║
╔══════════════════════════════════════════════════════════════╗

📋 INSTRUCTIONS:
1. Open http://localhost:3002 in browser
2. Copy each question below
3. Paste into chat and verify answer
4. Check for citations, tool calls, and correct answers

═══════════════════════════════════════════════════════════════

🟢 LEVEL 1: Simple RAG (2.0 points)
───────────────────────────────────────────────────────────────

Q1.1: Who is the Team Platform lead?
Expected: Alex Chen
Citation: team_platform.md

Q1.2: What is the deployment freeze window?
Expected: Friday 18:00 to Monday 08:00
Citation: deployment_policy.md

Q1.3: What authentication method does PaymentGW API use?
Expected: API key + HMAC-SHA256 signature
Citation: api_reference_v2.md

═══════════════════════════════════════════════════════════════

🟡 LEVEL 2: Advanced RAG (3.0 points)
───────────────────────────────────────────────────────────────

Q2.1: What is the current API rate limit for PaymentGW?
Expected: 1,000 requests per minute (v2), was 500 in v1
Citations: api_reference_v2.md, api_reference_v1_archived.md
Check: Should mention v2 is current, v1 is archived

Q2.2: Can Team Commerce deploy a fix on Friday night for a P1 bug?
Expected: Yes, with VP approval (Mark Sullivan) - P1 overrides freeze
Citations: deployment_policy.md, incident_response_policy.md, team_commerce.md
Check: Should synthesize info from multiple docs

═══════════════════════════════════════════════════════════════

🔵 LEVEL 3: Tool-Augmented RAG (4.0 points)
───────────────────────────────────────────────────────────────

Q3.1: What was PaymentGW's total infrastructure cost in Q1 2026?
Expected: $16,500 (Jan: $4,200 + Feb: $4,800 + Mar: $7,500)
Tool: Database Query (should see SQL badge)
Check: Exact number, not estimate

Q3.2: What is PaymentGW's current p99 latency?
Expected: ~185ms (varies slightly each call)
Tool: Service Metrics API
Check: Should call API, not guess from docs

Q3.3: Which service had the highest cost in March 2026?
Expected: PaymentGW at $7,500
Tool: Database Query
Check: Should query DB, not retrieve from docs

Q3.4: Is NotificationSvc meeting its SLA targets?
Expected: No - latency 3200ms vs target 2000ms, error 2.1% vs 1.0%
Tools: Database Query + Service Metrics API (both)
Check: Should compare current metrics vs targets

═══════════════════════════════════════════════════════════════

🟣 LEVEL 4: Conversational Memory (1.0 point)
───────────────────────────────────────────────────────────────

IMPORTANT: Ask these in sequence WITHOUT refreshing page

Q4.1: Which service had the highest cost in March 2026?
Expected: PaymentGW at $7,500

Q4.2: Why did its costs spike?
Expected: Should understand "its" = PaymentGW
         Mention INC-005, circuit breaker incident in March
Check: Does NOT ask "which service?" - resolves pronoun

Q4.3: Which team is responsible for it?
Expected: Team Platform, led by Alex Chen
Check: Still talking about PaymentGW

Q4.4: What was their most recent incident?
Expected: INC-005 in March 2026
Check: Resolves "their" = Team Platform/PaymentGW

═══════════════════════════════════════════════════════════════

⭐ LEVEL 5: Structured Investigation (0.5 bonus)
───────────────────────────────────────────────────────────────

Q5.1: Investigate PaymentGW performance issues
Expected: Structured output with:
  - Current metrics
  - Recent incidents
  - Cost trend
  - SLA targets
Tool: Incident Investigation
Check: Should return JSON-like structured data

═══════════════════════════════════════════════════════════════

✅ SCORING CHECKLIST:
───────────────────────────────────────────────────────────────

[ ] L1: All 3 questions answered correctly with citations
[ ] L2: Both questions synthesize multiple docs correctly
[ ] L3: All 4 questions use tools and return exact numbers
[ ] L4: All 4 turns maintain context (pronouns resolved)
[ ] L5: Investigation returns structured output

Target: L1-L3 working = 9.0/10 points (90%)
Bonus: L4 + L5 = 10.5/10 points (105%)

═══════════════════════════════════════════════════════════════

📸 EVIDENCE PACK SCREENSHOTS NEEDED:
───────────────────────────────────────────────────────────────

1. L1: One question with citation visible
2. L2: Rate limit question showing conflict resolution
3. L3: Cost question showing tool call badge + exact number
4. L4: Full 4-turn conversation screenshot
5. L5: Investigation output

═══════════════════════════════════════════════════════════════
""")

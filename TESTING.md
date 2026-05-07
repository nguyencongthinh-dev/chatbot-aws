# GeekBrain AI - Testing Guide

## Quick Start

### 1. Start Services

**Terminal 1 - Web App:**
```bash
cd data_package/scripts
uv run uvicorn web_app:app --port 3002
```

**Terminal 2 - Monitoring API:**
```bash
cd data_package/scripts
uv run uvicorn monitoring_api:app --port 8000
```

### 2. Run Tests

**Option A: Automated Tests (Recommended)**
```bash
# Windows
run_tests.bat

# Linux/Mac
chmod +x run_tests.sh
./run_tests.sh
```

**Option B: Manual Testing**
```bash
cd data_package/scripts
python test_quick.py
```
Then copy/paste questions into http://localhost:3002

**Option C: Interactive Python**
```bash
cd data_package/scripts
uv run python test_all_levels.py
```

---

## Test Coverage

| Level | Points | Tests | What's Tested |
|-------|--------|-------|---------------|
| **L1** | 2.0 | 3 questions | Simple RAG retrieval + citations |
| **L2** | 3.0 | 2 questions | Multi-doc synthesis + conflict resolution |
| **L3** | 4.0 | 4 questions | Database queries + API calls + tool use |
| **L4** | 1.0 | 4-turn conversation | Conversational memory + pronoun resolution |
| **L5** | 0.5 | 1 investigation | Structured output + multi-tool orchestration |
| **Total** | **10.5** | **14 tests** | |

---

## Expected Results

### L1: Simple RAG (2.0 points)

✅ **Q: Who is the Team Platform lead?**
- Answer: Alex Chen
- Citation: `team_platform.md (0.95)`

✅ **Q: What is the deployment freeze window?**
- Answer: Friday 18:00 to Monday 08:00
- Citation: `deployment_policy.md (0.95)`

✅ **Q: What authentication method does PaymentGW API use?**
- Answer: API key + HMAC-SHA256 signature
- Citation: `api_reference_v2.md (0.95)`

### L2: Advanced RAG (3.0 points)

✅ **Q: What is the current API rate limit for PaymentGW?**
- Answer: 1,000 requests per minute (v2), was 500 in v1
- Citations: `api_reference_v2.md (0.95)`, `api_reference_v1_archived.md (0.87)`
- Must mention v2 is current

✅ **Q: Can Team Commerce deploy on Friday night for P1?**
- Answer: Yes, with VP Mark Sullivan approval - P1 overrides freeze
- Citations: Multiple docs (deployment_policy, incident_response, team_commerce)

### L3: Tool-Augmented RAG (4.0 points)

✅ **Q: PaymentGW total cost Q1 2026?**
- Answer: **$16,500** (exact)
- Tool: 🗄️ Database Query
- SQL: `SELECT SUM(total_cost) FROM monthly_costs WHERE service='PaymentGW' AND month IN ('2026-01','2026-02','2026-03')`

✅ **Q: PaymentGW current p99 latency?**
- Answer: ~185ms (varies)
- Tool: 📡 Service Metrics API

✅ **Q: Highest cost service March 2026?**
- Answer: PaymentGW at $7,500
- Tool: 🗄️ Database Query

✅ **Q: Is NotificationSvc meeting SLA?**
- Answer: No - latency 3200ms vs 2000ms target, error 2.1% vs 1.0%
- Tools: Both Database + API

### L4: Conversational Memory (1.0 point)

✅ **4-turn conversation:**
```
Turn 1: Which service had highest cost March 2026?
→ PaymentGW at $7,500

Turn 2: Why did its costs spike?
→ [Resolves "its" = PaymentGW] INC-005 circuit breaker incident

Turn 3: Which team is responsible for it?
→ [Still PaymentGW context] Team Platform, Alex Chen

Turn 4: What was their most recent incident?
→ [Resolves "their"] INC-005 in March 2026
```

### L5: Structured Investigation (0.5 bonus)

✅ **Q: Investigate PaymentGW performance**
- Tool: 🔍 Incident Investigation
- Output: JSON with current_metrics, recent_incidents, cost_trend, sla_targets

---

## Troubleshooting

### Tests Fail: "Server not running"
```bash
# Start web app
cd data_package/scripts
uv run uvicorn web_app:app --port 3002
```

### L3 Tests Fail: "Cannot connect to API"
```bash
# Start monitoring API
cd data_package/scripts
uv run uvicorn monitoring_api:app --port 8000
```

### L3 Tests Fail: "no such table"
```bash
# Seed database
cd data_package/scripts
uv run python seed_data.py --db-type sqlite --sqlite-path geekbrain.db
```

### L4 Tests Fail: Pronouns not resolved
- Check query rewriting is enabled in `web_app.py`
- Verify conversation history is being maintained
- Try creating new session (refresh page)

### Citations Not Showing
- Check RAG is returning results: look for `[RAG AWS]` or `[RAG LOCAL]` in logs
- Verify knowledge base files exist in `data_package/knowledge_base/`
- Check citations parsing regex in `web_app.py`

---

## Evidence Pack Checklist

For presentation, capture these screenshots:

- [ ] **L1:** Question with citation visible
- [ ] **L2:** Rate limit conflict resolution
- [ ] **L3:** Tool call badge + exact number ($16,500)
- [ ] **L4:** Full 4-turn conversation
- [ ] **L5:** Investigation structured output
- [ ] **Architecture diagram:** Your system design
- [ ] **Tool call logs:** Console showing SQL/API calls

---

## Scoring

| Grade | Score | Status |
|-------|-------|--------|
| **A+** | 10.0-10.5 | All levels pass |
| **A** | 9.0-9.9 | L1-L3 + partial L4 |
| **B** | 7.0-8.9 | L1-L3 working |
| **C** | 5.0-6.9 | L1-L2 working |
| **F** | <5.0 | L1 incomplete |

**Target:** L1-L3 = 9.0/10 (90%) = **Pass**

---

## Next Steps

1. ✅ Run automated tests
2. ✅ Fix any failing tests
3. ✅ Capture screenshots
4. ✅ Write Evidence Pack
5. ✅ Prepare 5-minute demo
6. ✅ Practice presentation

Good luck! 🚀

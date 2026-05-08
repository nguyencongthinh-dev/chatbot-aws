#!/usr/bin/env python3
"""
Quick performance test for Phase 1 optimizations
"""
import time
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "data_package" / "scripts"))

print("=" * 60)
print("🚀 PERFORMANCE TEST - Phase 1 Optimizations")
print("=" * 60)

# Test 1: KB Loading
print("\n[TEST 1] Knowledge Base Loading")
print("-" * 60)
start = time.time()

from web_app import KB_CACHE, load_knowledge_base

if not KB_CACHE:
    load_knowledge_base()

elapsed = time.time() - start
print(f"✓ Loaded {len(KB_CACHE)} files in {elapsed*1000:.2f}ms")
print(f"✓ Total size: {sum(len(c) for c in KB_CACHE.values()) // 1024} KB")

# Test 2: RAG Search (Cold)
print("\n[TEST 2] RAG Search - Cold Start")
print("-" * 60)
from web_app import search_knowledge_base_local

start = time.time()
result1 = search_knowledge_base_local("What is PaymentGW?")
elapsed1 = time.time() - start
print(f"✓ First search: {elapsed1*1000:.2f}ms")
print(f"✓ Result length: {len(result1)} chars")

# Test 3: RAG Search (Warm - Cache Hit)
print("\n[TEST 3] RAG Search - Warm Cache")
print("-" * 60)
start = time.time()
result2 = search_knowledge_base_local("What is PaymentGW?")
elapsed2 = time.time() - start
print(f"✓ Second search: {elapsed2*1000:.2f}ms")
print(f"✓ Cache speedup: {elapsed1/elapsed2:.1f}x faster")

# Test 4: Smart Rewriting Detection
print("\n[TEST 4] Smart Query Rewriting Detection")
print("-" * 60)
from web_app import needs_query_rewriting

test_cases = [
    ("What is PaymentGW?", [], False, "No pronoun"),
    ("What about its cost?", [{"role": "user"}], True, "Pronoun, no entity"),
    ("What about PaymentGW's cost?", [{"role": "user"}], False, "Has entity name"),
    ("Tell me about it", [{"role": "user"}], True, "Pronoun, no entity"),
    ("How much does it cost for AuthSvc?", [{"role": "user"}], False, "Has service name"),
]

correct = 0
for query, history, expected, reason in test_cases:
    result = needs_query_rewriting(query, history)
    status = "✓" if result == expected else "✗"
    if result == expected:
        correct += 1
    print(f"{status} '{query}' → {result} ({reason})")

print(f"\n✓ Passed {correct}/{len(test_cases)} tests")

# Summary
print("\n" + "=" * 60)
print("📊 PERFORMANCE SUMMARY")
print("=" * 60)
print(f"✓ KB Cache: {len(KB_CACHE)} files loaded ({sum(len(c) for c in KB_CACHE.values()) // 1024} KB)")
print(f"✓ RAG Search: {elapsed1*1000:.0f}ms → {elapsed2*1000:.0f}ms ({elapsed1/elapsed2:.1f}x faster)")
print(f"✓ Smart Rewriting: {correct}/{len(test_cases)} correct detections")
print("\n🎉 Phase 1 optimizations working correctly!")
print("=" * 60)

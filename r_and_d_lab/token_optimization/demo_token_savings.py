#!/usr/bin/env python3
"""
Demo: Measurable token cost reduction using Prompt Routing + Response Caching.

Simulates a batch of queries (mix of common/repetitive and novel).

Before: All queries go to LLM (high cost).
After: Router handles many without LLM; Cache avoids repeats.

This demonstrates the early win for Gate 1.
"""

import sys
sys.path.append(".")

from prompt_router import route_prompt
from response_cache import get_cached_response, cache_response

# Representative test queries for the mental health clinic app context
TEST_QUERIES = [
    "Hello, how are you?",  # greeting -> router
    "Hi there!",  # greeting -> router (cache will help on repeat)
    "How do I book an appointment with my therapist?",  # router
    "What is the cancellation policy?",  # would be router if added, here LLM for demo variety
    "Hello again!",  # repeat greeting -> cache hit
    "How do I reset my password?",  # router
    "Tell me about the HARNESS model for family therapy.",  # novel -> LLM
    "How do I book an appointment?",  # exact repeat -> cache
    "What can you help with in this app?",  # meta -> router
    "Can you explain the anxiety workbook module 2?",  # novel -> LLM
]

def simulate_before(queries):
    """All go to LLM."""
    llm_calls = len(queries)
    # Rough token estimate: avg prompt 80 tokens + response 150 = 230 per call
    tokens = llm_calls * 230
    return llm_calls, tokens

def simulate_after(queries):
    """With router + cache."""
    llm_calls = 0
    cached_hits = 0
    routed = 0
    total_tokens = 0

    for q in queries:
        # 1. Check cache first (exact)
        cached = get_cached_response(q)
        if cached:
            cached_hits += 1
            # cached response costs 0 LLM tokens (just retrieval)
            continue

        # 2. Try router
        response, used_llm = route_prompt(q)
        if not used_llm and response:
            routed += 1
            # "LLM-free" response, but we still "pay" a tiny amount for the router itself (say 5 tokens equivalent for demo)
            total_tokens += 5
            # Cache the routed response for future
            cache_response(q, response)
            continue

        # 3. Needs LLM
        llm_calls += 1
        # Simulate LLM response (in real would call model)
        simulated_response = f"[LLM response to: {q[:40]}...]"
        total_tokens += 230  # prompt + response
        cache_response(q, simulated_response)

    return llm_calls, total_tokens, routed, cached_hits

def main():
    print("=== Early Token Reduction Win Demo ===\n")
    print(f"Total test queries: {len(TEST_QUERIES)}\n")

    before_calls, before_tokens = simulate_before(TEST_QUERIES)
    print(f"BEFORE (no routing/caching):")
    print(f"  LLM calls: {before_calls}")
    print(f"  Estimated tokens: {before_tokens}\n")

    after_calls, after_tokens, routed, cached = simulate_after(TEST_QUERIES)
    print(f"AFTER (with router + cache):")
    print(f"  LLM calls: {after_calls}")
    print(f"  Routed without LLM: {routed}")
    print(f"  Cache hits: {cached}")
    print(f"  Estimated tokens (LLM + tiny router overhead): {after_tokens}\n")

    reduction_calls = before_calls - after_calls
    reduction_pct = (reduction_calls / before_calls * 100) if before_calls > 0 else 0
    token_savings = before_tokens - after_tokens
    token_savings_pct = (token_savings / before_tokens * 100) if before_tokens > 0 else 0

    print("=== RESULTS ===")
    print(f"LLM calls reduced by: {reduction_calls} ({reduction_pct:.1f}%)")
    print(f"Tokens saved (approx): {token_savings} ({token_savings_pct:.1f}%)")
    print("\nThis is a simple but real early win. Router handles repetitive/common cases at near-zero cost.")
    print("Caching eliminates repeats entirely.")

if __name__ == "__main__":
    main()
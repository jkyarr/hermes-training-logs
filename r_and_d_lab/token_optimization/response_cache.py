#!/usr/bin/env python3
"""
Basic Response Caching for token savings.

Supports exact match caching (by normalized prompt hash).

Can be extended to semantic caching using embeddings later (e.g. with bge or sentence-transformers).

Simple in-memory + optional file persistence for demo.
"""

import hashlib
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

CACHE_FILE = os.path.join(os.path.dirname(__file__), "response_cache.json")

# In-memory cache: key -> {"response": str, "timestamp": str, "prompt": str}
_cache: Dict[str, Dict[str, Any]] = {}

def _load_cache():
    global _cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _cache = json.load(f)
        except Exception:
            _cache = {}

def _save_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_cache, f, indent=2, ensure_ascii=False)
    except Exception:
        pass  # fail silently for demo

def _get_key(prompt: str) -> str:
    """Normalize and hash the prompt for exact match."""
    normalized = " ".join(prompt.lower().strip().split())
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()

def get_cached_response(prompt: str, max_age_hours: int = 24*7) -> Optional[str]:
    """
    Return cached response if exact match exists and not too old.
    """
    _load_cache()
    key = _get_key(prompt)
    entry = _cache.get(key)
    if not entry:
        return None

    try:
        ts = datetime.fromisoformat(entry.get("timestamp", ""))
        if datetime.now() - ts > timedelta(hours=max_age_hours):
            # expired
            del _cache[key]
            _save_cache()
            return None
    except Exception:
        return None

    return entry.get("response")

def cache_response(prompt: str, response: str):
    """
    Store the response for future exact matches.
    """
    _load_cache()
    key = _get_key(prompt)
    _cache[key] = {
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt[:200]  # store snippet for debugging
    }
    _save_cache()

def clear_cache():
    global _cache
    _cache = {}
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)

if __name__ == "__main__":
    # Demo
    p1 = "How do I book an appointment?"
    print("First call (cache miss):", get_cached_response(p1))
    cache_response(p1, "To book an appointment, use the Schedule tab in the app.")
    print("Second call (cache hit):", get_cached_response(p1))
    print("Cache file:", CACHE_FILE)
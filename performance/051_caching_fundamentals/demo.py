"""
Demo: Caching Fundamentals
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import time
from typing import Any, Optional


# ── Section 1: A simple TTL cache ─────────────────────────────────────────────

class TTLCache:
    """
    A minimal in-memory cache with TTL (Time-To-Live) support.
    This is the mental model behind Redis, Memcached, and lru_cache.
    """
    def __init__(self, max_size: int = 100):
        self._store: dict[str, tuple[Any, Optional[float]]] = {}
        self._max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Return cached value, or None on miss/expiry."""
        entry = self._store.get(key)
        if entry is None:
            self.misses += 1
            return None
        value, expires_at = entry
        if expires_at is not None and time.monotonic() > expires_at:
            del self._store[key]   # expired — evict
            self.misses += 1
            return None
        self.hits += 1
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value. ttl=None means it never expires."""
        if len(self._store) >= self._max_size:
            # Eviction: remove oldest entry (FIFO — simple but not ideal)
            oldest_key = next(iter(self._store))
            del self._store[oldest_key]
        expires_at = time.monotonic() + ttl if ttl is not None else None
        self._store[key] = (value, expires_at)

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def size(self) -> int:
        return len(self._store)

    def stats(self) -> dict:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{self.hit_rate:.1%}",
            "size": self.size,
        }


# ── Section 2: Simulated expensive operation ──────────────────────────────────

DB_QUERY_COUNT = 0

def get_user_from_db(user_id: int) -> dict:
    """Simulates a slow database query (10ms)."""
    global DB_QUERY_COUNT
    DB_QUERY_COUNT += 1
    time.sleep(0.01)   # 10ms DB query
    return {"id": user_id, "name": f"User_{user_id}", "email": f"user{user_id}@x.com"}


# ── Section 3: Cache-aware lookup (cache-aside pattern preview) ───────────────

cache = TTLCache(max_size=50)

def get_user(user_id: int) -> dict:
    """Try cache first; fall back to DB on miss."""
    key = f"user:{user_id}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    # Cache miss — go to DB
    user = get_user_from_db(user_id)
    cache.set(key, user, ttl=30)   # cache for 30 seconds
    return user


# ── Section 4: TTL expiry demonstration ──────────────────────────────────────

def demonstrate_ttl():
    """Shows how values expire after TTL."""
    short_cache = TTLCache()
    short_cache.set("temp_value", "I expire quickly", ttl=1)

    print("  Right after set:")
    print(f"    get('temp_value') = {short_cache.get('temp_value')!r}")

    time.sleep(1.1)   # wait for TTL to expire

    print("  After 1.1 seconds (TTL=1s):")
    print(f"    get('temp_value') = {short_cache.get('temp_value')!r}  ← expired, returns None")


# ── Section 5: Cache eviction (max_size) ─────────────────────────────────────

def demonstrate_eviction():
    """Shows what happens when the cache is full."""
    tiny_cache = TTLCache(max_size=3)
    for i in range(1, 5):
        tiny_cache.set(f"key_{i}", f"value_{i}")
        print(f"  Set key_{i}. Size: {tiny_cache.size}. "
              f"key_1 still there: {tiny_cache.get('key_1') is not None}")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Caching Fundamentals")
    print("=" * 55)

    print("\n--- Without cache: every request hits the DB ---")
    t0 = time.monotonic()
    for uid in [1, 2, 1, 3, 1, 2]:
        get_user_from_db(uid)
    no_cache_time = time.monotonic() - t0
    print(f"  6 requests, 6 DB queries, took {no_cache_time*1000:.0f}ms")
    DB_QUERY_COUNT = 0

    print("\n--- With cache: DB only hit on first request per user ---")
    t0 = time.monotonic()
    for uid in [1, 2, 1, 3, 1, 2]:
        get_user(uid)
    cache_time = time.monotonic() - t0
    print(f"  6 requests, {DB_QUERY_COUNT} DB queries, took {cache_time*1000:.0f}ms")
    print(f"  Cache stats: {cache.stats()}")
    print(f"  Speedup: {no_cache_time/cache_time:.1f}x faster")

    print("\n--- Cache concepts ---")
    print(f"  Hit:  returned from cache (fast)")
    print(f"  Miss: not in cache, went to DB (slow, then cached)")
    print(f"  TTL:  time before cached value expires")
    print(f"  Hit rate: hits/(hits+misses) = {cache.hit_rate:.1%}")

    print("\n--- TTL expiry ---")
    demonstrate_ttl()

    print("\n--- Eviction when cache is full (max_size=3) ---")
    demonstrate_eviction()

    print("\n--- When to cache: decision guide ---")
    scenarios = [
        ("User profile data (changes rarely)",        "YES — TTL 60s"),
        ("Product catalog (100s of requests/sec)",    "YES — TTL 5m"),
        ("Bank account balance",                       "NO  — must be real-time"),
        ("Weather data",                               "YES — TTL 10m"),
        ("User's shopping cart",                      "NO  — per-user, changes often"),
        ("Total user count on homepage",              "YES — TTL 1m"),
        ("Auth token validation",                     "MAYBE — short TTL, revocation tricky"),
    ]
    print()
    for scenario, recommendation in scenarios:
        print(f"  {scenario:50s} → {recommendation}")

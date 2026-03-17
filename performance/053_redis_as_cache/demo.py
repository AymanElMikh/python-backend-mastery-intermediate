"""
Demo: Redis as a Cache
Level: Intermediate (2–3 years experience)
Run:  python demo.py

This demo simulates Redis behaviour without requiring a Redis server.
The real code is shown in comments — identical except for the client calls.

To run with a real Redis:
  pip install redis
  docker run -d -p 6379:6379 redis:alpine
  Then replace FakeRedis with: import redis; r = redis.Redis(decode_responses=True)
"""

import json
import time
from typing import Optional


# ── Fake Redis client (identical API to redis-py) ────────────────────────────

class FakeRedis:
    """
    Simulates redis.Redis with GET, SET, DELETE, EXISTS, TTL.
    Real redis-py has the exact same method names.
    """
    def __init__(self):
        self._store: dict[str, tuple[str, Optional[float]]] = {}
        self.get_calls = 0
        self.set_calls = 0

    def get(self, key: str) -> Optional[str]:
        """GET key → value or None."""
        self.get_calls += 1
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at is not None and time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """SET key value [EX seconds]"""
        self.set_calls += 1
        expires_at = time.monotonic() + ex if ex is not None else None
        self._store[key] = (value, expires_at)
        return True

    def delete(self, *keys: str) -> int:
        """DEL key [key ...] → number of keys deleted"""
        deleted = sum(1 for k in keys if self._store.pop(k, None) is not None)
        return deleted

    def exists(self, *keys: str) -> int:
        """EXISTS key → 1 if exists, 0 if not"""
        return sum(1 for k in keys if self.get(k) is not None)

    def ttl(self, key: str) -> int:
        """TTL key → seconds remaining, -1 if no TTL, -2 if not exists"""
        entry = self._store.get(key)
        if entry is None:
            return -2
        _, expires_at = entry
        if expires_at is None:
            return -1  # no TTL
        remaining = expires_at - time.monotonic()
        return max(0, int(remaining))

    def keys(self, pattern: str = "*") -> list[str]:
        """Return all keys (simplified — no real pattern matching)."""
        return list(self._store.keys())


# ── Use it just like the real redis-py ───────────────────────────────────────
r = FakeRedis()
# Real code: r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


# ── Section 1: Basic GET / SET with TTL ───────────────────────────────────────

DB_QUERY_COUNT = 0

def fetch_from_db(user_id: int) -> dict:
    """Simulates a slow DB query."""
    global DB_QUERY_COUNT
    DB_QUERY_COUNT += 1
    time.sleep(0.02)
    return {"id": user_id, "name": f"User_{user_id}", "email": f"u{user_id}@x.com", "role": "user"}


def get_user(user_id: int) -> dict:
    """
    Cache-aside pattern with Redis.
    Real code: same, just `r = redis.Redis(...)`.
    """
    key = f"user:{user_id}"

    # 1. Try Redis cache
    cached = r.get(key)
    if cached is not None:
        return json.loads(cached)   # deserialize from JSON string

    # 2. Cache miss — hit the database
    user = fetch_from_db(user_id)

    # 3. Store in Redis with TTL (5 minutes in real life, 2 seconds for demo)
    r.set(key, json.dumps(user), ex=60)

    return user


def invalidate_user_cache(user_id: int) -> None:
    """Call this whenever user data changes (update, delete)."""
    deleted = r.delete(f"user:{user_id}")
    print(f"  [Cache] Invalidated user:{user_id} → deleted={deleted}")


# ── Section 2: Storing different data types ──────────────────────────────────

def cache_product_list(category: str, products: list, ttl: int = 300) -> None:
    """Cache a list of products as JSON."""
    key = f"products:{category}"
    r.set(key, json.dumps(products), ex=ttl)


def get_product_list(category: str) -> Optional[list]:
    raw = r.get(f"products:{category}")
    return json.loads(raw) if raw else None


# ── Section 3: The "store Python dict directly" mistake ──────────────────────

def wrong_way_to_cache():
    """Shows what happens when you don't serialize to JSON."""
    data = {"id": 1, "name": "Alice"}
    try:
        r.set("user:1", data)  # Can't store a dict directly in real Redis
    except TypeError as e:
        print(f"  TypeError: {e}")
    print("  Fix: r.set('user:1', json.dumps(data), ex=60)")


# ── Section 4: Key naming conventions ────────────────────────────────────────

KEY_EXAMPLES = """
Redis key naming conventions:
  user:{id}                → user:42
  user:{id}:profile        → user:42:profile
  product:{id}             → product:101
  products:category:{slug} → products:category:electronics
  session:{token}          → session:abc123
  rate_limit:{ip}          → rate_limit:192.168.1.1

  Rules:
  - Use colons as separators (readable, and Redis sorts them well)
  - Include the entity type prefix (user:, product:, session:)
  - Keep keys short but descriptive
  - Never store user IDs in key values that are also user IDs (confusing)
"""


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Redis as a Cache")
    print("=" * 55)

    print("\n--- Basic cache-aside pattern ---")
    users_to_fetch = [1, 2, 1, 3, 1, 2, 3, 1]
    t0 = time.monotonic()
    results = []
    for uid in users_to_fetch:
        user = get_user(uid)
        hit = "HIT " if r.exists(f"user:{uid}") else "MISS"
        results.append(f"  user:{uid} {hit} → {user['name']}")

    for line in results:
        print(line)

    elapsed = time.monotonic() - t0
    print(f"\n  {len(users_to_fetch)} fetches, {DB_QUERY_COUNT} DB queries")
    print(f"  Time: {elapsed*1000:.0f}ms | Redis GETs: {r.get_calls} | SETs: {r.set_calls}")

    print("\n--- TTL inspection ---")
    for uid in [1, 2, 3]:
        ttl = r.ttl(f"user:{uid}")
        print(f"  user:{uid} TTL: {ttl}s remaining")

    print("\n--- Cache invalidation on update ---")
    print(f"  Keys before: {r.keys()}")
    invalidate_user_cache(2)
    print(f"  user:2 in cache: {r.exists('user:2')}")
    print("  Next fetch of user:2 will hit DB:")
    DB_QUERY_COUNT = 0
    get_user(2)
    print(f"  DB queries: {DB_QUERY_COUNT}")

    print("\n--- Caching a list (products) ---")
    products = [{"id": 1, "name": "Laptop"}, {"id": 2, "name": "Mouse"}]
    cache_product_list("electronics", products, ttl=30)
    cached = get_product_list("electronics")
    print(f"  Cached and retrieved: {cached}")
    print(f"  Not cached: {get_product_list('clothing')}")

    print("\n--- Common mistake: not serializing to JSON ---")
    wrong_way_to_cache()

    print(KEY_EXAMPLES)

    print("--- Real redis-py code (same API) ---")
    print("""
  import redis
  import json

  r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

  # SET with TTL
  r.set("user:42", json.dumps({"id": 42, "name": "Alice"}), ex=300)

  # GET
  raw = r.get("user:42")
  user = json.loads(raw) if raw else None

  # DELETE
  r.delete("user:42")
""")

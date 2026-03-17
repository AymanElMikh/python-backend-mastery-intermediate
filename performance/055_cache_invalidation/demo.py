"""
Demo: Cache Invalidation Strategies
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import json
import time
from typing import Optional


# ── Shared infrastructure ─────────────────────────────────────────────────────

class FakeRedis:
    def __init__(self):
        self._store: dict = {}

    def get(self, key):
        entry = self._store.get(key)
        if not entry:
            return None
        value, exp = entry
        if exp and time.monotonic() > exp:
            del self._store[key]
            return None
        return value

    def set(self, key, value, ex=None):
        self._store[key] = (value, time.monotonic() + ex if ex else None)

    def delete(self, *keys):
        for k in keys:
            self._store.pop(k, None)

    def scan_keys(self, prefix: str) -> list[str]:
        """Simulates Redis SCAN with MATCH prefix* — safe for production."""
        return [k for k in self._store if k.startswith(prefix)]

    def exists(self, key) -> bool:
        return self.get(key) is not None


cache = FakeRedis()
DB_WRITES = 0

def db_update(table: str, id_: int, data: dict) -> dict:
    global DB_WRITES
    DB_WRITES += 1
    print(f"    [DB] UPDATE {table} id={id_} {data}")
    return {"id": id_, **data}


# ── Strategy 1: TTL-based invalidation ───────────────────────────────────────

def get_product_ttl(product_id: int) -> dict:
    """
    Simple TTL strategy: cache for 5 minutes.
    Staleness window = TTL. Acceptable for product catalog.
    """
    key = f"product:{product_id}"
    raw = cache.get(key)
    if raw:
        return json.loads(raw)
    product = {"id": product_id, "name": f"Product {product_id}", "price": 99.99}
    cache.set(key, json.dumps(product), ex=300)   # 5 minute TTL
    return product


def update_product_ttl_only(product_id: int, price: float) -> dict:
    """
    BAD for price data: cache is NOT invalidated.
    User will see old price for up to 5 minutes.
    Acceptable for non-critical data, NOT for prices.
    """
    product = db_update("products", product_id, {"price": price})
    # No cache invalidation — stale data for up to TTL
    print(f"    [Cache] NO invalidation — stale data for up to 5min")
    return product


# ── Strategy 2: Explicit invalidation on write ────────────────────────────────

def get_user(user_id: int) -> dict:
    key = f"user:{user_id}"
    raw = cache.get(key)
    if raw:
        return json.loads(raw)
    user = {"id": user_id, "email": f"u{user_id}@x.com", "name": f"User {user_id}"}
    cache.set(key, json.dumps(user), ex=60)
    return user


def update_user_explicit(user_id: int, email: str) -> dict:
    """
    Explicit invalidation: delete cache key immediately on write.
    Zero staleness — next read re-fetches fresh data.
    """
    user = db_update("users", user_id, {"email": email})

    # Explicit delete — not update, delete
    cache.delete(f"user:{user_id}")
    print(f"    [Cache] DEL user:{user_id} (explicit invalidation)")

    return user


# ── Strategy 3: Pattern invalidation ─────────────────────────────────────────

def cache_products_in_category(category: str, products: list) -> None:
    for product in products:
        key = f"products:{category}:{product['id']}"
        cache.set(key, json.dumps(product), ex=300)
        print(f"    [Cache] SET {key}")


def invalidate_category(category: str) -> int:
    """
    Pattern invalidation: delete all keys for a category.
    Use SCAN (not KEYS) in production — KEYS blocks Redis.
    """
    keys = cache.scan_keys(f"products:{category}:")
    if keys:
        cache.delete(*keys)
        print(f"    [Cache] DEL {len(keys)} keys matching 'products:{category}:*'")
    return len(keys)


# ── Strategy 4: Event-driven invalidation (Observer pattern) ─────────────────

class CacheInvalidationBus:
    """
    Listens to data change events and invalidates the right cache keys.
    In production: use Redis pub/sub or a message queue.
    """
    def on_user_updated(self, user_id: int) -> None:
        cache.delete(f"user:{user_id}")
        print(f"    [EventBus] Invalidated user:{user_id}")

    def on_product_updated(self, product_id: int, category: str) -> None:
        cache.delete(f"product:{product_id}")
        # Also invalidate category listing
        cache.delete(f"products:{category}:list")
        print(f"    [EventBus] Invalidated product:{product_id} and category:{category} list")


invalidation_bus = CacheInvalidationBus()


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Cache Invalidation Strategies")
    print("=" * 55)

    print("\n--- Strategy 1: TTL-only (staleness until expiry) ---")
    p = get_product_ttl(10)
    print(f"  Cached product: {p}")
    print(f"  Updating price to $199...")
    update_product_ttl_only(10, 199.00)
    p = get_product_ttl(10)
    print(f"  Cache still shows OLD price: ${p['price']}  ← stale!")
    print("  (Will be fresh after TTL expires — 5 min in real usage)")

    print("\n--- Strategy 2: Explicit invalidation (zero staleness) ---")
    u = get_user(1)
    print(f"  Cached user: {u}")
    print(f"  Cache has user:1: {cache.exists('user:1')}")
    update_user_explicit(1, "alice.new@x.com")
    print(f"  Cache has user:1 after update: {cache.exists('user:1')}")
    u = get_user(1)
    print(f"  Fresh fetch (would be from DB): {u}")

    print("\n--- Strategy 3: Pattern invalidation ---")
    electronics = [
        {"id": 1, "name": "Laptop", "price": 999},
        {"id": 2, "name": "Mouse",  "price": 29},
        {"id": 3, "name": "Monitor","price": 399},
    ]
    cache_products_in_category("electronics", electronics)
    print(f"  Keys in cache: {cache.scan_keys('products:electronics:')}")
    count = invalidate_category("electronics")
    print(f"  Keys remaining: {cache.scan_keys('products:electronics:')}")

    print("\n--- Strategy 4: Event-driven invalidation ---")
    get_user(2)   # populate cache
    print(f"  user:2 in cache: {cache.exists('user:2')}")
    # Simulate an event fired when user is updated
    invalidation_bus.on_user_updated(2)
    print(f"  user:2 in cache after event: {cache.exists('user:2')}")

    print("\n--- TTL length guidelines ---")
    guidelines = [
        ("Static content (FAQs)",        "1 hour – 24 hours"),
        ("Product catalog",               "5–15 minutes"),
        ("User profile (read by others)", "1–5 minutes"),
        ("User's own account data",       "30–60 seconds"),
        ("Permission/role data",          "1–5 minutes"),
        ("Account balance",               "NEVER CACHE"),
    ]
    for data_type, ttl in guidelines:
        print(f"  {data_type:40s} TTL: {ttl}")

    print("\n--- Common mistake: KEYS * in production ---")
    print("  BAD:  r.keys('products:*')     ← blocks Redis while scanning ALL keys")
    print("  GOOD: r.scan_iter('products:*') ← iterates in batches, non-blocking")

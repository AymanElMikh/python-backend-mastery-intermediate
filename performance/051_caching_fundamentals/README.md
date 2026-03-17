# Caching Fundamentals

## 🎯 Interview Question
What is caching and what problems does it solve in a backend system? What are the main caching concepts you need to know?

## 💡 Short Answer (30 seconds)
Caching stores the result of an expensive operation so future requests can get the answer without repeating that work. A cache hit means the answer is already there — fast. A cache miss means the data isn't cached and you must compute it — slow. The main tradeoffs are freshness (is the cache stale?) versus speed (how expensive is a cache miss?). Key concepts: TTL, eviction policy, hit rate, and cache stampede.

## 🔬 Explanation
The most common expensive operations to cache:
- **Database queries** — "get all products in category X" — same result for many users
- **Computed values** — user reputation score, recommendation list
- **External API calls** — weather data, exchange rates
- **Rendered HTML or serialized JSON** — for heavy response payloads

**Cache hit rate** = hits / (hits + misses). A 90%+ hit rate on a slow operation can cut your database load by 10×.

**TTL (Time-To-Live)** — how long a cached value is considered fresh. After TTL expires, the next request gets a cache miss and refreshes the value.

**Eviction policies** — what happens when the cache is full:
- **LRU** (Least Recently Used) — evict the item not accessed for the longest time
- **LFU** (Least Frequently Used) — evict the item accessed least often
- **FIFO** — evict the oldest item

**Cache stampede** — when TTL expires, many simultaneous requests all get a miss and all hit the database at once, overwhelming it. Fix: probabilistic early expiration, locks, or background refresh.

## 💻 Code Example
```python
import time

class SimpleCache:
    def __init__(self, max_size: int = 100):
        self._store = {}     # key → (value, expires_at)
        self._max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, key: str):
        entry = self._store.get(key)
        if entry is None:
            self.misses += 1
            return None
        value, expires_at = entry
        if expires_at and time.time() > expires_at:
            del self._store[key]
            self.misses += 1
            return None
        self.hits += 1
        return value

    def set(self, key: str, value, ttl_seconds: int = None):
        if len(self._store) >= self._max_size:
            # Simple eviction: remove the first item (FIFO)
            oldest = next(iter(self._store))
            del self._store[oldest]
        expires_at = time.time() + ttl_seconds if ttl_seconds else None
        self._store[key] = (value, expires_at)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
```

## ⚠️ Common Mistakes
1. **Caching everything.** Only cache data that is expensive to compute AND accessed frequently. Caching infrequently-accessed data wastes memory and adds complexity.
2. **No TTL on mutable data.** User profile data without a TTL will show stale data forever. Always set a TTL unless the data genuinely never changes.
3. **Not handling cache misses in the request path.** On a cache miss, your app must still work correctly — it just falls back to the slow path. Never let a cache miss cause an error.

## ✅ When to Cache vs When NOT to Cache
**Cache when:**
- The result is expensive (DB query, external API call, heavy computation)
- The result is the same for many users or requests
- A few seconds of staleness is acceptable

**Don't cache when:**
- The data must always be current (account balances, inventory levels in a transactional system)
- The data is different for every request (personalized per user + per second)
- The computation is already fast (< 1ms)

## 🔗 Related Concepts
- [performance/052_lru_cache_memoization](../052_lru_cache_memoization) — Python's built-in function cache
- [performance/053_redis_as_cache](../053_redis_as_cache) — distributed cache with Redis
- [performance/055_cache_invalidation](../055_cache_invalidation) — how to keep caches fresh

## 🚀 Next Step
In `python-backend-mastery`: **Cache stampede prevention** — probabilistic early recomputation (XFetch algorithm), distributed locks with Redis `SETNX`, and write-through vs read-through cache patterns.

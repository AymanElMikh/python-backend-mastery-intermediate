# Redis as a Cache

## 🎯 Interview Question
How do you use Redis as a cache in a Python backend, and what makes it better than an in-memory dict for caching?

## 💡 Short Answer (30 seconds)
Redis is an in-memory data store that acts as a shared, external cache. Unlike a Python dict or `lru_cache`, Redis lives outside your application process — multiple API server instances can all read from and write to the same cache. You interact with it via `redis-py`. The key operations are `SET key value EX ttl` (store with expiry) and `GET key` (retrieve). Redis also provides atomic operations, pub/sub, and data structures beyond simple strings.

## 🔬 Explanation
Why Redis over a Python dict:

| | Python dict / lru_cache | Redis |
|---|---|---|
| Shared across processes | ❌ No | ✅ Yes |
| Survives app restart | ❌ No | ✅ Yes (with persistence) |
| TTL support | Manual | Built-in (`EX` flag) |
| Atomic operations | Manual locking | Built-in (`INCR`, `SETNX`) |
| Setup | Zero | Redis server needed |
| Latency | ~ns | ~0.1–1ms |

Typical workflow (cache-aside pattern):
```
GET key from Redis
  → hit: return cached value
  → miss: query DB, SET key in Redis, return value
```

In Python: use `redis-py` (`pip install redis`). Serialize Python objects to JSON strings before storing (Redis stores bytes/strings, not Python objects).

## 💻 Code Example
```python
import redis
import json
from typing import Optional

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def get_user(user_id: int) -> dict:
    key = f"user:{user_id}"

    # Try cache first
    cached = r.get(key)
    if cached is not None:
        return json.loads(cached)  # deserialize from JSON string

    # Cache miss — query DB
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")

    # Store in Redis with 5-minute TTL
    r.set(key, json.dumps(user), ex=300)

    return user

def invalidate_user(user_id: int) -> None:
    """Call this when user data changes."""
    r.delete(f"user:{user_id}")
```

## ⚠️ Common Mistakes
1. **Storing Python objects directly.** Redis stores bytes. You must serialize: `json.dumps(data)` before storing, `json.loads(data)` after retrieving. Or use `pickle` — but JSON is safer and human-readable.
2. **Not setting a TTL.** Keys without TTL live forever. Your Redis memory grows until it runs out. Always set `ex=` (seconds) or `px=` (milliseconds) unless you have a specific reason not to.
3. **Using Redis as your primary database.** Redis is for caching and ephemeral data. If the data is important and must not be lost, it must be in a real database. Redis can be configured with persistence, but it's not a replacement for Postgres.

## ✅ When to Use Redis Cache
**Use Redis for:**
- Shared cache across multiple app workers
- Session storage
- Rate limiting counters
- Leaderboards and sorted sets
- Pub/Sub for real-time features

**Use `lru_cache` instead when:**
- Cache only needed within a single process
- Data is stable and process-local (config, permission mappings)
- You want zero infrastructure

## 🔗 Related Concepts
- [performance/051_caching_fundamentals](../051_caching_fundamentals) — caching concepts
- [performance/054_cache_aside_pattern](../054_cache_aside_pattern) — the full GET-miss-DB-SET pattern
- [performance/055_cache_invalidation](../055_cache_invalidation) — when and how to delete cache keys

## 🚀 Next Step
In `python-backend-mastery`: **Redis data structures** — using Redis `HASH`, `SORTED SET`, `LIST`, `SET` for leaderboards, rate limiting, session management, and pub/sub beyond simple key-value caching.

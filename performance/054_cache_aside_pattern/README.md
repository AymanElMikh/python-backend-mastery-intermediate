# Cache-Aside Pattern

## 🎯 Interview Question
What is the cache-aside pattern and how do you implement it in a Python backend?

## 💡 Short Answer (30 seconds)
Cache-aside (also called lazy loading) is the most common caching strategy: your application code manages the cache manually. On a read: check the cache first; if it's a miss, fetch from the database, store the result in the cache, then return it. On a write: update the database, then delete (not update) the cached value so the next read re-fetches fresh data. Your app is the one "aside" from the cache — it decides when to populate and invalidate.

## 🔬 Explanation
The three-step read pattern:
```
1. GET from cache
   → Hit:  return cached value (done)
   → Miss: continue to step 2
2. GET from database
3. SET result in cache (with TTL)
   return result
```

The two-step write pattern:
```
1. UPDATE in database
2. DELETE from cache (NOT update)
```

Why delete on write instead of update? Because updating the cache with the new value and updating the DB must both succeed to be consistent. If you update the DB but fail to update the cache, you have stale data. Deleting is safer — the next read will re-fetch and re-populate.

**Cache-aside vs other strategies:**
- **Write-through**: app writes to cache AND DB simultaneously (more complex, better consistency)
- **Write-behind**: app writes to cache only; cache syncs to DB asynchronously (risk of data loss)
- **Cache-aside**: app manages manually — most common, most flexible

## 💻 Code Example
```python
import json
import redis

r = redis.Redis(decode_responses=True)

class UserRepository:
    def get_by_id(self, user_id: int) -> dict | None:
        key = f"user:{user_id}"

        # Step 1: Check cache
        cached = r.get(key)
        if cached:
            return json.loads(cached)

        # Step 2: Cache miss — query DB
        user = self._db.query("SELECT * FROM users WHERE id = ?", user_id)
        if user is None:
            return None

        # Step 3: Populate cache
        r.set(key, json.dumps(user), ex=300)
        return user

    def update(self, user_id: int, data: dict) -> dict:
        # Step 1: Update DB (source of truth)
        user = self._db.execute("UPDATE users SET ...", user_id, data)

        # Step 2: Invalidate cache (delete, not update)
        r.delete(f"user:{user_id}")

        return user
```

## ⚠️ Common Mistakes
1. **Updating the cache value on write instead of deleting it.** Update + DB write must both succeed atomically. Deleting on write is simpler and safer — worst case is one extra DB read.
2. **Not caching "not found" results.** If `get_user(99)` returns None (user doesn't exist), caching that None prevents repeated DB queries for non-existent users. Cache it with a short TTL.
3. **Forgetting to invalidate on delete.** When a user is deleted from the DB, also delete the cache key. Otherwise clients continue getting the "deleted" user from cache until TTL expires.

## ✅ When to Use Cache-Aside
**Best for:**
- Read-heavy workloads (most APIs)
- Data that's read far more often than it's written
- When you need full control over caching behavior

**Consider write-through instead when:**
- Consistency is critical (financial data)
- Writes are as frequent as reads
- You can't tolerate even brief staleness

## 🔗 Related Concepts
- [performance/053_redis_as_cache](../053_redis_as_cache) — Redis as the cache store
- [performance/055_cache_invalidation](../055_cache_invalidation) — when and how to invalidate
- [design_patterns/026_repository_pattern](../../design_patterns/026_repository_pattern) — the repository is where cache-aside logic lives

## 🚀 Next Step
In `python-backend-mastery`: **Write-through and read-through caches** — having the cache layer itself handle DB synchronization, and using Redis as a write-through cache with Lua scripts for atomic cache+DB updates.

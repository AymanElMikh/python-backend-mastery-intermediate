"""
Demo: Cache-Aside Pattern
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import json
import time
from typing import Optional


# ── Infrastructure ────────────────────────────────────────────────────────────

class FakeRedis:
    def __init__(self):
        self._store: dict = {}
        self.get_count = 0
        self.set_count = 0
        self.delete_count = 0

    def get(self, key: str) -> Optional[str]:
        self.get_count += 1
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at and time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: str, ex: int = None):
        self.set_count += 1
        expires_at = time.monotonic() + ex if ex else None
        self._store[key] = (value, expires_at)

    def delete(self, *keys):
        self.delete_count += 1
        for k in keys:
            self._store.pop(k, None)

    def exists(self, key: str) -> bool:
        return self.get(key) is not None

    def stats(self) -> str:
        return f"GETs={self.get_count} SETs={self.set_count} DELs={self.delete_count}"


class FakeDatabase:
    def __init__(self):
        self._users = {
            1: {"id": 1, "name": "Alice", "email": "alice@x.com", "score": 100},
            2: {"id": 2, "name": "Bob",   "email": "bob@x.com",   "score": 75},
            3: {"id": 3, "name": "Carol", "email": "carol@x.com", "score": 200},
        }
        self.query_count = 0

    def find_user(self, user_id: int) -> Optional[dict]:
        self.query_count += 1
        time.sleep(0.01)  # simulate 10ms DB latency
        user = self._users.get(user_id)
        print(f"    [DB] SELECT user:{user_id} (query #{self.query_count})")
        return dict(user) if user else None

    def update_user(self, user_id: int, updates: dict) -> Optional[dict]:
        self.query_count += 1
        if user_id not in self._users:
            return None
        self._users[user_id].update(updates)
        print(f"    [DB] UPDATE user:{user_id} {updates} (query #{self.query_count})")
        return dict(self._users[user_id])

    def delete_user(self, user_id: int) -> bool:
        self.query_count += 1
        existed = self._users.pop(user_id, None) is not None
        if existed:
            print(f"    [DB] DELETE user:{user_id} (query #{self.query_count})")
        return existed


# ── Cache-Aside Repository ────────────────────────────────────────────────────

class UserRepository:
    """
    Implements cache-aside at the repository layer.
    All caching logic is isolated here — the service layer is cache-unaware.
    """
    CACHE_TTL = 60  # 60 seconds

    def __init__(self, db: FakeDatabase, cache: FakeRedis):
        self._db = db
        self._cache = cache

    def _cache_key(self, user_id: int) -> str:
        return f"user:{user_id}"

    # ── READ: Check cache → miss → DB → populate cache ──────────────────────

    def get_by_id(self, user_id: int) -> Optional[dict]:
        key = self._cache_key(user_id)

        # Step 1: Check cache
        raw = self._cache.get(key)
        if raw is not None:
            print(f"    [Cache] HIT  user:{user_id}")
            return json.loads(raw)

        print(f"    [Cache] MISS user:{user_id}")

        # Step 2: Miss → query DB
        user = self._db.find_user(user_id)

        # Step 3: Populate cache (even cache None to avoid repeat DB hits)
        if user is not None:
            self._cache.set(key, json.dumps(user), ex=self.CACHE_TTL)
        else:
            # Cache "not found" with short TTL to avoid hammering DB
            self._cache.set(key, json.dumps(None), ex=10)

        return user

    # ── WRITE: Update DB → DELETE from cache (not update) ───────────────────

    def update(self, user_id: int, updates: dict) -> Optional[dict]:
        # Step 1: Update DB (source of truth)
        user = self._db.update_user(user_id, updates)
        if user is None:
            return None

        # Step 2: DELETE cache key (not update — delete is safer)
        self._cache.delete(self._cache_key(user_id))
        print(f"    [Cache] DEL  user:{user_id} (invalidated after update)")

        return user

    def delete(self, user_id: int) -> bool:
        # Step 1: Delete from DB
        deleted = self._db.delete_user(user_id)

        # Step 2: Remove from cache
        if deleted:
            self._cache.delete(self._cache_key(user_id))
            print(f"    [Cache] DEL  user:{user_id} (invalidated after delete)")

        return deleted


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Cache-Aside Pattern")
    print("=" * 55)

    db = FakeDatabase()
    cache = FakeRedis()
    repo = UserRepository(db, cache)

    print("\n--- READ PATTERN: first access (cache miss) ---")
    user = repo.get_by_id(1)
    print(f"  Result: {user}")

    print("\n--- READ PATTERN: second access (cache hit) ---")
    user = repo.get_by_id(1)
    print(f"  Result: {user}")

    print("\n--- Multiple reads: only 3 DB queries for 9 requests ---")
    requests = [1, 2, 3, 1, 2, 3, 1, 2, 3]
    for uid in requests:
        repo.get_by_id(uid)

    print(f"\n  Stats: DB queries={db.query_count}, {cache.stats()}")

    print("\n--- WRITE PATTERN: update invalidates cache ---")
    print("  Before update — user:1 is cached:")
    print(f"  Cache has user:1: {cache.exists('user:1')}")

    updated = repo.update(1, {"name": "Alice Updated", "score": 150})
    print(f"  Updated: {updated}")
    print(f"  Cache has user:1 after update: {cache.exists('user:1')}")

    print("\n  Next read re-fetches from DB:")
    user = repo.get_by_id(1)
    print(f"  Fresh from DB: {user}")

    print("\n--- DELETE PATTERN: delete also clears cache ---")
    repo.get_by_id(2)   # populate cache
    print(f"  Cache has user:2 before delete: {cache.exists('user:2')}")
    repo.delete(2)
    print(f"  Cache has user:2 after delete: {cache.exists('user:2')}")
    result = repo.get_by_id(2)   # should go to DB and get None
    print(f"  Fetch deleted user: {result}")

    print("\n--- Common mistakes ---")
    print("  BAD:  update cache value on write")
    print("        (update DB failed? cache now has wrong data)")
    print("  GOOD: DELETE cache on write; next read re-fetches fresh data")
    print()
    print("  BAD:  don't cache 'not found' results")
    print("        (100 requests for user:9999 → 100 DB queries)")
    print("  GOOD: cache None with short TTL (10s) to protect DB")

    print("\n--- Cache-aside vs other strategies ---")
    strategies = [
        ("Cache-Aside",    "App manages cache. Simple, flexible. Miss = DB + cache populate."),
        ("Write-Through",  "Write to cache AND DB simultaneously. Better consistency."),
        ("Write-Behind",   "Write to cache only; async sync to DB. Risk of loss on crash."),
        ("Read-Through",   "Cache itself fetches from DB on miss. App only talks to cache."),
    ]
    for name, desc in strategies:
        print(f"  {name:16s} {desc}")

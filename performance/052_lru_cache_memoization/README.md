# `lru_cache` — Function-Level Memoization

## 🎯 Interview Question
What is `functools.lru_cache` and when would you use it in a backend application?

## 💡 Short Answer (30 seconds)
`@lru_cache` is a Python decorator that caches the return value of a function based on its arguments. The first call with a given set of arguments computes the result and stores it. Subsequent calls with the same arguments return the cached value instantly. "LRU" means Least Recently Used — when the cache is full, it discards the entry that was used least recently. It's ideal for pure functions with expensive computation that get called repeatedly with the same inputs.

## 🔬 Explanation
`@lru_cache` works by hashing the function's arguments to create a cache key. This means all arguments must be hashable (strings, ints, tuples — yes; lists, dicts — no).

Common backend use cases:
- **Config lookups** — `get_settings()` reads from environment; no need to re-read on every call
- **Permission checks** — "does role X have permission Y?" — stable data, called frequently
- **Heavy regex compilation** — compile once and reuse
- **Fibonacci-style recursive algorithms** — prevent exponential re-computation

`maxsize` controls how many entries to keep. `maxsize=None` disables eviction and keeps everything (use `@cache` from Python 3.9+ as the cleaner alias).

**Important limitation**: `@lru_cache` is process-local. It does NOT work across multiple server processes or workers. For distributed caching, use Redis.

## 💻 Code Example
```python
from functools import lru_cache
import time

# Cache the result of an expensive DB lookup
@lru_cache(maxsize=128)
def get_permission_set(role: str) -> frozenset[str]:
    """Roles don't change often — safe to cache."""
    time.sleep(0.1)  # simulate DB query
    permissions = {
        "admin": frozenset(["read", "write", "delete", "manage_users"]),
        "editor": frozenset(["read", "write"]),
        "viewer": frozenset(["read"]),
    }
    return permissions.get(role, frozenset())

# First call: hits DB (slow)
perms = get_permission_set("admin")  # 100ms

# Second call: from cache (instant)
perms = get_permission_set("admin")  # 0ms

# Inspect cache state
print(get_permission_set.cache_info())
# CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)

# Clear cache when data changes
get_permission_set.cache_clear()
```

## ⚠️ Common Mistakes
1. **Using on functions with unhashable arguments.** `@lru_cache` on a function that takes a `list` or `dict` raises `TypeError`. Use `tuple` instead of `list`, or `frozenset` for sets.
2. **Caching methods on instances.** `@lru_cache` on a class method includes `self` in the cache key, which holds a reference to `self` and prevents garbage collection. Use `@cache` on module-level functions, or use `methodtools.lru_cache` for methods.
3. **Using on functions with side effects.** Cache the pure computation, not functions that write to DB or send emails. Those side effects should only happen once, not get "skipped" on cache hits.

## ✅ When to Use `@lru_cache` vs Redis
**`@lru_cache`** — single process, instant, zero setup. Use for:
- In-process computation results
- Settings and config loaded once
- Functions called many times in the same request with the same args

**Redis cache** — distributed, survives restarts, shared across workers. Use for:
- Caching DB query results
- Shared state across multiple API server instances
- Anything that needs to survive a process restart

## 🔗 Related Concepts
- [python_core/010_functools_basics](../../python_core/010_functools_basics) — `lru_cache`, `partial`, `wraps`
- [performance/051_caching_fundamentals](../051_caching_fundamentals) — caching concepts
- [performance/053_redis_as_cache](../053_redis_as_cache) — distributed alternative to lru_cache

## 🚀 Next Step
In `python-backend-mastery`: **`cache` + `cached_property`** — Python 3.9's `@cache` (unbounded alias for `lru_cache(maxsize=None)`), and `@cached_property` for computing instance attributes lazily and storing the result on the instance.

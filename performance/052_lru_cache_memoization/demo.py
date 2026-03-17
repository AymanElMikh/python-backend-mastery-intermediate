"""
Demo: lru_cache — Function-Level Memoization
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import time
from functools import lru_cache, cache
from typing import Optional


# ── Section 1: Basic lru_cache usage ─────────────────────────────────────────

DB_CALLS = 0

@lru_cache(maxsize=128)
def get_role_permissions(role: str) -> frozenset:
    """
    Simulates a DB lookup for permissions.
    Called many times per request — caching avoids repeated queries.
    Note: uses frozenset (hashable) not set (unhashable).
    """
    global DB_CALLS
    DB_CALLS += 1
    time.sleep(0.05)   # simulate 50ms DB query
    permissions = {
        "admin":   frozenset(["read", "write", "delete", "manage_users"]),
        "editor":  frozenset(["read", "write"]),
        "viewer":  frozenset(["read"]),
    }
    print(f"    [DB] Querying permissions for role={role!r} (call #{DB_CALLS})")
    return permissions.get(role, frozenset())


# ── Section 2: Recursive function — classic memoization ──────────────────────

@lru_cache(maxsize=None)   # unbounded — keep all results
def fibonacci(n: int) -> int:
    """
    Without @lru_cache this is O(2^n) — exponential.
    With @lru_cache each subproblem is computed once — O(n).
    """
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# ── Section 3: Config singleton via lru_cache ─────────────────────────────────

import os

@lru_cache(maxsize=1)
def get_app_settings() -> dict:
    """
    Reads config once on first call. Every subsequent call gets the cached dict.
    This is a Singleton implemented with @lru_cache.
    """
    print("    [Config] Reading environment variables...")
    return {
        "db_url": os.environ.get("DATABASE_URL", "sqlite:///dev.db"),
        "debug":  os.environ.get("DEBUG", "false").lower() == "true",
        "app_name": os.environ.get("APP_NAME", "MyApp"),
    }


# ── Section 4: The common mistake — unhashable arguments ─────────────────────

@lru_cache(maxsize=64)
def process_tags(tags: tuple) -> list:
    """
    CORRECT: takes a tuple (hashable), not a list (unhashable).
    Caller must convert: process_tags(tuple(my_list))
    """
    return sorted(set(tags))  # deduplicate and sort


def process_tags_bad(tags: list) -> list:
    """Can't use @lru_cache here — list is not hashable."""
    return sorted(set(tags))


# ── Section 5: cache_info and cache_clear ────────────────────────────────────

def check_permission(user_role: str, action: str) -> bool:
    """Uses cached permissions — fast after first call per role."""
    allowed = get_role_permissions(user_role)
    return action in allowed


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: lru_cache Memoization")
    print("=" * 55)

    print("\n--- Permission caching: same role called multiple times ---")
    t0 = time.monotonic()
    roles_and_actions = [
        ("admin", "delete"), ("editor", "write"), ("viewer", "read"),
        ("admin", "write"),  ("editor", "read"),  ("viewer", "delete"),
        ("admin", "manage_users"), ("editor", "write"), ("viewer", "read"),
    ]
    for role, action in roles_and_actions:
        allowed = check_permission(role, action)
        print(f"  {role:8s} can {action:15s}: {allowed}")

    elapsed = time.monotonic() - t0
    print(f"\n  Total time: {elapsed*1000:.0f}ms for {len(roles_and_actions)} checks")
    print(f"  Only 3 DB calls made (one per unique role)")
    print(f"  Cache info: {get_role_permissions.cache_info()}")

    print("\n--- Fibonacci with memoization ---")
    t0 = time.monotonic()
    for n in [10, 20, 30, 35]:
        result = fibonacci(n)
        print(f"  fibonacci({n:2d}) = {result}")
    elapsed = time.monotonic() - t0
    print(f"  All 4 calls took {elapsed*1000:.2f}ms total (subproblems reused)")
    print(f"  Cache info: {fibonacci.cache_info()}")

    print("\n--- Config singleton ---")
    for i in range(3):
        settings = get_app_settings()
    print(f"  Called 3 times, env read: 1 time")
    print(f"  Settings: {settings}")
    print(f"  Cache info: {get_app_settings.cache_info()}")

    print("\n--- Unhashable argument: the common mistake ---")
    try:
        @lru_cache(maxsize=64)
        def bad_fn(items: list) -> int:
            return len(items)
        bad_fn([1, 2, 3])  # will raise TypeError
    except TypeError as e:
        print(f"  list argument → TypeError: {e}")

    print("\n  Correct: use tuple instead of list")
    result = process_tags(("Python", "Backend", "Python", "API"))
    print(f"  process_tags(tuple) = {result}")
    print(f"  Cache info: {process_tags.cache_info()}")

    print("\n--- cache_clear: reset when underlying data changes ---")
    print(f"  Before clear: {get_role_permissions.cache_info()}")
    get_role_permissions.cache_clear()
    print(f"  After clear:  {get_role_permissions.cache_info()}")
    print("  Next call will hit DB again")

    print("\n--- lru_cache vs Redis: which to use ---")
    print("  lru_cache: in-process, instant, zero setup")
    print("             BUT: lost on restart, not shared between workers")
    print("  Redis:     distributed, survives restarts, shared across all workers")
    print("             BUT: network latency (~1ms), requires Redis server")
    print()
    print("  Rule: lru_cache for process-local stable data")
    print("        Redis for anything shared or that survives restarts")

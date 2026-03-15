"""
Demo: functools — lru_cache, partial, wraps
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import time
from functools import lru_cache, partial, wraps, cache

# ── Section 1: lru_cache — memoizing expensive function calls ────────────────

# Without cache: calling fibonacci(35) recalculates everything from scratch
def fibonacci_no_cache(n: int) -> int:
    if n < 2:
        return n
    return fibonacci_no_cache(n - 1) + fibonacci_no_cache(n - 2)

# With cache: each unique n is calculated only once, results stored in memory
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Real-world use: caching permission lookups (same role = same permissions)
_fake_db_call_count = [0]

@lru_cache(maxsize=256)
def get_role_permissions(role: str) -> frozenset:
    """Simulate an expensive DB lookup that we cache."""
    _fake_db_call_count[0] += 1
    permissions_map = {
        "admin": frozenset(["read", "write", "delete", "manage_users"]),
        "editor": frozenset(["read", "write"]),
        "viewer": frozenset(["read"]),
    }
    time.sleep(0.01)  # simulate DB latency
    return permissions_map.get(role, frozenset())


# ── Section 2: partial — pre-filling function arguments ──────────────────────

def send_notification(message: str, channel: str, priority: str = "normal",
                      retry: bool = True) -> dict:
    """Generic notification sender."""
    return {
        "message": message,
        "channel": channel,
        "priority": priority,
        "retry": retry,
    }

# Specialize the generic function for each channel
send_email = partial(send_notification, channel="email", retry=True)
send_sms   = partial(send_notification, channel="sms",   priority="high", retry=False)
send_slack = partial(send_notification, channel="slack", priority="normal", retry=True)

# partial with positional args
def power(base: float, exponent: float) -> float:
    return base ** exponent

square = partial(power, exponent=2)
cube   = partial(power, exponent=3)
sqrt   = partial(power, exponent=0.5)


# ── Section 3: wraps — preserving function metadata in decorators ─────────────

# WRONG: without @wraps, metadata is lost
def bad_timing_decorator(func):
    def wrapper(*args, **kwargs):  # wrapper's name, not the original
        start = time.time()
        result = func(*args, **kwargs)
        print(f"  Took {time.time() - start:.4f}s")
        return result
    return wrapper  # wrapper.__name__ = "wrapper"

# RIGHT: @wraps preserves __name__, __doc__, __module__, __annotations__
def good_timing_decorator(func):
    @wraps(func)  # copy metadata from func to wrapper
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"  [{func.__name__}] took {time.time() - start:.4f}s")
        return result
    return wrapper

@bad_timing_decorator
def important_calculation_bad(x: int, y: int) -> int:
    """Adds two numbers — very important."""
    return x + y

@good_timing_decorator
def important_calculation_good(x: int, y: int) -> int:
    """Adds two numbers — very important."""
    return x + y


# ── Section 4: Common mistake — unhashable arguments with lru_cache ───────────

@lru_cache(maxsize=None)
def process_items_cached(items: tuple) -> list:
    """lru_cache requires hashable args — use tuple, not list."""
    return [item * 2 for item in items]

# WRONG: process_items_cached([1, 2, 3])  →  TypeError: unhashable type: 'list'
# RIGHT: convert to tuple first
def process_items(items: list) -> list:
    return process_items_cached(tuple(items))  # convert before caching


# ── Section 5: cache_info and cache_clear ────────────────────────────────────

@cache  # Python 3.9+ — equivalent to @lru_cache(maxsize=None)
def expensive_lookup(key: str) -> str:
    """Simulates an expensive external lookup."""
    time.sleep(0.01)
    return f"result_for_{key}"


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: functools — lru_cache, partial, wraps")
    print("=" * 50)

    print("\n--- Section 1: lru_cache performance ---")
    # Without cache
    start = time.time()
    result = fibonacci_no_cache(30)
    no_cache_time = time.time() - start
    print(f"  fibonacci(30) without cache: {result} in {no_cache_time:.4f}s")

    # With cache
    start = time.time()
    result = fibonacci(30)
    with_cache_time = time.time() - start
    print(f"  fibonacci(30) with cache:    {result} in {with_cache_time:.6f}s")
    print(f"  Speedup: ~{no_cache_time / max(with_cache_time, 0.000001):.0f}x faster")
    print(f"  Cache info: {fibonacci.cache_info()}")

    print("\n  Permission lookup (should hit DB only once per role):")
    _fake_db_call_count[0] = 0
    for role in ["admin", "editor", "admin", "viewer", "editor", "admin"]:
        perms = get_role_permissions(role)
        print(f"    {role}: {sorted(perms)}")
    print(f"  Total DB calls: {_fake_db_call_count[0]} (instead of 6 — cache hit!)")
    print(f"  Cache info: {get_role_permissions.cache_info()}")

    print("\n--- Section 2: partial ---")
    print(f"  square(5)  = {square(5)}")
    print(f"  cube(3)    = {cube(3)}")
    print(f"  sqrt(16)   = {sqrt(16)}")

    email_notif = send_email("Server is down!", priority="critical")
    sms_notif   = send_sms("Alert: CPU > 90%")
    slack_notif = send_slack("Deployment complete")
    for n in [email_notif, sms_notif, slack_notif]:
        print(f"  {n}")

    print("\n--- Section 3: @wraps matters ---")
    print(f"  WITHOUT @wraps: name='{important_calculation_bad.__name__}', "
          f"doc='{important_calculation_bad.__doc__}'")
    print(f"  WITH    @wraps: name='{important_calculation_good.__name__}', "
          f"doc='{important_calculation_good.__doc__}'")
    important_calculation_good(3, 4)

    print("\n--- Section 4: lru_cache + unhashable args ---")
    result1 = process_items([1, 2, 3])
    result2 = process_items([1, 2, 3])  # cache hit
    result3 = process_items([4, 5, 6])
    print(f"  process_items([1,2,3]) = {result1}")
    print(f"  process_items([1,2,3]) = {result2} (from cache)")
    print(f"  process_items([4,5,6]) = {result3}")
    print(f"  Cache info: {process_items_cached.cache_info()}")

    print("\n--- Section 5: cache_info and cache_clear ---")
    for key in ["user:1", "user:2", "user:1", "user:3", "user:2"]:
        val = expensive_lookup(key)
    info = expensive_lookup.cache_info()
    print(f"  Cache info: hits={info.hits}, misses={info.misses}, size={info.currsize}")

    expensive_lookup.cache_clear()
    info = expensive_lookup.cache_info()
    print(f"  After cache_clear: {info}")

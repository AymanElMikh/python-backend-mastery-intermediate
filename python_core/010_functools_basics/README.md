# functools — lru_cache, partial, wraps

## 🎯 Interview Question
"What is `functools.lru_cache` and when would you use it? What about `functools.partial`?"

## 💡 Short Answer (30 seconds)
`functools` is a standard library module with utilities for working with functions. `lru_cache` is a decorator that memoizes function results — it caches the return value based on the arguments, so repeated calls with the same args skip the computation. `partial` lets you pre-fill some arguments of a function to create a new, simpler callable. You'd use `lru_cache` for expensive pure functions (DB lookups, computations), and `partial` when you want to specialize a general function for a specific use case.

## 🔬 Explanation
The three most important parts of `functools` for backend developers:

**`lru_cache(maxsize=128)`**:
- LRU = Least Recently Used — old entries are evicted when the cache fills
- Works only with **pure functions** — same input must always give same output
- Arguments must be **hashable** (no lists or dicts as args — use tuples)
- `maxsize=None` = unlimited cache (use `cache` alias in Python 3.9+)
- Check stats: `my_func.cache_info()`, clear: `my_func.cache_clear()`

**`partial(func, *args, **kwargs)`**:
- Creates a new callable with some arguments pre-filled
- Equivalent to a closure that calls `func` with fixed args, but more readable
- Common use: adapting a function's signature for use as a callback

**`wraps(func)`**:
- Used inside decorators to copy the wrapped function's `__name__`, `__doc__`, etc.
- Without it, all decorated functions appear as `wrapper` in tracebacks and docs

Real-world examples:
```python
# Caching expensive config lookups
@lru_cache(maxsize=256)
def get_permission_set(role: str) -> frozenset:
    return frozenset(DB.fetch_permissions(role))

# Specializing a generic send function
send_email = partial(send_notification, channel="email", retry=True)
send_sms = partial(send_notification, channel="sms", retry=False)
```

## 💻 Code Example
```python
from functools import lru_cache, partial, wraps
import time

# lru_cache: memoize expensive computations
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)  # without cache: exponential time

# partial: pre-fill arguments
def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube   = partial(power, exponent=3)

print(square(5))  # 25
print(cube(3))    # 27

# wraps: preserve function metadata in decorators
def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

## ⚠️ Common Mistakes

1. **Caching functions with mutable or unhashable arguments** — `@lru_cache` requires all arguments to be hashable. Passing a `list` or `dict` raises `TypeError`. Convert to `tuple` or `frozenset` before calling.

2. **Caching functions with side effects or time-dependent results** — `lru_cache` is for pure functions. Caching `get_current_user()` or anything that reads from a database without a stable key will return stale data.

3. **Forgetting `@wraps` in decorators** — leads to all decorated functions showing as `<function wrapper at 0x...>` in logs, tracebacks, and documentation tools. Always include `@wraps(func)`.

## ✅ When to Use vs When NOT to Use

**Use `lru_cache` when:**
- The function is pure (deterministic, no side effects)
- The same arguments are called repeatedly
- The computation is expensive (CPU-heavy, or a lookup you want to avoid repeating)
- Memory usage is acceptable (the cache lives in-process, not distributed)

**Don't use `lru_cache` when:**
- Results can change over time (DB reads, config that can update)
- Arguments are large objects (caches the return value by reference — memory bloat)
- You need cross-process or distributed caching — use Redis instead

**Use `partial` when:**
- You want to create a specialized version of a general function
- You're passing a function as a callback and need to bind some arguments first

## 🔗 Related Concepts
- [001_decorators_basics](../001_decorators_basics) — `@wraps` is used in every decorator
- [004_closures](../004_closures) — `partial` is similar to a closure factory
- [003_generators_yield](../003_generators_yield) — `itertools` is the sibling module for iteration

## 🚀 Next Step
In `python-backend-mastery`: **`functools.reduce`, `operator` module, and functional pipelines** — composing functions with `reduce`, using `operator.itemgetter` / `attrgetter` for sorting, and building data transformation pipelines without lambda overuse.

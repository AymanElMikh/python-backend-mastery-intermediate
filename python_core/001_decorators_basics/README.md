# Decorators — How and Why

## 🎯 Interview Question
"Can you explain what a Python decorator is and show me how you'd write one from scratch?"

## 💡 Short Answer (30 seconds)
A decorator is a function that wraps another function to add behavior before or after it runs — without changing the original function's code. You apply it with the `@decorator_name` syntax above a function definition. They're used heavily in real projects for logging, timing, auth checks, and caching.

## 🔬 Explanation
Think of a decorator like a sleeve over a water bottle — the bottle (your function) stays the same, but the sleeve adds something extra (insulation, a grip, a label).

When Python sees `@my_decorator` above `def my_function`, it's equivalent to:
```python
my_function = my_decorator(my_function)
```

Your function gets passed into the decorator, which returns a new function (the "wrapper") that adds behavior. This pattern is everywhere in real backends:
- **FastAPI/Flask**: `@app.get("/")` is a decorator registering routes
- **Auth**: `@login_required` checks if a user is authenticated before running a view
- **Timing/logging**: wrapping functions to measure performance
- **Retry logic**: automatically retrying failed API calls

The key insight: decorators let you separate concerns — your business logic stays clean while cross-cutting concerns (logging, auth, timing) live in decorators.

## 💻 Code Example
```python
import functools
import time

# A decorator is just a function that takes a function and returns a function
def timer(func):
    @functools.wraps(func)  # preserves the original function's name and docstring
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)  # call the original function
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def fetch_users():
    time.sleep(0.1)  # simulate a DB call
    return ["alice", "bob"]

# This is identical to: fetch_users = timer(fetch_users)
users = fetch_users()
```

## ⚠️ Common Mistakes

1. **Forgetting `@functools.wraps(func)`** — without it, your wrapped function loses its `__name__` and `__doc__`. Debugging becomes painful because every function looks like `wrapper`.

2. **Not passing through `*args, **kwargs`** — if your wrapper only does `def wrapper()`, it breaks for any function that takes arguments. Always use `def wrapper(*args, **kwargs)`.

3. **Returning the result** — forgetting `return result` in the wrapper means your function silently returns `None`. Classic bug that's hard to spot.

## ✅ When to Use vs When NOT to Use

**Use decorators when:**
- You need the same behavior across many functions (logging, auth, retry)
- The added behavior is truly separate from the function's purpose
- You're building a framework or library with reusable cross-cutting concerns

**Avoid decorators when:**
- The behavior is only needed once — just call the helper directly
- The logic is complex enough that hiding it makes debugging harder
- You need to inspect or modify arguments in non-obvious ways — a plain function call is clearer

## 🔗 Related Concepts
- [004_closures](../004_closures) — decorators are built on closures
- [010_functools_basics](../010_functools_basics) — `functools.wraps` and `functools.lru_cache`

## 🚀 Next Step
In `python-backend-mastery`: **Class-based decorators and descriptor protocol** — how decorators interact with `__get__` when used on class methods, and how to write decorators that work on both functions and methods seamlessly.

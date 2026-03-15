# Context Managers — The `with` Statement

## 🎯 Interview Question
"What is a context manager in Python, and why would you write a custom one instead of just using try/finally?"

## 💡 Short Answer (30 seconds)
A context manager is an object that defines setup and teardown logic that runs automatically when you enter and exit a `with` block. You use them to guarantee cleanup happens even if an exception is raised — for things like closing files, releasing database connections, or releasing locks. Writing a custom one is cleaner than `try/finally` because the cleanup logic lives in one reusable place.

## 🔬 Explanation
The `with` statement is Python's way of saying "set this up, do some work, then always clean up — no matter what."

Under the hood, `with` calls two methods on the context manager object:
- `__enter__`: runs at the start, can return a value (the `as` part)
- `__exit__`: runs at the end, even if an exception occurred

You see this constantly in real projects:
- `with open("file.txt") as f:` — file is always closed
- `with db.session() as session:` — transaction is always committed or rolled back
- `with lock:` — threading lock is always released
- `with pytest.raises(ValueError):` — test assertion

**Two ways to write a custom context manager:**
1. A class with `__enter__` and `__exit__` — more control, good for complex state
2. `@contextmanager` from `contextlib` — simpler for most cases, just use `yield`

In 2–3 year developer interviews, showing you know `contextlib.contextmanager` and can explain *why* it's better than try/finally is a strong signal.

## 💻 Code Example
```python
from contextlib import contextmanager
import time

# Option 1: using @contextmanager (simplest — use this 90% of the time)
@contextmanager
def timer(label):
    start = time.time()
    try:
        yield  # everything in the `with` block runs here
    finally:
        elapsed = time.time() - start
        print(f"{label}: {elapsed:.4f}s")

with timer("database query"):
    time.sleep(0.1)  # simulate work

# Option 2: class-based (when you need more control)
class DatabaseConnection:
    def __enter__(self):
        print("Opening DB connection")
        self.conn = "fake_connection"
        return self.conn  # this is what `as conn` gets

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing DB connection")
        # if exc_type is not None, an exception occurred
        return False  # False = don't suppress the exception

with DatabaseConnection() as conn:
    print(f"Using {conn}")
```

## ⚠️ Common Mistakes

1. **Not handling exceptions in `__exit__`** — `__exit__` receives `(exc_type, exc_val, exc_tb)`. If you return `True`, you suppress the exception silently. This is almost never what you want. Always return `False` (or `None`) unless you intentionally want to swallow errors.

2. **Forgetting `try/finally` inside `@contextmanager`** — if you don't wrap the `yield` in `try/finally`, cleanup code after `yield` won't run when an exception occurs inside the `with` block.

3. **Thinking `with` replaces exception handling** — `with` ensures cleanup runs, but exceptions still propagate. `with open(...)` doesn't catch `FileNotFoundError`.

## ✅ When to Use vs When NOT to Use

**Use context managers when:**
- You have setup + teardown that must always be paired (open/close, lock/unlock, begin/commit)
- You want to share this cleanup pattern across multiple call sites
- You're writing code that other developers will use and cleanup should be automatic

**Avoid over-engineering when:**
- You only need cleanup in one place — a `try/finally` block is fine and more explicit
- The "resource" is just a local variable with no cleanup needed

## 🔗 Related Concepts
- [001_decorators_basics](../001_decorators_basics) — `@contextmanager` is itself a decorator
- [007_exception_handling](../007_exception_handling) — context managers and exception propagation

## 🚀 Next Step
In `python-backend-mastery`: **AsyncContextManager** — writing `async with` compatible context managers using `__aenter__`/`__aexit__`, essential for async database connections and HTTP clients like `httpx.AsyncClient`.

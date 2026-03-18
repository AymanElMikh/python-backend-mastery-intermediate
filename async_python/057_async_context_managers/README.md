# Async Context Managers — `async with` for Resource Management

## 🎯 Interview Question
"What is an async context manager and when would you use `async with` instead of `with`?"

## 💡 Short Answer (30 seconds)
An async context manager is like a regular context manager, but its setup and teardown involve async operations — like opening a database connection or acquiring a network resource. You use `async with` when the entering or exiting of the context requires an `await`. Common examples: database sessions, HTTP client sessions, file I/O libraries.

## 🔬 Explanation
Regular `with` works great for synchronous setup/teardown:
```python
with open("file.txt") as f:  # __enter__ / __exit__
    data = f.read()
```

But what if opening a connection requires a network call? That's async I/O — you can't block for it. `async with` solves this:

```python
async with get_db_session() as session:  # __aenter__ / __aexit__
    await session.execute(query)
```

**How to create one:** Implement `__aenter__` and `__aexit__` as async methods. Or use `@asynccontextmanager` from `contextlib` with `yield`.

**Where you'll see this in real projects:**
- SQLAlchemy async sessions: `async with AsyncSession() as session:`
- aiohttp HTTP clients: `async with aiohttp.ClientSession() as session:`
- asyncpg database connections: `async with pool.acquire() as conn:`
- asyncio locks: `async with lock:`

## 💻 Code Example
```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_db_connection(db_url: str):
    print(f"Opening connection to {db_url}")
    connection = {"url": db_url, "open": True}  # simulate connection
    try:
        yield connection
    finally:
        # This cleanup always runs — even if an exception occurred
        connection["open"] = False
        print("Connection closed")

async def main():
    async with managed_db_connection("postgresql://localhost/mydb") as conn:
        print(f"Using connection: {conn}")
        # do database work here
```

## ⚠️ Common Mistakes
1. **Using regular `with` for async resources** — if an async library returns an async context manager, using `with` instead of `async with` raises a `TypeError` or silently skips the setup.
2. **Forgetting `async with` inside sync code** — `async with` can only be used inside `async def` functions, just like `await`.
3. **Not using context managers at all** — manually opening and closing connections without a context manager risks leaking connections if an exception occurs.

## ✅ When to Use vs When NOT to Use
**Use `async with` when:** Opening database sessions, HTTP client sessions, acquiring locks, or any resource where setup/teardown involves async I/O.

**Regular `with` is fine for:** Synchronous resources like file handles, in-memory locks, or anything that doesn't need async setup.

## 🔗 Related Concepts
- [051_async_await_basics](../051_async_await_basics) — foundational async syntax
- [058_async_iterators](../058_async_iterators) — async for, the iteration counterpart
- [python_core/002_context_managers](../../python_core/002_context_managers) — sync context managers

## 🚀 Next Step
In `python-backend-mastery`: **lifespan context managers in FastAPI** — using `@asynccontextmanager` with the `lifespan` parameter to manage startup/shutdown of DB pools, caches, and background workers.

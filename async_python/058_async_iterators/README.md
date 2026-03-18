# Async Iterators — `async for` to Stream Data Without Blocking

## 🎯 Interview Question
"What is an async iterator? When would you use `async for` instead of `for`?"

## 💡 Short Answer (30 seconds)
An async iterator is like a regular iterator, but each call to get the next item is an async operation — like streaming rows from a database or reading chunks from a network socket. You use `async for` when iterating itself involves waiting for I/O, and you don't want to block the event loop while fetching each item.

## 🔬 Explanation
A regular `for` loop pulls all items at once (or from an in-memory iterator). That's fine for lists. But imagine streaming 100,000 rows from a database — you don't want to load them all into memory at once.

Async iterators let you fetch items **lazily and asynchronously** — each `__anext__` call is awaited, so the event loop stays responsive between items.

**The protocol:**
- `__aiter__()` returns the iterator object
- `__anext__()` is an async method that returns the next item or raises `StopAsyncIteration`

**Where you see this in real code:**
- `async for row in db_cursor:` — streaming DB results (SQLAlchemy async)
- `async for chunk in response.content:` — streaming HTTP response body (aiohttp)
- `async for message in websocket:` — WebSocket messages (FastAPI/starlette)

The simplest way to create one: use `async def` with `yield` — an **async generator**.

## 💻 Code Example
```python
import asyncio

async def stream_users(total: int):
    """Async generator — yields one user at a time from a 'database'."""
    for i in range(1, total + 1):
        await asyncio.sleep(0.1)  # simulates fetching the next row
        yield {"id": i, "name": f"User {i}"}

async def main():
    # async for — handles the await between each item automatically
    async for user in stream_users(5):
        print(f"Processing: {user}")
```

## ⚠️ Common Mistakes
1. **Using a regular `for` on an async iterable** — `for row in async_cursor` doesn't await each step, so you'll get a `TypeError` or iterate over coroutine objects instead of values.
2. **Loading everything into memory first** — `results = [r async for r in cursor]` collects all items before processing. This defeats the streaming benefit for large datasets.
3. **Forgetting that `async for` requires an async context** — just like `await`, you can only use `async for` inside an `async def` function.

## ✅ When to Use vs When NOT to Use
**Use `async for` when:** Iterating over a stream where each item requires an async fetch — DB cursor, HTTP stream, WebSocket messages, Kafka consumer.

**Regular `for` is fine for:** In-memory collections, sync generators, anything already loaded into memory.

## 🔗 Related Concepts
- [057_async_context_managers](../057_async_context_managers) — `async with` is often used alongside `async for` (e.g., opening a DB session then iterating)
- [python_core/003_generators_yield](../../python_core/003_generators_yield) — sync generators, the foundation for async generators
- [051_async_await_basics](../051_async_await_basics) — the event loop model

## 🚀 Next Step
In `python-backend-mastery`: **Async generators with back-pressure** — using `asyncio.Queue` to control how fast data flows through a pipeline, and streaming responses in FastAPI with `StreamingResponse`.

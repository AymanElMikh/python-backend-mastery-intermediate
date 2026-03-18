# async/await Basics — Writing Non-Blocking Code

## 🎯 Interview Question
"What does `async def` and `await` do in Python? How is it different from a regular function?"

## 💡 Short Answer (30 seconds)
`async def` defines a coroutine — a function that can pause and resume. `await` is the pause point: it suspends the current coroutine and gives control back to the event loop, which can run other tasks while waiting. This is how you do non-blocking I/O without threads.

## 🔬 Explanation
Think of `await` like saying "I'm waiting for something that takes time — go do other work and come back to me when it's ready."

With normal (synchronous) code, if you make a network call, your entire program sits frozen waiting for the response. With `async/await`, Python can work on other tasks during that wait — no threads, no callbacks.

Key rules to know:
- `async def` makes a function into a coroutine. Calling it doesn't run it — it returns a coroutine object.
- `await` can only be used inside `async def` functions.
- You need an **event loop** to actually run coroutines (usually `asyncio.run()`).

Real use case: When your FastAPI endpoint makes a database call and an external API call, `async/await` lets them overlap instead of waiting for each one in sequence.

## 💻 Code Example
```python
import asyncio

# Regular function — blocks everything while "sleeping"
def sync_fetch():
    import time
    time.sleep(1)
    return "data"

# Async function — pauses WITHOUT blocking the event loop
async def async_fetch():
    await asyncio.sleep(1)  # simulates a slow I/O call (DB, HTTP, etc.)
    return "data"

async def main():
    # This runs but doesn't block other async tasks
    result = await async_fetch()
    print(f"Got: {result}")

# asyncio.run() creates the event loop and runs the coroutine
asyncio.run(main())
```

## ⚠️ Common Mistakes
1. **Calling `async def` without `await`** — `result = async_fetch()` returns a coroutine object, not the result. You'll see `<coroutine object async_fetch at 0x...>` and a `RuntimeWarning`.
2. **Using `time.sleep()` inside async code** — it blocks the entire event loop. Always use `await asyncio.sleep()` instead.
3. **Thinking `async` makes things faster by itself** — it only helps when you're waiting on I/O. CPU-heavy work (`for` loops, math) is not improved by async.

## ✅ When to Use vs When NOT to Use
**Use async when:** Your code waits on I/O — database queries, HTTP calls, file reads, Redis, message queues.

**Don't use async when:** Your code is CPU-bound (data processing, image manipulation, complex calculations). Use `multiprocessing` or a task queue like Celery instead.

## 🔗 Related Concepts
- [052_coroutines_explained](../052_coroutines_explained) — what a coroutine actually is
- [053_asyncio_run](../053_asyncio_run) — how to start and run the event loop
- [054_asyncio_tasks](../054_asyncio_tasks) — running multiple coroutines concurrently
- [056_when_to_use_async](../056_when_to_use_async) — the full IO-bound vs CPU-bound guide

## 🚀 Next Step
In `python-backend-mastery`: **Event loop internals** — how `asyncio` actually schedules coroutines, and how to work with multiple event loops or custom loop policies.

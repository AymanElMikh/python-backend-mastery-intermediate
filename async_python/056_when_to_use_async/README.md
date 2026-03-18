# When to Use Async — I/O-Bound vs CPU-Bound

## 🎯 Interview Question
"When should you use async/await in Python, and when should you NOT use it? What's the difference between I/O-bound and CPU-bound?"

## 💡 Short Answer (30 seconds)
Use async for I/O-bound work — anything where your code spends time *waiting* for something external (database, API, file). Avoid async for CPU-bound work — heavy computation, image processing, data crunching — because async doesn't add parallelism there. For CPU-bound tasks, use `multiprocessing` or offload to a task queue like Celery.

## 🔬 Explanation
**I/O-bound:** Your code is fast; the bottleneck is waiting for something else.
- Database query: your CPU is idle while the DB processes and responds.
- HTTP call: your CPU is idle while the network delivers bytes.
- File read: your CPU is idle while the disk seeks and reads.

With `async/await`, the event loop can run other coroutines during those idle waits. One process handles thousands of concurrent requests because they're all just waiting on I/O at different times.

**CPU-bound:** Your code *is* the bottleneck — it needs the processor every millisecond.
- Resizing images, parsing huge CSV files, computing hashes, machine learning inference.
- `async` doesn't help here — while one coroutine computes, the event loop is blocked anyway. Python's GIL also prevents true parallel CPU work in threads.

**The rule:**
- I/O-bound → `async/await` (or threads, but async is cleaner)
- CPU-bound → `multiprocessing`, `concurrent.futures.ProcessPoolExecutor`, or Celery worker

**In FastAPI:** Even if your endpoint is `async def`, if it calls a CPU-heavy synchronous library, you're still blocking. Use `run_in_executor()` to push that work to a thread/process pool.

## 💻 Code Example
```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

# ✅ Good async use — waiting on I/O
async def fetch_from_db(user_id: int) -> dict:
    await asyncio.sleep(0.1)  # DB is thinking
    return {"id": user_id}

# ❌ Bad async use — CPU work doesn't benefit
async def bad_compute(n: int) -> int:
    total = sum(range(n))  # blocks the event loop!
    return total

# ✅ Right way for CPU work — offload to process pool
async def good_compute(n: int) -> int:
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, sum, range(n))
    return result
```

## ⚠️ Common Mistakes
1. **Wrapping CPU work in `async def` and thinking it's now concurrent** — the coroutine still runs on the same thread. The event loop is blocked while it computes. No benefit.
2. **Using `async def` for everything by default** — if a function never awaits anything, it doesn't need to be async. Adding `async` to a sync function just makes callers need to `await` it for no reason.
3. **Mixing sync blocking libraries in async code** — calling `requests.get()` (synchronous) inside an `async def` blocks the entire event loop. Use `httpx` or `aiohttp` instead.

## ✅ When to Use vs When NOT to Use
**Async shines for:** Web servers handling many concurrent requests, microservices doing lots of external calls, anything involving network or disk I/O.

**Async doesn't help for:** Number crunching, ML inference, data transformation pipelines, image/video processing.

## 🔗 Related Concepts
- [051_async_await_basics](../051_async_await_basics) — the syntax
- [054_asyncio_tasks](../054_asyncio_tasks) — running I/O operations concurrently
- [060_async_http_requests](../060_async_http_requests) — practical I/O-bound async example
- [performance/celery_intro](../../performance) — offloading CPU work to task queues

## 🚀 Next Step
In `python-backend-mastery`: **`asyncio.run_in_executor()`** deep dive — how to bridge the sync/async boundary cleanly, and `uvloop` for making I/O-bound async even faster.

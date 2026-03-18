# asyncio Timeouts — Cancelling Slow Operations

## 🎯 Interview Question
"How do you add a timeout to an async operation in Python? What happens if the operation exceeds the limit?"

## 💡 Short Answer (30 seconds)
Use `asyncio.wait_for()` to add a timeout to any awaitable. If the operation doesn't complete within the given seconds, it raises `asyncio.TimeoutError` and automatically cancels the underlying task. In Python 3.11+, `asyncio.timeout()` is the newer context manager approach.

## 🔬 Explanation
In production, any I/O call can hang — a slow database, an unresponsive external API, a network partition. Without timeouts, your coroutine waits forever and eventually exhausts your server's resources.

**`asyncio.wait_for(coro, timeout=N)`:**
- Runs the coroutine with a deadline
- Raises `asyncio.TimeoutError` if it exceeds N seconds
- Cancels the coroutine automatically on timeout

**Python 3.11+ `asyncio.timeout(N)`:**
- Context manager style — cleaner for wrapping multiple awaits
- Raises `TimeoutError` (built-in, not `asyncio.TimeoutError`)

Real use case: Your endpoint calls an external payment API. If it doesn't respond in 5 seconds, return an error to the user instead of hanging their request.

**Always handle `TimeoutError`:** If you don't catch it, the exception propagates to the caller. In FastAPI, unhandled timeouts become 500 errors. Catch and return a 408 (Request Timeout) or 503 (Service Unavailable) instead.

## 💻 Code Example
```python
import asyncio

async def call_payment_api() -> dict:
    await asyncio.sleep(10)  # this API is very slow
    return {"status": "ok"}

async def process_payment():
    try:
        result = await asyncio.wait_for(call_payment_api(), timeout=5.0)
        return result
    except asyncio.TimeoutError:
        # Don't leave the user hanging — return a useful error
        raise Exception("Payment service timed out. Please try again.")
```

## ⚠️ Common Mistakes
1. **Not catching `TimeoutError`** — the exception propagates up and often becomes an unhandled 500. Always wrap `wait_for` in a try/except.
2. **Setting timeouts too tight** — a 100ms timeout on a DB query that normally takes 80ms will cause flaky failures in production. Base timeouts on measured p99 latency + buffer.
3. **Forgetting that timeout cancels the task** — if you have cleanup to do (close a connection, log an audit record), use `try/finally` inside the coroutine to handle `CancelledError`.

## ✅ When to Use vs When NOT to Use
**Always use timeouts for:** External API calls, third-party service integrations, any I/O you don't control directly.

**Less critical for:** Internal database calls with connection pooling (the pool has its own timeout), operations with known bounded execution time.

## 🔗 Related Concepts
- [054_asyncio_tasks](../054_asyncio_tasks) — tasks and cancellation
- [055_asyncio_gather](../055_asyncio_gather) — timeout a group of parallel operations
- [060_async_http_requests](../060_async_http_requests) — real-world timeout on HTTP calls

## 🚀 Next Step
In `python-backend-mastery`: **Circuit breakers** — going beyond timeouts to detect when a service is failing and stop calling it temporarily, preventing cascade failures across microservices.

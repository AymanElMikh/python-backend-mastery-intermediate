# asyncio.gather() — Running Multiple Coroutines and Collecting Results

## 🎯 Interview Question
"What does `asyncio.gather()` do, and when would you use it over manually creating tasks?"

## 💡 Short Answer (30 seconds)
`asyncio.gather()` runs multiple coroutines concurrently and returns all their results as a list, in the same order you passed them. It's the clean, idiomatic way to fan out and collect results — instead of manually creating tasks and awaiting each one.

## 🔬 Explanation
Think of `asyncio.gather()` as a "start all of these at the same time and give me all the results." It's the async equivalent of "make all these API calls in parallel, then continue when they've all finished."

Under the hood, `gather()` wraps each coroutine in a `Task`, runs them concurrently, and waits for all to complete before returning. Results come back in the **same order** as the inputs — not in completion order.

**Behavior options:**
- `return_exceptions=False` (default): if any coroutine raises, `gather()` immediately raises that exception and the other tasks continue running (but their results are discarded).
- `return_exceptions=True`: exceptions are returned as values in the result list instead of raised. Good for when partial failures are acceptable.

Real use case: A dashboard endpoint that needs to fetch user data, recent orders, and notification count from three separate services — all in parallel.

## 💻 Code Example
```python
import asyncio

async def get_user(user_id: int) -> dict:
    await asyncio.sleep(0.2)
    return {"id": user_id, "name": "Alice"}

async def get_orders(user_id: int) -> list:
    await asyncio.sleep(0.3)
    return [{"item": "laptop"}]

async def get_notifications(user_id: int) -> int:
    await asyncio.sleep(0.1)
    return 5

async def main():
    # All three run concurrently — total time ~0.3s (the longest one)
    user, orders, notifications = await asyncio.gather(
        get_user(1),
        get_orders(1),
        get_notifications(1),
    )
    print(f"User: {user}, Orders: {orders}, Notifications: {notifications}")
```

## ⚠️ Common Mistakes
1. **Expecting results in completion order** — `gather()` always returns results in input order. If the first coroutine is the slowest, you wait for it before the list is returned, but the index still matches.
2. **Not handling exceptions with `return_exceptions=True`** — if one of your parallel calls might fail, use `return_exceptions=True` and check each result: `if isinstance(result, Exception): handle it`.
3. **Using `gather()` for dependent operations** — if B needs A's result, they can't run in parallel. `gather()` is only for independent operations.

## ✅ When to Use vs When NOT to Use
**Use `gather()` when:** You have multiple independent I/O calls and want all their results — fan-out patterns, parallel data loading, dashboard aggregation.

**Don't use `gather()` when:** Operations are sequential (one depends on another), or you only have one coroutine (just `await` it directly).

## 🔗 Related Concepts
- [054_asyncio_tasks](../054_asyncio_tasks) — the lower-level way to do concurrency
- [059_asyncio_timeout](../059_asyncio_timeout) — timeouts for gather operations
- [060_async_http_requests](../060_async_http_requests) — real-world use of gather with HTTP

## 🚀 Next Step
In `python-backend-mastery`: **asyncio.TaskGroup** (Python 3.11+) — a safer alternative to `gather()` with structured cancellation, and **asyncio.as_completed()** for processing results as they arrive rather than waiting for all.

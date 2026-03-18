# asyncio Tasks — Running Coroutines Concurrently

## 🎯 Interview Question
"How do you run multiple async operations concurrently in Python? What's the difference between `await coroutine()` and `asyncio.create_task()`?"

## 💡 Short Answer (30 seconds)
`await coroutine()` runs a coroutine sequentially — you wait for it to finish before moving on. `asyncio.create_task()` schedules a coroutine to run in the background concurrently. Tasks let you start multiple operations and let them overlap, so a 3-second job + a 2-second job takes 3 seconds total instead of 5.

## 🔬 Explanation
The difference is timing:

- `await fetch_user()` → start it, wait for it, then continue. Like making one phone call, waiting on hold, then making the next call.
- `asyncio.create_task(fetch_user())` → start it now, continue doing other things, and check back when you need the result. Like sending emails to multiple people — you don't wait for each reply before sending the next.

`create_task()` immediately schedules the coroutine in the event loop. It returns a `Task` object — like a future/promise for the result. You `await` the task later when you need the result.

**Key behaviors:**
- Tasks run as soon as the event loop gets control (at the next `await` point).
- If you don't `await` a task, it may be garbage-collected before finishing (and Python warns you).
- You can cancel a task with `task.cancel()`.

Real use case: Fetching a user's profile AND their recent orders at the same time — two DB queries that don't depend on each other.

## 💻 Code Example
```python
import asyncio

async def fetch_profile(user_id: int) -> dict:
    await asyncio.sleep(0.5)  # simulates DB query
    return {"id": user_id, "name": "Alice"}

async def fetch_orders(user_id: int) -> list:
    await asyncio.sleep(0.3)  # simulates another DB query
    return [{"order": "laptop"}, {"order": "mouse"}]

async def main():
    # Sequential: 0.5 + 0.3 = 0.8 seconds
    profile = await fetch_profile(1)
    orders = await fetch_orders(1)

    # Concurrent with tasks: max(0.5, 0.3) = 0.5 seconds
    profile_task = asyncio.create_task(fetch_profile(1))
    orders_task = asyncio.create_task(fetch_orders(1))

    profile = await profile_task
    orders = await orders_task
```

## ⚠️ Common Mistakes
1. **Creating a task but never awaiting it** — the task runs in the background but you might not get the result, and if an exception occurs, it's silently swallowed. Always await your tasks.
2. **Expecting tasks to run before the first `await`** — tasks are scheduled but don't actually start until the event loop gets control (i.e., when you `await` something). The order of `create_task()` calls matters less than when you first yield control.
3. **Using `await coroutine()` when you want concurrency** — this is sequential. You must use `create_task()` (or `asyncio.gather()`) to get actual concurrent execution.

## ✅ When to Use vs When NOT to Use
**Use tasks when:** You have independent I/O operations that can run simultaneously — multiple DB queries, parallel API calls, sending notifications while processing data.

**Don't use tasks when:** Operations depend on each other (must use result of A to start B). Sequential `await` is clearer and correct there.

## 🔗 Related Concepts
- [051_async_await_basics](../051_async_await_basics) — understanding await vs tasks
- [055_asyncio_gather](../055_asyncio_gather) — cleaner way to run multiple tasks and collect results
- [059_asyncio_timeout](../059_asyncio_timeout) — cancelling tasks that take too long

## 🚀 Next Step
In `python-backend-mastery`: **asyncio.TaskGroup** (Python 3.11+) — structured concurrency that automatically cancels all sibling tasks if one fails, preventing the "fire and forget" task leak problem.

# Coroutines Explained — What They Are and How They Work

## 🎯 Interview Question
"What is a coroutine in Python? How is it different from a regular function or a generator?"

## 💡 Short Answer (30 seconds)
A coroutine is a function that can suspend its execution partway through and resume later. Unlike a regular function that runs start-to-finish in one shot, a coroutine can pause at `await` points, hand control back to the event loop, and pick up where it left off when the awaited thing is done.

## 🔬 Explanation
Think of coroutines like a chef who can juggle multiple dishes. When a dish is in the oven (waiting), the chef doesn't just stand there — they prep another dish. When the oven timer goes off, they return to the first dish. That's what `await` does: "I'm waiting for something — go do other work."

**Coroutine vs regular function:**
- Regular function: runs to completion, returns once, discarded.
- Coroutine: can be paused mid-execution, resumed multiple times, controlled by the event loop.

**Coroutine vs generator:**
- Generators use `yield` to produce values lazily.
- Coroutines use `await` to pause on I/O operations.
- Both are "suspendable" — but generators are about producing sequences, coroutines are about concurrency.

**The lifecycle of a coroutine:**
1. `async def my_func()` — defines it (but doesn't run it).
2. `my_func()` — creates a coroutine object (still hasn't run).
3. `await my_func()` or `asyncio.run(my_func())` — actually executes it.
4. When it hits `await something`, it suspends and gives control to the event loop.
5. When `something` completes, the event loop resumes the coroutine.

## 💻 Code Example
```python
import asyncio

async def fetch_user(user_id: int) -> dict:
    # Step 1: coroutine starts running
    print(f"Fetching user {user_id}...")

    # Step 2: hits await — SUSPENDS here, event loop can do other work
    await asyncio.sleep(0.5)  # simulates DB or HTTP call

    # Step 3: resumes when the await completes
    return {"id": user_id, "name": "Alice"}

async def main():
    # Creating a coroutine object — nothing runs yet
    coro = fetch_user(42)
    print(f"Type: {type(coro)}")  # <class 'coroutine'>

    # Now actually run it
    user = await coro
    print(f"Result: {user}")

asyncio.run(main())
```

## ⚠️ Common Mistakes
1. **Forgetting to await** — `result = fetch_user(42)` gives you a coroutine object, not the user. Python 3.10+ gives a clear warning, but the bug is silent in older code.
2. **Mixing sync and async** — calling a regular function with `await` (`await regular_func()`) raises a `TypeError`. Regular functions return values, not awaitables.
3. **Running coroutines outside an event loop** — if you call `asyncio.run()` inside an already-running loop (like in Jupyter), it raises a `RuntimeError`. Use `await` directly instead.

## ✅ When to Use vs When NOT to Use
**Use coroutines when:** Any function that does I/O — database access, HTTP requests, reading files, connecting to Redis.

**Don't wrap CPU work in async:** `async def compute():` with a heavy `for` loop still blocks the event loop. Use `asyncio.run_in_executor()` to move CPU work to a thread pool.

## 🔗 Related Concepts
- [051_async_await_basics](../051_async_await_basics) — the syntax fundamentals
- [053_asyncio_run](../053_asyncio_run) — how to start the event loop
- [054_asyncio_tasks](../054_asyncio_tasks) — concurrent coroutine execution
- [python_core/003_generators_yield](../../python_core/003_generators_yield) — generators, coroutines' cousin

## 🚀 Next Step
In `python-backend-mastery`: **Event loop internals** — how `asyncio` schedules coroutines, how the selector/proactor models work under the hood, and when to use `uvloop` for performance.

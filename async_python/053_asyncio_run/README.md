# asyncio.run() — The Entry Point to Async Python

## 🎯 Interview Question
"How do you actually run an async function in Python? What does `asyncio.run()` do?"

## 💡 Short Answer (30 seconds)
`asyncio.run()` is the standard entry point for async programs. It creates a new event loop, runs your top-level coroutine until it completes, then shuts down the loop and cleans up. You call it once at the top level — inside async code, you just use `await` instead.

## 🔬 Explanation
Every async program needs an **event loop** — the engine that schedules coroutines, handles I/O callbacks, and drives everything forward. `asyncio.run()` handles the event loop lifecycle for you:

1. Creates a new event loop
2. Runs the passed coroutine until it returns
3. Cancels remaining tasks and closes the loop

Before Python 3.7, you had to do this manually:
```python
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
```

`asyncio.run()` replaced all that boilerplate. Use it only at the **top level** of your program (like `if __name__ == "__main__":`). Never call it inside an already-running event loop — that raises a `RuntimeError`.

**In FastAPI/web frameworks:** You almost never call `asyncio.run()` yourself. The framework runs its own event loop. You just write `async def endpoint()` and `await` things inside it.

## 💻 Code Example
```python
import asyncio

async def fetch_data(url: str) -> dict:
    await asyncio.sleep(0.1)  # simulate HTTP call
    return {"url": url, "status": 200}

async def main():
    data = await fetch_data("https://api.example.com/users")
    print(data)

# This is the only place asyncio.run() belongs
if __name__ == "__main__":
    asyncio.run(main())
```

## ⚠️ Common Mistakes
1. **Calling `asyncio.run()` inside an async function** — raises `RuntimeError: This event loop is already running`. Inside async code, always use `await`.
2. **Calling `asyncio.run()` multiple times in a loop** — each call creates and destroys an event loop. It works but is wasteful. Use a single `asyncio.run(main())` that orchestrates everything.
3. **Using the old `loop.run_until_complete()` pattern** — still works but verbose. `asyncio.run()` is the modern, recommended way.

## ✅ When to Use vs When NOT to Use
**Use `asyncio.run()` when:** Writing a script or CLI tool with async code. It's the entry point for the event loop.

**Don't use it in:** FastAPI, aiohttp, or any async web framework — they manage their own event loop. Just `await` inside your route handlers.

## 🔗 Related Concepts
- [051_async_await_basics](../051_async_await_basics) — the syntax you write inside async functions
- [052_coroutines_explained](../052_coroutines_explained) — what asyncio.run() is actually running
- [054_asyncio_tasks](../054_asyncio_tasks) — what to do once your loop is running

## 🚀 Next Step
In `python-backend-mastery`: **Custom event loop policies** — using `uvloop` as a drop-in replacement for the default event loop to get 2-4x throughput improvement in production servers.

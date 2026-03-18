# Async HTTP Requests — Making Non-Blocking External Calls

## 🎯 Interview Question
"How do you make HTTP requests in async Python code? Why can't you use the `requests` library?"

## 💡 Short Answer (30 seconds)
The `requests` library is synchronous — it blocks the event loop while waiting for the response. In async code, use `httpx` (with `AsyncClient`) or `aiohttp` instead. They make non-blocking HTTP calls so other coroutines can run while you're waiting for the response.

## 🔬 Explanation
`requests.get("https://api.example.com/users")` blocks the entire thread — the event loop freezes until the HTTP response comes back. In a sync server, this is fine. In an async server (FastAPI, aiohttp), it kills concurrency.

**`httpx.AsyncClient`** is the modern choice:
- Drop-in replacement for `requests` with an async interface
- Session-based (reuses TCP connections — important for performance)
- Supports timeouts, retries, auth, streaming
- Works in both sync and async contexts

**`aiohttp`** is the older, battle-tested option:
- `aiohttp.ClientSession` — the session keeps a connection pool
- Slightly more verbose but very performant

**Key practice:** Always use a session, not one-off requests. Creating a new `AsyncClient` per request creates a new connection each time — slow and resource-wasteful. Create it once (via dependency injection or at startup) and reuse it.

## 💻 Code Example
```python
import asyncio
import httpx

async def fetch_user(client: httpx.AsyncClient, user_id: int) -> dict:
    response = await client.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()  # raises on 4xx/5xx
    return response.json()

async def main():
    # One client, one connection pool, many requests
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Fetch 3 users in parallel
        users = await asyncio.gather(
            fetch_user(client, 1),
            fetch_user(client, 2),
            fetch_user(client, 3),
        )
```

## ⚠️ Common Mistakes
1. **Using `requests` inside async code** — blocks the event loop. In a FastAPI app under load, one slow `requests.get()` call can make all concurrent requests slow down.
2. **Creating a new `AsyncClient` per request** — expensive. Each client creates a new connection pool. Share one client across the application lifetime.
3. **Not calling `raise_for_status()`** — a 404 or 500 response doesn't raise an exception by default. Always call it (or check `response.status_code`) to handle errors.

## ✅ When to Use vs When NOT to Use
**Use async HTTP clients when:** Your code runs inside an async server (FastAPI, aiohttp) and makes external API calls, webhook deliveries, or service-to-service communication.

**Sync `requests` is fine when:** Writing CLI tools, scripts, or sync Django views where async overhead isn't justified.

## 🔗 Related Concepts
- [055_asyncio_gather](../055_asyncio_gather) — making parallel HTTP calls
- [059_asyncio_timeout](../059_asyncio_timeout) — adding timeouts to HTTP calls
- [056_when_to_use_async](../056_when_to_use_async) — why async HTTP is I/O-bound work

## 🚀 Next Step
In `python-backend-mastery`: **Streaming responses with httpx** — iterating over large HTTP responses chunk by chunk, and **connection pool tuning** for high-throughput microservice architectures.

"""
Demo: Async HTTP Requests — Making Non-Blocking External Calls
Level: Intermediate (2–3 years experience)
Run:  python demo.py

Note: This demo uses httpx with a mock server (no real HTTP calls).
      In production, replace mock_server with real URLs.
"""

import asyncio
import time
from unittest.mock import AsyncMock, patch


# ── Setup: Mock async HTTP client for demo (no real network needed) ───────────

class MockResponse:
    """Simulates an httpx Response object."""

    def __init__(self, data: dict, status_code: int = 200, delay: float = 0.1):
        self._data = data
        self.status_code = status_code
        self._delay = delay

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code} error")

    def json(self) -> dict:
        return self._data


class MockAsyncClient:
    """Simulates httpx.AsyncClient."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def get(self, url: str, **kwargs) -> MockResponse:
        # Simulate different response times for different endpoints
        if "users" in url:
            await asyncio.sleep(0.15)
            user_id = url.split("/")[-1]
            return MockResponse({"id": int(user_id), "name": f"User {user_id}"})
        elif "posts" in url:
            await asyncio.sleep(0.2)
            return MockResponse([{"title": "Post 1"}, {"title": "Post 2"}])
        elif "slow" in url:
            await asyncio.sleep(2.0)  # simulates a slow API
            return MockResponse({"result": "finally"})
        elif "error" in url:
            return MockResponse({}, status_code=404)
        return MockResponse({})

    async def post(self, url: str, json: dict = None, **kwargs) -> MockResponse:
        await asyncio.sleep(0.1)
        return MockResponse({"created": True, "data": json})


# Replace httpx.AsyncClient with our mock for the demo
AsyncClient = MockAsyncClient


# ── Section 1: Basic async HTTP GET ──────────────────────────────────────────

async def fetch_user(client, user_id: int) -> dict:
    response = await client.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()  # raises if 4xx or 5xx
    return response.json()


async def demo_basic_get():
    print("[Section 1] Basic async HTTP GET")

    async with AsyncClient() as client:
        user = await fetch_user(client, 42)
        print(f"  Fetched: {user}")


# ── Section 2: Parallel requests with gather ─────────────────────────────────

async def demo_parallel_requests():
    print("\n[Section 2] Parallel HTTP calls with asyncio.gather")
    start = time.perf_counter()

    async with AsyncClient() as client:
        # All 3 requests fire at the same time — total ≈ slowest (0.2s)
        users = await asyncio.gather(
            fetch_user(client, 1),
            fetch_user(client, 2),
            fetch_user(client, 3),
        )

    elapsed = time.perf_counter() - start
    print(f"  Fetched {len(users)} users in {elapsed:.2f}s")
    print(f"  (Sequential would be ~0.45s — parallel is ~0.15s)")
    for user in users:
        print(f"    {user}")


# ── Section 3: POST request ───────────────────────────────────────────────────

async def create_user(client, data: dict) -> dict:
    response = await client.post(
        "https://api.example.com/users",
        json=data,
    )
    response.raise_for_status()
    return response.json()


async def demo_post_request():
    print("\n[Section 3] Async HTTP POST")

    async with AsyncClient() as client:
        result = await create_user(client, {"name": "Alice", "email": "alice@example.com"})
        print(f"  Created: {result}")


# ── Section 4: Error handling ─────────────────────────────────────────────────

async def demo_error_handling():
    print("\n[Section 4] Handling HTTP errors properly")

    async with AsyncClient() as client:
        # Endpoint that returns 404
        response = await client.get("https://api.example.com/error/user")

        print(f"  Response status: {response.status_code}")

        try:
            response.raise_for_status()  # raises on 4xx/5xx
        except Exception as e:
            print(f"  Error caught: {e}")
            print(f"  (Return a user-friendly error, don't let 500 propagate)")


# ── Section 5: Timeout on HTTP calls ─────────────────────────────────────────

async def demo_timeout():
    print("\n[Section 5] Adding timeout to async HTTP calls")

    async with AsyncClient() as client:
        try:
            result = await asyncio.wait_for(
                client.get("https://api.example.com/slow/endpoint"),
                timeout=0.3,  # give it 300ms max
            )
        except asyncio.TimeoutError:
            print("  External API timed out — returning error to caller")
            print("  (In FastAPI: raise HTTPException(status_code=503))")


# ── Section 6: The 'requests' mistake ────────────────────────────────────────

def demo_requests_mistake():
    print("\n[Section 6] Common mistake: using 'requests' in async code")

    print("  WRONG — blocks the event loop:")
    print("    import requests")
    print("    async def get_user(user_id):")
    print("        response = requests.get(f'/users/{user_id}')  # BLOCKS!")
    print("        return response.json()")

    print("\n  RIGHT — non-blocking:")
    print("    import httpx")
    print("    async def get_user(client: httpx.AsyncClient, user_id):")
    print("        response = await client.get(f'/users/{user_id}')")
    print("        response.raise_for_status()")
    print("        return response.json()")

    print("\n  Also wrong — creating client per request:")
    print("    async def get_user(user_id):  # wasteful!")
    print("        async with httpx.AsyncClient() as client:  # new pool each time!")
    print("            return await client.get(f'/users/{user_id}')")

    print("\n  RIGHT — share one client (e.g., via FastAPI Depends):")
    print("    # Create once at startup, inject into each handler")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Async HTTP Requests with httpx")
    print("=" * 55)

    asyncio.run(demo_basic_get())
    asyncio.run(demo_parallel_requests())
    asyncio.run(demo_post_request())
    asyncio.run(demo_error_handling())
    asyncio.run(demo_timeout())
    demo_requests_mistake()

    print("\n" + "=" * 55)
    print("Key takeaways:")
    print("  1. Use httpx.AsyncClient (or aiohttp) — not 'requests'")
    print("  2. Create ONE client, share it — don't create per request")
    print("  3. Always call raise_for_status() to catch HTTP errors")
    print("  4. Use asyncio.gather() + one client for parallel API calls")

"""
Demo: Async Context Managers — `async with` for Resource Management
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import asyncio
from contextlib import asynccontextmanager


# ── Section 1: Building an async context manager with a class ─────────────────

class AsyncDatabaseSession:
    """
    Simulates an async DB session (like SQLAlchemy AsyncSession).
    Uses __aenter__ / __aexit__ — the async equivalents of __enter__ / __exit__.
    """

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.is_open = False

    async def __aenter__(self):
        # This async setup is why we need 'async with' instead of 'with'
        await asyncio.sleep(0.05)  # simulates connection handshake
        self.is_open = True
        print(f"  [DB] Connected to {self.db_url}")
        return self  # what gets assigned to 'as session'

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Always runs — even if an exception occurred inside the block
        await asyncio.sleep(0.02)  # simulates graceful close
        self.is_open = False
        if exc_type:
            print(f"  [DB] Closing connection (exception: {exc_val})")
        else:
            print(f"  [DB] Connection closed cleanly")
        return False  # don't suppress exceptions

    async def execute(self, query: str) -> list:
        await asyncio.sleep(0.05)  # simulates query time
        return [{"result": f"row from: {query}"}]


async def demo_class_based():
    print("[Section 1] Class-based async context manager")

    async with AsyncDatabaseSession("postgresql://localhost/mydb") as session:
        print(f"  Session open: {session.is_open}")
        results = await session.execute("SELECT * FROM users LIMIT 1")
        print(f"  Query result: {results}")

    print(f"  Session open after block: {session.is_open}")


# ── Section 2: asynccontextmanager decorator (simpler) ───────────────────────

@asynccontextmanager
async def http_client_session(base_url: str):
    """
    Simulates aiohttp.ClientSession or httpx.AsyncClient.
    The @asynccontextmanager decorator is the clean, concise way.
    """
    print(f"  [HTTP] Opening session for {base_url}")
    session = {"base_url": base_url, "active": True}
    try:
        yield session  # code inside 'async with' runs here
    finally:
        # Cleanup always runs — even on exception
        session["active"] = False
        print(f"  [HTTP] Session closed")


async def demo_decorator_based():
    print("\n[Section 2] @asynccontextmanager decorator")

    async with http_client_session("https://api.example.com") as client:
        print(f"  Client active: {client['active']}")
        # In real code: response = await client.get("/users")
        await asyncio.sleep(0.05)  # simulates HTTP call
        print(f"  Made HTTP request via {client['base_url']}")

    print(f"  Client active after block: {client['active']}")


# ── Section 3: Exception safety — cleanup always runs ────────────────────────

async def demo_exception_safety():
    print("\n[Section 3] Cleanup runs even when exceptions occur")

    try:
        async with AsyncDatabaseSession("postgresql://localhost/mydb") as session:
            print(f"  Session open: {session.is_open}")
            raise ValueError("Something went wrong in business logic!")
    except ValueError as e:
        print(f"  Caught exception: {e}")
        print(f"  Session was cleaned up automatically")


# ── Section 4: asyncio.Lock — built-in async context manager ──────────────────

async def demo_async_lock():
    print("\n[Section 4] asyncio.Lock — preventing race conditions")

    lock = asyncio.Lock()
    shared_counter = {"value": 0}

    async def increment(task_id: int):
        # Without the lock, concurrent tasks would have race conditions
        async with lock:  # only one task can be here at a time
            current = shared_counter["value"]
            await asyncio.sleep(0.01)  # simulates read-modify-write delay
            shared_counter["value"] = current + 1

    # Run 5 tasks concurrently — lock prevents data corruption
    await asyncio.gather(*[increment(i) for i in range(5)])
    print(f"  Final counter: {shared_counter['value']} (expected: 5)")


# ── Section 5: The common mistake — using 'with' instead of 'async with' ──────

def demo_wrong_usage():
    print("\n[Section 5] Common mistake: 'with' on an async context manager")

    print("  WRONG:")
    print("    with AsyncDatabaseSession('db_url') as session:")
    print("        # TypeError: 'AsyncDatabaseSession' object does not support")
    print("        # the context manager protocol (no __enter__)")

    print("\n  RIGHT:")
    print("    async with AsyncDatabaseSession('db_url') as session:")
    print("        await session.execute('SELECT ...')")

    print("\n  Also wrong: using async with outside an async function")
    print("    def sync_function():")
    print("        async with resource as r:  # SyntaxError!")
    print("            pass")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Async Context Managers")
    print("=" * 55)

    asyncio.run(demo_class_based())
    asyncio.run(demo_decorator_based())
    asyncio.run(demo_exception_safety())
    asyncio.run(demo_async_lock())
    demo_wrong_usage()

    print("\n" + "=" * 55)
    print("Key takeaways:")
    print("  1. async with = context manager where setup/teardown needs await")
    print("  2. Implement __aenter__ / __aexit__ or use @asynccontextmanager")
    print("  3. Cleanup in __aexit__ / finally ALWAYS runs, even on exception")
    print("  4. asyncio.Lock uses async with to prevent race conditions")

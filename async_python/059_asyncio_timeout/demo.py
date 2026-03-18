"""
Demo: asyncio Timeouts — Cancelling Slow Operations
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import asyncio
import sys


# ── Section 1: asyncio.wait_for() — the fundamental timeout ──────────────────

async def fast_api_call() -> dict:
    await asyncio.sleep(0.1)  # responds in 100ms
    return {"status": "ok", "data": "user info"}


async def slow_api_call() -> dict:
    await asyncio.sleep(5.0)  # responds in 5 seconds (too slow)
    return {"status": "ok"}


async def demo_wait_for_success():
    print("[Section 1a] wait_for — fast operation completes within timeout")
    result = await asyncio.wait_for(fast_api_call(), timeout=2.0)
    print(f"  Result: {result}")


async def demo_wait_for_timeout():
    print("\n[Section 1b] wait_for — slow operation exceeds timeout")
    try:
        result = await asyncio.wait_for(slow_api_call(), timeout=0.3)
    except asyncio.TimeoutError:
        print("  asyncio.TimeoutError raised — operation was cancelled")
        print("  (The coroutine was automatically cancelled by wait_for)")


# ── Section 2: Cleanup with CancelledError ────────────────────────────────────

async def db_write_with_cleanup(data: str) -> str:
    """
    Simulates a DB write that might be cancelled.
    Always do cleanup in finally — it runs even when cancelled.
    """
    try:
        print(f"  [db_write] Starting write: {data!r}")
        await asyncio.sleep(2.0)  # will be cancelled
        return "written"
    except asyncio.CancelledError:
        print(f"  [db_write] Cancelled — rolling back transaction")
        raise  # ALWAYS re-raise CancelledError
    finally:
        print(f"  [db_write] Connection released (finally always runs)")


async def demo_cleanup_on_cancel():
    print("\n[Section 2] Cleanup when a timeout cancels your coroutine")
    try:
        await asyncio.wait_for(db_write_with_cleanup("user data"), timeout=0.1)
    except asyncio.TimeoutError:
        print("  Timeout caught — error returned to caller")


# ── Section 3: Timeout on gather — parallel operations with deadline ──────────

async def fetch_service(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name} data"


async def demo_timeout_with_gather():
    print("\n[Section 3] Timeout wrapping a gather() call")

    try:
        # All 3 calls must complete within 0.25 seconds total
        results = await asyncio.wait_for(
            asyncio.gather(
                fetch_service("user-service", 0.1),
                fetch_service("order-service", 0.3),  # this one is too slow
                fetch_service("inventory-service", 0.1),
            ),
            timeout=0.25,
        )
        print(f"  Results: {results}")
    except asyncio.TimeoutError:
        print("  One service took too long — all operations cancelled")
        print("  (In production: return partial data or a 503 error)")


# ── Section 4: Python 3.11+ asyncio.timeout() context manager ─────────────────

async def demo_timeout_context_manager():
    print("\n[Section 4] Python 3.11+ asyncio.timeout() — context manager style")

    # Only show this if Python >= 3.11
    if sys.version_info >= (3, 11):
        try:
            async with asyncio.timeout(0.2):
                await asyncio.sleep(0.1)  # fast enough
                print("  First call: succeeded within timeout")

            async with asyncio.timeout(0.05):
                await asyncio.sleep(0.2)  # too slow
        except TimeoutError:  # built-in TimeoutError in 3.11+
            print("  Second call: TimeoutError raised (built-in, not asyncio.TimeoutError)")
    else:
        print(f"  Python {sys.version_info.major}.{sys.version_info.minor} detected")
        print("  asyncio.timeout() requires Python 3.11+ — using wait_for() instead")
        try:
            async with asyncio.timeout_at(asyncio.get_event_loop().time() + 0.05):
                await asyncio.sleep(0.2)
        except (TimeoutError, AttributeError):
            print("  Timeout via wait_for equivalent")


# ── Section 5: The common mistake — not catching TimeoutError ────────────────

async def demo_uncaught_timeout_mistake():
    print("\n[Section 5] Common mistake: not catching TimeoutError")

    print("  WRONG: no try/except around wait_for()")
    print("    result = await asyncio.wait_for(slow_call(), timeout=1.0)")
    print("    # If timeout fires: asyncio.TimeoutError propagates to caller")
    print("    # In FastAPI: becomes a 500 Internal Server Error")

    print("\n  RIGHT: always catch and return a meaningful response")
    print("    try:")
    print("        result = await asyncio.wait_for(slow_call(), timeout=1.0)")
    print("    except asyncio.TimeoutError:")
    print("        raise HTTPException(503, 'Service temporarily unavailable')")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: asyncio Timeouts")
    print("=" * 55)

    asyncio.run(demo_wait_for_success())
    asyncio.run(demo_wait_for_timeout())
    asyncio.run(demo_cleanup_on_cancel())
    asyncio.run(demo_timeout_with_gather())
    asyncio.run(demo_timeout_context_manager())
    asyncio.run(demo_uncaught_timeout_mistake())

    print("\n" + "=" * 55)
    print("Key takeaways:")
    print("  1. asyncio.wait_for(coro, timeout=N) — adds a deadline")
    print("  2. TimeoutError is raised AND the coroutine is cancelled")
    print("  3. Use try/finally for cleanup when cancellation may happen")
    print("  4. ALWAYS catch TimeoutError — don't let it become a 500")

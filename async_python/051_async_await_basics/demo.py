"""
Demo: async/await Basics — Writing Non-Blocking Code
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import asyncio
import time


# ── Section 1: The problem async solves ──────────────────────────────────────

def slow_sync_task(name: str, seconds: float) -> str:
    """Simulates a blocking I/O call (like a slow DB query)."""
    time.sleep(seconds)
    return f"{name} done"


async def slow_async_task(name: str, seconds: float) -> str:
    """Same concept, but non-blocking — releases the event loop while waiting."""
    await asyncio.sleep(seconds)
    return f"{name} done"


# ── Section 2: async def doesn't run immediately ──────────────────────────────

async def demo_coroutine_is_lazy():
    print("\n[Section 2] Coroutines are lazy — calling doesn't run them")

    # WRONG: this returns a coroutine object, not the result
    coro = slow_async_task("task", 0.1)
    print(f"  Before await: {coro}")   # <coroutine object ...>

    # RIGHT: you must await to actually execute it
    result = await slow_async_task("task", 0.1)
    print(f"  After await:  {result}")  # "task done"

    # Clean up the unawaited coroutine (suppress RuntimeWarning in demo)
    coro.close()


# ── Section 3: await suspends, not blocks ────────────────────────────────────

async def task_a():
    print("  Task A: starting (will wait 0.3s)")
    await asyncio.sleep(0.3)
    print("  Task A: finished")
    return "A"


async def task_b():
    print("  Task B: starting (will wait 0.1s)")
    await asyncio.sleep(0.1)
    print("  Task B: finished")
    return "B"


async def demo_sequential():
    """Running tasks one after the other — still better than sync for I/O."""
    print("\n[Section 3a] Sequential async (still non-blocking, just ordered)")
    start = time.perf_counter()

    result_a = await task_a()  # waits for A to finish before starting B
    result_b = await task_b()

    elapsed = time.perf_counter() - start
    print(f"  Results: {result_a}, {result_b}")
    print(f"  Time: {elapsed:.2f}s (sequential: 0.3 + 0.1 = ~0.4s)")


# ── Section 4: The common mistake — time.sleep() in async code ───────────────

async def demo_blocking_mistake():
    print("\n[Section 4] Common mistake: time.sleep() blocks the event loop")

    print("  WRONG approach (don't do this):")
    print("    async def fetch():")
    print("        time.sleep(1)  # This FREEZES the event loop!")
    print("        return data")

    print("\n  RIGHT approach:")
    print("    async def fetch():")
    print("        await asyncio.sleep(1)  # Event loop free during wait")
    print("        return data")

    # Demonstrate correct approach
    start = time.perf_counter()
    await asyncio.sleep(0.1)
    elapsed = time.perf_counter() - start
    print(f"\n  await asyncio.sleep(0.1) completed in {elapsed:.3f}s ✓")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: async/await Basics")
    print("=" * 55)

    asyncio.run(demo_coroutine_is_lazy())
    asyncio.run(demo_sequential())
    asyncio.run(demo_blocking_mistake())

    print("\n" + "=" * 55)
    print("Key takeaways:")
    print("  1. async def creates a coroutine — must be awaited to run")
    print("  2. await suspends (not blocks) the current coroutine")
    print("  3. Use asyncio.sleep(), NOT time.sleep() in async code")
    print("  4. Async helps I/O-bound work, not CPU-bound work")

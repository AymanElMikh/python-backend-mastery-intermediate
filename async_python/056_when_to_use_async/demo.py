"""
Demo: When to Use Async — I/O-Bound vs CPU-Bound
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor


# ── Section 1: I/O-bound — async helps ────────────────────────────────────────

async def io_task(label: str, delay: float) -> str:
    """Simulates an I/O-bound operation (DB query, HTTP call, etc.)."""
    await asyncio.sleep(delay)  # CPU is free during this wait
    return f"{label} done"


async def demo_io_bound():
    """Running 5 I/O tasks concurrently — total ≈ longest single task."""
    start = time.perf_counter()

    # 5 tasks each "waiting" 0.2s — total ≈ 0.2s (not 1.0s)
    results = await asyncio.gather(
        io_task("DB query 1", 0.2),
        io_task("HTTP call", 0.15),
        io_task("Redis get", 0.05),
        io_task("DB query 2", 0.2),
        io_task("File read", 0.1),
    )

    elapsed = time.perf_counter() - start
    print(f"  {len(results)} I/O tasks completed in {elapsed:.2f}s")
    print(f"  (Sequential would take ~0.7s — async saved ~{0.7 - elapsed:.2f}s)")


# ── Section 2: CPU-bound — async does NOT help ─────────────────────────────────

def cpu_work(n: int) -> int:
    """CPU-bound: keeps the processor busy the entire time."""
    return sum(i * i for i in range(n))


async def bad_cpu_in_async(n: int) -> int:
    """
    WRONG: CPU work inside async def.
    The event loop is BLOCKED while this computes.
    Other coroutines cannot run during this time.
    """
    return cpu_work(n)  # no await — blocks the event loop


async def demo_cpu_blocks_event_loop():
    print("\n[Section 2] CPU work blocks the event loop")

    # Start a background task that should print every 0.05s
    results = []

    async def background_ticker():
        for i in range(5):
            await asyncio.sleep(0.05)
            results.append(f"tick {i}")

    ticker = asyncio.create_task(background_ticker())

    # Do CPU work WITHOUT yielding — ticker gets blocked
    start = time.perf_counter()
    _ = await bad_cpu_in_async(3_000_000)
    elapsed = time.perf_counter() - start

    await ticker
    print(f"  CPU task took {elapsed:.2f}s")
    print(f"  Background ticker got {len(results)} ticks")
    print(f"  (Ideally 5 ticks, but CPU blocked the event loop)")


# ── Section 3: Right way to handle CPU work — run_in_executor ─────────────────

async def demo_cpu_in_executor():
    print("\n[Section 3] RIGHT way: offload CPU work to a thread")

    loop = asyncio.get_event_loop()

    async def background_ticker():
        ticks = []
        for i in range(5):
            await asyncio.sleep(0.05)
            ticks.append(f"tick {i}")
        return ticks

    # Start background ticker
    ticker_task = asyncio.create_task(background_ticker())

    # Run CPU work in a thread pool — event loop stays free
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpu_work, 3_000_000)

    ticks = await ticker_task
    print(f"  CPU result: {result}")
    print(f"  Background ticker completed: {len(ticks)} ticks ✓")
    print(f"  (Event loop was free while CPU worked in thread)")


# ── Section 4: The "async for everything" mistake ─────────────────────────────

def demo_async_vs_sync_choice():
    print("\n[Section 4] When NOT to use async — pure sync functions")

    print("  WRONG: adding async to a function that never awaits anything")
    print("    async def compute_tax(amount: float) -> float:")
    print("        return amount * 0.2   # pure computation, no I/O")
    print("    # Now every caller must await it — for no benefit")

    print("\n  RIGHT: keep sync functions sync")
    print("    def compute_tax(amount: float) -> float:")
    print("        return amount * 0.2   # call directly, no await needed")

    print("\n  Rule: only use async def if the function contains 'await'")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: When to Use Async — I/O-Bound vs CPU-Bound")
    print("=" * 55)

    print("\n[Section 1] I/O-bound tasks — async excels here")
    asyncio.run(demo_io_bound())

    asyncio.run(demo_cpu_blocks_event_loop())
    asyncio.run(demo_cpu_in_executor())
    demo_async_vs_sync_choice()

    print("\n" + "=" * 55)
    print("Key takeaways:")
    print("  ✅ I/O-bound (DB, HTTP, files) → use async/await")
    print("  ❌ CPU-bound (compute, math)   → use multiprocessing/Celery")
    print("  ⚠️  CPU in async def blocks the event loop")
    print("  🔧 Use run_in_executor() to bridge CPU work into async code")

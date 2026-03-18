"""
Demo: asyncio Tasks — Running Coroutines Concurrently
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import asyncio
import time


# ── Section 1: Sequential vs Concurrent — the timing difference ───────────────

async def fetch_profile(user_id: int) -> dict:
    await asyncio.sleep(0.3)  # simulates a DB query taking 300ms
    return {"id": user_id, "name": "Alice"}


async def fetch_orders(user_id: int) -> list:
    await asyncio.sleep(0.2)  # simulates another DB query taking 200ms
    return [{"item": "laptop"}, {"item": "mouse"}]


async def demo_sequential():
    """Sequential: total time = 0.3 + 0.2 = 0.5s"""
    start = time.perf_counter()

    profile = await fetch_profile(1)   # wait 300ms
    orders = await fetch_orders(1)     # then wait 200ms

    elapsed = time.perf_counter() - start
    print(f"  Sequential:  {elapsed:.2f}s (0.3 + 0.2 = ~0.5s expected)")
    return profile, orders


async def demo_concurrent_tasks():
    """Concurrent with tasks: total time = max(0.3, 0.2) = 0.3s"""
    start = time.perf_counter()

    # Both tasks are scheduled immediately — they run at the same time
    profile_task = asyncio.create_task(fetch_profile(1))
    orders_task = asyncio.create_task(fetch_orders(1))

    # Now await both — profile takes longer so it determines total time
    profile = await profile_task
    orders = await orders_task

    elapsed = time.perf_counter() - start
    print(f"  Concurrent:  {elapsed:.2f}s (max(0.3, 0.2) = ~0.3s expected)")
    return profile, orders


# ── Section 2: Task object and its state ─────────────────────────────────────

async def demo_task_object():
    print("\n[Section 2] Task object properties")

    async def slow_job() -> str:
        await asyncio.sleep(0.1)
        return "job complete"

    task = asyncio.create_task(slow_job())
    print(f"  Just created — done? {task.done()}")

    await asyncio.sleep(0)   # yield control so the task can start
    print(f"  After yield   — done? {task.done()}")

    result = await task
    print(f"  After await   — done? {task.done()}, result: {result!r}")


# ── Section 3: Cancelling a task ─────────────────────────────────────────────

async def long_running_job() -> str:
    try:
        print("  [job] Starting long work...")
        await asyncio.sleep(10)  # this will be cancelled
        return "finished"
    except asyncio.CancelledError:
        print("  [job] Received cancellation — cleaning up")
        raise  # important: always re-raise CancelledError


async def demo_cancel_task():
    print("\n[Section 3] Cancelling a task")

    task = asyncio.create_task(long_running_job())
    await asyncio.sleep(0.05)  # let the task start

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print(f"  Task was cancelled. done={task.done()}, cancelled={task.cancelled()}")


# ── Section 4: The common mistake — not awaiting a task ──────────────────────

async def demo_unawaited_task_mistake():
    print("\n[Section 4] Common mistake: creating tasks but not awaiting them")

    async def important_job():
        await asyncio.sleep(0.05)
        print("  [important_job] Completed!")
        return "important result"

    print("  WRONG: creating a task and ignoring it")
    print("    task = asyncio.create_task(important_job())")
    print("    # Never awaited — result is lost, exceptions are silently dropped")

    print("\n  RIGHT: always await your tasks")
    task = asyncio.create_task(important_job())
    result = await task
    print(f"    result = await task  →  {result!r}")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: asyncio Tasks")
    print("=" * 55)

    print("\n[Section 1] Sequential vs Concurrent")
    asyncio.run(demo_sequential())
    asyncio.run(demo_concurrent_tasks())

    asyncio.run(demo_task_object())
    asyncio.run(demo_cancel_task())
    asyncio.run(demo_unawaited_task_mistake())

    print("\n" + "=" * 55)
    print("Key takeaways:")
    print("  1. await coroutine() = sequential (one at a time)")
    print("  2. create_task() = concurrent (overlap I/O operations)")
    print("  3. Always await your tasks — don't fire-and-forget")
    print("  4. Tasks can be cancelled with task.cancel()")

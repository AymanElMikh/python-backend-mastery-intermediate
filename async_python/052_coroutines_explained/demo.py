"""
Demo: Coroutines Explained — What They Are and How They Work
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import asyncio
import inspect


# ── Section 1: Coroutine vs regular function ──────────────────────────────────

def regular_function(x: int) -> int:
    """Plain function — runs to completion, returns immediately."""
    return x * 2


async def async_function(x: int) -> int:
    """Coroutine — can pause, needs to be awaited."""
    await asyncio.sleep(0)  # yield control once, then continue
    return x * 2


def demo_coroutine_type():
    print("[Section 1] Coroutine vs regular function")

    # Regular function: call it → get result immediately
    result = regular_function(5)
    print(f"  regular_function(5) = {result}")
    print(f"  Type returned: {type(result)}")  # int

    # Coroutine function: calling it creates a coroutine OBJECT, doesn't run
    coro = async_function(5)
    print(f"\n  async_function(5) = {coro}")
    print(f"  Type returned: {type(coro)}")  # coroutine

    # Is it a coroutine? Python has a built-in check
    print(f"  inspect.iscoroutine(coro): {inspect.iscoroutine(coro)}")

    # Must close it to prevent "was never awaited" warning
    coro.close()


# ── Section 2: The coroutine lifecycle ───────────────────────────────────────

async def lifecycle_demo():
    print("\n[Section 2] Coroutine lifecycle")

    async def step_by_step():
        print("  → Step 1: coroutine starts")
        await asyncio.sleep(0.05)  # SUSPEND here
        print("  → Step 2: coroutine resumes after await")
        await asyncio.sleep(0.05)  # SUSPEND again
        print("  → Step 3: coroutine finishes")
        return "done"

    print("  Creating coroutine object (not running yet)...")
    coro = step_by_step()
    print(f"  State: {inspect.getcoroutinestate(coro)}")  # CREATED

    print("  Awaiting it now...")
    result = await coro
    print(f"  Result: {result}")


# ── Section 3: What happens at each await ────────────────────────────────────

async def task_one():
    print("  [task_one] Starting")
    await asyncio.sleep(0.1)   # suspends — event loop runs task_two
    print("  [task_one] Resumed and finishing")
    return "one"


async def task_two():
    print("  [task_two] Starting")
    await asyncio.sleep(0.05)  # suspends — event loop resumes task_one
    print("  [task_two] Resumed and finishing")
    return "two"


async def demo_interleaving():
    print("\n[Section 3] How coroutines interleave at await points")
    print("  (Running task_one and task_two as concurrent tasks)")

    # asyncio.gather runs both concurrently — see 055_asyncio_gather for details
    results = await asyncio.gather(task_one(), task_two())
    print(f"  Both done: {results}")
    print("  Notice: task_two finished before task_one (shorter sleep)")


# ── Section 4: The common mistake — calling without awaiting ─────────────────

async def demo_unawaited_mistake():
    print("\n[Section 4] Common mistake: not awaiting a coroutine")

    async def get_data() -> str:
        await asyncio.sleep(0)
        return "real data"

    # WRONG: result is a coroutine object, not a string
    wrong_result = get_data()
    print(f"  WRONG:  result = get_data()  →  {wrong_result}")
    wrong_result.close()  # clean up

    # RIGHT: await it
    right_result = await get_data()
    print(f"  RIGHT:  result = await get_data()  →  {right_result!r}")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Coroutines Explained")
    print("=" * 55)

    demo_coroutine_type()
    asyncio.run(lifecycle_demo())
    asyncio.run(demo_interleaving())
    asyncio.run(demo_unawaited_mistake())

    print("\n" + "=" * 55)
    print("Key takeaways:")
    print("  1. async def creates a coroutine function")
    print("  2. Calling it returns a coroutine OBJECT (not the result)")
    print("  3. await both runs and suspends the coroutine at I/O points")
    print("  4. The event loop decides what runs while a coroutine waits")

"""
Demo: asyncio.run() — The Entry Point to Async Python
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import asyncio


# ── Section 1: Basic asyncio.run() usage ─────────────────────────────────────

async def greet(name: str) -> str:
    await asyncio.sleep(0.05)  # simulates async work
    return f"Hello, {name}!"


async def main_simple():
    result = await greet("Alice")
    print(f"  {result}")


# ── Section 2: asyncio.run() lifecycle ───────────────────────────────────────

async def main_lifecycle():
    print("  [1] Inside event loop — running")

    await asyncio.sleep(0.05)

    print("  [2] After await — still inside event loop")
    return "finished"


# ── Section 3: What asyncio.run() manages for you ────────────────────────────

async def task_with_cleanup():
    """Simulates a task that asyncio.run() will clean up if needed."""
    try:
        await asyncio.sleep(10)  # long-running task
    except asyncio.CancelledError:
        print("  Task was cancelled during cleanup — handled gracefully")
        raise  # always re-raise CancelledError


async def main_with_background_task():
    # Start a background task
    task = asyncio.create_task(task_with_cleanup())

    # Do some work
    await asyncio.sleep(0.05)
    print("  Main work done — returning (background task will be cancelled)")

    # Cancel the task before returning
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass  # expected


# ── Section 4: The common mistake — calling run() inside async code ───────────

def demo_wrong_usage():
    print("\n[Section 4] Common mistake: asyncio.run() inside async context")

    print("  WRONG — do NOT do this inside an async function:")
    print("    async def my_handler():          # e.g. FastAPI route")
    print("        result = asyncio.run(fetch())  # RuntimeError!")
    print("        # RuntimeError: This event loop is already running")

    print("\n  RIGHT — just use await inside async functions:")
    print("    async def my_handler():")
    print("        result = await fetch()  # correct!")

    print("\n  RIGHT — use asyncio.run() only at the script entry point:")
    print("    if __name__ == '__main__':")
    print("        asyncio.run(main())")


# ── Section 5: Running multiple top-level coroutines ─────────────────────────

async def step_a() -> str:
    await asyncio.sleep(0.03)
    return "step_a result"


async def step_b(input_value: str) -> str:
    await asyncio.sleep(0.02)
    return f"step_b processed: {input_value}"


async def main_orchestrated():
    """
    The top-level 'main' coroutine orchestrates everything.
    asyncio.run() is called once — main() sequences all work.
    """
    a = await step_a()
    b = await step_b(a)
    print(f"  Final: {b}")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: asyncio.run()")
    print("=" * 55)

    print("\n[Section 1] Basic usage")
    asyncio.run(main_simple())

    print("\n[Section 2] Lifecycle")
    result = asyncio.run(main_lifecycle())
    print(f"  asyncio.run() returned: {result!r}")
    print("  Event loop is now closed")

    print("\n[Section 3] Cleanup of background tasks")
    asyncio.run(main_with_background_task())

    demo_wrong_usage()

    print("\n[Section 5] Orchestrating multiple steps in one run()")
    asyncio.run(main_orchestrated())

    print("\n" + "=" * 55)
    print("Key takeaways:")
    print("  1. asyncio.run() = create loop + run coroutine + close loop")
    print("  2. Call it ONCE at the script top level")
    print("  3. Inside async code, always use 'await', never asyncio.run()")
    print("  4. It handles cleanup of pending tasks automatically")

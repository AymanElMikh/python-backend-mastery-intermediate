"""
Demo: asyncio.gather() — Running Multiple Coroutines and Collecting Results
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import asyncio
import time


# ── Section 1: gather() vs manual task creation ───────────────────────────────

async def fetch_user(user_id: int) -> dict:
    await asyncio.sleep(0.2)
    return {"id": user_id, "name": f"User {user_id}"}


async def fetch_posts(user_id: int) -> list:
    await asyncio.sleep(0.3)
    return [f"Post {i}" for i in range(1, 4)]


async def fetch_followers(user_id: int) -> int:
    await asyncio.sleep(0.15)
    return 1042


async def demo_gather_basic():
    """gather() is the clean way to fan out and collect results."""
    start = time.perf_counter()

    # All three run concurrently — results come back in INPUT ORDER
    user, posts, followers = await asyncio.gather(
        fetch_user(42),
        fetch_posts(42),
        fetch_followers(42),
    )

    elapsed = time.perf_counter() - start
    print(f"  user:      {user}")
    print(f"  posts:     {posts}")
    print(f"  followers: {followers}")
    print(f"  Time: {elapsed:.2f}s  (max of 0.2, 0.3, 0.15 = ~0.3s expected)")


# ── Section 2: Results are always in input order ──────────────────────────────

async def slow_task(label: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{label} (took {delay}s)"


async def demo_result_ordering():
    print("\n[Section 2] Results are in INPUT order, not completion order")

    results = await asyncio.gather(
        slow_task("A", 0.3),   # slowest
        slow_task("B", 0.05),  # fastest — finishes first
        slow_task("C", 0.15),  # middle
    )

    print("  Completion order: B, C, A")
    print(f"  Results order:    {results}")
    print("  → gather() always preserves input order")


# ── Section 3: return_exceptions=True for resilient parallel calls ─────────────

async def risky_task(label: str, should_fail: bool) -> str:
    await asyncio.sleep(0.1)
    if should_fail:
        raise ValueError(f"{label} failed!")
    return f"{label} succeeded"


async def demo_return_exceptions():
    print("\n[Section 3] Handling partial failures with return_exceptions=True")

    # With return_exceptions=True, exceptions are returned as values
    results = await asyncio.gather(
        risky_task("A", should_fail=False),
        risky_task("B", should_fail=True),   # this one fails
        risky_task("C", should_fail=False),
        return_exceptions=True,
    )

    for label, result in zip(["A", "B", "C"], results):
        if isinstance(result, Exception):
            print(f"  Task {label}: FAILED — {result}")
        else:
            print(f"  Task {label}: OK    — {result}")


# ── Section 4: Default behavior (no return_exceptions) ───────────────────────

async def demo_exception_propagation():
    print("\n[Section 4] Default behavior: first exception is raised")
    print("  (return_exceptions=False by default)")

    try:
        results = await asyncio.gather(
            risky_task("A", should_fail=False),
            risky_task("B", should_fail=True),  # causes gather() to raise
            risky_task("C", should_fail=False),
        )
    except ValueError as e:
        print(f"  gather() raised: {e}")
        print("  Tasks A and C were abandoned (their results discarded)")


# ── Section 5: Common mistake — using gather() for dependent work ─────────────

async def demo_gather_mistake():
    print("\n[Section 5] Common mistake: gather() for DEPENDENT operations")

    print("  WRONG: B depends on A's result — cannot run in parallel")
    print("    user_id, token = await asyncio.gather(")
    print("        create_user(data),         # returns user_id")
    print("        generate_token(user_id),   # needs user_id — race condition!")
    print("    )")

    print("\n  RIGHT: sequential await when results depend on each other")
    print("    user_id = await create_user(data)")
    print("    token = await generate_token(user_id)")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: asyncio.gather()")
    print("=" * 55)

    print("\n[Section 1] Basic gather usage")
    asyncio.run(demo_gather_basic())
    asyncio.run(demo_result_ordering())
    asyncio.run(demo_return_exceptions())
    asyncio.run(demo_exception_propagation())
    asyncio.run(demo_gather_mistake())

    print("\n" + "=" * 55)
    print("Key takeaways:")
    print("  1. gather() runs all coroutines concurrently")
    print("  2. Results always match INPUT order (not completion order)")
    print("  3. Use return_exceptions=True for resilient parallel calls")
    print("  4. Only use for INDEPENDENT operations")

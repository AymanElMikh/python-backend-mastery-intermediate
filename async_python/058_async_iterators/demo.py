"""
Demo: Async Iterators — `async for` to Stream Data Without Blocking
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import asyncio


# ── Section 1: Async generator (simplest form of async iterator) ──────────────

async def stream_database_rows(table: str, count: int):
    """
    Simulates streaming rows from a database cursor.
    Each 'yield' represents fetching the next batch from the DB.
    In real SQLAlchemy async: async for row in result:
    """
    for i in range(1, count + 1):
        await asyncio.sleep(0.05)  # simulates fetch time per row
        yield {"id": i, "table": table, "data": f"row_{i}"}


async def demo_async_generator():
    print("[Section 1] Async generator — streaming DB rows")

    # async for handles the await between each item automatically
    async for row in stream_database_rows("users", 4):
        print(f"  Processing: {row}")

    print("  All rows processed")


# ── Section 2: Class-based async iterator ─────────────────────────────────────

class EventStream:
    """
    Class-based async iterator.
    Think: WebSocket messages, Kafka events, SSE stream.
    """

    def __init__(self, events: list):
        self.events = events
        self.index = 0

    def __aiter__(self):
        return self  # the object itself is the iterator

    async def __anext__(self):
        if self.index >= len(self.events):
            raise StopAsyncIteration  # signals end of iteration

        event = self.events[self.index]
        self.index += 1
        await asyncio.sleep(0.03)  # simulates waiting for next event
        return event


async def demo_class_iterator():
    print("\n[Section 2] Class-based async iterator")

    events = ["user.created", "order.placed", "payment.processed", "email.sent"]
    stream = EventStream(events)

    async for event in stream:
        print(f"  Received event: {event}")


# ── Section 3: Async list comprehension ──────────────────────────────────────

async def demo_async_comprehension():
    print("\n[Section 3] Async comprehensions — collect all results into a list")

    # Collect all rows into a list — useful when you need random access
    # Note: this loads everything into memory before processing
    rows = [row async for row in stream_database_rows("orders", 3)]
    print(f"  All rows loaded: {len(rows)} items")
    print(f"  First row: {rows[0]}")
    print(f"  Last row:  {rows[-1]}")


# ── Section 4: Async generator with early exit ────────────────────────────────

async def stream_with_filter(total: int, max_id: int):
    """Async generator that stops early based on a condition."""
    async for row in stream_database_rows("products", total):
        if row["id"] > max_id:
            return  # stop generating — 'break' equivalent in generator
        yield row


async def demo_early_exit():
    print("\n[Section 4] Async generator with early exit condition")

    async for row in stream_with_filter(total=10, max_id=3):
        print(f"  Got row: {row['id']}")

    print("  Stopped after row 3")


# ── Section 5: The common mistake — regular for on async iterable ─────────────

async def demo_wrong_usage():
    print("\n[Section 5] Common mistake: regular 'for' on async iterator")

    stream = EventStream(["event_1", "event_2"])

    print("  WRONG: for item in async_iterator")
    print("    for event in EventStream([...]):")
    print("        # TypeError: 'async for' required, not 'for'")

    print("\n  RIGHT: async for item in async_iterator")
    async for event in stream:
        print(f"    event: {event}")

    print("\n  Also wrong: regular list comp on async generator")
    print("    rows = [row for row in stream_database_rows(...)]")
    print("    # TypeError: use [r async for r in stream_database_rows(...)]")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Async Iterators and async for")
    print("=" * 55)

    asyncio.run(demo_async_generator())
    asyncio.run(demo_class_iterator())
    asyncio.run(demo_async_comprehension())
    asyncio.run(demo_early_exit())
    asyncio.run(demo_wrong_usage())

    print("\n" + "=" * 55)
    print("Key takeaways:")
    print("  1. async for = iterate where each 'next' is an awaitable")
    print("  2. Async generators (yield in async def) are the simplest form")
    print("  3. Class-based: implement __aiter__ and async __anext__")
    print("  4. [x async for x in gen] for async list comprehensions")

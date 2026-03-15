"""
Demo: Generators — Lazy Iteration with `yield`
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import sys
import time

# ── Section 1: Basic generator vs regular function ───────────────────────────

def get_numbers_list(n):
    """Returns ALL numbers at once — everything in memory."""
    return [i for i in range(n)]

def get_numbers_gen(n):
    """Yields numbers one at a time — lazy."""
    for i in range(n):
        yield i  # pauses here each iteration


# ── Section 2: Memory comparison ──────────────────────────────────────────────

def compare_memory():
    n = 100_000

    # List: allocates all n integers immediately
    numbers_list = get_numbers_list(n)
    list_size = sys.getsizeof(numbers_list)

    # Generator: just stores the generator object (tiny)
    numbers_gen = get_numbers_gen(n)
    gen_size = sys.getsizeof(numbers_gen)

    print(f"  List of {n} ints: {list_size:,} bytes ({list_size / 1024:.1f} KB)")
    print(f"  Generator for {n} ints: {gen_size} bytes")
    print(f"  Memory ratio: {list_size // gen_size}x more for list")


# ── Section 3: Real-world pattern — streaming large file / DB rows ─────────────

def read_log_lines(lines):
    """
    Simulates reading a large log file line by line.
    In real code: for line in open("app.log"): yield line
    """
    for line in lines:
        yield line.strip()

def parse_errors(lines):
    """Generator pipeline stage: filter only error lines."""
    for line in lines:
        if "ERROR" in line:
            yield line

def format_output(lines):
    """Generator pipeline stage: format for display."""
    for i, line in enumerate(lines, start=1):
        yield f"  [{i}] {line}"

# ── Section 4: Generator expression ──────────────────────────────────────────

# list comprehension: [x*x for x in range(10)]  — builds list in memory
# generator expression: (x*x for x in range(10)) — lazy, uses ()

# Use generator expression when passing to sum(), max(), any(), all()
# because those functions consume one item at a time anyway


# ── Section 5: Common mistake — iterating a generator twice ──────────────────

def show_generator_exhaustion():
    gen = (x * 2 for x in range(5))

    print("  First iteration:")
    for val in gen:
        print(f"    {val}", end=" ")
    print()

    print("  Second iteration (generator is exhausted):")
    for val in gen:
        print(f"    {val}", end=" ")
    print("  (nothing printed — generator is done)")

    # Fix: if you need multiple passes, use list()
    data = list(x * 2 for x in range(5))
    print(f"  As list (reusable): {data}")
    print(f"  Again: {data}")  # works fine


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Generators — Lazy Iteration with `yield`")
    print("=" * 50)

    print("\n--- Section 1: Basic generator behavior ---")
    gen = get_numbers_gen(5)
    print(f"  Generator object: {gen}")
    print(f"  next(gen): {next(gen)}")
    print(f"  next(gen): {next(gen)}")
    print(f"  next(gen): {next(gen)}")
    print("  Remaining via for loop:", end=" ")
    for val in gen:
        print(val, end=" ")
    print()

    print("\n--- Section 2: Memory efficiency ---")
    compare_memory()

    print("\n--- Section 3: Generator pipeline ---")
    fake_log_lines = [
        "2026-03-15 INFO  User logged in",
        "2026-03-15 ERROR  Database timeout after 30s",
        "2026-03-15 INFO  Cache hit for key user:42",
        "2026-03-15 ERROR  Payment service unavailable",
        "2026-03-15 INFO  Health check OK",
        "2026-03-15 ERROR  Invalid token in request",
    ]
    # Chain generators — each stage is lazy, nothing runs until we consume
    lines = read_log_lines(fake_log_lines)
    errors = parse_errors(lines)
    formatted = format_output(errors)

    print("  Errors found:")
    for line in formatted:
        print(line)

    print("\n--- Section 4: Generator expression ---")
    # More memory efficient than list comprehension for sum/max/any
    numbers = range(1_000_000)
    total = sum(x * x for x in numbers)  # generator expr — no list built
    print(f"  Sum of squares (0..999999): {total:,}")

    has_large = any(x > 999_990 for x in range(1_000_000))  # stops early!
    print(f"  Any number > 999,990? {has_large}  (short-circuits, very fast)")

    print("\n--- Section 5: Common mistake — generator exhaustion ---")
    show_generator_exhaustion()

    print("\n--- Bonus: yield from (delegate to sub-generator) ---")
    def chain(*iterables):
        """Like itertools.chain — yield from each iterable in sequence."""
        for it in iterables:
            yield from it  # delegates to sub-iterator

    result = list(chain([1, 2], [3, 4], [5]))
    print(f"  chain([1,2], [3,4], [5]) = {result}")

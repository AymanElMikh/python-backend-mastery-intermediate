"""
Demo: __slots__ — Reducing Memory Overhead for High-Volume Classes
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import sys
import time
from dataclasses import dataclass

# ── Section 1: Without slots vs with slots ────────────────────────────────────

class EventNoSlots:
    """Standard class — every instance gets a __dict__."""
    def __init__(self, event_id: int, user_id: int, event_type: str, timestamp: float):
        self.event_id   = event_id
        self.user_id    = user_id
        self.event_type = event_type
        self.timestamp  = timestamp

    def __repr__(self) -> str:
        return f"Event(id={self.event_id}, type={self.event_type!r})"


class EventWithSlots:
    """With __slots__ — no per-instance __dict__, fixed attributes only."""
    __slots__ = ("event_id", "user_id", "event_type", "timestamp")

    def __init__(self, event_id: int, user_id: int, event_type: str, timestamp: float):
        self.event_id   = event_id
        self.user_id    = user_id
        self.event_type = event_type
        self.timestamp  = timestamp

    def __repr__(self) -> str:
        return f"Event(id={self.event_id}, type={self.event_type!r})"


# ── Section 2: Python 3.10+ dataclass with slots=True ────────────────────────

@dataclass(slots=True)  # Python 3.10+ — combine dataclass convenience + slots
class DataPoint:
    x: float
    y: float
    label: str = ""


# ── Section 3: Inheritance with __slots__ ────────────────────────────────────

class Base:
    __slots__ = ("id", "name")

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class ChildWithSlots(Base):
    """Right: defines its own __slots__ — no __dict__ at any level."""
    __slots__ = ("extra",)  # only NEW attributes here; inherited ones already declared

    def __init__(self, id: int, name: str, extra: str):
        super().__init__(id, name)
        self.extra = extra


class ChildWithoutSlots(Base):
    """Wrong: missing __slots__ — gets a __dict__ despite Base having slots."""
    def __init__(self, id: int, name: str, extra: str):
        super().__init__(id, name)
        self.extra = extra  # goes in __dict__


# ── Section 4: Memory comparison at scale ────────────────────────────────────

def measure_memory_usage(n: int = 100_000):
    """Compare total memory for n instances of each class."""
    ts = time.time()

    # Create n instances of each
    no_slots = [EventNoSlots(i, i % 1000, "click", ts) for i in range(n)]
    with_slots = [EventWithSlots(i, i % 1000, "click", ts) for i in range(n)]

    # Measure size of one instance
    one_no_slots = no_slots[0]
    one_with_slots = with_slots[0]

    size_no_slots   = sys.getsizeof(one_no_slots)
    size_with_slots = sys.getsizeof(one_with_slots)
    dict_overhead   = sys.getsizeof(one_no_slots.__dict__)

    return {
        "n": n,
        "obj_size_no_slots":   size_no_slots,
        "obj_size_with_slots": size_with_slots,
        "dict_overhead":       dict_overhead,
        "total_no_slots_est":  (size_no_slots + dict_overhead) * n,
        "total_with_slots_est": size_with_slots * n,
    }


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: __slots__ — Memory Optimization")
    print("=" * 50)

    print("\n--- Section 1: Single instance comparison ---")
    ts = time.time()
    no_slots   = EventNoSlots(1, 42, "login", ts)
    with_slots = EventWithSlots(1, 42, "login", ts)

    print(f"  EventNoSlots   object size: {sys.getsizeof(no_slots):4d} bytes")
    print(f"  EventNoSlots   __dict__:    {sys.getsizeof(no_slots.__dict__):4d} bytes")
    print(f"  EventNoSlots   total:       {sys.getsizeof(no_slots) + sys.getsizeof(no_slots.__dict__):4d} bytes")
    print()
    print(f"  EventWithSlots object size: {sys.getsizeof(with_slots):4d} bytes")
    print(f"  EventWithSlots __dict__:    N/A (no __dict__!)")
    print(f"  EventWithSlots total:       {sys.getsizeof(with_slots):4d} bytes")

    # Confirm no __dict__
    print(f"\n  hasattr(no_slots,   '__dict__'): {hasattr(no_slots,   '__dict__')}")
    print(f"  hasattr(with_slots, '__dict__'): {hasattr(with_slots, '__dict__')}")
    print(f"  with_slots.__slots__: {with_slots.__slots__}")

    print("\n--- Section 1b: Attribute behavior ---")
    # Reading and writing work the same
    print(f"  with_slots.event_type: {with_slots.event_type}")
    with_slots.event_type = "logout"
    print(f"  After set: {with_slots.event_type}")

    # Can't add new attributes
    try:
        with_slots.new_attr = "surprise"
    except AttributeError as e:
        print(f"  Can't add new attribute: {e}")

    # Can add new attributes to no_slots
    no_slots.new_attr = "dynamic!"
    print(f"  no_slots.new_attr: {no_slots.new_attr}  ← works, dict is flexible")

    print("\n--- Section 2: dataclass(slots=True) ---")
    dp = DataPoint(1.5, 2.5, "A")
    print(f"  DataPoint: {dp}")
    print(f"  has __dict__: {hasattr(dp, '__dict__')}")
    print(f"  size: {sys.getsizeof(dp)} bytes")

    print("\n--- Section 3: Inheritance with __slots__ ---")
    good_child = ChildWithSlots(1, "Alice", "extra_data")
    bad_child  = ChildWithoutSlots(1, "Bob", "extra_data")

    print(f"  ChildWithSlots has __dict__:    {hasattr(good_child, '__dict__')}")
    print(f"  ChildWithoutSlots has __dict__: {hasattr(bad_child,  '__dict__')}")
    print(f"  good_child size: {sys.getsizeof(good_child)} bytes")
    print(f"  bad_child  size: {sys.getsizeof(bad_child) + sys.getsizeof(bad_child.__dict__)} bytes (obj + dict)")

    print("\n--- Section 4: Memory at scale ---")
    stats = measure_memory_usage(100_000)
    print(f"  For {stats['n']:,} instances:")
    print(f"  Without slots: ~{stats['total_no_slots_est'] / 1_000_000:.1f} MB estimated")
    print(f"  With slots:    ~{stats['total_with_slots_est'] / 1_000_000:.1f} MB estimated")
    savings_pct = (1 - stats['total_with_slots_est'] / stats['total_no_slots_est']) * 100
    print(f"  Memory savings: ~{savings_pct:.0f}%")
    print()
    print("  Rule: use __slots__ when you'll have 10,000+ instances alive at once")
    print("  Don't optimize prematurely — measure first!")

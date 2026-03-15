"""
Demo: dataclasses — Auto-Generated __init__, __repr__, and More
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from dataclasses import dataclass, field, asdict, astuple
from datetime import datetime, date
from typing import Optional

# ── Section 1: Basic dataclass vs manual class ────────────────────────────────

# BEFORE dataclasses — lots of boilerplate
class ManualPoint:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"ManualPoint(x={self.x}, y={self.y})"
    def __eq__(self, other):
        return isinstance(other, ManualPoint) and self.x == other.x and self.y == other.y


# AFTER — same result, 5x less code
@dataclass
class Point:
    x: float
    y: float
    # __init__, __repr__, __eq__ all auto-generated


# ── Section 2: Defaults, default_factory, field() ────────────────────────────

@dataclass
class User:
    name: str
    email: str
    role: str = "viewer"                           # simple default
    tags: list = field(default_factory=list)       # mutable default — CORRECT
    is_active: bool = True
    created_at: datetime = field(
        default_factory=datetime.now,
        repr=False   # don't show in __repr__ — too verbose
    )
    password_hash: Optional[str] = field(
        default=None,
        repr=False,     # never show in repr — security!
        compare=False   # don't include in __eq__ comparison
    )

    def __post_init__(self):
        """Runs after __init__ — validate and normalize."""
        self.email = self.email.strip().lower()
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email!r}")
        # Derived attribute based on other fields
        if not self.name:
            raise ValueError("Name cannot be empty")


# ── Section 3: frozen=True — immutable, hashable value objects ────────────────

@dataclass(frozen=True)
class Coordinate:
    """
    frozen=True: instances are immutable + automatically hashable.
    Perfect for value objects (coordinates, currencies, dates).
    """
    lat: float
    lon: float

    def distance_to(self, other: "Coordinate") -> float:
        """Rough distance in degrees (not real geodesic)."""
        return ((self.lat - other.lat)**2 + (self.lon - other.lon)**2) ** 0.5


# ── Section 4: order=True — enables sorting ───────────────────────────────────

@dataclass(order=True)
class SemVer:
    """
    order=True generates __lt__, __le__, __gt__, __ge__.
    Comparison uses fields in definition order: major, then minor, then patch.
    """
    major: int
    minor: int
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


# ── Section 5: asdict and astuple — converting to plain Python ────────────────

@dataclass
class Address:
    street: str
    city: str
    country: str = "US"

@dataclass
class Contact:
    name: str
    email: str
    address: Address  # nested dataclass — asdict handles recursively


# ── Section 6: Common mistake — mutable default ──────────────────────────────

# Python prevents this at class definition time (unlike regular classes):
# @dataclass
# class BadUser:
#     tags: list = []  # ValueError: mutable default [] not allowed
#                      # Use: tags: list = field(default_factory=list)


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: dataclasses")
    print("=" * 50)

    print("\n--- Section 1: Basic dataclass ---")
    p1 = Point(3.0, 4.0)
    p2 = Point(3.0, 4.0)
    p3 = Point(1.0, 2.0)
    mp = ManualPoint(3.0, 4.0)

    print(f"  Point:       {p1}")
    print(f"  ManualPoint: {mp}")
    print(f"  p1 == p2: {p1 == p2}  (value equality from __eq__)")
    print(f"  p1 is p2: {p1 is p2}  (different objects)")
    print(f"  p1 == p3: {p1 == p3}")

    print("\n--- Section 2: User with fields, defaults, __post_init__ ---")
    alice = User("Alice", "  Alice@Example.COM  ", role="admin", tags=["admin"])
    bob   = User("Bob",   "bob@example.com")

    print(f"  {alice}")  # no created_at or password_hash in repr
    print(f"  {bob}")
    print(f"  alice.created_at is set: {alice.created_at is not None}")
    print(f"  alice.tags: {alice.tags}")
    print(f"  bob.tags:   {bob.tags}  ← different list (not shared)")

    # __post_init__ normalized email
    print(f"  email normalized: {alice.email!r}")

    # Tags are independent per instance
    alice.tags.append("superuser")
    print(f"  alice.tags after append: {alice.tags}")
    print(f"  bob.tags unchanged:      {bob.tags}")

    # Validation in __post_init__
    try:
        User("Bad", "not-an-email")
    except ValueError as e:
        print(f"  Validation: {e}")

    print("\n--- Section 3: frozen=True (immutable + hashable) ---")
    paris  = Coordinate(48.8566, 2.3522)
    london = Coordinate(51.5074, -0.1278)
    paris2 = Coordinate(48.8566, 2.3522)

    print(f"  {paris}")
    print(f"  paris == paris2: {paris == paris2}")
    print(f"  distance Paris→London: {paris.distance_to(london):.4f}°")

    # frozen=True makes it hashable — can be used in sets and dict keys
    locations = {paris, london, paris2}  # paris and paris2 are equal → 2 items
    print(f"  Set of 3 coordinates (2 equal): {locations}")
    travel_notes = {paris: "Eiffel Tower", london: "Big Ben"}
    print(f"  Dict key lookup: {travel_notes[paris2]}")  # paris2 == paris

    # frozen: can't modify
    try:
        paris.lat = 0
    except Exception as e:
        print(f"  Immutable: {e}")

    print("\n--- Section 4: order=True (sorting) ---")
    versions = [
        SemVer(2, 0),
        SemVer(1, 3, 5),
        SemVer(1, 3, 0),
        SemVer(1, 10, 0),
        SemVer(2, 0, 1),
    ]
    print(f"  Unsorted: {[str(v) for v in versions]}")
    print(f"  Sorted:   {[str(v) for v in sorted(versions)]}")
    print(f"  Latest:   {max(versions)}")

    print("\n--- Section 5: asdict and astuple ---")
    contact = Contact(
        name="Alice",
        email="alice@example.com",
        address=Address("123 Main St", "Springfield")
    )
    d = asdict(contact)  # recursively converts nested dataclasses too
    print(f"  asdict:   {d}")
    t = astuple(contact)
    print(f"  astuple:  {t}")
    # Great for JSON serialization:
    import json
    print(f"  JSON:     {json.dumps(d)}")

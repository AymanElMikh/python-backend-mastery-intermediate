"""
Demo: Properties — Controlled Attribute Access with @property
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import math
from functools import cached_property
from datetime import date

# ── Section 1: Basic @property, setter, and read-only ────────────────────────

class BankAccount:
    """
    Shows getter, setter with validation, and read-only property.
    """
    def __init__(self, owner: str, initial_balance: float = 0.0):
        self.owner = owner
        self._balance = initial_balance  # backing attribute — note underscore
        self._account_id = id(self)      # read-only: set once at creation

    @property
    def balance(self) -> float:
        """Getter — called when you read account.balance."""
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        """Setter — called when you write account.balance = x."""
        if not isinstance(value, (int, float)):
            raise TypeError(f"Balance must be a number, got {type(value).__name__}")
        if value < 0:
            raise ValueError(f"Balance cannot be negative: {value}")
        self._balance = round(float(value), 2)

    @property
    def account_id(self) -> int:
        """Read-only — no setter defined."""
        return self._account_id

    # No @account_id.setter → trying to set it raises AttributeError

    def deposit(self, amount: float) -> None:
        self.balance = self.balance + amount  # goes through the setter

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance = self.balance - amount  # goes through the setter


# ── Section 2: Computed properties ────────────────────────────────────────────

class Person:
    """
    Shows properties derived from other attributes.
    """
    def __init__(self, first_name: str, last_name: str, birthdate: date):
        self.first_name = first_name
        self.last_name = last_name
        self.birthdate = birthdate

    @property
    def full_name(self) -> str:
        """Computed from first + last — no backing attribute needed."""
        return f"{self.first_name} {self.last_name}"

    @full_name.setter
    def full_name(self, value: str) -> None:
        """Allow setting full_name as a string — splits into parts."""
        parts = value.strip().split(" ", 1)
        self.first_name = parts[0]
        self.last_name = parts[1] if len(parts) > 1 else ""

    @property
    def age(self) -> int:
        """Always current — computed from birthdate."""
        today = date.today()
        years = today.year - self.birthdate.year
        # Adjust if birthday hasn't occurred yet this year
        if (today.month, today.day) < (self.birthdate.month, self.birthdate.day):
            years -= 1
        return years

    @property
    def is_adult(self) -> bool:
        return self.age >= 18


# ── Section 3: cached_property — compute once, remember forever ───────────────

class DataReport:
    """
    Shows functools.cached_property for expensive computations.
    The first access computes the value; subsequent accesses use the cache.
    """
    def __init__(self, data: list[int]):
        self.data = data
        self._compute_count = 0  # track how many times we compute

    @cached_property
    def statistics(self) -> dict:
        """
        Expensive computation — cached after first access.
        cached_property stores the result on the instance dict,
        so subsequent accesses bypass the property entirely.
        """
        self._compute_count += 1
        print(f"  Computing statistics (call #{self._compute_count})...")
        return {
            "count": len(self.data),
            "sum": sum(self.data),
            "mean": sum(self.data) / len(self.data) if self.data else 0,
            "min": min(self.data) if self.data else None,
            "max": max(self.data) if self.data else None,
        }


# ── Section 4: Common mistake — using property name as backing attribute ──────

class BadCircle:
    """WRONG: self.radius calls the setter, which calls itself — infinite recursion!"""
    def __init__(self, radius):
        self.radius = radius  # BUG: calls setter, which calls setter, which...

    @property
    def radius(self):
        return self.radius  # calls itself recursively!

    @radius.setter
    def radius(self, value):
        self.radius = value  # calls itself recursively!


class GoodCircle:
    """RIGHT: backing attribute has underscore prefix."""
    def __init__(self, radius: float):
        self._radius = radius  # stores in _radius, not radius

    @property
    def radius(self) -> float:
        return self._radius   # reads from _radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value < 0:
            raise ValueError("Radius must be non-negative")
        self._radius = value  # writes to _radius

    @property
    def area(self) -> float:
        return math.pi * self._radius ** 2

    @property
    def circumference(self) -> float:
        return 2 * math.pi * self._radius


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Properties — @property, setter, cached_property")
    print("=" * 50)

    print("\n--- Section 1: BankAccount (getter, setter, read-only) ---")
    acc = BankAccount("Alice", 1000.0)
    print(f"  balance: {acc.balance}")
    print(f"  account_id: {acc.account_id}")

    acc.deposit(500)
    acc.withdraw(200)
    print(f"  After deposit+withdraw: {acc.balance}")

    # Setter validation
    try:
        acc.balance = -100
    except ValueError as e:
        print(f"  Negative balance: {e}")

    try:
        acc.balance = "lots"
    except TypeError as e:
        print(f"  Wrong type: {e}")

    # Read-only: no setter
    try:
        acc.account_id = 9999
    except AttributeError as e:
        print(f"  Read-only: {e}")

    print("\n--- Section 2: Computed properties ---")
    alice = Person("Alice", "Smith", date(1995, 6, 15))
    print(f"  full_name: {alice.full_name}")
    print(f"  age: {alice.age}")
    print(f"  is_adult: {alice.is_adult}")

    # Setter that splits full_name
    alice.full_name = "Alice Johnson"
    print(f"  After full_name = 'Alice Johnson': first={alice.first_name}, last={alice.last_name}")

    # age updates automatically — it's computed, not stored
    young = Person("Kid", "Test", date(2015, 1, 1))
    print(f"  Kid age: {young.age}, is_adult: {young.is_adult}")

    print("\n--- Section 3: cached_property ---")
    data = list(range(1, 101))
    report = DataReport(data)

    print("  First access:")
    stats = report.statistics
    print(f"  stats: {stats}")
    print("  Second access (should NOT recompute):")
    stats2 = report.statistics
    print(f"  compute_count: {report._compute_count}  (still 1 — cached!)")
    assert stats is stats2  # same object — not recomputed

    print("\n--- Section 4: Common mistake — recursive property ---")
    try:
        bad = BadCircle(5)  # RecursionError
    except RecursionError:
        print("  BadCircle: RecursionError — self.radius called itself!")

    c = GoodCircle(5)
    print(f"  GoodCircle radius={c.radius}")
    print(f"  GoodCircle area={c.area:.4f}")
    print(f"  GoodCircle circumference={c.circumference:.4f}")
    c.radius = 10
    print(f"  After radius=10: area={c.area:.4f}")

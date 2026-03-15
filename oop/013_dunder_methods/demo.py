"""
Demo: Dunder Methods — Making Objects Behave Like Python Builtins
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from functools import total_ordering

# ── Section 1: __repr__ and __str__ ──────────────────────────────────────────

class Product:
    """
    Shows the difference between __repr__ (devs) and __str__ (users).
    """
    def __init__(self, name: str, price: float, sku: str):
        self.name = name
        self.price = price
        self.sku = sku

    def __repr__(self) -> str:
        # Developer-facing: enough info to recreate or identify the object
        return f"Product(name={self.name!r}, price={self.price!r}, sku={self.sku!r})"

    def __str__(self) -> str:
        # User-facing: clean, human-readable
        return f"{self.name} — ${self.price:.2f}"


# ── Section 2: __eq__ and __hash__ ───────────────────────────────────────────

class Point:
    """
    2D point with value equality and hashability.
    """
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __eq__(self, other) -> bool:
        if not isinstance(other, Point):
            return NotImplemented  # let Python try the other side
        return self.x == other.x and self.y == other.y

    # REQUIRED: define __hash__ when you define __eq__
    # Python removes __hash__ automatically when you define __eq__
    def __hash__(self) -> int:
        return hash((self.x, self.y))  # hash the tuple of values

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"


# ── Section 3: Comparison dunders with @total_ordering ───────────────────────

@total_ordering  # generates >, >=, <= from __eq__ + __lt__ automatically
class Version:
    """
    Semantic version — supports comparison and sorting.
    """
    def __init__(self, major: int, minor: int, patch: int = 0):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __eq__(self, other) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other) -> "bool":
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __hash__(self) -> int:
        return hash((self.major, self.minor, self.patch))

    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        return f"Version({self.major}, {self.minor}, {self.patch})"


# ── Section 4: Collection-like dunders ───────────────────────────────────────

class ShoppingCart:
    """
    Cart with __len__, __bool__, __contains__, __iter__.
    """
    def __init__(self):
        self._items: list = []

    def add(self, product: Product, quantity: int = 1) -> None:
        self._items.append({"product": product, "quantity": quantity})

    def __len__(self) -> int:
        return sum(item["quantity"] for item in self._items)

    def __bool__(self) -> bool:
        return len(self._items) > 0  # empty cart is falsy

    def __contains__(self, product: Product) -> bool:
        return any(item["product"].sku == product.sku for item in self._items)

    def __iter__(self):
        return iter(self._items)

    def total(self) -> float:
        return sum(item["product"].price * item["quantity"] for item in self._items)

    def __repr__(self) -> str:
        return f"ShoppingCart({len(self)} items, total=${self.total():.2f})"


# ── Section 5: __call__ — making instances callable ──────────────────────────

class TaxCalculator:
    """
    __call__ makes an instance usable like a function.
    Useful for strategies, validators, and transformers.
    """
    def __init__(self, rate: float):
        self.rate = rate

    def __call__(self, amount: float) -> float:
        return round(amount * (1 + self.rate), 2)

    def __repr__(self) -> str:
        return f"TaxCalculator(rate={self.rate:.1%})"


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Dunder Methods")
    print("=" * 50)

    print("\n--- Section 1: __repr__ vs __str__ ---")
    p = Product("Wireless Mouse", 29.99, "SKU-001")
    print(f"  str(p):  {str(p)}")
    print(f"  repr(p): {repr(p)}")
    print(f"  print:   {p}")  # calls __str__
    print(f"  In list: {[p]}")  # calls __repr__ for container display

    print("\n--- Section 2: __eq__ and __hash__ ---")
    p1 = Point(3, 4)
    p2 = Point(3, 4)
    p3 = Point(1, 2)

    print(f"  Point(3,4) == Point(3,4): {p1 == p2}")  # True (value equality)
    print(f"  Point(3,4) is Point(3,4): {p1 is p2}")  # False (different objects)
    print(f"  Point(3,4) == Point(1,2): {p1 == p3}")

    # __hash__ lets us use Points in sets and as dict keys
    point_set = {p1, p2, p3}  # p1 and p2 are equal, so set has 2 items
    print(f"  Set of 3 points (2 equal): {point_set}")
    point_labels = {p1: "origin-ish", p3: "near-origin"}
    print(f"  Dict lookup by value: {point_labels[p2]}")  # p2 == p1

    print("\n--- Section 3: Comparison + sorting with @total_ordering ---")
    v1 = Version(1, 2, 3)
    v2 = Version(1, 3, 0)
    v3 = Version(2, 0, 0)
    v4 = Version(1, 2, 3)

    print(f"  {v1} == {v4}: {v1 == v4}")
    print(f"  {v1} < {v2}: {v1 < v2}")
    print(f"  {v2} > {v1}: {v2 > v1}")  # generated by @total_ordering
    print(f"  {v3} >= {v2}: {v3 >= v2}")

    versions = [v3, v1, v2, v4]
    print(f"  sorted: {sorted(versions)}")
    print(f"  max:    {max(versions)}")
    print(f"  min:    {min(versions)}")

    print("\n--- Section 4: Collection dunders ---")
    laptop = Product("Laptop", 999.99, "SKU-002")
    mouse  = Product("Mouse",  29.99,  "SKU-001")
    cart   = ShoppingCart()

    print(f"  Empty cart is falsy: {bool(cart)}")
    cart.add(laptop, 1)
    cart.add(mouse, 2)
    print(f"  {repr(cart)}")
    print(f"  len(cart): {len(cart)}")
    print(f"  bool(cart): {bool(cart)}")
    print(f"  laptop in cart: {laptop in cart}")
    print(f"  Items:")
    for item in cart:
        print(f"    {item['product']} × {item['quantity']}")

    print("\n--- Section 5: __call__ ---")
    us_tax = TaxCalculator(rate=0.08)   # 8% tax
    eu_vat = TaxCalculator(rate=0.20)   # 20% VAT

    price = 100.00
    print(f"  {us_tax}: ${price:.2f} → ${us_tax(price)}")  # called like a function
    print(f"  {eu_vat}: ${price:.2f} → ${eu_vat(price)}")
    print(f"  is callable: {callable(us_tax)}")  # True because __call__ is defined

    # Useful: pass instance as a callback
    prices = [10.0, 25.50, 99.99]
    taxed = list(map(us_tax, prices))  # us_tax used as a function
    print(f"  Prices after 8% tax: {taxed}")

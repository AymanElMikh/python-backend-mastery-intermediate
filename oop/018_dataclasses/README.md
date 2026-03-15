# dataclasses — Auto-Generated `__init__`, `__repr__`, and More

## 🎯 Interview Question
"What is a Python dataclass and when would you use it over a regular class?"

## 💡 Short Answer (30 seconds)
A dataclass is a regular Python class decorated with `@dataclass` that auto-generates common boilerplate: `__init__`, `__repr__`, and optionally `__eq__`, `__hash__`, and `__lt__`. You use them for data-holder classes — models, DTOs (Data Transfer Objects), config objects — where you'd otherwise write the same `__init__` by hand. They're faster to write, less error-prone, and immediately readable.

## 🔬 Explanation
Before dataclasses, writing a simple data model required lots of boilerplate:

```python
# Without dataclass — 10 lines
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"
    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y
```

With `@dataclass`:
```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
# __init__, __repr__, __eq__ all auto-generated!
```

**Key parameters on `@dataclass`:**
- `frozen=True` — makes instances immutable (sets `__hash__` too)
- `order=True` — generates `__lt__`, `__le__`, `__gt__`, `__ge__` for sorting
- `eq=True` (default) — generates `__eq__`

**Field options with `field()`:**
- `default_factory=list` — mutable defaults (solves the `[]` default bug)
- `repr=False` — exclude from `__repr__` (e.g., passwords)
- `compare=False` — exclude from `__eq__` comparisons
- `init=False` — exclude from `__init__`, set in `__post_init__`

**`__post_init__`**: called automatically after `__init__` — for validation and derived attributes.

Dataclasses are widely used for:
- API request/response DTOs
- Config objects
- Internal data models (before Pydantic if validation isn't needed)
- Value objects in domain logic

## 💻 Code Example
```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    name: str
    email: str
    role: str = "viewer"
    tags: list = field(default_factory=list)  # mutable default — CORRECT way
    created_at: datetime = field(default_factory=datetime.now, repr=False)

    def __post_init__(self):
        self.email = self.email.lower().strip()
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")

alice = User("Alice", "Alice@Example.COM", role="admin")
print(alice)  # User(name='Alice', email='alice@example.com', role='admin', tags=[])

@dataclass(frozen=True)  # immutable — hashable, usable as dict key
class Coordinate:
    lat: float
    lon: float
```

## ⚠️ Common Mistakes

1. **Mutable default without `field(default_factory=...)`** — `tags: list = []` in a dataclass raises `ValueError` at definition time. Python warns you immediately (unlike regular classes where this causes a silent bug). Use `tags: list = field(default_factory=list)`.

2. **Using `@dataclass` when you need heavy validation** — dataclasses have `__post_init__` but it's manual. For complex validation with many fields, Pydantic's `BaseModel` is better — it validates types and values automatically.

3. **Forgetting `frozen=True` for value objects** — if a dataclass is meant to be immutable (a coordinate, a currency amount), add `frozen=True`. Without it, nothing stops mutation.

## ✅ When to Use vs When NOT to Use

**Use `@dataclass` when:**
- You're writing a data-holder class (model, DTO, config, event)
- You don't need type coercion or complex validation — just storage
- You want `__repr__` and `__eq__` for free

**Use Pydantic `BaseModel` instead when:**
- You need type coercion (string `"42"` → int `42`)
- You need field validation with error messages
- You're building a FastAPI API (Pydantic is already there)

**Use a regular class when:**
- The class has significant behavior, not just data
- You need fine-grained control over `__init__` logic

## 🔗 Related Concepts
- [011_classes_and_init](../011_classes_and_init) — dataclasses replace manual `__init__`
- [013_dunder_methods](../013_dunder_methods) — dataclasses auto-generate many dunders
- [019_slots](../019_slots) — `@dataclass(slots=True)` for memory efficiency

## 🚀 Next Step
In `python-backend-mastery`: **Pydantic v2 models** — strict validation, custom validators, model serialization/deserialization, and how Pydantic builds on dataclass concepts to power FastAPI's entire request/response model.

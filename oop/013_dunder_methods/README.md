# Dunder Methods — Making Objects Behave Like Python Builtins

## 🎯 Interview Question
"What are dunder methods in Python? Can you name a few that are useful in real projects and explain what they do?"

## 💡 Short Answer (30 seconds)
Dunder methods (double-underscore methods, also called "magic methods") let your objects integrate with Python's built-in operators and functions. `__str__` controls what `print(obj)` shows, `__repr__` controls the developer-facing representation, `__eq__` makes `==` work between objects, `__len__` makes `len(obj)` work, and `__lt__` enables sorting. They're how you make your classes feel like first-class Python citizens.

## 🔬 Explanation
Python's operators and built-in functions are all backed by dunder methods:

| What you write | Dunder called | Used for |
|---|---|---|
| `str(obj)` or `print(obj)` | `__str__` | Human-readable string |
| `repr(obj)` | `__repr__` | Developer/debug representation |
| `obj1 == obj2` | `__eq__` | Equality check |
| `obj1 < obj2` | `__lt__` | Less-than comparison |
| `len(obj)` | `__len__` | Length |
| `obj[key]` | `__getitem__` | Index/key access |
| `key in obj` | `__contains__` | Membership test |
| `obj()` | `__call__` | Make instance callable |
| `with obj:` | `__enter__`, `__exit__` | Context manager |
| `for x in obj:` | `__iter__`, `__next__` | Iteration |
| `bool(obj)` | `__bool__` | Truthiness |

**`__repr__` vs `__str__`**: the rule is "repr is for devs, str is for users." `__repr__` should ideally produce valid Python code to recreate the object. If only one is defined, Python uses `__repr__` as fallback for both.

In real backend projects, you'll most commonly implement:
- `__repr__` on every model class (for logging and debugging)
- `__eq__` when you need to compare model objects (e.g., in tests)
- `__hash__` when objects are used as dict keys or in sets (required if you define `__eq__`)
- `__len__` and `__bool__` on collection-like classes

## 💻 Code Example
```python
class Money:
    def __init__(self, amount: float, currency: str = "USD"):
        self.amount = round(amount, 2)
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money({self.amount!r}, {self.currency!r})"

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __lt__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount < other.amount

m1 = Money(10.50)
m2 = Money(5.25)
print(str(m1))     # USD 10.50
print(repr(m1))    # Money(10.5, 'USD')
print(m1 + m2)     # USD 15.75
print(m1 > m2)     # True  (uses __lt__ + reflection)
print(sorted([m1, m2]))  # sorted works because __lt__ is defined
```

## ⚠️ Common Mistakes

1. **Defining `__eq__` without `__hash__`** — Python removes `__hash__` when you define `__eq__`. If you use the object as a dict key or in a set, it breaks with `TypeError: unhashable type`. If equality is based on an immutable attribute, add `__hash__ = <parent>.__hash__` or implement your own.

2. **`__str__` calling itself recursively** — `def __str__(self): return str(self)` is infinite recursion. Use f-strings with explicit attributes.

3. **`__repr__` being too vague** — `return f"<User object>"` is useless. A good `__repr__` should show enough info to identify the object: `return f"User(id={self.id!r}, name={self.name!r})"`.

## ✅ When to Use vs When NOT to Use

**Always implement:**
- `__repr__` on any class you'll use in logging or debugging
- `__eq__` when you need value equality (not identity) between instances

**Implement as needed:**
- `__str__` when the user-facing and developer-facing representations differ
- `__lt__` (plus `__eq__`) when objects need to be sorted
- `__len__`, `__bool__` for collection-like classes
- `__call__` when an object should be callable (like a strategy or handler)

**Avoid:**
- Overloading operators in confusing ways (`__add__` for non-additive things)
- Implementing dunders that don't have an obvious, intuitive meaning for your class

## 🔗 Related Concepts
- [011_classes_and_init](../011_classes_and_init) — `__init__` is the most common dunder
- [002_context_managers](../../python_core/002_context_managers) — `__enter__`/`__exit__`
- [009_iterators_iterables](../../python_core/009_iterators_iterables) — `__iter__`/`__next__`

## 🚀 Next Step
In `python-backend-mastery`: **Descriptors (`__get__`, `__set__`, `__delete__`)** — how SQLAlchemy columns, Pydantic fields, and `@property` all work under the hood; essential for understanding the Python data model at depth.

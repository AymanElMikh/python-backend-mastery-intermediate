# Classes and `__init__` — Building Objects in Python

## 🎯 Interview Question
"How do you define a class in Python? What is `__init__` and what is `self`?"

## 💡 Short Answer (30 seconds)
A class is a blueprint for creating objects. `__init__` is the initializer method — it runs automatically when you create a new instance and lets you set up the object's initial state. `self` is a reference to the instance being created; it's how the object refers to its own attributes and methods. Every instance method takes `self` as its first parameter.

## 🔬 Explanation
Classes bundle **data** (attributes) and **behavior** (methods) together. When you write `user = User("Alice", "alice@example.com")`, Python:
1. Creates a new `User` object in memory
2. Calls `User.__init__(user, "Alice", "alice@example.com")` automatically
3. Returns the new object and assigns it to `user`

**`self` explained**: `self` is not a keyword — it's just a naming convention. Python passes the instance as the first argument to every method. When you write `user.greet()`, Python translates it to `User.greet(user)`.

**Instance vs class attributes**:
- Instance attributes (defined in `__init__` with `self.x = ...`) belong to each object — different for each instance
- Class attributes (defined at class body level) are shared across all instances — use for defaults or constants

In real backend projects, classes appear everywhere:
- **Models**: `User`, `Order`, `Product` — encapsulating data + validation
- **Services**: `UserService`, `EmailService` — grouping related operations
- **Repositories**: `UserRepository` — abstracting database access
- **Pydantic models, SQLAlchemy models, dataclasses** — all built on this foundation

## 💻 Code Example
```python
class User:
    # Class attribute — shared by all instances
    DEFAULT_ROLE = "viewer"

    def __init__(self, name: str, email: str, role: str = None):
        # Instance attributes — unique to each object
        self.name = name
        self.email = email
        self.role = role or self.DEFAULT_ROLE
        self.is_active = True

    def greet(self) -> str:
        return f"Hi, I'm {self.name} ({self.email})"

    def deactivate(self) -> None:
        self.is_active = False

    def __repr__(self) -> str:
        return f"User(name={self.name!r}, email={self.email!r})"

alice = User("Alice", "alice@example.com", role="admin")
bob   = User("Bob",   "bob@example.com")

print(alice.greet())   # Hi, I'm Alice (alice@example.com)
print(bob.role)        # viewer  — picked up DEFAULT_ROLE
```

## ⚠️ Common Mistakes

1. **Mutable default argument in `__init__`** — `def __init__(self, tags=[])` shares the list across ALL instances. Use `def __init__(self, tags=None)` and then `self.tags = tags if tags is not None else []`.

2. **Forgetting `self.` when setting instance attributes** — writing `name = value` inside `__init__` creates a local variable, not an attribute. Always write `self.name = value`.

3. **Using class attributes for mutable state** — `class User: sessions = []` makes all users share the same list. That's almost never what you want. Mutable per-instance data belongs in `__init__`.

## ✅ When to Use vs When NOT to Use

**Use a class when:**
- You have data and behavior that naturally belong together
- You need multiple instances with their own independent state
- You'll use inheritance or want to implement protocols (like iteration)

**Avoid classes when:**
- You just need to group a few functions — a module does that
- You have stateless logic — use a plain function
- You only ever create one instance — consider a module-level function or `dataclass`

## 🔗 Related Concepts
- [012_inheritance_super](../012_inheritance_super) — building on existing classes
- [013_dunder_methods](../013_dunder_methods) — `__repr__`, `__str__`, `__eq__` and more
- [018_dataclasses](../018_dataclasses) — auto-generate `__init__` and `__repr__` with `@dataclass`

## 🚀 Next Step
In `python-backend-mastery`: **`__new__` vs `__init__`** — how object creation actually works, when to override `__new__` (Singleton, immutable types), and the `__init_subclass__` hook for automatic subclass registration.

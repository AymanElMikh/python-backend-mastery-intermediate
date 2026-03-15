# Abstract Base Classes — Enforcing Interfaces in Python

## 🎯 Interview Question
"What is an abstract base class (ABC) in Python, and why would you use one instead of a regular base class?"

## 💡 Short Answer (30 seconds)
An abstract base class is a class that declares methods that subclasses *must* implement. You can't instantiate an ABC directly — only concrete subclasses that implement all abstract methods. Use them when you're defining an interface or contract: "anyone who inherits from this must implement `save()`, `load()`, and `delete()`." They're Python's way of enforcing a protocol at class definition time rather than failing at runtime.

## 🔬 Explanation
Without ABCs, base classes in Python rely on convention — subclasses *should* override methods, but nothing enforces it. With ABCs, Python raises `TypeError` at instantiation time if a subclass doesn't implement all abstract methods.

**How to use:**
```python
from abc import ABC, abstractmethod

class BaseRepository(ABC):
    @abstractmethod
    def get(self, id: int): ...

    @abstractmethod
    def save(self, entity): ...
```

Now `BaseRepository()` raises `TypeError`. Any subclass that forgets `save()` also raises `TypeError` when you try to instantiate it.

**Real-world uses in backend development:**
- **Repository pattern**: `BaseRepository(ABC)` with `get`, `save`, `delete` — swap SQLAlchemy for an in-memory repo in tests
- **Notification service**: `BaseNotifier(ABC)` with `send()` — email, SMS, Slack all implement the same interface
- **Storage backends**: `BaseStorage(ABC)` with `upload`, `download` — S3, local disk, GCS all interchangeable
- **Payment processors**: `BasePaymentProcessor(ABC)` with `charge`, `refund`

The key benefit: if you swap implementations (e.g., swap your SQL repo for an in-memory repo in tests), Python guarantees the interface is correct — not just by convention, but enforced.

## 💻 Code Example
```python
from abc import ABC, abstractmethod

class BaseRepository(ABC):
    @abstractmethod
    def get(self, id: int) -> dict | None: ...

    @abstractmethod
    def save(self, entity: dict) -> dict: ...

    @abstractmethod
    def delete(self, id: int) -> bool: ...

    def exists(self, id: int) -> bool:
        """Non-abstract method: shared logic, available to all subclasses."""
        return self.get(id) is not None

class InMemoryUserRepo(BaseRepository):
    def __init__(self):
        self._store: dict = {}

    def get(self, id: int) -> dict | None:
        return self._store.get(id)

    def save(self, entity: dict) -> dict:
        self._store[entity["id"]] = entity
        return entity

    def delete(self, id: int) -> bool:
        return self._store.pop(id, None) is not None

# BaseRepository() → TypeError: Can't instantiate abstract class
repo = InMemoryUserRepo()  # works fine
```

## ⚠️ Common Mistakes

1. **Inheriting ABC but not marking methods `@abstractmethod`** — a class can inherit from `ABC` but without `@abstractmethod`, nothing is enforced. The `@abstractmethod` decorator on each method is what creates the contract.

2. **Forgetting that abstract methods can have a body** — `@abstractmethod` doesn't mean the method must be empty. The base can provide a default implementation that subclasses call via `super().method()`. This is useful for shared logic with required extension points.

3. **Over-abstracting** — if you only ever have one implementation, an ABC adds ceremony with no benefit. Create the ABC when you have (or clearly anticipate) 2+ concrete implementations.

## ✅ When to Use vs When NOT to Use

**Use ABCs when:**
- You have a concept with multiple implementations that must be interchangeable (repo pattern, storage backends, notification channels)
- You want Python to enforce the interface at class definition time rather than at first call
- You're writing a library or framework and consumers must implement certain methods

**Avoid ABCs when:**
- You only have one implementation — just write the class
- You're forcing inheritance where composition would be cleaner
- The "interface" is just one method — a simple callable/function might be enough

## 🔗 Related Concepts
- [012_inheritance_super](../012_inheritance_super) — ABCs use inheritance
- [015_composition_vs_inheritance](../015_composition_vs_inheritance) — when ABCs go too far
- [007_exception_handling](../../python_core/007_exception_handling) — `AppError(Exception)` is a practical ABC example

## 🚀 Next Step
In `python-backend-mastery`: **`typing.Protocol`** — structural subtyping (duck typing with static checking). A `Protocol` defines an interface without requiring inheritance — any class that has the right methods satisfies it, regardless of its class hierarchy.

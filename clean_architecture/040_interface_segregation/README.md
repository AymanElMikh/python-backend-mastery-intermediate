# Interface Segregation

## 🎯 Interview Question
What is the Interface Segregation Principle (ISP) and how do you apply it in Python?

## 💡 Short Answer (30 seconds)
The Interface Segregation Principle says: don't force a class to implement methods it doesn't need. Instead of one large interface with 10 methods, define several focused interfaces — each with only the methods that belong together. In Python, this means keeping your abstract base classes small and role-specific, so implementations only need to implement what they actually do.

## 🔬 Explanation
Imagine a `StorageBackend` ABC with four methods: `save()`, `load()`, `delete()`, `list_files()`. You create a `ReadOnlyStorage` implementation that only makes sense for reading — but now you're forced to implement `save()` and `delete()` even though they should never be called.

The fix: split the interface by role:
- `Readable`: just `load()`
- `Writable`: just `save()`
- `Deletable`: just `delete()`
- `Listable`: just `list_files()`
- `FullStorage` implements all four (or inherits from all four)

Now `ReadOnlyStorage` only implements `Readable`. If someone tries to pass it where a `Writable` is expected, they get a clear type error instead of a surprise `NotImplementedError` at runtime.

In Python backend work this pattern appears in:
- Repository interfaces (read-only vs read-write)
- Notification services (email-only vs SMS-only vs both)
- Storage backends (some can only write, some can only read)

## 💻 Code Example
```python
from abc import ABC, abstractmethod

# ❌ Fat interface — forces ReadOnlyRepo to implement write methods
class UserRepository(ABC):
    @abstractmethod
    def get(self, user_id: int): pass

    @abstractmethod
    def save(self, user): pass  # ReadOnlyRepo has to stub this out

    @abstractmethod
    def delete(self, user_id: int): pass  # Same problem

# ✅ Segregated interfaces — each class only implements what it needs
class UserReader(ABC):
    @abstractmethod
    def get(self, user_id: int): pass

class UserWriter(ABC):
    @abstractmethod
    def save(self, user): pass

class UserDeleter(ABC):
    @abstractmethod
    def delete(self, user_id: int): pass

# Full access: implements all three
class UserRepository(UserReader, UserWriter, UserDeleter):
    def get(self, user_id): ...
    def save(self, user): ...
    def delete(self, user_id): ...

# Read-only cache: only needs UserReader
class UserCache(UserReader):
    def get(self, user_id): ...  # Returns from cache; no save/delete needed
```

## ⚠️ Common Mistakes
1. **Creating one interface per class.** ISP doesn't mean "one method per interface". It means "group methods that are used together." Two methods always used together belong in the same interface.
2. **Stubbing methods with `raise NotImplementedError`.** If you implement `save()` just to raise `NotImplementedError`, your interface is too large. Split it.
3. **Over-segregating.** Four separate ABCs for four methods that are always injected together is over-engineering. Start with a reasonable interface; split when you actually have a class that shouldn't implement part of it.

## ✅ When to Use vs When NOT to Use
**Use when:**
- You have implementations that naturally only support a subset of operations (read-only, write-only, append-only)
- A class is being forced to stub out methods with `pass` or `raise NotImplementedError`
- Different callers need different subsets of the interface

**Don't use when:**
- All implementations naturally implement all methods — no splitting needed
- You'd end up with 10 one-method ABCs just to follow the principle mechanically

## 🔗 Related Concepts
- [oop/014_abstract_base_classes](../../oop/014_abstract_base_classes) — ABCs are how Python expresses interfaces
- [oop/015_composition_vs_inheritance](../../oop/015_composition_vs_inheritance) — multiple inheritance is how Python composes interfaces
- [design_patterns/026_repository_pattern](../../design_patterns/026_repository_pattern) — repositories are a common place to apply ISP

## 🚀 Next Step
In `python-backend-mastery`: **SOLID principles end-to-end** — applying all five SOLID principles (SRP, OCP, LSP, ISP, DIP) to a real-world FastAPI service with a detailed refactoring walkthrough.

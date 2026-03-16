# Repository Pattern

## 🎯 Interview Question
What is the Repository pattern and why would you use it in a Python backend project?

## 💡 Short Answer (30 seconds)
The Repository pattern adds a layer between your business logic and the database. Instead of scattering raw SQL or ORM queries across your service code, all database access for a given model lives in one class — the repository. Your service layer calls `user_repo.get_by_id(1)` without caring whether it's using SQLAlchemy, a raw DB driver, or a mock. This makes your code easier to test and easier to swap databases.

## 🔬 Explanation
Without a repository, your service functions contain SQLAlchemy session calls directly. When you want to test the service, you need a real database — or you have to mock SQLAlchemy's session object, which is tedious and brittle.

With a repository:
- The service calls `repo.find_by_email("a@b.com")` — a clean Python method
- In production, the repo talks to SQLAlchemy
- In tests, you inject a fake in-memory repo — no database needed

This is a key piece of "clean architecture" — your business logic doesn't depend on infrastructure (the DB). This pattern is especially valuable in FastAPI/Flask apps where services grow large.

## 💻 Code Example
```python
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> dict | None:
        pass

    @abstractmethod
    def save(self, user: dict) -> dict:
        pass

class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._store: dict[int, dict] = {}
        self._next_id = 1

    def get_by_id(self, user_id: int) -> dict | None:
        return self._store.get(user_id)

    def save(self, user: dict) -> dict:
        user["id"] = self._next_id
        self._store[self._next_id] = user
        self._next_id += 1
        return user

class UserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo  # Injected — doesn't know which implementation

    def register(self, email: str) -> dict:
        return self._repo.save({"email": email})
```

## ⚠️ Common Mistakes
1. **Putting business logic in the repository.** The repo should only do DB operations — no "if user is premium, do X" logic. That belongs in the service.
2. **Leaking ORM objects out of the repository.** If you return a SQLAlchemy model object, your service is now coupled to SQLAlchemy. Return plain dicts or dataclasses instead.
3. **One giant repository for everything.** One repo per aggregate/model is the rule. A `UserRepository` and `OrderRepository` should be separate.

## ✅ When to Use vs When NOT to Use
**Use when:**
- You want to test service logic without a real database
- You may need to swap databases (SQLite in tests, Postgres in prod)
- Your database access logic is duplicated across multiple service functions

**Don't use when:**
- It's a tiny script or prototype — direct ORM calls are fine
- Your queries are so complex that the repository abstraction doesn't add clarity
- The framework already provides a sufficient abstraction (Django's ORM managers)

## 🔗 Related Concepts
- [oop/014_abstract_base_classes](../../oop/014_abstract_base_classes) — ABC defines the repo interface
- [design_patterns/021_factory_pattern](../021_factory_pattern) — factory can create the right repo implementation
- [clean_architecture](../../clean_architecture) — repository is a key building block of service/repository architecture
- [databases](../../databases) — SQLAlchemy-backed repository implementation

## 🚀 Next Step
In `python-backend-mastery`: **Unit of Work pattern** — combining multiple repositories in a single transaction, with rollback on failure. Essential for complex business operations.

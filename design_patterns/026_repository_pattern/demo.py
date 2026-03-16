"""
Demo: Repository Pattern
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


# ── Section 1: Domain object (what the app works with) ───────────────────────

@dataclass
class User:
    email: str
    name: str
    id: Optional[int] = None  # None until saved


# ── Section 2: The repository interface ──────────────────────────────────────

class UserRepository(ABC):
    """
    Contract for all user data access.
    Service code depends only on this interface — never on the implementation.
    """
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass

    @abstractmethod
    def list_all(self) -> list[User]:
        pass


# ── Section 3: In-memory implementation (great for tests) ────────────────────

class InMemoryUserRepository(UserRepository):
    """
    No database. Data lives in a dict.
    Perfect for unit tests — fast, zero setup, no cleanup.
    """
    def __init__(self):
        self._store: dict[int, User] = {}
        self._next_id = 1

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self._store.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        for user in self._store.values():
            if user.email == email:
                return user
        return None

    def save(self, user: User) -> User:
        if user.id is None:
            # New user — assign an ID
            user.id = self._next_id
            self._next_id += 1
        self._store[user.id] = user
        return user

    def delete(self, user_id: int) -> bool:
        if user_id in self._store:
            del self._store[user_id]
            return True
        return False

    def list_all(self) -> list[User]:
        return list(self._store.values())


# ── Section 4: Service layer — depends on the interface, not implementation ───

class UserService:
    """
    All business logic lives here.
    No SQLAlchemy, no database — just the repository interface.
    """
    def __init__(self, repo: UserRepository):
        self._repo = repo  # Injected from outside

    def register(self, email: str, name: str) -> User:
        # Business rule: no duplicate emails
        existing = self._repo.get_by_email(email)
        if existing:
            raise ValueError(f"Email '{email}' is already registered.")
        user = User(email=email, name=name)
        return self._repo.save(user)

    def get_user(self, user_id: int) -> User:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise ValueError(f"User #{user_id} not found.")
        return user

    def delete_user(self, user_id: int) -> None:
        deleted = self._repo.delete(user_id)
        if not deleted:
            raise ValueError(f"User #{user_id} not found.")

    def list_users(self) -> list[User]:
        return self._repo.list_all()


# ── Section 5: Common mistake — business logic in the repository ──────────────

class BadUserRepository(InMemoryUserRepository):
    def save(self, user: User) -> User:
        # BAD: business rule in the repo. This belongs in UserService.
        if "@" not in user.email:
            raise ValueError("Invalid email")
        return super().save(user)


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Repository Pattern")
    print("=" * 55)

    print("\n--- Setup: inject in-memory repo into service ---")
    repo = InMemoryUserRepository()
    service = UserService(repo)

    print("\n--- Register users ---")
    alice = service.register("alice@example.com", "Alice")
    bob = service.register("bob@example.com", "Bob")
    charlie = service.register("charlie@example.com", "Charlie")
    print(f"  Registered: {alice}")
    print(f"  Registered: {bob}")
    print(f"  Registered: {charlie}")

    print("\n--- Duplicate email raises early ---")
    try:
        service.register("alice@example.com", "Another Alice")
    except ValueError as e:
        print(f"  ValueError: {e}")

    print("\n--- Get user by ID ---")
    found = service.get_user(2)
    print(f"  Found: {found}")

    print("\n--- Get non-existent user ---")
    try:
        service.get_user(999)
    except ValueError as e:
        print(f"  ValueError: {e}")

    print("\n--- List all users ---")
    for user in service.list_users():
        print(f"  {user}")

    print("\n--- Delete a user ---")
    service.delete_user(bob.id)
    print(f"  Deleted user #{bob.id}")
    print(f"  Remaining: {[u.email for u in service.list_users()]}")

    print("\n--- Testing is easy: swap repo for a fresh one ---")
    # Each test gets a clean repo — no DB setup, no cleanup
    test_repo = InMemoryUserRepository()
    test_service = UserService(test_repo)
    u = test_service.register("test@example.com", "Test User")
    assert u.id == 1
    assert test_service.get_user(1).email == "test@example.com"
    print("  Tests pass with in-memory repo — no database needed!")

    print("\n--- Common mistake: business rule in repository ---")
    bad_repo = BadUserRepository()
    bad_service = UserService(bad_repo)
    try:
        bad_service.register("not-an-email", "Bad User")
    except ValueError as e:
        print(f"  Rule enforced in wrong place: {e}")
        print("  This should be in UserService, not BadUserRepository")

"""
Demo: Dependency Injection
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from abc import ABC, abstractmethod
from typing import Optional


# ── Section 1: Without DI — hardcoded dependencies ───────────────────────────

class HardcodedEmailClient:
    def send(self, to: str, subject: str) -> None:
        print(f"  [Real Email] Sending '{subject}' to {to}")


class HardcodedRepo:
    def __init__(self):
        self._store: dict = {}

    def save(self, user: dict) -> dict:
        user["id"] = len(self._store) + 1
        self._store[user["id"]] = user
        return user

    def find(self, email: str) -> Optional[dict]:
        return next((u for u in self._store.values() if u["email"] == email), None)


class UserServiceBad:
    """
    BAD: creates its own dependencies.
    - Can't test without sending real emails
    - Can't swap the DB without editing this class
    """
    def __init__(self):
        self._repo = HardcodedRepo()     # hardcoded
        self._email = HardcodedEmailClient()  # hardcoded — real email in tests!

    def register(self, email: str) -> dict:
        user = self._repo.save({"email": email})
        self._email.send(email, "Welcome!")
        return user


# ── Section 2: With DI — dependencies come from outside ──────────────────────

class EmailService(ABC):
    @abstractmethod
    def send_welcome(self, email: str) -> None:
        pass


class UserRepo(ABC):
    @abstractmethod
    def save(self, user: dict) -> dict:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[dict]:
        pass


# Production implementations
class RealEmailService(EmailService):
    def send_welcome(self, email: str) -> None:
        print(f"  [SendGrid] Sending welcome email to {email}")


class InMemoryUserRepo(UserRepo):
    def __init__(self):
        self._store: dict = {}
        self._next_id = 1

    def save(self, user: dict) -> dict:
        user["id"] = self._next_id
        self._store[self._next_id] = user
        self._next_id += 1
        return user

    def find_by_email(self, email: str) -> Optional[dict]:
        return next((u for u in self._store.values() if u["email"] == email), None)


class UserService:
    """
    GOOD: dependencies are injected.
    - Test by injecting fakes
    - Swap implementations without touching this class
    """
    def __init__(self, repo: UserRepo, email: EmailService):
        self._repo = repo      # injected
        self._email = email    # injected

    def register(self, email: str) -> dict:
        if self._repo.find_by_email(email):
            raise ValueError(f"'{email}' already registered")
        user = self._repo.save({"email": email})
        self._email.send_welcome(email)
        return user

    def get_user(self, email: str) -> Optional[dict]:
        return self._repo.find_by_email(email)


# ── Section 3: Test doubles (fakes) — made easy by DI ───────────────────────

class FakeEmailService(EmailService):
    """Records what was sent — no real network call."""
    def __init__(self):
        self.sent: list[str] = []

    def send_welcome(self, email: str) -> None:
        self.sent.append(email)


class FakeUserRepo(UserRepo):
    """In-memory repo — no real database."""
    def __init__(self, existing: list[str] = None):
        self._emails = set(existing or [])
        self._saved: list[dict] = []

    def save(self, user: dict) -> dict:
        user["id"] = len(self._saved) + 1
        self._saved.append(user)
        self._emails.add(user["email"])
        return user

    def find_by_email(self, email: str) -> Optional[dict]:
        return {"email": email} if email in self._emails else None


# ── Section 4: Manual wiring (dependency composition root) ───────────────────

def build_user_service() -> UserService:
    """
    The "composition root" — the one place where real implementations are wired.
    In FastAPI, this becomes a Depends() function.
    In Flask, it's called in create_app().
    """
    repo = InMemoryUserRepo()
    email = RealEmailService()
    return UserService(repo, email)


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Dependency Injection")
    print("=" * 55)

    print("\n--- BAD: hardcoded dependencies ---")
    bad_service = UserServiceBad()
    bad_service.register("alice@example.com")
    print("  (In tests, this sends a real email — there's no way to prevent it)")

    print("\n--- GOOD: injected dependencies (production) ---")
    prod_service = build_user_service()
    prod_service.register("bob@example.com")
    prod_service.register("carol@example.com")

    print("\n--- GOOD: injected fakes (tests) ---")
    fake_email = FakeEmailService()
    fake_repo = FakeUserRepo()
    test_service = UserService(fake_repo, fake_email)

    user = test_service.register("test@example.com")
    print(f"  Registered: {user}")
    print(f"  Welcome email recorded (not sent): {fake_email.sent}")

    # Test: duplicate registration
    try:
        test_service.register("test@example.com")
    except ValueError as e:
        print(f"  Duplicate blocked: {e}")

    # Test: no email sent for duplicate
    print(f"  Email count after duplicate attempt: {len(fake_email.sent)} (still 1)")

    print("\n--- Testing the business rule (no HTTP, no DB, no email) ---")
    # Pre-populate repo with an existing user
    repo_with_existing = FakeUserRepo(existing=["taken@example.com"])
    svc = UserService(repo_with_existing, FakeEmailService())

    try:
        svc.register("taken@example.com")
    except ValueError as e:
        print(f"  ✓ ValueError raised: {e}")

    new_user = svc.register("fresh@example.com")
    print(f"  ✓ New user registered: {new_user}")

    print("\n--- Key point ---")
    print("  UserService never changed between production and test.")
    print("  Only the injected implementations differ.")

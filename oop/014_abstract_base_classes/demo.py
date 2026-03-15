"""
Demo: Abstract Base Classes — Enforcing Interfaces in Python
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from abc import ABC, abstractmethod
from typing import Optional

# ── Section 1: Defining and using an ABC ─────────────────────────────────────

class BaseNotifier(ABC):
    """
    Interface contract: every notifier MUST implement send() and validate().
    ABCs enforce this at class definition time.
    """
    @abstractmethod
    def send(self, recipient: str, subject: str, body: str) -> bool:
        """Send a notification. Returns True if successful."""
        ...

    @abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        """Check if recipient address/number is valid."""
        ...

    def send_safe(self, recipient: str, subject: str, body: str) -> bool:
        """
        Non-abstract method — shared logic available to all subclasses.
        Validates before sending.
        """
        if not self.validate_recipient(recipient):
            print(f"  [{self.__class__.__name__}] Invalid recipient: {recipient}")
            return False
        return self.send(recipient, subject, body)


class EmailNotifier(BaseNotifier):
    """Concrete implementation: sends via email."""

    def send(self, recipient: str, subject: str, body: str) -> bool:
        print(f"  [Email] To: {recipient} | Subject: {subject}")
        print(f"          Body: {body[:50]}...")
        return True

    def validate_recipient(self, recipient: str) -> bool:
        return "@" in recipient and "." in recipient.split("@")[-1]


class SlackNotifier(BaseNotifier):
    """Concrete implementation: posts to Slack."""

    def __init__(self, channel: str):
        self.channel = channel

    def send(self, recipient: str, subject: str, body: str) -> bool:
        print(f"  [Slack #{self.channel}] @{recipient}: {subject} — {body[:40]}...")
        return True

    def validate_recipient(self, recipient: str) -> bool:
        # Slack usernames: no @ in them, no spaces
        return " " not in recipient and "@" not in recipient


class SMSNotifier(BaseNotifier):
    """Concrete implementation: sends via SMS."""

    def send(self, recipient: str, subject: str, body: str) -> bool:
        # SMS: subject is ignored, body is truncated
        sms_text = f"{body[:140]}"
        print(f"  [SMS] To: {recipient} | {sms_text}")
        return True

    def validate_recipient(self, recipient: str) -> bool:
        # Simple check: starts with +, rest are digits
        return recipient.startswith("+") and recipient[1:].isdigit()


# ── Section 2: Repository pattern — the classic ABC use case ─────────────────

class BaseUserRepository(ABC):
    """
    Defines the contract for user storage.
    Swap InMemory ↔ SQLAlchemy ↔ Redis without changing service code.
    """
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[dict]:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[dict]:
        ...

    @abstractmethod
    def save(self, user: dict) -> dict:
        ...

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        ...

    def exists(self, user_id: int) -> bool:
        """Shared logic: built on top of abstract get_by_id."""
        return self.get_by_id(user_id) is not None


class InMemoryUserRepository(BaseUserRepository):
    """Fast in-memory implementation — ideal for unit tests."""

    def __init__(self):
        self._store: dict[int, dict] = {}
        self._next_id = 1

    def get_by_id(self, user_id: int) -> Optional[dict]:
        return self._store.get(user_id)

    def get_by_email(self, email: str) -> Optional[dict]:
        return next((u for u in self._store.values() if u["email"] == email), None)

    def save(self, user: dict) -> dict:
        if "id" not in user:
            user = {**user, "id": self._next_id}
            self._next_id += 1
        self._store[user["id"]] = user
        return user

    def delete(self, user_id: int) -> bool:
        return self._store.pop(user_id, None) is not None


# ── Section 3: Service that works with ANY repo implementation ────────────────

class UserService:
    """
    Depends on BaseUserRepository, not a specific implementation.
    This is the power of ABCs — swap the concrete class without changing this.
    """
    def __init__(self, repo: BaseUserRepository):
        self.repo = repo

    def register(self, name: str, email: str) -> dict:
        existing = self.repo.get_by_email(email)
        if existing:
            raise ValueError(f"Email {email} already registered")
        return self.repo.save({"name": name, "email": email, "active": True})

    def deactivate(self, user_id: int) -> bool:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        user["active"] = False
        self.repo.save(user)
        return True


# ── Section 4: What happens with incomplete implementations ──────────────────

class IncompleteNotifier(BaseNotifier):
    """Missing validate_recipient — will fail at instantiation."""

    def send(self, recipient, subject, body):
        return True
    # forgot validate_recipient!


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Abstract Base Classes")
    print("=" * 50)

    print("\n--- Section 1: ABC can't be instantiated ---")
    try:
        n = BaseNotifier()
    except TypeError as e:
        print(f"  TypeError: {e}")

    print("\n--- Section 1b: Notifier implementations ---")
    notifiers: list[BaseNotifier] = [
        EmailNotifier(),
        SlackNotifier(channel="alerts"),
        SMSNotifier(),
    ]

    recipients = ["alice@example.com", "alice_dev", "+14155550123"]
    for notifier, recipient in zip(notifiers, recipients):
        notifier.send_safe(recipient, "Server Alert", "CPU usage exceeded 90% on prod-01")

    print("\n--- Section 1c: Invalid recipients ---")
    email = EmailNotifier()
    email.send_safe("not-an-email", "Test", "This should fail validation")
    email.send_safe("alice@example.com", "Test", "This should work fine")

    print("\n--- Section 2 & 3: Repository pattern ---")
    repo = InMemoryUserRepository()
    service = UserService(repo)

    alice = service.register("Alice", "alice@example.com")
    bob   = service.register("Bob",   "bob@example.com")
    print(f"  Registered: {alice}")
    print(f"  Registered: {bob}")

    print(f"  repo.exists(1): {repo.exists(1)}")
    print(f"  repo.exists(99): {repo.exists(99)}")

    service.deactivate(alice["id"])
    print(f"  Alice after deactivation: {repo.get_by_id(alice['id'])}")

    try:
        service.register("Alice2", "alice@example.com")  # duplicate email
    except ValueError as e:
        print(f"  Duplicate: {e}")

    print("\n--- Section 4: Incomplete subclass ---")
    try:
        bad = IncompleteNotifier()
    except TypeError as e:
        print(f"  TypeError: {e}")
        print("  (Python enforces the ABC contract at instantiation time)")

    print("\n--- issubclass and isinstance with ABC ---")
    print(f"  EmailNotifier is subclass of BaseNotifier: {issubclass(EmailNotifier, BaseNotifier)}")
    print(f"  email isinstance BaseNotifier: {isinstance(email, BaseNotifier)}")

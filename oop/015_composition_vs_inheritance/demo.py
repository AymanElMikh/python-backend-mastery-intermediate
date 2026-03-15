"""
Demo: Composition vs Inheritance — Choosing the Right Relationship
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from abc import ABC, abstractmethod

# ── Section 1: The wrong way — inheriting for code reuse ─────────────────────

class EmailSender:
    """Sends emails — a utility with its own concerns."""
    def send(self, to: str, subject: str, body: str) -> bool:
        print(f"  [Email] To: {to} | {subject}")
        return True

class Logger:
    """Logs messages — another utility."""
    def log(self, level: str, message: str) -> None:
        print(f"  [LOG {level}] {message}")


class BadUserService(EmailSender, Logger):
    """
    WRONG: inherits from EmailSender and Logger just to reuse their methods.
    BadUserService IS-A EmailSender? IS-A Logger? No — it just USES them.
    This couples the implementation, makes mocking hard, and leaks EmailSender's
    public interface onto UserService.
    """
    def register(self, name: str, email: str) -> dict:
        user = {"name": name, "email": email}
        self.log("INFO", f"Registering user: {name}")  # inherited
        self.send(email, "Welcome!", f"Hello {name}")  # inherited
        return user


# ── Section 2: The right way — composition with dependency injection ──────────

class BaseEmailSender(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> bool: ...

class BaseLogger(ABC):
    @abstractmethod
    def log(self, level: str, message: str) -> None: ...

class RealEmailSender(BaseEmailSender):
    def send(self, to: str, subject: str, body: str) -> bool:
        print(f"  [Email] To: {to} | {subject}: {body[:30]}...")
        return True

class FakeEmailSender(BaseEmailSender):
    """Use this in tests — no real emails sent."""
    def __init__(self):
        self.sent: list = []

    def send(self, to: str, subject: str, body: str) -> bool:
        self.sent.append({"to": to, "subject": subject, "body": body})
        return True

class ConsoleLogger(BaseLogger):
    def log(self, level: str, message: str) -> None:
        print(f"  [LOG {level}] {message}")

class SilentLogger(BaseLogger):
    """Use in tests — suppresses all log output."""
    def log(self, level: str, message: str) -> None:
        pass  # do nothing


class GoodUserService:
    """
    RIGHT: UserService HAS-A email sender and HAS-A logger.
    Dependencies are injected — can be real or fake.
    The public interface of UserService is CLEAN — no send/log methods leaking.
    """
    def __init__(self, email_sender: BaseEmailSender, logger: BaseLogger):
        self._email = email_sender
        self._logger = logger
        self._users: dict[int, dict] = {}
        self._next_id = 1

    def register(self, name: str, email: str) -> dict:
        self._logger.log("INFO", f"Registering user: {name}")
        user = {"id": self._next_id, "name": name, "email": email}
        self._users[self._next_id] = user
        self._next_id += 1
        self._email.send(email, "Welcome!", f"Hi {name}, welcome aboard!")
        return user

    def get(self, user_id: int) -> dict | None:
        return self._users.get(user_id)


# ── Section 3: Composition enables runtime swapping ──────────────────────────

class Order:
    """
    An Order is composed of a payment processor and a notifier.
    Both can be swapped without changing Order's code.
    """
    def __init__(self, order_id: str, amount: float):
        self.order_id = order_id
        self.amount = amount
        self._paid = False

    def process(self, payment_processor, notifier) -> bool:
        if payment_processor.charge(self.amount, self.order_id):
            self._paid = True
            notifier.notify(f"Order {self.order_id} confirmed — ${self.amount:.2f}")
            return True
        return False


class StripeProcessor:
    def charge(self, amount: float, ref: str) -> bool:
        print(f"  [Stripe] Charging ${amount:.2f} for {ref}")
        return True

class FakeProcessor:
    def charge(self, amount: float, ref: str) -> bool:
        print(f"  [Fake]   Would charge ${amount:.2f} for {ref}")
        return True


class EmailNotifyChannel:
    def notify(self, message: str) -> None:
        print(f"  [Email notification] {message}")

class LogNotifyChannel:
    def notify(self, message: str) -> None:
        print(f"  [Log notification] {message}")


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Composition vs Inheritance")
    print("=" * 50)

    print("\n--- Section 1: WRONG — inheritance for code reuse ---")
    bad_service = BadUserService()
    bad_service.register("Alice", "alice@example.com")
    # Problem: these methods are now public on BadUserService — unwanted API leak
    print(f"  has send(): {hasattr(bad_service, 'send')}")  # True — leaked!
    print(f"  has log():  {hasattr(bad_service, 'log')}")   # True — leaked!

    print("\n--- Section 2: RIGHT — composition with real dependencies ---")
    prod_service = GoodUserService(
        email_sender=RealEmailSender(),
        logger=ConsoleLogger()
    )
    user = prod_service.register("Bob", "bob@example.com")
    print(f"  Registered: {user}")
    print(f"  has send(): {hasattr(prod_service, 'send')}")  # False — clean API

    print("\n--- Section 2b: Swap to fake dependencies for testing ---")
    fake_email = FakeEmailSender()
    test_service = GoodUserService(
        email_sender=fake_email,     # no real emails sent
        logger=SilentLogger()        # no log noise in tests
    )
    carol = test_service.register("Carol", "carol@example.com")
    print(f"  Registered in test: {carol}")
    print(f"  Emails captured by fake: {fake_email.sent}")
    # Test assertions work perfectly:
    assert fake_email.sent[0]["to"] == "carol@example.com"
    assert "Welcome" in fake_email.sent[0]["subject"]
    print("  Assertions passed!")

    print("\n--- Section 3: Runtime swapping of composed objects ---")
    order = Order("ORD-001", 99.99)

    print("  Production: Stripe + Email")
    order.process(StripeProcessor(), EmailNotifyChannel())

    print("  Testing: Fake + Log")
    order2 = Order("ORD-002", 49.99)
    order2.process(FakeProcessor(), LogNotifyChannel())

    print("\n--- Summary ---")
    print("  Inheritance: use for true IS-A relationships + polymorphism")
    print("  Composition: use when class USES or HAS other objects")
    print("  Composition benefit: easier to test, swap, and reason about")

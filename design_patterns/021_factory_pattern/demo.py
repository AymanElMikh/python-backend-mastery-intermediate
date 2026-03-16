"""
Demo: Factory Pattern
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from abc import ABC, abstractmethod


# ── Section 1: The problem without a factory ──────────────────────────────────

# Imagine this scattered in 5 different files — every time you add "slack"
# you have to find and update all of them. This is the problem the factory solves.

def send_notification_bad(channel: str, message: str) -> None:
    """The wrong way — branching logic repeated everywhere."""
    if channel == "email":
        print(f"[Email] {message}")
    elif channel == "sms":
        print(f"[SMS] {message}")
    # Add Slack? You have to update every function like this.


# ── Section 2: The factory pattern ────────────────────────────────────────────

class Notifier(ABC):
    """The shared interface — every notifier must implement send()."""
    @abstractmethod
    def send(self, message: str) -> None:
        pass


class EmailNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"[Email]  Sending: {message}")


class SMSNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"[SMS]    Sending: {message}")


class PushNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"[Push]   Sending: {message}")


class SlackNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"[Slack]  Sending: {message}")


# The factory — ONE place with all the wiring.
# Adding a new channel = add one line here, zero changes elsewhere.
_NOTIFIERS = {
    "email": EmailNotifier,
    "sms": SMSNotifier,
    "push": PushNotifier,
    "slack": SlackNotifier,
}


def get_notifier(channel: str) -> Notifier:
    """Factory function — caller gets the right object without knowing the class."""
    cls = _NOTIFIERS.get(channel)
    if cls is None:
        raise ValueError(
            f"Unknown channel '{channel}'. Available: {list(_NOTIFIERS.keys())}"
        )
    return cls()


# ── Section 3: Real-world scenario — sending alerts based on user preference ──

def notify_user(user_channel: str, event: str) -> None:
    """
    This function doesn't know or care which notifier it gets.
    It just calls .send() — the factory handles the rest.
    """
    notifier = get_notifier(user_channel)
    notifier.send(f"Alert: {event}")


# ── Section 4: Common mistake — returning None instead of raising ──────────────

def get_notifier_bad(channel: str):
    """BAD: silently returns None for unknown channels."""
    notifiers = {"email": EmailNotifier}
    return notifiers.get(channel)  # Returns None for "sms" — caller will crash later


def get_notifier_good(channel: str) -> Notifier:
    """GOOD: raises immediately with a clear message."""
    notifiers = {"email": EmailNotifier, "sms": SMSNotifier}
    cls = notifiers.get(channel)
    if cls is None:
        raise ValueError(f"No notifier for channel: '{channel}'")
    return cls()


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Factory Pattern")
    print("=" * 55)

    print("\n--- Without factory (bad): logic repeated inline ---")
    send_notification_bad("email", "Your password was changed")
    send_notification_bad("sms", "Your password was changed")

    print("\n--- With factory: caller doesn't know the class ---")
    for channel in ["email", "sms", "push", "slack"]:
        notify_user(channel, "Login from new device")

    print("\n--- Factory: unknown channel raises clearly ---")
    try:
        get_notifier("fax")
    except ValueError as e:
        print(f"ValueError caught: {e}")

    print("\n--- Common mistake: returning None silently ---")
    result = get_notifier_bad("sms")
    print(f"get_notifier_bad('sms') returned: {result}")  # None — will crash at .send()
    try:
        result.send("hi")  # AttributeError: 'NoneType' has no attribute 'send'
    except AttributeError as e:
        print(f"AttributeError: {e}  ← this is why we raise instead of return None")

    print("\n--- Good factory raises immediately ---")
    try:
        get_notifier_good("fax")
    except ValueError as e:
        print(f"ValueError (clear, early): {e}")

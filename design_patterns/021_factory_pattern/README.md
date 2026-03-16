# Factory Pattern

## 🎯 Interview Question
What is the Factory pattern and when would you use it in a Python backend project?

## 💡 Short Answer (30 seconds)
The Factory pattern is a way to create objects without hardcoding which class to instantiate — you delegate that decision to a factory function or class. It's useful when the type of object you need depends on runtime data, like a request parameter or config value, and you want to keep that branching logic in one place instead of scattered everywhere.

## 🔬 Explanation
Imagine you're building a notification system. You need to send emails, SMS, and push notifications. Without a factory, every part of your code that creates a notifier has `if type == "email": ... elif type == "sms": ...` spread all over the place. When you add Slack, you have to find and update every one of those spots.

The Factory pattern centralizes that `if/elif` logic in a single function. The rest of your code just asks: "give me a notifier for 'email'" and uses it — no branching needed.

In Python, this is usually just a function or a class with a `create()` method. You don't need a complex class hierarchy. Keep it simple.

## 💻 Code Example
```python
from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass

class EmailNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"[Email] {message}")

class SMSNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"[SMS] {message}")

class PushNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"[Push] {message}")

# The factory — ONE place with the branching logic
def get_notifier(channel: str) -> Notifier:
    notifiers = {
        "email": EmailNotifier,
        "sms": SMSNotifier,
        "push": PushNotifier,
    }
    cls = notifiers.get(channel)
    if cls is None:
        raise ValueError(f"Unknown channel: {channel}")
    return cls()

# Caller doesn't care which class it gets
notifier = get_notifier("email")
notifier.send("Your order shipped!")
```

## ⚠️ Common Mistakes
1. **Putting the factory logic everywhere.** The whole point is one place. If you have `if type == "email"` in three files, you don't have a factory — you have a mess.
2. **Over-engineering with AbstractFactory.** For most backend apps, a simple dict + function is enough. You don't need a `ConcreteFactoryA` and `ConcreteFactoryB` unless you have multiple product families.
3. **Not validating the input.** If someone passes an unknown channel, raise a clear `ValueError` — don't silently return `None`.

## ✅ When to Use vs When NOT to Use
**Use when:**
- You create objects based on a string/config value (type of payment, notification channel, file parser)
- You want a single place to register and look up implementations
- You're writing a plugin system where new types need to be addable without changing callers

**Don't use when:**
- You only ever create one type of object — a factory for a single class is pointless overhead
- The logic is dead simple and only lives in one place — just instantiate directly

## 🔗 Related Concepts
- [oop/014_abstract_base_classes](../../oop/014_abstract_base_classes) — ABCs define the interface the factory guarantees
- [design_patterns/023_strategy_pattern](../023_strategy_pattern) — often paired with factory to swap algorithms
- [design_patterns/026_repository_pattern](../026_repository_pattern) — repository can use a factory internally

## 🚀 Next Step
In `python-backend-mastery`: **Abstract Factory** — creating families of related objects (e.g., a DB factory that returns different query builders for Postgres vs MySQL), and **dependency injection containers** that automate factory wiring.

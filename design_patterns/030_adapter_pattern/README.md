# Adapter Pattern

## 🎯 Interview Question
What is the Adapter pattern? Give a practical example from backend development.

## 💡 Short Answer (30 seconds)
The Adapter pattern wraps an incompatible interface so it looks like what your code expects. Think of it like a power adapter when traveling abroad — the outlet is different, the adapter makes it work without changing the outlet or your device. In backend code, a common use case: your app expects a `send(message)` method, but your third-party SMS library has `transmit(content, recipient)` — an adapter bridges the gap.

## 🔬 Explanation
Real-world backend scenario: you built your system against a `Logger` interface with a `log(level, message)` method. Now you need to integrate a third-party logging service (Datadog, Sentry, Logtail) that has a completely different API.

Instead of rewriting your code or the third-party library, you write a thin adapter class that translates your interface calls into the third-party API calls.

This is especially valuable when:
- Integrating legacy systems with a new service layer
- Wrapping a vendor SDK so you can swap providers without touching business code
- Writing tests — adapters make it easy to inject fake implementations

## 💻 Code Example
```python
from abc import ABC, abstractmethod

# Your app's expected interface
class Logger(ABC):
    @abstractmethod
    def log(self, level: str, message: str) -> None:
        pass

# A third-party library with a different interface
class DatadogClient:
    def send_event(self, event_type: str, text: str, alert_type: str) -> None:
        print(f"[Datadog] event={event_type} alert={alert_type} text={text}")

# Adapter: makes DatadogClient look like Logger
class DatadogAdapter(Logger):
    def __init__(self, client: DatadogClient):
        self._client = client

    def log(self, level: str, message: str) -> None:
        # Translate: Logger.log() → DatadogClient.send_event()
        alert_type = "error" if level == "ERROR" else "info"
        self._client.send_event(
            event_type=f"app.{level.lower()}",
            text=message,
            alert_type=alert_type
        )

# Your app code never changes — just swap the adapter
logger: Logger = DatadogAdapter(DatadogClient())
logger.log("ERROR", "Database connection failed")
logger.log("INFO", "User logged in")
```

## ⚠️ Common Mistakes
1. **Adapting too much.** An adapter should translate one interface to another, not add business logic. If your adapter is doing validation, calculations, or decisions — that logic belongs elsewhere.
2. **Not hiding the adapted object.** The whole point is to make the third-party disappear behind your interface. Don't expose the underlying `DatadogClient` through the adapter's public API.
3. **Forgetting to adapt all methods.** If your interface has 5 methods and you only adapt 3, callers who use the other 2 will get `NotImplementedError`. Always fully implement the interface.

## ✅ When to Use vs When NOT to Use
**Use when:**
- Integrating a third-party library whose API doesn't match what your code expects
- Wrapping a legacy component so new code can use it without knowing its internals
- Swapping payment providers, notification services, storage backends, etc.

**Don't use when:**
- You control both sides of the interface — just change one to match the other
- The interfaces are so different that adapting them is more code than just rewriting the integration directly
- You're adding behavior beyond translation — use Decorator for that

## 🔗 Related Concepts
- [design_patterns/024_decorator_pattern](../024_decorator_pattern) — Decorator adds behavior; Adapter changes the interface
- [oop/014_abstract_base_classes](../../oop/014_abstract_base_classes) — ABCs define the target interface the adapter implements
- [design_patterns/026_repository_pattern](../026_repository_pattern) — repositories often use adapters internally for different DB drivers

## 🚀 Next Step
In `python-backend-mastery`: **Anti-Corruption Layer (ACL)** — a more robust version of the adapter for DDD, translating between your domain model and an external system's model to prevent the external model from "bleeding" into your domain.

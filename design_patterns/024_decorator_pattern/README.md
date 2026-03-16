# Decorator Pattern (Design Pattern)

## 🎯 Interview Question
What is the Decorator design pattern, and how is it different from Python's `@decorator` syntax?

## 💡 Short Answer (30 seconds)
The Decorator design pattern wraps an object with another object that adds behavior, while keeping the same interface. Python's `@decorator` syntax is a language feature that does something similar but for functions. The design pattern is object-oriented — you wrap a class instance. The Python syntax wraps a function or method. They share the same idea (wrapping to add behavior) but are implemented differently.

## 🔬 Explanation
Classic use case: you have a `DataExporter` that writes to CSV. Later you need logging, then compression, then encryption — but not always all three. The Decorator pattern lets you stack these behaviors:

```
encrypted(compressed(logged(exporter)))
```

Each wrapper adds one responsibility and delegates everything else to the wrapped object. This is much cleaner than subclassing (`LoggedCompressedEncryptedExporter`) — which explodes combinatorially.

In Python backend work, you see this in:
- HTTP middleware stacks (each middleware wraps the next handler)
- Caching wrappers around DB repositories
- Retry wrappers around API clients

## 💻 Code Example
```python
from abc import ABC, abstractmethod

class DataExporter(ABC):
    @abstractmethod
    def export(self, data: list) -> str:
        pass

class CSVExporter(DataExporter):
    def export(self, data: list) -> str:
        return ",".join(str(x) for x in data)

class LoggingDecorator(DataExporter):
    def __init__(self, wrapped: DataExporter):
        self._wrapped = wrapped  # Holds reference to the real exporter

    def export(self, data: list) -> str:
        print(f"[LOG] Exporting {len(data)} items")
        result = self._wrapped.export(data)  # Delegate
        print(f"[LOG] Done, result length: {len(result)}")
        return result

class CachingDecorator(DataExporter):
    def __init__(self, wrapped: DataExporter):
        self._wrapped = wrapped
        self._cache = {}

    def export(self, data: list) -> str:
        key = tuple(data)
        if key not in self._cache:
            self._cache[key] = self._wrapped.export(data)
        return self._cache[key]

# Stack decorators — order matters
exporter = CachingDecorator(LoggingDecorator(CSVExporter()))
result = exporter.export([1, 2, 3])
```

## ⚠️ Common Mistakes
1. **Confusing with Python's `@decorator` syntax.** Python decorators wrap functions; the Decorator pattern wraps objects. Both "add behavior to something without changing it" but the implementation is different.
2. **Not delegating properly.** Every decorator must call `self._wrapped.method()`. Forgetting the delegate call means the original behavior disappears.
3. **Using inheritance instead.** Adding every combination as a subclass (`LoggedCachedExporter`, `CachedExporter`, etc.) is unmaintainable. Composition via Decorator scales better.

## ✅ When to Use vs When NOT to Use
**Use when:**
- You want to add optional, stackable behaviors (logging, caching, retry, auth)
- Subclassing would create a combinatorial explosion of classes
- You're building middleware or pipeline stages

**Don't use when:**
- You only need one extra behavior — simple subclassing or a plain function call is fine
- The wrapped object's interface is very large — you'd have to delegate every method
- Python's `functools.wraps` / function decorators already solve the problem

## 🔗 Related Concepts
- [python_core/001_decorators_basics](../../python_core/001_decorators_basics) — Python's `@decorator` syntax (function-level)
- [oop/015_composition_vs_inheritance](../../oop/015_composition_vs_inheritance) — Decorator is composition in action
- [design_patterns/023_strategy_pattern](../023_strategy_pattern) — Strategy swaps behavior; Decorator adds behavior

## 🚀 Next Step
In `python-backend-mastery`: **Middleware chains in ASGI/WSGI** — understanding how FastAPI/Starlette use the Decorator pattern internally to stack authentication, CORS, and rate-limiting middleware.

# Singleton Pattern

## 🎯 Interview Question
What is the Singleton pattern? How do you implement it in Python, and when is it actually useful?

## 💡 Short Answer (30 seconds)
A Singleton ensures only one instance of a class exists for the lifetime of the program. In Python, the simplest approach is to use a module-level variable or override `__new__`. It's useful for shared resources like a database connection pool or a configuration object — things where multiple instances would waste memory or cause conflicts.

## 🔬 Explanation
The classic use case: you have a `Config` class that reads from environment variables. If every module creates its own `Config()`, you're re-reading the environment on every instantiation. With a Singleton, the first call creates it; every subsequent call returns the same object.

In Python, there are three common approaches:
1. **Module-level instance** — just create it at the bottom of the module (simplest, most Pythonic)
2. **`__new__` override** — intercept object creation to return the existing instance
3. **`@lru_cache` on a factory function** — clean and thread-safe for most cases

Be careful: Singletons are easy to overuse. They create hidden global state, which makes testing harder. In most production apps, dependency injection is preferred over Singletons.

## 💻 Code Example
```python
# Approach 1: Module-level instance (most Pythonic)
# config.py
class Config:
    def __init__(self):
        self.db_url = "postgresql://localhost/mydb"
        self.debug = False

config = Config()  # One instance for the whole app

# Other files just: from config import config


# Approach 2: __new__ override
class DatabasePool:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connections = []  # Init once
        return cls._instance

pool1 = DatabasePool()
pool2 = DatabasePool()
assert pool1 is pool2  # Same object
```

## ⚠️ Common Mistakes
1. **Using Singleton for everything "shared".** Not everything shared needs a Singleton. A function parameter or dependency injection is usually cleaner and more testable.
2. **Forgetting thread safety.** If multiple threads call `__new__` simultaneously, two instances can be created. Use a lock if you need thread-safe initialization.
3. **Hard-coding in tests.** Singletons make tests bleed into each other — one test mutates the singleton, the next test sees dirty state. Always reset or mock singletons in tests.

## ✅ When to Use vs When NOT to Use
**Use when:**
- Configuration that's read once and shared across the whole app
- A connection pool or resource that's expensive to create
- A logger instance shared app-wide

**Don't use when:**
- You just want to avoid passing an argument — that's laziness, not design
- You're writing testable code that needs to inject different implementations
- The "shared" thing actually changes per request (use request-scoped state instead)

## 🔗 Related Concepts
- [python_core/001_decorators_basics](../../python_core/001_decorators_basics) — `@lru_cache` can implement a lazy singleton
- [python_core/010_functools_basics](../../python_core/010_functools_basics) — `lru_cache` under the hood
- [design_patterns/021_factory_pattern](../021_factory_pattern) — factory can return a singleton

## 🚀 Next Step
In `python-backend-mastery`: **Dependency Injection containers** (like `dependency-injector`) — a more flexible, testable alternative to singletons for managing shared resources.

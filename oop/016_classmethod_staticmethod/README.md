# @classmethod and @staticmethod — Alternative Constructors and Utilities

## 🎯 Interview Question
"What's the difference between a regular method, a `@classmethod`, and a `@staticmethod` in Python? When would you use each?"

## 💡 Short Answer (30 seconds)
A regular method receives the instance (`self`) as the first argument. A `@classmethod` receives the *class* (`cls`) instead — used for alternative constructors like `User.from_dict()` or `User.from_env()`. A `@staticmethod` receives neither — it's just a plain function that lives in the class namespace because it's logically related to the class but doesn't need access to the instance or class.

## 🔬 Explanation
**Regular method** (`self`): accesses and modifies instance state. Most methods you write.

**`@classmethod`** (`cls`): receives the class object, not an instance. Common uses:
- **Alternative constructors**: `Date.from_string("2026-03-15")` — create an instance from different input formats
- **Factory methods**: `User.create_admin(name, email)` — enforce specific setup rules
- **Accessing class-level config** without hard-coding the class name (important for subclasses)

**`@staticmethod`**: no implicit first argument. Common uses:
- **Utility functions** that belong logically to the class but don't need `self` or `cls`
- **Validation helpers**: `User.is_valid_email(email)` — doesn't need an instance
- **Pure functions** related to the domain concept

**The key distinction for `@classmethod` vs `@staticmethod`**: if you need to create an instance of the class (or need `cls` for subclass support), use `@classmethod`. If you just need a utility that lives conceptually near the class, use `@staticmethod`.

## 💻 Code Example
```python
from datetime import datetime

class User:
    def __init__(self, name: str, email: str, created_at: datetime = None):
        self.name = name
        self.email = email
        self.created_at = created_at or datetime.now()

    # @classmethod — alternative constructor
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            name=data["name"],
            email=data["email"],
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        )

    # @classmethod — factory with enforced rules
    @classmethod
    def create_guest(cls) -> "User":
        return cls(name="Guest", email="guest@anonymous.com")

    # @staticmethod — utility, needs no instance or class
    @staticmethod
    def is_valid_email(email: str) -> bool:
        return "@" in email and "." in email.split("@")[-1]

    def greet(self) -> str:  # regular method
        return f"Hi, I'm {self.name}"

user = User.from_dict({"name": "Alice", "email": "alice@example.com"})
guest = User.create_guest()
print(User.is_valid_email("bad-email"))  # False — no instance needed
```

## ⚠️ Common Mistakes

1. **Using `@staticmethod` when `@classmethod` would enable subclass support** — if `User.from_dict()` is a `@staticmethod`, it always returns a `User`. As a `@classmethod`, `AdminUser.from_dict()` returns an `AdminUser` — because `cls` is `AdminUser`. This is why most factory/constructor methods should be `@classmethod`.

2. **Using a regular method for logic that doesn't need `self`** — if a method never touches `self`, it should be `@staticmethod`. Calling `self.is_valid_email(...)` works but is misleading — readers assume it uses instance state.

3. **Putting business logic in `@staticmethod`** — static methods are for simple utilities. Complex logic that changes over time belongs in a service or module-level function, not buried in a class.

## ✅ When to Use vs When NOT to Use

**Use `@classmethod` when:**
- Creating alternative constructors (`from_dict`, `from_json`, `from_env`)
- Writing factory methods that enforce creation rules
- You need subclass-aware instantiation

**Use `@staticmethod` when:**
- The function is logically part of the class but doesn't need instance or class data
- Simple validation or transformation utilities (`is_valid_email`, `hash_password`)
- You want to call it without instantiating the class

**Use regular methods for:**
- Everything that reads or modifies `self`

## 🔗 Related Concepts
- [011_classes_and_init](../011_classes_and_init) — `__init__` is the primary constructor
- [018_dataclasses](../018_dataclasses) — `@classmethod` often pairs with `@dataclass`

## 🚀 Next Step
In `python-backend-mastery`: **`__init_subclass__` and class decorators** — automatically registering subclasses in a registry when they're defined, a pattern used by plugin systems, serialization frameworks, and ORM model discovery.

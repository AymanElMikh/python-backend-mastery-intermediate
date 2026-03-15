# Mixin Pattern — Adding Capabilities Without Deep Hierarchies

## 🎯 Interview Question
"What is a mixin in Python and when would you use one?"

## 💡 Short Answer (30 seconds)
A mixin is a class that provides methods to other classes through inheritance, but is not meant to be instantiated on its own. Unlike regular inheritance (which represents an "is-a" relationship), a mixin adds a specific capability — like serialization, logging, or validation — to any class that inherits from it, regardless of that class's type hierarchy. It's a way to share behavior across unrelated classes without creating a deep inheritance chain.

## 🔬 Explanation
Mixins sit at the intersection of inheritance and composition. They're small, focused classes that each do one thing well:

```
class User(TimestampMixin, SerializableMixin, LoggableMixin, BaseModel):
    ...
```

Each mixin adds one orthogonal capability:
- `TimestampMixin` — adds `created_at`, `updated_at` fields and `touch()` method
- `SerializableMixin` — adds `to_dict()`, `to_json()`, `from_dict()` methods
- `LoggableMixin` — adds `log_action()` with context

**Why mixins over regular inheritance:**
- A `User` class doesn't "is-a" serializable — it just *has* serialization capability
- Same mixin can be applied to `User`, `Product`, `Order` — no common parent needed
- Each mixin is independent and testable in isolation

**The rules for clean mixins:**
1. Mixin names typically end in `Mixin` by convention
2. Mixins should never be instantiated directly
3. Mixins should not call `super().__init__()` unless supporting cooperative multiple inheritance
4. Each mixin should have one responsibility

**In real projects**, mixins appear heavily in:
- Django: `LoginRequiredMixin`, `PermissionRequiredMixin` on class-based views
- Django REST Framework: `CreateModelMixin`, `ListModelMixin` on viewsets
- SQLAlchemy: timestamp mixins on ORM models
- Custom bases for audit logging, soft-delete, caching

## 💻 Code Example
```python
class TimestampMixin:
    """Adds created_at and updated_at to any model."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # cooperative MI
        from datetime import datetime
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def touch(self):
        from datetime import datetime
        self.updated_at = datetime.now()

class SerializableMixin:
    """Adds to_dict() to any class."""
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()
                if not k.startswith("_")}

class User(TimestampMixin, SerializableMixin):
    def __init__(self, name: str, email: str):
        super().__init__()  # triggers mixin __init__ via MRO
        self.name = name
        self.email = email

user = User("Alice", "alice@example.com")
print(user.to_dict())   # includes name, email, created_at, updated_at
user.touch()            # updates updated_at
```

## ⚠️ Common Mistakes

1. **Mixins with too many responsibilities** — a `UtilityMixin` with 20 methods is a sign of poor design. Each mixin should do one thing. Split into `SerializableMixin`, `LoggableMixin`, etc.

2. **Not using `super().__init__()` in cooperative mixins** — if multiple mixins each call `super().__init__()`, Python's MRO ensures all of them run in the right order. If a mixin skips `super().__init__()`, subsequent mixins in the chain are silently skipped.

3. **Using a mixin when composition would be cleaner** — for non-model classes, injecting the capability as a dependency (composition) is often cleaner than inheriting from a mixin. Mixins shine in framework contexts (Django views, ORM models) where inheritance is the natural extension mechanism.

## ✅ When to Use vs When NOT to Use

**Use mixins when:**
- You want to add the same capability to multiple unrelated classes
- You're working in a framework where inheritance is the extension mechanism (Django, SQLAlchemy)
- The capability is small, focused, and adds methods — not data/state

**Avoid mixins when:**
- The capability is complex or has significant state — use composition instead
- You're not in a framework context — a service/utility class is usually cleaner
- The mixin would override core methods of the target class in surprising ways

## 🔗 Related Concepts
- [012_inheritance_super](../012_inheritance_super) — mixins use `super()` for cooperative inheritance
- [015_composition_vs_inheritance](../015_composition_vs_inheritance) — composition is the alternative
- [014_abstract_base_classes](../014_abstract_base_classes) — mixins can define abstract methods

## 🚀 Next Step
In `python-backend-mastery`: **MRO and cooperative multiple inheritance (C3 linearization)** — exactly how Python resolves which `super().__init__()` runs and in what order when 4+ mixins are combined, and how to design mixin hierarchies that don't break.

# Properties — Controlled Attribute Access with `@property`

## 🎯 Interview Question
"What is `@property` in Python and when would you use it instead of a plain attribute?"

## 💡 Short Answer (30 seconds)
`@property` lets you expose a method as if it were an attribute — the caller writes `user.full_name` but behind the scenes, a method runs. You use it when you need computed attributes (values derived from other attributes), validation on set (reject invalid data), or to make an attribute read-only. It keeps the API clean — callers don't need to know whether they're reading a stored value or calling a computed one.

## 🔬 Explanation
`@property` comes in three parts:
- `@property` (getter) — called when you read `obj.attr`
- `@attr.setter` — called when you write `obj.attr = value`
- `@attr.deleter` — called when you `del obj.attr` (rarely used)

**When to use `@property`:**
1. **Computed values**: `full_name` from `first_name + last_name`, `age` from `birthdate`
2. **Read-only attributes**: expose data without a setter — `obj.id` can't be changed after creation
3. **Validation on assignment**: reject invalid values at the point of assignment, not later
4. **Lazy loading**: compute a value only the first time it's accessed and cache it

**The "uniform access principle"**: callers shouldn't care whether `user.age` is a stored field or a computed property. If you start with a plain attribute and later need to add validation, `@property` lets you add it without changing the caller's code at all.

In real backend code, properties appear in:
- **Model classes**: `@property full_name`, `@property is_expired`
- **Config objects**: read-only properties that validate on init
- **ORM models**: SQLAlchemy uses the descriptor protocol (which `@property` is built on) for column definitions

## 💻 Code Example
```python
class Circle:
    def __init__(self, radius: float):
        self._radius = radius  # store internally with underscore

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value < 0:
            raise ValueError(f"Radius must be non-negative, got {value}")
        self._radius = value

    @property
    def area(self) -> float:
        """Computed from radius — no setter (read-only)."""
        import math
        return math.pi * self._radius ** 2

c = Circle(5)
print(c.radius)  # 5 — calls the getter
print(c.area)    # 78.54 — computed property, no setter
c.radius = 10   # calls the setter
c.radius = -1   # raises ValueError
```

## ⚠️ Common Mistakes

1. **Storing with the same name as the property** — if your property is `radius` and you write `self.radius = value` inside `__init__`, you call the setter recursively. Use `self._radius` (with an underscore) for the backing attribute.

2. **Doing expensive computation in a getter called frequently** — if `obj.expensive_property` is called in a loop, it recalculates every time. Cache with a `_cache` attribute or use `functools.cached_property` (Python 3.8+).

3. **Using `@property` when a method name would be clearer** — `user.email` as a property is fine. But `user.send_email()` should be a method — it has side effects. Properties should feel like reading a value, not performing an action.

## ✅ When to Use vs When NOT to Use

**Use `@property` when:**
- The value is derived from other attributes (computed)
- You need read-only access (no setter)
- You need validation when a value is set
- You want to migrate a plain attribute to controlled access without breaking callers

**Avoid `@property` when:**
- The computation is expensive and called often — use a method with a clear name (`get_report()`) so callers know it's not cheap
- The attribute is truly simple with no validation or derivation — a plain attribute is cleaner
- You have side effects — use a method, not a property

## 🔗 Related Concepts
- [011_classes_and_init](../011_classes_and_init) — the backing `self._attr` is set in `__init__`
- [010_functools_basics](../../python_core/010_functools_basics) — `functools.cached_property` for lazy computed properties

## 🚀 Next Step
In `python-backend-mastery`: **Descriptors (`__get__`, `__set__`, `__delete__`)** — `@property` is built on Python's descriptor protocol. Understanding descriptors explains how SQLAlchemy columns, `@staticmethod`, `@classmethod`, and `@property` all work under the hood.

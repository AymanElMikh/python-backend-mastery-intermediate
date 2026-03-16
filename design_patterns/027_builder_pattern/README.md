# Builder Pattern

## 🎯 Interview Question
What is the Builder pattern and when is it more useful than a constructor with many arguments?

## 💡 Short Answer (30 seconds)
The Builder pattern constructs complex objects step by step. Instead of a constructor with 10 optional arguments, you chain method calls to set only what you need, then call `.build()` to get the final object. It's most useful when an object has many optional fields, some of which depend on others, or when you want to construct different "flavors" of the same object in a readable way.

## 🔬 Explanation
Imagine building an HTTP request: you need a URL, maybe headers, maybe a body, maybe query params, maybe auth. A constructor like `Request(url, headers=None, body=None, params=None, auth=None, timeout=30, retries=3)` works but is hard to read at call sites.

Builder gives you:
```python
request = (RequestBuilder("https://api.example.com/users")
    .with_auth("Bearer token123")
    .with_timeout(10)
    .with_retry(3)
    .build())
```

Each method returns `self`, enabling chaining. This is highly readable and you only specify what you actually need.

In Python, `dataclasses` with many optional fields can often replace the full Builder pattern for simple cases. Use Builder when construction involves validation, conditional logic, or multiple steps that must happen in order.

## 💻 Code Example
```python
from dataclasses import dataclass

@dataclass
class QueryConfig:
    table: str
    filters: dict
    limit: int
    offset: int
    order_by: str | None
    include_deleted: bool

class QueryBuilder:
    def __init__(self, table: str):
        self._table = table
        self._filters = {}
        self._limit = 100
        self._offset = 0
        self._order_by = None
        self._include_deleted = False

    def filter(self, **kwargs) -> "QueryBuilder":
        self._filters.update(kwargs)
        return self  # Enables chaining

    def limit(self, n: int) -> "QueryBuilder":
        self._limit = n
        return self

    def order_by(self, field: str) -> "QueryBuilder":
        self._order_by = field
        return self

    def build(self) -> QueryConfig:
        return QueryConfig(
            table=self._table,
            filters=self._filters,
            limit=self._limit,
            offset=self._offset,
            order_by=self._order_by,
            include_deleted=self._include_deleted,
        )

# Clean, readable construction
query = (QueryBuilder("users")
    .filter(is_active=True, role="admin")
    .limit(25)
    .order_by("created_at")
    .build())
```

## ⚠️ Common Mistakes
1. **Forgetting to return `self` in builder methods.** Every setter method must `return self` for chaining to work. This is the #1 bug in Builder implementations.
2. **Mutating the builder after calling `.build()`.** Once you call `.build()`, treat the builder as done. Create a new builder instance for a new object.
3. **Using Builder for simple objects.** If an object has 2-3 fields, a regular constructor or dataclass is clearer. Builder is for complex, multi-step construction.

## ✅ When to Use vs When NOT to Use
**Use when:**
- Objects have many optional parameters (5+) and different valid combinations
- Construction involves validation between fields
- You want readable, self-documenting object creation in tests and application code

**Don't use when:**
- The object is simple — a dataclass or `__init__` with defaults is fine
- You just need named arguments — Python's `**kwargs` already handles this well
- There's no combinatorial complexity — Builder adds ceremony without benefit

## 🔗 Related Concepts
- [python_core/008_type_hints](../../python_core/008_type_hints) — type hints make builder return types clear
- [oop/018_dataclasses](../../oop/018_dataclasses) — often a simpler alternative for straightforward configs
- [design_patterns/021_factory_pattern](../021_factory_pattern) — factory creates different types; builder creates one type with different configs

## 🚀 Next Step
In `python-backend-mastery`: **Fluent interfaces and query DSLs** — how SQLAlchemy's ORM uses Builder-style chaining for queries (`session.query(User).filter(...).order_by(...).limit(...)`).

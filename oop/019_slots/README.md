# `__slots__` — Reducing Memory Overhead for High-Volume Classes

## 🎯 Interview Question
"What is `__slots__` in Python and when would you use it?"

## 💡 Short Answer (30 seconds)
`__slots__` is a class-level declaration that tells Python to use a fixed set of attribute slots instead of the default per-instance `__dict__`. This reduces memory usage by 30–50% per instance because there's no dictionary overhead. You'd use it when you're creating thousands or millions of instances of a class — like parsing large datasets, processing queue messages, or building high-throughput data pipelines.

## 🔬 Explanation
By default, every Python object stores its attributes in a `__dict__` — a hash map that allows arbitrary attribute assignment. This is flexible but costs memory: a `__dict__` for a simple 3-attribute object might use 200+ bytes of overhead.

With `__slots__ = ("x", "y", "z")`, Python allocates compact fixed-size slots instead. No `__dict__` is created per instance. The memory saving is significant at scale:

- A simple 3-attribute class without slots: ~200–300 bytes per instance
- Same class with `__slots__`: ~50–100 bytes per instance

**Side effects of `__slots__`:**
- You cannot add new attributes dynamically (`obj.new_attr = x` raises `AttributeError`)
- No `__dict__` on instances (unless you explicitly add `"__dict__"` to slots)
- Inheritance works, but subclasses should also define their own `__slots__` — or the memory savings are lost

**Real-world use cases:**
- Parsing JSON/CSV with millions of rows into model objects
- Message queue consumers that instantiate thousands of event objects per second
- Time-series data points in a monitoring system
- Any class where you'll have 10,000+ instances alive at once

Python 3.10+ dataclasses support `@dataclass(slots=True)` — a clean way to combine both.

## 💻 Code Example
```python
import sys

class PointNoSlots:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class PointWithSlots:
    __slots__ = ("x", "y", "z")  # no __dict__ allocated per instance

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

p1 = PointNoSlots(1, 2, 3)
p2 = PointWithSlots(1, 2, 3)

print(sys.getsizeof(p1))           # ~48 bytes for object
print(sys.getsizeof(p1.__dict__))  # ~200+ bytes for dict overhead
print(sys.getsizeof(p2))           # ~64 bytes — more compact, no dict
# p2.__dict__  → AttributeError (no dict!)
```

## ⚠️ Common Mistakes

1. **Defining `__slots__` but not in subclasses** — if a parent has `__slots__` but a subclass doesn't define its own `__slots__`, the subclass gets a `__dict__` again. You must define `__slots__` at every level of the hierarchy to preserve the savings.

2. **Using `__slots__` for classes that need dynamic attributes** — pickling, some ORMs, and frameworks that add attributes dynamically (like SQLAlchemy) may break. Don't use slots for ORM model classes.

3. **Premature optimization** — `__slots__` adds constraint and reduces flexibility. Only reach for it when you've confirmed memory is actually the bottleneck (profiled, 10k+ instances).

## ✅ When to Use vs When NOT to Use

**Use `__slots__` when:**
- You create thousands or millions of instances
- Memory profiling shows instance `__dict__` as a bottleneck
- The set of attributes is fixed and known at class definition time

**Avoid `__slots__` when:**
- You need `__dict__` for dynamic attribute assignment
- Working with ORMs, serialization frameworks, or tools that add attributes
- You haven't profiled — don't optimize prematurely

## 🔗 Related Concepts
- [018_dataclasses](../018_dataclasses) — `@dataclass(slots=True)` combines both (Python 3.10+)
- [011_classes_and_init](../011_classes_and_init) — `__dict__` is the default attribute storage

## 🚀 Next Step
In `python-backend-mastery`: **Memory profiling with `tracemalloc` and `memory_profiler`** — identifying actual memory hotspots in production Python services, and using `weakref` for cache patterns that don't prevent garbage collection.

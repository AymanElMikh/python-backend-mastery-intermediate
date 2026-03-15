# Comprehensions — List, Dict, Set

## 🎯 Interview Question
"What are Python comprehensions and when should you use one vs a regular `for` loop?"

## 💡 Short Answer (30 seconds)
Comprehensions are a concise syntax for building collections — lists, dicts, or sets — by expressing the transformation and optional filter in a single line. Use them when you're transforming or filtering a collection into a new one and the logic fits in one readable line. Use a regular `for` loop when the logic is complex, has side effects, or needs multiple lines to stay readable.

## 🔬 Explanation
Python has three types of comprehensions:

- **List**: `[expression for item in iterable if condition]` → returns a `list`
- **Dict**: `{key: value for item in iterable if condition}` → returns a `dict`
- **Set**: `{expression for item in iterable if condition}` → returns a `set`

(There's also the generator expression `(x for x in ...)` — covered in [003_generators_yield](../003_generators_yield).)

Comprehensions are not just syntactic sugar — they're often faster than equivalent `for` loops because Python optimizes them internally.

Real backend examples you'll write constantly:
```python
# Extract IDs from query results
user_ids = [user.id for user in db_users]

# Build a lookup dict from a list
users_by_id = {user.id: user for user in db_users}

# Filter active users
active_users = [u for u in users if u.is_active]

# Transform API response fields
response = {k: v for k, v in raw_data.items() if v is not None}

# Unique tags from a list of posts
all_tags = {tag for post in posts for tag in post.tags}
```

The key rule: if you can say it in plain English in one sentence ("give me the IDs of all active users"), it probably belongs in a comprehension.

## 💻 Code Example
```python
users = [
    {"name": "Alice", "age": 30, "active": True,  "score": 95},
    {"name": "Bob",   "age": 17, "active": True,  "score": 72},
    {"name": "Carol", "age": 25, "active": False, "score": 88},
]

# List comprehension — transform
names = [u["name"] for u in users]
# ['Alice', 'Bob', 'Carol']

# List comprehension — filter + transform
adult_names = [u["name"] for u in users if u["age"] >= 18]
# ['Alice', 'Carol']

# Dict comprehension — build lookup
score_by_name = {u["name"]: u["score"] for u in users}
# {'Alice': 95, 'Bob': 72, 'Carol': 88}

# Set comprehension — unique values
active_states = {u["active"] for u in users}
# {True, False}
```

## ⚠️ Common Mistakes

1. **Nested comprehensions that are hard to read** — a comprehension with 2 loops and a condition is often clearer as a regular `for` loop. Rule of thumb: if it doesn't fit in one readable line, unroll it.

2. **Side effects inside comprehensions** — don't do `[print(x) for x in items]` just to loop. Comprehensions should produce a value, not cause side effects. Use a `for` loop for that.

3. **Using a list comprehension when a generator expression would do** — `sum([x*x for x in range(million)])` builds a million-item list just to sum it. `sum(x*x for x in range(million))` uses no extra memory.

## ✅ When to Use vs When NOT to Use

**Use comprehensions when:**
- Transforming one collection into another (map-like)
- Filtering a collection by a condition (filter-like)
- Building dicts or sets from sequences
- The logic fits in one readable expression

**Use a regular `for` loop when:**
- You need multiple statements per iteration
- You have side effects (logging, modifying external state, appending to multiple lists)
- The comprehension would need 2+ levels of nesting
- Readability suffers

## 🔗 Related Concepts
- [003_generators_yield](../003_generators_yield) — generator expressions are lazy comprehensions
- [009_iterators_iterables](../009_iterators_iterables) — comprehensions work on any iterable

## 🚀 Next Step
In `python-backend-mastery`: **`itertools` and functional programming** — `map`, `filter`, `reduce`, `itertools.chain`, `itertools.groupby` for advanced data pipeline construction without loops.

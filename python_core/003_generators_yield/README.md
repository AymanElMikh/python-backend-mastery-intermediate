# Generators — Lazy Iteration with `yield`

## 🎯 Interview Question
"What is a generator in Python and when would you use one over returning a list?"

## 💡 Short Answer (30 seconds)
A generator is a function that uses `yield` instead of `return` — it produces values one at a time, on demand, rather than building the whole collection in memory at once. You'd use one when processing large datasets (like reading a million rows from a database), streaming data, or building pipelines — anywhere that loading everything at once would be too slow or memory-intensive.

## 🔬 Explanation
When you call a regular function, it runs to completion and returns a value. When you call a generator function (one with `yield`), it returns a **generator object** immediately — without running any code yet. The code only runs when you iterate over it (with `for`, `next()`, or `list()`).

Each time `yield` is hit, the function **pauses** and hands back a value. On the next iteration, it **resumes exactly where it left off**.

Real-world uses in backend development:
- **Streaming large query results**: instead of `users = session.query(User).all()` (loads all in RAM), yield rows in batches
- **Processing CSV/log files**: read line by line instead of loading the whole file
- **Infinite sequences**: a generator can `yield` forever — useful for IDs, timestamps, event streams
- **Data pipelines**: chain generators together — each stage processes and yields to the next

The key advantage: **memory efficiency**. A generator for 10 million records uses the same memory as one for 10.

## 💻 Code Example
```python
# REGULAR function — builds the entire list in memory
def get_user_ids_list(n):
    return [i for i in range(n)]  # allocates a list of n items

# GENERATOR function — yields one at a time
def get_user_ids_gen(n):
    for i in range(n):
        yield i  # pauses here, resumes on next iteration

# The generator object is created instantly, uses almost no memory
gen = get_user_ids_gen(1_000_000)
print(next(gen))  # 0 — runs until first yield
print(next(gen))  # 1 — resumes from where it paused

# In practice: iterate with for
for user_id in get_user_ids_gen(5):
    print(user_id)  # 0, 1, 2, 3, 4

# Generator expression (like a list comp, but lazy)
squares = (x * x for x in range(10))  # note: () not []
```

## ⚠️ Common Mistakes

1. **Iterating a generator twice** — once a generator is exhausted, it's done. Calling `list(gen)` twice gives an empty list the second time. If you need to iterate multiple times, convert to a list first or recreate the generator.

2. **Confusing `yield` with `return`** — a function can have both, but `return` inside a generator raises `StopIteration` (ends the loop cleanly). It's rarely needed; just let the function end naturally.

3. **Building a list inside a generator** — `yield list_of_items` yields the whole list as one item. If you want to yield each item, use `yield from list_of_items` or loop and yield individually.

## ✅ When to Use vs When NOT to Use

**Use generators when:**
- Processing large datasets where holding everything in memory is impractical
- Building streaming pipelines (read → transform → write)
- You only need to iterate once and don't need random access
- You want to represent an infinite or lazily-computed sequence

**Avoid generators when:**
- You need to iterate the data multiple times — use a list
- You need `len()`, indexing (`data[5]`), or slicing — generators don't support these
- The dataset is small — the extra complexity isn't worth it

## 🔗 Related Concepts
- [009_iterators_iterables](../009_iterators_iterables) — generators implement the iterator protocol
- [006_comprehensions](../006_comprehensions) — generator expressions vs list comprehensions

## 🚀 Next Step
In `python-backend-mastery`: **Async generators** — using `async def` with `yield` for streaming async data (e.g., reading from an async database cursor or SSE streams), and `yield from` for generator delegation.

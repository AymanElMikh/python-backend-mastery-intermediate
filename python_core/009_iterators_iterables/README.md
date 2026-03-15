# Iterators vs Iterables

## 🎯 Interview Question
"What's the difference between an iterable and an iterator in Python? Can you walk me through what happens when you write `for x in my_list`?"

## 💡 Short Answer (30 seconds)
An **iterable** is any object you can loop over — it has `__iter__()` which returns an iterator. An **iterator** is the object that does the actual looping — it has `__next__()` which returns the next value or raises `StopIteration` when done. Lists, dicts, and strings are iterables but not iterators. When you write `for x in my_list`, Python calls `iter(my_list)` to get an iterator, then calls `next()` repeatedly until `StopIteration`.

## 🔬 Explanation
The two protocols:

**Iterable protocol**: object has `__iter__()` → returns an iterator
**Iterator protocol**: object has `__next__()` → returns next value or raises `StopIteration`, AND `__iter__()` returns `self`

**Why iterators also implement `__iter__`**: this lets you use an iterator directly in a `for` loop — `for x in my_iterator:` works because `iter(iterator)` just returns the same iterator.

**What `for` actually does:**
```python
for x in my_list:
    print(x)
# is exactly equivalent to:
_iter = iter(my_list)          # calls my_list.__iter__()
while True:
    try:
        x = next(_iter)        # calls _iter.__next__()
        print(x)
    except StopIteration:
        break
```

**Key difference from generators**: generators are iterators (they implement both protocols automatically via `yield`). All generators are iterators, but not all iterators are generators.

**Real-world use**: understanding this lets you write custom iterable objects (like a paginated API client that auto-fetches next pages), use `itertools` effectively, and understand why a `for` loop exhausts a file object but not a list.

## 💻 Code Example
```python
# Lists are iterable but NOT iterators
my_list = [1, 2, 3]
print(hasattr(my_list, '__iter__'))   # True — it's iterable
print(hasattr(my_list, '__next__'))   # False — not an iterator

# Get an iterator from a list
iterator = iter(my_list)
print(next(iterator))  # 1
print(next(iterator))  # 2
print(next(iterator))  # 3
# next(iterator)        # StopIteration!

# Custom iterable class
class CountUp:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def __iter__(self):
        return CountUpIterator(self.start, self.stop)

class CountUpIterator:
    def __init__(self, current, stop):
        self.current = current
        self.stop = stop

    def __iter__(self):
        return self  # iterators must return themselves

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += 1
        return value

for n in CountUp(1, 4):
    print(n)  # 1, 2, 3
```

## ⚠️ Common Mistakes

1. **Assuming an iterator can be reset** — once an iterator is exhausted, it's done. `list(my_iter)` twice gives `[]` the second time. An iterable like a list can produce a fresh iterator any number of times.

2. **Confusing iterables and iterators** — a list is iterable (can be passed to `for`) but is not an iterator (you can't call `next()` directly on it). Calling `next([1,2,3])` raises `TypeError`.

3. **Forgetting `__iter__` returning `self` in iterator classes** — if your iterator's `__iter__` doesn't return `self`, it can't be used in a `for` loop or with `itertools`.

## ✅ When to Use vs When NOT to Use

**Write custom iterators/iterables when:**
- You have a data source that's naturally sequential (database cursor, API pagination, file)
- You want lazy evaluation — compute the next item only when asked
- You're building a library or framework and want your objects to work naturally in `for` loops

**Don't write classes when:**
- A generator function does the same job with much less code (it usually does)
- You just need to transform or filter an existing collection — use comprehensions or `itertools`

## 🔗 Related Concepts
- [003_generators_yield](../003_generators_yield) — generators are iterators
- [006_comprehensions](../006_comprehensions) — comprehensions use the iterator protocol internally
- [010_functools_basics](../010_functools_basics) — `itertools` complements iterators

## 🚀 Next Step
In `python-backend-mastery`: **`itertools` deep dive** — `chain`, `groupby`, `islice`, `tee`, `product` for building efficient data pipelines; also `__getitem__`-based iteration and sequence protocol.

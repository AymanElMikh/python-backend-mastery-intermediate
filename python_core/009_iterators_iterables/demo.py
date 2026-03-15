"""
Demo: Iterators vs Iterables
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

# ── Section 1: What makes something iterable vs an iterator ──────────────────

def check_protocols(obj, name):
    has_iter = hasattr(obj, '__iter__')
    has_next = hasattr(obj, '__next__')
    kind = "iterator" if (has_iter and has_next) else ("iterable" if has_iter else "neither")
    print(f"  {name:20s} __iter__={has_iter}, __next__={has_next}  → {kind}")


# ── Section 2: How `for` works under the hood ─────────────────────────────────

def manual_for_loop(iterable):
    """Manually implement what `for x in iterable` does."""
    results = []
    _iter = iter(iterable)          # calls __iter__()
    while True:
        try:
            value = next(_iter)     # calls __next__()
            results.append(value)
        except StopIteration:       # raised when exhausted
            break
    return results


# ── Section 3: Custom iterable — a real-world pattern ────────────────────────

class PaginatedResults:
    """
    Simulates paginated API results.
    Real use case: auto-fetching next pages when iterating over results.
    """
    def __init__(self, data: list, page_size: int = 3):
        self.data = data
        self.page_size = page_size

    def __iter__(self):
        # Each call to __iter__ returns a fresh iterator
        return PaginatedIterator(self.data, self.page_size)

    def __len__(self):
        return len(self.data)


class PaginatedIterator:
    def __init__(self, data: list, page_size: int):
        self.data = data
        self.page_size = page_size
        self.index = 0

    def __iter__(self):
        return self  # iterators must return self

    def __next__(self):
        if self.index >= len(self.data):
            raise StopIteration
        # In a real paginated API, you'd fetch the next page here
        value = self.data[self.index]
        self.index += 1
        return value


# ── Section 4: Generator shortcut — same thing with less code ────────────────

def paginated_results_gen(data: list, page_size: int = 3):
    """Same as PaginatedResults but as a generator — much simpler."""
    for item in data:
        yield item


# ── Section 5: Iterator exhaustion — common mistake ──────────────────────────

def show_exhaustion():
    my_list = [10, 20, 30]
    my_iterator = iter(my_list)  # iterator from a list

    print("  First pass through list (iterable — fresh each time):")
    for x in my_list:
        print(f"    {x}", end=" ")
    print()
    print("  Second pass through list:")
    for x in my_list:
        print(f"    {x}", end=" ")
    print()

    print("  First pass through iterator:")
    for x in my_iterator:
        print(f"    {x}", end=" ")
    print()
    print("  Second pass through iterator (exhausted):")
    for x in my_iterator:
        print(f"    {x}", end=" ")
    print("  (nothing — iterator is done)")

    print("\n  Fix: call iter() again to get a fresh iterator")
    my_iterator = iter(my_list)  # create a new one
    for x in my_iterator:
        print(f"    {x}", end=" ")
    print()


# ── Section 6: Built-in functions that use the iterator protocol ──────────────

def show_builtin_usage():
    data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]

    # These all consume iterators one item at a time:
    print(f"  sum:  {sum(data)}")
    print(f"  max:  {max(data)}")
    print(f"  min:  {min(data)}")
    print(f"  list: {list(x * 2 for x in data)}")  # consumes generator

    # zip() and enumerate() return iterators
    names = ["Alice", "Bob", "Carol"]
    scores = [95, 72, 88]

    zipped = zip(names, scores)
    print(f"  zip is an iterator: {hasattr(zipped, '__next__')}")
    for name, score in zipped:
        print(f"    {name}: {score}")

    for i, name in enumerate(names, start=1):
        print(f"    {i}. {name}")


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Iterators vs Iterables")
    print("=" * 50)

    print("\n--- Section 1: Protocols check ---")
    check_protocols([1, 2, 3],       "list")
    check_protocols((1, 2, 3),       "tuple")
    check_protocols({1, 2, 3},       "set")
    check_protocols({"a": 1},        "dict")
    check_protocols("hello",         "str")
    check_protocols(iter([1, 2, 3]), "iter(list)")
    check_protocols((x for x in []), "generator")
    check_protocols(range(5),        "range")

    print("\n--- Section 2: Manual for loop ---")
    result = manual_for_loop([10, 20, 30])
    print(f"  manual_for_loop([10,20,30]) = {result}")

    print("\n--- Section 3: Custom iterable (PaginatedResults) ---")
    api_data = list(range(1, 8))  # items 1-7
    results = PaginatedResults(api_data, page_size=3)
    print(f"  Data: {api_data}")
    print("  First iteration:")
    for item in results:
        print(f"    item: {item}")
    print("  Second iteration (fresh — PaginatedResults is reusable):")
    for item in results:
        print(f"    item: {item}")

    print("\n--- Section 4: Generator equivalent ---")
    print("  Generator (same output, much less code):")
    for item in paginated_results_gen(api_data):
        print(f"    item: {item}")

    print("\n--- Section 5: Iterator exhaustion ---")
    show_exhaustion()

    print("\n--- Section 6: Built-ins using iterator protocol ---")
    show_builtin_usage()

    print("\n--- next() with a default ---")
    # next() accepts a default to avoid StopIteration
    empty_iter = iter([])
    value = next(empty_iter, "nothing here")
    print(f"  next(empty_iter, 'nothing here') = '{value}'")

    first_even = next((x for x in range(100) if x % 2 == 0 and x > 10), None)
    print(f"  First even > 10: {first_even}")

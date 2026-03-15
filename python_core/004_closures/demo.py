"""
Demo: Closures — Functions That Remember
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

# ── Section 1: What a closure is ─────────────────────────────────────────────

def make_greeting(greeting_word):
    """Outer function — defines the 'greeting_word' variable."""
    def greet(name):
        # 'greeting_word' is captured from the enclosing scope
        return f"{greeting_word}, {name}!"
    return greet  # return the inner function (not a call to it)

# Each call to make_greeting creates a new closure
say_hello = make_greeting("Hello")
say_hi = make_greeting("Hi")
say_hola = make_greeting("Hola")


# ── Section 2: Real-world use — factory functions ─────────────────────────────

def make_validator(min_len, max_len, field_name):
    """Creates a validation function pre-configured for a specific field."""
    def validate(value):
        if not isinstance(value, str):
            return f"{field_name}: must be a string"
        if len(value) < min_len:
            return f"{field_name}: too short (min {min_len} chars)"
        if len(value) > max_len:
            return f"{field_name}: too long (max {max_len} chars)"
        return None  # None means valid
    return validate

# Build validators once, use everywhere
validate_username = make_validator(3, 20, "username")
validate_bio = make_validator(0, 500, "bio")


# ── Section 3: Closure with mutable state (counter) ──────────────────────────

def make_counter(start=0):
    """A simple counter using closure state — no class needed."""
    count = [start]  # use a list so we can mutate it without `nonlocal`

    def increment(by=1):
        count[0] += by
        return count[0]

    def reset():
        count[0] = start
        return count[0]

    def current():
        return count[0]

    # Return multiple functions that share the same closure
    return increment, reset, current


# ── Section 4: The loop closure trap — common mistake ────────────────────────

def show_loop_trap():
    """Demonstrates the classic 'loop variable capture' bug."""

    # WRONG: all functions share the same 'i' variable
    # By the time they run, the loop is done and i == 4
    wrong_funcs = []
    for i in range(5):
        wrong_funcs.append(lambda: i)  # captures i by reference, not by value

    # RIGHT: use a default argument to capture current value of i
    right_funcs = []
    for i in range(5):
        right_funcs.append(lambda i=i: i)  # i=i binds current value

    return wrong_funcs, right_funcs


# ── Section 5: nonlocal — reassigning a closed-over variable ─────────────────

def make_accumulator():
    """
    Shows nonlocal — needed when reassigning (not just mutating) outer var.
    """
    total = 0

    def add(amount):
        nonlocal total  # tells Python: 'total' is from the enclosing scope
        total += amount  # this is reassignment — needs nonlocal
        return total

    return add


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Closures — Functions That Remember")
    print("=" * 50)

    print("\n--- Section 1: Basic closure ---")
    print(f"  say_hello('Alice') = '{say_hello('Alice')}'")
    print(f"  say_hi('Bob')      = '{say_hi('Bob')}'")
    print(f"  say_hola('Carlos') = '{say_hola('Carlos')}'")

    # Inspect what's in the closure
    print(f"\n  say_hello captures: {say_hello.__closure__[0].cell_contents!r}")
    print(f"  say_hi captures:    {say_hi.__closure__[0].cell_contents!r}")

    print("\n--- Section 2: Factory functions (validators) ---")
    tests = [
        ("alice", validate_username),
        ("ab", validate_username),          # too short
        ("x" * 25, validate_username),      # too long
        ("I love Python!", validate_bio),
    ]
    for value, validator in tests:
        error = validator(value)
        display = value if len(value) <= 20 else value[:17] + "..."
        status = f"ERROR: {error}" if error else "OK"
        print(f"  validate('{display}') → {status}")

    print("\n--- Section 3: Counter with closure state ---")
    inc, reset, current = make_counter(start=10)
    print(f"  Starting at: {current()}")
    print(f"  +1 → {inc()}")
    print(f"  +1 → {inc()}")
    print(f"  +5 → {inc(5)}")
    print(f"  reset → {reset()}")
    print(f"  current: {current()}")

    print("\n--- Section 4: Loop closure trap ---")
    wrong, right = show_loop_trap()
    print("  WRONG (all return same value — loop var's final value):")
    print(f"  {[f() for f in wrong]}")
    print("  RIGHT (each captures its own value):")
    print(f"  {[f() for f in right]}")

    print("\n--- Section 5: nonlocal ---")
    acc = make_accumulator()
    print(f"  acc(10) = {acc(10)}")
    print(f"  acc(20) = {acc(20)}")
    print(f"  acc(5)  = {acc(5)}")

    print("\n--- Closures vs class comparison ---")
    # Closure approach
    def make_adder(n):
        def add(x):
            return x + n
        return add

    # Equivalent class approach
    class Adder:
        def __init__(self, n):
            self.n = n
        def __call__(self, x):
            return x + self.n

    add5_closure = make_adder(5)
    add5_class = Adder(5)
    print(f"  Closure: add5(3) = {add5_closure(3)}")
    print(f"  Class:   add5(3) = {add5_class(3)}")
    print("  Both work — use closure for simple cases, class when state grows")

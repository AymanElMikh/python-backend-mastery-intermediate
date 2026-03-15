"""
Demo: Decorators — How and Why
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import functools
import time

# ── Section 1: Basic decorator — the pattern to memorize ──────────────────────

def timer(func):
    """Measures how long a function takes to run."""
    @functools.wraps(func)  # keeps func.__name__ and func.__doc__ intact
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  [{func.__name__}] took {elapsed:.4f}s")
        return result
    return wrapper


@timer
def slow_query(user_id):
    """Simulates a slow database query."""
    time.sleep(0.05)
    return {"id": user_id, "name": "Alice"}


# ── Section 2: A real-world scenario — logging decorator ─────────────────────

def log_call(func):
    """Logs every call to a function with its arguments."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"  Calling {func.__name__}({signature})")
        result = func(*args, **kwargs)
        print(f"  {func.__name__} returned {result!r}")
        return result
    return wrapper


@log_call
def create_order(item, quantity=1):
    return {"item": item, "quantity": quantity, "status": "pending"}


# ── Section 3: Stacking decorators ────────────────────────────────────────────

# You can stack multiple decorators — they apply bottom-up
# @timer runs first (outermost), then @log_call, then the real function

@timer
@log_call
def process_payment(order_id, amount):
    time.sleep(0.02)
    return f"Payment {order_id} of ${amount} processed"


# ── Section 4: The common mistake — and the fix ───────────────────────────────

# WRONG: forgetting functools.wraps
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper  # wrapper.__name__ is "wrapper", not the original name

# RIGHT: always use functools.wraps
def good_decorator(func):
    @functools.wraps(func)  # preserves __name__, __doc__, __module__, etc.
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_decorator
def my_function_bad():
    """Does something important."""
    pass

@good_decorator
def my_function_good():
    """Does something important."""
    pass


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Decorators — How and Why")
    print("=" * 50)

    print("\n--- Section 1: timer decorator ---")
    user = slow_query(42)
    print(f"  Result: {user}")

    print("\n--- Section 2: log_call decorator ---")
    order = create_order("laptop", quantity=2)

    print("\n--- Section 3: stacked decorators (@timer + @log_call) ---")
    result = process_payment("ORD-123", 299.99)

    print("\n--- Section 4: why functools.wraps matters ---")
    print(f"  Without @wraps: function name = '{my_function_bad.__name__}'")
    print(f"  With    @wraps: function name = '{my_function_good.__name__}'")
    print(f"  Without @wraps: docstring     = '{my_function_bad.__doc__}'")
    print(f"  With    @wraps: docstring     = '{my_function_good.__doc__}'")

    print("\n--- Proof that @decorator is just syntactic sugar ---")
    def shout(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result.upper()
        return wrapper

    def greet(name):
        return f"hello, {name}"

    # These two are identical:
    decorated_v1 = shout(greet)           # explicit
    @shout                                 # syntactic sugar
    def greet_v2(name):
        return f"hello, {name}"

    print(f"  shout(greet)('world')  → '{decorated_v1('world')}'")
    print(f"  @shout greet_v2('world') → '{greet_v2('world')}'")

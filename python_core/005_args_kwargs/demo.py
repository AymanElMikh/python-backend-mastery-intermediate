"""
Demo: *args and **kwargs — Flexible Function Signatures
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import functools

# ── Section 1: *args — variable positional arguments ─────────────────────────

def total(*numbers):
    """Accepts any number of numbers and sums them."""
    # numbers is a tuple inside the function
    return sum(numbers)

def log_event(event_type, *messages):
    """First arg is required, rest are variadic."""
    combined = " | ".join(str(m) for m in messages)
    return f"[{event_type.upper()}] {combined}"


# ── Section 2: **kwargs — variable keyword arguments ─────────────────────────

def create_user(**fields):
    """Build a user dict from any keyword arguments."""
    # kwargs is a regular dict inside the function
    required = {"name", "email"}
    missing = required - set(fields.keys())
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    return {"id": 1, **fields}  # ** unpacking merges dicts


def build_query(table, **conditions):
    """Simulate a dynamic query builder."""
    where_parts = [f"{col}={val!r}" for col, val in conditions.items()]
    where = " AND ".join(where_parts) if where_parts else "1=1"
    return f"SELECT * FROM {table} WHERE {where}"


# ── Section 3: Combined — the decorator pattern ───────────────────────────────

def retry(max_attempts=3):
    """Decorator factory — the wrapper uses *args/**kwargs to wrap any function."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"  Attempt {attempt} failed: {e}. Retrying...")
        return wrapper
    return decorator

call_count = 0

@retry(max_attempts=3)
def unstable_api_call(endpoint, timeout=5):
    """Simulates a flaky API call that succeeds on the 3rd try."""
    global call_count
    call_count += 1
    if call_count < 3:
        raise ConnectionError(f"Connection failed to {endpoint}")
    return {"status": "ok", "data": [1, 2, 3]}


# ── Section 4: Unpacking — * and ** in function calls ────────────────────────

def greet(first_name, last_name, title=""):
    prefix = f"{title} " if title else ""
    return f"Hello, {prefix}{first_name} {last_name}!"

# Instead of: greet(user[0], user[1])
# Use unpacking:

user_info = ["Jane", "Doe"]
user_details = {"title": "Dr."}


# ── Section 5: Common mistake — parameter order ───────────────────────────────

def right_order(regular, *args, keyword_only, **kwargs):
    """Correct order: regular → *args → keyword-only → **kwargs"""
    return {
        "regular": regular,
        "args": args,
        "keyword_only": keyword_only,
        "kwargs": kwargs
    }

# This would be a SyntaxError:
# def wrong_order(**kwargs, *args):  # SyntaxError
#     pass


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: *args and **kwargs")
    print("=" * 50)

    print("\n--- Section 1: *args ---")
    print(f"  total(1, 2, 3)        = {total(1, 2, 3)}")
    print(f"  total(10, 20)         = {total(10, 20)}")
    print(f"  total()               = {total()}")
    print(f"  total(1,2,3,4,5,6,7)  = {total(1,2,3,4,5,6,7)}")
    print()
    print(f"  {log_event('error', 'DB timeout', 'host=db-01', 'retry=3')}")
    print(f"  {log_event('info', 'Server started')}")

    print("\n--- Section 2: **kwargs ---")
    user = create_user(name="Alice", email="alice@example.com", role="admin")
    print(f"  create_user(name=...) = {user}")

    q1 = build_query("users")
    q2 = build_query("users", role="admin", active=True)
    q3 = build_query("orders", status="pending", user_id=42)
    print(f"  {q1}")
    print(f"  {q2}")
    print(f"  {q3}")

    print("\n--- Section 3: *args/**kwargs in decorator ---")
    global call_count
    call_count = 0
    result = unstable_api_call("/api/users", timeout=10)
    print(f"  Success after retries: {result}")

    print("\n--- Section 4: Unpacking in function calls ---")
    # Unpack list as positional args
    print(f"  greet(*{user_info}) = '{greet(*user_info)}'")

    # Unpack dict as keyword args
    print(f"  greet('Jane', 'Doe', **{user_details}) = '{greet('Jane', 'Doe', **user_details)}'")

    # Combine both
    all_args = ["Jane", "Doe"]
    all_kwargs = {"title": "Prof."}
    print(f"  greet(*args, **kwargs) = '{greet(*all_args, **all_kwargs)}'")

    # Useful for dict merging (Python 3.9+ also has | but ** works everywhere)
    defaults = {"timeout": 30, "retries": 3, "verify_ssl": True}
    overrides = {"timeout": 5, "debug": True}
    merged = {**defaults, **overrides}  # overrides wins on conflicts
    print(f"\n  Dict merge with **: {merged}")

    print("\n--- Section 5: Correct parameter order ---")
    result = right_order("hello", 1, 2, 3, keyword_only="required", extra="yes", more=42)
    for k, v in result.items():
        print(f"  {k}: {v}")

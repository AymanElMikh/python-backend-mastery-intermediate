"""
Demo: Type Hints — Annotations in Practice
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from typing import Optional, Union, Callable, Any
from datetime import datetime

# ── Section 1: Basic annotations ──────────────────────────────────────────────

def greet(name: str, times: int = 1) -> str:
    """Basic parameter and return type annotations."""
    return (f"Hello, {name}! " * times).strip()


def add(a: int, b: int) -> int:
    return a + b


# ── Section 2: Collection types ───────────────────────────────────────────────

# Python 3.9+ — use built-in generics: list[], dict[], tuple[], set[]
# Python 3.8 — use from typing import List, Dict, Tuple, Set

def get_names(users: list[dict]) -> list[str]:
    """Extract names from a list of user dicts."""
    return [u["name"] for u in users]


def build_index(items: list[str]) -> dict[str, int]:
    """Build a word → position index."""
    return {item: i for i, item in enumerate(items)}


def get_coordinates() -> tuple[float, float]:
    """Return lat, lon as a fixed-size tuple."""
    return (48.8566, 2.3522)


# ── Section 3: Optional — values that might be None ──────────────────────────

def find_user_by_email(email: str, users: list[dict]) -> Optional[dict]:
    """Returns a user or None if not found."""
    for user in users:
        if user.get("email") == email:
            return user
    return None  # explicitly return None when not found


def get_display_name(user: dict) -> str:
    """Show how to handle Optional return values correctly."""
    nickname: Optional[str] = user.get("nickname")  # might be None

    # WRONG: nickname.upper()  →  AttributeError if nickname is None
    # RIGHT: check before using
    if nickname is not None:
        return nickname
    return user["name"]  # fallback


# ── Section 4: Union — value can be one of several types ─────────────────────

# Python 3.10+ syntax: str | int | None
# Python 3.9 and below: Union[str, int, None]

def parse_user_id(raw: Union[str, int]) -> int:
    """Accept id as either string or int (common in API inputs)."""
    if isinstance(raw, str):
        return int(raw)
    return raw


def format_date(value: Union[str, datetime, None]) -> str:
    """Handle multiple input types gracefully."""
    if value is None:
        return "N/A"
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime("%Y-%m-%d")


# ── Section 5: Callable — annotating function arguments ──────────────────────

def apply_to_all(items: list[int], transform: Callable[[int], int]) -> list[int]:
    """Accepts a function as an argument — annotate with Callable."""
    return [transform(item) for item in items]


def run_with_retry(fn: Callable[[], Any], max_retries: int = 3) -> Any:
    """Retry any zero-argument callable."""
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"  Retry {attempt + 1}: {e}")


# ── Section 6: None return and NoReturn ──────────────────────────────────────

def log(message: str, level: str = "INFO") -> None:
    """-> None: this function has no return value."""
    print(f"  [{level}] {message}")


# ── Section 7: Common mistake — Optional not handled ─────────────────────────

def show_optional_mistake():
    users = [{"name": "Alice", "email": "alice@test.com"}]

    # WRONG: don't call methods directly on Optional return
    user = find_user_by_email("missing@test.com", users)
    # user_name = user["name"]  # KeyError / TypeError if user is None!

    # RIGHT: check first
    if user is not None:
        print(f"  Found: {user['name']}")
    else:
        print("  User not found — handled gracefully")

    # Also right: use walrus operator (Python 3.8+)
    if (found := find_user_by_email("alice@test.com", users)) is not None:
        print(f"  Found with walrus: {found['name']}")


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Type Hints — Annotations in Practice")
    print("=" * 50)

    print("\n--- Section 1: Basic annotations ---")
    print(f"  greet('Alice') = '{greet('Alice')}'")
    print(f"  greet('Bob', 3) = '{greet('Bob', 3)}'")
    print(f"  add(3, 4) = {add(3, 4)}")

    print("\n--- Section 2: Collection types ---")
    users = [
        {"name": "Alice", "email": "alice@test.com"},
        {"name": "Bob",   "email": "bob@test.com"},
    ]
    print(f"  get_names: {get_names(users)}")
    print(f"  build_index: {build_index(['apple', 'banana', 'cherry'])}")
    lat, lon = get_coordinates()
    print(f"  coordinates: lat={lat}, lon={lon}")

    print("\n--- Section 3: Optional ---")
    found = find_user_by_email("alice@test.com", users)
    missing = find_user_by_email("x@test.com", users)
    print(f"  find alice: {found}")
    print(f"  find missing: {missing}")

    user_with_nick = {"name": "Alice", "nickname": "ali"}
    user_without = {"name": "Bob"}
    print(f"  display name (has nick): {get_display_name(user_with_nick)}")
    print(f"  display name (no nick):  {get_display_name(user_without)}")

    print("\n--- Section 4: Union ---")
    print(f"  parse_user_id('42') = {parse_user_id('42')}")
    print(f"  parse_user_id(42) = {parse_user_id(42)}")
    print(f"  format_date(None) = {format_date(None)}")
    print(f"  format_date('2026-03-15') = {format_date('2026-03-15')}")
    print(f"  format_date(datetime.now()) = {format_date(datetime.now())}")

    print("\n--- Section 5: Callable ---")
    numbers = [1, 2, 3, 4, 5]
    doubled = apply_to_all(numbers, lambda x: x * 2)
    squared = apply_to_all(numbers, lambda x: x ** 2)
    print(f"  doubled: {doubled}")
    print(f"  squared: {squared}")

    attempt_count = [0]
    def flaky():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise ConnectionError("not ready yet")
        return "success!"

    result = run_with_retry(flaky)
    print(f"  run_with_retry result: {result}")

    print("\n--- Section 6: -> None ---")
    log("Server started", level="INFO")
    log("High memory usage", level="WARN")

    print("\n--- Section 7: Handling Optional correctly ---")
    show_optional_mistake()

    print("\n--- Type hints at runtime (they're just metadata) ---")
    # Type hints don't enforce at runtime — Python doesn't check them
    result = add("hello", " world")  # type: ignore — this actually runs!
    print(f"  add('hello', ' world') = '{result}'  (runtime doesn't check types)")
    print("  → Use mypy or Pyright to catch these errors BEFORE runtime")

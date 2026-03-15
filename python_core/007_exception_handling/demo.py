"""
Demo: Exception Handling Patterns
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import traceback

# ── Section 1: try/except/else/finally anatomy ───────────────────────────────

def divide(a, b):
    """Shows all four clauses of try/except."""
    try:
        result = a / b          # might raise ZeroDivisionError
    except ZeroDivisionError:
        print("  [except]  Can't divide by zero!")
        return None
    except TypeError as e:
        print(f"  [except]  Wrong types: {e}")
        return None
    else:
        # Runs ONLY if no exception occurred — often forgotten!
        print(f"  [else]    Success: {a} / {b} = {result}")
        return result
    finally:
        # Always runs — use for cleanup (close file, release lock, etc.)
        print(f"  [finally] Done with divide({a}, {b})")


# ── Section 2: Custom exception hierarchy ────────────────────────────────────

class AppError(Exception):
    """Base exception for the entire application."""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code  # machine-readable error code

    def __str__(self):
        base = super().__str__()
        return f"{base} (code={self.code})" if self.code else base


class NotFoundError(AppError):
    """Resource does not exist."""
    pass


class ValidationError(AppError):
    """Input data is invalid."""
    def __init__(self, field, message):
        super().__init__(f"'{field}': {message}", code="VALIDATION_ERROR")
        self.field = field


class ConflictError(AppError):
    """Resource already exists or state conflict."""
    pass


class AuthError(AppError):
    """Authentication or authorization failure."""
    pass


# ── Section 3: Service layer — raises specific exceptions ─────────────────────

# Fake database
_users = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
    2: {"id": 2, "name": "Bob",   "email": "bob@example.com",   "active": False},
}

def get_user(user_id: int) -> dict:
    if not isinstance(user_id, int):
        raise ValidationError("user_id", f"must be int, got {type(user_id).__name__}")
    if user_id <= 0:
        raise ValidationError("user_id", "must be a positive integer")
    user = _users.get(user_id)
    if user is None:
        raise NotFoundError(f"User with id={user_id} not found", code="USER_NOT_FOUND")
    return user


def create_user(name: str, email: str) -> dict:
    if not name or not name.strip():
        raise ValidationError("name", "cannot be empty")
    if "@" not in email:
        raise ValidationError("email", "must be a valid email address")
    # Check for duplicate
    for u in _users.values():
        if u["email"] == email:
            raise ConflictError(f"Email '{email}' is already registered", code="DUPLICATE_EMAIL")
    new_id = max(_users) + 1
    new_user = {"id": new_id, "name": name, "email": email, "active": True}
    _users[new_id] = new_user
    return new_user


# ── Section 4: API layer — catches exceptions and returns responses ───────────

def handle_request(action, *args, **kwargs):
    """Simulates a FastAPI/Flask error handler — catches app errors."""
    try:
        result = action(*args, **kwargs)
        return {"status": 200, "data": result}
    except ValidationError as e:
        return {"status": 400, "error": str(e), "field": e.field}
    except NotFoundError as e:
        return {"status": 404, "error": str(e), "code": e.code}
    except ConflictError as e:
        return {"status": 409, "error": str(e), "code": e.code}
    except AuthError as e:
        return {"status": 401, "error": str(e)}
    except AppError as e:
        return {"status": 500, "error": f"Unexpected error: {e}"}


# ── Section 5: raise ... from ... — chaining exceptions ──────────────────────

def load_config(key):
    """Shows raise X from Y — preserves original exception as context."""
    raw_config = {"port": "not_a_number", "debug": "true"}
    try:
        return int(raw_config[key])
    except KeyError as e:
        raise AppError(f"Config key '{key}' not found") from e
    except ValueError as e:
        raise AppError(f"Config key '{key}' has invalid value: {raw_config[key]!r}") from e


# ── Section 6: Common mistakes ────────────────────────────────────────────────

def show_bare_except_problem():
    """WRONG: bare except swallows bugs."""
    # This catches EVERYTHING — including typos, AttributeErrors, etc.
    # A KeyError in your logic becomes invisible.
    try:
        data = {"users": [1, 2, 3]}
        # Bug: wrong key name — but bare except hides it!
        result = data["user"]  # KeyError
    except:  # bare except — don't do this
        pass  # silently fails — how would you ever know?
    return None

def show_specific_except():
    """RIGHT: catch only what you expect."""
    try:
        data = {"users": [1, 2, 3]}
        result = data["user"]  # this will raise
    except KeyError as e:
        print(f"  Config key missing: {e}")
        return []
    # Any other exception (e.g., AttributeError) propagates up — good!


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Exception Handling Patterns")
    print("=" * 50)

    print("\n--- Section 1: try/except/else/finally ---")
    divide(10, 2)
    print()
    divide(10, 0)
    print()
    divide(10, "x")

    print("\n--- Section 3 & 4: Custom exceptions + API layer ---")
    tests = [
        (get_user, 1),                            # success
        (get_user, 99),                           # not found
        (get_user, -1),                           # validation error
        (get_user, "abc"),                        # validation error (wrong type)
        (create_user, "Carol", "carol@test.com"), # success
        (create_user, "Alice", "alice@example.com"),  # conflict
        (create_user, "", "x@y.com"),             # validation error
    ]
    for action, *args in tests:
        response = handle_request(action, *args)
        print(f"  {response}")

    print("\n--- Section 5: raise X from Y ---")
    for key in ["port", "host", "debug"]:
        try:
            value = load_config(key)
            print(f"  config['{key}'] = {value}")
        except AppError as e:
            print(f"  AppError: {e}")
            # The original cause is preserved in __cause__:
            if e.__cause__:
                print(f"    Caused by: {type(e.__cause__).__name__}: {e.__cause__}")

    print("\n--- Section 6: Bare except (bad) vs specific except (good) ---")
    show_bare_except_problem()
    print("  bare except: returned None silently (bug hidden!)")
    show_specific_except()

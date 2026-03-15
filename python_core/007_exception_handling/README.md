# Exception Handling Patterns

## 🎯 Interview Question
"How do you handle exceptions in Python? How do you design custom exceptions for a backend service?"

## 💡 Short Answer (30 seconds)
Python uses `try/except/else/finally` for exception handling. In backend services, you define a hierarchy of custom exceptions — like `AppError → NotFoundError`, `ValidationError` — so that different layers of the app can raise specific errors and the API layer can catch them and return the right HTTP status codes. The key principle: catch exceptions at the right level, not everywhere.

## 🔬 Explanation
**The full `try` block anatomy:**
- `try` — the code that might fail
- `except ExceptionType` — handles a specific exception
- `else` — runs only if NO exception was raised (often forgotten!)
- `finally` — always runs, even if an exception occurred (for cleanup)

**Exception hierarchy matters**: catch the most specific exception first, most general last. Catching bare `Exception` (or worse, `BaseException`) masks bugs.

**Custom exception classes** are how real backend services communicate errors between layers:
```
AppError (base)
├── ValidationError (400 Bad Request)
├── NotFoundError   (404 Not Found)
├── ConflictError   (409 Conflict)
└── AuthError       (401 Unauthorized)
```

The service layer raises `NotFoundError("User not found")`. The FastAPI/Flask error handler catches `NotFoundError` and returns a `404` response. This separation means your service code doesn't need to know about HTTP.

**`raise` vs `raise from`**: use `raise X from Y` when converting one exception type to another — it preserves the original exception as context, making tracebacks useful.

## 💻 Code Example
```python
class AppError(Exception):
    """Base class for all application errors."""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code

class NotFoundError(AppError):
    pass

class ValidationError(AppError):
    pass

def get_user(user_id):
    if not isinstance(user_id, int):
        raise ValidationError(f"user_id must be int, got {type(user_id).__name__}")
    if user_id <= 0:
        raise NotFoundError(f"User {user_id} not found", code="USER_NOT_FOUND")
    return {"id": user_id, "name": "Alice"}

# At the API layer — catch specific errors, return appropriate responses
try:
    user = get_user(0)
except NotFoundError as e:
    print(f"404: {e}")  # caller sees HTTP 404
except ValidationError as e:
    print(f"400: {e}")  # caller sees HTTP 400
except AppError as e:
    print(f"500: Unexpected app error: {e}")
```

## ⚠️ Common Mistakes

1. **Bare `except:` or `except Exception:`** — catches everything including `KeyboardInterrupt`, system exits, and bugs you should know about. Always catch the most specific exception type you expect.

2. **Swallowing exceptions silently** — `except Exception: pass` hides real errors. At minimum, log the error. Silently ignoring exceptions is how bugs live undetected for months.

3. **Catching exceptions too broadly in business logic** — catching `Exception` in service code means a typo (e.g., `AttributeError`) gets swallowed. Catch only what you can meaningfully handle.

## ✅ When to Use vs When NOT to Use

**Raise custom exceptions when:**
- You need to distinguish error types at a higher layer (API returning different status codes)
- The error has domain-specific meaning (e.g., `InsufficientFundsError`)
- You want to add structured context (error codes, user-facing messages, details)

**Use built-in exceptions when:**
- The situation is truly generic — `ValueError` for bad input, `TypeError` for wrong type
- You're writing a utility function, not domain logic

**Don't create exceptions for:**
- Flow control that isn't actually exceptional (use `if` instead)
- Every possible edge case — too many exception types is hard to maintain

## 🔗 Related Concepts
- [002_context_managers](../002_context_managers) — `__exit__` receives exception info; `finally` is similar
- [008_type_hints](../008_type_hints) — annotating functions that raise

## 🚀 Next Step
In `python-backend-mastery`: **Exception groups and `except*`** (Python 3.11+) for async concurrent error handling, and structured logging with exception context for production observability.

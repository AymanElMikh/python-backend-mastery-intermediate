# Custom Exceptions — Domain Error Hierarchy

## 🎯 Interview Question
Why would you define custom exception classes in a Python backend instead of using built-in exceptions like `ValueError` or `Exception`?

## 💡 Short Answer (30 seconds)
Custom exceptions make error handling precise and readable. Instead of catching `ValueError` (which could mean anything), you catch `InsufficientFundsError` — the code at the call site immediately communicates what went wrong and what to do about it. They also let you define an exception hierarchy (all payment errors inherit from `PaymentError`) so you can catch a category of errors without listing each one.

## 🔬 Explanation
In a layered architecture, exceptions flow upward: the service raises a domain exception, the route catches it and converts it to an HTTP response.

Without custom exceptions:
```python
# Service raises generic ValueError
raise ValueError("insufficient funds")

# Route catches it — but ALL ValueErrors look the same
try:
    service.transfer(...)
except ValueError as e:
    return {"error": str(e)}, 400  # Is this a validation error? A business rule? A bug?
```

With custom exceptions:
```python
# Service raises a specific domain error
raise InsufficientFundsError(available=100, requested=500)

# Route catches the specific type — intent is clear
try:
    service.transfer(...)
except InsufficientFundsError:
    return {"error": "insufficient funds"}, 422
except AccountNotFoundError:
    return {"error": "account not found"}, 404
```

A good exception hierarchy also lets you add context (attach the amount, the account ID) that logging and error monitoring can use.

## 💻 Code Example
```python
# Base exception for the whole domain
class AppError(Exception):
    """All app-specific errors inherit from this."""
    pass

# Category-level errors
class NotFoundError(AppError):
    def __init__(self, resource: str, id: int):
        super().__init__(f"{resource} #{id} not found")
        self.resource = resource
        self.id = id

class ValidationError(AppError):
    def __init__(self, field: str, reason: str):
        super().__init__(f"Invalid {field}: {reason}")
        self.field = field

class BusinessRuleError(AppError):
    pass

# Specific errors
class InsufficientFundsError(BusinessRuleError):
    def __init__(self, available: float, requested: float):
        super().__init__(f"Need ${requested:.2f}, have ${available:.2f}")
        self.available = available
        self.requested = requested
```

## ⚠️ Common Mistakes
1. **Catching `Exception` everywhere.** `except Exception: return 500` swallows bugs silently. Catch specific exception types; let unexpected exceptions propagate to a global error handler.
2. **Using exceptions for flow control.** Exceptions should signal unexpected situations. "User not found" in a lookup is expected — return `None` or `Optional`. "User not found when they should exist" is exceptional — raise.
3. **Not attaching context to exceptions.** `raise ValueError("not found")` gives you nothing to debug with. `raise UserNotFoundError(user_id=42)` tells you exactly what happened.

## ✅ When to Use vs When NOT to Use
**Use custom exceptions when:**
- You have domain-specific error conditions (not found, insufficient funds, expired)
- You need to carry structured data with the exception (the invalid field, the missing ID)
- Different callers need to handle different error types differently

**Stick with built-ins when:**
- The error is truly generic (`TypeError` for wrong argument types)
- The function is utility-level with no domain meaning
- The error is programming mistake, not a business condition

## 🔗 Related Concepts
- [clean_architecture/035_service_layer](../035_service_layer) — services raise custom exceptions
- [clean_architecture/032_three_layer_architecture](../032_three_layer_architecture) — route layer converts exceptions to HTTP responses
- [python_core/007_exception_handling](../../python_core/007_exception_handling) — Python exception basics

## 🚀 Next Step
In `python-backend-mastery`: **Structured error responses and RFC 7807** — standardizing error payloads with `type`, `title`, `status`, `detail`, `instance` fields for machine-readable API errors.

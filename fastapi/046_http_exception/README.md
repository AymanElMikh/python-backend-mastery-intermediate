# HTTPException in FastAPI

## 🎯 Interview Question
How do you raise and handle HTTP errors in FastAPI, and how do you customize the error response format?

## 💡 Short Answer (30 seconds)
FastAPI provides `HTTPException` — raise it anywhere in your route or dependency to immediately stop processing and return an error response with the given status code and detail message. For global error handling (catching domain exceptions or adding consistent error formatting), you register exception handlers with `@app.exception_handler(ExceptionType)`.

## 🔬 Explanation
The two-layer pattern works best in FastAPI:

**Layer 1 — Route/Dependency**: raise `HTTPException` for HTTP-level concerns (auth failures, not found).

**Layer 2 — Global exception handler**: catch domain exceptions from services and convert them to HTTP errors in one place. This keeps domain exceptions out of routes and keeps route code clean.

```python
# Route raises HTTPException directly (fine for simple cases)
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = db.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Global handler: converts domain exception → HTTP response everywhere
@app.exception_handler(UserNotFoundError)
def handle_user_not_found(request: Request, exc: UserNotFoundError):
    return JSONResponse(status_code=404, content={"error": str(exc)})
```

## 💻 Code Example
```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Raise in route
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = repo.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User #{user_id} not found")
    return user

# Raise in dependency (also stops processing)
def get_current_user(token: str = Header(...)):
    user = verify_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Global exception handler
@app.exception_handler(InsufficientFundsError)
async def handle_insufficient_funds(request: Request, exc: InsufficientFundsError):
    return JSONResponse(
        status_code=422,
        content={"error": "insufficient_funds", "detail": str(exc)},
    )
```

## ⚠️ Common Mistakes
1. **Raising `HTTPException` in service layer.** Services should raise domain exceptions (`UserNotFoundError`). `HTTPException` belongs in routes and dependencies only. If your service imports FastAPI, the layering is broken.
2. **Using `detail` for structured error data.** `detail` accepts a string or dict. For machine-readable errors, pass a dict: `detail={"code": "INSUFFICIENT_FUNDS", "available": 100}`.
3. **Not handling `RequestValidationError`.** Pydantic validation failures raise `RequestValidationError`, not `HTTPException`. Register a separate handler if you want to customize the 422 format.

## ✅ When to Use `HTTPException` vs Custom Exception Handlers
**`HTTPException` directly** — in route handlers and dependencies, for straightforward cases (auth, simple not-found).

**Custom exception handlers** — when your services raise domain exceptions and you want a single place to map them to HTTP codes. Avoids duplicating `try/except HTTPException` across every route.

## 🔗 Related Concepts
- [clean_architecture/038_custom_exceptions](../../clean_architecture/038_custom_exceptions) — domain exceptions that global handlers catch
- [fastapi/045_status_codes_responses](../045_status_codes_responses) — which status code to use
- [fastapi/044_depends_di](../044_depends_di) — dependencies that raise HTTPException

## 🚀 Next Step
In `python-backend-mastery`: **RFC 7807 Problem Details** — standardizing error responses with `type`, `title`, `status`, `detail`, `instance` fields, and building a custom exception handler that auto-generates compliant problem objects.

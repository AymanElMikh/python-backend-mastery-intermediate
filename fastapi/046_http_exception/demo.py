"""
Demo: HTTPException in FastAPI
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from typing import Optional, Callable, Any
from dataclasses import dataclass


# ── Minimal HTTP infrastructure ───────────────────────────────────────────────

class HTTPException(Exception):
    """Mirrors FastAPI's HTTPException."""
    def __init__(self, status_code: int, detail: Any, headers: dict = None):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers or {}
        super().__init__(str(detail))


class Request:
    """Minimal stand-in for FastAPI's Request object."""
    def __init__(self, method: str, path: str, headers: dict = None):
        self.method = method
        self.url = path
        self.headers = headers or {}


# ── Domain exceptions (from clean_architecture/038) ──────────────────────────

class AppError(Exception):
    pass

class UserNotFoundError(AppError):
    def __init__(self, user_id: int):
        super().__init__(f"User #{user_id} not found")
        self.user_id = user_id

class InsufficientFundsError(AppError):
    def __init__(self, available: float, required: float):
        super().__init__(f"Need ${required:.2f}, have ${available:.2f}")
        self.available = available
        self.required = required

class EmailAlreadyExistsError(AppError):
    def __init__(self, email: str):
        super().__init__(f"Email '{email}' is already registered")
        self.email = email


# ── Mini FastAPI application ──────────────────────────────────────────────────

class MiniApp:
    def __init__(self):
        self._routes: list[dict] = []
        self._exception_handlers: dict[type, Callable] = {}
        # Default handler for HTTPException
        self._exception_handlers[HTTPException] = self._default_http_handler

    @staticmethod
    def _default_http_handler(request: Request, exc: HTTPException) -> dict:
        return {
            "status": exc.status_code,
            "body": {"detail": exc.detail},
            "headers": exc.headers,
        }

    def exception_handler(self, exc_class: type):
        """Register a global exception handler (like @app.exception_handler)."""
        def decorator(fn: Callable):
            self._exception_handlers[exc_class] = fn
            return fn
        return decorator

    def route(self, method: str, path: str):
        def decorator(fn: Callable):
            self._routes.append({"method": method, "path": path, "handler": fn})
            return fn
        return decorator

    def call(self, method: str, path: str, headers: dict = None, **kwargs) -> dict:
        """Dispatch a request — simulate FastAPI request processing."""
        request = Request(method, path, headers or {})
        for r in self._routes:
            if r["method"] == method and r["path"] == path:
                try:
                    result = r["handler"](request=request, **kwargs)
                    return {"status": 200, "body": result}
                except Exception as exc:
                    return self._handle_exception(request, exc)
        return {"status": 404, "body": {"detail": f"No route: {method} {path}"}}

    def _handle_exception(self, request: Request, exc: Exception) -> dict:
        # Check for specific handler first, then base classes
        for exc_type, handler in self._exception_handlers.items():
            if isinstance(exc, exc_type):
                return handler(request, exc)
        # Unhandled — 500
        return {"status": 500, "body": {"detail": f"Internal server error: {exc}"}}


app = MiniApp()


# ── Section 1: Fake data + service ───────────────────────────────────────────

USERS = {
    1: {"id": 1, "email": "alice@x.com", "balance": 500.0},
    2: {"id": 2, "email": "bob@x.com",   "balance": 25.0},
}

class UserService:
    def get(self, user_id: int) -> dict:
        user = USERS.get(user_id)
        if user is None:
            raise UserNotFoundError(user_id)   # domain exception, NOT HTTPException
        return user

    def transfer(self, from_id: int, to_id: int, amount: float) -> dict:
        sender = USERS.get(from_id)
        if sender is None:
            raise UserNotFoundError(from_id)
        if sender["balance"] < amount:
            raise InsufficientFundsError(sender["balance"], amount)
        USERS[from_id]["balance"] -= amount
        USERS.get(to_id, {})["balance"] = USERS.get(to_id, {}).get("balance", 0) + amount
        return {"from": from_id, "to": to_id, "amount": amount, "status": "completed"}

service = UserService()


# ── Section 2: Global exception handlers ─────────────────────────────────────

@app.exception_handler(UserNotFoundError)
def handle_user_not_found(request: Request, exc: UserNotFoundError) -> dict:
    return {
        "status": 404,
        "body": {"error": "user_not_found", "detail": str(exc), "user_id": exc.user_id},
        "headers": {},
    }

@app.exception_handler(InsufficientFundsError)
def handle_insufficient_funds(request: Request, exc: InsufficientFundsError) -> dict:
    return {
        "status": 422,
        "body": {
            "error": "insufficient_funds",
            "detail": str(exc),
            "available": exc.available,
        },
        "headers": {},
    }

@app.exception_handler(EmailAlreadyExistsError)
def handle_duplicate_email(request: Request, exc: EmailAlreadyExistsError) -> dict:
    return {
        "status": 409,
        "body": {"error": "duplicate_email", "detail": str(exc)},
        "headers": {},
    }


# ── Section 3: Routes ─────────────────────────────────────────────────────────

VALID_TOKENS = {"Bearer token-alice": 1, "Bearer token-bob": 2}

def get_current_user(headers: dict) -> dict:
    """Auth dependency — raises HTTPException directly (appropriate for HTTP concerns)."""
    token = headers.get("authorization", "")
    user_id = VALID_TOKENS.get(token)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return service.get(user_id)


@app.route("GET", "/users/{user_id}")
def get_user(request: Request, user_id: int) -> dict:
    # Route itself is clean — exception handling is delegated to global handlers
    return service.get(user_id)


@app.route("POST", "/transfer")
def transfer(request: Request, from_id: int, to_id: int, amount: float) -> dict:
    # Auth check via dependency (raises HTTPException on fail)
    get_current_user(request.headers)
    return service.transfer(from_id, to_id, amount)


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: HTTPException in FastAPI")
    print("=" * 55)

    print("\n--- Happy path ---")
    resp = app.call("GET", "/users/{user_id}", user_id=1)
    print(f"  GET /users/1 → {resp['status']}: {resp['body']}")

    print("\n--- Domain exception → global handler → HTTP response ---")
    resp = app.call("GET", "/users/{user_id}", user_id=99)
    print(f"  GET /users/99 → {resp['status']}: {resp['body']}")

    print("\n--- HTTPException from auth dependency ---")
    resp = app.call("POST", "/transfer",
                    headers={"authorization": "Bearer bad-token"},
                    from_id=1, to_id=2, amount=50.0)
    print(f"  No auth → {resp['status']}: {resp['body']}")
    print(f"  Headers: {resp.get('headers')}")

    print("\n--- Auth passes but business rule fails ---")
    resp = app.call("POST", "/transfer",
                    headers={"authorization": "Bearer token-bob"},
                    from_id=2, to_id=1, amount=1000.0)
    print(f"  Bob transfer $1000 → {resp['status']}: {resp['body']}")

    print("\n--- Successful transfer ---")
    resp = app.call("POST", "/transfer",
                    headers={"authorization": "Bearer token-alice"},
                    from_id=1, to_id=2, amount=100.0)
    print(f"  Alice → Bob $100 → {resp['status']}: {resp['body']}")

    print("\n--- Unhandled exception → 500 ---")
    @app.route("GET", "/buggy")
    def buggy_route(request: Request) -> dict:
        raise RuntimeError("Unexpected bug in the code")

    resp = app.call("GET", "/buggy")
    print(f"  Buggy route → {resp['status']}: {resp['body']}")

    print("\n--- Key patterns ---")
    print("  Services raise:     domain exceptions (UserNotFoundError)")
    print("  Global handlers:    convert domain exceptions → HTTP responses")
    print("  Routes/deps raise:  HTTPException for HTTP-level concerns only")
    print("  Services NEVER import FastAPI/HTTPException")

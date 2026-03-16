"""
Demo: Middleware Basics in FastAPI
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Callable, Optional


# ── Minimal request/response objects ─────────────────────────────────────────

@dataclass
class Request:
    method: str
    path: str
    headers: dict = field(default_factory=dict)
    body: dict = field(default_factory=dict)


@dataclass
class Response:
    status_code: int
    body: dict
    headers: dict = field(default_factory=dict)


# ── Minimal FastAPI simulator with middleware support ─────────────────────────

class FastAPI:
    def __init__(self):
        self._routes: dict[tuple, Callable] = {}
        self._middleware_stack: list[Callable] = []

    def route(self, method: str, path: str):
        def decorator(fn: Callable):
            self._routes[(method, path)] = fn
            return fn
        return decorator

    def add_middleware(self, middleware_fn: Callable):
        """Register middleware. Last registered runs outermost (first on request)."""
        self._middleware_stack.append(middleware_fn)

    def _dispatch(self, request: Request) -> Response:
        """Run the actual route handler."""
        handler = self._routes.get((request.method, request.path))
        if handler is None:
            return Response(404, {"error": f"No route: {request.method} {request.path}"})
        try:
            result = handler(request)
            if isinstance(result, Response):
                return result
            return Response(200, result)
        except Exception as e:
            return Response(500, {"error": str(e)})

    def request(self, method: str, path: str, headers: dict = None, body: dict = None) -> Response:
        """Process a request through the full middleware stack."""
        req = Request(method, path, headers or {}, body or {})

        # Build the chain: middleware wraps middleware wraps ... wraps route handler
        def base_call_next(r: Request) -> Response:
            return self._dispatch(r)

        call_next = base_call_next
        # Wrap in reverse order so the first middleware registered is the outermost
        for mw in reversed(self._middleware_stack):
            outer_call_next = call_next
            def make_wrapper(mw, cnext):
                def wrapper(r: Request) -> Response:
                    return mw(r, cnext)
                return wrapper
            call_next = make_wrapper(mw, outer_call_next)

        return call_next(req)


# ── Section 1: Middleware implementations ────────────────────────────────────

def timing_middleware(request: Request, call_next: Callable) -> Response:
    """
    Measures how long each request takes.
    In real FastAPI: @app.middleware("http") async def timing(request, call_next)
    """
    start = time.perf_counter()
    response = call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
    return response


def request_id_middleware(request: Request, call_next: Callable) -> Response:
    """
    Adds a unique ID to every request — vital for distributed tracing.
    The ID appears in request headers AND in the response.
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    request.headers["X-Request-ID"] = request_id
    response = call_next(request)
    response.headers["X-Request-ID"] = request_id   # echo back in response
    return response


def logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Logs every request and response. In real apps: use structlog or Python logging.
    """
    print(f"  [MW Log] → {request.method} {request.path} "
          f"[req-id={request.headers.get('X-Request-ID', '?')}]")
    response = call_next(request)
    print(f"  [MW Log] ← {response.status_code} "
          f"({response.headers.get('X-Process-Time-Ms', '?')}ms)")
    return response


def security_headers_middleware(request: Request, call_next: Callable) -> Response:
    """
    Adds security headers to every response.
    This is much better than adding them in every route function.
    """
    response = call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


def maintenance_mode_middleware(enabled: bool):
    """
    Factory that returns a middleware. Blocks all requests when maintenance is on.
    Shows how middleware can short-circuit without calling call_next.
    """
    def middleware(request: Request, call_next: Callable) -> Response:
        if enabled and request.path != "/health":
            # Short-circuit: don't call call_next at all
            return Response(503, {"error": "Service temporarily unavailable"},
                            headers={"Retry-After": "300"})
        return call_next(request)
    return middleware


# ── Section 2: App setup ──────────────────────────────────────────────────────

app = FastAPI()

# Middleware is applied in registration order (first registered = outermost)
app.add_middleware(logging_middleware)
app.add_middleware(request_id_middleware)
app.add_middleware(timing_middleware)
app.add_middleware(security_headers_middleware)

USERS = {1: {"id": 1, "name": "Alice"}, 2: {"id": 2, "name": "Bob"}}

@app.route("GET", "/health")
def health(req: Request) -> dict:
    return {"status": "ok"}

@app.route("GET", "/users")
def list_users(req: Request) -> dict:
    return {"users": list(USERS.values())}

@app.route("GET", "/users/1")
def get_user(req: Request) -> dict:
    return USERS[1]

@app.route("GET", "/slow")
def slow_route(req: Request) -> dict:
    time.sleep(0.05)  # simulate slow DB query
    return {"result": "took a while"}


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Middleware Basics in FastAPI")
    print("=" * 55)

    print("\n--- Middleware stack (outermost → innermost → route) ---")
    print("  Logging → RequestID → Timing → SecurityHeaders → Route")

    print("\n--- Normal requests (all middleware runs) ---")
    for method, path in [("GET", "/health"), ("GET", "/users"), ("GET", "/users/1")]:
        print()
        resp = app.request(method, path)
        print(f"  Response: {resp.status_code} | headers: {resp.headers}")

    print("\n--- Slow route (timing header shows the delay) ---")
    resp = app.request("GET", "/slow")
    print(f"  X-Process-Time-Ms: {resp.headers.get('X-Process-Time-Ms')}")

    print("\n--- Request with existing request ID (propagated) ---")
    resp = app.request("GET", "/health", headers={"X-Request-ID": "my-trace-123"})
    print(f"  Request-ID echoed: {resp.headers.get('X-Request-ID')}")

    print("\n--- Maintenance mode middleware (short-circuits) ---")
    maintenance_app = FastAPI()
    maintenance_app.add_middleware(maintenance_mode_middleware(enabled=True))
    maintenance_app.add_middleware(logging_middleware)

    @maintenance_app.route("GET", "/health")
    def maintenance_health(req: Request) -> dict:
        return {"status": "ok"}

    @maintenance_app.route("GET", "/users")
    def maintenance_users(req: Request) -> dict:
        return {"users": []}

    print()
    for path in ["/health", "/users"]:
        resp = maintenance_app.request("GET", path)
        print(f"  GET {path} → {resp.status_code}: {resp.body}")

    print("\n--- Middleware vs Depends() quick guide ---")
    print("  Middleware: runs for ALL requests — logging, timing, CORS, security headers")
    print("  Depends():  runs for SPECIFIC routes — auth for /admin, DB for /users")
    print()
    print("  BAD: putting per-route auth in middleware (hard to selectively skip)")
    print("  GOOD: router-level Depends(require_admin) for /admin/* routes")

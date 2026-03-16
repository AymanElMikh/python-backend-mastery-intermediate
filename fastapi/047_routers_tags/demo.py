"""
Demo: FastAPI Routers & Tags
Level: Intermediate (2–3 years experience)
Run:  python demo.py

Shows how APIRouter organizes a growing FastAPI application.
Simulates include_router() and prefix logic without a running server.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional


# ── Minimal APIRouter + FastAPI simulator ─────────────────────────────────────

@dataclass
class RouteEntry:
    method: str
    full_path: str
    handler: Callable
    tags: list[str]
    requires_auth: bool = False


class APIRouter:
    """Mirrors FastAPI's APIRouter."""
    def __init__(self, prefix: str = "", tags: list[str] = None,
                 require_auth: bool = False):
        self.prefix = prefix
        self.tags = tags or []
        self.require_auth = require_auth
        self._routes: list[dict] = []

    def _add(self, method: str, path: str, fn: Callable):
        self._routes.append({"method": method, "path": path, "handler": fn})
        return fn

    def get(self, path: str):
        return lambda fn: self._add("GET", path, fn)

    def post(self, path: str):
        return lambda fn: self._add("POST", path, fn)

    def put(self, path: str):
        return lambda fn: self._add("PUT", path, fn)

    def delete(self, path: str):
        return lambda fn: self._add("DELETE", path, fn)


class FastAPI:
    def __init__(self, title: str = "API"):
        self.title = title
        self._routes: list[RouteEntry] = []

    def include_router(self, router: APIRouter, prefix: str = "",
                       tags: list[str] = None):
        """Merge router routes into the app with a prefix."""
        combined_prefix = (prefix or router.prefix).rstrip("/")
        combined_tags = (tags or router.tags)
        for r in router._routes:
            path = r["path"].lstrip("/")
            full_path = f"{combined_prefix}/{path}".rstrip("/") or "/"
            self._routes.append(RouteEntry(
                method=r["method"],
                full_path=full_path,
                handler=r["handler"],
                tags=combined_tags,
                requires_auth=router.require_auth,
            ))

    def get(self, path: str, tags: list[str] = None):
        def decorator(fn):
            self._routes.append(RouteEntry("GET", path, fn, tags or []))
            return fn
        return decorator

    def request(self, method: str, path: str,
                auth_token: Optional[str] = None, **kwargs) -> dict:
        for route in self._routes:
            if route.method == method and self._matches(route.full_path, path):
                if route.requires_auth and not auth_token:
                    return {"status": 401, "body": {"error": "Authentication required"}}
                params = self._extract_params(route.full_path, path)
                params.update(kwargs)
                try:
                    return {"status": 200, "body": route.handler(**params)}
                except Exception as e:
                    return {"status": 500, "body": {"error": str(e)}}
        return {"status": 404, "body": {"error": f"No route: {method} {path}"}}

    def _matches(self, pattern: str, path: str) -> bool:
        import re
        regex = re.sub(r"\{(\w+)\}", r"[^/]+", pattern) + "$"
        return bool(re.match(regex, path))

    def _extract_params(self, pattern: str, path: str) -> dict:
        import re
        regex = re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", pattern) + "$"
        m = re.match(regex, path)
        if m:
            return {k: int(v) if v.isdigit() else v for k, v in m.groupdict().items()}
        return {}

    def list_routes(self) -> None:
        print(f"\n  {self.title} — Registered Routes:")
        by_tag: dict[str, list] = {}
        for r in self._routes:
            tag = r.tags[0] if r.tags else "default"
            by_tag.setdefault(tag, []).append(r)
        for tag, routes in by_tag.items():
            print(f"  [{tag}]")
            for r in routes:
                auth_marker = " 🔒" if r.requires_auth else ""
                print(f"    {r.method:6s} {r.full_path}{auth_marker}")


# ── Section 1: Router files (as they'd be in separate files) ──────────────────

# --- routers/users.py ---
users_router = APIRouter(tags=["Users"])

USERS = {1: {"id": 1, "name": "Alice"}, 2: {"id": 2, "name": "Bob"}}

@users_router.get("/")
def list_users():
    return list(USERS.values())

@users_router.get("/{user_id}")
def get_user(user_id: int):
    user = USERS.get(user_id)
    return user if user else {"error": f"User #{user_id} not found"}

@users_router.post("/")
def create_user():
    return {"id": 99, "name": "New User", "created": True}


# --- routers/orders.py ---
orders_router = APIRouter(tags=["Orders"])

ORDERS = {
    1: {"id": 1, "user_id": 1, "total": 99.99},
    2: {"id": 2, "user_id": 2, "total": 49.00},
}

@orders_router.get("/")
def list_orders():
    return list(ORDERS.values())

@orders_router.get("/{order_id}")
def get_order(order_id: int):
    order = ORDERS.get(order_id)
    return order if order else {"error": f"Order #{order_id} not found"}


# --- routers/admin.py --- (requires auth for ALL routes)
admin_router = APIRouter(tags=["Admin"], require_auth=True)

@admin_router.get("/stats")
def admin_stats():
    return {"total_users": len(USERS), "total_orders": len(ORDERS)}

@admin_router.delete("/users/{user_id}")
def admin_delete_user(user_id: int):
    if user_id in USERS:
        del USERS[user_id]
        return {"deleted": user_id}
    return {"error": "not found"}


# ── Section 2: main.py — wire everything together ────────────────────────────

app = FastAPI(title="My API")

# Root health check (directly on app)
@app.get("/health", tags=["Meta"])
def health():
    return {"status": "ok"}

# Include routers with prefixes
app.include_router(users_router,  prefix="/users",  tags=["Users"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])
app.include_router(admin_router,  prefix="/admin",  tags=["Admin"])


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: FastAPI Routers & Tags")
    print("=" * 55)

    app.list_routes()

    print("\n--- Routes work with correct prefixes ---")
    tests = [
        ("GET",    "/health",        None),
        ("GET",    "/users",         None),
        ("GET",    "/users/1",       None),
        ("GET",    "/users/99",      None),
        ("GET",    "/orders",        None),
        ("GET",    "/orders/2",      None),
        ("GET",    "/admin/stats",   "Bearer admin-token"),   # with auth
        ("GET",    "/admin/stats",   None),                   # without auth → 401
        ("DELETE", "/admin/users/2", "Bearer admin-token"),   # delete via admin
        ("GET",    "/users",         None),                   # only 1 user now
    ]

    for method, path, token in tests:
        resp = app.request(method, path, auth_token=token)
        auth_note = " [auth]" if token else ""
        print(f"  {method:6s} {path:25s}{auth_note} → {resp['status']}: {resp['body']}")

    print("\n--- File structure this maps to ---")
    print("  app/")
    print("  ├── main.py                    ← creates app, calls include_router()")
    print("  └── routers/")
    print("      ├── users.py               ← users_router = APIRouter()")
    print("      ├── orders.py              ← orders_router = APIRouter()")
    print("      └── admin.py               ← admin_router = APIRouter(require_auth=True)")

    print("\n--- Common mistake: prefix duplication ---")
    print("  BAD:  @router.get('/users/')   then  include_router(router, prefix='/users')")
    print("        → results in: /users/users/")
    print("  GOOD: @router.get('/')         then  include_router(router, prefix='/users')")
    print("        → results in: /users/")

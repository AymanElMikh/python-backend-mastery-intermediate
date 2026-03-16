"""
Demo: FastAPI Routes & Path Parameters
Level: Intermediate (2–3 years experience)
Run:  python demo.py

Note: This demo simulates FastAPI's routing behaviour WITHOUT running a server.
To see the real thing: pip install fastapi uvicorn httpx
Then: uvicorn demo_server:app --reload
"""

# ── What FastAPI does for you ─────────────────────────────────────────────────
# The code below simulates what happens inside FastAPI when a request arrives.
# In real FastAPI you'd just write the route function and decorators.

from dataclasses import dataclass
from typing import Callable, Any
import re


# ── Minimal router simulator ──────────────────────────────────────────────────

@dataclass
class Route:
    method: str
    pattern: str           # e.g. "/users/{user_id}"
    handler: Callable
    param_types: dict      # e.g. {"user_id": int}

    def match(self, method: str, path: str) -> tuple[bool, dict]:
        if self.method != method:
            return False, {}
        regex = re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", self.pattern) + "$"
        m = re.match(regex, path)
        if not m:
            return False, {}
        return True, m.groupdict()


class MiniFastAPI:
    def __init__(self):
        self._routes: list[Route] = []

    def _register(self, method: str, path: str, func: Callable) -> Callable:
        import inspect
        hints = {
            k: v for k, v in func.__annotations__.items()
            if k != "return" and f"{{{k}}}" in path
        }
        self._routes.append(Route(method, path, func, hints))
        return func

    def get(self, path: str):
        def decorator(func):
            return self._register("GET", path, func)
        return decorator

    def post(self, path: str):
        def decorator(func):
            return self._register("POST", path, func)
        return decorator

    def request(self, method: str, path: str, body: dict = None) -> dict:
        for route in self._routes:
            matched, raw_params = route.match(method, path)
            if not matched:
                continue
            # Type conversion (what FastAPI does automatically)
            params = {}
            for k, v in raw_params.items():
                target_type = route.param_types.get(k, str)
                try:
                    params[k] = target_type(v)
                except (ValueError, TypeError):
                    return {
                        "status": 422,
                        "detail": f"Path param '{k}' must be {target_type.__name__}, got '{v}'"
                    }
            try:
                if body:
                    result = route.handler(**params, body=body)
                else:
                    result = route.handler(**params)
                return {"status": 200, "data": result}
            except Exception as e:
                return {"status": 500, "error": str(e)}
        return {"status": 404, "detail": f"No route for {method} {path}"}


# ── Section 1: Define routes (like real FastAPI) ──────────────────────────────

app = MiniFastAPI()

# Simple GET with no path params
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0"}

# Path parameter — int type
@app.get("/users/{user_id}")
def get_user(user_id: int):
    users = {1: "Alice", 2: "Bob", 3: "Carol"}
    name = users.get(user_id)
    if name is None:
        return {"error": "not found"}
    return {"id": user_id, "name": name}

# Multiple path params
@app.get("/orgs/{org_id}/users/{user_id}")
def get_org_user(org_id: str, user_id: int):
    return {"org": org_id, "user_id": user_id, "result": f"{org_id}/user#{user_id}"}

# String path param
@app.get("/categories/{slug}")
def get_category(slug: str):
    return {"category": slug, "url_safe": slug.lower().replace(" ", "-")}

# POST with path param
@app.post("/users/{user_id}/activate")
def activate_user(user_id: int):
    return {"user_id": user_id, "status": "activated"}


# ── Section 2: Route ordering matters! ───────────────────────────────────────

# PROBLEM: if /users/{user_id} was registered before /users/me,
# then GET /users/me would match {user_id} = "me" and fail int conversion.

# SOLUTION: register specific routes BEFORE parameterized ones.
# FastAPI handles this based on declaration order.

@app.get("/items/featured")      # specific — register FIRST
def get_featured_items():
    return {"items": ["laptop", "phone"], "featured": True}

@app.get("/items/{item_id}")     # parameterized — register AFTER
def get_item(item_id: int):
    return {"item_id": item_id}


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: FastAPI Routes & Path Parameters")
    print("=" * 55)

    tests = [
        ("GET",  "/health"),
        ("GET",  "/users/1"),
        ("GET",  "/users/2"),
        ("GET",  "/users/999"),
        ("GET",  "/users/abc"),           # invalid int → 422
        ("GET",  "/orgs/acme/users/7"),
        ("GET",  "/categories/Electronics"),
        ("POST", "/users/5/activate"),
        ("GET",  "/items/featured"),      # must match before /items/{item_id}
        ("GET",  "/items/42"),
        ("GET",  "/items/abc"),           # invalid int → 422
        ("GET",  "/nonexistent"),
    ]

    for method, path in tests:
        resp = app.request(method, path)
        status = resp.get("status")
        payload = resp.get("data") or resp.get("detail") or resp.get("error")
        print(f"  {method:4s} {path:35s} → {status}: {payload}")

    print("\n--- Key FastAPI behaviours shown above ---")
    print("  ✓ Type conversion:  /users/1 → user_id=int(1)")
    print("  ✓ Validation:       /users/abc → 422 (not an int)")
    print("  ✓ Route ordering:   /items/featured matches before /items/{item_id}")
    print("  ✓ Multiple params:  /orgs/{org}/users/{id} both extracted")

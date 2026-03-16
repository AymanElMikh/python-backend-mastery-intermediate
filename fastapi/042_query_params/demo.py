"""
Demo: FastAPI Query Parameters
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from typing import Optional
from urllib.parse import parse_qs, urlparse


# ── Query param parsing helper (simulates what FastAPI does) ─────────────────

def parse_query(url: str) -> dict[str, str]:
    """Extract query params from a URL string."""
    parsed = urlparse(url)
    raw = parse_qs(parsed.query)
    # parse_qs returns lists; take the first value of each
    return {k: v[0] for k, v in raw.items()}


def coerce(value: str, target_type: type, param_name: str):
    """
    Convert a raw string query param to the target type.
    This is what FastAPI does automatically via Pydantic.
    """
    if target_type == bool:
        if value.lower() in ("true", "1", "yes"):
            return True
        if value.lower() in ("false", "0", "no"):
            return False
        raise ValueError(f"Query param '{param_name}' must be true/false, got '{value}'")
    try:
        return target_type(value)
    except (ValueError, TypeError):
        raise ValueError(f"Query param '{param_name}' must be {target_type.__name__}, got '{value}'")


# ── Section 1: Route handler with query params ────────────────────────────────

# Fake in-memory data
USERS = [
    {"id": 1, "name": "Alice", "role": "admin",  "is_active": True,  "age": 30},
    {"id": 2, "name": "Bob",   "role": "user",   "is_active": True,  "age": 25},
    {"id": 3, "name": "Carol", "role": "user",   "is_active": False, "age": 35},
    {"id": 4, "name": "Dave",  "role": "admin",  "is_active": True,  "age": 28},
    {"id": 5, "name": "Eve",   "role": "viewer", "is_active": True,  "age": 22},
]


def list_users(
    page: int = 1,
    limit: int = 3,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    q: Optional[str] = None,
) -> dict:
    """
    Equivalent to a FastAPI route:
    @app.get("/users")
    def list_users(page: int = 1, limit: int = 3, role: str | None = None, ...)
    """
    results = USERS.copy()

    # Apply filters
    if role is not None:
        results = [u for u in results if u["role"] == role]
    if is_active is not None:
        results = [u for u in results if u["is_active"] == is_active]
    if q is not None:
        results = [u for u in results if q.lower() in u["name"].lower()]

    # Pagination
    total = len(results)
    start = (page - 1) * limit
    end = start + limit
    page_data = results[start:end]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "results": page_data,
    }


def simulate_request(url: str) -> dict:
    """Parse query params from URL and call list_users (like FastAPI does)."""
    params = parse_query(url)
    kwargs = {}
    schema = {
        "page": (int, 1),
        "limit": (int, 3),
        "role": (str, None),
        "is_active": (bool, None),
        "q": (str, None),
    }
    for name, (typ, default) in schema.items():
        if name in params:
            try:
                kwargs[name] = coerce(params[name], typ, name)
            except ValueError as e:
                return {"status": 422, "error": str(e)}
        elif default is not None:
            kwargs[name] = default
    return {"status": 200, "data": list_users(**kwargs)}


# ── Section 2: Required query param ──────────────────────────────────────────

def search_products(
    q: str,               # REQUIRED — no default
    min_price: float = 0,
    max_price: float = 9999,
    in_stock: bool = True,
) -> dict:
    """
    'q' is required — FastAPI returns 422 if it's missing.
    The others are optional with defaults.
    """
    products = [
        {"name": "Laptop",  "price": 999, "in_stock": True},
        {"name": "Mouse",   "price": 29,  "in_stock": True},
        {"name": "Monitor", "price": 399, "in_stock": False},
        {"name": "Keyboard","price": 79,  "in_stock": True},
    ]
    results = [
        p for p in products
        if q.lower() in p["name"].lower()
        and min_price <= p["price"] <= max_price
        and (not in_stock or p["in_stock"])
    ]
    return {"query": q, "results": results}


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: FastAPI Query Parameters")
    print("=" * 55)

    print("\n--- GET /users (no params — all defaults) ---")
    r = simulate_request("/users")
    print(f"  → {r['data']}")

    print("\n--- Pagination ---")
    for page in [1, 2]:
        r = simulate_request(f"/users?page={page}&limit=2")
        names = [u["name"] for u in r["data"]["results"]]
        print(f"  page={page}: {names}")

    print("\n--- Filter by role ---")
    r = simulate_request("/users?role=admin")
    print(f"  role=admin: {[u['name'] for u in r['data']['results']]}")

    print("\n--- Filter by is_active ---")
    r = simulate_request("/users?is_active=false")
    print(f"  is_active=false: {[u['name'] for u in r['data']['results']]}")

    r = simulate_request("/users?is_active=true&role=admin")
    print(f"  is_active=true&role=admin: {[u['name'] for u in r['data']['results']]}")

    print("\n--- Search by name ---")
    r = simulate_request("/users?q=al")
    print(f"  q=al: {[u['name'] for u in r['data']['results']]}")

    print("\n--- Type validation ---")
    r = simulate_request("/users?page=abc")
    print(f"  page=abc → {r['status']}: {r.get('error')}")

    r = simulate_request("/users?is_active=maybe")
    print(f"  is_active=maybe → {r['status']}: {r.get('error')}")

    print("\n--- Required query param ---")
    print("  /search?q=laptop&min_price=50&max_price=500:")
    result = search_products(q="laptop")
    print(f"    {result}")

    result = search_products(q="o", min_price=50, max_price=500, in_stock=True)
    print(f"  q=o, 50-500, in_stock=true: {result}")

    print("\n--- Common mistakes ---")
    print("  BAD:  GET /users?id=42      ← id is resource identity, use path param")
    print("  GOOD: GET /users/42          ← path param identifies the resource")
    print()
    print("  BAD:  GET /users?limit=10000 ← no upper bound, could dump your DB")
    print("  GOOD: use Query(le=100) to enforce a max limit")
    print()
    print("  BAD:  role: str = None       ← misleading, should be str | None = None")
    print("  GOOD: role: str | None = None ← explicit that None is a valid value")

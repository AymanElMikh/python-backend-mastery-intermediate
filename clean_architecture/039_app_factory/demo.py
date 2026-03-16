"""
Demo: Application Factory Pattern
Level: Intermediate (2–3 years experience)
Run:  python demo.py

Simulates the app factory pattern without requiring Flask/FastAPI installed.
The pattern is identical — replace "MiniApp" with Flask() or FastAPI().
"""

from dataclasses import dataclass, field
from typing import Callable, Optional


# ── Section 1: Config objects ─────────────────────────────────────────────────

@dataclass
class Config:
    """Base config — shared settings."""
    debug: bool = False
    database_url: str = "postgresql://localhost/myapp"
    secret_key: str = "changeme"
    max_connections: int = 10


@dataclass
class TestConfig(Config):
    """Test config — in-memory DB, fast, isolated."""
    debug: bool = True
    database_url: str = "sqlite:///:memory:"
    secret_key: str = "test-secret"
    max_connections: int = 1


@dataclass
class ProductionConfig(Config):
    """Production config — real DB, strict settings."""
    debug: bool = False
    database_url: str = "postgresql://prod-host/myapp"
    secret_key: str = "super-secret-production-key"
    max_connections: int = 20


# ── Section 2: A minimal "framework" (simulates Flask/FastAPI) ───────────────

@dataclass
class Route:
    path: str
    method: str
    handler: Callable


class MiniApp:
    """Simulates a web framework app object."""
    def __init__(self, config: Config):
        self.config = config
        self._routes: list[Route] = []
        self._started = False

    def add_route(self, path: str, method: str, handler: Callable) -> None:
        self._routes.append(Route(path=path, method=method, handler=handler))

    def start(self) -> None:
        self._started = True
        print(f"  [App] Started | debug={self.config.debug} | db={self.config.database_url}")

    def handle(self, method: str, path: str, body: dict = None) -> dict:
        """Simulate processing a request."""
        for route in self._routes:
            if route.path == path and route.method == method:
                return route.handler(body or {})
        return {"error": "Not found", "status": 404}

    def registered_routes(self) -> list[str]:
        return [f"{r.method} {r.path}" for r in self._routes]


# ── Section 3: Route handlers ─────────────────────────────────────────────────

class FakeDatabase:
    def __init__(self, url: str):
        self.url = url
        self._store: dict = {}
        self._next_id = 1
        print(f"  [DB] Initialized: {url}")

    def insert(self, data: dict) -> dict:
        data["id"] = self._next_id
        self._store[self._next_id] = data
        self._next_id += 1
        return data

    def find_all(self) -> list:
        return list(self._store.values())


def make_user_routes(db: FakeDatabase):
    """Returns route handlers bound to this specific DB instance."""
    def get_users(body: dict) -> dict:
        return {"users": db.find_all(), "status": 200}

    def post_user(body: dict) -> dict:
        if not body.get("email"):
            return {"error": "email required", "status": 400}
        user = db.insert({"email": body["email"], "name": body.get("name", "")})
        return {"user": user, "status": 201}

    return get_users, post_user


def make_health_route(config: Config):
    def health(body: dict) -> dict:
        return {"status": "ok", "debug": config.debug, "db": config.database_url}
    return health


# ── Section 4: The factory ────────────────────────────────────────────────────

def create_app(config: Optional[Config] = None) -> MiniApp:
    """
    THE FACTORY FUNCTION.
    Creates a fresh app with the given config.
    Called differently for dev, test, and production.

    In Flask: returns a Flask app instance.
    In FastAPI: returns a FastAPI instance.
    """
    cfg = config or ProductionConfig()
    print(f"\n  [Factory] Creating app...")

    # 1. Create the app with config
    app = MiniApp(config=cfg)

    # 2. Initialize infrastructure (DB, cache, etc.)
    db = FakeDatabase(url=cfg.database_url)

    # 3. Create route handlers (inject dependencies)
    get_users, post_user = make_user_routes(db)
    health = make_health_route(cfg)

    # 4. Register routes (like register_blueprint in Flask)
    app.add_route("/health",  "GET",  health)
    app.add_route("/users",   "GET",  get_users)
    app.add_route("/users",   "POST", post_user)

    # 5. Start the app
    app.start()
    return app


# ── Section 5: The problem without a factory ─────────────────────────────────

# Simulates the module-level anti-pattern:
print("Simulating module-level app (runs on import):")
_module_level_db = FakeDatabase("postgresql://hardcoded-prod-db/myapp")
_module_level_app = MiniApp(config=ProductionConfig())
# ^ This runs once when the module is imported.
# In tests, you'd get this production-configured app every time.
# There's no clean way to swap in a test database.


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("DEMO: Application Factory Pattern")
    print("=" * 55)

    print("\n--- BAD: module-level app (can't be reconfigured) ---")
    print("  (see code above: _module_level_app is always production config)")
    print("  Tests that import this get the prod DB URL — no way to override.")

    print("\n--- GOOD: factory creates fresh app per call ---")

    print("\n  1. Production app:")
    prod_app = create_app(ProductionConfig())
    print(f"  Routes: {prod_app.registered_routes()}")
    resp = prod_app.handle("GET", "/health")
    print(f"  GET /health → {resp}")

    print("\n  2. Test app (different DB, same code):")
    test_app = create_app(TestConfig())
    print(f"  Routes: {test_app.registered_routes()}")
    resp = test_app.handle("GET", "/health")
    print(f"  GET /health → {resp}")

    print("\n--- Each app has its own state ---")
    # Prod app and test app have completely separate databases
    prod_app.handle("POST", "/users", {"email": "prod@example.com", "name": "Prod User"})
    test_app.handle("POST", "/users", {"email": "test@example.com", "name": "Test User"})

    prod_users = prod_app.handle("GET", "/users")
    test_users = test_app.handle("GET", "/users")

    print(f"\n  Prod app users: {prod_users}")
    print(f"  Test app users: {test_users}")
    print("\n  Test data never leaks into prod — completely isolated instances.")

    print("\n--- Simulating test setup (pytest fixture pattern) ---")
    def make_test_client():
        """What a pytest fixture looks like with a factory."""
        app = create_app(TestConfig())
        return app

    client1 = make_test_client()
    client2 = make_test_client()
    print(f"\n  client1 and client2 are separate: {client1 is not client2}")
    print("  Each test gets a fresh app with a clean database.")

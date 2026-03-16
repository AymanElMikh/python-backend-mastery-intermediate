"""
Demo: FastAPI Dependency Injection with Depends()
Level: Intermediate (2–3 years experience)
Run:  python demo.py

Simulates FastAPI's Depends() system without requiring a running server.
The real-code patterns are shown in comments throughout.
"""

from typing import Optional, Generator
from contextlib import contextmanager


# ── Simulated infrastructure ──────────────────────────────────────────────────

class FakeSession:
    """Simulates a SQLAlchemy database session."""
    def __init__(self):
        self._store = {
            1: {"id": 1, "email": "alice@x.com", "role": "admin"},
            2: {"id": 2, "email": "bob@x.com",   "role": "user"},
        }
        self.open = True
        print("    [DB] Session opened")

    def query(self, user_id: int) -> Optional[dict]:
        return self._store.get(user_id)

    def all(self) -> list:
        return list(self._store.values())

    def close(self):
        self.open = False
        print("    [DB] Session closed")


# ── Section 1: The generator dependency pattern (yield for cleanup) ───────────

def get_db() -> Generator[FakeSession, None, None]:
    """
    Classic Depends() pattern for database sessions.

    In real FastAPI:
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()

        @app.get("/users")
        def list_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = FakeSession()
    try:
        yield db          # Route runs here — db is available
    finally:
        db.close()        # Always runs, even if route raised an exception


@contextmanager
def with_db():
    """Helper to use get_db() in this demo (replaces FastAPI's request lifecycle)."""
    gen = get_db()
    db = next(gen)
    try:
        yield db
    finally:
        try:
            next(gen)
        except StopIteration:
            pass


# ── Section 2: Authentication dependency ─────────────────────────────────────

VALID_TOKENS = {
    "token-alice": {"id": 1, "email": "alice@x.com", "role": "admin"},
    "token-bob":   {"id": 2, "email": "bob@x.com",   "role": "user"},
}


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def get_current_user(authorization: Optional[str] = None) -> dict:
    """
    Auth dependency — verifies token and returns the user.

    In real FastAPI:
        from fastapi import Header, HTTPException, Depends

        def get_current_user(authorization: str = Header(...)) -> User:
            token = authorization.replace("Bearer ", "")
            user = verify_token(token)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid token")
            return user

        @app.get("/profile")
        def profile(user: User = Depends(get_current_user)):
            return {"email": user.email}
    """
    if not authorization:
        raise HTTPException(401, "Authorization header required")
    token = authorization.replace("Bearer ", "")
    user = VALID_TOKENS.get(token)
    if not user:
        raise HTTPException(401, "Invalid or expired token")
    return user


def require_admin(user: dict = None) -> dict:
    """
    Depends on get_current_user (chained dependency).
    FastAPI resolves the whole graph automatically.
    """
    if user is None:
        raise HTTPException(401, "Not authenticated")
    if user["role"] != "admin":
        raise HTTPException(403, f"Admin access required. Your role: {user['role']}")
    return user


# ── Section 3: Service dependency ────────────────────────────────────────────

class UserRepository:
    def __init__(self, db: FakeSession):
        self._db = db

    def get_by_id(self, user_id: int) -> Optional[dict]:
        return self._db.query(user_id)

    def list_all(self) -> list:
        return self._db.all()


class UserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    def get_user(self, user_id: int) -> dict:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, f"User #{user_id} not found")
        return user

    def list_users(self) -> list:
        return self._repo.list_all()


def get_user_service(db: FakeSession) -> UserService:
    """
    In FastAPI:
        def get_user_service(db: Session = Depends(get_db)) -> UserService:
            return UserService(UserRepository(db))

        @app.get("/users")
        def list_users(svc: UserService = Depends(get_user_service)):
            return svc.list_users()
    """
    return UserService(UserRepository(db))


# ── Section 4: Simulated route calls ─────────────────────────────────────────

def handle(route_fn, *args, **kwargs) -> dict:
    """Simulate FastAPI's request lifecycle: run route, handle errors."""
    try:
        result = route_fn(*args, **kwargs)
        return {"status": 200, "data": result}
    except HTTPException as e:
        return {"status": e.status_code, "error": e.detail}


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: FastAPI Depends() — Dependency Injection")
    print("=" * 55)

    print("\n--- Pattern 1: DB session dependency (with cleanup) ---")
    with with_db() as db:
        svc = get_user_service(db)
        result = handle(svc.list_users)
        print(f"  GET /users → {result}")
    # Session is closed here — guaranteed by the generator

    print("\n--- Pattern 2: Auth dependency ---")
    for token in ["Bearer token-alice", "Bearer token-bob", "Bearer bad-token", None]:
        try:
            user = get_current_user(token)
            label = token or "(no token)"
            print(f"  {label[:25]:25s} → {user['email']} [{user['role']}]")
        except HTTPException as e:
            label = token or "(no token)"
            print(f"  {label[:25]:25s} → {e.status_code}: {e.detail}")

    print("\n--- Pattern 3: Chained dependencies (auth → admin check) ---")
    for token in ["Bearer token-alice", "Bearer token-bob"]:
        try:
            user = get_current_user(token)
            admin = require_admin(user)
            print(f"  {token[:25]:25s} → Admin access granted: {admin['email']}")
        except HTTPException as e:
            print(f"  {token[:25]:25s} → {e.status_code}: {e.detail}")

    print("\n--- Pattern 4: Full route with DB + auth ---")
    def get_user_route(user_id: int, auth_header: str) -> dict:
        """Simulates: @app.get('/users/{user_id}') with Depends(get_db) + Depends(get_current_user)"""
        current_user = get_current_user(auth_header)  # auth check
        with with_db() as db:
            svc = get_user_service(db)
            return svc.get_user(user_id)

    print(f"  Alice fetches user 1:")
    print(f"  {handle(get_user_route, 1, 'Bearer token-alice')}")
    print(f"  Bob fetches user 99 (not found):")
    print(f"  {handle(get_user_route, 99, 'Bearer token-bob')}")
    print(f"  No auth token:")
    print(f"  {handle(get_user_route, 1, None)}")

    print("\n--- Common mistake: calling Depends wrong ---")
    print("  BAD:  Depends(get_db())  ← calls get_db() immediately, passes the result")
    print("  GOOD: Depends(get_db)    ← passes the function; FastAPI calls it per request")
    print()
    print("  BAD:  def get_db(): return SessionLocal()  ← no cleanup!")
    print("  GOOD: def get_db(): db=SessionLocal(); yield db; db.close()  ← cleanup runs always")

"""
Demo: DTO Pattern — Data Transfer Objects
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from dataclasses import dataclass
from typing import Optional
import hashlib


# ── Section 1: Domain model (internal, full detail) ───────────────────────────

@dataclass
class User:
    """
    The internal domain object.
    Has everything — including sensitive/internal fields.
    Should NEVER be sent directly to a client.
    """
    id: int
    email: str
    name: str
    password_hash: str     # NEVER expose this
    is_superuser: bool     # internal admin flag
    internal_notes: str    # NEVER expose this
    created_at: str


# ── Section 2: DTOs — data shapes for the API boundary ────────────────────────

@dataclass
class CreateUserRequest:
    """
    Input DTO: what the API client sends to create a user.
    Accepts a plain password (which we'll hash before storing).
    No id, no created_at — those are server-generated.
    """
    email: str
    name: str
    password: str   # comes in, gets hashed, never goes out


@dataclass
class UpdateUserRequest:
    """Input DTO for updating a user. Only updatable fields."""
    name: Optional[str] = None
    # email changes might need verification — not included here


@dataclass
class UserResponse:
    """
    Output DTO: what the API returns.
    Carefully chosen fields — no password, no internal flags, no notes.
    """
    id: int
    email: str
    name: str
    created_at: str

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        """Convert a domain User to an API-safe response."""
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
        )


@dataclass
class UserSummary:
    """
    A minimal DTO for lists — even less data than full UserResponse.
    Useful for paginated lists where you don't need all fields.
    """
    id: int
    name: str

    @classmethod
    def from_domain(cls, user: User) -> "UserSummary":
        return cls(id=user.id, name=user.name)


# ── Section 3: Service layer (works with domain objects) ─────────────────────

class FakeUserStore:
    def __init__(self):
        self._store: dict[int, User] = {}
        self._next_id = 1

    def save(self, user: User) -> User:
        user.id = self._next_id
        self._store[self._next_id] = user
        self._next_id += 1
        return user

    def get_all(self) -> list[User]:
        return list(self._store.values())

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self._store.get(user_id)


class UserService:
    def __init__(self, store: FakeUserStore):
        self._store = store

    def register(self, request: CreateUserRequest) -> User:
        """Accepts a request DTO, returns a domain object."""
        password_hash = hashlib.sha256(request.password.encode()).hexdigest()
        user = User(
            id=0,
            email=request.email,
            name=request.name,
            password_hash=password_hash,
            is_superuser=False,
            internal_notes="auto-registered via API",
            created_at="2026-03-15T10:00:00Z",
        )
        return self._store.save(user)

    def list_users(self) -> list[User]:
        return self._store.get_all()

    def get_user(self, user_id: int) -> Optional[User]:
        return self._store.get_by_id(user_id)


# ── Section 4: Route layer (converts domain → DTO before returning) ───────────

def post_user(body: CreateUserRequest, service: UserService) -> dict:
    """Route: accepts DTO, calls service, converts result to response DTO."""
    domain_user = service.register(body)
    response = UserResponse.from_domain(domain_user)
    return {
        "status": 201,
        "data": {
            "id": response.id,
            "email": response.email,
            "name": response.name,
            "created_at": response.created_at,
        }
    }


def get_users(service: UserService) -> dict:
    """Returns a summary list — even less data than full UserResponse."""
    users = service.list_users()
    summaries = [UserSummary.from_domain(u) for u in users]
    return {
        "status": 200,
        "data": [{"id": s.id, "name": s.name} for s in summaries]
    }


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: DTO Pattern")
    print("=" * 55)

    store = FakeUserStore()
    service = UserService(store)

    print("\n--- POST /users (creates user, returns safe response) ---")
    resp = post_user(
        CreateUserRequest(email="alice@example.com", name="Alice", password="s3cret"),
        service
    )
    print(f"  Response: {resp}")

    post_user(CreateUserRequest(email="bob@example.com", name="Bob", password="pass123"), service)
    post_user(CreateUserRequest(email="carol@example.com", name="Carol", password="pass456"), service)

    print("\n--- GET /users (summary list — minimal data) ---")
    resp = get_users(service)
    print(f"  Response: {resp}")

    print("\n--- Domain object has sensitive fields (NEVER sent to client) ---")
    internal_user = service.get_user(1)
    print(f"  Internal domain object for user 1:")
    print(f"    email:          {internal_user.email}")
    print(f"    password_hash:  {internal_user.password_hash[:20]}...  ← NEVER in response")
    print(f"    is_superuser:   {internal_user.is_superuser}        ← NEVER in response")
    print(f"    internal_notes: {internal_user.internal_notes!r}  ← NEVER in response")

    print("\n--- UserResponse (what client actually sees) ---")
    safe = UserResponse.from_domain(internal_user)
    print(f"  id:         {safe.id}")
    print(f"  email:      {safe.email}")
    print(f"  name:       {safe.name}")
    print(f"  created_at: {safe.created_at}")
    print("  (no password_hash, no is_superuser, no internal_notes)")

    print("\n--- Common mistake: returning domain object directly ---")
    print("  If you do: return internal_user.__dict__")
    print(f"  You'd expose: {list(internal_user.__dataclass_fields__.keys())}")
    print("  Including password_hash and internal_notes — a security leak!")

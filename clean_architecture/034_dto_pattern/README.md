# DTO Pattern — Data Transfer Objects

## 🎯 Interview Question
What is a DTO (Data Transfer Object) and why do you use them instead of passing ORM models directly through your layers?

## 💡 Short Answer (30 seconds)
A DTO is a plain object whose only job is to carry data between layers — no business logic, no database connection. You use them to define exactly what data enters your API (request DTO) and what data leaves it (response DTO), separately from your internal domain model. This prevents accidentally exposing internal fields (like password hashes) and keeps your API contract stable even when your database schema changes.

## 🔬 Explanation
Imagine you have a SQLAlchemy `User` model with 15 fields: `id`, `email`, `password_hash`, `created_at`, `updated_at`, `is_superuser`, `internal_notes`, etc.

If you return the ORM model directly from your API, you either expose `password_hash` and `internal_notes` (security risk), or you forget and it leaks in a future schema migration.

With DTOs:
- **Request DTO** (input): `CreateUserRequest(email, name, password)` — only what the client sends
- **Response DTO** (output): `UserResponse(id, email, name, created_at)` — only what the client needs
- **Domain model** (internal): `User` — the full picture, only used inside your services

In FastAPI, Pydantic models serve as DTOs. The pattern is the same with or without FastAPI.

## 💻 Code Example
```python
from pydantic import BaseModel, EmailStr
from dataclasses import dataclass

# ── Input DTO — what the API accepts ──
class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    password: str  # accepted but never returned

# ── Output DTO — what the API returns ──
class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    # no password, no internal_notes, no is_superuser

    @classmethod
    def from_domain(cls, user: "User") -> "UserResponse":
        return cls(id=user.id, email=user.email, name=user.name)

# ── Domain/DB model ──
@dataclass
class User:
    id: int
    email: str
    name: str
    password_hash: str   # internal only
    is_superuser: bool   # internal only
```

## ⚠️ Common Mistakes
1. **Returning ORM models from routes.** SQLAlchemy models are not JSON-serializable and may contain lazy-loaded relationships or sensitive fields. Always convert to a DTO before returning.
2. **One DTO for everything.** Use separate DTOs for input (request) and output (response). The fields are often different — password goes in, never out; `id` and `created_at` come out, never in.
3. **Putting validation logic in DTOs.** A DTO is a data container with basic type/format validation (via Pydantic). Complex business rules ("email must not be from a competitor domain") belong in the service layer.

## ✅ When to Use vs When NOT to Use
**Use when:**
- Building an API where the internal model and the public API contract differ
- Sensitive fields exist that should never be exposed (passwords, internal flags)
- You want a stable API contract independent of database schema changes

**Don't use when:**
- The response is 100% identical to the domain model — the conversion is pure overhead
- Internal scripts or CLI tools with no public API surface

## 🔗 Related Concepts
- [clean_architecture/032_three_layer_architecture](../032_three_layer_architecture) — DTOs live at the boundary between layers
- [fastapi](../../fastapi) — Pydantic models as DTOs is a core FastAPI pattern
- [clean_architecture/037_domain_vs_db_model](../037_domain_vs_db_model) — related: keeping domain and persistence models separate

## 🚀 Next Step
In `python-backend-mastery`: **API versioning with DTOs** — maintaining multiple response versions (`UserResponseV1`, `UserResponseV2`) to evolve your API without breaking clients.

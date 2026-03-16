# Three-Layer Architecture

## 🎯 Interview Question
Describe how you'd structure a Python backend API project. What are the layers and what does each one do?

## 💡 Short Answer (30 seconds)
A typical Python backend has three layers: the **presentation layer** (routes/controllers — handles HTTP), the **service layer** (business logic — handles rules and orchestration), and the **data layer** (repositories — handles database access). Each layer only talks to the one below it. Routes call services; services call repositories. Nothing skips a layer.

## 🔬 Explanation
Think of a restaurant: the waiter (route) takes your order and brings your food. The chef (service) decides how to make the dish and coordinates the kitchen. The pantry worker (repository) fetches the raw ingredients. The waiter never goes into the pantry; the pantry worker doesn't decide what to cook.

```
HTTP Request
    ↓
[Route Layer]        ← "presentation" — speaks HTTP, knows about requests/responses
    ↓
[Service Layer]      ← "business logic" — speaks Python, knows about your domain rules
    ↓
[Repository Layer]   ← "data access" — speaks SQL/ORM, knows about your database
    ↓
Database
```

In a FastAPI project this maps to:
- `routers/` — route handlers, Pydantic request/response schemas
- `services/` — plain Python classes with business rules
- `repositories/` — SQLAlchemy queries

## 💻 Code Example
```
project/
├── routers/
│   └── users.py        ← Route layer: HTTP only
├── services/
│   └── user_service.py ← Service layer: business rules
├── repositories/
│   └── user_repo.py    ← Data layer: DB queries
├── models/
│   └── user.py         ← SQLAlchemy model
└── schemas/
    └── user_schema.py  ← Pydantic request/response models
```

```python
# routers/users.py
@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(body: CreateUserRequest, service: UserService = Depends(get_user_service)):
    return service.register(body.email, body.name)

# services/user_service.py
class UserService:
    def register(self, email: str, name: str) -> User:
        if self._repo.find_by_email(email):
            raise EmailAlreadyExists(email)
        return self._repo.save(User(email=email, name=name))

# repositories/user_repo.py
class UserRepository:
    def find_by_email(self, email: str) -> User | None:
        return self._session.query(User).filter_by(email=email).first()
```

## ⚠️ Common Mistakes
1. **Skipping layers.** Route calling repository directly (bypassing the service) means you can't enforce business rules consistently. Always route → service → repository.
2. **Circular imports.** If your service imports from your router (e.g., to access request context), you've broken the layering. Data should only flow down, never up.
3. **Anemic service layer.** A service that just calls `repo.save(data)` with no logic isn't a service layer — it's indirection for its own sake. Services should contain real decisions and rules.

## ✅ When to Use vs When NOT to Use
**Use when:**
- Building any API with more than a few endpoints
- The project will grow and be maintained over time
- Multiple developers work on the codebase

**Don't use when:**
- Throwaway scripts, one-off data migrations, or tiny tools
- Prototypes where speed of development matters more than structure (but plan to refactor)

## 🔗 Related Concepts
- [clean_architecture/031_separation_of_concerns](../031_separation_of_concerns) — the principle behind this structure
- [clean_architecture/033_dependency_injection](../033_dependency_injection) — how layers get wired together
- [clean_architecture/035_service_layer](../035_service_layer) — deep dive into the service layer
- [design_patterns/026_repository_pattern](../../design_patterns/026_repository_pattern) — the data layer in detail

## 🚀 Next Step
In `python-backend-mastery`: **Clean Architecture / Onion Architecture** — inverting the dependency direction so the domain core has zero dependencies, and all infrastructure (DB, HTTP) depends on the domain instead.

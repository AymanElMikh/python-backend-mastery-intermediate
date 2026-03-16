# Separation of Concerns

## 🎯 Interview Question
What does "separation of concerns" mean in a Python backend project, and why does it matter?

## 💡 Short Answer (30 seconds)
Separation of concerns means each part of your code has one clear job, and those jobs don't bleed into each other. Your route handler handles the HTTP layer. Your service handles business logic. Your repository handles database access. When they're mixed together, changing one thing breaks others and testing becomes painful.

## 🔬 Explanation
The most common violation in junior/mid Python backends: a FastAPI or Flask route function that does everything — validates the request, queries the database directly, applies business rules, formats the response, and sends an email, all in one 60-line function.

The problem isn't that it works. It does work. The problem is:
- To test the business rule, you need a full HTTP request + real database
- To change the email provider, you dig through route code
- To reuse the "create user" logic in a CLI script, you can't — it's tangled in Flask

Separation of concerns gives each layer a boundary:
- **Routes** — parse HTTP input, call the service, return HTTP output
- **Services** — pure Python, business rules only, no HTTP, no SQL
- **Repositories** — SQL/ORM only, no business rules

Each layer can be tested, changed, and reused independently.

## 💻 Code Example
```python
# ❌ BAD — everything in one place
@app.post("/users")
def create_user(data: dict):
    if not data.get("email"):
        return {"error": "email required"}, 400
    if db.query(User).filter_by(email=data["email"]).first():
        return {"error": "already exists"}, 409
    user = User(email=data["email"])
    db.add(user)
    db.commit()
    send_welcome_email(user.email)  # email logic in route!
    return {"id": user.id}

# ✅ GOOD — each layer has one job
# route.py
@app.post("/users")
def create_user(body: CreateUserRequest):
    user = user_service.register(body.email)  # one call
    return UserResponse.from_domain(user)

# service.py
def register(email: str) -> User:
    if user_repo.find_by_email(email):
        raise EmailAlreadyExistsError(email)
    user = user_repo.save(User(email=email))
    email_service.send_welcome(user.email)
    return user

# repository.py
def find_by_email(email: str) -> User | None:
    return db.query(User).filter_by(email=email).first()
```

## ⚠️ Common Mistakes
1. **Putting SQL queries in route handlers.** The route handler should never import SQLAlchemy models or call `db.query()` directly. That's the repository's job.
2. **Putting business rules in repositories.** "Find all users who are eligible for a discount" should be in the service. Repositories just fetch data.
3. **Using response models inside services.** A service should return domain objects, not JSON-ready dicts or Pydantic response models. The route layer handles that conversion.

## ✅ When to Use vs When NOT to Use
**Always apply** — this isn't optional in production code. Even a small app benefits from separation because it grows.

**Degree of formality varies:**
- Tiny script or one-off tool → a single file is fine
- API with 3+ endpoints → apply the 3-layer structure
- API with 10+ endpoints → enforce strict layer boundaries

## 🔗 Related Concepts
- [clean_architecture/032_three_layer_architecture](../032_three_layer_architecture) — the concrete 3-layer structure
- [clean_architecture/035_service_layer](../035_service_layer) — deep dive into the service layer
- [design_patterns/026_repository_pattern](../../design_patterns/026_repository_pattern) — the data access layer

## 🚀 Next Step
In `python-backend-mastery`: **Hexagonal Architecture (Ports & Adapters)** — a stricter formalization where the core domain has zero knowledge of the outside world; all I/O goes through defined ports.

# Dependency Injection

## 🎯 Interview Question
What is dependency injection and how do you use it in a Python backend project without a DI framework?

## 💡 Short Answer (30 seconds)
Dependency injection means a class receives its dependencies from the outside rather than creating them internally. Instead of `UserService` calling `UserRepository()` inside its `__init__`, you pass the repository in: `UserService(repo)`. This makes the service testable (you inject a fake repo in tests) and flexible (you can swap implementations without touching the service code).

## 🔬 Explanation
"Dependency injection" sounds fancy but the core idea is simple: don't `new` up your dependencies inside a class. Pass them in.

Without DI:
```python
class UserService:
    def __init__(self):
        self._repo = UserRepository()  # hardcoded — can't swap, can't test
        self._email = SendGridClient()  # hardcoded — calls real email in tests!
```

With DI:
```python
class UserService:
    def __init__(self, repo: UserRepository, email: EmailService):
        self._repo = repo    # injected from outside
        self._email = email  # injected from outside
```

In tests you pass fakes. In production you pass the real implementations. The service itself never changes.

FastAPI has a built-in `Depends()` system that does DI at the request level. For simpler apps, manually wiring dependencies in a `dependencies.py` or `container.py` file works well.

## 💻 Code Example
```python
# Manual DI (no framework)
def get_user_service() -> UserService:
    repo = UserRepository(db_session)
    email = SendGridEmailService(api_key=settings.SENDGRID_KEY)
    return UserService(repo, email)

# FastAPI-style DI with Depends
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db), EmailService())

@router.post("/users")
def create_user(body: CreateUserRequest, svc: UserService = Depends(get_user_service)):
    return svc.register(body.email)
```

## ⚠️ Common Mistakes
1. **Creating dependencies inside `__init__`.** `self._repo = UserRepository()` inside the service defeats the whole purpose. Always accept dependencies as constructor parameters.
2. **Passing too many dependencies.** If a class needs 6+ injected dependencies, it's doing too much. Split it into smaller services.
3. **Leaking infrastructure into the domain.** Don't inject a `SQLAlchemy Session` directly into a service — inject a `Repository` that wraps the session. The service shouldn't know it's talking to SQLAlchemy.

## ✅ When to Use vs When NOT to Use
**Always use DI for:**
- Database connections / sessions
- External API clients (email, SMS, payment)
- Configuration/settings objects

**Don't bother for:**
- Pure utility functions that have no external dependencies
- Simple value objects (dataclasses, configs) — just pass the values

## 🔗 Related Concepts
- [clean_architecture/031_separation_of_concerns](../031_separation_of_concerns) — DI is how layers stay separated
- [clean_architecture/035_service_layer](../035_service_layer) — services are the primary recipient of DI
- [design_patterns/026_repository_pattern](../../design_patterns/026_repository_pattern) — repositories are the classic injected dependency
- [unit_tests](../../unit_tests) — DI makes mocking easy in tests

## 🚀 Next Step
In `python-backend-mastery`: **DI containers** (`dependency-injector` library) — automatic wiring of dependency graphs, scoped lifetimes (singleton vs per-request), and lazy initialization.

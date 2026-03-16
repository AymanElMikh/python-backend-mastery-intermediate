# FastAPI Dependency Injection with `Depends()`

## 🎯 Interview Question
How does FastAPI's `Depends()` system work, and what are its main use cases?

## 💡 Short Answer (30 seconds)
`Depends()` is FastAPI's built-in dependency injection system. You define a function that creates or provides something — a database session, a current user, a service instance — and declare it as a parameter with `Depends(your_function)`. FastAPI calls the dependency function automatically before calling your route, injects the result, and if the dependency is a generator (using `yield`), handles cleanup after the response too.

## 🔬 Explanation
Three main use cases:

**1. Database sessions** — the classic use:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db        # give the session to the route
    finally:
        db.close()      # always close, even if the route raises

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

**2. Authentication** — check the request has a valid token:
```python
def get_current_user(token: str = Header(...)) -> User:
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401)
    return user

@app.get("/profile")
def my_profile(user: User = Depends(get_current_user)):
    return {"email": user.email}
```

**3. Service injection** — create your service with its dependencies:
```python
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))

@app.post("/users")
def create_user(body: CreateUserRequest, svc: UserService = Depends(get_user_service)):
    return svc.register(body.email)
```

## ⚠️ Common Mistakes
1. **Calling the dependency function instead of passing it.** `Depends(get_db())` (with parentheses) calls `get_db` immediately and passes the result. You want `Depends(get_db)` — pass the function reference.
2. **Forgetting `yield` for cleanup.** If your dependency opens a resource (DB session, file handle), use `yield` so FastAPI can guarantee cleanup. A plain `return` won't run cleanup code after the route finishes.
3. **Over-nesting dependencies.** FastAPI resolves a dependency graph — each dependency can have its own `Depends`. This is powerful but can get hard to follow. Keep the graph shallow (max 2-3 levels).

## ✅ When to Use `Depends()`
**Always use for:**
- Database sessions (one per request)
- Authentication and authorization checks
- Service instances that need per-request scope

**Skip `Depends()` for:**
- Module-level singletons (settings, read-only config) — just import them
- Pure utility functions — just call them directly

## 🔗 Related Concepts
- [clean_architecture/033_dependency_injection](../../clean_architecture/033_dependency_injection) — the general DI concept
- [fastapi/046_http_exception](../046_http_exception) — dependencies often raise HTTPException for auth failures
- [fastapi/041_routes_path_params](../041_routes_path_params) — dependencies are just another kind of "parameter"

## 🚀 Next Step
In `python-backend-mastery`: **Dependency scopes and caching** — `Depends(use_cache=True)` (the default) reuses the same dependency instance within a request; understanding when to disable that, and background task dependencies.

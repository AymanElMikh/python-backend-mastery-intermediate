# FastAPI Routers & Tags

## 🎯 Interview Question
How do you organize routes in a large FastAPI application, and what is `APIRouter` used for?

## 💡 Short Answer (30 seconds)
`APIRouter` is FastAPI's equivalent of Flask's blueprints — it lets you define routes in separate files and then include them in the main app with a common prefix. For example, all user routes live in `routers/users.py`, all order routes in `routers/orders.py`. You include them with `app.include_router(users_router, prefix="/users", tags=["users"])`. Tags group routes in the auto-generated Swagger UI docs.

## 🔬 Explanation
In a small app, all routes in `main.py` is fine. Once you have 20+ routes, that file becomes unmanageable. `APIRouter` lets you split routes logically:

```
app/
├── main.py           ← creates the FastAPI app, includes all routers
├── routers/
│   ├── users.py      ← APIRouter() with /users routes
│   ├── orders.py     ← APIRouter() with /orders routes
│   └── admin.py      ← APIRouter() with /admin routes, requires admin auth
```

Benefits:
- Each router file is small and focused
- You can apply a prefix, tags, and dependencies to all routes in a router at once
- Admin routes can have an auth dependency applied to the whole router instead of each individual route

## 💻 Code Example
```python
# routers/users.py
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/")           # becomes GET /users/
def list_users(): ...

@router.get("/{user_id}")  # becomes GET /users/{user_id}
def get_user(user_id: int): ...

@router.post("/")          # becomes POST /users/
def create_user(): ...


# routers/admin.py
from fastapi import APIRouter, Depends
from .dependencies import require_admin

admin_router = APIRouter(
    dependencies=[Depends(require_admin)]  # all routes require admin
)

@admin_router.delete("/users/{user_id}")
def admin_delete_user(user_id: int): ...


# main.py
from fastapi import FastAPI
from .routers import users, admin

app = FastAPI()
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(admin.admin_router, prefix="/admin", tags=["Admin"])
```

## ⚠️ Common Mistakes
1. **Not using a prefix, then duplicating it in every route.** `@router.get("/users/")` in the router file when you'll include with `prefix="/users"` results in `/users/users/`. Define routes relative to the prefix — `@router.get("/")`.
2. **One giant router file.** If you just move all routes to one `routers.py`, you haven't gained anything. Split by domain concept: users, orders, products, auth.
3. **Forgetting tags.** Tags group routes in Swagger UI. Without them, all routes appear in a single ungrouped list. Always tag your routers.

## ✅ When to Use `APIRouter`
**Always use** once your app has more than one domain concept (users + orders = time to split).

**One router per domain concept** — `UsersRouter`, `OrdersRouter`, `AuthRouter`, `AdminRouter`.

## 🔗 Related Concepts
- [fastapi/044_depends_di](../044_depends_di) — apply dependencies to a whole router
- [fastapi/046_http_exception](../046_http_exception) — exception handling applies globally, not per router
- [clean_architecture/032_three_layer_architecture](../../clean_architecture/032_three_layer_architecture) — routers are the presentation layer

## 🚀 Next Step
In `python-backend-mastery`: **Router-level middleware and OpenAPI customization** — adding per-router request/response logging, customizing operation IDs for clean OpenAPI specs, and generating typed TypeScript/Python clients from the OpenAPI schema.

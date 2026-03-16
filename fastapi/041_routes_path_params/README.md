# FastAPI Routes & Path Parameters

## 🎯 Interview Question
How do you define routes in FastAPI, and what's the difference between a path parameter and a query parameter?

## 💡 Short Answer (30 seconds)
In FastAPI, routes are defined with decorators like `@app.get("/users/{user_id}")`. A **path parameter** is part of the URL path itself — `{user_id}` in `/users/42` — and is required. A **query parameter** comes after the `?` in the URL — `/users?page=2&limit=10` — and is usually optional. FastAPI reads the type annotation on the function argument to decide which is which and to validate + convert the value automatically.

## 🔬 Explanation
FastAPI's routing is built on Starlette. When you write:

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    ...
```

FastAPI does three things automatically:
1. **Registers** the route `/users/{user_id}` for GET requests
2. **Extracts** `user_id` from the URL and **converts** it from string → int
3. **Validates** it — if `user_id` is `"abc"`, FastAPI returns a 422 before your function is even called

This is completely different from Flask where you handle conversion and validation yourself.

## 💻 Code Example
```python
from fastapi import FastAPI

app = FastAPI()

# Path parameter — required, part of the URL
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

# Multiple path params
@app.get("/orgs/{org_id}/users/{user_id}")
def get_org_user(org_id: str, user_id: int):
    return {"org": org_id, "user": user_id}

# GET /users/42        → {"user_id": 42}
# GET /users/abc       → 422 Unprocessable Entity (not an int)
# GET /orgs/acme/users/7 → {"org": "acme", "user": 7}
```

## ⚠️ Common Mistakes
1. **Ordering routes wrong.** If you define `/users/me` after `/users/{user_id}`, FastAPI matches `/users/me` as `user_id="me"` (and fails the int cast). Define specific routes before parameterized ones.
2. **Not using type annotations.** Without `user_id: int`, FastAPI treats the parameter as a string and skips validation. Always annotate.
3. **Confusing path params with query params.** Path params are in the URL path with `{}`. Query params are plain function args (no `{}`). FastAPI distinguishes them by whether the name appears in the path string.

## ✅ When to Use Path Params vs Query Params
**Path parameters** — when the param identifies a specific resource:
- `/users/{user_id}` — identifies which user
- `/orders/{order_id}/items/{item_id}` — identifies nested resource

**Query parameters** — for filtering, pagination, optional modifiers:
- `/users?role=admin&page=2` — filter and paginate
- `/search?q=laptop&sort=price` — search options

## 🔗 Related Concepts
- [fastapi/042_query_params](../042_query_params) — the other kind of URL parameter
- [fastapi/043_pydantic_models](../043_pydantic_models) — Pydantic validates and converts request bodies
- [fastapi/047_routers_tags](../047_routers_tags) — organizing routes into blueprints/routers

## 🚀 Next Step
In `python-backend-mastery`: **Custom path parameter validation** — using `Annotated` + `Path(ge=1, le=1000)` for constraint validation on path params, and custom route converters for complex patterns.

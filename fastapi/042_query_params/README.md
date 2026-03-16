# FastAPI Query Parameters

## 🎯 Interview Question
How do query parameters work in FastAPI, and how do you make them optional with defaults?

## 💡 Short Answer (30 seconds)
In FastAPI, any function parameter that is NOT in the path string is treated as a query parameter. You make it optional by giving it a default value — `page: int = 1`. If the default is `None`, the type hint should be `Optional[str]` or `str | None`. FastAPI validates the type and converts it automatically, just like path params.

## 🔬 Explanation
Query parameters come from the URL after `?`: `/users?role=admin&page=2&limit=25`.

FastAPI figures out what's a path param vs query param by checking whether the name appears in the path pattern:
- If `{user_id}` is in `/users/{user_id}` → path param
- If `page` is NOT in the path → query param

You can mix them: `/users/{user_id}/orders?status=pending&page=1` — `user_id` is a path param, `status` and `page` are query params.

Common patterns:
- `page: int = 1` — optional, defaults to 1
- `limit: int = 20` — optional, defaults to 20
- `role: str | None = None` — optional, defaults to None (no filtering)
- `q: str` — required query param (no default, not Optional)

## 💻 Code Example
```python
from fastapi import FastAPI
from typing import Optional

app = FastAPI()

@app.get("/users")
def list_users(
    page: int = 1,
    limit: int = 20,
    role: Optional[str] = None,
    is_active: bool = True,
):
    return {
        "page": page,
        "limit": limit,
        "role": role,
        "is_active": is_active,
    }

# GET /users                       → page=1, limit=20, role=None, is_active=True
# GET /users?page=3&limit=5        → page=3, limit=5
# GET /users?role=admin            → role="admin"
# GET /users?is_active=false       → is_active=False  (auto-converts "false" → bool)
# GET /users?limit=abc             → 422 (not an int)
```

## ⚠️ Common Mistakes
1. **Forgetting `Optional` when the default is `None`.** `role: str = None` technically works in Python but is wrong — use `role: str | None = None` or `Optional[str] = None` to be explicit and correct.
2. **Using query params for resource identity.** `GET /users?id=42` should be `GET /users/42`. Query params are for filtering and options, not resource identity.
3. **Not validating ranges.** `limit: int = 20` allows `limit=10000`, which could page-dump your database. Use `Query(ge=1, le=100)` to constrain values.

## ✅ When to Use Query Params
**Use for:**
- Pagination: `?page=2&limit=20`
- Filtering: `?status=active&role=admin`
- Sorting: `?sort=name&order=asc`
- Search: `?q=laptop`
- Feature flags: `?include_deleted=true`

**Don't use for:**
- Resource identity (use path params)
- Authentication tokens (use headers)
- Large data payloads (use request body)

## 🔗 Related Concepts
- [fastapi/041_routes_path_params](../041_routes_path_params) — path params vs query params
- [fastapi/048_request_validation](../048_request_validation) — `Query()` for constraints on query params
- [api_design](../../api_design) — REST conventions for pagination and filtering

## 🚀 Next Step
In `python-backend-mastery`: **`Query()` with advanced validation** — `Query(alias="page_number", min_length=1, regex=r"^\d+$")`, deprecated params, and OpenAPI documentation annotations.

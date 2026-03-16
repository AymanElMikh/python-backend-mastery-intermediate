# Request Validation in FastAPI

## 🎯 Interview Question
How do you add constraints and custom validation to request fields in FastAPI beyond basic type checking?

## 💡 Short Answer (30 seconds)
Use Pydantic's `Field()` inside your model to set constraints like `min_length`, `max_length`, `ge` (greater-or-equal), `le` (less-or-equal), `pattern` for regex. For query and path parameters, use `Query()` and `Path()` the same way. For cross-field business rules, use Pydantic's `@field_validator` or `@model_validator`. FastAPI returns a 422 with detailed error messages automatically when any constraint fails.

## 🔬 Explanation
There are three levels of validation in FastAPI:

**Level 1 — Type validation** (free, automatic): `age: int` fails if age isn't a number.

**Level 2 — Constraint validation** (`Field()`, `Query()`, `Path()`): `age: int = Field(ge=0, le=150)` ensures the number is in range.

**Level 3 — Custom validators** (`@field_validator`, `@model_validator`): check business rules like "end_date must be after start_date" or "at least one contact method must be provided."

The key principle: **format and constraints go in Pydantic validators; business rules go in the service layer.** Pydantic validators should be stateless and only inspect the data they're given. Anything that requires a database query or external state belongs in the service.

## 💻 Code Example
```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class CreateProductRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(gt=0, description="Price in USD, must be positive")
    category: str = Field(pattern=r"^[a-z_]+$")  # lowercase slug
    stock: int = Field(ge=0, default=0)
    tags: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("name")
    @classmethod
    def name_not_reserved(cls, v: str) -> str:
        reserved = {"test", "admin", "null"}
        if v.lower() in reserved:
            raise ValueError(f"'{v}' is a reserved name")
        return v.strip()

# In routes:
@app.get("/users")
def list_users(
    page: int = Query(ge=1, default=1),
    limit: int = Query(ge=1, le=100, default=20),
    email: str = Query(default=None, pattern=r".+@.+\..+"),
):
    ...
```

## ⚠️ Common Mistakes
1. **Putting database checks in `@field_validator`.** `email already exists` is a business rule that requires querying the DB. It belongs in the service, not in a Pydantic validator.
2. **Not constraining `limit` in pagination.** `limit: int = 0` allows `?limit=1000000` which can dump your entire database. Always add `Query(le=100)` or similar.
3. **Forgetting `@classmethod` on `@field_validator`.** In Pydantic v2, validators must be class methods. Omitting `@classmethod` causes a confusing error.

## ✅ What Goes in Pydantic Validators vs Service Layer
**Pydantic validators:**
- Format checks (valid email format, valid slug pattern)
- Range constraints (price > 0, age between 0-150)
- Cross-field consistency (end_date > start_date)
- Normalization (strip whitespace, lowercase)

**Service layer:**
- Uniqueness (email not already registered)
- Permission checks (user can edit this resource)
- Business rules that depend on state

## 🔗 Related Concepts
- [fastapi/043_pydantic_models](../043_pydantic_models) — Pydantic model basics
- [fastapi/042_query_params](../042_query_params) — Query() for query parameter constraints
- [clean_architecture/038_custom_exceptions](../../clean_architecture/038_custom_exceptions) — where business rules live

## 🚀 Next Step
In `python-backend-mastery`: **Custom Pydantic types and annotated validators** — creating reusable `PositivePrice`, `Slug`, `UserId` types with `Annotated[float, Field(gt=0)]` that work across all your models.

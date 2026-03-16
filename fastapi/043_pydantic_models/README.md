# Pydantic Models in FastAPI

## 🎯 Interview Question
What role do Pydantic models play in FastAPI, and how do they differ from plain Python dataclasses?

## 💡 Short Answer (30 seconds)
Pydantic models are how FastAPI handles request body parsing and response serialization. When you declare a function parameter as `body: CreateUserRequest` (a Pydantic model), FastAPI automatically parses the JSON body, validates every field, coerces types, and returns a 422 with descriptive errors if anything is wrong — all before your function runs. Dataclasses don't do any of that automatically.

## 🔬 Explanation
Pydantic's `BaseModel` gives you:
- **Parsing**: JSON → typed Python object, automatically
- **Validation**: email format, string length, numeric ranges
- **Type coercion**: `"42"` → `42` if the field is `int`
- **Serialization**: `.model_dump()` converts back to dict for JSON responses
- **Documentation**: FastAPI auto-generates OpenAPI/Swagger docs from Pydantic models

The typical pattern for a route:
1. Define a request model for input (`CreateUserRequest`)
2. Define a response model for output (`UserResponse`)
3. Route function receives the request model, returns the response model
4. FastAPI handles all JSON parsing and serialization

## 💻 Code Example
```python
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class CreateUserRequest(BaseModel):
    email: EmailStr           # validated as a real email address
    name: str
    age: int
    role: str = "user"        # optional with default

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    # no password_hash, no internal fields

    model_config = {"from_attributes": True}  # lets you do from_orm(db_model)

# Validator: custom field-level rule
class ProductRequest(BaseModel):
    name: str
    price: float

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be positive")
        return v

# In your route:
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(body: CreateUserRequest):
    # body.email, body.name, body.age — already validated
    ...
```

## ⚠️ Common Mistakes
1. **Using `response_model` to return ORM models directly.** `response_model=UserORM` exposes all ORM fields including sensitive ones. Always use a dedicated response model with only the fields you want to expose.
2. **Forgetting `model_config = {"from_attributes": True}`.** Without this, `UserResponse.model_validate(orm_obj)` fails because Pydantic won't read from object attributes by default.
3. **Putting business logic in validators.** Pydantic validators should check data shape and format (valid email, positive number). Business rules ("email must not be from a competitor") belong in the service layer.

## ✅ When to Use Pydantic vs Dataclasses
**Pydantic** (`BaseModel`) — whenever you need validation, parsing from dicts/JSON, or serialization. Use for all API request/response models.

**Dataclasses** — for internal domain objects that are passed between layers in Python. No validation overhead, no JSON parsing — just structured data.

## 🔗 Related Concepts
- [clean_architecture/034_dto_pattern](../../clean_architecture/034_dto_pattern) — Pydantic models ARE the DTOs in FastAPI
- [fastapi/048_request_validation](../048_request_validation) — deeper validation with `Field()` and validators
- [fastapi/045_status_codes_responses](../045_status_codes_responses) — `response_model` controls what gets serialized

## 🚀 Next Step
In `python-backend-mastery`: **Pydantic v2 advanced features** — `model_validator`, `computed_field`, `model_serializer`, discriminated unions for polymorphic models, and performance gains from the Rust-based v2 core.

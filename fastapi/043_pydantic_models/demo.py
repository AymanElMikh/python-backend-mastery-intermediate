"""
Demo: Pydantic Models in FastAPI
Level: Intermediate (2–3 years experience)
Run:  python demo.py

Requires: pip install pydantic
(pydantic is installed with fastapi, or standalone: pip install pydantic[email])
"""

try:
    from pydantic import BaseModel, field_validator, model_validator, ValidationError
    from typing import Optional
    import json
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("Pydantic not installed. Run: pip install pydantic[email]")
    print("Showing code examples only.\n")


# ── Section 1: Basic request and response models ──────────────────────────────

if PYDANTIC_AVAILABLE:

    class CreateUserRequest(BaseModel):
        """Request body for POST /users — what the client sends."""
        name: str
        email: str
        age: int
        role: str = "user"           # optional with default
        bio: Optional[str] = None    # truly optional, can be null


    class UserResponse(BaseModel):
        """Response for GET /users/{id} — what the API returns."""
        id: int
        name: str
        email: str
        role: str
        # No age, no bio in response — deliberate choice


    # ── Section 2: Field validators ───────────────────────────────────────────

    class ProductRequest(BaseModel):
        name: str
        price: float
        category: str
        stock: int = 0

        @field_validator("price")
        @classmethod
        def price_must_be_positive(cls, v: float) -> float:
            if v <= 0:
                raise ValueError("price must be greater than 0")
            return round(v, 2)   # normalize to 2 decimal places

        @field_validator("name")
        @classmethod
        def name_not_empty(cls, v: str) -> str:
            v = v.strip()
            if not v:
                raise ValueError("name cannot be empty or whitespace")
            return v

        @field_validator("category")
        @classmethod
        def valid_category(cls, v: str) -> str:
            allowed = {"electronics", "clothing", "books", "food"}
            if v.lower() not in allowed:
                raise ValueError(f"category must be one of: {allowed}")
            return v.lower()


    # ── Section 3: Cross-field validation with model_validator ────────────────

    class DateRangeRequest(BaseModel):
        start_date: str   # "YYYY-MM-DD"
        end_date: str
        max_days: int = 30

        @model_validator(mode="after")
        def end_must_be_after_start(self) -> "DateRangeRequest":
            if self.end_date < self.start_date:
                raise ValueError("end_date must be after start_date")
            return self


    # ── Section 4: Parsing from different sources ─────────────────────────────

    def simulate_post(raw_json: str, model_class) -> dict:
        """Simulate FastAPI parsing a JSON request body."""
        try:
            data = json.loads(raw_json)
            obj = model_class(**data)
            return {"status": 201, "data": obj.model_dump()}
        except ValidationError as e:
            # FastAPI converts this to a 422 response automatically
            errors = [
                {"field": ".".join(str(x) for x in err["loc"]), "msg": err["msg"]}
                for err in e.errors()
            ]
            return {"status": 422, "errors": errors}
        except json.JSONDecodeError as e:
            return {"status": 400, "error": f"Invalid JSON: {e}"}


    if __name__ == "__main__":
        print("=" * 55)
        print("DEMO: Pydantic Models in FastAPI")
        print("=" * 55)

        print("\n--- Valid user creation ---")
        resp = simulate_post(
            '{"name": "Alice", "email": "alice@example.com", "age": 30}',
            CreateUserRequest
        )
        print(f"  → {resp['status']}: {resp['data']}")

        print("\n--- Type coercion: age as string '25' becomes int 25 ---")
        resp = simulate_post(
            '{"name": "Bob", "email": "bob@example.com", "age": "25"}',
            CreateUserRequest
        )
        print(f"  → {resp['status']}: {resp.get('data', resp.get('errors'))}")

        print("\n--- Missing required field ---")
        resp = simulate_post('{"name": "Carol"}', CreateUserRequest)
        print(f"  → {resp['status']}: {resp.get('errors')}")

        print("\n--- Wrong type for age ---")
        resp = simulate_post(
            '{"name": "Dave", "email": "dave@x.com", "age": "notanumber"}',
            CreateUserRequest
        )
        print(f"  → {resp['status']}: {resp.get('errors')}")

        print("\n--- Product with field validators ---")
        resp = simulate_post(
            '{"name": "  Laptop  ", "price": "999.999", "category": "Electronics"}',
            ProductRequest
        )
        print(f"  Valid: → {resp['status']}: {resp.get('data')}")

        resp = simulate_post(
            '{"name": "", "price": -10, "category": "weapons"}',
            ProductRequest
        )
        print(f"  Invalid: → {resp['status']}:")
        for err in resp.get("errors", []):
            print(f"    field={err['field']}: {err['msg']}")

        print("\n--- Cross-field validation ---")
        resp = simulate_post(
            '{"start_date": "2026-01-01", "end_date": "2026-01-15"}',
            DateRangeRequest
        )
        print(f"  Valid range → {resp['status']}: {resp.get('data')}")

        resp = simulate_post(
            '{"start_date": "2026-06-01", "end_date": "2026-01-01"}',
            DateRangeRequest
        )
        print(f"  Bad range → {resp['status']}: {resp.get('errors')}")

        print("\n--- Response model filtering ---")
        # Pydantic only serializes the fields defined in the model
        user_resp = UserResponse(id=1, name="Alice", email="alice@x.com", role="admin")
        print(f"  UserResponse fields: {list(user_resp.model_dump().keys())}")
        print(f"  (age and bio are NOT in UserResponse — never exposed)")

        print("\n--- Pydantic vs dataclass comparison ---")
        from dataclasses import dataclass as dc

        @dc
        class UserDC:
            name: str
            age: int

        user_dc = UserDC(name="Alice", age="not-a-number")  # silently accepts!
        print(f"  Dataclass with age='not-a-number': age={user_dc.age!r}  ← NO validation")

        try:
            user_pm = CreateUserRequest(name="Alice", email="x@x.com", age="not-a-number")
        except ValidationError as e:
            print(f"  Pydantic with age='not-a-number': ValidationError ← caught immediately")

else:
    print("""
Real FastAPI Pydantic usage (requires: pip install pydantic):

from pydantic import BaseModel, field_validator
from typing import Optional

class CreateUserRequest(BaseModel):
    name: str
    email: str
    age: int
    role: str = "user"
    bio: Optional[str] = None

    @field_validator("age")
    @classmethod
    def age_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("age must be positive")
        return v

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

# In FastAPI route:
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(body: CreateUserRequest):
    user = user_service.register(body.email, body.name, body.age)
    return UserResponse(id=user.id, name=user.name, email=user.email)
""")

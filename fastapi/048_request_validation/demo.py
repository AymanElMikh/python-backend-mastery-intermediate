"""
Demo: Request Validation in FastAPI
Level: Intermediate (2–3 years experience)
Run:  python demo.py

Requires: pip install pydantic
"""

try:
    from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
    from typing import Optional
    import json
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("Run: pip install pydantic")

if PYDANTIC_AVAILABLE:

    # ── Section 1: Field() constraints ───────────────────────────────────────

    class CreateProductRequest(BaseModel):
        name: str = Field(
            min_length=2,
            max_length=100,
            description="Product name, 2-100 characters",
        )
        price: float = Field(
            gt=0,
            description="Price in USD — must be greater than 0",
        )
        category: str = Field(
            pattern=r"^[a-z][a-z_]*[a-z]$",
            description="Lowercase slug, e.g. 'electronics' or 'home_goods'",
        )
        stock: int = Field(ge=0, default=0)
        tags: list[str] = Field(default_factory=list, max_length=5,
                                 description="Max 5 tags")
        discount_pct: float = Field(ge=0, le=100, default=0,
                                     description="Discount 0-100%")

        @field_validator("name")
        @classmethod
        def name_not_reserved(cls, v: str) -> str:
            reserved = {"test", "admin", "null", "undefined"}
            if v.strip().lower() in reserved:
                raise ValueError(f"'{v}' is a reserved name")
            return v.strip()  # normalize: strip whitespace

        @field_validator("tags")
        @classmethod
        def tags_lowercase(cls, tags: list[str]) -> list[str]:
            return [t.strip().lower() for t in tags]


    # ── Section 2: Cross-field validation ────────────────────────────────────

    class SalePeriodRequest(BaseModel):
        start_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
        end_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
        discount_pct: float = Field(gt=0, le=100)

        @model_validator(mode="after")
        def end_after_start(self) -> "SalePeriodRequest":
            if self.end_date <= self.start_date:
                raise ValueError(
                    f"end_date ({self.end_date}) must be after start_date ({self.start_date})"
                )
            return self


    # ── Section 3: Query parameter constraints (equivalent to Query()) ────────

    class ListProductsQuery:
        """
        Simulates: page: int = Query(ge=1, default=1)
        In real FastAPI, you'd use Query() directly in the function signature.
        """
        def __init__(
            self,
            page: int = 1,
            limit: int = 20,
            min_price: float = 0,
            max_price: float = 999999,
        ):
            errors = []
            if page < 1:
                errors.append(f"page must be >= 1, got {page}")
            if not (1 <= limit <= 100):
                errors.append(f"limit must be 1-100, got {limit}")
            if min_price < 0:
                errors.append(f"min_price must be >= 0, got {min_price}")
            if max_price < min_price:
                errors.append(f"max_price ({max_price}) must be >= min_price ({min_price})")
            if errors:
                raise ValueError("; ".join(errors))
            self.page = page
            self.limit = limit
            self.min_price = min_price
            self.max_price = max_price


    # ── Section 4: Helpers ────────────────────────────────────────────────────

    def try_create(data: dict, model_class=CreateProductRequest) -> dict:
        try:
            obj = model_class(**data)
            return {"status": 201, "data": obj.model_dump()}
        except ValidationError as e:
            return {
                "status": 422,
                "errors": [
                    {"field": ".".join(str(x) for x in err["loc"]),
                     "msg": err["msg"],
                     "type": err["type"]}
                    for err in e.errors()
                ]
            }


    def show(label: str, data: dict, model_class=CreateProductRequest):
        resp = try_create(data, model_class)
        status = resp["status"]
        if status == 201:
            print(f"  ✓ {label:45s} → {status}: {resp['data']}")
        else:
            msgs = [f"{e['field']}: {e['msg']}" for e in resp["errors"]]
            print(f"  ✗ {label:45s} → {status}:")
            for m in msgs:
                print(f"      {m}")


    if __name__ == "__main__":
        print("=" * 55)
        print("DEMO: Request Validation in FastAPI")
        print("=" * 55)

        print("\n--- Valid products ---")
        show(
            "Full valid product",
            {"name": "Wireless Mouse", "price": 29.99, "category": "electronics",
             "stock": 50, "tags": ["WIRELESS", "  USB  "], "discount_pct": 10},
        )
        show(
            "Minimal product (defaults)",
            {"name": "Book", "price": 9.99, "category": "books"},
        )

        print("\n--- Field constraint violations ---")
        show("name too short (1 char)",
             {"name": "X", "price": 9.99, "category": "books"})
        show("price not > 0 (price=0)",
             {"name": "Book", "price": 0, "category": "books"})
        show("price negative",
             {"name": "Book", "price": -5, "category": "books"})
        show("category invalid (has uppercase)",
             {"name": "Book", "price": 9.99, "category": "Books"})
        show("too many tags (6 > max 5)",
             {"name": "Gadget", "price": 9.99, "category": "electronics",
              "tags": ["a", "b", "c", "d", "e", "f"]})
        show("discount_pct out of range (110 > 100)",
             {"name": "Sale Item", "price": 9.99, "category": "books",
              "discount_pct": 110})

        print("\n--- Custom validator: reserved name ---")
        show("Reserved name 'admin'",
             {"name": "admin", "price": 9.99, "category": "books"})
        show("Reserved name 'TEST' (case-insensitive)",
             {"name": "TEST", "price": 9.99, "category": "books"})

        print("\n--- Multiple errors in one request ---")
        show(
            "Multiple invalid fields",
            {"name": "X", "price": -10, "category": "Bad-Category", "discount_pct": 200},
        )

        print("\n--- Cross-field validation ---")
        show("Valid sale period",
             {"start_date": "2026-01-01", "end_date": "2026-01-31", "discount_pct": 20},
             SalePeriodRequest)
        show("end_date before start_date",
             {"start_date": "2026-06-01", "end_date": "2026-01-01", "discount_pct": 10},
             SalePeriodRequest)
        show("end_date equals start_date",
             {"start_date": "2026-01-01", "end_date": "2026-01-01", "discount_pct": 5},
             SalePeriodRequest)

        print("\n--- Query parameter constraints (simulated Query(ge=1, le=100)) ---")
        for kwargs in [
            {"page": 1, "limit": 20},
            {"page": 0, "limit": 20},      # page < 1
            {"page": 1, "limit": 500},     # limit > 100
            {"page": 1, "limit": 10, "min_price": 100, "max_price": 50},  # range inverted
        ]:
            try:
                q = ListProductsQuery(**kwargs)
                print(f"  ✓ {kwargs} → page={q.page} limit={q.limit}")
            except ValueError as e:
                print(f"  ✗ {kwargs} → 422: {e}")

        print("\n--- Pydantic vs service layer responsibilities ---")
        print("  Pydantic handles: format, type, range, pattern, cross-field math")
        print("  Service handles:  uniqueness (DB query), permissions, state-based rules")

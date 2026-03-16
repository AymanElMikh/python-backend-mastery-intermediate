"""
Demo: Custom Exceptions — Domain Error Hierarchy
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""


# ── Section 1: Exception hierarchy ───────────────────────────────────────────

class AppError(Exception):
    """
    Base for all application-specific errors.
    Catching AppError catches ALL our custom errors.
    Built-in exceptions (ValueError, KeyError) do NOT inherit from this.
    """
    pass


# ── Category-level errors ──────────────────────────────────────────────────────

class NotFoundError(AppError):
    """Something that should exist doesn't."""
    def __init__(self, resource: str, identifier):
        super().__init__(f"{resource} not found: {identifier!r}")
        self.resource = resource
        self.identifier = identifier


class ValidationError(AppError):
    """Input data fails validation rules."""
    def __init__(self, field: str, reason: str):
        super().__init__(f"Validation error on '{field}': {reason}")
        self.field = field
        self.reason = reason


class BusinessRuleError(AppError):
    """A business rule was violated — not a data error, a domain rule."""
    pass


class AuthorizationError(AppError):
    """The user doesn't have permission for this action."""
    def __init__(self, action: str):
        super().__init__(f"Not authorized to: {action}")
        self.action = action


# ── Specific domain errors (inherit from categories) ─────────────────────────

class UserNotFoundError(NotFoundError):
    def __init__(self, user_id: int):
        super().__init__("User", user_id)
        self.user_id = user_id


class ProductNotFoundError(NotFoundError):
    def __init__(self, product_id: int):
        super().__init__("Product", product_id)
        self.product_id = product_id


class InsufficientFundsError(BusinessRuleError):
    def __init__(self, available: float, requested: float):
        super().__init__(
            f"Insufficient funds: have ${available:.2f}, need ${requested:.2f}"
        )
        self.available = available
        self.requested = requested


class SubscriptionRequiredError(BusinessRuleError):
    def __init__(self, feature: str):
        super().__init__(f"Feature '{feature}' requires an active subscription")
        self.feature = feature


class DuplicateEmailError(ValidationError):
    def __init__(self, email: str):
        super().__init__("email", f"'{email}' is already registered")
        self.email = email


# ── Section 2: Service that raises domain exceptions ─────────────────────────

class FakeUserDB:
    def __init__(self):
        self._users = {
            1: {"id": 1, "email": "alice@x.com", "balance": 500.0, "plan": "pro"},
            2: {"id": 2, "email": "bob@x.com",   "balance": 25.0,  "plan": "free"},
        }
        self._emails = {u["email"] for u in self._users.values()}

    def get(self, user_id: int):
        return self._users.get(user_id)

    def email_exists(self, email: str) -> bool:
        return email in self._emails


db = FakeUserDB()


class UserService:
    def get_user(self, user_id: int) -> dict:
        user = db.get(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    def register(self, email: str, name: str) -> dict:
        if not email or "@" not in email:
            raise ValidationError("email", "must be a valid email address")
        if db.email_exists(email):
            raise DuplicateEmailError(email)
        return {"id": 99, "email": email, "name": name}

    def charge(self, user_id: int, amount: float) -> dict:
        if amount <= 0:
            raise ValidationError("amount", "must be positive")
        user = self.get_user(user_id)  # raises UserNotFoundError if missing
        if user["balance"] < amount:
            raise InsufficientFundsError(user["balance"], amount)
        return {"charged": amount, "remaining": user["balance"] - amount}

    def use_feature(self, user_id: int, feature: str) -> str:
        user = self.get_user(user_id)
        if feature == "export" and user["plan"] == "free":
            raise SubscriptionRequiredError(feature)
        return f"Feature '{feature}' activated for user #{user_id}"


# ── Section 3: Route layer — maps exceptions to HTTP responses ────────────────

HTTP_CODES = {
    NotFoundError: 404,
    ValidationError: 400,
    BusinessRuleError: 422,
    AuthorizationError: 403,
    AppError: 500,  # Catch-all for any other app error
}


def handle(service_call):
    """Generic error handler: domain exception → HTTP response."""
    try:
        result = service_call()
        return {"data": result, "status": 200}
    except NotFoundError as e:
        return {"error": str(e), "status": 404}
    except ValidationError as e:
        return {"error": str(e), "field": e.field, "status": 400}
    except BusinessRuleError as e:
        return {"error": str(e), "status": 422}
    except AppError as e:
        return {"error": str(e), "status": 500}
    # Note: we do NOT catch Exception here — unexpected bugs should propagate


service = UserService()

if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Custom Exceptions")
    print("=" * 55)

    print("\n--- Exception hierarchy ---")
    print("  AppError")
    print("  ├── NotFoundError")
    print("  │   ├── UserNotFoundError")
    print("  │   └── ProductNotFoundError")
    print("  ├── ValidationError")
    print("  │   └── DuplicateEmailError")
    print("  ├── BusinessRuleError")
    print("  │   ├── InsufficientFundsError")
    print("  │   └── SubscriptionRequiredError")
    print("  └── AuthorizationError")

    print("\n--- Happy paths ---")
    print(handle(lambda: service.get_user(1)))
    print(handle(lambda: service.charge(1, 100.0)))
    print(handle(lambda: service.use_feature(1, "export")))

    print("\n--- Not found ---")
    print(handle(lambda: service.get_user(99)))

    print("\n--- Validation errors ---")
    print(handle(lambda: service.register("not-an-email", "Bad")))
    print(handle(lambda: service.register("alice@x.com", "Alice2")))  # duplicate
    print(handle(lambda: service.charge(1, -50.0)))

    print("\n--- Business rule violations ---")
    print(handle(lambda: service.charge(2, 500.0)))       # insufficient funds
    print(handle(lambda: service.use_feature(2, "export")))  # free plan

    print("\n--- Catching by category (useful in logging middleware) ---")
    errors = [
        UserNotFoundError(42),
        DuplicateEmailError("x@x.com"),
        InsufficientFundsError(10, 100),
    ]
    for err in errors:
        if isinstance(err, NotFoundError):
            print(f"  404 → {err} (resource={err.resource}, id={err.identifier})")
        elif isinstance(err, ValidationError):
            print(f"  400 → {err} (field={err.field})")
        elif isinstance(err, BusinessRuleError):
            print(f"  422 → {err}")

    print("\n--- Why not just use ValueError? ---")
    try:
        raise ValueError("insufficient funds")
    except ValueError as e:
        print(f"  Caught ValueError: {e}")
        print("  Which ValueError? Data format? Config error? Business rule?")
        print("  Can't tell. InsufficientFundsError tells you exactly.")

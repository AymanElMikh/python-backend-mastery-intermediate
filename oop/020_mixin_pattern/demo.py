"""
Demo: Mixin Pattern — Adding Capabilities Without Deep Hierarchies
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import json
from datetime import datetime

# ── Section 1: Define focused, single-responsibility mixins ───────────────────

class TimestampMixin:
    """
    Adds created_at and updated_at timestamps to any model class.
    Call super().__init__() to support cooperative multiple inheritance.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # pass remaining args up the MRO chain
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()

    def touch(self) -> None:
        """Update updated_at to now — call after any modification."""
        self.updated_at = datetime.now()


class SerializableMixin:
    """Adds to_dict() and to_json() to any class."""

    def to_dict(self) -> dict:
        """Convert public attributes to a plain dict."""
        return {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith("_")  # skip private attributes
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = self.to_dict()
        # Convert datetime objects to ISO strings for JSON compatibility
        serializable = {}
        for k, v in data.items():
            if isinstance(v, datetime):
                serializable[k] = v.isoformat()
            else:
                serializable[k] = v
        return json.dumps(serializable, indent=2)


class ValidatableMixin:
    """
    Adds a validate() method that subclasses can override.
    Calls validate() at the end of __init__ automatically.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate()

    def validate(self) -> None:
        """Override in subclasses to add validation logic."""
        pass  # base implementation does nothing


class LoggableMixin:
    """Adds action logging capability."""

    def log_action(self, action: str, detail: str = "") -> str:
        class_name = self.__class__.__name__
        msg = f"[{class_name}] {action}"
        if detail:
            msg += f" — {detail}"
        print(f"  {msg}")
        return msg


# ── Section 2: Apply mixins to multiple unrelated classes ────────────────────

class User(TimestampMixin, SerializableMixin, LoggableMixin):
    """User model with timestamps, serialization, and logging."""

    def __init__(self, name: str, email: str, role: str = "viewer"):
        super().__init__()  # triggers TimestampMixin.__init__ → ... → object.__init__
        self.name = name
        self.email = email
        self.role = role

    def promote(self, new_role: str) -> None:
        old_role = self.role
        self.role = new_role
        self.touch()
        self.log_action("promoted", f"{old_role} → {new_role}")

    def __repr__(self) -> str:
        return f"User(name={self.name!r}, role={self.role!r})"


class Product(TimestampMixin, SerializableMixin):
    """Product model — also gets timestamps and serialization."""

    def __init__(self, name: str, price: float, sku: str):
        super().__init__()
        self.name = name
        self.price = price
        self.sku = sku

    def update_price(self, new_price: float) -> None:
        self.price = new_price
        self.touch()  # inherited from TimestampMixin

    def __repr__(self) -> str:
        return f"Product(sku={self.sku!r}, price={self.price:.2f})"


class APIRequest(ValidatableMixin, LoggableMixin):
    """Represents an incoming API request — validates on creation."""

    def __init__(self, method: str, path: str, body: dict = None):
        self.method = method.upper()
        self.path = path
        self.body = body or {}
        super().__init__()  # triggers ValidatableMixin.__init__ → validate()

    def validate(self) -> None:
        valid_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
        if self.method not in valid_methods:
            raise ValueError(f"Invalid HTTP method: {self.method!r}")
        if not self.path.startswith("/"):
            raise ValueError(f"Path must start with '/': {self.path!r}")
        self.log_action("validated", f"{self.method} {self.path}")


# ── Section 3: MRO — how Python resolves mixin method calls ──────────────────

# ── Section 4: Django-style mixin example — permission checking ───────────────

class LoginRequiredMixin:
    """Simulates Django's LoginRequiredMixin for class-based views."""

    def dispatch(self, request: dict) -> dict:
        if not request.get("user"):
            return {"status": 401, "error": "Authentication required"}
        return super().dispatch(request)


class PermissionRequiredMixin:
    """Check specific permissions before handling a request."""
    required_permission = None  # override in subclass

    def dispatch(self, request: dict) -> dict:
        user = request.get("user", {})
        if self.required_permission and self.required_permission not in user.get("permissions", []):
            return {"status": 403, "error": f"Permission denied: {self.required_permission}"}
        return super().dispatch(request)


class BaseView:
    """Base class for all views — the final handler."""
    def dispatch(self, request: dict) -> dict:
        return {"status": 200, "data": f"Handled {request.get('path', '/')}"}


class AdminDashboardView(LoginRequiredMixin, PermissionRequiredMixin, BaseView):
    """Requires login + admin permission."""
    required_permission = "admin"


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Mixin Pattern")
    print("=" * 50)

    print("\n--- Section 1 & 2: User with 3 mixins ---")
    alice = User("Alice", "alice@example.com", role="editor")
    print(f"  Created: {alice}")
    print(f"  created_at set: {alice.created_at is not None}")
    alice.promote("admin")
    print(f"  After promote: {alice}")

    print("\n  Serialization (from SerializableMixin):")
    d = alice.to_dict()
    for k, v in d.items():
        display = v.isoformat() if isinstance(v, datetime) else v
        print(f"    {k}: {display!r}")

    print("\n--- Section 2b: Product with 2 mixins ---")
    widget = Product("Widget Pro", 29.99, "WGT-001")
    print(f"  {widget}")
    widget.update_price(24.99)
    print(f"  After price update: {widget}")
    print(f"  JSON:\n{widget.to_json()}")

    print("\n--- Section 2c: APIRequest with validate mixin ---")
    try:
        req = APIRequest("GET", "/api/users")
        print(f"  Valid request: {req.method} {req.path}")
    except ValueError as e:
        print(f"  Error: {e}")

    try:
        bad = APIRequest("FETCH", "/api/users")  # invalid method
    except ValueError as e:
        print(f"  Invalid method: {e}")

    try:
        bad2 = APIRequest("GET", "no-leading-slash")  # invalid path
    except ValueError as e:
        print(f"  Invalid path: {e}")

    print("\n--- Section 3: MRO shows mixin resolution order ---")
    print(f"  User MRO: {[c.__name__ for c in User.__mro__]}")
    print(f"  Product MRO: {[c.__name__ for c in Product.__mro__]}")

    print("\n--- Section 4: Django-style view mixins ---")
    view = AdminDashboardView()

    # No user
    r1 = view.dispatch({"path": "/admin"})
    print(f"  No user:           {r1}")

    # User without admin permission
    r2 = view.dispatch({"path": "/admin", "user": {"name": "Bob", "permissions": ["read"]}})
    print(f"  No admin perm:     {r2}")

    # User with admin permission
    r3 = view.dispatch({"path": "/admin", "user": {"name": "Admin", "permissions": ["read", "admin"]}})
    print(f"  Admin user:        {r3}")

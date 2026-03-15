"""
Demo: @classmethod and @staticmethod — Alternative Constructors and Utilities
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from datetime import datetime, date
import json

# ── Section 1: All three method types side-by-side ───────────────────────────

class Temperature:
    """
    Shows all three method types clearly.
    Stores temperature in Celsius internally.
    """
    def __init__(self, celsius: float):
        self.celsius = celsius

    # ── Regular method: accesses self ──────────────
    def to_fahrenheit(self) -> float:
        return self.celsius * 9/5 + 32

    def describe(self) -> str:
        if self.celsius < 0:
            return "freezing"
        elif self.celsius < 20:
            return "cold"
        elif self.celsius < 30:
            return "comfortable"
        return "hot"

    # ── @classmethod: alternative constructors ──────
    @classmethod
    def from_fahrenheit(cls, fahrenheit: float) -> "Temperature":
        celsius = (fahrenheit - 32) * 5/9
        return cls(celsius)

    @classmethod
    def from_kelvin(cls, kelvin: float) -> "Temperature":
        return cls(kelvin - 273.15)

    # ── @staticmethod: utility, no self or cls needed ──
    @staticmethod
    def celsius_to_fahrenheit(c: float) -> float:
        """Pure conversion — doesn't need the class or any instance."""
        return c * 9/5 + 32

    @staticmethod
    def is_valid_celsius(value: float) -> bool:
        return value >= -273.15  # absolute zero

    def __repr__(self) -> str:
        return f"Temperature({self.celsius:.1f}°C)"


# ── Section 2: @classmethod for subclass-aware factories ─────────────────────

class Event:
    """Base event for an audit log."""
    def __init__(self, name: str, user_id: int, timestamp: datetime = None):
        self.name = name
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now()

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        """
        @classmethod means cls = the actual class (Event or its subclass).
        If called as UserLoginEvent.from_dict(...), cls is UserLoginEvent.
        A @staticmethod would always return an Event, even for subclasses.
        """
        return cls(
            name=data["name"],
            user_id=data["user_id"],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Event":
        return cls.from_dict(json.loads(json_str))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, user_id={self.user_id})"


class UserLoginEvent(Event):
    """Subclass — from_dict returns a UserLoginEvent, not an Event."""
    def __init__(self, name: str, user_id: int, ip_address: str = "unknown", **kwargs):
        super().__init__(name, user_id, **kwargs)
        self.ip_address = ip_address

    @classmethod
    def from_dict(cls, data: dict) -> "UserLoginEvent":
        instance = super().from_dict(data)  # calls Event.from_dict but cls=UserLoginEvent
        instance.ip_address = data.get("ip_address", "unknown")
        return instance


# ── Section 3: Real-world — User with multiple creation patterns ──────────────

class User:
    DEFAULT_ROLE = "viewer"

    def __init__(self, name: str, email: str, role: str = None,
                 created_at: date = None):
        self.name = name
        self.email = email
        self.role = role or self.DEFAULT_ROLE
        self.created_at = created_at or date.today()
        self.is_active = True

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create from API payload or database row."""
        return cls(
            name=data["name"],
            email=data["email"],
            role=data.get("role", cls.DEFAULT_ROLE),
            created_at=date.fromisoformat(data["created_at"]) if "created_at" in data else None
        )

    @classmethod
    def create_admin(cls, name: str, email: str) -> "User":
        """Factory: creates an admin with all the right setup."""
        user = cls(name=name, email=email, role="admin")
        return user

    @classmethod
    def create_service_account(cls, service_name: str) -> "User":
        """Creates a machine/service account."""
        return cls(
            name=f"svc-{service_name}",
            email=f"{service_name}@internal.service",
            role="service"
        )

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Utility: validate email format — no instance needed."""
        if "@" not in email:
            return False
        parts = email.split("@")
        return len(parts) == 2 and "." in parts[1] and len(parts[1]) > 2

    @staticmethod
    def normalize_email(email: str) -> str:
        """Utility: lowercase and strip whitespace."""
        return email.strip().lower()

    def __repr__(self) -> str:
        return f"User(name={self.name!r}, role={self.role!r})"


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: @classmethod and @staticmethod")
    print("=" * 50)

    print("\n--- Section 1: Temperature — three method types ---")
    t1 = Temperature(25)
    print(f"  {t1}.to_fahrenheit() = {t1.to_fahrenheit():.1f}°F  (regular method)")

    t2 = Temperature.from_fahrenheit(98.6)
    print(f"  from_fahrenheit(98.6) = {t2}  (classmethod)")

    t3 = Temperature.from_kelvin(373.15)
    print(f"  from_kelvin(373.15)   = {t3}  (classmethod)")

    # @staticmethod: call on class or instance — both work
    converted = Temperature.celsius_to_fahrenheit(100)
    print(f"  celsius_to_fahrenheit(100) = {converted}  (staticmethod on class)")
    print(f"  t1.celsius_to_fahrenheit(0) = {t1.celsius_to_fahrenheit(0)}  (staticmethod on instance)")
    print(f"  is_valid_celsius(-300) = {Temperature.is_valid_celsius(-300)}")
    print(f"  is_valid_celsius(-273) = {Temperature.is_valid_celsius(-273)}")

    print("\n--- Section 2: @classmethod preserves subclass type ---")
    event_data = {"name": "login", "user_id": 42}
    login_data = {"name": "login", "user_id": 42, "ip_address": "192.168.1.1"}

    e1 = Event.from_dict(event_data)
    e2 = UserLoginEvent.from_dict(login_data)

    print(f"  Event.from_dict()          → {type(e1).__name__}: {e1}")
    print(f"  UserLoginEvent.from_dict() → {type(e2).__name__}: {e2}")
    print(f"  e2.ip_address = {e2.ip_address}")

    print("\n--- Section 3: User factory methods ---")
    # Create from API payload
    api_payload = {"name": "Alice", "email": "alice@example.com"}
    user1 = User.from_dict(api_payload)
    print(f"  from_dict: {user1}")

    # Create admin
    admin = User.create_admin("Eve", "eve@example.com")
    print(f"  create_admin: {admin}")

    # Create service account
    svc = User.create_service_account("payment-processor")
    print(f"  create_service_account: {svc}")

    # Static utilities — no instantiation needed
    emails = ["alice@example.com", "bad-email", "  BOB@TEST.COM  ", "@nodomain"]
    for email in emails:
        valid = User.is_valid_email(email)
        normalized = User.normalize_email(email)
        print(f"  {email!r:30s} valid={valid}, normalized={normalized!r}")

    print("\n--- Why @classmethod beats @staticmethod for constructors ---")
    class PremiumUser(User):
        DEFAULT_ROLE = "premium"

    # @classmethod — cls is PremiumUser, so from_dict returns PremiumUser
    premium = PremiumUser.from_dict({"name": "VIP", "email": "vip@example.com"})
    print(f"  PremiumUser.from_dict() → type: {type(premium).__name__}, role: {premium.role}")

"""
Demo: Inheritance and super() — Building on Existing Classes
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

# ── Section 1: Basic inheritance ─────────────────────────────────────────────

class Vehicle:
    """Base class for all vehicles."""
    def __init__(self, make: str, model: str, year: int):
        self.make = make
        self.model = model
        self.year = year
        self.is_running = False

    def start(self) -> str:
        self.is_running = True
        return f"{self.make} {self.model} engine started"

    def stop(self) -> str:
        self.is_running = False
        return f"{self.make} {self.model} engine stopped"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.year} {self.make} {self.model})"


class Car(Vehicle):
    """Car IS-A Vehicle — adds doors and a honk."""
    def __init__(self, make: str, model: str, year: int, doors: int = 4):
        super().__init__(make, model, year)  # run Vehicle.__init__ first
        self.doors = doors  # add car-specific attribute

    def honk(self) -> str:
        return f"{self.make} {self.model}: Beep beep!"


class ElectricCar(Car):
    """ElectricCar IS-A Car IS-A Vehicle — three-level hierarchy."""
    def __init__(self, make: str, model: str, year: int,
                 battery_kwh: float, doors: int = 4):
        super().__init__(make, model, year, doors)  # run Car.__init__
        self.battery_kwh = battery_kwh
        self.charge_pct = 100.0

    def start(self) -> str:
        # Override start — electric cars are silent
        self.is_running = True
        return f"{self.make} {self.model} silently powered on (battery: {self.charge_pct:.0f}%)"

    def charge(self, percent: float) -> str:
        self.charge_pct = min(100.0, self.charge_pct + percent)
        return f"Charged to {self.charge_pct:.0f}%"


# ── Section 2: Real-world pattern — User hierarchy ───────────────────────────

class User:
    """Base user model."""
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        self.is_active = True
        self._permissions: set = {"read"}

    def has_permission(self, perm: str) -> bool:
        return perm in self._permissions

    def deactivate(self) -> None:
        self.is_active = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


class EditorUser(User):
    """Editor can also write and publish content."""
    def __init__(self, name: str, email: str, section: str):
        super().__init__(name, email)
        self._permissions.update({"write", "publish"})
        self.section = section  # which content section they own


class AdminUser(User):
    """Admin has all permissions and can manage other users."""
    def __init__(self, name: str, email: str):
        super().__init__(name, email)
        self._permissions.update({"write", "publish", "delete", "manage_users"})

    def deactivate_user(self, target: User) -> str:
        target.deactivate()
        return f"{self.name} deactivated {target.name}"


# ── Section 3: isinstance() and issubclass() ──────────────────────────────────

def process_user(user: User) -> str:
    """Demonstrates polymorphism — works with any User subclass."""
    base = f"Processing {user.__class__.__name__}: {user.name}"
    if isinstance(user, AdminUser):
        return f"{base} [admin — full access]"
    if isinstance(user, EditorUser):
        return f"{base} [editor — section: {user.section}]"
    return f"{base} [viewer]"


# ── Section 4: Common mistake — forgetting super().__init__ ──────────────────

class BadChild(User):
    """WRONG: doesn't call super().__init__ — parent attributes are missing."""
    def __init__(self, name: str):
        # Forgot: super().__init__(name, email)
        self.name = name  # manually set name, but email/_permissions are missing!


class GoodChild(User):
    """RIGHT: always call super().__init__ first."""
    def __init__(self, name: str, email: str, extra: str):
        super().__init__(name, email)  # parent gets fully initialized
        self.extra = extra


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Inheritance and super()")
    print("=" * 50)

    print("\n--- Section 1: Vehicle hierarchy ---")
    car = Car("Toyota", "Camry", 2023)
    ev  = ElectricCar("Tesla", "Model 3", 2024, battery_kwh=75)

    print(f"  {car}")
    print(f"  {car.start()}")
    print(f"  {car.honk()}")
    print(f"  {car.stop()}")
    print()
    print(f"  {ev}")
    print(f"  {ev.start()}")  # overridden method
    ev.charge_pct = 40
    print(f"  {ev.charge(30)}")

    print("\n--- isinstance checks ---")
    print(f"  car is Vehicle: {isinstance(car, Vehicle)}")
    print(f"  car is Car:     {isinstance(car, Car)}")
    print(f"  ev  is Car:     {isinstance(ev, Car)}")
    print(f"  ev  is Vehicle: {isinstance(ev, Vehicle)}")
    print(f"  car is ElectricCar: {isinstance(car, ElectricCar)}")

    print("\n--- MRO (Method Resolution Order) ---")
    print(f"  ElectricCar MRO: {[c.__name__ for c in ElectricCar.__mro__]}")

    print("\n--- Section 2: User hierarchy ---")
    viewer = User("Carol", "carol@example.com")
    editor = EditorUser("Dave", "dave@example.com", section="tech")
    admin  = AdminUser("Eve", "eve@example.com")

    for user in [viewer, editor, admin]:
        print(f"  {process_user(user)}")
        print(f"    permissions: {sorted(user._permissions)}")

    print(f"\n  editor has 'publish': {editor.has_permission('publish')}")
    print(f"  viewer has 'publish': {viewer.has_permission('publish')}")
    print(f"  {admin.deactivate_user(viewer)}")
    print(f"  Carol is_active: {viewer.is_active}")

    print("\n--- Section 4: Forgetting super().__init__ ---")
    try:
        bad = BadChild("Frank")
        print(f"  bad.name = {bad.name}")
        print(f"  bad.email = {bad.email}")  # AttributeError!
    except AttributeError as e:
        print(f"  AttributeError: {e}")
        print("  (because super().__init__ was never called)")

    good = GoodChild("Grace", "grace@example.com", extra="bonus")
    print(f"  good.name = {good.name}")
    print(f"  good.email = {good.email}")
    print(f"  good.extra = {good.extra}")
    print(f"  good permissions: {good._permissions}")

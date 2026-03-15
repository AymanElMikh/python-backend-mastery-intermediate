"""
Demo: Classes and __init__ — Building Objects in Python
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

# ── Section 1: A well-structured class ───────────────────────────────────────

class BankAccount:
    """
    Models a bank account — a realistic class with state and behavior.
    """
    # Class attribute: shared by ALL instances
    CURRENCY = "USD"
    _next_id = 1  # class-level counter (use underscore = internal)

    def __init__(self, owner: str, initial_balance: float = 0.0):
        # Instance attributes: unique to each object
        self.account_id = BankAccount._next_id
        BankAccount._next_id += 1
        self.owner = owner
        self.balance = initial_balance
        self._transactions: list = []  # _ prefix = "private by convention"

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self._transactions.append(("deposit", amount))
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError(f"Insufficient funds (balance: {self.balance})")
        self.balance -= amount
        self._transactions.append(("withdraw", amount))
        return self.balance

    def get_history(self) -> list:
        return list(self._transactions)  # return a copy, not the internal list

    def __repr__(self) -> str:
        return (f"BankAccount(id={self.account_id}, owner={self.owner!r}, "
                f"balance={self.balance:.2f} {self.CURRENCY})")


# ── Section 2: Instance vs class attributes ──────────────────────────────────

class Config:
    """Shows the difference between instance and class attributes."""
    # Class attribute — shared across all Config instances
    DEBUG = False
    VERSION = "1.0.0"

    def __init__(self, app_name: str):
        # Instance attribute — each Config has its own app_name
        self.app_name = app_name
        self.settings: dict = {}

    def set(self, key: str, value) -> None:
        self.settings[key] = value

    def get(self, key: str, default=None):
        return self.settings.get(key, default)


# ── Section 3: Common mistake — mutable default argument ─────────────────────

class BadUser:
    """WRONG: mutable default — all instances share the same list!"""
    def __init__(self, name: str, tags=[]):  # BUG: shared list
        self.name = name
        self.tags = tags  # this is the class-level default list


class GoodUser:
    """RIGHT: use None and create a new list per instance."""
    def __init__(self, name: str, tags: list = None):
        self.name = name
        self.tags = tags if tags is not None else []  # fresh list every time


# ── Section 4: Class showing `self` is just the instance ──────────────────────

class Counter:
    def __init__(self, start: int = 0):
        self.value = start

    def increment(self, by: int = 1) -> "Counter":
        self.value += by
        return self  # return self enables method chaining

    def reset(self) -> "Counter":
        self.value = 0
        return self

    def __repr__(self) -> str:
        return f"Counter({self.value})"


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Classes and __init__")
    print("=" * 50)

    print("\n--- Section 1: BankAccount ---")
    alice_acc = BankAccount("Alice", initial_balance=1000.0)
    bob_acc   = BankAccount("Bob")
    print(f"  Created: {alice_acc}")
    print(f"  Created: {bob_acc}")

    alice_acc.deposit(500)
    alice_acc.withdraw(200)
    alice_acc.deposit(100)
    print(f"  Alice after transactions: balance = {alice_acc.balance:.2f}")
    print(f"  Transaction history: {alice_acc.get_history()}")

    try:
        alice_acc.withdraw(10000)
    except ValueError as e:
        print(f"  Withdraw too much: {e}")

    print(f"  Both use class attr CURRENCY: {alice_acc.CURRENCY}, {bob_acc.CURRENCY}")

    print("\n--- Section 2: Instance vs class attributes ---")
    dev_config  = Config("dev-api")
    prod_config = Config("prod-api")

    dev_config.set("port", 8000)
    prod_config.set("port", 80)

    print(f"  dev  app_name:  {dev_config.app_name}")
    print(f"  prod app_name:  {prod_config.app_name}")
    print(f"  dev  port:      {dev_config.get('port')}")
    print(f"  prod port:      {prod_config.get('port')}")
    print(f"  Shared VERSION: {Config.VERSION}")

    # Changing a class attribute on the class affects all instances
    Config.VERSION = "2.0.0"
    print(f"  After Config.VERSION = '2.0.0':")
    print(f"    dev.VERSION  = {dev_config.VERSION}")
    print(f"    prod.VERSION = {prod_config.VERSION}")

    print("\n--- Section 3: Mutable default bug ---")
    bad1 = BadUser("Alice")
    bad2 = BadUser("Bob")
    bad1.tags.append("admin")  # modifying the SHARED list
    print(f"  BadUser - Alice tags: {bad1.tags}")
    print(f"  BadUser - Bob tags:   {bad2.tags}  ← BUG! Bob has Alice's tag")

    good1 = GoodUser("Alice")
    good2 = GoodUser("Bob")
    good1.tags.append("admin")
    print(f"  GoodUser - Alice tags: {good1.tags}")
    print(f"  GoodUser - Bob tags:   {good2.tags}  ← correct, empty")

    print("\n--- Section 4: Method chaining with self ---")
    c = Counter(0)
    result = c.increment(5).increment(3).increment(2).reset().increment(1)
    print(f"  Counter after chain: {result}")

    print("\n--- self is just the instance ---")
    # These two calls are identical:
    counter = Counter(10)
    counter.increment(5)             # normal method call
    Counter.increment(counter, 5)    # explicit: class.method(instance, args)
    print(f"  After two increments of 5: {counter}")

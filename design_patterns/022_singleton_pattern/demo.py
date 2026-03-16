"""
Demo: Singleton Pattern
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

# ── Section 1: Module-level instance (most Pythonic approach) ─────────────────

class AppConfig:
    """
    Reads config once. The module-level `config` below is the singleton.
    Other modules do: from demo import config
    """
    def __init__(self):
        # In a real app this reads from os.environ
        self.db_url = "postgresql://localhost/mydb"
        self.debug = False
        self.secret_key = "super-secret"
        print("  AppConfig.__init__ called (reading config...)")

# The singleton — created once when this module is imported
config = AppConfig()


# ── Section 2: __new__ override approach ──────────────────────────────────────

class DatabasePool:
    """
    Classic Singleton via __new__.
    Only one pool exists — expensive setup happens once.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("  DatabasePool: creating new instance")
            cls._instance = super().__new__(cls)
            cls._instance.connections = []
            cls._instance.max_connections = 10
        else:
            print("  DatabasePool: returning existing instance")
        return cls._instance

    def get_connection(self):
        return f"conn_{len(self.connections) + 1}"


# ── Section 3: lru_cache approach (clean, lazy) ───────────────────────────────

from functools import lru_cache

class RedisClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        print(f"  RedisClient: connecting to {host}:{port}")

    def ping(self) -> str:
        return f"PONG from {self.host}:{self.port}"


@lru_cache(maxsize=1)
def get_redis_client() -> RedisClient:
    """
    First call creates the client. Subsequent calls return cached instance.
    @lru_cache makes this thread-safe and lazy.
    """
    return RedisClient(host="localhost", port=6379)


# ── Section 4: The testing problem — why singletons can hurt ─────────────────

class Counter:
    """A Singleton counter — demonstrates the test pollution problem."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.count = 0
        return cls._instance

    def increment(self):
        self.count += 1


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Singleton Pattern")
    print("=" * 55)

    print("\n--- Approach 1: Module-level instance ---")
    print(f"config is the same object everywhere: {id(config)}")
    print(f"db_url = {config.db_url}")
    # Importing 'config' again from the same module returns the same object
    from demo import config as config2  # noqa
    print(f"config is config2: {config is config2}")

    print("\n--- Approach 2: __new__ override ---")
    pool1 = DatabasePool()
    pool2 = DatabasePool()
    print(f"pool1 is pool2: {pool1 is pool2}")
    print(f"Same id: {id(pool1)} == {id(pool2)}")

    print("\n--- Approach 3: lru_cache (lazy singleton) ---")
    print("First call:")
    client1 = get_redis_client()
    print("Second call:")
    client2 = get_redis_client()
    print(f"client1 is client2: {client1 is client2}")
    print(f"Ping: {client1.ping()}")

    print("\n--- The testing problem ---")
    c1 = Counter()
    c1.increment()
    c1.increment()
    print(f"After test A: count = {c1.count}")

    # "Test B" — gets the SAME instance, sees dirty state from test A
    c2 = Counter()
    print(f"In test B: count = {c2.count}  ← not 0! Singleton leaked state")

    # Fix: reset the singleton between tests
    Counter._instance = None
    c3 = Counter()
    print(f"After reset: count = {c3.count}  ← clean now")

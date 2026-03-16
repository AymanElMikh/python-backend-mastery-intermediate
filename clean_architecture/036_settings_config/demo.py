"""
Demo: Settings & Configuration Management
Level: Intermediate (2–3 years experience)
Run:  python demo.py

Note: This demo uses os.environ and dataclasses to simulate Pydantic BaseSettings
without requiring pydantic-settings to be installed.
In real projects, use: pip install pydantic-settings
"""

import os
from dataclasses import dataclass, field
from typing import Optional


# ── Section 1: The wrong way — hardcoded config ───────────────────────────────

class DatabaseBad:
    """
    BAD: connection string is hardcoded.
    - Works only on the developer's machine
    - Can't deploy to staging or prod without code changes
    - If this is a real API key, it will end up in git history
    """
    DATABASE_URL = "postgresql://admin:password123@prod-db:5432/myapp"  # hardcoded!
    API_KEY = "sk_live_abc123xyz"  # This would be in git forever if committed

    def connect(self):
        print(f"  [DB] Connecting to: {self.DATABASE_URL}")


# ── Section 2: The right way — environment-based settings ─────────────────────

@dataclass
class Settings:
    """
    A settings object that reads from environment variables.
    Validates types and provides defaults.
    This is what pydantic-settings does, but implemented manually for the demo.
    """
    # Required — app fails to start if these aren't set
    database_url: str
    secret_key: str

    # Optional with defaults
    debug: bool = False
    max_db_connections: int = 10
    redis_url: str = "redis://localhost:6379"
    allowed_hosts: list = field(default_factory=lambda: ["localhost"])

    @classmethod
    def from_env(cls) -> "Settings":
        """Read all config from environment variables. Fail fast on missing required vars."""
        errors = []

        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            errors.append("DATABASE_URL is required")

        secret_key = os.environ.get("SECRET_KEY")
        if not secret_key:
            errors.append("SECRET_KEY is required")

        if errors:
            raise EnvironmentError(
                "Missing required configuration:\n" +
                "\n".join(f"  - {e}" for e in errors)
            )

        debug_raw = os.environ.get("DEBUG", "false").lower()
        debug = debug_raw in ("true", "1", "yes")

        max_connections_raw = os.environ.get("MAX_DB_CONNECTIONS", "10")
        try:
            max_connections = int(max_connections_raw)
        except ValueError:
            raise EnvironmentError(f"MAX_DB_CONNECTIONS must be an integer, got: {max_connections_raw!r}")

        return cls(
            database_url=database_url,
            secret_key=secret_key,
            debug=debug,
            max_db_connections=max_connections,
            redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379"),
        )

    def is_production(self) -> bool:
        return not self.debug

    def __repr__(self) -> str:
        # Never print the secret_key — mask it
        return (
            f"Settings("
            f"database_url={self.database_url!r}, "
            f"secret_key='***', "
            f"debug={self.debug}, "
            f"max_db_connections={self.max_db_connections}"
            f")"
        )


# ── Section 3: Simulating pydantic-settings (the real-world version) ─────────

PYDANTIC_SETTINGS_EXAMPLE = '''
# In real projects, install pydantic-settings and do this:

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str                          # Required — fails at startup if missing
    secret_key: str                            # Required
    debug: bool = False                        # Optional with default
    max_db_connections: int = 10               # Auto-cast from string env var
    redis_url: str = "redis://localhost:6379"

    model_config = {
        "env_file": ".env",         # Auto-reads .env file in dev
        "env_file_encoding": "utf-8",
    }

# Module-level singleton — one settings object for the whole app
settings = Settings()

# Usage anywhere in the app:
# from settings import settings
# engine = create_engine(settings.database_url)
'''


# ── Section 4: Injecting settings into services ───────────────────────────────

class DatabaseService:
    """Receives settings via injection — doesn't read env vars itself."""
    def __init__(self, settings: Settings):
        self._url = settings.database_url
        self._pool_size = settings.max_db_connections

    def connect(self) -> str:
        return f"Connected to {self._url} (pool: {self._pool_size})"


class TokenService:
    """Signs tokens using the secret key from settings."""
    def __init__(self, settings: Settings):
        self._secret = settings.secret_key

    def sign(self, payload: str) -> str:
        # Real implementation would use JWT
        import hashlib
        return hashlib.sha256(f"{self._secret}:{payload}".encode()).hexdigest()[:16]


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Settings & Configuration Management")
    print("=" * 55)

    print("\n--- BAD: hardcoded config ---")
    bad_db = DatabaseBad()
    bad_db.connect()
    print("  This URL and key are now in source code.")
    print("  If committed to git, they're there forever.")

    print("\n--- Simulating .env file (setting environment variables) ---")
    # In real dev: these come from a .env file loaded by pydantic-settings
    # Here we set them directly for the demo
    os.environ["DATABASE_URL"] = "postgresql://localhost/myapp_dev"
    os.environ["SECRET_KEY"] = "dev-secret-key-not-for-production"
    os.environ["DEBUG"] = "true"
    os.environ["MAX_DB_CONNECTIONS"] = "5"

    print("\n--- GOOD: settings loaded from environment ---")
    settings = Settings.from_env()
    print(f"  {settings}")  # secret_key is masked
    print(f"  debug:      {settings.debug}")
    print(f"  production: {settings.is_production()}")

    print("\n--- Settings injected into services ---")
    db_service = DatabaseService(settings)
    print(f"  DB: {db_service.connect()}")

    token_service = TokenService(settings)
    token = token_service.sign("user_id=42")
    print(f"  Token (first 16 chars of HMAC): {token}")

    print("\n--- Missing required config fails at startup ---")
    del os.environ["DATABASE_URL"]
    del os.environ["SECRET_KEY"]
    try:
        Settings.from_env()
    except EnvironmentError as e:
        print(f"  EnvironmentError:\n{e}")
    print("  Good — fails immediately at startup, not at 3am in production.")

    print("\n--- Wrong type fails with clear message ---")
    os.environ["DATABASE_URL"] = "sqlite:///dev.db"
    os.environ["SECRET_KEY"] = "mysecret"
    os.environ["MAX_DB_CONNECTIONS"] = "not-a-number"
    try:
        Settings.from_env()
    except EnvironmentError as e:
        print(f"  EnvironmentError: {e}")

    print("\n--- Best practices summary ---")
    print("  .env       → local dev, in .gitignore, NEVER committed")
    print("  .env.example → committed, fake values, documents required vars")
    print("  settings   → one object, one place, type-validated")
    print("  services   → receive settings via injection, don't read os.environ directly")

    print("\n--- What pydantic-settings looks like (code sample) ---")
    print(PYDANTIC_SETTINGS_EXAMPLE)

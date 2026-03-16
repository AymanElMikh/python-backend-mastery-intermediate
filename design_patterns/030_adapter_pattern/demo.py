"""
Demo: Adapter Pattern
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from abc import ABC, abstractmethod


# ── Section 1: Your app's expected interfaces ─────────────────────────────────

class Logger(ABC):
    """The interface YOUR app depends on."""
    @abstractmethod
    def log(self, level: str, message: str) -> None:
        pass


class StorageBackend(ABC):
    """The interface YOUR app uses for file storage."""
    @abstractmethod
    def save(self, key: str, content: bytes) -> str:
        pass

    @abstractmethod
    def load(self, key: str) -> bytes:
        pass


# ── Section 2: Third-party libraries (incompatible interfaces) ───────────────

class DatadogClient:
    """
    Imagine this is the real Datadog SDK.
    It has a completely different API from your Logger.
    """
    def send_event(self, event_type: str, text: str, alert_type: str) -> None:
        print(f"  [Datadog SDK] type={event_type!r} alert={alert_type!r} text={text!r}")


class S3Client:
    """
    Imagine this is the real boto3 S3 client.
    It has a different API from your StorageBackend.
    """
    def put_object(self, Bucket: str, Key: str, Body: bytes) -> dict:
        print(f"  [S3 SDK] PUT s3://{Bucket}/{Key} ({len(Body)} bytes)")
        return {"ETag": "abc123"}

    def get_object(self, Bucket: str, Key: str) -> dict:
        print(f"  [S3 SDK] GET s3://{Bucket}/{Key}")
        return {"Body": b"fake content from S3"}


class SentryClient:
    """Another third-party logger SDK."""
    def capture_message(self, message: str, level: str = "info") -> str:
        print(f"  [Sentry SDK] level={level!r} message={message!r}")
        return "event_id_abc123"

    def capture_exception(self, exc: Exception) -> str:
        print(f"  [Sentry SDK] exception={exc!r}")
        return "event_id_xyz789"


# ── Section 3: Adapters — translate your interface → third-party API ──────────

class DatadogAdapter(Logger):
    """Makes DatadogClient look like Logger."""

    def __init__(self, client: DatadogClient):
        self._client = client  # Wrapped, hidden from callers

    def log(self, level: str, message: str) -> None:
        # Translate: Logger.log() → DatadogClient.send_event()
        alert_type = "error" if level == "ERROR" else "warning" if level == "WARN" else "info"
        self._client.send_event(
            event_type=f"app.{level.lower()}",
            text=message,
            alert_type=alert_type,
        )


class SentryAdapter(Logger):
    """Makes SentryClient look like Logger."""

    def __init__(self, client: SentryClient):
        self._client = client

    def log(self, level: str, message: str) -> None:
        sentry_level = level.lower()  # Sentry uses lowercase
        self._client.capture_message(message=message, level=sentry_level)


class S3Adapter(StorageBackend):
    """Makes S3Client look like StorageBackend."""

    def __init__(self, client: S3Client, bucket: str):
        self._client = client
        self._bucket = bucket  # S3-specific config stays inside the adapter

    def save(self, key: str, content: bytes) -> str:
        self._client.put_object(Bucket=self._bucket, Key=key, Body=content)
        return f"s3://{self._bucket}/{key}"

    def load(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"]


# ── Section 4: Simple default implementations (no third-party needed) ─────────

class ConsoleLogger(Logger):
    """A simple logger for local dev — no adapter needed."""
    def log(self, level: str, message: str) -> None:
        print(f"  [{level}] {message}")


class LocalStorageBackend(StorageBackend):
    """In-memory storage for tests."""
    def __init__(self):
        self._store: dict[str, bytes] = {}

    def save(self, key: str, content: bytes) -> str:
        self._store[key] = content
        return f"local://{key}"

    def load(self, key: str) -> bytes:
        return self._store.get(key, b"")


# ── Section 5: Application code — depends only on interfaces ─────────────────

class UserService:
    """
    Doesn't know if it's using Datadog, Sentry, or console logging.
    Doesn't know if it's using S3 or local storage.
    Just uses the interfaces.
    """
    def __init__(self, logger: Logger, storage: StorageBackend):
        self._logger = logger
        self._storage = storage

    def register_user(self, email: str) -> dict:
        self._logger.log("INFO", f"Registering user: {email}")
        avatar = f"avatar for {email}".encode()
        path = self._storage.save(f"avatars/{email}.png", avatar)
        self._logger.log("INFO", f"Default avatar saved at {path}")
        return {"email": email, "avatar": path}

    def delete_user(self, email: str) -> None:
        self._logger.log("WARN", f"Deleting user: {email}")
        # ... delete logic ...
        self._logger.log("ERROR", f"User {email} deletion triggered audit alert")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Adapter Pattern")
    print("=" * 55)

    print("\n--- Dev environment: ConsoleLogger + LocalStorage ---")
    dev_service = UserService(
        logger=ConsoleLogger(),
        storage=LocalStorageBackend(),
    )
    dev_service.register_user("alice@example.com")

    print("\n--- Production: Datadog + S3 (via adapters) ---")
    prod_service = UserService(
        logger=DatadogAdapter(DatadogClient()),
        storage=S3Adapter(S3Client(), bucket="myapp-prod"),
    )
    prod_service.register_user("bob@example.com")

    print("\n--- Swap logger to Sentry — zero changes to UserService ---")
    sentry_service = UserService(
        logger=SentryAdapter(SentryClient()),
        storage=LocalStorageBackend(),
    )
    sentry_service.delete_user("charlie@example.com")

    print("\n--- Key insight: UserService never changed ---")
    print("  Same code, different adapters = different infrastructure.")
    print("  Adapter hides the third-party API behind your interface.")

    print("\n--- Common mistake: exposing internals ---")
    adapter = DatadogAdapter(DatadogClient())
    # DON'T do this in real code:
    # adapter._client.send_event(...)  # Bypasses the adapter, couples to Datadog
    print("  adapter._client is private — callers should never reach through the adapter.")

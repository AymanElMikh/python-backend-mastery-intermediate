"""
Demo: Interface Segregation Principle (ISP)
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from abc import ABC, abstractmethod
from typing import Optional


# ── Section 1: Fat interface — the problem ────────────────────────────────────

class FatStorageInterface(ABC):
    """
    BAD: One big interface that forces every implementation to define
    save, load, delete, and list — even if the implementation only does one.
    """
    @abstractmethod
    def save(self, key: str, data: bytes) -> None:
        pass

    @abstractmethod
    def load(self, key: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def list_keys(self) -> list[str]:
        pass


class ReadOnlyStorageBad(FatStorageInterface):
    """
    This is a read-only archive — it should never delete or save.
    But the fat interface forces us to implement those methods anyway.
    """
    def __init__(self):
        self._archive = {"report_2025.pdf": b"PDF content here"}

    def load(self, key: str) -> bytes:
        return self._archive.get(key, b"")

    def list_keys(self) -> list[str]:
        return list(self._archive.keys())

    # These shouldn't exist — but the interface forces us to define them
    def save(self, key: str, data: bytes) -> None:
        raise NotImplementedError("This is a read-only archive!")  # surprise at runtime

    def delete(self, key: str) -> None:
        raise NotImplementedError("This is a read-only archive!")  # surprise at runtime


# ── Section 2: Segregated interfaces — the solution ──────────────────────────

class Readable(ABC):
    """Interface for storage that supports reading."""
    @abstractmethod
    def load(self, key: str) -> Optional[bytes]:
        pass


class Writable(ABC):
    """Interface for storage that supports writing."""
    @abstractmethod
    def save(self, key: str, data: bytes) -> None:
        pass


class Deletable(ABC):
    """Interface for storage that supports deletion."""
    @abstractmethod
    def delete(self, key: str) -> None:
        pass


class Listable(ABC):
    """Interface for storage that supports listing keys."""
    @abstractmethod
    def list_keys(self) -> list[str]:
        pass


# Combine interfaces for full-access storage
class FullStorage(Readable, Writable, Deletable, Listable):
    """
    Full read-write-delete storage.
    Only implement this if your storage supports all four operations.
    """
    pass


# ── Section 3: Implementations — only implement what they support ─────────────

class ReadOnlyArchive(Readable, Listable):
    """
    Read-only. Only implements Readable and Listable.
    No stubs, no NotImplementedError surprises.
    Type system will catch misuse at wiring time, not at runtime.
    """
    def __init__(self):
        self._data = {
            "report_2025.pdf": b"Annual report content",
            "audit_log.txt": b"Audit trail data",
        }

    def load(self, key: str) -> Optional[bytes]:
        return self._data.get(key)

    def list_keys(self) -> list[str]:
        return list(self._data.keys())


class WriteOnlyQueue(Writable):
    """
    Write-only append queue (like a log sink).
    Can only save — loading is not supported.
    """
    def __init__(self):
        self._queue: list[tuple[str, bytes]] = []

    def save(self, key: str, data: bytes) -> None:
        self._queue.append((key, data))
        print(f"  [Queue] Appended: {key} ({len(data)} bytes)")

    def pending(self) -> list:
        return self._queue


class InMemoryStorage(FullStorage):
    """
    Full-featured in-memory storage.
    Used in tests — implements all four interfaces.
    """
    def __init__(self):
        self._store: dict[str, bytes] = {}

    def save(self, key: str, data: bytes) -> None:
        self._store[key] = data
        print(f"  [Mem] Saved: {key}")

    def load(self, key: str) -> Optional[bytes]:
        return self._store.get(key)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)
        print(f"  [Mem] Deleted: {key}")

    def list_keys(self) -> list[str]:
        return list(self._store.keys())


# ── Section 4: Services that depend on specific capabilities ─────────────────

class ReportReader:
    """
    Only needs to read reports. Takes a Readable — nothing more.
    Can be used with ReadOnlyArchive OR InMemoryStorage.
    """
    def __init__(self, storage: Readable):
        self._storage = storage

    def get_report(self, filename: str) -> str:
        data = self._storage.load(filename)
        if data is None:
            return f"Report '{filename}' not found"
        return f"Report content: {data.decode()}"


class LogWriter:
    """
    Only needs to write. Takes a Writable.
    Can be used with WriteOnlyQueue OR InMemoryStorage.
    """
    def __init__(self, storage: Writable):
        self._storage = storage

    def log(self, event: str) -> None:
        key = f"log_{event.replace(' ', '_')}.txt"
        self._storage.save(key, event.encode())


class StorageManager:
    """
    Needs all four capabilities. Takes FullStorage.
    """
    def __init__(self, storage: FullStorage):
        self._storage = storage

    def backup(self, key: str, data: bytes) -> None:
        self._storage.save(key, data)

    def restore(self, key: str) -> Optional[bytes]:
        return self._storage.load(key)

    def cleanup(self, key: str) -> None:
        self._storage.delete(key)

    def audit(self) -> list[str]:
        return self._storage.list_keys()


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Interface Segregation Principle")
    print("=" * 55)

    print("\n--- BAD: fat interface forces stubbed methods ---")
    bad = ReadOnlyStorageBad()
    print(f"  load('report_2025.pdf'): {bad.load('report_2025.pdf')}")
    try:
        bad.save("new.pdf", b"data")
    except NotImplementedError as e:
        print(f"  save(): NotImplementedError — surprise at runtime! {e}")

    print("\n--- GOOD: segregated — ReadOnlyArchive has no save/delete ---")
    archive = ReadOnlyArchive()
    reader = ReportReader(archive)  # ReportReader only needs Readable
    print(f"  {reader.get_report('report_2025.pdf')}")
    print(f"  {reader.get_report('audit_log.txt')}")
    print(f"  {reader.get_report('missing.pdf')}")
    print(f"  Available: {archive.list_keys()}")

    print("\n--- WriteOnlyQueue: can write, can't read ---")
    queue = WriteOnlyQueue()
    writer = LogWriter(queue)
    writer.log("user login")
    writer.log("payment processed")
    print(f"  Pending in queue: {[k for k, _ in queue.pending()]}")

    print("\n--- InMemoryStorage: implements all four (FullStorage) ---")
    mem = InMemoryStorage()
    manager = StorageManager(mem)
    manager.backup("config.json", b'{"debug": true}')
    manager.backup("users.csv", b"id,email\n1,alice@x.com")
    print(f"  All keys: {manager.audit()}")
    print(f"  Restore config: {manager.restore('config.json')}")
    manager.cleanup("config.json")
    print(f"  After cleanup: {manager.audit()}")

    print("\n--- Swap implementations — same service, different storage ---")
    # ReportReader works with EITHER ReadOnlyArchive OR InMemoryStorage
    mem_storage = InMemoryStorage()
    mem_storage.save("memo.txt", b"Important memo content")
    mem_reader = ReportReader(mem_storage)  # InMemoryStorage is also Readable
    print(f"  {mem_reader.get_report('memo.txt')}")

    print("\n--- Type safety: passing wrong storage type ---")
    print("  If you try: StorageManager(archive)  ← won't work")
    print("  ReadOnlyArchive is NOT a FullStorage — it's only Readable+Listable")
    print("  The type system catches this at wiring time, not at runtime.")

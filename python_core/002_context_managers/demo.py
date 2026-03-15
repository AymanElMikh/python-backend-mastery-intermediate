"""
Demo: Context Managers — The `with` Statement
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import time
import tempfile
import os
from contextlib import contextmanager

# ── Section 1: Why context managers exist — the problem they solve ─────────────

def read_file_wrong(path):
    """BAD: file might never be closed if an exception occurs."""
    f = open(path, "r")
    content = f.read()
    # if an exception happens here, f.close() never runs → resource leak
    f.close()
    return content

def read_file_right_tryfinally(path):
    """BETTER: try/finally guarantees close, but verbose."""
    f = open(path, "r")
    try:
        content = f.read()
        return content
    finally:
        f.close()  # always runs, even if exception

def read_file_best(path):
    """BEST: context manager is clean and idiomatic."""
    with open(path, "r") as f:
        return f.read()  # f.close() is automatic


# ── Section 2: Writing a custom context manager with @contextmanager ──────────

@contextmanager
def timer(label):
    """Measures execution time of the block inside `with`."""
    start = time.time()
    try:
        yield  # code in the `with` block runs at this point
    finally:
        # finally ensures this runs even if the `with` block raises an exception
        elapsed = time.time() - start
        print(f"  [{label}] completed in {elapsed:.4f}s")


@contextmanager
def temporary_directory():
    """Creates a temp dir, yields it, then cleans up automatically."""
    tmpdir = tempfile.mkdtemp()
    print(f"  Created temp dir: {tmpdir}")
    try:
        yield tmpdir
    finally:
        # cleanup: remove temp files
        for fname in os.listdir(tmpdir):
            os.remove(os.path.join(tmpdir, fname))
        os.rmdir(tmpdir)
        print(f"  Cleaned up temp dir: {tmpdir}")


# ── Section 3: Class-based context manager ────────────────────────────────────

class ManagedConnection:
    """
    Simulates a database connection that must be properly opened and closed.
    Use class-based when you need to store state or have complex __exit__ logic.
    """
    def __init__(self, db_url):
        self.db_url = db_url
        self.conn = None

    def __enter__(self):
        print(f"  Connecting to {self.db_url}...")
        self.conn = f"Connection({self.db_url})"
        return self  # return self so `as conn` gets the ManagedConnection instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # an exception occurred inside the `with` block
            print(f"  Exception occurred: {exc_val}. Rolling back.")
        else:
            print("  Committing transaction.")
        print("  Closing connection.")
        self.conn = None
        return False  # False = let the exception propagate (don't suppress it)

    def execute(self, query):
        return f"Result of: {query}"


# ── Section 4: Common mistake — missing try/finally in @contextmanager ────────

@contextmanager
def bad_context_manager():
    """WRONG: cleanup doesn't run if an exception is raised."""
    print("  Setting up resource (bad)")
    yield
    print("  Cleaning up resource (bad)")  # won't run if exception raised above!

@contextmanager
def good_context_manager():
    """RIGHT: finally ensures cleanup always runs."""
    print("  Setting up resource (good)")
    try:
        yield
    finally:
        print("  Cleaning up resource (good)")  # always runs


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Context Managers — The `with` Statement")
    print("=" * 50)

    print("\n--- Section 1: File reading ---")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        tmp.write("Hello, context managers!")
        tmp_path = tmp.name
    try:
        content = read_file_best(tmp_path)
        print(f"  Read: '{content}'")
    finally:
        os.unlink(tmp_path)

    print("\n--- Section 2: @contextmanager timer ---")
    with timer("simulated work"):
        time.sleep(0.05)

    print("\n--- Section 2b: temporary_directory ---")
    with temporary_directory() as tmpdir:
        # create a file in it
        filepath = os.path.join(tmpdir, "test.txt")
        with open(filepath, "w") as f:
            f.write("temp data")
        print(f"  File created: {os.path.exists(filepath)}")

    print("\n--- Section 3: class-based context manager ---")
    with ManagedConnection("postgres://localhost/mydb") as db:
        result = db.execute("SELECT * FROM users")
        print(f"  Query result: {result}")

    print("\n--- Section 3b: exception inside with block ---")
    try:
        with ManagedConnection("postgres://localhost/mydb") as db:
            raise ValueError("Something went wrong in the business logic")
    except ValueError:
        print("  Exception was re-raised (not suppressed)")

    print("\n--- Section 4: missing try/finally ---")
    print("  Good context manager (exception case):")
    try:
        with good_context_manager():
            raise RuntimeError("simulated error")
    except RuntimeError:
        pass

    print("  Bad context manager (exception case):")
    try:
        with bad_context_manager():
            raise RuntimeError("simulated error")
    except RuntimeError:
        pass
    # notice: "Cleaning up resource (bad)" was NOT printed above

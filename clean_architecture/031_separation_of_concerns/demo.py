"""
Demo: Separation of Concerns
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

# ── Section 1: The "everything in one place" anti-pattern ────────────────────

class FakeDB:
    """Simulates a database session."""
    def __init__(self):
        self._store = {}
        self._next_id = 1

    def find(self, email):
        return next((u for u in self._store.values() if u["email"] == email), None)

    def insert(self, record):
        record["id"] = self._next_id
        self._store[self._next_id] = record
        self._next_id += 1
        return record

db = FakeDB()


def handle_create_user_bad(request_body: dict) -> tuple[dict, int]:
    """
    BAD: Route handler doing everything.
    Validation + business rule + DB query + DB write + email + response formatting.
    To test the "no duplicate email" rule, you need a full HTTP request + DB.
    """
    # Validation
    if not request_body.get("email"):
        return {"error": "email required"}, 400

    email = request_body["email"].strip().lower()

    # Business rule (mixed into route)
    if db.find(email):
        return {"error": "email already registered"}, 409

    # DB write (mixed into route)
    user = db.insert({"email": email, "role": "user"})

    # Side effect (mixed into route)
    print(f"  [Email] Sending welcome email to {email}")

    # Response formatting (fair, but mixed with everything else)
    return {"id": user["id"], "email": user["email"]}, 201


# ── Section 2: The same logic, properly separated ────────────────────────────

# --- Repository layer: only talks to the DB ---

class UserRepository:
    def __init__(self, db):
        self._db = db

    def find_by_email(self, email: str) -> dict | None:
        return self._db.find(email)

    def save(self, user: dict) -> dict:
        return self._db.insert(user)


# --- Email service: only sends emails ---

class EmailService:
    def send_welcome(self, email: str) -> None:
        print(f"  [Email] Welcome email sent to {email}")


# --- Service layer: only business logic ---

class EmailAlreadyExistsError(Exception):
    """A clear domain error — not an HTTP error, not a DB error."""
    pass


class UserService:
    def __init__(self, repo: UserRepository, email_svc: EmailService):
        self._repo = repo
        self._email_svc = email_svc

    def register(self, email: str) -> dict:
        """
        Pure business logic. No HTTP. No SQL. No JSON.
        Easy to test: inject a fake repo and fake email service.
        """
        email = email.strip().lower()

        if self._repo.find_by_email(email):
            raise EmailAlreadyExistsError(f"'{email}' is already registered")

        user = self._repo.save({"email": email, "role": "user"})
        self._email_svc.send_welcome(user["email"])
        return user


# --- Route layer: only handles HTTP concerns ---

def handle_create_user_good(request_body: dict, service: UserService) -> tuple[dict, int]:
    """
    GOOD: Route handler only does HTTP things.
    - Parses input
    - Calls service
    - Converts domain error → HTTP error
    - Returns HTTP response
    """
    if not request_body.get("email"):
        return {"error": "email required"}, 400

    try:
        user = service.register(request_body["email"])
    except EmailAlreadyExistsError as e:
        return {"error": str(e)}, 409

    # Route layer formats the response (it knows about HTTP, the service doesn't)
    return {"id": user["id"], "email": user["email"]}, 201


# ── Section 3: Testing each layer independently ───────────────────────────────

class FakeUserRepository:
    """Test double — no real DB needed to test UserService."""
    def __init__(self, existing_emails: list[str] = None):
        self._emails = set(existing_emails or [])
        self._saved = []

    def find_by_email(self, email: str) -> dict | None:
        return {"email": email} if email in self._emails else None

    def save(self, user: dict) -> dict:
        user["id"] = len(self._saved) + 1
        self._saved.append(user)
        self._emails.add(user["email"])
        return user


class FakeEmailService:
    def __init__(self):
        self.sent = []

    def send_welcome(self, email: str) -> None:
        self.sent.append(email)


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Separation of Concerns")
    print("=" * 55)

    print("\n--- BAD: everything in the route handler ---")
    resp, status = handle_create_user_bad({"email": "alice@example.com"})
    print(f"  POST /users → {status}: {resp}")
    resp, status = handle_create_user_bad({"email": "alice@example.com"})
    print(f"  POST /users (dup) → {status}: {resp}")
    resp, status = handle_create_user_bad({})
    print(f"  POST /users (no email) → {status}: {resp}")

    print("\n--- GOOD: 3 layers, each with one job ---")
    clean_db = FakeDB()
    repo = UserRepository(clean_db)
    email_svc = EmailService()
    service = UserService(repo, email_svc)

    resp, status = handle_create_user_good({"email": "bob@example.com"}, service)
    print(f"  POST /users → {status}: {resp}")
    resp, status = handle_create_user_good({"email": "bob@example.com"}, service)
    print(f"  POST /users (dup) → {status}: {resp}")
    resp, status = handle_create_user_good({}, service)
    print(f"  POST /users (no email) → {status}: {resp}")

    print("\n--- Testing the service in isolation (no HTTP, no real DB) ---")
    fake_repo = FakeUserRepository(existing_emails=["existing@example.com"])
    fake_email = FakeEmailService()
    test_service = UserService(fake_repo, fake_email)

    # Test happy path
    user = test_service.register("newuser@example.com")
    assert user["email"] == "newuser@example.com"
    assert fake_email.sent == ["newuser@example.com"]
    print("  ✓ register() creates user and sends welcome email")

    # Test duplicate email
    try:
        test_service.register("existing@example.com")
        assert False, "Should have raised"
    except EmailAlreadyExistsError:
        print("  ✓ register() raises EmailAlreadyExistsError for duplicates")

    print("\n  All service tests pass — no HTTP server, no database needed.")

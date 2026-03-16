# Service Layer

## 🎯 Interview Question
What goes in the service layer of a Python backend, and what should NOT go there?

## 💡 Short Answer (30 seconds)
The service layer contains your business rules and orchestration logic — the "what the application does" independent of how it's delivered (HTTP) or stored (database). It validates business constraints, coordinates multiple repositories, handles transactions, and triggers side effects like emails. What doesn't go there: SQL queries (repository's job), HTTP status codes (route's job), or response formatting.

## 🔬 Explanation
The service layer is the heart of your application. If a competitor copied your code but used gRPC instead of HTTP and MongoDB instead of PostgreSQL, the service layer would be identical — because it expresses what your app *does*, not *how* it communicates or stores data.

A good service:
- Takes plain Python types or domain objects as input (not `Request` objects)
- Returns domain objects (not HTTP responses or ORM models)
- Raises domain-specific exceptions (`InsufficientFundsError`, not `HTTPException(400)`)
- Coordinates: calls the repo, calls email, checks rules
- Is easy to unit test with fakes injected

A service that's getting too big should be split into smaller, focused services.

## 💻 Code Example
```python
class TransferService:
    def __init__(self, account_repo, notification_svc, ledger_repo):
        self._accounts = account_repo
        self._notify = notification_svc
        self._ledger = ledger_repo

    def transfer(self, from_id: int, to_id: int, amount: float) -> Transfer:
        # Rule 1: both accounts must exist
        sender = self._accounts.get(from_id)
        recipient = self._accounts.get(to_id)
        if not sender or not recipient:
            raise AccountNotFoundError(from_id if not sender else to_id)

        # Rule 2: sufficient funds
        if sender.balance < amount:
            raise InsufficientFundsError(sender.balance, amount)

        # Rule 3: amount must be positive
        if amount <= 0:
            raise InvalidAmountError(amount)

        # Orchestrate: debit, credit, record, notify
        self._accounts.deduct(from_id, amount)
        self._accounts.add(to_id, amount)
        transfer = self._ledger.record(from_id, to_id, amount)
        self._notify.send(sender.email, f"Transfer of ${amount} sent")
        return transfer
```

## ⚠️ Common Mistakes
1. **Importing `HTTPException` in services.** Services should raise domain exceptions (`InsufficientFundsError`). The route layer translates those to HTTP errors. If you import FastAPI/Flask into your service, you've broken the separation.
2. **Making services too thin.** A service that just calls `repo.save(data)` with no validation or rules is useless indirection. Put real business rules in services.
3. **Making services too thick.** When a service grows to 500+ lines, it's doing too much. Split by domain concept (e.g., `UserRegistrationService`, `UserProfileService`, `UserAuthService`).

## ✅ When to Use vs When NOT to Use
**Always have a service layer for:**
- Any operation with business rules
- Operations that touch multiple repositories
- Operations with side effects (email, notifications, audit logs)

**Skip the service layer for:**
- Simple CRUD with no rules — a route calling a repo directly is fine for "list all tags"
- Read-only views with no business logic

## 🔗 Related Concepts
- [clean_architecture/031_separation_of_concerns](../031_separation_of_concerns) — why the service layer exists
- [clean_architecture/033_dependency_injection](../033_dependency_injection) — how services receive their dependencies
- [clean_architecture/038_custom_exceptions](../038_custom_exceptions) — domain exceptions the service raises

## 🚀 Next Step
In `python-backend-mastery`: **Application services vs Domain services** — the distinction between orchestration logic (application service) and pure domain logic (domain service/entity methods) in DDD.

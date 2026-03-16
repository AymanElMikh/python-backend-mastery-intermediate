"""
Demo: Service Layer
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Domain objects ────────────────────────────────────────────────────────────

@dataclass
class Account:
    id: int
    owner: str
    email: str
    balance: float


@dataclass
class Transfer:
    id: int
    from_id: int
    to_id: int
    amount: float


# ── Domain exceptions (service raises these, route translates to HTTP) ────────

class AccountNotFoundError(Exception):
    def __init__(self, account_id: int):
        super().__init__(f"Account #{account_id} not found")
        self.account_id = account_id

class InsufficientFundsError(Exception):
    def __init__(self, available: float, requested: float):
        super().__init__(f"Insufficient funds: have ${available:.2f}, need ${requested:.2f}")
        self.available = available
        self.requested = requested

class InvalidAmountError(Exception):
    def __init__(self, amount: float):
        super().__init__(f"Amount must be positive, got: {amount}")


# ── Repositories (data layer) ─────────────────────────────────────────────────

class AccountRepository:
    def __init__(self):
        self._accounts = {
            1: Account(id=1, owner="Alice", email="alice@example.com", balance=1000.00),
            2: Account(id=2, owner="Bob",   email="bob@example.com",   balance=250.00),
            3: Account(id=3, owner="Carol", email="carol@example.com", balance=500.00),
        }

    def get(self, account_id: int) -> Optional[Account]:
        return self._accounts.get(account_id)

    def deduct(self, account_id: int, amount: float) -> None:
        self._accounts[account_id].balance -= amount
        print(f"    [DB] Account #{account_id} balance: ${self._accounts[account_id].balance:.2f}")

    def add(self, account_id: int, amount: float) -> None:
        self._accounts[account_id].balance += amount
        print(f"    [DB] Account #{account_id} balance: ${self._accounts[account_id].balance:.2f}")

    def get_balance(self, account_id: int) -> Optional[float]:
        acct = self._accounts.get(account_id)
        return acct.balance if acct else None


class TransferLedger:
    def __init__(self):
        self._transfers: list[Transfer] = []
        self._next_id = 1

    def record(self, from_id: int, to_id: int, amount: float) -> Transfer:
        t = Transfer(id=self._next_id, from_id=from_id, to_id=to_id, amount=amount)
        self._transfers.append(t)
        self._next_id += 1
        return t

    def list_all(self) -> list[Transfer]:
        return list(self._transfers)


class NotificationService:
    def __init__(self):
        self.sent: list[str] = []

    def send(self, email: str, message: str) -> None:
        msg = f"{email}: {message}"
        self.sent.append(msg)
        print(f"    [Email] {msg}")


# ── Service Layer ──────────────────────────────────────────────────────────────

class TransferService:
    """
    The service layer. Contains all transfer business rules.
    No SQL, no HTTP, no JSON — pure Python domain logic.
    """
    def __init__(
        self,
        accounts: AccountRepository,
        ledger: TransferLedger,
        notify: NotificationService,
    ):
        self._accounts = accounts
        self._ledger = ledger
        self._notify = notify

    def transfer(self, from_id: int, to_id: int, amount: float) -> Transfer:
        """
        Orchestrates a complete transfer:
        1. Validate inputs
        2. Check both accounts exist
        3. Check sufficient funds
        4. Debit, credit, record, notify
        """
        # Rule: valid amount
        if amount <= 0:
            raise InvalidAmountError(amount)

        # Rule: accounts must exist
        sender = self._accounts.get(from_id)
        if sender is None:
            raise AccountNotFoundError(from_id)

        recipient = self._accounts.get(to_id)
        if recipient is None:
            raise AccountNotFoundError(to_id)

        # Rule: sufficient funds
        if sender.balance < amount:
            raise InsufficientFundsError(sender.balance, amount)

        # Orchestrate the operation
        self._accounts.deduct(from_id, amount)
        self._accounts.add(to_id, amount)
        transfer = self._ledger.record(from_id, to_id, amount)
        self._notify.send(sender.email, f"Sent ${amount:.2f} to {recipient.owner}")
        self._notify.send(recipient.email, f"Received ${amount:.2f} from {sender.owner}")

        return transfer

    def get_balance(self, account_id: int) -> float:
        acct = self._accounts.get(account_id)
        if acct is None:
            raise AccountNotFoundError(account_id)
        return acct.balance


# ── Route Layer (translates domain errors to HTTP) ────────────────────────────

def post_transfer(body: dict, service: TransferService) -> tuple[dict, int]:
    try:
        t = service.transfer(body["from_id"], body["to_id"], body["amount"])
        return {"transfer_id": t.id, "amount": t.amount, "status": "completed"}, 201
    except InvalidAmountError as e:
        return {"error": str(e)}, 400
    except AccountNotFoundError as e:
        return {"error": str(e)}, 404
    except InsufficientFundsError as e:
        return {"error": str(e)}, 422


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Service Layer")
    print("=" * 55)

    accounts = AccountRepository()
    ledger = TransferLedger()
    notify = NotificationService()
    service = TransferService(accounts, ledger, notify)

    print("\n--- Happy path: Alice sends $200 to Bob ---")
    resp, status = post_transfer({"from_id": 1, "to_id": 2, "amount": 200.00}, service)
    print(f"  → {status}: {resp}")

    print(f"\n  Alice's new balance: ${service.get_balance(1):.2f}")
    print(f"  Bob's new balance:   ${service.get_balance(2):.2f}")

    print("\n--- Insufficient funds: Bob tries to send $500 ---")
    resp, status = post_transfer({"from_id": 2, "to_id": 3, "amount": 500.00}, service)
    print(f"  → {status}: {resp}")

    print("\n--- Account not found ---")
    resp, status = post_transfer({"from_id": 99, "to_id": 1, "amount": 10.00}, service)
    print(f"  → {status}: {resp}")

    print("\n--- Invalid amount ---")
    resp, status = post_transfer({"from_id": 1, "to_id": 2, "amount": -50.00}, service)
    print(f"  → {status}: {resp}")

    print("\n--- Ledger history ---")
    for t in ledger.list_all():
        print(f"  Transfer #{t.id}: account #{t.from_id} → #{t.to_id} ${t.amount:.2f}")

    print("\n--- What belongs in the service layer ---")
    print("  ✓ Business rules (sufficient funds, valid amount)")
    print("  ✓ Orchestration (deduct + credit + record + notify)")
    print("  ✓ Domain exceptions (InsufficientFundsError, not HTTPException)")
    print("  ✗ SQL queries       → repository")
    print("  ✗ HTTP status codes → route layer")
    print("  ✗ JSON formatting   → route layer")

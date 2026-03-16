"""
Demo: Domain Model vs Database Model
Level: Intermediate (2–3 years experience)
Run:  python demo.py

Note: Uses a simulated ORM instead of real SQLAlchemy to keep this zero-setup.
The pattern is identical with real SQLAlchemy.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


# ══════════════════════════════════════════════════════
# DATABASE MODEL (ORM layer)
# Represents how data is stored. No business methods.
# In real SQLAlchemy: inherits from Base, has Column() fields.
# ══════════════════════════════════════════════════════

class UserORM:
    """
    Simulates a SQLAlchemy ORM model.
    Its job: map Python ↔ database rows.
    It should NOT have business methods.
    """
    __tablename__ = "users"

    def __init__(self, id, email, name, plan_id, subscription_expires_at,
                 stripe_customer_id, is_deleted):
        self.id = id
        self.email = email
        self.name = name
        self.plan_id = plan_id                          # FK to plans table
        self.subscription_expires_at = subscription_expires_at
        self.stripe_customer_id = stripe_customer_id   # payment system detail
        self.is_deleted = is_deleted                    # soft delete flag

    def __repr__(self):
        return f"UserORM(id={self.id}, email={self.email!r}, plan_id={self.plan_id})"


# ══════════════════════════════════════════════════════
# DOMAIN MODEL
# Represents business concepts. No ORM. Pure Python.
# Can have methods that express business rules.
# ══════════════════════════════════════════════════════

@dataclass
class User:
    """
    Domain model: the business's view of a User.
    No SQLAlchemy, no session, no ORM concerns.
    Has methods that express what a User can DO.
    """
    id: int
    email: str
    name: str
    plan: str                               # "free", "pro", "enterprise"
    subscription_expires_at: Optional[datetime]

    def is_subscriber(self) -> bool:
        """Business rule: is the subscription currently active?"""
        if self.plan == "free":
            return False
        if self.subscription_expires_at is None:
            return False
        return self.subscription_expires_at > datetime.now()

    def can_export_data(self) -> bool:
        """Feature gate: only subscribers can export."""
        return self.is_subscriber()

    def can_invite_team(self) -> bool:
        """Feature gate: only enterprise plan."""
        return self.plan == "enterprise" and self.is_subscriber()

    def days_until_renewal(self) -> Optional[int]:
        """How many days until subscription expires?"""
        if not self.is_subscriber():
            return None
        delta = self.subscription_expires_at - datetime.now()
        return max(0, delta.days)

    def display_name(self) -> str:
        """Presentation helper — what to show in the UI."""
        tier = f"[{self.plan.upper()}]" if self.plan != "free" else ""
        return f"{self.name} {tier}".strip()


# ══════════════════════════════════════════════════════
# REPOSITORY: maps ORM ↔ Domain
# The repository is the ONLY place that knows about both models.
# ══════════════════════════════════════════════════════

PLAN_MAP = {1: "free", 2: "pro", 3: "enterprise"}
PLAN_ID_MAP = {v: k for k, v in PLAN_MAP.items()}


class UserRepository:
    def __init__(self):
        # Fake in-memory "database" of ORM objects
        self._db: dict[int, UserORM] = {
            1: UserORM(1, "alice@x.com", "Alice", 3,
                       datetime.now() + timedelta(days=30), "cus_abc", False),
            2: UserORM(2, "bob@x.com", "Bob",   2,
                       datetime.now() - timedelta(days=5),  "cus_def", False),  # expired
            3: UserORM(3, "carol@x.com","Carol", 1,
                       None, None, False),                                       # free plan
            4: UserORM(4, "dave@x.com", "Dave",  2,
                       datetime.now() + timedelta(days=90), "cus_ghi", False),
        }

    def get_by_id(self, user_id: int) -> Optional[User]:
        orm = self._db.get(user_id)
        if orm is None or orm.is_deleted:
            return None
        return self._to_domain(orm)

    def list_active(self) -> list[User]:
        return [
            self._to_domain(orm)
            for orm in self._db.values()
            if not orm.is_deleted
        ]

    def _to_domain(self, orm: UserORM) -> User:
        """
        The mapping function. This is the bridge between ORM and domain.
        When schema changes, update here — domain model stays clean.
        """
        return User(
            id=orm.id,
            email=orm.email,
            name=orm.name,
            plan=PLAN_MAP.get(orm.plan_id, "free"),
            subscription_expires_at=orm.subscription_expires_at,
            # Note: stripe_customer_id and is_deleted are NOT in the domain model
            # — they're infrastructure concerns the service doesn't need to know about
        )

    def _to_orm(self, domain: User) -> UserORM:
        """Reverse mapping: domain → ORM for saving."""
        orm = self._db.get(domain.id)
        if orm is None:
            raise ValueError(f"User #{domain.id} not in DB")
        orm.email = domain.email
        orm.name = domain.name
        orm.plan_id = PLAN_ID_MAP.get(domain.plan, 1)
        orm.subscription_expires_at = domain.subscription_expires_at
        return orm


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Domain Model vs Database Model")
    print("=" * 55)

    repo = UserRepository()

    print("\n--- ORM model (raw DB representation) ---")
    for orm in repo._db.values():
        print(f"  {orm} | stripe={orm.stripe_customer_id} | deleted={orm.is_deleted}")

    print("\n--- Domain model (business view) ---")
    users = repo.list_active()
    for user in users:
        print(f"  id={user.id} | {user.display_name():20s} | plan={user.plan:10s} | subscriber={user.is_subscriber()}")

    print("\n--- Business rules on domain model (no DB needed) ---")
    alice = repo.get_by_id(1)
    bob   = repo.get_by_id(2)
    carol = repo.get_by_id(3)
    dave  = repo.get_by_id(4)

    print(f"\n  Alice (enterprise, active):")
    print(f"    can_export_data: {alice.can_export_data()}")
    print(f"    can_invite_team: {alice.can_invite_team()}")
    print(f"    days_until_renewal: {alice.days_until_renewal()}")

    print(f"\n  Bob (pro, EXPIRED):")
    print(f"    is_subscriber:   {bob.is_subscriber()}")
    print(f"    can_export_data: {bob.can_export_data()}")

    print(f"\n  Carol (free plan):")
    print(f"    is_subscriber:   {carol.is_subscriber()}")
    print(f"    can_export_data: {carol.can_export_data()}")
    print(f"    can_invite_team: {carol.can_invite_team()}")

    print(f"\n  Dave (pro, 90 days left):")
    print(f"    days_until_renewal: {dave.days_until_renewal()}")

    print("\n--- Key insight ---")
    print("  ORM model has: plan_id (FK), stripe_customer_id, is_deleted")
    print("  Domain model has: plan (name), no stripe, no soft-delete flag")
    print("  Business rules (is_subscriber, can_export) live on the domain model.")
    print("  SQLAlchemy knows nothing about business rules.")
    print("  Business rules know nothing about SQLAlchemy.")

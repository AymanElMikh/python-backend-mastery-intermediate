# Domain Model vs Database Model

## 🎯 Interview Question
What's the difference between a domain model and a database model, and why would you keep them separate?

## 💡 Short Answer (30 seconds)
The domain model represents your business concepts in pure Python — no ORM, no SQL, no database concerns. The database model (ORM model) represents how data is stored and related in your DB. Keeping them separate means your business logic doesn't depend on SQLAlchemy or any specific database, you can change your schema without touching business rules, and your domain objects can have behavior that SQLAlchemy models shouldn't.

## 🔬 Explanation
Consider a `User` in your business domain: they have an email, a name, a subscription tier, and methods like `can_access_feature(feature)` or `is_trial_expired()`. These are business concepts.

Your DB table for User might look different: it has `subscription_expires_at` instead of a computed `is_trial_expired`, it has foreign keys to a `plans` table, it has columns like `created_at`, `updated_at`, and `stripe_customer_id` that are implementation details.

If you use the SQLAlchemy model as your domain model:
- Every service that touches `User` depends on SQLAlchemy
- Moving to a different ORM means rewriting your business logic
- SQLAlchemy model methods mix ORM concerns (`session`, `lazy loading`) with business rules

Keeping them separate means the repository converts between the two: DB model in, domain object out.

For small apps this distinction may be overkill. For anything with real business rules or that you plan to maintain for years, it pays off.

## 💻 Code Example
```python
from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ── Database model (ORM) — knows about SQLAlchemy ──
class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    subscription_expires_at = Column(DateTime, nullable=True)

# ── Domain model — pure Python, no SQLAlchemy ──
@dataclass
class User:
    id: int
    email: str
    name: str
    subscription_expires_at: datetime | None

    def is_subscriber(self) -> bool:
        if self.subscription_expires_at is None:
            return False
        return self.subscription_expires_at > datetime.now()

    def can_export_data(self) -> bool:
        return self.is_subscriber()

# ── Repository maps between the two ──
class UserRepository:
    def get_by_id(self, user_id: int) -> User | None:
        orm_user = self._session.query(UserORM).get(user_id)
        if orm_user is None:
            return None
        return self._to_domain(orm_user)

    def _to_domain(self, orm: UserORM) -> User:
        return User(id=orm.id, email=orm.email, name=orm.name,
                    subscription_expires_at=orm.subscription_expires_at)
```

## ⚠️ Common Mistakes
1. **Putting business methods on ORM models.** `UserORM.is_subscriber()` works until you need to test it without a database session. Domain methods belong on the domain model.
2. **Skipping the separation for small apps, then regretting it when the app grows.** It's harder to separate after the fact. At least keep business rules off ORM models from the start.
3. **Forgetting to map all fields.** When you add a column to the ORM model, update the `_to_domain()` mapping or you'll get stale data in domain objects silently.

## ✅ When to Use vs When NOT to Use
**Use when:**
- The app has real business rules that need testing
- You may change your ORM or database in the future
- The domain model and DB schema differ significantly

**Don't use when:**
- It's a CRUD app with no real business rules — the ORM model is the whole story
- The app is tiny and the added mapping code is more burden than benefit

## 🔗 Related Concepts
- [clean_architecture/034_dto_pattern](../034_dto_pattern) — DTOs at the API boundary; domain/DB split at the data layer
- [design_patterns/026_repository_pattern](../../design_patterns/026_repository_pattern) — the repository is where mapping happens
- [databases](../../databases) — SQLAlchemy ORM model details

## 🚀 Next Step
In `python-backend-mastery`: **Aggregate roots and invariants** — DDD concept where domain models enforce their own consistency rules, preventing invalid states from ever being persisted.

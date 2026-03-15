# Composition vs Inheritance — Choosing the Right Relationship

## 🎯 Interview Question
"What's the difference between composition and inheritance in Python? When would you choose one over the other?"

## 💡 Short Answer (30 seconds)
Inheritance is an "is-a" relationship — a Dog is-a Animal. Composition is a "has-a" relationship — a Car has-an Engine. You should prefer composition when you want to reuse behavior without creating a strict type relationship. Inheritance is best for true hierarchies (User → AdminUser) and polymorphism. In practice, composition tends to make code more flexible and testable — it's easier to swap a component than to change an inheritance chain.

## 🔬 Explanation
**The "is-a vs has-a" test:**
- `AdminUser` **is-a** `User` → inheritance makes sense
- `Car` **has-an** `Engine` → composition makes sense
- `UserService` **uses** `EmailSender` → composition (not inheritance!)

**Why "favor composition over inheritance" (classic OOP advice):**

1. **Flexibility**: you can swap composed objects at runtime (or in tests). You can't swap a parent class.
2. **Avoids fragile base class problem**: changing the parent can silently break all children.
3. **No accidental coupling**: inheriting gives you *everything* in the parent, even methods you didn't want.
4. **Easier testing**: inject mock dependencies rather than inheriting from a base that has side effects.

**When inheritance is still right:**
- Genuine type hierarchies where polymorphism is needed
- Exception hierarchies (`NotFoundError(AppError)`)
- Framework integration (`class UserModel(Base)` for SQLAlchemy)

A practical rule: if you find yourself inheriting from a class just to reuse 1–2 methods, that's a sign composition would serve you better.

## 💻 Code Example
```python
# BAD: using inheritance just to reuse send_email
class UserService(EmailService):  # UserService IS-A EmailService? No!
    def register(self, user):
        ...
        self.send_email(user.email, "Welcome!")

# GOOD: compose the dependency
class UserService:
    def __init__(self, email_service: EmailService):  # UserService HAS-A EmailService
        self.email_service = email_service

    def register(self, user):
        ...
        self.email_service.send(user.email, "Welcome!")
```

The composition version lets you inject a mock email service in tests without network calls.

## ⚠️ Common Mistakes

1. **Inheriting for code reuse, not type relationships** — the most common mistake. If you're inheriting just to share `send_email()` or `log()`, inject those as dependencies instead.

2. **Deep inheritance hierarchies** — more than 2–3 levels deep becomes very hard to reason about. Each level adds cognitive overhead when tracing method calls.

3. **Tightly coupled tests** — if `UserService(EmailService)` uses inheritance, you can't test `UserService` without also exercising `EmailService`. With composition, inject a fake/mock.

## ✅ When to Use vs When NOT to Use

**Use inheritance when:**
- There's a true "is-a" relationship and you want polymorphism
- Building exception hierarchies
- Integrating with frameworks that require it (SQLAlchemy `Base`, Pydantic `BaseModel`)

**Use composition when:**
- You want to reuse behavior without a type relationship
- You need to swap implementations (especially in tests)
- Multiple unrelated capabilities are needed — compose them, don't inherit

## 🔗 Related Concepts
- [012_inheritance_super](../012_inheritance_super) — when inheritance IS appropriate
- [014_abstract_base_classes](../014_abstract_base_classes) — ABC defines interfaces for composition targets
- [020_mixin_pattern](../020_mixin_pattern) — a middle ground: adding behavior without deep hierarchies

## 🚀 Next Step
In `python-backend-mastery`: **Dependency Injection containers** — frameworks like `dependency-injector` or FastAPI's `Depends()` that automate composition at scale, and how this enables clean architecture.

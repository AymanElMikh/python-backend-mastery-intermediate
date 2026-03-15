# Inheritance and `super()` — Building on Existing Classes

## 🎯 Interview Question
"How does inheritance work in Python? When would you use `super()` and what does it do?"

## 💡 Short Answer (30 seconds)
Inheritance lets a child class reuse and extend a parent class. `super()` gives you a reference to the parent class so you can call its methods — most commonly `super().__init__(...)` to run the parent's setup before adding the child's own setup. You use inheritance when there's a genuine "is-a" relationship and you want to share behavior, not just code.

## 🔬 Explanation
When class `Dog` inherits from `Animal`, `Dog` gets all of `Animal`'s methods and attributes. You can:
- **Use** them as-is (inherited behavior)
- **Override** them (replace with child-specific behavior)
- **Extend** them (call `super().method()` then add more)

**`super()` explained**: it returns a proxy object that delegates method calls to the parent class following the MRO (Method Resolution Order). In simple single-inheritance cases, it's straightforward — it calls the parent. Always use `super().__init__()` at the start of a child's `__init__` to ensure the parent is properly initialized first.

**When inheritance makes sense in backend code:**
- `AdminUser(User)` — same as user, adds `can_delete_users` permissions
- `SQLAlchemyRepository(BaseRepository)` — implements the abstract interface for SQL
- `ValidationError(AppError)` — custom exception hierarchy (from [007_exception_handling](../007_exception_handling))
- `TimestampedModel(Base)` — all DB models that need `created_at`/`updated_at`

**The rule of thumb**: only inherit if the child truly "is a" kind of the parent. If you're just reusing some methods, prefer composition instead (see [015_composition_vs_inheritance](../015_composition_vs_inheritance)).

## 💻 Code Example
```python
class Animal:
    def __init__(self, name: str, sound: str):
        self.name = name
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name} says {self.sound}"

class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name, sound="Woof")  # initialize parent first
        self.breed = breed  # then add child-specific attributes

    def fetch(self) -> str:
        return f"{self.name} fetches the ball!"

    def speak(self) -> str:
        # Extend parent behavior
        base = super().speak()
        return f"{base} (tail wagging)"

rex = Dog("Rex", "Labrador")
print(rex.speak())   # Rex says Woof (tail wagging)
print(rex.fetch())   # Rex fetches the ball!
print(isinstance(rex, Animal))  # True — Dog IS-A Animal
```

## ⚠️ Common Mistakes

1. **Forgetting `super().__init__()`** — if a parent `__init__` sets up important attributes and you don't call `super().__init__()`, the parent's setup never runs. Accessing those attributes later gives `AttributeError`.

2. **Inheriting just to reuse code** — if `Car` and `Animal` both need a `start()` method, don't make one inherit from the other. They're not related — use a mixin or composition.

3. **Overriding without calling `super()`** when you should** — if you override a method but need the parent's behavior too, call `super().method()`. Forgetting this silently drops parent logic.

## ✅ When to Use vs When NOT to Use

**Use inheritance when:**
- There's a true "is-a" relationship (Dog is-a Animal, AdminUser is-a User)
- You want polymorphism — treating different subclasses uniformly
- Sharing behavior in an exception hierarchy or a framework's base class

**Avoid inheritance when:**
- You just want to reuse some methods — use composition or mixins
- The relationship is "has-a" or "uses-a" (a Car *has* an Engine, doesn't *inherit* Engine)
- Deep inheritance chains (3+ levels) — hard to debug, prefer flatter designs

## 🔗 Related Concepts
- [014_abstract_base_classes](../014_abstract_base_classes) — enforcing what subclasses must implement
- [015_composition_vs_inheritance](../015_composition_vs_inheritance) — when NOT to use inheritance
- [020_mixin_pattern](../020_mixin_pattern) — adding capabilities without deep hierarchies

## 🚀 Next Step
In `python-backend-mastery`: **MRO (Method Resolution Order) and cooperative multiple inheritance** — how Python's C3 linearization resolves diamond inheritance, and why `super()` is essential for cooperative mixin chains.

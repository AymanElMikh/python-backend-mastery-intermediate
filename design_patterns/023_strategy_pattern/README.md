# Strategy Pattern

## 🎯 Interview Question
What is the Strategy pattern and can you give a real backend example of where you'd use it?

## 💡 Short Answer (30 seconds)
The Strategy pattern lets you swap out an algorithm or behavior at runtime without changing the code that uses it. You define a common interface, write multiple implementations, and inject whichever one you need. A classic backend example: a payment processor that supports Stripe, PayPal, and bank transfer — same interface, different strategies.

## 🔬 Explanation
Without the Strategy pattern, you end up with a big `if/elif` block inside your processing function: "if payment method is stripe, do this; elif paypal, do that." Every new payment method means editing that function, which violates the Open/Closed Principle — open for extension, closed for modification.

With Strategy, you write a `PaymentProcessor` class that accepts a `strategy` object. The class calls `strategy.charge(amount)` without knowing which payment provider it's talking to. New providers? Create a new class, inject it. No existing code changes.

In Python, strategies are often just objects with a single method — or even plain functions, since functions are first-class. You don't always need a formal abstract class, though it helps with documentation and type checking.

## 💻 Code Example
```python
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def charge(self, amount: float) -> str:
        pass

class StripeStrategy(PaymentStrategy):
    def charge(self, amount: float) -> str:
        return f"Stripe: charged ${amount:.2f}"

class PayPalStrategy(PaymentStrategy):
    def charge(self, amount: float) -> str:
        return f"PayPal: charged ${amount:.2f}"

class OrderProcessor:
    def __init__(self, payment_strategy: PaymentStrategy):
        # Strategy is injected — OrderProcessor doesn't pick it
        self._strategy = payment_strategy

    def checkout(self, amount: float) -> str:
        return self._strategy.charge(amount)

# Swap strategies without changing OrderProcessor
processor = OrderProcessor(StripeStrategy())
print(processor.checkout(99.99))   # Stripe: charged $99.99

processor = OrderProcessor(PayPalStrategy())
print(processor.checkout(49.00))   # PayPal: charged $49.00
```

## ⚠️ Common Mistakes
1. **Hardcoding the strategy inside the class.** `self._strategy = StripeStrategy()` defeats the purpose. The strategy must come from outside (constructor, setter, or function arg).
2. **Creating a strategy per call instead of injecting.** If you create `StripeStrategy()` inside `checkout()`, you've just moved the `if/elif` one level deeper.
3. **Using Strategy when you only have one algorithm.** Don't add the abstraction before you need it. Start with a plain function; extract to Strategy when you have two or more real variants.

## ✅ When to Use vs When NOT to Use
**Use when:**
- You have multiple interchangeable algorithms or behaviors (sorting strategies, payment methods, notification channels, export formats)
- The algorithm used depends on user choice, config, or request data
- You want to add new behaviors without touching existing code

**Don't use when:**
- You only ever have one implementation — premature abstraction
- The variation is trivial (a boolean flag is fine) — Strategy is overkill
- Python's duck typing means you can often just pass a function instead of a class

## 🔗 Related Concepts
- [design_patterns/021_factory_pattern](../021_factory_pattern) — factory often creates the strategy
- [oop/014_abstract_base_classes](../../oop/014_abstract_base_classes) — used to define the strategy interface
- [design_patterns/024_decorator_pattern](../024_decorator_pattern) — decorator wraps; strategy swaps

## 🚀 Next Step
In `python-backend-mastery`: **Command + Strategy combined** — building a rule engine where strategies are commands, enabling undo/redo and audit logs on business logic.

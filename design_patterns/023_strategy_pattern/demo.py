"""
Demo: Strategy Pattern
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from abc import ABC, abstractmethod
from typing import Callable


# ── Section 1: Without strategy — the if/elif problem ────────────────────────

def checkout_bad(amount: float, method: str) -> str:
    """
    BAD: every new payment method requires editing this function.
    Imagine this scattered across your codebase.
    """
    if method == "stripe":
        return f"Stripe: charged ${amount:.2f}"
    elif method == "paypal":
        return f"PayPal: charged ${amount:.2f}"
    elif method == "bank":
        return f"Bank Transfer: processing ${amount:.2f}"
    else:
        raise ValueError(f"Unknown method: {method}")


# ── Section 2: Strategy pattern with ABC ─────────────────────────────────────

class PaymentStrategy(ABC):
    """The interface — every payment strategy must implement charge()."""
    @abstractmethod
    def charge(self, amount: float) -> str:
        pass


class StripeStrategy(PaymentStrategy):
    def __init__(self, api_key: str = "sk_test_..."):
        self.api_key = api_key

    def charge(self, amount: float) -> str:
        # In real life: calls stripe.PaymentIntent.create(...)
        return f"[Stripe]  Charged ${amount:.2f} (key: {self.api_key[:8]}...)"


class PayPalStrategy(PaymentStrategy):
    def __init__(self, client_id: str = "paypal_id"):
        self.client_id = client_id

    def charge(self, amount: float) -> str:
        return f"[PayPal]  Charged ${amount:.2f} (client: {self.client_id})"


class BankTransferStrategy(PaymentStrategy):
    def charge(self, amount: float) -> str:
        return f"[Bank]    Transfer of ${amount:.2f} initiated"


class OrderProcessor:
    """
    Knows HOW to process an order, but not WHICH payment system to use.
    The strategy is injected from outside.
    """
    def __init__(self, payment_strategy: PaymentStrategy):
        self._strategy = payment_strategy

    def set_strategy(self, strategy: PaymentStrategy) -> None:
        """Allow swapping strategy after creation."""
        self._strategy = strategy

    def checkout(self, amount: float) -> str:
        # No if/elif here — just delegates to the strategy
        result = self._strategy.charge(amount)
        return f"Order complete: {result}"


# ── Section 3: Strategy with plain functions (Pythonic alternative) ───────────
# In Python you can use callables instead of classes when the strategy is simple.

def apply_discount(price: float, discount_fn: Callable[[float], float]) -> float:
    """
    discount_fn IS the strategy — a plain function.
    No class needed for simple cases.
    """
    return discount_fn(price)


def ten_percent_off(price: float) -> float:
    return price * 0.90

def flat_five_off(price: float) -> float:
    return max(0, price - 5.00)

def no_discount(price: float) -> float:
    return price


# ── Section 4: Common mistake — hardcoding strategy ──────────────────────────

class BadOrderProcessor:
    def checkout(self, amount: float) -> str:
        # BAD: strategy is created inside — you can never swap it
        strategy = StripeStrategy()
        return strategy.charge(amount)


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Strategy Pattern")
    print("=" * 55)

    print("\n--- Without strategy (if/elif): works but doesn't scale ---")
    print(checkout_bad(100.0, "stripe"))
    print(checkout_bad(50.0, "paypal"))

    print("\n--- With strategy: OrderProcessor doesn't change ---")
    stripe = StripeStrategy(api_key="sk_test_abc123")
    processor = OrderProcessor(stripe)
    print(processor.checkout(99.99))

    paypal = PayPalStrategy(client_id="pp_client_xyz")
    processor.set_strategy(paypal)
    print(processor.checkout(49.00))

    bank = BankTransferStrategy()
    processor.set_strategy(bank)
    print(processor.checkout(500.00))

    print("\n--- Swapping strategy at runtime based on user choice ---")
    strategies = {
        "stripe": StripeStrategy(),
        "paypal": PayPalStrategy(),
        "bank": BankTransferStrategy(),
    }
    for user_choice in ["stripe", "bank", "paypal"]:
        proc = OrderProcessor(strategies[user_choice])
        print(f"  User chose '{user_choice}': {proc.checkout(25.00)}")

    print("\n--- Pythonic: functions as strategies ---")
    cart_price = 80.00
    for name, fn in [("10% off", ten_percent_off), ("$5 flat", flat_five_off), ("no discount", no_discount)]:
        final = apply_discount(cart_price, fn)
        print(f"  {name:15s}: ${final:.2f}")

    print("\n--- Common mistake: hardcoded strategy ---")
    bad = BadOrderProcessor()
    print(f"  Always uses Stripe: {bad.checkout(10.0)}  ← can't test with mock")

"""
Demo: Observer Pattern
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from typing import Callable


# ── Section 1: The problem without Observer ───────────────────────────────────

class OrderServiceBad:
    """
    BAD: OrderService knows about every downstream system.
    Adding SMS notifications? Edit this class. Adding audit log? Edit this class.
    """
    def place_order(self, order: dict) -> None:
        print(f"  [Order] Placed order #{order['id']}")
        # Coupled directly to every side effect:
        print(f"  [Email] Sending confirmation for #{order['id']}")
        print(f"  [Inventory] Deducting item: {order['item']}")
        print(f"  [Audit] Logging order #{order['id']}")


# ── Section 2: A simple EventBus (Observer implementation) ───────────────────

class EventBus:
    """
    Lightweight event bus. Publishers fire events; subscribers react.
    Publisher doesn't know who's subscribed.
    """
    def __init__(self):
        self._listeners: dict[str, list[Callable[[dict], None]]] = {}

    def subscribe(self, event: str, handler: Callable[[dict], None]) -> None:
        """Register a handler for an event."""
        self._listeners.setdefault(event, []).append(handler)
        print(f"  [Bus] Subscribed handler '{handler.__name__}' to '{event}'")

    def unsubscribe(self, event: str, handler: Callable[[dict], None]) -> None:
        """Remove a specific handler."""
        handlers = self._listeners.get(event, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event: str, data: dict) -> None:
        """Notify all subscribers. Errors in one don't block others."""
        handlers = self._listeners.get(event, [])
        if not handlers:
            print(f"  [Bus] No subscribers for '{event}'")
            return
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                # One bad handler doesn't kill the others
                print(f"  [Bus] Handler '{handler.__name__}' failed: {e}")


# ── Section 3: Subscriber handlers ───────────────────────────────────────────

def send_confirmation_email(event_data: dict) -> None:
    print(f"  [Email] Confirmation sent for order #{event_data['id']} to {event_data.get('email', 'user@example.com')}")


def update_inventory(event_data: dict) -> None:
    print(f"  [Inventory] Deducted '{event_data['item']}' (qty: {event_data.get('qty', 1)})")


def write_audit_log(event_data: dict) -> None:
    print(f"  [Audit] ORDER_PLACED | id={event_data['id']} | item={event_data['item']}")


def send_sms_notification(event_data: dict) -> None:
    print(f"  [SMS] Text sent: Your order #{event_data['id']} is confirmed!")


def broken_handler(event_data: dict) -> None:
    raise RuntimeError("Something went wrong in this handler")


# ── Section 4: OrderService using EventBus ───────────────────────────────────

class OrderService:
    """
    GOOD: OrderService fires events and does nothing else.
    It doesn't know about email, inventory, or audit.
    """
    def __init__(self, event_bus: EventBus):
        self._bus = event_bus

    def place_order(self, order: dict) -> None:
        print(f"  [Order] Processing order #{order['id']}...")
        # Business logic here (validate, save to DB, etc.)
        # Then fire the event — that's it.
        self._bus.publish("order_placed", order)
        print(f"  [Order] Done.")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Observer Pattern")
    print("=" * 55)

    print("\n--- Without Observer (tightly coupled) ---")
    bad_service = OrderServiceBad()
    bad_service.place_order({"id": 1, "item": "book"})

    print("\n--- Setting up EventBus ---")
    bus = EventBus()
    bus.subscribe("order_placed", send_confirmation_email)
    bus.subscribe("order_placed", update_inventory)
    bus.subscribe("order_placed", write_audit_log)

    print("\n--- OrderService fires event, subscribers react ---")
    service = OrderService(bus)
    service.place_order({"id": 42, "item": "laptop", "qty": 1, "email": "alice@example.com"})

    print("\n--- Adding SMS subscriber without touching OrderService ---")
    bus.subscribe("order_placed", send_sms_notification)
    service.place_order({"id": 43, "item": "phone", "qty": 2, "email": "bob@example.com"})

    print("\n--- One broken handler doesn't break others ---")
    bus.subscribe("order_placed", broken_handler)
    service.place_order({"id": 44, "item": "charger"})

    print("\n--- Unsubscribe: remove a handler ---")
    bus.unsubscribe("order_placed", broken_handler)
    bus.unsubscribe("order_placed", send_sms_notification)
    print("After removing broken_handler and sms:")
    service.place_order({"id": 45, "item": "cable"})

    print("\n--- No subscribers for an event ---")
    bus.publish("payment_failed", {"id": 99, "reason": "card declined"})

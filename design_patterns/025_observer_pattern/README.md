# Observer Pattern

## 🎯 Interview Question
What is the Observer pattern? Give a real backend example where you'd use it.

## 💡 Short Answer (30 seconds)
The Observer pattern (also called Pub/Sub or event system) lets objects subscribe to events and get notified automatically when something happens — without the event source knowing who's listening. A real backend example: when an order is placed, you need to send a confirmation email, update inventory, and create an audit log. With Observer, the order service fires one event and all listeners react independently.

## 🔬 Explanation
Without Observer, your `OrderService.place_order()` directly calls `email_service.send()`, `inventory_service.update()`, `audit_log.record()`. Now `OrderService` is coupled to all three. Adding a fourth notification (SMS) means editing `OrderService`.

With Observer:
- `OrderService` fires an event: `order_placed`
- `EmailListener`, `InventoryListener`, and `AuditListener` are all subscribed
- Each one reacts when notified — `OrderService` doesn't know who they are

This is the basis of Django signals, FastAPI's event hooks, and message queues like Celery tasks triggered by events.

## 💻 Code Example
```python
from typing import Callable

class EventBus:
    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def subscribe(self, event: str, handler: Callable) -> None:
        self._listeners.setdefault(event, []).append(handler)

    def publish(self, event: str, data: dict) -> None:
        for handler in self._listeners.get(event, []):
            handler(data)

bus = EventBus()

bus.subscribe("order_placed", lambda d: print(f"Email: order #{d['id']} confirmed"))
bus.subscribe("order_placed", lambda d: print(f"Inventory: deduct {d['item']}"))

bus.publish("order_placed", {"id": 42, "item": "book"})
```

## ⚠️ Common Mistakes
1. **Letting exceptions in one listener block others.** If the email handler raises, inventory never gets notified. Wrap handler calls in try/except or use a queue.
2. **Creating memory leaks via unremoved listeners.** If you subscribe an object and never unsubscribe when it's destroyed, the event bus holds a reference and the object is never garbage collected.
3. **Overusing it for simple flows.** If there's only one listener and it's always the same, a direct call is cleaner. Observer shines when the publisher truly doesn't know about its subscribers.

## ✅ When to Use vs When NOT to Use
**Use when:**
- An action triggers multiple independent side effects (order placed → email + inventory + audit)
- You want to add/remove behaviors without touching the publisher
- Building plugin systems or extensible hooks

**Don't use when:**
- There's always exactly one subscriber — it's just function-calling overhead
- Order of execution matters and is complex — direct calls are easier to reason about
- You need synchronous, guaranteed error handling between publisher and subscriber

## 🔗 Related Concepts
- [design_patterns/023_strategy_pattern](../023_strategy_pattern) — strategy swaps how; observer notifies who
- [design_patterns/028_command_pattern](../028_command_pattern) — commands can be dispatched via an event bus
- [async_python](../../async_python) — async event systems use asyncio for non-blocking notification

## 🚀 Next Step
In `python-backend-mastery`: **Event-driven architecture with message brokers** — Celery tasks triggered by domain events, Redis Pub/Sub, and how Observer scales across services.

"""
Demo: Three-Layer Architecture
Level: Intermediate (2–3 years experience)
Run:  python demo.py

Simulates a complete 3-layer flow for a "create order" feature:
  Route Layer → Service Layer → Repository Layer → (fake) Database
"""

from dataclasses import dataclass, field
from typing import Optional


# ══════════════════════════════════════════════════════
# LAYER 0: Domain objects (shared across all layers)
# ══════════════════════════════════════════════════════

@dataclass
class Product:
    id: int
    name: str
    price: float
    stock: int


@dataclass
class Order:
    id: Optional[int]
    user_id: int
    product_id: int
    quantity: int
    total: float


# ══════════════════════════════════════════════════════
# LAYER 3: Data Layer (Repository)
# Knows about storage. Knows nothing about HTTP or business rules.
# ══════════════════════════════════════════════════════

class ProductRepository:
    def __init__(self):
        # Fake in-memory "database"
        self._products = {
            1: Product(id=1, name="Laptop", price=999.99, stock=5),
            2: Product(id=2, name="Mouse",  price=29.99,  stock=50),
            3: Product(id=3, name="Monitor",price=399.99, stock=0),  # out of stock
        }

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self._products.get(product_id)

    def decrement_stock(self, product_id: int, qty: int) -> None:
        if product_id in self._products:
            self._products[product_id].stock -= qty


class OrderRepository:
    def __init__(self):
        self._orders: dict[int, Order] = {}
        self._next_id = 1

    def save(self, order: Order) -> Order:
        order.id = self._next_id
        self._orders[self._next_id] = order
        self._next_id += 1
        print(f"    [DB] Saved order #{order.id}")
        return order

    def list_by_user(self, user_id: int) -> list[Order]:
        return [o for o in self._orders.values() if o.user_id == user_id]


# ══════════════════════════════════════════════════════
# LAYER 2: Service Layer
# Knows about business rules. No HTTP, no SQL.
# ══════════════════════════════════════════════════════

class ProductNotFoundError(Exception):
    pass

class OutOfStockError(Exception):
    pass

class InvalidQuantityError(Exception):
    pass


class OrderService:
    """
    All business rules live here.
    - Product must exist
    - Must have enough stock
    - Quantity must be positive
    - Total price calculation
    """
    def __init__(self, product_repo: ProductRepository, order_repo: OrderRepository):
        self._products = product_repo
        self._orders = order_repo

    def place_order(self, user_id: int, product_id: int, quantity: int) -> Order:
        # Business rule: valid quantity
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be at least 1")

        # Business rule: product must exist
        product = self._products.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product #{product_id} not found")

        # Business rule: must have enough stock
        if product.stock < quantity:
            raise OutOfStockError(
                f"Only {product.stock} units of '{product.name}' available"
            )

        # Calculate total (business logic, not DB logic)
        total = round(product.price * quantity, 2)

        # Persist
        self._products.decrement_stock(product_id, quantity)
        order = self._orders.save(Order(
            id=None,
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total=total,
        ))
        return order

    def get_user_orders(self, user_id: int) -> list[Order]:
        return self._orders.list_by_user(user_id)


# ══════════════════════════════════════════════════════
# LAYER 1: Route Layer (Presentation)
# Knows about HTTP. Translates HTTP ↔ domain.
# ══════════════════════════════════════════════════════

@dataclass
class PlaceOrderRequest:
    """What the HTTP client sends (like a Pydantic model)."""
    user_id: int
    product_id: int
    quantity: int


@dataclass
class OrderResponse:
    """What we send back to the HTTP client."""
    order_id: int
    total: float
    message: str

    @classmethod
    def from_domain(cls, order: Order) -> "OrderResponse":
        return cls(
            order_id=order.id,
            total=order.total,
            message=f"Order #{order.id} placed successfully",
        )


def post_order(request: PlaceOrderRequest, service: OrderService) -> tuple[dict, int]:
    """
    Route handler: speaks HTTP (status codes, response dicts).
    Delegates ALL business logic to the service.
    Only knows how to convert domain errors → HTTP errors.
    """
    try:
        order = service.place_order(request.user_id, request.product_id, request.quantity)
        response = OrderResponse.from_domain(order)
        return {"order_id": response.order_id, "total": response.total, "message": response.message}, 201

    except InvalidQuantityError as e:
        return {"error": str(e)}, 400
    except ProductNotFoundError as e:
        return {"error": str(e)}, 404
    except OutOfStockError as e:
        return {"error": str(e)}, 409


def get_user_orders(user_id: int, service: OrderService) -> tuple[dict, int]:
    orders = service.get_user_orders(user_id)
    return {"orders": [{"id": o.id, "product_id": o.product_id, "total": o.total} for o in orders]}, 200


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Three-Layer Architecture")
    print("=" * 55)

    # Wire up the layers (in FastAPI this is done with Depends())
    product_repo = ProductRepository()
    order_repo = OrderRepository()
    service = OrderService(product_repo, order_repo)

    print("\n--- Layer flow: Route → Service → Repository ---")
    print("  Each layer only calls the one below it.\n")

    print("  [Route] POST /orders {user_id:1, product_id:1, quantity:2}")
    resp, status = post_order(PlaceOrderRequest(user_id=1, product_id=1, quantity=2), service)
    print(f"  [Route] → {status}: {resp}\n")

    print("  [Route] POST /orders {user_id:1, product_id:2, quantity:5}")
    resp, status = post_order(PlaceOrderRequest(user_id=1, product_id=2, quantity=5), service)
    print(f"  [Route] → {status}: {resp}\n")

    print("--- Business rules enforced by service layer ---")

    print("  Out of stock (Monitor has 0 units):")
    resp, status = post_order(PlaceOrderRequest(user_id=2, product_id=3, quantity=1), service)
    print(f"  → {status}: {resp}")

    print("  Product not found:")
    resp, status = post_order(PlaceOrderRequest(user_id=2, product_id=99, quantity=1), service)
    print(f"  → {status}: {resp}")

    print("  Invalid quantity:")
    resp, status = post_order(PlaceOrderRequest(user_id=2, product_id=2, quantity=-1), service)
    print(f"  → {status}: {resp}")

    print("\n--- GET /users/1/orders ---")
    resp, status = get_user_orders(user_id=1, service=service)
    print(f"  → {status}: {resp}")

    print("\n--- Layer summary ---")
    print("  Route  layer: handles HTTP, parses requests, formats responses")
    print("  Service layer: validates rules, calculates totals, orchestrates")
    print("  Repo   layer: reads and writes to the database")
    print("  Each layer is replaceable independently.")

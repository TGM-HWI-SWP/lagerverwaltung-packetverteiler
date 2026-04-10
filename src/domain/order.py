"""Order Domain Model (Bestellung)"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    """Einzelnes Item in einer Bestellung"""

    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total_price: float = field(init=False)

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity muss positiv sein")
        if self.unit_price < 0:
            raise ValueError("Unit price kann nicht negativ sein")
        self.total_price = self.quantity * self.unit_price


@dataclass
class Order:
    """
    Bestellung von Produkten
    """

    id: str
    customer_id: str
    supplier_id: Optional[str] = None  # Für Einkaufsbestellungen bei Lieferanten
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    order_date: datetime = field(default_factory=datetime.now)
    delivery_date: Optional[datetime] = None
    total_amount: float = field(init=False)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            raise ValueError("Order ID kann nicht leer sein")
        if not self.customer_id:
            raise ValueError("Customer ID kann nicht leer sein")
        self._calculate_total()

    def _calculate_total(self) -> None:
        self.total_amount = sum(item.total_price for item in self.items)

    def add_item(self, product_id: str, product_name: str, quantity: int, unit_price: float) -> None:
        item = OrderItem(product_id, product_name, quantity, unit_price)
        self.items.append(item)
        self._calculate_total()
        self.updated_at = datetime.now()

    def update_status(self, status: OrderStatus) -> None:
        self.status = status
        self.updated_at = datetime.now()

    def set_delivery_date(self, delivery_date: datetime) -> None:
        self.delivery_date = delivery_date
        self.updated_at = datetime.now()
"""Warehouse Domain Model (Verteilzentrum)"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

from .product import Product


@dataclass
class Movement:
    """Paketbewegung"""

    id: str
    product_id: str
    product_name: str
    quantity_change: int
    movement_type: str
    reason: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    performed_by: str = "system"


class Warehouse:
    """Verteilzentrum"""

    def __init__(self, name: str):
        self.name = name
        self.products: Dict[str, Product] = {}
        self.movements: list[Movement] = []

    def add_product(self, product: Product) -> None:
        if product.id in self.products:
            raise ValueError("Produkt existiert bereits")

        self.products[product.id] = product

    def get_product(self, product_id: str) -> Optional[Product]:
        return self.products.get(product_id)

    def record_movement(self, movement: Movement) -> None:
        if movement.product_id not in self.products:
            raise ValueError("Produkt existiert nicht")

        self.movements.append(movement)

    def get_total_inventory_value(self) -> float:
        return sum(p.get_total_value() for p in self.products.values())
"""Product Domain Model (repräsentiert ein Paket)"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    """
    Produkt = Paket im Paketverteilungssystem
    """

    id: str
    name: str
    description: str
    price: float
    quantity: int = 1
    sku: str = ""
    category: str = "Paket"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            raise ValueError("Product ID kann nicht leer sein")

        if self.price < 0:
            raise ValueError("Preis kann nicht negativ sein")

        if self.quantity < 0:
            raise ValueError("Bestand kann nicht negativ sein")

    def update_quantity(self, amount: int) -> None:
        new_quantity = self.quantity + amount

        if new_quantity < 0:
            raise ValueError("Bestand kann nicht negativ werden")

        self.quantity = new_quantity
        self.updated_at = datetime.now()

    def get_total_value(self) -> float:
        return self.price * self.quantity
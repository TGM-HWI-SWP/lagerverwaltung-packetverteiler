"""Supplier Domain Model (Lieferant)"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Supplier:
    """
    Lieferant für Produkte
    """

    id: str
    name: str
    contact_email: str
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            raise ValueError("Supplier ID kann nicht leer sein")

        if not self.name:
            raise ValueError("Supplier Name kann nicht leer sein")

        if not self.contact_email:
            raise ValueError("Contact Email kann nicht leer sein")

    def update_contact(self, email: str = None, phone: str = None, address: str = None) -> None:
        if email:
            self.contact_email = email
        if phone:
            self.contact_phone = phone
        if address:
            self.address = address
        self.updated_at = datetime.now()
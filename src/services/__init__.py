"""Services - Business Logic Layer"""

from datetime import datetime
from typing import Dict, List, Optional

from ..domain.product import Product
from ..domain.warehouse import Movement, Warehouse
from ..domain.supplier import Supplier
from ..domain.customer import Customer
from ..domain.order import Order, OrderStatus, OrderItem
from ..ports import RepositoryPort


class WarehouseService:
    """Service für Lagerverwaltung"""

    def __init__(self, repository: RepositoryPort):
        self.repository = repository
        self.warehouse = Warehouse("Hauptlager")

    def create_product(
        self,
        product_id: str,
        name: str,
        description: str,
        price: float,
        category: str = "",
        initial_quantity: int = 0,
    ) -> Product:
        """Neues Produkt erstellen und speichern"""
        product = Product(
            id=product_id,
            name=name,
            description=description,
            price=price,
            quantity=initial_quantity,
            category=category,
        )
        self.repository.save_product(product)
        self.warehouse.add_product(product)
        return product

    def add_to_stock(
        self, product_id: str, quantity: int, reason: str = "", user: str = "system"
    ) -> None:
        """Bestand erhöhen"""
        product = self.repository.load_product(product_id)
        if not product:
            raise ValueError(f"Produkt {product_id} nicht gefunden")

        product.update_quantity(quantity)
        self.repository.save_product(product)

        movement = Movement(
            id=f"mov_{datetime.now().timestamp()}",
            product_id=product_id,
            product_name=product.name,
            quantity_change=quantity,
            movement_type="IN",
            reason=reason,
            performed_by=user,
        )
        self.repository.save_movement(movement)

    def remove_from_stock(
        self, product_id: str, quantity: int, reason: str = "", user: str = "system"
    ) -> None:
        """Bestand verringern"""
        product = self.repository.load_product(product_id)
        if not product:
            raise ValueError(f"Produkt {product_id} nicht gefunden")

        if product.quantity < quantity:
            raise ValueError(
                f"Unzureichender Bestand. Verfügbar: {product.quantity}, Angefordert: {quantity}"
            )

        product.update_quantity(-quantity)
        self.repository.save_product(product)

        movement = Movement(
            id=f"mov_{datetime.now().timestamp()}",
            product_id=product_id,
            product_name=product.name,
            quantity_change=-quantity,
            movement_type="OUT",
            reason=reason,
            performed_by=user,
        )
        self.repository.save_movement(movement)

    def get_product(self, product_id: str) -> Optional[Product]:
        """Produkt abrufen"""
        return self.repository.load_product(product_id)

    def delete_product(self, product_id: str) -> None:
        """Produkt löschen"""
        product = self.get_product(product_id)
        if not product:
            raise ValueError(f"Produkt {product_id} nicht gefunden")
        self.repository.delete_product(product_id)

    def get_all_products(self) -> Dict[str, Product]:
        """Alle Produkte abrufen"""
        return self.repository.load_all_products()

    def get_movements(self) -> List[Movement]:
        """Alle Lagerbewegungen abrufen"""
        return self.repository.load_movements()

    def get_total_inventory_value(self) -> float:
        """Gesamtwert des Lagerbestands berechnen"""
        products = self.repository.load_all_products()
        return sum(p.get_total_value() for p in products.values())

    # Supplier Management
    def create_supplier(
        self,
        supplier_id: str,
        name: str,
        contact_email: str,
        contact_phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Supplier:
        """Neuen Lieferanten erstellen"""
        supplier = Supplier(
            id=supplier_id,
            name=name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            address=address,
        )
        self.repository.save_supplier(supplier)
        return supplier

    def get_supplier(self, supplier_id: str) -> Optional[Supplier]:
        """Lieferant abrufen"""
        return self.repository.load_supplier(supplier_id)

    def get_all_suppliers(self) -> Dict[str, Supplier]:
        """Alle Lieferanten abrufen"""
        return self.repository.load_all_suppliers()

    def delete_supplier(self, supplier_id: str) -> None:
        """Lieferant löschen"""
        supplier = self.get_supplier(supplier_id)
        if not supplier:
            raise ValueError(f"Lieferant {supplier_id} nicht gefunden")
        self.repository.delete_supplier(supplier_id)

    # Customer Management
    def create_customer(
        self,
        customer_id: str,
        name: str,
        contact_email: str,
        contact_phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Customer:
        """Neuen Kunden erstellen"""
        customer = Customer(
            id=customer_id,
            name=name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            address=address,
        )
        self.repository.save_customer(customer)
        return customer

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Kunde abrufen"""
        return self.repository.load_customer(customer_id)

    def get_all_customers(self) -> Dict[str, Customer]:
        """Alle Kunden abrufen"""
        return self.repository.load_all_customers()

    def delete_customer(self, customer_id: str) -> None:
        """Kunde löschen"""
        customer = self.get_customer(customer_id)
        if not customer:
            raise ValueError(f"Kunde {customer_id} nicht gefunden")
        self.repository.delete_customer(customer_id)

    # Order Management
    def create_order(
        self,
        order_id: str,
        customer_id: str,
        supplier_id: Optional[str] = None,
    ) -> Order:
        """Neue Bestellung erstellen"""
        customer = self.get_customer(customer_id)
        if not customer:
            raise ValueError(f"Kunde {customer_id} nicht gefunden")

        if supplier_id:
            supplier = self.get_supplier(supplier_id)
            if not supplier:
                raise ValueError(f"Lieferant {supplier_id} nicht gefunden")

        order = Order(
            id=order_id,
            customer_id=customer_id,
            supplier_id=supplier_id,
        )
        self.repository.save_order(order)
        return order

    def add_item_to_order(
        self,
        order_id: str,
        product_id: str,
        quantity: int,
        unit_price: Optional[float] = None,
    ) -> None:
        """Artikel zu Bestellung hinzufügen"""
        order = self.repository.load_order(order_id)
        if not order:
            raise ValueError(f"Bestellung {order_id} nicht gefunden")

        product = self.get_product(product_id)
        if not product:
            raise ValueError(f"Produkt {product_id} nicht gefunden")

        if unit_price is None:
            unit_price = product.price

        order.add_item(product_id, product.name, quantity, unit_price)
        self.repository.save_order(order)

    def update_order_status(self, order_id: str, status: OrderStatus) -> None:
        """Bestellstatus aktualisieren"""
        order = self.repository.load_order(order_id)
        if not order:
            raise ValueError(f"Bestellung {order_id} nicht gefunden")

        order.update_status(status)
        self.repository.save_order(order)

        # Wenn Bestellung geliefert wird, Bestand aktualisieren
        if status == OrderStatus.DELIVERED:
            for item in order.items:
                if order.supplier_id:  # Einkaufsbestellung - Bestand erhöhen
                    self.add_to_stock(item.product_id, item.quantity, f"Bestellung {order_id}", "system")
                else:  # Verkaufsbestellung - Bestand verringern
                    self.remove_from_stock(item.product_id, item.quantity, f"Bestellung {order_id}", "system")

    def get_order(self, order_id: str) -> Optional[Order]:
        """Bestellung abrufen"""
        return self.repository.load_order(order_id)

    def get_all_orders(self) -> Dict[str, Order]:
        """Alle Bestellungen abrufen"""
        return self.repository.load_all_orders()

    def delete_order(self, order_id: str) -> None:
        """Bestellung löschen"""
        order = self.get_order(order_id)
        if not order:
            raise ValueError(f"Bestellung {order_id} nicht gefunden")
        self.repository.delete_order(order_id)

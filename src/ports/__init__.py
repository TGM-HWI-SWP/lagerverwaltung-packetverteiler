"""Ports - Schnittstellen für externe Abhängigkeiten (Abstraktion)"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ..domain.product import Product
from ..domain.warehouse import Movement
from ..domain.supplier import Supplier
from ..domain.customer import Customer
from ..domain.order import Order


class RepositoryPort(ABC):
    """Port für Datenpersistenz"""

    @abstractmethod
    def save_product(self, product: Product) -> None:
        """Produkt speichern"""
        pass

    @abstractmethod
    def load_product(self, product_id: str) -> Optional[Product]:
        """Produkt laden"""
        pass

    @abstractmethod
    def load_all_products(self) -> Dict[str, Product]:
        """Alle Produkte laden"""
        pass

    @abstractmethod
    def delete_product(self, product_id: str) -> None:
        """Produkt löschen"""
        pass

    @abstractmethod
    def save_movement(self, movement: Movement) -> None:
        """Lagerbewegung speichern"""
        pass

    @abstractmethod
    def load_movements(self) -> List[Movement]:
        """Alle Lagerbewegungen laden"""
        pass

    @abstractmethod
    def save_supplier(self, supplier: Supplier) -> None:
        """Lieferant speichern"""
        pass

    @abstractmethod
    def load_supplier(self, supplier_id: str) -> Optional[Supplier]:
        """Lieferant laden"""
        pass

    @abstractmethod
    def load_all_suppliers(self) -> Dict[str, Supplier]:
        """Alle Lieferanten laden"""
        pass

    @abstractmethod
    def delete_supplier(self, supplier_id: str) -> None:
        """Lieferant löschen"""
        pass

    @abstractmethod
    def save_customer(self, customer: Customer) -> None:
        """Kunde speichern"""
        pass

    @abstractmethod
    def load_customer(self, customer_id: str) -> Optional[Customer]:
        """Kunde laden"""
        pass

    @abstractmethod
    def load_all_customers(self) -> Dict[str, Customer]:
        """Alle Kunden laden"""
        pass

    @abstractmethod
    def delete_customer(self, customer_id: str) -> None:
        """Kunde löschen"""
        pass

    @abstractmethod
    def save_order(self, order: Order) -> None:
        """Bestellung speichern"""
        pass

    @abstractmethod
    def load_order(self, order_id: str) -> Optional[Order]:
        """Bestellung laden"""
        pass

    @abstractmethod
    def load_all_orders(self) -> Dict[str, Order]:
        """Alle Bestellungen laden"""
        pass

    @abstractmethod
    def delete_order(self, order_id: str) -> None:
        """Bestellung löschen"""
        pass


class ReportPort(ABC):
    """Port für Report-Generierung"""

    @abstractmethod
    def generate_inventory_report(self) -> str:
        """Lagerbestandsbericht generieren"""
        pass

    @abstractmethod
    def generate_movement_report(self) -> str:
        """Lagerbewegungsbericht generieren"""
        pass

    @abstractmethod
    def generate_movement_report(self) -> str:
        """Bewegungsprotokoll generieren"""
        pass

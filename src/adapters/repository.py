"""Repository Adapter"""

from typing import Dict, List, Optional

from ..domain.product import Product
from ..domain.warehouse import Movement
from ..domain.supplier import Supplier
from ..domain.customer import Customer
from ..domain.order import Order
from ..ports import RepositoryPort


class InMemoryRepository(RepositoryPort):

    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.movements: List[Movement] = []
        self.suppliers: Dict[str, Supplier] = {}
        self.customers: Dict[str, Customer] = {}
        self.orders: Dict[str, Order] = {}

    def save_product(self, product: Product) -> None:
        self.products[product.id] = product

    def load_product(self, product_id: str) -> Optional[Product]:
        return self.products.get(product_id)

    def load_all_products(self) -> Dict[str, Product]:
        return self.products.copy()

    def delete_product(self, product_id: str) -> None:
        if product_id in self.products:
            del self.products[product_id]

    def save_movement(self, movement: Movement) -> None:
        self.movements.append(movement)

    def load_movements(self) -> List[Movement]:
        return self.movements.copy()

    def save_supplier(self, supplier: Supplier) -> None:
        self.suppliers[supplier.id] = supplier

    def load_supplier(self, supplier_id: str) -> Optional[Supplier]:
        return self.suppliers.get(supplier_id)

    def load_all_suppliers(self) -> Dict[str, Supplier]:
        return self.suppliers.copy()

    def delete_supplier(self, supplier_id: str) -> None:
        if supplier_id in self.suppliers:
            del self.suppliers[supplier_id]

    def save_customer(self, customer: Customer) -> None:
        self.customers[customer.id] = customer

    def load_customer(self, customer_id: str) -> Optional[Customer]:
        return self.customers.get(customer_id)

    def load_all_customers(self) -> Dict[str, Customer]:
        return self.customers.copy()

    def delete_customer(self, customer_id: str) -> None:
        if customer_id in self.customers:
            del self.customers[customer_id]

    def save_order(self, order: Order) -> None:
        self.orders[order.id] = order

    def load_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)

    def load_all_orders(self) -> Dict[str, Order]:
        return self.orders.copy()

    def delete_order(self, order_id: str) -> None:
        if order_id in self.orders:
            del self.orders[order_id]


class RepositoryFactory:

    @staticmethod
    def create_repository(repository_type: str = "memory"):

        if repository_type == "memory":
            return InMemoryRepository()

        raise ValueError("Unbekannter Repository Typ")
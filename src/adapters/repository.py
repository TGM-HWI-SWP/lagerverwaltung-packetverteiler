"""Repository Adapter"""

from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional

from ..domain.product import Product
from ..domain.warehouse import Movement
from ..domain.supplier import Supplier
from ..domain.customer import Customer
from ..domain.order import Order, OrderItem, OrderStatus
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


class JsonFileRepository(RepositoryPort):

    def __init__(self, file_path: str = "data/warehouse_data.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        self.products: Dict[str, Product] = {}
        self.movements: List[Movement] = []
        self.suppliers: Dict[str, Supplier] = {}
        self.customers: Dict[str, Customer] = {}
        self.orders: Dict[str, Order] = {}

        self._load_from_disk()

    def _dt_to_iso(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    def _iso_to_dt(self, value: Optional[str]) -> Optional[datetime]:
        if value is None:
            return None
        return datetime.fromisoformat(value)

    def _serialize_order(self, order: Order) -> Dict:
        payload = asdict(order)
        payload["status"] = order.status.value
        payload["order_date"] = self._dt_to_iso(order.order_date)
        payload["delivery_date"] = self._dt_to_iso(order.delivery_date)
        payload["created_at"] = self._dt_to_iso(order.created_at)
        payload["updated_at"] = self._dt_to_iso(order.updated_at)
        return payload

    def _serialize_state(self) -> Dict:
        return {
            "products": {
                pid: {
                    **asdict(product),
                    "created_at": self._dt_to_iso(product.created_at),
                    "updated_at": self._dt_to_iso(product.updated_at),
                }
                for pid, product in self.products.items()
            },
            "movements": [
                {
                    **asdict(movement),
                    "timestamp": self._dt_to_iso(movement.timestamp),
                }
                for movement in self.movements
            ],
            "suppliers": {
                sid: {
                    **asdict(supplier),
                    "created_at": self._dt_to_iso(supplier.created_at),
                    "updated_at": self._dt_to_iso(supplier.updated_at),
                }
                for sid, supplier in self.suppliers.items()
            },
            "customers": {
                cid: {
                    **asdict(customer),
                    "created_at": self._dt_to_iso(customer.created_at),
                    "updated_at": self._dt_to_iso(customer.updated_at),
                }
                for cid, customer in self.customers.items()
            },
            "orders": {
                oid: self._serialize_order(order)
                for oid, order in self.orders.items()
            },
        }

    def _persist(self) -> None:
        with self.file_path.open("w", encoding="utf-8") as handle:
            json.dump(self._serialize_state(), handle, ensure_ascii=False, indent=2)

    def _load_from_disk(self) -> None:
        if not self.file_path.exists():
            self._persist()
            return

        with self.file_path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)

        self.products = {
            pid: Product(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                price=data["price"],
                quantity=data["quantity"],
                sku=data.get("sku", ""),
                category=data.get("category", "Paket"),
                created_at=self._iso_to_dt(data.get("created_at")) or datetime.now(),
                updated_at=self._iso_to_dt(data.get("updated_at")) or datetime.now(),
                notes=data.get("notes"),
            )
            for pid, data in raw.get("products", {}).items()
        }

        self.movements = [
            Movement(
                id=data["id"],
                product_id=data["product_id"],
                product_name=data["product_name"],
                quantity_change=data["quantity_change"],
                movement_type=data["movement_type"],
                reason=data.get("reason"),
                timestamp=self._iso_to_dt(data.get("timestamp")) or datetime.now(),
                performed_by=data.get("performed_by", "system"),
            )
            for data in raw.get("movements", [])
        ]

        self.suppliers = {
            sid: Supplier(
                id=data["id"],
                name=data["name"],
                contact_email=data["contact_email"],
                contact_phone=data.get("contact_phone"),
                address=data.get("address"),
                created_at=self._iso_to_dt(data.get("created_at")) or datetime.now(),
                updated_at=self._iso_to_dt(data.get("updated_at")) or datetime.now(),
                notes=data.get("notes"),
            )
            for sid, data in raw.get("suppliers", {}).items()
        }

        self.customers = {
            cid: Customer(
                id=data["id"],
                name=data["name"],
                contact_email=data["contact_email"],
                contact_phone=data.get("contact_phone"),
                address=data.get("address"),
                created_at=self._iso_to_dt(data.get("created_at")) or datetime.now(),
                updated_at=self._iso_to_dt(data.get("updated_at")) or datetime.now(),
                notes=data.get("notes"),
            )
            for cid, data in raw.get("customers", {}).items()
        }

        self.orders = {
            oid: Order(
                id=data["id"],
                customer_id=data["customer_id"],
                supplier_id=data.get("supplier_id"),
                items=[OrderItem(**item) for item in data.get("items", [])],
                status=OrderStatus(data.get("status", "pending")),
                order_date=self._iso_to_dt(data.get("order_date")) or datetime.now(),
                delivery_date=self._iso_to_dt(data.get("delivery_date")),
                created_at=self._iso_to_dt(data.get("created_at")) or datetime.now(),
                updated_at=self._iso_to_dt(data.get("updated_at")) or datetime.now(),
                notes=data.get("notes"),
            )
            for oid, data in raw.get("orders", {}).items()
        }

    def save_product(self, product: Product) -> None:
        self.products[product.id] = product
        self._persist()

    def load_product(self, product_id: str) -> Optional[Product]:
        return self.products.get(product_id)

    def load_all_products(self) -> Dict[str, Product]:
        return self.products.copy()

    def delete_product(self, product_id: str) -> None:
        if product_id in self.products:
            del self.products[product_id]
            self._persist()

    def save_movement(self, movement: Movement) -> None:
        self.movements.append(movement)
        self._persist()

    def load_movements(self) -> List[Movement]:
        return self.movements.copy()

    def save_supplier(self, supplier: Supplier) -> None:
        self.suppliers[supplier.id] = supplier
        self._persist()

    def load_supplier(self, supplier_id: str) -> Optional[Supplier]:
        return self.suppliers.get(supplier_id)

    def load_all_suppliers(self) -> Dict[str, Supplier]:
        return self.suppliers.copy()

    def delete_supplier(self, supplier_id: str) -> None:
        if supplier_id in self.suppliers:
            del self.suppliers[supplier_id]
            self._persist()

    def save_customer(self, customer: Customer) -> None:
        self.customers[customer.id] = customer
        self._persist()

    def load_customer(self, customer_id: str) -> Optional[Customer]:
        return self.customers.get(customer_id)

    def load_all_customers(self) -> Dict[str, Customer]:
        return self.customers.copy()

    def delete_customer(self, customer_id: str) -> None:
        if customer_id in self.customers:
            del self.customers[customer_id]
            self._persist()

    def save_order(self, order: Order) -> None:
        self.orders[order.id] = order
        self._persist()

    def load_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)

    def load_all_orders(self) -> Dict[str, Order]:
        return self.orders.copy()

    def delete_order(self, order_id: str) -> None:
        if order_id in self.orders:
            del self.orders[order_id]
            self._persist()


class RepositoryFactory:

    @staticmethod
    def create_repository(repository_type: str = "memory", **kwargs):

        if repository_type == "memory":
            return InMemoryRepository()

        if repository_type == "json":
            return JsonFileRepository(file_path=kwargs.get("file_path", "data/warehouse_data.json"))

        raise ValueError("Unbekannter Repository Typ")
"""Repository Adapter - In-Memory, JSON, und SQLite Persistierung"""

from dataclasses import asdict
from datetime import datetime
import json
import sqlite3
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


class SqliteRepository(RepositoryPort):
    """SQLite-Persistierungs-Adapter für Datenbankoperationen"""

    def __init__(self, db_path: str = "data/warehouse.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _get_connection(self):
        """Erstelle eine Datenbankverbindung"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_database(self) -> None:
        """Erstelle Datenbanktabellen beim ersten Start"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Produkt-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                sku TEXT,
                category TEXT,
                created_at TEXT,
                updated_at TEXT,
                notes TEXT
            )
        """)

        # Lagerbewegung-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movements (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity_change INTEGER NOT NULL,
                movement_type TEXT NOT NULL,
                reason TEXT,
                timestamp TEXT,
                performed_by TEXT,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)

        # Lieferanten-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                contact_email TEXT NOT NULL,
                contact_phone TEXT,
                address TEXT,
                created_at TEXT,
                updated_at TEXT,
                notes TEXT
            )
        """)

        # Kunden-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                contact_email TEXT NOT NULL,
                contact_phone TEXT,
                address TEXT,
                created_at TEXT,
                updated_at TEXT,
                notes TEXT
            )
        """)

        # Bestellungen-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                supplier_id TEXT,
                status TEXT,
                order_date TEXT,
                delivery_date TEXT,
                total_amount REAL,
                created_at TEXT,
                updated_at TEXT,
                notes TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        """)

        # Bestellungs-Items-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)

        conn.commit()
        conn.close()

    # ===== PRODUKT METHODEN =====

    def save_product(self, product: Product) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO products 
            (id, name, description, price, quantity, sku, category, created_at, updated_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product.id, product.name, product.description, product.price, product.quantity,
            product.sku, product.category, product.created_at.isoformat(),
            product.updated_at.isoformat(), product.notes
        ))
        conn.commit()
        conn.close()

    def load_product(self, product_id: str) -> Optional[Product]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return Product(
            id=row["id"], name=row["name"], description=row["description"],
            price=row["price"], quantity=row["quantity"], sku=row["sku"],
            category=row["category"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            notes=row["notes"]
        )

    def load_all_products(self) -> Dict[str, Product]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        conn.close()

        products = {}
        for row in rows:
            product = Product(
                id=row["id"], name=row["name"], description=row["description"],
                price=row["price"], quantity=row["quantity"], sku=row["sku"],
                category=row["category"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                notes=row["notes"]
            )
            products[product.id] = product

        return products

    def delete_product(self, product_id: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()

    # ===== BEWEGUNG METHODEN =====

    def save_movement(self, movement: Movement) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO movements 
            (id, product_id, product_name, quantity_change, movement_type, reason, timestamp, performed_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            movement.id, movement.product_id, movement.product_name, movement.quantity_change,
            movement.movement_type, movement.reason, movement.timestamp.isoformat(),
            movement.performed_by
        ))
        conn.commit()
        conn.close()

    def load_movements(self) -> List[Movement]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movements ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()

        movements = []
        for row in rows:
            movement = Movement(
                id=row["id"], product_id=row["product_id"], product_name=row["product_name"],
                quantity_change=row["quantity_change"], movement_type=row["movement_type"],
                reason=row["reason"], timestamp=datetime.fromisoformat(row["timestamp"]),
                performed_by=row["performed_by"]
            )
            movements.append(movement)

        return movements

    # ===== LIEFERANT METHODEN =====

    def save_supplier(self, supplier: Supplier) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO suppliers 
            (id, name, contact_email, contact_phone, address, created_at, updated_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            supplier.id, supplier.name, supplier.contact_email, supplier.contact_phone,
            supplier.address, supplier.created_at.isoformat(),
            supplier.updated_at.isoformat(), supplier.notes
        ))
        conn.commit()
        conn.close()

    def load_supplier(self, supplier_id: str) -> Optional[Supplier]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return Supplier(
            id=row["id"], name=row["name"], contact_email=row["contact_email"],
            contact_phone=row["contact_phone"], address=row["address"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            notes=row["notes"]
        )

    def load_all_suppliers(self) -> Dict[str, Supplier]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers")
        rows = cursor.fetchall()
        conn.close()

        suppliers = {}
        for row in rows:
            supplier = Supplier(
                id=row["id"], name=row["name"], contact_email=row["contact_email"],
                contact_phone=row["contact_phone"], address=row["address"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                notes=row["notes"]
            )
            suppliers[supplier.id] = supplier

        return suppliers

    def delete_supplier(self, supplier_id: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
        conn.commit()
        conn.close()

    # ===== KUNDEN METHODEN =====

    def save_customer(self, customer: Customer) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO customers 
            (id, name, contact_email, contact_phone, address, created_at, updated_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer.id, customer.name, customer.contact_email, customer.contact_phone,
            customer.address, customer.created_at.isoformat(),
            customer.updated_at.isoformat(), customer.notes
        ))
        conn.commit()
        conn.close()

    def load_customer(self, customer_id: str) -> Optional[Customer]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return Customer(
            id=row["id"], name=row["name"], contact_email=row["contact_email"],
            contact_phone=row["contact_phone"], address=row["address"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            notes=row["notes"]
        )

    def load_all_customers(self) -> Dict[str, Customer]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers")
        rows = cursor.fetchall()
        conn.close()

        customers = {}
        for row in rows:
            customer = Customer(
                id=row["id"], name=row["name"], contact_email=row["contact_email"],
                contact_phone=row["contact_phone"], address=row["address"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                notes=row["notes"]
            )
            customers[customer.id] = customer

        return customers

    def delete_customer(self, customer_id: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        conn.close()

    # ===== BESTELLUNGEN METHODEN =====

    def save_order(self, order: Order) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO orders 
            (id, customer_id, supplier_id, status, order_date, delivery_date, total_amount, created_at, updated_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order.id, order.customer_id, order.supplier_id, order.status.value,
            order.order_date.isoformat(),
            order.delivery_date.isoformat() if order.delivery_date else None,
            order.total_amount, order.created_at.isoformat(),
            order.updated_at.isoformat(), order.notes
        ))

        # Lösche alte Items
        cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order.id,))

        # Speichere neue Items
        for item in order.items:
            cursor.execute("""
                INSERT INTO order_items 
                (order_id, product_id, product_name, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                order.id, item.product_id, item.product_name, item.quantity,
                item.unit_price, item.total_price
            ))

        conn.commit()
        conn.close()

    def load_order(self, order_id: str) -> Optional[Order]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        # Lade Order Items
        cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
        items_rows = cursor.fetchall()
        conn.close()

        items = [
            OrderItem(
                product_id=item_row["product_id"],
                product_name=item_row["product_name"],
                quantity=item_row["quantity"],
                unit_price=item_row["unit_price"]
            )
            for item_row in items_rows
        ]

        order = Order(
            id=row["id"], customer_id=row["customer_id"], supplier_id=row["supplier_id"],
            items=items, status=OrderStatus(row["status"]),
            order_date=datetime.fromisoformat(row["order_date"]),
            delivery_date=datetime.fromisoformat(row["delivery_date"]) if row["delivery_date"] else None,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            notes=row["notes"]
        )
        return order

    def load_all_orders(self) -> Dict[str, Order]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders")
        rows = cursor.fetchall()

        orders = {}
        for row in rows:
            # Lade Items für diese Order
            cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (row["id"],))
            items_rows = cursor.fetchall()

            items = [
                OrderItem(
                    product_id=item_row["product_id"],
                    product_name=item_row["product_name"],
                    quantity=item_row["quantity"],
                    unit_price=item_row["unit_price"]
                )
                for item_row in items_rows
            ]

            order = Order(
                id=row["id"], customer_id=row["customer_id"], supplier_id=row["supplier_id"],
                items=items, status=OrderStatus(row["status"]),
                order_date=datetime.fromisoformat(row["order_date"]),
                delivery_date=datetime.fromisoformat(row["delivery_date"]) if row["delivery_date"] else None,
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                notes=row["notes"]
            )
            orders[order.id] = order

        conn.close()
        return orders

    def delete_order(self, order_id: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()


class RepositoryFactory:
    """Factory Pattern für Repository-Erstellung"""

    @staticmethod
    def create_repository(repository_type: str = "memory", **kwargs) -> RepositoryPort:
        """
        Erstelle ein Repository basierend auf Typ.
        
        Args:
            repository_type: "memory", "json", oder "sqlite"
            **kwargs: Zusätzliche Parameter (z.B. file_path für JSON/SQLite)
        
        Returns:
            RepositoryPort-Implementierung
        
        Raises:
            ValueError: Falls repository_type unbekannt ist
        """
        if repository_type == "memory":
            return InMemoryRepository()

        if repository_type == "json":
            return JsonFileRepository(
                file_path=kwargs.get("file_path", "data/warehouse_data.json")
            )

        if repository_type == "sqlite":
            return SqliteRepository(
                db_path=kwargs.get("db_path", "data/warehouse.db")
            )

        raise ValueError(
            f"Unbekannter Repository-Typ '{repository_type}'. "
            "Unterstützt: 'memory', 'json', 'sqlite'"
        )
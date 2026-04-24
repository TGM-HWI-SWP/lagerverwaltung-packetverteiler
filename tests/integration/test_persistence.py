"""Tests für Persistierungs-Adapter (JSON und SQLite)"""

import pytest
import tempfile
import json
from pathlib import Path

from src.adapters.repository import (
    InMemoryRepository,
    JsonFileRepository,
    SqliteRepository,
    RepositoryFactory,
)
from src.domain.product import Product
from src.domain.warehouse import Movement
from src.domain.supplier import Supplier
from src.domain.customer import Customer
from src.domain.order import Order, OrderItem, OrderStatus
from datetime import datetime


class TestRepositoryFactory:
    """Test RepositoryFactory für alle Adapter"""

    def test_factory_creates_memory_repository(self):
        """Test: Factory erstellt InMemoryRepository"""
        repo = RepositoryFactory.create_repository("memory")
        assert isinstance(repo, InMemoryRepository)

    def test_factory_creates_json_repository(self):
        """Test: Factory erstellt JsonFileRepository"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = str(Path(tmpdir) / "test.json")
            repo = RepositoryFactory.create_repository("json", file_path=file_path)
            assert isinstance(repo, JsonFileRepository)

    def test_factory_creates_sqlite_repository(self):
        """Test: Factory erstellt SqliteRepository"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "test.db")
            repo = RepositoryFactory.create_repository("sqlite", db_path=db_path)
            assert isinstance(repo, SqliteRepository)

    def test_factory_raises_on_unknown_type(self):
        """Test: Factory wirft ValueError bei unbekanntem Typ"""
        with pytest.raises(ValueError):
            RepositoryFactory.create_repository("unknown_type")


class TestJsonRepository:
    """Test JsonFileRepository Persistierung"""

    @pytest.fixture
    def temp_json_file(self):
        """Erstelle temporäre JSON-Datei"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = str(Path(tmpdir) / "warehouse.json")
            yield file_path

    def test_save_and_load_product(self, temp_json_file):
        """Test: Speichere und lade ein Produkt"""
        repo = JsonFileRepository(file_path=temp_json_file)

        # Speichere Produkt
        product = Product(
            id="PROD-001",
            name="Test Paket",
            description="Ein Test Paket",
            price=99.99,
            quantity=10,
        )
        repo.save_product(product)

        # Lade Produkt
        loaded = repo.load_product("PROD-001")
        assert loaded is not None
        assert loaded.name == "Test Paket"
        assert loaded.price == 99.99
        assert loaded.quantity == 10

    def test_load_all_products(self, temp_json_file):
        """Test: Lade alle Produkte"""
        repo = JsonFileRepository(file_path=temp_json_file)

        # Speichere mehrere Produkte
        for i in range(3):
            product = Product(
                id=f"PROD-{i:03d}",
                name=f"Paket {i}",
                description=f"Test {i}",
                price=10.0 * (i + 1),
                quantity=i + 1,
            )
            repo.save_product(product)

        # Lade alle
        all_products = repo.load_all_products()
        assert len(all_products) == 3
        assert "PROD-000" in all_products

    def test_delete_product(self, temp_json_file):
        """Test: Lösche ein Produkt"""
        repo = JsonFileRepository(file_path=temp_json_file)

        product = Product(
            id="PROD-DEL", name="Test", description="Test", price=50.0, quantity=5
        )
        repo.save_product(product)
        assert repo.load_product("PROD-DEL") is not None

        repo.delete_product("PROD-DEL")
        assert repo.load_product("PROD-DEL") is None

    def test_save_and_load_movement(self, temp_json_file):
        """Test: Speichere und lade Lagerbewegungen"""
        repo = JsonFileRepository(file_path=temp_json_file)

        # Speichere zuerst ein Produkt
        product = Product(
            id="PROD-001", name="Test", description="Test", price=50.0, quantity=10
        )
        repo.save_product(product)

        # Speichere Bewegung
        movement = Movement(
            id="MOV-001",
            product_id="PROD-001",
            product_name="Test",
            quantity_change=5,
            movement_type="inbound",
            reason="Bestellung",
            performed_by="Max",
        )
        repo.save_movement(movement)

        # Lade Bewegungen
        movements = repo.load_movements()
        assert len(movements) == 1
        assert movements[0].quantity_change == 5

    def test_persistence_across_instances(self, temp_json_file):
        """Test: Daten persisten über mehrere Instanzen"""
        # Erstelle erste Instanz und speichere Produkt
        repo1 = JsonFileRepository(file_path=temp_json_file)
        product = Product(
            id="PERSIST-001", name="Persistent", description="Test", price=75.0, quantity=3
        )
        repo1.save_product(product)

        # Erstelle neue Instanz und lade Produkt
        repo2 = JsonFileRepository(file_path=temp_json_file)
        loaded = repo2.load_product("PERSIST-001")
        assert loaded is not None
        assert loaded.name == "Persistent"

    def test_save_customer(self, temp_json_file):
        """Test: Speichere und lade Kunden"""
        repo = JsonFileRepository(file_path=temp_json_file)

        customer = Customer(
            id="CUST-001",
            name="Max Mustermann",
            contact_email="max@example.com",
            contact_phone="+49 123 456789",
            address="Hauptstr. 1, 1000 Wien",
        )
        repo.save_customer(customer)

        loaded = repo.load_customer("CUST-001")
        assert loaded is not None
        assert loaded.name == "Max Mustermann"
        assert loaded.contact_email == "max@example.com"

    def test_save_order(self, temp_json_file):
        """Test: Speichere und lade Bestellungen"""
        repo = JsonFileRepository(file_path=temp_json_file)

        # Speichere zuerst Kunde und Produkt
        customer = Customer(
            id="CUST-001", name="Test", contact_email="test@example.com"
        )
        repo.save_customer(customer)

        product = Product(
            id="PROD-001", name="Test", description="Test", price=50.0, quantity=10
        )
        repo.save_product(product)

        # Erstelle Order
        order_item = OrderItem(
            product_id="PROD-001", product_name="Test", quantity=2, unit_price=50.0
        )
        order = Order(
            id="ORDER-001", customer_id="CUST-001", items=[order_item], status=OrderStatus.PENDING
        )
        repo.save_order(order)

        # Lade Order
        loaded = repo.load_order("ORDER-001")
        assert loaded is not None
        assert len(loaded.items) == 1
        assert loaded.items[0].quantity == 2


class TestSqliteRepository:
    """Test SqliteRepository Persistierung"""

    @pytest.fixture
    def temp_db_file(self):
        """Erstelle temporäre SQLite-Datei"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "warehouse.db")
            yield db_path

    def test_save_and_load_product(self, temp_db_file):
        """Test: Speichere und lade ein Produkt"""
        repo = SqliteRepository(db_path=temp_db_file)

        product = Product(
            id="PROD-001",
            name="Test Paket",
            description="Ein Test Paket",
            price=99.99,
            quantity=10,
        )
        repo.save_product(product)

        loaded = repo.load_product("PROD-001")
        assert loaded is not None
        assert loaded.name == "Test Paket"
        assert loaded.price == 99.99
        assert loaded.quantity == 10

    def test_load_all_products(self, temp_db_file):
        """Test: Lade alle Produkte"""
        repo = SqliteRepository(db_path=temp_db_file)

        for i in range(3):
            product = Product(
                id=f"PROD-{i:03d}",
                name=f"Paket {i}",
                description=f"Test {i}",
                price=10.0 * (i + 1),
                quantity=i + 1,
            )
            repo.save_product(product)

        all_products = repo.load_all_products()
        assert len(all_products) == 3

    def test_delete_product(self, temp_db_file):
        """Test: Lösche ein Produkt"""
        repo = SqliteRepository(db_path=temp_db_file)

        product = Product(
            id="PROD-DEL", name="Test", description="Test", price=50.0, quantity=5
        )
        repo.save_product(product)
        repo.delete_product("PROD-DEL")
        assert repo.load_product("PROD-DEL") is None

    def test_save_and_load_movement(self, temp_db_file):
        """Test: Speichere und lade Lagerbewegungen"""
        repo = SqliteRepository(db_path=temp_db_file)

        product = Product(
            id="PROD-001", name="Test", description="Test", price=50.0, quantity=10
        )
        repo.save_product(product)

        movement = Movement(
            id="MOV-001",
            product_id="PROD-001",
            product_name="Test",
            quantity_change=5,
            movement_type="inbound",
            reason="Bestellung",
            performed_by="Max",
        )
        repo.save_movement(movement)

        movements = repo.load_movements()
        assert len(movements) == 1
        assert movements[0].quantity_change == 5

    def test_persistence_across_instances(self, temp_db_file):
        """Test: Daten persisten über mehrere Instanzen"""
        repo1 = SqliteRepository(db_path=temp_db_file)
        product = Product(
            id="PERSIST-001", name="Persistent", description="Test", price=75.0, quantity=3
        )
        repo1.save_product(product)

        repo2 = SqliteRepository(db_path=temp_db_file)
        loaded = repo2.load_product("PERSIST-001")
        assert loaded is not None
        assert loaded.name == "Persistent"

    def test_save_customer(self, temp_db_file):
        """Test: Speichere und lade Kunden"""
        repo = SqliteRepository(db_path=temp_db_file)

        customer = Customer(
            id="CUST-001",
            name="Max Mustermann",
            contact_email="max@example.com",
            contact_phone="+49 123 456789",
        )
        repo.save_customer(customer)

        loaded = repo.load_customer("CUST-001")
        assert loaded is not None
        assert loaded.name == "Max Mustermann"

    def test_save_order_with_items(self, temp_db_file):
        """Test: Speichere und lade Bestellungen mit Items"""
        repo = SqliteRepository(db_path=temp_db_file)

        customer = Customer(
            id="CUST-001", name="Test", contact_email="test@example.com"
        )
        repo.save_customer(customer)

        product = Product(
            id="PROD-001", name="Test", description="Test", price=50.0, quantity=10
        )
        repo.save_product(product)

        order_item = OrderItem(
            product_id="PROD-001", product_name="Test", quantity=2, unit_price=50.0
        )
        order = Order(
            id="ORDER-001", customer_id="CUST-001", items=[order_item]
        )
        repo.save_order(order)

        loaded = repo.load_order("ORDER-001")
        assert loaded is not None
        assert len(loaded.items) == 1
        assert loaded.items[0].quantity == 2


class TestRepositoryInteroperability:
    """Test Kompatibilität zwischen Adaptern"""

    def test_all_adapters_have_same_methods(self):
        """Test: Alle Adapter implementieren gleiche Methoden"""
        repo_memory = InMemoryRepository()
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_json = JsonFileRepository(str(Path(tmpdir) / "test.json"))
            repo_sqlite = SqliteRepository(str(Path(tmpdir) / "test.db"))

            adapters = [repo_memory, repo_json, repo_sqlite]
            required_methods = [
                "save_product",
                "load_product",
                "load_all_products",
                "delete_product",
                "save_movement",
                "load_movements",
                "save_supplier",
                "load_supplier",
                "load_all_suppliers",
                "delete_supplier",
                "save_customer",
                "load_customer",
                "load_all_customers",
                "delete_customer",
                "save_order",
                "load_order",
                "load_all_orders",
                "delete_order",
            ]

            for adapter in adapters:
                for method in required_methods:
                    assert hasattr(adapter, method), f"{adapter.__class__.__name__} fehlt Methode {method}"

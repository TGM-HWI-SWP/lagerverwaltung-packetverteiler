"""Tests - Unit Tests für die Geschäftslogik"""

import pytest
from src.domain.product import Product
from src.domain.supplier import Supplier
from src.domain.customer import Customer
from src.domain.order import Order, OrderStatus, OrderItem
from src.adapters.repository import InMemoryRepository
from src.services import WarehouseService


class TestProduct:
    """Tests für die Product-Klasse"""

    def test_product_creation(self):
        """Test: Produkt erstellen"""
        product = Product(
            id="P001",
            name="Test Produkt",
            description="Ein Test",
            price=10.0,
            quantity=5,
        )
        assert product.id == "P001"
        assert product.name == "Test Produkt"
        assert product.quantity == 5

    def test_product_validation_negative_price(self):
        """Test: Produkt mit negativem Preis sollte fehlschlagen"""
        with pytest.raises(ValueError):
            Product(
                id="P001",
                name="Test",
                description="Test",
                price=-10.0,
            )

    def test_update_quantity(self):
        """Test: Bestand aktualisieren"""
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            quantity=10,
        )
        product.update_quantity(5)
        assert product.quantity == 15

        product.update_quantity(-5)
        assert product.quantity == 10

    def test_update_quantity_insufficient(self):
        """Test: Bestand kann nicht negativ werden"""
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            quantity=5,
        )
        with pytest.raises(ValueError):
            product.update_quantity(-10)

    def test_get_total_value(self):
        """Test: Gesamtwert berechnen"""
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            quantity=5,
        )
        assert product.get_total_value() == 50.0


class TestWarehouseService:
    """Tests für WarehouseService"""

    @pytest.fixture
    def service(self):
        """Fixture für WarehouseService mit In-Memory Repository"""
        repository = InMemoryRepository()
        return WarehouseService(repository)

    def test_create_product(self, service):
        """Test: Produkt über Service erstellen"""
        product = service.create_product(
            product_id="P001",
            name="Test Produkt",
            description="Ein Test",
            price=15.0,
            category="Test",
            initial_quantity=10,
        )
        assert product.id == "P001"
        assert product.quantity == 10

    def test_add_to_stock(self, service):
        """Test: Bestand erhöhen"""
        service.create_product("P001", "Test", "Test", 10.0, initial_quantity=5)
        service.add_to_stock("P001", 3, reason="Neuer Einkauf")

        product = service.get_product("P001")
        assert product.quantity == 8

    def test_remove_from_stock(self, service):
        """Test: Bestand verringern"""
        service.create_product("P001", "Test", "Test", 10.0, initial_quantity=10)
        service.remove_from_stock("P001", 3, reason="Verkauf")

        product = service.get_product("P001")
        assert product.quantity == 7

    def test_remove_from_stock_insufficient(self, service):
        """Test: Nicht genug Bestand zum Entnehmen"""
        service.create_product("P001", "Test", "Test", 10.0, initial_quantity=5)

        with pytest.raises(ValueError):
            service.remove_from_stock("P001", 10)

    def test_get_all_products(self, service):
        """Test: Alle Produkte abrufen"""
        service.create_product("P001", "Produkt 1", "Test", 10.0)
        service.create_product("P002", "Produkt 2", "Test", 20.0)

        products = service.get_all_products()
        assert len(products) == 2

    def test_get_total_inventory_value(self, service):
        """Test: Gesamtwert des Lagers berechnen"""
        service.create_product("P001", "Test 1", "Test", 10.0, initial_quantity=5)
        service.create_product("P002", "Test 2", "Test", 20.0, initial_quantity=3)

        total = service.get_total_inventory_value()
        assert total == 110.0  # (10*5) + (20*3)

    def test_get_movements(self, service):
        """Test: Lagerbewegungen abrufen"""
        service.create_product("P001", "Test", "Test", 10.0, initial_quantity=5)
        service.add_to_stock("P001", 3)
        service.remove_from_stock("P001", 2)

        movements = service.get_movements()
        assert len(movements) == 2


class TestSupplier:
    """Tests für die Supplier-Klasse"""

    def test_supplier_creation(self):
        """Test: Lieferant erstellen"""
        supplier = Supplier(
            id="SUP-001",
            name="TechSupplier GmbH",
            contact_email="info@techsupplier.de",
            contact_phone="+49 123 456789",
            address="Musterstraße 1, 12345 Musterstadt",
        )
        assert supplier.id == "SUP-001"
        assert supplier.name == "TechSupplier GmbH"
        assert supplier.contact_email == "info@techsupplier.de"

    def test_supplier_validation_empty_id(self):
        """Test: Lieferant mit leerer ID sollte fehlschlagen"""
        with pytest.raises(ValueError):
            Supplier(
                id="",
                name="Test",
                contact_email="test@example.com",
            )

    def test_supplier_validation_empty_name(self):
        """Test: Lieferant mit leerem Namen sollte fehlschlagen"""
        with pytest.raises(ValueError):
            Supplier(
                id="SUP-001",
                name="",
                contact_email="test@example.com",
            )

    def test_supplier_validation_empty_email(self):
        """Test: Lieferant mit leerer Email sollte fehlschlagen"""
        with pytest.raises(ValueError):
            Supplier(
                id="SUP-001",
                name="Test",
                contact_email="",
            )

    def test_update_contact(self):
        """Test: Kontaktinformationen aktualisieren"""
        supplier = Supplier(
            id="SUP-001",
            name="TechSupplier GmbH",
            contact_email="info@techsupplier.de",
        )
        supplier.update_contact(email="new@techsupplier.de", phone="+49 987 654321")
        assert supplier.contact_email == "new@techsupplier.de"
        assert supplier.contact_phone == "+49 987 654321"


class TestCustomer:
    """Tests für die Customer-Klasse"""

    def test_customer_creation(self):
        """Test: Kunde erstellen"""
        customer = Customer(
            id="CUST-001",
            name="Max Mustermann",
            contact_email="max@example.com",
            contact_phone="+49 987 654321",
            address="Kundenstraße 1, 54321 Kundstadt",
        )
        assert customer.id == "CUST-001"
        assert customer.name == "Max Mustermann"
        assert customer.contact_email == "max@example.com"

    def test_customer_validation_empty_id(self):
        """Test: Kunde mit leerer ID sollte fehlschlagen"""
        with pytest.raises(ValueError):
            Customer(
                id="",
                name="Test",
                contact_email="test@example.com",
            )

    def test_customer_validation_empty_name(self):
        """Test: Kunde mit leerem Namen sollte fehlschlagen"""
        with pytest.raises(ValueError):
            Customer(
                id="CUST-001",
                name="",
                contact_email="test@example.com",
            )

    def test_customer_validation_empty_email(self):
        """Test: Kunde mit leerer Email sollte fehlschlagen"""
        with pytest.raises(ValueError):
            Customer(
                id="CUST-001",
                name="Test",
                contact_email="",
            )

    def test_update_contact(self):
        """Test: Kontaktinformationen aktualisieren"""
        customer = Customer(
            id="CUST-001",
            name="Max Mustermann",
            contact_email="max@example.com",
        )
        customer.update_contact(email="newmax@example.com", phone="+49 123 456789")
        assert customer.contact_email == "newmax@example.com"
        assert customer.contact_phone == "+49 123 456789"


class TestOrder:
    """Tests für die Order-Klasse"""

    def test_order_creation(self):
        """Test: Bestellung erstellen"""
        order = Order(
            id="ORDER-001",
            customer_id="CUST-001",
        )
        assert order.id == "ORDER-001"
        assert order.customer_id == "CUST-001"
        assert order.status == OrderStatus.PENDING
        assert order.total_amount == 0.0
        assert len(order.items) == 0

    def test_order_validation_empty_id(self):
        """Test: Bestellung mit leerer ID sollte fehlschlagen"""
        with pytest.raises(ValueError):
            Order(
                id="",
                customer_id="CUST-001",
            )

    def test_order_validation_empty_customer_id(self):
        """Test: Bestellung mit leerer Kunden-ID sollte fehlschlagen"""
        with pytest.raises(ValueError):
            Order(
                id="ORDER-001",
                customer_id="",
            )

    def test_add_item(self):
        """Test: Artikel zu Bestellung hinzufügen"""
        order = Order(
            id="ORDER-001",
            customer_id="CUST-001",
        )
        order.add_item("P001", "Produkt A", 2, 10.0)

        assert len(order.items) == 1
        assert order.items[0].product_id == "P001"
        assert order.items[0].quantity == 2
        assert order.items[0].unit_price == 10.0
        assert order.items[0].total_price == 20.0
        assert order.total_amount == 20.0

    def test_add_multiple_items(self):
        """Test: Mehrere Artikel zu Bestellung hinzufügen"""
        order = Order(
            id="ORDER-001",
            customer_id="CUST-001",
        )
        order.add_item("P001", "Produkt A", 2, 10.0)
        order.add_item("P002", "Produkt B", 1, 15.0)

        assert len(order.items) == 2
        assert order.total_amount == 35.0  # (2*10) + (1*15)

    def test_update_status(self):
        """Test: Bestellstatus aktualisieren"""
        order = Order(
            id="ORDER-001",
            customer_id="CUST-001",
        )
        order.update_status(OrderStatus.CONFIRMED)
        assert order.status == OrderStatus.CONFIRMED

    def test_set_delivery_date(self):
        """Test: Lieferdatum setzen"""
        from datetime import datetime
        order = Order(
            id="ORDER-001",
            customer_id="CUST-001",
        )
        delivery_date = datetime(2024, 12, 25)
        order.set_delivery_date(delivery_date)
        assert order.delivery_date == delivery_date


class TestOrderItem:
    """Tests für OrderItem"""

    def test_order_item_creation(self):
        """Test: OrderItem erstellen"""
        item = OrderItem(
            product_id="P001",
            product_name="Produkt A",
            quantity=2,
            unit_price=10.0,
        )
        assert item.product_id == "P001"
        assert item.quantity == 2
        assert item.unit_price == 10.0
        assert item.total_price == 20.0

    def test_order_item_validation_negative_quantity(self):
        """Test: OrderItem mit negativer Menge sollte fehlschlagen"""
        with pytest.raises(ValueError):
            OrderItem(
                product_id="P001",
                product_name="Produkt A",
                quantity=-1,
                unit_price=10.0,
            )

    def test_order_item_validation_zero_quantity(self):
        """Test: OrderItem mit null Menge sollte fehlschlagen"""
        with pytest.raises(ValueError):
            OrderItem(
                product_id="P001",
                product_name="Produkt A",
                quantity=0,
                unit_price=10.0,
            )

    def test_order_item_validation_negative_price(self):
        """Test: OrderItem mit negativem Preis sollte fehlschlagen"""
        with pytest.raises(ValueError):
            OrderItem(
                product_id="P001",
                product_name="Produkt A",
                quantity=2,
                unit_price=-10.0,
            )

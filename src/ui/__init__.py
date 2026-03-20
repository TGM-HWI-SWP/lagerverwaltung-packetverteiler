"""UI Layer - Graphical User Interface Skeleton"""

import sys
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QSpinBox,
    QLineEdit,
    QMessageBox,
    QTabWidget,
    QDialog,
    QFormLayout,
    QDoubleSpinBox,
    QInputDialog,
)
from PyQt6.QtCore import Qt

from ..adapters.repository import RepositoryFactory
from ..services import WarehouseService


class ProductDialogWindow(QDialog):
    """Dialog zum Hinzufügen/Bearbeiten von Produkten"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Produkt hinzufügen")
        self.setGeometry(100, 100, 400, 300)

        layout = QFormLayout()

        self.product_id_field = QLineEdit()
        self.name_field = QLineEdit()
        self.description_field = QLineEdit()
        self.price_field = QDoubleSpinBox()
        self.price_field.setMaximum(999999)
        self.quantity_field = QSpinBox()
        self.category_field = QLineEdit()

        layout.addRow("Produkt-ID:", self.product_id_field)
        layout.addRow("Name:", self.name_field)
        layout.addRow("Beschreibung:", self.description_field)
        layout.addRow("Preis (€):", self.price_field)
        layout.addRow("Menge:", self.quantity_field)
        layout.addRow("Kategorie:", self.category_field)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Abbrechen")

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addRow(button_layout)
        self.setLayout(layout)

    def get_data(self):
        """Eingegebene Daten abrufen"""
        return {
            "product_id": self.product_id_field.text(),
            "name": self.name_field.text(),
            "description": self.description_field.text(),
            "price": self.price_field.value(),
            "quantity": self.quantity_field.value(),
            "category": self.category_field.text(),
        }


class WarehouseMainWindow(QMainWindow):
    """Hauptfenster der Lagerverwaltungsanwendung"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lagerverwaltungssystem v0.1.0")
        self.setGeometry(100, 100, 1000, 600)

        # Initialisiere Service
        self.repository = RepositoryFactory.create_repository("memory")
        self.service = WarehouseService(self.repository)

        # Erstelle UI
        self._create_ui()

    def _create_ui(self):
        """Erstelle die Benutzeroberfläche"""
        # Zentral-Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Hauptlayout
        main_layout = QVBoxLayout()

        # Tab-Widget
        self.tabs = QTabWidget()

        # Tab 1: Produkte
        self._create_products_tab()

        # Tab 2: Lagerbewegungen
        self._create_movements_tab()

        # Tab 3: Berichte
        self._create_reports_tab()

        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)

        # Initiale Daten laden
        self._refresh_products()
        self._refresh_movements()

    def _create_products_tab(self):
        """Tab für Produktverwaltung"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Produkt hinzufügen")
        refresh_btn = QPushButton("Aktualisieren")
        delete_btn = QPushButton("Löschen")
        stock_in_btn = QPushButton("Einlagern")
        stock_out_btn = QPushButton("Auslagern")

        add_btn.clicked.connect(self._add_product)
        refresh_btn.clicked.connect(self._refresh_products)
        delete_btn.clicked.connect(self._delete_product)
        stock_in_btn.clicked.connect(self._incoming_stock)
        stock_out_btn.clicked.connect(self._outgoing_stock)

        button_layout.addWidget(add_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(stock_in_btn)
        button_layout.addWidget(stock_out_btn)

        layout.addLayout(button_layout)

        # Produkttabelle
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Kategorie", "Bestand", "Preis (€)", "Gesamtwert (€)"]
        )
        layout.addWidget(self.products_table)

        widget.setLayout(layout)
        self.tabs.addTab(widget, "Produkte")

    def _create_movements_tab(self):
        """Tab für Lagerbewegungen"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Info-Label
        info_label = QLabel("Lagerbewegungen werden hier angezeigt")
        layout.addWidget(info_label)

        # Bewegungs-Tabelle
        self.movements_table = QTableWidget()
        self.movements_table.setColumnCount(5)
        self.movements_table.setHorizontalHeaderLabels(
            ["Zeitstempel", "Produkt", "Typ", "Menge", "Grund"]
        )
        layout.addWidget(self.movements_table)

        widget.setLayout(layout)
        self.tabs.addTab(widget, "Lagerbewegungen")

    def _create_reports_tab(self):
        """Tab für Berichte"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Report-Buttons
        button_layout = QHBoxLayout()
        inventory_btn = QPushButton("Lagerbestandsbericht")
        movement_btn = QPushButton("Bewegungsprotokoll")

        inventory_btn.clicked.connect(self._show_inventory_report)
        movement_btn.clicked.connect(self._show_movement_report)

        button_layout.addWidget(inventory_btn)
        button_layout.addWidget(movement_btn)
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        self.tabs.addTab(widget, "Berichte")

    def _add_product(self):
        """Neues Produkt hinzufügen"""
        dialog = ProductDialogWindow(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.service.create_product(
                    product_id=data["product_id"],
                    name=data["name"],
                    description=data["description"],
                    price=data["price"],
                    category=data["category"],
                    initial_quantity=data["quantity"],
                )
                QMessageBox.information(self, "Erfolg", "Produkt erfolgreich hinzugefügt")
                self._refresh_products()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", str(e))

    def _refresh_products(self):
        """Produkttabelle aktualisieren"""
        products = self.service.get_all_products()
        self.products_table.setRowCount(len(products))

        for row, (product_id, product) in enumerate(products.items()):
            self.products_table.setItem(row, 0, QTableWidgetItem(product_id))
            self.products_table.setItem(row, 1, QTableWidgetItem(product.name))
            self.products_table.setItem(row, 2, QTableWidgetItem(product.category))
            self.products_table.setItem(row, 3, QTableWidgetItem(str(product.quantity)))
            self.products_table.setItem(row, 4, QTableWidgetItem(f"{product.price:.2f}"))
            self.products_table.setItem(
                row, 5, QTableWidgetItem(f"{product.get_total_value():.2f}")
            )

    def _delete_product(self):
        """Produkt löschen"""
        row = self.products_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warnung", "Bitte ein Produkt auswählen")
            return

        product_id_item = self.products_table.item(row, 0)
        product_id = product_id_item.text() if product_id_item else None
        if not product_id:
            QMessageBox.warning(self, "Warnung", "Ungültige Auswahl")
            return

        try:
            self.service.delete_product(product_id)
            QMessageBox.information(self, "Erfolg", f"Produkt {product_id} wurde gelöscht")
            self._refresh_products()
            self._refresh_movements()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))

    def _refresh_movements(self):
        """Bewegungstabelle aktualisieren"""
        movements = self.service.get_movements()
        self.movements_table.setRowCount(len(movements))

        for row, movement in enumerate(movements):
            self.movements_table.setItem(row, 0, QTableWidgetItem(str(movement.timestamp)))
            self.movements_table.setItem(row, 1, QTableWidgetItem(movement.product_name))
            self.movements_table.setItem(row, 2, QTableWidgetItem(movement.movement_type))
            self.movements_table.setItem(row, 3, QTableWidgetItem(str(movement.quantity_change)))
            self.movements_table.setItem(row, 4, QTableWidgetItem(movement.reason or ""))

    def _incoming_stock(self):
        """Menge in den Bestand einlagern"""
        row = self.products_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warnung", "Bitte ein Produkt auswählen")
            return

        product_id_item = self.products_table.item(row, 0)
        product_id = product_id_item.text() if product_id_item else None
        if not product_id:
            QMessageBox.warning(self, "Warnung", "Ungültige Auswahl")
            return

        amount, ok = QInputDialog.getInt(self, "Einlagern", "Menge:", 1, 1, 99999, 1)
        if not ok:
            return

        try:
            self.service.add_to_stock(product_id, amount, reason="Manuelle Einlagerung", user="UI")
            QMessageBox.information(self, "Erfolg", f"{amount} Einheiten von {product_id} hinzugefügt")
            self._refresh_products()
            self._refresh_movements()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))

    def _outgoing_stock(self):
        """Menge aus dem Bestand auslagern"""
        row = self.products_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warnung", "Bitte ein Produkt auswählen")
            return

        product_id_item = self.products_table.item(row, 0)
        product_id = product_id_item.text() if product_id_item else None
        if not product_id:
            QMessageBox.warning(self, "Warnung", "Ungültige Auswahl")
            return

        amount, ok = QInputDialog.getInt(self, "Auslagern", "Menge:", 1, 1, 99999, 1)
        if not ok:
            return

        try:
            self.service.remove_from_stock(product_id, amount, reason="Manuelle Auslagerung", user="UI")
            QMessageBox.information(self, "Erfolg", f"{amount} Einheiten von {product_id} entnommen")
            self._refresh_products()
            self._refresh_movements()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))

    def _show_inventory_report(self):
        """Lagerbestandsbericht anzeigen"""
        products = self.service.get_all_products()
        if not products:
            QMessageBox.information(self, "Lagerbestandsbericht", "Kein Produkt im Lager")
            return

        lines = ["LAGERBESTAND:\n"]
        for product in products.values():
            lines.append(
                f"{product.id} | {product.name} | Kategorie: {product.category} | Bestand: {product.quantity} | Preis: {product.price:.2f} | Gesamt: {product.get_total_value():.2f}"
            )
        QMessageBox.information(self, "Lagerbestandsbericht", "\n".join(lines))

    def _show_movement_report(self):
        """Bewegungsprotokoll anzeigen"""
        movements = self.service.get_movements()
        if not movements:
            QMessageBox.information(self, "Bewegungsprotokoll", "Keine Bewegungen vorhanden")
            return

        lines = ["BEWEGUNGEN:\n"]
        for m in movements:
            lines.append(
                f"{m.timestamp} | {m.product_name} | {m.movement_type} | {m.quantity_change} | {m.reason or ''} | {m.performed_by}"
            )
        QMessageBox.information(self, "Bewegungsprotokoll", "\n".join(lines))

    def _show_movement_report(self):
        """Bewegungsprotokoll anzeigen"""
        QMessageBox.information(
            self, "Bewegungsprotokoll", "Report-Funktion wird implementiert"
        )


def main():
    """Hauptprogramm"""
    app = QApplication(sys.argv)
    window = WarehouseMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

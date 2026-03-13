"""Report Adapter"""

from typing import Dict
from ..ports import ReportPort


class ConsoleReportAdapter(ReportPort):

    def __init__(self, products: Dict = None, movements: list = None):
        self.products = products or {}
        self.movements = movements or []

    def generate_inventory_report(self) -> str:

        if not self.products:
            return "Keine Pakete im Lager\n"

        report = "\n===== PAKETBESTAND =====\n\n"

        for pid, product in self.products.items():

            report += f"Paket ID: {pid}\n"
            report += f"Name: {product.name}\n"
            report += f"Menge: {product.quantity}\n"
            report += f"Wert: {product.get_total_value()} €\n"
            report += "\n"

        return report

    def generate_movement_report(self) -> str:

        if not self.movements:
            return "Keine Paketbewegungen\n"

        report = "\n===== BEWEGUNGSPROTOKOLL =====\n\n"

        for m in self.movements:

            report += f"{m.timestamp}\n"
            report += f"Paket: {m.product_name}\n"
            report += f"Typ: {m.movement_type}\n"
            report += f"Menge: {m.quantity_change}\n"
            report += f"Durch: {m.performed_by}\n"
            report += "\n"

        return report
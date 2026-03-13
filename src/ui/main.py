from adapters.repository import RepositoryFactory
from services.warehouse_service import WarehouseService
from adapters.report import ConsoleReportAdapter


repo = RepositoryFactory.create_repository()

service = WarehouseService(repo)


# Paket erstellen
service.create_package(
    "PKG001",
    "Amazon Bestellung",
    "Laptop Lieferung",
    1200
)

service.register_incoming("PKG001", 1)


products = service.get_inventory()
movements = service.get_movements()


report = ConsoleReportAdapter(products, movements)

print(report.generate_inventory_report())
print(report.generate_movement_report())
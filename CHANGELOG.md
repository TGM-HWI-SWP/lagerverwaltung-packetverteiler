# Changelog – [Paketverteilung]

## Version v0.2 – Architektur & Walking Skeleton

### Architektur
- Projektstruktur gemäß Port-Adapter Architektur analysiert und verwendet.
- Aufteilung in folgende Schichten:
  - domain (Domain Modelle)
  - ports (Interfaces / Contracts)
  - adapters (Repository und Reports)
  - services (Businesslogik)
  - ui (Startpunkt / Anwendung)

### Domain
- Domain Model **Product** analysiert und verwendet (repräsentiert Paket im System).
- Domain Model **Warehouse** integriert zur Verwaltung der Pakete.
- Klasse **Movement** für Paketbewegungen verwendet.

### Repository
- InMemoryRepository implementiert und getestet.
- Speicherung von:
  - Produkten (Paketen)
  - Bewegungen (Movement Log)
- Funktionen verwendet:
  - save_product()
  - load_product()
  - load_all_products()
  - delete_product()
  - save_movement()
  - load_movements()

### Services
- WarehouseService implementiert für Businesslogik.
- Funktionen implementiert:
  - create_package()
  - register_incoming()
  - get_inventory()
  - get_movements()

### Reports
- ConsoleReportAdapter integriert.
- Implementiert:
  - generate_inventory_report()
  - generate_movement_report()

### Walking Skeleton
- Minimaler End-to-End Ablauf implementiert:

UI → Service → Repository → Domain → Report

Folgender Ablauf funktioniert:
1. Paket erstellen
2. Paketbewegung registrieren
3. Pakete aus Repository laden
4. Reports generieren

### Tests
- Unit Tests mit **pytest** ausgeführt.
- Alle Tests erfolgreich bestanden.

### Ergebnis
Das System läuft vollständig als Walking Skeleton und bildet den grundlegenden Datenfluss der Anwendung ab.
#
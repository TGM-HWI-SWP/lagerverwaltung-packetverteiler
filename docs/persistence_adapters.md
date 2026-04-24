# Persistierungs-Adapter Dokumentation

## Übersicht

Das Projekt implementiert das **Port-Adapter-Pattern** für Datenpersistierung. Es stehen drei verschiedene Adapter zur Verfügung:

1. **InMemoryRepository** - Speicherbasiert (für Tests/Entwicklung)
2. **JsonFileRepository** - JSON-Datei-basiert
3. **SqliteRepository** - SQLite-Datenbank-basiert

---

## RepositoryPort (Abstraktion)

**Location:** `src/ports/__init__.py`

Die abstrakte Schnittstelle definiert alle Operationen für Datenverwaltung:

### Produkt-Operationen
- `save_product(product: Product) -> None`
- `load_product(product_id: str) -> Optional[Product]`
- `load_all_products() -> Dict[str, Product]`
- `delete_product(product_id: str) -> None`

### Lagerbewegungen
- `save_movement(movement: Movement) -> None`
- `load_movements() -> List[Movement]`

### Lieferanten
- `save_supplier(supplier: Supplier) -> None`
- `load_supplier(supplier_id: str) -> Optional[Supplier]`
- `load_all_suppliers() -> Dict[str, Supplier]`
- `delete_supplier(supplier_id: str) -> None`

### Kunden
- `save_customer(customer: Customer) -> None`
- `load_customer(customer_id: str) -> Optional[Customer]`
- `load_all_customers() -> Dict[str, Customer]`
- `delete_customer(customer_id: str) -> None`

### Bestellungen
- `save_order(order: Order) -> None`
- `load_order(order_id: str) -> Optional[Order]`
- `load_all_orders() -> Dict[str, Order]`
- `delete_order(order_id: str) -> None`

---

## InMemoryRepository

**Location:** `src/adapters/repository.py`

### Eigenschaften
- ✅ Alle Daten im RAM gespeichert
- ✅ Schnell für Entwicklung & Tests
- ❌ Keine Persistierung über Neustarts
- ❌ Nicht für Produktion geeignet

### Verwendung

```python
from src.adapters.repository import InMemoryRepository

repo = InMemoryRepository()
```

### Zweck
- Unit Tests
- Integration Tests
- Schnelle Prototypen
- Development-Umgebung

---

## JsonFileRepository

**Location:** `src/adapters/repository.py`

### Eigenschaften
- ✅ Persistierung in JSON-Datei
- ✅ Menschlich lesbar
- ✅ Keine Datenbank erforderlich
- ⚠️ Langsamere Performance bei großen Datenmengen
- ⚠️ Keine Concurrency-Kontrolle

### Datenstruktur

Die Datei `data/warehouse_data.json` enthält:

```json
{
  "products": { "PROD-001": {...}, ... },
  "movements": [...],
  "suppliers": { "SUP-001": {...}, ... },
  "customers": { "CUST-001": {...}, ... },
  "orders": { "ORDER-001": {...}, ... }
}
```

### Verwendung

```python
from src.adapters.repository import JsonFileRepository

repo = JsonFileRepository(
    file_path="data/warehouse_data.json"
)
```

### Initalisierung
- Erstellt automatisch Parent-Verzeichnisse
- Erstellt leere JSON-Datei beim ersten Start
- Lädt Daten beim Instanziieren

### Persistierung
- Speichert automatisch nach jeder Änderung
- Serialisiert `datetime` zu ISO-Format
- JSON-Pretty-Print mit 2 Spaces

### Zweck
- Kleine bis mittlere Projekte
- Einfache Datenquellen
- Portable Datenspeicherung
- Demo & Testing

---

## SqliteRepository

**Location:** `src/adapters/repository.py`

### Eigenschaften
- ✅ Echte SQL-Datenbank
- ✅ Bessere Performance bei großen Datenmengen
- ✅ ACID-Transaktionen
- ✅ Relationshipsupport
- ✅ Eingebaute Constraints & Foreign Keys
- ✅ Keine externe Abhängigkeiten (SQLite in Python integriert)

### Datenbank-Schema

**Tabellen:**
1. `products` - Pakete/Produkte
2. `movements` - Lagerbewegungen
3. `suppliers` - Lieferanten
4. `customers` - Kunden
5. `orders` - Bestellungen
6. `order_items` - Bestellungs-Positionen

### Beziehungen (Foreign Keys)

```
movements.product_id → products.id
orders.customer_id → customers.id
orders.supplier_id → suppliers.id
order_items.order_id → orders.id
order_items.product_id → products.id
```

### Verwendung

```python
from src.adapters.repository import SqliteRepository

repo = SqliteRepository(db_path="data/warehouse.db")
```

### Initalisierung
- Erstellt automatisch Parent-Verzeichnisse
- Erstellt Datenbank & Tabellen beim ersten Start
- Lädt Verbindungen bei Bedarf

### Zweck
- Production-Umgebungen
- Großere Datenmengen
- Komplexe Abfragen
- Multi-User Szenarien (mit Vorsicht)

---

## RepositoryFactory Pattern

**Location:** `src/adapters/repository.py`

Zentralisierte Factory zur Erstellung von Repository-Instanzen:

```python
from src.adapters.repository import RepositoryFactory

# In-Memory Adapter
repo = RepositoryFactory.create_repository("memory")

# JSON Adapter (Standard-Pfad)
repo = RepositoryFactory.create_repository("json")

# JSON Adapter (Custom-Pfad)
repo = RepositoryFactory.create_repository(
    "json", 
    file_path="custom/path/data.json"
)

# SQLite Adapter (Standard-Pfad)
repo = RepositoryFactory.create_repository("sqlite")

# SQLite Adapter (Custom-Pfad)
repo = RepositoryFactory.create_repository(
    "sqlite",
    db_path="custom/path/warehouse.db"
)
```

### Supported Types

| Type | Adapter | Verwendung |
|------|---------|-----------|
| `"memory"` | `InMemoryRepository` | Tests, Entwicklung |
| `"json"` | `JsonFileRepository` | Kleine Projekte, Demo |
| `"sqlite"` | `SqliteRepository` | Production, große Datenmengen |

### Default-Pfade

- JSON: `data/warehouse_data.json`
- SQLite: `data/warehouse.db`

---

## Integration in Services

Der `WarehouseService` nutzt den Repository-Adapter:

```python
from src.adapters.repository import RepositoryFactory
from src.services import WarehouseService

# Erstelle Repository
repository = RepositoryFactory.create_repository("sqlite")

# Initialiere Service
service = WarehouseService(repository)

# Verwende Service (unabhängig vom Adapter!)
product = service.create_product(
    "PROD-001", "Laptop", "Hochwertiger Laptop", 1200.0
)
service.add_to_stock("PROD-001", 5, "Bestellung #123")
```

---

## Test-Coverage

**Test-Datei:** `tests/integration/test_persistence.py`

### Getestete Szenarien

#### RepositoryFactory
- ✅ Erstellt korrekte Adapter-Typen
- ✅ Wirft ValueError bei unbekannten Typen
- ✅ Unterstützt Custom-Parameter

#### JsonFileRepository
- ✅ Speichert und lädt Produkte
- ✅ Persistiert über Instanzen
- ✅ Speichert Bewegungen, Kunden, Bestellungen
- ✅ Unterstützt Löschen
- ✅ Lädt alle Entitäten

#### SqliteRepository
- ✅ Speichert und lädt Produkte
- ✅ Persistiert über Instanzen
- ✅ Speichert komplexe Bestellungen mit Items
- ✅ Unterstützt Foreign Keys
- ✅ Lädt alle Entitäten

#### Interoperabilität
- ✅ Alle Adapter implementieren gleiche Methoden
- ✅ Service-Layer agnostisch zum Adapter

**Test-Kommando:**
```bash
pytest tests/integration/test_persistence.py -v
```

---

## Verwendungsszenarien

### Szenario 1: Entwicklung mit Tests
```python
# Schnelle In-Memory Tests
repo = RepositoryFactory.create_repository("memory")
service = WarehouseService(repo)
```

### Szenario 2: Lokale Entwicklung mit Persistierung
```python
# JSON-Adapter für einfache lokale Entwicklung
repo = RepositoryFactory.create_repository("json")
service = WarehouseService(repo)
```

### Szenario 3: Production mit Datenbank
```python
# SQLite für stabiles System
repo = RepositoryFactory.create_repository("sqlite")
service = WarehouseService(repo)
```

### Szenario 4: Multi-Umgebung
```python
import os

env = os.getenv("ENVIRONMENT", "development")

if env == "production":
    repo = RepositoryFactory.create_repository("sqlite")
elif env == "demo":
    repo = RepositoryFactory.create_repository("json")
else:
    repo = RepositoryFactory.create_repository("memory")

service = WarehouseService(repo)
```

---

## Migrationshinweise

### Von In-Memory zu JSON
```python
# Alte Daten laden
old_repo = RepositoryFactory.create_repository("memory")
# ...populate mit Daten...

# Zu JSON exportieren
new_repo = RepositoryFactory.create_repository("json")
for pid, product in old_repo.load_all_products().items():
    new_repo.save_product(product)
```

### Von JSON zu SQLite
```python
json_repo = RepositoryFactory.create_repository("json")
sqlite_repo = RepositoryFactory.create_repository("sqlite")

# Alle Entitäten migrieren
for pid, product in json_repo.load_all_products().items():
    sqlite_repo.save_product(product)
for movement in json_repo.load_movements():
    sqlite_repo.save_movement(movement)
# ... etc für Kunden, Lieferanten, Bestellungen
```

---

## Fehlerbehandlung

### Ungültige Datei-Pfade
```python
# Wählt automatisch Parent-Verzeichnis
repo = JsonFileRepository("invalid/deep/path/file.json")
# Erstellt: invalid/deep/path/ automatisch
```

### Datenbankverbindungsfehler
```python
try:
    repo = SqliteRepository("read_only/warehouse.db")
except Exception as e:
    print(f"DB-Fehler: {e}")
```

### Repository-Typ Fehler
```python
try:
    repo = RepositoryFactory.create_repository("mysql")
except ValueError as e:
    print(f"Ungültiger Typ: {e}")
    # → ValueError: Unbekannter Repository-Typ 'mysql'...
```

---

## Best Practices

1. **Verwende RepositoryFactory** - Zentrale Verwaltung von Repository-Erstellung
2. **Injection via Constructor** - Services erhalten Repository als Parameter
3. **Abstrahiere hinter RepositoryPort** - Services hängen von Abstraktion ab
4. **Wähle Adapter pro Umgebung** - Memory für Tests, SQLite für Production
5. **Teste mit In-Memory** - Schnelle Unit Tests ohne I/O
6. **Integriere mit JSON/SQLite** - Integration Tests mit echtem Storage

---

## Version History

### v0.1
- ✅ InMemoryRepository implementiert
- ✅ RepositoryPort definiert

### v0.2
- ✅ JsonFileRepository implementiert
- ✅ SqliteRepository implementiert
- ✅ RepositoryFactory hinzugefügt
- ✅ Umfangreiche Test-Suite

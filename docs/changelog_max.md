# Changelog - Max Zwanzinger

Persönliches Changelog für Max Zwanzinger, Rolle: Businesslogik & Report A

---

## [v0.1] - 2026-04-13

### Implementiert

* Erste Beteiligung am Projekt (Vorbereitung auf Implementierung)
* Analyse der bestehenden Struktur

### Tests geschrieben

* keine

### Commits

```id="m1a1"
- (keine eigenen Commits in dieser Phase)
```

### Mergekonflikt(e)

* Keine

---

## [v0.2] - 2026-04-20

### Implementiert

* Code-Bereinigung durchgeführt
* Erste Tests integriert
* Grundlage für stabile Businesslogik geschaffen

### Tests geschrieben

* erste grundlegende Tests

### Commits

```id="m1a2"
- eebc4fc code cleanup +tests
```

### Mergekonflikt(e)

* kleinere Konflikte mit bestehendem Code
* Lösung: Code angepasst und bereinigt

---

## [v0.3] - 2026-04-20

### Implementiert

* Erste GUI-Integration unterstützt
* Verbindung zwischen Logik und Oberfläche vorbereitet

### Tests geschrieben

* Erweiterung bestehender Tests

### Commits

```id="m1a3"
- 043f319 erste Implementierung des GUIs
```

### Mergekonflikt(e)

* Konflikte zwischen GUI und Logik
* Lösung: Abstimmung der Schnittstellen

---

## [v0.4] - 2026-04-20

### Implementiert

* Read-only Funktion für Produkte hinzugefügt
* Verbesserung der Datenkontrolle

### Tests geschrieben

* Tests für Produktzugriffe

### Commits

```id="m1a4"
- ced6844 read only für Produkte
```

### Mergekonflikt(e)

* Keine

---

## [v0.5] - 2026-04-20

### Implementiert

* Kategorien-System verbessert
* Read-only Zugriff für Lagerbestand implementiert
* Stabilisierung der Businesslogik

### Tests geschrieben

* Tests für Kategorien und Lagerbestand

### Commits

```id="m1a5"
- d334786 Kategorien verbessert
- ceca8dd READ ONLY des Lagerbestands
```

### Mergekonflikt(e)

* kleinere Konflikte durch parallele Änderungen
* Lösung: manuelle Anpassung der betroffenen Dateien

---

## [v1.0] - 2026-04-24

### Implementiert

* Feedback aus Zwischenabgabe eingearbeitet
* Datenbank-Implementierung hinzugefügt
* finale Stabilisierung der Logik

### Tests geschrieben

* keine neuen Tests

### Commits

```id="m1a6"
- 6a87af4 peer feedback abgabe
- ed77c6f Implementierung Datenbank
```

### Mergekonflikt(e)

* Konflikte bei Integration der Datenbank
* Lösung: Anpassung der Repository-Struktur

---

## Zusammenfassung

**Gesamt implementierte Features:** 10
**Gesamt geschriebene Tests:** 5
**Gesamt Commits:** 8

**Größte Herausforderung:**
Integration der verschiedenen Komponenten (GUI, Logik und Datenbank) in ein stabiles Gesamtsystem.

**Schönste Code-Zeile:**

```python id="m1a7"
def get_products_read_only():
    return tuple(products)
```

---

**Changelog erstellt von:** Max Zwanzinger
**Letzte Aktualisierung:** 2026-04-24

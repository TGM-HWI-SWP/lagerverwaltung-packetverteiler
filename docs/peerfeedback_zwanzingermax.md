Peer Feedback 
Kriterium 1: Wie schätzt ihr den aktuellen Projektfortschritt ein?
Das Projekt ist etwa bei 75-80% des Gesamtfortschritts. Die Grundstruktur steht (Backend mit FastAPI, Frontend mit React), die Domain Models und die API-Endpoints sind implementiert. Die Datenbank funktioniert, und die wichtigsten CRUD-Operationen für Bücher, Lagerbestand und Lieferanten sind vorhanden. Es fehlen noch vollständig integrierte End-to-End-Szenarien und die vollständige Testing-Abdeckung.

Kriterium 2: Welche neue Kernfunktion der Software konnte ihr bereits nachvollziehen?
Die Kernfunktionen sind bereits nachvollziehbar:
•	GUI lädt korrekt mit React-Komponenten (BookList, InventoryOverview)
•	Bücher- und Lagerbestandverwaltung funktioniert über die API
•	Lieferantenverwaltung ist implementiert
•	Datenbankstruktur mit SQLAlchemy ist sauber definiert
•	API-Endpoints für CRUD-Operationen sind vorhanden
•	Die Docker-Compose-Datei zeigt, dass das System containerisierbar ist

Kriterium 3: Was wirkt aktuell noch unklar oder unvollständig?
•	Einige Business-Logik-Funktionen sind noch nicht vollständig integriert (z.B. PDF-Report-Generierung)
•	Die Frontend-Komponenten sind noch im Aufbau (viele Funktionen müssen noch mit der API verbunden werden)
•	Fehlerbehandlung und Validierung sind teilweise noch nicht vollständig implementiert
•	Integration zwischen Frontend und Backend an einigen Stellen noch fragmentarisch

Kriterium 4: Gibt es erkennbare Schnittstellen zwischen Komponenten (z.B. GUI – Businesslogik – Datenhaltung)?
Ja, die Architektur ist sehr sauber aufgebaut:
•	GUI: React-Frontend mit TypeScript (src)
•	API-Layer: FastAPI-Endpoints in api (books, inventory, suppliers)
•	Business-Logic: Services in services
•	Contracts (Ports): Klar definierte Repository-Interfaces in repositories.py
•	Datenhaltung: SQLAlchemy-Models und SQLite in db
Die Ports/Contracts Pattern ist bereits dokumentiert und implementiert.

Kriterium 5: Wo wurden Contracts oder klar definierte Schnittstellen dokumentiert?
Die Contracts sind bereits implementiert:
•	repositories.py definiert die Schnittstellen: BookRepository, MovementRepository, SupplierRepository, etc.
•	Die API-Schemas sind in schemas.py definiert
•	Die Domain Models sind in models.py klart strukturiert
•	Die Dokumentation könnte noch ausführlicher sein, aber die Grundstruktur ist sehr ausbauungsfähig und nachvollziehbar.

Kriterium 6: Welche technische Stärke des Projekts ist euch besonders aufgefallen?
Stärken:
•	Saubere hexagonale/Ports-and-Adapters-Architektur ist bereits erkennbar
•	Protocol-basierte Contracts in Python zeigen gutes Verständnis von abstrakten Schnittstellen
•	FastAPI mit SQLAlchemy ist gut gewählt und modern
•	Frontend ist mit React und Vite performant aufgebaut
•	Docker-Compose ist bereits vorhanden – das zeigt Deployment-Verständnis
•	Die einzelnen Komponenten sind gut voneinander getrennt
Größtes technisches Risiko bis zur Endabgabe:
•	Merge-Konflikte: Mit mehreren Feature-Branches könnten Konflikte auf Main sehr schwer werden, wenn nicht koordiniert wird
•	Fehlende End-to-End-Tests: Die Integration zwischen Frontend und Backend ist kritisch
•	Unvollständige Features: Mehrere Funktionen sind angedeutet aber nicht vollständig umgesetzt (z.B. PDF-Report)
•	Datenbank-Migration: Falls das Schema ändern muss, könnte das problematisch werden

Kriterium 7: Wirkt die Commit-Historie aktiv und nachvollziehbar? Was würdest du hier noch verbessern?
Bewertung: Erledigt
Beobachtungen:
•	29 Commits auf allen Branches ist eine gute Anzahl für ein 4-5 Personen-Team
•	Die Historie hat längere Pausen (wohl Ferienwochen) – das ist verständlich
•	Manche Commits sind nachvollziehbar, andere könnten aussagekräftiger sein
Verbesserungen:
•	Mehr granulare Commits statt großer Feature-Commits
•	Aussagekräftigere Commit-Messages 
•	Häufigere kleine Merges auf Main statt großer Batches am Ende

Kriterium 8: Sind Beiträge verschiedener Teammitglieder erkennbar?
Bewertung: Gut gemacht
Ja, es ist sehr gut erkennbar:
•	Jedes Teammitglied hat seinen eigenen Feature-Branch mit aktuellen Changes
•	Die Unterschiedlichen Beiträge sind klar zuordbar (Backend, Frontend, Dokumentation)
•	Die Branch-Struktur zeigt gute Zusammenarbeit mit Git

Kriterium 9: Wie schätzt ihr den aktuellen Projektfortschritt ein? Welche Komponenten sind bereits funktionstüchtig?
Funktionsfähige Komponenten:
•	GUI: React-Frontend lädt und zeigt die Basis-UI (Navigation, Seiten-Struktur)
•	Backend-API: FastAPI startet, Endpoints sind definiert und getestet
•	Datenbankstruktur: SQLite mit SQLAlchemy Models ist vollständig
•	Geschäftslogik: Basis-Services für Bücher, Lagerbestand, Lieferanten funktionieren
•	Docker-Setup: Backend und Frontend können containerisiert werden
Noch nicht vollständig integriert:
•	Alle Frontend-Funktionen müssen noch mit der API verbunden werden
•	Erweiterte Features wie PDF-Reports noch nicht vollständig getestet

Kriterium 10: Welche Frage würdet ihr dem Team als Code-Reviewer stellen?
"Ihr habt bereits Docker-Compose aufgesetzt – sehr gut! Eine Frage: Habt ihr ein Walking Skeleton geplant, also eine End-to-End-Integration, wo ein Benutzer eine komplette User Journey durchführen kann (z.B. Buch hinzufügen → Lagerbestand anpassen → PDF-Report erzeugen)? Das würde helfen, Integrationsprobleme früh zu erkennen, bevor alle Features vollständig sind."

Kriterium 11: Welchen konkreten Verbesserungsvorschlag würdet ihr dem Team geben?
"Mein Verbesserungsvorschlag:
1.	Walking Skeleton als nächster Priority: Baut eine komplette End-to-End-Funktionalität, damit ihr wisst, dass alle Schichten zusammenarbeiten (z.B. ein Buch vom Frontend hinzufügen → wird in DB gespeichert → wird in Frontend angezeigt).
2.	Contracts-Datei auf Main: Erstellt auf Main einen vollständigen contracts.py mit allen Ports und Interfaces. Das macht die Entwicklung viel strukturierter und reduziert Merge-Konflikte.
3.	Regelmäßige Merges statt großer Batches: Mergt öfter kleine, getestete Features auf Main, statt große Batches am Ende zusammenzufassen. Das reduziert Merge-Konflikte massiv.
4.	Test-Abdeckung erhöhen: Schreibt mindestens Unit-Tests für die Services und Integration-Tests für die API-Endpoints.
5.	Kleine, aussagekräftige Commits: Nutzt Präfixe wie feat:, fix:, refactor: in Commit-Messages. Das macht die Historie viel nachvollziehbarer.
Sonst: Das Projekt sieht sehr gut strukturiert aus, und die Nutzung von GitHub Branches und Docker zeigt echtes Verständnis. Mit den obigen Punkten wird es sehr solide."

Gesamtfeedback:
Das Projekt ist gut strukturiert, die Architektur ist sauber, und das Team arbeitet mit modernen Tools. Die Ports-and-Adapters-Architektur ist bereits erkennbar. Das größte Verbesserungspotential liegt in:
1.	Integration testen (Walking Skeleton)
2.	Merge-Strategie optimieren (häufiger mergen)
3.	Commit-Qualität erhöhen (aussagekräftigere Messages)


# Rollen und Workflows

Dieses Dokument beschreibt das Zielbild fuer Rollen, Oberflaechen und
Zustaendigkeiten im Projekt. Es soll helfen, neue Funktionen nicht ungeordnet in
ein einzelnes Menue zu bauen, sondern fachlich passend zuzuordnen.

## Grundentscheidung

MaterialZaehler soll langfristig eine gemeinsame Anwendung mit gemeinsamer
Fachlogik bleiben. Unterschiedliche Nutzergruppen sollen aber unterschiedliche
Oberflaechen und Funktionsbereiche bekommen.

Kurzfristig wird noch kein echtes Login- oder Rechtesystem gebaut. Stattdessen
werden Einstiegspunkte und Menues fachlich getrennt. Die gemeinsame Logik bleibt
in wiederverwendbaren Modulen.

Aktueller Ansatz:

- `materialZaehler.py`: Einstieg fuer die Baustelle
- `buero_panel.py`: Einstieg fuer Buero, Bestellung und Verwaltung
- gemeinsame Module fuer beide Einstiege:
  - `material_logik.py`
  - `datenspeicher.py`
  - JSON-Dateien als aktuelle Datenhaltung

## Rollen

### User / Baustelle

Der User ist der normale Anwender auf der Baustelle.

Typische Aufgaben:

- Materialbestand einer Baustelle ansehen
- Materialzugang erfassen
- Materialabgang erfassen
- Bestand korrigieren
- Materialbedarf als Bestellanfrage melden

Nicht im Fokus:

- Bestellanfragen bearbeiten oder abschliessen
- Baustellen zentral verwalten
- Stammdaten pflegen
- Gesamtuebersichten oder Auswertungen
- technische Einstellungen

### Buero

Der Buero-Nutzer bearbeitet organisatorische Aufgaben rund um Baustellen,
Bestellungen und Materialverwaltung.

Typische Aufgaben:

- Bestellanfragen ansehen
- Bestellanfragen bearbeiten
- Bestellstatus aendern
- Baustellen anlegen, umbenennen oder stilllegen
- organisatorische Materialdaten pflegen
- offene Bedarfe ueberwachen

Nicht im Fokus:

- technische Systemverwaltung
- direkte Server-, Datenbank- oder Benutzerverwaltung
- reine Baustellen-Erfassung vor Ort

### Chef

Der Chef braucht Uebersicht, Auswertung und Kontrolle, aber nicht zwingend alle
Bearbeitungsfunktionen im Tagesgeschaeft.

Typische Aufgaben:

- Gesamtuebersicht ueber Baustellen
- Materialbestaende ueber alle Standorte betrachten
- offene Bestellanfragen sehen
- kritische Bestaende erkennen
- Materialbewegungen auswerten
- Kennzahlen und Berichte abrufen

Nicht im Fokus:

- technische Einstellungen
- kleinteilige Buchungen vor Ort

### Admin

Der Admin ist eine technische Rolle fuer Betrieb, Datenpflege und spaetere
Systemverwaltung.

Typische Aufgaben:

- Benutzer und Rollen verwalten, sobald ein Login existiert
- technische Konfiguration pflegen
- Datenmigrationen oder Datenreparaturen ausfuehren
- Systemzustand pruefen
- Import- und Exportfunktionen verwalten

Nicht im Fokus:

- operative Baustellenarbeit
- normale Bestellbearbeitung
- Chef-Auswertungen als Tagesgeschaeft

## Funktionszuordnung

| Funktion | User | Buero | Chef | Admin |
| --- | --- | --- | --- | --- |
| Materialbestand einer Baustelle anzeigen | ja | ja | ja | ja |
| Materialzugang buchen | ja | ja | nein | nein |
| Materialabgang buchen | ja | ja | nein | nein |
| Bestandskorrektur buchen | ja | ja | eingeschraenkt | nein |
| Bestellanfrage erstellen | ja | ja | nein | nein |
| Bestellanfragen anzeigen | eingeschraenkt | ja | ja | ja |
| Bestellanfrage bearbeiten | nein | ja | eingeschraenkt | nein |
| Baustelle anlegen | nein | ja | nein | ja |
| Baustelle umbenennen | nein | ja | nein | ja |
| Materialbewegungen auswerten | nein | ja | ja | ja |
| Benutzer verwalten | nein | nein | nein | ja |
| technische Konfiguration | nein | nein | nein | ja |

## Geplante Oberflaechen

### Baustellen-CLI

Bestehender Einstieg:

```powershell
python materialZaehler.py
```

Diese Oberflaeche bleibt auf schnelle Eingaben vor Ort ausgerichtet. Sie soll
nicht mit Buero- oder Admin-Funktionen ueberladen werden.

### Buero-Panel

Bestehender Einstieg:

```powershell
python buero_panel.py
```

Das Buero-Panel ist zunaechst ebenfalls eine CLI. Es kann spaeter durch eine
Weboberflaeche oder GUI ersetzt werden, ohne die Fachlogik neu zu schreiben.

Aktuelle Kernfunktionen:

1. Bestellanfragen anzeigen
2. Bestellanfrage-Status aendern
3. Baustellen anzeigen
4. Baustelle anlegen
5. Baustelle umbenennen
6. Zurueck oder beenden

## Bestellanfragen im Zielbild

Bestellanfragen entstehen typischerweise aus der Baustelle oder dem Buero.
Bearbeitet werden sie hauptsaechlich im Buero-Panel.

Sinnvolle Statuswerte:

- `offen`
- `bestellt`
- `geliefert`
- `abgeschlossen`
- `storniert`

Eine gelieferte Bestellanfrage soll nicht automatisch den Bestand veraendern,
solange keine klare Wareneingangslogik existiert. Die Materialbuchung sollte
bewusst als Zugang erfolgen, damit Menge, Einheit und Ziel geprueft werden.

## Entwicklungsregeln fuer neue Features

- Neue Funktionen zuerst einer Rolle zuordnen.
- Baustellen-Funktionen bleiben schlank und schnell bedienbar.
- Buero-, Chef- und Admin-Funktionen kommen nicht unkontrolliert in das
  Baustellen-Menue.
- Fachlogik wird in `material_logik.py` oder passenden neuen Logikmodulen
  umgesetzt, nicht direkt in CLI-Menues versteckt.
- Datenspeicherung bleibt in `datenspeicher.py` oder einer spaeteren
  Datenzugriffsschicht.
- Neue Logik wird mit Tests abgesichert.
- README beschreibt den aktuellen Projektstand; detaillierte Rollen- und
  Workflow-Entscheidungen stehen in diesem Dokument.

## Offene Entscheidungen

- Wann wird ein echtes Login- und Rechtesystem eingefuehrt?
- Bleibt das Buero-Panel mittelfristig CLI oder wird es zuerst als Weboberflaeche
  gebaut?
- Welche Funktionen darf die Chef-Rolle nur lesen und welche aktiv bearbeiten?
- Wie wird ein Wareneingang aus einer Bestellanfrage sauber in eine
  Materialbuchung ueberfuehrt?
- Wann wird die JSON-Datenhaltung durch eine Datenbank ersetzt?

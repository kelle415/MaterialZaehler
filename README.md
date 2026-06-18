# MaterialZaehler

MaterialZaehler ist eine lokale Kommandozeilenanwendung zur Verwaltung von
Materialbestaenden je Baustelle oder Standort. Das Projekt speichert den
aktuellen Datenstand in JSON-Dateien und ist so aufgebaut, dass Eingabelogik,
Fachlogik und Datenspeicherung getrennt weiterentwickelt werden koennen.

## Aktueller Funktionsumfang

- Material fuer Baustellen oder Standorte erfassen
- Materiallisten pro Baustelle anzeigen
- Materialnamen, Mengen und Einheiten aendern
- Baustellen umbenennen
- Firmenlager automatisch sicherstellen und anzeigen
- Bestellanfragen erfassen und anzeigen
- Tippfehler-Abgleich fuer Baustellen- und Standortnamen
- Automatisierte Tests fuer Fachlogik, Datenspeicherung und Eingabehelfer

## Projektstatus

Das Projekt ist aktuell eine lokale CLI-Anwendung. Die Datenhaltung erfolgt in
JSON-Dateien im Projektverzeichnis. Es gibt noch keine Benutzerverwaltung, keine
API, keine grafische Oberflaeche und keine echte Datenbankanbindung.

Die Struktur ist bewusst einfach gehalten, damit spaeter eine Datenbank, eine
Weboberflaeche oder eine API ergaenzt werden koennen, ohne die komplette
Fachlogik neu zu schreiben.

## Voraussetzungen

- Python 3.10 oder neuer
- Git

Es werden aktuell keine externen Python-Pakete benoetigt.

## Installation

Repository klonen:

```powershell
git clone <repository-url>
cd MaterialZaehler
```

Optional kann eine virtuelle Umgebung genutzt werden:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Anwendung starten

```powershell
python materialZaehler.py
```

Nach dem Start fuehrt das Hauptmenue durch die vorhandenen Funktionen:

1. Material eintragen
2. Material Liste anzeigen
3. Material aendern
4. Lager anzeigen
5. Material bestellen
6. Beenden

## Baustellen-Suche und Tippfehler-Abgleich

Bei Eingaben von Baustellen oder Standorten wird die Eingabe mit bekannten
Baustellen abgeglichen. Wenn ein aehnlicher Name gefunden wird, fragt das
Programm nach:

```text
Meintest du "Bielefeld"? (75% Uebereinstimmung) (J/N)
```

Wird der Vorschlag bestaetigt, verwendet das Programm den bekannten Namen. Wird
er abgelehnt, bleibt je nach Kontext entweder die freie Eingabe erlaubt oder es
wird erneut gefragt.

Der Abgleich wird fuer Baustellen- und Standort-Eingaben genutzt, nicht fuer
Materialnamen. Materialnamen bleiben bewusst frei, weil dort Abweichungen haeufig
fachlich gewollt sein koennen.

## Datenhaltung

Die Anwendung nutzt aktuell zwei JSON-Dateien:

- `baustellenListe.json`: Baustellen, Lager und Materialbestaende
- `bestellanfragen.json`: offene oder gespeicherte Bestellanfragen

Beispiel fuer eine Baustelle:

```json
{
  "Bielefeld": {
    "Material": {
      "Zement": {
        "Menge": 200,
        "Einheit": "kg"
      }
    }
  }
}
```

Beispiel fuer eine Bestellanfrage:

```json
{
  "id": 1,
  "ziel": "Bielefeld",
  "material": "Zement",
  "menge": 20,
  "einheit": "kg",
  "status": "offen"
}
```

## Projektstruktur

```text
MaterialZaehler/
|-- materialZaehler.py              # CLI, Menues und Benutzereingaben
|-- material_logik.py               # Fachlogik fuer Material, Baustellen, Suche
|-- datenspeicher.py                # Laden und Speichern der JSON-Dateien
|-- baustellenListe.json            # Aktuelle Baustellen- und Materialdaten
|-- bestellanfragen.json            # Aktuelle Bestellanfragen
`-- tests/
    |-- test_material_logik.py
    |-- test_material_zaehler_helpers.py
    `-- test_datenspeicher.py
```

## Tests ausfuehren

```powershell
python -m unittest discover -s tests
```

Die Tests decken unter anderem ab:

- Material eintragen und aktualisieren
- Baustellen und Material umbenennen
- Mengen und Einheiten aendern
- Bestellanfragen erstellen
- JSON-Daten laden und speichern
- Baustellen-Vorschlaege bei Tippfehlern
- CLI-Helfer fuer Eingaben


## Bekannte Einschraenkungen

- Keine gleichzeitige Bearbeitung durch mehrere Benutzer
- Keine Zugriffskontrolle oder Benutzerrollen
- Keine Historie fuer Materialbewegungen
- Keine Validierung gegen zentrale Artikel- oder Baustellenstammdaten
- JSON-Dateien sind fuer produktive Mehrbenutzer-Szenarien nur begrenzt geeignet

## Naechste sinnvolle Erweiterungen

- Materialbewegungen protokollieren
- Bestellanfragen mit Statuswechseln erweitern
- Import und Export fuer CSV oder Excel
- Datenbankanbindung vorbereiten
- API-Schicht ergaenzen
- Benutzeroberflaeche fuer produktive Nutzung entwickeln
- Zentrale Konfiguration fuer Dateipfade und Umgebung einfuehren

## Entwicklungsstandard

Vor jedem Commit sollten die Tests ausgefuehrt werden:

```powershell
python -m unittest discover -s tests
```

Neue Features sollten mindestens einen Test fuer die Fachlogik enthalten. Wenn
Benutzereingaben betroffen sind, sollte zusaetzlich ein Test fuer die jeweilige
CLI-Hilfsfunktion ergaenzt werden.

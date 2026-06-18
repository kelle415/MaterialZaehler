# MaterialZaehler

MaterialZaehler ist eine lokale Kommandozeilenanwendung zur Verwaltung von
Materialbestaenden je Baustelle oder Standort. Das Projekt speichert den
aktuellen Datenstand in JSON-Dateien und ist so aufgebaut, dass Eingabelogik,
Fachlogik und Datenspeicherung getrennt weiterentwickelt werden koennen.

## Aktueller Funktionsumfang

- Material fuer Baustellen oder Standorte buchen
- Zugang, Abgang und Bestandskorrektur erfassen
- Materiallisten pro Baustelle anzeigen
- Materialnamen, Mengen und Einheiten aendern
- Baustellen umbenennen
- Firmenlager automatisch sicherstellen und anzeigen
- Bestellanfragen erfassen und anzeigen
- Bestellanfragen mit Statushistorie und Begruendung bearbeiten
- Gelieferte Bestellanfragen bewusst als Wareneingang buchen
- Materialbewegungen im Materialeintrag protokollieren
- Materialbewegungen im Buero-Panel anzeigen
- Chef-Panel mit Gesamtbestand, offenen Bestellungen und kritischen Bestaenden
- Mitarbeiterbestand je Baustelle pflegen
- Mitarbeiteranfragen fuer zusaetzliches Personal erfassen und anzeigen
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

Fuer die Anwendung selbst werden aktuell keine externen Python-Pakete benoetigt.
Fuer Entwicklung und Tests werden die in den Checkbefehlen genannten Werkzeuge
benoetigt, zum Beispiel `pytest`, `ruff`, `mypy`, `hypothesis`, `pytest-cov` und
`bandit`.

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

Baustellen-CLI:

```powershell
python materialZaehler.py
```

Nach dem Start fuehrt das Baustellen-Hauptmenue durch die vorhandenen Funktionen:

1. Material eintragen
2. Material Liste anzeigen
3. Material aendern
4. Lager anzeigen
5. Bedarf bestellen
6. Beenden

Buero-Panel:

```powershell
python buero_panel.py
```

Das Buero-Panel ist fuer organisatorische Aufgaben vorgesehen:

1. Bestellanfragen anzeigen
2. Bestellanfrage Status aendern
3. Baustellen anzeigen
4. Baustelle anlegen
5. Baustelle umbenennen
6. Materialbewegungen anzeigen
7. Mitarbeiterbestand eintragen
8. Mitarbeiteranfragen anzeigen
9. Beenden

Chef-Panel:

```powershell
python chef_panel.py
```

Das Chef-Panel buendelt die Gesamtuebersicht:

1. Chef-Uebersicht anzeigen
2. Gesamtbestand anzeigen
3. Offene Bestellungen anzeigen
4. Kritische oder leere Bestaende anzeigen
5. Baustelle anlegen
6. Mitarbeiterbestand eintragen
7. Mitarbeiteruebersicht anzeigen
8. Mitarbeiteranfragen anzeigen
9. Materialbewegungen anzeigen
10. Beenden

## Materialbuchungen

Material wird ueber Buchungsarten erfasst:

- `Zugang`: addiert die eingegebene Menge zum vorhandenen Bestand
- `Abgang`: zieht die eingegebene Menge vom vorhandenen Bestand ab
- `Korrektur`: setzt den Bestand bewusst auf die eingegebene Menge

Wenn ein Material noch nicht vorhanden ist, wird es bei Zugang oder Korrektur
neu angelegt. Ein Abgang fuer unbekanntes Material wird abgelehnt. Ein Abgang,
der den Bestand unter 0 setzen wuerde, wird ebenfalls abgelehnt.
Eine Korrektur darf den Bestand auch auf 0 setzen.

Bei vorhandenem Material muss die eingegebene Einheit zur gespeicherten Einheit
passen. Dadurch werden versehentliche Mischungen wie `kg` und `Stk` verhindert.

## Bestellanfragen und Wareneingang

Bestellanfragen haben einen Status und eine `statusHistorie`. Jeder
Statuswechsel speichert den alten Status, den neuen Status, den Zeitpunkt und
den angegebenen Grund.

Wenn eine Bestellanfrage im Buero-Panel auf `geliefert` gesetzt wird, fragt das
Programm bewusst nach, ob der Wareneingang jetzt in den Zielbestand gebucht
werden soll. Bei Bestaetigung wird ein Materialzugang am Zielstandort angelegt
und die Materialbewegung bekommt eine Referenz auf die Bestellanfrage.

## Materialbewegungen

Materialbewegungen werden pro Material gespeichert und im Buero-Panel
standortuebergreifend angezeigt. Die Anzeige enthaelt Zeitpunkt, Standort,
Material, Buchungsart, Menge, Einheit sowie Bestand vorher und nachher. Wenn
eine Bewegung aus einem Wareneingang stammt, wird die Bestellanfrage als Referenz
angezeigt.

## Chef-Uebersicht

Das Chef-Panel ist ein eigener CLI-Einstieg fuer Gesamtuebersichten. Es zeigt
die Anzahl der Baustellen, zusammengefasste Materialbestaende, offene
Bestellungen, kritische oder leere Bestaende, Mitarbeiter je Baustelle und offene
Mitarbeiteranfragen.

Kritische Bestaende werden aktuell erkannt, wenn die Menge `0` oder kleiner ist
oder wenn ein Material spaeter einen `Mindestbestand` bekommt und die aktuelle
Menge diesen Wert erreicht oder unterschreitet.

## Mitarbeiter und Personalbedarf

Baustellen koennen einen Mitarbeiterbestand speichern:

```json
{
  "Mitarbeiter": {
    "Anzahl": 6,
    "Aktualisiert": "2026-06-18T09:00:00+00:00",
    "Notiz": "Rohbau"
  }
}
```

Chef und Buero koennen diesen Bestand eintragen. Der normale Baustellen-User
kann im Bedarf-Menue zusaetzliche Mitarbeiter anfragen. Diese Anfragen werden in
`mitarbeiteranfragen.json` gespeichert und im Buero- sowie Chef-Panel angezeigt.

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

Die Anwendung nutzt aktuell drei JSON-Dateien:

- `baustellenListe.json`: Baustellen, Lager und Materialbestaende
- `bestellanfragen.json`: offene oder gespeicherte Bestellanfragen
- `mitarbeiteranfragen.json`: offene oder gespeicherte Mitarbeiteranfragen

Beispiel fuer eine Baustelle:

```json
{
  "Bielefeld": {
    "Typ": "Baustelle",
    "Mitarbeiter": {
      "Anzahl": 6,
      "Aktualisiert": "2026-06-18T09:00:00+00:00",
      "Notiz": "Rohbau"
    },
    "Material": {
      "Zement": {
        "Menge": 200,
        "Einheit": "kg",
        "Bewegungen": [
          {
            "Art": "zugang",
            "Menge": 200,
            "Einheit": "kg",
            "BestandVorher": 0,
            "BestandNachher": 200,
            "Zeitpunkt": "2026-06-18T09:00:00+00:00",
            "Referenz": "Bestellanfrage #1",
            "Notiz": "Wareneingang"
          }
        ]
      }
    }
  }
}
```

Beispiel fuer eine Mitarbeiteranfrage:

```json
{
  "id": 1,
  "ziel": "Bielefeld",
  "anzahl": 3,
  "rolle": "Maurer",
  "grund": "Termin zieht an",
  "status": "offen",
  "erstelltAm": "2026-06-18T09:00:00+00:00",
  "statusHistorie": [
    {
      "von": null,
      "zu": "offen",
      "zeitpunkt": "2026-06-18T09:00:00+00:00",
      "grund": "Mitarbeiteranfrage erstellt"
    }
  ]
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
  "status": "geliefert",
  "statusHistorie": [
    {
      "von": null,
      "zu": "offen",
      "zeitpunkt": "2026-06-18T08:00:00+00:00",
      "grund": "Bestellanfrage erstellt"
    },
    {
      "von": "offen",
      "zu": "geliefert",
      "zeitpunkt": "2026-06-18T09:00:00+00:00",
      "grund": "Lieferung angekommen"
    }
  ],
  "wareneingang": {
    "gebucht": true,
    "zeitpunkt": "2026-06-18T09:00:00+00:00",
    "ziel": "Bielefeld",
    "material": "Zement",
    "menge": 20,
    "einheit": "kg"
  }
}
```

## Projektstruktur

```text
MaterialZaehler/
|-- materialZaehler.py              # CLI, Menues und Benutzereingaben
|-- buero_panel.py                  # CLI fuer Buero- und Verwaltungsaufgaben
|-- chef_panel.py                   # CLI fuer Chef-Uebersicht und Steuerung
|-- cli_helpers.py                  # Wiederverwendbare CLI-Eingabehelfer
|-- material_logik.py               # Fachlogik fuer Material, Baustellen, Suche
|-- datenspeicher.py                # Laden und Speichern der JSON-Dateien
|-- baustellenListe.json            # Aktuelle Baustellen- und Materialdaten
|-- bestellanfragen.json            # Aktuelle Bestellanfragen
|-- mitarbeiteranfragen.json        # Mitarbeiteranfragen, falls vorhanden
|-- docs/
|   `-- rollen-und-workflows.md     # Rollen, Oberflaechen und Ziel-Workflows
`-- tests/
    |-- test_material_logik.py
    |-- test_material_zaehler_helpers.py
    |-- test_chef_panel.py
    |-- test_buero_panel.py
    `-- test_datenspeicher.py
```

## Weitere Dokumentation

- `docs/rollen-und-workflows.md`: Zielbild fuer Rollen, Oberflaechen,
  Zustaendigkeiten und kuenftige Workflows

## Tests ausfuehren

```powershell
python -m pytest
```

Die Tests decken unter anderem ab:

- Material eintragen und aktualisieren
- Zugang, Abgang und Korrektur von Material
- Baustellen und Material umbenennen
- Mengen und Einheiten aendern
- Bestellanfragen erstellen
- Bestellanfragen mit Statushistorie und Wareneingang buchen
- Chef-Uebersicht erstellen
- Mitarbeiterbestand und Mitarbeiteranfragen verwalten
- Materialbewegungen sammeln und im Buero-Panel anzeigen
- rollenuebergreifende Nutzer-Workflows von Baustelle ueber Buero bis Chef
- JSON-Daten laden und speichern
- Baustellen-Vorschlaege bei Tippfehlern
- CLI-Helfer fuer Eingaben

Die Entwicklungswerkzeuge sind in `pyproject.toml` konfiguriert. Fuer einen
vollstaendigen lokalen Checklauf:

```powershell
python -m ruff check .
python -m mypy .
python -m pytest
python -m bandit -r .
```

## Bekannte Einschraenkungen

- Keine gleichzeitige Bearbeitung durch mehrere Benutzer
- Keine Zugriffskontrolle oder Benutzerrollen
- Noch keine Filter oder Auswertungen fuer Materialbewegungen
- Mitarbeiteranfragen haben noch keine eigene Statusbearbeitung
- Keine Validierung gegen zentrale Artikel- oder Baustellenstammdaten
- JSON-Dateien sind fuer produktive Mehrbenutzer-Szenarien nur begrenzt geeignet

## Naechste sinnvolle Erweiterungen

- Materialbewegungen filtern und auswerten
- Mitarbeiteranfragen im Buero- oder Chef-Panel einplanen und abschliessen
- Import und Export fuer CSV oder Excel
- Datenbankanbindung vorbereiten
- API-Schicht ergaenzen
- Benutzeroberflaeche fuer produktive Nutzung entwickeln
- Zentrale Konfiguration fuer Dateipfade und Umgebung einfuehren

## Entwicklungsstandard

Vor jedem Commit sollten die Qualitaetschecks ausgefuehrt werden:

```powershell
python -m ruff check .
python -m mypy .
python -m pytest
python -m bandit -r .
```

Neue Features sollten mindestens einen Test fuer die Fachlogik enthalten. Wenn
Benutzereingaben betroffen sind, sollte zusaetzlich ein Test fuer die jeweilige
CLI-Hilfsfunktion ergaenzt werden.

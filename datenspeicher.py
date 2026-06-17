import json
from pathlib import Path


STANDARD_DATEIPFAD = Path(__file__).with_name("baustellenListe.json")
BESTELLANFRAGEN_DATEIPFAD = Path(__file__).with_name("bestellanfragen.json")


def baustellen_laden(dateipfad=STANDARD_DATEIPFAD):
    dateipfad = Path(dateipfad)
    with dateipfad.open("r", encoding="utf-8") as datei:
        return json.load(datei)


def baustellen_speichern(baustellen_liste, dateipfad=STANDARD_DATEIPFAD):
    dateipfad = Path(dateipfad)
    with dateipfad.open("w", encoding="utf-8") as datei:
        json.dump(baustellen_liste, datei, indent=4, ensure_ascii=False)


def bestellanfragen_laden(dateipfad=BESTELLANFRAGEN_DATEIPFAD):
    dateipfad = Path(dateipfad)
    if not dateipfad.exists():
        return []

    with dateipfad.open("r", encoding="utf-8") as datei:
        bestellanfragen = json.load(datei)

    if not isinstance(bestellanfragen, list):
        raise ValueError("bestellanfragen.json muss eine Liste enthalten")

    return bestellanfragen


def bestellanfragen_speichern(
    bestellanfragen_liste, dateipfad=BESTELLANFRAGEN_DATEIPFAD
):
    dateipfad = Path(dateipfad)
    with dateipfad.open("w", encoding="utf-8") as datei:
        json.dump(bestellanfragen_liste, datei, indent=4, ensure_ascii=False)

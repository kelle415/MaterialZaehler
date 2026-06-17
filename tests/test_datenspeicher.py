import json
import tempfile
import unittest
from pathlib import Path

from datenspeicher import (
    baustellen_laden,
    baustellen_speichern,
    bestellanfragen_laden,
    bestellanfragen_speichern,
)


PROJEKT_ROOT = Path(__file__).resolve().parents[1]


def temporaeres_testverzeichnis():
    return tempfile.TemporaryDirectory(dir=PROJEKT_ROOT)


class DatenspeicherTests(unittest.TestCase):
    def test_baustellen_speichern_und_laden(self):
        daten = {
            "Köln": {
                "Material": {
                    "Beton": {"Menge": 1000, "Einheit": "kg"},
                }
            }
        }

        with temporaeres_testverzeichnis() as ordner:
            dateipfad = Path(ordner) / "baustellenListe.json"

            baustellen_speichern(daten, dateipfad)
            geladene_daten = baustellen_laden(dateipfad)

        self.assertEqual(geladene_daten, daten)

    def test_bestellanfragen_laden_gibt_leere_liste_bei_fehlender_datei_zurueck(self):
        with temporaeres_testverzeichnis() as ordner:
            dateipfad = Path(ordner) / "bestellanfragen.json"

            bestellanfragen = bestellanfragen_laden(dateipfad)

        self.assertEqual(bestellanfragen, [])

    def test_bestellanfragen_speichern_und_laden(self):
        daten = [
            {
                "id": 1,
                "ziel": "Bielefeld",
                "material": "Zement",
                "menge": 20,
                "einheit": "kg",
                "status": "offen",
            }
        ]

        with temporaeres_testverzeichnis() as ordner:
            dateipfad = Path(ordner) / "bestellanfragen.json"

            bestellanfragen_speichern(daten, dateipfad)
            geladene_daten = bestellanfragen_laden(dateipfad)

        self.assertEqual(geladene_daten, daten)

    def test_bestellanfragen_laden_lehnt_objekt_statt_liste_ab(self):
        with temporaeres_testverzeichnis() as ordner:
            dateipfad = Path(ordner) / "bestellanfragen.json"
            dateipfad.write_text(json.dumps({"id": 1}), encoding="utf-8")

            with self.assertRaises(ValueError):
                bestellanfragen_laden(dateipfad)


if __name__ == "__main__":
    unittest.main()

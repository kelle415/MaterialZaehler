import unittest
from unittest.mock import patch

from buero_panel import (
    baustelleAnlegen,
    baustelleUmbenennen,
    bestellanfrageStatusAendern,
    mitarbeiterbestandEintragen,
    materialbewegungenAnzeigen,
)


class BueroPanelTests(unittest.TestCase):
    def test_bestellanfrage_status_aendern_speichert_status(self):
        bestellanfragen = [{"id": 1, "status": "offen"}]

        with patch(
            "builtins.input",
            side_effect=["1", "2", "Beim Lieferanten bestellt"],
        ), patch(
            "builtins.print"
        ), patch("buero_panel.bestellanfragen_speichern") as speichern:
            erfolgreich = bestellanfrageStatusAendern(bestellanfragen)

        self.assertTrue(erfolgreich)
        self.assertEqual(bestellanfragen[0]["status"], "bestellt")
        self.assertEqual(
            bestellanfragen[0]["statusHistorie"][0]["grund"],
            "Beim Lieferanten bestellt",
        )
        speichern.assert_called_once_with(bestellanfragen)

    def test_bestellanfrage_status_geliefert_bucht_wareneingang(self):
        bestellanfragen = [
            {
                "id": 1,
                "ziel": "Bielefeld",
                "material": "Zement",
                "menge": 5,
                "einheit": "kg",
                "status": "bestellt",
            }
        ]
        baustellen = {
            "Bielefeld": {
                "Material": {
                    "Zement": {"Menge": 10, "Einheit": "kg"},
                }
            }
        }

        with patch(
            "builtins.input",
            side_effect=["1", "3", "Lieferung angekommen", "j"],
        ), patch("builtins.print"), patch(
            "buero_panel.bestellanfragen_speichern"
        ) as bestellungen_speichern, patch(
            "buero_panel.baustellen_speichern"
        ) as baustellen_speichern:
            erfolgreich = bestellanfrageStatusAendern(bestellanfragen, baustellen)

        self.assertTrue(erfolgreich)
        self.assertEqual(bestellanfragen[0]["status"], "geliefert")
        self.assertTrue(bestellanfragen[0]["wareneingang"]["gebucht"])
        self.assertEqual(baustellen["Bielefeld"]["Material"]["Zement"]["Menge"], 15)
        bestellungen_speichern.assert_called_once_with(bestellanfragen)
        baustellen_speichern.assert_called_once_with(baustellen)

    def test_bestellanfrage_status_aendern_ohne_bestellungen_speichert_nicht(self):
        bestellanfragen = []

        with patch("builtins.print"), patch(
            "buero_panel.bestellanfragen_speichern"
        ) as speichern:
            erfolgreich = bestellanfrageStatusAendern(bestellanfragen)

        self.assertFalse(erfolgreich)
        speichern.assert_not_called()

    def test_materialbewegungen_anzeigen_gibt_bewegungen_aus(self):
        baustellen = {
            "Bielefeld": {
                "Material": {
                    "Zement": {
                        "Menge": 10,
                        "Einheit": "kg",
                        "Bewegungen": [
                            {
                                "Art": "zugang",
                                "Menge": 10,
                                "Einheit": "kg",
                                "BestandVorher": 0,
                                "BestandNachher": 10,
                                "Zeitpunkt": "2026-01-01T10:00:00+00:00",
                            }
                        ],
                    }
                }
            }
        }

        with patch("builtins.print") as ausgabe:
            erfolgreich = materialbewegungenAnzeigen(baustellen)

        gedruckt = "\n".join(
            " ".join(str(wert) for wert in aufruf.args)
            for aufruf in ausgabe.call_args_list
        )
        self.assertTrue(erfolgreich)
        self.assertIn("Zement", gedruckt)
        self.assertIn("zugang 10 kg", gedruckt)

    def test_baustelle_anlegen_speichert_neue_baustelle(self):
        baustellen = {"Bielefeld": {"Material": {}}}

        with patch("builtins.input", return_value="Berlin"), patch(
            "builtins.print"
        ), patch("buero_panel.baustellen_speichern") as speichern:
            erfolgreich = baustelleAnlegen(baustellen)

        self.assertTrue(erfolgreich)
        self.assertEqual(baustellen["Berlin"]["Typ"], "Baustelle")
        self.assertEqual(baustellen["Berlin"]["Material"], {})
        self.assertEqual(baustellen["Berlin"]["Mitarbeiter"]["Anzahl"], 0)
        speichern.assert_called_once_with(baustellen)

    def test_mitarbeiterbestand_eintragen_speichert_baustelle(self):
        baustellen = {"Bielefeld": {"Material": {}}}

        with patch(
            "builtins.input",
            side_effect=["Bielefeld", "6", "Rohbau"],
        ), patch("builtins.print"), patch(
            "buero_panel.baustellen_speichern"
        ) as speichern:
            erfolgreich = mitarbeiterbestandEintragen(baustellen)

        self.assertTrue(erfolgreich)
        self.assertEqual(baustellen["Bielefeld"]["Mitarbeiter"]["Anzahl"], 6)
        speichern.assert_called_once_with(baustellen)

    def test_baustelle_umbenennen_speichert_geaenderten_namen(self):
        baustellen = {"Bielefeld": {"Material": {}}}

        with patch("builtins.input", side_effect=["Bielefeld", "Berlin", "j"]), patch(
            "builtins.print"
        ), patch("buero_panel.baustellen_speichern") as speichern:
            erfolgreich = baustelleUmbenennen(baustellen)

        self.assertTrue(erfolgreich)
        self.assertIn("Berlin", baustellen)
        self.assertNotIn("Bielefeld", baustellen)
        speichern.assert_called_once_with(baustellen)


if __name__ == "__main__":
    unittest.main()

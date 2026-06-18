import unittest
from unittest.mock import patch

from chef_panel import (
    baustelleAnlegen,
    chefUebersichtAnzeigen,
    mitarbeiteranfragenAnzeigen,
    mitarbeiterbestandEintragen,
)


class ChefPanelTests(unittest.TestCase):
    def test_chef_uebersicht_zeigt_zentrale_kennzahlen(self):
        baustellen = {
            "Bielefeld": {
                "Material": {
                    "Zement": {"Menge": 0, "Einheit": "kg"},
                },
                "Mitarbeiter": {"Anzahl": 4},
            }
        }
        bestellanfragen = [{"id": 1, "status": "offen"}]
        mitarbeiteranfragen = [{"id": 1, "status": "offen"}]

        with patch("builtins.print") as ausgabe:
            uebersicht = chefUebersichtAnzeigen(
                baustellen, bestellanfragen, mitarbeiteranfragen
            )

        gedruckt = "\n".join(
            " ".join(str(wert) for wert in aufruf.args)
            for aufruf in ausgabe.call_args_list
        )
        self.assertEqual(len(uebersicht["OffeneBestellanfragen"]), 1)
        self.assertIn("Offene Bestellungen: 1", gedruckt)
        self.assertIn("Mitarbeiteranfragen offen: 1", gedruckt)

    def test_baustelle_anlegen_speichert_neue_baustelle(self):
        baustellen = {}

        with patch("builtins.input", return_value="Berlin"), patch(
            "builtins.print"
        ), patch("chef_panel.baustellen_speichern") as speichern:
            erfolgreich = baustelleAnlegen(baustellen)

        self.assertTrue(erfolgreich)
        self.assertEqual(baustellen["Berlin"]["Material"], {})
        self.assertEqual(baustellen["Berlin"]["Mitarbeiter"]["Anzahl"], 0)
        speichern.assert_called_once_with(baustellen)

    def test_mitarbeiterbestand_eintragen_speichert_baustelle(self):
        baustellen = {"Bielefeld": {"Material": {}}}

        with patch(
            "builtins.input",
            side_effect=["Bielefeld", "7", "Dach"],
        ), patch("builtins.print"), patch(
            "chef_panel.baustellen_speichern"
        ) as speichern:
            erfolgreich = mitarbeiterbestandEintragen(baustellen)

        self.assertTrue(erfolgreich)
        self.assertEqual(baustellen["Bielefeld"]["Mitarbeiter"]["Anzahl"], 7)
        speichern.assert_called_once_with(baustellen)

    def test_mitarbeiteranfragen_anzeigen_gibt_offene_anfragen_aus(self):
        mitarbeiteranfragen = [
            {
                "id": 1,
                "ziel": "Bielefeld",
                "anzahl": 3,
                "rolle": "Maurer",
                "grund": "Termin",
                "status": "offen",
            }
        ]

        with patch("builtins.print") as ausgabe:
            erfolgreich = mitarbeiteranfragenAnzeigen(mitarbeiteranfragen)

        gedruckt = "\n".join(
            " ".join(str(wert) for wert in aufruf.args)
            for aufruf in ausgabe.call_args_list
        )
        self.assertTrue(erfolgreich)
        self.assertIn("Maurer", gedruckt)
        self.assertIn("Bielefeld", gedruckt)


if __name__ == "__main__":
    unittest.main()

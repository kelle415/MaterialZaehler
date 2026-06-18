import unittest
from unittest.mock import patch

from buero_panel import (
    baustelleAnlegen,
    baustelleUmbenennen,
    bestellanfrageStatusAendern,
)


class BueroPanelTests(unittest.TestCase):
    def test_bestellanfrage_status_aendern_speichert_status(self):
        bestellanfragen = [{"id": 1, "status": "offen"}]

        with patch("builtins.input", side_effect=["1", "2"]), patch(
            "builtins.print"
        ), patch("buero_panel.bestellanfragen_speichern") as speichern:
            erfolgreich = bestellanfrageStatusAendern(bestellanfragen)

        self.assertTrue(erfolgreich)
        self.assertEqual(bestellanfragen[0]["status"], "bestellt")
        speichern.assert_called_once_with(bestellanfragen)

    def test_bestellanfrage_status_aendern_ohne_bestellungen_speichert_nicht(self):
        bestellanfragen = []

        with patch("builtins.print"), patch(
            "buero_panel.bestellanfragen_speichern"
        ) as speichern:
            erfolgreich = bestellanfrageStatusAendern(bestellanfragen)

        self.assertFalse(erfolgreich)
        speichern.assert_not_called()

    def test_baustelle_anlegen_speichert_neue_baustelle(self):
        baustellen = {"Bielefeld": {"Material": {}}}

        with patch("builtins.input", return_value="Berlin"), patch(
            "builtins.print"
        ), patch("buero_panel.baustellen_speichern") as speichern:
            erfolgreich = baustelleAnlegen(baustellen)

        self.assertTrue(erfolgreich)
        self.assertEqual(baustellen["Berlin"], {"Typ": "Baustelle", "Material": {}})
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

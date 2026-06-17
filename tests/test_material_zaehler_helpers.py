import unittest
from unittest.mock import patch

from materialZaehler import ganzzahlAbfragen, istJa, istNein, textAbfragen


class MaterialZaehlerHelperTests(unittest.TestCase):
    def test_ist_ja_und_ist_nein_erkennen_eingaben(self):
        self.assertTrue(istJa("J"))
        self.assertTrue(istJa("ja"))
        self.assertFalse(istJa("nein"))
        self.assertTrue(istNein("N"))
        self.assertTrue(istNein("nein"))
        self.assertFalse(istNein("ja"))

    def test_ganzzahl_abfragen_wiederholt_bis_gueltige_zahl_eingegeben_wird(self):
        with (
            patch("builtins.input", side_effect=["abc", "0", "2"]),
            patch("builtins.print"),
        ):
            zahl = ganzzahlAbfragen("Menge: ", minimum=1)

        self.assertEqual(zahl, 2)

    def test_text_abfragen_wiederholt_bis_text_eingegeben_wird(self):
        with patch("builtins.input", side_effect=["", "Bielefeld"]), patch(
            "builtins.print"
        ):
            text = textAbfragen("Baustelle: ", "Bitte eingeben")

        self.assertEqual(text, "Bielefeld")


if __name__ == "__main__":
    unittest.main()

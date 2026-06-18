import unittest
from unittest.mock import patch

from materialZaehler import (
    baustelleAbfragen,
    baustellenNamenAenderungAbfragen,
    bestellDatenAbfragen,
    ganzzahlAbfragen,
    istJa,
    istNein,
    textAbfragen,
)


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

    def test_baustelle_abfragen_nutzt_bestaetigten_vorschlag(self):
        baustellen = {
            "Bielefeld": {"Material": {}},
            "Hamburg": {"Material": {}},
        }

        with patch("builtins.input", side_effect=["BIifeld", "j"]), patch(
            "builtins.print"
        ):
            baustelle = baustelleAbfragen(baustellen)

        self.assertEqual(baustelle, "Bielefeld")

    def test_baustelle_abfragen_erlaubt_neue_baustelle_nach_ablehnung(self):
        baustellen = {"Bielefeld": {"Material": {}}}

        with patch("builtins.input", side_effect=["BIifeld", "n"]), patch(
            "builtins.print"
        ):
            baustelle = baustelleAbfragen(baustellen)

        self.assertEqual(baustelle, "BIifeld")

    def test_baustelle_abfragen_wiederholt_bei_unbekanntem_standort(self):
        baustellen = {"Bielefeld": {"Material": {}}}

        with patch("builtins.input", side_effect=["Berlin", "Bielefeld"]), patch(
            "builtins.print"
        ):
            baustelle = baustelleAbfragen(baustellen, neueBaustelleErlaubt=False)

        self.assertEqual(baustelle, "Bielefeld")

    def test_bestell_daten_abfragen_nutzt_baustellen_vorschlag_fuer_ziel(self):
        baustellen = {"Bielefeld": {"Material": {}}}

        with patch(
            "builtins.input",
            side_effect=["BIifeld", "j", "Zement", "5", "kg"],
        ), patch("builtins.print"):
            ziel, materialname, materialmenge, materialeinheit = bestellDatenAbfragen(
                baustellen
            )

        self.assertEqual(ziel, "Bielefeld")
        self.assertEqual(materialname, "Zement")
        self.assertEqual(materialmenge, 5)
        self.assertEqual(materialeinheit, "kg")

    def test_baustellen_namen_aenderung_abfragen_nutzt_vorschlag(self):
        baustellen = {"Bielefeld": {"Material": {}}}

        with patch(
            "builtins.input",
            side_effect=["BIifeld", "j", "Berlin", "j"],
        ), patch("builtins.print"):
            zuaendern, geandert, sicherheitsfrage, materialname = (
                baustellenNamenAenderungAbfragen(baustellen)
            )

        self.assertEqual(zuaendern, "Bielefeld")
        self.assertEqual(geandert, "Berlin")
        self.assertEqual(sicherheitsfrage, "j")
        self.assertIsNone(materialname)


if __name__ == "__main__":
    unittest.main()

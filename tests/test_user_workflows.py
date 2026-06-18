import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import buero_panel
import chef_panel
import materialZaehler
from datenspeicher import (
    baustellen_laden,
    baustellen_speichern,
    bestellanfragen_laden,
    bestellanfragen_speichern,
    mitarbeiteranfragen_laden,
    mitarbeiteranfragen_speichern,
)
from material_logik import (
    baustelle_anlegen,
    bestellanfrage_erstellen,
    bestellanfrage_wareneingang_buchen,
    chef_uebersicht_erstellen,
    material_eintragen,
    mitarbeiteranfrage_erstellen,
    mitarbeiterbestand_setzen,
)


PROJEKT_ROOT = Path(__file__).resolve().parents[1]


def gedruckten_text(ausgabe):
    return "\n".join(
        " ".join(str(wert) for wert in aufruf.args)
        for aufruf in ausgabe.call_args_list
    )


class UserWorkflowTests(unittest.TestCase):
    def test_baustelle_buero_chef_workflow_von_bedarf_bis_uebersicht(self):
        baustellen = {
            "Bielefeld": {
                "Typ": "Baustelle",
                "Material": {},
                "Mitarbeiter": {"Anzahl": 2},
            }
        }
        bestellanfragen = []
        mitarbeiteranfragen = []

        with patch(
            "builtins.input",
            side_effect=[
                "5",
                "1",
                "Bielefeld",
                "Zement",
                "25",
                "kg",
                "j",
                "j",
                "5",
                "2",
                "Bielefeld",
                "3",
                "Maurer",
                "Termin zieht an",
                "j",
                "n",
                "j",
            ],
        ), patch("builtins.print"), patch(
            "materialZaehler.bestellanfragen_speichern"
        ) as bestellungen_speichern, patch(
            "materialZaehler.baustellen_speichern"
        ) as baustellen_speichern, patch(
            "materialZaehler.mitarbeiteranfragen_laden",
            return_value=mitarbeiteranfragen,
        ), patch(
            "materialZaehler.mitarbeiteranfragen_speichern"
        ) as personal_speichern:
            with self.assertRaises(SystemExit):
                materialZaehler.menueverweis(baustellen, bestellanfragen)

        self.assertEqual(len(bestellanfragen), 1)
        self.assertEqual(bestellanfragen[0]["material"], "Zement")
        self.assertEqual(len(mitarbeiteranfragen), 1)
        self.assertEqual(mitarbeiteranfragen[0]["rolle"], "Maurer")
        bestellungen_speichern.assert_called()
        personal_speichern.assert_called_once_with(mitarbeiteranfragen)
        baustellen_speichern.assert_called()

        with patch(
            "builtins.input",
            side_effect=[
                "2",
                "1",
                "3",
                "Lieferung angekommen",
                "j",
                "9",
            ],
        ), patch("builtins.print"), patch(
            "buero_panel.bestellanfragen_speichern"
        ) as buero_bestellungen_speichern, patch(
            "buero_panel.baustellen_speichern"
        ) as buero_baustellen_speichern, patch(
            "buero_panel.mitarbeiteranfragen_speichern"
        ) as buero_personal_speichern:
            with self.assertRaises(SystemExit):
                buero_panel.bueroMenue(
                    baustellen, bestellanfragen, mitarbeiteranfragen
                )

        self.assertEqual(bestellanfragen[0]["status"], "geliefert")
        self.assertEqual(baustellen["Bielefeld"]["Material"]["Zement"]["Menge"], 25)
        bewegung = baustellen["Bielefeld"]["Material"]["Zement"]["Bewegungen"][0]
        self.assertEqual(bewegung["Referenz"], "Bestellanfrage #1")
        buero_bestellungen_speichern.assert_called()
        buero_baustellen_speichern.assert_called()
        buero_personal_speichern.assert_called_once_with(mitarbeiteranfragen)

        with patch("builtins.input", side_effect=["1", "10"]), patch(
            "builtins.print"
        ) as ausgabe, patch("chef_panel.baustellen_speichern"), patch(
            "chef_panel.bestellanfragen_speichern"
        ), patch(
            "chef_panel.mitarbeiteranfragen_speichern"
        ):
            with self.assertRaises(SystemExit):
                chef_panel.chefMenue(baustellen, bestellanfragen, mitarbeiteranfragen)

        text = gedruckten_text(ausgabe)
        self.assertIn("Offene Bestellungen: 0", text)
        self.assertIn("Mitarbeiteranfragen offen: 1", text)
        self.assertIn("- Bielefeld: 2", text)

    def test_daten_bleiben_nach_realem_speichern_und_laden_konsistent(self):
        baustellen = {}
        bestellanfragen = []
        mitarbeiteranfragen = []

        erfolgreich, _ = baustelle_anlegen(baustellen, "Berlin")
        self.assertTrue(erfolgreich)
        erfolgreich, _ = mitarbeiterbestand_setzen(
            baustellen, "Berlin", 5, "Startteam"
        )
        self.assertTrue(erfolgreich)
        erfolgreich, _ = material_eintragen(baustellen, "Berlin", "Holz", 10, "m")
        self.assertTrue(erfolgreich)
        erfolgreich, _, bestellung = bestellanfrage_erstellen(
            bestellanfragen, "Berlin", "Holz", 15, "m"
        )
        self.assertTrue(erfolgreich)
        erfolgreich, _, personalbedarf = mitarbeiteranfrage_erstellen(
            mitarbeiteranfragen, "Berlin", 2, "Zimmerer", "Dachstuhl"
        )
        self.assertTrue(erfolgreich)
        erfolgreich, _, _ = bestellanfrage_wareneingang_buchen(
            bestellanfragen, baustellen, bestellung["id"], "Lieferung komplett"
        )
        self.assertTrue(erfolgreich)

        with tempfile.TemporaryDirectory(dir=PROJEKT_ROOT) as ordner:
            ordner = Path(ordner)
            baustellen_datei = ordner / "baustellenListe.json"
            bestellungen_datei = ordner / "bestellanfragen.json"
            personal_datei = ordner / "mitarbeiteranfragen.json"

            baustellen_speichern(baustellen, baustellen_datei)
            bestellanfragen_speichern(bestellanfragen, bestellungen_datei)
            mitarbeiteranfragen_speichern(mitarbeiteranfragen, personal_datei)

            geladene_baustellen = baustellen_laden(baustellen_datei)
            geladene_bestellungen = bestellanfragen_laden(bestellungen_datei)
            geladene_personalanfragen = mitarbeiteranfragen_laden(personal_datei)

        self.assertEqual(geladene_baustellen["Berlin"]["Mitarbeiter"]["Anzahl"], 5)
        self.assertEqual(geladene_baustellen["Berlin"]["Material"]["Holz"]["Menge"], 25)
        self.assertEqual(geladene_bestellungen[0]["status"], "geliefert")
        self.assertTrue(geladene_bestellungen[0]["wareneingang"]["gebucht"])
        self.assertEqual(geladene_personalanfragen[0]["id"], personalbedarf["id"])

        uebersicht = chef_uebersicht_erstellen(
            geladene_baustellen, geladene_bestellungen, geladene_personalanfragen
        )
        self.assertEqual(len(uebersicht["OffeneBestellanfragen"]), 0)
        self.assertEqual(len(uebersicht["OffeneMitarbeiteranfragen"]), 1)
        self.assertEqual(uebersicht["Gesamtbestand"][0]["Gesamtmenge"], 25)


if __name__ == "__main__":
    unittest.main()

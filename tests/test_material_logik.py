import unittest

from material_logik import (
    FIRMENLAGER_NAME,
    baustelle_umbenennen,
    baustellen_namen,
    bestellanfrage_erstellen,
    einheit_aendern,
    lager_sicherstellen,
    material_eintragen,
    material_namen,
    material_umbenennen,
    materialien_fuer_baustelle,
    menge_aendern,
    mengen_und_einheiten,
)


def beispiel_baustellen():
    return {
        "Bielefeld": {
            "Material": {
                "Zement": {"Menge": 200, "Einheit": "kg"},
                "Hammer": {"Menge": 5, "Einheit": "Stk"},
            }
        },
        "Hamburg": {"Material": {}},
        "Metadaten": ["kein Standort"],
    }


class MaterialLogikTests(unittest.TestCase):
    def test_baustellen_namen_filtert_nur_standorte(self):
        baustellen = beispiel_baustellen()

        namen = baustellen_namen(baustellen)

        self.assertEqual(namen, ["Bielefeld", "Hamburg"])

    def test_lager_sicherstellen_legt_firmenlager_an(self):
        baustellen = beispiel_baustellen()

        geaendert = lager_sicherstellen(baustellen)

        self.assertTrue(geaendert)
        self.assertEqual(baustellen[FIRMENLAGER_NAME]["Typ"], "Lager")
        self.assertEqual(baustellen[FIRMENLAGER_NAME]["Material"], {})

    def test_material_eintragen_legt_neuen_standort_an(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = material_eintragen(
            baustellen, "Köln", "Beton", 1000, "kg"
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Material gespeichert")
        self.assertEqual(baustellen["Köln"]["Typ"], "Baustelle")
        self.assertEqual(baustellen["Köln"]["Material"]["Beton"]["Menge"], 1000)

    def test_material_eintragen_aktualisiert_vorhandenes_material(self):
        baustellen = beispiel_baustellen()

        material_eintragen(baustellen, "Bielefeld", "Zement", 250, "kg")

        self.assertEqual(baustellen["Bielefeld"]["Material"]["Zement"]["Menge"], 250)

    def test_materialien_fuer_unbekannten_standort_ist_none(self):
        baustellen = beispiel_baustellen()

        self.assertIsNone(materialien_fuer_baustelle(baustellen, "NichtDa"))

    def test_material_namen_und_mengen_einheiten(self):
        baustellen = beispiel_baustellen()

        self.assertEqual(material_namen(baustellen, "Bielefeld"), ["Zement", "Hammer"])
        einheiten, mengen = mengen_und_einheiten(baustellen, "Bielefeld")
        self.assertEqual(einheiten, ["kg", "Stk"])
        self.assertEqual(mengen, [200, 5])

    def test_baustelle_umbenennen(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = baustelle_umbenennen(baustellen, "Bielefeld", "Berlin")

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Baustelle umbenannt")
        self.assertIn("Berlin", baustellen)
        self.assertNotIn("Bielefeld", baustellen)

    def test_baustelle_umbenennen_verhindert_doppelten_namen(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = baustelle_umbenennen(baustellen, "Bielefeld", "Hamburg")

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Dieser Baustellenname existiert bereits")
        self.assertIn("Bielefeld", baustellen)

    def test_firmenlager_kann_nicht_umbenannt_werden(self):
        baustellen = beispiel_baustellen()
        lager_sicherstellen(baustellen)

        erfolgreich, meldung = baustelle_umbenennen(
            baustellen, FIRMENLAGER_NAME, "Hauptlager"
        )

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Das Firmenlager kann nicht umbenannt werden")
        self.assertIn(FIRMENLAGER_NAME, baustellen)

    def test_material_umbenennen(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = material_umbenennen(
            baustellen, "Bielefeld", "Zement", "Schnellzement"
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Material umbenannt")
        self.assertIn("Schnellzement", baustellen["Bielefeld"]["Material"])
        self.assertNotIn("Zement", baustellen["Bielefeld"]["Material"])

    def test_material_umbenennen_verhindert_doppelten_namen(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = material_umbenennen(
            baustellen, "Bielefeld", "Zement", "Hammer"
        )

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Dieser Materialname existiert bereits")

    def test_menge_aendern(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = menge_aendern(baustellen, "Bielefeld", "Hammer", 10)

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Menge geändert")
        self.assertEqual(baustellen["Bielefeld"]["Material"]["Hammer"]["Menge"], 10)

    def test_einheit_aendern(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = einheit_aendern(
            baustellen, "Bielefeld", "Hammer", "Stück"
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Einheit geändert")
        self.assertEqual(baustellen["Bielefeld"]["Material"]["Hammer"]["Einheit"], "Stück")

    def test_einheit_aendern_lehnt_leere_einheit_ab(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = einheit_aendern(baustellen, "Bielefeld", "Hammer", "")

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Bitte gib eine Einheit ein")

    def test_bestellanfrage_erstellen(self):
        bestellanfragen = [{"id": 4, "status": "offen"}, {"id": "ungueltig"}]

        erfolgreich, meldung, bestellanfrage = bestellanfrage_erstellen(
            bestellanfragen, "Bielefeld", "Zement", 50, "kg"
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Bestellanfrage gespeichert")
        self.assertEqual(bestellanfrage["id"], 5)
        self.assertEqual(bestellanfrage["status"], "offen")
        self.assertEqual(bestellanfragen[-1], bestellanfrage)

    def test_bestellanfrage_erstellen_lehnt_ungueltige_menge_ab(self):
        bestellanfragen = []

        erfolgreich, meldung, bestellanfrage = bestellanfrage_erstellen(
            bestellanfragen, "Bielefeld", "Zement", 0, "kg"
        )

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Bitte gib eine Menge größer als 0 ein")
        self.assertIsNone(bestellanfrage)
        self.assertEqual(bestellanfragen, [])


if __name__ == "__main__":
    unittest.main()

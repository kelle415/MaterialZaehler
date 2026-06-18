import unittest

from material_logik import (
    BUCHUNGSART_ABGANG,
    BUCHUNGSART_KORREKTUR,
    BUCHUNGSART_ZUGANG,
    BESTELLSTATUS_BESTELLT,
    BESTELLSTATUS_GELIEFERT,
    FIRMENLAGER_NAME,
    baustelle_anlegen,
    baustelle_umbenennen,
    baustellen_namen,
    baustellen_vorschlaege,
    bestellanfrage_erstellen,
    bestellanfrage_status_aendern,
    bestellstatus_normalisieren,
    buchungsart_normalisieren,
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

    def test_baustellen_vorschlaege_findet_aehnlichen_namen(self):
        baustellen = beispiel_baustellen()

        vorschlaege = baustellen_vorschlaege(baustellen, "BIifeld")

        self.assertEqual(vorschlaege[0][0], "Bielefeld")
        self.assertGreaterEqual(vorschlaege[0][1], 60)

    def test_baustellen_vorschlaege_ignoriert_schwache_treffer(self):
        baustellen = beispiel_baustellen()

        vorschlaege = baustellen_vorschlaege(baustellen, "xyz")

        self.assertEqual(vorschlaege, [])

    def test_baustellen_vorschlaege_ignoriert_umlaute(self):
        baustellen = {"K\u00f6ln": {"Material": {}}}

        vorschlaege = baustellen_vorschlaege(baustellen, "Koln")

        self.assertEqual(vorschlaege[0][0], "K\u00f6ln")

    def test_lager_sicherstellen_legt_firmenlager_an(self):
        baustellen = beispiel_baustellen()

        geaendert = lager_sicherstellen(baustellen)

        self.assertTrue(geaendert)
        self.assertEqual(baustellen[FIRMENLAGER_NAME]["Typ"], "Lager")
        self.assertEqual(baustellen[FIRMENLAGER_NAME]["Material"], {})

    def test_buchungsart_normalisieren_erkennt_eingaben(self):
        self.assertEqual(buchungsart_normalisieren("1"), BUCHUNGSART_ZUGANG)
        self.assertEqual(buchungsart_normalisieren("minus"), BUCHUNGSART_ABGANG)
        self.assertEqual(buchungsart_normalisieren("Korrektur"), BUCHUNGSART_KORREKTUR)
        self.assertIsNone(buchungsart_normalisieren("unbekannt"))

    def test_bestellstatus_normalisieren_erkennt_eingaben(self):
        self.assertEqual(bestellstatus_normalisieren("2"), BESTELLSTATUS_BESTELLT)
        self.assertEqual(bestellstatus_normalisieren("geliefert"), BESTELLSTATUS_GELIEFERT)
        self.assertIsNone(bestellstatus_normalisieren("unbekannt"))

    def test_material_eintragen_legt_neuen_standort_an(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = material_eintragen(
            baustellen, "Köln", "Beton", 1000, "kg"
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Materialbuchung gespeichert")
        self.assertEqual(baustellen["Köln"]["Typ"], "Baustelle")
        self.assertEqual(baustellen["Köln"]["Material"]["Beton"]["Menge"], 1000)
        bewegung = baustellen["Köln"]["Material"]["Beton"]["Bewegungen"][0]
        self.assertEqual(bewegung["Art"], BUCHUNGSART_ZUGANG)
        self.assertEqual(bewegung["BestandVorher"], 0)
        self.assertEqual(bewegung["BestandNachher"], 1000)

    def test_material_eintragen_addiert_vorhandenes_material_als_zugang(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = material_eintragen(
            baustellen, "Bielefeld", "Zement", 50, "kg", BUCHUNGSART_ZUGANG
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Materialbuchung gespeichert")
        self.assertEqual(baustellen["Bielefeld"]["Material"]["Zement"]["Menge"], 250)
        bewegung = baustellen["Bielefeld"]["Material"]["Zement"]["Bewegungen"][0]
        self.assertEqual(bewegung["Art"], BUCHUNGSART_ZUGANG)
        self.assertEqual(bewegung["BestandVorher"], 200)
        self.assertEqual(bewegung["BestandNachher"], 250)

    def test_material_eintragen_zieht_abgang_ab(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = material_eintragen(
            baustellen, "Bielefeld", "Zement", 50, "kg", BUCHUNGSART_ABGANG
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Materialbuchung gespeichert")
        self.assertEqual(baustellen["Bielefeld"]["Material"]["Zement"]["Menge"], 150)

    def test_material_eintragen_verhindert_negativen_bestand(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = material_eintragen(
            baustellen, "Bielefeld", "Zement", 250, "kg", BUCHUNGSART_ABGANG
        )

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Bestand reicht nicht aus")
        self.assertEqual(baustellen["Bielefeld"]["Material"]["Zement"]["Menge"], 200)

    def test_material_eintragen_korrigiert_bestand(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = material_eintragen(
            baustellen, "Bielefeld", "Zement", 20, "kg", BUCHUNGSART_KORREKTUR
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Materialbuchung gespeichert")
        self.assertEqual(baustellen["Bielefeld"]["Material"]["Zement"]["Menge"], 20)
        bewegung = baustellen["Bielefeld"]["Material"]["Zement"]["Bewegungen"][0]
        self.assertEqual(bewegung["Art"], BUCHUNGSART_KORREKTUR)
        self.assertEqual(bewegung["BestandVorher"], 200)
        self.assertEqual(bewegung["BestandNachher"], 20)

    def test_material_eintragen_korrigiert_bestand_auf_null(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = material_eintragen(
            baustellen, "Bielefeld", "Zement", 0, "kg", BUCHUNGSART_KORREKTUR
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Materialbuchung gespeichert")
        self.assertEqual(baustellen["Bielefeld"]["Material"]["Zement"]["Menge"], 0)

    def test_material_eintragen_lehnt_abgang_fuer_unbekanntes_material_ab(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = material_eintragen(
            baustellen, "Bielefeld", "Beton", 20, "kg", BUCHUNGSART_ABGANG
        )

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Material nicht gefunden")
        self.assertNotIn("Beton", baustellen["Bielefeld"]["Material"])

    def test_material_eintragen_lehnt_falsche_einheit_ab(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = material_eintragen(
            baustellen, "Bielefeld", "Zement", 20, "Stk", BUCHUNGSART_ZUGANG
        )

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Einheit stimmt nicht mit vorhandener Einheit ueberein")
        self.assertEqual(baustellen["Bielefeld"]["Material"]["Zement"]["Menge"], 200)

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

    def test_baustelle_anlegen(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = baustelle_anlegen(baustellen, "Berlin")

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Baustelle angelegt")
        self.assertEqual(baustellen["Berlin"], {"Typ": "Baustelle", "Material": {}})

    def test_baustelle_anlegen_verhindert_doppelten_namen(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = baustelle_anlegen(baustellen, "Bielefeld")

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Dieser Baustellenname existiert bereits")

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
        self.assertEqual(meldung, "Materialbuchung gespeichert")
        self.assertEqual(baustellen["Bielefeld"]["Material"]["Hammer"]["Menge"], 10)
        bewegung = baustellen["Bielefeld"]["Material"]["Hammer"]["Bewegungen"][0]
        self.assertEqual(bewegung["Art"], BUCHUNGSART_KORREKTUR)
        self.assertEqual(bewegung["BestandVorher"], 5)
        self.assertEqual(bewegung["BestandNachher"], 10)

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

    def test_bestellanfrage_status_aendern(self):
        bestellanfragen = [{"id": 3, "status": "offen"}]

        erfolgreich, meldung, bestellanfrage = bestellanfrage_status_aendern(
            bestellanfragen, 3, BESTELLSTATUS_BESTELLT
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Bestellstatus geaendert")
        self.assertEqual(bestellanfrage["status"], BESTELLSTATUS_BESTELLT)
        self.assertEqual(bestellanfragen[0]["status"], BESTELLSTATUS_BESTELLT)

    def test_bestellanfrage_status_aendern_lehnt_unbekannte_id_ab(self):
        bestellanfragen = [{"id": 3, "status": "offen"}]

        erfolgreich, meldung, bestellanfrage = bestellanfrage_status_aendern(
            bestellanfragen, 9, BESTELLSTATUS_BESTELLT
        )

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Bestellanfrage nicht gefunden")
        self.assertIsNone(bestellanfrage)

    def test_bestellanfrage_status_aendern_lehnt_ungueltigen_status_ab(self):
        bestellanfragen = [{"id": 3, "status": "offen"}]

        erfolgreich, meldung, bestellanfrage = bestellanfrage_status_aendern(
            bestellanfragen, 3, "unbekannt"
        )

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Bestellstatus ist ungueltig")
        self.assertIsNone(bestellanfrage)


if __name__ == "__main__":
    unittest.main()

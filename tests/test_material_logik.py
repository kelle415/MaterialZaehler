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
    bestellanfrage_wareneingang_buchen,
    bestellstatus_normalisieren,
    buchungsart_normalisieren,
    chef_uebersicht_erstellen,
    einheit_aendern,
    gesamtbestand_sammeln,
    kritische_bestaende_sammeln,
    lager_sicherstellen,
    material_eintragen,
    materialbewegungen_sammeln,
    material_namen,
    material_umbenennen,
    materialien_fuer_baustelle,
    mitarbeiteranfrage_erstellen,
    mitarbeiterbestand_setzen,
    mitarbeiteruebersicht_sammeln,
    menge_aendern,
    mengen_und_einheiten,
    offene_bestellanfragen_sammeln,
    offene_mitarbeiteranfragen_sammeln,
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

    def test_material_eintragen_speichert_referenz_und_notiz(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = material_eintragen(
            baustellen,
            "Bielefeld",
            "Zement",
            50,
            "kg",
            BUCHUNGSART_ZUGANG,
            referenz="Bestellanfrage #8",
            notiz="Wareneingang",
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Materialbuchung gespeichert")
        bewegung = baustellen["Bielefeld"]["Material"]["Zement"]["Bewegungen"][0]
        self.assertEqual(bewegung["Referenz"], "Bestellanfrage #8")
        self.assertEqual(bewegung["Notiz"], "Wareneingang")

    def test_materialbewegungen_sammeln_sortiert_und_ergaenzt_kontext(self):
        baustellen = {
            "Bielefeld": {
                "Material": {
                    "Zement": {
                        "Menge": 20,
                        "Einheit": "kg",
                        "Bewegungen": [
                            {
                                "Art": "zugang",
                                "Menge": 20,
                                "Einheit": "kg",
                                "BestandVorher": 0,
                                "BestandNachher": 20,
                                "Zeitpunkt": "2026-01-01T10:00:00+00:00",
                            }
                        ],
                    }
                }
            },
            "Hamburg": {
                "Material": {
                    "Holz": {
                        "Menge": 5,
                        "Einheit": "stk",
                        "Bewegungen": [
                            {
                                "Art": "abgang",
                                "Menge": 2,
                                "Einheit": "stk",
                                "BestandVorher": 7,
                                "BestandNachher": 5,
                                "Zeitpunkt": "2026-01-02T10:00:00+00:00",
                            }
                        ],
                    }
                }
            },
        }

        bewegungen = materialbewegungen_sammeln(baustellen, limit=1)

        self.assertEqual(len(bewegungen), 1)
        self.assertEqual(bewegungen[0]["Standort"], "Hamburg")
        self.assertEqual(bewegungen[0]["Material"], "Holz")

    def test_gesamtbestand_sammeln_addiert_material_ueber_standorte(self):
        baustellen = beispiel_baustellen()

        bestand = gesamtbestand_sammeln(baustellen)

        zement = next(eintrag for eintrag in bestand if eintrag["Material"] == "Zement")
        self.assertEqual(zement["Gesamtmenge"], 200)
        self.assertEqual(zement["Einheit"], "kg")
        self.assertEqual(zement["Standorte"][0]["Standort"], "Bielefeld")

    def test_kritische_bestaende_sammeln_findet_leere_und_mindestbestand(self):
        baustellen = {
            "Bielefeld": {
                "Material": {
                    "Zement": {"Menge": 0, "Einheit": "kg"},
                    "Hammer": {"Menge": 3, "Einheit": "Stk", "Mindestbestand": 5},
                }
            }
        }

        kritische_bestaende = kritische_bestaende_sammeln(baustellen)

        self.assertEqual(len(kritische_bestaende), 2)
        self.assertEqual(kritische_bestaende[0]["Grund"], "unter Mindestbestand")
        self.assertEqual(kritische_bestaende[1]["Grund"], "leer")

    def test_offene_bestellanfragen_sammeln_filtert_abgeschlossene_status(self):
        bestellanfragen = [
            {"id": 1, "status": "offen"},
            {"id": 2, "status": "bestellt"},
            {"id": 3, "status": "abgeschlossen"},
        ]

        offene_bestellungen = offene_bestellanfragen_sammeln(bestellanfragen)

        self.assertEqual([bestellung["id"] for bestellung in offene_bestellungen], [1, 2])

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
        self.assertEqual(baustellen["Berlin"]["Typ"], "Baustelle")
        self.assertEqual(baustellen["Berlin"]["Material"], {})
        self.assertEqual(baustellen["Berlin"]["Mitarbeiter"]["Anzahl"], 0)

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
        self.assertEqual(bestellanfrage["statusHistorie"][0]["von"], None)
        self.assertEqual(bestellanfrage["statusHistorie"][0]["zu"], "offen")
        self.assertEqual(
            bestellanfrage["statusHistorie"][0]["grund"], "Bestellanfrage erstellt"
        )
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
            bestellanfragen, 3, BESTELLSTATUS_BESTELLT, "Beim Lieferanten bestellt"
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Bestellstatus geaendert")
        self.assertEqual(bestellanfrage["status"], BESTELLSTATUS_BESTELLT)
        self.assertEqual(bestellanfragen[0]["status"], BESTELLSTATUS_BESTELLT)
        self.assertEqual(bestellanfrage["statusHistorie"][0]["von"], "offen")
        self.assertEqual(bestellanfrage["statusHistorie"][0]["zu"], "bestellt")
        self.assertEqual(
            bestellanfrage["statusHistorie"][0]["grund"],
            "Beim Lieferanten bestellt",
        )

    def test_bestellanfrage_wareneingang_bucht_material_und_status(self):
        baustellen = beispiel_baustellen()
        bestellanfragen = [
            {
                "id": 7,
                "ziel": "Bielefeld",
                "material": "Zement",
                "menge": 50,
                "einheit": "kg",
                "status": BESTELLSTATUS_BESTELLT,
            }
        ]

        erfolgreich, meldung, bestellanfrage = bestellanfrage_wareneingang_buchen(
            bestellanfragen, baustellen, 7, "Lieferung angekommen"
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Wareneingang gebucht und Bestellstatus geaendert")
        self.assertEqual(bestellanfrage["status"], BESTELLSTATUS_GELIEFERT)
        self.assertTrue(bestellanfrage["wareneingang"]["gebucht"])
        self.assertEqual(baustellen["Bielefeld"]["Material"]["Zement"]["Menge"], 250)
        bewegung = baustellen["Bielefeld"]["Material"]["Zement"]["Bewegungen"][0]
        self.assertEqual(bewegung["Art"], BUCHUNGSART_ZUGANG)
        self.assertEqual(bewegung["Referenz"], "Bestellanfrage #7")
        self.assertEqual(bewegung["Notiz"], "Wareneingang")
        self.assertEqual(bestellanfrage["statusHistorie"][0]["von"], "bestellt")
        self.assertEqual(bestellanfrage["statusHistorie"][0]["zu"], "geliefert")
        self.assertEqual(
            bestellanfrage["statusHistorie"][0]["grund"], "Lieferung angekommen"
        )

    def test_bestellanfrage_wareneingang_verhindert_doppelte_buchung(self):
        baustellen = beispiel_baustellen()
        bestellanfragen = [
            {
                "id": 7,
                "ziel": "Bielefeld",
                "material": "Zement",
                "menge": 50,
                "einheit": "kg",
                "status": BESTELLSTATUS_GELIEFERT,
                "wareneingang": {"gebucht": True},
            }
        ]

        erfolgreich, meldung, bestellanfrage = bestellanfrage_wareneingang_buchen(
            bestellanfragen, baustellen, 7, "Noch einmal geliefert"
        )

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Wareneingang wurde bereits gebucht")
        self.assertIsNone(bestellanfrage)
        self.assertEqual(baustellen["Bielefeld"]["Material"]["Zement"]["Menge"], 200)

    def test_mitarbeiterbestand_setzen_und_uebersicht_sammeln(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = mitarbeiterbestand_setzen(
            baustellen, "Bielefeld", 8, "Rohbau"
        )
        uebersicht = mitarbeiteruebersicht_sammeln(baustellen)

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Mitarbeiterbestand gespeichert")
        bielefeld = next(eintrag for eintrag in uebersicht if eintrag["Standort"] == "Bielefeld")
        self.assertEqual(bielefeld["Anzahl"], 8)
        self.assertEqual(bielefeld["Notiz"], "Rohbau")

    def test_mitarbeiterbestand_setzen_lehnt_unbekannte_baustelle_ab(self):
        baustellen = beispiel_baustellen()

        erfolgreich, meldung = mitarbeiterbestand_setzen(
            baustellen, "Berlin", 3
        )

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Baustelle nicht gefunden")

    def test_mitarbeiteranfrage_erstellen(self):
        mitarbeiteranfragen = [{"id": 2}]

        erfolgreich, meldung, anfrage = mitarbeiteranfrage_erstellen(
            mitarbeiteranfragen, "Bielefeld", 4, "Maurer", "Termin zieht an"
        )

        self.assertTrue(erfolgreich)
        self.assertEqual(meldung, "Mitarbeiteranfrage gespeichert")
        self.assertEqual(anfrage["id"], 3)
        self.assertEqual(anfrage["status"], "offen")
        self.assertEqual(anfrage["anzahl"], 4)
        self.assertEqual(anfrage["rolle"], "Maurer")
        self.assertEqual(anfrage["statusHistorie"][0]["zu"], "offen")

    def test_offene_mitarbeiteranfragen_sammeln_filtert_erledigte(self):
        mitarbeiteranfragen = [
            {"id": 1, "status": "offen"},
            {"id": 2, "status": "eingeplant"},
            {"id": 3, "status": "erledigt"},
        ]

        offene_anfragen = offene_mitarbeiteranfragen_sammeln(mitarbeiteranfragen)

        self.assertEqual([anfrage["id"] for anfrage in offene_anfragen], [1, 2])

    def test_chef_uebersicht_erstellen_buendelt_alle_bereiche(self):
        baustellen = beispiel_baustellen()
        bestellanfragen = [{"id": 1, "status": "offen"}]
        mitarbeiteranfragen = [{"id": 1, "status": "offen"}]

        uebersicht = chef_uebersicht_erstellen(
            baustellen, bestellanfragen, mitarbeiteranfragen
        )

        self.assertIn("Bielefeld", uebersicht["Baustellen"])
        self.assertEqual(len(uebersicht["Gesamtbestand"]), 2)
        self.assertEqual(len(uebersicht["OffeneBestellanfragen"]), 1)
        self.assertEqual(len(uebersicht["OffeneMitarbeiteranfragen"]), 1)

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

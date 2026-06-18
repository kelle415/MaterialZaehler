import unittest
from unittest.mock import patch

import materialZaehler


def baustellen_mit_material():
    return {
        "Bielefeld": {
            "Material": {
                "Zement": {
                    "Menge": 5,
                    "Einheit": "kg",
                }
            }
        },
        "Hamburg": {"Material": {}},
    }


def gedruckter_text(ausgabe):
    return "\n".join(
        " ".join(str(wert) for wert in aufruf.args)
        for aufruf in ausgabe.call_args_list
    )


class MaterialZaehlerCliTests(unittest.TestCase):
    def test_menueverweis_routet_hauptauswahlen(self):
        faelle = [
            ("1", "materialEintragen"),
            ("2", "materialAnzeigen"),
            ("3", "allgemeinAendernabfragen"),
            ("4", "lagerAnzeigen"),
        ]

        for auswahl, erwartete_funktion in faelle:
            with self.subTest(auswahl=auswahl):
                baustellen = baustellen_mit_material()
                bestellanfragen = []
                with patch("builtins.input", return_value=auswahl), patch(
                    "builtins.print"
                ), patch(
                    "materialZaehler.baustelleAbfragen", return_value="Bielefeld"
                ), patch(
                    "materialZaehler.materialEintragen"
                ) as material_eintragen, patch(
                    "materialZaehler.materialAnzeigen"
                ) as material_anzeigen, patch(
                    "materialZaehler.allgemeinAendernabfragen"
                ) as allgemein_aendern, patch(
                    "materialZaehler.lagerAnzeigen"
                ) as lager_anzeigen, patch(
                    "materialZaehler.zurueck"
                ) as zurueck:
                    materialZaehler.menueverweis(baustellen, bestellanfragen)

                erwartete_mock = {
                    "materialEintragen": material_eintragen,
                    "materialAnzeigen": material_anzeigen,
                    "allgemeinAendernabfragen": allgemein_aendern,
                    "lagerAnzeigen": lager_anzeigen,
                }[erwartete_funktion]
                erwartete_mock.assert_called_once()
                zurueck.assert_called_once_with(baustellen, bestellanfragen)

    def test_menueverweis_routet_bestellen_und_beenden(self):
        baustellen = baustellen_mit_material()
        bestellanfragen = []
        with patch("builtins.input", return_value="5"), patch(
            "builtins.print"
        ), patch("materialZaehler.bestellMenue") as bestell_menue:
            materialZaehler.menueverweis(baustellen, bestellanfragen)

        bestell_menue.assert_called_once_with(baustellen, bestellanfragen)

        with patch("builtins.input", return_value="6"), patch(
            "builtins.print"
        ), patch("materialZaehler.beenden") as beenden:
            materialZaehler.menueverweis(baustellen, bestellanfragen)

        beenden.assert_called_once_with(baustellen, bestellanfragen)

    def test_material_anzeigen_deckt_unbekannt_leer_und_material_ab(self):
        baustellen = baustellen_mit_material()

        with patch("builtins.print") as ausgabe:
            ergebnis = materialZaehler.materialAnzeigen(baustellen, "Unbekannt")
        self.assertFalse(ergebnis)
        self.assertIn("Standort nicht gefunden", gedruckter_text(ausgabe))

        with patch("builtins.print") as ausgabe:
            ergebnis = materialZaehler.materialAnzeigen(baustellen, "Hamburg")
        self.assertTrue(ergebnis)
        self.assertIn("Kein Material vorhanden", gedruckter_text(ausgabe))

        with patch("builtins.print") as ausgabe:
            ergebnis = materialZaehler.materialAnzeigen(baustellen, "Bielefeld")
        self.assertTrue(ergebnis)
        self.assertIn("- Zement: 5 kg", gedruckter_text(ausgabe))

    def test_lager_anzeigen_stellt_lager_sicher_und_speichert(self):
        baustellen = {}

        with patch("materialZaehler.baustellen_speichern") as speichern, patch(
            "materialZaehler.materialAnzeigen"
        ) as anzeigen:
            materialZaehler.lagerAnzeigen(baustellen)

        self.assertIn(materialZaehler.FIRMENLAGER_NAME, baustellen)
        speichern.assert_called_once_with(baustellen)
        anzeigen.assert_called_once_with(baustellen, materialZaehler.FIRMENLAGER_NAME)

    def test_allgemein_aendernabfragen_routet_auswahlen(self):
        faelle = [
            ("1", "baustelleAendernabfragen"),
            ("2", "materialAendernabfragen"),
            ("3", "mengeAendernabfragen"),
            ("4", "einheitAendernabfragen"),
        ]

        for auswahl, erwartete_funktion in faelle:
            with self.subTest(auswahl=auswahl):
                baustellen = baustellen_mit_material()
                with patch("builtins.input", return_value=auswahl), patch(
                    "builtins.print"
                ), patch(
                    "materialZaehler.materialAnzeigen", return_value=True
                ), patch(
                    "materialZaehler.baustelleAendernabfragen"
                ) as baustelle_aendern, patch(
                    "materialZaehler.materialAendernabfragen"
                ) as material_aendern, patch(
                    "materialZaehler.mengeAendernabfragen"
                ) as menge_aendern, patch(
                    "materialZaehler.einheitAendernabfragen"
                ) as einheit_aendern:
                    materialZaehler.allgemeinAendernabfragen(
                        baustellen, [], "Bielefeld"
                    )

                erwartete_mock = {
                    "baustelleAendernabfragen": baustelle_aendern,
                    "materialAendernabfragen": material_aendern,
                    "mengeAendernabfragen": menge_aendern,
                    "einheitAendernabfragen": einheit_aendern,
                }[erwartete_funktion]
                erwartete_mock.assert_called_once()

    def test_aendernabfragen_liefert_material_oder_mengendaten(self):
        with patch(
            "builtins.input", side_effect=["Zement", "Beton", "j"]
        ), patch("builtins.print"):
            ergebnis = materialZaehler.aendernabfragen(None)

        self.assertEqual(ergebnis, ("Zement", "Beton", "j", None))

        with patch(
            "builtins.input", side_effect=["Zement", "5", "7", "j"]
        ), patch("builtins.print"):
            ergebnis = materialZaehler.aendernabfragen("menge")

        self.assertEqual(ergebnis, ("5", "7", "j", "Zement"))

    def test_aendernabfrage_wrapper_brechen_bei_nein_ab(self):
        baustellen = baustellen_mit_material()

        funktionen = [
            (
                materialZaehler.baustelleAendernabfragen,
                (baustellen, "Bielefeld", "1", ["Bielefeld"]),
            ),
            (
                materialZaehler.materialAendernabfragen,
                (baustellen, "Bielefeld", "2", ["Zement"]),
            ),
            (
                materialZaehler.mengeAendernabfragen,
                (baustellen, "Bielefeld", "3", ["Zement"], [5]),
            ),
            (
                materialZaehler.einheitAendernabfragen,
                (baustellen, "Bielefeld", ["Zement"], ["kg"]),
            ),
        ]

        for funktion, argumente in funktionen:
            with self.subTest(funktion=funktion.__name__):
                with patch("builtins.input", return_value="n"), patch(
                    "builtins.print"
                ) as ausgabe:
                    funktion(*argumente)

                self.assertIn("abgebrochen", gedruckter_text(ausgabe).casefold())

    def test_bestell_menue_routet_auswahlen(self):
        faelle = [
            ("1", "bestellanfrageErstellen"),
            ("2", "mitarbeiteranfrageErstellen"),
            ("3", "bestellanfragenAnzeigen"),
        ]

        for auswahl, erwartete_funktion in faelle:
            with self.subTest(auswahl=auswahl):
                baustellen = baustellen_mit_material()
                bestellanfragen = []
                with patch("builtins.input", return_value=auswahl), patch(
                    "builtins.print"
                ), patch(
                    "materialZaehler.bestellanfrageErstellen"
                ) as bestellung_erstellen, patch(
                    "materialZaehler.mitarbeiteranfrageErstellen"
                ) as personal_erstellen, patch(
                    "materialZaehler.bestellanfragenAnzeigen"
                ) as bestellungen_anzeigen, patch(
                    "materialZaehler.zurueck"
                ) as zurueck:
                    materialZaehler.bestellMenue(baustellen, bestellanfragen)

                erwartete_mock = {
                    "bestellanfrageErstellen": bestellung_erstellen,
                    "mitarbeiteranfrageErstellen": personal_erstellen,
                    "bestellanfragenAnzeigen": bestellungen_anzeigen,
                }[erwartete_funktion]
                erwartete_mock.assert_called_once()
                zurueck.assert_called_once_with(baustellen, bestellanfragen)

        with patch("builtins.input", return_value="4"), patch(
            "builtins.print"
        ), patch("materialZaehler.menueverweis") as menueverweis:
            materialZaehler.bestellMenue({}, [])

        menueverweis.assert_called_once_with({}, [])

    def test_bestellanfrage_erstellen_speichert_bestaetigte_anfrage(self):
        bestellanfragen = []
        with patch(
            "materialZaehler.bestellDatenAbfragen",
            return_value=("Berlin", "Zement", 5, "kg"),
        ), patch("builtins.input", return_value="j"), patch(
            "builtins.print"
        ) as ausgabe, patch(
            "materialZaehler.bestellanfragen_speichern"
        ) as speichern:
            materialZaehler.bestellanfrageErstellen({}, bestellanfragen)

        self.assertEqual(bestellanfragen[0]["ziel"], "Berlin")
        self.assertIn("existiert noch nicht", gedruckter_text(ausgabe))
        speichern.assert_called_once_with(bestellanfragen)

    def test_bestellanfrage_erstellen_bricht_ab_oder_lehnt_antwort_ab(self):
        for antwort, erwarteter_text in [
            ("n", "abgebrochen"),
            ("vielleicht", "unverwertbare eingabe"),
        ]:
            with self.subTest(antwort=antwort):
                bestellanfragen = []
                with patch(
                    "materialZaehler.bestellDatenAbfragen",
                    return_value=("Bielefeld", "Zement", 5, "kg"),
                ), patch("builtins.input", return_value=antwort), patch(
                    "builtins.print"
                ) as ausgabe, patch(
                    "materialZaehler.bestellanfragen_speichern"
                ) as speichern:
                    materialZaehler.bestellanfrageErstellen(
                        baustellen_mit_material(), bestellanfragen
                    )

                self.assertEqual(bestellanfragen, [])
                self.assertIn(erwarteter_text, gedruckter_text(ausgabe).casefold())
                speichern.assert_not_called()

    def test_mitarbeiteranfrage_erstellen_bricht_ab_oder_lehnt_antwort_ab(self):
        for antwort, erwarteter_text in [
            ("n", "abgebrochen"),
            ("vielleicht", "unverwertbare eingabe"),
        ]:
            with self.subTest(antwort=antwort):
                with patch(
                    "materialZaehler.mitarbeiterAnfrageDatenAbfragen",
                    return_value=("Bielefeld", 2, "Maurer", "Termin"),
                ), patch("builtins.input", return_value=antwort), patch(
                    "builtins.print"
                ) as ausgabe, patch(
                    "materialZaehler.mitarbeiteranfragen_laden"
                ) as laden:
                    materialZaehler.mitarbeiteranfrageErstellen(
                        baustellen_mit_material()
                    )

                self.assertIn(erwarteter_text, gedruckter_text(ausgabe).casefold())
                laden.assert_not_called()

    def test_bestellanfragen_anzeigen_deckt_leere_und_gefuellte_liste_ab(self):
        with patch("builtins.print") as ausgabe:
            materialZaehler.bestellanfragenAnzeigen([])
        self.assertIn("Keine Bestellanfragen", gedruckter_text(ausgabe))

        bestellanfragen = [
            {
                "id": 7,
                "ziel": "Bielefeld",
                "material": "Zement",
                "menge": 5,
                "einheit": "kg",
                "status": "offen",
            }
        ]
        with patch("builtins.print") as ausgabe:
            materialZaehler.bestellanfragenAnzeigen(bestellanfragen)

        self.assertIn("#7: 5 kg Zement", gedruckter_text(ausgabe))

    def test_aenderungsfunktionen_speichern_gueltige_aenderungen(self):
        baustellen = baustellen_mit_material()

        with patch("materialZaehler.baustellen_speichern") as speichern, patch(
            "materialZaehler.materialAnzeigen"
        ) as anzeigen, patch("builtins.print"):
            materialZaehler.baustellennamenaendern(
                baustellen, "Bielefeld", "Bielefeld", "Berlin", "j", None
            )

        self.assertIn("Berlin", baustellen)
        speichern.assert_called_with(baustellen)
        anzeigen.assert_called_with(baustellen, "Berlin")

        with patch("materialZaehler.baustellen_speichern") as speichern, patch(
            "materialZaehler.materialAnzeigen"
        ) as anzeigen, patch("builtins.print"):
            materialZaehler.materialnamenaendern(
                baustellen, "Berlin", "Zement", "Beton", "j", None
            )

        self.assertIn("Beton", baustellen["Berlin"]["Material"])
        speichern.assert_called_with(baustellen)
        anzeigen.assert_called_with(baustellen, "Berlin")

    def test_menge_und_einheit_aendern_behandeln_fehler_und_erfolg(self):
        baustellen = baustellen_mit_material()

        with patch("builtins.print") as ausgabe, patch(
            "materialZaehler.baustellen_speichern"
        ) as speichern:
            materialZaehler.mengenaendern(
                baustellen, "Bielefeld", "5", "abc", "j", "Zement"
            )

        self.assertIn("ganze Zahl", gedruckter_text(ausgabe))
        speichern.assert_not_called()

        with patch("builtins.print"), patch(
            "materialZaehler.baustellen_speichern"
        ) as speichern, patch("materialZaehler.materialAnzeigen") as anzeigen:
            materialZaehler.mengenaendern(
                baustellen, "Bielefeld", "5", "8", "j", "Zement"
            )

        self.assertEqual(baustellen["Bielefeld"]["Material"]["Zement"]["Menge"], 8)
        speichern.assert_called_once_with(baustellen)
        anzeigen.assert_called_once_with(baustellen, "Bielefeld")

        with patch("builtins.print"), patch(
            "materialZaehler.baustellen_speichern"
        ) as speichern, patch("materialZaehler.materialAnzeigen") as anzeigen:
            materialZaehler.einheitaendern(baustellen, "Bielefeld", "Zement", "t", "j")

        self.assertEqual(baustellen["Bielefeld"]["Material"]["Zement"]["Einheit"], "t")
        speichern.assert_called_once_with(baustellen)
        anzeigen.assert_called_once_with(baustellen, "Bielefeld")

    def test_zurueck_routet_zum_menue_oder_beendet(self):
        baustellen = baustellen_mit_material()
        bestellanfragen = []

        with patch("builtins.input", return_value="j"), patch(
            "materialZaehler.menueverweis"
        ) as menueverweis:
            materialZaehler.zurueck(baustellen, bestellanfragen)

        menueverweis.assert_called_once_with(baustellen, bestellanfragen)

        with patch("builtins.input", side_effect=["n", "j"]), patch(
            "materialZaehler.beenden"
        ) as beenden:
            materialZaehler.zurueck(baustellen, bestellanfragen)

        beenden.assert_called_once_with(baustellen, bestellanfragen)

    def test_beenden_speichert_und_beendet(self):
        baustellen = baustellen_mit_material()
        bestellanfragen = [{"id": 1}]

        with patch("materialZaehler.baustellen_speichern") as baustellen_speichern, patch(
            "materialZaehler.bestellanfragen_speichern"
        ) as bestellanfragen_speichern, patch("builtins.print"):
            with self.assertRaises(SystemExit):
                materialZaehler.beenden(baustellen, bestellanfragen)

        baustellen_speichern.assert_called_once_with(baustellen)
        bestellanfragen_speichern.assert_called_once_with(bestellanfragen)

from copy import deepcopy
import unittest

from hypothesis import given
from hypothesis import strategies as st

from material_logik import (
    BUCHUNGSART_ABGANG,
    BUCHUNGSART_ZUGANG,
    gesamtbestand_sammeln,
    material_eintragen,
    text_normalisieren,
)


# Die Strategien koppeln Mengen so, dass jede Property gezielt gueltige
# oder bewusst ungueltige Buchungssituationen prueft.
@st.composite
def gueltige_buchungsfolgen(draw):
    startbestand = draw(st.integers(min_value=0, max_value=10_000))
    zugang = draw(st.integers(min_value=1, max_value=10_000))
    abgang = draw(st.integers(min_value=1, max_value=startbestand + zugang))
    return startbestand, zugang, abgang


@st.composite
def ueberzogene_abgaenge(draw):
    startbestand = draw(st.integers(min_value=0, max_value=10_000))
    abgang = draw(st.integers(min_value=startbestand + 1, max_value=startbestand + 10_000))
    return startbestand, abgang


def baustellen_mit_zement(startbestand):
    return {
        "Bielefeld": {
            "Material": {
                "Zement": {
                    "Menge": startbestand,
                    "Einheit": "kg",
                    "Bewegungen": [],
                }
            }
        }
    }


class MaterialLogikPropertyTests(unittest.TestCase):
    # Diese Tests sichern fachliche Invarianten statt einzelner Beispielwerte.
    @given(gueltige_buchungsfolgen())
    def test_materialbuchungen_bilanzieren_bestand_exakt(self, buchungsfolge):
        startbestand, zugang, abgang = buchungsfolge
        baustellen = baustellen_mit_zement(startbestand)

        erfolgreich, meldung = material_eintragen(
            baustellen,
            "Bielefeld",
            "Zement",
            zugang,
            "kg",
            BUCHUNGSART_ZUGANG,
        )
        self.assertTrue(erfolgreich, meldung)

        erfolgreich, meldung = material_eintragen(
            baustellen,
            "Bielefeld",
            "Zement",
            abgang,
            "kg",
            BUCHUNGSART_ABGANG,
        )
        self.assertTrue(erfolgreich, meldung)

        erwarteter_bestand = startbestand + zugang - abgang
        material = baustellen["Bielefeld"]["Material"]["Zement"]
        self.assertEqual(material["Menge"], erwarteter_bestand)

        bewegungen = material["Bewegungen"]
        self.assertEqual(len(bewegungen), 2)
        self.assertEqual(bewegungen[0]["BestandVorher"], startbestand)
        self.assertEqual(bewegungen[0]["BestandNachher"], startbestand + zugang)
        self.assertEqual(bewegungen[1]["BestandVorher"], startbestand + zugang)
        self.assertEqual(bewegungen[1]["BestandNachher"], erwarteter_bestand)

    @given(ueberzogene_abgaenge())
    def test_ueberzogener_abgang_veraendert_bestand_nicht(self, abgangsdaten):
        startbestand, abgang = abgangsdaten
        baustellen = baustellen_mit_zement(startbestand)
        vorher = deepcopy(baustellen)

        erfolgreich, meldung = material_eintragen(
            baustellen,
            "Bielefeld",
            "Zement",
            abgang,
            "kg",
            BUCHUNGSART_ABGANG,
        )

        self.assertFalse(erfolgreich)
        self.assertEqual(meldung, "Bestand reicht nicht aus")
        self.assertEqual(baustellen, vorher)

    @given(
        st.lists(st.integers(min_value=0, max_value=10_000), min_size=1, max_size=20)
    )
    def test_gesamtbestand_addiert_alle_standorte(self, mengen):
        baustellen = {
            f"Standort {index}": {
                "Material": {
                    "Zement": {
                        "Menge": menge,
                        "Einheit": "kg",
                    }
                }
            }
            for index, menge in enumerate(mengen)
        }
        baustellen["Metadaten"] = ["kein Standort"]

        bestand = gesamtbestand_sammeln(baustellen)

        self.assertEqual(len(bestand), 1)
        self.assertEqual(bestand[0]["Material"], "Zement")
        self.assertEqual(bestand[0]["Einheit"], "kg")
        self.assertEqual(bestand[0]["Gesamtmenge"], sum(mengen))
        self.assertEqual(
            bestand[0]["Standorte"],
            [
                {"Standort": f"Standort {index}", "Menge": menge}
                for index, menge in enumerate(mengen)
            ],
        )

    @given(st.text(max_size=100))
    def test_text_normalisieren_ist_idempotent(self, text):
        normalisiert = text_normalisieren(text)

        self.assertEqual(text_normalisieren(normalisiert), normalisiert)

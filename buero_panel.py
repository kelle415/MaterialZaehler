"""
Buero-Panel fuer organisatorische Aufgaben.

Dieses CLI ist der Einstieg fuer Funktionen, die nicht in die Baustellenansicht
gehoeren: Bestellanfragen bearbeiten und Baustellen verwalten.
"""

from cli_helpers import (
    baustellenNamenAenderungAbfragen,
    ganzzahlAbfragen,
    istJa,
    istNein,
    textAbfragen,
)
from datenspeicher import (
    baustellen_laden,
    baustellen_speichern,
    bestellanfragen_laden,
    bestellanfragen_speichern,
)
from material_logik import (
    BESTELLSTATUS_GELIEFERT,
    BESTELLSTATUS_WERTE,
    baustelle_anlegen,
    baustelle_umbenennen,
    baustellen_namen,
    bestellanfrage_status_aendern,
    bestellanfrage_wareneingang_buchen,
    bestellstatus_normalisieren,
    lager_sicherstellen,
    materialbewegungen_sammeln,
)


def bestellanfragenAnzeigen(bestellanfragenListe):
    print("\n", "-" * 35)
    print(" Bestellanfragen")
    if not bestellanfragenListe:
        print("Keine Bestellanfragen vorhanden")
        print("-" * 35, "\n")
        return

    for bestellanfrage in bestellanfragenListe:
        bestell_id = bestellanfrage.get("id")
        ziel = bestellanfrage.get("ziel")
        material = bestellanfrage.get("material")
        menge = bestellanfrage.get("menge")
        einheit = bestellanfrage.get("einheit")
        status = bestellanfrage.get("status")
        print(f"- #{bestell_id}: {menge} {einheit} {material} fuer {ziel} ({status})")

        historie = bestellanfrage.get("statusHistorie", [])
        if historie:
            letzter_eintrag = historie[-1]
            zeitpunkt = letzter_eintrag.get("zeitpunkt")
            grund = letzter_eintrag.get("grund")
            print(f"  letzter Statuswechsel: {zeitpunkt} - {grund}")

        wareneingang = bestellanfrage.get("wareneingang")
        if isinstance(wareneingang, dict) and wareneingang.get("gebucht"):
            print(f"  Wareneingang gebucht: {wareneingang.get('zeitpunkt')}")
    print("-" * 35, "\n")


def baustellenAnzeigen(baustellenListe):
    print("\n", "-" * 35)
    print(" Baustellen und Standorte")
    namen = baustellen_namen(baustellenListe)
    if not namen:
        print("Keine Baustellen vorhanden")
        print("-" * 35, "\n")
        return

    for name in namen:
        typ = baustellenListe.get(name, {}).get("Typ", "Baustelle")
        print(f"- {name} ({typ})")
    print("-" * 35, "\n")


def bestellstatusAbfragen():
    print("\nWelcher Status soll gesetzt werden?")
    for nummer, status in enumerate(BESTELLSTATUS_WERTE, start=1):
        print(f" {nummer}. {status}")

    while True:
        status = bestellstatus_normalisieren(input("Antwort: "))
        if status is not None:
            return status
        print("Bitte waehle einen gueltigen Bestellstatus.")


def bestellanfrageStatusAendern(bestellanfragenListe, baustellenListe=None):
    bestellanfragenAnzeigen(bestellanfragenListe)
    if not bestellanfragenListe:
        return False

    bestell_id = ganzzahlAbfragen("Welche Bestellnummer soll geaendert werden: ")
    neuer_status = bestellstatusAbfragen()
    grund = textAbfragen(
        "Warum wird der Status geaendert: ",
        "Bitte gib einen Grund fuer die Statusaenderung ein.",
    )

    if neuer_status == BESTELLSTATUS_GELIEFERT:
        if baustellenListe is None:
            print("Wareneingang kann ohne Baustellendaten nicht gebucht werden.")
            return False

        print("Wareneingang jetzt in den Zielbestand buchen? (J/N)")
        bestaetigung = input("Antwort: ")
        if istNein(bestaetigung):
            print("Statusaenderung abgebrochen.")
            return False
        if not istJa(bestaetigung):
            print("unverwertbare eingabe")
            return False

        erfolgreich, meldung, _ = bestellanfrage_wareneingang_buchen(
            bestellanfragenListe, baustellenListe, bestell_id, grund
        )
    else:
        erfolgreich, meldung, _ = bestellanfrage_status_aendern(
            bestellanfragenListe, bestell_id, neuer_status, grund
        )

    print(meldung)
    if erfolgreich:
        bestellanfragen_speichern(bestellanfragenListe)
        if neuer_status == BESTELLSTATUS_GELIEFERT:
            baustellen_speichern(baustellenListe)
        bestellanfragenAnzeigen(bestellanfragenListe)
    return erfolgreich


def materialbewegungenAnzeigen(baustellenListe, limit=20):
    print("\n", "-" * 35)
    print(" Materialbewegungen")
    bewegungen = materialbewegungen_sammeln(baustellenListe, limit=limit)
    if not bewegungen:
        print("Keine Materialbewegungen vorhanden")
        print("-" * 35, "\n")
        return False

    for bewegung in bewegungen:
        zeitpunkt = bewegung.get("Zeitpunkt")
        standort = bewegung.get("Standort")
        material = bewegung.get("Material")
        art = bewegung.get("Art")
        menge = bewegung.get("Menge")
        einheit = bewegung.get("Einheit")
        vorher = bewegung.get("BestandVorher")
        nachher = bewegung.get("BestandNachher")
        zeile = (
            f"- {zeitpunkt}: {standort} | {material} | "
            f"{art} {menge} {einheit} ({vorher} -> {nachher})"
        )

        referenz = bewegung.get("Referenz")
        if referenz:
            zeile += f" | {referenz}"

        notiz = bewegung.get("Notiz")
        if notiz:
            zeile += f" | {notiz}"

        print(zeile)

    print("-" * 35, "\n")
    return True


def baustelleAnlegen(baustellenListe):
    baustellen_name = textAbfragen(
        "Wie heisst die neue Baustelle: ",
        "Bitte gib einen Baustellennamen ein.",
    )
    erfolgreich, meldung = baustelle_anlegen(baustellenListe, baustellen_name)
    print(meldung)
    if erfolgreich:
        baustellen_speichern(baustellenListe)
        baustellenAnzeigen(baustellenListe)
    return erfolgreich


def baustelleUmbenennen(baustellenListe):
    zuaendern, geandert, sicherheitsfrage, _ = baustellenNamenAenderungAbfragen(
        baustellenListe
    )
    if istNein(sicherheitsfrage):
        print("Aenderung abgebrochen.")
        return False
    if not istJa(sicherheitsfrage):
        print("unverwertbare eingabe")
        return False

    erfolgreich, meldung = baustelle_umbenennen(baustellenListe, zuaendern, geandert)
    print(meldung)
    if erfolgreich:
        baustellen_speichern(baustellenListe)
        baustellenAnzeigen(baustellenListe)
    return erfolgreich


def bueroMenue(baustellenListe, bestellanfragenListe):
    while True:
        print(
            "\nBuero-Panel"
            "\n 1. Bestellanfragen anzeigen"
            "\n 2. Bestellanfrage Status aendern"
            "\n 3. Baustellen anzeigen"
            "\n 4. Baustelle anlegen"
            "\n 5. Baustelle umbenennen"
            "\n 6. Materialbewegungen anzeigen"
            "\n 7. Beenden"
        )
        auswahl = input("\nAntwort: ").strip().lower()
        if auswahl in ("1", "bestellanfragen anzeigen", "anzeigen"):
            bestellanfragenAnzeigen(bestellanfragenListe)
        elif auswahl in ("2", "status aendern", "status ändern"):
            bestellanfrageStatusAendern(bestellanfragenListe, baustellenListe)
        elif auswahl in ("3", "baustellen anzeigen", "baustellen"):
            baustellenAnzeigen(baustellenListe)
        elif auswahl in ("4", "baustelle anlegen", "anlegen"):
            baustelleAnlegen(baustellenListe)
        elif auswahl in ("5", "baustelle umbenennen", "umbenennen"):
            baustelleUmbenennen(baustellenListe)
        elif auswahl in ("6", "materialbewegungen anzeigen", "bewegungen"):
            materialbewegungenAnzeigen(baustellenListe)
        elif auswahl in ("7", "beenden"):
            baustellen_speichern(baustellenListe)
            bestellanfragen_speichern(bestellanfragenListe)
            print("Daten gespeichert. Auf wieder sehen")
            raise SystemExit(0)
        else:
            print("ungueltige eingabe")


def main():
    baustellenListe = baustellen_laden()
    if lager_sicherstellen(baustellenListe):
        baustellen_speichern(baustellenListe)
    bestellanfragenListe = bestellanfragen_laden()
    bueroMenue(baustellenListe, bestellanfragenListe)


if __name__ == "__main__":
    main()

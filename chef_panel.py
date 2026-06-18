"""
Chef-Panel fuer Gesamtuebersicht und steuernde Aufgaben.

Der Chef sieht alle wichtigen Daten gebuendelt und darf neue Baustellen sowie
Mitarbeiterbestaende pflegen.
"""

from cli_helpers import ganzzahlAbfragen, textAbfragen
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
    chef_uebersicht_erstellen,
    gesamtbestand_sammeln,
    kritische_bestaende_sammeln,
    lager_sicherstellen,
    materialbewegungen_sammeln,
    mitarbeiterbestand_setzen,
    mitarbeiteruebersicht_sammeln,
    offene_bestellanfragen_sammeln,
    offene_mitarbeiteranfragen_sammeln,
)


def gesamtbestandAnzeigen(baustellenListe):
    print("\n", "-" * 45)
    print(" Gesamtbestand")
    bestaende = gesamtbestand_sammeln(baustellenListe)
    if not bestaende:
        print("Kein Materialbestand vorhanden")
        print("-" * 45, "\n")
        return False

    for bestand in bestaende:
        material = bestand.get("Material")
        gesamtmenge = bestand.get("Gesamtmenge")
        einheit = bestand.get("Einheit")
        print(f"- {material}: {gesamtmenge} {einheit}")
        for standort in bestand.get("Standorte", []):
            print(f"  {standort.get('Standort')}: {standort.get('Menge')} {einheit}")

    print("-" * 45, "\n")
    return True


def offeneBestellungenAnzeigen(bestellanfragenListe):
    print("\n", "-" * 45)
    print(" Offene Bestellungen")
    offene_bestellungen = offene_bestellanfragen_sammeln(bestellanfragenListe)
    if not offene_bestellungen:
        print("Keine offenen Bestellungen vorhanden")
        print("-" * 45, "\n")
        return False

    for bestellung in offene_bestellungen:
        print(
            f"- #{bestellung.get('id')}: {bestellung.get('menge')} "
            f"{bestellung.get('einheit')} {bestellung.get('material')} "
            f"fuer {bestellung.get('ziel')} ({bestellung.get('status')})"
        )

    print("-" * 45, "\n")
    return True


def kritischeBestaendeAnzeigen(baustellenListe):
    print("\n", "-" * 45)
    print(" Kritische oder leere Bestaende")
    kritische_bestaende = kritische_bestaende_sammeln(baustellenListe)
    if not kritische_bestaende:
        print("Keine kritischen oder leeren Bestaende vorhanden")
        print("-" * 45, "\n")
        return False

    for bestand in kritische_bestaende:
        mindestbestand = bestand.get("Mindestbestand")
        zusatz = ""
        if isinstance(mindestbestand, int):
            zusatz = f", Mindestbestand {mindestbestand}"
        print(
            f"- {bestand.get('Standort')}: {bestand.get('Material')} "
            f"{bestand.get('Menge')} {bestand.get('Einheit')} "
            f"({bestand.get('Grund')}{zusatz})"
        )

    print("-" * 45, "\n")
    return True


def mitarbeiteruebersichtAnzeigen(baustellenListe):
    print("\n", "-" * 45)
    print(" Mitarbeiter auf Baustellen")
    uebersicht = mitarbeiteruebersicht_sammeln(baustellenListe)
    if not uebersicht:
        print("Keine Baustellen vorhanden")
        print("-" * 45, "\n")
        return False

    for eintrag in uebersicht:
        zeile = f"- {eintrag.get('Standort')}: {eintrag.get('Anzahl')} Mitarbeiter"
        if eintrag.get("Notiz"):
            zeile += f" | {eintrag.get('Notiz')}"
        print(zeile)

    print("-" * 45, "\n")
    return True


def mitarbeiteranfragenAnzeigen(mitarbeiteranfragenListe):
    print("\n", "-" * 45)
    print(" Offene Mitarbeiteranfragen")
    offene_anfragen = offene_mitarbeiteranfragen_sammeln(mitarbeiteranfragenListe)
    if not offene_anfragen:
        print("Keine offenen Mitarbeiteranfragen vorhanden")
        print("-" * 45, "\n")
        return False

    for anfrage in offene_anfragen:
        print(
            f"- #{anfrage.get('id')}: {anfrage.get('anzahl')} "
            f"{anfrage.get('rolle')} fuer {anfrage.get('ziel')} "
            f"({anfrage.get('status')}) - {anfrage.get('grund')}"
        )

    print("-" * 45, "\n")
    return True


def materialbewegungenAnzeigen(baustellenListe, limit=20):
    print("\n", "-" * 45)
    print(" Materialbewegungen")
    bewegungen = materialbewegungen_sammeln(baustellenListe, limit=limit)
    if not bewegungen:
        print("Keine Materialbewegungen vorhanden")
        print("-" * 45, "\n")
        return False

    for bewegung in bewegungen:
        print(
            f"- {bewegung.get('Zeitpunkt')}: {bewegung.get('Standort')} | "
            f"{bewegung.get('Material')} | {bewegung.get('Art')} "
            f"{bewegung.get('Menge')} {bewegung.get('Einheit')} "
            f"({bewegung.get('BestandVorher')} -> {bewegung.get('BestandNachher')})"
        )

    print("-" * 45, "\n")
    return True


def chefUebersichtAnzeigen(
    baustellenListe, bestellanfragenListe, mitarbeiteranfragenListe
):
    uebersicht = chef_uebersicht_erstellen(
        baustellenListe, bestellanfragenListe, mitarbeiteranfragenListe
    )
    print("\n", "-" * 45)
    print(" Chef-Uebersicht")
    print(f"Baustellen/Standorte: {len(uebersicht['Baustellen'])}")
    print(f"Materialpositionen gesamt: {len(uebersicht['Gesamtbestand'])}")
    print(f"Offene Bestellungen: {len(uebersicht['OffeneBestellanfragen'])}")
    print(f"Kritische/leere Bestaende: {len(uebersicht['KritischeBestaende'])}")
    print(f"Mitarbeiteranfragen offen: {len(uebersicht['OffeneMitarbeiteranfragen'])}")

    print("\nMitarbeiter je Baustelle:")
    if not uebersicht["Mitarbeiter"]:
        print("- Keine Baustellen vorhanden")
    for eintrag in uebersicht["Mitarbeiter"]:
        print(f"- {eintrag.get('Standort')}: {eintrag.get('Anzahl')}")

    print("-" * 45, "\n")
    return uebersicht


def baustelleAnlegen(baustellenListe):
    baustellen_name = textAbfragen(
        "Wie heisst die neue Baustelle: ",
        "Bitte gib einen Baustellennamen ein.",
    )
    erfolgreich, meldung = baustelle_anlegen(baustellenListe, baustellen_name)
    print(meldung)
    if erfolgreich:
        baustellen_speichern(baustellenListe)
    return erfolgreich


def mitarbeiterbestandEintragen(baustellenListe):
    baustellen_name = textAbfragen(
        "Fuer welche Baustelle soll der Mitarbeiterbestand gesetzt werden: ",
        "Bitte gib einen Baustellennamen ein.",
    )
    anzahl = ganzzahlAbfragen("Wie viele Mitarbeiter sind dort aktuell: ", minimum=0)
    notiz = input("Notiz optional: ").strip()

    erfolgreich, meldung = mitarbeiterbestand_setzen(
        baustellenListe, baustellen_name, anzahl, notiz
    )
    print(meldung)
    if erfolgreich:
        baustellen_speichern(baustellenListe)
        mitarbeiteruebersichtAnzeigen(baustellenListe)
    return erfolgreich


def chefMenue(baustellenListe, bestellanfragenListe, mitarbeiteranfragenListe):
    while True:
        print(
            "\nChef-Panel"
            "\n 1. Chef-Uebersicht anzeigen"
            "\n 2. Gesamtbestand anzeigen"
            "\n 3. Offene Bestellungen anzeigen"
            "\n 4. Kritische oder leere Bestaende anzeigen"
            "\n 5. Baustelle anlegen"
            "\n 6. Mitarbeiterbestand eintragen"
            "\n 7. Mitarbeiteruebersicht anzeigen"
            "\n 8. Mitarbeiteranfragen anzeigen"
            "\n 9. Materialbewegungen anzeigen"
            "\n 10. Beenden"
        )
        auswahl = input("\nAntwort: ").strip().lower()
        if auswahl in ("1", "uebersicht", "chef-uebersicht"):
            chefUebersichtAnzeigen(
                baustellenListe, bestellanfragenListe, mitarbeiteranfragenListe
            )
        elif auswahl in ("2", "gesamtbestand", "bestand"):
            gesamtbestandAnzeigen(baustellenListe)
        elif auswahl in ("3", "offene bestellungen", "bestellungen"):
            offeneBestellungenAnzeigen(bestellanfragenListe)
        elif auswahl in ("4", "kritische bestaende", "kritisch"):
            kritischeBestaendeAnzeigen(baustellenListe)
        elif auswahl in ("5", "baustelle anlegen", "anlegen"):
            baustelleAnlegen(baustellenListe)
        elif auswahl in ("6", "mitarbeiterbestand", "mitarbeiter eintragen"):
            mitarbeiterbestandEintragen(baustellenListe)
        elif auswahl in ("7", "mitarbeiteruebersicht", "mitarbeiter"):
            mitarbeiteruebersichtAnzeigen(baustellenListe)
        elif auswahl in ("8", "mitarbeiteranfragen", "personalbedarf"):
            mitarbeiteranfragenAnzeigen(mitarbeiteranfragenListe)
        elif auswahl in ("9", "materialbewegungen", "bewegungen"):
            materialbewegungenAnzeigen(baustellenListe)
        elif auswahl in ("10", "beenden"):
            baustellen_speichern(baustellenListe)
            bestellanfragen_speichern(bestellanfragenListe)
            mitarbeiteranfragen_speichern(mitarbeiteranfragenListe)
            print("Daten gespeichert. Auf wieder sehen")
            raise SystemExit(0)
        else:
            print("ungueltige eingabe")


def main():
    baustellenListe = baustellen_laden()
    if lager_sicherstellen(baustellenListe):
        baustellen_speichern(baustellenListe)
    bestellanfragenListe = bestellanfragen_laden()
    mitarbeiteranfragenListe = mitarbeiteranfragen_laden()
    chefMenue(baustellenListe, bestellanfragenListe, mitarbeiteranfragenListe)


if __name__ == "__main__":
    main()

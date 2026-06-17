"""
Material eintragen mit Menge in JSON und Menü aufrufbar:
eintragen, einsehen, ändern, bestellen, beenden.
"""

from datenspeicher import (
    baustellen_laden,
    baustellen_speichern,
    bestellanfragen_laden,
    bestellanfragen_speichern,
)
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


def istJa(eingabe):
    return eingabe.strip().lower() in ("j", "ja")


def istNein(eingabe):
    return eingabe.strip().lower() in ("n", "nein")


def ganzzahlAbfragen(frage, minimum=None):
    while True:
        try:
            zahl = int(input(frage))
        except ValueError:
            print("Bitte gib eine ganze Zahl ein.")
            continue

        if minimum is not None and zahl < minimum:
            print(f"Bitte gib mindestens {minimum} ein.")
            continue

        return zahl


def textAbfragen(frage, fehlermeldung):
    while True:
        antwort = input(frage).strip()
        if antwort:
            return antwort
        print(fehlermeldung)


def baustelleAbfragen():
    return textAbfragen(
        "Auf welcher baustelle bist du im moment: ",
        "Bitte gib einen Baustellennamen ein.",
    )


def materialUndMengeAbfrage():
    materialname = textAbfragen(
        "welches material möchtest du eintragen: ",
        "Bitte gib einen Materialnamen ein.",
    )
    materialmenge = ganzzahlAbfragen(
        f"wie viel {materialname} möchtest du eintragen: "
    )
    materialeinheit = textAbfragen(
        f"welche einheit hat {materialname} mit menge {materialmenge}: ",
        "Bitte gib eine Einheit ein.",
    )

    return materialname, materialmenge, materialeinheit


def bestellDatenAbfragen():
    ziel = textAbfragen(
        "Für welche Baustelle oder welchen Standort wird Material gebraucht: ",
        "Bitte gib ein Ziel an.",
    )
    materialname = textAbfragen(
        "Welches Material wird gebraucht: ",
        "Bitte gib einen Materialnamen ein.",
    )
    materialmenge = ganzzahlAbfragen(
        f"Wie viel {materialname} wird gebraucht: ", minimum=1
    )
    materialeinheit = textAbfragen(
        f"Welche Einheit hat {materialname} mit Menge {materialmenge}: ",
        "Bitte gib eine Einheit ein.",
    )

    return ziel, materialname, materialmenge, materialeinheit


def menueverweis(baustellenListe, bestellanfragenListe):
    print(
        "\nWas möchtest du heute machen? "
        "\n 1. Material eintragen"
        "\n 2. Material Liste anzeigen"
        "\n 3. Material ändern"
        "\n 4. Lager anzeigen"
        "\n 5. Material bestellen"
        "\n 6. Beenden"
    )
    menue = str(input("\nAntwort: ")).strip().lower()
    if menue in ("eintragen", "material eintragen", "1"):
        baustellenInput = baustelleAbfragen()
        materialEintragen(baustellenListe, baustellenInput)
        zurueck(baustellenListe, bestellanfragenListe)
    elif menue in ("liste anzeigen", "material anzeigen", "2"):
        baustellenInput = baustelleAbfragen()
        materialAnzeigen(baustellenListe, baustellenInput)
        zurueck(baustellenListe, bestellanfragenListe)
    elif menue in (
        "aus liste entfernen",
        "material ändern",
        "material aendern",
        "ändern",
        "aendern",
        "3",
    ):
        baustellenInput = baustelleAbfragen()
        allgemeinAendernabfragen(baustellenListe, bestellanfragenListe, baustellenInput)
        zurueck(baustellenListe, bestellanfragenListe)
    elif menue in ("lager anzeigen", "lager", "4"):
        lagerAnzeigen(baustellenListe)
        zurueck(baustellenListe, bestellanfragenListe)
    elif menue in ("material bestellen", "bestellen", "5"):
        bestellMenue(baustellenListe, bestellanfragenListe)
    elif menue in ("beenden", "6"):
        beenden(baustellenListe, bestellanfragenListe)
    else:
        print("ungültige eingabe")
        menueverweis(baustellenListe, bestellanfragenListe)


def materialEintragen(baustellenListe, baustellenInput):
    materialname, materialmenge, materialeinheit = materialUndMengeAbfrage()
    erfolgreich, meldung = material_eintragen(
        baustellenListe, baustellenInput, materialname, materialmenge, materialeinheit
    )
    print(meldung)
    if erfolgreich:
        baustellen_speichern(baustellenListe)


def materialAnzeigen(baustellenListe, baustellenInput):
    print("\n", "-" * 25)
    print(f" Standort: {baustellenInput}")
    materialien = materialien_fuer_baustelle(baustellenListe, baustellenInput)
    if materialien is None:
        print("Standort nicht gefunden")
        print("-" * 25, "\n")
        return False

    if not materialien:
        print("Kein Material vorhanden")
        print("-" * 25, "\n")
        return True

    for name, info in materialien.items():
        menge = info.get("Menge")
        einheit = info.get("Einheit")
        print(f"- {name}: {menge} {einheit}")
    print("-" * 25, "\n")
    return True


def lagerAnzeigen(baustellenListe):
    lager_sicherstellen(baustellenListe)
    baustellen_speichern(baustellenListe)
    materialAnzeigen(baustellenListe, FIRMENLAGER_NAME)


def allgemeinAendernabfragen(baustellenListe, bestellanfragenListe, baustellenInput):
    if not materialAnzeigen(baustellenListe, baustellenInput):
        return

    temporaereListeMaterial = material_namen(baustellenListe, baustellenInput)
    temporaereListeBaustelle = baustellen_namen(baustellenListe)
    temporaereListeEinheit, temporaereListeMenge = mengen_und_einheiten(
        baustellenListe, baustellenInput
    )
    print("was möchtest du ändern ?")
    print(
        f"\n 1. Baustellennamen{temporaereListeBaustelle},"
        f"\n 2. Material{temporaereListeMaterial},"
        f"\n 3. Menge{temporaereListeMenge},"
        f"\n 4. Einheiten{temporaereListeEinheit},"
        "\n 5. Nichts(Beenden)"
    )
    abfrage = input("\nAntwort: ").strip().lower()
    if abfrage in ("1", "baustellennamen", "baustellen"):
        baustelleAendernabfragen(
            baustellenListe, baustellenInput, abfrage, temporaereListeBaustelle
        )
    elif abfrage in ("2", "material"):
        materialAendernabfragen(
            baustellenListe, baustellenInput, abfrage, temporaereListeMaterial
        )
    elif abfrage in ("3", "menge"):
        mengeAendernabfragen(
            baustellenListe,
            baustellenInput,
            abfrage,
            temporaereListeMaterial,
            temporaereListeMenge,
        )
    elif abfrage in ("4", "einheiten", "einheit"):
        einheitAendernabfragen(
            baustellenListe,
            baustellenInput,
            temporaereListeMaterial,
            temporaereListeEinheit,
        )
    elif abfrage in ("5", "nichts", "beenden"):
        beenden(baustellenListe, bestellanfragenListe)
    else:
        print("unverwertbare eingabe")


def baustelleAendernabfragen(
    baustellenListe, baustellenInput, abfrage, temporaereListeBaustelle
):
    print(
        f"\nMöchtest du hierraus {abfrage}: "
        f"{temporaereListeBaustelle} etwas ändern? (J/N)"
    )
    aenderninput = input("Antwort: ")
    if istJa(aenderninput):
        modus = modus1(False)
        zuaendern, geandert, sicherheitsfrage, materialname = aendernabfragen(modus)
        baustellennamenaendern(
            baustellenListe,
            baustellenInput,
            zuaendern,
            geandert,
            sicherheitsfrage,
            materialname,
        )
    elif istNein(aenderninput):
        print("Änderung abgebrochen.")
    else:
        print("unverwertbare eingabe")


def materialAendernabfragen(
    baustellenListe, baustellenInput, abfrage, temporaereListeMaterial
):
    print(
        f"\nMöchtest du hierraus {abfrage}: "
        f"{temporaereListeMaterial} etwas ändern? (J/N)"
    )
    aenderninput = input("Antwort: ")
    if istJa(aenderninput):
        modus = modus1(False)
        zuaendern, geandert, sicherheitsfrage, materialname = aendernabfragen(modus)
        materialnamenaendern(
            baustellenListe,
            baustellenInput,
            zuaendern,
            geandert,
            sicherheitsfrage,
            materialname,
        )
    elif istNein(aenderninput):
        print("Änderung abgebrochen.")
    else:
        print("unverwertbare eingabe")


def mengeAendernabfragen(
    baustellenListe,
    baustellenInput,
    abfrage,
    temporaereListeMaterial,
    temporaereListeMenge,
):
    print(
        f"\nMöchtest du hierraus {abfrage}: "
        f"{temporaereListeMaterial}:{temporaereListeMenge} etwas ändern? (J/N)"
    )
    aenderninput = input("Antwort: ")
    if istJa(aenderninput):
        modus = modus1(True)
        zuaendern, geandert, sicherheitsfrage, materialname = aendernabfragen(modus)
        mengenaendern(
            baustellenListe,
            baustellenInput,
            zuaendern,
            geandert,
            sicherheitsfrage,
            materialname,
        )
    elif istNein(aenderninput):
        print("Änderung abgebrochen.")
    else:
        print("unverwertbare eingabe")


def einheitAendernabfragen(
    baustellenListe, baustellenInput, temporaereListeMaterial, temporaereListeEinheit
):
    print(
        f"\nMöchtest du hierraus Einheiten: "
        f"{temporaereListeMaterial}:{temporaereListeEinheit} etwas ändern? (J/N)"
    )
    aenderninput = input("Antwort: ")
    if istJa(aenderninput):
        materialname = input("Für welches Material soll die Einheit geändert werden: ")
        materialname = materialname.strip()
        neueEinheit = input("Welche neue Einheit soll eingetragen werden: ").strip()
        print(
            f"\nBist du sicher das die Einheit von {materialname} "
            f"zu {neueEinheit} geändert werden soll? (J/N)"
        )
        sicherheitsfrage = input("Antwort: ")
        einheitaendern(
            baustellenListe, baustellenInput, materialname, neueEinheit, sicherheitsfrage
        )
    elif istNein(aenderninput):
        print("Änderung abgebrochen.")
    else:
        print("unverwertbare eingabe")


def bestellMenue(baustellenListe, bestellanfragenListe):
    print(
        "\nMaterial bestellen"
        "\n 1. Bestellanfrage erstellen"
        "\n 2. Bestellanfragen anzeigen"
        "\n 3. Zurück zum Hauptmenü"
    )
    auswahl = input("\nAntwort: ").strip().lower()
    if auswahl in ("1", "bestellanfrage erstellen", "erstellen"):
        bestellanfrageErstellen(baustellenListe, bestellanfragenListe)
        zurueck(baustellenListe, bestellanfragenListe)
    elif auswahl in ("2", "bestellanfragen anzeigen", "anzeigen"):
        bestellanfragenAnzeigen(bestellanfragenListe)
        zurueck(baustellenListe, bestellanfragenListe)
    elif auswahl in ("3", "zurück", "zurueck"):
        menueverweis(baustellenListe, bestellanfragenListe)
    else:
        print("ungültige eingabe")
        bestellMenue(baustellenListe, bestellanfragenListe)


def bestellanfrageErstellen(baustellenListe, bestellanfragenListe):
    ziel, materialname, materialmenge, materialeinheit = bestellDatenAbfragen()
    if ziel not in baustellenListe:
        print("Hinweis: Das Ziel existiert noch nicht als Baustelle oder Lager.")

    print(
        f"\nBestellanfrage: {materialmenge} {materialeinheit} "
        f"{materialname} für {ziel} erstellen? (J/N)"
    )
    sicherheitsfrage = input("Antwort: ")
    if istNein(sicherheitsfrage):
        print("Bestellanfrage abgebrochen.")
        return
    if not istJa(sicherheitsfrage):
        print("unverwertbare eingabe")
        return

    erfolgreich, meldung, bestellanfrage = bestellanfrage_erstellen(
        bestellanfragenListe, ziel, materialname, materialmenge, materialeinheit
    )
    print(meldung)
    if erfolgreich:
        bestellanfragen_speichern(bestellanfragenListe)
        print(f"Bestellnummer: {bestellanfrage['id']}")


def bestellanfragenAnzeigen(bestellanfragenListe):
    print("\n", "-" * 25)
    print(" Bestellanfragen")
    if not bestellanfragenListe:
        print("Keine Bestellanfragen vorhanden")
        print("-" * 25, "\n")
        return

    for bestellanfrage in bestellanfragenListe:
        bestell_id = bestellanfrage.get("id")
        ziel = bestellanfrage.get("ziel")
        material = bestellanfrage.get("material")
        menge = bestellanfrage.get("menge")
        einheit = bestellanfrage.get("einheit")
        status = bestellanfrage.get("status")
        print(f"- #{bestell_id}: {menge} {einheit} {material} für {ziel} ({status})")
    print("-" * 25, "\n")


def modus1(daten):
    if daten:
        return "menge"
    return None


def aendernabfragen(modus):
    materialname = None
    if modus == "menge":
        print("wie ist der zugehörige material name? ")
        materialname = input("Antwort: ").strip()
        zuaendern = input("Bitte gib die zu ändernde Menge ein: ")
        print("\nWie lautet die neue Menge? ")
        geandert = input("Antwort: ")
    else:
        zuaendern = input("Bitte gib den zu ändernden namen ein: ").strip()
        print("\nWie soll der neue name heißen ? ")
        geandert = input("Antwort: ").strip()

    print(f"\nBist du sicher das {zuaendern} zu {geandert} geändert werden soll? (J/N)")
    sicherheitsfrage = input("Antwort: ")
    return zuaendern, geandert, sicherheitsfrage, materialname


def baustellennamenaendern(
    baustellenListe, baustellenInput, zuaendern, geandert, sicherheitsfrage, materialname
):
    if istJa(sicherheitsfrage):
        erfolgreich, meldung = baustelle_umbenennen(
            baustellenListe, zuaendern, geandert
        )
        print(meldung)
        if erfolgreich:
            baustellen_speichern(baustellenListe)
            anzeigeBaustelle = (
                geandert if baustellenInput == zuaendern else baustellenInput
            )
            materialAnzeigen(baustellenListe, anzeigeBaustelle)
    elif istNein(sicherheitsfrage):
        print("Änderung abgebrochen.")


def materialnamenaendern(
    baustellenListe, baustellenInput, zuaendern, geandert, sicherheitsfrage, materialname
):
    if istJa(sicherheitsfrage):
        erfolgreich, meldung = material_umbenennen(
            baustellenListe, baustellenInput, zuaendern, geandert
        )
        print(meldung)
        if erfolgreich:
            baustellen_speichern(baustellenListe)
            materialAnzeigen(baustellenListe, baustellenInput)
    elif istNein(sicherheitsfrage):
        print("Änderung abgebrochen.")


def mengenaendern(
    baustellenListe, baustellenInput, zuaendern, geandert, sicherheitsfrage, materialname
):
    if istJa(sicherheitsfrage):
        try:
            neueMenge = int(geandert)
        except ValueError:
            print("Bitte gib eine ganze Zahl ein.")
            return

        erfolgreich, meldung = menge_aendern(
            baustellenListe, baustellenInput, materialname, neueMenge
        )
        print(meldung)
        if erfolgreich:
            baustellen_speichern(baustellenListe)
            materialAnzeigen(baustellenListe, baustellenInput)
    elif istNein(sicherheitsfrage):
        print("Änderung abgebrochen.")


def einheitaendern(
    baustellenListe, baustellenInput, materialname, neueEinheit, sicherheitsfrage
):
    if istJa(sicherheitsfrage):
        erfolgreich, meldung = einheit_aendern(
            baustellenListe, baustellenInput, materialname, neueEinheit
        )
        print(meldung)
        if erfolgreich:
            baustellen_speichern(baustellenListe)
            materialAnzeigen(baustellenListe, baustellenInput)
    elif istNein(sicherheitsfrage):
        print("Änderung abgebrochen.")


def zurueck(baustellenListe, bestellanfragenListe):
    abfragezurueck = input("Möchtest du zurück ins hauptmenue? (J/N): ")
    if istJa(abfragezurueck):
        menueverweis(baustellenListe, bestellanfragenListe)
    elif istNein(abfragezurueck):
        abfragebeenden = input("Möchtest du beenden? (J/N)")
        if istJa(abfragebeenden):
            beenden(baustellenListe, bestellanfragenListe)
        elif istNein(abfragebeenden):
            print("es gibt keine möglichkeit mehr")
            beenden(baustellenListe, bestellanfragenListe)
        else:
            print("unverwertbare eingabe")
            zurueck(baustellenListe, bestellanfragenListe)
    else:
        print("unverwertbare eingabe")
        zurueck(baustellenListe, bestellanfragenListe)


def beenden(baustellenListe, bestellanfragenListe):
    baustellen_speichern(baustellenListe)
    bestellanfragen_speichern(bestellanfragenListe)
    print("Daten gespeichert. Auf wieder sehen")
    raise SystemExit(0)


def main():
    baustellenListe = baustellen_laden()
    if lager_sicherstellen(baustellenListe):
        baustellen_speichern(baustellenListe)
    bestellanfragenListe = bestellanfragen_laden()
    menueverweis(baustellenListe, bestellanfragenListe)


if __name__ == "__main__":
    main()

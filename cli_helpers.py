from material_logik import (
    BUCHUNGSART_KORREKTUR,
    baustellen_namen,
    baustellen_vorschlaege,
    buchungsart_normalisieren,
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


def baustelleIstBekannt(baustellenListe, baustellenInput):
    return baustellenInput in baustellen_namen(baustellenListe)


def baustelleAbfragen(
    baustellenListe=None,
    neueBaustelleErlaubt=True,
    frage="Auf welcher baustelle bist du im moment: ",
    fehlermeldung="Bitte gib einen Baustellennamen ein.",
):
    while True:
        baustellenInput = textAbfragen(frage, fehlermeldung)
        if baustellenListe is None or baustelleIstBekannt(
            baustellenListe, baustellenInput
        ):
            return baustellenInput

        vorschlaege = baustellen_vorschlaege(
            baustellenListe, baustellenInput, limit=1
        )
        if vorschlaege:
            vorschlag, aehnlichkeit = vorschlaege[0]
            print(
                f'Meintest du "{vorschlag}"? '
                f"({aehnlichkeit}% Uebereinstimmung) (J/N)"
            )
            bestaetigung = input("Antwort: ")
            if istJa(bestaetigung):
                return vorschlag
            if not istNein(bestaetigung):
                print("unverwertbare eingabe")
                continue

        if neueBaustelleErlaubt:
            return baustellenInput

        print("Standort nicht gefunden. Bitte erneut eingeben.")


def buchungsartAbfragen():
    print(
        "\nWelche Materialbuchung moechtest du erfassen?"
        "\n 1. Zugang"
        "\n 2. Abgang"
        "\n 3. Korrektur"
    )
    while True:
        buchungsart = buchungsart_normalisieren(input("Antwort: "))
        if buchungsart is not None:
            return buchungsart
        print("Bitte waehle Zugang, Abgang oder Korrektur.")


def materialUndMengeAbfrage():
    buchungsart = buchungsartAbfragen()
    materialname = textAbfragen(
        "welches material möchtest du eintragen: ",
        "Bitte gib einen Materialnamen ein.",
    )
    mindestmenge = 0 if buchungsart == BUCHUNGSART_KORREKTUR else 1
    materialmenge = ganzzahlAbfragen(
        f"wie viel {materialname} möchtest du eintragen: ", minimum=mindestmenge
    )
    materialeinheit = textAbfragen(
        f"welche einheit hat {materialname} mit menge {materialmenge}: ",
        "Bitte gib eine Einheit ein.",
    )

    return buchungsart, materialname, materialmenge, materialeinheit


def bestellDatenAbfragen(baustellenListe):
    ziel = baustelleAbfragen(
        baustellenListe,
        True,
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


def mitarbeiterAnfrageDatenAbfragen(baustellenListe):
    ziel = baustelleAbfragen(
        baustellenListe,
        False,
        "Fuer welche Baustelle werden mehr Mitarbeiter gebraucht: ",
        "Bitte gib eine bekannte Baustelle ein.",
    )
    anzahl = ganzzahlAbfragen(
        "Wie viele zusaetzliche Mitarbeiter werden gebraucht: ", minimum=1
    )
    rolle = textAbfragen(
        "Welche Rolle oder welcher Einsatzbereich wird gebraucht: ",
        "Bitte gib eine Rolle oder einen Einsatzbereich ein.",
    )
    grund = textAbfragen(
        "Warum werden mehr Mitarbeiter gebraucht: ",
        "Bitte gib einen Grund ein.",
    )

    return ziel, anzahl, rolle, grund


def baustellenNamenAenderungAbfragen(baustellenListe):
    zuaendern = baustelleAbfragen(
        baustellenListe,
        False,
        "Welche Baustelle soll umbenannt werden: ",
        "Bitte gib einen Baustellennamen ein.",
    )
    geandert = textAbfragen(
        "\nWie soll der neue name heissen ? ",
        "Bitte gib einen neuen Baustellennamen ein.",
    )

    print(f"\nBist du sicher das {zuaendern} zu {geandert} geaendert werden soll? (J/N)")
    sicherheitsfrage = input("Antwort: ")
    return zuaendern, geandert, sicherheitsfrage, None

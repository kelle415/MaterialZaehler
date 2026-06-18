from datetime import datetime, timezone
from difflib import SequenceMatcher
import unicodedata


FIRMENLAGER_NAME = "Firmenlager"
BUCHUNGSART_ZUGANG = "zugang"
BUCHUNGSART_ABGANG = "abgang"
BUCHUNGSART_KORREKTUR = "korrektur"
BESTELLSTATUS_OFFEN = "offen"
BESTELLSTATUS_BESTELLT = "bestellt"
BESTELLSTATUS_GELIEFERT = "geliefert"
BESTELLSTATUS_ABGESCHLOSSEN = "abgeschlossen"
BESTELLSTATUS_STORNIERT = "storniert"
BESTELLSTATUS_WERTE = (
    BESTELLSTATUS_OFFEN,
    BESTELLSTATUS_BESTELLT,
    BESTELLSTATUS_GELIEFERT,
    BESTELLSTATUS_ABGESCHLOSSEN,
    BESTELLSTATUS_STORNIERT,
)
MITARBEITERANFRAGE_STATUS_OFFEN = "offen"
MITARBEITERANFRAGE_STATUS_EINGEPLANT = "eingeplant"
MITARBEITERANFRAGE_STATUS_ERLEDIGT = "erledigt"
MITARBEITERANFRAGE_STATUS_STORNIERT = "storniert"
MITARBEITERANFRAGE_OFFENE_STATUS = (
    MITARBEITERANFRAGE_STATUS_OFFEN,
    MITARBEITERANFRAGE_STATUS_EINGEPLANT,
)


def zeitpunkt_utc():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ist_standort(eintrag):
    return isinstance(eintrag, dict) and "Material" in eintrag


def baustellen_namen(baustellen_liste):
    return [
        name for name, eintrag in baustellen_liste.items() if ist_standort(eintrag)
    ]


def text_normalisieren(text):
    text = str(text).strip().casefold()
    text = unicodedata.normalize("NFKD", text)
    return "".join(
        zeichen for zeichen in text if not unicodedata.combining(zeichen)
    ).strip()


def buchungsart_normalisieren(eingabe):
    buchungsart = text_normalisieren(eingabe)
    if buchungsart in ("1", "zugang", "addieren", "plus"):
        return BUCHUNGSART_ZUGANG
    if buchungsart in ("2", "abgang", "abziehen", "minus"):
        return BUCHUNGSART_ABGANG
    if buchungsart in ("3", "korrektur", "korrigieren", "setzen"):
        return BUCHUNGSART_KORREKTUR
    return None


def bestellstatus_normalisieren(eingabe):
    status = text_normalisieren(eingabe)
    status_mapping = {
        "1": BESTELLSTATUS_OFFEN,
        BESTELLSTATUS_OFFEN: BESTELLSTATUS_OFFEN,
        "2": BESTELLSTATUS_BESTELLT,
        BESTELLSTATUS_BESTELLT: BESTELLSTATUS_BESTELLT,
        "3": BESTELLSTATUS_GELIEFERT,
        BESTELLSTATUS_GELIEFERT: BESTELLSTATUS_GELIEFERT,
        "4": BESTELLSTATUS_ABGESCHLOSSEN,
        BESTELLSTATUS_ABGESCHLOSSEN: BESTELLSTATUS_ABGESCHLOSSEN,
        "5": BESTELLSTATUS_STORNIERT,
        BESTELLSTATUS_STORNIERT: BESTELLSTATUS_STORNIERT,
    }
    return status_mapping.get(status)


def bewegung_erstellen(
    buchungsart,
    menge,
    einheit,
    bestand_vorher,
    bestand_nachher,
    referenz=None,
    notiz=None,
):
    bewegung = {
        "Art": buchungsart,
        "Menge": menge,
        "Einheit": einheit,
        "BestandVorher": bestand_vorher,
        "BestandNachher": bestand_nachher,
        "Zeitpunkt": zeitpunkt_utc(),
    }
    if referenz:
        bewegung["Referenz"] = referenz
    if notiz:
        bewegung["Notiz"] = notiz
    return bewegung


def einheiten_stimmen_ueberein(einheit, vorhandene_einheit):
    return text_normalisieren(einheit) == text_normalisieren(vorhandene_einheit)


def baustellen_vorschlaege(
    baustellen_liste, eingabe, mindest_aehnlichkeit=60, limit=3
):
    suchtext = text_normalisieren(eingabe)
    if not suchtext:
        return []

    vorschlaege = []
    for baustellen_name in baustellen_namen(baustellen_liste):
        kandidat = text_normalisieren(baustellen_name)
        aehnlichkeit = round(SequenceMatcher(None, suchtext, kandidat).ratio() * 100)
        if aehnlichkeit >= mindest_aehnlichkeit:
            vorschlaege.append((baustellen_name, aehnlichkeit))

    vorschlaege.sort(key=lambda vorschlag: (-vorschlag[1], vorschlag[0]))
    return vorschlaege[:limit]


def lager_sicherstellen(baustellen_liste):
    if FIRMENLAGER_NAME not in baustellen_liste:
        baustellen_liste[FIRMENLAGER_NAME] = {"Typ": "Lager", "Material": {}}
        return True

    lager = baustellen_liste[FIRMENLAGER_NAME]
    if not isinstance(lager, dict):
        baustellen_liste[FIRMENLAGER_NAME] = {"Typ": "Lager", "Material": {}}
        return True

    geaendert = False
    if lager.get("Typ") != "Lager":
        lager["Typ"] = "Lager"
        geaendert = True
    if "Material" not in lager or not isinstance(lager["Material"], dict):
        lager["Material"] = {}
        geaendert = True

    return geaendert


def baustelle_anlegen(baustellen_liste, baustellen_name):
    if not str(baustellen_name).strip():
        return False, "Bitte gib einen Baustellennamen ein"
    if baustellen_name in baustellen_liste:
        return False, "Dieser Baustellenname existiert bereits"

    baustellen_liste[baustellen_name] = {
        "Typ": "Baustelle",
        "Material": {},
        "Mitarbeiter": {"Anzahl": 0, "Aktualisiert": zeitpunkt_utc()},
    }
    return True, "Baustelle angelegt"


def materialien_fuer_baustelle(baustellen_liste, baustellen_name):
    baustelle = baustellen_liste.get(baustellen_name)
    if baustelle is None or not isinstance(baustelle, dict):
        return None
    return baustelle.get("Material", {})


def material_namen(baustellen_liste, baustellen_name):
    materialien = materialien_fuer_baustelle(baustellen_liste, baustellen_name)
    if materialien is None:
        return []
    return list(materialien.keys())


def mengen_und_einheiten(baustellen_liste, baustellen_name):
    mengen = []
    einheiten = []
    materialien = materialien_fuer_baustelle(baustellen_liste, baustellen_name)
    if materialien is None:
        return einheiten, mengen

    for info in materialien.values():
        mengen.append(info.get("Menge"))
        einheiten.append(info.get("Einheit"))

    return einheiten, mengen


def material_eintragen(
    baustellen_liste,
    baustellen_name,
    material_name,
    menge,
    einheit,
    buchungsart=BUCHUNGSART_ZUGANG,
    referenz=None,
    notiz=None,
):
    buchungsart = buchungsart_normalisieren(buchungsart)
    if buchungsart is None:
        return False, "Buchungsart ist ungueltig"
    if menge < 0:
        return False, "Bitte gib eine Menge ab 0 ein"
    if buchungsart != BUCHUNGSART_KORREKTUR and menge == 0:
        return False, "Bitte gib eine Menge groesser als 0 ein"

    baustelle = baustellen_liste.setdefault(
        baustellen_name, {"Typ": "Baustelle", "Material": {}}
    )
    if not isinstance(baustelle, dict):
        return False, "Standortdaten sind ungueltig"

    materialien = baustelle.setdefault("Material", {})
    if not isinstance(materialien, dict):
        return False, "Materialdaten sind ungueltig"

    material = materialien.get(material_name)
    if material is None:
        if buchungsart == BUCHUNGSART_ABGANG:
            return False, "Material nicht gefunden"

        bestand_vorher = 0
        bestand_nachher = menge
        materialien[material_name] = {
            "Menge": bestand_nachher,
            "Einheit": einheit,
            "Bewegungen": [
                bewegung_erstellen(
                    buchungsart,
                    menge,
                    einheit,
                    bestand_vorher,
                    bestand_nachher,
                    referenz,
                    notiz,
                )
            ],
        }
        return True, "Materialbuchung gespeichert"

    if not isinstance(material, dict):
        return False, "Materialdaten sind ungueltig"

    bestand_vorher = material.get("Menge")
    vorhandene_einheit = material.get("Einheit")
    if not isinstance(bestand_vorher, int):
        return False, "Materialmenge ist ungueltig"
    if not vorhandene_einheit:
        return False, "Materialeinheit ist ungueltig"
    if not einheiten_stimmen_ueberein(einheit, vorhandene_einheit):
        return False, "Einheit stimmt nicht mit vorhandener Einheit ueberein"

    if buchungsart == BUCHUNGSART_ZUGANG:
        bestand_nachher = bestand_vorher + menge
    elif buchungsart == BUCHUNGSART_ABGANG:
        bestand_nachher = bestand_vorher - menge
        if bestand_nachher < 0:
            return False, "Bestand reicht nicht aus"
    else:
        bestand_nachher = menge

    bewegungen = material.setdefault("Bewegungen", [])
    if not isinstance(bewegungen, list):
        return False, "Bewegungsdaten sind ungueltig"

    material["Menge"] = bestand_nachher
    material["Einheit"] = vorhandene_einheit
    bewegungen.append(
        bewegung_erstellen(
            buchungsart,
            menge,
            vorhandene_einheit,
            bestand_vorher,
            bestand_nachher,
            referenz,
            notiz,
        )
    )
    return True, "Materialbuchung gespeichert"


def materialbewegungen_sammeln(baustellen_liste, baustellen_name=None, limit=None):
    if baustellen_name is None:
        standort_namen = baustellen_namen(baustellen_liste)
    else:
        standort_namen = [baustellen_name]

    alle_bewegungen = []
    for standort_name in standort_namen:
        materialien = materialien_fuer_baustelle(baustellen_liste, standort_name)
        if not isinstance(materialien, dict):
            continue

        for material_name, material in materialien.items():
            if not isinstance(material, dict):
                continue

            bewegungen = material.get("Bewegungen", [])
            if not isinstance(bewegungen, list):
                continue

            for bewegung in bewegungen:
                if not isinstance(bewegung, dict):
                    continue

                eintrag = dict(bewegung)
                eintrag["Standort"] = standort_name
                eintrag["Material"] = material_name
                alle_bewegungen.append(eintrag)

    alle_bewegungen.sort(
        key=lambda bewegung: bewegung.get("Zeitpunkt") or "", reverse=True
    )
    if limit is not None:
        return alle_bewegungen[:limit]
    return alle_bewegungen


def gesamtbestand_sammeln(baustellen_liste):
    bestaende = {}
    for standort_name in baustellen_namen(baustellen_liste):
        materialien = materialien_fuer_baustelle(baustellen_liste, standort_name)
        if not isinstance(materialien, dict):
            continue

        for material_name, material in materialien.items():
            if not isinstance(material, dict):
                continue

            menge = material.get("Menge")
            einheit = material.get("Einheit")
            if not isinstance(menge, int) or not einheit:
                continue

            schluessel = (text_normalisieren(material_name), text_normalisieren(einheit))
            if schluessel not in bestaende:
                bestaende[schluessel] = {
                    "Material": material_name,
                    "Einheit": einheit,
                    "Gesamtmenge": 0,
                    "Standorte": [],
                }

            bestaende[schluessel]["Gesamtmenge"] += menge
            bestaende[schluessel]["Standorte"].append(
                {"Standort": standort_name, "Menge": menge}
            )

    return sorted(
        bestaende.values(),
        key=lambda bestand: (
            text_normalisieren(bestand["Material"]),
            text_normalisieren(bestand["Einheit"]),
        ),
    )


def kritische_bestaende_sammeln(baustellen_liste):
    kritische_bestaende = []
    for standort_name in baustellen_namen(baustellen_liste):
        materialien = materialien_fuer_baustelle(baustellen_liste, standort_name)
        if not isinstance(materialien, dict):
            continue

        for material_name, material in materialien.items():
            if not isinstance(material, dict):
                continue

            menge = material.get("Menge")
            einheit = material.get("Einheit")
            mindestbestand = material.get("Mindestbestand")
            if not isinstance(menge, int):
                continue

            grund = None
            if menge <= 0:
                grund = "leer"
            elif isinstance(mindestbestand, int) and menge <= mindestbestand:
                grund = "unter Mindestbestand"

            if grund:
                kritische_bestaende.append(
                    {
                        "Standort": standort_name,
                        "Material": material_name,
                        "Menge": menge,
                        "Einheit": einheit,
                        "Mindestbestand": mindestbestand,
                        "Grund": grund,
                    }
                )

    return sorted(
        kritische_bestaende,
        key=lambda bestand: (
            bestand["Standort"],
            text_normalisieren(bestand["Material"]),
        ),
    )


def offene_bestellanfragen_sammeln(bestellanfragen_liste):
    offene_status = {BESTELLSTATUS_OFFEN, BESTELLSTATUS_BESTELLT}
    return [
        bestellanfrage
        for bestellanfrage in bestellanfragen_liste
        if isinstance(bestellanfrage, dict)
        and bestellanfrage.get("status", BESTELLSTATUS_OFFEN) in offene_status
    ]


def mitarbeiterbestand_auslesen(standort):
    mitarbeiter = standort.get("Mitarbeiter", 0)
    if isinstance(mitarbeiter, int):
        return {"Anzahl": mitarbeiter}
    if isinstance(mitarbeiter, dict):
        anzahl = mitarbeiter.get("Anzahl", 0)
        if not isinstance(anzahl, int):
            anzahl = 0
        return {
            "Anzahl": anzahl,
            "Aktualisiert": mitarbeiter.get("Aktualisiert"),
            "Notiz": mitarbeiter.get("Notiz"),
        }
    return {"Anzahl": 0}


def mitarbeiterbestand_setzen(
    baustellen_liste, baustellen_name, anzahl, notiz=None
):
    if not isinstance(anzahl, int):
        return False, "Mitarbeiterzahl ist ungueltig"
    if anzahl < 0:
        return False, "Bitte gib eine Mitarbeiterzahl ab 0 ein"

    standort = baustellen_liste.get(baustellen_name)
    if not ist_standort(standort):
        return False, "Baustelle nicht gefunden"

    eintrag = {"Anzahl": anzahl, "Aktualisiert": zeitpunkt_utc()}
    notiz = str(notiz or "").strip()
    if notiz:
        eintrag["Notiz"] = notiz
    standort["Mitarbeiter"] = eintrag
    return True, "Mitarbeiterbestand gespeichert"


def mitarbeiteruebersicht_sammeln(baustellen_liste):
    uebersicht = []
    for standort_name in baustellen_namen(baustellen_liste):
        standort = baustellen_liste.get(standort_name, {})
        mitarbeiter = mitarbeiterbestand_auslesen(standort)
        uebersicht.append(
            {
                "Standort": standort_name,
                "Typ": standort.get("Typ", "Baustelle"),
                "Anzahl": mitarbeiter.get("Anzahl", 0),
                "Aktualisiert": mitarbeiter.get("Aktualisiert"),
                "Notiz": mitarbeiter.get("Notiz"),
            }
        )

    return sorted(uebersicht, key=lambda eintrag: eintrag["Standort"])


def baustelle_umbenennen(baustellen_liste, alter_name, neuer_name):
    if alter_name not in baustellen_liste:
        return False, "Baustelle nicht gefunden"
    if alter_name == FIRMENLAGER_NAME:
        return False, "Das Firmenlager kann nicht umbenannt werden"
    if neuer_name in baustellen_liste and neuer_name != alter_name:
        return False, "Dieser Baustellenname existiert bereits"

    baustellen_liste[neuer_name] = baustellen_liste.pop(alter_name)
    return True, "Baustelle umbenannt"


def material_umbenennen(baustellen_liste, baustellen_name, alter_name, neuer_name):
    materialien = materialien_fuer_baustelle(baustellen_liste, baustellen_name)
    if materialien is None:
        return False, "Baustelle nicht gefunden"
    if alter_name not in materialien:
        return False, "Material nicht gefunden"
    if neuer_name in materialien and neuer_name != alter_name:
        return False, "Dieser Materialname existiert bereits"

    materialien[neuer_name] = materialien.pop(alter_name)
    return True, "Material umbenannt"


def menge_aendern(baustellen_liste, baustellen_name, material_name, neue_menge):
    materialien = materialien_fuer_baustelle(baustellen_liste, baustellen_name)
    if materialien is None:
        return False, "Baustelle nicht gefunden"
    if material_name not in materialien:
        return False, "Material nicht gefunden"

    einheit = materialien[material_name].get("Einheit")
    return material_eintragen(
        baustellen_liste,
        baustellen_name,
        material_name,
        neue_menge,
        einheit,
        BUCHUNGSART_KORREKTUR,
    )


def einheit_aendern(baustellen_liste, baustellen_name, material_name, neue_einheit):
    materialien = materialien_fuer_baustelle(baustellen_liste, baustellen_name)
    if materialien is None:
        return False, "Baustelle nicht gefunden"
    if material_name not in materialien:
        return False, "Material nicht gefunden"
    if not neue_einheit:
        return False, "Bitte gib eine Einheit ein"

    materialien[material_name]["Einheit"] = neue_einheit
    return True, "Einheit geändert"


def naechste_bestellanfrage_id(bestellanfragen_liste):
    hoechste_id = 0
    for bestellanfrage in bestellanfragen_liste:
        if not isinstance(bestellanfrage, dict):
            continue
        bestell_id = bestellanfrage.get("id", 0)
        if isinstance(bestell_id, int) and bestell_id > hoechste_id:
            hoechste_id = bestell_id

    return hoechste_id + 1


def naechste_mitarbeiteranfrage_id(mitarbeiteranfragen_liste):
    hoechste_id = 0
    for mitarbeiteranfrage in mitarbeiteranfragen_liste:
        if not isinstance(mitarbeiteranfrage, dict):
            continue
        anfrage_id = mitarbeiteranfrage.get("id", 0)
        if isinstance(anfrage_id, int) and anfrage_id > hoechste_id:
            hoechste_id = anfrage_id

    return hoechste_id + 1


def statushistorie_eintrag_erstellen(von_status, zu_status, grund):
    grund = str(grund or "Nicht angegeben").strip() or "Nicht angegeben"
    return {
        "von": von_status,
        "zu": zu_status,
        "zeitpunkt": zeitpunkt_utc(),
        "grund": grund,
    }


def statushistorie_sicherstellen(bestellanfrage):
    historie = bestellanfrage.setdefault("statusHistorie", [])
    if not isinstance(historie, list):
        return None
    return historie


def bestellanfrage_erstellen(
    bestellanfragen_liste, ziel, material_name, menge, einheit
):
    if not ziel:
        return False, "Bitte gib ein Ziel an", None
    if not material_name:
        return False, "Bitte gib ein Material an", None
    if menge <= 0:
        return False, "Bitte gib eine Menge größer als 0 ein", None
    if not einheit:
        return False, "Bitte gib eine Einheit ein", None

    bestellanfrage = {
        "id": naechste_bestellanfrage_id(bestellanfragen_liste),
        "ziel": ziel,
        "material": material_name,
        "menge": menge,
        "einheit": einheit,
        "status": BESTELLSTATUS_OFFEN,
        "statusHistorie": [
            statushistorie_eintrag_erstellen(
                None, BESTELLSTATUS_OFFEN, "Bestellanfrage erstellt"
            )
        ],
    }
    bestellanfragen_liste.append(bestellanfrage)
    return True, "Bestellanfrage gespeichert", bestellanfrage


def mitarbeiteranfrage_erstellen(
    mitarbeiteranfragen_liste, ziel, anzahl, rolle, grund
):
    if not ziel:
        return False, "Bitte gib ein Ziel an", None
    if not isinstance(anzahl, int):
        return False, "Mitarbeiterzahl ist ungueltig", None
    if anzahl <= 0:
        return False, "Bitte gib eine Mitarbeiterzahl groesser als 0 ein", None

    rolle = str(rolle or "Allgemein").strip() or "Allgemein"
    grund = str(grund or "").strip()
    if not grund:
        return False, "Bitte gib einen Grund an", None

    mitarbeiteranfrage = {
        "id": naechste_mitarbeiteranfrage_id(mitarbeiteranfragen_liste),
        "ziel": ziel,
        "anzahl": anzahl,
        "rolle": rolle,
        "grund": grund,
        "status": MITARBEITERANFRAGE_STATUS_OFFEN,
        "erstelltAm": zeitpunkt_utc(),
        "statusHistorie": [
            statushistorie_eintrag_erstellen(
                None,
                MITARBEITERANFRAGE_STATUS_OFFEN,
                "Mitarbeiteranfrage erstellt",
            )
        ],
    }
    mitarbeiteranfragen_liste.append(mitarbeiteranfrage)
    return True, "Mitarbeiteranfrage gespeichert", mitarbeiteranfrage


def offene_mitarbeiteranfragen_sammeln(mitarbeiteranfragen_liste):
    return [
        mitarbeiteranfrage
        for mitarbeiteranfrage in mitarbeiteranfragen_liste
        if isinstance(mitarbeiteranfrage, dict)
        and mitarbeiteranfrage.get("status", MITARBEITERANFRAGE_STATUS_OFFEN)
        in MITARBEITERANFRAGE_OFFENE_STATUS
    ]


def chef_uebersicht_erstellen(
    baustellen_liste, bestellanfragen_liste, mitarbeiteranfragen_liste=None
):
    mitarbeiteranfragen_liste = mitarbeiteranfragen_liste or []
    return {
        "Baustellen": baustellen_namen(baustellen_liste),
        "Gesamtbestand": gesamtbestand_sammeln(baustellen_liste),
        "OffeneBestellanfragen": offene_bestellanfragen_sammeln(bestellanfragen_liste),
        "KritischeBestaende": kritische_bestaende_sammeln(baustellen_liste),
        "Mitarbeiter": mitarbeiteruebersicht_sammeln(baustellen_liste),
        "OffeneMitarbeiteranfragen": offene_mitarbeiteranfragen_sammeln(
            mitarbeiteranfragen_liste
        ),
    }


def bestellanfrage_finden(bestellanfragen_liste, bestell_id):
    for bestellanfrage in bestellanfragen_liste:
        if not isinstance(bestellanfrage, dict):
            continue
        if bestellanfrage.get("id") == bestell_id:
            return bestellanfrage
    return None


def bestellanfrage_status_aendern(
    bestellanfragen_liste, bestell_id, neuer_status, grund=None
):
    neuer_status = bestellstatus_normalisieren(neuer_status)
    if neuer_status is None:
        return False, "Bestellstatus ist ungueltig", None

    bestellanfrage = bestellanfrage_finden(bestellanfragen_liste, bestell_id)
    if bestellanfrage is None:
        return False, "Bestellanfrage nicht gefunden", None

    historie = statushistorie_sicherstellen(bestellanfrage)
    if historie is None:
        return False, "Statushistorie ist ungueltig", None

    alter_status = bestellanfrage.get("status")
    bestellanfrage["status"] = neuer_status
    historie.append(statushistorie_eintrag_erstellen(alter_status, neuer_status, grund))
    return True, "Bestellstatus geaendert", bestellanfrage


def bestellanfrage_wareneingang_buchen(
    bestellanfragen_liste, baustellen_liste, bestell_id, grund=None
):
    bestellanfrage = bestellanfrage_finden(bestellanfragen_liste, bestell_id)
    if bestellanfrage is None:
        return False, "Bestellanfrage nicht gefunden", None

    if bestellanfrage.get("status") == BESTELLSTATUS_STORNIERT:
        return False, "Stornierte Bestellanfragen koennen nicht geliefert werden", None

    wareneingang = bestellanfrage.get("wareneingang")
    if isinstance(wareneingang, dict) and wareneingang.get("gebucht"):
        return False, "Wareneingang wurde bereits gebucht", None

    historie = statushistorie_sicherstellen(bestellanfrage)
    if historie is None:
        return False, "Statushistorie ist ungueltig", None

    ziel = bestellanfrage.get("ziel")
    material_name = bestellanfrage.get("material")
    menge = bestellanfrage.get("menge")
    einheit = bestellanfrage.get("einheit")
    if (
        not ziel
        or not material_name
        or not isinstance(menge, int)
        or menge <= 0
        or not einheit
    ):
        return False, "Bestellanfrage ist unvollstaendig", None

    erfolgreich, meldung = material_eintragen(
        baustellen_liste,
        ziel,
        material_name,
        menge,
        einheit,
        BUCHUNGSART_ZUGANG,
        referenz=f"Bestellanfrage #{bestell_id}",
        notiz="Wareneingang",
    )
    if not erfolgreich:
        return False, f"Wareneingang nicht gebucht: {meldung}", None

    alter_status = bestellanfrage.get("status")
    bestellanfrage["status"] = BESTELLSTATUS_GELIEFERT
    historie.append(
        statushistorie_eintrag_erstellen(
            alter_status,
            BESTELLSTATUS_GELIEFERT,
            grund or "Wareneingang gebucht",
        )
    )
    bestellanfrage["wareneingang"] = {
        "gebucht": True,
        "zeitpunkt": zeitpunkt_utc(),
        "ziel": ziel,
        "material": material_name,
        "menge": menge,
        "einheit": einheit,
    }
    return True, "Wareneingang gebucht und Bestellstatus geaendert", bestellanfrage

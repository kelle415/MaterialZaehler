from datetime import datetime, timezone
from difflib import SequenceMatcher
import unicodedata


FIRMENLAGER_NAME = "Firmenlager"
BUCHUNGSART_ZUGANG = "zugang"
BUCHUNGSART_ABGANG = "abgang"
BUCHUNGSART_KORREKTUR = "korrektur"


def ist_standort(eintrag):
    return isinstance(eintrag, dict) and "Material" in eintrag


def baustellen_namen(baustellen_liste):
    return [
        name for name, eintrag in baustellen_liste.items() if ist_standort(eintrag)
    ]


def text_normalisieren(text):
    text = str(text).strip().casefold()
    text = unicodedata.normalize("NFKD", text)
    return "".join(zeichen for zeichen in text if not unicodedata.combining(zeichen))


def buchungsart_normalisieren(eingabe):
    buchungsart = text_normalisieren(eingabe)
    if buchungsart in ("1", "zugang", "addieren", "plus"):
        return BUCHUNGSART_ZUGANG
    if buchungsart in ("2", "abgang", "abziehen", "minus"):
        return BUCHUNGSART_ABGANG
    if buchungsart in ("3", "korrektur", "korrigieren", "setzen"):
        return BUCHUNGSART_KORREKTUR
    return None


def bewegung_erstellen(buchungsart, menge, einheit, bestand_vorher, bestand_nachher):
    zeitpunkt = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "Art": buchungsart,
        "Menge": menge,
        "Einheit": einheit,
        "BestandVorher": bestand_vorher,
        "BestandNachher": bestand_nachher,
        "Zeitpunkt": zeitpunkt,
    }


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
                    buchungsart, menge, einheit, bestand_vorher, bestand_nachher
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
            buchungsart, menge, vorhandene_einheit, bestand_vorher, bestand_nachher
        )
    )
    return True, "Materialbuchung gespeichert"


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
        "status": "offen",
    }
    bestellanfragen_liste.append(bestellanfrage)
    return True, "Bestellanfrage gespeichert", bestellanfrage

FIRMENLAGER_NAME = "Firmenlager"


def ist_standort(eintrag):
    return isinstance(eintrag, dict) and "Material" in eintrag


def baustellen_namen(baustellen_liste):
    return [
        name for name, eintrag in baustellen_liste.items() if ist_standort(eintrag)
    ]


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


def material_eintragen(baustellen_liste, baustellen_name, material_name, menge, einheit):
    baustelle = baustellen_liste.setdefault(
        baustellen_name, {"Typ": "Baustelle", "Material": {}}
    )
    if not isinstance(baustelle, dict):
        return False, "Standortdaten sind ungültig"

    materialien = baustelle.setdefault("Material", {})
    if not isinstance(materialien, dict):
        return False, "Materialdaten sind ungültig"

    materialien[material_name] = {"Menge": menge, "Einheit": einheit}
    return True, "Material gespeichert"


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

    materialien[material_name]["Menge"] = neue_menge
    return True, "Menge geändert"


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

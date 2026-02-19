"""
material eintragen mit menge in listen und menue aufrzfbar : eintragen, einsehen, entfernen, beenden

menue aufbau verbessern, 
"""

import json

def baustellenListedatenLaden():
    with open("baustellenListe.json","r", encoding="utf-8") as f:
        return json.load(f)

def temporaereListeBaustelleerstellen(baustellenListe):
    return list(baustellenListe.keys())

def temporaereListeMaterialerstellen(baustellenListe,baustellenInput):
    temporaereListeMaterial = []
    materialien = baustellenListe.get(baustellenInput,{}).get("Material",{})
    for materialname in materialien.keys():
        temporaereListeMaterial.append(materialname)
    
    return temporaereListeMaterial

def temporaereListeMenge_temporaereListeEinheit_erstellen(baustellenListe,baustellenInput):
    temporaereListeMenge = []
    temporaereListeEinheit =[]
    materialien = baustellenListe.get(baustellenInput,{}).get("Material",{})
    for info in materialien.values():
        temporaereListeMenge.append(info.get("Menge"))
        temporaereListeEinheit.append(info.get("Einheit"))

    return temporaereListeEinheit,temporaereListeMenge


def baustellendatenspeichern(baustellenListe):
    with open("baustellenListe.json", "w",encoding="utf-8") as f:
        json.dump(baustellenListe,f,indent=4, ensure_ascii=False)

def baustelleAbfragen():
    baustellenInput = input(f"Auf welcher baustelle bist du im moment: ")
    return baustellenInput

def materialUndMengeAbfrage():
    materialname = input("welches material möchtest du eintragen: ")
    materialmenge = int(input(f"wie viel {materialname} möchtest du eintragen: "))
    materialeinheit = input(f"welche einheit hat {materialname} mit menge {materialmenge}: ")
    return materialname,materialmenge, materialeinheit

def baustellendatenzusammenstellen(baustellenInput,materialname,materialmenge,materialeinheit):
    baustellenListe[baustellenInput]["Material"].setdefault(materialname, {"Menge":materialmenge,"Einheit":materialeinheit})
    baustellendatenspeichern(baustellenListe)

def menueverweis():
    baustellenInput= baustelleAbfragen()
    print("was möchtest du heute machen? \n 1. Material eintragen\n 2. Material Liste anzeigen\n 3. Material ändern\n 4. Beenden")
    menue = str(input("Antwort: "))
    if menue in ("eintragen","Material eintragen","1"):
        materialEintragen()
        zurueck()
    elif menue in ("Liste anzeigen","Material anzeigen","2"):
        materialAnzeigen(baustellenListe,baustellenInput)
        zurueck()
    elif menue in ("aus liste entfernen","Material ändern","3"):
        materialAendernabfragen(baustellenInput)
        zurueck()
    elif menue in ("Beenden","4"):
        beenden()
        
def materialEintragen(baustellenInput):
    materialname, materialmenge, materialeinheit= materialUndMengeAbfrage()
    baustellendatenzusammenstellen(baustellenInput,materialname,materialmenge, materialeinheit)

def materialAnzeigen(baustellenListe,baustellenInput):
    print("\n","-" * 25)
    print(f" Baustelle: {baustellenInput}")

    material = baustellenListe[baustellenInput].get("Material", {})
    if not material:
        print("Kein Material vorhanden")
        return

    for name, info in material.items():
        menge = info["Menge"]
        einheit = info["Einheit"]
        print(f"- {name}: {menge} {einheit}")
    print("-" * 25,"\n")

def materialAendernabfragen(baustellenInput):
    temporaereListeMaterial = temporaereListeMaterialerstellen(baustellenListe,baustellenInput)
    temporaereListeBaustelle = temporaereListeBaustelleerstellen(baustellenListe)
    temporaereListeEinheit,temporaereListeMenge = temporaereListeMenge_temporaereListeEinheit_erstellen(baustellenListe,baustellenInput)
    materialAnzeigen(baustellenListe,baustellenInput)
    print("was möchtest du ändern ?")
    print(f"\n 1. Baustellennamen{temporaereListeBaustelle},\n 2. Material{temporaereListeMaterial},\n 3. Menge{temporaereListeMenge},\n 4. Einheiten,\n 5. Nichts(Beenden)")
    abfrage = input("\n")
    if abfrage in ("1","Baustellennamen","baustellen"):
        baustelleAendernabfragen(abfrage)
    elif abfrage in temporaereListeMaterial:
        pass
    elif abfrage in temporaereListeMenge:
        pass
    elif abfrage in temporaereListeEinheit:
        pass
    else: 
        print("unverwertbare eingabe")

def baustelleAendernabfragen(abfrage):
    print(f"Möchtest du hierraus {abfrage} etwas ändern? (J/N)")
    aenderninput= input("\n")
    if aenderninput == "J":
        aendern()

def aendern():
    geaendert = input("Bitte gib den geänderten namen ein: ")
    sicherheitsfrage = input(f"ist {geaendert} richtig geschrieben? (J/N)")
    if sicherheitsfrage == "J":
        wert = ""
        baustellenListe[geaendert]
        baustellendatenspeichern(baustellenListe)


def zurueck():
    abfragezurueck = input("Möchtest du zurück ins hauptmenue? (J/N)")
    if abfragezurueck == "J":
        menueverweis()
    elif abfragezurueck == "N":
        abfragebeenden = input("Möchtest du beenden? (J/N)")
        if abfragebeenden == "J":
            beenden()
        elif abfragebeenden == "N":
            print("es gibt keine möglichkeit mehr")
            beenden()

def beenden():
    baustellendatenspeichern(baustellenListe)
    print("Daten gespeichert. Auf wieder sehen")

baustellenListe = baustellenListedatenLaden()

menueverweis()



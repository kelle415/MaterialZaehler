"""
material eintragen mit menge in listen und menue aufrzfbar : eintragen, einsehen, entfernen, beenden

menue aufbau verbessern, 
"""

import json

def baustellenListedatenLaden():
    with open("baustellenListe.json","r", encoding="utf-8") as f:
        return json.load(f)

def speichernInListe(baustellenListe):
    #hier soll eine funktion hin die alle keys in eine such begriffe liste rein packt damit man dann nur die liste in material ändern() einsetzten muss
    temporaereListeMaterial = []
    temporaereListeMenge = []
    temporaereListeEinheit =[]
    temporaereListeBaustelle= []
    
    for baustelle, baustellen_daten in baustellenListe.items():
        temporaereListeBaustelle.append(baustelle)

        materialien = baustellen_daten.get("Material", {})
        for materialname, info in materialien.items():
            temporaereListeMaterial.append(materialname)
            temporaereListeMenge.append(info.get("Menge"))
            temporaereListeEinheit.append(info.get("Einheit"))

    return (temporaereListeEinheit,temporaereListeBaustelle,temporaereListeMaterial,temporaereListeMenge)

def baustellendatenspeichern(baustellenListe):
    with open("baustellenListe.json", "w",encoding="utf-8") as f:
        json.dump(baustellenListe,f,indent=4, ensure_ascii=False)

def baustelleAbfragen():
    baustellenInput = input("Auf welcher baustelle bist du im moment: ")
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
    print("was möchtest du heute machen? \n 1. Material eintragen\n 2. Material Liste anzeigen\n 3. Material ändern\n 4. Beenden")
    menue = str(input("Antwort: "))
    if menue in ("eintragen","Material eintragen","1"):
        materialEintragen()
    elif menue in ("Liste anzeigen","Material anzeigen","2"):
        materialAnzeigen(baustellenListe)
    elif menue in ("aus liste entfernen","Material ändern","3"):
        materialAendernabfragen()
    elif menue in ("Beenden","4"):
        beenden()
        
def materialEintragen():
    baustellenInput = baustelleAbfragen()
    materialname, materialmenge, materialeinheit= materialUndMengeAbfrage()
    baustellendatenzusammenstellen(baustellenInput,materialname,materialmenge, materialeinheit)

def materialAnzeigen(baustellenListe):
    baustellenInput = baustelleAbfragen()
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

def materialAendernabfragen():
    temporaereListeEinheit,temporaereListeBaustelle,temporaereListeMaterial,temporaereListeMenge = speichernInListe()
    materialAnzeigen(baustellenListe)
    print("was möchtest du ändern ?")
    abfrage = input("\n")
    if abfrage in temporaereListeBaustelle:
        pass
    elif abfrage in temporaereListeMaterial:
        pass
    elif abfrage in temporaereListeMenge:
        pass
    elif abfrage in temporaereListeEinheit:
        pass
    else: 
        print("unverwertbare eingabe")

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



"""
material eintragen mit menge in json und menue aufrufbar: eintragen, einsehen, entfernen, beenden

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
    print("\nWas möchtest du heute machen? \n 1. Material eintragen\n 2. Material Liste anzeigen\n 3. Material ändern\n 4. Beenden")
    menue = str(input("\nAntwort: "))
    baustellenInput= baustelleAbfragen()
    if menue in ("eintragen","Material eintragen","1"):
        materialEintragen(baustellenInput)
        zurueck()
    elif menue in ("Liste anzeigen","Material anzeigen","2"):
        materialAnzeigen(baustellenListe,baustellenInput)
        zurueck()
    elif menue in ("aus liste entfernen","Material ändern","3"):
        allgemeinAendernabfragen(baustellenListe,baustellenInput)
        zurueck()
    if menue in ("Beenden","4"):
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
def bennung():
    "hier soll dann mitgegebne werden ob tembaustellen oder tempmaterial oder tempmenge angezeigt wird"

def allgemeinAendernabfragen(baustellenListe,baustellenInput):
    temporaereListeMaterial = temporaereListeMaterialerstellen(baustellenListe,baustellenInput)
    temporaereListeBaustelle = temporaereListeBaustelleerstellen(baustellenListe)
    temporaereListeEinheit,temporaereListeMenge = temporaereListeMenge_temporaereListeEinheit_erstellen(baustellenListe,baustellenInput)
    materialAnzeigen(baustellenListe,baustellenInput)
    print("was möchtest du ändern ?")
    print(f"\n 1. Baustellennamen{temporaereListeBaustelle},\n 2. Material{temporaereListeMaterial},\n 3. Menge{temporaereListeMenge},\n 4. Einheiten,\n 5. Nichts(Beenden)")
    abfrage = input("\nAntwort: ")
    if abfrage in ("1","Baustellennamen","baustellen"):
        baustelleAendernabfragen(baustellenListe,baustellenInput,abfrage, temporaereListeBaustelle)
    elif abfrage in ("2","Material"):
        materialAendernabfragen(baustellenListe,baustellenInput,abfrage, temporaereListeMaterial)
    elif abfrage in ("3","Menge","menge"):
        mengeAendernabfragen(baustellenListe,baustellenInput,abfrage,temporaereListeMaterial,temporaereListeMenge)
    elif abfrage in temporaereListeEinheit:
        pass
    else: 
        print("unverwertbare eingabe")

def baustelleAendernabfragen(baustellenListe,baustellenInput,abfrage,temporaereListeBaustelle):
    print(f"\nMöchtest du hierraus {abfrage}: {temporaereListeBaustelle} etwas ändern? (J/N)")
    aenderninput= input("Antwort: ")
    if aenderninput == "J":
        modus = modus1(False)
        zuaendern,geandert,sicherheitsfrage,materialname = aendernabfragen(modus)
        baustellennamenaendern(baustellenListe,baustellenInput,zuaendern,geandert,sicherheitsfrage,materialname)
    elif aenderninput == "N":
        zurueck()

def materialAendernabfragen(baustellenListe,baustellenInput,abfrage,temporaereListeMaterial):
    print(f"\nMöchtest du hierraus {abfrage}: {temporaereListeMaterial} etwas ändern? (J/N)")
    aenderninput= input("Antwort: ")
    if aenderninput == "J":
        modus = modus1(False)
        zuaendern,geandert,sicherheitsfrage,materialname = aendernabfragen(modus)
        materialnamenaendern(baustellenListe,baustellenInput,zuaendern,geandert,sicherheitsfrage,materialname)
    elif aenderninput == "N":
        zurueck()

def mengeAendernabfragen(baustellenListe,baustellenInput,abfrage,temporaereListeMaterial,temporaereListeMenge):
    print(f"\nMöchtest du hierraus {abfrage}: {temporaereListeMaterial}:{temporaereListeMenge} etwas ändern? (J/N)")
    aenderninput = input("Antwort: ")
    if aenderninput =="J":
        modus= modus1(True)
        zuaendern,geandert,sicherheitsfrage,materialname = aendernabfragen(modus)
        mengenaendern(baustellenListe,baustellenInput,zuaendern,geandert,sicherheitsfrage,materialname)
    elif aenderninput == "N":
        zurueck()

def modus1(daten):
    if daten:
        return "menge"
    else:
        None

def aendernabfragen(modus):
    materialname = None
    if modus == "menge":
        print("wie ist der zugehörige material name? ")
        materialname = input("Antwort: ")

    zuaendern = input("Bitte gib den zuändernden namen ein: ")
    print("\nWie soll der neue name heißen ? ")
    geandert = input("Antwort: ")
    print(f"\nBist du sicher das {zuaendern} zu {geandert} geändert werden soll? (J/N)")
    sicherheitsfrage = input("Antwort: ")
    return zuaendern,geandert,sicherheitsfrage,materialname

def baustellennamenaendern(baustellenListe,baustellenInput,zuaendern,geandert,sicherheitsfrage,materialname):
    if sicherheitsfrage == "J":
        if zuaendern in baustellenListe: 
            baustellenListe[geandert] = baustellenListe.pop(zuaendern)
            baustellendatenspeichern(baustellenListe)
            materialAnzeigen(baustellenListe,baustellenInput)
    elif sicherheitsfrage == "N":
        aendernabfragen(baustellenListe,baustellenInput)

def materialnamenaendern(baustellenListe,baustellenInput,zuaendern,geandert,sicherheitsfrage,materialname):
    if sicherheitsfrage == "J":
        if zuaendern in baustellenListe[baustellenInput]["Material"]:
            baustellenListe[baustellenInput]["Material"][geandert] = baustellenListe[baustellenInput]["Material"].pop(zuaendern) 
            baustellendatenspeichern(baustellenListe)
            materialAnzeigen(baustellenListe,baustellenInput)
    elif sicherheitsfrage == "N":
        aendernabfragen(baustellenListe,baustellenInput)
   
def mengenaendern(baustellenListe,baustellenInput,zuaendern,geandert,sicherheitsfrage,materialname):
    if sicherheitsfrage == "J":
        baustellenListe[baustellenInput]["Material"][materialname]["Menge"] = int(geandert)
        baustellendatenspeichern(baustellenListe)
        materialAnzeigen(baustellenListe,baustellenInput)
    elif sicherheitsfrage == "N":
        aendernabfragen(baustellenListe,baustellenInput)


def zurueck():
    abfragezurueck = input("Möchtest du zurück ins hauptmenue? (J/N): ")
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



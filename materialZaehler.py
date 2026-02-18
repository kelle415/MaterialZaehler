"""
material eintragen mit menge in listen und menue aufrzfbar : eintragen, einsehen, entfernen, beenden
"""

import json

def baustellenListedatenLaden():
    with open("baustellenListe.json","r", encoding="utf-8") as f:
        return json.load(f)

def baustellendatenspeichern(baustellenListe):
    with open("baustellenListe.json", "w",encoding="utf-8") as f:
        json.dump(baustellenListe,f,indent=4, ensure_ascii=False)

def baustelleAbfragen():
    baustellenInput = input("Auf welcher baustelle bist du im moment: ")
    return baustellenInput

def materialUndMengeAbfrage():
    materialname = input("welches material möchtest du eintragen: ")
    materialmenge = input(f"wie viel {materialname} möchtest du eintragen: ")
    return materialname,materialmenge

def baustellendatenzusammenstellen(baustellenInput,materialname,materialmenge):
    baustellenListe[baustellenInput]["Material"].setdefault(materialname, {"Menge":materialmenge})
    baustellendatenspeichern(baustellenListe)

def ablaufplan():
    baustellenInput = baustelleAbfragen()
    materialname, materialmenge = materialUndMengeAbfrage()
    baustellendatenzusammenstellen(
        baustellenInput,
        materialname,
        materialmenge
    )
    print(baustellenListe)

baustellenListe = baustellenListedatenLaden()

ablaufplan()



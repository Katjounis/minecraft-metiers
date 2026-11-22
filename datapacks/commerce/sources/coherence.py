# -*- coding: utf-8 -*-
# Contrôle du catalogue avec les données officielles de la 26.1 (donnees_26.1.json, tiré de minecraft-data) :
#   1. chaque id existe dans le jeu, sans doublon ;
#   2. aucune boucle « racheter les ingrédients, crafter ou cuire, revendre » n'est rentable.
# Le pire cas pour le vendeur est x3,64 (marché tendu x1,3, pénurie x1,6, bonus de métier x1,75) ;
# le rachat ne descend jamais sous x4. Un objet fabriqué ne doit donc pas dépasser 1,05 fois ses ingrédients.
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from catalogue import ITEMS, RARES, CUISSON

D = json.load(open(os.path.join(HERE, "donnees_26.1.json"), encoding="utf-8"))
NOMS = set(D["items"])
prix, achetable, err = {}, set(), []
for cat, lst in ITEMS.items():
    for iid, nom, p, vol, mj in lst:
        if iid not in NOMS: err.append(f"id inconnu en 26.1 : {iid}")
        if iid in prix: err.append(f"doublon : {iid}")
        prix[iid] = p
        if cat not in RARES: achetable.add(iid)
MARGE, FUEL = 1.05, 0.125


def verif(res, n, ings, quoi):
    if res not in prix or not ings or any(i not in achetable for i in ings):
        return
    cout = sum(prix[i] for i in ings) + (FUEL if quoi == "cuisson" else 0)
    if prix[res] * n > MARGE * cout + 1e-9:
        err.append(f"{quoi} rentable : {n} x {res} ({prix[res]}) > ingrédients {cout:.3f} [{', '.join(ings)}]")


vus = set()
for res, n, ings in D["recettes"]:
    k = (res, n, tuple(sorted(ings)))
    if k in vus: continue
    vus.add(k)
    verif(res, n, ings, "craft")
for res, ing in CUISSON:
    verif(res, 1, [ing], "cuisson")
print("\n".join(err) if err else f"Catalogue cohérent : {len(prix)} objets, {len(achetable)} achetables.")
sys.exit(1 if err else 0)

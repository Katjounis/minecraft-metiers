# -*- coding: utf-8 -*-
# Écrit la police et les images de l'arbre de compétences (préparées par ref_arbre.py) dans build/metiers_rp.
os.makedirs(os.path.join(_RPF, "textures", "font", "arbre"), exist_ok=True)
os.makedirs(os.path.join(_RPF, "font"), exist_ok=True)
for _nom, _im in ARB_FICHIERS:
    _im.save(os.path.join(_RPF, "textures", "font", "arbre", _nom + ".png"))
json.dump(ARB_FONT, open(os.path.join(_RPF, "font", "arbre.json"), "w", encoding="utf-8"), ensure_ascii=False)

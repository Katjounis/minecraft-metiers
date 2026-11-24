# -*- coding: utf-8 -*-
# 25.8 (24/11/2026) : décor de fond propre à chaque métier en tête de sa page, de ses récompenses et de son barème.
# Les images sont dessinées par Commerce (SCENES dans commerce/sources/datapack.py), glyphe chr(0xE100 + idx) de la police
# commerce:recette du resource pack commun. 36 px de haut, soit 4 lignes de texte.
SCENE = lambda d: ('{type:"minecraft:plain_message",width:310,contents:[{text:""},{text:"' + chr(0xE100 + d["idx"]) +
                   '",font:"commerce:recette",color:"white",shadow_color:0},{text:"\\n\\n\\n"}]}')
for j, d in jobs.items():
    for fic, avant in ((f"{j}/page_dialog.mcfunction", "body:["), (f"{j}/recompenses_dialog.mcfunction", "body:["),
                       (f"bareme/{j}.mcfunction", "body:[" + BAN_B + ",")):
        pth = os.path.join(ROOT, F, fic)
        t = open(pth, encoding="utf-8").read()
        assert t.count(avant) >= 1, fic
        t = t.replace(avant, "body:[" + SCENE(d) + ",", 1)
        open(pth, "w", encoding="utf-8").write(t)

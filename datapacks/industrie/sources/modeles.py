# -*- coding: utf-8 -*-
"""Export des bâtiments d'Industrie en modèles d'objet (resource pack), affichés par des item_display.

Chaque scène de voxels.py est mise à l'échelle dans la boîte autorisée par le jeu (-16 à 32), centrée en x et z,
posée sur son plan bas (y = -16). Avec item_display:"none", le modèle mesure donc 3 blocs de côté au plus pour une
échelle 1 ; datapack.py agrandit l'entité (ECHELLE) et la remonte de 1,5 x l'échelle pour la poser au sol.
"""
import os, json, math
import voxels as V

ORS = {"or": V.OR, "diamant": V.DIA, "emeraude": V.EME, "netherite": V.NET}
SCENES = {
    "carriere": lambda s: V.carriere(s),
    "serre": lambda s: V.serre(s),
    "fourneau": lambda s: V.haut_fourneau(s, 0, 0),
    "chaudiere": lambda s: V.chaudiere(s),
    "puits_or": lambda s: V.puits_cristal(s, 0, 0, V.OR),
    "fonderie": lambda s: V.fonderie(s),
    "distill": lambda s: V.distillerie(s, 0, 0),
    "lave": lambda s: V.centrale_lave(s),
    "puits_dia": lambda s: V.puits_cristal(s, 0, 0, V.DIA),
    "puits_eme": lambda s: V.puits_cristal(s, 0, 0, V.EME),
    "atelier": lambda s: V.atelier_meca(s),
    "puits_net": lambda s: V.puits_cristal(s, 0, 0, V.NET),
    "joaillerie": lambda s: V.joaillerie(s),
    "coeur": lambda s: V.coeur_stellaire(s),
    "forge": lambda s: V.forge_reliques(s),
    "nexus": lambda s: V.nexus(s, 22, 22),
    "echoppe": lambda s: V.comptoir_marche(s),
    "halle": lambda s: V.halle(s, 0, 0),
    "banque": lambda s: V.banque(s, 0, 0),
    "labo": lambda s: V.laboratoire(s),
    "oeuvre": lambda s: V.monument(s),
}


def _coins(e):
    f, t, r = e["from"], e["to"], e.get("rotation")
    pts = [(x, y, z) for x in (f[0], t[0]) for y in (f[1], t[1]) for z in (f[2], t[2])]
    if r:
        for ax in ("x", "y", "z"):
            if r.get(ax):
                a = math.radians(r[ax]); c, s_ = math.cos(a), math.sin(a); o = r["origin"]
                nv = []
                for p in pts:
                    x, y, z = p[0] - o[0], p[1] - o[1], p[2] - o[2]
                    if ax == "x": y, z = y * c - z * s_, y * s_ + z * c
                    elif ax == "y": x, z = x * c + z * s_, -x * s_ + z * c
                    else: x, y = x * c - y * s_, x * s_ + y * c
                    nv.append((x + o[0], y + o[1], z + o[2]))
                pts = nv
    return pts


def exporter(rp, ns="industrie"):
    """Écrit modèles, textures et définitions d'objet. Renvoie {nom: (largeur, hauteur) en unités de modèle}."""
    meta = {}
    sans_tube = V.tube
    for nom, fab in SCENES.items():
        V.tube = lambda *a, **k: None                    # les tubes sont des entités à part en jeu
        s = V.Scene(); fab(s)
        V.tube = sans_tube
        pts = [p for e in s.els for p in _coins(e)]
        x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
        y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
        z0, z1 = min(p[2] for p in pts), max(p[2] for p in pts)
        k = 47.0 / max(x1 - x0, y1 - y0, z1 - z0)
        cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
        T = lambda p: [round((p[0] - cx) * k + 8, 3), round((p[1] - y0) * k - 16, 3), round((p[2] - cz) * k + 8, 3)]
        els = []
        for i_, e in enumerate(s.els):
            # 27/11/2026 : faces confondues qui clignotaient (z-fighting) : chaque boîte est gonflée d'un poil différent
            g_ = 0.035 * (i_ % 5)
            e = dict(e, **{"from": [v - g_ for v in e["from"]], "to": [v + g_ for v in e["to"]]})
            el = {"from": T(e["from"]), "to": T(e["to"]), "faces": {f: {"uv": [round(v, 4) for v in d["uv"]], "texture": "#a"} for f, d in e["faces"].items()}}
            r = e.get("rotation")
            if r:
                rr = {ax: r[ax] for ax in ("x", "y", "z") if r.get(ax)}
                if rr:
                    rr["origin"] = T(r["origin"]); el["rotation"] = rr
            els.append(el)
        tex = f"{ns}:block/{nom}"
        mdl = {"textures": {"a": tex, "particle": tex}, "elements": els,
               "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, -2, 0], "scale": [0.32, 0.32, 0.32]},
                           "fixed": {"scale": [0.5, 0.5, 0.5]}}}
        for sous, obj in ((f"models/machine/{nom}.json", mdl),
                          (f"items/{nom}.json", {"model": {"type": "minecraft:model", "model": f"{ns}:machine/{nom}"}})):
            p = os.path.join(rp, "assets", ns, *sous.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            json.dump(obj, open(p, "w", encoding="utf-8"), separators=(",", ":"))
        p = os.path.join(rp, "assets", ns, "textures", "block", f"{nom}.png")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        s.atlas().save(p, optimize=True)
        meta[nom] = (round((max(x1 - x0, z1 - z0)) * k, 2), round((y1 - y0) * k, 2), len(els))
    return meta

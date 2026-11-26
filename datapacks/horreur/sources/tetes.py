"""Tetes en 3D des creatures « habit » du bestiaire (26/11/2026).

Avant : la tete etait la couche d'armure du patron (un cube peint). Maintenant c'est un modele d'objet pose dans
l'emplacement de tete du mob (sans « equippable », le jeu affiche alors le modele sur la tete et le fait tourner avec
elle) : museau du loup-garou, epingles de Pinhead, voile de la Nonne, nez et touffes du Clown, cornes du Croque-mitaine...
Le corps, les bras et les jambes gardent les habits peints de resourcepack.py.

Unites : celles du modele d'objet (16 = 0,625 bloc sur la tete, la tete du mob fait environ 13 x 13 x 13).
Construit avec le moteur de squelettes du pack Boss (rig.py, peintres.py).
"""
import math, os, sys

BOSS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "boss", "sources")
sys.path.insert(0, os.path.abspath(BOSS))
from rig import Rig  # noqa: E402

H = 6.5  # demi-cote de la tete


def _yeux(R, o, c, x=2.8, y=0.6, w=2.6, h=1.6, z=H + 0.15):
    for s in (-1, 1):
        R.boite(o, (s * x, y, z), (w, h, 0.3), "uni", {"c": c, "bruit": 6})


def herobrine():
    R = Rig("tete_herobrine"); o = R.racine
    R.boite(o, (0, 0, 0), (13, 13, 13), "uni", {"c": "#c8946a", "bruit": 14})
    R.boite(o, (0, 5.4, 0), (13.4, 2.6, 13.4), "uni", {"c": "#3e2716", "bruit": 12})
    R.boite(o, (0, 1.5, -6.6), (13.4, 10, 0.6), "uni", {"c": "#3e2716", "bruit": 12})
    for s in (-1, 1):
        R.boite(o, (s * 6.6, 3, -2), (0.6, 5, 9), "uni", {"c": "#3e2716", "bruit": 12})
    _yeux(R, o, "#ffffff", w=2.8, h=1.4)
    R.boite(o, (0, -3.2, H + 0.15), (4.2, 1.2, 0.3), "uni", {"c": "#5a3420", "bruit": 6})
    R.boite(o, (0, -4.8, H + 0.1), (6.5, 2.2, 0.25), "uni", {"c": "#4a2c18", "bruit": 8})
    return R


def nonne():
    R = Rig("tete_nonne"); o = R.racine
    R.boite(o, (0, -0.5, 0.3), (12, 12, 12), "uni", {"c": "#e2d6c2", "bruit": 12})
    # guimpe blanche autour du visage
    R.boite(o, (0, 5.6, 6.3), (12.6, 1.6, 0.8), "uni", {"c": "#f4f2ea", "bruit": 6})
    for s in (-1, 1):
        R.boite(o, (s * 6.2, -0.5, 6.1), (1.2, 12, 1.2), "uni", {"c": "#f4f2ea", "bruit": 6})
    R.boite(o, (0, -6.8, 4.5), (13, 1.6, 4), "uni", {"c": "#f4f2ea", "bruit": 6})
    # voile noir qui retombe dans le dos
    N = {"c": "#111014", "bruit": 10}
    R.boite(o, (0, 7.2, -0.5), (15, 1.6, 14.5), "uni", N)
    R.boite(o, (0, -3, -7.4), (15, 21, 1.4), "uni", N)
    for s in (-1, 1):
        R.boite(o, (s * 7.4, -2, -1.5), (1.4, 18, 11), "uni", N)
    # visage : orbites noires, pupilles jaunes, bouche beante
    for s in (-1, 1):
        R.boite(o, (s * 2.6, 0.8, H + 0.1), (3, 2.6, 0.3), "uni", {"c": "#050505", "bruit": 2})
        R.boite(o, (s * 2.6, 0.8, H + 0.3), (0.8, 0.8, 0.3), "uni", {"c": "#e8c020", "bruit": 2})
    R.boite(o, (0, -3.6, H + 0.1), (3.2, 3.4, 0.3), "uni", {"c": "#0a0505", "bruit": 2})
    R.boite(o, (0, -5.6, H + 0.15), (0.8, 2, 0.3), "uni", {"c": "#5a0a0a", "bruit": 2})
    return R


def clown():
    R = Rig("tete_clown"); o = R.racine
    R.boite(o, (0, 0, 0), (13, 13, 13), "uni", {"c": "#f2f0ea", "bruit": 8})
    R.boite(o, (0, -0.2, H + 1.6), (3.2, 3.2, 3.2), "uni", {"c": "#e01818", "bruit": 10})
    for s in (-1, 1):
        R.boite(o, (s * 2.9, 1.6, H + 0.1), (2.2, 2.6, 0.3), "uni", {"c": "#0a0a0a", "bruit": 2})
        R.boite(o, (s * 2.9, 1.6, H + 0.25), (0.6, 0.6, 0.3), "uni", {"c": "#ffd23a", "bruit": 2})
        R.boite(o, (s * 2.9, 4.4, H + 0.15), (0.7, 2.8, 0.3), "uni", {"c": "#c0202a", "bruit": 4})
        R.boite(o, (s * 2.9, -1.2, H + 0.15), (0.7, 2.4, 0.3), "uni", {"c": "#c0202a", "bruit": 4})
        # touffes rouges de chaque cote, crane chauve
        R.boite(o, (s * 7.6, 2.5, -1.5), (3.4, 5.5, 8), "uni", {"c": "#d8401a", "bruit": 30})
        R.boite(o, (s * 9.6, 4.5, -2), (2.2, 3.2, 5), "uni", {"c": "#e8602a", "bruit": 30})
    # sourire rouge jusqu'aux oreilles et dents pointues
    R.boite(o, (0, -3.8, H + 0.1), (9, 1.6, 0.3), "uni", {"c": "#b01020", "bruit": 6})
    for s in (-1, 1):
        R.boite(o, (s * 4.8, -2.8, H + 0.1), (1.2, 1.6, 0.3), "uni", {"c": "#b01020", "bruit": 6})
    for x in (-3, -1.5, 0, 1.5, 3):
        R.boite(o, (x, -3.6, H + 0.3), (0.7, 1.1, 0.3), "uni", {"c": "#f4f0dc", "bruit": 4})
    R.boite(o, (0, 6.6, 0), (9, 0.8, 9), "uni", {"c": "#e8e4dc", "bruit": 8})
    return R


def pinhead():
    R = Rig("tete_pinhead"); o = R.racine
    R.boite(o, (0, 0, 0), (13, 13, 13), "uni", {"c": "#d4cfc4", "bruit": 10})
    G = {"c": "#5a2222", "bruit": 6}
    # quadrillage de cicatrices (devant, dessus, cotes) et epingles a chaque croisement
    pas = [-4.2, -1.4, 1.4, 4.2]
    for v in pas:
        R.boite(o, (v, 0, H + 0.05), (0.35, 13, 0.2), "uni", G)
        R.boite(o, (0, v, H + 0.05), (13, 0.35, 0.2), "uni", G)
        R.boite(o, (v, H + 0.05, 0), (0.35, 0.2, 13), "uni", G)
        R.boite(o, (0, H + 0.05, v), (13, 0.2, 0.35), "uni", G)
        for s in (-1, 1):
            R.boite(o, (s * (H + 0.05), 0, v), (0.2, 13, 0.35), "uni", G)
            R.boite(o, (s * (H + 0.05), v, 0), (0.2, 0.35, 13), "uni", G)
    M = {"c": "#9aa0a8", "bruit": 12}
    T = {"c": "#d8dde4", "bruit": 6}
    for a in pas:
        for b in pas:
            if abs(b + 0.2) < 1 and abs(a) < 3:
                continue                                   # pas d'epingle dans les yeux
            R.boite(o, (a, b, H + 1.4), (0.45, 0.45, 2.8), "uni", M)
            R.boite(o, (a, b, H + 2.9), (0.9, 0.9, 0.5), "uni", T)
            R.boite(o, (a, H + 1.4, b), (0.45, 2.8, 0.45), "uni", M)
            R.boite(o, (a, H + 2.9, b), (0.9, 0.5, 0.9), "uni", T)
            for s in (-1, 1):
                R.boite(o, (s * (H + 1.4), a, b), (2.8, 0.45, 0.45), "uni", M)
                R.boite(o, (s * (H + 2.9), a, b), (0.5, 0.9, 0.9), "uni", T)
    for s in (-1, 1):
        R.boite(o, (s * 2.8, 0.2, H + 0.1), (2.2, 1.3, 0.3), "uni", {"c": "#050505", "bruit": 2})
    R.boite(o, (0, -3.6, H + 0.1), (3.4, 0.8, 0.3), "uni", {"c": "#3a1010", "bruit": 2})
    return R


def dame():
    R = Rig("tete_dame"); o = R.racine
    R.boite(o, (0, 0, 0.4), (12.4, 12.4, 12.4), "uni", {"c": "#eef0f8", "bruit": 6})
    C = {"c": "#f6f6fc", "bruit": 14}
    R.boite(o, (0, 6.7, -0.3), (14, 1.6, 13.6), "uni", C)
    R.boite(o, (0, -6, -7.2), (14, 26, 1.4), "uni", C)
    for s in (-1, 1):
        R.boite(o, (s * 7, -4, -0.5), (1.4, 22, 12), "uni", C)
        R.boite(o, (s * 5.2, -7, 6.2), (2.2, 14, 1), "uni", C)       # meches devant les epaules
    for s in (-1, 1):
        R.boite(o, (s * 2.6, 0.8, H + 0.5), (2.4, 2.4, 0.3), "uni", {"c": "#060608", "bruit": 2})
        R.boite(o, (s * 2.6, -1.8, H + 0.5), (0.6, 3, 0.3), "uni", {"c": "#20202a", "bruit": 2})   # larmes noires
    R.boite(o, (0, -3.8, H + 0.5), (2.2, 2.6, 0.3), "uni", {"c": "#14141c", "bruit": 2})
    return R


def loup():
    R = Rig("tete_loup"); o = R.racine
    F_ = {"c": "#6b5a48", "bruit": 26}
    R.boite(o, (0, 0.5, -0.5), (13, 12, 12), "uni", F_)
    R.boite(o, (0, -2.2, 10), (7, 5.6, 9), "uni", {"c": "#86735c", "bruit": 20})
    R.boite(o, (0, 0.4, 14.55), (3, 1.8, 0.4), "uni", {"c": "#151010", "bruit": 2})
    R.boite(o, (0, -5.6, 9.5), (6.4, 1.6, 8), "uni", {"c": "#5a2a22", "bruit": 6})       # gueule
    for x in (-2.2, 2.2):
        R.boite(o, (x, -4.6, 13.6), (0.8, 1.6, 0.6), "uni", {"c": "#f0ead8", "bruit": 4})  # crocs
    for s in (-1, 1):
        R.boite(o, (s * 4, 8.4, -1.5), (3.2, 4.4, 2), "uni", F_)
        R.boite(o, (s * 4, 8.2, -0.5), (1.6, 3, 0.2), "uni", {"c": "#c89a8a", "bruit": 6})
        R.boite(o, (s * 6.9, -1, -2), (1, 6, 6), "uni", {"c": "#584a3a", "bruit": 30})     # bajoues
        R.boite(o, (s * 3, 2, H - 0.3), (2.4, 1.4, 0.3), "uni", {"c": "#ffd030", "bruit": 6})
        R.boite(o, (s * 3, 2, H - 0.1), (0.6, 1.2, 0.3), "uni", {"c": "#100800", "bruit": 2})
    R.boite(o, (0, 3.6, H - 0.4), (8, 1, 0.5), "uni", {"c": "#4a3c2e", "bruit": 10})      # arcade
    return R


def rodeur():
    R = Rig("tete_rodeur"); o = R.racine
    P = {"c": "#b8b2a8", "bruit": 14}
    R.boite(o, (0, 1, 0), (12, 13, 12), "uni", P)
    R.boite(o, (0, -6.5, 1.5), (9, 5, 9), "uni", {"c": "#a8a298", "bruit": 14})          # machoire qui pend
    R.boite(o, (0, -5, 6.1), (6, 5.5, 0.4), "uni", {"c": "#0a0808", "bruit": 2})
    for x in (-2, -0.7, 0.7, 2):
        R.boite(o, (x, -2.9, 6.25), (0.6, 1.2, 0.3), "uni", {"c": "#e8e2d0", "bruit": 4})
    for s in (-1, 1):
        R.boite(o, (s * 2.7, 2, 6.1), (3.2, 4, 0.4), "uni", {"c": "#030303", "bruit": 2})
        R.boite(o, (s * 2.7, 1.4, 6.3), (0.6, 0.6, 0.3), "uni", {"c": "#c8c8b0", "bruit": 2})
    for (x, y) in ((-3, 6), (2, 5.5), (4, 3)):
        R.boite(o, (x, y, 6.05), (0.4, 2.4, 0.2), "uni", {"c": "#5a544c", "bruit": 2})
    return R


def croque():
    R = Rig("tete_croque"); o = R.racine
    R.boite(o, (0, 0.5, -0.5), (14, 14, 13.5), "uni", {"c": "#1a0f14", "bruit": 10})
    R.boite(o, (0, -0.5, 6.35), (10, 10, 0.4), "uni", {"c": "#020102", "bruit": 1})
    for s in (-1, 1):
        R.boite(o, (s * 2.4, 1, 6.6), (1.8, 1, 0.3), "uni", {"c": "#ff1a1a", "bruit": 10})
        for (x, y, w, h) in ((7.8, 5, 3, 3), (10.2, 7.8, 2.6, 2.6), (11.6, 10.6, 2, 3), (12.2, 13.6, 1.5, 2.5)):
            R.boite(o, (s * x, y, 0), (w, h, w), "uni", {"c": "#d8d0bc", "bruit": 14})
    R.boite(o, (0, -6.8, 3), (14, 3, 8), "uni", {"c": "#22141a", "bruit": 10})          # col du manteau
    return R


def slender():
    R = Rig("tete_slender"); o = R.racine
    R.boite(o, (0, 1.5, 0), (11, 16, 11), "uni", {"c": "#ecebe6", "bruit": 5})
    for s in (-1, 1):
        R.boite(o, (s * 2.4, 3, 5.55), (1.6, 2, 0.2), "uni", {"c": "#d6d4ce", "bruit": 3})
    R.boite(o, (0, -7.5, 0), (13, 2.5, 13), "uni", {"c": "#111114", "bruit": 6})
    R.boite(o, (0, -7.4, 6.6), (2.6, 2.4, 0.3), "uni", {"c": "#e8e8e6", "bruit": 3})
    R.boite(o, (0, -7.6, 6.8), (1, 2.2, 0.3), "uni", {"c": "#a01010", "bruit": 4})
    return R


TETES = {"slender": slender, "herobrine": herobrine, "nonne": nonne, "clown": clown, "pinhead": pinhead, "dame": dame,
         "loup": loup, "rodeur": rodeur, "croque": croque}


def generer(A):
    """Ecrit les modeles (A = dossier assets/horreur) et renvoie {id: id du modele}."""
    import json
    out = {}
    for k, f in TETES.items():
        R = f()
        fac = R.construire(A, "horreur")
        pid = R.ident_piece(R.racine, False)
        assert fac[pid] == 1, (k, fac[pid])
        p = os.path.join(A, "models", "item", "boss", pid + ".json")
        m = json.load(open(p, encoding="utf-8"))
        m["display"] = {"head": {"translation": [0, 0, 0], "scale": [1, 1, 1]},
                        "gui": {"rotation": [20, 200, 0], "scale": [0.75, 0.75, 0.75]},
                        "ground": {"scale": [0.5, 0.5, 0.5]}, "fixed": {"scale": [0.9, 0.9, 0.9]}}
        json.dump(m, open(p, "w", encoding="utf-8"), separators=(",", ":"))
        out[k] = pid
    return out

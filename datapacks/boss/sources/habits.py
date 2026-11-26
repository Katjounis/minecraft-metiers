"""Modeles animes des 5 boss du pack Metiers (26/11/2026, deuxieme version : vrais squelettes comme les boss du pack).

Le mob de Metiers garde son IA, sa vie et ses attaques ; il devient invisible (armure et objets tenus vides) et un
squelette d'item_display le suit (un seul boss de Metiers a la fois : les pieces sont teleportees sur lui a chaque tick).
Animations : repos, marche (selon qu'il se deplace), attaque (quand Metiers lance une attaque, signal metiers.atk).
  - Colosse des Metiers : forgeron geant en armure de plaques, coeur de forge rougeoyant, casque a cornes, marteau ;
  - Reine arachnide : huit pattes articulees, gros abdomen marque de violet, crocs, huit yeux rouges, couronne d'epines ;
  - Liche du givre : squelette en robe de givre dechiree, couronne de glace, baton a cristal, eclats qui tournent ;
  - Brasier ancestral : tete de magma, colonne d'obsidienne fendue de lave, deux anneaux de batons de feu qui tournent ;
  - Creeper geant : creeper de pierre moussue fendue de lueurs vertes, fagot de TNT, cristal sur la tete.
"""
import math
from rig import Rig, snbt_matrice, mul, trans, echelle
from squelettes import humanoide, marche, repos, U, L

# ------------------------------------------------------------------------------------------------ Colosse
def colosse():
    R = Rig("mb_colosse")
    PL = ("metal", {"pal": ["#3a3c42", "#46484f", "#2e3035", "#52555d"], "rivet": "#c89a3a"})
    B = humanoide(R, 6, 6, (9, 12, 5), 6, 6, (8, 8, 8), {"torse": PL, "tete": PL, "bras": PL, "avbras": PL, "jambe": PL},
                  ecart=2.3, larg_j=4.4, larg_b=4.4)
    T, H = B["torse"], B["tete"]
    R.boite(T, (0, 6.5, 2.7), (5.4, 5.4, 0.6), "lave", {"lueur": True})                            # coeur de forge
    for y in (1, 11.2):
        R.boite(T, (0, y, 2.6), (9.4, 0.8, 0.4), "uni", U("#c89a3a", 8))
    R.boite(T, (0, 6, 2.9), (6.4, 6.4, 0.3), "uni", U("#c89a3a", 8))
    R.boite(T, (0, 1, 2.9), (8, 5, 0.4), "tissu", {"c": "#4a2e1a"})                               # tablier de cuir
    for s in (-1, 1):
        R.boite(T, (s * 6.4, 11.5, 0), (5, 3, 6.4), *PL)                                          # epaulieres
        R.boite(T, (s * 6.4, 13.2, 0), (4, 0.8, 5.4), "uni", U("#c89a3a", 8))
        R.boite(H, (s * 5.6, 5, 0), (3.6, 2, 2), "uni", U("#d8cfb5", 10))                         # cornes
        R.boite(H, (s * 7.4, 7.6, 0), (2, 4, 2), "uni", U("#e8e0c8", 10))
        R.boite(H, (s * 7.6, 10.2, 0), (1.4, 2, 1.4), "uni", U("#f4eedc", 8))
    for y in (3, 5):
        R.boite(H, (0, y, 4.15), (6, 0.6, 0.3), "uni", U("#050505", 2))                          # visiere
    R.boite(H, (0, 4, 4.3), (4, 0.4, 0.3), "uni", L("#ff6a2a", 20))
    R.boite(H, (0, 8.6, 0), (2, 1.6, 8.6), "uni", U("#c89a3a", 8))
    M = R.art(B["avbras_d"], (0, -6, 0), (70, 0, 0), nom="marteau")     # tete vers l avant (+Z)
    R.boite(M, (0, 4, 0), (1.4, 18, 1.4), "bois_mort", {"pal": ["#5a3a22", "#4a2e1a", "#6b4529"]})
    R.boite(M, (0, 13, 0), (9, 5, 5), "metal")
    R.boite(M, (0, 13, 0), (1.2, 5.4, 5.4), "uni", U("#c89a3a", 8))
    A = {"repos": repos({"marteau": {"r": (6, 0, 0)}, "torse": {"r": (2, 0, 0)}}, {"marteau": {"r": (-4, 0, 0)}, "torse": {"r": (0, 0, 0)}}, 30),
         "marche": marche(26, 16, 1.0, 16, 4),
         "attaque": {"boucle": False, "cles": [(8, {"bras_d": {"r": (-170, 0, 10)}, "bras_g": {"r": (-150, 0, -10)}, "torse": {"r": (-14, 0, 0)}}),
                                              (4, {"bras_d": {"r": (-30, 0, 0)}, "bras_g": {"r": (-30, 0, 0)}, "torse": {"r": (28, 0, 0)},
                                                   "bassin": {"t": (0, -2, 0)}}), (12, {})]}}
    return R, A


# ------------------------------------------------------------------------------------------------ Reine arachnide
def reine():
    R = Rig("mb_reine")
    CHI = ("pierre", {"pal": ["#1a1420", "#24182c", "#141016", "#2e1e36"], "fissures": .2})
    corps = R.art(None, (0, 7, 0), nom="corps")
    R.boite(corps, (0, 0, 3), (8, 5, 8), *CHI)                                                    # cephalothorax
    ab = R.art(corps, (0, 1, -1), (-12, 0, 0), nom="abdomen")
    R.boite(ab, (0, 3, -7), (12, 10, 14), *CHI)
    for (x, z) in ((0, -3), (0, -7), (0, -11), (-3, -9), (3, -9)):
        R.boite(ab, (x, 8.1, z), (2, 0.4, 2), "uni", L("#9a4adf", 30))                           # marques violettes
    for k in range(4):
        R.boite(ab, (0, 8.15, -1 - k * 3.2), (0.8, 0.3, 1.4), "uni", U("#3a7a2a", 10))
    T = R.art(corps, (0, 1, 7), nom="tete")
    R.boite(T, (0, 0, 1.5), (6, 4.6, 4), *CHI)
    for (x, y) in ((-2, 1.2), (-0.7, 1.6), (0.7, 1.6), (2, 1.2), (-1.4, 0.2), (1.4, 0.2), (-2.4, -0.4), (2.4, -0.4)):
        R.boite(T, (x, y, 3.55), (0.8, 0.8, 0.3), "uni", L("#ff2020", 20))
    for s in (-1, 1):
        cr = R.art(T, (s * 1.2, -1.8, 3), nom="croc_" + ("g" if s < 0 else "d"))
        R.boite(cr, (0, -1.4, 0.6), (1, 3, 1), "uni", U("#d8d0b8", 6))
    for k in range(6):                                                                            # couronne d'epines
        a = k / 6 * math.tau
        R.boite(T, (math.cos(a) * 2.4, 3.4 + (k % 2), 1.5 + math.sin(a) * 1.6), (0.8, 2.4 + (k % 2), 0.8), "uni", U("#7a3ab0", 12))
    # huit pattes : femur leve vers l'exterieur, tibia replie vers le sol
    for i, (z, ang) in enumerate(((5, 40), (2.5, 14), (0, -14), (-2.5, -40))):
        for s, c in ((-1, "g"), (1, "d")):
            nom = f"patte{i}_{c}"
            P = R.art(corps, (s * 3.6, 0.5, z), (0, -s * ang, 0), nom=nom)
            F = R.art(P, (0, 0, 0), (0, 0, s * 38), nom=nom + "_f")
            R.boite(F, (s * 5, 0, 0), (10, 1.7, 1.7), *CHI)
            Ti = R.art(F, (s * 10, 0, 0), (0, 0, -s * 105), nom=nom + "_b")
            R.boite(Ti, (s * 6.5, 0, 0), (13, 1.3, 1.3), *CHI)
            R.boite(Ti, (s * 2, 0, 0), (1.4, 1.6, 1.6), "uni", U("#3a7a2a", 10))
    def pas(sg):
        d = {}
        for i in range(4):
            for c in ("g", "d"):
                v = sg * (1 if (i + (c == "d")) % 2 else -1)
                d[f"patte{i}_{c}"] = {"r": (0, v * 16, 0)}
                d[f"patte{i}_{c}_f"] = {"r": (0, 0, (8 if c == "d" else -8) * max(v, 0))}
        d["corps"] = {"t": (0, 0.6 * sg, 0)}
        d["abdomen"] = {"r": (-3 * sg, 0, 0)}
        return d
    A = {"repos": repos({"abdomen": {"r": (4, 0, 0)}, "croc_g": {"r": (10, 0, 0)}, "croc_d": {"r": (10, 0, 0)}, "corps": {"t": (0, 0.4, 0)}},
                        {"abdomen": {"r": (-2, 0, 0)}, "croc_g": {"r": (-6, 0, 0)}, "croc_d": {"r": (-6, 0, 0)}}, 24),
         "marche": {"boucle": True, "cles": [(6, pas(1)), (6, pas(-1))]},
         "attaque": {"boucle": False, "cles": [(6, {"corps": {"r": (-25, 0, 0), "t": (0, 3, 0)}, "patte0_g_f": {"r": (0, 0, -40)}, "patte0_d_f": {"r": (0, 0, 40)},
                                                    "croc_g": {"r": (-30, 0, 0)}, "croc_d": {"r": (-30, 0, 0)}}),
                                              (4, {"corps": {"r": (15, 0, 0)}, "croc_g": {"r": (30, 0, 0)}, "croc_d": {"r": (30, 0, 0)}}), (10, {})]}}
    return R, A


# ------------------------------------------------------------------------------------------------ Liche du givre
def liche():
    R = Rig("mb_liche")
    OS_ = ("peau", {"c": "#d8d2bd", "bruit": 12, "veines": 1, "cv": "#8a846e"})
    ROBE = ("tissu", {"c": "#1e2c46", "bruit": 12, "ourlet": "#7ad8ff"})
    GIVRE = ("cristal", {})
    bas = R.art(None, (0, 15, 0), nom="bassin")
    # longue robe qui touche le sol, en lambeaux bordes de givre
    jupe = R.art(bas, (0, 0, 0), nom="jupe")
    for k, (w, y) in enumerate(((8, -1.5), (9.4, -5), (10.8, -8.5), (12.2, -12))):
        R.boite(jupe, (0, y, 0), (w, 3.6, w * 0.62), *ROBE)
    for (x, z) in ((-5.6, 2), (4.8, 3), (0, 3.9), (-3, -3.6), (3.6, -3.2)):
        R.boite(jupe, (x, -14.5, z), (1.6, 1.4, 1.6), *GIVRE)                                   # givre au sol
    T = R.art(bas, (0, 0, 0), (6, 0, 0), nom="torse")
    R.boite(T, (0, 6, 0), (8, 12, 4.4), *ROBE)
    R.boite(T, (0, 6, 2.25), (2.4, 11, 0.3), "tissu", {"c": "#7ad8ff", "bruit": 6})              # pan central brode
    for y in (3, 6, 9):
        R.boite(T, (0, y, 2.45), (1.4, 1.4, 0.3), "cristal", {})
    R.boite(T, (0, 12, 0), (12, 2, 6.4), "uni", U("#e8eef4", 12))                                # col de fourrure
    for s in (-1, 1):
        R.boite(T, (s * 5.6, 12.6, 0), (3.4, 3, 5.4), "uni", U("#dfe6ee", 12))                  # epaulieres de fourrure
        R.boite(T, (s * 6.4, 14.6, 0), (1.2, 3, 1.2), *GIVRE)
    # capuche et crane
    H = R.art(T, (0, 12.5, 0.4), nom="tete")
    R.boite(H, (0, 4, -0.4), (8.4, 9, 8.4), *ROBE)                                               # capuche
    R.boite(H, (0, 3.6, 2.4), (6.2, 6.6, 3.2), *OS_)                                             # crane
    for s in (-1, 1):
        R.boite(H, (s * 1.5, 4.4, 4.05), (1.8, 1.8, 0.2), "uni", U("#020204", 1))
        R.boite(H, (s * 1.5, 4.4, 4.2), (0.8, 0.8, 0.2), "uni", L("#5ad0ff", 10))
    R.boite(H, (0, 2.6, 4.05), (0.8, 0.8, 0.2), "uni", U("#1a1410", 2))
    for x in (-1.6, -0.5, 0.5, 1.6):
        R.boite(H, (x, 1.2, 4.05), (0.6, 1, 0.2), "uni", U("#efe9d6", 4))
    for (x, z, h) in ((0, 1.6, 6), (-2.2, 1.6, 4), (2.2, 1.6, 4), (-3.8, -0.6, 3.4), (3.8, -0.6, 3.4)):
        R.boite(H, (x, 8.6 + h / 2, z), (1, h, 1), *GIVRE)                                       # couronne de glace
    # bras osseux sortant de manches larges
    for s, c in ((-1, "g"), (1, "d")):
        b = R.art(T, (s * 5.6, 11, 0), nom="bras_" + c)
        R.boite(b, (0, -4.5, 0), (3.4, 9, 3.4), *ROBE)
        R.boite(b, (0, -9, 0), (4, 1.4, 4), "tissu", {"c": "#7ad8ff", "bruit": 6})
        a = R.art(b, (0, -9, 0), nom="avbras_" + c)
        R.boite(a, (0, -3.5, 0), (1.2, 7, 1.2), *OS_)
        for f in range(3):
            R.boite(a, ((f - 1) * 0.6, -8, 0.3), (0.35, 3, 0.35), *OS_)
    B2 = R.art(R.os[[o.nom for o in R.os].index("avbras_d")], (0, -7, 0), (80, 0, 0), nom="baton")
    R.boite(B2, (0, 4, 0), (1.2, 30, 1.2), "bois_mort", {"pal": ["#2a3442", "#1e2632", "#36404e"]})
    R.boite(B2, (0, 19, 0), (2.8, 1.4, 2.8), "uni", U("#a8c8e0", 8))
    for (x, y, z, w, h) in ((0, 22.5, 0, 2.8, 6), (1.6, 21, 0.4, 1.2, 3.4), (-1.4, 21.4, -0.6, 1.2, 3), (0, 20.5, 1.6, 1, 2.6)):
        R.boite(B2, (x, y, z), (w, h, w), "cristal", {"lueur": True})
    orb = R.art(None, (0, 30, 0), nom="eclats")
    for k in range(6):
        a = k / 6 * math.tau
        R.boite(orb, (math.cos(a) * 9, math.sin(a * 2) * 1.5, math.sin(a) * 9), (0.9, 2.4, 0.9), "cristal", {})
    A = {"repos": {"boucle": True, "cles": [(20, {"eclats": {"r": (0, 120, 0)}, "jupe": {"r": (3, 0, 2)}, "bassin": {"t": (0, 1, 0)}, "tete": {"r": (6, 0, 4)}}),
                                            (20, {"eclats": {"r": (0, 240, 0)}, "jupe": {"r": (-2, 0, -2)}, "tete": {"r": (0, 0, -3)}}),
                                            (20, {"eclats": {"r": (0, 359, 0)}, "jupe": {"r": (2, 0, 0)}, "bassin": {"t": (0, 1, 0)}})]},
         "marche": {"boucle": True, "cles": [(10, {"bassin": {"t": (0, 1.2, 0)}, "jupe": {"r": (-8, 0, 3)}, "bras_g": {"r": (-20, 0, -6)},
                                                   "eclats": {"r": (0, 180, 0)}}),
                                             (10, {"bassin": {"t": (0, 0.2, 0)}, "jupe": {"r": (-5, 0, -3)}, "bras_g": {"r": (-10, 0, -6)},
                                                   "eclats": {"r": (0, 359, 0)}})]},
         "attaque": {"boucle": False, "cles": [(8, {"bras_d": {"r": (-170, 0, 0)}, "bras_g": {"r": (-120, 0, -40)}, "tete": {"r": (-20, 0, 0)},
                                                    "eclats": {"s": 1.6}}),
                                              (5, {"bras_d": {"r": (-80, 0, 0)}, "bras_g": {"r": (-60, 0, -20)}, "eclats": {"s": 0.6}}), (12, {})]}}
    return R, A


# ------------------------------------------------------------------------------------------------ Brasier ancestral
def brasier():
    R = Rig("mb_brasier")
    OBS = ("pierre", {"pal": ["#140a1e", "#1d1030", "#0d0614", "#26143c"], "fissures": .8})
    c = R.art(None, (0, 18, 0), nom="corps")
    for (w, y) in ((4, -11), (5, -7), (6.4, -2.6)):
        R.boite(c, (0, y, 0), (w, 4.4, w), *OBS)
        R.boite(c, (0, y - 1, 0), (w + 0.2, 0.6, w + 0.2), "lave", {"lueur": True})
    R.boite(c, (0, -14, 0), (2, 3, 2), "lave", {"lueur": True})
    T = R.art(c, (0, 2, 0), nom="tete")
    R.boite(T, (0, 4, 0), (7.4, 7.4, 7.4), "lave", {"lueur": True})                             # magma
    R.boite(T, (0, 4.4, 3.85), (7.8, 5, 0.5), *OBS)                                               # masque d'obsidienne
    for s in (-1, 1):
        R.boite(T, (s * 1.7, 5, 4.15), (1.8, 0.9, 0.3), "uni", L("#fff3a0", 10))
        R.boite(T, (s * 4, 4, 0), (0.6, 7, 7.6), *OBS)
    R.boite(T, (0, 2.6, 4.15), (3, 0.6, 0.3), "uni", L("#ff8a10", 10))
    for k in range(7):
        a = k / 7 * math.tau
        h = 4 if k % 2 else 6
        R.boite(T, (math.cos(a) * 3.2, 8 + h / 2, math.sin(a) * 3.2), (1.4, h, 1.4), *OBS)
        R.boite(T, (math.cos(a) * 3.2, 8 + h + 0.8, math.sin(a) * 3.2), (0.9, 1.6, 0.9), "lave", {"lueur": True})
    for nom, y, r_, n in (("anneau_h", 1, 10, 6), ("anneau_b", -8, 8, 5)):
        an = R.art(c, (0, y, 0), nom=nom)
        for k in range(n):
            a = k / n * math.tau
            R.boite(an, (math.cos(a) * r_, 0, math.sin(a) * r_), (1.3, 8, 1.3), "lave", {"lueur": True})
            R.boite(an, (math.cos(a) * r_, 4.6, math.sin(a) * r_), (2.2, 1.4, 2.2), *OBS)
            R.boite(an, (math.cos(a) * r_, -4.6, math.sin(a) * r_), (2.2, 1.4, 2.2), *OBS)
    A = {"repos": {"boucle": True, "cles": [(14, {"anneau_h": {"r": (0, 120, 0)}, "anneau_b": {"r": (0, -120, 0)}, "corps": {"t": (0, 1.5, 0)}}),
                                            (14, {"anneau_h": {"r": (0, 240, 0)}, "anneau_b": {"r": (0, -240, 0)}, "corps": {"t": (0, 0, 0)}}),
                                            (14, {"anneau_h": {"r": (0, 359, 0)}, "anneau_b": {"r": (0, -359, 0)}, "corps": {"t": (0, 1.5, 0)}})]},
         "attaque": {"boucle": False, "cles": [(6, {"anneau_h": {"s": 1.5, "r": (0, 90, 0)}, "anneau_b": {"s": 1.5, "r": (0, -90, 0)}, "tete": {"r": (-20, 0, 0)}}),
                                              (6, {"anneau_h": {"s": 0.7, "r": (0, 180, 0)}, "anneau_b": {"s": 0.7, "r": (0, -180, 0)}}), (10, {})]}}
    A["marche"] = A["repos"]
    return R, A


# ------------------------------------------------------------------------------------------------ Creeper geant
def creeper():
    R = Rig("mb_creeper")
    MOUSSE = ("pierre", {"pal": ["#3a5a30", "#2f4a2a", "#4a6a38", "#24381f", "#5a7a40"], "fissures": .6})
    corps = R.art(None, (0, 6, 0), nom="corps")
    R.boite(corps, (0, 6, 0), (8, 12, 4.6), *MOUSSE)
    for (x, y) in ((-2, 3), (2, 8), (-1, 10), (3, 2)):
        R.boite(corps, (x, y, 2.35), (0.6, 2.4, 0.3), "uni", L("#7aff5a", 20))                   # fissures lumineuses
    T = R.art(corps, (0, 12, 0), nom="tete")
    R.boite(T, (0, 4, 0), (8, 8, 8), *MOUSSE)
    for s in (-1, 1):
        R.boite(T, (s * 1.8, 5, 4.05), (2, 2, 0.3), "uni", U("#050505", 2))
    R.boite(T, (0, 2.4, 4.05), (2, 3, 0.3), "uni", U("#050505", 2))
    for s in (-1, 1):
        R.boite(T, (s * 1.6, 1.2, 4.05), (1.2, 2, 0.3), "uni", U("#050505", 2))
    for (x, y) in ((-3, 6.5), (3.2, 2.5), (-2.6, 1)):
        R.boite(T, (x, y, 4.05), (0.5, 2, 0.3), "uni", L("#7aff5a", 20))
    R.boite(T, (0, 9.5, 0), (3, 5, 3), "cristal", {"pal": ["#5aff5a", "#9aff7a", "#3ad03a"], "lueur": True})
    R.boite(T, (0, 8.2, 0), (5, 0.8, 5), "pierre", {"pal": ["#2f4a2a", "#24381f"]})
    tnt = R.art(corps, (0, 7, -3), nom="tnt")
    for x in (-2.4, 0, 2.4):
        R.boite(tnt, (x, 0, -0.8), (2.2, 7, 2.2), "tnt")
        R.boite(tnt, (x, 4, -0.8), (0.4, 1.2, 0.4), "uni", U("#3a3a3a", 4))
    R.boite(tnt, (0, 1.5, -0.8), (7.4, 0.8, 2.6), "uni", U("#3a2a1a", 6))
    for i, (x, z) in enumerate(((-2, 2), (2, 2), (-2, -2), (2, -2))):
        P = R.art(None, (x, 6, z), nom=f"pied{i}")
        R.boite(P, (0, -3, 0), (4, 6, 4), *MOUSSE)
    def pas(s):
        return {"pied0": {"r": (30 * s, 0, 0)}, "pied3": {"r": (30 * s, 0, 0)}, "pied1": {"r": (-30 * s, 0, 0)}, "pied2": {"r": (-30 * s, 0, 0)},
                "corps": {"r": (0, 0, 3 * s)}, "tnt": {"r": (6 * s, 0, 0)}}
    A = {"repos": repos({"tete": {"r": (6, 0, 0)}, "corps": {"t": (0, 0.3, 0)}}, {"tete": {"r": (0, 0, 0)}}, 30),
         "marche": {"boucle": True, "cles": [(7, pas(1)), (7, pas(-1))]},
         "attaque": {"boucle": False, "cles": [(10, {"corps": {"s": 1.12}, "tete": {"s": 1.1}}), (4, {"corps": {"s": 0.94}}),
                                              (6, {"corps": {"s": 1.1}}), (10, {})]}}
    return R, A


BOSS_RIGS = {"zombie": colosse, "spider": reine, "stray": liche, "blaze": brasier, "creeper": creeper}
# taille d'affichage = echelle du mob de Metiers (Colosse 2,5, Reine 3, Liche 2,2, Brasier 2,5, Creeper 3)
TAILLE = {"zombie": 2.5, "spider": 3.0, "stray": 2.2, "blaze": 2.5, "creeper": 3.0}
VIDE = '{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"boss:vide"}}'


def ecrire_rp(RP, ns, ecrire_json):
    for f in BOSS_RIGS.values():
        R, _ = f()
        R.construire(RP, ns)


def ecrire_dp(fn, NS):
    import rigdp
    habiller = ["tag @s add bs.hab", "effect give @s minecraft:invisibility infinite 0 true",
                "data merge entity @s {drop_chances:{head:0f,chest:0f,legs:0f,feet:0f,mainhand:0f,offhand:0f}}",
                "item replace entity @s armor.head with minecraft:air", "item replace entity @s armor.chest with minecraft:air",
                "item replace entity @s armor.legs with minecraft:air", "item replace entity @s armor.feet with minecraft:air",
                "execute if entity @s[type=minecraft:zombie] run item replace entity @s weapon.mainhand with minecraft:air",
                'execute if entity @s[type=minecraft:stray] run item replace entity @s weapon.mainhand with minecraft:bow[minecraft:item_model="boss:vide"]',
                "kill @e[type=minecraft:item_display,tag=bs.mos]"]
    tick = ["execute as @e[tag=metiers.boss,tag=bs.hab,limit=1] unless entity @e[type=minecraft:item_display,tag=bs.mos] run tag @s remove bs.hab",
            f"execute as @e[tag=metiers.boss,tag=!bs.hab,limit=1] at @s run function {NS}:metiers/habiller",
            "execute unless entity @e[tag=metiers.boss] run kill @e[type=minecraft:item_display,tag=bs.mos]",
            f"execute as @e[tag=metiers.boss,tag=bs.hab,limit=1] at @s run function {NS}:metiers/suivre"]
    suivre = ["tp @e[type=minecraft:item_display,tag=bs.mos] ~ ~ ~ ~ 0"]
    for t, f in BOSS_RIGS.items():
        R, A = f()
        _calc_facteurs(R)
        nom = R.nom
        ids = rigdp.generer(R, A, f"{NS}:metiers/{nom}_defaut", luminosite=13, view=4.0, racine=(TAILLE[t], "bs.mos"))
        fn(f"metiers/{nom}_defaut", f"function {NS}:rig/{nom}/jouer/repos")
        habiller.append(f"execute if entity @s[type=minecraft:{t}] run function {NS}:rig/{nom}/invoquer")
        habiller.append(f"execute if entity @s[type=minecraft:{t}] run function {NS}:rig/{nom}/jouer/repos")
        suivre += [f"execute if entity @s[type=minecraft:{t}] run function {NS}:metiers/{nom}_etat"]
        fn(f"metiers/{nom}_etat", [
            f"function {NS}:rig/{nom}/tick",
            f"execute if entity @s[tag=metiers.atk] run function {NS}:rig/{nom}/jouer/attaque",
            "tag @s remove metiers.atk",
            f"execute if score #a{nom} bs.an matches {ids['attaque']} run return 0",
            f"execute if predicate {NS}:bouge unless score #a{nom} bs.an matches {ids['marche']} run function {NS}:rig/{nom}/jouer/marche",
            f"execute unless predicate {NS}:bouge unless score #a{nom} bs.an matches {ids['repos']} run function {NS}:rig/{nom}/jouer/repos"])
    fn("metiers/habiller", habiller)
    fn("metiers/tick", tick)
    fn("metiers/suivre", suivre)
    fn("metiers/seconde", ["return 0"])


def _calc_facteurs(R):
    fac = {}
    for o, lueur in R.pieces():
        bx = [b for b in o.boites if bool(b[3].get("lueur")) == lueur]
        ext = max(max(abs(c[i]) + s[i] / 2 for i in range(3)) for c, s, _, _ in bx)
        k = 1.0
        while ext / k > 23.5:
            k *= 2
        fac[R.ident_piece(o, lueur)] = k
    R.facteurs = fac

"""Squelettes animes des creatures du bestiaire (26/11/2026), meme moteur que les boss (pack Boss : rig.py).

Chaque creature garde son mob invisible (IA, vie, coups) ; son apparence devient un squelette d'item_display
passagers du mob, animes par poses interpolees (repos, marche, attaque). Unites : pixels, 16 px = 1 bloc, a la
taille 1 ; le squelette est ensuite agrandi par l'echelle de la creature. Devant = +Z, pieds en y = 0.
"""
import math, os, sys

BOSS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "boss", "sources")
sys.path.insert(0, os.path.abspath(BOSS))
from rig import Rig  # noqa: E402

U = lambda c, b=10: {"c": c, "bruit": b}
L = lambda c, b=20: {"c": c, "bruit": b, "lueur": True}


def humanoide(R, cuisse, tibia, torse, bras, avbras, tete, P, ecart=2.2, larg_j=3.4, larg_b=3.2, pr=0):
    """Squelette humain de base. torse = (l, h, p), tete = (l, h, p). P : peintres par partie (nom, options)."""
    tl, th, tp = torse
    hj = cuisse + tibia
    B = {}
    B["bassin"] = R.art(None, (0, hj, 0), nom="bassin")
    B["torse"] = R.art(B["bassin"], (0, 0, 0), (pr, 0, 0), nom="torse")
    R.boite(B["torse"], (0, th / 2, 0), (tl, th, tp), *P["torse"])
    B["tete"] = R.art(B["torse"], (0, th, 0), nom="tete")
    R.boite(B["tete"], (0, tete[1] / 2, 0), tete, *P["tete"])
    for s, c in ((-1, "g"), (1, "d")):
        b = R.art(B["torse"], (s * (tl / 2 + larg_b / 2), th - 1.5, 0), nom="bras_" + c)
        R.boite(b, (0, -bras / 2, 0), (larg_b, bras, larg_b), *P["bras"])
        a = R.art(b, (0, -bras, 0), nom="avbras_" + c)
        R.boite(a, (0, -avbras / 2, 0), (larg_b - 0.4, avbras, larg_b - 0.4), *P.get("avbras", P["bras"]))
        B["bras_" + c], B["avbras_" + c] = b, a
        j = R.art(B["bassin"], (s * ecart, 0, 0), nom="cuisse_" + c)
        R.boite(j, (0, -cuisse / 2, 0), (larg_j, cuisse, larg_j), *P["jambe"])
        t = R.art(j, (0, -cuisse, 0), nom="tibia_" + c)
        R.boite(t, (0, -tibia / 2, 0), (larg_j - 0.4, tibia, larg_j - 0.4), *P.get("tibia", P["jambe"]))
        B["cuisse_" + c], B["tibia_" + c] = j, t
    return B


def marche(amp=24, bras=20, bob=1.0, plie=18, torse=4, extra=None):
    cles = []
    for i, s in enumerate((1, -1)):
        p = {"cuisse_g": {"r": (-amp * s, 0, 0)}, "cuisse_d": {"r": (amp * s, 0, 0)},
             "tibia_g": {"r": (plie if s < 0 else 4, 0, 0)}, "tibia_d": {"r": (plie if s > 0 else 4, 0, 0)},
             "bras_g": {"r": (bras * s, 0, 0)}, "bras_d": {"r": (-bras * s, 0, 0)},
             "torse": {"r": (torse, 3 * s, 0)}, "bassin": {"t": (0, bob, 0)}}
        if extra:
            for k, v in extra(s).items():
                p[k] = v
        cles.append((8, p))
        q = {k: dict(v) for k, v in p.items()}
        q["bassin"] = {"t": (0, -bob * 0.5, 0)}
        cles.append((4, q))
    return {"boucle": True, "cles": cles}


def repos(extra_a, extra_b, d=24):
    return {"boucle": True, "cles": [(d, extra_a), (d, extra_b)]}


# =============================================================================================== SlenderMan
def slender():
    R = Rig("hr_slender")
    COS, CHE = ("tissu", {"c": "#141418", "bruit": 8}), ("tissu", {"c": "#e8e8e6", "bruit": 4})
    B = humanoide(R, 22, 22, (8, 22, 4), 18, 18, (6, 9, 6),
                  {"torse": COS, "tete": ("uni", U("#ecebe6", 5)), "bras": COS, "avbras": COS, "jambe": COS},
                  ecart=1.8, larg_j=2.6, larg_b=2.2)
    T = B["torse"]
    R.boite(T, (0, 14, 2.1), (2.6, 14, 0.4), *CHE)
    R.boite(T, (0, 13, 2.35), (0.9, 11, 0.4), "uni", U("#a01010", 6))
    R.boite(T, (0, 19.5, 2.35), (1.6, 1.2, 0.4), "uni", U("#a01010", 6))
    for c in ("g", "d"):
        R.boite(B["avbras_" + c], (0, -19, 0), (2, 3, 2), "uni", U("#ecebe6", 5))     # mains blanches
        R.boite(B["tibia_" + c], (0, -21.5, 0.6), (2.6, 1, 3.6), "uni", U("#050505", 2))
    # visage : a peine deux ombres
    for s in (-1, 1):
        R.boite(B["tete"], (s * 1.4, 5, 3.05), (1, 1.2, 0.2), "uni", U("#cfcdc8", 3))
    # tentacules dans le dos
    for t in range(6):
        ang = (t - 2.5) * 28
        par = R.art(T, ((t - 2.5) * 1.2, 16, -2), (-30, ang, 0), nom=f"tent{t}")
        w = 1.6
        for k in range(5):
            seg = R.art(par, (0, 7 if k else 0, 0), (-16 + k * 4, 0, math.sin(t + k) * 14), nom=f"tent{t}_{k}")
            R.boite(seg, (0, 3.5, 0), (w, 7, w), "uni", U("#0a0a0c", 6))
            par, w = seg, max(0.6, w - 0.22)
    tent = lambda a: {f"tent{t}_{k}": {"r": (a * math.sin(t * 1.3 + k), 0, a * math.cos(t + k))} for t in range(6) for k in range(1, 5)}
    A = {
        "repos": repos({**tent(10), "tete": {"r": (0, 0, 8)}}, {**tent(-10), "tete": {"r": (0, 0, -3)}}, 30),
        "marche": marche(18, 6, 0.6, 12, 2, extra=lambda s: tent(8 * s)),
        "attaque": {"boucle": False, "cles": [
            (6, {**{f"tent{t}": {"r": (-80, 0, 0)} for t in range(6)}, "bras_g": {"r": (-100, 0, -10)}, "bras_d": {"r": (-100, 0, 10)},
                 "tete": {"r": (-10, 0, 25)}}),
            (4, {**{f"tent{t}": {"r": (-10, 0, 0)} for t in range(6)}, **{f"tent{t}_{k}": {"r": (30, 0, 0)} for t in range(6) for k in range(1, 5)},
                 "bras_g": {"r": (-70, 0, 0)}, "bras_d": {"r": (-70, 0, 0)}, "torse": {"r": (14, 0, 0)}}),
            (10, {})]},
    }
    return R, A


# =============================================================================================== Herobrine
def herobrine():
    R = Rig("hr_herobrine")
    PEAU, CHEM, PANT = ("peau", {"c": "#c8946a"}), ("tissu", {"c": "#1fa3b3"}), ("tissu", {"c": "#3b4ea0"})
    B = humanoide(R, 6, 6, (8, 12, 4), 6, 6, (8, 8, 8), {"torse": CHEM, "tete": PEAU, "bras": CHEM, "avbras": PEAU, "jambe": PANT,
                                                         "tibia": PANT}, ecart=2, larg_j=4, larg_b=4)
    H = B["tete"]
    R.boite(H, (0, 7.2, 0), (8.4, 1.8, 8.4), "uni", U("#3e2716", 10))
    R.boite(H, (0, 4.5, -4.1), (8.4, 6, 0.5), "uni", U("#3e2716", 10))
    for s in (-1, 1):
        R.boite(H, (s * 2, 4, 4.15), (2, 1, 0.3), "uni", L("#ffffff", 4))
    R.boite(H, (0, 1.6, 4.1), (3, 0.8, 0.3), "uni", U("#5a3420", 4))
    for c in ("g", "d"):
        R.boite(B["tibia_" + c], (0, -5.5, 0), (4.2, 1.5, 4.2), "uni", U("#4a4a4a", 8))
    A = {"repos": repos({"tete": {"r": (6, 10, 0)}, "bras_g": {"r": (4, 0, 0)}}, {"tete": {"r": (0, -10, 0)}, "bras_d": {"r": (4, 0, 0)}}, 30),
         "marche": marche(30, 30, 0.5, 14, 2),
         "attaque": {"boucle": False, "cles": [(5, {"bras_d": {"r": (-150, 0, 0)}, "torse": {"r": (-6, -20, 0)}}),
                                              (3, {"bras_d": {"r": (-20, 0, 0)}, "torse": {"r": (12, 20, 0)}}), (8, {})]}}
    return R, A


# =============================================================================================== Siren Head
def siren():
    R = Rig("hr_siren")
    PEAU = ("peau", {"c": "#8a7458", "bruit": 22, "veines": 1.5, "cv": "#4a3624"})
    B = humanoide(R, 26, 26, (9, 24, 5), 22, 22, (2, 2, 2), {"torse": PEAU, "tete": ("metal", {"pal": ["#5a5a5e", "#6a6a6e", "#4a4a4e"]}),
                                                           "bras": PEAU, "jambe": PEAU}, ecart=2.4, larg_j=2.6, larg_b=2.2, pr=8)
    T = B["torse"]
    for k in range(5):
        R.boite(T, (0, 8 + k * 3, 2.6), (8 - k * 0.6, 0.8, 0.3), "uni", U("#5a4636", 8))           # cotes
    R.boite(T, (0, 2, 2.6), (6, 3, 0.4), "uni", U("#4a3626", 10))
    # mat et sirenes
    M = B["tete"]
    R.boite(M, (0, 12, 0), (1.6, 24, 1.6), "metal", {"pal": ["#5a5a5e", "#6a6a6e", "#4a4a4e"]})
    R.boite(M, (0, 24, 0), (10, 1.4, 1.4), "metal", {"pal": ["#5a5a5e", "#6a6a6e"]})
    for s, c in ((-1, "g"), (1, "d")):
        S = R.art(M, (s * 5, 24, 0), (0, s * -35, 0), nom="sirene_" + c)
        R.boite(S, (0, 0, 2), (3, 3, 4), "metal", {"pal": ["#6a6a6e", "#7a7a7e"]})
        R.boite(S, (0, 0, 5), (5, 5, 2), "metal", {"pal": ["#7a7a7e", "#8a8a8e"]})
        R.boite(S, (0, 0, 6.2), (4, 4, 0.4), "uni", U("#111114", 4))
    for c in ("g", "d"):
        for f in range(3):
            R.boite(B["avbras_" + c], ((f - 1) * 0.7, -23.5, 0.6), (0.5, 4, 0.5), "uni", U("#3a2a1a", 6))
    sir = lambda a: {"sirene_g": {"r": (0, a, 0)}, "sirene_d": {"r": (0, a, 0)}}
    A = {"repos": repos({**sir(25), "tete": {"r": (0, 20, 6)}}, {**sir(-25), "tete": {"r": (0, -20, -6)}}, 40),
         "marche": marche(20, 14, 1.4, 22, 6, extra=lambda s: {"tete": {"r": (0, 8 * s, 4 * s)}}),
         "attaque": {"boucle": False, "cles": [
             (8, {"bras_g": {"r": (-160, 0, -20)}, "bras_d": {"r": (-160, 0, 20)}, "torse": {"r": (-12, 0, 0)}}),
             (4, {"bras_g": {"r": (-30, 0, 0)}, "bras_d": {"r": (-30, 0, 0)}, "torse": {"r": (30, 0, 0)}, "bassin": {"t": (0, -4, 0)}}),
             (12, {})]}}
    return R, A


# =============================================================================================== La Nonne
def nonne():
    R = Rig("hr_nonne")
    ROBE, PEAU = ("tissu", {"c": "#16141a", "bruit": 8}), ("peau", {"c": "#ddd2bc", "veines": 1, "cv": "#8a7a90"})
    bas = R.art(None, (0, 16, 0), nom="bassin")
    jupe = R.art(bas, (0, 0, 0), nom="jupe")
    for k, (w, y) in enumerate(((12, -2), (13, -6), (14, -10), (15, -14))):
        R.boite(jupe, (0, y, 0), (w, 4, w * 0.6), *ROBE)
    T = R.art(bas, (0, 0, 0), nom="torse")
    R.boite(T, (0, 6, 0), (9, 12, 5), *ROBE)
    R.boite(T, (0, 11, 2.6), (6, 2.6, 0.4), "uni", U("#f2efe6", 4))                       # guimpe
    R.boite(T, (0, 7, 2.7), (0.6, 4, 0.3), "uni", U("#c8a040", 6))                        # croix
    R.boite(T, (0, 8, 2.75), (2.4, 0.6, 0.3), "uni", U("#c8a040", 6))
    H = R.art(T, (0, 12, 0), nom="tete")
    R.boite(H, (0, 4, 0.3), (7, 8, 7), *PEAU)
    R.boite(H, (0, 8.6, -0.3), (8.4, 1.4, 8.2), "uni", U("#111014", 8))
    R.boite(H, (0, 1.5, -4), (8.4, 13, 1.2), "uni", U("#111014", 8))
    for s in (-1, 1):
        R.boite(H, (s * 4.1, 3, -1), (0.9, 11, 7), "uni", U("#111014", 8))
        R.boite(H, (s * 1.6, 5, 3.85), (2, 1.8, 0.3), "uni", U("#030303", 2))
        R.boite(H, (s * 1.6, 5, 4.0), (0.6, 0.6, 0.3), "uni", L("#ffd22a", 4))
    R.boite(H, (0, 2, 3.9), (2, 2.4, 0.3), "uni", U("#0a0505", 2))
    for s, c in ((-1, "g"), (1, "d")):
        b = R.art(T, (s * 5.6, 10.5, 0), nom="bras_" + c)
        R.boite(b, (0, -5, 0), (2.8, 10, 2.8), *ROBE)
        a = R.art(b, (0, -10, 0), nom="avbras_" + c)
        R.boite(a, (0, -1.5, 0), (2, 3, 2), *PEAU)
        for f in range(4):
            R.boite(a, ((f - 1.5) * 0.5, -4.2, 0.3), (0.35, 2.8, 0.35), "uni", U("#cfc4ae", 4))
    A = {"repos": {"boucle": True, "cles": [(20, {"bassin": {"t": (0, 1.5, 0)}, "jupe": {"r": (4, 0, 2)}, "tete": {"r": (0, 0, 12)}}),
                                            (20, {"bassin": {"t": (0, -0.5, 0)}, "jupe": {"r": (-3, 0, -2)}, "tete": {"r": (4, 0, 4)}})]},
         "marche": {"boucle": True, "cles": [(10, {"bassin": {"t": (0, 1.5, 0)}, "jupe": {"r": (-10, 0, 3)}, "torse": {"r": (10, 0, 0)},
                                                   "bras_g": {"r": (-70, 0, 0)}, "bras_d": {"r": (-70, 0, 0)}}),
                                             (10, {"bassin": {"t": (0, 0, 0)}, "jupe": {"r": (-6, 0, -3)}, "torse": {"r": (10, 0, 0)},
                                                   "bras_g": {"r": (-80, 0, 0)}, "bras_d": {"r": (-80, 0, 0)}})]},
         "attaque": {"boucle": False, "cles": [(5, {"bras_g": {"r": (-120, 0, -20)}, "bras_d": {"r": (-120, 0, 20)}, "tete": {"r": (-20, 0, 40)}}),
                                              (4, {"bras_g": {"r": (-60, 0, 0)}, "bras_d": {"r": (-60, 0, 0)}, "torse": {"r": (25, 0, 0)}}), (10, {})]}}
    return R, A


# =============================================================================================== Le Clown
def clown():
    R = Rig("hr_clown")
    HAB, PEAU = ("tissu", {"c": "#e8e6e0", "bruit": 8}), ("peau", {"c": "#f4f2ec", "bruit": 6})
    B = humanoide(R, 7, 6, (9, 12, 6), 6, 6, (8, 8, 8), {"torse": HAB, "tete": PEAU, "bras": HAB, "avbras": HAB, "jambe": HAB},
                  ecart=2.3, larg_j=4.2, larg_b=4)
    T, H = B["torse"], B["tete"]
    R.boite(T, (0, 12, 0), (14, 2, 10), "uni", U("#f6f4f0", 12))                          # collerette
    R.boite(T, (0, 11, 0), (12, 1.6, 9), "uni", U("#d8d4cc", 12))
    for y in (3, 6, 9):
        R.boite(T, (0, y, 3.2), (1.8, 1.8, 1.4), "uni", U("#e01818", 10))                 # pompons
    for c in ("g", "d"):
        R.boite(B["tibia_" + c], (0, -6, 1.4), (4.6, 1.6, 6.6), "uni", U("#e05a10", 8))     # grosses chaussures
        R.boite(B["avbras_" + c], (0, -6.5, 0), (3.6, 1.4, 3.6), "uni", U("#f6f4f0", 8))
    R.boite(H, (0, 3.5, 4.8), (2.4, 2.4, 2.4), "uni", U("#e01818", 8))                     # nez
    for s in (-1, 1):
        R.boite(H, (s * 2, 5.4, 4.05), (1.8, 1.6, 0.3), "uni", U("#0a0a0a", 2))
        R.boite(H, (s * 2, 5.4, 4.2), (0.6, 0.6, 0.3), "uni", L("#ffd23a", 4))
        R.boite(H, (s * 2, 7.2, 4.05), (0.5, 1.8, 0.3), "uni", U("#c0202a", 4))
        R.boite(H, (s * 5, 6, -1), (2.4, 4, 6), "uni", U("#d8401a", 30))                  # touffes
        R.boite(H, (s * 6.4, 7.2, -1.5), (1.4, 2.4, 4), "uni", U("#e8602a", 30))
    R.boite(H, (0, 1.6, 4.05), (6, 1.2, 0.3), "uni", U("#b01020", 6))
    for x in (-2, -0.7, 0.7, 2):
        R.boite(H, (x, 1.7, 4.2), (0.5, 0.8, 0.3), "uni", U("#f4f0dc", 4))
    # le ballon rouge, au bout de sa ficelle
    # 26/11/2026 : ficelle plus longue et penchée vers l'extérieur, le ballon flotte au-dessus de l'épaule (il était dans la tête)
    F_ = R.art(B["avbras_g"], (0, -6, 0), (0, 0, 24), nom="ficelle")
    R.boite(F_, (0, 13, 0), (0.25, 26, 0.25), "uni", U("#e8e8e8", 2))
    R.boite(F_, (0, 30, 0), (7, 8, 7), "uni", U("#e01818", 14))
    R.boite(F_, (0, 30.5, 3.6), (2, 2.5, 0.3), "uni", U("#ff7a7a", 6))
    R.boite(F_, (0, 25.6, 0), (1.4, 1.2, 1.4), "uni", U("#b01010", 6))
    A = {"repos": repos({"tete": {"r": (0, 0, 22)}, "ficelle": {"r": (6, 0, 6)}}, {"tete": {"r": (0, 0, -14)}, "ficelle": {"r": (-4, 0, -6)}}, 22),
         "marche": marche(34, 34, 1.6, 20, 6, extra=lambda s: {"tete": {"r": (0, 0, 12 * s)}, "ficelle": {"r": (8 * s, 0, 0)},
                                                             "bras_g": {"r": (-40, 0, -10)}}),
         "attaque": {"boucle": False, "cles": [(5, {"bras_d": {"r": (-130, 0, 20)}, "tete": {"r": (-25, 0, 30)}, "torse": {"r": (-8, 0, 0)}}),
                                              (3, {"bras_d": {"r": (-30, 0, 0)}, "torse": {"r": (20, 0, 0)}, "tete": {"r": (10, 0, -10)}}), (10, {})]}}
    return R, A


# =============================================================================================== Pinhead
def pinhead():
    R = Rig("hr_pinhead")
    CUIR, PEAU = ("tissu", {"c": "#18161c", "bruit": 10}), ("peau", {"c": "#d4cfc4", "veines": 1.2, "cv": "#7a3a3a"})
    B = humanoide(R, 7, 6, (8, 12, 4), 6, 6, (8, 8, 8), {"torse": CUIR, "tete": PEAU, "bras": CUIR, "avbras": CUIR, "jambe": CUIR},
                  ecart=2, larg_j=4, larg_b=4)
    T, H = B["torse"], B["tete"]
    pan = R.art(T, (0, 0, 0), nom="soutane")
    R.boite(pan, (0, -6, 0), (9, 12, 5), "uni", U("#121016", 8))
    for x in (-2.5, 0, 2.5):
        R.boite(T, (x, 6, 2.15), (0.5, 10, 0.3), "uni", U("#3a3640", 4))
    R.boite(T, (0, 9, 2.2), (6, 3, 0.4), "uni", U("#a8a098", 4))                            # chairs ouvertes
    for v in (-2.4, -0.8, 0.8, 2.4):
        R.boite(H, (v, 4, 4.05), (0.25, 8, 0.2), "uni", U("#5a2222", 3))
        R.boite(H, (0, 4 + v, 4.05), (8, 0.25, 0.2), "uni", U("#5a2222", 3))
        for v2 in (-2.4, -0.8, 0.8, 2.4):
            if abs(v2 - 0.8) < 0.1 and abs(v) < 2:
                continue
            R.boite(H, (v, 4 + v2, 5), (0.3, 0.3, 1.9), "uni", U("#9aa0a8", 6))
            R.boite(H, (v, 8.9, v2), (0.3, 1.9, 0.3), "uni", U("#9aa0a8", 6))
            for s in (-1, 1):
                R.boite(H, (s * 4.9, 4 + v, v2), (1.9, 0.3, 0.3), "uni", U("#9aa0a8", 6))
    for s in (-1, 1):
        R.boite(H, (s * 1.6, 4.6, 4.1), (1.6, 1, 0.3), "uni", U("#050505", 2))
    # chaines a crochets qui pendent des mains
    for c in ("g", "d"):
        ch = R.art(B["avbras_" + c], (0, -6, 0), nom="chaine_" + c)
        for k in range(5):
            R.boite(ch, (0, -1 - k * 2, 0), (0.6, 1.6, 0.6) if k % 2 else (0.6, 1.6, 0.25), "uni", U("#7a7a80", 8))
        R.boite(ch, (0, -11.5, 0.8), (0.5, 0.5, 2), "uni", U("#9a9aa0", 6))
    A = {"repos": repos({"chaine_g": {"r": (8, 0, 4)}, "chaine_d": {"r": (-6, 0, -4)}, "tete": {"r": (-4, 6, 0)}},
                        {"chaine_g": {"r": (-6, 0, -2)}, "chaine_d": {"r": (8, 0, 2)}, "tete": {"r": (0, -6, 0)}}, 30),
         "marche": marche(16, 10, 0.3, 10, 0, extra=lambda s: {"soutane": {"r": (-8 * s, 0, 0)}, "chaine_g": {"r": (14 * s, 0, 0)},
                                                             "chaine_d": {"r": (-14 * s, 0, 0)}}),
         "attaque": {"boucle": False, "cles": [(6, {"bras_d": {"r": (-160, 0, 0)}, "chaine_d": {"r": (-60, 0, 0)}}),
                                              (4, {"bras_d": {"r": (-80, 0, 0)}, "chaine_d": {"r": (-90, 0, 0)}, "torse": {"r": (10, 0, 0)}}), (10, {})]}}
    return R, A


# =============================================================================================== La Dame blanche
def dame():
    R = Rig("hr_dame")
    ROBE = ("tissu", {"c": "#eeeef8", "bruit": 8})
    bas = R.art(None, (0, 18, 0), nom="bassin")
    jupe = R.art(bas, (0, 0, 0), nom="jupe")
    for k, (w, y) in enumerate(((10, -2), (12, -6), (14, -10), (16, -14), (18, -17))):
        R.boite(jupe, (0, y, 0), (w, 4, w * 0.7), *ROBE)
    T = R.art(bas, (0, 0, 0), nom="torse")
    R.boite(T, (0, 6, 0), (8, 12, 4.5), "uni", U("#f6f6fc", 6))
    H = R.art(T, (0, 12, 0), nom="tete")
    R.boite(H, (0, 4, 0.3), (7, 8, 7), "uni", U("#eef0f8", 5))
    C = ("uni", U("#ffffff", 12))
    R.boite(H, (0, 8.6, -0.3), (8, 1.4, 8), *C)
    R.boite(H, (0, -2, -4.1), (8, 20, 1.2), *C)
    for s in (-1, 1):
        R.boite(H, (s * 4, 0, -0.5), (1, 16, 7.5), *C)
        R.boite(H, (s * 1.6, 5, 3.85), (1.8, 1.8, 0.3), "uni", L("#c8e8ff", 6))
        R.boite(H, (s * 1.6, 3, 3.9), (0.4, 2.4, 0.3), "uni", U("#20202a", 2))
    R.boite(H, (0, 1.6, 3.85), (1.8, 2.2, 0.3), "uni", U("#14141c", 2))
    for s, c in ((-1, "g"), (1, "d")):
        b = R.art(T, (s * 5, 10.5, 0), (-80, 0, 0), nom="bras_" + c)
        R.boite(b, (0, -5, 0), (2.4, 10, 2.4), "uni", U("#f6f6fc", 6))
        a = R.art(b, (0, -10, 0), nom="avbras_" + c)
        R.boite(a, (0, -4, 0), (2, 8, 2), "uni", U("#eceef6", 6))
        for f in range(4):
            R.boite(a, ((f - 1.5) * 0.5, -9, 0), (0.3, 2.4, 0.3), "uni", U("#d8d8e2", 4))
        R.boite(b, (0, -6, 1.6), (3, 9, 0.6), *ROBE)                                           # manches flottantes
    A = {"repos": {"boucle": True, "cles": [(24, {"bassin": {"t": (0, 2, 0)}, "jupe": {"r": (5, 6, 0)}, "tete": {"r": (8, 0, 6)}}),
                                            (24, {"bassin": {"t": (0, -1, 0)}, "jupe": {"r": (-4, -6, 0)}, "tete": {"r": (0, 0, -4)}})]},
         "marche": {"boucle": True, "cles": [(10, {"bassin": {"t": (0, 2, 0)}, "jupe": {"r": (-14, 4, 0)}, "torse": {"r": (12, 0, 0)}}),
                                             (10, {"bassin": {"t": (0, 0.5, 0)}, "jupe": {"r": (-10, -4, 0)}, "torse": {"r": (12, 0, 0)}})]},
         "attaque": {"boucle": False, "cles": [(6, {"tete": {"r": (-40, 0, 0)}, "bras_g": {"r": (-60, 0, -50)}, "bras_d": {"r": (-60, 0, 50)},
                                                    "jupe": {"r": (12, 0, 0)}}),
                                              (4, {"torse": {"r": (25, 0, 0)}, "bras_g": {"r": (0, 0, 0)}, "bras_d": {"r": (0, 0, 0)}}), (12, {})]}}
    return R, A


# =============================================================================================== Le Loup-garou
def loup():
    R = Rig("hr_loup")
    POIL, CLAIR = ("fourrure", {"c": "#6e5c48"}), ("fourrure", {"c": "#96806a"})
    B = humanoide(R, 7, 8, (10, 12, 7), 7, 7, (7, 7, 7), {"torse": POIL, "tete": POIL, "bras": POIL, "jambe": POIL},
                  ecart=2.8, larg_j=4.2, larg_b=4.2, pr=25)
    T, H = B["torse"], B["tete"]
    R.boite(T, (0, 9, 1), (12, 6, 8), *POIL)                                                    # epaules massives
    R.boite(T, (0, 5, 3.6), (7, 6, 0.6), *CLAIR)
    H.r = (-20, 0, 0)
    R.boite(H, (0, 2.6, 6), (4.4, 3.6, 5.6), *CLAIR)                                           # museau
    R.boite(H, (0, 3.8, 8.9), (1.8, 1.2, 0.4), "uni", U("#151010", 2))
    R.boite(H, (0, 0.9, 5.8), (4, 1, 4.6), "uni", U("#5a2a22", 6))
    for x in (-1.4, 1.4):
        R.boite(H, (x, 1.6, 8.2), (0.5, 1.2, 0.5), "uni", U("#f0ead8", 3))
    for s in (-1, 1):
        R.boite(H, (s * 2.4, 8.4, -1), (2, 3, 1.4), *POIL)
        R.boite(H, (s * 1.8, 4.8, 3.55), (1.4, 0.9, 0.3), "uni", L("#ffd030", 6))
    for c in ("g", "d"):
        for f in range(3):
            R.boite(B["avbras_" + c], ((f - 1) * 1.3, -7.8, 1.4), (0.5, 2.2, 0.5), "uni", U("#e8e0cc", 4))   # griffes
        R.boite(B["tibia_" + c], (0, -8, 2), (4, 1.5, 4.5), *POIL)
    Q = R.art(B["bassin"], (0, 1, -3.4), (-40, 0, 0), nom="queue")
    R.boite(Q, (0, -5, 0), (2.6, 10, 2.6), *POIL)
    A = {"repos": repos({"tete": {"r": (-35, 0, 0)}, "queue": {"r": (10, 10, 0)}, "bassin": {"t": (0, 0.5, 0)}},
                        {"tete": {"r": (-15, 10, 0)}, "queue": {"r": (0, -10, 0)}}, 26),
         "marche": marche(38, 50, 1.4, 30, 10, extra=lambda s: {"queue": {"r": (0, 20 * s, 0)}, "tete": {"r": (6 * s, 0, 0)}}),
         "attaque": {"boucle": False, "cles": [(4, {"bras_d": {"r": (-150, 0, 30)}, "bras_g": {"r": (-150, 0, -30)}, "tete": {"r": (-30, 0, 0)}}),
                                              (3, {"bras_d": {"r": (-20, 0, -10)}, "bras_g": {"r": (-20, 0, 10)}, "torse": {"r": (20, 0, 0)}}), (8, {})]}}
    return R, A


# =============================================================================================== Le Feu follet
def feu():
    R = Rig("hr_feu")
    c = R.art(None, (0, 8, 0), nom="coeur")
    for (w, y, col) in ((6, 0, "#bff0ff"), (4.6, 3.6, "#7fd8ff"), (3.2, 6.4, "#4aa8ff"), (2, 8.6, "#2a70ff")):
        R.boite(c, (0, y, 0), (w, w, w), "uni", L(col, 30))
    for s in (-1, 1):
        R.boite(c, (s * 1.2, 0.6, 3.05), (0.8, 1, 0.2), "uni", U("#0a2040", 4))
    for k in range(5):
        a = k / 5 * math.tau
        R.boite(c, (math.cos(a) * 5, -2 + k, math.sin(a) * 5), (1, 1, 1), "uni", L("#bfe8ff", 20))
    A = {"repos": {"boucle": True, "cles": [(10, {"coeur": {"t": (0, 2, 0), "s": 1.1, "r": (0, 90, 0)}}),
                                            (10, {"coeur": {"t": (0, 0, 0), "s": 0.92, "r": (0, 180, 0)}}),
                                            (10, {"coeur": {"t": (0, 2, 0), "s": 1.1, "r": (0, 270, 0)}}),
                                            (10, {"coeur": {"t": (0, 0, 0), "s": 0.92, "r": (0, 359, 0)}})]}}
    A["marche"] = A["repos"]
    A["attaque"] = {"boucle": False, "cles": [(4, {"coeur": {"s": 1.5}}), (6, {"coeur": {"s": 0.8}}), (6, {})]}
    return R, A


# =============================================================================================== Le Rodeur des grottes
def rodeur():
    R = Rig("hr_rodeur")
    PEAU = ("peau", {"c": "#b8b2a8", "bruit": 16, "veines": 2, "cv": "#6a5a6a"})
    B = humanoide(R, 7, 7, (7, 13, 4), 11, 11, (6, 8, 6), {"torse": PEAU, "tete": PEAU, "bras": PEAU, "jambe": PEAU},
                  ecart=2.2, larg_j=2.6, larg_b=2.2, pr=45)
    T, H = B["torse"], B["tete"]
    for k in range(4):
        R.boite(T, (0, 4 + k * 2.4, 2.1), (6 - k * 0.5, 0.7, 0.3), "uni", U("#7a746a", 6))
    for k in range(5):
        R.boite(T, (0, 2 + k * 2.4, -2.2), (1.2, 1.2, 0.6), "uni", U("#a29c92", 8))           # vertebres
    H.r = (-40, 0, 0)
    R.boite(H, (0, -0.6, 1.2), (5, 3, 4.6), "uni", U("#a8a298", 14))
    R.boite(H, (0, 0, 3.6), (3.6, 2.6, 0.3), "uni", U("#0a0808", 2))
    for s in (-1, 1):
        R.boite(H, (s * 1.5, 5, 3.05), (2, 2.6, 0.3), "uni", U("#030303", 2))
        R.boite(H, (s * 1.5, 4.6, 3.2), (0.4, 0.4, 0.3), "uni", L("#e8e8c8", 4))
    for c in ("g", "d"):
        for f in range(4):
            R.boite(B["avbras_" + c], ((f - 1.5) * 0.55, -12.5, 0.3), (0.35, 3.4, 0.35), "uni", U("#8a8478", 4))
    A = {"repos": repos({"bras_g": {"r": (-50, 0, -8)}, "bras_d": {"r": (-40, 0, 8)}, "tete": {"r": (0, 20, 10)}},
                        {"bras_g": {"r": (-40, 0, -8)}, "bras_d": {"r": (-50, 0, 8)}, "tete": {"r": (0, -20, -6)}}, 20),
         "marche": marche(30, 40, 0.8, 30, 6, extra=lambda s: {"bras_g": {"r": (-60 + 30 * s, 0, 0)}, "bras_d": {"r": (-60 - 30 * s, 0, 0)},
                                                             "tete": {"r": (0, 10 * s, 0)}}),
         "attaque": {"boucle": False, "cles": [(4, {"bras_g": {"r": (-170, 0, -20)}, "bras_d": {"r": (-170, 0, 20)}, "bassin": {"r": (20, 0, 0)}}),
                                              (3, {"bras_g": {"r": (-40, 0, 0)}, "bras_d": {"r": (-40, 0, 0)}, "bassin": {"r": (60, 0, 0)}}), (8, {})]}}
    return R, A


# =============================================================================================== Le Croque-mitaine
def croque():
    R = Rig("hr_croque")
    CAPE = ("haillons", {"pal": ["#141016", "#1c141c", "#0c0a0e", "#2a1018"], "trou": True})
    SOMBRE = ("tissu", {"c": "#140e12", "bruit": 8})
    B = humanoide(R, 10, 10, (10, 14, 6), 10, 10, (8, 9, 8), {"torse": SOMBRE, "tete": SOMBRE, "bras": SOMBRE, "avbras": SOMBRE, "jambe": SOMBRE},
                  ecart=2.6, larg_j=3.6, larg_b=3.4, pr=10)
    T, H = B["torse"], B["tete"]
    cape = R.art(T, (0, 13, -3.4), (8, 0, 0), nom="cape")
    for j, x in enumerate((-6, -3, 0, 3, 6)):
        R.boite(cape, (x, -16 - (j % 2) * 3, 0), (3.4, 32 + (j % 2) * 6, 0.8), *CAPE)
    R.boite(H, (0, 5, 0), (10, 11, 10), "haillons", {"pal": ["#141016", "#1c141c", "#0c0a0e"]})      # capuche
    R.boite(H, (0, 4, 5.05), (6.4, 7, 0.3), "uni", U("#000000", 1))
    for s in (-1, 1):
        R.boite(H, (s * 1.6, 5, 5.25), (1.4, 0.8, 0.3), "uni", L("#ff1a1a", 6))
        for (x, y, w, h) in ((5.6, 9, 2.4, 2.4), (7.4, 11, 2, 2.4), (8.4, 13.4, 1.6, 2.6), (8.8, 16, 1.2, 2.2)):
            R.boite(H, (s * x, y, 0), (w, h, w), "uni", U("#d8d0bc", 12))
    for c in ("g", "d"):
        for f in range(4):
            R.boite(B["avbras_" + c], ((f - 1.5) * 0.8, -12.5, 0.4), (0.45, 5, 0.45), "uni", U("#c8c0b0", 6))
    sac = R.art(T, (5, 6, -4), (10, 0, -10), nom="sac")
    R.boite(sac, (0, -3, -2), (7, 9, 6), "toile", {"pal": ["#6a5a3c", "#5a4a30", "#7a6a48", "#4a3a26"]})
    R.boite(sac, (0, 2, -2), (3, 2, 3), "uni", U("#3a2a18", 6))
    A = {"repos": repos({"cape": {"r": (12, 0, 4)}, "tete": {"r": (10, 0, 10)}, "bras_g": {"r": (-6, 0, -6)}},
                        {"cape": {"r": (4, 0, -4)}, "tete": {"r": (4, 0, -6)}, "bras_d": {"r": (-6, 0, 6)}}, 30),
         "marche": marche(22, 18, 1.0, 16, 4, extra=lambda s: {"cape": {"r": (20 + 6 * s, 0, 0)}, "sac": {"r": (8 * s, 0, 0)}}),
         "attaque": {"boucle": False, "cles": [(6, {"bras_d": {"r": (-170, 0, 30)}, "bras_g": {"r": (-170, 0, -30)}, "tete": {"r": (-20, 0, 0)},
                                                    "cape": {"r": (40, 0, 0)}}),
                                              (4, {"bras_d": {"r": (-40, 0, -10)}, "bras_g": {"r": (-40, 0, 10)}, "torse": {"r": (20, 0, 0)}}), (12, {})]}}
    return R, A


CREATURES_RIG = {"slender": slender, "herobrine": herobrine, "siren": siren, "nonne": nonne, "clown": clown, "pinhead": pinhead,
                 "dame": dame, "loup": loup, "feu": feu, "rodeur": rodeur, "croque": croque}


# taille d'affichage du squelette (le mob garde son echelle a lui pour la vie et les coups)
TAILLE = {"slender": 1.15, "herobrine": 1.0, "siren": 1.25, "nonne": 0.95, "clown": 1.0, "pinhead": 1.05, "dame": 1.0,
          "loup": 1.35, "feu": 0.9, "rodeur": 1.1, "croque": 1.6}

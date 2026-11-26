"""Les squelettes des boss (memes formes que les maquettes 3D validees) et leurs animations.

Grimoire Vivant : livre ouvert en V, oeil dans la reliure, eventail de pages a runes, 4 tentacules d'encre,
anneau de runes en orbite.  Corbeau-Epouvantail : epouvantail decharne attache a sa croix, tete en sac cousu,
chapeau dechire, cape de plumes, longues jambes de batons, corbeaux perches sur la traverse.
Petits modeles : corbeau (deux battements d'ailes), livre volant, tentacule qui sort du sol, rune, lune rouge.
"""
import math
from rig import Rig

PIERRE_ENCRE = {"pal": ["#140a1e", "#1d1030", "#26143c", "#0d0614", "#2f1a4a"], "fissures": .3}
PLUMES_HAILLONS = {"pal": ["#0e0e14", "#181824", "#232338", "#2c3050"], "trou": True}


# ================================================================================================ Grimoire
def grimoire():
    R = Rig("grimoire", racine=(0, 47, 0))
    G = R.art(None, (0, 0, 0), (22, 0, 0), nom="livre")
    for sx, cote in ((-1, "g"), (1, "d")):
        cov = R.art(G, (0, 0, 0), (0, 0, sx * -18), nom="couv_" + cote)
        R.boite(cov, (sx * 26, 0, 0), (52, 3, 40), "cuir", {"rune": True})
        R.boite(cov, (sx * 25, 3, 0), (48, 5, 37), "page", {"faces": ["tranche", "tranche", "page", "page", "tranche", "tranche"]})
        if sx > 0:
            f = R.art(cov, (52, 0, 0), (0, 0, 70), nom="fermoir")
            R.boite(f, (0, -6, 0), (3, 12, 8), "uni", {"c": "#d9a640"})
            R.boite(f, (0, -12, 0), (4, 4, 10), "uni", {"c": "#f0c95a"})
    R.boite(G, (0, -2, 0), (8, 8, 40), "cuir", {"liseré": False})
    O = R.art(G, (0, 4, 20), (10, 0, 0), nom="oeil")
    R.boite(O, (0, 0, 0), (26, 20, 6), "oeil", {"lueur": True, "faces": ["cuir", "cuir", "cuir", "cuir", "oeil", "cuir"]})
    PH = R.art(O, (0, 11, 2), (25, 0, 0), nom="paup_h")
    R.boite(PH, (0, 0, 0), (30, 4, 9), "cuir", {"liseré": False})
    for x in (-12, -6, 0, 6, 12):
        R.boite(PH, (x, 3, 3), (1.5, 4, 1.5), "uni", {"c": "#1a0f22"})
    PB = R.art(O, (0, -11, 2), (-25, 0, 0), nom="paup_b")
    R.boite(PB, (0, 0, 0), (30, 4, 9), "cuir", {"liseré": False})
    for i in range(9):
        a = -60 + i * 15
        pg = R.art(G, (0, 8, 0), (0, 0, a), nom=f"page{i}")
        R.boite(pg, (0, 22, (i - 4) * 1.5), (1, 40, 30), "page", {"faces": ["page", "page", "tranche", "tranche", "tranche", "tranche"]})
        if i % 3 == 1:
            R.boite(pg, (1, 26, (i - 4) * 1.5), (0.5, 18, 14), "runes", {"lueur": True})
    for t in range(4):
        par = R.art(G, ((t - 1.5) * 16, -6, 6 if t % 2 else -6), (0, t * 40, 0), nom=f"tent{t}")
        wd = 8
        for k in range(5):
            seg = R.art(par, (0, -12 if k else 0, 0), (math.sin(k * .8 + t) * 16, 0, math.cos(k * .7 + t) * 16), nom=f"tent{t}_{k}")
            R.boite(seg, (0, -6, 0), (wd, 12, wd), "pierre", PIERRE_ENCRE)
            if k in (1, 3):
                R.boite(seg, (wd / 2 + 0.3, -5, 0), (0.6, 5, 3), "runes", {"lueur": True})
            par = seg
            wd = max(3, wd - 1.2)
    anneau = R.art(None, (0, 30, 0), (0, 0, 0), nom="anneau")
    for k in range(8):
        a = k / 8 * math.pi * 2
        R.boite(anneau, (math.cos(a) * 60, math.sin(a * 3) * 5, math.sin(a) * 60), (5, 5, 5), "runes",
                {"lueur": True, "fond": "#3a1a6a"})
    return R


def _t(*a):
    return tuple(a)


GRIMOIRE_ANIM = {
    # vol : flotte, les couvertures battent doucement, les pages ondulent, les tentacules ondoient, l'anneau tourne
    "vol": {"boucle": True, "cles": [
        (20, {"racine": {"t": (0, 3, 0)}, "couv_g": {"r": (0, 0, 6)}, "couv_d": {"r": (0, 0, -6)},
              **{f"page{i}": {"r": (0, 0, 4 * math.sin(i))} for i in range(9)},
              **{f"tent{t}_{k}": {"r": (8 * math.sin(t + k), 0, 6)} for t in range(4) for k in range(1, 5)},
              "anneau": {"r": (0, 45, 0)}, "oeil": {"r": (-4, 0, 0)}}),
        (20, {"racine": {"t": (0, -2, 0)}, "couv_g": {"r": (0, 0, -4)}, "couv_d": {"r": (0, 0, 4)},
              **{f"page{i}": {"r": (0, 0, -4 * math.sin(i))} for i in range(9)},
              **{f"tent{t}_{k}": {"r": (-8 * math.sin(t + k), 0, -6)} for t in range(4) for k in range(1, 5)},
              "anneau": {"r": (0, 90, 0)}, "oeil": {"r": (4, 0, 0)}}),
    ]},
    # pages tranchantes : l'eventail s'ouvre en grand, les couvertures s'ecartent, puis claquent
    "pages": {"boucle": False, "cles": [
        (12, {"couv_g": {"r": (0, 0, 24)}, "couv_d": {"r": (0, 0, -24)},
              **{f"page{i}": {"r": (0, 0, (i - 4) * 9), "s": 1.15} for i in range(9)}, "oeil": {"s": 1.15}}),
        (4, {"couv_g": {"r": (0, 0, -10)}, "couv_d": {"r": (0, 0, 10)},
             **{f"page{i}": {"r": (0, 0, -(i - 4) * 4)} for i in range(9)}}),
        (10, {}),
    ]},
    # tentacule : les tentacules se tendent vers le bas et fouettent
    "fouet": {"boucle": False, "cles": [
        (10, {**{f"tent{t}_{k}": {"r": (-14, 0, 0)} for t in range(4) for k in range(5)}, "oeil": {"r": (-12, 0, 0)}}),
        (4, {**{f"tent{t}_{k}": {"r": (18, 0, 0)} for t in range(4) for k in range(5)}, "racine": {"t": (0, -4, 0)}}),
        (10, {}),
    ]},
    # enchaine : tire au sol, couvertures a moitie refermees, tremblements, tentacules molles
    "enchaine": {"boucle": True, "cles": [
        (4, {"couv_g": {"r": (0, 0, -30)}, "couv_d": {"r": (0, 0, 30)}, "racine": {"t": (1.5, 0, 0)},
             **{f"tent{t}_{k}": {"r": (20, 0, 0)} for t in range(4) for k in range(5)},
             **{f"page{i}": {"r": (0, 0, -(i - 4) * 5), "s": 0.8} for i in range(9)}, "paup_h": {"r": (-25, 0, 0)}}),
        (4, {"couv_g": {"r": (0, 0, -26)}, "couv_d": {"r": (0, 0, 26)}, "racine": {"t": (-1.5, 0, 0)},
             **{f"tent{t}_{k}": {"r": (22, 0, 0)} for t in range(4) for k in range(5)},
             **{f"page{i}": {"r": (0, 0, -(i - 4) * 5), "s": 0.8} for i in range(9)}, "paup_h": {"r": (-20, 0, 0)}}),
    ]},
    # rugissement (changement de phase) : tout s'ouvre, l'oeil grossit
    "rugit": {"boucle": False, "cles": [
        (8, {"couv_g": {"r": (0, 0, 30)}, "couv_d": {"r": (0, 0, -30)}, "oeil": {"s": 1.4}, "paup_h": {"r": (25, 0, 0)},
             "paup_b": {"r": (-25, 0, 0)}, **{f"page{i}": {"r": (0, 0, (i - 4) * 12), "s": 1.25} for i in range(9)},
             "anneau": {"s": 1.4}}),
        (24, {"couv_g": {"r": (0, 0, 32)}, "couv_d": {"r": (0, 0, -32)}, "oeil": {"s": 1.5}, "racine": {"t": (0, 4, 0)},
              **{f"page{i}": {"r": (0, 0, (i - 4) * 13), "s": 1.3} for i in range(9)}, "anneau": {"s": 1.5, "r": (0, 120, 0)}}),
        (10, {}),
    ]},
    # apparition : le livre ferme tombe puis s'ouvre
    "apparition": {"boucle": False, "cles": [
        (1, {"racine": {"s": 0.05, "t": (0, 40, 0)}}),
        (20, {"racine": {"s": 0.6}, "couv_g": {"r": (0, 0, -70)}, "couv_d": {"r": (0, 0, 70)}}),
        (14, {"couv_g": {"r": (0, 0, -70)}, "couv_d": {"r": (0, 0, 70)}}),
        (8, {"couv_g": {"r": (0, 0, 30)}, "couv_d": {"r": (0, 0, -30)}, "oeil": {"s": 1.4}}),
        (10, {}),
    ]},
    # mort : il se referme d'un coup, tombe et retrecit
    "mort": {"boucle": False, "fige": True, "cles": [
        (6, {"couv_g": {"r": (0, 0, -72)}, "couv_d": {"r": (0, 0, 72)}, "oeil": {"s": 0.4}}),
        (24, {"couv_g": {"r": (0, 0, -72)}, "couv_d": {"r": (0, 0, 72)}, "racine": {"t": (0, -30, 0)}, "livre": {"r": (60, 0, 30)},
              "anneau": {"s": 0.01}, **{f"page{i}": {"s": 0.01} for i in range(9)}}),
        (30, {"racine": {"s": 0.01, "t": (0, -40, 0)}}),
    ]},
}


# ================================================================================================ Corbeau
def _corbeau_perche(R, par, p, ry_signe):
    x, y, z = p
    R.boite(par, (x, y + 2, z), (4, 4, 8), "plumes")
    R.boite(par, (x, y + 4, z + 5 * ry_signe), (3.4, 3.4, 3.4), "plumes")
    R.boite(par, (x, y + 3.5, z + 7.6 * ry_signe), (1.2, 1.2, 3), "uni", {"c": "#3a3a40"})
    R.boite(par, (x, y + 1.5, z - 6 * ry_signe), (4, 1, 5), "plumes")
    for ex in (-1.75, 1.75):
        R.boite(par, (x + ex, y + 4.7, z + 5.6 * ry_signe), (0.3, 0.8, 0.8), "uni", {"c": "#ff2a10", "lueur": True})


def corbeau():
    R = Rig("corbeau", racine=(0, 0, 0))
    X = R.art(None, (0, 5, -7.5), (-4, 0, 0), nom="croix")
    R.boite(X, (0, 62, 0), (7, 132, 7), "bois_mort")
    R.boite(X, (0, 85, 0), (132, 7, 7), "bois_mort")
    for x in (-60, 60):
        R.boite(X, (x, 79, 1), (3, 10, 3), "bois_mort")
    for y in (81, 89):
        R.boite(X, (0, y, 4.5), (10, 2, 2), "uni", {"c": "#3a2a18"})
    for x, s in ((-52, 1), (-38, -1), (44, 1)):
        _corbeau_perche(R, X, (x, 88.5, 0), s)

    T = R.art(None, (0, 58, 0), (3, 0, 3), nom="torse")
    R.boite(T, (0, 14, 0), (16, 30, 9), "haillons")
    for k in range(4):
        R.boite(T, (0, 6 + k * 5, 4.8), (12 - k, 1.5, 1), "paille")
    R.boite(T, (2, 16, 5), (5, 7, 1), "uni", {"c": "#050305", "bruit": 2})
    R.boite(T, (0, -1, 0), (17, 3, 10), "uni", {"c": "#4b3a22"})
    for i, x in enumerate((-6, -3, 0, 2, 5, 7)):
        R.boite(T, (x, -4 - (i % 3), (i % 2) * 4 - 2), (1, 8 + (i % 3) * 2, 1), "paille")
    C = R.art(T, (0, 29, -4), (18, 0, 0), nom="cape")
    for nom, cx, rz in (("cape_g", -12, -8), ("cape_m", 0, 0), ("cape_d", 12, 8)):
        cb = R.art(C, (cx, 0, 0), (0, 0, rz), nom=nom)
        for j, dx in enumerate((-4, 0, 4)):
            R.boite(cb, (dx, -18 - ((j + cx // 4) % 3) * 3, 0), (4, 36 + ((j + cx // 4) % 3) * 6, 1), "haillons", PLUMES_HAILLONS)
        R.boite(cb, (0, -2, 1.5), (12, 6, 2), "plumes")
    for sx, cote in ((-1, "g"), (1, "d")):
        B = R.art(T, (sx * 8, 27, -3), (0, 0, sx * -82), nom="bras_" + cote)
        R.boite(B, (0, 20, 0), (4, 40, 4), "haillons")
        for k in range(3):
            R.boite(B, (0, 10 + k * 12, 0), (5, 2, 5), "uni", {"c": "#4b3a22"})
        AB = R.art(B, (0, 40, 0), (sx * 10, 0, sx * -118), nom="avbras_" + cote)
        R.boite(AB, (0, 14, 0), (3, 28, 3), "bois_mort")
        R.boite(AB, (0, 22, 1.8), (1, 8, 1), "paille")
        M = R.art(AB, (0, 28, 0), (0, 0, 0), nom="main_" + cote)
        M2 = R.art(M, (0, 12, 0), (35, 0, 0), nom="doigts_" + cote)
        for f in range(4):
            R.boite(M, ((f - 1.5) * 1.8, 6, 0), (1, 12, 1), "bois_mort")
            R.boite(M2, ((f - 1.5) * 1.8, 4, 0), (1, 8, 1), "bois_mort")

    H = R.art(T, (0, 31, 2), (-8, -6, 10), nom="tete")
    R.boite(H, (0, 3, 0), (4, 6, 4), "paille")
    R.boite(H, (0, 15, 0), (19, 20, 18), "toile", {"couture": .62})
    R.boite(H, (0, 6, 0), (21, 3, 20), "uni", {"c": "#4b3a22"})
    for ex in (-5, 5):
        R.boite(H, (ex, 18, 9.1), (5, 5, 0.5), "uni", {"c": "#070206", "bruit": 2})
        R.boite(H, (ex, 18, 9.4), (2, 2, 0.5), "uni", {"c": "#ff3a1a", "lueur": True, "bruit": 30})
    for k in range(7):
        R.boite(H, (-6 + k * 2, 10, 9.2), (1.4, 0.6, 0.4), "uni", {"c": "#1a0c08"})
        R.boite(H, (-6 + k * 2, 10, 9.3), (0.5, 3, 0.4), "uni", {"c": "#1a0c08"})
    R.boite(H, (3, 10, 9.4), (3, 2, 0.3), "uni", {"c": "#4a0606"})
    for k in range(12):
        a = k / 12 * math.pi * 2
        R.boite(H, (math.cos(a) * 10, 22, math.sin(a) * 9.5), (1, 6, 1), "paille")
    CH = R.art(H, (0, 25, 0), (0, 0, -8), nom="chapeau")
    HAT = {"pal": ["#17141a", "#1e1a22", "#0f0d12"]}
    R.boite(CH, (0, 0, 0), (34, 2, 32), "haillons", HAT)
    R.boite(CH, (0, 6, 0), (17, 10, 16), "haillons", HAT)
    CT = R.art(CH, (2, 13, 1), (0, 20, -25), nom="pointe")
    R.boite(CT, (0, 0, 0), (11, 6, 10), "haillons", HAT)
    R.boite(CT, (3, 4, 1), (5, 5, 5), "haillons", HAT)

    for sx, cote in ((-1, "g"), (1, "d")):
        J = R.art(None, (sx * 5, 60, 2), (0, 0, sx * 6), nom="cuisse_" + cote)
        R.boite(J, (0, -15, 0), (6, 30, 6), "haillons")
        Gm = R.art(J, (0, -30, 0), (0, 0, 0), nom="tibia_" + cote)
        R.boite(Gm, (0, -14, 0), (3, 28, 3), "bois_mort")
        R.boite(Gm, (0, -3, 0), (5, 4, 5), "haillons", {"trou": True})
        R.boite(Gm, (0.5, -7, 0.5), (4, 3, 4), "haillons", {"trou": True})
        P = R.art(Gm, (0, -28, 0), (0, 0, -sx * 6), nom="pied_" + cote)
        for f in range(3):
            R.boite(P, ((f - 1) * 1.8, -1, 4), (1, 1, 9), "bois_mort")
    return R


def _marche(i):
    s = 1 if i % 2 == 0 else -1
    return {"cuisse_g": {"r": (-24 * s, 0, 0)}, "tibia_g": {"r": (18 if s < 0 else 4, 0, 0)},
            "cuisse_d": {"r": (24 * s, 0, 0)}, "tibia_d": {"r": (18 if s > 0 else 4, 0, 0)},
            "torse": {"r": (4, 6 * s, -4 * s)}, "tete": {"r": (0, 0, 10 * s)}, "croix": {"r": (0, 4 * s, 3 * s)},
            "cape_g": {"r": (6, 0, 0)}, "cape_m": {"r": (8 + 4 * s, 0, 0)}, "cape_d": {"r": (6, 0, 0)},
            "avbras_g": {"r": (0, 0, 12 * s)}, "avbras_d": {"r": (0, 0, -12 * s)}, "racine": {"t": (0, 1.5, 0)}}


def _rien(noms):
    return {n: {"s": 0.001} for n in noms}


CORBEAU_ANIM = {
    "marche": {"boucle": True, "cles": [(12, _marche(0)), (4, {**_marche(0), "racine": {"t": (0, -1, 0)}}),
                                         (12, _marche(1)), (4, {**_marche(1), "racine": {"t": (0, -1, 0)}})]},
    "repos": {"boucle": True, "cles": [
        (20, {"torse": {"r": (5, 0, 0)}, "tete": {"r": (0, 0, 14)}, "cape_m": {"r": (6, 0, 0)}}),
        (20, {"torse": {"r": (2, 0, 0)}, "tete": {"r": (0, 0, 4)}, "cape_m": {"r": (2, 0, 0)}})]},
    # la tete se tord a 90 degres avant chaque attaque
    "torsion": {"boucle": False, "cles": [(6, {"tete": {"r": (0, 0, 60)}}), (4, {"tete": {"r": (0, 0, 92)}}),
                                          (10, {"tete": {"r": (0, 0, 95)}}), (6, {})]},
    # fauchage : il arme son buste en arriere, puis tourne sur lui-meme (4 quarts de tour)
    "fauchage": {"boucle": False, "cles": [
        (14, {"torse": {"r": (-14, -50, 0)}, "croix": {"r": (-10, -40, 0)}, "tete": {"r": (0, 0, 90)}}),
        (6, {"torse": {"r": (-16, -60, 0)}, "croix": {"r": (-12, -50, 0)}, "tete": {"r": (0, 0, 95)}}),
        (3, {"racine": {"r": (0, 90, 0)}, "torse": {"r": (10, 20, 0)}}),
        (3, {"racine": {"r": (0, 180, 0)}, "torse": {"r": (10, 20, 0)}}),
        (3, {"racine": {"r": (0, 270, 0)}, "torse": {"r": (10, 20, 0)}}),
        (3, {"racine": {"r": (0, 359, 0)}, "torse": {"r": (10, 20, 0)}}),
        (10, {}),
    ]},
    # nuee : la cage de paille s'ouvre, il se cambre
    "nuee": {"boucle": False, "cles": [
        (10, {"torse": {"r": (-20, 0, 0)}, "tete": {"r": (-30, 0, 0)}, "bras_g": {"r": (0, 0, -20)}, "bras_d": {"r": (0, 0, 20)}}),
        (16, {"torse": {"r": (-24, 0, 0), "s": 1.06}, "tete": {"r": (-40, 0, 0)}, "bras_g": {"r": (0, 0, -24)}, "bras_d": {"r": (0, 0, 24)}}),
        (10, {}),
    ]},
    # dispersion : il se defait piece par piece, de la tete vers les jambes
    "dispersion": {"boucle": False, "fige": True, "cles": [
        (6, {"tete": {"r": (0, 0, 80)}}),
        (5, {**_rien(["tete"])}),
        (5, {**_rien(["tete", "bras_g", "bras_d", "cape"])}),
        (5, {**_rien(["tete", "bras_g", "bras_d", "cape", "torse", "croix"])}),
        (5, {**_rien(["tete", "bras_g", "bras_d", "cape", "torse", "croix", "cuisse_g", "cuisse_d"])}),
    ]},
    "cache": {"boucle": False, "fige": True, "cles": [(1, {**_rien(["tete", "bras_g", "bras_d", "cape", "torse", "croix", "cuisse_g", "cuisse_d"])})]},
    "reforme": {"boucle": False, "cles": [
        (1, {**_rien(["tete", "bras_g", "bras_d", "cape", "torse", "croix", "cuisse_g", "cuisse_d"])}),
        (5, {**_rien(["tete", "bras_g", "bras_d", "cape", "torse", "croix"])}),
        (5, {**_rien(["tete", "bras_g", "bras_d", "cape"])}),
        (5, {**_rien(["tete"])}),
        (6, {"tete": {"r": (0, 0, 80)}}),
        (8, {}),
    ]},
    # crucifie (phase 3) : bras en croix plaques sur la traverse, tete pendante, pieds decolles
    "croix": {"boucle": True, "cles": [
        (20, {"racine": {"t": (0, 8, 0)}, "avbras_g": {"r": (0, 0, 118)}, "avbras_d": {"r": (0, 0, -118)},
              "tete": {"r": (30, 0, 20)}, "cuisse_g": {"r": (0, 0, 4)}, "cuisse_d": {"r": (0, 0, -4)}, "cape_m": {"r": (-8, 0, 0)}}),
        (20, {"racine": {"t": (0, 10, 0)}, "avbras_g": {"r": (0, 0, 114)}, "avbras_d": {"r": (0, 0, -114)},
              "tete": {"r": (26, 0, 14)}, "cuisse_g": {"r": (0, 0, 2)}, "cuisse_d": {"r": (0, 0, -2)}, "cape_m": {"r": (-4, 0, 0)}}),
    ]},
    # charge : penche en avant, bras tendus
    "charge": {"boucle": True, "cles": [
        (4, {**_marche(0), "torse": {"r": (30, 0, 0)}, "tete": {"r": (10, 0, 0)}, "croix": {"r": (24, 0, 0)},
             "avbras_g": {"r": (-60, 0, 30)}, "avbras_d": {"r": (-60, 0, -30)}}),
        (4, {**_marche(1), "torse": {"r": (30, 0, 0)}, "tete": {"r": (10, 0, 0)}, "croix": {"r": (24, 0, 0)},
             "avbras_g": {"r": (-60, 0, 30)}, "avbras_d": {"r": (-60, 0, -30)}}),
    ]},
    # sonne apres sa charge : a genoux, vulnerable
    "sonne": {"boucle": True, "cles": [
        (10, {"racine": {"t": (0, -14, 0)}, "cuisse_g": {"r": (-70, 0, 0)}, "tibia_g": {"r": (90, 0, 0)},
              "cuisse_d": {"r": (-70, 0, 0)}, "tibia_d": {"r": (90, 0, 0)}, "torse": {"r": (30, 0, 0)}, "tete": {"r": (40, 0, 20)}}),
        (10, {"racine": {"t": (0, -14, 0)}, "cuisse_g": {"r": (-70, 0, 0)}, "tibia_g": {"r": (90, 0, 0)},
              "cuisse_d": {"r": (-70, 0, 0)}, "tibia_d": {"r": (90, 0, 0)}, "torse": {"r": (34, 0, 0)}, "tete": {"r": (44, 0, -10)}}),
    ]},
    "apparition": {"boucle": False, "cles": [
        (1, {"racine": {"t": (0, -140, 0)}}),
        (40, {"racine": {"t": (0, -20, 0)}, "tete": {"r": (40, 0, 0)}}),
        (10, {"tete": {"r": (0, 0, 92)}}),
        (12, {}),
    ]},
    "mort": {"boucle": False, "fige": True, "cles": [
        (8, {"tete": {"r": (0, 0, 95)}, "torse": {"r": (-20, 0, 0)}}),
        (16, {"racine": {"t": (0, -20, 0)}, "torse": {"r": (60, 0, 0)}, "croix": {"r": (-40, 0, 0)},
              "cuisse_g": {"r": (-80, 0, 0)}, "cuisse_d": {"r": (-80, 0, 0)}}),
        (30, {**_rien(["tete", "bras_g", "bras_d", "cape", "torse", "croix", "cuisse_g", "cuisse_d"])}),
    ]},
}


# ================================================================================================ petits modeles
def corbeau_vol(haut):
    """Corbeau en vol, ailes hautes (haut=True) ou basses : deux modeles qu'on alterne pour le battement."""
    R = Rig("oiseau_" + ("a" if haut else "b"))
    o = R.racine
    R.boite(o, (0, 0, 0), (4, 4, 8), "plumes")
    R.boite(o, (0, 1.5, 5), (3.4, 3.4, 3.4), "plumes")
    R.boite(o, (0, 1, 7.6), (1.2, 1.2, 3), "uni", {"c": "#3a3a40"})
    R.boite(o, (0, 0.5, -6), (4, 1, 5), "plumes")
    d = 1 if haut else -1
    for sx in (-1, 1):
        R.boite(o, (sx * 6, 1 + 1.5 * d, -1), (8, 1, 6), "plumes")
        R.boite(o, (sx * 13, 1 + 4 * d, -2), (7, 0.8, 5), "plumes")
    for ex in (-1.75, 1.75):
        R.boite(o, (ex, 2.2, 5.6), (0.3, 0.8, 0.8), "uni", {"c": "#ff2a10", "lueur": True})
    return R


def livre_vol(ouvert):
    R = Rig("livre_" + ("a" if ouvert else "b"))
    o = R.racine
    h = 0 if ouvert else 3
    for sx in (-1, 1):
        R.boite(o, (sx * (6 - h), h, 0), (11 - h * 2, 1, 13), "cuir", {"pal": ["#5a1f1f", "#702828", "#3e1414"]})
        R.boite(o, (sx * (5.5 - h), 1 + h, 0), (9 - h * 2, 2, 11), "page", {"faces": ["tranche", "tranche", "page", "page", "tranche", "tranche"]})
    R.boite(o, (0, 0, 0), (2, 2, 13), "cuir", {"pal": ["#5a1f1f", "#702828"], "liseré": False})
    R.boite(o, (0, 3 + h, 0), (3, 1, 3), "uni", {"c": "#ff5a2a", "lueur": True})
    return R


def tentacule():
    R = Rig("tentacule")
    o = R.racine
    wd, x, y = 10, 0, 0
    for k in range(8):
        R.boite(o, (x, y + 5, 0), (wd, 10, wd), "pierre", PIERRE_ENCRE)
        if k % 2:
            R.boite(o, (x + wd / 2 + 0.3, y + 5, 0), (0.6, 5, 3), "runes", {"lueur": True})
        y += 10
        x += (1.5 if k < 4 else -1.0)
        wd = max(2.5, wd - 1.1)
    return R


def rune():
    R = Rig("rune")
    R.boite(R.racine, (0, 0, 0), (5, 5, 5), "runes", {"lueur": True, "fond": "#4a1a8a"})
    return R


def lune():
    R = Rig("lune")
    r0 = 30
    for y in range(-r0, r0, 4):
        w = 2 * math.sqrt(r0 * r0 - (y + 2) ** 2)
        R.boite(R.racine, (0, y + 2, 0), (max(4, round(w / 4) * 4), 4, 1), "uni", {"c": "#ff5040", "lueur": True, "bruit": 30})
    for x, y, w, h in ((-8, 8, 10, 6), (10, -5, 8, 8), (-2, -15, 12, 4)):
        R.boite(R.racine, (x, y, 0.6), (w, h, 0.4), "uni", {"c": "#c8301e", "lueur": True, "bruit": 20})
    return R


def livre_main():
    """Grimoire d'encre (recompense) : petit livre a oeil, tenu en main."""
    R = Rig("grimoire_encre")
    o = R.racine
    for sx in (-1, 1):
        R.boite(o, (sx * 3.5, 0, 0), (7, 1, 10), "cuir", {"liseré": False})
        R.boite(o, (sx * 3.3, 1, 0), (6, 1.5, 9), "page", {"faces": ["tranche", "tranche", "page", "page", "tranche", "tranche"]})
    R.boite(o, (0, 0.5, 5.2), (4, 3, 0.6), "oeil")
    return R



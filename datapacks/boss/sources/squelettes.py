"""Aides communes pour les squelettes humanoides (pack Boss et pack Horreur)."""
import math

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



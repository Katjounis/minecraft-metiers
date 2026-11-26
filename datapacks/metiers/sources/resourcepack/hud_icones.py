# Cœurs, gigots et armures dessinés à la main pour la DA pierre et laiton.
# Appelé par interface_details.py (fonction icones() -> {chemin sprite: Image}).
# Cœur : rubis taillé (facettes), même gabarit que vanilla. Gigot : gigot rôti avec papillote.
# Armure : plastron en laiton, arête centrale, ceinture rivetée.
from PIL import Image

CONTOUR = (30, 21, 16, 235)
VIDE = [(60, 51, 45), (50, 43, 38), (42, 36, 32)]

# ------------------------------------------------------------------ cœurs
COEUR = [
    ".........",
    "..lm.lm..",
    ".lhlmlmd.",
    ".llmmmmd.",
    ".dmmmmld.",
    "..dmmld..",
    "...dmd...",
    "....x....",
    ".........",
]
CREUX_HC = [(2, 2), (2, 3), (3, 3), (3, 4), (6, 2), (6, 3), (5, 3), (5, 4)]
RUBIS = {
    "": [(255, 222, 222), (244, 98, 104), (206, 36, 56), (148, 20, 44), (94, 10, 30)],
    "poisoned": [(222, 244, 176), (152, 192, 72), (110, 150, 42), (74, 104, 28), (46, 66, 18)],
    "withered": [(126, 118, 112), (74, 68, 66), (52, 48, 46), (36, 33, 32), (20, 18, 18)],
    "frozen": [(244, 252, 255), (172, 228, 248), (112, 190, 228), (72, 140, 192), (40, 92, 140)],
    "absorbing": [(255, 240, 170), (240, 202, 108), (210, 164, 72), (166, 120, 44), (114, 80, 26)],
    "vehicle": [(255, 216, 164), (240, 142, 72), (210, 98, 42), (150, 62, 26), (100, 36, 14)],
}
ROLE = {"h": 0, "l": 1, "m": 2, "d": 3, "x": 4}


def blanchi(c, t):
    return tuple(int(c[i] + (255 - c[i]) * t) for i in range(3))


def coeur(variante, demi, hardcore, clignote):
    im = Image.new("RGBA", (9, 9), (0, 0, 0, 0))
    px = im.load()
    R = RUBIS[variante]
    for y, ligne in enumerate(COEUR):
        for x, ch in enumerate(ligne):
            if ch == "." or (demi and x > 4):
                continue
            c = R[ROLE[ch]]
            if hardcore and (x, y) in CREUX_HC:
                c = R[4]
            if clignote:
                c = blanchi(c, .38)
            px[x, y] = c + (255,)
    return im


def coeur_vide(clignote, hardcore=False):
    im = Image.new("RGBA", (9, 9), (0, 0, 0, 0))
    px = im.load()
    masque = {(x, y) for y, l in enumerate(COEUR) for x, ch in enumerate(l) if ch != "."}
    for y in range(9):
        for x in range(9):
            if (x, y) in masque:
                c = VIDE[0] if y <= 2 else VIDE[1] if y <= 4 else VIDE[2]
                px[x, y] = c + (255,)
            elif any((x + dx, y + dy) in masque for dx in (-1, 0, 1) for dy in (-1, 0, 1) if abs(dx) + abs(dy) == 1):
                px[x, y] = ((236, 226, 210, 255) if clignote else (LAITON_SOMBRE + (255,) if hardcore else CONTOUR))
    return im


LAITON_SOMBRE = (118, 82, 28)

# ------------------------------------------------------------------ gigots
GIGOT = [
    ".........",
    "..lhl....",
    ".lhllm...",
    ".llmmmd..",
    ".lmmmdd..",
    "..mddd...",
    "....dbB..",
    "......pP.",
    ".........",
]
VIANDE = {"h": (255, 206, 146), "l": (214, 128, 68), "m": (176, 88, 44), "d": (120, 56, 28),
          "b": (238, 228, 204), "B": (186, 172, 146), "p": (255, 255, 255), "P": (206, 202, 196)}


def gigot(demi, faim):
    im = Image.new("RGBA", (9, 9), (0, 0, 0, 0))
    px = im.load()
    for y, ligne in enumerate(GIGOT):
        for x, ch in enumerate(ligne):
            if ch == "." or (demi and x + y < 7):
                continue
            c = VIANDE[ch]
            if faim:
                vert = (120, 148, 64) if ch in "hlmd" else (200, 214, 150)
                c = tuple(int(c[i] * .5 + vert[i] * .5) for i in range(3))
            px[x, y] = c + (255,)
    return im


def gigot_vide(faim):
    im = Image.new("RGBA", (9, 9), (0, 0, 0, 0))
    px = im.load()
    masque = {(x, y) for y, l in enumerate(GIGOT) for x, ch in enumerate(l) if ch != "."}
    for y in range(9):
        for x in range(9):
            if (x, y) in masque:
                c = VIDE[0] if x + y < 6 else VIDE[1] if x + y < 9 else VIDE[2]
                if faim:
                    c = (c[0] - 6, c[1] + 6, c[2] - 6)
                px[x, y] = c + (255,)
            elif any((x + dx, y + dy) in masque for dx in (-1, 0, 1) for dy in (-1, 0, 1) if abs(dx) + abs(dy) == 1):
                px[x, y] = CONTOUR
    return im


# ------------------------------------------------------------------ armures
PLASTRON = [
    ".oo...oo.",
    "orLo.oLro",
    "oLLLoLMMo",
    "oDLLHMMDo",
    ".oLLHMMo.",
    ".obbrbbo.",
    ".oLLHMDo.",
    ".oDDDDDo.",
    "..ooooo..",
]
LAITON = {"r": (255, 240, 170), "H": (255, 226, 140), "L": (236, 196, 104), "M": (206, 160, 70), "D": (160, 116, 42),
          "b": (118, 82, 28)}


def plastron(etat):
    im = Image.new("RGBA", (9, 9), (0, 0, 0, 0))
    px = im.load()
    for y, ligne in enumerate(PLASTRON):
        for x, ch in enumerate(ligne):
            if ch == ".":
                continue
            if ch == "o" or (etat == "half" and x == 4):
                px[x, y] = CONTOUR
                continue
            plein = etat == "full" or (etat == "half" and x < 4)
            if plein:
                c = LAITON[ch]
            else:
                c = VIDE[0] if y <= 2 else VIDE[1] if y <= 5 else VIDE[2]
                if ch == "b":
                    c = (40, 34, 30)
            px[x, y] = c + (255,)
    return im


def icones():
    out = {}
    for var in RUBIS:
        for hc in (False, True):
            if var == "vehicle" and hc:
                continue
            for demi in (False, True):
                for cl in (False, True):
                    if var == "vehicle" and cl:
                        continue
                    nom = "_".join(p for p in (var, "hardcore" if hc else "", "half" if demi else "full", "blinking" if cl else "") if p)
                    out[f"hud/heart/{nom}.png"] = coeur(var, demi, hc, cl)
    out["hud/heart/container.png"] = coeur_vide(False)
    out["hud/heart/container_blinking.png"] = coeur_vide(True)
    out["hud/heart/container_hardcore.png"] = coeur_vide(False, True)
    out["hud/heart/container_hardcore_blinking.png"] = coeur_vide(True)
    out["hud/heart/vehicle_container.png"] = coeur_vide(False)
    for faim in (False, True):
        s = "_hunger" if faim else ""
        out[f"hud/food_full{s}.png"] = gigot(False, faim)
        out[f"hud/food_half{s}.png"] = gigot(True, faim)
        out[f"hud/food_empty{s}.png"] = gigot_vide(faim)
    for etat in ("full", "half", "empty"):
        out[f"hud/armor_{etat}.png"] = plastron(etat)
    return out

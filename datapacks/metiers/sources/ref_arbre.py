# -*- coding: utf-8 -*-
# Arbre de compétences dessiné dans la page de chaque métier (25/11/2026).
# Police « metiers:arbre » du resource pack : un fond par métier (bloc du métier assombri, cadre doré), les 6 nœuds
# dans les 4 états (acquise, disponible, points manquants, bloquée) avec l'icône de la compétence et les cadres de
# l'écran des Progrès, et les 6 liens en deux états (gris, blanc quand les deux compétences sont acquises).
# Tout est posé par-dessus le fond avec des espaces négatifs : chaque calque revient à l'origine après lui.
# Exécuté depuis ref_menu.py (mêmes variables globales). Textures du jeu copiées dans sources/textures_arbre/.
from PIL import Image as _Img, ImageDraw as _Draw

_TA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures_arbre")
_RPF = os.path.join(ROOT, "..", "metiers_rp", "assets", "metiers")


def _tex(p):
    im = _Img.open(os.path.join(_TA, p + ".png")).convert("RGBA")
    return im.crop((0, 0, im.width, im.width)) if im.height > im.width else im   # 1re image d'une texture animée


# 26.0 (26/11/2026) : 18 nœuds sur 3 colonnes (branche gauche, tronc, branche droite) et 6 rangées de niveau
ARB_W, ARB_H = 260, 190   # 26/11/2026 : cadre de pierre noire de 12 px autour
ARB_COL = {"G": 50, "T": 130, "D": 210}
ARB_ROW = [27, 54, 81, 108, 135, 162]   # 26/11/2026 : resserré, la page tient sans défiler
ARB_P = {k: (ARB_COL["T"], ARB_ROW[k - 1]) for k in range(1, 7)}
ARB_P.update({k: (ARB_COL["G"], ARB_ROW[k - 7]) for k in range(7, 13)})
ARB_P.update({k: (ARB_COL["D"], ARB_ROW[k - 13]) for k in range(13, 19)})
ARB_LIENS = [(k, k + 1) for k in range(1, 6)] + [(1, 7)] + [(k, k + 1) for k in range(7, 12)] + [(1, 13)] + [(k, k + 1) for k in range(13, 18)]
ARB_FOND = {"b": "oak_planks", "f": "farmland_moist", "m": "deepslate", "c": "mossy_cobblestone", "p": "prismarine_bricks",
            "e": "hay_block_side", "n": "purpur_block", "x": "moss_block", "t": "emerald_block", "k": "bricks"}
ARB_IC = {
    "b": ["block/oak_log", "item/iron_axe", "block/oak_sapling", "block/azalea_leaves", "item/charcoal", "item/golden_apple"],
    "f": ["item/wheat", "item/wheat_seeds", "item/bread", "item/bone_meal", "item/golden_carrot", "block/hay_block_side"],
    "m": ["item/iron_pickaxe", "item/iron_ingot", "item/glow_berries", "item/diamond", "block/furnace_front", "item/heart_of_the_sea"],
    "c": ["item/iron_sword", "item/compass_00", "item/leather", "item/phantom_membrane", "item/bone", "item/netherite_sword"],
    "p": ["item/fishing_rod", "item/turtle_helmet", "item/cod", "item/prismarine_crystals", "item/nautilus_shell", "item/trident"],
    "e": ["item/shears", "item/glistering_melon_slice", "item/leather", "item/wheat", "item/egg", "item/saddle"],
    "n": ["item/enchanted_book", "item/experience_bottle", "item/lapis_lazuli", "item/ender_pearl", "item/blaze_rod", "item/nether_star"],
    "x": ["item/chainmail_boots", "item/sugar", "item/feather", "item/wind_charge", "item/spyglass", "item/map"],
    "t": ["item/emerald", "item/name_tag", "item/ink_sac", "item/goat_horn", "item/bundle", "block/emerald_block"],
    "k": ["item/stick", "item/iron_boots", "block/scaffolding_side", "item/clock_00", "block/bricks", "item/golden_pickaxe"]}
ARB_ETATS = ("acquise", "dispo", "points", "bloquee")
_ASC0 = 7                       # ascent du fond : le haut du dessin à 7 px au-dessus de la ligne de base
_prov, _code = [], [0xE800]
ARB_FICHIERS = []   # écrits à la fin par ref_arbre_ecrire.py : ref_batisseur.py vide build/metiers_rp entre-temps


def _car():
    c = chr(_code[0]); _code[0] += 1
    return c


# ---------------------------------------------------------------- espaces (avances positives et négatives)
_ESP = {}


def _esp(n):
    if n == 0:
        return ""
    if n not in _ESP:
        _ESP[n] = _car()
    return _ESP[n]



def _avance(im):
    """Avance d'un glyphe bitmap du jeu : dernière colonne non transparente + 1, plus 1 d'espacement."""
    bb = im.getbbox()
    return (bb[2] if bb else 0) + 1


def _glyphe(nom, im, top, car=None):
    """Enregistre un glyphe dont le coin haut gauche est à « top » px sous le haut du fond. Rend (caractère, avance)."""
    assert max(im.size) <= 240, nom
    ARB_FICHIERS.append((nom, im))
    c = car or _car()
    _prov.append({"type": "bitmap", "file": f"metiers:font/arbre/{nom}.png", "height": im.height, "ascent": _ASC0 - top, "chars": [c]})
    return c, _avance(im)


# ---------------------------------------------------------------- liens (gris / blanc), communs à tous les métiers
ARB_SEG = {}
for n, (a_, b_) in enumerate(ARB_LIENS, 1):
    (x1, y1), (x2, y2) = ARB_P[a_], ARB_P[b_]
    var = {}
    for etat, coul in (("gris", (110, 110, 110, 255)), ("blanc", (255, 255, 255, 255))):
        if y1 == y2:      # lien horizontal (racine vers une branche), entre les bords des cadres
            xa, xb = sorted((x1, x2))
            x0, ytop = xa + 13, y1 - 1
            im = _Img.new("RGBA", (xb - 13 - x0, 3))
            d = _Draw.Draw(im)
            d.rectangle([(0, 0), (im.width - 1, 2)], fill=(0, 0, 0, 255))
            d.line([(0, 1), (im.width - 1, 1)], fill=coul, width=1)
        else:             # lien vertical dans une colonne
            x0, ytop = x1 - 1, y1 + 13
            im = _Img.new("RGBA", (3, y2 - 13 - ytop))
            d = _Draw.Draw(im)
            d.rectangle([(0, 0), (2, im.height - 1)], fill=(0, 0, 0, 255))
            d.line([(1, 0), (1, im.height - 1)], fill=coul, width=1)
        var[etat] = _glyphe(f"lien_{n}_{etat}", im, ytop)
    assert var["gris"][1] == var["blanc"][1]
    ARB_SEG[n] = {"x": x0, "gris": var["gris"][0], "blanc": var["blanc"][0], "adv": var["gris"][1], "ab": (a_, b_)}

# ---------------------------------------------------------------- fond et nœuds de chaque métier
_CAD = {(t_, o): _tex(f"cadre/{t_}_frame_{'obtained' if o else 'unobtained'}").resize((26, 26), _Img.NEAREST)
        for t_ in ("task", "goal", "challenge") for o in (True, False)}
_PAST = {"dispo": (255, 255, 85, 255), "points": (255, 85, 85, 255)}
ARB = {}


def _gris(ic, alpha):
    g = ic.convert("LA").convert("RGBA")
    g.putalpha(ic.split()[3].point(lambda a: a * alpha // 10))
    return g


# 26.0 : fond en blocs mêlés par métier (bordure d'un bloc, intérieur tiré au hasard avec des poids, toujours le même tirage)
ARB_MIX = {
    "b": ("oak_log", [("oak_planks", 5), ("spruce_planks", 2), ("birch_planks", 1), ("stripped_oak_log", 1)]),
    "f": ("hay_block_side", [("farmland_moist", 4), ("dirt", 2), ("coarse_dirt", 1), ("rooted_dirt", 1)]),
    "m": ("deepslate_bricks", [("deepslate", 4), ("cobbled_deepslate", 2), ("tuff", 2), ("deepslate_tiles", 1)]),
    "c": ("stone_bricks", [("mossy_cobblestone", 3), ("cobblestone", 2), ("mossy_stone_bricks", 2), ("cracked_stone_bricks", 1)]),
    "p": ("dark_prismarine", [("prismarine_bricks", 3), ("prismarine", 3), ("dark_prismarine", 1)]),
    "e": ("stripped_spruce_log", [("hay_block_top", 3), ("packed_mud", 2), ("mud_bricks", 1), ("coarse_dirt", 1)]),
    "n": ("dark_oak_planks", [("bookshelf", 3), ("purpur_block", 2), ("end_stone_bricks", 1)]),
    "x": ("oak_log", [("moss_block", 3), ("podzol_top", 1), ("rooted_dirt", 1), ("mossy_cobblestone", 1)]),
    "t": ("terracotta", [("cut_sandstone", 3), ("chiseled_sandstone", 1), ("emerald_block", 1), ("gold_block", 1)]),
    "k": ("oak_planks", [("bricks", 3), ("stone_bricks", 2), ("terracotta", 1)])}


CADRE_E = 12   # épaisseur du cadre


def _fond_mixte(j, W=None, H=None, graine=None):
    """Blocs mêlés du métier (ARB_MIX), assombris, avec une ombre intérieure (le fond est en retrait du cadre)."""
    import random as _r
    W, H = W or ARB_W, H or ARB_H
    bord, mix = ARB_MIX[j] if isinstance(j, str) else j
    rnd = _r.Random(graine or ("arbre-" + str(j)))
    tir = [b for b, n in mix for _ in range(n)]
    tx = {b: _tex("block/" + b) for b in set(tir)}
    im = _Img.new("RGBA", (W, H))
    for x in range(0, W, 16):
        for y in range(0, H, 16):
            im.paste(tx[rnd.choice(tir)], (x, y))
    im.alpha_composite(_Img.new("RGBA", (W, H), (0, 0, 0, 110)))
    return cadre_noir(im)


def _biseau(im, x0, y0, x1, y1, teintes):
    d = _Draw.Draw(im)
    for o, c in enumerate(teintes):
        hi = tuple(min(255, int(v * 1.25)) for v in c) + (255,); lo = tuple(int(v * 0.7) for v in c) + (255,)
        d.line([(x0 + o, y0 + o), (x1 - o, y0 + o)], fill=hi); d.line([(x0 + o, y0 + o), (x0 + o, y1 - o)], fill=hi)
        d.line([(x0 + o, y1 - o), (x1 - o, y1 - o)], fill=lo); d.line([(x1 - o, y0 + o), (x1 - o, y1 - o)], fill=lo)


def cadre_noir(im):
    """26/11/2026 : cadre en relief, briques de pierre noire polie, coins en pierre noire dorée avec un clou d'or,
    filet d'or autour du fond et ombre portée vers l'intérieur."""
    W, H = im.size
    E = CADRE_E
    fond = im.crop((E, E, W - E, H - E))
    ombre = _Img.new("RGBA", fond.size)
    d = _Draw.Draw(ombre)
    for i in range(6):
        d.rectangle([(i, i), (fond.width - 1 - i, fond.height - 1 - i)], outline=(0, 0, 0, int(150 * (1 - i / 6))))
    fond.alpha_composite(ombre)
    out = _Img.new("RGBA", (W, H))
    br = _tex("block/polished_blackstone_bricks")
    for x in range(0, W, 16):
        out.paste(br, (x, 0)); out.paste(br, (x, H - 16))
    for y in range(0, H, 16):
        out.paste(br, (0, y)); out.paste(br, (W - 16, y))
    out.paste(fond, (E, E))
    _biseau(out, 0, 0, W - 1, H - 1, [(40, 36, 44), (70, 64, 78), (55, 50, 62)])
    d = _Draw.Draw(out)
    d.rectangle([(E - 3, E - 3), (W - E + 2, H - E + 2)], outline=(205, 155, 45, 255))
    d.rectangle([(E - 2, E - 2), (W - E + 1, H - E + 1)], outline=(110, 75, 20, 255))
    d.rectangle([(E - 1, E - 1), (W - E, H - E)], outline=(10, 8, 12, 255))
    gb = _tex("block/gilded_blackstone")
    for p in ((0, 0), (W - 16, 0), (0, H - 16), (W - 16, H - 16)):
        out.paste(gb, p)
        _biseau(out, p[0], p[1], p[0] + 15, p[1] + 15, [(60, 50, 40)])
    for cx, cy in ((7, 7), (W - 8, 7), (7, H - 8), (W - 8, H - 8)):
        d.ellipse([(cx - 3, cy - 3), (cx + 3, cy + 3)], fill=(255, 200, 60, 255), outline=(60, 40, 10, 255))
        d.point([(cx - 1, cy - 1)], fill=(255, 245, 200, 255))
    d.rectangle([(0, 0), (W - 1, H - 1)], outline=(0, 0, 0, 255))
    return out


def fond_glyphes(nom, im):
    """Glyphes de 240 px au plus posés bout à bout : (caractères, avance totale)."""
    W = im.width
    cf, af, x0 = "", 0, 0
    while x0 < W:
        x1 = min(W, x0 + 240)
        c_, a_ = _glyphe(f"{nom}_{x0}", im.crop((x0, 0, x1, im.height)), 0)
        cf += (_esp(-1) if cf else "") + c_
        af += a_ - (1 if x0 else 0)
        x0 = x1
    return cf, af


for j in jobs:
    fond = _fond_mixte(j)
    cf, af = fond_glyphes(f"fond_{j}", fond)
    nd = {}
    icones = ARB_IC[j] + ([ic for _n, _d, ic in NOUVELLES[j]] if j in NOUVELLES else [])
    for k in range(1, NB_SK[j] + 1):
        ic = _tex(icones[k - 1]).resize((16, 16), _Img.NEAREST)
        cadre = "challenge" if k in (12, 18) else ("goal" if k == 6 else "task")
        nd[k] = {}
        for e in ARB_ETATS:
            im = _CAD[(cadre, e == "acquise")].copy()
            # 26.0 : seule une compétence acquise garde ses couleurs ; les autres sont grisées
            icn = ic if e == "acquise" else _gris(ic, 8 if e == "dispo" else (7 if e == "points" else 4))
            im.alpha_composite(icn, (5, 5))
            if e in _PAST:
                dd = _Draw.Draw(im)
                dd.rectangle([(20, 1), (24, 5)], fill=_PAST[e], outline=(0, 0, 0, 255))
            # pixel presque invisible en dernière colonne : même avance (27 px) pour tous les états et tous les cadres
            im.putpixel((25, 13), (0, 0, 0, 3)) if im.getpixel((25, 13))[3] == 0 else None
            cx, cy = ARB_P[k]
            nd[k][e] = _glyphe(f"{j}_{k}_{e}", im, cy - 13)
        assert len({v[1] for v in nd[k].values()}) == 1
    ARB[j] = {"fond": cf, "adv": af, "noeuds": nd}

# ---------------------------------------------------------------- décors des menus (25/11/2026)
# Une scène encadrée d'or en tête des menus principaux : serveur (îles volantes), Métiers, Commerce, Compagnons,
# Bestiaire. 228 x 84 px, blocs du jeu dessinés à 8 px. Glyphes de la même police metiers:arbre.
DEC_W, DEC_H = 228, 84


def _teinte(im, c):
    o = im.copy(); px = o.load()
    for x in range(o.width):
        for y in range(o.height):
            r, g, b, a = px[x, y]; l = (r + g + b) // 3
            px[x, y] = (l * c[0] // 255, l * c[1] // 255, l * c[2] // 255, a)
    return o


def _b8(nom, tint=None):
    im = _tex("block/" + nom).resize((8, 8), _Img.NEAREST)
    return _teinte(im, tint) if tint else im


def _ciel(a, haut, bas):
    d = _Draw.Draw(a)
    for y in range(DEC_H):
        t = y / DEC_H
        d.line([(0, y), (DEC_W, y)], fill=tuple(int(haut[i] + (bas[i] - haut[i]) * t) for i in range(3)) + (255,))


def _nuages(a, liste, coul=(245, 245, 250, 255)):
    d = _Draw.Draw(a)
    for cx, cy, cw in liste:
        d.rectangle([(cx, cy), (cx + cw, cy + 5)], fill=coul)
        d.rectangle([(cx + 6, cy - 3), (cx + cw - 8, cy)], fill=coul)


def _sol(a, y0, bloc_haut, bloc_bas, x0=0, x1=DEC_W):
    for x in range(x0, x1, 8):
        a.alpha_composite(bloc_haut, (x, y0))
        for y in range(y0 + 8, DEC_H, 8):
            a.alpha_composite(bloc_bas, (x, y))


def _arbre_bloc(a, x, y, tronc, feuilles, haut=2):
    for i in range(haut):
        a.alpha_composite(tronc, (x, y - 8 * (i + 1)))
    top = y - 8 * haut
    for dx in (-8, 0, 8):
        a.alpha_composite(feuilles, (x + dx, top - 8))
    a.alpha_composite(feuilles, (x, top - 16))


def _cadre(a):
    d = _Draw.Draw(a)
    d.rectangle([(0, 0), (DEC_W - 1, DEC_H - 1)], outline=(0, 0, 0, 255), width=2)
    d.rectangle([(2, 2), (DEC_W - 3, DEC_H - 3)], outline=(170, 128, 40, 255), width=1)
    return a


def _icone(a, nom, x, y, taille=16):
    a.alpha_composite(_tex("item/" + nom).resize((taille, taille), _Img.NEAREST), (x, y))


HERBE = (120, 190, 80)
FEUIL = (90, 160, 60)
DECORS = {}
# serveur : ciel de fin de journée, deux îles volantes
a = _Img.new("RGBA", (DEC_W, DEC_H)); _ciel(a, (70, 110, 190), (220, 180, 150)); _nuages(a, [(30, 18, 34), (150, 12, 46), (200, 30, 28)])
for x0, y0, lg in ((18, 52, 7), (130, 44, 10)):
    for i in range(lg):
        a.alpha_composite(_b8("grass_block_side"), (x0 + i * 8, y0))
    for r, b in ((1, "dirt"), (2, "stone")):
        for i in range(r, lg - r):
            a.alpha_composite(_b8(b), (x0 + i * 8, y0 + r * 8))
_arbre_bloc(a, 162, 44, _b8("oak_log"), _b8("oak_leaves", FEUIL))
DECORS["serveur"] = _cadre(a)
# Métiers : forêt à gauche, falaise de pierre et minerais à droite
a = _Img.new("RGBA", (DEC_W, DEC_H)); _ciel(a, (90, 140, 210), (190, 215, 235)); _nuages(a, [(60, 10, 40), (170, 18, 30)])
_sol(a, 68, _b8("grass_block_side"), _b8("dirt"), 0, 120)
for x in (14, 46, 86):
    _arbre_bloc(a, x, 68, _b8("oak_log"), _b8("oak_leaves", FEUIL), 2 + (x % 2))
for x in range(120, DEC_W, 8):
    for y in range(36 + (x - 120) // 12 * 0, DEC_H, 8):
        b = "coal_ore" if (x * 7 + y * 3) % 23 == 0 else "iron_ore" if (x * 5 + y) % 31 == 0 else "diamond_ore" if (x + y * 7) % 59 == 0 else "stone"
        a.alpha_composite(_b8(b), (x, y))
for x in range(120, DEC_W, 8):
    a.alpha_composite(_b8("grass_block_side"), (x, 28))
DECORS["metiers"] = _cadre(a)
# Commerce : place de marché, étals à auvent rayé
a = _Img.new("RGBA", (DEC_W, DEC_H)); _ciel(a, (110, 160, 220), (230, 210, 170)); _nuages(a, [(20, 12, 36), (120, 8, 44)])
_sol(a, 76, _b8("grass_block_side"), _b8("dirt"))
for x0 in (14, 84, 154):
    for i in range(6):
        a.alpha_composite(_b8("red_wool" if i % 2 == 0 else "white_wool"), (x0 + i * 8, 36))
    for y in (44, 52, 60):
        a.alpha_composite(_b8("spruce_log"), (x0, y)); a.alpha_composite(_b8("spruce_log"), (x0 + 40, y))
    for i in range(6):
        a.alpha_composite(_b8("barrel_side"), (x0 + i * 8, 68))
    _icone(a, "emerald", x0 + 12, 52, 12); _icone(a, "iron_ingot", x0 + 26, 52, 12)
DECORS["commerce"] = _cadre(a)
# Compagnons : prairie au coucher du soleil, les objets des compagnons posés dans l'herbe
a = _Img.new("RGBA", (DEC_W, DEC_H)); _ciel(a, (240, 150, 90), (250, 210, 140))
d = _Draw.Draw(a); d.ellipse([(160, 30), (196, 66)], fill=(255, 230, 120, 255))
_sol(a, 66, _b8("grass_block_side"), _b8("dirt"))
_arbre_bloc(a, 30, 66, _b8("spruce_log"), _b8("spruce_leaves", (70, 120, 70)), 3)
for i, n in enumerate(("bone", "cod", "feather", "snowball", "lead")):
    _icone(a, n, 64 + i * 26, 48)
DECORS["compagnons"] = _cadre(a)
# Bestiaire : nuit, lune, forêt sombre, yeux rouges
a = _Img.new("RGBA", (DEC_W, DEC_H)); _ciel(a, (8, 10, 30), (30, 20, 50))
d = _Draw.Draw(a)
for i in range(40):
    d.point(((i * 53) % DEC_W, (i * 29) % 50), fill=(230, 230, 255, 255))
d.ellipse([(170, 10), (194, 34)], fill=(235, 235, 210, 255)); d.ellipse([(176, 12), (198, 32)], fill=(20, 16, 40, 255))
_sol(a, 70, _b8("grass_block_side", (60, 70, 60)), _b8("dirt", (70, 60, 60)))
for x in (10, 44, 80, 120, 150, 196):
    _arbre_bloc(a, x, 70, _b8("dark_oak_log", (90, 80, 90)), _b8("spruce_leaves", (40, 50, 50)), 3)
for x, y in ((66, 58), (106, 60), (138, 56)):
    d.rectangle([(x, y), (x + 1, y)], fill=(255, 40, 40, 255)); d.rectangle([(x + 4, y), (x + 5, y)], fill=(255, 40, 40, 255))
DECORS["bestiaire"] = _cadre(a)
# caractères fixes : les autres packs (Commerce, Compagnons, Horreur) les écrivent en dur
DECOR_CODE = {"serveur": 0xE7F0, "metiers": 0xE7F1, "commerce": 0xE7F2, "compagnons": 0xE7F3, "bestiaire": 0xE7F4}
DECOR_CAR = {n: _glyphe(f"decor_{n}", im, 0, chr(DECOR_CODE[n])) for n, im in DECORS.items()}


def decor_corps(nom):
    """Élément de corps de dialogue (SNBT) : la scène encadrée, puis les lignes vides qui lui laissent sa hauteur."""
    c, _ = DECOR_CAR[nom]
    return ('{type:"minecraft:plain_message",width:240,contents:[{text:"' + c + '",font:"metiers:arbre",color:"white",shadow_color:0},'
            '{text:"' + "\\n" * 9 + '"}]}')


def _q(t):
    return t.replace("\\", "\\\\").replace('"', '\\"')


_LARGF = {**{c: 2 for c in "i!,.:;|"}, **{c: 3 for c in "l'`"}, **{c: 4 for c in "It[] "}, **{c: 5 for c in "fk<>(){}*\""}}


def _larg(s, gras=True):
    return sum(_LARGF.get(c, 6) + (1 if gras else 0) for c in s)


def _liens(j):
    return [(n, s) for n, s in ARB_SEG.items() if max(s["ab"]) <= NB_SK[j]]


def arbre_texte(j):
    """Composants (SNBT) qui posent le fond puis chaque calque ; $(sN) et $(aK) sont remplis par la page.
    Chaque nœud porte son infobulle (nom, effet, coût, niveau, prérequis) et se clique pour acheter ou basculer."""
    A = ARB[j]
    F_ = 'font:"metiers:arbre",color:"white",shadow_color:0'
    t = A["fond"] + _esp(-A["adv"])
    for n, s in _liens(j):
        t += _esp(s["x"]) + f"$(s{n})" + _esp(-(s["x"] + s["adv"]))
    comps = ['{text:"' + _q(t) + '",' + F_ + '}']
    d = jobs[j]
    for k in range(1, NB_SK[j] + 1):
        x = ARB_P[k][0] - 13
        adv = A["noeuds"][k]["acquise"][1]
        nom, cout, req, desc = SKILLS[j][k - 1]
        rq = " + ".join(SKILLS[j][r - 1][0] for r in req) if req else "rien"
        bulle = (f'[{{text:"{_q(nom)}\\n",color:"gold",bold:true}},{{text:"{_q(desc)}\\n\\n",color:"white"}},'
                 f'{{text:"Coût : {cout} points · niveau {SKILL_LVL[k - 1]} · requiert : {_q(rq)}\\n",color:"gray"}},'
                 '{text:"Clic : acheter, ou activer/désactiver si acquise.",color:"dark_gray"}]')
        comps.append('{text:"' + _q(_esp(x)) + f'$(a{k})' + _q(_esp(-(x + adv))) + '",' + F_ +
                     f',click_event:{{action:"run_command",command:"trigger metiers set {TSK(d, k)}"}},'
                     f'hover_event:{{action:"show_text",value:{bulle}}}}}')
    comps.append('{text:"' + _q(_esp(A["adv"])) + '",' + F_ + '}')
    return comps


def arbre_legende(j):
    """Noms des branches centrés sous leur colonne (espaces de la police de l'arbre, texte en police normale)."""
    if j not in BRANCHES:
        return []
    F_ = 'font:"metiers:arbre",color:"white",shadow_color:0'
    out, cur = [], 0
    for col, nom, coul in (("G", BRANCHES[j][0], "green"), ("T", "Tronc", "gold"), ("D", BRANCHES[j][1], "red")):
        w_ = _larg(nom)
        x = ARB_COL[col] - w_ // 2
        out.append('{text:"' + _q(_esp(x - cur)) + '",' + F_ + '}')
        out.append(f'{{text:"{nom}",color:"{coul}",bold:true,font:"minecraft:default"}}')   # sinon hérite de la police de l'arbre
        cur = x + w_
    out.append('{text:"' + _q(_esp(ARB_W - cur)) + '",' + F_ + '}')   # même largeur que le dessin : même centrage
    return out


exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref_panneaux.py"), encoding="utf-8").read())
_ARB_TXT = {j: arbre_texte(j) for j in jobs}
_ARB_LEG = {j: arbre_legende(j) for j in jobs}
_prov.append({"type": "space", "advances": {c: n for n, c in _ESP.items()}})
ARB_FONT = {"providers": _prov}


def arbre_etats(j, sk_tag):
    """Lignes qui remplissent pg aK (état de chaque nœud) et pg sN (lien allumé ou non) d'après les couleurs déjà
    calculées (cK) et les compétences acquises."""
    L = []
    for k in range(1, NB_SK[j] + 1):
        n = ARB[j]["noeuds"][k]
        L += [f'data modify storage {NS}:pg a{k} set value "{n["bloquee"][0]}"',
              f'execute if data storage {NS}:pg {{c{k}:"yellow"}} run data modify storage {NS}:pg a{k} set value "{n["dispo"][0]}"',
              f'execute if data storage {NS}:pg {{c{k}:"red"}} run data modify storage {NS}:pg a{k} set value "{n["points"][0]}"',
              f'execute if entity @s[tag={sk_tag}{k}] run data modify storage {NS}:pg a{k} set value "{n["acquise"][0]}"']
    for n, s in _liens(j):
        a_, b_ = s["ab"]
        L += [f'data modify storage {NS}:pg s{n} set value "{s["gris"]}"',
              f'execute if entity @s[tag={sk_tag}{a_},tag={sk_tag}{b_}] run data modify storage {NS}:pg s{n} set value "{s["blanc"]}"']
    return L


def arbre_corps(j):
    """Élément de corps de dialogue (SNBT) : le dessin, des lignes vides pour lui laisser sa hauteur, puis les noms des branches."""
    return ('{type:"minecraft:plain_message",width:' + str(ARB_W + 20) + ',contents:[' + ",".join(_ARB_TXT[j]) + ','
            '{text:"' + "\\n" * 21 + '"}' + "".join("," + c for c in _ARB_LEG[j]) + ']}')

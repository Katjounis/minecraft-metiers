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


ARB_W, ARB_H = 228, 138
ARB_P = {1: (114, 22), 2: (52, 54), 3: (176, 54), 4: (52, 86), 5: (176, 86), 6: (114, 116)}
ARB_LIENS = [(1, 2), (1, 3), (2, 4), (3, 5), (4, 6), (5, 6)]
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
for n, (a, b) in enumerate(ARB_LIENS, 1):
    (x1, y1), (x2, y2) = ARB_P[a], ARB_P[b]
    my = (y1 + y2) // 2
    x0, xmax, ytop, ybot = min(x1, x2) - 1, max(x1, x2) + 1, y1 + 13, y2 - 13
    var = {}
    for etat, coul in (("gris", (110, 110, 110, 255)), ("blanc", (255, 255, 255, 255))):
        im = _Img.new("RGBA", (xmax - x0 + 1, ybot - ytop + 1))
        d = _Draw.Draw(im)
        pts = [(x1 - x0, 0), (x1 - x0, my - ytop), (x2 - x0, my - ytop), (x2 - x0, ybot - ytop)]
        for i in range(3):
            d.line([pts[i], pts[i + 1]], fill=(0, 0, 0, 255), width=3)
        for i in range(3):
            d.line([pts[i], pts[i + 1]], fill=coul, width=1)
        var[etat] = _glyphe(f"lien_{n}_{etat}", im, ytop)
    assert var["gris"][1] == var["blanc"][1]
    ARB_SEG[n] = {"x": x0, "gris": var["gris"][0], "blanc": var["blanc"][0], "adv": var["gris"][1]}

# ---------------------------------------------------------------- fond et nœuds de chaque métier
_CAD = {(t, o): _tex(f"cadre/{t}_frame_{'obtained' if o else 'unobtained'}").resize((26, 26), _Img.NEAREST)
        for t in ("task", "goal") for o in (True, False)}
_PAST = {"dispo": (255, 255, 85, 255), "points": (255, 85, 85, 255)}
ARB = {}
for j in jobs:
    bloc = _tex("block/" + ARB_FOND[j])
    fond = _Img.new("RGBA", (ARB_W, ARB_H))
    for x in range(0, ARB_W, 16):
        for y in range(0, ARB_H, 16):
            fond.paste(bloc, (x, y))
    fond.alpha_composite(_Img.new("RGBA", (ARB_W, ARB_H), (0, 0, 0, 105)))
    d = _Draw.Draw(fond)
    d.rectangle([(0, 0), (ARB_W - 1, ARB_H - 1)], outline=(0, 0, 0, 255), width=2)
    d.rectangle([(2, 2), (ARB_W - 3, ARB_H - 3)], outline=(170, 128, 40, 255), width=1)
    cf, af = _glyphe(f"fond_{j}", fond, 0)
    nd = {}
    for k in range(1, 7):
        ic = _tex(ARB_IC[j][k - 1]).resize((16, 16), _Img.NEAREST)
        nd[k] = {}
        for e in ARB_ETATS:
            im = _CAD[("goal" if k == 6 else "task", e == "acquise")].copy()
            icn = ic
            if e == "bloquee":
                g = ic.convert("LA").convert("RGBA")
                g.putalpha(ic.split()[3].point(lambda a: a * 6 // 10))
                icn = g
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


# ---------------------------------------------------------------- espaces (avances positives et négatives)
_ESP = {}


def _esp(n):
    if n == 0:
        return ""
    if n not in _ESP:
        _ESP[n] = _car()
    return _ESP[n]


def _q(t):
    return t.replace("\\", "\\\\").replace('"', '\\"')


def arbre_texte(j):
    """Composants (SNBT) qui posent le fond puis chaque calque ; $(sN) et $(aK) sont remplis par la page.
    25/11/2026 : chaque nœud porte son infobulle (nom, effet, coût, niveau) et se clique pour acheter ou basculer."""
    A = ARB[j]
    F_ = 'font:"metiers:arbre",color:"white",shadow_color:0'
    t = A["fond"] + _esp(-A["adv"])
    for n, s in ARB_SEG.items():
        t += _esp(s["x"]) + f"$(s{n})" + _esp(-(s["x"] + s["adv"]))
    comps = ['{text:"' + _q(t) + '",' + F_ + '}']
    d = jobs[j]
    for k in range(1, 7):
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


_ARB_TXT = {j: arbre_texte(j) for j in jobs}
_prov.append({"type": "space", "advances": {c: n for n, c in _ESP.items()}})
ARB_FONT = {"providers": _prov}


def arbre_etats(j, sk_tag):
    """Lignes qui remplissent pg aK (état de chaque nœud) et pg sN (lien allumé ou non) d'après les couleurs déjà
    calculées (cK) et les compétences acquises."""
    L = []
    for k in range(1, 7):
        n = ARB[j]["noeuds"][k]
        L += [f'data modify storage {NS}:pg a{k} set value "{n["bloquee"][0]}"',
              f'execute if data storage {NS}:pg {{c{k}:"yellow"}} run data modify storage {NS}:pg a{k} set value "{n["dispo"][0]}"',
              f'execute if data storage {NS}:pg {{c{k}:"red"}} run data modify storage {NS}:pg a{k} set value "{n["points"][0]}"',
              f'execute if entity @s[tag={sk_tag}{k}] run data modify storage {NS}:pg a{k} set value "{n["acquise"][0]}"']
    for n, (a, b) in enumerate(ARB_LIENS, 1):
        s = ARB_SEG[n]
        L += [f'data modify storage {NS}:pg s{n} set value "{s["gris"]}"',
              f'execute if entity @s[tag={sk_tag}{a},tag={sk_tag}{b}] run data modify storage {NS}:pg s{n} set value "{s["blanc"]}"']
    return L


def arbre_corps(j):
    """Élément de corps de dialogue (SNBT) : le dessin, puis des lignes vides pour lui laisser sa hauteur."""
    return ('{type:"minecraft:plain_message",width:240,contents:[' + ",".join(_ARB_TXT[j]) + ','
            '{text:"' + "\\n" * 15 + '"}]}')

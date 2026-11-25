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


def _glyphe(nom, im, top):
    """Enregistre un glyphe dont le coin haut gauche est à « top » px sous le haut du fond. Rend (caractère, avance)."""
    assert max(im.size) <= 240, nom
    ARB_FICHIERS.append((nom, im))
    c = _car()
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

# ---------------------------------------------------------------- espaces (avances positives et négatives)
_ESP = {}


def _esp(n):
    if n == 0:
        return ""
    if n not in _ESP:
        _ESP[n] = _car()
    return _ESP[n]


def arbre_texte(j):
    """Texte (police metiers:arbre) qui pose le fond puis chaque calque ; $(sN) et $(aK) sont remplis par la page."""
    A = ARB[j]
    t = A["fond"] + _esp(-A["adv"])
    for n, s in ARB_SEG.items():
        t += _esp(s["x"]) + f"$(s{n})" + _esp(-(s["x"] + s["adv"]))
    for k in range(1, 7):
        x = ARB_P[k][0] - 13
        adv = A["noeuds"][k]["acquise"][1]
        t += _esp(x) + f"$(a{k})" + _esp(-(x + adv))
    return t + _esp(A["adv"])


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
    txt = _ARB_TXT[j].replace("\\", "\\\\").replace('"', '\\"')
    return ('{type:"minecraft:plain_message",width:240,contents:[{text:"' + txt + '",font:"metiers:arbre",color:"white",shadow_color:0},'
            '{text:"' + "\\n" * 15 + '"}]}')

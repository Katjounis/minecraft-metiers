# -*- coding: utf-8 -*-
"""Pastilles des boutons de navigation (24/11/2026), communes aux 4 packs.

Chaque bouton dont le libellé commence par une icône du jeu (composant « object » atlas) suivie d'un texte coloré
voit son icône remplacée par une pastille dessinée : carré arrondi 18 x 18 en dégradé de la couleur du texte, liseré
sombre, reflet, et l'icône du jeu posée dessus avec une ombre. Une pastille par couple (icône, couleur), dans la police
<ns>:badges du resource pack du pack (fusionné par fusion_rp.py).

Appel, juste avant le zip du datapack :
    exec(open(.../labo/outils/badges.py).read()); appliquer(ROOT, NS, RP_ASSETS, exclure=lambda rel: ...)
"""
import json as _bj, os as _bo, re as _bre, urllib.request as _bu
from PIL import Image as _BI

_BADGES_FICHIER = _bo.path.abspath(_bo.path.join(_bo.path.dirname(_bo.path.abspath(__file__ if "__file__" in dir() else ".")), "badges.py")) \
    if "_BADGES_FICHIER" not in globals() else _BADGES_FICHIER

COULEURS_MC = {"black": (40, 40, 40), "dark_blue": (30, 40, 170), "dark_green": (20, 130, 40), "dark_aqua": (20, 140, 150),
               "dark_red": (160, 20, 20), "dark_purple": (130, 40, 170), "gold": (230, 160, 20), "gray": (150, 150, 155),
               "dark_gray": (85, 85, 90), "blue": (70, 90, 230), "green": (60, 190, 60), "aqua": (40, 200, 220),
               "red": (220, 60, 50), "light_purple": (220, 90, 220), "yellow": (235, 215, 50), "white": (205, 205, 210)}

_K = lambda k: f'"?{k}"?'   # clés SNBT avec ou sans guillemets (Horreur écrit du JSON)
_RE = _bre.compile(rf'({_K("label")}:\[(?:\{{{_K("text")}:""\}},)?)\{{{_K("object")}:"atlas",{_K("atlas")}:"minecraft:(items|blocks)",'
                   rf'{_K("sprite")}:"minecraft:([a-z0-9_/]+)"\}},(\{{{_K("text")}:"[^"]*",{_K("color")}:"(#[0-9A-Fa-f]{{6}}|[a-z_]+)")')


def _rgb(c):
    if c.startswith("#"):
        return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    return COULEURS_MC.get(c, (150, 150, 150))


def _texture(sprite, dossier):
    """Texture du jeu (26.1), mise en cache dans labo/outils/textures_cache/ (versionné)."""
    pth = _bo.path.join(dossier, sprite.replace("/", "__") + ".png")
    if not _bo.path.exists(pth):
        _bo.makedirs(dossier, exist_ok=True)
        url = f"https://raw.githubusercontent.com/InventivetalentDev/minecraft-assets/26.1/assets/minecraft/textures/{sprite}.png"
        with _bu.urlopen(url, timeout=20) as r:
            open(pth, "wb").write(r.read())
    im = _BI.open(pth).convert("RGBA")
    if im.height > im.width:   # texture animée : première image
        im = im.crop((0, 0, im.width, im.width))
    return im.resize((16, 16), _BI.NEAREST) if im.size != (16, 16) else im


def _pastille(sprite, couleur, dossier):
    W = 18
    haut = tuple(int(v * 0.8) for v in couleur)
    bas = tuple(int(v * 0.32) for v in couleur)
    b = _BI.new("RGBA", (W, W), (0, 0, 0, 0)); px = b.load()
    for y in range(W):
        f = y / (W - 1)
        col = tuple(int(haut[i] + (bas[i] - haut[i]) * f) for i in range(3))
        for x in range(W):
            coin = (x in (0, W - 1)) and (y in (0, W - 1))
            if coin:
                continue
            bord = x in (0, W - 1) or y in (0, W - 1)
            if bord:
                px[x, y] = (int(couleur[0] * 0.18), int(couleur[1] * 0.18), int(couleur[2] * 0.18), 255)
            elif y == 1 and 1 < x < W - 2:
                px[x, y] = tuple(min(255, v + 45) for v in col) + (255,)
            else:
                px[x, y] = col + (235,)
    ic = _texture(sprite, dossier)
    ombre = _BI.new("RGBA", (16, 16), (0, 0, 0, 0)); op = ombre.load(); ip = ic.load()
    for x in range(16):
        for y in range(16):
            if ip[x, y][3]:
                op[x, y] = (0, 0, 0, 110)
    b.alpha_composite(ombre, (2, 2)); b.alpha_composite(ic, (1, 1))
    return b


def appliquer(root, ns, rp_assets, exclure=lambda rel: False):
    """Remplace les icônes des boutons par des pastilles dans tous les .mcfunction de root ; dessine la police."""
    combos, n = {}, 0
    def sub(m):
        nonlocal n
        cle = (m.group(3), m.group(5))
        if cle not in combos:
            combos[cle] = chr(0xE600 + len(combos))
        n += 1
        return (m.group(1) + f'{{text:"{combos[cle]}",font:"{ns}:badges",color:"white",shadow_color:0}},' + m.group(4))
    for dp, _, fs in _bo.walk(root):
        for fn in fs:
            if not fn.endswith(".mcfunction"):
                continue
            p = _bo.path.join(dp, fn); rel = _bo.path.relpath(p, root).replace(_bo.sep, "/")
            if exclure(rel):
                continue
            t = open(p, encoding="utf-8").read()
            if "label" not in t:
                continue
            t2 = _RE.sub(sub, t)
            if t2 != t:
                open(p, "w", encoding="utf-8").write(t2)
    dossier = _bo.path.join(_bo.path.dirname(_bo.path.abspath(_BADGES_FICHIER)), "textures_cache")
    tex_dir = _bo.path.join(rp_assets, ns, "textures", "font", "badges")
    _bo.makedirs(tex_dir, exist_ok=True); _bo.makedirs(_bo.path.join(rp_assets, ns, "font"), exist_ok=True)
    provs = []
    for (sprite, coul), ch in sorted(combos.items(), key=lambda kv: kv[1]):
        k = ord(ch) - 0xE600
        _pastille(sprite, _rgb(coul), dossier).save(_bo.path.join(tex_dir, f"b{k}.png"))
        provs.append({"type": "bitmap", "file": f"{ns}:font/badges/b{k}.png", "height": 18, "ascent": 13, "chars": [ch]})
    _bj.dump({"providers": provs}, open(_bo.path.join(rp_assets, ns, "font", "badges.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"pastilles {ns} : {len(combos)} dessinées, {n} boutons")
    return combos

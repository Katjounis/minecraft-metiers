# -*- coding: utf-8 -*-
"""Boutons dessinés des 4 packs (24/11/2026, refait le soir même : bouton entier et non plus une pastille).

Chaque bouton de navigation dont le libellé est « icône du jeu + texte fixe coloré » reçoit une face dessinée qui couvre
l'intérieur exact du bouton (W - 6 x 14 px, le cadre du bouton fait 3 px d'interface) : fond dégradé dans la couleur du texte, motif de biais, grande icône en
filigrane à droite, l'icône nette à gauche sur un halo, liseré clair et coins coupés. Le texte reste écrit par le jeu
(accents, ombre), posé sur la face grâce à des espaces négatifs : [face][recul][texte][avance] fait exactement la
largeur de la face, donc le jeu centre le tout pile sur le bouton.

Les boutons de métier (texte variable : niveau, barre) prennent une face à part, avec le bloc du métier en fond
(face_manuelle, appelée par Métiers pendant sa génération).

Tout va dans la police <ns>:badges du resource pack du pack (fusionné par fusion_rp.py). Appel, avant le zip :
    _BADGES_FICHIER = ".../labo/outils/badges.py"; exec(open(_BADGES_FICHIER).read()); appliquer(ROOT, NS, RP_ASSETS, exclure)
"""
import json as _bj, os as _bo, re as _bre, random as _brd, urllib.request as _bu
from PIL import Image as _BI

_BDIR = _bo.path.dirname(_bo.path.abspath(_BADGES_FICHIER))
if "_FACES" not in globals():
    _FACES = {}          # clé -> (car, largeur, sprite icône, rgb, texture de fond ou None)

COULEURS_MC = {"black": (40, 40, 40), "dark_blue": (30, 40, 170), "dark_green": (20, 130, 40), "dark_aqua": (20, 140, 150),
               "dark_red": (170, 25, 25), "dark_purple": (130, 40, 170), "gold": (230, 160, 20), "gray": (150, 150, 155),
               "dark_gray": (85, 85, 90), "blue": (70, 90, 230), "green": (60, 190, 60), "aqua": (40, 200, 220),
               "red": (220, 60, 50), "light_purple": (220, 90, 220), "yellow": (235, 215, 50), "white": (190, 190, 200)}


def _rgb(c):
    if c.startswith("#"):
        return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    return COULEURS_MC.get(c, (150, 150, 150))


# ---------------------------------------------------------------- largeur du texte (police du jeu, ascii.png)
_ASC = _BI.open(_bo.path.join(_BDIR, "..", "..", "datapacks", "commerce", "sources", "textures_recette", "ascii.png")).convert("RGBA")
_BASE = str.maketrans("éèêëàâäîïôöûùüçÉÈÊÀÂÎÔÛÙÇœ", "eeeeaaaiioouuucEEEAAIOUUCo")
_SPEC = {" ": 4, "’": 2, "'": 2, "·": 2, "▶": 8, "◀": 8, "•": 4, "★": 8, "…": 8}


def _avance(ch):
    if ch in _SPEC:
        return _SPEC[ch]
    b = ch.translate(_BASE)
    o = ord(b)
    if o > 255:
        return 7
    cell = _ASC.crop(((o % 16) * 8, (o // 16) * 8, (o % 16) * 8 + 8, (o // 16) * 8 + 8))
    xs = [x for x in range(8) for y in range(8) if cell.getpixel((x, y))[3]]
    return (max(xs) + 2) if xs else 4


def blargeur(txt, gras=False):
    return sum(_avance(c) + (1 if gras and c != " " else 0) for c in txt)


def besp(n):
    """Espace de n px (négatif = recul), police <ns>:badges."""
    n = max(-400, min(400, int(n)))
    return chr(0xE800 + 400 + n)


# ---------------------------------------------------------------- textures du jeu (cache versionné)
def _texture(sprite):
    dossier = _bo.path.join(_BDIR, "textures_cache")
    pth = _bo.path.join(dossier, sprite.replace("/", "__") + ".png")
    if not _bo.path.exists(pth):
        _bo.makedirs(dossier, exist_ok=True)
        url = f"https://raw.githubusercontent.com/InventivetalentDev/minecraft-assets/26.1/assets/minecraft/textures/{sprite}.png"
        with _bu.urlopen(url, timeout=20) as r:
            open(pth, "wb").write(r.read())
    im = _BI.open(pth).convert("RGBA")
    if im.height > im.width:
        im = im.crop((0, 0, im.width, im.width))
    return im.resize((16, 16), _BI.NEAREST) if im.size != (16, 16) else im


# ---------------------------------------------------------------- dessin d'une face
def _face(W, sprite, coul, fond=None, graine=0):
    H = 14   # intérieur du bouton : le cadre (nine_slice, border 3) fait 3 px tout autour
    rg = _brd.Random(graine)
    im = _BI.new("RGBA", (W, H), (0, 0, 0, 0)); px = im.load()
    clair = tuple(min(255, int(v * 1.1 + 40)) for v in coul)
    if fond:   # bloc du thème, x2, assombri et teinté
        t = _texture(fond).resize((32, 32), _BI.NEAREST); tp = t.load()
    for y in range(H):
        for x in range(W):
            coin = False   # pas de cadre propre : la face se fond dans celui du bouton
            if coin:
                continue
            if fond:
                r, g, b, _ = tp[x % 32, (y + 7) % 32]
                k = 0.42 - 0.12 * y / H
                c = [r * k * 0.7 + coul[0] * 0.10, g * k * 0.7 + coul[1] * 0.10, b * k * 0.7 + coul[2] * 0.10]
            else:
                f = y / (H - 1)
                c = [v * (0.34 - 0.16 * f) for v in coul]
                if ((x + y) // 3) % 4 == 0:                       # motif de biais discret
                    c = [v + 6 for v in c]
                n = rg.randint(-2, 2); c = [v + n for v in c]
            # halo derrière l'icône
            d = ((x - 10) ** 2 + (y - 8) ** 2) ** 0.5
            if d < 11:
                a = (1 - d / 11) * 0.35
                c = [c[i] * (1 - a) + coul[i] * a for i in range(3)]
            if y == 0:
                c = [min(255, v + 0.30 * (clair[i] - v) + 14) for i, v in enumerate(c)]
            elif y == H - 1:
                c = [v * 0.65 for v in c]
            px[x, y] = tuple(max(0, min(255, int(v))) for v in c) + (255,)
    ic = _texture(sprite)
    # filigrane : grande icône à droite, coupée par le bord
    big = ic.resize((32, 32), _BI.NEAREST); bp = big.load()
    ox, oy = W - 28, -9
    for x in range(32):
        for y in range(32):
            X, Y = ox + x, oy + y
            if 0 <= X < W and 0 <= Y < H and bp[x, y][3]:
                r, g, b, a = px[X, Y]
                s = bp[x, y]; al = 0.16
                px[X, Y] = (int(r * (1 - al) + s[0] * al), int(g * (1 - al) + s[1] * al), int(b * (1 - al) + s[2] * al), 255)
    # icône nette avec ombre
    ombre = _BI.new("RGBA", (16, 16), (0, 0, 0, 0)); op = ombre.load(); ip = ic.load()
    for x in range(16):
        for y in range(16):
            if ip[x, y][3]:
                op[x, y] = (0, 0, 0, 140)
    # icône 16 px dans une face de 14 : on rogne 1 px en haut et en bas (les icônes du jeu ont presque toujours ces lignes vides)
    im.alpha_composite(ombre.crop((0, 1, 16, 15)), (3, 1)); im.alpha_composite(ic.crop((0, 1, 16, 15)), (2, 0))
    return im


def face_manuelle(cle, W, sprite, couleur, fond=None):
    """Réserve une face (dessinée par appliquer) et renvoie son caractère."""
    if cle not in _FACES:
        _FACES[cle] = (chr(0xE000 + len(_FACES)), W - 6, sprite, _rgb(couleur) if isinstance(couleur, str) else couleur, fond)
    return _FACES[cle][0]


# Largeur totale du libellé = 0 (24/11/2026 23 h) : un libellé plus large que le bouton moins 4 px défile de gauche
# à droite, et la mesure du jeu ne colle jamais au pixel près. À largeur nulle, le jeu place le début au centre du
# bouton et ne fait jamais défiler : on recule d'une demi-face, on pose la face, on revient poser le texte, puis on
# revient au centre.
def _sequence(W, tw):
    F = W - 6
    x0 = 22 + max(0, (F - 26 - tw) // 2)
    return F, [besp(-(W // 2 - 3)), None, besp(-F - 1 + x0), "TEXTE", besp(W // 2 - 3 - x0 - tw)]


def libelle(ns, cle, W, sprite, couleur, composants, tw, fond=None):
    """Libellé complet (SNBT) : face calée dans le cadre du bouton, texte posé dessus, largeur totale nulle."""
    ch = face_manuelle(cle, W, sprite, couleur, fond)
    F, q = _sequence(W, tw)
    return ('[{text:""},' + f'{{text:"{q[0]}",font:"{ns}:badges"}},'
            + f'{{text:"{ch}",font:"{ns}:badges",color:"white",shadow_color:0}},'
            + f'{{text:"{q[2]}",font:"{ns}:badges"}},' + ",".join(composants)
            + f',{{text:"{q[4]}",font:"{ns}:badges"}}]')


def libelle_json(ns, cle, W, sprite, couleur, composants, tw, fond=None):
    """Même chose en JSON (dialogues fixes comme le menu G) : composants = liste de dicts."""
    ch = face_manuelle(cle, W, sprite, couleur, fond)
    F, q = _sequence(W, tw)
    return ([{"text": ""}, {"text": q[0], "font": f"{ns}:badges"}, {"text": ch, "font": f"{ns}:badges", "color": "white", "shadow_color": 0},
             {"text": q[2], "font": f"{ns}:badges"}] + composants + [{"text": q[4], "font": f"{ns}:badges"}])


POINT = chr(0xE7FF)      # pastille rouge de largeur fixe (6 px), pour les boutons à texte variable
POINT_L = 6


# ---------------------------------------------------------------- application automatique
_K = lambda k: f'"?{k}"?'
_RE = _bre.compile(rf'({_K("label")}:)\[(?:\{{{_K("text")}:""\}},)?\{{{_K("object")}:"atlas",{_K("atlas")}:"minecraft:(?:items|blocks)",'
                   rf'{_K("sprite")}:"minecraft:([a-z0-9_/]+)"\}},(\{{{_K("text")}:"([^"$]*)",{_K("color")}:"(#[0-9A-Fa-f]{{6}}|[a-z_]+)"'
                   rf'(?:,{_K("bold")}:(true|false|1b|0b))?[^{{}}\]]*\}})\],({_K("width")}:(\d+))')


def appliquer(root, ns, rp_assets, exclure=lambda rel: False):
    n = 0
    def sub(m):
        nonlocal n
        etiq, sprite, comp, texte, coul, gras, wtxt, W = m.groups()
        W = int(W); txt_ = texte.strip()
        gr = gras in ("true", "1b")
        comp = comp.replace(f'"{texte}"', f'"{txt_}"', 1)
        tw = blargeur(txt_, gr)
        if tw > W - 30:          # trop long pour la face : on laisse le bouton tel quel
            return m.group(0)
        n += 1
        return etiq + libelle(ns, (sprite, coul, W), W, sprite, coul, [comp], tw) + "," + wtxt
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
    tex_dir = _bo.path.join(rp_assets, ns, "textures", "font", "boutons")
    _bo.makedirs(tex_dir, exist_ok=True); _bo.makedirs(_bo.path.join(rp_assets, ns, "font"), exist_ok=True)
    provs = [{"type": "space", "advances": {chr(0xE800 + 400 + k): k for k in range(-400, 401)}}]
    pt = _BI.new("RGBA", (5, 5), (0, 0, 0, 0)); pp = pt.load()
    for x_ in range(5):
        for y_ in range(5):
            if (x_ - 2) ** 2 + (y_ - 2) ** 2 <= 5:
                pp[x_, y_] = (255, 70, 70, 255) if (x_, y_) != (1, 1) else (255, 170, 170, 255)
    pt.save(_bo.path.join(tex_dir, "point.png"))
    provs.append({"type": "bitmap", "file": f"{ns}:font/boutons/point.png", "height": 5, "ascent": 5, "chars": [POINT]})
    for cle, (ch, F, sprite, rgb, fond) in sorted(_FACES.items(), key=lambda kv: kv[1][0]):
        k = ord(ch) - 0xE000
        _face(F, sprite, rgb, fond, graine=k).save(_bo.path.join(tex_dir, f"f{k}.png"))
        provs.append({"type": "bitmap", "file": f"{ns}:font/boutons/f{k}.png", "height": 14, "ascent": 10, "chars": [ch]})
    _bj.dump({"providers": provs}, open(_bo.path.join(rp_assets, ns, "font", "badges.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"boutons {ns} : {len(_FACES)} faces dessinées, {n} boutons automatiques")

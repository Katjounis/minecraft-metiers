# Détails de l'interface « Forge » : à lancer APRÈS interface_finition.py et AVANT interface_animations.py.
# Redessine dans la DA pierre et laiton ce qui restait en simple recoloration :
#   - cœurs en rubis taillé (toutes variantes), gigots rôtis à papillote, plastrons en laiton (voir hud_icones.py) ;
#   - infobulles : fond pierre sombre, cadre en laiton avec coins rivetés ;
#   - onglets, cases à cocher, curseurs, ascenseurs ;
#   - boutons des interfaces (tailleur de pierre, métier à tisser, balise, livre de recettes),
#     lignes de la table d'enchantement, flèche d'échange du villageois.
# Usage : python3 interface_details.py metiers_resourcepack.zip <dossier gui/sprites vanilla>
import io, os, sys, zipfile, colorsys
from PIL import Image
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from palette import *   # deepslate et cuivre (palette.py)

ZIP, VAN = sys.argv[1], sys.argv[2]
GUI = "assets/minecraft/textures/gui/sprites/"
BAY = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
CONTOUR = (34, 24, 18)


def tramage(rampe, v, x, y):
    i = int(v + (BAY[y % 4][x % 4] + .5) / 16)
    return rampe[max(0, min(len(rampe) - 1, i))]


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def neuf(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return im, im.load()


# ------------------------------------------------------------------ icônes du HUD : silhouettes vanilla, nouvelle matière
def matiere(c, nom):
    r, g, b = c
    if max(c) < 24:
        return CONTOUR
    if max(c) - min(c) < (16 if "armor" in nom else 8):  # gris
        v = max(c)
        if "armor" in nom and v > 70:  # plaques d'armure en laiton
            t = (v - 100) / 130
            return LAITON[4] if t < .1 else LAITON[3] if t < .55 else LAITON[2] if t < .85 else LAITON[0]
        if v < 70:  # fond des conteneurs vides
            return (58, 50, 44) if v > 50 else (48, 41, 36)
        return mix((r, g, b), (90, 80, 72), .25)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    h = (h + .985) % 1 if (h < .05 or h > .95) else h  # rouges un peu plus chauds
    s = min(1, s * 1.05)
    rr, gg, bb = colorsys.hsv_to_rgb(h, s, v * .96)
    return (int(rr * 255), int(gg * 255), int(bb * 255))


def icone(im, nom):
    im = im.convert("RGBA")
    w, h = im.size
    src = im.load()
    out, px = neuf(w, h)
    ys = [y for y in range(h) for x in range(w) if src[x, y][3] and max(src[x, y][:3]) >= 24]
    ya, yb = (min(ys), max(ys)) if ys else (0, h - 1)
    for y in range(h):
        for x in range(w):
            r, g, b, a = src[x, y]
            if not a:
                continue
            c = matiere((r, g, b), nom)
            vif = max(r, g, b) > 70 and max(r, g, b) - min(r, g, b) > 30
            if c != CONTOUR and vif:
                if min(r, g, b) > 170:  # reflet vanilla : crème chaud
                    c = (255, 236, 220)
                else:
                    # modelé : haut éclairé, bas dans l'ombre
                    t = (y - ya) / max(1, yb - ya)
                    k = 1.14 - .5 * t
                    c = tuple(max(0, min(255, int(v * k))) for v in c)
            px[x, y] = c + (a,)
    return out


# ------------------------------------------------------------------ infobulles
def infobulle_fond():
    im, px = neuf(100, 100)
    for y in range(8, 92):
        for x in range(8, 92):
            if (x in (8, 91)) and (y in (8, 91)):
                continue
            t = (y - 8) / 83
            c = tramage([(34, 28, 24), (28, 23, 20), (22, 18, 16)], .3 + t * 2.2, x, y)
            px[x, y] = c + (242,)
    return im


def infobulle_cadre():
    im, px = neuf(100, 100)
    a, b = 9, 90
    for i in range(a, b + 1):
        for (x, y, c) in ((i, a, LAITON[2]), (i, b, LAITON[4]), (a, i, LAITON[3]), (b, i, LAITON[3])):
            px[x, y] = c + (255,)
    for i in range(a + 2, b - 1):
        px[i, a + 1] = LAITON[4] + (120,)
    for (cx, cy) in ((a, a), (b - 1, a), (a, b - 1), (b - 1, b - 1)):
        for j in range(2):
            for i in range(2):
                px[cx + i, cy + j] = (LAITON[0] if (i, j) == (0, 0) else LAITON[1]) + (255,)
    return im


# ------------------------------------------------------------------ widgets
def case_a_cocher(coche, survol):
    im, px = neuf(20, 20)
    for y in range(20):
        for x in range(20):
            d = min(x, y, 19 - x, 19 - y)
            hg = min(x, y) == d
            if d == 0:
                c = SOMBRE
            elif d == 1:
                c = (LAITON[1] if hg else LAITON[3]) if survol else (LAITON[2] if hg else LAITON[4])
            elif d == 2:
                c = (18, 15, 13) if hg else CASE[0]
            else:
                c = tramage(CASE, 2.6 - (y / 20) * 2.2, x, y)
            px[x, y] = c + (255,)
    if coche:
        pts = [(5, 10), (6, 11), (7, 12), (8, 13), (9, 12), (10, 11), (11, 10), (12, 9), (13, 8), (14, 7), (15, 6)]
        for (x, y) in pts:
            for dy in (0, 1):
                px[x + 1, y + dy + 1] = SOMBRE + (255,)
        for (x, y) in pts:
            px[x, y] = (LAITON[0] if survol else LAITON[1]) + (255,)
            px[x, y + 1] = LAITON[2] + (255,)
    return im


def glissiere(survol):
    im, px = neuf(200, 20)
    for y in range(20):
        for x in range(200):
            d = min(x, y, 199 - x, 19 - y)
            if d == 0:
                c = LAITON[3] if survol else SOMBRE
            elif y == 1:
                c = (16, 13, 11)
            else:
                c = tramage(CASE, 2.8 - (y / 20) * 2.4, x, y)
                if y in (9, 10) and 4 <= x <= 195:
                    c = (24, 20, 17) if y == 9 else (66, 57, 50)
            px[x, y] = c + (255,)
    return im


def poignee(survol):
    im, px = neuf(8, 20)
    L = [mix(c, (255, 255, 255), .18) for c in LAITON] if survol else LAITON
    for y in range(20):
        for x in range(8):
            d = min(x, y, 7 - x, 19 - y)
            if d == 0:
                c = SOMBRE
            elif d == 1:
                c = L[0] if min(x, y) == 1 else L[4]
            else:
                c = L[1] if x < 4 else L[2]
                if y in (8, 10, 12) and 2 <= x <= 5:
                    c = L[4]
            px[x, y] = c + (255,)
    return im


def ascenseur(fond):
    im, px = neuf(6, 32)
    for y in range(32):
        for x in range(6):
            d = min(x, y, 5 - x, 31 - y)
            if fond:
                c = SOMBRE if d == 0 else (22, 18, 16)
            elif d == 0:
                c = SOMBRE
            else:
                c = LAITON[1] if x < 3 else LAITON[3]
                if x == 1:
                    c = LAITON[0]
                if y in (13, 15, 17) and 1 <= x <= 4:
                    c = LAITON[4]
            px[x, y] = c + (255,)
    return im


def onglet(selec, survol):
    im, px = neuf(130, 24)
    haut = 0 if selec else 4
    for y in range(haut, 24):
        for x in range(130):
            if x in (0, 129) or y == haut:
                c = SOMBRE
            elif x in (1, 128) or y == haut + 1:
                c = (LAITON[1] if survol else LAITON[2]) if (selec or survol) else LAITON[4]
            else:
                rampe = PIERRE if selec else PIERRE[2:] + [(68, 60, 52), (58, 51, 45)]
                c = tramage(rampe, 1.6 + ((y - haut) / 24) * 2.2, x, y)
            px[x, y] = c + (255,)
    return im


def plaque(w, h, etat, teinte=None):
    """Petit bouton d'interface : normal, highlighted, selected, disabled."""
    im, px = neuf(w, h)
    rampe = {"normal": PIERRE, "highlighted": PIERRE, "selected": [(84, 74, 64), (74, 65, 56), (64, 56, 49), (56, 49, 43), (48, 42, 37)],
             "disabled": [(78, 74, 70), (70, 66, 62), (62, 59, 56), (54, 52, 49)]}[etat]
    for y in range(h):
        for x in range(w):
            d = min(x, y, w - 1 - x, h - 1 - y)
            hg = min(x, y) == d
            if d == 0:
                c = SOMBRE
            elif d == 1:
                if etat == "highlighted":
                    c = LAITON[0] if hg else LAITON[2]
                elif etat == "selected":
                    c = LAITON[3] if hg else LAITON[1]
                elif etat == "disabled":
                    c = (90, 84, 76) if hg else (46, 43, 40)
                else:
                    c = LAITON[2] if hg else LAITON[4]
            else:
                c = tramage(rampe, 1.0 + (y / h) * 2.2 + (.6 if etat == "normal" else 0), x, y)
            if teinte and d > 1:
                c = mix(c, teinte, .35)
            px[x, y] = c + (255,)
    return im


def ligne_enchant(etat):
    w, h = 108, 19
    im, px = neuf(w, h)
    fond = {"normal": [(214, 198, 168), (204, 186, 154), (192, 174, 142), (180, 162, 130)],
            "highlighted": [(116, 88, 70), (104, 78, 62), (92, 68, 54), (80, 58, 46)],
            "disabled": [(64, 56, 50), (58, 51, 45), (52, 46, 41), (46, 41, 37)]}[etat]
    for y in range(h):
        for x in range(w):
            d = min(x, y, w - 1 - x, h - 1 - y)
            hg = min(x, y) == d
            if d == 0:
                c = SOMBRE
            elif d == 1:
                if etat == "highlighted":
                    c = LAITON[0] if hg else LAITON[2]
                elif etat == "disabled":
                    c = (82, 74, 66) if hg else (40, 36, 32)
                else:
                    c = LAITON[2] if hg else LAITON[3]
            else:
                c = tramage(fond, .4 + (y / h) * 2.6, x, y)
            px[x, y] = c + (255,)
    return im


def fleche_echange():
    im, px = neuf(10, 9)
    forme = ["..........", ".....#....", ".....##...", "########..", "#########.", "########..", ".....##...", ".....#....", ".........."]
    for y, l in enumerate(forme):
        for x, ch in enumerate(l):
            if ch == "#":
                px[x, y] = (LAITON[0] if y < 3 else LAITON[1] if y < 5 else LAITON[2]) + (255,)
    src = im.copy().load()
    for y in range(9):
        for x in range(10):
            if src[x, y][3] and (x + 1 >= 10 or y + 1 >= 9 or not src[x + 1, y][3] or not src[x, y + 1][3]):
                px[x, y] = LAITON[3] + (255,)
    return im


# ------------------------------------------------------------------ écriture
zin = zipfile.ZipFile(ZIP)
fichiers = {n: zin.read(n) for n in zin.namelist()}
zin.close()
sortie = {}


def png(nom, im):
    b = io.BytesIO()
    im.save(b, "PNG")
    sortie[GUI + nom] = b.getvalue()


def copie_meta(nom):
    src = os.path.join(VAN, nom + ".mcmeta")
    if os.path.exists(src) and GUI + nom + ".mcmeta" not in fichiers:
        sortie[GUI + nom + ".mcmeta"] = open(src, "rb").read()


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hud_icones import icones  # cœurs rubis, gigots, plastrons en laiton dessinés à la main
for nom, im in icones().items():
    png(nom, im)

png("tooltip/background.png", infobulle_fond())
png("tooltip/frame.png", infobulle_cadre())
for coche in (False, True):
    for survol in (False, True):
        png("widget/checkbox" + ("_selected" if coche else "") + ("_highlighted" if survol else "") + ".png", case_a_cocher(coche, survol))
png("widget/slider.png", glissiere(False))
png("widget/slider_highlighted.png", glissiere(True))
png("widget/slider_handle.png", poignee(False))
png("widget/slider_handle_highlighted.png", poignee(True))
png("widget/scroller.png", ascenseur(False))
png("widget/scroller_background.png", ascenseur(True))
for selec in (False, True):
    for survol in (False, True):
        png("widget/tab" + ("_selected" if selec else "") + ("_highlighted" if survol else "") + ".png", onglet(selec, survol))

for base, (w, h) in (("container/stonecutter/recipe", (16, 18)), ("container/loom/pattern", (14, 14))):
    png(base + ".png", plaque(w, h, "normal"))
    png(base + "_highlighted.png", plaque(w, h, "highlighted"))
    png(base + "_selected.png", plaque(w, h, "selected"))
for etat in ("normal", "highlighted", "selected", "disabled"):
    png("container/beacon/button" + ("" if etat == "normal" else "_" + etat) + ".png", plaque(22, 22, etat))
png("recipe_book/slot_craftable.png", plaque(25, 25, "normal"))
png("recipe_book/slot_many_craftable.png", plaque(25, 25, "normal"))
png("recipe_book/slot_uncraftable.png", plaque(25, 25, "normal", (170, 50, 40)))
png("recipe_book/slot_many_uncraftable.png", plaque(25, 25, "normal", (170, 50, 40)))
for etat in ("normal", "highlighted", "disabled"):
    png("container/enchanting_table/enchantment_slot" + ("" if etat == "normal" else "_" + etat) + ".png", ligne_enchant(etat))
png("container/villager/trade_arrow.png", fleche_echange())

for n in list(sortie):
    copie_meta(n[len(GUI):])
fichiers.update(sortie)
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for n in sorted(fichiers):
        zi = zipfile.ZipInfo(n, date_time=(2026, 1, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, fichiers[n])
open(ZIP, "wb").write(buf.getvalue())
print(len(sortie), "sprites de détail écrits")

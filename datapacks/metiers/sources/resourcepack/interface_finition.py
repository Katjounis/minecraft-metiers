# Finition de l'interface « Forge » : à lancer APRÈS interface_forge.py, directement sur le resource pack.
# Garde la DA pierre + or et les dispositions vanilla au pixel près, et ajoute :
#   - un vrai appareillage de briques ombrées sur la pierre des panneaux ;
#   - des cases creusées (dégradé sombre) ;
#   - une niche en dégradé à la place des grands aplats noirs (vitrine du joueur, etc.) ;
#   - des boutons pierre sombre + laiton, une barre d'action et une sélection en laiton, des bossbars à embouts en laiton.
# Usage : python3 interface_finition.py metiers_resourcepack.zip
import io, sys, zipfile, random
from PIL import Image
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from palette import *   # deepslate et cuivre (palette.py)

ZIP = sys.argv[1]
GUI = "assets/minecraft/textures/gui/"
BAY = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]



def tramage(rampe, v, x, y):
    i = int(v + (BAY[y % 4][x % 4] + .5) / 16)
    return rampe[max(0, min(len(rampe) - 1, i))]


def proche(c, ref, tol):
    return abs(c[0] - ref[0]) <= tol and abs(c[1] - ref[1]) <= tol and abs(c[2] - ref[2]) <= tol


def est_pierre(c):
    # pierre de la forge : (112, 98, 84) +-4, joints -9, rangée claire +5
    return c[3] and proche(c, (110, 96, 82), 14) and c[0] > c[2] + 18


def est_creux(c):
    # intérieur des cases de la forge : (40, 35, 32) +-2 et ombre (26, 22, 20)
    return c[3] and (proche(c, (40, 35, 32), 4))


def composantes(px, W, H, test):
    vu = set()
    comps = []
    for y in range(H):
        for x in range(W):
            if (x, y) in vu or not test(px[x, y]):
                continue
            pile = [(x, y)]
            vu.add((x, y))
            pts = []
            while pile:
                a, b = pile.pop()
                pts.append((a, b))
                for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    na, nb = a + da, b + db
                    if 0 <= na < W and 0 <= nb < H and (na, nb) not in vu and test(px[na, nb]):
                        vu.add((na, nb))
                        pile.append((na, nb))
            comps.append(pts)
    return comps


def finit_panneau(im):
    im = im.convert("RGBA")
    W, H = im.size
    px = im.load()
    pierre = [(x, y) for y in range(H) for x in range(W) if est_pierre(px[x, y])]
    if len(pierre) < 400:
        return None
    x0 = min(p[0] for p in pierre)
    y0 = min(p[1] for p in pierre)
    rnd = random.Random(W * 1000 + H + len(pierre))
    briques = set(pierre)
    tons = {}
    for (x, y) in pierre:
        rang = (y - y0) // 8
        dec = 8 if rang % 2 else 0
        bx, by = (x - x0 + dec) % 16, (y - y0) % 8
        cle = (rang, (x - x0 + dec) // 16)
        if cle not in tons:
            tons[cle] = rnd.uniform(1.5, 2.2)
        if bx == 0 or by == 0:
            c = JOINT
        else:
            v = tons[cle]
            if by == 1:
                v -= .6
            elif by == 7:
                v += .6
            if bx == 15:
                v += .3
            if rnd.random() < .05:
                v += rnd.choice((-.5, .5))
            c = tramage(PIERRE, v, x, y)
        px[x, y] = c + (px[x, y][3],)
    # cases : dégradé du haut (sombre) vers le bas
    for pts in composantes(px, W, H, est_creux):
        if len(pts) < 20:
            continue
        ys = [p[1] for p in pts]
        ya, yb = min(ys), max(ys)
        for (x, y) in pts:
            t = (y - ya) / max(1, yb - ya)
            px[x, y] = tramage(CASE, 2.4 - t * 2.0, x, y) + (px[x, y][3],)
    # grands aplats très sombres (vitrine du joueur…) : niche en dégradé
    noir = lambda c: c[3] and c[0] < 22 and c[1] < 20 and c[2] < 20
    for pts in composantes(px, W, H, noir):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        w, h = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
        if w < 30 or h < 30 or len(pts) < .8 * w * h:
            continue
        ya = min(ys)
        for (x, y) in pts:
            t = (y - ya) / max(1, h - 1)
            px[x, y] = tramage([(20, 18, 20), (28, 26, 28), (38, 34, 32), (50, 44, 38)], t * 3.2, x, y) + (255,)
        for x in range(min(xs) + 1, max(xs)):
            px[x, ya] = LAITON[3] + (255,)
    # or de la forge -> cuivre ; tout le reste (cadre brun, ombres) passe en gris froid de deepslate
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if not a or (x, y) in briques:
                continue
            l = (r * 3 + g * 6 + b) / 10
            if r > 110 and r - b > 55:
                px[x, y] = LAITON[0 if l > 200 else 1 if l > 150 else 2 if l > 115 else 3 if l > 85 else 4] + (a,)
            elif r > b + 4:
                v = int(l * .92)
                px[x, y] = (v, v, min(255, v + 6), a)
    # bandeaux clairs sous les titres (le jeu les écrit en gris foncé) : ligne du titre et ligne « Inventaire »
    hp = im.getbbox()[3]   # hauteur du panneau : le jeu écrit le titre à y = 6 et « Inventaire » à y = hauteur - 94
    for (ya, yb) in ((5, 14), (hp - 95, hp - 86)):
        for y in range(ya, yb + 1):
            for x in range(W):
                if (x, y) in briques:
                    px[x, y] = tramage(PLAQUE, .4 + (y - ya) / max(1, yb - ya) * 2.2, x, y) + (255,)
        for y, yv in ((ya - 1, ya), (yb + 1, yb)):
            for x in range(W):
                if (x, y) in briques and (x, yv) in briques:
                    px[x, y] = LAITON[3] + (255,)
    return im


def bouton(etat):
    w, h = 200, 20
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    rampe = PIERRE if etat != "disabled" else [(100, 95, 88), (90, 86, 80), (80, 76, 72), (70, 67, 63), (60, 58, 55), (52, 50, 48)]
    for y in range(h):
        for x in range(w):
            d = min(x, y, w - 1 - x, h - 1 - y)
            hg = min(x, y) == d
            if d == 0:
                c = SOMBRE
            elif d == 1:
                if etat == "hover":
                    c = LAITON[0] if hg else LAITON[2]
                elif etat == "disabled":
                    c = (86, 78, 66)
                else:
                    c = LAITON[2] if hg else LAITON[4]
            elif d == 2 and etat == "hover":
                c = LAITON[1] if hg else LAITON[3]
            else:
                v = (2.2 if etat == "hover" else 3.2) + (y / h) * 1.6
                c = tramage(rampe, v, x, y)
                if y == 2 or (etat == "hover" and y == 3):
                    c = rampe[1]
                if y == h - 3:
                    c = rampe[5]
            px[x, y] = c + (255,)
    return im


def case_barre(im, x, y, s=18):
    px = im.load()
    for j in range(s):
        for i in range(s):
            if i == 0 or j == 0:
                c = (24, 20, 16)
            elif i == s - 1 or j == s - 1:
                c = LAITON[2]
            else:
                c = tramage(CASE, 2.6 - (j / s) * 2.0, x + i, y + j)
            px[x + i, y + j] = c + (255,)


def barre_action():
    w, h = 182, 22
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for y in range(h):
        for x in range(w):
            d = min(x, y, w - 1 - x, h - 1 - y)
            if d == 0:
                c = SOMBRE
            elif d == 1:
                c = LAITON[1] if min(x, y) == 1 else LAITON[3]
            else:
                c = tramage(PIERRE, 2.4 + (y / h) * 1.2, x, y)
            px[x, y] = c + (255,)
    for i in range(9):
        case_barre(im, 2 + 20 * i, 2)
    return im


def selection():
    w, h = 24, 23
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for y in range(h):
        for x in range(w):
            d = min(x, y, w - 1 - x, h - 1 - y)
            hg = min(x, y) == d
            c = {0: SOMBRE + (255,), 1: (LAITON[0] if hg else LAITON[2]) + (255,), 2: (LAITON[1] if hg else LAITON[3]) + (255,),
                 3: SOMBRE + (150,)}.get(d)
            if c:
                px[x, y] = c
    for (cx, cy) in ((0, 0), (w - 3, 0), (0, h - 3), (w - 3, h - 3)):
        for j in range(3):
            for i in range(3):
                px[cx + i, cy + j] = (LAITON[0] if (i, j) == (1, 1) else LAITON[2]) + (255,)
    return im


TEINTES = {"blue": [(150, 214, 255), (84, 168, 240), (52, 118, 200)], "red": [(255, 160, 150), (230, 84, 70), (180, 46, 40)],
           "green": [(190, 250, 140), (110, 210, 80), (66, 156, 50)], "yellow": [(255, 240, 150), (240, 200, 70), (196, 150, 40)],
           "purple": [(222, 170, 255), (170, 110, 230), (122, 70, 180)], "pink": [(255, 180, 220), (236, 110, 170), (190, 66, 130)],
           "white": [(255, 255, 255), (220, 224, 230), (176, 182, 192)]}


def bossbar(coul, genre, taille):
    w, h = 182, 5
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    t = TEINTES[coul]
    for x in range(w):
        for y in range(h):
            emb = x < 2 or x >= w - 2
            if y in (0, h - 1):
                c = LAITON[3] if emb else SOMBRE
            elif emb:
                c = LAITON[1] if y == 1 else LAITON[2]
            elif genre == "background":
                c = (36, 31, 27) if y == 1 else (47, 41, 36)
            else:
                c = t[0] if y == 1 else (t[1] if y == 2 else t[2])
            px[x, y] = c + (255,)
    return im.resize(taille, Image.NEAREST)


zin = zipfile.ZipFile(ZIP)
fichiers = {n: zin.read(n) for n in zin.namelist()}
zin.close()
sortie = {}


def ecrit(nom, im):
    b = io.BytesIO()
    im.save(b, "PNG")
    sortie[nom] = b.getvalue()


nb = 0
BASE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "base_forge")   # panneaux tels qu'interface_forge.py les rend
for nom in sorted(fichiers):
    if nom.startswith(GUI + "container/") and nom.endswith(".png"):
        src = _os.path.join(BASE, nom[len(GUI + "container/"):])
        im = finit_panneau(Image.open(src if _os.path.exists(src) else io.BytesIO(fichiers[nom])))
        if im is not None:
            ecrit(nom, im)
            nb += 1
ecrit(GUI + "sprites/widget/button.png", bouton("normal"))
ecrit(GUI + "sprites/widget/button_highlighted.png", bouton("hover"))
ecrit(GUI + "sprites/widget/button_disabled.png", bouton("disabled"))
ecrit(GUI + "sprites/hud/hotbar.png", barre_action())
ecrit(GUI + "sprites/hud/hotbar_selection.png", selection())
for coul in TEINTES:
    for genre in ("background", "progress"):
        nom = GUI + f"sprites/boss_bar/{coul}_{genre}.png"
        taille = Image.open(io.BytesIO(fichiers[nom])).size if nom in fichiers else (182, 5)
        ecrit(nom, bossbar(coul, genre, taille))

fichiers.update(sortie)
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for n in sorted(fichiers):
        zi = zipfile.ZipInfo(n, date_time=(2026, 1, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, fichiers[n])
open(ZIP, "wb").write(buf.getvalue())
print(nb, "panneaux finis,", len(sortie) - nb, "sprites refaits")

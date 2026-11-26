# Animations et barres de l'interface « Forge » : à lancer APRÈS interface_finition.py, directement sur le resource pack.
# Les sprites d'interface acceptent une animation image par image (fichier .mcmeta) : les images sont empilées
# verticalement dans le PNG et le jeu les fait défiler.
#   - bossbars (7 couleurs) en haute définition : canal en pierre, embouts en laiton, graduations tous les 10 %,
#     remplissage en dégradé avec un reflet lumineux qui balaie la barre ;
#   - crans des bossbars (6, 10, 12, 20) en laiton ;
#   - barre d'expérience assortie, avec le même reflet ;
#   - bouton survolé : un éclat de lumière traverse la pierre ;
#   - sélection de la barre d'action : le laiton « respire » ;
#   - four et haut fourneau : flamme qui vacille, flèche de cuisson en laiton.
# Usage : python3 interface_animations.py metiers_resourcepack.zip [dossier_apercus]
import io, sys, json, math, zipfile, random
from PIL import Image
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from palette import *   # deepslate et cuivre (palette.py)

ZIP = sys.argv[1]
APERCUS = sys.argv[2] if len(sys.argv) > 2 else None
GUI = "assets/minecraft/textures/gui/sprites/"
BAY = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

TEINTES = {  # du plus clair au plus sombre
    "blue": [(196, 234, 255), (120, 190, 250), (72, 146, 228), (46, 104, 190), (28, 66, 136)],
    "red": [(255, 196, 186), (246, 118, 100), (214, 66, 54), (164, 38, 34), (110, 22, 22)],
    "green": [(214, 255, 176), (140, 224, 96), (90, 186, 64), (58, 136, 42), (34, 90, 26)],
    "yellow": [(255, 246, 186), (250, 214, 96), (226, 172, 48), (176, 124, 26), (120, 82, 16)],
    "purple": [(236, 206, 255), (190, 136, 246), (146, 90, 212), (104, 58, 166), (66, 34, 112)],
    "pink": [(255, 208, 232), (246, 138, 192), (218, 86, 152), (168, 52, 110), (112, 30, 72)],
    "white": [(255, 255, 255), (236, 240, 246), (204, 210, 220), (160, 166, 178), (112, 118, 130)],
}


def tramage(rampe, v, x, y):
    i = int(v + (BAY[y % 4][x % 4] + .5) / 16)
    return rampe[max(0, min(len(rampe) - 1, i))]


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def empile(images):
    w, h = images[0].size
    out = Image.new("RGBA", (w, h * len(images)), (0, 0, 0, 0))
    for k, im in enumerate(images):
        out.paste(im, (0, h * k))
    return out


# ------------------------------------------------------------------ bossbars (728 x 20, soit 4 px par pixel affiché)
BW, BH, CAP = 728, 20, 16


FER = [(150, 146, 142), (118, 113, 110), (92, 87, 84), (68, 64, 62)]


def embouts(px, teinte=None, k=.5):
    """Embouts thématisés : rouge (boss, horreur) en fer noirci et braise, violet en laiton et améthyste,
    autres couleurs en laiton avec une pierre de la couleur de la barre. k (0..1) fait respirer la pierre."""
    corps = FER if teinte == "red" else LAITON[1:]
    for side in (0, 1):
        for i in range(CAP):
            x = i if side == 0 else BW - 1 - i
            for y in range(BH):
                if y in (0, BH - 1) or i == 0:
                    c = SOMBRE
                elif i >= CAP - 2:
                    c = LAITON[4]
                elif y in (1, BH - 2) and teinte == "red":
                    c = LAITON[3]
                else:
                    t = (y - 1) / (BH - 3)
                    c = corps[0] if t < .25 else corps[1] if t < .6 else corps[2]
                px[x, y] = c + (255,)
        cx = 7 if side == 0 else BW - 8
        if teinte is None:
            for (dx, dy, c) in ((0, 0, LAITON[0]), (1, 0, LAITON[1]), (0, 1, LAITON[1]), (1, 1, LAITON[3]), (-1, 0, LAITON[3]), (0, -1, LAITON[1])):
                px[cx + dx, 9 + dy] = c + (255,)
            continue
        T = TEINTES[teinte]
        # pierre taillée qui remplit l'embout, cerclée de métal
        for y in range(3, BH - 3):
            for i in range(3, CAP - 4):
                x = i if side == 0 else BW - 1 - i
                if y in (3, BH - 4) or i in (3, CAP - 5):
                    c = SOMBRE
                else:
                    u = (i - 4) / (CAP - 10) if side == 0 else 1 - (i - 4) / (CAP - 10)
                    f = u + (y - 4) / (BH - 9)
                    c = T[0] if f < .45 else T[1] if f < 1.0 else T[2] if f < 1.5 else T[3]
                    if f < .45:
                        c = mix(c, (255, 255, 255), .35 * k)
                px[x, y] = c + (255,)


def boss_fond(teinte=None):
    im = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    px = im.load()
    for x in range(CAP, BW - CAP):
        for y in range(BH):
            if y in (0, BH - 1):
                c = SOMBRE
            elif y == 1:
                c = (18, 14, 12)
            elif y == BH - 2:
                c = PIERRE[4]
            else:
                t = (y - 2) / (BH - 4)
                c = tramage([(30, 26, 24), (38, 33, 30), (46, 40, 36), (54, 47, 42)], .4 + t * 2.6, x, y)
            px[x, y] = c + (255,)
    for k in range(1, 10):
        tx = CAP + int((BW - 2 * CAP) * k / 10)
        for y in range(3, BH - 3):
            px[tx, y] = (64, 56, 48, 255)
            px[tx + 1, y] = (24, 20, 18, 255)
    embouts(px, teinte)
    return im


def boss_rempli(teinte, phase, n, gemme=True):
    im = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    px = im.load()
    T = TEINTES[teinte]
    larg = BW - 2 * CAP
    balayage = n // 2  # moitié des images pour le reflet, moitié de pause : plus discret
    centre = -80 + (larg + 160) * phase / balayage if phase < balayage else -10000
    k = .5 + .5 * math.sin(2 * math.pi * phase / n)
    for x in range(CAP, BW - CAP):
        for y in range(BH):
            if y in (0, BH - 1):
                c = SOMBRE
            elif y == 1:
                c = T[4]
            else:
                t = (y - 2) / (BH - 4)
                if y in (2, 3):
                    c = T[0]
                elif t > .85:
                    c = T[4]
                else:
                    c = tramage(T, 1.0 + t * 2.6, x, y)
                d = (x - CAP) - centre - (y - BH / 2) * 3
                if abs(d) < 26:
                    c = mix(c, (255, 255, 255), .35 * (1 - abs(d) / 26))
            px[x, y] = c + (255,)
    for k in range(1, 10):
        tx = CAP + int(larg * k / 10)
        for y in range(4, BH - 3):
            px[tx, y] = mix(px[tx, y][:3], (0, 0, 0), .35) + (255,)
    embouts(px, teinte if gemme else None, k)
    return im


def crans(n, genre):
    im = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    px = im.load()
    larg = BW - 2 * CAP
    for k in range(1, n):
        tx = CAP + int(larg * k / n) - 2
        for y in range(1, BH - 1):
            for i in range(4):
                c = (LAITON[1] if i == 1 else LAITON[2] if i == 2 else LAITON[4]) if genre == "progress" else \
                    (LAITON[3] if i in (1, 2) else LAITON[4])
                if i == 0:
                    c = SOMBRE
                px[tx + i, y] = c + (255,)
        for (dx, dy) in ((1, 0), (2, 0)):
            px[tx + dx, 1] = (LAITON[0] if genre == "progress" else LAITON[2]) + (255,)
    return im


# ------------------------------------------------------------------ barre d'expérience (même gabarit, plus fine)
def xp_fond():
    return boss_fond(None)


def xp_rempli(phase, n):
    return boss_rempli("green", phase, n, gemme=False)


# ------------------------------------------------------------------ bouton survolé : éclat qui traverse la pierre
def bouton_survol(base, phase, n):
    im = base.copy()
    px = im.load()
    w, h = im.size
    centre = -40 + (w + 80) * phase / (n // 2) if phase < n // 2 else -10000
    for y in range(3, h - 3):
        for x in range(3, w - 3):
            d = x - centre - (y - h / 2) * 2
            if abs(d) < 12:
                r, g, b, a = px[x, y]
                px[x, y] = mix((r, g, b), (255, 236, 180), .3 * (1 - abs(d) / 12)) + (a,)
    return im


# ------------------------------------------------------------------ sélection de la barre d'action : laiton qui respire
def selection(phase, n):
    w, h = 24, 23
    k = .5 + .5 * math.sin(2 * math.pi * phase / n)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for y in range(h):
        for x in range(w):
            d = min(x, y, w - 1 - x, h - 1 - y)
            hg = min(x, y) == d
            if d == 0:
                px[x, y] = SOMBRE + (255,)
            elif d == 1:
                px[x, y] = mix(LAITON[2] if not hg else LAITON[1], LAITON[0], k * .7) + (255,)
            elif d == 2:
                px[x, y] = mix(LAITON[3] if not hg else LAITON[2], LAITON[1], k * .6) + (255,)
            elif d == 3:
                px[x, y] = LAITON[1] + (int(40 + 70 * k),)
    for (cx, cy) in ((0, 0), (w - 3, 0), (0, h - 3), (w - 3, h - 3)):
        for j in range(3):
            for i in range(3):
                px[cx + i, cy + j] = (mix(LAITON[1], (255, 255, 255), .5 * k) if (i, j) == (1, 1) else LAITON[2]) + (255,)
    return im


# ------------------------------------------------------------------ four : flamme qui vacille, flèche en laiton
def flamme(phase, n):
    w, h = 14, 14
    rnd = random.Random(phase * 31 + 7)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    FL = [(255, 248, 200), (255, 214, 110), (250, 150, 50), (214, 84, 30), (140, 40, 20)]
    for (cx, haut, larg) in ((3.5, 9 + rnd.randint(-1, 1), 2.4), (7, 12 + rnd.randint(-1, 1), 3.0), (10.5, 8 + rnd.randint(-1, 1), 2.4)):
        for y in range(h):
            hy = (h - 1 - y)
            if hy > haut:
                continue
            t = hy / haut
            demi = larg * (1 - t ** 1.6) + .3
            ox = math.sin((y + phase * 2) * .9) * .6 * t
            for x in range(w):
                d = abs(x - cx - ox)
                if d <= demi:
                    v = t * 3.2 + d / max(.5, demi) * 1.4
                    c = tramage(FL, v, x, y)
                    old = px[x, y]
                    if old[3] == 0 or sum(c) > sum(old[:3]):
                        px[x, y] = c + (255,)
    return im


def fleche_cuisson():
    w, h = 24, 16
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for y in range(h):
        for x in range(w):
            corps = 5 <= y <= 10 and x <= 15
            pointe = x > 15 and abs(y - 7.5) <= (23 - x) * .95
            if corps or pointe:
                t = y / h
                c = LAITON[0] if t < .35 else LAITON[1] if t < .6 else LAITON[2]
                px[x, y] = c + (255,)
    src = im.copy()
    sp = src.load()
    for y in range(h):
        for x in range(w):
            if sp[x, y][3] == 0 and any(0 <= x + dx < w and 0 <= y + dy < h and sp[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = SOMBRE + (255,)
    return im


# ------------------------------------------------------------------ écriture dans le pack
zin = zipfile.ZipFile(ZIP)
fichiers = {n: zin.read(n) for n in zin.namelist()}
zin.close()
sortie = {}


def png(nom, im):
    b = io.BytesIO()
    im.save(b, "PNG")
    sortie[GUI + nom] = b.getvalue()


# Images non carrées : l'animation doit donner la taille d'une image (width, height), sinon le jeu ne découpe pas
# la bande et affiche la texture manquante (corrigé le 26/11/2026).
def meta(nom, contenu):
    sortie[GUI + nom + ".mcmeta"] = json.dumps(contenu).encode()


apercus = {}
N = 32
fonds = {}
for teinte in TEINTES:
    fond = fonds[teinte] = boss_fond(teinte)
    png(f"boss_bar/{teinte}_background.png", fond)
    images = [boss_rempli(teinte, k, N) for k in range(N)]
    png(f"boss_bar/{teinte}_progress.png", empile(images))
    meta(f"boss_bar/{teinte}_progress.png", {"animation": {"frametime": 2, "interpolate": False, "width": BW, "height": BH}})
    apercus[teinte] = images
for n in (6, 10, 12, 20):
    for genre in ("background", "progress"):
        png(f"boss_bar/notched_{n}_{genre}.png", crans(n, genre))
png("hud/experience_bar_background.png", xp_fond())
xp = [xp_rempli(k, N) for k in range(N)]
png("hud/experience_bar_progress.png", empile(xp))
meta("hud/experience_bar_progress.png", {"animation": {"frametime": 2, "width": BW, "height": BH}})

cle_bouton = GUI + "widget/button_highlighted.png"
base = Image.open(io.BytesIO(fichiers[cle_bouton])).convert("RGBA").crop((0, 0, 200, 20))  # 1re image si déjà animé
NB = 28
bts = [bouton_survol(base, k, NB) for k in range(NB)]
png("widget/button_highlighted.png", empile(bts))
meta("widget/button_highlighted.png", {"gui": {"scaling": {"type": "nine_slice", "width": 200, "height": 20, "border": 3}},
                                       "animation": {"frametime": 2, "width": 200, "height": 20}})

NS = 12
sels = [selection(k, NS) for k in range(NS)]
png("hud/hotbar_selection.png", empile(sels))
meta("hud/hotbar_selection.png", {"animation": {"frametime": 3, "interpolate": True, "width": 24, "height": 23}})

NF = 6
fl = [flamme(k, NF) for k in range(NF)]
fleche = fleche_cuisson()
for four in ("furnace", "blast_furnace", "smoker"):
    png(f"container/{four}/lit_progress.png", empile(fl))
    meta(f"container/{four}/lit_progress.png", {"animation": {"frametime": 3}})
    png(f"container/{four}/burn_progress.png", fleche)

fichiers.update(sortie)
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for n in sorted(fichiers):
        zi = zipfile.ZipInfo(n, date_time=(2026, 1, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, fichiers[n])
open(ZIP, "wb").write(buf.getvalue())
print(len(sortie), "fichiers d'animation ajoutés")

# ------------------------------------------------------------------ aperçus GIF (facultatif)
if APERCUS:
    import os
    os.makedirs(APERCUS, exist_ok=True)
    fr = []
    for k in range(N):
        planche = Image.new("RGBA", (BW // 2 + 20, (BH // 2 + 14) * 8 + 10), (24, 26, 32, 255))
        for i, teinte in enumerate(TEINTES):
            barre = fonds[teinte].copy()
            plein = apercus[teinte][k]
            frac = [.32, .68, .55, .8, .45, .9, .6][i]
            barre.paste(plein.crop((0, 0, int(BW * frac), BH)), (0, 0))
            barre.paste(plein.crop((BW - CAP, 0, BW, BH)), (BW - CAP, 0)) if frac > .98 else None
            planche.alpha_composite(barre.resize((BW // 2, BH // 2), Image.NEAREST), (10, 10 + i * (BH // 2 + 14)))
        x = xp_fond()
        x.paste(xp[k].crop((0, 0, int(BW * .58), BH)), (0, 0))
        planche.alpha_composite(x.resize((BW // 2, BH // 4), Image.NEAREST), (10, 10 + 7 * (BH // 2 + 14) + 4))
        fr.append(planche.convert("RGB"))
    fr[0].save(os.path.join(APERCUS, "bossbars.gif"), save_all=True, append_images=fr[1:], duration=100, loop=0)
    b = [im.resize((600, 60), Image.NEAREST).convert("RGB") for im in bts]
    b[0].save(os.path.join(APERCUS, "bouton.gif"), save_all=True, append_images=b[1:], duration=100, loop=0)
    s = []
    hb = Image.open(io.BytesIO(fichiers[GUI + "hud/hotbar.png"])).convert("RGBA")
    for im in sels:
        p = Image.new("RGBA", (184, 24), (24, 26, 32, 255))
        p.alpha_composite(hb, (1, 1))
        p.alpha_composite(im, (0, 0))
        s.append(p.resize((552, 72), Image.NEAREST).convert("RGB"))
    s[0].save(os.path.join(APERCUS, "selection.gif"), save_all=True, append_images=s[1:], duration=150, loop=0)
    f = []
    for im in fl:
        p = Image.new("RGBA", (48, 18), (58, 52, 46, 255))
        p.alpha_composite(im, (2, 2))
        p.alpha_composite(fleche, (22, 1))
        f.append(p.resize((288, 108), Image.NEAREST).convert("RGB"))
    f[0].save(os.path.join(APERCUS, "four.gif"), save_all=True, append_images=f[1:], duration=150, loop=0)

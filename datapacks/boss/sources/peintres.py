"""Peintres de textures (pixel art genere, 1 pixel de texture = 1 pixel de modele).

Chaque peintre remplit un rectangle (x, y, w, h) d'une png.Image avec un hasard reproductible.
Ce sont les memes recettes que les maquettes 3D validees par Samuel (pierre, cuir, pages, toile de sac...).
"""
import math, random


def hexa(c):
    c = c.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255)


def _pal(o, defaut):
    return [hexa(c) for c in (o.get("pal") or defaut)]


def _choix(pal, n, seuils):
    for i, s in enumerate(seuils):
        if n < s:
            return pal[min(i, len(pal) - 1)]
    return pal[-1]


def pierre(img, x0, y0, w, h, R, o):
    pal = _pal(o, ["#2b2b30", "#34343a", "#3d3d44", "#46464e", "#25252a"])
    for y in range(h):
        for x in range(w):
            img.set(x0 + x, y0 + y, _choix(pal, R.random(), (.35, .65, .85, .95, 2)))
    y = 3
    while y < h:
        for x in range(w):
            if R.random() > .25:
                img.set(x0 + x, y0 + y, (15, 15, 18, 255))
        y += 4 + int(R.random() * 3)
    for _ in range(max(1, int(w * h / 90 * o.get("fissures", 1)))):
        x, y = int(R.random() * w), int(R.random() * h)
        for _ in range(3 + int(R.random() * 9)):
            if 0 <= x < w and 0 <= y < h:
                img.set(x0 + x, y0 + y, (18, 18, 20, 255))
            x += int(R.random() * 3) - 1
            y += 1 if R.random() > .4 else 0


def cuir(img, x0, y0, w, h, R, o):
    pal = _pal(o, ["#3b1d4f", "#4a2660", "#2e1540", "#56306e"])
    for y in range(h):
        for x in range(w):
            img.set(x0 + x, y0 + y, pal[int(R.random() * len(pal))])
    if o.get("liseré", True) and w > 3 and h > 3:
        for x in range(w):
            img.set(x0 + x, y0, hexa("#d9a640")); img.set(x0 + x, y0 + h - 1, hexa("#d9a640"))
        for y in range(h):
            img.set(x0, y0 + y, hexa("#d9a640")); img.set(x0 + w - 1, y0 + y, hexa("#d9a640"))
        if w > 8 and h > 8:
            for cx, cy in ((1, 1), (w - 4, 1), (1, h - 4), (w - 4, h - 4)):
                for i in range(3):
                    for j in range(3):
                        img.set(x0 + cx + i, y0 + cy + j, hexa("#f0c95a"))
                img.set(x0 + cx + 1, y0 + cy + 1, hexa("#8a5f1a"))
    if o.get("rune") and w > 10 and h > 10:
        cx, cy = w // 2, h // 2
        for i in range(-4, 5):
            for px, py in ((cx + i, cy), (cx, cy + i), (cx + i, cy + i), (cx + i, cy - i)):
                img.set(x0 + px, y0 + py, hexa("#c58cff"))


def page(img, x0, y0, w, h, R, o):
    for y in range(h):
        for x in range(w):
            n = R.random()
            img.set(x0 + x, y0 + y, hexa("#eadfc0" if n < .5 else "#e0d2ad" if n < .85 else "#f4ecd6"))
    for y in range(3, h - 2, 3):
        for x in range(2, w - 2):
            if R.random() > .35:
                img.set(x0 + x, y0 + y, hexa("#7a2fd0" if R.random() > .93 else "#3a3046"))


def tranche(img, x0, y0, w, h, R, o):
    for y in range(h):
        for x in range(w):
            c = "#d9caa0" if y % 2 else "#efe4c6"
            if R.random() > .9:
                c = "#b8a77a"
            img.set(x0 + x, y0 + y, hexa(c))


def runes(img, x0, y0, w, h, R, o):
    fond = o.get("fond")
    for y in range(h):
        for x in range(w):
            img.set(x0 + x, y0 + y, hexa(fond) if fond else (0, 0, 0, 0))
    c = hexa(o.get("c", "#c58cff"))
    for _ in range(max(1, w * h // 5)):
        x, y = int(R.random() * w), int(R.random() * h)
        col = c if R.random() > .3 else (255, 255, 255, 255)
        img.set(x0 + x, y0 + y, col)
        if R.random() > .7 and y + 1 < h:
            img.set(x0 + x, y0 + y + 1, col)


def oeil(img, x0, y0, w, h, R, o):
    for y in range(h):
        for x in range(w):
            img.set(x0 + x, y0 + y, hexa("#f2efe6"))
    for _ in range(w * h // 18):
        img.set(x0 + int(R.random() * w), y0 + int(R.random() * h), hexa("#c0392b"))
    cx, cy, ri = w / 2, h / 2, min(w, h) * .38
    for y in range(h):
        for x in range(w):
            d = math.hypot(x + .5 - cx, y + .5 - cy)
            if d < ri:
                c = "#0a0410" if d < ri * .38 else ("#9b4dff" if d < ri * .7 else "#5a1fb0")
                if d > ri * .38 and R.random() > .8:
                    c = "#d6b3ff"
                img.set(x0 + x, y0 + y, hexa(c))
    for i in range(2):
        for j in range(2):
            img.set(x0 + int(cx - ri * .45) + i, y0 + int(cy - ri * .5) + j, (255, 255, 255, 255))


def toile(img, x0, y0, w, h, R, o):
    pal = _pal(o, ["#8a7552", "#7a6646", "#9b8660", "#6b583b"])
    for y in range(h):
        for x in range(w):
            img.set(x0 + x, y0 + y, pal[((x + y) % 2) * 2 + (1 if R.random() > .5 else 0)])
    for _ in range(w * h // 30):
        x, y = int(R.random() * w), int(R.random() * h)
        c = (60, 40, 20, 255) if R.random() > .5 else (90, 20, 20, 255)
        img.set(x0 + x, y0 + y, c)
        if x + 1 < w:
            img.set(x0 + x + 1, y0 + y, c)
    if o.get("couture"):
        yc = int(h * o["couture"])
        for x in range(1, w - 1, 2):
            for dy in (0, -1):
                if 0 <= yc + dy < h:
                    img.set(x0 + x, y0 + yc + dy, hexa("#2a1a10"))


def haillons(img, x0, y0, w, h, R, o):
    pal = _pal(o, ["#1b1a1f", "#25222a", "#2e2a33", "#131216", "#3a2a2a"])
    trou = o.get("trou", False)
    for y in range(h):
        for x in range(w):
            bas = y > h - 4 - int(R.random() * 4)
            if trou and ((bas and R.random() > .45) or R.random() < .03):
                img.set(x0 + x, y0 + y, (0, 0, 0, 0))
                continue
            img.set(x0 + x, y0 + y, pal[int(R.random() * len(pal))])
    for _ in range(w * h // 40):
        img.set(x0 + int(R.random() * w), y0 + int(R.random() * h), hexa("#5a1a1a"))


def paille(img, x0, y0, w, h, R, o):
    for y in range(h):
        for x in range(w):
            n = R.random()
            img.set(x0 + x, y0 + y, hexa("#a68a3a" if n < .4 else "#8c7230" if n < .7 else "#c2a64e" if n < .9 else "#6b5524"))


def plumes(img, x0, y0, w, h, R, o):
    for y in range(h):
        for x in range(w):
            n = R.random()
            img.set(x0 + x, y0 + y, hexa("#0e0e14" if n < .5 else "#181824" if n < .8 else "#232338" if n < .95 else "#3b3f6a"))
    for y in range(1, h, 3):
        for x in range(y % 2, w, 3):
            img.set(x0 + x, y0 + y, hexa("#2c3050"))


def bois_mort(img, x0, y0, w, h, R, o):
    for y in range(h):
        for x in range(w):
            n = R.random()
            img.set(x0 + x, y0 + y, hexa("#4a4038" if n < .4 else "#3b332c" if n < .7 else "#5a4f45" if n < .9 else "#2a241f"))
    for x in range(0, w, 3):
        for y in range(h):
            if R.random() > .3:
                img.set(x0 + x, y0 + y, hexa("#231e19"))


def encre(img, x0, y0, w, h, R, o):
    pal = _pal(o, ["#140a1e", "#1d1030", "#26143c", "#0d0614", "#2f1a4a"])
    for y in range(h):
        for x in range(w):
            img.set(x0 + x, y0 + y, pal[int(R.random() * len(pal))])
    for _ in range(w * h // 25):
        img.set(x0 + int(R.random() * w), y0 + int(R.random() * h), hexa("#6a3aa8"))


def uni(img, x0, y0, w, h, R, o):
    c = hexa(o.get("c", "#808080"))
    for y in range(h):
        for x in range(w):
            v = int((R.random() - .5) * o.get("bruit", 10))
            img.set(x0 + x, y0 + y, tuple(max(0, min(255, c[i] + v)) for i in range(3)) + (255,))


PEINTRES = {k: v for k, v in globals().items() if callable(v) and k not in ("hexa", "_pal", "_choix")}

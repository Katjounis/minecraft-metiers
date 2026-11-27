# -*- coding: utf-8 -*-
"""Voxels des bâtiments d'Industrie : une scène = des boîtes texturées par un atlas de motifs 512 px.
Les mêmes fonctions ont servi aux visuels de conception (planches du 27/11/2026) ; modeles.py les exporte
en modèles d'objet du resource pack (item_display)."""
import math
import numpy as np
from PIL import Image
MOTIFS_LUEUR = {"lueur", "runes", "lave"}
class Scene:
    def __init__(s): s.els = []; s.cols = {}
    def cell(s, col, motif):
        k = (col, motif)
        if k not in s.cols: s.cols[k] = len(s.cols)
        return s.cols[k]
    def add(s, frm, to, col, motif="bruit", rot=None, faces=None):
        c = s.cell(col, motif); cx, cy = (c % 16) * 1.0, (c // 16) * 1.0
        uv = [cx + 0.02, cy + 0.02, cx + 0.98, cy + 0.98]
        s.els.append({"from": list(frm), "to": list(to), "rotation": rot,
                      "faces": {f: {"uv": uv, "glow": motif in MOTIFS_LUEUR} for f in (faces or ["north", "south", "east", "west", "up", "down"])}})
    def atlas(s):
        im = np.zeros((512, 512, 4), np.uint8); rng = np.random.default_rng(5)
        for (col, motif), c in s.cols.items():
            base = np.array([int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16)], float)
            x0, y0 = (c % 16) * 32, (c // 16) * 32
            for y in range(32):
                for x in range(32):
                    v = 1 + rng.uniform(-0.05, 0.05); extra = None
                    if motif == "brique": v *= 0.68 if (y % 8 == 0 or (x + (8 if (y // 8) % 2 else 0)) % 16 == 0) else 1
                    elif motif == "pave": v *= 0.7 if ((x // 8 + y // 8) % 2 and (x % 8 == 0 or y % 8 == 0)) or (x % 8 == 0 and y % 8 == 0) else (1.08 if (x // 8 + y // 8) % 2 else 0.95)
                    elif motif == "planches": v *= (0.7 if y % 8 == 0 else 1) * (1 + 0.08 * np.sin(x * 0.7 + (y // 8) * 2))
                    elif motif == "metal": v *= 1.25 if ((x in (3, 28) and y in (3, 28))) else (0.8 if x in (0, 31) or y in (0, 31) else 1 + 0.04 * np.sin(y * 1.3))
                    elif motif == "cuivre": v *= 1.0; extra = (95, 168, 138) if rng.random() < 0.12 else None
                    elif motif == "dore": v *= 1.3 if (x + y) % 11 == 0 else (0.85 if x in (0, 31) or y in (0, 31) else 1)
                    elif motif == "rayure": v = 0.3 if ((x + y) // 6) % 2 else 1.0
                    elif motif == "minerai": extra = None if rng.random() > 0.25 else (90, 90, 98)
                    elif motif == "lueur": v = 0.85 + 0.35 * (1 - (abs(x - 15.5) + abs(y - 15.5)) / 31)
                    elif motif == "lave": v = 0.8 + 0.4 * abs(np.sin(x * 0.4 + y * 0.25))
                    elif motif == "runes": v = 1.25 if (x % 8 in (2, 5) and y % 10 in (2, 3, 4, 5, 6)) or (y % 10 == 4 and x % 8 in (3, 4)) else 0.25
                    elif motif == "verre": v = 0.75 if (x in (0, 31) or y in (0, 31)) else (1.3 if abs(x - y) < 2 else 1.0)
                    elif motif == "plat": v = 1.0
                    px = np.clip(base * v, 0, 255) if extra is None else np.array(extra)
                    im[y0 + y, x0 + x, :3] = px; im[y0 + y, x0 + x, 3] = 255
        return Image.fromarray(im, "RGBA")

# ---- scenes3.py
CUIV, PATINE, OR_, BOIS, PLANCHE, ARDO, PIERRE, FERS = "#c8754a", "#4fa384", "#e8b830", "#4a2e1a", "#a0703e", "#3a3a44", "#8e8984", "#9aa0a8"
FER, OR, DIA, EME, NET, AME, RED = "#e6e6ea", "#f7c843", "#5ff0e6", "#3ee070", "#ff7a3a", "#b878ff", "#ff5a6a"

def lisere(s, x0, y, z0, x1, z1, col="#e8b830", ep=1.0):
    for (a0, b0, a1, b1) in ((x0, z0, x1, z0 + ep), (x0, z1 - ep, x1, z1), (x0, z0, x0 + ep, z1), (x1 - ep, z0, x1, z1)):
        s.add((a0, y, b0), (a1, y + 1.0, b1), col, "dore")

def rond(s, cx, y0, y1, cz, r, col, motif="bruit", n=3):
    """Cylindre approché : n carrés tournés."""
    for k in range(n):
        s.add((cx - r, y0, cz - r), (cx + r, y1, cz + r), col, motif, rot={"y": k * 90 / n, "origin": [cx, y0, cz]})

def anneau(s, cx, cy, cz, R, col, motif="dore", n=16, ep=1.2, plan="xz", tilt=0):
    for k in range(n):
        a = k * 360 / n
        if plan == "xz":
            s.add((cx + R - ep / 2, cy - ep / 2, cz - 0.9), (cx + R + ep / 2, cy + ep / 2, cz + 0.9), col, motif, rot={"y": a, "x": tilt, "origin": [cx, cy, cz]} if tilt else {"y": a, "origin": [cx, cy, cz]})
        else:
            s.add((cx - 0.9, cy + R - ep / 2, cz - ep / 2), (cx + 0.9, cy + R + ep / 2, cz + ep / 2), col, motif, rot={"z": a, "origin": [cx, cy, cz]})

def engrenage(s, cx, cy, z, r, col, dents=10, ep=1.4):
    for a in (0, 22.5, 45, 67.5):
        s.add((cx - r * 0.72, cy - r * 0.72, z), (cx + r * 0.72, cy + r * 0.72, z + ep), col, "metal", rot={"z": a, "origin": [cx, cy, z]})
    for k in range(dents):
        s.add((cx - 0.8, cy + r * 0.65, z), (cx + 0.8, cy + r * 1.08, z + ep), col, "metal", rot={"z": k * 360 / dents, "origin": [cx, cy, z]})
    s.add((cx - r * 0.25, cy - r * 0.25, z - 0.4), (cx + r * 0.25, cy + r * 0.25, z + ep + 0.4), OR_, "dore")

def haut_fourneau(s, x0, z0):
    """Haut-fourneau des Titans : ferme à fer géante."""
    s.add((x0 - 4, 0, z0 - 4), (x0 + 44, 4, z0 + 44), ARDO, "pave")
    s.add((x0, 4, z0), (x0 + 40, 8, z0 + 40), PIERRE, "pave")
    lisere(s, x0 - 0.5, 7.5, z0 - 0.5, x0 + 40.5, z0 + 40.5)
    s.add((x0 + 4, 8, z0 + 4), (x0 + 36, 50, z0 + 36), PIERRE, "brique")
    for (a, b) in ((0, 0), (32, 0), (0, 32), (32, 32)):   # contreforts à gradins, chapeaux d'or
        s.add((x0 + a, 8, z0 + b), (x0 + a + 8, 40, z0 + b + 8), "#7a7570", "brique")
        s.add((x0 + a + 1, 40, z0 + b + 1), (x0 + a + 7, 52, z0 + b + 7), "#7a7570", "brique")
        s.add((x0 + a + 0.5, 52, z0 + b + 0.5), (x0 + a + 7.5, 54, z0 + b + 7.5), OR_, "dore")
        s.add((x0 + a + 2.5, 54, z0 + b + 2.5), (x0 + a + 5.5, 60, z0 + b + 5.5), OR_, "dore", rot={"y": 45, "origin": [x0 + a + 4, 54, z0 + b + 4]})
        s.add((x0 + a + 3, 60, z0 + b + 3), (x0 + a + 5, 63, z0 + b + 5), "#ffd060", "lueur")
    # grande baie à barreaux de cuivre (face avant z = 36)
    s.add((x0 + 10, 12, z0 + 35.6), (x0 + 30, 44, z0 + 36.4), "#140c0a", "plat")
    for k in range(12, 30, 3):
        s.add((x0 + k, 12, z0 + 36.2), (x0 + k + 1, 44, z0 + 37.2), CUIV, "cuivre")
    for y in (20, 30, 40):
        s.add((x0 + 10, y, z0 + 36.2), (x0 + 30, y + 1, z0 + 37.2), CUIV, "cuivre")
    s.add((x0 + 9, 44, z0 + 35.5), (x0 + 31, 47, z0 + 37.5), OR_, "dore")
    # golem à l'intérieur, sur la lave
    s.add((x0 + 11, 12, z0 + 20), (x0 + 29, 13, z0 + 35), "#ff6a10", "lave")
    g = (x0 + 20, z0 + 28)
    for (a0, a1, b0, b1, c0, c1) in ((-6, 6, -3, 3, 24, 37), (-3, 3, -3, 3, 37, 43), (-9, -6, -2, 2, 21, 36), (6, 9, -2, 2, 21, 36), (-5, -1, -2, 2, 13, 24), (1, 5, -2, 2, 13, 24)):
        s.add((g[0] + a0, c0, g[1] + b0), (g[0] + a1, c1, g[1] + b1), "#dcd2c2")
    s.add((g[0] - 2, 39.5, g[1] + 3), (g[0] - 0.8, 40.5, g[1] + 3.3), RED, "lueur"); s.add((g[0] + 0.8, 39.5, g[1] + 3), (g[0] + 2, 40.5, g[1] + 3.3), RED, "lueur")
    # dôme de cuivre : gradins, nervures dorées, lanterne
    for i in range(5):
        m = 4 + i * 3
        s.add((x0 + m, 50 + 3 * i, z0 + m), (x0 + 40 - m, 53 + 3 * i, z0 + 40 - m), PATINE, "cuivre")
    for k in range(8):
        s.add((x0 + 19.4, 50, z0 + 4), (x0 + 20.6, 52, z0 + 20), OR_, "dore", rot={"y": k * 45, "x": -38, "origin": [x0 + 20, 50, z0 + 20]})
    s.add((x0 + 16, 65, z0 + 16), (x0 + 24, 72, z0 + 24), OR_, "dore")
    s.add((x0 + 17.5, 66, z0 + 15.8), (x0 + 22.5, 71, z0 + 24.2), "#ffdd70", "lueur")
    s.add((x0 + 18.5, 72, z0 + 18.5), (x0 + 21.5, 82, z0 + 21.5), OR_, "dore", rot={"y": 45, "origin": [x0 + 20, 72, z0 + 20]})
    # engrenages et cheminées
    engrenage(s, x0 + 44.5, 26, z0 + 12, 7, OR_); engrenage(s, x0 + 44.5, 16, z0 + 24, 5, CUIV)
    for z in (6, 30):
        rond(s, x0 - 6, 8, 70, z0 + z, 2.6, CUIV, "cuivre")
        s.add((x0 - 9, 70, z0 + z - 3), (x0 - 3, 73, z0 + z + 3), OR_, "dore")
        s.add((x0 - 7.5, 73, z0 + z - 1.5), (x0 - 4.5, 74, z0 + z + 1.5), "#ff8a30", "lueur")
    # coulée de fer et moules à lingots
    s.add((x0 + 17, 8, z0 + 40), (x0 + 23, 10, z0 + 64), ARDO, "pave"); s.add((x0 + 18.5, 9.6, z0 + 40), (x0 + 21.5, 10.2, z0 + 62), "#ffa040", "lave")
    for i in range(4):
        z = z0 + 44 + i * 5
        for sx in (-1, 1):
            x = x0 + 20 + sx * 7
            s.add((x - 3, 4, z), (x + 3, 7, z + 4), ARDO, "pave"); s.add((x - 2.3, 7, z + 0.7), (x + 2.3, 8.2, z + 3.3), FER, "metal")

def puits_cristal(s, x0, z0, col, base="#262230"):
    """Puits de cristal : générateur de minerai."""
    for i, (m, h) in enumerate(((0, 4), (4, 8), (8, 12))):
        s.add((x0 + m, h - 4, z0 + m), (x0 + 48 - m, h, z0 + 48 - m), base if i != 1 else ARDO, "pave")
        lisere(s, x0 + m - 0.4, h - 0.6, z0 + m - 0.4, x0 + 48 - m + 0.4, z0 + 48 - m + 0.4)
    s.add((x0 + 16, 12, z0 + 16), (x0 + 32, 13, z0 + 32), col, "runes")
    for (a, b) in ((6, 6), (38, 6), (6, 38), (38, 38)):   # piliers runiques et pierres flottantes
        s.add((x0 + a, 12, z0 + b), (x0 + a + 4, 34, z0 + b + 4), "#2e2a36", "pave")
        s.add((x0 + a - 0.2, 18, z0 + b - 0.2), (x0 + a + 4.2, 28, z0 + b + 4.2), col, "runes", faces=["north", "south", "east", "west"])
        s.add((x0 + a - 0.6, 34, z0 + b - 0.6), (x0 + a + 4.6, 36, z0 + b + 4.6), OR_, "dore")
        s.add((x0 + a + 0.5, 39, z0 + b + 0.5), (x0 + a + 3.5, 42, z0 + b + 3.5), col, "lueur", rot={"y": 45, "x": 35, "origin": [x0 + a + 2, 40.5, z0 + b + 2]})
    cx, cy, cz = x0 + 24, 32, z0 + 24
    s.add((cx - 6, cy - 6, cz - 6), (cx + 6, cy + 6, cz + 6), col, "minerai", rot={"y": 45, "x": 35, "origin": [cx, cy, cz]})
    for k, (dx, dy, dz, sz, a) in enumerate(((8, -4, 2, 3.2, 20), (-7, -5, -3, 2.6, -25), (2, 8, -7, 2.4, 40), (-3, -8, 7, 2.8, 10))):
        s.add((cx + dx - sz, cy + dy - sz, cz + dz - sz), (cx + dx + sz, cy + dy + sz, cz + dz + sz), col, "minerai", rot={"z": a, "y": a * 2, "origin": [cx + dx, cy + dy, cz + dz]})
    anneau(s, cx, cy, cz, 13, OR_, "dore", n=20)
    anneau(s, cx, cy, cz, 10.5, col, "lueur", n=18, ep=0.9, tilt=55)
    s.add((cx - 0.8, cy + 10, cz - 0.8), (cx + 0.8, cy + 46, cz + 0.8), col, "lueur")      # faisceau
    s.add((x0 + 48, 0, z0 + 16), (x0 + 60, 6, z0 + 32), ARDO, "pave"); lisere(s, x0 + 47.6, 5.6, z0 + 15.6, x0 + 60.4, z0 + 32.4)
    for i in range(4):
        s.add((x0 + 50 + (i % 2) * 4, 6.4 + 1.4 * (i // 2), z0 + 19 + i * 2), (x0 + 56 + (i % 2) * 4, 7.6 + 1.4 * (i // 2), z0 + 22 + i * 2), col, "metal")

def distillerie(s, x0, z0):
    s.add((x0, 0, z0), (x0 + 44, 10, z0 + 28), "#6a3a2a", "brique")
    s.add((x0 + 6, 2, z0 - 0.3), (x0 + 16, 8, z0 + 0.2), "#ff6a20", "lave"); s.add((x0 + 28, 2, z0 - 0.3), (x0 + 38, 8, z0 + 0.2), "#ff6a20", "lave")
    s.add((x0 - 1, 10, z0 - 1), (x0 + 45, 11, z0 + 29), "#4a2a1e", "pave"); lisere(s, x0 - 1.2, 10.2, z0 - 1.2, x0 + 45.2, z0 + 29.2)
    for cx in (x0 + 11, x0 + 33):   # alambics de cuivre
        rond(s, cx, 11, 15, z0 + 14, 5.5, CUIV, "cuivre", n=4); rond(s, cx, 15, 25, z0 + 14, 7, CUIV, "cuivre", n=4); rond(s, cx, 25, 29, z0 + 14, 5, CUIV, "cuivre", n=4); rond(s, cx, 29, 38, z0 + 14, 1.8, CUIV, "cuivre", n=4)
        s.add((cx - 7.4, 17, z0 + 6.6), (cx + 7.4, 18.4, z0 + 21.4), OR_, "dore")
        s.add((cx - 1, 36, z0 + 13), (cx + 12, 38, z0 + 15), CUIV, "cuivre", rot={"z": -18, "origin": [cx, 37, z0 + 14]})
    for i, c in enumerate((RED, AME, "#50d0ff", EME, OR)):   # fioles lumineuses sur l'étagère
        x = x0 + 4 + i * 8
        s.add((x0 + 2, 0, z0 + 30), (x0 + 42, 2, z0 + 38), PLANCHE, "planches") if i == 0 else None
        s.add((x, 2, z0 + 31), (x + 5, 8, z0 + 36), "#d0f0ff", "verre"); s.add((x + 0.6, 2.4, z0 + 31.6), (x + 4.4, 6, z0 + 35.4), c, "lueur")
        s.add((x + 1.5, 8, z0 + 32.5), (x + 3.5, 10, z0 + 34.5), "#8a6a4a")

def tapis(s, x0, z0, L, axe="x", y=0, items=()):
    for i in range(L):
        bx, bz = (x0 + 16 * i, z0) if axe == "x" else (x0, z0 + 16 * i)
        P = lambda a, b, c=0: ((bx + a, y + c, bz + b) if axe == "x" else (bx + b, y + c, bz + a))
        def box(a0, b0, c0, a1, b1, c1, col, m="bruit"):
            p, q = P(a0, b0, c0), P(a1, b1, c1)
            s.add(tuple(min(u, v) for u, v in zip(p, q)), tuple(max(u, v) for u, v in zip(p, q)), col, m)
        for a in (1, 13):
            for b in (1, 13): box(a, b, 0, a + 2, b + 2, 5, BOIS, "planches")
        box(0, 0, 5, 16, 2, 8, PLANCHE, "planches"); box(0, 14, 5, 16, 16, 8, PLANCHE, "planches")
        box(0, -0.3, 7.6, 16, 2.3, 8.6, CUIV, "cuivre"); box(0, 13.7, 7.6, 16, 16.3, 8.6, CUIV, "cuivre")
        box(0, 2, 5.5, 16, 14, 7, "#2a2622")
        for k in range(0, 16, 4): box(k + 0.5, 2.3, 7, k + 1.5, 13.7, 7.3, "#4a443e")
        box(6.5, 6.8, 7.31, 9.5, 9.2, 7.45, "#ffd060", "lueur")
        for a in (0, 16): box(a - 1, 0.8, 4.8, a + 1, 2.2, 7.6, OR_, "dore"); box(a - 1, 13.8, 4.8, a + 1, 15.2, 7.6, OR_, "dore")
    for (k, col, sz) in items:
        bx, bz = (x0 + k, z0 + 8) if axe == "x" else (x0 + 8, z0 + k)
        s.add((bx - sz, y + 7.4, bz - sz * 0.6), (bx + sz, y + 7.4 + sz * 0.7, bz + sz * 0.6), col, "metal")

def trieur(s, x0, z0):
    """Trieur : un tapis entre, trois sortent selon l'objet."""
    s.add((x0, 0, z0), (x0 + 24, 12, z0 + 24), ARDO, "pave"); s.add((x0 - 0.5, 11.5, z0 - 0.5), (x0 + 24.5, 12.5, z0 + 24.5), OR_, "dore")
    rond(s, x0 + 12, 12, 20, z0 + 12, 7, CUIV, "cuivre"); s.add((x0 + 8, 20, z0 + 8), (x0 + 16, 22, z0 + 16), OR_, "dore")
    engrenage(s, x0 + 12, 6, z0 + 24.2, 5, OR_)
    for i, c in enumerate((FER, OR, DIA)):
        s.add((x0 + 4 + i * 7, 13, z0 - 0.4), (x0 + 8 + i * 7, 16, z0), c, "lueur")

# ---- scenes4.py
"""v4 : tubes à faisceau (flux virtuels) reliant les machines au Nexus."""

def tube(s, pts, col, items=(), r=1.6, pas=5.0, y_items=None, ring=OR_):
    """Tube de verre : 4 rails sombres, colliers dorés, faisceau, paquets d'objets lumineux."""
    k = 0
    for (a, b) in zip(pts, pts[1:]):
        ax = 0 if a[0] != b[0] else (1 if a[1] != b[1] else 2)
        lo, hi = min(a[ax], b[ax]), max(a[ax], b[ax])
        def box(c0, c1, off0, off1, cl, m):
            p = list(a); q = list(a)
            p[ax], q[ax] = c0, c1
            o = [i for i in range(3) if i != ax]
            p[o[0]] += off0[0]; q[o[0]] += off1[0]; p[o[1]] += off0[1]; q[o[1]] += off1[1]
            s.add(tuple(min(u, v) for u, v in zip(p, q)), tuple(max(u, v) for u, v in zip(p, q)), cl, m)
        t = lo
        while t < hi:
            u = min(hi, t + 6)
            for sa in (-1, 1):
                for sb in (-1, 1):
                    box(t, u, (sa * r - 0.45, sb * r - 0.45), (sa * r + 0.45, sb * r + 0.45), "#2a2c34", "metal")
            box(t, u, (-0.6, -0.6), (0.6, 0.6), col, "lueur")
            t = u
        c = lo + 2
        while c < hi - 1:
            e = 0.55
            for (o0, o1) in (((-r - e, -r - e), (r + e, -r + e)), ((-r - e, r - e), (r + e, r + e)), ((-r - e, -r - e), (-r + e, r + e)), ((r - e, -r - e), (r + e, r + e))):
                box(c, c + 0.9, o0, o1, ring, "dore")
            c += 9
        c = lo + 1.5 + (k % 3)
        while c < hi - 1:
            ic = items[k % len(items)] if items else col
            sz = r * 0.5
            box(c, c + sz * 1.8, (-sz, -sz), (sz, sz), ic, "lueur"); c += pas; k += 1
    for p in pts[1:-1]:   # coudes : boîtier sombre à hublot
        s.add((p[0] - r - 0.6, p[1] - r - 0.6, p[2] - r - 0.6), (p[0] + r + 0.6, p[1] + r + 0.6, p[2] + r + 0.6), "#2a2632", "metal")
        s.add((p[0] - r * 0.5, p[1] + r + 0.6, p[2] - r * 0.5), (p[0] + r * 0.5, p[1] + r + 0.9, p[2] + r * 0.5), col, "lueur")
        lisere(s, p[0] - r - 0.8, p[1] - r - 0.8, p[2] - r - 0.8, p[0] + r + 0.8, p[2] + r + 0.8, ep=0.6)

def nexus(s, cx, cz):
    """Nexus : entrepôt virtuel, avale tous les flux."""
    s.add((cx - 22, 0, cz - 22), (cx + 22, 5, cz + 22), "#1e1a26", "pave"); lisere(s, cx - 22.4, 4.4, cz - 22.4, cx + 22.4, cz + 22.4)
    s.add((cx - 16, 5, cz - 16), (cx + 16, 9, cz + 16), ARDO, "pave"); lisere(s, cx - 16.4, 8.4, cz - 16.4, cx + 16.4, cz + 16.4)
    rond(s, cx, 9, 30, cz, 11, "#24202c", "pave", n=4)
    rond(s, cx, 30, 33, cz, 12.5, OR_, "dore", n=4)
    for k in range(8):   # vitres lumineuses tout autour
        s.add((cx - 2, 13, cz - 11.6), (cx + 2, 28, cz - 10.6), AME, "runes", rot={"y": k * 45, "origin": [cx, 13, cz]})
    rond(s, cx, 33, 44, cz, 7, "#2c2636", "pave", n=4)
    rond(s, cx, 44, 46, cz, 8.5, OR_, "dore", n=4)
    c = (cx, 56, cz)
    s.add((c[0] - 5, c[1] - 5, c[2] - 5), (c[0] + 5, c[1] + 5, c[2] + 5), AME, "lueur", rot={"y": 45, "x": 35, "origin": list(c)})
    anneau(s, *c, 10, OR_, "dore", n=20)
    anneau(s, *c, 8, "#e0c0ff", "lueur", n=18, ep=0.8, tilt=60)
    anneau(s, *c, 12.5, "#e0c0ff", "lueur", n=22, ep=0.6, tilt=-35)
    s.add((cx - 1, 46, cz - 1), (cx + 1, 51, cz + 1), "#e0c0ff", "lueur")
    for (a, b) in ((-19, -19), (19, -19), (-19, 19), (19, 19)):
        s.add((cx + a - 1.5, 5, cz + b - 1.5), (cx + a + 1.5, 18, cz + b + 1.5), "#2e2a36", "pave")
        s.add((cx + a - 1, 18, cz + b - 1), (cx + a + 1, 21, cz + b + 1), AME, "lueur")

def scene_flux():
    s = Scene()
    for i in range(-112, 96, 16):
        for j in range(-112, 96, 16):
            s.add((i, -3, j), (i + 16, -0.01, j + 16), "#34323a" if (i // 16 + j // 16) % 2 else "#2e2c34", "pave")
    nexus(s, 0, 0)
    puits_cristal(s, -110, -110, DIA)
    puits_cristal(s, 40, -110, OR)
    puits_cristal(s, -110, 40, NET)
    R = 2.6
    tube(s, [(-62, 24, -86), (-6, 24, -86), (-6, 24, -12)], DIA, items=(DIA, "#c8fffa"), r=R, pas=6)
    tube(s, [(-62, 14, -78), (-14, 14, -78), (-14, 14, -10)], DIA, items=(DIA, "#c8fffa"), r=R, pas=6)
    tube(s, [(52, 24, -86), (6, 24, -86), (6, 24, -12)], OR, items=(OR, "#fff4b0"), r=R, pas=6)
    tube(s, [(-86, 24, 52), (-86, 24, 6), (-12, 24, 6)], NET, items=(NET, "#ffc090"), r=R, pas=6)
    # sortie vers la bourse (gros tube violet)
    tube(s, [(12, 38, 0), (60, 38, 0), (60, 38, 40), (60, 8, 40)], AME, items=(AME, OR, DIA, NET, "#f0e0ff"), r=3.4, pas=5)
    s.add((48, 0, 44), (72, 30, 70), "#24202c", "pave"); lisere(s, 47.5, 29.5, 43.5, 72.5, 70.5)
    s.add((51, 6, 70), (69, 26, 70.6), AME, "runes"); s.add((52, 30, 48), (68, 34, 66), OR_, "dore")
    s.add((57, 34, 54), (63, 46, 60), "#ffe080", "lueur", rot={"y": 45, "origin": [60, 34, 57]})
    return s

def scene_hall():
    s = Scene()
    for i in range(0, 240, 16):
        for j in range(0, 250, 16):
            s.add((i - 10, -3, j - 10), (i + 6, -0.01, j + 6), "#34323a" if (i // 16 + j // 16) % 2 else "#2e2c34", "pave")
    haut_fourneau(s, 8, 8)
    puits_cristal(s, 160, 4, DIA)
    puits_cristal(s, 4, 168, OR)
    puits_cristal(s, 160, 168, NET)
    NX, NZ = 112, 112
    nexus(s, NX, NZ)
    # flux : fer, diamant, or, netherite vers le Nexus
    tube(s, [(52, 30, 30), (NX - 4, 30, 30), (NX - 4, 30, NZ - 12)], "#f0f0f6", items=(FER, "#ffffff", FER))
    tube(s, [(166, 24, 28), (NX + 4, 24, 28), (NX + 4, 24, NZ - 12)], DIA, items=(DIA, "#b8fff8"))
    tube(s, [(52, 24, 192), (NX - 4, 24, 192), (NX - 4, 24, NZ + 12)], OR, items=(OR, "#fff0a0"))
    tube(s, [(166, 24, 192), (NX + 4, 24, 192), (NX + 4, 24, NZ + 12)], NET, items=(NET, "#ffb080"))
    # deuxième tube parallèle (gros débit) sur le diamant
    tube(s, [(166, 18, 36), (NX + 10, 18, 36), (NX + 10, 18, NZ - 12)], DIA, items=(DIA, "#b8fff8"))
    # sortie du Nexus vers la raffinerie / bourse
    tube(s, [(NX + 12, 36, NZ), (150, 36, NZ), (150, 36, 140)], AME, items=(AME, "#e8d0ff", OR, DIA), r=2.2, pas=4)
    s.add((140, 0, 140), (160, 40, 156), "#24202c", "pave"); lisere(s, 139.5, 39.5, 139.5, 160.5, 156.5)
    s.add((143, 10, 156), (157, 34, 156.6), AME, "runes")
    s.add((144, 40, 144), (156, 44, 152), OR_, "dore")
    s.add((148, 44, 146), (152, 54, 150), "#ffe080", "lueur", rot={"y": 45, "origin": [150, 44, 148]})
    return s


# ---- scenes5.py
"""v5 : Halle de la Bourse (structure de marché obligatoire)."""
QUARTZ, QUARTZ2 = "#e6e0d2", "#cfc7b6"

def colonne(s, x, z, h, y=0):
    s.add((x - 2.4, y, z - 2.4), (x + 2.4, y + 2, z + 2.4), QUARTZ2, "pave")
    rond(s, x, y + 2, y + h - 3, z, 1.8, QUARTZ, "plat", n=3)
    s.add((x - 2.6, y + h - 3, z - 2.6), (x + 2.6, y + h - 1.5, z + 2.6), OR_, "dore")
    s.add((x - 2.2, y + h - 1.5, z - 2.2), (x + 2.2, y + h, z + 2.2), QUARTZ2, "pave")

def echoppe(s, x, z, col, marchandise):
    s.add((x, 0, z), (x + 12, 5, z + 8), BOIS, "planches")
    s.add((x + 0.5, 5, z + 0.5), (x + 11.5, 6, z + 7.5), PLANCHE, "planches")
    for i in range(4):
        s.add((x + 1 + i * 2.8, 6, z + 2), (x + 3 + i * 2.8, 7.4, z + 5), marchandise, "lueur" if i % 2 else "metal")
    for a in (0.4, 11.0):
        s.add((x + a, 5, z + 0.4), (x + a + 0.6, 13, z + 1.0), BOIS); s.add((x + a, 5, z + 7), (x + a + 0.6, 13, z + 7.6), BOIS)
    s.add((x - 1, 13, z - 1.5), (x + 13, 14, z + 9), col, "rayure", rot={"x": -12, "origin": [x, 13, z + 4]})

def halle(s, x0, z0):
    W, D = 72, 52
    # socle à degrés
    for i, (m, h) in enumerate(((0, 2), (2, 4), (4, 6))):
        s.add((x0 - 6 + m, h - 2, z0 - 10 + m), (x0 + W + 6 - m, h, z0 + D + 4 - m), QUARTZ2 if i != 1 else "#b8ae9a", "pave")
    lisere(s, x0 - 2.4, 5.4, z0 - 6.4, x0 + W + 2.4, z0 + D + 0.4)
    # corps
    s.add((x0, 6, z0), (x0 + W, 40, z0 + D), QUARTZ, "brique")
    s.add((x0 - 0.5, 40, z0 - 0.5), (x0 + W + 0.5, 43, z0 + D + 0.5), OR_, "dore")
    s.add((x0 - 1, 43, z0 - 1), (x0 + W + 1, 46, z0 + D + 1), QUARTZ2, "pave")
    # portique et colonnade avant (face z = z0)
    for i in range(7):
        colonne(s, x0 + 6 + i * 10, z0 - 6, 36, 6)
    s.add((x0 + 2, 42, z0 - 9), (x0 + W - 2, 46, z0), QUARTZ2, "pave")
    s.add((x0 + 2, 46, z0 - 9), (x0 + W - 2, 47, z0), OR_, "dore")
    for k in range(9):   # fronton à gradins
        m = k * 3.6
        s.add((x0 + 4 + m, 47 + k * 1.6, z0 - 8.5), (x0 + W - 4 - m, 48.6 + k * 1.6, z0 - 2), QUARTZ, "pave")
    s.add((x0 + 30, 52, z0 - 8.8), (x0 + 42, 58, z0 - 8.4), OR_, "dore")
    s.add((x0 + 33, 53.5, z0 - 9), (x0 + 39, 56.5, z0 - 8.8), "#ffe080", "lueur")
    # tableau des cours lumineux sur la façade
    s.add((x0 + 14, 14, z0 - 0.6), (x0 + 58, 36, z0), "#0e0c12", "plat")
    cols = [EME, RED, EME, EME, RED, OR, EME, RED]
    L = [30, 18, 36, 24, 12, 28, 34, 20]
    for i in range(8):
        y = 16 + i * 2.5
        s.add((x0 + 16, y, z0 - 0.9), (x0 + 22, y + 1.4, z0 - 0.6), "#f0f0f0", "lueur")
        s.add((x0 + 24, y, z0 - 0.9), (x0 + 24 + L[i], y + 1.4, z0 - 0.6), cols[i], "lueur")
    s.add((x0 + 13.4, 13.4, z0 - 1.2), (x0 + 58.6, 14, z0 - 0.4), OR_, "dore")
    s.add((x0 + 13.4, 36, z0 - 1.2), (x0 + 58.6, 36.6, z0 - 0.4), OR_, "dore")
    # dôme de verre et de cuivre
    cx, cz = x0 + W / 2, z0 + D / 2
    for i in range(6):
        r = 18 - i * 3
        rond(s, cx, 46 + i * 3, 49 + i * 3, cz, r, PATINE if i % 2 == 0 else "#6fc0a0", "cuivre" if i % 2 == 0 else "verre", n=4)
    rond(s, cx, 64, 66, cz, 4, OR_, "dore", n=4)
    s.add((cx - 1.5, 66, cz - 1.5), (cx + 1.5, 74, cz + 1.5), OR_, "dore", rot={"y": 45, "origin": [cx, 66, cz]})
    s.add((cx - 2, 74, cz - 2), (cx + 2, 78, cz + 2), "#ffe080", "lueur", rot={"y": 45, "x": 35, "origin": [cx, 76, cz]})
    # tours d'angle
    for (a, b) in ((-4, -4), (W - 8, -4), (-4, D - 8), (W - 8, D - 8)):
        s.add((x0 + a, 6, z0 + b), (x0 + a + 12, 54, z0 + b + 12), QUARTZ2, "brique")
        s.add((x0 + a - 0.5, 54, z0 + b - 0.5), (x0 + a + 12.5, 56, z0 + b + 12.5), OR_, "dore")
        rond(s, x0 + a + 6, 56, 64, z0 + b + 6, 4.5, PATINE, "cuivre", n=4)
        s.add((x0 + a + 5, 64, z0 + b + 5), (x0 + a + 7, 70, z0 + b + 7), OR_, "dore")
        s.add((x0 + a + 2, 30, z0 + b - 0.4), (x0 + a + 10, 46, z0 + b), "#1a1622", "plat")
        s.add((x0 + a + 3, 31, z0 + b - 0.6), (x0 + a + 9, 45, z0 + b - 0.3), AME, "runes")
    # quai de réception : tubes qui entrent par le côté droit, balance de pesée dorée
    s.add((x0 + W + 6, 0, z0 + 10), (x0 + W + 30, 14, z0 + 40), ARDO, "pave"); lisere(s, x0 + W + 5.6, 13.6, z0 + 9.6, x0 + W + 30.4, z0 + 40.4)
    bx, bz = x0 + W + 18, z0 + 25
    s.add((bx - 1, 14, bz - 1), (bx + 1, 30, bz + 1), OR_, "dore")
    s.add((bx - 12, 29, bz - 0.8), (bx + 12, 30.5, bz + 0.8), OR_, "dore")
    for sx, c in ((-1, DIA), (1, OR)):
        px = bx + sx * 11
        s.add((px - 0.3, 22, bz - 0.3), (px + 0.3, 29, bz + 0.3), "#5a4a30")
        s.add((px - 4, 20, bz - 4), (px + 4, 22, bz + 4), OR_, "dore")
        s.add((px - 2.4, 22, bz - 2.4), (px + 2.4, 25, bz + 2.4), c, "lueur", rot={"y": 45, "origin": [px, 22, bz]})
    tube(s, [(x0 + W + 56, 20, z0 + 16), (x0 + W + 30, 20, z0 + 16)], DIA, items=(DIA, "#c8fffa"), r=2.6, pas=5)
    tube(s, [(x0 + W + 56, 20, z0 + 25), (x0 + W + 30, 20, z0 + 25)], OR, items=(OR, "#fff4b0"), r=2.6, pas=5)
    tube(s, [(x0 + W + 56, 20, z0 + 34), (x0 + W + 30, 20, z0 + 34)], NET, items=(NET, "#ffc090"), r=2.6, pas=5)
    # échoppes devant (marché aux villageois) et coffres d'écus
    for i, (c, m) in enumerate((("#d04848", EME), ("#3a7fd0", FER), ("#e0a020", OR), ("#4aa050", DIA))):
        echoppe(s, x0 + 2 + i * 18, z0 - 34, c, m)
    for i in range(3):
        x = x0 + 22 + i * 10
        s.add((x, 6, z0 - 14), (x + 6, 10, z0 - 10), BOIS, "planches"); s.add((x - 0.3, 9, z0 - 14.3), (x + 6.3, 10, z0 - 9.7), OR_, "dore")
        s.add((x + 1, 10, z0 - 13), (x + 5, 11.5, z0 - 11), "#ffd040", "lueur")

def scene_halle():
    s = Scene()
    for i in range(-16, 144, 16):
        for j in range(-48, 64, 16):
            s.add((i, -3, j), (i + 16, -0.01, j + 16), "#3a3832" if (i // 16 + j // 16) % 2 else "#34322c", "pave")
    halle(s, 0, 0)
    return s


# ---- scenes6.py
"""v6 : Banque de l'Archipel (coffre-fort industriel)."""
OBS, OBS2 = "#1c1826", "#2a2436"

def pile_ecus(s, x, z, h, r=2.2):
    for i in range(h):
        rond(s, x + (0.25 if i % 2 else -0.25), i * 1.1, i * 1.1 + 1.0, z, r, OR, "dore", n=4)

def banque(s, x0, z0):
    W, D = 64, 48
    for i, (m, h) in enumerate(((0, 2), (2, 4), (4, 6))):
        s.add((x0 - 6 + m, h - 2, z0 - 12 + m), (x0 + W + 6 - m, h, z0 + D + 4 - m), OBS2 if i != 1 else "#3a3246", "pave")
    lisere(s, x0 - 2.4, 5.4, z0 - 8.4, x0 + W + 2.4, z0 + D + 0.4)
    for bx in range(0, W, 8):          # corps découpé pour que le tri du peintre ne mange pas la porte
        for by in range(6, 44, 8):
            s.add((x0 + bx, by, z0), (x0 + bx + 8, min(44, by + 8), z0 + D), OBS, "brique")
    s.add((x0 - 1, 44, z0 - 1), (x0 + W + 1, 47, z0 + D + 1), OR_, "dore")
    s.add((x0 + 2, 47, z0 + 2), (x0 + W - 2, 50, z0 + D - 2), OBS2, "pave")
    # porte de coffre géante sur la façade (z = z0)
    cx, cy, cz = x0 + W / 2, 24, z0 - 0.6
    for R, ep, col, mot in ((13.5, 2.2, OR_, "dore"), (11, 1.2, "#8a8a96", "metal"), (8.5, 1.6, OR_, "dore")):
        anneau(s, cx, cy, cz - 0.6, R, col, mot, n=28, ep=ep, plan="xy")
    engrenage(s, cx, cy, cz - 2.6, 6, OR_, dents=12, ep=1.6)
    for k in range(6):   # verrous
        s.add((cx - 0.6, cy + 7, cz - 2.2), (cx + 0.6, cy + 12, cz - 0.6), "#c8c8d0", "metal", rot={"z": k * 60, "origin": [cx, cy, cz]})
    s.add((cx - 1.6, cy - 1.6, cz - 3.4), (cx + 1.6, cy + 1.6, cz - 2.4), "#ffe080", "lueur")
    # colonnes d'obsidienne à chapiteau doré
    for x in (x0 + 4, x0 + 12, x0 + W - 12, x0 + W - 4):
        s.add((x - 2.2, 6, z0 - 8), (x + 2.2, 42, z0 - 3.6), "#2e2838", "pave")
        s.add((x - 2.6, 40, z0 - 8.4), (x + 2.6, 42.5, z0 - 3.2), OR_, "dore")
        s.add((x - 0.6, 10, z0 - 8.3), (x + 0.6, 38, z0 - 8.0), AME, "lueur")
    s.add((x0 + 1, 42.5, z0 - 9), (x0 + W - 1, 46, z0), OBS2, "pave"); s.add((x0 + 1, 46, z0 - 9), (x0 + W - 1, 47, z0), OR_, "dore")
    # vitrines de lingots de chaque côté de la porte
    for vx in (x0 + 4, x0 + W - 18):
        for i in range(5):
            for j in range(2):
                c = (OR, DIA, EME, FER, NET)[i]
                s.add((vx + 0.8 + i * 2.7, 10.4 + j * 2.6, z0 - 1.2), (vx + 2.8 + i * 2.7, 11.8 + j * 2.6, z0 - 0.3), c, "lueur" if j else "metal")
    # tours de pièces d'or sur le toit
    for (px, pz, h) in ((x0 + 10, z0 + 10, 9), (x0 + 18, z0 + 8, 6), (x0 + W - 10, z0 + 10, 11), (x0 + W - 18, z0 + 12, 7), (x0 + 12, z0 + D - 10, 8), (x0 + W - 12, z0 + D - 10, 10)):
        for i in range(h):
            rond(s, px + (0.3 if i % 2 else -0.3), 50 + i * 1.2, 51.1 + i * 1.2, pz, 3, OR, "dore", n=4)
    # dôme de verre au-dessus de la salle des coffres, avec un énorme lingot flottant
    gx, gz = x0 + W / 2, z0 + D / 2
    for i in range(4):
        rond(s, gx, 50 + i * 3, 53 + i * 3, gz, 12 - i * 3, "#9fe0ff" if i % 2 else AME, "verre" if i % 2 else "runes", n=4)
    s.add((gx - 5, 66, gz - 2.5), (gx + 5, 70, gz + 2.5), OR, "lueur", rot={"y": 30, "origin": [gx, 68, gz]})
    anneau(s, gx, 68, gz, 9, OR_, "dore", n=20)
    # tubes du Nexus qui entrent par le côté
    for k, (c, it) in enumerate(((DIA, "#c8fffa"), (OR, "#fff4b0"), (FER, "#ffffff"), (AME, "#e8d0ff"))):
        tube(s, [(x0 + W + 46, 14 + k * 7, z0 + 12 + k * 7), (x0 + W, 14 + k * 7, z0 + 12 + k * 7)], c, items=(c, it), r=2.2, pas=5)
    # sacs et charrettes d'écus devant
    for i, (px, pz) in enumerate(((x0 + 22, z0 - 20), (x0 + 30, z0 - 22), (x0 + 38, z0 - 20))):
        pile_ecus(s, px, pz, 4 + i * 2)

def scene_banque():
    s = Scene()
    for i in range(-16, 112, 16):
        for j in range(-32, 64, 16):
            s.add((i, -3, j), (i + 16, -0.01, j + 16), "#2c2a30" if (i // 16 + j // 16) % 2 else "#26242a", "pave")
    banque(s, 0, 0)
    return s



# =====================================================================================================
# Bâtiments ajoutés pour le pack (27/11/2026). Emprise d'environ 48 x 48 unités, posés à l'origine.
# =====================================================================================================
PIERRE2, ACIER, VERRE = "#6a6670", "#8a9098", "#bfe8ff"

def socle(s, w, d, col="#2a2630", h=4):
    s.add((0, 0, 0), (w, h, d), col, "pave"); lisere(s, -0.4, h - 0.6, -0.4, w + 0.4, d + 0.4)

def carriere(s):
    """Carrière automatique : fosse à gradins, bras de forage, wagonnets de pierre, charbon et cuivre."""
    socle(s, 48, 48, ARDO)
    for i in range(4):   # gradins de la fosse
        m = 6 + i * 4
        s.add((m, 4 - i * 0.01, m), (48 - m, 4.5, 48 - m), ("#5a5660", "#4a4650", "#3e3a44", "#2c2830")[i], "minerai")
    for (x, z) in ((4, 4), (40, 4), (4, 40), (40, 40)):
        s.add((x, 4, z), (x + 4, 34, z + 4), FERS, "metal"); s.add((x - 0.5, 34, z - 0.5), (x + 4.5, 36, z + 4.5), OR_, "dore")
    s.add((4, 34, 4), (44, 37, 8), FERS, "metal"); s.add((4, 34, 40), (44, 37, 44), FERS, "metal")
    s.add((20, 30, 4), (28, 38, 44), "#3a3a44", "metal")                  # chariot du pont roulant
    s.add((22.5, 6, 22.5), (25.5, 30, 25.5), ACIER, "metal")               # tige de forage
    for k in range(5):
        s.add((21 - k * 0.3, 6 + k * 4, 21 - k * 0.3), (27 + k * 0.3, 7 + k * 4, 27 + k * 0.3), OR_, "dore", rot={"y": k * 18, "origin": [24, 6, 24]})
    s.add((22, 5, 22), (26, 8, 26), "#ffb040", "lave")
    for i, (c, m) in enumerate((("#8e8984", "pave"), ("#2a2a30", "minerai"), (CUIV, "cuivre"))):
        x = 6 + i * 13
        s.add((x, 4, 2), (x + 10, 9, 10), BOIS, "planches"); s.add((x + 1, 9, 3), (x + 9, 12, 9), c, m)
        s.add((x + 1, 4, 1.6), (x + 3, 6, 2), "#222222", "metal"); s.add((x + 7, 4, 1.6), (x + 9, 6, 2), "#222222", "metal")

def serre(s):
    """Serre hydroponique : verrière à arceaux de cuivre, bacs lumineux de cannes, verrues et citrouilles."""
    socle(s, 48, 40, "#3a3226")
    for z in range(4, 37, 8):
        for x in (4, 44):
            s.add((x - 1, 4, z - 1), (x + 1, 26, z + 1), PATINE, "cuivre")
        s.add((3, 26, z - 1), (45, 28, z + 1), PATINE, "cuivre")
    for z0 in range(4, 36, 8):
        s.add((5, 27, z0), (43, 28.5, z0 + 8), "#9fe8ff", "verre")
    for i, (c, h) in enumerate((("#7ad050", 14), ("#a01828", 6), ("#e08a20", 5))):
        z = 8 + i * 10
        s.add((7, 4, z), (41, 7, z + 6), "#5a4030", "planches"); s.add((7.5, 7, z + 0.5), (40.5, 7.6, z + 5.5), "#3fa0e0", "lueur")
        for k in range(8):
            x = 9 + k * 4
            if i == 0: s.add((x, 7.6, z + 2), (x + 1.4, 7.6 + h, z + 3.4), c, "bruit")
            elif i == 1: s.add((x, 7.6, z + 1.5), (x + 2, 7.6 + h, z + 4), c, "bruit")
            else: s.add((x - 0.5, 7.6, z + 1), (x + 2.5, 10.6, z + 4), c, "rayure")
    s.add((20, 28.5, 16), (28, 34, 24), OR_, "dore"); s.add((21.5, 29, 15.8), (26.5, 33, 24.2), "#ffe080", "lueur")

def chaudiere(s):
    """Chaudière à charbon : cuve de fer rivetée, foyer rougeoyant, cheminée et manomètre doré."""
    socle(s, 32, 32, ARDO)
    rond(s, 16, 4, 26, 16, 10, "#4a4a52", "metal", n=4)
    for y in (8, 16, 24): rond(s, 16, y, y + 1.2, 16, 10.4, OR_, "dore", n=4)
    s.add((11, 5, 5.2), (21, 12, 6), "#ff6a10", "lave")
    rond(s, 22, 26, 46, 22, 2.6, "#3a3a40", "metal", n=3); s.add((19, 46, 19), (25, 48, 25), OR_, "dore")
    s.add((5, 18, 13), (6, 22, 19), "#f0e0c0", "plat"); s.add((4.6, 17.6, 12.6), (5.2, 22.4, 19.4), OR_, "dore")

def centrale_lave(s):
    """Centrale à lave : bassin de lave, turbine à pales dorées, colonnes de basalte."""
    socle(s, 44, 44, "#2a2228")
    s.add((6, 4, 6), (38, 6, 38), "#3a2a2a", "pave"); s.add((8, 4.5, 8), (36, 6.2, 36), "#ff5a10", "lave")
    for (x, z) in ((4, 4), (36, 4), (4, 36), (36, 36)):
        s.add((x, 4, z), (x + 4, 30, z + 4), "#3c3640", "brique"); s.add((x - 0.5, 30, z - 0.5), (x + 4.5, 32, z + 4.5), OR_, "dore")
    rond(s, 22, 6, 22, 22, 4, "#4a4a52", "metal", n=4)
    for k in range(6):
        s.add((21, 18, 22 - 0.5), (35, 20, 22 + 0.5), OR_, "dore", rot={"y": k * 60, "origin": [22, 19, 22]})
    s.add((18, 22, 18), (26, 26, 26), "#ffd060", "lueur")
    anneau(s, 22, 24, 22, 13, "#ff8a30", "lueur", n=20, ep=0.8)

def coeur_stellaire(s):
    """Cœur stellaire : étoile du Nether en lévitation dans trois anneaux, socle d'obsidienne."""
    socle(s, 40, 40, "#1c1826")
    s.add((10, 4, 10), (30, 10, 30), "#2a2436", "pave"); lisere(s, 9.6, 9.4, 9.6, 30.4, 30.4)
    for (x, z) in ((6, 6), (32, 6), (6, 32), (32, 32)):
        s.add((x, 4, z), (x + 2, 28, z + 2), "#2e2a36", "pave"); s.add((x - 0.4, 22, z - 0.4), (x + 2.4, 26, z + 2.4), "#fff6c0", "lueur")
    c = (20, 26, 20)
    s.add((c[0] - 4, c[1] - 4, c[2] - 4), (c[0] + 4, c[1] + 4, c[2] + 4), "#fffbe0", "lueur", rot={"y": 45, "x": 35, "origin": list(c)})
    for R, t in ((9, 0), (11, 60), (13, -50)):
        anneau(s, *c, R, OR_ if t == 0 else "#fff0a0", "dore" if t == 0 else "lueur", n=22, ep=0.8, tilt=t)
    s.add((19, 10, 19), (21, 22, 21), "#fff6c0", "lueur")

def fonderie(s):
    """Fonderie : creuset basculant de métal en fusion, coulée vers des moules à lingots d'acier."""
    socle(s, 48, 40, ARDO)
    s.add((4, 4, 6), (22, 30, 34), "#5a4a44", "brique"); s.add((3.6, 30, 5.6), (22.4, 32, 34.4), OR_, "dore")
    s.add((8, 8, 5.6), (18, 16, 6.2), "#ff7a20", "lave")
    rond(s, 32, 14, 24, 20, 6, "#3a3a40", "metal", n=4, )
    s.add((27, 23.5, 15), (37, 24.6, 25), "#ffb040", "lave")
    s.add((37, 18, 19), (44, 19, 21), "#ffa040", "lave", rot={"z": -20, "origin": [37, 18, 20]})
    for i in range(3):
        x = 26 + i * 7
        s.add((x, 4, 30), (x + 6, 7, 36), ARDO, "pave"); s.add((x + 0.7, 7, 30.7), (x + 5.3, 8.4, 35.3), ACIER, "metal")
    rond(s, 10, 32, 50, 12, 2.4, CUIV, "cuivre", n=3)

def atelier_meca(s):
    """Atelier mécanique : halle à toit en dents de scie, grands engrenages en façade, bras articulé."""
    socle(s, 48, 40, ARDO)
    s.add((4, 4, 4), (44, 22, 36), "#5a5660", "brique")
    for k in range(4):
        x = 4 + k * 10
        s.add((x, 22, 4), (x + 10, 30, 36), "#4a4650", "metal", rot={"z": -20, "origin": [x, 22, 20]})
        s.add((x + 7.6, 22, 4.2), (x + 9.6, 29, 35.8), "#9fe8ff", "verre")
    engrenage(s, 14, 13, 3.0, 7, OR_, dents=12); engrenage(s, 27, 10, 3.2, 5, CUIV, dents=10); engrenage(s, 37, 15, 3.0, 4, OR_, dents=9)
    s.add((44, 4, 14), (48, 26, 18), "#3a3a44", "metal"); s.add((44, 24, 15), (60, 26, 17), "#3a3a44", "metal", rot={"z": -25, "origin": [46, 25, 16]})

def joaillerie(s):
    """Joaillerie : pavillon de marbre à coupole, vitrines de bijoux lumineux, diamant géant sur la flèche."""
    socle(s, 44, 44, "#d8d0c0")
    s.add((6, 4, 6), (38, 22, 38), "#ece6da", "brique")
    for (x, z) in ((6, 6), (34, 6), (6, 34), (34, 34)):
        s.add((x - 1, 4, z - 1), (x + 5, 26, z + 5), "#d8d0c0", "pave"); s.add((x - 1.4, 26, z - 1.4), (x + 5.4, 27.4, z + 5.4), OR_, "dore")
    s.add((5.6, 22, 5.6), (38.4, 24, 38.4), OR_, "dore")
    for i in range(4):
        rond(s, 22, 24 + i * 3, 27 + i * 3, 22, 12 - i * 3, "#e8dcff" if i % 2 else OR_, "verre" if i % 2 else "dore", n=4)
    c = (22, 42, 22)
    s.add((c[0] - 3, c[1] - 3, c[2] - 3), (c[0] + 3, c[1] + 3, c[2] + 3), DIA, "lueur", rot={"y": 45, "x": 35, "origin": list(c)})
    for i, col in enumerate((OR, DIA, EME, AME)):
        x = 9 + i * 7
        s.add((x, 8, 5.4), (x + 5, 14, 6), "#202028", "plat"); s.add((x + 1, 9, 5.0), (x + 4, 12, 5.6), col, "lueur")

def forge_reliques(s):
    """Forge des reliques : enclume titanesque sur un autel de netherite, braises violettes, relique en lévitation."""
    socle(s, 48, 48, "#1c1820")
    for i, m in enumerate((4, 8, 12)):
        s.add((m, 4 + i * 4, m), (48 - m, 8 + i * 4, 48 - m), ("#2c2630", "#3a2a2e", "#24202a")[i], "pave")
        lisere(s, m - 0.4, 7.4 + i * 4, m - 0.4, 48 - m + 0.4, 48 - m + 0.4)
    s.add((16, 16, 20), (32, 20, 28), "#3a3640", "metal"); s.add((19, 20, 21.5), (29, 24, 26.5), "#4a4650", "metal")
    s.add((12, 24, 19), (36, 28, 29), "#3a3640", "metal")
    for (x, z) in ((6, 6), (38, 6), (6, 38), (38, 38)):
        s.add((x, 4, z), (x + 4, 36, z + 4), "#2a2230", "brique")
        s.add((x + 0.5, 36, z + 0.5), (x + 3.5, 40, z + 3.5), "#c070ff", "lave")
    c = (24, 38, 24)
    s.add((c[0] - 3, c[1] - 6, c[2] - 1), (c[0] + 3, c[1] + 6, c[2] + 1), "#ffd060", "lueur", rot={"y": 30, "origin": list(c)})
    anneau(s, *c, 9, "#c070ff", "lueur", n=20, ep=0.7, tilt=60); anneau(s, *c, 11, OR_, "dore", n=22)

def laboratoire(s):
    """Laboratoire : tour d'observation à coupole, lunette, bobines de Tesla et fioles."""
    socle(s, 40, 40, ARDO)
    rond(s, 20, 4, 30, 20, 11, "#4a4658", "brique", n=4)
    for y in (12, 22): rond(s, 20, y, y + 1, 20, 11.4, OR_, "dore", n=4)
    for i in range(3): rond(s, 20, 30 + i * 3, 33 + i * 3, 20, 10 - i * 3, PATINE, "cuivre", n=4)
    s.add((18, 36, 18), (34, 39, 22), "#3a3a44", "metal", rot={"z": 30, "origin": [20, 37, 20]}); s.add((32, 42, 18.5), (35, 45, 21.5), "#9fe8ff", "lueur")
    for (x, z) in ((5, 5), (35, 5)):
        rond(s, x, 4, 16, z, 1.6, CUIV, "cuivre", n=3); s.add((x - 2, 16, z - 2), (x + 2, 19, z + 2), "#80e0ff", "lueur")
    for i, c in enumerate((RED, AME, EME)):
        s.add((14 + i * 5, 6, 8.4), (17 + i * 5, 11, 9.2), c, "lueur")

def comptoir_marche(s):
    """Échoppe et Comptoir (Halle niveaux 1 et 2) : estrade, deux étals à rayures, balance dorée."""
    socle(s, 40, 32, "#4a3a2a", h=3)
    echoppe(s, 2, 14, "#d04848", EME); echoppe(s, 22, 14, "#3a7fd0", OR)
    bx, bz = 20, 8
    s.add((bx - 0.6, 3, bz - 0.6), (bx + 0.6, 16, bz + 0.6), OR_, "dore"); s.add((bx - 8, 15.5, bz - 0.5), (bx + 8, 16.5, bz + 0.5), OR_, "dore")
    for sx, c in ((-1, DIA), (1, OR)):
        px = bx + sx * 7
        s.add((px - 3, 10, bz - 3), (px + 3, 11, bz + 3), OR_, "dore"); s.add((px - 1.6, 11, bz - 1.6), (px + 1.6, 13, bz + 1.6), c, "lueur")
    for i in range(3):
        pile_ecus(s, 6 + i * 4, 4, 2 + i)

def monument(s):
    """Grand Œuvre : obélisque d'or et d'obsidienne à pointe lumineuse."""
    socle(s, 24, 24, "#1c1826")
    s.add((6, 4, 6), (18, 8, 18), "#2a2436", "pave")
    for i in range(6):
        m = 8 + i * 0.6
        s.add((m, 8 + i * 8, m), (24 - m, 16 + i * 8, 24 - m), "#2a2436" if i % 2 else OR_, "brique" if i % 2 else "dore")
    s.add((10.5, 56, 10.5), (13.5, 64, 13.5), "#fff0a0", "lueur", rot={"y": 45, "origin": [12, 56, 12]})

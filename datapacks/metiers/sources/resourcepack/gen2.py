"""Refonte : 11 paliers pour chaque outil de métier + arcs du Chasseur.
Les heaumes et les épées des paliers 0, 5 et 9 validés sont repris tels quels depuis gen.py."""
import os, sys, json, math, re
import numpy as np
from PIL import Image
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else "."]
import gen
from gen import Model, mirror, tip, hx, R, save, sword_display, epee_0, epee_5, epee_9, heaume_3, heaume_5, OUT

# ------------------------------------------------------------------ palettes des 11 paliers (reprises de textures.py)
src = open("/home/claude/katjounis/minecraft-metiers/sources/textures.py").read()
OLD = eval(src[src.index("TIERS = [") + 8: src.index("]\n\n# ----") + 1], {"dict": dict})
# Progression calée sur le datapack : fer (palier 0), diamant (1 à 4), netherite (5 à 10).
IRON = ["#25262b", "#5d6169", "#8d929b", "#bcc1c9", "#eef1f5"]
DIAM = ["#0a3238", "#17838c", "#33c4cb", "#8cefed", "#f2ffff"]
NETH = ["#0e0b0d", "#221c20", "#332a30", "#4a3e45", "#75666e"]
GOLD = ["#6b4a0b", "#c9972a", "#ffe08a"]
WOOD = ["#2e1d0e", "#5c3a1d", "#7f532c", "#a3713f"]
LEATH_D = ["#1b1622", "#352b44", "#4e4063", "#6a5885"]
LEATH_N = ["#160f0f", "#2f2020", "#463030", "#5e4242"]
VOID = ["#2a0a4a", "#8a3cff", "#e8d0ff"]
TIERS = [
    dict(name="diamant", head=DIAM, handle=LEATH_D, trim=["#3d4046", "#8d929b", "#d8dce2"], band=["#1b2346", "#2f3d7a", "#4b5fb3"], gem=["#0a3238", "#33c4cb", "#f2ffff"]),
    dict(name="diamant_forge", head=DIAM, handle=LEATH_D, trim=GOLD, band=["#1b2346", "#2f3d7a", "#4b5fb3"], gem=["#0d2f63", "#2f6fe0", "#bfe0ff"]),
    dict(name="netherite", head=NETH, handle=LEATH_N, trim=GOLD, band=["#2a2026", "#3e3038", "#57444f"], gem=["#6b4a0b", "#ffc83a", "#fff1b0"]),
    dict(name="netherite_epines", head=NETH, handle=LEATH_N, trim=GOLD, band=["#3d0c0c", "#6e1717", "#9c2424"], gem=["#4d0a0a", "#d42a2a", "#ffb3b3"]),
    dict(name="netherite_amethyste", head=NETH, handle=LEATH_N, trim=GOLD, band=["#2b1b3d", "#4b2f6b", "#6d47a0"], gem=["#3b1060", "#a35cf0", "#efd9ff"], crystals=["#5f2d91", "#b787ec", "#f3e7ff"]),
    dict(name="netherite_braise", head=NETH, handle=LEATH_N, trim=GOLD, band=["#3d0c0c", "#6e1717", "#9c2424"], gem=["#7a2a08", "#ff8a2e", "#ffe0b0"], crystals=["#7a2a08", "#ff8a2e", "#ffe0b0"]),
    dict(name="netherite_rubis", head=NETH, handle=LEATH_N, trim=GOLD, band=["#3d0c0c", "#6e1717", "#9c2424"], gem=["#5e0808", "#ff3030", "#ffd0d0"]),
    dict(name="netherite_runique", head=NETH, handle=["#0c0a12", "#1d1828", "#2e2740", "#433a5a"], trim=GOLD, band=["#0d3a44", "#167585", "#2fc2d6"], gem=["#0b4552", "#2fe6ff", "#d6fbff"], rune="#4ff0ff"),
    dict(name="netherite_vide", head=NETH, handle=["#0c0a12", "#1d1828", "#2e2740", "#433a5a"], trim=["#3a1c5e", "#8a3cff", "#e8d0ff"], band=["#1e0a36", "#3a1660", "#5a2a90"], gem=VOID, crystals=VOID, rune="#b07cff"),
    OLD[9], OLD[10],
]
NOMS = ["Diamant", "Diamant forgé", "Netherite", "Netherite épineuse", "Netherite d'améthyste", "Netherite de braise",
        "Netherite rubis", "Netherite runique", "Netherite du Vide", "Mythique", "Dieu"]

def light(c, k=0.45): return c + (255 - c) * k
def dark(c, k=0.45): return c * (1 - k)

def palette(k):
    T = TIERS[k]
    head = R(T["head"])
    hand = R(T["handle"])
    trim = R(T["trim"]) if T.get("trim") else (R(T["band"]) if T.get("band") else [dark(head[1]), head[1], head[2]])
    gem = R(T["gem"]) if T.get("gem") else [head[1], head[2], head[3]]
    band = R(T["band"]) if T.get("band") else [dark(hand[1]), hand[1], hand[2]]
    glow_src = T.get("crystals") or T.get("gem") or T["head"][2:]
    g = R(glow_src)
    if T.get("rune"): g = [dark(hx(T["rune"]), .5), hx(T["rune"]), light(hx(T["rune"]), .7)]
    if k == 10: g = R(["#e0a020", "#fff1a0", "#ffffff"])
    return dict(metal=[head[0], head[1], head[2], head[3], head[4], light(head[4], .6)], blade=head, grip=hand,
                trim=[dark(trim[0], .3), trim[0], trim[1], trim[2]], gem=[gem[0], gem[1], gem[2], light(gem[2], .7)],
                cloth=[dark(band[0], .3), band[0], band[1], band[2]], glow=[g[1], light(g[1], .35), light(g[2], .6)],
                feather=[head[2], head[3], head[4], light(head[4], .6)], rune=hx(T.get("rune", "#ffffff")) if T.get("rune") else light(gem[2], .5))

# ------------------------------------------------------------------ briques communes
def seg2d(m, start, segs, mats, depth=None, mir=False, zc=8.0):
    """Chaîne de segments dans le plan xy ; chaque segment = (longueur, épaisseur, angle en degrés depuis +x)."""
    x, y = start
    pts = []
    for (L, th, a), mat in zip(segs, mats):
        ar = math.radians(a)
        cx, cy = x + math.cos(ar) * L / 2, y + math.sin(ar) * L / 2
        d = depth if depth else th
        frm = (cx - L / 2 - 0.12, cy - th / 2, zc - d / 2); to = (cx + L / 2 + 0.12, cy + th / 2, zc + d / 2)
        rot = dict(z=round(a, 2), origin=[round(cx, 3), round(cy, 3), zc])
        (mirror(m, frm, to, mat, rot) if mir else m.add(frm, to, mat, rot))
        x, y = x + math.cos(ar) * L, y + math.sin(ar) * L
        pts.append((x, y))
    return pts

def diamond(m, cx, cy, size, mat, zc=8.0, depth=None, extra_rot=None):
    s = size / math.sqrt(2); d = depth or s
    rot = dict(z=45, origin=[cx, cy, zc])
    if extra_rot: rot.update(extra_rot)
    m.add((cx - s / 2, cy - s / 2, zc - d / 2), (cx + s / 2, cy + s / 2, zc + d / 2), mat, rot)

def ring_y(m, cx, cy, cz, Rr, n=10, th=0.5):
    """Anneau lumineux horizontal (autour d'un axe vertical)."""
    for k in range(n):
        t = 2 * math.pi * k / n
        px, pz = cx + Rr * math.cos(t), cz + Rr * math.sin(t)
        L = 2 * Rr * math.tan(math.pi / n) + 0.1
        m.add((px - L / 2, cy - th / 2, pz - th / 2), (px + L / 2, cy + th / 2, pz + th / 2), "glow", dict(y=-(math.degrees(t) + 90), origin=[px, cy, pz]))

def ring_z(m, cx, cy, Rr, n=12, th=0.5, zc=8.0):
    """Anneau lumineux vertical, dans le plan de l'outil."""
    for k in range(n):
        t = 2 * math.pi * k / n
        px, py = cx + Rr * math.cos(t), cy + Rr * math.sin(t)
        L = 2 * Rr * math.tan(math.pi / n) + 0.1
        m.add((px - L / 2, py - th / 2, zc - th / 2), (px + L / 2, py + th / 2, zc + th / 2), "glow", dict(z=math.degrees(t) + 90, origin=[px, py, zc]))

def manche(m, k, y0, y1, w=1.4):
    a, b = 8 - w / 2, 8 + w / 2
    m.add((a, y0, a), (b, y1, b), "grip", name="manche")
    if k >= 1:
        for yy in (y0 + 1.0, (y0 + y1) / 2):
            m.add((a - 0.25, yy, a - 0.25), (b + 0.25, yy + 0.7, b + 0.25), "trim")
    m.add((a - 0.35, y0 - 1.2, a - 0.35), (b + 0.35, y0, b + 0.35), "plate")
    if 1 <= k <= 8:
        diamond(m, 8, y0 - 2.0, 1.8 + 0.1 * k, "glow")
    if k >= 3:
        for yy in (y0 + 2.4, y1 - 1.6):
            mirror(m, (a - 0.9, yy, 7.6), (a - 0.3, yy + 1.2, 8.4), "edge", dict(z=-35, origin=[a - 0.3, yy, 8]))
    if k >= 9:
        m.add((7.0, y0 - 3.2, 7.0), (9.0, y0 - 1.2, 9.0), "glow", dict(x=35, y=45, origin=[8, y0 - 2.2, 8]))

def socket(m, k, cx, cy, zf, zb):
    """Gemme sertie des deux côtés de la tête (paliers 1+)."""
    if k < 1: return
    mat = "glow"
    for z0, z1 in ((zf - 0.5, zf + 0.05), (zb - 0.05, zb + 0.5)):
        m.add((cx - 1.2, cy - 1.2, z0), (cx + 1.2, cy + 1.2, z1), "trim")
    for z0, z1 in ((zf - 0.85, zf - 0.4), (zb + 0.4, zb + 0.85)):
        m.add((cx - 0.7, cy - 0.7, z0), (cx + 0.7, cy + 0.7, z1), mat, dict(z=45, origin=[cx, cy, (z0 + z1) / 2]))

def crystals(m, k, spots):
    """Cristaux en losanges inclinés (paliers 4+) : jamais de barres verticales."""
    if k < 4: return
    for (x, y, a, s) in spots:
        s *= 1.3
        m.add((x - s * 0.35, y, 7.55), (x + s * 0.35, y + s, 8.45), "glow", dict(z=a, origin=[x, y, 8]))
        diamond(m, x - math.sin(math.radians(a)) * s, y + math.cos(math.radians(a)) * s, s * 0.6, "glow")

def floaters(m, k, spots):
    """Éclats détachés qui flottent autour de la tête (paliers 6+)."""
    if k < 6: return
    for (x, y) in spots:
        diamond(m, x, y, 1.7 if k < 9 else 2.0, "glow", extra_rot=dict(y=30))

def tool_display(scale, grip_y):
    d = sword_display(scale, grip_y)
    d["gui"] = {"rotation": [0, 0, -45], "translation": [0, 0, 0], "scale": [0.5, 0.5, 0.5]}
    return d

def size(k): return 1 + 0.035 * k

def renfort(m, k, cx, cy, hw, h=4.0):
    """Plaques de renfort inclinées de part et d'autre de la tête (paliers 2+)."""
    if k < 2: return
    mirror(m, (cx - hw - 1.4, cy - h / 2, 6.9), (cx - hw, cy + h / 2, 9.1), "plate", dict(z=-14, origin=[cx - hw, cy, 8]))
    mirror(m, (cx - hw - 1.6, cy - h / 2 - 0.4, 6.8), (cx - hw - 1.2, cy + h / 2 + 0.4, 9.2), "trim", dict(z=-14, origin=[cx - hw, cy, 8]))

def epines(m, k, spots):
    """Pointes qui changent la silhouette (paliers 3+), plus longues aux paliers hauts."""
    if k < 3: return
    g = 1 + 0.08 * (k - 3)
    for (x, y, a) in spots:
        seg2d(m, (x, y), [(1.8 * g, 1.3, a), (1.6 * g, 0.8, a + 12)], ["plate", "edge"], depth=0.9)

def veines(m, k, x0, y0, x1, y1, zf, zb):
    """Veines lumineuses sur les grandes faces (paliers 5+)."""
    if k < 5: return
    L = math.hypot(x1 - x0, y1 - y0); a = math.degrees(math.atan2(y1 - y0, x1 - x0)); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for z0, z1 in ((zf - 0.2, zf), (zb, zb + 0.2)):
        m.add((cx - L / 2, cy - 0.4, z0), (cx + L / 2, cy + 0.4, z1), "glow", dict(z=a, origin=[cx, cy, (z0 + z1) / 2]))

# ------------------------------------------------------------------ pioche (Mineur)
def pioche(k, P):
    """0-1 arc classique, 2-3 lourde à pointes, 4-5 bras terminés par un cristal, 6-7 bras fendus en deux dents,
    8+ pointes détachées qui flottent."""
    m = Model(f"m_{k}", P); s = size(k)
    manche(m, k, -6, 14)
    m.add((6.6, 12.6, 6.6), (9.4, 16.4, 9.4), "plate", name="collier")
    th = 1.0 + (0.25 if k >= 2 else 0)
    segs = [(3.2 * s, 2.6 * th, 170), (3.2 * s, 2.2 * th, 195), (3.0 * s, 1.8 * th, 218)]
    mats = ["plate", "plate", "plate"]
    if k < 4 or k >= 8:
        segs.append((2.6 * s, 1.3, 242)); mats.append("edge")
    pts = seg2d(m, (7.0, 15.0), segs, mats, depth=1.8 + (0.4 if k >= 2 else 0), mir=True)
    ex, ey = pts[-1]
    if 4 <= k <= 5:
        for sx in (1, -1):
            x = ex if sx == 1 else 16 - ex
            m.add((x - 1.0, ey - 3.4 * s, 7.2), (x + 1.0, ey, 8.8), "glow", dict(z=-24 * sx, origin=[x, ey, 8]))
            diamond(m, x - 1.2 * sx, ey - 3.6 * s, 2.0, "glow")
    if 6 <= k <= 7:
        for sx in (1, -1):
            x = ex if sx == 1 else 16 - ex
            for d, L in ((-30, 3.4), (14, 2.8)):
                seg2d(m, (x, ey), [(L * s, 1.1, 242 + d if sx == 1 else 298 - d)], ["edge"], depth=1.4)
    if k >= 8:
        for sx in (1, -1):
            x = ex if sx == 1 else 16 - ex
            diamond(m, x - 1.0 * sx, ey - 3.0, 2.2, "glow", extra_rot=dict(y=30))
    if k >= 2: m.add((6.3, 14.2, 6.3), (9.7, 15.0, 9.7), "trim")
    socket(m, k, 8, 14.5, 6.6, 9.4)
    renfort(m, k, 8, 14.4, 1.4, 3.6)
    epines(m, k, [(8, 16.4, 90), (5.0, 16.0 + 0.3 * th, 125), (11.0, 16.0 + 0.3 * th, 55)])
    veines(m, k, 4.6, 14.6, 11.4, 14.6, 6.55, 9.45)
    floaters(m, k, [(8, 21.0 + 0.3 * k)] + ([(3.0, 19.0), (13.0, 19.0)] if k >= 7 else []))
    if k >= 8: ring_y(m, 8, 11.6, 8, 2.6 + 0.4 * (k - 8), n=10)
    if k == 10: rays(m, 8, 16.4)
    return m.build(tool_display(0.62, 4))

def rays(m, cx, y0):
    for a, L in ((-50, 2.6), (-25, 3.4), (0, 4.2), (25, 3.4), (50, 2.6)):
        m.add((cx - 0.4, y0, 7.6), (cx + 0.4, y0 + L, 8.4), "trim", dict(z=-a, origin=[cx, y0, 8]))

# ------------------------------------------------------------------ hache (Bûcheron)
def hache(k, P):
    m = Model(f"b_{k}", P); s = size(k)
    manche(m, k, -6, 15.5)
    h = 6.6 + 0.55 * k
    yb = 15.0 - h / 2 + 0.6
    def lame(mm, x_in):
        cy = yb + h / 2
        mm.add((x_in - 2.0 * s, cy - h * 0.28, 7.55), (x_in, cy + h * 0.28, 8.45), "blade")
        mm.add((x_in - 3.6 * s, cy - h * 0.40, 7.5), (x_in - 2.0 * s, cy + h * 0.40, 8.5), "blade")
        mm.add((x_in - 4.9 * s, yb, 7.5), (x_in - 3.6 * s, yb + h, 8.5), "runeblade" if k >= 7 else "blade")
        mm.add((x_in - 5.8 * s, yb - 0.4, 7.35), (x_in - 4.9 * s, yb + h + 0.4, 8.65), "edge")
        mm.add((x_in - 4.9 * s, yb + h - 0.2, 7.45), (x_in - 3.0 * s, yb + h + 0.7, 8.55), "edge", dict(z=-28, origin=[x_in - 4.9 * s, yb + h, 8]))
        mm.add((x_in - 4.9 * s, yb - 0.7, 7.45), (x_in - 3.0 * s, yb + 0.2, 8.55), "edge", dict(z=28, origin=[x_in - 4.9 * s, yb, 8]))
    lame(m, 7.0)
    if 4 <= k <= 5:
        seg2d(m, (7.0 - 4.9 * s, yb), [(2.4 * s, 1.4, 250), (2.0 * s, 1.0, 300)], ["blade", "edge"], depth=1.0)
    if k >= 6:
        mm = Model("tmp", P); lame(mm, 7.0)
        for e in mm.els:
            mirror_only(m, e)
    else:
        m.add((9.0, 12.6, 7.2), (10.8, 16.6, 8.8), "plate", name="talon")
        if k >= 3: seg2d(m, (10.8, 14.6), [(2.6 * size(k), 1.6, 12), (2.2 * size(k), 1.1, 30)], ["plate", "edge"], depth=1.2)
    m.add((6.7, 11.8, 6.7), (9.3, 17.6, 9.3), "plate", name="collier")
    if k >= 2: m.add((6.4, 17.6, 6.4), (9.6, 18.4, 9.6), "trim")
    socket(m, k, 4.4, yb + h / 2, 7.5, 8.5)
    renfort(m, k, 8, 14.6, 1.3, 4.4)
    epines(m, k, [(8, 18.4, 90)])
    veines(m, k, 2.0, yb + 1.0, 2.0, yb + h - 1.0, 7.5, 8.5)
    crystals(m, k, [(8.0, 18.4, 0, 2.2)])
    floaters(m, k, [(8, 21.0)] + ([(2.0 - 0.8, yb + h + 2.2)] if k < 7 else [(1.2, yb + h + 2.2), (14.8, yb + h + 2.2)]))
    if k >= 8: ring_y(m, 8, 10.4, 8, 2.6 + 0.4 * (k - 8))
    if k == 10: rays(m, 8, 18.4)
    return m.build(tool_display(0.62, 4))

def mirror_only(m, e):
    frm, to = e["frm"], e["to"]
    f2 = [16 - to[0], frm[1], frm[2]]; t2 = [16 - frm[0], to[1], to[2]]
    r2 = None
    if e["rot"]:
        r2 = dict(e["rot"]); r2["origin"] = [16 - e["rot"]["origin"][0], e["rot"]["origin"][1], e["rot"]["origin"][2]]
        for ax in ("y", "z"):
            if ax in r2: r2[ax] = -r2[ax]
    m.add(f2, t2, e["mat"], r2)

# ------------------------------------------------------------------ pelle (Explorateur)
def pelle(k, P):
    m = Model(f"x_{k}", P); s = size(k)
    manche(m, k, -6, 11.5)
    m.add((5.6, -7.6, 7.4), (10.4, -6.4, 8.6), "trim", name="poignee_T")
    m.add((7.0, 10.6, 7.0), (9.0, 13.4, 9.0), "plate", name="douille")
    w = 6.6 * s * (0.8 if k >= 6 else 1); L = 7.2 * s * (1.35 if k >= 6 else 1)
    m.add((8 - w / 2, 13.2, 7.55), (8 + w / 2, 13.2 + L, 8.45), "blade", name="fer")
    m.add((8 - w / 2 - 0.2, 12.8, 7.3), (8 + w / 2 + 0.2, 13.8, 8.7), "trim")
    tip(m, 8, 13.2 + L, w, 7.55, 8.45)
    m.add((7.5, 13.8, 7.25), (8.5, 13.2 + L * 0.8, 8.75), "edge")
    if k >= 2: m.add((8 - w / 2 - 0.6, 13.6, 7.6), (8 - w / 2, 13.2 + L * 0.7, 8.4), "edge"); m.add((8 + w / 2, 13.6, 7.6), (8 + w / 2 + 0.6, 13.2 + L * 0.7, 8.4), "edge")
    socket(m, k, 8, 13.2 + L * 0.45, 7.55, 8.45)
    if 4 <= k <= 5:
        for i in range(3):
            y = 14.6 + i * 2.0
            mirror(m, (8 - w / 2 - 1.3, y, 7.65), (8 - w / 2, y + 1.0, 8.35), "edge", dict(z=-25, origin=[8 - w / 2, y, 8]))
    if k >= 6:
        mirror(m, (8 - w / 2 - 2.4, 12.6, 7.6), (8 - w / 2, 13.8, 8.4), "plate", dict(z=-35, origin=[8 - w / 2, 13.2, 8]))
        mirror(m, (8 - w / 2 - 3.2, 13.2, 7.7), (8 - w / 2 - 2.0, 15.6, 8.3), "edge", dict(z=-35, origin=[8 - w / 2, 13.2, 8]))
    renfort(m, k, 8, 12.0, 1.0, 3.0)
    epines(m, k, [(8 - w / 2 - 0.5, 13.4, 160), (8 + w / 2 + 0.5, 13.4, 20)])
    veines(m, k, 8 - w / 2 + 1, 14.2, 8, 13.2 + L, 7.55, 8.45); veines(m, k, 8 + w / 2 - 1, 14.2, 8, 13.2 + L, 7.55, 8.45)
    crystals(m, k, [(8 - w / 2 - 0.3, 13.4, 35, 2.0), (8 + w / 2 + 0.3, 13.4, -35, 2.0)])
    floaters(m, k, [(8 - w / 2 - 1.8, 13.2 + L), (8 + w / 2 + 1.8, 13.2 + L)] + ([(8, 13.2 + L + w * 0.7 + 1.6)] if k >= 8 else []))
    if k >= 8: ring_y(m, 8, 9.0, 8, 2.4 + 0.4 * (k - 8))
    if k == 10: rays(m, 8, 13.2 + L + w * 0.55)
    return m.build(tool_display(0.62, 4))

# ------------------------------------------------------------------ houe / faux (Fermier)
def houe(k, P):
    m = Model(f"f_{k}", P); s = 1 + 0.05 * k
    manche(m, k, -6, 15.5)
    m.add((6.6, 13.6, 6.8), (9.6, 16.8, 9.2), "plate", name="tete")
    n = 3 if k < 2 else 4 if k < 5 else 5
    segs = [(3.6 * s, 2.0, 180), (2.8 * s, 1.8, 206), (2.6 * s, 1.5, 232), (2.4 * s, 1.2, 256), (2.0 * s, 0.9, 278)][:n]
    mats = ["plate", "blade", "blade", "edge", "edge"][:n]
    pts = seg2d(m, (6.9, 15.2), segs, mats, depth=1.0)
    if k >= 2: m.add((9.6, 14.4, 7.4), (10.8, 16.0, 8.6), "trim")
    if k >= 1: diamond(m, 11.6, 15.2, 1.8 + 0.12 * k, "glow")
    socket(m, k, 8.1, 15.2, 6.8, 9.2)
    renfort(m, k, 8.1, 15.2, 1.5, 3.2)
    epines(m, k, [(9.4, 16.8, 70), (8.1, 13.6, -90)])
    veines(m, k, pts[0][0], pts[0][1], pts[-1][0], pts[-1][1], 7.5, 8.5)
    crystals(m, k, [(7.0, 16.8, 15, 2.0)])
    floaters(m, k, [(pts[-1][0] - 1.4, pts[-1][1] - 1.2), (8.1, 19.6)])
    if k >= 8: ring_y(m, 8, 11.2, 8, 2.4 + 0.4 * (k - 8))
    if k == 10: rays(m, 8.1, 16.8)
    return m.build(tool_display(0.62, 4))

# ------------------------------------------------------------------ canne à pêche (Pêcheur)
def canne(k, P, cast=False):
    m = Model(f"p_{k}" + ("_cast" if cast else ""), P); s = size(k)
    pts = seg2d(m, (8, -6), [(7.0, 1.5, 86), (6.4 * s, 1.15, 78), (5.4 * s, 0.85, 66), (4.0 * s, 0.6, 52)],
                ["grip", "plate", "plate", "edge"], depth=None)
    m.add((8.6, -2.6, 7.0), (10.6, -0.6, 9.0), "trim", name="moulinet")
    m.add((10.6, -2.0, 7.6), (11.6, -1.2, 8.4), "plate")
    if k >= 1:
        for (x, y) in pts[:3]: m.add((x - 0.5, y - 0.5, 7.5), (x + 0.5, y + 0.5, 8.5), "trim")
    tx, ty = pts[-1]
    if not cast:
        m.add((tx - 0.12, ty - 13, 7.9), (tx + 0.12, ty, 8.1), "string", name="fil")
        m.add((tx - 0.6, ty - 13.6, 7.8), (tx + 0.1, ty - 13, 8.2), "edge")
        if k >= 1: diamond(m, tx, ty - 11.4, 1.4 + 0.1 * k, "glow")
    socket(m, k, 9.6, -1.6, 7.0, 9.0)
    renfort(m, k, 9.6, -1.6, 1.0, 2.4)
    epines(m, k, [(8.3, 4.0, 150), (8.7, 1.0, 20)])
    crystals(m, k, [(8.6, 3.0, -20, 1.8)])
    floaters(m, k, [(tx + 1.4, ty + 1.2), (9.6, 4.6)])
    if k >= 8: ring_z(m, 9.6, -1.6, 2.2, n=10)
    if k == 10: rays(m, tx, ty)
    return m.build(tool_display(0.62, 2))

# ------------------------------------------------------------------ houlette (Éleveur)
def houlette(k, P):
    m = Model(f"e_{k}", P); s = size(k)
    manche(m, k, -7, 8)
    m.add((7.25, 8, 7.25), (8.75, 17.5, 8.75), "plate", name="hampe")
    curl = [(2.6, 1.4, 92), (2.6, 1.4, 62), (2.6, 1.4, 24), (2.4, 1.3, -22), (2.2, 1.2, -70), (1.8, 1.1, -118)]
    if k >= 2: curl.append((1.6, 1.0, -160))
    if k >= 5: curl.append((1.4, 0.9, -200))
    curl = [(L * s, t, a) for (L, t, a) in curl]
    pts = seg2d(m, (8, 17.4), curl, ["plate"] * 2 + ["trim"] + ["plate"] * 4)
    m.add((7.0, 16.8, 7.0), (9.0, 18.0, 9.0), "trim")
    if k >= 1:
        x, y = pts[-1]
        m.add((x - 0.15, y - 2.2, 7.85), (x + 0.15, y, 8.15), "string")
        m.add((x - 0.9, y - 3.8, 7.1), (x + 0.9, y - 2.2, 8.9), "trim" if k < 3 else "glow", name="clochette")
    socket(m, k, 8, 12.5, 7.25, 8.75)
    renfort(m, k, 8, 16.4, 0.75, 3.0)
    epines(m, k, [(8.75, 9.0, 20), (7.25, 11.0, 160), (8.0, 23.0, 95)])
    crystals(m, k, [(8.0, 22.2, -10, 1.8)])
    floaters(m, k, [(pts[2][0] + 1.4, pts[2][1] + 1.6), (6.0, 19.4)])
    if k >= 8: ring_z(m, pts[3][0] - 0.6, pts[3][1] - 1.8, 3.6, n=12)
    if k == 10: rays(m, 9.4, 22.6)
    return m.build(tool_display(0.62, 2))

# ------------------------------------------------------------------ grimoire (Enchanteur)
def grimoire(k, P):
    m = Model(f"n_{k}", P); s = 1 + 0.015 * k
    x0, x1, y0, y1 = 8 - 4.2 * s, 8 + 4.2 * s, 8 - 5.6 * s, 8 + 5.6 * s
    m.add((x0, y0, 6.4), (x1, y1, 7.2), "leather", name="plat_avant")
    m.add((x0, y0, 8.8), (x1, y1, 9.6), "leather", name="plat_arriere")
    m.add((x0 + 0.3, y0 + 0.3, 7.2), (x1 - 0.2, y1 - 0.3, 8.8), "page", name="pages")
    m.add((x0 - 0.8, y0, 6.4), (x0, y1, 9.6), "leather", name="dos")
    for yy in (y0 + 1.2, y1 - 2.0): m.add((x0 - 1.0, yy, 6.2), (x0 + 0.2, yy + 0.8, 9.8), "trim")
    if k >= 1:
        for (cx, cy) in ((x1 - 0.8, y1 - 0.8), (x1 - 0.8, y0 + 0.8), (x0 + 0.8, y1 - 0.8), (x0 + 0.8, y0 + 0.8)):
            m.add((cx - 0.9, cy - 0.9, 6.1), (cx + 0.9, cy + 0.9, 6.5), "trim")
    if k >= 2: m.add((x1 - 0.2, 7.0, 6.1), (x1 + 0.9, 9.0, 9.9), "trim", name="fermoir")
    m.add((6.4, 6.4, 6.0), (9.6, 9.6, 6.45), "trim")
    m.add((7.1, 7.1, 5.6), (8.9, 8.9, 6.1), "gem" if k < 1 else "glow", dict(z=45, origin=[8, 8, 5.85]), name="embleme")
    if k >= 2:
        for (cx, cy) in ((x1 - 0.8, y1 - 0.8), (x1 - 0.8, y0 + 0.8), (x0 + 0.8, y1 - 0.8), (x0 + 0.8, y0 + 0.8)):
            m.add((cx - 1.4, cy - 1.4, 5.9), (cx + 1.4, cy + 1.4, 6.4), "plate")
    epines(m, k, [(x1 + 0.4, y1 + 0.4, 45), (x0 - 0.4, y1 + 0.4, 135), (x1 + 0.4, y0 - 0.4, -45), (x0 - 0.4, y0 - 0.4, -135)])
    veines(m, k, 8, y0 + 1.2, 8, y1 - 1.2, 6.0, 10.0); veines(m, k, x0 + 1.2, 8, x1 - 1.2, 8, 6.0, 10.0)
    if k >= 4:
        for a in (0, 90, 180, 270):
            ar = math.radians(a); cx, cy = 8 + 2.6 * math.cos(ar), 8 + 2.6 * math.sin(ar)
            m.add((cx - 0.3, cy - 0.3, 6.0), (cx + 0.3, cy + 0.3, 6.4), "glow")
    crystals(m, k, [(x1 + 0.2, y1 - 0.2, -40, 1.8), (x0 - 0.2, y0 + 0.4, 140, 1.6)])
    if k >= 6:
        for i in range(3 if k < 9 else 5):
            a = math.radians(30 + i * 60); cx, cy = 8 + 7.2 * math.cos(a), 8 + 7.6 * math.sin(a)
            m.add((cx - 0.7, cy - 0.9, 7.6), (cx + 0.7, cy + 0.9, 8.4), "glow", dict(z=15, origin=[cx, cy, 8]))
    if k >= 8: ring_z(m, 8, 8, 8.4, n=16, zc=8.0)
    if k == 10: rays(m, 8, y1 + 0.4)
    d = tool_display(0.62, 8)
    d["thirdperson_righthand"] = {"rotation": [0, -90, 0], "translation": [0, 2, 1], "scale": [0.55, 0.55, 0.55]}
    d["gui"] = {"rotation": [0, 20, 0], "scale": [0.85, 0.85, 0.85]}
    return m.build(d)

# ------------------------------------------------------------------ bourse (Marchand)
def bourse(k, P):
    m = Model(f"t_{k}", P); s = 1 + 0.015 * k
    c = lambda a, b, y0, y1, mat="cloth", name=None: m.add((8 - a * s, y0, 8 - b * s), (8 + a * s, y1, 8 + b * s), mat, name=name)
    c(3.0, 3.0, 1.0, 2.0); c(4.0, 4.0, 2.0, 7.4, name="panse"); c(3.4, 3.4, 7.4, 9.0)
    c(1.8, 1.8, 9.0, 10.6, name="col"); c(2.1, 2.1, 9.4, 10.2, "trim", name="lien"); c(2.8, 2.8, 10.6, 11.8)
    m.add((5.2, 9.6, 3.6), (6.4, 10.0, 6.0), "trim", dict(x=-35, origin=[5.8, 9.8, 6.0]))
    for i, (x, y) in enumerate(((6.2, 4.0), (9.2, 3.0), (7.6, 6.0))[: 1 + min(2, k)]):
        m.add((x - 0.9, y - 0.9, 3.65), (x + 0.9, y + 0.9, 3.95), "trim", name=f"piece_{i}")
    if k >= 1:
        m.add((7.0, 6.6, 3.6), (9.0, 8.6, 4.0), "trim")
        m.add((7.4, 7.0, 3.3), (8.6, 8.2, 3.7), "glow", dict(z=45, origin=[8, 7.6, 3.5]))
    if k >= 2:
        c(4.2, 4.2, 2.6, 3.4, "trim"); c(4.2, 4.2, 6.0, 6.8, "trim")
    if k >= 3:
        for (x, z) in ((3.6, 8), (12.4, 8), (8, 12.4)):
            m.add((x - 0.6, 4.2, z - 0.6), (x + 0.6, 5.4, z + 0.6), "edge", dict(y=45, origin=[x, 4.8, z]))
    if k >= 5:
        c(4.05, 4.05, 4.6, 4.9, "glow")
    crystals(m, k, [(6.8, 11.6, 20, 1.8), (9.4, 11.6, -25, 2.2)])
    if k >= 6:
        for i in range(3 if k < 9 else 5):
            a = math.radians(-20 + i * 50); cx, cy = 8 + 6.0 * math.cos(a), 9 + 4.6 * math.sin(a)
            m.add((cx - 0.8, cy - 0.8, 7.8), (cx + 0.8, cy + 0.8, 8.2), "glow", dict(y=40, origin=[cx, cy, 8]))
    if k >= 8: ring_y(m, 8, 5.0, 8, 5.6, n=14)
    if k == 10: rays(m, 8, 11.8)
    d = tool_display(0.62, 4)
    d["thirdperson_righthand"] = {"rotation": [0, -90, 0], "translation": [0, 0, 1], "scale": [0.55, 0.55, 0.55]}
    d["gui"] = {"rotation": [25, 30, 0], "scale": [0.85, 0.85, 0.85]}
    return m.build(d)

# ------------------------------------------------------------------ épées : 11 paliers (0, 5, 9 validés et inchangés)
def epee_longue(k, P):
    m = Model(f"c_{k}", P)
    m.add((7.0, -5.6, 7.0), (9.0, -3.6, 9.0), "plate" if k < 2 else "gem", dict(y=45, origin=[8, -4.6, 8]) if k >= 2 else None)
    m.add((7.4, -3.6, 7.4), (8.6, 2.0, 8.6), "grip")
    m.add((3.6, 2.0, 7.15), (12.4, 3.1, 8.85), "trim" if k else "plate")
    if k >= 1: mirror(m, (2.4, 2.5, 7.3), (3.8, 3.5, 8.7), "trim", dict(z=-30, origin=[3.8, 2.6, 8]))
    m.add((6.9, 1.6, 6.9), (9.1, 3.5, 9.1), "plate")
    L = 24.5 + 0.4 * k
    m.add((6.5, 3.1, 7.5), (9.5, L, 8.5), "blade")
    tip(m, 8, L, 3.0, 7.5, 8.5)
    return m.build(sword_display(0.7, 0.0))

def epee_batarde(k, P, name=None):
    m = Model(name or f"c_{k}", P)
    diamond(m, 8, -5.0, 2.4, "gem" if k == 3 else "glow")
    m.add((7.2, -4.0, 7.2), (8.8, -3.2, 8.8), "trim")
    m.add((7.3, -3.2, 7.3), (8.7, 2.2, 8.7), "grip")
    m.add((2.6, 2.2, 7.1), (13.4, 3.4, 8.9), "trim", name="garde")
    for x in (2.6, 13.4): diamond(m, x, 2.8, 2.2, "gem" if k == 3 else "glow")
    m.add((6.6, 1.8, 6.6), (9.4, 3.8, 9.4), "plate")
    m.add((6.3, 3.4, 7.45), (9.7, 6.0, 8.55), "plate", name="ricasso")
    L = 25.4 + 0.5 * (k - 3)
    m.add((6.3, 6.0, 7.5), (9.7, L, 8.5), "blade")
    m.add((7.6, 6.6, 7.25), (8.4, L - 2.0, 8.75), "edge")
    tip(m, 8, L, 3.4, 7.5, 8.5)
    if k == 4: m.add((7.4, 3.9, 7.2), (8.6, 5.1, 8.8), "glow", dict(z=45, origin=[8, 4.5, 8]))
    return m.build(sword_display(0.7, 0.0))

def epee_segmentee(k, P, name=None):
    m = Model(name or f"c_{k}", P)
    m.add((6.8, -6.6, 6.8), (9.2, -4.2, 9.2), "glow", dict(y=45, x=35, origin=[8, -5.4, 8]))
    m.add((7.3, -4.2, 7.3), (8.7, 2.0, 8.7), "grip")
    m.add((5.6, 1.6, 6.8), (10.4, 4.2, 9.2), "trim")
    mirror(m, (2.2, 2.6, 7.3), (5.8, 3.8, 8.7), "plate", dict(z=-28, origin=[5.8, 3.2, 8]))
    mirror(m, (1.0, 4.4, 7.4), (2.6, 6.0, 8.6), "glow", dict(z=45, origin=[1.8, 5.2, 8]))
    y = 4.2; n = 4 if k == 7 else 5
    for i in range(n):
        h = 4.6 - 0.25 * i
        w = 3.8 - 0.2 * i
        m.add((8 - w / 2, y, 7.45), (8 + w / 2, y + h, 8.55), "runeblade" if k == 8 else "blade")
        mirror(m, (8 - w / 2 - 0.6, y + 0.4, 7.6), (8 - w / 2, y + h - 0.4, 8.4), "edge")
        y += h
        if i < n - 1:
            diamond(m, 8, y + 0.4, 1.4, "glow"); y += 0.8
    tip(m, 8, y, 3.0, 7.5, 8.5)
    if k == 8: ring_y(m, 8, y - 6.0, 8, 2.8, n=10)
    return m.build(sword_display(0.7, 0.0))

def epee_epineuse(P, name):
    m = Model(name, P)
    m.add((7.1, -6.2, 7.1), (8.9, -4.4, 8.9), "plate"); seg2d(m, (8, -6.2), [(1.6, 1.0, -90), (1.2, 0.6, -90)], ["plate", "edge"], depth=0.8)
    m.add((7.3, -4.4, 7.3), (8.7, 2.0, 8.7), "grip")
    m.add((4.4, 1.6, 6.8), (11.6, 4.0, 9.2), "trim", name="garde")
    for sx in (1, -1):
        x = 4.4 if sx == 1 else 11.6
        seg2d(m, (x, 3.4), [(2.2, 1.4, 150 if sx == 1 else 30), (2.0, 1.0, 115 if sx == 1 else 65), (1.6, 0.6, 95 if sx == 1 else 85)], ["plate", "plate", "edge"], depth=1.2)
    m.add((5.6, 4.0, 7.4), (10.4, 21.0, 8.6), "blade", name="lame")
    tip(m, 8, 21.0, 4.8, 7.4, 8.6)
    m.add((7.5, 4.6, 7.2), (8.5, 19.6, 8.8), "edge")
    for y in (6.0, 9.0, 12.0, 15.0, 18.0):
        for sx in (1, -1):
            x = 5.6 if sx == 1 else 10.4
            m.add((x - 2.0 if sx == 1 else x, y, 7.6), (x if sx == 1 else x + 2.0, y + 1.1, 8.4), "edge", dict(z=32 * sx, origin=[x, y, 8]))
    return m.build(sword_display(0.7, 0.0))

def epee_flamberge(P, name):
    m = Model(name, P)
    diamond(m, 8, -5.4, 2.6, "glow")
    m.add((7.3, -4.2, 7.3), (8.7, 2.0, 8.7), "grip")
    m.add((5.4, 1.6, 6.8), (10.6, 4.0, 9.2), "trim", name="garde")
    for sx in (1, -1):
        x = 5.4 if sx == 1 else 10.6
        seg2d(m, (x, 2.8), [(2.4, 1.3, 200 if sx == 1 else -20), (2.0, 1.0, 240 if sx == 1 else -60), (1.4, 0.7, 275 if sx == 1 else -95)], ["plate", "plate", "glow"], depth=1.2)
    y = 4.0
    for i in range(9):
        off = 0.7 if i % 2 == 0 else -0.7
        w = 4.8 - 0.2 * i
        m.add((8 - w / 2 + off, y, 7.45), (8 + w / 2 + off, y + 2.4, 8.55), "blade", dict(z=12 if i % 2 == 0 else -12, origin=[8 + off, y + 1.2, 8]))
        y += 2.0
    tip(m, 8 + 0.7, y + 0.2, 2.4, 7.5, 8.5)
    m.add((7.65, 4.4, 7.3), (8.35, y - 0.4, 8.7), "glow", name="coeur")
    for (x, yy) in ((3.6, 9.0), (12.6, 12.0), (3.4, 16.0), (12.8, 19.0)): diamond(m, x, yy, 1.4, "glow", extra_rot=dict(y=30))
    return m.build(sword_display(0.7, 0.0))

def epee_fourchue(P, name):
    m = Model(name, P)
    m.add((6.8, -6.6, 6.8), (9.2, -4.2, 9.2), "glow", dict(y=45, x=35, origin=[8, -5.4, 8]))
    m.add((7.3, -4.2, 7.3), (8.7, 2.0, 8.7), "grip")
    m.add((3.4, 1.6, 6.8), (12.6, 4.4, 9.2), "trim", name="garde")
    mirror(m, (0.8, 3.0, 7.3), (3.6, 4.4, 8.7), "plate", dict(z=-24, origin=[3.6, 3.7, 8]))
    for sx in (1, -1):
        cx = 8 - 2.7 * sx
        m.add((cx - 1.4, 4.4, 7.45), (cx + 1.4, 24.0, 8.55), "runeblade", dict(z=-3 * sx, origin=[cx, 4.4, 8]))
        tip(m, cx - 1.0 * sx, 24.0, 2.8, 7.5, 8.5)
        m.add((cx - 1.4 - 0.6 if sx == 1 else cx + 1.4, 6.0, 7.6), (cx - 1.4 if sx == 1 else cx + 2.0, 21.0, 8.4), "edge", dict(z=-3 * sx, origin=[cx, 4.4, 8]))
    for y in (8.0, 12.0, 16.0, 20.0):
        diamond(m, 8, y, 1.6, "glow")
    m.add((7.75, 5.0, 7.75), (8.25, 22.0, 8.25), "glow", name="arc")
    return m.build(sword_display(0.7, 0.0))

def epee(k, P):
    """0 longue diamant, 1 bâtarde, 2 et 3 lame large netherite, 4 forme validée (améthyste), 5 braises,
    6 et 7 segmentée, 8 lame flottante du Vide, 9 forme validée mythique, 10 Dieu."""
    if k == 0: return epee_longue(0, P)
    if k == 1: return epee_batarde(4, P, "c_1")
    if k == 2: return epee_5("c_2", P)
    if k == 3: return epee_epineuse(P, "c_3")
    if k == 4: return epee_5("c_4", P)
    if k == 5: return epee_flamberge(P, "c_5")
    if k == 6: return epee_segmentee(7, P, "c_6")
    if k == 7: return epee_fourchue(P, "c_7")
    if k == 8: return epee_9("c_8", P)
    if k == 9: return epee_9()
    if k == 10:
        def couronne(m):
            rays(m, 8, 4.4); ring_y(m, 8, 23.0, 8, 3.0, n=10)
        return epee_9("c_10", P, couronne)

# ------------------------------------------------------------------ arcs (Chasseur)
def arc(k, P, pull=None):
    name = f"arc_{k}" + (f"_pulling_{pull}" if pull is not None else "")
    m = Model(name, P)
    bend = [0, 6, 12, 18][0 if pull is None else pull + 1]
    m.add((7.2, 5.4, 7.4), (8.8, 10.6, 8.6), "grip", name="poignee")
    m.add((6.9, 10.4, 7.2), (9.1, 11.2, 8.8), "trim"); m.add((6.9, 4.8, 7.2), (9.1, 5.6, 8.8), "trim")
    up = [(3.4, 1.5, 96 + bend * 0.3), (3.2, 1.3, 110 + bend * 0.6), (3.0, 1.1, 126 + bend), (2.4, 0.9, 140 + bend * 1.2)]
    mats = ["plate", "plate", "plate", "trim"]
    pu = seg2d(m, (8, 10.8), up, mats)
    pd = seg2d(m, (8, 5.2), [(L, t, -a) for (L, t, a) in up], mats)
    tx_u, ty_u = pu[-1]; tx_d, ty_d = pd[-1]
    pullx = 0 if pull is None else [2.4, 4.0, 5.6][pull]
    sx = tx_u + pullx
    if pull is None:
        m.add((tx_u - 0.15, ty_d, 7.85), (tx_u + 0.15, ty_u, 8.15), "string" if k < 9 else "glow", name="corde")
    else:
        for (ax, ay) in ((tx_u, ty_u), (tx_d, ty_d)):
            dx, dy = sx - ax, 8 - ay; L = math.hypot(dx, dy); a = math.degrees(math.atan2(dy, dx))
            cx, cy = (ax + sx) / 2, (ay + 8) / 2
            m.add((cx - L / 2, cy - 0.15, 7.85), (cx + L / 2, cy + 0.15, 8.15), "string" if k < 9 else "glow", dict(z=a, origin=[cx, cy, 8]))
        m.add((sx - 13, 7.85, 7.85), (sx, 8.15, 8.15), "grip", name="fleche")
        diamond(m, sx - 13.4, 8, 1.4, "edge", depth=0.4)
        m.add((sx - 1.6, 7.4, 7.95), (sx - 0.2, 8.6, 8.05), "cloth")
    if k >= 3: socket(m, k, 8, 8, 7.4, 8.6)
    crystals(m, k, [(tx_u, ty_u, 30, 1.6), (tx_d, ty_d - 1.6, 150, 1.6)])
    if k >= 7: diamond(m, tx_u - 1.4, ty_u + 1.2, 1.4, "glow"); diamond(m, tx_d - 1.4, ty_d - 1.2, 1.4, "glow")
    if k >= 9: ring_z(m, 8, 8, 2.4, n=10, zc=8)
    d = {"thirdperson_righthand": {"rotation": [-80, 260, -40], "translation": [-1, -2, 2.5], "scale": [0.9, 0.9, 0.9]},
         "thirdperson_lefthand": {"rotation": [-80, -280, 40], "translation": [-1, -2, 2.5], "scale": [0.9, 0.9, 0.9]},
         "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
         "firstperson_lefthand": {"rotation": [0, 90, -25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
         "gui": {"rotation": [0, 0, -45], "scale": [0.8, 0.8, 0.8]}}
    return m.build(d)

# ------------------------------------------------------------------ export
BASE = os.path.join(OUT, "pack", "assets", "metiers")
def item_def(name, model):
    os.makedirs(f"{BASE}/items", exist_ok=True)
    json.dump({"model": model}, open(f"{BASE}/items/proto_{name}.json", "w"), indent=1)
def save(mdl, at, gl, S, name):
    t = mdl["textures"]
    for key in list(t):
        t[key] = f"metiers:item/proto/{name}_glow" if key == "glow" else f"metiers:item/proto/{name}"
    gen.save(mdl, at, gl, S, name)
def ref(n): return {"type": "minecraft:model", "model": f"metiers:item/proto/{n}"}

GEN = {"c": epee, "b": hache, "m": pioche, "x": pelle, "f": houe, "p": canne, "e": houlette, "n": grimoire, "t": bourse}
if __name__ == "__main__":
    import shutil
    shutil.rmtree(os.path.join(OUT, "pack"), ignore_errors=True)
    count = 11
    for j, fn in GEN.items():
        for k in range(11):
            P = palette(k)
            mdl, at, gl, S = fn(k, P)
            name = f"{j}_{k}"
            save(mdl, at, gl, S, name); count += 1
            if j == "p":
                mdl, at, gl, S = canne(k, P, cast=True); save(mdl, at, gl, S, f"p_{k}_cast")
                item_def(name, {"type": "minecraft:condition", "property": "minecraft:fishing_rod/cast", "on_false": ref(name), "on_true": ref(name + "_cast")})
    for k in (2, 9):
        P = palette(k)
        for pull in (None, 0, 1, 2):
            mdl, at, gl, S = arc(k, P, pull)
            n = f"arc_{k}" + (f"_pulling_{pull}" if pull is not None else "")
            save(mdl, at, gl, S, n)
        item_def(f"arc_{k}", {"type": "minecraft:condition", "property": "minecraft:using_item", "on_false": ref(f"arc_{k}"),
                              "on_true": {"type": "minecraft:range_dispatch", "property": "minecraft:use_duration", "scale": 0.05,
                                          "entries": [{"threshold": 0.65, "model": ref(f"arc_{k}_pulling_1")}, {"threshold": 0.9, "model": ref(f"arc_{k}_pulling_2")}],
                                          "fallback": ref(f"arc_{k}_pulling_0")}})
        count += 1
    for f in os.listdir(f"{BASE}/items"):
        if re.match(r"proto_(arc_\d_pulling_\d|p_\d+_cast)\.json", f): os.remove(f"{BASE}/items/{f}")
    json.dump({"pack": {"description": "Métiers : prototypes refonte (test)", "min_format": 69, "max_format": 999}},
              open(os.path.join(OUT, "pack", "pack.mcmeta"), "w"), indent=1)
    print("objets", count)

# ------------------------------------------------------------------ armure des guildes : 11 paliers
sys.path.insert(0, "/home/claude/katjounis/minecraft-metiers/sources")
import armorgen2
from gen import coque, GUILDE, HEAD_DISPLAY, chain, gorget

def hexs(c): return "#%02x%02x%02x" % tuple(int(max(0, min(255, v))) for v in c)

def heaume(k):
    """Une silhouette par palier : 0-1 heaume à visière, 2 pointes, 3 cornes de taureau, 4 cornes de bélier et crête
    de cristaux, 5 masque de forge à cheminées, 6 couronne de pointes à rubis, 7 roue runique, 8-10 ailes."""
    P = palette(k)
    if k == 10: return heaume_5("heaume_10")
    if k >= 8:
        def vide(m):
            if k == 8:
                for (x, y) in ((-3.0, 14.0), (19.0, 14.0)): diamond(m, x, y, 1.8, "glow", extra_rot=dict(y=30))
        return heaume_5(f"heaume_{k}", P, vide)
    if k == 3:
        def pointes(m):
            for x in (3.0, 13.0): seg2d(m, (x, 15.0), [(1.8, 1.2, 90), (1.4, 0.7, 100)], ["plate", "edge"], depth=1.0)
        return heaume_3("heaume_3", P, pointes)
    m = Model(f"heaume_{k}", P)
    if k <= 2:
        coque(m, "visor")
        mirror(m, (0.5, 3.0, 7.4), (0.9, 10.4, 8.6), "trim")
        m.add((5.9, 10.2, 0.0), (10.1, 14.0, 0.9), "trim")
        m.add((7.0, 11.1, -0.5), (9.0, 13.1, 0.3), "glow", dict(z=45, origin=[8, 12.1, -0.1]))
        if k >= 1:
            m.add((7.1, 15.6, 1.8), (8.9, 18.0, 14.2), "plate", name="crete")
            m.add((7.25, 18.0, 3.2), (8.75, 19.6, 12.6), "trim")
            m.add((7.2, 16.0, 13.0), (8.8, 18.2, 17.4), "cloth", dict(x=-30, origin=[8, 17.1, 13.0]))
            mirror(m, (-0.6, 6.0, 5.0), (0.6, 12.0, 11.0), "plate", dict(y=-20, origin=[0, 9, 8]))
        if k >= 2:
            for x in (2.6, 13.4): seg2d(m, (x, 15.2), [(2.2, 1.4, 90), (1.8, 0.9, 98)], ["plate", "edge"], depth=1.2)
        return m.build(HEAD_DISPLAY)
    if k == 4:
        # cornes de bélier qui s'enroulent, crête de cristaux, joues évasées
        coque(m, "grill")
        chain(m, (0.4, 13.0, 8.0), [(4.0, 3.0, 30, -10), (3.8, 2.8, 0, -50), (3.6, 2.6, -40, -95), (3.2, 2.2, -80, -150), (2.8, 1.8, -60, 150), (2.2, 1.4, -15, 110)],
              ["plate", "plate", "trim", "plate", "plate", "edge"])
        for i, (z, h) in enumerate(((2.6, 4.4), (5.2, 6.6), (8.0, 8.4), (10.8, 6.4), (13.4, 4.0))):
            m.add((6.9, 15.4, z - 1.1), (9.1, 15.4 + h, z + 1.1), "glow", dict(x=-22 + i * 9, y=45, origin=[8, 15.4, z]))
            if i in (1, 3):
                for sx in (-1, 1):
                    m.add((8 + sx * 2.2 - 0.7, 15.4, z - 0.7), (8 + sx * 2.2 + 0.7, 15.4 + h * 0.55, z + 0.7), "glow", dict(z=-sx * 24, y=45, origin=[8 + sx * 2.2, 15.4, z]))
        mirror(m, (-1.4, 2.6, 1.6), (0.4, 9.2, 8.0), "plate", dict(y=-28, z=-10, origin=[0.4, 6, 4.8]))
        m.add((5.9, 10.2, 0.0), (10.1, 14.0, 0.9), "trim")
        m.add((7.0, 11.1, -0.5), (9.0, 13.1, 0.3), "glow", dict(z=45, origin=[8, 12.1, -0.1]))
        return m.build(HEAD_DISPLAY)
    if k == 5:
        # masque de forge : mâchoire avancée, trois cheminées à braises, petites cornes épaisses
        coque(m, "visor")
        m.add((3.0, 1.0, -1.8), (13.0, 6.2, 1.2), "plate", name="machoire")
        for x in range(4, 13, 2): m.add((x - 0.35, 1.6, -2.1), (x + 0.35, 5.6, -1.7), "trim")
        m.add((2.2, 8.6, -0.3), (13.8, 9.8, 0.6), "glow", name="fente")
        for (x, z, h) in ((4.0, 11.0, 4.6), (8.0, 12.4, 6.2), (12.0, 11.0, 4.6)):
            m.add((x - 1.1, 16.0, z - 1.1), (x + 1.1, 16.0 + h, z + 1.1), "plate")
            m.add((x - 1.3, 16.0 + h, z - 1.3), (x + 1.3, 16.8 + h, z + 1.3), "trim")
            m.add((x - 0.7, 16.2 + h, z - 0.7), (x + 0.7, 17.0 + h, z + 0.7), "glow")
            diamond(m, x + 0.6, 19.4 + h, 1.0, "glow", extra_rot=dict(y=30))
        chain(m, (0.8, 11.2, 6.0), [(2.6, 3.0, 10, 10), (2.2, 2.4, 45, 35), (1.8, 1.6, 75, 60)], ["plate", "plate", "edge"])
        return m.build(HEAD_DISPLAY)
    if k == 6:
        # couronne de pointes inclinées, un rubis au bout de chaque pointe
        coque(m, "visor")
        m.add((0.6, 15.0, 0.6), (15.4, 16.4, 15.4), "trim", name="bandeau_couronne")
        n = 10
        for i in range(n):
            t = 2 * math.pi * i / n
            cx, cz = 8 + 6.6 * math.sin(t), 8 - 6.6 * math.cos(t)
            h = 6.4 if i == 0 else (4.6 if i in (1, n - 1) else 3.6)
            m.add((cx - 0.6, 16.0, cz - 0.6), (cx + 0.6, 16.0 + h, cz + 0.6), "plate", dict(x=-14 * math.cos(t), z=14 * math.sin(t), origin=[cx, 16.0, cz]))
            ex, ez = cx + math.sin(t) * h * 0.24, cz - math.cos(t) * h * 0.24
            diamond(m, ex, 16.0 + h + 0.4, 1.3, "glow", extra_rot=dict(y=30))
        m.add((5.6, 10.0, 0.0), (10.4, 14.4, 0.9), "trim")
        m.add((6.8, 11.0, -0.6), (9.2, 13.4, 0.3), "glow", dict(z=45, origin=[8, 12.2, -0.15]))
        m.add((2.6, 8.8, 0.2), (13.4, 9.6, 0.7), "glow")
        for (x, y) in ((-2.4, 13.0), (18.4, 13.0), (-1.4, 18.0), (17.4, 18.0)): diamond(m, x, y, 1.6, "glow", extra_rot=dict(y=30))
        return m.build(HEAD_DISPLAY)
    if k == 7:
        # double paire de cornes et roue runique verticale derrière la tête
        coque(m, "grill")
        chain(m, (1.2, 11.2, 7.6), [(3.2, 2.4, 6, 0), (3.0, 2.1, 30, 12), (2.8, 1.8, 58, 24), (2.4, 1.4, 82, 34)], ["plate", "plate", "trim", "trim"])
        chain(m, (0.8, 6.0, 10.0), [(2.6, 1.8, -10, -60), (2.2, 1.4, -30, -100), (1.8, 1.0, -10, -150)], ["plate", "plate", "edge"])
        ring_z(m, 8, 14.0, 10.0, n=20, th=0.7, zc=18.0)
        for a in range(0, 360, 45):
            ar = math.radians(a); x, y = 8 + 10.0 * math.cos(ar), 14.0 + 10.0 * math.sin(ar)
            m.add((x - 0.9, y - 0.9, 17.4), (x + 0.9, y + 0.9, 18.6), "trim", dict(z=45, origin=[x, y, 18]))
        m.add((7.6, 4.0, 15.2), (8.4, 14.0, 18.0), "plate")
        m.add((2.4, 8.8, -0.3), (13.6, 9.7, 0.5), "glow")
        m.add((5.9, 10.2, 0.0), (10.1, 14.0, 0.9), "trim")
        m.add((7.0, 11.1, -0.5), (9.0, 13.1, 0.3), "glow", dict(z=45, origin=[8, 12.1, -0.1]))
        return m.build(HEAD_DISPLAY)

def motif(k, im, P, legs=False):
    """Motif propre au palier peint sur les faces avant et arrière (texture 128x64, 2 px par pixel du modèle)."""
    if k < 3: return im
    a = np.array(im).astype(float)
    S2 = 2
    rects = [(4, 20, 4, 12), (12, 20, 4, 12)] + ([(20, 20, 8, 12), (32, 20, 8, 12)] if True else [])
    if not legs: rects += [(44, 20, 4, 12), (52, 20, 4, 12)]
    g = P["glow"]; t = P["trim"]; me = P["metal"]
    def px(x, y, c):
        if 0 <= y < a.shape[0] and 0 <= x < a.shape[1] and a[y, x, 3] > 0: a[y, x, :3] = c
    for (x0, y0, w, h) in rects:
        X0, Y0, W, H = x0 * S2, y0 * S2, w * S2, h * S2
        if k == 3:    # pointes rivetées en chevrons
            for yy in range(Y0 + 3, Y0 + H - 2, 6):
                for i in range(min(W // 2, 4)):
                    px(X0 + W // 2 - i, yy + i, me[5]); px(X0 + W // 2 + i, yy + i, me[5]); px(X0 + W // 2 - i, yy + i + 1, me[0]); px(X0 + W // 2 + i, yy + i + 1, me[0])
        elif k == 4:  # veines de cristal en diagonale
            for d in range(-H, W, 7):
                for i in range(H):
                    if 0 <= d + i < W: px(X0 + d + i, Y0 + i, g[1] if (i // 2) % 3 else g[2])
        elif k == 5:  # fissures de lave
            import random
            rnd = random.Random(x0 * 31 + y0)
            for _ in range(2):
                x, y = X0 + 2 + rnd.randrange(max(1, W - 4)), Y0 + rnd.randrange(H // 3)
                end = y + H // 2 + rnd.randrange(H // 3)
                while y < min(end, Y0 + H):
                    px(x, y, g[2] if rnd.random() < 0.2 else g[1])
                    y += 1; x = max(X0 + 1, min(X0 + W - 2, x + rnd.choice((-1, 0, 0, 1))))
        elif k == 6:  # grille de rubis sertis d'or
            for yy in range(Y0 + 3, Y0 + H - 2, 7):
                for xx in range(X0 + 2 + (yy // 7) % 2 * 3, X0 + W - 2, 6):
                    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)): px(xx + dx, yy + dy, t[2])
                    px(xx, yy, g[2]); px(xx + 1, yy, g[1])
        elif k == 7:  # runes verticales
            for xx in range(X0 + 2, X0 + W - 1, 5):
                for yy in range(Y0 + 2, Y0 + H - 2):
                    if (yy + xx) % 6 not in (0, 3): px(xx, yy, g[1])
                    if (yy + xx) % 6 == 1: px(xx + 1, yy, g[2])
        elif k >= 8:  # constellations
            for i in range(6):
                xx, yy = X0 + (i * 7 + 3) % W, Y0 + (i * 11 + 5) % H
                px(xx, yy, g[2]); px(xx + 1, yy, g[1]); px(xx, yy + 1, g[1])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")

def armure_textures(k):
    if k == 10:
        im1, im2 = armorgen2.worn(5)
    else:
        P = palette(k)
        armorgen2.T[100 + k] = dict(metal=[hexs(c) for c in P["metal"]], trim=[hexs(c) for c in P["trim"]],
                                    cloth=[hexs(c) for c in P["cloth"]], gem=[hexs(c) for c in P["gem"]],
                                    glow=hexs(P["glow"][1]), runes=k >= 7, sun=False)
        im1, im2 = armorgen2.worn(100 + k)
        im1, im2 = motif(k, im1, P), motif(k, im2, P, legs=True)
    base = os.path.join(OUT, "pack", "assets", "metiers")
    for sub, im in (("humanoid", im1), ("humanoid_leggings", im2)):
        os.makedirs(f"{base}/textures/entity/equipment/{sub}", exist_ok=True)
        im.save(f"{base}/textures/entity/equipment/{sub}/proto_guilde_{k}.png")
    os.makedirs(f"{base}/equipment", exist_ok=True)
    json.dump({"layers": {"humanoid": [{"texture": f"metiers:proto_guilde_{k}"}], "humanoid_leggings": [{"texture": f"metiers:proto_guilde_{k}"}]}},
              open(f"{base}/equipment/proto_guilde_{k}.json", "w"), indent=1)

if __name__ == "__main__":
    for k in range(11):
        mdl, at, gl, S = heaume(k); save(mdl, at, gl, S, f"heaume_{k}")
        armure_textures(k)
    for n in ("heaume_3", "heaume_5"):
        for p in (f"{BASE}/items/proto_{n}.json",):
            pass
    print("armure 11 paliers ok")

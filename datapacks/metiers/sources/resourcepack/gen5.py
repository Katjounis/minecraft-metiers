"""Skins v2 (27/11/2026) : 6 nouvelles palettes (Sakura, Céleste, Abysses, Sculk, Dragon de l'End, Éclipse), formes
légendaires pour les 4 dernières (la forme ne dépend plus du palier), nouvelle épée du palier 3 (« Épine », sans les
petites dents sur les côtés). Écrit seulement les fichiers ajoutés ou remplacés, puis les verse dans
metiers_resourcepack.zip à la racine du dépôt (fusion_rp.py n'est pas nécessaire).

    python gen5.py            génère, fusionne et affiche le SHA-1
"""
import os, sys, json, math, io, zipfile, hashlib, shutil
import numpy as np
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
SOURCES = os.path.dirname(ICI)
DEPOT = os.path.abspath(os.path.join(ICI, "..", "..", "..", ".."))
ZIP = os.path.join(DEPOT, "metiers_resourcepack.zip")
OUT = os.path.join(SOURCES, "..", "build", "skins_v2")

# gen.py et gen2.py lisent leurs voisins dans /home/claude/katjounis/minecraft-metiers/sources : on y relie les sources
_ANC = "/home/claude/katjounis/minecraft-metiers/sources"
os.makedirs(_ANC, exist_ok=True)
for f in os.listdir(SOURCES):
    if f.endswith(".py") and not os.path.exists(os.path.join(_ANC, f)):
        os.symlink(os.path.join(SOURCES, f), os.path.join(_ANC, f))
os.chdir(ICI)
sys.path.insert(0, ICI)
sys.argv = [sys.argv[0], "/tmp/gen5_proto"]
import gen, gen2, gen4
from gen2 import Model, seg2d, diamond, mirror, tip, ring_z, ring_y, tool_display, palette, R
from gen import sword_display

# ------------------------------------------------------------------ palettes
NEW = {
    "sakura":   dict(metal=["#6a3a4a", "#b86a84", "#e8a0b8", "#f8c8d8", "#fff0f6", "#ffffff"], glow=["#ff5ab0", "#ffb0dc", "#ffffff"],
                     trim=["#1e0c10", "#3a1a20", "#5a2a32", "#7a3e48"], cloth=["#4a0a24", "#8a1a44", "#d03a72", "#ff7aac"], grip=["#24100e", "#3e1e1a", "#5a2e28", "#7a423a"]),
    "celeste":  dict(metal=["#5a5a66", "#a8a8b8", "#d8d8e2", "#f2f2f6", "#ffffff", "#ffffff"], glow=["#36d8ff", "#9af0ff", "#ffffff"],
                     trim=["#6b4a0b", "#c9a23a", "#f0d878", "#fff6c8"], cloth=["#1a3a6a", "#2a5aa0", "#4a8ad8", "#8ac0ff"], grip=["#e0d8c8", "#f0e8d8", "#fff8ec", "#ffffff"]),
    "abysses":  dict(metal=["#020612", "#061430", "#0c2450", "#163a78", "#2a5aa8", "#5a8ad8"], glow=["#18ffd0", "#8affe8", "#ffffff"],
                     trim=["#1a1e26", "#3a424e", "#6a7480", "#a8b0ba"], cloth=["#02181a", "#063236", "#0a5050", "#12807a"], grip=["#04080e", "#0a1220", "#121e32", "#1e2e48"]),
    "sculk":    dict(metal=["#01080a", "#051418", "#0a2228", "#0f3440", "#185060", "#2a7a8a"], glow=["#14e8ff", "#7af6ff", "#e8ffff"],
                     trim=["#04201e", "#0a3a36", "#13615a", "#2a9a8a"], cloth=["#020a0c", "#061a20", "#0c2c36", "#144452"], grip=["#020608", "#060e12", "#0c181e", "#14242c"]),
    "dragon":   dict(metal=["#08020c", "#160622", "#260c3a", "#3a1458", "#5a2486", "#8a4ac0"], glow=["#ff3ae0", "#ff9af0", "#ffffff"],
                     trim=["#1e0a2a", "#3c1458", "#6a2a96", "#a85ae0"], cloth=["#0c0410", "#1c0a26", "#2e123e", "#461e5c"], grip=["#060208", "#100614", "#1a0a22", "#281232"]),
    "eclipse":  dict(metal=["#020202", "#0a0908", "#151310", "#221e18", "#363026", "#5a5040"], glow=["#ff8a1a", "#ffd060", "#fffbe0"],
                     trim=["#5a3a06", "#b07a10", "#f0b830", "#fff0a0"], cloth=["#2a0802", "#5a1404", "#9a2a08", "#e05a14"], grip=["#060504", "#0e0c0a", "#1a1612", "#28221c"]),
}
LEGENDAIRES = ["abysses", "sculk", "dragon", "eclipse"]
TOUS = dict(gen4.SKINS); TOUS.update(NEW)

def skinP(s, k):
    P = dict(palette(k)); d = TOUS[s]
    P["metal"] = R(d["metal"]); P["blade"] = R(d["metal"][:5]); P["glow"] = R(d["glow"]); P["trim"] = R(d["trim"])
    P["cloth"] = R(d["cloth"]); P["grip"] = R(d["grip"]); P["feather"] = R(d["metal"][2:6])
    return P

# ------------------------------------------------------------------ épée du palier 3 : « Épine »
def epee_epine(P, name="c_3"):
    m = Model(name, P)
    diamond(m, 8, -5.6, 2.4, "gem")
    m.add((7.15, -4.6, 7.15), (8.85, -3.8, 8.85), "trim")
    m.add((7.3, -3.8, 7.3), (8.7, 1.8, 8.7), "grip")
    for y in (-2.4, -0.4):
        m.add((7.15, y, 7.15), (8.85, y + 0.5, 8.85), "cloth")
    m.add((5.2, 1.6, 6.9), (10.8, 3.6, 9.1), "trim", name="garde")
    for sx in (1, -1):
        x = 5.2 if sx == 1 else 10.8
        seg2d(m, (x, 3.0), [(2.4, 1.3, 165 if sx == 1 else 15), (2.2, 1.0, 120 if sx == 1 else 60), (1.6, 0.6, 95 if sx == 1 else 85)],
              ["trim", "plate", "edge"], depth=1.3)
    y0, y1 = 3.6, 18.4
    m.add((6.5, y0, 7.45), (9.5, y1, 8.55), "blade", name="lame")
    for sx in (1, -1):
        x = 5.6 if sx == 1 else 9.4
        m.add((x, y0, 7.6), (x + 1.0, y1 + 1.4, 8.4), "edge", dict(z=-2.6 * sx, origin=[x + 0.5, y0, 8]))
    m.add((7.6, y0 + 1.0, 7.3), (8.4, y1 - 0.8, 8.7), "glow")
    tip(m, 8, y1 + 0.6, 3.8, 7.45, 8.55)
    return m.build(sword_display(0.7, 0.0))

_epee_orig = gen2.epee
def epee(k, P):
    if k == 3: return epee_epine(P, "c_3")
    if k == 9: return gen2.epee_9("c_9", P)   # epee(9) ignore la palette (comme epee_sk de gen_final.py)
    return _epee_orig(k, P)
gen2.epee = epee

# ------------------------------------------------------------------ briques des formes légendaires
def manche_epee(m, y0=-4.4, y1=1.8):
    m.add((7.3, y0, 7.3), (8.7, y1, 8.7), "grip")
    for y in (y0 + 1.2, y0 + 3.2):
        m.add((7.12, y, 7.12), (8.88, y + 0.5, 8.88), "cloth")
    m.add((7.1, y0 - 0.8, 7.1), (8.9, y0, 8.9), "trim")

def aile(m, x, y, sx, a0, L, zc=8.0, mem="trim"):
    """Aile de dragon : os d'attaque épais et pans de membrane qui pendent dessous en pointes."""
    a = a0 if sx == 1 else 180 - a0
    pts = seg2d(m, (x, y), [(L, 1.0, a), (L * 0.7, 0.7, a + 32 * sx), (L * 0.35, 0.45, a + 60 * sx)], ["plate", "plate", "edge"], depth=1.0, zc=zc)
    anc = [(x + math.cos(math.radians(a)) * L * f, y + math.sin(math.radians(a)) * L * f) for f in (0.35, 0.7)] + [pts[0], pts[1]]
    for n, (px, py) in enumerate(anc):
        d = (a - 90 * sx) - 18 * sx * n
        Lm = (3.4 - 0.4 * n) * L / 4.6
        seg2d(m, (px, py), [(Lm, (1.9 - 0.25 * n) * L / 4.6, d), (Lm * 0.45, 0.8 * L / 4.6, d - 15 * sx)], [mem, mem], depth=0.35, zc=zc)

# ornements posés sur les outils qui gardent leur base (hache, houe, pelle, canne, houlette, grimoire, Dank Null)
def orn_dragon(m, x, y, s, zc):
    for sx in (1, -1):
        aile(m, x - 0.9 * s * sx, y, sx, 150, 3.8 * s, zc)
    m.add((x - 1.1 * s, y - 1.0 * s, zc - 1.1 * s), (x + 1.1 * s, y + 1.1 * s, zc + 1.1 * s), "plate")
    for z0, z1 in ((zc - 1.1 * s - 0.25, zc - 1.1 * s), (zc + 1.1 * s, zc + 1.1 * s + 0.25)):
        m.add((x - 0.9 * s, y, z0), (x - 0.2 * s, y + 0.6 * s, z1), "glow"); m.add((x + 0.2 * s, y, z0), (x + 0.9 * s, y + 0.6 * s, z1), "glow")
    for sx in (1, -1):
        seg2d(m, (x - 0.7 * s * sx, y + 1.1 * s), [(1.6 * s, 0.6, 90 + 25 * sx), (1.0 * s, 0.4, 90 + 50 * sx)], ["trim", "edge"], depth=0.6, zc=zc)

def orn_sculk(m, x, y, s, zc):
    for i, L in enumerate((3.0, 2.4)):
        for sx in (1, -1):
            seg2d(m, (x - 0.8 * sx, y + 0.9 * s * i), [(L * s, 0.9, 90 + 70 * sx), (L * 0.8 * s, 0.7, 90 + 35 * sx), (L * 0.5 * s, 0.45, 90 + 8 * sx)],
                  ["plate", "plate", "edge"], depth=1.0, zc=zc)
    diamond(m, x, y + 0.6 * s, 2.0 * s, "glow", zc=zc, depth=1.8 * s)

def orn_abysses(m, x, y, s, zc):
    ring_z(m, x, y, 1.9 * s, n=12, th=0.6, zc=zc)
    diamond(m, x, y, 1.4 * s, "glow", zc=zc)
    for sx in (1, -1):
        pts = seg2d(m, (x - 1.8 * s * sx, y - 0.4 * s), [(1.8 * s, 0.6, 270 - 30 * sx), (1.6 * s, 0.5, 270 + 25 * sx), (1.0 * s, 0.4, 270 - 20 * sx)],
                    ["cloth", "cloth", "cloth"], depth=0.6, zc=zc)
        diamond(m, pts[-1][0], pts[-1][1], 0.9 * s, "glow", zc=zc)

def orn_eclipse(m, x, y, s, zc):
    ring_z(m, x, y, 2.4 * s, n=14, th=0.6, zc=zc)
    ring_y(m, x, y, zc, 2.0 * s, n=10, th=0.45)
    diamond(m, x, y, 1.8 * s, "glow", zc=zc)
    for k in range(6):
        a = k * 60 + 30; r = math.radians(a)
        seg2d(m, (x + 2.6 * s * math.cos(r), y + 2.6 * s * math.sin(r)), [(1.2 * s, 0.6, a), (0.8 * s, 0.4, a + 30)], ["trim", "glow"], depth=0.5, zc=zc)

ORN = {"dragon": orn_dragon, "sculk": orn_sculk, "abysses": orn_abysses, "eclipse": orn_eclipse}
# (générateur, palier de base, point d'accroche x, y, taille, plan z)
BASE_OUTIL = {"b": (gen2.hache, 7, 8.0, 20.6, 1.45, 8.0), "f": (gen2.houe, 7, 8.1, 19.4, 1.35, 8.0), "x": (gen2.pelle, 7, 8.0, 11.6, 1.45, 8.0),
              "p": (gen2.canne, 7, 9.6, -1.6, 0.9, 8.0), "e": (gen2.houlette, 7, 8.0, 12.6, 1.3, 8.0),
              "n": (gen2.grimoire, 7, 8.0, 8.0, 1.3, 5.2), "t": (gen2.bourse, 7, 8.0, 12.8, 1.3, 8.0)}

_build = gen.Model.build
_HOOK = []
def _build_hook(self, display):
    for h in _HOOK: h(self)
    return _build(self, display)
gen.Model.build = _build_hook

def legendaire_base(s, j, cast=False):
    fn, k, x, y, sc, zc = BASE_OUTIL[j]
    P = skinP(s, 8)
    _HOOK[:] = [lambda m: ORN[s](m, x, y, sc, zc)]
    try:
        return fn(k, P, cast=True) if cast else fn(k, P)
    finally:
        _HOOK[:] = []

# ------------------------------------------------------------------ épées et pioches légendaires (formes propres)
def dragon_c(P):
    m = Model("lg_dragon_c", P); manche_epee(m)
    diamond(m, 8, -6.5, 2.4, "glow")
    for a in (-55, -125):
        seg2d(m, (8 + 1.1 * math.cos(math.radians(a)), -5.6 + 1.1 * math.sin(math.radians(a))), [(1.3, 0.6, a), (1.0, 0.45, a + (-35 if a > -90 else 35))], ["trim", "edge"], depth=0.6)
    m.add((6.2, 1.4, 6.6), (9.8, 4.6, 9.4), "plate", name="tete")
    m.add((6.6, 4.6, 6.9), (9.4, 5.6, 9.1), "plate")
    for z0, z1 in ((6.35, 6.6), (9.4, 9.65)):
        m.add((6.6, 3.2, z0), (7.6, 3.9, z1), "glow"); m.add((8.4, 3.2, z0), (9.4, 3.9, z1), "glow")
    for sx in (1, -1):
        seg2d(m, (6.6 if sx == 1 else 9.4, 4.0), [(2.2, 0.9, 200 if sx == 1 else -20), (1.8, 0.6, 235 if sx == 1 else -55), (1.2, 0.4, 260 if sx == 1 else -80)], ["trim", "trim", "edge"], depth=0.9)
        aile(m, 6.2 if sx == 1 else 9.8, 3.6, sx, 150, 4.6)
    mirror(m, (6.7, 5.4, 7.6), (7.3, 6.6, 8.4), "edge", dict(z=-15, origin=[7.0, 5.4, 8]))
    segs = [(5.4, 3.6, 90), (5.0, 3.3, 94), (4.6, 2.9, 99), (3.8, 2.3, 106), (2.8, 1.5, 116), (1.8, 0.8, 130)]
    seg2d(m, (8, 5.4), segs, ["blade"] * 6, depth=1.1)
    seg2d(m, (9.5, 5.4), [(L, 0.55, a) for L, _, a in segs[:5]], ["edge"] * 5, depth=1.35)
    seg2d(m, (7.7, 6.4), [(4.8, 0.6, 91), (4.6, 0.6, 96), (3.8, 0.5, 102), (2.4, 0.4, 110)], ["glow"] * 4, depth=1.3)
    return m.build(sword_display(0.62, 0.0))

def dragon_m(P):
    m = Model("lg_dragon_m", P)
    gen2.manche(m, 6, -6, 12)
    m.add((6.2, 11.6, 6.2), (9.8, 15.6, 9.8), "plate", name="crane")
    m.add((6.7, 15.6, 6.5), (9.3, 17.2, 9.5), "plate")
    for z0, z1 in ((5.95, 6.2), (9.8, 10.05)):
        m.add((6.5, 13.8, z0), (7.4, 14.6, z1), "glow"); m.add((8.6, 13.8, z0), (9.4, 14.6, z1), "glow")
    for sx in (1, -1):
        aile(m, 6.2 if sx == 1 else 9.8, 15.0, sx, 165, 5.0)
        seg2d(m, (7.0 if sx == 1 else 9.0, 17.0), [(2.0, 0.8, 115 if sx == 1 else 65), (1.6, 0.5, 90)], ["trim", "edge"], depth=0.8)
    return m.build(tool_display(0.8, 0.0))

def sculk_c(P):
    m = Model("lg_sculk_c", P); manche_epee(m)
    m.add((6.3, -7.0, 6.3), (9.7, -5.2, 9.7), "plate")
    m.add((6.8, -7.4, 6.8), (9.2, -7.0, 9.2), "glow")
    m.add((5.0, 1.6, 6.8), (11.0, 3.8, 9.2), "trim", name="garde")
    m.add((6.4, 3.8, 7.4), (9.6, 19.6, 8.6), "blade", name="lame")
    tip(m, 8, 19.6, 3.2, 7.4, 8.6, "edge")
    for i, y in enumerate((4.6, 8.4, 12.2)):
        L = 3.6 - 0.4 * i
        for sx in (1, -1):
            x = 6.6 if sx == 1 else 9.4
            seg2d(m, (x, y), [(L, 1.1, 165 if sx == 1 else 15), (L * 0.8, 0.8, 125 if sx == 1 else 55), (L * 0.5, 0.5, 95 if sx == 1 else 85)], ["plate", "plate", "edge"], depth=1.4)
    diamond(m, 8, 10.4, 3.0, "glow", depth=1.8)
    m.add((7.6, 4.4, 7.25), (8.4, 18.6, 8.75), "glow")
    for sx in (1, -1):
        pts = seg2d(m, (8 - 0.8 * sx, 19.8), [(1.6, 0.5, 90 + 25 * sx), (1.6, 0.4, 90 + 5 * sx)], ["plate", "plate"], depth=0.5)
        diamond(m, pts[-1][0], pts[-1][1] + 0.3, 0.9, "glow")
    return m.build(sword_display(0.62, 0.0))

def sculk_m(P):
    m = Model("lg_sculk_m", P)
    gen2.manche(m, 6, -6, 13)
    m.add((6.4, 12.4, 6.4), (9.6, 16.6, 9.6), "plate", name="collier")
    diamond(m, 8, 14.5, 2.4, "glow", depth=3.6)
    pts = seg2d(m, (7.0, 15.4), [(3.6, 2.4, 172), (3.4, 2.0, 198), (3.0, 1.5, 224), (2.4, 0.9, 250)], ["plate", "plate", "plate", "edge"], depth=1.9, mir=True)
    for (x, y), L in zip(pts[:3], (3.0, 2.6, 2.0)):
        for sx in (1, -1):
            xx = x if sx == 1 else 16 - x
            seg2d(m, (xx, y + 0.4), [(L, 0.7, 90 + 30 * sx), (L * 0.6, 0.5, 90 + 5 * sx)], ["plate", "edge"], depth=0.7)
    return m.build(tool_display(0.8, 0.0))

def abysses_c(P):
    m = Model("lg_abysses_c", P)
    m.add((7.3, -4.4, 7.3), (8.7, 1.8, 8.7), "grip")
    for i in range(4):
        y = -4.0 + 1.5 * i
        m.add((6.9, y, 7.0), (9.1, y + 0.55, 9.0), "cloth", dict(z=18, origin=[8, y + 0.3, 8]))
    ring_z(m, 8, -6.2, 1.3, n=10, th=0.5); diamond(m, 8, -6.2, 1.4, "glow")
    ring_z(m, 4.8, 3.0, 2.0, n=12, th=0.8); ring_z(m, 5.2, 3.3, 1.0, n=8, th=0.6)
    m.add((5.8, 1.6, 6.9), (10.4, 3.6, 9.1), "trim", name="garde")
    seg2d(m, (10.4, 2.6), [(2.2, 1.2, 10), (1.8, 1.0, 50), (1.6, 0.8, 110), (1.2, 0.6, 170), (0.8, 0.5, 220)], ["trim", "trim", "plate", "plate", "glow"], depth=1.2)
    m.add((6.4, 3.6, 7.45), (9.6, 13.6, 8.55), "blade", name="lame")
    m.add((7.6, 4.4, 7.3), (8.4, 12.8, 8.7), "glow")
    diamond(m, 8, 14.2, 2.0, "glow", depth=2.0)
    m.add((7.2, 14.6, 7.5), (8.8, 22.0, 8.5), "blade"); tip(m, 8, 22.0, 2.4, 7.5, 8.5, "edge")
    for sx in (1, -1):
        seg2d(m, (8 - 1.6 * sx, 13.4), [(3.2, 1.3, 90 + 35 * sx), (4.0, 1.1, 90 + 4 * sx), (1.8, 0.7, 90 - 14 * sx)], ["blade", "blade", "edge"], depth=1.0)
        seg2d(m, (8 - (3.9 if sx == 1 else -3.9), 17.2), [(1.6, 0.6, 90 - 130 * sx)], ["edge"], depth=0.8)
    return m.build(sword_display(0.62, 0.0))

def abysses_m(P):
    m = Model("lg_abysses_m", P)
    gen2.manche(m, 6, -6, 12)
    for i in range(3):
        y = -3.0 + 3.0 * i
        m.add((7.0, y, 7.0), (9.0, y + 0.6, 9.0), "cloth", dict(z=20, origin=[8, y + 0.3, 8]))
    ring_z(m, 8, 16.2, 1.8, n=12, th=0.6)
    m.add((7.2, 11.0, 7.2), (8.8, 14.6, 8.8), "plate")
    m.add((4.6, 13.2, 7.3), (11.4, 14.2, 8.7), "trim")
    pts = seg2d(m, (7.6, 11.4), [(2.8, 1.9, 185), (2.8, 1.7, 215), (2.4, 1.4, 245), (1.6, 1.0, 270)], ["plate", "plate", "plate", "plate"], depth=1.9, mir=True)
    x, y = pts[-1]
    mirror(m, (x - 1.7, y - 0.6, 7.2), (x + 1.7, y + 1.8, 8.8), "edge", dict(z=40, origin=[x, y, 8]))
    for sx in (1, -1):
        xx = pts[1][0] if sx == 1 else 16 - pts[1][0]
        seg2d(m, (xx, pts[1][1]), [(1.8, 0.6, 250 if sx == 1 else -70), (1.6, 0.5, 290 if sx == 1 else -110), (1.0, 0.4, 250 if sx == 1 else -70)], ["cloth", "cloth", "glow"], depth=0.6)
    return m.build(tool_display(0.8, 0.0))

def eclipse_c(P):
    m = Model("lg_eclipse_c", P); manche_epee(m)
    diamond(m, 8, -6.2, 2.4, "glow")
    m.add((5.2, 1.6, 6.9), (10.8, 3.6, 9.1), "trim", name="garde")
    cy = 7.4
    m.add((5.4, cy - 2.6, 9.0), (10.6, cy + 2.6, 9.25), "plate")
    m.add((5.4, cy - 2.6, 6.75), (10.6, cy + 2.6, 7.0), "plate")
    ring_z(m, 8, cy, 3.6, n=16, th=0.6)
    ring_y(m, 8, cy, 8, 3.0, n=12, th=0.5)
    for k in range(8):
        a = k * 45 + 22.5; r = math.radians(a)
        seg2d(m, (8 + 3.8 * math.cos(r), cy + 3.8 * math.sin(r)), [(1.8, 0.9, a), (1.4, 0.6, a + 25), (0.9, 0.4, a + 45)], ["trim", "glow", "glow"], depth=0.6)
    m.add((6.4, 3.6, 7.4), (9.6, 20.0, 8.6), "blade", name="lame")
    for sx in (1, -1):
        x = 5.8 if sx == 1 else 9.5
        m.add((x, 3.6, 7.55), (x + 0.7, 20.4, 8.45), "trim", dict(z=-1.6 * sx, origin=[x + 0.35, 3.6, 8]))
    for i, y in enumerate((20.0, 21.6, 22.8)):
        w = 3.0 - 0.9 * i
        m.add((8 - w / 2 + (0.4 if i % 2 else -0.4), y, 7.5), (8 + w / 2 + (0.4 if i % 2 else -0.4), y + 1.8, 8.5), "glow" if i == 2 else "trim", dict(z=10 if i % 2 else -10, origin=[8, y, 8]))
    diamond(m, 8, cy, 2.2, "glow", depth=1.6)
    return m.build(sword_display(0.6, 0.0))

def eclipse_m(P):
    m = Model("lg_eclipse_m", P)
    gen2.manche(m, 6, -6, 12)
    ring_z(m, 8, 14.6, 2.4, n=14, th=0.6); ring_y(m, 8, 14.6, 8, 2.0, n=10, th=0.45)
    diamond(m, 8, 14.6, 2.2, "glow")
    seg2d(m, (8.0, 18.0), [(2.8, 1.7, 180), (2.8, 1.6, 205), (2.8, 1.4, 230), (2.6, 1.1, 255), (1.8, 0.6, 278)], ["plate", "plate", "plate", "plate", "trim"], depth=1.8, mir=True)
    for k in range(5):
        a = 30 + k * 30; r = math.radians(a)
        seg2d(m, (8 + 3.0 * math.cos(r), 14.6 + 3.0 * math.sin(r)), [(1.2, 0.6, a), (0.8, 0.4, a + 30)], ["trim", "glow"], depth=0.5)
    m.add((6.8, 17.2, 7.0), (9.2, 19.0, 9.0), "trim")
    return m.build(tool_display(0.8, 0.0))

PROPRES = {("dragon", "c"): dragon_c, ("dragon", "m"): dragon_m, ("sculk", "c"): sculk_c, ("sculk", "m"): sculk_m,
           ("abysses", "c"): abysses_c, ("abysses", "m"): abysses_m, ("eclipse", "c"): eclipse_c, ("eclipse", "m"): eclipse_m}

# ------------------------------------------------------------------ écriture
A = os.path.join(OUT, "assets", "metiers")
NF = 16
def save(mdl, at, gl, S, name):
    t = mdl["textures"]
    for key in list(t):
        t[key] = f"metiers:item/v2/{name}_glow" if key == "glow" else f"metiers:item/v2/{name}"
    os.makedirs(f"{A}/models/item/v2", exist_ok=True); os.makedirs(f"{A}/textures/item/v2", exist_ok=True)
    json.dump(mdl, open(f"{A}/models/item/v2/{name}.json", "w"), separators=(",", ":"))
    Image.fromarray(at, "RGBA").save(f"{A}/textures/item/v2/{name}.png", optimize=True)
    if gl is not None:
        frames = []
        for f in range(NF):
            k = 0.72 + 0.28 * (0.5 + 0.5 * math.cos(2 * math.pi * f / NF))
            g = gl.astype(float); g[..., :3] *= k
            frames.append(np.clip(g, 0, 255).astype(np.uint8))
        Image.fromarray(np.concatenate(frames, 0), "RGBA").save(f"{A}/textures/item/v2/{name}_glow.png", optimize=True)
        json.dump({"animation": {"frametime": 2, "interpolate": True}}, open(f"{A}/textures/item/v2/{name}_glow.png.mcmeta", "w"))

def ref(n): return {"type": "minecraft:model", "model": f"metiers:item/v2/{n}"}
def canne_ref(n): return {"type": "minecraft:condition", "property": "minecraft:fishing_rod/cast", "on_false": ref(n), "on_true": ref(n + "_cast")}

def heaume_sk(k, P):
    if k == 10: return gen.heaume_5("heaume_10", P)
    if k == 9: return gen.heaume_5("heaume_9", P)
    real = gen2.palette
    gen2.palette = lambda kk: P
    try:
        return gen2.heaume(k)
    finally:
        gen2.palette = real

import armorgen2
def worn(k, P, tag):
    armorgen2.T[1000] = dict(metal=[gen2.hexs(c) for c in P["metal"]], trim=[gen2.hexs(c) for c in P["trim"]],
                             cloth=[gen2.hexs(c) for c in P["cloth"]], gem=[gen2.hexs(c) for c in P["gem"]],
                             glow=gen2.hexs(P["glow"][1]), runes=k >= 7, sun=k == 10)
    im1, im2 = armorgen2.worn(1000)
    im1, im2 = gen2.motif(k, im1, P), gen2.motif(k, im2, P, legs=True)
    for d in ("textures/entity/equipment/humanoid", "textures/entity/equipment/humanoid_leggings", "equipment"):
        os.makedirs(f"{A}/{d}", exist_ok=True)
    im1.save(f"{A}/textures/entity/equipment/humanoid/{tag}.png", optimize=True)
    im2.save(f"{A}/textures/entity/equipment/humanoid_leggings/{tag}.png", optimize=True)
    json.dump({"layers": {"humanoid": [{"texture": f"metiers:{tag}"}], "humanoid_leggings": [{"texture": f"metiers:{tag}"}]}},
              open(f"{A}/equipment/{tag}.json", "w"))

JOBS = {"c": gen2.epee, "b": gen2.hache, "m": gen2.pioche, "x": gen2.pelle, "f": gen2.houe, "p": gen2.canne,
        "e": gen2.houlette, "n": gen2.grimoire, "t": gen2.bourse}

def generer():
    shutil.rmtree(OUT, ignore_errors=True)
    n = 0
    # 1. épée du palier 3 refaite, pour la base et les 6 anciens skins
    save(*epee_epine(palette(3)), "c_3"); n += 1
    for s in gen4.SKINS:
        save(*epee_epine(skinP(s, 3), f"c_3_{s}"), f"c_3_{s}"); n += 1
    # 2. palettes Sakura et Céleste sur les 11 paliers de chaque outil, nouveaux skins sur le heaume et l'armure portée
    for s in NEW:
        for k in range(11):
            if s not in LEGENDAIRES:
                for j, fn in JOBS.items():
                    P = skinP(s, k)
                    save(*(epee_epine(P, f"c_3_{s}") if (j, k) == ("c", 3) else fn(k, P)), f"{j}_{k}_{s}"); n += 1
                    if j == "p":
                        save(*gen2.canne(k, P, cast=True), f"p_{k}_{s}_cast"); n += 1
            save(*heaume_sk(k, skinP(s, k)), f"heaume_{k}_{s}"); n += 1
            worn(k, skinP(s, k), f"guilde_{k}_{s}")
    # 3. formes légendaires : une par outil, la même à tous les paliers
    for s in LEGENDAIRES:
        for j in JOBS:
            if (s, j) in PROPRES:
                save(*PROPRES[(s, j)](skinP(s, 8)), f"lg_{s}_{j}")
            else:
                save(*legendaire_base(s, j), f"lg_{s}_{j}")
                if j == "p":
                    save(*legendaire_base(s, j, cast=True), f"lg_{s}_{j}_cast")
            n += 1
    return n

def items_maj(z):
    """Ajoute les nouveaux skins dans les sélecteurs d'objets existants (outils et heaumes)."""
    os.makedirs(f"{A}/items", exist_ok=True)
    for j in JOBS:
        for k in range(11):
            p = f"assets/metiers/items/{j}_{k}.json"
            d = json.loads(z.read(p))
            cases = [c for c in d["model"]["cases"] if c["when"] not in NEW]
            for s in NEW:
                if s in LEGENDAIRES:
                    mod = canne_ref(f"lg_{s}_{j}") if j == "p" else ref(f"lg_{s}_{j}")
                else:
                    mod = canne_ref(f"{j}_{k}_{s}") if j == "p" else ref(f"{j}_{k}_{s}")
                cases.append({"when": s, "model": mod})
            d["model"]["cases"] = cases
            json.dump(d, open(f"{A}/items/{j}_{k}.json", "w"), separators=(",", ":"))
    for k in range(11):
        p = f"assets/metiers/items/heaume_{k}.json"
        d = json.loads(z.read(p))
        d["model"]["cases"] = [c for c in d["model"]["cases"] if c["when"] not in NEW] + [{"when": s, "model": ref(f"heaume_{k}_{s}")} for s in NEW]
        json.dump(d, open(f"{A}/items/heaume_{k}.json", "w"), separators=(",", ":"))

def fusionner():
    with open(ZIP, "rb") as f:
        ancien = zipfile.ZipFile(io.BytesIO(f.read()))
    items_maj(ancien)
    neufs = {}
    for dp, _, fs in os.walk(OUT):
        for fn in fs:
            full = os.path.join(dp, fn)
            neufs[os.path.relpath(full, OUT).replace(os.sep, "/")] = full
    sortie = io.BytesIO()
    with zipfile.ZipFile(sortie, "w", zipfile.ZIP_DEFLATED) as z:
        for info in ancien.infolist():
            if info.filename in neufs: continue
            z.writestr(info, ancien.read(info))
        for arc in sorted(neufs):
            zi = zipfile.ZipInfo(arc, date_time=(2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, open(neufs[arc], "rb").read())
    data = sortie.getvalue()
    open(ZIP, "wb").write(data)
    print(f"{len(neufs)} fichiers versés dans metiers_resourcepack.zip")
    print("SHA-1 :", hashlib.sha1(data).hexdigest())

if __name__ == "__main__":
    print(generer(), "modèles")
    fusionner()

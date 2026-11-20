"""Objets de la Forge : objets de métier, objets communs et cristaux d'amélioration (modèles 3D + définitions d'objet)."""
import sys, math
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else "."]
import gen2
from gen2 import Model, mirror, diamond, seg2d, ring_z, ring_y, manche, palette, save, item_def, ref, tool_display, R, hx, light, dark, tip
from gen import chain

NETH = palette(5)

def pal(metal=None, glow=None, trim=None, cloth=None, grip=None, gem=None):
    P = dict(palette(4))
    if metal: P["metal"] = R(metal); P["blade"] = R(metal[:5])
    if glow: P["glow"] = R(glow)
    if trim: P["trim"] = R(trim)
    if cloth: P["cloth"] = R(cloth)
    if grip: P["grip"] = R(grip)
    if gem: P["gem"] = R(gem)
    return P

GOLD = ["#3a2a06", "#6b4a0b", "#c9972a", "#ffe08a"]
DARK = ["#0e0b0d", "#221c20", "#332a30", "#4a3e45", "#75666e", "#a89aa2"]

def marteau():
    P = pal(metal=DARK, glow=["#b0601a", "#ff9a3a", "#ffe0b0"], trim=GOLD)
    m = Model("forge_marteau", P)
    manche(m, 3, -7, 12)
    m.add((2.2, 11.0, 5.4), (13.8, 18.2, 10.6), "plate", name="tete")
    for x0, x1 in ((1.4, 2.2), (13.8, 14.6)): m.add((x0, 10.4, 4.8), (x1, 18.8, 11.2), "trim")
    m.add((5.0, 18.2, 6.6), (11.0, 19.2, 9.4), "plate")
    for x in (4.4, 8.0, 11.6): m.add((x - 0.9, 13.6, 5.0), (x + 0.9, 15.6, 5.4), "glow")
    for x in (4.4, 8.0, 11.6): m.add((x - 0.9, 13.6, 10.6), (x + 0.9, 15.6, 11.0), "glow")
    diamond(m, 8, 21.0, 2.0, "glow", extra_rot=dict(y=30))
    return m.build(tool_display(0.62, 4))

def faux():
    P = pal(metal=["#0b2310", "#1d5a2a", "#2f9a48", "#7ad88a", "#d8ffe0", "#ffffff"], glow=["#2a8a3a", "#7cff8a", "#e0ffe4"], trim=GOLD,
            grip=["#2e1d0e", "#5c3a1d", "#7f532c", "#a3713f"])
    m = Model("forge_faux", P)
    manche(m, 3, -8, 18)
    m.add((6.8, 17.0, 6.8), (9.2, 19.6, 9.2), "trim")
    seg2d(m, (7.0, 18.6), [(4.0, 2.4, 182), (3.8, 2.2, 202), (3.6, 1.9, 224), (3.2, 1.5, 246), (2.6, 1.1, 266), (2.0, 0.7, 284)],
          ["plate", "blade", "blade", "blade", "edge", "edge"], depth=1.0)
    seg2d(m, (8.0, 3.0), [(3.0, 1.0, 20)], ["grip"], depth=1.0)
    for (x, y) in ((9.6, 21.0), (2.0, 22.0)):
        m.add((x - 0.4, y, 7.6), (x + 0.4, y + 2.2, 8.4), "glow", dict(z=-20, origin=[x, y, 8]))
        diamond(m, x + 0.4, y + 2.6, 1.2, "glow")
    return m.build(tool_display(0.62, 4))

def arc3():
    P = pal(metal=["#2a0606", "#5e1010", "#9c2424", "#d24848", "#ff9a9a", "#ffe0e0"], glow=["#a01818", "#ff4a4a", "#ffd0d0"], trim=GOLD,
            grip=["#1f0d12", "#41192a", "#5f2640", "#7f3858"], cloth=["#2a0606", "#5e1010", "#9c2424", "#d24848"])
    m = Model("forge_arc3", P)
    m.add((7.2, 5.4, 7.4), (8.8, 10.6, 8.6), "grip")
    up = [(3.4, 1.6, 100), (3.2, 1.4, 118), (3.0, 1.2, 136), (2.6, 1.0, 152)]
    pu = seg2d(m, (8, 10.8), up, ["plate", "plate", "plate", "trim"])
    pd = seg2d(m, (8, 5.2), [(L, t, -a) for (L, t, a) in up], ["plate", "plate", "plate", "trim"])
    tx, ty = pu[-1]; bx, by = pd[-1]
    sx = tx + 3.0
    for (ax, ay) in ((tx, ty), (bx, by)):
        dx, dy = sx - ax, 8 - ay; L = math.hypot(dx, dy); a = math.degrees(math.atan2(dy, dx)); cx, cy = (ax + sx) / 2, (ay + 8) / 2
        m.add((cx - L / 2, cy - 0.15, 7.85), (cx + L / 2, cy + 0.15, 8.15), "string", dict(z=a, origin=[cx, cy, 8]))
    for ang in (-12, 0, 12):
        r = math.radians(ang); L = 14
        cx, cy = sx - math.cos(r) * L / 2, 8 + math.sin(-r) * L / 2
        m.add((cx - L / 2, cy - 0.18, 7.82), (cx + L / 2, cy + 0.18, 8.18), "grip", dict(z=-ang, origin=[cx, cy, 8]))
        ex, ey = sx - math.cos(r) * L, 8 - math.sin(r) * L
        diamond(m, ex, ey, 1.6, "glow", depth=0.5)
    m.add((7.0, 7.0, 7.0), (9.0, 9.0, 9.0), "glow", dict(z=45, origin=[8, 8, 8]))
    return m.build(gen2.arc(9, palette(9))[0]["display"] if False else {"gui": {"rotation": [0, 0, -45], "scale": [0.8, 0.8, 0.8]},
                    "thirdperson_righthand": {"rotation": [-80, 260, -40], "translation": [-1, -2, 2.5], "scale": [0.9, 0.9, 0.9]},
                    "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]}})

def lasso():
    P = pal(metal=["#2e1d0e", "#5c3a1d", "#8a5a2c", "#b88a4f", "#e0c08a", "#fff0d0"], glow=["#9a3a9a", "#ff70e8", "#ffe0fa"], trim=GOLD,
            grip=["#3a2416", "#6b4424", "#9a6a3a", "#c8955a"])
    m = Model("forge_lasso", P)
    for r, y, n in ((5.2, 6.0, 16), (4.6, 7.2, 14), (4.0, 8.4, 12)):
        ring_y_mat(m, 8, y, 8, r, n, "plate", 1.0)
    seg2d(m, (12.6, 8.4), [(3.0, 1.0, 70), (3.0, 1.0, 100), (2.6, 1.0, 140), (2.4, 1.0, 190)], ["plate"] * 4, depth=1.0)
    m.add((6.6, 12.0, 7.0), (8.6, 14.0, 9.0), "trim")
    m.add((7.0, 4.4, 2.6), (9.0, 6.4, 3.4), "glow", dict(z=45, origin=[8, 5.4, 3.0]))
    d = tool_display(0.62, 4); d["gui"] = {"rotation": [30, 30, 0], "scale": [0.85, 0.85, 0.85]}
    return m.build(d)

def ring_y_mat(m, cx, cy, cz, Rr, n, mat, th):
    for k in range(n):
        t = 2 * math.pi * k / n
        px, pz = cx + Rr * math.cos(t), cz + Rr * math.sin(t)
        L = 2 * Rr * math.tan(math.pi / n) + 0.1
        m.add((px - L / 2, cy - th / 2, pz - th / 2), (px + L / 2, cy + th / 2, pz + th / 2), mat, dict(y=-(math.degrees(t) + 90), origin=[px, cy, pz]))

def parchemin():
    P = pal(metal=["#7a5a2a", "#a88050", "#d8bc8a", "#efe2c2", "#fff6e2", "#ffffff"], glow=["#5a1aa0", "#b07cff", "#f0e0ff"], trim=GOLD,
            cloth=["#3a0a0a", "#6a1414", "#9a2020", "#c83030"])
    m = Model("forge_parchemin", P)
    m.add((2.6, 4.0, 7.7), (13.4, 12.0, 8.3), "page", name="feuille")
    for y in (3.0, 12.2):
        m.add((2.0, y - 1.0, 7.0), (14.0, y + 1.0, 9.0), "plate")
        m.add((1.2, y - 0.6, 7.4), (2.0, y + 0.6, 8.6), "trim"); m.add((14.0, y - 0.6, 7.4), (14.8, y + 0.6, 8.6), "trim")
    m.add((6.8, 6.4, 7.4), (9.2, 8.8, 7.7), "cloth", name="sceau")
    m.add((7.4, 7.0, 7.1), (8.6, 8.2, 7.4), "glow", dict(z=45, origin=[8, 7.6, 7.25]))
    for x in (4.0, 5.6, 10.4, 12.0): m.add((x - 0.2, 9.4, 7.65), (x + 0.2, 10.8, 7.7), "glow")
    d = tool_display(0.62, 8); d["gui"] = {"rotation": [0, 20, 0], "scale": [0.85, 0.85, 0.85]}
    return m.build(d)

def aimant():
    P = pal(metal=["#3a0606", "#7a1010", "#c02020", "#e85050", "#ffa0a0", "#ffe0e0"], glow=["#2a6aa0", "#7cd0ff", "#e0f6ff"], trim=["#3d4046", "#8d929b", "#d8dce2", "#ffffff"])
    m = Model("forge_aimant", P)
    seg2d(m, (3.6, 4.0), [(3.0, 2.6, 90), (2.4, 2.6, 60), (2.4, 2.6, 30), (2.4, 2.6, 0), (2.4, 2.6, -30), (2.4, 2.6, -60), (3.0, 2.6, -90)],
          ["plate"] * 7, depth=2.6)
    for x in (3.6, 12.4): m.add((x - 1.35, 1.6, 6.7), (x + 1.35, 4.0, 9.3), "trim")
    for (x, y) in ((2.0, -1.0), (8.0, -2.4), (14.0, -1.0)): diamond(m, x, y, 1.4, "glow", extra_rot=dict(y=30))
    d = tool_display(0.62, 4); d["gui"] = {"rotation": [0, 20, 0], "scale": [0.85, 0.85, 0.85]}
    return m.build(d)

def cape():
    P = pal(metal=GOLD + ["#ffe08a", "#fff6c8"], cloth=["#0a1230", "#172a64", "#2848a8", "#5277dc"], glow=["#2a6aa0", "#7cd0ff", "#e0f6ff"], trim=GOLD)
    m = Model("forge_cape", P)
    m.add((3.0, 14.0, 7.0), (13.0, 15.6, 9.0), "trim", name="col")
    for i, (x0, x1, a) in enumerate(((2.0, 6.0, -8), (6.0, 10.0, 0), (10.0, 14.0, 8))):
        m.add((x0, 1.0, 7.6), (x1, 14.2, 8.4), "cloth", dict(z=a, origin=[(x0 + x1) / 2, 14.2, 8]))
    mirror(m, (-2.0, 4.0, 7.7), (2.4, 13.6, 8.3), "cloth", dict(z=-24, origin=[2.4, 13.6, 8]))
    m.add((7.0, 14.2, 6.6), (9.0, 16.2, 7.0), "glow", dict(z=45, origin=[8, 15.2, 6.8]))
    d = tool_display(0.62, 4); d["gui"] = {"rotation": [0, 20, 0], "scale": [0.85, 0.85, 0.85]}
    return m.build(d)

CRISTAUX = {"sagesse": ["#0d3a5a", "#2f9ae0", "#c0ecff"], "fortune": ["#0b3d24", "#2fd07a", "#c9ffe0"],
            "echo": ["#2a0a4a", "#8a3cff", "#e8d0ff"], "efficacite": ["#5a3a04", "#ffc83a", "#fff1b0"]}
def cristal(nom):
    g = CRISTAUX[nom]
    P = pal(metal=GOLD + ["#ffe08a", "#fff6c8"], glow=g, gem=[g[0], g[1], g[2], "#ffffff"], trim=GOLD)
    m = Model(f"forge_cristal_{nom}", P)
    m.add((4.4, 1.0, 4.4), (11.6, 3.0, 11.6), "trim", name="socle")
    m.add((5.4, 3.0, 5.4), (10.6, 4.0, 10.6), "plate")
    shapes = {"sagesse": [(8, 4, 0, 3.4, 9.0)], "fortune": [(8, 4, 0, 3.0, 7.0), (5.6, 4, 24, 1.8, 4.4), (10.4, 4, -24, 1.8, 4.4)],
              "echo": [(8, 4, 0, 2.6, 8.0), (8, 13.2, 0, 1.6, 2.4)], "efficacite": [(7.0, 4, 10, 2.2, 8.0), (9.4, 4, -14, 2.0, 6.4), (8, 4, 0, 1.6, 10.0)]}
    for (x, y, a, w, h) in shapes[nom]:
        m.add((x - w / 2, y, 8 - w / 2), (x + w / 2, y + h, 8 + w / 2), "glow", dict(z=a, y=45, origin=[x, y, 8]))
        diamond(m, x - math.sin(math.radians(a)) * h, y + math.cos(math.radians(a)) * h, w, "glow", extra_rot=dict(y=45))
    if nom == "echo": ring_y(m, 8, 9.0, 8, 4.2, n=12)
    d = tool_display(0.62, 4); d["gui"] = {"rotation": [25, 30, 0], "scale": [0.85, 0.85, 0.85]}
    return m.build(d)

if __name__ == "__main__":
    fns = [marteau, faux, arc3, lasso, parchemin, aimant, cape] + [(lambda n=n: cristal(n)) for n in CRISTAUX]
    for fn in fns:
        mdl, at, gl, S = fn()
        name = [e for e in ("forge_marteau", "forge_faux", "forge_arc3", "forge_lasso", "forge_parchemin", "forge_aimant", "forge_cape")
                if fn is not None][0]
        n = mdl["textures"]["atlas"].split("/")[-1]
        save(mdl, at, gl, S, n)
        item_def(n, ref(n))
    print("forge ok")

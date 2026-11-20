"""Prototypes refonte : heaumes 3D (rare, légendaire) et épées 3D (commune, rare, légendaire).
Chaque face d'élément a sa propre zone peinte dans l'atlas, à densité constante (2 px par unité),
pour que la texture suive le volume au lieu d'être étirée."""
import os, sys, json, math, hashlib
import numpy as np
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
D = 2  # px de texture par unité de modèle
NF = 16  # frames d'animation des pièces lumineuses

def hx(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)

def R(lst): return [hx(c) for c in lst]

def hsh(*a):
    return int(hashlib.md5(repr(a).encode()).hexdigest()[:6], 16) / 0xFFFFFF

# ------------------------------------------------------------------ peinture par matériau
def paint(mat, w, h, P, seed, face):
    a = np.zeros((h, w, 3))
    if mat in ("plate", "visor", "grill", "cap"):
        m = P["metal"]
        for y in range(h):
            for x in range(w):
                c = m[3]
                if mat == "cap": c = m[3] * 0.6 + m[4] * 0.4
                if y % 6 == 5 and mat != "cap": c = m[2]
                n = hsh(seed, x, y)
                if n < 0.08: c = m[2]
                elif n > 0.94: c = m[4]
                a[y, x] = c
        a[0, :] = m[4]; a[:, 0] = m[4] * 0.6 + m[3] * 0.4
        a[h - 1, :] = m[1]; a[:, w - 1] = m[2]
        if h > 2 and w > 2:
            a[0, 0] = m[5]
        if w >= 12 and h >= 12 and mat == "plate":
            for (x, y) in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)):
                a[y, x] = m[5]; a[min(h - 1, y + 1), x] = m[1]
        if mat in ("visor", "grill"):
            sy = int(h * 0.38); x0, x1 = int(w * 0.14), int(w * 0.86)
            dark = P["metal"][0] * 0.5
            a[sy:sy + 2, x0:x1] = dark
            a[sy - 1, x0:x1] = m[1]; a[sy + 2, x0:x1] = m[4]
            if mat == "visor":
                cx = w // 2
                a[sy:int(h * 0.78), cx - 1:cx + 1] = dark
                a[sy + 2:int(h * 0.78), cx + 1] = m[4]
            else:
                for yy in range(int(h * 0.58), int(h * 0.86), 3):
                    for xx in range(int(w * 0.56), int(w * 0.84), 3):
                        a[yy, xx] = dark; a[yy + 1, xx] = m[4]
    elif mat == "trim":
        t = P["trim"]
        a[:] = t[2]
        a[0, :] = t[3]; a[h - 1, :] = t[0]
        if h >= 4:
            cy = h // 2
            for x in range(1, w - 1, 3): a[cy, x] = t[3]; a[cy + 1 if cy + 1 < h - 1 else cy, x] = t[1]
        if w >= 4: a[:, 0] = t[3] * 0.5 + t[2] * 0.5; a[:, w - 1] = t[1]
    elif mat == "gem":
        g = P["gem"]
        for y in range(h):
            for x in range(w):
                u, v = x / max(1, w - 1), y / max(1, h - 1)
                c = g[1]
                if u + v < 0.8: c = g[2]
                if u + v > 1.4: c = g[0]
                a[y, x] = c
        a[min(1, h - 1), min(1, w - 1)] = g[3]
    elif mat == "cloth":
        c = P["cloth"]
        for y in range(h):
            for x in range(w):
                a[y, x] = c[2] if (x // 2) % 2 == 0 else c[1]
                if hsh(seed, x, y) < 0.06: a[y, x] = c[3]
        a[0, :] = c[3]; a[h - 1, :] = c[0]
    elif mat == "feather":
        m = P["feather"]
        for y in range(h):
            for x in range(w):
                c = m[2]
                if (x + y) % 3 == 0: c = m[1]
                a[y, x] = c
        if face in ("east", "west"):
            a[h // 2, :] = m[3]
        a[0, :] = m[3]; a[h - 1, :] = m[0]
    elif mat in ("blade", "runeblade", "edge"):
        b = P["blade"]
        for y in range(h):
            for x in range(w):
                c = b[2] * 0.45 + b[3] * 0.55
                if face in ("north", "south"):
                    u = x / max(1, w - 1)
                    if abs(u - 0.5) < 0.12: c = b[2]
                    if abs(u - 0.5) < 0.05: c = b[1] * 0.4 + b[2] * 0.6
                    if x == 0 or x == w - 1: c = b[4]
                    if hsh(seed, x // 2, y // 3) > 0.93: c = b[4] * 0.6 + c * 0.4
                else:
                    c = b[4] if face in ("east", "west") else b[2]
                a[y, x] = c
        if mat == "runeblade" and face in ("north", "south") and w >= 5:
            r = P["rune"]
            cx = w // 2
            for y0 in range(3, h - 4, 7):
                pat = [(0, 0), (1, 1), (0, 2), (-1, 1), (0, 3)] if (y0 // 7) % 2 == 0 else [(0, 0), (0, 1), (1, 2), (-1, 2), (0, 3)]
                for dx, dy in pat:
                    if 0 <= y0 + dy < h: a[y0 + dy, cx + dx] = r
    elif mat == "grip":
        g = P["grip"]
        for y in range(h):
            for x in range(w):
                a[y, x] = g[2] if ((x + y) // 2) % 2 == 0 else g[1]
        a[:, 0] = g[0] * 0.5 + g[1] * 0.5
        for y in range(0, h, 7): a[y, :] = P["trim"][2]
    elif mat == "page":
        for y in range(h):
            for x in range(w):
                a[y, x] = hx("#efe6cf") if (y % 2 == 0) else hx("#d9cdae")
        a[:, 0] = hx("#b8aa88")
    elif mat == "leather":
        c = P["cloth"]
        for y in range(h):
            for x in range(w):
                a[y, x] = c[2] if hsh(seed, x, y) > 0.12 else c[1]
        a[0, :] = c[3]; a[:, 0] = c[3] * 0.5 + c[2] * 0.5; a[h - 1, :] = c[0]; a[:, w - 1] = c[1]
        if w > 6 and h > 6:
            a[2, 2:w - 2] = P["trim"][2]; a[h - 3, 2:w - 2] = P["trim"][2]; a[2:h - 2, 2] = P["trim"][2]; a[2:h - 2, w - 3] = P["trim"][2]
    elif mat == "string":
        a[:] = hx("#f2efe6")
    elif mat == "glow":
        gl = P["glow"]
        for y in range(h):
            for x in range(w):
                u, v = (x + 0.5) / w - 0.5, (y + 0.5) / h - 0.5
                d = min(1, math.hypot(u, v) * 1.7)
                a[y, x] = gl[2] * (1 - d) + gl[1] * d
        a[0, :] = gl[1] * 0.7 + gl[0] * 0.3; a[h - 1, :] = gl[0]
    return np.clip(a, 0, 255)

# ------------------------------------------------------------------ modèle
FACES = ("north", "south", "east", "west", "up", "down")

class Model:
    def __init__(self, name, P):
        self.name, self.P, self.els = name, P, []
    def add(self, frm, to, mat, rot=None, over=None, name=None):
        self.els.append(dict(frm=list(frm), to=list(to), mat=mat, rot=rot, over=over or {}, name=name))
        return self
    def build(self, display):
        rects = []
        for i, e in enumerate(self.els):
            dx, dy, dz = (e["to"][k] - e["frm"][k] for k in range(3))
            for f in FACES:
                w, h = {"north": (dx, dy), "south": (dx, dy), "east": (dz, dy), "west": (dz, dy), "up": (dx, dz), "down": (dx, dz)}[f]
                wp, hp = max(1, round(w * D)), max(1, round(h * D))
                mat = e["over"].get(f, e["mat"])
                rects.append(dict(i=i, f=f, w=wp, h=hp, mat=mat))
        S = 64
        while True:
            ok = self._pack(rects, S)
            if ok: break
            S *= 2
        atlas = np.zeros((S, S, 4)); glow = np.zeros((S, S, 4))
        any_glow = False
        for r in rects:
            img = paint(r["mat"], r["w"], r["h"], self.P, (self.name, r["i"], r["f"]), r["f"])
            tgt = glow if r["mat"] == "glow" else atlas
            any_glow |= r["mat"] == "glow"
            tgt[r["y"]:r["y"] + r["h"], r["x"]:r["x"] + r["w"], :3] = img
            tgt[r["y"]:r["y"] + r["h"], r["x"]:r["x"] + r["w"], 3] = 255
        k = 16 / S
        elements = []
        for i, e in enumerate(self.els):
            el = {"from": [round(v, 3) for v in e["frm"]], "to": [round(v, 3) for v in e["to"]], "faces": {}}
            if e["name"]: el["name"] = e["name"]
            if e["rot"]:
                rr = {ax: e["rot"][ax] for ax in ("x", "y", "z") if e["rot"].get(ax)}
                rr["origin"] = e["rot"]["origin"]
                el["rotation"] = rr
            for r in [r for r in rects if r["i"] == i]:
                el["faces"][r["f"]] = {"uv": [round(r["x"] * k, 4), round(r["y"] * k, 4), round((r["x"] + r["w"]) * k, 4), round((r["y"] + r["h"]) * k, 4)],
                                       "texture": "#glow" if r["mat"] == "glow" else "#atlas"}
            elements.append(el)
        tex = {"atlas": f"metiers:item/proto/{self.name}", "particle": f"metiers:item/proto/{self.name}"}
        if any_glow: tex["glow"] = f"metiers:item/proto/{self.name}_glow"
        model = {"texture_size": [S, S], "textures": tex, "elements": elements, "display": display}
        return model, atlas.astype(np.uint8), (glow.astype(np.uint8) if any_glow else None), S

    @staticmethod
    def _pack(rects, S):
        x = y = rowh = 0
        for r in sorted(rects, key=lambda r: (-r["h"], -r["w"])):
            if r["w"] > S: return False
            if x + r["w"] > S: x, y, rowh = 0, y + rowh, 0
            if y + r["h"] > S: return False
            r["x"], r["y"] = x, y
            x += r["w"]; rowh = max(rowh, r["h"])
        return True

def mirror(m, frm, to, mat, rot=None, over=None):
    """Ajoute l'élément et son symétrique par rapport au plan x = 8."""
    m.add(frm, to, mat, rot, over)
    f2 = [16 - to[0], frm[1], frm[2]]; t2 = [16 - frm[0], to[1], to[2]]
    r2 = None
    if rot:
        r2 = dict(rot); r2["origin"] = [16 - rot["origin"][0], rot["origin"][1], rot["origin"][2]]
        if "y" in r2: r2["y"] = -r2["y"]
        if "z" in r2: r2["z"] = -r2["z"]
    m.add(f2, t2, mat, r2, over)

# ------------------------------------------------------------------ palettes (reprises du pack actuel)
GUILDE = {
    3: dict(metal=R(["#241602", "#5e3f06", "#9a6c0c", "#d09e24", "#f0cc4c", "#fff3bc"]), trim=R(["#300407", "#6e0b16", "#a81628", "#e2485a"]),
            cloth=R(["#24040a", "#520a16", "#8a1224", "#c02a3c"]), gem=R(["#4a0710", "#c8142f", "#ff6a80", "#ffe4ea"]),
            glow=R(["#7a0a18", "#ff3a50", "#ffd0d8"]), feather=R(["#5e3f06", "#d09e24", "#f0cc4c", "#fff3bc"])),
    5: dict(metal=R(["#3f2d06", "#8c6c22", "#c4a456", "#e8d283", "#fbf0cc", "#ffffff"]), trim=R(["#5a3e08", "#b8861e", "#f2c63c", "#fff6c8"]),
            cloth=R(["#30040a", "#6e0a16", "#b0122a", "#e8485c"]), gem=R(["#6a4a08", "#e8b020", "#fff07a", "#ffffff"]),
            glow=R(["#c08a10", "#ffe27a", "#ffffff"]), feather=R(["#c9b47a", "#fff4d6", "#ffffff", "#ffffff"])),
}
OUTIL = {
    0: dict(blade=R(["#25262b", "#5d6169", "#8d929b", "#bcc1c9", "#eef1f5"]), grip=R(["#2e1d0e", "#5c3a1d", "#7f532c", "#a3713f"]),
            metal=R(["#25262b", "#3d4046", "#5d6169", "#8d929b", "#bcc1c9", "#eef1f5"]), trim=R(["#2e1d0e", "#5c3a1d", "#7f532c", "#a3713f"])),
    5: dict(blade=R(["#24103a", "#552886", "#844cc2", "#b787ec", "#f3e7ff"]), grip=R(["#1f0d12", "#41192a", "#5f2640", "#7f3858"]),
            metal=R(["#24103a", "#3a1c5e", "#552886", "#844cc2", "#b787ec", "#f3e7ff"]), trim=R(["#5b4310", "#8a6a1c", "#b58c2a", "#ecd27a"]),
            gem=R(["#4a0f2e", "#d03a86", "#ffc3e3", "#ffffff"]), glow=R(["#7a1a50", "#ff5aa8", "#ffe0f0"])),
    9: dict(blade=R(["#04100e", "#0b2b27", "#135a52", "#1f9b8a", "#93f7e3"]), grip=R(["#0f0a18", "#22163a", "#352457", "#4c3678"]),
            metal=R(["#04100e", "#0b2b27", "#135a52", "#1f9b8a", "#5fd9c6", "#c8fff4"]), trim=R(["#1e3e44", "#3b6f7a", "#7fd6e0", "#e6ffff"]),
            gem=R(["#3b0d63", "#b45cff", "#f0d9ff", "#ffffff"]), glow=R(["#5a1aa0", "#c27bff", "#ffffff"]), rune=hx("#d79bff")),
}

# ------------------------------------------------------------------ heaumes
HEAD_DISPLAY = {"head": {"translation": [0, 0, 0], "scale": [1, 1, 1]},
                "gui": {"rotation": [25, 210, 0], "translation": [0, -1.5, 0], "scale": [0.5, 0.5, 0.5]},
                "ground": {"translation": [0, 2, 0], "scale": [0.3, 0.3, 0.3]},
                "fixed": {"scale": [0.5, 0.5, 0.5]},
                "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.3, 0.3, 0.3]},
                "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.3, 0.3, 0.3]}}

def gorget(m, mat="plate"):
    m.add((2.6, -0.2, 0.5), (13.4, 2.2, 1.9), mat, dict(x=12, origin=[8, 2.2, 1.2]))
    m.add((2.6, -0.2, 14.1), (13.4, 2.2, 15.5), mat, dict(x=-12, origin=[8, 2.2, 14.8]))
    mirror(m, (0.5, -0.2, 2.6), (1.9, 2.2, 13.4), mat, dict(z=-12, origin=[1.2, 2.2, 8]))

def chain(m, start, segs, mats, side_mirror=True):
    """Corne ou panache en segments : chaque segment est orienté selon (montée u, avancée f) en degrés."""
    x, y, z = start
    for k, (L, th, u, f) in enumerate(segs):
        ur, fr = math.radians(u), math.radians(f)
        d = (-math.cos(ur) * math.cos(fr), math.sin(ur), -math.cos(ur) * math.sin(fr))
        cx, cy, cz = x + d[0] * L / 2, y + d[1] * L / 2, z + d[2] * L / 2
        e = (-d[0], -d[1], -d[2])
        phi = -math.degrees(math.asin(max(-1, min(1, e[2]))))
        psi = math.degrees(math.atan2(e[1], e[0]))
        rot = dict(y=round(phi, 2), z=round(psi, 2), origin=[round(cx, 3), round(cy, 3), round(cz, 3)])
        frm = (cx - L / 2 - 0.15, cy - th / 2, cz - th / 2); to = (cx + L / 2 + 0.15, cy + th / 2, cz + th / 2)
        (mirror if side_mirror else m.add)(*( (m, frm, to, mats[k], rot) if side_mirror else (frm, to, mats[k], rot) ))
        x, y, z = x + d[0] * L, y + d[1] * L, z + d[2] * L

def coque(m, face):
    m.add((0.8, 1.2, 0.8), (15.2, 15.0, 15.2), "plate", over={"north": face}, name="coque")
    m.add((1.8, 15.0, 1.8), (14.2, 16.2, 14.2), "cap")
    m.add((3.6, 16.2, 3.6), (12.4, 17.0, 12.4), "cap")
    m.add((0.4, 10.6, 0.4), (15.6, 12.0, 15.6), "trim", name="bandeau")
    m.add((7.2, 2.0, 0.05), (8.8, 10.6, 1.65), "plate", dict(y=45, origin=[8, 6.3, 0.85]), name="arete")
    gorget(m)
    mirror(m, (0.0, 1.4, 1.2), (1.4, 9.8, 7.4), "plate", dict(y=-18, origin=[0.7, 5.6, 4.3]))

def heaume_5(name="heaume_5", P=None, extra=None):
    m = Model(name, P or GUILDE[5])
    coque(m, "visor")
    for a, L in ((-66, 3.4), (-34, 5.0), (0, 6.6), (34, 5.0), (66, 3.4)):
        ra = math.radians(a); cx, cz = 8 + 6.2 * math.sin(ra), 8 - 6.2 * math.cos(ra)
        m.add((cx - 0.6, 15.4, cz - 0.6), (cx + 0.6, 15.4 + L, cz + 0.6), "trim", dict(x=-18, y=-a, origin=[cx, 15.4, cz]))
    m.add((7.2, 22.0, 0.6), (8.8, 23.6, 2.2), "glow", dict(z=45, origin=[8, 22.8, 1.4]))
    m.add((5.9, 10.2, 0.0), (10.1, 14.2, 0.9), "trim")
    m.add((7.0, 11.1, -0.5), (9.0, 13.1, 0.3), "glow", dict(z=45, origin=[8, 12.1, -0.1]))
    # ailes : quatre rémiges par côté, en éventail vers l'arrière et le haut
    for i, (L, pitch) in enumerate(((16.5, -6), (15.0, -22), (13.0, -38), (10.5, -54), (8.0, -70))):
        y0 = 8.2 + i * 0.5
        mirror(m, (-0.6, y0, 7.6), (0.4, y0 + 2.2, 7.6 + L), "feather", dict(x=pitch, y=-38, origin=[-0.1, y0 + 1.1, 7.6]))
    mirror(m, (-0.9, 7.8, 6.0), (1.1, 11.6, 9.4), "trim")
    m.add((6.9, 13.6, 14.8), (9.1, 15.6, 15.6), "trim")
    # auréole flottante
    Rh, n = 6.6, 16
    for k in range(n):
        th = 2 * math.pi * k / n
        cx, cz = 8 + Rh * math.cos(th), 8 + Rh * math.sin(th)
        L = 2 * Rh * math.tan(math.pi / n) + 0.15
        m.add((cx - L / 2, 25.0, cz - 0.4), (cx + L / 2, 25.8, cz + 0.4), "glow", dict(y=-(math.degrees(th) + 90), origin=[cx, 25.4, cz]))
    if extra: extra(m)
    return m.build(HEAD_DISPLAY)

def heaume_3(name="heaume_3", P=None, extra=None):
    m = Model(name, P or GUILDE[3])
    coque(m, "grill")
    # crête haute en trois étages
    m.add((7.1, 15.6, 1.6), (8.9, 18.4, 14.4), "plate", name="crete")
    m.add((7.2, 18.4, 2.8), (8.8, 20.6, 13.0), "plate")
    m.add((7.35, 20.6, 4.6), (8.65, 22.0, 11.0), "trim")
    m.add((7.2, 18.6, 0.6), (8.8, 21.2, 2.6), "plate", dict(x=-30, origin=[8, 18.6, 2.6]))
    # panache rouge qui retombe dans le dos
    pan = [(3.6, 2.4, 10, -90), (3.6, 2.2, -20, -90), (3.6, 2.0, -45, -90), (3.2, 1.6, -70, -90)]
    chain(m, (8, 19.0, 13.0), pan, ["cloth"] * 4, side_mirror=False)
    # cornes de taureau : sortent sur les côtés puis montent et avancent
    corne = [(3.2, 2.4, 6, 0), (3.0, 2.1, 30, 12), (2.8, 1.8, 58, 24), (2.4, 1.4, 82, 34)]
    chain(m, (1.2, 11.2, 7.6), corne, ["plate", "plate", "trim", "trim"])
    m.add((5.9, 10.2, 0.0), (10.1, 14.0, 0.9), "plate")
    m.add((7.0, 11.1, -0.5), (9.0, 13.1, 0.3), "glow", dict(z=45, origin=[8, 12.1, -0.1]))
    if extra: extra(m)
    return m.build(HEAD_DISPLAY)

# ------------------------------------------------------------------ épées (modèle vertical, poignée en bas)
def sword_display(scale, grip_y):
    s = scale
    ty = (8 - grip_y) * s
    return {"thirdperson_righthand": {"rotation": [0, -90, 10], "translation": [0, round(ty, 2), 1], "scale": [s, s, s]},
            "thirdperson_lefthand": {"rotation": [0, 90, -10], "translation": [0, round(ty, 2), 1], "scale": [s, s, s]},
            "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, round(ty * 0.9, 2), 1.13], "scale": [s * 0.95] * 3},
            "firstperson_lefthand": {"rotation": [0, 90, -25], "translation": [1.13, round(ty * 0.9, 2), 1.13], "scale": [s * 0.95] * 3},
            "gui": {"rotation": [0, 0, -45], "translation": [-0.5, -0.5, 0], "scale": [0.46, 0.46, 0.46]},
            "ground": {"translation": [0, 2, 0], "scale": [0.4, 0.4, 0.4]},
            "fixed": {"rotation": [0, 0, -45], "scale": [0.6, 0.6, 0.6]}}

def tip(m, cx, y, w, z0, z1, mat="blade"):
    s = w / math.sqrt(2)
    m.add((cx - s / 2, y - s / 2, z0), (cx + s / 2, y + s / 2, z1), mat, dict(z=45, origin=[cx, y, (z0 + z1) / 2]))

def epee_0():
    m = Model("epee_0", OUTIL[0])
    m.add((7.0, -5.6, 7.0), (9.0, -3.6, 9.0), "plate", name="pommeau")
    m.add((7.4, -3.6, 7.4), (8.6, 2.0, 8.6), "grip", name="poignee")
    m.add((3.6, 2.0, 7.15), (12.4, 3.1, 8.85), "plate", name="garde")
    m.add((6.9, 1.6, 6.9), (9.1, 3.5, 9.1), "plate")
    m.add((6.5, 3.1, 7.5), (9.5, 24.5, 8.5), "blade", name="lame")
    tip(m, 8, 24.5, 3.0, 7.5, 8.5)
    return m.build(sword_display(0.7, 0.0))

def epee_5(name="epee_5", P=None, extra=None):
    m = Model(name, P or OUTIL[5])
    m.add((6.9, -6.4, 6.9), (9.1, -4.2, 9.1), "gem", dict(y=45, origin=[8, -5.3, 8]), name="pommeau")
    m.add((7.2, -4.4, 7.2), (8.8, -3.6, 8.8), "trim")
    m.add((7.3, -3.6, 7.3), (8.7, 2.0, 8.7), "grip", name="poignee")
    m.add((6.3, 1.8, 6.6), (9.7, 4.4, 9.4), "trim", name="garde")
    mirror(m, (2.6, 2.6, 7.2), (6.4, 3.8, 8.8), "trim", dict(z=-24, origin=[6.4, 3.2, 8]))
    mirror(m, (1.9, 3.6, 7.35), (3.3, 5.0, 8.65), "gem", dict(z=45, origin=[2.6, 4.3, 8]))
    m.add((7.2, 2.5, 6.25), (8.8, 4.1, 6.65), "glow")
    m.add((7.2, 2.5, 9.35), (8.8, 4.1, 9.75), "glow")
    m.add((5.9, 4.4, 7.4), (10.1, 19.6, 8.6), "blade", name="lame")
    m.add((7.6, 5.0, 7.1), (8.4, 19.0, 8.9), "edge")
    m.add((5.9, 19.6, 7.4), (9.4, 23.0, 8.6), "blade")
    tip(m, 7.65, 23.0, 3.5, 7.4, 8.6)
    mirror(m, (5.0, 4.2, 7.55), (5.9, 7.4, 8.45), "gem", dict(z=18, origin=[5.9, 4.4, 8]))
    if extra: extra(m)
    return m.build(sword_display(0.7, 0.0))

def epee_9(name="epee_9", P=None, extra=None):
    m = Model(name, P or OUTIL[9])
    m.add((6.8, -7.0, 6.8), (9.2, -4.6, 9.2), "glow", dict(y=45, x=35, origin=[8, -5.8, 8]), name="pommeau")
    m.add((7.1, -4.9, 7.1), (8.9, -4.1, 8.9), "trim")
    m.add((7.3, -4.1, 7.3), (8.7, 1.8, 8.7), "grip", name="poignee")
    m.add((5.8, 1.6, 6.6), (10.2, 4.4, 9.4), "trim", name="garde")
    m.add((7.2, 2.2, 6.2), (8.8, 3.8, 6.6), "glow")
    m.add((7.2, 2.2, 9.4), (8.8, 3.8, 9.8), "glow")
    # garde en ailes : trois segments par côté, de plus en plus relevés
    mirror(m, (2.8, 2.4, 7.3), (6.0, 3.6, 8.7), "trim", dict(z=-14, origin=[6.0, 3.0, 8]))
    mirror(m, (0.9, 3.0, 7.4), (3.4, 4.0, 8.6), "plate", dict(z=-34, origin=[3.4, 3.5, 8]))
    mirror(m, (-0.2, 4.4, 7.5), (1.6, 5.2, 8.5), "plate", dict(z=-58, origin=[1.6, 4.8, 8]))
    mirror(m, (-0.5, 5.4, 7.6), (0.7, 6.6, 8.4), "glow", dict(z=45, origin=[0.1, 6.0, 8]))
    # lame basse
    m.add((6.1, 4.4, 7.4), (9.9, 14.6, 8.6), "runeblade", name="lame_basse")
    m.add((6.1, 14.6, 7.4), (9.9, 15.4, 8.6), "trim")
    # noyau et anneau d'énergie
    m.add((7.0, 15.9, 7.0), (9.0, 17.9, 9.0), "glow", dict(x=45, y=45, origin=[8, 16.9, 8]), name="noyau")
    n, Rr = 10, 3.4
    for k in range(n):
        th = 2 * math.pi * k / n
        cx, cz = 8 + Rr * math.cos(th), 8 + Rr * math.sin(th)
        L = 2 * Rr * math.tan(math.pi / n) + 0.1
        m.add((cx - L / 2, 16.65, cz - 0.25), (cx + L / 2, 17.15, cz + 0.25), "glow", dict(y=-(math.degrees(th) + 90), origin=[cx, 16.9, cz]))
    # lame haute, détachée
    m.add((6.1, 18.4, 7.4), (9.9, 19.2, 8.6), "trim")
    m.add((6.1, 19.2, 7.4), (9.9, 27.6, 8.6), "runeblade", name="lame_haute")
    tip(m, 8, 27.6, 3.8, 7.4, 8.6)
    mirror(m, (5.3, 19.6, 7.6), (6.1, 23.0, 8.4), "edge")
    if extra: extra(m)
    return m.build(sword_display(0.7, 0.0))

# ------------------------------------------------------------------ export
def save(model, atlas, glow, S, name):
    base = os.path.join(OUT, "pack", "assets", "metiers")
    os.makedirs(f"{base}/models/item/proto", exist_ok=True)
    os.makedirs(f"{base}/textures/item/proto", exist_ok=True)
    os.makedirs(f"{base}/items", exist_ok=True)
    json.dump(model, open(f"{base}/models/item/proto/{name}.json", "w"), indent=1)
    Image.fromarray(atlas, "RGBA").save(f"{base}/textures/item/proto/{name}.png")
    if glow is not None:
        frames = []
        for f in range(NF):
            k = 0.72 + 0.28 * (0.5 + 0.5 * math.cos(2 * math.pi * f / NF))
            g = glow.astype(float); g[..., :3] *= k
            frames.append(np.clip(g, 0, 255).astype(np.uint8))
        Image.fromarray(np.concatenate(frames, 0), "RGBA").save(f"{base}/textures/item/proto/{name}_glow.png")
        json.dump({"animation": {"frametime": 2, "interpolate": True}}, open(f"{base}/textures/item/proto/{name}_glow.png.mcmeta", "w"))
    json.dump({"model": {"type": "minecraft:model", "model": f"metiers:item/proto/{name}"}},
              open(f"{base}/items/proto_{name}.json", "w"), indent=1)
    print(name, "elements", len(model["elements"]), "atlas", S)

if __name__ == "__main__":
  for fn in (heaume_3, heaume_5, epee_0, epee_5, epee_9):
    mdl, at, gl, S = fn()
    save(mdl, at, gl, S, fn.__name__)

  json.dump({"pack": {"description": "Métiers : prototypes refonte (test)", "min_format": 69, "max_format": 999}},
          open(os.path.join(OUT, "pack", "pack.mcmeta"), "w"), indent=1)

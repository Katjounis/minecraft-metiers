"""Heaumes 3D (modèles d'item à éléments) pour les 5 paliers + tuiles de texture + aperçu isométrique."""
import os, sys, json, math
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from armorgen2 import T, hx

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/heaume"
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- tuiles 16x16
def tile_metal(P):
    m = [hx(c) for c in P["metal"]]
    a = np.zeros((16, 16, 4))
    for y in range(16):
        for x in range(16):
            band = (y // 4)
            c = m[3] if band % 2 == 0 else m[2]
            if y % 4 == 0: c = m[4]
            if y % 4 == 3: c = m[1]
            if x == 0: c = m[4]
            if x == 15: c = m[1]
            if (x * 7 + y * 5) % 17 == 0: c = c * 0.85 + m[0] * 0.15
            a[y, x, :3] = c; a[y, x, 3] = 255
    for (x, y) in ((3, 2), (12, 2), (3, 10), (12, 10)):
        a[y, x, :3] = m[5]; a[y + 1, x, :3] = m[1]
    return a

def tile_trim(P):
    t = [hx(c) for c in P["trim"]]
    a = np.zeros((16, 16, 4))
    for y in range(16):
        for x in range(16):
            c = t[2]
            if (x + y) % 4 == 0: c = t[3]
            if (x - y) % 6 == 0: c = t[1]
            if x in (0, 15) or y in (0, 15): c = t[1] if (x == 15 or y == 15) else t[3]
            a[y, x, :3] = c; a[y, x, 3] = 255
    return a

def tile_face(P):
    a = tile_metal(P)
    dark = hx("#07070c")
    for x in range(2, 14):
        a[6, x, :3] = dark; a[7, x, :3] = dark
    for y in range(7, 13):
        a[y, 7, :3] = dark; a[y, 8, :3] = dark
    eye = hx(P["glow"]) if P["glow"] else hx(P["gem"][2])
    for x in (4, 5, 10, 11):
        a[6, x, :3] = eye; a[7, x, :3] = eye * 0.7 + dark * 0.3
    for y in range(13, 16):
        for x in range(16):
            if (x + y) % 3 == 0:
                a[y, x, :3] = dark * 0.5 + a[y, x, :3] * 0.5
    return a

def tile_gem(P):
    g = [hx(c) for c in P["gem"]]
    a = np.zeros((16, 16, 4))
    for y in range(16):
        for x in range(16):
            d = abs(x - 7.5) + abs(y - 7.5)
            c = g[0] if d > 7 else (g[1] if d > 3 else g[2])
            if x < 6 and y < 6 and d < 6: c = g[3]
            a[y, x, :3] = c; a[y, x, 3] = 255
    return a

def tile_horn(P):
    m = [hx(c) for c in (P["cloth"] if P.get("sun") else P["metal"])]
    tr = [hx(c) for c in P["trim"]]
    a = np.zeros((16, 16, 4))
    for y in range(16):
        for x in range(16):
            c = m[min(len(m) - 1, 1 + (15 - y) * (len(m) - 2) // 15)]
            if y % 5 == 0: c = tr[2]
            a[y, x, :3] = c; a[y, x, 3] = 255
    return a

def tile_glow(P):
    g = hx(P["glow"] or P["gem"][2]); w = hx("#ffffff")
    a = np.zeros((16, 16, 4))
    for y in range(16):
        for x in range(16):
            k = 1 - min(1, (abs(x - 7.5) + abs(y - 7.5)) / 12)
            a[y, x, :3] = g * (1 - k * 0.6) + w * k * 0.6; a[y, x, 3] = 255
    return a

def tile_feather(P):
    w = [hx(c) for c in ("#c9c2b0", "#ece6d8", "#ffffff")] if P.get("sun") else [hx(c) for c in P["metal"][2:5]]
    tr = hx(P["trim"][2])
    a = np.zeros((16, 16, 4))
    for y in range(16):
        for x in range(16):
            c = w[(x + y // 3) % 3]
            if x % 4 == 0: c = c * 0.8
            if y == 0: c = tr
            a[y, x, :3] = c; a[y, x, 3] = 255
    return a

TILES = {"metal": tile_metal, "trim": tile_trim, "face": tile_face, "gem": tile_gem,
         "horn": tile_horn, "glow": tile_glow, "feather": tile_feather}

# ---------------------------------------------------------------- géométrie (unités de modèle, tête ~ 1.6 à 14.4)
def el(frm, to, tex, faces=None, rot=None):
    fs = faces or ["north", "south", "east", "west", "up", "down"]
    e = {"from": [round(v, 2) for v in frm], "to": [round(v, 2) for v in to],
         "faces": {f: {"texture": f"#{tex if not isinstance(tex, dict) else tex.get(f, tex['*'])}", "uv": [0, 0, 16, 16]} for f in fs}}
    if rot:
        e["rotation"] = rot
    return e

def mirror(e):
    f, t = e["from"], e["to"]
    m = json.loads(json.dumps(e))
    m["from"] = [round(16 - t[0], 2), f[1], f[2]]; m["to"] = [round(16 - f[0], 2), t[1], t[2]]
    fc = m["faces"]
    if "east" in fc or "west" in fc:
        fc["east"], fc["west"] = e["faces"].get("west"), e["faces"].get("east")
        m["faces"] = {k: v for k, v in fc.items() if v}
    if "rotation" in m:
        r = m["rotation"]; r["origin"] = [round(16 - r["origin"][0], 2), r["origin"][1], r["origin"][2]]
        if r["axis"] in ("y", "z"): r["angle"] = -r["angle"]
    return m

def heaume(tier):
    E = []
    shell = {"north": "face", "*": "metal"}
    E.append(el([1.2, 1.0, 1.2], [14.8, 15.0, 14.8], shell))
    E.append(el([0.9, 9.6, 0.9], [15.1, 11.2, 15.1], "trim"))                 # bandeau
    E.append(el([7.1, 3.0, 0.5], [8.9, 11.2, 1.2], "trim"))                   # nasal
    E.append(el([6.6, 9.4, 0.3], [9.4, 12.2, 0.9], "gem"))                    # gemme frontale
    E.append(el([1.2, 1.0, 0.7], [5.6, 6.6, 1.2], "metal"))                   # joues
    E.append(el([10.4, 1.0, 0.7], [14.8, 6.6, 1.2], "metal"))
    E.append(el([0.8, 0.2, 14.8], [15.2, 3.6, 16.0], "metal"))                # couvre-nuque
    E.append(el([7.0, 15.0, 1.5], [9.0, 18.0, 15.0], "trim"))                 # crête
    if tier == 1:
        E.append(el([7.3, 17.0, 6.0], [8.7, 19.5, 14.5], "horn"))
    if tier >= 2:  # plumet
        E.append(el([7.2, 17.5, 4.0], [8.8, 21.0, 12.0], "feather"))
        E.append(el([7.2, 15.0, 12.0], [8.8, 20.0, 17.0], "feather", rot={"angle": -22.5, "axis": "x", "origin": [8, 16, 12]}))
    if tier == 2 or tier == 3:  # petites ailes latérales
        w = [el([-1.6, 9.0, 6.0], [1.2, 13.5, 11.0], "feather", rot={"angle": 22.5, "axis": "z", "origin": [1.2, 11, 8]}),
             el([-3.6, 11.5, 7.0], [-0.5, 16.0, 10.5], "feather", rot={"angle": 22.5, "axis": "z", "origin": [1.2, 11, 8]})]
        for e in w:
            E += [e, mirror(e)]
    if tier == 3:  # couronne
        for x in (2.0, 5.0, 8.0 - 0.75, 10.0, 13.0):
            E.append(el([x, 15.0, 0.6], [x + 1.5, 17.5 + (1.0 if abs(x - 7.25) < 1 else 0), 1.6], "trim"))
        E.append(el([1.0, 14.6, 0.6], [15.0, 15.6, 1.6], "trim"))
    if tier == 4:  # grandes cornes
        segs = [([-1.2, 10.5, 6.5], [1.2, 13.5, 9.5], 0), ([-3.8, 11.5, 6.8], [-0.8, 14.5, 9.2], 22.5),
                ([-5.2, 14.0, 7.0], [-2.6, 17.5, 9.0], 45), ([-5.6, 17.0, 7.3], [-3.6, 21.5, 8.7], 22.5)]
        for i, (f, t, a) in enumerate(segs):
            e = el(f, t, "glow" if i == 3 else "horn", rot={"angle": 0 if a == 0 else (22.5 if a else 0), "axis": "z", "origin": [f[0], f[1], 8]} if a else None)
            E += [e, mirror(e)]
    if tier == 5:  # grandes ailes d'ange + auréole
        feathers = [([-1.5, 9.0, 7.5], [1.2, 15.0, 13.5], 22.5), ([-4.5, 11.0, 8.0], [-1.0, 18.0, 14.0], 22.5),
                    ([-7.0, 13.0, 8.5], [-3.5, 21.0, 14.5], 22.5), ([-8.5, 17.0, 9.0], [-5.5, 24.0, 15.0], 22.5)]
        for f, t, a in feathers:
            e = el(f, t, "feather", rot={"angle": a, "axis": "z", "origin": [1.2, 12, 8]})
            E += [e, mirror(e)]
        for (f, t) in (([4.0, 22.0, 4.0], [12.0, 22.8, 5.0]), ([4.0, 22.0, 11.0], [12.0, 22.8, 12.0]),
                       ([4.0, 22.0, 5.0], [5.0, 22.8, 11.0]), ([11.0, 22.0, 5.0], [12.0, 22.8, 11.0])):
            E.append(el(f, t, "glow"))
    for e in E:
        r = e.get("rotation")
        if r and r["angle"] not in (-45, -22.5, 0, 22.5, 45):
            r["angle"] = 22.5
    return E

def model(tier):
    return {"textures": {**{k: f"metiers:item/heaume/{k}_{tier}" for k in TILES}, "particle": f"metiers:item/heaume/metal_{tier}"},
            "elements": heaume(tier),
            "display": {"head": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]},
                        "gui": {"rotation": [25, 210, 0], "translation": [0, -2, 0], "scale": [0.48, 0.48, 0.48]},
                        "ground": {"translation": [0, 2, 0], "scale": [0.3, 0.3, 0.3]},
                        "fixed": {"scale": [0.5, 0.5, 0.5]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.3, 0.3, 0.3]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.3, 0.3, 0.3]}}}

# ---------------------------------------------------------------- aperçu isométrique (rendu simple par faces)
def render(tier, size=360):
    P = T[tier]
    tex = {k: f(P) for k, f in TILES.items()}
    img = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    yaw, pitch = math.radians(-32), math.radians(24)
    sc = size * 2 / 40
    def proj(p):
        x, y, z = p[0] - 8, p[1] - 10, p[2] - 8
        xr = x * math.cos(yaw) - z * math.sin(yaw)
        zr = x * math.sin(yaw) + z * math.cos(yaw)
        up = y * math.cos(pitch) + zr * math.sin(pitch)
        depth = zr * math.cos(pitch) - y * math.sin(pitch)
        return (size + xr * sc, size * 1.1 - up * sc), depth
    def rot(p, r):
        if not r: return p
        o = r["origin"]; a = math.radians(r["angle"]); x, y, z = p[0] - o[0], p[1] - o[1], p[2] - o[2]
        if r["axis"] == "z": x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        if r["axis"] == "x": y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
        if r["axis"] == "y": x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
        return (x + o[0], y + o[1], z + o[2])
    quads = []
    N = 8
    for e in heaume(tier):
        f, t = e["from"], e["to"]
        faces = {
            "north": lambda u, v: (f[0] + (t[0] - f[0]) * u, t[1] - (t[1] - f[1]) * v, f[2]),
            "west": lambda u, v: (f[0], t[1] - (t[1] - f[1]) * v, t[2] - (t[2] - f[2]) * u),
            "east": lambda u, v: (t[0], t[1] - (t[1] - f[1]) * v, f[2] + (t[2] - f[2]) * u),
            "up": lambda u, v: (f[0] + (t[0] - f[0]) * u, t[1], t[2] - (t[2] - f[2]) * v),
            "south": lambda u, v: (t[0] - (t[0] - f[0]) * u, t[1] - (t[1] - f[1]) * v, t[2]),
        }
        shade = {"north": 1.0, "up": 1.18, "west": 0.78, "east": 0.78, "south": 0.62}
        for face, fn in faces.items():
            if face not in e["faces"]: continue
            key = e["faces"][face]["texture"][1:]
            tx = tex[key]
            for i in range(N):
                for j in range(N):
                    pts = [fn(i / N, j / N), fn((i + 1) / N, j / N), fn((i + 1) / N, (j + 1) / N), fn(i / N, (j + 1) / N)]
                    pp = [proj(rot(q, e.get("rotation"))) for q in pts]
                    depth = sum(q[1] for q in pp) / 4
                    col = tx[int((j + 0.5) * 16 / N), int((i + 0.5) * 16 / N), :3] * shade[face]
                    quads.append((depth, [q[0] for q in pp], tuple(int(min(255, max(0, v))) for v in col) + (255,)))
    quads.sort(key=lambda q: -q[0])
    for depth, pts, col in quads:
        d.polygon(pts, fill=col)
    return img.resize((size, size), Image.LANCZOS)

if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "tex"), exist_ok=True)
    sheet = Image.new("RGBA", (5 * 300, 330), (34, 36, 44, 255))
    for tier in range(1, 6):
        P = T[tier]
        for k, f in TILES.items():
            Image.fromarray(np.clip(f(P), 0, 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, "tex", f"{k}_{tier}.png"))
        json.dump(model(tier), open(os.path.join(OUT, f"heaume_{tier}.json"), "w"), indent=1)
        sheet.alpha_composite(render(tier, 300), ((tier - 1) * 300, 15))
    sheet.save(os.path.join(OUT, "_apercu.png"))
    print("ok")

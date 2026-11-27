"""Petit moteur de rendu des modèles d'objet (éléments texturés, peintre) : aperçus des skins pour les menus (gen6.py)."""
import json, math, zipfile, io, sys
import numpy as np
from PIL import Image, ImageDraw

class Source:
    def __init__(self, zpath=None, files=None):
        self.z = zipfile.ZipFile(zpath) if zpath else None
        self.files = files or {}
    def json(self, rid):
        ns, p = rid.split(":") if ":" in rid else ("minecraft", rid)
        path = f"assets/{ns}/models/{p}.json"
        if path in self.files: return self.files[path]
        return json.loads(self.z.read(path))
    def png(self, rid):
        ns, p = rid.split(":") if ":" in rid else ("minecraft", rid)
        path = f"assets/{ns}/textures/{p}.png"
        if path in self.files: return self.files[path]
        im = Image.open(io.BytesIO(self.z.read(path))).convert("RGBA")
        if im.height > im.width: im = im.crop((0, 0, im.width, im.width))
        return im

TS = [16, 16]
def resolve(src, rid):
    global TS
    m = src.json(rid)
    TS = m.get("texture_size", [16, 16])
    tex, els = {}, None
    chain = [m]
    while "parent" in chain[-1] and not chain[-1]["parent"].startswith("builtin") and "elements" not in chain[-1]:
        try: chain.append(src.json(chain[-1]["parent"]))
        except KeyError: break
    for c in reversed(chain):
        tex.update(c.get("textures", {}))
        if "elements" in c: els = c["elements"]
    for k in list(tex):
        v = tex[k]
        for _ in range(5):
            if isinstance(v, str) and v.startswith("#"): v = tex.get(v[1:], v)
        tex[k] = v
    return els or [], tex

def rot(p, axis, ang, o):
    a = math.radians(ang); x, y, z = p[0] - o[0], p[1] - o[1], p[2] - o[2]
    c, s = math.cos(a), math.sin(a)
    if axis == "x": y, z = y * c - z * s, y * s + z * c
    elif axis == "y": x, z = x * c + z * s, -x * s + z * c
    else: x, y = x * c - y * s, x * s + y * c
    return (x + o[0], y + o[1], z + o[2])

FACES = {"north": [(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0)], "south": [(0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)],
         "west": [(0, 1, 0), (0, 1, 1), (0, 0, 1), (0, 0, 0)], "east": [(1, 1, 1), (1, 1, 0), (1, 0, 0), (1, 0, 1)],
         "up": [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)], "down": [(0, 0, 1), (1, 0, 1), (1, 0, 0), (0, 0, 0)]}
LUM = {"up": 1.0, "south": 0.9, "north": 0.75, "east": 0.8, "west": 0.7, "down": 0.55}

def _coeffs(dst, srcp):
    A = []; B = []
    for (x, y), (u, v) in zip(dst, srcp):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    try: return np.linalg.solve(np.array(A, float), np.array(B, float))
    except np.linalg.LinAlgError: return None

def render(src, rid, size=420, yaw=-30, pitch=20, roll=-45, bg=(36, 40, 48, 255), ss=2):
    els, tex = resolve(src, rid)
    imgs = {}
    polys = []
    for e in els:
        f, t = e["from"], e["to"]
        r = e.get("rotation")
        for fn, corners in FACES.items():
            fd = e.get("faces", {}).get(fn)
            if not fd: continue
            pts = [(f[0] + (t[0] - f[0]) * a, f[1] + (t[1] - f[1]) * b, f[2] + (t[2] - f[2]) * c) for a, b, c in corners]
            if r and "axis" in r: pts = [rot(p, r["axis"], r["angle"], r["origin"]) for p in pts]
            elif r:
                for ax in ("x", "y", "z"):
                    if r.get(ax): pts = [rot(p, ax, r[ax], r["origin"]) for p in pts]
            key = fd["texture"][1:]
            tid = tex.get(key)
            if not tid or tid.startswith("#"): continue
            if tid not in imgs:
                try: imgs[tid] = src.png(tid)
                except Exception: imgs[tid] = None
            im = imgs[tid]
            if im is None: continue
            W = im.width / 16
            u = fd.get("uv", [0, 0, 16, 16])
            tc = [(u[0] * W, u[1] * W), (u[2] * W, u[1] * W), (u[2] * W, u[3] * W), (u[0] * W, u[3] * W)]
            k = (fd.get("rotation", 0) // 90) % 4
            tc = tc[k:] + tc[:k]
            polys.append((pts, im, tc, 1.0 if "glow" in tid or key == "glow" else LUM[fn]))
    def view(p):
        p = rot(p, "z", roll, (8, 8, 8)); p = rot(p, "y", yaw, (8, 8, 8)); p = rot(p, "x", pitch, (8, 8, 8))
        return p
    V = [([view(p) for p in pts], im, tc, l) for pts, im, tc, l in polys]
    allp = [p for v in V for p in v[0]]
    xs = [p[0] for p in allp]; ys = [p[1] for p in allp]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    S = size * ss
    sc = S * 0.88 / max(max(xs) - min(xs), max(ys) - min(ys), 1)
    img = Image.new("RGBA", (S, S), bg)
    V.sort(key=lambda v: sum(p[2] for p in v[0]) / 4)
    for pts, im, tc, l in V:
        q = [(S / 2 + (p[0] - cx) * sc, S / 2 - (p[1] - cy) * sc) for p in pts]
        x0, y0 = max(0, int(min(p[0] for p in q)) - 1), max(0, int(min(p[1] for p in q)) - 1)
        x1, y1 = min(S, int(max(p[0] for p in q)) + 2), min(S, int(max(p[1] for p in q)) + 2)
        if x1 <= x0 or y1 <= y0: continue
        c = _coeffs([(px - x0, py - y0) for px, py in q], tc)
        if c is None: continue
        patch = im.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, tuple(c), Image.NEAREST)
        mask = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(mask).polygon([(px - x0, py - y0) for px, py in q], fill=255)
        a = np.array(patch).astype(float)
        a[..., :3] *= l
        a[..., 3] = np.minimum(a[..., 3], np.array(mask))
        a[..., 3] = np.where(a[..., 3] > 40, 255, 0)
        img.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), (x0, y0))
    return img.resize((size, size), Image.LANCZOS)

def planche(images, titres, path, cols=6, size=300):
    from PIL import ImageFont
    rows = (len(images) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * size, rows * (size + 28)), (28, 31, 38, 255)); d = ImageDraw.Draw(sheet)
    try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except Exception: font = None
    for i, (im, t) in enumerate(zip(images, titres)):
        x, y = (i % cols) * size, (i // cols) * (size + 28)
        sheet.alpha_composite(im.resize((size, size)), (x, y + 28))
        d.text((x + 10, y + 5), t, fill=(230, 230, 230), font=font)
    sheet.save(path)

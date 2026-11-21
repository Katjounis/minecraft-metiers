# Correctifs du resource pack (à lancer sur metiers_resourcepack.zip, réécrit sur place) :
#  1. rotations d'éléments vides ({origin} seul) : refusées par le jeu, le modèle passe en texture manquante ;
#  2. éléments hors de la zone -16..32 : idem, le modèle est rétréci et l'affichage agrandi d'autant ;
#  3. outils plus gros dans l'inventaire : l'échelle « gui » remplit la case ;
#  4. heaumes 3D grossis sur la tête (1,18) pour passer au-dessus de la couche externe du skin.
# Usage : python3 correctifs_rp.py metiers_resourcepack.zip
import io, json, math, re, sys, zipfile
from PIL import Image

src = sys.argv[1]
zin = zipfile.ZipFile(src)
files = {n: zin.read(n) for n in zin.namelist()}
zin.close()

def rot_pts(pts, ang_z):
    a = math.radians(ang_z); c, s = math.cos(a), math.sin(a)
    return [(x * c - y * s, x * s + y * c) for x, y in pts]

def corners(e):
    (x0, y0, z0), (x1, y1, z1) = e["from"], e["to"]
    P = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    r = e.get("rotation")
    if r and any(k in r for k in ("x", "y", "z", "angle")):
        ox, oy, oz = r.get("origin", [8, 8, 8])
        ang = {"x": r.get("x", 0), "y": r.get("y", 0), "z": r.get("z", 0)}
        if "angle" in r: ang = {"x": 0, "y": 0, "z": 0}; ang[r["axis"]] = r["angle"]
        out = []
        for x, y, z in P:
            x, y, z = x - ox, y - oy, z - oz
            for ax in ("x", "y", "z"):
                a = math.radians(ang[ax]); c, s = math.cos(a), math.sin(a)
                if ax == "x": y, z = y * c - z * s, y * s + z * c
                elif ax == "y": x, z = x * c + z * s, -x * s + z * c
                else: x, y = x * c - y * s, x * s + y * c
            out.append((x + ox, y + oy, z + oz))
        P = out
    return P

stats = {"rot": 0, "bornes": 0, "gui": 0, "heaumes": 0}
OUTIL = re.compile(r"assets/metiers/models/item/v2/([a-z]_\d+|arc_\d+|forge_[a-z0-9_]+)(_[a-z_]+)?\.json$")
HEAUME = re.compile(r"assets/metiers/models/item/v2/heaume_\d+(_[a-z_]+)?\.json$")
files.pop("assets/metiers/textures/item/v2/doublure.png", None)

for n in list(files):
    if not (n.startswith("assets/metiers/models/") and n.endswith(".json")): continue
    d = json.loads(files[n]); changed = False
    els = d.get("elements", [])
    # 1. rotations vides
    for e in els:
        r = e.get("rotation")
        if r is not None and not ({"angle", "x", "y", "z"} & set(r)):
            del e["rotation"]; stats["rot"] += 1; changed = True
    # 2. hors bornes
    if els:
        lo = min(min(e["from"] + e["to"]) for e in els); hi = max(max(e["from"] + e["to"]) for e in els)
        if lo < -16 or hi > 32:
            f = min(24 / (8 - lo) if lo < -16 else 1, 24 / (hi - 8) if hi > 32 else 1) * 0.98
            S = lambda v: [8 + (c - 8) * f for c in v]
            for e in els:
                e["from"], e["to"] = S(e["from"]), S(e["to"])
                if "rotation" in e and "origin" in e["rotation"]: e["rotation"]["origin"] = S(e["rotation"]["origin"])
            for ctx, t in d.get("display", {}).items():
                if "scale" in t: t["scale"] = [round(s / f, 4) for s in t["scale"]]
            stats["bornes"] += 1; changed = True
    # 3. gui : remplir la case
    if OUTIL.search(n) and els and "gui" in d.get("display", {}):
        g = d["display"]["gui"]; rz = g.get("rotation", [0, 0, 0])[2]
        pts = [p for e in els for p in corners(e)]
        xy = rot_pts([(x - 8, y - 8) for x, y, z in pts], rz)
        xs = [p[0] for p in xy]; ys = [p[1] for p in xy]
        ext = max(max(xs) - min(xs), max(ys) - min(ys))
        sc = round(min(17.0 / ext, 1.6), 3) if ext > 0 else 0
        if sc > g.get("scale", [1])[0] * 1.05:
            cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
            g["scale"] = [sc, sc, sc]
            g["translation"] = [round(-cx * sc, 2), round(-cy * sc, 2), 0]
            stats["gui"] += 1; changed = True
    # 4. heaumes : plus de doublure, le heaume est grossi sur la tête pour passer au-dessus de la couche externe du skin
    if HEAUME.search(n) and els:
        n0 = len(els); els[:] = [e for e in els if e.get("name") != "doublure"]
        if len(els) != n0: d.get("textures", {}).pop("doublure", None); changed = True
        h = d.setdefault("display", {}).setdefault("head", {})
        if h.get("scale", [1])[0] < 1.18:
            h["scale"] = [1.18, 1.18, 1.18]; stats["heaumes"] += 1; changed = True
    if changed:
        files[n] = json.dumps(d, separators=(",", ":")).encode()

out = io.BytesIO()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for n in sorted(files):
        zi = zipfile.ZipInfo(n, date_time=(2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, files[n])
open(src, "wb").write(out.getvalue())
print(stats)

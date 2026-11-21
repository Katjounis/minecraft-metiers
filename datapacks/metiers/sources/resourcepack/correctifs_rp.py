# Correctifs du resource pack (à lancer sur metiers_resourcepack.zip, réécrit sur place) :
#  1. rotations d'éléments vides ({origin} seul) : refusées par le jeu, le modèle passe en texture manquante ;
#  2. éléments hors de la zone -16..32 : idem, le modèle est rétréci et l'affichage agrandi d'autant ;
#  3. outils plus gros dans l'inventaire : l'échelle « gui » remplit la case ;
#  4. heaumes 3D grossis sur la tête (1,10) pour passer au-dessus de la couche externe du skin.
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

stats = {"rot": 0, "bornes": 0, "gui": 0, "heaumes": 0, "arcs": 0, "zfight": 0}
MARQ = "assets/metiers/correctifs.json"
FAIT = set(json.loads(files[MARQ])) if MARQ in files else set()
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
        if h.get("scale", [1])[0] != 1.10:
            h["scale"] = [1.10, 1.10, 1.10]; stats["heaumes"] += 1; changed = True
    # 5. arcs : la corde partait vers la poignée en bandant (animation à l'envers) et la flèche pointait vers l'archer.
    #    On renvoie la corde et la flèche de l'autre côté des pointes des branches.
    if "arc5" not in FAIT and re.search(r"/arc_\d+(_[a-z_]+)?_pulling_\d\.json$", n):
        noms = [e.get("name") for e in els]
        if "fleche" in noms:
            i = noms.index("fleche"); part = els[i - 2:i + 3]
            e0 = els[i - 2]; r = e0["rotation"]; o = r["origin"]; a = math.radians(r.get("z", r.get("angle", 0)))
            ends = []
            for x in (e0["from"][0], e0["to"][0]):
                y = (e0["from"][1] + e0["to"][1]) / 2; dx, dy = x - o[0], y - o[1]
                ends.append((o[0] + dx * math.cos(a) - dy * math.sin(a), o[1] + dx * math.sin(a) + dy * math.cos(a)))
            t = min(ends, key=lambda q: abs(q[1] - 8) * -1)[0]   # extrémité loin de y=8 : la pointe
            for e in part:
                fx, tx = e["from"][0], e["to"][0]
                e["from"][0], e["to"][0] = 2 * t - tx, 2 * t - fx
                rr = e.get("rotation")
                if rr:
                    if "origin" in rr: rr["origin"][0] = 2 * t - rr["origin"][0]
                    for k in ("z", "y"):
                        if k in rr: rr[k] = -rr[k]
                    if "angle" in rr and rr.get("axis") in ("z", "y"): rr["angle"] = -rr["angle"]
                fc = e.get("faces", {})
                if "east" in fc or "west" in fc:
                    fc["east"], fc["west"] = fc.get("west"), fc.get("east")
                    for k in ("east", "west"):
                        if fc[k] is None: del fc[k]
            stats["arcs"] += 1; changed = True
    # 6. faces qui se chevauchent (scintillement) : chaque élément est très légèrement grossi, un peu plus que le précédent
    if "zfight" not in FAIT and n.startswith("assets/metiers/models/item/v2/") and els:
        for k, e in enumerate(els):
            ep = min(0.006 * (k + 1), 0.18)
            e["from"] = [c - ep for c in e["from"]]; e["to"] = [c + ep for c in e["to"]]
        stats["zfight"] += 1; changed = True
    if changed:
        files[n] = json.dumps(d, separators=(",", ":")).encode()

# 7. armure palier 4 (netherite d'améthyste) : plus de traits violets en diagonale,
#    remplacés par quelques gemmes d'améthyste serties au centre de chaque plaque.
EQ4 = re.compile(r"assets/metiers/textures/entity/equipment/(humanoid|humanoid_leggings)/guilde_4(_[a-z_]+)?\.png$")
if "ame4" not in FAIT:
    for n in list(files):
        m = EQ4.search(n)
        if not m: continue
        legs = m.group(1) == "humanoid_leggings"
        im = Image.open(io.BytesIO(files[n])).convert("RGBA"); px = im.load()
        rects = [(4, 20, 4, 12), (12, 20, 4, 12), (20, 20, 8, 12), (32, 20, 8, 12)] + ([] if legs else [(44, 20, 4, 12), (52, 20, 4, 12)])
        for (x0, y0, w, h) in rects:
            X0, Y0, W, H = x0 * 2, y0 * 2, w * 2, h * 2
            pts = set()
            for dd in range(-H, W, 7):
                for i in range(H):
                    if 0 <= dd + i < W and px[X0 + dd + i, Y0 + i][3] > 0: pts.add((X0 + dd + i, Y0 + i))
            cols = {}
            for q in pts: cols[px[q][:3]] = cols.get(px[q][:3], 0) + 1
            if not cols: continue
            ordre = sorted(cols, key=lambda c: -cols[c]); g1 = ordre[0]; g2 = ordre[1] if len(ordre) > 1 else g1
            for (x, y) in pts:   # on rebouche avec le métal voisin sur la même ligne
                for dx in (-1, 1, -2, 2, -3, 3):
                    if (x + dx, y) not in pts and X0 <= x + dx < X0 + W and px[x + dx, y][3] > 0:
                        px[x, y] = px[x + dx, y]; break
            cx = X0 + W // 2 - 1
            for y in range(Y0 + 5, Y0 + H - 3, 8):
                for dx, dy, c in ((0, -2, g2), (1, -2, g2), (-1, -1, g1), (2, -1, g1), (-1, 0, g1), (2, 0, g1), (0, 1, g2), (1, 1, g2)):
                    if px[cx + dx, y + dy][3] > 0: px[cx + dx, y + dy] = c + (255,)
                for x in (cx, cx + 1):
                    for yy in (y - 1, y):
                        if px[x, yy][3] > 0: px[x, yy] = g2 + (255,)
        b2 = io.BytesIO(); im.save(b2, "PNG"); files[n] = b2.getvalue(); stats["ame4"] = stats.get("ame4", 0) + 1

files[MARQ] = json.dumps(sorted(FAIT | {"arc5", "zfight", "ame4"})).encode()
out = io.BytesIO()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for n in sorted(files):
        zi = zipfile.ZipInfo(n, date_time=(2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, files[n])
open(src, "wb").write(out.getvalue())
print(stats)

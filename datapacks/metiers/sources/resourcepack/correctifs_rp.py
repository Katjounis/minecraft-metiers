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
OUTIL = re.compile(r"assets/metiers/models/item/v2/([a-z]_\d+|forge_[a-z0-9_]+)(_[a-z_]+)?\.json$")
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
    # 8. scintillement encore visible (pointes de la pioche du Vétéran...) : écart supplémentaire entre éléments
    if "zfight2" not in FAIT and n.startswith("assets/metiers/models/item/v2/") and els:
        for k, e in enumerate(els):
            ep = min(0.014 * (k + 1), 0.32)
            e["from"] = [c - ep for c in e["from"]]; e["to"] = [c + ep for c in e["to"]]
        stats["zfight2"] = stats.get("zfight2", 0) + 1; changed = True
    # 8 bis. au-delà de 20 pièces l'écart plafonnait : les dernières pièces (picots du dessus des pioches...)
    #        avaient de nouveau des faces confondues. Écart cyclique pour que deux pièces voisines diffèrent toujours.
    if "zfight3" not in FAIT and n.startswith("assets/metiers/models/item/v2/") and els:
        for k, e in enumerate(els):
            ep = 0.016 * ((k % 9) + 1)
            e["from"] = [c - ep for c in e["from"]]; e["to"] = [c + ep for c in e["to"]]
        stats["zfight3"] = stats.get("zfight3", 0) + 1; changed = True
    # 8 ter. dernières faces confondues : on écarte la seconde pièce de 0,02 sur l'axe concerné, jusqu'à n'en plus trouver
    if "zfight4" not in FAIT and n.startswith("assets/metiers/models/item/v2/") and els:
        def axes_rot(e):
            r = e.get("rotation") or {}
            if "angle" in r: return {r["axis"]} if r["angle"] else set()
            return {k for k in ("x", "y", "z") if r.get(k)}
        AX = "xyz"
        for _ in range(6):
            touche = False
            for i in range(len(els)):
                for j in range(i + 1, len(els)):
                    a_, b_ = els[i], els[j]
                    for ax in range(3):
                        ra, rb = axes_rot(a_), axes_rot(b_)
                        if not (ra <= {AX[ax]} and rb <= {AX[ax]}): continue
                        if any(abs(fa - fb) < 0.01 for fa in (a_["from"][ax], a_["to"][ax]) for fb in (b_["from"][ax], b_["to"][ax])):
                            if all(min(a_["to"][q], b_["to"][q]) > max(a_["from"][q], b_["from"][q]) for q in range(3) if q != ax):
                                b_["from"][ax] -= 0.02; b_["to"][ax] += 0.02; touche = True
            if not touche: break
        stats["zfight4"] = stats.get("zfight4", 0) + 1; changed = True
    # 9. arcs vus en miroir par rapport à l'arc vanilla (corde loin, poignée devant) : miroir complet en x
    if "arcmiroir" not in FAIT and re.search(r"/v2/arc_\d+", n) and els:
        for e in els:
            fx, tx = e["from"][0], e["to"][0]
            e["from"][0], e["to"][0] = 16 - tx, 16 - fx
            rr = e.get("rotation")
            if rr:
                if "origin" in rr: rr["origin"][0] = 16 - rr["origin"][0]
                for k in ("z", "y"):
                    if k in rr: rr[k] = -rr[k]
                if "angle" in rr and rr.get("axis") in ("z", "y"): rr["angle"] = -rr["angle"]
            fc = e.get("faces", {})
            if "east" in fc or "west" in fc:
                fe, fw = fc.pop("east", None), fc.pop("west", None)
                if fw is not None: fc["east"] = fw
                if fe is not None: fc["west"] = fe
        stats["arcmiroir"] = stats.get("arcmiroir", 0) + 1; changed = True
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

# 10. icônes de métier en grand pour les barres du haut (défis, heure du métier)
FONT = "assets/metiers/font/icones.json"
if "grandes_icones" not in FAIT and FONT in files:
    fo = json.loads(files[FONT]); prov = fo["providers"]; ajout = []
    for i, j in enumerate("bfmcpenxt"):
        sp = next((q for q in prov if q.get("file", "").endswith(f"font/metier_{j}.png")), None)
        if sp: ajout.append({"type": "bitmap", "file": sp["file"], "height": 16, "ascent": 12, "chars": [chr(0xE200 + i)]})
    prov += ajout; files[FONT] = json.dumps(fo, ensure_ascii=False, indent=1).encode()
    stats["grandes_icones"] = len(ajout)

# 11. cristaux de métier (police d'icônes) : grappe de cristaux à facettes sur un socle, à la place des pastilles
import colorsys
from PIL import ImageDraw
def shade(c, f):
    h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in c[:3]])
    l = max(0, min(1, l * f if f < 1 else l + (1 - l) * (f - 1)))
    return tuple(int(v * 255) for v in colorsys.hls_to_rgb(h, l, s)) + (255,)
def prism(d, cx, base, top, w, col):
    # prisme hexagonal vu de face : pointe, face gauche claire, centre, face droite sombre
    pt = (cx, top); tl = (cx - w, top + w); tr = (cx + w, top + w); bl = (cx - w, base); br = (cx + w, base); m = (cx, base + 1)
    d.polygon([pt, tl, bl, (cx - w // 2, base + 1), (cx, top + w + 1)], fill=shade(col, 1.25))
    d.polygon([pt, tr, br, (cx + w // 2, base + 1), (cx, top + w + 1)], fill=shade(col, 0.55))
    d.polygon([(cx, top + w + 1), (cx - w // 2, base + 1), (cx + w // 2, base + 1)], fill=shade(col, 0.9))
    d.line([pt, (cx, top + w + 1)], fill=shade(col, 1.6))
    d.line([(cx - w + 1, top + w + 1), (cx - w + 1, base - 2)], fill=shade(col, 1.45))
def gem(col):
    S = 24; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    prism(d, 5, 20, 9, 4, shade(col, 0.8))
    prism(d, 19, 20, 11, 3, shade(col, 0.72))
    d.polygon([(12, 0), (6, 6), (6, 21), (18, 21), (18, 6)], fill=(20, 16, 22, 255))
    prism(d, 12, 20, 1, 5, col)
    # socle de roche
    d.polygon([(2, 20), (22, 20), (20, 23), (4, 23)], fill=(70, 62, 58, 255))
    d.line([(4, 21), (19, 21)], fill=(98, 88, 80, 255))
    # contour sombre
    a = im.load(); out = Image.new("RGBA", (S, S), (0, 0, 0, 0)); o = out.load()
    for x in range(S):
        for y in range(S):
            if a[x, y][3] == 0 and any(0 <= x + dx < S and 0 <= y + dy < S and a[x + dx, y + dy][3] > 0 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                o[x, y] = (20, 16, 22, 255)
    out.alpha_composite(im)
    # éclat de lumière
    o = out.load(); o[10, 5] = (255, 255, 255, 255); o[10, 6] = shade(col, 1.8); o[9, 6] = shade(col, 1.8)
    return out

if "gemmes" not in FAIT:
    for n in list(files):
        m = re.search(r"assets/metiers/textures/font/cristal_([a-z])\.png$", n)
        if not m: continue
        ancien = Image.open(io.BytesIO(files[n])).convert("RGBA")
        b3 = io.BytesIO(); gem(ancien.getpixel((5, 7))[:3]).save(b3, "PNG"); files[n] = b3.getvalue()
        stats["gemmes"] = stats.get("gemmes", 0) + 1

# 12. arcs trop grands dans la barre d'objets (coupés) : échelle « gui » calculée sur l'arc au repos,
#     et la même pour ses 3 états bandés, pour que l'icône ne saute pas
if True:   # recalculé à chaque passage (idempotent)
    for n in list(files):
        m = re.search(r"(assets/metiers/models/item/v2/arc_\d+)\.json$", n)
        if not m: continue
        d = json.loads(files[n]); els = d["elements"]
        pts = [p for e in els for p in corners(e)]
        xy = rot_pts([(x - 8, y - 8) for x, y, z in pts], -45)
        xs = [q[0] for q in xy]; ys = [q[1] for q in xy]
        sc = round(15.0 / max(max(xs) - min(xs), max(ys) - min(ys)), 3)
        g = {"rotation": [0, 0, -45], "translation": [round(-(max(xs) + min(xs)) / 2 * sc, 2), round(-(max(ys) + min(ys)) / 2 * sc, 2), 0], "scale": [sc, sc, sc]}
        for k in ("", "_pulling_0", "_pulling_1", "_pulling_2"):
            q = m.group(1) + k + ".json"
            if q in files:
                dq = json.loads(files[q]); dq.setdefault("display", {})["gui"] = g; files[q] = json.dumps(dq, separators=(",", ":")).encode()
        stats["arcgui"] = stats.get("arcgui", 0) + 1

# 13. boutons de tout le jeu au style de la Forge : pierre sombre, filet doré, rivets ; survol doré vif ; inactif éteint
import random
def bouton(etat):
    W, H = 200, 20; im = Image.new("RGBA", (W, H)); px = im.load(); rnd = random.Random(7)
    corps = {"normal": (58, 52, 49), "survol": (74, 64, 52), "inactif": (40, 37, 36)}[etat]
    or_ = {"normal": (176, 136, 58), "survol": (255, 212, 96), "inactif": (70, 64, 60)}[etat]
    for x in range(W):
        for y in range(H):
            n = rnd.randint(-5, 5) if etat != "inactif" else rnd.randint(-2, 2)
            c = tuple(max(0, min(255, v + n)) for v in corps)
            if y in (2,): c = tuple(min(255, v + 18) for v in c)           # reflet haut
            if y in (H - 3,): c = tuple(max(0, v - 16) for v in c)         # ombre bas
            px[x, y] = c + (255,)
    for x in range(W):
        for y in range(H):
            bord = x == 0 or y == 0 or x == W - 1 or y == H - 1
            filet = (x == 1 or y == 1 or x == W - 2 or y == H - 2) and not bord
            if bord: px[x, y] = (16, 13, 12, 255)
            elif filet: px[x, y] = or_ + (255,) if not (y == H - 2) else tuple(int(v * 0.7) for v in or_) + (255,)
    if etat != "inactif":   # rivets dans les coins
        for (x, y) in ((2, 2), (W - 3, 2), (2, H - 3), (W - 3, H - 3)):
            px[x, y] = tuple(min(255, v + 50) for v in or_) + (255,)
    return im

if "boutons" not in FAIT:
    meta = json.dumps({"gui": {"scaling": {"type": "nine_slice", "width": 200, "height": 20, "border": 3}}}).encode()
    for nom, etat in (("button", "normal"), ("button_highlighted", "survol"), ("button_disabled", "inactif")):
        b4 = io.BytesIO(); bouton(etat).save(b4, "PNG")
        files[f"assets/minecraft/textures/gui/sprites/widget/{nom}.png"] = b4.getvalue()
        files[f"assets/minecraft/textures/gui/sprites/widget/{nom}.png.mcmeta"] = meta
    stats["boutons"] = 3

# 14. bandeau de séparation pour les menus (dessiné par une « lettre » de la police d'icônes qui recouvre l'intérieur du bouton)
#     + espaces de largeur fixe (-256..+256 px) pour placer le texte par-dessus
if "bandeau" not in FAIT and FONT in files:
    W, H = 194, 16; im = Image.new("RGBA", (W, H), (30, 25, 22, 255)); px = im.load()
    for x in range(W):
        px[x, 0] = (176, 136, 58, 255); px[x, H - 1] = (120, 92, 40, 255); px[x, 1] = (48, 40, 34, 255); px[x, H - 2] = (20, 16, 14, 255)
    b5 = io.BytesIO(); im.save(b5, "PNG"); files["assets/metiers/textures/font/bandeau.png"] = b5.getvalue()
    fo = json.loads(files[FONT])
    fo["providers"].append({"type": "bitmap", "file": "metiers:font/bandeau.png", "height": 16, "ascent": 11, "chars": ["\ue220"]})
    fo["providers"].append({"type": "space", "advances": {chr(0xE300 + a + 256): a for a in range(-256, 257)}})
    files[FONT] = json.dumps(fo, ensure_ascii=False, indent=1).encode()
    stats["bandeau"] = 1

# 15. sac à dos : la barque à coffre en bambou sert de sac invisible devant les yeux du joueur, sa texture est vidée
#     (contrepartie : les vraies barques à coffre en bambou deviennent invisibles elles aussi)
if "sac_invisible" not in FAIT:
    b6 = io.BytesIO(); Image.new("RGBA", (128, 128), (0, 0, 0, 0)).save(b6, "PNG")
    files["assets/minecraft/textures/entity/chest_boat/bamboo.png"] = b6.getvalue()
    stats["sac_invisible"] = 1

files[MARQ] = json.dumps(sorted(FAIT | {"arc5", "zfight", "ame4", "zfight2", "zfight3", "zfight4", "arcmiroir", "grandes_icones", "gemmes", "arcgui", "boutons", "bandeau", "sac_invisible"})).encode()
out = io.BytesIO()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for n in sorted(files):
        zi = zipfile.ZipInfo(n, date_time=(2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, files[n])
open(src, "wb").write(out.getvalue())
print(stats)

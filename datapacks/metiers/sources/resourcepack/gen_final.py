"""Resource pack final « Métiers » : outils 11 paliers + skins, arcs, heaumes et armures 11 paliers + skins,
objets de la Forge, sac à dos, icônes de menu (police), barres de boss. Sortie : final/pack."""
import os, sys, json, math, shutil, glob
import numpy as np
from PIL import Image
sys.argv = [sys.argv[0], "."]
import gen, gen2, gen3, gen4
from gen2 import palette, R, hx, light, dark

OUT = os.path.abspath("final/pack")
SRC = "/home/claude/katjounis/minecraft-metiers"
shutil.rmtree("final", ignore_errors=True)
A = os.path.join(OUT, "assets", "metiers")
for d in ("items", "models/item/v2", "textures/item/v2", "equipment", "textures/entity/equipment/humanoid",
          "textures/entity/equipment/humanoid_leggings", "font", "textures/font"):
    os.makedirs(f"{A}/{d}", exist_ok=True)

NF = 16
def save(mdl, at, gl, S, name):
    """Écrit le modèle et ses textures sous metiers:item/v2/<name>."""
    t = mdl["textures"]
    for key in list(t):
        t[key] = f"metiers:item/v2/{name}_glow" if key == "glow" else f"metiers:item/v2/{name}"
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
def item(name, model): json.dump({"model": model}, open(f"{A}/items/{name}.json", "w"), separators=(",", ":"))
def skinsel(base_model, per_skin):
    """Sélection du skin par la première chaîne de custom_model_data."""
    return {"type": "minecraft:select", "property": "minecraft:custom_model_data", "index": 0,
            "cases": [{"when": s, "model": per_skin(s)} for s in SKINS], "fallback": base_model}

SKINS = list(gen4.SKINS)
JOBS = {"c": gen2.epee, "b": gen2.hache, "m": gen2.pioche, "x": gen2.pelle, "f": gen2.houe, "p": gen2.canne,
        "e": gen2.houlette, "n": gen2.grimoire, "t": gen2.bourse}

def skinP(s, k):
    P = dict(palette(k)); d = gen4.SKINS[s]
    P["metal"] = R(d["metal"]); P["blade"] = R(d["metal"][:5]); P["glow"] = R(d["glow"]); P["trim"] = R(d["trim"])
    P["cloth"] = R(d["cloth"]); P["grip"] = R(d["grip"]); P["feather"] = R(d["metal"][2:6])
    return P

def epee_sk(k, P):
    if k == 9: return gen2.epee_9("c_9", P)
    return gen2.epee(k, P)

count = 0
# ------------------------------------------------------------------ outils de métier
for j, fn in JOBS.items():
    for k in range(11):
        P = palette(k)
        mdl = fn(k, P); save(*mdl, f"{j}_{k}"); count += 1
        for s in SKINS:
            f2 = epee_sk if j == "c" else fn
            save(*f2(k, skinP(s, k)), f"{j}_{k}_{s}"); count += 1
        if j == "p":
            save(*gen2.canne(k, P, cast=True), f"p_{k}_cast")
            for s in SKINS: save(*gen2.canne(k, skinP(s, k), cast=True), f"p_{k}_{s}_cast")
            cast = lambda n: {"type": "minecraft:condition", "property": "minecraft:fishing_rod/cast", "on_false": ref(n), "on_true": ref(n + "_cast")}
            item(f"p_{k}", skinsel(cast(f"p_{k}"), lambda s, k=k: cast(f"p_{k}_{s}")))
        else:
            item(f"{j}_{k}", skinsel(ref(f"{j}_{k}"), lambda s, j=j, k=k: ref(f"{j}_{k}_{s}")))
    print("outils", j)

# ------------------------------------------------------------------ arcs du Chasseur (11 paliers, 4 états)
def bow_model(n):
    return {"type": "minecraft:condition", "property": "minecraft:using_item", "on_false": ref(n),
            "on_true": {"type": "minecraft:range_dispatch", "property": "minecraft:use_duration", "scale": 0.05,
                        "entries": [{"threshold": 0.65, "model": ref(f"{n}_pulling_1")}, {"threshold": 0.9, "model": ref(f"{n}_pulling_2")}],
                        "fallback": ref(f"{n}_pulling_0")}}
for k in range(11):
    P = palette(k)
    for pull in (None, 0, 1, 2):
        mdl = gen2.arc(k, P, pull); save(*mdl, f"arc_{k}" + (f"_pulling_{pull}" if pull is not None else ""))
    item(f"arc_{k}", bow_model(f"arc_{k}"))
print("arcs")

# ------------------------------------------------------------------ heaumes 11 paliers + skins
def heaume_sk(k, P):
    if k == 10: return gen.heaume_5("heaume_10", P)
    if k == 9: return gen.heaume_5("heaume_9", P)
    real = gen2.palette
    gen2.palette = lambda kk: P
    try:
        return gen2.heaume(k)
    finally:
        gen2.palette = real
for k in range(11):
    save(*gen2.heaume(k), f"heaume_{k}")
    for s in SKINS: save(*heaume_sk(k, skinP(s, k)), f"heaume_{k}_{s}")
    item(f"heaume_{k}", skinsel(ref(f"heaume_{k}"), lambda s, k=k: ref(f"heaume_{k}_{s}")))
print("heaumes")

# ------------------------------------------------------------------ armure portée 11 paliers + skins
import armorgen2
def worn(k, P, tag):
    armorgen2.T[1000] = dict(metal=[gen2.hexs(c) for c in P["metal"]], trim=[gen2.hexs(c) for c in P["trim"]],
                             cloth=[gen2.hexs(c) for c in P["cloth"]], gem=[gen2.hexs(c) for c in P["gem"]],
                             glow=gen2.hexs(P["glow"][1]), runes=k >= 7, sun=k == 10)
    im1, im2 = armorgen2.worn(1000)
    im1, im2 = gen2.motif(k, im1, P), gen2.motif(k, im2, P, legs=True)
    im1.save(f"{A}/textures/entity/equipment/humanoid/{tag}.png", optimize=True)
    im2.save(f"{A}/textures/entity/equipment/humanoid_leggings/{tag}.png", optimize=True)
    json.dump({"layers": {"humanoid": [{"texture": f"metiers:{tag}"}], "humanoid_leggings": [{"texture": f"metiers:{tag}"}]}},
              open(f"{A}/equipment/{tag}.json", "w"))
for k in range(11):
    if k == 10:
        im1, im2 = armorgen2.worn(5)
        im1.save(f"{A}/textures/entity/equipment/humanoid/guilde_10.png"); im2.save(f"{A}/textures/entity/equipment/humanoid_leggings/guilde_10.png")
        json.dump({"layers": {"humanoid": [{"texture": "metiers:guilde_10"}], "humanoid_leggings": [{"texture": "metiers:guilde_10"}]}},
                  open(f"{A}/equipment/guilde_10.json", "w"))
    else:
        worn(k, palette(k), f"guilde_{k}")
    for s in SKINS: worn(k, skinP(s, k), f"guilde_{k}_{s}")
print("armures")

# ------------------------------------------------------------------ icônes 2D des pièces d'armure (recolorées depuis le pack actuel)
OLDICON = f"/tmp/claude-0/-home-claude/83cd9679-6d06-5f5d-ab34-18704b5e4543/scratchpad/rp/assets/metiers/textures/item"
def recolor(src, ramp):
    im = np.array(Image.open(src).convert("RGBA")).astype(float)
    lum = (im[..., 0] * .3 + im[..., 1] * .59 + im[..., 2] * .11) / 255
    out = im.copy()
    idx = np.clip((lum * (len(ramp) - 1)).round().astype(int), 0, len(ramp) - 1)
    rr = np.array(ramp)
    out[..., :3] = rr[idx]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
for piece in ("chestplate", "leggings", "boots"):
    for k in range(11):
        P = palette(k)
        ramp = [P["metal"][0], P["metal"][1], P["metal"][2], P["trim"][2], P["metal"][4], P["metal"][5]]
        recolor(f"{OLDICON}/guilde_{piece}_5.png", ramp).save(f"{A}/textures/item/v2/guilde_{piece}_{k}.png")
        json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": f"metiers:item/v2/guilde_{piece}_{k}"}},
                  open(f"{A}/models/item/v2/guilde_{piece}_{k}.json", "w"))
        item(f"guilde_{piece}_{k}", ref(f"guilde_{piece}_{k}"))
print("icônes armure")

# ------------------------------------------------------------------ objets de la Forge, cristaux, sac à dos
for fn, n in ((gen3.marteau, "forge_marteau"), (gen3.faux, "forge_faux"), (gen3.arc3, "forge_arc3"), (gen3.lasso, "forge_lasso"),
              (gen3.parchemin, "forge_parchemin"), (gen3.aimant, "forge_aimant"), (gen3.cape, "forge_cape")):
    save(*fn(), n); item(n, ref(n))
for c in gen3.CRISTAUX:
    save(*gen3.cristal(c), f"forge_cristal_{c}"); item(f"forge_cristal_{c}", ref(f"forge_cristal_{c}"))

def sac(tier):
    from gen2 import Model, mirror, diamond
    P = dict(palette(0))
    P["cloth"] = R(["#2a1a0e", "#4a2e18", "#6e4626", "#946038"]); P["trim"] = R(["#3a2a06", "#6b4a0b", "#c9972a", "#ffe08a"])
    P["metal"] = R(["#1a1a1a", "#3a3a3a", "#5a5a5a", "#8a8a8a", "#bababa", "#eaeaea"]); P["glow"] = R(["#2a6aa0", "#7cd0ff", "#e0f6ff"])
    m = Model(f"sac_{tier}", P)
    m.add((3.0, 1.0, 5.0), (13.0, 12.0, 11.0), "cloth", name="corps")
    m.add((3.4, 12.0, 5.4), (12.6, 14.0, 10.6), "cloth", name="rabat")
    m.add((4.0, 3.0, 3.6), (12.0, 8.4, 5.0), "cloth", name="poche")
    m.add((7.2, 6.4, 3.3), (8.8, 7.6, 3.6), "trim")
    for x in (4.2, 10.6): m.add((x, 2.0, 11.0), (x + 1.2, 13.0, 11.8), "plate")
    m.add((5.0, 13.6, 7.2), (11.0, 15.4, 8.8), "plate", name="poignee")
    if tier >= 2:
        m.add((2.4, 1.0, 5.6), (3.0, 9.0, 10.4), "cloth"); m.add((13.0, 1.0, 5.6), (13.6, 9.0, 10.4), "cloth")
    if tier >= 3:
        diamond(m, 8, 11.0, 1.6, "glow")
    d = gen2.tool_display(0.62, 4); d["gui"] = {"rotation": [25, 30, 0], "scale": [0.85, 0.85, 0.85]}
    return m.build(d)
for t in (1, 2, 3):
    save(*sac(t), f"sac_{t}"); item(f"sac_{t}", ref(f"sac_{t}"))
print("Forge et sac")

# ------------------------------------------------------------------ police d'icônes (menus, titres, barres)
TF = f"{A}/textures/font"
providers = []
CH = {}
code = [0xE000]
def glyph(name, img, height=9, ascent=8):
    c = chr(code[0]); code[0] += 1
    img.save(f"{TF}/{name}.png")
    providers.append({"type": "bitmap", "file": f"metiers:font/{name}.png", "height": height, "ascent": ascent, "chars": [c]})
    CH[name] = c
# icône de chaque métier = son outil au palier 4, rendue en 16 px
ICONDIR = "icons_final"
for j in JOBS:
    p = f"{ICONDIR}/{j}.png"
    if os.path.exists(p):
        glyph(f"metier_{j}", Image.open(p).convert("RGBA").resize((16, 16), Image.LANCZOS))
# barres de progression : 11 remplissages
for i in range(11):
    im = Image.new("RGBA", (42, 7), (0, 0, 0, 0)); a = np.array(im)
    a[0, 1:41] = a[6, 1:41] = (20, 20, 20, 255); a[1:6, 0] = a[1:6, 41] = (20, 20, 20, 255)
    a[1:6, 1:41] = (58, 58, 58, 255)
    w = round(40 * i / 10)
    if w: a[1:6, 1:1 + w] = (85, 255, 85, 255); a[1, 1:1 + w] = (170, 255, 170, 255); a[5, 1:1 + w] = (40, 170, 40, 255)
    glyph(f"barre_{i}", Image.fromarray(a), height=7, ascent=7)
# cristaux de métier et éclat de boss
CRC = {"b": "#d9a441", "f": "#5fd36a", "m": "#b8bcc6", "c": "#e2484a", "p": "#4fc9e8", "e": "#e070d8", "n": "#9a5cf0", "x": "#5a8cf0", "t": "#3fa860"}
def cristal_px(col):
    c = hx(col); d = dark(c, .5); l = light(c, .5)
    rows = ["..##..", ".#LL#.", "#LCCC#", "#CCCD#", "#CCDD#", ".#DD#.", "..##.."]
    a = np.zeros((7, 6, 4), dtype=np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            col2 = {"#": (20, 20, 20), "L": l, "C": c, "D": d}.get(ch)
            if col2 is not None: a[y, x, :3] = col2; a[y, x, 3] = 255
    return Image.fromarray(a).resize((12, 14), Image.NEAREST)
for j, col in CRC.items(): glyph(f"cristal_{j}", cristal_px(col))
glyph("eclat", cristal_px("#c46cff"))
# cadres de titre (gauche / droite)
FRAMEPAL = {"bois": ["#3a2410", "#7a5230", "#a8743f", None], "fer": ["#202226", "#6a6e76", "#b8bcc6", "#e8eaee"],
            "dore": ["#4a3204", "#b8861e", "#f2c63c", "#e2485a"], "runique": ["#062a32", "#167585", "#2fe6ff", "#d6fbff"],
            "flammes": ["#5a1004", "#e0601a", "#ffb000", "#fff1a0"], "celeste": ["#8a7a50", "#e8d283", "#fffaf0", "#ffffff"]}
def frame(fid, right):
    P = [hx(c) if c else None for c in FRAMEPAL[fid]]
    a = np.zeros((11, 8, 4), dtype=np.uint8)
    def px(x, y, c):
        if c is None: return
        xx = 7 - x if right else x
        a[y, xx, :3] = c; a[y, xx, 3] = 255
    for y in range(1, 10): px(2, y, P[1]); px(3, y, P[0])
    for (x, y, i) in ((3, 0, 2), (4, 0, 2), (5, 0, 1), (3, 10, 2), (4, 10, 2), (5, 10, 1), (2, 1, 2), (2, 9, 1)): px(x, y, P[i])
    extra = {"fer": [(3, 2, 3), (3, 5, 3), (3, 8, 3)], "dore": [(1, 5, 3), (0, 5, 2), (1, 4, 2), (1, 6, 2)],
             "runique": [(1, 3, 2), (0, 4, 3), (1, 7, 2), (0, 6, 3), (2, 5, 3)],
             "flammes": [(1, 2, 2), (0, 1, 3), (1, 5, 1), (0, 4, 2), (1, 8, 2), (0, 7, 3), (1, 9, 1)],
             "celeste": [(1, 2, 3), (0, 3, 3), (0, 4, 2), (0, 5, 3), (0, 6, 2), (1, 7, 2), (1, 8, 1)]}.get(fid, [])
    for (x, y, i) in extra: px(x, y, P[i])
    return Image.fromarray(a)
for fid in FRAMEPAL:
    glyph(f"cadre_{fid}_g", frame(fid, False), height=10, ascent=8)
    glyph(f"cadre_{fid}_d", frame(fid, True), height=10, ascent=8)
# objets de la Forge en icône de bouton
for n in ("forge_marteau", "forge_faux", "forge_arc3", "forge_lasso", "forge_parchemin", "forge_aimant", "forge_cape",
          "forge_cristal_sagesse", "forge_cristal_fortune", "forge_cristal_echo", "forge_cristal_efficacite", "sac_1"):
    p = f"{ICONDIR}/{n}.png"
    if os.path.exists(p): glyph(n, Image.open(p).convert("RGBA").resize((16, 16), Image.LANCZOS))
json.dump({"providers": providers}, open(f"{A}/font/icones.json", "w"), ensure_ascii=False, indent=1)
json.dump(CH, open("final/glyphes.json", "w"), ensure_ascii=False, indent=1)
print("police", len(CH))

# ------------------------------------------------------------------ barres de boss (sprites vanilla retexturés, 4x)
BB = os.path.join(OUT, "assets", "minecraft", "textures", "gui", "sprites", "boss_bar")
os.makedirs(BB, exist_ok=True)
BAR = {"pink": (["#6a4a08", "#e0a820", "#fff1a0"], ["#1a1204", "#c9972a"]),     # heure du métier : or
       "purple": (["#3a1060", "#8a3cff", "#d8b0ff"], ["#0e0716", "#6a4a8a"]),   # défis
       "red": (["#5a1a0a", "#a83a1a", "#e0743a"], ["#1a0d06", "#8a6a3a"]),      # Colosse
       "green": (["#0f3a14", "#2a8a3a", "#7cd86a"], ["#0a1a0a", "#4a6a3a"]),    # Reine arachnide
       "blue": (["#123a5a", "#2f8ad0", "#a8e8ff"], ["#0a1424", "#7a8aa8"]),     # Liche
       "yellow": (["#6a2408", "#e0601a", "#ffc040"], ["#1a0a04", "#c9972a"]),   # Brasier
       "white": (["#1a4a10", "#3aa82a", "#9cff6a"], ["#0a1a06", "#5a7a4a"])}    # Creeper géant
W, H = 182 * 4, 5 * 4
for col, (c, fr) in BAR.items():
    c = [hx(x) for x in c]; fr = [hx(x) for x in fr]
    bg = np.zeros((H, W, 4), dtype=np.uint8); pr = np.zeros((H, W, 4), dtype=np.uint8)
    bg[:, :, :3] = fr[0]; bg[:, :, 3] = 255
    bg[2:H - 2, 2:W - 2, :3] = fr[1]; bg[4:H - 4, 4:W - 4, :3] = (20, 15, 24)
    for x0 in (0, W - 12):
        bg[0:H, x0:x0 + 12, :3] = fr[1]; bg[4:H - 4, x0 + 4:x0 + 8, :3] = c[1]
    pr[4:H - 4, 12:W - 12, 3] = 255
    pr[4:7, 12:W - 12, :3] = c[2]; pr[7:H - 7, 12:W - 12, :3] = c[1]; pr[H - 7:H - 4, 12:W - 12, :3] = c[0]
    Image.fromarray(bg).save(f"{BB}/{col}_background.png"); Image.fromarray(pr).save(f"{BB}/{col}_progress.png")
for n in (6, 10, 12, 20):
    for kind in ("background", "progress"):
        a = np.zeros((H, W, 4), dtype=np.uint8)
        for i in range(1, n):
            x = 12 + round((W - 24) * i / n)
            a[4:H - 4, x - 1:x + 1] = (0, 0, 0, 150)
        Image.fromarray(a).save(f"{BB}/notched_{n}_{kind}.png")
print("barres")

json.dump({"pack": {"description": "Métiers : outils, armures et menus", "min_format": 69, "max_format": 999}},
          open(f"{OUT}/pack.mcmeta", "w"), ensure_ascii=False, indent=1)
print("modèles", count)

"""Armure des Guildes : textures portées (humanoid 64x32 + leggings) et icônes 32x32, 5 paliers."""
import os, sys, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from texgen import hx, blank, poly, bevel, near, stroke, line

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/armor_tex"
os.makedirs(OUT, exist_ok=True)

TIERS = {
    1: dict(name="Bronze guildien", base=["#2e1c0c", "#6e421b", "#a8692f", "#d4945a", "#ffd2a0"],
            trim=["#1f3a1d", "#3f7a3a", "#9fe09a"], gem=["#123c1f", "#2f9a52", "#c9ffd9"], eye=None),
    2: dict(name="Argent runique", base=["#22262f", "#565e70", "#939cb0", "#c8d0df", "#f5f8ff"],
            trim=["#152657", "#2f5fd0", "#9cc2ff"], gem=["#0d2f63", "#2f6fe0", "#d6ecff"], eye="#6fd2ff"),
    3: dict(name="Or royal", base=["#3a2603", "#8f620c", "#d09c1e", "#f1cf4e", "#fff6c4"],
            trim=["#4a0f12", "#a8142c", "#ff6a7a"], gem=["#5e0a16", "#e01e3c", "#ffd6dc"], eye="#ffdf6a"),
    4: dict(name="Obsidienne astrale", base=["#07040d", "#170e26", "#2a1d42", "#433364", "#715e9b"],
            trim=["#0b4552", "#22c9e6", "#d6fbff"], gem=["#3b0d63", "#b45cff", "#f0d9ff"], eye="#4ff0ff", runes=True),
    5: dict(name="Céleste", base=["#5a4210", "#c4a03c", "#efd986", "#fff4d2", "#ffffff"],
            trim=["#5e0a16", "#c4122f", "#ff7088"], gem=["#7a5a10", "#ffd44a", "#fffbe0"], eye="#ffffff", runes=True, sun=True),
}

def C(h):
    return tuple(int(v) for v in hx(h)) + (255,)

# ---------------------------------------------------------------- textures portées
def face(px, x0, y0, w, h, P, shade=0):
    b = P["base"]
    for y in range(h):
        for x in range(w):
            t = y / max(1, h - 1)
            idx = 3 if t < 0.25 else (2 if t < 0.75 else 1)
            idx = max(1, idx - shade)
            col = b[idx]
            if (x * 7 + y * 13 + x0) % 11 == 0 and idx == 2:
                col = b[1]
            px[x0 + x, y0 + y] = C(col)
    for x in range(w):
        px[x0 + x, y0] = C(b[4] if shade == 0 else b[3])
        px[x0 + x, y0 + h - 1] = C(b[0])
    for y in range(h):
        px[x0, y0 + y] = C(b[0]) if y else px[x0, y0 + y]
        px[x0 + w - 1, y0 + y] = C(b[0])

def box(px, ox, oy, w, h, d, P):
    """Faces d'une boîte au format des skins : (ox, oy) = coin du patron."""
    face(px, ox + d, oy, w, d, P)                 # dessus
    face(px, ox + d + w, oy, w, d, P, 1)          # dessous
    face(px, ox, oy + d, d, h, P, 1)              # droite
    face(px, ox + d, oy + d, w, h, P)             # devant
    face(px, ox + d + w, oy + d, d, h, P, 1)      # gauche
    face(px, ox + 2 * d + w, oy + d, w, h, P, 1)  # dos

def trimrow(px, x0, x1, y, P, k=1):
    for x in range(x0, x1):
        px[x, y] = C(P["trim"][2 if (x % 2 == 0) else k])

def gem(px, cx, cy, P, big=False):
    g = P["gem"]
    for dx, dy, c in ((0, -1, 2), (-1, 0, 1), (0, 0, 1), (1, 0, 0), (0, 1, 0)) + (((-1, -1, 0), (1, -1, 0), (-1, 1, 0), (1, 1, 0)) if big else ()):
        px[cx + dx, cy + dy] = C(g[c])
    px[cx, cy] = C(g[2]) if not big else C(g[1])
    if big:
        px[cx - 1, cy - 1] = C(g[2])

def worn(t):
    P = TIERS[t]
    im1 = Image.new("RGBA", (64, 32), (0, 0, 0, 0)); a = im1.load()
    im2 = Image.new("RGBA", (64, 32), (0, 0, 0, 0)); b = im2.load()
    # --- couche 1 : casque, plastron, bras, bottes
    box(a, 0, 0, 8, 8, 8, P)            # tête
    box(a, 16, 16, 8, 12, 4, P)         # corps
    box(a, 40, 16, 4, 12, 4, P)         # bras
    # bottes : bas des jambes
    for (x0, y0, w, h) in ((0, 26, 4, 6), (4, 26, 4, 6), (8, 26, 4, 6), (12, 26, 4, 6)):
        face(a, x0, y0, w, h, P, 1 if x0 != 4 else 0)
    face(a, 4, 16, 4, 4, P); face(a, 8, 16, 4, 4, P, 1)
    for x in range(0, 16):
        a[x, 26] = C(P["trim"][2 if x % 2 == 0 else 1])
        a[x, 31] = C(P["base"][0])
    # casque : visière, crête, gemme frontale
    for x in range(9, 15):
        a[x, 12] = C("#0b0b10"); a[x, 13] = C(P["base"][0])
    if P["eye"]:
        a[10, 12] = C(P["eye"]); a[13, 12] = C(P["eye"])
    trimrow(a, 8, 16, 8, P)
    for y in range(0, 8):
        a[12, y] = C(P["trim"][1 + (y % 2)]); a[11, y] = C(P["trim"][0])
    gem(a, 12, 10, P)
    for x in (8, 15):
        for y in range(9, 16):
            a[x, y] = C(P["trim"][1])
    # plastron : emblème, ligne centrale, ceinture, épaules
    for y in range(20, 32):
        a[23, y] = C(P["trim"][1]); a[24, y] = C(P["trim"][2] if y % 3 else P["trim"][1])
    trimrow(a, 20, 28, 20, P)
    trimrow(a, 20, 28, 30, P, 0)
    gem(a, 24, 24, P, big=t >= 3)
    for x in range(32, 40):
        a[x, 30] = C(P["trim"][1])
    # bras : épaulière + bracelet
    trimrow(a, 40, 56, 20, P); trimrow(a, 40, 56, 21, P, 0)
    trimrow(a, 40, 56, 29, P)
    for x in range(44, 48):
        a[x, 16] = C(P["trim"][2])
    if t >= 2:
        gem(a, 46, 24, P)
    # runes lumineuses
    if P.get("runes"):
        rc = P["eye"]
        for (x, y) in ((21, 22), (26, 22), (21, 27), (26, 27), (34, 23), (37, 26), (42, 25), (50, 25), (9, 10), (14, 10)):
            a[x, y] = C(rc)
    # soleil céleste dans le dos + ailes stylisées
    if P.get("sun"):
        cx, cy = 36, 25
        for ang in range(0, 360, 45):
            dx = round(2.6 * math.cos(math.radians(ang))); dy = round(2.6 * math.sin(math.radians(ang)))
            a[cx + dx, cy + dy] = C(P["trim"][2])
        a[cx, cy] = C("#ffffff"); a[cx - 1, cy] = C(P["gem"][1]); a[cx + 1, cy] = C(P["gem"][1])
        a[cx, cy - 1] = C(P["gem"][1]); a[cx, cy + 1] = C(P["gem"][1])
    # --- couche 2 : jambières
    box(b, 0, 16, 4, 12, 4, P)
    box(b, 16, 16, 8, 12, 4, P)
    for y in range(16, 32):           # on ne garde que la taille sur le corps
        for x in range(16, 40):
            if y < 26:
                b[x, y] = (0, 0, 0, 0)
    for x in range(16, 40):
        b[x, 26] = C(P["trim"][2 if x % 2 else 1])
    for x in range(0, 16):
        b[x, 23] = C(P["trim"][1]); b[x, 24] = C(P["base"][3])
    gem(b, 6, 24, P) if t >= 2 else None
    gem(b, 24, 28, P)
    return im1, im2

# ---------------------------------------------------------------- icônes 32x32
SHAPES = {
    "helmet": [(6, 12), (8, 6), (13, 3), (19, 3), (24, 6), (26, 12), (26, 22), (21, 22), (21, 15), (11, 15), (11, 22), (6, 22)],
    "chestplate": [(4, 5), (11, 3), (13, 6), (19, 6), (21, 3), (28, 5), (28, 13), (24, 13), (24, 28), (8, 28), (8, 13), (4, 13)],
    "leggings": [(6, 4), (26, 4), (27, 28), (19, 28), (17, 12), (15, 12), (13, 28), (5, 28)],
    "boots": [(3, 8), (11, 8), (11, 20), (14, 22), (14, 26), (3, 26), (18, 8), (26, 8), (26, 20), (29, 22), (29, 26), (18, 26)],
}

def icon(piece, t):
    P = TIERS[t]
    m = blank()
    pts = SHAPES[piece]
    if piece == "boots":
        poly(m, pts[:6]); poly(m, pts[6:])
    else:
        poly(m, pts)
    bv = bevel(m, 5)
    img = np.zeros((32, 32, 4))
    pal = [hx(c) for c in P["base"]]
    for y in range(32):
        for x in range(32):
            if m[y, x]:
                img[y, x, :3] = pal[bv[y, x]]; img[y, x, 3] = 255
                if bv[y, x] == 2 and (x * 13 + y * 7) % 9 == 0:
                    img[y, x, :3] = pal[1] * 0.3 + pal[2] * 0.7
    tr = [hx(c) for c in P["trim"]]
    def setp(x, y, c):
        if 0 <= x < 32 and 0 <= y < 32 and m[y, x]:
            img[y, x, :3] = c
    if piece == "helmet":
        for x in range(8, 25):
            setp(x, 9, tr[1] if x % 2 else tr[2])
        for x in range(12, 21):
            setp(x, 15, hx("#0b0b10"))
        for y in range(3, 15):
            setp(16, y, tr[2] if y % 2 else tr[1])
        gc = (16, 11)
    elif piece == "chestplate":
        for y in range(7, 28):
            setp(16, y, tr[2] if y % 3 else tr[1]); setp(15, y, tr[1])
        for x in range(8, 25):
            setp(x, 25, tr[1] if x % 2 else tr[2])
        for x in range(4, 13):
            setp(x, 10, tr[1])
        for x in range(20, 29):
            setp(x, 10, tr[1])
        gc = (16, 15)
    elif piece == "leggings":
        for x in range(6, 27):
            setp(x, 6, tr[1] if x % 2 else tr[2])
        for x in range(5, 14):
            setp(x, 19, tr[1])
        for x in range(19, 28):
            setp(x, 19, tr[1])
        gc = (16, 8)
    else:
        for x in list(range(3, 12)) + list(range(18, 27)):
            setp(x, 10, tr[1] if x % 2 else tr[2])
        for x in list(range(3, 15)) + list(range(18, 30)):
            setp(x, 25, tr[0])
        gc = (7, 16)
    g = [hx(c) for c in P["gem"]]
    big = t >= 3
    cx, cy = gc
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            d = abs(dx) + abs(dy)
            if d <= (2 if big else 1):
                c = g[0] if d == (2 if big else 1) else g[1]
                if (dx, dy) == (-1, -1) or (not big and (dx, dy) == (0, -1)):
                    c = g[2]
                setp(cx + dx, cy + dy, c)
    if piece == "boots":
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if abs(dx) + abs(dy) <= 1:
                    setp(22 + dx, 16 + dy, g[2] if (dx, dy) == (0, -1) else g[1])
    if P.get("runes"):
        rc = hx(P["eye"])
        for (x, y) in ((10, 20), (22, 20), (12, 12), (20, 12), (9, 15), (23, 15)):
            setp(x, y, rc)
    # contour
    out = img.copy()
    for y in range(32):
        for x in range(32):
            if img[y, x, 3] == 0 and any(0 <= y + dy < 32 and 0 <= x + dx < 32 and img[y + dy, x + dx, 3] > 0
                                         for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out[y, x, :3] = pal[0]; out[y, x, 3] = 255
    img = out
    if P.get("sun"):
        for y in range(32):
            for x in range(32):
                if img[y, x, 3] == 0 and any(0 <= y + dy < 32 and 0 <= x + dx < 32 and img[y + dy, x + dx, 3] == 255
                                             for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                    img[y, x, :3] = hx("#fff07a"); img[y, x, 3] = 60
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA")

def preview(im1, im2, scale=10):
    """Vue de face approximative sur un mannequin."""
    W, H = 16, 32
    pv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    def paste(src, box, dst):
        pv.alpha_composite(src.crop(box), dst)
    paste(im1, (8, 8, 16, 16), (4, 0))          # tête
    paste(im2, (4, 20, 8, 32), (4, 20)); paste(im2, (4, 20, 8, 32), (8, 20))   # jambes
    paste(im2, (20, 20, 28, 32), (4, 8))        # taille
    paste(im1, (20, 20, 28, 32), (4, 8))        # torse
    paste(im1, (44, 20, 48, 32), (0, 8)); paste(im1, (44, 20, 48, 32), (12, 8))  # bras
    boots = im1.crop((4, 26, 8, 32))
    pv.alpha_composite(boots, (4, 26)); pv.alpha_composite(boots, (8, 26))
    return pv.resize((W * scale, H * scale), Image.NEAREST)

if __name__ == "__main__":
    sheet = Image.new("RGBA", (5 * 300, 600), (40, 44, 52, 255))
    for t in range(1, 6):
        im1, im2 = worn(t)
        im1.save(os.path.join(OUT, f"guilde_{t}.png"))
        im2.save(os.path.join(OUT, f"guilde_{t}_leggings.png"))
        sheet.alpha_composite(preview(im1, im2, 9), ((t - 1) * 300 + 78, 10))
        for i, piece in enumerate(("helmet", "chestplate", "leggings", "boots")):
            ic = icon(piece, t)
            ic.save(os.path.join(OUT, f"guilde_{piece}_{t}.png"))
            sheet.alpha_composite(ic.resize((64, 64), Image.NEAREST), ((t - 1) * 300 + 10 + i * 70, 310 + 0))
            sheet.alpha_composite(ic.resize((64, 64), Image.NEAREST), ((t - 1) * 300 + 10 + i * 70, 380)) if False else None
    sheet.save(os.path.join(OUT, "_apercu.png"))
    print("ok")

"""Armure des Guildes v2 : textures portées 128x64 (double résolution), plaques biseautées, cape brodée."""
import os, sys, math
import numpy as np
from PIL import Image

S = 2
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/armor_tex2"
os.makedirs(OUT, exist_ok=True)

def hx(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)

T = {
    1: dict(metal=["#1e1208", "#4a2c12", "#7a4a1e", "#a8692f", "#d4945a", "#ffd2a0"],
            trim=["#2e2206", "#7a5c16", "#b8953a", "#ead48a"], cloth=["#0b1d0d", "#183e1c", "#28672e", "#42954a"],
            gem=["#0b2e17", "#1f8a47", "#62e08e", "#e2ffec"], glow=None),
    2: dict(metal=["#111419", "#323946", "#545c6e", "#8a93a8", "#c3cbdb", "#f5f8ff"],
            trim=["#2e2206", "#7a5c16", "#c9a640", "#f6e39a"], cloth=["#0a1230", "#172a64", "#2848a8", "#5277dc"],
            gem=["#0a2050", "#1f5fd8", "#7fb8ff", "#e8f4ff"], glow="#7fd8ff"),
    3: dict(metal=["#241602", "#5e3f06", "#9a6c0c", "#d09e24", "#f0cc4c", "#fff3bc"],
            trim=["#300407", "#6e0b16", "#a81628", "#e2485a"], cloth=["#24040a", "#520a16", "#8a1224", "#c02a3c"],
            gem=["#4a0710", "#c8142f", "#ff6a80", "#ffe4ea"], glow="#ffe07a"),
    4: dict(metal=["#030107", "#0b0715", "#150d23", "#261a3c", "#3e2f5c", "#6a5893"],
            trim=["#06222b", "#147186", "#2cc8e0", "#c4f9ff"], cloth=["#0c0416", "#1e0e36", "#341a5c", "#532c90"],
            gem=["#2a0848", "#8a32d8", "#cf8cff", "#f6e6ff"], glow="#46ecff", runes=True),
    5: dict(metal=["#3f2d06", "#8c6c22", "#c4a456", "#e8d283", "#fbf0cc", "#ffffff"],
            trim=["#5a3e08", "#b8861e", "#f2c63c", "#fff6c8"], cloth=["#30040a", "#6e0a16", "#b0122a", "#e8485c"],
            gem=["#6a4a08", "#e8b020", "#fff07a", "#ffffff"], glow="#fff7c0", runes=True, sun=True),
}

class Tex:
    def __init__(self):
        self.a = np.zeros((32 * S, 64 * S, 4))
    def put(self, x, y, c, k=1.0):
        if 0 <= x < self.a.shape[1] and 0 <= y < self.a.shape[0]:
            c = np.asarray(c, dtype=float)
            if self.a[y, x, 3] == 0 or k >= 1:
                self.a[y, x, :3] = c if self.a[y, x, 3] == 0 else self.a[y, x, :3] * (1 - k) + c * k
            else:
                self.a[y, x, :3] = self.a[y, x, :3] * (1 - k) + c * k
            self.a[y, x, 3] = 255
    def clear(self, x, y, w, h):
        self.a[y:y + h, x:x + w] = 0
    def img(self):
        return Image.fromarray(np.clip(self.a, 0, 255).astype(np.uint8), "RGBA")

def R(x, y, w, h):
    return (x * S, y * S, w * S, h * S)

# ---------------------------------------------------------------- primitives
def plate(t, rect, ramp, light=0, rivets=False, seam_bottom=True):
    """Plaque biseautée : reflet en haut à gauche, ombre en bas à droite."""
    x0, y0, w, h = rect
    m = [hx(c) for c in ramp]
    for y in range(h):
        for x in range(w):
            g = y / max(1, h - 1)
            base = 3 + light - (1 if g > 0.6 else 0)
            base = max(1, min(4, base))
            col = m[base]
            if (x * 5 + y * 3 + x0) % 13 == 0:
                col = col * 0.88 + m[base - 1] * 0.12
            t.put(x0 + x, y0 + y, col)
    for x in range(w):
        t.put(x0 + x, y0, m[min(5, 4 + light)])
        t.put(x0 + x, y0 + h - 1, m[0] if seam_bottom else m[1])
        if h > 3:
            t.put(x0 + x, y0 + h - 2, m[1], 0.6)
    for y in range(h):
        t.put(x0, y0 + y, m[4], 0.7 if y else 1)
        t.put(x0 + w - 1, y0 + y, m[1])
    if rivets and w >= 6:
        for rx in (x0 + 2, x0 + w - 3):
            t.put(rx, y0 + 2, m[5]); t.put(rx + 1, y0 + 2, m[2]); t.put(rx, y0 + 3, m[1])

def band(t, x0, y0, w, h, ramp, dots=True):
    m = [hx(c) for c in ramp]
    for y in range(h):
        for x in range(w):
            c = m[3] if y == 0 else (m[1] if y == h - 1 else m[2])
            t.put(x0 + x, y0 + y, c)
    if dots and h >= 3:
        for x in range(x0 + 2, x0 + w - 1, 4):
            t.put(x, y0 + h // 2, m[3]); t.put(x + 1, y0 + h // 2, m[0])

def vband(t, x0, y0, w, h, ramp):
    m = [hx(c) for c in ramp]
    for y in range(h):
        for x in range(w):
            c = m[3] if x == 0 else (m[1] if x == w - 1 else m[2])
            t.put(x0 + x, y0 + y, c)

def gem(t, cx, cy, P, r=2):
    g = [hx(c) for c in P["gem"]]
    tr = [hx(c) for c in P["trim"]]
    for dy in range(-r - 1, r + 2):
        for dx in range(-r - 1, r + 2):
            d = abs(dx) + abs(dy)
            if d == r + 1:
                t.put(cx + dx, cy + dy, tr[2] if dy < 0 or dx < 0 else tr[1])
            elif d <= r:
                c = g[1] if d <= r - 1 else g[0]
                if dx + dy < -r + 1:
                    c = g[2]
                t.put(cx + dx, cy + dy, c)
    t.put(cx - 1, cy - 1, g[3]); t.put(cx, cy - 1, g[2])
    if P["glow"]:
        gl = hx(P["glow"])
        for dy in range(-r - 2, r + 3):
            for dx in range(-r - 2, r + 3):
                if abs(dx) + abs(dy) == r + 2:
                    t.put(cx + dx, cy + dy, gl, 0.35)

def glow_px(t, x, y, P, k=1.0):
    if P["glow"]:
        gl = hx(P["glow"])
        t.put(x, y, gl, k)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            t.put(x + dx, y + dy, gl, 0.3 * k)

def chain(t, rect, P):
    x0, y0, w, h = rect
    m = [hx(c) for c in P["metal"]]
    for y in range(h):
        for x in range(w):
            c = m[3] if (x + (y // 2)) % 2 == 0 else m[1]
            if y % 2 == 1:
                c = c * 0.8 + m[0] * 0.2
            t.put(x0 + x, y0 + y, c)

def cloth(t, rect, P, emblem=True):
    x0, y0, w, h = rect
    c = [hx(v) for v in P["cloth"]]
    for y in range(h):
        for x in range(w):
            fold = (x * 3 // 4) % 3
            col = c[2] if fold == 0 else (c[3] if fold == 1 else c[1])
            if y > h - 4 and (x + (y - (h - 4)) * 2) % 5 == 0:
                continue
            t.put(x0 + x, y0 + y, col)
    band(t, x0, y0, w, 3, P["trim"], dots=False)
    for y in range(3, h - 3):
        t.put(x0 + 1, y0 + y, hx(P["trim"][2]), 0.8)
        t.put(x0 + w - 2, y0 + y, hx(P["trim"][2]), 0.8)
    if emblem:
        cx, cy = x0 + w // 2, y0 + h // 2
        tr = [hx(v) for v in P["trim"]]
        if P.get("sun"):
            for ang in range(0, 360, 30):
                for rr in (3, 4, 5):
                    t.put(cx + round(rr * math.cos(math.radians(ang))), cy + round(rr * math.sin(math.radians(ang))), tr[3] if rr < 5 else tr[2])
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    if dx * dx + dy * dy <= 4:
                        t.put(cx + dx, cy + dy, hx(P["gem"][2]))
            # ailes brodées
            for i in range(6):
                for side in (-1, 1):
                    t.put(cx + side * (6 + i), cy - 3 + i // 2, tr[3])
                    t.put(cx + side * (6 + i), cy - 2 + i // 2, tr[2])
        else:
            # écu brodé
            for dy in range(-5, 6):
                half = 4 if dy < 2 else 4 - (dy - 1)
                for dx in range(-half, half + 1):
                    edge = abs(dx) == half or dy == -5
                    t.put(cx + dx, cy + dy, tr[2] if edge else c[0])
            gem(t, cx, cy - 1, P, 1)

def runes(t, rect, P, step=5):
    if not P.get("runes"):
        return
    x0, y0, w, h = rect
    for y in range(2, h - 2, step):
        for x in range(2, w - 2, step + 1):
            if (x * 7 + y * 3) % 4 == 0:
                glow_px(t, x0 + x, y0 + y, P, 0.9)

# ---------------------------------------------------------------- pièces
def helmet(t, P):
    M = P["metal"]
    fx, fy, fw, fh = R(8, 8, 8, 8)
    plate(t, (fx, fy, fw, fh), M)
    band(t, fx, fy + 3, fw, 3, P["trim"])
    gem(t, fx + 8, fy + 4, P, 1)
    for x in range(fx + 2, fx + 14):
        t.put(x, fy + 7, hx("#06060a")); t.put(x, fy + 8, hx("#0d0d14"))
    for y in range(fy + 8, fy + 13):
        t.put(fx + 7, y, hx("#06060a")); t.put(fx + 8, y, hx("#0d0d14"))
    if P["glow"]:
        for ex in (fx + 4, fx + 5, fx + 10, fx + 11):
            glow_px(t, ex, fy + 7, P)
    else:
        for ex in (fx + 4, fx + 11):
            t.put(ex, fy + 7, hx(P["gem"][2]))
    for (rx, ry) in ((fx + 2, fy + 11), (fx + 13, fy + 11), (fx + 2, fy + 14), (fx + 13, fy + 14)):
        t.put(rx, ry, hx(M[5])); t.put(rx, ry + 1, hx(M[1]))
    for y in range(fy, fy + 3):
        t.put(fx + 7, y, hx(M[5])); t.put(fx + 8, y, hx(M[4]))
    if P.get("runes"):
        for (x, y) in ((fx + 3, fy + 12), (fx + 12, fy + 12), (fx + 5, fy + 1), (fx + 10, fy + 1)):
            glow_px(t, x, y, P)
    # dessus : crête
    x0, y0, w, h = R(8, 0, 8, 8)
    plate(t, (x0, y0, w, h), M, 1)
    vband(t, x0 + 6, y0, 4, h, P["trim"])
    # côtés
    for sx in (0, 16):
        x0, y0, w, h = R(sx, 8, 8, 8)
        plate(t, (x0, y0, w, h // 2), M, 0)
        plate(t, (x0, y0 + h // 2, w, h // 2), M, -1)
        band(t, x0, y0 + 3, w, 3, P["trim"])
        gem(t, x0 + w // 2, y0 + 11, P, 1)
    # nuque en lames
    x0, y0, w, h = R(24, 8, 8, 8)
    for i in range(4):
        plate(t, (x0, y0 + i * 4, w, 4), M, -1 if i > 1 else 0)
    vband(t, x0 + 6, y0, 4, 7, P["trim"])
    x0, y0, w, h = R(16, 0, 8, 8)
    plate(t, (x0, y0, w, h), M, -1)

def chest(t, P):
    M = P["metal"]
    x0, y0, w, h = R(20, 20, 8, 12)
    plate(t, (x0, y0 + 2, w // 2, 10), M, 1, rivets=True)
    plate(t, (x0 + w // 2, y0 + 2, w // 2, 10), M, 0, rivets=True)
    for i in range(3):
        plate(t, (x0 + 1, y0 + 12 + i * 3, w - 2, 3), M, -i // 2)
    t.put(x0, y0 + 12, hx(M[0]))
    band(t, x0, y0, w, 2, P["trim"], dots=False)
    band(t, x0, y0 + 20, w, 4, P["trim"])
    gem(t, x0 + w // 2, y0 + 21, P, 1)
    cx, cy = x0 + w // 2, y0 + 7
    tr = [hx(c) for c in P["trim"]]
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            if abs(dx) + abs(dy) == 5:
                t.put(cx + dx, cy + dy, tr[3] if dy < 0 else tr[1])
            elif abs(dx) + abs(dy) == 4:
                t.put(cx + dx, cy + dy, tr[0])
    gem(t, cx, cy, P, 2)
    if P.get("runes"):
        for (x, y) in ((x0 + 3, y0 + 14), (x0 + 12, y0 + 14), (x0 + 3, y0 + 17), (x0 + 12, y0 + 17), (x0 + 2, y0 + 4), (x0 + 13, y0 + 4)):
            glow_px(t, x, y, P)
    # flancs
    for sx in (16, 28):
        a0, b0, aw, ah = R(sx, 20, 4, 12)
        plate(t, (a0, b0, aw, 12), M, 0)
        for i in range(3):
            plate(t, (a0, b0 + 12 + i * 3, aw, 3), M, -1)
        band(t, a0, b0 + 20, aw, 4, P["trim"], dots=False)
    # dessus / dessous
    a0, b0, aw, ah = R(20, 16, 8, 4)
    plate(t, (a0, b0, aw, ah), M, 1)
    band(t, a0, b0 + ah - 2, aw, 2, P["trim"], dots=False)
    a0, b0, aw, ah = R(28, 16, 8, 4)
    plate(t, (a0, b0, aw, ah), M, -1)
    # dos : cape
    cloth(t, R(32, 20, 8, 12), P)

def arm(t, P):
    M = P["metal"]
    for sx in (40, 44, 48, 52):
        x0, y0, w, h = R(sx, 20, 4, 12)
        plate(t, (x0, y0, w, 4), M, 1, rivets=True)
        plate(t, (x0, y0 + 3, w, 3), M, 0)
        plate(t, (x0, y0 + 6, w, 3), M, -1)
        band(t, x0, y0 + 2, w, 2, P["trim"], dots=False)
        chain(t, (x0, y0 + 9, w, 5), P)
        plate(t, (x0, y0 + 14, w, 10), M, 0)
        band(t, x0, y0 + 14, w, 2, P["trim"], dots=False)
        band(t, x0, y0 + 21, w, 3, P["trim"], dots=False)
        if sx == 44:
            gem(t, x0 + w // 2, y0 + 18, P, 1)
        elif P.get("runes"):
            glow_px(t, x0 + w // 2, y0 + 18, P)
    x0, y0, w, h = R(44, 16, 4, 4)
    plate(t, (x0, y0, w, h), M, 1)
    gem(t, x0 + w // 2, y0 + h // 2, P, 1)
    x0, y0, w, h = R(48, 16, 4, 4)
    plate(t, (x0, y0, w, h), M, -1)

def boots(t, P):
    M = P["metal"]
    for sx in (0, 4, 8, 12):
        x0, y0, w, h = R(sx, 26, 4, 6)
        band(t, x0, y0, w, 3, P["trim"])
        plate(t, (x0, y0 + 3, w, 3), M, 0)
        plate(t, (x0, y0 + 6, w, 3), M, -1)
        plate(t, (x0, y0 + 9, w, 3), M, 1 if sx == 4 else -1)
        if sx == 4:
            gem(t, x0 + w // 2, y0 + 5, P, 1)
    for sx in (4, 8):
        x0, y0, w, h = R(sx, 16, 4, 4)
        plate(t, (x0, y0, w, h), M, -1)

def leggings(t, P):
    M = P["metal"]
    # taille : ceinture + tassettes (moitié basse du torse)
    for (sx, sw) in ((16, 4), (20, 8), (28, 4), (32, 8)):
        x0, y0, w, h = R(sx, 26, sw, 6)
        band(t, x0, y0, w, 3, P["trim"])
        if sw == 8:
            plate(t, (x0, y0 + 3, w // 2 - 1, 9), M, 0)
            plate(t, (x0 + w // 2 + 1, y0 + 3, w // 2 - 1, 9), M, 0)
            gem(t, x0 + w // 2, y0 + 1, P, 1)
        else:
            plate(t, (x0, y0 + 3, w, 9), M, -1)
    for sx in (0, 4, 8, 12):
        x0, y0, w, h = R(sx, 20, 4, 12)
        plate(t, (x0, y0, w, 10), M, 0, rivets=True)
        plate(t, (x0, y0 + 10, w, 6), M, 1)
        plate(t, (x0, y0 + 16, w, 8), M, -1)
        band(t, x0, y0 + 9, w, 2, P["trim"], dots=False)
        if sx == 4:
            gem(t, x0 + w // 2, y0 + 12, P, 1)
            if P.get("runes"):
                glow_px(t, x0 + 2, y0 + 4, P); glow_px(t, x0 + 5, y0 + 4, P)
    for sx in (4, 8):
        x0, y0, w, h = R(sx, 16, 4, 4)
        plate(t, (x0, y0, w, h), M, 0)

def worn(tier):
    P = T[tier]
    t1, t2 = Tex(), Tex()
    helmet(t1, P); chest(t1, P); arm(t1, P); boots(t1, P)
    leggings(t2, P)
    return t1.img(), t2.img()

# ---------------------------------------------------------------- aperçu (face et dos)
def mannequin(im1, im2, back=False):
    W, H = 16 * S, 32 * S
    pv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    skin = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    def crop(im, x, y, w, h):
        return im.crop((x * S, y * S, (x + w) * S, (y + h) * S))
    if not back:
        parts = [(im2, (4, 20, 4, 12), (4, 20)), (im2, (4, 20, 4, 12), (8, 20)), (im2, (20, 20, 8, 12), (4, 8)),
                 (im1, (8, 8, 8, 8), (4, 0)), (im1, (20, 20, 8, 12), (4, 8)), (im1, (44, 20, 4, 12), (0, 8)),
                 (im1, (44, 20, 4, 12), (12, 8)), (im1, (4, 26, 4, 6), (4, 26)), (im1, (4, 26, 4, 6), (8, 26))]
    else:
        parts = [(im2, (12, 20, 4, 12), (4, 20)), (im2, (12, 20, 4, 12), (8, 20)), (im2, (32, 20, 8, 12), (4, 8)),
                 (im1, (24, 8, 8, 8), (4, 0)), (im1, (32, 20, 8, 12), (4, 8)), (im1, (52, 20, 4, 12), (0, 8)),
                 (im1, (52, 20, 4, 12), (12, 8)), (im1, (12, 26, 4, 6), (4, 26)), (im1, (12, 26, 4, 6), (8, 26))]
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for (x, y, w, h) in ((4, 0, 8, 8), (4, 8, 8, 12), (0, 8, 4, 12), (12, 8, 4, 12), (4, 20, 8, 12)):
        base.paste((90, 74, 62, 255), (x * S, y * S, (x + w) * S, (y + h) * S))
    pv.alpha_composite(base)
    for im, (x, y, w, h), (dx, dy) in parts:
        pv.alpha_composite(crop(im, x, y, w, h), (dx * S, dy * S))
    return pv

if __name__ == "__main__":
    sheet = Image.new("RGBA", (5 * 330, 420), (34, 36, 44, 255))
    for tier in range(1, 6):
        im1, im2 = worn(tier)
        im1.save(os.path.join(OUT, f"guilde_{tier}.png"))
        im2.save(os.path.join(OUT, f"guilde_{tier}_leggings.png"))
        f = mannequin(im1, im2).resize((16 * S * 5, 32 * S * 5 // 1), Image.NEAREST)
        b = mannequin(im1, im2, True).resize((16 * S * 5, 32 * S * 5 // 1), Image.NEAREST)
        f = f.resize((150, 300), Image.NEAREST); b = b.resize((150, 300), Image.NEAREST)
        sheet.alpha_composite(f, ((tier - 1) * 330 + 10, 60))
        sheet.alpha_composite(b, ((tier - 1) * 330 + 170, 60))
    sheet.save(os.path.join(OUT, "_apercu.png"))
    print("ok")

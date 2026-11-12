"""Textures 32x32 des outils de métier (5 outils x 11 paliers), animées aux paliers hauts."""
import math, os, json, sys
import numpy as np
from PIL import Image

N = 32
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/rp_textures"
os.makedirs(OUT, exist_ok=True)

def hx(h):
    h = h.lstrip("#"); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], dtype=float)

# ---------------------------------------------------------------- matériaux par palier
# head : contour, ombre, moyen, clair, reflet ; handle : contour, ombre, moyen, clair
TIERS = [
    dict(name="fer", head=["#25262b", "#5d6169", "#8d929b", "#bcc1c9", "#eef1f5"],
         handle=["#2e1d0e", "#5c3a1d", "#7f532c", "#a3713f"], band=None, trim=None, gem=None),
    dict(name="cuivre", head=["#33160c", "#7d3a20", "#b45f37", "#de8a5c", "#ffc9a3"], patina="#4c9e87",
         handle=["#24170c", "#4a3119", "#694626", "#8a6036"], band=["#3a2416", "#5e3b24", "#7d5131"], trim=None, gem=None),
    dict(name="or", head=["#3d2903", "#93660d", "#d39f1f", "#f3d250", "#fff6c4"],
         handle=["#1e130a", "#3d2715", "#56381f", "#71492a"], band=["#4a1f12", "#7a3420", "#a14a2e"], trim=None,
         gem=["#123c1f", "#2f9a52", "#9df2b6"]),
    dict(name="emeraude", studs=2, head=["#05291a", "#0e6d3d", "#1ca95a", "#56dd8b", "#d0ffe2"],
         handle=["#1f1a14", "#3e352a", "#5a4d3d", "#786853"], band=["#1a2f3b", "#2d4f63", "#447791"], trim=["#5b4310", "#b58c2a", "#ecd27a"],
         gem=["#0b3d24", "#2fd07a", "#c9ffe0"]),
    dict(name="diamant", studs=3, glint=True, anim=True, head=["#0a3238", "#17838c", "#33c4cb", "#8cefed", "#f2ffff"],
         handle=["#1b1622", "#352b44", "#4e4063", "#6a5885"], band=["#1b2346", "#2f3d7a", "#4b5fb3"], trim=["#5b4310", "#b58c2a", "#ecd27a"],
         gem=["#0d2f63", "#2f6fe0", "#bfe0ff"]),
    dict(name="amethyste", studs=3, crystals=["#5f2d91", "#b787ec", "#f3e7ff"], glint=True, anim=True, head=["#24103a", "#552886", "#844cc2", "#b787ec", "#f3e7ff"],
         handle=["#1f0d12", "#41192a", "#5f2640", "#7f3858"], band=["#2b1b3d", "#4b2f6b", "#6d47a0"], trim=["#5b4310", "#b58c2a", "#ecd27a"],
         gem=["#4a0f2e", "#d03a86", "#ffc3e3"]),
    dict(name="netherite", studs=3, studc=["#5e0808", "#ff3a3a", "#ffd0d0"], embers=["#ff9b3d", "#ff5a1e"], anim=True, head=["#141113", "#332c30", "#4f454b", "#71656c", "#a3959d"],
         handle=["#160f0f", "#2f2020", "#463030", "#5e4242"], band=["#3d0c0c", "#6e1717", "#9c2424"], trim=["#6b4a0b", "#c9972a", "#ffe08a"],
         gem=["#4d0a0a", "#d42a2a", "#ffb3b3"]),
    dict(name="rubis", studs=4, studc=["#5e0808", "#ff3a3a", "#ffd0d0"], flames=["#fff3a0", "#ffb12e", "#ff5a1e", "#b31c10"], head=["#120d0f", "#2e2328", "#463a40", "#665760", "#9a8790"], edge=["#a81c10", "#ff4a2e", "#ffc2a6"],
         handle=["#160f0f", "#2f2020", "#463030", "#5e4242"], band=["#3d0c0c", "#6e1717", "#9c2424"], trim=["#6b4a0b", "#c9972a", "#ffe08a"],
         gem=["#5e0808", "#ff3030", "#ffd0d0"], anim=True),
    dict(name="legende", studs=4, flames=["#e0ffff", "#5ff0ff", "#1aa7c9", "#0d4f73"], head=["#08050f", "#191029", "#2c1f45", "#453568", "#75629f"], rune="#4ff0ff",
         handle=["#0c0a12", "#1d1828", "#2e2740", "#433a5a"], band=["#0d3a44", "#167585", "#2fc2d6"], trim=["#6b4a0b", "#c9972a", "#ffe08a"],
         gem=["#0b4552", "#2fe6ff", "#d6fbff"], anim=True),
    dict(name="mythique", studs=4, studc=["#3b0d63", "#c27bff", "#f6e8ff"], crystals=["#135a52", "#5ff5dc", "#e8fffb"], flames=["#ffe0ff", "#d77bff", "#9a2fe0", "#4a1373"], head=["#04100e", "#0b2b27", "#135a52", "#1f9b8a", "#93f7e3"], rune="#c070ff",
         handle=["#0f0a18", "#22163a", "#352457", "#4c3678"], band=["#3a1560", "#6a2aa8", "#a65ef0"], trim=["#3b6f7a", "#7fd6e0", "#e6ffff"],
         gem=["#3b0d63", "#b45cff", "#f0d9ff"], sparkle=["#d9a8ff", "#ffffff"], anim=True),
    dict(name="dieu", studs=5, flames=["#ffffff", "#fff1a0", "#ffc83a", "#e07b10"], glint=True, head=["#4d360a", "#b8902f", "#ecd27a", "#fff3cf", "#ffffff"], edge=["#b8902f", "#fff0b0", "#ffffff"],
         handle=["#3a2a12", "#8a6a34", "#c8a45e", "#efd8a2"], band=["#5e0a16", "#a8142c", "#e0304e"], trim=["#7a5a10", "#ffd44a", "#fffbe0"],
         gem=["#5e0a16", "#e01e3c", "#ffd6dc"], sparkle=["#ffe066", "#ffffff"], anim=True, halo=True),
]

# ---------------------------------------------------------------- géométrie
def blank():
    return np.zeros((N, N), dtype=bool)

def bez(p0, p1, p2, t):
    return ((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t**2*p2[0], (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t**2*p2[1])

def stroke(mask, pts_fn, r_fn, tparam=None, steps=300):
    for i in range(steps + 1):
        t = i / steps
        cx, cy = pts_fn(t); r = r_fn(t)
        for y in range(max(0, int(cy - r - 1)), min(N, int(cy + r + 2))):
            for x in range(max(0, int(cx - r - 1)), min(N, int(cx + r + 2))):
                if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
                    mask[y, x] = True
                    if tparam is not None and (tparam[y, x] < 0 or abs(t - 0.5) < abs(tparam[y, x] - 0.5)):
                        tparam[y, x] = t

def line(a, b):
    return lambda t: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

def poly(mask, pts):
    from matplotlib.path import Path
    p = Path(pts)
    for y in range(N):
        for x in range(N):
            if p.contains_point((x + 0.5, y + 0.5)):
                mask[y, x] = True

def near(mask, pts, d):
    m = blank()
    for y in range(N):
        for x in range(N):
            if mask[y, x]:
                for i in range(len(pts) - 1):
                    ax, ay = pts[i]; bx, by = pts[i + 1]
                    vx, vy = bx - ax, by - ay
                    tt = max(0, min(1, ((x + .5 - ax) * vx + (y + .5 - ay) * vy) / (vx * vx + vy * vy)))
                    if math.hypot(x + .5 - ax - tt * vx, y + .5 - ay - tt * vy) <= d:
                        m[y, x] = True
    return m

def handle_t(a, b):
    t = np.zeros((N, N))
    vx, vy = b[0] - a[0], b[1] - a[1]; L2 = vx * vx + vy * vy
    for y in range(N):
        for x in range(N):
            t[y, x] = ((x + .5 - a[0]) * vx + (y + .5 - a[1]) * vy) / L2
    return t

INLAY = {}

def shape(tool):
    head, edge, hand, gem_c, rod_line = blank(), blank(), blank(), None, blank()
    if tool == "pickaxe":
        H0, H1 = (4, 28), (22, 10)
        stroke(hand, line(H0, H1), lambda t: 1.35)
        A, Q, B = (6.5, 6.0), (31.0, 1.5), (26.0, 25.5)
        stroke(head, lambda t: bez(A, Q, B, t), lambda t: 0.75 + 2.05 * math.sin(math.pi * t) ** 0.8)
        edge = near(head, [A, (9, 5), (11, 4.5)], 2.6) | near(head, [B, (27, 22), (27.5, 19)], 2.6)
        INLAY[tool] = near(head, [bez(A, Q, B, t / 10) for t in range(3, 8)], 0.55)
        gem_c = (22, 10)
    elif tool == "axe":
        H0, H1 = (4, 28), (24, 8)
        stroke(hand, line(H0, H1), lambda t: 1.35)
        blade = [(19.5, 14.8), (16, 12.8), (12.5, 15.4), (8.8, 14.6), (6.4, 10.6), (6.8, 6.2), (9.6, 2.8), (13.8, 1.2),
                 (15.6, 4.9), (18.2, 7.0), (22.8, 7.0), (24.8, 9.4), (23.8, 11.8)]
        poly(head, blade)
        poly(head, [(23.4, 11.2), (26.8, 12.0), (28.2, 15.2), (25.0, 15.8), (22.4, 14.2)])
        edge = near(head, [(12.5, 15.4), (8.8, 14.6), (6.4, 10.6), (6.8, 6.2), (9.6, 2.8), (13.8, 1.2)], 1.7)
        INLAY[tool] = near(head, [(13.5, 12.5), (10.5, 10.5), (10.5, 6.5), (13.5, 4.5)], 0.5)
        gem_c = (20, 11)
    elif tool == "hoe":
        H0, H1 = (4, 28), (23, 9)
        stroke(hand, line(H0, H1), lambda t: 1.35)
        stroke(head, line((25, 7), (15.5, 3.5)), lambda t: 1.9)
        poly(head, [(18, 1.5), (13.5, 1), (8.5, 6.5), (7.5, 11.5), (10.5, 12), (13, 8.5), (17.5, 6)])
        edge = near(head, [(13.5, 1), (8.5, 6.5), (7.5, 11.5), (10.5, 12)], 1.6)
        INLAY[tool] = near(head, [(23.5, 6.5), (16.5, 3.8)], 0.5)
        gem_c = (21, 9)
    elif tool == "sword":
        H0, H1 = (4.5, 27.5), (10, 22)
        stroke(hand, line(H0, H1), lambda t: 1.3)
        stroke(head, line((10, 22), (28.5, 3.5)), lambda t: 2.5 - 1.9 * max(0, t - 0.55) / 0.45)
        guard = blank(); stroke(guard, line((5.5, 17.5), (14.5, 26.5)), lambda t: 1.35)
        hand_guard = guard & ~head
        head |= hand_guard
        edge = blank()
        INLAY[tool] = near(head, [(12.5, 19.5), (24, 8)], 0.5) & ~hand_guard
        gem_c = (10, 22)
        return head, edge, hand, gem_c, rod_line, hand_guard
    elif tool == "fishing_rod":
        P0, Q, P2 = (3.5, 28.5), (13, 10), (27, 4)
        stroke(hand, lambda t: bez(P0, Q, P2, t * 0.32), lambda t: 1.35)
        stroke(head, lambda t: bez(P0, Q, P2, 0.3 + t * 0.7), lambda t: 1.05 - 0.45 * t)
        stroke(head, lambda t: (9.2, 21.0), lambda t: 2.4)  # moulinet
        for yy in range(5, 25):
            rod_line[yy, 27] = True
        stroke(head, line((27, 25), (27, 27.5)), lambda t: 0.6)
        stroke(head, lambda t: bez((27, 27.5), (25, 29.5), (24.5, 26), t), lambda t: 0.6)
        gem_c = (9, 21)
    elif tool == "shears":
        for (cx, cy) in ((7.5, 21.5), (11.5, 26.0)):
            stroke(hand, lambda t, cx=cx, cy=cy: (cx + 4.2 * math.cos(2 * math.pi * t), cy + 4.2 * math.sin(2 * math.pi * t)), lambda t: 1.25, steps=200)
        stroke(head, line((10.5, 18.5), (27.5, 3.5)), lambda t: 2.0 - 1.3 * t)
        stroke(head, line((14.0, 22.0), (28.5, 7.5)), lambda t: 2.0 - 1.3 * t)
        edge = near(head, [(13, 16.5), (27.5, 3.5)], 0.7) | near(head, [(16, 20), (28.5, 7.5)], 0.7)
        INLAY[tool] = near(head, [(15, 15.5), (22, 9)], 0.45)
        gem_c = (14, 18)
    elif tool == "book":
        poly(hand, [(5, 6), (9, 4.5), (11, 28.5), (7, 29.5)])
        poly(head, [(9, 4.5), (26, 2.5), (28, 25.5), (11, 28.5)])
        poly(rod_line, [(26, 2.5), (28.5, 4), (30, 25), (28, 25.5)])
        INLAY[tool] = near(head, [(12, 7), (24, 5.5), (25.5, 23), (13, 25.5), (12, 7)], 0.5)
        gem_c = (18, 15)
    elif tool == "boots":
        poly(head, [(9, 3), (19, 3), (19, 17), (27, 19), (28.5, 22), (27.5, 25), (9, 25)])
        poly(hand, [(8.5, 25), (28.2, 25), (28, 28), (8.5, 28)])
        INLAY[tool] = near(head, [(9.5, 6), (18.5, 6)], 0.6)
        edge = near(head, [(19, 17), (27, 19), (28.5, 22)], 0.8)
        gem_c = (14, 13)
    elif tool == "bundle":
        poly(head, [(16 + 10.5 * math.cos(a / 40 * 2 * math.pi), 19.5 + 8.5 * math.sin(a / 40 * 2 * math.pi)) for a in range(40)])
        poly(head, [(12, 12.5), (20, 12.5), (21, 9), (11, 9)])
        poly(head, [(10, 8.5), (12.5, 2.5), (16, 6.5), (19.5, 2.5), (22, 8.5)])
        stroke(hand, line((10.5, 9.8), (21.5, 9.8)), lambda t: 1.1)
        INLAY[tool] = near(head, [(7, 21), (25, 21)], 0.5)
        gem_c = (16, 20)
    return head, edge, hand, gem_c, rod_line, None


def top_pixels(head):
    pts = []
    for x in range(N):
        for y in range(N):
            if head[y, x]:
                if y == 0 or not head[y - 1, x]:
                    pts.append((x, y))
    return pts

def pick_studs(head, edge, n, hbv):
    cand = [(x, y) for y in range(N) for x in range(N)
            if head[y, x] and not edge[y, x] and hbv[y, x] in (2, 3)
            and all(head[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if 0 <= y + dy < N and 0 <= x + dx < N)]
    cand.sort(key=lambda p: (p[0] * 37 + p[1] * 101) % 97)
    out = []
    for c in cand:
        if all(abs(c[0] - o[0]) + abs(c[1] - o[1]) >= 6 for o in out):
            out.append(c)
        if len(out) >= n:
            break
    return out

def hsh(*a):
    v = 2166136261
    for x in a:
        v = ((v ^ (x & 0xffffffff)) * 16777619) & 0xffffffff
    return v

# ---------------------------------------------------------------- rendu
def bevel(mask, ramp_idx):
    """1 = ombre, 2 = moyen, 3 = clair, 4 = reflet (lumière en haut à gauche)."""
    out = np.zeros((N, N), dtype=int)
    def m(y, x):
        return 0 <= y < N and 0 <= x < N and mask[y, x]
    for y in range(N):
        for x in range(N):
            if not mask[y, x]:
                continue
            tl = (not m(y - 1, x)) or (not m(y, x - 1))
            br = (not m(y + 1, x)) or (not m(y, x + 1))
            tl2 = (not m(y - 2, x)) or (not m(y, x - 2)) or (not m(y - 1, x - 1))
            if tl and not br:
                out[y, x] = 4
            elif br and not tl:
                out[y, x] = 1
            elif tl and br:
                out[y, x] = 3
            elif tl2:
                out[y, x] = 3
            else:
                out[y, x] = 2
    return out

def render(tool, tier, frame=0, nframes=1):
    T = TIERS[tier]
    res = shape(tool)
    head, edge, hand, gem_c, rod_line, guard = res
    img = np.zeros((N, N, 4))
    hp = [hx(c) for c in T["head"]]
    hd = [hx(c) for c in T["handle"]]
    ht = handle_t((4, 28), (24, 8))

    # manche
    hb = bevel(hand, 4)
    for y in range(N):
        for x in range(N):
            if not hand[y, x]:
                continue
            lvl = hb[y, x]
            col = hd[min(3, max(1, lvl))] if lvl < 4 else hd[3]
            if (x + 2 * y) % 5 == 0 and lvl == 2:
                col = hd[1]
            t = ht[y, x]
            if T.get("band") is not None and any(a <= t <= a + 0.06 for a in (0.12, 0.24, 0.36)):
                bp = [hx(c) for c in T["band"]]
                col = bp[2] if lvl >= 3 else (bp[0] if lvl == 1 else bp[1])
            if T.get("trim") is not None and (t < 0.05 or 0.78 <= t <= 0.84):
                tp = [hx(c) for c in T["trim"]]
                col = tp[2] if lvl >= 3 else (tp[0] if lvl == 1 else tp[1])
            img[y, x, :3] = col; img[y, x, 3] = 255

    # tête
    hbv = bevel(head, 5)
    for y in range(N):
        for x in range(N):
            if not head[y, x]:
                continue
            col = hp[hbv[y, x]]
            if guard is not None and guard[y, x] and T.get("trim") is not None:
                tp = [hx(c) for c in T["trim"]]
                col = tp[2] if hbv[y, x] >= 3 else (tp[0] if hbv[y, x] == 1 else tp[1])
            if edge[y, x]:
                ep = [hx(c) for c in T["edge"]] if T.get("edge") else [hp[2], hp[3], hp[4]]
                col = ep[2] if hbv[y, x] >= 3 else ep[1]
            inl = INLAY.get(tool)
            if inl is not None and inl[y, x] and not edge[y, x] and tier >= 3:
                ip = [hx(c) for c in (T["trim"] if tier >= 6 else T["gem"])]
                col = ip[1] if (x + y) % 2 else ip[2]
            elif inl is not None and inl[y, x] and not edge[y, x] and tier >= 1:
                col = hp[1]
            if hbv[y, x] == 2 and ((x * 13 + y * 7) % 9 == 0):
                col = col * 0.82 + hp[1] * 0.18
            if T.get("patina") and (x * 5 + y * 3) % 13 == 0 and hbv[y, x] == 2:
                col = hx(T["patina"])
            img[y, x, :3] = col; img[y, x, 3] = 255

    # fil de pêche
    for y in range(N):
        for x in range(N):
            if rod_line[y, x] and img[y, x, 3] == 0:
                if tool == "book":
                    img[y, x, :3] = hx("#f3ead2") if (x + y) % 3 else hx("#d9cdb0")
                else:
                    img[y, x, :3] = hx("#d8d8d8") if y % 2 else hx("#bdbdbd")
                img[y, x, 3] = 255

    # runes animées
    if T.get("rune"):
        rc = hx(T["rune"])
        pulse = 0.55 + 0.45 * math.sin(2 * math.pi * frame / nframes)
        for y in range(N):
            for x in range(N):
                if head[y, x] and hbv[y, x] == 2 and (x * 7 + y * 3) % 11 == 0 and not edge[y, x]:
                    img[y, x, :3] = img[y, x, :3] * (1 - pulse) + rc * pulse

    # gemme
    if T.get("gem") and gem_c:
        gp = [hx(c) for c in T["gem"]]
        cx, cy = gem_c
        big = tier >= 6
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                d = abs(dx) + abs(dy)
                if d <= (2 if big else 1):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < N and 0 <= y < N:
                        c = gp[0] if d == (2 if big else 1) else gp[1]
                        if (dx, dy) == (-1, -1) or (not big and (dx, dy) == (0, -1)):
                            c = gp[2]
                        if (dx, dy) == (0, 0):
                            c = gp[1]
                        img[y, x, :3] = c; img[y, x, 3] = 255

    # reflet animé qui balaie l'outil
    if T.get("anim"):
        pos = -6 + (N * 2 + 12) * frame / nframes
        for y in range(N):
            for x in range(N):
                if img[y, x, 3] > 0 and (head[y, x] or (guard is not None and guard[y, x])):
                    d = abs((x - y + 16) - pos)
                    if d < 2.2:
                        k = 0.55 * (1 - d / 2.2)
                        img[y, x, :3] = img[y, x, :3] * (1 - k) + 255 * k

    # contour
    filled = img[:, :, 3] > 0
    out = img.copy()
    for y in range(N):
        for x in range(N):
            if filled[y, x]:
                continue
            nb = [(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= y + dy < N and 0 <= x + dx < N and filled[y + dy, x + dx]]
            if nb:
                yy, xx = nb[0]
                src = "head" if head[yy, xx] else "handle"
                if rod_line[yy, xx] and not head[yy, xx] and not hand[yy, xx]:
                    continue
                c = hx(T["head"][0]) if src == "head" else hx(T["handle"][0])
                out[y, x, :3] = c; out[y, x, 3] = 255
    img = out

    # gemmes serties
    if T.get("studs"):
        gp = [hx(c) for c in T.get("studc", ["#14606e", "#7fe8ff", "#ffffff"])]
        for (sx, sy) in pick_studs(head, edge, min(3, T["studs"]), hbv):
            for dx, dy, c in ((0, 0, 2), (-1, 0, 1), (0, -1, 1), (1, 0, 0), (0, 1, 0)):
                img[sy + dy, sx + dx, :3] = gp[c]; img[sy + dy, sx + dx, 3] = 255
            if T.get("glint") and (hsh(sx, sy) + frame) % nframes == 0:
                img[sy, sx, :3] = hx("#ffffff")

    # éclats de cristal qui sortent de la tête
    if T.get("crystals"):
        cp = [hx(c) for c in T["crystals"]]
        tops = top_pixels(head)
        for (x, y) in tops[2::5][:4]:
            for k in range(1, 4):
                yy = y - 1 - k
                if yy < 0 or img[yy, x, 3] > 0:
                    break
                img[yy, x, :3] = cp[2] if k == 3 else cp[1]; img[yy, x, 3] = 255
                if x + 1 < N and k < 3 and img[yy, x + 1, 3] == 0:
                    img[yy, x + 1, :3] = cp[0]; img[yy, x + 1, 3] = 255

    # halo divin
    if T.get("halo"):
        filled = img[:, :, 3] > 0
        gold = hx("#fff07a")
        a = 38 + 28 * math.sin(2 * math.pi * frame / nframes)
        for y in range(N):
            for x in range(N):
                if filled[y, x]:
                    continue
                if any(0 <= y + dy < N and 0 <= x + dx < N and filled[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                    img[y, x, :3] = gold; img[y, x, 3] = a

    # flammes animées le long du bord supérieur
    if T.get("flames"):
        fp = [hx(c) for c in T["flames"]]
        for (x, y) in top_pixels(head):
            hgt = 1 + hsh(x, frame // 2) % 5
            if hsh(x * 3, frame) % 3 == 0:
                hgt = max(0, hgt - 2)
            for k in range(1, hgt + 1):
                yy = y - 1 - k
                if yy < 0 or img[yy, x, 3] > 120:
                    break
                ci = min(3, (k - 1) * 4 // max(1, hgt))
                img[yy, x, :3] = fp[ci]; img[yy, x, 3] = 255 if ci < 3 else 200
            if hgt >= 3 and hsh(x, frame, 7) % 4 == 0:
                yy = y - hgt - 3
                if 0 <= yy < N and img[yy, x, 3] < 100:
                    img[yy, x, :3] = fp[1]; img[yy, x, 3] = 230

    # braises
    if T.get("embers"):
        ep = [hx(c) for c in T["embers"]]
        tops = top_pixels(head)
        for i in range(3):
            bx, by = tops[(i * 7 + 3) % len(tops)]
            yy = by - 1 - ((frame + i * 4) % nframes) // 2
            xx = bx + (1 if (frame // 3 + i) % 2 else 0)
            if 0 <= yy < N and 0 <= xx < N and img[yy, xx, 3] == 0:
                img[yy, xx, :3] = ep[i % 2]; img[yy, xx, 3] = 255

    # étincelles
    if T.get("sparkle"):
        sp = [hx(c) for c in T["sparkle"]]
        spots = [(6, 22), (26, 27), (14, 13), (28, 11), (19, 25), (3, 15), (24, 2), (11, 29)]
        for i, (sx, sy) in enumerate(spots):
            ph = (frame + i * 3) % nframes
            if ph < 3:
                size = [1, 2, 1][ph]
                for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)][: 1 if size == 1 else 5]:
                    x, y = sx + dx, sy + dy
                    if 0 <= x < N and 0 <= y < N and img[y, x, 3] < 200:
                        img[y, x, :3] = sp[1] if (dx, dy) == (0, 0) else sp[0]; img[y, x, 3] = 255
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA")

JOBS = {"b": "axe", "m": "pickaxe", "f": "hoe", "c": "sword", "p": "fishing_rod",
        "e": "shears", "n": "book", "x": "boots", "t": "bundle"}

if __name__ == "__main__":
    sheet = Image.new("RGBA", (11 * 34 * 4, len(JOBS) * 34 * 4), (40, 44, 52, 255))
    for r, (j, tool) in enumerate(JOBS.items()):
        for tier in range(11):
            T = TIERS[tier]
            nf = 12 if T.get("anim") else 1
            frames = [render(tool, tier, f, nf) for f in range(nf)]
            strip = Image.new("RGBA", (N, N * nf))
            for i, fr in enumerate(frames):
                strip.paste(fr, (0, i * N))
            strip.save(os.path.join(OUT, f"{j}_{tier}.png"))
            if nf > 1:
                with open(os.path.join(OUT, f"{j}_{tier}.png.mcmeta"), "w") as fh:
                    json.dump({"animation": {"frametime": 2, "interpolate": False}}, fh)
            big = frames[0].resize((N * 4, N * 4), Image.NEAREST)
            sheet.alpha_composite(big, (tier * 34 * 4 + 4, r * 34 * 4 + 4))
    sheet.save(os.path.join(OUT, "_apercu.png"))
    print("ok")

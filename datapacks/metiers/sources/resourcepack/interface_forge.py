# Interface « Forge » : recolore l'interface vanilla (conteneurs, barre d'action, info-bulles, curseurs...) et l'ajoute
# au resource pack. Les dispositions vanilla sont conservées pixel pour pixel : seules les couleurs changent.
# Usage : python3 interface_forge.py <dossier assets/minecraft/textures/gui vanilla 26.x> metiers_resourcepack.zip
import io, os, sys, zipfile
from PIL import Image

VAN, ZIP = sys.argv[1], sys.argv[2]

# gris vanilla -> palette Forge (pierre chaude, filets dorés, cases sombres)
ANCRES = {0: (18, 14, 12), 33: (22, 18, 16), 55: (26, 21, 19), 85: (66, 55, 46), 139: (52, 46, 42),
          198: (124, 110, 96), 255: (212, 172, 92)}
def gris(v):
    if v in ANCRES: return ANCRES[v]
    ks = sorted(ANCRES); lo = max(k for k in ks if k <= v); hi = min(k for k in ks if k >= v)
    t = (v - lo) / (hi - lo); a, b = ANCRES[lo], ANCRES[hi]
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

def recolore(im, table=None):
    im = im.convert("RGBA"); px = im.load()
    for x in range(im.width):
        for y in range(im.height):
            r, g, b, a = px[x, y]
            if a == 0: continue
            if table and (r, g, b) in table: px[x, y] = table[(r, g, b)] + (a,)
            elif r == g == b and table is None: px[x, y] = gris(r) + (a,)
    return im

import random
def stylise(src):
    im = src.convert("RGBA"); W, H = im.size; o = im.load()
    out = im.copy(); px = out.load(); rnd = random.Random(11)
    def g(x, y):
        if 0 <= x < W and 0 <= y < H:
            r, gg, b, a = o[x, y]
            if a and r == gg == b: return r
        return None
    ys = [y for y in range(H) for x in range(W) if g(x, y) == 198]
    if not ys: return None
    for x in range(W):
        for y in range(H):
            r, gg, b, a = o[x, y]
            if not a or not (r == gg == b): continue
            v = r; n = rnd.randint(-4, 4)
            if v == 198:   # panneau : pierre chaude, appareillage de briques discret
                c = [112 + n, 98 + n, 84 + n]
                if y % 8 == 0 or (x + (8 if (y // 8) % 2 else 0)) % 16 == 0: c = [c[0] - 9, c[1] - 9, c[2] - 8]
                elif y % 8 == 1: c = [c[0] + 5, c[1] + 5, c[2] + 4]
                px[x, y] = tuple(max(0, min(255, k)) for k in c) + (a,)
            elif v == 255:
                voisin_case = any(g(x + dx, y + dy) == 139 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                px[x, y] = ((154, 118, 56) if voisin_case else (226, 184, 96)) + (a,)
            elif v == 85: px[x, y] = (62, 50, 40, a)
            elif v == 0: px[x, y] = (14, 11, 10, a)
            elif v == 139:   # case : creux sombre, ombre intérieure en haut à gauche
                c = (40 + n // 2, 35 + n // 2, 32 + n // 2)
                if g(x - 1, y) == 55 or g(x, y - 1) == 55: c = (26, 22, 20)
                px[x, y] = c + (a,)
            elif v == 55: px[x, y] = (16, 13, 12, a)
            elif v in (33,): px[x, y] = (20, 16, 14, a)
            else:
                t = v / 255; px[x, y] = (int(20 + 200 * t), int(16 + 160 * t), int(14 + 80 * t), a)
    # double filet intérieur le long du bord du panneau (seulement sur la pierre, jamais sur les cases)
    xs_ = [x for x in range(W) for y in range(H) if g(x, y) == 198]
    X0, X1, Y0, Y1 = min(xs_), max(xs_), min(ys), max(ys)
    for k, col in ((2, (58, 46, 36)), (3, (176, 136, 64))):
        for x in range(X0 + k, X1 - k + 1):
            for y in (Y0 + k, Y1 - k):
                if g(x, y) == 198: px[x, y] = col + (255,)
        for y in range(Y0 + k, Y1 - k + 1):
            for x in (X0 + k, X1 - k):
                if g(x, y) == 198: px[x, y] = col + (255,)
    # ornements dorés aux 4 coins du panneau
    xs = [x for x in range(W) for y in range(H) if g(x, y) == 198]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    motif = ["..#..", ".#O#.", "#OGO#", ".#O#.", "..#.."]
    for cx, cy in ((x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x0 + 3, y1 - 3), (x1 - 3, y1 - 3)):  # sur le filet
        for j, ligne in enumerate(motif):
            for i, ch in enumerate(ligne):
                X, Y = cx - 2 + i, cy - 2 + j
                if ch == "." or g(X, Y) not in (198, 255, 85): continue
                px[X, Y] = {"#": (70, 50, 22, 255), "O": (226, 184, 96, 255), "G": (255, 236, 160, 255)}[ch]
    return out

out = {}
def ajoute(rel, im):
    b = io.BytesIO(); im.save(b, "PNG"); out["assets/minecraft/textures/gui/" + rel] = b.getvalue()

# 1. conteneurs : textures pleines et sprites de cases
for base in ("container", "sprites/container", "sprites/recipe_book"):
    for dp, _, fs in os.walk(os.path.join(VAN, base)):
        for f in fs:
            p = os.path.join(dp, f); rel = os.path.relpath(p, VAN).replace(os.sep, "/")
            if f.endswith(".png"):
                riche = stylise(Image.open(p)) if base == "container" else None   # panneaux : pierre, filets et ornements
                ajoute(rel, riche if riche is not None else recolore(Image.open(p)))
            elif f.endswith(".mcmeta"): out["assets/minecraft/textures/gui/" + rel] = open(p, "rb").read()
ajoute("recipe_book.png", stylise(Image.open(os.path.join(VAN, "recipe_book.png"))) or recolore(Image.open(os.path.join(VAN, "recipe_book.png"))))

# 2. barre d'action
HOT = {(93, 93, 93): (96, 72, 40), (126, 126, 126): (214, 168, 80), (0, 0, 0): (18, 14, 12), (39, 37, 5): (26, 21, 18), (4, 4, 4): (10, 8, 7)}
for f in ("hotbar.png", "hotbar_offhand_left.png", "hotbar_offhand_right.png"):
    ajoute("sprites/hud/" + f, recolore(Image.open(os.path.join(VAN, "sprites/hud", f)), HOT))
SEL = {(213, 232, 208): (255, 214, 104), (161, 178, 157): (214, 160, 64), (95, 109, 92): (128, 88, 34)}
im = Image.open(os.path.join(VAN, "sprites/hud/hotbar_selection.png")).convert("RGBA"); px = im.load()
for x in range(im.width):
    for y in range(im.height):
        r, g, b, a = px[x, y]
        if a and (r, g, b) not in SEL and not (r < 10 and g < 10 and b < 10):   # nuances intermédiaires du cadre vert
            l = (r + g + b) // 3; px[x, y] = (min(255, l + 50), min(255, int(l * 0.85) + 20), int(l * 0.35)) + (a,)
ajoute("sprites/hud/hotbar_selection.png", recolore(im, SEL))

# 3. info-bulles : fond pierre sombre, cadre doré
TT = {(16, 0, 16): (24, 19, 17), (80, 0, 255): (214, 170, 88), (40, 0, 127): (120, 88, 40),
      (77, 0, 244): (206, 164, 84), (75, 0, 238): (200, 160, 82)}
for f in ("background.png", "frame.png"):
    im = recolore(Image.open(os.path.join(VAN, "sprites/tooltip", f)), TT)
    if f == "frame.png":
        px = im.load()
        for x in range(im.width):
            for y in range(im.height):
                r, g, b, a = px[x, y]
                if a:
                    k = max(r, g, b) / 255; px[x, y] = (int(40 + 190 * k), int(28 + 150 * k), int(10 + 70 * k), 210)
    ajoute("sprites/tooltip/" + f, im)
    out["assets/minecraft/textures/gui/sprites/tooltip/" + f + ".mcmeta"] = open(os.path.join(VAN, "sprites/tooltip", f + ".mcmeta"), "rb").read()

# 4. menus : curseurs, barres de défilement, cases à cocher, séparateurs
for f in sorted(os.listdir(os.path.join(VAN, "sprites/widget"))):
    if not f.endswith(".png") or f.startswith("button") or "realms" in f: continue
    if f.split(".")[0] in ("slider", "slider_highlighted", "slider_handle", "slider_handle_highlighted", "scroller", "scroller_background",
                           "checkbox", "checkbox_highlighted", "checkbox_selected", "checkbox_selected_highlighted", "slot_frame",
                           "page_forward", "page_forward_highlighted", "page_backward", "page_backward_highlighted", "tab", "tab_selected",
                           "tab_highlighted", "tab_selected_highlighted"):
        ajoute("sprites/widget/" + f, recolore(Image.open(os.path.join(VAN, "sprites/widget", f))))
        mm = os.path.join(VAN, "sprites/widget", f + ".mcmeta")
        if os.path.exists(mm): out["assets/minecraft/textures/gui/sprites/widget/" + f + ".mcmeta"] = open(mm, "rb").read()
for f in ("header_separator.png", "footer_separator.png", "inworld_header_separator.png", "inworld_footer_separator.png", "tab_header_background.png"):
    p = os.path.join(VAN, f)
    if os.path.exists(p):
        im = Image.open(p).convert("RGBA"); px = im.load()
        for x in range(im.width):
            for y in range(im.height):
                r, g, b, a = px[x, y]
                if a: l = (r + g + b) // 3; px[x, y] = (min(255, int(l * 1.0) + 30), min(255, int(l * 0.8) + 18), int(l * 0.4), a)
        ajoute(f, im)

# « Les Couillons » dans l'inventaire, à droite de la seconde main
G = {  # police 5 px de haut
 "L": ["#..", "#..", "#..", "#..", "###"], "e": ["...", "###", "#.#", "##.", "###"], "s": ["...", "###", "##.", "..#", "###"],
 "C": [".##", "#..", "#..", "#..", ".##"], "o": ["...", "###", "#.#", "#.#", "###"], "u": ["...", "#.#", "#.#", "#.#", "###"],
 "i": ["#", ".", "#", "#", "#"], "l": ["#", "#", "#", "#", "#"], "n": ["...", "##.", "#.#", "#.#", "#.#"], " ": ["..", "..", "..", "..", ".."]}
def ecrit(im, x, y, txt, col, ombre):
    px = im.load(); cx = x
    for ch in txt:
        g = G[ch]
        for j, ligne in enumerate(g):
            for i, c in enumerate(ligne):
                if c == "#":
                    px[cx + i + 1, y + j + 1] = ombre; px[cx + i, y + j] = col
        cx += len(g[0]) + 1
    return cx - x - 1
def largeur(txt): return sum(len(G[c][0]) + 1 for c in txt) - 1
def signe(im):
    # à droite de la seconde main (case 77,62), sous l'établi 2x2, hors du bouton du livre de recettes (104..124, 61..79)
    l1, l2 = "Les", "Couillons"; x0, x1 = 126, 172
    for t, y in ((l1, 63), (l2, 70)):
        ecrit(im, x0 + (x1 - x0 - largeur(t)) // 2, y, t, (232, 190, 100, 255), (52, 40, 28, 255))
    return im

_k = "assets/minecraft/textures/gui/container/inventory.png"
_im = signe(Image.open(io.BytesIO(out[_k])).convert("RGBA")); _b = io.BytesIO(); _im.save(_b, "PNG"); out[_k] = _b.getvalue()

zin = zipfile.ZipFile(ZIP); files = {n: zin.read(n) for n in zin.namelist()}; zin.close()
files.update(out)
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for n in sorted(files):
        zi = zipfile.ZipInfo(n, date_time=(2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED; z.writestr(zi, files[n])
open(ZIP, "wb").write(buf.getvalue())
print(len(out), "fichiers d'interface")

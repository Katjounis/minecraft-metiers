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

out = {}
def ajoute(rel, im):
    b = io.BytesIO(); im.save(b, "PNG"); out["assets/minecraft/textures/gui/" + rel] = b.getvalue()

# 1. conteneurs : textures pleines et sprites de cases
for base in ("container", "sprites/container", "sprites/recipe_book"):
    for dp, _, fs in os.walk(os.path.join(VAN, base)):
        for f in fs:
            p = os.path.join(dp, f); rel = os.path.relpath(p, VAN).replace(os.sep, "/")
            if f.endswith(".png"): ajoute(rel, recolore(Image.open(p)))
            elif f.endswith(".mcmeta"): out["assets/minecraft/textures/gui/" + rel] = open(p, "rb").read()
ajoute("recipe_book.png", recolore(Image.open(os.path.join(VAN, "recipe_book.png"))))

# 2. barre d'action
HOT = {(93, 93, 93): (88, 74, 60), (126, 126, 126): (176, 136, 58), (0, 0, 0): (18, 14, 12)}
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

zin = zipfile.ZipFile(ZIP); files = {n: zin.read(n) for n in zin.namelist()}; zin.close()
files.update(out)
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for n in sorted(files):
        zi = zipfile.ZipInfo(n, date_time=(2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED; z.writestr(zi, files[n])
open(ZIP, "wb").write(buf.getvalue())
print(len(out), "fichiers d'interface")

# Écran des progrès, notifications, effets et infobulles par métier dans la DA pierre et laiton.
# À lancer après interface_details.py et avant interface_animations.py.
#   - progrès : fenêtre (cadre de pierre claire, le titre du jeu y est écrit en gris foncé), onglets, cadres tâche,
#     objectif et défi en laiton (obtenus) ou en pierre (à faire), bandeaux de titre ;
#   - notifications : progrès et messages système en pierre sombre ; recettes et tutoriels en parchemin
#     (le jeu y écrit en violet foncé et en noir, il faut un fond clair) ;
#   - fonds des effets (HUD et inventaire) ;
#   - styles d'infobulle « metiers:<métier> » (cadre de la couleur du métier) et « metiers:legendaire » (cadre animé),
#     à poser sur les objets avec le composant tooltip_style ;
#   - son : clic en laiton sur les boutons (sons/clic_laiton.ogg, fabriqué par sons/sons_interface.py).
# Usage : python3 interface_extras.py metiers_resourcepack.zip <dossier gui/sprites vanilla>
import io, os, sys, json, math, zipfile
from PIL import Image

ZIP, VAN = sys.argv[1], sys.argv[2]
VGUI = os.path.dirname(VAN.rstrip("/\\"))  # .../textures/gui
GUI = "assets/minecraft/textures/gui/"
BAY = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
PIERRE = [(146, 130, 112), (132, 117, 100), (119, 105, 89), (106, 93, 79), (93, 81, 69), (80, 70, 60)]
PIERRE_CLAIRE = [(214, 202, 180), (202, 189, 166), (190, 176, 152), (176, 162, 138), (160, 146, 122)]
PIERRE_SOMBRE = [(70, 60, 52), (60, 52, 45), (52, 45, 39), (44, 38, 33), (36, 31, 27)]
PARCHEMIN = [(244, 234, 208), (236, 224, 194), (226, 212, 180), (212, 196, 162)]
LAITON = [(255, 236, 160), (236, 196, 104), (206, 160, 70), (166, 120, 44), (118, 82, 28)]
SOMBRE = (30, 22, 14)


def tram(r, v, x, y):
    i = int(v + (BAY[y % 4][x % 4] + .5) / 16)
    return r[max(0, min(len(r) - 1, i))]


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vanille(nom):
    return Image.open(os.path.join(VAN, nom)).convert("RGBA")


def rhabille(src, fond, biseau, contour=SOMBRE, garder_sombre=True):
    """Garde la silhouette d'un sprite vanilla : contour sombre, biseau (clair en haut à gauche, sombre en bas à droite)
    sur le premier pixel intérieur, fond tramé en dégradé vertical."""
    w, h = src.size
    sp = src.load()
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = out.load()
    opaque = lambda x, y: 0 <= x < w and 0 <= y < h and sp[x, y][3] > 0
    sombre = lambda x, y: opaque(x, y) and sum(sp[x, y][:3]) < 70
    ys = [y for y in range(h) for x in range(w) if opaque(x, y)]
    ya, yb = (min(ys), max(ys)) if ys else (0, h)
    for y in range(h):
        for x in range(w):
            if not opaque(x, y):
                continue
            a = sp[x, y][3]
            if garder_sombre and sombre(x, y):
                px[x, y] = contour + (a,)
                continue
            bord = lambda dx, dy: not opaque(x + dx, y + dy) or sombre(x + dx, y + dy)
            if bord(0, -1) or bord(-1, 0):
                c = biseau[0]
            elif bord(0, 1) or bord(1, 0):
                c = biseau[1]
            else:
                c = tram(fond, .3 + (y - ya) / max(1, yb - ya) * (len(fond) - 1.4), x, y)
            px[x, y] = c + (a,)
    return out


def boite(w, h, fond, biseau, coins=True, alpha=255):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for y in range(h):
        for x in range(w):
            d = min(x, y, w - 1 - x, h - 1 - y)
            if d == 0:
                if (x in (0, w - 1)) and (y in (0, h - 1)):
                    continue
                c = SOMBRE
            elif d == 1:
                c = biseau[0] if min(x, y) == 1 else biseau[1]
            else:
                c = tram(fond, .3 + y / h * (len(fond) - 1.4), x, y)
            px[x, y] = c + (alpha if d > 1 else 255,)
    if coins:
        for (cx, cy) in ((2, 2), (w - 4, 2), (2, h - 4), (w - 4, h - 4)):
            px[cx, cy] = LAITON[0] + (255,)
            px[cx + 1, cy] = LAITON[2] + (255,)
            px[cx, cy + 1] = LAITON[2] + (255,)
            px[cx + 1, cy + 1] = LAITON[4] + (255,)
    return im


# ------------------------------------------------------------------ infobulles par métier
METIERS = {"bucheron": (150, 98, 52), "fermier": (120, 170, 60), "mineur": (140, 150, 168), "chasseur": (196, 60, 52),
           "pecheur": (60, 140, 200), "eleveur": (214, 150, 90), "enchanteur": (164, 96, 220), "explorateur": (70, 170, 140),
           "marchand": (90, 190, 90), "batisseur": (200, 110, 70)}


def cadre_infobulle(col, eclat=0.0):
    im = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    px = im.load()
    a, b = 9, 90
    clair = mix(col, (255, 255, 255), .35 + .35 * eclat)
    fonce = mix(col, (0, 0, 0), .45)
    for i in range(a, b + 1):
        px[i, a] = clair + (255,)
        px[i, b] = fonce + (255,)
        px[a, i] = mix(clair, fonce, (i - a) / (b - a)) + (255,)
        px[b, i] = mix(clair, fonce, (i - a) / (b - a)) + (255,)
    for i in range(a + 2, b - 1):
        px[i, a + 1] = col + (110,)
    for (cx, cy) in ((a, a), (b - 1, a), (a, b - 1), (b - 1, b - 1)):
        for j in range(2):
            for i in range(2):
                px[cx + i, cy + j] = (LAITON[0] if (i, j) == (0, 0) else LAITON[2]) + (255,)
    return im


def fond_infobulle(teinte=None):
    im = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    px = im.load()
    base = [(34, 28, 24), (28, 23, 20), (22, 18, 16)]
    if teinte:
        base = [mix(c, teinte, .12) for c in base]
    for y in range(8, 92):
        for x in range(8, 92):
            if (x in (8, 91)) and (y in (8, 91)):
                continue
            px[x, y] = tram(base, .3 + (y - 8) / 83 * 2.2, x, y) + (242,)
    return im


# ------------------------------------------------------------------ écriture
zin = zipfile.ZipFile(ZIP)
fichiers = {n: zin.read(n) for n in zin.namelist()}
zin.close()
sortie = {}


def png(chemin, im):
    b = io.BytesIO()
    im.save(b, "PNG")
    sortie[chemin] = b.getvalue()


def meta(chemin, contenu):
    sortie[chemin + ".mcmeta"] = json.dumps(contenu, indent=2).encode()


def sprite(nom, im):
    png(GUI + "sprites/" + nom, im)
    src = os.path.join(VAN, nom + ".mcmeta")
    if os.path.exists(src):
        sortie[GUI + "sprites/" + nom + ".mcmeta"] = open(src, "rb").read()


B_LAITON = (LAITON[1], LAITON[3])
B_PIERRE = (PIERRE[0], PIERRE[4])

# progrès : fenêtre (pas un sprite)
fen = Image.open(os.path.join(VGUI, "advancements", "window.png")).convert("RGBA")
png(GUI + "advancements/window.png", rhabille(fen, PIERRE_CLAIRE, (LAITON[1], LAITON[3])))
for nom in sorted(os.listdir(os.path.join(VAN, "advancements"))):
    if not nom.endswith(".png"):
        continue
    v = vanille("advancements/" + nom)
    n = "advancements/" + nom
    if nom.startswith("tab_"):
        sel = "selected" in nom
        sprite(n, rhabille(v, PIERRE_CLAIRE if sel else PIERRE_CLAIRE[2:] + [(146, 132, 110)], (LAITON[1], LAITON[3]) if sel else (PIERRE_CLAIRE[0], PIERRE[3])))
    elif "_frame_" in nom:
        ok = "_obtained" in nom
        sprite(n, rhabille(v, [LAITON[1], LAITON[2], LAITON[3]] if ok else PIERRE[1:5], (LAITON[0], LAITON[4]) if ok else (PIERRE[0], PIERRE[5])))
    elif nom.startswith("box_obtained"):
        sprite(n, rhabille(v, [LAITON[2], LAITON[3], LAITON[3], LAITON[4]], (LAITON[1], LAITON[4])))
    elif nom.startswith(("box_unobtained", "title_box")):
        sprite(n, rhabille(v, PIERRE_SOMBRE, (PIERRE[3], (24, 20, 17))))

# notifications
sprite("toast/advancement.png", boite(160, 32, PIERRE_SOMBRE, B_LAITON))
sprite("toast/now_playing.png", boite(160, 32, PIERRE_SOMBRE, B_LAITON, coins=False))
sprite("toast/recipe.png", boite(160, 32, PARCHEMIN, B_LAITON))
sprite("toast/tutorial.png", boite(160, 32, PARCHEMIN, B_LAITON, coins=False))
sysv = vanille("toast/system.png")
sprite("toast/system.png", rhabille(sysv, PIERRE_SOMBRE, B_LAITON))

# effets
sprite("hud/effect_background.png", boite(24, 24, PIERRE_SOMBRE, B_LAITON, coins=False))
sprite("hud/effect_background_ambient.png", boite(24, 24, [mix(c, (60, 140, 160), .3) for c in PIERRE_SOMBRE], (LAITON[0], LAITON[2]), coins=False))
sprite("container/inventory/effect_background_large.png", boite(120, 32, PIERRE_SOMBRE, B_LAITON))
sprite("container/inventory/effect_background_small.png", boite(32, 32, PIERRE_SOMBRE, B_LAITON))

# infobulles par métier
NS9 = {"gui": {"scaling": {"type": "nine_slice", "width": 100, "height": 100, "border": 9}}}
NS10 = {"gui": {"scaling": {"type": "nine_slice", "width": 100, "height": 100, "border": 10, "stretch_inner": True}}}
TT = "assets/metiers/textures/gui/sprites/tooltip/"
for nom, col in METIERS.items():
    png(TT + nom + "_background.png", fond_infobulle(col))
    meta(TT + nom + "_background.png", NS9)
    png(TT + nom + "_frame.png", cadre_infobulle(col))
    meta(TT + nom + "_frame.png", NS10)
# légendaire : cadre doré qui scintille doucement
N = 24
images = [cadre_infobulle((236, 180, 60), .5 + .5 * math.sin(2 * math.pi * k / N)) for k in range(N)]
bande = Image.new("RGBA", (100, 100 * N), (0, 0, 0, 0))
for k, im in enumerate(images):
    bande.paste(im, (0, 100 * k))
png(TT + "legendaire_frame.png", bande)
meta(TT + "legendaire_frame.png", {**NS10, "animation": {"frametime": 2, "interpolate": True}})
png(TT + "legendaire_background.png", fond_infobulle((236, 180, 60)))
meta(TT + "legendaire_background.png", NS9)

# sons : clic en laiton sur tous les boutons (le .ogg est fabriqué par sons/sons_interface.py)
ICI = os.path.dirname(os.path.abspath(__file__))
sortie["assets/metiers/sounds/ui/clic_laiton.ogg"] = open(os.path.join(ICI, "sons", "clic_laiton.ogg"), "rb").read()
SJ = "assets/minecraft/sounds.json"
sons = json.loads(fichiers[SJ]) if SJ in fichiers else {}
sons["ui.button.click"] = {"replace": True, "sounds": [{"name": "metiers:ui/clic_laiton", "volume": 0.8}]}
sortie[SJ] = json.dumps(sons, indent=1, ensure_ascii=False).encode()

fichiers.update(sortie)
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for n in sorted(fichiers):
        zi = zipfile.ZipInfo(n, date_time=(2026, 1, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, fichiers[n])
open(ZIP, "wb").write(buf.getvalue())
print(len(sortie), "fichiers (progrès, notifications, effets, infobulles)")

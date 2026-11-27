"""Aperçus des skins pour le menu (27/11/2026) : une image par objet (armure + 9 outils) et par skin (base + 12), rendue
depuis les modèles du resource pack, posée en glyphe de police « metiers:apercu » : petit (boutons de la liste) et
grand (fiche du skin). Les menus ne savent pas afficher un modèle 3D en grand, une police si.

    python gen6.py      après gen5.py : génère, verse dans metiers_resourcepack.zip et affiche le SHA-1
Glyphe du skin i (0 = base) pour la cible n° c (ordre CIBLES) : grand U+E000 + 13 c + i, petit U+E200 + 13 c + i, moyen U+E400 + 13 c + i.
"""
import os, io, json, zipfile, hashlib
from PIL import Image
import rendu3d as R3

ICI = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.abspath(os.path.join(ICI, "..", "..", "..", ".."))
ZIP = os.path.join(DEPOT, "metiers_resourcepack.zip")
OUT = os.path.join(ICI, "..", "..", "build", "apercus")
CIBLES = ["a", "b", "f", "m", "c", "p", "e", "n", "x", "t"]          # même ordre que TGT dans ref_menu.py
SKINS = ["", "givre", "corail", "or_royal", "ossements", "magma", "ombre", "sakura", "celeste", "abysses", "sculk", "dragon", "eclipse"]
LEG = {"abysses", "sculk", "dragon", "eclipse"}
PAL = 6                                                               # palier montré pour les skins de couleur
GRAND, PETIT = 0xE000, 0xE200

class Pack(R3.Source):
    """Lit les modèles et textures dans le zip ; textures d'armure portée remises au carré pour le rendu."""
    def json(self, rid):
        if rid in MODS: return MODS[rid]
        return super().json(rid)
    def png(self, rid):
        if rid.startswith("x:"):
            sub, tag = rid[2:].split("/")
            im = Image.open(io.BytesIO(self.z.read(f"assets/metiers/textures/entity/equipment/{sub}/{tag}.png"))).convert("RGBA")
            sq = Image.new("RGBA", (im.width, im.width)); sq.paste(im, (0, 0))
            return sq
        return super().png(rid)
MODS = {}

def _box(frm, to, u, v, w, h, d, key, flip=False, k=4.0):
    f = lambda a, b, c, e: [a / k, b / k, c / k, e / k]
    faces = {"up": f(u + d, v, u + d + w, v + d), "down": f(u + d + w, v, u + d + 2 * w, v + d), "east": f(u, v + d, u + d, v + d + h),
             "north": f(u + d, v + d, u + d + w, v + d + h), "west": f(u + d + w, v + d, u + 2 * d + w, v + d + h),
             "south": f(u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h)}
    if flip:
        faces = {kk: [c[2], c[1], c[0], c[3]] for kk, c in faces.items()}; faces["east"], faces["west"] = faces["west"], faces["east"]
    return {"from": frm, "to": to, "faces": {kk: {"uv": uv, "texture": "#" + key} for kk, uv in faces.items()}}

def joueur(tag):
    """Corps du joueur habillé de l'armure portée (texture 128 x 64, mise en page standard)."""
    i, j = 0.6, 0.35
    e = [_box([4 - i, 12 - i, 6 - i], [12 + i, 24 + i, 10 + i], 16, 16, 8, 12, 4, "a"),
         _box([0 - i, 12 - i, 6 - i], [4 + i, 24 + i, 10 + i], 40, 16, 4, 12, 4, "a"),
         _box([12 - i, 12 - i, 6 - i], [16 + i, 24 + i, 10 + i], 40, 16, 4, 12, 4, "a", True),
         _box([4 - j, 12 - j, 6 - j], [12 + j, 15 + j, 10 + j], 16, 16, 8, 12, 4, "l"),
         _box([4 - j, 0 - j, 6 - j], [8 + j, 12 + j, 10 + j], 0, 16, 4, 12, 4, "l"),
         _box([8 - j, 0 - j, 6 - j], [12 + j, 12 + j, 10 + j], 0, 16, 4, 12, 4, "l", True),
         _box([4 - i, 0 - i, 6 - i], [8 + i, 4, 10 + i], 0, 16, 4, 12, 4, "a"),
         _box([8 - i, 0 - i, 6 - i], [12 + i, 4, 10 + i], 0, 16, 4, 12, 4, "a", True)]
    return {"textures": {"a": f"x:humanoid/{tag}", "l": f"x:humanoid_leggings/{tag}"}, "elements": e}

def modele(c, s):
    if c == "a":
        tag = f"guilde_{PAL}" + (f"_{s}" if s else "")
        MODS["apercu:joueur"] = joueur(tag)
        return "apercu:joueur", dict(roll=0, yaw=22, pitch=8)
    if s in LEG:
        rid = f"metiers:item/v2/lg_{s}_{c}"
    else:
        rid = f"metiers:item/v2/{c}_{PAL}" + (f"_{s}" if s else "")
    vue = dict(roll=0, yaw=-35, pitch=15) if c in "nt" else dict(roll=-45, yaw=-40, pitch=12)
    return rid, vue

def generer():
    src = Pack(ZIP)
    os.makedirs(f"{OUT}/assets/metiers/textures/font/apercu", exist_ok=True)
    os.makedirs(f"{OUT}/assets/metiers/font", exist_ok=True)
    prov = []
    for ci, c in enumerate(CIBLES):
        for i, s in enumerate(SKINS):
            rid, vue = modele(c, s)
            im = R3.render(src, rid, size=128, bg=(0, 0, 0, 0), **vue)
            nom = f"{c}_{s or 'base'}"
            im.save(f"{OUT}/assets/metiers/textures/font/apercu/{nom}.png", optimize=True)
            n = 13 * ci + i
            prov.append({"type": "bitmap", "file": f"metiers:font/apercu/{nom}.png", "height": 96, "ascent": 8, "chars": [chr(GRAND + n)]})
            prov.append({"type": "bitmap", "file": f"metiers:font/apercu/{nom}.png", "height": 14, "ascent": 11, "chars": [chr(PETIT + n)]})
            prov.append({"type": "bitmap", "file": f"metiers:font/apercu/{nom}.png", "height": 48, "ascent": 8, "chars": [chr(0xE400 + n)]})
    json.dump({"providers": prov}, open(f"{OUT}/assets/metiers/font/apercu.json", "w", encoding="utf-8"), ensure_ascii=False)
    return len(prov) // 2

def fusionner():
    with open(ZIP, "rb") as f:
        ancien = zipfile.ZipFile(io.BytesIO(f.read()))
    neufs = {}
    for dp, _, fs in os.walk(OUT):
        for fn in fs:
            full = os.path.join(dp, fn); neufs[os.path.relpath(full, OUT).replace(os.sep, "/")] = full
    sortie = io.BytesIO()
    with zipfile.ZipFile(sortie, "w", zipfile.ZIP_DEFLATED) as z:
        for info in ancien.infolist():
            if info.filename in neufs: continue
            z.writestr(info, ancien.read(info))
        for arc in sorted(neufs):
            zi = zipfile.ZipInfo(arc, date_time=(2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, open(neufs[arc], "rb").read())
    data = sortie.getvalue(); open(ZIP, "wb").write(data)
    print(f"{len(neufs)} fichiers versés ; SHA-1 : {hashlib.sha1(data).hexdigest()}")

if __name__ == "__main__":
    print(generer(), "aperçus")
    fusionner()

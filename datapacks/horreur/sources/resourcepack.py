"""Genere la partie Horreur du resource pack : build/horreur_rp/assets/horreur/...

Tout est dessine ici, pixel par pixel (aucun asset externe). La fusion dans metiers_resourcepack.zip
est faite par labo/outils/fusion_rp.py.
"""
import json, os, random, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from png import Image, hexa, nuance, TETE, CHAPEAU, CORPS, BRAS, JAMBE
from creatures import CREATURES

ICI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ICI, "..", "build", "horreur_rp")
A = os.path.join(OUT, "assets", "horreur")


def ecrire_json(chemin, obj):
    p = os.path.join(A, chemin)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))


def sauver(img, chemin):
    p = os.path.join(A, chemin)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)


# ======================================================================================
# Habits : textures « humanoid » 64x32 (tete, corps, bras, jambes)
# ======================================================================================
def peindre(img, faces, c, bruit=6, graine=1):
    for (x, y, w, h) in faces.values():
        img.rect(x, y, w, h, c, bruit, graine)


def face(img, cube, nom):
    """Origine (x, y) d'une face du patron."""
    return cube[nom][0], cube[nom][1]


def herobrine():
    im = Image(64, 32)
    peau, cheveux = hexa("#b5856a"), hexa("#3a281b")
    peindre(im, TETE, peau, 5, 1)
    x, y = face(im, TETE, "haut"); im.rect(x, y, 8, 8, cheveux, 6, 2)
    for n in ("droite", "gauche", "dos"):
        x, y = face(im, TETE, n); im.rect(x, y, 8, 3 if n != "dos" else 8, cheveux, 6, 3)
    x, y = face(im, TETE, "face")
    im.rect(x, y, 8, 2, cheveux, 6, 4)
    im.set(x, y + 2, cheveux); im.set(x + 7, y + 2, cheveux)
    # Les yeux : entierement blancs, legerement lumineux
    im.rect(x + 1, y + 4, 2, 1, "#ffffff"); im.rect(x + 5, y + 4, 2, 1, "#ffffff")
    im.rect(x + 1, y + 3, 2, 1, "#e8f4ff"); im.rect(x + 5, y + 3, 2, 1, "#e8f4ff")
    im.rect(x + 3, y + 5, 2, 1, nuance(peau, -35))
    im.rect(x + 2, y + 6, 4, 1, "#5a3020")
    chemise, jean = hexa("#00a8a8"), hexa("#3b3fa0")
    peindre(im, CORPS, chemise, 6, 5)
    peindre(im, BRAS, peau, 5, 6)
    for n in ("droite", "face", "gauche", "dos"):
        x, y = face(im, BRAS, n); im.rect(x, y, 4, 4, chemise, 6, 7)
    x, y = face(im, BRAS, "haut"); im.rect(x, y, 4, 4, chemise, 6, 8)
    peindre(im, JAMBE, jean, 6, 9)
    for n in ("droite", "face", "gauche", "dos"):
        x, y = face(im, JAMBE, n); im.rect(x, y + 10, 4, 2, "#6b6b6b", 6, 10)
    x, y = face(im, JAMBE, "bas"); im.rect(x, y, 4, 4, "#6b6b6b", 6, 11)
    return im


def nonne():
    im = Image(64, 32)
    noir, blanc, peau = hexa("#141414"), hexa("#e8e4d8"), hexa("#cfc9b0")
    peindre(im, TETE, noir, 4, 1)
    x, y = face(im, TETE, "face")
    im.rect(x + 1, y + 1, 6, 7, peau, 4, 2)
    im.rect(x + 1, y + 1, 6, 1, blanc)                       # bandeau de la coiffe
    im.rect(x + 1, y + 3, 2, 2, "#050505"); im.rect(x + 5, y + 3, 2, 2, "#050505")   # orbites
    im.set(x + 2, y + 4, "#f0d020"); im.set(x + 5, y + 4, "#f0d020")                 # yeux jaunes
    im.rect(x + 2, y + 6, 4, 2, "#0a0505")                   # bouche beante
    im.set(x + 2, y + 6, "#d8d0b8"); im.set(x + 5, y + 6, "#d8d0b8"); im.set(x + 3, y + 7, "#d8d0b8")
    for n in ("droite", "gauche"):
        x, y = face(im, TETE, n); im.rect(x + (5 if n == "droite" else 0), y + 1, 3, 1, blanc)
    peindre(im, CORPS, noir, 4, 3)
    x, y = face(im, CORPS, "face"); im.rect(x + 1, y, 6, 2, blanc, 3, 4); im.rect(x + 3, y + 2, 2, 3, "#c0b070")
    peindre(im, BRAS, noir, 4, 5)
    for n in ("droite", "face", "gauche", "dos"):
        x, y = face(im, BRAS, n); im.rect(x, y + 9, 4, 3, peau, 4, 6)
    x, y = face(im, BRAS, "bas"); im.rect(x, y, 4, 4, peau, 4, 7)
    peindre(im, JAMBE, noir, 4, 8)
    return im


def clown():
    im = Image(64, 32)
    blanc, rouge, gris = hexa("#f2efe8"), hexa("#d02020"), hexa("#a8a8b0")
    peindre(im, TETE, blanc, 3, 1)
    x, y = face(im, TETE, "haut"); im.rect(x, y, 2, 8, rouge, 10, 2); im.rect(x + 6, y, 2, 8, rouge, 10, 2)
    for n in ("droite", "gauche", "dos"):
        x, y = face(im, TETE, n); im.rect(x, y, 8, 5, rouge, 12, 3)
    x, y = face(im, TETE, "face")
    im.rect(x, y, 1, 4, rouge, 10, 4); im.rect(x + 7, y, 1, 4, rouge, 10, 4)
    im.rect(x + 1, y + 3, 2, 1, "#101010"); im.rect(x + 5, y + 3, 2, 1, "#101010")    # yeux
    im.rect(x + 2, y + 1, 1, 2, rouge); im.rect(x + 5, y + 1, 1, 2, rouge)            # traits au-dessus
    im.rect(x + 2, y + 4, 1, 1, rouge); im.rect(x + 5, y + 4, 1, 1, rouge)            # traits en dessous
    im.set(x + 3, y + 5, "#ff2020"); im.set(x + 4, y + 5, "#ff2020")                  # nez
    im.rect(x + 1, y + 6, 6, 1, rouge); im.set(x, y + 5, rouge); im.set(x + 7, y + 5, rouge)   # sourire
    im.rect(x + 2, y + 7, 4, 1, "#701010")
    peindre(im, CORPS, gris, 6, 5)
    x, y = face(im, CORPS, "face")
    im.rect(x, y, 8, 2, blanc, 4, 6)                         # collerette
    for j in (4, 7, 10):
        im.rect(x + 3, y + j, 2, 2, rouge)                   # pompons
    peindre(im, BRAS, gris, 6, 7)
    for n in ("droite", "face", "gauche", "dos"):
        x, y = face(im, BRAS, n); im.rect(x, y + 8, 4, 1, blanc); im.rect(x, y + 9, 4, 3, "#f8f8f8", 2, 8)
    peindre(im, JAMBE, gris, 6, 9)
    for n in ("droite", "face", "gauche", "dos"):
        x, y = face(im, JAMBE, n); im.rect(x, y + 10, 4, 2, "#e05010", 6, 10)
    x, y = face(im, JAMBE, "bas"); im.rect(x, y, 4, 4, "#e05010", 6, 11)
    return im


def pinhead():
    im = Image(64, 32)
    peau, cuir = hexa("#d6c8b8"), hexa("#1b1a1c")
    peindre(im, TETE, peau, 4, 1)
    # Quadrillage entaille + clous aux intersections, sur toute la tete
    for nom, (x, y, w, h) in TETE.items():
        if nom == "bas":
            continue
        for j in range(h):
            for i in range(w):
                if i % 2 == 1 or j % 2 == 1:
                    im.set(x + i, y + j, "#7a3a3a" if (i + j) % 3 else "#5a2828")
                if i % 2 == 1 and j % 2 == 1:
                    im.set(x + i, y + j, "#c8c8d0")
    x, y = face(im, TETE, "face")
    im.rect(x + 1, y + 4, 2, 1, "#0a0a0a"); im.rect(x + 5, y + 4, 2, 1, "#0a0a0a")
    im.rect(x + 2, y + 6, 4, 1, "#3a1818")
    peindre(im, CORPS, cuir, 5, 2)
    x, y = face(im, CORPS, "face")
    im.rect(x + 3, y, 2, 12, "#2c2a30"); im.rect(x, y + 6, 8, 1, "#3a3840")
    for j in range(1, 12, 3):
        im.set(x + 1, y + j, "#9090a0"); im.set(x + 6, y + j, "#9090a0")
    peindre(im, BRAS, cuir, 5, 3)
    for n in ("droite", "face", "gauche", "dos"):
        x, y = face(im, BRAS, n); im.rect(x, y + 10, 4, 2, peau, 4, 4)
    peindre(im, JAMBE, cuir, 5, 5)
    for n in ("face",):
        x, y = face(im, JAMBE, n); im.rect(x + 1, y, 1, 12, "#2c2a30")
    return im


HABITS = {"herobrine": herobrine, "nonne": nonne, "clown": clown, "pinhead": pinhead}


# ======================================================================================
# Modeles 3D (statues, ballon, trophees) : cubes + atlas genere
# ======================================================================================
class Modele:
    """Boites (from, to) dont chaque face est peinte par une fonction peintre(img, x, y, w, h, nom_face)."""
    COTES = ("north", "south", "east", "west", "up", "down")

    def __init__(self, nom):
        self.nom, self.boites = nom, []

    def boite(self, a, b, peintre):
        self.boites.append((a, b, peintre))

    def construire(self, larg=64):
        # Taille en pixels de chaque face (1 unite de modele = 1 pixel), rangement en etageres
        faces, x, y, hl = [], 0, 0, 0
        for i, (a, b, p) in enumerate(self.boites):
            dx, dy, dz = (max(1, round(b[k] - a[k])) for k in range(3))
            for cote, (w, h) in zip(self.COTES, ((dx, dy), (dx, dy), (dz, dy), (dz, dy), (dx, dz), (dx, dz))):
                if x + w > larg:
                    x, y, hl = 0, y + hl, 0
                faces.append((i, cote, x, y, w, h))
                x, hl = x + w, max(hl, h)
        haut = 16
        while haut < y + hl:
            haut *= 2
        img = Image(larg, haut)
        elems = [{"from": list(a), "to": list(b), "faces": {}} for a, b, _ in self.boites]
        for i, cote, x, y, w, h in faces:
            self.boites[i][2](img, x, y, w, h, cote)
            # Le jeu lit les UV sur 0..16 quelle que soit la taille de l'image (texture_size ne sert qu'a Blockbench)
            su, sv = 16 / larg, 16 / haut
            elems[i]["faces"][cote] = {"uv": [round(x * su, 4), round(y * sv, 4), round((x + w) * su, 4),
                                              round((y + h) * sv, 4)], "texture": "#t"}
        sauver(img, f"textures/item/{self.nom}.png")
        modele = {"texture_size": [larg, haut],
                  "textures": {"t": f"horreur:item/{self.nom}", "particle": f"horreur:item/{self.nom}"},
                  "elements": elems}
        return modele


def uni(c, bruit=6, graine=1):
    def p(img, x, y, w, h, cote):
        img.rect(x, y, w, h, c, bruit, graine + x + y)
    return p


def selon(defaut, **par_cote):
    """Peintre different selon la face (north = devant)."""
    def p(img, x, y, w, h, cote):
        (par_cote.get(cote) or defaut)(img, x, y, w, h, cote)
    return p


def slender():
    m = Modele("slender")
    costume, chemise, peau = hexa("#121214"), hexa("#e8e8e8"), hexa("#eceae6")

    def torse_devant(img, x, y, w, h, c):
        img.rect(x, y, w, h, costume, 4, 1)
        mid = w // 2
        img.rect(x + mid - 1, y, 2, h - 2, chemise, 3, 2)          # chemise
        img.rect(x + mid, y + 1, 1, h - 5, "#a01010")              # cravate
        img.set(x + mid - 1, y + 1, "#a01010")

    def tete(img, x, y, w, h, c):
        img.rect(x, y, w, h, peau, 4, 3)
        if c == "north":                                            # « visage » : a peine une ombre
            img.rect(x + 1, y + 2, 1, 1, nuance(peau, -14)); img.rect(x + w - 2, y + 2, 1, 1, nuance(peau, -14))

    def main_basse(img, x, y, w, h, c):
        img.rect(x, y, w, h, costume, 4, 4)
        if c not in ("up", "down"):
            img.rect(x, y + h - 3, w, 3, peau, 3, 5)                 # mains blanches
        if c == "down":
            img.rect(x, y, w, h, peau)

    def jambe(img, x, y, w, h, c):
        img.rect(x, y, w, h, costume, 4, 6)
        if c not in ("up", "down"):
            img.rect(x, y + h - 2, w, 2, "#050505")

    for x0 in (5.2, 8.8):
        m.boite((x0, -16, 7), (x0 + 2, 6, 9), jambe)
    m.boite((4.5, 6, 6.5), (11.5, 20, 9.5), selon(uni(costume, 4, 7), north=torse_devant))
    m.boite((2.6, 0, 7), (4.4, 20, 8.8), main_basse)
    m.boite((11.6, 0, 7), (13.4, 20, 8.8), main_basse)
    m.boite((7.2, 20, 7.2), (8.8, 22, 8.8), uni(peau, 3, 8))
    m.boite((5.5, 22, 5.5), (10.5, 29, 10.5), tete)
    return m


def siren():
    m = Modele("siren")
    chair, sombre = hexa("#8c7a62"), hexa("#4a3c2c")

    def corps(img, x, y, w, h, c):
        img.rect(x, y, w, h, chair, 14, 1)
        r = random.Random(x * 31 + y)
        for _ in range(w * h // 5):
            img.set(x + r.randrange(w), y + r.randrange(h), nuance(sombre, r.randint(-10, 10)))

    def torse(img, x, y, w, h, c):
        corps(img, x, y, w, h, c)
        if c in ("north", "south"):
            for j in range(1, h - 2, 2):
                img.rect(x + 1, y + j, w - 2, 1, "#3a2e22")            # cotes

    def hautparleur(img, x, y, w, h, c):
        img.rect(x, y, w, h, "#6a6a6e", 8, 2)
        if c in ("north", "south"):
            img.rect(x, y, w, h, "#1a1a1c", 3, 3)
            for j in range(0, h, 2):
                for i in range(j % 4 // 2, w, 2):
                    img.set(x + i, y + j, "#3c3c40")                 # grille

    for x0 in (5, 9):
        m.boite((x0, -16, 7), (x0 + 2, 10, 9), corps)
    m.boite((5, 10, 6.5), (11, 20, 9.5), torse)
    m.boite((3.4, -4, 7.2), (5, 20, 8.8), corps)
    m.boite((11, -4, 7.2), (12.6, 20, 8.8), corps)
    m.boite((7.2, 20, 7.2), (8.8, 28, 8.8), corps)
    m.boite((2, 27, 5.5), (7, 31, 10.5), hautparleur)
    m.boite((9, 25, 5.5), (14, 29, 10.5), hautparleur)
    m.boite((6.5, 27.5, 7.4), (9.5, 28.5, 8.6), uni("#3a3a3e", 4, 9))   # support
    return m


def ballon():
    m = Modele("ballon")
    m.boite((5, 22, 5), (11, 29, 11), selon(uni("#d81818", 10, 1), north=lambda i, x, y, w, h, c: (
        i.rect(x, y, w, h, "#d81818", 10, 1), i.rect(x + 1, y + 1, 1, 2, "#ff8080"))))
    m.boite((7.4, 21, 7.4), (8.6, 22, 8.6), uni("#a01010", 4, 2))
    m.boite((7.85, -8, 7.85), (8.15, 21, 8.15), uni("#e0e0e0", 6, 3))
    return m


def trophee(c):
    """Tete de la creature (cube 16) a poser sur sa tete ou a exposer, texturee comme le patron 8x8."""
    m = Modele("trophee_" + c["id"])
    if c["id"] in HABITS:
        src = HABITS[c["id"]]()
        cubes = {"north": "face", "south": "dos", "east": "gauche", "west": "droite", "up": "haut", "down": "bas"}

        def p(img, x, y, w, h, cote):
            sx, sy, sw, sh = TETE[cubes[cote]]
            for j in range(h):
                for i in range(w):
                    img.set(x + i, y + j, src.get(sx + i * sw // w, sy + j * sh // h))
        m.boite((0, 0, 0), (16, 16, 16), p)
    elif c["id"] == "slender":
        m.boite((2, 0, 2), (14, 16, 14), uni("#eceae6", 5, 4))
    else:  # siren : un haut-parleur
        m.boite((1, 3, 1), (15, 13, 15), selon(uni("#6a6a6e", 8, 2),
                north=lambda i, x, y, w, h, s: (i.rect(x, y, w, h, "#1a1a1c", 3, 3),
                                                [i.set(x + a, y + b, "#3c3c40") for b in range(0, h, 2) for a in range(0, w, 2)])))
    mod = m.construire(64)
    mod["parent"] = "minecraft:block/block"
    return mod


def generer():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    # Objet invisible (porte en tete par les statues pour ne pas bruler au soleil)
    ecrire_json("items/vide.json", {"model": {"type": "minecraft:empty"}})
    for c in CREATURES:
        k = c["id"]
        if c["apparence"] == "habit":
            sauver(HABITS[k](), f"textures/entity/equipment/humanoid/{k}.png")
            ecrire_json(f"equipment/{k}.json", {"layers": {"humanoid": [{"texture": f"horreur:{k}"}]}})
        else:
            ecrire_json(f"models/item/{k}.json", globals()[k]().construire(64))
            ecrire_json(f"items/{k}.json", {"model": {"type": "minecraft:model", "model": f"horreur:item/{k}"}})
        ecrire_json(f"models/item/trophee_{k}.json", trophee(c))
        ecrire_json(f"items/trophee_{k}.json", {"model": {"type": "minecraft:model", "model": f"horreur:item/trophee_{k}"}})
    ecrire_json("models/item/ballon.json", ballon().construire(32))
    ecrire_json("items/ballon.json", {"model": {"type": "minecraft:model", "model": "horreur:item/ballon"}})
    import sons
    sons.generer_rp(A)
    n = sum(len(f) for _, _, f in os.walk(OUT))
    print("resource pack horreur :", n, "fichiers dans", os.path.normpath(OUT))


if __name__ == "__main__":
    generer()

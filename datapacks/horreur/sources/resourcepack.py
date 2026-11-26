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


def dame():
    im = Image(64, 32)
    robe, peau, cheveux = hexa("#ecebf4"), hexa("#e4e6ee"), hexa("#d8d8e2")
    peindre(im, TETE, cheveux, 4, 1)
    x, y = face(im, TETE, "face")
    im.rect(x + 1, y + 2, 6, 6, peau, 3, 2)
    im.rect(x, y, 8, 2, cheveux, 4, 3); im.rect(x, y + 2, 1, 6, cheveux); im.rect(x + 7, y + 2, 1, 6, cheveux)
    im.rect(x + 2, y + 4, 1, 1, "#20202a"); im.rect(x + 5, y + 4, 1, 1, "#20202a")    # yeux vides
    im.rect(x + 3, y + 6, 2, 1, "#9a9aa8")
    peindre(im, CORPS, robe, 5, 4)
    x, y = face(im, CORPS, "face"); im.rect(x + 2, y, 4, 1, "#c8c8d8")
    peindre(im, BRAS, robe, 5, 5)
    for n in ("droite", "face", "gauche", "dos"):
        x, y = face(im, BRAS, n); im.rect(x, y + 10, 4, 2, peau, 3, 6)
    peindre(im, JAMBE, robe, 5, 7)                          # la robe descend jusqu'au sol
    for n in ("droite", "face", "gauche", "dos"):
        x, y = face(im, JAMBE, n); im.rect(x, y + 10, 4, 2, "#b8b8c8", 4, 8)
    return im


def loup():
    im = Image(64, 32)
    poil, sombre, peau = hexa("#6e6052"), hexa("#3e342a"), hexa("#8a7a68")
    peindre(im, TETE, poil, 14, 1)
    x, y = face(im, TETE, "face")
    im.rect(x + 2, y + 4, 4, 4, sombre, 8, 2)                # museau
    im.rect(x + 3, y + 4, 2, 1, "#101010")                   # truffe
    im.set(x + 1, y + 2, "#f0c020"); im.set(x + 6, y + 2, "#f0c020")   # yeux jaunes
    im.rect(x + 2, y + 7, 4, 1, "#e8e0d0")                   # crocs
    x, y = face(im, TETE, "haut"); im.rect(x, y, 2, 2, sombre); im.rect(x + 6, y, 2, 2, sombre)   # oreilles
    peindre(im, CORPS, poil, 14, 3)
    x, y = face(im, CORPS, "face"); im.rect(x + 1, y + 2, 6, 8, peau, 10, 4)
    peindre(im, BRAS, poil, 14, 5)
    for n in ("droite", "face", "gauche", "dos"):
        x, y = face(im, BRAS, n); im.rect(x, y + 10, 4, 2, sombre, 6, 6)
    peindre(im, JAMBE, poil, 14, 7)
    for n in ("droite", "face", "gauche", "dos"):
        x, y = face(im, JAMBE, n); im.rect(x, y + 10, 4, 2, sombre, 6, 8)
    return im


def rodeur():
    im = Image(64, 32)
    peau, ombre = hexa("#b8b2a8"), hexa("#7a746a")
    peindre(im, TETE, peau, 6, 1)
    x, y = face(im, TETE, "face")
    im.rect(x + 1, y + 2, 2, 3, "#050505"); im.rect(x + 5, y + 2, 2, 3, "#050505")   # orbites noires
    im.rect(x + 2, y + 6, 4, 2, "#1a0a0a"); im.set(x + 3, y + 6, "#d8d0c0"); im.set(x + 4, y + 7, "#d8d0c0")
    peindre(im, CORPS, peau, 6, 2)
    x, y = face(im, CORPS, "face")
    for j in range(2, 10, 2):
        im.rect(x + 1, y + j, 6, 1, ombre)                   # côtes
    peindre(im, BRAS, peau, 6, 3)
    for n in ("droite", "face", "gauche", "dos"):
        x, y = face(im, BRAS, n); im.rect(x, y + 10, 4, 2, "#2a2420")   # griffes
    peindre(im, JAMBE, ombre, 6, 4)
    return im


def croque():
    im = Image(64, 32)
    cape, ombre = hexa("#16101a"), hexa("#2a1420")
    peindre(im, TETE, cape, 5, 1)
    x, y = face(im, TETE, "face")
    im.rect(x + 1, y + 1, 6, 7, "#08060a")
    im.rect(x + 2, y + 3, 1, 1, "#f8f0f0"); im.rect(x + 5, y + 3, 1, 1, "#f8f0f0")   # yeux blancs
    im.rect(x + 2, y + 6, 4, 1, "#701020")                   # sourire rouge
    im.set(x + 1, y + 5, "#701020"); im.set(x + 6, y + 5, "#701020")
    peindre(im, CORPS, cape, 5, 2)
    x, y = face(im, CORPS, "face"); im.rect(x + 3, y, 2, 12, ombre)
    peindre(im, BRAS, cape, 5, 3)
    for n in ("droite", "face", "gauche", "dos"):
        x, y = face(im, BRAS, n); im.rect(x, y + 9, 4, 3, "#d8d0d0", 3, 4)   # longues mains pâles
    peindre(im, JAMBE, cape, 5, 5)
    return im


HABITS = {"herobrine": herobrine, "nonne": nonne, "clown": clown, "pinhead": pinhead,
          "dame": dame, "loup": loup, "rodeur": rodeur, "croque": croque}



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
    """Siren Head : corps décharné de 8 m, bras qui tombent sous les genoux, mât en guise de cou, deux sirènes."""
    m = Modele("siren")
    chair, sombre, os_ = hexa("#8a7356"), hexa("#3e3022"), hexa("#cbb896")

    def peau(img, x, y, w, h, c):
        img.rect(x, y, w, h, chair, 16, 1)
        r = random.Random(x * 31 + y * 7)
        for _ in range(w * h // 4):
            img.set(x + r.randrange(w), y + r.randrange(h), nuance(sombre, r.randint(-12, 12)))

    def torse(img, x, y, w, h, c):
        peau(img, x, y, w, h, c)
        if c in ("north", "south"):
            img.rect(x + w // 2, y, 1, h, nuance(sombre, -10))              # colonne / sternum
            for j in range(2, h - 3, 2):
                img.rect(x, y + j, w, 1, nuance(os_, -20))                 # côtes saillantes
                img.rect(x + w // 2, y + j, 1, 1, sombre)

    def main(img, x, y, w, h, c):
        img.rect(x, y, w, h, sombre, 10, 4)
        if c in ("north", "south", "east", "west"):
            for i in range(0, w, 2):
                img.rect(x + i, y + h - 2, 1, 2, "#1a120c")                # doigts

    def metal(img, x, y, w, h, c):
        img.rect(x, y, w, h, "#7a7a80", 10, 5)
        r = random.Random(x + y * 13)
        for _ in range(w * h // 5):
            img.set(x + r.randrange(w), y + r.randrange(h), "#7a4a2a")    # rouille

    def pavillon(img, x, y, w, h, c):
        metal(img, x, y, w, h, c)
        if c == "north":                                               # pavillon : bord, cône sombre, membrane
            img.rect(x, y, w, h, "#9a9aa0", 6, 6)
            img.rect(x + 1, y + 1, w - 2, h - 2, "#0c0c0e")
            img.rect(x + w // 2 - 1, y + h // 2 - 1, 2, 2, "#4a4a52")
            img.set(x + 1, y + 1, "#2a2a30"); img.set(x + w - 2, y + h - 2, "#2a2a30")

    # jambes maigres, bassin, torse décharné, épaules
    for x0 in (5.6, 8.8):
        m.boite((x0, -16, 7.2), (x0 + 1.6, 6, 8.8), peau)
    m.boite((5.4, 6, 6.8), (10.6, 8, 9.2), peau)
    m.boite((5.8, 8, 6.9), (10.2, 19, 9.1), torse)
    m.boite((3.4, 18, 7.0), (12.6, 19.6, 9.0), peau)
    # bras très longs, mains qui pendent sous les genoux
    for x0 in (2.3, 12.5):
        m.boite((x0, -5, 7.3), (x0 + 1.2, 19, 8.7), peau)
        m.boite((x0 - 0.3, -10, 7.0), (x0 + 1.5, -5, 9.0), main)
    # mât et traverse
    m.boite((7.4, 19.6, 7.4), (8.6, 27.6, 8.6), peau)
    m.boite((2.5, 27.4, 7.5), (13.5, 28.4, 8.5), metal)
    # deux sirènes : corps, cône, pavillon tourné vers l'avant
    for cx in (4.5, 11.5):
        m.boite((cx - 1.5, 28.4, 7), (cx + 1.5, 31.4, 10), metal)
        m.boite((cx - 2, 27.9, 5.5), (cx + 2, 31.9, 7), metal)
        m.boite((cx - 3, 26.6, 4.2), (cx + 3, 32, 5.5), pavillon)
    return m


def feu():
    m = Modele("feu")
    m.boite((5, 5, 5), (11, 11, 11), uni("#7fd8ff", 18, 1))
    m.boite((6.5, 11, 6.5), (9.5, 14, 9.5), uni("#c8f0ff", 10, 2))
    m.boite((7.2, 14, 7.2), (8.8, 16, 8.8), uni("#ffffff", 4, 3))
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
    elif c["id"] == "feu":
        m.boite((4, 4, 4), (12, 12, 12), uni("#7fd8ff", 18, 1))
    elif c["id"] == "slender":
        m.boite((2, 0, 2), (14, 16, 14), uni("#eceae6", 5, 4))
    else:  # siren : un haut-parleur
        m.boite((1, 3, 1), (15, 13, 15), selon(uni("#6a6a6e", 8, 2),
                north=lambda i, x, y, w, h, s: (i.rect(x, y, w, h, "#1a1a1c", 3, 3),
                                                [i.set(x + a, y + b, "#3c3c40") for b in range(0, h, 2) for a in range(0, w, 2)])))
    mod = m.construire(64)
    mod["parent"] = "minecraft:block/block"
    return mod


# ======================================================================================
# Habits en HD : le patron 64x32 est redessine en 128x64 (le jeu adapte les UV a la taille de l'image).
# Chaque pixel devient 4 sous-pixels : degrade de lumiere sur la face (haut eclaire, bas dans l'ombre), ombre
# portee sur le bord de chaque face, contours adoucis vers les details sombres (yeux, bouches, coutures) et grain fin.
# ======================================================================================
def _lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def hd(im):
    out = Image(im.w * 2, im.h * 2)
    r = random.Random(4242)
    for cube in (TETE, CHAPEAU, CORPS, BRAS, JAMBE):
        for nom, (x, y, w, h) in cube.items():
            for j in range(h):
                for i in range(w):
                    c = im.get(x + i, y + j)
                    if not c[3]:
                        continue
                    if nom == "haut":
                        g = 8
                    elif nom == "bas":
                        g = -14
                    else:
                        g = round(10 - 22 * (j + 0.5) / h)
                    for b in (0, 1):
                        for a in (0, 1):
                            d = g + r.randint(-3, 3)
                            sx, sy = 2 * i + a, 2 * j + b
                            if sx in (0, 2 * w - 1) or sy in (0, 2 * h - 1):
                                d -= 12
                            for (di, dj) in ((1 if a else -1, 0), (0, 1 if b else -1)):
                                ii, jj = i + di, j + dj
                                if 0 <= ii < w and 0 <= jj < h:
                                    v = im.get(x + ii, y + jj)
                                    if v[3]:
                                        ecart = _lum(v) - _lum(c)
                                        if ecart < -40:
                                            d -= 10
                                        elif ecart > 40:
                                            d += 6
                            out.set(2 * (x + i) + a, 2 * (y + j) + b, nuance(c, d))
    return out


def generer():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    # Objet invisible (porte en tete par les statues pour ne pas bruler au soleil)
    ecrire_json("items/vide.json", {"model": {"type": "minecraft:empty"}})
    for c in CREATURES:
        k = c["id"]
        if c["apparence"] == "habit":
            sauver(hd(HABITS[k]()), f"textures/entity/equipment/humanoid/{k}.png")
            ecrire_json(f"equipment/{k}.json", {"layers": {"humanoid": [{"texture": f"horreur:{k}"}]}})
        else:
            ecrire_json(f"models/item/{k}.json", globals()[k]().construire(64))
            ecrire_json(f"items/{k}.json", {"model": {"type": "minecraft:model", "model": f"horreur:item/{k}"}})
        ecrire_json(f"models/item/trophee_{k}.json", trophee(c))
        ecrire_json(f"items/trophee_{k}.json", {"model": {"type": "minecraft:model", "model": f"horreur:item/trophee_{k}"}})
    ecrire_json("models/item/ballon.json", ballon().construire(32))
    ecrire_json("items/ballon.json", {"model": {"type": "minecraft:model", "model": "horreur:item/ballon"}})
    # 26/11/2026 : trophees en tetes 3D (tetes.py) et squelettes animes des creatures (rigs.py)
    import tetes, rigs
    for k, pid in tetes.generer(A).items():
        m = json.load(open(os.path.join(A, "models", "item", "boss", pid + ".json"), encoding="utf-8"))
        ecrire_json(f"models/item/trophee_{k}.json", m)
    for k, f in rigs.CREATURES_RIG.items():
        R, _ = f()
        R.construire(A, "horreur")
    import sons
    sons.generer_rp(A)
    n = sum(len(f) for _, _, f in os.walk(OUT))
    print("resource pack horreur :", n, "fichiers dans", os.path.normpath(OUT))


if __name__ == "__main__":
    generer()

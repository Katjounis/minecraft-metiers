"""Moteur de squelettes animes pour item_display (vanilla, sans mod) : equivalent maison d'Animated Java.

Un boss est un arbre d'os (Os). Chaque os porte des boites (pixels, 16 px = 1 bloc) peintes par peintres.py.
Chaque os qui porte des boites devient UN item_display (deux si certaines boites brillent : la lueur a son propre
item_display en pleine lumiere). Le modele de l'os est un modele d'objet (elements) avec sa texture propre.

Reperes (« espace entite ») : +Y en haut, +Z devant (la ou regarde le boss), unites en pixels.
L'item_display retourne le modele de 180 degres autour de Y : on ecrit donc les elements retournes (x -> -x, z -> -z),
la face avant (+Z) devient la face « north » du modele. Les elements doivent rester dans -16..32 : un os trop grand
est dessine reduit (facteur k) et agrandi d'autant dans sa matrice.

Animation : une pose = {os: {"r": (rx, ry, rz) en degres ajoutes au repos, "t": (dx, dy, dz) px, "s": echelle}}.
Une animation = liste de (duree en ticks, pose). On calcule la matrice de chaque item_display pour chaque pose ;
le jeu interpole tout seul entre deux matrices (interpolation_duration).
"""
import math, os, random
from png import Image
from peintres import PEINTRES

# ------------------------------------------------------------------------------------------ matrices 4x4
def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def ident():
    return [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]


def trans(x, y, z):
    m = ident(); m[0][3], m[1][3], m[2][3] = x, y, z
    return m


def echelle(s):
    m = ident(); m[0][0] = m[1][1] = m[2][2] = s
    return m


def rot(rx, ry, rz):
    """Rotation en degres, ordre YXZ (comme les maquettes three.js) : R = Ry . Rx . Rz."""
    a, b, c = (math.radians(v) for v in (rx, ry, rz))
    Rx = [[1, 0, 0, 0], [0, math.cos(a), -math.sin(a), 0], [0, math.sin(a), math.cos(a), 0], [0, 0, 0, 1]]
    Ry = [[math.cos(b), 0, math.sin(b), 0], [0, 1, 0, 0], [-math.sin(b), 0, math.cos(b), 0], [0, 0, 0, 1]]
    Rz = [[math.cos(c), -math.sin(c), 0, 0], [math.sin(c), math.cos(c), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    return mul(mul(Ry, Rx), Rz)


def _f(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def quaternion(R):
    """Matrice de rotation 3x3 -> quaternion [x, y, z, w]."""
    tr = R[0][0] + R[1][1] + R[2][2]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        q = [(R[2][1] - R[1][2]) / s, (R[0][2] - R[2][0]) / s, (R[1][0] - R[0][1]) / s, 0.25 * s]
    elif R[0][0] > R[1][1] and R[0][0] > R[2][2]:
        s = math.sqrt(1.0 + R[0][0] - R[1][1] - R[2][2]) * 2
        q = [0.25 * s, (R[0][1] + R[1][0]) / s, (R[0][2] + R[2][0]) / s, (R[2][1] - R[1][2]) / s]
    elif R[1][1] > R[2][2]:
        s = math.sqrt(1.0 + R[1][1] - R[0][0] - R[2][2]) * 2
        q = [(R[0][1] + R[1][0]) / s, 0.25 * s, (R[1][2] + R[2][1]) / s, (R[0][2] - R[2][0]) / s]
    else:
        s = math.sqrt(1.0 + R[2][2] - R[0][0] - R[1][1]) * 2
        q = [(R[0][2] + R[2][0]) / s, (R[1][2] + R[2][1]) / s, 0.25 * s, (R[1][0] - R[0][1]) / s]
    n = math.sqrt(sum(v * v for v in q))
    q = [v / n for v in q]
    if q[3] < 0:
        q = [-v for v in q]
    return q


def snbt_matrice(m):
    """Matrice (rotation . echelle uniforme + translation) en transformation decomposee : le jeu interpole
    proprement la rotation (slerp), ce qui n'est pas garanti avec une matrice brute."""
    s = math.sqrt(m[0][0] ** 2 + m[1][0] ** 2 + m[2][0] ** 2)
    R = [[m[i][j] / s if s > 1e-9 else (1.0 if i == j else 0.0) for j in range(3)] for i in range(3)]
    q = quaternion(R)
    return ("{left_rotation:[" + ",".join(_f(v) + "f" for v in q) + "],right_rotation:[0f,0f,0f,1f],"
            "translation:[" + ",".join(_f(m[i][3]) + "f" for i in range(3)) + "],"
            "scale:[" + ",".join([_f(s) + "f"] * 3) + "]}")


# ------------------------------------------------------------------------------------------ squelette
class Os:
    def __init__(self, rig, nom, parent, p, r):
        self.rig, self.nom, self.parent = rig, nom, parent
        self.p, self.r = tuple(p), tuple(r)
        self.boites = []            # (centre, taille, peintre, options, faces)
        self.enfants = []
        if parent:
            parent.enfants.append(self)


class Rig:
    def __init__(self, nom, racine=(0, 0, 0)):
        self.nom = nom
        self.os = []
        self.racine = Os(self, "racine", None, racine, (0, 0, 0))
        self.os.append(self.racine)
        self._n = 0

    def art(self, parent, p, r=(0, 0, 0), nom=None):
        self._n += 1
        o = Os(self, nom or f"o{self._n}", parent or self.racine, p, r)
        self.os.append(o)
        return o

    def boite(self, parent, p, s, peintre, o=None, r=(0, 0, 0)):
        """Boite centree en p (px, repere de l'os), taille s, faces peintes ; r non nul -> petit os fixe."""
        o = dict(o or {})
        parent = parent or self.racine
        if any(r):
            parent = self.art(parent, p, r, nom=None)
            p = (0, 0, 0)
        parent.boites.append((tuple(p), tuple(s), peintre, o))
        return parent

    # -------------------------------------------------------------------------- entites (un ou deux par os)
    def pieces(self):
        """Liste des (os, lueur) qui portent des boites, dans un ordre stable."""
        out = []
        for o in self.os:
            for lueur in (False, True):
                if any(bool(b[3].get("lueur")) == lueur for b in o.boites):
                    out.append((o, lueur))
        return out

    def ident_piece(self, o, lueur):
        return f"{self.nom}_{o.nom}" + ("_l" if lueur else "")

    # -------------------------------------------------------------------------- modeles et textures
    def construire(self, dossier_assets, ns):
        """Ecrit models/item/<id>.json, items/<id>.json et textures/item/<id>.png. Renvoie {id: facteur k}."""
        import json
        facteurs = {}
        graine = 1
        for o, lueur in self.pieces():
            bx = [b for b in o.boites if bool(b[3].get("lueur")) == lueur]
            ext = max(max(abs(c[i]) + s[i] / 2 for i in range(3)) for c, s, _, _ in bx)
            k = 1.0
            while ext / k > 23.5:
                k *= 2
            pid = self.ident_piece(o, lueur)
            facteurs[pid] = k
            # faces : tailles en pixels de texture (on garde la densite d'origine, 1 texel par pixel)
            faces = []
            for i, (c, s, pt, opt) in enumerate(bx):
                dx, dy, dz = (max(1, round(v)) for v in s)
                # ordre three.js : +x, -x, +y, -y, +z, -z ; nom de face dans le modele (retourne de 180 deg)
                for idx, (nomf, (fw, fh)) in enumerate(zip(("west", "east", "up", "down", "north", "south"),
                                                         ((dz, dy), (dz, dy), (dx, dz), (dx, dz), (dx, dy), (dx, dy)))):
                    faces.append((i, idx, nomf, fw, fh))
            larg = 16
            while larg < max(f[3] for f in faces):
                larg *= 2
            larg = max(larg, 64)
            # rangement en etageres
            pos, x, y, hl = [], 0, 0, 0
            for f in sorted(faces, key=lambda f: -f[4]):
                if x + f[3] > larg:
                    x, y, hl = 0, y + hl, 0
                pos.append((f, x, y))
                x, hl = x + f[3], max(hl, f[4])
            haut = 16
            while haut < y + hl:
                haut *= 2
            img = Image(larg, haut)
            elems = []
            for c, s, _, _ in bx:
                a = [c[i] - s[i] / 2 for i in range(3)]
                b = [c[i] + s[i] / 2 for i in range(3)]
                frm = [8 - b[0] / k, 8 + a[1] / k, 8 - b[2] / k]
                to = [8 - a[0] / k, 8 + b[1] / k, 8 - a[2] / k]
                elems.append({"from": [round(v, 4) for v in frm], "to": [round(v, 4) for v in to], "faces": {}})
            su, sv = 16 / larg, 16 / haut
            for (i, idx, nomf, fw, fh), px, py in pos:
                c, s, pt, opt = bx[i]
                nom_p = (opt.get("faces") or [None] * 6)[idx] or pt
                opt_f = ((opt.get("optFaces") or [None] * 6)[idx]) or opt
                graine += 1
                PEINTRES[nom_p](img, px, py, fw, fh, random.Random(graine * 7919 + i), opt_f)
                if opt.get("cache") and idx in opt["cache"]:
                    continue
                elems[i]["faces"][nomf] = {"uv": [round(px * su, 4), round(py * sv, 4), round((px + fw) * su, 4),
                                                  round((py + fh) * sv, 4)], "texture": "#t"}
            chemin = os.path.join(dossier_assets, "textures", "item", "boss", pid + ".png")
            os.makedirs(os.path.dirname(chemin), exist_ok=True)
            img.save(chemin)
            modele = {"texture_size": [larg, haut], "textures": {"t": f"{ns}:item/boss/{pid}", "particle": f"{ns}:item/boss/{pid}"},
                      "elements": elems}
            for sous, obj in ((f"models/item/boss/{pid}.json", modele),
                              (f"items/{pid}.json", {"model": {"type": "minecraft:model", "model": f"{ns}:item/boss/{pid}"}})):
                p = os.path.join(dossier_assets, *sous.split("/"))
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(obj, f, separators=(",", ":"))
        self.facteurs = facteurs
        return facteurs

    # -------------------------------------------------------------------------- poses
    def matrices(self, pose=None):
        """{id piece: matrice 4x4 (blocs)} pour une pose."""
        pose = pose or {}
        glob = {}

        def visite(o, M):
            d = pose.get(o.nom, {})
            t = d.get("t", (0, 0, 0)); r = d.get("r", (0, 0, 0)); s = d.get("s", 1)
            Mo = mul(M, trans(*((o.p[i] + t[i]) / 16 for i in range(3))))
            Mo = mul(Mo, rot(*(o.r[i] + r[i] for i in range(3))))
            if s != 1:
                Mo = mul(Mo, echelle(s))
            glob[o.nom] = Mo
            for e in o.enfants:
                visite(e, Mo)

        visite(self.racine, ident())
        out = {}
        for o, lueur in self.pieces():
            pid = self.ident_piece(o, lueur)
            out[pid] = mul(glob[o.nom], echelle(self.facteurs[pid]))
        return out

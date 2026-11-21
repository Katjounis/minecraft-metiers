"""Mini-bibliotheque d'images en Python pur (pas de PIL) : dessin pixel par pixel et ecriture PNG."""
import random, struct, zlib


def hexa(c, a=255):
    """'#rrggbb' -> (r, g, b, a)."""
    c = c.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a)


def nuance(c, d):
    """Eclaircit (d > 0) ou assombrit (d < 0) une couleur RGBA."""
    return tuple(max(0, min(255, v + d)) for v in c[:3]) + (c[3],)


class Image:
    def __init__(self, w, h, fond=(0, 0, 0, 0)):
        self.w, self.h = w, h
        self.px = [list(fond) for _ in range(w * h)]

    def get(self, x, y):
        return tuple(self.px[y * self.w + x])

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            if isinstance(c, str):
                c = hexa(c)
            self.px[y * self.w + x] = list(c if len(c) == 4 else tuple(c) + (255,))

    def rect(self, x, y, w, h, c, bruit=0, graine=0):
        """Rectangle plein ; `bruit` ajoute un grain aleatoire (reproductible) a la couleur."""
        if isinstance(c, str):
            c = hexa(c)
        r = random.Random(graine * 7919 + x * 131 + y * 17)
        for j in range(y, y + h):
            for i in range(x, x + w):
                self.set(i, j, nuance(c, r.randint(-bruit, bruit)) if bruit else c)

    def coller(self, autre, x, y):
        for j in range(autre.h):
            for i in range(autre.w):
                p = autre.get(i, j)
                if p[3]:
                    self.set(x + i, y + j, p)

    def save(self, chemin):
        brut = b"".join(b"\x00" + bytes(v for p in self.px[y * self.w:(y + 1) * self.w] for v in p)
                        for y in range(self.h))

        def bloc(t, d):
            return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

        with open(chemin, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + bloc(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 6, 0, 0, 0))
                    + bloc(b"IDAT", zlib.compress(brut, 9)) + bloc(b"IEND", b""))


# --- Patron « humanoide » 64x32 (couche d'armure), coordonnees des faces de chaque cube ---
def faces_cube(u, v, w, h, d):
    """Rectangles (x, y, w, h) des 6 faces d'un cube de patron Minecraft place en (u, v)."""
    return {"haut": (u + d, v, w, d), "bas": (u + d + w, v, w, d),
            "droite": (u, v + d, d, h), "face": (u + d, v + d, w, h),
            "gauche": (u + d + w, v + d, d, h), "dos": (u + d + w + d, v + d, w, h)}


TETE = faces_cube(0, 0, 8, 8, 8)
CHAPEAU = faces_cube(32, 0, 8, 8, 8)
CORPS = faces_cube(16, 16, 8, 12, 4)
BRAS = faces_cube(40, 16, 4, 12, 4)
JAMBE = faces_cube(0, 16, 4, 12, 4)

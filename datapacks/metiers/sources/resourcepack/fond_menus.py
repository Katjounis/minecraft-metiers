# Fond des menus en jeu (24/11/2026) : remplace le voile sombre posé sur le monde flouté (dialogues, menu Échap,
# options) par un appareillage de pierre chaude presque opaque, dans la palette de l'interface Forge.
# Le jeu répète la texture tous les 32 px d'interface. Usage : python3 fond_menus.py ../../../../metiers_resourcepack.zip
import io, random, sys, zipfile
from PIL import Image

ZIP = sys.argv[1]
NOM = "assets/minecraft/textures/gui/inworld_menu_background.png"
rnd = random.Random(7)
im = Image.new("RGBA", (32, 32)); px = im.load()
for y in range(32):
    rang = y // 8
    for x in range(32):
        xx = (x + (8 if rang % 2 else 0)) % 32
        n = rnd.randint(-3, 3)
        if y % 8 == 0 or xx % 16 == 0:
            c = (17 + n // 2, 14 + n // 2, 13 + n // 2)            # joint
        elif y % 8 == 1 or xx % 16 == 1:
            c = (40 + n, 34 + n, 30 + n)                            # arête éclairée
        elif y % 8 == 7 or xx % 16 == 15:
            c = (24 + n, 20 + n, 18 + n)                            # arête dans l'ombre
        else:
            c = (31 + n, 26 + n, 23 + n)                            # face
        px[x, y] = c + (242,)
for x, y in ((16, 0), (8, 8), (0, 16), (24, 24)):                  # rivets dorés aux croisements
    px[x, y] = (150, 112, 50, 255)
buf = io.BytesIO(); im.save(buf, "PNG")
src = zipfile.ZipFile(ZIP); items = [(i, src.read(i.filename)) for i in src.infolist() if i.filename != NOM]; src.close()
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for info, data in items:
        z.writestr(info, data)
    zi = zipfile.ZipInfo(NOM, date_time=(2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(zi, buf.getvalue())
print("fond des menus posé :", NOM)

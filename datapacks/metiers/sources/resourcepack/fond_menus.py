# Décor des menus en jeu (24/11/2026) : à la place du monde flouté derrière les dialogues, le menu Échap et les options. Usage : python3 fond_menus.py ../../../../metiers_resourcepack.zip
import io, random, sys, zipfile
from PIL import Image

ZIP = sys.argv[1]
NOM = "assets/minecraft/textures/gui/inworld_menu_background.png"
# 24/11/2026 soir : le décor est un paysage de nuit animé calculé par un shader (decor_menu.fsh) qui remplace le flou
# (post_effect/blur.json) ; la texture de fond n'est plus qu'un voile très léger pour garder le texte lisible.
im = Image.new("RGBA", (32, 32), (6, 4, 10, 46))
import os, json
ICI = os.path.dirname(os.path.abspath(__file__))
# 24/11/2026 22 h 20 : DÉSACTIVÉ. En jeu, ouvrir un menu (touche G) chargeait ce post_effect, le chargement échouait,
# le client retirait tous les resource packs et se déconnectait. On garde le code pour le retester au labo, avec
# les logs du client, avant de le remettre (SHADER_DECOR = True).
SHADER_DECOR = False
FICHIERS_DECOR = {
    "assets/minecraft/shaders/post/decor_menu.fsh": open(os.path.join(ICI, "decor_menu.fsh"), encoding="utf-8").read().encode("utf-8"),
    "assets/minecraft/post_effect/blur.json": json.dumps({
        "targets": {"swap": {}},
        "passes": [
            {"vertex_shader": "minecraft:core/screenquad", "fragment_shader": "minecraft:post/decor_menu",
             "inputs": [{"sampler_name": "In", "target": "minecraft:main", "bilinear": True}], "output": "swap"},
            {"vertex_shader": "minecraft:core/screenquad", "fragment_shader": "minecraft:post/blit",
             "inputs": [{"sampler_name": "In", "target": "swap"}],
             "uniforms": {"BlitConfig": [{"name": "ColorModulate", "type": "vec4", "value": [1.0, 1.0, 1.0, 1.0]}]},
             "output": "minecraft:main"}]}, indent=1).encode("utf-8")}
FICHIERS = dict(FICHIERS_DECOR) if SHADER_DECOR else {}
buf = io.BytesIO(); im.save(buf, "PNG")
FICHIERS[NOM] = None
src = zipfile.ZipFile(ZIP); items = [(i, src.read(i.filename)) for i in src.infolist() if i.filename not in FICHIERS and i.filename not in FICHIERS_DECOR]; src.close()
FICHIERS[NOM] = buf.getvalue()
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for info, data in items:
        z.writestr(info, data)
    for nom, data in FICHIERS.items():
        zi = zipfile.ZipInfo(nom, date_time=(2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, data)
print("décor des menus posé :", ", ".join(FICHIERS))

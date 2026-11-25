# -*- coding: utf-8 -*-
# Encadré du solde en haut à gauche. Exécuté par datapack.py après dessiner_rp() (partage w, F, NS, RP, ECU...).
#
# Le vanilla n'a aucun affichage en haut à gauche : on se sert du « title » (aucun pack du serveur ne l'utilise),
# écrit dans la police commerce:hud, et le shader de texte du resource pack le déplace dans le coin, à l'échelle 1.
#   - les glyphes ont une opacité de 9 % : sans le shader (shaderpack qui le remplace), le jeu les jette (seuil 10 %)
#     et rien ne s'affiche au milieu de l'écran ; avec le shader, l'opacité est remultipliée par 11.
#   - le shader reconnaît le texte à ses deux couleurs marqueurs (#FEFEFD cadre et pièce, #FEC841 chiffres).
#   - largeur du texte constante (chiffres à chasse fixe, zéros de tête remplacés par un blanc de même largeur) :
#     le shader peut retrouver la position de chaque glyphe sans connaître le texte.
from PIL import Image, ImageDraw

HUD = os.path.join(HERE, "..", "build", "commerce_rp", "assets")
ALPHA = 11                                     # facteur rendu par le shader
low = lambda a: 0 if a == 0 else max(1, min(23, round(a / ALPHA)))
asc_img = Image.open(os.path.join(HERE, "textures_recette", "ascii.png")).convert("RGBA")


def cell(ch):
    o = ord(ch)
    return asc_img.crop(((o % 16) * 8, (o // 16) * 8, (o % 16) * 8 + 8, (o // 16) * 8 + 8))


def baisse(im):
    """Opacité divisée par ALPHA (le shader la remultiplie)."""
    px = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, low(a))
    return im


def largeur(im):
    px = im.load()
    cols = [x for x in range(im.size[0]) for y in range(im.size[1]) if px[x, y][3]]
    return (max(cols) + 1) if cols else 0


# ---------------------------------------------------------------- glyphes
os.makedirs(os.path.join(RP, "textures", "font"), exist_ok=True)
CH = {"box": "", "neg": "", "coin": "", "sp": "", "blank": "", "comma": "", "thin": ""}
DIG = [chr(0xE210 + d) for d in range(10)]
# chiffres à chasse fixe : un pixel quasi transparent en colonne 4 force la largeur à 5 (avance 6)
digits = Image.new("RGBA", (8 * 11, 8), (0, 0, 0, 0))
for d in range(10):
    c = baisse(cell(str(d)).copy())
    c.putpixel((4, 7), (255, 255, 255, 1)) if c.getpixel((4, 7))[3] == 0 else None
    digits.paste(c, (8 * d, 0))
digits.putpixel((8 * 10 + 4, 7), (255, 255, 255, 1))               # blanc de chiffre
digits.save(os.path.join(RP, "textures", "font", "hud_chiffres.png"))
virg = baisse(cell(",").copy())
virg.save(os.path.join(RP, "textures", "font", "hud_virgule.png"))
W_COMMA = largeur(virg) + 1
piece = Image.open(os.path.join(RP, "textures", "font", "ecu.png")).convert("RGBA").copy()
baisse(piece).save(os.path.join(RP, "textures", "font", "hud_ecu.png"))
W_COIN = 9
CONTENU = W_COIN + 3 + 8 * 6 + 2 * 2 + W_COMMA + 12            # pièce, espace, 8 chiffres, 2 séparateurs, virgule, centimes
PAD = 5
BOXW = PAD + CONTENU + 4
HUD_W = PAD + CONTENU                                          # largeur totale du texte (le cadre est compensé)
# cadre : bord doré, fond sombre à 80 %, filet intérieur (texture 2x pour un trait fin)
S4 = 2                                         # 2x : un glyphe ne doit pas dépasser 256 px de texture
bx = Image.new("RGBA", (BOXW * S4, 14 * S4), (0, 0, 0, 0))
dd = ImageDraw.Draw(bx)
dd.rounded_rectangle([0, 0, BOXW * S4 - 1, 14 * S4 - 1], radius=3, fill=(18, 14, 12, 205), outline=(226, 184, 96, 255), width=2)
dd.rounded_rectangle([2, 2, BOXW * S4 - 3, 14 * S4 - 3], radius=2, outline=(90, 66, 30, 255), width=1)
baisse(bx).save(os.path.join(RP, "textures", "font", "hud_cadre.png"))
os.makedirs(os.path.join(RP, "font"), exist_ok=True)
json.dump({"providers": [
    {"type": "bitmap", "file": "commerce:font/hud_cadre.png", "height": 14, "ascent": 11, "chars": [CH["box"]]},
    {"type": "bitmap", "file": "commerce:font/hud_ecu.png", "height": 8, "ascent": 7, "chars": [CH["coin"]]},
    {"type": "bitmap", "file": "commerce:font/hud_chiffres.png", "height": 8, "ascent": 7, "chars": ["".join(DIG) + CH["blank"]]},
    {"type": "bitmap", "file": "commerce:font/hud_virgule.png", "height": 8, "ascent": 7, "chars": [CH["comma"]]},
    {"type": "space", "advances": {CH["neg"]: -(BOXW + 1) + PAD, CH["sp"]: 3, CH["thin"]: 2}}]},
    open(os.path.join(RP, "font", "hud.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- shader de texte (26.3) avec le déplacement
SH = os.path.join(HERE, "shaders_26.3")
vsh = open(os.path.join(SH, "text.vsh"), encoding="utf-8").read()
fsh = open(os.path.join(SH, "text.fsh"), encoding="utf-8").read()
A_V = "layout(location = 3) out vec2 texCoord0;\n"
assert A_V in vsh and vsh.rstrip().endswith("}")
vsh = vsh.replace(A_V, A_V + "layout(location = 4) out float hudMark;\n")
vsh = vsh.rstrip()[:-1] + f'''
    // Commerce : encadré du solde. Le « title » (échelle 4, centré) est ramené en haut à gauche, échelle 1.
    hudMark = 0.0;
    ivec3 hudRgb = ivec3(round(Color.rgb * 255.0));
    if (hudRgb == ivec3(254, 254, 253) || hudRgb == ivec3(254, 200, 65)) {{
        hudMark = 1.0;
        float sw = abs(2.0 / ProjMat[0][0]);
        float sh = abs(2.0 / ProjMat[1][1]);
        vec4 clip = gl_Position;
        float sx = (clip.x / clip.w + 1.0) * 0.5 * sw;
        float sy = (1.0 - clip.y / clip.w) * 0.5 * sh;
        float lx = (sx - sw * 0.5) / 4.0 + {HUD_W / 2:.1f};
        float ly = (sy - sh * 0.5) / 4.0 + 10.0;
        float nx = 4.0 + lx;
        float ny = 8.0 + ly;
        gl_Position = vec4(nx / sw * 2.0 - 1.0, 1.0 - ny / sh * 2.0, clip.z / clip.w, 1.0);
    }}
}}
'''
A_F = "layout(location = 3) in vec2 texCoord0;\n"
B_F = "    if (color.a < 0.1) {"
assert A_F in fsh and B_F in fsh
fsh = fsh.replace(A_F, A_F + "layout(location = 4) in float hudMark;\n")
fsh = fsh.replace(B_F, "    if (hudMark > 0.5) {\n        color.a = min(color.a * %.1f, 1.0);\n    }\n\n" % ALPHA + B_F)
# 25/11/2026 : shader de texte DÉBRANCHÉ. Le remplacer touche tout le texte du jeu, et en 26.3 les panneaux et les
# noms (comptoirs) s'affichaient en lettres hachées. Le solde passe dans la barre latérale (tableau/on), le seul
# affichage permanent de vanilla. HUD_SHADER = True rebrancherait l'encadré en haut à gauche.
HUD_SHADER = False
if HUD_SHADER:
    SHD = os.path.join(HUD, "minecraft", "shaders", "core")
    os.makedirs(SHD, exist_ok=True)
    open(os.path.join(SHD, "text.vsh"), "w", encoding="utf-8").write(vsh)
    open(os.path.join(SHD, "text.fsh"), "w", encoding="utf-8").write(fsh)

# ---------------------------------------------------------------- commandes
H_ = F + "hud/"
w(H_ + "load.mcfunction", [
    "scoreboard objectives add c.hudv dummy", "scoreboard objectives add c.hudr dummy",
    "scoreboard objectives add c.quit minecraft.custom:minecraft.leave_game",
    # l'ancien tableau de la barre latérale est retiré une fois (tableau/on le remet si besoin)
    f"execute unless score #hud c.g matches 1.. run function {NS}:tableau/off",
    "execute unless score #hud c.g matches 2.. run scoreboard players set #hud c.g 1"] + ([] if HUD_SHADER else [
    # sans shader : l'encadré est retiré une fois et la barre latérale du solde est remise
    "execute unless score #hud c.g matches 2 run title @a clear",
    f"execute unless score #hud c.g matches 2 run function {NS}:tableau/on",
    "scoreboard players set #hud c.g 2"]))
HJ = [
    "execute if score @s c.quit matches 1.. run scoreboard players set @s c.hudv -1",
    "scoreboard players set @s c.quit 0",
    "scoreboard players operation #hv c.t = @s c.ecus", "scoreboard players operation #hv c.t *= #100 c.g",
    "scoreboard players operation #hv c.t += @s c.cts",
    "scoreboard players add @s c.hudr 1",
    "execute if score @s c.hudr matches 1200.. run scoreboard players set @s c.hudv -1",
    f"execute unless score #hv c.t = @s c.hudv run function {NS}:hud/maj"]
w(H_ + "joueur.mcfunction", HJ if HUD_SHADER else ["return 0"])
HM = ["scoreboard players operation @s c.hudv = #hv c.t", "scoreboard players set @s c.hudr 0",
      "scoreboard players operation #n c.t = @s c.ecus",
      "execute if score #n c.t matches 100000000.. run scoreboard players set #n c.t 99999999"]
for k in range(8):
    HM += [f"scoreboard players operation #d c.t = #n c.t"]
    if k:
        HM += [f"scoreboard players set #p c.t {10 ** k}", "scoreboard players operation #d c.t /= #p c.t"]
    HM += ["scoreboard players operation #d c.t %= #10 c.g"]
    HM += [f'execute if score #d c.t matches {d} run data modify storage {NS}:h d{k} set value "{DIG[d]}"' for d in range(10)]
    if k:
        HM.append(f'execute if score #n c.t matches ..{10 ** k - 1} run data modify storage {NS}:h d{k} set value "{CH["blank"]}"')
HM += ["scoreboard players operation #d c.t = @s c.cts", "scoreboard players operation #d c.t /= #10 c.g"]
HM += [f'execute if score #d c.t matches {d} run data modify storage {NS}:h c1 set value "{DIG[d]}"' for d in range(10)]
HM += ["scoreboard players operation #d c.t = @s c.cts", "scoreboard players operation #d c.t %= #10 c.g"]
HM += [f'execute if score #d c.t matches {d} run data modify storage {NS}:h c0 set value "{DIG[d]}"' for d in range(10)]
HM += ["title @s times 0 2000000000 0", f"function {NS}:hud/titre with storage {NS}:h"]
w(H_ + "maj.mcfunction", HM)
TXT = (f'[{{text:"",font:"commerce:hud",color:"#FEFEFD",shadow_color:0,extra:['
       f'{{text:"{CH["box"]}{CH["neg"]}{CH["coin"]}{CH["sp"]}"}},'
       f'{{text:"$(d7)$(d6){CH["thin"]}$(d5)$(d4)$(d3){CH["thin"]}$(d2)$(d1)$(d0){CH["comma"]}$(c1)$(c0)",color:"#FEC841"}}]}}]')
w(H_ + "titre.mcfunction", "$title @s title " + TXT)
w(H_ + "cacher.mcfunction", ["title @s clear", "scoreboard players set @s c.hudv -2"])

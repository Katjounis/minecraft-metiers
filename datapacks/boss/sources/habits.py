"""Habille les 5 boss du pack Metiers (sans toucher a leur IA ni a leurs attaques).

  - Colosse des Metiers (zombie) : armure de forge peinte (plaques sombres, rivets, rune rouge), casque a cornes,
    marteau de forge geant a la place de la hache ;
  - Liche du givre (stray) : robe de givre peinte, couronne de pics de glace, baton a cristal a la place de l'arc ;
  - Reine arachnide (araignee) : couronne d'epines et grappe d'yeux qui brillent, dos herisse de cristaux et de cocons ;
  - Brasier ancestral (blaze) : anneau de plaques d'obsidienne veinees de lave qui tourne autour de lui, couronne de feu ;
  - Creeper geant : fagot de TNT sangle dans le dos, noyau de cristal vert qui brille sur la tete.
Les parures sont des item_display passagers du boss (orientation recopiee chaque tick) ; les armures sont des
assets d'equipement (couche humanoid) ; casques et armes sont des modeles d'objet poses dans les emplacements du mob.
"""
import math, os, random
from rig import Rig, snbt_matrice, mul, rot, trans, echelle
from png import Image, TETE, CORPS, BRAS, JAMBE
import peintres as P

# ------------------------------------------------------------------------------------------------ modeles
def marteau():
    R = Rig("marteau_forge")
    o = R.racine
    R.boite(o, (0, -3, 0), (2, 26, 2), "bois_mort", {"pal": ["#5a3a22", "#4a2e1a", "#6b4529"]})
    R.boite(o, (0, -12, 0), (2.6, 4, 2.6), "uni", {"c": "#c89a3a"})
    R.boite(o, (0, 12, 0), (13, 7, 7), "metal")
    for x in (-4, 4):
        R.boite(o, (x, 12, 0), (1.5, 7.6, 7.6), "uni", {"c": "#c89a3a"})
    R.boite(o, (0, 17, 0), (3, 3, 3), "metal")
    R.boite(o, (7.5, 12, 0), (2, 5, 5), "metal")
    return R


def casque():
    R = Rig("casque_forge")
    o = R.racine
    R.boite(o, (0, 0, 0), (17, 15, 17), "metal", {"pal": ["#3a3c42", "#46484f", "#2e3035"], "rivet": "#c89a3a"})
    for y in (-1, 2):
        R.boite(o, (0, y, 8.7), (12, 1, 0.6), "uni", {"c": "#0a0a0c", "bruit": 2})
    R.boite(o, (0, 4.5, 8.8), (3, 3, 0.6), "uni", {"c": "#c02010"})
    R.boite(o, (0, 9, 0), (3, 3, 15), "uni", {"c": "#c89a3a"})
    for s in (-1, 1):
        R.boite(o, (s * 11, 4, 0), (6, 3, 3), "uni", {"c": "#d8cfb5"})
        R.boite(o, (s * 14, 8.5, 0), (3, 7, 3), "uni", {"c": "#e8e0c8"})
        R.boite(o, (s * 14, 13, 0), (2, 3, 2), "uni", {"c": "#f4eedc"})
    return R


def couronne_givre():
    R = Rig("couronne_givre")
    o = R.racine
    for z in (-8.5, 8.5):
        R.boite(o, (0, 9, z), (18, 2, 1), "cristal")
    for x in (-8.5, 8.5):
        R.boite(o, (x, 9, 0), (1, 2, 18), "cristal")
    for (x, z, h) in ((0, 8.5, 10), (-5, 8.5, 6), (5, 8.5, 6), (-8.5, 0, 7), (8.5, 0, 7), (0, -8.5, 6), (-8.5, -8.5, 5), (8.5, -8.5, 5), (-8.5, 8.5, 5), (8.5, 8.5, 5)):
        R.boite(o, (x, 10 + h / 2, z), (2, h, 2), "cristal")
    R.boite(o, (0, 10, 9.2), (3, 3, 0.6), "uni", {"c": "#3ad0ff"})
    return R


def baton_givre():
    R = Rig("baton_givre")
    o = R.racine
    R.boite(o, (0, -4, 0), (1.6, 28, 1.6), "bois_mort", {"pal": ["#2a3442", "#1e2632", "#36404e"]})
    R.boite(o, (0, 12, 0), (4, 7, 4), "cristal")
    for s in (-1, 1):
        R.boite(o, (s * 2.5, 10, 0), (1.5, 4, 1.5), "cristal")
    R.boite(o, (0, 8, 0), (3, 1.5, 3), "uni", {"c": "#a8c8e0"})
    return R


def reine_couronne():
    R = Rig("reine_couronne")
    o = R.racine
    for k in range(8):
        a = k / 8 * math.tau
        h = 9 if k % 2 == 0 else 6
        R.boite(o, (math.cos(a) * 9, h / 2, math.sin(a) * 9), (2.5, h, 2.5), "pierre", {"pal": ["#2a1a3a", "#3a2050", "#1a3a1a", "#244a24"], "fissures": .2})
    R.boite(o, (0, 0, 0), (20, 2, 20), "pierre", {"pal": ["#1a2a1a", "#2a3a22", "#203020"], "fissures": .2})
    for (x, y) in ((-5, 2), (-2, 4), (2, 4), (5, 2), (-3, 0.5), (3, 0.5)):
        R.boite(o, (x, y, 10.5), (2, 2, 1), "uni", {"c": "#ff2a2a", "lueur": True, "bruit": 30})
    return R


def reine_dos():
    R = Rig("reine_dos")
    o = R.racine
    for k, z in enumerate((-12, -6, 0, 6)):
        h = 10 + (k % 2) * 4
        R.boite(o, (0, h / 2, z), (3, h, 3), "cristal", {"pal": ["#5a2a8a", "#7a3ab0", "#3a1a5a", "#9a5ad0"]})
        s = 1 if k % 2 else -1
        R.boite(o, (s * 5, h * .3, z), (2, h * .6, 2), "cristal", {"pal": ["#5a2a8a", "#7a3ab0", "#3a1a5a"]})
    for (x, z) in ((-7, -9), (6, -4), (-5, 4)):
        R.boite(o, (x, 2.5, z), (5, 5, 6), "toile", {"pal": ["#e8e2d0", "#d8d0bc", "#f0ece0", "#c8c0aa"]})
    for z in (-10, -2, 6):
        R.boite(o, (0, 0.5, z), (1, 1, 5), "uni", {"c": "#7dff5a", "lueur": True, "bruit": 30})
    return R


def brasier_anneau():
    R = Rig("brasier_anneau")
    o = R.racine
    for k in range(8):
        a = k / 8 * math.tau
        x, z = math.cos(a) * 16, math.sin(a) * 16
        R.boite(o, (x, (k % 2) * 3, z), (6, 11, 6), "pierre", {"pal": ["#140a1e", "#1d1030", "#0d0614", "#26143c"], "fissures": .6})
        R.boite(o, (x, (k % 2) * 3, z), (6.4, 2, 6.4), "lave", {"lueur": True})
    return R


def brasier_couronne():
    R = Rig("brasier_couronne")
    o = R.racine
    for k in range(10):
        a = k / 10 * math.tau
        h = 8 if k % 2 == 0 else 5
        R.boite(o, (math.cos(a) * 6, h / 2, math.sin(a) * 6), (2, h, 2), "lave", {"lueur": True})
    return R


def creeper_tnt():
    R = Rig("creeper_tnt")
    o = R.racine
    for x in (-5, 0, 5):
        R.boite(o, (x, 0, 0), (4.6, 14, 4.6), "tnt")
        R.boite(o, (x, 7.5, 0), (0.8, 2, 0.8), "uni", {"c": "#3a3a3a"})
    for y in (-4, 4):
        R.boite(o, (0, y, 0), (15.5, 1.6, 5.2), "uni", {"c": "#3a2a1a"})
    return R


def creeper_noyau():
    R = Rig("creeper_noyau")
    o = R.racine
    R.boite(o, (0, 0, 0), (10, 2, 10), "pierre", {"pal": ["#2f4a2a", "#3a5a30", "#24381f"], "fissures": .3})
    R.boite(o, (0, 5, 0), (5, 9, 5), "cristal", {"pal": ["#5aff5a", "#9aff7a", "#3ad03a", "#c8ffb0"], "lueur": True})
    for s in (-1, 1):
        R.boite(o, (s * 3.5, 3, 1), (2.5, 5, 2.5), "cristal", {"pal": ["#5aff5a", "#3ad03a"], "lueur": True})
    return R


OBJETS = [marteau(), casque(), couronne_givre(), baton_givre()]          # portes par le mob (main, tete)
PARURES = {"reine": [reine_couronne(), reine_dos()], "brasier": [brasier_anneau(), brasier_couronne()],
           "creeper": [creeper_tnt(), creeper_noyau()]}

# position des parures (blocs) par rapport au point d'attache du passager, echelle
POSE = {"reine_couronne": (0, -0.9, 1.55, 3.2), "reine_dos": (0, -0.55, -1.2, 3.0),
        "brasier_anneau": (0, -2.4, 0, 2.6), "brasier_couronne": (0, -0.15, 0, 2.6),
        "creeper_tnt": (0, -2.9, -1.05, 3.0), "creeper_noyau": (0, -0.05, 0, 3.0)}

DISPLAY_MAIN = {"thirdperson_righthand": {"rotation": [0, -90, 55], "translation": [0, 5, 1.5], "scale": [0.95, 0.95, 0.95]},
                "thirdperson_lefthand": {"rotation": [0, 90, -55], "translation": [0, 5, 1.5], "scale": [0.95, 0.95, 0.95]},
                "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1, 3, 1], "scale": [0.7, 0.7, 0.7]},
                "gui": {"rotation": [30, 225, 0], "scale": [0.6, 0.6, 0.6]}}
DISPLAY_TETE = {"head": {"translation": [0, 0, 0], "scale": [1, 1, 1]}, "gui": {"rotation": [30, 225, 0], "scale": [0.6, 0.6, 0.6]}}


def armure(nom, base, opt, detail):
    img = Image(64, 32)
    for cube in (TETE, CORPS, BRAS, JAMBE):
        for (x, y, w, h) in cube.values():
            P.PEINTRES[base](img, x, y, w, h, random.Random(x * 7 + y), opt)
    detail(img)
    return img


def det_colosse(img):
    fx, fy, fw, fh = CORPS["face"]
    for y in range(fy + 3, fy + 8):                               # rune de forge rouge sur le torse
        img.set(fx + 3, y, P.hexa("#d0301a")); img.set(fx + 4, y, P.hexa("#d0301a"))
    for x in range(fx + 1, fx + 7):
        img.set(x, fy + 5, P.hexa("#ff6a2a"))
    for x in range(fx, fx + fw):                                  # ceinture de cuir et boucle d'or
        img.set(x, fy + 9, P.hexa("#3a2414")); img.set(x, fy + 10, P.hexa("#4a2e1a"))
    img.set(fx + 3, fy + 9, P.hexa("#e0b040")); img.set(fx + 4, fy + 10, P.hexa("#e0b040"))
    for c in (BRAS, JAMBE):
        x, y, w, h = c["face"]
        for xx in range(x, x + w):
            img.set(xx, y, P.hexa("#c89a3a")); img.set(xx, y + h - 1, P.hexa("#c89a3a"))


def det_liche(img):
    fx, fy, fw, fh = CORPS["face"]
    for y in range(fy, fy + fh):                                  # pan de robe et runes de givre
        img.set(fx + 3, y, P.hexa("#1a2a44")); img.set(fx + 4, y, P.hexa("#1a2a44"))
    for (dx, dy) in ((1, 3), (6, 3), (2, 7), (5, 7), (3, 10), (4, 10)):
        img.set(fx + dx, fy + dy, P.hexa("#7ad8ff"))
    for x in range(fx - 4, fx + fw + 4):                          # col de fourrure blanche
        if 0 <= x < 64:
            img.set(x, fy, P.hexa("#f0f4f8")); img.set(x, fy + 1, P.hexa("#d8e0e8"))


def ecrire_rp(RP, ns, ecrire_json):
    for R in OBJETS + [r for l in PARURES.values() for r in l]:
        R.construire(RP, ns)
    for R, disp in ((OBJETS[0], DISPLAY_MAIN), (OBJETS[1], DISPLAY_TETE), (OBJETS[2], DISPLAY_TETE), (OBJETS[3], DISPLAY_MAIN)):
        pid = R.ident_piece(R.racine, False)
        p = os.path.join(RP, "models", "item", "boss", pid + ".json")
        import json
        m = json.load(open(p, encoding="utf-8"))
        m["display"] = disp
        json.dump(m, open(p, "w", encoding="utf-8"), separators=(",", ":"))
    for nom, base, opt, det in (("colosse", "metal", {"pal": ["#3a3c42", "#46484f", "#2e3035", "#52555d"], "rivet": "#c89a3a"}, det_colosse),
                                ("liche", "haillons", {"pal": ["#22324e", "#2a3c5c", "#1a2840", "#30466a"]}, det_liche)):
        img = armure(nom, base, opt, det)
        for couche in ("humanoid", "humanoid_leggings"):
            d = os.path.join(RP, "textures", "entity", "equipment", couche)
            os.makedirs(d, exist_ok=True)
            img.save(os.path.join(d, nom + ".png"))
        ecrire_json(f"equipment/{nom}.json", {"layers": {"humanoid": [{"texture": f"{ns}:{nom}"}],
                                                         "humanoid_leggings": [{"texture": f"{ns}:{nom}"}]}})


def ecrire_dp(fn, NS):
    def piece(slot, asset):
        return (f'minecraft:paper[minecraft:equippable={{slot:"{slot}",asset_id:"{NS}:{asset}"}},'
                f'minecraft:item_model="{NS}:vide"]')
    tenue = {
        "zombie": [f"item replace entity @s armor.{s} with {piece(s, 'colosse')}" for s in ("chest", "legs", "feet")]
                  + [f'item replace entity @s armor.head with minecraft:paper[minecraft:item_model="{NS}:casque_forge_racine"]',
                     f'item replace entity @s weapon.mainhand with minecraft:netherite_axe[minecraft:item_model="{NS}:marteau_forge_racine"]'],
        "stray": [f"item replace entity @s armor.{s} with {piece(s, 'liche')}" for s in ("chest", "legs", "feet")]
                 + [f'item replace entity @s armor.head with minecraft:paper[minecraft:item_model="{NS}:couronne_givre_racine"]',
                    f'item replace entity @s weapon.mainhand with minecraft:bow[minecraft:item_model="{NS}:baton_givre_racine"]'],
    }
    passagers = {"spider": "reine", "blaze": "brasier", "creeper": "creeper"}
    lignes = ["tag @s add bs.hab",
              "data merge entity @s {drop_chances:{head:0f,chest:0f,legs:0f,feet:0f,mainhand:0f,offhand:0f}}"]
    for t, l in tenue.items():
        fn(f"metiers/tenue_{t}", l)
        lignes.append(f"execute if entity @s[type=minecraft:{t}] run function {NS}:metiers/tenue_{t}")
    for t, nom in passagers.items():
        sous = []
        for R in PARURES[nom]:
            M = R.matrices({})
            for o, lueur in R.pieces():
                pid = R.ident_piece(o, lueur)
                x, y, z, s = POSE[R.nom]
                m = mul(mul(trans(x, y, z), echelle(s)), M[pid])
                br = "brightness:{sky:15,block:15}" if lueur else "brightness:{sky:0,block:13}"
                tags = ["bs.mh", "bs.mhn"] + (["bs.tourne"] if R.nom == "brasier_anneau" else [])
                sous.append(f'summon minecraft:item_display ~ ~ ~ {{Tags:{tags!r},item:{{id:"minecraft:paper",count:1,components:{{"minecraft:item_model":"{NS}:{pid}"}}}},'
                            f'item_display:"none",view_range:3f,{br},transformation:{snbt_matrice(m)}}}'.replace("'", '"'))
                sous.append("ride @e[type=minecraft:item_display,tag=bs.mhn,limit=1] mount @s")
                sous.append("tag @e[type=minecraft:item_display,tag=bs.mhn] remove bs.mhn")
        fn(f"metiers/parure_{nom}", sous)
        lignes.append(f"execute if entity @s[type=minecraft:{t}] run function {NS}:metiers/parure_{nom}")
    fn("metiers/habiller", lignes)
    # anneau du Brasier : il tourne (3 tiers de tour par cycle de 2 s, le jeu interpole)
    R = PARURES["brasier"][0]
    M = R.matrices({})
    tours = []
    for i, ang in enumerate((120, 240, 0)):
        l = []
        for o, lueur in R.pieces():
            pid = R.ident_piece(o, lueur)
            x, y, z, s = POSE[R.nom]
            m = mul(mul(mul(trans(x, y, z), rot(0, ang, 0)), echelle(s)), M[pid])
            l.append(f'execute as @e[type=minecraft:item_display,tag=bs.tourne] if items entity @s contents *[minecraft:item_model="{NS}:{pid}"] run '
                     f"data merge entity @s {{start_interpolation:0,interpolation_duration:40,transformation:{snbt_matrice(m)}}}")
        fn(f"metiers/tour_{i}", l)
    fn("metiers/tick", [
        f"execute as @e[tag=metiers.boss,tag=!bs.hab] at @s run function {NS}:metiers/habiller",
        f"execute as @e[tag=metiers.boss,tag=bs.hab] run function {NS}:metiers/suivre",
        f"execute as @e[type=minecraft:item_display,tag=bs.mh] unless predicate {NS}:monte run kill @s"])
    fn("metiers/suivre", ["data modify storage boss:t m set from entity @s Rotation[0]",
                          "execute on passengers if entity @s[tag=bs.mh,tag=!bs.tourne] run data modify entity @s Rotation[0] set from storage boss:t m"])
    fn("metiers/seconde", ["scoreboard players add #tour bs.ev 1", "execute if score #tour bs.ev matches 6.. run scoreboard players set #tour bs.ev 0",
                           f"execute if score #tour bs.ev matches 0 run function {NS}:metiers/tour_0",
                           f"execute if score #tour bs.ev matches 2 run function {NS}:metiers/tour_1",
                           f"execute if score #tour bs.ev matches 4 run function {NS}:metiers/tour_2"])

"""Genere le datapack Horreur : build/horreur_datapack/ + horreur.zip (convention de l'usine).

Creatures (table dans creatures.py) :
  - mob vanilla INVISIBLE (IA, vie) + apparence du resource pack (habit = equipement, statue = item_display passager)
  - apparitions rares par joueur (toutes les 30 s, selon le lieu), delai entre deux apparitions par joueur
  - comportements toutes les 5 ticks (c/<id>), disparition si personne n'est la, ou au lever du jour
Bestiaire : progres « joueur a tue » par creature -> compteur, paliers 1 / 10 / 50, menu par dialogue.
"""
import json, os, shutil, sys, zipfile

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from creatures import CREATURES, PALIERS
import sons

# Sons personnalises presents dans le resource pack (sons.py) ; sinon on garde un son vanilla
SONS_OK = sons.disponibles()


def son(nom, vanilla):
    """'horreur:slender.statique' si le son existe, sinon le son vanilla de secours (meme ligne playsound)."""
    return "horreur:" + nom.replace("_", ".", 1) if nom in SONS_OK else vanilla

ROOT = os.path.join(ICI, "..", "build", "horreur_datapack")
NS = "horreur"
F = f"data/{NS}/function/"
if os.path.exists(ROOT):
    shutil.rmtree(ROOT)


def w(path, txt):
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    lignes = [l.strip() for l in txt.strip().splitlines()]
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(l for l in lignes if l) + "\n")


def wj(path, obj):
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def snbt(obj):
    """JSON compact = SNBT valide (cles entre guillemets acceptees)."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def tags_nbt(tag):
    return '{Tags:["' + tag + '"]}'


C = {c["id"]: c for c in CREATURES}
IDS = [c["id"] for c in CREATURES]

# ---------------------------------------------------------------------------------------------
wj("pack.mcmeta", {"pack": {"description": "Horreur : créatures de cauchemar et bestiaire",
                            "min_format": 84, "max_format": 200}})
wj("data/minecraft/tags/function/load.json", {"values": [f"{NS}:load"]})
wj("data/minecraft/tags/function/tick.json", {"values": [f"{NS}:tick"]})

# Blocs qu'une creature peut occuper (recherche du sol)
wj(f"data/{NS}/tags/block/passable.json", {"values": [
    "#minecraft:air", "#minecraft:leaves", "#minecraft:flowers", "#minecraft:saplings", "#minecraft:wool_carpets",
    "minecraft:short_grass", "minecraft:tall_grass", "minecraft:fern", "minecraft:large_fern", "minecraft:dead_bush",
    "minecraft:vine", "minecraft:glow_lichen", "minecraft:snow", "minecraft:moss_carpet", "minecraft:light",
    "minecraft:nether_sprouts", "minecraft:crimson_roots", "minecraft:warped_roots", "minecraft:hanging_roots",
    {"id": "minecraft:bush", "required": False}, {"id": "minecraft:firefly_bush", "required": False},
    {"id": "minecraft:short_dry_grass", "required": False}, {"id": "minecraft:tall_dry_grass", "required": False},
    {"id": "minecraft:leaf_litter", "required": False}]})

# ---------------------------------------------------------------------------------------------
# Lieux d'apparition (predicats evalues sur le joueur)
OW = {"dimension": "minecraft:overworld"}


def loc(**p):
    return {"type": "minecraft:location_check", "predicate": p}


wj(f"data/{NS}/predicate/lieu/surface.json", loc(**OW, can_see_sky=True))
wj(f"data/{NS}/predicate/lieu/foret.json", {"type": "minecraft:all_of", "terms": [
    loc(**OW),
    {"type": "minecraft:any_of", "terms": [loc(biomes="#minecraft:is_forest"), loc(biomes="#minecraft:is_taiga")]}]})
wj(f"data/{NS}/predicate/lieu/plaine.json", {"type": "minecraft:all_of", "terms": [
    loc(**OW, can_see_sky=True),
    {"type": "minecraft:any_of", "terms": [
        loc(biomes="#minecraft:is_savanna"),
        loc(biomes=["minecraft:plains", "minecraft:sunflower_plains", "minecraft:meadow", "minecraft:snowy_plains"])]}]})
# sous terre : plus de condition de lumière (une torche n'empêche plus rien), dès la couche 62
wj(f"data/{NS}/predicate/lieu/grotte.json", loc(**OW, can_see_sky=False, position={"y": {"max": 62}}))
wj(f"data/{NS}/predicate/lieu/sous_terre.json", loc(**OW, can_see_sky=False, position={"y": {"max": 62}}))
wj(f"data/{NS}/predicate/lieu/nether.json", loc(dimension="minecraft:the_nether"))
for nom, a, b in (("nuit", 13000, 23000), ("minuit", 17500, 18500)):
    wj(f"data/{NS}/predicate/{nom}.json", {"type": "minecraft:time_check", "clock": "minecraft:overworld",
                                          "value": {"min": a, "max": b}, "period": 24000})

LIEU = {  # lignes de la fonction lieu/<id> (renvoie 1 si le joueur est dans le bon lieu)
    "foret": ["execute if score #nuit hr.tmp matches 1 if predicate horreur:lieu/foret run return 1"],
    "surface": ["execute if score #nuit hr.tmp matches 1 if predicate horreur:lieu/surface run return 1"],
    "plaine": ["execute if score #nuit hr.tmp matches 1 if predicate horreur:lieu/plaine run return 1"],
    "grotte": ["execute if predicate horreur:lieu/grotte run return 1"],
    "sous_terre": ["execute if predicate horreur:lieu/sous_terre run return 1"],
    "enfer": ["execute if predicate horreur:lieu/nether run return 1",
              "execute if score #nuit hr.tmp matches 1 if predicate horreur:lieu/surface run return 1"],
}
for c in CREATURES:
    w(F + f"lieu/{c['id']}.mcfunction", "\n".join(LIEU[c["lieu"]] + ["return fail"]))
    # Le joueur regarde-t-il cette creature ? (ligne de vue reelle, blocs compris)
    wj(f"data/{NS}/predicate/regarde/{c['id']}.json", {
        "type": "minecraft:entity_properties", "entity": "this",
        "predicate": {"minecraft:type_specific/player": {"looking_at": {"minecraft:nbt": tags_nbt("hr.c." + c["id"])}}}})

# ---------------------------------------------------------------------------------------------
# Chargement, boucles
objs = ["hr.tmp", "hr.cfg", "hr.cd", "hr.vie", "hr.age", "hr.etat", "hr.t", "hr.r"] + [f"hr.k.{i}" for i in IDS]
w(F + "load.mcfunction", "\n".join(
    [f"scoreboard objectives add {o} dummy" for o in objs]
    + ["scoreboard objectives add bestiaire trigger",
       "execute unless score #init hr.cfg matches 1 run function horreur:config/defaut",
       # version 2 des réglages (apparitions plus fréquentes) : remplace les anciennes chances une fois
       "execute unless score #ver hr.cfg matches 2.. run function horreur:config/defaut",
       "schedule function horreur:seconde 20t replace"]))
w(F + "config/defaut.mcfunction", "\n".join(
    [f"scoreboard players set #ch_{c['id']} hr.cfg {c['chance']}" for c in CREATURES]
    + ["scoreboard players set #cd hr.cfg 600", "scoreboard players set #actif hr.cfg 1",
       "scoreboard players set #init hr.cfg 1", "scoreboard players set #ver hr.cfg 2"]))
w(F + "config/debug.mcfunction", "\n".join(
    ["# Test : apparitions tres frequentes (toutes les 30 s, sans delai). Revenir avec horreur:config/defaut"]
    + [f"scoreboard players set #ch_{c['id']} hr.cfg 500" for c in CREATURES]
    + ["scoreboard players set #cd hr.cfg 0", "scoreboard players set @a hr.cd 0",
       'tellraw @s {"text":"[Horreur] Mode test : apparitions très fréquentes.","color":"red"}']))
w(F + "config/arret.mcfunction", """
scoreboard players set #actif hr.cfg 0
tellraw @s {"text":"[Horreur] Apparitions désactivées (horreur:config/marche pour relancer).","color":"gray"}""")
w(F + "config/marche.mcfunction", """
scoreboard players set #actif hr.cfg 1
tellraw @s {"text":"[Horreur] Apparitions activées.","color":"gray"}""")

w(F + "tick.mcfunction", """
execute as @a[scores={bestiaire=1..}] run function horreur:ui/trigger
execute if entity @e[tag=hr.e,limit=1] run function horreur:creatures""")

w(F + "creatures.mcfunction", """
# Apparences : une statue sans son mob est retiree, et suit la rotation de son mob
tag @e[type=item_display,tag=hr.vis] remove hr.ok
execute as @e[tag=hr.c] on passengers run tag @s add hr.ok
execute as @e[type=item_display,tag=hr.vis,tag=!hr.ok] at @s run function horreur:vis/orphelin
execute as @e[type=item_display,tag=hr.envol] at @s run function horreur:vis/envol
execute as @e[tag=hr.statue] run function horreur:vis/tourner
# Comportements toutes les 5 ticks
scoreboard players add #t5 hr.tmp 1
execute if score #t5 hr.tmp matches 5.. run scoreboard players set #t5 hr.tmp 0
execute if score #t5 hr.tmp matches 0 as @e[tag=hr.c] at @s run function horreur:c/comportement""")

w(F + "vis/tourner.mcfunction", """
data modify storage horreur:t r set from entity @s Rotation[0]
execute on passengers if entity @s[tag=hr.vis] run data modify entity @s Rotation[0] set from storage horreur:t r""")
w(F + "vis/orphelin.mcfunction", """
execute if entity @s[tag=hr.ballon] run return run function horreur:vis/lacher
particle minecraft:large_smoke ~ ~1 ~ 0.3 0.8 0.3 0.02 25
kill @s""")
w(F + "vis/lacher.mcfunction", """
tag @s remove hr.vis
tag @s add hr.envol
scoreboard players set @s hr.t 0""")
w(F + "vis/envol.mcfunction", """
tp @s ~ ~0.12 ~
scoreboard players add @s hr.t 1
execute if score @s hr.t matches 100.. run kill @s""")

w(F + "seconde.mcfunction", """
schedule function horreur:seconde 20t replace
scoreboard players enable @a bestiaire
scoreboard players remove @a[scores={hr.cd=1..}] hr.cd 1
scoreboard players set #nuit hr.tmp 0
execute if predicate horreur:nuit run scoreboard players set #nuit hr.tmp 1
scoreboard players set #minuit hr.tmp 0
execute if predicate horreur:minuit run scoreboard players set #minuit hr.tmp 1
execute as @e[tag=hr.c] at @s run function horreur:c/vie
execute as @e[tag=hr.serv] at @s run function horreur:c/vie_serviteur
scoreboard players add #s hr.tmp 1
execute if score #s hr.tmp matches 30.. run function horreur:spawn/cycle""")

w(F + "c/vie.mcfunction", """
scoreboard players add @s hr.age 1
execute if score @s hr.age matches 900.. run return run function horreur:c/disparaitre
execute if entity @s[tag=hr.nuit] if score #nuit hr.tmp matches 0 run return run function horreur:c/disparaitre
execute if entity @a[distance=..20,gamemode=!spectator] run return 0
scoreboard players remove @s hr.vie 1
execute if score @s hr.vie matches ..0 run function horreur:c/disparaitre""")
w(F + "c/vie_serviteur.mcfunction", """
scoreboard players add @s hr.age 1
execute if score @s hr.age matches 90.. run function horreur:c/disparaitre""")
w(F + "c/disparaitre.mcfunction", """
particle minecraft:large_smoke ~ ~1 ~ 0.4 0.9 0.4 0.02 40
playsound minecraft:entity.enderman.teleport hostile @a[distance=..32] ~ ~ ~ 1 0.5
execute on passengers run kill @s
tp @s ~ -1000 ~
kill @s""")

# ---------------------------------------------------------------------------------------------
# Apparitions
w(F + "spawn/cycle.mcfunction", """
scoreboard players set #s hr.tmp 0
execute if score #actif hr.cfg matches 1 as @a[gamemode=!spectator] at @s unless score @s hr.cd matches 1.. run function horreur:spawn/tenter""")
tenter = ["# Une seule creature a la fois autour d'un joueur",
          "execute if entity @e[tag=hr.c,distance=..128] run return 0",
          "execute store result score #r hr.tmp run random value 1..1000"]
for c in CREATURES:
    k = c["id"]
    if c.get("bonus"):   # plus de chances dans son biome de prédilection
        tenter.append(f"execute if function horreur:lieu/{k} if predicate horreur:lieu/{c['bonus'][0]} run scoreboard players remove #r hr.tmp {c['bonus'][1]}")
    tenter += [f"execute if function horreur:lieu/{k} run scoreboard players operation #r hr.tmp -= #ch_{k} hr.cfg",
               f"execute if score #r hr.tmp matches ..0 run return run function horreur:spawn/{k}"]
w(F + "spawn/tenter.mcfunction", "\n".join(tenter))

# Placement : angle (relatif au regard du joueur), distance, recherche du sol, hauteur libre
PLACE = {"slender": (0, 359, 24, 3), "herobrine": (-45, 45, 24, 2), "siren": (0, 359, 24, 8),
         "nonne": (160, 200, 4, 2), "clown": (0, 359, 6, 2), "pinhead": (0, 359, 8, 3)}
for c in CREATURES:
    k = c["id"]
    a0, a1, lim, h = PLACE[k]
    d0, d1 = c["distance"]
    w(F + f"spawn/{k}.mcfunction", f"""
data modify storage horreur:t s set value {{c:"{k}",a0:{a0},a1:{a1},d0:{d0},d1:{d1}}}
scoreboard players set #lim hr.tmp {lim}
scoreboard players set #h hr.tmp {h}
scoreboard players set #surf hr.tmp {1 if c["lieu"] in ("foret", "surface", "plaine") else 0}
function horreur:spawn/placer""")
w(F + "spawn/placer.mcfunction", """
summon minecraft:marker ~ ~ ~ {Tags:["hr.pt"]}
scoreboard players set #essai hr.tmp 0
function horreur:spawn/essai with storage horreur:t s
kill @e[type=minecraft:marker,tag=hr.pt]""")
w(F + "spawn/essai.mcfunction", """
scoreboard players add #essai hr.tmp 1
execute if score #essai hr.tmp matches 9.. run return fail
$execute store result storage horreur:t s.a int 1 run random value $(a0)..$(a1)
$execute store result storage horreur:t s.d int 1 run random value $(d0)..$(d1)
function horreur:spawn/viser with storage horreur:t s""")
w(F + "spawn/viser.mcfunction", """
$execute rotated ~$(a) 0 positioned ^ ^ ^$(d) run tp @e[type=minecraft:marker,tag=hr.pt,limit=1] ~ ~ ~
execute if score #surf hr.tmp matches 1 as @e[type=minecraft:marker,tag=hr.pt,limit=1] at @s positioned over motion_blocking_no_leaves run tp @s ~ ~ ~
execute as @e[type=minecraft:marker,tag=hr.pt,limit=1] at @s run function horreur:sol/trouver
execute unless score #ok hr.tmp matches 1 run return run function horreur:spawn/essai with storage horreur:t s
scoreboard players operation @s hr.cd = #cd hr.cfg
$execute at @e[type=minecraft:marker,tag=hr.pt,limit=1] run function horreur:invoquer/$(c)
execute at @e[type=minecraft:marker,tag=hr.pt,limit=1] run tellraw @a[distance=..64,gamemode=!spectator] {"text":"Quelque chose rôde près d'ici...","color":"dark_gray","italic":true}""")

# Recherche du sol a partir de la position de l'entite executante (marqueur) : #lim pas max, #h blocs libres
w(F + "sol/trouver.mcfunction", """
scoreboard players set #n hr.tmp 0
scoreboard players set #ok hr.tmp 0
execute unless block ~ ~ ~ #horreur:passable run return run function horreur:sol/monter
function horreur:sol/descendre""")
w(F + "sol/monter.mcfunction", """
scoreboard players add #n hr.tmp 1
execute if score #n hr.tmp > #lim hr.tmp run return fail
tp @s ~ ~1 ~
execute at @s unless block ~ ~ ~ #horreur:passable run return run function horreur:sol/monter
execute at @s run function horreur:sol/valider""")
w(F + "sol/descendre.mcfunction", """
execute unless block ~ ~-1 ~ #horreur:passable run return run function horreur:sol/valider
scoreboard players add #n hr.tmp 1
execute if score #n hr.tmp > #lim hr.tmp run return fail
tp @s ~ ~-1 ~
execute at @s run function horreur:sol/descendre""")
w(F + "sol/valider.mcfunction", """
execute unless block ~ ~1 ~ #horreur:passable run return fail
execute if block ~ ~-1 ~ #minecraft:leaves run return fail
execute if block ~ ~-1 ~ minecraft:water run return fail
execute if block ~ ~-1 ~ minecraft:lava run return fail
execute if block ~ ~-1 ~ minecraft:powder_snow run return fail
execute if score #h hr.tmp matches 3.. unless block ~ ~2 ~ #horreur:passable run return fail
execute if score #h hr.tmp matches 5.. unless block ~ ~4 ~ #horreur:passable run return fail
execute if score #h hr.tmp matches 8.. unless block ~ ~7 ~ #horreur:passable run return fail
scoreboard players set #ok hr.tmp 1""")

# ---------------------------------------------------------------------------------------------
# Invocation
HAUT = {"zombie": 1.95, "husk": 1.95}


def item_nbt(slot, k):
    return ('{id:"minecraft:paper",count:1,components:{"minecraft:equippable":{slot:"' + slot
            + '",asset_id:"horreur:' + k + '"},"minecraft:item_model":"horreur:vide"}}')


VIDE = '{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"horreur:vide"}}'


def display(modele, tags, s, t, x=0.0, portee=2.0):
    return ('{id:"minecraft:item_display",Tags:' + snbt(["hr.e", "hr.vis"] + tags)
            + ',item:{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"horreur:' + modele + '"}}'
            + f',item_display:"none",teleport_duration:2,view_range:{portee}f'
            + f',transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],'
            + f'translation:[{x:.3f}f,{t:.3f}f,0f],scale:[{s}f,{s}f,{s}f]}}}}')


def summon(c):
    k = c["id"]
    tags = ["hr.e", "hr.c", "hr.c." + k, "hr.neuf"]
    if c["apparence"] == "statue":
        tags.append("hr.statue")
    if c["nuit"]:
        tags.append("hr.nuit")
    attrs = [("max_health", c["vie"]), ("attack_damage", c["degats"]), ("armor", c["armure"]),
             ("movement_speed", c["vitesse"]), ("knockback_resistance", c["recul"]), ("follow_range", 64),
             ("scale", c["echelle"]), ("spawn_reinforcements", 0), ("step_height", 1.2 if c["echelle"] > 2 else 0.6)]
    nbt = [f"Tags:{snbt(tags)}", "Silent:1b", "PersistenceRequired:1b", "CanPickUpLoot:0b", "IsBaby:0b",
           "CanBreakDoors:0b", f'DeathLootTable:"horreur:creature/{k}"', f"Health:{c['vie']}f",
           "CustomName:" + snbt({"text": c["nom"], "color": c["couleur"]}),
           "attributes:[" + ",".join(f'{{id:"minecraft:{a}",base:{v}d}}' for a, v in attrs) + "]",
           "active_effects:[{id:\"minecraft:invisibility\",duration:-1,amplifier:0b,show_particles:0b,show_icon:0b},"
           "{id:\"minecraft:fire_resistance\",duration:-1,amplifier:0b,show_particles:0b,show_icon:0b}]",
           "drop_chances:{head:0f,chest:0f,legs:0f,feet:0f,mainhand:0f,offhand:0f}"]
    passagers = []
    if c["apparence"] == "habit":
        nbt.append("equipment:{head:" + item_nbt("head", k) + ",chest:" + item_nbt("chest", k)
                   + ",feet:" + item_nbt("feet", k) + "}")
    else:
        nbt.append("equipment:{head:" + VIDE + "}")
        s = c["statue_echelle"]
        # Le passager est accroche au sommet du mob : on redescend le modele (pieds du modele a y = -16 px)
        t = 1.5 * s - HAUT[c["base"]] * c["echelle"]
        passagers.append(display(k, ["hr.statue_vis"], s, t, portee=4.0 if c["echelle"] > 2 else 2.0))
    if c.get("ballon"):
        passagers.append(display("ballon", ["hr.ballon"], 1.0, 0.9 + 1.0 - HAUT[c["base"]] * c["echelle"], x=0.45))
    if passagers:
        nbt.append("Passengers:[" + ",".join(passagers) + "]")
    return f"summon minecraft:{c['base']} ~ ~ ~ {{" + ",".join(nbt) + "}"


INIT_EXTRA = {
    "slender": [f"playsound {son('slender_presence', 'minecraft:ambient.cave')} hostile @a[distance=..48] ~ ~ ~ 1.5 1"],
    "herobrine": [],
    "siren": ["function horreur:c/siren_cri"],
    "nonne": [f"playsound {son('nonne_murmure', 'minecraft:entity.vex.ambient')} hostile @a[distance=..16] ~ ~ ~ 1 " + ("1" if "nonne_murmure" in SONS_OK else "0.5")],
    "clown": [f"playsound {son('clown_rire', 'minecraft:entity.witch.celebrate')} hostile @a[distance=..32] ~ ~ ~ 1.5 " + ("1" if "clown_rire" in SONS_OK else "1.4")],
    "pinhead": [f"playsound {son('pinhead_cloche', 'minecraft:block.bell.resonate')} hostile @a[distance=..48] ~ ~ ~ 2 " + ("1" if "pinhead_cloche" in SONS_OK else "0.5"),
                "execute if dimension minecraft:overworld run tag @s add hr.nuit"],
}
for c in CREATURES:
    k = c["id"]
    w(F + f"invoquer/{k}.mcfunction", summon(c) + f"\nexecute as @e[tag=hr.neuf] at @s run function horreur:c/init_{k}")
    w(F + f"c/init_{k}.mcfunction", "\n".join(
        ["tag @s remove hr.neuf", "scoreboard players set @s hr.vie 120", "scoreboard players set @s hr.age 0",
         "scoreboard players set @s hr.etat 0", "scoreboard players set @s hr.t 0", "scoreboard players set @s hr.r 0"]
        + INIT_EXTRA[k]))
w(F + "invoquer.mcfunction", """
# Admin : /function horreur:invoquer {c:"slender"}  (slender, herobrine, siren, nonne, clown, pinhead)
# 4 blocs devant soi a l'horizontale (le regard vers le bas ne compte pas), pose au sol ; sinon aux pieds
scoreboard players set #lim hr.tmp 6
scoreboard players set #h hr.tmp 2
summon minecraft:marker ~ ~ ~ {Tags:["hr.pt"]}
execute rotated ~ 0 positioned ^ ^ ^4 align y run tp @e[type=minecraft:marker,tag=hr.pt,limit=1] ~ ~ ~
execute as @e[type=minecraft:marker,tag=hr.pt,limit=1] at @s run function horreur:sol/trouver
execute unless score #ok hr.tmp matches 1 run tp @e[type=minecraft:marker,tag=hr.pt,limit=1] ~ ~ ~
$execute at @e[type=minecraft:marker,tag=hr.pt,limit=1] align xz positioned ~0.5 ~ ~0.5 run function horreur:invoquer/$(c)
kill @e[type=minecraft:marker,tag=hr.pt]""")

# Butin (format 26.x : « modifier » et « type ») : chaque objet courant tombe, plus une chance sur 4 d'un objet rare
def entree(it, a, b, poids=1):
    e = {"type": "minecraft:item", "name": f"minecraft:{it}", "weight": poids}
    mods = []
    if (a, b) != (1, 1):
        mods.append({"type": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": a, "max": b}})
    if it == "enchanted_book":
        mods.append({"type": "minecraft:enchant_with_levels", "levels": 30})
    if mods:
        e["modifier"] = mods
    return e
for c in CREATURES:
    pools = [{"rolls": 1, "entries": [entree(it, a, b)]} for it, a, b, _ in c["butin"]]
    rares = [entree(it, a, b, p) for it, a, b, p in c.get("rare", [])]
    if rares:
        pools.append({"rolls": 1, "entries": rares + [{"type": "minecraft:empty", "weight": 3 * sum(p for *_, p in c["rare"])}]})
    wj(f"data/{NS}/loot_table/creature/{c['id']}.json", {"type": "minecraft:entity", "pools": pools})

# ---------------------------------------------------------------------------------------------
# Comportements (toutes les 5 ticks, en tant que creature)
w(F + "c/comportement.mcfunction", "\n".join(
    f"execute if entity @s[tag=hr.c.{k}] run return run function horreur:c/{k}" for k in IDS))

JOUEUR = "gamemode=!spectator"
# Regard : rayon depuis les yeux de chaque joueur proche, arrêté par les blocs pleins ; les joueurs qui voient
# la créature (@s, taguée hr.cible) reçoivent le tag hr.voit et #vu passe à 1
w(F + "c/vu.mcfunction", f"""
tag @a remove hr.voit
scoreboard players set #vu hr.tmp 0
tag @s add hr.cible
execute as @a[distance=..64,{JOUEUR}] at @s anchored eyes positioned ^ ^ ^1 run function horreur:c/rayon
tag @s remove hr.cible""")
w(F + "c/rayon.mcfunction", """
scoreboard players set #p hr.tmp 0
function horreur:c/rayon_pas""")
w(F + "c/rayon_pas.mcfunction", """
execute if entity @e[tag=hr.cible,distance=..1.8] run return run function horreur:c/voit
execute positioned ~ ~-1.6 ~ if entity @e[tag=hr.cible,distance=..1.4] run return run function horreur:c/voit
execute unless block ~ ~ ~ #horreur:passable run return 0
scoreboard players add #p hr.tmp 1
execute if score #p hr.tmp matches ..63 positioned ^ ^ ^1 run function horreur:c/rayon_pas""")
w(F + "c/voit.mcfunction", "tag @s add hr.voit\nscoreboard players set #vu hr.tmp 1")
w(F + "c/slender.mcfunction", f"""
particle minecraft:portal ~ ~1.6 ~ 0.3 1 0.3 0.4 4
execute unless entity @a[distance=..64,{JOUEUR}] run return 0
execute if score @s hr.etat matches 2 run return run function horreur:c/slender_chasse
rotate @s facing entity @p[{JOUEUR}] feet
function horreur:c/vu
execute if score #vu hr.tmp matches 1 run return run function horreur:c/slender_fixe
scoreboard players set @s hr.r 0
scoreboard players add @s hr.t 5
execute if score @s hr.t matches 60.. run function horreur:c/slender_approche""")
w(F + "c/slender_fixe.mcfunction", f"""
scoreboard players add @s hr.r 5
execute if score @s hr.r matches 20 as @a[tag=hr.voit] run effect give @s minecraft:darkness 8 0 true
execute if score @s hr.r matches 20 as @a[tag=hr.voit] at @s run playsound {son('slender_statique', 'minecraft:block.portal.ambient')} hostile @s ~ ~ ~ 0.8 1
execute if score @s hr.r matches 40 as @a[tag=hr.voit] at @s run playsound {son('slender_statique', 'minecraft:entity.enderman.stare')} hostile @s ~ ~ ~ 1 0.8
execute if score @s hr.r matches 40 as @a[tag=hr.voit] run effect give @s minecraft:nausea 8 0 true
execute if score @s hr.r matches 60.. run function horreur:c/slender_decide""")
w(F + "c/slender_decide.mcfunction", """
execute store result score #r hr.tmp run random value 1..2
execute if score #r hr.tmp matches 1 run return run function horreur:c/slender_reveil
function horreur:c/disparaitre""")
w(F + "c/slender_reveil.mcfunction", f"""
scoreboard players set @s hr.etat 2
scoreboard players set @s hr.t 0
attribute @s minecraft:movement_speed base set 0.34
playsound {son('slender_reveil', 'minecraft:entity.enderman.scream')} hostile @a[distance=..48] ~ ~ ~ 2 1
effect give @a[distance=..24,gamemode=!spectator] minecraft:darkness 10 0 true""")
w(F + "c/slender_chasse.mcfunction", f"""
scoreboard players add @s hr.t 5
execute if score @s hr.t matches 80.. unless entity @a[distance=..8,{JOUEUR}] run function horreur:c/slender_approche""")
w(F + "c/slender_approche.mcfunction", f"""
scoreboard players set @s hr.t 0
execute if score @s hr.etat matches 0 if entity @a[distance=..7,{JOUEUR}] run return run function horreur:c/slender_reveil
execute if entity @a[distance=..20,{JOUEUR}] run playsound {son('slender_presence', 'minecraft:block.portal.ambient')} hostile @a[distance=..20] ~ ~ ~ 0.8 1
scoreboard players set #lim hr.tmp 10
scoreboard players set #h hr.tmp 3
summon minecraft:marker ~ ~ ~ {{Tags:["hr.pt2"]}}
execute facing entity @p[{JOUEUR}] feet rotated ~ 0 positioned ^ ^ ^6 run tp @e[type=minecraft:marker,tag=hr.pt2,limit=1] ~ ~ ~
execute as @e[type=minecraft:marker,tag=hr.pt2,limit=1] at @s run function horreur:sol/trouver
execute if score #ok hr.tmp matches 1 run function horreur:c/teleporter
kill @e[type=minecraft:marker,tag=hr.pt2]""")
w(F + "c/teleporter.mcfunction", """
particle minecraft:portal ~ ~1.5 ~ 0.3 1 0.3 0.6 30
tp @s @e[type=minecraft:marker,tag=hr.pt2,limit=1]
execute at @s run rotate @s facing entity @p[gamemode=!spectator] feet
execute at @s run particle minecraft:portal ~ ~1.5 ~ 0.3 1 0.3 0.6 30""")

w(F + "c/herobrine.mcfunction", f"""
execute unless entity @a[distance=..64,{JOUEUR}] run return 0
execute if score @s hr.etat matches 2 run return 0
execute if entity @a[distance=..14,{JOUEUR}] run return run function horreur:c/herobrine_decide
function horreur:c/vu
execute if score #vu hr.tmp matches 1 run scoreboard players add @s hr.r 5
execute if score @s hr.r matches 60.. run function horreur:c/herobrine_decide""")
w(F + "c/herobrine_decide.mcfunction", f"""
execute store result score #r hr.tmp run random value 1..4
execute if score #r hr.tmp matches 1 run return run function horreur:c/herobrine_reveil
playsound {son('herobrine_apparition', 'minecraft:ambient.cave')} hostile @a[distance=..48] ~ ~ ~ 1.5 1
function horreur:c/disparaitre""")
w(F + "c/herobrine_reveil.mcfunction", f"""
scoreboard players set @s hr.etat 2
attribute @s minecraft:movement_speed base set 0.36
scoreboard players set #lim hr.tmp 4
scoreboard players set #h hr.tmp 2
summon minecraft:marker ~ ~ ~ {{Tags:["hr.pt2"]}}
execute as @p[{JOUEUR}] at @s rotated ~180 0 positioned ^ ^ ^2 run tp @e[type=minecraft:marker,tag=hr.pt2,limit=1] ~ ~ ~
execute as @e[type=minecraft:marker,tag=hr.pt2,limit=1] at @s run function horreur:sol/trouver
execute if score #ok hr.tmp matches 1 run function horreur:c/teleporter
kill @e[type=minecraft:marker,tag=hr.pt2]
execute at @s run playsound {son('herobrine_apparition', 'minecraft:entity.lightning_bolt.thunder')} hostile @a[distance=..32] ~ ~ ~ 1.5 1
execute at @s run effect give @a[distance=..6,{JOUEUR}] minecraft:blindness 2 0 true""")

w(F + "c/siren.mcfunction", f"""
scoreboard players add @s hr.t 5
execute store result score #r hr.tmp run random value 1..30
execute if score #r hr.tmp matches 1 if entity @a[distance=..32,{JOUEUR}] run playsound {son('siren_voix', 'minecraft:entity.warden.ambient')} hostile @a[distance=..40] ~ ~6 ~ 2.5 1
execute if score @s hr.t matches 120.. run function horreur:c/siren_cri""")
w(F + "c/siren_cri.mcfunction", f"""
scoreboard players set @s hr.t 0
playsound {son('siren_sirene', 'minecraft:event.raid.horn')} hostile @a[distance=..160] ~ ~6 ~ 10 1""")

w(F + "c/nonne.mcfunction", f"""
execute store result score #r hr.tmp run random value 1..40
execute if score #r hr.tmp matches 1 run playsound {son('nonne_murmure', 'minecraft:entity.vex.ambient')} hostile @a[distance=..20] ~ ~ ~ 1 {1 if 'nonne_murmure' in SONS_OK else 0.5}
execute if score #r hr.tmp matches 2 run playsound minecraft:ambient.cave hostile @a[distance=..20] ~ ~ ~ 0.8 1.2""")

w(F + "c/clown.mcfunction", f"""
execute store result score #r hr.tmp run random value 1..30
execute if score #r hr.tmp matches 1 run playsound {son('clown_rire', 'minecraft:entity.witch.celebrate')} hostile @a[distance=..32] ~ ~ ~ 1.5 {1 if 'clown_rire' in SONS_OK else 1.4}
execute if score #r hr.tmp matches 2 run playsound minecraft:entity.witch.ambient hostile @a[distance=..32] ~ ~ ~ 1 1.6""")

w(F + "c/pinhead.mcfunction", f"""
scoreboard players add @s hr.t 5
execute if score @s hr.t matches 80.. if entity @a[distance=..16,{JOUEUR}] run function horreur:c/pinhead_chaines
execute if score @s hr.etat matches 0 store result score #hp hr.tmp run data get entity @s Health
execute if score @s hr.etat matches 0 if score #hp hr.tmp matches ..60 run function horreur:c/pinhead_cenobites""")
w(F + "c/pinhead_chaines.mcfunction", f"""
scoreboard players set @s hr.t 0
playsound {son('pinhead_chaines', 'minecraft:block.anvil.land')} hostile @a[distance=..24] ~ ~ ~ 1.5 1
execute as @a[distance=..16,{JOUEUR},limit=2,sort=nearest] at @s run function horreur:c/pinhead_tirer""")
w(F + "c/pinhead_tirer.mcfunction", "\n".join(
    [f"execute anchored eyes facing entity @e[tag=hr.c.pinhead,sort=nearest,limit=1] eyes run particle minecraft:dust{{color:[0.42,0.42,0.48],scale:1.1}} ^ ^ ^{i} 0 0 0 0 1"
     for i in range(1, 15)]
    + ["effect give @s minecraft:slowness 2 2 true",
       "execute facing entity @e[tag=hr.c.pinhead,sort=nearest,limit=1] feet rotated ~ 0 positioned ^ ^ ^1.5 "
       "if block ~ ~ ~ #horreur:passable if block ~ ~1 ~ #horreur:passable run tp @s ~ ~ ~"]))
CENOBITE = ('summon minecraft:zombie ~{dx} ~ ~{dz} {{Tags:["hr.e","hr.serv"],PersistenceRequired:1b,CanPickUpLoot:0b,IsBaby:0b,'
            'CustomName:{{"text":"Cénobite","color":"gray"}},DeathLootTable:"minecraft:empty",'
            'attributes:[{{id:"minecraft:spawn_reinforcements",base:0d}},{{id:"minecraft:movement_speed",base:0.26d}}],'
            'equipment:{{head:{{id:"minecraft:chainmail_helmet",count:1}},chest:{{id:"minecraft:chainmail_chestplate",count:1}},'
            'legs:{{id:"minecraft:chainmail_leggings",count:1}}}},drop_chances:{{head:0f,chest:0f,legs:0f}}}}')
w(F + "c/pinhead_cenobites.mcfunction", "\n".join([
    "scoreboard players set @s hr.etat 1",
    f"playsound {son('pinhead_cloche', 'minecraft:block.bell.resonate')} hostile @a[distance=..32] ~ ~ ~ 1.5 " + ("1.3" if "pinhead_cloche" in SONS_OK else "0.5"),
    "particle minecraft:soul ~ ~1 ~ 1 0.5 1 0.02 30",
    CENOBITE.format(dx=1.5, dz=0), CENOBITE.format(dx=-1.5, dz=0),
    "scoreboard players set @e[tag=hr.serv,distance=..3] hr.age 0"]))

# Coups recus par un joueur (progres « mob blesse joueur »)
COUPS = {
    "slender": ["effect give @s minecraft:darkness 6 0 true"],
    "nonne": ["effect give @s minecraft:blindness 3 0 true", "effect give @s minecraft:weakness 5 0 true"],
    "clown": ["effect give @s minecraft:slowness 3 1 true"],
    "siren": ["effect give @s minecraft:nausea 5 0 true"],
    "pinhead": ["effect give @s minecraft:slowness 2 1 true"],
}
for k, lignes in COUPS.items():
    wj(f"data/{NS}/advancement/coup/{k}.json", {"criteria": {"c": {"trigger": "minecraft:entity_hurt_player", "conditions": {
        "damage": {"type": {"source_entity": {"minecraft:nbt": tags_nbt("hr.c." + k)}}}}}}, "rewards": {"function": f"{NS}:coup/{k}"}})
    w(F + f"coup/{k}.mcfunction", "\n".join([f"advancement revoke @s only horreur:coup/{k}"] + lignes))

# ---------------------------------------------------------------------------------------------
# Bestiaire : kills, paliers
def trophee(c):
    return (f'give @s minecraft:paper[minecraft:item_model="horreur:trophee_{c["id"]}",'
            f'minecraft:equippable={{slot:"head"}},minecraft:max_stack_size=1,minecraft:rarity="epic",'
            f'minecraft:item_name={snbt({"text": "Trophée : " + c["nom"], "color": "gold"})},'
            f'minecraft:lore=[{snbt({"text": str(PALIERS[1]) + " " + c["nom"] + " vaincus", "color": "gray", "italic": False})},'
            f'{snbt({"text": "Se porte sur la tête", "color": "dark_gray", "italic": False})}]]')


PREF = '{"text":"[Bestiaire] ","color":"dark_red"}'
# XP Chasseur (pack Metiers) : le bonus va dans m.c_bal ; au tick suivant, Metiers le verse avec l'XP
# de la stat killed:<base> (deja comptee, d'ou XP_BASE) -> un seul message "+N XP Chasseur"
XP_BASE = {"zombie": 3, "husk": 3}
for c in CREATURES:
    k, nom = c["id"], c["nom"]
    wj(f"data/{NS}/advancement/tue/{k}.json", {"criteria": {"c": {"trigger": "minecraft:player_killed_entity", "conditions": {
        "entity": {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"minecraft:nbt": tags_nbt("hr.c." + k)}}}}}, "rewards": {"function": f"{NS}:tue/{k}"}})
    w(F + f"tue/{k}.mcfunction", f"""
advancement revoke @s only horreur:tue/{k}
scoreboard players add @s hr.k.{k} 1
execute unless score @s m.afk matches 240.. if score @s m.c_bal matches -2147483648.. run scoreboard players add @s m.c_bal {max(0, c['xp'] - XP_BASE.get(c['base'], 0))}
execute if score @s hr.k.{k} matches {PALIERS[0]} run function horreur:palier/{k}_1
execute if score @s hr.k.{k} matches {PALIERS[1]} run function horreur:palier/{k}_2
execute if score @s hr.k.{k} matches {PALIERS[2]} run function horreur:palier/{k}_3""")
    nom_c = snbt({"text": nom, "color": c["couleur"], "bold": True})
    w(F + f"palier/{k}_1.mcfunction", f"""
tellraw @s [{PREF},{{"text":"Nouvelle créature découverte : ","color":"gray"}},{nom_c},{{"text":" ! (touche G ou /trigger bestiaire)","color":"gray"}}]
playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 0.8 0.8
xp add @s 50 points""")
    w(F + f"palier/{k}_2.mcfunction", f"""
tellraw @s [{PREF},{{"text":"{PALIERS[1]} victoires contre ","color":"gray"}},{nom_c},{{"text":" : voici ton trophée !","color":"gold"}}]
playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 0.7
{trophee(c)}""")
    w(F + f"palier/{k}_3.mcfunction", f"""
tellraw @a [{PREF},{{"selector":"@s","color":"gold"}},{{"text":" a vaincu {PALIERS[2]} fois ","color":"gray"}},{nom_c},{{"text":" et devient « {c['titre']} » !","color":"gold"}}]
playsound minecraft:ui.toast.challenge_complete master @a ~ ~ ~ 1 0.6""")

# ---------------------------------------------------------------------------------------------
# Menus (dialogues)
def bouton(label, val, larg=140, tip=None):
    b = {"label": label, "width": larg, "action": {"type": "minecraft:run_command", "command": f"trigger bestiaire set {val}"}}
    if tip:
        b["tooltip"] = {"text": tip}
    return b


def msg(contenu, larg=300):
    return {"type": "minecraft:plain_message", "width": larg, "contents": contenu}


TITRE = {"text": "☠ Bestiaire ☠", "color": "dark_red", "bold": True}
wj(f"data/{NS}/dialog/bestiaire.json", {
    "type": "minecraft:multi_action", "title": TITRE, "external_title": {"text": "Bestiaire", "color": "dark_red"},
    "can_close_with_escape": True, "pause": False,
    "body": [msg({"text": "Les créatures de la nuit que tu as affrontées. Tue une créature pour révéler sa fiche.", "color": "gray"})],
    "actions": [bouton({"text": "Ouvrir le bestiaire", "color": "red"}, 1, 200)], "columns": 1})
wj("data/minecraft/tags/dialog/quick_actions.json", {"values": [f"{NS}:bestiaire"]})
wj("data/minecraft/tags/dialog/pause_screen_additions.json", {"values": [f"{NS}:bestiaire"]})

w(F + "ui/trigger.mcfunction", "\n".join(
    ["scoreboard players operation #v hr.tmp = @s bestiaire", "scoreboard players set @s bestiaire 0",
     "scoreboard players enable @s bestiaire",
     "execute if score #v hr.tmp matches 1 run return run function horreur:ui/liste"]
    + [f"execute if score #v hr.tmp matches {11 + i} run return run function horreur:ui/fiche/{k}" for i, k in enumerate(IDS)]))

liste = ["scoreboard players set #d hr.tmp 0"]
for i, c in enumerate(CREATURES, 1):
    k = c["id"]
    connu = snbt({"text": c["nom"], "color": c["couleur"]})
    liste += [f'data modify storage horreur:ui m.l{i} set value {{"text":"???","color":"dark_gray"}}',
              f"execute if score @s hr.k.{k} matches 1.. run data modify storage horreur:ui m.l{i} set value {connu}",
              f"execute if score @s hr.k.{k} matches 1.. run scoreboard players add #d hr.tmp 1"]
liste += ["execute store result storage horreur:ui m.d int 1 run scoreboard players get #d hr.tmp",
          "function horreur:ui/liste_m with storage horreur:ui m"]
w(F + "ui/liste.mcfunction", "\n".join(liste))
d_liste = {"type": "minecraft:multi_action", "title": TITRE, "can_close_with_escape": True, "pause": False,
           "body": [msg({"text": f"§D / {len(CREATURES)} créatures découvertes", "color": "gray"})],
           "actions": [bouton(f"§L{i}", 11 + i - 1) for i in range(1, len(CREATURES) + 1)],
           "columns": 2, "exit_action": {"label": {"text": "Fermer"}}}
s = snbt(d_liste).replace("§D", "$(d)")
for i in range(1, len(CREATURES) + 1):
    s = s.replace(f'"§L{i}"', f"$(l{i})")
w(F + "ui/liste_m.mcfunction", "$dialog show @s " + s)

RETOUR = bouton({"text": "◀ Retour"}, 1, 120)
for c in CREATURES:
    k = c["id"]
    inconnu = {"type": "minecraft:multi_action", "title": {"text": "???", "color": "dark_gray", "bold": True},
               "can_close_with_escape": True, "pause": False,
               "body": [msg({"text": "Tu n'as encore jamais vaincu cette créature.", "color": "gray"}),
                        msg([{"text": "Indice : ", "color": "dark_red"}, {"text": c["ou"], "color": "gray"}])],
               "actions": [RETOUR], "exit_action": {"label": {"text": "Fermer"}}}
    fiche = {"type": "minecraft:multi_action", "title": {"text": c["nom"], "color": c["couleur"], "bold": True},
             "can_close_with_escape": True, "pause": False,
             "body": [msg({"text": c["desc"], "color": "white"}),
                      msg([{"text": "Où : ", "color": "dark_red"}, {"text": c["ou"], "color": "gray"}]),
                      msg([{"text": "Danger : ", "color": "dark_red"}, {"text": c["comportement"], "color": "gray"}]),
                      msg([{"text": "Vaincue : ", "color": "dark_red"}, {"text": "§N fois", "color": "white"}]),
                      msg([{"text": f"✔ {PALIERS[0]} : fiche découverte\n", "color": "green"},
                           {"text": f"§P2 {PALIERS[1]} : trophée (tête de {c['nom']})\n", "color": "§C2"},
                           {"text": f"§P3 {PALIERS[2]} : titre « {c['titre']} »", "color": "§C3"}])],
             "actions": [RETOUR], "exit_action": {"label": {"text": "Fermer"}}}
    fs = snbt(fiche)
    for a, b in (("§N", "$(n)"), ("§P2", "$(p2)"), ("§P3", "$(p3)"), ("§C2", "$(c2)"), ("§C3", "$(c3)")):
        fs = fs.replace(a, b)
    lignes = [f"execute unless score @s hr.k.{k} matches 1.. run return run dialog show @s {snbt(inconnu)}",
              f"execute store result storage horreur:ui f.n int 1 run scoreboard players get @s hr.k.{k}",
              'data modify storage horreur:ui f merge value {p2:"✖",c2:"dark_gray",p3:"✖",c3:"dark_gray"}',
              f'execute if score @s hr.k.{k} matches {PALIERS[1]}.. run data modify storage horreur:ui f merge value {{p2:"✔",c2:"green"}}',
              f'execute if score @s hr.k.{k} matches {PALIERS[2]}.. run data modify storage horreur:ui f merge value {{p3:"✔",c3:"gold"}}',
              f"function horreur:ui/fiche/{k}_m with storage horreur:ui f"]
    w(F + f"ui/fiche/{k}.mcfunction", "\n".join(lignes))
    w(F + f"ui/fiche/{k}_m.mcfunction", "$dialog show @s " + fs)

# ---------------------------------------------------------------------------------------------
w(F + "desinstaller.mcfunction", "\n".join(
    ["# /function horreur:desinstaller  puis  /datapack disable \"file/horreur.zip\"",
     "execute as @e[tag=hr.e] run tp @s ~ -1000 ~", "kill @e[tag=hr.e]", "schedule clear horreur:seconde"]
    + [f"scoreboard objectives remove {o}" for o in objs]
    + ["scoreboard objectives remove bestiaire", "data remove storage horreur:t s", "data remove storage horreur:t r",
       "data remove storage horreur:ui m", "data remove storage horreur:ui f",
       'tellraw @s {"text":"[Horreur] Désinstallé. Désactive maintenant le pack : /datapack disable \\"file/horreur.zip\\"","color":"gray"}']))

# ---------------------------------------------------------------------------------------------
n = 0
zp = os.path.join(ICI, "..", "horreur.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, _, fs in os.walk(ROOT):
        for fn in sorted(fs):
            full = os.path.join(dp, fn)
            z.write(full, os.path.relpath(full, ROOT).replace(os.sep, "/"))
            n += 1
print("fichiers :", n)

# Le resource pack (assets/horreur) est regenere avec le datapack
import resourcepack
resourcepack.generer()

# -*- coding: utf-8 -*-
# Générateur du datapack Commerce (Minecraft Java 26.x, vanilla).
# Écrit le pack décompressé dans ../build/commerce_datapack et le zip dans ../commerce.zip.
# Dépend du pack Métiers (scores m.id, m.<métier>_lvl, m.cr_<métier>, m.heure, police metiers:icones).
import os, sys, json, shutil, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from catalogue import ACHAT, CATEGORIES, ITEMS, RARES

ROOT = os.path.join(HERE, "..", "build", "commerce_datapack")
NS = "commerce"
F = f"data/{NS}/function/"
VERSION = 16
if os.path.exists(ROOT):
    shutil.rmtree(ROOT)

GLY = json.load(open(os.path.join(HERE, "..", "..", "metiers", "sources", "glyphes.json"), encoding="utf-8"))
ECU = "\ue010"   # pièce d'Écu : glyphe de la police commerce:recette (resource pack)
ECU_C = f'{{text:"{ECU}",font:"commerce:recette",color:"white",bold:false}}'


def w(path, txt):
    if isinstance(txt, list):
        txt = "\n".join(txt)
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(txt.strip() + "\n")


def wj(path, obj):
    w(path, json.dumps(obj, ensure_ascii=False, indent=2))


def T(text, col="white", bold=False):
    """Composant de texte en SNBT (dialogues, tellraw). Le symbole ECU devient la pièce dessinée du resource pack."""
    b = "true" if bold else "false"
    if ECU in text:
        parts = text.split(ECU)
        kids = []
        for k, p in enumerate(parts):
            if p:
                kids.append(f'{{text:"{p}"}}')
            if k < len(parts) - 1:
                kids.append(ECU_C)
        return f'{{text:"",color:"{col}",bold:{b},italic:false,extra:[{",".join(kids)}]}}'
    return f'{{text:"{text}",color:"{col}",bold:{b},italic:false}}'


def G(name, col="white"):
    """Icône de la police du pack Métiers."""
    return f'{{text:"{GLY[name]}",font:"metiers:icones",color:"{col}",bold:false,italic:false}}'


def L(*parts):
    """Liste de composants, précédée d'un parent vide pour ne pas hériter du style du premier."""
    return "[" + ",".join(['{text:""}'] + list(parts)) + "]"


def btn(label, val, width=150, tip=None):
    s = f"{{label:{label},width:{width}"
    if tip:
        s += f',tooltip:{{text:"{tip}"}}'
    return s + f',action:{{type:"run_command",command:"trigger commerce set {val}"}}}}'


PREFIX = '{text:"[Commerce] ",color:"gold",bold:false,italic:false}'


def say(txt, col="gray", who="@s"):
    return f"tellraw {who} {L(PREFIX, T(txt, col))}"


JOBS = [("b", "Bûcheron", "gold"), ("f", "Fermier", "green"), ("m", "Mineur", "gray"), ("c", "Chasseur", "red"),
        ("p", "Pêcheur", "aqua"), ("e", "Éleveur", "light_purple"), ("n", "Enchanteur", "dark_purple"),
        ("x", "Explorateur", "blue"), ("t", "Marchand", "dark_green"), ("k", "Bâtisseur", "#C08850")]
JIDX = {j: k for k, (j, _, _) in enumerate(JOBS, 1)}
JNAME = {j: n for j, n, _ in JOBS}

# ---------------------------------------------------------------- catalogue à plat (catégories rares en dernier)
CATNAME = {c: n for c, n, *_ in CATEGORIES}
ITL = []
for cat in sorted(ITEMS, key=lambda c: (c in RARES, c)):
    for iid, nom, prix, vol, mj in ITEMS[cat]:
        ITL.append({"id": iid, "n": nom, "b": round(prix * 100), "V": vol, "mj": JIDX.get(mj, 0),
                    "rare": cat in RARES, "cat": cat})
for k, it in enumerate(ITL, 1):
    it["i"] = k
    it["i3"] = f"{k:03d}"
NIT = len(ITL)
NCOM = sum(1 for it in ITL if not it["rare"])   # les objets achetables sont les NCOM premiers
assert all(not it["rare"] for it in ITL[:NCOM]) and NIT < 1000
assert len({it["id"] for it in ITL}) == NIT, "objet en double dans le catalogue"
H = lambda it: f'#{it["id"]}'   # porteur de score de l'objet

# =====================================================================
# PACK, CHARGEMENT, TICK
# =====================================================================
wj("pack.mcmeta", {"pack": {"description": "Commerce : Écus, marché, bourse, comptoirs", "min_format": 84, "max_format": 200}})
wj("data/minecraft/tags/function/load.json", {"values": [f"{NS}:load"]})
wj("data/minecraft/tags/function/tick.json", {"values": [f"{NS}:tick"]})

PLAYER_OBJ = ["c.ecus", "c.cts", "c.deb", "c.cmpt", "c.ser", "c.own", "c.nom", "c.init", "c.vu", "c.tv", "c.ta", "c.ncr"]
PLAYER_OBJ += [f"c.pp_{j}" for j, *_ in JOBS] + [f"c.dd_{j}" for j, *_ in JOBS] + ["c.dall", "c.wd", "c.wk", "c.bk", "c.init2", "c.kb"]
ITEM_OBJ = ["c.p", "c.h", "c.vs", "c.as", "c.ev", "c.x", "c.jv", "c.ja"]
LD = [f"scoreboard objectives add {o} dummy" for o in PLAYER_OBJ + ITEM_OBJ + ["c.t", "c.g"]]
LD += ["scoreboard objectives add commerce trigger",
       "scoreboard objectives add c.oeuf minecraft.used:minecraft.villager_spawn_egg",
       "scoreboard objectives add c.craft minecraft.crafted:minecraft.villager_spawn_egg"]
for c in (2, 5, 7, 10, 12, 100, 105, 250, 500, 1000, 1000000, -1):
    LD.append(f"scoreboard players set #{c} c.g {c}")
LD.append(f"scoreboard players set #achat c.g {ACHAT}")
for o in ("#dec", "#hr", "#cv", "#t", "#evi", "#evt", "#semp"):
    LD.append(f"scoreboard players add {o} c.g 0")
LD.append("execute unless score #indice c.g matches 1.. run scoreboard players set #indice c.g 1000")
for o in ():
    LD.append(f"scoreboard players add {o} c.g 0")
for it in ITL:
    LD += [f"scoreboard players add {H(it)} {o} 0" for o in ("c.p", "c.h", "c.vs", "c.as", "c.ev")]
LD += [f'execute unless data storage {NS}:g evtxt run data modify storage {NS}:g evtxt set value ""',
       f"execute unless data storage {NS}:j l run data modify storage {NS}:j l set value []",
       f'data modify storage {NS}:t msg set value ""']
LD += ["execute unless score #tableau c.g matches 0..1 run scoreboard players set #tableau c.g 1",
       f"execute if score #tableau c.g matches 1 run function {NS}:tableau/on"]
LD.append(f"function {NS}:prive/load")
LD.append(f"function {NS}:hud/load")
LD.append(f"function {NS}:stat/load")
LD.append(f"function {NS}:spawner/load")
LD += [f"function {NS}:guilde/load", f"function {NS}:banque/load", f"function {NS}:hdv/load", f"function {NS}:boutique/load", "scoreboard objectives add c.gd dummy",
       "scoreboard players set #50 c.g 50", "scoreboard players set #95 c.g 95"]
w(F + "load.mcfunction", LD)
# Barre latérale : le seul affichage permanent fiable en vanilla. Elle montre le solde de chaque joueur,
# trié du plus riche au moins riche (les fortunes sont publiques), avec le préfixe de titre de Métiers.
w(F + "tableau/on.mcfunction", [
    "scoreboard players set #tableau c.g 1", "scoreboard objectives setdisplay sidebar c.ecus",
    f'scoreboard objectives modify c.ecus displayname [{{text:""}},{{text:"{ECU}",font:"commerce:recette",color:"white"}},{{text:" Écus ",color:"gold",bold:true}}]',
    'scoreboard objectives modify c.ecus numberformat styled {color:"yellow",bold:true}'])
w(F + "tableau/off.mcfunction", ["scoreboard players set #tableau c.g 0", "scoreboard objectives setdisplay sidebar"])

w(F + "tick.mcfunction", [
    "scoreboard players enable @a commerce",
    f"execute as @a[scores={{commerce=1..}}] at @s run function {NS}:trigger/entree",
    f"execute as @a[scores={{commerce=..-1}}] at @s run function {NS}:trigger/entree",
    f"execute as @e[type=minecraft:villager,tag=commerce.nouveau] at @s run function {NS}:comptoir/pose",
    f"execute as @e[type=minecraft:interaction,tag=commerce.clic] if data entity @s interaction run function {NS}:comptoir/clic_i",
    "execute as @e[type=minecraft:interaction,tag=commerce.clic] if data entity @s attack run data remove entity @s attack",
    "scoreboard players set @a[scores={c.oeuf=1..}] c.oeuf 0",
    f"execute as @a run function {NS}:hud/joueur",
    f"function {NS}:spawner/tick",
    "scoreboard players add #pt c.g 1",
    f"execute if score #pt c.g matches 2.. run function {NS}:prive/tick",
    "execute if entity @a run scoreboard players add #t c.g 1",
    f"execute if score #t c.g matches 20.. run function {NS}:seconde"])

w(F + "seconde.mcfunction", [
    "scoreboard players set #t c.g 0",
    f"function {NS}:prive/seconde",
    f"function {NS}:stat/seconde",
    f"function {NS}:spawner/seconde",
    f"execute as @a at @s run function {NS}:joueur/seconde",
    "execute as @e[type=minecraft:villager,tag=commerce.comptoir] at @s run rotate @s facing entity @p[distance=..6,gamemode=!spectator] eyes",
    "scoreboard players add #cv c.g 1",
    f"execute if score #cv c.g matches 5.. run function {NS}:comptoir/verif_tous",
    "scoreboard players add #dec c.g 1",
    f"execute if score #dec c.g matches 120.. run function {NS}:marche/detente",
    "scoreboard players add #hr c.g 1",
    f"execute if score #hr c.g matches 3600.. run function {NS}:marche/heure",
    # nouvelle semaine de Métiers : son compteur #semaine repart à zéro
    "scoreboard players operation #sem c.t = #semp c.g",
    "execute store result score #semp c.g run scoreboard players get #semaine m.defi",
    f"execute if score #semp c.g < #sem c.t run function {NS}:marche/semaine"])

w(F + "version.mcfunction", say(f"Version {VERSION} : Écus, comptoirs, marché de {NIT} objets à prix dynamiques, bourse, graphiques, fortunes, cristaux, spawners, coffres privés, banque, hôtel des ventes, magasins.", "gold"))

# =====================================================================
# JOUEURS : arrivée, nom, primes de palier
# =====================================================================
w(F + "joueur/seconde.mcfunction", [
    f"execute unless score @s c.vu matches 1 run function {NS}:joueur/arrivee",
    f"execute unless score @s c.nom matches 1 run function {NS}:joueur/inscrire",
    f"execute unless score @s c.init matches 1 run function {NS}:joueur/init_paliers",
    f"execute if score @s c.craft matches 1.. unless score @s c.deb matches 1 run function {NS}:debloque",
    f"function {NS}:joueur/paliers",
    f"execute unless score @s c.init2 matches 1 run function {NS}:joueur/evts_init",
    f"function {NS}:joueur/evts", f"function {NS}:guilde/sync"])
w(F + "joueur/arrivee.mcfunction", [f"scoreboard players add @s {o} 0" for o in PLAYER_OBJ] + [
    f"recipe give @s {NS}:oeuf", "scoreboard players set @s c.vu 1",
    f"execute unless score @s c.gd matches 1 run function {NS}:serveur/bienvenue"])

# Le nom du joueur n'existe dans aucune donnée lisible : on le récupère sur une tête de joueur générée
# par une table de butin, posée un instant dans un item_display.
wj(f"data/{NS}/loot_table/tete.json", {"type": "minecraft:generic", "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": "minecraft:player_head",
   "modifier": [{"type": "minecraft:fill_player_head", "entity": "this"}]}]}]})
w(F + "joueur/inscrire.mcfunction", [
    "summon minecraft:item_display ~ ~ ~ {Tags:[\"commerce.tete\"]}",
    f"loot replace entity @e[type=minecraft:item_display,tag=commerce.tete,limit=1,sort=nearest] contents loot {NS}:tete",
    f'data modify storage {NS}:t nom set value "Joueur"',
    f'data modify storage {NS}:t nom set from entity @e[type=minecraft:item_display,tag=commerce.tete,limit=1,sort=nearest] item.components."minecraft:profile".name',
    "kill @e[type=minecraft:item_display,tag=commerce.tete]",
    "scoreboard players set @s c.nom 1",
    f'execute if data storage {NS}:t {{nom:"Joueur"}} run return 0',
    f"execute store result storage {NS}:t nj.id int 1 run scoreboard players get @s m.id",
    f"data modify storage {NS}:t nj.nom set from storage {NS}:t nom",
    f"function {NS}:joueur/registre with storage {NS}:t nj"])
w(F + "joueur/registre.mcfunction", [
    f'$data remove storage {NS}:j l[{{nom:"$(nom)"}}]',
    f'$data modify storage {NS}:j l append value {{id:$(id),nom:"$(nom)"}}'])

PL = []
for j, nom, col in JOBS:
    PL += [f"scoreboard players add @s c.pp_{j} 0", f"scoreboard players set #k c.t 0", f"scoreboard players operation #k c.t = @s m.{j}_lvl",
           "scoreboard players operation #k c.t /= #10 c.g",
           f"execute if score #k c.t > @s c.pp_{j} run function {NS}:prime/palier_{j}",
           f"execute if score #k c.t < @s c.pp_{j} run scoreboard players operation @s c.pp_{j} = #k c.t"]
    w(F + f"prime/palier_{j}.mcfunction", [
        f"scoreboard players add @s c.pp_{j} 1",
        f"scoreboard players operation #x c.t = @s c.pp_{j}", "scoreboard players operation #x c.t *= #250 c.g",
        "scoreboard players operation @s c.ecus += #x c.t",
        f'tellraw @s {L(PREFIX, T("Prime de palier " + nom + " : +", col), "{score:{name:\"#x\",objective:\"c.t\"},color:\"gold\"}", T(" " + ECU, "gold"))}',
        "playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 0.8"])
w(F + "joueur/paliers.mcfunction", PL)
IP = []
for j, *_ in JOBS:
    IP += ["scoreboard players set #k c.t 0", f"scoreboard players operation #k c.t = @s m.{j}_lvl",
           "scoreboard players operation #k c.t /= #10 c.g", f"scoreboard players operation @s c.pp_{j} = #k c.t"]
w(F + "joueur/init_paliers.mcfunction", IP + ["scoreboard players set @s c.init 1"])

# primes branchées sur les évènements du pack Métiers (tags #metiers:evt/...)
PRIMES = {"defi_jour": (150, "défi du jour"), "defis_tous": (300, "tous les défis du jour"),
          "defi_semaine": (1500, "défi de la semaine"), "defi_collectif": (400, "défi collectif"), "boss": (600, "boss vaincu")}
for k, (val, lib) in PRIMES.items():
    lines = [f"scoreboard players add @s c.ecus {val}",
             f'tellraw @s {L(PREFIX, T(f"+{val} {ECU}", "gold", True), T(" (" + lib + ")", "gray"))}']
    w(F + f"prime/{k}.mcfunction", lines)

# Commerce ne modifie pas Métiers : il lit ses scores chaque seconde et paie quand ils changent.
#   m.dd_<métier> = 1 défi du jour réussi, m.wd = 1 défi de la semaine, m.wk = 1 défi collectif,
#   m.bk1..5 = boss vaincus, #semaine m.defi repart à 0 à la nouvelle semaine.
BKSUM = ["scoreboard players set #s c.t 0"] + [f"scoreboard players operation #s c.t += @s m.bk{k}" for k in range(1, 6)]
EV = []
for j, *_ in JOBS:
    EV += [f"execute if score @s m.dd_{j} matches 1 unless score @s c.dd_{j} matches 1 run function {NS}:prime/defi_jour",
           f"scoreboard players set @s c.dd_{j} 0", f"execute if score @s m.dd_{j} matches 1 run scoreboard players set @s c.dd_{j} 1"]
EV += ["scoreboard players set #n c.t 0"] + [f"execute if score @s c.dd_{j} matches 1 run scoreboard players add #n c.t 1" for j, *_ in JOBS]
EV += [f"execute if score #n c.t matches {len(JOBS)} unless score @s c.dall matches 1 run function {NS}:prime/defis_tous",
       "scoreboard players set @s c.dall 0", f"execute if score #n c.t matches {len(JOBS)} run scoreboard players set @s c.dall 1",
       f"execute if score @s m.wd matches 1 unless score @s c.wd matches 1 run function {NS}:prime/defi_semaine",
       "scoreboard players set @s c.wd 0", "execute if score @s m.wd matches 1 run scoreboard players set @s c.wd 1",
       f"execute if score @s m.wk matches 1 unless score @s c.wk matches 1 run function {NS}:prime/defi_collectif",
       "scoreboard players set @s c.wk 0", "execute if score @s m.wk matches 1 run scoreboard players set @s c.wk 1"]
EV += BKSUM + [f"execute if score #s c.t > @s c.bk run function {NS}:prime/boss", "scoreboard players operation @s c.bk = #s c.t"]
w(F + "joueur/evts.mcfunction", EV)
EI = []
for j, *_ in JOBS:
    EI += [f"scoreboard players set @s c.dd_{j} 0", f"execute if score @s m.dd_{j} matches 1 run scoreboard players set @s c.dd_{j} 1"]
EI += ["scoreboard players set @s c.dall 1", "scoreboard players set @s c.wd 0", "execute if score @s m.wd matches 1 run scoreboard players set @s c.wd 1",
       "scoreboard players set @s c.wk 0", "execute if score @s m.wk matches 1 run scoreboard players set @s c.wk 1"]
EI += BKSUM + ["scoreboard players operation @s c.bk = #s c.t", "scoreboard players set @s c.init2 1"]
w(F + "joueur/evts_init.mcfunction", EI)

# =====================================================================
# OeUF DU COMPTOIR, DÉBLOCAGE
# =====================================================================
EGG_ENTITY_SNBT = ('{id:"minecraft:villager",Tags:["commerce.nouveau"],NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,'
                   'CustomNameVisible:1b,VillagerData:{type:"minecraft:plains",profession:"minecraft:none",level:1},Offers:{Recipes:[]}}')
EGG_ENTITY_JSON = {"id": "minecraft:villager", "Tags": ["commerce.nouveau"], "NoAI": True, "Invulnerable": True,
                   "PersistenceRequired": True, "Silent": True, "CustomNameVisible": True,
                   "VillagerData": {"type": "minecraft:plains", "profession": "minecraft:none", "level": 1},
                   "Offers": {"Recipes": []}}
EGG_NAME = {"text": "Oeuf de comptoir", "color": "gold", "bold": True, "italic": False}
EGG_LORE = [{"text": "Pose-le à ta base : c'est ton comptoir de commerce.", "color": "gray", "italic": False},
            {"text": "Un seul par joueur. Touche G pour le déplacer.", "color": "gray", "italic": False}]
wj(f"data/{NS}/recipe/oeuf.json", {
    "type": "minecraft:crafting_shaped", "category": "misc",
    "pattern": ["GEG", "ECE", "GEG"],  # recette simplifiée (24/11/2026) : 4 émeraudes, 4 lingots d'or, un tonneau
    "key": {"E": "minecraft:emerald", "G": "minecraft:gold_ingot", "C": "minecraft:barrel"},
    "result": {"id": "minecraft:villager_spawn_egg", "count": 1, "components": {
        "minecraft:custom_name": EGG_NAME, "minecraft:lore": EGG_LORE, "minecraft:entity_data": EGG_ENTITY_JSON,
        "minecraft:custom_data": {"commerce": "oeuf"}, "minecraft:max_stack_size": 1, "minecraft:rarity": "epic",
        "minecraft:enchantment_glint_override": True}}})
sn = lambda d: json.dumps(d, ensure_ascii=False).replace('"text"', "text").replace('"color"', "color").replace('"bold"', "bold").replace('"italic"', "italic")
w(F + "oeuf/donner.mcfunction",
  f"give @s minecraft:villager_spawn_egg[minecraft:custom_name={sn(EGG_NAME)},minecraft:lore={sn(EGG_LORE)},"
  f"minecraft:entity_data={EGG_ENTITY_SNBT},minecraft:custom_data={{commerce:\"oeuf\"}},minecraft:max_stack_size=1,"
  f'minecraft:rarity="epic",minecraft:enchantment_glint_override=true] 1')

w(F + "debloque.mcfunction", [
    f"execute if score @s c.deb matches 1 run return 0",
    "scoreboard players set @s c.deb 1",
    f'tellraw @a {L(PREFIX, "{selector:\"@s\",color:\"white\"}", T(" ouvre son comptoir : le Commerce est débloqué !", "gold", True))}',
    say("Pose l'oeuf à ta base. Touche G, Commerce : marché, bourse, banque et cristaux, depuis n'importe où.", "yellow"),
    "playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1"])

# =====================================================================
# COMPTOIR : pose, refus, déplacement, vérification, clic
# =====================================================================
w(F + "comptoir/pose.mcfunction", [
    "tag @s remove commerce.nouveau", "tag @s add commerce.pose",
    "execute unless entity @a[distance=..8,scores={c.oeuf=1..}] run return run kill @s",
    f"execute as @a[distance=..8,scores={{c.oeuf=1..}},limit=1,sort=nearest] at @s run function {NS}:comptoir/proprio",
    "tag @s remove commerce.pose"])
w(F + "comptoir/proprio.mcfunction", [
    f"execute if score @s c.cmpt matches 1 run return run function {NS}:comptoir/refus",
    "scoreboard players add @s c.ser 1",
    f"function {NS}:comptoir/ser_maj",
    "scoreboard players operation @e[type=minecraft:villager,tag=commerce.pose,limit=1] c.ser = @s c.ser",
    "scoreboard players operation @e[type=minecraft:villager,tag=commerce.pose,limit=1] c.own = @s m.id",
    "scoreboard players set @s c.cmpt 1", "scoreboard players set @s c.deb 1",
    f"function {NS}:joueur/inscrire",
    f"execute as @e[type=minecraft:villager,tag=commerce.pose,limit=1] run function {NS}:comptoir/nommer with storage {NS}:t",
    "execute as @e[type=minecraft:villager,tag=commerce.pose,limit=1] run data modify entity @s Age set value 0",
    "tag @e[type=minecraft:villager,tag=commerce.pose,limit=1] add commerce.comptoir",
    "execute at @e[type=minecraft:villager,tag=commerce.pose,limit=1] run summon minecraft:interaction ~ ~ ~ {Tags:[\"commerce.clic\"],width:0.9f,height:2.0f,response:1b}",
    "execute at @e[type=minecraft:villager,tag=commerce.pose,limit=1] run particle minecraft:happy_villager ~ ~1 ~ 0.5 1 0.5 0 30",
    "playsound minecraft:entity.villager.celebrate master @s ~ ~ ~ 1 1",
    say("Ton comptoir est posé. Tout le monde peut l'utiliser (clic droit). Pour le déplacer : touche G, Commerce, Mon comptoir.", "green")])
w(F + "comptoir/nommer.mcfunction", '$data modify entity @s CustomName set value {text:"Comptoir de $(nom)",color:"gold",bold:true}')
w(F + "comptoir/ser_maj.mcfunction", [
    f"execute store result storage {NS}:t o.id int 1 run scoreboard players get @s m.id",
    f"function {NS}:comptoir/ser_maj_m with storage {NS}:t o"])
w(F + "comptoir/ser_maj_m.mcfunction", "$scoreboard players operation #o$(id) c.ser = @s c.ser")
w(F + "comptoir/refus.mcfunction", [
    "kill @e[type=minecraft:villager,tag=commerce.pose,limit=1]",
    f"execute unless entity @s[gamemode=creative] run function {NS}:oeuf/donner",
    say("Tu as déjà un comptoir. Pour le changer de place : touche G, Commerce, Mon comptoir. L'oeuf t'est rendu.", "red")])
w(F + "comptoir/verif_tous.mcfunction", [
    "scoreboard players set #cv c.g 0",
    f"execute as @e[type=minecraft:villager,tag=commerce.comptoir] at @s run function {NS}:comptoir/verif",
    "execute as @e[type=minecraft:interaction,tag=commerce.clic] at @s unless entity @e[type=minecraft:villager,tag=commerce.comptoir,distance=..1] run kill @s"])
w(F + "comptoir/verif.mcfunction", [
    f"execute store result storage {NS}:t o.id int 1 run scoreboard players get @s c.own",
    f"function {NS}:comptoir/verif_m with storage {NS}:t o"])
w(F + "comptoir/verif_m.mcfunction", f"$execute unless score @s c.ser = #o$(id) c.ser run function {NS}:comptoir/retirer")
w(F + "comptoir/retirer.mcfunction", [
    "kill @e[type=minecraft:interaction,tag=commerce.clic,distance=..1]",
    "particle minecraft:poof ~ ~1 ~ 0.3 0.6 0.3 0.02 20", "tp @s ~ -400 ~", "kill @s"])
w(F + "comptoir/deplacer.mcfunction", [
    f"execute unless score @s c.cmpt matches 1 run return run {say('Tu n’as pas de comptoir posé. Crafte un oeuf de comptoir pour en avoir un.', 'red')}",
    "scoreboard players operation #pid c.t = @s m.id",
    f"execute as @e[type=minecraft:villager,tag=commerce.comptoir] if score @s c.own = #pid c.t at @s run function {NS}:comptoir/retirer",
    "scoreboard players add @s c.ser 1", f"function {NS}:comptoir/ser_maj",
    "scoreboard players set @s c.cmpt 0", f"function {NS}:oeuf/donner",
    "playsound minecraft:item.bundle.insert master @s ~ ~ ~ 1 1",
    say("Ton comptoir est rangé dans ton inventaire : pose l'oeuf où tu veux.", "green")])
w(F + "comptoir/clic_i.mcfunction", [
    f"execute on target run function {NS}:comptoir/clic",
    "data remove entity @s interaction", "data remove entity @s attack"])
w(F + "comptoir/clic.mcfunction", [
    f"execute unless score @s c.deb matches 1 run return run function {NS}:page/verrou",
    f"function {NS}:page/accueil"])

# =====================================================================
# OBJETS : chargement et sauvegarde des scores d'un objet (#i = numéro)
# =====================================================================
# blocs posables achetés : crédit c.kb lu par Métiers (Bâtisseur : +2 XP par bloc du shop posé)
_BLOCS = set(json.load(open(os.path.join(HERE, "donnees_26.1.json"), encoding="utf-8")).get("blocs", []))
POSABLE = lambda it: it["id"] in _BLOCS and it["cat"] not in (10, 11, 12, 13, 15)
for it in ITL:
    cn = CATNAME[it["cat"]]
    w(F + f"i/{it['i']}/charger.mcfunction", [
        f"scoreboard players set #b c.t {it['b']}", f"scoreboard players set #V c.t {it['V']}",
        f"scoreboard players set #mj c.t {it['mj']}", f"scoreboard players set #rare c.t {1 if it['rare'] else 0}",
        f"scoreboard players set #blk c.t {1 if POSABLE(it) else 0}",
        f"scoreboard players set #cher c.t {1 if (POSABLE(it) or it['cat'] == 8) else 0}",
        f'data modify storage {NS}:t it set value {{id:"{it["id"]}",n:"{it["n"]}",i3:"{it["i3"]}",cn:"{cn}",cb:{100 + it["cat"]}}}',
        f"scoreboard players operation #p c.t = {H(it)} c.p", f"scoreboard players operation #h c.t = {H(it)} c.h",
        f"scoreboard players operation #vs c.t = {H(it)} c.vs", f"scoreboard players operation #as c.t = {H(it)} c.as",
        f"scoreboard players operation #e c.t = {H(it)} c.ev", "scoreboard players add #e c.t 1000"])
    w(F + f"i/{it['i']}/sauver.mcfunction", [
        f"scoreboard players operation {H(it)} c.p = #p c.t", f"scoreboard players operation {H(it)} c.h = #h c.t",
        f"scoreboard players operation {H(it)} c.vs = #vs c.t", f"scoreboard players operation {H(it)} c.as = #as c.t",
        f"scoreboard players operation {H(it)} c.ev = #e c.t", f"scoreboard players remove {H(it)} c.ev 1000"])
for act in ("charger", "sauver"):
    w(F + f"item/{act}.mcfunction", [
        f"execute store result storage {NS}:t k.n int 1 run scoreboard players get #i c.t",
        f"function {NS}:item/{act}_m with storage {NS}:t k"])
    w(F + f"item/{act}_m.mcfunction", f"$function {NS}:i/$(n)/{act}")
w(F + "item/marquer.mcfunction", "$scoreboard players set #$(id) c.x 1")

# =====================================================================
# PRIX
#   #pm : pression au milieu de l'opération (-300 à 700). Prix = base x (1000 - pression) / 1000.
#   #e  : évènement de marché (1000 = normal). #bon : bonus de métier du joueur (1000 = aucun).
# =====================================================================
w(F + "prix/mid.mcfunction", [
    "scoreboard players operation #pm c.t = #d c.t", "scoreboard players operation #pm c.t /= #2 c.g",
    "scoreboard players operation #pm c.t += #p c.t",
    "execute if score #pm c.t matches 701.. run scoreboard players set #pm c.t 700",
    "execute if score #pm c.t matches ..-301 run scoreboard players set #pm c.t -300"])
w(F + "prix/vente.mcfunction", [
    "scoreboard players set #f c.t 1000", "scoreboard players operation #f c.t -= #pm c.t",
    "scoreboard players operation #u c.t = #b c.t", "scoreboard players operation #u c.t *= #f c.t",
    "scoreboard players operation #u c.t /= #1000 c.g", "scoreboard players operation #u c.t *= #e c.t",
    "scoreboard players operation #u c.t /= #1000 c.g",
    "execute if score #u c.t matches ..0 run scoreboard players set #u c.t 1",
    "scoreboard players operation #u0 c.t = #u c.t",
    "scoreboard players operation #u c.t *= #bon c.t", "scoreboard players operation #u c.t /= #1000 c.g",
    "execute if score #u c.t matches ..0 run scoreboard players set #u c.t 1",
    # rachat : ne descend jamais sous ACHAT x la base (ni marché saturé, ni krach), monte avec la demande et les pénuries
    "scoreboard players operation #f c.t = #pm c.t", "execute if score #f c.t matches 1.. run scoreboard players set #f c.t 0",
    "scoreboard players operation #f c.t *= #-1 c.g", "scoreboard players add #f c.t 1000",
    "scoreboard players operation #a c.t = #b c.t", "scoreboard players operation #a c.t *= #f c.t",
    "scoreboard players operation #a c.t /= #1000 c.g", "scoreboard players operation #f c.t = #e c.t",
    "execute if score #f c.t matches ..999 run scoreboard players set #f c.t 1000",
    "scoreboard players operation #a c.t *= #f c.t", "scoreboard players operation #a c.t /= #1000 c.g",
    "scoreboard players operation #a c.t *= #achat c.g",
    # 26/11/2026 : blocs posables et minerais/métaux s'achètent 2 fois plus cher (rachat 20 x la base au lieu de 10), la revente ne change pas
    "execute if score #cher c.t matches 1 run scoreboard players operation #a c.t *= #2 c.g"])
BO = ["scoreboard players set #bon c.t 1000", "scoreboard players set #lv c.t 0"]
BO += [f"execute if score #mj c.t matches {JIDX[j]} run scoreboard players operation #lv c.t = @s m.{j}_lvl" for j, *_ in JOBS]
BO += ["execute if score #lv c.t matches 101.. run scoreboard players set #lv c.t 100",
       "execute if score #lv c.t matches ..-1 run scoreboard players set #lv c.t 0",
       "scoreboard players operation #lv c.t *= #5 c.g", "scoreboard players operation #bon c.t += #lv c.t",
       "execute if score #mj c.t matches 1.. if score #mj c.t = #job m.heure run scoreboard players add #bon c.t 250",
       # synergie Négoce de Métiers (Mineur + Marchand niveau 50) : +5 %
       "execute if score @s m.syn matches 1 run scoreboard players add #bon c.t 50",
       # Métiers 26 : Vendeur, Vendeur aguerri, Grossiste (+3, +6, +10 %)
       "scoreboard players operation #bon c.t += @s m.tmb"]
w(F + "prix/bonus.mcfunction", BO)
w(F + "prix/sans_bonus.mcfunction", "scoreboard players set #bon c.t 1000")


def fmt(dest, key):
    """Formate le score #x (centièmes d'Écu) dans dest.<key>e, <key>z, <key>c : affichage « $(ke),$(kz)$(kc) »."""
    return [f"function {NS}:fmt/centi",
            f"data modify storage {dest} {key}e set from storage {NS}:t f.e",
            f"data modify storage {dest} {key}z set from storage {NS}:t f.z",
            f"data modify storage {dest} {key}c set from storage {NS}:t f.c"]


w(F + "fmt/centi.mcfunction", [
    "scoreboard players operation #fe c.t = #x c.t", "scoreboard players operation #fe c.t /= #100 c.g",
    "scoreboard players operation #fc c.t = #x c.t", "scoreboard players operation #fc c.t %= #100 c.g",
    f"execute store result storage {NS}:t f.e int 1 run scoreboard players get #fe c.t",
    f"execute store result storage {NS}:t f.c int 1 run scoreboard players get #fc c.t",
    f'data modify storage {NS}:t f.z set value ""',
    f'execute if score #fc c.t matches 0..9 run data modify storage {NS}:t f.z set value "0"'])
w(F + "fmt/solde.mcfunction", [
    f"execute store result storage {NS}:t s.e int 1 run scoreboard players get @s c.ecus",
    f"execute store result storage {NS}:t s.c int 1 run scoreboard players get @s c.cts",
    f'data modify storage {NS}:t s.z set value ""',
    f'execute if score @s c.cts matches 0..9 run data modify storage {NS}:t s.z set value "0"'])
SOLDE = lambda st: [f"function {NS}:fmt/solde", f"data modify storage {st} se set from storage {NS}:t s.e",
                    f"data modify storage {st} sz set from storage {NS}:t s.z", f"data modify storage {st} sc set from storage {NS}:t s.c"]
SOLDE_TXT = f'{T("Solde : ", "gray")},{T("$(se),$(sz)$(sc) " + ECU, "gold", True)}'

w(F + "fmt/tendance.mcfunction", [
    f'data modify storage {NS}:t tr set value "▬"', f'data modify storage {NS}:t trc set value "gray"',
    "execute unless score #h c.t matches 1.. run return 0",
    "scoreboard players operation #cu c.t = #u0 c.t", "scoreboard players operation #cu c.t *= #100 c.g",
    "scoreboard players operation #hu c.t = #h c.t", "scoreboard players operation #hu c.t *= #100 c.g",
    "scoreboard players operation #hu c.t += #h c.t", "scoreboard players operation #hu c.t += #h c.t",
    "scoreboard players operation #hu c.t += #h c.t",
    f'execute if score #cu c.t > #hu c.t run data modify storage {NS}:t tr set value "▲"',
    f'execute if score #cu c.t > #hu c.t run data modify storage {NS}:t trc set value "green"',
    "scoreboard players operation #hl c.t = #h c.t", "scoreboard players operation #hl c.t *= #100 c.g",
    "scoreboard players operation #hl c.t -= #h c.t", "scoreboard players operation #hl c.t -= #h c.t",
    "scoreboard players operation #hl c.t -= #h c.t",
    f'execute if score #cu c.t < #hl c.t run data modify storage {NS}:t tr set value "▼"',
    f'execute if score #cu c.t < #hl c.t run data modify storage {NS}:t trc set value "red"'])

# =====================================================================
# OPÉRATIONS : vendre, acheter, créditer
# =====================================================================
# ni objets de pack (outils, trophées du Bestiaire...), ni objets renommés. 24/11/2026 : en 26.3 la description (lore)
# est un composant par défaut (liste vide) sur tous les objets, donc « !minecraft:lore » refusait tout : on exige une
# description vide à la place.
FILTRE = "[!minecraft:custom_data,!minecraft:custom_name,minecraft:lore=[]]"
w(F + "op/compter.mcfunction", f"$return run clear @s minecraft:$(id){FILTRE} 0")
w(F + "op/retirer.mcfunction", f"$clear @s minecraft:$(id){FILTRE} $(q)")
w(F + "op/donner.mcfunction", "$give @s minecraft:$(id) $(q)")
w(F + "op/crediter.mcfunction", [
    "scoreboard players operation #xe c.t = #tot c.t", "scoreboard players operation #xe c.t /= #100 c.g",
    "scoreboard players operation #xc c.t = #tot c.t", "scoreboard players operation #xc c.t %= #100 c.g",
    "scoreboard players operation @s c.ecus += #xe c.t", "scoreboard players operation @s c.cts += #xc c.t",
    "execute if score @s c.cts matches 100.. run scoreboard players add @s c.ecus 1",
    "execute if score @s c.cts matches 100.. run scoreboard players remove @s c.cts 100",
    "scoreboard players operation @s c.tv += #xe c.t"])
w(F + "op/entree.mcfunction", [
    "scoreboard players operation #act c.t = #v c.t", "scoreboard players operation #act c.t /= #1000000 c.g",
    "scoreboard players operation #i c.t = #v c.t", "scoreboard players operation #i c.t %= #1000000 c.g",
    "scoreboard players operation #i c.t /= #1000 c.g",
    "scoreboard players operation #q c.t = #v c.t", "scoreboard players operation #q c.t %= #1000 c.g",
    f"execute unless score #i c.t matches 1..{NIT} run return 0",
    "execute if score #act c.t matches 1..2 unless score #q c.t matches 1..640 run return 0",
    f"execute if score #act c.t matches 1 run function {NS}:op/acheter",
    f"execute if score #act c.t matches 2..3 run function {NS}:op/vendre",
    f"function {NS}:page/item"])
w(F + "op/vendre.mcfunction", [
    f"function {NS}:item/charger",
    f"execute store result score #have c.t run function {NS}:op/compter with storage {NS}:t it",
    "execute if score #act c.t matches 3 run scoreboard players operation #q c.t = #have c.t",
    "execute if score #q c.t matches 641.. run scoreboard players set #q c.t 640",
    "execute if score #q c.t > #have c.t run scoreboard players operation #q c.t = #have c.t",
    f'execute if score #q c.t matches ..0 run return run data modify storage {NS}:t msg set value "Tu n\'en as pas dans ton inventaire (les objets renommés ou spéciaux sont refusés)."',
    "scoreboard players operation #d c.t = #q c.t", "scoreboard players operation #d c.t *= #1000 c.g",
    "scoreboard players operation #d c.t /= #V c.t",
    f"function {NS}:prix/mid", f"function {NS}:prix/bonus", f"function {NS}:prix/vente",
    "scoreboard players operation #tot c.t = #u c.t", "scoreboard players operation #tot c.t *= #q c.t",
    f"execute store result storage {NS}:t it.q int 1 run scoreboard players get #q c.t",
    f"function {NS}:op/retirer with storage {NS}:t it",
    "scoreboard players operation #p c.t += #d c.t",
    "execute if score #p c.t matches 701.. run scoreboard players set #p c.t 700",
    "scoreboard players operation #vs c.t += #q c.t",
    f"function {NS}:item/sauver", f"function {NS}:op/crediter", f"function {NS}:stat/vente with storage {NS}:t it",
    "scoreboard players operation #x c.t = #tot c.t"] + fmt(f"{NS}:t", "m.") + [
    f"data modify storage {NS}:t m.q set from storage {NS}:t it.q",
    f"data modify storage {NS}:t m.n set from storage {NS}:t it.n",
    f"function {NS}:op/msg_vente with storage {NS}:t m",
    f"data modify storage {NS}:t m.n set from storage {NS}:t it.n", f"execute store result storage {NS}:t hl.id int 1 run scoreboard players get @s m.id",
    f'data modify storage {NS}:t hl.col set value "green"', f"function {NS}:banque/hist_txt_vente",
    "playsound minecraft:entity.villager.yes master @s ~ ~ ~ 0.8 1.2",
    "playsound minecraft:block.chain.place master @s ~ ~ ~ 0.6 1.6"])
w(F + "op/msg_vente.mcfunction", [f'$data modify storage {NS}:t msg set value "Vendu : $(q) pour $(e),$(z)$(c) Écus."',
    # 25/11/2026 : le montant aussi dans le chat, pour toi seul (pas pendant un « Tout vendre », qui fait un total)
    '$execute unless score #lot c.t matches 1 run tellraw @s [{"text":"[Commerce] ","color":"green"},{"text":"Vendu : ","color":"gray"},{"text":"$(q) $(n)","color":"white"},{"text":" pour ","color":"gray"},{"text":"+$(e),$(z)$(c) Écus","color":"gold"}]'])
w(F + "op/acheter.mcfunction", [
    f"function {NS}:item/charger",
    f'execute if score #rare c.t matches 1 run return run data modify storage {NS}:t msg set value "Le serveur ne revend pas cet objet, il le rachète seulement."',
    "scoreboard players operation #d c.t = #q c.t", "scoreboard players operation #d c.t *= #500 c.g",
    "scoreboard players operation #d c.t /= #V c.t", "scoreboard players operation #d c.t *= #-1 c.g",
    f"function {NS}:prix/mid", f"function {NS}:prix/sans_bonus", f"function {NS}:prix/vente",
    "scoreboard players operation #tot c.t = #a c.t", "scoreboard players operation #tot c.t *= #q c.t",
    # Métiers 26 : Acheteur malin (-5 %)
    "execute if score @s m.tam matches 1 run scoreboard players operation #tot c.t *= #95 c.g",
    "execute if score @s m.tam matches 1 run scoreboard players operation #tot c.t /= #100 c.g",
    # paiement au centime près : #ce Écus et #cc centimes
    "scoreboard players operation #ce c.t = #tot c.t", "scoreboard players operation #ce c.t /= #100 c.g",
    "scoreboard players operation #cc c.t = #tot c.t", "scoreboard players operation #cc c.t %= #100 c.g",
    "scoreboard players operation #x c.t = #tot c.t"] + fmt(f"{NS}:t", "m.") + [
    f"execute store result storage {NS}:t it.q int 1 run scoreboard players get #q c.t",
    f"data modify storage {NS}:t m.q set from storage {NS}:t it.q",
    "scoreboard players set #ok c.t 0",
    "execute if score @s c.ecus > #ce c.t run scoreboard players set #ok c.t 1",
    "execute if score @s c.ecus = #ce c.t if score @s c.cts >= #cc c.t run scoreboard players set #ok c.t 1",
    f"execute if score #ok c.t matches 0 run return run function {NS}:op/msg_pauvre with storage {NS}:t m",
    "scoreboard players operation @s c.ecus -= #ce c.t", "scoreboard players operation @s c.cts -= #cc c.t",
    "execute if score @s c.cts matches ..-1 run scoreboard players remove @s c.ecus 1",
    "execute if score @s c.cts matches ..-1 run scoreboard players add @s c.cts 100",
    "scoreboard players operation @s c.ta += #ce c.t",
    # Métiers 26 : Contrebandier, 5 % de chance d'être remboursé
    "execute if score @s m.tcb matches 1 store result score #r c.t run random value 1..100",
    f"execute if score @s m.tcb matches 1 if score #r c.t matches ..5 run function {NS}:op/contrebande",
    f"function {NS}:op/donner with storage {NS}:t it",
    # bonus du Bâtisseur : seulement pour les blocs à 1 Écu pièce ou plus (sinon de la terre devenait une machine à XP)
    "execute if score #blk c.t matches 1 if score #a c.t matches 250.. run scoreboard players operation @s c.kb += #q c.t",
    "scoreboard players operation #p c.t += #d c.t",
    "execute if score #p c.t matches ..-301 run scoreboard players set #p c.t -300",
    "scoreboard players operation #as c.t += #q c.t",
    f"function {NS}:item/sauver", f"function {NS}:stat/achat with storage {NS}:t it",
    f"data modify storage {NS}:t m.n set from storage {NS}:t it.n",
    f"function {NS}:op/msg_achat with storage {NS}:t m",
    f"data modify storage {NS}:t m.n set from storage {NS}:t it.n", f"execute store result storage {NS}:t hl.id int 1 run scoreboard players get @s m.id",
    f'data modify storage {NS}:t hl.col set value "red"', f"function {NS}:banque/hist_txt_achat",
    "playsound minecraft:entity.villager.trade master @s ~ ~ ~ 0.8 1",
    "playsound minecraft:entity.item.pickup master @s ~ ~ ~ 0.6 0.8"])
w(F + "op/msg_achat.mcfunction", [f'$data modify storage {NS}:t msg set value "Acheté : $(q) pour $(e),$(z)$(c) Écus."',
    '$execute unless score #lot c.t matches 1 run tellraw @s [{"text":"[Commerce] ","color":"green"},{"text":"Acheté : ","color":"gray"},{"text":"$(q) $(n)","color":"white"},{"text":" pour ","color":"gray"},{"text":"-$(e),$(z)$(c) Écus","color":"red"}]'])
w(F + "op/contrebande.mcfunction", ["scoreboard players operation @s c.ecus += #ce c.t", "scoreboard players operation @s c.cts += #cc c.t",
    "execute if score @s c.cts matches 100.. run scoreboard players add @s c.ecus 1", "execute if score @s c.cts matches 100.. run scoreboard players remove @s c.cts 100",
    'tellraw @s [{"text":"[Commerce] ","color":"green"},{"text":"Contrebandier : cet achat t\'est remboursé.","color":"dark_green"}]'])
w(F + "op/msg_pauvre.mcfunction", [
    f'$data modify storage {NS}:t msg set value "Pas assez d\'Écus : il te faut $(e),$(z)$(c) Écus pour $(q)."',
    "playsound minecraft:entity.villager.no master @s ~ ~ ~ 0.8 1"])

# =====================================================================
# MARCHÉ : détente des prix, relevé horaire, évènements, semaine
# =====================================================================
DT = ["scoreboard players set #dec c.g 0"]
for it in ITL:
    DT += [f"scoreboard players operation #x c.t = {H(it)} c.p", "scoreboard players operation #x c.t /= #12 c.g",
           f"scoreboard players operation {H(it)} c.p -= #x c.t",
           f"execute if score {H(it)} c.p matches -11..11 run scoreboard players set {H(it)} c.p 0"]
w(F + "marche/detente.mcfunction", DT)
RL = []
for it in ITL:
    RL += [f"scoreboard players set #i c.t {it['i']}", f"function {NS}:marche/releve_un"]
RL = ["scoreboard players set #isum c.t 0"] + RL + [
    "scoreboard players operation #h c.t = #isum c.t", f"scoreboard players set #n c.t {NIT}",
    "scoreboard players operation #h c.t /= #n c.t", "scoreboard players operation #indice c.g = #h c.t",
    f"data modify storage {NS}:hist _indice append value 0",
    f"execute store result storage {NS}:hist _indice[-1] int 1 run scoreboard players get #h c.t",
    f"execute if data storage {NS}:hist _indice[24] run data remove storage {NS}:hist _indice[0]"]
w(F + "marche/releve.mcfunction", RL)
w(F + "marche/releve_un.mcfunction", [
    f"function {NS}:item/charger", "scoreboard players set #d c.t 0", f"function {NS}:prix/mid",
    f"function {NS}:prix/sans_bonus", f"function {NS}:prix/vente",
    "scoreboard players operation #h c.t = #u0 c.t", f"function {NS}:item/sauver",
    f"function {NS}:hist/ajout with storage {NS}:t it",
    # indice : moyenne des prix rapportés à leur base, en millièmes
    "scoreboard players operation #r c.t = #u0 c.t", "scoreboard players operation #r c.t *= #1000 c.g",
    "scoreboard players operation #r c.t /= #b c.t", "scoreboard players operation #isum c.t += #r c.t"])
w(F + "hist/ajout.mcfunction", [
    f"$data modify storage {NS}:hist $(id) append value 0",
    f"$execute store result storage {NS}:hist $(id)[-1] int 1 run scoreboard players get #h c.t",
    f"$execute if data storage {NS}:hist $(id)[24] run data remove storage {NS}:hist $(id)[0]"])
w(F + "marche/heure.mcfunction", [
    "scoreboard players set #hr c.g 0", f"function {NS}:marche/releve",
    "scoreboard players set #r c.t 100",
    "execute if score #evi c.g matches 0 store result score #r c.t run random value 1..100",
    "execute if score #evt c.g matches 1.. run scoreboard players remove #evt c.g 1",
    f"execute if score #evi c.g matches 1.. if score #evt c.g matches 0 run function {NS}:marche/evt_fin",
    f"execute if score #r c.t matches ..40 run function {NS}:marche/evt_debut"])
w(F + "marche/evt_debut.mcfunction", [
    f"execute store result score #i c.t run random value 1..{NCOM}",
    "scoreboard players operation #evi c.g = #i c.t", "scoreboard players set #evt c.g 2",
    f"function {NS}:item/charger",
    "execute store result score #r c.t run random value 1..2",
    "execute if score #r c.t matches 1 run scoreboard players set #e c.t 1600",
    "execute if score #r c.t matches 2 run scoreboard players set #e c.t 500",
    f"function {NS}:item/sauver",
    f"execute if score #r c.t matches 1 run function {NS}:marche/evt_penurie with storage {NS}:t it",
    f"execute if score #r c.t matches 2 run function {NS}:marche/evt_krach with storage {NS}:t it",
    f"tellraw @a {L(PREFIX, T('Bourse : ', 'light_purple', True), '{storage:\"commerce:g\",nbt:\"evtxt\",color:\"white\"}')}",
    "execute as @a at @s run playsound minecraft:block.bell.use master @s ~ ~ ~ 0.7 1.4"])
w(F + "marche/evt_penurie.mcfunction", f'$data modify storage {NS}:g evtxt set value "Pénurie de $(n) ! Il se vend 60 % plus cher pendant 2 h de jeu."')
w(F + "marche/evt_krach.mcfunction", f'$data modify storage {NS}:g evtxt set value "Krach de $(n) ! Son prix est divisé par deux pendant 2 h de jeu."')
w(F + "marche/evt_fin.mcfunction", [
    "scoreboard players operation #i c.t = #evi c.g", f"function {NS}:item/charger",
    "scoreboard players set #e c.t 1000", f"function {NS}:item/sauver",
    "scoreboard players set #evi c.g 0",
    f'data modify storage {NS}:g evtxt set value ""',
    f"tellraw @a {L(PREFIX, T('Bourse : le cours de ', 'light_purple'), '{storage:\"commerce:t\",nbt:\"it.n\",color:\"white\"}', T(' revient à la normale.', 'light_purple'))}"])
SEM = [f"function {NS}:stat/semaine", f"function {NS}:banque/interets"]
for it in ITL:
    SEM += [f"scoreboard players set {H(it)} c.vs 0", f"scoreboard players set {H(it)} c.as 0"]
SEM += ["scoreboard players reset * c.ncr", say("Nouvelle semaine de bourse : le prix des cristaux redescend, les tops repartent à zéro.", "light_purple", "@a")]
w(F + "marche/semaine.mcfunction", SEM)

# =====================================================================
# CLASSEMENTS (joueurs connus, même déconnectés) : rang/calcul {obj, n} -> storage commerce:r C (texte)
# =====================================================================
w(F + "rang/calcul.mcfunction", [
    f"data modify storage {NS}:r L set value []", f"data modify storage {NS}:r R set value []",
    f"data modify storage {NS}:r W set from storage {NS}:j l",
    f'$data modify storage {NS}:r obj set value "$(obj)"', "$scoreboard players set #rn c.t $(n)",
    f"function {NS}:rang/remplir", "scoreboard players set #rk c.t 0", f"function {NS}:rang/extraire",
    f"function {NS}:rang/texte"])
w(F + "rang/remplir.mcfunction", [
    f"execute unless data storage {NS}:r W[0] run return 0",
    f"data modify storage {NS}:r cur set from storage {NS}:r W[0]",
    f"data modify storage {NS}:r cur.obj set from storage {NS}:r obj",
    f"function {NS}:rang/remplir_m with storage {NS}:r cur",
    f"data remove storage {NS}:r W[0]", f"function {NS}:rang/remplir"])
w(F + "rang/remplir_m.mcfunction", [
    "scoreboard players set #e c.t 0",
    "$execute store result score #e c.t run scoreboard players get $(nom) $(obj)",
    f'$data modify storage {NS}:r L append value {{nom:"$(nom)",e:0}}',
    f"execute store result storage {NS}:r L[-1].e int 1 run scoreboard players get #e c.t"])
w(F + "rang/extraire.mcfunction", [
    "execute if score #rk c.t >= #rn c.t run return 0",
    f"execute unless data storage {NS}:r L[0] run return 0",
    "scoreboard players set #m c.t -1", f"data modify storage {NS}:r W set from storage {NS}:r L",
    f"function {NS}:rang/max",
    "scoreboard players add #rk c.t 1",
    f"data modify storage {NS}:r R append from storage {NS}:r best",
    f"execute store result storage {NS}:r R[-1].r int 1 run scoreboard players get #rk c.t",
    f"function {NS}:rang/oter with storage {NS}:r best", f"function {NS}:rang/extraire"])
w(F + "rang/max.mcfunction", [
    f"execute unless data storage {NS}:r W[0] run return 0",
    f"execute store result score #x c.t run data get storage {NS}:r W[0].e",
    f"execute if score #x c.t > #m c.t run data modify storage {NS}:r best set from storage {NS}:r W[0]",
    "execute if score #x c.t > #m c.t run scoreboard players operation #m c.t = #x c.t",
    f"data remove storage {NS}:r W[0]", f"function {NS}:rang/max"])
w(F + "rang/oter.mcfunction", f'$data remove storage {NS}:r L[{{nom:"$(nom)"}}]')
w(F + "rang/texte.mcfunction", [
    f'data modify storage {NS}:r C set value [{{text:""}}]',
    f'execute unless data storage {NS}:r R[0] run data modify storage {NS}:r C append value {{text:"Personne pour l\'instant.",color:"gray"}}',
    f"data modify storage {NS}:r W set from storage {NS}:r R", f"function {NS}:rang/texte_boucle"])
w(F + "rang/texte_boucle.mcfunction", [
    f"execute unless data storage {NS}:r W[0] run return 0",
    f"function {NS}:rang/texte_m with storage {NS}:r W[0]",
    f"data remove storage {NS}:r W[0]", f"function {NS}:rang/texte_boucle"])
w(F + "rang/texte_m.mcfunction", [
    f'$data modify storage {NS}:r C append value {{text:"$(r). ",color:"gray"}}',
    f'$data modify storage {NS}:r C append value {{text:"$(nom)",color:"white"}}',
    f'$data modify storage {NS}:r C append value {{text:"   $(e) ",color:"gold"}}',
    f'data modify storage {NS}:r C append value {ECU_C}',
    f'data modify storage {NS}:r C append value {{text:"\\n"}}'])

# =====================================================================
# CRISTAUX DE MÉTIER : 2 500 Écus, +5 % à chaque achat de la semaine
# =====================================================================
w(F + "cristal/prix.mcfunction", [
    "scoreboard players set #cp c.t 2500", "scoreboard players operation #n c.t = @s c.ncr",
    "execute if score #n c.t matches 201.. run scoreboard players set #n c.t 200",
    f"function {NS}:cristal/prix_boucle"])
w(F + "cristal/prix_boucle.mcfunction", [
    "execute if score #n c.t matches ..0 run return 0",
    "scoreboard players operation #cp c.t *= #105 c.g", "scoreboard players operation #cp c.t /= #100 c.g",
    "scoreboard players remove #n c.t 1", f"function {NS}:cristal/prix_boucle"])
for j, nom, col in JOBS:
    w(F + f"cristal/acheter_{j}.mcfunction", [
        f"function {NS}:cristal/prix",
        f"execute store result storage {NS}:t m.e int 1 run scoreboard players get #cp c.t",
        f"execute if score @s c.ecus < #cp c.t run return run function {NS}:cristal/msg_pauvre with storage {NS}:t m",
        "scoreboard players operation @s c.ecus -= #cp c.t", "scoreboard players operation @s c.ta += #cp c.t",
        f"scoreboard players add @s m.cr_{j} 1", "scoreboard players add @s c.ncr 1",
        f'data modify storage {NS}:t msg set value "Cristal de {nom} acheté. Le suivant coûte 5 % de plus."',
        "playsound minecraft:block.amethyst_block.chime master @s ~ ~ ~ 1 1.2"])
w(F + "cristal/msg_pauvre.mcfunction", [
    f'$data modify storage {NS}:t msg set value "Pas assez d\'Écus : un cristal coûte $(e) Écus."',
    "playsound minecraft:entity.villager.no master @s ~ ~ ~ 0.8 1"])

# =====================================================================
# PAGES (dialogues)
# =====================================================================
def dlg(title, body, actions, cols=2, kind="multi_action"):
    return (f'dialog show @s {{type:"minecraft:{kind}",title:{title},can_close_with_escape:true,pause:false,'
            f'body:[{",".join(body)}],actions:[{",".join(actions)}],columns:{cols}}}')


def msg_line(st, pre=""):
    return [f"data modify storage {st} {pre}msg set from storage {NS}:t msg", f'data modify storage {NS}:t msg set value ""']


MSG_TXT = T("$(msg)", "yellow")
RETOUR = btn(T("Accueil", "white"), 1, 100)

# ---------------------------------------------------------------- textures des objets dans les boutons
# Composant de texte « object » (1.21.9+) : affiche une texture d'un atlas du jeu, sans resource pack.
# Correspondance objet -> texture tirée des textures officielles de la 26.1 (sprites_26.1.json, minecraft-assets).
SPRITES = json.load(open(os.path.join(HERE, "sprites_26.1.json"), encoding="utf-8"))
spr = lambda iid: f'{{object:"atlas",atlas:"minecraft:{SPRITES[iid][0]}",sprite:"minecraft:{SPRITES[iid][1]}"}}'

# ---------------------------------------------------------------- recette de l'oeuf : une seule image
# Le haut de la texture d'établi du resource pack commun (interface Forge) avec les vraies textures des ingrédients
# déjà posées dans les cases : rien à aligner au pixel en jeu. Taille réelle (176 x 88), sous les 256 px permis.
RP = os.path.join(HERE, "..", "build", "commerce_rp", "assets", "commerce")
PANNEAU = ""
RECETTE = {"E": "emerald", "G": "gold_ingot", "C": "barrel_side"}
GRID = ["GEG", "ECE", "GEG"]
BANNIERES = [("COMMERCE", "emerald"), ("MARCHÉ", "emerald"), ("BOURSE", "bell"), ("FORTUNES", "gold_ingot"), ("CRISTAUX", "diamond"), ("SPAWNERS", "spawner"), ("GRAPHIQUES", "clock"),
             # bandeaux des autres packs (même police, resource pack commun) : Métiers 7 à 11, Horreur 12, Compagnons 13
             ("MÉTIERS", "iron_pickaxe"), ("FORGE", "anvil_top"), ("QUETES", "writable_book"), ("GUILDE", "name_tag"), ("BAREME", "book"), ("BESTIAIRE", "bone"), ("COMPAGNONS", "lead"),
             ("LES COUILLONS", "gold_ingot")]   # 14 : menu G commun (plus large)
# boutons du menu G (25.8) : chaque libellé est une image (icône + titre en police x2 dégradée), glyphe chr(0xE040 + k)
MENU_BTN = [("MÉTIERS", "iron_pickaxe", (140, 255, 255), (20, 150, 190)), ("COMMERCE", "emerald", (255, 222, 90), (215, 120, 10)),
            ("BESTIAIRE", "bone", (255, 110, 90), (150, 15, 15)), ("COMPAGNONS", "lead", (250, 200, 120), (180, 100, 30)),
            ("MON PROFIL", "name_tag", (255, 245, 140), (200, 160, 20)), ("GUIDE", "book", (255, 255, 255), (170, 170, 180))]
MENU_GLY = [chr(0xE040 + k) for k in range(len(MENU_BTN))]
# décors des pages de métier (lus par Métiers) : nom, bloc de fond, outil, dégradé haut/bas, blocs semés dans le fond
SCENES = {"b": ("BÛCHERON", "oak_log", "iron_axe", (255, 215, 110), (200, 120, 20), []),
          "f": ("FERMIER", "farmland_moist", "wheat", (150, 255, 120), (40, 150, 30), ["hay_block_top"]),
          "m": ("MINEUR", "deepslate", "iron_pickaxe", (235, 235, 240), (130, 130, 145), ["deepslate_diamond_ore", "deepslate_gold_ore"]),
          "c": ("CHASSEUR", "mossy_cobblestone", "iron_sword", (255, 120, 100), (170, 20, 20), []),
          "p": ("PÊCHEUR", "prismarine_bricks", "fishing_rod", (150, 255, 255), (20, 150, 190), []),
          "e": ("ÉLEVEUR", "hay_block_top", "lead", (255, 160, 255), (180, 60, 190), []),
          "n": ("ENCHANTEUR", "bookshelf", "enchanted_book", (220, 150, 255), (110, 30, 170), []),
          "x": ("EXPLORATEUR", "cartography_table_top", "compass_00", (140, 170, 255), (40, 60, 200), ["map"]),
          "t": ("MARCHAND", "emerald_block", "emerald", (140, 255, 150), (20, 130, 40), []),
          "k": ("BÂTISSEUR", "bricks", "brush", (240, 200, 150), (170, 110, 60), [])}
SCENE_IDX = {"b": 1, "f": 2, "m": 3, "c": 4, "p": 5, "e": 6, "n": 7, "x": 8, "t": 9, "k": 10}
# bandeau k : glyphe chr(0xE020 + k), 27 px de haut, soit 3 lignes de texte
BAN = lambda k: f'{{type:"minecraft:plain_message",width:310,contents:[{{text:""}},{{text:"{chr(0xE020 + k)}",font:"commerce:recette",color:"white",shadow_color:0}},{{text:"\\n\\n"}}]}}'


GLYPHE_MAX = 240   # taille maxi d'un glyphe de police (px)


def dessiner_rp():
    import io as _io
    from PIL import Image, ImageDraw
    with zipfile.ZipFile(os.path.join(HERE, "..", "..", "..", "metiers_resourcepack.zip")) as z:
        ct = Image.open(_io.BytesIO(z.read("assets/minecraft/textures/gui/container/crafting_table.png"))).convert("RGBA")
    im = Image.new("RGBA", (176, 88), (0, 0, 0, 0))
    im.paste(ct.crop((0, 0, 176, 81)), (0, 0))
    im.paste(ct.crop((0, 159, 176, 166)), (0, 81))
    tex = lambda n: Image.open(os.path.join(HERE, "textures_recette", n + ".png")).convert("RGBA")
    for r, row in enumerate(GRID):
        for c, k in enumerate(row):
            t = tex(RECETTE[k]); im.paste(t, (30 + 18 * c, 17 + 18 * r), t)
    t = tex("villager_spawn_egg"); im.paste(t, (124, 35), t)
    assert max(im.size) <= 256, "glyphe de police trop grand (256 px au plus)"
    os.makedirs(os.path.join(RP, "textures", "font"), exist_ok=True)
    im.save(os.path.join(RP, "textures", "font", "recette.png"))
    # pièce d'Écu, 8 px d'interface (texture 32 x 32) : or, bord sombre, reflet, É gravé
    p = Image.new("RGBA", (32, 32), (0, 0, 0, 0)); q = ImageDraw.Draw(p)
    q.ellipse([0, 2, 31, 31], fill=(122, 78, 10, 255))
    q.ellipse([0, 0, 31, 29], fill=(176, 120, 20, 255))
    q.ellipse([3, 3, 28, 26], fill=(246, 196, 60, 255))
    q.ellipse([6, 5, 18, 14], fill=(255, 232, 140, 255))
    q.ellipse([8, 7, 23, 22], outline=(196, 140, 30, 255), width=2)
    for x0, y0, x1, y1 in [(12, 10, 14, 20), (12, 10, 20, 12), (12, 14, 18, 16), (12, 18, 20, 20), (15, 6, 18, 8)]:
        q.rectangle([x0, y0, x1 - 1, y1 - 1], fill=(150, 98, 12, 255))
    p.save(os.path.join(RP, "textures", "font", "ecu.png"))
    # bandeaux de titre : plaque façon interface Forge (pierre, cadre doré), texte en police Minecraft x2, icônes
    asc = Image.open(os.path.join(HERE, "textures_recette", "ascii.png")).convert("RGBA")
    def lettre(ch):
        o = ord(ch); cell = asc.crop(((o % 16) * 8, (o // 16) * 8, (o % 16) * 8 + 8, (o // 16) * 8 + 8))
        w_ = max([x for x in range(8) for y in range(8) if cell.getpixel((x, y))[3]] or [2]) + 1
        return cell, (4 if ch == " " else w_)
    pierre = ct.crop((7, 7, 23, 23))

    def plaque(Wb, Hb):
        """Plaque en 9 tranches prises sur la texture d'établi : coins, bords et fond de pierre d'origine."""
        b = Image.new("RGBA", (Wb, Hb), (0, 0, 0, 0))
        for x in range(7, Wb - 7, 16):
            for y in range(7, Hb - 7, 16):
                b.paste(pierre.crop((0, 0, min(16, Wb - 7 - x), min(16, Hb - 7 - y))), (x, y))
        for x in range(7, Wb - 7):
            b.paste(ct.crop((7, 0, 8, 7)), (x, 0)); b.paste(ct.crop((7, 159, 8, 166)), (x, Hb - 7))
        for y in range(7, Hb - 7):
            b.paste(ct.crop((0, 7, 7, 8)), (0, y)); b.paste(ct.crop((169, 7, 176, 8)), (Wb - 7, y))
        b.paste(ct.crop((0, 0, 7, 7)), (0, 0)); b.paste(ct.crop((169, 0, 176, 7)), (Wb - 7, 0))
        b.paste(ct.crop((0, 159, 7, 166)), (0, Hb - 7)); b.paste(ct.crop((169, 159, 176, 166)), (Wb - 7, Hb - 7))
        return b
    provs = []
    for k, (txt, ico) in enumerate(BANNIERES):
        Wb, Hb = (240 if k == 14 else 200), 27   # glyphe < 256 px : au-delà le client plante, à 256 pile le texte du jeu se corrompt (25/11/2026)
        b = plaque(Wb, Hb)
        d2 = ImageDraw.Draw(b)
        # texte centré, deux fois la taille de la police, ombre portée
        larg = sum(lettre(ch)[1] + 1 for ch in txt) * 2 - 2
        x0, y0 = (Wb - larg) // 2, 5
        for dx, dy, col in ((2, 2, (63, 45, 20)), (0, 0, (255, 205, 70))):
            x = x0
            for ch in txt:
                cell, w_ = lettre("E" if ch == "É" else ch)
                big = cell.resize((16, 16), Image.NEAREST)
                for yy in range(16):
                    for xx in range(16):
                        if big.getpixel((xx, yy))[3]:
                            b.putpixel((x + xx + dx, y0 + yy + dy), col + (255,))
                if ch == "É":   # accent aigu dessiné à la main
                    for xx, yy in ((8, -2), (6, -1)):
                        d2.rectangle([x + xx + dx, y0 + yy + dy, x + xx + dx + 1, y0 + yy + dy], fill=col + (255,))
                x += (w_ + 1) * 2
        for ix in (8, Wb - 24):
            t = tex(ico); b.paste(t, (ix, (Hb - 16) // 2), t)
        b.save(os.path.join(RP, "textures", "font", f"bandeau_{k}.png"))
        provs.append({"type": "bitmap", "file": f"commerce:font/bandeau_{k}.png", "height": Hb, "ascent": 7, "chars": [chr(0xE020 + k)]})
    # libellés du menu G : 140 x 18, icône 16 px puis titre x2 (lettres de 14 px) en dégradé vertical, ombre sombre
    for k, (txt, ico, haut, bas) in enumerate(MENU_BTN):
        Wb, Hb = 140, 18
        b = Image.new("RGBA", (Wb, Hb), (0, 0, 0, 0))
        larg = sum(lettre("E" if ch == "É" else ch)[1] * 2 + 1 for ch in txt) - 1
        x0 = (Wb - (16 + 4 + larg)) // 2
        t = tex(ico); b.paste(t, (x0, 1), t)
        ombre = tuple(int(c * 0.22) for c in bas)
        for dx, dy, grad in ((2, 2, False), (0, 0, True)):
            x = x0 + 20
            for ch in txt:
                cell, w_ = lettre("E" if ch == "É" else ch)
                big = cell.resize((16, 16), Image.NEAREST)
                pts = [(xx, yy) for yy in range(16) for xx in range(16) if big.getpixel((xx, yy))[3]]
                if ch == "É":
                    pts += [(8, -2), (9, -2), (6, -1), (7, -1)]
                for xx, yy in pts:
                    yy += 2   # accent compris
                    f = min(1, max(0, (yy - 2) / 13))
                    col = tuple(int(haut[i] + (bas[i] - haut[i]) * f) for i in range(3)) if grad else ombre
                    X, Y = x + xx + dx, yy + dy
                    if 0 <= X < Wb and 0 <= Y < Hb:
                        b.putpixel((X, Y), col + (255,))
                x += w_ * 2 + 1
        b.save(os.path.join(RP, "textures", "font", f"menu_{k}.png"))
        provs.append({"type": "bitmap", "file": f"commerce:font/menu_{k}.png", "height": Hb, "ascent": 13, "chars": [MENU_GLY[k]]})
    # décors des pages de métier (Métiers, 24/11/2026) : 300 x 36, fond de blocs du métier x2 assombri, cadre doré,
    # nom en grosses lettres dégradées, outil de chaque côté. Glyphe chr(0xE100 + idx du métier).
    ACC = {"É": ("E", [(6, -3), (7, -3), (4, -2), (5, -2)]), "Ê": ("E", [(4, -3), (5, -3), (2, -2), (3, -2), (6, -2), (7, -2)]),
           "Û": ("U", [(4, -3), (5, -3), (2, -2), (3, -2), (6, -2), (7, -2)]), "Â": ("A", [(4, -3), (5, -3), (2, -2), (3, -2), (6, -2), (7, -2)])}
    def gros(img, txt, x, y, haut, bas, ombre):
        for dx, dy, grad in ((2, 2, False), (0, 0, True)):
            xx0 = x
            for ch in txt:
                base, acc = ACC.get(ch, (ch, []))
                cell, w_ = lettre(base)
                big = cell.resize((16, 16), Image.NEAREST)
                pts = [(u, v) for v in range(16) for u in range(16) if big.getpixel((u, v))[3]] + acc
                for u, v in pts:
                    f = min(1, max(0, v / 13))
                    col = tuple(int(haut[i] + (bas[i] - haut[i]) * f) for i in range(3)) if grad else ombre
                    X, Y = xx0 + u + dx, y + v + dy
                    if 0 <= X < img.width and 0 <= Y < img.height:
                        img.putpixel((X, Y), col + (255,))
                xx0 += w_ * 2 + 2
    for j, (nom, fond, ico, haut, bas, sem) in SCENES.items():
        Wb, Hb = 240, 36   # glyphe < 256 px : à 256 pile, le texte des panneaux et des noms devenait illisible en 26.3 (25/11/2026)
        b = Image.new("RGBA", (Wb, Hb), (0, 0, 0, 255))
        tf = tex(fond).resize((32, 32), Image.NEAREST)
        semis = [tex(x_).resize((32, 32), Image.NEAREST) for x_ in sem]
        import random as _rd
        rg = _rd.Random(j)
        for tx in range(0, Wb, 32):
            for ty in range(-14, Hb, 32):
                t_ = rg.choice(semis) if semis and rg.random() < 0.25 else tf
                b.paste(t_, (tx, ty))
        px = b.load()
        for X in range(Wb):
            for Y in range(Hb):
                r, g, b_, a_ = px[X, Y]
                k_ = 0.42 * (1 - 0.5 * (abs(X - Wb / 2) / (Wb / 2)) ** 2)
                k_ *= 0.55 if fond == "emerald_block" else 1
                px[X, Y] = (int(r * k_), int(g * k_), int(b_ * k_), 255)
        d3 = ImageDraw.Draw(b)
        d3.rectangle([0, 0, Wb - 1, Hb - 1], outline=(40, 26, 8, 255))
        d3.rectangle([1, 1, Wb - 2, Hb - 2], outline=(222, 170, 60, 255))
        d3.rectangle([2, 2, Wb - 3, Hb - 3], outline=(120, 80, 20, 255))
        for cx, cy in ((3, 3), (Wb - 4, 3), (3, Hb - 4), (Wb - 4, Hb - 4)):
            d3.point((cx, cy), fill=(255, 225, 120, 255))
        it = tex(ico).resize((24, 24), Image.NEAREST)
        b.paste(it, (10, 6), it); b.paste(it.transpose(Image.FLIP_LEFT_RIGHT), (Wb - 34, 6), it.transpose(Image.FLIP_LEFT_RIGHT))
        larg = sum(lettre(ACC.get(ch, (ch,))[0])[1] * 2 + 2 for ch in nom) - 2
        gros(b, nom, (Wb - larg) // 2, 12, haut, bas, tuple(int(c * 0.18) for c in bas))
        b.save(os.path.join(RP, "textures", "font", f"scene_{j}.png"))
        provs.append({"type": "bitmap", "file": f"commerce:font/scene_{j}.png", "height": Hb, "ascent": 7, "chars": [chr(0xE100 + SCENE_IDX[j])]})
    for _p in provs:   # garde-fou : glyphe seul de 256 px ou plus = plantage ou texte corrompu chez le client (24-25/11/2026)
        if _p["type"] == "bitmap" and len(_p["chars"]) == 1 and len(_p["chars"][0]) == 1:
            _im = Image.open(os.path.join(RP, "textures", "font", _p["file"].split("font/")[1]))
            assert max(_im.size) <= GLYPHE_MAX, f"glyphe trop grand : {_p['file']} {_im.size}"
    # barres de courbe : 8 hauteurs, blanches (la couleur du texte les teinte), 2 px de large, posées sur la ligne
    bar = Image.new("RGBA", (24, 9), (0, 0, 0, 0))
    for k in range(8):
        for y in range(8 - k, 9):
            for x in range(2):
                bar.putpixel((k * 3 + x, y), (255, 255, 255, 255))
    bar.save(os.path.join(RP, "textures", "font", "barres.png"))
    provs.append({"type": "bitmap", "file": "commerce:font/barres.png", "height": 9, "ascent": 8, "chars": ["".join(chr(0xE030 + k) for k in range(8))]})
    os.makedirs(os.path.join(RP, "font"), exist_ok=True)
    json.dump({"providers": [
        {"type": "bitmap", "file": "commerce:font/recette.png", "height": 88, "ascent": 7, "chars": [PANNEAU]},
        {"type": "bitmap", "file": "commerce:font/ecu.png", "height": 8, "ascent": 7, "chars": [ECU]}] + provs},
        open(os.path.join(RP, "font", "recette.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if os.path.exists(os.path.join(HERE, "..", "build", "commerce_rp")):
    shutil.rmtree(os.path.join(HERE, "..", "build", "commerce_rp"))
dessiner_rp()
exec(open(os.path.join(HERE, "hud.py"), encoding="utf-8").read())
# l'image occupe 88 px, soit 10 lignes de texte : la ligne qui la porte est suivie de 10 retours à la ligne
GRILLE_SNBT = L(f'{{text:"{PANNEAU}",font:"commerce:recette",color:"white",shadow_color:0}}', T("\\n" * 10, "white"),
                T("Émeraude : 4 blocs · Diamant : 1 bloc · Or : 2 blocs · Netherite : 1 lingot · Tonneau : 1", "gray"))

# ---------------------------------------------------------------- touche G (dialogue fixe, lu au démarrage)
wj(f"data/{NS}/dialog/ouvrir.json", {
    "type": "minecraft:multi_action", "title": {"text": "Commerce", "color": "gold", "bold": True},
    "external_title": {"text": "Commerce"}, "can_close_with_escape": True, "pause": False,
    "body": [{"type": "minecraft:plain_message", "width": 300,
              "contents": [{"text": "Ton compte en Écus, le marché, la bourse, les fortunes et les cristaux. Il se débloque en craftant l'oeuf de comptoir.", "color": "gray"}]}],
    "actions": [{"label": {"text": "Ouvrir le Commerce", "color": "gold", "bold": True}, "width": 200,
                 "action": {"type": "run_command", "command": "trigger commerce set 1"}}],
    "columns": 1})
wj("data/minecraft/tags/dialog/quick_actions.json", {"values": [f"{NS}:ouvrir"]})
wj("data/minecraft/tags/dialog/pause_screen_additions.json", {"values": [f"{NS}:ouvrir"]})

# ---------------------------------------------------------------- pagination du marché
PAGE = 10                                   # objets par page : 5 rangées de 2 boutons, tout tient sans défiler
CATIT = {c: [it for it in ITL if it["cat"] == c] for c in ITEMS}
NPAGES = {c: (len(v) + PAGE - 1) // PAGE for c, v in CATIT.items()}
for c, v in CATIT.items():
    for k, it in enumerate(v):
        it["page"] = k // PAGE
RELIQUE_PRIX = 15000   # vente d'une relique de boss de Métiers (25/11/2026)
# anciennes reliques, sans marque custom_data : reconnues par leur nom exact (tel que posé par les tables de butin de Métiers)
RELIQUES_NOM = [("netherite_axe", "Hache du Colosse", "dark_red"), ("bow", "Arc de la Reine", "dark_green"),
                ("trident", "Trident du givre", "aqua"), ("netherite_chestplate", "Plastron du Brasier", "gold"),
                ("crossbow", "Arbalète du Creeper", "green")]
w(F + "relique/vendre.mcfunction", [
    f"execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{metiers_relique:1b}}] run return run function {NS}:relique/ok"] + [
    f'execute if items entity @s weapon.mainhand minecraft:{i}[minecraft:custom_name={{text:"{n}",color:"{c}",bold:1b,italic:0b}}] run return run function {NS}:relique/ok'
    for i, n, c in RELIQUES_NOM] + [
    say("Prends une relique de boss en main (objet nommé avec « Relique de boss » en description), puis clique sur Vendre.", "red"),
    "playsound minecraft:entity.villager.no master @s ~ ~ ~ 1 1"])
w(F + "relique/ok.mcfunction", [
    "item replace entity @s weapon.mainhand with minecraft:air",
    f"scoreboard players add @s c.ecus {RELIQUE_PRIX}", f"scoreboard players add @s c.tv {RELIQUE_PRIX}",
    say(f"Relique vendue : +{RELIQUE_PRIX:,} Écus.".replace(",", " "), "gold"),
    "playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 0.8"])
# « Tout vendre » du Butin de boss (25.8) : chaque objet de la catégorie 17 passe par la vente normale (prix du marché,
# bonus de métier), puis toutes les reliques à prix fixe
# 25/11/2026 : « Tout vendre » prend aussi tout ce que lâchent les boss et qui est rangé dans une autre catégorie
# (diamants, débris antiques, netherite, étoile du Nether, totems...). Liste lue dans les tables de butin des boss de
# Métiers et du Croque-mitaine d'Horreur (zips des packs voisins), recoupée avec le catalogue.
def _ids_butin(o, acc):
    if isinstance(o, dict):
        if o.get("type") in ("minecraft:item", "item") and "name" in o:
            acc.add(o["name"].replace("minecraft:", ""))
        for v in o.values():
            _ids_butin(v, acc)
    elif isinstance(o, list):
        for v in o:
            _ids_butin(v, acc)
BOSS_IDS = set()
for _zip, _pref in ((os.path.join(HERE, "..", "..", "metiers", "metiers.zip"), ("data/metiers/loot_table/boss/",)),
                    (os.path.join(HERE, "..", "..", "horreur", "horreur.zip"),
                     ("data/horreur/loot_table/creature/croque.json", "data/horreur/loot_table/bonus/croque.json"))):
    with zipfile.ZipFile(_zip) as _z:
        for _n in _z.namelist():
            if _n.endswith(".json") and _n.startswith(_pref):
                _ids_butin(json.loads(_z.read(_n)), BOSS_IDS)
assert BOSS_IDS, "aucune table de butin de boss trouvée"
VENTE_BOSS = [it for it in ITL if it["cat"] == 17 or it["id"] in BOSS_IDS]
print("Tout vendre (butin de boss) :", len(VENTE_BOSS), "objets ; hors catalogue :",
      sorted(BOSS_IDS - {it["id"] for it in ITL}))
BT_ = ["scoreboard players set #btot c.t 0", "scoreboard players set #lot c.t 1"]
for it in VENTE_BOSS:
    if True:
        BT_ += [f"execute unless items entity @s container.* minecraft:{it['id']}{FILTRE} unless items entity @s weapon.offhand minecraft:{it['id']}{FILTRE} run scoreboard players set #i c.t 0",
                f"execute if items entity @s container.* minecraft:{it['id']}{FILTRE} run scoreboard players set #i c.t {it['i']}",
                f"execute if items entity @s weapon.offhand minecraft:{it['id']}{FILTRE} run scoreboard players set #i c.t {it['i']}",
                "scoreboard players set #tot c.t 0", "scoreboard players set #act c.t 3", "scoreboard players set #q c.t 0",
                f"execute if score #i c.t matches 1.. run function {NS}:op/vendre",
                "scoreboard players operation #btot c.t += #tot c.t"]
BT_ += ["scoreboard players operation #btot c.t /= #100 c.g",
        f"execute store result score #nr c.t run clear @s *[minecraft:custom_data~{{metiers_relique:1b}}]"]
for i, n, c in RELIQUES_NOM:
    BT_ += [f'execute store result score #x c.t run clear @s minecraft:{i}[minecraft:custom_name={{text:"{n}",color:"{c}",bold:1b,italic:0b}}]',
            "scoreboard players operation #nr c.t += #x c.t"]
BT_ += ["scoreboard players set #k c.t " + str(RELIQUE_PRIX), "scoreboard players operation #x c.t = #nr c.t",
        "scoreboard players operation #x c.t *= #k c.t", "scoreboard players operation @s c.ecus += #x c.t",
        "scoreboard players operation @s c.tv += #x c.t", "scoreboard players operation #btot c.t += #x c.t",
        f'execute if score #btot c.t matches ..0 run tellraw @s {L(PREFIX, T("Aucun butin de boss à vendre dans ton inventaire (les objets renommés à la main ne comptent pas).", "red"))}',
        f'execute if score #btot c.t matches 1.. run tellraw @s {L(PREFIX, T("Butin de boss vendu : ", "gold"), "{score:{name:\"#btot\",objective:\"c.t\"},color:\"yellow\",bold:true}", T(" Écus, dont ", "gold"), "{score:{name:\"#nr\",objective:\"c.t\"},color:\"yellow\"}", T(" relique(s).", "gold"))}',
        "execute if score #btot c.t matches 1.. run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.7 1.4",
        "scoreboard players set #lot c.t 0",
        f"function {NS}:page/cat_17_0"]
w(F + "relique/tout.mcfunction", BT_)
# 25/11/2026 : bouton « Tout vendre » en tête de chaque catégorie : vend tout ce que tu as de cette catégorie
for c in ITEMS:
    if c == 17:
        continue
    TV = ["scoreboard players set #btot c.t 0", "scoreboard players set #lot c.t 1"]
    for it in CATIT[c]:
        TV += [f"execute unless items entity @s container.* minecraft:{it['id']}{FILTRE} unless items entity @s weapon.offhand minecraft:{it['id']}{FILTRE} run scoreboard players set #i c.t 0",
               f"execute if items entity @s container.* minecraft:{it['id']}{FILTRE} run scoreboard players set #i c.t {it['i']}",
               f"execute if items entity @s weapon.offhand minecraft:{it['id']}{FILTRE} run scoreboard players set #i c.t {it['i']}",
               "scoreboard players set #tot c.t 0", "scoreboard players set #act c.t 3", "scoreboard players set #q c.t 0",
               f"execute if score #i c.t matches 1.. run function {NS}:op/vendre",
               "scoreboard players operation #btot c.t += #tot c.t"]
    TV += ["scoreboard players set #lot c.t 0", "scoreboard players operation #btot c.t /= #100 c.g",
           f'execute if score #btot c.t matches ..0 run tellraw @s {L(PREFIX, T("Rien à vendre dans cette catégorie (les objets renommés ou spéciaux sont gardés).", "red"))}',
           f'execute if score #btot c.t matches 1.. run tellraw @s {L(PREFIX, T(CATNAME[c] + " vendu en entier : ", "gray"), "{score:{name:\"#btot\",objective:\"c.t\"},color:\"gold\",bold:true}", T(" Écus", "gold"))}',
           "execute if score #btot c.t matches 1.. run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.7 1.4",
           f"function {NS}:page/cat_{c}_0"]
    w(F + f"page/tout_{c}.mcfunction", TV)
PG = lambda c, p: 1000 + 10 * c + p         # valeur du trigger d'une page de catégorie
for it in ITL:
    # retour vers la bonne page de la catégorie : on corrige la valeur stockée par i/<n>/charger
    pth = os.path.join(ROOT, F, "i", str(it["i"]), "charger.mcfunction")
    txt = open(pth, encoding="utf-8").read().replace(f'cb:{100 + it["cat"]}}}', f'cb:{PG(it["cat"], it["page"])}}}')
    open(pth, "w", encoding="utf-8").write(txt)

# ---------------------------------------------------------------- aiguillage du trigger
TR = ["scoreboard players operation #v c.t = @s commerce", "scoreboard players set @s commerce 0",
      "scoreboard players enable @s commerce",
      f"execute if score #v c.t matches 60 run return run function {NS}:page/aide",
      f"execute if score #v c.t matches 7000 run return run function {NS}:spawner/aide",
      f"execute if score #v c.t matches 30 run return run function {NS}:serveur/profil"] + [
      f"execute if score #v c.t matches {31 + i} run return run function {NS}:serveur/guide_{i + 1}" for i in range(5)] + [
      f"execute unless score @s c.deb matches 1 run return run function {NS}:page/verrou",
      f"execute if score #v c.t matches 1 run return run function {NS}:page/accueil",
      f"execute if score #v c.t matches 9 run return run function {NS}:page/marche",
      f"execute if score #v c.t matches 20 run return run function {NS}:page/bourse",
      f"execute if score #v c.t matches 21 run return run function {NS}:page/fortunes",
      f"execute if score #v c.t matches 22 run return run function {NS}:page/cristaux",
      f"execute if score #v c.t matches 23 run return run function {NS}:page/plus",
      f"execute if score #v c.t matches 50 run return run function {NS}:comptoir/deplacer",
      f"execute if score #v c.t matches ..-1 run return run function {NS}:saisie/entree",
      f"execute if score #v c.t matches 90 run return run function {NS}:banque/page",
      f"execute if score #v c.t matches 91 run return run function {NS}:banque/destinataires",
      f"execute if score #v c.t matches 8100000..8199999 run return run function {NS}:banque/dest_choisi"] + [
      f"execute if score #v c.t matches {940 + i} run return run function {NS}:banque/op_depot_{i}" for i in range(4)] + [
      f"execute if score #v c.t matches {950 + i} run return run function {NS}:banque/op_retrait_{i}" for i in range(4)] + [
      f"execute if score #v c.t matches {6000 + p} run return run function {NS}:hdv/page_{p}" for p in range(10)] + [
      f"execute if score #v c.t matches 6100 run return run function {NS}:hdv/vendre",
      f"execute if score #v c.t matches 6200 run return run function {NS}:hdv/mes",
      f"execute if score #v c.t matches 9000000..9499999 run return run function {NS}:hdv/acheter",
      f"execute if score #v c.t matches 9500000..9999999 run return run function {NS}:hdv/retirer",
      f"execute if score #v c.t matches 7500000..7599999 run return run function {NS}:boutique/acheter",
      f"execute if score #v c.t matches 7700..7799 run return run function {NS}:guilde/entree",
      f"execute if score #v c.t matches 7800 run return run function {NS}:relique/vendre",
      f"execute if score #v c.t matches 7801 run return run function {NS}:relique/tout",
      f"execute if score #v c.t matches 81..84 run return run function {NS}:stat/global",
      f"execute if score #v c.t matches 70 run return run function {NS}:spawner/entree",
      f"execute if score #v c.t matches 700..799 run return run function {NS}:spawner/entree",
      f"execute if score #v c.t matches 7100..7399 run return run function {NS}:spawner/entree",
      f"execute if score #v c.t matches 4000000..4999999 run return run function {NS}:stat/item_entree",
      f"execute if score #v c.t matches 5000000..5999999 run return run function {NS}:stat/jour_entree"]
TR += [f"execute if score #v c.t matches {PG(c, p)} run return run function {NS}:page/cat_{c}_{p}" for c in ITEMS for p in range(NPAGES[c])]
TR += [f"execute if score #v c.t matches {7900 + c} run return run function {NS}:page/tout_{c}" for c in ITEMS if c != 17]
TR += [f"execute if score #v c.t matches {400 + JIDX[j]} run return run function {NS}:page/cristal_{j}" for j, *_ in JOBS]
TR += [f"execute if score #v c.t matches 10001..{10000 + NIT} run return run function {NS}:page/item_depuis",
       f"execute if score #v c.t matches 1000000..3999999 run return run function {NS}:op/entree"]
w(F + "trigger/entree.mcfunction", TR)
for j, *_ in JOBS:
    w(F + f"page/cristal_{j}.mcfunction", [f"function {NS}:cristal/acheter_{j}", f"function {NS}:page/cristaux"])
w(F + "page/item_depuis.mcfunction", ["scoreboard players operation #i c.t = #v c.t",
                                      "scoreboard players remove #i c.t 10000", f"function {NS}:page/item"])

# ---------------------------------------------------------------- page verrouillée : la recette en image, le reste grisé
GRIS = lambda txt: btn(T(txt, "dark_gray"), 1, 96, "Verrouillé : crafte l’oeuf de comptoir pour l’ouvrir.")
w(F + "page/verrou.mcfunction", SOLDE(f"{NS}:v") + [f"function {NS}:page/verrou_d with storage {NS}:v"])
w(F + "page/verrou_d.mcfunction", "$" + dlg(
    T("Commerce : verrouillé", "gold", True),
    [f'{{type:"minecraft:plain_message",width:310,contents:{L(T("Crafte l’", "gray"), T("oeuf de comptoir", "gold", True), T(" puis pose-le à ta base pour ouvrir le Commerce. ", "gray"), SOLDE_TXT)}}}',
     f'{{type:"minecraft:plain_message",width:310,contents:{GRILLE_SNBT}}}'],
    [GRIS("Marché"), GRIS("Bourse"), GRIS("Fortunes"), GRIS("Cristaux"), GRIS("Mon comptoir"), btn(T("Aide", "white"), 60, 96)], 3))

# ---------------------------------------------------------------- aide
AIDE = [
    ("Écus", "Sur un compte, impossible à perdre ou à voler. Tout le monde voit les fortunes."),
    ("Gagner", "Vendre ce que tu récoltes, paliers de métier (250 x le palier), défis (150 à 1 500), boss (600)."),
    ("Prix", "Plus le serveur rachète un objet, plus son prix baisse, puis il remonte en une heure de jeu. Acheter coûte au moins 10 fois la vente (20 fois pour les blocs et les métaux)."),
    ("Bonus", "+0,5 % par niveau du métier lié à l’objet, +25 % pendant l’heure du métier."),
    ("Cristaux", "2 500 Écus le premier, +5 % à chaque achat de la semaine."),
    ("Comptoir", "Un par joueur, clic droit pour ouvrir. Mon comptoir le range pour le reposer ailleurs."),
    ("Spawners", "Accueil, Spawners. Très chers, améliorables par clic droit. Leurs créatures donnent la moitié de l’XP de Chasseur."),
    ("Graphiques", "Accueil, Graphiques, ou bouton Graphiques d’un objet : cours, ventes par jour et par semaine. Clique un jour pour son détail."),
    ("Banque", "Virements à un joueur, épargne à 2 % par semaine, tes 15 dernières opérations."),
    ("Hôtel des ventes", "Prends un objet en main et mets-le en vente à ton prix ; 5 % de taxe à la vente."),
    ("Magasin", "Un panneau [Vente] sur un coffre : tu choisis le prix, les clients achètent d’un clic droit sur le panneau."),
    ("Coffre privé", "Pose un panneau sur ton coffre ou ton tonneau et écris [Privé] : toi seul l’ouvres, et il se reconstruit s’il est cassé. Casse le panneau pour le libérer."),
]
# 25/11/2026 : aide en grille de sujets, l'explication s'affiche au survol (plus de pavé à faire défiler)
w(F + "page/aide.mcfunction", dlg(
    T("Commerce : comment ça marche", "gold", True),
    [f'{{type:"minecraft:plain_message",width:300,contents:{L(T("Survole un sujet pour lire son explication.", "gray"))}}}'],
    [btn(T(tt, "gold"), 60, 100, dd) for tt, dd in AIDE] + [btn(T("Accueil", "white"), 1, 100)], 3))

# ---------------------------------------------------------------- accueil
AC = SOLDE(f"{NS}:a") + [
    f"execute store result storage {NS}:a tv int 1 run scoreboard players get @s c.tv",
    f"execute store result storage {NS}:a ta int 1 run scoreboard players get @s c.ta",
    f"data modify storage {NS}:a ev set from storage {NS}:g evtxt"] + msg_line(f"{NS}:a") + [
    f"function {NS}:page/accueil_d with storage {NS}:a"]
w(F + "page/accueil.mcfunction", AC)
# 25/11/2026 : décor encadré du marché (glyphe U+E7F2 de metiers:arbre, dessiné par Métiers), boutons verts sur 3 colonnes
DECOR = lambda n: ('{type:"minecraft:plain_message",width:240,contents:[{text:"' + {"serveur": "\ue7f0", "metiers": "\ue7f1", "commerce": "\ue7f2",
                   "compagnons": "\ue7f3", "bestiaire": "\ue7f4"}[n] + '",font:"metiers:arbre",color:"white",shadow_color:0},{text:"' + "\\n" * 9 + '"}]}')
# 25/11/2026 : accueil allégé, 6 grandes entrées sur 3 colonnes ; le reste passe dans « Plus » (23)
SPR_B = lambda b: '{object:"atlas",atlas:"minecraft:blocks",sprite:"minecraft:block/' + b + '"}'
SPR_I = lambda i: '{object:"atlas",atlas:"minecraft:items",sprite:"minecraft:item/' + i + '"}'
# 26/11/2026 : accueil en panneau « succès » (dessiné par Métiers : metiers/sources/panneaux.json)
exec(open(os.path.join(HERE, "..", "..", "metiers", "sources", "panneaux_lib.py"), encoding="utf-8").read())
_AC = [(9, "Marché", "Acheter et vendre, par catégorie ou de A à Z."), (90, "Banque", "Virements, épargne, historique."),
       (6000, "Hôtel des ventes", "Achète et vends des objets entre joueurs."), (20, "Bourse", "Évènements, tendances, tops."),
       (70, "Spawners", "Des spawners à acheter et à améliorer."), (23, "Plus", "Fortunes, graphiques, cristaux de métier, trésor de guilde, comptoir, aide.")]
_PAN_C = pan_snbt(pan_corps("commerce", {i: f"trigger commerce set {v}" for i, (v, _n, _t) in enumerate(_AC, 1)},
                            {i: [{"text": n + "\n", "color": "green", "bold": True}, {"text": tp, "color": "gray", "bold": False}] for i, (v, n, tp) in enumerate(_AC, 1)},
                            {i: "on" for i in range(1, 7)}))
w(F + "page/accueil_d.mcfunction",
  '$dialog show @s {type:"minecraft:notice",title:' + T("Commerce", "green", True) + ',can_close_with_escape:true,pause:false,body:['
  + f'{{type:"minecraft:plain_message",width:310,contents:{L(SOLDE_TXT, T("\\nVendu : $(tv) " + ECU + "   ·   acheté : $(ta) " + ECU, "gray"), T("\\n$(ev)", "light_purple"), MSG_TXT)}}},'
  + _PAN_C + '],action:{label:"Fermer",width:200}}')
w(F + "page/plus.mcfunction", dlg(
    T("Commerce  ·  Plus", "green", True),
    [f'{{type:"minecraft:plain_message",width:300,contents:{L(T("Classements, graphiques, cristaux, guilde, comptoir et aide.", "gray"))}}}'],
    [btn(L(spr("gold_ingot"), T("  Fortunes", "green", True)), 21, 130, "Le solde de tout le monde."),
     btn(L(SPR_I("clock_00"), T("  Graphiques", "green", True)), 81, 130, "Courbes et flux du marché, jour par jour."),
     btn(L(G("cristal_m"), T("  Cristaux", "green", True)), 22, 130, "Cristaux de métier : hors de prix, mais c’est le but."),
     btn(L(SPR_I("name_tag"), T("  Trésor de guilde", "green", True)), 7700, 130, "Niveaux et avantages pour tous les membres de ta guilde."),
     btn(L(spr("barrel"), T("  Mon comptoir", "green", True)), 50, 130, "Range ton comptoir dans ton inventaire pour le reposer ailleurs."),
     btn(L(SPR_I("paper"), T("  Aide", "white", True)), 60, 130, "Comment marchent les prix, la vente, la banque.")]
    + [btn(T("Retour", "white"), 1, 130)], cols=3))

# ---------------------------------------------------------------- index du marché : une ligne de texte, puis les boutons
CATSHOW = {c: (vit, col, desc) for c, _, vit, col, desc in CATEGORIES}
w(F + "page/marche.mcfunction", SOLDE(f"{NS}:mk") + [f"function {NS}:page/marche_d with storage {NS}:mk"])
w(F + "page/marche_d.mcfunction", "$" + dlg(
    T("Marché", "green", True),
    [f'{{type:"minecraft:plain_message",width:310,contents:{L(SOLDE_TXT)}}}'],
    [btn(L(SPR_I("spyglass"), T("  Index A à Z", "gold", True)), 3000, 130, "Trouver un objet par la première lettre de son nom."),
     btn(L(spr("diamond"), T("  Bourse", "green", True)), 20, 130, "Évènements, tendances, tops."),
     btn(T("Accueil", "white"), 1, 130)]
    + [btn(L(spr(CATSHOW[c][0]), T("  " + (CATNAME[c] if len(CATNAME[c]) <= 16 else CATNAME[c][:15].rstrip() + "…"), "white")), PG(c, 0), 130, CATNAME[c] + " : " + CATSHOW[c][2]) for c in ITEMS],
    cols=3))

# ---------------------------------------------------------------- une page de catégorie : 10 boutons, prix en infobulle
w(F + "page/ligne.mcfunction", [
    f"function {NS}:item/charger", "scoreboard players set #d c.t 0", f"function {NS}:prix/mid",
    f"function {NS}:prix/bonus", f"function {NS}:prix/vente",
    "scoreboard players operation #x c.t = #u c.t"] + fmt(f"{NS}:l", "v") + [
    "scoreboard players operation #x c.t = #a c.t"] + fmt(f"{NS}:l", "a") + [
    f"function {NS}:fmt/tendance",
    f"data modify storage {NS}:l t set from storage {NS}:t tr"])
VIDE = '{label:{text:"·",color:"dark_gray"},width:160}'
ABREV = [("Bûche écorcée ", "Écorcée "), ("Tige carmin écorcée", "Carmin écorcée"), ("Tige biscornue écorcée", "Biscornue écorcée"),
         ("Bloc de bambou écorcé", "Bambou écorcé"), ("Briques de pierre ", "Briques "), ("Terre cuite émaillée ", "Émaillée "),
         ("Pomme de terre empoisonnée", "Patate empoisonnée"), ("Pomme de terre cuite", "Patate cuite"),
         ("Côtelette de porc crue", "Porc cru"), ("Côtelette de porc cuite", "Porc cuit"), ("Briques de roche noire polie", "Briques roche noire"),
         ("Bloc de verrues ", "Verrues "), ("Crâne de wither squelette", "Crâne de wither"), ("Poche d'encre lumineuse", "Encre lumineuse"),
         ("Pierre taillée moussue", "Pierre moussue"), ("Planches de ", "Planches "), ("Feuilles de ", "Feuilles "),
         ("Propagule de palétuvier", "Propagule"), ("Terre cuite ", "T. cuite "), ("Verre teinté ", "Verre "),
         ("Briques rouges du Nether", "Briques rouges"), ("Oeil d'araignée fermenté", "Oeil fermenté"), ("Cristaux de prismarine", "Cristaux prismarine")]


def court(n, maxi=21):
    """Libellé de bouton : le nom complet reste dans l'infobulle. Les boutons font 160 px, environ 21 caractères."""
    for a, b in ABREV:
        n = n.replace(a, b)
    return n if len(n) <= maxi else n[:maxi - 1].rstrip() + "…"

for c in ITEMS:
    rare = c in RARES
    for p in range(NPAGES[c]):
        its = CATIT[c][p * PAGE:(p + 1) * PAGE]
        CL = SOLDE(f"{NS}:cp")
        for it in its:
            CL += [f"scoreboard players set #i c.t {it['i']}", f"function {NS}:page/ligne"]
            CL += [f"data modify storage {NS}:cp {k}{it['i']} set from storage {NS}:l {k}" for k in ("ve", "vz", "vc", "ae", "az", "ac", "t")]
        CL.append(f"function {NS}:page/cat_{c}_{p}_d with storage {NS}:cp")
        w(F + f"page/cat_{c}_{p}.mcfunction", CL)
        acts = []
        if c != 17:   # 25/11/2026 : « Tout vendre » de la catégorie, tout en haut
            acts += [btn(L(spr("emerald"), T("  Tout vendre : " + court(CATNAME[c], 12), "gold", True)), 7900 + c, 160,
                         "Vend d’un coup tout ce que tu as de cette catégorie dans ton inventaire, au prix du marché. Les objets renommés ou spéciaux sont gardés."),
                     btn(T("Marché", "yellow"), 9, 160)]
        for it in its:
            k = it["i"]
            tip = f"Vente : $(ve{k}),$(vz{k})$(vc{k}) Écus l’unité" + ("" if rare else f"\\nAchat : $(ae{k}),$(az{k})$(ac{k}) Écus l’unité") + f"\\nTendance sur 1 h : $(t{k})"
            acts.append(btn(L(spr(it["id"]), T("  " + court(it["n"]), "white")), 10000 + k, 160, it["n"] + "\\n" + tip))
        if len(its) % 2:
            acts.append(VIDE)
        if c == 17:   # reliques de boss (objets nommés, refusés par la vente normale)
            acts += [btn(L(spr("nether_star"), T("  Vendre la relique en main", "gold", True)), 7800, 160,
                         f"Une relique de boss (objet unique nommé) se vend {RELIQUE_PRIX:,} Écus. Prends-la en main puis clique.".replace(",", " ")),
                     btn(L(spr("chest") if "chest" in SPRITES else spr("nether_star"), T("  Tout vendre", "gold", True)), 7801, 160,
                         "Vend d’un coup tout ce que lâchent les boss (diamants, débris, netherite, objets de cette page...) et les reliques présents dans ton inventaire, au prix du marché.")]
        acts.append(btn(T("◀  Page précédente", "white"), PG(c, p - 1), 160) if p > 0 else VIDE)
        acts.append(btn(T("Page suivante  ▶", "white"), PG(c, p + 1), 160) if p < NPAGES[c] - 1 else VIDE)
        acts += [btn(T("Marché", "yellow"), 9, 160), btn(T("Accueil", "white"), 1, 160)]
        sub = f"   ·   page {p + 1}/{NPAGES[c]}" if NPAGES[c] > 1 else ""
        w(F + f"page/cat_{c}_{p}_d.mcfunction", "$" + dlg(
            T(CATNAME[c], CATSHOW[c][1], True),
            [f'{{type:"minecraft:plain_message",width:310,contents:{L(SOLDE_TXT, T(sub + "   ·   prix au survol", "gray"))}}}'], acts))

# ---------------------------------------------------------------- index A à Z (25/11/2026)
# Une vraie recherche par texte est impossible en vanilla (un joueur non-op ne renvoie que des nombres). Index par
# première lettre du nom français : page 3000 = les lettres, 3010 + 10 x lettre + page = les objets de cette lettre.
import unicodedata as _ud
def _lettre(n):
    n = n.replace("Œ", "O").replace("œ", "o")
    return _ud.normalize("NFD", n)[0].upper()
PARLET = {}
for it in sorted(ITL, key=lambda x: _ud.normalize("NFD", x["n"].replace("Œ", "Oe")).lower()):
    PARLET.setdefault(_lettre(it["n"]), []).append(it)
ALPHA = [chr(65 + i) for i in range(26)]
PL = lambda li, p: 3010 + 10 * li + p
AZ_ACTS = []
for li, l in enumerate(ALPHA):
    n = len(PARLET.get(l, []))
    AZ_ACTS.append(btn(T(f"{l}   ", "yellow", True) if n else T(l, "dark_gray"), PL(li, 0) if n else 3000, 60,
                       f"{n} objet{'s' if n > 1 else ''} commençant par {l}" if n else f"Aucun objet en {l}"))
AZ_ACTS += [btn(T("Marché", "yellow"), 9, 60), btn(T("Accueil", "white"), 1, 60)]
w(F + "page/index.mcfunction", dlg(T("Index A à Z", "yellow", True),
    [f'{{type:"minecraft:plain_message",width:310,contents:{T("Choisis la première lettre de l’objet cherché (sans accent : Écorce est au E).", "gray")}}}'],
    AZ_ACTS, cols=7))
for li, l in enumerate(ALPHA):
    its_l = PARLET.get(l, [])
    np_ = max(1, -(-len(its_l) // PAGE))
    for p in range(np_):
        its = its_l[p * PAGE:(p + 1) * PAGE]
        CL = SOLDE(f"{NS}:cp")
        for it in its:
            CL += [f"scoreboard players set #i c.t {it['i']}", f"function {NS}:page/ligne"]
            CL += [f"data modify storage {NS}:cp {k}{it['i']} set from storage {NS}:l {k}" for k in ("ve", "vz", "vc", "ae", "az", "ac", "t")]
        CL.append(f"function {NS}:page/lettre_{l.lower()}_{p}_d with storage {NS}:cp")
        w(F + f"page/lettre_{l.lower()}_{p}.mcfunction", CL)
        acts = []
        for it in its:
            k = it["i"]
            rare = it["cat"] in RARES
            tip = f"Vente : $(ve{k}),$(vz{k})$(vc{k}) Écus l’unité" + ("" if rare else f"\\nAchat : $(ae{k}),$(az{k})$(ac{k}) Écus l’unité") + f"\\nTendance sur 1 h : $(t{k})"
            acts.append(btn(L(spr(it["id"]), T("  " + court(it["n"]), "white")), 10000 + k, 160, it["n"] + "\\n" + tip))
        if len(its) % 2:
            acts.append(VIDE)
        acts.append(btn(T("◀  Page précédente", "white"), PL(li, p - 1), 160) if p > 0 else VIDE)
        acts.append(btn(T("Page suivante  ▶", "white"), PL(li, p + 1), 160) if p < np_ - 1 else VIDE)
        acts += [btn(T("Index A à Z", "yellow"), 3000, 160), btn(T("Marché", "white"), 9, 160)]
        sub = f"   ·   page {p + 1}/{np_}" if np_ > 1 else ""
        w(F + f"page/lettre_{l.lower()}_{p}_d.mcfunction", "$" + dlg(
            T(f"Objets en {l}", "yellow", True),
            [f'{{type:"minecraft:plain_message",width:310,contents:{L(SOLDE_TXT, T(sub + "   ·   prix au survol", "gray"))}}}'], acts))
        TR.insert(-2, f"execute if score #v c.t matches {PL(li, p)} run return run function {NS}:page/lettre_{l.lower()}_{p}")
TR.insert(-2, f"execute if score #v c.t matches 3000 run return run function {NS}:page/index")
w(F + "trigger/entree.mcfunction", TR)

# ---------------------------------------------------------------- courbes (barres de la police commerce:recette)
w(F + "hist/courbe.mcfunction", [
    f'data modify storage {NS}:t SP set value [{{text:""}}]', f'data modify storage {NS}:t VAR set value ""',
    f'data modify storage {NS}:t VARC set value "gray"',
    f"execute store result score #hn c.t run data get storage {NS}:t H",
    f'execute if score #hn c.t matches ..1 run return run data modify storage {NS}:t SP set value [{{text:"pas encore assez de relevés (un par heure de jeu)",color:"dark_gray",italic:true}}]',
    "scoreboard players set #hmin c.t 2147483647", "scoreboard players set #hmax c.t -2147483648",
    f"data modify storage {NS}:t W2 set from storage {NS}:t H", f"function {NS}:hist/minmax",
    "scoreboard players operation #hsp c.t = #hmax c.t", "scoreboard players operation #hsp c.t -= #hmin c.t",
    f"data modify storage {NS}:t W2 set from storage {NS}:t H", f"function {NS}:hist/barres",
    # variation entre le premier et le dernier relevé, en millièmes
    f"execute store result score #h0 c.t run data get storage {NS}:t H[0]",
    f"execute store result score #h1 c.t run data get storage {NS}:t H[-1]",
    "execute if score #h0 c.t matches ..0 run scoreboard players set #h0 c.t 1",
    "scoreboard players operation #hv c.t = #h1 c.t", "scoreboard players operation #hv c.t -= #h0 c.t",
    "scoreboard players operation #hv c.t *= #1000 c.g", "scoreboard players operation #hv c.t /= #h0 c.t",
    f'execute if score #hv c.t matches 1.. run data modify storage {NS}:t VARC set value "green"',
    f'execute if score #hv c.t matches ..-1 run data modify storage {NS}:t VARC set value "red"',
    f'data modify storage {NS}:t vs set value "+"', f'execute if score #hv c.t matches ..-1 run data modify storage {NS}:t vs set value "-"',
    "execute if score #hv c.t matches ..-1 run scoreboard players operation #hv c.t *= #-1 c.g",
    "scoreboard players operation #hve c.t = #hv c.t", "scoreboard players operation #hve c.t /= #10 c.g",
    "scoreboard players operation #hvd c.t = #hv c.t", "scoreboard players operation #hvd c.t %= #10 c.g",
    f"execute store result storage {NS}:t ve int 1 run scoreboard players get #hve c.t",
    f"execute store result storage {NS}:t vd int 1 run scoreboard players get #hvd c.t",
    f"function {NS}:hist/var with storage {NS}:t"])
w(F + "hist/var.mcfunction", f'$data modify storage {NS}:t VAR set value "  $(vs)$(ve),$(vd) %"')
w(F + "hist/minmax.mcfunction", [
    f"execute unless data storage {NS}:t W2[0] run return 0",
    f"execute store result score #x c.t run data get storage {NS}:t W2[0]",
    "scoreboard players operation #hmin c.t < #x c.t", "scoreboard players operation #hmax c.t > #x c.t",
    f"data remove storage {NS}:t W2[0]", f"function {NS}:hist/minmax"])
HB = [f"execute unless data storage {NS}:t W2[0] run return 0",
      f"execute store result score #x c.t run data get storage {NS}:t W2[0]",
      "scoreboard players set #hh c.t 3",
      "execute if score #hsp c.t matches 1.. run scoreboard players operation #x c.t -= #hmin c.t",
      "execute if score #hsp c.t matches 1.. run scoreboard players operation #x c.t *= #7 c.g",
      "execute if score #hsp c.t matches 1.. run scoreboard players operation #x c.t /= #hsp c.t",
      "execute if score #hsp c.t matches 1.. run scoreboard players operation #hh c.t = #x c.t"]
HB += [f'execute if score #hh c.t matches {k} run data modify storage {NS}:t SP append value {{text:"{chr(0xE030 + k)}",font:"commerce:recette"}}' for k in range(8)]
HB += [f"data remove storage {NS}:t W2[0]", f"function {NS}:hist/barres"]
w(F + "hist/barres.mcfunction", HB)
w(F + "hist/charger.mcfunction", [f"data modify storage {NS}:t H set value []", f"$data modify storage {NS}:t H set from storage {NS}:hist $(id)"])

# ---------------------------------------------------------------- un objet : prix totaux écrits sur les boutons
TOT = [1, 16, 64]
IPG = [f"function {NS}:item/charger", f"data modify storage {NS}:t ip set from storage {NS}:t it",
       f"execute store result score #have c.t run function {NS}:op/compter with storage {NS}:t it",
       f"execute store result storage {NS}:t ip.have int 1 run scoreboard players get #have c.t"]
for q in TOT + ["tout"]:
    if q == "tout":
        IPG += ["scoreboard players operation #q c.t = #have c.t", "execute if score #q c.t matches 641.. run scoreboard players set #q c.t 640"]
    else:
        IPG.append(f"scoreboard players set #q c.t {q}")
    IPG += ["scoreboard players operation #d c.t = #q c.t", "scoreboard players operation #d c.t *= #1000 c.g",
            "scoreboard players operation #d c.t /= #V c.t", f"function {NS}:prix/mid", f"function {NS}:prix/bonus",
            f"function {NS}:prix/vente", "scoreboard players operation #x c.t = #u c.t",
            "scoreboard players operation #x c.t *= #q c.t"] + fmt(f"{NS}:t", f"ip.s{q}")
    if q != "tout":
        IPG += ["scoreboard players operation #d c.t = #q c.t", "scoreboard players operation #d c.t *= #500 c.g",
                "scoreboard players operation #d c.t /= #V c.t", "scoreboard players operation #d c.t *= #-1 c.g",
                f"function {NS}:prix/mid", f"function {NS}:prix/sans_bonus", f"function {NS}:prix/vente",
                "scoreboard players operation #x c.t = #a c.t", "scoreboard players operation #x c.t *= #q c.t",
               ] + fmt(f"{NS}:t", f"ip.b{q}")
# prix à l'unité, tendance, demande
IPG += ["scoreboard players set #d c.t 0", f"function {NS}:prix/mid", f"function {NS}:prix/bonus", f"function {NS}:prix/vente",
        "scoreboard players operation #x c.t = #u c.t"] + fmt(f"{NS}:t", "ip.v") + [
        "scoreboard players operation #x c.t = #a c.t"] + fmt(f"{NS}:t", "ip.a") + [
        "scoreboard players operation #x c.t = #bon c.t", "scoreboard players remove #x c.t 1000",
        "scoreboard players operation #x c.t /= #10 c.g",
        f'data modify storage {NS}:t ip.bp set value ""',
        f'execute if score #x c.t matches 1.. run function {NS}:page/item_bonus',
        f"function {NS}:fmt/tendance",
        f"data modify storage {NS}:t ip.tr set from storage {NS}:t tr", f"data modify storage {NS}:t ip.trc set from storage {NS}:t trc",
        f"function {NS}:hist/charger with storage {NS}:t it", f"function {NS}:hist/courbe",
        f"data modify storage {NS}:t ip.sp set from storage {NS}:t SP", f"data modify storage {NS}:t ip.var set from storage {NS}:t VAR",
        f"data modify storage {NS}:t ip.varc set from storage {NS}:t VARC",
        f'data modify storage {NS}:t ip.ev set value ""',
        f'execute if score #e c.t matches 1001.. run data modify storage {NS}:t ip.ev set value "   ·   pénurie : x1,6"',
        f'execute if score #e c.t matches ..999 run data modify storage {NS}:t ip.ev set value "   ·   krach : /2"'] + msg_line(f"{NS}:t", "ip.") + [
        f"execute if score #rare c.t matches 1 run return run function {NS}:page/item_v with storage {NS}:t ip",
        f"function {NS}:page/item_a with storage {NS}:t ip"]
w(F + "page/item.mcfunction", IPG)
w(F + "page/item_bonus.mcfunction", [
    f"execute store result storage {NS}:t f.e int 1 run scoreboard players get #x c.t",
    f"function {NS}:page/item_bonus_m with storage {NS}:t f"])
w(F + "page/item_bonus_m.mcfunction", f'$data modify storage {NS}:t ip.bp set value " (+$(e) % métier)"')


def btn_cmd(label, cmd, tip=None):
    s = f"{{label:{label},width:160"
    if tip:
        s += f',tooltip:{{text:"{tip}"}}'
    return s + f',action:{{type:"run_command",command:"{cmd}"}}}}'


for kind in ("a", "v"):
    desc = [T("Vente ", "gray"), T(f"$(ve),$(vz)$(vc) {ECU}", "gold", True), T("$(bp)", "gray")]
    if kind == "a":
        desc += [T("   Achat ", "gray"), T(f"$(ae),$(az)$(ac) {ECU}", "yellow", True)]
    desc += [T("  l’unité\\nTu en as $(have)$(ev)", "gray"), T("\\nCours 24 h  ", "gray"), "{text:\"\",color:\"$(varc)\",extra:$(sp)}", "{text:\"$(var)\",color:\"$(varc)\",bold:true}", T("\\n$(msg)", "yellow")]
    body = [f'{{type:"minecraft:item",item:{{id:"minecraft:$(id)"}},show_decorations:false,description:{{width:280,contents:{L(*desc)}}}}}']
    vend = lambda q: btn_cmd(L(T(f"Vendre {q}  ", "gold", True), T(f"$(s{q}e),$(s{q}z)$(s{q}c) {ECU}", "white")), f"trigger commerce set 2$(i3){q:03d}",
                             "Prix total, bonus de métier compris. Le prix baisse un peu à mesure que tu vends.")
    ach = lambda q: btn_cmd(L(T(f"Acheter {q}  ", "yellow", True), T(f"$(b{q}e),$(b{q}z)$(b{q}c) {ECU}", "white")), f"trigger commerce set 1$(i3){q:03d}",
                            "Prix total. Le prix monte un peu à mesure que tu achètes.")
    tout = btn_cmd(L(T("Tout vendre ($(have))  ", "gold", True), T(f"$(stoute),$(stoutz)$(stoutc) {ECU}", "white")), "trigger commerce set 3$(i3)000",
                   "Vend tout ce que tu as de cet objet (10 stacks au plus par clic).")
    retour = btn_cmd(T("Retour : $(cn)", "white"), "trigger commerce set $(cb)")
    graph = btn_cmd(L('{object:"atlas",atlas:"minecraft:items",sprite:"minecraft:item/clock_00"}', T("  Graphiques", "aqua", True)), "trigger commerce set 4003$(i3)", "Ventes par jour et par semaine, cours sur 24 h et sur 14 jours.")
    if kind == "a":
        acts = [vend(1), ach(1), vend(16), ach(16), vend(64), ach(64), tout, graph, retour, btn_cmd(T("Marché", "yellow"), "trigger commerce set 9")]
    else:
        acts = [vend(1), vend(16), vend(64), tout, graph, retour]
    w(F + f"page/item_{kind}.mcfunction", "$" + dlg('{text:"$(n)",color:"gold",bold:true}', body, acts))

# ---------------------------------------------------------------- bourse (tops de 3 pour tenir sans défiler)
NTOP = 3
BO = [f"scoreboard players reset * c.x"]
for key, obj in (("tv", "c.vs"), ("ta", "c.as")):
    for k in range(1, NTOP + 1):
        BO += ["scoreboard players set #m c.t 0", "scoreboard players set #best c.t 0"]
        BO.append(f"function {NS}:bourse/{key}_passe")
        BO += [f'data modify storage {NS}:r {key}{k}n set value "·"', f'data modify storage {NS}:r {key}{k}q set value ""',
               f"execute if score #best c.t matches 1.. run function {NS}:bourse/{key}_retenir_{k}"]
        w(F + f"bourse/{key}_retenir_{k}.mcfunction", [
            "scoreboard players operation #i c.t = #best c.t", f"function {NS}:item/charger",
            f"function {NS}:item/marquer with storage {NS}:t it",
            f"data modify storage {NS}:r {key}{k}n set from storage {NS}:t it.n",
            f"execute store result storage {NS}:r {key}{k}q int 1 run scoreboard players get #m c.t"])
    BO.append("scoreboard players reset * c.x")
    PS = []
    for it in ITL:
        PS += [f"execute unless score {H(it)} c.x matches 1 if score {H(it)} {obj} > #m c.t run scoreboard players set #best c.t {it['i']}",
               f"execute if score #best c.t matches {it['i']} run scoreboard players operation #m c.t = {H(it)} {obj}"]
    w(F + f"bourse/{key}_passe.mcfunction", PS)
BO += [f"data modify storage {NS}:t H set from storage {NS}:hist _indice", f"function {NS}:hist/courbe",
       f"data modify storage {NS}:r sp set from storage {NS}:t SP", f"data modify storage {NS}:r var set from storage {NS}:t VAR",
       f"data modify storage {NS}:r varc set from storage {NS}:t VARC",
       "scoreboard players operation #x c.t = #indice c.g", "scoreboard players operation #x c.t /= #10 c.g",
       f"execute store result storage {NS}:r ind int 1 run scoreboard players get #x c.t",
       f'function {NS}:rang/calcul {{obj:"c.tv",n:3}}',
       f"data modify storage {NS}:r ev set from storage {NS}:g evtxt",
       f'execute if data storage {NS}:r {{ev:""}} run data modify storage {NS}:r ev set value "Pas d’évènement en cours."',
       f"function {NS}:page/bourse_d with storage {NS}:r"]
w(F + "page/bourse.mcfunction", BO)
NL = "\\n"
top = lambda key, col: ",".join(T(f"{k}. ", "gray") + "," + T(f"$({key}{k}n)", col) + "," + T(f"  $({key}{k}q)" + (NL if k < NTOP else ""), "gray") for k in range(1, NTOP + 1))
w(F + "page/bourse_d.mcfunction", "$" + dlg(
    T("Bourse", "light_purple", True),
    [f'{{type:"minecraft:plain_message",width:310,contents:{L(T("Indice du marché  ", "white", True), T("$(ind) %  ", "gold", True), "{text:\"\",color:\"$(varc)\",extra:$(sp)}", "{text:\"$(var)\",color:\"$(varc)\",bold:true}", T("\\n$(ev)\\n\\n", "light_purple"), T("Plus vendus cette semaine\\n", "gold", True), top("tv", "white"), T("\\n\\nPlus achetés cette semaine\\n", "yellow", True), top("ta", "white"), T("\\n\\nPlus gros marchands\\n", "green", True))[:-1]},{{text:"",extra:$(C)}}]}}'],
    [btn(T("Marché", "yellow"), 9, 150), btn(T("Graphiques", "aqua"), 81, 150), btn(T("Fortunes", "gold"), 21, 150), btn(T("Accueil", "white"), 1, 150)], 2))

# ---------------------------------------------------------------- fortunes
w(F + "page/fortunes.mcfunction", [f'function {NS}:rang/calcul {{obj:"c.ecus",n:10}}'] + SOLDE(f"{NS}:r") + [
    f"function {NS}:page/fortunes_d with storage {NS}:r"])
w(F + "page/fortunes_d.mcfunction", "$" + dlg(
    T("Fortunes", "gold", True),
    [f'{{type:"minecraft:plain_message",width:310,contents:[{SOLDE_TXT},{T("\\n\\nLes 10 plus riches du serveur\\n", "gold", True)},{{text:"",extra:$(C)}}]}}'],
    [btn(T("Bourse", "light_purple"), 20, 160), btn(T("Accueil", "white"), 1, 160)]))

# ---------------------------------------------------------------- cristaux
CR = SOLDE(f"{NS}:cr") + [f"function {NS}:cristal/prix",
                          f"execute store result storage {NS}:cr p int 1 run scoreboard players get #cp c.t",
                          f"execute store result storage {NS}:cr n int 1 run scoreboard players get @s c.ncr"]
CR += [f"execute store result storage {NS}:cr {j} int 1 run scoreboard players get @s m.cr_{j}" for j, *_ in JOBS]
CR += msg_line(f"{NS}:cr") + [f"function {NS}:page/cristaux_d with storage {NS}:cr"]
w(F + "page/cristaux.mcfunction", CR)
w(F + "page/cristaux_d.mcfunction", "$" + dlg(
    T("Cristaux de métier", "aqua", True),
    [f'{{type:"minecraft:plain_message",width:310,contents:{L(SOLDE_TXT, T("   ·   un cristal : ", "gray"), T("$(p) " + ECU, "aqua", True), T("\\nAchetés cette semaine : $(n), +5 % à chaque achat.", "gray"), T("\\n$(msg)", "yellow"))}}}'],
    [btn(L(G("cristal_" + j), T(f" {nom} ", col), T(f"($({j}))", "gray")), 400 + JIDX[j], 160, f"Acheter 1 cristal de {nom}.") for j, nom, col in JOBS] + [btn(T("Accueil", "white"), 1, 160)]))

# =====================================================================
# ADMIN
# =====================================================================
w(F + "admin/oeuf.mcfunction", f"function {NS}:oeuf/donner")
w(F + "admin/ecus.mcfunction", ["scoreboard players add @s c.ecus 10000", say("+10 000 Écus (admin).", "gold")])
w(F + "admin/marche_reset.mcfunction", [f"scoreboard players set {H(it)} c.{o} 0" for it in ITL for o in ("p", "h", "ev")] +
  ["scoreboard players set #evi c.g 0", "scoreboard players set #evt c.g 0", f'data modify storage {NS}:g evtxt set value ""', say("Marché remis à zéro.", "gold")])
w(F + "admin/evenement.mcfunction", f"function {NS}:marche/evt_debut")
w(F + "desinstaller.mcfunction", [f"scoreboard objectives remove {o}" for o in PLAYER_OBJ + ITEM_OBJ + ["c.t", "c.g", "commerce", "c.oeuf", "c.craft"]] + ["kill @e[type=minecraft:interaction,tag=commerce.clic]"] + [
    f"data remove storage {NS}:{s} x" for s in ()] + [
    f"data modify storage {NS}:g evtxt set value \"\"",
    f"function {NS}:prive/desinstaller", f"function {NS}:spawner/desinstaller",
    say("Commerce désinstallé (les comptoirs posés restent des villageois). Retire commerce.zip puis redémarre.", "gold")])

# =====================================================================
# GRAPHIQUES, SPAWNERS
# =====================================================================
exec(open(os.path.join(HERE, "grafiques.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "spawners.py"), encoding="utf-8").read())
for _m in ("banque.py", "hdv.py", "boutiques.py", "serveur.py", "guilde.py"):
    exec(open(os.path.join(HERE, _m), encoding="utf-8").read())

# =====================================================================
# COFFRES PRIVÉS
# =====================================================================
exec(open(os.path.join(HERE, "prive.py"), encoding="utf-8").read())

# =====================================================================
# ZIP
# =====================================================================
zp = os.path.join(HERE, "..", "commerce.zip")
if os.path.exists(zp):
    os.remove(zp)
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, _, fs in os.walk(ROOT):
        for fn in sorted(fs):
            full = os.path.join(dp, fn)
            z.write(full, os.path.relpath(full, ROOT))
print("objets :", NIT, "dont achetables :", NCOM, "| fichiers :", sum(len(f) for _, _, f in os.walk(ROOT)))

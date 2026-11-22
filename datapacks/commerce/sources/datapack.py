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
VERSION = 6
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
        ("x", "Explorateur", "blue"), ("t", "Marchand", "dark_green")]
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
PLAYER_OBJ += [f"c.pp_{j}" for j, *_ in JOBS] + [f"c.dd_{j}" for j, *_ in JOBS] + ["c.dall", "c.wd", "c.wk", "c.bk", "c.init2"]
ITEM_OBJ = ["c.p", "c.h", "c.vs", "c.as", "c.ev", "c.x"]
LD = [f"scoreboard objectives add {o} dummy" for o in PLAYER_OBJ + ITEM_OBJ + ["c.t", "c.g"]]
LD += ["scoreboard objectives add commerce trigger",
       "scoreboard objectives add c.oeuf minecraft.used:minecraft.villager_spawn_egg",
       "scoreboard objectives add c.craft minecraft.crafted:minecraft.villager_spawn_egg"]
for c in (2, 5, 10, 12, 100, 105, 250, 500, 1000, 1000000, -1):
    LD.append(f"scoreboard players set #{c} c.g {c}")
LD.append(f"scoreboard players set #achat c.g {ACHAT}")
for o in ("#dec", "#hr", "#cv", "#t", "#evi", "#evt", "#semp"):
    LD.append(f"scoreboard players add {o} c.g 0")
for it in ITL:
    LD += [f"scoreboard players add {H(it)} {o} 0" for o in ("c.p", "c.h", "c.vs", "c.as", "c.ev")]
LD += [f'execute unless data storage {NS}:g evtxt run data modify storage {NS}:g evtxt set value ""',
       f"execute unless data storage {NS}:j l run data modify storage {NS}:j l set value []",
       f'data modify storage {NS}:t msg set value ""']
w(F + "load.mcfunction", LD)

w(F + "tick.mcfunction", [
    "scoreboard players enable @a commerce",
    f"execute as @a[scores={{commerce=1..}}] at @s run function {NS}:trigger/entree",
    f"execute as @e[type=minecraft:villager,tag=commerce.nouveau] at @s run function {NS}:comptoir/pose",
    f"execute as @e[type=minecraft:interaction,tag=commerce.clic] if data entity @s interaction run function {NS}:comptoir/clic_i",
    "execute as @e[type=minecraft:interaction,tag=commerce.clic] if data entity @s attack run data remove entity @s attack",
    "scoreboard players set @a[scores={c.oeuf=1..}] c.oeuf 0",
    "execute if entity @a run scoreboard players add #t c.g 1",
    f"execute if score #t c.g matches 20.. run function {NS}:seconde"])

w(F + "seconde.mcfunction", [
    "scoreboard players set #t c.g 0",
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

w(F + "version.mcfunction", say(f"Version {VERSION} : Écus, comptoirs, marché de {NIT} objets à prix dynamiques, bourse, fortunes, cristaux.", "gold"))

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
    f"function {NS}:joueur/evts"])
w(F + "joueur/arrivee.mcfunction", [f"scoreboard players add @s {o} 0" for o in PLAYER_OBJ] + [
    f"recipe give @s {NS}:oeuf", "scoreboard players set @s c.vu 1"])

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
    PL += [f"scoreboard players set #k c.t 0", f"scoreboard players operation #k c.t = @s m.{j}_lvl",
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
    "pattern": ["EDE", "GNG", "ECE"],  # C = tonneau
    "key": {"E": "minecraft:emerald_block", "D": "minecraft:diamond_block", "G": "minecraft:gold_block",
            "N": "minecraft:netherite_ingot", "C": "minecraft:barrel"},
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
    "data remove entity @s interaction", "data remove entity @s attack",
    f"execute on target run function {NS}:comptoir/clic"])
w(F + "comptoir/clic.mcfunction", [
    f"execute unless score @s c.deb matches 1 run return run function {NS}:page/verrou",
    f"function {NS}:page/accueil"])

# =====================================================================
# OBJETS : chargement et sauvegarde des scores d'un objet (#i = numéro)
# =====================================================================
for it in ITL:
    cn = CATNAME[it["cat"]]
    w(F + f"i/{it['i']}/charger.mcfunction", [
        f"scoreboard players set #b c.t {it['b']}", f"scoreboard players set #V c.t {it['V']}",
        f"scoreboard players set #mj c.t {it['mj']}", f"scoreboard players set #rare c.t {1 if it['rare'] else 0}",
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
    "scoreboard players operation #a c.t *= #achat c.g"])
BO = ["scoreboard players set #bon c.t 1000", "scoreboard players set #lv c.t 0"]
BO += [f"execute if score #mj c.t matches {JIDX[j]} run scoreboard players operation #lv c.t = @s m.{j}_lvl" for j, *_ in JOBS]
BO += ["execute if score #lv c.t matches 101.. run scoreboard players set #lv c.t 100",
       "execute if score #lv c.t matches ..-1 run scoreboard players set #lv c.t 0",
       "scoreboard players operation #lv c.t *= #5 c.g", "scoreboard players operation #bon c.t += #lv c.t",
       "execute if score #mj c.t matches 1.. if score #mj c.t = #job m.heure run scoreboard players add #bon c.t 250"]
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
FILTRE = "[!minecraft:custom_data,!minecraft:custom_name]"
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
    f"function {NS}:item/sauver", f"function {NS}:op/crediter",
    "scoreboard players operation #x c.t = #tot c.t"] + fmt(f"{NS}:t m", "") + [
    f"data modify storage {NS}:t m.q set from storage {NS}:t it.q",
    f"function {NS}:op/msg_vente with storage {NS}:t m",
    "playsound minecraft:entity.villager.yes master @s ~ ~ ~ 0.8 1.2",
    "playsound minecraft:block.chain.place master @s ~ ~ ~ 0.6 1.6"])
w(F + "op/msg_vente.mcfunction", f'$data modify storage {NS}:t msg set value "Vendu : $(q) pour $(e),$(z)$(c) Écus."')
w(F + "op/acheter.mcfunction", [
    f"function {NS}:item/charger",
    f'execute if score #rare c.t matches 1 run return run data modify storage {NS}:t msg set value "Le serveur ne revend pas cet objet, il le rachète seulement."',
    "scoreboard players operation #d c.t = #q c.t", "scoreboard players operation #d c.t *= #500 c.g",
    "scoreboard players operation #d c.t /= #V c.t", "scoreboard players operation #d c.t *= #-1 c.g",
    f"function {NS}:prix/mid", f"function {NS}:prix/sans_bonus", f"function {NS}:prix/vente",
    "scoreboard players operation #tot c.t = #a c.t", "scoreboard players operation #tot c.t *= #q c.t",
    "scoreboard players operation #ce c.t = #tot c.t", "scoreboard players add #ce c.t 99",
    "scoreboard players operation #ce c.t /= #100 c.g",
    f"execute store result storage {NS}:t m.e int 1 run scoreboard players get #ce c.t",
    f"execute store result storage {NS}:t it.q int 1 run scoreboard players get #q c.t",
    f"data modify storage {NS}:t m.q set from storage {NS}:t it.q",
    f"execute if score @s c.ecus < #ce c.t run return run function {NS}:op/msg_pauvre with storage {NS}:t m",
    "scoreboard players operation @s c.ecus -= #ce c.t", "scoreboard players operation @s c.ta += #ce c.t",
    f"function {NS}:op/donner with storage {NS}:t it",
    "scoreboard players operation #p c.t += #d c.t",
    "execute if score #p c.t matches ..-301 run scoreboard players set #p c.t -300",
    "scoreboard players operation #as c.t += #q c.t",
    f"function {NS}:item/sauver",
    f"function {NS}:op/msg_achat with storage {NS}:t m",
    "playsound minecraft:entity.villager.trade master @s ~ ~ ~ 0.8 1",
    "playsound minecraft:entity.item.pickup master @s ~ ~ ~ 0.6 0.8"])
w(F + "op/msg_achat.mcfunction", f'$data modify storage {NS}:t msg set value "Acheté : $(q) pour $(e) Écus."')
w(F + "op/msg_pauvre.mcfunction", [
    f'$data modify storage {NS}:t msg set value "Pas assez d\'Écus : il te faut $(e) Écus pour $(q)."',
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
w(F + "marche/releve.mcfunction", RL)
w(F + "marche/releve_un.mcfunction", [
    f"function {NS}:item/charger", "scoreboard players set #d c.t 0", f"function {NS}:prix/mid",
    f"function {NS}:prix/sans_bonus", f"function {NS}:prix/vente",
    "scoreboard players operation #h c.t = #u0 c.t", f"function {NS}:item/sauver"])
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
SEM = []
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

# ---------------------------------------------------------------- grille de craft de l'oeuf, en vraies textures
# Composant de texte « object » (1.21.9+) : affiche une texture d'un atlas du jeu, sans resource pack.
# Seulement dans les dialogues envoyés par commande : une erreur y est sans gravité. Pas dans les fichiers
# de registre (dialog/*.json) lus au démarrage, où une faute bloquerait le serveur.
# Depuis la 1.21.11 les objets sont dans l'atlas minecraft:items, les blocs dans minecraft:blocks.
SPR = {"E": ("blocks", "block/emerald_block"), "D": ("blocks", "block/diamond_block"), "G": ("blocks", "block/gold_block"),
       "N": ("items", "item/netherite_ingot"), "C": ("blocks", "block/barrel_side"), "O": ("items", "item/villager_spawn_egg")}
GRID = ["EDE", "GNG", "ECE"]

# Fond de l'établi : un seul glyphe (resource pack, police commerce:recette) dessiné au style vanilla
# (panneau gris clair, cases en creux, flèche, case de résultat), posé sous la première ligne de la grille.
# Les textures des objets se placent par-dessus avec des espaces exacts (fournisseur « space »).
# Repères mesurés en jeu : un sprite « object » fait 8 px de large, avance de 8, haut à y = -1 ; ligne de 9 px.
RP = os.path.join(HERE, "..", "build", "commerce_rp", "assets", "commerce")
# Fond : le haut de la texture d'établi du resource pack commun (interface Forge), 176 x 80 px, plus le bas du cadre,
# affiché à l'échelle 1/2 : une case de 18 px devient 9 px, le pas des lignes de texte et des sprites de 8 px.
# Une police n'accepte pas de glyphe de plus de 256 px de côté (la v4 en faisait 264 : il ne s'affichait pas).
GX, PW, PTOP, PH = 15, 88, -10, 44     # x des cases, largeur, haut (y relatif à la 1re ligne), hauteur (px d'interface)
RX = 62                               # x de l'œuf dans la case de résultat
ESP = {-(PW + 1): "\ue001", GX: "\ue002", 1: "\ue003", PW - GX - 26: "\ue004", RX - GX - 26: "\ue005", PW - RX - 8: "\ue006"}
PANNEAU = "\ue000"


def dessiner_etabli():
    import io as _io
    from PIL import Image, ImageDraw
    with zipfile.ZipFile(os.path.join(HERE, "..", "..", "..", "metiers_resourcepack.zip")) as z:
        ct = Image.open(_io.BytesIO(z.read("assets/minecraft/textures/gui/container/crafting_table.png"))).convert("RGBA")
    im = Image.new("RGBA", (176, 88), (0, 0, 0, 0))
    im.paste(ct.crop((0, 0, 176, 80)), (0, 1))        # 1 ligne vide en haut : les cases tombent sur des pixels pairs
    im.paste(ct.crop((0, 159, 176, 166)), (0, 81))    # bas du cadre
    assert max(im.size) <= 256, "glyphe de police trop grand (256 px au plus)"
    os.makedirs(os.path.join(RP, "textures", "font"), exist_ok=True)
    im.save(os.path.join(RP, "textures", "font", "etabli.png"))
    # pièce d'Écu, 8 px d'interface (texture 32 x 32) : or, bord sombre, reflet, É gravé
    p = Image.new("RGBA", (32, 32), (0, 0, 0, 0)); q = ImageDraw.Draw(p)
    q.ellipse([0, 2, 31, 31], fill=(122, 78, 10, 255))           # tranche
    q.ellipse([0, 0, 31, 29], fill=(176, 120, 20, 255))          # bord
    q.ellipse([3, 3, 28, 26], fill=(246, 196, 60, 255))          # face
    q.ellipse([6, 5, 18, 14], fill=(255, 232, 140, 255))         # reflet
    q.ellipse([8, 7, 23, 22], outline=(196, 140, 30, 255), width=2)
    for x0, y0, x1, y1 in [(12, 10, 14, 20), (12, 10, 20, 12), (12, 14, 18, 16), (12, 18, 20, 20), (15, 6, 18, 8)]:
        q.rectangle([x0, y0, x1 - 1, y1 - 1], fill=(150, 98, 12, 255))  # « É »
    p.save(os.path.join(RP, "textures", "font", "ecu.png"))
    os.makedirs(os.path.join(RP, "font"), exist_ok=True)
    json.dump({"providers": [
        {"type": "bitmap", "file": "commerce:font/etabli.png", "height": PH, "ascent": 7 - PTOP, "chars": [PANNEAU]},
        {"type": "bitmap", "file": "commerce:font/ecu.png", "height": 8, "ascent": 7, "chars": [ECU]},
        {"type": "space", "advances": {c: v for v, c in ESP.items()}}]},
        open(os.path.join(RP, "font", "recette.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if os.path.exists(os.path.join(HERE, "..", "build", "commerce_rp")):
    shutil.rmtree(os.path.join(HERE, "..", "build", "commerce_rp"))
dessiner_etabli()


def grille(fmt="snbt"):
    """Grille de l'établi : panneau en fond, textures des objets posées dans les cases. Lignes de même largeur
    pour que le centrage du dialogue ne les décale pas."""
    t = lambda x, c: f'{{text:"{x}",color:"{c}",bold:false,italic:false}}'
    sp = lambda k: f'{{object:"atlas",atlas:"minecraft:{SPR[k][0]}",sprite:"minecraft:{SPR[k][1]}"}}'
    e = lambda v: f'{{text:"{ESP[v]}",font:"commerce:recette"}}'
    out = [t("Recette de l’oeuf de comptoir (établi)\\n\\n\\n", "gold")]
    for r, row in enumerate(GRID):
        if r == 0:
            out += [f'{{text:"{PANNEAU}",font:"commerce:recette",color:"white",shadow_color:0}}', e(-(PW + 1))]
        out.append(e(GX))
        for c, k in enumerate(row):
            out.append(sp(k))
            if c < 2:
                out.append(e(1))
        if r == 1:
            out += [e(RX - GX - 26), sp("O"), e(PW - RX - 8)]
        else:
            out.append(e(PW - GX - 26))
        out.append(t("\\n", "white"))
    out.append(t("\\n\\nÉmeraude : 4 blocs · Diamant : 1 bloc · Or : 2 blocs\\nNetherite : 1 lingot · Tonneau : 1", "gray"))
    return "[" + ",".join(['{text:""}'] + out) + "]"


GRILLE_SNBT = grille("snbt")

# ---------------------------------------------------------------- touche G (dialogue fixe, lu au démarrage)
wj(f"data/{NS}/dialog/ouvrir.json", {
    "type": "minecraft:multi_action", "title": {"text": "Commerce", "color": "gold", "bold": True},
    "external_title": {"text": "Commerce"}, "can_close_with_escape": True, "pause": False,
    "body": [{"type": "minecraft:plain_message", "width": 300,
              "contents": [{"text": "Ton compte en Écus, le marché, la bourse, les fortunes et les cristaux. Il se débloque en craftant l'oeuf de comptoir.", "color": "gray"}]},
             {"type": "minecraft:plain_message", "width": 300, "contents": {"text": "La grille de craft de l'oeuf s'affiche quand tu ouvres le Commerce.", "color": "dark_gray"}}],
    "actions": [{"label": {"text": "Ouvrir le Commerce", "color": "gold", "bold": True}, "width": 200,
                 "action": {"type": "run_command", "command": "trigger commerce set 1"}}],
    "columns": 1})
wj("data/minecraft/tags/dialog/quick_actions.json", {"values": [f"{NS}:ouvrir"]})
wj("data/minecraft/tags/dialog/pause_screen_additions.json", {"values": [f"{NS}:ouvrir"]})

# ---------------------------------------------------------------- aiguillage du trigger
TR = ["scoreboard players operation #v c.t = @s commerce", "scoreboard players set @s commerce 0",
      "scoreboard players enable @s commerce",
      f"execute if score #v c.t matches 60 run return run function {NS}:page/aide",
      f"execute unless score @s c.deb matches 1 run return run function {NS}:page/verrou",
      f"execute if score #v c.t matches 1 run return run function {NS}:page/accueil",
      f"execute if score #v c.t matches 9 run return run function {NS}:page/marche",
      f"execute if score #v c.t matches 20 run return run function {NS}:page/bourse",
      f"execute if score #v c.t matches 21 run return run function {NS}:page/fortunes",
      f"execute if score #v c.t matches 22 run return run function {NS}:page/cristaux",
      f"execute if score #v c.t matches 50 run return run function {NS}:comptoir/deplacer"]
TR += [f"execute if score #v c.t matches {100 + c} run return run function {NS}:page/cat_{c}" for c in ITEMS]
TR += [f"execute if score #v c.t matches {400 + JIDX[j]} run return run function {NS}:page/cristal_{j}" for j, *_ in JOBS]
TR += [f"execute if score #v c.t matches 10001..{10000 + NIT} run return run function {NS}:page/item_depuis",
       f"execute if score #v c.t matches 1000000..3999999 run return run function {NS}:op/entree"]
w(F + "trigger/entree.mcfunction", TR)
for j, *_ in JOBS:
    w(F + f"page/cristal_{j}.mcfunction", [f"function {NS}:cristal/acheter_{j}", f"function {NS}:page/cristaux"])
w(F + "page/item_depuis.mcfunction", ["scoreboard players operation #i c.t = #v c.t",
                                      "scoreboard players remove #i c.t 10000", f"function {NS}:page/item"])

GRIS = lambda txt: btn(T(txt, "dark_gray"), 1, 96, "Verrouillé : crafte l’oeuf de comptoir pour l’ouvrir.")
w(F + "page/verrou.mcfunction", SOLDE(f"{NS}:v") + [f"function {NS}:page/verrou_d with storage {NS}:v"])
w(F + "page/verrou_d.mcfunction", "$" + dlg(
    T("Commerce : verrouillé", "gold", True),
    [f'{{type:"minecraft:plain_message",width:310,contents:{L(T("Pour ouvrir le Commerce, crafte un ", "gray"), T("oeuf de comptoir", "gold", True), T(" à l’établi puis pose-le à ta base. En attendant, tes paliers, défis et boss te rapportent déjà des Écus.\\n", "gray"), SOLDE_TXT)}}}',
     f'{{type:"minecraft:plain_message",width:310,contents:{GRILLE_SNBT}}}'],
    [GRIS("Marché"), GRIS("Bourse"), GRIS("Fortunes"), GRIS("Cristaux"), GRIS("Mon comptoir"), btn(T("Aide", "white"), 60, 96)], 3))

# ---------------------------------------------------------------- aide
AIDE = [
    ("Les Écus", "Ton argent est sur un compte, impossible à perdre ou à voler. Tout le monde voit les fortunes."),
    ("Gagner", "Vends ce que tu récoltes, passe des paliers de métier (250 x le palier), fais les défis (150 à 1 500) et les boss (600)."),
    ("Prix qui bougent", "Plus le serveur rachète un objet, plus son prix baisse, puis il remonte en une heure de jeu environ. Acheter coûte au moins 4 fois le prix de vente de base, et plus quand l'objet est demandé."),
    ("Bonus de métier", "Tes produits se vendent +0,5 % par niveau du métier lié, et +25 % pendant l'heure du métier."),
    ("Bourse", "Évènements de marché (pénurie, krach), tendances sur une heure, objets les plus vendus et achetés."),
    ("Cristaux", "Achetables, mais hors de prix : 2 500 Écus le premier, +5 % à chaque achat de la semaine."),
    ("Comptoir", "Un par joueur, clic droit pour ouvrir. Touche G pour le ranger et le reposer ailleurs."),
]
w(F + "page/aide.mcfunction", dlg(
    T("Commerce : comment ça marche", "gold", True),
    [f'{{type:"minecraft:plain_message",width:320,contents:{L(T(t + " : ", "gold", True), T(d, "gray"))}}}' for t, d in AIDE],
    [btn(T("Accueil", "white"), 1, 100)], 1))

# ---------------------------------------------------------------- accueil
AC = SOLDE(f"{NS}:a") + [
    f"execute store result storage {NS}:a tv int 1 run scoreboard players get @s c.tv",
    f"execute store result storage {NS}:a ta int 1 run scoreboard players get @s c.ta",
    f'data modify storage {NS}:a cp set value "pas posé"',
    f'execute if score @s c.cmpt matches 1 run data modify storage {NS}:a cp set value "posé"',
    f"data modify storage {NS}:a ev set from storage {NS}:g evtxt"] + msg_line(f"{NS}:a") + [
    f"function {NS}:page/accueil_d with storage {NS}:a"]
w(F + "page/accueil.mcfunction", AC)
w(F + "page/accueil_d.mcfunction", "$" + dlg(
    T("Mon compte", "gold", True),
    [f'{{type:"minecraft:item",item:{{id:"minecraft:emerald"}},show_decorations:false,description:{{width:260,contents:{L(SOLDE_TXT, T("\\nVendu au total : $(tv) " + ECU + "   ·   acheté : $(ta) " + ECU, "gray"), T("\\nComptoir : $(cp)", "gray"))}}}}}',
     f'{{type:"minecraft:plain_message",width:300,contents:{L(T("$(ev)", "light_purple"), T("\\n", "white"), MSG_TXT)}}}'],
    [btn(T("Marché", "yellow", True), 9, 150, "Acheter et vendre, objet par objet."),
     btn(T("Bourse", "light_purple", True), 20, 150, "Tendances, évènements, tops."),
     btn(T("Fortunes", "gold"), 21, 150, "Le solde de tout le monde."),
     btn(L(G("cristal_m"), T(" Cristaux de métier", "aqua")), 22, 150, "Hors de prix, mais c'est le but."),
     btn(T("Mon comptoir : déplacer", "white"), 50, 150, "Range ton comptoir dans ton inventaire pour le reposer ailleurs."),
     btn(T("Aide", "gray"), 60, 150)]))

# ---------------------------------------------------------------- index du marché
CATSHOW = {c: (vit, col, desc) for c, _, vit, col, desc in CATEGORIES}
w(F + "page/marche.mcfunction", SOLDE(f"{NS}:mk") + [f"function {NS}:page/marche_d with storage {NS}:mk"])
w(F + "page/marche_d.mcfunction", "$" + dlg(
    T("Marché", "yellow", True),
    [f'{{type:"minecraft:plain_message",width:300,contents:{L(SOLDE_TXT, T("\\nAchat et vente depuis n’importe où. Les prix suivent l’offre et la demande.", "gray"))}}}']
    + [f'{{type:"minecraft:item",item:{{id:"minecraft:{CATSHOW[c][0]}"}},show_decorations:false,description:{{width:250,contents:{L(T(CATNAME[c] + "\\n", CATSHOW[c][1], True), T(CATSHOW[c][2], "gray"))}}}}}' for c in ITEMS],
    [btn(T(CATNAME[c], CATSHOW[c][1]), 100 + c) for c in ITEMS] + [RETOUR]))

# ---------------------------------------------------------------- une catégorie
w(F + "page/ligne.mcfunction", [
    f"function {NS}:item/charger", "scoreboard players set #d c.t 0", f"function {NS}:prix/mid",
    f"function {NS}:prix/bonus", f"function {NS}:prix/vente",
    "scoreboard players operation #x c.t = #u c.t"] + fmt(f"{NS}:l", "v") + [
    "scoreboard players operation #x c.t = #a c.t"] + fmt(f"{NS}:l", "a") + [
    f"function {NS}:fmt/tendance",
    f"data modify storage {NS}:l t set from storage {NS}:t tr", f"data modify storage {NS}:l tc set from storage {NS}:t trc"])
for c in ITEMS:
    its = [it for it in ITL if it["cat"] == c]
    rare = c in RARES
    CL = SOLDE(f"{NS}:cp")
    for it in its:
        CL += [f"scoreboard players set #i c.t {it['i']}", f"function {NS}:page/ligne"]
        for k in ("ve", "vz", "vc", "ae", "az", "ac", "t", "tc"):
            CL.append(f"data modify storage {NS}:cp {k}{it['i']} set from storage {NS}:l {k}")
    CL.append(f"function {NS}:page/cat_{c}_d with storage {NS}:cp")
    w(F + f"page/cat_{c}.mcfunction", CL)
    body = [f'{{type:"minecraft:plain_message",width:300,contents:{L(SOLDE_TXT, T("\\nPrix à l’unité, bonus de métier compris. Clique sur un nom pour vendre" + ("." if rare else " ou acheter."), "gray"))}}}']
    for it in its:
        k = it["i"]
        desc = [T(it["n"] + "\n", "white", True), T("Vente ", "gray"), T(f"$(ve{k}),$(vz{k})$(vc{k}) {ECU}", "gold")]
        if not rare:
            desc += [T("   Achat ", "gray"), T(f"$(ae{k}),$(az{k})$(ac{k}) {ECU}", "yellow")]
        desc += [T("   ", "gray"), f'{{text:"$(t{k})",color:"$(tc{k})",bold:true,italic:false}}']
        body.append(f'{{type:"minecraft:item",item:{{id:"minecraft:{it["id"]}"}},show_decorations:false,description:{{width:260,contents:{L(*desc).replace(chr(10), chr(92) + "n")}}}}}')
    acts = [btn(T(it["n"], "white"), 10000 + it["i"], 150) for it in its] + [btn(T("Marché", "yellow"), 9, 150), RETOUR]
    w(F + f"page/cat_{c}_d.mcfunction", "$" + dlg(T(CATNAME[c], CATSHOW[c][1], True), body, acts))

# ---------------------------------------------------------------- un objet
QTE = [("001", "1"), ("008", "8"), ("016", "16"), ("032", "32"), ("064", "64 (1 stack)"), ("128", "128 (2 stacks)"),
       ("320", "320 (5 stacks)"), ("640", "640 (10 stacks)")]
QOPT = ",".join(f'{{id:"{i}",display:{{text:"{d}"}}{",initial:true" if i == "064" else ""}}}' for i, d in QTE)
IPG = [f"function {NS}:item/charger", "scoreboard players set #d c.t 0", f"function {NS}:prix/mid",
       f"function {NS}:prix/bonus", f"function {NS}:prix/vente",
       f"data modify storage {NS}:t ip set from storage {NS}:t it",
       "scoreboard players operation #x c.t = #u c.t"] + fmt(f"{NS}:t", "ip.v") + [
       "scoreboard players operation #x c.t = #a c.t"] + fmt(f"{NS}:t", "ip.a") + [
       "scoreboard players operation #x c.t = #bon c.t", "scoreboard players remove #x c.t 1000",
       "scoreboard players operation #x c.t /= #10 c.g",
       f'data modify storage {NS}:t ip.bp set value ""',
       f'execute if score #x c.t matches 1.. run function {NS}:page/item_bonus',
       f"function {NS}:fmt/tendance",
       f"data modify storage {NS}:t ip.tr set from storage {NS}:t tr", f"data modify storage {NS}:t ip.trc set from storage {NS}:t trc",
       f"execute store result storage {NS}:t ip.have int 1 run function {NS}:op/compter with storage {NS}:t it",
       f"execute store result storage {NS}:t ip.vs int 1 run scoreboard players get #vs c.t",
       f"execute store result storage {NS}:t ip.as int 1 run scoreboard players get #as c.t",
       # barre de demande : pleine quand le prix est au plus haut (pression -300), vide au plancher (700)
       "scoreboard players set #x c.t 700", "scoreboard players operation #x c.t -= #p c.t",
       "scoreboard players operation #x c.t /= #100 c.g"]
IPG += [f'execute if score #x c.t matches {k} run data modify storage {NS}:t ip.bar set value "{GLY["barre_" + str(k)]}"' for k in range(11)]
IPG += [f'data modify storage {NS}:t ip.ev set value ""',
        f'execute if score #e c.t matches 1001.. run data modify storage {NS}:t ip.ev set value "\\nPénurie en cours : prix de vente x1,6."',
        f'execute if score #e c.t matches ..999 run data modify storage {NS}:t ip.ev set value "\\nKrach en cours : prix divisé par deux."',
        f'data modify storage {NS}:t ip.q set value "$(q)"'] + msg_line(f"{NS}:t", "ip.") + [
        f"execute if score #rare c.t matches 1 run return run function {NS}:page/item_v with storage {NS}:t ip",
        f"function {NS}:page/item_a with storage {NS}:t ip"]
w(F + "page/item.mcfunction", IPG)
w(F + "page/item_bonus.mcfunction", [
    f"execute store result storage {NS}:t f.e int 1 run scoreboard players get #x c.t",
    f"function {NS}:page/item_bonus_m with storage {NS}:t f"])
w(F + "page/item_bonus_m.mcfunction", f'$data modify storage {NS}:t ip.bp set value " (dont +$(e) % de métier)"')
for kind in ("a", "v"):
    desc = [T("Vente : ", "gray"), T(f"$(ve),$(vz)$(vc) {ECU}", "gold", True), T(" l’unité$(bp)", "gray")]
    if kind == "a":
        desc += [T("\\nAchat : ", "gray"), T(f"$(ae),$(az)$(ac) {ECU}", "yellow", True), T(" l’unité", "gray")]
    else:
        desc += [T("\\nLe serveur ne revend pas cet objet.", "dark_gray")]
    body = [f'{{type:"minecraft:item",item:{{id:"minecraft:$(id)"}},show_decorations:false,description:{{width:260,contents:{L(*desc)}}}}}',
            f'{{type:"minecraft:plain_message",width:300,contents:{L(T("Demande  ", "gray"), "{text:\"$(bar)\",font:\"metiers:icones\",color:\"white\"}", T("  sur 1 h : ", "gray"), "{text:\"$(tr)\",color:\"$(trc)\",bold:true}", T("\\nTu en as $(have)   ·   vendus cette semaine : $(vs)   ·   achetés : $(as)", "gray"), T("$(ev)", "light_purple"), T("\\n$(msg)", "yellow"))}}}']
    acts = ['{label:{text:"Vendre",color:"gold",bold:true},width:150,tooltip:{text:"Vend la quantité choisie (ce que tu as, au plus)."},action:{type:"minecraft:dynamic/run_command",template:"trigger commerce set 2$(i3)$(q)"}}']
    if kind == "a":
        acts.append('{label:{text:"Acheter",color:"yellow",bold:true},width:150,tooltip:{text:"Achète la quantité choisie."},action:{type:"minecraft:dynamic/run_command",template:"trigger commerce set 1$(i3)$(q)"}}')
    acts += ['{label:{text:"Tout vendre",color:"gold"},width:150,tooltip:{text:"Vend tout ce que tu as (10 stacks au plus par clic)."},action:{type:"run_command",command:"trigger commerce set 3$(i3)000"}}',
             '{label:{text:"Retour : $(cn)",color:"white"},width:150,action:{type:"run_command",command:"trigger commerce set $(cb)"}}']
    inp = f'inputs:[{{type:"minecraft:single_option",key:"q",label:{{text:"Quantité"}},width:200,options:[{QOPT}]}}],'
    d = dlg('{text:"$(n)",color:"gold",bold:true}', body, acts)
    d = d.replace("body:[", inp + "body:[", 1)
    w(F + f"page/item_{kind}.mcfunction", "$" + d)

# ---------------------------------------------------------------- bourse
BO = [f"scoreboard players reset * c.x"]
for key, obj in (("tv", "c.vs"), ("ta", "c.as")):
    for k in range(1, 6):
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
BO += [f'function {NS}:rang/calcul {{obj:"c.tv",n:3}}',
       f"data modify storage {NS}:r ev set from storage {NS}:g evtxt",
       f'execute if data storage {NS}:r {{ev:""}} run data modify storage {NS}:r ev set value "Pas d’évènement en cours. Un nouveau peut tomber à chaque heure de jeu."',
       f"function {NS}:page/bourse_d with storage {NS}:r"]
w(F + "page/bourse.mcfunction", BO)
NL = "\\n"
top = lambda key, col: ",".join(T(f"{k}. ", "gray") + "," + T(f"$({key}{k}n)", col) + "," + T(f"  $({key}{k}q)" + (NL if k < 5 else ""), "gray") for k in range(1, 6))
w(F + "page/bourse_d.mcfunction", "$" + dlg(
    T("Bourse", "light_purple", True),
    [f'{{type:"minecraft:item",item:{{id:"minecraft:bell"}},show_decorations:false,description:{{width:260,contents:{L(T("$(ev)", "light_purple"))}}}}}',
     f'{{type:"minecraft:plain_message",width:300,contents:{L(T("Les plus vendus cette semaine\\n", "gold", True), top("tv", "white"))}}}',
     f'{{type:"minecraft:plain_message",width:300,contents:{L(T("Les plus achetés cette semaine\\n", "yellow", True), top("ta", "white"))}}}',
     f'{{type:"minecraft:plain_message",width:300,contents:[{T("Plus gros marchands (total vendu)\\n", "green", True)},{{text:"",extra:$(C)}}]}}'],
    [btn(T("Marché", "yellow"), 9, 150), btn(T("Fortunes", "gold"), 21, 150), RETOUR]))

# ---------------------------------------------------------------- fortunes
w(F + "page/fortunes.mcfunction", [f'function {NS}:rang/calcul {{obj:"c.ecus",n:10}}'] + SOLDE(f"{NS}:r") + [
    f"function {NS}:page/fortunes_d with storage {NS}:r"])
w(F + "page/fortunes_d.mcfunction", "$" + dlg(
    T("Fortunes", "gold", True),
    [f'{{type:"minecraft:plain_message",width:300,contents:[{SOLDE_TXT},{T("\\n\\nLes 10 plus riches du serveur\\n", "gold", True)},{{text:"",extra:$(C)}}]}}'],
    [btn(T("Bourse", "light_purple"), 20, 150), RETOUR]))

# ---------------------------------------------------------------- cristaux
CR = SOLDE(f"{NS}:cr") + [f"function {NS}:cristal/prix",
                          f"execute store result storage {NS}:cr p int 1 run scoreboard players get #cp c.t",
                          f"execute store result storage {NS}:cr n int 1 run scoreboard players get @s c.ncr"]
CR += [f"execute store result storage {NS}:cr {j} int 1 run scoreboard players get @s m.cr_{j}" for j, *_ in JOBS]
CR += msg_line(f"{NS}:cr") + [f"function {NS}:page/cristaux_d with storage {NS}:cr"]
w(F + "page/cristaux.mcfunction", CR)
w(F + "page/cristaux_d.mcfunction", "$" + dlg(
    T("Cristaux de métier", "aqua", True),
    [f'{{type:"minecraft:plain_message",width:320,contents:{L(SOLDE_TXT, T("\\nPrix d’un cristal : ", "gray"), T("$(p) " + ECU, "aqua", True), T("\\nAchetés cette semaine : $(n). Chaque achat augmente le prix de 5 %, remise à zéro à la nouvelle semaine.", "gray"), T("\\n$(msg)", "yellow"))}}}'],
    [btn(L(G("cristal_" + j), T(f" {nom} ", col), T(f"($({j}))", "gray")), 400 + JIDX[j], 150, f"Acheter 1 cristal de {nom}.") for j, nom, col in JOBS] + [RETOUR]))

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
    say("Commerce désinstallé (les comptoirs posés restent des villageois). Retire commerce.zip puis redémarre.", "gold")])

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

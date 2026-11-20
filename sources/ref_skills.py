# -*- coding: utf-8 -*-
# Refonte v24, partie 2 : effets des nouvelles compétences.

_p = os.path.join(ROOT, F, "p/peche.mcfunction")
_t = open(_p, encoding="utf-8").read().replace(
    "scoreboard players add #thr m.tmp 20\n",
    "scoreboard players add #thr m.tmp 20\nexecute if entity @s[tag=metiers.sk.p6] run scoreboard players operation #thr m.tmp *= #2 m.const\n", 1)
open(_p, "w", encoding="utf-8").write(_t)

w(F + "bonus.mcfunction", f"""
function {NS}:refonte/joueur

# Bûcheron (Double coupe et Charbonnier passent par les sources d'XP, Abattage par le tick)

# Fermier
execute if entity @s[tag=metiers.sk.f2] run function {NS}:f/semeur
execute if entity @s[tag=metiers.sk.f3] if score #t m.timer matches 120 run effect give @s minecraft:saturation 1 0 true
execute if entity @s[tag=metiers.sk.f4] if score #soixante m.timer matches 0 run function {NS}:f/engrais
execute if score @s m.saison matches 1.. run scoreboard players remove @s m.saison 1

# Mineur
execute if entity @s[tag=metiers.sk.m1] if items entity @s weapon.mainhand #minecraft:pickaxes run effect give @s minecraft:haste 2 0 true
execute if entity @s[tag=metiers.sk.m2] if items entity @s weapon.mainhand #minecraft:pickaxes run effect give @s minecraft:haste 2 1 true
execute if entity @s[tag=metiers.sk.m6] if items entity @s weapon.mainhand #minecraft:pickaxes run effect give @s minecraft:haste 2 2 true
execute if entity @s[tag=metiers.sk.m3] run effect give @s minecraft:night_vision 15 0 true
execute if entity @s[tag=metiers.sk.m6,y=-64,dy=64] run effect give @s minecraft:resistance 2 0 true
execute if entity @s[tag=metiers.sk.m5] run function {NS}:m/fonte

# Chasseur
attribute @s minecraft:attack_damage modifier remove {NS}:c1
attribute @s minecraft:attack_damage modifier remove {NS}:c5
execute if entity @s[tag=metiers.sk.c1] run attribute @s minecraft:attack_damage modifier add {NS}:c1 1 add_value
execute if entity @s[tag=metiers.sk.c2] if items entity @s weapon.mainhand #{NS}:epees run effect give @e[type=#{NS}:hostiles,distance=..16] minecraft:glowing 2 0 true
execute if entity @s[tag=metiers.sk.c4] if predicate {NS}:nuit run effect give @s minecraft:strength 2 0 true
execute if entity @s[tag=metiers.sk.c4] if predicate {NS}:nuit run effect give @s minecraft:speed 2 0 true
execute if entity @s[tag=metiers.sk.c6] if entity @e[type=#{NS}:hostiles,distance=..8] run effect give @s minecraft:strength 2 0 true
execute if entity @s[tag=metiers.sk.c6] if entity @e[type=#{NS}:hostiles,distance=..8] run effect give @s minecraft:speed 2 0 true

# Pêcheur
attribute @s minecraft:luck modifier remove {NS}:p1
attribute @s minecraft:luck modifier remove {NS}:p6
execute if entity @s[tag=metiers.sk.p1] run attribute @s minecraft:luck modifier add {NS}:p1 2 add_value
execute if entity @s[tag=metiers.sk.p6] run attribute @s minecraft:luck modifier add {NS}:p6 3 add_value
execute if entity @s[tag=metiers.sk.p2] if block ~ ~1 ~ minecraft:water run effect give @s minecraft:water_breathing 3 0 true
execute if entity @s[tag=metiers.sk.p4] if block ~ ~ ~ minecraft:water run effect give @s minecraft:dolphins_grace 2 0 true
execute if entity @s[tag=metiers.sk.p6] if block ~ ~ ~ minecraft:water run effect give @s minecraft:conduit_power 3 0 true

# Éleveur
execute if entity @s[tag=metiers.sk.e2] run effect give @e[type=#{NS}:animaux,distance=..6] minecraft:regeneration 3 0 true
execute if entity @s[tag=metiers.sk.e4] if score #t m.timer matches 120 run function {NS}:e/croissance
execute if entity @s[tag=metiers.sk.e5] if score #soixante m.timer matches 0 run function {NS}:e/fertilite
execute if entity @s[tag=metiers.sk.e6] on vehicle run effect give @s minecraft:speed 2 1 true
execute if entity @s[tag=metiers.sk.e6] on vehicle run effect give @s minecraft:jump_boost 2 1 true

# Enchanteur
execute if entity @s[tag=metiers.sk.n2] if score #huit m.timer matches 0 run function {NS}:n/renouveau
execute if entity @s[tag=metiers.sk.n3] run function {NS}:n/bouclier
execute if entity @s[tag=metiers.sk.n4] run function {NS}:n/clignement
execute if entity @s[tag=metiers.sk.n5] run function {NS}:n/foudre
execute if score @s m.blcd matches 1.. run scoreboard players remove @s m.blcd 1
execute if score @s m.bscd matches 1.. run scoreboard players remove @s m.bscd 1
execute if score @s m.fdcd matches 1.. run scoreboard players remove @s m.fdcd 1
scoreboard players set @s s.jump 0
scoreboard players set @s s.hit 0

# Explorateur
attribute @s minecraft:step_height modifier remove {NS}:x1
attribute @s minecraft:fall_damage_multiplier modifier remove {NS}:x3
execute if entity @s[tag=metiers.sk.x1] run attribute @s minecraft:step_height modifier add {NS}:x1 0.5 add_value
execute if entity @s[tag=metiers.sk.x2] run effect give @s minecraft:speed 2 0 true
execute if entity @s[tag=metiers.sk.x4] run effect give @s minecraft:speed 2 1 true
execute if entity @s[tag=metiers.sk.x3] run effect give @s minecraft:jump_boost 2 0 true
execute if entity @s[tag=metiers.sk.x3] run attribute @s minecraft:fall_damage_multiplier modifier add {NS}:x3 -0.5 add_multiplied_base
execute if entity @s[tag=metiers.sk.x5] if predicate {NS}:accroupi run function {NS}:x/instinct
execute if entity @s[tag=metiers.sk.x6] run effect give @s minecraft:fire_resistance 3 0 true
execute if entity @s[tag=metiers.sk.x6] run effect give @s minecraft:water_breathing 3 0 true

# Marchand
execute if entity @s[tag=metiers.sk.t2] run effect give @s minecraft:hero_of_the_village 3 0 true
execute if entity @s[tag=metiers.sk.t4] run effect give @s minecraft:hero_of_the_village 3 2 true
execute if entity @s[tag=metiers.sk.t6] run effect give @s minecraft:hero_of_the_village 3 4 true
execute if entity @s[tag=metiers.sk.t5] run function {NS}:t/colporteur
""")
wj(f"data/{NS}/predicate/nuit.json", {"type": "minecraft:time_check", "clock": "minecraft:overworld", "value": {"min": 13000, "max": 23000}, "period": 24000})
wj(f"data/{NS}/predicate/accroupi.json", {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"flags": {"is_sneaking": True}}})

# ---------------- Bûcheron : abattage (b2), replanteur (b3), effeuillage (b4), esprit de la forêt (b6)
SAPLING = {"oak_log": "oak_sapling", "spruce_log": "spruce_sapling", "birch_log": "birch_sapling", "jungle_log": "jungle_sapling",
           "acacia_log": "acacia_sapling", "dark_oak_log": "dark_oak_sapling", "mangrove_log": "mangrove_propagule",
           "cherry_log": "cherry_sapling", "pale_oak_log": "pale_oak_sapling", "crimson_stem": "crimson_fungus", "warped_stem": "warped_fungus"}
AT = ["scoreboard players set #sum m.tmp 0"]
AT += [f"scoreboard players operation #sum m.tmp += @s a.{l}" for l in LOGS]
AT += [f'execute if score @s a.{l} matches 1.. run data modify storage {NS}:bois pousse set value "{SAPLING[l]}"' for l in LOGS]
AT += [f"scoreboard players set @s a.{l} 0" for l in LOGS]
AT.append(f"execute if score #sum m.tmp matches 1.. if score @s a.sneak matches 1.. if entity @s[tag=metiers.sk.b2] if items entity @s weapon.mainhand #minecraft:axes run function {NS}:b/abattage/debut")
AT.append(f"execute if score #sum m.tmp matches 1.. if entity @s[tag=metiers.sk.b3] run function {NS}:b/replante/debut")
AT.append("scoreboard players set @s a.sneak 0")
w(F + "b/abattage/tick.mcfunction", "\n".join(AT))
w(F + "b/replante/debut.mcfunction", f"""
scoreboard players set #pas m.tmp 0
execute anchored eyes positioned ^ ^ ^0.3 run function {NS}:b/replante/rayon
""")
w(F + "b/replante/rayon.mcfunction", f"""
scoreboard players add #pas m.tmp 1
execute if block ~ ~ ~ #minecraft:air if block ~ ~-1 ~ #minecraft:dirt align xyz positioned ~0.5 ~ ~0.5 run return run function {NS}:b/replante/poser with storage {NS}:bois
execute if block ~ ~ ~ #minecraft:air if block ~ ~-1 ~ #minecraft:nylium align xyz positioned ~0.5 ~ ~0.5 run return run function {NS}:b/replante/poser with storage {NS}:bois
execute if score #pas m.tmp matches ..55 positioned ^ ^ ^0.1 run function {NS}:b/replante/rayon
""")
w(F + "b/replante/poser.mcfunction", "$setblock ~ ~ ~ minecraft:$(pousse)\nparticle minecraft:happy_villager ~ ~0.3 ~ 0.3 0.3 0.3 0 8")
_p = os.path.join(ROOT, F, "b/abattage/bloc.mcfunction")
_t = open(_p, encoding="utf-8").read().replace(
    'setblock ~ ~ ~ minecraft:air destroy\n',
    'setblock ~ ~ ~ minecraft:air destroy\nexecute if entity @s[tag=metiers.sk.b4] run fill ~-2 ~-2 ~-2 ~2 ~2 ~2 minecraft:air replace #minecraft:leaves[persistent=false] destroy\n', 1)
open(_p, "w", encoding="utf-8").write(_t)
add_lines(F + "b/abattage/demarrer.mcfunction", [
    "execute if entity @s[tag=metiers.sk.b6] if score #n m.tmp matches 4.. run effect give @s minecraft:strength 20 1 true",
    "execute if entity @s[tag=metiers.sk.b6] if score #n m.tmp matches 4.. run effect give @s minecraft:haste 20 1 true"])

# ---------------- Fermier : semeur (f2), engrais (f4), saison des moissons (f6)
SEM = [("s.seed", "wheat_seeds", "wheat"), ("s.seedc", "carrot", "carrots"), ("s.seedp", "potato", "potatoes"), ("s.seedb", "beetroot_seeds", "beetroots")]
SE = []
for obj, item_, bloc in SEM:
    SE.append(f'execute if score @s {obj} matches 1.. run function {NS}:f/semer {{item:"{item_}",bloc:"{bloc}"}}')
SE += [f"scoreboard players set @s {obj} 0" for obj, _, _ in SEM]
w(F + "f/semeur.mcfunction", "\n".join(SE))
SM = ["scoreboard players set #pas m.tmp 0",
      f"$execute anchored eyes positioned ^ ^ ^0.3 run function {NS}:f/semer_rayon {{item:\"$(item)\",bloc:\"$(bloc)\"}}"]
w(F + "f/semer.mcfunction", "\n".join(SM))
w(F + "f/semer_rayon.mcfunction", "\n".join([
    "scoreboard players add #pas m.tmp 1",
    f"$execute if block ~ ~ ~ minecraft:$(bloc) align xyz positioned ~0.5 ~ ~0.5 run return run function {NS}:f/semer_zone {{item:\"$(item)\",bloc:\"$(bloc)\"}}",
    f"$execute if score #pas m.tmp matches ..55 positioned ^ ^ ^0.1 run function {NS}:f/semer_rayon {{item:\"$(item)\",bloc:\"$(bloc)\"}}"]))
SZ = []
for dx in (-1, 0, 1):
    for dz in (-1, 0, 1):
        if dx == 0 and dz == 0: continue
        SZ.append(f"$execute positioned ~{dx} ~ ~{dz} if block ~ ~ ~ #minecraft:air if block ~ ~-1 ~ minecraft:farmland if items entity @p container.* minecraft:$(item) run function {NS}:f/semer_un {{item:\"$(item)\",bloc:\"$(bloc)\"}}")
w(F + "f/semer_zone.mcfunction", "\n".join(SZ))
w(F + "f/semer_un.mcfunction", "$setblock ~ ~ ~ minecraft:$(bloc)\n$clear @p minecraft:$(item) 1")
EG = []
for c, mx in (("wheat", 7), ("carrots", 7), ("potatoes", 7), ("beetroots", 3), ("nether_wart", 3)):
    for a in range(mx - 1, -1, -1):
        EG.append(f"fill ~-4 ~-2 ~-4 ~4 ~2 ~4 minecraft:{c}[age={a + 1}] replace minecraft:{c}[age={a}]")
EG.append("particle minecraft:happy_villager ~ ~0.5 ~ 3 0.5 3 0 15")
w(F + "f/engrais.mcfunction", "\n".join(EG))
w(F + "f/saison.mcfunction", "\n".join([
    f"execute unless entity @s[tag=metiers.sk.f6] run return run {tr('Il faut la compétence Saison des moissons.', 'red')}",
    f"execute if score @s m.saison matches 1.. run return run {tr('Saison des moissons déjà utilisée : reviens dans un jour de jeu (20 min).', 'red')}",
    "scoreboard players set @s m.saison 2400"] +
    [f"fill ~-12 ~-3 ~-12 ~12 ~3 ~12 minecraft:{c}[age={mx}] replace minecraft:{c}" for c, mx in (("wheat", 7), ("carrots", 7), ("potatoes", 7), ("beetroots", 3), ("nether_wart", 3), ("sweet_berry_bush", 3))] +
    ["particle minecraft:happy_villager ~ ~1 ~ 8 1 8 0 200", "playsound minecraft:block.amethyst_block.chime master @a ~ ~ ~ 1 0.8",
     tr("La saison des moissons fait mûrir toutes les cultures autour de toi.", "green")]))

# ---------------- Éleveur : fertilité (e5)
w(F + "e/fertilite.mcfunction", f"""
execute as @e[type=#{NS}:animaux,distance=..6] store result score @s m.tmp run data get entity @s Age
execute as @e[type=#{NS}:animaux,distance=..6] if score @s m.tmp matches 2.. store result entity @s Age int 0.5 run scoreboard players get @s m.tmp
""")

# ---------------- Enchanteur
w(F + "n/renouveau.mcfunction", "\n".join(
    [f'execute if items entity @s {sl} *[minecraft:damage~{{damage:{{min:1}}}}] run item modify entity @s {sl} {{function:"minecraft:set_damage",type:"minecraft:set_damage",damage:0.01,add:true}}'
     for sl in ("weapon.mainhand", "armor.head", "armor.chest", "armor.legs", "armor.feet")]))
w(F + "n/bouclier.mcfunction", f"""
execute if score @s m.bscd matches 1.. run return 0
execute store result score @s m.hp run data get entity @s Health
execute if score @s m.hp matches 1..8 run function {NS}:n/bouclier_on
""")
w(F + "n/bouclier_on.mcfunction", """
effect give @s minecraft:absorption 15 1 true
scoreboard players set @s m.bscd 240
particle minecraft:enchant ~ ~1 ~ 0.5 0.8 0.5 1 80
playsound minecraft:item.shield.block master @s ~ ~ ~ 1 1.4
""")
w(F + "n/clignement.mcfunction", f"""
execute if score @s m.blcd matches 1.. run return 0
execute unless score @s s.jump matches 1.. run return 0
execute unless predicate {NS}:accroupi run return 0
execute unless items entity @s weapon.mainhand {SEL("n")} run return 0
scoreboard players set #pas m.tmp 9
function {NS}:n/clignement_cherche
""")
w(F + "n/clignement_cherche.mcfunction", "\n".join(
    [f"execute if score #pas m.tmp matches {d} positioned ^ ^ ^{d} if block ~ ~ ~ #{NS}:vide if block ~ ~1 ~ #{NS}:vide unless block ~ ~ ~ minecraft:lava run return run function {NS}:n/clignement_go"
     for d in range(8, 1, -1)] + ["scoreboard players remove #pas m.tmp 1",
     f"execute if score #pas m.tmp matches 2.. run function {NS}:n/clignement_cherche"]))
w(F + "n/clignement_go.mcfunction", """
particle minecraft:reverse_portal ~ ~1 ~ 0.3 0.6 0.3 0.1 30
tp @s ~ ~ ~
playsound minecraft:entity.enderman.teleport master @a ~ ~ ~ 1 1.4
scoreboard players set @s m.blcd 60
""")
w(F + "n/foudre.mcfunction", f"""
execute if score @s m.fdcd matches 1.. run return 0
execute unless score @s s.hit matches 1.. run return 0
execute positioned ^ ^ ^2 as @e[type=#{NS}:hostiles,distance=..4,sort=nearest,limit=1] at @s run function {NS}:n/foudre_frappe
""")
w(F + "n/foudre_frappe.mcfunction", """
damage @s 8 minecraft:lightning_bolt by @p
particle minecraft:electric_spark ~ ~1 ~ 0.3 1 0.3 0.4 60
particle minecraft:flash ~ ~1 ~ 0 0 0 0 1
playsound minecraft:entity.lightning_bolt.thunder master @a ~ ~ ~ 0.5 1.6
scoreboard players set @p m.fdcd 60
""")
SUR_ENCH = ["sharpness", "smite", "bane_of_arthropods", "efficiency", "fortune", "looting", "protection", "fire_protection",
            "blast_protection", "projectile_protection", "power", "punch", "unbreaking", "feather_falling", "respiration",
            "depth_strider", "luck_of_the_sea", "lure", "loyalty", "impaling", "riptide", "piercing", "quick_charge",
            "density", "breach", "wind_burst", "sweeping_edge", "fire_aspect", "knockback", "thorns", "swift_sneak", "soul_speed", "frost_walker"]
SU = [f"execute unless entity @s[tag=metiers.sk.n6] run return run {tr('Il faut la compétence Surpuissance.', 'red')}",
      f"execute unless items entity @s weapon.mainhand *[minecraft:enchantments] run return run {tr('Tiens un objet enchanté en main.', 'red')}",
      f"execute unless data entity @s SelectedItem.components.\"minecraft:enchantments\" run return run {tr('Tiens un objet enchanté en main.', 'red')}",
      f"execute if data entity @s SelectedItem.components.\"minecraft:custom_data\".surpuissance run return run {tr('Cet objet a déjà reçu la Surpuissance.', 'red')}",
      f"execute if data entity @s SelectedItem.components.\"minecraft:custom_data\".metiers_outil run return run {tr('Impossible sur un objet de métier.', 'red')}",
      f"execute unless entity @s[level=30..] run return run {tr('Il faut 30 niveaux d’XP.', 'red')}",
      "xp add @s -30 levels"]
SU += [f'execute if items entity @s weapon.mainhand *[minecraft:enchantments~[{{enchantments:"minecraft:{e}"}}]] run item modify entity @s weapon.mainhand {{function:"minecraft:set_enchantments",type:"minecraft:set_enchantments",enchantments:{{"minecraft:{e}":1}},add:true}}'
       for e in SUR_ENCH]
SU += ['item modify entity @s weapon.mainhand {function:"minecraft:set_custom_data",type:"minecraft:set_custom_data",tag:{surpuissance:1b}}',
       "particle minecraft:enchant ~ ~1 ~ 0.5 1 0.5 1 200", "playsound minecraft:block.enchantment_table.use master @a ~ ~ ~ 1 0.6",
       tr("Surpuissance ! Tous les enchantements de l'objet montent d'un niveau.", "light_purple")]
w(F + "n/surpuissance.mcfunction", "\n".join(SU))

# ---------------- Explorateur : instinct (x5)
w(F + "x/instinct.mcfunction", """
execute store result score #x m.tmp run data get entity @s Pos[0]
execute store result score #y m.tmp run data get entity @s Pos[1]
execute store result score #z m.tmp run data get entity @s Pos[2]
execute store result score #mx m.tmp run data get entity @s LastDeathLocation.pos[0]
execute store result score #my m.tmp run data get entity @s LastDeathLocation.pos[1]
execute store result score #mz m.tmp run data get entity @s LastDeathLocation.pos[2]
execute if data entity @s LastDeathLocation run title @s actionbar [{"text":"Toi : ","color":"aqua"},{"score":{"name":"#x","objective":"m.tmp"},"color":"white"},{"text":" "},{"score":{"name":"#y","objective":"m.tmp"},"color":"white"},{"text":" "},{"score":{"name":"#z","objective":"m.tmp"},"color":"white"},{"text":"   Dernière mort : ","color":"red"},{"score":{"name":"#mx","objective":"m.tmp"},"color":"white"},{"text":" "},{"score":{"name":"#my","objective":"m.tmp"},"color":"white"},{"text":" "},{"score":{"name":"#mz","objective":"m.tmp"},"color":"white"}]
execute unless data entity @s LastDeathLocation run title @s actionbar [{"text":"Toi : ","color":"aqua"},{"score":{"name":"#x","objective":"m.tmp"},"color":"white"},{"text":" "},{"score":{"name":"#y","objective":"m.tmp"},"color":"white"},{"text":" "},{"score":{"name":"#z","objective":"m.tmp"},"color":"white"}]
""")

# ---------------- Marchand : colporteur (t5)
w(F + "t/colporteur.mcfunction", f"""
scoreboard players add @s m.colp 1
execute if score @s m.colp matches 4800.. unless entity @e[type=minecraft:wandering_trader,distance=..64] run function {NS}:t/colporteur_venir
""")
w(F + "t/colporteur_venir.mcfunction", f"""
scoreboard players set @s m.colp 0
summon minecraft:wandering_trader ~3 ~ ~3 {{DespawnDelay:24000}}
spreadplayers ~ ~ 2 6 false @e[type=minecraft:wandering_trader,distance=..6,limit=1,sort=nearest]
{tr("Un marchand ambulant passe près de toi.", "dark_green")}
""")

# ---------------- cristaux : Sagesse (+10 % d'XP) et Écho (5 % de chance de cristal) dans le gain
for j in JL:
    _p = os.path.join(ROOT, F, f"{j}/gain.mcfunction")
    _t = open(_p, encoding="utf-8").read()
    _t = _t.replace(f"execute if score #job m.heure matches {jobs[j]['idx']} run scoreboard players operation @s m.gain *= #2 m.const\n",
                    f"execute if score #job m.heure matches {jobs[j]['idx']} run scoreboard players operation @s m.gain *= #2 m.const\n"
                    f"execute if score @s m.csag_{j} matches 1 run function {NS}:refonte/sagesse\n"
                    f"execute if score @s m.ceco_{j} matches 1 store result score #r m.tmp run random value 1..100\n"
                    f"execute if score @s m.ceco_{j} matches 1 if score #r m.tmp matches ..5 run scoreboard players add @s m.cr_{j} 1\n", 1)
    open(_p, "w", encoding="utf-8").write(_t)
w(F + "refonte/sagesse.mcfunction", "scoreboard players operation #s m.tmp = @s m.gain\nscoreboard players operation #s m.tmp /= #10 m.const\nexecute if score #s m.tmp matches 0 run scoreboard players set #s m.tmp 1\nscoreboard players operation @s m.gain += #s m.tmp")

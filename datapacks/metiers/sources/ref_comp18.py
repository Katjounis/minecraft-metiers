# -*- coding: utf-8 -*-
# 26.0 (26/11/2026) : effets des 108 compétences de branche (comp18.py). Exécuté après ref_skills.py.
# Rythmes : comp/joueur toutes les 0,5 s (appelé par bonus, positionné sur le joueur), comp/tick à chaque tick,
# crochets « au gain » dans comp18.py (relevé des statistiques). Les sélecteurs tag=metiers.sk.XN reçoivent
# automatiquement « et pas désactivée » à la fin du build.
C = F + "comp/"
SK = lambda j, k: f"tag=metiers.sk.{j}{k}"
HACHE = "weapon.mainhand #minecraft:axes"
HOUE = "weapon.mainhand #minecraft:hoes"
PIOCHE = "weapon.mainhand #minecraft:pickaxes"
MAXE = {"protection": 4, "fire_protection": 4, "blast_protection": 4, "projectile_protection": 4, "feather_falling": 4,
        "respiration": 3, "aqua_affinity": 1, "thorns": 3, "depth_strider": 3, "frost_walker": 2, "soul_speed": 3, "swift_sneak": 3,
        "sharpness": 5, "smite": 5, "bane_of_arthropods": 5, "knockback": 2, "fire_aspect": 2, "looting": 3, "sweeping_edge": 3,
        "efficiency": 5, "silk_touch": 1, "unbreaking": 3, "fortune": 3, "power": 5, "punch": 2, "flame": 1, "infinity": 1,
        "luck_of_the_sea": 3, "lure": 3, "loyalty": 3, "impaling": 5, "riptide": 3, "channeling": 1, "multishot": 1,
        "quick_charge": 3, "piercing": 4, "density": 5, "breach": 4, "wind_burst": 3, "mending": 1}

# ---------------------------------------------------------------- objectifs, prédicats, types de dégâts
add_lines(F + "refonte/load.mcfunction", [f"scoreboard objectives add {o} dummy" for o in (
    "m.rage", "m.ragt", "m.tbcd", "m.lavcd", "m.lvl", "m.lvrest", "m.pmpf", "m.sprt", "m.drs", "m.anv", "m.anvl", "m.saig",
    "m.arcd", "m.pluie", "m.grap", "m.mont", "m.tmb", "m.tam", "m.ttx", "m.tbq", "m.tcb", "m.ocd")] + [
    f"scoreboard objectives add {o} {c}" for o, c in {
        "s.apple": "minecraft.used:minecraft.apple", "s.bone": "minecraft.used:minecraft.bone_meal",
        "s.shear": "minecraft.used:minecraft.shears", "s.anvil": "minecraft.custom:minecraft.interact_with_anvil",
        "s.rod": "minecraft.used:minecraft.fishing_rod", "s.kl2": "minecraft.custom:minecraft.mob_kills",
        "s.cake": "minecraft.custom:minecraft.eat_cake_slice", "m.mortn": "deathCount",
        "s.st1": "minecraft.used:minecraft.mushroom_stew", "s.st2": "minecraft.used:minecraft.rabbit_stew",
        "s.st3": "minecraft.used:minecraft.beetroot_soup", "s.st4": "minecraft.used:minecraft.suspicious_stew",
        "s.st5": "minecraft.used:minecraft.pumpkin_pie"}.items()])
P_ = f"data/{NS}/predicate/"
wj(P_ + "au_sol.json", {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"flags": {"is_on_ground": True}}})
wj(P_ + "court.json", {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"flags": {"is_sprinting": True}}})
wj(P_ + "plane.json", {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"flags": {"is_flying": True}}})
wj(P_ + "avance.json", {"type": "minecraft:entity_properties", "entity": "this",
                        "predicate": {"type_specific/player": {"input": {"forward": True}}}})
wj(P_ + "monte.json", {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"vehicle": {}}})
wj(P_ + "pluie.json", {"type": "minecraft:weather_check", "raining": True})
wj(P_ + "sombre.json", {"type": "minecraft:location_check", "predicate": {"light": {"light": {"max": 3}}}})
wj(P_ + "absorption.json", {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"effects": {"minecraft:absorption": {}}}})
for dt, msg in (("critique", "player"), ("saignement", "generic")):
    wj(f"data/{NS}/damage_type/{dt}.json", {"message_id": msg, "exhaustion": 0.0, "scaling": "never"})
wj("data/minecraft/tags/damage_type/bypasses_invulnerability.json", {"replace": False, "values": [f"{NS}:critique", f"{NS}:saignement"]})
wj("data/minecraft/tags/damage_type/bypasses_armor.json", {"replace": False, "values": [f"{NS}:saignement"]})
wj("data/minecraft/tags/damage_type/no_knockback.json", {"replace": False, "values": [f"{NS}:critique", f"{NS}:saignement"]})
wj(f"data/{NS}/tags/item/roche.json", {"values": [f"minecraft:{b}" for b in (
    "cobblestone", "cobbled_deepslate", "stone", "deepslate", "tuff", "granite", "diorite", "andesite", "netherrack", "dirt",
    "calcite", "blackstone", "basalt", "smooth_basalt")]})
wj(f"data/{NS}/tags/item/viande_crue.json", {"values": [f"minecraft:{b}" for b in ("beef", "porkchop", "mutton", "chicken", "rabbit")]})
wj(f"data/{NS}/tags/entity_type/montures.json", {"values": [f"minecraft:{a}" for a in (
    "horse", "donkey", "mule", "camel", "llama", "skeleton_horse", "zombie_horse", "strider")]})
wj(f"data/{NS}/tags/entity_type/geants.json", {"values": [f"minecraft:{a}" for a in ("wither", "ender_dragon", "warden", "elder_guardian")]})
wj(f"data/{NS}/tags/entity_type/apprivoisables.json", {"values": [f"minecraft:{a}" for a in (
    "wolf", "cat", "parrot", "horse", "donkey", "mule", "llama", "camel")]})
wj(f"data/{NS}/tags/entity_type/neutres.json", {"values": [f"minecraft:{a}" for a in ("wolf", "polar_bear", "bee", "panda", "llama", "trader_llama")]})
wj(f"data/{NS}/loot_table/legendaire.json", {"pools": [{"rolls": 1, "entries": [
    {"type": "minecraft:item", "name": "minecraft:totem_of_undying", "weight": 3},
    {"type": "minecraft:item", "name": "minecraft:enchanted_golden_apple", "weight": 2},
    {"type": "minecraft:item", "name": "minecraft:netherite_upgrade_smithing_template", "weight": 2}]}]})

# ---------------------------------------------------------------- attributs (retirés puis remis toutes les 0,5 s)
ATT = [  # (modificateur, attribut, valeur, opération, condition supplémentaire)
    ("b7", "block_break_speed", 0.5, "add_multiplied_base", f"if items entity @s {HACHE}"),
    ("b13a", "attack_damage", 2, "add_value", f"if items entity @s {HACHE}"),
    ("b13b", "attack_speed", 0.3, "add_value", f"if items entity @s {HACHE}"),
    ("b14a", "entity_interaction_range", 1, "add_value", f"if items entity @s {HACHE}"),
    ("b14b", "block_interaction_range", 1, "add_value", f"if items entity @s {HACHE}"),
    ("b15", "armor", 2, "add_value", f"if items entity @s {HACHE}"),
    ("b18", "max_health", 8, "add_value", ""),
    ("f13a", "attack_damage", 3, "add_value", f"if items entity @s {HOUE}"),
    ("f13b", "sweeping_damage_ratio", 0.5, "add_value", f"if items entity @s {HOUE}"),
    ("m14", "explosion_knockback_resistance", 1, "add_value", ""),
    ("m18a", "armor", 4, "add_value", ""), ("m18b", "armor_toughness", 2, "add_value", ""),
    ("m18c", "knockback_resistance", 0.5, "add_value", ""),
    ("p13", "oxygen_bonus", 3, "add_value", ""),
    ("p14", "water_movement_efficiency", 0.5, "add_value", ""),
    ("p15", "submerged_mining_speed", 0.8, "add_value", ""),
    ("p16", "attack_damage", 3, "add_value", "if block ~ ~0.5 ~ minecraft:water"),
    ("x8a", "jump_strength", 0.1, "add_value", ""), ("x8b", "safe_fall_distance", 2, "add_value", "")]
ATT += [(f"c11r{n}", "attack_damage", 1, "add_value", f"if score @s m.rage matches {n}..") for n in range(1, 6)]
J_ = []
for mid, att, val, op, cond in ATT:
    import re as _rx
    jk = _rx.match(r"([a-z])(\d+)", mid).group(0)
    # on n'enlève jamais pour remettre aussitôt (la vie max retomberait à chaque passage) : ajout si droit, retrait sinon
    J_.append(f"execute unless entity @s[{SK(jk[0], jk[1:])}] run attribute @s minecraft:{att} modifier remove {NS}:k_{mid}")
    if cond:
        J_.append(f"execute if entity @s[{SK(jk[0], jk[1:])}] {'unless' + cond[2:]} run attribute @s minecraft:{att} modifier remove {NS}:k_{mid}")
    J_.append(f"execute if entity @s[{SK(jk[0], jk[1:])}] {cond} run attribute @s minecraft:{att} modifier add {NS}:k_{mid} {val} {op}".replace("  ", " "))

# ---------------------------------------------------------------- effets toutes les 0,5 s
J_ += [
    # Bûcheron
    f"execute if entity @s[{SK('b', 8)}] if items entity @s {HACHE} as @e[type=minecraft:item,distance=2..12] if items entity @s contents #{NS}:bois_ramasse run tp @s @p",
    f"execute if entity @s[{SK('b', 10)}] if score @s s.apple matches 1.. run function {NS}:comp/b_seve",
    "scoreboard players set @s s.apple 0",
    f"execute if entity @s[{SK('b', 17)}] if items entity @s {HACHE} run effect give @s minecraft:regeneration 2 0 true",
    "execute if score @s m.tbcd matches 1.. run scoreboard players remove @s m.tbcd 1",
    # Fermier
    f"execute if entity @s[{SK('f', 8)}] if score @s s.bone matches 1.. run function {NS}:comp/f_os",
    "scoreboard players set @s s.bone 0",
    f"execute if entity @s[{SK('f', 9)}] if score #quatre m.timer matches 0 run fill ~-6 ~-2 ~-6 ~6 ~1 ~6 minecraft:farmland[moisture=7] replace minecraft:farmland",
    f"execute if entity @s[{SK('f', 12)}] if predicate {NS}:pluie run function {NS}:comp/f_pluie",
    f"execute if entity @s[{SK('f', 16)}] if block ~ ~-0.2 ~ minecraft:farmland run effect give @s minecraft:regeneration 2 0 true",
    f"execute if entity @s[{SK('f', 16)}] if block ~ ~ ~ #minecraft:crops run effect give @s minecraft:regeneration 2 0 true",
    # Mineur
    "execute if score @s m.arcd matches 1.. run scoreboard players remove @s m.arcd 1",
    f"execute if entity @s[{SK('m', 13)}] unless score @s m.arcd matches 1.. if predicate {NS}:sombre if block ~ ~ ~ minecraft:air unless block ~ ~-1 ~ #{NS}:vide if items entity @s container.* minecraft:torch run function {NS}:comp/m_torche",
    f"execute if entity @s[{SK('m', 14)}] if entity @e[type=minecraft:creeper,distance=..5] run effect give @s minecraft:resistance 2 1 true",
    f"execute if entity @s[{SK('m', 14)}] if entity @e[type=minecraft:tnt,distance=..5] run effect give @s minecraft:resistance 2 1 true",
    "execute if score @s m.lavcd matches 1.. run scoreboard players remove @s m.lavcd 1",
    f"execute if entity @s[{SK('m', 17)}] unless score @s m.lavcd matches 1.. if block ~ ~ ~ minecraft:lava run function {NS}:comp/m_lave",
    f"execute if entity @s[{SK('m', 17)}] unless score @s m.lavcd matches 1.. if block ~ ~0.5 ~ minecraft:lava run function {NS}:comp/m_lave",
    # Chasseur
    f"execute if score @s s.kl2 matches 1.. if entity @s[{SK('c', 11)}] run function {NS}:comp/c_rage",
    "scoreboard players set @s s.kl2 0",
    "execute if score @s m.ragt matches 1.. run scoreboard players remove @s m.ragt 1",
    "execute if score @s m.ragt matches 0 run scoreboard players set @s m.rage 0",
    # Pêcheur
    f"execute if entity @s[{SK('p', 17)}] if entity @e[type=#{NS}:marins,distance=..16] run effect give @s minecraft:resistance 2 1 true",
    f"execute if entity @s[{SK('p', 18)}] if predicate {NS}:pluie run effect give @s minecraft:strength 2 0 true",
    f"execute if entity @s[{SK('p', 18)}] if predicate {NS}:pluie run effect give @s minecraft:speed 2 0 true",
    # Éleveur
    f"execute if entity @s[{SK('e', 7)}] if score @s s.shear matches 1.. as @e[type=minecraft:sheep,distance=..4] run function {NS}:comp/e_tondre",
    "scoreboard players set @s s.shear 0",
    f"execute if entity @s[{SK('e', 8)}] run function {NS}:comp/e_dresser",
    f"execute if entity @s[{SK('e', 12)}] as @e[type=#{NS}:neutres,distance=..16] run function {NS}:comp/e_calmer",
    f"execute if entity @s[{SK('e', 14)}] as @e[type=minecraft:item,distance=..8] if items entity @s contents #{NS}:viande_crue run function {NS}:comp/e_cuire",
    f"execute if entity @s[{SK('e', 18)}] if score #quatre m.timer matches 0 run effect give @e[type=#{NS}:animaux,distance=..16] minecraft:resistance 3 3 true",
    f"execute if entity @s[{SK('e', 18)}] if score #quatre m.timer matches 0 run effect give @e[type=#{NS}:animaux,distance=..16] minecraft:regeneration 3 0 true",
    f"execute on vehicle if entity @s[type=#{NS}:montures] run function {NS}:comp/e_monture",
    # Enchanteur
    f"execute if entity @s[{SK('n', 10)}] run function {NS}:comp/n_reserve",
    f"execute if entity @s[{SK('n', 13)}] as @e[type=minecraft:experience_orb,distance=..4,tag=!{NS}.xo] run function {NS}:comp/n_orbe {{p:15}}",
    f"execute if entity @s[{SK('n', 16)}] as @e[type=minecraft:experience_orb,distance=..4,tag=!{NS}.xo] run function {NS}:comp/n_orbe {{p:35}}",
    f"execute if entity @s[{SK('n', 15)}] if score @s s.anvil matches 1.. run function {NS}:comp/n_enclume_ouvre",
    "scoreboard players set @s s.anvil 0",
    f"execute if entity @s[{SK('n', 15)}] if score @s m.anv matches 1.. run function {NS}:comp/n_enclume",
    f"execute store result score #h m.tmp run data get entity @s Health",
    f"execute if score #h m.tmp matches 1.. store result score @s m.lvl run experience query @s levels",
    f"execute if score #h m.tmp matches 1.. if score @s m.lvrest matches 1.. run function {NS}:comp/n_rendre",
    # Explorateur
    f"execute if entity @s[{SK('x', 7)}] if predicate {NS}:court run effect give @s minecraft:saturation 1 0 true",
    f"execute if entity @s[{SK('x', 11)}] if predicate {NS}:plane run function {NS}:comp/x_propulseur",
    f"execute if entity @s[{SK('x', 12)}] if predicate {NS}:court run scoreboard players add @s m.sprt 1",
    f"execute unless predicate {NS}:court run scoreboard players set @s m.sprt 0",
    f"execute if entity @s[{SK('x', 12)}] if score @s m.sprt matches 10.. run effect give @s minecraft:speed 2 2 true",
    f"execute if entity @s[{SK('x', 14)}] run effect clear @s minecraft:blindness",
    f"execute if entity @s[{SK('x', 14)}] run effect clear @s minecraft:darkness",
    f"execute if entity @s[{SK('x', 13)}] run function {NS}:comp/x_coffre_vise",
    f"execute unless entity @s[{SK('x', 13)}] if entity @s[{SK('x', 16)}] run function {NS}:comp/x_coffre_vise",
    f"execute unless entity @s[{SK('x', 13)}] unless entity @s[{SK('x', 16)}] if entity @s[{SK('x', 18)}] run function {NS}:comp/x_coffre_vise",
    # Marchand (Commerce lit m.tmb, m.tam, m.ttx, m.tbq, m.tcb)
    f"execute if entity @s[{SK('t', 7)}] if score #quatre m.timer matches 0 as @e[type=minecraft:villager,distance=..16] run function {NS}:comp/t_oubli",
    f"execute if entity @s[{SK('t', 8)}] if score #quatre m.timer matches 0 as @e[type=minecraft:villager,distance=..8] run data modify entity @s Offers.Recipes[].uses set value 0",
    f"execute if entity @s[{SK('t', 9)}] if score #quatre m.timer matches 0 as @e[type=minecraft:villager,distance=..8] run data modify entity @s Offers.Recipes[].demand set value 0",
    f"execute if entity @s[{SK('t', 11)}] if score #huit m.timer matches 0 as @e[type=minecraft:villager,distance=..8] run function {NS}:comp/t_livres",
    "scoreboard players set @s m.tmb 0",
    f"execute if entity @s[{SK('t', 13)}] run scoreboard players set @s m.tmb 30",
    f"execute if entity @s[{SK('t', 16)}] run scoreboard players set @s m.tmb 60",
    f"execute if entity @s[{SK('t', 18)}] run scoreboard players set @s m.tmb 100",
    "scoreboard players set @s m.tam 0", f"execute if entity @s[{SK('t', 14)}] run scoreboard players set @s m.tam 1",
    "scoreboard players set @s m.ttx 0", f"execute if entity @s[{SK('t', 15)}] run scoreboard players set @s m.ttx 1",
    "scoreboard players set @s m.tbq 0", f"execute if entity @s[{SK('t', 17)}] run scoreboard players set @s m.tbq 1",
    "scoreboard players set @s m.tcb 0", f"execute if entity @s[{SK('t', 12)}] run scoreboard players set @s m.tcb 1"]
w(C + "joueur.mcfunction", "\n".join(J_))
add_lines(F + "bonus.mcfunction", [f"function {NS}:comp/joueur"])
wj(f"data/{NS}/tags/entity_type/marins.json", {"values": [f"minecraft:{a}" for a in ("guardian", "elder_guardian", "drowned")]})
wj(f"data/{NS}/tags/item/bois_ramasse.json", {"values": ["#minecraft:logs", "#minecraft:saplings", "minecraft:apple", "minecraft:stick",
                                                        "minecraft:mangrove_propagule"]})

# ---------------------------------------------------------------- fonctions des effets
w(C + "b_seve.mcfunction", "effect give @s minecraft:instant_health 1 0 true\neffect give @s minecraft:absorption 60 0 true\nparticle minecraft:heart ~ ~1.5 ~ 0.3 0.3 0.3 0 3")
w(C + "m_gemme.mcfunction", "\n".join([
    "execute store result score #r m.tmp run random value 1..3",
    "execute if score #r m.tmp matches 1 run give @s minecraft:emerald 1",
    "execute if score #r m.tmp matches 2 run give @s minecraft:lapis_lazuli 3",
    "execute if score #r m.tmp matches 3 run give @s minecraft:quartz 2",
    'title @s actionbar {"text":"Gemme trouvée dans la roche !","color":"green"}']))
w(C + "m_torche.mcfunction", "setblock ~ ~ ~ minecraft:torch\nclear @s minecraft:torch 1\nscoreboard players set @s m.arcd 4")
w(C + "m_lave.mcfunction", "effect give @s minecraft:fire_resistance 15 0 true\nscoreboard players set @s m.lavcd 240\n"
  'title @s actionbar {"text":"Lave apprivoisée : 15 s de résistance au feu","color":"gold"}')
w(C + "p_miracle.mcfunction", "scoreboard players add @s m.cr_p 5\nplaysound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1.6\n"
  + tr("Pêche miraculeuse : 5 cristaux de Pêcheur !", "aqua"))
w(C + "c_rage.mcfunction", "scoreboard players operation @s m.rage += @s s.kl2\nexecute if score @s m.rage matches 6.. run scoreboard players set @s m.rage 5\n"
  "scoreboard players set @s m.ragt 10")
# Fermier : poudre d'os qui fait mûrir d'un coup (rayon vers le bloc visé)
CR_MAX = [("wheat", 7), ("carrots", 7), ("potatoes", 7), ("beetroots", 3), ("torchflower_crop", 2), ("pitcher_crop", 4), ("sweet_berry_bush", 3)]
w(C + "f_os.mcfunction", f"scoreboard players set #pas m.tmp 0\nexecute anchored eyes positioned ^ ^ ^0.2 run function {NS}:comp/f_os_rayon")
w(C + "f_os_rayon.mcfunction", "\n".join(
    ["scoreboard players add #pas m.tmp 1"] +
    [f"execute if block ~ ~ ~ minecraft:{c} run return run setblock ~ ~ ~ minecraft:{c}[age={a}]" for c, a in CR_MAX] +
    [f"execute if score #pas m.tmp matches ..50 unless block ~ ~ ~ #{NS}:vide run return 0",
     f"execute if score #pas m.tmp matches ..50 positioned ^ ^ ^0.1 run function {NS}:comp/f_os_rayon"]))
PL = ["scoreboard players add @s m.pluie 1", "execute if score @s m.pluie matches ..119 run return 0", "scoreboard players set @s m.pluie 0"]
for c, mx in (("wheat", 7), ("carrots", 7), ("potatoes", 7), ("beetroots", 3), ("nether_wart", 3)):
    for a in range(mx - 1, -1, -1):
        PL.append(f"fill ~-16 ~-2 ~-16 ~16 ~2 ~16 minecraft:{c}[age={a + 1}] replace minecraft:{c}[age={a}]")
PL.append("particle minecraft:falling_water ~ ~2 ~ 8 1 8 0 80")
w(C + "f_pluie.mcfunction", "\n".join(PL))
w(C + "f_repas.mcfunction", "\n".join(
    ["scoreboard players set #r m.tmp 0"] + [f"scoreboard players operation #r m.tmp += @s s.st{i}" for i in range(1, 6)] +
    ["scoreboard players operation #r m.tmp += @s s.cake"] + [f"scoreboard players set @s s.st{i} 0" for i in range(1, 6)] +
    ["scoreboard players set @s s.cake 0", "execute if score #r m.tmp matches 1.. run effect give @s minecraft:strength 120 0",
     "execute if score #r m.tmp matches 1.. run effect give @s minecraft:speed 120 0"]))
# Éleveur
COUL = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray", "cyan", "purple", "blue",
        "brown", "green", "red", "black"]
w(C + "e_tondre.mcfunction", "\n".join(
    ["execute if data entity @s {Sheared:1b} run return 0", "execute store result score #a m.tmp run data get entity @s Age",
     "execute if score #a m.tmp matches ..-1 run return 0"] +
    [f"execute if data entity @s {{Color:{i}b}} run summon minecraft:item ~ ~0.5 ~ {{Item:{{id:\"minecraft:{c}_wool\",count:2}}}}" for i, c in enumerate(COUL)] +
    ["data modify entity @s Sheared set value 1b", "playsound minecraft:entity.sheep.shear neutral @a ~ ~ ~ 0.6 1"]))
w(C + "e_cuire.mcfunction", "\n".join(
    [f'execute if items entity @s contents minecraft:{c} run data modify entity @s Item.id set value "minecraft:cooked_{c}"' for c in ("beef", "porkchop", "mutton", "chicken", "rabbit")]
    + ["particle minecraft:flame ~ ~0.2 ~ 0.1 0.1 0.1 0 3"]))
w(C + "e_calmer.mcfunction", "data modify entity @s AngerTime set value 0\ndata remove entity @s AngryAt\n"
  "data modify entity @s anger_end_time set value -1L\ndata remove entity @s angry_at")
w(C + "e_monture.mcfunction", "scoreboard players operation @s m.mont = @p m.id")
w(C + "e_ecurie.mcfunction", "\n".join([
    f"execute as @e[type=#{NS}:montures,distance=..10,tag=!{NS}.poulain] store result score @s m.tmp run data get entity @s Age",
    f"execute as @e[type=#{NS}:montures,distance=..10,tag=!{NS}.poulain] if score @s m.tmp matches ..-23500 run function {NS}:comp/e_poulain"]))
w(C + "e_poulain.mcfunction", "\n".join([
    f"tag @s add {NS}.poulain", "attribute @s minecraft:max_health base set 30", "attribute @s minecraft:movement_speed base set 0.3375",
    "attribute @s minecraft:jump_strength base set 1.0", "particle minecraft:happy_villager ~ ~1 ~ 0.4 0.4 0.4 0 12"]))
# Dresseur : accroupi 3 s près d'un apprivoisable sauvage, sa nourriture en main
NOURR = "*[minecraft:item_model]"
w(C + "e_dresser.mcfunction", "\n".join([
    f"execute unless predicate {NS}:accroupi run return run scoreboard players set @s m.drs 0",
    f"execute unless entity @e[type=#{NS}:apprivoisables,distance=..3,predicate=!{NS}:a_maitre] run return run scoreboard players set @s m.drs 0",
    "scoreboard players add @s m.drs 1",
    "particle minecraft:heart ~ ~1.8 ~ 0.3 0.1 0.3 0 1",
    f"execute if score @s m.drs matches 6.. as @e[type=#{NS}:apprivoisables,distance=..3,predicate=!{NS}:a_maitre,sort=nearest,limit=1] run function {NS}:comp/e_apprivoiser",
    "execute if score @s m.drs matches 6.. run scoreboard players set @s m.drs 0"]))
wj(P_ + "a_maitre.json", {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"nbt": "{Owner:[I;]}"}})
w(C + "e_apprivoiser.mcfunction", "\n".join([
    "data modify entity @s Owner set from entity @p UUID", "data modify entity @s Tame set value 1b",
    "particle minecraft:heart ~ ~1 ~ 0.4 0.4 0.4 0 10", "playsound minecraft:entity.player.levelup neutral @a ~ ~ ~ 0.6 1.6",
    'title @p actionbar {"text":"Dresseur : il est à toi !","color":"light_purple"}']))
# Enchanteur
w(C + "n_reserve.mcfunction", "\n".join([
    "execute store result score #l m.tmp run experience query @s levels",
    f"execute if score #l m.tmp matches 30.. unless predicate {NS}:absorption run effect give @s minecraft:absorption infinite 0 true",
    "execute if score #l m.tmp matches 50.. run effect give @s minecraft:absorption infinite 1 true",
    "execute if score #l m.tmp matches ..29 run effect clear @s minecraft:absorption"]))
w(C + "n_orbe.mcfunction", "\n".join([
    f"tag @s add {NS}.xo", "execute store result score #r m.tmp run random value 1..100",
    "$execute if score #r m.tmp matches ..$(p) store result entity @s Value short 2 run data get entity @s Value"]))
w(C + "n_enclume_ouvre.mcfunction", "scoreboard players set @s m.anv 120\nexecute store result score @s m.anvl run experience query @s levels")
w(C + "n_enclume.mcfunction", "\n".join([
    "scoreboard players remove @s m.anv 1", "execute store result score #l m.tmp run experience query @s levels",
    "execute if score #l m.tmp >= @s m.anvl run return run scoreboard players operation @s m.anvl = #l m.tmp",
    "scoreboard players operation #d m.tmp = @s m.anvl", "scoreboard players operation #d m.tmp -= #l m.tmp",
    "scoreboard players operation #d m.tmp /= #2 m.const",
    f"execute store result storage {NS}:t n int 1 run scoreboard players get #d m.tmp",
    f"execute if score #d m.tmp matches 1.. run function {NS}:comp/n_xp with storage {NS}:t",
    "execute store result score @s m.anvl run experience query @s levels"]))
w(C + "n_xp.mcfunction", "$xp add @s $(n) levels\n$title @s actionbar {\"text\":\"Enclume douce : $(n) niveaux rendus\",\"color\":\"dark_purple\"}")
add_lines(F + "n/enchant.mcfunction", [
    f"execute if entity @s[{SK('n', 7)}] if score #lv m.tmp matches 1.. store result score #r m.tmp run random value 1..2",
    f"execute if entity @s[{SK('n', 7)}] if score #lv m.tmp matches 1.. if score #r m.tmp matches 1 run function {NS}:comp/n_lapis"])
w(C + "n_lapis.mcfunction", f"execute store result storage {NS}:t n int 1 run scoreboard players get #lv m.tmp\nfunction {NS}:comp/n_lapis_m with storage {NS}:t")
w(C + "n_lapis_m.mcfunction", "$give @s minecraft:lapis_lazuli $(n)")
# Garde-niveaux et Sac étanche : à la mort
add_lines(F + "refonte/tick.mcfunction", [f"execute as @a[scores={{m.mortn=1..}}] at @s run function {NS}:comp/mort"])
w(C + "mort.mcfunction", "\n".join([
    "scoreboard players set @s m.mortn 0",
    f"execute if entity @s[{SK('n', 18)}] run scoreboard players operation @s m.lvrest = @s m.lvl",
    f"execute if entity @s[{SK('n', 18)}] run scoreboard players operation @s m.lvrest /= #2 m.const",
    f"execute if entity @s[{SK('x', 17)}] as @e[type=minecraft:item,distance=..8] run data merge entity @s {{Age:-12000s,Invulnerable:1b}}"]))
w(C + "n_rendre.mcfunction", "\n".join([
    f"execute store result storage {NS}:t n int 1 run scoreboard players get @s m.lvrest", "scoreboard players set @s m.lvrest 0",
    f"function {NS}:comp/n_xp with storage {NS}:t"]))
# Explorateur
w(C + "x_propulseur.mcfunction", "\n".join([
    "scoreboard players add @s m.pmpf 1", "execute if score @s m.pmpf matches ..29 run return 0", "scoreboard players set @s m.pmpf 0",
    "execute store result score #n m.tmp run clear @s minecraft:firework_rocket 0",
    "execute if score #n m.tmp matches ..2 run give @s minecraft:firework_rocket[minecraft:fireworks={flight_duration:2b}] 1"]))
# coffres de structure : on regarde le coffre visé ; s'il n'a jamais été ouvert (LootTable), on ajoute un butin
w(C + "x_coffre_vise.mcfunction", f"scoreboard players set #pas m.tmp 0\nexecute anchored eyes positioned ^ ^ ^0.2 run function {NS}:comp/x_coffre_rayon")
w(C + "x_coffre_rayon.mcfunction", "\n".join([
    "scoreboard players add #pas m.tmp 1",
    f"execute if data block ~ ~ ~ LootTable align xyz positioned ~0.5 ~0.5 ~0.5 unless entity @e[type=minecraft:marker,tag={NS}.pille,distance=..0.3] run return run function {NS}:comp/x_coffre",
    f"execute if score #pas m.tmp matches ..45 if block ~ ~ ~ #{NS}:vide positioned ^ ^ ^0.1 run function {NS}:comp/x_coffre_rayon"]))
w(C + "x_coffre.mcfunction", "\n".join([
    f'summon minecraft:marker ~ ~ ~ {{Tags:["{NS}.pille"]}}',
    f"data modify storage {NS}:t lt set from block ~ ~ ~ LootTable",
    "execute store result score #r m.tmp run random value 1..100",
    f"execute if entity @p[{SK('x', 13)}] if score #r m.tmp matches ..30 run function {NS}:comp/x_second with storage {NS}:t",
    "execute store result score #r m.tmp run random value 1..100",
    f"execute if entity @p[{SK('x', 16)}] if score #r m.tmp matches ..25 run loot insert ~ ~ ~ loot minecraft:chests/shipwreck_map",
    "execute store result score #r m.tmp run random value 1..100",
    f"execute if entity @p[{SK('x', 18)}] if score #r m.tmp matches ..5 run loot insert ~ ~ ~ loot {NS}:legendaire"]))
w(C + "x_second.mcfunction", "$loot insert ~ ~ ~ loot $(lt)")
# Marchand
w(C + "t_oubli.mcfunction", 'data remove entity @s Gossips[{Type:"minor_negative"}]\ndata remove entity @s Gossips[{Type:"major_negative"}]')
w(C + "t_guerir.mcfunction", "execute store result score #c m.tmp run data get entity @s ConversionTime\n"
  "execute if score #c m.tmp matches 2.. run data modify entity @s ConversionTime set value 1")
TL = ['execute unless data entity @s VillagerData{profession:"minecraft:librarian"} run return 0']
for e, mx in MAXE.items():
    for lv in range(1, mx):
        TL.append(f'data modify entity @s Offers.Recipes[{{sell:{{components:{{"minecraft:stored_enchantments":{{"minecraft:{e}":{lv}}}}}}}}}].sell.components."minecraft:stored_enchantments"."minecraft:{e}" set value {mx}')
w(C + "t_livres.mcfunction", "\n".join(TL))

# ---------------------------------------------------------------- frappe et coups reçus (progrès)
wj(f"data/{NS}/advancement/comp/frappe.json", {"criteria": {"h": {"trigger": "minecraft:player_hurt_entity"}}, "rewards": {"function": f"{NS}:comp/frappe"}})
wj(f"data/{NS}/advancement/comp/touche.json", {"criteria": {"h": {"trigger": "minecraft:entity_hurt_player"}}, "rewards": {"function": f"{NS}:comp/touche"}})
ARME = "weapon.mainhand #metiers:armes_cac"
wj(f"data/{NS}/tags/item/armes_cac.json", {"values": ["#minecraft:swords", "#minecraft:axes"]})
w(C + "frappe.mcfunction", "\n".join([
    f"tag @s add {NS}.frappeur",
    f"execute as @e[type=!minecraft:player,distance=..8,nbt={{HurtTime:10s}},sort=nearest,limit=1] at @s run function {NS}:comp/victime",
    f"execute if entity @s[{SK('b', 16)}] unless score @s m.tbcd matches 1.. if predicate {NS}:accroupi if items entity @s {HACHE} run function {NS}:comp/b_tourbillon",
    f"tag @s remove {NS}.frappeur",
    f"advancement revoke @s only {NS}:comp/frappe"]))
w(C + "victime.mcfunction", "\n".join([
    "scoreboard players set #crit m.tmp 0", "execute store result score #r m.tmp run random value 1..100",
    f"execute if entity @p[tag={NS}.frappeur,{SK('c', 7)}] if items entity @p[tag={NS}.frappeur] {ARME} if score #r m.tmp matches ..10 run scoreboard players set #crit m.tmp 1",
    f"execute if entity @p[tag={NS}.frappeur,{SK('c', 12)}] if items entity @p[tag={NS}.frappeur] {ARME} if score #r m.tmp matches ..20 run scoreboard players set #crit m.tmp 1",
    f"execute if score #crit m.tmp matches 1 run damage @s 5 {NS}:critique by @p[tag={NS}.frappeur]",
    "execute if score #crit m.tmp matches 1 run particle minecraft:crit ~ ~1 ~ 0.3 0.5 0.3 0.3 20",
    f"execute if entity @p[tag={NS}.frappeur,{SK('c', 8)}] run scoreboard players set @s m.saig 6",
    f"execute if score #crit m.tmp matches 1 if entity @p[tag={NS}.frappeur,{SK('c', 12)}] run scoreboard players set @s m.saig 6",
    f"execute if score #crit m.tmp matches 1 if entity @p[tag={NS}.frappeur,{SK('c', 12)}] run effect give @p[tag={NS}.frappeur] minecraft:regeneration 2 1 true",
    f"execute if entity @p[tag={NS}.frappeur,{SK('c', 18)}] if entity @s[type=#{NS}:geants] run damage @s 5 {NS}:critique by @p[tag={NS}.frappeur]",
    f"execute if entity @p[tag={NS}.frappeur,{SK('c', 18)}] if entity @s[tag={NS}.boss] run damage @s 5 {NS}:critique by @p[tag={NS}.frappeur]"]))
w(C + "b_tourbillon.mcfunction", "\n".join([
    "scoreboard players set @s m.tbcd 12",
    f"execute as @e[type=#{NS}:hostiles,distance=..3] run damage @s 6 {NS}:critique by @p[tag={NS}.frappeur]",
    "particle minecraft:sweep_attack ~ ~1 ~ 1.5 0.2 1.5 0 10", "playsound minecraft:entity.player.attack.sweep master @a ~ ~ ~ 1 0.7"]))
w(C + "touche.mcfunction", "\n".join([
    f"advancement revoke @s only {NS}:comp/touche",
    f"execute unless entity @s[{SK('c', 10)}] run return 0",
    "execute store result score #r m.tmp run random value 1..100", "execute if score #r m.tmp matches 11.. run return 0",
    "effect give @s minecraft:instant_health 1 0 true", "effect give @s minecraft:speed 2 1 true",
    "particle minecraft:cloud ~ ~1 ~ 0.3 0.5 0.3 0.05 10", 'title @s actionbar {"text":"Esquive !","color":"aqua"}']))
# saignement des créatures, toutes les 0,5 s
add_lines(F + "loop.mcfunction", [f"execute as @e[scores={{m.saig=1..}}] at @s run function {NS}:comp/saigne"])
w(C + "saigne.mcfunction", f"scoreboard players remove @s m.saig 1\ndamage @s 1 {NS}:saignement\nparticle minecraft:block{{block_state:\"minecraft:redstone_block\"}} ~ ~1 ~ 0.2 0.3 0.2 0 4")

# ---------------------------------------------------------------- chaque tick
TK = [
    # Fermier : Pied léger (la chute lente remet la distance de chute à zéro : plus de piétinement)
    f"execute as @a[{SK('f', 7)},predicate=!{NS}:au_sol] at @s if block ~ ~-0.6 ~ minecraft:farmland run effect give @s minecraft:slow_falling 1 0 true",
    f"execute as @a[{SK('f', 7)},predicate=!{NS}:au_sol] at @s if block ~ ~-1.4 ~ minecraft:farmland run effect give @s minecraft:slow_falling 1 0 true",
    # Mineur : Tri automatique
    f"execute as @a[{SK('m', 7)}] at @s if items entity @s {PIOCHE} as @e[type=minecraft:item,distance=..5] if items entity @s contents #{NS}:roche run kill @s",
    # Chasseur : flèches tirées (Œil de faucon, Flèches perçantes)
    f"execute as @e[type=#minecraft:arrows,tag=!{NS}.fv] run function {NS}:comp/fleche",
    # Explorateur : Grimpeur
    f"execute as @a[{SK('x', 10)},predicate={NS}:avance] at @s rotated ~ 0 unless block ^ ^0.5 ^0.6 #{NS}:vide unless block ^ ^0.5 ^0.6 #minecraft:replaceable run function {NS}:comp/x_grimpe",
    f"execute as @a[tag={NS}.grimpe] at @s rotated ~ 0 if block ^ ^0.5 ^0.6 #{NS}:vide run function {NS}:comp/x_lache",
    f"execute as @a[tag={NS}.grimpe,predicate=!{NS}:avance] run function {NS}:comp/x_lache",
    # Pêcheur : Canne grappin
    f"execute as @e[type=minecraft:fishing_bobber,tag=!{NS}.bvu] run function {NS}:comp/p_bouchon",
    f"execute as @a[{SK('p', 11)}] at @s run function {NS}:comp/p_grappin",
    f"execute as @a[scores={{m.grap=1..}}] at @s run function {NS}:comp/p_tire"]
w(C + "tick.mcfunction", "\n".join(TK))
add_lines(F + "refonte/tick.mcfunction", [f"function {NS}:comp/tick"])
w(C + "fleche.mcfunction", f"tag @s add {NS}.fv\ntag @s add {NS}.fvn\nexecute on origin run function {NS}:comp/fleche_tireur\ntag @s remove {NS}.fvn")
w(C + "fleche_tireur.mcfunction", "\n".join([
    f"execute if entity @s[{SK('c', 14)}] as @e[type=#minecraft:arrows,tag={NS}.fvn,limit=1] store result entity @s damage double 0.0125 run data get entity @s damage 100",
    f"execute if entity @s[{SK('c', 15)}] as @e[type=#minecraft:arrows,tag={NS}.fvn,limit=1] run data modify entity @s PierceLevel set value 1b"]))
w(C + "x_grimpe.mcfunction", f"tag @s add {NS}.grimpe\neffect give @s minecraft:levitation 1 2 true")
w(C + "x_lache.mcfunction", f"tag @s remove {NS}.grimpe\neffect clear @s minecraft:levitation\neffect give @s minecraft:slow_falling 1 0 true")
# Canne grappin : un marqueur suit le bouchon posé au sol ; quand on ramène la canne, on est tiré vers lui
w(C + "p_grappin.mcfunction", "\n".join([
    "scoreboard players operation #pid m.tmp = @s m.id",
    f"tag @e[type=minecraft:marker,tag={NS}.grap] remove {NS}.gmoi",
    f"execute as @e[type=minecraft:marker,tag={NS}.grap] if score @s m.own = #pid m.tmp run tag @s add {NS}.gmoi",
    "scoreboard players set #bob m.tmp 0",
    f"execute as @e[type=minecraft:fishing_bobber,distance=..64] if score @s m.own = #pid m.tmp run scoreboard players set #bob m.tmp 1",
    f"execute if score @s s.rod matches 1.. if score #bob m.tmp matches 0 if entity @e[type=minecraft:marker,tag={NS}.gmoi,tag={NS}.gsol,distance=4..40] run scoreboard players set @s m.grap 40",
    "scoreboard players set @s s.rod 0",
    f"execute unless score @s m.grap matches 1.. if score #bob m.tmp matches 0 run kill @e[type=minecraft:marker,tag={NS}.gmoi]",
    f"execute unless score @s m.grap matches 1.. as @e[type=minecraft:marker,tag={NS}.gmoi] run tag @s remove {NS}.gsol",
    f"execute unless score @s m.grap matches 1.. as @e[type=minecraft:fishing_bobber,distance=..64,predicate={NS}:au_sol] if score @s m.own = #pid m.tmp at @s unless block ~ ~ ~ minecraft:water run function {NS}:comp/p_marque"]))
w(C + "p_bouchon.mcfunction", f"tag @s add {NS}.bvu\nexecute on origin run scoreboard players operation #o m.tmp = @s m.id\nscoreboard players operation @s m.own = #o m.tmp")
w(C + "p_marque.mcfunction", "\n".join([
    f"execute unless entity @e[type=minecraft:marker,tag={NS}.gmoi] run summon minecraft:marker ~ ~ ~ {{Tags:[\"{NS}.grap\",\"{NS}.gmoi\"]}}",
    f"execute as @e[type=minecraft:marker,tag={NS}.gmoi] run scoreboard players operation @s m.own = #pid m.tmp",
    f"tp @e[type=minecraft:marker,tag={NS}.gmoi] ~ ~ ~", f"tag @e[type=minecraft:marker,tag={NS}.gmoi] add {NS}.gsol"]))
w(C + "p_tire.mcfunction", "\n".join([
    "scoreboard players remove @s m.grap 1", "scoreboard players operation #pid m.tmp = @s m.id",
    f"tag @e[type=minecraft:marker,tag={NS}.grap] remove {NS}.gmoi",
    f"execute as @e[type=minecraft:marker,tag={NS}.grap] if score @s m.own = #pid m.tmp run tag @s add {NS}.gmoi",
    f"execute unless entity @e[type=minecraft:marker,tag={NS}.gmoi,distance=1.5..] run return run function {NS}:comp/p_fin",
    f"execute facing entity @e[type=minecraft:marker,tag={NS}.gmoi,limit=1] feet unless block ^ ^0.3 ^0.8 #{NS}:vide run return run function {NS}:comp/p_fin",
    f"execute facing entity @e[type=minecraft:marker,tag={NS}.gmoi,limit=1] feet unless block ^ ^1.5 ^0.8 #{NS}:vide run return run function {NS}:comp/p_fin",
    f"execute facing entity @e[type=minecraft:marker,tag={NS}.gmoi,limit=1] feet run tp @s ^ ^ ^0.8",
    "particle minecraft:crit ~ ~1 ~ 0.1 0.1 0.1 0 2",
    "execute if score @s m.grap matches 0 run function metiers:comp/p_fin"]))
w(C + "p_fin.mcfunction", f"scoreboard players set @s m.grap 0\nkill @e[type=minecraft:marker,tag={NS}.gmoi]\neffect give @s minecraft:slow_falling 2 0 true\n"
  "playsound minecraft:entity.fishing_bobber.retrieve master @a ~ ~ ~ 1 0.8")

# ---------------------------------------------------------------- Enchanteur : Forge arcanique (onglet Outil)
FA = [f"execute unless entity @s[{SK('n', 9)}] run return run {tr('Il faut la compétence Forge arcanique I.', 'red')}",
      f"execute unless items entity @s weapon.mainhand *[minecraft:enchantments] run return run {tr('Tiens un objet enchanté en main.', 'red')}",
      f"execute if data entity @s SelectedItem.components.\"minecraft:custom_data\".metiers_outil run return run {tr('Impossible sur un objet de métier.', 'red')}",
      f"execute unless entity @s[level=15..] run return run {tr('Il faut 15 niveaux d’XP.', 'red')}",
      f"execute store result score #n m.tmp run clear @s minecraft:lapis_lazuli 0",
      f"execute unless score #n m.tmp matches 10.. run return run {tr('Il faut 10 lapis-lazuli.', 'red')}",
      "scoreboard players set #pal m.tmp 1", f"execute if entity @s[{SK('n', 11)}] run scoreboard players set #pal m.tmp 2",
      f"execute if entity @s[{SK('n', 12)}] run scoreboard players set #pal m.tmp 3", "scoreboard players set #monte m.tmp 0"]
for e, mx in MAXE.items():
    FA += [f'execute store result score #l m.tmp run data get entity @s SelectedItem.components."minecraft:enchantments"."minecraft:{e}"',
           f"scoreboard players set #cap m.tmp {mx}", "scoreboard players operation #cap m.tmp += #pal m.tmp",
           f'execute if score #l m.tmp matches 1.. if score #l m.tmp < #cap m.tmp run item modify entity @s weapon.mainhand {{function:"minecraft:set_enchantments",type:"minecraft:set_enchantments",enchantments:{{"minecraft:{e}":1}},add:true}}',
           f"execute if score #l m.tmp matches 1.. if score #l m.tmp < #cap m.tmp run scoreboard players add #monte m.tmp 1"]
FA += [f"execute if score #monte m.tmp matches 0 run return run {tr('Tous ses enchantements sont déjà au plafond de ta Forge arcanique.', 'gold')}",
       "xp add @s -15 levels", "clear @s minecraft:lapis_lazuli 10",
       "particle minecraft:enchant ~ ~1 ~ 0.5 1 0.5 1 200", "playsound minecraft:block.enchantment_table.use master @a ~ ~ ~ 1 0.5",
       tr("Forge arcanique : les enchantements de l'objet montent d'un niveau.", "light_purple")]
w(C + "n_forge.mcfunction", "\n".join(FA))

# ---------------------------------------------------------------- Bûcheron : Abattage étendu (plafond 150 blocs, 600 avec b9)
_p = os.path.join(ROOT, F, "b/abattage/bloc.mcfunction")
_t = open(_p, encoding="utf-8").read()
assert "execute if score #n m.tmp matches 150.. run return 0" in _t
open(_p, "w", encoding="utf-8").write(_t.replace("execute if score #n m.tmp matches 150.. run return 0",
                                                 "execute if score #n m.tmp >= #abmax m.tmp run return 0", 1))
_p = os.path.join(ROOT, F, "b/abattage/demarrer.mcfunction")
_t = open(_p, encoding="utf-8").read()
open(_p, "w", encoding="utf-8").write("scoreboard players set #abmax m.tmp 150\n"
                                      f"execute if entity @s[{SK('b', 9)}] run scoreboard players set #abmax m.tmp 600\n" + _t)

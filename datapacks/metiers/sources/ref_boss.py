# -*- coding: utf-8 -*-
# Refonte v24, partie 4 : 5 boss en rotation, PV selon les joueurs connectés, attaques, vagues à 66 % et 33 %, éclats.

BOSS = {
    1: dict(nom="Le Colosse des Métiers", col="dark_red", bar="red", etype="zombie", scale=2.5, atk=14, arm=16, spd=0.3,
            extra='equipment:{head:{id:"minecraft:netherite_helmet",count:1},chest:{id:"minecraft:netherite_chestplate",count:1},legs:{id:"minecraft:netherite_leggings",count:1},feet:{id:"minecraft:netherite_boots",count:1},mainhand:{id:"minecraft:netherite_axe",count:1}},drop_chances:{head:0f,chest:0f,legs:0f,feet:0f,mainhand:0f},CanPickUpLoot:0b',
            part="minecraft:soul_fire_flame", atks=("seisme", "bond")),
    2: dict(nom="La Reine arachnide", col="dark_green", bar="green", etype="spider", scale=3.0, atk=10, arm=10, spd=0.34,
            extra="", part="minecraft:spore_blossom_air", atks=("venin", "toile")),
    3: dict(nom="La Liche du givre", col="aqua", bar="blue", etype="stray", scale=2.2, atk=8, arm=12, spd=0.28,
            extra='equipment:{head:{id:"minecraft:wither_skeleton_skull",count:1},mainhand:{id:"minecraft:bow",count:1}},drop_chances:{head:0f,mainhand:0f},CanPickUpLoot:0b',
            part="minecraft:snowflake", atks=("drain", "blizzard", "clignement")),
    4: dict(nom="Le Brasier ancestral", col="gold", bar="yellow", etype="blaze", scale=2.5, atk=10, arm=12, spd=0.3,
            extra="", part="minecraft:flame", atks=("pluie_feu", "onde")),
    5: dict(nom="Le Creeper géant", col="white", bar="white", etype="creeper", scale=3.0, atk=1, arm=14, spd=0.28,
            extra="Fuse:32767s,ExplosionRadius:0b", part="minecraft:happy_villager", atks=("detonation", "souffle")),
}
VAGUE = {
    1: [f'summon minecraft:zombie ~{dx} ~ ~{dz} {{Tags:["metiers.sbire"],CustomName:{{text:"Sbire du Colosse",color:"red"}},equipment:{{head:{{id:"minecraft:iron_helmet",count:1}}}},drop_chances:{{head:0f}}}}' for dx, dz in ((2, 0), (-2, 0), (0, 2), (0, -2))],
    2: [f'summon minecraft:cave_spider ~{dx} ~ ~{dz} {{Tags:["metiers.sbire"],CustomName:{{text:"Couvée de la Reine",color:"green"}}}}' for dx, dz in ((2, 0), (-2, 0), (0, 2), (0, -2), (2, 2))],
    3: [f'summon minecraft:skeleton ~{dx} ~ ~{dz} {{Tags:["metiers.sbire"],CustomName:{{text:"Serviteur de la Liche",color:"aqua"}},equipment:{{head:{{id:"minecraft:iron_helmet",count:1}},mainhand:{{id:"minecraft:bow",count:1}}}},drop_chances:{{head:0f,mainhand:0f}}}}' for dx, dz in ((3, 0), (-3, 0), (0, 3))],
    4: [f'summon minecraft:magma_cube ~{dx} ~ ~{dz} {{Tags:["metiers.sbire"],Size:2,CustomName:{{text:"Braise vivante",color:"gold"}}}}' for dx, dz in ((2, 0), (-2, 0), (0, 2))],
    5: [f'summon minecraft:zombie ~{dx} ~ ~{dz} {{Tags:["metiers.sbire"],CustomName:{{text:"Rejeton du Creeper",color:"green"}},equipment:{{head:{{id:"minecraft:creeper_head",count:1}}}},drop_chances:{{head:0f}}}}' for dx, dz in ((2, 0), (-2, 0), (0, 2), (0, -2))],
}
B = "@e[tag=metiers.boss,limit=1]"
ANN = lambda txt, col="white": f'tellraw @a {PREFIX},{{"text":"{txt}","color":"{col}"}}]'

w(F + "boss/alerte.mcfunction", "\n".join([
    # 26/11/2026 : pas pendant un evenement du pack Boss (Grimoire, Corbeau) : on retente plus tard
    "execute if score #etat bs.ev matches 1.. run return run scoreboard players set #cycle m.boss 3000",
    "execute store result score #n m.boss if entity @a[gamemode=!spectator]",
    "execute if score #n m.boss matches ..0 run return run scoreboard players set #cycle m.boss 3000",
    "scoreboard players set #cycle m.boss 0", "scoreboard players set #compte m.boss 240",
    "scoreboard players add #type m.boss 1", "execute unless score #type m.boss matches 1..5 run scoreboard players set #type m.boss 1"] +
    [f'execute if score #type m.boss matches {k} run tellraw @a {PREFIX},{{"text":"{b["nom"]} se réveille ! ","color":"{b["col"]}","bold":true}},{{"text":"Il apparaît dans 2 minutes près d\'un joueur au hasard. Préparez-vous.","color":"white"}}]' for k, b in BOSS.items()] +
    ["execute as @a at @s run playsound minecraft:entity.wither.spawn master @s ~ ~ ~ 0.6 0.6"]))

AP = ["execute store result score #n m.boss if entity @a[gamemode=!spectator]",
      "scoreboard players operation #max m.boss = #n m.boss", "scoreboard players operation #max m.boss *= #200 m.const",
      "scoreboard players add #max m.boss 350",
      # le jeu plafonne les PV max à 1 024 : au-delà de 1 000, la Résistance prend le relais (4 joueurs et plus)
      "scoreboard players set #res m.boss 0",
      "execute if score #max m.boss matches 1100.. run scoreboard players set #res m.boss 1",
      "execute if score #max m.boss matches 1500.. run scoreboard players set #res m.boss 2",
      "execute if score #max m.boss matches 1001.. run scoreboard players set #max m.boss 1000",
      f"execute store result storage {NS}:boss hp int 1 run scoreboard players get #max m.boss",
      f"function {NS}:boss/lieu"]
AP += [f"execute if score #type m.boss matches {k} at @e[type=minecraft:marker,tag=metiers.blieu,limit=1] run function {NS}:boss/apparaitre_{k} with storage {NS}:boss" for k in BOSS]
AP += ["kill @e[type=minecraft:marker,tag=metiers.blieu]",
       f"execute if score #res m.boss matches 1 run effect give {B} minecraft:resistance infinite 0 true",
       f"execute if score #res m.boss matches 2 run effect give {B} minecraft:resistance infinite 1 true",
       "scoreboard players set #actif m.boss 1", "scoreboard players set #temps m.boss 0",
       "scoreboard players set #phase m.boss 0", "scoreboard players set #atk m.boss 0", "scoreboard players set #tue m.boss 0",
       "scoreboard players set #mk m.boss 0",
       "scoreboard players operation #last m.boss = #max m.boss", "scoreboard players set @a m.dmg 0", "scoreboard players set @a m.bdmg 0",
       "execute store result bossbar metiers:boss max run scoreboard players get #max m.boss",
       "execute store result bossbar metiers:boss value run scoreboard players get #max m.boss",
       "bossbar set metiers:boss style notched_10", "bossbar set metiers:boss visible true", "bossbar set metiers:boss players @a",
       f"execute store result score #x m.boss run data get entity {B} Pos[0]",
       f"execute store result score #y m.boss run data get entity {B} Pos[1]",
       f"execute store result score #z m.boss run data get entity {B} Pos[2]",
       f'tellraw @a {PREFIX},{{"text":"Le boss est apparu près de ","color":"red","bold":true}},{{"selector":"@s"}},{{"text":" en ","color":"white"}},{{"score":{{"name":"#x","objective":"m.boss"}},"color":"yellow"}},{{"text":" ","color":"white"}},{{"score":{{"name":"#y","objective":"m.boss"}},"color":"yellow"}},{{"text":" ","color":"white"}},{{"score":{{"name":"#z","objective":"m.boss"}},"color":"yellow"}},{{"text":". PV : ","color":"white"}},{{"score":{{"name":"#max","objective":"m.boss"}},"color":"red"}},{{"text":". Chaque participant gagne un éclat de boss.","color":"white"}}]',
       "execute as @a at @s run playsound minecraft:entity.ravager.roar master @s ~ ~ ~ 1 0.6"]
w(F + "boss/apparaitre.mcfunction", "\n".join(AP))
wj(f"data/{NS}/tags/block/boss_vide.json", {"values": ["minecraft:air", "minecraft:cave_air", "minecraft:void_air", "minecraft:short_grass",
   "minecraft:tall_grass", "minecraft:fern", "minecraft:large_fern", "minecraft:dead_bush", "minecraft:dandelion", "minecraft:poppy"]})
wj(f"data/{NS}/tags/block/boss_pas_sol.json", {"values": ["minecraft:water", "minecraft:lava", "minecraft:fire", "minecraft:soul_fire",
   "minecraft:powder_snow", "minecraft:cactus", "minecraft:magma_block", "minecraft:sweet_berry_bush", "minecraft:bedrock", "#minecraft:leaves"]})
w(F + "boss/place_ok.mcfunction", "\n".join(
    [f"execute if block ~ ~-1 ~ #{NS}:boss_vide run return 0", f"execute if block ~ ~-1 ~ #{NS}:boss_pas_sol run return 0"] +
    [f"execute unless block ~ ~{h} ~ #{NS}:boss_vide run return 0" for h in range(6)] + ["return 1"]))
w(F + "boss/lieu.mcfunction", "\n".join([
    "kill @e[type=minecraft:marker,tag=metiers.blieu]",
    'summon minecraft:marker ~ ~ ~ {Tags:["metiers.blieu"]}',
    "scoreboard players set #trouve m.boss 0", "scoreboard players set #essai m.boss 0",
    f"function {NS}:boss/lieu_essai",
    # rien trouvé autour du joueur : à la surface, comme avant
    "execute if score #trouve m.boss matches 0 run spreadplayers ~ ~ 4 12 false @e[type=minecraft:marker,tag=metiers.blieu]"]))
w(F + "boss/lieu_essai.mcfunction", "\n".join([
    "scoreboard players add #essai m.boss 1",
    "execute if score #essai m.boss matches 41.. run return 0",
    "execute store result score #dx m.boss run random value -12..12",
    "execute store result score #dz m.boss run random value -12..12",
    f"execute if score #dx m.boss matches -3..3 if score #dz m.boss matches -3..3 run return run function {NS}:boss/lieu_essai",
    f"execute store result storage {NS}:boss l.dx int 1 run scoreboard players get #dx m.boss",
    f"execute store result storage {NS}:boss l.dz int 1 run scoreboard players get #dz m.boss",
    f"function {NS}:boss/lieu_m with storage {NS}:boss l",
    f"execute if score #trouve m.boss matches 0 run function {NS}:boss/lieu_essai"]))
w(F + "boss/lieu_m.mcfunction", f"$execute positioned ~$(dx) ~ ~$(dz) align xyz positioned ~0.5 ~ ~0.5 run function {NS}:boss/lieu_col")
w(F + "boss/lieu_col.mcfunction", "\n".join(
    [f"execute if score #trouve m.boss matches 0 positioned ~ ~{dy} ~ if function {NS}:boss/place_ok run function {NS}:boss/lieu_ok" for dy in range(4, -9, -1)]))
w(F + "boss/lieu_ok.mcfunction", "scoreboard players set #trouve m.boss 1\ntp @e[type=minecraft:marker,tag=metiers.blieu,limit=1] ~ ~ ~")
for k, b in BOSS.items():
    attrs = (f'attributes:[{{id:"minecraft:max_health",base:$(hp)d}},{{id:"minecraft:attack_damage",base:{b["atk"]}d}},{{id:"minecraft:armor",base:{b["arm"]}d}},'
             f'{{id:"minecraft:knockback_resistance",base:1d}},{{id:"minecraft:movement_speed",base:{b["spd"]}d}},{{id:"minecraft:follow_range",base:64d}},'
             f'{{id:"minecraft:scale",base:{b["scale"]}d}}' + (',{id:"minecraft:spawn_reinforcements",base:0d}' if b["etype"] == "zombie" else "") + "]")
    nbt = (f'Tags:["metiers.boss"],CustomName:{{text:"{b["nom"]}",color:"{b["col"]}",bold:true}},CustomNameVisible:1b,PersistenceRequired:1b,DeathLootTable:"minecraft:empty",'
           f'Health:$(hp)f,{attrs}' + (f",{b['extra']}" if b["extra"] else ""))
    w(F + f"boss/apparaitre_{k}.mcfunction", "\n".join([
        f"$summon minecraft:{b['etype']} ~ ~ ~ {{{nbt}}}",
        f"effect give {B} minecraft:fire_resistance infinite 0 true",
        f'bossbar set metiers:boss name {{"text":"{b["nom"]}","color":"{b["col"]}","bold":true}}',
        f"bossbar set metiers:boss color {b['bar']}"]))

# 25/11/2026 : boss qui « s'enfuyait » quand le seul joueur se déconnectait (chunk déchargé = boss introuvable) et
# restait ensuite orphelin, sans barre ni récompense. Combat en pause sans joueur, 5 min de grâce si le boss est
# simplement hors des chunks chargés, et tout boss orphelin est repris dès qu'il est rechargé (boss/adopter).
w(F + "boss/encours.mcfunction", "\n".join([
    "execute unless entity @a[gamemode=!spectator] run return 0",
    f"execute store result score #hp m.boss run data get entity {B} Health",
    "execute if score #hp m.boss matches 1.. store result bossbar metiers:boss value run scoreboard players get #hp m.boss",
    f"execute if entity {B} run scoreboard players operation #last m.boss = #hp m.boss",
    f"execute as @a[scores={{m.dmg=1..}}] at @s if entity @e[tag=metiers.boss,distance=..32] run function {NS}:boss/frappe",
    "scoreboard players set @a m.dmg 0",
    # boss introuvable : tué, ou simplement dans un chunk déchargé ? On regarde si sa dernière position est chargée.
    f"execute unless entity {B} unless score #tue m.boss matches 1 run return run function {NS}:boss/absent with storage {NS}:boss",
    f"execute unless entity {B} run return run function {NS}:boss/disparu",
    "scoreboard players set #abs m.boss 0",
    f"execute store result storage {NS}:boss bx int 1 run data get entity {B} Pos[0]",
    f"execute store result storage {NS}:boss by int 1 run data get entity {B} Pos[1]",
    f"execute store result storage {NS}:boss bz int 1 run data get entity {B} Pos[2]",
    f'execute at {B} if dimension minecraft:overworld run data modify storage {NS}:boss bdim set value "minecraft:overworld"',
    f'execute at {B} if dimension minecraft:the_nether run data modify storage {NS}:boss bdim set value "minecraft:the_nether"',
    f'execute at {B} if dimension minecraft:the_end run data modify storage {NS}:boss bdim set value "minecraft:the_end"',
    "scoreboard players add #temps m.boss 1",
    "bossbar set metiers:boss players @a",
    "scoreboard players set #seuil m.boss 0", "scoreboard players operation #seuil m.boss = #max m.boss",
    "scoreboard players operation #seuil m.boss *= #2 m.const",
    "scoreboard players operation #hp3 m.boss = #hp m.boss", "scoreboard players operation #hp3 m.boss *= #3 m.const",
    f"execute if score #phase m.boss matches 0 if score #hp3 m.boss <= #seuil m.boss as {B} at @s run function {NS}:boss/vague",
    "scoreboard players operation #seuil m.boss = #max m.boss",
    f"execute if score #phase m.boss matches 1 if score #hp3 m.boss <= #seuil m.boss as {B} at @s run function {NS}:boss/vague",
    "scoreboard players add #atk m.boss 1",
    f"execute if score #phase m.boss matches 2 run scoreboard players add #atk m.boss 1",
    f"execute if score #atk m.boss matches 10.. as {B} at @s run function {NS}:boss/attaque",
    f"execute if score #mk m.boss matches 1.. run function {NS}:boss/marques",
    f"execute at {B} run function {NS}:boss/particules",
    "execute if score #type m.boss matches 5 if score #temps m.boss matches 2400.. run function metiers:boss/fuite",
    f"execute if score #temps m.boss matches 3600.. run function {NS}:boss/fuite"]))
AD = ["tag @s add metiers.badopte",
      f"kill @e[tag=metiers.boss,tag=!metiers.badopte]"]
for k, b in BOSS.items():
    AD += [f"execute if entity @s[type=minecraft:{b['etype']}] run scoreboard players set #type m.boss {k}"]
AD += ["tag @s remove metiers.badopte",
       f'data modify storage {NS}:boss bdim set value "minecraft:overworld"',
       "execute store result score #max m.boss run attribute @s minecraft:max_health base get",
       "execute store result score #hp m.boss run data get entity @s Health",
       "scoreboard players set #actif m.boss 1", "scoreboard players set #compte m.boss 0",
       "scoreboard players set #temps m.boss 0", "scoreboard players set #abs m.boss 0",
       "scoreboard players set #phase m.boss 0", "scoreboard players set #atk m.boss 0",
       "scoreboard players set #tue m.boss 0", "scoreboard players set #mk m.boss 0", "scoreboard players set #fin m.boss 0",
       "scoreboard players operation #last m.boss = #hp m.boss",
       "scoreboard players set @a m.dmg 0", "scoreboard players set @a m.bdmg 0",
       "execute store result bossbar metiers:boss max run scoreboard players get #max m.boss",
       "execute store result bossbar metiers:boss value run scoreboard players get #hp m.boss",
       "bossbar set metiers:boss style notched_10", "bossbar set metiers:boss visible true", "bossbar set metiers:boss players @a"]
for k, b in BOSS.items():
    AD += [f'execute if score #type m.boss matches {k} run bossbar set metiers:boss name {{"text":"{b["nom"]}","color":"{b["col"]}","bold":true}}',
           f"execute if score #type m.boss matches {k} run bossbar set metiers:boss color {b['bar']}"]
AD += [f'tellraw @a {PREFIX},{{"text":"Le boss est toujours là, le combat reprend !","color":"red","bold":true}}]']
w(F + "boss/adopter.mcfunction", "\n".join(AD))
w(F + "boss/frappe.mcfunction", "tag @s add metiers.bossp\nscoreboard players operation @s m.bdmg += @s m.dmg")
w(F + "boss/particules.mcfunction", "\n".join(
    [f"execute if score #type m.boss matches {k} run particle {b['part']} ~ ~2.5 ~ 0.9 1.6 0.9 0.02 10" for k, b in BOSS.items()]))
# position chargée et boss absent : il est mort (feu, chute, explosion...) -> fin du combat tout de suite.
# Position déchargée (joueur parti, déconnexion) : jusqu'à 5 min de grâce, la barre reste.
w(F + "boss/absent.mcfunction", "\n".join([
    f"$execute in $(bdim) if loaded $(bx) $(by) $(bz) run return run function {NS}:boss/disparu",
    "scoreboard players add #abs m.boss 1",
    f"execute if score #abs m.boss matches 600.. run return run function {NS}:boss/disparu",
    "bossbar set metiers:boss players @a"]))
w(F + "boss/disparu.mcfunction", "\n".join([
    f"execute if score #tue m.boss matches 1 run return run function {NS}:boss/victoire",
    # mort pendant que des joueurs le combattaient : victoire, même si le coup final n'est pas d'un joueur
    f"execute if entity @a[tag=metiers.bossp] if score #abs m.boss matches ..599 run return run function {NS}:boss/victoire",
    "scoreboard players operation #seuil m.boss = #max m.boss", "scoreboard players operation #seuil m.boss /= #4 m.const",
    f"execute if score #last m.boss <= #seuil m.boss run return run function {NS}:boss/victoire",
    f"function {NS}:boss/fuite"]))
w(F + "boss/tue.mcfunction", f"advancement revoke @s only {NS}:boss_tue\nscoreboard players set #tue m.boss 1\ntag @s add metiers.bossp")
# 25/11/2026 : les tirs (arc, arbalète, trident) ne comptent pas dans la statistique damage_dealt : un boss abattu à
# distance (Brasier qui vole, Creeper géant qu'on évite au corps à corps) ne récompensait personne. Tout coup porté au
# boss, projectile compris, inscrit maintenant le joueur (environ 4 PV comptés par touche pour le meilleur dégât).
wj(f"data/{NS}/advancement/boss_touche.json", {
    "criteria": {"touche": {"trigger": "minecraft:player_hurt_entity", "conditions": {"entity": {
        "type": "minecraft:entity_properties", "entity": "this",
        "predicate": {"minecraft:nbt": '{Tags:["metiers.boss"]}'}}}}},
    "rewards": {"function": f"{NS}:boss/touche"}})
w(F + "boss/touche.mcfunction", "\n".join([f"advancement revoke @s only {NS}:boss_touche",
    "tag @s add metiers.bossp", "execute unless score @s m.dmg matches 1.. run scoreboard players add @s m.bdmg 40"]))
# 25/11/2026 : le succès qui déclenche boss/tue n'était plus généré ; la victoire ne tenait qu'au filet « dernier PV
# connus sous 25 % » et le tueur n'était récompensé que s'il avait été vu frapper à moins de 32 blocs.
wj(f"data/{NS}/advancement/boss_tue.json", {
    "criteria": {"tue": {"trigger": "minecraft:player_killed_entity", "conditions": {"entity": {
        "type": "minecraft:entity_properties", "entity": "this",
        "predicate": {"minecraft:nbt": '{Tags:["metiers.boss"]}'}}}}},
    "rewards": {"function": f"{NS}:boss/tue"}})

# vagues à 66 % et 33 %
VG = ["scoreboard players add #phase m.boss 1"]
VG += [f"execute if score #type m.boss matches {k} run function {NS}:boss/vague_{k}" for k in BOSS]
VG += ["particle minecraft:large_smoke ~ ~1 ~ 2 1 2 0.05 120", "execute as @a at @s run playsound minecraft:entity.ravager.roar master @s ~ ~ ~ 1 0.5",
       ANN("Le boss appelle ses renforts !", "red"),
       f"execute if score #phase m.boss matches 2 run effect give @s minecraft:speed infinite 0 true",
       f"execute if score #phase m.boss matches 2 run effect give @s minecraft:strength infinite 0 true",
       f'execute if score #phase m.boss matches 2 run tellraw @a {PREFIX},{{"text":"Le boss est enragé : ses attaques s\'accélèrent.","color":"dark_red","bold":true}}]']
w(F + "boss/vague.mcfunction", "\n".join(VG))
for k, L in VAGUE.items():
    w(F + f"boss/vague_{k}.mcfunction", "\n".join(L))

# attaques (exécutées par le boss, à sa position)
AT = ["scoreboard players set #atk m.boss 0"]
for k, b in BOSS.items():
    n = len(b["atks"])
    AT.append(f"execute if score #type m.boss matches {k} store result score #r m.boss run random value 1..{n}")
    AT += [f"execute if score #type m.boss matches {k} if score #r m.boss matches {i} run function {NS}:boss/a_{a}" for i, a in enumerate(b["atks"], 1)]
w(F + "boss/attaque.mcfunction", "\n".join(AT))
PL = "gamemode=!spectator,gamemode=!creative"
A = {
    "seisme": [f"particle minecraft:explosion ~ ~ ~ 4 0.2 4 0 30", "playsound minecraft:entity.generic.explode hostile @a ~ ~ ~ 2 0.5",
               f"execute as @a[distance=..9,{PL}] run damage @s 8 minecraft:mob_attack by @e[tag=metiers.boss,limit=1]",
               f"effect give @a[distance=..9,{PL}] minecraft:levitation 1 3 true",
               ANN("Le Colosse frappe le sol !", "dark_red")],
    "bond": [f"execute as @p[distance=4..30,{PL}] at @s if function {NS}:boss/place_ok run tp @e[tag=metiers.boss,limit=1] ~ ~ ~",
             "playsound minecraft:entity.ravager.attack hostile @a ~ ~ ~ 2 0.6",
             f"execute at @s as @a[distance=..4,{PL}] run damage @s 6 minecraft:mob_attack by @e[tag=metiers.boss,limit=1]"],
    "venin": ["particle minecraft:item_slime ~ ~1 ~ 4 1 4 0 60", f"effect give @a[distance=..10,{PL}] minecraft:poison 6 1",
              "playsound minecraft:entity.spider.ambient hostile @a ~ ~ ~ 2 0.5", ANN("La Reine crache son venin.", "dark_green")],
    "toile": [f"execute as @a[distance=..16,{PL}] at @s run particle minecraft:crit ~ ~1 ~ 0.6 1 0.6 0 30",
              f"effect give @a[distance=..16,{PL}] minecraft:slowness 4 3", f"effect give @a[distance=..16,{PL}] minecraft:mining_fatigue 4 1",
              ANN("Vous êtes pris dans la toile !", "dark_green")],
    "drain": [f"effect give @a[distance=..12,{PL}] minecraft:wither 4 1", "effect give @s minecraft:instant_damage 1 1 true",
              "particle minecraft:soul ~ ~2 ~ 3 1 3 0.02 40", ANN("La Liche draine votre vie.", "aqua")],
    "blizzard": [f"execute as @a[distance=..16,{PL}] at @s run particle minecraft:snowflake ~ ~2 ~ 1 1 1 0.02 40",
                 f"execute as @a[distance=..16,{PL}] run damage @s 5 minecraft:freeze", f"effect give @a[distance=..16,{PL}] minecraft:slowness 3 1",
                 "playsound minecraft:block.powder_snow.break hostile @a ~ ~ ~ 2 0.5"],
    "clignement": [f"execute as @r[distance=..40,{PL}] at @s rotated ~ 0 positioned ^ ^ ^-4 align xyz positioned ~0.5 ~ ~0.5 if function {NS}:boss/place_ok run tp @e[tag=metiers.boss,limit=1] ~ ~ ~",
                   "particle minecraft:reverse_portal ~ ~1 ~ 1 1 1 0.2 60", "playsound minecraft:entity.enderman.teleport hostile @a ~ ~ ~ 2 0.5"],
    "pluie_feu": [f"execute as @a[distance=..20,{PL}] at @s run particle minecraft:flame ~ ~3 ~ 1 0.5 1 0.02 40",
                  f"execute as @a[distance=..20,{PL}] at @s run particle minecraft:lava ~ ~1 ~ 1 0.5 1 0 10",
                  f"execute as @a[distance=..20,{PL}] run damage @s 6 minecraft:in_fire",
                  "playsound minecraft:entity.blaze.shoot hostile @a ~ ~ ~ 2 0.5", ANN("Une pluie de braises s’abat !", "gold")],
    "onde": ["particle minecraft:flame ~ ~1 ~ 4 0.3 4 0.1 120", f"execute as @a[distance=..8,{PL}] run damage @s 9 minecraft:on_fire",
             "playsound minecraft:item.firecharge.use hostile @a ~ ~ ~ 2 0.5"],
    "detonation": [f'execute as @a[distance=..20,{PL}] at @s run summon minecraft:marker ~ ~ ~ {{Tags:["metiers.bmark"]}}',
                   "scoreboard players set #mk m.boss 6", "playsound minecraft:entity.creeper.primed hostile @a ~ ~ ~ 2 0.5",
                   ANN("Le Creeper géant gonfle... éloignez-vous des cercles !", "green")],
    "souffle": ["particle minecraft:explosion_emitter ~ ~1 ~ 0 0 0 0 1", "playsound minecraft:entity.generic.explode hostile @a ~ ~ ~ 3 0.6",
                f"execute as @a[distance=..7,{PL}] run damage @s 12 minecraft:explosion"],
}
for a, L in A.items():
    w(F + f"boss/a_{a}.mcfunction", "\n".join(L))
w(F + "boss/marques.mcfunction", "\n".join([
    "scoreboard players remove #mk m.boss 1",
    "execute at @e[type=minecraft:marker,tag=metiers.bmark] run particle minecraft:dust{color:[1.0,0.2,0.2],scale:1.5} ~ ~0.1 ~ 1.5 0 1.5 0 30",
    f"execute if score #mk m.boss matches 0 at @e[type=minecraft:marker,tag=metiers.bmark] run function {NS}:boss/explosion",
    "execute if score #mk m.boss matches 0 run kill @e[type=minecraft:marker,tag=metiers.bmark]"]))
w(F + "boss/explosion.mcfunction", "\n".join([
    "particle minecraft:explosion_emitter ~ ~ ~ 0 0 0 0 1", "playsound minecraft:entity.generic.explode hostile @a ~ ~ ~ 2 0.8",
    f"execute as @a[distance=..3.5,{PL}] run damage @s 10 minecraft:explosion"]))

w(F + "boss/fin.mcfunction", "\n".join([
    "kill @e[tag=metiers.sbire]", "kill @e[type=minecraft:marker,tag=metiers.bmark]",
    "scoreboard players set #actif m.boss 0", "scoreboard players set #cycle m.boss 0", "scoreboard players set #mk m.boss 0",
    "bossbar set metiers:boss visible false", "tag @a remove metiers.bossp", "tag @a remove metiers.btop", "scoreboard players set @a m.bdmg 0"]))
w(F + "boss/fuite.mcfunction", "\n".join([
    f"execute as {B} run tp @s ~ -400 ~", "kill @e[tag=metiers.boss]",
    ANN("Le boss s'est enfui... Il reviendra.", "gray"), f"function {NS}:boss/fin"]))
w(F + "boss/victoire.mcfunction", "\n".join([
    "execute unless score #actif m.boss matches 1 run return 0",
    "scoreboard players set #top m.boss 0",
    "execute as @a[tag=metiers.bossp] run scoreboard players operation #top m.boss > @s m.bdmg",
    "execute as @a[tag=metiers.bossp] if score @s m.bdmg = #top m.boss run tag @s add metiers.btop",
    f'tellraw @a {PREFIX},{{"text":"Le boss est terrassé ! ","color":"gold","bold":true}},{{"text":"Récompensés : ","color":"white"}},{{"selector":"@a[tag=metiers.bossp]","color":"yellow"}},{{"text":". Plus gros dégâts : ","color":"white"}},{{"selector":"@a[tag=metiers.btop]","color":"light_purple"}}]',
    f"execute as @a[tag=metiers.bossp] at @s run function {NS}:boss/recompense",
    "execute as @a at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 0.7",
    f"function {NS}:boss/fin"]))
RC = ["scoreboard players add @s m.ecl 3", "execute if entity @s[tag=metiers.btop] run scoreboard players add @s m.ecl 2",  # 25.6 : boss 2,5 fois plus rares, butin plus gros
      # 25/11/2026 : 30 % du niveau de Chasseur en cours au lieu d'un niveau entier
      "scoreboard players operation @s m.tmp = @s m.c_need", "scoreboard players operation @s m.tmp *= #3 m.const",
      "scoreboard players operation @s m.tmp /= #10 m.const",
      "scoreboard players operation @s m.c_bal += @s m.tmp", f"function {NS}:c/gain",
      "execute if score @s c.ecus matches -2147483648.. run scoreboard players add @s c.ecus 5000"]
RC += [f"execute if score #type m.boss matches {k} run scoreboard players add @s m.bk{k} 1" for k in BOSS]
RC += [f'tellraw @s {PREFIX},{{"text":"Récompense : ","color":"gold"}},{json.dumps(gj("eclat"), ensure_ascii=False)},{{"text":" 3 éclats de boss, 30 % d’un niveau de Chasseur et 5 000 Écus.","color":"gold"}}]',
       f'execute if entity @s[tag=metiers.btop] run tellraw @s {PREFIX},{{"text":"Plus gros dégâts : +2 éclats de boss.","color":"light_purple"}}]',
       "particle minecraft:totem_of_undying ~ ~1 ~ 0.5 1 0.5 0.4 80"]
w(F + "boss/recompense.mcfunction", "\n".join(RC))
# le Brasier ne met pas le feu au décor : ses boules de feu sont supprimées
add_lines(F + "refonte/tick.mcfunction", ["execute if score #actif m.boss matches 1 if score #type m.boss matches 4 run kill @e[type=minecraft:small_fireball]"])
add_lines(F + "refonte/load.mcfunction", ["scoreboard players add #type m.boss 0", "scoreboard players add #mk m.boss 0", "scoreboard players add #tue m.boss 0"] +
          [f"scoreboard players set #{c} m.const {c}" for c in (2, 3, 5, 10, 15, 50, 100, 150, 200, 300, 7200)])


# ---------------------------------------------------------------- butin des boss : une table par boss, tirée 1 fois en facile,
# 2 en normal, 3 en difficile, +1 pour le plus gros dégât ; et une chance d'objet rare (10 % par niveau de difficulté, +10 % au top)
def E(n, w, a=1, b=1, extra=None):
    e = {"type": "minecraft:item", "name": f"minecraft:{n}", "weight": w}
    mods = []
    if (a, b) != (1, 1): mods.append({"type": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": a, "max": b}})
    if extra: mods.append(extra)
    if mods: e["modifier"] = mods
    return e
def EN(n, w, a=1, b=1, ench=None, niv=None, nom=None, col="gold", lore=None):
    """Entrée de butin : quantité, enchantements fixes ou au hasard (niveau d'enchantement), nom et description de relique."""
    mods = []
    if (a, b) != (1, 1): mods.append({"type": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": a, "max": b}})
    if niv: mods.append({"type": "minecraft:enchant_with_levels", "levels": niv})
    if ench: mods.append({"type": "minecraft:set_enchantments", "enchantments": {f"minecraft:{k}": v for k, v in ench.items()}})
    if nom:
        mods.append({"type": "minecraft:set_name", "target": "custom_name", "name": {"text": nom, "color": col, "bold": True, "italic": False}})
        mods.append({"type": "minecraft:set_lore", "mode": "replace_all", "lore": [{"text": lore, "color": "gray", "italic": False},
                                                                                {"text": "Relique de boss", "color": "light_purple", "italic": False}]})
        mods.append({"type": "minecraft:set_components", "components": {"minecraft:rarity": "epic"}})
        mods.append({"type": "minecraft:set_custom_data", "tag": {"metiers_relique": True}})   # vendable au Commerce (Butin de boss)
    e = {"type": "minecraft:item", "name": f"minecraft:{n}", "weight": w}
    if mods: e["modifier"] = mods
    return e
# butin courant (25.8 : plus aucun outil, arme ni armure, les métiers les donnent déjà), tiré 1 fois en facile, 2 en normal, 3 en difficile, +1 pour le plus gros dégât
BUTIN = {
    1: [EN("diamond", 12, 3, 6), EN("iron_block", 12, 2, 5), EN("gold_block", 10, 1, 3), EN("emerald_block", 8, 1, 3),
        EN("netherite_scrap", 6, 1, 2), EN("ancient_debris", 5, 1, 2), EN("experience_bottle", 4, 16, 32), EN("enchanted_book", 4, niv=30),
        EN("netherite_upgrade_smithing_template", 3), EN("anvil", 3)],
    2: [EN("ender_pearl", 12, 4, 8), EN("diamond", 10, 2, 4), EN("enchanted_book", 10, niv=30), EN("golden_apple", 8, 2, 4),
        EN("name_tag", 6, 1, 2), EN("string", 8, 16, 32), EN("cobweb", 5, 4, 8), EN("saddle", 4), EN("ominous_bottle", 4), EN("emerald_block", 4, 1, 3)],
    3: [EN("experience_bottle", 14, 16, 32), EN("enchanted_book", 12, niv=30), EN("diamond", 10, 2, 4), EN("lapis_block", 10, 3, 6),
        EN("amethyst_shard", 6, 8, 16), EN("blue_ice", 6, 8, 16), EN("echo_shard", 3, 1, 2), EN("nautilus_shell", 3, 1, 3), EN("diamond", 4, 1, 3)],
    4: [EN("blaze_rod", 14, 8, 16), EN("gold_block", 10, 2, 5), EN("netherite_scrap", 8, 1, 3), EN("ancient_debris", 6, 1, 3),
        EN("golden_apple", 8, 2, 4), EN("magma_cream", 6, 6, 12), EN("fire_charge", 5, 8, 16), EN("netherite_ingot", 2), EN("ghast_tear", 4, 2, 4)],
    5: [EN("diamond", 10, 2, 4), EN("emerald_block", 8, 2, 4), EN("tnt", 10, 4, 8), EN("gunpowder", 12, 16, 32), EN("firework_rocket", 8, 32, 64),
        EN("heart_of_the_sea", 2), EN("emerald", 4, 8, 16)] +
       [EN(f"music_disc_{d}", 2) for d in ("cat", "blocks", "chirp", "far", "mall", "mellohi", "stal", "strad", "ward", "wait")] +
       [EN("music_disc_pigstep", 1), EN("music_disc_otherside", 1)],
}
# reliques : un objet unique par boss, dans le butin rare
RELIQUE = {
    1: EN("netherite_axe", 4, ench={"sharpness": 5, "efficiency": 5, "unbreaking": 3, "mending": 1}, nom="Hache du Colosse", col="dark_red",
          lore="Arrachée au Colosse des Métiers."),
    2: EN("bow", 4, ench={"power": 5, "punch": 2, "flame": 1, "infinity": 1, "unbreaking": 3}, nom="Arc de la Reine", col="dark_green",
          lore="Tendu avec la soie de la Reine arachnide."),
    3: EN("trident", 4, ench={"impaling": 5, "loyalty": 3, "unbreaking": 3, "mending": 1}, nom="Trident du givre", col="aqua",
          lore="Taillé dans la glace de la Liche."),
    4: EN("mace", 4, ench={"density": 5, "fire_aspect": 2, "unbreaking": 3, "mending": 1}, nom="Masse du Brasier", col="gold",
          lore="Encore tiède du Brasier ancestral."),   # 25.8 : remplace le plastron (inutile à côté de l'Armure des Guildes)
    5: EN("crossbow", 4, ench={"multishot": 1, "quick_charge": 3, "unbreaking": 3, "mending": 1}, nom="Arbalète du Creeper", col="green",
          lore="Gonflée à bloc, comme le Creeper géant."),
}
RARE = [EN("enchanted_golden_apple", 3), EN("totem_of_undying", 3), EN("netherite_ingot", 3), EN("heart_of_the_sea", 2),
        EN("shulker_shell", 2, 2, 4), EN("nether_star", 1)]
# 26/11/2026 : tables plus écrites (plus aucun objet de boss, et surtout plus d'arme ni d'armure nulle part)
# 25/11/2026 : plus aucun objet en butin de boss (ni minerais, ni reliques), seulement éclats, Écus et XP. Les tables
# de butin ci-dessus restent écrites mais ne sont plus tirées. Chaque tirage (1 par niveau de difficulté, +1 pour le
# meilleur dégât) rapporte 2 500 Écus ; le « butin rare » devient 2 éclats et 5 000 Écus de plus.
BT = ["execute store result score #diff m.boss run difficulty", "scoreboard players operation #tirs m.boss = #diff m.boss",
      "execute if entity @s[tag=metiers.btop] run scoreboard players add #tirs m.boss 1",
      "scoreboard players operation #gain m.boss = #tirs m.boss", "scoreboard players operation #gain m.boss *= #2500 m.const",
      "execute if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus += #gain m.boss",
      "scoreboard players operation #chance m.boss = #diff m.boss", "scoreboard players operation #chance m.boss *= #15 m.const",
      "scoreboard players add #chance m.boss 20",
      "execute if entity @s[tag=metiers.btop] run scoreboard players add #chance m.boss 15",
      "execute store result score #r m.boss run random value 1..100",
      "execute if score #r m.boss <= #chance m.boss run scoreboard players add @s m.ecl 2",
      "execute if score #r m.boss <= #chance m.boss if score @s c.ecus matches -2147483648.. run scoreboard players add @s c.ecus 5000",
      f'execute if score #r m.boss <= #chance m.boss run tellraw @a {PREFIX},{{"selector":"@s","color":"white"}},{{"text":" décroche le bonus rare du boss : 2 éclats et 5 000 Écus !","color":"light_purple","bold":true}}]',
      f'tellraw @s {PREFIX},{{"text":"Prime de combat : ","color":"gold"}},{{"score":{{"name":"#gain","objective":"m.boss"}},"color":"yellow"}},{{"text":" Écus (plus en difficile).","color":"gold"}}]']
add_lines(F + "refonte/load.mcfunction", ["scoreboard players set #2500 m.const 2500"])
w(F + "boss/butin.mcfunction", "\n".join(BT))
add_lines(F + "boss/recompense.mcfunction", [f"function {NS}:boss/butin"])


# ---------------------------------------------------------------- Brasier : rien ne brûle
# Pendant le combat, la règle mob_griefing passe à false (les boules de feu ne posent plus de feu), puis reprend sa valeur.
# En plus, le feu éventuel autour du boss est éteint toutes les 0,5 s.
add_lines(F + "boss/apparaitre_4.mcfunction", ["weather clear 1800s", "execute store result score #mg m.boss run gamerule mob_griefing",
                                               "scoreboard players set #mgset m.boss 1", "gamerule mob_griefing false"])
add_lines(F + "boss/fin.mcfunction", ["execute if score #mgset m.boss matches 1 if score #mg m.boss matches 1 run gamerule mob_griefing true",
                                      "scoreboard players set #mgset m.boss 0"])
add_lines(F + "boss/encours.mcfunction", [f"execute if score #type m.boss matches 4 at {B} run fill ~-15 ~-8 ~-15 ~15 ~7 ~15 minecraft:air replace minecraft:fire"])
add_lines(F + "refonte/load.mcfunction", ["execute if score #mgset m.boss matches 1 unless score #actif m.boss matches 1 run gamerule mob_griefing true",
                                          "execute if score #mgset m.boss matches 1 unless score #actif m.boss matches 1 run scoreboard players set #mgset m.boss 0"])
# position mémorisée du boss : valeur de départ hors du monde (jamais chargée) pour qu'un combat repris sans position
# connue passe par la grâce de 5 min au lieu d'être déclaré terminé
add_lines(F + "refonte/load.mcfunction", [
    f'execute unless data storage {NS}:boss bx run data merge storage {NS}:boss {{bx:29999000,by:64,bz:29999000,bdim:"minecraft:overworld"}}'])

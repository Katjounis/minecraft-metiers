# -*- coding: utf-8 -*-
# Refonte v24, partie 5 : récompenses des défis en cristaux, défi de la semaine, défi collectif, barres violettes et roses.

GJ = lambda n: json.dumps(gj(n), ensure_ascii=False)

# ---------------------------------------------------------------- défis du jour : 4 cristaux + un demi-niveau
for j, d in jobs.items():
    w(F + f"defis/fini_{j}.mcfunction", "\n".join([
        f"scoreboard players set @s m.dd_{j} 1", f"scoreboard players operation @s m.tmp = @s m.{j}_need", "scoreboard players operation @s m.tmp /= #2 m.const",
        f"scoreboard players operation @s m.{j}_bal += @s m.tmp", f"scoreboard players add @s m.cr_{j} 4",
        f'tellraw @a {PREFIX},{{"selector":"@s","color":"white"}},{{"text":" a réussi le défi du jour ","color":"gray"}},{GJ("metier_" + j)},{{"text":" {d["name"]}","color":"{d["color"]}","bold":true}}]',
        f'tellraw @s {PREFIX},{{"text":"+4 ","color":"aqua"}},{GJ("cristal_" + j)},{{"text":" cristaux de {d["name"]} et un demi-niveau.","color":"aqua"}}]',
        "playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1.2", "scoreboard players set @s m.tmp 0"] +
        [f"execute if score @s m.dd_{jj} matches 1 run scoreboard players add @s m.tmp 1" for jj in jobs] +
        [f"execute if score @s m.tmp matches {NJ} run function {NS}:defis/tous", f"function {NS}:defis/plus1"]))
w(F + "defis/tous.mcfunction", "\n".join(
    [f"scoreboard players add @s m.cr_{j} 2" for j in jobs] +
    [f'tellraw @a {PREFIX},{{"selector":"@s","color":"white"}},{{"text":" a réussi tous les défis du jour ! +2 cristaux de chaque métier.","color":"gold","bold":true}}]',
     "playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 0.5"]))
for j, pool in DEFIS.items():
    d = jobs[j]
    BJ = ["$bossbar set metiers:d$(id) color purple", "$bossbar set metiers:d$(id) style notched_10"]
    for i, (desc, tgt, crits, div) in enumerate(pool, 1):
        BJ += [f'$execute if score #d_{j} m.defi matches {i} run bossbar set metiers:d$(id) name [{GJ("metier_" + j)},{{"text":" Défi {d["name"]} : ","color":"{d["color"]}","bold":true}},{{"text":"{desc}  ","color":"white","bold":false}},{{"score":{{"name":"@s","objective":"m.dp_{j}"}},"color":"yellow"}},{{"text":" / {tgt}","color":"gray"}}]',
               f"$execute if score #d_{j} m.defi matches {i} run bossbar set metiers:d$(id) max {tgt}"]
    BJ.append(f"$execute store result bossbar metiers:d$(id) value run scoreboard players get @s m.dp_{j}")
    w(F + f"defis/barre_{j}.mcfunction", "\n".join(BJ))
w(F + "defis/barre_fini.mcfunction", "\n".join([
    '$bossbar set metiers:d$(id) name [{"text":"✔ Tous les défis du jour sont faits ! ","color":"green","bold":true},{"text":"Nouveaux défis dans ","color":"white","bold":false},{"score":{"name":"#left","objective":"m.defi"},"color":"yellow"},{"text":" h","color":"white"}]',
    "$bossbar set metiers:d$(id) color purple", "$bossbar set metiers:d$(id) max 1", "$bossbar set metiers:d$(id) value 1"]))

# ---------------------------------------------------------------- heure du métier : barre rose avec icône
HL = ["scoreboard players set #cycle m.heure 0", f"execute store result score #job m.heure run random value 1..{NJ}",
      "scoreboard players set #reste m.heure 3600", "bossbar set metiers:heure color pink", "bossbar set metiers:heure style progress"]
for j, d in jobs.items():
    i = d["idx"]
    HL += [f'execute if score #job m.heure matches {i} run bossbar set metiers:heure name [{GJ("metier_" + j)},{{"text":" Heure du {d["name"]}","color":"{d["color"]}","bold":true}},{{"text":" : XP x2","color":"white","bold":false}}]',
           f'execute if score #job m.heure matches {i} run tellraw @a {PREFIX},{{"text":"C\'est l\'heure du {d["name"]} ! ","color":"{d["color"]}","bold":true}},{{"text":"Toute l\'XP de ce métier compte double pendant 30 minutes.","color":"white"}}]']
HL += ["bossbar set metiers:heure visible true", "bossbar set metiers:heure players @a",
       "execute as @a at @s run playsound minecraft:block.bell.use master @s ~ ~ ~ 1 1"]
w(F + "heure/lancer.mcfunction", "\n".join(HL))

# ---------------------------------------------------------------- défi de la semaine (personnel) et défi collectif
SEM = [("b", "Coupe 1000 bûches", 1000, [f"minecraft.mined:minecraft.{l}" for l in LOGS], 1),
       ("f", "Récolte 1500 cultures", 1500, ["minecraft.picked_up:minecraft.wheat", "minecraft.picked_up:minecraft.carrot", "minecraft.picked_up:minecraft.potato", "minecraft.picked_up:minecraft.beetroot"], 1),
       ("m", "Mine 3000 blocs de pierre ou deepslate", 3000, ["minecraft.mined:minecraft.stone", "minecraft.mined:minecraft.deepslate"], 1),
       ("c", "Élimine 400 créatures", 400, ["minecraft.custom:minecraft.mob_kills"], 1),
       ("p", "Pêche 200 poissons", 200, ["minecraft.custom:minecraft.fish_caught"], 1),
       ("e", "Fais naître 120 animaux", 120, ["minecraft.custom:minecraft.animals_bred"], 1),
       ("n", "Enchante 40 objets", 40, ["minecraft.custom:minecraft.enchant_item"], 1),
       ("x", "Parcours 40 km à pied", 40000, ["minecraft.custom:minecraft.walk_one_cm", "minecraft.custom:minecraft.sprint_one_cm"], 100),
       ("t", "Fais 150 échanges", 150, ["minecraft.custom:minecraft.traded_with_villager"], 1)]
COLL = [("Ensemble : minez 10 000 blocs de pierre", 10000, ["minecraft.mined:minecraft.stone", "minecraft.mined:minecraft.deepslate"]),
        ("Ensemble : coupez 3000 bûches", 3000, [f"minecraft.mined:minecraft.{l}" for l in LOGS]),
        ("Ensemble : éliminez 1500 créatures", 1500, ["minecraft.custom:minecraft.mob_kills"]),
        ("Ensemble : pêchez 400 poissons", 400, ["minecraft.custom:minecraft.fish_caught"]),
        ("Ensemble : faites 400 échanges", 400, ["minecraft.custom:minecraft.traded_with_villager"]),
        ("Ensemble : récoltez 4000 cultures", 4000, ["minecraft.picked_up:minecraft.wheat", "minecraft.picked_up:minecraft.carrot", "minecraft.picked_up:minecraft.potato"])]
LDW = ["scoreboard objectives add m.ccs dummy"]
for i, (_, _, _, crits, _) in enumerate(SEM, 1):
    LDW += [f"scoreboard objectives add dw.{i}_{n} {c}" for n, c in enumerate(crits)]
for i, (_, _, crits) in enumerate(COLL, 1):
    LDW += [f"scoreboard objectives add dc.{i}_{n} {c}" for n, c in enumerate(crits)]
add_lines(F + "refonte/load.mcfunction", LDW)

NW = ["scoreboard players set #semaine m.defi 0", f"execute store result score #s_def m.defi run random value 1..{len(SEM)}",
      f"execute store result score #c_def m.defi run random value 1..{len(COLL)}", "scoreboard players set #c_ok m.defi 0",
      "scoreboard players reset * m.wd", "scoreboard players reset * m.wk", "scoreboard players reset * m.cc"]
for i, (_, _, _, crits, _) in enumerate(SEM, 1):
    NW += [f"scoreboard players reset * dw.{i}_{n}" for n in range(len(crits))]
for i, (_, _, crits) in enumerate(COLL, 1):
    NW += [f"scoreboard players reset * dc.{i}_{n}" for n in range(len(crits))]
NW.append(f'tellraw @a {PREFIX},{{"text":"Nouvelle semaine : un défi de la semaine et un défi collectif sont lancés ","color":"light_purple","bold":true}},{{"text":"(touche G, Défis du jour).","color":"white"}}]')
w(F + "defis/semaine.mcfunction", "\n".join(NW))
# horloge : 7 journées de défis (temps de jeu avec au moins un joueur connecté)
add_lines(F + "defis/tick.mcfunction", [
    "execute if entity @a run scoreboard players add #semaine m.defi 1",
    f"execute unless score #s_def m.defi matches 1.. run function {NS}:defis/semaine",
    f"execute if score #semaine m.defi matches 201600.. run function {NS}:defis/semaine",
    "scoreboard players set #sleft m.defi 201600", "scoreboard players operation #sleft m.defi -= #semaine m.defi",
    "scoreboard players operation #sleft m.defi /= #7200 m.const", "scoreboard players add #sleft m.defi 1",
    f"execute if score #quatre m.timer matches 0 run function {NS}:defis/collectif_total"])
CT = ["scoreboard players set #c_tot m.defi 0"]
for i, (_, tgt, crits) in enumerate(COLL, 1):
    CT += [f"execute if score #c_def m.defi matches {i} run scoreboard players operation #c_tot m.defi += * dc.{i}_{n}" for n in range(len(crits))]
    CT.append(f"execute if score #c_def m.defi matches {i} run scoreboard players set #c_tgt m.defi {tgt}")
CT += [f"execute if score #c_ok m.defi matches 0 if score #c_tot m.defi >= #c_tgt m.defi run function {NS}:defis/collectif_fini"]
w(F + "defis/collectif_total.mcfunction", "\n".join(CT))
w(F + "defis/collectif_fini.mcfunction", "\n".join([
    "scoreboard players set #c_ok m.defi 1",
    f'tellraw @a {PREFIX},{{"text":"Défi collectif réussi ! ","color":"light_purple","bold":true}},{{"text":"Chaque joueur qui y a participé (2 % de l\'objectif) reçoit un éclat de boss.","color":"white"}}]',
    "execute as @a at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 0.9"]))
# suivi par joueur (ajouté à defis/joueur, toutes les secondes)
DW = ["scoreboard players set @s m.wp 0", "scoreboard players set @s m.cc 0"]
for i, (j, desc, tgt, crits, div) in enumerate(SEM, 1):
    DW += [f"execute if score #s_def m.defi matches {i} run scoreboard players operation @s m.wp += @s dw.{i}_{n}" for n in range(len(crits))]
    if div > 1:
        DW.append(f"execute if score #s_def m.defi matches {i} run scoreboard players operation @s m.wp /= #100 m.const")
    DW.append(f"execute if score #s_def m.defi matches {i} unless score @s m.wd matches 1 if score @s m.wp matches {tgt}.. run function {NS}:defis/semaine_fini_{i}")
    w(F + f"defis/semaine_fini_{i}.mcfunction", "\n".join([
        "scoreboard players set @s m.wd 1", f"scoreboard players add @s m.cr_{j} 20", "scoreboard players add @s m.ecl 1",
        f'tellraw @a {PREFIX},{{"selector":"@s","color":"white"}},{{"text":" a réussi le défi de la semaine ! ","color":"light_purple","bold":true}},{{"text":"+20 ","color":"aqua"}},{GJ("cristal_" + j)},{{"text":" et 1 ","color":"aqua"}},{GJ("eclat")}]',
        "playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 0.8"]))
for i, (_, tgt, crits) in enumerate(COLL, 1):
    DW += [f"execute if score #c_def m.defi matches {i} run scoreboard players operation @s m.cc += @s dc.{i}_{n}" for n in range(len(crits))]
    DW.append(f"execute if score #c_def m.defi matches {i} run scoreboard players set #c_min m.defi {max(1, tgt // 50)}")
DW.append(f"execute if score #c_ok m.defi matches 1 unless score @s m.wk matches 1 if score @s m.cc >= #c_min m.defi run function {NS}:defis/collectif_gain")
add_lines(F + "defis/joueur.mcfunction", DW)
w(F + "defis/collectif_gain.mcfunction", "\n".join([
    "scoreboard players set @s m.wk 1", "scoreboard players add @s m.ecl 1",
    f'tellraw @s {PREFIX},{{"text":"Défi collectif : +1 ","color":"light_purple"}},{GJ("eclat")},{{"text":" éclat de boss.","color":"light_purple"}}]']))

# ---------------------------------------------------------------- écran des défis
DM = [f"function {NS}:defis/joueur", f"execute store result storage {NS}:defis left int 1 run scoreboard players get #left m.defi",
      f"execute store result storage {NS}:defis sleft int 1 run scoreboard players get #sleft m.defi",
      f"execute store result storage {NS}:defis wp int 1 run scoreboard players get @s m.wp",
      f"execute store result storage {NS}:defis cc int 1 run scoreboard players get @s m.cc",
      f"execute store result storage {NS}:defis ct int 1 run scoreboard players get #c_tot m.defi",
      f'data modify storage {NS}:defis wok set value ""', f'execute if score @s m.wd matches 1 run data modify storage {NS}:defis wok set value "  ✔ réussi"',
      f'data modify storage {NS}:defis cok set value ""', f'execute if score #c_ok m.defi matches 1 run data modify storage {NS}:defis cok set value "  ✔ réussi"']
for i, (j, desc, tgt, crits, div) in enumerate(SEM, 1):
    DM += [f'execute if score #s_def m.defi matches {i} run data modify storage {NS}:defis wd set value "{desc}"',
           f"execute if score #s_def m.defi matches {i} run data modify storage {NS}:defis wt set value {tgt}",
           f'execute if score #s_def m.defi matches {i} run data modify storage {NS}:defis wj set value "{GLY["cristal_" + j]}"']
for i, (desc, tgt, crits) in enumerate(COLL, 1):
    DM += [f'execute if score #c_def m.defi matches {i} run data modify storage {NS}:defis cd set value "{desc}"',
           f"execute if score #c_def m.defi matches {i} run data modify storage {NS}:defis cg set value {tgt}",
           f"execute if score #c_def m.defi matches {i} run data modify storage {NS}:defis cm set value {max(1, tgt // 50)}"]
for j, pool in DEFIS.items():
    DM += [f"execute store result storage {NS}:defis {j}_p int 1 run scoreboard players get @s m.dp_{j}",
           f'data modify storage {NS}:defis {j}_ok set value ""',
           f'execute if score @s m.dd_{j} matches 1 run data modify storage {NS}:defis {j}_ok set value "  ✔"']
    for i, (desc, tgt, crits, div) in enumerate(pool, 1):
        DM += [f'execute if score #d_{j} m.defi matches {i} run data modify storage {NS}:defis {j}_d set value "{desc}"',
               f"execute if score #d_{j} m.defi matches {i} run data modify storage {NS}:defis {j}_t set value {tgt}"]
DM.append(f"function {NS}:defis/menu_dialog with storage {NS}:defis")
w(F + "defis/menu.mcfunction", "\n".join(DM))
lines = []
for j, d in jobs.items():
    lines.append(f'{gs("metier_" + j)},{{text:" {d["name"]}  ",color:"{d["color"]}",bold:true}},{{text:"$({j}_d)  ",color:"white",bold:false}},'
                 f'{{text:"$({j}_p) / $({j}_t)",color:"yellow"}},{{text:"$({j}_ok)\\n",color:"green",bold:true}}')
db = [f'{{type:"minecraft:plain_message",width:400,contents:[{{text:"Défis du jour\\n",color:"aqua",bold:true}},{",".join(lines)},'
      f'{{text:"Chaque défi : 4 cristaux du métier et un demi-niveau. Les 9 : +2 cristaux de chaque métier. Nouveaux défis dans $(left) h.",color:"gray"}}]}}',
      f'{{type:"minecraft:plain_message",width:400,contents:[{{text:"Défi de la semaine\\n",color:"light_purple",bold:true}},{{text:"$(wd)  ",color:"white"}},'
      f'{{text:"$(wp) / $(wt)",color:"yellow"}},{{text:"$(wok)\\n",color:"green",bold:true}},{{text:"Récompense : 20 ",color:"gray"}},{{text:"$(wj)",font:"metiers:icones",color:"white"}},'
      f'{{text:" et 1 ",color:"gray"}},{gs("eclat")},{{text:"   ·   ",color:"gray"}},{{text:"Fin dans $(sleft) h de jeu.",color:"gray"}}]}}',
      f'{{type:"minecraft:plain_message",width:400,contents:[{{text:"Défi collectif\\n",color:"gold",bold:true}},{{text:"$(cd)  ",color:"white"}},'
      f'{{text:"$(ct) / $(cg)",color:"yellow"}},{{text:"$(cok)\\n",color:"green",bold:true}},{{text:"Ta part : $(cc). Il faut au moins $(cm) pour toucher 1 ",color:"gray"}},{gs("eclat")},{{text:" éclat.",color:"gray"}}]}}']
w(F + "defis/menu_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Défis",color:"aqua",bold:true},can_close_with_escape:true,pause:false,'
  'body:[' + ",".join(db) + '],actions:[{label:{text:"Afficher / masquer la barre",color:"white"},width:200,action:{type:"run_command",command:"trigger metiers set 7"}}],'
  'columns:1,exit_action:{label:"Retour",width:150,action:{type:"run_command",command:"trigger metiers set 1"}}}')
w(F + "version.mcfunction", 'tellraw @s {"text":"[Métiers] Version 24 : refonte (outils 11 paliers, Forge, skins, 5 boss, défis de la semaine et collectifs)","color":"gold"}')

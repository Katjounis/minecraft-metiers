# -*- coding: utf-8 -*-
# Métiers 25 (23/11/2026) : synergies, quêtes, guildes, boss plus durs, effets visuels, bandeaux des menus.
# Exécuté à la fin de datapack.py (mêmes variables : w, wj, jobs, JL, NS, F, PREFIX, tr, btn, txt, gs, add_lines...).
S = "scoreboard players"
BANDEAU = lambda k: ('{type:"minecraft:plain_message",width:310,contents:[{text:""},{text:"' + chr(0xE020 + k) +
                     '",font:"commerce:recette",color:"white",shadow_color:0},{text:"\\n\\n"}]}')
# bandeaux dessinés par Commerce (police commerce:recette) : 7 MÉTIERS, 8 FORGE, 9 QUÊTES, 10 GUILDE, 11 BARÈME, 12 BESTIAIRE
BAN_METIERS, BAN_FORGE, BAN_QUETES, BAN_GUILDE, BAN_BAREME = 7, 8, 9, 10, 11

add_lines(F + "refonte/load.mcfunction", [f"scoreboard objectives add {o} dummy" for o in
          ("m.gid", "m.ginv", "m.gxp", "m.gwk", "m.syn")] + [f"scoreboard objectives add m.q_{j} dummy" for j in JL] +
          [f"scoreboard objectives add m.qb_{j} dummy" for j in JL] +
          [f"{S} add #gidn m.const 0", f"{S} add #gweek m.const 0",
           f"execute unless data storage {NS}:gu L run data modify storage {NS}:gu L set value []"])

# =====================================================================
# SYNERGIES : deux métiers au niveau 50 (ou passés par le prestige) débloquent un bonus permanent
# =====================================================================
SYN = [  # (id, métier 1, métier 2, nom, effet)
    ("bf", "b", "f", "Sylviculture", "10 % de chance d’une pomme par bûche coupée."),
    ("mx", "m", "x", "Spéléologue", "Vision nocturne et Résistance I sous la couche 0."),
    ("cn", "c", "n", "Lame savante", "30 % de chance de 5 points d’expérience en plus par monstre tué."),
    ("pe", "p", "e", "Ami des bêtes", "Chance I en permanence (meilleur butin)."),
    ("mt", "m", "t", "Négoce", "+5 % sur toutes tes ventes au Commerce."),
    ("fc", "f", "c", "Garde-manger", "Saturation : la faim ne descend plus quand tu es rassasié."),
    ("kb", "k", "b", "Charpentier", "Célérité II avec une hache en main."),
]
SYT = []
for sid, a, b, nom, eff in SYN:
    ok = lambda j: f"execute if score @s m.{j}_lvl matches 50.."
    SYT += [f"tag @s remove metiers.sk.y{sid}",
            f"execute if score @s m.{a}_lvl matches 50.. if score @s m.{b}_lvl matches 50.. run tag @s add metiers.sk.y{sid}",
            f"execute if score @s m.{a}_pr matches 1.. if score @s m.{b}_lvl matches 50.. run tag @s add metiers.sk.y{sid}",
            f"execute if score @s m.{a}_lvl matches 50.. if score @s m.{b}_pr matches 1.. run tag @s add metiers.sk.y{sid}",
            f"execute if score @s m.{a}_pr matches 1.. if score @s m.{b}_pr matches 1.. run tag @s add metiers.sk.y{sid}"]
SYT += ["execute if entity @s[tag=metiers.sk.ymx] if predicate {type:\"minecraft:location_check\",predicate:{position:{y:{max:0}}}} run effect give @s minecraft:night_vision 15 0 true",
        "execute if entity @s[tag=metiers.sk.ymx] if predicate {type:\"minecraft:location_check\",predicate:{position:{y:{max:0}}}} run effect give @s minecraft:resistance 3 0 true",
        "execute if entity @s[tag=metiers.sk.ype] run effect give @s minecraft:luck infinite 0 true",
        "execute if entity @s[tag=metiers.sk.yfc] run effect give @s minecraft:saturation 1 0 true",
        "execute if entity @s[tag=metiers.sk.ykb] if items entity @s weapon.mainhand #minecraft:axes run effect give @s minecraft:haste 3 1 true",
        # Négoce : Commerce lit m.syn (1 = +5 % sur les ventes)
        "scoreboard players set @s m.syn 0", "execute if entity @s[tag=metiers.sk.ymt] run scoreboard players set @s m.syn 1"]
w(F + "synergie/tick.mcfunction", "\n".join(SYT))
add_lines(F + "refonte/joueur.mcfunction", [f"execute if score #quatre m.timer matches 0 run function {NS}:synergie/tick"])
SYP = []
for sid, a, b, nom, eff in SYN:
    SYP += [f'data modify storage {NS}:sy {sid} set value "dark_gray"', f'execute if entity @s[tag=metiers.sk.y{sid}] run data modify storage {NS}:sy {sid} set value "green"',
            f'data modify storage {NS}:sy {sid}t set value "✖"', f'execute if entity @s[tag=metiers.sk.y{sid}] run data modify storage {NS}:sy {sid}t set value "✔"']
SYP.append(f"function {NS}:synergie/page_d with storage {NS}:sy")
w(F + "synergie/page.mcfunction", "\n".join(SYP))
sy_l = []
for sid, a, b, nom, eff in SYN:
    # 25/11/2026 : une ligne par synergie, l'effet s'affiche au survol du nom
    sy_l.append(f'{{text:"$({sid}t) ",color:"$({sid})",bold:true}},{gs("metier_" + a)},{gs("metier_" + b)},{{text:" {nom}",color:"$({sid})",bold:true,'
                f'hover_event:{{action:"show_text",value:{{text:"{eff}",color:"white"}}}}}},'
                f'{{text:"  {jobs[a]["name"]} + {jobs[b]["name"]}\\n",color:"gray",bold:false}}')
w(F + "synergie/page_d.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Synergies",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  f'body:[{BANDEAU(BAN_METIERS)},{{type:"minecraft:plain_message",width:400,contents:[{{text:"Deux métiers au niveau 50 (ou passés par le prestige) débloquent un bonus permanent. Survole un nom pour son effet.\\n\\n",color:"gray"}},{",".join(sy_l)}]}}],'
  'actions:[{label:{text:"Retour",color:"white"},width:200,action:{type:"run_command",command:"trigger metiers set 1"}}],columns:1}')

# =====================================================================
# QUÊTES : 10 étapes par métier, progression comptée depuis le début de l'étape (statistiques du jeu)
# =====================================================================
QUETES = {
    "b": [("mined:minecraft.oak_log", 64, "Couper 64 bûches de chêne"), ("mined:minecraft.spruce_log", 64, "Couper 64 bûches de sapin"),
          ("mined:minecraft.birch_log", 128, "Couper 128 bûches de bouleau"), ("mined:minecraft.jungle_log", 128, "Couper 128 bûches d’acajou"),
          ("mined:minecraft.dark_oak_log", 128, "Couper 128 bûches de chêne noir"), ("mined:minecraft.acacia_log", 128, "Couper 128 bûches d’acacia"),
          ("mined:minecraft.mangrove_log", 128, "Couper 128 bûches de palétuvier"), ("mined:minecraft.cherry_log", 192, "Couper 192 bûches de cerisier"),
          ("mined:minecraft.crimson_stem", 192, "Couper 192 tiges carmin"), ("mined:minecraft.warped_stem", 256, "Couper 256 tiges biscornues")],
    "f": [("picked_up:minecraft.wheat", 128, "Récolter 128 blés"), ("picked_up:minecraft.carrot", 128, "Récolter 128 carottes"),
          ("picked_up:minecraft.potato", 192, "Récolter 192 pommes de terre"), ("picked_up:minecraft.beetroot", 192, "Récolter 192 betteraves"),
          ("mined:minecraft.melon", 64, "Casser 64 pastèques"), ("mined:minecraft.pumpkin", 64, "Casser 64 citrouilles"),
          ("picked_up:minecraft.nether_wart", 192, "Récolter 192 verrues du Nether"), ("mined:minecraft.sugar_cane", 192, "Couper 192 cannes à sucre"),
          ("mined:minecraft.cocoa", 96, "Récolter 96 cabosses de cacao"), ("picked_up:minecraft.sweet_berries", 256, "Récolter 256 baies sucrées")],
    "m": [("mined:minecraft.coal_ore", 64, "Miner 64 minerais de charbon"), ("mined:minecraft.iron_ore", 64, "Miner 64 minerais de fer"),
          ("mined:minecraft.copper_ore", 96, "Miner 96 minerais de cuivre"), ("mined:minecraft.deepslate_iron_ore", 96, "Miner 96 minerais de fer des abîmes"),
          ("mined:minecraft.redstone_ore", 64, "Miner 64 minerais de redstone"), ("mined:minecraft.lapis_ore", 48, "Miner 48 minerais de lapis"),
          ("mined:minecraft.gold_ore", 48, "Miner 48 minerais d’or"), ("mined:minecraft.diamond_ore", 16, "Miner 16 minerais de diamant"),
          ("mined:minecraft.deepslate_diamond_ore", 32, "Miner 32 diamants des abîmes"), ("mined:minecraft.ancient_debris", 16, "Miner 16 débris antiques")],
    "c": [("killed:minecraft.zombie", 50, "Tuer 50 zombies"), ("killed:minecraft.skeleton", 50, "Tuer 50 squelettes"),
          ("killed:minecraft.spider", 40, "Tuer 40 araignées"), ("killed:minecraft.creeper", 30, "Tuer 30 creepers"),
          ("killed:minecraft.enderman", 25, "Tuer 25 endermen"), ("killed:minecraft.witch", 15, "Tuer 15 sorcières"),
          ("killed:minecraft.blaze", 25, "Tuer 25 blazes"), ("killed:minecraft.wither_skeleton", 20, "Tuer 20 wither squelettes"),
          ("killed:minecraft.evoker", 5, "Tuer 5 évocateurs"), ("killed:minecraft.ravager", 5, "Tuer 5 ravageurs")],
    "p": [("custom:minecraft.fish_caught", n, f"Pêcher {n} prises") for n in (32, 64, 128, 192, 256, 320, 400, 500, 650, 800)],
    "e": [("custom:minecraft.animals_bred", n, f"Faire naître {n} animaux") for n in (10, 25, 50, 75, 100, 150, 200, 250, 300, 400)],
    "n": [("custom:minecraft.enchant_item", n, f"Enchanter {n} objets") for n in (5, 10, 20, 30, 40, 50, 65, 80, 100, 128)],
    "x": [("custom:minecraft.walk_one_cm", km * 100000, f"Marcher {km} km") for km in (2, 5, 10, 15, 20, 30, 40, 50, 75, 100)],
    "t": [("custom:minecraft.traded_with_villager", n, f"Faire {n} échanges") for n in (10, 25, 50, 75, 100, 150, 200, 300, 400, 500)],
    "k": [("used:minecraft.oak_planks", 128, "Poser 128 planches de chêne"), ("used:minecraft.cobblestone", 192, "Poser 192 pierres taillées"),
          ("used:minecraft.stone_bricks", 192, "Poser 192 briques de pierre"), ("used:minecraft.glass", 128, "Poser 128 blocs de verre"),
          ("used:minecraft.bricks", 192, "Poser 192 briques"), ("used:minecraft.spruce_planks", 256, "Poser 256 planches de sapin"),
          ("used:minecraft.white_concrete", 256, "Poser 256 bétons blancs"), ("used:minecraft.deepslate_tiles", 256, "Poser 256 carrelages d’ardoise des abîmes"),
          ("used:minecraft.quartz_block", 256, "Poser 256 blocs de quartz"), ("used:minecraft.end_stone_bricks", 320, "Poser 320 briques de l’End")],
}
QL = []
for j in JL:
    for n, (crit, tgt, txt_) in enumerate(QUETES[j], 1):
        QL.append(f"scoreboard objectives add q.{j}{n} minecraft.{crit}")
add_lines(F + "refonte/load.mcfunction", QL)
QC = []
for j in JL:
    d = jobs[j]
    QC += [f"execute unless score @s m.q_{j} matches 1.. run function {NS}:quete/{j}_debut_1",
           f"execute if score @s m.q_{j} matches 1..10 run function {NS}:quete/{j}"]
    QJ = []
    for n, (crit, tgt, txt_) in enumerate(QUETES[j], 1):
        QJ.append(f"execute if score @s m.q_{j} matches {n} run return run function {NS}:quete/{j}_{n}")
        w(F + f"quete/{j}_{n}.mcfunction", "\n".join([
            f"{S} add @s q.{j}{n} 0",
            f"scoreboard players operation #qp m.tmp = @s q.{j}{n}", f"scoreboard players operation #qp m.tmp -= @s m.qb_{j}",
            f"execute if score #qp m.tmp matches {tgt}.. run function {NS}:quete/{j}_fin_{n}"]))
        cr = 20 * n
        nxt = [f"function {NS}:quete/{j}_debut_{n + 1}"] if n < 10 else [f"{S} set @s m.q_{j} 11"]
        w(F + f"quete/{j}_fin_{n}.mcfunction", "\n".join([
            f"scoreboard players add @s m.cr_{j} {cr}",
            f"scoreboard players operation @s m.tmp = @s m.{j}_need", f"scoreboard players operation @s m.tmp /= #2 m.const",
            f"scoreboard players operation @s m.{j}_bal += @s m.tmp"] +
            ([f"scoreboard players add @s m.ecl 1"] if n % 3 == 0 else []) +
            [f"execute if score @s c.ecus matches -2147483648.. run scoreboard players add @s c.ecus {200 * n}",
             'tellraw @a ' + PREFIX + f',{{"selector":"@s","color":"white"}},{{"text":" termine la quête {d["name"]} {n}/10 : ","color":"gray"}},{{"text":"{txt_}","color":"{d["color"]}","bold":true}}]',
             tr(f"Récompense : {cr} cristaux de {d['name']}, un demi-niveau" + (", 1 éclat de boss" if n % 3 == 0 else "") + f", {200 * n} Écus.", "gold"),
             "playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 0.8 1.3",
             "particle minecraft:totem_of_undying ~ ~1 ~ 0.4 0.8 0.4 0.3 40"] + nxt))
        w(F + f"quete/{j}_debut_{n}.mcfunction", "\n".join([
            f"{S} set @s m.q_{j} {n}", f"{S} add @s q.{j}{n} 0", f"scoreboard players operation @s m.qb_{j} = @s q.{j}{n}"]))
    w(F + f"quete/{j}.mcfunction", "\n".join(QJ))
w(F + "quete/tick.mcfunction", "\n".join(QC))
add_lines(F + "refonte/joueur.mcfunction", [f"execute if score #quatre m.timer matches 0 run function {NS}:quete/tick"])
# page des quêtes (495)
QP = []
for j in JL:
    QP += [f'data modify storage {NS}:qu {j}t set value "Toutes les quêtes sont finies !"', f'data modify storage {NS}:qu {j}p set value ""']
    for n, (crit, tgt, txt_) in enumerate(QUETES[j], 1):
        unit = 100000 if j == "x" else 1
        QP += [f'execute if score @s m.q_{j} matches {n} run data modify storage {NS}:qu {j}t set value "{n}/10 · {txt_}"',
               f"execute if score @s m.q_{j} matches {n} run scoreboard players operation #qp m.tmp = @s q.{j}{n}",
               f"execute if score @s m.q_{j} matches {n} run scoreboard players operation #qp m.tmp -= @s m.qb_{j}"]
        if unit > 1:
            QP.append(f"execute if score @s m.q_{j} matches {n} run scoreboard players operation #qp m.tmp /= #1000 m.const")
            QP.append(f"execute if score @s m.q_{j} matches {n} run scoreboard players operation #qp m.tmp /= #100 m.const")
        QP += [f"execute if score @s m.q_{j} matches {n} store result storage {NS}:qu {j}n int 1 run scoreboard players get #qp m.tmp",
               f"execute if score @s m.q_{j} matches {n} run function {NS}:quete/prog {{j:\"{j}\",t:\"{tgt // unit}{' km' if unit > 1 else ''}\"}}"]
QP.append(f"function {NS}:quete/page_d with storage {NS}:qu")
w(F + "quete/page.mcfunction", "\n".join(QP))
w(F + "quete/prog.mcfunction", f'$function {NS}:quete/prog_m {{j:"$(j)",t:"$(t)"}}')
w(F + "quete/prog_m.mcfunction", f"$data modify storage {NS}:qu $(j)p set value \"   ($(j)n/$(t))\"".replace("$(j)n", "§N"))
# la progression lue dans le storage puis recopiée en texte
w(F + "quete/prog_m.mcfunction", "\n".join([
    f"$data modify storage {NS}:qu tmp set value {{t:\"$(t)\"}}",
    f"$data modify storage {NS}:qu tmp.n set from storage {NS}:qu $(j)n",
    f"$data modify storage {NS}:qu tmp.j set value \"$(j)\"",
    f"function {NS}:quete/prog_txt with storage {NS}:qu tmp"]))
w(F + "quete/prog_txt.mcfunction", f'$data modify storage {NS}:qu $(j)p set value "   ($(n)/$(t))"')
ql = []
for j in JL:
    d = jobs[j]
    ql.append(f'{gs("metier_" + j)},{{text:" {d["name"]}  ",color:"{d["color"]}",bold:true}},{{text:"$({j}t)",color:"white"}},{{text:"$({j}p)\\n",color:"yellow"}}')
w(F + "quete/page_d.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Quêtes des métiers",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  f'body:[{BANDEAU(BAN_QUETES)},{{type:"minecraft:plain_message",width:420,contents:[{{text:"Une quête par métier, 10 étapes chacune. Récompense : cristaux, un quart de niveau, des Écus, et un éclat toutes les 3 étapes.\\n\\n",color:"gray"}},{",".join(ql)}]}}],'
  'actions:[{label:{text:"Retour",color:"white"},width:200,action:{type:"run_command",command:"trigger metiers set 1"}}],columns:1}')

# =====================================================================
# GUILDES : créer, inviter, quitter, exclure ; défi de la semaine (XP gagnée ensemble) ; classement
#   storage metiers:gu L : [{id, nomc (texte), chef (id), mem: [{id, nom}], pts (XP de toujours)}]
#   scores : m.gid (guilde du joueur), m.ginv (invitation), m.gxp (XP pas encore versée à la guilde),
#            #g<id> m.gxpt (XP de la semaine), m.gwk (semaine de la dernière récompense touchée)
# =====================================================================
G_ = F + "guilde/"
w(G_ + "nom.mcfunction", "\n".join([  # pseudo du joueur exécutant -> storage metiers:gu moi
    f'data modify storage {NS}:gu moi set value "?"',
    'summon minecraft:item_display ~ ~-2 ~ {Tags:["metiers.nomeur"],item:{id:"minecraft:paper",count:1}}',
    'item modify entity @e[type=minecraft:item_display,tag=metiers.nomeur,limit=1] contents {function:"minecraft:set_name",type:"minecraft:set_name",entity:"this",target:"custom_name",name:{selector:"@s"}}',
    f'data modify storage {NS}:gu moi set from entity @e[type=minecraft:item_display,tag=metiers.nomeur,limit=1] item.components."minecraft:custom_name".text',
    f'execute unless data entity @e[type=minecraft:item_display,tag=metiers.nomeur,limit=1] item.components."minecraft:custom_name".text run data modify storage {NS}:gu moi set from entity @e[type=minecraft:item_display,tag=metiers.nomeur,limit=1] item.components."minecraft:custom_name"',
    "kill @e[type=minecraft:item_display,tag=metiers.nomeur]"]))
# créer (771) : nom = objet renommé tenu en main, sinon « Guilde de <pseudo> »
w(G_ + "creer.mcfunction", "\n".join([
    f"execute if score @s m.gid matches 1.. run return run {tr('Tu es déjà dans une guilde.', 'red')}",
    "scoreboard players add #gidn m.const 1", "scoreboard players operation @s m.gid = #gidn m.const",
    f"function {NS}:guilde/nom",
    f"data modify storage {NS}:gu n set value {{mem:[],pts:0}}",
    f"execute store result storage {NS}:gu n.id int 1 run scoreboard players get #gidn m.const",
    f"execute store result storage {NS}:gu n.chef int 1 run scoreboard players get @s m.id",
    f"function {NS}:guilde/nom_guilde with storage {NS}:gu",
    f'execute if data entity @s SelectedItem.components."minecraft:custom_name" run data modify storage {NS}:gu n.nomc set from entity @s SelectedItem.components."minecraft:custom_name"',
    f"data modify storage {NS}:gu L append from storage {NS}:gu n",
    f"function {NS}:guilde/ajouter_moi",
    'tellraw @a ' + PREFIX + ',{"selector":"@s","color":"white"},{"text":" fonde une guilde !","color":"gold","bold":true}]',
    "playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1", f"function {NS}:guilde/page"]))
w(G_ + "nom_guilde.mcfunction", f'$data modify storage {NS}:gu n.nomc set value {{text:"Guilde de $(moi)"}}')
w(G_ + "ajouter_moi.mcfunction", "\n".join([
    f"function {NS}:guilde/nom",
    f"execute store result storage {NS}:gu a.g int 1 run scoreboard players get @s m.gid",
    f"execute store result storage {NS}:gu a.id int 1 run scoreboard players get @s m.id",
    f"data modify storage {NS}:gu a.nom set from storage {NS}:gu moi",
    f"function {NS}:guilde/ajouter_m with storage {NS}:gu a"]))
w(G_ + "ajouter_m.mcfunction", f'$data modify storage {NS}:gu L[{{id:$(g)}}].mem append value {{id:$(id),nom:"$(nom)"}}')
# quitter (772)
w(G_ + "quitter.mcfunction", "\n".join([
    f"execute unless score @s m.gid matches 1.. run return run {tr('Tu n’es dans aucune guilde.', 'red')}",
    f"execute store result storage {NS}:gu a.g int 1 run scoreboard players get @s m.gid",
    f"execute store result storage {NS}:gu a.id int 1 run scoreboard players get @s m.id",
    f"function {NS}:guilde/oter_m with storage {NS}:gu a",
    f"{S} set @s m.gid 0", tr("Tu as quitté ta guilde.", "yellow"), f"function {NS}:guilde/page"]))
w(G_ + "oter_m.mcfunction", "\n".join([
    f"$data remove storage {NS}:gu L[{{id:$(g)}}].mem[{{id:$(id)}}]",
    # plus personne : la guilde disparaît ; le chef part : le premier membre restant devient chef
    f"$execute unless data storage {NS}:gu L[{{id:$(g)}}].mem[0] run return run data remove storage {NS}:gu L[{{id:$(g)}}]",
    f"$execute if data storage {NS}:gu L[{{id:$(g),chef:$(id)}}] run data modify storage {NS}:gu L[{{id:$(g)}}].chef set from storage {NS}:gu L[{{id:$(g)}}].mem[0].id"]))
# inviter (773 : liste des joueurs en ligne sans guilde, clic = 71xxxxx)
w(G_ + "inviter_liste.mcfunction", "\n".join([
    f"execute unless function {NS}:guilde/suis_chef run return run {tr('Seul le chef de la guilde invite.', 'red')}",
    f"data modify storage {NS}:gu D set value [{{text:\"\"}}]",
    f"execute as @a[scores={{m.gid=..0}}] run function {NS}:guilde/inviter_ligne",
    f"execute as @a unless score @s m.gid matches -2147483648.. run function {NS}:guilde/inviter_ligne",
    f"function {NS}:guilde/inviter_d with storage {NS}:gu"]))
w(G_ + "suis_chef.mcfunction", "\n".join([
    f"execute unless score @s m.gid matches 1.. run return fail",
    f"execute store result storage {NS}:gu a.g int 1 run scoreboard players get @s m.gid",
    f"execute store result storage {NS}:gu a.id int 1 run scoreboard players get @s m.id",
    f"return run function {NS}:guilde/suis_chef_m with storage {NS}:gu a"]))
w(G_ + "suis_chef_m.mcfunction", f"$execute if data storage {NS}:gu L[{{id:$(g),chef:$(id)}}] run return 1\nreturn fail")
w(G_ + "inviter_ligne.mcfunction", "\n".join([
    f"function {NS}:guilde/nom", f"execute store result storage {NS}:gu b.id int 1 run scoreboard players get @s m.id",
    "scoreboard players set #tv m.tmp 7100000", "scoreboard players operation #tv m.tmp += @s m.id",
    f"execute store result storage {NS}:gu b.v int 1 run scoreboard players get #tv m.tmp",
    f"data modify storage {NS}:gu b.nom set from storage {NS}:gu moi", f"function {NS}:guilde/inviter_ligne_m with storage {NS}:gu b"]))
w(G_ + "inviter_ligne_m.mcfunction",
  f'$data modify storage {NS}:gu D append value {{text:"$(nom)     ",color:"yellow",underlined:true,click_event:{{action:"run_command",command:"trigger metiers set $(v)"}},hover_event:{{action:"show_text",value:"Inviter $(nom)"}}}}')
w(G_ + "inviter_d.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Inviter dans la guilde",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:plain_message",width:320,contents:[{text:"Joueurs en ligne sans guilde (clic pour inviter) :\\n\\n",color:"gray"},{text:"",extra:$(D)}]}],'
  'actions:[{label:{text:"Retour"},width:200,action:{type:"run_command",command:"trigger metiers set 770"}}],columns:1}')
w(G_ + "inviter.mcfunction", "\n".join([  # #v = 7100000 + id du joueur invité
    f"execute unless function {NS}:guilde/suis_chef run return 0",
    "scoreboard players operation #cible m.tmp = @s m.trig", "scoreboard players remove #cible m.tmp 7100000",
    "scoreboard players operation #g m.tmp = @s m.gid",
    f"execute as @a if score @s m.id = #cible m.tmp run function {NS}:guilde/invite_recu",
    tr("Invitation envoyée.", "green")]))
w(G_ + "invite_recu.mcfunction", "\n".join([
    "scoreboard players operation @s m.ginv = #g m.tmp",
    'tellraw @s ' + PREFIX + ',{"text":"Tu es invité dans une guilde ! ","color":"gold"},{"text":"[Accepter]","color":"green","bold":true,"click_event":{"action":"run_command","command":"/trigger metiers set 775"}}]',
    "playsound minecraft:block.note_block.bell master @s ~ ~ ~ 1 1.5"]))
w(G_ + "accepter.mcfunction", "\n".join([
    f"execute if score @s m.gid matches 1.. run return run {tr('Quitte d’abord ta guilde.', 'red')}",
    f"execute unless score @s m.ginv matches 1.. run return run {tr('Aucune invitation en attente.', 'red')}",
    f"execute store result storage {NS}:gu a.g int 1 run scoreboard players get @s m.ginv",
    f"execute unless function {NS}:guilde/existe run return run {tr('Cette guilde n’existe plus.', 'red')}",
    "scoreboard players operation @s m.gid = @s m.ginv", f"{S} set @s m.ginv 0",
    "scoreboard players operation @s m.gwk = #gweek m.const",
    f"function {NS}:guilde/ajouter_moi",
    'tellraw @a ' + PREFIX + ',{"selector":"@s","color":"white"},{"text":" rejoint une guilde.","color":"gold"}]',
    f"function {NS}:guilde/page"]))
w(G_ + "existe.mcfunction", f"return run function {NS}:guilde/existe_m with storage {NS}:gu a")
w(G_ + "existe_m.mcfunction", f"$execute if data storage {NS}:gu L[{{id:$(g)}}] run return 1\nreturn fail")
# exclure (72xxxxx : id du membre) : marche aussi hors ligne (score par pseudo)
w(G_ + "exclure.mcfunction", "\n".join([
    f"execute unless function {NS}:guilde/suis_chef run return run {tr('Seul le chef exclut.', 'red')}",
    "scoreboard players operation #cible m.tmp = @s m.trig", "scoreboard players remove #cible m.tmp 7200000",
    f"execute if score #cible m.tmp = @s m.id run return run {tr('Pour partir, utilise « Quitter ».', 'red')}",
    f"execute store result storage {NS}:gu a.id int 1 run scoreboard players get #cible m.tmp",
    f"data modify storage {NS}:gu a.nom set value \"\"",
    f"function {NS}:guilde/exclure_m with storage {NS}:gu a",
    f"function {NS}:guilde/page"]))
w(G_ + "exclure_m.mcfunction", "\n".join([
    f"$data modify storage {NS}:gu a.nom set from storage {NS}:gu L[{{id:$(g)}}].mem[{{id:$(id)}}].nom",
    f"$data remove storage {NS}:gu L[{{id:$(g)}}].mem[{{id:$(id)}}]",
    f"function {NS}:guilde/exclure_score with storage {NS}:gu a"]))
w(G_ + "exclure_score.mcfunction", "$scoreboard players set $(nom) m.gid 0\n$tellraw @a[name=$(nom)] " + PREFIX + ',{"text":"Tu as été exclu de ta guilde.","color":"red"}]')
# XP versée à la guilde (toutes les 2 s) et défi de la semaine : 5 000 XP par membre ; récompense 3 éclats chacun
for j in JL:
    add_lines(F + f"{j}/gain.mcfunction", ["execute if score @s m.gid matches 1.. run scoreboard players operation @s m.gxp += @s m.gain"])
w(G_ + "tick.mcfunction", "\n".join([
    f"execute if score @s m.gid matches 1.. if score @s m.gxp matches 1.. run function {NS}:guilde/verser",
    f"execute if score @s m.gid matches 1.. unless score @s m.gwk = #gweek m.const run function {NS}:guilde/recompense_verif"]))
w(G_ + "verser.mcfunction", "\n".join([
    f"execute store result storage {NS}:gu a.g int 1 run scoreboard players get @s m.gid",
    f"execute store result storage {NS}:gu a.x int 1 run scoreboard players get @s m.gxp",
    f"{S} set @s m.gxp 0", f"function {NS}:guilde/verser_m with storage {NS}:gu a"]))
w(G_ + "verser_m.mcfunction", "\n".join([
    "$scoreboard players add #g$(g) m.gxpt $(x)",
    f"$execute store result score #p m.tmp run data get storage {NS}:gu L[{{id:$(g)}}].pts",
    "$scoreboard players add #p m.tmp $(x)",
    f"$execute store result storage {NS}:gu L[{{id:$(g)}}].pts int 1 run scoreboard players get #p m.tmp"]))
w(G_ + "recompense_verif.mcfunction", "\n".join([
    f"execute store result storage {NS}:gu a.g int 1 run scoreboard players get @s m.gid",
    f"function {NS}:guilde/objectif with storage {NS}:gu a",
    "execute unless score #gx m.tmp >= #gobj m.tmp run return 0",
    "scoreboard players operation @s m.gwk = #gweek m.const", "scoreboard players add @s m.ecl 3",
    tr("Défi de guilde de la semaine réussi : +3 éclats de boss !", "gold"),
    "playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1.1"]))
w(G_ + "objectif.mcfunction", "\n".join([  # #gx = XP de la semaine, #gobj = 5 000 x membres
    f"{S} set #gx m.tmp 0", "$execute store result score #gx m.tmp run scoreboard players get #g$(g) m.gxpt",
    f"$execute store result score #gobj m.tmp run data get storage {NS}:gu L[{{id:$(g)}}].mem",
    "scoreboard players operation #gobj m.tmp *= #5000 m.const"]))
add_lines(F + "refonte/load.mcfunction", ["scoreboard objectives add m.gxpt dummy", f"{S} set #5000 m.const 5000"])
add_lines(F + "refonte/joueur.mcfunction", [f"execute if score #quatre m.timer matches 0 run function {NS}:guilde/tick"])
add_lines(F + "defis/semaine.mcfunction", ["scoreboard players add #gweek m.const 1", "scoreboard players reset * m.gxpt"])
# page de la guilde (770)
GP = [f"execute unless score @s m.gid matches 1.. run return run function {NS}:guilde/page_sans",
      f"execute store result storage {NS}:gu a.g int 1 run scoreboard players get @s m.gid",
      f"function {NS}:guilde/page_m with storage {NS}:gu a"]
w(G_ + "page.mcfunction", "\n".join(GP))
w(G_ + "page_m.mcfunction", "\n".join([
    f"$data modify storage {NS}:gu p set from storage {NS}:gu L[{{id:$(g)}}]",
    f"function {NS}:guilde/objectif with storage {NS}:gu a",
    f"execute store result storage {NS}:gu p.x int 1 run scoreboard players get #gx m.tmp",
    f"execute store result storage {NS}:gu p.o int 1 run scoreboard players get #gobj m.tmp",
    f'data modify storage {NS}:gu p.ok set value ""',
    f'execute if score @s m.gwk = #gweek m.const run data modify storage {NS}:gu p.ok set value "  ✔ réussi"',
    f"data modify storage {NS}:gu M set value [{{text:\"\"}}]", f"data modify storage {NS}:gu W set from storage {NS}:gu p.mem",
    f"function {NS}:guilde/membres",
    f"function {NS}:guilde/classement",
    f"function {NS}:guilde/page_d with storage {NS}:gu p"]))
w(G_ + "membres.mcfunction", "\n".join([
    f"execute unless data storage {NS}:gu W[0] run return 0",
    "scoreboard players set #tv m.tmp 7200000",
    f"execute store result score #ti m.tmp run data get storage {NS}:gu W[0].id", "scoreboard players operation #tv m.tmp += #ti m.tmp",
    f"execute store result storage {NS}:gu W[0].v int 1 run scoreboard players get #tv m.tmp",
    f"function {NS}:guilde/membre_m with storage {NS}:gu W[0]",
    f"data remove storage {NS}:gu W[0]", f"function {NS}:guilde/membres"]))
w(G_ + "membre_m.mcfunction",
  f'$data modify storage {NS}:gu M append value {{text:"$(nom)   ",color:"white",click_event:{{action:"run_command",command:"trigger metiers set $(v)"}},hover_event:{{action:"show_text",value:"Chef : clic pour exclure $(nom)"}}}}')
# classement des guildes (XP de toujours), 5 premières
w(G_ + "classement.mcfunction", "\n".join([
    f"data modify storage {NS}:gu R set value [{{text:\"\"}}]", f"data modify storage {NS}:gu W set from storage {NS}:gu L",
    f"{S} set #rk m.tmp 0", f"function {NS}:guilde/rang"]))
w(G_ + "rang.mcfunction", "\n".join([
    "execute if score #rk m.tmp matches 5.. run return 0", f"execute unless data storage {NS}:gu W[0] run return 0",
    f"{S} set #m m.tmp -1", f"data modify storage {NS}:gu W2 set from storage {NS}:gu W", f"function {NS}:guilde/max",
    "scoreboard players add #rk m.tmp 1", f"execute store result storage {NS}:gu best.r int 1 run scoreboard players get #rk m.tmp",
    f"function {NS}:guilde/rang_ligne with storage {NS}:gu best",
    f"function {NS}:guilde/rang_oter with storage {NS}:gu best", f"function {NS}:guilde/rang"]))
w(G_ + "max.mcfunction", "\n".join([
    f"execute unless data storage {NS}:gu W2[0] run return 0",
    f"execute store result score #x m.tmp run data get storage {NS}:gu W2[0].pts",
    f"execute if score #x m.tmp > #m m.tmp run data modify storage {NS}:gu best set from storage {NS}:gu W2[0]",
    "execute if score #x m.tmp > #m m.tmp run scoreboard players operation #m m.tmp = #x m.tmp",
    f"data remove storage {NS}:gu W2[0]", f"function {NS}:guilde/max"]))
w(G_ + "rang_ligne.mcfunction", "\n".join([
    f'$data modify storage {NS}:gu R append value {{text:"$(r). ",color:"gray"}}',
    f"$data modify storage {NS}:gu R append value $(nomc)",
    f'$data modify storage {NS}:gu R append value {{text:"   $(pts) XP\\n",color:"gold"}}']))
w(G_ + "rang_oter.mcfunction", f"$data remove storage {NS}:gu W[{{id:$(id)}}]")
w(G_ + "page_d.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"",extra:[$(nomc)],color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  f'body:[{BANDEAU(BAN_GUILDE)},{{type:"minecraft:plain_message",width:380,contents:[{{text:"Défi de la semaine : ",color:"gold",bold:true}},{{text:"$(x) / $(o) XP de métier gagnée ensemble",color:"white"}},{{text:"$(ok)\\n",color:"green"}},'
  '{text:"Récompense : 3 éclats de boss pour chaque membre.\\n\\n",color:"gray"},{text:"Membres : ",color:"gold",bold:true},{text:"",extra:$(M)},'
  '{text:"\\n\\nClassement des guildes\\n",color:"gold",bold:true},{text:"",extra:$(R)}]}],'
  'actions:[{label:{text:"Inviter",color:"green"},width:150,action:{type:"run_command",command:"trigger metiers set 773"}},'
  '{label:{text:"Quitter la guilde",color:"red"},width:150,action:{type:"run_command",command:"trigger metiers set 772"}},'
  '{label:{text:"Trésor de guilde",color:"gold",bold:true},width:150,tooltip:{text:"Dans le Commerce : dépôts des membres, niveaux de guilde (ventes, épargne, XP de métier pour tous)."},action:{type:"run_command",command:"trigger commerce set 7700"}},'
  '{label:{text:"Retour"},width:150,action:{type:"run_command",command:"trigger metiers set 1"}}],columns:3}')
w(G_ + "page_sans.mcfunction", "\n".join([
    f"function {NS}:guilde/classement", f"function {NS}:guilde/page_sans_d with storage {NS}:gu"]))
w(G_ + "page_sans_d.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Guildes",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  f'body:[{BANDEAU(BAN_GUILDE)},{{type:"minecraft:plain_message",width:380,contents:[{{text:"Fonde une guilde avec tes amis : un défi commun chaque semaine (3 éclats chacun), un coffre partagé (panneau [Guilde] sur un coffre, avec le Commerce) et un classement.\\n\\n",color:"gray"}},'
  '{text:"Le nom de la guilde est celui de l’objet renommé que tu tiens en main (une enclume suffit), sinon « Guilde de <ton pseudo> ».\\n\\n",color:"white"},'
  '{text:"Classement des guildes\\n",color:"gold",bold:true},{text:"",extra:$(R)}]}],'
  'actions:[{label:{text:"Fonder une guilde",color:"gold",bold:true},width:150,action:{type:"run_command",command:"trigger metiers set 771"}},'
  '{label:{text:"Accepter l’invitation",color:"green"},width:150,action:{type:"run_command",command:"trigger metiers set 775"}},'
  '{label:{text:"Retour"},width:150,action:{type:"run_command",command:"trigger metiers set 1"}}],columns:3}')

# =====================================================================
# BOSS PLUS DURS : adaptés au niveau des joueurs, une attaque en plus chacun, phase finale à 15 %
# =====================================================================
add_lines(F + "boss/apparaitre.mcfunction", [
    # niveau moyen de Chasseur des joueurs connectés (prestige compris) : +1 dégât et +1 armure tous les 20 niveaux
    f"{S} set #ns m.boss 0", f"{S} set #nn m.boss 0",
    "execute as @a[gamemode=!spectator] run scoreboard players operation #ns m.boss += @s m.c_lvl",
    "execute as @a[gamemode=!spectator] run scoreboard players add #nn m.boss 1",
    "execute if score #nn m.boss matches 1.. run scoreboard players operation #ns m.boss /= #nn m.boss",
    "scoreboard players operation #ns m.boss /= #20 m.const",
    f"execute as {B} store result score #ad m.boss run attribute @s minecraft:attack_damage base get",
    "scoreboard players operation #ad m.boss += #ns m.boss",
    f"execute store result storage {NS}:boss ad int 1 run scoreboard players get #ad m.boss",
    f"execute as {B} store result score #ar m.boss run attribute @s minecraft:armor base get",
    "scoreboard players operation #ar m.boss += #ns m.boss",
    f"execute store result storage {NS}:boss ar int 1 run scoreboard players get #ar m.boss",
    f"execute as {B} run function {NS}:boss/renforcer with storage {NS}:boss",
    f"{S} set #fin m.boss 0"])
add_lines(F + "refonte/load.mcfunction", [f"{S} set #20 m.const 20"])
w(F + "boss/renforcer.mcfunction", "$attribute @s minecraft:attack_damage base set $(ad)\n$attribute @s minecraft:armor base set $(ar)")
# phase finale : sous 15 % des PV, régénération par à-coups et attaques deux fois plus fréquentes
add_lines(F + "boss/encours.mcfunction", [
    "scoreboard players operation #s15 m.boss = #max m.boss", "scoreboard players operation #s15 m.boss *= #3 m.const",
    "scoreboard players operation #s15 m.boss /= #20 m.const",
    f"execute if score #fin m.boss matches 0 if score #hp m.boss matches 1.. if score #hp m.boss <= #s15 m.boss as {B} at @s run function {NS}:boss/phase_finale",
    "execute if score #fin m.boss matches 1 run scoreboard players add #atk m.boss 1"])
w(F + "boss/phase_finale.mcfunction", "\n".join([
    f"{S} set #fin m.boss 1", "effect give @s minecraft:regeneration 20 1 true", "effect give @s minecraft:resistance 10 0 true",
    "particle minecraft:explosion_emitter ~ ~1 ~ 0 0 0 0 1", "execute as @a at @s run playsound minecraft:entity.wither.ambient master @s ~ ~ ~ 1 0.5",
    'tellraw @a ' + PREFIX + ',{"text":"Dernier souffle : le boss se régénère et frappe deux fois plus vite !","color":"dark_red","bold":true}]']))
PLS = "gamemode=!spectator,gamemode=!creative"
NEW_ATK = {
    1: ("onde_choc", ["particle minecraft:sweep_attack ~ ~1 ~ 5 0.3 5 0 40", "playsound minecraft:entity.iron_golem.attack hostile @a ~ ~ ~ 2 0.5",
                      f"execute as @a[distance=..10,{PLS}] run damage @s 6 minecraft:mob_attack by @e[tag=metiers.boss,limit=1]",
                      f"execute as @a[distance=..10,{PLS}] at @s facing entity @e[tag=metiers.boss,limit=1] feet rotated ~180 0 positioned ^ ^0.5 ^3 if block ~ ~ ~ #{NS}:boss_vide if block ~ ~1 ~ #{NS}:boss_vide run tp @s ~ ~ ~",
                      'tellraw @a ' + PREFIX + ',{"text":"Onde de choc du Colosse !","color":"dark_red"}]']),
    2: ("nid", [f"execute as @a[distance=..14,{PLS}] at @s run summon minecraft:cave_spider ~1 ~ ~ {{Tags:[\"metiers.sbire\"]}}",
                f"effect give @a[distance=..14,{PLS}] minecraft:poison 4 0", "playsound minecraft:entity.spider.ambient hostile @a ~ ~ ~ 2 0.4",
                'tellraw @a ' + PREFIX + ',{"text":"La Reine libère son nid !","color":"dark_green"}]']),
    3: ("gel", [f"execute as @a[distance=..14,{PLS}] run data modify entity @s TicksFrozen set value 300",
                f"effect give @a[distance=..14,{PLS}] minecraft:slowness 5 2", "particle minecraft:snowflake ~ ~2 ~ 6 1 6 0.05 200",
                "playsound minecraft:block.glass.break hostile @a ~ ~ ~ 2 0.5", 'tellraw @a ' + PREFIX + ',{"text":"La Liche gèle le sang de ses ennemis.","color":"aqua"}]']),
    4: ("meteores", [f"execute as @a[distance=..20,{PLS}] at @s run particle minecraft:flame ~ ~6 ~ 0.3 3 0.3 0 80",
                     f"execute as @a[distance=..20,{PLS}] run damage @s 7 minecraft:in_fire", f"effect give @a[distance=..20,{PLS}] minecraft:blindness 1 0",
                     "playsound minecraft:entity.generic.explode hostile @a ~ ~ ~ 2 0.7", 'tellraw @a ' + PREFIX + ',{"text":"Des météores s’écrasent autour du Brasier !","color":"gold"}]']),
    5: ("rejetons", ["summon minecraft:creeper ~2 ~ ~ {Tags:[\"metiers.sbire\"],ExplosionRadius:0b,Fuse:20s}",
                     "summon minecraft:creeper ~-2 ~ ~ {Tags:[\"metiers.sbire\"],ExplosionRadius:0b,Fuse:20s}",
                     "summon minecraft:creeper ~ ~ ~2 {Tags:[\"metiers.sbire\"],ExplosionRadius:0b,Fuse:20s}",
                     "playsound minecraft:entity.creeper.primed hostile @a ~ ~ ~ 2 0.7", 'tellraw @a ' + PREFIX + ',{"text":"Le Creeper géant libère ses rejetons !","color":"green"}]']),
}
for k, (nom, L_) in NEW_ATK.items():
    w(F + f"boss/a_{nom}.mcfunction", "\n".join(L_))
AT2 = ["scoreboard players set #atk m.boss 0"]
for k, b in BOSS.items():
    atks = list(b["atks"]) + [NEW_ATK[k][0]]
    AT2.append(f"execute if score #type m.boss matches {k} store result score #r m.boss run random value 1..{len(atks)}")
    AT2 += [f"execute if score #type m.boss matches {k} if score #r m.boss matches {i} run function {NS}:boss/a_{a}" for i, a in enumerate(atks, 1)]
w(F + "boss/attaque.mcfunction", "\n".join(AT2))

# =====================================================================
# EFFETS VISUELS : montée de niveau et de palier
# =====================================================================
for j in JL:
    add_lines(F + f"{j}/levelup.mcfunction", [
        "particle minecraft:happy_villager ~ ~1 ~ 0.4 0.6 0.4 0 20", "particle minecraft:enchant ~ ~1.5 ~ 0.5 0.5 0.5 1 30",
        f"execute if score @s m.{j}_lvl matches 10 run function {NS}:effet/palier",
        f"execute if score @s m.{j}_lvl matches 20 run function {NS}:effet/palier", f"execute if score @s m.{j}_lvl matches 30 run function {NS}:effet/palier",
        f"execute if score @s m.{j}_lvl matches 40 run function {NS}:effet/palier", f"execute if score @s m.{j}_lvl matches 50 run function {NS}:effet/palier",
        f"execute if score @s m.{j}_lvl matches 60 run function {NS}:effet/palier", f"execute if score @s m.{j}_lvl matches 70 run function {NS}:effet/palier",
        f"execute if score @s m.{j}_lvl matches 80 run function {NS}:effet/palier", f"execute if score @s m.{j}_lvl matches 90 run function {NS}:effet/palier",
        f"execute if score @s m.{j}_lvl matches 100 run function {NS}:effet/palier"])
w(F + "effet/palier.mcfunction", "\n".join([
    'summon minecraft:firework_rocket ~ ~1 ~ {LifeTime:18,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":{flight_duration:1,explosions:[{shape:"burst",colors:[I;5635925,16777045],has_twinkle:true}]}}}}',
    "particle minecraft:totem_of_undying ~ ~1 ~ 0.5 1 0.5 0.4 60"]))

# =====================================================================
# MENU : boutons Quêtes, Guilde, Synergies ; déclencheurs
# =====================================================================
add_lines(F + "trigger.mcfunction", [
    f'execute if score @s m.trig matches 495 run function {NS}:appel {{f:"quete/page"}}',
    f'execute if score @s m.trig matches 496 run function {NS}:appel {{f:"synergie/page"}}',
    f'execute if score @s m.trig matches 770 run function {NS}:appel {{f:"guilde/page"}}',
    f'execute if score @s m.trig matches 771 run function {NS}:appel {{f:"guilde/creer"}}',
    f'execute if score @s m.trig matches 772 run function {NS}:appel {{f:"guilde/quitter"}}',
    f'execute if score @s m.trig matches 773 run function {NS}:appel {{f:"guilde/inviter_liste"}}',
    f'execute if score @s m.trig matches 775 run function {NS}:appel {{f:"guilde/accepter"}}',
    f'execute if score @s m.trig matches 7100000..7199999 run function {NS}:appel {{f:"guilde/inviter"}}',
    f'execute if score @s m.trig matches 7200000..7299999 run function {NS}:appel {{f:"guilde/exclure"}}'])

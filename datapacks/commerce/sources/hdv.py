# -*- coding: utf-8 -*-
# Hôtel des ventes : les joueurs mettent en vente l'objet qu'ils tiennent (n'importe lequel, même spécial),
# au prix qu'ils choisissent ; les autres l'achètent depuis le menu. 5 ventes au plus par joueur, 60 en tout,
# 5 % de taxe prélevés à la vente (l'argent sort de l'économie).
#   storage commerce:hdv L : [{n: numéro, v: id du vendeur, vn: pseudo, p: prix, it: objet complet}]
#   triggers : 6000 + page (6 par page), 6100 mettre en vente, 6200 mes ventes, 9000000 + n acheter, 9500000 + n retirer
S = "scoreboard players"
H_ = F + "hdv/"
HV = f"{NS}:hdv"
HP = f"{NS}:hp"            # page en cours de construction (racine = arguments de macro)
PAR_PAGE = 6

w(H_ + "load.mcfunction", [f"execute unless data storage {HV} L run data modify storage {HV} L set value []", f"{S} add #hdvn c.g 0"])

# ---------------------------------------------------------------- mettre en vente (6100 : dialogue de prix)
w(H_ + "vendre.mcfunction", [
    f'execute unless items entity @s weapon.mainhand * run return run function {NS}:hdv/erreur {{m:"Prends en main l’objet à vendre, puis reviens ici."}}',
    f"execute store result storage {NS}:t o.id int 1 run scoreboard players get @s m.id",
    f"{S} set #nb c.t 0", f"data modify storage {NS}:t W set from storage {HV} L", f"function {NS}:hdv/compter with storage {NS}:t o",
    f'execute if score #nb c.t matches 5.. run return run function {NS}:hdv/erreur {{m:"Tu as déjà 5 objets en vente. Retires-en un avant."}}',
    f"execute store result score #nb c.t run data get storage {HV} L",
    f'execute if score #nb c.t matches 60.. run return run function {NS}:hdv/erreur {{m:"L’hôtel des ventes est plein (60 objets)."}}',
    f"{S} set @s c.pend 2",
    f"data modify storage {NS}:t vit set from entity @s SelectedItem",
    f'data modify storage {NS}:t p set value "$(p)"',
    f"function {NS}:hdv/prix_d with storage {NS}:t"])
w(H_ + "compter.mcfunction", [
    f"execute unless data storage {NS}:t W[0] run return 0",
    f"$execute if data storage {NS}:t W[0]{{v:$(id)}} run scoreboard players add #nb c.t 1",
    f"data remove storage {NS}:t W[0]", f"function {NS}:hdv/compter with storage {NS}:t o"])
w(H_ + "erreur.mcfunction", [f"$data modify storage {NS}:t msg set value \"$(m)\"", "playsound minecraft:entity.villager.no master @s ~ ~ ~ 0.8 1",
                              f"function {NS}:hdv/page_0"])
w(H_ + "prix_d.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Mettre en vente",color:"light_purple",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:item",item:$(vit),description:{width:220,contents:{text:"L’objet que tu tiens en main. Il quitte ton inventaire tant qu’il est en vente ; tu peux le retirer quand tu veux.",color:"gray"}}}],'
  'inputs:[{type:"minecraft:text",key:"p",label:{text:"Prix en Écus"},width:200,max_length:9}],'
  'actions:[{label:{text:"Mettre en vente",color:"light_purple",bold:true},width:150,action:{type:"minecraft:dynamic/run_command",template:"trigger commerce set -$(p)"}},'
  '{label:{text:"Annuler"},width:150,action:{type:"run_command",command:"trigger commerce set 6000"}}],columns:2}')
# prix reçu (trigger négatif, c.pend 2)
w(H_ + "prix.mcfunction", [
    f"{S} set @s c.pend 0",
    "scoreboard players operation #q c.t = #v c.t", "scoreboard players operation #q c.t *= #-1 c.g",
    f'execute unless items entity @s weapon.mainhand * run return run function {NS}:hdv/erreur {{m:"Tu ne tiens plus d’objet en main."}}',
    "scoreboard players add #hdvn c.g 1",
    f"data modify storage {NS}:t e set value {{}}",
    f"execute store result storage {NS}:t e.n int 1 run scoreboard players get #hdvn c.g",
    f"execute store result storage {NS}:t e.v int 1 run scoreboard players get @s m.id",
    f"execute store result storage {NS}:t e.p int 1 run scoreboard players get #q c.t",
    f"function {NS}:joueur/nom_moi", f"data modify storage {NS}:t e.vn set from storage {NS}:t moi",
    f"data modify storage {NS}:t e.it set from entity @s SelectedItem",
    "item replace entity @s weapon.mainhand with minecraft:air",
    f"data modify storage {HV} L append from storage {NS}:t e",
    f'data modify storage {NS}:t msg set value "Objet mis en vente."',
    "playsound minecraft:block.barrel.close master @s ~ ~ ~ 1 1.2",
    f'tellraw @a [{{text:"[Hôtel des ventes] ",color:"light_purple"}},{{selector:"@s",color:"white"}},{{text:" met en vente un objet pour ",color:"gray"}},{{score:{{name:"#q",objective:"c.t"}},color:"gold"}},{{text:" Écus.",color:"gray"}}]',
    f"function {NS}:hdv/page_0"])

# ---------------------------------------------------------------- pages (6 objets, illustration et vendeur, bouton acheter)
w(H_ + "page.mcfunction", [  # #pg = numéro de page
    f"data modify storage {HP} B set value []", f"data modify storage {HP} A set value []",
    f"data modify storage {NS}:t W set from storage {HV} L",
    "scoreboard players operation #skip c.t = #pg c.t", f"scoreboard players set #pp c.t {PAR_PAGE}", "scoreboard players operation #skip c.t *= #pp c.t",
    f"function {NS}:hdv/sauter", f"{S} set #k c.t 0", f"function {NS}:hdv/remplir",
    f"execute store result score #nb c.t run data get storage {HV} L",
    f'execute if score #nb c.t matches 0 run data modify storage {HP} B append value {{type:"minecraft:plain_message",width:300,contents:{{text:"Rien en vente pour l’instant. Prends un objet en main et clique « Mettre en vente ».",color:"gray"}}}}',
    # navigation
    "scoreboard players operation #x c.t = #pg c.t", "scoreboard players remove #x c.t 1", "execute if score #x c.t matches ..-1 run scoreboard players set #x c.t 0",
    "scoreboard players add #x c.t 6000", f"execute store result storage {HP} av int 1 run scoreboard players get #x c.t",
    "scoreboard players operation #x c.t = #pg c.t", "scoreboard players add #x c.t 1",
    "scoreboard players operation #y c.t = #x c.t", "scoreboard players operation #y c.t *= #pp c.t",
    "execute if score #y c.t >= #nb c.t run scoreboard players operation #x c.t = #pg c.t",
    "scoreboard players add #x c.t 6000", f"execute store result storage {HP} ap int 1 run scoreboard players get #x c.t",
    "scoreboard players operation #x c.t = #pg c.t", "scoreboard players add #x c.t 1", f"execute store result storage {HP} np int 1 run scoreboard players get #x c.t",
    "scoreboard players operation #x c.t = #nb c.t", "scoreboard players add #x c.t 5", "scoreboard players operation #x c.t /= #pp c.t",
    "execute if score #x c.t matches ..0 run scoreboard players set #x c.t 1",
    f"execute store result storage {HP} nt int 1 run scoreboard players get #x c.t",
    f"execute store result storage {HP} nb int 1 run scoreboard players get #nb c.t"] + SOLDE(HP) + msg_line(HP) + [
    f"function {NS}:hdv/entete with storage {HP}", f"function {NS}:hdv/nav with storage {HP}",
    f"function {NS}:hdv/page_d with storage {HP}"])
w(H_ + "sauter.mcfunction", ["execute if score #skip c.t matches ..0 run return 0", f"data remove storage {NS}:t W[0]",
                             "scoreboard players remove #skip c.t 1", f"function {NS}:hdv/sauter"])
w(H_ + "remplir.mcfunction", [
    f"execute if score #k c.t matches {PAR_PAGE}.. run return 0", f"execute unless data storage {NS}:t W[0] run return 0",
    f"data modify storage {NS}:t e set from storage {NS}:t W[0]",
    f"execute store result score #x c.t run data get storage {NS}:t e.n", "scoreboard players add #x c.t 9000000",
    f"execute store result storage {NS}:t e.c int 1 run scoreboard players get #x c.t",
    f"function {NS}:hdv/ligne with storage {NS}:t e",
    f"data remove storage {NS}:t W[0]", "scoreboard players add #k c.t 1", f"function {NS}:hdv/remplir"])
w(H_ + "ligne.mcfunction", [
    f'$data modify storage {HP} B append value {{type:"minecraft:item",item:$(it),show_decorations:true,description:{{width:220,contents:[{{text:"Vendu par ",color:"gray"}},{{text:"$(vn)",color:"white"}},{{text:"   $(p) Écus",color:"gold",bold:true}}]}}}}',
    f'$data modify storage {HP} A append value {{label:[{{text:"Acheter  ",color:"yellow",bold:true}},{{text:"$(p) ",color:"white"}},{ECU_C}],width:160,action:{{type:"run_command",command:"trigger commerce set $(c)"}}}}'])
# en-tête, navigation, dialogue : le corps et les boutons sont des listes construites dans le storage
HDR = f'{{type:"minecraft:plain_message",width:320,contents:{L(SOLDE_TXT, T("   ·   page $(np)/$(nt)   ·   $(nb) objets", "gray"), T("\\nSurvole un objet pour ses détails. 5 % de taxe à la vente.", "dark_gray"), T("\\n$(msg)", "yellow"))}}}'
w(H_ + "entete.mcfunction", f"$data modify storage {HP} B prepend value {HDR}")
nav = lambda lab, col, val, larg=160: f'{{label:{T(lab, col, True)},width:{larg},action:{{type:"run_command",command:"trigger commerce set {val}"}}}}'
w(H_ + "nav.mcfunction", [
    f'$data modify storage {HP} A append value {{label:{T("◀  Page précédente", "white")},width:160,action:{{type:"run_command",command:"trigger commerce set $(av)"}}}}',
    f'$data modify storage {HP} A append value {{label:{T("Page suivante  ▶", "white")},width:160,action:{{type:"run_command",command:"trigger commerce set $(ap)"}}}}',
    f"data modify storage {HP} A append value " + nav("Mettre en vente", "light_purple", 6100),
    f"data modify storage {HP} A append value " + nav("Mes ventes", "yellow", 6200),
    f"data modify storage {HP} A append value " + nav("Banque", "gold", 90),
    f"data modify storage {HP} A append value " + nav("Accueil", "white", 1)])
DLG = ('$dialog show @s {type:"minecraft:multi_action",title:' + T("Hôtel des ventes", "light_purple", True) +
       ',can_close_with_escape:true,pause:false,body:$(B),actions:$(A),columns:2}')
w(H_ + "page_d.mcfunction", DLG)
for p in range(10):
    w(H_ + f"page_{p}.mcfunction", [f"{S} set #pg c.t {p}", f"function {NS}:hdv/page"])

# ---------------------------------------------------------------- acheter (9000000 + n)
w(H_ + "acheter.mcfunction", [
    "scoreboard players operation #n c.t = #v c.t", "scoreboard players remove #n c.t 9000000",
    f"execute store result storage {NS}:t o.n int 1 run scoreboard players get #n c.t",
    f"data remove storage {NS}:t e", f"function {NS}:hdv/trouver with storage {NS}:t o",
    f'execute unless data storage {NS}:t e.n run return run function {NS}:hdv/erreur {{m:"Cet objet n’est plus en vente."}}',
    f"execute store result score #q c.t run data get storage {NS}:t e.p",
    f"execute store result score #vid c.t run data get storage {NS}:t e.v",
    f'execute if score #vid c.t = @s m.id run return run function {NS}:hdv/erreur {{m:"C’est ton propre objet : retire-le depuis « Mes ventes »."}}',
    f'execute if score @s c.ecus < #q c.t run return run function {NS}:hdv/erreur {{m:"Pas assez d’Écus."}}',
    "scoreboard players operation @s c.ecus -= #q c.t", "scoreboard players operation @s c.ta += #q c.t",
    # vendeur : prix moins 5 %
    "scoreboard players operation #net c.t = #q c.t", "scoreboard players operation #net c.t *= #95 c.g", "scoreboard players operation #net c.t /= #100 c.g",
    f"execute store result storage {NS}:t e.net int 1 run scoreboard players get #net c.t",
    f"function {NS}:hdv/payer with storage {NS}:t e",
    f"function {NS}:hdv/donner",
    f"function {NS}:hdv/oter with storage {NS}:t o",
    # historique
    f"data modify storage {NS}:t m.nom set from storage {NS}:t e.vn", f"execute store result storage {NS}:t m.v int 1 run scoreboard players get #q c.t",
    f"execute store result storage {NS}:t hl.id int 1 run scoreboard players get @s m.id", f'data modify storage {NS}:t hl.col set value "red"',
    f"function {NS}:banque/hist_txt_hdv_a", f"function {NS}:joueur/nom_moi", f"data modify storage {NS}:t m.nom set from storage {NS}:t moi",
    f"execute store result storage {NS}:t m.v int 1 run scoreboard players get #net c.t",
    f"execute store result storage {NS}:t hl.id int 1 run scoreboard players get #vid c.t", f'data modify storage {NS}:t hl.col set value "green"',
    f"function {NS}:banque/hist_txt_hdv_v",
    f'data modify storage {NS}:t msg set value "Acheté ! L’objet est à tes pieds ou dans ton inventaire."',
    "playsound minecraft:entity.villager.trade master @s ~ ~ ~ 1 1", f"function {NS}:hdv/page_0"])
w(H_ + "trouver.mcfunction", f"$data modify storage {NS}:t e set from storage {HV} L[{{n:$(n)}}]")
w(H_ + "oter.mcfunction", f"$data remove storage {HV} L[{{n:$(n)}}]")
w(H_ + "payer.mcfunction", [
    "$scoreboard players add $(vn) c.ecus $(net)",
    '$tellraw @a[name=$(vn)] [{text:"[Hôtel des ventes] ",color:"light_purple"},{selector:"@s",color:"white"},{text:" a acheté ton objet : +$(net) Écus.",color:"green"}]'])
# l'objet apparaît sur le joueur (ramassé tout de suite, ou au sol si l'inventaire est plein)
w(H_ + "donner.mcfunction", [
    'summon minecraft:item ~ ~0.3 ~ {Item:{id:"minecraft:stone",count:1},PickupDelay:0s,Tags:["commerce.hdvg"]}',
    f"data modify entity @e[type=minecraft:item,tag=commerce.hdvg,limit=1,sort=nearest] Item set from storage {NS}:t e.it",
    "tag @e[type=minecraft:item,tag=commerce.hdvg] remove commerce.hdvg"])

# ---------------------------------------------------------------- mes ventes (6200) et retrait (9500000 + n)
w(H_ + "mes.mcfunction", [
    f"data modify storage {HP} B set value []", f"data modify storage {HP} A set value []",
    f"execute store result storage {NS}:t o.id int 1 run scoreboard players get @s m.id",
    f"data modify storage {NS}:t W set from storage {HV} L", f"function {NS}:hdv/mes_boucle with storage {NS}:t o",
    f'execute unless data storage {HP} B[0] run data modify storage {HP} B append value {{type:"minecraft:plain_message",width:300,contents:{{text:"Tu n’as rien en vente.",color:"gray"}}}}',
    f"data modify storage {HP} A append value " + nav("Hôtel des ventes", "light_purple", 6000),
    f"data modify storage {HP} A append value " + nav("Accueil", "white", 1),
    f"function {NS}:hdv/page_d with storage {HP}"])
w(H_ + "mes_boucle.mcfunction", [
    f"execute unless data storage {NS}:t W[0] run return 0",
    f"$execute if data storage {NS}:t W[0]{{v:$(id)}} run function {NS}:hdv/mes_ligne",
    f"data remove storage {NS}:t W[0]", f"function {NS}:hdv/mes_boucle with storage {NS}:t o"])
w(H_ + "mes_ligne.mcfunction", [
    f"data modify storage {NS}:t e set from storage {NS}:t W[0]",
    f"execute store result score #x c.t run data get storage {NS}:t e.n", "scoreboard players add #x c.t 9500000",
    f"execute store result storage {NS}:t e.c int 1 run scoreboard players get #x c.t",
    f"function {NS}:hdv/mes_ligne_m with storage {NS}:t e"])
w(H_ + "mes_ligne_m.mcfunction", [
    f'$data modify storage {HP} B append value {{type:"minecraft:item",item:$(it),description:{{width:220,contents:[{{text:"En vente pour ",color:"gray"}},{{text:"$(p) Écus",color:"gold",bold:true}}]}}}}',
    f'$data modify storage {HP} A append value {{label:{{text:"Retirer ($(p) Écus)",color:"red"}},width:160,action:{{type:"run_command",command:"trigger commerce set $(c)"}}}}'])
w(H_ + "retirer.mcfunction", [
    "scoreboard players operation #n c.t = #v c.t", "scoreboard players remove #n c.t 9500000",
    f"execute store result storage {NS}:t o.n int 1 run scoreboard players get #n c.t",
    f"data remove storage {NS}:t e", f"function {NS}:hdv/trouver with storage {NS}:t o",
    f'execute unless data storage {NS}:t e.n run return run function {NS}:hdv/erreur {{m:"Cet objet n’est plus en vente."}}',
    f"execute store result score #vid c.t run data get storage {NS}:t e.v",
    f'execute unless score #vid c.t = @s m.id run return run function {NS}:hdv/erreur {{m:"Ce n’est pas ton objet."}}',
    f"function {NS}:hdv/donner", f"function {NS}:hdv/oter with storage {NS}:t o",
    f'data modify storage {NS}:t msg set value "Objet retiré de la vente."', f"function {NS}:hdv/mes"])

# -*- coding: utf-8 -*-
# Magasins de joueurs : un panneau « [Vente] » posé sur un coffre, un coffre piégé ou un tonneau en fait un magasin.
# Le coffre devient privé (comme [Privé]) ; son propriétaire choisit le prix à l'unité dans un dialogue.
# Le panneau est réécrit : un clic droit dessus achète 1 objet, celui de la première case non vide du coffre.
# Le prix est sur le marqueur du panneau (c.shp), le magasin est le groupe de protection (c.grp).
S = "scoreboard players"
B_ = F + "boutique/"

w(B_ + "load.mcfunction", ["scoreboard objectives add c.shp dummy"])

# création : exécuté comme le joueur, à la position du panneau, juste après la protection (prive/panneau)
w(B_ + "creer.mcfunction", [
    "tag @e[type=minecraft:marker,tag=commerce.prive_s,distance=..0.9,limit=1,sort=nearest] add commerce.shop",
    f"{S} set @e[type=minecraft:marker,tag=commerce.prive_s,distance=..0.9,limit=1,sort=nearest] c.shp 0",
    "scoreboard players operation @s c.shid = #gid c.g", f"{S} set @s c.pend 3",
    f"function {NS}:boutique/prix_d"])
w(B_ + "prix_d.mcfunction",
  'dialog show @s {type:"minecraft:multi_action",title:{text:"Ton magasin",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:plain_message",width:300,contents:[{text:"Prix en Écus pour UN objet. Les clients achètent, un clic à la fois, l’objet de la première case non vide du coffre. Toi seul ouvres le coffre pour le remplir.\\n",color:"gray"},'
  '{text:"Pour changer le prix plus tard : casse le panneau et repose-le.",color:"dark_gray"}]}],'
  'inputs:[{type:"minecraft:text",key:"p",label:{text:"Prix à l’unité"},width:200,max_length:9}],'
  'actions:[{label:{text:"Ouvrir le magasin",color:"gold",bold:true},width:200,action:{type:"minecraft:dynamic/run_command",template:"trigger commerce set -$(p)"}}],columns:1}')
# prix reçu (trigger négatif, c.pend 3) : on règle le panneau de ce magasin
w(B_ + "prix.mcfunction", [
    f"{S} set @s c.pend 0",
    "scoreboard players operation #q c.t = #v c.t", "scoreboard players operation #q c.t *= #-1 c.g",
    "scoreboard players operation #sid c.t = @s c.shid", "scoreboard players operation #pid c.t = @s m.id",
    f"{S} set #fait c.t 0",
    f"execute as @e[type=minecraft:marker,tag=commerce.shop] if score @s c.grp = #sid c.t if score @s c.own = #pid c.t at @s run function {NS}:boutique/regler",
    f"execute if score #fait c.t matches 0 run return run " + say("Magasin introuvable : repose le panneau [Vente].", "red"),
    say("Magasin ouvert ! Les clients font un clic droit sur le panneau pour acheter.", "green")])
w(B_ + "regler.mcfunction", [
    "scoreboard players operation @s c.shp = #q c.t", f"{S} set #fait c.t 1",
    f"execute store result storage {NS}:t sh.p int 1 run scoreboard players get #q c.t",
    "scoreboard players operation #x c.t = #sid c.t", "scoreboard players add #x c.t 7500000",
    f"execute store result storage {NS}:t sh.c int 1 run scoreboard players get #x c.t",
    f"function {NS}:joueur/nom_moi", f"data modify storage {NS}:t sh.nom set from storage {NS}:t moi",
    f"function {NS}:boutique/texte with storage {NS}:t sh",
    f"function {NS}:prive/photo_panneau"])
CLIC = ',click_event:{action:"run_command",command:"trigger commerce set $(c)"}'
w(B_ + "texte.mcfunction",
  '$data merge block ~ ~ ~ {is_waxed:1b,front_text:{messages:['
  f'{{text:"[Vente]",color:"gold",bold:true{CLIC}}},'
  '{text:"$(p) Écus l’unité",color:"dark_green"},'
  '{text:"Clic : acheter 1",color:"dark_gray"},'
  '{text:"$(nom)",color:"black"}]}}')

# achat (7500000 + magasin) : exécuté comme le client
w(B_ + "acheter.mcfunction", [
    "scoreboard players operation #sid c.t = #v c.t", "scoreboard players remove #sid c.t 7500000",
    f"{S} set #trouve c.t 0", "tag @s add commerce.client",
    f"execute as @e[type=minecraft:marker,tag=commerce.shop,distance=..8] if score @s c.grp = #sid c.t run function {NS}:boutique/lire",
    "tag @s remove commerce.client",
    "execute if score #trouve c.t matches 0 run return run " + say("Approche-toi du magasin.", "red"),
    "execute if score #shp c.t matches ..0 run return run " + say("Ce magasin n’a pas encore de prix.", "red"),
    "execute if score #own c.t = @s m.id run return run " + say("C’est ton magasin.", "gray"),
    "execute if score @s c.ecus < #shp c.t run return run " + say("Pas assez d’Écus.", "red"),
    # 27/11/2026 : le nom du vendeur est lu AVANT de prendre l'objet et de débiter le client. Sans nom dans le registre,
    # « scoreboard players add  c.ecus » échouait : le client payait, le vendeur ne recevait rien (Écus perdus).
    f"execute store result storage {NS}:t o.id int 1 run scoreboard players get #own c.t",
    f'data modify storage {NS}:t o.nom set value ""', f"function {NS}:banque/nom_t with storage {NS}:t o",
    f'execute if data storage {NS}:t o{{nom:""}} run return run ' + say("Le propriétaire de ce magasin est introuvable : achat annulé, rien n’est débité.", "red"),
    # un conteneur du magasin avec au moins un objet
    f"data remove storage {NS}:t sh", f"{S} set #ok c.t 0",
    f"execute as @e[type=minecraft:marker,tag=commerce.prive_c,distance=..10] if score @s c.grp = #sid c.t at @s if score #ok c.t matches 0 if data block ~ ~ ~ Items[0] run function {NS}:boutique/prendre",
    "execute if score #ok c.t matches 0 run return run " + say("Ce magasin est vide.", "red"),
    "scoreboard players operation @s c.ecus -= #shp c.t", "scoreboard players operation @s c.ta += #shp c.t",
    f"execute store result storage {NS}:t sh.p int 1 run scoreboard players get #shp c.t",
    f"data modify storage {NS}:t sh.nom set from storage {NS}:t o.nom",
    f"function {NS}:boutique/payer with storage {NS}:t sh",
    'summon minecraft:item ~ ~0.3 ~ {Item:{id:"minecraft:stone",count:1},PickupDelay:0s,Tags:["commerce.hdvg"]}',
    f"data modify entity @e[type=minecraft:item,tag=commerce.hdvg,limit=1,sort=nearest] Item set from storage {NS}:t sh.it",
    "tag @e[type=minecraft:item,tag=commerce.hdvg] remove commerce.hdvg",
    # historique des deux côtés
    f"data modify storage {NS}:t m.nom set from storage {NS}:t o.nom", f"execute store result storage {NS}:t m.v int 1 run scoreboard players get #shp c.t",
    f"execute store result storage {NS}:t hl.id int 1 run scoreboard players get @s m.id", f'data modify storage {NS}:t hl.col set value "red"',
    f"function {NS}:banque/hist_txt_shop_a",
    f"function {NS}:joueur/nom_moi", f"data modify storage {NS}:t m.nom set from storage {NS}:t moi",
    f"execute store result storage {NS}:t hl.id int 1 run scoreboard players get #own c.t", f'data modify storage {NS}:t hl.col set value "green"',
    f"function {NS}:banque/hist_txt_shop_v",
    "playsound minecraft:entity.villager.trade master @s ~ ~ ~ 1 1"])
w(B_ + "lire.mcfunction", [f"{S} set #trouve c.t 1", "scoreboard players operation #shp c.t = @s c.shp", "scoreboard players operation #own c.t = @s c.own"])
# on prend 1 objet de la première case non vide (le marqueur du conteneur exécute, à sa position)
w(B_ + "prendre.mcfunction", [
    f"{S} set #ok c.t 1",
    f"data modify storage {NS}:t sh.it set from block ~ ~ ~ Items[0]",
    f"data remove storage {NS}:t sh.it.Slot", f"data modify storage {NS}:t sh.it.count set value 1",
    f"execute store result storage {NS}:t sh.s int 1 run data get block ~ ~ ~ Items[0].Slot",
    f"function {NS}:boutique/retirer_un with storage {NS}:t sh",
    f"function {NS}:prive/photo"])
w(B_ + "retirer_un.mcfunction",
  '$item modify block ~ ~ ~ container.$(s) {function:"minecraft:set_count",type:"minecraft:set_count",count:-1,add:true}')
w(B_ + "payer.mcfunction", [
    "$scoreboard players add $(nom) c.ecus $(p)",
    '$tellraw @a[name=$(nom)] [{text:"[Magasin] ",color:"gold"},{selector:"@s",color:"white"},{text:" t’achète un objet : +$(p) Écus.",color:"green"}]'])

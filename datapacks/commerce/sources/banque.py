# -*- coding: utf-8 -*-
# Banque : virements entre joueurs, historique des opérations, épargne avec intérêts.
# Exécuté par datapack.py (partage w, wj, F, NS, T, L, btn, btn_cmd, dlg, say, SOLDE, SOLDE_TXT, msg_line, ECU, BAN...).
#
# Saisie de montants : les dialogues ont un champ texte et un bouton « trigger commerce set -<montant> ».
# Une valeur négative du trigger est un montant ; le score c.pend dit à quoi il sert (1 virement, 2 prix d'une vente
# à l'hôtel des ventes, 3 prix d'un magasin). Les joueurs n'ont pas le droit de lancer une fonction : tout passe
# par le trigger.
S = "scoreboard players"
B_ = F + "banque/"
BQ = f"{NS}:bq"

w(B_ + "load.mcfunction", [f"scoreboard objectives add {o} dummy" for o in ("c.ep", "c.pend", "c.dest", "c.shid")])

# ---------------------------------------------------------------- historique (storage commerce:h p<id> : 15 lignes)
# ajouter : storage commerce:t hl = {id, txt, col}
w(B_ + "hist.mcfunction", [
    f'$data modify storage {NS}:h p$(id) prepend value {{text:"$(txt)\\n",color:"$(col)"}}',
    f"$execute if data storage {NS}:h p$(id)[15] run data remove storage {NS}:h p$(id)[15]"])
HIST = lambda id_cmd, txt, col: [f"execute store result storage {NS}:t hl.id int 1 run {id_cmd}",
                                  f'data modify storage {NS}:t hl.col set value "{col}"', f"function {NS}:banque/hist_txt_{txt}"]

# textes d'historique (macros sur storage commerce:t m / it)
TXTS = {
    "vente": "$(q) × $(n) vendus : +$(e),$(z)$(c) Écus",
    "achat": "$(q) × $(n) achetés : -$(e),$(z)$(c) Écus",
    "vir_env": "Virement à $(nom) : -$(v) Écus",
    "vir_rec": "Virement de $(nom) : +$(v) Écus",
    "dep": "Épargne : $(v) Écus déposés",
    "ret": "Épargne : $(v) Écus retirés",
    "hdv_v": "Hôtel des ventes, vendu à $(nom) : +$(v) Écus",
    "hdv_a": "Hôtel des ventes, acheté à $(nom) : -$(v) Écus",
    "shop_v": "Magasin, vente à $(nom) : +$(v) Écus",
    "shop_a": "Magasin de $(nom), achat : -$(v) Écus",
    "int": "Intérêts de l’épargne : +$(v) Écus",
}
for k, t in TXTS.items():
    w(B_ + f"hist_txt_{k}.mcfunction", [f"data modify storage {NS}:t hl.src set from storage {NS}:t m", f"function {NS}:banque/hist_txt_{k}_m with storage {NS}:t hl.src"])
    w(B_ + f"hist_txt_{k}_m.mcfunction", [f'$data modify storage {NS}:t hl.txt set value "{t}"', f"function {NS}:banque/hist with storage {NS}:t hl"])

# ---------------------------------------------------------------- page banque (90)
PG = SOLDE(BQ) + [f"execute store result storage {BQ} ep int 1 run scoreboard players get @s c.ep",
                  f"execute store result storage {BQ} o.id int 1 run scoreboard players get @s m.id",
                  f'data modify storage {BQ} hl set value [{{text:"Aucune opération pour l’instant.",color:"dark_gray"}}]',
                  f"function {NS}:banque/hist_lire with storage {BQ} o"] + msg_line(BQ) + [f"function {NS}:banque/page_d with storage {BQ}"]
w(B_ + "page.mcfunction", PG)
w(B_ + "hist_lire.mcfunction", f"$execute if data storage {NS}:h p$(id)[0] run data modify storage {BQ} hl set from storage {NS}:h p$(id)")
_IC = lambda p: f'{{object:"atlas",atlas:"minecraft:{"blocks" if p.startswith("block/") else "items"}",sprite:"minecraft:{p}"}}'
w(B_ + "page_d.mcfunction", "$" + dlg(
    T("Banque", "gold", True),
    [f'{{type:"minecraft:plain_message",width:320,contents:{L(SOLDE_TXT, T("   ·   épargne : ", "gray"), T("$(ep) " + ECU, "aqua", True), T("\\nL’épargne rapporte 2 % par semaine de jeu (5 000 " + ECU + " au plus). Elle est à l’abri des achats.", "gray"), T("\\n$(msg)", "yellow"))}}}',
     f'{{type:"minecraft:plain_message",width:320,contents:[{{text:"Dernières opérations\\n",color:"gold",bold:true}},{{text:"",extra:$(hl)}}]}}'],
    [btn(L(_IC("item/paper"), T("  Virement", "yellow", True)), 91, 130, "Envoyer des Écus à un autre joueur."),
     btn(L(_IC("item/emerald"), T("  Hôtel des ventes", "light_purple")), 6000, 130),
     btn(L(_IC("item/compass_00"), T("  Accueil", "white")), 1, 130),
     btn(L(_IC("item/gold_nugget"), T("  Déposer 100", "aqua")), 940, 130), btn(L(_IC("item/gold_ingot"), T("  Déposer 1 000", "aqua")), 941, 130),
     btn(L(_IC("block/gold_block"), T("  Déposer 10 000", "aqua")), 942, 130),
     btn(L(_IC("item/gold_nugget"), T("  Retirer 100", "white")), 950, 130), btn(L(_IC("item/gold_ingot"), T("  Retirer 1 000", "white")), 951, 130),
     btn(L(_IC("block/gold_block"), T("  Retirer 10 000", "white")), 952, 130),
     btn(T("Tout déposer", "aqua", True), 943, 130), btn(T("Tout retirer", "white", True), 953, 130)], 3))

# dépôts et retraits
for i, (q, lib) in enumerate(((100, "100"), (1000, "1 000"), (10000, "10 000"), (None, "tout"))):
    D = [f"{S} set #q c.t {q}" if q else "scoreboard players operation #q c.t = @s c.ecus",
         "execute if score #q c.t matches ..0 run return run " + f'data modify storage {NS}:t msg set value "Rien à déposer."',
         f'execute if score @s c.ecus < #q c.t run return run data modify storage {NS}:t msg set value "Pas assez d\'Écus sur ton compte."',
         "scoreboard players operation @s c.ecus -= #q c.t", "scoreboard players operation @s c.ep += #q c.t",
         f"execute store result storage {NS}:t m.v int 1 run scoreboard players get #q c.t"] + HIST("scoreboard players get @s m.id", "dep", "aqua") + [
         f'data modify storage {NS}:t msg set value "Déposé sur ton épargne."', "playsound minecraft:block.chain.place master @s ~ ~ ~ 0.8 1.4"]
    w(B_ + f"depot_{i}.mcfunction", D)
    R_ = [f"{S} set #q c.t {q}" if q else "scoreboard players operation #q c.t = @s c.ep",
          "execute if score #q c.t matches ..0 run return run " + f'data modify storage {NS}:t msg set value "Ton épargne est vide."',
          f'execute if score @s c.ep < #q c.t run return run data modify storage {NS}:t msg set value "Pas assez sur ton épargne."',
          "scoreboard players operation @s c.ep -= #q c.t", "scoreboard players operation @s c.ecus += #q c.t",
          f"execute store result storage {NS}:t m.v int 1 run scoreboard players get #q c.t"] + HIST("scoreboard players get @s m.id", "ret", "white") + [
          f'data modify storage {NS}:t msg set value "Retiré de ton épargne."', "playsound minecraft:block.chain.break master @s ~ ~ ~ 0.8 1.4"]
    w(B_ + f"retrait_{i}.mcfunction", R_)
# intérêts : 2 % par semaine, 5 000 au plus, pour tous les joueurs du registre (même hors ligne)
w(B_ + "interets.mcfunction", [f"data modify storage {NS}:t W set from storage {NS}:j l", f"function {NS}:banque/interets_boucle"])
w(B_ + "interets_boucle.mcfunction", [f"execute unless data storage {NS}:t W[0] run return 0",
                                      f"function {NS}:banque/interets_m with storage {NS}:t W[0]",
                                      f"data remove storage {NS}:t W[0]", f"function {NS}:banque/interets_boucle"])
w(B_ + "interets_m.mcfunction", [
    f"{S} set #x c.t 0", "$execute store result score #x c.t run scoreboard players get $(nom) c.ep",
    "scoreboard players operation #x c.t /= #50 c.g",
    # Métiers 26 : compétence Banquier du Marchand, +1 % par semaine
    f"{S} set #z c.t 0", "$execute if score $(nom) m.tbq matches 1 store result score #z c.t run scoreboard players get $(nom) c.ep",
    "scoreboard players operation #z c.t /= #100 c.g", "scoreboard players operation #x c.t += #z c.t",
    # guilde niveau 2 ou 3 : 3 % ; niveau 4 ou 5 : 4 % et plafond 10 000
    f"{S} set #gn c.t 0", "$execute store result score #gn c.t run scoreboard players get $(nom) c.gn",
    f"{S} operation #y c.t = #x c.t", f"{S} set #2 c.t 2",
    "execute if score #gn c.t matches 2..3 run scoreboard players operation #y c.t /= #2 c.t",
    "execute if score #gn c.t matches 2..3 run scoreboard players operation #x c.t += #y c.t",
    "execute if score #gn c.t matches 4.. run scoreboard players operation #x c.t *= #2 c.t",
    "execute if score #gn c.t matches ..3 if score #x c.t matches 5001.. run scoreboard players set #x c.t 5000",
    "execute if score #gn c.t matches 4.. if score #x c.t matches 10001.. run scoreboard players set #x c.t 10000",
    "execute if score #x c.t matches ..0 run return 0",
    "$scoreboard players operation $(nom) c.ep += #x c.t",
    f"execute store result storage {NS}:t m.v int 1 run scoreboard players get #x c.t",
    f"$data modify storage {NS}:t hl.id set value $(id)", f'data modify storage {NS}:t hl.col set value "aqua"', f"function {NS}:banque/hist_txt_int"])

# ---------------------------------------------------------------- virement (91 : choix du destinataire, 81xxxxx : destinataire, montant négatif)
w(B_ + "destinataires.mcfunction", [
    f'data modify storage {BQ} D set value [{{text:""}}]', f"data modify storage {NS}:t W set from storage {NS}:j l",
    f"function {NS}:banque/dest_boucle", f"function {NS}:banque/dest_d with storage {BQ}"])
w(B_ + "dest_boucle.mcfunction", [f"execute unless data storage {NS}:t W[0] run return 0",
                                  # valeur du clic calculée (8100000 + id) : « 81 » collé devant l'id donnait 815 pour l'id 5
                                  "scoreboard players set #dv c.t 8100000", f"execute store result score #di c.t run data get storage {NS}:t W[0].id",
                                  "scoreboard players operation #dv c.t += #di c.t",
                                  f"execute store result storage {NS}:t W[0].v int 1 run scoreboard players get #dv c.t",
                                  f"function {NS}:banque/dest_m with storage {NS}:t W[0]",
                                  f"data remove storage {NS}:t W[0]", f"function {NS}:banque/dest_boucle"])
w(B_ + "dest_m.mcfunction", [
    "$execute if score @s m.id matches $(id) run return 0",
    f'$data modify storage {BQ} D append value {{text:"$(nom)",color:"yellow",underlined:true,click_event:{{action:"run_command",command:"trigger commerce set $(v)"}},hover_event:{{action:"show_text",value:"Envoyer des Écus à $(nom)"}}}}',
    f'data modify storage {BQ} D append value {{text:"     "}}'])
w(B_ + "dest_d.mcfunction", "$" + dlg(
    T("Envoyer des Écus", "gold", True),
    [f'{{type:"minecraft:plain_message",width:320,contents:[{{text:"Clique sur le joueur à qui envoyer :\\n\\n",color:"gray"}},{{text:"",extra:$(D)}}]}}'],
    [btn(T("Banque", "white"), 90, 160)], 1))
# 81 + id : le destinataire est choisi, on demande le montant
w(B_ + "dest_choisi.mcfunction", [
    "scoreboard players operation @s c.dest = #v c.t", "scoreboard players remove @s c.dest 8100000",
    f"{S} set @s c.pend 1",
    f"execute store result storage {BQ} o.id int 1 run scoreboard players get @s c.dest",
    f'data modify storage {BQ} o.nom set value "?"', f"function {NS}:banque/nom_de with storage {BQ} o",
    # le modèle du bouton garde « $(m) » : le dialogue le remplace par la saisie (la macro de fonction le recopie tel quel)
    f'data modify storage {BQ} o.m set value "$(m)"',
    f"function {NS}:banque/montant_d with storage {BQ} o"])
w(B_ + "nom_de.mcfunction", f"$data modify storage {BQ} o.nom set from storage {NS}:j l[{{id:$(id)}}].nom")
w(B_ + "montant_d.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Virement à $(nom)",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:plain_message",width:300,contents:{text:"Montant en Écus (nombre entier) :",color:"gray"}}],'
  'inputs:[{type:"minecraft:text",key:"m",label:{text:"Montant"},width:200,max_length:9}],'
  'actions:[{label:{text:"Envoyer",color:"yellow",bold:true},width:150,action:{type:"minecraft:dynamic/run_command",template:"trigger commerce set -$(m)"}},'
  '{label:{text:"Annuler"},width:150,action:{type:"run_command",command:"trigger commerce set 90"}}],columns:2}')
w(B_ + "virer.mcfunction", [
    "scoreboard players operation #q c.t = #v c.t", "scoreboard players operation #q c.t *= #-1 c.g",
    f"{S} set @s c.pend 0",
    f'execute if score @s c.ecus < #q c.t run return run data modify storage {NS}:t msg set value "Pas assez d\'Écus pour ce virement."',
    f"execute store result storage {NS}:t o.id int 1 run scoreboard players get @s c.dest",
    f'data modify storage {NS}:t o.nom set value ""', f"function {NS}:banque/nom_t with storage {NS}:t o",
    f'execute if data storage {NS}:t o{{nom:""}} run return run data modify storage {NS}:t msg set value "Joueur introuvable."',
    "scoreboard players operation @s c.ecus -= #q c.t",
    f"execute store result storage {NS}:t o.q int 1 run scoreboard players get #q c.t",
    f"function {NS}:banque/virer_m with storage {NS}:t o",
    # historique des deux côtés
    f"data modify storage {NS}:t m.nom set from storage {NS}:t o.nom",
    f"execute store result storage {NS}:t m.v int 1 run scoreboard players get #q c.t"] + HIST("scoreboard players get @s m.id", "vir_env", "red") + [
    f"function {NS}:joueur/nom_moi",
    f"data modify storage {NS}:t m.nom set from storage {NS}:t moi"] + HIST("scoreboard players get @s c.dest", "vir_rec", "green") + [
    f'data modify storage {NS}:t msg set value "Virement envoyé."', "playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 1"])
w(B_ + "nom_t.mcfunction", f"$data modify storage {NS}:t o.nom set from storage {NS}:j l[{{id:$(id)}}].nom")
w(B_ + "virer_m.mcfunction", [
    "$scoreboard players add $(nom) c.ecus $(q)",
    f'$tellraw @a[name=$(nom)] [{{text:"[Commerce] ",color:"gold"}},{{selector:"@s",color:"white"}},{{text:" t’envoie $(q) Écus.",color:"green"}}]'])
# nom du joueur exécutant, lu dans le registre : storage commerce:t moi
w(F + "joueur/nom_moi.mcfunction", [f'data modify storage {NS}:t moi set value "?"', f"execute store result storage {NS}:t o2.id int 1 run scoreboard players get @s m.id",
                                     f"function {NS}:joueur/nom_moi_m with storage {NS}:t o2"])
w(F + "joueur/nom_moi_m.mcfunction", f"$data modify storage {NS}:t moi set from storage {NS}:j l[{{id:$(id)}}].nom")

# ---------------------------------------------------------------- saisie d'un montant (trigger négatif)
w(F + "saisie/entree.mcfunction", [
    f"execute if score @s c.pend matches 1 run return run function {NS}:saisie/virer",
    f"execute if score @s c.pend matches 2 run return run function {NS}:hdv/prix",
    f"execute if score @s c.pend matches 3 run return run function {NS}:boutique/prix",
    say("Ce montant ne correspond à rien en cours.", "red")])
w(F + "saisie/virer.mcfunction", [f"function {NS}:banque/virer", f"function {NS}:banque/page"])
for i in range(4):
    w(B_ + f"op_depot_{i}.mcfunction", [f"function {NS}:banque/depot_{i}", f"function {NS}:banque/page"])
    w(B_ + f"op_retrait_{i}.mcfunction", [f"function {NS}:banque/retrait_{i}", f"function {NS}:banque/page"])

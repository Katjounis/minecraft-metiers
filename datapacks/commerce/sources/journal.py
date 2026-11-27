# -*- coding: utf-8 -*-
# Journal des Écus (27/11/2026) : plus aucun gain ni perte d'Écus sans explication.
# Exécuté par datapack.py après banque.py (partage w, F, NS, S, HIST...).
#
# Chaque pack double ses opérations sur c.ecus par la même sur son compteur annoncé (voir
# metiers/sources/journal_ecus.py). Chaque seconde, pour chaque joueur connecté :
#   variation = c.ecus - c.ecv (solde vu la seconde précédente)
#   chaque compteur annoncé non nul est retiré de la variation ; ceux des autres packs écrivent une ligne
#   d'historique avec le nom du pack (au-delà de 50 Écus, pour ne pas noyer l'historique sous les petits gains) ;
#   ce qui reste est un mouvement non enregistré : ligne d'historique, message au joueur, trace pour les admins.
S = "scoreboard players"
J_ = F + "journal/"
# compteur, libellé dans l'historique (None : déjà écrit par Commerce ou par le pack lui-même)
CATS = [("com", None), ("met", "Métiers"), ("cmp", "Compagnons"), ("bos", "Boss"), ("hor", "Horreur"), ("ind", None)]
OBJS = ["c.ecv"] + [f"c.a_{k}" for k, _ in CATS]

w(J_ + "load.mcfunction", [f"scoreboard objectives add {o} dummy" for o in OBJS] + [
    f"execute unless data storage {NS}:journal anomalies run data modify storage {NS}:journal anomalies set value []"])
w(J_ + "init.mcfunction", [f"{S} operation @s c.ecv = @s c.ecus"] + [f"{S} set @s c.a_{k} 0" for k, _ in CATS])

JJ = [f"execute unless score @s c.ecv matches -2147483648.. run return run function {NS}:journal/init",
      f"execute unless score @s c.ecus matches -2147483648.. run return 0",
      f"{S} operation #jd c.t = @s c.ecus", f"{S} operation #jd c.t -= @s c.ecv"]
for k, lib in CATS:
    JJ += [f"{S} add @s c.a_{k} 0", f"execute unless score @s c.a_{k} matches 0 run function {NS}:journal/cat_{k}"]
    C = [f"{S} operation #jd c.t -= @s c.a_{k}"]
    if lib:
        C += [f"{S} operation #jv c.t = @s c.a_{k}",
              f"execute if score #jv c.t matches -49..49 run return run {S} set @s c.a_{k} 0",
              f'data modify storage {NS}:t m.l set value "{lib}"', f"function {NS}:journal/ligne"]
    C += [f"{S} set @s c.a_{k} 0"]
    w(J_ + f"cat_{k}.mcfunction", C)
JJ += [f"execute unless score #jd c.t matches 0 run function {NS}:journal/inexplique",
       f"{S} operation @s c.ecv = @s c.ecus"]
w(J_ + "joueur.mcfunction", JJ)

# ligne d'historique « <pack> : +N Écus » (montant dans #jv)
w(J_ + "ligne.mcfunction", [
    f"execute store result storage {NS}:t m.v int 1 run {S} get #jv c.t",
    f'data modify storage {NS}:t m.s set value ""', f'execute if score #jv c.t matches 1.. run data modify storage {NS}:t m.s set value "+"',
    f'data modify storage {NS}:t hl.col set value "green"', f'execute if score #jv c.t matches ..-1 run data modify storage {NS}:t hl.col set value "red"',
    f"execute store result storage {NS}:t hl.id int 1 run {S} get @s m.id",
    f"data modify storage {NS}:t hl.src set from storage {NS}:t m", f"function {NS}:journal/ligne_m with storage {NS}:t hl.src"])
w(J_ + "ligne_m.mcfunction", [f'$data modify storage {NS}:t hl.txt set value "$(l) : $(s)$(v) Écus"', f"function {NS}:banque/hist with storage {NS}:t hl"])

# mouvement que personne n'a annoncé : historique, message, trace des 50 derniers pour les admins
w(J_ + "inexplique.mcfunction", [
    f"{S} operation #jv c.t = #jd c.t",
    f'data modify storage {NS}:t m.l set value "Mouvement non enregistré"', f"function {NS}:journal/ligne",
    f"execute store result storage {NS}:t ja.v int 1 run {S} get #jd c.t",
    f"execute store result storage {NS}:t ja.s int 1 run {S} get @s c.ecus",
    f"execute store result storage {NS}:t ja.t int 1 run time query gametime",
    f"function {NS}:joueur/nom_moi", f"data modify storage {NS}:t ja.nom set from storage {NS}:t moi",
    f"data modify storage {NS}:journal anomalies prepend from storage {NS}:t ja",
    f"execute if data storage {NS}:journal anomalies[50] run data remove storage {NS}:journal anomalies[50]",
    f"function {NS}:journal/msg with storage {NS}:t m"])
w(J_ + "msg.mcfunction",
  '$tellraw @s [{"text":"[Commerce] ","color":"gold"},{"text":"Ton solde a bougé de $(s)$(v) Écus sans opération enregistrée. '
  'C\'est noté dans ton historique (Banque) et transmis aux admins.","color":"yellow"}]')

# admins : /function commerce:admin/journal affiche les 10 derniers mouvements non enregistrés
w(F + "admin/journal.mcfunction", [
    say("Derniers mouvements d'Écus non enregistrés (joueur, montant, solde après, heure de jeu) :", "gold"),
    f"data modify storage {NS}:t W set from storage {NS}:journal anomalies",
    f"{S} set #jn c.t 0", f"function {NS}:admin/journal_boucle"])
w(F + "admin/journal_boucle.mcfunction", [
    f"execute unless data storage {NS}:t W[0] run return 0",
    f"execute if score #jn c.t matches 10.. run return 0",
    f"function {NS}:admin/journal_m with storage {NS}:t W[0]",
    f"data remove storage {NS}:t W[0]", f"{S} add #jn c.t 1", f"function {NS}:admin/journal_boucle"])
w(F + "admin/journal_m.mcfunction",
  '$tellraw @s [{"text":" · $(nom) ","color":"white"},{"text":"$(v) Écus","color":"yellow"},{"text":"  solde $(s)  tick $(t)","color":"gray"}]')

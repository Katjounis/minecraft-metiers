# -*- coding: utf-8 -*-
# 25.8 (24/11/2026) : récompenses de palier relevées (voir CRIST, ECL_PAL, ECUS_PAL et EXTRAS dans datapack.py).
# Rattrapage unique (tag metiers.v258, après le recalcul 25.7) : pour chaque palier déjà récupéré, le joueur reçoit
# la différence de cristaux, d'éclats et d'Écus entre l'ancien et le nouveau barème. Les objets bonus ne sont pas
# rattrapés (ils arrivent aux prochains paliers).
RP = ["tag @s add metiers.v258"]
for j in jobs:
    for k in range(1, 11):
        dc = CRIST[k] - CRIST_25_6[k]
        de = ECL_PAL.get(k, 0) - ECL_25_6.get(k, 0)
        du = ECUS_PAL.get(k, 0) - ECUS_25_6.get(k, 0)
        c = f"execute if score @s m.{j}_pal matches {k}.."
        if dc > 0: RP.append(f"{c} run scoreboard players add @s m.cr_{j} {dc}")
        if de > 0: RP.append(f"{c} run scoreboard players add @s m.ecl {de}")
        if du > 0: RP.append(f"{c} if score @s c.ecus matches -2147483648.. run scoreboard players add @s c.ecus {du}")
RP += ['tellraw @s [{"text":"[Métiers] ","color":"gold"},{"text":"Mise à jour 25.8 : récompenses de palier relevées (plus de cristaux, des éclats dès le palier 40, des Écus à chaque palier et des objets bonus). Tu reçois la différence pour les paliers déjà récupérés.","color":"yellow"}]',
       "playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1.2"]
w(F + "paliers/rattrapage.mcfunction", "\n".join(RP))
add_lines(F + "joueur.mcfunction", [f"execute if entity @s[tag=metiers.v257] unless entity @s[tag=metiers.v258] run function {NS}:paliers/rattrapage"])
w(F + "version.mcfunction", 'tellraw @s {"text":"[Métiers] Version 27.0 : arbres à 18 compétences, objets de métier, capacités de la Forge sur les outils","color":"gold"}')


# 26/11/2026 : remise à zéro de toutes les compétences de tous les joueurs, une seule fois (tag metiers.rz2611).
# Les points reviennent d'eux-mêmes (recalculés d'après les compétences acquises).
RZ = ["tag @s add metiers.rz2611"]
for j in jobs:
    for k in range(1, NB_SK[j] + 1):
        RZ += [f"tag @s remove metiers.sk.{j}{k}", f"tag @s remove metiers.skoff.{j}{k}"]
    RZ += [f"advancement revoke @s only {NS}:{j}/competence_{k}" for k in range(1, NB_SK[j] + 1)]
RZ += [f"function {NS}:objets/retirer_elytres", "tag @s remove metiers.grimpe",
       'tellraw @s [{"text":"[Métiers] ","color":"gold"},{"text":"Remise à zéro des compétences : tous tes points te sont rendus, reconstruis tes arbres comme tu veux (touche G).","color":"yellow"}]',
       "playsound minecraft:block.beacon.activate master @s ~ ~ ~ 1 1.2"]
w(F + "paliers/rz_competences.mcfunction", "\n".join(RZ))
add_lines(F + "joueur.mcfunction", [f"execute unless entity @s[tag=metiers.rz2611] run function {NS}:paliers/rz_competences"])

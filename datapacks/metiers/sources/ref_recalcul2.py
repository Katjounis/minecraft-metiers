# -*- coding: utf-8 -*-
# 25.8 (26/11/2026) : courbe d'XP allégée (Q&A avec Samuel : niveau 50 en ~12 h au lieu de ~20, même forme,
# prestige baissé pareil). Besoin par niveau : max(90 x 1,06^(niveau-1), 9 000 x étoiles), soit 0,6 x l'ancien.
# Recalcul unique de chaque joueur : l'XP déjà gagnée dans l'étoile en cours (sur l'ancienne courbe 150 / 15 000)
# est rejouée sur la nouvelle, donc chacun monte d'un coup. Les étoiles ne changent pas (le prestige reste un choix
# du joueur), le niveau est plafonné à 100. Les récompenses de palier des niveaux gagnés sont à récupérer comme
# d'habitude (rétroactives), les points de compétence suivent le niveau. Exécuté après ref_recalcul.py (25.7).
_ANC = lambda L, p: max(round(150 * 1.06 ** (L - 1)), 15000 * p)
_NOU = lambda L, p: max(round(90 * 1.06 ** (L - 1)), 9000 * p)


def _cum(f):
    C = {p: [0, 0] for p in range(6)}
    for p in range(6):
        for L in range(2, 101):
            C[p].append(C[p][L - 1] + f(L - 1, p))
    return C


CA, CN = _cum(_ANC), _cum(_NOU)
for p in range(6):
    w(F + f"recalcul2/ancien_{p}.mcfunction", "\n".join(
        f"execute if score #L m.tmp matches {L} run return run scoreboard players set #T m.tmp {CA[p][L]}" for L in range(1, 101)))
    w(F + f"recalcul2/table_{p}.mcfunction", "\n".join(
        [f"execute if score #T m.tmp matches {CN[p][L]}.. run return run function {NS}:recalcul/poser {{l:{L},c:{CN[p][L]}}}"
         for L in range(100, 1, -1)] + [f"function {NS}:recalcul/poser {{l:1,c:0}}"]))

S_ = "scoreboard players"
RC2 = ["tag @s add metiers.c258"]
for j, d in jobs.items():
    R = [f"{S_} add @s m.{j}_lvl 0", f"{S_} add @s m.{j}_xp 0", f"{S_} add @s m.{j}_pr 0",
         f"execute unless score @s m.{j}_lvl matches 1.. run {S_} set @s m.{j}_lvl 1",
         f"execute if score @s m.{j}_pr matches 6.. run return 0",
         f"{S_} operation #ancien m.tmp = @s m.{j}_lvl", f"{S_} operation #L m.tmp = @s m.{j}_lvl"]
    R += [f"execute if score @s m.{j}_pr matches {p} run function {NS}:recalcul2/ancien_{p}" for p in range(6)]
    R += [f"execute if score @s m.{j}_lvl matches ..99 if score @s m.{j}_xp matches 1.. run {S_} operation #T m.tmp += @s m.{j}_xp"]
    R += [f"execute if score @s m.{j}_pr matches {p} run function {NS}:recalcul2/table_{p}" for p in range(6)]
    R += [f"{S_} operation @s m.{j}_lvl = #L m.tmp",
          f"{S_} operation #T m.tmp -= #C m.tmp", f"{S_} operation @s m.{j}_xp = #T m.tmp",
          f"execute if score @s m.{j}_lvl matches 100.. run {S_} set @s m.{j}_xp 0",
          f"function {NS}:{j}/points", f"function {NS}:{j}/check",
          f"execute unless score #ancien m.tmp = @s m.{j}_lvl run function {NS}:recalcul/dire_{j}"]
    w(F + f"recalcul2/{j}.mcfunction", "\n".join(R))
RC2 += [f"function {NS}:recalcul2/{j}" for j in jobs]
RC2 += ["function metiers:prestige/tags", f"function {NS}:classement/maj",
        'tellraw @s [{"text":"[Métiers] ","color":"gold"},{"text":"Mise à jour 25.8 : monter de niveau coûte 40 % d’XP en moins (prestige compris). Toute l’XP déjà gagnée a été recomptée sur la nouvelle courbe. Les récompenses des paliers atteints t’attendent dans le menu (G).","color":"yellow"}]',
        "playsound minecraft:block.beacon.power_select master @s ~ ~ ~ 1 1.2"]
w(F + "recalcul2/joueur.mcfunction", "\n".join(RC2))
add_lines(F + "joueur.mcfunction", [f"execute unless entity @s[tag=metiers.c258] run function {NS}:recalcul2/joueur"])
w(F + "version.mcfunction", 'tellraw @s {"text":"[Métiers] Version 25.8 : courbe d’XP allégée (90 XP au niveau 1, +6 % par niveau), prestige à 9 000 XP par niveau et par étoile","color":"gold"}')

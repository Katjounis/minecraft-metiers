# -*- coding: utf-8 -*-
# 25.7 (24/11/2026) : recalcul unique de chaque joueur sur la nouvelle courbe d'XP (demande de Samuel : « tout
# recalculer » et « tout ramener au niveau »). Exécuté à la fin de datapack.py.
#
# 1. XP totale gagnée dans le métier, avec l'ANCIENNE formule (besoin = 40 + 10 x (niveau + 100 x étoiles)) :
#    T = 40n + 5n(n+1) + 1000.p.n + xp + 53 460.p + 49 500.p(p-1)    (n = niveau - 1, p = étoiles)
# 2. Cette XP est rejouée sur la NOUVELLE courbe (besoin = max(150 x 1,06^(niveau-1), 15 000 x étoiles)) : étoiles
#    entières d'abord (un cycle complet coûte K[p]), puis le niveau dans le cycle, le reste devient l'XP en cours.
# 3. Tout est ramené au nouveau niveau : compétences au-dessus du niveau retirées (points rendus), outil et palier
#    de récompenses redescendus au palier du niveau, capacités de prestige recalculées, Armure des Guildes remise au
#    nouveau score total. Les cristaux et objets déjà reçus restent acquis.
f6 = lambda L: round(150 * 1.06 ** (L - 1))
BES = lambda L, p: max(f6(L), 15000 * p)
CUM = {p: [0, 0] for p in range(6)}            # CUM[p][L] : XP pour aller du niveau 1 au niveau L dans le cycle p
for p in range(6):
    for L in range(2, 101):
        CUM[p].append(CUM[p][L - 1] + BES(L - 1, p))
K = {p: CUM[p][100] for p in range(6)}        # cycle complet (niveau 1 -> 100)

for p in range(6):
    w(F + f"recalcul/table_{p}.mcfunction", "\n".join(
        [f"execute if score #T m.tmp matches {CUM[p][L]}.. run return run function {NS}:recalcul/poser {{l:{L},c:{CUM[p][L]}}}"
         for L in range(100, 1, -1)] + [f"function {NS}:recalcul/poser {{l:1,c:0}}"]))
w(F + "recalcul/poser.mcfunction", "$scoreboard players set #L m.tmp $(l)\n$scoreboard players set #C m.tmp $(c)")

S_ = "scoreboard players"
RC = ["tag @s add metiers.v257"]
for j, d in jobs.items():
    R = [f"{S_} add @s m.{j}_lvl 0", f"{S_} add @s m.{j}_xp 0", f"{S_} add @s m.{j}_pr 0",
         f"execute unless score @s m.{j}_lvl matches 1.. run {S_} set @s m.{j}_lvl 1",
         # 1. ancienne XP totale
         f"{S_} operation #n m.tmp = @s m.{j}_lvl", f"{S_} remove #n m.tmp 1",
         f"{S_} set #k m.tmp 40", f"{S_} operation #T m.tmp = #n m.tmp", f"{S_} operation #T m.tmp *= #k m.tmp",
         f"{S_} operation #a m.tmp = #n m.tmp", f"{S_} add #a m.tmp 1", f"{S_} operation #a m.tmp *= #n m.tmp",
         f"{S_} set #k m.tmp 5", f"{S_} operation #a m.tmp *= #k m.tmp", f"{S_} operation #T m.tmp += #a m.tmp",
         f"{S_} operation #a m.tmp = @s m.{j}_pr", f"{S_} set #k m.tmp 1000", f"{S_} operation #a m.tmp *= #k m.tmp",
         f"{S_} operation #a m.tmp *= #n m.tmp", f"{S_} operation #T m.tmp += #a m.tmp",
         f"execute if score @s m.{j}_xp matches 1.. run {S_} operation #T m.tmp += @s m.{j}_xp",
         f"{S_} operation #a m.tmp = @s m.{j}_pr", f"{S_} set #k m.tmp 53460", f"{S_} operation #a m.tmp *= #k m.tmp",
         f"{S_} operation #T m.tmp += #a m.tmp",
         f"{S_} operation #a m.tmp = @s m.{j}_pr", f"{S_} remove #a m.tmp 1", f"{S_} operation #a m.tmp *= @s m.{j}_pr",
         f"{S_} set #k m.tmp 49500", f"{S_} operation #a m.tmp *= #k m.tmp", f"{S_} operation #T m.tmp += #a m.tmp",
         f"{S_} operation #ancien m.tmp = @s m.{j}_lvl",
         # 2. rejoué sur la nouvelle courbe
         f"{S_} set #P m.tmp 0"]
    # étoiles entières : un cycle à la fois (le drapeau #ok évite d'enchaîner deux tests sur la même valeur)
    for p in range(5):
        R += [f"{S_} set #ok m.tmp 0",
              f"execute if score #P m.tmp matches {p} if score #T m.tmp matches {K[p]}.. run {S_} set #ok m.tmp 1",
              f"execute if score #ok m.tmp matches 1 run {S_} remove #T m.tmp {K[p]}",
              f"execute if score #ok m.tmp matches 1 run {S_} add #P m.tmp 1"]
    R += [f"execute if score #P m.tmp matches {p} run function {NS}:recalcul/table_{p}" for p in range(6)]
    R += [f"{S_} operation @s m.{j}_pr = #P m.tmp", f"{S_} operation @s m.{j}_lvl = #L m.tmp",
          f"{S_} operation #T m.tmp -= #C m.tmp", f"{S_} operation @s m.{j}_xp = #T m.tmp",
          f"execute if score @s m.{j}_lvl matches 100.. run {S_} set @s m.{j}_xp 0"]
    # 3. compétences au-dessus du niveau (sans étoile) retirées, points recomptés
    for k in range(1, 7):
        R += [f"execute if score @s m.{j}_pr matches 0 unless score @s m.{j}_lvl matches {SKILL_LVL[k - 1]}.. run tag @s remove metiers.sk.{j}{k}",
              f"execute if score @s m.{j}_pr matches 0 unless score @s m.{j}_lvl matches {SKILL_LVL[k - 1]}.. run advancement revoke @s only {NS}:{j}/competence_{k}"]
    R.append(f"{S_} set @s m.{j}_spent 0")
    R += [f"execute if entity @s[tag=metiers.sk.{j}{k}] run {S_} add @s m.{j}_spent {SKILLS[j][k - 1][1]}" for k in range(1, 7)]
    R += [f"function {NS}:{j}/points",
          f"execute if score @s m.tmp matches ..-1 run function {NS}:recalcul/vider_{j}"]
    # outil et palier de récompenses ramenés au palier du niveau (avec une étoile, l'outil garde son palier)
    R += [f"{S_} operation #pl m.tmp = @s m.{j}_lvl", f"{S_} operation #pl m.tmp /= #10 m.const",
          f"execute if score @s m.{j}_pr matches 0 run {S_} operation @s m.{j}_out < #pl m.tmp",
          f"{S_} operation @s m.{j}_pal < #pl m.tmp",
          f"execute if score @s m.{j}_out matches 1.. if items entity @s container.* {SEL(j)} run function {NS}:{j}/outil_donner",
          f"execute if score @s m.{j}_out matches ..0 run clear @s {SEL(j)}",
          f"function {NS}:{j}/check",
          f"execute unless score #ancien m.tmp = @s m.{j}_lvl run function {NS}:recalcul/dire_{j}"]
    w(F + f"recalcul/{j}.mcfunction", "\n".join(R))
    w(F + f"recalcul/vider_{j}.mcfunction", "\n".join(
        [f"tag @s remove metiers.sk.{j}{k}" for k in range(1, 7)] + [f"advancement revoke @s from {NS}:{j}/competence_1",
                                                                      f"{S_} set @s m.{j}_spent 0"]))
    w(F + f"recalcul/dire_{j}.mcfunction",
      f'tellraw @s [{{"text":"[Métiers] ","color":"gold"}},{{"text":"{d["name"]} : niveau ","color":"{d["color"]}"}},'
      f'{{"score":{{"name":"#ancien","objective":"m.tmp"}},"color":"gray"}},{{"text":" → ","color":"gray"}},'
      f'{{"score":{{"name":"@s","objective":"m.{j}_lvl"}},"color":"yellow","bold":true}},'
      f'{{"text":"  (étoiles : ","color":"gray"}},{{"score":{{"name":"@s","objective":"m.{j}_pr"}},"color":"gold"}},{{"text":")","color":"gray"}}]')
RC += [f"function {NS}:recalcul/{j}" for j in jobs]
RC += ["function metiers:prestige/tags",
       # Armure des Guildes : reprise puis redonnée au palier du nouveau score total
       *[f"execute if items entity @s enderchest.{i} *[minecraft:custom_data~{{metiers_armure:1b}}] run item replace entity @s enderchest.{i} with minecraft:air" for i in range(27)],
       "scoreboard players set @s m.arm 0", "tag @s add metiers.avait_armure", f"function {NS}:classement/maj",
       "execute if score @s m.arm matches 0 run clear @s *[minecraft:custom_data~{metiers_armure:1b}]",
       'tellraw @s [{"text":"[Métiers] ","color":"gold"},{"text":"Mise à jour 25.7 : tes niveaux ont été recalculés sur la nouvelle courbe d’XP à partir de toute l’XP déjà gagnée. Compétences, outils, récompenses de palier et Armure des Guildes suivent ton nouveau niveau.","color":"yellow"}]',
       "playsound minecraft:block.beacon.power_select master @s ~ ~ ~ 1 0.8"]
w(F + "recalcul/joueur.mcfunction", "\n".join(RC))
add_lines(F + "joueur.mcfunction", [f"execute unless entity @s[tag=metiers.v257] run function {NS}:recalcul/joueur"])
w(F + "version.mcfunction", 'tellraw @s {"text":"[Métiers] Version 25.7 : niveaux recalculés sur la courbe exponentielle (+6 % par niveau), prestige à 15 000 XP par niveau et par étoile","color":"gold"}')

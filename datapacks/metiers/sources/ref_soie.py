# -*- coding: utf-8 -*-
# Toucher de soie (26/11/2026) : en vanilla, un minerai cassé en Toucher de soie ne lâche pas d'orbes d'XP.
# Le serveur les rend : chaque minerai miné avec une pioche en Toucher de soie donne l'XP moyenne du vanilla
# (charbon 1, lapis, redstone et quartz 3, diamant et émeraude 5, or du Nether 1 ; fer, cuivre et or : 0 comme en vanilla).
# Anti-triche : poser un de ces minerais retire autant d'XP (solde m.sxp, dette limitée à 200 points).
# Objectifs séparés de ceux du métier (s.m.mi.*), donc l'XP de Mineur n'est pas touchée.
SOIE_XP = {"coal_ore": 1, "deepslate_coal_ore": 1, "lapis_ore": 3, "deepslate_lapis_ore": 3,
           "redstone_ore": 3, "deepslate_redstone_ore": 3, "nether_quartz_ore": 3, "nether_gold_ore": 1,
           "diamond_ore": 5, "deepslate_diamond_ore": 5, "emerald_ore": 5, "deepslate_emerald_ore": 5}
LDS = ["scoreboard objectives add m.sxp dummy"]
TK = ["scoreboard players add @s m.sxp 0",
      "execute if items entity @s weapon.mainhand *[minecraft:enchantments~[{enchantments:\"minecraft:silk_touch\"}]] run tag @s add metiers.soie"]
for i, (o, x) in enumerate(SOIE_XP.items()):
    LDS += [f"scoreboard objectives add s.sx{i} minecraft.mined:minecraft.{o}", f"scoreboard objectives add s.su{i} minecraft.used:minecraft.{o}"]
    TK += [f"execute if entity @s[tag=metiers.soie] if score @s s.sx{i} matches 1.. run scoreboard players operation @s m.tmp = @s s.sx{i}",
           f"execute if entity @s[tag=metiers.soie] if score @s s.sx{i} matches 1.. run scoreboard players operation @s m.tmp *= #{x} m.const" if x > 1 else "",
           f"execute if entity @s[tag=metiers.soie] if score @s s.sx{i} matches 1.. run scoreboard players operation @s m.sxp += @s m.tmp",
           f"execute if score @s s.su{i} matches 1.. run scoreboard players operation @s m.tmp = @s s.su{i}",
           f"execute if score @s s.su{i} matches 1.. run scoreboard players operation @s m.tmp *= #{x} m.const" if x > 1 else "",
           f"execute if score @s s.su{i} matches 1.. run scoreboard players operation @s m.sxp -= @s m.tmp",
           f"scoreboard players set @s s.sx{i} 0", f"scoreboard players set @s s.su{i} 0"]
TK += ["tag @s remove metiers.soie",
       "execute if score @s m.sxp matches ..-201 run scoreboard players set @s m.sxp -200",
       "execute unless score @s m.sxp matches 1.. run return 0",
       f"execute store result storage {NS}:tmp sxp int 1 run scoreboard players get @s m.sxp",
       "scoreboard players set @s m.sxp 0",
       f"function {NS}:m/soie_xp_m with storage {NS}:tmp"]
w(F + "m/soie_xp.mcfunction", "\n".join(l for l in TK if l))
w(F + "m/soie_xp_m.mcfunction", "$xp add @s $(sxp) points")
add_lines(F + "load.mcfunction", LDS)
add_lines(F + "loop.mcfunction", [f"execute as @a[gamemode=!spectator] run function {NS}:m/soie_xp"])

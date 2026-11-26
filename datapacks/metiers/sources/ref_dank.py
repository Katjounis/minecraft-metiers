# -*- coding: utf-8 -*-
# Dank Null du Marchand (26/11/2026) : branchement des fonctions t/dank/* (écrites avec l'outil dans datapack.py).
# Toutes les 10 ticks, chaque joueur qui porte son Dank Null détruit les objets qui correspondent à ses filtres.
add_lines(F + "load.mcfunction", ["scoreboard objectives add m.dkav dummy"])
add_lines(F + "loop.mcfunction", [f"execute as @a[gamemode=!spectator] at @s run function {NS}:t/dank/tick"])

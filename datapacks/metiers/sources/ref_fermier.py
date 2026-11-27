# -*- coding: utf-8 -*-
# 26/11/2026 : nouvelles sources d'XP du Fermier (« vraiment léger, dur à augmenter »).
#  - labourer (houe sur terre) : 0,5 XP ; composter un objet : 0,5 XP ; 30 points par minute au plus pour les deux ;
#  - poudre d'os qui fait pousser une culture : 1 XP (elle se consomme, pas de plafond) ;
#  - poudre d'os ramassée en sortie de composteur : 3 XP (critère de statistique dans datapack.py).
# Le progrès « objet utilisé sur un bloc » est vérifié APRÈS l'action : la terre labourée est déjà de la terre labourée.
CULTURES_OS = ["minecraft:wheat", "minecraft:carrots", "minecraft:potatoes", "minecraft:beetroots", "minecraft:melon_stem",
               "minecraft:pumpkin_stem", "minecraft:attached_melon_stem", "minecraft:attached_pumpkin_stem",
               "minecraft:sweet_berry_bush", "minecraft:cocoa", "minecraft:torchflower_crop", "minecraft:pitcher_crop"]


def _adv_bloc(nom, blocs, outil):
    termes = [{"type": "minecraft:location_check", "predicate": {"block": {"blocks": blocs}}}]
    if outil:
        termes.append({"type": "minecraft:match_tool", "predicate": {"items": outil}})
    wj(f"data/{NS}/advancement/f/{nom}.json", {
        "criteria": {"c": {"trigger": "minecraft:item_used_on_block",
                           "conditions": {"location": {"type": "minecraft:all_of", "terms": termes}}}},
        "rewards": {"function": f"{NS}:f/{nom}"}})


_adv_bloc("laboure", ["minecraft:farmland", "minecraft:dirt"], "#minecraft:hoes")
_adv_bloc("os", CULTURES_OS, "minecraft:bone_meal")
_adv_bloc("compost", ["minecraft:composter"], None)
add_lines(F + "refonte/load.mcfunction", ["scoreboard objectives add m.fcap dummy", f"schedule function {NS}:f/minute 60s replace"])
w(F + "f/minute.mcfunction", "\n".join(["scoreboard players reset * m.fcap", f"schedule function {NS}:f/minute 60s replace"]))
for nom in ("laboure", "compost"):
    w(F + f"f/{nom}.mcfunction", "\n".join([
        f"advancement revoke @s only {NS}:f/{nom}",
        "scoreboard players add @s m.fcap 0",
        "execute if score @s m.fcap matches ..19 run scoreboard players add @s m.f_raw 1",
        "execute if score @s m.fcap matches ..19 run scoreboard players add @s m.fcap 1"]))
# 27/11/2026 : poudre d'os sur culture à 0,5 XP et dans le même plafond (20 points, soit 10 XP par minute en tout)
w(F + "f/os.mcfunction", "\n".join([f"advancement revoke @s only {NS}:f/os", "scoreboard players add @s m.fcap 0",
    "execute if score @s m.fcap matches ..19 run scoreboard players add @s m.f_raw 1",
    "execute if score @s m.fcap matches ..19 run scoreboard players add @s m.fcap 1"]))

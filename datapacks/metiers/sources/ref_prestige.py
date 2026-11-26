# -*- coding: utf-8 -*-
# Prestige 24.2 : on garde ses compétences, la courbe d'XP continue (dans datapack.py), récompenses à chaque étoile,
# une capacité de prestige par métier (1, 3 et 5 étoiles), outil étoilé, aura, annonce, cadre Étoilé.
mille = lambda n: f"{n:,}".replace(",", " ")
# Paliers de capacité : tags metiers.sk.p<métier>1 / 3 / 5, tenus à jour toutes les 0,5 s.

add_lines(F + "refonte/load.mcfunction", [
    "scoreboard objectives add m.cd_7 dummy", "scoreboard objectives add m.fk dummy",
    "scoreboard objectives add m.dmgx minecraft.custom:minecraft.damage_dealt",
    "scoreboard players set #99 m.const 99"])

# ---------------------------------------------------------------- paliers de capacité
PT = []
for j in JL:
    for n in (1, 3, 5):
        PT += [f"execute if score @s m.{j}_pr matches {n}.. run tag @s add metiers.sk.p{j}{n}",
               f"execute unless score @s m.{j}_pr matches {n}.. run tag @s remove metiers.sk.p{j}{n}"]
w(F + "prestige/tags.mcfunction", "\n".join(PT))

# ---------------------------------------------------------------- effets permanents (Explorateur, Marchand) et aura
EF = [f"function {NS}:prestige/tags",
      "execute if entity @s[tag=metiers.sk.px5] run effect give @s minecraft:speed infinite 1 true",
      "execute if entity @s[tag=metiers.sk.px1,tag=!metiers.sk.px5] run effect give @s minecraft:speed infinite 0 true",
      "execute if entity @s[tag=metiers.sk.px3] run attribute @s minecraft:fall_damage_multiplier base set 0",
      "execute if entity @s[tag=metiers.sk.pt5] run effect give @s minecraft:hero_of_the_village infinite 4 true",
      "execute if entity @s[tag=metiers.sk.pt3,tag=!metiers.sk.pt5] run effect give @s minecraft:hero_of_the_village infinite 2 true",
      "execute if entity @s[tag=metiers.sk.pt1,tag=!metiers.sk.pt3] run effect give @s minecraft:hero_of_the_village infinite 0 true",
      "execute if entity @s[tag=metiers.sk.pf5,gamemode=!spectator] run function metiers:f/moisson_3",
      "execute if entity @s[tag=metiers.sk.pf3,tag=!metiers.sk.pf5,gamemode=!spectator] run function metiers:f/moisson_2",
      "execute if entity @s[tag=metiers.sk.pf1,tag=!metiers.sk.pf3,gamemode=!spectator] run function metiers:f/moisson_1",
      "execute unless entity @s[tag=metiers.aura_off] unless entity @s[gamemode=spectator] run function metiers:prestige/aura"]
add_lines(F + "refonte/joueur.mcfunction", EF)
AU = ["scoreboard players set #ap m.tmp 0"] + [f"scoreboard players operation #ap m.tmp > @s m.{j}_pr" for j in JL] + [
      "execute if score #ap m.tmp matches 1.. run particle minecraft:end_rod ~ ~1 ~ 0.4 0.6 0.4 0.01 2",
      "execute if score #ap m.tmp matches 3.. run particle minecraft:enchant ~ ~1.2 ~ 0.4 0.5 0.4 0.5 6",
      "execute if score #ap m.tmp matches 5.. run particle minecraft:dust{color:[1.0,0.82,0.2],scale:1.0} ~ ~0.2 ~ 0.45 0.05 0.45 0 6"]
w(F + "prestige/aura.mcfunction", "\n".join(AU))
w(F + "prestige/aura_basculer.mcfunction", "\n".join([
    f"execute if entity @s[tag=metiers.aura_off] run return run function {NS}:prestige/aura_on",
    "tag @s add metiers.aura_off", tr("Aura de prestige coupée. Le même bouton la remet.", "gold"), f"function {NS}:menu"]))
w(F + "prestige/aura_on.mcfunction", "\n".join([
    "tag @s remove metiers.aura_off", tr("Aura de prestige active (si tu as au moins une étoile).", "green"), f"function {NS}:menu"]))

# ---------------------------------------------------------------- passage d'une étoile : récompenses, outil étoilé, annonce
for j, d in jobs.items():
    sel = SEL(j)
    G = [f"function {NS}:prestige/tags"]
    for n in range(1, 6):
        G += [f"execute if score @s m.{j}_pr matches {n} run scoreboard players add @s m.cr_{j} {100 * n}",
              f"execute if score @s m.{j}_pr matches {n} run scoreboard players add @s m.ecl {2 * n}",
              f"execute if score @s m.{j}_pr matches {n} run scoreboard players add @s c.ecus {5000 * n}",
              f'execute if score @s m.{j}_pr matches {n} run tellraw @s {PREFIX},{{"text":"Récompense de l’étoile {n} : {100 * n} cristaux de {d["name"]}, {2 * n} éclats de boss, {mille(5000 * n)} Écus.","color":"gold"}}]']
    G += [f"execute if items entity @s container.* {sel} run function {NS}:{j}/outil_donner",
          f"execute unless items entity @s container.* {sel} if items entity @s weapon.offhand {sel} run function {NS}:{j}/outil_donner",
          'summon minecraft:firework_rocket ~ ~1 ~ {LifeTime:22,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":{flight_duration:1,explosions:[{shape:"star",colors:[I;16766720,16777215],fade_colors:[I;16753920],has_twinkle:true,has_trail:true},{shape:"large_ball",colors:[I;16766720],has_trail:true}]}}}}',
          f'tellraw @a [{{"text":"✦ ","color":"gold","bold":true}},{{"selector":"@s","color":"white","bold":true}},{{"text":" débloque la capacité de prestige ","color":"gray","bold":false}},{{"text":"{PCAP[j][0]}","color":"gold","bold":true}},{{"text":" en {d["name"]} ✦","color":"gray","bold":false}}]']
    w(F + f"prestige/gain_{j}.mcfunction", "\n".join(G))
    # outil : étoiles dorées devant le nom et reflet dès 1 étoile ; Pêcheur : Appât du palier + prestige (5 au plus)
    OPX = [f'data modify storage {NS}:tmp et set value ""', f'data modify storage {NS}:tmp gl set value "false"']
    for n in range(1, 6):
        OPX += [f'execute if score @s m.{j}_pr matches {n} run data modify storage {NS}:tmp et set value "{"★" * n} "',
                f'execute if score @s m.{j}_pr matches {n} run data modify storage {NS}:tmp gl set value "true"']
    if j == "p":
        OPX.append("scoreboard players set #lu m.tmp 1")
        for k in range(11):
            OPX.append(f"execute if score @s m.p_out matches {k} run scoreboard players set #lu m.tmp {tool_ench('p', k)['lure']}")
        OPX += ["execute if score @s m.p_pr matches 1.. run scoreboard players add #lu m.tmp 1",
                "execute if score @s m.p_pr matches 3.. run scoreboard players add #lu m.tmp 1",
                "execute if score #lu m.tmp matches 6.. run scoreboard players set #lu m.tmp 5",
                f"execute store result storage {NS}:tmp lure int 1 run scoreboard players get #lu m.tmp"]
    add_lines(F + f"{j}/outil_params.mcfunction", OPX)

# ---------------------------------------------------------------- Mineur : Filon
FAM = {}
for o in ORES:
    FAM.setdefault(o.replace("deepslate_", "").replace("_ore", ""), []).append(o)
FAMS = list(FAM)
for f_, lst in FAM.items():
    wj(f"data/{NS}/tags/block/filon_{f_}.json", {"values": [f"minecraft:{o}" for o in lst]})
VOIS = [(dx, dy, dz) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1) if (dx, dy, dz) != (0, 0, 0)]
for code, f_ in enumerate(FAMS, 1):
    w(F + f"m/filon_{f_}_voisins.mcfunction", "\n".join(
        f"execute if score #fn m.tmp < #fmax m.tmp positioned ~{dx} ~{dy} ~{dz} if block ~ ~ ~ #{NS}:filon_{f_} run function {NS}:m/filon_{f_}_bloc"
        for dx, dy, dz in VOIS))
    w(F + f"m/filon_{f_}_bloc.mcfunction", "\n".join(
        ["scoreboard players add #fn m.tmp 1"] +
        [f"execute if block ~ ~ ~ minecraft:{o} run scoreboard players add @s m.m_raw {ORES[o]}" for o in FAM[f_]] +
        ["loot give @s mine ~ ~ ~ mainhand", "setblock ~ ~ ~ minecraft:air",
         "particle minecraft:block{block_state:\"minecraft:stone\"} ~ ~ ~ 0.3 0.3 0.3 0 4",
         f"function {NS}:m/filon_{f_}_voisins"]))
w(F + "m/filon_depart.mcfunction", "\n".join(
    ["scoreboard players set #fn m.tmp 0", "scoreboard players set #fmax m.tmp 8",
     "execute if entity @s[tag=metiers.sk.pm3] run scoreboard players set #fmax m.tmp 16",
     "execute if entity @s[tag=metiers.sk.pm5] run scoreboard players set #fmax m.tmp 32"] +
    [f"execute if score #fgo m.tmp matches {c} run function {NS}:m/filon_{f_}_voisins" for c, f_ in enumerate(FAMS, 1)] +
    ["execute if score #fn m.tmp matches 1.. run playsound minecraft:block.deepslate.break master @s ~ ~ ~ 1 0.7"]))
MK = "@e[type=minecraft:marker,tag=metiers.fvise]"
w(F + "m/filon_tick.mcfunction", "\n".join([
    "scoreboard players operation #pid m.tmp = @s m.id",
    # minerai visé au tick d'avant devenu de l'air : il vient d'être cassé, on casse la veine
    "scoreboard players set #fgo m.tmp 0",
    f"execute as {MK} if score @s m.own = #pid m.tmp if score @s m.fk matches 1.. at @s if block ~ ~ ~ #{NS}:vide run function {NS}:m/filon_casse",
    f"execute if score #fgo m.tmp matches 1.. at @e[type=minecraft:marker,tag=metiers.fgo,limit=1] run function {NS}:m/filon_depart",
    "tag @e[type=minecraft:marker,tag=metiers.fgo] remove metiers.fgo",
    # un seul repère par joueur, près de lui
    f"execute as @e[type=minecraft:marker,tag=metiers.fvise,distance=16..] if score @s m.own = #pid m.tmp run kill @s",
    "scoreboard players set #fm m.tmp 0",
    f"execute as {MK} if score @s m.own = #pid m.tmp run scoreboard players set #fm m.tmp 1",
    f'execute if score #fm m.tmp matches 0 run summon minecraft:marker ~ ~ ~ {{Tags:["metiers.fvise","metiers.fnew"]}}',
    "scoreboard players operation @e[type=minecraft:marker,tag=metiers.fnew] m.own = #pid m.tmp",
    "tag @e[type=minecraft:marker,tag=metiers.fnew] remove metiers.fnew",
    # le minerai visé maintenant
    "scoreboard players set #fk m.tmp 0", "scoreboard players set #fpas m.tmp 0",
    f"execute anchored eyes positioned ^ ^ ^ run function {NS}:m/filon_rayon",
    f"execute as {MK} if score @s m.own = #pid m.tmp run scoreboard players operation @s m.fk = #fk m.tmp"]))
w(F + "m/filon_casse.mcfunction", "scoreboard players operation #fgo m.tmp = @s m.fk\ntag @s add metiers.fgo\nscoreboard players set @s m.fk 0")
w(F + "m/filon_rayon.mcfunction", "\n".join([
    f"execute unless block ~ ~ ~ #{NS}:vide run return run function {NS}:m/filon_viser",
    "scoreboard players add #fpas m.tmp 1",
    f"execute if score #fpas m.tmp matches ..55 positioned ^ ^ ^0.1 run function {NS}:m/filon_rayon"]))
w(F + "m/filon_viser.mcfunction", "\n".join(
    [f"execute if block ~ ~ ~ #{NS}:filon_{f_} run scoreboard players set #fk m.tmp {c}" for c, f_ in enumerate(FAMS, 1)] +
    [f"execute if score #fk m.tmp matches 1.. align xyz positioned ~0.5 ~0.5 ~0.5 as {MK} if score @s m.own = #pid m.tmp run tp @s ~ ~ ~"]))
add_lines(F + "refonte/tick.mcfunction", [
    f"execute as @a[tag=metiers.sk.pm1,gamemode=!spectator] at @s if items entity @s weapon.mainhand #minecraft:pickaxes run function {NS}:m/filon_tick"])

# ---------------------------------------------------------------- Mineur : compétence Veine (m15, ex-Lanterne), accroupi (26/11/2026)
# Même mécanique que le Filon (repère sur le bloc visé, veine cassée quand il devient de l'air), mais pour les minerais
# et les roches et blocs naturels qu'on creuse à la pioche ; jamais la pierre, la deepslate ni la netherrack.
VEINE_EXTRA = ["granite", "diorite", "andesite", "tuff", "calcite", "dripstone_block", "basalt", "smooth_basalt", "blackstone",
               "obsidian", "crying_obsidian", "amethyst_block", "glowstone", "magma_block", "end_stone", "sandstone",
               "red_sandstone", "terracotta", "packed_ice", "blue_ice", "cobblestone", "mossy_cobblestone", "cobbled_deepslate",
               "raw_iron_block", "raw_copper_block", "raw_gold_block", "bone_block", "prismarine", "purpur_block"]
VFAM = {**{f_: lst for f_, lst in FAM.items()}, **{b: [b] for b in VEINE_EXTRA}}
VFAMS = list(VFAM)
for f_, lst in VFAM.items():
    wj(f"data/{NS}/tags/block/veine_{f_}.json", {"values": [f"minecraft:{o}" for o in lst]})
for code, f_ in enumerate(VFAMS, 1):
    w(F + f"m/veine_{f_}_voisins.mcfunction", "\n".join(
        f"execute if score #fn m.tmp < #fmax m.tmp positioned ~{dx} ~{dy} ~{dz} if block ~ ~ ~ #{NS}:veine_{f_} run function {NS}:m/veine_{f_}_bloc"
        for dx, dy, dz in VOIS))
    w(F + f"m/veine_{f_}_bloc.mcfunction", "\n".join(
        ["scoreboard players add #fn m.tmp 1"] +
        [f"execute if block ~ ~ ~ minecraft:{o} run scoreboard players add @s m.m_raw {ORES[o]}" for o in VFAM[f_] if o in ORES] +
        ["loot give @s mine ~ ~ ~ mainhand", "setblock ~ ~ ~ minecraft:air",
         "particle minecraft:block{block_state:\"minecraft:stone\"} ~ ~ ~ 0.3 0.3 0.3 0 4",
         f"function {NS}:m/veine_{f_}_voisins"]))
w(F + "m/veine_depart.mcfunction", "\n".join(
    ["scoreboard players set #fn m.tmp 0", "scoreboard players set #fmax m.tmp 48"] +
    [f"execute if score #vgo m.tmp matches {c} run function {NS}:m/veine_{f_}_voisins" for c, f_ in enumerate(VFAMS, 1)] +
    ["execute if score #fn m.tmp matches 1.. run playsound minecraft:block.deepslate.break master @s ~ ~ ~ 1 0.7"]))
VK = "@e[type=minecraft:marker,tag=metiers.vvise]"
w(F + "m/veine_tick.mcfunction", "\n".join([
    "scoreboard players operation #pid m.tmp = @s m.id",
    "scoreboard players set #vgo m.tmp 0",
    f"execute as {VK} if score @s m.own = #pid m.tmp if score @s m.vk matches 1.. at @s if block ~ ~ ~ #{NS}:vide run function {NS}:m/veine_casse",
    f"execute if score #vgo m.tmp matches 1.. at @e[type=minecraft:marker,tag=metiers.vgo,limit=1] run function {NS}:m/veine_depart",
    "tag @e[type=minecraft:marker,tag=metiers.vgo] remove metiers.vgo",
    f"execute as @e[type=minecraft:marker,tag=metiers.vvise,distance=16..] if score @s m.own = #pid m.tmp run kill @s",
    "scoreboard players set #fm m.tmp 0",
    f"execute as {VK} if score @s m.own = #pid m.tmp run scoreboard players set #fm m.tmp 1",
    f'execute if score #fm m.tmp matches 0 run summon minecraft:marker ~ ~ ~ {{Tags:["metiers.vvise","metiers.vnew"]}}',
    "scoreboard players operation @e[type=minecraft:marker,tag=metiers.vnew] m.own = #pid m.tmp",
    "tag @e[type=minecraft:marker,tag=metiers.vnew] remove metiers.vnew",
    "scoreboard players set #vk m.tmp 0", "scoreboard players set #fpas m.tmp 0",
    f"execute anchored eyes positioned ^ ^ ^ run function {NS}:m/veine_rayon",
    f"execute as {VK} if score @s m.own = #pid m.tmp run scoreboard players operation @s m.vk = #vk m.tmp"]))
w(F + "m/veine_casse.mcfunction", "scoreboard players operation #vgo m.tmp = @s m.vk\ntag @s add metiers.vgo\nscoreboard players set @s m.vk 0")
w(F + "m/veine_rayon.mcfunction", "\n".join([
    f"execute unless block ~ ~ ~ #{NS}:vide run return run function {NS}:m/veine_viser",
    "scoreboard players add #fpas m.tmp 1",
    f"execute if score #fpas m.tmp matches ..55 positioned ^ ^ ^0.1 run function {NS}:m/veine_rayon"]))
w(F + "m/veine_viser.mcfunction", "\n".join(
    [f"execute if block ~ ~ ~ #{NS}:veine_{f_} run scoreboard players set #vk m.tmp {c}" for c, f_ in enumerate(VFAMS, 1)] +
    [f"execute if score #vk m.tmp matches 1.. align xyz positioned ~0.5 ~0.5 ~0.5 as {VK} if score @s m.own = #pid m.tmp run tp @s ~ ~ ~"]))
add_lines(F + "refonte/load.mcfunction", ["scoreboard objectives add m.vk dummy"])
add_lines(F + "refonte/tick.mcfunction", [
    f"execute as @a[tag=metiers.sk.m15,predicate={NS}:accroupi,gamemode=!spectator] at @s if items entity @s weapon.mainhand #minecraft:pickaxes run function {NS}:m/veine_tick"])

# ---------------------------------------------------------------- Fermier : Moisson (même récolte que la Faux de la Forge)
for r in (1, 2, 3):
    w(F + f"f/moisson_{r}.mcfunction", "\n".join(
        f"execute positioned ~{dx} ~ ~{dz} run function {NS}:forge/faux_bloc" for dx in range(-r, r + 1) for dz in range(-r, r + 1)))

# ---------------------------------------------------------------- Chasseur : Exécution
wj(f"data/{NS}/tags/entity_type/executables.json",
   {"values": [{"id": f"minecraft:{h}", "required": False} for h in HOSTILES if h not in ("elder_guardian", "warden")]})
w(F + "c/execution.mcfunction", "\n".join([
    "tag @s add metiers.exec", "scoreboard players set #thr m.tmp 10",
    "execute if entity @s[tag=metiers.sk.pc3] run scoreboard players set #thr m.tmp 15",
    "execute if entity @s[tag=metiers.sk.pc5] run scoreboard players set #thr m.tmp 20",
    f"execute as @e[type=#{NS}:executables,distance=..12,tag=!metiers.boss,tag=!hr.c] if data entity @s {{HurtTime:10s}} run function {NS}:c/execution_mob",
    "tag @s remove metiers.exec"]))
w(F + "c/execution_mob.mcfunction", "\n".join([
    "scoreboard players set #ok m.tmp 0",
    "execute on attacker if entity @s[tag=metiers.exec] run scoreboard players set #ok m.tmp 1",
    "execute if score #ok m.tmp matches 0 run return 0",
    "execute store result score #h m.tmp run data get entity @s Health 100",
    "execute store result score #mx m.tmp run attribute @s minecraft:max_health get 1",
    "scoreboard players operation #mx m.tmp *= #thr m.tmp",
    f"execute if score #h m.tmp matches 1.. if score #h m.tmp <= #mx m.tmp run function {NS}:c/executer"]))
w(F + "c/executer.mcfunction", "\n".join([
    "particle minecraft:sweep_attack ~ ~1 ~ 0.2 0.2 0.2 0 2", "particle minecraft:crit ~ ~1 ~ 0.4 0.5 0.4 0.3 20",
    "playsound minecraft:entity.player.attack.crit master @a ~ ~ ~ 1 0.6",
    "damage @s 9999 minecraft:player_attack by @a[tag=metiers.exec,limit=1]"]))
add_lines(F + "refonte/tick.mcfunction", [
    f"execute as @a[tag=metiers.sk.pc1,scores={{m.dmgx=1..}}] at @s run function {NS}:c/execution",
    "scoreboard players set @a[scores={m.dmgx=1..}] m.dmgx 0"])

# ---------------------------------------------------------------- Éleveur : Jumeaux (appelé par la statistique animals_bred)
JU = ["execute store result score #r m.tmp run random value 1..100", "scoreboard players set #thr m.tmp 20",
      "execute if entity @s[tag=metiers.sk.pe3] run scoreboard players set #thr m.tmp 35",
      "execute if entity @s[tag=metiers.sk.pe5] run scoreboard players set #thr m.tmp 50",
      "execute if score #r m.tmp > #thr m.tmp run return 0",
      "tag @e[tag=metiers.ne] remove metiers.ne",
      f"execute as @e[type=#{NS}:animaux,distance=..12] store result score @s m.tmp run data get entity @s Age",
      f"execute as @e[type=#{NS}:animaux,distance=..12,scores={{m.tmp=-24000..-23960}},limit=1,sort=nearest] run tag @s add metiers.ne"]
JU += [f"execute as @e[tag=metiers.ne,type=minecraft:{a}] at @s run summon minecraft:{a} ~ ~ ~ {{Age:-24000}}" for a in ANIMAUX]
JU += ["execute at @e[tag=metiers.ne] run particle minecraft:heart ~ ~0.6 ~ 0.4 0.3 0.4 0 8",
       f"execute if entity @e[tag=metiers.ne] run scoreboard players add @s m.e_raw 16",
       f'execute if entity @e[tag=metiers.ne] run title @s actionbar {{"text":"Jumeaux ! Un deuxième petit est né.","color":"light_purple"}}',
       "tag @e[tag=metiers.ne] remove metiers.ne"]
w(F + "e/jumeaux.mcfunction", "\n".join(JU))

# ---------------------------------------------------------------- Enchanteur : Érudit (niveaux rendus)
add_lines(F + "n/enchant.mcfunction", [
    "scoreboard players operation #lv m.tmp = @s m.n_prev", "scoreboard players operation #lv m.tmp -= @s m.n_now",
    "execute if score #lv m.tmp matches 4.. run scoreboard players set #lv m.tmp 3",
    f"execute if entity @s[tag=metiers.sk.pn1] if score #lv m.tmp matches 1.. run function {NS}:n/erudit"])
w(F + "n/erudit.mcfunction", "\n".join([
    "execute store result score #r m.tmp run random value 1..100", "scoreboard players set #thr m.tmp 20",
    "execute if entity @s[tag=metiers.sk.pn3] run scoreboard players set #thr m.tmp 35",
    "execute if entity @s[tag=metiers.sk.pn5] run scoreboard players set #thr m.tmp 50",
    "execute if score #r m.tmp > #thr m.tmp run return 0",
    "execute if score #lv m.tmp matches 1 run xp add @s 1 levels", "execute if score #lv m.tmp matches 2 run xp add @s 2 levels",
    "execute if score #lv m.tmp matches 3 run xp add @s 3 levels",
    'title @s actionbar {"text":"Érudit : tes niveaux te sont rendus.","color":"dark_purple"}',
    "playsound minecraft:block.enchantment_table.use master @s ~ ~ ~ 1 1.5"]))

# ---------------------------------------------------------------- cadre Étoilé (7) et déclencheurs
w(F + "skins/cadre_7.mcfunction", "\n".join(
    [f"execute if score @s m.cd_7 matches 1 run return run function {NS}:skins/cadre {{i:7}}", "scoreboard players set #p5 m.tmp 0"] +
    [f"execute if score @s m.{j}_pr matches 5.. run scoreboard players set #p5 m.tmp 1" for j in JL] +
    [f"execute if score #p5 m.tmp matches 0 run return run {tr('Le cadre Étoilé demande 5 étoiles de prestige dans un métier.', 'red')}",
     "scoreboard players set @s m.cd_7 1", f"function {NS}:skins/cadre {{i:7}}"]))
add_lines(F + "trigger.mcfunction", [
    f'execute if score @s m.trig matches 447 run function {NS}:appel {{f:"skins/cadre_7"}}',
    f'execute if score @s m.trig matches 499 run function {NS}:appel {{f:"prestige/aura_basculer"}}'])

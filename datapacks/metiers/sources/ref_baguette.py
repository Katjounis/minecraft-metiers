# -*- coding: utf-8 -*-
# 27/11/2026 : Baguette du bâtisseur (building wand). C'est l'outil du métier (elle remplace la truelle) : clic droit.
# Clic droit sur la face d'un bloc : chaque bloc identique de cette face (même bloc, même état) dans un carré centré
# sur le bloc visé reçoit une copie posée devant lui, tant que l'inventaire en contient. Taille du carré :
# 3x3, puis 5x5 au palier 4, 7x7 au palier 7, 9x9 au palier 10, un cran de plus avec la synergie Charpentier (9x9 au plus). Rien n'est cassé : la baguette ne remplit que de l'air, de l'eau ou de l'herbe basse.
# La copie garde l'orientation (clone), l'objet retiré de l'inventaire est celui que donnerait le bloc au Toucher de soie.
BG = F + "baguette/"
NB = f"{NS}:baguette/"

wj(f"data/{NS}/tags/block/baguette_libre.json", {"values": [
    "minecraft:air", "minecraft:cave_air", "minecraft:void_air", "minecraft:water", "minecraft:short_grass", "minecraft:fern"]})
# blocs refusés : sans objet propre, sur deux blocs, accrochés à un support, ou qui se dupliqueraient
wj(f"data/{NS}/tags/block/baguette_interdit.json", {"values": [
    "minecraft:bedrock", "minecraft:barrier", "minecraft:light", "minecraft:structure_void", "minecraft:reinforced_deepslate",
    "minecraft:end_portal_frame", "minecraft:budding_amethyst", "minecraft:dragon_egg", "minecraft:piston_head", "minecraft:moving_piston",
    "minecraft:farmland", "minecraft:dirt_path", "minecraft:cake", "minecraft:snow", "minecraft:sea_pickle", "minecraft:turtle_egg",
    "minecraft:frogspawn", "minecraft:powder_snow", "minecraft:bubble_column", "minecraft:tall_grass", "minecraft:large_fern",
    "minecraft:sunflower", "minecraft:lilac", "minecraft:rose_bush", "minecraft:peony", "minecraft:pitcher_plant", "minecraft:tall_seagrass",
    "minecraft:torch", "minecraft:wall_torch", "minecraft:soul_torch", "minecraft:soul_wall_torch", "minecraft:redstone_torch",
    "minecraft:redstone_wall_torch", "minecraft:ladder", "minecraft:lever", "minecraft:vine", "minecraft:glow_lichen", "minecraft:tripwire",
    "minecraft:tripwire_hook", "minecraft:cocoa", "minecraft:chorus_plant", "minecraft:chorus_flower", "minecraft:kelp", "minecraft:kelp_plant",
    "minecraft:cave_vines", "minecraft:cave_vines_plant", "minecraft:weeping_vines", "minecraft:weeping_vines_plant",
    "minecraft:twisting_vines", "minecraft:twisting_vines_plant", "minecraft:big_dripleaf_stem", "minecraft:pointed_dripstone",
    "minecraft:infested_stone", "minecraft:infested_cobblestone", "minecraft:infested_stone_bricks", "minecraft:infested_mossy_stone_bricks",
    "minecraft:infested_cracked_stone_bricks", "minecraft:infested_chiseled_stone_bricks", "minecraft:infested_deepslate",
    "#minecraft:doors", "#minecraft:beds", "#minecraft:crops", "#minecraft:fire", "#minecraft:portals", "#minecraft:candles",
    "#minecraft:buttons", "#minecraft:pressure_plates", "#minecraft:rails", "#minecraft:saplings", "#minecraft:small_flowers",
    "#minecraft:wool_carpets", "#minecraft:banners", "#minecraft:all_signs"]})
# entités qui n'empêchent pas de poser
wj(f"data/{NS}/tags/entity_type/baguette_ignore.json", {"values": [
    "minecraft:item", "minecraft:experience_orb", "minecraft:marker", "minecraft:item_display", "minecraft:block_display",
    "minecraft:text_display", "minecraft:interaction", "minecraft:arrow", "minecraft:spectral_arrow", "minecraft:area_effect_cloud"]})

# ---------------------------------------------------------------- clic : lancer de rayon depuis les yeux
w(BG + "clic.mcfunction", "\n".join([
    "execute if score @s m.ocd matches 1.. run return 0",
    "scoreboard players set @s m.ocd 1",
    f"execute if entity @s[gamemode=adventure] run return run {tr('La baguette ne marche pas en mode aventure.', 'red')}",
    "kill @e[type=minecraft:marker,tag=metiers.bgair]",
    'summon minecraft:marker ~ ~ ~ {Tags:["metiers.bgair"]}',
    "scoreboard players set #pas m.tmp 0", "scoreboard players set #ok m.tmp 0",
    f"execute anchored eyes positioned ^ ^ ^ run function {NB}rayon",
    "kill @e[type=minecraft:marker,tag=metiers.bgair]",
    f"execute if score #ok m.tmp matches 0 run title @s actionbar {{\"text\":\"Vise la face d'un bloc à portée.\",\"color\":\"red\"}}"]))
# pas de 0,1 bloc, 9 blocs au plus ; le marker garde la dernière case libre traversée
w(BG + "rayon.mcfunction", "\n".join([
    "scoreboard players add #pas m.tmp 1",
    "execute if score #pas m.tmp matches 91.. run return 0",
    f"execute unless block ~ ~ ~ #{NS}:baguette_libre align xyz run return run function {NB}touche",
    "execute align xyz run tp @e[type=minecraft:marker,tag=metiers.bgair,limit=1] ~ ~ ~",
    f"execute positioned ^ ^ ^0.1 run function {NB}rayon"]))

# bloc touché (exécuté au coin du bloc) : face = case libre - bloc touché
w(BG + "touche.mcfunction", "\n".join([
    "scoreboard players set #ok m.tmp 1",
    "execute store result score #hx m.tmp run data get entity @e[type=minecraft:marker,tag=metiers.bgair,limit=1] Pos[0]",
    "execute store result score #hy m.tmp run data get entity @e[type=minecraft:marker,tag=metiers.bgair,limit=1] Pos[1]",
    "execute store result score #hz m.tmp run data get entity @e[type=minecraft:marker,tag=metiers.bgair,limit=1] Pos[2]",
    "tp @e[type=minecraft:marker,tag=metiers.bgair,limit=1] ~ ~ ~",
    "execute store result score #bx m.tmp run data get entity @e[type=minecraft:marker,tag=metiers.bgair,limit=1] Pos[0]",
    "execute store result score #by m.tmp run data get entity @e[type=minecraft:marker,tag=metiers.bgair,limit=1] Pos[1]",
    "execute store result score #bz m.tmp run data get entity @e[type=minecraft:marker,tag=metiers.bgair,limit=1] Pos[2]",
    "scoreboard players operation #hx m.tmp -= #bx m.tmp", "scoreboard players operation #hy m.tmp -= #by m.tmp",
    "scoreboard players operation #hz m.tmp -= #bz m.tmp",
    # premier pas du rayon déjà dans un bloc : pas de case libre connue
    f"execute if score #pas m.tmp matches 1 run return run {tr('Recule un peu : la baguette a besoin de voir la face.', 'red')}",
    # bloc refusé
    f"execute if data block ~ ~ ~ x run return run title @s actionbar {{\"text\":\"Ce bloc ne se copie pas (bloc avec un contenu).\",\"color\":\"red\"}}",
    f"execute if block ~ ~ ~ #{NS}:baguette_interdit run return run title @s actionbar {{\"text\":\"Ce bloc ne se copie pas à la baguette.\",\"color\":\"red\"}}",
    f"execute if block ~ ~ ~ #minecraft:slabs[type=double] run return run title @s actionbar {{\"text\":\"Pas de dalles doubles à la baguette.\",\"color\":\"red\"}}",
    # objet correspondant (Toucher de soie)
    "kill @e[type=minecraft:item_display,tag=metiers.bgloot]",
    'summon minecraft:item_display ~0.5 ~0.5 ~0.5 {Tags:["metiers.bgloot"]}',
    'loot replace entity @e[type=minecraft:item_display,tag=metiers.bgloot,limit=1] contents mine ~ ~ ~ minecraft:netherite_pickaxe[minecraft:enchantments={"minecraft:silk_touch":1}]',
    f"data remove storage {NS}:bg id",
    f"data modify storage {NS}:bg id set from entity @e[type=minecraft:item_display,tag=metiers.bgloot,limit=1] item.id",
    "kill @e[type=minecraft:item_display,tag=metiers.bgloot]",
    f"execute unless data storage {NS}:bg id run return run title @s actionbar {{\"text\":\"Ce bloc ne se copie pas à la baguette.\",\"color\":\"red\"}}",
    # taille selon le palier de l'outil : 3x3, 5x5 (palier 4), 7x7 (7), 9x9 (10) ; +1 avec Charpentier, 9x9 au plus
    'execute store result score #pal m.tmp run data get entity @s SelectedItem.components."minecraft:custom_data".palier',
    "scoreboard players set #wr m.tmp 1",
    "execute if score #pal m.tmp matches 4.. run scoreboard players set #wr m.tmp 2",
    "execute if score #pal m.tmp matches 7.. run scoreboard players set #wr m.tmp 3",
    "execute if score #pal m.tmp matches 10.. run scoreboard players set #wr m.tmp 4",
    f"execute if entity @s[tag={NS}.sk.ykb] run scoreboard players add #wr m.tmp 1",
    "execute if score #wr m.tmp matches 5.. run scoreboard players set #wr m.tmp 4",
    f"function {NB}stock with storage {NS}:bg",
    "execute if entity @s[gamemode=creative] run scoreboard players set #reste m.tmp 9999",
    f"execute if score #reste m.tmp matches ..0 run return run title @s actionbar {{\"text\":\"Il te faut ce bloc dans ton inventaire.\",\"color\":\"red\"}}",
    "scoreboard players set #poses m.tmp 0"] +
    [f"execute if score #hx m.tmp matches {dx} if score #hy m.tmp matches {dy} if score #hz m.tmp matches {dz} run function {NB}face_{nom}"
     for nom, (dx, dy, dz) in (("est", (1, 0, 0)), ("ouest", (-1, 0, 0)), ("haut", (0, 1, 0)), ("bas", (0, -1, 0)), ("sud", (0, 0, 1)), ("nord", (0, 0, -1)))] +
    [f"execute if score #poses m.tmp matches 0 run return run title @s actionbar {{\"text\":\"Rien à prolonger ici (place libre ou face nette).\",\"color\":\"gray\"}}",
     f"execute store result storage {NS}:bg n int 1 run scoreboard players get #poses m.tmp",
     f"execute unless entity @s[gamemode=creative] run function {NB}payer with storage {NS}:bg",
     "playsound minecraft:block.amethyst_block.chime master @a ~ ~ ~ 1 1.2",
     'title @s actionbar [{"text":"Baguette : ","color":"#C08850"},{"score":{"name":"#poses","objective":"m.tmp"},"color":"white"},{"text":" blocs posés","color":"#C08850"}]']))
w(BG + "stock.mcfunction", "$execute store result score #reste m.tmp run clear @s $(id) 0")
w(BG + "payer.mcfunction", "$clear @s $(id) $(n)")
w(BG + "pose.mcfunction", "\n".join([
    "$clone ~$(sx) ~$(sy) ~$(sz) ~$(sx) ~$(sy) ~$(sz) ~ ~ ~",
    "scoreboard players remove #reste m.tmp 1", "scoreboard players add #poses m.tmp 1",
    "particle minecraft:wax_on ~0.5 ~0.5 ~0.5 0.3 0.3 0.3 0 3"]))

# une fonction par face : cases du plan triées du centre vers le bord (le stock part d'abord au centre)
RMAX = 4
for nom, n in (("est", (1, 0, 0)), ("ouest", (-1, 0, 0)), ("haut", (0, 1, 0)), ("bas", (0, -1, 0)), ("sud", (0, 0, 1)), ("nord", (0, 0, -1))):
    axes = [i for i in range(3) if n[i] == 0]
    cases = []
    for a in range(-RMAX, RMAX + 1):
        for b in range(-RMAX, RMAX + 1):
            o = [0, 0, 0]
            o[axes[0]], o[axes[1]] = a, b
            cases.append((max(abs(a), abs(b)), a * a + b * b, o))
    cases.sort(key=lambda c: (c[0], c[1]))
    L = []
    for ring, _, o in cases:
        t = [o[i] + n[i] for i in range(3)]
        L.append(f"execute if score #reste m.tmp matches 1.. if score #wr m.tmp matches {ring}.. "
                 f"if blocks ~{o[0]} ~{o[1]} ~{o[2]} ~{o[0]} ~{o[1]} ~{o[2]} ~ ~ ~ all "
                 f"positioned ~{t[0]} ~{t[1]} ~{t[2]} if block ~ ~ ~ #{NS}:baguette_libre "
                 f"unless entity @e[type=!#{NS}:baguette_ignore,dx=0,dy=0,dz=0] "
                 f"run function {NB}pose {{sx:{-t[0]},sy:{-t[1]},sz:{-t[2]}}}")
    w(BG + f"face_{nom}.mcfunction", "\n".join(L))

# ---------------------------------------------------------------- l'ancienne truelle (pinceau) est échangée contre la baguette
_VT = 'minecraft:brush[minecraft:custom_data~{metiers_outil:"k"}]'
w(BG + "echange.mcfunction", "\n".join([
    f"clear @s {_VT}",
    f"function {NS}:k/outil_donner",
    "playsound minecraft:block.amethyst_block.chime master @s ~ ~ ~ 1 1.4",
    tr("Ta truelle devient la Baguette du bâtisseur : clic droit sur la face d’un bloc pour la prolonger avec les blocs de ton inventaire.", "light_purple")]))
add_lines(F + "refonte/joueur.mcfunction", [
    f"execute if score #quatre m.timer matches 0 if items entity @s container.* {_VT} run function {NS}:baguette/echange",
    f"execute if score #quatre m.timer matches 0 if items entity @s weapon.offhand {_VT} run function {NS}:baguette/echange"])

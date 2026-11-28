# -*- coding: utf-8 -*-
import json
# Îles, parcelles, bâtiments, voyage et protection. Exécuté par datapack.py.
#
# Île n : centre (cx, cz) = ((n % 16) x 2048, (n / 16) x 2048), sol en y = 63. Grille de 7 x 7 parcelles de 32 x 32,
# parcelle idx = j x 7 + i (i, j de 0 à 6, centre 24). Emplacements de machine : 4 par parcelle (quarts), 2 au centre
# (côté ouest), numéro sid = idx x 4 + s. Le centre porte le Nexus, la Halle, la Banque, le Laboratoire et les Grands Œuvres.
SLOTS = [(8, 8), (24, 8), (8, 24), (24, 24)]
ECH_M = 2.3                                        # échelle des machines (environ 7 blocs)
BAT = {"nexus": (16, 16, 2.0, 90), "halle": (25, 7, 2.2, 91), "banque": (25, 25, 2.0, 92), "labo": (16, 28, 1.6, 93), "oeuvre": (16, 3, 1.0, 94)}

# ---------------------------------------------------------------- centre de l'île du joueur (#cx, #cz) depuis #n
fn("ile/centre", [f"{S} operation #cx i.t = #n i.t", f"{S} operation #cx i.t %= #16 i.g", f"{S} operation #cx i.t *= #2048 i.g",
                  f"{S} operation #cz i.t = #n i.t", f"{S} operation #cz i.t /= #16 i.g", f"{S} operation #cz i.t *= #2048 i.g"])

# ---------------------------------------------------------------- création de l'île (première visite)
fn("ile/creer", [
    f"{S} operation @s i.ile = #next i.g", f"{S} add #next i.g 1",
    f"{S} set @s i.p24 1", f"{S} set @s i.np 1", f"{S} set @s i.rang 1", f"{S} set @s i.halle 0",
    f"{S} operation #min i.t = #now i.g", f"{S} operation #min i.t /= #1200 i.g", f"{S} operation @s i.tl = #min i.t",
    f"{S} operation #x i.t = #now i.g", f"{S} operation #x i.t /= #72000 i.g", f"{S} operation @s i.th = #x i.t",
    f"{S} operation #x i.t = #now i.g", f"{S} operation #x i.t /= #1728000 i.g", f"{S} operation @s i.td = #x i.t",
    # la carrière offerte (ses entités sont posées par le chantier du centre)
    f"{S} set @s i.q_carriere 100", f"{S} set @s i.n_carriere 1", f"{S} set @s i.k_carriere 10",
    f"function {NS}:contrat/tirer",
    f"{S} operation #n i.t = @s i.ile", f"{S} set #idx i.t 24", f"{S} operation #own i.t = @s m.id",
    f"function {NS}:parcelle/commander",
    "playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1",
    say("Ton île t'attend dans l'Archipel : Nexus, Échoppe et une Carrière automatique déjà posés. Bienvenue, Atelier !", "gold")])

# ---------------------------------------------------------------- commande d'une parcelle : forceload puis chantier
# #n île, #idx parcelle, #own propriétaire (m.id)
fn("parcelle/commander", [
    f"function {NS}:ile/centre",
    f"{S} operation #i i.t = #idx i.t", f"{S} operation #i i.t %= #7 i.g", f"{S} operation #j i.t = #idx i.t", f"{S} operation #j i.t /= #7 i.g",
    f"{S} operation #ox i.t = #i i.t", f"{S} operation #ox i.t *= #32 i.g", f"{S} operation #ox i.t += #cx i.t", f"{S} remove #ox i.t 112",
    f"{S} operation #oz i.t = #j i.t", f"{S} operation #oz i.t *= #32 i.g", f"{S} operation #oz i.t += #cz i.t", f"{S} remove #oz i.t 112",
    f"{S} set #ring i.t 0",
    f"{S} operation #a i.t = #i i.t", f"{S} remove #a i.t 3", f"execute if score #a i.t matches ..-1 run {S} operation #a i.t *= #-1 i.g",
    f"{S} operation #b i.t = #j i.t", f"{S} remove #b i.t 3", f"execute if score #b i.t matches ..-1 run {S} operation #b i.t *= #-1 i.g",
    f"{S} operation #ring i.t = #a i.t", f"execute if score #b i.t > #a i.t run {S} operation #ring i.t = #b i.t",
    f"execute store result storage {NS}:t c.ox int 1 run {S} get #ox i.t", f"execute store result storage {NS}:t c.oz int 1 run {S} get #oz i.t",
    f"{S} operation #x i.t = #ox i.t", f"{S} add #x i.t 31", f"execute store result storage {NS}:t c.ox2 int 1 run {S} get #x i.t",
    f"{S} operation #x i.t = #oz i.t", f"{S} add #x i.t 31", f"execute store result storage {NS}:t c.oz2 int 1 run {S} get #x i.t",
    f"execute store result storage {NS}:t c.ring int 1 run {S} get #ring i.t", f"execute store result storage {NS}:t c.idx int 1 run {S} get #idx i.t",
    f"execute store result storage {NS}:t c.own int 1 run {S} get #own i.t",
    f"execute store result storage {NS}:t c.cx int 1 run {S} get #cx i.t", f"execute store result storage {NS}:t c.cz int 1 run {S} get #cz i.t",
    f"function {NS}:parcelle/forceload with storage {NS}:t c",
    f"data modify storage {NS}:file l append from storage {NS}:t c",
    f"schedule function {NS}:chantier 5t append"])
fn("parcelle/forceload", f"$execute in {DIM} run forceload add $(ox) $(oz) $(ox2) $(oz2)")
fn("chantier", [
    f"execute unless data storage {NS}:file l[0] run return 0",
    f"data modify storage {NS}:t k set from storage {NS}:file l[0]", f"data remove storage {NS}:file l[0]",
    f"function {NS}:chantier_m with storage {NS}:t k",
    f"execute if data storage {NS}:file l[0] run schedule function {NS}:chantier 5t append"])
fn("chantier_m", [
    f"$execute in {DIM} positioned $(ox) 63 $(oz) run function {NS}:parcelle/batir_$(ring)",
    f"$execute in {DIM} positioned $(ox) 64 $(oz) run function {NS}:parcelle/slots {{idx:$(idx),own:$(own)}}",
    f"$execute in {DIM} run forceload remove $(ox) $(oz) $(ox2) $(oz2)",
    f"$execute in {DIM} positioned $(ox) 64 $(oz) run particle minecraft:happy_villager ~16 ~1 ~16 10 1 10 0 200 force"])

SOL = {0: ("minecraft:polished_deepslate", "minecraft:moss_block"), 1: ("minecraft:dirt", "minecraft:grass_block"),
       2: ("minecraft:dirt", "minecraft:grass_block"), 3: ("minecraft:sandstone", "minecraft:sand")}
for r, (sous, dessus) in SOL.items():
    fn(f"parcelle/batir_{r}", [
        f"fill ~ ~-2 ~ ~31 ~-1 ~31 minecraft:stone", f"fill ~ ~-1 ~ ~31 ~-1 ~31 {sous}", f"fill ~ ~ ~ ~31 ~ ~31 {dessus}",
        # chemin de bordure et liseré doré aux coins
        f"fill ~ ~ ~ ~31 ~ ~ minecraft:polished_andesite", f"fill ~ ~ ~31 ~31 ~ ~31 minecraft:polished_andesite",
        f"fill ~ ~ ~ ~ ~ ~31 minecraft:polished_andesite", f"fill ~31 ~ ~ ~31 ~ ~31 minecraft:polished_andesite",
        *[f"setblock ~{x} ~ ~{z} minecraft:gold_block" for x in (0, 31) for z in (0, 31)],
        *[f"setblock ~{x} ~1 ~{z} minecraft:lantern" for x in (0, 31) for z in (0, 31)]])

# emplacements : dalle de 9 x 9 et marqueur (macro : idx, own)
fn("parcelle/slots", [
    f"{S} set #c24 i.t 0",
    "$scoreboard players set #pidx i.t $(idx)",
    f"execute if score #pidx i.t matches 24 run {S} set #c24 i.t 1",
    f"execute if score #c24 i.t matches 1 run function {NS}:ile/batir_centre",
    f"{S} set #ss i.t 0"] + [
    f"execute if score #c24 i.t matches 0 positioned ~{x - 4} ~-1 ~{z - 4} run function {NS}:parcelle/dalle" for x, z in SLOTS] + [
    f"execute if score #c24 i.t matches 0 positioned ~{x} ~ ~{z} run function {NS}:parcelle/marqueur" for x, z in SLOTS] + [
    f"execute if score #c24 i.t matches 1 positioned ~{SLOTS[s][0]} ~ ~{SLOTS[s][1]} run function {NS}:parcelle/marqueur_c {{s:{s}}}" for s in (0, 2)] + [
    "$scoreboard players set @e[type=minecraft:marker,tag=ind.nouv] i.own $(own)",
    f"$scoreboard players set #base i.t $(idx)", f"{S} operation #base i.t *= #4 i.g",
    f"execute as @e[type=minecraft:marker,tag=ind.nouv] run {S} operation @s i.sid += #base i.t",
    "tag @e[type=minecraft:marker,tag=ind.nouv] remove ind.nouv",
    f"{S} set #c24 i.t 0"])
fn("parcelle/dalle", ["fill ~ ~ ~ ~8 ~ ~8 minecraft:polished_blackstone", "fill ~1 ~ ~1 ~7 ~ ~7 minecraft:polished_blackstone_bricks",
                      *[f"setblock ~{x} ~ ~{z} minecraft:gold_block" for x in (0, 8) for z in (0, 8)]])
fn("parcelle/marqueur", [
    'summon minecraft:marker ~0.5 ~ ~0.5 {Tags:["ind.slot","ind.nouv"]}',
    f"{S} operation @e[type=minecraft:marker,tag=ind.nouv,limit=1,sort=nearest] i.sid = #ss i.t", f"{S} add #ss i.t 1"])
fn("parcelle/marqueur_c", [
    'summon minecraft:marker ~0.5 ~ ~0.5 {Tags:["ind.slot","ind.nouv"]}',
    "$scoreboard players set @e[type=minecraft:marker,tag=ind.nouv,limit=1,sort=nearest] i.sid $(s)",
    # l'emplacement 0 du centre porte la carrière offerte
    "$execute if score #zero_$(s) i.g matches 0 run tag @e[type=minecraft:marker,tag=ind.nouv,limit=1,sort=nearest] add ind.occ",
    f"execute positioned ~-4 ~-1 ~-4 run function {NS}:parcelle/dalle"])


def bat_summon(nom, x, z, ech, code):
    h = round(1.5 * ech, 2)
    return [f'summon minecraft:item_display ~{x} ~{h} ~{z} {{Tags:["ind.bat","ind.b_{nom}","ind.nouvb"],item_display:"none",view_range:3f,'
            f'brightness:{{sky:15,block:15}},item:{{id:"minecraft:paper",count:1,components:{{"minecraft:item_model":"{NS}:{nom}"}}}},'
            f'transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[{ech}f,{ech}f,{ech}f]}}}}',
            f'summon minecraft:interaction ~{x} ~ ~{z} {{Tags:["ind.bi","ind.nouvb"],width:{round(ech * 2.6, 1)}f,height:{round(ech * 2.4, 1)}f}}',
            f"execute as @e[tag=ind.nouvb,distance=..40] unless score @s i.mt matches -2147483648.. run {S} set @s i.mt {code}"]


CENTRE = []
for nom, (x, z, ech, code) in BAT.items():
    if nom in ("nexus", "halle"):
        CENTRE += bat_summon(nom if nom != "halle" else "echoppe", x, z, ech, code)
CENTRE += [f"{S} operation @e[tag=ind.nouvb,distance=..40] i.own = #own i.t", "tag @e[tag=ind.nouvb,distance=..40] remove ind.nouvb",
           # la carrière offerte, sur l'emplacement 0 du centre
           f"{S} set #pm i.t 0", f"{S} set #pl i.t 1", f"{S} set #psid i.t 96", f"{S} set #tt i.t 0",
           f"{S} set #mob i.t 0", f"{S} set #sf i.t 100", f"{S} set #spv i.t 0", f"{S} set #spq i.t 0",
           f"execute positioned ~{SLOTS[0][0]} ~ ~{SLOTS[0][1]} run function {NS}:machine/visuel_ici",
           "fill ~10 ~-1 ~10 ~22 ~-1 ~22 minecraft:polished_blackstone_bricks", "fill ~12 ~-1 ~12 ~20 ~-1 ~20 minecraft:chiseled_polished_blackstone"]
fn("ile/batir_centre", [f"execute store result score #own i.t run data get storage {NS}:t k.own"] + CENTRE)

# bâtiment posé plus tard (Banque, Laboratoire, Grand Œuvre, Halle) : macro nom, ech, code, x, z sur le centre de l'île de @s
fn("batiment/poser", [
    f"{S} operation #n i.t = @s i.ile", f"function {NS}:ile/centre",
    f"execute store result storage {NS}:t b.x int 1 run {S} get #cx i.t", f"execute store result storage {NS}:t b.z int 1 run {S} get #cz i.t",
    f"function {NS}:batiment/poser_m with storage {NS}:t b"])
fn("batiment/poser_m", [
    "$kill @e[tag=ind.b_$(old),x=$(x),y=64,z=$(z),distance=..40]",
    "$execute in industrie:archipel positioned $(x) 63 $(z) positioned ~-16 ~1 ~-16 run function industrie:batiment/poser_ici with storage industrie:t b"])
fn("batiment/poser_ici", [
    '$summon minecraft:item_display ~$(dx) ~$(h) ~$(dz) {Tags:["ind.bat","ind.b_$(nom)","ind.nouvb"],item_display:"none",view_range:3f,'
    'brightness:{sky:15,block:15},item:{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"industrie:$(nom)"}},'
    'transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[$(ech)f,$(ech)f,$(ech)f]}}',
    '$execute positioned ~$(dx) ~ ~$(dz) unless entity @e[type=minecraft:interaction,tag=ind.bi,distance=..3] run summon minecraft:interaction ~ ~ ~ {Tags:["ind.bi","ind.nouvb"],width:$(lw)f,height:$(lh)f}',
    f"$scoreboard players set @e[tag=ind.nouvb,distance=..60] i.mt $(code)",
    f"{S} operation @e[tag=ind.nouvb,distance=..60] i.own = @s m.id", "tag @e[tag=ind.nouvb] remove ind.nouvb"])


def poser_bat(nom, cle=None, old="aucun"):
    x, z, ech, code = BAT[cle or nom]
    return [f'data modify storage {NS}:t b set value {{nom:"{nom}",old:"{old}",dx:{x},dz:{z},h:{round(1.5 * ech, 2)},ech:{ech},code:{code},'
            f'lw:{round(ech * 2.6, 1)},lh:{round(ech * 2.4, 1)}}}',
            f"execute at @s if dimension {DIM} run function {NS}:batiment/poser"]


# ---------------------------------------------------------------- voyage
fn("ile/aller", [
    f"execute unless score @s m.id matches 1.. run return run " + say("Métiers doit d'abord t'inscrire (reconnecte-toi).", "red"),
    f"execute at @s unless dimension {DIM} run function {NS}:ile/sauver",
    f"execute unless score @s i.ile matches 0.. run function {NS}:ile/creer",
    f"{S} operation #n i.t = @s i.ile", f"function {NS}:ile/tp",
    f"execute in {DIM} positioned as @s unless entity @e[type=minecraft:interaction,tag=ind.ret,distance=..24] run function {NS}:ile/portail_retour",
    
    f"function {NS}:ile/etiquettes",
    f"execute unless score @s i.cin matches 1.. run return run {S} set @s i.cin 1",
    'title @s actionbar [{"text":"Retour au monde normal : le portail à côté de toi, ou G puis Industrie, Revenir","color":"#F7C843"}]'])
# portail de retour au monde normal, à côté du point d'arrivée (posé une fois par île)
fn("ile/portail_retour", [
    "setblock ~3 63 ~ minecraft:gold_block", "setblock ~3 64 ~ minecraft:crying_obsidian", "setblock ~3 65 ~ minecraft:crying_obsidian",
    'summon minecraft:text_display ~3.5 66.4 ~0.5 {Tags:["ind.rett"],billboard:"center",background:1426063360,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.55f,0.55f,0.55f]},'
    'text:[{"text":"⟲ ","color":"#F7C843"},{"text":"Retour au monde normal","color":"white","bold":true},{"text":"\\nclic droit sur l\'obsidienne","color":"gray"}]}',
    'summon minecraft:interaction ~3.5 64 ~0.5 {Tags:["ind.bi","ind.ret"],width:1.4f,height:2.2f}',
    "particle minecraft:portal ~3.5 65 ~0.5 0.4 1 0.4 0.2 60"])
fn("ile/tp", [
    f"function {NS}:ile/centre",
    f"{S} operation #x i.t = #cx i.t", f"{S} operation #z i.t = #cz i.t", f"{S} add #z i.t 7",
    f"execute store result storage {NS}:t v.x int 1 run {S} get #x i.t", f"execute store result storage {NS}:t v.z int 1 run {S} get #z i.t",
    "effect give @s minecraft:slow_falling 6 0 true", "effect give @s minecraft:resistance 6 4 true",
    f"function {NS}:ile/tp_m with storage {NS}:t v",
    "playsound minecraft:block.portal.travel master @s ~ ~ ~ 0.4 1.6"])
fn("ile/tp_m", f"$execute in {DIM} run tp @s $(x).5 66 $(z).5 180 10")
fn("ile/sauver", [
    "execute store result score @s i.rx run data get entity @s Pos[0] 10", "execute store result score @s i.ry run data get entity @s Pos[1] 10",
    "execute store result score @s i.rz run data get entity @s Pos[2] 10", f"{S} set @s i.rd 0",
    f"execute if dimension minecraft:the_nether run {S} set @s i.rd 1", f"execute if dimension minecraft:the_end run {S} set @s i.rd 2",
    f"{S} set @s i.gm 0", f"execute if entity @s[gamemode=adventure] run {S} set @s i.gm 2"])
fn("ile/retour", [
    f"execute at @s unless dimension {DIM} run return run " + say("Tu n'es pas dans l'Archipel.", "gray"),
    "tag @s remove ind.adv", f"execute if score @s i.gm matches 0 if entity @s[gamemode=adventure] run gamemode survival @s",
    f"execute unless score @s i.ry matches -2147483648.. run return run execute in minecraft:overworld run spreadplayers 0 0 0 1 false @s",
    "execute store result storage industrie:r x double 0.1 run scoreboard players get @s i.rx",
    "execute store result storage industrie:r y double 0.1 run scoreboard players get @s i.ry",
    "execute store result storage industrie:r z double 0.1 run scoreboard players get @s i.rz",
    'data modify storage industrie:r d set value "minecraft:overworld"',
    'execute if score @s i.rd matches 1 run data modify storage industrie:r d set value "minecraft:the_nether"',
    'execute if score @s i.rd matches 2 run data modify storage industrie:r d set value "minecraft:the_end"',
    f"function {NS}:ile/retour_m with storage industrie:r", "effect give @s minecraft:resistance 4 4 true"])
fn("ile/retour_m", "$execute in $(d) run tp @s $(x) $(y) $(z)")
# visite de l'île d'un autre joueur : 8000 + numéro d'île
fn("ile/visiter", [
    f"{S} operation #n i.t = #v i.t", f"{S} remove #n i.t 8000",
    f"execute at @s unless dimension {DIM} run function {NS}:ile/sauver",
    f"function {NS}:ile/tp", say("Tu visites une île : regarde, mais ne touche à rien (mode aventure).", "gray")])

# ---------------------------------------------------------------- garde : mode de jeu selon la parcelle, chute dans le vide
G_ = [f"execute if entity @s[gamemode=creative] run return 0", f"execute if entity @s[gamemode=spectator] run return 0",
      "execute store result score #px i.t run data get entity @s Pos[0]", "execute store result score #py i.t run data get entity @s Pos[1]",
      "execute store result score #pz i.t run data get entity @s Pos[2]",
      f"execute if score #py i.t matches ..40 run return run function {NS}:ile/vide",
      f"{S} set #ok i.t 0",
      f"{S} operation #a i.t = #px i.t", f"{S} add #a i.t 1024", f"{S} operation #b i.t = #pz i.t", f"{S} add #b i.t 1024",
      f"execute if score #a i.t matches 0.. if score #b i.t matches 0.. run function {NS}:ile/garde_calc",
      f"execute if score #ok i.t matches 1 if entity @s[tag=ind.adv] run function {NS}:ile/survie",
      f"execute if score #ok i.t matches 0 unless entity @s[tag=ind.adv] if entity @s[gamemode=survival] run function {NS}:ile/aventure"]
fn("ile/garde", G_)
GC = [f"{S} operation #a i.t /= #2048 i.g", f"{S} operation #b i.t /= #2048 i.g",
      f"execute if score #a i.t matches 16.. run return 0",
      f"{S} operation #n i.t = #b i.t", f"{S} operation #n i.t *= #16 i.g", f"{S} operation #n i.t += #a i.t",
      f"execute unless score #n i.t = @s i.ile run return 0",
      f"function {NS}:ile/centre",
      f"{S} operation #i i.t = #px i.t", f"{S} operation #i i.t -= #cx i.t", f"{S} add #i i.t 112",
      f"{S} operation #j i.t = #pz i.t", f"{S} operation #j i.t -= #cz i.t", f"{S} add #j i.t 112",
      f"execute unless score #i i.t matches 0..223 run return 0", f"execute unless score #j i.t matches 0..223 run return 0",
      f"{S} operation #i i.t /= #32 i.g", f"{S} operation #j i.t /= #32 i.g",
      f"{S} operation #idx i.t = #j i.t", f"{S} operation #idx i.t *= #7 i.g", f"{S} operation #idx i.t += #i i.t"]
GC += [f"execute if score #idx i.t matches {k} if score @s i.p{k} matches 1 run {S} set #ok i.t 1" for k in range(49)]
fn("ile/garde_calc", GC)
fn("ile/aventure", ["tag @s add ind.adv", "gamemode adventure @s"])
fn("ile/survie", ["tag @s remove ind.adv", "gamemode survival @s"])
fn("ile/vide", [f"execute unless score @s i.ile matches 0.. run return run function {NS}:ile/retour",
                f"{S} operation #n i.t = @s i.ile", f"function {NS}:ile/tp", say("Rattrapé au-dessus du vide !", "gray")])
# hors de l'Archipel : on rend le mode survie si on l'avait retiré
fn("ile/hors", ["tag @s remove ind.adv", "execute if entity @s[gamemode=adventure] run gamemode survival @s"])

# ---------------------------------------------------------------- collisions : barrières invisibles dans l'emprise des machines
# et des bâtiments (27/11/2026). Un peu plus petites que la zone de clic (entité interaction) pour que le clic droit passe.
# Posées toutes les 5 s autour des joueurs de l'Archipel, jamais sur un joueur (rien à moins de 4 blocs).
fn("ile/barrieres", [f"function {NS}:ile/etiquettes",
    f"execute as @e[type=minecraft:interaction,tag=ind.mi,distance=..96] at @s unless entity @a[distance=..4] run fill ~-2 ~ ~-2 ~2 ~4 ~2 minecraft:barrier replace minecraft:air",
    f"execute as @e[type=minecraft:interaction,tag=ind.bi,tag=!ind.ret,distance=..96] at @s if score @s i.mt matches 90..92 unless entity @a[distance=..4] run fill ~-2 ~ ~-2 ~1 ~4 ~1 minecraft:barrier replace minecraft:air",
    f"execute as @e[type=minecraft:interaction,tag=ind.bi,tag=!ind.ret,distance=..96] at @s if score @s i.mt matches 93 unless entity @a[distance=..3] run fill ~-1 ~ ~-1 ~ ~4 ~ minecraft:barrier replace minecraft:air"])

# ---------------------------------------------------------------- étiquettes (28/11/2026) : nom et rôle au-dessus de chaque machine et bâtiment
# posées par la passe des 5 s (ile/barrieres) là où il n'y en a pas encore : marche aussi pour les îles déjà construites.
def etiquette(titre, role, tags, h):
    return (f'summon minecraft:text_display ~ ~{h} ~ {{Tags:{json.dumps(tags)},billboard:"center",view_range:0.6f,shadow:true,'
            f'background:1426063360,line_width:200,transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.55f,0.55f,0.55f]}},brightness:{{sky:15,block:15}},'
            f'text:[{{"text":"{titre}","color":"#F7C843","bold":true}},{{"text":"\\n{role}","color":"white"}},'
            f'{{"text":"\\nclic droit","color":"gray","italic":true}}]}}')

# hauteur réelle de chaque modèle (unités de modèle, 16 = 1 bloc à l'échelle 1), pour poser l'étiquette juste au-dessus
import tempfile, sys as _sys
_sys.path.insert(0, ICI)
import modeles as _mo
_HM = {n: v[1] for n, v in _mo.exporter(tempfile.mkdtemp()).items()}
def h_lab(nom, ech):
    return round(_HM[nom] / 16 * ech + 1.0, 1)
ROLE_BAT = {90: ("NEXUS", "Ton entrepôt et ton menu principal", h_lab("nexus", BAT["nexus"][2])),
            91: ("HALLE DU MARCHÉ", "Vend ton stock, contrats du jour", h_lab("halle", BAT["halle"][2])),
            92: ("BANQUE", "Garder ou vendre, prêts", h_lab("banque", BAT["banque"][2])),
            93: ("LABORATOIRE", "Brevets : bonus permanents", h_lab("labo", BAT["labo"][2])),
            94: ("GRAND ŒUVRE", "Bureau : rangs et Grands Œuvres", h_lab("oeuvre", BAT["oeuvre"][2]))}


def role_machine(m):
    d = MACH[m]
    if d["kw"] < 0:
        return f"Énergie : +{-d['kw']} kW\\npour tes machines"
    if m == "spawner":
        return "Tue les créatures de ton spawner, garde le butin"
    noms = ", ".join(f"{mille(q)} {PROD[p][0].lower()}" for p, q in d["out"].items())
    if d.get("inp"):
        return f"Transforme {', '.join(PROD[p][0].lower() for p in d['inp'])}\\nen {noms} par heure"
    return f"Produit par heure :\\n{noms}"


ET = []
for k, m in enumerate(ML):
    fn(f"ile/etiq_m{k}", [etiquette(MACH[m]["nom"].upper(), role_machine(m), ["ind.lab", "ind.labm", "ind.lv2"], 0)])
    ET.append(f"execute as @e[type=minecraft:interaction,tag=ind.mi,distance=..96] if score @s i.mt matches {k} at @s positioned ~ ~{h_lab(m, ECH_M)} ~ "
              f"unless entity @e[type=minecraft:text_display,tag=ind.lab,distance=..2] run function {NS}:ile/etiq_m{k}")
for code, (titre, role, h) in ROLE_BAT.items():
    fn(f"ile/etiq_b{code}", [etiquette(titre, role, ["ind.lab", "ind.labb", f"ind.lb{code}"], 0)])
    ET.append(f"execute as @e[type=minecraft:interaction,tag=ind.bi,tag=!ind.ret,distance=..96] if score @s i.mt matches {code} at @s positioned ~ ~{h} ~ "
              f"unless entity @e[type=minecraft:text_display,tag=ind.lab,distance=..2] run function {NS}:ile/etiq_b{code}")
REP = [  # 28/11/2026 : le Nexus des îles déjà créées portait le code de la Halle (et donc son étiquette et son menu)
    f"execute as @e[type=minecraft:interaction,tag=ind.bi,tag=!ind.ret,distance=..96] at @s if entity @e[type=minecraft:item_display,tag=ind.b_nexus,distance=..5] run {S} set @s i.mt 90",
    f"execute as @e[type=minecraft:item_display,tag=ind.b_nexus,distance=..96] at @s run kill @e[type=minecraft:text_display,tag=ind.labb,tag=!ind.lb90,distance=..9]",
    # portail de retour : les blocs avaient été effacés par le chantier de la parcelle
    "execute as @e[type=minecraft:interaction,tag=ind.ret,distance=..96] at @s run setblock ~ ~-1 ~ minecraft:gold_block keep",
    "execute as @e[type=minecraft:interaction,tag=ind.ret,distance=..96] at @s run fill ~ ~ ~ ~ ~1 ~ minecraft:crying_obsidian replace minecraft:air"]
REP += ["kill @e[type=minecraft:text_display,tag=ind.labm,tag=!ind.lv2,distance=..96]",
        "execute as @e[type=minecraft:text_display,tag=ind.rett,distance=..96] run data merge entity @s {transformation:{scale:[0.55f,0.55f,0.55f]}}",
        "execute as @e[type=minecraft:text_display,tag=ind.lab,distance=..96] run data merge entity @s {transformation:{scale:[0.55f,0.55f,0.55f]}}",
        f"execute as @e[type=minecraft:interaction,tag=ind.mi,tag=!ind.t3,distance=..96] at @s run function {NS}:tube/refaire"]
fn("ile/etiquettes", REP + ET)

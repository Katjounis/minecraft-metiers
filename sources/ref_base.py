# -*- coding: utf-8 -*-
# Refonte v24, partie 1 : chargement, migration, armure 11 paliers, arc, sac à dos, grimoire, houlette, objets de la Forge.
# Ce fichier est exécuté à la fin de datapack.py (mêmes variables globales : w, wj, jobs, NS, F, PREFIX, tr...).

GLY = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "glyphes.json"), encoding="utf-8"))

def gs(name, col="white"):
    """Glyphe de la police d'icônes, en SNBT (dialogues)."""
    return f'{{text:"{GLY[name]}",font:"metiers:icones",color:"{col}",bold:false,italic:false}}'

def gj(name):
    """Glyphe de la police d'icônes, en JSON (tellraw, bossbar, équipes)."""
    return {"text": GLY[name], "font": "metiers:icones", "color": "white", "bold": False}

def add_lines(path, lines):
    p = os.path.join(ROOT, path)
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

JL = list(jobs)                     # ordre b f m c p e n x t
SEL = lambda j: f'*[minecraft:custom_data~{{metiers_outil:"{j}"}}]'
ANIM_EGG = [a for a in ANIMAUX if a not in ("hoglin",)]

# ---------------------------------------------------------------- chargement
LD = []
OBJ = ["m.ecl", "m.skin_a", "m.skt", "m.cadre", "m.bk1", "m.bk2", "m.bk3", "m.bk4", "m.bk5", "m.bdmg", "m.prtot",
       "m.tpcd", "m.tpinc", "m.tpx", "m.tpy", "m.tpz", "m.tpk", "m.blcd", "m.bscd", "m.fdcd", "m.saison", "m.colp",
       "m.sacp", "m.saco", "m.sact", "m.own", "m.ax", "m.mene", "m.arcser", "m.forgecd", "m.cadres", "m.hp",
       "m.wk", "m.wd", "m.wp", "m.cc"]
OBJ += [f"m.cd_{i}" for i in range(1, 7)]
for j in JL:
    OBJ += [f"m.cr_{j}", f"m.ceff_{j}", f"m.cfor_{j}", f"m.csag_{j}", f"m.ceco_{j}", f"m.skin_{j}"]
for t in ["a"] + JL:
    OBJ += [f"m.so_{t}{i}" for i in range(1, 7)]
LD += [f"scoreboard objectives add {o} dummy" for o in OBJ]
STATS = {"s.cos": "minecraft.used:minecraft.carrot_on_a_stick", "s.pick": "minecraft.used:minecraft.netherite_pickaxe",
         "s.bow": "minecraft.used:minecraft.bow", "s.jump": "minecraft.custom:minecraft.jump",
         "s.hurt": "minecraft.custom:minecraft.damage_taken", "s.hit": "minecraft.custom:minecraft.damage_dealt",
         "s.seed": "minecraft.used:minecraft.wheat_seeds", "s.seedc": "minecraft.used:minecraft.carrot",
         "s.seedp": "minecraft.used:minecraft.potato", "s.seedb": "minecraft.used:minecraft.beetroot_seeds",
         "s.kills": "minecraft.custom:minecraft.mob_kills"}
STATS.update({f"s.egg_{a}": f"minecraft.used:minecraft.{a}_spawn_egg" for a in ANIM_EGG})
LD += [f"scoreboard objectives add {o} {c}" for o, c in STATS.items()]
for c in (5, 6, 8, 10, 12, 16, 20, 24, 30, 40, 54, 60, 100, 120, 240, 600, 1200, 4800):
    LD.append(f"scoreboard players set #{c} m.const {c}")
LD += ["bossbar set metiers:heure color pink", "bossbar set metiers:boss style progress",
       "scoreboard players add #semaine m.defi 0", "scoreboard players add #coll m.defi 0"]
w(F + "refonte/load.mcfunction", "\n".join(LD))

wj(f"data/{NS}/tags/block/vide.json", {"values": ["minecraft:air", "minecraft:cave_air", "minecraft:void_air", "minecraft:water",
                                                  "minecraft:lava", "minecraft:light", "minecraft:short_grass", "minecraft:tall_grass"]})
wj(f"data/{NS}/tags/block/marteau_exclu.json", {"values": ["minecraft:obsidian", "minecraft:crying_obsidian", "minecraft:respawn_anchor",
                                                          "minecraft:reinforced_deepslate", "minecraft:ender_chest", "minecraft:spawner",
                                                          "minecraft:trial_spawner", "minecraft:vault", "minecraft:enchanting_table"]})

# ---------------------------------------------------------------- migration v24
MG = ["tag @s add metiers.v24"]
for j in JL:
    MG += [f"tag @s remove metiers.sk.{j}{k}" for k in range(1, 7)]
    MG += [f"scoreboard players set @s m.{j}_spent 0", f"advancement revoke @s from {NS}:{j}/competence_1"]
    for k in range(1, 11):
        MG.append(f"execute if score @s m.{j}_pal matches {k}.. run scoreboard players add @s m.cr_{j} {CRIST[k]}")
for j in JL:
    MG.append(f"execute if items entity @s container.* {SEL(j)} run function {NS}:{j}/outil_donner")
    MG.append(f"execute if items entity @s armor.* {SEL(j)} run function {NS}:{j}/outil_donner")
    MG.append(f"execute if items entity @s weapon.offhand {SEL(j)} run function {NS}:{j}/outil_donner")
MG += [f"execute if items entity @s armor.* {ASEL} run tag @s add metiers.avait_armure",
       f"clear @s {ASEL}",
       "scoreboard players set @s m.arm 0", "tag @s add metiers.arm2",
       f"function {NS}:armure/check",
       "tag @s remove metiers.avait_armure",
       tr("Grosse mise à jour des métiers ! Tes points de compétence sont rendus (les arbres ont changé), tes récompenses de palier passées sont converties en cristaux pour la Forge, et tes outils et ton armure ont leur nouvelle apparence. Touche G pour tout voir.", "gold")]
w(F + "refonte/migration.mcfunction", "\n".join(MG))

# ---------------------------------------------------------------- armure des Guildes : 11 paliers (m.arm = palier + 1)
ARM_NOM = ["Diamant", "Diamant forgé", "Netherite", "Netherite épineuse", "Netherite d'améthyste", "Netherite de braise",
           "Netherite rubis", "Netherite runique", "Netherite du Vide", "Mythique", "Céleste"]
ARM_DE = ["de Diamant", "de Diamant forgé", "de Netherite", "de Netherite épineuse", "de Netherite d'améthyste",
          "de Netherite de braise", "de Netherite rubis", "de Netherite runique", "de Netherite du Vide", "Mythique", "Céleste"]
ARM_COL = ["#33C4CB", "#8CEFED", "#9A8790", "#C83A3A", "#B787EC", "#FF8A2E", "#FF3030", "#2FE6FF", "#8A3CFF", "#5FF5DC", "#FFF4D2"]
ARM_SEUIL = [30, 60, 100, 150, 210, 280, 360, 450, 560, 700, 850]
ARMV = {"head": [3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5], "chest": [8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10],
        "legs": [6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8], "feet": [3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5]}
TOUGHV = [2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5]
KBV = [0, 0, 0.1, 0.1, 0.1, 0.1, 0.15, 0.15, 0.15, 0.2, 0.2]
VIEV = [0, 0, 0, 0, 2, 2, 2, 4, 4, 6, 6]
ARM_BON = {2: "Hâte I", 4: "Vitesse I", 6: "Résistance I", 8: "Régénération I", 10: "Force I"}

def piece_item2(piece, slot, nom, p):
    mods = [f'{{type:"minecraft:armor",amount:{ARMV[slot][p]},id:"metiers:g_{slot}_a",operation:"add_value",slot:"{slot}"}}',
            f'{{type:"minecraft:armor_toughness",amount:{TOUGHV[p]},id:"metiers:g_{slot}_t",operation:"add_value",slot:"{slot}"}}']
    if KBV[p]:
        mods.append(f'{{type:"minecraft:knockback_resistance",amount:{KBV[p]},id:"metiers:g_{slot}_k",operation:"add_value",slot:"{slot}"}}')
    if slot == "chest" and VIEV[p]:
        mods.append(f'{{type:"minecraft:max_health",amount:{VIEV[p]},id:"metiers:g_vie",operation:"add_value",slot:"chest"}}')
    ench = {"protection": min(4, 2 + p // 3), "unbreaking": 3}
    if slot == "feet": ench["feather_falling"] = min(4, 1 + p // 3)
    if slot == "head": ench["respiration"] = min(3, 1 + p // 4)
    e = ",".join(f'"minecraft:{a}":{v}' for a, v in ench.items())
    bon = ", ".join(v for k, v in ARM_BON.items() if k <= p) or "aucun bonus de set avant le palier 2"
    base = "diamond" if p <= 1 else "netherite"
    comps = [f"minecraft:enchantments={{{e}}}",
             f'minecraft:custom_name={{text:"{nom} {ARM_DE[p]}",color:"{ARM_COL[p]}",bold:true,italic:false}}',
             f'minecraft:lore=[{{text:"Armure des Guildes, palier {p}/10",color:"gray",italic:false}},{{text:"Set complet : {bon}",color:"gold",italic:false}}]',
             f"minecraft:custom_data={{metiers_armure:1b,palier:{p},o:$(o),s:$(s)}}",
             (f'minecraft:item_model="metiers:heaume_{p}"' if slot == "head" else f'minecraft:item_model="metiers:guilde_{piece}_{p}"'),
             'minecraft:custom_model_data={strings:["$(skin)"]}',
             (f'minecraft:equippable={{slot:"head",equip_sound:"minecraft:item.armor.equip_netherite"}}' if slot == "head" else
              f'minecraft:equippable={{slot:"{slot}",asset_id:"metiers:guilde_{p}$(askin)",equip_sound:"minecraft:item.armor.equip_netherite"}}'),
             "minecraft:attribute_modifiers=[" + ",".join(mods) + "]",
             "minecraft:unbreakable={}", "minecraft:enchantment_glint_override=false",
             'minecraft:rarity="epic"', "minecraft:repair_cost=1000", "!minecraft:repairable"]
    return f"minecraft:{base}_{piece}[{','.join(comps)}]"

AD = []
for p in range(11):
    for piece, slot, nom, _ in PIECES:
        it = piece_item2(piece, slot, nom, p)
        AD.append(f"$execute if score @s m.arm matches {p + 1} if entity @s[tag=metiers.a_{slot}] run item replace entity @s armor.{slot} with {it}")
        AD.append(f"$execute if score @s m.arm matches {p + 1} unless entity @s[tag=metiers.a_{slot}] run give @s {it}")
w(F + "armure/donner_m.mcfunction", "\n".join(AD))
ASK = ['data modify storage metiers:tmp skin set value ""', 'data modify storage metiers:tmp askin set value ""']
for i, sk in enumerate(SKIN_IDS, 1):
    ASK += [f'execute if score @s m.skin_a matches {i} run data modify storage metiers:tmp skin set value "{sk}"',
            f'execute if score @s m.skin_a matches {i} run data modify storage metiers:tmp askin set value "_{sk}"']
w(F + "armure/donner.mcfunction", "\n".join(
    [f"tag @s remove metiers.a_{sl}" for _, sl, _, _ in PIECES] +
    [f"execute if items entity @s armor.{sl} {ASEL} run tag @s add metiers.a_{sl}" for _, sl, _, _ in PIECES] +
    [f"execute if items entity @s armor.{sl} {ASEL} run item replace entity @s armor.{sl} with minecraft:air" for _, sl, _, _ in PIECES] + [
    f"clear @s {ASEL}", "scoreboard players add @s m.aser 1",
    f"execute store result storage {NS}:tmp o int 1 run scoreboard players get @s m.id",
    f"execute store result storage {NS}:tmp s int 1 run scoreboard players get @s m.aser"] + ASK + [
    f"function {NS}:armure/donner_m with storage {NS}:tmp"] + [f"tag @s remove metiers.a_{sl}" for _, sl, _, _ in PIECES] + [
    "playsound minecraft:item.armor.equip_netherite master @s ~ ~ ~ 1 0.8",
    "particle minecraft:totem_of_undying ~ ~1 ~ 0.4 1 0.4 0.3 60"]))
AC = ["scoreboard players add @s m.arm 0", "tag @s add metiers.arm2", "scoreboard players set @s m.tmp 0"]
AC += [f"execute if score @s m.total matches {ARM_SEUIL[p]}.. run scoreboard players set @s m.tmp {p + 1}" for p in range(11)]
AC += ["execute if score @s m.tmp <= @s m.arm run return 0", "scoreboard players operation @s m.arm = @s m.tmp"]
AC += [f'execute if score @s m.arm matches {p + 1} unless entity @s[tag=metiers.avait_armure] run tellraw @a ' + PREFIX +
       f',{{"selector":"@s","color":"white"}},{{"text":" obtient l\'Armure des Guildes : ","color":"gray"}},{{"text":"{ARM_NOM[p]}","color":"{ARM_COL[p]}","bold":true}}]' for p in range(11)]
AC += [f'function {NS}:appel {{f:"armure/donner"}}', "execute unless entity @s[tag=metiers.avait_armure] as @a at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 0.6 1.3"]
w(F + "armure/check.mcfunction", "\n".join(AC))
w(F + "armure/recup.mcfunction", "\n".join([
    "scoreboard players add @s m.arm 0",
    f"execute if score @s m.arm matches 0 run return run {tr('Ton armure se débloque à 30 points de score (somme de tes niveaux).', 'red')}",
    "scoreboard players operation @s m.tmp = @s m.acd", "scoreboard players operation @s m.tmp /= #60 m.const",
    "scoreboard players operation @s m.tmp /= #2 m.const", "scoreboard players add @s m.tmp 1",
    'execute if score @s m.acd matches 1.. run return run tellraw @s ' + PREFIX + ',{"text":"Patiente encore ","color":"red"},{"score":{"name":"@s","objective":"m.tmp"},"color":"yellow"},{"text":" min.","color":"red"}]',
    "scoreboard players set @s m.acd 1200", f'function {NS}:appel {{f:"armure/donner"}}',
    tr("Ton Armure des Guildes est remise à neuf.", "green")]))
AB = [f"execute unless items entity @s armor.{s} {ASEL} run return 0" for _, s, _, _ in PIECES]
AB += ["execute if score @s m.arm matches 3.. run effect give @s minecraft:haste 2 0 true",
       "execute if score @s m.arm matches 5.. run effect give @s minecraft:speed 2 0 true",
       "execute if score @s m.arm matches 7.. run effect give @s minecraft:resistance 2 0 true",
       "execute if score @s m.arm matches 9.. run effect give @s minecraft:regeneration 3 0 true",
       "execute if score @s m.arm matches 11.. run effect give @s minecraft:strength 2 0 true"]
w(F + "armure/bonus.mcfunction", "\n".join(AB))
AMN = ["scoreboard players add @s m.arm 0", f"execute store result storage {NS}:arm score int 1 run scoreboard players get @s m.total",
       f'data modify storage {NS}:arm nom set value "Pas encore débloquée"', f'data modify storage {NS}:arm col set value "gray"',
       f'data modify storage {NS}:arm next set value "Débloque-la à {ARM_SEUIL[0]} points"', f'data modify storage {NS}:arm model set value "heaume_0"']
for p in range(11):
    nxt = f"Prochain palier à {ARM_SEUIL[p + 1]} points" if p < 10 else "Palier maximum atteint"
    AMN += [f'execute if score @s m.arm matches {p + 1} run data modify storage {NS}:arm nom set value "{ARM_NOM[p]} (palier {p}/10)"',
            f'execute if score @s m.arm matches {p + 1} run data modify storage {NS}:arm col set value "{ARM_COL[p]}"',
            f'execute if score @s m.arm matches {p + 1} run data modify storage {NS}:arm next set value "{nxt}"',
            f'execute if score @s m.arm matches {p + 1} run data modify storage {NS}:arm model set value "heaume_{p}"']
AMN.append(f"function {NS}:armure/menu_dialog with storage {NS}:arm")
w(F + "armure/menu.mcfunction", "\n".join(AMN))
paliers = "\\n".join(f"{p}. {ARM_NOM[p]} : {ARM_SEUIL[p]} pts" + (f", set complet + {ARM_BON[p]}" if p in ARM_BON else "") for p in range(11))
w(F + "armure/menu_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Armure des Guildes",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:item",item:{id:"minecraft:paper",components:{"minecraft:item_model":"metiers:$(model)"}},show_decorations:false,show_tooltip:false,'
  'description:{width:240,contents:[{text:"$(nom)\\n",color:"$(col)",bold:true},{text:"Score : $(score) points\\n$(next)",color:"white",bold:false}]}},'
  '{type:"minecraft:plain_message",width:320,contents:['
  f'{{text:"{paliers}\\n\\n",color:"gray"}},'
  '{text:"Ton score est la somme de tes niveaux (+100 par prestige). Les bonus de set se cumulent quand tu portes les 4 pièces.",color:"dark_gray"}]}],'
  'actions:[{label:{text:"Récupérer mon armure",color:"green"},width:200,tooltip:{text:"Une fois toutes les 10 minutes."},action:{type:"run_command",command:"trigger metiers set 8"}}],'
  'columns:1,exit_action:{label:"Retour",width:150,action:{type:"run_command",command:"trigger metiers set 1"}}}')

# ---------------------------------------------------------------- arc évolutif du Chasseur
PW = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5]
def arc_item(k):
    ench = {"power": PW[k]}
    if k >= 4: ench["infinity"] = 1
    if k >= 6: ench["punch"] = 1 if k < 9 else 2
    if k >= 7: ench["flame"] = 1
    if k < 5: ench["unbreaking"] = 3
    e = ",".join(f'"minecraft:{a}":{v}' for a, v in ench.items())
    nom = "Arc du Dieu de la Chasse" if k == 10 else f"Arc {DE[k]}"
    comps = [f"minecraft:enchantments={{{e}}}", f'minecraft:custom_name={{text:"{nom}",color:"{tier_style("c", k)["color"]}",bold:true,italic:false}}',
             f'minecraft:lore=[{{text:"Arc du Chasseur",color:"red",italic:false}},{{text:"Palier {k}/10, il évolue avec ton épée",color:"gray",italic:false}}]',
             f'minecraft:item_model="metiers:arc_{k}"', f"minecraft:custom_data={{metiers_arc:1b,o:$(o)}}",
             "minecraft:enchantment_glint_override=false", "minecraft:repair_cost=1000", 'minecraft:rarity="epic"']
    if k >= 5: comps.append("minecraft:unbreakable={}")
    return f"minecraft:bow[{','.join(comps)}] 1"
ARCSEL = "*[minecraft:custom_data~{metiers_arc:1b}]"
AR = []
for k in range(11):
    AR += [f"$execute if score @s m.c_out matches {k} if entity @s[tag=metiers.arc_main] run item replace entity @s weapon.mainhand with {arc_item(k)}",
           f"$execute if score @s m.c_out matches {k} unless entity @s[tag=metiers.arc_main] run give @s {arc_item(k)}"]
w(F + "c/arc_donner_m.mcfunction", "\n".join(AR))
w(F + "c/arc_donner.mcfunction", "\n".join([
    "tag @s remove metiers.arc_main", f"execute if items entity @s weapon.mainhand {ARCSEL} run tag @s add metiers.arc_main",
    f"clear @s {ARCSEL}", f"execute store result storage {NS}:tmp o int 1 run scoreboard players get @s m.id",
    f"function {NS}:c/arc_donner_m with storage {NS}:tmp", "tag @s remove metiers.arc_main"]))
w(F + "c/arc_recup.mcfunction", "\n".join([
    f"execute if items entity @s container.* {ARCSEL} run return run {tr('Tu as déjà ton arc de Chasseur sur toi.')}",
    f"function {NS}:c/arc_donner", tr("Voici ton arc de Chasseur. Il évolue en même temps que ton épée.", "green")]))
add_lines(F + "c/outil_monte.mcfunction", [f"execute if items entity @s container.* {ARCSEL} run function {NS}:c/arc_donner"])

# ---------------------------------------------------------------- objets de la Forge
FORGE_IT = {
    "marteau": ("netherite_pickaxe", "Marteau du Mineur", "forge_marteau", "gray", "Creuse en 3x3 dans la direction visée.",
                ['minecraft:enchantments={"minecraft:efficiency":5,"minecraft:unbreaking":3}', "minecraft:unbreakable={}"]),
    "faux": ("netherite_hoe", "Faux du Fermier", "forge_faux", "green", "Clic droit sur des cultures : récolte et replante en 5x5.",
             ["minecraft:unbreakable={}", 'minecraft:consumable={consume_seconds:100000,animation:"none",has_consume_particles:false,sound:"minecraft:intentionally_empty"}']),
    "arc3": ("bow", "Arc à triple tir", "forge_arc3", "red", "Chaque tir lance trois flèches en éventail.",
             ['minecraft:enchantments={"minecraft:power":4}', "minecraft:unbreakable={}"]),
    "lasso": ("carrot_on_a_stick", "Lasso de l'Éleveur", "forge_lasso", "light_purple", "Clic droit en visant un animal : il est capturé. Pose l'œuf pour le relâcher.",
              ["minecraft:unbreakable={}"]),
    "parchemin": ("carrot_on_a_stick", "Parchemin de transfert", "forge_parchemin", "dark_purple",
                  "Objet enchanté en main secondaire, clic droit : ses enchantements passent sur un livre.", []),
    "aimant": ("paper", "Aimant à objets", "forge_aimant", "aqua", "En main secondaire : attire les objets au sol à 8 blocs.", []),
    "cape": ("elytra", "Cape-planeur", "forge_cape", "blue", "Se porte au torse : vol plané sans fusées.", ["minecraft:unbreakable={}"]),
}
def forge_give(key):
    iid, nom, model, col, desc, extra = FORGE_IT[key]
    comps = [f'minecraft:custom_name={{text:"{nom}",color:"{col}",bold:true,italic:false}}',
             f'minecraft:lore=[{{text:"{desc}",color:"gray",italic:false}},{{text:"Objet de la Forge",color:"gold",italic:false}}]',
             f'minecraft:item_model="metiers:{model}"', f'minecraft:custom_data={{forge:"{key}"}}', "minecraft:max_stack_size=1",
             'minecraft:rarity="epic"', "minecraft:repair_cost=1000"] + extra
    return f"minecraft:{iid}[{','.join(comps)}] 1"
for key in FORGE_IT:
    w(F + f"forge/donner_{key}.mcfunction", f"give @s {forge_give(key)}")
FSEL = lambda key: f'*[minecraft:custom_data~{{forge:"{key}"}}]'

# faux : clic droit détecté par un progrès « using_item »
wj(f"data/{NS}/advancement/forge/faux.json", {"criteria": {"u": {"trigger": "minecraft:using_item", "conditions": {
    "item": {"items": "minecraft:netherite_hoe", "predicates": {"minecraft:custom_data": "{forge:\"faux\"}"}}}}},
    "rewards": {"function": f"{NS}:forge/faux"}})
CROPS_AGE = [("wheat", 7), ("carrots", 7), ("potatoes", 7), ("beetroots", 3), ("nether_wart", 3)]
FX = [f"advancement revoke @s only {NS}:forge/faux", "execute if score @s m.forgecd matches 1.. run return 0", "scoreboard players set @s m.forgecd 2"]
for dx in range(-2, 3):
    for dz in range(-2, 3):
        FX.append(f"execute positioned ~{dx} ~ ~{dz} run function {NS}:forge/faux_bloc")
FX += ["playsound minecraft:item.hoe.till master @s ~ ~ ~ 1 0.8", "particle minecraft:sweep_attack ~ ~0.5 ~ 1.5 0.2 1.5 0 6"]
w(F + "forge/faux.mcfunction", "\n".join(FX))
FB = []
for dy in (0, -1, 1):
    for c, age in CROPS_AGE:
        FB += [f"execute positioned ~ ~{dy} ~ if block ~ ~ ~ minecraft:{c}[age={age}] run loot spawn ~ ~0.5 ~ mine ~ ~ ~ minecraft:netherite_hoe",
               f"execute positioned ~ ~{dy} ~ if block ~ ~ ~ minecraft:{c}[age={age}] run setblock ~ ~ ~ minecraft:{c}[age=0]"]
w(F + "forge/faux_bloc.mcfunction", "\n".join(FB))

# marteau : on mémorise le bloc visé à chaque tick, puis on casse le 3x3 quand la pioche sert
MT = ["scoreboard players operation #pid m.tmp = @s m.id",
      "scoreboard players set #has m.tmp 0",
      "execute as @e[type=minecraft:marker,tag=metiers.mvise] if score @s m.own = #pid m.tmp run scoreboard players set #has m.tmp 1",
      f"execute if score #has m.tmp matches 0 run summon minecraft:marker ~ ~ ~ {{Tags:[\"metiers.mvise\",\"metiers.mnew\"]}}",
      "scoreboard players operation @e[type=minecraft:marker,tag=metiers.mnew] m.own = #pid m.tmp", "tag @e[tag=metiers.mnew] remove metiers.mnew",
      "execute if score @s s.pick matches 1.. as @e[type=minecraft:marker,tag=metiers.mvise] if score @s m.own = #pid m.tmp at @s run function metiers:forge/marteau_casser",
      "scoreboard players set @s s.pick 0",
      "execute store result score #pitch m.tmp run data get entity @s Rotation[1]",
      "execute store result score #yaw m.tmp run data get entity @s Rotation[0]",
      "scoreboard players set #ax m.tmp 2",
      "execute if score #yaw m.tmp matches -135..-45 run scoreboard players set #ax m.tmp 1",
      "execute if score #yaw m.tmp matches 45..135 run scoreboard players set #ax m.tmp 1",
      "execute if score #pitch m.tmp matches 45.. run scoreboard players set #ax m.tmp 0",
      "execute if score #pitch m.tmp matches ..-45 run scoreboard players set #ax m.tmp 0",
      "scoreboard players set #pas m.tmp 0",
      f"execute anchored eyes positioned ^ ^ ^ run function {NS}:forge/marteau_rayon"]
w(F + "forge/marteau.mcfunction", "\n".join(MT))
w(F + "forge/marteau_rayon.mcfunction", f"""
scoreboard players add #pas m.tmp 1
execute unless block ~ ~ ~ #{NS}:vide align xyz positioned ~0.5 ~0.5 ~0.5 as @e[type=minecraft:marker,tag=metiers.mvise] if score @s m.own = #pid m.tmp run return run function {NS}:forge/marteau_poser
execute if score #pas m.tmp matches ..50 positioned ^ ^ ^0.1 run function {NS}:forge/marteau_rayon
""")
w(F + "forge/marteau_poser.mcfunction", "tp @s ~ ~ ~\nscoreboard players operation @s m.ax = #ax m.tmp")
CS = []
for ax, offs in ((0, [(dx, 0, dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1)]), (1, [(0, dy, dz) for dy in (-1, 0, 1) for dz in (-1, 0, 1)]),
                 (2, [(dx, dy, 0) for dx in (-1, 0, 1) for dy in (-1, 0, 1)])):
    for (dx, dy, dz) in offs:
        if (dx, dy, dz) == (0, 0, 0): continue
        CS.append(f"execute if score @s m.ax matches {ax} positioned ~{dx} ~{dy} ~{dz} if block ~ ~ ~ #minecraft:mineable/pickaxe unless block ~ ~ ~ #{NS}:marteau_exclu run setblock ~ ~ ~ minecraft:air destroy")
w(F + "forge/marteau_casser.mcfunction", "\n".join(CS))

# arc à triple tir : deux flèches en plus, tirées à ±10°
w(F + "forge/arc3.mcfunction", f"""
scoreboard players set @s s.bow 0
execute anchored eyes rotated ~10 ~ run function {NS}:forge/arc3_fleche
execute anchored eyes rotated ~-10 ~ run function {NS}:forge/arc3_fleche
playsound minecraft:entity.arrow.shoot master @a ~ ~ ~ 0.8 1.3
""")
w(F + "forge/arc3_fleche.mcfunction", f"""
summon minecraft:marker ^ ^ ^ {{Tags:["metiers.a0"]}}
summon minecraft:marker ^ ^ ^3 {{Tags:["metiers.a1"]}}
execute store result score #x0 m.tmp run data get entity @e[tag=metiers.a0,limit=1] Pos[0] 1000
execute store result score #y0 m.tmp run data get entity @e[tag=metiers.a0,limit=1] Pos[1] 1000
execute store result score #z0 m.tmp run data get entity @e[tag=metiers.a0,limit=1] Pos[2] 1000
execute store result score #x1 m.tmp run data get entity @e[tag=metiers.a1,limit=1] Pos[0] 1000
execute store result score #y1 m.tmp run data get entity @e[tag=metiers.a1,limit=1] Pos[1] 1000
execute store result score #z1 m.tmp run data get entity @e[tag=metiers.a1,limit=1] Pos[2] 1000
scoreboard players operation #x1 m.tmp -= #x0 m.tmp
scoreboard players operation #y1 m.tmp -= #y0 m.tmp
scoreboard players operation #z1 m.tmp -= #z0 m.tmp
summon minecraft:arrow ^ ^ ^1 {{Tags:["metiers.a2"],pickup:0b,damage:2.5d}}
execute store result entity @e[tag=metiers.a2,limit=1] Motion[0] double 0.001 run scoreboard players get #x1 m.tmp
execute store result entity @e[tag=metiers.a2,limit=1] Motion[1] double 0.001 run scoreboard players get #y1 m.tmp
execute store result entity @e[tag=metiers.a2,limit=1] Motion[2] double 0.001 run scoreboard players get #z1 m.tmp
data modify entity @e[tag=metiers.a2,limit=1] Owner set from entity @s UUID
tag @e[tag=metiers.a2] remove metiers.a2
kill @e[type=minecraft:marker,tag=metiers.a0]
kill @e[type=minecraft:marker,tag=metiers.a1]
""")

# lasso : capture de l'animal visé dans un œuf
LS = ["scoreboard players set #pas m.tmp 0", "tag @s add metiers.lanceur",
      f"execute anchored eyes positioned ^ ^ ^ run function {NS}:forge/lasso_rayon", "tag @s remove metiers.lanceur"]
w(F + "forge/lasso.mcfunction", "\n".join(LS))
w(F + "forge/lasso_rayon.mcfunction", f"""
scoreboard players add #pas m.tmp 1
execute as @e[type=#{NS}:animaux,distance=..1.2,limit=1,sort=nearest] run return run function {NS}:forge/lasso_prendre
execute if score #pas m.tmp matches ..40 positioned ^ ^ ^0.1 run function {NS}:forge/lasso_rayon
""")
LP = ["summon minecraft:item ~ ~ ~ {Tags:[\"metiers.lasso_oeuf\"],PickupDelay:32767s,Item:{id:\"minecraft:pig_spawn_egg\",count:1}}",
      "data modify entity @e[tag=metiers.lasso_oeuf,limit=1] Item.components.\"minecraft:entity_data\" set from entity @s",
      "data remove entity @e[tag=metiers.lasso_oeuf,limit=1] Item.components.\"minecraft:entity_data\".UUID",
      "data remove entity @e[tag=metiers.lasso_oeuf,limit=1] Item.components.\"minecraft:entity_data\".Pos",
      "data remove entity @e[tag=metiers.lasso_oeuf,limit=1] Item.components.\"minecraft:entity_data\".Motion",
      "data remove entity @e[tag=metiers.lasso_oeuf,limit=1] Item.components.\"minecraft:entity_data\".leash"]
for a in ANIM_EGG:
    LP += [f'execute if entity @s[type=minecraft:{a}] run data modify entity @e[tag=metiers.lasso_oeuf,limit=1] Item.id set value "minecraft:{a}_spawn_egg"',
           f'execute if entity @s[type=minecraft:{a}] run data modify entity @e[tag=metiers.lasso_oeuf,limit=1] Item.components."minecraft:entity_data".id set value "minecraft:{a}"']
LP += ['data modify entity @e[tag=metiers.lasso_oeuf,limit=1] Item.components."minecraft:custom_name" set value {text:"Lasso (animal capturé)",color:"light_purple",bold:true,italic:false}',
       'data modify entity @e[tag=metiers.lasso_oeuf,limit=1] Item.components."minecraft:item_model" set value "metiers:forge_lasso"',
       'data modify entity @e[tag=metiers.lasso_oeuf,limit=1] Item.components."minecraft:custom_data" set value {forge:"lasso_plein"}',
       'data modify entity @e[tag=metiers.lasso_oeuf,limit=1] Item.components."minecraft:enchantment_glint_override" set value 1b',
       "execute as @a[tag=metiers.lanceur,limit=1] run item replace entity @s weapon.mainhand from entity @e[tag=metiers.lasso_oeuf,limit=1] contents",
       "kill @e[tag=metiers.lasso_oeuf]",
       "execute as @a[tag=metiers.lanceur] run tag @s add metiers.lasso_plein",
       "particle minecraft:cloud ~ ~0.5 ~ 0.3 0.3 0.3 0.02 15", "playsound minecraft:entity.leash_knot.place master @a ~ ~ ~ 1 1",
       "tp @s ~ -400 ~", "kill @s"]
w(F + "forge/lasso_prendre.mcfunction", "\n".join(LP))
LR = ["scoreboard players set #egg m.tmp 0"]
LR += [f"scoreboard players operation #egg m.tmp += @s s.egg_{a}" for a in ANIM_EGG]
LR += [f"scoreboard players set @s s.egg_{a} 0" for a in ANIM_EGG]
LR += [f"execute if score #egg m.tmp matches 1.. if entity @s[tag=metiers.lasso_plein] unless items entity @s container.* {FSEL('lasso_plein')} run function {NS}:forge/lasso_rendre"]
w(F + "forge/lasso_retour.mcfunction", "\n".join(LR))
w(F + "forge/lasso_rendre.mcfunction", f"tag @s remove metiers.lasso_plein\nfunction {NS}:forge/donner_lasso")

# parchemin : transfert des enchantements de la main secondaire vers un livre
w(F + "forge/parchemin.mcfunction", f"""
execute unless items entity @s weapon.offhand *[minecraft:enchantments] run return run {tr("Mets un objet enchanté dans ta main secondaire.", "red")}
execute if data entity @s equipment.offhand.components."minecraft:custom_data".metiers_outil run return run {tr("Impossible sur un objet de métier.", "red")}
execute unless data entity @s equipment.offhand.components."minecraft:enchantments" run return run {tr("Cet objet n'a pas d'enchantement à transférer.", "red")}
summon minecraft:item ~ ~ ~ {{Tags:["metiers.livre"],PickupDelay:32767s,Item:{{id:"minecraft:enchanted_book",count:1}}}}
data modify entity @e[tag=metiers.livre,limit=1] Item.components."minecraft:stored_enchantments" set from entity @s equipment.offhand.components."minecraft:enchantments"
item modify entity @s weapon.offhand {{function:"minecraft:set_components",type:"minecraft:set_components",components:{{"!minecraft:enchantments":{{}}}}}}
item replace entity @s weapon.mainhand from entity @e[tag=metiers.livre,limit=1] contents
kill @e[tag=metiers.livre]
playsound minecraft:block.enchantment_table.use master @s ~ ~ ~ 1 1.4
particle minecraft:enchant ~ ~1 ~ 0.4 0.6 0.4 0.5 60
{tr("Les enchantements sont passés sur le livre.", "light_purple")}
""")

# ---------------------------------------------------------------- houlette de l'Éleveur : les animaux proches te suivent
HN = [2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 8]
HU = ["scoreboard players operation #pid m.tmp = @s m.id", "scoreboard players set #n m.tmp 0",
      f"execute as @e[type=#{NS}:animaux,distance=..48] if score @s m.own = #pid m.tmp run scoreboard players add #n m.tmp 1",
      f"execute if score #n m.tmp matches 1.. as @e[type=#{NS}:animaux,distance=..48] if score @s m.own = #pid m.tmp run scoreboard players reset @s m.own",
      f"execute if score #n m.tmp matches 1.. run return run {tr('Les animaux ne te suivent plus.')}",
      "scoreboard players set #n m.tmp 0"]
for k in range(11):
    HU.append(f"execute if score @s m.e_out matches {k} run scoreboard players set #max m.tmp {HN[k]}")
HU += [f"function {NS}:e/houlette_boucle",
       f'tellraw @s {PREFIX},{{"score":{{"name":"#n","objective":"m.tmp"}},"color":"yellow"}},{{"text":" animaux te suivent. Clic droit à nouveau pour les libérer.","color":"light_purple"}}]',
       "playsound minecraft:block.note_block.bell master @a ~ ~ ~ 0.8 1.6"]
w(F + "e/houlette.mcfunction", "\n".join(HU))
wj(f"data/{NS}/predicate/suit_moi.json", {"type": "minecraft:entity_scores", "entity": "this", "scores": {"m.own": {"min": 1}}})
w(F + "e/houlette_boucle.mcfunction", "\n".join([
    "execute if score #n m.tmp >= #max m.tmp run return 0",
    f"execute unless entity @e[type=#{NS}:animaux,distance=..10,predicate=!{NS}:suit_moi] run return 0",
    f"execute as @e[type=#{NS}:animaux,distance=..10,sort=nearest,limit=1,predicate=!{NS}:suit_moi] run function {NS}:e/houlette_prendre",
    f"function {NS}:e/houlette_boucle"]))
w(F + "e/houlette_prendre.mcfunction", "scoreboard players operation @s m.own = #pid m.tmp\nscoreboard players add #n m.tmp 1\nparticle minecraft:heart ~ ~1 ~ 0.3 0.3 0.3 0 2")
w(F + "e/houlette_suivre.mcfunction", f"""
scoreboard players operation #pid m.tmp = @s m.id
execute as @e[type=#{NS}:animaux,distance=..48] if score @s m.own = #pid m.tmp at @s unless entity @p[distance=..3] facing entity @p feet run tp @s ^ ^ ^0.28
""")

# ---------------------------------------------------------------- sac à dos de l'Explorateur
LOCK = ('{Slot:SLOTb,id:"minecraft:gray_stained_glass_pane",count:1,components:{"minecraft:custom_name":{text:"Case verrouillée",color:"gray",italic:false},'
        '"minecraft:lore":[{text:"Se débloque au niveau 50 d\'Explorateur",color:"dark_gray",italic:false}],"minecraft:custom_data":{metiers_lock:1b}}}')
PAGEB = ('{Slot:26b,id:"minecraft:arrow",count:1,components:{"minecraft:custom_name":{text:"Changer de page","color":"aqua",italic:false},'
         '"minecraft:lore":[{text:"Prends cette flèche pour passer à l\'autre page",color:"gray",italic:false}],"minecraft:custom_data":{metiers_page:1b}}}').replace('"color"', 'color')
SAC_TIER = ["", "18 cases", "27 cases", "2 pages, 52 cases"]
def sac_item(t):
    return (f'minecraft:carrot_on_a_stick[minecraft:custom_name={{text:"Sac à dos",color:"blue",bold:true,italic:false}},'
            f'minecraft:lore=[{{text:"{SAC_TIER[t]}, grandit avec ton niveau d\'Explorateur",color:"gray",italic:false}},{{text:"Clic droit, puis clic sur le coffre qui apparaît",color:"dark_gray",italic:false}}],'
            f'minecraft:item_model="metiers:sac_{t}",minecraft:custom_data={{metiers_sac:1b}},minecraft:unbreakable={{}},minecraft:max_stack_size=1,'
            f'minecraft:repair_cost=1000,minecraft:enchantment_glint_override=false] 1')
SACSEL = "*[minecraft:custom_data~{metiers_sac:1b}]"
w(F + "sac/donner.mcfunction", "\n".join([
    "scoreboard players set @s m.sact 0",
    "execute if score @s m.x_lvl matches 20.. run scoreboard players set @s m.sact 1",
    "execute if score @s m.x_lvl matches 50.. run scoreboard players set @s m.sact 2",
    "execute if score @s m.x_lvl matches 80.. run scoreboard players set @s m.sact 3",
    f"execute if score @s m.sact matches 0 run return run {tr('Le sac à dos se débloque au niveau 20 d’Explorateur.', 'red')}",
    f"clear @s {SACSEL}"] + [f"execute if score @s m.sact matches {t} run give @s {sac_item(t)}" for t in (1, 2, 3)] +
    [tr("Voici ton sac à dos. Ce que tu y ranges reste dedans, même si tu le perds : récupère-le ici.", "green")]))
add_lines(F + "x/outil_monte.mcfunction", [f"execute if items entity @s container.* {SACSEL} run function {NS}:sac/donner"])
w(F + "sac/ouvrir.mcfunction", f"""
scoreboard players operation #pid m.tmp = @s m.id
execute as @e[type=minecraft:chest_minecart,tag=metiers.sac] if score @s m.own = #pid m.tmp run function {NS}:sac/fermer
scoreboard players set @s m.sact 1
execute if score @s m.x_lvl matches 50.. run scoreboard players set @s m.sact 2
execute if score @s m.x_lvl matches 80.. run scoreboard players set @s m.sact 3
execute unless score @s m.sacp matches 1..2 run scoreboard players set @s m.sacp 1
execute if score @s m.sact matches ..2 run scoreboard players set @s m.sacp 1
execute anchored eyes positioned ^ ^-0.4 ^1.6 run summon minecraft:chest_minecart ~ ~ ~ {{Tags:["metiers.sac","metiers.sacnew"],Invulnerable:1b,NoGravity:1b,Silent:1b,CustomName:{{text:"Sac à dos",color:"blue"}}}}
scoreboard players operation @e[tag=metiers.sacnew] m.own = #pid m.tmp
scoreboard players set @e[tag=metiers.sacnew] m.tmp 0
scoreboard players set @s m.saco 1
execute as @e[tag=metiers.sacnew] run function {NS}:sac/remplir
tag @e[tag=metiers.sacnew] remove metiers.sacnew
title @s actionbar {{"text":"Clique sur le coffre pour ouvrir ton sac","color":"aqua"}}
playsound minecraft:item.bundle.drop_contents master @s ~ ~ ~ 1 0.8
""")
# le chariot lit la page du joueur (#pid) et y ajoute les cases verrouillées
w(F + "sac/remplir.mcfunction", "\n".join([
    f"execute store result storage {NS}:sac id int 1 run scoreboard players get #pid m.tmp",
    f"execute as @a if score @s m.id = #pid m.tmp store result storage {NS}:sac page int 1 run scoreboard players get @s m.sacp",
    f"execute as @a if score @s m.id = #pid m.tmp store result score #t m.tmp run scoreboard players get @s m.sact",
    "data modify entity @s Items set value []",
    f"function {NS}:sac/charger with storage {NS}:sac"] +
    [f"execute if score #t m.tmp matches 1 run data modify entity @s Items append value {LOCK.replace('SLOT', str(sl))}" for sl in range(18, 27)] +
    [f"execute if score #t m.tmp matches 3 run data modify entity @s Items append value {PAGEB}"]))
w(F + "sac/charger.mcfunction", f"$execute if data storage {NS}:sac j$(id).p$(page) run data modify entity @s Items append from storage {NS}:sac j$(id).p$(page)[]")
w(F + "sac/sauver.mcfunction", "\n".join([
    f"$data modify storage {NS}:sac j$(id).p$(page) set from entity @s Items",
    f"$data remove storage {NS}:sac j$(id).p$(page)[{{components:{{\"minecraft:custom_data\":{{metiers_lock:1b}}}}}}]",
    f"$data remove storage {NS}:sac j$(id).p$(page)[{{components:{{\"minecraft:custom_data\":{{metiers_page:1b}}}}}}]"]))
# suivi toutes les 0,5 s pendant que le sac est ouvert
w(F + "sac/suivi.mcfunction", "\n".join([
    "scoreboard players operation #pid m.tmp = @s m.id",
    f"execute store result storage {NS}:sac id int 1 run scoreboard players get @s m.id",
    f"execute store result storage {NS}:sac page int 1 run scoreboard players get @s m.sacp",
    "scoreboard players set #trouve m.tmp 0", "scoreboard players operation #t m.tmp = @s m.sact",
    f"execute as @e[type=minecraft:chest_minecart,tag=metiers.sac] if score @s m.own = #pid m.tmp run function {NS}:sac/suivi_chariot",
    "execute if score #trouve m.tmp matches 0 run scoreboard players set @s m.saco 0",
    "clear @s *[minecraft:custom_data~{metiers_lock:1b}]",
    f"execute if items entity @s container.* *[minecraft:custom_data~{{metiers_page:1b}}] run function {NS}:sac/page",
    f"execute if items entity @s player.cursor *[minecraft:custom_data~{{metiers_page:1b}}] run function {NS}:sac/page"]))
w(F + "sac/suivi_chariot.mcfunction", "\n".join([
    "scoreboard players set #trouve m.tmp 1",
    "scoreboard players add @s m.tmp 1",
    f"function {NS}:sac/sauver with storage {NS}:sac",
    f"execute unless items entity @s container.26 *[minecraft:custom_data~{{metiers_page:1b}}] if score #t m.tmp matches 3 run return 0",
    f"execute unless entity @a[distance=..6] run return run function {NS}:sac/fermer",
    f"execute if score @s m.tmp matches 240.. run return run function {NS}:sac/fermer",
    f"function {NS}:sac/reverrouiller"]))
w(F + "sac/reverrouiller.mcfunction", "\n".join(
    [f"execute as @a if score @s m.id = #pid m.tmp store result score #t m.tmp run scoreboard players get @s m.sact"] +
    [f"execute if score #t m.tmp matches 1 unless items entity @s container.{sl} *[minecraft:custom_data~{{metiers_lock:1b}}] run function {NS}:sac/case {{slot:{sl}}}" for sl in range(18, 27)]))
w(F + "sac/case.mcfunction", "\n".join([
    "$execute if items entity @s container.$(slot) * run summon minecraft:item ~ ~ ~ {Tags:[\"metiers.rendu\"],Item:{id:\"minecraft:stone\",count:1}}",
    "$execute if items entity @s container.$(slot) * run data modify entity @e[tag=metiers.rendu,limit=1] Item set from entity @s Items[{Slot:$(slot)b}]",
    "$execute if items entity @s container.$(slot) * run data remove entity @e[tag=metiers.rendu,limit=1] Item.Slot",
    "$execute if items entity @s container.$(slot) * run tp @e[tag=metiers.rendu] @p",
    "tag @e[tag=metiers.rendu] remove metiers.rendu",
    "$data remove entity @s Items[{Slot:$(slot)b}]",
    f"$data modify entity @s Items append value {LOCK.replace('SLOT', '$(slot)')}"]))
w(F + "sac/page.mcfunction", "\n".join([
    "clear @s *[minecraft:custom_data~{metiers_page:1b}]",
    "execute if score @s m.sacp matches 1 run scoreboard players set #np m.tmp 2",
    "execute if score @s m.sacp matches 2 run scoreboard players set #np m.tmp 1",
    "scoreboard players operation @s m.sacp = #np m.tmp",
    "scoreboard players operation #pid m.tmp = @s m.id",
    f"execute as @e[type=minecraft:chest_minecart,tag=metiers.sac] if score @s m.own = #pid m.tmp run function {NS}:sac/remplir",
    'title @s actionbar [{"text":"Sac à dos : page ","color":"aqua"},{"score":{"name":"@s","objective":"m.sacp"},"color":"yellow"}]',
    "playsound minecraft:item.book.page_turn master @s ~ ~ ~ 1 1"]))
w(F + "sac/fermer.mcfunction", "\n".join([
    "data modify entity @s Items set value []", "tp @s ~ -400 ~", "kill @s"]))

# ---------------------------------------------------------------- grimoire de téléportation de l'Enchanteur
TPMAX = [1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
TPCD = [1200, 1100, 1000, 880, 760, 640, 520, 400, 300, 200, 120]     # en demi-secondes
DIMS = [("overworld", "Surface"), ("the_nether", "Nether"), ("the_end", "End")]
GR = [f"execute store result storage {NS}:tp id int 1 run scoreboard players get @s m.id",
      f'data modify storage {NS}:tp b set value {{}}',
      f"function {NS}:tp/lister with storage {NS}:tp"]
for k in range(11):
    GR += [f"execute if score @s m.n_out matches {k} run data modify storage {NS}:tp b.max set value {TPMAX[k]}"]
GR += [f"execute store result storage {NS}:tp b.cd int 0.5 run scoreboard players get @s m.tpcd",
       f"function {NS}:tp/menu with storage {NS}:tp b"]
w(F + "tp/ouvrir.mcfunction", "\n".join(GR))
LI = [f'$data modify storage {NS}:tp b.l{i} set value "— emplacement libre —"' for i in range(1, 11)]
LI += [f"$execute if data storage {NS}:tp j$(id)[{i - 1}] run function {NS}:tp/etiquette with storage {NS}:tp j$(id)[{i - 1}]" for i in range(1, 11)]
w(F + "tp/lister.mcfunction", "\n".join(LI))
w(F + "tp/etiquette.mcfunction", f'$data modify storage {NS}:tp b.l$(n) set value "$(n). $(nom) : $(x) $(y) $(z)"')
btn = []
for i in range(1, 11):
    btn.append(f'{{label:{{text:"$(l{i})",color:"light_purple"}},width:300,tooltip:{{text:"Téléportation après 3 secondes immobile"}},action:{{type:"run_command",command:"trigger metiers set {720 + i}"}}}}')
w(F + "tp/menu.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Grimoire de téléportation",color:"dark_purple",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:plain_message",width:300,contents:[{text:"Points : $(max) au maximum à ton palier.\\n",color:"gray"},{text:"Recharge restante : $(cd) s\\n",color:"yellow"},'
  '{text:"Les autres dimensions s\'ouvrent au palier 8.",color:"dark_gray"}]}],'
  'actions:[{label:{text:"Enregistrer ma position ici",color:"green"},width:300,action:{type:"run_command",command:"trigger metiers set 701"}},'
  + ",".join(btn) +
  ',{label:{text:"Effacer le dernier point",color:"red"},width:300,action:{type:"run_command",command:"trigger metiers set 702"}}],'
  'columns:1,exit_action:{label:"Fermer",width:150}}')
EN = [f"execute store result storage {NS}:tp id int 1 run scoreboard players get @s m.id",
      f"execute store result score #n m.tmp run data get storage {NS}:tp tmpl"]
w(F + "tp/compter.mcfunction", f"$execute store result score #n m.tmp run data get storage {NS}:tp j$(id)")
EN = [f"execute store result storage {NS}:tp id int 1 run scoreboard players get @s m.id",
      f"function {NS}:tp/compter with storage {NS}:tp"]
for k in range(11):
    EN.append(f"execute if score @s m.n_out matches {k} run scoreboard players set #max m.tmp {TPMAX[k]}")
EN += [f"execute if score #n m.tmp >= #max m.tmp run return run {tr('Tous tes emplacements sont pris : efface le dernier point ou monte de palier.', 'red')}",
       f"execute store result storage {NS}:tp p.x int 1 run data get entity @s Pos[0]",
       f"execute store result storage {NS}:tp p.y int 1 run data get entity @s Pos[1]",
       f"execute store result storage {NS}:tp p.z int 1 run data get entity @s Pos[2]",
       "scoreboard players add #n m.tmp 1",
       f"execute store result storage {NS}:tp p.n int 1 run scoreboard players get #n m.tmp"]
EN += [f'execute if dimension minecraft:{d} run data modify storage {NS}:tp p.d set value "{d}"' for d, _ in DIMS]
EN += [f'execute if dimension minecraft:{d} run data modify storage {NS}:tp p.nom set value "{lab}"' for d, lab in DIMS]
EN += [f"function {NS}:tp/ajouter with storage {NS}:tp", tr("Position enregistrée dans ton grimoire.", "light_purple"), f"function {NS}:tp/ouvrir"]
w(F + "tp/enregistrer.mcfunction", "\n".join(EN))
w(F + "tp/ajouter.mcfunction", f"$data modify storage {NS}:tp j$(id) append from storage {NS}:tp p")
w(F + "tp/effacer.mcfunction", "\n".join([f"execute store result storage {NS}:tp id int 1 run scoreboard players get @s m.id",
                                          f"function {NS}:tp/effacer_m with storage {NS}:tp", f"function {NS}:tp/ouvrir"]))
w(F + "tp/effacer_m.mcfunction", f"$data remove storage {NS}:tp j$(id)[-1]")
# départ de l'incantation
GO = [f"execute if score @s m.tpcd matches 1.. run return run {tr('Ton grimoire se recharge encore.', 'red')}",
      f"execute store result storage {NS}:tp id int 1 run scoreboard players get @s m.id",
      "scoreboard players operation @s m.tpk = @s m.trig", "scoreboard players remove @s m.tpk 721",
      f"execute store result storage {NS}:tp k int 1 run scoreboard players get @s m.tpk",
      f'data remove storage {NS}:tp cible', f"function {NS}:tp/choisir with storage {NS}:tp",
      f"execute unless data storage {NS}:tp cible run return run {tr('Cet emplacement est vide.', 'red')}",
      f'execute if score @s m.n_out matches ..7 if data storage {NS}:tp cible{{d:"overworld"}} unless dimension minecraft:overworld run return run {tr("Avant le palier 8, ton grimoire ne traverse pas les dimensions.", "red")}',
      f'execute if score @s m.n_out matches ..7 if data storage {NS}:tp cible{{d:"the_nether"}} unless dimension minecraft:the_nether run return run {tr("Avant le palier 8, ton grimoire ne traverse pas les dimensions.", "red")}',
      f'execute if score @s m.n_out matches ..7 if data storage {NS}:tp cible{{d:"the_end"}} unless dimension minecraft:the_end run return run {tr("Avant le palier 8, ton grimoire ne traverse pas les dimensions.", "red")}',
      "execute store result score @s m.tpx run data get entity @s Pos[0] 10",
      "execute store result score @s m.tpy run data get entity @s Pos[1] 10",
      "execute store result score @s m.tpz run data get entity @s Pos[2] 10",
      "scoreboard players set @s s.hurt 0", "scoreboard players set @s m.tpinc 1",
      tr("Incantation... ne bouge pas pendant 3 secondes.", "light_purple")]
w(F + "tp/aller.mcfunction", "\n".join(GO))
w(F + "tp/choisir.mcfunction", f"$data modify storage {NS}:tp cible set from storage {NS}:tp j$(id)[$(k)]")
w(F + "tp/incantation.mcfunction", "\n".join([
    "execute store result score #x m.tmp run data get entity @s Pos[0] 10",
    "execute store result score #y m.tmp run data get entity @s Pos[1] 10",
    "execute store result score #z m.tmp run data get entity @s Pos[2] 10",
    "scoreboard players operation #x m.tmp -= @s m.tpx", "scoreboard players operation #y m.tmp -= @s m.tpy", "scoreboard players operation #z m.tmp -= @s m.tpz",
    f"execute unless score #x m.tmp matches -5..5 run return run function {NS}:tp/rate",
    f"execute unless score #y m.tmp matches -5..5 run return run function {NS}:tp/rate",
    f"execute unless score #z m.tmp matches -5..5 run return run function {NS}:tp/rate",
    f"execute if score @s s.hurt matches 1.. run return run function {NS}:tp/rate",
    "scoreboard players add @s m.tpinc 1",
    "particle minecraft:portal ~ ~1 ~ 0.4 0.8 0.4 0.6 30",
    "playsound minecraft:block.portal.ambient master @s ~ ~ ~ 0.3 1.8",
    f"execute if score @s m.tpinc matches 7.. run function {NS}:tp/partir"]))
w(F + "tp/rate.mcfunction", "scoreboard players set @s m.tpinc 0\n" + tr("Incantation interrompue.", "red"))
TPG = ["scoreboard players set @s m.tpinc 0",
       f"execute store result storage {NS}:tp id int 1 run scoreboard players get @s m.id",
       f"execute store result storage {NS}:tp k int 1 run scoreboard players get @s m.tpk",
       f"function {NS}:tp/choisir with storage {NS}:tp", f"function {NS}:tp/tp with storage {NS}:tp cible"]
for k in range(11):
    TPG.append(f"execute if score @s m.n_out matches {k} run scoreboard players set @s m.tpcd {TPCD[k]}")
TPG += ["playsound minecraft:entity.enderman.teleport master @a ~ ~ ~ 1 1", "particle minecraft:reverse_portal ~ ~1 ~ 0.4 0.8 0.4 0.2 60"]
w(F + "tp/partir.mcfunction", "\n".join(TPG))
w(F + "tp/tp.mcfunction", "$execute in minecraft:$(d) run tp @s $(x).5 $(y) $(z).5")

# ---------------------------------------------------------------- clic droit (carotte sur un bâton) : grimoire, houlette, sac, lasso, parchemin
w(F + "refonte/clic.mcfunction", "\n".join([
    "scoreboard players set @s s.cos 0",
    f'execute if items entity @s weapon.mainhand {SEL("n")} run return run function {NS}:tp/ouvrir',
    f'execute if items entity @s weapon.mainhand {SEL("e")} run return run function {NS}:e/houlette',
    f"execute if items entity @s weapon.mainhand {SACSEL} run return run function {NS}:sac/ouvrir",
    f"execute if items entity @s weapon.mainhand {FSEL('lasso')} run return run function {NS}:forge/lasso",
    f"execute if items entity @s weapon.mainhand {FSEL('parchemin')} run return run function {NS}:forge/parchemin"]))

# ---------------------------------------------------------------- tick (chaque tick) et joueur (toutes les 0,5 s)
w(F + "refonte/tick.mcfunction", "\n".join([
    f"execute as @a[scores={{s.cos=1..}}] at @s run function {NS}:refonte/clic",
    f"execute as @a at @s if items entity @s weapon.mainhand {FSEL('marteau')} run function {NS}:forge/marteau",
    f"execute as @a[scores={{s.bow=1..}}] at @s if items entity @s weapon.mainhand {FSEL('arc3')} run function {NS}:forge/arc3",
    "scoreboard players set @a s.bow 0", "scoreboard players set @a s.pick 0",
    f"execute as @a at @s if entity @e[type=#{NS}:animaux,distance=..48,predicate={NS}:suit_moi] run function {NS}:e/houlette_suivre",
    "scoreboard players remove @a[scores={m.forgecd=1..}] m.forgecd 1"]))
RJ = [f"execute unless entity @s[tag=metiers.v24] run function {NS}:refonte/migration",
      f"execute if score @s m.saco matches 1 run function {NS}:sac/suivi",
      f"execute if score @s m.tpinc matches 1.. run function {NS}:tp/incantation",
      "execute if score @s m.tpcd matches 1.. run scoreboard players remove @s m.tpcd 1",
      f"execute if entity @s[tag=metiers.lasso_plein] run function {NS}:forge/lasso_retour",
      f"execute if items entity @s weapon.offhand {FSEL('aimant')} run tp @e[type=minecraft:item,distance=1.5..8,nbt=!{{PickupDelay:32767s}}] @s",
      f"execute if items entity @s weapon.offhand {FSEL('aimant')} run tp @e[type=minecraft:experience_orb,distance=1.5..8] @s"]
w(F + "refonte/joueur.mcfunction", "\n".join(RJ))

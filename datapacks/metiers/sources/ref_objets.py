# -*- coding: utf-8 -*-
# 26.0 (26/11/2026) : objets des compétences de branche (achetés en Écus dans l'onglet Outil du métier) et fin des
# objets de la Forge (marteau, faux, arc triple, lasso, parchemin, aimant, cape) : leurs capacités passent sur l'outil
# du métier par palier, l'arc et les élytres deviennent des récompenses de palier, les anciens objets sont remboursés.
# Exécuté avant ref_menu.py (qui ajoute OBJ_BTN aux onglets Outil).
O_ = F + "objets/"
OSEL = lambda k: f'*[minecraft:custom_data~{{metiers_obj:"{k}"}}]'
# clé : (métier, compétence, nom, objet de base, modèle, prix en Écus, effet)
OBJETS = {
    "graine": ("b", 11, "Graine de forêt", "carrot_on_a_stick", "minecraft:oak_sapling", 400,
               "Clic droit en visant une pousse : l'arbre adulte apparaît d'un coup."),
    "bombe": ("f", 11, "Bombe d'engrais", "snowball", "minecraft:bone_meal", 250, "Lance-la : tout mûrit en 7x7 là où elle tombe."),
    "arrosoir": ("f", 14, "Arrosoir", "carrot_on_a_stick", "minecraft:water_bucket", 6000,
                 "Clic droit : les cultures en 5x5 autour de toi avancent d'un stade (recharge 2 s). Se garde."),
    "epouvantail": ("f", 17, "Épouvantail", "armor_stand", "minecraft:carved_pumpkin", 12000,
                    "Pose-le : plus aucun monstre à 24 blocs. Casse-le pour le reprendre."),
    "dynamite": ("m", 10, "Dynamite", "snowball", "minecraft:tnt", 150,
                 "Lance-la : elle creuse 5x5x5 sans toucher aux minerais, ce qu'elle casse revient dans ton inventaire."),
    "lanterne": ("m", 13, "Lanterne", "paper", "minecraft:lantern", 8000, "En main secondaire : la lumière te suit. Se garde."),
    "piege": ("c", 16, "Piège à mâchoires", "armor_stand", "minecraft:tripwire_hook", 800,
              "Pose-le : il bloque et blesse le premier monstre qui passe (recharge 10 s). Casse-le pour le reprendre."),
    "filet": ("p", 9, "Filet de pêche", "armor_stand", "minecraft:cobweb", 15000,
              "Pose-le dans l'eau : il pêche seul toutes les 2 min, dans un coffre ou un tonneau collé à lui (sinon au sol)."),
    "sifflet": ("e", 16, "Sifflet", "carrot_on_a_stick", "minecraft:goat_horn", 4000,
                "Clic droit : la dernière monture que tu as montée te rejoint (si son coin est chargé). Se garde."),
    "mangeoire": ("e", 10, "Mangeoire", "armor_stand", "minecraft:hay_block", 10000,
                  "Pose-la : les animaux adultes à 8 blocs se reproduisent toutes les 5 min (sans XP)."),
    "tente": ("x", 15, "Tente", "armor_stand", "minecraft:white_bed", 5000,
              "Pose-la : elle devient ton point de réapparition. Casse-la pour la reprendre."),
    "baguette": ("k", 4, "Baguette du bâtisseur", "carrot_on_a_stick", "minecraft:blaze_rod", 5000,
                 "Clic droit sur une face : elle la prolonge d'un rang (3x3, 5x5 avec Maître d'œuvre) avec les blocs de ton inventaire. Se garde."),
}
POSES = [k for k, v in OBJETS.items() if v[3] == "armor_stand"]
LANCES = [k for k, v in OBJETS.items() if v[3] == "snowball"]


def obj_item(k, n=1):
    j, sk, nom, base, mod, prix, desc = OBJETS[k]
    c = [f'minecraft:custom_name={{text:"{nom}",color:"{jobs[j]["color"]}",bold:true,italic:false}}',
         f'minecraft:lore=[{{text:"{desc}",color:"gray",italic:false}},{{text:"Objet de {jobs[j]["name"]}",color:"gold",italic:false}}]',
         f'minecraft:item_model="{mod}"', f'minecraft:custom_data={{metiers_obj:"{k}"}}']
    if base == "carrot_on_a_stick":
        c += ["!minecraft:max_damage", "!minecraft:damage", "minecraft:max_stack_size=16"]
    if base == "armor_stand":
        c.append(f'minecraft:entity_data={{id:"minecraft:armor_stand",Tags:["{NS}.obj","{NS}.o_{k}","{NS}.onew"],Invisible:1b,Small:1b,'
                 f'NoBasePlate:1b,DisabledSlots:4144959,equipment:{{head:{{id:"{mod}",count:1}}}}}}')
    if k in ("lanterne", "arrosoir", "sifflet", "baguette"):
        c.append("minecraft:max_stack_size=1")
    return f"minecraft:{base}[{','.join(c)}] {n}"


for k in OBJETS:
    w(O_ + f"donner_{k}.mcfunction", f"give @s {obj_item(k)}")

# ---------------------------------------------------------------- boutique de chaque métier (onglet Outil)
OBJ_J = {}
for i, (k, v) in enumerate(OBJETS.items()):
    OBJ_J.setdefault(v[0], []).append((i, k))
OBJ_BTN = {}
TRG_O = []
for j, lst in OBJ_J.items():
    d = jobs[j]
    acts = []
    for i, k in lst:
        _, sk, nom, base, mod, prix, desc = OBJETS[k]
        ptxt = f"{prix:,} Écus".replace(",", " ")
        acts.append(f'{{label:[{{text:"{nom}  ",color:"{d["color"]}",bold:true}},{{text:"{ptxt}",color:"gold",bold:false}}],width:260,'
                    f'tooltip:{{text:"{desc}\\nDébloqué par la compétence {SKILLS[j][sk - 1][0]}."}},'
                    f'action:{{type:"run_command",command:"trigger metiers set {3500 + i}"}}}}')
        TRG_O.append(f'execute if score @s m.trig matches {3500 + i} run function {NS}:appel {{f:"objets/acheter_{k}"}}')
        w(O_ + f"acheter_{k}.mcfunction", "\n".join([
            f"execute unless entity @s[tag={NS}.sk.{j}{sk}] run return run {tr(f'Il faut la compétence {SKILLS[j][sk - 1][0]} ({d[chr(110)+chr(97)+chr(109)+chr(101)]}).', 'red')}",
            f"execute unless score @s c.ecus matches {prix}.. run return run {tr(f'Il te faut {prix} Écus.', 'red')}",
            f"scoreboard players remove @s c.ecus {prix}", f"function {NS}:objets/donner_{k}",
            "playsound minecraft:entity.villager.trade master @s ~ ~ ~ 1 1.2",
            tr(f"Acheté : {nom} pour {prix} Écus.", "green"), f"function {NS}:objets/boutique_{j}"]))
    w(O_ + f"boutique_{j}.mcfunction", f"execute store result storage {NS}:t e int 1 run scoreboard players get @s c.ecus\n"
      f"function {NS}:objets/boutique_{j}_d with storage {NS}:t")
    w(O_ + f"boutique_{j}_d.mcfunction",
      f'$dialog show @s {{type:"minecraft:multi_action",title:{{text:"Objets de {d["name"]}",color:"{d["color"]}",bold:true}},can_close_with_escape:true,pause:false,'
      f'body:[{{type:"minecraft:plain_message",width:300,contents:[{{text:"Ton solde : ",color:"gray"}},{{text:"$(e) Écus",color:"gold",bold:true}},'
      f'{{text:"\\nChaque objet se débloque avec une compétence de l’arbre. Survole pour son effet.",color:"gray"}}]}}],'
      f'actions:[{",".join(acts)}],columns:1,'
      f'exit_action:{{label:"Retour",width:200,action:{{type:"run_command",command:"trigger metiers set {550 + d["idx"]}"}}}}}}')
    # 27/11/2026 : 3480 + 10 tombait sur 3490 (Forge arcanique) pour le Bâtisseur, d'où 3494
    _tb = 3494 if d["idx"] == 10 else 3480 + d["idx"]
    OBJ_BTN[j] = (_tb, f"Objets de {d['name']}")
    TRG_O.append(f'execute if score @s m.trig matches {_tb} run function {NS}:appel {{f:"objets/boutique_{j}"}}')
TRG_O += [f'execute if score @s m.trig matches 3490 run function {NS}:appel {{f:"comp/n_forge"}}',
          f'execute if score @s m.trig matches 3492 run function {NS}:appel {{f:"objets/recup_elytres"}}']
add_lines(F + "trigger.mcfunction", TRG_O)

# ---------------------------------------------------------------- clic droit (carotte sur un bâton)
_p = os.path.join(ROOT, F, "refonte/clic.mcfunction")
_t = open(_p, encoding="utf-8").read().split("\n")
_t[1:1] = [f"execute if items entity @s weapon.mainhand {OSEL('graine')} run return run function {NS}:objets/graine",
           f"execute if items entity @s weapon.mainhand {OSEL('arrosoir')} run return run function {NS}:objets/arrosoir",
           f"execute if items entity @s weapon.mainhand {OSEL('sifflet')} run return run function {NS}:objets/sifflet",
           f"execute if items entity @s weapon.mainhand {OSEL('baguette')} run return run function {NS}:baguette/clic",
           # anciens objets de la Forge sur l'outil : Éleveur (lasso) et Enchanteur (parchemin), accroupi
           f'execute if items entity @s weapon.mainhand {SEL("e")} if predicate {NS}:accroupi if entity @s[tag={NS}.sk.e15] run return run function {NS}:forge/lasso',
           f'execute if items entity @s weapon.mainhand {SEL("n")} if predicate {NS}:accroupi if entity @s[tag={NS}.sk.n8] run return run function {NS}:objets/parchemin']
open(_p, "w", encoding="utf-8").write("\n".join(_t))
SAPF = {"oak_sapling": "oak", "spruce_sapling": "spruce", "birch_sapling": "birch", "jungle_sapling": "jungle_tree",
        "acacia_sapling": "acacia", "dark_oak_sapling": "dark_oak", "cherry_sapling": "cherry", "mangrove_propagule": "mangrove",
        "pale_oak_sapling": "pale_oak", "azalea": "azalea_tree", "flowering_azalea": "azalea_tree"}
w(O_ + "graine.mcfunction", f"scoreboard players set #pas m.tmp 0\nscoreboard players set #ok m.tmp 0\n"
  f"execute anchored eyes positioned ^ ^ ^0.2 run function {NS}:objets/graine_rayon\n"
  f"execute if score #ok m.tmp matches 0 run {tr('Vise une pousse d’arbre.', 'red')}\n"
  'execute if score #ok m.tmp matches 1 run item modify entity @s weapon.mainhand {function:"minecraft:set_count",type:"minecraft:set_count",count:-1,add:true}')
w(O_ + "graine_rayon.mcfunction", "\n".join(
    ["scoreboard players add #pas m.tmp 1"] +
    [f"execute if block ~ ~ ~ minecraft:{s} align xyz run return run function {NS}:objets/graine_pousse {{s:\"{s}\",f:\"{f}\"}}" for s, f in SAPF.items()] +
    [f"execute if score #pas m.tmp matches ..50 if block ~ ~ ~ #{NS}:vide positioned ^ ^ ^0.1 run function {NS}:objets/graine_rayon"]))
w(O_ + "graine_pousse.mcfunction", "\n".join([
    "setblock ~ ~ ~ minecraft:air",
    "$execute store success score #ok m.tmp run place feature minecraft:$(f) ~ ~ ~",
    "$execute if score #ok m.tmp matches 0 run setblock ~ ~ ~ minecraft:$(s)",
    "execute if score #ok m.tmp matches 0 run tellraw @p " + '{"text":"Pas assez de place pour cet arbre.","color":"red"}',
    "execute if score #ok m.tmp matches 1 run particle minecraft:happy_villager ~0.5 ~2 ~0.5 1.5 2 1.5 0 60",
    "execute if score #ok m.tmp matches 1 run playsound minecraft:block.grass.place master @a ~ ~ ~ 1 0.6"]))
AR = ["execute if score @s m.ocd matches 1.. run return 0", "scoreboard players set @s m.ocd 4"]
for c, mx in (("wheat", 7), ("carrots", 7), ("potatoes", 7), ("beetroots", 3), ("nether_wart", 3)):
    for a in range(mx - 1, -1, -1):
        AR.append(f"fill ~-2 ~-1 ~-2 ~2 ~1 ~2 minecraft:{c}[age={a + 1}] replace minecraft:{c}[age={a}]")
AR += ["particle minecraft:splash ~ ~0.5 ~ 2 0.3 2 0 80", "playsound minecraft:item.bucket.empty master @a ~ ~ ~ 0.6 1.4"]
w(O_ + "arrosoir.mcfunction", "\n".join(AR))
w(O_ + "sifflet.mcfunction", "\n".join([
    "execute if score @s m.ocd matches 1.. run return 0", "scoreboard players set @s m.ocd 6",
    "scoreboard players operation #pid m.tmp = @s m.id", "scoreboard players set #ok m.tmp 0",
    f"execute as @e[type=#{NS}:montures] if score @s m.mont = #pid m.tmp run scoreboard players set #ok m.tmp 1",
    f"execute as @e[type=#{NS}:montures] if score @s m.mont = #pid m.tmp run tp @s @p[scores={{m.ocd=6}}]",
    "playsound minecraft:item.goat_horn.sound.0 master @a ~ ~ ~ 1 1.4",
    f"execute if score #ok m.tmp matches 0 run {tr('Ta monture est trop loin (coin du monde non chargé) ou tu n’en as jamais monté.', 'gold')}"]))
# parchemin sur le grimoire : le livre arrive dans l'inventaire, le grimoire reste en main
_par = open(os.path.join(ROOT, F, "forge/parchemin.mcfunction"), encoding="utf-8").read()
_par = _par.replace("item replace entity @s weapon.mainhand from entity @e[tag=metiers.livre,limit=1] contents\nkill @e[tag=metiers.livre]",
                    "data modify entity @e[tag=metiers.livre,limit=1] PickupDelay set value 0s\ntp @e[tag=metiers.livre] @s\ntag @e[tag=metiers.livre] remove metiers.livre")
assert "PickupDelay set value 0s" in _par
w(O_ + "parchemin.mcfunction", _par)
# lasso sur la houlette : l'œuf arrive dans l'inventaire, la houlette reste en main
_ls = open(os.path.join(ROOT, F, "forge/lasso_prendre.mcfunction"), encoding="utf-8").read()
for a_, b_ in (("execute as @a[tag=metiers.lanceur,limit=1] run item replace entity @s weapon.mainhand from entity @e[tag=metiers.lasso_oeuf,limit=1] contents\n",
                "data modify entity @e[tag=metiers.lasso_oeuf,limit=1] PickupDelay set value 0s\ntp @e[tag=metiers.lasso_oeuf] @a[tag=metiers.lanceur,limit=1]\n"),
               ("kill @e[tag=metiers.lasso_oeuf]\n", "tag @e[tag=metiers.lasso_oeuf] remove metiers.lasso_oeuf\n"),
               ("execute as @a[tag=metiers.lanceur] run tag @s add metiers.lasso_plein\n", ""),
               ('Item.components."minecraft:custom_data" set value {forge:"lasso_plein"}', 'Item.components."minecraft:custom_data" set value {metiers_oeuf:1b}')):
    assert a_ in _ls, a_
    _ls = _ls.replace(a_, b_)
w(F + "forge/lasso_prendre.mcfunction", _ls)

# ---------------------------------------------------------------- objets lancés : un marqueur suit la boule de neige et agit où elle tombe
add_lines(F + "refonte/load.mcfunction", ["scoreboard objectives add m.pk dummy", "scoreboard objectives add m.ot dummy"])
TO = [f"execute as @e[type=minecraft:snowball,tag=!{NS}.pv] run function {NS}:objets/lance",
      f"tag @e[type=minecraft:marker,tag={NS}.proj] remove {NS}.pvivant",
      f"execute as @e[type=minecraft:snowball,tag={NS}.plt] at @s run function {NS}:objets/suivre",
      f"execute as @e[type=minecraft:marker,tag={NS}.proj,tag=!{NS}.pvivant] at @s run function {NS}:objets/impact",
      # Lanterne en main secondaire
      f"execute as @a if items entity @s weapon.offhand {OSEL('lanterne')} at @s run function {NS}:objets/lumiere",
      f"execute as @e[type=minecraft:marker,tag={NS}.lum] at @s run function {NS}:objets/lumiere_verif",
      # objets posés : nouveaux
      f"execute as @e[type=minecraft:armor_stand,tag={NS}.onew] at @s run function {NS}:objets/pose",
      # Mineur : compétence Aimant (26/11/2026, remplace la Bourse aimantée du Marchand)
      f'execute as @a[tag={NS}.sk.m14] at @s run function {NS}:objets/aimant',
      # Mineur : Pioche large (m16, 26/11/2026) : 3x3 tant que la compétence est active (Désactiver dans l'arbre) ;
      # accroupi, c'est la Veine (m15, ref_prestige.py, m/veine_tick) si elle est acquise
      f'execute as @a[predicate=!{NS}:accroupi] if items entity @s weapon.mainhand #minecraft:pickaxes if entity @s[tag={NS}.sk.m16] at @s run function {NS}:objets/marteau',
      # accroupi sans la Veine (pas acquise ou désactivée), le 3x3 marche aussi
      f'execute as @a[predicate={NS}:accroupi,tag=!{NS}.sk.m15] if items entity @s weapon.mainhand #minecraft:pickaxes if entity @s[tag={NS}.sk.m16] at @s run function {NS}:objets/marteau',
      f'execute as @a[predicate={NS}:accroupi,tag={NS}.skoff.m15] if items entity @s weapon.mainhand #minecraft:pickaxes if entity @s[tag={NS}.sk.m16] at @s run function {NS}:objets/marteau',
      "scoreboard players set @a s.pk 0"]
_ELY = "*[minecraft:custom_data~{metiers_elytres:1b}]"
TO += [f"clear @a[tag=!{NS}.sk.x9] {_ELY}", f"clear @a[tag={NS}.skoff.x9] {_ELY}"]
# retirer les élytres partout sur le joueur (inventaire, armure et coffre de l'Ender) : une seule paire existe à la fois
w(O_ + "retirer_elytres.mcfunction", "\n".join([f"clear @s {_ELY}"] + [
    f"execute if items entity @s enderchest.{n} {_ELY} run item replace entity @s enderchest.{n} with minecraft:air" for n in range(27)]))
w(O_ + "tick.mcfunction", "\n".join(TO))
add_lines(F + "refonte/tick.mcfunction", [f"function {NS}:objets/tick"])
w(O_ + "lance.mcfunction", "\n".join(
    [f"tag @s add {NS}.pv"] +
    [f'execute if items entity @s contents {OSEL(k)} run function {NS}:objets/lance_go {{k:"{k}"}}' for k in LANCES]))
w(O_ + "lance_go.mcfunction", "\n".join([
    f"tag @s add {NS}.plt", "scoreboard players add #pk m.tmp 1", "scoreboard players operation @s m.pk = #pk m.tmp",
    f'$summon minecraft:marker ~ ~ ~ {{Tags:["{NS}.proj","{NS}.p_$(k)","{NS}.pnew","{NS}.pvivant"]}}',
    f"scoreboard players operation @e[type=minecraft:marker,tag={NS}.pnew] m.pk = #pk m.tmp",
    "scoreboard players set #o m.tmp 0", "execute on origin run scoreboard players operation #o m.tmp = @s m.id",
    f"scoreboard players operation @e[type=minecraft:marker,tag={NS}.pnew] m.own = #o m.tmp",
    f"tag @e[type=minecraft:marker,tag={NS}.pnew] remove {NS}.pnew"]))
w(O_ + "suivre.mcfunction", "scoreboard players operation #k m.tmp = @s m.pk\n"
  f"execute as @e[type=minecraft:marker,tag={NS}.proj] if score @s m.pk = #k m.tmp run function {NS}:objets/suivre_m")
w(O_ + "suivre_m.mcfunction", f"tp @s ~ ~ ~\ntag @s add {NS}.pvivant")
w(O_ + "impact.mcfunction", "\n".join(
    ["scoreboard players operation #o m.tmp = @s m.own", f"tag @a remove {NS}.proprio",
     f"execute as @a if score @s m.id = #o m.tmp run tag @s add {NS}.proprio"] +
    [f"execute if entity @s[tag={NS}.p_{k}] run function {NS}:objets/impact_{k}" for k in LANCES] + ["kill @s"]))
BO = []
for c, mx in (("wheat", 7), ("carrots", 7), ("potatoes", 7), ("beetroots", 3), ("nether_wart", 3), ("sweet_berry_bush", 3), ("torchflower_crop", 2)):
    BO.append(f"fill ~-3 ~-2 ~-3 ~3 ~2 ~3 minecraft:{c}[age={mx}] replace minecraft:{c}")
BO += ["particle minecraft:happy_villager ~ ~0.5 ~ 2.5 0.8 2.5 0 120", "playsound minecraft:item.bone_meal.use master @a ~ ~ ~ 1 0.8"]
w(O_ + "impact_bombe.mcfunction", "\n".join(BO))
wj(f"data/{NS}/tags/block/dynamite.json", {"values": [f"minecraft:{b}" for b in (
    "stone", "deepslate", "cobblestone", "cobbled_deepslate", "granite", "diorite", "andesite", "tuff", "calcite", "dirt", "coarse_dirt",
    "rooted_dirt", "gravel", "sand", "red_sand", "sandstone", "red_sandstone", "netherrack", "basalt", "smooth_basalt", "blackstone",
    "dripstone_block", "clay", "grass_block", "mud", "end_stone", "soul_sand", "soul_soil")]})
w(O_ + "impact_dynamite.mcfunction", "\n".join([
    f"fill ~-2 ~-2 ~-2 ~2 ~2 ~2 minecraft:air replace #{NS}:dynamite destroy",
    f"tp @e[type=minecraft:item,distance=..5] @a[tag={NS}.proprio,limit=1]",
    "particle minecraft:explosion_emitter ~ ~ ~ 0 0 0 0 1", "playsound minecraft:entity.generic.explode master @a ~ ~ ~ 1.5 1"]))
w(O_ + "impact_fumigene.mcfunction", "\n".join([
    f"effect give @e[type=#{NS}:hostiles,distance=..8] minecraft:slowness 6 3", f"effect give @e[type=#{NS}:hostiles,distance=..8] minecraft:weakness 6 1",
    "particle minecraft:campfire_cosy_smoke ~ ~0.5 ~ 3 1 3 0.02 200", "playsound minecraft:block.fire.extinguish master @a ~ ~ ~ 1 0.6"]))
# Lanterne : un bloc de lumière suit le joueur (un marqueur par joueur garde sa place)
w(O_ + "lumiere.mcfunction", "\n".join([
    "scoreboard players operation #pid m.tmp = @s m.id", "scoreboard players set #ici m.tmp 0",
    f"execute anchored eyes positioned ^ ^ ^ align xyz positioned ~0.5 ~0.5 ~0.5 as @e[type=minecraft:marker,tag={NS}.lum,distance=..0.2] if score @s m.own = #pid m.tmp run scoreboard players set #ici m.tmp 1",
    f"execute if score #ici m.tmp matches 1 as @e[type=minecraft:marker,tag={NS}.lum,distance=..3] if score @s m.own = #pid m.tmp run return run scoreboard players set @s m.ot 3",
    f"execute as @e[type=minecraft:marker,tag={NS}.lum] if score @s m.own = #pid m.tmp at @s run function {NS}:objets/lumiere_off",
    f"execute anchored eyes positioned ^ ^ ^ align xyz positioned ~0.5 ~0.5 ~0.5 if block ~ ~ ~ minecraft:air run summon minecraft:marker ~ ~ ~ {{Tags:[\"{NS}.lum\",\"{NS}.lnew\"]}}",
    f"execute as @e[type=minecraft:marker,tag={NS}.lnew] at @s run setblock ~ ~ ~ minecraft:light[level=15]",
    f"scoreboard players operation @e[type=minecraft:marker,tag={NS}.lnew] m.own = #pid m.tmp",
    f"scoreboard players set @e[type=minecraft:marker,tag={NS}.lnew] m.ot 3",
    f"tag @e[type=minecraft:marker,tag={NS}.lnew] remove {NS}.lnew"]))
w(O_ + "lumiere_off.mcfunction", "execute if block ~ ~ ~ minecraft:light run setblock ~ ~ ~ minecraft:air\nkill @s")
w(O_ + "lumiere_verif.mcfunction", f"scoreboard players remove @s m.ot 1\nexecute if score @s m.ot matches ..0 run function {NS}:objets/lumiere_off")
w(O_ + "aimant.mcfunction", "tp @e[type=minecraft:item,distance=1.5..8,nbt=!{PickupDelay:32767s}] @s\ntp @e[type=minecraft:experience_orb,distance=1.5..8] @s")
# 3x3 de la pioche du Mineur : mêmes fonctions que l'ancien Marteau, toutes pioches confondues
PK = {f"s.pk_{m}": f"minecraft.used:minecraft.{m}_pickaxe" for m in ("wooden", "stone", "copper", "iron", "golden", "diamond", "netherite")}
add_lines(F + "refonte/load.mcfunction", [f"scoreboard objectives add {o} {c}" for o, c in PK.items()] + ["scoreboard objectives add s.pk dummy"])
w(O_ + "marteau.mcfunction", "\n".join(
    [f"scoreboard players operation @s s.pk += @s {o}" for o in PK] +
    ["scoreboard players operation @s s.pick = @s s.pk", f"function {NS}:forge/marteau"]))
add_lines(O_ + "tick.mcfunction", [f"scoreboard players set @a {o} 0" for o in PK])

# ---------------------------------------------------------------- objets posés (porte-armures invisibles)
w(O_ + "pose.mcfunction", "\n".join([
    f"tag @s remove {NS}.onew", "scoreboard players add #pk m.tmp 1", "scoreboard players operation @s m.pk = #pk m.tmp",
    "scoreboard players operation @s m.own = @p m.id", "scoreboard players set @s m.ot 0",
    f"execute if entity @s[tag={NS}.o_tente] run spawnpoint @p ~ ~ ~",
    f"execute if entity @s[tag={NS}.o_tente] run tellraw @p " + '{"text":"Tente posée : tu réapparaîtras ici.","color":"blue"}']))
OB = [f"execute as @e[type=minecraft:armor_stand,tag={NS}.obj] at @s run function {NS}:objets/poses_un",
      f"execute as @e[type=minecraft:marker,tag={NS}.otwin] at @s run function {NS}:objets/jumeau"]
w(O_ + "poses.mcfunction", "\n".join(OB))
add_lines(F + "loop.mcfunction", [f"function {NS}:objets/poses", "execute as @a if score @s m.ocd matches 1.. run scoreboard players remove @s m.ocd 1"])
# chaque objet posé a un jumeau (marqueur) : s'il disparaît (cassé), on rend l'objet à la place du porte-armure vanilla
w(O_ + "poses_un.mcfunction", "\n".join(
    ["scoreboard players add @s m.ot 1", "scoreboard players operation #k m.tmp = @s m.pk", "scoreboard players set #j m.tmp 0",
     f"execute as @e[type=minecraft:marker,tag={NS}.otwin,distance=..2] if score @s m.pk = #k m.tmp run scoreboard players set #j m.tmp 1"] +
    [f"execute if score #j m.tmp matches 0 if entity @s[tag={NS}.o_{k}] run summon minecraft:marker ~ ~ ~ {{Tags:[\"{NS}.otwin\",\"{NS}.t_{k}\",\"{NS}.tnew\"]}}" for k in POSES] +
    [f"scoreboard players operation @e[type=minecraft:marker,tag={NS}.tnew] m.pk = #k m.tmp", f"tag @e[type=minecraft:marker,tag={NS}.tnew] remove {NS}.tnew"] +
    [f"execute if entity @s[tag={NS}.o_{k}] run function {NS}:objets/effet_{k}" for k in POSES if k != "tente"]))
w(O_ + "jumeau.mcfunction", "\n".join(
    ["scoreboard players operation #k m.tmp = @s m.pk", "scoreboard players set #j m.tmp 0",
     f"execute as @e[type=minecraft:armor_stand,tag={NS}.obj,distance=..2] if score @s m.pk = #k m.tmp run scoreboard players set #j m.tmp 1",
     "execute if score #j m.tmp matches 1 run return 0",
     "kill @e[type=minecraft:item,distance=..3,nbt={Item:{id:\"minecraft:armor_stand\"}}]"] +
    [f"execute if entity @s[tag={NS}.t_{k}] as @p run function {NS}:objets/donner_{k}" for k in POSES] +
    ["kill @s"]))
w(O_ + "effet_epouvantail.mcfunction", "\n".join([
    "execute unless score @s m.ot matches 2.. run return 0", "scoreboard players set @s m.ot 0",
    f"execute as @e[type=#{NS}:hostiles,distance=..24,tag=!{NS}.boss] unless data entity @s CustomName run function {NS}:objets/chasser"]))
w(O_ + "chasser.mcfunction", "particle minecraft:poof ~ ~1 ~ 0.3 0.5 0.3 0.02 10\ntp @s ~ -400 ~\nkill @s")
w(O_ + "effet_piege.mcfunction", "\n".join([
    "execute if score @s m.ot matches ..20 run return 0",
    f"execute unless entity @e[type=#{NS}:hostiles,distance=..1.3] run return 0", "scoreboard players set @s m.ot 0",
    f"effect give @e[type=#{NS}:hostiles,distance=..1.3] minecraft:slowness 5 9", f"damage @e[type=#{NS}:hostiles,distance=..1.3,limit=1,sort=nearest] 6 minecraft:cactus",
    "playsound minecraft:block.iron_trapdoor.close master @a ~ ~ ~ 1 0.6"]))
wj(f"data/{NS}/tags/block/conteneurs.json", {"values": ["minecraft:chest", "minecraft:barrel", "minecraft:trapped_chest"]})
FI = ["execute if score @s m.ot matches ..239 run return 0", "scoreboard players set @s m.ot 0",
      "execute unless block ~ ~ ~ minecraft:water unless block ~ ~1 ~ minecraft:water run return 0",
      "scoreboard players set #ok m.tmp 0"]
for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0)):
    FI.append(f"execute if score #ok m.tmp matches 0 align xyz positioned ~{dx} ~{dy} ~{dz} if block ~ ~ ~ #{NS}:conteneurs run function {NS}:objets/filet_coffre")
FI += ["execute if score #ok m.tmp matches 0 run loot spawn ~ ~1 ~ loot minecraft:gameplay/fishing", "particle minecraft:splash ~ ~1 ~ 0.4 0.2 0.4 0 20"]
w(O_ + "effet_filet.mcfunction", "\n".join(FI))
w(O_ + "filet_coffre.mcfunction", "loot insert ~ ~ ~ loot minecraft:gameplay/fishing\nscoreboard players set #ok m.tmp 1")
w(O_ + "effet_mangeoire.mcfunction", "\n".join([
    "execute if score @s m.ot matches ..599 run return 0", "scoreboard players set @s m.ot 0",
    f"execute as @e[type=#{NS}:animaux,distance=..8,limit=12] if data entity @s {{Age:0}} run data modify entity @s InLove set value 600",
    "particle minecraft:heart ~ ~1 ~ 4 1 4 0 20"]))

# ---------------------------------------------------------------- arc du Chasseur (palier 5) et élytres de l'Explorateur (palier 6)
ARC = ('minecraft:bow[minecraft:custom_name={text:"Arc du Chasseur",color:"red",bold:true,italic:false},'
       'minecraft:lore=[{text:"Chaque tir lance trois flèches en éventail.",color:"gray",italic:false},{text:"Récompense du palier 5 de Chasseur",color:"gold",italic:false}],'
       'minecraft:item_model="metiers:forge_arc3",minecraft:custom_data={metiers_arc:1b},minecraft:enchantments={"minecraft:power":4},'
       'minecraft:unbreakable={},minecraft:max_stack_size=1,minecraft:rarity="epic"] 1')
ELY = ('minecraft:elytra[minecraft:custom_name={text:"Élytres de l\'Explorateur",color:"blue",bold:true,italic:false},'
       'minecraft:lore=[{text:"Incassables.",color:"gray",italic:false},{text:"Compétence Ailes de l\'Explorateur",color:"gold",italic:false}],'
       'minecraft:custom_data={metiers_elytres:1b},minecraft:unbreakable={},minecraft:rarity="epic"] 1')
w(O_ + "donner_arc.mcfunction", f"give @s {ARC}")
w(O_ + "donner_elytres.mcfunction", f"give @s {ELY}")
ARCSEL = "*[minecraft:custom_data~{metiers_arc:1b}]"
ELYSEL = "*[minecraft:custom_data~{metiers_elytres:1b}]"
add_lines(F + "refonte/tick.mcfunction", [
    f"execute as @a[scores={{s.bow2=1..}},tag={NS}.sk.c17] at @s run function {NS}:forge/arc3",
    f"execute as @a[scores={{s.bow2=1..}},tag=!{NS}.sk.c17] at @s if items entity @s weapon.mainhand {ARCSEL} run function {NS}:forge/arc3",
    "scoreboard players set @a s.bow2 0"])
add_lines(F + "refonte/load.mcfunction", ["scoreboard objectives add s.bow2 minecraft.used:minecraft.bow"])
for nom_, sel_, fn_, j_, pal_ in (("arc", ARCSEL, "donner_arc", "c", 5), ("elytres", ELYSEL, "donner_elytres", "x", 6)):
    cond_ = (f"execute unless entity @s[tag={NS}.sk.x9] run return run {tr('Il faut la compétence Ailes (Explorateur).', 'red')}" if nom_ == "elytres"
             else f"execute unless score @s m.{j_}_pal matches {pal_}.. run return run {tr(f'Il faut avoir récupéré la récompense du palier {pal_}.', 'red')}")
    w(O_ + f"recup_{nom_}.mcfunction", "\n".join([
        cond_,
        f"execute if items entity @s container.* {sel_} run return run {tr('Tu l’as déjà sur toi.', 'gold')}",
        f"execute if items entity @s armor.chest {sel_} run return run {tr('Tu l’as déjà sur toi.', 'gold')}",
        f"execute if items entity @s enderchest.* {sel_} run return run {tr('Il est dans ton coffre de l’Ender.', 'gold')}",
        f"execute if score @s m.ocd matches 1.. run return run {tr('Patiente quelques secondes.', 'red')}",
        "scoreboard players set @s m.ocd 20", f"function {NS}:objets/{fn_}"]))

# ---------------------------------------------------------------- fin des objets de la Forge : remboursement une fois, puis retrait
# prix payés à la Forge (copie de CRP et COMMUN de ref_menu.py, exécuté après ce fichier)
CRP = {"marteau": ("m", 260, 4, 50), "faux": ("f", 220, 3, 50), "arc3": ("c", 300, 5, 60), "lasso": ("e", 140, 1, 40), "parchemin": ("n", 60, 0, 40)}
COMMUN = {"aimant": 6, "cape": 12}
RB = [f"tag @s add {NS}.v26f"]
for key, (j_, p_, e_, lv_) in CRP.items():
    RB += [f"execute if score @s m.fo_{key} matches 1 run scoreboard players add @s m.cr_{j_} {p_}",
           f"execute if score @s m.fo_{key} matches 1 run scoreboard players add @s m.ecl {e_}"]
for key, e_ in COMMUN.items():
    RB.append(f"execute if score @s m.fo_{key} matches 1 run scoreboard players add @s m.ecl {e_}")
RB += [f"scoreboard players set @s m.fo_{key} 0" for key in list(CRP) + list(COMMUN)]
for j in ("m", "f", "e", "n", "t"):
    RB.append(f"execute if items entity @s container.* {SEL(j)} run function {NS}:{j}/outil_donner")
RB += [f"execute if entity @s[tag={NS}.sk.x9] run function {NS}:objets/donner_elytres",
       tr("Mise à jour 26 : les objets de la Forge disparaissent. Ce que tu avais payé (cristaux et éclats) t'est rendu, "
          "et leurs capacités passent sur tes outils de métier (voir l'onglet Outil).", "gold")]
w(O_ + "migration.mcfunction", "\n".join(RB))
RT = [f"execute unless entity @s[tag={NS}.v26f] run function {NS}:objets/migration"]
RT += [f"clear @s *[minecraft:custom_data~{{forge:\"{k}\"}}]" for k in FKEYS + ["lasso_plein"]]
for n in range(27):
    RT += [f"execute if items entity @s enderchest.{n} *[minecraft:custom_data~{{forge:\"{k}\"}}] run item replace entity @s enderchest.{n} with minecraft:air" for k in FKEYS]
w(O_ + "joueur.mcfunction", "\n".join(RT))
add_lines(F + "refonte/joueur.mcfunction", [f"execute if score #huit m.timer matches 0 run function {NS}:objets/joueur"])

# ---------------------------------------------------------------- houe du Fermier : récolte au clic droit (ancienne Faux), 3x3 puis 5x5
wj(f"data/{NS}/advancement/objets/houe.json", {"criteria": {"u": {"trigger": "minecraft:using_item", "conditions": {
    "item": {"items": "#minecraft:hoes", "predicates": {"minecraft:custom_data": "{metiers_outil:\"f\"}"}}}}},
    "rewards": {"function": f"{NS}:objets/houe"}})
HO = [f"advancement revoke @s only {NS}:objets/houe", "execute if score @s m.forgecd matches 1.. run return 0",
      f"execute unless entity @s[tag={NS}.sk.f15] run return 0", "scoreboard players set @s m.forgecd 2"]
for dx in range(-2, 3):
    for dz in range(-2, 3):
        cond = "" if max(abs(dx), abs(dz)) <= 1 else f"if entity @s[tag={NS}.sk.f18] "
        HO.append(f"execute {cond}positioned ~{dx} ~ ~{dz} run function {NS}:forge/faux_bloc")
HO += ["playsound minecraft:item.hoe.till master @s ~ ~ ~ 1 0.8", "particle minecraft:sweep_attack ~ ~0.5 ~ 1 0.2 1 0 4"]
w(O_ + "houe.mcfunction", "\n".join(HO))

# 26/11/2026 : la houe du Fermier reçoit le clic droit à tous les paliers (compétences Faux et Grande faux) : on la remet à jour une fois
add_lines(O_ + "joueur.mcfunction", [f'execute unless entity @s[tag={NS}.v27h] if items entity @s container.* {SEL("f")} run function {NS}:f/outil_donner',
                                     f"tag @s add {NS}.v27h"])

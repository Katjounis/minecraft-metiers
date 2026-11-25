# -*- coding: utf-8 -*-
# Spawners achetables et améliorables. Exécuté par datapack.py (partage w, F, NS, T, L, G, dlg, btn, btn_cmd, say, SOLDE...).
#
# Achat : touche G, Commerce, Spawners. L'objet porte custom_data {commerce_sp:{m,v,q,p,c}} (créature, niveaux).
# Pose : un joueur non op pose un spawner vide (le jeu ignore ses données) ; Commerce retient les données de
#   l'objet tenu, repère la pose (statistique used:spawner), suit le regard jusqu'au bloc posé et le remplit.
# Chaque spawner a un marqueur (propriétaire, créature, niveaux) et une entité interaction : clic droit = menu.
# L'interaction couvre le bloc, on ne peut pas le miner ; s'il disparaît quand même (explosion), il revient.
# Le propriétaire le ramasse depuis le menu, avec ses améliorations.
# XP : les créatures d'un spawner donnent la moitié de l'XP de Chasseur de Métiers (une dette retirée de m.c_bal),
#   les animaux naissent adultes et ne peuvent pas se reproduire, les moutons restent tondus : pas d'XP d'Éleveur.
import re as _re

_src = open(os.path.join(HERE, "..", "..", "metiers", "sources", "datapack.py"), encoding="utf-8").read()
XP_CH = eval(_re.search(r"^MOBS = (\{.*?\})$", _src, _re.M).group(1))      # XP de Chasseur par créature (Métiers)

ELEV = {"chicken", "pig", "rabbit", "sheep", "cow", "goat", "mooshroom", "hoglin"}
SPM = [("chicken", "Poulet", 20000), ("pig", "Cochon", 25000), ("rabbit", "Lapin", 25000), ("sheep", "Mouton", 30000),
       ("cow", "Vache", 30000), ("goat", "Chèvre", 35000), ("mooshroom", "Champimeuh", 45000),
       ("silverfish", "Poisson d'argent", 30000), ("zombie", "Zombie", 40000), ("spider", "Araignée", 45000),
       ("husk", "Zombie momifié", 45000), ("drowned", "Noyé", 50000), ("skeleton", "Squelette", 50000),
       ("cave_spider", "Araignée venimeuse", 50000), ("stray", "Vagabond", 55000), ("bogged", "Embourbé", 55000),
       ("slime", "Slime", 60000), ("zombified_piglin", "Piglin zombifié", 60000), ("magma_cube", "Cube de magma", 70000),
       ("creeper", "Creeper", 75000), ("piglin", "Piglin", 80000), ("phantom", "Phantom", 80000),
       ("witch", "Sorcière", 90000), ("hoglin", "Hoglin", 90000), ("pillager", "Pillard", 90000),
       ("guardian", "Gardien", 110000), ("enderman", "Enderman", 120000), ("blaze", "Blaze", 120000),
       ("vindicator", "Vindicateur", 130000), ("ghast", "Ghast", 150000), ("breeze", "Breeze", 160000),
       ("wither_skeleton", "Wither squelette", 180000), ("ravager", "Ravageur", 220000),
       ("shulker", "Shulker", 250000), ("evoker", "Évocateur", 500000)]
NSP = len(SPM)
# niveaux 0..3 : (délai min, délai max en ticks), créatures par vague, portée, créatures max autour
VIT = [(200, 800), (140, 560), (90, 360), (50, 200)]
QTE = [4, 5, 6, 8]
POR = [16, 24, 32, 48]
CAP = [6, 10, 14, 20]
COUT = [0, 40, 80, 150]          # % du prix du spawner pour atteindre le niveau
STATS = [("Vitesse", "v"), ("Quantité", "q"), ("Portée", "p"), ("Capacité", "c")]
BARRE = ["□□□", "■□□", "■■□", "■■■"]


def mille(n):
    return f"{n:,}".replace(",", " ")


def court_k(n):
    return f"{n // 1000} k" if n % 1000 == 0 else mille(n)


def sec(t):
    s = t / 20
    return (f"{s:.1f}".replace(".", ",")).replace(",0", "")


DESC = {
    1: [f"une vague toutes les {sec(a)} à {sec(b)} s" for a, b in VIT],
    2: [f"{n} créatures par vague" for n in QTE],
    3: [f"actif à {r} blocs d’un joueur" for r in POR],
    4: [f"s’arrête à {c} créatures autour" for c in CAP]}
SP = f"{NS}:sp"
SPU, SPB = f"{NS}:spu", f"{NS}:spb"     # pages (racine du storage = arguments de macro)
S = "scoreboard players"
SPI = "type=minecraft:interaction,tag=commerce.spi"
SPMK = "type=minecraft:marker,tag=commerce.sp"
egg = lambda m: f'{{object:"atlas",atlas:"minecraft:items",sprite:"minecraft:item/{m}_spawn_egg"}}'
OBJ = ["c.spid", "c.spc", "c.spm", "c.lv1", "c.lv2", "c.lv3", "c.lv4", "c.spd", "c.sdt"]

# ---------------------------------------------------------------- table des créatures (storage commerce:sp M[k-1])
ENT = []
for k, (m, nom, prix) in enumerate(SPM, 1):
    ex = ""
    if m in ELEV:
        ex += ",Age:2000000000"
    if m == "sheep":
        ex += ",Sheared:1b"
    wgt = XP_CH.get(m, 0)
    ent = {"id": m, "nom": nom, "ex": ex, "w": wgt}
    for L_ in (1, 2, 3):
        ent[f"c{L_}"] = mille(prix * COUT[L_] // 100)
    ENT.append(ent)
snbt_s = lambda v: '"' + str(v).replace('"', '\\"') + '"' if isinstance(v, str) else str(v)
M_SNBT = "[" + ",".join("{" + ",".join(f"{k}:{snbt_s(v)}" for k, v in e.items()) + "}" for e in ENT) + "]"
w(F + "spawner/load.mcfunction", [f"scoreboard objectives add {o} dummy" for o in OBJ] + [
    "scoreboard objectives add c.spu minecraft.used:minecraft.spawner",
    f"{S} add #spn c.g 0",
    f"data modify storage {SP} M set value {M_SNBT}"])
PRIX = [f"execute if score #m c.t matches {k} run {S} set #pp c.t {p}" for k, (_, _, p) in enumerate(SPM, 1)]
w(F + "spawner/prix.mcfunction", [f"{S} set #pp c.t 0"] + PRIX)
w(F + "spawner/fiche_m.mcfunction", f"$data modify storage {SP} e set from storage {SP} M[$(k)]")
w(F + "spawner/fiche.mcfunction", [
    "scoreboard players operation #x c.t = #m c.t", "scoreboard players remove #x c.t 1",
    f"execute store result storage {SP} f.k int 1 run scoreboard players get #x c.t",
    f"function {NS}:spawner/fiche_m with storage {SP} f"])

# ---------------------------------------------------------------- tick
w(F + "spawner/tick.mcfunction", [
    f"execute as @a[scores={{c.spu=1..}}] at @s run function {NS}:spawner/pose",
    f"execute as @a if items entity @s weapon.* minecraft:spawner[minecraft:custom_data~{{commerce_sp:{{}}}}] run function {NS}:spawner/memo",
    f"execute as @a[scores={{c.spm=1..}}] unless items entity @s weapon.* minecraft:spawner[minecraft:custom_data~{{commerce_sp:{{}}}}] run {S} set @s c.spm 0",
    f"execute as @e[{SPI}] if data entity @s interaction run function {NS}:spawner/clic_i",
    f"execute as @e[{SPI}] if data entity @s attack run data remove entity @s attack",
    f"{S} add #sp4 c.g 1",
    f"execute if score #sp4 c.g matches 4.. run function {NS}:spawner/morts"])
w(F + "spawner/seconde.mcfunction", [
    f"execute as @e[{SPMK}] at @s run function {NS}:spawner/garde",
    "execute as @e[type=minecraft:sheep,tag=commerce.spm] run data modify entity @s Sheared set value 1b"])

# ---------------------------------------------------------------- objet tenu : on retient ses données
for sl, path in (("main", "SelectedItem"), ("off", "equipment.offhand")):
    w(F + f"spawner/memo_{sl}.mcfunction", [
        f'execute store result score @s c.spm run data get entity @s {path}.components."minecraft:custom_data".commerce_sp.m'] + [
        f'execute store result score @s c.lv{n} run data get entity @s {path}.components."minecraft:custom_data".commerce_sp.{k}'
        for n, (_, k) in enumerate(STATS, 1)])
w(F + "spawner/memo.mcfunction", [
    f"execute if items entity @s weapon.mainhand minecraft:spawner[minecraft:custom_data~{{commerce_sp:{{}}}}] run return run function {NS}:spawner/memo_main",
    f"function {NS}:spawner/memo_off"])

# ---------------------------------------------------------------- pose : le premier spawner sur la ligne du regard
w(F + "spawner/pose.mcfunction", [
    f"{S} set @s c.spu 0",
    "execute unless score @s c.spm matches 1.. run return 0",
    f"{S} set #ray c.t 0",
    f"execute anchored eyes positioned ^ ^ ^ run function {NS}:spawner/rayon"])
w(F + "spawner/rayon.mcfunction", [
    f"execute if block ~ ~ ~ minecraft:spawner align xyz positioned ~0.5 ~0.5 ~0.5 unless entity @e[{SPMK},distance=..0.3] run return run function {NS}:spawner/installer",
    "execute if block ~ ~ ~ minecraft:spawner run return 0",
    f"{S} add #ray c.t 1",
    f"execute if score #ray c.t matches ..70 positioned ^ ^ ^0.1 run function {NS}:spawner/rayon"])
w(F + "spawner/installer.mcfunction", [
    f"{S} add #spn c.g 1",
    'summon minecraft:marker ~ ~ ~ {Tags:["commerce.sp","commerce.spn"]}',
    'summon minecraft:interaction ~ ~-0.52 ~ {Tags:["commerce.spi","commerce.spn"],width:1.04f,height:1.04f,response:1b}',
    f"{S} operation @e[tag=commerce.spn,distance=..1] c.spid = #spn c.g",
    f"{S} operation @e[{SPMK},tag=commerce.spn,distance=..1] c.own = @s m.id",
    f"{S} operation @e[{SPMK},tag=commerce.spn,distance=..1] c.spm = @s c.spm"] + [
    f"{S} operation @e[{SPMK},tag=commerce.spn,distance=..1] c.lv{n} = @s c.lv{n}" for n in range(1, 5)] + [
    f"execute as @e[{SPMK},tag=commerce.spn,distance=..1] at @s run function {NS}:spawner/appliquer",
    "tag @e[tag=commerce.spn,distance=..1] remove commerce.spn",
    f"{S} set @s c.spm 0",
    "particle minecraft:flame ~ ~ ~ 0.4 0.4 0.4 0.01 25",
    "playsound minecraft:block.respawn_anchor.charge master @s ~ ~ ~ 1 1.2",
    say("Spawner posé. Clic droit dessus pour ses améliorations ; toi seul peux l’améliorer et le ramasser.", "green")])

# ---------------------------------------------------------------- réglage du bloc depuis le marqueur (exécuté en @s = marqueur, à sa place)
AP = ["scoreboard players operation #m c.t = @s c.spm", f"function {NS}:spawner/fiche",
      f"data modify storage {SP} a set value {{}}",
      f"data modify storage {SP} a.id set from storage {SP} e.id", f"data modify storage {SP} a.ex set from storage {SP} e.ex",
      f"data modify storage {SP} a.w set from storage {SP} e.w"]
for n, vals in ((1, None), (2, QTE), (3, POR), (4, CAP)):
    for L_ in range(4):
        if n == 1:
            AP += [f"execute if score @s c.lv1 matches {L_} run data modify storage {SP} a.d0 set value {VIT[L_][0]}",
                   f"execute if score @s c.lv1 matches {L_} run data modify storage {SP} a.d1 set value {VIT[L_][1]}"]
        else:
            AP.append(f"execute if score @s c.lv{n} matches {L_} run data modify storage {SP} a.s{n} set value {vals[L_]}")
AP.append(f"function {NS}:spawner/appliquer_m with storage {SP} a")
w(F + "spawner/appliquer.mcfunction", AP)
w(F + "spawner/appliquer_m.mcfunction",
  '$data merge block ~ ~ ~ {SpawnData:{entity:{id:"minecraft:$(id)",Tags:["commerce.spm","commerce.w$(w)"]$(ex)},'
  'custom_spawn_rules:{block_light_limit:[0,15],sky_light_limit:[0,15]}},SpawnPotentials:[],Delay:40s,'
  'MinSpawnDelay:$(d0)s,MaxSpawnDelay:$(d1)s,SpawnCount:$(s2)s,RequiredPlayerRange:$(s3)s,MaxNearbyEntities:$(s4)s,SpawnRange:4s}')
# chaque seconde : le bloc est là, l'interaction aussi
w(F + "spawner/garde.mcfunction", [
    f"execute unless block ~ ~ ~ minecraft:spawner run function {NS}:spawner/restaurer",
    f"execute unless entity @e[{SPI},distance=..0.8] run function {NS}:spawner/interaction"])
w(F + "spawner/restaurer.mcfunction", [
    "setblock ~ ~ ~ minecraft:spawner", f"function {NS}:spawner/appliquer",
    "kill @e[type=minecraft:experience_orb,distance=..3]",
    "kill @e[type=minecraft:item,distance=..2,nbt={Item:{id:\"minecraft:spawner\"}}]",
    "particle minecraft:reverse_portal ~ ~ ~ 0.4 0.4 0.4 0.05 40",
    "playsound minecraft:block.respawn_anchor.set_spawn block @a ~ ~ ~ 1 1"])
w(F + "spawner/interaction.mcfunction", [
    'summon minecraft:interaction ~ ~-0.52 ~ {Tags:["commerce.spi","commerce.spn"],width:1.04f,height:1.04f,response:1b}',
    f"{S} operation @e[{SPI},tag=commerce.spn,distance=..1] c.spid = @s c.spid",
    "tag @e[tag=commerce.spn,distance=..1] remove commerce.spn"])

# ---------------------------------------------------------------- XP : la moitié du Chasseur, rien pour l'Éleveur
WS = sorted({e["w"] for e in ENT if e["w"]})
w(F + "spawner/morts.mcfunction", [
    f"{S} set #sp4 c.g 0",
    "execute as @e[tag=commerce.spm,tag=!commerce.mort] store result score @s c.sdt run data get entity @s DeathTime",
    f"execute as @e[tag=commerce.spm,tag=!commerce.mort,scores={{c.sdt=1..}}] run function {NS}:spawner/mort"])
w(F + "spawner/mort.mcfunction", ["tag @s add commerce.mort", f"{S} set #w c.t 0"] + [
    f"execute if entity @s[tag=commerce.w{x}] run {S} set #w c.t {x}" for x in WS] + [
    "execute if score #w c.t matches 0 run return 0",
    f"execute on attacker if entity @s[type=minecraft:player] run function {NS}:spawner/xp"])
# c.spd compte des demi-points d'XP ; chaque point entier est retiré de la réserve d'XP de Chasseur de Métiers
w(F + "spawner/xp.mcfunction", [
    "scoreboard players operation @s c.spd += #w c.t",
    "scoreboard players operation #h c.t = @s c.spd", "scoreboard players operation #h c.t /= #2 c.g",
    "scoreboard players operation @s m.c_bal -= #h c.t",
    "scoreboard players operation #h c.t *= #2 c.g", "scoreboard players operation @s c.spd -= #h c.t"])

# ---------------------------------------------------------------- clic droit : menu du spawner
w(F + "spawner/clic_i.mcfunction", [
    "scoreboard players operation #sid c.t = @s c.spid",
    f"execute on target run function {NS}:spawner/ouvrir",
    "data remove entity @s interaction"])
w(F + "spawner/ouvrir.mcfunction", ["scoreboard players operation @s c.spc = #sid c.t", f"function {NS}:spawner/menu"])
# retrouve le spawner courant du joueur (à 10 blocs au plus) : #trouve, #own, #m, #l1..#l4, tag commerce.sel
w(F + "spawner/trouver.mcfunction", [
    "scoreboard players operation #sid c.t = @s c.spc", f"{S} set #trouve c.t 0",
    f"tag @e[{SPMK},tag=commerce.sel] remove commerce.sel",
    "tag @s add commerce.moi",
    f"execute as @e[{SPMK}] if score @s c.spid = #sid c.t at @s if entity @a[tag=commerce.moi,distance=..10] run function {NS}:spawner/lire",
    "tag @s remove commerce.moi",
    f"{S} set #pro c.t 0",
    "execute if score #trouve c.t matches 1 if score #own c.t = @s m.id run scoreboard players set #pro c.t 1"])
w(F + "spawner/lire.mcfunction", [
    f"{S} set #trouve c.t 1", "tag @s add commerce.sel",
    "scoreboard players operation #own c.t = @s c.own", "scoreboard players operation #m c.t = @s c.spm"] + [
    f"scoreboard players operation #l{n} c.t = @s c.lv{n}" for n in range(1, 5)])
LOIN = say("Approche-toi du spawner (10 blocs au plus).", "red")
MN = [f"function {NS}:spawner/trouver",
      f"execute if score #trouve c.t matches 0 run return run {LOIN}",
      f"function {NS}:spawner/fiche", "function commerce:spawner/prix",
      f"data modify storage {SPU} nom set from storage {SP} e.nom", f"data modify storage {SPU} id set from storage {SP} e.id",
      f'data modify storage {SPU} own set value "?"',
      f"execute store result storage {SP} o.id int 1 run scoreboard players get #own c.t",
      f"function {NS}:spawner/nom_proprio with storage {SP} o"]
for n in range(1, 5):
    nom = STATS[n - 1][0]
    for L_ in range(4):
        MN.append(f'execute if score #l{n} c.t matches {L_} run data modify storage {SPU} d{n} set value "{DESC[n][L_]}"')
        if L_ == 3:
            MN += [f'execute if score #l{n} c.t matches 3 run data modify storage {SPU} n{n} set value "{nom}  {BARRE[3]}  au maximum"',
                   f'execute if score #l{n} c.t matches 3 run data modify storage {SPU} k{n} set value "dark_gray"',
                   f'execute if score #l{n} c.t matches 3 run data modify storage {SPU} c{n} set value ""',
                   f'execute if score #l{n} c.t matches 3 run data modify storage {SPU} t{n} set value "Niveau maximum : {DESC[n][3]}."']
        else:
            MN += [f'execute if score #l{n} c.t matches {L_} run data modify storage {SPU} n{n} set value "{nom}  {BARRE[L_]}  → "',
                   f'execute if score #l{n} c.t matches {L_} run data modify storage {SPU} k{n} set value "yellow"',
                   f"execute if score #l{n} c.t matches {L_} run data modify storage {SPU} c{n} set from storage {SP} e.c{L_ + 1}",
                   f'execute if score #l{n} c.t matches {L_} run data modify storage {SPU} t{n} set value "Niveau {L_ + 1} : {DESC[n][L_ + 1]}."']
    MN += [f'execute if score #pro c.t matches 0 run data modify storage {SPU} k{n} set value "dark_gray"',
           f'execute if score #pro c.t matches 0 run data modify storage {SPU} t{n} set value "Réservé au propriétaire."']
MN += [f'data modify storage {SPU} kr set value "gold"',
       f'execute if score #pro c.t matches 0 run data modify storage {SPU} kr set value "dark_gray"']
MN += SOLDE(SPU) + msg_line(SPU) + [f"function {NS}:spawner/menu_d with storage {SPU}"]
w(F + "spawner/menu.mcfunction", MN)
w(F + "spawner/nom_proprio.mcfunction", f"$data modify storage {SPU} own set from storage {NS}:j l[{{id:$(id)}}].nom")
ACT_SP = [btn_cmd(L(T("$(n" + str(n) + ")", "$(k" + str(n) + ")", True), T("$(c" + str(n) + ")", "gold")), f"trigger commerce set {7300 + n}", "$(t" + str(n) + ")") for n in range(1, 5)]
ACT_SP += [btn_cmd(T("Ramasser le spawner", "$(kr)", True), "trigger commerce set 7310", "Le reprend dans ton inventaire, avec ses améliorations (propriétaire seulement)."),
           btn_cmd(T("Mode d’emploi", "white"), "trigger commerce set 7000")]
w(F + "spawner/menu_d.mcfunction", "$" + dlg(
    T("Spawner : $(nom)", "light_purple", True),
    [f'{{type:"minecraft:item",item:{{id:"minecraft:$(id)_spawn_egg"}},show_decorations:false,description:{{width:270,contents:{L(T("Propriétaire : ", "gray"), T("$(own)", "white", True), T("\\nVitesse : $(d1)\\nQuantité : $(d2)\\nPortée : $(d3)\\nCapacité : $(d4)", "gray"))}}}}}',
     f'{{type:"minecraft:plain_message",width:310,contents:{L(SOLDE_TXT, T("   ·   prix d’amélioration sur chaque bouton", "dark_gray"), T("\\n$(msg)", "yellow"))}}}'],
    ACT_SP))

# ---------------------------------------------------------------- amélioration (7301..7304) et ramassage (7310)
for n in range(1, 5):
    w(F + f"spawner/ameliorer_{n}.mcfunction", [
        f"function {NS}:spawner/trouver",
        f"execute if score #trouve c.t matches 0 run return run {LOIN}",
        f'execute if score #pro c.t matches 0 run return run function {NS}:spawner/msg {{m:"Seul le propriétaire peut améliorer ce spawner."}}',
        f'execute if score #l{n} c.t matches 3.. run return run function {NS}:spawner/msg {{m:"{STATS[n - 1][0]} est déjà au maximum."}}',
        f"function {NS}:spawner/prix",
        "scoreboard players operation #cout c.t = #pp c.t"] + [
        f"execute if score #l{n} c.t matches {L_ - 1} run scoreboard players set #pc c.t {COUT[L_]}" for L_ in (1, 2, 3)] + [
        "scoreboard players operation #cout c.t *= #pc c.t", "scoreboard players operation #cout c.t /= #100 c.g",
        f"execute if score @s c.ecus < #cout c.t run return run function {NS}:spawner/msg {{m:\"Pas assez d'Écus pour cette amélioration.\"}}",
        "scoreboard players operation @s c.ecus -= #cout c.t", "scoreboard players operation @s c.ta += #cout c.t",
        f"scoreboard players add @e[{SPMK},tag=commerce.sel,limit=1] c.lv{n} 1",
        f"execute as @e[{SPMK},tag=commerce.sel,limit=1] at @s run function {NS}:spawner/appliquer",
        f"execute at @e[{SPMK},tag=commerce.sel,limit=1] run particle minecraft:happy_villager ~ ~ ~ 0.5 0.5 0.5 0 30",
        "playsound minecraft:block.anvil.use master @s ~ ~ ~ 0.7 1.4",
        f'data modify storage {NS}:t msg set value "{STATS[n - 1][0]} améliorée."',
        f"function {NS}:spawner/menu"])
w(F + "spawner/msg.mcfunction", [f"$data modify storage {NS}:t msg set value \"$(m)\"", "playsound minecraft:entity.villager.no master @s ~ ~ ~ 0.8 1",
                                  f"function {NS}:spawner/menu"])
w(F + "spawner/ramasser.mcfunction", [
    f"function {NS}:spawner/trouver",
    f"execute if score #trouve c.t matches 0 run return run {LOIN}",
    f'execute if score #pro c.t matches 0 run return run function {NS}:spawner/msg {{m:"Seul le propriétaire peut ramasser ce spawner."}}',
    f"function {NS}:spawner/fiche",
    f"data modify storage {SP} g set value {{}}", f"data modify storage {SP} g.nom set from storage {SP} e.nom",
    f"execute store result storage {SP} g.m int 1 run scoreboard players get #m c.t"] + [
    f"execute store result storage {SP} g.{k} int 1 run scoreboard players get #l{n} c.t" for n, (_, k) in enumerate(STATS, 1)] + [
    f"function {NS}:spawner/donner with storage {SP} g",
    f"execute at @e[{SPMK},tag=commerce.sel,limit=1] run kill @e[{SPI},distance=..0.8]",
    f"execute at @e[{SPMK},tag=commerce.sel,limit=1] run setblock ~ ~ ~ minecraft:air",
    f"execute at @e[{SPMK},tag=commerce.sel,limit=1] run particle minecraft:poof ~ ~ ~ 0.3 0.3 0.3 0.02 20",
    f"kill @e[{SPMK},tag=commerce.sel,limit=1]",
    "playsound minecraft:item.bundle.insert master @s ~ ~ ~ 1 0.8",
    say("Spawner ramassé, avec ses améliorations.", "green")])
w(F + "spawner/donner.mcfunction",
  '$give @s minecraft:spawner[minecraft:custom_name={text:"Spawner : $(nom)",color:"light_purple",bold:true,italic:false},'
  'minecraft:lore=[{text:"Vitesse $(v)/3  ·  Quantité $(q)/3",color:"gray",italic:false},{text:"Portée $(p)/3  ·  Capacité $(c)/3",color:"gray",italic:false},'
  '{text:"Pose-le, puis clic droit dessus pour l’améliorer.",color:"dark_gray",italic:false}],'
  'minecraft:custom_data={commerce_sp:{m:$(m),v:$(v),q:$(q),p:$(p),c:$(c)}},minecraft:max_stack_size=1,'
  'minecraft:rarity="epic",minecraft:enchantment_glint_override=true] 1')

# ---------------------------------------------------------------- boutique : 70 = première page, 700 + p, fiche 7100 + k, achat 7200 + k
PSP = 10
NPSP = (NSP + PSP - 1) // PSP
for p in range(NPSP):
    lot = list(enumerate(SPM, 1))[p * PSP:(p + 1) * PSP]
    acts = [btn(L(egg(m), T("  " + nom, "white"), T("  " + court_k(prix), "gold")), 7100 + k, 160,
                f"{nom}\\nPrix : {mille(prix)} Écus\\nXP de Chasseur : {'moitié' if XP_CH.get(m) else 'aucune'}") for k, (m, nom, prix) in lot]
    if len(lot) % 2:
        acts.append(VIDE)
    acts.append(btn(T("◀  Page précédente", "white"), 700 + p - 1, 160) if p > 0 else VIDE)
    acts.append(btn(T("Page suivante  ▶", "white"), 700 + p + 1, 160) if p < NPSP - 1 else VIDE)
    acts += [btn(T("Mode d’emploi", "aqua", True), 7000, 160), btn(T("Accueil", "white"), 1, 160)]
    w(F + f"spawner/boutique_{p}.mcfunction", SOLDE(SPB) + [f"function {NS}:spawner/boutique_{p}_d with storage {SPB}"])
    w(F + f"spawner/boutique_{p}_d.mcfunction", "$" + dlg(
        T("Spawners", "light_purple", True),
        [f'{{type:"minecraft:plain_message",width:310,contents:{L(SOLDE_TXT, T(f"   ·   page {p + 1}/{NPSP}   ·   prix au survol", "gray"))}}}'], acts))
for k, (m, nom, prix) in enumerate(SPM, 1):
    p = (k - 1) // PSP
    xp = "la moitié de l’XP de Chasseur habituelle" if XP_CH.get(m) else "pas d’XP de Chasseur"
    desc = [T(f"Spawner : {nom}", "light_purple", True), T(f"\\nPrix : ", "gray"), T(f"{mille(prix)} " + ECU, "gold", True),
            T(f"\\nDe base : {DESC[1][0]}, {DESC[2][0]}, {DESC[3][0]}.", "gray"),
            T(f"\\nSes créatures donnent {xp}" + (", et ne se reproduisent pas." if m in ELEV else "."), "gray")]
    w(F + f"spawner/fiche_{k}.mcfunction", SOLDE(SPB) + msg_line(SPB) + [f"function {NS}:spawner/fiche_{k}_d with storage {SPB}"])
    w(F + f"spawner/fiche_{k}_d.mcfunction", "$" + dlg(
        T(f"Spawner : {nom}", "light_purple", True),
        [f'{{type:"minecraft:item",item:{{id:"minecraft:{m}_spawn_egg"}},show_decorations:false,description:{{width:270,contents:{L(*desc)}}}}}',
         f'{{type:"minecraft:plain_message",width:310,contents:{L(SOLDE_TXT, T("\\n$(msg)", "yellow"))}}}'],
        [btn(L(T("Acheter  ", "gold", True), T(f"{mille(prix)} ", "white"), ECU_C), 7200 + k, 160, "L’objet arrive dans ton inventaire."),
         btn(T("Mode d’emploi", "aqua"), 7000, 160), btn(T("Retour : spawners", "white"), 700 + p, 160), btn(T("Accueil", "white"), 1, 160)]))
    w(F + f"spawner/acheter_{k}.mcfunction", [
        f"execute if score @s c.ecus matches ..{prix - 1} run return run function {NS}:spawner/pauvre {{k:{k}}}",
        f"scoreboard players remove @s c.ecus {prix}", f"scoreboard players add @s c.ta {prix}",
        f'function {NS}:spawner/donner {{nom:"{nom}",m:{k},v:0,q:0,p:0,c:0}}',
        "playsound minecraft:entity.villager.trade master @s ~ ~ ~ 0.8 1",
        "playsound minecraft:block.respawn_anchor.charge master @s ~ ~ ~ 0.6 1.4",
        f'data modify storage {NS}:t msg set value "Spawner acheté : il est dans ton inventaire. Pose-le, puis clic droit dessus."',
        f'tellraw @a {L(PREFIX, "{selector:\"@s\",color:\"white\"}", T(f" s’offre un spawner : {nom} !", "light_purple"))}',
        f"function {NS}:spawner/fiche_{k}"])
w(F + "spawner/pauvre.mcfunction", [f'data modify storage {NS}:t msg set value "Pas assez d\'Écus pour ce spawner."',
                                     "playsound minecraft:entity.villager.no master @s ~ ~ ~ 0.8 1", f"$function {NS}:spawner/fiche_$(k)"])

# ---------------------------------------------------------------- mode d'emploi illustré (7000)
ill = lambda item, titre, txt: (f'{{type:"minecraft:item",item:{{id:"minecraft:{item}"}},show_decorations:false,'
                                f'description:{{width:260,contents:{L(T(titre, "gold", True), T(chr(92) + "n" + txt, "gray"))}}}}}')
w(F + "spawner/aide.mcfunction", dlg(
    T("Spawners : mode d’emploi", "light_purple", True),
    [ill("spawner", "Acheter, poser", "Touche G, Commerce, Spawners. Pose-le où tu veux : il marche même éclairé. Clic droit dessus : son menu."),
     ill("clock", "Vitesse", f"Une vague toutes les {sec(VIT[0][0])} à {sec(VIT[0][1])} s, jusqu’à {sec(VIT[3][0])} à {sec(VIT[3][1])} s au niveau 3."),
     ill("zombie_spawn_egg", "Quantité", f"{QTE[0]} créatures par vague, jusqu’à {QTE[3]}."),
     ill("spyglass", "Portée", f"Tourne si un joueur est à {POR[0]} blocs, jusqu’à {POR[3]} blocs."),
     ill("chest", "Capacité", f"S’arrête à {CAP[0]} créatures autour, jusqu’à {CAP[3]}."),
     ill("iron_sword", "XP de métier", "Ses créatures donnent la moitié de l’XP de Chasseur. Les animaux ne se reproduisent pas et les moutons restent tondus : pas d’XP d’Éleveur."),
     ill("obsidian", "Incassable, à toi", "Personne ne peut le miner ; s’il explose, il revient. Toi seul l’améliores et le ramasses (bouton du menu), améliorations gardées.")],
    [btn(T("Spawners", "light_purple", True), 70, 160), btn(T("Accueil", "white"), 1, 160)]))

# ---------------------------------------------------------------- aiguillage (appelé par trigger/entree pour 70, 700.., 7000..)
RT = [f"execute if score #v c.t matches 70 run return run function {NS}:spawner/boutique_0"]
RT += [f"execute if score #v c.t matches {700 + p} run return run function {NS}:spawner/boutique_{p}" for p in range(NPSP)]
RT += [f"execute if score #v c.t matches {7100 + k} run return run function {NS}:spawner/fiche_{k}" for k in range(1, NSP + 1)]
RT += [f"execute if score #v c.t matches {7200 + k} run return run function {NS}:spawner/acheter_{k}" for k in range(1, NSP + 1)]
RT += [f"execute if score #v c.t matches {7300 + n} run return run function {NS}:spawner/ameliorer_{n}" for n in range(1, 5)]
RT += [f"execute if score #v c.t matches 7310 run return run function {NS}:spawner/ramasser",
       f"execute if score #v c.t matches 7311 run return run function {NS}:spawner/menu"]
w(F + "spawner/entree.mcfunction", RT)
w(F + "spawner/desinstaller.mcfunction", [f"kill @e[{SPI}]", f"kill @e[{SPMK}]"] + [f"scoreboard objectives remove {o}" for o in OBJ + ["c.spu"]])
w(F + "admin/spawner.mcfunction", [f'function {NS}:spawner/donner {{nom:"Zombie",m:9,v:0,q:0,p:0,c:0}}', say("Spawner de zombie donné (admin).", "gold")])

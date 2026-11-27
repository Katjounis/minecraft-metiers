# -*- coding: utf-8 -*-
# 27/11/2026 : refonte des attaques des 5 boss de Métiers.
#
# Constat : le Creeper géant tombait en moins d'une minute à l'épée. Ses explosions faisaient des dégâts fixes
# (8 à 12) de type explosion, quasi annulés par l'armure de métier (netherite, Protection), ses rejetons avaient
# ExplosionRadius 0 donc ne faisaient rien, et rien ne punissait le fait de rester collé à le frapper.
#
# Principes de la refonte :
# - AUCUN bloc cassé ni posé : pas d'explosion vanilla, uniquement des commandes damage, des particules, des sons,
#   des markers et des block_display (des entités, pas des blocs).
# - Attaques annoncées : un cercle rouge au sol pendant 1 à 2 s, puis l'impact. On les évite en sortant du cercle
#   (ou en sautant pour l'onde du Colosse). Les dégâts passent par le type metiers:boss qui ignore l'armure et ses
#   enchantements : l'esquive est la vraie défense (le bouclier et la Résistance marchent toujours).
# - Rang du boss : score de métiers (somme des niveaux, prestige compris) du meilleur joueur à 64 blocs du point
#   d'apparition, par paliers de 50 (rang 0 à 20). Le rang fixe PV, armure, dégâts, cadence et récompenses.
# - Anti-spam : chaque boss compte les coups reçus sur 3 s. Au-delà d'un seuil (5 en solo, +2 par joueur proche),
#   il riposte (contre, morsure, repli, combustion, fuite de gaz). Le Creeper a en plus une aura de gaz au contact.

PLB = "gamemode=!spectator,gamemode=!creative"
SB = "scoreboard players"
B2 = f"{NS}:boss2/"
FB = F + "boss2/"
DM = f"with storage {NS}:boss dm"

# ---------------------------------------------------------------- type de dégâts : ignore l'armure et ses enchantements
wj(f"data/{NS}/damage_type/boss.json", {"message_id": "generic", "exhaustion": 0.0, "scaling": "never"})
for _tag in ("bypasses_armor", "bypasses_enchantments"):
    _p = os.path.join(ROOT, f"data/minecraft/tags/damage_type/{_tag}.json")
    _v = json.load(open(_p, encoding="utf-8"))["values"] if os.path.exists(_p) else []
    if f"{NS}:boss" not in _v:
        _v.append(f"{NS}:boss")
    wj(f"data/minecraft/tags/damage_type/{_tag}.json", {"replace": False, "values": _v})

# ---------------------------------------------------------------- dessin d'un cercle au sol
import math as _m
_RINGS = {}
def anneau(r, part='minecraft:dust{color:[1.0,0.25,0.1],scale:1.4}'):
    """Nom d'une fonction qui dessine un cercle de rayon r (couleur d'alerte par défaut)."""
    cle = (r, part)
    if cle not in _RINGS:
        nom = f"anneau_{len(_RINGS)}"
        n = max(12, round(2 * _m.pi * r / 0.7))
        L = [f"particle {part} ~{r * _m.cos(2 * _m.pi * i / n):.2f} ~0.15 ~{r * _m.sin(2 * _m.pi * i / n):.2f} 0 0 0 0 1 force"
             for i in range(n)]
        w(FB + nom + ".mcfunction", "\n".join(L))
        _RINGS[cle] = nom
    return B2 + _RINGS[cle]

# ---------------------------------------------------------------- zones annoncées (marker + compte à rebours)
# nom : (rayon, durée d'annonce en demi-secondes, dégâts s/m/l, au sol seulement, effets sur chaque touché,
#        effets visuels de l'impact, commandes après impact exécutées par le marker)
BOOM = ["particle minecraft:explosion_emitter ~ ~0.5 ~ 0 0 0 0 1 force", "playsound minecraft:entity.generic.explode hostile @a ~ ~ ~ 2 0.8"]
SAUT = [f"execute if function {NS}:boss/place_ok run tp @e[tag=metiers.boss,limit=1] ~ ~ ~"]
K = {
    # Colosse
    "marteau":  (2.5, 3, "m", False, ["effect give @s minecraft:slowness 2 1"],
                 ["particle minecraft:explosion ~ ~0.3 ~ 1 0.1 1 0 6 force", "playsound minecraft:block.anvil.land hostile @a ~ ~ ~ 1.5 0.5"], []),
    "onde":     (7, 3, "m", True, ["effect give @s minecraft:levitation 1 2 true"],
                 ["particle minecraft:sweep_attack ~ ~0.5 ~ 4 0.2 4 0 40 force", "particle minecraft:cloud ~ ~0.3 ~ 5 0.1 5 0.2 80 force",
                  "playsound minecraft:entity.iron_golem.attack hostile @a ~ ~ ~ 2 0.4"], []),
    "saut":     (3.5, 3, "l", False, ["effect give @s minecraft:levitation 1 1 true"], BOOM + ["playsound minecraft:entity.ravager.roar hostile @a ~ ~ ~ 1.5 0.7"], SAUT),
    "contre":   (4.5, 1, "m", False, ["effect give @s minecraft:levitation 1 2 true"],
                 ["particle minecraft:sweep_attack ~ ~1 ~ 2.5 0.3 2.5 0 25 force", "playsound minecraft:item.shield.block hostile @a ~ ~ ~ 2 0.5"], []),
    # Reine arachnide
    "crachat":  (3, 3, "m", False, ["effect give @s minecraft:poison 5 1"],
                 ["particle minecraft:item_slime ~ ~0.5 ~ 1.5 0.3 1.5 0 40 force", "playsound minecraft:entity.spider.hurt hostile @a ~ ~ ~ 1.5 0.5"], []),
    "bondreine": (3, 3, "l", False, ["effect give @s minecraft:poison 3 0"], BOOM, SAUT),
    # Liche du givre
    "pic":      (2, 2, "m", False, ["effect give @s minecraft:slowness 3 2"],
                 ["particle minecraft:snowflake ~ ~1 ~ 0.6 1 0.6 0.05 40 force", "particle minecraft:block{block_state:\"minecraft:packed_ice\"} ~ ~0.5 ~ 0.6 0.6 0.6 0 30 force",
                  "playsound minecraft:block.glass.break hostile @a ~ ~ ~ 1.5 0.6"], []),
    "blizzard": (2, 3, "m", False, ["effect give @s minecraft:slowness 2 1"],
                 ["particle minecraft:snowflake ~ ~1 ~ 0.8 1 0.8 0.05 40 force", "playsound minecraft:block.powder_snow.break hostile @a ~ ~ ~ 1.5 0.5"], []),
    "nova":     (5, 2, "m", False, ["effect give @s minecraft:slowness 3 2", "effect give @s minecraft:weakness 3 0"],
                 ["particle minecraft:snowflake ~ ~1 ~ 3 0.5 3 0.1 150 force", "playsound minecraft:block.glass.break hostile @a ~ ~ ~ 2 0.4"], []),
    "givre":    (4, 2, "m", False, ["effect give @s minecraft:slowness 3 3"],
                 ["particle minecraft:snowflake ~ ~1 ~ 2.5 0.5 2.5 0.1 120 force", "playsound minecraft:block.glass.break hostile @a ~ ~ ~ 2 0.5"], []),
    # Brasier ancestral
    "braise":   (2, 3, "m", False, [],
                 ["particle minecraft:lava ~ ~0.3 ~ 0.6 0.2 0.6 0 10 force", "particle minecraft:flame ~ ~0.5 ~ 0.8 0.5 0.8 0.05 40 force",
                  "playsound minecraft:entity.blaze.shoot hostile @a ~ ~ ~ 1.2 0.6"], []),
    "nova_feu": (8, 3, "m", False, ["effect give @s minecraft:levitation 1 1 true"],
                 ["particle minecraft:flame ~ ~0.5 ~ 5 0.3 5 0.15 250 force", "playsound minecraft:item.firecharge.use hostile @a ~ ~ ~ 2 0.5"], []),
    "meteore":  (4, 4, "l", False, ["effect give @s minecraft:blindness 1 0 true"],
                 BOOM + ["particle minecraft:lava ~ ~0.5 ~ 2 0.3 2 0 40 force", "particle minecraft:flame ~ ~6 ~ 0.3 3 0.3 0 80 force"], []),
    # Creeper géant
    "detonation": (3.5, 3, "l", False, ["effect give @s minecraft:levitation 1 1 true"], BOOM, []),
    "fusion":   (8, 4, "l", False, ["effect give @s minecraft:levitation 1 2 true"],
                 BOOM + ["particle minecraft:explosion ~ ~1 ~ 4 0.5 4 0 30 force", "particle minecraft:happy_villager ~ ~1 ~ 5 1 5 0 60 force"], []),
    "bondcreeper": (3.5, 3, "l", False, ["effect give @s minecraft:levitation 1 1 true"], BOOM, SAUT),
    "gaz":      (4.5, 1, "m", False, ["effect give @s minecraft:levitation 1 2 true", "effect give @s minecraft:nausea 4 0 true"],
                 ["particle minecraft:explosion ~ ~1 ~ 2 0.5 2 0 15 force", "particle minecraft:happy_villager ~ ~1 ~ 3 1 3 0 50 force",
                  "playsound minecraft:entity.creeper.hurt hostile @a ~ ~ ~ 2 0.5", "playsound minecraft:entity.generic.explode hostile @a ~ ~ ~ 1.5 1.2"], []),
    # explosions immédiates (mines, rejetons)
    "petard":   (3, 0, "m", False, ["effect give @s minecraft:levitation 1 1 true"], BOOM, []),
}
SONS_ALERTE = {"onde": "minecraft:entity.ravager.stunned", "fusion": "minecraft:entity.creeper.primed", "nova_feu": "minecraft:entity.blaze.ambient",
               "meteore": "minecraft:entity.blaze.shoot", "saut": "minecraft:entity.ravager.attack", "bondreine": "minecraft:entity.spider.ambient",
               "bondcreeper": "minecraft:entity.creeper.primed", "nova": "minecraft:entity.stray.ambient", "gaz": "minecraft:entity.creeper.primed",
               "contre": "minecraft:item.shield.block"}

for nom, (r, t, d, sol, eff, fx, apres) in K.items():
    sel = f"@a[distance=..{r},{PLB}" + (",predicate=metiers:au_sol" if sol else "") + "]"
    # impact (exécuté à la position du marker, macro sur storage metiers:boss dm)
    IMP = [f"execute as {sel} run {e}" for e in eff]
    IMP.append(f"$execute as {sel} run damage @s $({d}) {NS}:boss at ~ ~ ~")
    IMP += fx + ["function " + anneau(r, "minecraft:dust{color:[1.0,0.9,0.3],scale:2.0}")] + apres
    w(FB + f"impact_{nom}.mcfunction", "\n".join(IMP))
    if t == 0:
        continue
    # pose de l'annonce
    son = SONS_ALERTE.get(nom, "minecraft:block.note_block.basedrum")
    w(FB + f"poser_{nom}.mcfunction", "\n".join([
        f'summon minecraft:marker ~ ~ ~ {{Tags:["metiers.bz","metiers.bznew","metiers.k_{nom}"]}}',
        f"{SB} set @e[type=minecraft:marker,tag=metiers.bznew] m.bzt {t}",
        f"execute if score #tier m.boss matches 12.. run {SB} remove @e[type=minecraft:marker,tag=metiers.bznew,scores={{m.bzt=3..}}] m.bzt 1",
        "tag @e[type=minecraft:marker,tag=metiers.bznew] remove metiers.bznew",
        f"function {anneau(r)}",
        f"playsound {son} hostile @a ~ ~ ~ 1.2 0.7"]))

# chaque demi-seconde, pour chaque annonce : on redessine, et à zéro on frappe
MQ = [f"{SB} remove @s m.bzt 1"]
for nom, (r, t, *_x) in K.items():
    if t == 0:
        continue
    MQ.append(f"execute if entity @s[tag=metiers.k_{nom}] run function {anneau(r)}")
    MQ.append(f"execute if entity @s[tag=metiers.k_{nom}] if score @s m.bzt matches ..0 run function {B2}impact_{nom} {DM}")
MQ += ["execute if score @s m.bzt matches 1 run particle minecraft:dust{color:[1.0,0.1,0.1],scale:2.5} ~ ~0.2 ~ 0.8 0 0.8 0 25 force",
       "execute if score @s m.bzt matches ..0 run kill @s"]
w(FB + "marque.mcfunction", "\n".join(MQ))

# ---------------------------------------------------------------- semer des annonces au hasard autour du boss
# storage s {k:"nom", r:rayon} et #sn = nombre ; chaque point cherche un sol libre (de 3 blocs au-dessus à 12 en dessous)
w(FB + "semer.mcfunction", "\n".join([
    f"$execute store result storage {NS}:boss s.dx int 1 run random value -$(r)..$(r)",
    f"$execute store result storage {NS}:boss s.dz int 1 run random value -$(r)..$(r)",
    f"function {B2}semer_m with storage {NS}:boss s",
    f"{SB} remove #sn m.boss 1",
    f"execute if score #sn m.boss matches 1.. run function {B2}semer with storage {NS}:boss s"]))
w(FB + "semer_m.mcfunction", f"$execute positioned ~$(dx) ~ ~$(dz) align xyz positioned ~0.5 ~ ~0.5 run function {B2}sol {{k:\"$(k)\"}}")
w(FB + "sol.mcfunction", "\n".join([f"{SB} set #ok m.boss 0"] + [
    f"$execute if score #ok m.boss matches 0 positioned ~ ~{dy} ~ if block ~ ~ ~ #{NS}:boss_vide unless block ~ ~-1 ~ #{NS}:boss_vide "
    f"unless block ~ ~-1 ~ minecraft:water unless block ~ ~-1 ~ minecraft:lava run function {B2}sol_ok {{k:\"$(k)\"}}" for dy in range(3, -13, -1)]))
w(FB + "sol_ok.mcfunction", f"{SB} set #ok m.boss 1\n$function {B2}poser_$(k)")
def semer(k, r, base, par_rang):
    """Commandes qui sèment base + rang/par_rang annonces k dans un rayon r autour de la position courante."""
    L = [f'data modify storage {NS}:boss s set value {{k:"{k}",r:{r}}}', f"{SB} set #sn m.boss {base}"]
    if par_rang:
        L += [f"{SB} operation #tmp m.boss = #tier m.boss", f"{SB} set #div m.boss {par_rang}",
              f"{SB} operation #tmp m.boss /= #div m.boss", f"{SB} operation #sn m.boss += #tmp m.boss"]
    return L + [f"function {B2}semer with storage {NS}:boss s"]

# ---------------------------------------------------------------- zones qui restent au sol (forge, couronne, toile)
Z = {
    "forge":    (2, 20, "minecraft:flame", ["minecraft:lava ~ ~0.2 ~ 0.8 0 0.8 0 2 force"], "s", []),
    "couronne": (2.5, 20, "minecraft:flame", ["minecraft:flame ~ ~0.8 ~ 1 0.6 1 0.02 12 force"], "s", []),
    "toile":    (3, 16, "minecraft:block{block_state:\"minecraft:cobweb\"}", ["minecraft:item_cobweb ~ ~0.5 ~ 1.5 0.3 1.5 0 6 force"], None,
                 ["effect give @s minecraft:slowness 2 4", "effect give @s minecraft:mining_fatigue 2 1"]),
}
for nom, (r, vie, bord, fx, d, eff) in Z.items():
    w(FB + f"poser_{nom}.mcfunction", "\n".join([
        f'summon minecraft:marker ~ ~ ~ {{Tags:["metiers.bzz","metiers.bznew","metiers.z_{nom}"]}}',
        f"{SB} set @e[type=minecraft:marker,tag=metiers.bznew] m.bzt {vie}",
        "tag @e[type=minecraft:marker,tag=metiers.bznew] remove metiers.bznew",
        "playsound minecraft:block.fire.ambient hostile @a ~ ~ ~ 1 0.6"]))
    ZL = [f"function {anneau(r, bord + '')}"] + [f"particle {p}" for p in fx]
    # 1 s de délai avant d'être active, puis une touche par seconde
    ZL += [f"execute if score @s m.bzt matches ..{vie - 2} if score #pair m.timer matches 0 as @a[distance=..{r},{PLB}] run {e}" for e in eff]
    if d:
        ZL.append(f"$execute if score @s m.bzt matches ..{vie - 2} if score #pair m.timer matches 0 as @a[distance=..{r},{PLB}] run damage @s $({d}) {NS}:boss at ~ ~ ~")
    w(FB + f"zone_{nom}.mcfunction", "\n".join(ZL))
ZT = [f"{SB} remove @s m.bzt 1"] + [f"execute if entity @s[tag=metiers.z_{n}] run function {B2}zone_{n}" + (f" {DM}" if Z[n][4] else "") for n in Z] + \
     ["execute if score @s m.bzt matches ..0 run kill @s"]
w(FB + "zone.mcfunction", "\n".join(ZT))

# ---------------------------------------------------------------- mines du Creeper (block_display de TNT, pas un bloc)
w(FB + "poser_mine.mcfunction", "\n".join([
    'summon minecraft:block_display ~ ~ ~ {Tags:["metiers.bmine","metiers.bznew"],block_state:{Name:"minecraft:tnt"},Glowing:1b,glow_color_override:16711680,'
    'brightness:{sky:15,block:15},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-0.3f,0f,-0.3f],scale:[0.6f,0.6f,0.6f]}}',
    f"{SB} set @e[type=minecraft:block_display,tag=metiers.bznew] m.bzt 60",
    "tag @e[type=minecraft:block_display,tag=metiers.bznew] remove metiers.bznew",
    "playsound minecraft:entity.tnt.primed hostile @a ~ ~ ~ 1 1.4"]))
w(FB + "mine.mcfunction", "\n".join([
    f"{SB} remove @s m.bzt 1",
    "execute if score @s m.bzt matches ..56 run particle minecraft:dust{color:[0.3,1.0,0.3],scale:1.0} ~ ~0.8 ~ 0.2 0.1 0.2 0 3 force",
    "execute if score @s m.bzt matches ..56 if score #pair m.timer matches 0 run playsound minecraft:block.note_block.hat hostile @a[distance=..8] ~ ~ ~ 0.6 2",
    f"execute if score @s m.bzt matches ..56 if entity @a[distance=..1.8,{PLB}] run return run function {B2}mine_boum",
    f"execute if score @s m.bzt matches ..0 run function {B2}mine_boum"]))
w(FB + "mine_boum.mcfunction", f"function {B2}impact_petard {DM}\nkill @s")

# ---------------------------------------------------------------- rejetons kamikazes (creepers qui n'explosent jamais pour de vrai)
w(FB + "rejeton.mcfunction",
  'summon minecraft:creeper ~ ~ ~ {Tags:["metiers.sbire","metiers.rejeton"],CustomName:{text:"Rejeton",color:"green"},Fuse:32767s,ExplosionRadius:0b,'
  'DeathLootTable:"minecraft:empty",PersistenceRequired:1b,attributes:[{id:"minecraft:scale",base:0.6d},{id:"minecraft:movement_speed",base:0.33d},'
  '{id:"minecraft:max_health",base:8d},{id:"minecraft:follow_range",base:40d}],Health:8f}')
w(FB + "rejeton_boum.mcfunction", f"function {B2}impact_petard {DM}\ntp @s ~ -400 ~\nkill @s")
w(FB + "boucle.mcfunction", "\n".join([
    f"{SB} remove #sn m.boss 1",
    f"$function {B2}$(f)",
    f"$execute if score #sn m.boss matches 1.. run function {B2}boucle {{f:\"$(f)\"}}"]))
def repeter(f, base, par_rang):
    L = [f"{SB} set #sn m.boss {base}"]
    if par_rang:
        L += [f"{SB} operation #tmp m.boss = #tier m.boss", f"{SB} set #div m.boss {par_rang}",
              f"{SB} operation #tmp m.boss /= #div m.boss", f"{SB} operation #sn m.boss += #tmp m.boss"]
    return L + [f'function {B2}boucle {{f:"{f}"}}']

# ---------------------------------------------------------------- les attaques, par boss
ANN2 = lambda txt, col: f'title @a[distance=..48] actionbar {{"text":"{txt}","color":"{col}","bold":true}}'
P = lambda nom: f"function {B2}poser_{nom}"
ATQ = {
    1: {  # Colosse : corps à corps lourd
        "martelement": [f"execute as @a[distance=..16,{PLB}] at @s run {P('marteau')}", ANN2("Le Colosse lève son marteau : sortez des cercles !", "dark_red")],
        "onde": ["effect give @s minecraft:slowness 2 9 true", P("onde"), ANN2("Onde de choc : sautez !", "dark_red")],
        "saut": [f"execute as @a[distance=4..30,{PLB},sort=random,limit=1] at @s run {P('saut')}", ANN2("Le Colosse va bondir !", "dark_red")],
        "forge": semer("forge", 8, 2, 5) + [f"execute as @a[distance=..16,{PLB}] at @s run {P('forge')}", ANN2("La forge déborde : le sol brûle.", "gold")],
    },
    2: {  # Reine arachnide : contrôle et poison
        "crachat": [f"execute as @a[distance=..20,{PLB},sort=random,limit=2] at @s run {P('crachat')}", ANN2("La Reine crache son venin !", "dark_green")],
        "toile": semer("toile", 8, 2, 6) + [f"execute as @a[distance=..16,{PLB},sort=nearest,limit=1] at @s run {P('toile')}", ANN2("Des toiles couvrent le sol.", "dark_green")],
        "nid": [f"execute as @a[distance=..16,{PLB},sort=random,limit=1] at @s run function {B2}nid", ANN2("La Reine libère son nid !", "dark_green")],
        "bond": [f"execute as @a[distance=..30,{PLB},sort=furthest,limit=1] at @s run {P('bondreine')}", ANN2("La Reine va bondir sur le plus éloigné !", "dark_green")],
    },
    3: {  # Liche : distance, gel
        "pics": [f"execute as @a[distance=..24,{PLB}] at @s run {P('pic')}", ANN2("Des pics de glace jaillissent !", "aqua")],
        "blizzard": semer("blizzard", 9, 4, 4) + [ANN2("Blizzard !", "aqua")],
        "drain": [f"execute as @a[distance=..14,{PLB}] at @s run particle minecraft:soul ~ ~1 ~ 0.4 0.6 0.4 0.02 15 force",
                  f"effect give @a[distance=..14,{PLB}] minecraft:wither 4 1",
                  f"execute if entity @a[distance=..14,{PLB}] run effect give @s minecraft:instant_damage 1 1 true",
                  "playsound minecraft:entity.stray.ambient hostile @a ~ ~ ~ 2 0.5", ANN2("La Liche draine votre vie : éloignez-vous !", "aqua")],
        "clignement": [f"execute as @a[distance=..30,{PLB},sort=random,limit=1] at @s rotated ~ 0 positioned ^ ^ ^-3 align xyz positioned ~0.5 ~ ~0.5 "
                       f"if function {NS}:boss/place_ok run tp @e[tag=metiers.boss,limit=1] ~ ~ ~",
                       "particle minecraft:reverse_portal ~ ~1 ~ 1 1 1 0.2 60 force", "playsound minecraft:entity.enderman.teleport hostile @a ~ ~ ~ 2 0.5",
                       f"execute at @e[tag=metiers.boss,limit=1] run {P('nova')}", ANN2("La Liche apparaît dans votre dos !", "aqua")],
    },
    4: {  # Brasier : pluie de zones
        "pluie": semer("braise", 10, 5, 3) + [f"execute as @a[distance=..24,{PLB}] at @s run {P('braise')}", ANN2("Une pluie de braises s'abat !", "gold")],
        "nova": [P("nova_feu"), ANN2("Le Brasier va exploser : éloignez-vous !", "gold")],
        "meteores": [f"execute as @a[distance=..24,{PLB}] at @s run {P('meteore')}", ANN2("Des météores tombent sur vous !", "gold")],
        "couronne": semer("couronne", 9, 3, 5) + [ANN2("Couronne de flammes.", "gold")],
    },
    5: {  # Creeper géant : explosions annoncées, mines, kamikazes
        "detonation": [f"execute as @a[distance=..20,{PLB}] at @s run {P('detonation')}",
                       "execute if score #tier m.boss matches 10.. run " + f"function {B2}detonation_bonus",
                       ANN2("Le Creeper gonfle : sortez des cercles !", "green")],
        "fusion": ["effect give @s minecraft:slowness 2 9 true", P("fusion"), "particle minecraft:happy_villager ~ ~2 ~ 2 2 2 0 60 force",
                   ANN2("MÉGAFUSION : fuyez loin du Creeper !", "green")],
        "mines": semer("mine", 10, 3, 4) + [ANN2("Le Creeper sème des mines : ne marchez pas dessus.", "green")],
        "rejetons": repeter("rejeton", 2, 6) + ["playsound minecraft:entity.creeper.primed hostile @a ~ ~ ~ 2 0.7",
                                                 ANN2("Rejetons kamikazes : abattez-les à distance !", "green")],
        "bond": [f"execute as @a[distance=4..30,{PLB},sort=random,limit=1] at @s run {P('bondcreeper')}", ANN2("Le Creeper va bondir !", "green")],
    },
}
w(FB + "nid.mcfunction", "\n".join(repeter("araignee", 2, 5) + ["playsound minecraft:entity.spider.ambient hostile @a ~ ~ ~ 2 0.4"]))
w(FB + "araignee.mcfunction", 'summon minecraft:cave_spider ~ ~ ~ {Tags:["metiers.sbire"],DeathLootTable:"minecraft:empty",CustomName:{text:"Couvée de la Reine",color:"green"}}')
w(FB + "detonation_bonus.mcfunction", "\n".join(semer("detonation", 8, 2, 0)))
for k, atqs in ATQ.items():
    for nom, L in atqs.items():
        w(FB + f"a{k}_{nom}.mcfunction", "\n".join(L))

# ---------------------------------------------------------------- choix de l'attaque (remplace boss/attaque)
AT3 = ["tag @s add metiers.atk",  # signal pour le modèle animé du pack Boss
       # cadence : on repart de rang/5 (3 au plus), le compteur doit atteindre 10 (+1 par demi-seconde, +2 enragé, +3 en phase finale)
       f"{SB} operation #atk m.boss = #tier m.boss", f"{SB} operation #atk m.boss /= #5 m.const",
       f"execute if score #atk m.boss matches 4.. run {SB} set #atk m.boss 3"]
for k, atqs in ATQ.items():
    noms = list(atqs)
    AT3.append(f"execute if score #type m.boss matches {k} store result score #r m.boss run random value 1..{len(noms)}")
    # pas deux fois la même attaque de suite
    AT3.append(f"execute if score #type m.boss matches {k} if score #r m.boss = #ratk m.boss run {SB} add #r m.boss 1")
    AT3.append(f"execute if score #type m.boss matches {k} if score #r m.boss matches {len(noms) + 1}.. run {SB} set #r m.boss 1")
    AT3 += [f"execute if score #type m.boss matches {k} if score #r m.boss matches {i} run function {B2}a{k}_{n}" for i, n in enumerate(noms, 1)]
AT3.append(f"{SB} operation #ratk m.boss = #r m.boss")
w(F + "boss/attaque.mcfunction", "\n".join(AT3))

# ---------------------------------------------------------------- ripostes (trop de coups reçus en 3 s)
RIP = {
    1: ["effect give @s minecraft:resistance 2 4 true", P("contre"), ANN2("Le Colosse pare et contre-attaque !", "dark_red")],
    2: [f"execute as @a[distance=..4.5,{PLB}] run effect give @s minecraft:slowness 2 9", f"execute as @a[distance=..4.5,{PLB}] run effect give @s minecraft:poison 4 1",
        f"$execute as @a[distance=..4.5,{PLB}] run damage @s $(s) {NS}:boss at ~ ~ ~", "particle minecraft:item_slime ~ ~1 ~ 2 0.5 2 0 40 force",
        "playsound minecraft:entity.spider.hurt hostile @a ~ ~ ~ 2 0.4", ANN2("La Reine vous mord et vous enlace !", "dark_green")],
    3: [P("givre"), f"execute as @a[distance=..16,{PLB},sort=nearest,limit=1] at @s facing entity @e[tag=metiers.boss,limit=1] feet rotated ~ 0 "
        f"positioned as @e[tag=metiers.boss,limit=1] positioned ^ ^ ^7 align xyz positioned ~0.5 ~ ~0.5 if function {NS}:boss/place_ok run tp @e[tag=metiers.boss,limit=1] ~ ~ ~",
        "particle minecraft:reverse_portal ~ ~1 ~ 1 1 1 0.2 60 force", "playsound minecraft:entity.enderman.teleport hostile @a ~ ~ ~ 2 0.6",
        ANN2("La Liche se dérobe et laisse un piège de givre !", "aqua")],
    4: [f"$execute as @a[distance=..5,{PLB}] run damage @s $(s) {NS}:boss at ~ ~ ~", f"effect give @a[distance=..5,{PLB}] minecraft:levitation 1 2 true",
        "particle minecraft:flame ~ ~1 ~ 2.5 1 2.5 0.15 150 force", "playsound minecraft:item.firecharge.use hostile @a ~ ~ ~ 2 0.6",
        ANN2("Combustion : le Brasier repousse ses assaillants !", "gold")],
    5: [P("gaz"), ANN2("Le Creeper siffle : fuite de gaz !", "green")],
}
for k, L in RIP.items():
    w(FB + f"riposte_{k}.mcfunction", "\n".join(L))
w(FB + "riposte.mcfunction", "\n".join(
    [f"{SB} set #coups m.boss 0", f"{SB} set #rcd m.boss 8"] +
    [f"execute if score #type m.boss matches {k} run function {B2}riposte_{k}" + (f" {DM}" if any(x.startswith("$") for x in RIP[k]) else "") for k in RIP]))
w(FB + "fenetre.mcfunction", "\n".join([
    f"{SB} set #fen m.boss 0", f"{SB} set #coups m.boss 0",
    f"execute store result score #rseuil m.boss at @e[tag=metiers.boss,limit=1] if entity @a[distance=..24,{PLB}]",
    f"{SB} operation #rseuil m.boss *= #2 m.const", f"{SB} add #rseuil m.boss 3"]))

# aura de gaz du Creeper : rester collé coûte cher (une touche par seconde)
w(FB + "aura_creeper.mcfunction", "\n".join([
    "particle minecraft:happy_villager ~ ~1 ~ 1.8 1 1.8 0 12 force",
    f"execute if entity @a[distance=..3.5,{PLB}] run particle minecraft:dust{{color:[0.4,1.0,0.2],scale:1.6}} ~ ~0.5 ~ 2 0.4 2 0 30 force",
    f"$execute as @a[distance=..3.5,{PLB}] run damage @s $(a) {NS}:boss at ~ ~ ~",
    f"execute as @a[distance=..3.5,{PLB}] run effect give @s minecraft:poison 2 0"]))

# carapace du Creeper à 33 % : invulnérable 6 s, il sème des mines et des détonations
w(FB + "carapace.mcfunction", "\n".join([
    "effect give @s minecraft:resistance 6 4 true", "effect give @s minecraft:slowness 6 9 true",
    "particle minecraft:totem_of_undying ~ ~2 ~ 2 2 2 0.2 80 force"] + semer("mine", 10, 6, 3) + semer("detonation", 9, 3, 0) +
    [f"execute as @a[distance=..20,{PLB}] at @s run {P('detonation')}",
     'tellraw @a ' + PREFIX + ',{"text":"Le Creeper se blinde de TNT (invulnérable 6 s) : survivez aux mines !","color":"green","bold":true}]']))
add_lines(F + "boss/vague.mcfunction", [f"execute if score #phase m.boss matches 2 if score #type m.boss matches 5 run function {B2}carapace"])

# ---------------------------------------------------------------- boucle (toutes les 0,5 s pendant un combat)
w(FB + "tick.mcfunction", "\n".join([
    f"execute as @e[type=minecraft:marker,tag=metiers.bz] at @s run function {B2}marque",
    f"execute as @e[type=minecraft:marker,tag=metiers.bzz] at @s run function {B2}zone",
    f"execute as @e[type=minecraft:block_display,tag=metiers.bmine] at @s run function {B2}mine",
    f"execute as @e[type=minecraft:creeper,tag=metiers.rejeton] at @s if entity @a[distance=..2,{PLB}] run function {B2}rejeton_boum",
    f"{SB} add #fen m.boss 1",
    f"execute if score #rcd m.boss matches 1.. run {SB} remove #rcd m.boss 1",
    f"execute if score #rcd m.boss matches ..0 if score #coups m.boss >= #rseuil m.boss as @e[tag=metiers.boss,limit=1] at @s run function {B2}riposte",
    f"execute if score #fen m.boss matches 6.. run function {B2}fenetre",
    f"execute if score #type m.boss matches 5 if score #pair m.timer matches 0 as @e[tag=metiers.boss,limit=1] at @s run function {B2}aura_creeper {DM}"]))
add_lines(F + "boss/encours.mcfunction", [f"function {B2}tick"])
add_lines(F + "boss/touche.mcfunction", [f"{SB} add #coups m.boss 1"])
add_lines(F + "boss/fin.mcfunction", ["kill @e[type=minecraft:marker,tag=metiers.bz]", "kill @e[type=minecraft:marker,tag=metiers.bzz]",
                                      "kill @e[type=minecraft:block_display,tag=metiers.bmine]", f"{SB} set #coups m.boss 0"])

# ---------------------------------------------------------------- rang, PV, statistiques (remplace boss/apparaitre)
SJ = [f"{SB} set #acc m.boss 0"]
for j in JL:
    SJ += [f"{SB} operation #pj m.boss = @s m.{j}_pr", f"{SB} operation #pj m.boss *= #100 m.const",
           f"{SB} operation #pj m.boss += @s m.{j}_lvl", f"{SB} operation #acc m.boss += #pj m.boss"]
SJ.append(f"{SB} operation #tier m.boss > #acc m.boss")
w(FB + "score_joueur.mcfunction", "\n".join(SJ))

CAL = [  # dégâts des attaques selon le rang (PV d'un joueur : 20)
    f"{SB} operation #v m.boss = #tier m.boss", f"{SB} operation #v m.boss /= #4 m.const", f"{SB} add #v m.boss 3",
    f"execute store result storage {NS}:boss dm.s int 1 run {SB} get #v m.boss",          # petites : 3 à 8
    f"{SB} operation #v m.boss = #tier m.boss", f"{SB} operation #v m.boss *= #2 m.const", f"{SB} operation #v m.boss /= #5 m.const",
    f"{SB} add #v m.boss 6", f"execute store result storage {NS}:boss dm.m int 1 run {SB} get #v m.boss",   # moyennes : 6 à 14
    f"{SB} operation #v m.boss = #tier m.boss", f"{SB} operation #v m.boss *= #3 m.const", f"{SB} operation #v m.boss /= #5 m.const",
    f"{SB} add #v m.boss 10", f"execute store result storage {NS}:boss dm.l int 1 run {SB} get #v m.boss",  # lourdes : 10 à 22
    f"{SB} operation #v m.boss = #tier m.boss", f"{SB} operation #v m.boss /= #5 m.const", f"{SB} add #v m.boss 2",
    f"execute store result storage {NS}:boss dm.a int 1 run {SB} get #v m.boss",          # aura du Creeper : 2 à 6
    f"{SB} set #coups m.boss 0", f"{SB} set #fen m.boss 0", f"{SB} set #rcd m.boss 0", f"{SB} set #rseuil m.boss 5", f"{SB} set #ratk m.boss 0"]
w(FB + "calibrer.mcfunction", "\n".join(CAL))

# armure = moitié de l'armure de base + rang (30 au plus), robustesse = rang / 2, attaque au contact = base + rang / 2
ST = [f"{SB} operation #v m.boss = #tier m.boss", f"{SB} operation #v m.boss /= #2 m.const"]
for k, b in BOSS.items():
    ST += [f"execute if score #type m.boss matches {k} run {SB} set #ar m.boss {b['arm'] // 2}",
           f"execute if score #type m.boss matches {k} run {SB} set #ad m.boss {b['atk']}"]
ST += [f"{SB} operation #ar m.boss += #tier m.boss", f"execute if score #ar m.boss matches 31.. run {SB} set #ar m.boss 30",
       f"execute unless score #type m.boss matches 5 run {SB} operation #ad m.boss += #v m.boss",
       f"execute store result storage {NS}:boss st.ar int 1 run {SB} get #ar m.boss",
       f"execute store result storage {NS}:boss st.ad int 1 run {SB} get #ad m.boss",
       f"execute store result storage {NS}:boss st.to int 1 run {SB} get #v m.boss",
       f"function {B2}stats_m with storage {NS}:boss st"]
w(FB + "stats.mcfunction", "\n".join(ST))
w(FB + "stats_m.mcfunction", "\n".join(["$attribute @s minecraft:armor base set $(ar)", "$attribute @s minecraft:armor_toughness base set $(to)",
                                         "$attribute @s minecraft:attack_damage base set $(ad)"]))

NOMBAR = []
for k, b in BOSS.items():
    NOMBAR.append(f'execute if score #type m.boss matches {k} run bossbar set metiers:boss name [{{"text":"{b["nom"]}","color":"{b["col"]}","bold":true}},'
                  f'{{"text":"  Rang ","color":"gray","bold":false}},{{"score":{{"name":"#tier","objective":"m.boss"}},"color":"yellow","bold":false}}]')
w(FB + "nom_barre.mcfunction", "\n".join(NOMBAR))

AP2 = [
    # rang : meilleur score de métiers à 64 blocs du joueur près de qui le boss apparaît, par paliers de 50 (20 au plus)
    f"{SB} set #tier m.boss 0",
    f"execute as @a[distance=..64,gamemode=!spectator] run function {B2}score_joueur",
    f"{SB} operation #tier m.boss /= #50 m.const",
    f"execute if score #tier m.boss matches 21.. run {SB} set #tier m.boss 20",
    # PV : 350 + 35 par rang + 220 par joueur en plus ; plafond du jeu à 1 024, la Résistance prend le relais
    "execute store result score #n m.boss if entity @a[gamemode=!spectator]",
    f"{SB} operation #max m.boss = #n m.boss", f"{SB} remove #max m.boss 1", f"{SB} operation #max m.boss *= #220 m.const",
    f"{SB} operation #v m.boss = #tier m.boss", f"{SB} operation #v m.boss *= #35 m.const",
    f"{SB} operation #max m.boss += #v m.boss", f"{SB} add #max m.boss 350",
    f"{SB} set #res m.boss 0",
    f"execute if score #max m.boss matches 1300.. run {SB} set #res m.boss 1",
    f"execute if score #max m.boss matches 1800.. run {SB} set #res m.boss 2",
    f"execute if score #max m.boss matches 1001.. run {SB} set #max m.boss 1000",
    f"execute store result storage {NS}:boss hp int 1 run {SB} get #max m.boss",
    f"function {NS}:boss/lieu"]
AP2 += [f"execute if score #type m.boss matches {k} at @e[type=minecraft:marker,tag=metiers.blieu,limit=1] run function {NS}:boss/apparaitre_{k} with storage {NS}:boss" for k in BOSS]
AP2 += ["kill @e[type=minecraft:marker,tag=metiers.blieu]",
        f"execute if score #res m.boss matches 1 run effect give {B} minecraft:resistance infinite 0 true",
        f"execute if score #res m.boss matches 2 run effect give {B} minecraft:resistance infinite 1 true",
        f"execute as {B} run function {B2}stats", f"function {B2}calibrer", f"function {B2}nom_barre",
        f"{SB} set #actif m.boss 1", f"{SB} set #temps m.boss 0", f"{SB} set #phase m.boss 0", f"{SB} set #atk m.boss 0",
        f"{SB} set #tue m.boss 0", f"{SB} set #mk m.boss 0", f"{SB} set #fin m.boss 0",
        f"{SB} operation #last m.boss = #max m.boss", "scoreboard players set @a m.dmg 0", "scoreboard players set @a m.bdmg 0",
        "execute store result bossbar metiers:boss max run scoreboard players get #max m.boss",
        "execute store result bossbar metiers:boss value run scoreboard players get #max m.boss",
        "bossbar set metiers:boss style notched_10", "bossbar set metiers:boss visible true", "bossbar set metiers:boss players @a",
        f"execute store result score #x m.boss run data get entity {B} Pos[0]",
        f"execute store result score #y m.boss run data get entity {B} Pos[1]",
        f"execute store result score #z m.boss run data get entity {B} Pos[2]",
        f'tellraw @a {PREFIX},{{"text":"Le boss est apparu près de ","color":"red","bold":true}},{{"selector":"@s"}},{{"text":" en ","color":"white"}},'
        f'{{"score":{{"name":"#x","objective":"m.boss"}},"color":"yellow"}},{{"text":" ","color":"white"}},{{"score":{{"name":"#y","objective":"m.boss"}},"color":"yellow"}},'
        f'{{"text":" ","color":"white"}},{{"score":{{"name":"#z","objective":"m.boss"}},"color":"yellow"}},{{"text":". Rang ","color":"white"}},'
        f'{{"score":{{"name":"#tier","objective":"m.boss"}},"color":"gold"}},{{"text":", PV ","color":"white"}},{{"score":{{"name":"#max","objective":"m.boss"}},"color":"red"}},'
        f'{{"text":". Ses attaques ignorent l\'armure : esquivez les cercles rouges.","color":"white"}}]',
        "execute as @a at @s run playsound minecraft:entity.ravager.roar master @s ~ ~ ~ 1 0.6"]
w(F + "boss/apparaitre.mcfunction", "\n".join(AP2))
# combat repris après un /reload ou un redémarrage : le rang est gardé dans #tier
add_lines(F + "boss/adopter.mcfunction", [f"function {B2}calibrer", f"function {B2}nom_barre"])

# ---------------------------------------------------------------- récompenses proportionnelles au rang
add_lines(F + "boss/recompense.mcfunction", [
    f"{SB} operation #eb m.boss = #tier m.boss", f"{SB} operation #eb m.boss /= #4 m.const",
    f"{SB} operation @s m.ecl += #eb m.boss",
    f"{SB} operation #ub m.boss = #tier m.boss", f"{SB} operation #ub m.boss *= #1500 m.const",
    f"execute if score @s c.ecus matches -2147483648.. run {SB} operation @s c.ecus += #ub m.boss",
    f'execute if score #tier m.boss matches 1.. run tellraw @s {PREFIX},{{"text":"Bonus de rang ","color":"gold"}},{{"score":{{"name":"#tier","objective":"m.boss"}},"color":"yellow"}},'
    f'{{"text":" : +","color":"gold"}},{{"score":{{"name":"#eb","objective":"m.boss"}},"color":"yellow"}},{{"text":" éclats et +","color":"gold"}},'
    f'{{"score":{{"name":"#ub","objective":"m.boss"}},"color":"yellow"}},{{"text":" Écus.","color":"gold"}}]'])

add_lines(F + "refonte/load.mcfunction", ["scoreboard objectives add m.bzt dummy",
                                          f"{SB} add #tier m.boss 0", f"{SB} add #coups m.boss 0", f"{SB} add #rcd m.boss 0",
                                          f"{SB} add #fen m.boss 0", f"{SB} add #rseuil m.boss 0", f"{SB} add #ratk m.boss 0",
                                          f"execute unless score #rseuil m.boss matches 1.. run {SB} set #rseuil m.boss 5",
                                          f"execute unless data storage {NS}:boss dm run function {B2}calibrer"] +
          [f"{SB} set #{c} m.const {c}" for c in (2, 3, 4, 5, 35, 50, 100, 220, 1500)])

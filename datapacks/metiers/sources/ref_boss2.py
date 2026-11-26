# -*- coding: utf-8 -*-
# 26/11/2026 : boss de Métiers durcis (Samuel : « vraiment trop simples à battre »).
# Exécuté après ref_v26.py, dont il remplace l'adaptation au niveau de Chasseur moyen.
#
# Rang : le boss se cale sur le score de métiers (m.total : somme des niveaux, +100 par étoile) du joueur près de qui
# il apparaît, par paliers de 50 points (rang 0 à 24). Par rang : +15 % de PV (plus Résistance au-delà de 1 024),
# +8 % de dégâts (coups et attaques scriptées), +1 d'armure (30 au plus), attaques plus rapprochées, et récompenses
# +15 % (Écus, XP de Chasseur, éclats). Deux attaques de plus par boss (une dès 0 point, une dès 200 points) et des
# ensorcellements gagnés avec le rang (régénération, ronces, bouclier, aura, furie).
import math
import re as _re

RANG_PALIER, RANG_MAX = 50, 24
PL2 = "gamemode=!spectator,gamemode=!creative"
BF = F + "boss/"


def _lire(nom):
    with open(os.path.join(ROOT, BF + nom + ".mcfunction"), encoding="utf-8") as f_:
        return f_.read()


def _ecrire(nom, txt):
    w(BF + nom + ".mcfunction", txt)


def _rempl(nom, a, b):
    t = _lire(nom)
    assert a in t, (nom, a)
    _ecrire(nom, t.replace(a, b))


def coup(base, typ):
    """Dégât scripté mis à l'échelle du rang (#pw m.boss = 100 + 8 par rang), en tant que joueur touché."""
    return f'function {NS}:boss/coup {{b:{base},t:"minecraft:{typ}"}}'


w(BF + "coup.mcfunction", "\n".join([
    "$scoreboard players set #d m.boss $(b)",
    "scoreboard players operation #d m.boss *= #pw m.boss", "scoreboard players operation #d m.boss /= #100 m.const",
    f"execute store result storage {NS}:boss d.n int 1 run scoreboard players get #d m.boss",
    f'$data modify storage {NS}:boss d.t set value "$(t)"',
    f"function {NS}:boss/coup2 with storage {NS}:boss d"]))
w(BF + "coup2.mcfunction", "\n".join([
    "$execute if entity @e[tag=metiers.boss,limit=1] run return run damage @s $(n) $(t) by @e[tag=metiers.boss,limit=1]",
    "$damage @s $(n) $(t)"]))

# ---------------------------------------------------------------- apparition : rang, PV, dégâts, armure, ensorcellements
RG = ["# rang : score de métiers du joueur près de qui le boss apparaît (@s), par paliers de 50 points",
      "scoreboard players set #rg m.boss 0",
      "execute if score @s m.total matches 1.. run scoreboard players operation #rg m.boss = @s m.total",
      "scoreboard players operation #rg m.boss /= #50 m.const",
      f"execute if score #rg m.boss matches {RANG_MAX + 1}.. run scoreboard players set #rg m.boss {RANG_MAX}",
      "scoreboard players operation #pw m.boss = #rg m.boss", "scoreboard players operation #pw m.boss *= #8 m.const",
      "scoreboard players add #pw m.boss 100",
      "scoreboard players operation #mul m.boss = #rg m.boss", "scoreboard players operation #mul m.boss *= #15 m.const",
      "scoreboard players add #mul m.boss 100",
      # une attaque toutes les 5 s au rang 0, toutes les 2,5 s au rang 20 et plus
      "scoreboard players set #atkcd m.boss 10", "scoreboard players operation #e2 m.boss = #rg m.boss",
      "scoreboard players operation #e2 m.boss /= #4 m.const", "scoreboard players operation #atkcd m.boss -= #e2 m.boss",
      "execute if score #atkcd m.boss matches ..4 run scoreboard players set #atkcd m.boss 5",
      "scoreboard players set #rgj m.boss 0",
      "execute if score @s m.total matches 1.. run scoreboard players operation #rgj m.boss = @s m.total"]
REN = []
for k, b in BOSS.items():
    REN += [f"execute if score #type m.boss matches {k} run scoreboard players set #ad m.boss {b['atk']}",
            f"execute if score #type m.boss matches {k} run scoreboard players set #ar m.boss {b['arm']}"]
REN += ["scoreboard players operation #ad m.boss *= #pw m.boss", "scoreboard players operation #ad m.boss /= #100 m.const",
        "scoreboard players operation #ar m.boss += #rg m.boss",
        "execute if score #ar m.boss matches 31.. run scoreboard players set #ar m.boss 30",
        f"execute store result storage {NS}:boss ad int 1 run scoreboard players get #ad m.boss",
        f"execute store result storage {NS}:boss ar int 1 run scoreboard players get #ar m.boss",
        f"execute as @e[tag=metiers.boss,limit=1] run function {NS}:boss/renforcer with storage {NS}:boss",
        # ensorcellements
        "execute if score #rg m.boss matches 3.. run effect give @e[tag=metiers.boss,limit=1] minecraft:regeneration infinite 0 true",
        f'tellraw @a {PREFIX},{{"text":"Le boss se cale sur ","color":"gray"}},{{"selector":"@s"}},'
        f'{{"text":" (","color":"gray"}},{{"score":{{"name":"#rgj","objective":"m.boss"}},"color":"yellow"}},{{"text":" points de métiers) : rang ","color":"gray"}},'
        f'{{"score":{{"name":"#rg","objective":"m.boss"}},"color":"red","bold":true}},{{"text":". Récompenses +","color":"gray"}},'
        f'{{"score":{{"name":"#bonus","objective":"m.boss"}},"color":"gold"}},{{"text":" %.","color":"gray"}}]']
# texte des ensorcellements selon le rang (un tellraw par cas, plus simple qu'une liste dynamique)
ENS_TXT = [(3, "régénération"), (6, "ronces (renvoie des coups)"), (10, "bouclier à chaque vague"),
           (14, "aura qui ronge"), (18, "furie (dernier souffle dès 30 %)")]
for i, (r, _x) in enumerate(ENS_TXT):
    hi = ENS_TXT[i + 1][0] - 1 if i + 1 < len(ENS_TXT) else None
    liste = ", ".join(x for rr, x in ENS_TXT if rr <= r)
    REN.append(f'execute if score #rg m.boss matches {r}..{hi if hi else ""} run tellraw @a {PREFIX},{{"text":"Ensorcellements : ","color":"dark_purple"}},{{"text":"{liste}.","color":"light_purple"}}]')
# l'ancienne adaptation au niveau moyen de Chasseur (ref_v26) est remplacée par le rang
t_app = _lire("apparaitre")
i0 = t_app.index("scoreboard players set #ns m.boss 0")
i1 = t_app.index("execute as @e[tag=metiers.boss,limit=1] run function metiers:boss/renforcer with storage metiers:boss")
i1 = t_app.index("\n", i1) + 1
corps = t_app[:i0] + "\n".join(REN) + "\n" + t_app[i1:]
for a, b_ in (("scoreboard players add #max m.boss 350\n",
               "scoreboard players add #max m.boss 350\n"
               "scoreboard players operation #max m.boss *= #mul m.boss\nscoreboard players operation #max m.boss /= #100 m.const\n"),
              ("execute if score #max m.boss matches 1001.. run scoreboard players set #max m.boss 1000\n",
               "execute if score #max m.boss matches 2400.. run scoreboard players set #res m.boss 3\n"
               "execute if score #max m.boss matches 1001.. run scoreboard players set #max m.boss 1000\n"),
              ("execute if score #res m.boss matches 2 run effect give @e[tag=metiers.boss,limit=1] minecraft:resistance infinite 1 true\n",
               "execute if score #res m.boss matches 2 run effect give @e[tag=metiers.boss,limit=1] minecraft:resistance infinite 1 true\n"
               "execute if score #res m.boss matches 3 run effect give @e[tag=metiers.boss,limit=1] minecraft:resistance infinite 2 true\n"),
              ('{"text":". Chaque participant gagne un éclat de boss.","color":"white"}]', '{"text":".","color":"white"}]')):
    assert a in corps, a
    corps = corps.replace(a, b_)
_ecrire("apparaitre", "\n".join(RG + ["scoreboard players operation #bonus m.boss = #mul m.boss",
                                      "scoreboard players remove #bonus m.boss 100"]) + "\n" + corps)

# ---------------------------------------------------------------- combat : cadence, zones, aura, furie
_rempl("encours", "execute if score #atk m.boss matches 10.. as @e[tag=metiers.boss,limit=1] at @s run function metiers:boss/attaque",
       "execute if score #atk m.boss >= #atkcd m.boss as @e[tag=metiers.boss,limit=1] at @s run function metiers:boss/attaque")
_rempl("encours", "scoreboard players operation #s15 m.boss /= #20 m.const\n",
       "scoreboard players operation #s15 m.boss /= #20 m.const\n"
       "execute if score #rg m.boss matches 18.. run scoreboard players operation #s15 m.boss *= #2 m.const\n")
add_lines(BF + "encours.mcfunction", [
    f"execute as @e[type=minecraft:marker,tag=metiers.bz] at @s run function {NS}:boss/zone",
    # aura (rang 14+) : toutes les 2 s, ronge ceux qui restent collés au boss
    "scoreboard players operation #m4 m.boss = #temps m.boss", "scoreboard players operation #m4 m.boss %= #4 m.const",
    f"execute if score #rg m.boss matches 14.. if score #m4 m.boss matches 0 at @e[tag=metiers.boss,limit=1] as @a[distance=..4.5,{PL2}] run {coup(2, 'wither')}",
    f"execute if score #rg m.boss matches 14.. if score #m4 m.boss matches 0 at @e[tag=metiers.boss,limit=1] run particle minecraft:soul ~ ~1 ~ 2.5 0.5 2.5 0.01 12"])
add_lines(BF + "vague.mcfunction", [
    # bouclier (rang 10+) : à chaque vague, une couche de vie en plus à casser
    "execute if score #rg m.boss matches 10.. run effect give @s minecraft:absorption 60 4 true",
    f'execute if score #rg m.boss matches 10.. run tellraw @a {PREFIX},{{"text":"Un bouclier runique entoure le boss.","color":"light_purple"}}]'])
add_lines(BF + "touche.mcfunction", [
    # ronces (rang 6+) : une touche sur trois renvoie un coup
    "execute unless score #rg m.boss matches 6.. run return 0",
    "execute store result score #rr m.boss run random value 1..3",
    f"execute if score #rr m.boss matches 1 run {coup(3, 'thorns')}",
    "execute if score #rr m.boss matches 1 at @s run particle minecraft:enchanted_hit ~ ~1 ~ 0.4 0.6 0.4 0.1 10"])
add_lines(BF + "fin.mcfunction", ["kill @e[type=minecraft:marker,tag=metiers.bz]"])

# zones : un marqueur brille au sol (annonce), puis frappe
ZONES_B = {  # type : (rayon, particule, impact)
    "forge": (3.0, "minecraft:flame",
              ["particle minecraft:lava ~ ~0.5 ~ 1.2 0.3 1.2 0 20", "particle minecraft:flame ~ ~1 ~ 1.2 1 1.2 0.05 60",
               "playsound minecraft:block.anvil.use hostile @a[distance=..32] ~ ~ ~ 1.5 0.6",
               f"execute as @a[distance=..3,{PL2}] run {coup(8, 'in_fire')}", f"effect give @a[distance=..3,{PL2}] minecraft:slowness 2 1"]),
    "enclume": (2.5, "minecraft:crit",
                ['particle minecraft:block{block_state:"minecraft:anvil"} ~ ~1 ~ 1 1 1 0 60',
                 "playsound minecraft:block.anvil.land hostile @a[distance=..32] ~ ~ ~ 2 0.5",
                 f"execute as @a[distance=..2.5,{PL2}] run {coup(12, 'falling_anvil')}",
                 f"effect give @a[distance=..2.5,{PL2}] minecraft:slowness 3 3", f"effect give @a[distance=..2.5,{PL2}] minecraft:nausea 4 0"]),
    "comete": (3.0, "minecraft:dust{color:[1.0,0.45,0.0],scale:1.6}",
               ["particle minecraft:explosion_emitter ~ ~0.5 ~ 0 0 0 0 1", "particle minecraft:flame ~ ~6 ~ 0.3 3 0.3 0 80",
                "playsound minecraft:entity.generic.explode hostile @a[distance=..48] ~ ~ ~ 2 0.7",
                f"execute as @a[distance=..3,{PL2}] run {coup(10, 'explosion')}"]),
    "mine": (3.0, "minecraft:dust{color:[0.3,1.0,0.3],scale:1.6}",
             ["particle minecraft:explosion_emitter ~ ~0.5 ~ 0 0 0 0 1", "playsound minecraft:entity.generic.explode hostile @a[distance=..48] ~ ~ ~ 2 0.9",
              f"execute as @a[distance=..3,{PL2}] run {coup(10, 'explosion')}"]),
}
DELAI_B = {"forge": 3, "enclume": 4, "comete": 4, "mine": 6}   # en demi-secondes
ZT = ["scoreboard players remove @s m.bzt 1"]
for z, (r, part, impact) in ZONES_B.items():
    ZT.append(f"execute if entity @s[tag=metiers.bz_{z}] run return run function {NS}:boss/zone_{z}")
    anneau = [f"particle {part} ~{r * math.cos(a * math.pi / 8):.2f} ~0.15 ~{r * math.sin(a * math.pi / 8):.2f} 0 0 0 0 1" for a in range(16)]
    w(BF + f"zone_{z}.mcfunction", "\n".join([f"execute if score @s m.bzt matches 1.. run return run function {NS}:boss/zone_{z}_a",
                                               f"function {NS}:boss/zone_{z}_c", "kill @s"]))
    w(BF + f"zone_{z}_a.mcfunction", "\n".join(anneau))
    w(BF + f"zone_{z}_c.mcfunction", "\n".join(impact))
ZT.append("kill @s")
w(BF + "zone.mcfunction", "\n".join(ZT))


def zone_b(z, prefixes):
    out = [f'{p}summon minecraft:marker ~ ~0.1 ~ {{Tags:["metiers.bz","metiers.bz_{z}","metiers.bzn"]}}' for p in prefixes]
    return out + [f"scoreboard players set @e[type=minecraft:marker,tag=metiers.bzn] m.bzt {DELAI_B[z]}",
                  "tag @e[type=minecraft:marker,tag=metiers.bzn] remove metiers.bzn"]


ANN2 = lambda txt, col: f'tellraw @a {PREFIX},{{"text":"{txt}","color":"{col}"}}]'
# ---------------------------------------------------------------- deux attaques de plus par boss : (dès 0 point, dès 200 points)
NOUV = {
    1: (("forge", zone_b("forge", [f"execute as @a[distance=..20,{PL2}] at @s run "]) + [ANN2("La forge du Colosse s'embrase sous vos pieds !", "dark_red")]),
        ("enclume", zone_b("enclume", [f"execute as @a[distance=..24,{PL2},sort=random,limit=2] at @s run "]) +
         [ANN2("Des enclumes tombent du ciel !", "dark_red"), "playsound minecraft:block.anvil.place hostile @a ~ ~ ~ 2 0.5"])),
    2: (("ponte", [f'execute as @a[distance=..16,{PL2},sort=random,limit=2] at @s run summon minecraft:cave_spider ~1 ~ ~ {{Tags:["metiers.sbire"]}}',
                   f'execute as @a[distance=..16,{PL2},sort=random,limit=2] at @s run summon minecraft:cave_spider ~-1 ~ ~ {{Tags:["metiers.sbire"]}}',
                   "playsound minecraft:entity.spider.ambient hostile @a ~ ~ ~ 2 0.4", ANN2("La Reine pond autour de vous.", "dark_green")]),
        ("bond_venin", [f"execute as @a[distance=4..30,{PL2},sort=furthest,limit=1] at @s if function {NS}:boss/place_ok run tp @e[tag=metiers.boss,limit=1] ~ ~ ~",
                        f"execute at @s run function {NS}:boss/a_bond_venin2"])),
    3: (("prison", [f"effect give @a[distance=..12,{PL2}] minecraft:slowness 3 6",
                    f"execute as @a[distance=..12,{PL2}] at @s run particle minecraft:snowflake ~ ~1 ~ 0.5 1 0.5 0.02 40",
                    f"execute as @a[distance=..12,{PL2}] run {coup(6, 'freeze')}",
                    "playsound minecraft:block.glass.place hostile @a ~ ~ ~ 2 0.5", ANN2("La Liche vous emprisonne dans la glace !", "aqua")]),
        ("rayon", [f"tag @a[distance=..30,{PL2},sort=random,limit=1] add metiers.cible"] +
         [f"execute anchored eyes facing entity @a[tag=metiers.cible,limit=1] eyes run particle minecraft:snowflake ^ ^ ^{d} 0.05 0.05 0.05 0 2" for d in range(1, 26)] +
         [f"execute as @a[tag=metiers.cible] run {coup(9, 'freeze')}", "effect give @a[tag=metiers.cible] minecraft:slowness 3 2",
          "playsound minecraft:entity.guardian.attack hostile @a ~ ~ ~ 2 0.6", "tag @a remove metiers.cible"])),
    4: (("comete", zone_b("comete", [f"execute as @a[distance=..24,{PL2},sort=random,limit=3] at @s run "]) +
         [ANN2("Des comètes visent les cercles de feu !", "gold"), "playsound minecraft:entity.blaze.ambient hostile @a ~ ~ ~ 2 0.5"]),
        ("anneau", [f"particle minecraft:flame ~{8 * math.cos(a * math.pi / 12):.2f} ~0.3 ~{8 * math.sin(a * math.pi / 12):.2f} 0.2 0.3 0.2 0.02 4" for a in range(24)] +
         [f"execute as @a[distance=5..14,{PL2}] run {coup(8, 'on_fire')}", "playsound minecraft:item.firecharge.use hostile @a ~ ~ ~ 2 0.4",
          ANN2("Un anneau de flammes : collez-vous au Brasier !", "gold")])),
    5: (("mines", zone_b("mine", [f"execute as @a[distance=..16,{PL2}] at @s rotated ~ 0 positioned ^ ^ ^2 run ", "execute at @s run "]) +
         ["playsound minecraft:entity.creeper.primed hostile @a ~ ~ ~ 2 0.5", ANN2("Le Creeper géant sème des mines...", "green")]),
        ("aspiration", [f"execute as @a[distance=..14,{PL2}] at @s facing entity @e[tag=metiers.boss,limit=1] feet rotated ~ 0 positioned ^ ^ ^3 "
                        f"if block ~ ~ ~ #{NS}:boss_vide if block ~ ~1 ~ #{NS}:boss_vide run tp @s ~ ~ ~",
                        f"effect give @a[distance=..14,{PL2}] minecraft:slowness 2 2", "particle minecraft:poof ~ ~1 ~ 4 1 4 0.1 80",
                        f"execute as @a[distance=..4.5,{PL2}] run {coup(6, 'explosion')}",
                        "playsound minecraft:entity.creeper.primed hostile @a ~ ~ ~ 2 0.4", ANN2("Le Creeper géant vous aspire !", "green")])),
}
w(BF + "a_bond_venin2.mcfunction", "\n".join([
    "particle minecraft:item_slime ~ ~1 ~ 2 0.5 2 0 60", "playsound minecraft:entity.spider.hurt hostile @a ~ ~ ~ 2 0.4",
    f"execute as @a[distance=..4,{PL2}] run {coup(6, 'mob_attack')}", f"effect give @a[distance=..4,{PL2}] minecraft:poison 6 1",
    ANN2("La Reine bondit sur sa proie !", "dark_green")]))
for k, ((n0, l0), (n1, l1)) in NOUV.items():
    w(BF + f"a_{n0}.mcfunction", "\n".join(l0))
    w(BF + f"a_{n1}.mcfunction", "\n".join(l1))
AT3 = ["tag @s add metiers.atk", "scoreboard players set #atk m.boss 0"]
for k, b in BOSS.items():
    base = list(b["atks"]) + [NEW_ATK[k][0], NOUV[k][0][0]]
    n = len(base)
    AT3 += [f"execute if score #type m.boss matches {k} store result score #r m.boss run random value 1..{n + 1}",
            # la dernière attaque n'est débloquée qu'à partir du rang 4 (200 points)
            f"execute if score #type m.boss matches {k} if score #r m.boss matches {n + 1} unless score #rg m.boss matches 4.. store result score #r m.boss run random value 1..{n}"]
    AT3 += [f"execute if score #type m.boss matches {k} if score #r m.boss matches {i} run function {NS}:boss/a_{a}" for i, a in enumerate(base + [NOUV[k][1][0]], 1)]
w(BF + "attaque.mcfunction", "\n".join(AT3))

# ---------------------------------------------------------------- tous les dégâts scriptés passent par boss/coup (rang)
_DMG = _re.compile(r"damage @s (\d+) (minecraft:[a-z_]+)(?: by @e\[tag=metiers\.boss,limit=1\])?")
for _f in sorted(os.listdir(os.path.join(ROOT, BF))):
    if not _f.endswith(".mcfunction") or _f.startswith("coup"):
        continue
    _t = _lire(_f[:-11])
    _n = _DMG.sub(lambda m: f'function {NS}:boss/coup {{b:{m.group(1)},t:"{m.group(2)}"}}', _t)
    if _n != _t:
        _ecrire(_f[:-11], _n)

# ---------------------------------------------------------------- récompenses proportionnelles au rang
RC2 = ["scoreboard players set #e m.boss 3", "scoreboard players operation #e2 m.boss = #rg m.boss",
       "scoreboard players operation #e2 m.boss /= #4 m.const", "scoreboard players operation #e m.boss += #e2 m.boss",
       "execute if entity @s[tag=metiers.btop] run scoreboard players add #e m.boss 2",
       "scoreboard players operation @s m.ecl += #e m.boss",
       # 30 % du niveau de Chasseur en cours, x (100 + 15 x rang) / 100
       "scoreboard players operation @s m.tmp = @s m.c_need", "scoreboard players operation @s m.tmp *= #3 m.const",
       "scoreboard players operation @s m.tmp /= #10 m.const", "scoreboard players operation @s m.tmp *= #mul m.boss",
       "scoreboard players operation @s m.tmp /= #100 m.const",
       "scoreboard players operation @s m.c_bal += @s m.tmp", f"function {NS}:c/gain",
       "scoreboard players set #ec m.boss 5000", "scoreboard players operation #ec m.boss *= #mul m.boss",
       "scoreboard players operation #ec m.boss /= #100 m.const",
       "execute if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus += #ec m.boss"]
RC2 += [f"execute if score #type m.boss matches {k} run scoreboard players add @s m.bk{k} 1" for k in BOSS]
RC2 += [f'tellraw @s {PREFIX},{{"text":"Récompense : ","color":"gold"}},{json.dumps(gj("eclat"), ensure_ascii=False)},'
        f'{{"text":" ","color":"gold"}},{{"score":{{"name":"#e","objective":"m.boss"}},"color":"light_purple"}},'
        f'{{"text":" éclats de boss, XP de Chasseur et ","color":"gold"}},{{"score":{{"name":"#ec","objective":"m.boss"}},"color":"yellow"}},'
        f'{{"text":" Écus (rang ","color":"gold"}},{{"score":{{"name":"#rg","objective":"m.boss"}},"color":"red"}},{{"text":").","color":"gold"}}]',
        "particle minecraft:totem_of_undying ~ ~1 ~ 0.5 1 0.5 0.4 80", f"function {NS}:boss/butin"]
w(BF + "recompense.mcfunction", "\n".join(RC2))
_rempl("butin", "scoreboard players operation #gain m.boss *= #2500 m.const\n",
       "scoreboard players operation #gain m.boss *= #2500 m.const\n"
       "scoreboard players operation #gain m.boss *= #mul m.boss\nscoreboard players operation #gain m.boss /= #100 m.const\n")
_rempl("butin", "execute if score #r m.boss <= #chance m.boss if score @s c.ecus matches -2147483648.. run scoreboard players add @s c.ecus 5000",
       "scoreboard players operation #ec m.boss = #mul m.boss\nscoreboard players operation #ec m.boss *= #50 m.const\n"
       "execute if score #r m.boss <= #chance m.boss if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus += #ec m.boss")
_rempl("butin", " décroche le bonus rare du boss : 2 éclats et 5 000 Écus !", " décroche le bonus rare du boss : 2 éclats et des Écus en plus !")

add_lines(F + "refonte/load.mcfunction", [
    "scoreboard objectives add m.bzt dummy",
    "scoreboard players set #4 m.const 4", "scoreboard players set #8 m.const 8", "scoreboard players set #15 m.const 15",
    "scoreboard players set #50 m.const 50",
    # valeurs par défaut (boss repris après un rechargement, ou d'avant cette version)
    "execute unless score #pw m.boss matches 1.. run scoreboard players set #pw m.boss 100",
    "execute unless score #mul m.boss matches 1.. run scoreboard players set #mul m.boss 100",
    "execute unless score #atkcd m.boss matches 1.. run scoreboard players set #atkcd m.boss 10",
    "execute unless score #rg m.boss matches 0.. run scoreboard players set #rg m.boss 0"])

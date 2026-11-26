"""Rang, sorts et ensorcellements des créatures du pack Horreur (26/11/2026).

Appelé par datapack.py juste avant le zip : sorts.ecrire(globals()).

Rang : chaque créature se cale sur le score de métiers (somme des niveaux, +100 par étoile, score m.total du pack
Métiers) du joueur près de qui elle apparaît, par paliers de 50 points. Le rang règle la vie, les dégâts, l'armure,
la fréquence des sorts, les sorts débloqués et les ensorcellements (voir creatures.py). Sans Métiers : rang 0.

Sorts : toutes les SORT_CD ticks (moins avec le rang), une créature en combat lance un de ses sorts débloqués.
Zones : un sort de zone pose un marqueur qui brille au sol (on a le temps de s'écarter), puis frappe.
"""
import math


def ecrire(g):
    w, F, NS, deg = g["w"], g["F"], g["NS"], g["deg"]
    wj, tags_nbt, son, P = g["wj"], g["tags_nbt"], g["son"], g["P"]
    CREATURES, C, SORTS, SORT_CD = g["CREATURES"], g["C"], g["SORTS"], g["SORT_CD"]
    ENS, RANG_MAX, JOBS, OMBRE, PRIMES = g["ENSORCELLEMENTS"], g["RANG_MAX"], g["JOBS"], g["OMBRE"], g["PRIMES"]
    J = "gamemode=!spectator"

    def fn(nom, lignes):
        w(F + nom + ".mcfunction", "\n".join(lignes) if isinstance(lignes, list) else lignes)

    # ------------------------------------------------------------------------------------------ rang
    fn("rang/calc", [
        "# en tant que joueur : #rg = score de métiers / 50 (plafonné), 0 sans le pack Métiers",
        "scoreboard players set #rg hr.tmp 0",
        "execute if score @s m.total matches 1.. run scoreboard players operation #rg hr.tmp = @s m.total",
        "scoreboard players operation #rg hr.tmp /= #k50 hr.cfg",
        f"execute if score #rg hr.tmp matches {RANG_MAX + 1}.. run scoreboard players set #rg hr.tmp {RANG_MAX}"])
    fn("rang/attributs", [
        "$attribute @s minecraft:max_health base set $(hp)",
        "$data modify entity @s Health set value $(hp)f",
        "$attribute @s minecraft:attack_damage base set $(dg)",
        "$attribute @s minecraft:armor base set $(ar)",
        "$attribute @s minecraft:armor_toughness base set $(ro)"])
    for c in CREATURES:
        k = c["id"]
        L = ["scoreboard players operation @s hr.rg = #rg hr.tmp",
             # puissance des coups et des sorts : 100 + 8 par rang
             "scoreboard players operation @s hr.pw = @s hr.rg", "scoreboard players operation @s hr.pw *= #k8 hr.cfg",
             "scoreboard players add @s hr.pw 100",
             # vie : base x (100 + 15 par rang) / 100, plafond du jeu 1 024, Résistance au-delà
             "scoreboard players operation #m hr.tmp = @s hr.rg", "scoreboard players operation #m hr.tmp *= #k15 hr.cfg",
             "scoreboard players add #m hr.tmp 100",
             f"scoreboard players set #hp hr.tmp {c['vie']}", "scoreboard players operation #hp hr.tmp *= #m hr.tmp",
             "scoreboard players operation #hp hr.tmp /= #k100 hr.cfg",
             "scoreboard players set #res hr.tmp 0",
             "execute if score #hp hr.tmp matches 1300.. run scoreboard players set #res hr.tmp 1",
             "execute if score #hp hr.tmp matches 1800.. run scoreboard players set #res hr.tmp 2",
             "execute if score #hp hr.tmp matches 2600.. run scoreboard players set #res hr.tmp 3",
             "execute if score #hp hr.tmp matches 1025.. run scoreboard players set #hp hr.tmp 1024",
             "scoreboard players operation @s hr.pv = #hp hr.tmp",
             "execute store result storage horreur:t g.hp int 1 run scoreboard players get #hp hr.tmp",
             f"scoreboard players set #x hr.tmp {c['degats']}", "scoreboard players operation #x hr.tmp *= @s hr.pw",
             "scoreboard players operation #x hr.tmp /= #k100 hr.cfg",
             "execute store result storage horreur:t g.dg int 1 run scoreboard players get #x hr.tmp",
             f"scoreboard players set #x hr.tmp {c['armure']}", "scoreboard players operation #x hr.tmp += @s hr.rg",
             "execute if score #x hr.tmp matches 31.. run scoreboard players set #x hr.tmp 30",
             "execute store result storage horreur:t g.ar int 1 run scoreboard players get #x hr.tmp",
             "scoreboard players operation #x hr.tmp = @s hr.rg", "scoreboard players operation #x hr.tmp /= #k2 hr.cfg",
             "execute store result storage horreur:t g.ro int 1 run scoreboard players get #x hr.tmp",
             "function horreur:rang/attributs with storage horreur:t g",
             "execute if score #res hr.tmp matches 1 run effect give @s minecraft:resistance infinite 0 true",
             "execute if score #res hr.tmp matches 2 run effect give @s minecraft:resistance infinite 1 true",
             "execute if score #res hr.tmp matches 3 run effect give @s minecraft:resistance infinite 2 true",
             # délai entre deux sorts : base - base x rang / 40 (moitié au rang 20)
             f"scoreboard players set @s hr.scd {SORT_CD[k]}",
             f"scoreboard players set #x hr.tmp {SORT_CD[k]}", "scoreboard players operation #x hr.tmp *= @s hr.rg",
             "scoreboard players operation #x hr.tmp /= #k40 hr.cfg",
             "scoreboard players operation @s hr.scd -= #x hr.tmp",
             f"execute if score @s hr.scd matches ..{SORT_CD[k] // 2} run scoreboard players set @s hr.scd {SORT_CD[k] // 2}",
             # premier sort assez vite après l'apparition
             f"scoreboard players set @s hr.s {SORT_CD[k] // 3}"]
        L += [f"execute if score @s hr.rg matches {r}.. run tag @s add {t}" for r, t, _n, _q in ENS]
        L += ["execute if entity @s[tag=hr.regen] run effect give @s minecraft:regeneration infinite 0 true"]
        if c.get("boss"):
            L += ["execute store result bossbar horreur:boss max run scoreboard players get @s hr.pv",
                  'tellraw @a [{"text":"Le Croque-mitaine se cale sur ","color":"dark_red"},{"selector":"@p[gamemode=!spectator]"},'
                  '{"text":" : rang ","color":"dark_red"},{"score":{"name":"@s","objective":"hr.rg"},"color":"red","bold":true},'
                  '{"text":", ","color":"dark_red"},{"score":{"name":"@s","objective":"hr.pv"},"color":"red"},{"text":" PV.","color":"dark_red"}]']
        fn(f"rang/appliquer_{k}", L)

    # ------------------------------------------------------------------------------------------ outils communs
    fn("sort/frapper", [
        "$execute if entity @e[tag=hr.c,distance=..96] run return run damage @s $(n) $(t) by @e[tag=hr.c,sort=nearest,limit=1]",
        "$damage @s $(n) $(t)"])
    fn("c/commun", [
        "# toutes les 5 ticks, en tant que créature : rang posé sur les joueurs proches (récompenses), ensorcellements, sorts",
        f"scoreboard players operation @a[distance=..48,{J}] hr.rgk = @s hr.rg",
        "execute if entity @s[tag=hr.aura] run function horreur:sort/aura",
        "execute if entity @s[tag=hr.rage,tag=!hr.enrage] run function horreur:sort/rage",
        f"execute unless entity @a[distance=..24,{J}] run return 0",
        # les créatures qui observent de loin ne lancent rien tant qu'elles n'ont pas attaqué
        "execute if entity @s[tag=hr.c.slender] unless score @s hr.etat matches 2 run return 0",
        "execute if entity @s[tag=hr.c.herobrine] unless score @s hr.etat matches 2 run return 0",
        "execute if entity @s[tag=hr.c.dame] unless score @s hr.etat matches 2 run return 0",
        "scoreboard players add @s hr.s 5",
        "execute if score @s hr.s >= @s hr.scd run function horreur:sort/lancer"])
    LA = ["scoreboard players set @s hr.s 0",
          "execute store result score #r hr.tmp run random value 1..3",
          "execute if score #r hr.tmp matches 3 unless score @s hr.rg matches 6.. run scoreboard players set #r hr.tmp 2",
          "execute if score #r hr.tmp matches 2 unless score @s hr.rg matches 2.. run scoreboard players set #r hr.tmp 1",
          "tag @s add hr.lanceur"]
    LA += [f"execute if entity @s[tag=hr.c.{c['id']}] run function horreur:sort/{c['id']}" for c in CREATURES]
    LA += ["tag @s remove hr.lanceur"]
    fn("sort/lancer", LA)
    for c in CREATURES:
        k = c["id"]
        n = len(SORTS[k])
        fn(f"sort/{k}", [f"function horreur:rig/{k}/jouer_attaque"] +
           [f"execute if score #r hr.tmp matches {i} run return run function horreur:sort/{k}_{i}" for i in range(1, n + 1)])

    # ensorcellements
    fn("sort/aura", ["scoreboard players add @s hr.au 5", "execute if score @s hr.au matches ..19 run return 0",
                     "scoreboard players set @s hr.au 0",
                     f"execute if entity @a[distance=..4,{J}] run particle minecraft:soul ~ ~1 ~ 2 0.5 2 0.01 12"] +
       deg(2, f"@a[distance=..4,{J}]", "wither"))
    fn("sort/rage", ["function horreur:c/pct", "execute if score #hp hr.tmp matches 31.. run return 0",
                     "tag @s add hr.enrage",
                     "effect give @s minecraft:strength infinite 0 true", "effect give @s minecraft:speed infinite 0 true",
                     "scoreboard players operation @s hr.scd *= #k2 hr.cfg", "scoreboard players operation @s hr.scd /= #k3 hr.cfg",
                     "particle minecraft:angry_villager ~ ~2 ~ 0.6 0.6 0.6 0 12",
                     "playsound minecraft:entity.ravager.roar hostile @a[distance=..32] ~ ~ ~ 1.5 0.7"])
    fn("sort/vampire", ["effect give @s minecraft:regeneration 3 2 true", "particle minecraft:damage_indicator ~ ~1.5 ~ 0.4 0.6 0.4 0.1 6"])
    # Ronces : un coup porté à une créature (projectiles compris) renvoie une partie des dégâts, une fois sur trois
    wj(f"data/{NS}/advancement/riposte.json", {"criteria": {"c": {"trigger": "minecraft:player_hurt_entity", "conditions": {
        "entity": {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"minecraft:nbt": tags_nbt("hr.ronce")}}}}},
        "rewards": {"function": f"{NS}:sort/riposte"}})
    fn("sort/riposte", ["advancement revoke @s only horreur:riposte",
                        "execute store result score #r hr.tmp run random value 1..3",
                        "execute unless score #r hr.tmp matches 1 run return 0",
                        "tag @s add hr.rip",
                        "execute as @e[tag=hr.ronce,sort=nearest,limit=1,distance=..48] at @s run function horreur:sort/riposte_c",
                        "tag @s remove hr.rip"])
    fn("sort/riposte_c", ["particle minecraft:enchanted_hit ~ ~1.2 ~ 0.5 0.6 0.5 0.1 12"] + deg(3, "@a[tag=hr.rip]", "thorns"))

    # ------------------------------------------------------------------------------------------ zones
    ZONES = {  # type : (rayon, particule d'annonce, lignes de l'impact (dans le contexte du marqueur))
        "foudre": (2.5, "minecraft:electric_spark",
                   ["particle minecraft:end_rod ~ ~4 ~ 0.1 4 0.1 0 60", "particle minecraft:explosion ~ ~0.5 ~ 0.5 0.2 0.5 0 3",
                    "playsound minecraft:entity.lightning_bolt.thunder hostile @a[distance=..48] ~ ~ ~ 1.5 1.2",
                    "playsound minecraft:entity.lightning_bolt.impact hostile @a[distance=..16] ~ ~ ~ 2 1"]
                   + deg(7, f"@a[distance=..2.5,{J}]", "lightning_bolt")
                   + [f"effect give @a[distance=..2.5,{J}] minecraft:slowness 2 1 true"]),
        "ballon": (2.5, "minecraft:dust{color:[0.9,0.1,0.1],scale:1.4}",
                   ["particle minecraft:explosion ~ ~0.5 ~ 0.8 0.3 0.8 0 4",
                    "playsound minecraft:entity.generic.explode hostile @a[distance=..24] ~ ~ ~ 1 1.4",
                    "playsound minecraft:entity.witch.celebrate hostile @a[distance=..24] ~ ~ ~ 1 1.6"]
                   + deg(6, f"@a[distance=..2.5,{J}]", "explosion")),
        "crochet": (2.0, "minecraft:dust{color:[0.45,0.45,0.52],scale:1.2}",
                    ["particle minecraft:crit ~ ~1 ~ 0.6 1 0.6 0.4 30",
                     f"playsound {son('pinhead_chaines', 'minecraft:block.chain.break')} hostile @a[distance=..24] ~ ~ ~ 1.5 1"]
                    + deg(6, f"@a[distance=..2,{J}]", "mob_attack")
                    + [f"effect give @a[distance=..2,{J}] minecraft:wither 3 1 true",
                       f"effect give @a[distance=..2,{J}] minecraft:slowness 3 3 true"]),
        "eboulis": (2.0, "minecraft:falling_dust{block_state:\"minecraft:gravel\"}",
                    ["particle minecraft:block{block_state:\"minecraft:gravel\"} ~ ~1.5 ~ 1 1 1 0 60",
                     "playsound minecraft:block.gravel.break hostile @a[distance=..24] ~ ~ ~ 2 0.5"]
                    + deg(6, f"@a[distance=..2,{J}]", "falling_block")
                    + [f"effect give @a[distance=..2,{J}] minecraft:mining_fatigue 6 1 true"]),
        "cauchemar": (3.5, "minecraft:dust{color:[0.55,0.02,0.08],scale:1.6}",
                      ["particle minecraft:large_smoke ~ ~0.5 ~ 1.5 0.4 1.5 0.02 60",
                       f"playsound {son('croque_grondement', 'minecraft:entity.warden.attack_impact')} hostile @a[distance=..32] ~ ~ ~ 1.5 {P('croque_grondement', 1.2)}"]
                      + deg(8, f"@a[distance=..3.5,{J}]", "magic")
                      + [f"effect give @a[distance=..3.5,{J}] minecraft:wither 4 1 true"]),
    }
    TICK = ["scoreboard players remove @s hr.t 5"]
    for z, (r, part, coup) in ZONES.items():
        TICK.append(f"execute if entity @s[tag=hr.z.{z}] run return run function horreur:zone/{z}")
        cercle = [f"particle {part} ~{r * math.cos(a * math.pi / 8):.2f} ~0.15 ~{r * math.sin(a * math.pi / 8):.2f} 0 0 0 0 1" for a in range(16)]
        fn(f"zone/{z}", [f"execute if score @s hr.t matches 1.. run return run function horreur:zone/{z}_annonce",
                         f"function horreur:zone/{z}_coup", "kill @s"])
        fn(f"zone/{z}_annonce", cercle + [f"particle {part} ~ ~0.2 ~ {r / 3:.2f} 0 {r / 3:.2f} 0 4"])
        fn(f"zone/{z}_coup", coup)
    TICK.append("kill @s")
    fn("zone/tick", TICK)

    def zone(z, delai, pos_lignes):
        """pos_lignes : préfixes 'execute ... run' (ou '') devant le summon ; @s = lanceur (garde hr.pw)."""
        out = [f'{p}summon minecraft:marker ~ ~0.1 ~ {{Tags:["hr.e","hr.zone","hr.z.{z}","hr.zneuf"]}}' for p in pos_lignes]
        return out + ["scoreboard players operation @e[type=minecraft:marker,tag=hr.zneuf] hr.pw = @s hr.pw",
                      f"scoreboard players set @e[type=minecraft:marker,tag=hr.zneuf] hr.t {delai}",
                      "tag @e[type=minecraft:marker,tag=hr.zneuf] remove hr.zneuf"]

    def sous(sel):
        return f"execute as {sel} at @s run "

    def ring_vers(dx, dz, sel):
        return f"execute as {sel} at @s positioned ~{dx} ~ ~{dz} run "

    # serviteurs (hr.serv : disparaissent au bout de 90 s)
    def serviteur(base, nom, couleur, pv, extra=""):
        return (f'summon minecraft:{base} ~ ~1 ~ {{Tags:["hr.e","hr.serv"],CustomName:{{"text":"{nom}","color":"{couleur}"}},'
                f'DeathLootTable:"minecraft:empty",PersistenceRequired:1b,attributes:[{{id:"minecraft:max_health",base:{pv}d}}'
                + (',{id:"minecraft:spawn_reinforcements",base:0d}' if base in ("zombie", "husk") else "")
                + f'],Health:{pv}f{extra}}}')

    # attirer vers le lanceur (tag hr.lanceur) de 2 blocs, si la place est libre
    fn("sort/attirer", [
        "execute anchored eyes facing entity @e[tag=hr.lanceur,limit=1] eyes run particle minecraft:dust{color:[0.15,0.15,0.15],scale:1} ^ ^ ^1 0.2 0.2 0.2 0 6",
        "execute facing entity @e[tag=hr.lanceur,limit=1] feet rotated ~ 0 positioned ^ ^ ^2 "
        "if block ~ ~ ~ #horreur:passable if block ~ ~1 ~ #horreur:passable run tp @s ~ ~ ~"])
    # bond : le lanceur saute à côté du joueur le plus proche entre 5 et 30 blocs (#h = hauteur libre voulue)
    fn("sort/bond", [
        "scoreboard players set #ok hr.tmp 0",
        "scoreboard players set #lim hr.tmp 6",
        'summon minecraft:marker ~ ~ ~ {Tags:["hr.pt2"]}',
        f"execute as @p[distance=5..30,{J}] at @s facing entity @e[tag=hr.lanceur,limit=1] feet rotated ~ 0 positioned ^ ^ ^2 run tp @e[type=minecraft:marker,tag=hr.pt2,limit=1] ~ ~ ~",
        "execute as @e[type=minecraft:marker,tag=hr.pt2,limit=1] at @s run function horreur:sol/trouver",
        "execute if score #ok hr.tmp matches 1 run particle minecraft:cloud ~ ~0.5 ~ 0.6 0.3 0.6 0.05 20",
        "execute if score #ok hr.tmp matches 1 run function horreur:c/teleporter",
        "kill @e[type=minecraft:marker,tag=hr.pt2]"])

    S = {}
    # SlenderMan
    S["slender_1"] = ([f"execute as @a[distance=..20,{J}] at @s run playsound {son('slender_statique', 'minecraft:block.portal.ambient')} hostile @s ~ ~ ~ 1 0.7",
                       f"effect give @a[distance=..20,{J}] minecraft:nausea 6 0 true",
                       f"execute as @a[distance=..20,{J}] at @s run particle minecraft:glow ~ ~1.5 ~ 0.4 0.4 0.4 0 10"]
                      + deg(4, f"@a[distance=..20,{J}]"))
    S["slender_2"] = ["function horreur:c/rodeur_cache", "execute at @s run function horreur:sort/slender_2b"]
    S["slender_2b"] = deg(6, f"@a[distance=..3.5,{J}]", "mob_attack") + [f"effect give @a[distance=..3.5,{J}] minecraft:darkness 5 0 true"]
    S["slender_3"] = ([f"execute as @a[distance=..12,{J}] at @s run function horreur:sort/attirer",
                       f"effect give @a[distance=..12,{J}] minecraft:wither 4 1 true",
                       f"effect give @a[distance=..12,{J}] minecraft:slowness 3 1 true",
                       "playsound minecraft:entity.enderman.scream hostile @a[distance=..24] ~ ~ ~ 1.5 0.5"]
                      + deg(3, f"@a[distance=..12,{J}]"))
    # Herobrine
    S["herobrine_1"] = (["playsound minecraft:block.beacon.power_select hostile @a[distance=..24] ~ ~ ~ 1 1.8"]
                        + zone("foudre", 25, [sous(f"@a[distance=..20,{J}]")]))
    S["herobrine_2"] = ([f"effect give @a[distance=..16,{J}] minecraft:weakness 8 1 true", f"effect give @a[distance=..16,{J}] minecraft:hunger 8 2 true",
                         f"effect give @a[distance=..16,{J}] minecraft:mining_fatigue 8 1 true",
                         f"execute as @a[distance=..16,{J}] at @s run particle minecraft:witch ~ ~1 ~ 0.4 0.8 0.4 0 20",
                         "playsound minecraft:entity.illusioner.cast_spell hostile @a[distance=..24] ~ ~ ~ 1.5 0.6"]
                        + deg(3, f"@a[distance=..16,{J}]"))
    S["herobrine_3"] = (["playsound minecraft:block.beacon.power_select hostile @a[distance=..24] ~ ~ ~ 1 1.4"]
                        + zone("foudre", 30, [sous(f"@p[distance=..20,{J}]")] + [ring_vers(dx, dz, f"@p[distance=..20,{J}]")
                                                                            for dx, dz in ((3, 0), (-3, 0), (0, 3), (0, -3))]))
    # Siren Head
    S["siren_1"] = ([f"playsound {son('siren_sirene', 'minecraft:event.raid.horn')} hostile @a[distance=..64] ~ ~6 ~ 4 1.3",
                     f"execute as @a[distance=..20,{J}] at @s run particle minecraft:sonic_boom ~ ~1 ~ 0 0 0 0 1",
                     f"effect give @a[distance=..20,{J}] minecraft:nausea 6 0 true", f"effect give @a[distance=..20,{J}] minecraft:slowness 3 1 true"]
                    + deg(6, f"@a[distance=..20,{J}]", "sonic_boom"))
    S["siren_2"] = ["scoreboard players set #h hr.tmp 8", "function horreur:sort/bond",
                    "execute if score #ok hr.tmp matches 1 at @s run function horreur:c/siren_frappe"]
    S["siren_3"] = [serviteur("husk", "Écho de la sirène", "#a08a6a", 24, ",Silent:1b"),
                    serviteur("husk", "Écho de la sirène", "#a08a6a", 24, ",Silent:1b"),
                    "playsound minecraft:entity.warden.ambient hostile @a[distance=..32] ~ ~ ~ 2 0.6",
                    "scoreboard players set @e[tag=hr.serv,distance=..4] hr.age 0"]
    # La Nonne
    S["nonne_1"] = ["effect give @s minecraft:regeneration 4 2 true", "particle minecraft:enchant ~ ~1.5 ~ 0.5 0.8 0.5 0.5 40",
                    f"effect give @a[distance=..12,{J}] minecraft:weakness 6 0 true",
                    f"playsound {son('nonne_murmure', 'minecraft:entity.vex.ambient')} hostile @a[distance=..20] ~ ~ ~ 1.5 0.8"]
    S["nonne_2"] = ([f"effect give @a[distance=..10,{J}] minecraft:wither 5 1 true", f"effect give @a[distance=..10,{J}] minecraft:blindness 2 0 true",
                     "particle minecraft:soul ~ ~1 ~ 2 1 2 0.02 30", "playsound minecraft:entity.evoker.prepare_wololo hostile @a[distance=..24] ~ ~ ~ 1 0.5"]
                    + deg(4, f"@a[distance=..10,{J}]"))
    S["nonne_3"] = [serviteur("vex", "Sœur damnée", "#d0c8a0", 8), serviteur("vex", "Sœur damnée", "#d0c8a0", 8),
                    "playsound minecraft:entity.vex.charge hostile @a[distance=..24] ~ ~ ~ 1.5 0.5",
                    "scoreboard players set @e[tag=hr.serv,distance=..4] hr.age 0"]
    # Le Clown
    S["clown_1"] = (["playsound minecraft:entity.witch.celebrate hostile @a[distance=..24] ~ ~ ~ 1.5 1.7"]
                    + zone("ballon", 35, [sous(f"@p[distance=..20,{J}]"),
                                          f"execute if score @s hr.rg matches 6.. as @p[distance=..20,{J}] at @s positioned ~3 ~ ~1 run ",
                                          f"execute if score @s hr.rg matches 6.. as @p[distance=..20,{J}] at @s positioned ~-2 ~ ~-3 run "]))
    S["clown_2"] = ["function horreur:c/rodeur_cache", "execute at @s run function horreur:sort/clown_2b"]
    S["clown_2b"] = deg(5, f"@a[distance=..3.5,{J}]", "mob_attack") + [f"effect give @a[distance=..3.5,{J}] minecraft:slowness 3 2 true"]
    S["clown_3"] = ([f"execute as @a[distance=..12,{J}] at @s run tp @s ~ ~ ~ ~180 ~",
                     f"effect give @a[distance=..12,{J}] minecraft:nausea 10 0 true", f"effect give @a[distance=..12,{J}] minecraft:slowness 4 2 true",
                     f"playsound {son('clown_rire', 'minecraft:entity.witch.celebrate')} hostile @a[distance=..32] ~ ~ ~ 2 {1 if 'clown_rire' in g['SONS_OK'] else 1.2}"]
                    + deg(3, f"@a[distance=..12,{J}]"))
    # Pinhead
    S["pinhead_1"] = zone("crochet", 20, [sous(f"@a[distance=..16,{J},sort=nearest,limit=2]")])
    S["pinhead_2"] = ([f"effect give @a[distance=..10,{J}] minecraft:slowness 3 6 true",
                       f"execute as @a[distance=..10,{J}] at @s run function horreur:sort/attirer",
                       f"execute as @a[distance=..10,{J}] at @s run particle minecraft:dust{{color:[0.45,0.45,0.52],scale:1.2}} ~ ~1 ~ 0.6 1 0.6 0 30",
                       "playsound minecraft:block.chain.place hostile @a[distance=..24] ~ ~ ~ 2 0.5"]
                      + deg(4, f"@a[distance=..10,{J}]"))
    S["pinhead_3"] = ["function horreur:c/pct", "execute if score #hp hr.tmp matches 26.. run return run function horreur:sort/pinhead_1",
                      "execute if score @s hr.etat matches 2.. run return run function horreur:sort/pinhead_1",
                      "function horreur:c/pinhead_cenobites", "scoreboard players set @s hr.etat 2"]
    # La Dame blanche
    S["dame_1"] = (["playsound minecraft:entity.ghast.scream hostile @a[distance=..32] ~ ~ ~ 2 0.6",
                    f"effect give @a[distance=..14,{J}] minecraft:darkness 5 0 true", "particle minecraft:sonic_boom ~ ~1.4 ~ 0 0 0 0 1"]
                   + deg(5, f"@a[distance=..14,{J}]"))
    S["dame_2"] = ([f"effect give @a[distance=..8,{J}] minecraft:slowness 4 3 true",
                    f"execute as @a[distance=..8,{J}] at @s run particle minecraft:snowflake ~ ~1 ~ 0.5 1 0.5 0.02 30",
                    "playsound minecraft:block.powder_snow.break hostile @a[distance=..24] ~ ~ ~ 2 0.5"]
                   + deg(4, f"@a[distance=..8,{J}]", "freeze"))
    S["dame_3"] = ["function horreur:c/rodeur_cache", "execute at @s run function horreur:sort/dame_3b"]
    S["dame_3b"] = (deg(4, f"@a[distance=..3.5,{J}]") + [f"effect give @a[distance=..3.5,{J}] minecraft:wither 4 1 true",
                                                         "effect give @s minecraft:regeneration 4 2 true"])
    # Le Loup-garou
    S["loup_1"] = ["scoreboard players set #h hr.tmp 2", "function horreur:sort/bond",
                   "execute if score #ok hr.tmp matches 1 at @s run function horreur:sort/loup_1b"]
    S["loup_1b"] = ["playsound minecraft:entity.wolf.growl hostile @a[distance=..24] ~ ~ ~ 2 0.5"] + deg(6, f"@a[distance=..3.5,{J}]", "mob_attack")
    S["loup_2"] = ["effect give @s minecraft:speed 8 1 true", "effect give @s minecraft:strength 8 1 true",
                   "particle minecraft:angry_villager ~ ~2 ~ 0.5 0.5 0.5 0 8",
                   f"playsound {son('loup_hurlement', 'minecraft:entity.wolf.howl')} hostile @a[distance=..64] ~ ~ ~ 2.5 {P('loup_hurlement', 0.6)}"]
    S["loup_3"] = deg(5, f"@a[distance=..5,{J}]", "mob_attack") + [f"effect give @a[distance=..5,{J}] minecraft:wither 6 1 true",
                                                                 f"execute as @a[distance=..5,{J}] at @s run particle minecraft:damage_indicator ~ ~1 ~ 0.3 0.5 0.3 0.1 8"]
    # Le Feu follet
    S["feu_1"] = (deg(3, f"@a[distance=..7,{J}]", "freeze") + [f"effect give @a[distance=..7,{J}] minecraft:slowness 4 1 true",
                                                              "particle minecraft:snowflake ~ ~0.5 ~ 2 1 2 0.02 40"])
    S["feu_2"] = [serviteur("vex", "Lueur", "#7fd8ff", 6), serviteur("vex", "Lueur", "#7fd8ff", 6),
                  "particle minecraft:soul_fire_flame ~ ~0.5 ~ 0.5 0.5 0.5 0.05 20",
                  "scoreboard players set @e[tag=hr.serv,distance=..4] hr.age 0"]
    S["feu_3"] = [f"effect give @a[distance=..8,{J}] minecraft:levitation 2 1 true", f"effect give @a[distance=..8,{J}] minecraft:blindness 3 0 true",
                  "playsound minecraft:block.amethyst_block.chime hostile @a[distance=..16] ~ ~ ~ 1.5 0.5"]
    # Le Rôdeur des grottes
    S["rodeur_1"] = deg(5, f"@a[distance=..4,{J}]", "mob_attack") + [f"effect give @a[distance=..4,{J}] minecraft:wither 4 0 true",
                                                                   "particle minecraft:sweep_attack ~ ~1 ~ 1 0.3 1 0 3"]
    S["rodeur_2"] = [f"effect give @a[distance=..20,{J}] minecraft:darkness 8 0 true", "effect give @s minecraft:speed 6 1 true",
                     "playsound minecraft:ambient.cave hostile @a[distance=..24] ~ ~ ~ 2 0.5"]
    S["rodeur_3"] = zone("eboulis", 25, [sous(f"@a[distance=..16,{J},sort=nearest,limit=2]")])
    # Le Croque-mitaine
    S["croque_1"] = [OMBRE, OMBRE, "execute if score @s hr.rg matches 8.. run " + OMBRE,
                     'tellraw @a[distance=..48] {"text":"Le Croque-mitaine appelle ses ombres !","color":"dark_red"}']
    S["croque_2"] = ["function horreur:c/rodeur_cache", f"execute at @s run effect give @a[distance=..8,{J}] minecraft:blindness 2 0 true"]
    S["croque_3"] = [f"effect give @a[distance=..24,{J}] minecraft:darkness 8 0 true", f"effect give @a[distance=..24,{J}] minecraft:slowness 4 1 true",
                     f"playsound {son('croque_grondement', 'minecraft:entity.warden.roar')} hostile @a[distance=..48] ~ ~ ~ 2.5 {P('croque_grondement', 0.7)}"]
    S["croque_4"] = (['tellraw @a[distance=..48] {"text":"Le sol saigne sous vos pieds...","color":"dark_red"}']
                     + zone("cauchemar", 30, [sous(f"@a[distance=..24,{J}]")]))
    S["croque_5"] = (["particle minecraft:sweep_attack ~ ~1.5 ~ 2.5 0.3 2.5 0 12", "playsound minecraft:entity.player.attack.sweep hostile @a[distance=..24] ~ ~ ~ 2 0.5"]
                     + deg(10, f"@a[distance=..5,{J}]", "mob_attack"))
    S["croque_6"] = [f"effect give @a[distance=..16,{J}] minecraft:slowness 3 6 true", f"effect give @a[distance=..16,{J}] minecraft:darkness 6 0 true",
                     f"execute as @a[distance=..16,{J}] at @s run particle minecraft:dust{{color:[0.3,0.0,0.05],scale:1.5}} ~ ~1 ~ 0.7 1 0.7 0 30",
                     'tellraw @a[distance=..48] {"text":"La terreur vous cloue sur place !","color":"dark_red"}']
    S["croque_7"] = (deg(4, f"@a[distance=..20,{J}]") + ["effect give @s minecraft:regeneration 5 3 true",
                                                         f"execute as @a[distance=..20,{J}] at @s run particle minecraft:soul ~ ~1 ~ 0.3 0.6 0.3 0.05 10",
                                                         'tellraw @a[distance=..48] {"text":"Le Croque-mitaine dévore vos âmes !","color":"dark_red"}'])
    # répartition des sorts du Croque-mitaine : 1 à 5 toujours, 6 dès le rang 4, 7 dès le rang 8
    fn("sort/croque", ["function horreur:rig/croque/jouer_attaque",
                       "execute store result score #r hr.tmp run random value 1..7",
                       "execute if score #r hr.tmp matches 7 unless score @s hr.rg matches 8.. run scoreboard players set #r hr.tmp 4",
                       "execute if score #r hr.tmp matches 6 unless score @s hr.rg matches 4.. run scoreboard players set #r hr.tmp 5"]
       + [f"execute if score #r hr.tmp matches {i} run return run function horreur:sort/croque_{i}" for i in range(1, 8)])
    for nom, lignes in S.items():
        fn(f"sort/{nom}", lignes)

    # ------------------------------------------------------------------------------------------ récompense du Croque-mitaine
    # 26/11/2026 : plus aucun objet. Tous les joueurs à 48 blocs du coup final : cristaux de chaque métier, XP, et pour
    # ceux qui n'ont pas porté le coup final la même prime en Écus et la même XP Chasseur que le tueur (tue/croque).
    # Tout est multiplié par (100 + 15 x rang) / 100.
    cr = C["croque"]
    fn("croque/recompense", [
        "scoreboard players set #m hr.tmp 0", "scoreboard players operation #m hr.tmp = @s hr.rgk",
        "scoreboard players operation #m hr.tmp *= #k15 hr.cfg", "scoreboard players add #m hr.tmp 100",
        "scoreboard players set #cr hr.tmp 10", "scoreboard players operation #cr hr.tmp *= #m hr.tmp",
        "scoreboard players operation #cr hr.tmp /= #k100 hr.cfg"]
        + [f"execute if score @s m.cr_{j} matches -2147483648.. run scoreboard players operation @s m.cr_{j} += #cr hr.tmp" for j in JOBS]
        + ["xp add @s 300 points",
           "execute if entity @s[tag=hr.tueur] run return run function horreur:croque/message",
           f"scoreboard players set #pr hr.tmp {PRIMES['croque']}",
           "execute if score #sang hr.cfg matches 1 run scoreboard players operation #pr hr.tmp += #pr hr.tmp",
           "scoreboard players operation #pr hr.tmp *= #m hr.tmp", "scoreboard players operation #pr hr.tmp /= #k100 hr.cfg",
           "execute if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus += #pr hr.tmp",
           f"scoreboard players set #x hr.tmp {cr['xp']}", "scoreboard players operation #x hr.tmp *= #m hr.tmp",
           "scoreboard players operation #x hr.tmp /= #k100 hr.cfg",
           "execute unless score @s m.afk matches 240.. if score @s m.c_bal matches -2147483648.. run scoreboard players operation @s m.c_bal += #x hr.tmp",
           "function horreur:croque/message"])
    fn("croque/message", [
        'tellraw @s [{"text":"[Bestiaire] ","color":"dark_red"},{"text":"Croque-mitaine vaincu : +","color":"gold"},'
        '{"score":{"name":"#cr","objective":"hr.tmp"},"color":"aqua"},{"text":" cristaux dans chaque métier, de l\'XP","color":"aqua"},'
        '{"text":" et la prime en Écus.","color":"gold"}]',
        "particle minecraft:totem_of_undying ~ ~1 ~ 0.5 1 0.5 0.4 60",
        "playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 0.7"])

    # nettoyage : le tick des zones (toutes les 5 ticks) s'ajoute à la boucle des créatures
    import os
    chemin = os.path.join(g["ROOT"], F + "creatures.mcfunction")
    with open(chemin, "a", encoding="utf-8") as f:
        f.write("execute if score #t5 hr.tmp matches 0 as @e[type=minecraft:marker,tag=hr.zone] at @s run function horreur:zone/tick\n")

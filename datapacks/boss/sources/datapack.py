"""Genere le pack Boss : build/boss_datapack/, boss.zip et build/boss_rp/ (convention de l'usine).

Deux boss de serveur modelises et animes (item_display sur un mob invisible qui sert de hitbox) :
  - le Grimoire Vivant, au sommet de la Bibliotheque Interdite (dimension boss:grimoire) ;
  - le Corbeau-Epouvantail, dans le Champ maudit (dimension boss:corbeau).
Evenement automatique toutes les 3 a 5 h de jeu (meme avec un seul joueur connecte) : 2 min de preavis
(titre, fenetre Rejoindre / Pas cette fois, message cliquable dans le chat), teleportation des inscrits,
combat, retour de chacun la ou il etait, recompenses. On ne meurt pas dans l'arene : a 3 coeurs, K.O.
"""
import math, os, shutil, sys, zipfile

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from commun import ROOT, RP, NS, F, w, fn, wj, js, dire, titre, barre, blesse, PREF
import arenes, modeles, rigdp
from rig import snbt_matrice

if os.path.exists(os.path.join(ICI, "..", "build")):
    shutil.rmtree(os.path.join(ICI, "..", "build"))

# =============================================================================================== modeles (RP)
RIGS = {
    "grimoire": modeles.grimoire(), "corbeau": modeles.corbeau(),
    "oiseau_a": modeles.corbeau_vol(True), "oiseau_b": modeles.corbeau_vol(False),
    "livre_a": modeles.livre_vol(True), "livre_b": modeles.livre_vol(False),
    "tentacule": modeles.tentacule(), "rune": modeles.rune(), "lune": modeles.lune(),
    "grimoire_encre": modeles.livre_main(),
}
for R in RIGS.values():
    R.construire(RP, NS)

GY, CY = arenes.GY, arenes.CY
B = {1: dict(id="grimoire", nom="Le Grimoire Vivant", court="le Grimoire", col="light_purple", bar="purple", dim="boss:grimoire",
             hb="husk", vue=(0, GY + 14, 22)),
     2: dict(id="corbeau", nom="Le Corbeau-Épouvantail", court="le Corbeau", col="dark_red", bar="red", dim="boss:corbeau",
             hb="zombie", vue=(0, CY + 16, 26))}

# =============================================================================================== pack, dimensions
wj("pack.mcmeta", {"pack": {"description": "Boss : le Grimoire Vivant et le Corbeau-Épouvantail", "min_format": 84, "max_format": 200}})
wj("data/minecraft/tags/function/load.json", {"values": [f"{NS}:load"]})
wj("data/minecraft/tags/function/tick.json", {"values": [f"{NS}:tick"]})

LIT = {"can_set_spawn": "never", "can_sleep": "never", "error_message": {"text": "Impossible de dormir ici."}}


def type_dim(ambiant):
    return {"ambient_light": ambiant,
            "attributes": {"minecraft:gameplay/bed_rule": LIT, "minecraft:gameplay/straw_bed_rule": LIT,
                           "minecraft:gameplay/respawn_anchor_works": False, "minecraft:gameplay/can_start_raid": False},
            "coordinate_scale": 1.0, "has_ceiling": False, "has_ender_dragon_fight": False, "has_fixed_time": True,
            "has_skylight": False, "height": 256, "infiniburn": "#minecraft:infiniburn_end", "logical_height": 256,
            "min_y": 0, "monster_spawn_block_light_limit": 0, "monster_spawn_light_level": 0, "skybox": "none", "timelines": []}


def biome(fog, ciel, particule, proba, herbe=None):
    b = {"attributes": {
            "minecraft:gameplay/natural_mob_spawns": {"argument": {"spawn_costs": {}, "spawns_by_category": {
                k: [] for k in ("ambient", "axolotls", "creature", "misc", "monster", "underground_water_creature", "water_ambient", "water_creature")}},
                "modifier": "overlay"},
            "minecraft:visual/fog_color": fog, "minecraft:visual/sky_color": ciel,
            "minecraft:visual/fog_start_distance": 18.0, "minecraft:visual/fog_end_distance": 150.0,
            "minecraft:visual/ambient_particles": {"argument": [{"particle": {"type": particule}, "probability": proba}], "modifier": "append"},
            "minecraft:audio/ambient_sounds": {"mood": {"block_search_extent": 8, "offset": 2.0, "sound": "minecraft:ambient.soul_sand_valley.mood", "tick_delay": 3000},
                                                "additions": {"sound": "minecraft:ambient.basalt_deltas.additions", "tick_chance": 0.006}},
            "minecraft:audio/background_music": {"default": {"max_delay": 24000, "min_delay": 12000, "sound": "minecraft:music.nether.soul_sand_valley"}}},
         "carvers": [], "downfall": 0.0, "effects": {"water_color": "#3f2a4a"}, "features": [], "has_precipitation": False, "temperature": 0.5}
    if herbe:
        b["effects"]["grass_color"] = herbe
        b["effects"]["foliage_color"] = herbe
        b["effects"]["dry_foliage_color"] = herbe
    return b


wj(f"data/{NS}/dimension_type/bibliotheque.json", type_dim(0.12))
wj(f"data/{NS}/dimension_type/champ_maudit.json", type_dim(0.08))
wj(f"data/{NS}/worldgen/biome/bibliotheque.json", biome("#1e1230", "#120a22", "minecraft:reverse_portal", 0.02))
wj(f"data/{NS}/worldgen/biome/champ_maudit.json", biome("#2a080c", "#1a0406", "minecraft:white_ash", 0.03, herbe="#6b5a3a"))
for d, t, bi in (("grimoire", "bibliotheque", "bibliotheque"), ("corbeau", "champ_maudit", "champ_maudit")):
    wj(f"data/{NS}/dimension/{d}.json", {"type": f"{NS}:{t}", "generator": {"type": "minecraft:flat", "settings": {
        "biome": f"{NS}:{bi}", "features": False, "lakes": False, "layers": [], "structure_overrides": []}}})

# predicats
wj(f"data/{NS}/predicate/accroupi.json", {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"flags": {"is_sneaking": True}}})
wj(f"data/{NS}/predicate/au_sol.json", {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"flags": {"is_on_ground": True}}})
wj(f"data/{NS}/predicate/plane.json", {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"flags": {"is_flying": True}}})
wj(f"data/{NS}/predicate/monte.json", {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"vehicle": {}}})
wj(f"data/{NS}/tags/block/passable.json", {"values": ["#minecraft:air", "minecraft:light", "minecraft:short_dry_grass", "minecraft:tall_dry_grass",
                                                     "minecraft:dead_bush", "#minecraft:wool_carpets", "minecraft:candle"]})

# =============================================================================================== chargement
OBJ = ["bs.ev", "bs.tmp", "bs.an", "bs.g", "bs.c", "bs.k", "bs.ins", "bs.cid", "bs.rx", "bs.ry", "bs.rz", "bs.rd", "bs.gm",
       "bs.v1", "bs.v2", "bs.vu", "bs.ok"]
fn("load", [f"scoreboard objectives add {o} dummy" for o in OBJ] + [
    "scoreboard objectives add bs.rejoindre trigger",
    "scoreboard objectives add bs.pv health",
    "scoreboard objectives add bs.mort deathCount",
    "scoreboard players set #2 bs.tmp 2", "scoreboard players set #10 bs.tmp 10", "scoreboard players set #60 bs.tmp 60",
    "scoreboard players set #100 bs.tmp 100", "scoreboard players set #360 bs.tmp 360",
    "execute unless score #on bs.ev matches 0..1 run scoreboard players set #on bs.ev 1",
    "execute unless score #min bs.ev matches 1.. run scoreboard players set #min bs.ev 180",
    "execute unless score #max bs.ev matches 1.. run scoreboard players set #max bs.ev 300",
    "execute unless score #etat bs.ev matches 0.. run scoreboard players set #etat bs.ev 0",
    "execute unless score #eid bs.ev matches 0.. run scoreboard players set #eid bs.ev 0",
    f"execute unless score #t bs.ev matches 0.. run function {NS}:ev/prochain",
    'bossbar add boss:combat ""', "bossbar set boss:combat style notched_10",
    # un rechargement pendant un combat : on clot proprement (les joueurs rentrent chez eux)
    f"execute if score #etat bs.ev matches 1.. run function {NS}:ev/interrompu",
])
fn("ev/interrompu", [dire("@a", ("Le pack a été rechargé : l'événement de boss en cours est annulé.", "gray")),
                     f"function {NS}:ev/cloture"])

fn("tick", [
    "scoreboard players add #tk bs.ev 1",
    "scoreboard players operation #m4 bs.ev = #tk bs.ev", "scoreboard players set #4 bs.tmp 4",
    "scoreboard players operation #m4 bs.ev %= #4 bs.tmp",
    f"execute if score #tk bs.ev matches 20.. run function {NS}:seconde",
    f"execute if score #etat bs.ev matches 3..4 run function {NS}:combat/tick",
    f"execute if score #m4 bs.ev matches 0 run function {NS}:cape/tick",
])
fn("seconde", [
    "scoreboard players set #tk bs.ev 0",
    "scoreboard players enable @a bs.rejoindre",
    f"execute as @a[scores={{bs.rejoindre=1..}}] at @s run function {NS}:joueur/trigger",
    f"execute as @a[scores={{bs.mort=1..,bs.pv=1..}}] at @s run function {NS}:joueur/mort",
    f"execute as @a at @s run function {NS}:joueur/verifier",
    f"execute if score #etat bs.ev matches 0 run function {NS}:ev/attente",
    f"execute if score #etat bs.ev matches 1 run function {NS}:ev/preavis",
    f"execute if score #etat bs.ev matches 2 run function {NS}:ev/intro",
    f"execute if score #etat bs.ev matches 3 run function {NS}:ev/combat_s",
    f"execute if score #etat bs.ev matches 4 run function {NS}:ev/fin_s",
])

# =============================================================================================== evenement
fn("ev/prochain", [
    "execute store result storage boss:t a int 60 run scoreboard players get #min bs.ev",
    "execute store result storage boss:t b int 60 run scoreboard players get #max bs.ev",
    f"function {NS}:ev/prochain_m with storage boss:t"])
fn("ev/prochain_m", "$execute store result score #t bs.ev run random value $(a)..$(b)")
fn("ev/attente", [
    "execute unless score #on bs.ev matches 1 run return 0",
    "execute unless entity @a[gamemode=!spectator] run return 0",
    "scoreboard players remove #t bs.ev 1",
    f"execute if score #t bs.ev matches ..0 run function {NS}:ev/declencher"])
# pas deux boss en meme temps : le boss de Metiers (alerte ou combat) et le Croque-mitaine passent avant
fn("ev/declencher", [
    "scoreboard players set #occupe bs.tmp 0",
    "execute if score #actif m.boss matches 1 run scoreboard players set #occupe bs.tmp 1",
    "execute if score #compte m.boss matches 1.. run scoreboard players set #occupe bs.tmp 1",
    "execute if entity @e[tag=hr.c.croque] run scoreboard players set #occupe bs.tmp 1",
    "execute if score #occupe bs.tmp matches 1 run return run scoreboard players set #t bs.ev 300",
    "execute unless score #force bs.ev matches 1..2 store result score #boss bs.ev run random value 1..2",
    "execute if score #force bs.ev matches 1..2 run scoreboard players operation #boss bs.ev = #force bs.ev",
    "scoreboard players set #force bs.ev 0",
    f"function {NS}:ev/ouvrir"])
fn("ev/ouvrir", [
    "scoreboard players add #eid bs.ev 1",
    "scoreboard players set #etat bs.ev 1",
    "execute unless score #pvmax bs.ev matches 1.. run scoreboard players set #pvmax bs.ev 120",
    "scoreboard players operation #pv bs.ev = #pvmax bs.ev",
    "scoreboard players set #pvmax bs.ev 120",
    # l'arene se construit (chunks forces) pendant le preavis
    "execute if score #boss bs.ev matches 1 in boss:grimoire run forceload add -64 -64 63 63",
    "execute if score #boss bs.ev matches 2 in boss:corbeau run forceload add -48 -48 47 47",
    f"schedule function {NS}:arene/construire 60t replace",
    f"execute if score #boss bs.ev matches 1 run function {NS}:ev/annonce_1",
    f"execute if score #boss bs.ev matches 2 run function {NS}:ev/annonce_2",
    "execute as @a at @s run playsound minecraft:entity.elder_guardian.curse master @s ~ ~ ~ 0.7 0.5",
    "effect give @a[gamemode=!spectator] minecraft:darkness 3 0 true"])
for k, b in B.items():
    accroche = ("La Bibliothèque Interdite s'éveille…" if k == 1 else "Une lune rouge se lève…")
    fn(f"ev/annonce_{k}", titre("@a", accroche, f"{b['nom']} apparaît dans 2 minutes", "dark_purple" if k == 1 else "dark_red", "gray") + [
        f"dialog show @a {NS}:appel_{b['id']}",
        f"function {NS}:ev/chat_{k}"])
    fn(f"ev/chat_{k}", [
        "execute as @a run function boss:joueur/est_inscrit",
        dire("@a[tag=!bs.in]", {"text": b["nom"], "color": b["col"], "bold": True}, (" rôde. Arène ouverte dans ", "gray"),
             {"score": {"name": "#pv", "objective": "bs.ev"}, "color": "yellow"}, (" s. ", "gray"),
             {"text": "[REJOINDRE]", "color": "green", "bold": True,
              "click_event": {"action": "run_command", "command": "/trigger bs.rejoindre set 1"},
              "hover_event": {"action": "show_text", "value": {"text": "Tu seras téléporté dans l'arène au départ, puis ramené ici.", "color": "gray"}}}),
        dire("@a[tag=bs.in]", ("Tu es inscrit contre ", "gray"), {"text": b["nom"], "color": b["col"]}, (". Départ dans ", "gray"),
             {"score": {"name": "#pv", "objective": "bs.ev"}, "color": "yellow"}, (" s. ", "gray"),
             {"text": "[ME DÉSINSCRIRE]", "color": "red", "click_event": {"action": "run_command", "command": "/trigger bs.rejoindre set 2"}})])
    # la fenetre « succes » qui s'ouvre chez tout le monde
    regle = ("Accroupis-toi près des pupitres pour l'enchaîner au sol, tire-lui dessus quand il flotte."
             if k == 1 else "Il se disperse en corbeaux : tue-les avant qu'ils le rejoignent, sinon il se soigne.")
    wj(f"data/{NS}/dialog/appel_{b['id']}.json", {
        "type": "minecraft:confirmation",
        "title": {"text": b["nom"], "color": b["col"], "bold": True},
        "external_title": {"text": "Boss de serveur"},
        "can_close_with_escape": True, "pause": False, "after_action": "close",
        "body": [{"type": "minecraft:plain_message", "width": 300, "contents": [
            {"text": "Un boss de serveur se réveille !\n\n", "color": "gold", "bold": True},
            {"text": "L'arène ouvre dans 2 minutes. Les inscrits y sont téléportés ensemble, puis ramenés là où ils étaient. "
                     "On ne meurt pas dans l'arène : à 3 cœurs, tu es mis K.O. et renvoyé chez toi, sans rien perdre.\n\n", "color": "gray"},
            {"text": regle + "\n\n", "color": "white"},
            {"text": "Récompense : " + ("le Grimoire familier" if k == 1 else "la Cape de plumes noires") + " (première victoire), Écus, XP Chasseur, éclats de boss.",
             "color": "yellow"}]}],
        "yes": {"label": {"text": "Rejoindre", "color": "green", "bold": True}, "width": 140,
                "action": {"type": "minecraft:run_command", "command": "trigger bs.rejoindre set 1"}},
        "no": {"label": {"text": "Pas cette fois", "color": "gray"}, "width": 140,
               "action": {"type": "minecraft:run_command", "command": "trigger bs.rejoindre set 2"}}})

fn("ev/preavis", [
    "scoreboard players remove #pv bs.ev 1",
    f"execute if score #pv bs.ev matches 90 if score #boss bs.ev matches 1 run function {NS}:ev/chat_1",
    f"execute if score #pv bs.ev matches 90 if score #boss bs.ev matches 2 run function {NS}:ev/chat_2",
    f"execute if score #pv bs.ev matches 60 if score #boss bs.ev matches 1 run function {NS}:ev/chat_1",
    f"execute if score #pv bs.ev matches 60 if score #boss bs.ev matches 2 run function {NS}:ev/chat_2",
    f"execute if score #pv bs.ev matches 30 if score #boss bs.ev matches 1 run function {NS}:ev/chat_1",
    f"execute if score #pv bs.ev matches 30 if score #boss bs.ev matches 2 run function {NS}:ev/chat_2",
    "execute as @a run function boss:joueur/est_inscrit",
    f"execute if score #pv bs.ev matches 1..10 run title @a[tag=bs.in] actionbar [{{\"text\":\"Départ pour l'arène dans \",\"color\":\"gold\"}},{{\"score\":{{\"name\":\"#pv\",\"objective\":\"bs.ev\"}},\"color\":\"yellow\"}},{{\"text\":\" s\",\"color\":\"gold\"}}]",
    f"execute if score #pv bs.ev matches ..0 run function {NS}:ev/depart"])
fn("joueur/est_inscrit", ["tag @s remove bs.in", "execute if score @s bs.ins = #eid bs.ev run tag @s add bs.in"])

fn("ev/depart", [
    "execute as @a run function boss:joueur/est_inscrit",
    "execute store result score #n bs.ev if entity @a[tag=bs.in]",
    f"execute if score #n bs.ev matches 0 run return run function {NS}:ev/personne",
    "scoreboard players set #etat bs.ev 2", "scoreboard players set #intro bs.ev 6", "scoreboard players set #slot bs.tmp 0",
    "scoreboard players set #duree bs.ev 0", "scoreboard players set #lance bs.ev 0",
    f"execute as @a[tag=bs.in] at @s run function {NS}:joueur/entrer",
    f"execute if score #boss bs.ev matches 1 run function {NS}:arene/g/preparer",
    f"execute if score #boss bs.ev matches 2 run function {NS}:arene/c/preparer"])
fn("ev/personne", [
    f"execute if score #boss bs.ev matches 1 run {dire('@a', ('Personne n’a osé ouvrir le Grimoire. Il se referme dans un ricanement de pages… il reviendra.', 'light_purple'))}",
    f"execute if score #boss bs.ev matches 2 run {dire('@a', ('Personne n’est venu au champ. Le Corbeau-Épouvantail croasse de rire… il reviendra.', 'dark_red'))}",
    f"function {NS}:ev/cloture"])

fn("ev/intro", [
    "scoreboard players remove #intro bs.ev 1",
    *[f"execute if score #intro bs.ev matches {n} run title @a[tag=bs.joue] title {js({'text': str(n), 'color': 'gold', 'bold': True})}" for n in (1, 2, 3)],
    "execute if score #intro bs.ev matches 1..3 as @a[tag=bs.joue] at @s run playsound minecraft:block.note_block.basedrum master @s ~ ~ ~ 1 0.7",
    "execute if score #intro bs.ev matches 4 run title @a[tag=bs.joue] title {\"text\":\"Préparez-vous…\",\"color\":\"gray\"}",
    f"execute if score #intro bs.ev matches ..0 run function {NS}:ev/lancer"])
fn("ev/lancer", [
    "scoreboard players set #etat bs.ev 3", "scoreboard players set #lance bs.ev 1",
    f"execute if score #boss bs.ev matches 1 run function {NS}:g/lancer",
    f"execute if score #boss bs.ev matches 2 run function {NS}:c/lancer",
    "execute store result bossbar boss:combat max run scoreboard players get #max bs.ev",
    "execute store result bossbar boss:combat value run scoreboard players get #max bs.ev",
    "bossbar set boss:combat visible true"])
fn("ev/combat_s", [
    "scoreboard players add #duree bs.ev 1",
    "execute in boss:grimoire run bossbar set boss:combat players @a[distance=0..]",
    "execute if score #boss bs.ev matches 2 in boss:corbeau run bossbar set boss:combat players @a[distance=0..]",
    f"execute unless entity @a[tag=bs.joue] run return run function {NS}:ev/defaite",
    f"execute if score #duree bs.ev matches 900.. run return run function {NS}:ev/defaite"])

fn("combat/tick", [
    f"execute if score #boss bs.ev matches 1 run function {NS}:g/tick",
    f"execute if score #boss bs.ev matches 2 run function {NS}:c/tick",
    f"function {NS}:min/tick",
    f"execute as @a[tag=bs.joue] if score @s bs.pv matches ..6 run function {NS}:joueur/ko",
    f"execute as @a[tag=bs.joue] at @s if dimension boss:grimoire if entity @s[y=-100,dy={GY - 10 + 100}] run function {NS}:joueur/vide",
    f"execute as @a[tag=bs.joue] at @s if dimension boss:corbeau if entity @s[y=-100,dy={CY - 8 + 100}] run function {NS}:joueur/vide",
    "execute store result bossbar boss:combat value run data get entity @e[tag=bs.hb,limit=1] Health",
    f"execute if score #etat bs.ev matches 3 if score #lance bs.ev matches 1 unless entity @e[tag=bs.hb] run function {NS}:ev/victoire"])

fn("ev/victoire", [
    "scoreboard players set #etat bs.ev 4", "scoreboard players set #fin bs.ev 12",
    f"execute if score #boss bs.ev matches 1 run function {NS}:rig/grimoire/jouer/mort",
    f"execute if score #boss bs.ev matches 2 run function {NS}:rig/corbeau/jouer/mort",
    "execute as @a run function boss:joueur/est_inscrit",
    *titre("@a[tag=bs.in]", "VICTOIRE !", "Le boss est vaincu. Retour dans 12 secondes.", "gold", "yellow"),
    "execute as @a[tag=bs.in] at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 0.8",
    "execute as @a[tag=bs.in] at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 0.6",
    f"execute if score #boss bs.ev matches 1 run {dire('@a', {'text': 'Le Grimoire Vivant', 'color': 'light_purple', 'bold': True}, (' est vaincu ! Bravo aux ', 'gray'), {'score': {'name': '#n', 'objective': 'bs.ev'}, 'color': 'yellow'}, (' combattants.', 'gray'))}",
    f"execute if score #boss bs.ev matches 2 run {dire('@a', {'text': 'Le Corbeau-Épouvantail', 'color': 'dark_red', 'bold': True}, (' est vaincu ! Bravo aux ', 'gray'), {'score': {'name': '#n', 'objective': 'bs.ev'}, 'color': 'yellow'}, (' combattants.', 'gray'))}",
    f"execute as @a[tag=bs.in] at @s run function {NS}:recompense/donner",
    "kill @e[tag=bs.min]", "kill @e[tag=bs.mind]", "kill @e[tag=bs.fx]",
    "bossbar set boss:combat visible false"])
fn("ev/defaite", [
    "scoreboard players set #etat bs.ev 4", "scoreboard players set #fin bs.ev 6",
    f"execute if score #boss bs.ev matches 1 run function {NS}:rig/grimoire/jouer/rugit",
    f"execute if score #boss bs.ev matches 2 run function {NS}:rig/corbeau/jouer/dispersion",
    "tp @e[tag=bs.hb] ~ -500 ~", "kill @e[tag=bs.hb]",
    "kill @e[tag=bs.min]", "kill @e[tag=bs.mind]", "kill @e[tag=bs.fx]",
    "bossbar set boss:combat visible false",
    f"execute if score #duree bs.ev matches 900.. run {dire('@a', ('Le combat a trop duré : le boss s’en va. Il reviendra…', 'gray'))}",
    f"execute if score #duree bs.ev matches ..899 run {dire('@a', ('Tous les combattants sont K.O. : le boss l’emporte cette fois.', 'gray'))}",
    *titre("@a[tag=bs.joue]", "Défaite…", "Le boss s'en va. Retour dans quelques secondes.", "red", "gray")])
fn("ev/fin_s", ["scoreboard players remove #fin bs.ev 1",
                "execute if score #fin bs.ev matches 8 run kill @e[type=minecraft:item_display,tag=bs.os]",
                f"execute if score #fin bs.ev matches ..0 run function {NS}:ev/cloture"])
fn("ev/cloture", [
    "execute as @a at @s if dimension boss:grimoire run function boss:joueur/retour",
    "execute as @a at @s if dimension boss:corbeau run function boss:joueur/retour",
    "tag @a remove bs.joue", "tag @a remove bs.ko",
    "execute as @a[tag=bs.spec] run function boss:joueur/fin_spec",
    "kill @e[tag=bs.e]", "kill @e[tag=bs.hb]",
    "execute in boss:grimoire run kill @e[type=#minecraft:arrows,distance=0..]",
    "execute in boss:corbeau run kill @e[type=#minecraft:arrows,distance=0..]",
    "execute in boss:grimoire run kill @e[type=minecraft:item,distance=0..]",
    "execute in boss:corbeau run kill @e[type=minecraft:item,distance=0..]",
    "execute in boss:grimoire run forceload remove all", "execute in boss:corbeau run forceload remove all",
    "bossbar set boss:combat visible false", "bossbar set boss:combat players",
    "scoreboard players set #etat bs.ev 0", "scoreboard players set #lance bs.ev 0",
    f"function {NS}:ev/prochain"])

# =============================================================================================== joueurs
fn("joueur/trigger", [
    f"execute if score @s bs.rejoindre matches 1 run function {NS}:joueur/inscrire",
    f"execute if score @s bs.rejoindre matches 2 run function {NS}:joueur/refuser",
    f"execute if score @s bs.rejoindre matches 3 run function {NS}:joueur/regarder",
    f"execute if score @s bs.rejoindre matches 4 run function {NS}:joueur/quitter",
    "scoreboard players set @s bs.rejoindre 0"])
fn("joueur/inscrire", [
    f"execute if score #etat bs.ev matches 2..3 unless entity @s[tag=bs.joue] run return run {dire('@s', ('Le combat a déjà commencé. ', 'gray'), {'text': '[REGARDER]', 'color': 'aqua', 'bold': True, 'click_event': {'action': 'run_command', 'command': '/trigger bs.rejoindre set 3'}})}",
    f"execute unless score #etat bs.ev matches 1 run return run {dire('@s', ('Aucune arène de boss n’est ouverte pour le moment.', 'gray'))}",
    f"execute if score @s bs.ins = #eid bs.ev run return run {dire('@s', ('Tu es déjà inscrit.', 'gray'))}",
    "scoreboard players operation @s bs.ins = #eid bs.ev",
    "execute as @a run function boss:joueur/est_inscrit",
    "execute store result score #n bs.tmp if entity @a[tag=bs.in]",
    dire("@a", {"selector": "@s", "color": "white"}, (" rejoint le combat (", "gray"), {"score": {"name": "#n", "objective": "bs.tmp"}, "color": "yellow"},
         (" inscrit(s)).", "gray")),
    "playsound minecraft:item.goat_horn.sound.1 master @s ~ ~ ~ 0.6 1"])
fn("joueur/refuser", [
    f"execute if score #etat bs.ev matches 1 if score @s bs.ins = #eid bs.ev run return run function {NS}:joueur/desinscrire",
    dire("@s", ("D’accord, ce sera pour la prochaine fois.", "gray"))])
fn("joueur/desinscrire", ["scoreboard players set @s bs.ins 0", dire("@s", ("Tu ne participes plus à ce combat.", "gray"))])
fn("joueur/regarder", [
    f"execute unless score #etat bs.ev matches 3 run return run {dire('@s', ('Pas de combat à regarder pour le moment.', 'gray'))}",
    "execute if entity @s[tag=bs.joue] run return 0",
    "execute if entity @s[tag=bs.spec] run return 0",
    f"function {NS}:joueur/sauver",
    "scoreboard players operation @s bs.cid = #eid bs.ev",
    "tag @s add bs.spec", "gamemode spectator @s",
    *[f"execute if score #boss bs.ev matches {k} in {b['dim']} run tp @s {b['vue'][0]} {b['vue'][1]} {b['vue'][2]} 180 30" for k, b in B.items()],
    dire("@s", ("Tu regardes le combat. ", "gray"), {"text": "[QUITTER]", "color": "red", "click_event": {"action": "run_command", "command": "/trigger bs.rejoindre set 4"}})])
fn("joueur/quitter", [
    f"execute if entity @s[tag=bs.spec] run return run function {NS}:joueur/retour",
    "execute unless entity @s[tag=bs.joue] run return 0",
    "scoreboard players set @s bs.ins 0", "tag @s remove bs.joue",
    dire("@a", {"selector": "@s", "color": "white"}, (" abandonne le combat.", "gray")),
    f"function {NS}:joueur/retour"])

# position de retour (x10 pour garder une decimale), dimension, mode de jeu
fn("joueur/sauver", [
    "execute store result score @s bs.rx run data get entity @s Pos[0] 10",
    "execute store result score @s bs.ry run data get entity @s Pos[1] 10",
    "execute store result score @s bs.rz run data get entity @s Pos[2] 10",
    "scoreboard players set @s bs.rd 0",
    "execute if dimension minecraft:the_nether run scoreboard players set @s bs.rd 1",
    "execute if dimension minecraft:the_end run scoreboard players set @s bs.rd 2",
    "scoreboard players set @s bs.gm 0",
    "execute if entity @s[gamemode=creative] run scoreboard players set @s bs.gm 1",
    "execute if entity @s[gamemode=adventure] run scoreboard players set @s bs.gm 2"])
fn("joueur/retour", [
    "tag @s remove bs.joue", "tag @s remove bs.ko",
    f"execute if entity @s[tag=bs.spec] run function {NS}:joueur/fin_spec",
    "execute if score @s bs.gm matches 0 if entity @s[gamemode=adventure] run gamemode survival @s",
    f"execute unless score @s bs.rx = @s bs.rx run return run execute in minecraft:overworld run spreadplayers 0 0 0 1 false @s",
    "execute store result storage boss:r x double 0.1 run scoreboard players get @s bs.rx",
    "execute store result storage boss:r y double 0.1 run scoreboard players get @s bs.ry",
    "execute store result storage boss:r z double 0.1 run scoreboard players get @s bs.rz",
    'data modify storage boss:r d set value "minecraft:overworld"',
    'execute if score @s bs.rd matches 1 run data modify storage boss:r d set value "minecraft:the_nether"',
    'execute if score @s bs.rd matches 2 run data modify storage boss:r d set value "minecraft:the_end"',
    f"function {NS}:joueur/retour_m with storage boss:r",
    "effect clear @s minecraft:darkness", "effect clear @s minecraft:slowness", "effect clear @s minecraft:wither",
    "effect give @s minecraft:resistance 5 4 true", "effect give @s minecraft:slow_falling 5 0 true"])
fn("joueur/retour_m", "$execute in $(d) run tp @s $(x) $(y) $(z)")
fn("joueur/fin_spec", [
    "tag @s remove bs.spec",
    "execute if score @s bs.gm matches 0 run gamemode survival @s",
    "execute if score @s bs.gm matches 1 run gamemode creative @s",
    "execute if score @s bs.gm matches 2 run gamemode adventure @s"])
# toutes les secondes : quelqu'un dans une arene sans y avoir sa place (deconnecte pendant le combat, spectateur...)
fn("joueur/verifier", [
    f"execute if dimension boss:grimoire run function {NS}:joueur/dans_arene",
    f"execute if dimension boss:corbeau run function {NS}:joueur/dans_arene",
    f"execute unless dimension boss:grimoire unless dimension boss:corbeau if entity @s[tag=bs.spec] run function {NS}:joueur/fin_spec",
    "execute unless dimension boss:grimoire unless dimension boss:corbeau if entity @s[tag=bs.joue] run tag @s remove bs.joue"])
fn("joueur/dans_arene", [
    "scoreboard players set #ok bs.tmp 0",
    "execute if score #etat bs.ev matches 2..4 if score @s bs.cid = #eid bs.ev if entity @s[tag=bs.joue] run scoreboard players set #ok bs.tmp 1",
    "execute if score #etat bs.ev matches 2..4 if score @s bs.cid = #eid bs.ev if entity @s[tag=bs.spec] run scoreboard players set #ok bs.tmp 1",
    "execute if score #etat bs.ev matches 4 if score @s bs.cid = #eid bs.ev run scoreboard players set #ok bs.tmp 1",
    # les admins en creatif peuvent visiter les arenes
    "execute if entity @s[gamemode=creative] unless score @s bs.cid = #eid bs.ev run scoreboard players set #ok bs.tmp 1",
    f"execute if score #ok bs.tmp matches 0 run function {NS}:joueur/retour"])
fn("joueur/entrer", [
    f"function {NS}:joueur/sauver",
    "scoreboard players operation @s bs.cid = #eid bs.ev",
    "tag @s add bs.joue", "tag @s remove bs.ko",
    *[f"execute if score #boss bs.ev matches 1 if score #slot bs.tmp matches {i} in boss:grimoire run tp @s {x + .5} {GY + 1} {z + .5} facing 0 {GY + 4} 0"
      for i, (x, z) in enumerate(arenes.G_SPAWN)],
    *[f"execute if score #boss bs.ev matches 2 if score #slot bs.tmp matches {i} in boss:corbeau run tp @s {x + .5} {CY + 1} {z + .5} facing 0 {CY + 3} 0"
      for i, (x, z) in enumerate(arenes.C_SPAWN)],
    "scoreboard players add #slot bs.tmp 1", "execute if score #slot bs.tmp matches 8.. run scoreboard players set #slot bs.tmp 0",
    # mode aventure pendant le combat : on ne casse pas l'arene et on ne monte pas en tour vers le Grimoire
    "execute if score @s bs.gm matches 0 run gamemode adventure @s",
    "effect give @s minecraft:resistance 6 4 true", "effect give @s minecraft:instant_health 1 2 true",
    "scoreboard players set @s bs.vu 0"])
# degats scriptes : K.O. plutot que la mort
fn("joueur/blesse", [
    "$execute if score @s bs.pv matches ..$(lim) run return run function boss:joueur/ko",
    "$damage @s $(d) minecraft:mob_attack"])
fn("joueur/ko", [
    "tag @s remove bs.joue", "tag @s add bs.ko",
    "effect give @s minecraft:instant_health 1 3 true", "effect give @s minecraft:regeneration 10 1 true",
    *titre("@s", "K.O.", "Tu es renvoyé chez toi, sans rien perdre. Tu auras ta part si tes alliés gagnent.", "red", "gray"),
    dire("@a[tag=bs.joue]", {"selector": "@s", "color": "white"}, (" est K.O. !", "red")),
    "playsound minecraft:entity.player.hurt_on_fire master @s ~ ~ ~ 1 0.6",
    f"function {NS}:joueur/retour"])
fn("joueur/vide", [dire("@a[tag=bs.joue]", {"selector": "@s", "color": "white"}, (" est tombé dans le vide !", "gray")),
                   f"function {NS}:joueur/ko"])
# mort malgre tout (gros coup d'un seul tenant) : au reapparaitre, on le ramene la ou il etait
fn("joueur/mort", [
    "scoreboard players set @s bs.mort 0",
    "execute unless score @s bs.cid = #eid bs.ev run return 0",
    "execute unless score #etat bs.ev matches 2..4 run return 0",
    "execute unless entity @s[tag=bs.joue] run return 0",
    "tag @s remove bs.joue",
    f"function {NS}:joueur/retour"])
# un coup porte au boss : petit retour sonore
wj(f"data/{NS}/advancement/frappe.json", {"criteria": {"f": {"trigger": "minecraft:player_hurt_entity", "conditions": {
    "entity": {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"nbt": '{Tags:["bs.hb"]}'}}}}},
    "rewards": {"function": f"{NS}:joueur/frappe"}})
fn("joueur/frappe", [f"advancement revoke @s only {NS}:frappe",
                     "execute if score #boss bs.ev matches 1 run playsound minecraft:item.book.page_turn hostile @a[distance=..24] ~ ~ ~ 1.5 0.6",
                     "execute if score #boss bs.ev matches 2 run playsound minecraft:block.wood.break hostile @a[distance=..24] ~ ~ ~ 1.5 0.6"])

# =============================================================================================== arenes
G_CMDS = arenes.bibliotheque()
C_CMDS = arenes.champ()
N_PART = 2500
for nom, cmds, dim in (("g", G_CMDS, "boss:grimoire"), ("c", C_CMDS, "boss:corbeau")):
    parts = [cmds[i:i + N_PART] for i in range(0, len(cmds), N_PART)]
    for i, p in enumerate(parts):
        fn(f"arene/{nom}/blocs{i}", p)
    fn(f"arene/{nom}/construire", [f"execute in {dim} run function {NS}:arene/{nom}/blocs{i}" for i in range(len(parts))])
fn("arene/construire", [f"execute if score #boss bs.ev matches 1 run function {NS}:arene/g/construire",
                        f"execute if score #boss bs.ev matches 2 run function {NS}:arene/c/construire"])
for i in range(4):
    fn(f"arene/g/ligne_on_{i + 1}", [f"setblock {x} {GY} {z} minecraft:crying_obsidian" for x, z in arenes.ligne_runes(i)])
    fn(f"arene/g/ligne_off_{i + 1}", [f"setblock {x} {GY} {z} minecraft:obsidian" for x, z in arenes.ligne_runes(i)])
    px, pz = arenes.PUPITRES[i]
    fn(f"arene/g/pupitre_casse_{i + 1}", [f"setblock {px} {GY + 1} {pz} minecraft:air",
                                         f"setblock {px} {GY} {pz} minecraft:cobbled_deepslate",
                                         f"particle minecraft:block{{block_state:\"minecraft:lectern\"}} {px} {GY + 1.5} {pz} 0.5 0.5 0.5 0 40",
                                         f"playsound minecraft:block.wood.break hostile @a {px} {GY + 1} {pz} 2 0.6"]
       + [f"setblock {x} {GY} {z} minecraft:cracked_deepslate_tiles" for x, z in arenes.ligne_runes(i)])
fn("arene/g/pilier_tombe", arenes.pilier_cmds(seul=0, detruit=True) + [
    f"particle minecraft:block{{block_state:\"minecraft:polished_blackstone_bricks\"}} {arenes.PILIERS[0][0]} {GY + 6} {arenes.PILIERS[0][1]} 1.2 4 1.2 0 200",
    f"particle minecraft:explosion {arenes.PILIERS[0][0]} {GY + 4} {arenes.PILIERS[0][1]} 1 3 1 0 6",
    "playsound minecraft:entity.generic.explode hostile @a[distance=0..] 11 105 0 3 0.5"])
BORD = arenes.bord_effondre()
N_BORD = 4
nb_tranches = (len(BORD) + N_BORD - 1) // N_BORD
for i in range(nb_tranches):
    l = []
    for (x, z) in BORD[i * N_BORD:(i + 1) * N_BORD]:
        l += [f"particle minecraft:block{{block_state:\"minecraft:deepslate_tiles\"}} {x} {GY + 0.5} {z} 0.4 0.3 0.4 0 12",
              f"fill {x} {GY - 7} {z} {x} {GY + 4} {z} minecraft:air"]
    l.append(f"playsound minecraft:block.deepslate.break hostile @a[distance=0..] {BORD[i * N_BORD][0]} {GY} {BORD[i * N_BORD][1]} 1.5 0.6")
    fn(f"arene/g/bord/{i + 1}", l)
fn("arene/g/bord_tick", ["scoreboard players add #bord bs.g 1"] +
   [f"execute if score #bord bs.g matches {i + 1} run function {NS}:arene/g/bord/{i + 1}" for i in range(nb_tranches)])

# preparation au depart : marqueurs (pupitres, pivot), decor anime
fn("arene/g/preparer", [
    "execute in boss:grimoire run kill @e[tag=bs.e,distance=0..]",
    *[f'execute in boss:grimoire run summon minecraft:marker {x + .5} {GY + 1} {z + .5} {{Tags:["bs.e","bs.pu","bs.pu{i + 1}"]}}' for i, (x, z) in enumerate(arenes.PUPITRES)],
    *[f"scoreboard players set @e[type=minecraft:marker,tag=bs.pu{i + 1},limit=1] bs.k {i + 1}" for i in range(4)],
    "scoreboard players set @e[type=minecraft:marker,tag=bs.pu] bs.g 0",
    f'execute in boss:grimoire run summon minecraft:marker 0 {GY + 6} 0 {{Tags:["bs.e","bs.pivot"]}}',
    *[f"function {NS}:arene/g/ligne_off_{i + 1}" for i in range(4)]])
fn("arene/c/preparer", [
    "execute in boss:corbeau run kill @e[tag=bs.e,distance=0..]",
    *[f'execute in boss:corbeau run summon minecraft:marker {x + .5} {CY + 4.5} {z + .5} {{Tags:["bs.e","bs.epv","bs.epv{i + 1}"]}}' for i, (x, z) in enumerate(arenes.EPOUVANTAILS)],
    *[f"scoreboard players set @e[type=minecraft:marker,tag=bs.epv{i + 1},limit=1] bs.k {i + 1}" for i in range(len(arenes.EPOUVANTAILS))],
    *[f"execute as @e[type=minecraft:marker,tag=bs.epv{i + 1},limit=1] at @s run rotate @s facing 0 {CY + 4.5} 0" for i in range(len(arenes.EPOUVANTAILS))],
    *[f'execute in boss:corbeau run summon minecraft:marker {x + .5} {CY + 1} {z + .5} {{Tags:["bs.e","bs.cit"]}}' for (x, z) in arenes.CITROUILLES],
    # lune rouge, tres loin dans le brouillard
    *[f"execute in boss:corbeau run summon minecraft:item_display -40 {CY + 40} -60 " + nbt.replace("Tags:X", 'Tags:["bs.e","bs.lune"]')
      for _, nbt in rigdp.piece_simple(RIGS["lune"], "X", view=8.0, extra="")],
    "execute as @e[type=minecraft:item_display,tag=bs.lune] at @s run tp @s ~ ~ ~ facing 0 70 0",
    *[f"execute as @e[type=minecraft:item_display,tag=bs.lune] run data merge entity @s {{transformation:{snbt_matrice([[6 * RIGS['lune'].facteurs[p], 0, 0, 0], [0, 6 * RIGS['lune'].facteurs[p], 0, 0], [0, 0, 6 * RIGS['lune'].facteurs[p], 0], [0, 0, 0, 1]])}}}"
      for p in list(RIGS["lune"].facteurs)[:1]],
    # corbeaux qui tournent au-dessus du champ
    *[f"execute in boss:corbeau run summon minecraft:item_display {round(22 * math.cos(a * 0.785), 1)} {CY + 16 + (a % 3) * 3} {round(22 * math.sin(a * 0.785), 1)} "
      f"{{Tags:[\"bs.e\",\"bs.amb\",\"bs.vol\"],Rotation:[{a * 45}f,0f],item:{{id:\"minecraft:paper\",count:1,components:{{\"minecraft:item_model\":\"boss:oiseau_a_racine\"}}}},"
      f"item_display:\"none\",teleport_duration:1,view_range:4f,brightness:{{sky:0,block:6}},transformation:{snbt_matrice([[2.4, 0, 0, 0], [0, 2.4, 0, 0], [0, 0, 2.4, 0], [0, 0, 0, 1]])}}}"
      for a in range(8)]])

# =============================================================================================== squelettes animes
ANIM_G = rigdp.generer(RIGS["grimoire"], modeles.GRIMOIRE_ANIM, f"{NS}:g/anim_defaut", luminosite=11, view=4.0)
ANIM_C = rigdp.generer(RIGS["corbeau"], modeles.CORBEAU_ANIM, f"{NS}:c/anim_defaut", luminosite=9, view=4.0)
VIDE = '{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"boss:vide"}}'
INVIS = ('active_effects:[{id:"minecraft:invisibility",duration:-1,amplifier:0b,show_particles:0b,show_icon:0b},'
         '{id:"minecraft:fire_resistance",duration:-1,amplifier:0b,show_particles:0b,show_icon:0b}]')


def disp_nbt(rig, tags, echelle=1.0, ty=0.0, lum=None):
    """Passagers item_display d'un petit modele (corps + lueur)."""
    R = RIGS[rig]
    out = []
    for o, lueur in R.pieces():
        pid = R.ident_piece(o, lueur)
        k = R.facteurs[pid] * echelle
        m = [[k, 0, 0, 0], [0, k, 0, ty], [0, 0, k, 0], [0, 0, 0, 1]]
        t = list(tags) + (["bs.vol"] if (rig.startswith("oiseau") and not lueur) else []) + (["bs.livd"] if (rig.startswith("livre") and not lueur) else [])
        br = "brightness:{sky:15,block:15}" if lueur else f"brightness:{{sky:0,block:{lum or 10}}}"
        out.append(f'{{id:"minecraft:item_display",Tags:{js(t)},item:{{id:"minecraft:paper",count:1,components:{{"minecraft:item_model":"boss:{pid}"}}}},'
                   f'item_display:"none",teleport_duration:1,view_range:2f,{br},transformation:{snbt_matrice(m)}}}')
    return ",".join(out)


def vex(tags, nom, couleur, pv, degats, passagers, ia=True):
    return ('{Tags:' + js(["bs.e", "bs.min"] + tags) + f',Health:{pv}f,Silent:1b,PersistenceRequired:1b,DeathLootTable:"minecraft:empty",'
            + ("" if ia else "NoAI:1b,")
            + f'CustomName:{js({"text": nom, "color": couleur})},attributes:[{{id:"minecraft:max_health",base:{pv}d}},{{id:"minecraft:attack_damage",base:{degats}d}},{{id:"minecraft:follow_range",base:40d}}],'
            + INVIS.replace("fire_resistance", "fire_resistance") + f',equipment:{{mainhand:{VIDE}}},drop_chances:{{mainhand:0f}},Passengers:[{passagers}]}}')


OISEAU = disp_nbt("oiseau_a", ["bs.e", "bs.mind"], 1.6, -0.35, lum=7)
LIVRE = disp_nbt("livre_a", ["bs.e", "bs.mind"], 1.5, -0.3, lum=11)


def pv_max(base, par_joueur):
    return [f"scoreboard players set #c bs.tmp {par_joueur}",
            "scoreboard players operation #max bs.ev = #n bs.ev", "scoreboard players operation #max bs.ev *= #c bs.tmp",
            f"scoreboard players add #max bs.ev {base}",
            "scoreboard players set #res bs.ev 0",
            "execute if score #max bs.ev matches 1100.. run scoreboard players set #res bs.ev 1",
            "execute if score #max bs.ev matches 1500.. run scoreboard players set #res bs.ev 2",
            "execute if score #max bs.ev matches 1001.. run scoreboard players set #max bs.ev 1000",
            "execute store result storage boss:t hp int 1 run scoreboard players get #max bs.ev"]


def resistance(tag):
    return [f"execute if score #res bs.ev matches 1 run effect give @e[tag={tag},limit=1] minecraft:resistance infinite 0 true",
            f"execute if score #res bs.ev matches 2 run effect give @e[tag={tag},limit=1] minecraft:resistance infinite 1 true"]


HB_ATTR = '{{id:"minecraft:max_health",base:$(hp)d}},{{id:"minecraft:knockback_resistance",base:1d}}'

# ------------------------------------------------------------------------------------------------ Grimoire
fn("g/lancer", pv_max(300, 150) + [
    f"execute in boss:grimoire positioned 0 {GY + 6} 0 run function {NS}:g/invoquer with storage boss:t",
    *resistance("bs.hb.g"),
    f"execute at @e[tag=bs.hb.g,limit=1] run function {NS}:rig/grimoire/invoquer",
    f"function {NS}:rig/grimoire/jouer/apparition",
    'bossbar set boss:combat name {"text":"Le Grimoire Vivant","color":"light_purple","bold":true}', "bossbar set boss:combat color purple",
    "scoreboard players set #etat bs.g 0", "scoreboard players set #t bs.g 0", "scoreboard players set #atk bs.g 100",
    "scoreboard players set #ph bs.g 1", "scoreboard players set #pilier bs.g 0", "scoreboard players set #bordon bs.g 0",
    "scoreboard players operation #need bs.g = #n bs.ev",
    "execute if score #need bs.g matches ..1 run scoreboard players set #need bs.g 2",
    "execute if score #need bs.g matches 5.. run scoreboard players set #need bs.g 4",
    *titre("@a[tag=bs.joue]", "LE GRIMOIRE VIVANT", "Tire-lui dessus quand il flotte, frappe-le quand il descend !", "light_purple", "white"),
    "execute as @a[tag=bs.joue] at @s run playsound minecraft:entity.wither.spawn master @s ~ ~ ~ 0.7 1.4",
    dire("@a[tag=bs.joue]", ("Comment le vaincre : ", "gold"),
         ("accroupis-toi 3 s près d'un pupitre pour l'activer. Quand ", "white"), {"score": {"name": "#need", "objective": "bs.g"}, "color": "yellow"},
         (" pupitres brillent, ses chaînes le tirent au sol 10 s : frappe-le ! Le reste du temps, tire à l'arc. ", "white"),
         ("Esquive les pages : décale-toi quand elles brillent. Ses tentacules éteignent les pupitres : répartissez-vous.", "gray"))])
fn("g/invoquer", "$summon minecraft:husk ~ ~ ~ {Tags:[\"bs.e\",\"bs.hb\",\"bs.hb.g\"],NoAI:1b,NoGravity:1b,Silent:1b,PersistenceRequired:1b,"
   "CanPickUpLoot:0b,DeathLootTable:\"minecraft:empty\",Health:$(hp)f,"
   "CustomName:{text:\"Le Grimoire Vivant\",color:\"light_purple\",bold:true},"
   "attributes:[{id:\"minecraft:max_health\",base:$(hp)d},{id:\"minecraft:scale\",base:3d},{id:\"minecraft:armor\",base:6d},"
   "{id:\"minecraft:knockback_resistance\",base:1d}]," + INVIS + ",equipment:{head:" + VIDE + "},drop_chances:{head:0f}}")
fn("g/anim_defaut", [f"execute if score #etat bs.g matches 1 run return run function {NS}:rig/grimoire/jouer/enchaine",
                     f"function {NS}:rig/grimoire/jouer/vol"])
fn("g/tick", [
    f"function {NS}:rig/grimoire/tick",
    f"execute as @e[tag=bs.hb.g,limit=1] at @s run function {NS}:g/ia",
    f"function {NS}:g/effets",
    f"execute if score #bordon bs.g matches 1 run function {NS}:g/bord"])
fn("g/bord", [f"execute in boss:grimoire run function {NS}:arene/g/bord_tick",
              f"execute if score #bord bs.g matches {nb_tranches}.. run scoreboard players set #bordon bs.g 0"])
fn("g/ia", [
    "execute if score #etat bs.ev matches 4 run return 0",
    "execute unless score #etat bs.g matches 1 run rotate @s facing entity @p[tag=bs.joue] feet",
    "tp @e[type=minecraft:item_display,tag=bs.os.grimoire] ~ ~ ~ ~ 0",
    "scoreboard players add #t bs.g 1",
    f"execute if score #etat bs.g matches 0 run function {NS}:g/vol",
    f"execute if score #etat bs.g matches 1 run function {NS}:g/enchaine",
    f"execute if score #etat bs.g matches 2 run function {NS}:g/remonte",
    f"execute if score #tk bs.ev matches 0 run function {NS}:g/pupitres",
    f"execute if score #tk bs.ev matches 10 run function {NS}:g/pupitres",
    "execute store result score #hp bs.g run data get entity @s Health",
    "scoreboard players operation #pct bs.g = #hp bs.g", "scoreboard players operation #pct bs.g *= #100 bs.tmp",
    "scoreboard players operation #pct bs.g /= #max bs.ev",
    f"execute if score #ph bs.g matches 1 if score #pct bs.g matches ..60 run function {NS}:g/phase2",
    f"execute if score #ph bs.g matches 2 if score #pct bs.g matches ..30 run function {NS}:g/phase3"])
fn("g/vol", [
    "execute as @e[type=minecraft:marker,tag=bs.pivot,limit=1] at @s run tp @s ~ ~ ~ ~1.5 ~",
    "execute at @e[type=minecraft:marker,tag=bs.pivot,limit=1] rotated ~ 0 positioned ^ ^ ^3.5 run tp @s ~ ~ ~",
    "execute if score #t bs.g matches ..60 run return 0",
    "scoreboard players remove #atk bs.g 1",
    f"execute if score #atk bs.g matches ..0 run function {NS}:g/attaque"])
fn("g/attaque", [
    "scoreboard players set #atk bs.g 130",
    "execute if score #ph bs.g matches 2 run scoreboard players set #atk bs.g 105",
    "execute if score #ph bs.g matches 3 run scoreboard players set #atk bs.g 80",
    "execute if score #ph bs.g matches 1 store result score #r bs.tmp run random value 1..3",
    "execute if score #ph bs.g matches 2.. store result score #r bs.tmp run random value 1..5",
    f"execute if score #r bs.tmp matches 1 run return run function {NS}:g/at/pages",
    f"execute if score #r bs.tmp matches 2..3 run return run function {NS}:g/at/tentacule",
    f"execute if score #r bs.tmp matches 4 run return run function {NS}:g/at/runes",
    f"execute if score #r bs.tmp matches 5 run return run function {NS}:g/at/livres"])
# --- pages tranchantes : des lignes brillent 2 s au sol, puis coupent
fn("g/at/pages", [
    f"function {NS}:rig/grimoire/jouer/pages",
    "playsound minecraft:item.book.page_turn hostile @a[distance=..48] ~ ~ ~ 3 0.5",
    barre("@a[tag=bs.joue]", "Les pages brillent : décale-toi !", "light_purple"),
    *[f'execute in boss:grimoire run summon minecraft:marker 0 {GY + 1.2} 0 {{Tags:["bs.e","bs.fx","bs.ligne","bs.neuf"]}}' for _ in range(3)],
    f'execute if score #ph bs.g matches 3 in boss:grimoire run summon minecraft:marker 0 {GY + 1.2} 0 {{Tags:["bs.e","bs.fx","bs.ligne","bs.neuf"]}}',
    f"execute as @e[type=minecraft:marker,tag=bs.neuf] run function {NS}:g/at/ligne_init"])
fn("g/at/ligne_init", [
    "tag @s remove bs.neuf", "scoreboard players set @s bs.k 0",
    "execute store result storage boss:t x int 1 run random value -6..6",
    "execute store result storage boss:t z int 1 run random value -6..6",
    "execute store result storage boss:t r int 1 run random value 0..179",
    f"function {NS}:g/at/ligne_m with storage boss:t"])
fn("g/at/ligne_m", f"$tp @s $(x) {GY + 1.2} $(z) $(r) 0")
fn("g/at/ligne_tick", [
    "scoreboard players add @s bs.k 1",
    f"execute if score @s bs.k matches ..39 if score #m4 bs.ev matches 0 run function {NS}:g/at/ligne_brille",
    f"execute if score @s bs.k matches 40 run function {NS}:g/at/ligne_coupe",
    "execute if score @s bs.k matches 42.. run kill @s"])
fn("g/at/ligne_brille", [f"particle minecraft:dust{{color:[0.8,0.55,1.0],scale:1.4}} ^ ^ ^{d} 0.05 0.02 0.05 0 1" for d in range(-14, 15)] +
   [f"particle minecraft:enchant ^ ^0.4 ^{d} 0 0.2 0 0.6 3" for d in range(-14, 15, 4)])
fn("g/at/ligne_coupe", [f"execute positioned ^ ^ ^{d} run tag @a[tag=bs.joue,distance=..1.4] add bs.t" for d in range(-14, 15)] +
   [f"particle minecraft:sweep_attack ^ ^0.6 ^{d} 0 0 0 0 1" for d in range(-14, 15, 2)] +
   [f"execute as @a[tag=bs.t] run {blesse(7)}", "tag @a remove bs.t",
    "playsound minecraft:entity.player.attack.sweep hostile @a[distance=..32] ~ ~ ~ 2 0.6"])
# --- tentacule : sort du sol sous un joueur, s'abat, laisse une flaque d'encre et eteint les pupitres proches
TENT = RIGS["tentacule"]
TENT_P = [TENT.ident_piece(o, l) for o, l in TENT.pieces()]


def mat_k(pid, s=1.0, ty=0.0, rx=0.0):
    from rig import mul, rot, echelle as ech, trans
    k = TENT.facteurs[pid] * 1.3 * s
    return snbt_matrice(mul(mul(trans(0, ty, 0), rot(rx, 0, 0)), ech(k)))


fn("g/at/tentacule", [
    f"function {NS}:rig/grimoire/jouer/fouet",
    f"execute as @r[tag=bs.joue] at @s run function {NS}:g/at/tent_cible",
    f"execute if score #ph bs.g matches 3 as @r[tag=bs.joue] at @s run function {NS}:g/at/tent_cible"])
fn("g/at/tent_cible", [
    f'summon minecraft:marker ~ {GY + 1} ~ {{Tags:["bs.e","bs.fx","bs.frappe"]}}',
    *[f'summon minecraft:item_display ~ {GY + 1} ~ {{Tags:["bs.e","bs.fx","bs.tentd","bs.tentd{i}"],Rotation:[{i * 0}f,0f],'
      f'item:{{id:"minecraft:paper",count:1,components:{{"minecraft:item_model":"boss:{pid}"}}}},item_display:"none",view_range:3f,'
      + ("brightness:{sky:15,block:15}," if pid.endswith("_l") else "brightness:{sky:0,block:10},")
      + f'transformation:{mat_k(pid, 0.01, -1.0)}}}' for i, pid in enumerate(TENT_P)],
    "execute as @e[type=minecraft:item_display,tag=bs.tentd,tag=!bs.tok] at @s facing entity @e[tag=bs.hb.g,limit=1] feet run rotate @s ~ 0",
    "tag @e[type=minecraft:item_display,tag=bs.tentd] add bs.tok",
    barre("@s", "Le sol se gonfle sous tes pieds : bouge !", "dark_purple"),
    "playsound minecraft:entity.warden.emerge hostile @a[distance=..24] ~ ~ ~ 1.2 1.3"])
for i, pid in enumerate(TENT_P):
    fn(f"g/at/tentd{i}", [
        "scoreboard players add @s bs.k 1",
        f"execute if score @s bs.k matches 2 run data merge entity @s {{start_interpolation:0,interpolation_duration:12,transformation:{mat_k(pid)}}}",
        f"execute if score @s bs.k matches 30 run data merge entity @s {{start_interpolation:0,interpolation_duration:4,transformation:{mat_k(pid, rx=-80)}}}",
        f"execute if score @s bs.k matches 46 run data merge entity @s {{start_interpolation:0,interpolation_duration:10,transformation:{mat_k(pid, 0.01, -1.0, -80)}}}",
        "execute if score @s bs.k matches 58.. run kill @s"])
fn("g/at/frappe_tick", [
    "scoreboard players add @s bs.k 1",
    "execute if score @s bs.k matches ..33 if score #m4 bs.ev matches 0 run particle minecraft:squid_ink ~ ~0.2 ~ 1 0.1 1 0.02 6",
    *[f"execute if score @s bs.k matches ..33 if score #m4 bs.ev matches 0 run particle minecraft:dust{{color:[0.55,0.2,0.9],scale:1.3}} ~{2.4 * math.cos(a / 6 * math.pi):.2f} ~0.15 ~{2.4 * math.sin(a / 6 * math.pi):.2f} 0 0 0 0 1" for a in range(12)],
    f"execute if score @s bs.k matches 34 run function {NS}:g/at/frappe_coup",
    "execute if score @s bs.k matches 36.. run kill @s"])
fn("g/at/frappe_coup", [
    f"execute as @a[tag=bs.joue,distance=..2.6] run {blesse(9)}",
    "effect give @a[tag=bs.joue,distance=..2.6] minecraft:levitation 1 1 true",
    "particle minecraft:explosion ~ ~0.5 ~ 1 0.3 1 0 4", "particle minecraft:squid_ink ~ ~0.5 ~ 1.2 0.4 1.2 0.1 60",
    "playsound minecraft:entity.warden.attack_impact hostile @a[distance=..32] ~ ~ ~ 2 0.8",
    f"execute as @e[type=minecraft:marker,tag=bs.pu.on,distance=..4] run function {NS}:g/pupitre/eteindre",
    'summon minecraft:marker ~ ~ ~ {Tags:["bs.e","bs.fx","bs.encre"]}'])
fn("g/at/encre_tick", [
    "scoreboard players add @s bs.k 1",
    "execute if score #m4 bs.ev matches 0 run particle minecraft:squid_ink ~ ~0.1 ~ 1.1 0 1.1 0 3",
    "execute if score #m4 bs.ev matches 0 run particle minecraft:dust{color:[0.18,0.05,0.3],scale:2} ~ ~0.05 ~ 1.2 0 1.2 0 6",
    "execute if score #tk bs.ev matches 0 run effect give @a[tag=bs.joue,distance=..2] minecraft:slowness 2 1 true",
    "execute if score #tk bs.ev matches 0 run effect give @a[tag=bs.joue,distance=..2] minecraft:wither 2 0 true",
    "execute if score @s bs.k matches 300.. run kill @s"])
# --- rafale de runes (phase 2+)
RUNE_D = disp_nbt("rune", ["bs.e", "bs.fx", "bs.proj", "bs.rnew"], 1.0)
RUNE_SUM = "summon minecraft:item_display ~ ~3 ~ {" + RUNE_D[len('{id:"minecraft:item_display",'):]
fn("g/at/runes", [
    f"function {NS}:rig/grimoire/jouer/pages",
    "scoreboard players set #st bs.tmp 0",
    *[RUNE_SUM for _ in range(4)],
    f"execute if score #ph bs.g matches 3 run {RUNE_SUM}",
    f"execute if score #ph bs.g matches 3 run {RUNE_SUM}",
    f"execute as @e[type=minecraft:item_display,tag=bs.rnew] at @s run function {NS}:g/at/rune_init",
    "playsound minecraft:entity.evoker.cast_spell hostile @a[distance=..48] ~ ~ ~ 2 0.7",
    barre("@a[tag=bs.joue]", "Des runes te prennent pour cible : cours !", "light_purple")])
fn("g/at/rune_init", [
    "tag @s remove bs.rnew", "scoreboard players remove #st bs.tmp 6", "scoreboard players operation @s bs.k = #st bs.tmp",
    "execute facing entity @r[tag=bs.joue] eyes run tp @s ~ ~ ~ ~ ~"])
fn("g/at/rune_tick", [
    "scoreboard players add @s bs.k 1",
    "execute if score @s bs.k matches ..0 run return run particle minecraft:witch ~ ~ ~ 0.2 0.2 0.2 0 1",
    "tp @s ^ ^ ^0.45",
    "particle minecraft:witch ~ ~ ~ 0.1 0.1 0.1 0 2",
    f"execute positioned ~ ~-1 ~ if entity @a[tag=bs.joue,distance=..1.4] run return run function {NS}:g/at/rune_boum",
    f"execute unless block ~ ~ ~ #{NS}:passable run return run function {NS}:g/at/rune_eclat",
    "execute if score @s bs.k matches 70.. run kill @s"])
fn("g/at/rune_boum", [f"execute positioned ~ ~-1 ~ as @a[tag=bs.joue,distance=..1.6] run {blesse(5)}",
                      f"function {NS}:g/at/rune_eclat"])
fn("g/at/rune_eclat", ["particle minecraft:dust{color:[0.7,0.4,1.0],scale:2} ~ ~ ~ 0.3 0.3 0.3 0 15",
                       "playsound minecraft:block.amethyst_block.break hostile @a[distance=..16] ~ ~ ~ 1 0.8", "kill @s"])
# --- livres volants (phase 2+) : sortent des bibliotheques
MURS = [(round(13 * math.cos(math.radians(a))) + .5, GY + 3, round(13 * math.sin(math.radians(a))) + .5) for a in range(22, 360, 45)]
fn("g/at/livres", [
    "scoreboard players operation #nl bs.tmp = #n bs.ev", "scoreboard players operation #nl bs.tmp /= #2 bs.tmp",
    "scoreboard players add #nl bs.tmp 1", "execute if score #nl bs.tmp matches 5.. run scoreboard players set #nl bs.tmp 4",
    f"execute in boss:grimoire run function {NS}:g/at/livre_un",
    barre("@a[tag=bs.joue]", "Les bibliothèques s'ouvrent : des livres maudits s'envolent !", "dark_purple")])
fn("g/at/livre_un", [
    "execute if score #nl bs.tmp matches ..0 run return 0",
    "scoreboard players remove #nl bs.tmp 1",
    "execute store result score #r bs.tmp run random value 0..7",
    *[f"execute if score #r bs.tmp matches {i} run summon minecraft:vex {x} {y} {z} " + vex(["bs.livre"], "Livre maudit", "dark_purple", 10, 3, LIVRE)
      for i, (x, y, z) in enumerate(MURS)],
    "playsound minecraft:item.book.put hostile @a[distance=0..] 0 105 0 2 0.5",
    f"function {NS}:g/at/livre_un"])
fn("g/effets", [
    f"execute as @e[type=minecraft:marker,tag=bs.ligne] at @s run function {NS}:g/at/ligne_tick",
    f"execute as @e[type=minecraft:marker,tag=bs.frappe] at @s run function {NS}:g/at/frappe_tick",
    *[f"execute as @e[type=minecraft:item_display,tag=bs.tentd{i}] at @s run function {NS}:g/at/tentd{i}" for i in range(len(TENT_P))],
    f"execute as @e[type=minecraft:marker,tag=bs.encre] at @s run function {NS}:g/at/encre_tick",
    f"execute as @e[type=minecraft:item_display,tag=bs.proj] at @s run function {NS}:g/at/rune_tick"])
# --- pupitres de scellement
fn("g/pupitres", [
    f"execute as @e[type=minecraft:marker,tag=bs.pu,tag=!bs.pu.mort] at @s run function {NS}:g/pupitre/tick",
    "execute store result score #nact bs.g if entity @e[type=minecraft:marker,tag=bs.pu.on]",
    f"execute if score #etat bs.g matches 0 if score #nact bs.g >= #need bs.g run function {NS}:g/enchainer"])
BARRES = ["▮▯▯▯▯▯", "▮▮▯▯▯▯", "▮▮▮▯▯▯", "▮▮▮▮▯▯", "▮▮▮▮▮▯"]
fn("g/pupitre/tick", [
    f"execute if entity @s[tag=bs.pu.on] run return run function {NS}:g/pupitre/rayon",
    "execute unless entity @a[tag=bs.joue,distance=..2.8,predicate=boss:accroupi] run return run scoreboard players set @s bs.g 0",
    "scoreboard players add @s bs.g 1",
    "particle minecraft:enchant ~ ~1.6 ~ 0.3 0.3 0.3 1 25",
    "playsound minecraft:block.enchantment_table.use block @a[distance=..10] ~ ~ ~ 0.7 1.2",
    *[f"execute if score @s bs.g matches {i + 1} run " + barre("@a[tag=bs.joue,distance=..2.8]", "Scellement " + b, "light_purple") for i, b in enumerate(BARRES)],
    f"execute if score @s bs.g matches 6.. run function {NS}:g/pupitre/allumer"])
fn("g/pupitre/allumer", [
    "tag @s add bs.pu.on", "scoreboard players set @s bs.g 0",
    *[f"execute if score @s bs.k matches {i + 1} run function {NS}:arene/g/ligne_on_{i + 1}" for i in range(4)],
    "playsound minecraft:block.beacon.activate block @a[distance=0..] ~ ~ ~ 2 1.4",
    "particle minecraft:end_rod ~ ~1.5 ~ 0.4 0.6 0.4 0.05 30",
    barre("@a[tag=bs.joue,distance=..3]", "Pupitre activé ! Tenez-en assez en même temps pour l'enchaîner.", "aqua")])
fn("g/pupitre/rayon", [f"execute positioned ~ ~1.3 ~ facing entity @e[tag=bs.hb.g,limit=1] eyes run particle minecraft:end_rod ^ ^ ^{d} 0 0 0 0 1" for d in range(1, 15)])
fn("g/pupitre/eteindre", [
    "tag @s remove bs.pu.on", "scoreboard players set @s bs.g 0",
    *[f"execute if score @s bs.k matches {i + 1} run function {NS}:arene/g/ligne_off_{i + 1}" for i in range(4)],
    "playsound minecraft:block.beacon.deactivate block @a[distance=0..] ~ ~ ~ 2 1"])
fn("g/enchainer", [
    "scoreboard players set #etat bs.g 1", "scoreboard players set #t bs.g 0",
    f"function {NS}:rig/grimoire/jouer/enchaine",
    *titre("@a[tag=bs.joue]", "ENCHAÎNÉ !", "Ses chaînes le tirent au sol : frappez-le !", "aqua", "white"),
    "execute as @a[tag=bs.joue] at @s run playsound minecraft:block.chain.break master @s ~ ~ ~ 1 0.5",
    "execute as @a[tag=bs.joue] at @s run playsound minecraft:entity.iron_golem.damage master @s ~ ~ ~ 1 0.5"])
fn("g/enchaine", [
    f"execute if entity @s[y={GY + 1.6},dy=40] run tp @s ~ ~-0.3 ~",
    f"execute if score #m4 bs.ev matches 0 run function {NS}:g/chaines",
    f"execute if score #t bs.g matches 200.. run function {NS}:g/liberer"])
fn("g/chaines", [f"execute {'if score #pilier bs.g matches 0 ' if i == 0 else ''}positioned {x + .5} {GY + 11} {z + .5} facing entity @s eyes run particle minecraft:dust{{color:[0.5,0.5,0.56],scale:1.3}} ^ ^ ^{d} 0 0 0 0 1"
                 for i, (x, z) in enumerate(arenes.PILIERS) for d in range(1, 13)])
fn("g/liberer", [
    "scoreboard players set #etat bs.g 2", "scoreboard players set #t bs.g 0",
    f"execute as @e[type=minecraft:marker,tag=bs.pu.on] at @s run function {NS}:g/pupitre/eteindre",
    f"function {NS}:rig/grimoire/jouer/vol",
    barre("@a[tag=bs.joue]", "Il brise ses chaînes et remonte ! Réactivez les pupitres.", "light_purple"),
    "playsound minecraft:entity.evoker.prepare_summon hostile @a[distance=..48] ~ ~ ~ 2 0.6"])
fn("g/remonte", ["tp @s ~ ~0.25 ~", f"execute if entity @s[y={GY + 6},dy=50] run scoreboard players set #etat bs.g 0",
                 f"execute if entity @s[y={GY + 6},dy=50] run scoreboard players set #t bs.g 61"])
fn("g/phase2", [
    "scoreboard players set #ph bs.g 2", "scoreboard players set #atk bs.g 70", "scoreboard players set #pilier bs.g 1",
    f"execute unless score #etat bs.g matches 1 run function {NS}:rig/grimoire/jouer/rugit",
    *titre("@a[tag=bs.joue]", "PHASE 2", "Les livres s'envolent ! Gare aux runes.", "light_purple", "white"),
    barre("@a[tag=bs.joue]", "Un pilier s'effondre : moins d'abris contre les pages.", "gold"),
    "execute as @a[tag=bs.joue] at @s run playsound minecraft:entity.ender_dragon.growl master @s ~ ~ ~ 0.8 1.3",
    f"execute in boss:grimoire run function {NS}:arene/g/pilier_tombe",
    "scoreboard players set #nl bs.tmp 2", f"execute in boss:grimoire run function {NS}:g/at/livre_un"])
fn("g/phase3", [
    "scoreboard players set #ph bs.g 3", "scoreboard players set #atk bs.g 70",
    f"execute unless score #etat bs.g matches 1 run function {NS}:rig/grimoire/jouer/rugit",
    *titre("@a[tag=bs.joue]", "PHASE 3", "Le sol s'effondre ! Plus que 2 pupitres.", "light_purple", "white"),
    barre("@a[tag=bs.joue]", "Éloigne-toi du bord : il tombe dans le vide !", "gold"),
    "execute as @a[tag=bs.joue] at @s run playsound minecraft:entity.ender_dragon.growl master @s ~ ~ ~ 1 0.9",
    *[f"execute as @e[type=minecraft:marker,tag=bs.pu{i}] run function {NS}:g/pupitre/eteindre" for i in (3, 4)],
    *[f"tag @e[type=minecraft:marker,tag=bs.pu{i}] add bs.pu.mort" for i in (3, 4)],
    *[f"execute in boss:grimoire run function {NS}:arene/g/pupitre_casse_{i}" for i in (3, 4)],
    "execute if score #need bs.g matches 3.. run scoreboard players set #need bs.g 2",
    "scoreboard players set #bord bs.g 0", "scoreboard players set #bordon bs.g 1"])

# ------------------------------------------------------------------------------------------------ Corbeau
fn("c/lancer", pv_max(350, 160) + [
    f"execute in boss:corbeau positioned 0 {CY + 1} -14 run function {NS}:c/invoquer with storage boss:t",
    *resistance("bs.hb.c"),
    f"execute at @e[tag=bs.hb.c,limit=1] run function {NS}:rig/corbeau/invoquer",
    f"function {NS}:rig/corbeau/jouer/apparition",
    'bossbar set boss:combat name {"text":"Le Corbeau-Épouvantail","color":"dark_red","bold":true}', "bossbar set boss:combat color red",
    "scoreboard players set #etat bs.c 6", "scoreboard players set #t bs.c -10", "scoreboard players set #atk bs.c 120",
    "scoreboard players set #ph bs.c 1", "scoreboard players set #disp bs.c 0", "scoreboard players set #soin bs.c 0",
    "scoreboard players set #arr bs.c 0",
    "scoreboard players operation #unite bs.c = #max bs.ev", "scoreboard players operation #unite bs.c /= #60 bs.tmp",
    "execute if score #unite bs.c matches ..0 run scoreboard players set #unite bs.c 1",
    *titre("@a[tag=bs.joue]", "LE CORBEAU-ÉPOUVANTAIL", "Saute ou recule quand sa croix craque !", "dark_red", "white"),
    "execute as @a[tag=bs.joue] at @s run playsound minecraft:entity.wither.spawn master @s ~ ~ ~ 0.7 0.6",
    dire("@a[tag=bs.joue]", ("Comment le vaincre : ", "gold"),
         ("frappe-le quand il marche. Quand sa tête se tord et que sa croix craque, saute ou recule : il fauche tout autour de lui. ", "white"),
         ("Sous 60 %, il se disperse en corbeaux qui filent vers un épouvantail : tue-les en vol, sinon il se soigne. ", "white"),
         ("Sous 30 %, il se crucifie : esquive sa charge sur le côté, puis frappe le sac pendant qu'il est sonné.", "gray"))])
fn("c/invoquer", "$summon minecraft:zombie ~ ~ ~ {Tags:[\"bs.e\",\"bs.hb\",\"bs.hb.c\"],NoAI:1b,Silent:1b,PersistenceRequired:1b,"
   "CanPickUpLoot:0b,CanBreakDoors:0b,IsBaby:0b,DeathLootTable:\"minecraft:empty\",Health:$(hp)f,Rotation:[0f,0f],"
   "CustomName:{text:\"Le Corbeau-Épouvantail\",color:\"dark_red\",bold:true},"
   "attributes:[{id:\"minecraft:max_health\",base:$(hp)d},{id:\"minecraft:scale\",base:4.5d},{id:\"minecraft:armor\",base:8d},"
   "{id:\"minecraft:knockback_resistance\",base:1d},{id:\"minecraft:movement_speed\",base:0.17d},{id:\"minecraft:follow_range\",base:48d},"
   "{id:\"minecraft:attack_damage\",base:5d},{id:\"minecraft:spawn_reinforcements\",base:0d},{id:\"minecraft:step_height\",base:1.5d}],"
   + INVIS + ",equipment:{head:" + VIDE + "},drop_chances:{head:0f}}")
fn("c/anim_defaut", [
    "execute if score #etat bs.ev matches 4 run return 0",
    f"execute if score #etat bs.c matches 3 run return run function {NS}:rig/corbeau/jouer/croix",
    f"execute if score #etat bs.c matches 4 run return run function {NS}:rig/corbeau/jouer/charge",
    f"execute if score #etat bs.c matches 5 run return run function {NS}:rig/corbeau/jouer/sonne",
    f"execute if score #etat bs.c matches 6 run return run function {NS}:rig/corbeau/jouer/repos",
    f"function {NS}:rig/corbeau/jouer/marche"])
fn("c/tick", [
    f"function {NS}:rig/corbeau/tick",
    "execute as @e[type=minecraft:item_display,tag=bs.amb] at @s run tp @s ^ ^ ^0.35 ~2 ~",
    f"execute as @e[tag=bs.hb.c,limit=1] at @s run function {NS}:c/ia",
    f"function {NS}:c/effets"])
fn("c/ia", [
    "execute if score #etat bs.ev matches 4 run return 0",
    "tp @e[type=minecraft:item_display,tag=bs.os.corbeau] ~ ~ ~ ~ 0",
    "scoreboard players add #t bs.c 1",
    f"execute if score #etat bs.c matches 0 run function {NS}:c/marche",
    f"execute if score #etat bs.c matches 1 run function {NS}:c/attaque_cours",
    f"execute if score #etat bs.c matches 2 run function {NS}:c/disperse",
    f"execute if score #etat bs.c matches 3 run function {NS}:c/crucifie",
    f"execute if score #etat bs.c matches 4 run function {NS}:c/charge",
    f"execute if score #etat bs.c matches 5 run function {NS}:c/sonne",
    f"execute if score #etat bs.c matches 6 run function {NS}:c/attente",
    f"execute if score #etat bs.c matches 8 run function {NS}:c/vers_croix",
    "execute unless score #etat bs.c matches 0 run return 0",
    "execute store result score #hp bs.c run data get entity @s Health",
    "scoreboard players operation #pct bs.c = #hp bs.c", "scoreboard players operation #pct bs.c *= #100 bs.tmp",
    "scoreboard players operation #pct bs.c /= #max bs.ev",
    f"execute if score #ph bs.c matches 1 if score #pct bs.c matches ..60 run function {NS}:c/phase2",
    f"execute if score #ph bs.c matches 2 if score #pct bs.c matches ..30 run function {NS}:c/phase3"])
# attente (apparition, reformation) : immobile, puis il repart
fn("c/attente", ["execute if score #t bs.c matches 50.. run data merge entity @s {NoAI:0b}",
                 "execute if score #t bs.c matches 50.. run scoreboard players set #etat bs.c 0",
                 f"execute if score #t bs.c matches 50 run function {NS}:rig/corbeau/jouer/marche"])
fn("c/marche", [
    "scoreboard players remove #atk bs.c 1",
    "execute if score #ph bs.c matches 2 run scoreboard players remove #disp bs.c 1",
    f"execute if score #ph bs.c matches 2 if score #disp bs.c matches ..0 run return run function {NS}:c/disperser",
    f"execute if score #atk bs.c matches ..0 run function {NS}:c/attaque"])
fn("c/attaque", [
    "scoreboard players set #atk bs.c 130", "execute if score #ph bs.c matches 2 run scoreboard players set #atk bs.c 110",
    "execute store result score #r bs.tmp run random value 1..4",
    f"execute if score #r bs.tmp matches 1..2 run return run function {NS}:c/at/fauchage",
    f"execute if score #r bs.tmp matches 3 run return run function {NS}:c/at/nuee",
    f"execute if score #r bs.tmp matches 4 run function {NS}:c/at/regard"])
fn("c/geler", ["data merge entity @s {NoAI:1b}", "scoreboard players set #etat bs.c 1", "scoreboard players set #t bs.c 0",
               "rotate @s facing entity @p[tag=bs.joue] feet", "execute rotated as @s run rotate @s ~ 0"])
fn("c/at/fauchage", [f"function {NS}:c/geler", "scoreboard players set #att bs.c 1", f"function {NS}:rig/corbeau/jouer/fauchage",
                     "playsound minecraft:entity.zombie.attack_wooden_door hostile @a[distance=..32] ~ ~ ~ 2 0.5",
                     barre("@a[tag=bs.joue,distance=..10]", "Sa croix craque : saute ou recule !", "red")])
fn("c/at/nuee", [f"function {NS}:c/geler", "scoreboard players set #att bs.c 2", f"function {NS}:rig/corbeau/jouer/nuee",
                 "playsound minecraft:entity.phantom.ambient hostile @a[distance=..32] ~ ~ ~ 2 0.6"])
CERCLE = [(4.5 * math.cos(a / 8 * math.pi), 4.5 * math.sin(a / 8 * math.pi)) for a in range(16)]
fn("c/attaque_cours", [
    "execute if score #att bs.c matches 1 if score #t bs.c matches 14 run playsound minecraft:entity.zombie.attack_wooden_door hostile @a[distance=..32] ~ ~ ~ 2 0.4",
    *[f"execute if score #att bs.c matches 1 if score #t bs.c matches 21..32 run particle minecraft:sweep_attack ~{x:.2f} ~1.2 ~{z:.2f} 0 0 0 0 1" for x, z in CERCLE[::2]],
    f"execute if score #att bs.c matches 1 if score #t bs.c matches 24 as @a[tag=bs.joue,distance=..6.5] if predicate {NS}:au_sol run {blesse(10)}",
    "execute if score #att bs.c matches 1 if score #t bs.c matches 24 run playsound minecraft:entity.player.attack.sweep hostile @a[distance=..32] ~ ~ ~ 2 0.5",
    "execute if score #att bs.c matches 2 if score #t bs.c matches 10 run scoreboard players operation #nc bs.tmp = #n bs.ev",
    "execute if score #att bs.c matches 2 if score #t bs.c matches 10 run scoreboard players add #nc bs.tmp 2",
    "execute if score #att bs.c matches 2 if score #t bs.c matches 10 if score #nc bs.tmp matches 9.. run scoreboard players set #nc bs.tmp 8",
    f"execute if score #att bs.c matches 2 if score #t bs.c matches 10 positioned ~ ~5 ~ run function {NS}:c/at/corbeau_un",
    "execute if score #att bs.c matches 2 if score #t bs.c matches 10 run particle minecraft:large_smoke ~ ~5 ~ 0.5 0.8 0.5 0.05 30",
    f"execute if score #t bs.c matches 40.. run function {NS}:c/fin_attaque"])
fn("c/at/corbeau_un", [
    "execute if score #nc bs.tmp matches ..0 run return 0", "scoreboard players remove #nc bs.tmp 1",
    "summon minecraft:vex ~ ~ ~ " + vex(["bs.oiseau"], "Corbeau", "dark_gray", 4, 3, OISEAU),
    "playsound minecraft:entity.phantom.flap hostile @a[distance=..24] ~ ~ ~ 1 1.4",
    f"function {NS}:c/at/corbeau_un"])
fn("c/fin_attaque", ["data merge entity @s {NoAI:0b}", "scoreboard players set #etat bs.c 0",
                     f"function {NS}:rig/corbeau/jouer/marche"])
# --- le regard des epouvantails plantes
for i, (x, z) in enumerate(arenes.EPOUVANTAILS):
    f_ = arenes._face_vers_centre(x, z)
    fn(f"c/yeux_on_{i + 1}", f"setblock {x} {CY + 4} {z} minecraft:jack_o_lantern[facing={f_}]")
    fn(f"c/yeux_off_{i + 1}", f"setblock {x} {CY + 4} {z} minecraft:carved_pumpkin[facing={f_}]")
fn("c/at/regard", [
    "execute if entity @e[type=minecraft:marker,tag=bs.regarde] run return 0",
    "tag @e[type=minecraft:marker,tag=bs.epv,sort=random,limit=1] add bs.regarde",
    "scoreboard players set #rg bs.c 0", "tag @a remove bs.vise", "tag @r[tag=bs.joue] add bs.vise",
    "scoreboard players set @a bs.vu 0",
    *[f"execute if score @e[type=minecraft:marker,tag=bs.regarde,limit=1] bs.k matches {i + 1} in boss:corbeau run function {NS}:c/yeux_on_{i + 1}" for i in range(len(arenes.EPOUVANTAILS))],
    f"function {NS}:rig/corbeau/jouer/torsion",
    barre("@a[tag=bs.vise]", "Un épouvantail te fixe… ne le regarde pas !", "gold"),
    "execute as @a[tag=bs.vise] at @s run playsound minecraft:ambient.cave master @s ~ ~ ~ 1 0.5"])
fn("c/at/rayon", [f"execute positioned ^ ^ ^{d} if entity @e[type=minecraft:marker,tag=bs.regarde,distance=..1.4] run return 1" for d in range(1, 31)] + ["return 0"])
fn("c/at/regard_tick", [
    "scoreboard players add #rg bs.c 1",
    f"execute if score #m4 bs.ev matches 0 as @a[tag=bs.vise] at @s anchored eyes if function {NS}:c/at/rayon run scoreboard players add @s bs.vu 4",
    "execute if score #m4 bs.ev matches 0 at @e[type=minecraft:marker,tag=bs.regarde] run particle minecraft:dust{color:[1,0.35,0.1],scale:1} ~ ~ ~ 0.25 0.25 0.25 0 3",
    f"execute as @a[tag=bs.vise,scores={{bs.vu=40..}}] at @s run function {NS}:c/at/maudit",
    f"execute if score #rg bs.c matches 140.. run function {NS}:c/at/regard_fin"])
fn("c/at/maudit", ["effect give @s minecraft:slowness 6 2", "effect give @s minecraft:darkness 6 0",
                   barre("@s", "Tu l'as regardé trop longtemps…", "red"),
                   "playsound minecraft:entity.warden.nearby_closest master @s ~ ~ ~ 1 0.8",
                   "scoreboard players set @s bs.vu 0", "tag @s remove bs.vise"])
fn("c/at/regard_fin", [
    *[f"execute if score @e[type=minecraft:marker,tag=bs.regarde,limit=1] bs.k matches {i + 1} in boss:corbeau run function {NS}:c/yeux_off_{i + 1}" for i in range(len(arenes.EPOUVANTAILS))],
    "tag @e[type=minecraft:marker,tag=bs.regarde] remove bs.regarde", "tag @a remove bs.vise", "scoreboard players set @a bs.vu 0"])
# --- dispersion en corbeaux (phase 2) : les fragments filent vers un epouvantail ; chaque arrivee le soigne
OFFS = [(0, 0), (1.5, 1), (-1.5, 1), (0, 2.5), (1, -1.5), (-1, -1.5), (2.5, 2), (-2.5, 2), (2, -0.5), (-2, -0.5), (0, 4), (1.5, 3.5), (-1.5, 3.5)]
fn("c/disperser", [
    "data merge entity @s {NoAI:1b}", "scoreboard players set #etat bs.c 2", "scoreboard players set #t bs.c 0",
    f"function {NS}:rig/corbeau/jouer/dispersion",
    "playsound minecraft:entity.phantom.swoop hostile @a[distance=..48] ~ ~ ~ 2 0.5",
    "playsound minecraft:entity.bat.takeoff hostile @a[distance=..48] ~ ~ ~ 2 0.5",
    "tag @e[type=minecraft:marker,tag=bs.cible] remove bs.cible",
    "tag @e[type=minecraft:marker,tag=bs.epv,sort=random,limit=1] add bs.cible",
    *titre("@a[tag=bs.joue]", "", "Il se disperse ! Tue les corbeaux avant qu'ils le rejoignent.", "white", "red")])
fn("c/disperse", [
    "execute if score #t bs.c matches ..26 if score #m4 bs.ev matches 0 run particle minecraft:dust{color:[0.05,0.05,0.08],scale:2} ~ ~5 ~ 1.5 3 1.5 0 30",
    "execute if score #t bs.c matches ..26 if score #m4 bs.ev matches 0 run particle minecraft:large_smoke ~ ~5 ~ 1 2 1 0.02 10",
    f"execute if score #t bs.c matches 26 run function {NS}:c/fragments",
    f"execute if score #t bs.c matches 40.. unless entity @e[tag=bs.frag] run function {NS}:c/reformer"])
fn("c/fragments", [
    "scoreboard players operation #nf bs.tmp = #n bs.ev", "scoreboard players operation #nf bs.tmp *= #2 bs.tmp",
    "scoreboard players add #nf bs.tmp 3", "execute if score #nf bs.tmp matches 14.. run scoreboard players set #nf bs.tmp 13",
    "scoreboard players set #soin bs.c 0", "scoreboard players set #arr bs.c 0",
    *[f"execute if score #nf bs.tmp matches {i + 1}.. positioned ~{dx} ~{3 + (i % 4)} ~{dz} run summon minecraft:vex ~ ~ ~ "
      + vex(["bs.frag"], "Corbeau", "dark_gray", 2, 1, OISEAU, ia=False) for i, (dx, dz) in enumerate(OFFS)],
    "data merge entity @s {Invulnerable:1b,NoGravity:1b}",
    f"execute in boss:corbeau run tp @s 0 {CY - 30} 0",
    f"function {NS}:rig/corbeau/jouer/cache"])
fn("c/frag_arrive", ["scoreboard players operation #soin bs.c += #unite bs.c", "scoreboard players add #arr bs.c 1",
                     "particle minecraft:large_smoke ~ ~ ~ 0.3 0.3 0.3 0.02 10",
                     "playsound minecraft:entity.phantom.flap hostile @a[distance=..24] ~ ~ ~ 1 0.6",
                     "execute on passengers run kill @s", "kill @s"])
fn("c/reformer", [
    f"execute at @e[type=minecraft:marker,tag=bs.cible,limit=1] positioned ~ {CY + 1} ~ facing 0 {CY + 1} 0 positioned ^ ^ ^2.5 run tp @s ~ ~ ~ ~ 0",
    "data merge entity @s {Invulnerable:0b,NoGravity:0b}",
    "execute store result score #hp bs.c run data get entity @s Health",
    "scoreboard players operation #hp bs.c += #soin bs.c",
    "execute if score #hp bs.c > #max bs.ev run scoreboard players operation #hp bs.c = #max bs.ev",
    "execute store result entity @s Health float 1 run scoreboard players get #hp bs.c",
    f"function {NS}:rig/corbeau/jouer/reforme",
    "execute at @e[type=minecraft:marker,tag=bs.cible,limit=1] run particle minecraft:large_smoke ~ ~ ~ 1 2 1 0.05 60",
    f"execute if score #arr bs.c matches 1.. run title @a[tag=bs.joue] actionbar [{{\"score\":{{\"name\":\"#arr\",\"objective\":\"bs.c\"}},\"color\":\"red\"}},{{\"text\":\" corbeau(x) l'ont rejoint : il se soigne !\",\"color\":\"red\"}}]",
    f"execute if score #arr bs.c matches 0 run {barre('@a[tag=bs.joue]', 'Aucun corbeau n’est passé : il se reforme sans soin !', 'green')}",
    "tag @e[type=minecraft:marker,tag=bs.cible] remove bs.cible",
    "scoreboard players set #etat bs.c 6", "scoreboard players set #t bs.c 18", "scoreboard players set #disp bs.c 500",
    "playsound minecraft:entity.zombie.attack_wooden_door hostile @a[distance=..48] ~ ~ ~ 2 0.4"])
fn("c/phase2", [
    "scoreboard players set #ph bs.c 2", "scoreboard players set #disp bs.c 60", "scoreboard players set #atk bs.c 150",
    *titre("@a[tag=bs.joue]", "PHASE 2", "Il se disperse en corbeaux : tue-les avant qu'ils le rejoignent !", "dark_red", "white"),
    barre("@a[tag=bs.joue]", "Reste dans la lumière des citrouilles : la nuit te ronge.", "gold"),
    "execute as @a[tag=bs.joue] at @s run playsound minecraft:entity.ravager.roar master @s ~ ~ ~ 1 0.6"])
fn("c/phase3", [
    "scoreboard players set #ph bs.c 3", "data merge entity @s {NoAI:1b}",
    "scoreboard players set #etat bs.c 8", "scoreboard players set #t bs.c 0",
    f"function {NS}:rig/corbeau/jouer/dispersion",
    *titre("@a[tag=bs.joue]", "PHASE 3", "Il s'est crucifié ! Esquive sa charge sur le côté, puis frappe le sac.", "dark_red", "white"),
    "execute as @a[tag=bs.joue] at @s run playsound minecraft:entity.ender_dragon.growl master @s ~ ~ ~ 1 0.5",
    f"execute as @e[type=minecraft:item_display,tag=bs.lune] run data merge entity @s {{start_interpolation:0,interpolation_duration:80,transformation:{snbt_matrice([[8 * RIGS['lune'].facteurs[list(RIGS['lune'].facteurs)[0]], 0, 0, 0], [0, 8 * RIGS['lune'].facteurs[list(RIGS['lune'].facteurs)[0]], 0, 0], [0, 0, 8 * RIGS['lune'].facteurs[list(RIGS['lune'].facteurs)[0]], 0], [0, 0, 0, 1]])}}}"])
fn("c/vers_croix", [
    "execute if score #t bs.c matches ..26 if score #m4 bs.ev matches 0 run particle minecraft:large_smoke ~ ~5 ~ 1 2 1 0.02 12",
    "execute unless score #t bs.c matches 26 run return 0",
    "data merge entity @s {Invulnerable:1b}",
    f"execute in boss:corbeau run tp @s 0 {CY + 1} 0 0 0",
    f"function {NS}:rig/corbeau/jouer/croix",
    "scoreboard players set #etat bs.c 3", "scoreboard players set #pl bs.c 60", "scoreboard players set #ch bs.c 160",
    f"execute in boss:corbeau run particle minecraft:large_smoke 0 {CY + 5} 0 1 3 1 0.05 80"])
fn("c/crucifie", [
    "scoreboard players remove #pl bs.c 1", "scoreboard players remove #ch bs.c 1",
    f"execute if score #pl bs.c matches ..0 run function {NS}:c/plumes",
    f"execute if score #ch bs.c matches ..0 run function {NS}:c/charge_debut"])
fn("c/plumes", [
    "scoreboard players set #pl bs.c 90",
    f'execute as @a[tag=bs.joue] at @s run summon minecraft:marker ~ {CY + 1} ~ {{Tags:["bs.e","bs.fx","bs.plume"]}}',
    *[f"function {NS}:c/plume_hasard" for _ in range(2)],
    "playsound minecraft:entity.phantom.ambient hostile @a[distance=0..] 0 70 0 3 0.5",
    barre("@a[tag=bs.joue]", "Les plumes tombent : sors des cercles avant le piqué !", "gray")])
fn("c/plume_hasard", ["execute store result storage boss:t x int 1 run random value -15..15",
                      "execute store result storage boss:t z int 1 run random value -15..15",
                      f"execute in boss:corbeau run function {NS}:c/plume_m with storage boss:t"])
fn("c/plume_m", f'$summon minecraft:marker $(x) {CY + 1} $(z) {{Tags:["bs.e","bs.fx","bs.plume"]}}')
fn("c/plume_tick", [
    "scoreboard players add @s bs.k 1",
    *[f"execute if score @s bs.k matches ..39 if score #m4 bs.ev matches 0 run particle minecraft:dust{{color:[0.92,0.92,0.95],scale:1}} ~{2.5 * math.cos(a / 5 * math.pi):.2f} ~0.1 ~{2.5 * math.sin(a / 5 * math.pi):.2f} 0 0 0 0 1" for a in range(10)],
    "execute if score @s bs.k matches ..39 if score #m4 bs.ev matches 0 run particle minecraft:dust{color:[0.05,0.05,0.08],scale:1.5} ~ ~6 ~ 1.2 0.5 1.2 0 6",
    "execute if score @s bs.k matches ..39 if score #m4 bs.ev matches 0 run particle minecraft:white_ash ~ ~3 ~ 1.5 2 1.5 0 10",
    f"execute if score @s bs.k matches 40 run function {NS}:c/pique",
    "execute if score @s bs.k matches 42.. run kill @s"])
fn("c/pique", [f"execute as @a[tag=bs.joue,distance=..2.7] run {blesse(7)}",
               "particle minecraft:large_smoke ~ ~1 ~ 1 1 1 0.05 30", "particle minecraft:dust{color:[0.05,0.05,0.08],scale:2} ~ ~1 ~ 1 1 1 0 40",
               "playsound minecraft:entity.phantom.bite hostile @a[distance=..24] ~ ~ ~ 2 0.7"])
fn("c/charge_debut", [
    "scoreboard players set #etat bs.c 4", "scoreboard players set #t bs.c 0",
    "tag @a remove bs.chc", "tag @a remove bs.ch", "tag @r[tag=bs.joue] add bs.chc",
    f"function {NS}:rig/corbeau/jouer/torsion",
    "playsound minecraft:entity.zombie.attack_wooden_door hostile @a[distance=0..] ~ ~ ~ 3 0.4",
    barre("@a[tag=bs.joue]", "Il se décroche de sa croix : écarte-toi de la ligne rouge !", "red")])
fn("c/charge", [
    "execute if score #t bs.c matches ..18 facing entity @a[tag=bs.chc,limit=1] feet run rotate @s ~ 0",
    *[f"execute if score #t bs.c matches ..20 if score #m4 bs.ev matches 0 rotated ~ 0 run particle minecraft:dust{{color:[0.9,0.1,0.1],scale:1.3}} ^ ^0.2 ^{d} 0.1 0 0.1 0 1" for d in range(1, 19)],
    f"execute if score #t bs.c matches 20 run function {NS}:rig/corbeau/jouer/charge",
    "execute if score #t bs.c matches 20 run playsound minecraft:entity.ravager.roar hostile @a[distance=0..] ~ ~ ~ 3 0.7",
    "execute if score #t bs.c matches 21..46 rotated ~ 0 run tp @s ^ ^ ^0.7",
    f"execute if score #t bs.c matches 21..46 positioned 0 {CY + 1} 0 unless entity @s[distance=..21] run scoreboard players set #t bs.c 47",
    f"execute if score #t bs.c matches 21..46 as @a[tag=bs.joue,tag=!bs.ch,distance=..2.6] run function {NS}:c/charge_touche",
    f"execute if score #t bs.c matches 47.. run function {NS}:c/sonne_debut"])
fn("c/charge_touche", ["tag @s add bs.ch", blesse(9), "effect give @s minecraft:levitation 1 1 true"])
fn("c/sonne_debut", [
    "scoreboard players set #etat bs.c 5", "scoreboard players set #t bs.c 0", "data merge entity @s {Invulnerable:0b}",
    f"function {NS}:rig/corbeau/jouer/sonne",
    *titre("@a[tag=bs.joue]", "", "Il est sonné : frappe le sac !", "white", "gold"),
    "playsound minecraft:block.anvil.land hostile @a[distance=0..] ~ ~ ~ 2 0.5"])
fn("c/sonne", [
    "execute unless score #t bs.c matches 110.. run return 0",
    "particle minecraft:large_smoke ~ ~2 ~ 1 2 1 0.05 50",
    "data merge entity @s {Invulnerable:1b}",
    f"execute in boss:corbeau run tp @s 0 {CY + 1} 0 0 0",
    f"function {NS}:rig/corbeau/jouer/croix",
    "scoreboard players set #etat bs.c 3", "scoreboard players set #ch bs.c 220", "tag @a remove bs.chc"])
fn("c/effets", [
    f"execute as @e[tag=bs.frag] at @s facing entity @e[type=minecraft:marker,tag=bs.cible,limit=1] feet run tp @s ^ ^ ^0.2 ~ ~",
    f"execute as @e[tag=bs.frag] at @s if entity @e[type=minecraft:marker,tag=bs.cible,distance=..1.6] run function {NS}:c/frag_arrive",
    f"execute as @e[type=minecraft:marker,tag=bs.plume] at @s run function {NS}:c/plume_tick",
    f"execute if entity @e[type=minecraft:marker,tag=bs.regarde] run function {NS}:c/at/regard_tick",
    f"execute if score #ph bs.c matches 2.. if score #tk bs.ev matches 0 run function {NS}:c/nuit"])
fn("c/nuit", [
    "execute at @e[type=minecraft:marker,tag=bs.cit] run particle minecraft:dust{color:[1,0.6,0.1],scale:1.2} ~ ~0.3 ~ 3 0 3 0 14",
    "scoreboard players add #nuit bs.c 1", "execute if score #nuit bs.c matches ..2 run return 0", "scoreboard players set #nuit bs.c 0",
    f"execute as @a[tag=bs.joue] at @s unless entity @e[type=minecraft:marker,tag=bs.cit,distance=..6] run function {NS}:c/ronge"])
fn("c/ronge", [blesse(1), barre("@s", "La nuit te ronge : rapproche-toi d'une citrouille !", "dark_red"),
               "particle minecraft:dust{color:[0.1,0,0],scale:1} ~ ~1 ~ 0.3 0.5 0.3 0 8"])

# ------------------------------------------------------------------------------------------------ sbires (corbeaux, livres)
fn("min/tick", [
    f"execute as @e[tag=bs.min] run function {NS}:min/un",
    f"execute if score #m4 bs.ev matches 0 run function {NS}:min/battre",
    f"execute as @e[type=minecraft:item_display,tag=bs.mind] unless predicate {NS}:monte run kill @s"])
fn("min/un", [
    "scoreboard players add @s bs.k 1",
    f"execute if entity @s[tag=!bs.frag] if score @s bs.k matches 600.. run return run function {NS}:min/fin",
    "execute if entity @s[tag=bs.frag] if score @s bs.k matches 400.. run return run function boss:min/fin",
    "data modify storage boss:t r set from entity @s Rotation[0]",
    "execute on passengers run data modify entity @s Rotation[0] set from storage boss:t r"])
fn("min/fin", ["execute at @s run particle minecraft:large_smoke ~ ~ ~ 0.2 0.2 0.2 0.02 8", "execute on passengers run kill @s", "kill @s"])
fn("min/battre", [
    "scoreboard players add #aile bs.ev 1", "execute if score #aile bs.ev matches 2.. run scoreboard players set #aile bs.ev 0",
    'execute if score #aile bs.ev matches 1 as @e[type=minecraft:item_display,tag=bs.vol] run data modify entity @s item.components."minecraft:item_model" set value "boss:oiseau_b_racine"',
    'execute if score #aile bs.ev matches 0 as @e[type=minecraft:item_display,tag=bs.vol] run data modify entity @s item.components."minecraft:item_model" set value "boss:oiseau_a_racine"',
    'execute if score #aile bs.ev matches 1 as @e[type=minecraft:item_display,tag=bs.livd] run data modify entity @s item.components."minecraft:item_model" set value "boss:livre_b_racine"',
    'execute if score #aile bs.ev matches 0 as @e[type=minecraft:item_display,tag=bs.livd] run data modify entity @s item.components."minecraft:item_model" set value "boss:livre_a_racine"'])

# =============================================================================================== recompenses
CAPE = ('minecraft:elytra[minecraft:item_model="boss:cape_plumes",'
        'minecraft:equippable={slot:"chest",asset_id:"boss:cape_plumes",equip_sound:"minecraft:item.armor.equip_elytra",damage_on_hurt:false},'
        f'minecraft:custom_name={js({"text": "Cape de plumes noires", "color": "dark_purple", "italic": False})},'
        f'minecraft:lore=[{js({"text": "Arrachée au Corbeau-Épouvantail.", "color": "gray", "italic": False})},'
        f'{js({"text": "Lâche des plumes noires en vol.", "color": "dark_gray", "italic": True})}],'
        'minecraft:unbreakable={},minecraft:rarity="epic",minecraft:custom_data={bs_cape:1b}]')
# 26/11/2026 : plus aucune arme ni armure en recompense (regle du serveur) : le Grimoire laisse un familier cosmetique
FAMILIER = ('minecraft:paper[minecraft:item_model="boss:grimoire_encre_racine",minecraft:max_stack_size=1,'
            f'minecraft:custom_name={js({"text": "Grimoire familier", "color": "light_purple", "italic": False})},'
            f'minecraft:lore=[{js({"text": "Arraché au Grimoire Vivant.", "color": "gray", "italic": False})},'
            f'{js({"text": "Dans la main secondaire, des runes tournent autour de toi.", "color": "dark_gray", "italic": True})}],'
            'minecraft:rarity="epic",minecraft:enchantment_glint_override=true,minecraft:custom_data={bs_familier:1b}]')
fn("recompense/donner", [
    "execute if score @s c.ecus matches -2147483648.. run scoreboard players add @s c.ecus 15000",
    "execute unless score @s m.afk matches 240.. if score @s m.c_bal matches -2147483648.. run scoreboard players add @s m.c_bal 600",
    "execute if score @s m.ecl matches -2147483648.. run scoreboard players add @s m.ecl 3",
    "xp add @s 500 points",
    f"execute if score #boss bs.ev matches 1 run function {NS}:recompense/grimoire",
    f"execute if score #boss bs.ev matches 2 run function {NS}:recompense/corbeau",
    dire("@s", ("Récompense : ", "gold"), ("15 000 Écus, 600 XP Chasseur, 3 éclats de boss, 500 points d'XP.", "yellow"))])
fn("recompense/grimoire", [
    "scoreboard players add @s bs.v1 1",
    f"execute if score @s bs.v1 matches 1 run give @s {FAMILIER} 1",
    f"execute if score @s bs.v1 matches 1 run {dire('@a', {'selector': '@s', 'color': 'white'}, (' arrache le ', 'gray'), {'text': 'Grimoire familier', 'color': 'light_purple', 'bold': True}, (' au Grimoire Vivant !', 'gray'))}",
    "execute if score @s bs.v1 matches 2.. run give @s minecraft:diamond 6"])
fn("recompense/corbeau", [
    "scoreboard players add @s bs.v2 1",
    f"execute if score @s bs.v2 matches 1 run give @s {CAPE} 1",
    f"execute if score @s bs.v2 matches 1 run {dire('@a', {'selector': '@s', 'color': 'white'}, (' arrache la ', 'gray'), {'text': 'Cape de plumes noires', 'color': 'dark_purple', 'bold': True}, (' au Corbeau-Épouvantail !', 'gray'))}",
    "execute if score @s bs.v2 matches 2.. run give @s minecraft:diamond 6"])
# la cape lache des plumes en vol
fn("cape/tick", [
    f"execute as @a[predicate={NS}:plane] if items entity @s armor.chest minecraft:elytra[minecraft:custom_data~{{bs_cape:1b}}] at @s run function {NS}:cape/plumes",
    f"execute as @a if items entity @s weapon.offhand minecraft:paper[minecraft:custom_data~{{bs_familier:1b}}] at @s run function {NS}:cape/runes"])
fn("cape/runes", ["particle minecraft:dust{color:[0.7,0.4,1.0],scale:0.7} ~ ~1.1 ~ 0.7 0.5 0.7 0 2",
                  "particle minecraft:enchant ~ ~1.6 ~ 0.4 0.3 0.4 0.6 2"])
fn("cape/plumes", ["particle minecraft:dust{color:[0.06,0.06,0.09],scale:1.4} ^ ^0.4 ^-0.9 0.35 0.15 0.35 0 3",
                   "particle minecraft:white_ash ^ ^0.4 ^-1.2 0.3 0.2 0.3 0 2"])

# =============================================================================================== administration
fn("forcer", [f"execute unless score #etat bs.ev matches 0 run return run {dire('@s', ('Un événement de boss est déjà en cours.', 'gray'))}",
              "scoreboard players set #t bs.ev 1", dire("@s", ("Un boss au hasard se réveille dans une seconde.", "gray"))])
for k, b in B.items():
    fn(f"forcer_{b['id']}", [f"execute unless score #etat bs.ev matches 0 run return run {dire('@s', ('Un événement de boss est déjà en cours.', 'gray'))}",
                             f"scoreboard players set #force bs.ev {k}", "scoreboard players set #t bs.ev 1",
                             dire("@s", (f"{b['nom']} se réveille dans une seconde.", "gray"))])
    # test : preavis de 8 s, l'admin est inscrit d'office
    fn(f"test_{b['id']}", [f"execute unless score #etat bs.ev matches 0 run return run {dire('@s', ('Un événement de boss est déjà en cours.', 'gray'))}",
                           f"scoreboard players set #boss bs.ev {k}", "scoreboard players set #pvmax bs.ev 8",
                           f"function {NS}:ev/ouvrir", "scoreboard players operation @s bs.ins = #eid bs.ev",
                           dire("@s", ("Test : tu es inscrit, départ dans 8 s.", "gray"))])
fn("annuler", [f"execute if score #etat bs.ev matches 0 run return run {dire('@s', ('Aucun événement de boss en cours.', 'gray'))}",
               dire("@a", ("Un administrateur a annulé l'événement de boss.", "gray")), f"function {NS}:ev/cloture"])
fn("arret", ["scoreboard players set #on bs.ev 0", dire("@s", ("Événements de boss automatiques coupés.", "gray"))])
fn("marche", ["scoreboard players set #on bs.ev 1", dire("@s", ("Événements de boss automatiques relancés.", "gray"))])
fn("intervalle", ["$scoreboard players set #min bs.ev $(min)", "$scoreboard players set #max bs.ev $(max)", f"function {NS}:ev/prochain",
                  dire("@s", ("Nouvel intervalle enregistré, minuteur relancé.", "gray"))])
fn("prochain", ["scoreboard players operation #mn bs.tmp = #t bs.ev", "scoreboard players operation #mn bs.tmp /= #60 bs.tmp",
                dire("@s", ("Prochain boss dans ", "gray"), {"score": {"name": "#mn", "objective": "bs.tmp"}, "color": "yellow"},
                     (" min de jeu (avec au moins un joueur connecté).", "gray"))])
fn("desinstaller", [f"execute if score #etat bs.ev matches 1.. run function {NS}:ev/cloture",
                    "kill @e[tag=bs.e]", "bossbar remove boss:combat",
                    "execute in boss:grimoire run forceload remove all", "execute in boss:corbeau run forceload remove all",
                    *[f"scoreboard objectives remove {o}" for o in OBJ + ["bs.rejoindre", "bs.pv", "bs.mort"]],
                    'tellraw @s {"text":"Pack Boss retiré. Désactive-le avec /datapack disable.","color":"gray"}'])

# =============================================================================================== resource pack (complements)
def ecrire_rp(chemin, obj):
    import json
    p = os.path.join(RP, *chemin.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, separators=(",", ":"))


ecrire_rp("items/vide.json", {"model": {"type": "minecraft:empty"}})
# Grimoire familier tenu en main : positions d'affichage
import json as _json
_m = os.path.join(RP, "models", "item", "boss", "grimoire_encre_racine.json")
_mod = _json.load(open(_m, encoding="utf-8"))
_mod["display"] = {"thirdperson_righthand": {"rotation": [70, 0, 0], "translation": [0, 3, 1], "scale": [1.1, 1.1, 1.1]},
                   "thirdperson_lefthand": {"rotation": [70, 0, 0], "translation": [0, 3, 1], "scale": [1.1, 1.1, 1.1]},
                   "firstperson_righthand": {"rotation": [40, -20, 10], "translation": [1, 4, 0], "scale": [1, 1, 1]},
                   "firstperson_lefthand": {"rotation": [40, 20, -10], "translation": [1, 4, 0], "scale": [1, 1, 1]},
                   "gui": {"rotation": [40, 200, 0], "translation": [0, 1, 0], "scale": [1.3, 1.3, 1.3]},
                   "ground": {"rotation": [0, 0, 0], "translation": [0, 2, 0], "scale": [0.8, 0.8, 0.8]},
                   "fixed": {"rotation": [90, 0, 0], "scale": [1.3, 1.3, 1.3]}}
_json.dump(_mod, open(_m, "w", encoding="utf-8"), separators=(",", ":"))
# Cape de plumes noires : icone + ailes (patron d'elytres 64x32)
import random as _rd
from png import Image as _Img
import peintres as _pt
ic = _Img(16, 16)
for y in range(1, 15):
    larg = 3 + y // 2
    for x in range(8 - larg // 2 - 2, 8 + larg // 2 + 2):
        if 0 <= x < 16 and (y < 13 or (x + y) % 2):
            v = _rd.Random(x * 31 + y).random()
            ic.set(x, y, _pt.hexa("#0e0e14" if v < .5 else "#1c1c2c" if v < .85 else "#3b3f6a"))
for y in range(2, 13, 3):
    ic.set(7, y, _pt.hexa("#5a1a1a"))
os.makedirs(os.path.join(RP, "textures", "item"), exist_ok=True)
ic.save(os.path.join(RP, "textures", "item", "cape_plumes.png"))
ecrire_rp("models/item/cape_plumes.json", {"parent": "minecraft:item/generated", "textures": {"layer0": "boss:item/cape_plumes"}})
ecrire_rp("items/cape_plumes.json", {"model": {"type": "minecraft:model", "model": "boss:item/cape_plumes"}})
ailes = _Img(64, 32)
_pt.plumes(ailes, 22, 0, 24, 22, _rd.Random(5), {})
_pt.haillons(ailes, 22, 16, 24, 6, _rd.Random(6), {"pal": ["#0e0e14", "#181824", "#232338"], "trou": True})
for y in range(0, 22, 4):
    for x in range(22, 46, 5):
        ailes.set(x, y, _pt.hexa("#5a1a1a"))
os.makedirs(os.path.join(RP, "textures", "entity", "equipment", "wings"), exist_ok=True)
ailes.save(os.path.join(RP, "textures", "entity", "equipment", "wings", "cape_plumes.png"))
ecrire_rp("equipment/cape_plumes.json", {"layers": {"wings": [{"texture": "boss:cape_plumes"}]}})

# =============================================================================================== zip
ZIP = os.path.join(ICI, "..", "boss.zip")
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, _, fs in os.walk(ROOT):
        for f in sorted(fs):
            full = os.path.join(dp, f)
            zi = zipfile.ZipInfo(os.path.relpath(full, ROOT).replace(os.sep, "/"), date_time=(2026, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, open(full, "rb").read())
nf = sum(len(f) for _, _, f in os.walk(ROOT))
nr = sum(len(f) for _, _, f in os.walk(os.path.join(ICI, "..", "build", "boss_rp")))
print(f"datapack boss : {nf} fichiers -> boss.zip ; resource pack : {nr} fichiers dans build/boss_rp")

"""Génère le datapack Compagnons : build/compagnons_datapack/ + compagnons.zip (convention de l'usine).

Un compagnon à la fois par joueur, choisi parmi 6 (loup, chat, perroquet, bonhomme de neige, allay, golem de fer).
  - débloqués par les niveaux de Métiers (un métier par compagnon, le prestige compte comme le niveau 100) ;
  - niveaux propres (1 à 30) : XP par ennemi qu'il tue, par ennemi que tu tues avec lui, et avec le temps passé dehors ;
  - stats qui montent à chaque niveau, 4 capacités par compagnon (niveaux 5, 10, 20, 30), apparences à débloquer ;
  - jamais perdu : s'il tombe à court de vie il est mis K.O. (retour 60 s plus tard), il suit d'une dimension à l'autre.
Menus : touche G, Compagnons (déclencheur « compagnons »), au style des autres packs (icônes du jeu, 3 colonnes, bandeau).
Mob vanilla réel pour chaque compagnon : loup, chat et perroquet sont apprivoisés (IA de suivi du jeu), l'allay suit
son joueur aimé, le bonhomme de neige et le golem sont ramenés près du joueur quand ils s'éloignent.
"""
import json, os, shutil, zipfile

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(ICI, "..", "build", "compagnons_datapack")
NS = "compagnons"
F = f"data/{NS}/function/"
if os.path.exists(ROOT):
    shutil.rmtree(ROOT)
GLY = json.load(open(os.path.join(ICI, "..", "..", "metiers", "sources", "glyphes.json"), encoding="utf-8"))


def w(path, txt):
    if isinstance(txt, list):
        txt = "\n".join(txt)
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    lignes = [l.strip() for l in txt.strip().splitlines()]
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(l for l in lignes if l) + "\n")


def wj(path, obj):
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


S = "scoreboard players"
PREFIX = '{"text":"[Compagnons] ","color":"#E0A040"}'
def tr(txt, col="gray", qui="@s"):
    return f'tellraw {qui} [{PREFIX},{{"text":"{txt}","color":"{col}"}}]'
def IC(i):
    return f'{{object:"atlas",atlas:"minecraft:items",sprite:"minecraft:item/{i}"}}'
BAN = ('{type:"minecraft:plain_message",width:310,contents:[{text:""},{text:"' + chr(0xE020 + 13) +
       '",font:"commerce:recette",color:"white",shadow_color:0},{text:"\\n\\n"}]}')

# =====================================================================
# LES COMPAGNONS
# =====================================================================
# id, clé, nom, couleur, entité, icône, (métier, niveau, nom du métier), suit tout seul (IA du jeu), combat
TYPES = [
    (1, "loup", "Loup", "#C8C8C8", "wolf", "bone", ("c", 10, "Chasseur"), True, True),
    (2, "chat", "Chat", "#E0A040", "cat", "cod", ("f", 10, "Fermier"), True, False),
    (3, "perroquet", "Perroquet", "#40C860", "parrot", "feather", ("x", 15, "Explorateur"), True, False),
    (4, "neige", "Bonhomme de neige", "#D8F0FF", "snow_golem", "snowball", ("p", 20, "Pêcheur"), False, True),
    (5, "allay", "Allay", "#60C8FF", "allay", "amethyst_shard", ("n", 25, "Enchanteur"), True, False),
    (6, "golem", "Golem de fer", "#D8CFC0", "iron_golem", "iron_ingot", ("m", 30, "Mineur"), False, True),
    # montures volantes : un ghast joyeux harnaché (vol contrôlé par le jeu) ; dragon et wither = ghast invisible
    # (harnais sans rendu) qui porte le joueur, et le vrai boss figé (NoAI, invulnérable, réduit) collé dessus à chaque tick
    (7, "ghast", "Ghast joyeux", "#F4F4F4", "happy_ghast", "ghast_tear", ("x", 40, "Explorateur"), False, False),
    (8, "dragon", "Dragon de l’Ender", "#C060FF", "happy_ghast", "dragon_breath", ("c", 50, "Chasseur"), False, True),
    (9, "wither", "Wither", "#8A8A8A", "happy_ghast", "nether_star", ("c", 70, "Chasseur"), False, True),
]
MONTURES = (7, 8, 9)
# boss figé : (entité, taille, décalage de rotation, décalage vertical, tag)
VISUEL = {8: ("ender_dragon", 0.45, 180, -0.6, "cp.vdragon"), 9: ("wither", 0.8, 0, -0.4, "cp.vwither")}
OEUF = {7: "happy_ghast", 8: "ender_dragon", 9: "wither"}
# condition de boss en plus du niveau : (texte, lignes qui remettent #deb à 0 si elle manque)
BOSS = {8: ("après avoir vaincu l’Ender Dragon",
            ["execute if score #deb cp.t matches 1 unless entity @s[advancements={minecraft:end/kill_dragon=true}] run scoreboard players set #deb cp.t 0"]),
        9: ("après avoir affronté le Wither",
            ["scoreboard players set #bw cp.t 0",
             "execute if entity @s[advancements={minecraft:nether/summon_wither=true}] run scoreboard players set #bw cp.t 1",
             "execute if score @s cp.kwi matches 1.. run scoreboard players set #bw cp.t 1",
             "execute if score #bw cp.t matches 0 run scoreboard players set #deb cp.t 0"])}
T = {t[0]: t for t in TYPES}
DE = lambda m: ("d’" if m[0] in "AEÉIOUaeéiou" else "de ") + m
LE = lambda n: ("L’" if n[0] in "AEÉIOU" else "Le ") + n
LMAX = 30
def COND(k):
    """Texte de la condition de déblocage."""
    j, n, jn = T[k][6]
    return f"niveau {n} {DE(jn)}" + (" (ou Bâtisseur 30)" if k == 6 else "") + (f", {BOSS[k][0]}" if k in BOSS else "")

# stats au niveau L : (PV, dégâts, vitesse, armure, taille)
def stats(k, L):
    return {1: (20 + 2 * L, 4 + 0.25 * L, 0.30 + 0.002 * L, (L // 5) * 2, 1 + 0.007 * L),
            2: (10 + L, 3 + 0.1 * L, 0.30 + 0.002 * L, L // 6, 1.0),
            3: (6 + L, 0, 0.20 + 0.002 * L, L // 6, 1.0),
            4: (4 + 2 * L, 0, 0.20 + 0.003 * L, L // 5, 1 + 0.01 * L),
            5: (20 + L, 0, 0.10 + 0.002 * L, L // 6, 1.0),
            6: (60 + 4 * L, 10 + 0.5 * L, 0.25 + 0.002 * L, L // 3, 0.55 + 0.015 * L),
            7: (20 + 2 * L, 0, 0.20, L // 5, 0.7),
            8: (40 + 4 * L, 0, 0.20, L // 3, 0.55),
            9: (60 + 5 * L, 0, 0.20, L // 3, 0.55)}[k]
# vitesse de vol (attribut flying_speed ; un ghast joyeux du jeu vole à 0,05)
VOL = {5: lambda L: 0.1 + 0.003 * L, 7: lambda L: 0.05 + 0.0015 * L, 8: lambda L: 0.07 + 0.002 * L, 9: lambda L: 0.065 + 0.002 * L}

# capacités : (niveau, nom, effet)
CAPS = {
    1: [(5, "Croc paralysant", "Sa proie est ralentie."), (10, "Instinct de meute", "Vitesse I pour toi quand il est près de toi."),
        (20, "Saignement", "Sa proie se vide de sa vie (Wither)."),
        (30, "Alpha", "Sous 4 cœurs, deux loups de renfort arrivent pour 30 s (toutes les 2 min).")],
    2: [(5, "Ronronnement", "Régénération toutes les 10 s quand tu es blessé."), (10, "Vision féline", "Vision nocturne près de lui."),
        (20, "Neuf vies", "Sous 4 cœurs : absorption et régénération II (toutes les 2 min)."),
        (30, "Porte-bonheur", "Chance II en permanence (meilleur butin).")],
    3: [(5, "Sentinelle", "Les monstres à 16 blocs de toi deviennent lumineux."), (10, "Plume", "Chute lente quand tu tombes de haut."),
        (20, "Alerte", "Il te prévient quand un creeper approche."), (30, "Vent arrière", "Vitesse I et saut amélioré pour toi.")],
    4: [(5, "Givre", "Les monstres à 6 blocs sont ralentis."), (10, "Cœur de glace", "Il se régénère tout seul."),
        (20, "Blizzard", "Toutes les 10 s : monstres à 8 blocs gelés et blessés."),
        (30, "Hiver éternel", "Blizzard toutes les 5 s, plus large et plus fort.")],
    5: [(5, "Aimant", "Les objets à 10 blocs viennent jusqu’à toi."), (10, "Chant apaisant", "Régénération toutes les 10 s près de lui."),
        (20, "Fortune", "Chance I en permanence."),
        (30, "Ange gardien", "Sous 3 cœurs : absorption, régénération et résistance (toutes les 5 min).")],
    6: [(5, "Rempart", "Résistance I pour toi près de lui."), (10, "Frappe sismique", "Toutes les 8 s, les monstres collés à lui sont projetés."),
        (20, "Peau de fer", "Il encaisse beaucoup moins de dégâts."), (30, "Titan", "Il grandit encore et te donne de l’absorption chaque minute.")],
    7: [(5, "Nuage protecteur", "Résistance I quand tu le montes."), (10, "Rafale", "Il vole 25 % plus vite."),
        (20, "Vol de nuit", "Vision nocturne quand tu le montes."), (30, "Nuée", "Régénération et résistance au feu quand tu le montes.")],
    8: [(5, "Souffle", "Toutes les 3 s, il souffle sur les monstres devant lui."), (10, "Écailles", "Résistance I quand tu le montes."),
        (20, "Envergure", "Il vole 30 % plus vite."), (30, "Colère du dragon", "Souffle plus large et bien plus fort.")],
    9: [(5, "Crânes", "Toutes les 3 s, il frappe le monstre le plus proche (Wither)."), (10, "Armure de Wither", "Résistance I quand tu le montes."),
        (20, "Aura noire", "Les monstres à 6 blocs se flétrissent."), (30, "Explosion", "Toutes les 20 s, une onde pulvérise les monstres à 6 blocs (sans casser de blocs).")],
}
BASE = {1: "Te suit, attaque ce que tu frappes et ce qui t’attaque. Mode chasse : il va chercher les monstres tout seul.",
        2: "Te suit, fait fuir creepers et phantoms, rapporte parfois un cadeau le matin.",
        3: "Te suit ou se pose sur ton épaule, imite le cri des monstres proches.",
        4: "Bombarde les monstres de boules de neige. Ne fond plus, même dans le désert.",
        5: "Te suit en volant et ramasse les objets que tu lui donnes en main.",
        6: "Tank : frappe fort et encaisse. Ramené près de toi s’il s’éloigne.",
        7: "Monture volante : clic droit pour monter, regarde où aller et avance. Jusqu’à 4 passagers.",
        8: "Monture volante : clic droit pour monter, regarde où aller et avance. Pas dans l’End (le combat du dragon s’y joue).",
        9: "Monture volante : clic droit pour monter, regarde où aller et avance. Sa barre de boss porte son nom."}

# apparences : (valeur, nom), la n-ième se débloque au niveau 1 + PAS * n
VARIANTES = {
    1: ("variant", [("minecraft:pale", "Pâle"), ("minecraft:woods", "Des bois"), ("minecraft:ashen", "Cendré"), ("minecraft:black", "Noir"),
                    ("minecraft:chestnut", "Châtaigne"), ("minecraft:rusty", "Roux"), ("minecraft:spotted", "Tacheté"),
                    ("minecraft:striped", "Rayé"), ("minecraft:snowy", "Des neiges")], 3),
    2: ("variant", [("minecraft:tabby", "Tigré"), ("minecraft:black", "Noir"), ("minecraft:red", "Roux"), ("minecraft:siamese", "Siamois"),
                    ("minecraft:british_shorthair", "British"), ("minecraft:calico", "Calico"), ("minecraft:persian", "Persan"),
                    ("minecraft:ragdoll", "Ragdoll"), ("minecraft:white", "Blanc"), ("minecraft:jellie", "Jellie"), ("minecraft:all_black", "Tout noir")], 2),
    3: ("Variant", [(0, "Rouge"), (1, "Bleu"), (2, "Vert"), (3, "Cyan"), (4, "Gris")], 5),
    # ghast joyeux : couleur du harnais
    7: ("harnais", [("white", "Harnais blanc"), ("light_blue", "Harnais ciel"), ("yellow", "Harnais jaune"), ("lime", "Harnais vert"),
                    ("pink", "Harnais rose"), ("orange", "Harnais orange"), ("purple", "Harnais violet"), ("red", "Harnais rouge"),
                    ("black", "Harnais noir")], 3),
}

HOSTILES = ["zombie", "husk", "drowned", "zombie_villager", "skeleton", "stray", "bogged", "wither_skeleton", "spider", "cave_spider",
            "creeper", "witch", "pillager", "vindicator", "evoker", "ravager", "vex", "phantom", "slime", "magma_cube", "blaze", "ghast",
            "piglin_brute", "hoglin", "zoglin", "silverfish", "endermite", "guardian", "elder_guardian", "shulker", "breeze"]
wj(f"data/{NS}/tags/entity_type/hostiles.json", {"values": [f"minecraft:{h}" for h in HOSTILES]})
wj(f"data/{NS}/tags/entity_type/chasse.json", {"values": [f"minecraft:{h}" for h in HOSTILES if h != "creeper"]})

# =====================================================================
# CHARGEMENT ET BOUCLES
# =====================================================================
OBJ = ["cp.id", "cp.ser", "cp.out", "cp.cd", "cp.cda", "cp.mode", "cp.ag", "cp.own", "cp.typ", "cp.hp", "cp.hpm", "cp.min",
       "cp.vie", "cp.t", "cp.tk", "cp.ok", "cp.mt", "cp.att"] + [f"cp.{a}{k}" for k in T for a in ("l", "x", "v", "r", "f", "m")]
w(F + "load.mcfunction", [f"scoreboard objectives add {o} dummy" for o in OBJ] + [
    "scoreboard objectives add compagnons trigger",
    "scoreboard objectives add cp.mk minecraft.custom:minecraft.mob_kills",
    f"{S} add #next cp.t 0", f"{S} set #6 cp.t 6", f"{S} set #20 cp.t 20", f"{S} set #100 cp.t 100",
    f"execute unless data storage {NS}:noms J run data modify storage {NS}:noms J set value []",
    f"schedule function {NS}:seconde 1s replace"])
wj("data/minecraft/tags/function/load.json", {"values": [f"{NS}:load"]})
wj("data/minecraft/tags/function/tick.json", {"values": [f"{NS}:tick"]})
# toutes les 5 ticks : coups fatals (crédit au compagnon) ; le déclencheur, tout de suite
w(F + "tick.mcfunction", [
    f"execute as @a[scores={{compagnons=1..}}] at @s run function {NS}:menu/entree",
    f"{S} add #t5 cp.t 1", f"execute if score #t5 cp.t matches 5.. run {S} set #t5 cp.t 0",
    f"execute if score #t5 cp.t matches 0 as @e[tag=cp.c] at @s as @e[type=#{NS}:hostiles,distance=..24,tag=!cp.mort] if data entity @s {{Health:0.0f}} run function {NS}:xp/mort",
    f"execute as @e[tag=cp.porteur] at @s run function {NS}:c/visuel",
    f"execute as @e[tag=cp.c] at @s run function {NS}:c/suivre"])
# 25/11/2026 : suivi réel pour tous les compagnons (v4.1 : au pas, voir c/suivre_pas) (avant, golems et montures ne revenaient que par téléportation au-delà
# de 8 à 24 blocs). Le compagnon vise un point 3,5 blocs DERRIÈRE son joueur : il reste entre 2,5 et 6 blocs, hors du
# champ de vision, donc pas dans la pioche. Poussée par Motion (collisions et gravité respectées, pas de traversée de mur),
# petit saut devant une marche. Pas de suivi s'il est monté, en mode « reste », ou en plein combat près du joueur.
# 25/11/2026 v4.2 : le compagnon attaque ce que son joueur frappe. Au coup porté (succès player_hurt_entity), on
# retrouve la victime (HurtTime 10 et ce joueur comme attaquant), puis le loup, le bonhomme de neige et le golem de ce
# joueur reçoivent un coup symbolique « de la part » de la victime : leur riposte du jeu (HurtByTarget) les lance dessus.
wj(f"data/{NS}/advancement/frappe.json", {"criteria": {"coup": {"trigger": "minecraft:player_hurt_entity"}},
                                          "rewards": {"function": f"{NS}:c/frappe"}})
w(F + "c/frappe.mcfunction", [
    f"advancement revoke @s only {NS}:frappe",
    "tag @s add cp.frappeur_j",
    f"execute as @e[type=!minecraft:player,tag=!cp.c,tag=!cp.vis,distance=..8,nbt={{HurtTime:10s}}] run function {NS}:c/frappe_victime",
    f"{S} operation #o cp.t = @s cp.id",
    f"execute if entity @e[tag=cp.proie] as @e[tag=cp.c,type=#{NS}:combattants] if score @s cp.own = #o cp.t run damage @s 0.01 minecraft:mob_attack by @e[tag=cp.proie,limit=1]",
    "tag @e[tag=cp.proie] remove cp.proie",
    "tag @s remove cp.frappeur_j"])
w(F + "c/frappe_victime.mcfunction", [
    "tag @s add cp.teste",
    "execute on attacker if entity @s[tag=cp.frappeur_j] run tag @e[tag=cp.teste,limit=1] add cp.proie",
    "tag @s remove cp.teste"])
wj(f"data/{NS}/tags/entity_type/combattants.json",
   {"values": ["minecraft:wolf", "minecraft:snow_golem", "minecraft:iron_golem"]})
w(F + "c/suivre.mcfunction", [
    f"{S} operation #o cp.t = @s cp.own",
    "execute as @a if score @s cp.id = #o cp.t run tag @s add cp.guide",
    f"execute if entity @s[tag=!cp.lent,tag=!cp.vol] run return run tag @a remove cp.guide",
    f"execute if entity @a[tag=cp.guide,scores={{cp.mode=0}}] run function {NS}:c/suivre_pas",
    "tag @a remove cp.guide"])
w(F + "c/rejoindre_pieds.mcfunction", [
    "particle minecraft:poof ~ ~0.5 ~ 0.3 0.4 0.3 0.02 8",
    "tp @s @a[tag=cp.guide,limit=1]", "scoreboard players set @s cp.att 0", "tag @s remove cp.marche",
    "execute at @s run particle minecraft:poof ~ ~0.5 ~ 0.3 0.4 0.3 0.02 8"])
w(F + "c/suivre_pas.mcfunction", [
    "execute on passengers if entity @s[type=minecraft:player] run return 0",
    f"execute if entity @e[type=#{NS}:hostiles,distance=..8] if entity @a[tag=cp.guide,distance=..14] run return 0",
    # 25/11/2026 v4.1 : marche au pas, sans tourner autour du joueur. Il repart au-delà de 5 blocs et s'arrête à
    # 3 blocs (tag cp.marche), à vitesse de marche (0,12 bloc/tick, 0,15 pour les volants), en visant le joueur.
    "execute unless entity @a[tag=cp.guide,distance=..5] run tag @s add cp.marche",
    "execute if entity @a[tag=cp.guide,distance=..3] run tag @s remove cp.marche",
    "execute if entity @s[tag=!cp.marche] run return run scoreboard players set @s cp.att 0",
    # 4.2 : coincé (faille, mur, eau) ou distancé : au bout de 5 s de marche sans t'avoir rejoint, il apparaît à tes pieds
    "scoreboard players add @s cp.att 1",
    f"execute if score @s cp.att matches 100.. run return run function {NS}:c/rejoindre_pieds",
    "execute if entity @s[tag=!cp.vol,type=!minecraft:allay] facing entity @a[tag=cp.guide,limit=1] feet rotated ~ 0 positioned 0.0 0.0 0.0 run summon minecraft:marker ^ ^ ^0.12 {Tags:[\"cp.vec\"]}",
    "execute if entity @s[tag=cp.vol] positioned as @a[tag=cp.guide,limit=1] positioned ~ ~2 ~ run summon minecraft:marker ~ ~ ~ {Tags:[\"cp.cible\"]}",
    "execute if entity @s[type=minecraft:allay] positioned as @a[tag=cp.guide,limit=1] positioned ~ ~1.5 ~ run summon minecraft:marker ~ ~ ~ {Tags:[\"cp.cible\"]}",
    "execute if entity @e[type=minecraft:marker,tag=cp.cible,distance=..30] facing entity @e[type=minecraft:marker,tag=cp.cible,limit=1] feet positioned 0.0 0.0 0.0 run summon minecraft:marker ^ ^ ^0.15 {Tags:[\"cp.vec\"]}",
    "data modify entity @s Motion[0] set from entity @e[type=minecraft:marker,tag=cp.vec,limit=1] Pos[0]",
    "data modify entity @s Motion[2] set from entity @e[type=minecraft:marker,tag=cp.vec,limit=1] Pos[2]",
    "execute if entity @s[tag=cp.vol] run data modify entity @s Motion[1] set from entity @e[type=minecraft:marker,tag=cp.vec,limit=1] Pos[1]",
    "execute if entity @s[type=minecraft:allay] run data modify entity @s Motion[1] set from entity @e[type=minecraft:marker,tag=cp.vec,limit=1] Pos[1]",
    "execute if entity @s[tag=!cp.vol,type=!minecraft:allay] unless block ~ ~-0.2 ~ #minecraft:replaceable facing entity @a[tag=cp.guide,limit=1] feet rotated ~ 0 unless block ^ ^0.3 ^0.9 #minecraft:replaceable if block ^ ^1.3 ^0.9 #minecraft:replaceable if block ^ ^2.3 ^0.9 #minecraft:replaceable run data modify entity @s Motion[1] set value 0.42d",
    "rotate @s facing entity @a[tag=cp.guide,limit=1] feet",
    "kill @e[type=minecraft:marker,tag=cp.cible]", "kill @e[type=minecraft:marker,tag=cp.vec]"])
# le boss figé suit son porteur (ghast invisible) à chaque tick, tourné comme lui (le dragon du jeu regarde à l'envers)
w(F + "c/visuel.mcfunction", [f"{S} operation #o cp.t = @s cp.own", f"{S} operation #s cp.t = @s cp.ser"] +
  [f"execute as @e[tag={v[4]}] if score @s cp.own = #o cp.t if score @s cp.ser = #s cp.t run tp @s ~ ~{v[3]} ~ ~{v[2]} 0" for v in VISUEL.values()])
w(F + "c/vis_valide.mcfunction", [
    f"{S} operation #o cp.t = @s cp.own", f"{S} operation #s cp.t = @s cp.ser", f"{S} set #ok cp.t 0",
    f"execute as @e[tag=cp.porteur] if score @s cp.own = #o cp.t if score @s cp.ser = #s cp.t run {S} set #ok cp.t 1",
    "execute if score #ok cp.t matches 0 run tp @s ~ -1000 ~", "execute if score #ok cp.t matches 0 run kill @s"])
w(F + "seconde.mcfunction", [
    f"schedule function {NS}:seconde 1s replace", f"{S} add #s cp.tk 1",
    f"execute as @a at @s run function {NS}:joueur",
    f"execute as @e[tag=cp.c] run function {NS}:c/valide",
    f"execute as @e[tag=cp.vis] run function {NS}:c/vis_valide",
    f"execute as @e[tag=cp.renfort] run function {NS}:c/renfort"])

# =====================================================================
# JOUEUR (chaque seconde)
# =====================================================================
w(F + "id.mcfunction", [f"{S} add #next cp.t 1", f"{S} operation @s cp.id = #next cp.t",
                        f"execute store result storage {NS}:t id int 1 run {S} get @s cp.id",
                        f"function {NS}:noms/creer with storage {NS}:t"])
w(F + "noms/creer.mcfunction", f"$execute unless data storage {NS}:noms J[{{id:$(id)}}] run data modify storage {NS}:noms J append value {{id:$(id)}}")
J = [f"execute unless score @s cp.id matches 1.. run function {NS}:id", f"scoreboard players enable @s compagnons",
     f"{S} add @s cp.out 0", f"{S} add @s cp.mode 0", f"{S} add @s cp.ag 0", f"{S} add @s cp.min 0"] + \
    [f"execute unless score @s cp.l{k} matches 1.. run {S} set @s cp.l{k} 1" for k in T] + \
    [f"execute if score @s cp.cd matches 1.. run {S} remove @s cp.cd 1",
     f"execute if score @s cp.cda matches 1.. run {S} remove @s cp.cda 1",
     # XP : ennemis tués par le joueur pendant que son compagnon est dehors, temps passé ensemble
     f"execute if score @s cp.out matches 1.. if score @s cp.mk matches 1.. run function {NS}:xp/joueur_tue",
     f"{S} set @s cp.mk 0",
     f"execute if score @s cp.out matches 1.. run {S} add @s cp.min 1",
     f"execute if score @s cp.min matches 60.. run function {NS}:xp/minute",
     f"execute if score @s cp.out matches 1.. if score @s cp.cd matches ..0 run function {NS}:suivi"]
w(F + "joueur.mcfunction", J)
# le compagnon actuel du joueur (même propriétaire, même numéro d'invocation) reçoit le tag cp.cur
w(F + "marquer.mcfunction", [
    "tag @e[tag=cp.cur] remove cp.cur",
    f"{S} operation #o cp.t = @s cp.id", f"{S} operation #s cp.t = @s cp.ser",
    f"execute as @e[tag=cp.c] if score @s cp.own = #o cp.t if score @s cp.ser = #s cp.t run tag @s add cp.cur"])
w(F + "suivi.mcfunction", [
    f"function {NS}:marquer", "tag @s add cp.moi",
    # introuvable : resté dans une zone déchargée, ou mort d'un coup. Blessé avant : K.O. ; sinon il revient près du joueur
    f"{S} operation #h cp.t = @s cp.hpm", f"{S} operation #h cp.t /= #2 cp.t",
    f"execute unless entity @e[tag=cp.cur] if score @s cp.hp < #h cp.t run function {NS}:ko_perdu",
    f"execute unless entity @e[tag=cp.cur] if score @s cp.cd matches ..0 run function {NS}:invoquer/actuel",
    f"execute as @e[tag=cp.cur,limit=1] at @s run function {NS}:c/tour",
    "tag @s remove cp.moi"])
w(F + "ko_perdu.mcfunction", [f"{S} set @s cp.cd 60", f"{S} set @s cp.hp 99999",
                              tr("Ton compagnon est K.O. Il revient dans 60 secondes.", "red")])

# =====================================================================
# COMPAGNON (chaque seconde, exécuté par le compagnon, son joueur a le tag cp.moi)
# =====================================================================
TOUR = [f"execute store result score @s cp.hp run data get entity @s Health",
        f"execute store result score @s cp.hpm run attribute @s minecraft:max_health get",
        f"{S} operation @a[tag=cp.moi] cp.hp = @s cp.hp", f"{S} operation @a[tag=cp.moi] cp.hpm = @s cp.hpm",
        # K.O. sous 20 % de sa vie : il ne meurt jamais
        f"{S} operation #q cp.t = @s cp.hp", f"{S} operation #q cp.t *= #5 cp.t",
        f"execute if score #q cp.t <= @s cp.hpm run return run function {NS}:c/ko",
        # suivre : plus de 24 blocs (ou une autre dimension) : il revient près du joueur ; golem et bonhomme dès 8 blocs
        # monture : le joueur est-il dessus ? (alors pas de rappel), et personne d'autre ne la conduit
        f"{S} set #monte cp.t 0", f"execute on passengers if entity @s[tag=cp.moi] run {S} set #monte cp.t 1",
        # les amis peuvent monter derrière le propriétaire, pas prendre la monture sans lui
        "execute if entity @s[tag=cp.vol] if score #monte cp.t matches 0 on passengers if entity @s[type=minecraft:player,tag=!cp.moi] run ride @s dismount",
        # en descendant d'une monture en plein vol : chute lente
        "execute if entity @s[tag=cp.vol] if score #monte cp.t matches 0 as @a[tag=cp.moi,scores={cp.mt=1}] run effect give @s minecraft:slow_falling 8 0 true",
        f"{S} operation @a[tag=cp.moi] cp.mt = #monte cp.t",
        f"execute if score #monte cp.t matches 0 if entity @a[tag=cp.moi,scores={{cp.mode=0}}] unless entity @a[tag=cp.moi,distance=..24] run function {NS}:c/rejoindre",
        f"execute if score #monte cp.t matches 0 if entity @s[tag=cp.lent,tag=!cp.vol] if entity @a[tag=cp.moi,scores={{cp.mode=0}}] unless entity @a[tag=cp.moi,distance=..16] run function {NS}:c/rejoindre",
        f"execute if score #monte cp.t matches 0 if entity @s[tag=cp.vol] if entity @a[tag=cp.moi,scores={{cp.mode=0}}] unless entity @a[tag=cp.moi,distance=..14] run function {NS}:c/rejoindre",
        # le dragon ne vole pas dans l'End (le combat du dragon du jeu pourrait le prendre pour le vrai)
        f"execute if score @s cp.typ matches 8 if entity @a[tag=cp.moi,limit=1] as @a[tag=cp.moi] at @s if dimension minecraft:the_end run return run function {NS}:ranger_end",
        ]
for k in T:
    # niveau effectif des capacités : niveau + 2 par rang de Maîtrise
    w(F + f"c/niv_{k}.mcfunction", [f"{S} operation #L cp.t = @a[tag=cp.moi,limit=1] cp.l{k}",
                                    f"{S} operation #mm cp.t = @a[tag=cp.moi,limit=1] cp.m{k}", f"{S} operation #mm cp.t *= #2 cp.t",
                                    f"{S} operation #L cp.t += #mm cp.t"])
    TOUR.append(f"execute if score @s cp.typ matches {k} run function {NS}:c/niv_{k}")
    TOUR.append(f"execute if score @s cp.typ matches {k} run function {NS}:c/cap_{k}")
w(F + "c/tour.mcfunction", TOUR)
w(F + "ranger_end.mcfunction", [f"function {NS}:ranger_silence", tr("Le dragon refuse d’entrer dans l’End. Il t’attend dehors.", "light_purple")])
w(F + "c/rejoindre.mcfunction", [
    "particle minecraft:poof ~ ~0.5 ~ 0.3 0.4 0.3 0.02 8",
    "execute unless entity @s[tag=cp.vol] at @a[tag=cp.moi,limit=1] rotated ~ 0 run tp @s ^ ^ ^-3",
    "execute if entity @s[tag=cp.vol] at @a[tag=cp.moi,limit=1] rotated ~ 0 run tp @s ^ ^2 ^-5",
    "execute at @s run particle minecraft:poof ~ ~0.5 ~ 0.3 0.4 0.3 0.02 8"])
w(F + "c/ko.mcfunction", [
    "particle minecraft:cloud ~ ~0.6 ~ 0.3 0.4 0.3 0.05 20", "playsound minecraft:entity.player.hurt_sweet_berry_bush neutral @a[distance=..16] ~ ~ ~ 0.8 0.7",
    f"{S} set @a[tag=cp.moi] cp.cd 60", f"{S} set @a[tag=cp.moi] cp.hp 99999",
    "execute as @a[tag=cp.moi] run " + tr("Ton compagnon est K.O. Il se repose et revient dans 60 secondes.", "red"),
    f"{S} operation #o cp.t = @s cp.own", f"{S} operation #s cp.t = @s cp.ser",
    "execute as @e[tag=cp.vis] if score @s cp.own = #o cp.t if score @s cp.ser = #s cp.t run kill @s",
    "tp @s ~ -1000 ~", "kill @s"])
# compagnon sans joueur (déconnecté), ancien numéro d'invocation, ou compagnon rangé : il disparaît sans rien lâcher
w(F + "c/valide.mcfunction", [
    f"{S} operation #o cp.t = @s cp.own", f"{S} operation #s cp.t = @s cp.ser", f"{S} operation #y cp.t = @s cp.typ",
    f"{S} set #ok cp.t 0",
    f"execute as @a if score @s cp.id = #o cp.t if score @s cp.ser = #s cp.t if score @s cp.out = #y cp.t run {S} set #ok cp.t 1",
    "execute if score #ok cp.t matches 0 at @s run particle minecraft:poof ~ ~0.5 ~ 0.3 0.4 0.3 0.02 10",
    "execute if score #ok cp.t matches 0 run tp @s ~ -1000 ~", "execute if score #ok cp.t matches 0 run kill @s"])
w(F + "c/renfort.mcfunction", [f"{S} remove @s cp.vie 1", "execute if score @s cp.vie matches ..0 at @s run particle minecraft:poof ~ ~0.5 ~ 0.3 0.4 0.3 0.02 10",
                               "execute if score @s cp.vie matches ..0 run tp @s ~ -1000 ~", "execute if score @s cp.vie matches ..0 run kill @s"])

# --------------------------------------------------------------- capacités (#L = niveau, cp.moi = le joueur)
def L(k, n):
    return f"execute if score #L cp.t matches {n}.."
CAP = {}
CAP[1] = [  # loup
    f"{S} operation #L cp.t = @a[tag=cp.moi,limit=1] cp.l1",
    f"{L(1, 5)} on target run effect give @s minecraft:slowness 2 1",
    f"{L(1, 10)} run effect give @a[tag=cp.moi,distance=..16] minecraft:speed 2 0 true",
    f"{L(1, 20)} on target run effect give @s minecraft:wither 3 0",
    f"{L(1, 30)} if entity @a[tag=cp.moi,scores={{cp.hp=..0}}] run function {NS}:c/loup_alpha",
    # mode chasse : sans cible, il provoque le monstre le plus proche (hors creeper), qui l'attaque et se fait mordre
    f"{S} set #cible cp.t 0",
    f"execute if entity @a[tag=cp.moi,scores={{cp.ag=1}}] store success score #cible cp.t on target if entity @s",
    f"execute if entity @a[tag=cp.moi,scores={{cp.ag=1}}] unless score #cible cp.t matches 1 if score #s cp.tk matches 0.. run function {NS}:c/loup_chasse"]
# Alpha : on lit la vie du joueur à part (cp.hp sert déjà à la vie du compagnon)
CAP[1][4] = f"{L(1, 30)} as @a[tag=cp.moi,limit=1] if predicate {NS}:faible run function {NS}:c/loup_alpha"
w(F + "c/loup_chasse.mcfunction", [
    "tag @s add cp.chasseur",
    f"execute as @e[type=#{NS}:chasse,distance=..12,sort=nearest,limit=1] run damage @s 1 minecraft:mob_attack by @e[tag=cp.chasseur,limit=1]",
    "tag @s remove cp.chasseur"])
w(F + "c/loup_alpha.mcfunction", [  # exécuté par le joueur
    "execute if score @s cp.cda matches 1.. run return 0", f"{S} set @s cp.cda 120",
    "summon minecraft:wolf ~1 ~ ~ {Tags:[\"cp.renfort\",\"cp.nouveau\"],DeathLootTable:\"minecraft:empty\",PersistenceRequired:1b,variant:\"minecraft:black\"}",
    "summon minecraft:wolf ~-1 ~ ~ {Tags:[\"cp.renfort\",\"cp.nouveau\"],DeathLootTable:\"minecraft:empty\",PersistenceRequired:1b,variant:\"minecraft:black\"}",
    "execute as @e[tag=cp.nouveau] run data modify entity @s Owner set from entity @a[tag=cp.moi,limit=1] UUID",
    f"{S} set @e[tag=cp.nouveau] cp.vie 30", "tag @e[tag=cp.nouveau] remove cp.nouveau",
    "playsound minecraft:entity.wolf.howl neutral @a[distance=..32] ~ ~ ~ 1.5 0.8",
    tr("Alpha : la meute arrive en renfort !", "gold")])
CAP[2] = [  # chat
    f"{S} operation #L cp.t = @a[tag=cp.moi,limit=1] cp.l2",
    f"{L(2, 5)} if score #s cp.tk matches 0.. run function {NS}:c/chat_ronron",
    f"{L(2, 10)} run effect give @a[tag=cp.moi,distance=..24] minecraft:night_vision 15 0 true",
    f"{L(2, 20)} as @a[tag=cp.moi,limit=1] if predicate {NS}:faible run function {NS}:c/sauvetage_120",
    f"{L(2, 30)} run effect give @a[tag=cp.moi] minecraft:luck 3 1 true"]
w(F + "c/chat_ronron.mcfunction", [f"{S} operation #m cp.t = #s cp.tk", f"{S} operation #m cp.t %= #10 cp.t",
                                   "execute if score #m cp.t matches 0 as @a[tag=cp.moi,distance=..12] if predicate compagnons:blesse run effect give @s minecraft:regeneration 4 0 true"])
CAP[3] = [  # perroquet
    f"{S} operation #L cp.t = @a[tag=cp.moi,limit=1] cp.l3",
    f"{L(3, 5)} at @a[tag=cp.moi,limit=1] run effect give @e[type=#{NS}:hostiles,distance=..16] minecraft:glowing 2 0 true",
    f"{L(3, 10)} as @a[tag=cp.moi,limit=1] at @s if block ~ ~-1 ~ #minecraft:air if block ~ ~-2 ~ #minecraft:air if block ~ ~-3 ~ #minecraft:air unless predicate {NS}:planeur run effect give @s minecraft:slow_falling 2 0 true",
    f"{L(3, 20)} as @a[tag=cp.moi,limit=1] at @s if entity @e[type=minecraft:creeper,distance=..10] run function {NS}:c/alerte",
    f"{L(3, 30)} run effect give @a[tag=cp.moi] minecraft:speed 2 0 true",
    f"{L(3, 30)} run effect give @a[tag=cp.moi] minecraft:jump_boost 2 0 true"]
w(F + "c/alerte.mcfunction", ['title @s actionbar {"text":"Creeper tout près !","color":"green","bold":true}',
                              "playsound minecraft:entity.parrot.imitate.creeper neutral @s ~ ~ ~ 1 1"])
CAP[4] = [  # bonhomme de neige
    f"{S} operation #L cp.t = @a[tag=cp.moi,limit=1] cp.l4",
    "effect give @s minecraft:fire_resistance 3 0 true",
    f"{L(4, 5)} run effect give @e[type=#{NS}:hostiles,distance=..6] minecraft:slowness 2 0 true",
    f"{L(4, 10)} run effect give @s minecraft:regeneration 2 1 true",
    f"{S} operation #m cp.t = #s cp.tk", f"{S} operation #m cp.t %= #10 cp.t",
    f"execute if score #L cp.t matches 20..29 if score #m cp.t matches 0 run function {NS}:c/blizzard {{r:8,d:3}}",
    f"{S} operation #m cp.t = #s cp.tk", "scoreboard players set #5 cp.t 5", f"{S} operation #m cp.t %= #5 cp.t",
    f"{L(4, 30)} if score #m cp.t matches 0 run function {NS}:c/blizzard {{r:12,d:5}}"]
w(F + "c/blizzard.mcfunction", [
    "tag @s add cp.givreur",
    "$particle minecraft:snowflake ~ ~1 ~ $(r) 1 $(r) 0.02 120",
    "playsound minecraft:block.powder_snow.break neutral @a[distance=..24] ~ ~ ~ 1.5 0.6",
    f"$effect give @e[type=#{NS}:hostiles,distance=..$(r)] minecraft:slowness 4 2 true",
    f"$execute as @e[type=#{NS}:hostiles,distance=..$(r)] run damage @s $(d) minecraft:freeze by @e[tag=cp.givreur,limit=1]",
    "tag @s remove cp.givreur"])
CAP[5] = [  # allay
    f"{S} operation #L cp.t = @a[tag=cp.moi,limit=1] cp.l5",
    f"{L(5, 5)} at @a[tag=cp.moi,limit=1] run tp @e[type=minecraft:item,distance=1.5..10] @a[tag=cp.moi,limit=1]",
    f"{S} operation #m cp.t = #s cp.tk", f"{S} operation #m cp.t %= #10 cp.t",
    f"{L(5, 10)} if score #m cp.t matches 0 run effect give @a[tag=cp.moi,distance=..12] minecraft:regeneration 4 0 true",
    f"{L(5, 20)} run effect give @a[tag=cp.moi] minecraft:luck 3 0 true",
    f"{L(5, 30)} as @a[tag=cp.moi,limit=1] if predicate {NS}:tres_faible run function {NS}:c/sauvetage_300"]
CAP[6] = [  # golem
    f"{S} operation #L cp.t = @a[tag=cp.moi,limit=1] cp.l6",
    f"{L(6, 5)} run effect give @a[tag=cp.moi,distance=..10] minecraft:resistance 2 0 true",
    "scoreboard players set #8 cp.t 8", f"{S} operation #m cp.t = #s cp.tk", f"{S} operation #m cp.t %= #8 cp.t",
    f"{L(6, 10)} if score #m cp.t matches 0 if entity @e[type=#{NS}:hostiles,distance=..4] run function {NS}:c/seisme",
    f"{L(6, 20)} run effect give @s minecraft:resistance 2 1 true",
    "scoreboard players set #60 cp.t 60", f"{S} operation #m cp.t = #s cp.tk", f"{S} operation #m cp.t %= #60 cp.t",
    f"{L(6, 30)} if score #m cp.t matches 0 run effect give @a[tag=cp.moi,distance=..16] minecraft:absorption 60 1 true"]
w(F + "c/seisme.mcfunction", [
    "tag @s add cp.frappeur",
    "particle minecraft:explosion ~ ~ ~ 2 0.2 2 0 6", "playsound minecraft:entity.iron_golem.attack neutral @a[distance=..16] ~ ~ ~ 1.5 0.6",
    f"execute as @e[type=#{NS}:hostiles,distance=..4] run damage @s 4 minecraft:mob_attack by @e[tag=cp.frappeur,limit=1]",
    f"effect give @e[type=#{NS}:hostiles,distance=..4] minecraft:levitation 1 2 true",
    "tag @s remove cp.frappeur"])
for cd in (120, 300):
    w(F + f"c/sauvetage_{cd}.mcfunction", [  # exécuté par le joueur
        "execute if score @s cp.cda matches 1.. run return 0", f"{S} set @s cp.cda {cd}",
        "effect give @s minecraft:absorption 10 1 true", "effect give @s minecraft:regeneration 5 1 true"] +
        (["effect give @s minecraft:resistance 5 1 true"] if cd == 300 else []) +
        ["particle minecraft:heart ~ ~1.5 ~ 0.4 0.4 0.4 0 8", "playsound minecraft:item.totem.use neutral @s ~ ~ ~ 0.4 1.6",
         tr("Ton compagnon te sauve la mise !", "light_purple")])
CAP = {k: v[1:] for k, v in CAP.items()}
CAP[7] = [  # ghast joyeux
    f"{L(7, 5)} if score #monte cp.t matches 1 run effect give @a[tag=cp.moi] minecraft:resistance 2 0 true",
    f"attribute @s minecraft:flying_speed modifier remove {NS}:rafale",
    f"{L(7, 10)} run attribute @s minecraft:flying_speed modifier add {NS}:rafale 0.25 add_multiplied_base",
    f"{L(7, 20)} if score #monte cp.t matches 1 run effect give @a[tag=cp.moi] minecraft:night_vision 15 0 true",
    f"{L(7, 30)} if score #monte cp.t matches 1 run effect give @a[tag=cp.moi] minecraft:regeneration 2 0 true",
    f"{L(7, 30)} if score #monte cp.t matches 1 run effect give @a[tag=cp.moi] minecraft:fire_resistance 2 0 true"]
CAP[8] = [  # dragon
    "scoreboard players set #3 cp.t 3", f"{S} operation #m cp.t = #s cp.tk", f"{S} operation #m cp.t %= #3 cp.t",
    f"execute if score #L cp.t matches 5..29 if score #m cp.t matches 0 rotated as @s positioned ^ ^ ^5 if entity @e[type=#{NS}:hostiles,distance=..5] run function {NS}:c/souffle {{r:5,d:6}}",
    f"{L(8, 30)} if score #m cp.t matches 0 rotated as @s positioned ^ ^ ^6 if entity @e[type=#{NS}:hostiles,distance=..8] run function {NS}:c/souffle {{r:8,d:12}}",
    f"{L(8, 10)} if score #monte cp.t matches 1 run effect give @a[tag=cp.moi] minecraft:resistance 2 0 true",
    f"attribute @s minecraft:flying_speed modifier remove {NS}:envergure",
    f"{L(8, 20)} run attribute @s minecraft:flying_speed modifier add {NS}:envergure 0.3 add_multiplied_base"]
w(F + "c/souffle.mcfunction", [  # exécuté par le porteur, positionné devant lui
    "tag @s add cp.souffleur",
    "$particle minecraft:dragon_breath ~ ~1 ~ $(r) 1 $(r) 0.02 150",
    "playsound minecraft:entity.ender_dragon.shoot neutral @a[distance=..32] ~ ~ ~ 1.5 1",
    f"$execute as @e[type=#{NS}:hostiles,distance=..$(r)] run damage @s $(d) minecraft:dragon_breath by @e[tag=cp.souffleur,limit=1]",
    "tag @s remove cp.souffleur"])
CAP[9] = [  # wither
    "scoreboard players set #3 cp.t 3", f"{S} operation #m cp.t = #s cp.tk", f"{S} operation #m cp.t %= #3 cp.t",
    f"{L(9, 5)} if score #m cp.t matches 0 if entity @e[type=#{NS}:hostiles,distance=..16] run function {NS}:c/crane",
    f"{L(9, 10)} if score #monte cp.t matches 1 run effect give @a[tag=cp.moi] minecraft:resistance 2 0 true",
    f"{L(9, 20)} run effect give @e[type=#{NS}:hostiles,distance=..6] minecraft:wither 3 0",
    "scoreboard players set #20 cp.t 20", f"{S} operation #m cp.t = #s cp.tk", f"{S} operation #m cp.t %= #20 cp.t",
    f"{L(9, 30)} if score #m cp.t matches 0 if entity @e[type=#{NS}:hostiles,distance=..6] run function {NS}:c/onde"]
w(F + "c/crane.mcfunction", [
    "tag @s add cp.tireur",
    f"execute as @e[type=#{NS}:hostiles,distance=..16,sort=nearest,limit=1] at @s run function {NS}:c/crane_touche",
    "playsound minecraft:entity.wither.shoot neutral @a[distance=..32] ~ ~ ~ 1 1",
    "tag @s remove cp.tireur"])
w(F + "c/crane_touche.mcfunction", [
    "particle minecraft:large_smoke ~ ~1 ~ 0.3 0.5 0.3 0.02 15", "particle minecraft:soul ~ ~1 ~ 0.3 0.5 0.3 0.02 6",
    "damage @s 7 minecraft:wither_skull by @e[tag=cp.tireur,limit=1]", "effect give @s minecraft:wither 4 1"])
w(F + "c/onde.mcfunction", [
    "tag @s add cp.tireur",
    "particle minecraft:explosion_emitter ~ ~1 ~ 0 0 0 0 1", "playsound minecraft:entity.generic.explode neutral @a[distance=..32] ~ ~ ~ 1.5 0.8",
    f"execute as @e[type=#{NS}:hostiles,distance=..6] run damage @s 14 minecraft:explosion by @e[tag=cp.tireur,limit=1]",
    "tag @s remove cp.tireur"])
for k, lignes in CAP.items():
    w(F + f"c/cap_{k}.mcfunction", lignes)
# santé du joueur : prédicats (vie sous 8, 6, 20)
for nom, mx in (("faible", 8), ("tres_faible", 6), ("blesse", 19)):
    wj(f"data/{NS}/predicate/{nom}.json", {"type": "minecraft:entity_scores", "entity": "this",
                                           "scores": {"cp.vie_j": {"max": mx}}})
# la vie du joueur est relevée chaque seconde dans cp.vie_j (score dédié)
OBJ.append("cp.vie_j")
w(F + "joueur.mcfunction", ["execute store result score @s cp.vie_j run data get entity @s Health"] + J)
w(F + "load.mcfunction", [f"scoreboard objectives add {o} dummy" for o in OBJ] + [
    "scoreboard objectives add compagnons trigger",
    "scoreboard objectives add cp.mk minecraft.custom:minecraft.mob_kills",
    "scoreboard objectives add cp.kwi minecraft.killed:minecraft.wither",
    f"{S} add #next cp.t 0", f"{S} set #6 cp.t 6", f"{S} set #10 cp.t 10", f"{S} set #20 cp.t 20", f"{S} set #2 cp.t 2", f"{S} set #5 cp.t 5", f"{S} set #100 cp.t 100",
    f"execute unless data storage {NS}:noms J run data modify storage {NS}:noms J set value []",
    # compagnons sans collision : ils ne poussent pas le joueur et ne se coincent pas contre lui
    "team add cp.compagnons", "team modify cp.compagnons collisionRule never", "team join cp.compagnons @e[tag=cp.c]",
    f"schedule function {NS}:seconde 1s replace"])
wj(f"data/{NS}/predicate/planeur.json", {"type": "minecraft:entity_properties", "entity": "this",
                                         "predicate": {"minecraft:flags": {"is_flying": True}}})

# =====================================================================
# XP ET NIVEAUX
# =====================================================================
# monstre mort tout près d'un compagnon : si son dernier attaquant est un compagnon, son joueur gagne 5 XP pour lui
w(F + "xp/mort.mcfunction", ["tag @s add cp.mort", f"execute on attacker if entity @s[tag=cp.c] run function {NS}:xp/credit"])
w(F + "xp/credit.mcfunction", [
    f"{S} operation #o cp.t = @s cp.own", f"{S} operation #y cp.t = @s cp.typ", f"{S} set #g cp.t 5",
    f"execute as @a if score @s cp.id = #o cp.t run function {NS}:xp/gagner"])
w(F + "xp/joueur_tue.mcfunction", [f"{S} operation #y cp.t = @s cp.out", f"{S} operation #g cp.t = @s cp.mk",
                                   f"function {NS}:xp/gagner"])
w(F + "xp/minute.mcfunction", [f"{S} set @s cp.min 0", f"{S} operation #y cp.t = @s cp.out", f"{S} set #g cp.t 2",
                               f"function {NS}:xp/gagner"])
# #g XP pour le compagnon #y ; bonus de l'Éleveur de Métiers : +1 % par niveau (+100 % au prestige)
w(F + "xp/gagner.mcfunction", [
    f"{S} set #e cp.t 0", f"execute if score @s m.e_lvl matches 1.. run {S} operation #e cp.t = @s m.e_lvl",
    f"execute if score @s m.e_pr matches 1.. run {S} set #e cp.t 100",
    f"{S} operation #e cp.t *= #g cp.t", f"{S} operation #e cp.t /= #100 cp.t", f"{S} operation #g cp.t += #e cp.t"] +
    [f"execute if score #y cp.t matches {k} run function {NS}:xp/ajout_{k}" for k in T])
# 25.6 (v3) : courbe exponentielle, +8 % par niveau ; les montures demandent bien plus (dragon et wither surtout)
BESOIN0 = {1: 60, 2: 60, 3: 60, 4: 60, 5: 60, 6: 60, 7: 120, 8: 180, 9: 200}
BESOIN = lambda k, L: round(BESOIN0[k] * 1.08 ** (L - 1))
for k in T:
    w(F + f"xp/besoin_{k}.mcfunction", "\n".join(
        [f"execute if score @s cp.l{k} matches {L} run return run {S} set #n cp.t {BESOIN(k, L)}" for L in range(1, LMAX + 1)]))
for k, (_, cle, nom, col, ent, ico, req, suit, combat) in T.items():
    w(F + f"xp/ajout_{k}.mcfunction", [
        f"execute if score @s cp.l{k} matches {LMAX}.. run return 0",
        f"{S} operation @s cp.x{k} += #g cp.t", f"function {NS}:xp/monter_{k}"])
    w(F + f"xp/monter_{k}.mcfunction", [
        f"function {NS}:xp/besoin_{k}",
        f"execute if score @s cp.x{k} < #n cp.t run return 0",
        f"{S} operation @s cp.x{k} -= #n cp.t", f"{S} add @s cp.l{k} 1",
        f"execute if score @s cp.l{k} matches {LMAX}.. run {S} set @s cp.x{k} 0",
        f"execute store result storage {NS}:t lv int 1 run {S} get @s cp.l{k}",
        f"function {NS}:xp/annonce_{k} with storage {NS}:t",
        "playsound minecraft:entity.player.levelup neutral @s ~ ~ ~ 0.8 1.4",
        f"execute if score @s cp.out matches {k} run function {NS}:invoquer/maj",
        f"function {NS}:xp/monter_{k}"])
    caps = "".join(f"\\nexecute if score @s cp.l{k} matches {n} run " + tr(f"Nouvelle capacité : {cn} ({ce})", "gold") for n, cn, ce in CAPS[k])
    w(F + f"xp/annonce_{k}.mcfunction",
      f'$tellraw @s [{PREFIX},{{"text":"Ton {nom} passe niveau $(lv) !","color":"{col}","bold":true}}]' + caps.replace("\\n", "\n"))

# =====================================================================
# INVOQUER, RANGER, STATS
# =====================================================================
def deblocage(k):
    j, n, _ = T[k][6]
    return [f"{S} set #deb cp.t 0", f"execute if score @s m.{j}_lvl matches {n}.. run {S} set #deb cp.t 1",
            f"execute if score @s m.{j}_pr matches 1.. run {S} set #deb cp.t 1"] + \
           ([f"execute if score @s m.k_lvl matches {n}.. run {S} set #deb cp.t 1"] if k == 6 else []) + \
           (BOSS[k][1] if k in BOSS else [])
for k, (_, cle, nom, col, ent, ico, (j, n, jn), suit, combat) in T.items():
    # appel depuis le menu (20 + k) : invoque, ou range s'il est déjà dehors
    w(F + f"invoquer/{k}.mcfunction", deblocage(k) + [
        f"execute if score #deb cp.t matches 0 run return run " + tr(f"{LE(nom)} se débloque au {COND(k)}.", "red"),
        f"execute if score @s cp.out matches {k} run return run function {NS}:ranger",
        f"execute if score @s cp.cd matches 1.. run return run " + tr("Ton compagnon se repose encore (K.O.). Patiente un peu.", "red"),
        *([f"execute if dimension minecraft:the_end run return run " + tr("Le dragon refuse de voler dans l’End.", "light_purple")] if k == 8 else []),
        f"function {NS}:ranger_silence", f"{S} set @s cp.out {k}", f"function {NS}:invoquer/actuel",
        tr(f"Ton {nom} t’accompagne.", col)])
w(F + "ranger_silence.mcfunction", [f"function {NS}:marquer", "execute at @e[tag=cp.cur] run particle minecraft:poof ~ ~0.5 ~ 0.3 0.4 0.3 0.02 10",
                                    "execute as @e[tag=cp.vis] if score @s cp.own = #o cp.t if score @s cp.ser = #s cp.t run kill @s",
                                    "tp @e[tag=cp.cur] ~ -1000 ~", "kill @e[tag=cp.cur]", f"{S} set @s cp.out 0", f"{S} add @s cp.ser 1"])
w(F + "ranger.mcfunction", [f"function {NS}:ranger_silence", tr("Ton compagnon est rentré.", "gray"),
                            "playsound minecraft:entity.item.pickup neutral @s ~ ~ ~ 0.6 0.8"])
# (ré)apparition du compagnon cp.out près du joueur, avec un nouveau numéro (les anciennes copies disparaissent)
w(F + "invoquer/actuel.mcfunction", [f"{S} add @s cp.ser 1", f"{S} set @s cp.hp 99999"] +
  [f"execute if score @s cp.out matches {k} run function {NS}:invoquer/s_{k}" for k in T] + [
    f"{S} operation @e[tag=cp.nouveau] cp.own = @s cp.id", f"{S} operation @e[tag=cp.nouveau] cp.ser = @s cp.ser",
    f"{S} operation @e[tag=cp.nouveau] cp.typ = @s cp.out",
    f"{S} operation @e[tag=cp.nvis] cp.own = @s cp.id", f"{S} operation @e[tag=cp.nvis] cp.ser = @s cp.ser",
    f"execute as @e[tag=cp.nouveau] run function {NS}:invoquer/stats",
    "team join cp.compagnons @e[tag=cp.nouveau]",
    f"function {NS}:invoquer/nom", "tag @e[tag=cp.nouveau] remove cp.nouveau", "tag @e[tag=cp.nvis] remove cp.nvis",
    "particle minecraft:happy_villager ~ ~1 ~ 0.5 0.5 0.5 0 12", "playsound minecraft:entity.allay.item_given neutral @s ~ ~ ~ 0.6 1.2"])
for k, (_, cle, nom, col, ent, ico, req, suit, combat) in T.items():
    tags = ["cp.c", "cp.nouveau", f"cp.{cle}"] + ([] if suit else ["cp.lent"]) + (["cp.vol"] if k in MONTURES else []) + \
           (["cp.porteur"] if k in VISUEL else [])
    nbt = [f'Tags:{json.dumps(tags)}', 'DeathLootTable:"minecraft:empty"', "PersistenceRequired:1b", "CanPickUpLoot:0b", "CustomNameVisible:1b"]
    if ent == "iron_golem":
        nbt.append("PlayerCreated:1b")
    if ent == "snow_golem":
        nbt.append("Pumpkin:1b")
    if k in VISUEL:   # porteur invisible, harnais sans rendu (équipement « compagnons:vide » du resource pack)
        nbt.append('active_effects:[{id:"minecraft:invisibility",duration:-1,amplifier:0b,show_particles:0b,show_icon:0b}]')
        nbt.append('equipment:{body:{id:"minecraft:white_harness",count:1,components:{"minecraft:equippable":{slot:"body",asset_id:"compagnons:vide"}}}}')
        nbt.append("Silent:1b")
    post = []
    if ent in ("wolf", "cat", "parrot"):
        post.append("data modify entity @e[tag=cp.nouveau,limit=1] Owner set from entity @s UUID")
    if ent == "allay":
        post.append('data modify entity @e[tag=cp.nouveau,limit=1] Brain.memories."minecraft:liked_player".value set from entity @s UUID')
    if k in VARIANTES:
        cleV, lst, pas = VARIANTES[k]
        for i, (val, _) in enumerate(lst):
            v = f'"{val}"' if isinstance(val, str) else str(val)
            if cleV != "harnais":
                post.append(f"execute if score @s cp.v{k} matches {i} run data modify entity @e[tag=cp.nouveau,limit=1] {cleV} set value {v}")
    if k == 7:   # couleur du harnais
        for i, (couleur, _) in enumerate(VARIANTES[7][1]):
            post.append(f'execute if score @s cp.v7 matches {i} run data modify entity @e[tag=cp.nouveau,limit=1] equipment.body set value {{id:"minecraft:{couleur}_harness",count:1}}')
    if k in VISUEL:
        e, taille, rot, dy, tg = VISUEL[k]
        post.append(f'summon minecraft:{e} ^ ^ ^-3 {{Tags:["cp.vis","{tg}","cp.nvis"],NoAI:1b,Invulnerable:1b,Silent:1b,PersistenceRequired:1b,'
                    f'DeathLootTable:"minecraft:empty",' + ("Invul:0," if e == "wither" else "") +
                    f'attributes:[{{id:"minecraft:scale",base:{taille}d}}]}}')
    if k == 1:   # armure de loup dès le niveau 15
        post.append('execute if score @s cp.l1 matches 15.. run data modify entity @e[tag=cp.nouveau,limit=1] equipment.body set value {id:"minecraft:wolf_armor",count:1}')
    w(F + f"invoquer/s_{k}.mcfunction", [f"summon minecraft:{ent} ^ ^ ^-1.5 {{{','.join(nbt)}}}"] + post)
# stats du niveau, exécuté par le compagnon (lit le niveau de son joueur)
ST = [f"{S} operation #o cp.t = @s cp.own", f"{S} operation #y cp.t = @s cp.typ", f"{S} set #L cp.t 1"] + \
     [f"execute if score #y cp.t matches {k} as @a if score @s cp.id = #o cp.t run {S} operation #L cp.t = @s cp.l{k}" for k in T] + \
     [f"execute if score #y cp.t matches {k} as @a if score @s cp.id = #o cp.t run {S} operation #R cp.t = @s cp.r{k}" for k in T] + \
     [f"execute if score #y cp.t matches {k} as @a if score @s cp.id = #o cp.t run {S} operation #P cp.t = @s cp.f{k}" for k in T] + \
     [f"execute if score #y cp.t matches {k} run function {NS}:stats/{k}" for k in T] + \
     [f"function {NS}:stats/rangs"]
ST.insert(0, f"{S} set #R cp.t 0")
ST.insert(0, f"{S} set #P cp.t 0")
w(F + "invoquer/stats.mcfunction", ST)
# Robustesse : +10 % de vie par rang ; Puissance : +15 % de dégâts, +5 % de vitesse, +10 % de vol par rang
RG = [f"attribute @s minecraft:max_health modifier remove {NS}:robustesse", f"attribute @s minecraft:attack_damage modifier remove {NS}:puissance",
      f"attribute @s minecraft:movement_speed modifier remove {NS}:puissance", f"attribute @s minecraft:flying_speed modifier remove {NS}:puissance"]
for r in range(1, 6):
    RG += [f"execute if score #R cp.t matches {r} run attribute @s minecraft:max_health modifier add {NS}:robustesse {0.1 * r:.2f} add_multiplied_base",
           f"execute if score #P cp.t matches {r} run attribute @s minecraft:attack_damage modifier add {NS}:puissance {0.15 * r:.2f} add_multiplied_base",
           f"execute if score #P cp.t matches {r} run attribute @s minecraft:movement_speed modifier add {NS}:puissance {0.05 * r:.2f} add_multiplied_base",
           f"execute if score #P cp.t matches {r} run attribute @s minecraft:flying_speed modifier add {NS}:puissance {0.1 * r:.2f} add_multiplied_base"]
RG.append("execute store result entity @s Health float 1 run attribute @s minecraft:max_health get")
w(F + "stats/rangs.mcfunction", RG)
for k in T:
    lignes = []
    for lv in range(1, LMAX + 1):
        hp, dmg, spd, arm, sc = stats(k, lv)
        cmds = [f"attribute @s minecraft:max_health base set {hp}", f"attribute @s minecraft:armor base set {arm}",
                f"attribute @s minecraft:movement_speed base set {spd:.3f}", f"attribute @s minecraft:scale base set {sc:.3f}",
                f"data modify entity @s Health set value {hp}f"]
        if dmg:
            cmds.insert(1, f"attribute @s minecraft:attack_damage base set {dmg:.2f}")
        if k in VOL:
            cmds.append(f"attribute @s minecraft:flying_speed base set {VOL[k](lv):.4f}")
        w(F + f"stats/{k}_{lv}.mcfunction", cmds)
        lignes.append(f"execute if score #L cp.t matches {lv} run return run function {NS}:stats/{k}_{lv}")
    w(F + f"stats/{k}.mcfunction", lignes)
# remise à niveau du compagnon dehors (montée de niveau) : stats et nom
w(F + "invoquer/maj.mcfunction", [f"function {NS}:marquer", "tag @e[tag=cp.cur] add cp.nouveau",
                                  f"execute as @e[tag=cp.cur] run function {NS}:invoquer/stats", f"function {NS}:invoquer/nom",
                                  "tag @e[tag=cp.nouveau] remove cp.nouveau",
                                  "execute at @e[tag=cp.cur] run particle minecraft:totem_of_undying ~ ~1 ~ 0.3 0.5 0.3 0.3 20"])
# nom : celui choisi par le joueur (objet renommé), sinon le nom du compagnon ; suivi du niveau
w(F + "invoquer/nom.mcfunction", [
    f"execute store result storage {NS}:t id int 1 run {S} get @s cp.id",
    f"execute store result storage {NS}:t k int 1 run {S} get @s cp.out"] +
    [f'execute if score @s cp.out matches {k} store result storage {NS}:t lv int 1 run {S} get @s cp.l{k}' for k in T] +
    [f'execute if score @s cp.out matches {k} run data modify storage {NS}:t n set value {{text:"{T[k][2]}",color:"{T[k][3]}"}}' for k in T] +
    [f"function {NS}:invoquer/nom_lire with storage {NS}:t",
     f"function {NS}:invoquer/nom_poser with storage {NS}:t"])
w(F + "invoquer/nom_lire.mcfunction", f"$execute if data storage {NS}:noms J[{{id:$(id)}}].n$(k) run data modify storage {NS}:t n set from storage {NS}:noms J[{{id:$(id)}}].n$(k)")
w(F + "invoquer/nom_poser.mcfunction",
  '$data modify entity @e[tag=cp.nouveau,limit=1] CustomName set value [{text:"",color:"white",italic:false},$(n),{text:"  niv. $(lv)",color:"gray"}]\n'
  '$data modify entity @e[tag=cp.nvis,limit=1] CustomName set value [{text:"",color:"white",italic:false},$(n),{text:"  niv. $(lv)",color:"gray"}]')

# =====================================================================
# ACTIONS DU MENU
# =====================================================================
w(F + "mode.mcfunction", [
    f"execute if score @s cp.mode matches 1 run return run function {NS}:mode_suivre",
    f"{S} set @s cp.mode 1", f"function {NS}:marquer",
    "execute as @e[tag=cp.cur] run data modify entity @s Sitting set value 1b",
    tr("Ton compagnon reste ici (il défend la zone). Le même bouton le fait revenir.", "yellow")])
w(F + "mode_suivre.mcfunction", [f"{S} set @s cp.mode 0", f"function {NS}:marquer",
                                 "execute as @e[tag=cp.cur] run data modify entity @s Sitting set value 0b",
                                 tr("Ton compagnon te suit.", "green")])
w(F + "chasse.mcfunction", [
    f"execute if score @s cp.ag matches 1 run return run function {NS}:chasse_off",
    f"{S} set @s cp.ag 1", tr("Mode chasse : ton loup va chercher les monstres autour de toi (jamais les creepers).", "gold")])
w(F + "chasse_off.mcfunction", [f"{S} set @s cp.ag 0", tr("Mode chasse coupé : ton loup te défend seulement.", "gray")])
for k, (_, cle, nom, col, ent, ico, req, suit, combat) in T.items():
    if k in VARIANTES:
        cleV, lst, pas = VARIANTES[k]
        A = [f"{S} add @s cp.v{k} 1"]
        # passe à la suivante, revient à 0 si elle n'est pas encore débloquée ou si c'était la dernière
        A += [f"execute if score @s cp.v{k} matches {i} unless score @s cp.l{k} matches {1 + pas * i}.. run {S} set @s cp.v{k} 0" for i in range(1, len(lst))]
        A += [f"execute if score @s cp.v{k} matches {len(lst)}.. run {S} set @s cp.v{k} 0"]
        A += [f"execute if score @s cp.out matches {k} run function {NS}:invoquer/actuel",
              f"function {NS}:menu/page_{k}"]
        w(F + f"apparence/{k}.mcfunction", A)
    w(F + f"renommer/{k}.mcfunction", [
        f"execute unless data entity @s SelectedItem.components.\"minecraft:custom_name\" run return run " + tr("Tiens en main un objet renommé à l’enclume (une étiquette, un papier...), puis clique sur Renommer.", "red"),
        f"execute store result storage {NS}:t id int 1 run {S} get @s cp.id", f"data modify storage {NS}:t k set value {k}",
        f"function {NS}:noms/creer with storage {NS}:t",
        f"data modify storage {NS}:t n set from entity @s SelectedItem.components.\"minecraft:custom_name\"",
        f"function {NS}:renommer/poser with storage {NS}:t",
        f"execute if score @s cp.out matches {k} run function {NS}:invoquer/maj",
        tr(f"Ton {nom} a un nouveau nom.", "green"), f"function {NS}:menu/page_{k}"])
w(F + "renommer/poser.mcfunction", f"$data modify storage {NS}:noms J[{{id:$(id)}}].n$(k) set value $(n)")

# =====================================================================
# MENUS (dialogues, style des autres packs : icônes du jeu, 3 colonnes, bandeau)
# =====================================================================
def btn(label, val, width=130, tip=None):
    s = f"{{label:{label},width:{width}"
    if tip:
        s += f',tooltip:{{text:"{tip}"}}'
    return s + f',action:{{type:"run_command",command:"trigger compagnons set {val}"}}}}'
def txt(t, col="white", bold=False):
    return f'{{text:"{t}",color:"{col}",bold:{"true" if bold else "false"},italic:false}}'

# =====================================================================
# AMÉLIORATIONS : 3 voies de 5 rangs par compagnon, payées en points de dressage (1 par niveau) et en Écus
#   rang r : r points (les 3 voies au max coûtent 45 points, il y en a 30 : il faut choisir) et 4 000 x r Écus (25.6)
# =====================================================================
VOIES = [("r", "Robustesse", "red", "apple", "+10 % de vie par rang."),
         ("f", "Puissance", "gold", "blaze_powder", "+15 % de dégâts, +5 % de vitesse et +10 % de vitesse de vol par rang."),
         ("m", "Maîtrise", "light_purple", "experience_bottle", "Chaque rang débloque les capacités 2 niveaux plus tôt (10 niveaux au rang 5).")]
TRI = {0: 0, 1: 1, 2: 3, 3: 6, 4: 10, 5: 15}
def points(k):
    """#pt = points de dressage libres du compagnon k."""
    L_ = [f"{S} operation #pt cp.t = @s cp.l{k}"]
    for v, *_ in VOIES:
        L_ += [f"execute if score @s cp.{v}{k} matches {r} run {S} remove #pt cp.t {TRI[r]}" for r in range(1, 6)]
    return L_
for k, (_, cle, nom, col, ent, ico, req, suit, combat) in T.items():
    P_ = [f"{S} add @s cp.{v}{k} 0" for v, *_ in VOIES] + points(k) + \
         [f"execute store result storage {NS}:a pt int 1 run {S} get #pt cp.t"]
    for v, vn, vc, vi, vd in VOIES:
        P_ += [f"execute store result storage {NS}:a {v} int 1 run {S} get @s cp.{v}{k}",
               f'data modify storage {NS}:a c{v} set value "{vc}"', f'execute if score @s cp.{v}{k} matches 5.. run data modify storage {NS}:a c{v} set value "dark_gray"',
               f'data modify storage {NS}:a p{v} set value "max"']
        for r in range(0, 5):
            P_.append(f'execute if score @s cp.{v}{k} matches {r} run data modify storage {NS}:a p{v} set value "{r + 1} pt + {4000 * (r + 1):,} Écus"'.replace(",", " "))
    P_ += [f"execute store result storage {NS}:a e int 1 run {S} get @s c.ecus", f"function {NS}:menu/amel_{k}_d with storage {NS}:a"]
    w(F + f"menu/amel_{k}.mcfunction", P_)
    acts_ = [btn(f'[{IC(vi)},{{text:"  {vn} $({v})/5",color:"$(c{v})",bold:true}}]', 100 + 10 * k + i, 140, f"{vd}\\nProchain rang : $(p{v}).")
             for i, (v, vn, vc, vi, vd) in enumerate(VOIES, 1)]
    w(F + f"menu/amel_{k}_d.mcfunction",
      f'$dialog show @s {{type:"minecraft:multi_action",title:[{IC(ico)},{{text:"  {nom} : améliorations",color:"{col}",bold:true}}],can_close_with_escape:true,pause:false,'
      f'body:[{BAN},{{type:"minecraft:plain_message",width:440,contents:[{{text:"Points de dressage libres : ",color:"gray"}},{{text:"$(pt)",color:"yellow",bold:true}},'
      f'{{text:"   ·   ton compte : $(e) Écus\\n",color:"gray"}},{{text:"1 point par niveau du compagnon. Un rang coûte autant de points que son numéro, plus 4 000 Écus par rang. 30 points pour 45 au total : choisis ta voie.",color:"dark_gray"}}]}}],'
      f'actions:[{",".join(acts_)}],columns:3,'
      f'exit_action:{{label:"Retour",width:200,action:{{type:"run_command",command:"trigger compagnons set {10 + k}"}}}}}}')
    for i, (v, vn, vc, vi, vd) in enumerate(VOIES, 1):
        A_ = [f"execute if score @s cp.{v}{k} matches 5.. run return run " + tr(f"{vn} est déjà au maximum.", "red")] + points(k) + [
              f"{S} operation #c cp.t = @s cp.{v}{k}", f"{S} add #c cp.t 1",
              f"execute if score #pt cp.t < #c cp.t run return run " + tr("Pas assez de points de dressage : fais monter ton compagnon de niveau.", "red"),
              f"{S} operation #e cp.t = #c cp.t", f"{S} set #1500 cp.t 4000", f"{S} operation #e cp.t *= #1500 cp.t",
              f"{S} set #ok cp.t 0", f"execute if score @s c.ecus >= #e cp.t run {S} set #ok cp.t 1",
              f"execute if score #ok cp.t matches 0 run return run " + tr("Pas assez d’Écus sur ton compte.", "red"),
              f"{S} operation @s c.ecus -= #e cp.t", f"{S} add @s cp.{v}{k} 1",
              f"execute if score @s cp.out matches {k} run function {NS}:invoquer/maj",
              "playsound minecraft:block.enchantment_table.use neutral @s ~ ~ ~ 1 1.2",
              tr(f"{vn} de ton {nom} : un rang de plus !", vc)]
        w(F + f"amel/{k}_{v}.mcfunction", A_)
        w(F + f"amel/{k}_{v}_menu.mcfunction", [f"function {NS}:amel/{k}_{v}", f"function {NS}:menu/amel_{k}"])

ENT = [f"{S} operation #v cp.t = @s compagnons", f"{S} set @s compagnons 0", "scoreboard players enable @s compagnons",
       f"execute if score #v cp.t matches 1 run return run function {NS}:menu/accueil",
       f"execute if score #v cp.t matches 2 run return run function {NS}:ranger",
       f"execute if score #v cp.t matches 3 run return run function {NS}:mode",
       f"execute if score #v cp.t matches 4 run return run function {NS}:menu/aide",
       f"execute if score #v cp.t matches 5 run return run function {NS}:chasse"]
for k in T:
    ENT += [f"execute if score #v cp.t matches {10 + k} run return run function {NS}:menu/page_{k}",
            f"execute if score #v cp.t matches {20 + k} run return run function {NS}:menu/agir_{k}",
            f"execute if score #v cp.t matches {40 + k} run return run function {NS}:renommer/{k}"]
    if k in VARIANTES:
        ENT.append(f"execute if score #v cp.t matches {30 + k} run return run function {NS}:apparence/{k}")
    ENT.append(f"execute if score #v cp.t matches {50 + k} run return run function {NS}:menu/amel_{k}")
    ENT += [f"execute if score #v cp.t matches {100 + 10 * k + i} run return run function {NS}:amel/{k}_{v}_menu" for i, (v, *_) in enumerate(VOIES, 1)]
w(F + "menu/entree.mcfunction", ENT)
for k in T:
    w(F + f"menu/agir_{k}.mcfunction", [f"function {NS}:invoquer/{k}", f"function {NS}:menu/page_{k}"])

# ---------------------------------------------------------------- accueil
A = [f"execute unless score @s cp.id matches 1.. run function {NS}:id",
     f'data modify storage {NS}:m dehors set value "aucun"', f'data modify storage {NS}:m md set value "Il te suit"',
     f'execute if score @s cp.mode matches 1 run data modify storage {NS}:m md set value "Il garde la zone"']
for k, (_, cle, nom, col, ent, ico, (j, n, jn), suit, combat) in T.items():
    A += deblocage(k) + [
        f"execute store result storage {NS}:m l{k} int 1 run {S} get @s cp.l{k}",
        f'data modify storage {NS}:m b{k} set value {{text:"  {nom.split()[0]} niv. ",color:"{col}"}}',
        f'execute if score #deb cp.t matches 0 run data modify storage {NS}:m b{k} set value {{text:"  ✖ {nom.split()[0]}",color:"dark_gray"}}',
        f'execute if score @s cp.out matches {k} run data modify storage {NS}:m dehors set value "{nom}"',
        f'data modify storage {NS}:m s{k} set value ""',
        f"execute if score #deb cp.t matches 1 store result storage {NS}:m s{k} int 1 run {S} get @s cp.l{k}"]
A.append(f"function {NS}:menu/accueil_b with storage {NS}:m")
w(F + "menu/accueil.mcfunction", A)
acts = []
for k, (_, cle, nom, col, ent, ico, (j, n, jn), suit, combat) in T.items():
    tip = f"{nom} : {BASE[k]}\\nSe débloque au {COND(k)}."
    acts.append(btn(f'[{IC(ico)},$(b{k}),{{text:"$(s{k})",color:"yellow"}}]', 10 + k, 150, tip))
acts += [btn(f'[{IC("lead")},{txt("  Ranger", "gray")}]', 2, 150, "Fait rentrer ton compagnon."),
         btn(f'[{IC("compass_00")},{txt("  Suivre / Rester", "aqua")}]', 3, 150, "Il te suit, ou il reste là où il est pour garder la zone."),
         btn(f'[{IC("book")},{txt("  Comment ça marche", "white")}]', 4, 150, "Niveaux, capacités, apparences, K.O.")]
w(F + "menu/accueil_b.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Compagnons",color:"#E0A040",bold:true},can_close_with_escape:true,pause:false,'
  f'body:[{BAN},{{type:"minecraft:plain_message",width:460,contents:[{{text:"Compagnon dehors : ",color:"gray"}},{{text:"$(dehors)",color:"gold"}},'
  '{text:"   ·   $(md)\\n",color:"gray"},{text:"Un compagnon à la fois. Il se débloque avec tes métiers (et les boss pour le dragon et le wither), gagne ses niveaux, ses capacités et des améliorations. Ghast, dragon et wither se montent : on vole !",color:"dark_gray"}]}],'
  f'actions:[{",".join(acts)}],columns:3,'
  'exit_action:{label:"Fermer",width:200}}')

# ---------------------------------------------------------------- page d'un compagnon
for k, (_, cle, nom, col, ent, ico, (j, n, jn), suit, combat) in T.items():
    P = deblocage(k) + [
        f"execute if score #deb cp.t matches 0 run return run function {NS}:menu/verrou_{k}",
        f"execute store result storage {NS}:p lv int 1 run {S} get @s cp.l{k}",
        f"execute store result storage {NS}:p xp int 1 run {S} get @s cp.x{k}",
        f"function {NS}:xp/besoin_{k}",
        f"execute store result storage {NS}:p need int 1 run {S} get #n cp.t",
        f"{S} operation #b cp.t = @s cp.x{k}", f"{S} operation #b cp.t *= #10 cp.t", f"{S} operation #b cp.t /= #n cp.t",
        f"execute if score @s cp.l{k} matches {LMAX}.. run {S} set #b cp.t 10"] + \
        [f'execute if score #b cp.t matches {b} run data modify storage {NS}:p bar set value "{GLY["barre_" + str(b)]}"' for b in range(11)] + [
        f'data modify storage {NS}:p act set value "Invoquer"', f'data modify storage {NS}:p actc set value "green"',
        f'execute if score @s cp.out matches {k} run data modify storage {NS}:p act set value "Ranger"',
        f'execute if score @s cp.out matches {k} run data modify storage {NS}:p actc set value "gray"',
        f'execute if score @s cp.out matches {k} if score @s cp.mode matches 1 run data modify storage {NS}:p act set value "Ranger (il garde)"',
        f'data modify storage {NS}:p mdl set value "Il te suit"', f'execute if score @s cp.mode matches 1 run data modify storage {NS}:p mdl set value "Il garde la zone"',
        f'data modify storage {NS}:p ch set value "Chasse : non"', f'execute if score @s cp.ag matches 1 run data modify storage {NS}:p ch set value "Chasse : oui"']
    # stats lisibles par niveau
    for lv in range(1, LMAX + 1):
        hp, dmg, spd, arm, sc = stats(k, lv)
        st = f"{hp // 2} cœurs" + (f" · {dmg:.1f} dégâts".replace(".", ",") if dmg else "") + (f" · armure {arm}" if arm else "")
        P.append(f'execute if score @s cp.l{k} matches {lv} run data modify storage {NS}:p st set value "{st}"')
    P += [f"{S} operation #E cp.t = @s cp.l{k}", f"{S} operation #mm cp.t = @s cp.m{k}", f"{S} operation #mm cp.t *= #2 cp.t",
          f"{S} operation #E cp.t += #mm cp.t"] + points(k) + [f"execute store result storage {NS}:p pt int 1 run {S} get #pt cp.t"]
    for i, (lvc, cn, ce) in enumerate(CAPS[k]):
        P += [f'data modify storage {NS}:p c{i} set value "dark_gray"', f'data modify storage {NS}:p m{i} set value "✖"',
              f'execute if score #E cp.t matches {lvc}.. run data modify storage {NS}:p c{i} set value "green"',
              f'execute if score #E cp.t matches {lvc}.. run data modify storage {NS}:p m{i} set value "✔"']
    if k in VARIANTES:
        cleV, lst, pas = VARIANTES[k]
        P += [f'execute if score @s cp.v{k} matches {i} run data modify storage {NS}:p ap set value "{vn}"' for i, (_, vn) in enumerate(lst)]
        P.insert(0, f'data modify storage {NS}:p ap set value "{lst[0][1]}"')
    P.append(f"function {NS}:menu/page_{k}_d with storage {NS}:p")
    w(F + f"menu/page_{k}.mcfunction", P)
    caps = ",".join(f'{{text:"$(m{i}) {cn}",color:"$(c{i})",bold:true}},{{text:"  niv. {lvc} · {ce}\\n",color:"gray",bold:false}}'
                    for i, (lvc, cn, ce) in enumerate(CAPS[k]))
    body = (f'{{type:"minecraft:item",item:{{id:"minecraft:{OEUF.get(k, ent)}_spawn_egg"}},show_decorations:false,show_tooltip:false,'
            f'description:{{width:280,contents:[{{text:"{nom}\\n",color:"{col}",bold:true}},{{text:"Niveau $(lv)   ",color:"yellow",bold:false}},'
            f'{{text:"$(bar)",font:"metiers:icones",color:"white"}},{{text:"  $(xp) / $(need) XP\\n",color:"gray"}},{{text:"$(st)",color:"white"}}]}}}},'
            f'{{type:"minecraft:plain_message",width:420,contents:[{{text:"{BASE[k]}\\n\\n",color:"white"}},{caps}]}}')
    acts = [btn(f'[{IC(ico)},{{text:"  $(act)",color:"$(actc)",bold:true}}]', 20 + k, 130, "Invoquer ce compagnon (l’autre rentre), ou le ranger."),
            btn(f'[{IC("compass_00")},{{text:"  $(mdl)",color:"aqua"}}]', 3, 130, "Il te suit, ou il reste là où il est pour garder la zone."),
            btn(f'[{IC("name_tag")},{txt("  Renommer", "yellow")}]', 40 + k, 130, "Tiens en main un objet renommé à l’enclume, puis clique."),
            btn(f'[{IC("experience_bottle")},{{text:"  Améliorer ($(pt))",color:"green",bold:true}}]', 50 + k, 130,
                "Robustesse, Puissance, Maîtrise : 5 rangs chacune, payés en points de dressage et en Écus.")]
    if k in VARIANTES:
        cleV, lst, pas = VARIANTES[k]
        acts.append(btn(f'[{IC("painting")},{{text:"  $(ap)",color:"light_purple"}}]', 30 + k, 130,
                        f"Change d’apparence. Une nouvelle tous les {pas} niveaux ({len(lst)} en tout)."))
    if k == 1:
        acts.append(btn(f'[{IC("iron_sword")},{{text:"  $(ch)",color:"gold"}}]', 5, 130, "Mode chasse : il va chercher les monstres autour de toi (jamais les creepers)."))
    w(F + f"menu/page_{k}_d.mcfunction",
      f'$dialog show @s {{type:"minecraft:multi_action",title:[{IC(ico)},{{text:"  {nom}",color:"{col}",bold:true}}],can_close_with_escape:true,pause:false,'
      f'body:[{body}],actions:[{",".join(acts)}],columns:3,'
      'exit_action:{label:"Retour",width:200,action:{type:"run_command",command:"trigger compagnons set 1"}}}')
    w(F + f"menu/verrou_{k}.mcfunction", [
        tr(f"{LE(nom)} se débloque au {COND(k)}. Le prestige du métier compte aussi.", "red"),
        f"function {NS}:menu/accueil"])

w(F + "menu/aide.mcfunction",
  'dialog show @s {type:"minecraft:notice",title:{text:"Compagnons : comment ça marche",color:"#E0A040",bold:true},'
  f'body:[{BAN},{{type:"minecraft:plain_message",width:400,contents:[{{text:"'
  "Déblocage : chaque compagnon vient d’un métier (loup Chasseur 10, chat Fermier 10, perroquet Explorateur 15, bonhomme de neige Pêcheur 20, allay Enchanteur 25, golem Mineur ou Bâtisseur 30). Le prestige compte comme le niveau 100.\\n\\n"
  "Niveaux (de plus en plus longs, +8 % par niveau, montures bien plus lentes) : 5 XP par monstre qu’il achève, 1 par monstre que tu tues pendant qu’il est dehors, 2 par minute passée ensemble. +1 % par niveau d’Éleveur. À chaque niveau il gagne de la vie, des dégâts, de l’armure, et parfois grandit. Niveau maximum 30.\\n\\n"
  "Capacités : 4 par compagnon, aux niveaux 5, 10, 20 et 30. Apparences : une nouvelle régulièrement (loup, chat, perroquet). Le loup porte une armure dès le niveau 15.\\n\\n"
  "Montures : ghast joyeux (Explorateur 40), dragon de l’Ender (Chasseur 50 et l’Ender Dragon vaincu), wither (Chasseur 70 et un Wither affronté). Clic droit pour monter, regarde où tu veux aller et avance. En descendant en plein vol, tu tombes doucement.\\n\\n"
  "Améliorations : 1 point de dressage par niveau, à placer dans Robustesse (vie), Puissance (dégâts et vitesse) ou Maîtrise (capacités plus tôt), 5 rangs chacune, avec des Écus (4 000 par rang).\\n\\n"
  "K.O. : à court de vie, il rentre se reposer 60 secondes, il ne meurt jamais. Il te suit d’une dimension à l’autre et rentre quand tu te déconnectes."
  '",color:"white"}]}],action:{label:"Retour",width:200,action:{type:"run_command",command:"trigger compagnons set 1"}}}')

# ---------------------------------------------------------------- menu G commun (copie de celui de Commerce)
MENU = os.path.join(ICI, "..", "..", "commerce", "sources", "menu_serveur.json")
if os.path.exists(MENU):
    wj("data/serveur/dialog/menu.json", json.load(open(MENU, encoding="utf-8")))
    wj("data/minecraft/tags/dialog/quick_actions.json", {"values": ["serveur:menu"]})
    wj("data/minecraft/tags/dialog/pause_screen_additions.json", {"values": ["serveur:menu"]})

# ---------------------------------------------------------------- admin
w(F + "version.mcfunction", tr("Version 4.3 : suivi au pas entre 3 et 5 blocs, rattrapage s’il est coincé, et le compagnon attaque ce que tu frappes.", "gold"))
w(F + "admin/max.mcfunction", [f"{S} set @s cp.l{k} {LMAX}" for k in T] + [f"{S} set @s cp.x{k} 0" for k in T] +
  [f"execute if score @s cp.out matches 1.. run function {NS}:invoquer/maj", tr("Tous tes compagnons passent niveau 30 (test).", "gold")])
w(F + "admin/zero.mcfunction", [f"{S} set @s cp.l{k} 1" for k in T] + [f"{S} set @s cp.x{k} 0" for k in T] +
  [f"execute if score @s cp.out matches 1.. run function {NS}:invoquer/maj", tr("Tous tes compagnons repassent niveau 1.", "gray")])
w(F + "desinstaller.mcfunction", ["tp @e[tag=cp.c] ~ -1000 ~", "kill @e[tag=cp.c]", "kill @e[tag=cp.vis]", "tp @e[tag=cp.renfort] ~ -1000 ~", "kill @e[tag=cp.renfort]",
                                  f"schedule clear {NS}:seconde"] + [f"scoreboard objectives remove {o}" for o in OBJ] +
  ["scoreboard objectives remove compagnons", "scoreboard objectives remove cp.mk", "scoreboard objectives remove cp.kwi", f"data remove storage {NS}:noms J",
   'tellraw @s {"text":"[Compagnons] Désinstallé. Désactive maintenant le pack : /datapack disable \\"file/compagnons.zip\\"","color":"gray"}'])

wj("pack.mcmeta", {"pack": {"description": "Compagnons : loup, chat, golem... qui progressent avec toi", "min_format": 84, "max_format": 200}})

# ---------------------------------------------------------------- resource pack (fusionné par labo/outils/fusion_rp.py)
RP = os.path.join(ICI, "..", "build", "compagnons_rp")
if os.path.exists(RP):
    shutil.rmtree(RP)
os.makedirs(os.path.join(RP, "assets", NS, "equipment"))
# harnais invisible : une couche avec une texture entièrement transparente (une liste de couches vide est refusée
# par le client : « Map must have contents »)
json.dump({"layers": {"happy_ghast_body": [{"texture": f"{NS}:vide"}]}}, open(os.path.join(RP, "assets", NS, "equipment", "vide.json"), "w"))
os.makedirs(os.path.join(RP, "assets", NS, "textures", "entity", "equipment", "happy_ghast_body"))
from PIL import Image as _Im
_Im.new("RGBA", (128, 128), (0, 0, 0, 0)).save(os.path.join(RP, "assets", NS, "textures", "entity", "equipment", "happy_ghast_body", "vide.png"))

# ---------------------------------------------------------------------------------------------
n = 0
zp = os.path.join(ICI, "..", "compagnons.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, _, fs in os.walk(ROOT):
        for fn in sorted(fs):
            full = os.path.join(dp, fn)
            z.write(full, os.path.relpath(full, ROOT).replace(os.sep, "/"))
            n += 1
print("fichiers :", n)

import os, json, shutil, zipfile

ROOT = "/home/claude/metiers_datapack"
NS = "metiers"
if os.path.exists(ROOT):
    shutil.rmtree(ROOT)

ELISION = [(f"{a} {n}", f"{b}{n}") for n in ("Éleveur", "Enchanteur", "Explorateur")
           for a, b in (("du", "de l'"), ("de", "d'"), ("Du", "De l'"), ("De", "D'"))]

def w(path, txt):
    for a, b in ELISION:
        txt = txt.replace(a, b)
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(txt.strip() + "\n")

def wj(path, obj):
    w(path, json.dumps(obj, ensure_ascii=False, indent=2))

F = f"data/{NS}/function/"
MAXLVL = 100

# =====================================================================
# MÉTIERS ET SOURCES D'XP
# =====================================================================
LOGS = ["oak_log", "spruce_log", "birch_log", "jungle_log", "acacia_log", "dark_oak_log",
        "mangrove_log", "cherry_log", "pale_oak_log", "crimson_stem", "warped_stem"]
# Mineur : 4 points = 1 XP (pierre 1/4 XP, deepslate 1/2 XP, diamant 20 XP)
STONES = {"stone": 2, "deepslate": 3, "andesite": 2, "diorite": 2, "granite": 2, "tuff": 2, "blackstone": 2}
ORES = {"coal_ore": 8, "deepslate_coal_ore": 10, "copper_ore": 6, "deepslate_copper_ore": 8,
        "iron_ore": 16, "deepslate_iron_ore": 20, "gold_ore": 24, "deepslate_gold_ore": 28,
        "redstone_ore": 12, "deepslate_redstone_ore": 14, "lapis_ore": 20, "deepslate_lapis_ore": 24,
        "diamond_ore": 80, "deepslate_diamond_ore": 90, "emerald_ore": 100, "deepslate_emerald_ore": 110,
        "nether_gold_ore": 6, "nether_quartz_ore": 6, "ancient_debris": 160}
DIV = {"m": 4, "f": 2, "e": 2}
ORE_DROP = {"coal": "coal 1", "copper": "raw_copper 2", "iron": "raw_iron 1", "gold": "raw_gold 1",
            "redstone": "redstone 4", "lapis": "lapis_lazuli 4", "diamond": "diamond 1",
            "emerald": "emerald 1", "nether_gold": "gold_nugget 3", "nether_quartz": "quartz 1"}
# Fermier : 3 points = 1 XP (un plant de blé = 1 XP, une carotte = 1/3 XP car un plant en donne 2 à 5)
CROPS = {"wheat": 3, "carrot": 1, "potato": 1, "beetroot": 3, "melon_slice": 1, "pumpkin": 4,
         "nether_wart": 1, "cocoa_beans": 2, "sweet_berries": 1, "sugar_cane": 2}
PLANTABLE = ["carrot", "potato", "nether_wart", "cocoa_beans", "sweet_berries", "pumpkin", "sugar_cane"]
BOSSES = {"wither": 200, "ender_dragon": 300, "warden": 100, "elder_guardian": 45}

jobs = {
    "b": {"name": "Bûcheron", "color": "gold", "idx": 1, "icon": "♣", "src": []},
    "f": {"name": "Fermier", "color": "green", "idx": 2, "icon": "☘", "src": []},
    "m": {"name": "Mineur", "color": "gray", "idx": 3, "icon": "⛏", "src": []},
    "c": {"name": "Chasseur", "color": "red", "idx": 4, "icon": "⚔", "src": []},
    "p": {"name": "Pêcheur", "color": "aqua", "idx": 5, "icon": "⚓", "src": []},
    "e": {"name": "Éleveur", "color": "light_purple", "idx": 6, "icon": "♞", "src": []},
    "n": {"name": "Enchanteur", "color": "dark_purple", "idx": 7, "icon": "✦", "src": []},
    "x": {"name": "Explorateur", "color": "blue", "idx": 8, "icon": "⛰", "src": []},
    "t": {"name": "Marchand", "color": "dark_green", "idx": 9, "icon": "⚖", "src": []},
}
# source : (critère, poids, signe, objectif, hooks)  ; hooks = [(compétence, prédicat chance, commande)]
for l in LOGS:
    jobs["b"]["src"].append((f"minecraft.mined:minecraft.{l}", 1, 1, f"b.mi.{l}",
                             [("b2", "chance_10", "give @s minecraft:apple 1"),
                              ("b3", "chance_25", f"give @s minecraft:{l} 1")]))
    jobs["b"]["src"].append((f"minecraft.used:minecraft.{l}", 1, -1, f"b.us.{l}", []))
for s, x in STONES.items():
    jobs["m"]["src"].append((f"minecraft.mined:minecraft.{s}", x, 1, f"m.mi.{s}", []))
    jobs["m"]["src"].append((f"minecraft.used:minecraft.{s}", x, -1, f"m.us.{s}", []))
for o, x in ORES.items():
    hooks = []
    base = o.replace("deepslate_", "").replace("_ore", "")
    if base in ORE_DROP:
        hooks = [("m3", "chance_25", f"give @s minecraft:{ORE_DROP[base]}")]
    jobs["m"]["src"].append((f"minecraft.mined:minecraft.{o}", x, 1, f"m.mi.{o}", hooks))
    jobs["m"]["src"].append((f"minecraft.used:minecraft.{o}", x, -1, f"m.us.{o}", []))
for c, x in CROPS.items():
    jobs["f"]["src"].append((f"minecraft.picked_up:minecraft.{c}", x, 1, f"f.pu.{c}",
                             [("f2", "chance_25", f"give @s minecraft:{c} 2"),
                              ("f4", "chance_03", "give @s minecraft:golden_apple 1")]))
    jobs["f"]["src"].append((f"minecraft.dropped:minecraft.{c}", x, -1, f"f.dr.{c}", []))
    if c in PLANTABLE:
        jobs["f"]["src"].append((f"minecraft.used:minecraft.{c}", x, -1, f"f.us.{c}", []))
# XP selon la créature tuée (mob_kills ne sert plus qu'à la compétence Soif de sang)
MOBS = {'chicken': 1, 'cow': 1, 'pig': 1, 'sheep': 1, 'rabbit': 1, 'goat': 1, 'mooshroom': 1, 'silverfish': 2, 'slime': 2, 'endermite': 2, 'magma_cube': 2, 'zombie': 3, 'husk': 3, 'zombie_villager': 3, 'spider': 3, 'piglin': 3, 'zombified_piglin': 2, 'drowned': 4, 'skeleton': 4, 'cave_spider': 4, 'vex': 4, 'stray': 5, 'bogged': 5, 'creeper': 5, 'phantom': 6, 'pillager': 6, 'witch': 8, 'enderman': 6, 'blaze': 7, 'guardian': 6, 'hoglin': 7, 'creaking': 8, 'vindicator': 9, 'shulker': 9, 'zoglin': 9, 'ghast': 11, 'wither_skeleton': 11, 'breeze': 11, 'iron_golem': 3, 'piglin_brute': 13, 'evoker': 15, 'ravager': 21}
for mob, x in MOBS.items():
    jobs["c"]["src"].append((f"minecraft.killed:minecraft.{mob}", x, 1, f"c.k.{mob}", []))
jobs["c"]["src"].append(("minecraft.custom:minecraft.mob_kills", 0, 1, "c.kills",
                         [("c3", None, "effect give @s minecraft:regeneration 3 1 true")]))
for b, x in BOSSES.items():
    jobs["c"]["src"].append((f"minecraft.killed:minecraft.{b}", x, 1, f"c.k.{b}", []))
jobs["p"]["src"].append(("minecraft.custom:minecraft.fish_caught", 8, 1, "p.fish",
                         [("p3", "chance_25", "loot give @s loot minecraft:gameplay/fishing/fish"),
                          ("p5", "chance_10", "loot give @s loot minecraft:gameplay/fishing/treasure")]))
# Éleveur : 2 points = 1 XP ; naissance 6 XP, laine ramassée 1/2 XP (poser ou jeter la laine la retire)
jobs["e"]["src"].append(("minecraft.custom:minecraft.animals_bred", 16, 1, "e.bred",
                         [("e2", "chance_30", "give @s minecraft:leather 2")]))
for wl in ("white", "black", "gray", "light_gray", "brown"):
    jobs["e"]["src"].append((f"minecraft.picked_up:minecraft.{wl}_wool", 1, 1, f"e.pu.{wl}",
                             [("e1", "chance_25", f"give @s minecraft:{wl}_wool 2")]))
    jobs["e"]["src"].append((f"minecraft.dropped:minecraft.{wl}_wool", 1, -1, f"e.dr.{wl}", []))
    jobs["e"]["src"].append((f"minecraft.used:minecraft.{wl}_wool", 1, -1, f"e.us.{wl}", []))
# Enchanteur : l'XP vient des niveaux dépensés (calcul à part), ce critère ne sert qu'aux compétences
jobs["n"]["src"].append(("minecraft.custom:minecraft.enchant_item", 0, 1, "n.ench",
                         [("n1", None, "xp add @s 1 levels"), ("n4", None, "xp add @s 1 levels"),
                          ("n2", None, "give @s minecraft:lapis_lazuli 4"),
                          ("n5", "chance_15", "loot give @s loot minecraft:chests/stronghold_library")]))
jobs["n"]["src"].append(("minecraft.crafted:minecraft.bookshelf", 2, 1, "n.shelf", []))
jobs["t"]["src"].append(("minecraft.custom:minecraft.traded_with_villager", 6, 1, "t.trade",
                         [("t1", "chance_20", "give @s minecraft:emerald 1"), ("t3", "chance_10", "give @s minecraft:diamond 1"),
                          ("t6", "chance_05", "give @s minecraft:netherite_scrap 1")]))
# Explorateur : distance parcourue, 1 XP tous les 10 m (traité à part)
XDIST = ["walk_one_cm", "sprint_one_cm", "crouch_one_cm", "aviate_one_cm", "horse_one_cm", "climb_one_cm"]

ALL_STATS = [s for j in jobs.values() for s in j["src"]]
WEIGHTS = sorted({s[1] for s in ALL_STATS} | {2, 3, 4, 10, 15, 20, 30, 40, 60, 100, 1000, 7200, 20000})

# =====================================================================
# ARBRES DE COMPÉTENCES (1 point par niveau, 49 points au niveau 50 = tout l'arbre)
# =====================================================================
SKILLS = {
    "b": [
        ("Poigne ferme", 3, [], "Haste I avec une hache en main."),
        ("Cueilleur", 4, [1], "10 % de chance d'obtenir une pomme en coupant du bois."),
        ("Double coupe", 6, [1], "25 % de chance de récupérer une bûche en plus."),
        ("Bras de fer", 8, [2], "Haste II avec une hache en main."),
        ("Abattage", 12, [3], "Accroupi avec une hache : casser une bûche abat tout l'arbre."),
        ("Esprit de la forêt", 16, [4, 5], "Force I et Résistance I avec une hache en main."),
    ],
    "f": [
        ("Pas léger", 3, [], "Vitesse I avec une houe en main."),
        ("Main verte", 4, [1], "25 % de chance de récolte doublée."),
        ("Estomac solide", 6, [1], "Rassasiement toutes les 60 secondes."),
        ("Main d'or", 8, [2], "3 % de chance d'obtenir une pomme dorée en récoltant."),
        ("Aura de croissance", 12, [3], "Toutes les 60 s, les cultures autour de toi (4 blocs) arrivent à maturité."),
        ("Mère Nature", 16, [4, 5], "Régénération I avec une houe en main."),
    ],
    "m": [
        ("Coup de pioche", 3, [], "Haste I avec une pioche en main."),
        ("Œil de lynx", 4, [1], "Vision nocturne sous la couche 40."),
        ("Filon chanceux", 6, [1], "25 % de chance de minerai en double."),
        ("Bras de fer", 8, [2], "Haste II avec une pioche en main."),
        ("Fonte automatique", 12, [3], "Le fer, l'or et le cuivre bruts se transforment en lingots dans ton inventaire."),
        ("Cœur de la montagne", 16, [4, 5], "Haste III avec une pioche et Résistance I sous la couche 40."),
    ],
    "c": [
        ("Lame affûtée", 3, [], "+1 point de dégâts en mêlée."),
        ("Pisteur", 4, [1], "Épée en main : les monstres à 16 blocs deviennent lumineux."),
        ("Soif de sang", 6, [1], "Chaque mob tué donne Régénération II pendant 3 s."),
        ("Cuir épais", 8, [2], "Résistance I en permanence."),
        ("Bourreau", 12, [3], "+2 points de dégâts supplémentaires."),
        ("Prédateur", 16, [4, 5], "Force I et Vitesse I quand un monstre est à moins de 8 blocs."),
    ],
    "p": [
        ("Patience", 3, [], "Chance +2 (meilleur butin de pêche)."),
        ("Poumons d'acier", 4, [1], "Respiration aquatique dans l'eau."),
        ("Prise double", 6, [1], "25 % de chance d'attraper un poisson en plus."),
        ("Nageur", 8, [2], "Grâce du dauphin dans l'eau."),
        ("Chasseur de trésors", 12, [3], "10 % de chance de pêcher un trésor en plus."),
        ("Seigneur des mers", 16, [4, 5], "Puissance de conduit dans l'eau et Chance +3."),
    ],
    "e": [
        ("Berger", 3, [], "25 % de chance de 2 laines en plus quand tu ramasses de la laine."),
        ("Tanneur", 4, [1], "30 % de chance de 2 cuirs à chaque naissance."),
        ("Ami des bêtes", 6, [1], "Les animaux à 6 blocs de toi se régénèrent."),
        ("Vitalité", 8, [2], "Absorption I toutes les 60 secondes."),
        ("Croissance rapide", 12, [3], "Toutes les 60 s, les bébés animaux autour de toi deviennent adultes."),
        ("Cavalier légendaire", 16, [4, 5], "Ta monture reçoit Vitesse II et Saut amélioré II."),
    ],
    "n": [
        ("Érudit", 3, [], "Chaque enchantement te rend 1 niveau d'XP."),
        ("Lapidaire", 4, [1], "Chaque enchantement te donne 4 lapis-lazuli."),
        ("Lapis éternel", 6, [1], "Toutes les 60 s, 8 lapis si tu en as moins de 16."),
        ("Économe", 8, [2], "Chaque enchantement te rend 1 niveau de plus."),
        ("Grimoire perdu", 12, [3], "15 % de chance de trouver un butin de bibliothèque en enchantant."),
        ("Archimage", 16, [4, 5], "Régénération I, Résistance I et Vision nocturne en permanence."),
    ],
    "x": [
        ("Pas léger", 3, [], "Vitesse I en permanence."),
        ("Bon pied", 4, [1], "Saut amélioré I en permanence."),
        ("Nyctalope", 6, [1], "Vision nocturne en permanence."),
        ("Coureur des bois", 8, [2], "Vitesse II en permanence."),
        ("Planeur", 12, [3], "Chute lente automatique quand tu tombes de haut."),
        ("Grand voyageur", 16, [4, 5], "Résistance au feu et Respiration aquatique en permanence."),
    ],
    "t": [
        ("Pourboire", 3, [], "20 % de chance d'une émeraude en plus par échange."),
        ("Réputation", 4, [1], "Héros du village I en permanence."),
        ("Marché noir", 6, [1], "10 % de chance d'un diamant par échange."),
        ("Notable", 8, [2], "Héros du village III en permanence."),
        ("Caravane", 12, [3], "Vitesse I et Chance II près des villageois."),
        ("Magnat", 16, [4, 5], "Héros du village V et 5 % de chance d'un fragment de netherite par échange."),
    ],
}

# niveau 100 : 99 points, coûts doublés pour finir l'arbre au niveau max
SKILLS = {j: [(n, c * 2, r, d) for (n, c, r, d) in v] for j, v in SKILLS.items()}

# =====================================================================
# TITRES (11 paliers)
# =====================================================================
TIERS = [("Apprenti", "1..9"), ("Initié", "10..19"), ("Compagnon", "20..29"), ("Artisan", "30..39"),
         ("Expert", "40..49"), ("Vétéran", "50..59"), ("Maître", "60..69"), ("Grand Maître", "70..79"),
         ("Légende", "80..89"), ("Mythique", "90..99"), ("Dieu", "100..")]
DE = ["de l'Apprenti", "de l'Initié", "du Compagnon", "de l'Artisan", "de l'Expert", "du Vétéran",
      "du Maître", "du Grand Maître", "de Légende", "Mythique", None]

def tier_style(j, t):
    col = jobs[j]["color"]
    return [{"color": "gray"}, {"color": "white"}, {"color": col}, {"color": col, "bold": True},
            {"color": "yellow", "bold": True}, {"color": "gold", "bold": True},
            {"color": "red", "bold": True}, {"color": "light_purple", "bold": True},
            {"color": "dark_purple", "bold": True}, {"color": "aqua", "bold": True},
            {"color": "dark_red", "bold": True}][t]

# =====================================================================
# RÉCOMPENSES DE PALIER (tous les 10 niveaux, à récupérer via un écran)
# =====================================================================
TOOL = {"b": ("axe", "Hache", "Hache du Dieu de la Forêt"), "m": ("pickaxe", "Pioche", "Pioche du Dieu de la Mine"),
        "f": ("hoe", "Houe", "Faux du Dieu des Moissons"), "c": ("sword", "Lame", "Lame du Dieu de la Chasse"),
        "p": ("fishing_rod", "Canne", "Canne du Dieu des Mers"), "e": ("shears", "Cisailles", "Cisailles du Dieu des Troupeaux"),
        "n": ("book", "Grimoire", "Grimoire du Dieu des Arcanes"), "x": ("boots", "Bottes", "Bottes du Dieu Voyageur"),
        "t": ("bundle", "Bourse", "Bourse du Dieu du Commerce")}
MAT = [None, "diamond", "diamond", "diamond", "diamond", "netherite", "netherite", "netherite", "netherite", "netherite", "netherite"]
MAIN = [None, 4, 5, 5, 5, 5, 6, 6, 6, 7, 8]
UNB = [None, 2, 3, 4, 5, None, None, None, None, None, None]
FORT = [None, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6]
LUCK = [None, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6]
EXTRAS = {
    "m": {1: ["iron_ingot 16", "coal 32"], 2: ["gold_ingot 16", "lapis_lazuli 32"], 3: ["diamond 5", "emerald 8"],
          4: ["iron_block 8", "redstone_block 8"], 5: ["diamond 12", "ancient_debris 2"],
          6: ["gold_block 8", "emerald_block 4"], 7: ["diamond_block 2", "netherite_scrap 4"],
          8: ["diamond_block 4", "ancient_debris 8"], 9: ["netherite_ingot 4", "emerald_block 16"],
          10: ["netherite_block 1", "diamond_block 8", "beacon 1"]},
    "b": {1: ["oak_log 64", "apple 16"], 2: ["cherry_log 64", "golden_apple 2"], 3: ["mangrove_log 64", "experience_bottle 32"],
          4: ["pale_oak_log 64", "golden_apple 6"], 5: ["totem_of_undying 1", "experience_bottle 64"],
          6: ["enchanted_golden_apple 1", "crimson_stem 64"], 7: ["enchanted_golden_apple 2", "warped_stem 64"],
          8: ["elytra 1", "golden_apple 16"], 9: ["enchanted_golden_apple 4", "experience_bottle 64"],
          10: ["enchanted_golden_apple 8", "totem_of_undying 2"]},
    "f": {1: ["bone_meal 64", "bread 32"], 2: ["golden_carrot 32", "cake 1"], 3: ["golden_carrot 64", "experience_bottle 32"],
          4: ["golden_apple 8", "glistering_melon_slice 16"], 5: ["enchanted_golden_apple 1", "hay_block 32"],
          6: ["golden_apple 16", "sniffer_egg 1"], 7: ["enchanted_golden_apple 3", "experience_bottle 64"],
          8: ["totem_of_undying 1", "golden_carrot 64"], 9: ["enchanted_golden_apple 5", "bone_block 32"],
          10: ["enchanted_golden_apple 10", "beacon 1"]},
    "c": {1: ["arrow 64", "golden_apple 4"], 2: ["bow{power:4,infinity:1,mending:1}Arc du Compagnon", "cooked_beef 32"],
          3: ["diamond_helmet{protection:4,unbreaking:3,mending:1}Casque de l'Artisan"],
          4: ["totem_of_undying 1", "experience_bottle 32"],
          5: ["diamond_chestplate{protection:4,unbreaking:3,mending:1}Plastron du Vétéran"],
          6: ["crossbow{quick_charge:3,multishot:1,mending:1}Arbalète du Maître", "enchanted_golden_apple 1"],
          7: ["diamond_leggings{protection:4,unbreaking:3,mending:1}Jambières du Grand Maître"],
          8: ["diamond_boots{protection:4,feather_falling:4,unbreaking:3,mending:1}Bottes de Légende", "totem_of_undying 1"],
          9: ["bow{power:5,infinity:1,flame:1,punch:2,mending:1}Arc Mythique", "enchanted_golden_apple 3"],
          10: ["totem_of_undying 3", "enchanted_golden_apple 5"]},
    "p": {1: ["cooked_salmon 32", "name_tag 2"], 2: ["saddle 1", "nautilus_shell 4"], 3: ["name_tag 4", "experience_bottle 32"],
          4: ["trident{loyalty:3,unbreaking:3,mending:1}Trident de l'Expert"], 5: ["heart_of_the_sea 1", "nautilus_shell 8"],
          6: ["turtle_helmet{respiration:3,aqua_affinity:1,unbreaking:3,mending:1}Casque du Maître", "saddle 1"],
          7: ["enchanted_golden_apple 2", "name_tag 4"],
          8: ["diamond_boots{depth_strider:3,frost_walker:2,unbreaking:3,mending:1}Bottes des Profondeurs"],
          9: ["trident{loyalty:3,impaling:5,channeling:1,unbreaking:3,mending:1}Trident Mythique"],
          10: ["conduit 1", "enchanted_golden_apple 5"]},
    "e": {1: ["wheat 32", "lead 4"], 2: ["saddle 1", "golden_carrot 16"], 3: ["name_tag 3", "hay_block 16"],
          4: ["golden_apple 6", "experience_bottle 32"], 5: ["diamond_horse_armor 1", "golden_carrot 32"],
          6: ["sniffer_egg 2", "enchanted_golden_apple 1"], 7: ["totem_of_undying 1", "golden_apple 12"],
          8: ["armadillo_scute 8", "enchanted_golden_apple 2"], 9: ["netherite_ingot 2", "experience_bottle 64"],
          10: ["enchanted_golden_apple 6", "beacon 1"]},
    "n": {1: ["lapis_lazuli 32", "book 16"], 2: ["bookshelf 15", "experience_bottle 32"], 3: ["lapis_block 6", "experience_bottle 48"],
          4: ["anvil 1", "diamond 8"], 5: ["experience_bottle 64", "enchanted_golden_apple 1"],
          6: ["lapis_block 16", "totem_of_undying 1"], 7: ["experience_bottle 64", "netherite_ingot 1"],
          8: ["enchanted_golden_apple 3", "diamond_block 2"], 9: ["netherite_ingot 3", "experience_bottle 64"],
          10: ["enchanted_golden_apple 6", "beacon 1"]},
    "x": {1: ["cooked_beef 32", "map 4"], 2: ["firework_rocket 32", "golden_apple 4"], 3: ["ender_pearl 8", "experience_bottle 32"],
          4: ["firework_rocket 64", "diamond 8"], 5: ["elytra 1", "firework_rocket 64"],
          6: ["ender_pearl 16", "enchanted_golden_apple 1"], 7: ["totem_of_undying 1", "firework_rocket 64"],
          8: ["shulker_box 1", "netherite_ingot 1"], 9: ["netherite_ingot 3", "enchanted_golden_apple 3"],
          10: ["enchanted_golden_apple 6", "beacon 1"]},
    "t": {1: ["emerald 16", "bread 32"], 2: ["emerald 32", "golden_apple 4"], 3: ["emerald_block 4", "experience_bottle 32"],
          4: ["emerald_block 8", "diamond 8"], 5: ["emerald_block 12", "enchanted_golden_apple 1"],
          6: ["bell 1", "emerald_block 16"], 7: ["totem_of_undying 1", "emerald_block 20"],
          8: ["netherite_ingot 2", "emerald_block 24"], 9: ["netherite_ingot 3", "emerald_block 32"],
          10: ["enchanted_golden_apple 6", "beacon 1"]},
}
UNSTACK = {"totem_of_undying", "saddle", "cake", "elytra", "diamond_horse_armor", "anvil", "bell", "shulker_box"}

def mk_item(iid, ench, name, color, unbreak):
    e = ",".join(f'"minecraft:{k}":{v}' for k, v in ench.items())
    cname = f'{{text:"{name}",color:"{color}",bold:true,italic:false}}'
    comps = {"minecraft:enchantments": f"{{{e}}}", "minecraft:custom_name": cname, "minecraft:rarity": '"epic"'}
    if unbreak:
        comps["minecraft:unbreakable"] = "{}"
    give = f"minecraft:{iid}[" + ",".join(f"{k}={v}" for k, v in comps.items()) + "] 1"
    stack = f'{{id:"minecraft:{iid}",count:1,components:{{' + ",".join(f'"{k}":{v}' for k, v in comps.items()) + "}}"
    return {"give": give, "stack": stack, "name": name, "color": color, "ench": ench, "unb": unbreak, "iid": iid}

FR = {"experience_bottle": "Fioles d'expérience", "golden_apple": "Pommes dorées", "diamond": "Diamants",
      "enchanted_golden_apple": "Pommes de Notch", "netherite_ingot": "Lingots de netherite",
      "totem_of_undying": "Totem d'immortalité", "beacon": "Balise", "golden_carrot": "Carottes dorées",
      "bone_meal": "Poudre d'os", "heart_of_the_sea": "Cœur de la mer", "conduit": "Conduit",
      "netherite_block": "Bloc de netherite", "elytra": "Élytres", "iron_ingot": "Lingots de fer", "coal": "Charbon",
      "gold_ingot": "Lingots d'or", "lapis_lazuli": "Lapis-lazuli", "emerald": "Émeraudes", "iron_block": "Blocs de fer",
      "redstone_block": "Blocs de redstone", "ancient_debris": "Débris antiques", "gold_block": "Blocs d'or",
      "emerald_block": "Blocs d'émeraude", "diamond_block": "Blocs de diamant", "netherite_scrap": "Fragments de netherite",
      "oak_log": "Bûches de chêne", "apple": "Pommes", "cherry_log": "Bûches de cerisier", "mangrove_log": "Bûches de palétuvier",
      "pale_oak_log": "Bûches de chêne pâle", "crimson_stem": "Tiges carmin", "warped_stem": "Tiges biscornues",
      "bread": "Pains", "cake": "Gâteau", "glistering_melon_slice": "Pastèques scintillantes", "hay_block": "Bottes de foin",
      "sniffer_egg": "Œuf de renifleur", "bone_block": "Blocs d'os", "arrow": "Flèches", "cooked_beef": "Steaks",
      "cooked_salmon": "Saumons cuits", "name_tag": "Étiquettes", "saddle": "Selle", "nautilus_shell": "Coquilles de nautile",
      "wheat": "Blé", "lead": "Laisses", "diamond_horse_armor": "Armure de cheval en diamant", "armadillo_scute": "Écailles de tatou",
      "book": "Livres", "bookshelf": "Bibliothèques", "lapis_block": "Blocs de lapis", "anvil": "Enclume",
      "map": "Cartes", "firework_rocket": "Fusées", "ender_pearl": "Perles de l'Ender", "shulker_box": "Boîte de Shulker",
      "bell": "Cloche"}

ENCH_FR = {"soul_speed": "Agilité des âmes","efficiency": "Efficacité", "fortune": "Fortune", "unbreaking": "Solidité", "mending": "Raccommodage",
           "sharpness": "Tranchant", "looting": "Butin", "sweeping_edge": "Affilage", "fire_aspect": "Aura de feu",
           "luck_of_the_sea": "Chance de la mer", "lure": "Appât", "power": "Puissance", "infinity": "Infinité",
           "flame": "Flamme", "punch": "Frappe", "protection": "Protection", "feather_falling": "Chute amortie",
           "quick_charge": "Charge rapide", "multishot": "Tir multiple", "loyalty": "Loyauté", "impaling": "Empalement",
           "channeling": "Canalisation", "respiration": "Apnée", "aqua_affinity": "Affinité aquatique",
           "depth_strider": "Agilité aquatique", "frost_walker": "Semelles givrantes", "silk_touch": "Toucher de soie"}
ROM = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

def ench_txt(it):
    if not it["ench"] and not it.get("unb"):
        return "Emblème du métier"
    parts = [f"{ENCH_FR.get(e, e)}{'' if v == 1 and e in ('mending', 'infinity', 'flame', 'multishot', 'channeling', 'aqua_affinity', 'silk_touch') else ' ' + ROM[v]}"
             for e, v in it["ench"].items()]
    if it.get("unb"):
        parts.append("Incassable")
    return ", ".join(parts)

def simple(spec):
    iid, n = spec.split(); n = int(n)
    reps, cnt = (n, 1) if iid in UNSTACK else (1, n)
    return [{"give": f"minecraft:{iid} {cnt}", "stack": f'{{id:"minecraft:{iid}",count:{cnt}}}',
             "name": None, "color": None, "label": f"{cnt} x {FR.get(iid, iid.replace('_', ' '))}"} for _ in range(reps)]

def special(spec, color, tier=None):
    head, name = spec.split("}")
    iid, ench_s = head.split("{")
    ench, unb = {}, False
    for part in ench_s.split(","):
        if part == "unbreakable":
            unb = True
        else:
            k, v = part.split(":"); ench[k] = int(v)
    if tier and not unb and UNB[tier]:
        ench["unbreaking"] = UNB[tier]
    return [mk_item(iid, ench, name, color, unb)]

def rewards(j, k):
    tool, nom, dieu = TOOL[j]
    color = tier_style(j, k)["color"]
    iid = f"{MAT[k]}_{tool}" if j in ("b", "m", "f", "c", "x") else tool
    if j in ("n", "t"):
        ench = {}
    elif j == "x":
        ench = {"feather_falling": min(4, 1 + k // 2), "protection": min(4, 1 + k // 3)}
        if k >= 3: ench["depth_strider"] = min(3, k // 3)
        if k >= 6: ench["soul_speed"] = 3
    elif j == "e":
        ench = {"efficiency": MAIN[k]}
    elif j == "p":
        ench = {"luck_of_the_sea": LUCK[k], "lure": [0, 2, 3, 3, 4, 4, 4, 5, 5, 5, 5][k]}
    elif j == "c":
        ench = {"sharpness": MAIN[k], "looting": min(FORT[k], 3) + (k // 4)}
        if k >= 4: ench["sweeping_edge"] = 3
        if k >= 5: ench["fire_aspect"] = 2
    else:
        ench = {"efficiency": MAIN[k]}
        if j in ("m", "f"): ench["fortune"] = FORT[k]
        if j == "b" and k >= 5: ench["sharpness"] = 5
    if UNB[k]: ench["unbreaking"] = UNB[k]
    name = dieu if k == 10 else f"{nom} {DE[k]}"
    out = [mk_item(iid, ench, name, color, k >= 5 or j == "x")]
    for s in EXTRAS[j][k]:
        out += special(s, color, k) if "{" in s else simple(s)
    return out

R = {j: {k: rewards(j, k) for k in range(1, 11)} for j in jobs}


def prefix_component(j, t):
    st = dict(tier_style(j, t)); st["text"] = f"{TIERS[t][0]} {jobs[j]['name']}"
    return json.dumps(st, ensure_ascii=False)

def team_prefix(j, t, st=0):
    parts = [{"text": "", "color": "white"}]
    if st:
        parts.append({"text": "★" * st + " ", "color": "gold", "bold": False})
    if t == 10:
        parts.append({"text": "a", "color": "gold", "obfuscated": True})
    st = dict(tier_style(j, t)); st["text"] = f"{jobs[j]['icon']} {TIERS[t][0]}"
    parts.append(st)
    if t == 10:
        parts.append({"text": "a", "color": "gold", "obfuscated": True})
    parts.append({"text": " ", "color": "white", "bold": False})
    return json.dumps(parts, ensure_ascii=False)

PREFIX = "[{\"text\":\"[Métiers] \",\"color\":\"gold\"}"

# =====================================================================
# PACK, TAGS, PRÉDICATS
# =====================================================================
wj("pack.mcmeta", {"pack": {"description": "Métiers v2 : niveaux, compétences, titres",
                            "min_format": 84, "max_format": 200}})
wj("data/minecraft/tags/function/load.json", {"values": [f"{NS}:load"]})
wj("data/minecraft/tags/function/tick.json", {"values": [f"{NS}:tick"]})



ANIMAUX = ["cow", "mooshroom", "sheep", "pig", "chicken", "horse", "donkey", "mule", "llama", "goat", "rabbit",
           "camel", "turtle", "frog", "armadillo", "sniffer", "wolf", "cat", "fox", "bee", "panda", "hoglin", "strider"]
wj(f"data/{NS}/tags/entity_type/animaux.json", {"values": [{"id": f"minecraft:{a}", "required": False} for a in ANIMAUX]})
HOSTILES = ["zombie", "husk", "drowned", "zombie_villager", "skeleton", "stray", "bogged", "wither_skeleton",
            "creeper", "spider", "cave_spider", "enderman", "witch", "slime", "magma_cube", "blaze", "ghast",
            "phantom", "pillager", "vindicator", "evoker", "ravager", "vex", "hoglin", "zoglin", "piglin_brute",
            "guardian", "elder_guardian", "silverfish", "endermite", "shulker", "breeze", "creaking", "warden"]
wj(f"data/{NS}/tags/entity_type/hostiles.json",
   {"values": [{"id": f"minecraft:{h}", "required": False} for h in HOSTILES]})
wj(f"data/{NS}/tags/item/epees.json",
   {"values": [{"id": f"minecraft:{m}_sword", "required": False}
               for m in ("wooden", "stone", "copper", "iron", "golden", "diamond", "netherite")]})

WITH_G = True
if WITH_G:
    # dialogue de la touche G et du menu Échap
    def hub_btn(txt, col, val, wdt=150):
        return {"label": {"text": txt, "color": col}, "width": wdt,
                "action": {"type": "run_command", "command": f"trigger metiers set {val}"}}
    hub = [hub_btn("Mes métiers", "gold", 1)]
    hub += [hub_btn(f"{d['icon']} {d['name']}", d["color"], 20 + d["idx"]) for d in jobs.values()]
    hub += [hub_btn("Mon titre", "yellow", 2), hub_btn("Récompenses", "light_purple", 3),
            hub_btn("Défis du jour", "aqua", 4), hub_btn("Classement", "gold", 5), hub_btn("Armure des Guildes", "#F1CF4E", 6, 304)]
    wj(f"data/{NS}/dialog/ouvrir.json", {
        "type": "minecraft:multi_action",
        "title": {"text": "Métiers", "color": "gold", "bold": True},
        "external_title": {"text": "Métiers"},
        "can_close_with_escape": True,
        "pause": False,
        "body": [{"type": "minecraft:plain_message", "width": 300,
                  "contents": {"text": "Tes niveaux, l'arbre de compétences de chaque métier, ton titre et tes récompenses.", "color": "gray"}}],
        "actions": hub,
        "columns": 2,
    })
    wj("data/minecraft/tags/dialog/quick_actions.json", {"values": [f"{NS}:ouvrir"]})
    wj("data/minecraft/tags/dialog/pause_screen_additions.json", {"values": [f"{NS}:ouvrir"]})


DEFIS = {
    "b": [("Coupe 128 bûches de chêne", 128, ["minecraft.mined:minecraft.oak_log"], 1),
          ("Coupe 128 bûches de sapin", 128, ["minecraft.mined:minecraft.spruce_log"], 1),
          ("Coupe 128 bûches de bouleau", 128, ["minecraft.mined:minecraft.birch_log"], 1),
          ("Coupe 96 bûches de chêne noir", 96, ["minecraft.mined:minecraft.dark_oak_log"], 1),
          ("Coupe 256 bûches, toutes essences", 256, [f"minecraft.mined:minecraft.{l}" for l in LOGS], 1)],
    "f": [("Récolte 192 blés", 192, ["minecraft.picked_up:minecraft.wheat"], 1),
          ("Récolte 160 carottes", 160, ["minecraft.picked_up:minecraft.carrot"], 1),
          ("Récolte 160 pommes de terre", 160, ["minecraft.picked_up:minecraft.potato"], 1),
          ("Récolte 96 cannes à sucre", 96, ["minecraft.picked_up:minecraft.sugar_cane"], 1),
          ("Fais naître 12 animaux", 12, ["minecraft.custom:minecraft.animals_bred"], 1)],
    "m": [("Mine 512 blocs de pierre", 512, ["minecraft.mined:minecraft.stone"], 1),
          ("Mine 256 blocs de deepslate", 256, ["minecraft.mined:minecraft.deepslate"], 1),
          ("Mine 24 minerais de fer", 24, ["minecraft.mined:minecraft.iron_ore", "minecraft.mined:minecraft.deepslate_iron_ore"], 1),
          ("Mine 48 minerais de charbon", 48, ["minecraft.mined:minecraft.coal_ore", "minecraft.mined:minecraft.deepslate_coal_ore"], 1),
          ("Mine 4 minerais de diamant", 4, ["minecraft.mined:minecraft.diamond_ore", "minecraft.mined:minecraft.deepslate_diamond_ore"], 1)],
    "c": [("Élimine 60 créatures", 60, ["minecraft.custom:minecraft.mob_kills"], 1),
          ("Élimine 25 zombies", 25, ["minecraft.killed:minecraft.zombie"], 1),
          ("Élimine 25 squelettes", 25, ["minecraft.killed:minecraft.skeleton"], 1),
          ("Élimine 12 creepers", 12, ["minecraft.killed:minecraft.creeper"], 1),
          ("Élimine 10 endermen", 10, ["minecraft.killed:minecraft.enderman"], 1)],
    "p": [("Pêche 20 poissons", 20, ["minecraft.custom:minecraft.fish_caught"], 1),
          ("Pêche 35 poissons", 35, ["minecraft.custom:minecraft.fish_caught"], 1),
          ("Parcours 1000 m en bateau", 1000, ["minecraft.custom:minecraft.boat_one_cm"], 100),
          ("Nage 500 m", 500, ["minecraft.custom:minecraft.swim_one_cm"], 100),
          ("Pêche 50 poissons", 50, ["minecraft.custom:minecraft.fish_caught"], 1)],
    "e": [("Fais naître 10 animaux", 10, ["minecraft.custom:minecraft.animals_bred"], 1),
          ("Fais naître 20 animaux", 20, ["minecraft.custom:minecraft.animals_bred"], 1),
          ("Récolte 32 laines blanches", 32, ["minecraft.picked_up:minecraft.white_wool"], 1),
          ("Fais naître 30 animaux", 30, ["minecraft.custom:minecraft.animals_bred"], 1),
          ("Récolte 64 laines blanches", 64, ["minecraft.picked_up:minecraft.white_wool"], 1)],
    "n": [("Enchante 3 objets", 3, ["minecraft.custom:minecraft.enchant_item"], 1),
          ("Enchante 4 objets", 4, ["minecraft.custom:minecraft.enchant_item"], 1),
          ("Enchante 5 objets", 5, ["minecraft.custom:minecraft.enchant_item"], 1),
          ("Enchante 6 objets", 6, ["minecraft.custom:minecraft.enchant_item"], 1),
          ("Enchante 8 objets", 8, ["minecraft.custom:minecraft.enchant_item"], 1)],
    "x": [("Marche 3000 m", 3000, ["minecraft.custom:minecraft.walk_one_cm"], 100),
          ("Sprinte 2000 m", 2000, ["minecraft.custom:minecraft.sprint_one_cm"], 100),
          ("Parcours 5000 m à pied", 5000, ["minecraft.custom:minecraft.walk_one_cm", "minecraft.custom:minecraft.sprint_one_cm"], 100),
          ("Vole 5000 m en élytres", 5000, ["minecraft.custom:minecraft.aviate_one_cm"], 100),
          ("Parcours 3000 m à cheval", 3000, ["minecraft.custom:minecraft.horse_one_cm"], 100)],
    "t": [("Fais 10 échanges", 10, ["minecraft.custom:minecraft.traded_with_villager"], 1),
          ("Fais 15 échanges", 15, ["minecraft.custom:minecraft.traded_with_villager"], 1),
          ("Fais 20 échanges", 20, ["minecraft.custom:minecraft.traded_with_villager"], 1),
          ("Fais 25 échanges", 25, ["minecraft.custom:minecraft.traded_with_villager"], 1),
          ("Fais 30 échanges", 30, ["minecraft.custom:minecraft.traded_with_villager"], 1)],
}
BARCOL = {"b": "yellow", "f": "green", "m": "white", "c": "red", "p": "blue", "e": "pink", "n": "purple", "x": "blue", "t": "green"}
NJ = len(jobs)


# =====================================================================
# LOAD / TICK / LOOP
# =====================================================================
L = ["scoreboard objectives add m.tmp dummy", "scoreboard objectives add m.gain dummy",
     "scoreboard objectives add m.const dummy", "scoreboard objectives add m.timer dummy",
     "scoreboard objectives add m.pref dummy", "scoreboard objectives add m.trig dummy",
     'scoreboard objectives add metiers trigger "Menu métiers"']
for j in jobs:
    for k in ("lvl", "xp", "need", "bal", "spent", "pal", "pr", "out", "cd", "st"):
        L.append(f"scoreboard objectives add m.{j}_{k} dummy")
    L += [f"scoreboard objectives add m.dp_{j} dummy", f"scoreboard objectives add m.dd_{j} dummy"]
for crit, _, _, obj, _ in ALL_STATS:
    L.append(f"scoreboard objectives add s.{obj} {crit}")
for l in LOGS:
    L.append(f"scoreboard objectives add a.{l} minecraft.mined:minecraft.{l}")
L.append("scoreboard objectives add a.sneak minecraft.custom:minecraft.sneak_time")
L.append("scoreboard objectives add m.quit minecraft.custom:minecraft.leave_game")
for o in ("m.id", "m.dshow", "m.dall", "m.defi", "m.heure", "m.boss", "m.total"):
    L.append(f"scoreboard objectives add {o} dummy")
L.append("scoreboard objectives add m.dmg minecraft.custom:minecraft.damage_dealt")
L.append("scoreboard objectives add m.dur dummy")
L.append("scoreboard objectives add m.x_acc dummy")
L += [f"scoreboard objectives add m.{j}_raw dummy" for j in DIV]
L += ["scoreboard objectives add m.n_now dummy", "scoreboard objectives add m.n_prev dummy"]
L += [f"scoreboard objectives add m.p_{o} dummy" for o in ("serie", "timer", "mul", "aff", "pluie", "nuit", "ocean", "legok")]
L += [f"scoreboard objectives add m.p_l{i} dummy" for i in range(1, 11)]
L += ["scoreboard objectives add m.arm dummy", "scoreboard objectives add m.acd dummy", "scoreboard objectives add m.aser dummy"]
L += [f"scoreboard objectives add m.{j}_ser dummy" for j in jobs]
for st in XDIST:
    L.append(f"scoreboard objectives add s.x.{st} minecraft.custom:minecraft.{st}")
for j, pool in DEFIS.items():
    for i, (desc, tgt, crits, div) in enumerate(pool, 1):
        for n, cr in enumerate(crits):
            L.append(f"scoreboard objectives add dq.{j}{i}_{n} {cr}")
L += ["scoreboard players add #job m.heure 0", "scoreboard players add #cycle m.heure 0",
      "scoreboard players add #actif m.boss 0", "scoreboard players add #compte m.boss 0", "scoreboard players add #cycle m.boss 0",
      'bossbar add metiers:heure ""', "bossbar set metiers:heure max 3600", "bossbar set metiers:heure visible false",
      'bossbar add metiers:boss {"text":"Le Colosse des Métiers","color":"dark_red","bold":true}',
      "bossbar set metiers:boss color red", "bossbar set metiers:boss style notched_20", "bossbar set metiers:boss max 600",
      "execute unless score #actif m.boss matches 1 run bossbar set metiers:boss visible false",
      "execute in minecraft:overworld run forceload add 0 0"]
for wgt in WEIGHTS:
    L.append(f"scoreboard players set #{wgt} m.const {wgt}")
L += [f'function {NS}:cmd {{c:"gamerule sendCommandFeedback false"}}',
      f'function {NS}:cmd {{c:"gamerule send_command_feedback false"}}',
      f"execute unless data storage {NS}:cl {{v2:1b}} run data remove storage {NS}:cl joueurs[].nom",
      f"data modify storage {NS}:cl v2 set value 1b",
      f"function {NS}:prefixe/equipes", "tag @a add metiers.maj",
      f"schedule function {NS}:loop 10t replace",
      'tellraw @a ' + PREFIX + ',{"text":"Datapack v11 chargé. Tape ","color":"gray"},{"text":"/trigger metiers","color":"yellow"}]']
w(F + "load.mcfunction", "\n".join(L))

w(F + "cmd.mcfunction", "$$(c)")
w(F + "tick.mcfunction", f"""
execute as @a[scores={{metiers=1..}}] at @s run function {NS}:trigger
execute as @a[tag=metiers.sk.b5] at @s run function {NS}:b/abattage/tick
function {NS}:appel {{f:"outil/usure_tick"}}
""")
w(F + "outil/usure_tick.mcfunction", f"execute as @a at @s run function {NS}:outil/usure")
w(F + "outil/usure.mcfunction", "\n".join([
    'execute unless data entity @s SelectedItem.components."minecraft:custom_data".metiers_outil run return 0',
    'execute if data entity @s SelectedItem.components."minecraft:custom_data".verrou run return run title @s actionbar {"text":"✖ Outil à réparer ! Appuie sur G, choisis ton métier puis « Réparer mon outil ».","color":"red","bold":true}',
    'execute if data entity @s SelectedItem.components."minecraft:unbreakable" run return 0',
    'execute unless data entity @s SelectedItem.components."minecraft:custom_data".max run return 0',
    'execute store result score @s m.tmp run data get entity @s SelectedItem.components."minecraft:custom_data".max',
    'execute store result score @s m.dur run data get entity @s SelectedItem.components."minecraft:damage"',
    "scoreboard players operation @s m.tmp -= @s m.dur",
    f"execute if score @s m.tmp matches ..3 run function {NS}:outil/verrouiller"]))
w(F + "outil/verrouiller.mcfunction", "\n".join([
    f'data modify storage {NS}:tmp cd set from entity @s SelectedItem.components."minecraft:custom_data"',
    f"data modify storage {NS}:tmp cd.verrou set value 1b",
    'item modify entity @s weapon.mainhand {function:"minecraft:set_components",type:"minecraft:set_components",components:{"minecraft:unbreakable":{},"!minecraft:tool":{},"!minecraft:weapon":{}}}',
    f"function {NS}:outil/verrou_m with storage {NS}:tmp",
    "playsound minecraft:block.anvil.land master @s ~ ~ ~ 0.6 1.2",
    'tellraw @s ' + PREFIX + ',{"text":"Ton outil est à bout (3 de durabilité) : il est bloqué pour ne pas se casser. Appuie sur G, choisis ton métier puis « Réparer mon outil » (5 niveaux d\'XP). L\'enclume et le Raccommodage ne marchent pas sur les outils de métier.","color":"red"}]']))
w(F + "outil/verrou_m.mcfunction", '$item modify entity @s weapon.mainhand {function:"minecraft:set_custom_data",type:"minecraft:set_custom_data",tag:$(cd)}')

w(F + "loop.mcfunction", f"""
scoreboard players add #t m.timer 1
scoreboard players operation #pair m.timer = #t m.timer
scoreboard players operation #pair m.timer %= #2 m.const
scoreboard players operation #quatre m.timer = #t m.timer
scoreboard players operation #quatre m.timer %= #4 m.const
scoreboard players operation #huit m.timer = #t m.timer
scoreboard players operation #huit m.timer %= #8 m.const
scoreboard players operation #soixante m.timer = #t m.timer
scoreboard players operation #soixante m.timer %= #60 m.const
function {NS}:appel {{f:"heure/tick"}}
function {NS}:appel {{f:"defis/tick"}}
function {NS}:appel {{f:"boss/tick"}}
execute as @a[tag=!metiers.ok] run function {NS}:init
execute as @a at @s run function {NS}:joueur
execute if score #t m.timer matches 120.. run scoreboard players set #t m.timer 0
schedule function {NS}:loop 10t replace
""")

J = [f"execute unless entity @s[tag=metiers.v2] run function {NS}:migration",
     f"execute unless entity @s[tag=metiers.v3] run function {NS}:succes_sync",
     f"execute unless entity @s[tag=metiers.v5] run function {NS}:relance_paliers",
     f"execute unless entity @s[tag=metiers.v4] run function {NS}:connexion",
     f"tag @s add metiers.v4",
     f"execute if score @s m.quit matches 1.. run function {NS}:connexion",
     f"execute unless score @s m.id matches 1.. run function {NS}:id",
     f"execute unless entity @s[tag=metiers.v7] run function {NS}:migration6",
     f'execute unless entity @s[tag=metiers.v9] run function {NS}:appel {{f:"migration8"}}',
     f'execute unless entity @s[tag=metiers.v13] run function {NS}:appel {{f:"migration13"}}',
     f'execute unless entity @s[tag=metiers.v22] run function {NS}:appel {{f:"migration22"}}']
for j in jobs:
    J.append(f"execute if score @s m.{j}_cd matches 1.. run scoreboard players remove @s m.{j}_cd 1")
J += [f'execute if score #quatre m.timer matches 0 run function {NS}:appel {{f:"outil/check"}}',
      f'execute if score #pair m.timer matches 0 run function {NS}:appel {{f:"defis/joueur"}}',
      f'function {NS}:appel {{f:"armure/bonus"}}',
      f'execute if score #quatre m.timer matches 0 run function {NS}:appel {{f:"securite/check"}}',
      "execute if score @s m.acd matches 1.. run scoreboard players remove @s m.acd 1",
      f'execute if score #soixante m.timer matches 0 run function {NS}:appel {{f:"classement/maj"}}']
for j in jobs:
    J.append(f"execute unless score @s m.{j}_lvl matches 1.. run function {NS}:{j}/init")
for j in jobs:
    J.append(f"function {NS}:{j}/stats")
J += [f"function {NS}:bonus", "scoreboard players add @s m.pref 0",
      "scoreboard players enable @s metiers",
      f"execute if entity @s[tag=metiers.maj] run function {NS}:prefixe/maj"]
w(F + "joueur.mcfunction", "\n".join(J))

# init (nouveau joueur) et migration (joueur de la v1, garde ses niveaux)
I = []
for j in jobs:
    I += [f"scoreboard players set @s m.{j}_lvl 1", f"scoreboard players set @s m.{j}_xp 0",
          f"scoreboard players set @s m.{j}_need 50", f"scoreboard players set @s m.{j}_bal 0"]
for _, _, _, obj, _ in ALL_STATS:
    I.append(f"scoreboard players set @s s.{obj} 0")
I += ["tag @s add metiers.ok",
      'tellraw @s ' + PREFIX + ',{"text":"Bienvenue ! 5 métiers jusqu\'au niveau 50, avec compétences et titres. Tape ","color":"gray"},{"text":"/trigger metiers","color":"yellow"}]']
w(F + "init.mcfunction", "\n".join(I))
for j in jobs:
    w(F + f"{j}/init.mcfunction", "\n".join(
        [f"scoreboard players set @s m.{j}_{k} {v}" for k, v in
         (("lvl", 1), ("xp", 0), ("need", 50), ("bal", 0), ("spent", 0), ("pal", 0), ("pr", 0), ("out", 0), ("cd", 0))] +
        ["scoreboard players set @s m.x_acc 0"]))

M = ["tag @s add metiers.v2",
     "attribute @s minecraft:attack_damage modifier remove metiers:chasseur",
     "attribute @s minecraft:luck modifier remove metiers:pecheur"]
for j in jobs:
    M += [f"scoreboard players add @s m.{j}_spent 0", f"scoreboard players add @s m.{j}_pal 0"]
M.append('tellraw @s ' + PREFIX + ',{"text":"Nouveau : niveau max 100, arbres de compétences (1 point par niveau déjà gagné) et récompenses de palier à récupérer. Ouvre le menu avec la touche G ou dans le menu Échap.","color":"yellow"}]')
M.append(f"function {NS}:recompenses")
w(F + "migration.mcfunction", "\n".join(M))

# =====================================================================
# DISPATCH DU TRIGGER
# =====================================================================
T = ["scoreboard players operation @s m.trig = @s metiers",
     "scoreboard players set @s metiers 0",
     "scoreboard players enable @s metiers",
     f"execute if score @s m.trig matches 1 run function {NS}:menu",
     f"execute if score @s m.trig matches 2 run function {NS}:prefixe/menu",
     f"execute if score @s m.trig matches 3 unless function {NS}:recompenses run tellraw @s " + PREFIX + ',{"text":"Aucune récompense en attente.","color":"gray"}]',
     f"execute if score @s m.trig matches 10..19 run function {NS}:prefixe/choisir",
     f'execute if score @s m.trig matches 4 run function {NS}:appel {{f:"defis/menu"}}',
     f'execute if score @s m.trig matches 5 run function {NS}:appel {{f:"classement/menu"}}',
     f'execute if score @s m.trig matches 7 run function {NS}:appel {{f:"defis/basculer"}}',
     f'execute if score @s m.trig matches 6 run function {NS}:appel {{f:"armure/menu"}}',
     f'execute if score @s m.trig matches 8 run function {NS}:appel {{f:"armure/recup"}}',
     f'execute if score @s m.trig matches 70 run function {NS}:appel {{f:"p/carnet"}}']
for j, d in jobs.items():
    T += [f'execute if score @s m.trig matches {300 + d["idx"]} run function {NS}:appel {{f:"{j}/outil_recup"}}',
          f'execute if score @s m.trig matches {310 + d["idx"]} run function {NS}:appel {{f:"{j}/prestige_confirmer"}}',
          f'execute if score @s m.trig matches {320 + d["idx"]} run function {NS}:appel {{f:"{j}/prestige"}}',
          f'execute if score @s m.trig matches {330 + d["idx"]} run function {NS}:appel {{f:"{j}/outil_reparer"}}',
          f'execute if score @s m.trig matches {340 + d["idx"]} run function {NS}:appel {{f:"{j}/recompenses_menu"}}']
for j, d in jobs.items():
    T.append(f"execute if score @s m.trig matches {20 + d['idx']} run function {NS}:{j}/arbre")
    T.append(f"execute if score @s m.trig matches {200 + d['idx']} run function {NS}:{j}/reclamer")
    for k in range(1, 7):
        T.append(f"execute if score @s m.trig matches {100 + 10 * d['idx'] + k} run function {NS}:{j}/acheter_{k}")
w(F + "trigger.mcfunction", "\n".join(T))

POS = {1: "Base", 2: "Branche A", 3: "Branche B", 4: "Branche A", 5: "Branche B", 6: "Ultime"}

# =====================================================================
# PAR MÉTIER : stats, gain, niveau, paliers, arbre
# =====================================================================
for j, d in jobs.items():
    S = ["# Anti-triche : poser ou jeter l'objet retire l'XP gagnée"]
    for _, wgt, sign, obj, hooks in d["src"]:
        for sk, pred, cmd in hooks:
            cond = f"execute if entity @s[tag=metiers.sk.{sk}] if score @s s.{obj} matches 1.."
            if pred:
                S.append(f"{cond} store result score #r m.tmp run random value 1..100")
                cond += f" if score #r m.tmp matches ..{int(pred.split('_')[1])}"
            S.append(f"{cond} run {cmd}")
        op = "+=" if sign > 0 else "-="
        cible = f"m.{j}_raw" if j in DIV else f"m.{j}_bal"
        if wgt == 0:
            pass
        elif wgt == 1:
            S.append(f"scoreboard players operation @s {cible} {op} @s s.{obj}")
        else:
            S += [f"scoreboard players operation @s m.tmp = @s s.{obj}",
                  f"scoreboard players operation @s m.tmp *= #{wgt} m.const",
                  f"scoreboard players operation @s {cible} {op} @s m.tmp"]
        S.append(f"scoreboard players set @s s.{obj} 0")
    if j in DIV:
        S += [f"execute if score @s m.{j}_raw matches {DIV[j]}.. run scoreboard players operation @s m.tmp = @s m.{j}_raw",
              f"execute if score @s m.{j}_raw matches {DIV[j]}.. run scoreboard players operation @s m.tmp /= #{DIV[j]} m.const",
              f"execute if score @s m.{j}_raw matches {DIV[j]}.. run scoreboard players operation @s m.{j}_bal += @s m.tmp",
              f"execute if score @s m.{j}_raw matches {DIV[j]}.. run scoreboard players operation @s m.tmp *= #{DIV[j]} m.const",
              f"execute if score @s m.{j}_raw matches {DIV[j]}.. run scoreboard players operation @s m.{j}_raw -= @s m.tmp"]
    if j == "p":
        S = (["scoreboard players add @s m.p_timer 1",
              f'execute if score @s s.p.fish matches 1.. run function {NS}:appel {{f:"p/peche"}}'] + S)
    if j == "n":
        # XP selon les niveaux d'expérience dépensés à la table (1, 2 ou 3 niveaux => 15, 30 ou 45 XP)
        S = (["execute store result score @s m.n_now run experience query @s levels",
              "execute unless score @s m.n_prev matches 0.. run scoreboard players operation @s m.n_prev = @s m.n_now",
              f"execute if score @s s.n.ench matches 1.. run function {NS}:n/enchant"] + S +
             ["execute store result score @s m.n_prev run experience query @s levels"])
    if j == "x":
        for st in XDIST:
            if st == "aviate_one_cm":
                S += [f"scoreboard players operation @s s.x.{st} /= #3 m.const"]
            if st == "horse_one_cm":
                S += [f"scoreboard players operation @s s.x.{st} /= #2 m.const"]
            S += [f"scoreboard players operation @s m.x_acc += @s s.x.{st}", f"scoreboard players set @s s.x.{st} 0"]
        # XP versée par tranche de 200 m (20 XP d'un coup) pour éviter un message tous les 10 m
        S += ["scoreboard players operation @s m.tmp = @s m.x_acc", "scoreboard players operation @s m.tmp /= #20000 m.const",
              "scoreboard players operation @s m.tmp *= #20 m.const",
              "scoreboard players operation @s m.x_bal += @s m.tmp", "scoreboard players operation @s m.x_acc %= #20000 m.const"]
    S.append(f"execute if score @s m.{j}_bal matches 1.. run function {NS}:{j}/gain")
    if j == "p":
        S.append(f'execute if score @s m.p_aff matches 1 run function {NS}:appel {{f:"p/affiche"}}')
    w(F + f"{j}/stats.mcfunction", "\n".join(S))

    w(F + f"{j}/gain.mcfunction", f"""
scoreboard players operation @s m.gain = @s m.{j}_bal
scoreboard players set @s m.{j}_bal 0
scoreboard players operation @s m.tmp = @s m.gain
scoreboard players operation @s m.tmp *= @s m.{j}_pr
scoreboard players operation @s m.tmp /= #10 m.const
scoreboard players operation @s m.gain += @s m.tmp
execute if score #job m.heure matches {d['idx']} run scoreboard players operation @s m.gain *= #2 m.const
execute if score @s m.{j}_lvl matches {MAXLVL}.. run return 0
scoreboard players operation @s m.{j}_xp += @s m.gain
function {NS}:{j}/check
title @s actionbar [{{"text":"+","color":"green"}},{{"score":{{"name":"@s","objective":"m.gain"}},"color":"green"}},{{"text":" XP {d['name']}","color":"{d['color']}"}},{{"text":"  |  niv ","color":"gray"}},{{"score":{{"name":"@s","objective":"m.{j}_lvl"}},"color":"white"}},{{"text":"  (","color":"gray"}},{{"score":{{"name":"@s","objective":"m.{j}_xp"}},"color":"white"}},{{"text":"/","color":"gray"}},{{"score":{{"name":"@s","objective":"m.{j}_need"}},"color":"white"}},{{"text":")","color":"gray"}}]
""")

    w(F + f"{j}/check.mcfunction", f"""
scoreboard players operation @s m.{j}_need = @s m.{j}_lvl
scoreboard players operation @s m.{j}_need *= #10 m.const
scoreboard players operation @s m.{j}_need += #40 m.const
execute if score @s m.{j}_lvl matches ..{MAXLVL-1} if score @s m.{j}_xp >= @s m.{j}_need run function {NS}:{j}/levelup
""")

    LV = [f"scoreboard players operation @s m.{j}_xp -= @s m.{j}_need",
          f"scoreboard players add @s m.{j}_lvl 1",
          "xp add @s 2 levels",
          "playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1",
          f'tellraw @a [{{"selector":"@s","color":"white"}},{{"text":" passe ","color":"gray"}},{{"text":"{d["name"]}","color":"{d["color"]}"}},{{"text":" niveau ","color":"gray"}},{{"score":{{"name":"@s","objective":"m.{j}_lvl"}},"color":"yellow"}}]',
          f'tellraw @s ' + PREFIX + f',{{"text":"+1 point de compétence {d["name"]}.","color":"yellow"}}]']
    for t in range(1, 11):
        LV.append(f'execute if score @s m.{j}_lvl matches {10*t} run tellraw @a ' + PREFIX +
                  f',{{"selector":"@s","color":"white"}},{{"text":" débloque le titre ","color":"gray"}},{prefix_component(j, t)}]')
    LV += ["tag @s add metiers.maj",
           f"execute if score @s m.{j}_lvl matches {MAXLVL} run scoreboard players set @s m.{j}_xp 0"]
    for t in range(1, 11):
        LV.append(f'execute if score @s m.{j}_lvl matches {10*t} run function {NS}:appel {{f:"{j}/outil_monte"}}')
        LV.append(f"execute if score @s m.{j}_lvl matches {10*t} run function {NS}:recompenses")
    for t in range(1, 11):
        LV.append(f"execute if score @s m.{j}_lvl matches {10*t} run advancement grant @s only {NS}:{j}/niveau_{10*t}")
    LV.append(f"function {NS}:{j}/check")
    w(F + f"{j}/levelup.mcfunction", "\n".join(LV))

    # récompenses : m.X_pal = dernier palier récupéré, rétroactif
    AT_, RC = [], []
    for k in range(1, 11):
        cond = f"execute if score @s m.{j}_pal matches {k-1} if score @s m.{j}_lvl matches {10*k}.."
        AT_.append(f'{cond} run return run function {NS}:afficher {{j:"{j}",k:{k}}}')
        RC.append(f'{cond} run return run function {NS}:donner {{j:"{j}",k:{k}}}')
    AT_.append("return 0")
    RC.append('tellraw @s ' + PREFIX + ',{"text":"Aucune récompense en attente.","color":"gray"}]')
    w(F + f"{j}/attente.mcfunction", "\n".join(AT_))
    w(F + f"{j}/reclamer.mcfunction", "\n".join(RC))
    for k in range(1, 11):
        lv, items = 10 * k, R[j][k]
        n = len(items) - 1
        trig = 200 + d["idx"]
        main = items[0]
        body = [f'{{type:"minecraft:plain_message",width:300,contents:[{{text:"Bravo ! ",color:"gold",bold:true}},'
                f'{{text:"Tu as atteint le niveau {lv} en ",color:"white"}},{{text:"{d["name"]}",color:"{d["color"]}",bold:true}},'
                f'{{text:".\\nVoici ta récompense :",color:"white"}}]}}']
        lignes = []
        for ii, it in enumerate(items):
            if it["name"]:
                pre = "Ton outil a évolué : " if ii == 0 else ""
                lignes.append(f'{{text:"\\n• {pre}{it["name"]}",color:"{it["color"]}",bold:true}},{{text:"\\n   {ench_txt(it)}",color:"dark_aqua",bold:false}}')
            else:
                lignes.append(f'{{text:"\\n• {it["label"]}",color:"white",bold:false}}')
        body.append('{type:"minecraft:plain_message",width:320,contents:[{text:""},' + ",".join(lignes) + ']}')
        body.append(f'{{type:"minecraft:plain_message",width:300,contents:{{text:"Il te faut {n} emplacement{"s" if n > 1 else ""} libre{"s" if n > 1 else ""} dans ton inventaire.",color:"gray"}}}}')
        dlg = (f'dialog show @s {{type:"minecraft:confirmation",title:{{text:"Palier {lv} : {TIERS[k][0]} {d["name"]}",color:"gold",bold:true}},'
               f'can_close_with_escape:true,pause:false,body:[{",".join(body)}],'
               f'yes:{{label:{{text:"Récupérer",color:"green",bold:true}},width:150,action:{{type:"run_command",command:"trigger metiers set {trig}"}}}},'
               f'no:{{label:{{text:"Plus tard",color:"gray"}},width:150}}}}')
        chat = ('tellraw @s ' + PREFIX + f',{{"text":"Récompense du palier {lv} {d["name"]} disponible ! ","color":"yellow"}},'
                f'{{"text":"[Récupérer]","color":"green","bold":true,"click_event":{{"action":"run_command","command":"/trigger metiers set {trig}"}}}}]')
        w(F + f"{j}/notif_{k}.mcfunction", "\n".join(["playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1", chat]))
        w(F + f"{j}/ecran_{k}.mcfunction", dlg)
        G = [f"function {NS}:places",
             f'execute if score @s m.tmp matches ..{n-1} run tellraw @s ' + PREFIX + f',{{"text":"Inventaire plein ! Libère {n} emplacement{"s" if n > 1 else ""} puis réessaie (/trigger metiers > Récompenses).","color":"red"}}]',
             f"execute if score @s m.tmp matches ..{n-1} run playsound minecraft:entity.villager.no master @s ~ ~ ~ 1 1",
             f"execute if score @s m.tmp matches ..{n-1} run return 0",
             f"scoreboard players set @s m.{j}_pal {k}"]
        G += [f"give @s {it['give']}" for it in items[1:]]
        G += [f'tellraw @a ' + PREFIX + f',{{"selector":"@s","color":"white"}},{{"text":" récupère sa récompense","color":"gray"}},{{"text":" (palier {lv} {d["name"]})","color":"gray"}}]',
              "playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 0.6",
              "particle minecraft:totem_of_undying ~ ~1 ~ 0.5 1 0.5 0.3 60",
              f"function {NS}:recompenses"]
        w(F + f"{j}/donner_{k}.mcfunction", "\n".join(G))

    # points disponibles = niveau - 1 - dépensés
    w(F + f"{j}/points.mcfunction", f"""
scoreboard players operation @s m.tmp = @s m.{j}_lvl
scoreboard players remove @s m.tmp 1
scoreboard players operation @s m.tmp -= @s m.{j}_spent
""")

    sk = SKILLS[j]
    def reqsel(req):
        return ",".join(f"tag=metiers.sk.{j}{r}" for r in req)

    A = [f"function {NS}:{j}/points",
         f"execute store result storage {NS}:arbre pts int 1 run scoreboard players get @s m.tmp"]
    for k, (name, cost, req, desc) in enumerate(sk, 1):
        cond = f"execute if entity @s[{reqsel(req)}]" if req else "execute if entity @s"
        A += [f'data modify storage {NS}:arbre l{k} set value "✖  {POS[k]} · {name}   ({cost} pts)"',
              f'data modify storage {NS}:arbre c{k} set value "dark_gray"',
              f'{cond} run data modify storage {NS}:arbre l{k} set value "{POS[k]} · {name}   ({cost} pts)"',
              f'{cond} run data modify storage {NS}:arbre c{k} set value "yellow"',
              f'{cond} if score @s m.tmp matches ..{cost-1} run data modify storage {NS}:arbre c{k} set value "red"',
              f'execute if entity @s[tag=metiers.sk.{j}{k}] run data modify storage {NS}:arbre l{k} set value "✔  {POS[k]} · {name}"',
              f'execute if entity @s[tag=metiers.sk.{j}{k}] run data modify storage {NS}:arbre c{k} set value "green"']
    A.append(f"function {NS}:{j}/arbre_dialog with storage {NS}:arbre")
    w(F + f"{j}/arbre.mcfunction", "\n".join(A))

    n = [s[0] for s in sk]
    branches = f"{n[0]} > {n[1]} > {n[3]}\\n{n[0]} > {n[2]} > {n[4]}\\nUltime : {n[5]} ({n[3]} + {n[4]})"
    btns = {}
    for k, (name, cost, req, desc) in enumerate(sk, 1):
        rq = " + ".join(sk[r-1][0] for r in req) if req else "rien"
        btns[k] = (f'{{label:{{text:"$(l{k})",color:"$(c{k})"}},'
                    f'tooltip:{{text:"{desc}\\nCoût : {cost} points\\nRequiert : {rq}"}},width:300,'
                    f'action:{{type:"run_command",command:"trigger metiers set {100 + 10*d["idx"] + k}"}}}}').replace("width:300", "width:130")
    def vide(t=""):
        return f'{{label:{{text:"{t}",color:"dark_gray"}},width:130}}'
    liste = [btns[i].replace("width:130", "width:280") for i in (1, 2, 4, 3, 5, 6)]
    liste.append(f'{{label:{{text:"Récupérer mon outil",color:"aqua"}},width:280,tooltip:{{text:"Redonne ton outil de métier à son palier actuel (une fois toutes les 10 minutes)."}},action:{{type:"run_command",command:"trigger metiers set {300 + d["idx"]}"}}}}')
    if j == "p":
        liste.append('{label:{text:"Carnet du pêcheur (légendes)",color:"aqua"},width:280,action:{type:"run_command",command:"trigger metiers set 70"}}')
    liste.append(f'{{label:{{text:"Récompenses du métier",color:"light_purple"}},width:280,tooltip:{{text:"Tout ce que tu gagnes à chaque palier de 10 niveaux."}},action:{{type:"run_command",command:"trigger metiers set {340 + d["idx"]}"}}}}')
    liste.append(f'{{label:{{text:"Réparer mon outil (5 niv. d\'XP)",color:"green"}},width:280,tooltip:{{text:"Seule façon de réparer ton outil de métier (enclume et Raccommodage bloqués). Coût : 5 niveaux d\'XP. Incassable à partir du niveau 50."}},action:{{type:"run_command",command:"trigger metiers set {330 + d["idx"]}"}}}}')
    liste.append(f'{{label:{{text:"★ Prestige",color:"gold"}},width:280,tooltip:{{text:"Au niveau 100 : repars au niveau 1 avec une étoile et +10 % d\'XP par étoile (5 max)."}},action:{{type:"run_command",command:"trigger metiers set {310 + d["idx"]}"}}}}')
    grille = [vide(), btns[1], vide(),
              vide("↙"), vide(), vide("↘"),
              btns[2], vide(), btns[3],
              vide("↓"), vide(), vide("↓"),
              btns[4], vide(), btns[5],
              vide("↘"), vide(), vide("↙"),
              vide(), btns[6], vide()]
    w(F + f"{j}/arbre_dialog.mcfunction",
      f'$dialog show @s {{type:"minecraft:multi_action",title:{{text:"Compétences {d["name"]}",color:"{d["color"]}",bold:true}},'
      f'can_close_with_escape:true,pause:false,after_action:"none",body:[{{type:"minecraft:plain_message",width:400,contents:['
      f'{{text:"Points disponibles : ",color:"gray"}},{{text:"$(pts)",color:"yellow",bold:true}},'
      f'{{text:"   (1 point par niveau)\\nSurvole une compétence pour voir son effet.\\n\\n",color:"gray"}},{{text:"{branches}",color:"dark_aqua"}},{{text:"\\n\\nArbre visuel : touche L, onglet {d["name"]}.",color:"dark_gray"}}]}}],'
      f'actions:[{",".join(liste)}],columns:1,'
      f'exit_action:{{label:"Retour",width:150,action:{{type:"run_command",command:"trigger metiers set 1"}}}}}}')

    for k, (name, cost, req, desc) in enumerate(sk, 1):
        B = [f"execute if entity @s[tag=metiers.sk.{j}{k}] run return run function {NS}:{j}/arbre",
             f"function {NS}:{j}/points"]
        if req:
            B += [f'execute unless entity @s[{reqsel(req)}] run tellraw @s ' + PREFIX + f',{{"text":"Il faut d\'abord débloquer : {" + ".join(sk[r-1][0] for r in req)}.","color":"red"}}]',
                  f"execute unless entity @s[{reqsel(req)}] run return run function {NS}:{j}/arbre"]
        B += [f'execute if score @s m.tmp matches ..{cost-1} run tellraw @s ' + PREFIX + f',{{"text":"Pas assez de points ({cost} requis).","color":"red"}}]',
              f"execute if score @s m.tmp matches ..{cost-1} run return run function {NS}:{j}/arbre",
              f"scoreboard players add @s m.{j}_spent {cost}",
              f"tag @s add metiers.sk.{j}{k}",
              f"advancement grant @s only {NS}:{j}/competence_{k}",
              f'tellraw @a ' + PREFIX + f',{{"selector":"@s","color":"white"}},{{"text":" débloque la compétence ","color":"gray"}},{{"text":"{name}","color":"{d["color"]}","bold":true}}]',
              "playsound minecraft:block.enchantment_table.use master @s ~ ~ ~ 1 1"]
        if j == "b" and k == 5:
            B += [f"scoreboard players set @s a.{l} 0" for l in LOGS]
        B.append(f"function {NS}:{j}/arbre")
        w(F + f"{j}/acheter_{k}.mcfunction", "\n".join(B))

# =====================================================================
# EFFETS DES COMPÉTENCES (lancé toutes les 0,5 s, positionné sur le joueur)
# =====================================================================
w(F + "bonus.mcfunction", f"""
# Bûcheron
execute if entity @s[tag=metiers.sk.b1] if items entity @s weapon.mainhand #minecraft:axes run effect give @s minecraft:haste 2 0 true
execute if entity @s[tag=metiers.sk.b4] if items entity @s weapon.mainhand #minecraft:axes run effect give @s minecraft:haste 2 1 true
execute if entity @s[tag=metiers.sk.b6] if items entity @s weapon.mainhand #minecraft:axes run effect give @s minecraft:strength 2 0 true
execute if entity @s[tag=metiers.sk.b6] if items entity @s weapon.mainhand #minecraft:axes run effect give @s minecraft:resistance 2 0 true

# Mineur
execute if entity @s[tag=metiers.sk.m1] if items entity @s weapon.mainhand #minecraft:pickaxes run effect give @s minecraft:haste 2 0 true
execute if entity @s[tag=metiers.sk.m4] if items entity @s weapon.mainhand #minecraft:pickaxes run effect give @s minecraft:haste 2 1 true
execute if entity @s[tag=metiers.sk.m6] if items entity @s weapon.mainhand #minecraft:pickaxes run effect give @s minecraft:haste 2 2 true
execute if entity @s[tag=metiers.sk.m2,y=-64,dy=103] run effect give @s minecraft:night_vision 15 0 true
execute if entity @s[tag=metiers.sk.m6,y=-64,dy=103] run effect give @s minecraft:resistance 2 0 true
execute if entity @s[tag=metiers.sk.m5] run function {NS}:m/fonte

# Fermier
execute if entity @s[tag=metiers.sk.f1] if items entity @s weapon.mainhand #minecraft:hoes run effect give @s minecraft:speed 2 0 true
execute if entity @s[tag=metiers.sk.f3] if score #t m.timer matches 120 run effect give @s minecraft:saturation 1 0 true
execute if entity @s[tag=metiers.sk.f5] if score #t m.timer matches 120 run function {NS}:f/aura
execute if entity @s[tag=metiers.sk.f6] if items entity @s weapon.mainhand #minecraft:hoes run effect give @s minecraft:regeneration 3 0 true

# Chasseur
attribute @s minecraft:attack_damage modifier remove {NS}:c1
attribute @s minecraft:attack_damage modifier remove {NS}:c5
execute if entity @s[tag=metiers.sk.c1] run attribute @s minecraft:attack_damage modifier add {NS}:c1 1 add_value
execute if entity @s[tag=metiers.sk.c5] run attribute @s minecraft:attack_damage modifier add {NS}:c5 2 add_value
execute if entity @s[tag=metiers.sk.c2] if items entity @s weapon.mainhand #{NS}:epees run effect give @e[type=#{NS}:hostiles,distance=..16] minecraft:glowing 2 0 true
execute if entity @s[tag=metiers.sk.c4] run effect give @s minecraft:resistance 2 0 true
execute if entity @s[tag=metiers.sk.c6] if entity @e[type=#{NS}:hostiles,distance=..8] run effect give @s minecraft:strength 2 0 true
execute if entity @s[tag=metiers.sk.c6] if entity @e[type=#{NS}:hostiles,distance=..8] run effect give @s minecraft:speed 2 0 true

# Pêcheur
attribute @s minecraft:luck modifier remove {NS}:p1
attribute @s minecraft:luck modifier remove {NS}:p6
execute if entity @s[tag=metiers.sk.p1] run attribute @s minecraft:luck modifier add {NS}:p1 2 add_value
execute if entity @s[tag=metiers.sk.p6] run attribute @s minecraft:luck modifier add {NS}:p6 3 add_value
execute if entity @s[tag=metiers.sk.p2] if block ~ ~ ~ minecraft:water run effect give @s minecraft:water_breathing 3 0 true
execute if entity @s[tag=metiers.sk.p4] if block ~ ~ ~ minecraft:water run effect give @s minecraft:dolphins_grace 2 0 true
execute if entity @s[tag=metiers.sk.p6] if block ~ ~ ~ minecraft:water run effect give @s minecraft:conduit_power 3 0 true

# Éleveur
execute if entity @s[tag=metiers.sk.e3] run effect give @e[type=#{NS}:animaux,distance=..6] minecraft:regeneration 3 0 true
execute if entity @s[tag=metiers.sk.e4] if score #t m.timer matches 120 run effect give @s minecraft:absorption 60 0 true
execute if entity @s[tag=metiers.sk.e5] if score #t m.timer matches 120 run function {NS}:e/croissance
execute if entity @s[tag=metiers.sk.e6] on vehicle run effect give @s minecraft:speed 2 1 true
execute if entity @s[tag=metiers.sk.e6] on vehicle run effect give @s minecraft:jump_boost 2 1 true

# Enchanteur
execute if entity @s[tag=metiers.sk.n3] if score #t m.timer matches 120 run function {NS}:n/lapis
execute if entity @s[tag=metiers.sk.n6] run effect give @s minecraft:regeneration 3 0 true
execute if entity @s[tag=metiers.sk.n6] run effect give @s minecraft:resistance 2 0 true
execute if entity @s[tag=metiers.sk.n6] run effect give @s minecraft:night_vision 15 0 true

# Explorateur
execute if entity @s[tag=metiers.sk.x1] run effect give @s minecraft:speed 2 0 true
execute if entity @s[tag=metiers.sk.x4] run effect give @s minecraft:speed 2 1 true
execute if entity @s[tag=metiers.sk.x2] run effect give @s minecraft:jump_boost 2 0 true
execute if entity @s[tag=metiers.sk.x3] run effect give @s minecraft:night_vision 15 0 true
execute if entity @s[tag=metiers.sk.x5] run function {NS}:x/planeur
execute if entity @s[tag=metiers.sk.x6] run effect give @s minecraft:fire_resistance 3 0 true
execute if entity @s[tag=metiers.sk.x6] run effect give @s minecraft:water_breathing 3 0 true

# Marchand
execute if entity @s[tag=metiers.sk.t2] run effect give @s minecraft:hero_of_the_village 3 0 true
execute if entity @s[tag=metiers.sk.t4] run effect give @s minecraft:hero_of_the_village 3 2 true
execute if entity @s[tag=metiers.sk.t6] run effect give @s minecraft:hero_of_the_village 3 4 true
execute if entity @s[tag=metiers.sk.t5] if entity @e[type=minecraft:villager,distance=..16] run effect give @s minecraft:speed 2 0 true
execute if entity @s[tag=metiers.sk.t5] if entity @e[type=minecraft:villager,distance=..16] run effect give @s minecraft:luck 2 1 true
""")
w(F + "e/croissance.mcfunction", f"""
execute as @e[type=#{NS}:animaux,distance=..8] store result score @s m.tmp run data get entity @s Age
execute as @e[type=#{NS}:animaux,distance=..8] if score @s m.tmp matches ..-2 run data modify entity @s Age set value -1
particle minecraft:happy_villager ~ ~1 ~ 4 1 4 0 30
""")
w(F + "n/lapis.mcfunction", """
execute store result score @s m.tmp run clear @s minecraft:lapis_lazuli 0
execute if score @s m.tmp matches ..15 run give @s minecraft:lapis_lazuli 8
""")
w(F + "n/enchant.mcfunction", """
scoreboard players operation @s m.tmp = @s m.n_prev
scoreboard players operation @s m.tmp -= @s m.n_now
execute if score @s m.tmp matches ..0 run scoreboard players set @s m.tmp 1
execute if score @s m.tmp matches 4.. run scoreboard players set @s m.tmp 3
scoreboard players operation @s m.tmp *= #20 m.const
scoreboard players operation @s m.n_bal += @s m.tmp
""")
w(F + "x/planeur.mcfunction", """
execute store result score @s m.tmp run data get entity @s FallDistance
execute if score @s m.tmp matches 6.. run effect give @s minecraft:slow_falling 2 0 true
""")

# Mineur : fonte automatique
w(F + "m/fonte.mcfunction", f"""
execute store result score @s m.tmp run clear @s minecraft:raw_iron 0
execute if score @s m.tmp matches 1.. run function {NS}:m/fonte_item {{raw:"raw_iron",out:"iron_ingot"}}
execute store result score @s m.tmp run clear @s minecraft:raw_gold 0
execute if score @s m.tmp matches 1.. run function {NS}:m/fonte_item {{raw:"raw_gold",out:"gold_ingot"}}
execute store result score @s m.tmp run clear @s minecraft:raw_copper 0
execute if score @s m.tmp matches 1.. run function {NS}:m/fonte_item {{raw:"raw_copper",out:"copper_ingot"}}
""")
w(F + "m/fonte_item.mcfunction", f"""
$data modify storage {NS}:fonte out set value "$(out)"
$execute store result storage {NS}:fonte n int 1 run clear @s minecraft:$(raw)
function {NS}:m/fonte_give with storage {NS}:fonte
playsound minecraft:block.furnace.fire_crackle master @s ~ ~ ~ 0.6 1.2
""")
w(F + "m/fonte_give.mcfunction", "$give @s minecraft:$(out) $(n)")

# Fermier : aura de croissance
w(F + "f/aura.mcfunction", """
fill ~-4 ~-2 ~-4 ~4 ~2 ~4 minecraft:wheat[age=7] replace minecraft:wheat
fill ~-4 ~-2 ~-4 ~4 ~2 ~4 minecraft:carrots[age=7] replace minecraft:carrots
fill ~-4 ~-2 ~-4 ~4 ~2 ~4 minecraft:potatoes[age=7] replace minecraft:potatoes
fill ~-4 ~-2 ~-4 ~4 ~2 ~4 minecraft:beetroots[age=3] replace minecraft:beetroots
fill ~-4 ~-2 ~-4 ~4 ~2 ~4 minecraft:nether_wart[age=3] replace minecraft:nether_wart
fill ~-4 ~-2 ~-4 ~4 ~2 ~4 minecraft:sweet_berry_bush[age=3] replace minecraft:sweet_berry_bush
particle minecraft:happy_villager ~ ~0.5 ~ 3 0.5 3 0 40
playsound minecraft:block.amethyst_block.chime master @s ~ ~ ~ 1 1.2
""")

# Bûcheron : abattage (accroupi + hache), détection au tick puis rayon depuis les yeux
AT = ["scoreboard players set #sum m.tmp 0"]
AT += [f"scoreboard players operation #sum m.tmp += @s a.{l}" for l in LOGS]
AT += [f"scoreboard players set @s a.{l} 0" for l in LOGS]
AT.append(f"execute if score #sum m.tmp matches 1.. if score @s a.sneak matches 1.. if items entity @s weapon.mainhand #minecraft:axes run function {NS}:b/abattage/debut")
AT.append("scoreboard players set @s a.sneak 0")
w(F + "b/abattage/tick.mcfunction", "\n".join(AT))
w(F + "b/abattage/debut.mcfunction", f"""
scoreboard players set #pas m.tmp 0
execute anchored eyes positioned ^ ^ ^0.5 run function {NS}:b/abattage/rayon
""")
w(F + "b/abattage/rayon.mcfunction", f"""
scoreboard players add #pas m.tmp 1
execute if block ~ ~ ~ minecraft:air if block ~ ~1 ~ #minecraft:logs positioned ~ ~1 ~ align xyz run return run function {NS}:b/abattage/demarrer
execute if score #pas m.tmp matches ..55 positioned ^ ^ ^0.1 run function {NS}:b/abattage/rayon
""")
w(F + "b/abattage/demarrer.mcfunction", f"""
scoreboard players set #n m.tmp 0
function {NS}:b/abattage/bloc
playsound minecraft:block.wood.break master @a ~ ~ ~ 1 0.7
scoreboard players operation @s m.b_bal += #n m.tmp
""")
NB = ["~ ~1 ~", "~1 ~ ~", "~-1 ~ ~", "~ ~ ~1", "~ ~ ~-1", "~ ~-1 ~",
      "~1 ~1 ~", "~-1 ~1 ~", "~ ~1 ~1", "~ ~1 ~-1", "~1 ~1 ~1", "~1 ~1 ~-1", "~-1 ~1 ~1", "~-1 ~1 ~-1"]
BL = ["execute if score #n m.tmp matches 150.. run return 0",
      "setblock ~ ~ ~ minecraft:air destroy",
      "scoreboard players add #n m.tmp 1"]
BL += [f"execute positioned {o} if block ~ ~ ~ #minecraft:logs run function {NS}:b/abattage/bloc" for o in NB]
w(F + "b/abattage/bloc.mcfunction", "\n".join(BL))

w(F + "places.mcfunction", "scoreboard players set @s m.tmp 0\n" + "\n".join(
    f"execute unless items entity @s container.{i} * run scoreboard players add @s m.tmp 1" for i in range(36)))
w(F + "afficher.mcfunction", f"$function {NS}:notif_m {{j:\"$(j)\",k:$(k)}}\n$function {NS}:ecran_m {{j:\"$(j)\",k:$(k)}}\nreturn 1")
w(F + "notif_m.mcfunction", f"$function {NS}:$(j)/notif_$(k)")
w(F + "ecran_m.mcfunction", f"$function {NS}:$(j)/ecran_$(k)")
w(F + "donner.mcfunction", f"$function {NS}:$(j)/donner_$(k)\nreturn 1")
w(F + "relance_paliers.mcfunction", "tag @s add metiers.v5\ntag @s remove metiers.v4\n" + "\n".join(f"scoreboard players set @s m.{j}_pal 0" for j in jobs))
w(F + "connexion.mcfunction", f"scoreboard players set @s m.quit 0\nfunction {NS}:recompenses")
w(F + "recompenses.mcfunction", "\n".join([f"execute if function {NS}:{j}/attente run return 1" for j in jobs] + ["return 0"]))

ICONS_SK = {"b": ["iron_axe", "apple", "oak_log", "golden_axe", "diamond_axe", "oak_sapling"],
            "f": ["iron_hoe", "wheat_seeds", "bread", "golden_apple", "bone_meal", "flowering_azalea"],
            "m": ["iron_pickaxe", "spyglass", "raw_iron", "golden_pickaxe", "furnace", "diamond_pickaxe"],
            "c": ["iron_sword", "spectral_arrow", "redstone", "leather_chestplate", "diamond_sword", "wither_skeleton_skull"],
            "p": ["fishing_rod", "turtle_helmet", "cod", "prismarine_crystals", "heart_of_the_sea", "conduit"],
            "e": ["shears", "leather", "golden_carrot", "milk_bucket", "wheat", "saddle"],
            "n": ["lapis_lazuli", "bookshelf", "experience_bottle", "enchanting_table", "enchanted_book", "nether_star"],
            "x": ["leather_boots", "rabbit_foot", "ender_eye", "feather", "elytra", "compass"],
            "t": ["emerald", "bell", "diamond", "emerald_block", "map", "totem_of_undying"]}
BG = {"b": "minecraft:block/oak_planks", "f": "minecraft:block/hay_block_side", "m": "minecraft:block/stone",
      "c": "minecraft:block/nether_bricks", "p": "minecraft:block/prismarine_bricks"}
ROOT_ICON = {"b": "oak_log", "f": "wheat", "m": "iron_ore", "c": "skeleton_skull", "p": "cod",
             "e": "lead", "n": "enchanting_table", "x": "filled_map", "t": "emerald"}
BG.update({"e": "minecraft:block/hay_block_top", "n": "minecraft:block/bookshelf", "x": "minecraft:block/moss_block",
           "t": "minecraft:block/emerald_block"})
LVL_FIXE = {"p": "fishing_rod", "e": "shears", "n": "book", "x": "compass", "t": "emerald"}
LVL_ICON = ["wooden", "stone", "iron", "iron", "golden", "golden", "diamond", "diamond", "netherite", "netherite"]
TOOLI = {"b": "axe", "f": "hoe", "m": "pickaxe", "c": "sword"}
IMP = {"debloque": {"trigger": "minecraft:impossible"}}
SY = ["tag @s add metiers.v3"]
for j, d in jobs.items():
    A_ = f"data/{NS}/advancement/{j}/"
    wj(A_ + "racine.json", {"display": {"icon": {"id": f"minecraft:{ROOT_ICON[j]}"},
        "title": {"text": d["name"], "color": d["color"], "bold": True},
        "description": {"text": "Compétences et paliers du métier. Touche G pour ouvrir le menu.", "color": "gray"},
        "frame": "task", "background": BG[j], "show_toast": False, "announce_to_chat": False},
        "criteria": {"tick": {"trigger": "minecraft:tick"}}})
    parents = {1: "racine", 2: "competence_1", 3: "competence_1", 4: "competence_2", 5: "competence_3", 6: "competence_4"}
    for k, (name, cost, req, desc) in enumerate(SKILLS[j], 1):
        rq = " + ".join(SKILLS[j][r-1][0] for r in req) if req else "rien"
        wj(A_ + f"competence_{k}.json", {"parent": f"{NS}:{j}/{parents[k]}",
            "display": {"icon": {"id": f"minecraft:{ICONS_SK[j][k-1]}"},
                        "title": {"text": name, "color": d["color"]},
                        "description": {"text": f"{desc}\nCoût : {cost} points\nRequiert : {rq}", "color": "gray"},
                        "frame": "challenge" if k == 6 else ("goal" if k >= 4 else "task"),
                        "show_toast": True, "announce_to_chat": False},
            "criteria": IMP})
        SY.append(f"execute if entity @s[tag=metiers.sk.{j}{k}] run advancement grant @s only {NS}:{j}/competence_{k}")
    for t in range(1, 11):
        lv = 10 * t
        icon = (f"{LVL_ICON[t-1]}_{TOOLI[j]}" if j in TOOLI else LVL_FIXE[j])
        wj(A_ + f"niveau_{lv}.json", {"parent": f"{NS}:{j}/" + ("racine" if t == 1 else f"niveau_{lv-10}"),
            "display": {"icon": {"id": f"minecraft:{icon}"},
                        "title": {"text": f"{TIERS[t][0]} {d['name']}", "color": tier_style(j, t)["color"]},
                        "description": {"text": f"Atteindre le niveau {lv}.", "color": "gray"},
                        "frame": "challenge" if t == 10 else ("goal" if t % 5 == 0 else "task"),
                        "show_toast": True, "announce_to_chat": False},
            "criteria": IMP})
        SY.append(f"execute if score @s m.{j}_lvl matches {lv}.. run advancement grant @s only {NS}:{j}/niveau_{lv}")
w(F + "succes_sync.mcfunction", "\n".join(SY))

# =====================================================================
# MENUS
# =====================================================================
MD = []
for j, d in jobs.items():
    MD += [f'data modify storage {NS}:menu {j}_st set value ""'] + [
           f'execute if score @s m.{j}_pr matches {st} run data modify storage {NS}:menu {j}_st set value "{"★" * st} "' for st in range(1, 6)]
    MD += [f"execute store result storage {NS}:menu {j}_lvl int 1 run scoreboard players get @s m.{j}_lvl",
           f"execute store result storage {NS}:menu {j}_xp int 1 run scoreboard players get @s m.{j}_xp",
           f"execute store result storage {NS}:menu {j}_need int 1 run scoreboard players get @s m.{j}_need",
           f"function {NS}:{j}/points",
           f"execute store result storage {NS}:menu {j}_pts int 1 run scoreboard players get @s m.tmp",
           f"scoreboard players operation @s m.tmp = @s m.{j}_xp",
           f"scoreboard players operation @s m.tmp *= #10 m.const",
           f"scoreboard players operation @s m.tmp /= @s m.{j}_need",
           f"execute if score @s m.{j}_lvl matches {MAXLVL}.. run scoreboard players set @s m.tmp 10"]
    for k in range(11):
        MD.append(f'execute if score @s m.tmp matches {k} run data modify storage {NS}:menu {j}_b1 set value "{"■" * k}"')
        MD.append(f'execute if score @s m.tmp matches {k} run data modify storage {NS}:menu {j}_b2 set value "{"■" * (10 - k)}"')
    for t, (nom, rng) in enumerate(TIERS):
        MD.append(f'execute if score @s m.{j}_lvl matches {rng} run data modify storage {NS}:menu {j}_t set value "{nom}"')
w(F + "menu_data.mcfunction", "\n".join(MD))

w(F + "menu.mcfunction", f"function {NS}:menu_data\nfunction {NS}:menu_dialog with storage {NS}:menu")
body = []
for j, d in jobs.items():
    body.append('{type:"minecraft:plain_message",width:300,contents:['
                f'{{text:"$({j}_st)",color:"gold"}},{{text:"{d["name"]}",color:"{d["color"]}",bold:true}},'
                f'{{text:"   niveau $({j}_lvl)/{MAXLVL}   $({j}_t)\\n",color:"yellow"}},'
                f'{{text:"$({j}_b1)",color:"green"}},{{text:"$({j}_b2)",color:"dark_gray"}},'
                f'{{text:"   $({j}_xp)/$({j}_need) XP",color:"gray"}}]}}')
btns = [f'{{label:{{text:"Compétences {d["name"]} ($({j}_pts) pts)",color:"{d["color"]}"}},width:200,'
        f'action:{{type:"run_command",command:"trigger metiers set {20 + d["idx"]}"}}}}' for j, d in jobs.items()]
btns.append('{label:{text:"Choisir mon titre",color:"yellow"},width:200,action:{type:"run_command",command:"trigger metiers set 2"}}')
btns.append('{label:{text:"Récompenses de palier",color:"light_purple"},width:200,action:{type:"run_command",command:"trigger metiers set 3"}}')
btns.append('{label:{text:"Défis du jour",color:"aqua"},width:200,action:{type:"run_command",command:"trigger metiers set 4"}}')
btns.append('{label:{text:"Classement",color:"gold"},width:200,action:{type:"run_command",command:"trigger metiers set 5"}}')
btns.append('{label:{text:"Armure des Guildes",color:"#F1CF4E"},width:200,action:{type:"run_command",command:"trigger metiers set 6"}}')
w(F + "menu_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Mes métiers",color:"gold"},'
  'can_close_with_escape:true,pause:false,body:[' + ",".join(body) + '],'
  'actions:[' + ",".join(btns) + '],columns:2,exit_action:{label:"Fermer",width:150}}')

# titres
w(F + "prefixe/menu.mcfunction", f"function {NS}:menu_data\nfunction {NS}:prefixe/menu_dialog with storage {NS}:menu")
tb = [f'{{label:{{text:"$({j}_t) {d["name"]}",color:"{d["color"]}"}},width:150,'
      f'action:{{type:"run_command",command:"trigger metiers set {10 + d["idx"]}"}}}}' for j, d in jobs.items()]
tb.append('{label:{text:"Sans titre",color:"gray"},width:150,action:{type:"run_command",command:"trigger metiers set 10"}}')
w(F + "prefixe/menu_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Choisir mon titre",color:"gold"},'
  'can_close_with_escape:true,pause:false,body:[{type:"minecraft:plain_message",width:300,'
  'contents:{text:"Le titre s\'affiche devant ton pseudo et évolue tous les 10 niveaux.",color:"gray"}}],'
  'actions:[' + ",".join(tb) + '],columns:2,'
  'exit_action:{label:"Retour",width:150,action:{type:"run_command",command:"trigger metiers set 1"}}}')

E = []
for j in jobs:
    for t in range(11):
        E.append(f"team remove m.{j}{t}")
        for st in range(6):
            E += [f"team add m.{j}{t}_{st}", f"team modify m.{j}{t}_{st} prefix {team_prefix(j, t, st)}"]
w(F + "prefixe/equipes.mcfunction", "\n".join(E))

w(F + "prefixe/choisir.mcfunction", f"""
scoreboard players operation @s m.pref = @s m.trig
scoreboard players remove @s m.pref 10
execute if score @s m.pref matches 0 run team leave @s
execute if score @s m.pref matches 0 run tellraw @s {PREFIX},{{"text":"Titre retiré.","color":"gray"}}]
execute if score @s m.pref matches 1.. run tag @s add metiers.maj
execute if score @s m.pref matches 1.. run function {NS}:prefixe/maj
execute if score @s m.pref matches 1.. run tellraw @s {PREFIX},{{"text":"Titre mis à jour.","color":"gray"}}]
playsound minecraft:ui.button.click master @s
""")
MJ = ["tag @s remove metiers.maj"]
for j, d in jobs.items():
    for t, (_, rng) in enumerate(TIERS):
        for st in range(6):
            MJ.append(f"execute if score @s m.pref matches {d['idx']} if score @s m.{j}_lvl matches {rng} if score @s m.{j}_pr matches {st} run team join m.{j}{t}_{st} @s")
w(F + "prefixe/maj.mcfunction", "\n".join(MJ))

# =====================================================================
# APPEL ISOLÉ (une fonction cassée ne casse pas le reste)
# =====================================================================
w(F + "appel.mcfunction", f"$function {NS}:$(f)")
w(F + "version.mcfunction", 'tellraw @s {"text":"[Métiers] Version 23 : 9 métiers, Armure des Guildes (heaume 3D) (avec Éleveur, Enchanteur, Explorateur, Marchand)","color":"gold"}')

def tr(txt, col="gray"):
    return 'tellraw @s ' + PREFIX + f',{{"text":"{txt}","color":"{col}"}}]'

# =====================================================================
# OUTIL ÉVOLUTIF
# =====================================================================
MAXDUR = {"iron": 250, "diamond": 1561, "netherite": 2031, "golden": 32, "stone": 131, "wooden": 59}
BASE_TOOL = {"b": "iron_axe", "m": "iron_pickaxe", "f": "iron_hoe", "c": "iron_sword", "p": "fishing_rod",
             "e": "shears", "n": "book", "x": "iron_boots", "t": "bundle"}

def outil_give(j, k):
    d = jobs[j]
    if k == 0:
        iid, ench, name, color, unb = BASE_TOOL[j], ({} if j in ("n", "t") else {"unbreaking": 1}), f"{TOOL[j][1]} {DE[0]}", "gray", j == "x"
    else:
        it = R[j][k][0]
        iid, ench, name, color, unb = it["iid"], dict(it["ench"]), it["name"], it["color"], it["unb"]
    e = ",".join(f'"minecraft:{a}":{v}' for a, v in ench.items())
    lore = (f'[{{text:"Outil de {d["name"]}",color:"{d["color"]}",italic:false}},'
            f'{{text:"Palier {k}/10, il évolue tous les 10 niveaux",color:"gray",italic:false}}]')
    comps = [f"minecraft:enchantments={{{e}}}",
             f'minecraft:custom_name={{text:"{name}",color:"{color}",bold:true,italic:false}}',
             f"minecraft:lore={lore}",
             (f'minecraft:custom_data={{metiers_outil:"{j}",palier:{k},o:$(o),s:$(s)}}' if j in ("n", "t", "x") else
              f'minecraft:custom_data={{metiers_outil:"{j}",palier:{k},max:{ {"fishing_rod": 64, "shears": 238}.get(iid, MAXDUR.get(iid.split("_")[0], 250))},o:$(o),s:$(s)}}'),
             f'minecraft:item_model="metiers:{j}_{k}"',
             "minecraft:enchantment_glint_override=false",
             "minecraft:repair_cost=1000", "!minecraft:repairable", "minecraft:max_stack_size=1",
             'minecraft:rarity="epic"']
    if unb:
        comps.append("minecraft:unbreakable={}")
    return f"minecraft:{iid}[{','.join(comps)}] 1"

CHK = []
for j, d in jobs.items():
    sel = f'*[minecraft:custom_data~{{metiers_outil:"{j}"}}]'
    ODM = []
    for k in range(11):
        it = outil_give(j, k)
        ODM += [f"$execute if score @s m.{j}_out matches {k} if entity @s[tag=metiers.o_main] run item replace entity @s weapon.mainhand with {it}",
                f"$execute if score @s m.{j}_out matches {k} if entity @s[tag=metiers.o_off] run item replace entity @s weapon.offhand with {it}",
                f"$execute if score @s m.{j}_out matches {k} if entity @s[tag=metiers.o_feet] run item replace entity @s armor.feet with {it}",
                f"$execute if score @s m.{j}_out matches {k} if entity @s[tag=!metiers.o_main,tag=!metiers.o_off,tag=!metiers.o_feet] run give @s {it}"]
    w(F + f"{j}/outil_donner_m.mcfunction", "\n".join(ODM))
    OD = ["tag @s remove metiers.o_main", "tag @s remove metiers.o_off", "tag @s remove metiers.o_feet",
          f"execute if items entity @s weapon.mainhand {sel} run tag @s add metiers.o_main",
          f"execute if items entity @s weapon.offhand {sel} run tag @s add metiers.o_off",
          f"execute if items entity @s armor.feet {sel} run tag @s add metiers.o_feet",
          f"execute if items entity @s weapon.offhand {sel} run item replace entity @s weapon.offhand with minecraft:air",
          f"execute if items entity @s armor.feet {sel} run item replace entity @s armor.feet with minecraft:air",
          f"clear @s {sel}", f"scoreboard players add @s m.{j}_ser 1",
          f"execute store result storage {NS}:tmp o int 1 run scoreboard players get @s m.id",
          f"execute store result storage {NS}:tmp s int 1 run scoreboard players get @s m.{j}_ser",
          f"function {NS}:{j}/outil_donner_m with storage {NS}:tmp",
          "tag @s remove metiers.o_main", "tag @s remove metiers.o_off", "tag @s remove metiers.o_feet",
          "playsound minecraft:block.anvil.use master @s ~ ~ ~ 0.6 1.4"]
    w(F + f"{j}/outil_donner.mcfunction", "\n".join(OD))
    w(F + f"{j}/outil_recup.mcfunction", "\n".join([
        f"execute if items entity @s container.* {sel} run return run {tr('Tu as déjà ton outil de ' + d['name'] + ' sur toi.')}",
        f"execute if items entity @s weapon.offhand {sel} run return run {tr('Tu as déjà ton outil de ' + d['name'] + ' sur toi.')}",
        f"scoreboard players operation @s m.tmp = @s m.{j}_cd",
        f"scoreboard players operation @s m.tmp /= #60 m.const",
        f"scoreboard players operation @s m.tmp /= #2 m.const",
        f"scoreboard players add @s m.tmp 1",
        f'execute if score @s m.{j}_cd matches 1.. run return run tellraw @s ' + PREFIX + ',{"text":"Patiente encore ","color":"red"},{"score":{"name":"@s","objective":"m.tmp"},"color":"yellow"},{"text":" min avant de le récupérer.","color":"red"}]',
        f"scoreboard players set @s m.{j}_cd 1200",
        f"function {NS}:{j}/outil_donner",
        tr(f"Voici ton outil de {d['name']}. Il évolue tout seul à chaque palier de 10 niveaux.", "green")]))
    w(F + f"{j}/outil_lore.mcfunction",
      'item modify entity @s weapon.mainhand {function:"minecraft:set_lore",type:"minecraft:set_lore",entity:"this",mode:"replace_all",lore:['
      f'{{text:"Outil de {d["name"]}",color:"{d["color"]}",italic:false}},'
      f'[{{text:"Niveau ",color:"gray",italic:false}},{{score:{{name:"@s",objective:"m.{j}_lvl"}},color:"yellow"}},{{text:" / 100",color:"gray"}}],'
      f'[{{text:"Palier ",color:"gray",italic:false}},{{score:{{name:"@s",objective:"m.{j}_out"}},color:"yellow"}},{{text:" / 10, il évolue tous les 10 niveaux",color:"gray"}}]]}}')
    CHK.append(f'execute if items entity @s weapon.mainhand {sel} run function {NS}:appel {{f:"{j}/outil_lore"}}')
    RM = []
    for k in range(1, 11):
        RM += [f'data modify storage {NS}:rec s{k} set value "Niveau {10 * k} requis"',
               f'data modify storage {NS}:rec c{k} set value "dark_gray"',
               f'execute if score @s m.{j}_lvl matches {10 * k}.. run data modify storage {NS}:rec s{k} set value "À récupérer (G > Récompenses de palier)"',
               f'execute if score @s m.{j}_lvl matches {10 * k}.. run data modify storage {NS}:rec c{k} set value "yellow"',
               f'execute if score @s m.{j}_pal matches {k}.. run data modify storage {NS}:rec s{k} set value "✔ Récupéré"',
               f'execute if score @s m.{j}_pal matches {k}.. run data modify storage {NS}:rec c{k} set value "green"']
    RM.append(f"function {NS}:{j}/recompenses_dialog with storage {NS}:rec")
    w(F + f"{j}/recompenses_menu.mcfunction", "\n".join(RM))
    rb = []
    for k in range(1, 11):
        its = R[j][k]
        tool = its[0]
        extras = ", ".join((it["name"] or it["label"]) for it in its[1:])
        rb.append(f'{{type:"minecraft:plain_message",width:330,contents:[{{text:"Palier {k} · niveau {10 * k}   ",color:"gold",bold:true}},'
                  f'{{text:"$(s{k})",color:"$(c{k})",bold:false}},'
                  f'{{text:"\\nOutil : ",color:"gray",bold:false}},{{text:"{tool["name"]}",color:"{tool["color"]}",bold:true}},'
                  f'{{text:"\\n{ench_txt(tool)}",color:"dark_aqua",bold:false}},'
                  f'{{text:"\\nBonus : {extras}",color:"white",bold:false}}]}}')
    w(F + f"{j}/recompenses_dialog.mcfunction",
      f'$dialog show @s {{type:"minecraft:notice",title:{{text:"Récompenses {d["name"]}",color:"{d["color"]}",bold:true}},can_close_with_escape:true,pause:false,'
      f'body:[{",".join(rb)}],action:{{label:"Retour",width:150,action:{{type:"run_command",command:"trigger metiers set {20 + d["idx"]}"}}}}}}')
    w(F + f"{j}/outil_reparer.mcfunction", "\n".join([
        f"execute unless items entity @s container.* {sel} unless items entity @s weapon.offhand {sel} run return run {tr('Tu dois avoir ton outil de ' + d['name'] + ' sur toi pour le réparer.', 'red')}",
        f"execute if score @s m.{j}_out matches 5.. run return run {tr('Ton outil est déjà incassable.', 'green')}",
        f"execute unless entity @s[level=5..] run return run {tr('Il te faut 5 niveaux d’XP pour réparer ton outil.', 'red')}",
        "xp add @s -5 levels",
        f"function {NS}:{j}/outil_donner",
        tr(f"Ton outil de {d['name']} est comme neuf.", "green")]))
    w(F + f"{j}/outil_monte.mcfunction", "\n".join([
        f"scoreboard players operation @s m.tmp = @s m.{j}_lvl",
        f"scoreboard players operation @s m.tmp /= #10 m.const",
        f"execute if score @s m.{j}_out >= @s m.tmp run return 0",
        f"scoreboard players operation @s m.{j}_out = @s m.tmp",
        f'tellraw @a ' + PREFIX + f',{{"selector":"@s","color":"white"}},{{"text":" fait évoluer son outil de {d["name"]} !","color":"{d["color"]}","bold":true}}]',
        f"function {NS}:{j}/outil_donner",
        tr(f"Ton nouvel outil de {d['name']} est dans ton inventaire (l'ancien a été remplacé).", "yellow")]))
w(F + "outil/check.mcfunction", "\n".join(CHK))

M6 = ["tag @s add metiers.v7", "tag @s add metiers.v6"]
for j in jobs:
    M6 += [f"scoreboard players add @s m.{j}_pr 0", f"scoreboard players add @s m.{j}_cd 0",
           f"execute unless score @s m.{j}_out matches 0.. run scoreboard players set @s m.{j}_out 0",
           f"scoreboard players operation @s m.{j}_out > @s m.{j}_pal",
           f"scoreboard players operation @s m.tmp = @s m.{j}_lvl",
           f"scoreboard players operation @s m.tmp /= #10 m.const",
           f"scoreboard players operation @s m.{j}_out > @s m.tmp",
           f'execute if score @s m.{j}_out matches 1.. run function {NS}:appel {{f:"{j}/outil_donner"}}']
M6.append('tellraw @s ' + PREFIX + ',{"text":"Nouveau : chaque métier a son outil qui évolue avec toi ! Tu viens de recevoir ceux des métiers où tu es niveau 10 ou plus, au palier qui correspond à ton niveau. Pour les autres : touche G, le métier, puis « Récupérer mon outil ». Défis du jour, classement, prestige et boss de serveur sont aussi arrivés.","color":"yellow"}]')
w(F + "migration6.mcfunction", "\n".join(M6))
M8 = ["tag @s add metiers.v8", "tag @s add metiers.v9"]
for j in jobs:
    sel = f'*[minecraft:custom_data~{{metiers_outil:"{j}"}}]'
    M8.append(f"execute if items entity @s container.* {sel} run function {NS}:{j}/outil_donner")
M8.append('tellraw @s ' + PREFIX + ',{"text":"Tes outils de métier ont été mis à jour : incassables dès le niveau 50, bloqués avant de casser, et réparables uniquement via le menu (touche G).","color":"yellow"}]')
w(F + "migration8.mcfunction", "\n".join(M8))

w(F + "id.mcfunction", f"""
scoreboard players add #next m.id 1
scoreboard players operation @s m.id = #next m.id
execute store result storage {NS}:tmp id int 1 run scoreboard players get @s m.id
function {NS}:defis/creer_barre with storage {NS}:tmp
""")

# =====================================================================
# PRESTIGE
# =====================================================================
for j, d in jobs.items():
    w(F + f"{j}/prestige_confirmer.mcfunction", "\n".join([
        f"execute if score @s m.{j}_lvl matches ..99 run return run {tr('Le prestige se débloque au niveau 100 du métier.', 'red')}",
        f"execute if score @s m.{j}_pr matches 5.. run return run {tr('Tu as déjà les 5 étoiles de prestige, bravo !', 'gold')}",
        f'dialog show @s {{type:"minecraft:confirmation",title:{{text:"★ Prestige {d["name"]}",color:"gold",bold:true}},can_close_with_escape:true,pause:false,'
        f'body:[{{type:"minecraft:plain_message",width:300,contents:[{{text:"Ton métier repart au niveau 1 et tes compétences sont remises à zéro (tu regagnes les points en remontant).\\n\\n",color:"white"}},'
        f'{{text:"Tu gardes :",color:"green",bold:true}},{{text:" ton outil au palier atteint.\\n",color:"white"}},'
        f'{{text:"Tu gagnes :",color:"gold",bold:true}},{{text:" une étoile devant ton titre et +10 % d\'XP dans ce métier, pour toujours (5 étoiles max). Les récompenses de palier peuvent être regagnées.",color:"white"}}]}}],'
        f'yes:{{label:{{text:"Passer prestige",color:"gold",bold:true}},width:150,action:{{type:"run_command",command:"trigger metiers set {320 + d["idx"]}"}}}},'
        f'no:{{label:{{text:"Annuler",color:"gray"}},width:150}}}}']))
    PR = [f"execute if score @s m.{j}_lvl matches ..99 run return 0",
          f"execute if score @s m.{j}_pr matches 5.. run return 0",
          f"scoreboard players add @s m.{j}_pr 1",
          f"scoreboard players set @s m.{j}_lvl 1", f"scoreboard players set @s m.{j}_xp 0",
          f"scoreboard players set @s m.{j}_need 50", f"scoreboard players set @s m.{j}_spent 0",
          f"scoreboard players set @s m.{j}_pal 0"]
    PR += [f"tag @s remove metiers.sk.{j}{k}" for k in range(1, 7)]
    PR += [f"advancement revoke @s from {NS}:{j}/competence_1", f"advancement revoke @s from {NS}:{j}/niveau_10",
           "tag @s add metiers.maj",
           'tellraw @a ' + PREFIX + f',{{"selector":"@s","color":"white"}},{{"text":" passe ","color":"gray"}},{{"text":"★ Prestige ","color":"gold","bold":true}},{{"score":{{"name":"@s","objective":"m.{j}_pr"}},"color":"gold","bold":true}},{{"text":" en {d["name"]} !","color":"{d["color"]}","bold":true}}]',
           "playsound minecraft:ui.toast.challenge_complete master @a ~ ~ ~ 1 0.8",
           "playsound minecraft:entity.firework_rocket.large_blast master @a ~ ~ ~ 1 1",
           "particle minecraft:totem_of_undying ~ ~1 ~ 0.6 1.2 0.6 0.5 200",
           "particle minecraft:end_rod ~ ~1 ~ 0.4 1 0.4 0.15 80"]
    w(F + f"{j}/prestige.mcfunction", "\n".join(PR))

# =====================================================================
# HEURE DU MÉTIER (toutes les 90 min, un métier rapporte x2 pendant 30 min)
# =====================================================================
w(F + "heure/tick.mcfunction", f"""
scoreboard players add #cycle m.heure 1
execute if score #job m.heure matches 0 if score #cycle m.heure matches 10800.. if entity @a run function {NS}:heure/lancer
execute if score #job m.heure matches 1.. run function {NS}:heure/encours
""")
HL = ["scoreboard players set #cycle m.heure 0",
      f"execute store result score #job m.heure run random value 1..{NJ}",
      "scoreboard players set #reste m.heure 3600"]
for j, d in jobs.items():
    i = d["idx"]
    HL += [f'execute if score #job m.heure matches {i} run bossbar set metiers:heure name [{{"text":"{d["icon"]} Heure du {d["name"]}","color":"{d["color"]}","bold":true}},{{"text":" : XP x2","color":"white","bold":false}}]',
           f"execute if score #job m.heure matches {i} run bossbar set metiers:heure color {BARCOL[j]}",
           f'execute if score #job m.heure matches {i} run tellraw @a ' + PREFIX + f',{{"text":"C\'est l\'heure du {d["name"]} ! ","color":"{d["color"]}","bold":true}},{{"text":"Toute l\'XP de ce métier compte double pendant 30 minutes.","color":"white"}}]']
HL += ["bossbar set metiers:heure visible true", "bossbar set metiers:heure players @a",
       "execute as @a at @s run playsound minecraft:block.bell.use master @s ~ ~ ~ 1 1"]
w(F + "heure/lancer.mcfunction", "\n".join(HL))
w(F + "heure/encours.mcfunction", f"""
scoreboard players remove #reste m.heure 1
execute store result bossbar metiers:heure value run scoreboard players get #reste m.heure
bossbar set metiers:heure players @a
execute if score #reste m.heure matches ..0 run function {NS}:heure/fin
""")
w(F + "heure/fin.mcfunction", f"""
scoreboard players set #job m.heure 0
bossbar set metiers:heure visible false
tellraw @a {PREFIX},{{"text":"L'heure du métier est terminée. Prochaine dans 1 h 30.","color":"gray"}}]
""")

# =====================================================================
# DÉFIS DU JOUR
# =====================================================================
w(F + "defis/tick.mcfunction", f"""
execute if entity @a run scoreboard players add #jour m.defi 1
execute unless score #d_b m.defi matches 1.. run function {NS}:defis/nouveaux
execute if score #jour m.defi matches 28800.. run function {NS}:defis/nouveaux
scoreboard players set #left m.defi 28800
scoreboard players operation #left m.defi -= #jour m.defi
scoreboard players operation #left m.defi /= #7200 m.const
scoreboard players add #left m.defi 1
""")
NV = ["scoreboard players set #jour m.defi 0"]
for j, pool in DEFIS.items():
    NV.append(f"execute store result score #d_{j} m.defi run random value 1..{len(pool)}")
    NV.append(f"scoreboard players reset * m.dd_{j}")
    for i, (desc, tgt, crits, div) in enumerate(pool, 1):
        for n in range(len(crits)):
            NV.append(f"scoreboard players reset * dq.{j}{i}_{n}")
NV.append('tellraw @a ' + PREFIX + ',{"text":"Nouveaux défis du jour ! ","color":"aqua","bold":true},{"text":"Ils défilent dans ta barre de boss (touche G > Défis du jour).","color":"white"}]')
w(F + "defis/nouveaux.mcfunction", "\n".join(NV))
w(F + "defis/creer_barre.mcfunction", '$bossbar add metiers:d$(id) ""\n$bossbar set metiers:d$(id) style notched_10')

DJ = []
for j, pool in DEFIS.items():
    DJ.append(f"scoreboard players set @s m.dp_{j} 0")
    for i, (desc, tgt, crits, div) in enumerate(pool, 1):
        for n in range(len(crits)):
            DJ.append(f"execute if score #d_{j} m.defi matches {i} run scoreboard players operation @s m.dp_{j} += @s dq.{j}{i}_{n}")
        if div > 1:
            DJ.append(f"execute if score #d_{j} m.defi matches {i} run scoreboard players operation @s m.dp_{j} /= #100 m.const")
        DJ.append(f"execute if score #d_{j} m.defi matches {i} unless score @s m.dd_{j} matches 1 if score @s m.dp_{j} matches {tgt}.. run function {NS}:defis/fini_{j}")
DJ.append("scoreboard players set @s m.dall 0")
DJ += [f"execute if score @s m.dd_{j} matches 1 run scoreboard players add @s m.dall 1" for j in jobs]
DJ += [f"execute unless score @s m.dshow matches 1..{NJ} run scoreboard players set @s m.dshow 1",
       f"execute if score #huit m.timer matches 0 run function {NS}:defis/plus1"]
for _ in range(NJ):
    DJ += [f"execute if score @s m.dall matches ..{NJ - 1} if score @s m.dshow matches {d['idx']} if score @s m.dd_{j} matches 1 run function {NS}:defis/plus1" for j, d in jobs.items()]
DJ += [f"execute store result storage {NS}:tmp id int 1 run scoreboard players get @s m.id",
       f"function {NS}:defis/barre with storage {NS}:tmp"]
w(F + "defis/joueur.mcfunction", "\n".join(DJ))
w(F + "defis/plus1.mcfunction", f"scoreboard players add @s m.dshow 1\nexecute if score @s m.dshow matches {NJ + 1}.. run scoreboard players set @s m.dshow 1")

BA = ["$bossbar set metiers:d$(id) players @s",
      "$execute if entity @s[tag=metiers.nobar] run bossbar set metiers:d$(id) visible false",
      "execute if entity @s[tag=metiers.nobar] run return 0",
      "$bossbar set metiers:d$(id) visible true",
      f"$execute if score @s m.dall matches {NJ} run function {NS}:defis/barre_fini {{id:$(id)}}",
      f"execute if score @s m.dall matches {NJ} run return 0"]
for j, d in jobs.items():
    BA.append(f"$execute if score @s m.dshow matches {d['idx']} run function {NS}:defis/barre_{j} {{id:$(id)}}")
w(F + "defis/barre.mcfunction", "\n".join(BA))
w(F + "defis/barre_fini.mcfunction", "\n".join([
    '$bossbar set metiers:d$(id) name [{"text":"✔ Tous les défis du jour sont faits ! ","color":"green","bold":true},{"text":"Nouveaux défis dans ","color":"white","bold":false},{"score":{"name":"#left","objective":"m.defi"},"color":"yellow"},{"text":" h","color":"white"}]',
    "$bossbar set metiers:d$(id) color green", "$bossbar set metiers:d$(id) max 1", "$bossbar set metiers:d$(id) value 1"]))
for j, pool in DEFIS.items():
    d = jobs[j]
    BJ = [f"$bossbar set metiers:d$(id) color {BARCOL[j]}"]
    for i, (desc, tgt, crits, div) in enumerate(pool, 1):
        BJ += [f'$execute if score #d_{j} m.defi matches {i} run bossbar set metiers:d$(id) name [{{"text":"Défi {d["icon"]} {d["name"]} : ","color":"{d["color"]}","bold":true}},{{"text":"{desc}  ","color":"white","bold":false}},{{"score":{{"name":"@s","objective":"m.dp_{j}"}},"color":"yellow"}},{{"text":" / {tgt}","color":"gray"}}]',
               f"$execute if score #d_{j} m.defi matches {i} run bossbar set metiers:d$(id) max {tgt}"]
    BJ.append(f"$execute store result bossbar metiers:d$(id) value run scoreboard players get @s m.dp_{j}")
    w(F + f"defis/barre_{j}.mcfunction", "\n".join(BJ))
    w(F + f"defis/fini_{j}.mcfunction", "\n".join([
        f"scoreboard players set @s m.dd_{j} 1", f"scoreboard players operation @s m.tmp = @s m.{j}_need", f"scoreboard players operation @s m.tmp /= #2 m.const",
        f"scoreboard players operation @s m.{j}_bal += @s m.tmp",
        "give @s minecraft:diamond 2", "give @s minecraft:experience_bottle 16",
        'tellraw @a ' + PREFIX + f',{{"selector":"@s","color":"white"}},{{"text":" a réussi le défi du jour ","color":"gray"}},{{"text":"{d["icon"]} {d["name"]}","color":"{d["color"]}","bold":true}}]',
        "playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1.2",
        "scoreboard players set @s m.tmp 0"] +
        [f"execute if score @s m.dd_{jj} matches 1 run scoreboard players add @s m.tmp 1" for jj in jobs] +
        [f"execute if score @s m.tmp matches {NJ} run function {NS}:defis/tous", f"function {NS}:defis/plus1"]))
w(F + "defis/tous.mcfunction", "\n".join([
    "give @s minecraft:enchanted_golden_apple 1", "give @s minecraft:netherite_scrap 2",
    'tellraw @a ' + PREFIX + ',{"selector":"@s","color":"white"},{"text":" a réussi tous les défis du jour !","color":"gold","bold":true}]',
    "playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 0.5"]))
w(F + "defis/basculer.mcfunction", f"""
execute if entity @s[tag=metiers.nobar] run tag @s add metiers.barre_on
tag @s[tag=metiers.barre_on] remove metiers.nobar
execute unless entity @s[tag=metiers.barre_on] run tag @s add metiers.nobar
execute if entity @s[tag=metiers.nobar] run {tr("Barre des défis masquée.")}
execute if entity @s[tag=metiers.barre_on] run {tr("Barre des défis affichée.")}
tag @s remove metiers.barre_on
function {NS}:defis/menu
""")

DM = [f"function {NS}:defis/joueur",
      f"execute store result storage {NS}:defis left int 1 run scoreboard players get #left m.defi"]
for j, pool in DEFIS.items():
    DM += [f"execute store result storage {NS}:defis {j}_p int 1 run scoreboard players get @s m.dp_{j}",
           f'data modify storage {NS}:defis {j}_ok set value ""',
           f'execute if score @s m.dd_{j} matches 1 run data modify storage {NS}:defis {j}_ok set value "  ✔ réussi"']
    for i, (desc, tgt, crits, div) in enumerate(pool, 1):
        DM += [f'execute if score #d_{j} m.defi matches {i} run data modify storage {NS}:defis {j}_d set value "{desc}"',
               f"execute if score #d_{j} m.defi matches {i} run data modify storage {NS}:defis {j}_t set value {tgt}"]
DM.append(f"function {NS}:defis/menu_dialog with storage {NS}:defis")
w(F + "defis/menu.mcfunction", "\n".join(DM))
db = []
for j, d in jobs.items():
    db.append(f'{{type:"minecraft:plain_message",width:320,contents:[{{text:"{d["icon"]} {d["name"]}  ",color:"{d["color"]}",bold:true}},'
              f'{{text:"$({j}_d)\\n",color:"white"}},{{text:"$({j}_p) / $({j}_t)",color:"yellow"}},{{text:"$({j}_ok)",color:"green",bold:true}}]}}')
db.append('{type:"minecraft:plain_message",width:320,contents:[{text:"\\nChaque défi : un demi-niveau d\'XP du métier, 2 diamants et 16 fioles d\'XP. Tous : une pomme de Notch et 2 fragments de netherite en plus.\\n",color:"gray"},{text:"Nouveaux défis dans $(left) h.",color:"aqua"}]}')
w(F + "defis/menu_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Défis du jour",color:"aqua",bold:true},can_close_with_escape:true,pause:false,'
  'body:[' + ",".join(db) + '],actions:[{label:{text:"Afficher / masquer la barre",color:"white"},width:200,action:{type:"run_command",command:"trigger metiers set 7"}}],'
  'columns:1,exit_action:{label:"Retour",width:150,action:{type:"run_command",command:"trigger metiers set 1"}}}')

# =====================================================================
# CLASSEMENT ET PODIUM
# =====================================================================
CM = [f"execute store result storage {NS}:tmp id int 1 run scoreboard players get @s m.id",
      "scoreboard players set @s m.total 0"]
for j in jobs:
    CM += [f"scoreboard players operation @s m.tmp = @s m.{j}_pr",
           f"scoreboard players operation @s m.tmp *= #100 m.const",
           f"scoreboard players operation @s m.tmp += @s m.{j}_lvl",
           f"scoreboard players operation @s m.total += @s m.tmp",
           f"execute store result storage {NS}:tmp {j} int 1 run scoreboard players get @s m.tmp",
           f"execute store result storage {NS}:tmp {j}l int 1 run scoreboard players get @s m.{j}_lvl",
           f'data modify storage {NS}:tmp {j}st set value ""']
    CM += [f'execute if score @s m.{j}_pr matches {st} run data modify storage {NS}:tmp {j}st set value "{"★" * st}"' for st in range(1, 6)]
CM += [f"execute store result storage {NS}:tmp t int 1 run scoreboard players get @s m.total",
       f'function {NS}:appel {{f:"armure/check"}}',
       f"function {NS}:classement/ecrire with storage {NS}:tmp"]
w(F + "classement/maj.mcfunction", "\n".join(CM))
EC = [f"$execute unless data storage {NS}:cl joueurs[{{id:$(id)}}] run function {NS}:classement/nouveau {{id:$(id)}}",
      f'function {NS}:appel {{f:"classement/nom"}}',
      f"$data modify storage {NS}:cl joueurs[{{id:$(id)}}].t set value $(t)"]
for j in jobs:
    EC += [f"$data modify storage {NS}:cl joueurs[{{id:$(id)}}].{j} set value $({j})",
           f"$data modify storage {NS}:cl joueurs[{{id:$(id)}}].{j}l set value $({j}l)",
           f'$data modify storage {NS}:cl joueurs[{{id:$(id)}}].{j}st set value "$({j}st)"']
w(F + "classement/ecrire.mcfunction", "\n".join(EC))
w(F + "classement/nouveau.mcfunction", f"$data modify storage {NS}:cl joueurs append value {{id:$(id)}}")
# nom du joueur : un item_display temporaire reçoit le pseudo résolu, puis on le copie
w(F + "classement/nom.mcfunction", f"""
data remove storage {NS}:tmp nom
summon minecraft:item_display ~ ~-2 ~ {{Tags:["metiers.nomeur"],item:{{id:"minecraft:paper",count:1}}}}
item modify entity @e[type=minecraft:item_display,tag=metiers.nomeur,limit=1] contents {{function:"minecraft:set_name",type:"minecraft:set_name",entity:"this",target:"custom_name",name:{{selector:"@s"}}}}
data modify storage {NS}:tmp nom set from entity @e[type=minecraft:item_display,tag=metiers.nomeur,limit=1] item.components."minecraft:custom_name"
kill @e[type=minecraft:item_display,tag=metiers.nomeur]
execute if data storage {NS}:tmp nom run function {NS}:classement/nom_m with storage {NS}:tmp
""")
w(F + "classement/nom_m.mcfunction", f"$data modify storage {NS}:cl joueurs[{{id:$(id)}}].nom set from storage {NS}:tmp nom")

w(F + "classement/top.mcfunction", f"""
data modify storage {NS}:cl copie set from storage {NS}:cl joueurs
data modify storage {NS}:cl res set value []
$function {NS}:classement/rang {{f:"$(f)"}}
$function {NS}:classement/rang {{f:"$(f)"}}
$function {NS}:classement/rang {{f:"$(f)"}}
""")
w(F + "classement/rang.mcfunction", f"""
scoreboard players set #best m.tmp -1
data remove storage {NS}:cl best
data modify storage {NS}:cl it set from storage {NS}:cl copie
$function {NS}:classement/iter {{f:"$(f)"}}
execute unless data storage {NS}:cl best run return 0
data modify storage {NS}:cl res append from storage {NS}:cl best
function {NS}:classement/retirer with storage {NS}:cl best
""")
w(F + "classement/iter.mcfunction", f"""
execute unless data storage {NS}:cl it[0] run return 0
$execute store result score #v m.tmp run data get storage {NS}:cl it[0].$(f)
execute if score #v m.tmp > #best m.tmp run data modify storage {NS}:cl best set from storage {NS}:cl it[0]
execute if score #v m.tmp > #best m.tmp run scoreboard players operation #best m.tmp = #v m.tmp
data remove storage {NS}:cl it[0]
$function {NS}:classement/iter {{f:"$(f)"}}
""")
w(F + "classement/retirer.mcfunction", f"$data remove storage {NS}:cl copie[{{id:$(id)}}]")

MEDAL = [("1er", "#FFD700"), ("2e", "#C8C8D0"), ("3e", "#CD7F32")]
CC = [f"execute as @a run function {NS}:classement/maj", f'function {NS}:classement/top {{f:"t"}}']
for r in range(3):
    CC += [f'data modify storage {NS}:podium p{r}n set value {{text:"personne",color:"dark_gray"}}',
           f'execute if data storage {NS}:cl res[{r}] run data modify storage {NS}:podium p{r}n set value {{text:"joueur hors ligne",color:"gray"}}',
           f"data modify storage {NS}:podium p{r}n set from storage {NS}:cl res[{r}].nom",
           f"execute store result storage {NS}:podium p{r}v int 1 run data get storage {NS}:cl res[{r}].t",
           f"execute store result score #p{r} m.tmp run data get storage {NS}:cl res[{r}].t"]
CC.append("execute if score #p0 m.tmp matches ..0 run scoreboard players set #p0 m.tmp 1")
for r in range(3):
    CC += [f"scoreboard players operation #b m.tmp = #p{r} m.tmp",
           "scoreboard players operation #b m.tmp *= #20 m.const",
           "scoreboard players operation #b m.tmp /= #p0 m.tmp"]
    CC += [f'execute if score #b m.tmp matches {k} run data modify storage {NS}:podium p{r}b set value "{"▌" * k}"' for k in range(0, 21)]
for j in jobs:
    CC += [f'function {NS}:classement/top {{f:"{j}"}}',
           f'data modify storage {NS}:podium c{j}n set value {{text:"personne",color:"dark_gray"}}',
           f'execute if data storage {NS}:cl res[0] run data modify storage {NS}:podium c{j}n set value {{text:"joueur hors ligne",color:"gray"}}',
           f"data modify storage {NS}:podium c{j}n set from storage {NS}:cl res[0].nom",
           f"execute store result storage {NS}:podium c{j}l int 1 run data get storage {NS}:cl res[0].{j}l",
           f'data modify storage {NS}:podium c{j}s set value ""',
           f"data modify storage {NS}:podium c{j}s set from storage {NS}:cl res[0].{j}st"]
CC.append(f"function {NS}:classement/dialog with storage {NS}:podium")
w(F + "classement/menu.mcfunction", "\n".join(CC))
pb = ['{type:"minecraft:plain_message",width:320,contents:{text:"Podium général",color:"gold",bold:true}}']
for r, (lab, col) in enumerate(MEDAL):
    pb.append(f'{{type:"minecraft:plain_message",width:320,contents:[{{text:"{lab}  ",color:"{col}",bold:true}},$(p{r}n),'
              f'{{text:"   $(p{r}v) pts\\n",color:"white",bold:false}},{{text:"$(p{r}b)",color:"{col}"}}]}}')
lines = []
for j, d in jobs.items():
    lines.append(f'{{text:"{d["icon"]} {d["name"]} : ",color:"{d["color"]}",bold:true}},$(c{j}n),{{text:"  niv $(c{j}l) ",color:"gray",bold:false}},{{text:"$(c{j}s)\\n",color:"gold"}}')
pb.append('{type:"minecraft:plain_message",width:320,contents:[{text:"\\nMeilleur de chaque métier\\n",color:"gold",bold:true},' + ",".join(lines) + ']}')
pb.append('{type:"minecraft:plain_message",width:320,contents:{text:"Score = somme des niveaux de tous les métiers, +100 par étoile de prestige.",color:"dark_gray"}}')
w(F + "classement/dialog.mcfunction",
  '$dialog show @s {type:"minecraft:notice",title:{text:"Classement",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  'body:[' + ",".join(pb) + '],action:{label:"Retour",width:150,action:{type:"run_command",command:"trigger metiers set 1"}}}')

# =====================================================================
# BOSS DE SERVEUR
# =====================================================================
w(F + "boss/tick.mcfunction", f"""
scoreboard players add #cycle m.boss 1
execute if score #actif m.boss matches 0 if score #compte m.boss matches 1.. run function {NS}:boss/compte
execute if score #actif m.boss matches 0 if score #compte m.boss matches ..0 if score #cycle m.boss matches 21600.. run function {NS}:boss/alerte
execute if score #actif m.boss matches 1 run function {NS}:boss/encours
""")
w(F + "boss/alerte.mcfunction", f"""
execute store result score #n m.boss if entity @a
execute if score #n m.boss matches ..1 run return run scoreboard players set #cycle m.boss 18000
scoreboard players set #cycle m.boss 0
scoreboard players set #compte m.boss 240
tellraw @a {PREFIX},{{"text":"Le Colosse des Métiers se réveille ! ","color":"dark_red","bold":true}},{{"text":"Il apparaît dans 2 minutes près d'un joueur au hasard. Préparez-vous.","color":"white"}}]
execute as @a at @s run playsound minecraft:entity.wither.spawn master @s ~ ~ ~ 0.6 0.6
""")
w(F + "boss/compte.mcfunction", f"""
scoreboard players remove #compte m.boss 1
execute if score #compte m.boss matches 0 run function {NS}:boss/invoquer
""")
w(F + "boss/invoquer.mcfunction", f"execute as @r[gamemode=!spectator] at @s run function {NS}:boss/apparaitre")
w(F + "boss/apparaitre.mcfunction", f"""
summon minecraft:zombie ~ ~ ~ {{Tags:["metiers.boss"],CustomName:{{text:"Le Colosse des Métiers",color:"dark_red",bold:true}},CustomNameVisible:1b,PersistenceRequired:1b,CanPickUpLoot:0b,Health:600f,attributes:[{{id:"minecraft:max_health",base:600d}},{{id:"minecraft:attack_damage",base:14d}},{{id:"minecraft:armor",base:16d}},{{id:"minecraft:knockback_resistance",base:1d}},{{id:"minecraft:movement_speed",base:0.3d}},{{id:"minecraft:follow_range",base:64d}},{{id:"minecraft:scale",base:2.5d}},{{id:"minecraft:spawn_reinforcements",base:0d}}],equipment:{{head:{{id:"minecraft:netherite_helmet",count:1}},chest:{{id:"minecraft:netherite_chestplate",count:1}},legs:{{id:"minecraft:netherite_leggings",count:1}},feet:{{id:"minecraft:netherite_boots",count:1}},mainhand:{{id:"minecraft:netherite_axe",count:1}}}},drop_chances:{{head:0f,chest:0f,legs:0f,feet:0f,mainhand:0f}}}}
spreadplayers ~ ~ 6 14 false @e[type=minecraft:zombie,tag=metiers.boss,limit=1]
scoreboard players set #actif m.boss 1
scoreboard players set #temps m.boss 0
scoreboard players set #enrage m.boss 0
scoreboard players set #last m.boss 600
scoreboard players set @a m.dmg 0
bossbar set metiers:boss value 600
bossbar set metiers:boss visible true
bossbar set metiers:boss players @a
execute store result score #x m.boss run data get entity @e[type=minecraft:zombie,tag=metiers.boss,limit=1] Pos[0]
execute store result score #y m.boss run data get entity @e[type=minecraft:zombie,tag=metiers.boss,limit=1] Pos[1]
execute store result score #z m.boss run data get entity @e[type=minecraft:zombie,tag=metiers.boss,limit=1] Pos[2]
tellraw @a {PREFIX},{{"text":"Le Colosse est apparu près de ","color":"dark_red","bold":true}},{{"selector":"@s"}},{{"text":" en ","color":"white"}},{{"score":{{"name":"#x","objective":"m.boss"}},"color":"yellow"}},{{"text":" ","color":"white"}},{{"score":{{"name":"#y","objective":"m.boss"}},"color":"yellow"}},{{"text":" ","color":"white"}},{{"score":{{"name":"#z","objective":"m.boss"}},"color":"yellow"}},{{"text":". Tous ceux qui le frappent sont récompensés !","color":"white"}}]
execute as @a at @s run playsound minecraft:entity.ravager.roar master @s ~ ~ ~ 1 0.6
""")
w(F + "boss/encours.mcfunction", f"""
scoreboard players add #temps m.boss 1
execute store result score #hp m.boss run data get entity @e[type=minecraft:zombie,tag=metiers.boss,limit=1] Health
execute if score #hp m.boss matches 1.. store result bossbar metiers:boss value run scoreboard players get #hp m.boss
execute if entity @e[type=minecraft:zombie,tag=metiers.boss] run scoreboard players operation #last m.boss = #hp m.boss
execute as @a[scores={{m.dmg=1..}}] at @s if entity @e[type=minecraft:zombie,tag=metiers.boss,distance=..32] run tag @s add metiers.bossp
scoreboard players set @a m.dmg 0
execute unless entity @e[type=minecraft:zombie,tag=metiers.boss] if score #last m.boss matches ..90 run return run function {NS}:boss/victoire
bossbar set metiers:boss players @a
execute at @e[type=minecraft:zombie,tag=metiers.boss,limit=1] run particle minecraft:soul_fire_flame ~ ~2.5 ~ 0.8 1.6 0.8 0.02 8
execute if score #enrage m.boss matches 0 if score #hp m.boss matches 1..300 run function {NS}:boss/enrage
execute if score #temps m.boss matches 3600.. run function {NS}:boss/fuite
""")
w(F + "boss/enrage.mcfunction", f"""
scoreboard players set #enrage m.boss 1
execute as @e[type=minecraft:zombie,tag=metiers.boss,limit=1] at @s run function {NS}:boss/sbires
effect give @e[type=minecraft:zombie,tag=metiers.boss] minecraft:speed infinite 1 true
effect give @e[type=minecraft:zombie,tag=metiers.boss] minecraft:strength infinite 0 true
tellraw @a {PREFIX},{{"text":"Le Colosse est enragé et appelle ses sbires !","color":"red","bold":true}}]
execute as @a at @s run playsound minecraft:entity.ravager.roar master @s ~ ~ ~ 1 0.4
""")
w(F + "boss/sbires.mcfunction", "\n".join(
    [f'summon minecraft:zombie ~{dx} ~ ~{dz} {{Tags:["metiers.sbire"],CustomName:{{text:"Sbire du Colosse",color:"red"}},equipment:{{head:{{id:"minecraft:iron_helmet",count:1}}}},drop_chances:{{head:0f}}}}'
     for dx, dz in ((2, 0), (-2, 0), (0, 2), (0, -2))] + ["particle minecraft:large_smoke ~ ~1 ~ 2 1 2 0.05 120"]))
w(F + "boss/fuite.mcfunction", f"""
tp @e[type=minecraft:zombie,tag=metiers.boss] ~ -400 ~
kill @e[tag=metiers.boss]
kill @e[tag=metiers.sbire]
scoreboard players set #actif m.boss 0
scoreboard players set #cycle m.boss 0
bossbar set metiers:boss visible false
tag @a remove metiers.bossp
tellraw @a {PREFIX},{{"text":"Le Colosse s'est enfui... Il reviendra.","color":"gray"}}]
""")
w(F + "boss/victoire.mcfunction", f"""
execute unless score #actif m.boss matches 1 run return 0
tellraw @a {PREFIX},{{"text":"Le Colosse des Métiers est terrassé ! ","color":"gold","bold":true}},{{"text":"Tous ceux qui l'ont frappé sont récompensés : ","color":"white"}},{{"selector":"@a[tag=metiers.bossp]","color":"yellow"}}]
execute as @a[tag=metiers.bossp] at @s run function {NS}:boss/recompense
kill @e[tag=metiers.sbire]
scoreboard players set #actif m.boss 0
scoreboard players set #cycle m.boss 0
bossbar set metiers:boss visible false
execute as @a at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 0.7
""")
w(F + "boss/recompense.mcfunction", "\n".join([
    "scoreboard players operation @s m.c_bal += @s m.c_need",
    "give @s minecraft:netherite_ingot 2", "give @s minecraft:enchanted_golden_apple 2",
    "give @s minecraft:diamond 8", "give @s minecraft:totem_of_undying 1",
    tr("Récompense du Colosse : un niveau de Chasseur, 2 lingots de netherite, 2 pommes de Notch, 8 diamants et un totem.", "gold"),
    "particle minecraft:totem_of_undying ~ ~1 ~ 0.5 1 0.5 0.4 80",
    "tag @s remove metiers.bossp"]))

# =====================================================================
# ARMURE DES GUILDES (5 paliers selon le score total)
# =====================================================================
ARM_NOM = {1: "Bronze guildien", 2: "Argent runique", 3: "Or royal", 4: "Obsidienne astrale", 5: "Céleste"}
ARM_DE = {1: "de Bronze guildien", 2: "d'Argent runique", 3: "d'Or royal", 4: "d'Obsidienne astrale", 5: "Céleste"}
ARM_COL = {1: "#D4945A", 2: "#9CC2FF", 3: "#F1CF4E", 4: "#22C9E6", 5: "#FFF4D2"}
ARM_SEUIL = {1: 50, 2: 120, 3: 220, 4: 350, 5: 520}
ARM_BONUS = {1: "Célérité I", 2: "Vitesse I", 3: "Résistance I", 4: "Régénération I", 5: "Force I"}
PIECES = [("helmet", "head", "Heaume", 0), ("chestplate", "chest", "Cuirasse", 1), ("leggings", "legs", "Jambières", 2), ("boots", "feet", "Solerets", 3)]
ARMOR = {"head": [3, 3, 3, 4, 4], "chest": [8, 8, 9, 9, 10], "legs": [6, 6, 7, 7, 8], "feet": [3, 3, 3, 4, 4]}
TOUGH = [2, 3, 3, 4, 5]
KB = [0, 0.1, 0.1, 0.15, 0.2]
VIE = [0, 0, 2, 4, 6]

def piece_item(piece, slot, nom, t):
    i = t - 1
    mods = [f'{{type:"minecraft:armor",amount:{ARMOR[slot][i]},id:"metiers:g_{slot}_a",operation:"add_value",slot:"{slot}"}}',
            f'{{type:"minecraft:armor_toughness",amount:{TOUGH[i]},id:"metiers:g_{slot}_t",operation:"add_value",slot:"{slot}"}}']
    if KB[i]:
        mods.append(f'{{type:"minecraft:knockback_resistance",amount:{KB[i]},id:"metiers:g_{slot}_k",operation:"add_value",slot:"{slot}"}}')
    if slot == "chest" and VIE[i]:
        mods.append(f'{{type:"minecraft:max_health",amount:{VIE[i]},id:"metiers:g_vie",operation:"add_value",slot:"chest"}}')
    ench = {"protection": min(4, 1 + t), "unbreaking": 3}
    if slot == "feet": ench["feather_falling"] = min(4, t)
    if slot == "head": ench["respiration"] = min(3, t)
    e = ",".join(f'"minecraft:{a}":{v}' for a, v in ench.items())
    comps = [f"minecraft:enchantments={{{e}}}",
             f'minecraft:custom_name={{text:"{nom} {ARM_DE[t]}",color:"{ARM_COL[t]}",bold:true,italic:false}}',
             f'minecraft:lore=[{{text:"Armure des Guildes, palier {t}/5",color:"gray",italic:false}},{{text:"Set complet : {", ".join(ARM_BONUS[k] for k in range(1, t + 1))}",color:"gold",italic:false}}]',
             f"minecraft:custom_data={{metiers_armure:1b,palier:{t},o:$(o),s:$(s)}}",
             (f'minecraft:item_model="metiers:heaume_{t}"' if slot == "head" else f'minecraft:item_model="metiers:guilde_{piece}_{t}"'),
             (f'minecraft:equippable={{slot:"head",equip_sound:"minecraft:item.armor.equip_netherite"}}' if slot == "head" else
              f'minecraft:equippable={{slot:"{slot}",asset_id:"metiers:guilde_{t}",equip_sound:"minecraft:item.armor.equip_netherite"}}'),
             "minecraft:attribute_modifiers=[" + ",".join(mods) + "]",
             "minecraft:unbreakable={}", "minecraft:enchantment_glint_override=false",
             'minecraft:rarity="epic"', "minecraft:repair_cost=1000", "!minecraft:repairable"]
    return f"minecraft:netherite_{piece}[{','.join(comps)}]"

ASEL = '*[minecraft:custom_data~{metiers_armure:1b}]'
AD = []
for t in range(1, 6):
    for piece, slot, nom, _ in PIECES:
        it = piece_item(piece, slot, nom, t)
        # ordre important : on donne d'abord dans l'inventaire si l'emplacement porte une autre armure,
        # puis on équipe si l'emplacement est vide (sinon la 2e ligne voyait la pièce qu'on venait d'équiper)
        AD.append(f"$execute if score @s m.arm matches {t} if entity @s[tag=metiers.a_{slot}] run item replace entity @s armor.{slot} with {it}")
        AD.append(f"$execute if score @s m.arm matches {t} unless entity @s[tag=metiers.a_{slot}] run give @s {it}")
w(F + "armure/donner_m.mcfunction", "\n".join(AD))
w(F + "armure/donner.mcfunction", "\n".join(
    [f"tag @s remove metiers.a_{sl}" for _, sl, _, _ in PIECES] +
    [f"execute if items entity @s armor.{sl} {ASEL} run tag @s add metiers.a_{sl}" for _, sl, _, _ in PIECES] +
    [f"execute if items entity @s armor.{sl} {ASEL} run item replace entity @s armor.{sl} with minecraft:air" for _, sl, _, _ in PIECES] + [
    f"clear @s {ASEL}", "scoreboard players add @s m.aser 1",
    f"execute store result storage {NS}:tmp o int 1 run scoreboard players get @s m.id",
    f"execute store result storage {NS}:tmp s int 1 run scoreboard players get @s m.aser",
    f"function {NS}:armure/donner_m with storage {NS}:tmp"] + [f"tag @s remove metiers.a_{sl}" for _, sl, _, _ in PIECES] + [
    "playsound minecraft:item.armor.equip_netherite master @s ~ ~ ~ 1 0.8",
    "particle minecraft:totem_of_undying ~ ~1 ~ 0.4 1 0.4 0.3 60"]))

# contrôle anti-copie : un outil ou une pièce d'armure qui n'a pas le bon propriétaire ou le bon numéro de série disparaît
SC = [f"execute store result storage {NS}:sec o int 1 run scoreboard players get @s m.id",
      f"execute store result storage {NS}:sec sa int 1 run scoreboard players get @s m.aser"]
SC += [f"execute store result storage {NS}:sec s{j} int 1 run scoreboard players get @s m.{j}_ser" for j in jobs]
SC.append(f"function {NS}:securite/check_m with storage {NS}:sec")
w(F + "securite/check.mcfunction", "\n".join(SC))
CK = []
for j in jobs:
    for slot in ("weapon.mainhand", "weapon.offhand") + (("armor.feet",) if j == "x" else ()):
        CK.append(f'$execute if items entity @s {slot} *[minecraft:custom_data~{{metiers_outil:"{j}"}}] unless items entity @s {slot} *[minecraft:custom_data~{{metiers_outil:"{j}",o:$(o),s:$(s{j})}}] run function {NS}:securite/invalide {{slot:"{slot}"}}')
for _, slot, _, _ in PIECES:
    CK.append(f'$execute if items entity @s armor.{slot} *[minecraft:custom_data~{{metiers_armure:1b}}] unless items entity @s armor.{slot} *[minecraft:custom_data~{{metiers_armure:1b,o:$(o),s:$(sa)}}] run function {NS}:securite/invalide {{slot:"armor.{slot}"}}')
w(F + "securite/check_m.mcfunction", "\n".join(CK))
w(F + "securite/invalide.mcfunction", "\n".join([
    "$item replace entity @s $(slot) with minecraft:air",
    "playsound minecraft:entity.item.break master @s ~ ~ ~ 1 0.8",
    tr("Cet objet de métier n'est plus valide (copie, ancien exemplaire ou objet d'un autre joueur) : il disparaît. Le tien se récupère avec la touche G.", "red")]))
M13 = ["tag @s add metiers.v13"]
for j in jobs:
    M13.append(f'execute if items entity @s container.* *[minecraft:custom_data~{{metiers_outil:"{j}"}}] run function {NS}:{j}/outil_donner')
    M13.append(f'execute if items entity @s armor.* *[minecraft:custom_data~{{metiers_outil:"{j}"}}] run function {NS}:{j}/outil_donner')
M13.append(f"execute if score @s m.arm matches 1.. run function {NS}:armure/donner")
M13.append(tr("Tes outils et ton armure de métier ont reçu un numéro de série : les copies ne marchent plus.", "yellow"))
w(F + "migration13.mcfunction", "\n".join(M13))
w(F + "migration22.mcfunction", "\n".join(["tag @s add metiers.v22",
    f"execute if score @s m.arm matches 1.. run function {NS}:armure/donner"]))

AC = ["scoreboard players add @s m.arm 0",
      f'execute unless entity @s[tag=metiers.arm2] if score @s m.arm matches 1.. run function {NS}:appel {{f:"armure/donner"}}',
      "tag @s add metiers.arm2", "scoreboard players set @s m.tmp 0"]
AC += [f"execute if score @s m.total matches {ARM_SEUIL[t]}.. run scoreboard players set @s m.tmp {t}" for t in range(1, 6)]
AC += ["execute if score @s m.tmp <= @s m.arm run return 0",
       "scoreboard players operation @s m.arm = @s m.tmp"]
AC += [f'execute if score @s m.arm matches {t} run tellraw @a ' + PREFIX + f',{{"selector":"@s","color":"white"}},{{"text":" obtient l\'Armure des Guildes : ","color":"gray"}},{{"text":"{ARM_NOM[t]}","color":"{ARM_COL[t]}","bold":true}}]' for t in range(1, 6)]
AC += [f'function {NS}:appel {{f:"armure/donner"}}', "execute as @a at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 0.6 1.3"]
w(F + "armure/check.mcfunction", "\n".join(AC))

w(F + "armure/recup.mcfunction", "\n".join([
    "scoreboard players add @s m.arm 0",
    f"execute if score @s m.arm matches 0 run return run {tr('Ton armure se débloque à 50 points de score (somme de tes niveaux).', 'red')}",
    "scoreboard players operation @s m.tmp = @s m.acd", "scoreboard players operation @s m.tmp /= #60 m.const",
    "scoreboard players operation @s m.tmp /= #2 m.const", "scoreboard players add @s m.tmp 1",
    'execute if score @s m.acd matches 1.. run return run tellraw @s ' + PREFIX + ',{"text":"Patiente encore ","color":"red"},{"score":{"name":"@s","objective":"m.tmp"},"color":"yellow"},{"text":" min.","color":"red"}]',
    "scoreboard players set @s m.acd 1200",
    f'function {NS}:appel {{f:"armure/donner"}}',
    tr("Ton Armure des Guildes est remise à neuf : les pièces que tu portais sont remplacées, les autres sont dans ton inventaire.", "green")]))

AB = [f"execute unless items entity @s armor.{s} {ASEL} run return 0" for _, s, _, _ in PIECES]
AB += ["execute if score @s m.arm matches 1.. run effect give @s minecraft:haste 2 0 true",
       "execute if score @s m.arm matches 2.. run effect give @s minecraft:speed 2 0 true",
       "execute if score @s m.arm matches 3.. run effect give @s minecraft:resistance 2 0 true",
       "execute if score @s m.arm matches 4.. run effect give @s minecraft:regeneration 3 0 true",
       "execute if score @s m.arm matches 5.. run effect give @s minecraft:strength 2 0 true",
       "execute if score @s m.arm matches 4.. if score #huit m.timer matches 0 run particle minecraft:end_rod ~ ~1 ~ 0.35 0.6 0.35 0.01 6",
       "execute if score @s m.arm matches 5.. run particle minecraft:wax_off ~ ~1.2 ~ 0.3 0.5 0.3 0 2"]
w(F + "armure/bonus.mcfunction", "\n".join(AB))

AMN = ["scoreboard players add @s m.arm 0",
       f"execute store result storage {NS}:arm score int 1 run scoreboard players get @s m.total",
       f'data modify storage {NS}:arm nom set value "Pas encore débloquée"', f'data modify storage {NS}:arm col set value "gray"',
       f'data modify storage {NS}:arm next set value "Débloque-la à {ARM_SEUIL[1]} points"']
for t in range(1, 6):
    nxt = f"Prochain palier à {ARM_SEUIL[t + 1]} points" if t < 5 else "Palier maximum atteint"
    AMN += [f'execute if score @s m.arm matches {t} run data modify storage {NS}:arm nom set value "{ARM_NOM[t]} (palier {t}/5)"',
            f'execute if score @s m.arm matches {t} run data modify storage {NS}:arm col set value "{ARM_COL[t]}"',
            f'execute if score @s m.arm matches {t} run data modify storage {NS}:arm next set value "{nxt}"']
AMN.append(f"function {NS}:armure/menu_dialog with storage {NS}:arm")
w(F + "armure/menu.mcfunction", "\n".join(AMN))
paliers = "\\n".join(f"{t}. {ARM_NOM[t]} : {ARM_SEUIL[t]} pts, set complet + {ARM_BONUS[t]}" for t in range(1, 6))
w(F + "armure/menu_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Armure des Guildes",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:plain_message",width:320,contents:[{text:"$(nom)\\n",color:"$(col)",bold:true},'
  '{text:"Ton score : $(score) points (somme de tes niveaux, +100 par prestige)\\n$(next)\\n\\n",color:"white",bold:false},'
  f'{{text:"{paliers}\\n\\n",color:"gray"}},'
  '{text:"Les bonus se cumulent quand tu portes les 4 pièces. Incassable, ne se répare pas, évolue toute seule.",color:"dark_gray"}]}],'
  'actions:[{label:{text:"Récupérer mon armure",color:"green"},width:200,tooltip:{text:"Une fois toutes les 10 minutes."},action:{type:"run_command",command:"trigger metiers set 8"}}],'
  'columns:1,exit_action:{label:"Retour",width:150,action:{type:"run_command",command:"trigger metiers set 1"}}}')

# =====================================================================
# PÊCHEUR : série, ambiance, poissons légendaires, trésors des profondeurs
# =====================================================================
LEGENDES = [("Carpe d'or", "salmon", "gold"), ("Brochet des abysses", "cod", "dark_aqua"), ("Saumon royal", "salmon", "red"),
            ("Poisson-lune", "tropical_fish", "light_purple"), ("Anguille électrique", "cod", "yellow"),
            ("Silure géant", "cod", "dark_green"), ("Raie fantôme", "tropical_fish", "aqua"),
            ("Poisson-lanterne", "pufferfish", "gold"), ("Esturgeon millénaire", "salmon", "gray"), ("Kraken nain", "pufferfish", "dark_purple")]
PK = [f"execute if score @s m.p_timer matches ..80 run scoreboard players operation @s m.p_serie += @s s.p.fish",
      f"execute unless score @s m.p_timer matches ..80 run scoreboard players operation @s m.p_serie = @s s.p.fish",
      "scoreboard players set @s m.p_timer 0",
      "scoreboard players set @s m.p_mul 2",
      "execute if score @s m.p_serie matches 3..4 run scoreboard players add @s m.p_mul 1",
      "execute if score @s m.p_serie matches 5..7 run scoreboard players add @s m.p_mul 2",
      "execute if score @s m.p_serie matches 8.. run scoreboard players add @s m.p_mul 4",
      "scoreboard players set @s m.p_pluie 0", "scoreboard players set @s m.p_nuit 0", "scoreboard players set @s m.p_ocean 0",
      f'function {NS}:appel {{f:"p/ambiance"}}',
      "scoreboard players operation @s m.tmp = @s m.p_mul", "scoreboard players remove @s m.tmp 2",
      "scoreboard players operation @s m.tmp *= @s s.p.fish", "scoreboard players operation @s m.tmp *= #4 m.const",
      "scoreboard players operation @s m.p_bal += @s m.tmp",
      "scoreboard players set @s m.p_aff 1",
      "execute store result score #r m.tmp run random value 1..1000",
      "scoreboard players operation #thr m.tmp = @s m.p_lvl", "scoreboard players add #thr m.tmp 20",
      f"execute if score #r m.tmp <= #thr m.tmp run function {NS}:p/legende",
      "execute store result score #r m.tmp run random value 1..1000",
      "scoreboard players operation #thr m.tmp = @s m.p_lvl", "scoreboard players operation #thr m.tmp /= #2 m.const",
      "scoreboard players add #thr m.tmp 10",
      f"execute if score #r m.tmp <= #thr m.tmp run function {NS}:p/tresor"]
w(F + "p/peche.mcfunction", "\n".join(PK))
w(F + "p/ambiance.mcfunction", """
execute if predicate {type:"minecraft:weather_check",raining:true} run scoreboard players set @s m.p_pluie 1
execute if predicate {type:"minecraft:time_check",value:{min:13000,max:23000},period:24000} run scoreboard players set @s m.p_nuit 1
execute if biome ~ ~ ~ #minecraft:is_ocean run scoreboard players set @s m.p_ocean 1
execute if biome ~ ~ ~ #minecraft:is_deep_ocean run scoreboard players set @s m.p_ocean 1
scoreboard players operation @s m.p_mul += @s m.p_pluie
scoreboard players operation @s m.p_mul += @s m.p_nuit
scoreboard players operation @s m.p_mul += @s m.p_ocean
""")
AF = []
for m in range(2, 10):
    txt = f"x{m // 2}" + (",5" if m % 2 else "")
    AF.append(f'execute if score @s m.p_mul matches {m} run data modify storage {NS}:peche mul set value "{txt}"')
AF += [f'data modify storage {NS}:peche amb set value ""',
       f'execute if score @s m.p_pluie matches 1 run data modify storage {NS}:peche amb set value " · pluie"',
       f'execute if score @s m.p_nuit matches 1 run data modify storage {NS}:peche amb2 set value " · nuit"',
       f'execute unless score @s m.p_nuit matches 1 run data modify storage {NS}:peche amb2 set value ""',
       f'execute if score @s m.p_ocean matches 1 run data modify storage {NS}:peche amb3 set value " · océan"',
       f'execute unless score @s m.p_ocean matches 1 run data modify storage {NS}:peche amb3 set value ""',
       f"execute store result storage {NS}:peche serie int 1 run scoreboard players get @s m.p_serie",
       f"execute store result storage {NS}:peche gain int 1 run scoreboard players get @s m.gain",
       f"function {NS}:p/affiche_m with storage {NS}:peche",
       "scoreboard players set @s m.p_aff 0"]
w(F + "p/affiche.mcfunction", "\n".join(AF))
w(F + "p/affiche_m.mcfunction",
  '$title @s actionbar [{"text":"+$(gain) XP Pêcheur  ","color":"aqua"},{"text":"Série $(serie) ","color":"yellow","bold":true},'
  '{"text":"$(mul)","color":"gold","bold":true},{"text":"$(amb)$(amb2)$(amb3)","color":"gray"}]')
LG = ["execute store result score #f m.tmp run random value 1..10"]
for i, (nom, base, col) in enumerate(LEGENDES, 1):
    item = (f'minecraft:{base}[minecraft:custom_name={{text:"{nom}",color:"{col}",bold:true,italic:false}},'
            f'minecraft:lore=[{{text:"Prise légendaire {i}/10",color:"gray",italic:false}},{{text:"Trophée du Carnet du pêcheur",color:"dark_aqua",italic:false}}],'
            f'minecraft:custom_data={{metiers_legende:{i}}},minecraft:rarity="epic",minecraft:enchantment_glint_override=true,minecraft:max_stack_size=1]')
    w(F + f"p/leg_{i}.mcfunction", "\n".join([
        f"give @s {item} 1",
        "scoreboard players add @s m.p_bal 50",
        f'tellraw @a ' + PREFIX + f',{{"selector":"@s","color":"white"}},{{"text":" a pêché une prise légendaire : ","color":"gray"}},{{"text":"{nom}","color":"{col}","bold":true}}]',
        f'execute unless score @s m.p_l{i} matches 1 run tellraw @s ' + PREFIX + f',{{"text":"Nouvelle espèce dans ton Carnet du pêcheur !","color":"aqua","bold":true}}]',
        f"scoreboard players set @s m.p_l{i} 1",
        "playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1.4",
        "particle minecraft:bubble_column_up ~ ~0.5 ~ 0.6 0.4 0.6 0.1 60",
        f"function {NS}:p/carnet_check"]))
    LG.append(f"execute if score #f m.tmp matches {i} run function {NS}:p/leg_{i}")
w(F + "p/legende.mcfunction", "\n".join(LG))
CK = ["scoreboard players set @s m.tmp 0"] + [f"execute if score @s m.p_l{i} matches 1 run scoreboard players add @s m.tmp 1" for i in range(1, 11)]
CK += ["execute if score @s m.p_legok matches 1 run return 0",
       "execute unless score @s m.tmp matches 10 run return 0",
       "scoreboard players set @s m.p_legok 1",
       "give @s minecraft:enchanted_golden_apple 5", "give @s minecraft:netherite_ingot 3", "give @s minecraft:heart_of_the_sea 1",
       "scoreboard players add @s m.p_bal 500",
       'tellraw @a ' + PREFIX + ',{"selector":"@s","color":"white"},{"text":" a complété le Carnet du pêcheur : les 10 légendes ! ","color":"aqua","bold":true}]',
       "execute as @a at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 0.6"]
w(F + "p/carnet_check.mcfunction", "\n".join(CK))
TRES = ["shipwreck_treasure", "buried_treasure", "ancient_city", "ruined_portal", "underwater_ruin_big", "desert_pyramid"]
TR = ["execute store result score #f m.tmp run random value 1..6"]
TR += [f"execute if score #f m.tmp matches {i} run loot give @s loot minecraft:chests/{t}" for i, t in enumerate(TRES, 1)]
TR += ['tellraw @a ' + PREFIX + ',{"selector":"@s","color":"white"},{"text":" remonte un coffre des profondeurs !","color":"dark_aqua","bold":true}]',
       "playsound minecraft:block.chest.open master @s ~ ~ ~ 1 0.8",
       "particle minecraft:bubble ~ ~0.5 ~ 0.6 0.4 0.6 0.1 40"]
w(F + "p/tresor.mcfunction", "\n".join(TR))
CA = []
for i, (nom, base, col) in enumerate(LEGENDES, 1):
    CA += [f'data modify storage {NS}:carnet n{i} set value "???"', f'data modify storage {NS}:carnet c{i} set value "dark_gray"',
           f'execute if score @s m.p_l{i} matches 1 run data modify storage {NS}:carnet n{i} set value "✔ {nom}"',
           f'execute if score @s m.p_l{i} matches 1 run data modify storage {NS}:carnet c{i} set value "{col}"']
CA += ["scoreboard players set @s m.tmp 0"] + [f"execute if score @s m.p_l{i} matches 1 run scoreboard players add @s m.tmp 1" for i in range(1, 11)]
CA += [f"execute store result storage {NS}:carnet nb int 1 run scoreboard players get @s m.tmp",
       f"function {NS}:p/carnet_dialog with storage {NS}:carnet"]
w(F + "p/carnet.mcfunction", "\n".join(CA))
lignes = ",".join(f'{{text:"$(n{i})\\n",color:"$(c{i})",bold:true}}' for i in range(1, 11))
w(F + "p/carnet_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:notice",title:{text:"Carnet du pêcheur",color:"aqua",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:plain_message",width:300,contents:[{text:"Légendes trouvées : $(nb)/10\\n\\n",color:"yellow"},' + lignes + ']},'
  '{type:"minecraft:plain_message",width:300,contents:{text:"Chaque prise a une chance d\'être légendaire (2 % au niveau 1, 12 % au niveau 100). '
  'Collection complète : 5 pommes de Notch, 3 lingots de netherite, un cœur de la mer et 500 XP Pêcheur.",color:"gray"}}],'
  'action:{label:"Retour",width:150,action:{type:"run_command",command:"trigger metiers set 25"}}}')

# =====================================================================
# ADMIN
# =====================================================================
CL = ["tag @s add metiers.req"]
for j, d in jobs.items():
    CL.append(f'tellraw @s {{"text":"{d["name"]} :","color":"{d["color"]}"}}')
    CL.append(f'execute as @a run tellraw @p[tag=metiers.req] [{{"text":"  "}},{{"selector":"@s"}},{{"text":" niv ","color":"gray"}},{{"score":{{"name":"@s","objective":"m.{j}_lvl"}},"color":"yellow"}}]')
CL.append("tag @s remove metiers.req")
w(F + "classement.mcfunction", "\n".join(CL))

ALLTAGS = [f"metiers.sk.{j}{k}" for j in jobs for k in range(1, 7)]
w(F + "reset_joueur.mcfunction", "\n".join(
    ["tag @s remove metiers.ok", "tag @s remove metiers.v2", "tag @s remove metiers.v3", "team leave @s",
     f"advancement revoke @s from {NS}:b/racine", f"advancement revoke @s from {NS}:f/racine",
     f"advancement revoke @s from {NS}:m/racine", f"advancement revoke @s from {NS}:c/racine",
     f"advancement revoke @s from {NS}:p/racine", "scoreboard players set @s m.pref 0"] +
    [f"tag @s remove {t}" for t in ALLTAGS] +
    [f"scoreboard players set @s m.{j}_{k} 0" for j in jobs for k in ("spent", "pal")] +
    [f"function {NS}:init", f"function {NS}:migration"]))

U = [f"schedule clear {NS}:loop"]
for mod in ("c1", "c5", "chasseur"):
    U.append(f"execute as @a run attribute @s minecraft:attack_damage modifier remove {NS}:{mod}")
for mod in ("p1", "p6", "pecheur"):
    U.append(f"execute as @a run attribute @s minecraft:luck modifier remove {NS}:{mod}")
U += ["tag @a remove metiers.ok", "tag @a remove metiers.v2", "tag @a remove metiers.v3",
      f"advancement revoke @a from {NS}:b/racine", f"advancement revoke @a from {NS}:f/racine",
      f"advancement revoke @a from {NS}:m/racine", f"advancement revoke @a from {NS}:c/racine",
      f"advancement revoke @a from {NS}:p/racine"] + [f"tag @a remove {t}" for t in ALLTAGS]
for o in ("m.tmp", "m.gain", "m.const", "m.timer", "m.pref", "m.trig", "metiers"):
    U.append(f"scoreboard objectives remove {o}")
for j in jobs:
    for k in ("lvl", "xp", "need", "bal", "spent", "pal"):
        U.append(f"scoreboard objectives remove m.{j}_{k}")
    for t in range(11):
        for st in range(6):
            U.append(f"team remove m.{j}{t}_{st}")
for _, _, _, obj, _ in ALL_STATS:
    U.append(f"scoreboard objectives remove s.{obj}")
for l in LOGS:
    U.append(f"scoreboard objectives remove a.{l}")
U.append("scoreboard objectives remove a.sneak")
U.append("scoreboard objectives remove m.quit")
U.append("scoreboard objectives remove m.dmg")
U += ["scoreboard objectives remove m.arm", "scoreboard objectives remove m.acd"]
for o in ("m.id", "m.dshow", "m.dall", "m.defi", "m.heure", "m.boss", "m.total"):
    U.append(f"scoreboard objectives remove {o}")
for j in jobs:
    for k in ("pr", "out", "cd", "st"):
        U.append(f"scoreboard objectives remove m.{j}_{k}")
    U += [f"scoreboard objectives remove m.dp_{j}", f"scoreboard objectives remove m.dd_{j}"]
for j, pool in DEFIS.items():
    for i, (desc, tgt, crits, div) in enumerate(pool, 1):
        for n, cr in enumerate(crits):
            U.append(f"scoreboard objectives remove dq.{j}{i}_{n}")
U += ["bossbar remove metiers:heure", "bossbar remove metiers:boss", "tag @a remove metiers.v6",
      "kill @e[tag=metiers.boss]", "kill @e[tag=metiers.sbire]", "execute in minecraft:overworld run forceload remove 0 0"]
U.append("tag @a remove metiers.v4")
U.append("tag @a remove metiers.v5")
U.append('tellraw @s {"text":"[Métiers] Désinstallé. Retire le zip du dossier datapacks puis redémarre.","color":"gold"}')
w(F + "desinstaller.mcfunction", "\n".join(U))

# =====================================================================
zp = "/home/claude/metiers.zip"
if os.path.exists(zp):
    os.remove(zp)
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, _, fs in os.walk(ROOT):
        for fn in sorted(fs):
            full = os.path.join(dp, fn)
            z.write(full, os.path.relpath(full, ROOT))
print("fichiers :", sum(len(f) for _, _, f in os.walk(ROOT)))

# -*- coding: utf-8 -*-
# Barème d'XP illustré : une page par métier (touche G, Barème d'XP, ou le bouton de la page du métier).
# Les valeurs sont lues dans les tables de datapack.py (STONES, ORES, CROPS, MOBS...) : le barème suit tout seul
# si un poids change. Les images sont les textures du jeu (composant de texte « object », atlas items et blocks).

def fr_num(x):
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return s.replace(".", ",")

IT = lambda p: f'{{object:"atlas",atlas:"minecraft:items",sprite:"minecraft:item/{p}"}}'
BL = lambda p: f'{{object:"atlas",atlas:"minecraft:blocks",sprite:"minecraft:block/{p}"}}'
EGG = lambda m: IT(f"{m}_spawn_egg")
BAREME_SPRITES = set()   # chemins utilisés (contrôlés au build)

def spr(kind, p):
    BAREME_SPRITES.add(f"{'item' if kind == 'i' else 'block'}/{p}")
    return IT(p) if kind == "i" else BL(p)

NOM_MOB = {"chicken": "Poulet", "cow": "Vache", "pig": "Cochon", "sheep": "Mouton", "rabbit": "Lapin", "goat": "Chèvre",
           "mooshroom": "Champimeuh", "silverfish": "Poisson d'argent", "slime": "Slime", "magma_cube": "Cube de magma",
           "zombie": "Zombie", "husk": "Zombie momifié", "zombie_villager": "Zombie-villageois", "spider": "Araignée",
           "piglin": "Piglin", "zombified_piglin": "Piglin zombifié", "drowned": "Noyé", "skeleton": "Squelette",
           "cave_spider": "Araignée venimeuse", "vex": "Vex", "stray": "Vagabond", "bogged": "Embourbé", "creeper": "Creeper",
           "phantom": "Phantom", "pillager": "Pillard", "witch": "Sorcière", "enderman": "Enderman", "blaze": "Blaze",
           "guardian": "Gardien", "hoglin": "Hoglin", "creaking": "Grinceur", "vindicator": "Vindicateur", "shulker": "Shulker",
           "zoglin": "Zoglin", "ghast": "Ghast", "wither_skeleton": "Wither squelette", "breeze": "Breeze",
           "piglin_brute": "Piglin brutal", "evoker": "Évocateur", "ravager": "Ravageur",
           "wither": "Wither", "ender_dragon": "Ender Dragon", "warden": "Warden", "elder_guardian": "Gardien ancien"}
NOM_PIERRE = {"stone": "Roche", "deepslate": "Ardoise des abîmes", "andesite": "Andésite", "diorite": "Diorite", "granite": "Granite",
              "tuff": "Tuf", "blackstone": "Roche noire", "netherrack": "Netherrack", "basalt": "Basalte", "smooth_basalt": "Basalte lisse",
              "calcite": "Calcite", "dripstone_block": "Spéléothème", "end_stone": "Pierre de l'End", "sandstone": "Grès",
              "red_sandstone": "Grès rouge", "obsidian": "Obsidienne", "crying_obsidian": "Obsidienne pleureuse"}
NOM_MINERAI = {"coal": "Charbon", "copper": "Cuivre", "iron": "Fer", "gold": "Or", "redstone": "Redstone", "lapis": "Lapis-lazuli",
               "diamond": "Diamant", "emerald": "Émeraude"}
TEX_BLOC = {"basalt": "basalt_side", "ancient_debris": "ancient_debris_side", "melon": "melon_side", "pumpkin": "pumpkin_side",
            "cactus": "cactus_side", "sandstone": "sandstone", "red_sandstone": "red_sandstone"}
NOM_BOIS = {"oak_log": "Chêne", "spruce_log": "Sapin", "birch_log": "Bouleau", "jungle_log": "Acajou", "acacia_log": "Acacia",
            "dark_oak_log": "Chêne noir", "mangrove_log": "Palétuvier", "cherry_log": "Cerisier", "pale_oak_log": "Chêne pâle",
            "crimson_stem": "Tige carmin", "warped_stem": "Tige biscornue"}
NOM_CULTURE = {"wheat": "Blé", "carrot": "Carotte", "potato": "Pomme de terre", "beetroot": "Betterave", "nether_wart": "Verrue du Nether",
               "sweet_berries": "Baies sucrées", "glow_berries": "Baies lumineuses", "melon": "Pastèque", "pumpkin": "Citrouille",
               "sugar_cane": "Canne à sucre", "cocoa": "Cacao", "cactus": "Cactus"}
TEX_CULTURE = {"sugar_cane": ("i", "sugar_cane"), "cocoa": ("i", "cocoa_beans")}


def nom_minerai(o):
    if o == "ancient_debris": return "Débris antiques"
    if o == "nether_gold_ore": return "Or du Nether"
    if o == "nether_quartz_ore": return "Quartz du Nether"
    base = o.replace("deepslate_", "").replace("_ore", "")
    return NOM_MINERAI[base] + (" (abîmes)" if o.startswith("deepslate_") else "")


def entree(img, nom, col="white"):
    return f'{img},{{text:" {nom}   ",color:"{col}"}}'


def groupes(items, unite="XP"):
    """items : [(valeur, image, nom)] -> une ligne par valeur, de la plus haute à la plus basse."""
    par = {}
    for v, img, nom in items:
        par.setdefault(v, []).append((img, nom))
    out = []
    for v in sorted(par, reverse=True):
        out.append(f'{{text:"\\n{fr_num(v)} {unite}  ",color:"gold",bold:true}}')
        out += [entree(img, nom) for img, nom in par[v]]
    return out


def titre(t, col="yellow"):
    return f'{{text:"\\n\\n{t}",color:"{col}",bold:true}}'


def note(t):
    return f'{{text:"\\n{t}",color:"gray"}}'


BONUS = ('{text:"\\n\\nBonus : ",color:"aqua",bold:true},{text:"x2 pendant l’heure du métier, +10 % par étoile de prestige, '
         '+10 % avec le cristal de Sagesse sur l’outil. Poser ou jeter ce que tu viens de récolter retire l’XP gagnée. '
         'Niveau suivant : 150 XP au niveau 1, puis +6 % à chaque niveau (2 607 au niveau 50, 45 297 au niveau 99), plus 45 297 par étoile de prestige.",color:"gray"}')
DEFI = note("Défi du jour réussi : la moitié d’un niveau du métier, 2 diamants et 16 fioles d’expérience.")

PAGES = {}
# ---------------------------------------------------------------- Bûcheron
PAGES["b"] = [note("Chaque bloc de tronc cassé : bûche, bois, bûche ou bois écorcé. L’Abattage compte chaque bûche de l’arbre.")] + \
    groupes([(1, spr("b", l), NOM_BOIS[l]) for l in LOGS]) + [DEFI]
# ---------------------------------------------------------------- Fermier
d_f = DIV["f"]
PAGES["f"] = [titre("Récolte ramassée (par objet)")] + groupes(
    [(x / d_f, spr("i", c), NOM_CULTURE[c]) for c, x in CROPS.items()]) + [titre("Bloc cassé")] + groupes(
    [(x / d_f, spr(*TEX_CULTURE.get(c, ("b", TEX_BLOC.get(c, c)))), NOM_CULTURE[c]) for c, (x, _, _) in CROP_BLOCKS.items()]) + [
    note("Replanter carottes, patates, verrues et baies est gratuit : seule la graine posée en trop retire de l’XP."), DEFI]
# ---------------------------------------------------------------- Mineur
d_m = DIV["m"]
PAGES["m"] = [titre("Minerais")] + groupes([(x / d_m, spr("b", TEX_BLOC.get(o, o)), nom_minerai(o)) for o, x in ORES.items()]) + \
    [titre("Pierres")] + groupes([(x / d_m, spr("b", TEX_BLOC.get(s, s)), NOM_PIERRE[s]) for s, x in STONES.items()]) + [DEFI]
# ---------------------------------------------------------------- Chasseur
# Chasseur : deux onglets (créatures fortes / faibles et boss) pour ne pas faire défiler
PAGES["c"] = [titre("Créatures à 5 XP et plus")] + groupes([(x, spr("i", f"{m}_spawn_egg"), NOM_MOB[m]) for m, x in MOBS.items() if x >= 5]) + [
    note("Créatures d’un spawner acheté au Commerce : la moitié de l’XP. Pas d’XP quand tu es AFK."), DEFI]
PAGES["c2"] = [titre("Créatures à moins de 5 XP")] + groupes([(x, spr("i", f"{m}_spawn_egg"), NOM_MOB[m]) for m, x in MOBS.items() if x < 5]) + \
    [titre("Boss du jeu")] + groupes([(x, spr("i", f"{b}_spawn_egg"), NOM_MOB[b]) for b, x in BOSSES.items()]) + [
    note("Boss du serveur (Colosse, Reine, Liche, Brasier, Creeper géant) : la moitié d’un niveau de Chasseur pour chaque participant, plus butin et éclats.")]
# ---------------------------------------------------------------- Pêcheur
w_peche = [s for s in jobs["p"]["src"] if s[0].endswith("fish_caught")][0][1]
PAGES["p"] = [f'{{text:"\\n{w_peche} XP  ",color:"gold",bold:true}}', entree(spr("i", "cod"), "chaque prise (poisson, trésor ou déchet)"),
              titre("Multiplicateurs (ils s’additionnent)"),
              f'{{text:"\\n+0,5  ",color:"gold",bold:true}}', entree(spr("i", "water_bucket"), "sous la pluie"),
              entree(spr("i", "clock_00"), "la nuit"), entree(spr("i", "heart_of_the_sea"), "en océan"),
              f'{{text:"\\nSérie  ",color:"gold",bold:true}}', entree(spr("i", "fishing_rod"), "prises rapprochées : +0,5 dès 3, +1 dès 5, +2 dès 8"),
              note(f"Exemple : la nuit, sous la pluie, en océan, 8e prise d’affilée : x4,5, soit {int(w_peche * 4.5)} XP."),
              titre("Prises spéciales"),
              f'{{text:"\\n+50 XP  ",color:"gold",bold:true}}', entree(spr("i", "tropical_fish"), "prise légendaire (2 % au niveau 0, 12 % au niveau 100)"),
              f'{{text:"\\n+500 XP  ",color:"gold",bold:true}}', entree(spr("i", "book"), "Carnet du pêcheur complet (les 10 légendes)"),
              note("Coffre des profondeurs : 1 % au niveau 0, 6 % au niveau 100, sans XP mais avec un butin de trésor."), DEFI]
# ---------------------------------------------------------------- Éleveur
d_e = DIV["e"]
w_bred = [s for s in jobs["e"]["src"] if s[0].endswith("animals_bred")][0][1]
PAGES["e"] = groupes([(w_bred / d_e, spr("i", "cow_spawn_egg"), "naissance d’un animal que tu fais reproduire"),
                      (1 / d_e, spr("b", "white_wool"), "laine ramassée (par bloc, toutes couleurs)")]) + [
    note("Les animaux d’un spawner acheté au Commerce ne se reproduisent pas et ses moutons restent tondus."), DEFI]
# ---------------------------------------------------------------- Enchanteur
w_shelf = [s for s in jobs["n"]["src"] if s[0].endswith("bookshelf")][0][1]
PAGES["n"] = [titre("Table d’enchantement")] + groupes([(60, spr("b", "enchanting_table_top"), "enchantement à 3 niveaux"),
                                                         (40, spr("b", "enchanting_table_top"), "enchantement à 2 niveaux"),
                                                         (20, spr("b", "enchanting_table_top"), "enchantement à 1 niveau")]) + \
    groupes([(w_shelf, spr("b", "bookshelf"), "bibliothèque fabriquée (casser une bibliothèque la retire)")]) + [DEFI]
# ---------------------------------------------------------------- Explorateur (1 XP tous les 20 m à pied, versé par tranche de 200 m)
BASE_M = 20
DIST = [("walk_one_cm", "i", "leather_boots", "à pied"), ("sprint_one_cm", "i", "sugar", "en courant"),
        ("climb_one_cm", "b", "ladder", "en grimpant"), ("crouch_one_cm", "i", "leather_leggings", "accroupi"),
        ("swim_one_cm", "i", "water_bucket", "à la nage"), ("horse_one_cm", "i", "saddle", "à cheval"),
        ("boat_one_cm", "i", "oak_boat", "en bateau"), ("aviate_one_cm", "i", "elytra", "en élytres")]
dist_items = []
for st, k, tex, lib in DIST:
    m = BASE_M * XDIV.get(st, 1) / XMUL.get(st, 1)
    dist_items.append((m, spr(k, tex), lib))
PAGES["x"] = [titre("1 XP tous les...")] + groupes(dist_items, "m") + [titre("Découvertes (une fois chacune)")] + groupes(
    [(60, spr("i", "map"), f"nouvelle structure ({len(STRUCTS)} : villages, temples, forteresses...)"),
     (40, spr("i", "compass_00"), f"nouveau biome ({len(BIOMES)})")]) + [note("L’XP de distance arrive par tranche de 200 m (10 XP d’un coup)."), DEFI]
# ---------------------------------------------------------------- Marchand
w_trade = [s for s in jobs["t"]["src"] if s[0].endswith("traded_with_villager")][0][1]
PAGES["t"] = groupes([(w_trade, spr("i", "emerald"), "échange avec un villageois (chaque échange)")]) + [DEFI]

# ---------------------------------------------------------------- Bâtisseur (familles de blocs, valeur lue dans BLOCS_K)
d_k = DIV["k"]
FAM_K = [("quartz_block", "b", "quartz_block_side", "Quartz (bloc, briques, pilier, lisse)"),
         ("end_stone_bricks", "b", "end_stone_bricks", "Briques de l’End"), ("prismarine_bricks", "b", "prismarine_bricks", "Prismarine taillée et sombre"),
         ("white_glazed_terracotta", "b", "white_glazed_terracotta", "Terre cuite émaillée"),
         ("stone_bricks", "b", "stone_bricks", "Briques de pierre (toutes)"), ("bricks", "b", "bricks", "Briques et briques de boue"),
         ("white_concrete", "b", "white_concrete", "Béton (16 couleurs)"), ("terracotta", "b", "terracotta", "Terre cuite (et colorée)"),
         ("glass", "b", "glass", "Verre et vitraux"), ("deepslate_tiles", "b", "deepslate_tiles", "Ardoise taillée et carrelage"),
         ("polished_andesite", "b", "polished_andesite", "Pierres polies, tuf taillé"), ("oak_door", "i", "oak_door", "Porte en bois"),
         ("lantern", "i", "lantern", "Lanterne"), ("oak_planks", "b", "oak_planks", "Planches (12 bois)"),
         ("oak_slab", "b", "oak_planks", "Escaliers, dalles, barrières, trappes"), ("cobblestone", "b", "cobblestone", "Pierre taillée et pavés"),
         ("glass_pane", "b", "glass", "Vitres"), ("ladder", "b", "ladder", "Échelles, chaînes, barreaux")]
PAGES["k"] = [note("Tout bloc posé rapporte un peu, les blocs de construction beaucoup plus. Casser un bloc de construction retire ce qu’il a rapporté.")] + \
    [titre("Bonus en plus du bloc posé")] + groupes([(BLOCS_K[b] / d_k, spr(kd, tex), nom) for b, kd, tex, nom in FAM_K]) + \
    [titre("Tous les blocs")] + groupes([(1 / d_k, spr("b", "dirt"), "n’importe quel bloc posé (terre, sable, roche...), 2 XP par minute au plus"),
                                        (2, spr("i", "emerald"), "en plus, un bloc acheté au Commerce (256 par jour au plus)")]) + [DEFI]

BAREME_INTRO = {"b": "Tout ce qui sort d’un tronc.", "f": "Les cultures, ramassées ou cassées.", "m": "Les minerais et les pierres cassés.",
                "c": "Chaque créature tuée.", "p": "Chaque prise, avec des multiplicateurs.", "e": "Les naissances et la laine.",
                "n": "Les niveaux dépensés à la table.", "x": "La distance parcourue et les découvertes.", "t": "Les échanges avec les villageois.",
                "k": "Les blocs de construction posés."}
BAN_B = '{type:"minecraft:plain_message",width:310,contents:[{text:""},{text:"\ue02b",font:"commerce:recette",color:"white",shadow_color:0},{text:"\\n\\n"}]}'
w(F + "bareme/c2.mcfunction",
  f'dialog show @s {{type:"minecraft:multi_action",title:[{gs("metier_c")},{{text:" Barème d’XP : Chasseur (2/2)",color:"red",bold:true}}],'
  f'can_close_with_escape:true,pause:false,body:[{BAN_B},{{type:"minecraft:plain_message",width:420,contents:[{{text:""}},{",".join(PAGES["c2"])}]}}],'
  f'actions:[{btn(txt("◀ Créatures fortes", "red", True), 484, 200)},{btn(txt("Tous les barèmes", "white"), 480, 200)}],columns:2,'
  f'exit_action:{{label:"Fermer",width:200}}}}')
add_lines(F + "trigger.mcfunction", [f'execute if score @s m.trig matches 491 run function {NS}:appel {{f:"bareme/c2"}}'])
for j, d in jobs.items():
    contenu = [f'{{text:"{BAREME_INTRO[j]}",color:"white"}}'] + PAGES[j] + [BONUS,
               f'{{text:"\\n\\nPrestige ",color:"gold",bold:true}},{{text:"(niveau 100, 5 étoiles) : tu gardes tes compétences, la progression continue, +10 % d’XP par étoile et la capacité ",color:"gray"}},{{text:"{PCAP[j][0]}",color:"gold",bold:true}},{{text:" : {PCAP[j][1]}",color:"gray"}}']
    w(F + f"bareme/{j}.mcfunction",
      f'dialog show @s {{type:"minecraft:multi_action",title:[{gs("metier_" + j)},{{text:" Barème d’XP : {d["name"]}",color:"{d["color"]}",bold:true}}],'
      f'can_close_with_escape:true,pause:false,body:[{BAN_B},{{type:"minecraft:plain_message",width:420,contents:[{{text:""}},{",".join(contenu)}]}}],'
      f'actions:[{btn(txt("Page du métier", d["color"]), 20 + d["idx"], 200)},{btn(txt("Tous les barèmes", "white"), 480, 200)}' +
      (f',{btn(txt("Créatures faibles et boss ▶", "red", True), 491, 404)}' if j == "c" else "") + '],columns:2,'
      f'exit_action:{{label:"Fermer",width:200}}}}')
hub = [btn(f'[{gs("metier_" + j)},{txt(" " + d["name"], d["color"])}]', 480 + d["idx"], 130, BAREME_INTRO[j]) for j, d in jobs.items()]
w(F + "bareme/menu.mcfunction",
  f'dialog show @s {{type:"minecraft:multi_action",title:{{text:"Barème d’XP",color:"gold",bold:true}},can_close_with_escape:true,pause:false,'
  f'body:[{{type:"minecraft:plain_message",width:400,contents:{{text:"Ce que rapporte chaque action, métier par métier, avec les images du jeu.",color:"gray"}}}}],'
  f'actions:[{",".join(hub)}],columns:3,exit_action:{{label:"Retour",width:200,action:{{type:"run_command",command:"trigger metiers set 1"}}}}}}')
add_lines(F + "trigger.mcfunction", [f'execute if score @s m.trig matches 480 run function {NS}:appel {{f:"bareme/menu"}}'] +
          [f'execute if score @s m.trig matches {480 + d["idx"]} run function {NS}:appel {{f:"bareme/{j}"}}' for j, d in jobs.items()])
json.dump(sorted(BAREME_SPRITES), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "bareme_sprites.json"), "w"))

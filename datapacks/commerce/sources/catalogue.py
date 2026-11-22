# -*- coding: utf-8 -*-
# Catalogue du Commerce : tout ce que le serveur rachète et vend.
#
# Une ligne = (id Minecraft, nom affiché, prix de vente de base en Écus, volume de référence, métier lié)
#   - prix de vente : ce que le serveur paie à l'unité quand le marché est calme.
#     Le rachat coûte ACHAT fois plus et ne baisse jamais sous ce niveau (ni krach, ni marché saturé).
#   - volume de référence : nombre d'unités qui saturent le marché (prix au plancher, 30 % de la base) ;
#     le marché se remet en une heure de jeu environ.
#   - métier lié : +0,5 % par niveau, +25 % pendant l'heure du métier.
#     b Bûcheron, f Fermier, m Mineur, c Chasseur, p Pêcheur, e Éleveur, n Enchanteur, x Explorateur, t Marchand.
#
# Cohérence (contrôlée par coherence.py avec les recettes de la 26.1) : un objet fabriqué ou cuit ne se vend
# pas plus de 5 % au-dessus de ses ingrédients, sinon on pourrait racheter, crafter et revendre avec profit
# en cumulant bonus de métier, pénurie et marché tendu (x3,64 au plus, contre x4 au rachat).

ACHAT = 4

CATEGORIES = [
    # (numéro, nom, objet vitrine, couleur, description)
    (1, "Pierres", "stone_bricks", "gray", "Roches, briques, grès, prismarine"),
    (2, "Terre et glace", "grass_block", "green", "Terre, sable, gravier, argile, neige, glace"),
    (16, "Fleurs et plantes", "poppy", "red", "Fleurs, herbes, champignons, lianes"),
    (3, "Bûches", "oak_log", "gold", "Bûches et bûches écorcées"),
    (4, "Planches et feuillage", "oak_planks", "gold", "Planches, feuilles, pousses, bâtons"),
    (5, "Laines et teintures", "red_wool", "red", "16 couleurs de laine et de teinture"),
    (6, "Béton et terre cuite", "cyan_concrete", "aqua", "Béton et terre cuite de toutes les couleurs"),
    (7, "Verre", "light_blue_stained_glass", "aqua", "Verre, vitres, verre teinté, terre cuite émaillée"),
    (8, "Minerais et métaux", "iron_ingot", "white", "Charbon, fer, or, cuivre, redstone, lapis, blocs"),
    (9, "Nether et End", "quartz_block", "dark_red", "Roche noire, quartz, verrues, purpur"),
    (10, "Agriculture", "wheat", "green", "Récoltes, graines, sucre, papier, botte de foin"),
    (11, "Élevage et chasse", "leather", "light_purple", "Viandes, laine, butin des créatures"),
    (12, "Pêche", "salmon", "aqua", "Poissons et ressources de l'océan"),
    (13, "Cuisine", "bread", "yellow", "Plats cuits et préparés"),
    (14, "Utilitaires", "lantern", "#F1CF4E", "Éclairage, rangement, rails, redstone, outils"),
    (15, "Trésors", "diamond", "light_purple", "Vente seulement : le serveur ne les revend pas"),
]
RARES = {15}

COULEURS = [  # id, masculin, féminin, prix de la teinture
    ("white", "blanc", "blanche", 0.12), ("orange", "orange", "orange", 0.15), ("magenta", "magenta", "magenta", 0.15),
    ("light_blue", "bleu clair", "bleu clair", 0.16), ("yellow", "jaune", "jaune", 0.15), ("lime", "vert clair", "vert clair", 0.22),
    ("pink", "rose", "rose", 0.14), ("gray", "gris", "grise", 0.26), ("light_gray", "gris clair", "gris clair", 0.15),
    ("cyan", "cyan", "cyan", 0.28), ("purple", "violet", "violette", 0.17), ("blue", "bleu", "bleue", 0.20),
    ("brown", "marron", "marron", 0.45), ("green", "vert", "verte", 0.36), ("red", "rouge", "rouge", 0.15),
    ("black", "noir", "noire", 0.45),
]
BOIS = [  # id, nom de l'essence, prix de la bûche, id de la pousse, nom de la pousse
    ("oak", "chêne", 2.0, "oak_sapling", "Pousse de chêne"), ("spruce", "sapin", 2.0, "spruce_sapling", "Pousse de sapin"),
    ("birch", "bouleau", 2.0, "birch_sapling", "Pousse de bouleau"), ("jungle", "acajou", 2.0, "jungle_sapling", "Pousse d'acajou"),
    ("acacia", "acacia", 2.0, "acacia_sapling", "Pousse d'acacia"), ("dark_oak", "chêne noir", 2.0, "dark_oak_sapling", "Pousse de chêne noir"),
    ("mangrove", "palétuvier", 2.0, "mangrove_propagule", "Propagule de palétuvier"),
    ("cherry", "cerisier", 2.5, "cherry_sapling", "Pousse de cerisier"), ("pale_oak", "chêne pâle", 2.5, "pale_oak_sapling", "Pousse de chêne pâle"),
]
NETHER_BOIS = [("crimson", "carmin", 2.5, "crimson_fungus", "Champignon carmin"), ("warped", "biscornu", 2.5, "warped_fungus", "Champignon biscornu")]


def _r(x):
    return round(x, 2)


ITEMS = {c: [] for c, *_ in CATEGORIES}
I = lambda c, *t: ITEMS[c].append(t)

# 1 Pierres --------------------------------------------------------------
for t in [
    ("cobblestone", "Pierre taillée", 0.05, 4096, "m"), ("mossy_cobblestone", "Pierre taillée moussue", 0.15, 1024, "m"),
    ("stone", "Roche", 0.10, 2048, "m"), ("smooth_stone", "Roche lisse", 0.12, 1024, ""),
    ("stone_bricks", "Briques de pierre", 0.10, 1024, ""), ("mossy_stone_bricks", "Briques de pierre moussues", 0.15, 1024, ""),
    ("cracked_stone_bricks", "Briques de pierre craquelées", 0.12, 1024, ""), ("chiseled_stone_bricks", "Briques de pierre sculptées", 0.10, 1024, ""),
    ("granite", "Granite", 0.08, 2048, "m"), ("polished_granite", "Granite poli", 0.08, 1024, ""),
    ("diorite", "Diorite", 0.08, 2048, "m"), ("polished_diorite", "Diorite polie", 0.08, 1024, ""),
    ("andesite", "Andésite", 0.06, 2048, "m"), ("polished_andesite", "Andésite polie", 0.06, 1024, ""),
    ("deepslate", "Ardoise des abîmes", 0.12, 2048, "m"), ("cobbled_deepslate", "Ardoise taillée", 0.06, 4096, "m"),
    ("polished_deepslate", "Ardoise polie", 0.06, 1024, ""), ("deepslate_bricks", "Briques d'ardoise", 0.06, 1024, ""),
    ("deepslate_tiles", "Carreaux d'ardoise", 0.06, 1024, ""), ("chiseled_deepslate", "Ardoise sculptée", 0.06, 1024, ""),
    ("tuff", "Tuf", 0.10, 2048, "m"), ("polished_tuff", "Tuf poli", 0.10, 1024, ""), ("tuff_bricks", "Briques de tuf", 0.10, 1024, ""),
    ("calcite", "Calcite", 0.20, 1024, "m"), ("dripstone_block", "Bloc de spéléothème", 0.20, 1024, "m"),
    ("pointed_dripstone", "Spéléothème", 0.05, 1024, "m"),
    ("sandstone", "Grès", 0.30, 1024, ""), ("smooth_sandstone", "Grès lisse", 0.30, 1024, ""),
    ("cut_sandstone", "Grès taillé", 0.30, 1024, ""), ("chiseled_sandstone", "Grès sculpté", 0.30, 1024, ""),
    ("red_sandstone", "Grès rouge", 0.38, 1024, ""), ("smooth_red_sandstone", "Grès rouge lisse", 0.38, 1024, ""),
    ("cut_red_sandstone", "Grès rouge taillé", 0.38, 1024, ""),
    ("brick", "Brique", 0.30, 1024, ""), ("bricks", "Briques", 1.2, 512, ""),
    ("mud", "Boue", 0.05, 1024, ""), ("packed_mud", "Boue compacte", 0.50, 512, ""), ("mud_bricks", "Briques de boue", 0.50, 512, ""),
    ("prismarine", "Prismarine", 4.0, 256, "p"), ("prismarine_bricks", "Briques de prismarine", 9.0, 256, "p"),
    ("dark_prismarine", "Prismarine sombre", 8.0, 256, "p"), ("sea_lantern", "Lanterne aquatique", 11.0, 128, "p"),
    ("obsidian", "Obsidienne", 3.0, 128, "m"), ("crying_obsidian", "Obsidienne pleureuse", 4.0, 128, "m"),
]:
    I(1, *t)

# 2 Terre et nature ------------------------------------------------------
for t in [
    ("dirt", "Terre", 0.03, 4096, ""), ("coarse_dirt", "Terre stérile", 0.03, 2048, ""), ("rooted_dirt", "Terre racinée", 0.05, 1024, ""),
    ("podzol", "Podzol", 0.10, 1024, ""), ("mycelium", "Mycélium", 0.20, 1024, ""), ("grass_block", "Bloc d'herbe", 0.10, 1024, ""),
    ("moss_block", "Bloc de mousse", 0.15, 1024, ""), ("sand", "Sable", 0.08, 2048, ""), ("red_sand", "Sable rouge", 0.10, 2048, ""),
    ("gravel", "Gravier", 0.06, 2048, ""), ("clay_ball", "Argile", 0.30, 1024, ""), ("clay", "Bloc d'argile", 1.2, 512, ""),
    ("snowball", "Boule de neige", 0.02, 2048, ""), ("snow_block", "Bloc de neige", 0.08, 1024, ""),
    ("ice", "Glace", 0.20, 1024, ""), ("packed_ice", "Glace compacte", 1.8, 256, ""), ("blue_ice", "Glace bleue", 16.0, 64, ""),
    ("soul_sand", "Sable des âmes", 0.10, 1024, ""), ("soul_soil", "Terre des âmes", 0.10, 1024, ""),
    ("poppy", "Coquelicot", 0.20, 512, "f"), ("dandelion", "Pissenlit", 0.20, 512, "f"), ("blue_orchid", "Orchidée bleue", 0.30, 512, "f"),
    ("allium", "Allium", 0.20, 512, "f"), ("azure_bluet", "Houstonie bleue", 0.20, 512, "f"), ("red_tulip", "Tulipe rouge", 0.20, 512, "f"),
    ("orange_tulip", "Tulipe orange", 0.20, 512, "f"), ("white_tulip", "Tulipe blanche", 0.20, 512, "f"), ("pink_tulip", "Tulipe rose", 0.20, 512, "f"),
    ("oxeye_daisy", "Marguerite", 0.20, 512, "f"), ("cornflower", "Bleuet", 0.20, 512, "f"), ("lily_of_the_valley", "Muguet", 0.30, 512, "f"),
    ("sunflower", "Tournesol", 0.30, 512, "f"), ("lilac", "Lilas", 0.30, 512, "f"), ("rose_bush", "Rosier", 0.30, 512, "f"),
    ("peony", "Pivoine", 0.30, 512, "f"), ("pink_petals", "Pétales roses", 0.20, 512, "f"), ("wildflowers", "Fleurs sauvages", 0.20, 512, "f"),
    ("cactus_flower", "Fleur de cactus", 0.30, 512, "f"), ("firefly_bush", "Buisson à lucioles", 0.50, 256, "f"),
    ("vine", "Lianes", 0.10, 1024, "b"), ("fern", "Fougère", 0.05, 1024, ""), ("short_grass", "Herbe", 0.03, 2048, ""),
    ("dead_bush", "Buisson mort", 0.05, 1024, ""), ("leaf_litter", "Litière de feuilles", 0.05, 1024, "b"),
    ("brown_mushroom", "Champignon brun", 0.30, 512, "f"), ("red_mushroom", "Champignon rouge", 0.30, 512, "f"),
    ("glow_lichen", "Lichen lumineux", 0.10, 1024, ""), ("azalea", "Azalée", 0.30, 512, "b"), ("spore_blossom", "Sporanthe", 5.0, 32, "x"),
]:
    I(2, *t)

# les plantes passent dans leur propre catégorie
_k = [t[0] for t in ITEMS[2]].index("poppy")
ITEMS[16] = ITEMS[2][_k:]
ITEMS[2] = ITEMS[2][:_k]

# 3 et 4 Bois -------------------------------------------------------------
for ess, nom, p, sap, sapn in BOIS:
    I(3, f"{ess}_log", f"Bûche de {nom}", p, 1024, "b")
    I(3, f"stripped_{ess}_log", f"Bûche écorcée de {nom}", p, 1024, "b")
    I(4, f"{ess}_planks", f"Planches de {nom}", _r(p / 4), 2048, "b")
    I(4, f"{ess}_leaves", f"Feuilles de {nom}", 0.10, 1024, "b")
    I(4, sap, sapn, 0.20, 512, "b")
for ess, nom, p, fun, funn in NETHER_BOIS:
    fem = nom + ("e" if nom == "biscornu" else "")
    I(3, f"{ess}_stem", f"Tige {fem}", p, 1024, "b")
    I(3, f"stripped_{ess}_stem", f"Tige {fem} écorcée", p, 1024, "b")
    I(4, f"{ess}_planks", f"Planches {fem}s" if fem.endswith("e") else f"Planches {nom}", _r(p / 4), 2048, "b")
    I(4, fun, funn, 0.30, 512, "b")
I(3, "bamboo_block", "Bloc de bambou", 0.90, 1024, "b")
I(3, "stripped_bamboo_block", "Bloc de bambou écorcé", 0.90, 1024, "b")
I(4, "bamboo_planks", "Planches de bambou", 0.45, 2048, "b")
I(4, "stick", "Bâton", 0.12, 2048, "b")
I(4, "apple", "Pomme", 1.0, 512, "b")

# 5 Laines et teintures -----------------------------------------------------
for c, m, f, d in COULEURS:
    I(5, f"{c}_wool", f"Laine {f}", 1.0 if c == "white" else _r(1.0 + d), 1024, "e")
for c, m, f, d in COULEURS:
    I(5, f"{c}_dye", f"Teinture {f}", d, 1024, "")

# 6 Béton et terre cuite ----------------------------------------------------
for c, m, f, d in COULEURS:
    I(6, f"{c}_concrete", f"Béton {m}", _r(0.20 + d / 8), 1024, "")
I(6, "terracotta", "Terre cuite", 1.2, 512, "")
for c, m, f, d in COULEURS:
    I(6, f"{c}_terracotta", f"Terre cuite {f}", _r(1.2 + d / 8), 512, "")

# 7 Verre -----------------------------------------------------------------
I(7, "glass", "Verre", 0.18, 1024, "")
I(7, "glass_pane", "Vitre", 0.06, 2048, "")
for c, m, f, d in COULEURS:
    I(7, f"{c}_stained_glass", f"Verre teinté {m}", _r(0.18 + d / 8), 1024, "")
for c, m, f, d in COULEURS:
    I(7, f"{c}_glazed_terracotta", f"Terre cuite émaillée {f}", _r(1.2 + d / 8), 512, "")

# 8 Minerais et métaux ------------------------------------------------------
for t in [
    ("coal", "Charbon", 1.0, 1024, "m"), ("coal_block", "Bloc de charbon", 9.0, 128, "m"),
    ("raw_copper", "Cuivre brut", 1.9, 1024, "m"), ("copper_ingot", "Lingot de cuivre", 2.0, 1024, "m"),
    ("copper_block", "Bloc de cuivre", 18.0, 128, "m"), ("raw_copper_block", "Bloc de cuivre brut", 17.1, 128, "m"),
    ("cut_copper", "Cuivre taillé", 18.0, 128, ""), ("copper_nugget", "Pépite de cuivre", 0.22, 1024, "m"),
    ("raw_iron", "Fer brut", 7.9, 512, "m"), ("iron_ingot", "Lingot de fer", 8.0, 512, "m"),
    ("iron_nugget", "Pépite de fer", 0.88, 1024, "m"), ("iron_block", "Bloc de fer", 72.0, 64, "m"),
    ("raw_iron_block", "Bloc de fer brut", 71.1, 64, "m"),
    ("raw_gold", "Or brut", 11.9, 256, "m"), ("gold_ingot", "Lingot d'or", 12.0, 256, "m"),
    ("gold_nugget", "Pépite d'or", 1.33, 1024, "m"), ("gold_block", "Bloc d'or", 108.0, 32, "m"),
    ("raw_gold_block", "Bloc d'or brut", 107.1, 32, "m"),
    ("redstone", "Poudre de redstone", 1.0, 1024, "m"), ("redstone_block", "Bloc de redstone", 9.0, 128, "m"),
    ("lapis_lazuli", "Lapis-lazuli", 1.5, 1024, "m"), ("lapis_block", "Bloc de lapis-lazuli", 13.5, 128, "m"),
    ("quartz", "Quartz du Nether", 1.5, 1024, "m"), ("amethyst_shard", "Éclat d'améthyste", 1.0, 512, "m"),
    ("amethyst_block", "Bloc d'améthyste", 4.0, 256, "m"), ("flint", "Silex", 0.30, 512, "m"),
    ("iron_bars", "Barreaux de fer", 3.0, 512, ""), ("iron_chain", "Chaîne de fer", 9.0, 256, ""),
    ("lightning_rod", "Paratonnerre", 6.0, 128, ""),
]:
    I(8, *t)

# 9 Nether et End ---------------------------------------------------------
for t in [
    ("netherrack", "Netherrack", 0.02, 8192, "m"), ("nether_brick", "Brique du Nether", 0.02, 4096, ""),
    ("nether_bricks", "Briques du Nether", 0.08, 1024, ""), ("red_nether_bricks", "Briques rouges du Nether", 1.0, 512, ""),
    ("basalt", "Basalte", 0.08, 2048, "m"), ("polished_basalt", "Basalte poli", 0.08, 1024, ""), ("smooth_basalt", "Basalte lisse", 0.08, 1024, "m"),
    ("blackstone", "Roche noire", 0.10, 2048, "m"), ("polished_blackstone", "Roche noire polie", 0.10, 1024, ""),
    ("polished_blackstone_bricks", "Briques de roche noire polie", 0.10, 1024, ""), ("gilded_blackstone", "Roche noire dorée", 3.0, 128, "m"),
    ("magma_block", "Bloc de magma", 0.30, 1024, "m"), ("magma_cream", "Crème de magma", 3.0, 256, "c"),
    ("glowstone_dust", "Poudre lumineuse", 1.0, 1024, ""), ("glowstone", "Pierre lumineuse", 4.0, 256, ""),
    ("shroomlight", "Champilampe", 1.0, 512, "b"), ("nether_wart_block", "Bloc de verrues du Nether", 1.0, 512, "f"),
    ("warped_wart_block", "Bloc de verrues biscornues", 1.0, 512, "f"),
    ("quartz_block", "Bloc de quartz", 6.0, 256, ""), ("smooth_quartz", "Quartz lisse", 6.0, 256, ""),
    ("quartz_bricks", "Briques de quartz", 6.0, 256, ""), ("quartz_pillar", "Pilier de quartz", 6.0, 256, ""),
    ("bone_block", "Bloc d'os", 1.2, 512, "c"),
    ("end_stone", "Pierre de l'End", 0.30, 1024, "m"), ("end_stone_bricks", "Briques de l'End", 0.30, 1024, ""),
    ("chorus_fruit", "Fruit de chorus", 0.30, 1024, "x"), ("popped_chorus_fruit", "Chorus éclaté", 0.30, 1024, ""),
    ("purpur_block", "Bloc de purpur", 0.30, 512, ""), ("purpur_pillar", "Pilier de purpur", 0.30, 512, ""),
]:
    I(9, *t)

# 10 Agriculture -------------------------------------------------------------
for t in [
    ("wheat", "Blé", 1.0, 1024, "f"), ("hay_block", "Botte de foin", 9.0, 128, "f"), ("wheat_seeds", "Graines de blé", 0.05, 2048, "f"),
    ("carrot", "Carotte", 0.40, 2048, "f"), ("potato", "Pomme de terre", 0.40, 2048, "f"), ("poisonous_potato", "Pomme de terre empoisonnée", 0.05, 1024, "f"),
    ("beetroot", "Betterave", 0.80, 1024, "f"), ("beetroot_seeds", "Graines de betterave", 0.05, 2048, "f"),
    ("melon_slice", "Tranche de pastèque", 0.20, 2048, "f"), ("melon", "Pastèque", 1.8, 512, "f"), ("melon_seeds", "Graines de pastèque", 0.05, 2048, "f"),
    ("pumpkin", "Citrouille", 1.2, 512, "f"), ("carved_pumpkin", "Citrouille taillée", 1.2, 512, "f"),
    ("pumpkin_seeds", "Graines de citrouille", 0.05, 2048, "f"),
    ("sugar_cane", "Canne à sucre", 0.40, 1024, "f"), ("sugar", "Sucre", 0.40, 1024, "f"), ("paper", "Papier", 0.40, 1024, "f"),
    ("cocoa_beans", "Fèves de cacao", 0.50, 1024, "f"), ("nether_wart", "Verrues du Nether", 0.50, 1024, "f"),
    ("sweet_berries", "Baies sucrées", 0.30, 1024, "f"), ("glow_berries", "Baies lumineuses", 0.30, 1024, "f"),
    ("cactus", "Cactus", 0.40, 1024, "f"), ("bamboo", "Bambou", 0.10, 2048, "f"),
]:
    I(10, *t)

# 11 Élevage et chasse -------------------------------------------------------
for t in [
    ("leather", "Cuir", 2.0, 512, "e"), ("rabbit_hide", "Peau de lapin", 0.50, 512, "e"), ("rabbit_foot", "Patte de lapin", 5.0, 64, "e"),
    ("egg", "Œuf", 0.30, 1024, "e"), ("brown_egg", "Œuf brun", 0.30, 1024, "e"), ("blue_egg", "Œuf bleu", 0.30, 1024, "e"),
    ("feather", "Plume", 0.30, 1024, "e"), ("beef", "Bœuf cru", 1.5, 512, "e"), ("porkchop", "Côtelette de porc crue", 1.5, 512, "e"),
    ("chicken", "Poulet cru", 1.0, 512, "e"), ("mutton", "Mouton cru", 1.2, 512, "e"), ("rabbit", "Lapin cru", 1.5, 256, "e"),
    ("honeycomb", "Rayon de miel", 2.0, 256, "e"), ("honey_bottle", "Fiole de miel", 2.0, 256, "e"),
    ("honey_block", "Bloc de miel", 8.0, 64, "e"), ("turtle_scute", "Écaille de tortue", 10.0, 64, "e"),
    ("armadillo_scute", "Écaille de tatou", 3.0, 128, "e"),
    ("rotten_flesh", "Chair putréfiée", 0.05, 2048, "c"), ("bone", "Os", 0.40, 1024, "c"), ("bone_meal", "Poudre d'os", 0.13, 2048, "c"),
    ("string", "Ficelle", 0.50, 1024, "c"), ("gunpowder", "Poudre à canon", 2.0, 512, "c"), ("spider_eye", "Œil d'araignée", 0.80, 512, "c"),
    ("fermented_spider_eye", "Œil d'araignée fermenté", 1.5, 256, "c"),
    ("slime_ball", "Boule de slime", 3.0, 256, "c"), ("slime_block", "Bloc de slime", 27.0, 64, "c"),
    ("ender_pearl", "Perle de l'Ender", 6.0, 256, "c"), ("blaze_rod", "Bâton de blaze", 8.0, 256, "c"),
    ("blaze_powder", "Poudre de blaze", 4.0, 512, "c"), ("ender_eye", "Œil de l'Ender", 10.0, 128, "c"),
    ("breeze_rod", "Bâton de breeze", 10.0, 128, "c"), ("phantom_membrane", "Membrane de Phantom", 4.0, 128, "c"),
]:
    I(11, *t)

# 12 Pêche -----------------------------------------------------------------
for t in [
    ("cod", "Morue crue", 1.0, 512, "p"), ("salmon", "Saumon cru", 1.5, 512, "p"), ("tropical_fish", "Poisson tropical", 3.0, 256, "p"),
    ("pufferfish", "Poisson-globe", 3.0, 256, "p"), ("ink_sac", "Poche d'encre", 0.50, 512, "p"), ("glow_ink_sac", "Poche d'encre lumineuse", 2.0, 256, "p"),
    ("prismarine_shard", "Éclat de prismarine", 1.0, 512, "p"), ("prismarine_crystals", "Cristaux de prismarine", 1.5, 512, "p"),
    ("lily_pad", "Nénuphar", 0.50, 512, "p"), ("kelp", "Algue", 0.10, 2048, "p"), ("dried_kelp", "Algue séchée", 0.10, 2048, "p"),
    ("dried_kelp_block", "Bloc d'algues séchées", 0.90, 512, "p"), ("sea_pickle", "Cornichon de mer", 0.30, 512, "p"),
]:
    I(12, *t)

# 13 Cuisine ---------------------------------------------------------------
for t in [
    ("bread", "Pain", 3.0, 512, "f"), ("baked_potato", "Pomme de terre cuite", 0.50, 1024, "f"),
    ("pumpkin_pie", "Tarte à la citrouille", 1.9, 256, "f"), ("cookie", "Cookie", 0.30, 1024, "f"),
    ("golden_carrot", "Carotte dorée", 11.0, 128, "f"), ("mushroom_stew", "Ragoût de champignons", 0.60, 128, "f"),
    ("cooked_beef", "Steak", 1.6, 512, "e"), ("cooked_porkchop", "Côtelette de porc cuite", 1.6, 512, "e"),
    ("cooked_chicken", "Poulet rôti", 1.1, 512, "e"), ("cooked_mutton", "Mouton cuit", 1.3, 512, "e"),
    ("cooked_rabbit", "Lapin cuit", 1.6, 256, "e"), ("cooked_cod", "Morue cuite", 1.1, 512, "p"),
    ("cooked_salmon", "Saumon cuit", 1.6, 512, "p"), ("golden_apple", "Pomme dorée", 90.0, 32, ""),
]:
    I(13, *t)

# 14 Utilitaires --------------------------------------------------------------
for t in [
    ("torch", "Torche", 0.28, 1024, ""), ("soul_torch", "Torche des âmes", 0.28, 1024, ""), ("lantern", "Lanterne", 3.0, 256, ""),
    ("soul_lantern", "Lanterne des âmes", 3.0, 256, ""), ("campfire", "Feu de camp", 2.0, 128, ""),
    ("crafting_table", "Établi", 1.8, 128, ""), ("furnace", "Four", 0.40, 128, ""), ("chest", "Coffre", 3.6, 256, ""),
    ("barrel", "Tonneau", 3.6, 256, ""), ("ladder", "Échelle", 0.20, 512, ""), ("scaffolding", "Échafaudage", 0.18, 512, ""),
    ("book", "Livre", 3.0, 256, "n"), ("bookshelf", "Bibliothèque", 12.0, 128, "n"), ("item_frame", "Cadre", 2.5, 128, ""),
    ("flower_pot", "Pot de fleurs", 0.90, 256, ""), ("rail", "Rail", 3.0, 256, ""), ("powered_rail", "Rail de propulsion", 12.0, 128, ""),
    ("minecart", "Wagonnet", 40.0, 64, ""), ("piston", "Piston", 10.0, 128, ""), ("sticky_piston", "Piston collant", 13.0, 128, ""),
    ("observer", "Observateur", 3.8, 128, ""), ("hopper", "Entonnoir", 44.0, 64, ""), ("dropper", "Dropper", 1.2, 128, ""),
    ("dispenser", "Distributeur", 2.0, 128, ""), ("repeater", "Répéteur", 2.5, 256, ""), ("comparator", "Comparateur", 4.0, 256, ""),
    ("lever", "Levier", 0.10, 512, ""), ("redstone_torch", "Torche de redstone", 1.0, 512, ""), ("redstone_lamp", "Lampe de redstone", 7.0, 128, ""),
    ("bucket", "Seau", 24.0, 64, ""), ("shears", "Cisailles", 16.0, 64, ""), ("fishing_rod", "Canne à pêche", 1.2, 64, "p"),
    ("bow", "Arc", 1.8, 64, "c"), ("arrow", "Flèche", 0.18, 1024, "c"), ("shield", "Bouclier", 10.0, 64, ""),
    ("lead", "Laisse", 1.3, 64, "e"), ("name_tag", "Étiquette", 0.60, 32, "t"), ("saddle", "Selle", 14.0, 32, "e"),
    ("cauldron", "Chaudron", 56.0, 32, ""), ("anvil", "Enclume", 240.0, 8, ""),
]:
    I(14, *t)

# 15 Trésors (vente seulement) ------------------------------------------------
for t in [
    ("diamond", "Diamant", 120.0, 32, "m"), ("diamond_block", "Bloc de diamant", 1080.0, 4, "m"),
    ("emerald", "Émeraude", 15.0, 128, "t"), ("emerald_block", "Bloc d'émeraude", 135.0, 16, "t"),
    ("ancient_debris", "Débris antiques", 600.0, 8, "m"), ("netherite_scrap", "Fragment de netherite", 620.0, 8, "m"),
    ("netherite_ingot", "Lingot de netherite", 2600.0, 4, "m"), ("echo_shard", "Éclat d'écho", 50.0, 32, "x"),
    ("nautilus_shell", "Coquille de nautile", 40.0, 32, "p"), ("heart_of_the_sea", "Cœur de la mer", 800.0, 4, "p"),
    ("sponge", "Éponge", 30.0, 32, "p"), ("wet_sponge", "Éponge mouillée", 30.0, 32, "p"),
    ("ghast_tear", "Larme de ghast", 20.0, 64, "c"), ("shulker_shell", "Carapace de shulker", 100.0, 16, "c"),
    ("totem_of_undying", "Totem d'immortalité", 300.0, 8, "c"), ("wither_skeleton_skull", "Crâne de wither squelette", 150.0, 8, "c"),
    ("skeleton_skull", "Crâne de squelette", 30.0, 16, "c"), ("zombie_head", "Tête de zombie", 30.0, 16, "c"),
    ("creeper_head", "Tête de creeper", 50.0, 16, "c"), ("piglin_head", "Tête de piglin", 50.0, 16, "c"),
    ("nether_star", "Étoile du Nether", 1500.0, 4, "c"), ("dragon_breath", "Souffle de dragon", 20.0, 32, "c"),
    ("dragon_head", "Tête de dragon", 2000.0, 2, "c"), ("heavy_core", "Noyau lourd", 500.0, 4, "x"),
    ("goat_horn", "Corne de chèvre", 30.0, 16, "e"), ("sniffer_egg", "Œuf de renifleur", 100.0, 8, "e"),
    ("trident", "Trident", 400.0, 4, "c"), ("elytra", "Élytres", 2000.0, 2, "x"),
    ("enchanted_golden_apple", "Pomme de Notch", 1000.0, 4, ""),
]:
    I(15, *t)

# Cuisson au four (absente des recettes d'établi) : (résultat, ingrédient). Le combustible vaut 1/8 de charbon.
CUISSON = [("stone", "cobblestone"), ("smooth_stone", "stone"), ("cracked_stone_bricks", "stone_bricks"), ("glass", "sand"),
           ("brick", "clay_ball"), ("terracotta", "clay"), ("nether_brick", "netherrack"), ("smooth_sandstone", "sandstone"),
           ("smooth_red_sandstone", "red_sandstone"), ("smooth_quartz", "quartz_block"), ("smooth_basalt", "basalt"),
           ("deepslate", "cobbled_deepslate"), ("popped_chorus_fruit", "chorus_fruit"), ("iron_ingot", "raw_iron"),
           ("gold_ingot", "raw_gold"), ("copper_ingot", "raw_copper"), ("baked_potato", "potato"), ("cooked_beef", "beef"),
           ("cooked_porkchop", "porkchop"), ("cooked_chicken", "chicken"), ("cooked_mutton", "mutton"), ("cooked_rabbit", "rabbit"),
           ("cooked_cod", "cod"), ("cooked_salmon", "salmon"), ("dried_kelp", "kelp"), ("green_dye", "cactus"), ("lime_dye", "sea_pickle"),
           ("sponge", "wet_sponge")] + [(f"{c}_glazed_terracotta", f"{c}_terracotta") for c, *_ in COULEURS]

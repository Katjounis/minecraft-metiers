# -*- coding: utf-8 -*-
"""Tous les chiffres d'Industrie (27/11/2026), tirés de la simulation (modele d'équilibre) et calés sur les prix de
vente du Commerce. Le générateur ne contient aucun chiffre en dur : on règle tout ici."""

# ------------------------------------------------------------------ produits
# clé : (nom, objet vanilla pour le retrait ou None, prix de base en centièmes d'Écu, saturation S par jour)
# 27/11/2026 (17 h 24) : prix doublés par rapport au Commerce (la Bourse paie le gros volume) et saturation
# relevée, à la demande de Samuel : une machine se rembourse en 1 à 12 jours au lieu de 2 à 35.
PROD = {
    "pierre": ("Pierre", "stone", 20, 60000), "charbon": ("Charbon", "coal", 200, 12000), "cuivre": ("Cuivre", "copper_ingot", 400, 8000),
    "canne": ("Canne à sucre", "sugar_cane", 80, 30000), "verrue": ("Verrues du Nether", "nether_wart", 100, 20000),
    "citrouille": ("Citrouille", "pumpkin", 240, 10000),
    "ble": ("Blé", "wheat", 200, 10000), "carotte": ("Carotte", "carrot", 80, 20000), "patate": ("Pomme de terre", "potato", 80, 20000),
    "betterave": ("Betterave", "beetroot", 160, 10000), "pasteque": ("Pastèque", "melon_slice", 40, 20000),
    "fer": ("Fer", "iron_ingot", 1600, 4000), "or": ("Or", "gold_ingot", 2400, 3000), "emeraude": ("Émeraude", "emerald", 3000, 4000),
    "diamant": ("Diamant", "diamond", 24000, 1500), "netherite": ("Netherite", "netherite_ingot", 520000, 250),
    "acier": ("Acier", None, 6000, 2500), "elixir": ("Élixir", None, 8000, 1200), "mecanisme": ("Mécanisme", None, 44000, 1500),
    "bijou": ("Bijou", None, 90000, 1600), "relique": ("Relique", None, 3600000, 80),
    # butin de l'usine à spawner
    "chair": ("Chair putréfiée", "rotten_flesh", 10, 13333), "os": ("Os", "bone", 80, 6667), "ficelle": ("Ficelle", "string", 100, 6667),
    "oeil": ("Œil d'araignée", "spider_eye", 160, 3333), "viande": ("Viande", "beef", 300, 3333), "plume": ("Plume", "feather", 60, 6667),
    "laine": ("Laine", "white_wool", 200, 6667), "cuir": ("Cuir", "leather", 400, 3333), "slime": ("Boule de slime", "slime_ball", 600, 1667),
    "creme": ("Crème de magma", "magma_cream", 600, 1667), "poudre": ("Poudre à canon", "gunpowder", 400, 3333),
    "membrane": ("Membrane de phantom", "phantom_membrane", 800, 833), "prisma": ("Éclat de prismarine", "prismarine_shard", 200, 3333),
    "perle": ("Perle de l'Ender", "ender_pearl", 1200, 1667), "blaze": ("Bâton de blaze", "blaze_rod", 1600, 1667),
    "larme": ("Larme de ghast", "ghast_tear", 4000, 417), "breeze": ("Bâton de breeze", "breeze_rod", 2000, 833),
    "crane": ("Crâne de wither squelette", "wither_skeleton_skull", 30000, 53), "carapace": ("Carapace de shulker", "shulker_shell", 20000, 107),
    "totem": ("Totem d'immortalité", "totem_of_undying", 60000, 53),
}
PL = list(PROD)
PI = {p: i for i, p in enumerate(PL)}

# ------------------------------------------------------------------ machines
# rang, prix, éclats, kW (négatif = fournit), métier du bonus, sorties par heure, entrées par unité produite (ateliers)
MACH = {
    "carriere":   dict(nom="Carrière automatique", rang=1, prix=30_000, ecl=0, kw=20, met="m", out={"pierre": 4000, "charbon": 800, "cuivre": 300}),
    "serre":      dict(nom="Serre hydroponique", rang=1, prix=45_000, ecl=0, kw=25, met="f", out={"canne": 3000, "verrue": 1000, "citrouille": 500}),
    "cultures":   dict(nom="Serre de cultures", rang=1, prix=35_000, ecl=0, kw=25, met="f", out={"ble": 1500, "carotte": 2000, "patate": 2000, "betterave": 800, "pasteque": 3000}),
    "fourneau":   dict(nom="Haut-fourneau des Titans", rang=1, prix=120_000, ecl=0, kw=40, met="m", out={"fer": 400}),
    "chaudiere":  dict(nom="Chaudière à charbon", rang=1, prix=20_000, ecl=0, kw=-150, met="b", charbon=300),
    "puits_or":   dict(nom="Puits de cristal : or", rang=2, prix=500_000, ecl=5, kw=80, met="m", out={"or": 1500}),
    "fonderie":   dict(nom="Fonderie", rang=2, prix=400_000, ecl=0, kw=70, met="m", out={"acier": 600}, inp={"fer": 1, "charbon": 2}),
    "distill":    dict(nom="Distillerie alchimique", rang=2, prix=500_000, ecl=3, kw=50, met="n", out={"elixir": 400}, inp={"verrue": 2, "canne": 2, "citrouille": 1}),
    "spawner":    dict(nom="Usine à spawner", rang=2, prix=300_000, ecl=5, kw=60, met="c", out={}),
    "lave":       dict(nom="Centrale à lave", rang=2, prix=350_000, ecl=0, kw=-600, met="b"),
    "puits_dia":  dict(nom="Puits de cristal : diamant", rang=3, prix=3_000_000, ecl=15, kw=200, met="m", out={"diamant": 300}),
    "puits_eme":  dict(nom="Puits de cristal : émeraude", rang=3, prix=2_500_000, ecl=10, kw=150, met="m", out={"emeraude": 2000}),
    "atelier":    dict(nom="Atelier mécanique", rang=3, prix=3_000_000, ecl=10, kw=180, met="m", out={"mecanisme": 200}, inp={"acier": 2, "cuivre": 4}),
    "puits_net":  dict(nom="Puits de cristal : netherite", rang=4, prix=18_000_000, ecl=40, kw=500, met="m", out={"netherite": 30}),
    "joaillerie": dict(nom="Joaillerie", rang=4, prix=12_000_000, ecl=25, kw=350, met="t", out={"bijou": 200}, inp={"or": 1, "diamant": 1, "emeraude": 1}),
    "coeur":      dict(nom="Cœur stellaire", rang=4, prix=12_000_000, ecl=20, kw=-3000, met="b", etoile=1),
    "forge":      dict(nom="Forge des reliques", rang=5, prix=40_000_000, ecl=60, kw=900, met="m", out={"relique": 12}, inp={"netherite": 1, "bijou": 2, "mecanisme": 2}),
}
ML = list(MACH)
MI = {m: i for i, m in enumerate(ML)}
ATELIERS = ["fonderie", "distill", "atelier", "joaillerie", "forge"]       # ordre de transformation
LV_PROD = [100, 150, 220, 320, 450]          # production (et puissance des bâtiments d'énergie), en %
LV_KW = [10, 13, 17, 22, 28]                 # consommation, en dixièmes
LV_COUT = [1, 2, 5, 12, 30]                  # prix du passage au niveau k, en multiple du prix d'achat
LV_ECL = [0, 0, 0, 1, 2]                     # éclats du passage au niveau 4 et 5, en multiple (au moins 3 et 6)

def max_copies(m, rang):
    d = MACH[m]
    return 4 + rang if d["kw"] < 0 else max(0, min(5, 2 + rang - d["rang"]))

# usine à spawner : créatures des spawners du Commerce (même ordre que SPM de commerce/sources/spawners.py, 1 à 35)
# butin moyen par créature tuée ; 240 créatures par heure au niveau 1, +25 % par niveau de vitesse et de quantité du spawner
MOBS = [("chicken", {"plume": 100, "viande": 100}), ("pig", {"viande": 200}), ("rabbit", {"viande": 50, "cuir": 50}),
        ("sheep", {"laine": 100, "viande": 150}), ("cow", {"cuir": 100, "viande": 200}), ("goat", {"viande": 150}),
        ("mooshroom", {"cuir": 100, "viande": 200}), ("silverfish", {"chair": 50}), ("zombie", {"chair": 150, "fer": 1}),
        ("spider", {"ficelle": 100, "oeil": 33}), ("husk", {"chair": 150}), ("drowned", {"chair": 100, "cuivre": 10}),
        ("skeleton", {"os": 150}), ("cave_spider", {"ficelle": 100, "oeil": 33}), ("stray", {"os": 150}), ("bogged", {"os": 150}),
        ("slime", {"slime": 100}), ("zombified_piglin", {"chair": 100, "or": 10}), ("magma_cube", {"creme": 50}),
        ("creeper", {"poudre": 150}), ("piglin", {"or": 10}), ("phantom", {"membrane": 50}), ("witch", {"poudre": 50}),
        ("hoglin", {"viande": 300, "cuir": 50}), ("pillager", {"os": 50}), ("guardian", {"prisma": 150}), ("enderman", {"perle": 50}),
        ("blaze", {"blaze": 50}), ("vindicator", {"emeraude": 50}), ("ghast", {"larme": 50, "poudre": 100}), ("breeze", {"breeze": 150}),
        ("wither_skeleton", {"os": 100, "charbon": 33, "crane": 3}), ("ravager", {"cuir": 200}), ("shulker", {"carapace": 50}),
        ("evoker", {"totem": 100, "emeraude": 50})]          # quantités en centièmes par créature
SP_PAR_H = 240

# ------------------------------------------------------------------ îles, parcelles, rangs
ANNEAUX = [(0, 0), (1, 50_000), (2, 750_000), (3, 6_000_000)]       # prix d'une parcelle par anneau (anneau 3 : + 5 éclats)
PARC_MAX = {1: 5, 2: 9, 3: 17, 4: 30, 5: 49}
RANGS = {1: ("Atelier", 0, 0, 0, 0, None), 2: ("Manufacture", 3_000, 3, 200_000, 0, None),
         3: ("Industrie", 25_000, 15, 2_000_000, 10, "boss"), 4: ("Consortium", 150_000, 45, 12_000_000, 40, "wither"),
         5: ("Empire", 350_000, 90, 40_000_000, 100, "dragon")}
RI_ECUS = 250                             # 1 point de RI par tranche de 250 Écus vendus
CONTRAT_PAIE = 300                       # contrat payé 3 x le prix de base du Commerce (en %, sur le prix de base / 2)
CONTRATS_JOUR = {1: 1, 2: 2, 3: 3, 4: 3, 5: 3}
# Halle : nom, rang, prix, éclats, objets vendus par heure, commission %, bonus de saturation %
HALLE = [("Échoppe", 1, 0, 0, 10_000, 12, 100), ("Comptoir", 2, 150_000, 0, 25_000, 8, 100),
         ("Halle", 3, 2_500_000, 10, 60_000, 5, 110), ("Bourse impériale", 4, 20_000_000, 40, 200_000, 2, 125)]
# tubes : nom, rang, débit par minute et par machine, prix par machine posée, éclats
TUBES = [("cuivre", 1, 500, 0, 0), ("or", 2, 2500, 25_000, 0), ("cristal", 4, 10_000, 250_000, 1)]
BANQUE_PRIX = 250_000
OFFLINE_MIN = 480                         # minutes de production hors ligne (8 h), +120 aux niveaux 5 et 10 de Logistique
NEXUS_KW = 60
NEXUS_CAP = 1_000_000                     # x2 par niveau de Logistique, plafonné à 100 M
# entretien de l'empire : (seuil de recettes nettes du jour en Écus, part gardée %)
ENTRETIEN = [(12_000_000, 55), (5_000_000, 75)]
# prêts : plafond par rang, frais %, part prélevée sur les ventes %, durée en jours
PRET_MAX = {1: 0, 2: 500_000, 3: 5_000_000, 4: 30_000_000, 5: 100_000_000}
PRET_FRAIS, PRET_PART, PRET_JOURS = 10, 25, 14
RETRAIT_JOUR = 64
GARDE_PM = 2                              # frais de garde : 0,2 % par jour (en pour mille)
# recherche : branche, nom, effet, prix de base, ressource, quantité de base (x2 par niveau)
BRANCHES = [("commerce", "Réseau commercial", "saturation +25 % par niveau", 300_000, "or", 1000),
            ("cadence", "Cadence", "production +4 % par niveau", 200_000, "fer", 5000),
            ("logistique", "Logistique", "stock du Nexus x2, +2 h hors ligne aux niveaux 5 et 10", 150_000, "cuivre", 2000),
            ("reseau", "Réseau électrique", "consommation -3 % par niveau", 150_000, "charbon", 10000)]
# Grands Œuvres : Écus = 8 M x 1,8^(n-1), éclats = 10 n, ressources du niveau n
OEUVRES = [("Colosse de fer", {"fer": 500_000, "or": 100_000}), ("Jardins suspendus", {"ble": 500_000, "elixir": 50_000}),
           ("Phare de cristal", {"diamant": 50_000, "emeraude": 200_000}), ("Arche d'acier", {"acier": 300_000, "mecanisme": 30_000}),
           ("Ménagerie", {"viande": 200_000, "perle": 20_000}), ("Trésor des Rois", {"bijou": 30_000, "or": 500_000}),
           ("Forge du Monde", {"netherite": 5_000, "mecanisme": 100_000}), ("Couronne de l'Archipel", {"relique": 200, "bijou": 100_000})]
# noms français des créatures des spawners (même ordre que MOBS et que le Commerce)
MOB_NOM = ["Poulet", "Cochon", "Lapin", "Mouton", "Vache", "Chèvre", "Champimeuh", "Poisson d'argent", "Zombie", "Araignée",
           "Zombie momifié", "Noyé", "Squelette", "Araignée venimeuse", "Vagabond", "Embourbé", "Slime", "Piglin zombifié",
           "Cube de magma", "Creeper", "Piglin", "Phantom", "Sorcière", "Hoglin", "Pillard", "Gardien", "Enderman", "Blaze",
           "Vindicateur", "Ghast", "Breeze", "Wither squelette", "Ravageur", "Shulker", "Évocateur"]
# objet qui glisse dans le tube de chaque machine
PAQUET = {"carriere": "cobblestone", "serre": "sugar_cane", "cultures": "wheat", "fourneau": "iron_ingot", "chaudiere": "coal",
          "puits_or": "gold_ingot", "fonderie": "iron_block", "distill": "potion", "spawner": "bone", "lave": "magma_block",
          "puits_dia": "diamond", "puits_eme": "emerald", "atelier": "clock", "puits_net": "netherite_ingot", "joaillerie": "amethyst_shard",
          "coeur": "nether_star", "forge": "totem_of_undying"}

# 28/11/2026 : familles de production, une couleur chacune (verre des tubes, étiquettes, barres du tableau)
FAMILLES = {"min": ("Minerais", "#c8c8d0", "minecraft:light_gray_stained_glass"),
            "agr": ("Agriculture", "#7ad050", "minecraft:lime_stained_glass"),
            "met": ("Métallurgie", "#ff9a40", "minecraft:orange_stained_glass"),
            "ene": ("Énergie", "#ff5a3a", "minecraft:red_stained_glass"),
            "cri": ("Cristaux", "#5ff0e6", "minecraft:light_blue_stained_glass"),
            "ate": ("Ateliers", "#b878ff", "minecraft:purple_stained_glass"),
            "cre": ("Créatures", "#ff70d0", "minecraft:magenta_stained_glass")}
FAM = {"carriere": "min", "serre": "agr", "cultures": "agr", "fourneau": "met", "fonderie": "met", "chaudiere": "ene", "lave": "ene",
       "coeur": "ene", "puits_or": "cri", "puits_dia": "cri", "puits_eme": "cri", "puits_net": "cri", "distill": "ate", "atelier": "ate",
       "joaillerie": "ate", "forge": "ate", "spawner": "cre"}

# noms courts pour les boutons (un bouton fait 200 px : au-delà le texte défile)
COURT = {"carriere": "Carrière", "serre": "Serre hydro", "cultures": "Serre cultures", "fourneau": "Haut-fourneau", "chaudiere": "Chaudière",
         "puits_or": "Puits d'or", "fonderie": "Fonderie", "distill": "Distillerie", "spawner": "Usine spawner", "lave": "Centrale lave",
         "puits_dia": "Puits diamant", "puits_eme": "Puits émeraude", "atelier": "Atelier méca", "puits_net": "Puits netherite",
         "joaillerie": "Joaillerie", "coeur": "Cœur stellaire", "forge": "Forge reliques"}

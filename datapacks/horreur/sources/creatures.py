"""Table des creatures du pack Horreur : stats, apparition, textes du bestiaire.

Chaque creature est un mob vanilla INVISIBLE (il porte l'IA et la vie) habille par le resource pack :
  apparence "habit"  : 3 pieces d'equipement (couche d'armure humanoide texturee) -> membres animes
  apparence "statue" : un item_display passager qui affiche un modele 3D (silhouette geante ou figee)

xp : XP du metier Chasseur (pack Metiers) gagnee par kill, au total. Ignore si Metiers est absent.
chance : pour mille, a chaque tentative (toutes les 30 s par joueur dans le bon lieu). bonus = (lieu, pour mille en plus).
butin : (objet, min, max, poids) tous tires ; rare : une chance sur 4 de tirer un de ces objets (poids). Modifiable en jeu :
  /scoreboard players set #ch_<id> hr.cfg <valeur>
"""

PALIERS = (1, 10, 50)

CREATURES = [
    dict(id="slender", nom="SlenderMan", couleur="#c8c8c8", apparence="statue",
         base="zombie", echelle=1.5, statue_echelle=1.1,
         vie=60, degats=8, vitesse=0.0, vitesse_chasse=0.34, armure=4, recul=0.8,
         xp=40, chance=12, bonus=("foret", 30), lieu="surface", nuit=True, distance=(26, 42),
         butin=[("ender_pearl", 2, 4, 1), ("ender_eye", 1, 2, 1), ("paper", 1, 3, 1)],
         rare=[("diamond", 1, 2, 3), ("music_disc_11", 1, 1, 1), ("echo_shard", 1, 2, 1)],
         ou="La surface la nuit, surtout les forêts et les taïgas.",
         desc="Une silhouette immense en costume, sans visage. Une variante de l'enderman que personne n'a jamais vu marcher.",
         comportement="Il se rapproche quand tu ne le regardes pas. Le fixer trouble la vue… et peut le réveiller.",
         titre="Celui qui ne détourne pas les yeux"),
    dict(id="herobrine", nom="Herobrine", couleur="#ffffff", apparence="habit",
         base="zombie", echelle=1.0,
         vie=40, degats=7, vitesse=0.0, vitesse_chasse=0.36, armure=6, recul=0.5,
         xp=30, chance=20, lieu="surface", nuit=True, distance=(22, 36),
         butin=[("gold_ingot", 3, 6, 1), ("redstone", 4, 10, 1), ("redstone_torch", 1, 1, 1)],
         rare=[("diamond", 1, 3, 3), ("totem_of_undying", 1, 1, 1), ("golden_apple", 1, 2, 2)],
         ou="N'importe où en surface, la nuit. Toujours au loin.",
         desc="Le joueur aux yeux blancs. On le croyait retiré du jeu.",
         comportement="Il observe de loin et s'évanouit quand on approche. Parfois, il ne s'enfuit pas.",
         titre="Chasseur de légendes"),
    dict(id="siren", nom="Siren Head", couleur="#a08a6a", apparence="statue",
         base="zombie", echelle=4.0, statue_echelle=2.6,
         vie=180, degats=12, vitesse=0.17, vitesse_chasse=0.17, armure=8, recul=1.0,
         xp=80, chance=6, bonus=("plaine", 20), lieu="surface", nuit=True, distance=(40, 56),
         butin=[("copper_ingot", 8, 16, 1), ("emerald", 3, 6, 1), ("bone", 4, 8, 1), ("note_block", 1, 1, 1)],
         rare=[("goat_horn", 1, 1, 2), ("iron_block", 1, 3, 2), ("diamond", 2, 4, 2), ("heart_of_the_sea", 1, 1, 1)],
         ou="La surface la nuit, surtout les plaines, prairies et savanes. Rare.",
         desc="Un géant décharné de huit mètres, à la tête faite de deux sirènes.",
         comportement="On l'entend venir de très loin. Lent, mais chaque coup est terrible.",
         titre="Tueur de géants"),
    dict(id="nonne", nom="La Nonne", couleur="#d0c8a0", apparence="habit",
         base="husk", echelle=1.0,
         vie=30, degats=5, vitesse=0.36, vitesse_chasse=0.36, armure=2, recul=0.3,
         xp=25, chance=25, lieu="grotte", nuit=False, distance=(3, 3),
         butin=[("candle", 1, 3, 1), ("experience_bottle", 4, 8, 1), ("book", 1, 2, 1)],
         rare=[("enchanted_book", 1, 1, 3), ("golden_apple", 1, 1, 1)],
         ou="Sous terre, sous la couche 62.",
         desc="Une religieuse au visage blafard et aux yeux jaunes.",
         comportement="Elle apparaît dans ton dos. Ses coups aveuglent et affaiblissent.",
         titre="Exorciste"),
    dict(id="clown", nom="Le Clown", couleur="#e03030", apparence="habit",
         base="zombie", echelle=1.0, ballon=True,
         vie=40, degats=5, vitesse=0.3, vitesse_chasse=0.3, armure=2, recul=0.3,
         xp=25, chance=25, lieu="sous_terre", nuit=False, distance=(10, 18),
         butin=[("red_dye", 1, 3, 1), ("firework_rocket", 4, 8, 1), ("emerald", 2, 4, 1)],
         rare=[("cake", 1, 1, 2), ("diamond", 1, 2, 2), ("music_disc_13", 1, 1, 1)],
         ou="Sous terre, dans les cavernes et les ravins.",
         desc="Un clown au costume gris, toujours accompagné de son ballon rouge.",
         comportement="On entend son rire avant de le voir. Ses coups ralentissent.",
         titre="Ça ne fait plus rire personne"),
    dict(id="pinhead", nom="Pinhead", couleur="#9a9aa8", apparence="habit",
         base="zombie", echelle=1.05,
         vie=120, degats=9, vitesse=0.25, vitesse_chasse=0.25, armure=10, recul=0.8,
         xp=60, chance=10, lieu="enfer", nuit=False, distance=(8, 14),
         butin=[("iron_chain", 2, 5, 1), ("iron_ingot", 4, 8, 1), ("blaze_rod", 2, 4, 1)],
         rare=[("netherite_scrap", 1, 2, 2), ("echo_shard", 1, 2, 2), ("enchanted_golden_apple", 1, 1, 1)],
         ou="Le Nether, ou la surface la nuit. Rare.",
         desc="Le prêtre des cénobites, le crâne quadrillé de clous.",
         comportement="Ses chaînes t'attirent vers lui. Blessé, il appelle ses cénobites.",
         titre="Celui qui a résolu la boîte"),
]

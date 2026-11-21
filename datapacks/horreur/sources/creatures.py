"""Table des creatures du pack Horreur : stats, apparition, textes du bestiaire.

Chaque creature est un mob vanilla INVISIBLE (il porte l'IA et la vie) habille par le resource pack :
  apparence "habit"  : 3 pieces d'equipement (couche d'armure humanoide texturee) -> membres animes
  apparence "statue" : un item_display passager qui affiche un modele 3D (silhouette geante ou figee)

xp : XP du metier Chasseur (pack Metiers) gagnee par kill, au total. Ignore si Metiers est absent.
chance : pour mille, a chaque tentative (toutes les 30 s par joueur dans le bon lieu). Modifiable en jeu :
  /scoreboard players set #ch_<id> hr.cfg <valeur>
"""

PALIERS = (1, 10, 50)

CREATURES = [
    dict(id="slender", nom="SlenderMan", couleur="#c8c8c8", apparence="statue",
         base="zombie", echelle=1.5, statue_echelle=1.1,
         vie=60, degats=8, vitesse=0.0, vitesse_chasse=0.34, armure=4, recul=0.8,
         xp=40, chance=8, lieu="foret", nuit=True, distance=(26, 42),
         butin=[("minecraft:ender_pearl", 1, 2), ("minecraft:paper", 1, 3)],
         ou="Les forêts et les taïgas, la nuit.",
         desc="Une silhouette immense en costume, sans visage. Une variante de l'enderman que personne n'a jamais vu marcher.",
         comportement="Il se rapproche quand tu ne le regardes pas. Le fixer trouble la vue… et peut le réveiller.",
         titre="Celui qui ne détourne pas les yeux"),
    dict(id="herobrine", nom="Herobrine", couleur="#ffffff", apparence="habit",
         base="zombie", echelle=1.0,
         vie=40, degats=7, vitesse=0.0, vitesse_chasse=0.36, armure=6, recul=0.5,
         xp=30, chance=10, lieu="surface", nuit=True, distance=(22, 36),
         butin=[("minecraft:redstone_torch", 1, 1), ("minecraft:gold_ingot", 1, 3)],
         ou="N'importe où en surface, la nuit. Toujours au loin.",
         desc="Le joueur aux yeux blancs. On le croyait retiré du jeu.",
         comportement="Il observe de loin et s'évanouit quand on approche. Parfois, il ne s'enfuit pas.",
         titre="Chasseur de légendes"),
    dict(id="siren", nom="Siren Head", couleur="#a08a6a", apparence="statue",
         base="zombie", echelle=4.0, statue_echelle=2.6,
         vie=180, degats=12, vitesse=0.17, vitesse_chasse=0.17, armure=8, recul=1.0,
         xp=80, chance=4, lieu="plaine", nuit=True, distance=(40, 56),
         butin=[("minecraft:copper_ingot", 4, 9), ("minecraft:note_block", 1, 1), ("minecraft:bone", 2, 5)],
         ou="Les plaines, prairies et savanes, la nuit. Très rare.",
         desc="Un géant décharné de huit mètres, à la tête faite de deux sirènes.",
         comportement="On l'entend venir de très loin. Lent, mais chaque coup est terrible.",
         titre="Tueur de géants"),
    dict(id="nonne", nom="La Nonne", couleur="#d0c8a0", apparence="habit",
         base="husk", echelle=1.0,
         vie=30, degats=5, vitesse=0.36, vitesse_chasse=0.36, armure=2, recul=0.3,
         xp=25, chance=10, lieu="grotte", nuit=False, distance=(3, 3),
         butin=[("minecraft:candle", 1, 3), ("minecraft:book", 1, 1)],
         ou="Les grottes profondes (sous la couche 40), dans le noir.",
         desc="Une religieuse au visage blafard et aux yeux jaunes.",
         comportement="Elle apparaît dans ton dos. Ses coups aveuglent et affaiblissent.",
         titre="Exorciste"),
    dict(id="clown", nom="Le Clown", couleur="#e03030", apparence="habit",
         base="zombie", echelle=1.0, ballon=True,
         vie=40, degats=5, vitesse=0.3, vitesse_chasse=0.3, armure=2, recul=0.3,
         xp=25, chance=8, lieu="sous_terre", nuit=False, distance=(10, 18),
         butin=[("minecraft:red_dye", 1, 3), ("minecraft:cake", 1, 1)],
         ou="Sous terre, dans les cavernes et les ravins sombres.",
         desc="Un clown au costume gris, toujours accompagné de son ballon rouge.",
         comportement="On entend son rire avant de le voir. Ses coups ralentissent.",
         titre="Ça ne fait plus rire personne"),
    dict(id="pinhead", nom="Pinhead", couleur="#9a9aa8", apparence="habit",
         base="zombie", echelle=1.05,
         vie=120, degats=9, vitesse=0.25, vitesse_chasse=0.25, armure=10, recul=0.8,
         xp=60, chance=3, lieu="enfer", nuit=False, distance=(8, 14),
         butin=[("minecraft:iron_chain", 2, 5), ("minecraft:iron_nugget", 4, 10), ("minecraft:echo_shard", 0, 1)],
         ou="Le Nether, ou en surface à minuit pile. Très rare.",
         desc="Le prêtre des cénobites, le crâne quadrillé de clous.",
         comportement="Ses chaînes t'attirent vers lui. Blessé, il appelle ses cénobites.",
         titre="Celui qui a résolu la boîte"),
]

# Métiers : datapack et resource pack

Datapack vanilla de métiers (Bûcheron, Fermier, Mineur, Chasseur, Pêcheur, Éleveur, Enchanteur, Explorateur, Marchand, Bâtisseur) pour notre serveur, avec niveaux jusqu'à 100, arbres de compétences, outils et armure sur 11 paliers, Forge (cristaux et éclats), skins et cadres de titre, défis du jour, de la semaine et collectifs, classement, prestige, heure du métier et 5 boss de serveur en rotation.

![Aperçu des outils](apercu/outils.png)

## Contenu

| Fichier | Rôle |
|---|---|
| `metiers.zip` | Datapack, à mettre dans `world/datapacks/` |
| `../../metiers_resourcepack.zip` (racine du dépôt) | Resource pack v24 : modèles 3D des outils et de l'armure (11 paliers, 6 skins), objets de la Forge, icônes, barres de boss |
| `sources/datapack.py` | Générateur du datapack (exécute ensuite `ref_base.py`, `ref_skills.py`, `ref_menu.py`, `ref_boss.py`, `ref_defis.py`) |
| `sources/glyphes.json` | Correspondance des icônes de la police `metiers:icones` |
| `sources/resourcepack/` | Scripts de génération du resource pack v24 |
| `sources/textures.py`, `armure.py`... | Anciens générateurs (v23), gardés pour l'historique |
| `build/` (non versionné) | Datapack décompressé produit par `datapack.py`, branché dans le labo |

Le resource pack reste à la racine du dépôt : son URL est inscrite dans le `server.properties` de la prod.

Pour tester une modification : `labo\lab-reload.bat` depuis la racine du dépôt (voir `labo/LISEZMOI.md`).

## Installation sur le serveur

Dans `server.properties` :

```
resource-pack=https://github.com/Katjounis/minecraft-metiers/raw/main/metiers_resourcepack.zip
resource-pack-sha1=410acf42343a2be582c16630b01384ab45ea80aa
require-resource-pack=true
```

Le SHA-1 doit être recalculé à chaque nouvelle version du resource pack.

## En jeu

Touche G (ou menu Échap) pour ouvrir le menu des métiers, ou `/trigger metiers`.

Commandes admin : `/function metiers:boss/alerte` (boss suivant de la rotation dans 2 min), `/function metiers:heure/lancer`, `/function metiers:defis/nouveaux`, `/function metiers:defis/semaine`.

## Version 25 (23/11/2026)

Bâtisseur (10e métier, lettre `k`, `sources/ref_batisseur.py`) : l'XP vient des blocs de construction posés (planches, escaliers, dalles, barrières, portes et trappes des 12 bois, briques, pierres polies et taillées, béton, terre cuite, verre, quartz, prismarine...), 4 points = 1 XP ; casser un de ces blocs retire autant de points, poser puis casser ne rapporte donc rien. Les blocs bruts restent au Mineur et au Bûcheron. Ses statistiques sont relevées toutes les 3 s (170 blocs suivis). Compétences : Bras long (portée +1), Pied sûr (chute /2), Échafaudeur (chute lente accroupi dans le vide), Cadence (Célérité I), Grand chantier (portée +3 en tout), Maître d'œuvre (Célérité II, Résistance I). Outil : la Truelle, incassable, qui donne +1 à +3 de portée tenue dans une main (textures 64 px pré-rendues dans `sources/textures_batisseur/` par la forme `trowel` de `textures.py`). Kit de chantier une fois par jour de jeu (niveau 20), capacité de prestige Architecte, synergie Charpentier avec le Bûcheron, quête en 10 étapes, barème illustré. Déclencheurs propres au 10e métier : compétences 1001 à 1006, titre 620, kit 614, barème 490. Le build écrit `build/metiers_rp/` (truelle, icônes, police `icones.json` complétée) que `fusion_rp.py` verse dans le zip sans jamais retirer `assets/metiers/`.

Aussi dans la 25 (`sources/ref_v26.py`) : synergies (deux métiers au niveau 50), quêtes (10 étapes par métier), guildes (créer, inviter, défi de la semaine, classement), boss plus durs (attaque et armure selon le niveau moyen de Chasseur, phase finale, 5 nouvelles attaques), effets visuels de montée de niveau et de palier, bandeaux en tête des menus. La touche G ouvre le menu commun aux trois packs (dialogue `serveur:menu`, identique dans Métiers, Commerce et Horreur).

## Mise à jour 24.1 (23/11/2026)

Boss : butin refait (2 tirages par niveau de difficulté, +1 au plus gros dégât, livres enchantés au niveau 30 (plus aucun outil, arme ni armure depuis la 25.8, les métiers les donnent déjà), débris antiques, minerais en blocs, disques), butin rare à 15 % par niveau de difficulté (+15 % au plus gros dégât) avec une relique propre à chaque boss (Hache du Colosse, Arc de la Reine, Trident du givre, Masse du Brasier, Arbalète du Creeper ; le Plastron du Brasier a été remplacé en 25.8, inutile à côté de l'Armure des Guildes). Les reliques portent `custom_data {metiers_relique:1b}` et se vendent 15 000 Écus au Commerce (catégorie Butin de boss, bouton « Vendre la relique en main », anciennes reliques reconnues par leur nom) ; le butin courant se vend dans la même catégorie. Corrections : le boss apparaît à 4 à 12 blocs du joueur, à sa hauteur, sur un sol avec 6 blocs d'air (avant, à la surface au-dessus d'un joueur en grotte ou sur le toit du Nether) ; PV plafonnés à 1 000 (le jeu bloque à 1 024, la barre de boss ne partait plus pleine à 4 joueurs et plus) et Résistance pour les gros groupes ; bond et clignement seulement vers un endroit libre (le boss restait coincé dans les murs) ; beau temps pendant le Brasier (la pluie lui retirait des PV).

Forge : un objet forgé (marteau, faux, arc triple, lasso, parchemin, aimant, cape) se récupère gratuitement dans la boutique s'il est perdu, comme les outils de métier : il ne doit être ni sur le joueur ni dans son coffre de l'Ender, une fois toutes les 10 minutes. Un joueur qui a déjà l'objet sur lui est noté comme propriétaire automatiquement ; pour un objet perdu avant la mise à jour, voir `admin/forge_<objet>` dans le guide admin.

Barème d'XP : touche G, « Barème d’XP » (ou le bouton en haut de la page d'un métier). Une page par métier, ce que rapporte chaque action avec les images du jeu (œufs d'apparition pour les créatures, textures des blocs et des objets). Les valeurs sont lues dans les tables de `datapack.py`, le barème suit si un poids change (`sources/ref_bareme.py`).

## Prestige (24.2, 23/11/2026)

Décors (25.8) : la page de chaque métier, ses récompenses et son barème s'ouvrent sur un décor propre au métier (blocs du métier en fond, nom en grosses lettres, outil de chaque côté), dessiné par Commerce (`SCENES`) et posé par `sources/ref_scenes.py` ; il faut le resource pack commun à jour.

Récompenses de palier (tous les 10 niveaux, 25.8) : l'outil évolue, plus des cristaux du métier (5, 10, 15, 20, 30, 45, 65, 90, 120, 160), des Écus à chaque palier (500 au palier 10 jusqu'à 75 000 au palier 100), des éclats de boss dès le niveau 40 (1, 1, 2, 3, 4, 5, 8) et des objets bonus propres au métier (`EXTRAS` dans `sources/datapack.py`). Les paliers déjà récupérés avant la 25.8 reçoivent une fois la différence de cristaux, d'éclats et d'Écus (`sources/ref_paliers.py`).

Au niveau 100 d'un métier, le prestige remet le niveau à 1 mais garde les compétences, et la progression continue : le niveau suivant demande 150 x 1,06^(niveau - 1) XP, et au moins 15 000 x étoiles (courbe exponentielle depuis la 25.3, durcie en 25.4, prestige assoupli en 25.5 : environ 1,7 million d'XP pour une étoile complète ; en 25.7, chaque joueur est recalculé une fois à la connexion sur cette courbe à partir de toute l'XP déjà gagnée, voir `sources/ref_recalcul.py`), donc le niveau 1 d'une étoile demande plus que le niveau 100 d'avant. Les points de compétence des niveaux passés restent acquis et toutes les compétences restent achetables. Chaque étoile n donne 100 x n cristaux du métier, 2 x n éclats de boss et 5 000 x n Écus (score `c.ecus` de Commerce), l'outil regagne ses étoiles dorées et un reflet, une annonce et un feu d'artifice. Une capacité de prestige par métier, débloquée à 1 étoile et renforcée à 3 et 5 (`sources/ref_prestige.py`, tags `metiers.sk.p<métier><1|3|5>`) : Sève dorée, Moisson, Filon, Exécution, Appât, Jumeaux, Érudit, Pas léger, Négociant. Aura de particules (bouton dans le menu G pour la couper) et cadre de titre Étoilé à 5 étoiles dans un métier.

## Interface « Forge »

Le resource pack recolore toute l'interface vanilla (inventaire, conteneurs, barre d'action, info-bulles, curseurs, boutons) au style de la Forge. Script : `sources/resourcepack/interface_forge.py <textures gui vanilla 26.x> metiers_resourcepack.zip`, puis `sources/resourcepack/correctifs_rp.py metiers_resourcepack.zip`.

## Sac à dos

Le sac s'ouvre en un clic droit : tant qu'il est tenu en main, une barque à coffre en bambou invisible (texture vidée par le resource pack) suit les yeux du joueur. Contrepartie : les vraies barques à coffre en bambou sont invisibles sur le serveur.

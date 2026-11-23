# Commerce : économie en Écus

Datapack vanilla (Minecraft Java 26.x) qui ajoute une économie au serveur, branchée sur le pack Métiers. **Métiers v24 doit être installé**, mais Commerce ne le modifie pas : il lit seulement ses scores (niveaux, cristaux, défis, boss, heure du métier, semaine) et utilise sa police d'icônes. Compatible avec le `metiers.zip` en prod au 22/11/2026.

## Ce que ça fait (version 1)

| Élément | Fonctionnement |
|---|---|
| Écus | Argent sur un compte (score `c.ecus`, centimes dans `c.cts`), impossible à perdre ou à voler |
| Déblocage | Crafter l'**oeuf de comptoir** débloque le Commerce. Recette : blocs d'émeraude aux 4 coins, bloc de diamant en haut, blocs d'or à gauche et à droite, lingot de netherite au centre, tonneau en bas. La grille de craft est dessinée avec les vraies textures du jeu dans la fenêtre de la touche G et sur la page du Commerce ; tant que l'oeuf n'est pas crafté, les autres boutons sont grisés |
| Comptoir | L'oeuf pose un villageois immobile et invincible « Comptoir de <pseudo> ». Un seul par joueur, utilisable par tous (clic droit). Touche G, Mon comptoir : il revient en oeuf pour être reposé ailleurs |
| Menu | Touche G (ou menu Échap), Commerce, « Ouvrir le Commerce » : compte, marché, bourse, fortunes, cristaux. Tout marche depuis n'importe où |
| Marché | 459 objets en 16 catégories (pierres, terre, fleurs, bois, 16 couleurs de laine, béton, terre cuite et verre, minerais et blocs, Nether et End, agriculture, élevage, pêche, cuisine, utilitaires et redstone, trésors), achat et vente par 1 à 640, « Tout vendre ». Les Trésors (diamant, netherite, élytres...) sont en vente seulement |
| Prix dynamiques | Chaque vente fait baisser le prix de l'objet (jusqu'à 30 % du prix de base), chaque achat le fait monter (jusqu'à 130 %), et le marché se détend en une heure de jeu environ. Le rachat vaut au moins 4 fois le prix de vente de base et ne baisse jamais (ni krach, ni marché saturé) |
| Bonus de métier | +0,5 % par niveau du métier lié à l'objet, +25 % pendant l'heure du métier |
| Bourse | Évènement de marché (pénurie x1,6 ou krach /2 pendant 2 h, 40 % de chances à chaque heure de jeu), tendance de chaque objet sur 1 h, top 5 des objets vendus et achetés de la semaine, top 3 des marchands |
| Fortunes | Les 10 plus gros soldes du serveur, joueurs déconnectés compris |
| Cristaux | Achetables : 2 500 Écus le premier, +5 % à chaque achat de la semaine (remise à zéro avec le défi de la semaine de Métiers) |
| Primes | 250 Écus x numéro du palier à chaque palier de métier, défi du jour 150, tous les défis 300, défi de la semaine 1 500, défi collectif 400, boss 600. Les paliers déjà passés avant l'installation ne sont pas payés |

Les prix de base et les volumes sont dans `sources/catalogue.py`. `sources/coherence.py` vérifie avec les données officielles de la 26.1 (`donnees_26.1.json`, tirées de minecraft-data) que chaque id existe et qu'aucune recette d'établi ou de four ne permet de racheter, fabriquer et revendre avec profit.

## Historique

- v12 (23/11/2026) : solde permanent en haut à gauche, spawners, graphiques. Le solde s'affiche dans un petit cadre en haut à gauche de l'écran, seul, sans barre de boss : c'est le « title » vanilla écrit dans la police `commerce:hud`, que le shader de texte du resource pack ramène dans le coin à l'échelle 1 (`sources/hud.py`, contrôle avec `sources/verifier_shaders.py`). Ses glyphes ont 9 % d'opacité, le shader les remet à 100 % : avec un shaderpack qui remplace ce shader (Oculus, Iris), le cadre n'apparaît simplement pas, rien ne s'affiche au milieu de l'écran. Le tableau de la barre latérale est retiré une fois (`tableau/on` pour le remettre). Spawners (`sources/spawners.py`) : 35 créatures (pas de boss), de 20 000 à 500 000 Écus, achetés depuis Accueil, Spawners. Clic droit sur le spawner posé : menu d'amélioration (Vitesse, Quantité, Portée, Capacité, 3 niveaux, de 40 à 150 % du prix chacun) réservé au propriétaire, qui seul peut aussi le ramasser avec ses améliorations. Personne ne peut le miner (entité interaction autour), il se reconstruit s'il explose. Ses créatures donnent la moitié de l'XP de Chasseur (dette retirée de `m.c_bal`, Métiers n'est pas modifié), les animaux naissent adultes sans pouvoir se reproduire et les moutons restent tondus : pas d'XP d'Éleveur. Graphiques (`sources/grafiques.py`, police `commerce:graph`) : courbes de cours sur 24 h et 14 jours, histogrammes des quantités vendues et achetées par jour (14) et par semaine (8) pour chaque objet, et pour tout le marché l'indice sur 24 h et les Écus échangés par jour et par semaine. Chaque colonne a une infobulle, un clic sur un jour ouvre son détail (pour le marché : les 5 objets les plus vendus et achetés ce jour-là, cliquables). Le jour et la semaine sont ceux des défis de Métiers.
- v11 (23/11/2026) : coffres privés. Un panneau « [Privé] » (ou [Prive], [privé]…) sur un coffre, un coffre piégé ou un tonneau le réserve à celui qui l'a posé : verrou vanilla levé seulement si le propriétaire est à moins de 6 blocs et personne d'autre à moins de 8, coffre et panneau reconstruits avec leur contenu s'ils sont cassés ou explosés, entonnoir dessous mis en pause, wagonnet à entonnoir désactivé, coffre double protégé en entier. Le propriétaire casse le panneau pour retirer la protection. Code dans `sources/prive.py`.
- v10 (22/11/2026) : solde de tous les joueurs affiché en permanence dans la barre latérale (à droite, trié du plus riche au moins riche), achats payés au centime près (le prix affiché pour 1 vitre n'est plus arrondi à 1 Écu).
- v9 (22/11/2026) : bandeaux de titre au style de l'interface Forge (Commerce, Marché, Bourse, Fortunes, Cristaux), courbe du cours sur 24 h de jeu sur chaque objet, indice du marché avec sa courbe dans la Bourse, libellés de boutons raccourcis (nom complet en infobulle), « d’acajou » au lieu de « de acajou ».
- v8 (22/11/2026) : menus compacts, sans défilement pour trouver les boutons : marché en boutons avec la texture de chaque catégorie, catégories en pages de 10 objets (prix au survol), page d'un objet avec le prix total écrit sur chaque bouton (vendre et acheter 1, 16, 64, tout vendre). Recette de l'oeuf en une seule image (texture d'établi Forge et vraies textures des ingrédients). Clic droit sur le comptoir corrigé (le joueur était effacé avant d'être lu).
- v7 (22/11/2026) : la vente ne marchait pas, une commande mal écrite faisait ignorer toute la fonction de vente par le jeu. Corrigé, et `verifier.py` contrôle maintenant la structure des commandes data et scoreboard.
- v6 (22/11/2026) : le fond d'établi de la v4 ne s'affichait pas (glyphe de 264 px, au-delà de la limite de 256 des polices), d'où la première ligne décalée. Il est remplacé par le haut de la vraie texture d'établi du resource pack (interface Forge), cases calées sur les textures des objets.
- v5 (22/11/2026) : « oe » au lieu de « œ » partout (la police de l'interface Forge n'a pas ce caractère), et vraie pièce d'Écu dessinée (glyphe `ecu.png`) à la place du symbole ¤.
- v4 (22/11/2026) : vrai fond d'établi derrière la recette de l'oeuf (resource pack), lignes de largeur identique pour que la grille ne se décale plus.
- v3 (22/11/2026) : le serveur refusait de démarrer à cause de deux progrès écrits au format 1.21 (`clic_comptoir`, `debloque`). Le pack n'utilise plus aucun progrès : clic par entité `interaction`, déblocage par statistique de craft. Table de butin passée au format 26.x (`modifier`, `type`). `verifier.py` signale maintenant ces anciens formats.

## Resource pack

Commerce ajoute `assets/commerce/` (polices `commerce:recette`, `commerce:hud` et `commerce:graph`) et `assets/minecraft/shaders/core/text.vsh|fsh` (cadre du solde) au resource pack commun : `python sources/datapack.py` puis `python labo/outils/fusion_rp.py` depuis la racine du dépôt. Le SHA-1 affiché va dans `resource-pack-sha1` du `server.properties` une fois le zip poussé sur main.

## Fichiers

| Fichier | Rôle |
|---|---|
| `commerce.zip` | Le datapack, à mettre dans `world/datapacks/` à côté de `metiers.zip` |
| `sources/datapack.py` | Générateur (écrit `build/commerce_datapack/` et `commerce.zip`) |
| `sources/catalogue.py` | Objets, prix, volumes, métiers liés, catégories |
| `sources/coherence.py` | Contrôle du catalogue (ids 26.1, boucles de craft rentables) |
| `sources/donnees_26.1.json` | Liste des objets et recettes de la 26.1 |
| `sources/sprites_26.1.json` | Texture de chaque objet du catalogue (atlas et chemin), pour les icônes des boutons |
| `sources/textures_recette/` | Les 6 textures vanilla collées dans l'image de la recette de l'oeuf |
| `sources/hud.py`, `sources/spawners.py`, `sources/grafiques.py`, `sources/prive.py` | Modules exécutés par `datapack.py` : solde en haut à gauche, spawners, graphiques, coffres privés |
| `sources/verifier_shaders.py`, `sources/shaders_26.3/` | Compile le shader de texte modifié dans chaque variante du jeu (glslangValidator) |
| `sources/verifier.py` | Contrôle statique du pack généré (JSON, macros, fonctions, SNBT des dialogues). Demande `pip install nbtlib` |

## Liens avec Métiers

Commerce ne touche à aucun fichier de Métiers. Chaque seconde il lit `m.dd_<métier>` (défis du jour), `m.wd` (défi de la semaine), `m.wk` (défi collectif), `m.bk1` à `m.bk5` (boss vaincus) et `#semaine m.defi` (nouvelle semaine), et paie quand ils changent. Si Métiers renomme un de ces scores, il faut adapter `joueur/evts` ici.

Attention : les sources de Métiers dans ce dépôt sont en retard sur le `metiers.zip` de la prod (butin des boss, soie, rappel des défis...). Il ne faut pas régénérer `metiers.zip` depuis ces sources tant qu'elles n'ont pas été remises à jour.

## Installation et test

1. `python sources/coherence.py`, `python sources/datapack.py` puis `python sources/verifier.py` (doivent finir sans erreur).
2. Labo : `labo\lab-reload.bat complet` (le menu G a changé, redémarrage obligatoire), jusqu'à « Aucune erreur. ».
3. Prod : déposer `commerce.zip` à côté du `metiers.zip` actuel (on n'y touche pas), puis **redémarrer** (le menu G n'est lu qu'au démarrage).

Avec deux packs dans la touche G, le jeu affiche d'abord la liste « Métiers / Commerce ».

## Commandes admin

| Commande | Effet |
|---|---|
| `/function commerce:version` | Version chargée |
| `/function commerce:admin/oeuf` | Donne un oeuf de comptoir |
| `/function commerce:admin/ecus` | +10 000 Écus (tests) |
| `/function commerce:admin/evenement` | Lance un évènement de marché |
| `/function commerce:admin/marche_reset` | Remet tous les prix au calme |
| `/function commerce:tableau/off` | Retire le tableau des Écus de la barre latérale (`tableau/on` pour le remettre) |
| `/function commerce:admin/spawner` | Donne un spawner de zombie (tests) |
| `/function commerce:desinstaller` | Supprime les scores avant de retirer le zip |

## À tester en priorité au labo

- Solde en haut à gauche : cadre visible sans shaderpack, à la bonne place à toutes les échelles d'interface ; rien au milieu de l'écran avec un shaderpack.
- Spawners : pose par un joueur non op (le bloc doit se remplir dans le tick), clic droit, amélioration, ramassage, reconstruction après une explosion de creeper, XP de Chasseur divisée par deux.
- Graphiques : infobulles et clics sur les colonnes et les repères dans les dialogues.
- Coffres privés : que le texte du panneau soit bien reconnu en 26.3 (texte simple ou composant), que le verrou (`lock`) bloque l'ouverture, et que la reconstruction remette le contenu sans doublon.

- Le nom du comptoir et le classement des fortunes : le pseudo est lu sur une tête de joueur générée (`profile.name`). Si le comptoir s'appelle « Comptoir de Joueur », ce chemin a changé en 26.x.
- Le clic droit sur le comptoir ouvre bien le menu (entité `interaction` posée sur le villageois, lue chaque tick).
- Le craft de l'oeuf débloque le Commerce dans la seconde (statistique `minecraft.crafted:minecraft.villager_spawn_egg`).
- La recette de l'oeuf apparaît dans l'établi : si la 26.x refuse son format, le serveur démarre quand même mais la recette est absente du log (`Parsing error loading recipe commerce:oeuf`).
- Les listes déroulantes de quantité (dialogue `single_option` + `dynamic/run_command`).
- La grille de craft : fond repris de la texture d'établi du resource pack commun (interface Forge), à l'échelle 1/2 (glyphe `etabli.png` de la police `commerce:recette`, 256 px de côté au plus, sinon le jeu ne l'affiche pas) et textures des objets par-dessus via le composant de texte `object` (atlas `minecraft:blocks` et `minecraft:items`). Les positions viennent de mesures en jeu (sprite de 8 px, avance 8, haut à y = -1, lignes de 9 px) : si les objets tombent à côté des cases, ajuster `GX`, `RX` ou `PTOP` dans `datapack.py`.

## Prévu ensuite

Virements entre joueurs, historique des opérations, hôtel des ventes, courbes de prix sur 24 h, icône d'Écu et fond illustré dans le resource pack, métier Bâtisseur (Métiers v25) avec crédits de pose des blocs achetés.

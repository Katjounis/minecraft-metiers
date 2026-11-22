# Commerce : économie en Écus

Datapack vanilla (Minecraft Java 26.x) qui ajoute une économie au serveur, branchée sur le pack Métiers. **Métiers v24 doit être installé**, mais Commerce ne le modifie pas : il lit seulement ses scores (niveaux, cristaux, défis, boss, heure du métier, semaine) et utilise sa police d'icônes. Compatible avec le `metiers.zip` en prod au 22/11/2026.

## Ce que ça fait (version 1)

| Élément | Fonctionnement |
|---|---|
| Écus | Argent sur un compte (score `c.ecus`, centimes dans `c.cts`), impossible à perdre ou à voler |
| Déblocage | Crafter l'**œuf de comptoir** débloque le Commerce. Recette : blocs d'émeraude aux 4 coins, bloc de diamant en haut, blocs d'or à gauche et à droite, lingot de netherite au centre, tonneau en bas. La grille de craft est dessinée avec les vraies textures du jeu dans la fenêtre de la touche G et sur la page du Commerce ; tant que l'œuf n'est pas crafté, les autres boutons sont grisés |
| Comptoir | L'œuf pose un villageois immobile et invincible « Comptoir de <pseudo> ». Un seul par joueur, utilisable par tous (clic droit). Touche G, Mon comptoir : il revient en œuf pour être reposé ailleurs |
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

- v3 (22/11/2026) : le serveur refusait de démarrer à cause de deux progrès écrits au format 1.21 (`clic_comptoir`, `debloque`). Le pack n'utilise plus aucun progrès : clic par entité `interaction`, déblocage par statistique de craft. Table de butin passée au format 26.x (`modifier`, `type`). `verifier.py` signale maintenant ces anciens formats.

## Fichiers

| Fichier | Rôle |
|---|---|
| `commerce.zip` | Le datapack, à mettre dans `world/datapacks/` à côté de `metiers.zip` |
| `sources/datapack.py` | Générateur (écrit `build/commerce_datapack/` et `commerce.zip`) |
| `sources/catalogue.py` | Objets, prix, volumes, métiers liés, catégories |
| `sources/coherence.py` | Contrôle du catalogue (ids 26.1, boucles de craft rentables) |
| `sources/donnees_26.1.json` | Liste des objets et recettes de la 26.1 |
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
| `/function commerce:admin/oeuf` | Donne un œuf de comptoir |
| `/function commerce:admin/ecus` | +10 000 Écus (tests) |
| `/function commerce:admin/evenement` | Lance un évènement de marché |
| `/function commerce:admin/marche_reset` | Remet tous les prix au calme |
| `/function commerce:desinstaller` | Supprime les scores avant de retirer le zip |

## À tester en priorité au labo

- Le nom du comptoir et le classement des fortunes : le pseudo est lu sur une tête de joueur générée (`profile.name`). Si le comptoir s'appelle « Comptoir de Joueur », ce chemin a changé en 26.x.
- Le clic droit sur le comptoir ouvre bien le menu (entité `interaction` posée sur le villageois, lue chaque tick).
- Le craft de l'œuf débloque le Commerce dans la seconde (statistique `minecraft.crafted:minecraft.villager_spawn_egg`).
- La recette de l'œuf apparaît dans l'établi : si la 26.x refuse son format, le serveur démarre quand même mais la recette est absente du log (`Parsing error loading recipe commerce:oeuf`).
- Les listes déroulantes de quantité (dialogue `single_option` + `dynamic/run_command`).
- La grille de craft : elle utilise le composant de texte `object` (atlas `minecraft:blocks` et `minecraft:items`, découpage valable depuis la 1.21.11). Si une case affiche le damier violet et noir, le nom de l'atlas ou de la texture a changé en 26.x : à corriger dans `SPR` de `datapack.py`.

## Prévu ensuite

Virements entre joueurs, historique des opérations, hôtel des ventes, courbes de prix sur 24 h, icône d'Écu et fond illustré dans le resource pack, métier Bâtisseur (Métiers v25) avec crédits de pose des blocs achetés.

# Commerce : économie en Écus

Datapack vanilla (Minecraft Java 26.x) qui ajoute une économie au serveur, branchée sur le pack Métiers. **Métiers doit être installé** : Commerce lit ses niveaux, ses cristaux, son heure du métier et sa police d'icônes.

## Ce que ça fait (version 1)

| Élément | Fonctionnement |
|---|---|
| Écus | Argent sur un compte (score `c.ecus`, centimes dans `c.cts`), impossible à perdre ou à voler |
| Déblocage | Crafter l'**œuf de comptoir** débloque le Commerce. Recette : blocs d'émeraude aux 4 coins, bloc de diamant en haut, blocs d'or à gauche et à droite, lingot de netherite au centre, coffre en bas |
| Comptoir | L'œuf pose un villageois immobile et invincible « Comptoir de <pseudo> ». Un seul par joueur, utilisable par tous (clic droit). Touche G, Mon comptoir : il revient en œuf pour être reposé ailleurs |
| Menu | Touche G (ou menu Échap), Commerce : compte, marché, bourse, fortunes, cristaux. Tout marche depuis n'importe où |
| Marché | 133 objets en 9 catégories, achat et vente par 1 à 640, « Tout vendre ». Les Trésors (diamant, netherite, élytres...) sont en vente seulement |
| Prix dynamiques | Chaque vente fait baisser le prix de l'objet (jusqu'à 30 % du prix de base), chaque achat le fait monter (jusqu'à 130 %), et le marché se détend en une heure de jeu environ. Rachat = 4 fois le prix de vente |
| Bonus de métier | +0,5 % par niveau du métier lié à l'objet, +25 % pendant l'heure du métier |
| Bourse | Évènement de marché (pénurie x1,6 ou krach /2 pendant 2 h, 40 % de chances à chaque heure de jeu), tendance de chaque objet sur 1 h, top 5 des objets vendus et achetés de la semaine, top 3 des marchands |
| Fortunes | Les 10 plus gros soldes du serveur, joueurs déconnectés compris |
| Cristaux | Achetables : 2 500 Écus le premier, +5 % à chaque achat de la semaine (remise à zéro avec le défi de la semaine de Métiers) |
| Primes | 250 Écus x numéro du palier à chaque palier de métier, défi du jour 150, tous les défis 300, défi de la semaine 1 500, défi collectif 400, boss 600 (+600 pour les plus gros dégâts) |

Les prix de base et les volumes sont dans `sources/catalogue.py`, avec la règle de cohérence anti-boucle (un objet fabriqué ne se vend jamais plus cher que ses ingrédients rachetés).

## Fichiers

| Fichier | Rôle |
|---|---|
| `commerce.zip` | Le datapack, à mettre dans `world/datapacks/` à côté de `metiers.zip` |
| `sources/datapack.py` | Générateur (écrit `build/commerce_datapack/` et `commerce.zip`) |
| `sources/catalogue.py` | Objets, prix, volumes, métiers liés, catégories |
| `sources/verifier.py` | Contrôle statique du pack généré (JSON, macros, fonctions, SNBT des dialogues). Demande `pip install nbtlib` |

## Liens avec Métiers

Métiers appelle des tags de fonction vides (`#metiers:evt/defi_jour`, `defis_tous`, `defi_semaine`, `defi_collectif`, `boss`, `nouvelle_semaine`) que Commerce remplit. Métiers marche donc toujours seul. Il faut la version de `metiers.zip` qui contient ces tags (régénérée avec ce pack).

## Installation et test

1. `python sources/datapack.py` puis `python sources/verifier.py` (doit afficher « Aucune erreur statique. »).
2. Labo : `labo\lab-reload.bat complet` (le menu G a changé, redémarrage obligatoire), jusqu'à « Aucune erreur. ».
3. Prod : déposer `commerce.zip` et le nouveau `metiers.zip`, puis **redémarrer** (le menu G n'est lu qu'au démarrage).

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
- Le clic droit sur le comptoir ouvre bien le menu (progrès `player_interacted_with_entity`).
- Les listes déroulantes de quantité (dialogue `single_option` + `dynamic/run_command`).

## Prévu ensuite

Virements entre joueurs, historique des opérations, hôtel des ventes, courbes de prix sur 24 h, icône d'Écu et fond illustré dans le resource pack, métier Bâtisseur (Métiers v25) avec crédits de pose des blocs achetés.

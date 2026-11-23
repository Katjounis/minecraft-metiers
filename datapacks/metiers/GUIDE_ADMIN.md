# Serveur Minecraft : guide de passation du pack Métiers

Ce document résume tout ce qui tourne sur le serveur (hébergé chez Dawn, Minecraft Java 26.x, sans mod ni plugin) pour pouvoir le gérer sans repartir de zéro. Tout le système repose sur un datapack et un resource pack que j'ai fait générer, avec les sources dans le dépôt GitHub.

Dépôt : https://github.com/Katjounis/minecraft-metiers

## 1. Ce qui est installé

| Élément | Où | Rôle |
|---|---|---|
| `metiers.zip` | `world/datapacks/` sur le serveur | Toute la logique : métiers, niveaux, menus, défis, boss, etc. |
| `metiers_resourcepack.zip` | Hébergé sur le GitHub, imposé par `server.properties` | Textures des outils évolutifs (64x64 animées), de l'armure (portée et icônes) et modèle 3D du heaume |

Version actuelle du datapack : **24.1** (refonte : outils et armure sur 11 paliers, Forge, skins, 5 boss, défis de la semaine et collectifs ; depuis le 23/11/2026, butin et reliques des boss, apparition des boss corrigée, objets de la Forge récupérables). Pour vérifier en jeu : `/function metiers:version`.

### Réglages dans `server.properties`

```
require-resource-pack=true
resource-pack=https://github.com/Katjounis/minecraft-metiers/raw/main/metiers_resourcepack.zip
resource-pack-sha1=db78744b9895956bffce93eae8a5b981bbde63e6
```

Ces lignes existent déjà dans le fichier, il faut les modifier à leur place et pas les ajouter en double. Le serveur peut réécrire le lien en `https\://...`, c'est normal.

Le `require` est important : un joueur sans le pack voit les outils et l'armure en damier violet et noir.

## 2. Mettre à jour

### Le datapack
1. Supprimer **tout** ancien fichier métiers dans `world/datapacks/` (y compris un `metiers (1).zip` ou un dossier décompressé).
2. Déposer le nouveau `metiers.zip`.
3. `/reload` suffit pour la logique. Un **redémarrage complet** est obligatoire si le menu de la touche G a changé (ce menu n'est lu qu'au démarrage).
4. Vérifier avec `/function metiers:version` et `/datapack list` (le pack doit apparaître une seule fois).

### Le resource pack
1. Pousser le nouveau zip sur le GitHub (même nom, même endroit).
2. Remplacer `resource-pack-sha1` dans `server.properties` par l'empreinte SHA-1 du nouveau fichier.
3. Redémarrer. GitHub garde l'ancien fichier en cache quelques minutes : si un joueur a une erreur de téléchargement juste après, attendre 5 minutes.

## 3. Commandes admin utiles

| Commande | Effet |
|---|---|
| `/function metiers:version` | Affiche la version chargée |
| `/execute as <pseudo> run function metiers:admin/forge_<objet>` | Note un joueur comme propriétaire d'un objet de la Forge perdu avant la 24.1 (`marteau`, `faux`, `arc3`, `lasso`, `parchemin`, `aimant`, `cape`) : il peut ensuite le récupérer gratuitement dans la boutique |
| `/function metiers:boss/alerte` | Annonce le boss suivant de la rotation, il apparaît 2 minutes après (il faut au moins 2 joueurs) |
| `/function metiers:defis/semaine` | Relance le défi de la semaine et le défi collectif |
| `/function metiers:heure/lancer` | Lance une heure du métier (XP x2 sur un métier tiré au sort) |
| `/function metiers:defis/nouveaux` | Tire de nouveaux défis du jour |
| `/function metiers:classement` | Niveaux de tous les joueurs connectés dans le chat |
| `/execute as <pseudo> run function metiers:reset_joueur` | Remet un joueur à zéro dans tous les métiers |
| `/function metiers:desinstaller` | Désinstalle proprement (à faire avant de retirer le zip) |
| `/gamerule send_command_feedback true` | Réaffiche les retours de commandes (désactivés par le pack pour cacher les messages « Triggered ») |

Le pack désactive `send_command_feedback` pour que les clics dans les menus ne spamment pas le chat. Conséquence : les commandes admin n'affichent plus de confirmation. On peut le réactiver ponctuellement avec la commande ci-dessus.

## 4. Fonctionnement côté joueurs

### Accès
Touche **G** (actions rapides, réglable dans les options) ou bouton **Métiers** dans le menu Échap. En secours : `/trigger metiers`. Les progrès (touche **L**) contiennent un onglet par métier avec l'arbre des compétences et les paliers.

### Les 9 métiers (niveau max 100)

| Métier | Gagne de l'XP en | Outil évolutif |
|---|---|---|
| Bûcheron | coupant des bûches (1 XP) | hache |
| Mineur | minant pierre (1/2), deepslate (3/4) et minerais (diamant 20, débris 40) | pioche |
| Fermier | récoltant (environ 1,5 XP par plant) | houe |
| Chasseur | tuant des créatures, XP selon la créature (1 à 21, boss 45 à 300) | épée |
| Pêcheur | pêchant (8 XP, multiplié par la série et l'ambiance) | canne |
| Éleveur | faisant naître des animaux (8) et ramassant de la laine (1/2) | cisailles |
| Enchanteur | enchantant (20, 40 ou 60 XP selon les niveaux dépensés) | grimoire |
| Explorateur | se déplaçant (20 XP par 200 m, élytres et cheval comptent moins) | bottes |
| Marchand | échangeant avec les villageois (6) | bourse |

XP par niveau : `10 x niveau + 40`. Anti-triche : poser ou jeter un objet récolté retire l'XP gagnée avec. La netherrack ne rapporte rien.

### Progression
- **Compétences** : 1 point par niveau, un arbre de 6 compétences par métier (deux branches et une ultime). Se débloquent dans le menu du métier.
- **Paliers** : tous les 10 niveaux, l'outil du métier évolue automatiquement (texture, enchantements) et un écran propose des récompenses bonus, avec vérification de place dans l'inventaire.
- **Titres** : préfixe devant le pseudo (Apprenti, Initié, ..., Dieu), au choix du joueur parmi ses métiers.
- **Prestige** : au niveau 100, retour au niveau 1 contre une étoile et +10 % d'XP dans ce métier (5 étoiles max). L'outil est conservé.

### Outils et armure
- Un seul outil par métier, lié au joueur. Il évolue sur place à chaque palier (en main il reste en main, ailleurs il arrive dans l'inventaire).
- Incassable à partir du niveau 50. Avant, il se bloque à 3 de durabilité au lieu de casser. Réparation uniquement via le menu (5 niveaux d'XP), l'enclume et le Raccommodage sont bloqués.
- **Armure des Guildes** : 4 pièces, 5 paliers selon le score total (somme des niveaux, +100 par prestige) : 50, 120, 220, 350, 520 points. Bonus quand le set complet est porté. Rien ne s'équipe automatiquement : une pièce portée est remplacée sur place, sinon elle arrive dans l'inventaire.
- **Anti-duplication** : chaque outil et pièce d'armure porte le numéro du joueur et un numéro de série qui change à chaque redistribution. Une copie (coffre, ancien exemplaire, objet d'un autre joueur) disparaît dès qu'elle est tenue ou portée.

### Contenu commun
- **Défis du jour** : un défi par métier, affiché dans une barre de boss par joueur. Renouvelés toutes les 4 heures de jeu (seulement le temps où quelqu'un est connecté, le pack n'a pas accès à l'heure réelle). Récompense : un demi-niveau du métier, 2 diamants, 16 fioles. Les 9 : une pomme de Notch et 2 fragments de netherite en plus.
- **Classement** : podium général et meilleur de chaque métier, dans le menu. Les pseudos se mettent à jour toutes les 30 secondes pour les joueurs connectés.
- **Heure du métier** : toutes les 1 h 30 de jeu, un métier rapporte x2 pendant 30 minutes.
- **Le Colosse des Métiers** : boss toutes les 3 heures s'il y a au moins 2 joueurs, annoncé 2 minutes avant. Tous ceux qui l'ont frappé sont récompensés.
- **Pêcheur** : série de prises (jusqu'à x3), bonus pluie, nuit et océan, 10 poissons légendaires à collectionner (Carnet du pêcheur), coffres des profondeurs.

## 5. Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| Le serveur refuse de démarrer, « Failed to load datapacks » | Un fichier de registre du pack est mal formé (prédicat, progrès, menu) | Chercher `Errors in registry` dans `logs/latest.log`, me transmettre le bloc. En urgence : retirer `metiers.zip` pour relancer |
| Outils ou armure en damier violet et noir | Resource pack pas chargé | Vérifier les 3 lignes de `server.properties` et l'empreinte SHA-1 |
| Le menu G montre des anciens boutons | Le menu n'est relu qu'au démarrage | Redémarrage complet |
| Comportement d'une ancienne version | Deux zips dans `datapacks/` ou fichier pas remplacé | `/datapack list` puis nettoyer le dossier |
| Une fonction ne réagit pas | Erreur de chargement isolée | Chercher `metiers` dans `logs/latest.log` |

Les nouvelles fonctionnalités passent par des appels isolés : si l'une plante, elle ne bloque ni le reste ni le démarrage. Seuls les fichiers de registre (menu G, progrès, tags) peuvent empêcher le serveur de démarrer.

## 6. Modifier le pack

Les sources sont dans `datapacks/metiers/sources/` du dépôt :
- `datapack.py` génère tout le datapack (valeurs d'XP, compétences, récompenses, défis, etc. sont des tableaux en haut du fichier) ;
- `textures.py` génère les textures des outils, `armure.py` celles de l'armure.

Après modification : tester dans le labo (`labo\lab-reload.bat`, voir `labo/LISEZMOI.md`), refaire les zips, mettre à jour l'empreinte SHA-1 si le resource pack change. Le plus simple reste de me demander la modification.

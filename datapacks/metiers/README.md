# Métiers : datapack et resource pack

Datapack vanilla de métiers (Bûcheron, Fermier, Mineur, Chasseur, Pêcheur, Éleveur, Enchanteur, Explorateur, Marchand) pour notre serveur, avec niveaux jusqu'à 100, arbres de compétences, outils et armure sur 11 paliers, Forge (cristaux et éclats), skins et cadres de titre, défis du jour, de la semaine et collectifs, classement, prestige, heure du métier et 5 boss de serveur en rotation.

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
resource-pack-sha1=db78744b9895956bffce93eae8a5b981bbde63e6
require-resource-pack=true
```

Le SHA-1 doit être recalculé à chaque nouvelle version du resource pack.

## En jeu

Touche G (ou menu Échap) pour ouvrir le menu des métiers, ou `/trigger metiers`.

Commandes admin : `/function metiers:boss/alerte` (boss suivant de la rotation dans 2 min), `/function metiers:heure/lancer`, `/function metiers:defis/nouveaux`, `/function metiers:defis/semaine`.

## Mise à jour 24.1 (23/11/2026)

Boss : butin refait (2 tirages par niveau de difficulté, +1 au plus gros dégât, objets enchantés au niveau 30, débris antiques, minerais en blocs, disques), butin rare à 15 % par niveau de difficulté (+15 % au plus gros dégât) avec une relique propre à chaque boss (Hache du Colosse, Arc de la Reine, Trident du givre, Plastron du Brasier, Arbalète du Creeper). Corrections : le boss apparaît à 4 à 12 blocs du joueur, à sa hauteur, sur un sol avec 6 blocs d'air (avant, à la surface au-dessus d'un joueur en grotte ou sur le toit du Nether) ; PV plafonnés à 1 000 (le jeu bloque à 1 024, la barre de boss ne partait plus pleine à 4 joueurs et plus) et Résistance pour les gros groupes ; bond et clignement seulement vers un endroit libre (le boss restait coincé dans les murs) ; beau temps pendant le Brasier (la pluie lui retirait des PV).

Forge : un objet forgé (marteau, faux, arc triple, lasso, parchemin, aimant, cape) se récupère gratuitement dans la boutique s'il est perdu, comme les outils de métier : il ne doit être ni sur le joueur ni dans son coffre de l'Ender, une fois toutes les 10 minutes. Un joueur qui a déjà l'objet sur lui est noté comme propriétaire automatiquement ; pour un objet perdu avant la mise à jour, voir `admin/forge_<objet>` dans le guide admin.

Barème d'XP : touche G, « Barème d’XP » (ou le bouton en haut de la page d'un métier). Une page par métier, ce que rapporte chaque action avec les images du jeu (œufs d'apparition pour les créatures, textures des blocs et des objets). Les valeurs sont lues dans les tables de `datapack.py`, le barème suit si un poids change (`sources/ref_bareme.py`).

## Interface « Forge »

Le resource pack recolore toute l'interface vanilla (inventaire, conteneurs, barre d'action, info-bulles, curseurs, boutons) au style de la Forge. Script : `sources/resourcepack/interface_forge.py <textures gui vanilla 26.x> metiers_resourcepack.zip`, puis `sources/resourcepack/correctifs_rp.py metiers_resourcepack.zip`.

## Sac à dos

Le sac s'ouvre en un clic droit : tant qu'il est tenu en main, une barque à coffre en bambou invisible (texture vidée par le resource pack) suit les yeux du joueur. Contrepartie : les vraies barques à coffre en bambou sont invisibles sur le serveur.

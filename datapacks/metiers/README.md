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
resource-pack-sha1=3ef0c978b28f6d2522ea118f2aac7b7fd8d8739a
require-resource-pack=true
```

Le SHA-1 doit être recalculé à chaque nouvelle version du resource pack.

## En jeu

Touche G (ou menu Échap) pour ouvrir le menu des métiers, ou `/trigger metiers`.

Commandes admin : `/function metiers:boss/alerte` (boss suivant de la rotation dans 2 min), `/function metiers:heure/lancer`, `/function metiers:defis/nouveaux`, `/function metiers:defis/semaine`.

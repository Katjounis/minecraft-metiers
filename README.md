# Usine à datapacks Minecraft

Ce dépôt sert à fabriquer des datapacks pour Minecraft Java 26.x (vanilla, sans mod ni plugin). Il réunit les sources de chaque pack et un **labo**, c'est-à-dire un serveur local de test.

## Organisation

| Dossier | Contenu |
|---|---|
| `datapacks/<nom>/` | Un pack : ses sources, sa doc et le zip à installer |
| `datapacks/metiers/` | **Métiers** : niveaux, compétences, menus, défis, boss. Voir son [README](datapacks/metiers/README.md) |
| `metiers_resourcepack.zip` | Resource pack de Métiers. Il reste à la racine parce que son URL est utilisée par le serveur. |
| `labo/` | Scripts du serveur de test. Voir [labo/LISEZMOI.md](labo/LISEZMOI.md) |

## Ajouter un pack

Créer `datapacks/<nom>/` avec l'une de ces deux formes :

- **Pack écrit à la main** : `datapacks/<nom>/datapack/` contient `pack.mcmeta` et `data/`. Le labo le zippe au déploiement en `<nom>.zip`.
- **Pack généré par script** : `datapacks/<nom>/sources/datapack.py` écrit le pack décompressé dans `datapacks/<nom>/build/<nom>_datapack/` et le zip dans `datapacks/<nom>/<nom>.zip`. C'est le cas de Métiers.

Le labo détecte les packs tout seul (`python labo\outils\labo.py packs`). Il les branche dans son monde par des jonctions : une modification des sources est visible après `lab-reload.bat`, sans zip à refaire.

## Démarrage rapide

```
copy labo\local.exemple.cmd labo\local.cmd    (puis adapter les chemins)
labo\installer.bat
labo\lab-start.bat                            (serveur sur localhost:25566)
labo\lab-reload.bat                           (après chaque modification)
```

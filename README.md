# Usine à datapacks Minecraft

Ce dépôt sert à fabriquer des datapacks pour Minecraft Java 26.x (vanilla, sans mod ni plugin). Il réunit les sources de chaque pack et un **labo**, c'est-à-dire un serveur local de test.

## Organisation

| Dossier | Contenu |
|---|---|
| `datapacks/<nom>/` | Un pack : ses sources, sa doc et le zip à installer |
| `datapacks/metiers/` | **Métiers** : niveaux, compétences, menus, défis, boss. Voir son [README](datapacks/metiers/README.md) |
| `datapacks/commerce/` | **Commerce** : Écus, comptoirs, marché à prix dynamiques, bourse, fortunes, cristaux. Dépend de Métiers. Voir son [README](datapacks/commerce/README.md) |
| `datapacks/horreur/` | **Horreur** : créatures de cauchemar la nuit et bestiaire. Voir son [README](datapacks/horreur/README.md) |
| `datapacks/compagnons/` | **Compagnons** : 6 compagnons qui se battent et progressent avec le joueur, débloqués par Métiers. Voir son [README](datapacks/compagnons/README.md) |
| `datapacks/boss/` | **Boss** : le Grimoire Vivant et le Corbeau-Épouvantail, boss de serveur modélisés et animés dans leurs propres arènes (dimensions), qui se réveillent toutes les 3 à 5 h. Voir son [README](datapacks/boss/README.md) |
| `labo/outils/badges.py` | Faces dessinées des boutons (essai du 24/11/2026), débranché à la demande de Samuel : plus appelé par les packs, gardé pour mémoire. |
| `metiers_resourcepack.zip` | Resource pack commun à tous les packs, car le serveur n'en impose qu'un. Il reste à la racine parce que son URL est utilisée par le serveur. `python labo\outils\fusion_rp.py` y verse les textures des autres packs (`build/<nom>_rp/`). Le décor des menus en jeu (paysage de nuit animé calculé par un shader à la place du flou, `decor_menu.fsh`) se pose avec `python datapacks\metiers\sources\resourcepack\fond_menus.py metiers_resourcepack.zip`. |
| `datapacks/metiers/sources/resourcepack/interface_finition.py` | Finition de l'interface « Forge », à relancer après `interface_forge.py` : briques ombrées sur la pierre des panneaux, cases creusées en dégradé, niche en dégradé à la place des aplats noirs, boutons pierre sombre et laiton, barre d'action et bossbars à embouts en laiton. S'applique directement au zip : `python datapacks\metiers\sources\resourcepack\interface_finition.py metiers_resourcepack.zip`. |
| `datapacks/metiers/sources/resourcepack/interface_animations.py` | Animations de l'interface, à relancer après `interface_finition.py` : bossbars haute définition (canal en pierre, embouts en laiton, graduations, reflet qui balaie la barre), crans en laiton, barre d'expérience assortie, éclat lumineux sur le bouton survolé, sélection de la barre d'action qui pulse, flamme du four qui vacille. `python datapacks\metiers\sources\resourcepack\interface_animations.py metiers_resourcepack.zip` |
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

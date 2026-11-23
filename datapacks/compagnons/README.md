# Compagnons

Datapack vanilla (Minecraft Java 26.x) : chaque joueur a un compagnon qui le suit, se bat avec lui et gagne ses propres niveaux. Branché sur Métiers (déblocage par les niveaux de métier, bonus de l'Éleveur) et sur le menu G commun. Généré par `sources/datapack.py`.

## Les 6 compagnons

| Compagnon | Déblocage | Rôle | Capacités (niveaux 5, 10, 20, 30) |
|---|---|---|---|
| Loup | Chasseur 10 | Combat, mode chasse | Croc paralysant, Instinct de meute, Saignement, Alpha (renforts sous 4 cœurs) |
| Chat | Fermier 10 | Soutien, fait fuir creepers et phantoms | Ronronnement, Vision féline, Neuf vies, Porte-bonheur |
| Perroquet | Explorateur 15 | Éclaireur | Sentinelle (monstres lumineux), Plume (chute lente), Alerte creeper, Vent arrière |
| Bonhomme de neige | Pêcheur 20 | Tir à distance, ne fond plus | Givre, Cœur de glace, Blizzard, Hiver éternel |
| Allay | Enchanteur 25 | Ramassage, soin | Aimant (objets ramenés), Chant apaisant, Fortune, Ange gardien |
| Golem de fer | Mineur 30 ou Bâtisseur 30 | Tank | Rempart, Frappe sismique, Peau de fer, Titan |

Le prestige d'un métier compte comme son niveau 100. Un seul compagnon dehors à la fois.

## Progression

- Niveaux 1 à 30, XP pour le niveau suivant : 20 + 6 x niveau.
- 5 XP par monstre qu'il achève (crédit par le dernier attaquant du monstre, détecté toutes les 5 ticks), 1 XP par monstre tué par le joueur pendant qu'il est dehors, 2 XP par minute passée ensemble. +1 % par niveau d'Éleveur (+100 % au prestige).
- Chaque niveau : vie, dégâts, armure, vitesse, et taille pour le loup, le bonhomme de neige et le golem (tables `stats()` dans `datapack.py`).
- Apparences : 9 pour le loup, 11 pour le chat, 5 pour le perroquet, une nouvelle tous les 3, 2 ou 5 niveaux. Armure de loup dès le niveau 15. Renommer : objet renommé à l'enclume en main.

## Fonctionnement

- Vrais mobs du jeu. Loup, chat et perroquet sont apprivoisés (`Owner`), l'allay suit son joueur aimé, le bonhomme de neige et le golem (tag `cp.lent`) sont ramenés près du joueur au-delà de 8 blocs. Tous reviennent au-delà de 24 blocs ou d'une dimension à l'autre. Mode « Rester » : il garde la zone (assis pour loup, chat, perroquet).
- Jamais de mort : sous 20 % de sa vie il est K.O. (retour 60 s plus tard). Un compagnon introuvable (zone déchargée) revient tout seul, sauf s'il était blessé à plus de moitié (alors K.O.).
- Chaque invocation porte un numéro (`cp.ser`) : une copie restée dans une zone déchargée, celle d'un joueur déconnecté ou d'un compagnon rangé disparaît sans rien lâcher (`DeathLootTable` vide, pas de fer de golem à farmer).
- Menus : touche G, Compagnons (déclencheur `compagnons`), bandeau COMPAGNONS (n° 13, dessiné par Commerce), icônes du jeu, 3 colonnes.

## Commandes admin

| Commande | Effet |
|---|---|
| `/function compagnons:version` | Version chargée |
| `/function compagnons:admin/max` | Tous ses compagnons niveau 30 (tests) |
| `/function compagnons:admin/zero` | Retour au niveau 1 |
| `/function compagnons:desinstaller` | Retire les compagnons et les scores, puis désactiver le pack |

## Installation

`compagnons.zip` dans `world/datapacks/`, avec Métiers, Commerce et Horreur à jour (le menu G commun est le même fichier dans les quatre packs). Le resource pack commun contient le bandeau.

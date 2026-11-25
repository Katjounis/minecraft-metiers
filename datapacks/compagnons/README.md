# Compagnons

Datapack vanilla (Minecraft Java 26.x) : chaque joueur a un compagnon qui le suit, se bat avec lui et gagne ses propres niveaux. Trois d'entre eux sont des montures volantes (ghast joyeux, dragon de l'Ender, wither). Branché sur Métiers (déblocage par les niveaux de métier, bonus de l'Éleveur) et sur le menu G commun. Généré par `sources/datapack.py`.

## Les 9 compagnons

| Compagnon | Déblocage | Rôle | Capacités (niveaux 5, 10, 20, 30) |
|---|---|---|---|
| Loup | Chasseur 10 | Combat, mode chasse | Croc paralysant, Instinct de meute, Saignement, Alpha (renforts sous 4 cœurs) |
| Chat | Fermier 10 | Soutien, fait fuir creepers et phantoms | Ronronnement, Vision féline, Neuf vies, Porte-bonheur |
| Perroquet | Explorateur 15 | Éclaireur | Sentinelle (monstres lumineux), Plume (chute lente), Alerte creeper, Vent arrière |
| Bonhomme de neige | Pêcheur 20 | Tir à distance, ne fond plus | Givre, Cœur de glace, Blizzard, Hiver éternel |
| Allay | Enchanteur 25 | Ramassage, soin | Aimant (objets ramenés), Chant apaisant, Fortune, Ange gardien |
| Golem de fer | Mineur 30 ou Bâtisseur 30 | Tank | Rempart, Frappe sismique, Peau de fer, Titan |
| Ghast joyeux | Explorateur 40 | Monture volante, 4 passagers | Nuage protecteur, Rafale (+25 % de vol), Vol de nuit, Nuée |
| Dragon de l'Ender | Chasseur 50 et progrès « Libérer l'End » | Monture volante | Souffle, Écailles, Envergure (+30 % de vol), Colère du dragon |
| Wither | Chasseur 70 et un Wither invoqué ou tué | Monture volante | Crânes, Armure de Wither, Aura noire, Explosion (sans casser de blocs) |

Le prestige d'un métier compte comme son niveau 100. Un seul compagnon dehors à la fois.

## Montures

Le ghast joyeux est un vrai ghast joyeux harnaché : vol du jeu (clic droit pour monter, regarder et avancer), harnais de couleur selon l'apparence. Le dragon et le wither sont portés par un ghast joyeux invisible dont le harnais n'a pas de rendu (équipement `compagnons:vide` du resource pack, `build/compagnons_rp/`) ; le vrai boss, figé (`NoAI`, invulnérable, réduit par l'attribut `scale`), est replacé sur lui à chaque tick et tourné comme lui. La barre de boss du wither prend le nom du compagnon. Le dragon ne vole pas dans l'End (le combat du dragon du jeu pourrait le prendre pour le vrai). En descendant en plein vol : chute lente 8 s. Seul le propriétaire conduit ; des amis peuvent monter derrière lui.

## Améliorations

Trois voies par compagnon, 5 rangs chacune : Robustesse (+10 % de vie par rang), Puissance (+15 % de dégâts, +5 % de vitesse, +10 % de vol par rang), Maîtrise (capacités débloquées 2 niveaux plus tôt par rang). Un rang n coûte n points de dressage (1 par niveau du compagnon, 30 au maximum alors que tout acheter en coûte 45) et 4 000 x n Écus du Commerce.

## Progression

- Niveaux 1 à 30, XP pour le niveau suivant : base x 1,08^(niveau - 1), base 60 (120 pour le ghast, 180 pour le dragon, 200 pour le wither) : environ 6 200 XP pour le niveau 30, 18 700 pour le dragon.
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

## Version 4.2 (25/11/2026)

Le loup, le bonhomme de neige et le golem attaquent ce que leur joueur frappe : au coup porté (succès `frappe`, déclencheur `player_hurt_entity`), la victime est retrouvée et le compagnon reçoit d'elle un coup symbolique de 0,01, ce qui lance sa riposte du jeu sur elle.

## Version 4.1 (25/11/2026)

Suivi au pas : le compagnon repart quand il est à plus de 5 blocs et s'arrête à 3 (tag `cp.marche`), à vitesse de marche (0,12 bloc/tick, 0,15 pour les volants), en visant directement le joueur. Fini le point derrière le joueur et le décalage quand il passe devant : le golem tournait autour en courant.

## Version 4 (25/11/2026)

Suivi réel pour les 9 compagnons (`c/suivre`, à chaque tick) : il vise un point 3,5 blocs derrière son joueur (plus haut pour les volants), reste entre 2,5 et 6 blocs, et se décale s'il passe devant à moins de 5 blocs, pour ne pas gêner le minage. Déplacement par Motion, donc avec collisions, gravité et petit saut devant une marche. Pas de suivi s'il est monté, en mode « reste », ou en combat près du joueur. Équipe `cp.compagnons` sans collision : il ne pousse plus le joueur. Téléportation de rattrapage à 3 blocs derrière au lieu de 1,5.

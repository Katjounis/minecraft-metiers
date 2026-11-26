# Boss

Datapack pour Minecraft Java 26.x, sans mod. Deux boss de serveur modélisés et animés, chacun dans sa propre arène, qui se réveillent tout seuls toutes les 3 à 5 h de jeu, même avec un seul joueur connecté. Ils s'ajoutent aux boss de Métiers et au Croque-mitaine d'Horreur, sans jamais tomber en même temps qu'eux.

| Boss | Arène | Récompense unique (première victoire) |
|---|---|---|
| **Le Grimoire Vivant** | La Bibliothèque Interdite : sommet de tour rond de 29 blocs qui flotte dans le vide violet (dimension `boss:grimoire`) | **Grimoire familier** : petit grimoire à œil ; tenu dans la main secondaire, il donne Force II et Résistance II, avec des runes qui tournent autour du joueur |
| **Le Corbeau-Épouvantail** | Le Champ maudit : blé mort, épouvantails plantés, citrouilles, lune rouge (dimension `boss:corbeau`) | **Cape de plumes noires** : élytres redessinées qui lâchent des plumes en vol |

Pas d'arme ni d'armure, conformément à la règle du serveur. À chaque victoire, tous les inscrits gagnent aussi 15 000 Écus (Commerce), 600 XP Chasseur et 3 éclats de boss (Métiers) et 500 points d'XP. À partir de la deuxième victoire contre un même boss, l'objet unique est remplacé par 6 diamants.

## Déroulement d'un événement

1. **Réveil** : un minuteur tire un boss au hasard toutes les 3 à 5 h de jeu (le temps ne compte que si quelqu'un est connecté). Si le boss de Métiers est annoncé ou en cours, ou si le Croque-mitaine rôde, l'événement attend 5 min.
2. **Préavis de 2 min** : grand titre chez tout le monde (« La Bibliothèque Interdite s'éveille… » ou « Une lune rouge se lève… »), un son et un voile sombre, puis une fenêtre **Rejoindre / Pas cette fois**. Un message cliquable `[REJOINDRE]` revient dans le chat à 1:30, 1:00 et 0:30. Les inscrits ont un `[ME DÉSINSCRIRE]`.
3. **Départ** : les inscrits sont téléportés ensemble dans l'arène (compte à rebours 3, 2, 1). Le nombre d'inscrits fixe la difficulté : PV, nombre de pupitres à activer, nombre de corbeaux. Si personne ne s'est inscrit, le boss repart avec un message moqueur.
4. **Combat** : barre de boss, annonces en grand à chaque phase, et une ligne « Comment le vaincre » dans le chat au lancement. Les combattants passent en mode aventure (on ne casse pas l'arène). Les autres peuvent **regarder** en spectateur (`[REGARDER]` dans le chat, ou `/trigger bs.rejoindre set 3`).
5. **Fin** : victoire, ou défaite si tout le monde est K.O. ou si le combat dépasse 15 min. Chacun est ramené là où il était, dans son mode de jeu d'origine.

**On ne meurt pas dans l'arène** : à 3 cœurs, ou en tombant dans le vide, le joueur est mis K.O., soigné et renvoyé chez lui sans rien perdre. Il touche quand même la récompense si ses alliés gagnent.

Déconnexion pendant un combat : à la reconnexion, le joueur reprend le combat s'il dure encore, sinon il est renvoyé chez lui.

## Le Grimoire Vivant

Un livre ouvert en V, un œil dans la reliure, un éventail de pages à runes, quatre tentacules d'encre et un anneau de runes en orbite. Il flotte à 6 blocs en tournant autour du sceau central.

- **Pupitres de scellement** : un joueur active un pupitre en restant accroupi 4 s à côté (le trait de runes vers le centre devient de l'obsidienne pleureuse, un rayon part vers le livre). Quand assez de pupitres brillent en même temps (2 en solo, autant que de joueurs jusqu'à 4), ses chaînes le tirent au sol 7 s. Un pupitre allumé s'éteint tout seul au bout de 15 s : c'est la fenêtre pour le frapper. Le reste du temps, il faut tirer à l'arc.
- **Pages tranchantes** : 4 lignes (5 en phase 2, 6 en phase 3) brillent au sol 1,5 s, puis coupent (9 dégâts).
- **Tentacule** : le sol se gonfle sous un joueur, une tentacule en sort et s'abat (11 dégâts, une tentacule de plus en phase 2 et 3), laisse une flaque d'encre (lenteur, Wither) et éteint les pupitres proches.
- **Phase 2 (60 %)** : un pilier s'effondre, des livres maudits s'envolent des bibliothèques, rafales de runes qui visent les joueurs.
- **Phase 3 (30 %)** : le bord du plateau s'écroule bloc par bloc dans le vide, deux pupitres sont détruits.

## Le Corbeau-Épouvantail

Un épouvantail décharné de 9 blocs attaché à sa croix, tête en sac cousu aux yeux rouges, chapeau déchiré, cape de plumes et corbeaux perchés sur la traverse.

- **Fauchage** : sa tête se tord, sa croix craque, puis il tourne sur lui-même (12 dégâts à 7,5 blocs). On l'esquive en sautant ou en reculant.
- **Nuée** : sa cage de paille s'ouvre et des corbeaux s'en échappent (3 + 1 par joueur, 12 au plus).
- **Regard des épouvantails** : les yeux d'un épouvantail planté s'allument. Le joueur visé qui le regarde plus de 2 s prend Lenteur et Obscurité.
- **Phase 2 (60 %)** : toutes les 18 s, il se disperse en corbeaux qui filent vers un épouvantail. Chaque corbeau qui arrive lui rend 1/40 de sa vie : il faut les abattre en vol. En plus, la nuit ronge ceux qui s'éloignent à plus de 6 blocs d'une citrouille.
- **Phase 3 (30 %)** : il se crucifie au centre, invulnérable. Pluie de plumes (cercles au sol puis piqué de corbeaux) et charges en ligne droite annoncées par une ligne rouge. Après sa charge, il reste sonné 4 s : c'est là qu'on le frappe.

## Difficulté (version 1.1)

PV : Grimoire 500 + 250 par joueur, Corbeau 600 + 250 par joueur (au-delà de 1 000, Résistance). Attaques plus rapprochées (le Grimoire attaque toutes les 4,5 s puis 2,7 s en phase 3, le Corbeau toutes les 4,5 s puis 3,5 s), flaque d'encre sous un joueur à chaque attaque du Grimoire en phase 2, tentacule en plus à chaque attaque en phase 3, corbeaux pendant la pluie de plumes du Corbeau, nuit qui ronge plus fort (2 dégâts toutes les 2 s).

## Rang et nouveaux sorts (26/11/2026)

Le boss se cale sur le meilleur score de métiers parmi les combattants (somme des niveaux, +100 par étoile), par paliers de 50 points (rang 0 à 24), annoncé au lancement. Par rang : +15 % de PV (Résistance au-delà de 1 024, jusqu'à III), +8 % sur tous les dégâts scriptés (la règle du K.O. tient compte des dégâts réels), attaques plus rapprochées (jusqu'à -40 %), récompenses +15 % (Écus, XP de Chasseur) et +1 éclat tous les 4 rangs. Régénération dès 150 points, bouclier d'absorption à la phase 2 dès 500.

- **Grimoire, Marque d'encre** : une rune suit un joueur 2,5 s puis explose (10 dégâts à 3 blocs de lui) : il faut s'écarter de lui. **Festin de pages** (dès 300 points) : 4 dégâts à tous, le Grimoire se soigne.
- **Corbeau, Épouvante** : cri à 10 blocs (5 dégâts, Obscurité, Lenteur). **Picorage** (dès 300 points) : trois cercles sous des joueurs, les corbeaux piquent 1,5 s plus tard (8 dégâts).

Correctif : les PV du boss étaient rangés dans `#max bs.ev`, qui est aussi la borne haute de l'intervalle entre deux boss. Après un combat, l'intervalle passait à 3 à 16 h. Les PV ont maintenant leur propre score (`#pvmax`), et une borne abîmée est remise à 300 min une fois au chargement.

## Boss de Métiers redessinés

Les 5 boss de Métiers deviennent invisibles et un squelette animé les suit (repos, marche, attaque quand Métiers lance une attaque) :
- Colosse : forgeron géant en armure de plaques, cœur de forge rougeoyant, casque à cornes, marteau ;
- Reine arachnide : huit pattes articulées, gros abdomen marqué de violet, crocs, huit yeux rouges, couronne d'épines ;
- Liche du givre : crâne dans une capuche, longue robe bordée de givre, couronne de glace, bâton à cristal, éclats en orbite ;
- Brasier ancestral : tête de magma sous un masque d'obsidienne, deux anneaux de bâtons de feu qui tournent ;
- Creeper géant : pierre moussue fendue de lueurs vertes, fagot de TNT, cristal sur la tête.

## Commandes admin

| Commande | Effet |
|---|---|
| `/function boss:test_grimoire` et `boss:test_corbeau` | Lance le boss tout de suite, préavis de 8 s, tu es inscrit d'office. |
| `/function boss:forcer`, `boss:forcer_grimoire`, `boss:forcer_corbeau` | Déclenche l'événement normal (préavis de 2 min) dans une seconde. |
| `/function boss:annuler` | Annule l'événement en cours et ramène tout le monde. |
| `/function boss:prochain` | Temps de jeu avant le prochain boss. |
| `/function boss:intervalle {min:180,max:300}` | Intervalle entre deux boss, en minutes de jeu. |
| `/function boss:arret` et `boss:marche` | Coupe ou relance les événements automatiques. |
| `/function boss:desinstaller` | Retire entités et scores. Désactiver ensuite le pack. |

Un `/reload` pendant un événement l'annule proprement (tout le monde rentre). Les admins en créatif peuvent visiter les arènes (`/execute in boss:grimoire run tp @s 0 101 10`).

## Technique

- **Modèles** : chaque boss est un squelette d'os (`sources/modeles.py`), mêmes formes que les maquettes validées. Chaque os devient un `item_display` (un modèle d'objet par os, texture peinte par `sources/peintres.py`). Les os trop grands sont dessinés réduits et agrandis par leur transformation, pour rester dans la limite -16..32 des modèles.
- **Animations** : une animation est une suite de poses. Pour chaque pose, `sources/rig.py` calcule la transformation de chaque `item_display` (rotation en quaternion, translation, échelle) et le jeu interpole tout seul entre deux poses. C'est le principe d'Animated Java, en maison.
- **Hitbox** : un mob invisible porte la vie et les coups (husk de taille 3 qui flotte pour le Grimoire, zombie de taille 4,5 qui marche pour le Corbeau). Les `item_display` sont téléportés sur lui à chaque tick.
- **Arènes** : deux dimensions vides en nuit permanente (`dimension`, `dimension_type`, `worldgen/biome`), arènes reconstruites par commandes à chaque événement (`sources/arenes.py`), chunks forcés pendant l'événement seulement.
- **Sbires** : corbeaux et livres maudits sont des vex invisibles qui portent un `item_display` (deux modèles alternés pour le battement d'ailes).

## Fabrication

```
python datapacks\boss\sources\datapack.py     # build/boss_datapack, boss.zip et build/boss_rp
python labo\outils\fusion_rp.py               # verse build/boss_rp dans metiers_resourcepack.zip et affiche le SHA-1
```

Le pack ajoute deux dimensions : il faut **redémarrer** le serveur (`lab-reload.bat complet` au labo) pour qu'elles existent. Mise en prod : `lab-reload.bat complet` doit afficher « Aucune erreur. », puis commit et push du `metiers_resourcepack.zip`, et le nouveau SHA-1 dans `resource-pack-sha1` du `server.properties`.

## Version 1.1 (26/11/2026)

Textes à l'écran raccourcis, boss nettement plus durs, Grimoire familier utile (Force II et Résistance II en main secondaire, plus petit en main), boss de Métiers habillés.

## Version 1.0 (26/11/2026)

Première version. Elle n'a pas encore tourné en jeu : premier test à faire au labo avec `boss:test_grimoire` puis `boss:test_corbeau`, en regardant surtout l'orientation des modèles (le boss doit faire face au joueur), la lisibilité des attaques et l'équilibrage des PV.

# Métiers : datapack et resource pack

Datapack vanilla de métiers (Bûcheron, Fermier, Mineur, Chasseur, Pêcheur, Éleveur, Enchanteur, Explorateur, Marchand, Bâtisseur) pour notre serveur, avec niveaux jusqu'à 100, arbres de compétences, outils et armure sur 11 paliers, Forge (cristaux et éclats), skins et cadres de titre, défis du jour, de la semaine et collectifs, classement, prestige, heure du métier et 5 boss de serveur en rotation.

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
resource-pack-sha1=61ae039e7684b90429a0f2e0ccfb12bc266a1368
require-resource-pack=true
```

Le SHA-1 doit être recalculé à chaque nouvelle version du resource pack.

## En jeu

Touche G (ou menu Échap) pour ouvrir le menu des métiers, ou `/trigger metiers`.

Commandes admin : `/function metiers:boss/alerte` (boss suivant de la rotation dans 2 min), `/function metiers:heure/lancer`, `/function metiers:defis/nouveaux`, `/function metiers:defis/semaine`.

## Version 27.3 (26/11/2026)

Correctif : le message de l'arbre est plus large que le dessin (sinon la ligne passait à la ligne et le dessin se coupait en deux), et chaque panneau a assez de lignes pour toute sa hauteur (le bas du cadre était coupé).

Cadre en relief commun aux panneaux « succès » et aux arbres de compétences (`cadre_noir` dans `ref_arbre.py`) : briques de pierre noire polie biseautées, coins en pierre noire dorée avec un clou d'or, filet d'or autour du fond, ombre portée vers l'intérieur ; le fond reste en blocs mêlés. Panneaux agrandis (400 px de large, 6 px au moins entre les textes et le cadre), arbre de 260 x 190 px. Les fonds de plus de 240 px sont découpés en glyphes posés bout à bout (`fond_glyphes`).

## Version 27.2 (26/11/2026)

Les anciennes capacités de la Forge sont des compétences de l'arbre, plus des paliers d'outil : Faux (clic droit avec la houe du Fermier, récolte et replante en 3x3, f15) et Grande faux (5x5, f18), Pioche large (3x3 accroupi avec n'importe quelle pioche, m16), Tir triple (n'importe quel arc, c17), Lasso (houlette, accroupi + clic droit, e15), Parchemin (grimoire, accroupi + clic droit, n8), Bourse aimantée (bourse en main secondaire, t10). Elles remplacent Vigueur du terroir, Repas de fête, Pied de montagne, Fumigène, Peau épaisse, Remise et Guérisseur. La houe du Fermier accepte le clic droit à tous les paliers (remise à jour une fois à la connexion). L'Arc du Chasseur n'est plus donné au palier 5 (ceux déjà donnés tirent toujours en triple).

## Version 27.1 (26/11/2026)

Menus « succès » (`sources/ref_panneaux.py`) : un fond de blocs encadré et des icônes dans les cadres de l'écran des Progrès, cliquables, avec le nom et une info courte dessous. Mes métiers (les 10 métiers avec leur niveau, puis Forge, Défis, Quêtes, Armure, Sommaire, Plus), l'accueil de Commerce, le menu G, l'accueil de Compagnons et la liste du Bestiaire. Tout tient dans un seul plain_message : la ligne 0 pose le fond et les icônes, les lignes suivantes portent les libellés placés au pixel près (table des largeurs de la police du jeu dans `sources/larg_police.json`), chaque ligne fait la largeur exacte du panneau pour que le dialogue les centre toutes pareil. Les textes variables (niveau, nom caché) sont encadrés de deux espaces de rattrapage choisis selon leur longueur. Les autres packs lisent `sources/panneaux.json` avec `sources/panneaux_lib.py` : construire Métiers avant eux (ordre : Métiers, Commerce, Métiers, Compagnons, Horreur).

Arbre de la page de métier resserré (236 x 170 px) pour tenir sans défiler. Noms des branches en police normale (ils s'affichaient en carrés). Plus aucun décor ni bandeau illustré en tête des menus, dans les 4 packs.

## Version 27.0 (26/11/2026)

Arbres à 18 compétences (`sources/comp18.py`, effets dans `sources/ref_comp18.py`). Chaque métier garde ses 6 compétences en tronc, maintenant en chaîne, et gagne deux branches de 6 (gauche n° 7 à 12, droite n° 13 à 18) aux niveaux 10, 20, 30, 45, 60 et 80. Le Bâtisseur reste à 6. Coûts réels sans doublement : tronc 3, 4, 6, 8, 12, 16 ; branches 4, 6, 8, 10, 12, 14, soit 157 points pour tout l'arbre. Le niveau 100 en donne 99 et chaque étoile de prestige 99 de plus. Les points dépensés sont recalculés à chaque ouverture à partir des compétences acquises (anciens coûts doublés remboursés d'office). Déclencheurs d'achat des branches : 3000 + 20 x numéro du métier + n° de compétence.

Page de métier : l'arbre dessiné (236 x 200 px, fond en blocs mêlés propres à chaque métier, `ARB_MIX` dans `ref_arbre.py`) est seul à porter les compétences, on clique sur l'icône pour acheter ou basculer, l'infobulle donne nom, effet, coût, niveau et prérequis. Seules les compétences acquises gardent leurs couleurs. Les noms des branches sont écrits sous l'arbre. Restent dessous : Outil, Progression, Retour.

Effets : attributs (vie max, armure, portée, vitesse de casse, air, nage, minage sous l'eau, saut, recul), effets selon l'outil tenu ou le lieu, crochets sur les gains d'XP (chances de butin, `pm_N` pour une chance sur 1000), progrès `player_hurt_entity` et `entity_hurt_player` pour les coups critiques, le saignement (types de dégâts `metiers:critique` et `metiers:saignement`), l'esquive et le Tourbillon. Les compétences du Marchand côté marché sont lues par Commerce : `m.tmb` (bonus de vente en millièmes), `m.tam` (achats -5 %), `m.ttx` (taxe de l'hôtel des ventes à 2 %, retenue à la mise en vente), `m.tbq` (épargne +1 %), `m.tcb` (5 % d'achats remboursés).

Objets de métier (`sources/ref_objets.py`), achetés en Écus dans l'onglet Outil quand la compétence est acquise : Graine de forêt, Bombe d'engrais, Arrosoir, Épouvantail, Dynamite, Lanterne, Piège à mâchoires, Fumigène, Filet de pêche, Sifflet, Mangeoire, Tente. Les objets lancés sont des boules de neige suivies par un marqueur, les objets posés des porte-armures invisibles avec un marqueur jumeau qui rend l'objet quand on le casse.

Fin des objets de la Forge : la boutique disparaît (le bouton Forge ouvre le sertissage, les skins et les cadres). Le 3x3 passe sur la pioche du Mineur (palier 5, accroupi), la récolte au clic droit sur la houe du Fermier (3x3 au palier 3, 5x5 au palier 6), le lasso sur la houlette de l'Éleveur (palier 4, accroupi), le parchemin sur le grimoire de l'Enchanteur (palier 3, accroupi), l'aimant sur la bourse du Marchand en main secondaire (palier 4). L'arc triple devient la récompense du palier 5 de Chasseur, des élytres incassables celle du palier 6 d'Explorateur (récupérables dans l'onglet Outil). Les anciens objets sont retirés des inventaires et des coffres de l'Ender, une seule fois, avec le remboursement des cristaux et éclats payés.

## Version 26.5 (25/11/2026)

Récompenses de palier en grille de 10 cases (vert récupéré, jaune à prendre, gris à venir), l'outil, ses enchantements et les bonus passent dans l'infobulle ; un clic sur une case ou sur « Tout récupérer » récupère ce qui est disponible, Retour ramène à l'onglet Progression du métier. Page Synergies sur une ligne par synergie, l'effet au survol du nom.

## Version 26.4 (25/11/2026)

Décors encadrés en tête des menus principaux, dessinés dans la police `metiers:arbre` à des caractères fixes (U+E7F0 serveur, U+E7F1 Métiers, U+E7F2 Commerce, U+E7F3 Compagnons, U+E7F4 Bestiaire) pour que les autres packs les utilisent : menu Les Couillons (îles volantes, une couleur par pack), Mes métiers (forêt et falaise à minerais), accueil Commerce (étals du marché), Compagnons (prairie au couchant), Bestiaire (forêt de nuit).

## Version 26.3 (25/11/2026)

Barèmes d'XP en grille de cases sur 3 colonnes (icône, valeur, nom ; détail au survol) au lieu d'un pavé de texte centré. Les titres de section ouvrent une rangée, les explications sont dans une ligne courte en tête et dans trois cases d'aide (Bonus et malus, Prestige, Défi du jour). Le Mineur passe sur deux pages comme le Chasseur (minerais, puis pierres, déclencheur 492). Plus de décor en tête des barèmes.

## Version 26.2 (25/11/2026)

Arbre cliquable : chaque nœud du dessin porte une infobulle (nom, effet, coût, niveau, prérequis) et achète ou bascule la compétence au clic. Page de métier raccourcie : plus de décor en tête ni de légende, les 6 boutons de compétence tiennent sur 2 rangées. Mes métiers sur 3 colonnes (le Bâtisseur seul sur sa rangée, puis Forge, Défis, Quêtes, Armure, Sommaire, Plus).

## Version 26.1 (25/11/2026)

Boss sans aucun objet : plus de tables de butin tirées (minerais, reliques comme la Masse du Brasier) ni de butin vanilla du mob (`DeathLootTable` vide). Récompense : 3 éclats (+2 au meilleur dégât), 30 % d'un niveau de Chasseur, 5 000 Écus, plus une prime de 2 500 Écus par tirage (1 par niveau de difficulté, +1 au meilleur dégât) ; le bonus rare donne 2 éclats et 5 000 Écus. Les orbes d'XP du mob tombent toujours.

## Version 26.0 (25/11/2026)

Refonte des menus.

Page de métier : l'arbre de compétences est dessiné en haut (police `metiers:arbre`, `ref_arbre.py`) sur le bloc du métier, avec les cadres de l'écran des Progrès, les icônes des compétences et des liens qui s'allument quand les deux compétences sont acquises. Les nœuds ont 4 états (acquise, disponible, points manquants, niveau trop bas). Les boutons cliquables sont posés dessous dans la même forme. Le reste part dans deux onglets : Outil (récupérer, réparer, forger, skin, mode de la pioche) et Progression (récompense de palier, titre, prestige, barème, classement, capacité spéciale), déclencheurs 550 et 560 + numéro du métier.

Mes métiers : les 10 métiers sur 2 colonnes, puis Forge, Défis du jour, Quêtes, Armure, Sommaire A à Z et Plus. Plus (l'ancien Activités) regroupe Guilde, Classement, Synergies, Cadres de titre, Aura et Aide ; le barème, la Forge de l'outil et les skins sont dans les onglets de chaque métier.

Les textures du jeu utilisées pour dessiner l'arbre sont copiées dans `sources/textures_arbre/`. La police est écrite à la toute fin du build (`ref_arbre_ecrire.py`), après le nettoyage de `build/metiers_rp` par `ref_batisseur.py`.

## Version 25.14 (25/11/2026)

Page de métier : les 6 compétences posées en arbre cliquable (racine, deux branches, sommet) dans une grille de 3 colonnes avec des cases vides d'un pixel. Bouton « Sommaire A à Z » dans le menu Métiers (déclencheur 540) : tout Métiers par ordre alphabétique, métiers et classements de chaque métier compris. Une vraie recherche par texte est impossible en vanilla, un joueur non-op ne renvoyant que des nombres.

## Version 25.13 (25/11/2026)

Bouton « Classement » dans l'onglet de chaque métier (déclencheurs 521 à 530, `ref_classement.py`) : top 10 du serveur dans ce métier, trié par étoiles de prestige puis par niveau, médailles pour le podium. Les joueurs en ligne sont mis à jour à l'ouverture, les autres gardent leur dernier score connu. « Retour » ramène à l'onglet du métier.

## Version 25.12 (25/11/2026)

Boss sans récompense corrigés. Les tirs (arc, arbalète, trident) ne comptent pas dans `damage_dealt`, donc un boss abattu à distance (Brasier, Creeper géant) ne récompensait personne. Le succès `boss_touche` (déclencheur `player_hurt_entity`, projectiles compris) inscrit maintenant tout joueur qui touche le boss, avec environ 4 PV comptés par touche pour le meilleur dégât. Quand le boss disparaît, sa dernière position est testée (`execute if loaded`) : chunk chargé, il est mort, et le combat se termine en victoire si des joueurs le combattaient ; chunk déchargé, on attend jusqu'à 5 minutes (`boss/absent`).

## Version 25.11 (25/11/2026)

Le succès `boss_tue` (boss tué par un joueur, qui déclenche `boss/tue`) n'était plus généré : il est de retour, donc le tueur est toujours récompensé, même s'il n'a pas été vu frapper.

Boss : le combat se met en pause quand personne n'est connecté, et un boss hors des chunks chargés a 5 minutes de grâce avant d'être déclaré enfui. Avant, se déconnecter seul faisait « fuir » le boss alors qu'il restait dans le monde, sans barre ni récompense. Tout boss orphelin est repris dès qu'il est rechargé (`boss/adopter`) : barre remise, combat relancé, récompense à la clé.

Anti-triche : pendant 5 minutes après une mort (`m.mortr`, `m.ramas`), ramasser des cultures ou de la laine ne rapporte pas d'XP. Ce sont ses propres affaires, pas une récolte. Seules ces deux sources passent par le ramassage, les autres métiers ne pouvaient pas être farmés ainsi.

## Version 25.10 (25/11/2026)

Un boss toutes les 30 minutes au lieu de 75 (seuil `#cycle m.boss` à 3600, nouvel essai 5 minutes plus tard si personne n'est connecté). La récompense Chasseur passe d'un niveau entier à 30 % du niveau en cours (`m.c_need` x 3 / 10). Éclats, 5 000 Écus et butin inchangés.

## Version 25.9 (25/11/2026)

Correctif XP : l'anti-triche retire l'XP des blocs posés (bûches, cultures replantées, grès, netherrack...), mais la dette n'avait pas de limite. Après une grosse construction (Litematica), le solde d'un métier pouvait descendre à plusieurs milliers sous zéro, et plus rien ne rapportait d'XP tant qu'il n'était pas remboursé. La dette est maintenant plafonnée à 64 points par métier (`DETTE_MAX` dans `datapack.py`), ce qui suffit à annuler un aller-retour poser/casser. Les soldes déjà bloqués sont ramenés à -64 au premier passage, sans migration.

## Version 25 (23/11/2026)

Bâtisseur (10e métier, lettre `k`, `sources/ref_batisseur.py`) : l'XP vient des blocs de construction posés (planches, escaliers, dalles, barrières, portes et trappes des 12 bois, briques, pierres polies et taillées, béton, terre cuite, verre, quartz, prismarine...), 4 points = 1 XP ; casser un de ces blocs retire autant de points, poser puis casser ne rapporte donc rien. Les blocs bruts restent au Mineur et au Bûcheron. Ses statistiques sont relevées toutes les 3 s (170 blocs suivis). Compétences : Bras long (portée +1), Pied sûr (chute /2), Échafaudeur (chute lente accroupi dans le vide), Cadence (Célérité I), Grand chantier (portée +3 en tout), Maître d'œuvre (Célérité II, Résistance I). Outil : la Truelle, incassable, qui donne +1 à +3 de portée tenue dans une main (textures 64 px pré-rendues dans `sources/textures_batisseur/` par la forme `trowel` de `textures.py`). Kit de chantier une fois par jour de jeu (niveau 20), capacité de prestige Architecte, synergie Charpentier avec le Bûcheron, quête en 10 étapes, barème illustré. Déclencheurs propres au 10e métier : compétences 1001 à 1006, titre 620, kit 614, barème 490. Le build écrit `build/metiers_rp/` (truelle, icônes, police `icones.json` complétée) que `fusion_rp.py` verse dans le zip sans jamais retirer `assets/metiers/`.

Aussi dans la 25 (`sources/ref_v26.py`) : synergies (deux métiers au niveau 50), quêtes (10 étapes par métier), guildes (créer, inviter, défi de la semaine, classement), boss plus durs (attaque et armure selon le niveau moyen de Chasseur, phase finale, 5 nouvelles attaques), effets visuels de montée de niveau et de palier, bandeaux en tête des menus. La touche G ouvre le menu commun aux trois packs (dialogue `serveur:menu`, identique dans Métiers, Commerce et Horreur).

## Mise à jour 24.1 (23/11/2026)

Boss : butin refait (2 tirages par niveau de difficulté, +1 au plus gros dégât, livres enchantés au niveau 30 (plus aucun outil, arme ni armure depuis la 25.8, les métiers les donnent déjà), débris antiques, minerais en blocs, disques), butin rare à 15 % par niveau de difficulté (+15 % au plus gros dégât) avec une relique propre à chaque boss (Hache du Colosse, Arc de la Reine, Trident du givre, Masse du Brasier, Arbalète du Creeper ; le Plastron du Brasier a été remplacé en 25.8, inutile à côté de l'Armure des Guildes). Les reliques portent `custom_data {metiers_relique:1b}` et se vendent 15 000 Écus au Commerce (catégorie Butin de boss, bouton « Vendre la relique en main », anciennes reliques reconnues par leur nom) ; le butin courant se vend dans la même catégorie. Corrections : le boss apparaît à 4 à 12 blocs du joueur, à sa hauteur, sur un sol avec 6 blocs d'air (avant, à la surface au-dessus d'un joueur en grotte ou sur le toit du Nether) ; PV plafonnés à 1 000 (le jeu bloque à 1 024, la barre de boss ne partait plus pleine à 4 joueurs et plus) et Résistance pour les gros groupes ; bond et clignement seulement vers un endroit libre (le boss restait coincé dans les murs) ; beau temps pendant le Brasier (la pluie lui retirait des PV).

Forge : un objet forgé (marteau, faux, arc triple, lasso, parchemin, aimant, cape) se récupère gratuitement dans la boutique s'il est perdu, comme les outils de métier : il ne doit être ni sur le joueur ni dans son coffre de l'Ender, une fois toutes les 10 minutes. Un joueur qui a déjà l'objet sur lui est noté comme propriétaire automatiquement ; pour un objet perdu avant la mise à jour, voir `admin/forge_<objet>` dans le guide admin.

Barème d'XP : touche G, « Barème d’XP » (ou le bouton en haut de la page d'un métier). Une page par métier, ce que rapporte chaque action avec les images du jeu (œufs d'apparition pour les créatures, textures des blocs et des objets). Les valeurs sont lues dans les tables de `datapack.py`, le barème suit si un poids change (`sources/ref_bareme.py`).

## Prestige (24.2, 23/11/2026)

Décors (25.8) : la page de chaque métier, ses récompenses et son barème s'ouvrent sur un décor propre au métier (blocs du métier en fond, nom en grosses lettres, outil de chaque côté), dessiné par Commerce (`SCENES`) et posé par `sources/ref_scenes.py` ; il faut le resource pack commun à jour.

Récompenses de palier (tous les 10 niveaux, 25.8) : l'outil évolue, plus des cristaux du métier (5, 10, 15, 20, 30, 45, 65, 90, 120, 160), des Écus à chaque palier (500 au palier 10 jusqu'à 75 000 au palier 100), des éclats de boss dès le niveau 40 (1, 1, 2, 3, 4, 5, 8) et des objets bonus propres au métier (`EXTRAS` dans `sources/datapack.py`). Les paliers déjà récupérés avant la 25.8 reçoivent une fois la différence de cristaux, d'éclats et d'Écus (`sources/ref_paliers.py`).

Au niveau 100 d'un métier, le prestige remet le niveau à 1 mais garde les compétences, et la progression continue : le niveau suivant demande 150 x 1,06^(niveau - 1) XP, et au moins 15 000 x étoiles (courbe exponentielle depuis la 25.3, durcie en 25.4, prestige assoupli en 25.5 : environ 1,7 million d'XP pour une étoile complète ; en 25.7, chaque joueur est recalculé une fois à la connexion sur cette courbe à partir de toute l'XP déjà gagnée, voir `sources/ref_recalcul.py`), donc le niveau 1 d'une étoile demande plus que le niveau 100 d'avant. Les points de compétence des niveaux passés restent acquis et toutes les compétences restent achetables. Chaque étoile n donne 100 x n cristaux du métier, 2 x n éclats de boss et 5 000 x n Écus (score `c.ecus` de Commerce), l'outil regagne ses étoiles dorées et un reflet, une annonce et un feu d'artifice. Une capacité de prestige par métier, débloquée à 1 étoile et renforcée à 3 et 5 (`sources/ref_prestige.py`, tags `metiers.sk.p<métier><1|3|5>`) : Sève dorée, Moisson, Filon, Exécution, Appât, Jumeaux, Érudit, Pas léger, Négociant. Aura de particules (bouton dans le menu G pour la couper) et cadre de titre Étoilé à 5 étoiles dans un métier.

## Interface « Forge »

Le resource pack recolore toute l'interface vanilla (inventaire, conteneurs, barre d'action, info-bulles, curseurs, boutons) au style de la Forge. Script : `sources/resourcepack/interface_forge.py <textures gui vanilla 26.x> metiers_resourcepack.zip`, puis `sources/resourcepack/correctifs_rp.py metiers_resourcepack.zip`.

## Sac à dos

Le sac s'ouvre en un clic droit : tant qu'il est tenu en main, une barque à coffre en bambou invisible (texture vidée par le resource pack) suit les yeux du joueur. Contrepartie : les vraies barques à coffre en bambou sont invisibles sur le serveur.

# Horreur

Datapack pour Minecraft Java 26.x, sans mod. La nuit, des créatures de la pop-culture apparaissent rarement autour des joueurs. Un **bestiaire** se débloque en les tuant.

Inspiration : *Spooky Scary Creatures*. Aucun asset n'en est repris : textures et modèles sont générés par `sources/resourcepack.py`.


## Modèles animés (26/11/2026)

Toutes les créatures sont maintenant des squelettes d'item_display articulés (`sources/rigs.py`, moteur du pack Boss), passagers de leur mob invisible, avec trois animations : repos, marche (quand le mob se déplace) et attaque (quand il te frappe). SlenderMan a six tentacules dans le dos, Siren Head ses deux sirènes qui cherchent, le Loup-garou un museau et une queue, Pinhead ses épingles et ses chaînes, la Nonne et la Dame blanche glissent, le Clown tient son ballon, le Croque-mitaine porte cape, cornes et sac. Les trophées et les fiches du bestiaire montrent la tête en 3D de la créature (`sources/tetes.py`), ce qui corrige SlenderMan affiché couché. Le pack Boss doit être présent dans le dépôt pour fabriquer Horreur (il fournit `rig.py` et `peintres.py`).

## Sorts, rang et Croque-mitaine sans objet (26/11/2026)

**Rang.** Chaque créature se cale sur le score de métiers (somme des niveaux, +100 par étoile, score `m.total` du pack Métiers) du joueur près de qui elle apparaît, par paliers de 50 points (rang 0 à 24). Par rang : +15 % de vie, +8 % de dégâts (coups et sorts), +1 d'armure (30 au plus), +0,5 de robustesse, sorts plus rapprochés (deux fois plus à 1 000 points). La prime en Écus et l'XP de Chasseur suivent : +15 % par rang. Les valeurs du tableau ci-dessous sont celles du rang 0. Sans Métiers, tout reste au rang 0.

**Sorts.** Chaque créature a trois sorts (le 2e dès 100 points, le 3e dès 300), lancés quand un joueur est à moins de 24 blocs. SlenderMan, Herobrine et la Dame blanche n'en lancent qu'une fois réveillés. Les sorts de zone (foudre d'Herobrine, ballons du Clown, crochets de Pinhead, éboulis du Rôdeur, cauchemar du Croque-mitaine) font briller un cercle au sol avant de frapper : on a le temps de sortir. Liste complète dans `SORTS` (`sources/creatures.py`) et sur chaque fiche du bestiaire.

**Ensorcellements** gagnés avec le rang : Chair maudite (régénération, 150 points), Ronces (une fois sur trois, renvoie une partie des coups, 300), Vampirisme (se soigne en frappant, 500), Aura de terreur (ronge à 4 blocs, 700), Furie (s'enrage sous 30 %, 900).

**Croque-mitaine.** Sept sorts (Cage de terreur dès 200 points, Dévoreur d'âmes dès 400), enragé à 50 % de sa vie, nuit totale et quatre ombres à 25 %. Le rang et ses PV sont annoncés à sa sortie. Il ne donne plus aucun objet (ni butin, ni butin doublé de la Nuit de sang, ni trophée) : tous les joueurs à 48 blocs du coup final gagnent 10 cristaux dans chacun des 10 métiers (x rang), 300 points d'XP, la prime en Écus et l'XP de Chasseur ; 25 cristaux de chaque métier à 10 victoires à la place du trophée.

Fichiers : `sources/sorts.py` (rang, sorts, zones, récompense du Croque-mitaine), réglages dans `sources/creatures.py` (`SORTS`, `SORT_CD`, `ENSORCELLEMENTS`, `PALIER_RANG`).

## Créatures

| Créature | Où, quand | Ce qu'elle fait |
|---|---|---|
| **SlenderMan** | Surface la nuit, surtout forêts et taïgas | Silhouette immobile au loin. Il se rapproche quand on ne le regarde pas. Le fixer donne obscurité puis nausée ; ensuite il disparaît, ou il se réveille et attaque. |
| **Herobrine** | Surface, la nuit | Observe de loin et s'évanouit quand on approche. Une fois sur quatre, il surgit dans le dos du joueur et se bat. |
| **Siren Head** | Surface la nuit, surtout plaines, prairies, savanes (rare) | Géant de 8 m décharné, deux sirènes sur un mât. Accélère quand on le fuit, écrase tout à 6 blocs autour de lui toutes les 2 s (14 dégâts, recul, nausée). |
| **La Nonne** | Sous terre, sous la couche 62 | Apparaît dans le dos du joueur. Ses coups aveuglent et affaiblissent. |
| **Le Clown** | Sous terre, sous la couche 62 | On entend son rire. Ses coups ralentissent. À sa mort, son ballon rouge s'envole. |
| **Pinhead** | Nether, ou en surface la nuit (rare) | Ses chaînes attirent et ralentissent. Sous la moitié de sa vie, il appelle deux cénobites. |
| **La Dame blanche** | Surface la nuit, surtout au bord des chemins | Immobile au loin. Si on approche, elle hurle et éteint la vue, puis s'évanouit ou fond sur toi. |
| **Le Loup-garou** | Surface, les nuits de pleine lune | Rapide, hurle avant de charger, ses morsures font saigner (Wither). |
| **Le Feu follet** | Marais et mangroves, la nuit | Flamme bleue volante (vex), traverse les murs, s'enfuit quand on la suit, son contact glace. |
| **Le Rôdeur des grottes** | Sous terre | Disparaît dès qu'on le regarde et réapparaît dans le dos du joueur. |
| **Le Croque-mitaine** (boss) | Seulement pendant une Nuit de sang, vers minuit | 800 PV, barre de boss, se téléporte dans le dos, appelle des ombres, éteint la lumière. |

Le pack est « effrayant mais équitable » : aucun bloc n'est cassé ni modifié.

Chaque créature est un mob vanilla **invisible** (zombie ou husk) qui fournit l'IA et la vie. Son apparence vient du resource pack :
- les humanoïdes portent un **habit** (équipement texturé, membres animés) ;
- Slender, Siren Head et le ballon sont des **statues** (`item_display` passager du mob).

## Apparitions

Réglages du 23/11/2026 (Samuel) : environ une rencontre par nuit et par joueur en surface (4,8 % par tirage, 7,8 % en forêt, 6,8 % en plaine), une toutes les 20 min environ sous terre (5 %). Plus de condition de lumière sous terre (une torche n'empêche plus rien), Nonne dès la couche 62, Pinhead toute la nuit. Les nouvelles chances remplacent une fois les anciennes au chargement (`#ver hr.cfg`). Un message discret « Quelque chose rôde près d'ici... » prévient les joueurs à 64 blocs. SlenderMan et Herobrine : le regard est détecté par un rayon depuis les yeux (le prédicat `looking_at` ne voyait pas la statue), SlenderMan fait face au joueur, et les téléportations le tournent vers lui. Butin corrigé au format 26.x (`modifier` et `type` : avec `functions`, aucune créature ne lâchait rien) et enrichi, avec une chance sur 4 d'un objet rare.

- Un tirage toutes les 30 s par joueur, s'il est dans le bon lieu. Les chances sont exprimées pour mille.
- Il n'y a qu'une créature à la fois dans un rayon de 128 blocs, et 10 min d'attente par joueur entre deux apparitions.
- Une créature sans joueur à moins de 20 blocs disparaît au bout de 2 min. Toutes disparaissent après 15 min. Les créatures nocturnes s'évanouissent au lever du jour.

## Nuit de sang, primes, contrats (23/11/2026)

- **Nuit de sang** : une nuit sur huit, annoncée à tout le serveur. Créatures 4 fois plus fréquentes, 3 min d'attente au lieu de 10, butin doublé, pluie de particules rouges, et le Croque-mitaine sort vers minuit près d'un joueur au hasard. Admin : `/function horreur:sang`.
- **Primes en Écus** (pack Commerce) à chaque victoire, de 200 (Feu follet) à 10 000 (Croque-mitaine) depuis le 24/11/2026, +25 % dès 10 victoires sur la créature, +50 % dès 50, +100 % dès 100, et doublées pendant la Nuit de sang ; le bouton « Vendre mes trophées » du bestiaire les rachète 5 fois la prime.
- **Contrat de chasse** : chaque semaine de jeu (2 h 48 avec des joueurs connectés), une créature recherchée ; la première victoire de chaque joueur paie 5 fois la prime.
- **Classement** des victoires dans le bestiaire (pseudos lus dans le registre du pack Commerce).

## Bestiaire

- **Ouvrir le bestiaire** : touche **G** (à côté de Métiers), le menu **Échap**, ou `/trigger bestiaire`.
- **Avant le premier kill**, la créature affiche « ??? » et un indice sur son habitat.
- **Paliers** :
  - 1 kill : la fiche se débloque, avec de l'XP ;
  - 10 kills : un **trophée** (tête décorative, se porte sur la tête) ;
  - 50 kills : un **titre**, annoncé à tout le serveur ;
  - 100 kills : une prime de 5 000 Écus (plus d'arme ni d'armure depuis le 26/11/2026).
- **Bestiaire complet** (les 10 créatures hors boss) : titre « Chasseur de mythes », 20 000 Écus.
- Chaque fiche montre la créature, sa vie, ses dégâts, son XP et sa prime.

## XP Chasseur (avec Métiers)

Si le pack Métiers est installé, chaque kill rapporte de l'XP au métier **Chasseur**. Le réglage se fait avec le champ `xp` de `sources/creatures.py`, qui donne l'XP totale par kill :

| SlenderMan | Herobrine | Siren Head | La Nonne | Le Clown | Pinhead |
|---|---|---|---|---|---|
| 40 | 30 | 80 | 25 | 25 | 60 |

- Métiers compte déjà 3 XP pour le zombie ou le husk de base. Le pack Horreur ajoute seulement la différence.
- Le bonus de prestige et l'heure double de Métiers s'appliquent.
- Un joueur AFK ne gagne rien.
- Sans Métiers, le pack se charge normalement, sans XP.

## Commandes admin

| Commande | Effet |
|---|---|
| `/function horreur:invoquer {c:"slender"}` | Fait apparaître une créature à 4 blocs devant soi : `slender`, `herobrine`, `siren`, `nonne`, `clown` ou `pinhead`. Les créatures nocturnes disparaissent si on les invoque de jour. |
| `/scoreboard players set #ch_<id> hr.cfg <n>` | Change la chance d'apparition (pour mille). |
| `/scoreboard players set #cd hr.cfg <s>` | Change l'attente entre deux apparitions, en secondes (600 par défaut). |
| `/function horreur:config/debug` | Mode test : apparitions très fréquentes, sans attente. |
| `/function horreur:config/defaut` | Remet tous les réglages par défaut. |
| `/function horreur:config/arret` et `horreur:config/marche` | Coupe ou relance les apparitions. |
| `/function horreur:desinstaller` | Retire les créatures et les scores. Désactiver ensuite le pack. |

## Sons

Les sons sont dans le resource pack, sous `horreur:<créature>.<son>`, avec des sous-titres en français et en anglais.

- **Synthétisés par `sources/sons.py`** (100 % maison, voix faites d'une source glottale filtrée en formants) :
  - Slender : grésillement quand on le fixe, présence, cri de réveil ;
  - Siren Head : sirène et radio brouillée ;
  - Pinhead : chaînes et glas ;
  - Herobrine : souffle à l'apparition ;
  - Clown : rire hystérique sur une boîte à musique faussée ;
  - Nonne : prière chuchotée sur un chœur lointain ;
  - Dame blanche : plainte coupée de sanglots ;
  - Loup-garou : hurlement, un second loup répond au loin ;
  - Feu follet : sifflement, crépitements, carillon ;
  - Rôdeur : pas lourds dans les feuilles puis une respiration ;
  - Croque-mitaine : grondement très grave.
- **Remplacement à la main** : un fichier `datapacks/horreur/sons/<nom>.wav` (ou MP3, OGG, FLAC) du même nom passe avant la synthèse.

Pour encoder en OGG Vorbis, il faut **ffmpeg** (`winget install Gyan.FFmpeg`). Sans lui, le pack se construit quand même, mais avec les sons vanilla. Pour écouter les sons synthétisés avant de les intégrer, lancer `python sources\sons.py` : il écrit les WAV dans `build/sons_wav/`.

## Animations et textures (23/11/2026)

Les statues bougent : Slender oscille et respire, la tête de Siren Head cherche à gauche et à droite, le Feu follet flotte et tourne. Quatre poses par cycle de 4 s, le jeu interpole entre elles (`POSES` dans `datapack.py`, fonctions `vis/anim_0..3`). Les habits sont redessinés en 128x64 (fonction `hd` de `resourcepack.py`) : dégradé de lumière sur chaque face, ombre au bord des faces, contours adoucis vers les détails sombres. Le bestiaire a son bandeau en tête (police `commerce:recette`, dessiné par Commerce).

## Fabrication

```
python datapacks\horreur\sources\datapack.py     # build/horreur_datapack, horreur.zip et build/horreur_rp
python labo\outils\fusion_rp.py                  # verse build/horreur_rp dans metiers_resourcepack.zip et affiche le SHA-1
```

| Fichier | Rôle |
|---|---|
| `sources/creatures.py` | Stats, lieux, chances, butin et textes du bestiaire. C'est le seul fichier à modifier pour équilibrer. |
| `sources/datapack.py` | Fonctions, prédicats, progrès, dialogues. |
| `sources/resourcepack.py` | Textures (pixel art généré) et modèles. Utilise `png.py`, un écrivain PNG en Python pur. |

**Mise en prod** : `lab-reload.bat complet` doit afficher « Aucune erreur. ». Ensuite :
1. commiter et pousser `metiers_resourcepack.zip` ;
2. **dans la foulée**, recopier le nouveau SHA-1 dans `resource-pack-sha1` du `server.properties` de la prod ;
3. lancer `labo\lab-deploy.bat horreur`.

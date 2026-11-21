# Horreur

Datapack pour Minecraft Java 26.x, sans mod. La nuit, des créatures de la pop-culture apparaissent rarement autour des joueurs. Un **bestiaire** se débloque en les tuant.

Inspiration : *Spooky Scary Creatures*. Aucun asset n'en est repris : textures et modèles sont générés par `sources/resourcepack.py`.

## Créatures

| Créature | Où, quand | Ce qu'elle fait |
|---|---|---|
| **SlenderMan** | Forêts et taïgas, la nuit | Silhouette immobile au loin. Il se rapproche quand on ne le regarde pas. Le fixer donne obscurité puis nausée ; ensuite il disparaît, ou il se réveille et attaque. |
| **Herobrine** | Surface, la nuit | Observe de loin et s'évanouit quand on approche. Une fois sur quatre, il surgit dans le dos du joueur et se bat. |
| **Siren Head** | Plaines, prairies, savanes, la nuit (très rare) | Géant de 8 m, lent. Ses sirènes s'entendent de très loin. |
| **La Nonne** | Grottes sous la couche 40, dans le noir | Apparaît dans le dos du joueur. Ses coups aveuglent et affaiblissent. |
| **Le Clown** | Sous terre, dans le noir | On entend son rire. Ses coups ralentissent. À sa mort, son ballon rouge s'envole. |
| **Pinhead** | Nether, ou en surface vers minuit (très rare) | Ses chaînes attirent et ralentissent. Sous la moitié de sa vie, il appelle deux cénobites. |

Le pack est « effrayant mais équitable » : aucun bloc n'est cassé ni modifié.

Chaque créature est un mob vanilla **invisible** (zombie ou husk) qui fournit l'IA et la vie. Son apparence vient du resource pack :
- les humanoïdes portent un **habit** (équipement texturé, membres animés) ;
- Slender, Siren Head et le ballon sont des **statues** (`item_display` passager du mob).

## Apparitions

- Un tirage toutes les 30 s par joueur, s'il est dans le bon lieu. Les chances sont exprimées pour mille.
- Il n'y a qu'une créature à la fois dans un rayon de 128 blocs, et 10 min d'attente par joueur entre deux apparitions.
- Une créature sans joueur à moins de 20 blocs disparaît au bout de 2 min. Toutes disparaissent après 15 min. Les créatures nocturnes s'évanouissent au lever du jour.

## Bestiaire

- **Ouvrir le bestiaire** : touche **G** (à côté de Métiers), le menu **Échap**, ou `/trigger bestiaire`.
- **Avant le premier kill**, la créature affiche « ??? » et un indice sur son habitat.
- **Paliers** :
  - 1 kill : la fiche se débloque, avec de l'XP ;
  - 10 kills : un **trophée** (tête décorative, se porte sur la tête) ;
  - 50 kills : un **titre**, annoncé à tout le serveur.

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

- **Synthétisés par `sources/sons.py`** (100 % maison) :
  - Slender : grésillement quand on le fixe, présence, cri de réveil ;
  - Siren Head : sirène et radio brouillée ;
  - Pinhead : chaînes et glas ;
  - Herobrine : souffle à l'apparition.
- **Fournis à la main** dans `datapacks/horreur/sons/` (WAV, MP3, OGG ou FLAC, libres de droits) :
  - `clown_rire` pour le rire du Clown ;
  - `nonne_murmure` pour le murmure de la Nonne.

  Tant qu'un de ces deux fichiers manque, la créature garde un son vanilla.

Pour encoder en OGG Vorbis, il faut **ffmpeg** (`winget install Gyan.FFmpeg`). Sans lui, le pack se construit quand même, mais avec les sons vanilla. Pour écouter les sons synthétisés avant de les intégrer, lancer `python sources\sons.py` : il écrit les WAV dans `build/sons_wav/`.

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

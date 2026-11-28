# Industrie

Datapack pour Minecraft Java 26.x, sans mod. C'est le tycoon de fin de jeu du serveur. Chaque joueur reçoit une île dans l'Archipel des usines (dimension `industrie:archipel`). Il y pose des machines, les relie au Nexus par des tubes à faisceau, transforme sa production et la vend par la Halle du Marché. Il monte ainsi d'Atelier à Empire.

Le pack dépend de **Métiers** (identifiant `m.id`, niveaux de métier, éclats `m.ecl`, boss vaincus `m.bk1` à `m.bk5`, `m.kdragon`) et de **Commerce** (solde `c.ecus`, registre des noms, spawners).

Le plan complet et la simulation d'équilibre sont dans le document « Industrie » (Claude Docs). Tous les chiffres sont réunis dans `sources/tables.py`.

## Pour jouer

Ouvrir le menu avec la touche G puis le bouton **Industrie**, ou avec `/trigger industrie set 1`. Le premier passage crée l'île : la parcelle centrale, le Nexus, l'Échoppe et une Carrière automatique déjà en marche. Un clic droit sur une machine ouvre sa fiche (amélioration, revente). Un clic droit sur un bâtiment ouvre son menu.

| Menu | Rôle |
|---|---|
| Mon industrie | Recettes du jour, réputation, énergie, stock du Nexus, évènement de la Bourse |
| Comptoir des machines | 17 machines. L'achat se pose sur l'emplacement libre le plus proche (dalle noire à coins dorés) |
| Cadastre | Grille de 7 x 7 parcelles de 32 x 32 blocs. Une nouvelle parcelle doit toucher une parcelle déjà possédée |
| Halle du Marché | Niveau de la Halle, contrats du jour, agrandissement |
| Banque | Ordre de vente par produit (vendre, garder, plancher, étaler, réserver), retraits, prêts |
| Laboratoire | 4 branches de brevets, 10 niveaux chacune |
| Bureau de l'île | Passage de rang, Grands Œuvres, changement de tous les tubes |
| Parts d'île | Vendre, acheter et racheter des parts (dividende de 2 % par jour) |

## Fonctionnement

- **Production virtuelle.**
  - Les objets ne sont jamais des entités : ce sont des scores du joueur (`i.s_<produit>`).
  - La production se calcule chaque minute quand le joueur est connecté. À son retour, elle se rattrape d'un bloc, sur 8 h au plus (jusqu'à 12 h avec les brevets Logistique).
  - Les achats, améliorations et reventes tiennent à jour des sommes : `i.q_<machine>` (niveaux en %), `i.n_<machine>` (nombre), `i.k_<machine>` (consommation) et `i.qs<k>` (usines à spawner, par créature). Les entités ne servent qu'à l'affichage et au clic.
- **Énergie.** Le Nexus fournit 60 kW, la chaudière 150 kW (elle brûle du charbon), la centrale à lave 600 kW et le Cœur stellaire 3 000 kW. Si l'île manque d'énergie, toute la production baisse au prorata.
- **Tubes.** Chaque machine est reliée au Nexus par un tube en L à y = 73 : verre teinté, cœur lumineux et un objet qui glisse.
  - Le palier de tube fixe le débit par machine : cuivre 500, or 2 500, cristal 10 000 objets par minute.
- **Ateliers.** Fonderie, distillerie, atelier mécanique, joaillerie et forge des reliques consomment le stock du Nexus et y renvoient leur produit.
- **Usine à spawner.**
  - On tient en main un spawner acheté au Commerce, et l'usine le prend.
  - Elle tue 240 créatures par heure au niveau 1, +25 % par niveau de vitesse et de quantité du spawner, et produit leur butin moyen.
  - Revendue, elle rend le spawner.
- **Halle et prix dégressif.**
  - La Halle vend en continu, dans l'ordre de valeur des produits, dans la limite de son débit.
  - Le N-ième objet d'un produit vendu dans les 24 h rapporte prix de base x S / (S + N). La fenêtre se détend de 1/24 par heure.
  - Les prix de base valent le double de ceux du Commerce : la Bourse paie le gros volume.
  - Commission de 12 % à 2 % selon le niveau de la Halle (2 points de moins dès Marchand 50).
- **Entretien de l'empire.** Au-delà de 5 M d'Écus de recettes nettes dans la journée, 25 % sont prélevés. Au-delà de 12 M, 45 %.
- **Rangs.** Chaque rang demande de la réputation (1 point par 250 Écus vendus, plus 200 x le rang par contrat), des contrats livrés, des Écus et des éclats. Il faut aussi des victoires : un boss de Métiers pour Industrie, 3 Wither pour Consortium (comptés depuis l'installation), l'Ender Dragon pour Empire.
- **Retraits.** 64 objets par produit et par jour sont gratuits. Au-delà, chaque objet coûte 4 fois le prix du Commerce. Les objets sortis portent `custom_data {industrie:1b}`, que le filtre du Commerce refuse au rachat.
- **Protection.**
  - Dans l'Archipel, on passe en mode aventure hors de ses propres parcelles, et une chute dans le vide ramène sur son île.
  - Rien n'est jamais cassé : les parcelles et les bâtiments sont posés dans le vide (zone forcée chargée quelques ticks, puis libérée).
- **Journal des Écus.** Tous les gains et dépenses passent par `c.a_ind` (voir Commerce, journal des Écus).

## Fichiers

| Fichier | Contenu |
|---|---|
| `sources/tables.py` | Produits, machines, niveaux, Halle, tubes, rangs, prêts, brevets, Grands Œuvres |
| `sources/datapack.py` | Générateur : scores, horloges, production, ventes, encaissement, heure et jour |
| `sources/ile.py` | Îles, parcelles, chantier, bâtiments, voyage, protection |
| `sources/machines.py` | Achat, pose, tubes, fiche, amélioration, revente |
| `sources/economie.py` | Parcelles, contrats, Banque, prêts, Halle, Laboratoire, rangs, Grands Œuvres, parts, évènements |
| `sources/menus.py` | Aiguillage du déclencheur et dialogues |
| `sources/guide.py` | Parcours de départ et pages du guide |
| `sources/cine.py` | Présentation à l'arrivée et page « Que faire ? » |
| `sources/voxels.py`, `sources/modeles.py` | Bâtiments en voxels et export en modèles d'objet (resource pack, `build/industrie_rp`) |
| `sources/verifier.py` | Contrôle statique du pack généré |

Pour générer : `python sources/datapack.py`, puis `python labo/outils/fusion_rp.py` pour verser les modèles dans `metiers_resourcepack.zip`. L'ajout de la dimension demande un redémarrage complet du serveur (`lab-reload.bat complet`).

## Commandes admin

| Commande | Effet |
|---|---|
| `/function industrie:version` | Version du pack |
| `/function industrie:evenement/nouveau` | Tire un nouvel évènement de marché |
| `/scoreboard players set <joueur> i.rang <1-5>` | Change le rang d'un joueur (test) |

## Versions

- v8 (28/11/2026) : menus simplifiés (Mon industrie : 4 boutons, le reste dans « Autres menus », un seul bouton Retour partout, Halle sans boutons inutiles, Comptoir limité au rang suivant). Clics réparés hors de l'emplacement de spawn (portail de retour, fiches). Tubes refaits en item_display à y = 69, reconstruits sur les îles existantes. Étiquettes et titres plus petits.
- v7 (28/11/2026) : présentation à la première arrivée (titres et bâtiments mis en lumière, 30 s), page « Que faire ? » (objectif, rang actuel, ce que le prochain rang demande et débloque), machines et bâtiments bloqués marqués dans le Comptoir et Mon industrie. Réparations : le Nexus portait le code de la Halle (même étiquette, et le clic ouvrait la Halle), blocs du portail de retour effacés par le chantier.
- v6 (28/11/2026) : étiquette au-dessus de chaque machine et bâtiment (nom, rôle, « clic droit »), posée aussi sur les îles déjà construites. À l'arrivée, un titre montre le Nexus comme point de départ.
- v5 (28/11/2026) : parcours de départ en 6 étapes (objectif en bas de l'écran sur l'île, Écus à chaque étape), Guide en pages courtes (démarche, Nexus, machines, Halle et contrats, rangs), menus allégés. Les contrats demandent 1/8 de la saturation au lieu de la moitié, et la Halle met de côté leur quantité au lieu de tout vendre.
- v4 (28/11/2026) : modèles 3D refaits au format que le jeu accepte partout (un seul axe de rotation, angles par crans de 22,5 degrés, coordonnées dans la boîte -16 à 32). Avant, la plupart s'affichaient en cube violet et noir. Halle réécrite : ce qu'est un contrat, ce que tu as au Nexus pour chacun (vert si livrable, rouge sinon), le rang qui débloque les contrats 2 et 3. Métiers reconstruit : il embarquait encore l'ancien menu G à 7 cases.
- v3 (27/11/2026, nuit) : modèles 3D de la serre de cultures et de l'usine à spawner (elles s'affichaient en cube violet et noir), barrières invisibles dans l'emprise des machines et des bâtiments pour ne plus passer au travers (reposées toutes les 5 s, retirées à la revente), dialogues resserrés (Halle, Comptoir). Le menu G revient à l'état d'avant : Industrie est le bouton sous le panneau.
- v2 (27/11/2026, soir) : clic droit sur les machines et les bâtiments réparé (les données d'interaction étaient effacées avant de lire le joueur), portail « Retour au monde normal » à côté du point d'arrivée, textures qui clignotaient corrigées (faces confondues dans les modèles), Industrie dans le panneau du menu G.
- v1 (27/11/2026) : première version.
  - Îles, parcelles et 17 machines, dont la serre de cultures et l'usine à spawner.
  - Tubes à faisceau, Nexus, Halle du Marché à prix dégressif.
  - Banque : ordres par produit, retraits, prêts.
  - Laboratoire, rangs, contrats, Grands Œuvres, parts d'île, évènements de marché.
  - Modèles 3D des 21 bâtiments.
  - Pas encore faits : consortiums, saisons, caravanes d'export.

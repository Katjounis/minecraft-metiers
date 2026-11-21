# Labo de datapacks

Le labo est un serveur local pour tester les datapacks avant de les mettre en prod.

- Adresse en jeu : `localhost:25566`. Elle n'est accessible que depuis ce PC.
- RCON : port 25576, mot de passe `test`.
- Le resource pack est proposé au joueur, sans être obligatoire.

## Installation (une fois par PC)

1. Copier `local.exemple.cmd` en `local.cmd`, puis adapter les chemins :
   - `LABO_JAVA` : Java 25 ou plus récent.
   - `LABO_PROD` : dossier du serveur de prod, s'il est sur ce PC.
   - `LABO_PACKS_EXTERNES` : packs développés hors du dépôt.

   `local.cmd` n'est pas versionné.
2. Lancer `installer.bat`. Il crée `labo\serveur\` (non versionné) :
   - il copie `server.jar`, `ops.json` et `usercache.json` depuis la prod ;
   - il prend `server.properties` dans `modele\` ;
   - il récupère le monde de la dernière sauvegarde de la prod ;
   - il crée les jonctions vers les packs.

   Pour récupérer un ancien labo, lancer `installer.bat D:\Servers\lab` à la place. Il déplace le monde et les réglages de cet ancien labo.

## Organisation

| Emplacement | Rôle |
|---|---|
| `datapacks\<nom>\` | Sources des packs. Pour Métiers, on modifie `sources\*.py`, jamais le zip. |
| `labo\serveur\` | Le serveur de test : `server.jar`, monde, logs. |
| `labo\serveur\world\datapacks\<nom>` | **Jonctions** vers les sources de chaque pack. Le labo lit directement ce qu'on modifie, sans passer par un zip. |

## Boucle de travail

1. `lab-start.bat` démarre le labo dans sa propre fenêtre. Le serveur redémarre tout seul après un `stop`.
2. Modifier les sources d'un pack.
3. `lab-reload.bat` régénère les packs générés par script, fait un `/reload` et **affiche les erreurs du log**.
   - `lab-reload.bat complet` redémarre le serveur. C'est obligatoire si un menu (dialogue, touche G), un progrès, un tag ou un autre fichier de registre a changé.
4. Tester en jeu, ou sans lancer le jeu avec `lab-cmd.bat "commande 1" "commande 2"`.

Une seule erreur dans un fichier de registre fait échouer **tout** le chargement. Il faut obtenir « Aucune erreur. » avant de passer en prod.

## Autres scripts

| Script | Effet |
|---|---|
| `lab-stop.bat` | Arrête le serveur. Pour un arrêt définitif, fermer la fenêtre `lab-start`. |
| `lab-sync-monde.bat` | Remplace le monde du labo par la **dernière sauvegarde** de la prod. Le labo doit être éteint. Lancer `backup.bat` sur la prod juste avant pour avoir un monde à jour. |
| `lab-deploy.bat <pack>` | Passe un pack en **prod**. Il demande de taper `OUI`, fait une sauvegarde, puis remplace le pack dans `world\datapacks`. Il reste ensuite à faire `reload` ou `stop` dans la console de la prod. |
| `python outils\fusion_rp.py [--labo]` | Verse les resource packs des packs (`build/<nom>_rp/`) dans `metiers_resourcepack.zip` et affiche le SHA-1. Avec `--labo`, il sert aussi le zip sur `http://127.0.0.1:8765/` et y branche le labo, pour voir les textures avant de pousser. Redémarrer ensuite le labo. |
| `lab-cmd.bat < scenario.txt` | Joue un scénario de commandes : une commande par ligne, `#` pour un commentaire. |

## Commandes utiles en test

- `/gamerule send_command_feedback true` : à activer, car Métiers coupe les retours de commandes.
- `/tick freeze`, `/tick step 20`, `/tick sprint 3h` : faire avancer le temps. Utile pour les défis (toutes les 4 h), les boss (toutes les 3 h) et l'heure du métier.
- `/function metiers:version`, `/datapack list`
- `/execute as <pseudo> run function metiers:reset_joueur`

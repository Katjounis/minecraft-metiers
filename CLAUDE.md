# Consignes pour Claude

- Les commits se font au nom de la personne propriétaire du compte GitHub qui travaille sur le dépôt, et jamais au nom de « Claude ». Avant de commiter, vérifier `git config user.name` et `git config user.email` (configuration locale du clone). Si rien n'est configuré, demander quel compte utiliser.
  - Exemple pour Samuel (Katjounis) : `git -c user.name=Katjounis -c user.email=Katjounis@users.noreply.github.com commit ...`
- Le dépôt est une usine à datapacks : un dossier par pack dans `datapacks/<nom>/`, et le labo de test dans `labo/`. Voir `README.md` et `labo/LISEZMOI.md`.
- `metiers_resourcepack.zip` reste à la racine du dépôt. Le `server.properties` de la prod télécharge ce fichier par l'URL `raw/main/metiers_resourcepack.zip`, donc il ne faut pas le déplacer.
- Un pack n'est prêt pour la prod que si `labo\lab-reload.bat complet` affiche « Aucune erreur. ».

"""Allège les grosses images de police du resource pack (texte du monde illisible en 26.3).

Constat : chaque fois que les polices des menus ont grossi (glyphes de 256 px le 24/11, cadres et fonds d'arbre
le 26/11), les panneaux, les pseudos et les noms d'entités se sont mis à s'afficher en lettres hachées dans le
monde, alors que les menus restaient propres. Revenir à des glyphes plus légers avait réglé le problème le 25/11.
Les glyphes de police partagent leurs pages de texture avec les lettres du jeu : on garde donc ces pages
légères.

Ce script divise par deux la définition des grosses images de police (fonds d'arbre, panneaux, décors, scènes,
graphiques) sans changer leur taille à l'écran : le champ « height » de la police reste le même, le jeu agrandit
l'image. Les avances (largeur de chaque glyphe) restent identiques au pixel près, donc les espaces négatifs des
menus tombent toujours juste : une image dont la largeur utile serait changée n'est pas touchée.

Le traitement est marqué dans le zip (assets/minecraft/polices_allegees.json) : relancer le script ne réduit
pas deux fois la même image. Il est lancé automatiquement à la fin de fusion_rp.py.

  python labo\\outils\\allege_polices.py            traite metiers_resourcepack.zip et affiche le SHA-1
"""
import hashlib, io, json, os, sys, zipfile

from PIL import Image

OUTILS = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.dirname(os.path.dirname(OUTILS))
ZIP = os.path.join(DEPOT, "metiers_resourcepack.zip")
MARQUE = "assets/minecraft/polices_allegees.json"
SEUIL = 80          # un glyphe dont le grand côté atteint SEUIL px est réduit de moitié
EXCLUS = ("commerce:font/hud",)   # solde du Commerce : opacité codée pour le shader, on n'y touche pas


def _avances(im, cols, rows):
    """Avance de chaque case (dernière colonne non transparente + 1), comme le jeu la calcule."""
    cw, ch = im.width // cols, im.height // rows
    out = []
    for r in range(rows):
        for c in range(cols):
            bb = im.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)).getbbox()
            out.append(bb[2] if bb else 0)
    return out


def alleger(donnees):
    """Rend (zip modifié, liste des images réduites, surface avant, surface après)."""
    zin = zipfile.ZipFile(io.BytesIO(donnees))
    fichiers = {i.filename: (i, zin.read(i)) for i in zin.infolist()}
    deja = set(json.loads(fichiers[MARQUE][1])) if MARQUE in fichiers else set()
    reduites, avant, apres = [], 0, 0
    vues = set()
    for nom in sorted(fichiers):
        if not (nom.startswith("assets/") and "/font/" in nom and nom.endswith(".json")):
            continue
        police = json.loads(fichiers[nom][1])
        for p in police.get("providers", []):
            if p.get("type") != "bitmap":
                continue
            ns, chemin = p["file"].split(":", 1)
            img = f"assets/{ns}/textures/{chemin}"
            if img not in fichiers or img in vues or p["file"].startswith(EXCLUS):
                continue
            vues.add(img)
            im = Image.open(io.BytesIO(fichiers[img][1])).convert("RGBA")
            rows = len(p["chars"])
            cols = max(len(r) for r in p["chars"])
            cw, ch = im.width // cols, im.height // rows
            avant += im.width * im.height
            ok = (img not in deja and max(cw, ch) >= SEUIL and cw % 2 == 0 and ch % 2 == 0
                  and im.width == cw * cols and im.height == ch * rows)
            if ok:
                av = _avances(im, cols, rows)
                ok = all(a % 2 == 0 for a in av)
            if ok:
                petit = im.resize((im.width // 2, im.height // 2), Image.BOX)
                # le flou de la réduction ne doit pas changer les avances (bords transparents)
                if [a * 2 for a in _avances(petit, cols, rows)] != av:
                    a = petit.split()[3].point(lambda v: 255 if v >= 128 else 0)
                    petit.putalpha(a)
                ok = [x * 2 for x in _avances(petit, cols, rows)] == av
            if ok:
                buf = io.BytesIO()
                petit.save(buf, "PNG", optimize=True)
                fichiers[img] = (fichiers[img][0], buf.getvalue())
                reduites.append(img)
                deja.add(img)
                apres += petit.width * petit.height
            else:
                apres += im.width * im.height
    if not reduites:
        return donnees, [], avant, apres
    marque = zipfile.ZipInfo(MARQUE, date_time=(2026, 1, 1, 0, 0, 0))
    fichiers[MARQUE] = (marque, json.dumps(sorted(deja), indent=1).encode("utf-8"))
    sortie = io.BytesIO()
    with zipfile.ZipFile(sortie, "w", zipfile.ZIP_DEFLATED) as z:
        for nom, (info, data) in fichiers.items():
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    return sortie.getvalue(), reduites, avant, apres


def traiter(chemin=ZIP):
    with open(chemin, "rb") as f:
        donnees = f.read()
    neuf, reduites, avant, apres = alleger(donnees)
    if reduites:
        with open(chemin, "wb") as f:
            f.write(neuf)
    print(f"Polices : {len(reduites)} images réduites de moitié, surface {avant:,} -> {apres:,} px²".replace(",", " "))
    sha = hashlib.sha1(neuf).hexdigest()
    print(f"SHA-1 : {sha}")
    return sha


if __name__ == "__main__":
    traiter(sys.argv[1] if len(sys.argv) > 1 else ZIP)

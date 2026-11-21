"""Fusionne les resource packs des datapacks dans metiers_resourcepack.zip (racine du depot).

Le serveur ne peut imposer qu'UN resource pack : chaque pack qui a besoin de textures ecrit les siennes dans
datapacks/<nom>/build/<nom>_rp/assets/<nom>/ (via son sources/datapack.py), et ce script les verse dans le zip
commun. Il retire d'abord l'ancien assets/<nom>/ : on peut le relancer autant de fois qu'on veut, et il ne
touche jamais aux fichiers de Metiers.

  python fusion_rp.py            fusionne et affiche le SHA-1 (a recopier dans server.properties)
  python fusion_rp.py --labo     idem, puis sert le zip sur http://127.0.0.1:8765/ et y branche le labo
                                 (a redemarrer ensuite : lab-reload.bat complet). Ctrl+C pour arreter.
"""
import hashlib, http.server, io, json, os, re, sys, zipfile

OUTILS = os.path.dirname(os.path.abspath(__file__))
LABO = os.path.dirname(OUTILS)
DEPOT = os.path.dirname(LABO)
ZIP = os.path.join(DEPOT, "metiers_resourcepack.zip")
PORT = 8765


def packs_rp():
    d = os.path.join(DEPOT, "datapacks")
    for nom in sorted(os.listdir(d)):
        rp = os.path.join(d, nom, "build", nom + "_rp")
        if os.path.isdir(os.path.join(rp, "assets")):
            yield nom, rp


def fusionner():
    with open(ZIP, "rb") as f:
        ancien = zipfile.ZipFile(io.BytesIO(f.read()))
    rps = list(packs_rp())
    if not rps:
        print("Aucun resource pack a fusionner (lancer d'abord sources/datapack.py du pack).")
        return None
    retires = tuple(f"assets/{nom}/" for nom, _ in rps)
    sortie = io.BytesIO()
    ajoutes = 0
    with zipfile.ZipFile(sortie, "w", zipfile.ZIP_DEFLATED) as z:
        for info in ancien.infolist():
            if info.filename.startswith(retires):
                continue
            data = ancien.read(info)
            if info.filename == "pack.mcmeta":
                meta = json.loads(data.decode("utf-8"))
                meta["pack"]["description"] = "Métiers" + "".join(f" + {n.capitalize()}" for n, _ in rps) + " : textures et menus"
                data = json.dumps(meta, ensure_ascii=False, indent=1).encode("utf-8")
            z.writestr(info, data)
        for nom, rp in rps:
            for dp, _, fs in os.walk(rp):
                for fn in sorted(fs):
                    full = os.path.join(dp, fn)
                    arc = os.path.relpath(full, rp).replace(os.sep, "/")
                    # date fixe : meme contenu -> meme zip -> meme SHA-1
                    zi = zipfile.ZipInfo(arc, date_time=(2026, 1, 1, 0, 0, 0))
                    zi.compress_type = zipfile.ZIP_DEFLATED
                    with open(full, "rb") as f:
                        z.writestr(zi, f.read())
                    ajoutes += 1
    with open(ZIP, "wb") as f:
        f.write(sortie.getvalue())
    sha = hashlib.sha1(sortie.getvalue()).hexdigest()
    print(f"Fusionne : {', '.join(n for n, _ in rps)} ({ajoutes} fichiers) -> metiers_resourcepack.zip")
    print(f"SHA-1 : {sha}")
    print("Prod : apres commit + push, recopier ce SHA-1 dans resource-pack-sha1 du server.properties.")
    return sha


def brancher_labo(sha):
    sp = os.path.join(LABO, "serveur", "server.properties")
    with open(sp, encoding="utf-8") as f:
        txt = f.read()
    txt = re.sub(r"(?m)^resource-pack=.*$", f"resource-pack=http\\\\://127.0.0.1\\\\:{PORT}/metiers_resourcepack.zip", txt)
    txt = re.sub(r"(?m)^resource-pack-sha1=.*$", f"resource-pack-sha1={sha}", txt)
    with open(sp, "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"Labo : server.properties pointe sur http://127.0.0.1:{PORT}/ (redemarrer le labo pour le prendre en compte).")
    print("Pour revenir a GitHub : recopier les lignes resource-pack de labo/modele/server.properties.")


if __name__ == "__main__":
    sha = fusionner()
    if sha and "--labo" in sys.argv:
        brancher_labo(sha)
        os.chdir(DEPOT)
        print(f"Serveur http sur 127.0.0.1:{PORT} (Ctrl+C pour arreter)...")
        class SeulZip(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path.split("?")[0] != "/metiers_resourcepack.zip":
                    return self.send_error(404)
                return super().do_GET()

        http.server.ThreadingHTTPServer(("127.0.0.1", PORT), SeulZip).serve_forever()

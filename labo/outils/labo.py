"""Outils du labo de datapacks (appeles par les .bat du dossier labo).

  python labo.py packs                 liste les packs detectes
  python labo.py build [pack]          regenere les packs generes par script (tous par defaut)
  python labo.py reload [--complet]    build + /reload (ou redemarrage) + erreurs du log
  python labo.py erreurs [--depuis N]  erreurs de chargement dans serveur/logs/latest.log
  python labo.py installer [--depuis DOSSIER]
                                       cree le serveur du labo (ou recupere un ancien labo)
  python labo.py brancher              relie les packs du labo a leurs sources (jonctions)
  python labo.py sync                  remplace le monde du labo par la derniere sauvegarde de la prod
  python labo.py deploy <pack>         installe un pack sur la PROD

Reglages propres a chaque PC : labo/local.cmd (voir local.exemple.cmd), lus par les .bat
  LABO_JAVA            java.exe a utiliser
  LABO_PROD            dossier du serveur de production (sync, deploy, installer)
  LABO_PACKS_EXTERNES  packs hors depot : nom=dossier;nom2=dossier2
"""
import argparse, os, re, shutil, socket, subprocess, sys, time, zipfile

LABO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPOT = os.path.dirname(LABO)
DATAPACKS = os.path.join(DEPOT, "datapacks")
SERVEUR = os.path.join(LABO, "serveur")
MODELE = os.path.join(LABO, "modele")
LOG = os.path.join(SERVEUR, "logs", "latest.log")
RCON = os.path.join(LABO, "outils", "rcon.py")
RCON_PORT = 25576
PROD = os.environ.get("LABO_PROD") or None
# Erreurs connues et sans consequence, a masquer (expressions regulieres)
IGNORER = []


def packs():
    """Packs du depot (datapacks/<nom>/) et packs externes declares dans local.cmd.

    datapacks/<nom>/sources/datapack.py  -> pack genere : ecrit build/<nom>_datapack/ et <nom>.zip
    datapacks/<nom>/datapack/            -> pack ecrit a la main (pack.mcmeta + data/)
    """
    res = {}
    if os.path.isdir(DATAPACKS):
        for nom in sorted(os.listdir(DATAPACKS)):
            d = os.path.join(DATAPACKS, nom)
            gen = os.path.join(d, "sources", "datapack.py")
            if os.path.exists(gen):
                res[nom] = {"source": os.path.join(d, "build", nom + "_datapack"),
                            "zip": os.path.join(d, nom + ".zip"), "build": gen}
            elif os.path.isdir(os.path.join(d, "datapack")):
                res[nom] = {"source": os.path.join(d, "datapack"), "zip": os.path.join(d, nom + ".zip")}
    for item in filter(None, (os.environ.get("LABO_PACKS_EXTERNES") or "").split(";")):
        nom, _, dossier = item.partition("=")
        dossier = dossier.strip().rstrip("\\/")
        res[nom.strip()] = {"source": dossier, "zip": dossier + ".zip"}
    return res


def rcon(*cmds, quiet=False):
    args = [sys.executable, RCON] + (["-q"] if quiet else []) + list(cmds)
    return subprocess.run(args).returncode


def lab_allume():
    try:
        socket.create_connection(("127.0.0.1", RCON_PORT), timeout=1).close()
        return True
    except OSError:
        return False


def lignes_log():
    if not os.path.exists(LOG):
        return 0
    with open(LOG, encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def build(nom=None):
    ps = packs()
    if nom and nom not in ps:
        print("Pack inconnu. Choix :", ", ".join(ps))
        return False
    for n, p in ps.items():
        if "build" not in p or (nom and n != nom):
            continue
        print("== Generation de", n, "==")
        if subprocess.run([sys.executable, p["build"]], cwd=os.path.dirname(p["build"])).returncode:
            return False
    return True


def erreurs(depuis=0):
    """Affiche les erreurs du log a partir de la ligne `depuis` ; renvoie leur nombre."""
    if not os.path.exists(LOG):
        print("Pas encore de log.")
        return 0
    with open(LOG, encoding="utf-8", errors="replace") as f:
        lignes = f.read().splitlines()[depuis:]
    vues, n = set(), 0
    for i, l in enumerate(lignes):
        if "/ERROR]" not in l and not ("/WARN]" in l and "registry" in l.lower()):
            continue
        # La cause utile est dans l'exception Java qui suit
        detail = ""
        for suite in lignes[i + 1:i + 60]:
            if suite.startswith("[") and "] [" in suite:
                break
            if suite.startswith("Caused by:") or ("Exception" in suite and not suite.lstrip().startswith("at ")):
                detail = suite
        cle = re.sub(r"^\[[^\]]*\] \[[^\]]*\]: ", "", l) + detail
        if cle in vues or any(re.search(r, cle) for r in IGNORER):
            continue
        vues.add(cle)
        n += 1
        print("ERREUR :", re.sub(r"^\[[^\]]*\] \[[^\]]*\]: ", "", l))
        if detail:
            print("   ->", re.sub(r"^.*?(Exception|Error): ", "", detail)[:400])
    print("Aucune erreur." if n == 0 else f"{n} erreur(s).")
    return n


def reload(complet=False):
    if not build():
        return 1
    if not lab_allume():
        print("Le labo est eteint : lance lab-start.bat (les packs seront charges au demarrage).")
        return 1
    if complet:
        print("== Redemarrage complet (menus / dialogues) ==")
        rcon("stop", quiet=True)
        for _ in range(60):
            time.sleep(1)
            if not lab_allume():
                break
        print("Arret OK, la fenetre du labo relance le serveur...")
        for _ in range(180):
            time.sleep(1)
            if lab_allume():
                break
        else:
            print("Pas de redemarrage detecte (fenetre lab-start fermee ?).")
            return 1
        print("== Erreurs au demarrage ==")
        return 1 if erreurs(0) else 0
    debut = lignes_log()
    rcon("reload", quiet=True)
    time.sleep(3)
    print("== Erreurs apres /reload ==")
    n = erreurs(debut)
    print("Rappel : les menus (dialogues) ne sont relus qu'au redemarrage -> lab-reload.bat complet")
    return 1 if n else 0


def est_jonction(p):
    try:
        return bool(os.lstat(p).st_file_attributes & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT
    except (OSError, AttributeError):
        return False


def retirer(p):
    """Supprime un fichier, un dossier, ou seulement le lien s'il s'agit d'une jonction."""
    if est_jonction(p):
        os.rmdir(p)
    elif os.path.isdir(p):
        shutil.rmtree(p)
    elif os.path.exists(p):
        os.remove(p)


def retirer_jonctions(monde):
    """A faire AVANT d'effacer ou deplacer un monde, pour ne jamais toucher aux sources."""
    dp = os.path.join(monde, "datapacks")
    if os.path.isdir(dp):
        for f in os.listdir(dp):
            if est_jonction(os.path.join(dp, f)):
                os.rmdir(os.path.join(dp, f))


def copier_monde_prod():
    if not PROD:
        print("LABO_PROD n'est pas defini dans local.cmd : pas de monde de prod a copier.")
        return False
    dossier = os.path.join(PROD, "backups")
    sauvegardes = sorted(f for f in os.listdir(dossier) if f.endswith(".zip")) if os.path.isdir(dossier) else []
    if not sauvegardes:
        print("Aucune sauvegarde dans", dossier, "-> lance backup.bat sur la prod.")
        return False
    print("Monde copie depuis :", sauvegardes[-1])
    monde = os.path.join(SERVEUR, "world")
    retirer_jonctions(monde)
    if os.path.exists(monde):
        shutil.rmtree(monde)
    with zipfile.ZipFile(os.path.join(dossier, sauvegardes[-1])) as z:
        for m in z.namelist():
            if m.replace("\\", "/").startswith("world/"):
                z.extract(m, SERVEUR)
    return True


def sync():
    if lab_allume():
        print("Arrete d'abord le labo (fermer la fenetre lab-start).")
        return 1
    if not copier_monde_prod():
        return 1
    brancher()
    print("Monde du labo pret. Lance lab-start.bat.")
    return 0


def installer(depuis=None):
    if lab_allume():
        print("Un labo tourne deja : ferme sa fenetre lab-start avant d'installer.")
        return 1
    if os.path.exists(os.path.join(SERVEUR, "server.jar")):
        print("Serveur deja installe :", SERVEUR)
        brancher()
        return 0
    os.makedirs(SERVEUR, exist_ok=True)
    if depuis:
        # Recuperation d'un ancien labo : on deplace tout sauf les scripts
        depuis = os.path.abspath(depuis)
        retirer_jonctions(os.path.join(depuis, "world"))
        garder = {"outils", "LISEZMOI-LABO.md"}
        for f in os.listdir(depuis):
            if f in garder or f.endswith(".bat"):
                continue
            shutil.move(os.path.join(depuis, f), os.path.join(SERVEUR, f))
            print("Deplace :", f)
        print("Ancien labo recupere. Le dossier", depuis, "ne contient plus que ses anciens scripts : il peut etre supprime.")
    else:
        if not PROD or not os.path.exists(os.path.join(PROD, "server.jar")):
            print("Copie manuellement un server.jar (meme version que la prod) dans", SERVEUR,
                  "ou definis LABO_PROD dans local.cmd, puis relance.")
            return 1
        shutil.copy2(os.path.join(PROD, "server.jar"), SERVEUR)
        shutil.copy2(os.path.join(MODELE, "server.properties"), SERVEUR)
        for f in ("ops.json", "usercache.json", "server-icon.png"):
            if os.path.exists(os.path.join(PROD, f)):
                shutil.copy2(os.path.join(PROD, f), SERVEUR)
        # Meme compte Mojang que la prod, dont l'EULA est deja acceptee
        with open(os.path.join(SERVEUR, "eula.txt"), "w") as f:
            f.write("eula=true\n")
        if not copier_monde_prod():
            print("Le serveur creera un monde neuf au premier demarrage.")
    brancher()
    print("Labo installe. Lance lab-start.bat.")
    return 0


def brancher():
    """Remplace les zips des packs en developpement par une jonction vers leurs sources."""
    dp = os.path.join(SERVEUR, "world", "datapacks")
    os.makedirs(dp, exist_ok=True)
    for nom, p in packs().items():
        for f in os.listdir(dp):
            if f.lower() == nom or f.lower().startswith(nom + ".") or f.lower().startswith(nom + " "):
                retirer(os.path.join(dp, f))
        if "build" in p and not os.path.isdir(p["source"]):
            build(nom)
        if os.path.isdir(p["source"]):
            subprocess.run(["cmd", "/c", "mklink", "/J", os.path.join(dp, nom), p["source"]],
                           stdout=subprocess.DEVNULL, check=True)
            print("Branche :", nom, "->", p["source"])
        else:
            print("Introuvable, non branche :", nom, "->", p["source"])


def zipper(source, cible):
    if os.path.exists(cible):
        os.remove(cible)
    with zipfile.ZipFile(cible, "w", zipfile.ZIP_DEFLATED) as z:
        for d, _, fs in os.walk(source):
            for f in sorted(fs):
                full = os.path.join(d, f)
                z.write(full, os.path.relpath(full, source).replace(os.sep, "/"))


def deploy(nom):
    ps = packs()
    if nom not in ps:
        print("Pack inconnu. Choix :", ", ".join(ps))
        return 1
    if not PROD:
        print("LABO_PROD n'est pas defini dans local.cmd.")
        return 1
    p = ps[nom]
    if "build" in p:
        if not build(nom):
            return 1
    else:
        zipper(p["source"], p["zip"])
    print("Zip pret :", p["zip"])
    print("\n!! Ceci va modifier le serveur de PRODUCTION (" + PROD + ") !!")
    if input("Taper OUI pour continuer : ").strip() != "OUI":
        print("Annule.")
        return 1
    print("== Sauvegarde de la prod ==")
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                        os.path.join(PROD, "backup.ps1")])
    if r.returncode:
        print("Sauvegarde en echec : deploiement annule.")
        return 1
    dp = os.path.join(PROD, "world", "datapacks")
    for f in os.listdir(dp):
        if f.lower() == nom or f.lower().startswith(nom + ".") or f.lower().startswith(nom + " "):
            retirer(os.path.join(dp, f))
            print("Retire :", f)
    shutil.copy2(p["zip"], os.path.join(dp, nom + ".zip"))
    print("Installe : world\\datapacks\\" + nom + ".zip")
    print("\nDerniere etape, dans la console de la prod :")
    print("  reload   si seules des fonctions ont change")
    print("  stop     (start.bat redemarre tout seul) si un menu, un progres ou un autre fichier de registre a change")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("packs")
    b = sp.add_parser("build")
    b.add_argument("pack", nargs="?")
    sp.add_parser("brancher")
    r = sp.add_parser("reload")
    r.add_argument("--complet", action="store_true")
    e = sp.add_parser("erreurs")
    e.add_argument("--depuis", type=int, default=0)
    i = sp.add_parser("installer")
    i.add_argument("--depuis")
    sp.add_parser("sync")
    d = sp.add_parser("deploy")
    d.add_argument("pack")
    a = ap.parse_args()
    if a.cmd == "packs":
        for n, p in packs().items():
            print(f"{n:12} {'genere' if 'build' in p else 'manuel':7} {p['source']}")
    elif a.cmd == "build":
        sys.exit(0 if build(a.pack) else 1)
    elif a.cmd == "brancher":
        brancher()
    elif a.cmd == "reload":
        sys.exit(reload(a.complet))
    elif a.cmd == "erreurs":
        sys.exit(1 if erreurs(a.depuis) else 0)
    elif a.cmd == "installer":
        sys.exit(installer(a.depuis))
    elif a.cmd == "sync":
        sys.exit(sync())
    elif a.cmd == "deploy":
        sys.exit(deploy(a.pack))

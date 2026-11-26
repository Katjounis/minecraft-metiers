"""Outils d'ecriture communs du pack Boss (fonctions, JSON, textes) et des animations de squelette."""
import json, os

NS = "boss"
ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(ICI, "..", "build", "boss_datapack")
RP = os.path.join(ICI, "..", "build", "boss_rp", "assets", "boss")
F = f"data/{NS}/function/"


def w(path, txt):
    if isinstance(txt, (list, tuple)):
        txt = "\n".join(txt)
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    lignes = [l.strip() for l in txt.strip().splitlines()]
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(l for l in lignes if l and not l.startswith("#")) + "\n")


def fn(nom, txt):
    w(F + nom + ".mcfunction", txt)


def wj(path, obj):
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def js(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


PREF = {"text": "[Boss] ", "color": "dark_red", "bold": True}


def dire(cible, *morceaux):
    """tellraw avec le prefixe [Boss] ; morceaux = composants texte (dict) ou (texte, couleur)."""
    comp = [PREF]
    for m in morceaux:
        if isinstance(m, tuple):
            comp.append({"text": m[0], "color": m[1], "bold": False})
        else:
            comp.append(m)
    return f"tellraw {cible} {js(comp)}"


def titre(cible, t, sous=None, couleur="white", sous_couleur="gray"):
    out = [f"title {cible} times 8 60 16"]
    if sous:
        out.append(f"title {cible} subtitle {js({'text': sous, 'color': sous_couleur})}")
    out.append(f"title {cible} title {js({'text': t, 'color': couleur, 'bold': True})}")
    return out


def barre(cible, t, couleur="gold"):
    return f"title {cible} actionbar {js({'text': t, 'color': couleur})}"


def blesse(d):
    """Degats scriptes avec la regle « on ne meurt pas dans l'arene » (K.O. a 3 coeurs)."""
    return f"function boss:joueur/blesse {{d:{d},lim:{d + 6}}}"

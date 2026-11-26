# -*- coding: utf-8 -*-
# 26/11/2026 : outil commun aux 4 packs pour poser un panneau « succès » (dessiné par Métiers, voir ref_panneaux.py).
# Usage (dans un générateur) :
#   exec(open(<chemin>/panneaux_lib.py).read())
#   corps = pan_corps("commerce", clics={1: "trigger commerce set 9"}, survols={1: {"text": "..."}}, fixes={1: "on"})
# clics[k] : commande ; survols[k] : composant d'infobulle ; fixes[k] : état fixe (on, off, dispo, notif), sinon $(aK).
# Les textes variables ($(iK), $(nK)) et leurs rattrapages ($(pK) $(rK), $(qK) $(sK)) sont à remplir par le pack ;
# pan_pads(nom, k, lettre, texte) donne les deux caractères de rattrapage pour un texte donné.
import json as _pj
import copy as _pc
import os as _po

_PAN_FIC = _po.path.join(_po.path.dirname(_po.path.abspath(__file__)) if "__file__" in dir() else ".", "panneaux.json")


def _pan_data():
    for p in (_PAN_FIC, _po.path.join(_po.path.dirname(_po.path.abspath(__file__)), "..", "..", "metiers", "sources", "panneaux.json")):
        if _po.path.exists(p):
            return _pj.load(open(p, encoding="utf-8"))
    raise FileNotFoundError("panneaux.json : construire Métiers d'abord")


_PAN = _pan_data()
_LARG = _pj.load(open(_po.path.join(_po.path.dirname(_PAN_FIC) if _po.path.exists(_PAN_FIC) else
                                    _po.path.join(_po.path.dirname(_po.path.abspath(__file__)), "..", "..", "metiers", "sources"),
                                    "larg_police.json"), encoding="utf-8"))


def pan_larg(s):
    return sum(_LARG.get(c, 6) for c in s)


def pan_contenu(nom, clics, survols, fixes=None):
    P = _PAN[nom]
    out = []
    for c in _pc.deepcopy(P["contenu"]):
        ce = c.get("click_event")
        if ce and ce["command"].startswith("§C"):   # les signets du livre ont leur commande en dur
            k = int(ce["command"][2:])
            if clics.get(k):
                ce["command"] = clics[k]
            else:
                del c["click_event"]
        he = c.get("hover_event")
        if he and isinstance(he["value"], str) and he["value"].startswith("§H"):
            k = int(he["value"][2:])
            if survols.get(k):
                he["value"] = survols[k]
            else:
                del c["hover_event"]
        for k, e in (fixes or {}).items():
            c["text"] = c["text"].replace(f"$(a{k})", P["etats"][str(k)][e])
        out.append(c)
    return out


def pan_corps(nom, clics, survols, fixes=None):
    """Élément de corps (dict) : plain_message à la largeur du panneau."""
    return {"type": "minecraft:plain_message", "width": _PAN[nom]["largeur"], "contents": pan_contenu(nom, clics, survols, fixes)}


def pan_snbt(o):
    return _pj.dumps(o, ensure_ascii=False, separators=(",", ":"))


def pan_etat(nom, k, e):
    return _PAN[nom]["etats"][str(k)][e]


def pan_pads(nom, k, lettre, texte):
    """Les deux caractères (avant, après) qui centrent « texte » à la place de l'estimation ; lettre « p » (info) ou « q » (nom)."""
    return _PAN[nom]["pads"][f"{lettre}{k}"][str(min(140, pan_larg(texte)))]

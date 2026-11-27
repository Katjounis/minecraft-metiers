# -*- coding: utf-8 -*-
# Journal des Écus (27/11/2026). Partagé par tous les packs qui touchent au solde c.ecus de Commerce.
#
# Chaque ligne d'un pack qui ajoute ou retire des Écus est doublée, juste après, par la même opération sur un
# compteur « annoncé » propre au pack (c.a_met pour Métiers, c.a_cmp pour Compagnons...). Commerce compare chaque
# seconde la variation du solde avec la somme des compteurs : ce qui est annoncé part dans l'historique de la banque
# avec le nom du pack, le reste est noté « mouvement non enregistré ». Plus aucun Écu ne bouge sans trace.
#
# Usage, juste avant le zip d'un pack :  miroir_ecus(<dossier du pack généré>, "c.a_met")
import os, re

_ADD = re.compile(r"scoreboard players (add|remove) (\S+) c\.ecus (-?\d+|\$\(\w+\))$")
_OPE = re.compile(r"scoreboard players operation (\S+) c\.ecus ([+\-]=) (\S+) (\S+)$")


def miroir_ecus(root, obj):
    """Double chaque modification de c.ecus par la même sur obj. Renvoie le nombre de lignes doublées."""
    n = 0
    for dp, _, fs in os.walk(root):
        for fn in fs:
            if not fn.endswith(".mcfunction"):
                continue
            p = os.path.join(dp, fn)
            src = open(p, encoding="utf-8").read().split("\n")
            out = []
            for ln in src:
                out.append(ln)
                s = ln.rstrip()
                m = _ADD.search(s) or _OPE.search(s)
                if not m:
                    continue
                avant = s[:m.start()]
                # une condition sur le solde lui-même (autre que « le score existe ») serait relue après le paiement
                cond = re.findall(r"if score \S+ c\.ecus (matches \S+|[<>=]+ \S+ \S+)", avant)
                if any(c != "matches -2147483648.." for c in cond):
                    raise SystemExit(f"journal des Écus : condition sur c.ecus dans la même ligne que le paiement ({p}) : {s}")
                if m.re is _ADD:
                    mir = f"scoreboard players {m.group(1)} {m.group(2)} {obj} {m.group(3)}"
                else:
                    mir = f"scoreboard players operation {m.group(1)} {obj} {m.group(2)} {m.group(3)} {m.group(4)}"
                out.append(avant + mir)
                n += 1
            open(p, "w", encoding="utf-8").write("\n".join(out))
    return n

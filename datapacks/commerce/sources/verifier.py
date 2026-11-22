# -*- coding: utf-8 -*-
# Contrôle statique du pack généré (sans serveur) : JSON, lignes de macro, appels de fonctions,
# et SNBT des dialogues, tellraw et give (macros remplacées par des valeurs d'essai).
# Usage : python verifier.py  (après datapack.py). Ne remplace pas le labo, il attrape les fautes de frappe.
import os, re, json, sys
import nbtlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "commerce_datapack")
EXTERNES = {"metiers"}  # namespaces fournis par un autre pack
err = []
funcs, calls, tags = set(), [], set()
for dp, _, fs in os.walk(ROOT):
    for fn in fs:
        p = os.path.join(dp, fn)
        rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
        if fn.endswith(".json") or fn.endswith(".mcmeta"):
            try:
                json.load(open(p, encoding="utf-8"))
            except Exception as e:
                err.append(f"{rel}: JSON invalide ({e})")
            m = re.match(r"data/([^/]+)/tags/function/(.+)\.json", rel)
            if m:
                tags.add(f"{m.group(1)}:{m.group(2)}")
        if fn.endswith(".mcfunction"):
            m = re.match(r"data/([^/]+)/function/(.+)\.mcfunction", rel)
            funcs.add(f"{m.group(1)}:{m.group(2)}")

def snbt(txt):
    t = re.sub(r"\$\(([a-zA-Z0-9_]+)\)", lambda m: "[{text:\"\"}]" if m.group(1) == "C" else "1", txt)
    t = t.replace("\\n", " ")  # \n est valide en SNBT 26.x, pas dans nbtlib
    t = re.sub(r"(?<=[:,\[])true(?=[,}\]])", "1b", t)
    t = re.sub(r"(?<=[:,\[])false(?=[,}\]])", "0b", t)
    return nbtlib.parse_nbt(t)

def bloc(s, start):
    """Extrait un bloc {...} ou [...] équilibré à partir de start (guillemets respectés)."""
    o = s[start]; c = {"{": "}", "[": "]"}[o]; d = 0; q = None; i = start
    while i < len(s):
        ch = s[i]
        if q:
            if ch == "\\": i += 1
            elif ch == q: q = None
        elif ch in "\"'": q = ch
        elif ch in "{[": d += 1
        elif ch in "}]":
            d -= 1
            if d == 0: return s[start:i + 1]
        i += 1
    raise ValueError("bloc non fermé")

for dp, _, fs in os.walk(ROOT):
    for fn in fs:
        if not fn.endswith(".mcfunction"): continue
        p = os.path.join(dp, fn); rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
        for n, line in enumerate(open(p, encoding="utf-8").read().splitlines(), 1):
            if not line.strip() or line.startswith("#"): continue
            macro = line.startswith("$")
            body = line[1:] if macro else line
            if macro and "$(" not in body: err.append(f"{rel}:{n} ligne macro sans variable")
            if not macro and re.search(r"\$\([a-z]", body) and 'set value "$(q)"' not in body:
                err.append(f"{rel}:{n} variable de macro hors ligne macro")
            for m in re.finditer(r"function (#?[a-z_]+:[a-z0-9_/$()]+)", body):
                calls.append((rel, n, m.group(1)))
            for kw in ("dialog show @s ", "tellraw @s ", "tellraw @a ", "set value {", "append value {", "set value [", "give @s minecraft:villager_spawn_egg"):
                k = body.find(kw)
                if k < 0: continue
                if kw.startswith("give"):
                    s = body.index("[", k); blk = bloc(body, s)
                    for part in re.split(r",(?=minecraft:)", blk[1:-1]):
                        key, val = part.split("=", 1)
                        try: snbt(val)
                        except Exception as e: err.append(f"{rel}:{n} SNBT give {key} : {e}")
                    continue
                s = k + len(kw) - (1 if kw.endswith(("{", "[")) else 0)
                while body[s] not in "{[": s += 1
                try:
                    snbt(bloc(body, s))
                except Exception as e:
                    err.append(f"{rel}:{n} SNBT ({kw.strip()}) : {str(e)[:160]}")
for rel, n, f in calls:
    if "$(" in f: continue
    ns = f.lstrip("#").split(":")[0]
    if ns in EXTERNES and f.startswith("#"): continue
    if f.startswith("#"):
        if f[1:] not in tags: err.append(f"{rel}:{n} tag de fonction inconnu {f}")
    elif f not in funcs and ns not in EXTERNES:
        err.append(f"{rel}:{n} fonction inconnue {f}")
print("\n".join(err) if err else "Aucune erreur statique.")
print(len(funcs), "fonctions,", len(calls), "appels")
sys.exit(1 if err else 0)

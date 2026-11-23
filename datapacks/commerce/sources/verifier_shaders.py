# -*- coding: utf-8 -*-
# Compile les shaders du resource pack Commerce avec glslangValidator, dans chaque variante que le jeu construit
# (texte du monde, texte d'interface, texte vu à travers les blocs, OIT), après avoir remplacé les #include
# comme le fait Minecraft. Usage : python verifier_shaders.py <chemin de glslangValidator>
import os, re, sys, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
INC = os.path.join(HERE, "shaders_26.3")
SRC = os.path.join(HERE, "..", "build", "commerce_rp", "assets", "minecraft", "shaders", "core")
GLSL = sys.argv[1] if len(sys.argv) > 1 else "glslangValidator"
VARIANTES = [[], ["IS_GUI"], ["IS_SEE_THROUGH"], ["OIT", "OIT_COEFF_COUNT 4", "OIT_ACCUMULATE"], ["OIT", "OIT_COEFF_COUNT 8", "OIT_ACCUMULATE"], ["OIT", "OIT_COEFF_COUNT 4", "OIT_ALPHA_ONLY"], ["IS_GUI", "IS_GRAYSCALE"]]


def deplier(txt, vus=None):
    vus = vus or set()
    def rep(m):
        nom = m.group(1).split(":")[-1]
        if nom in vus:
            return ""
        vus.add(nom)
        return deplier(open(os.path.join(INC, nom), encoding="utf-8").read(), vus)
    return re.sub(r"#include <([^>]+)>", rep, txt)


def compiler(src, fn, defs):
    lignes = src.split("\n")
    k = 2 if lignes[1].startswith("#extension") else 1
    txt = deplier("\n".join(lignes[:k] + [f"#define {d}" for d in defs] + lignes[k:]))
    with tempfile.NamedTemporaryFile("w", suffix=".vert" if fn.endswith("vsh") else ".frag", delete=False) as t:
        t.write(txt)
    r = subprocess.run([GLSL, t.name], capture_output=True, text=True)
    return r.returncode == 0, r.stdout


# une variante compte si le shader vanilla y compile (sinon il manque des defines internes au jeu)
err = 0
for fn in ("text.vsh", "text.fsh"):
    src = open(os.path.join(SRC, fn), encoding="utf-8").read()
    van = open(os.path.join(INC, fn), encoding="utf-8").read()
    for defs in VARIANTES:
        if not compiler(van, fn, defs)[0]:
            print("--  " + fn, defs, "(non compilable en vanilla ici, ignorée)")
            continue
        ok, out = compiler(src, fn, defs)
        err += not ok
        print(("OK  " if ok else "ERR ") + fn, defs or "(monde)")
        if not ok:
            print(out[-1500:])
print("Shaders valides." if not err else f"{err} variante(s) en erreur.")
sys.exit(1 if err else 0)

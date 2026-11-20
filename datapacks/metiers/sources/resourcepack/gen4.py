"""Skins : variantes de palette appliquées aux formes existantes (aperçu sur la pioche et le heaume du palier 3)."""
import sys
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else "."]
import gen2
from gen2 import palette, save, item_def, ref, R

SKINS = {
    "givre":    dict(metal=["#1a2a3a", "#3a6a8a", "#7ab0d0", "#bfe4f5", "#eefaff", "#ffffff"], glow=["#5ac8ff", "#bff0ff", "#ffffff"],
                     trim=["#3d4046", "#8d929b", "#d8dce2", "#ffffff"], cloth=["#0a2a4a", "#1a4a7a", "#3a7ab0", "#7ab8e8"], grip=["#1a2430", "#2e4052", "#46607a", "#6a88a8"]),
    "corail":   dict(metal=["#04201e", "#0a4a46", "#14807a", "#3ac0b4", "#a0f0e8", "#e8fffc"], glow=["#ff5a4a", "#ff9a8a", "#ffe0da"],
                     trim=["#6a5a50", "#c8b8a8", "#f0e8e0", "#ffffff"], cloth=["#5a1a14", "#a03a2a", "#e0604a", "#ff9a8a"], grip=["#0a2422", "#16403c", "#245c56", "#3a807a"]),
    "or_royal": dict(metal=["#3a2a06", "#7a5a10", "#c9972a", "#f0cc4c", "#fff3bc", "#ffffff"], glow=["#c8142f", "#ff4a60", "#ffd0d8"],
                     trim=["#300407", "#6e0b16", "#a81628", "#e2485a"], cloth=["#30040a", "#6e0a16", "#b0122a", "#e8485c"], grip=["#30040a", "#5e0a16", "#8a1224", "#b02a3c"]),
    "ossements":dict(metal=["#3a3226", "#6a5c46", "#a8987a", "#d8ccb0", "#f2ead8", "#ffffff"], glow=["#2aa84a", "#7aff9a", "#e0ffe8"],
                     trim=["#3a1a0a", "#6a3214", "#9a4a1e", "#c8703a"], cloth=["#1a1a14", "#2e2e24", "#46463a", "#6a6a58"], grip=["#2a2016", "#4a3a26", "#6a543a", "#8a7050"]),
    "magma":    dict(metal=["#1a0402", "#4a0a04", "#8a1a08", "#d0401a", "#ff8a3a", "#ffd0a0"], glow=["#ffb000", "#ffe060", "#ffffff"],
                     trim=["#0e0b0d", "#221c20", "#332a30", "#4a3e45"], cloth=["#2a0602", "#5a1004", "#8a1a08", "#c03010"], grip=["#100604", "#24100a", "#381a10", "#4e2618"]),
    "ombre":    dict(metal=["#050308", "#110a1a", "#1e1230", "#2e1e48", "#4a3470", "#7a5aa8"], glow=["#6a1aff", "#b07cff", "#f0e0ff"],
                     trim=["#1e0a36", "#3a1660", "#6a2aa8", "#a65ef0"], cloth=["#0a0412", "#1a0a2a", "#2a1240", "#401a60"], grip=["#08050c", "#140c1e", "#20142e", "#2e1e42"]),
}
def P_of(n):
    P = dict(palette(3)); d = SKINS[n]
    P["metal"] = R(d["metal"]); P["blade"] = R(d["metal"][:5]); P["glow"] = R(d["glow"]); P["trim"] = R(d["trim"])
    P["cloth"] = R(d["cloth"]); P["grip"] = R(d["grip"]); P["feather"] = R(d["metal"][2:6])
    return P
if __name__ == "__main__":
    for n in SKINS:
        P = P_of(n)
        for kind, fn in (("m", lambda: gen2.pioche(3, P)), ("heaume", lambda: gen2.heaume_3("x", P, None))):
            mdl, at, gl, S = fn(); name = f"skin_{n}_{kind}"
            save(mdl, at, gl, S, name); item_def(name, ref(name))
    print("skins ok")

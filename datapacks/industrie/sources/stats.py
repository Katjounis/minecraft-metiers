# -*- coding: utf-8 -*-
# Tableau de l'île (28/11/2026) : clic droit sur le Nexus. Énergie en barre, recettes, et la production de chaque type de machine possédé.
ST = [val("jn", "i.jn"), val("r7", "i.r7"), val("np", "i.np"), val("ri", "i.ri"),
      f"{S} operation #x i.t = @s i.fe", f"{S} operation #x i.t /= #10 i.g", f"execute store result storage {M_} fep int 1 run {S} get #x i.t",
      f"{S} set #x i.t 0"] + [f"{S} operation #x i.t += @s i.s_{p}" for p in PL] + [
      f"execute store result storage {M_} st int 1 run {S} get #x i.t",
      f'data modify storage {M_} l set value [{{text:"MES MACHINES",color:"#F7C843",bold:true}}]']
# barre d'énergie : 10 cases
for k in range(11):
    bar = "█" * k + "░" * (10 - k)
    lo, hi = k * 100, k * 100 + 99
    cond = f"{lo}.." if k == 10 else f"{lo}..{hi}"
    ST.append(f'execute if score @s i.fe matches {cond} run data modify storage {M_} bar set value "{bar}"')
ST.append(f'execute if score @s i.fe matches ..-1 run data modify storage {M_} bar set value "{"░" * 10}"')
for k, m in enumerate(ML):
    d = MACH[m]
    nom = NOM_COURT[m]
    L_ = [val("n", f"i.n_{m}")]
    if d["kw"] < 0:
        L_ += [f"{S} operation #v i.t = @s i.q_{m}", f"{S} set #y i.t {-d['kw']}", f"{S} operation #v i.t *= #y i.t", f"{S} operation #v i.t /= #100 i.g",
               f"execute store result storage {M_} v0 int 1 run {S} get #v i.t"]
        txt = f"\\n{nom} x$(n) : +$(v0) kW"
    elif m == "spawner":
        txt = f"\\n{nom} x$(n) : butin de tes spawners"
    else:
        parts = []
        for i, (p, q) in enumerate(d["out"].items()):
            L_ += [f"{S} operation #v i.t = @s i.q_{m}", f"{S} set #y i.t {q}", f"{S} operation #v i.t *= #y i.t", f"{S} operation #v i.t /= #100 i.g",
                   f"execute store result storage {M_} v{i} int 1 run {S} get #v i.t"]
            parts.append(f"$(v{i}) {PROD[p][0].lower()}")
        txt = f"\\n{nom} x$(n) : " + ", ".join(parts) + " par heure"
    L_ += [f"function {NS}:stats/ligne_{k}_m with storage {M_}"]
    fn(f"stats/ligne_{k}", L_)
    fn(f"stats/ligne_{k}_m", "$" + f"data modify storage {M_} l append value " + T(txt, "white"))
    ST.append(f"execute if score @s i.n_{m} matches 1.. run function {NS}:stats/ligne_{k}")
ST.append(f"function {NS}:menu/stats_d with storage {M_}")
fn("menu/stats", ST)
fn("menu/stats_d", "$" + dlg(T("MON ÎLE", OR, True),
    [msg(L(T("Énergie  ", "aqua", True), T("$(bar)", "aqua"), T("  $(fep) %", "white"),
           T("\\nAujourd'hui : ", "gray"), T("$(jn) Écus", OR, True), T("   moyenne : $(r7) / jour", "gray"),
           T("\\nNexus : $(st) objets en stock   ·   $(np) parcelles", "gray")), 300),
     '{type:"minecraft:plain_message",width:300,contents:$(l)}'],
    [btn(T("Menu de l'industrie", "green", True), 1, 150), btn(T("Vendre et contrats", OR), 7, 150), btn(T("Acheter une machine", OR), 4, 150),
     btn(T("Fermer", "gray"), 0, 150)], 2))

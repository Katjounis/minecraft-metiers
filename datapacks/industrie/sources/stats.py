# -*- coding: utf-8 -*-
# Tableau de l'île (28/11/2026) : clic droit sur le Nexus. Graphiques en blocs de texte : recettes des 12 dernières heures,
# part de chaque type de machine dans la production (en Écus par heure au prix de base), énergie fournie / demandée.
# Chaque case est un « █ » (même largeur partout) : coloré si plein, gris très sombre si vide, donc les colonnes restent alignées.
PLEIN, VIDE = "█", "█"
NB_L = 16                                       # longueur des barres horizontales


def ap(txt, col):
    return f"data modify storage {M_} l append value " + T(txt, col)


ST = [val("jn", "i.jn"), val("r7", "i.r7"),
      f"{S} operation #x i.t = @s i.fe", f"{S} operation #x i.t /= #10 i.g", f"execute store result storage {M_} fep int 1 run {S} get #x i.t",
      f"{S} set #x i.t 0"] + [f"{S} operation #x i.t += @s i.s_{p}" for p in PL] + [
      f"execute store result storage {M_} st int 1 run {S} get #x i.t",
      f"data modify storage {M_} l set value [{{text:\"\"}}]"]

# ---- 1. recettes des 12 dernières heures : courbe en une ligne (▁▂▃▄▅▆▇█), l'heure en cours en vert
SPARK = "▁▂▃▄▅▆▇█"
ST += [f"{S} operation #mx i.t = @s i.h0"] + [f"execute if score @s i.h{k} > #mx i.t run {S} operation #mx i.t = @s i.h{k}" for k in range(1, 12)]
ST += [f"execute if score #mx i.t matches ..0 run {S} set #mx i.t 1", f"execute store result storage {M_} mx int 1 run {S} get #mx i.t",
       f"{S} operation #m1 i.t = #mx i.t", f"{S} remove #m1 i.t 1",
       ap("RECETTES, 12 DERNIÈRES HEURES\\n", OR)]
for k in range(11, -1, -1):
    col = "#4cd964" if k == 0 else OR
    ST += [f"{S} operation #t i.t = @s i.h{k}", f"{S} operation #t i.t *= #8 i.g", f"{S} operation #t i.t += #m1 i.t", f"{S} operation #t i.t /= #mx i.t",
           f"execute if score #t i.t matches ..0 run " + ap(SPARK[0], "#3a3a3a")]
    ST += [f"execute if score #t i.t matches {n} run " + ap(SPARK[n - 1], col) for n in range(1, 9)]
ST += [f"function {NS}:stats/titre_h with storage {M_}"]
fn("stats/titre_h", "$" + ap("\\nmeilleure heure : $(mx) Écus", "gray"))

# ---- 2. production par type de machine (Écus par heure au prix de base) : nom en couleur de famille, fine barre dessous
NB = 40
ST += [f"{S} set #mx i.t 1"]
VM = []
for k, m in enumerate(ML):
    d = MACH[m]
    if d["kw"] < 0 or m == "spawner" or not d.get("out"):
        continue
    v = sum(q * PROD[p][2] for p, q in d["out"].items())
    fn(f"stats/v_{k}", [f"{S} operation #v{k} i.t = @s i.q_{m}", f"{S} set #y i.t {max(1, v // 10000)}", f"{S} operation #v{k} i.t *= #y i.t",
                        f"execute if score #v{k} i.t > #mx i.t run {S} operation #mx i.t = #v{k} i.t"])
    ST += [f"{S} set #v{k} i.t 0", f"execute if score @s i.n_{m} matches 1.. run function {NS}:stats/v_{k}"]
    VM.append((k, m))
ST.append(ap("\\n\\nPRODUCTION (Écus par heure)", OR))


def barre(score, mx, col, n=NB, fond="#3a3a3a"):
    out = []
    for b in range(1, n + 1):
        out += [f"{S} operation #u i.t = {mx}", f"{S} set #y i.t {b}", f"{S} operation #u i.t *= #y i.t",
                f"{S} operation #t i.t = {score}", f"{S} set #y i.t {n}", f"{S} operation #t i.t *= #y i.t",
                f"execute if score #t i.t >= #u i.t run " + ap("|", col), f"execute unless score #t i.t >= #u i.t run " + ap("|", fond)]
    return out


for k, m in VM:
    c = FAMILLES[FAM[m]][1]
    L_ = [val("n", f"i.n_{m}"), f"execute store result storage {M_} v int 1 run {S} get #v{k} i.t", f"function {NS}:stats/b_{k}_m with storage {M_}"]
    L_ += barre(f"#v{k} i.t", "#mx i.t", c)
    fn(f"stats/b_{k}", L_)
    fn(f"stats/b_{k}_m", "$" + ap(f"\\n{COURT[m]} x$(n)  ·  $(v)\\n", c))
    ST.append(f"execute if score @s i.n_{m} matches 1.. run function {NS}:stats/b_{k}")

# ---- 3. énergie : une barre, bleu = couvert, rouge = ce qui manque
ST += [f"function {NS}:stats/energie"]
EG = [f"{S} operation #mx i.t = @s i.off", f"execute if score @s i.dem > #mx i.t run {S} operation #mx i.t = @s i.dem",
      f"execute if score #mx i.t matches ..0 run {S} set #mx i.t 1",
      f"{S} operation #x i.t = @s i.off", f"{S} operation #x i.t /= #10 i.g", f"execute store result storage {M_} eo int 1 run {S} get #x i.t",
      f"{S} operation #x i.t = @s i.dem", f"{S} operation #x i.t /= #10 i.g", f"execute store result storage {M_} ed int 1 run {S} get #x i.t",
      f"function {NS}:stats/e_titre with storage {M_}"]
fn("stats/e_titre", "$" + ap("\\n\\nÉNERGIE  $(eo) kW fournis / $(ed) kW demandés\\n", "aqua"))
EG += [f"{S} operation #ec i.t = @s i.off", f"execute if score @s i.dem < #ec i.t run {S} operation #ec i.t = @s i.dem"]
EG += barre("#ec i.t", "#mx i.t", "#5ff0e6", fond="#ff5a3a")
EG += [f"execute if score @s i.dem <= @s i.off run " + ap("\\n(tout est couvert : la barre rouge serait ce qui manque)", "dark_gray")]
fn("stats/energie", EG)

# ---- 4. ce qui freine tes revenus
cap = [f"execute if score @s i.halle matches {k} run {S} set #cap i.t {h[4]}" for k, h in enumerate(HALLE)]
PO = [f"{S} set #po i.t 0"]
for m in ML:
    d = MACH[m]
    tot = sum(d.get("out", {}).values())
    if tot and d["kw"] > 0:
        PO += [f"{S} operation #x i.t = @s i.q_{m}", f"{S} set #y i.t {tot}", f"{S} operation #x i.t *= #y i.t", f"{S} operation #x i.t /= #100 i.g",
               f"{S} operation #po i.t += #x i.t"]
fn("stats/conseils", PO + cap + [
    f"execute store result storage {M_} po int 1 run {S} get #po i.t", f"execute store result storage {M_} cap int 1 run {S} get #cap i.t",
    ap("\\n\\nÀ AMÉLIORER", "red"), f"{S} set #ok i.t 0",
    f"execute if score @s i.fe matches ..999 run {S} set #ok i.t 1",
    f"execute if score @s i.fe matches ..999 run " + ap("\\n• Énergie trop faible : ajoute une Chaudière (+150 kW).", "white"),
    f"execute if score #po i.t > #cap i.t run {S} set #ok i.t 1",
    f"execute if score #po i.t > #cap i.t run function {NS}:stats/cons_halle with storage {M_}",
    f"execute if score #ok i.t matches 0 run " + ap("\\n• Rien, tout tourne à plein.", "green")])
fn("stats/cons_halle", "$" + ap("\\n• Halle pleine : $(po) objets/h produits, $(cap) vendus. Agrandis-la.", "white"))
ST.append(f"function {NS}:stats/conseils")
ST.append(f"function {NS}:menu/stats_d with storage {M_}")
fn("menu/stats", ST)
fn("menu/stats_d", "$" + dlg(T("MON ÎLE", OR, True),
    [msg(L(T("Aujourd'hui : ", "gray"), T("$(jn) Écus", OR, True), T("  ·  Nexus : $(st) objets", "gray")), 320),
     '{type:"minecraft:plain_message",width:320,contents:$(l)}'],
    [btn(T("Menu de l'industrie", "green", True), 1, 150), btn(T("Vendre et contrats", OR), 7, 150),
     btn(T("Acheter une machine", OR), 4, 150), btn(T("Actualiser", "aqua"), 22, 150)], 2))

# ---- panneau vivant au-dessus du Nexus : recettes du jour, dernière heure, énergie (mis à jour toutes les 5 s quand le joueur est sur son île)
H_HOLO = round(h_lab("nexus", BAT["nexus"][2]) + 1.4 - 1.5 * BAT["nexus"][2], 1)
fn("ile/holo", [f"{S} operation #me i.t = @s m.id", val("jn", "i.jn"), val("h1", "i.h1"), val("h0", "i.h0"),
                f"{S} operation #x i.t = @s i.fe", f"{S} operation #x i.t /= #10 i.g", f"execute store result storage {M_} fep int 1 run {S} get #x i.t",
                f"execute as @e[type=minecraft:item_display,tag=ind.b_nexus,distance=..96] if score @s i.own = #me i.t at @s positioned ~ ~{H_HOLO} ~ run function {NS}:ile/holo_m with storage {M_}"])
fn("ile/holo_m", [
    'execute unless entity @e[type=minecraft:text_display,tag=ind.holo,distance=..1.5] run summon minecraft:text_display ~ ~ ~ {Tags:["ind.holo"],billboard:"center",'
    'view_range:0.8f,shadow:true,background:1426063360,line_width:220,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.6f,0.6f,0.6f]}}',
    '$data merge entity @e[type=minecraft:text_display,tag=ind.holo,distance=..1.5,limit=1] {text:[{"text":"Aujourd\'hui : ","color":"gray"},{"text":"$(jn) Écus","color":"#F7C843","bold":true},'
    '{"text":"\\nCette heure : ","color":"gray"},{"text":"$(h0)","color":"#4cd964"},{"text":"   heure passée : $(h1)","color":"gray"},'
    '{"text":"\\nÉnergie : ","color":"gray"},{"text":"$(fep) %","color":"aqua"}]}'])

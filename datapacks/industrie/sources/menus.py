# -*- coding: utf-8 -*-
# Menus (dialogues) et aiguillage du déclencheur /trigger industrie. Exécuté par datapack.py en dernier.
OR = "#F7C843"
M_ = f"{NS}:m"                                     # storage des valeurs affichées (racine = arguments de macro)


def val(cle, score, qui="@s"):
    return f"execute store result storage {M_} {cle} int 1 run {S} get {qui} {score}"


def nav(*items):
    return [btn(T(t, c), v, 120) for t, c, v in items]


NAV = nav(("Retour", "white", 1))   # 28/11/2026 : un seul bouton de retour, trop de boutons partout

# ---------------------------------------------------------------- aiguillage
TR = [f"{S} operation #v i.t = @s industrie", f"{S} set @s industrie 0",
      f"execute unless score @s i.vu matches 1 run function {NS}:joueur/init",
      f"execute store result score #now i.g run time query gametime"]
SIMPLE = {20: "menu/plus_o", 18: "menu/route", 19: "cine/revoir", 12: "menu/guide", 13: "menu/guide_13", 14: "menu/guide_14", 15: "menu/guide_15", 16: "menu/guide_16", 17: "menu/guide_17",
          1: "menu/accueil", 2: "ile/aller", 3: "ile/retour", 4: "menu/comptoir", 5: "menu/cadastre", 6: "menu/banque", 7: "menu/halle",
          8: "menu/labo", 9: "menu/bureau", 10: "menu/visites", 11: "menu/parts", 301: "machine/ameliorer", 302: "machine/revendre",
          500: "banque/emprunter", 501: "banque/rembourser", 530: "halle/ameliorer", 540: "tube/ameliorer", 550: "banque/acheter",
          570: "rang/passer", 571: "oeuvre/elever", 580: "parts/vendre", 582: "parts/racheter", 583: "parts/retirer"}
TR += [f"execute if score #v i.t matches {v} run return run function {NS}:{f}" for v, f in SIMPLE.items()]
TR += [f"execute if score #v i.t matches {100 + k} run return run function {NS}:machine/acheter_{k}" for k in range(len(ML))]
TR += [f"execute if score #v i.t matches 200..248 run return run function {NS}:parcelle/aiguille"]
TR += [f"execute if score #v i.t matches {510 + c} run return run function {NS}:contrat/livrer_{c}" for c in (1, 2, 3)]
TR += [f"execute if score #v i.t matches {560 + b} run return run function {NS}:labo/chercher_{b}" for b in range(1, 5)]
TR += [f"execute if score #v i.t matches 1000..{1000 + 10 * len(PL)} run return run function {NS}:menu/produit_aiguille",
       f"execute if score #v i.t matches 8000..8999 run return run function {NS}:ile/visiter",
       f"execute if score #v i.t matches 600000..999999 run return run function {NS}:parts/acheter"]
fn("trigger", TR)
fn("parcelle/aiguille", [f"execute if score #v i.t matches {200 + k} run return run function {NS}:parcelle/acheter_{k}" for k in range(49)])
PA = [f"{S} operation #pi i.t = #v i.t", f"{S} remove #pi i.t 1000", f"{S} operation #pa i.t = #pi i.t", f"{S} operation #pa i.t %= #10 i.g",
      f"{S} operation #pi i.t /= #10 i.g"]
for k, p in enumerate(PL):
    c = f"execute if score #pi i.t matches {k}"
    PA += [f"{c} if score #pa i.t matches 0 run return run function {NS}:menu/produit_{p}"]
    PA += [f"{c} if score #pa i.t matches {a} run return run function {NS}:banque/o_{p}_{a}" for a in range(1, 6)]
    PA += [f"{c} if score #pa i.t matches 6 run return run function {NS}:banque/plus_{p}", f"{c} if score #pa i.t matches 7 run return run function {NS}:banque/moins_{p}"]
    if PROD[p][1]:
        PA += [f"{c} if score #pa i.t matches 8 run return run function {NS}:banque/retirer_{p}"]
fn("menu/produit_aiguille", PA)

# ---------------------------------------------------------------- tableau de bord (1)
AC = [f"execute unless score @s i.ile matches 0.. run return run function {NS}:menu/bienvenue",
      val("ri", "i.ri"), val("ctr", "i.ctr"), val("jn", "i.jn"), val("r7", "i.r7"), val("np", "i.np"), val("fe", "i.fe"), val("go", "i.go"),
      f"{S} operation #x i.t = @s i.off", f"{S} operation #x i.t /= #10 i.g", f"execute store result storage {M_} off int 1 run {S} get #x i.t",
      f"{S} operation #x i.t = @s i.dem", f"{S} operation #x i.t /= #10 i.g", f"execute store result storage {M_} dem int 1 run {S} get #x i.t",
      f"{S} set #x i.t 0"] + [f"{S} operation #x i.t += @s i.n_{m}" for m in ML] + [
      f"execute store result storage {M_} nm int 1 run {S} get #x i.t",
      f"{S} set #x i.t 0"] + [f"{S} operation #x i.t += @s i.s_{p}" for p in PL] + [
      f"execute store result storage {M_} st int 1 run {S} get #x i.t",
      f"{S} operation #x i.t = @s i.fe", f"{S} operation #x i.t /= #10 i.g", f"execute store result storage {M_} fep int 1 run {S} get #x i.t",
      f'data modify storage {M_} rang set value "Atelier"'] + [
      f'execute if score @s i.rang matches {r} run data modify storage {M_} rang set value "{RANGS[r][0]}"' for r in range(2, 6)] + [
      f'data modify storage {M_} ev set from storage {NS}:g ev', f'execute unless data storage {NS}:g ev run data modify storage {M_} ev set value "Marché calme."',
      f"function {NS}:tuto/objectif", f"function {NS}:menu/accueil_d with storage {M_}"]
fn("menu/accueil", AC)
fn("menu/accueil_d", "$" + dlg(
    L(T("MON INDUSTRIE", OR, True), T("  ·  $(rang)", "white")),
    [msg(L(T("À faire : ", "green", True), T("$(obj)", "white"),
           T("\\n\\nAujourd'hui : $(jn) Écus  ·  Nexus : $(st) objets  ·  Énergie : $(fep) %", "gray")), 300)],
    [btn(T("Que faire ?", "green", True), 18, 200), btn(T("Acheter une machine", OR, True), 4, 200),
     btn(T("Vendre et contrats", OR), 7, 200), btn(T("Autres menus", "gray"), 20, 200)], 1))
fn("menu/plus", ["$" + dlg(T("AUTRES MENUS", OR, True), [],
    [btn(T("Cadastre (parcelles)", "white"), 5, 160), btn(T("Bureau (rangs)", "light_purple"), 9, 160),
     btn(T("$(lb)", "$(kb)"), 6, 160), btn(T("$(ll)", "$(kl)"), 8, 160), btn(T("$(lp)", "$(kp)"), 11, 160),
     btn(T("Visiter une île", "gray"), 10, 160), btn(T("Guide", "green"), 12, 160), btn(T("Revenir au monde", "white"), 3, 160),
     btn(T("Retour", "white"), 1, 160)], 2)])
fn("menu/bienvenue", dlg(T("L'ARCHIPEL DES USINES", OR, True),
                         [msg(L(T("Tu reçois une île avec une Carrière déjà en marche. Tes machines produisent, la Halle vend, tu gagnes des Écus.\\n\\n", "white"),
                                T("Un parcours de 6 étapes te guide, avec des Écus à chaque étape.", "green")), 300)],
                         [btn(T("Créer mon île et y aller", "green", True), 2, 200), btn(T("Lire le guide", "white"), 12, 140)], 2))

# ---------------------------------------------------------------- comptoir des machines (4)
CO = [f'data modify storage {M_} c set value []']
for k, m in enumerate(ML):
    d = MACH[m]
    lab = f'{d["nom"]}  ·  {fe(d["prix"])}' + (f' + {d["ecl"]} éclats' if d["ecl"] else "")
    tip = f'{RANGS[d["rang"]][0]}. {prod_txt(m, 1)}. {abs(d["kw"])} kW {"fournis" if d["kw"] < 0 else "consommés"}.' + (
        " Tiens un spawner du Commerce en main." if m == "spawner" else "") + (" Demande une étoile du Nether." if d.get("etoile") else "")
    ok = btn(T(lab, OR if d["rang"] >= 4 else ("aqua" if d["rang"] == 3 else ("green" if d["rang"] == 2 else "white")), True), 100 + k, 200, tip)
    ko = btn(L(T("BLOQUÉ ", "red", True), T(f'{d["nom"]} : rang {RANGS[d["rang"]][0]}', "dark_gray")), 100 + k, 200, "Débloqué au rang " + RANGS[d["rang"]][0] + ". " + tip)
    CO += [f"execute if score @s i.rang matches {d['rang']}.. run data modify storage {M_} c append value {ok}",
           f"execute if score @s i.rang matches {d['rang'] - 1} run data modify storage {M_} c append value {ko}"]   # seulement le rang suivant
CO += [f"data modify storage {M_} c append value {x}" for x in NAV] + [f"function {NS}:menu/comptoir_d with storage {M_}"]
fn("menu/comptoir", CO)
fn("menu/comptoir_d", '$dialog show @s {type:"minecraft:multi_action",title:' + T("COMPTOIR DES MACHINES", OR, True) +
   ',can_close_with_escape:true,pause:false,body:[' + msg(T("Achat posé sur l'emplacement libre le plus proche de toi (sur ton île). Survole une machine pour ses détails.", "gray")) +
   '],actions:$(c),columns:2}')

# ---------------------------------------------------------------- cadastre (5) : grille 7 x 7
CA = [f'data modify storage {M_} c set value []']
for idx in range(49):
    i, j = idx % 7, idx // 7
    ring = max(abs(i - 3), abs(j - 3))
    prix = ANNEAUX[ring][1]
    lab_ok = btn(T("■", "green", True), 200 + idx, 40, "À toi")
    lab_lib = btn(T(fe(prix).replace(" M", "M").replace(" ", ""), OR), 200 + idx, 40, f"Anneau {ring} : {mille(prix)} Écus" + (" + 5 éclats" if ring == 3 else "") + ". Doit toucher une de tes parcelles.")
    CA += [f"execute if score @s i.p{idx} matches 1 run data modify storage {M_} c append value {lab_ok}",
           f"execute unless score @s i.p{idx} matches 1 run data modify storage {M_} c append value {lab_lib}"]
CA += [val("np", "i.np"), f"{S} set #x i.t 0"] + [f"execute if score @s i.rang matches {r} run {S} set #x i.t {PARC_MAX[r]}" for r in range(1, 6)] + [
       f"execute store result storage {M_} max int 1 run {S} get #x i.t", f"function {NS}:menu/cadastre_d with storage {M_}"]
fn("menu/cadastre", CA)
fn("menu/cadastre_d", '$dialog show @s {type:"minecraft:multi_action",title:' + T("CADASTRE DE L'ÎLE", OR, True) +
   ',can_close_with_escape:true,pause:false,body:[' + msg(L(T("Parcelles : $(np) (ton rang en permet $(max)). Clique un prix pour acheter : 32 x 32 blocs, 4 emplacements de machine.", "gray"))) +
   '],actions:$(c),columns:7,exit_action:{label:' + T("Mon industrie", "white") + ',width:120,action:{type:"run_command",command:"trigger industrie set 1"}}}')

# ---------------------------------------------------------------- Halle du Marché (7)
HA = [val("hl", "i.halle")] + [f'execute if score @s i.halle matches {k} run data modify storage {M_} h set value {{nom:"{h[0]}",cap:"{mille(h[4])}",com:"{h[5]}",'
                                f'nx:"{(HALLE[k + 1][0] + " : " + mille(HALLE[k + 1][2]) + " Écus" + (f" + {HALLE[k + 1][3]} éclats" if HALLE[k + 1][3] else "") + ", rang " + RANGS[HALLE[k + 1][1]][0]) if k + 1 < len(HALLE) else "niveau maximal"}"}}'
                                for k, h in enumerate(HALLE)]
# 28/11/2026 : Halle réécrite pour qu'on comprenne ce qu'est un contrat et ce qu'il faut faire
for c in (1, 2, 3):
    r_ = next(r for r in range(1, 6) if CONTRATS_JOUR[r] >= c)
    HA += [f'data modify storage {M_} h.c{c} set value "Débloqué au rang {RANGS[r_][0]}."', f'data modify storage {M_} h.k{c} set value "dark_gray"',
           f'data modify storage {M_} h.b{c} set value "Contrat {c} : rang {RANGS[r_][0]}"', f'data modify storage {M_} h.e{c} set value ""', f'data modify storage {M_} h.n{c} set value ""', f'data modify storage {M_} h.t{c} set value ""']
    for k, p in enumerate(PL):
        HA += [f"execute if score @s i.c{c}p matches {k + 1} run {S} set @s i.c{c}q {CQ[p]}", f"execute if score @s i.c{c}p matches {k + 1} run {S} set @s i.c{c}r {CR[p]}"]
        HA += [f'execute if score @s i.c{c}p matches {k + 1} run data modify storage {M_} h.c{c} set value "{mille(CQ[p])} {PROD[p][0].lower()}, payé {mille(CR[p])} Écus"',
               f"execute if score @s i.c{c}p matches {k + 1} store result storage {M_} h.n{c} int 1 run {S} get @s i.s_{p}",
               f'execute if score @s i.c{c}p matches {k + 1} run data modify storage {M_} h.t{c} set value "  · tu as "',
               f"execute if score @s i.c{c}p matches {k + 1} if score @s i.s_{p} >= @s i.c{c}q run data modify storage {M_} h.k{c} set value \"green\"",
               f"execute if score @s i.c{c}p matches {k + 1} unless score @s i.s_{p} >= @s i.c{c}q run data modify storage {M_} h.k{c} set value \"red\""]
    HA += [f"execute if score @s i.c{c}p matches 1.. run data modify storage {M_} h.b{c} set value \"Livrer le contrat {c}\"",
           f'execute if score @s i.c{c}f matches 1 run data modify storage {M_} h.e{c} set value "  (livré)"',
           f'execute if score @s i.c{c}f matches 1 run data modify storage {M_} h.k{c} set value "gray"',
           f'execute if score @s i.c{c}f matches 1 run data modify storage {M_} h.b{c} set value "Contrat {c} livré"']
HA += [f'data modify storage {M_} h.ev set from storage {NS}:g ev', f'execute unless data storage {NS}:g ev run data modify storage {M_} h.ev set value "Marché calme."',
       f"{S} operation #x i.t = @s i.rang", f"{S} set #y i.t 200", f"{S} operation #x i.t *= #y i.t", f"execute store result storage {M_} h.rep int 1 run {S} get #x i.t",
       f"function {NS}:menu/halle_d with storage {M_} h"]
HA += [f"data modify storage {M_} h.a set value []"]
for c in (1, 2, 3):
    HA += [f"execute if score @s i.c{c}p matches 1.. unless score @s i.c{c}f matches 1 run function {NS}:menu/halle_bt{c} with storage {M_} h"]
    fn(f"menu/halle_bt{c}", "$" + f"data modify storage {M_} h.a append value " + btn(T(f"$(b{c})", f"$(k{c})", True), 510 + c, 150))
HA += [f"data modify storage {M_} h.a append value " + btn(T("Agrandir la Halle", OR), 530, 150), f"data modify storage {M_} h.a append value " + btn(T("Retour", "white"), 1, 150)]
HA = [f"function {NS}:tuto/halle"] + HA
fn("menu/halle", HA)
fn("menu/halle_d", "$" + dlg(
    T("HALLE DU MARCHÉ", OR, True),
    [msg(L(T("$(nom)", OR, True), T(" vend ton stock toute seule : $(cap) objets par heure, $(com) % de commission.", "gray"),
           T("\\nBourse : $(ev)", "yellow")), 300),
     msg(L(T("CONTRATS DU JOUR", "light_purple", True), T("  (livre d'un coup, payé 1,5 fois, + $(rep) réputation)", "gray"),
           T("\\n1. $(c1)$(e1)", "white"), T("$(t1)", "gray"), T("$(n1)", "$(k1)"),
           T("\\n2. $(c2)$(e2)", "white"), T("$(t2)", "gray"), T("$(n2)", "$(k2)"),
           T("\\n3. $(c3)$(e3)", "white"), T("$(t3)", "gray"), T("$(n3)", "$(k3)"),
           T("\\nLa Halle met de côté ce qu'il faut. Vert : livrable.", "gray")), 300),
     msg(L(T("Agrandir : $(nx)", "gray")), 300)],
    ["ACTIONS"], 2))

# ---------------------------------------------------------------- Banque (6)
BQ = [f"execute unless score @s i.bq matches 1 run return run function {NS}:menu/banque_offre",
      val("dette", "i.dette"), val("r7", "i.r7"), f'data modify storage {M_} c set value []',
      f'data modify storage {M_} pr set value "Aucun prêt."',
      f"execute if score @s i.dette matches 1.. run function {NS}:menu/banque_pret"]
ORD = ["vendre", "garder", "plancher", "étaler", "réserver"]
for k, p in enumerate(PL):
    BQ += [f"execute if score @s i.s_{p} matches 1.. run function {NS}:menu/bq_ligne_{p}"]
    fn(f"menu/bq_ligne_{p}", [val("q", f"i.s_{p}")] + [f'execute if score @s i.o_{p} matches {a} run data modify storage {M_} o set value "{o}"' for a, o in enumerate(ORD)] +
       [f"function {NS}:menu/bq_ligne_{p}_m with storage {M_}"])
    fn(f"menu/bq_ligne_{p}_m", f"$data modify storage {M_} c append value " + btn(L(T(f"{PROD[p][0]} ", "white", True), T("$(q)", OR), T("  · $(o)", "gray")), 1000 + 10 * k, 200))
BQ += [f"data modify storage {M_} c append value {x}" for x in [btn(T("Emprunter", "aqua", True), 500, 200), btn(T("Rembourser", "white"), 501, 200)] + NAV]
BQ += [f"function {NS}:menu/banque_d with storage {M_}"]
fn("menu/banque", BQ)
fn("menu/banque_pret", [val("pj", "i.pj"), f"function {NS}:menu/banque_pret_m with storage {M_}"])
fn("menu/banque_pret_m", f'$data modify storage {M_} pr set value "Prêt : $(dette) Écus à rembourser (jour $(pj) sur {PRET_JOURS})."')
fn("menu/banque_d", '$dialog show @s {type:"minecraft:multi_action",title:' + T("BANQUE DE L'ARCHIPEL", "aqua", True) +
   ',can_close_with_escape:true,pause:false,body:[' + msg(L(T("Clique un produit pour choisir : vendre, garder, plancher de prix, étaler ou réserver. "
                                                             "Garder coûte 0,2 % par jour de la valeur.\\n", "gray"), T("$(pr)", OR),
                                                           T(f"\\nPrêt possible : 3 jours de recettes (moyenne $(r7) / jour), frais {PRET_FRAIS} %, remboursé par {PRET_PART} % de tes ventes.", "gray")), 400) +
   '],actions:$(c),columns:2}')
fn("menu/banque_offre", dlg(T("BANQUE DE L'ARCHIPEL", "aqua", True),
                            [msg(L(T(f"Au rang Manufacture, la Banque ({mille(BANQUE_PRIX)} Écus) te laisse choisir produit par produit ce que tu gardes, "
                                     "vends à un prix plancher, étales ou réserves, et ouvre les prêts industriels.", "gray")), 360)],
                            [btn(T(f"Construire la Banque ({fe(BANQUE_PRIX)})", "aqua", True), 550, 220)] + NAV, 2))
# fiche d'un produit
for k, p in enumerate(PL):
    nom, item, p0, S0 = PROD[p]
    FP = [val("q", f"i.s_{p}"), val("j", f"i.j_{p}"), val("x", f"i.x_{p}"), val("w", f"i.w_{p}"),
          f"{S} set #S i.t {S0}", f"{S} operation #sb i.t = @s i.b1", f"{S} set #y i.t 25", f"{S} operation #sb i.t *= #y i.t", f"{S} add #sb i.t 100",
          f"{S} operation #S i.t *= #sb i.t", f"{S} operation #S i.t /= #100 i.g",
          f"{S} operation #pct i.t = #S i.t", f"{S} operation #pct i.t *= #100 i.g", f"{S} operation #den i.t = #S i.t", f"{S} operation #den i.t += @s i.v_{p}",
          f"{S} operation #pct i.t /= #den i.t", f"execute store result storage {M_} pct int 1 run {S} get #pct i.t",
          f"{S} operation #x i.t = #pct i.t", f"{S} set #y i.t {p0}", f"{S} operation #x i.t *= #y i.t", f"{S} operation #x i.t /= #10000 i.g",
          f"execute store result storage {M_} prix int 1 run {S} get #x i.t"]
    FP += [f'execute if score @s i.o_{p} matches {a} run data modify storage {M_} o set value "{o}"' for a, o in enumerate(ORD)]
    FP += [f'data modify storage {M_} par set value ""',
           f"execute if score @s i.o_{p} matches 2 run function {NS}:menu/par_2 with storage {M_}",
           f"execute if score @s i.o_{p} matches 3 run function {NS}:menu/par_3 with storage {M_}",
           f"execute if score @s i.o_{p} matches 4 run function {NS}:menu/par_4 with storage {M_}",
           f"function {NS}:menu/produit_{p}_d with storage {M_}"]
    fn(f"menu/produit_{p}", FP)
    acts = [btn(T(o.capitalize(), ("green", "aqua", OR, "light_purple", "gold")[a], True), 1000 + 10 * k + a + 1, 90) for a, o in enumerate(ORD)]
    acts += [btn(T("+", "white", True), 1000 + 10 * k + 6, 90, "Plancher +10 %, ou quantité x2"), btn(T("-", "white", True), 1000 + 10 * k + 7, 90, "Plancher -10 %, ou quantité /2")]
    if item:
        acts += [btn(T(f"Retirer {RETRAIT_JOUR}", "gray"), 1000 + 10 * k + 8, 120, f"{RETRAIT_JOUR} par jour gratuits, au-delà 4 fois le prix du Commerce. Le Commerce ne les rachète pas.")]
    acts += [btn(T("Banque", "aqua"), 6, 90)]
    fn(f"menu/produit_{p}_d", "$" + dlg(T(nom.upper(), OR, True),
        [msg(L(T("Au Nexus : ", "gray"), T("$(q)", "white", True), T("   ·   vendus aujourd'hui : $(j)   ·   retirés : $(w)", "gray"),
               T("\\nPrix du moment : ", "gray"), T("$(prix) Écus", OR, True), T(" ($(pct) % de la base)", "gray"),
               T("\\nOrdre : ", "gray"), T("$(o)", "aqua", True), T("$(par)", "aqua")), 380)], acts, 5))

fn("menu/par_2", f'$data modify storage {M_} par set value " à $(x) % du prix de base au moins"')
fn("menu/par_3", f'$data modify storage {M_} par set value " : $(x) par jour au plus"')
fn("menu/par_4", f'$data modify storage {M_} par set value " : $(x) toujours gardés"')

# ---------------------------------------------------------------- Laboratoire (8)
LA = [f"execute unless score @s i.rang matches 2.. run return run " + say("Le Laboratoire s'ouvre au rang Manufacture.", "red")]
LA += [val(f"b{b}", f"i.b{b}") for b in range(1, 5)] + [f'data modify storage {M_} rc set value "Aucune recherche en cours."']
LA += [f'execute if score @s i.rb matches {b} run data modify storage {M_} rc set value "En cours : {BRANCHES[b - 1][1]} (1 h de jeu)."' for b in range(1, 5)]
LA += [f"function {NS}:menu/labo_d with storage {M_}"]
fn("menu/labo", LA)
fn("menu/labo_d", "$" + dlg(T("LABORATOIRE", "light_purple", True),
    [msg(L(*[T(f"{nom} : niveau $(b{b}) / 10", "white", True) if False else T(f"{nom} : niv. $(b{b})/10  ·  {effet}\\n", "white") for b, (cle, nom, effet, *_r) in enumerate(BRANCHES, 1)],
           T("\\n$(rc)", "aqua"), T("\\nCoût : Écus et ressources du Nexus, x2,2 et x2 à chaque niveau. Les niveaux 6 à 10 demandent le rang Consortium.", "gray")), 400)],
    [btn(T(nom, "light_purple", True), 560 + b, 180, effet) for b, (cle, nom, effet, *_r) in enumerate(BRANCHES, 1)] + NAV, 2))

# ---------------------------------------------------------------- Bureau de l'île (9) : rangs, Grands Œuvres, tubes, Banque
BU = [val("ri", "i.ri"), val("ctr", "i.ctr"), val("go", "i.go"), val("kwi", "i.kwi")]
BU += [f'execute if score @s i.rang matches {r} run data modify storage {M_} r set value "{RANGS[r][0]}"' for r in range(1, 6)]
for r in range(1, 5):
    nom, ri, ctr, prix, ecl, cond = RANGS[r + 1]
    req = f"{nom} : {mille(ri)} RI, {ctr} contrats, {fe(prix)} Écus" + (f", {ecl} éclats" if ecl else "") + \
        {"boss": ", 1 boss de Métiers", "wither": ", 3 Wither", "dragon": ", l'Ender Dragon", None: ""}[cond]
    BU.append(f'execute if score @s i.rang matches {r} run data modify storage {M_} nx set value "{req}"')
BU += [f'execute if score @s i.rang matches 5 run data modify storage {M_} nx set value "Tu es au sommet : Empire."',
       f'data modify storage {M_} tu set value "{TUBES[0][0]}"'] + [f'execute if score @s i.tube matches {k} run data modify storage {M_} tu set value "{t[0]}"' for k, t in enumerate(TUBES)]
BU += [f"function {NS}:menu/bureau_d with storage {M_}"]
fn("menu/bureau", BU)
fn("menu/bureau_d", "$" + dlg(T("BUREAU DE L'ÎLE", "light_purple", True),
    [msg(L(T("Rang : ", "gray"), T("$(r)", OR, True), T("   ·   réputation $(ri)   ·   contrats $(ctr)   ·   Wither $(kwi)", "gray"),
           T("\\nRang suivant : $(nx)", "white"),
           T("\\n\\nGrands Œuvres : $(go) / 8 (+8 % de production chacun, dès le rang Consortium)", OR),
           T("\\nTubes : $(tu) (cuivre 500, or 2 500, cristal 10 000 objets par minute et par machine)", "aqua")), 400)],
    [btn(T("Passer au rang suivant", OR, True), 570, 180), btn(T("Élever un Grand Œuvre", OR), 571, 180),
     btn(T("Changer tous les tubes", "aqua"), 540, 180, "Or : 25 000 par machine (rang Manufacture). Cristal : 250 000 et 1 éclat par machine (rang Consortium)."),
     btn(T("Banque", "aqua"), 6, 180)] + NAV, 2))

# ---------------------------------------------------------------- parts d'île (11)
PT = [val("pv", "i.pv"), val("ph", "i.ph"), f'data modify storage {M_} c set value []',
      f"data modify storage {NS}:t W set from storage {NS}:parts offres", f"{S} set #nn i.t 0", f"function {NS}:menu/parts_boucle"]
PT += [f"data modify storage {M_} c append value {x}" for x in [btn(T("Vendre une part", OR, True), 580, 200), btn(T("Racheter une part", "white"), 582, 200),
                                                                   btn(T("Retirer mes offres", "gray"), 583, 200)] + NAV]
PT += [f"function {NS}:menu/parts_d with storage {M_}"]
fn("menu/parts", PT)
fn("menu/parts_boucle", [f"execute unless data storage {NS}:t W[0] run return 0", f"execute if score #nn i.t matches 12.. run return 0",
                         f"{S} add #nn i.t 1", f"execute store result score #k i.t run data get storage {NS}:t W[0].k", f"{S} add #k i.t 600000",
                         f"execute store result storage {NS}:t W[0].v int 1 run {S} get #k i.t",
                         f"function {NS}:menu/parts_m with storage {NS}:t W[0]", f"data remove storage {NS}:t W[0]", f"function {NS}:menu/parts_boucle"])
fn("menu/parts_m", f"$data modify storage {M_} c append value " + btn(L(T("Île de $(nom)  ", "white", True), T("$(p) Écus", OR)), "$(v)", 200, "Acheter cette part (+5 % de taxe)"))
fn("menu/parts_d", '$dialog show @s {type:"minecraft:multi_action",title:' + T("PARTS D'ÎLE", "light_purple", True) +
   ',can_close_with_escape:true,pause:false,body:[' + msg(L(T("Une part touche chaque jour 2 % des recettes nettes de l'île. Tu as vendu $(pv) parts de ton île et tu en détiens $(ph). "
                                                             "Rachat de tes parts : prix d'achat + 10 %.", "gray")), 400) + '],actions:$(c),columns:2}')

# ---------------------------------------------------------------- visites (10)
fn("menu/visites", [f'data modify storage {M_} c set value []', f"execute as @a[scores={{i.ile=0..}}] run function {NS}:menu/visite_un",
                    f"data modify storage {M_} c append value " + btn(T("Mon industrie", "white"), 1, 200), f"function {NS}:menu/visites_d with storage {M_}"])
fn("menu/visite_un", ["function commerce:joueur/nom_moi", f"data modify storage {NS}:t vi.nom set from storage commerce:t moi",
                      f"{S} operation #x i.t = @s i.ile", f"{S} add #x i.t 8000", f"execute store result storage {NS}:t vi.v int 1 run {S} get #x i.t",
                      f"function {NS}:menu/visite_m with storage {NS}:t vi"])
fn("menu/visite_m", f"$data modify storage {M_} c append value " + btn(T("Île de $(nom)", "green"), "$(v)", 200))
fn("menu/visites_d", '$dialog show @s {type:"minecraft:multi_action",title:' + T("VISITER UNE ÎLE", "green", True) +
   ',can_close_with_escape:true,pause:false,body:[' + msg(T("Les îles des joueurs connectés. En visite, tu es en mode aventure.", "gray")) + '],actions:$(c),columns:2}')

# ---------------------------------------------------------------- clic sur un bâtiment
fn("batiment/clic", [f"{S} operation #co i.t = @s i.own", f"{S} operation #cm i.t = @s i.mt",
                     f"execute if entity @s[tag=ind.ret] run return run function {NS}:batiment/retour_clic",
                     f"execute on target run function {NS}:batiment/clic_j", "data remove entity @s interaction", "data remove entity @s attack"])
fn("batiment/retour_clic", [f"execute on target run function {NS}:ile/retour", "data remove entity @s interaction", "data remove entity @s attack"])
fn("batiment/clic_j", [f"execute unless score @s m.id = #co i.t run return run " + say("Ce bâtiment appartient à une autre île.", "gray"),
                       f"execute if score #cm i.t matches 90 run return run function {NS}:menu/accueil",
                       f"execute if score #cm i.t matches 91 run return run function {NS}:menu/halle",
                       f"execute if score #cm i.t matches 92 run return run function {NS}:menu/banque",
                       f"execute if score #cm i.t matches 93 run return run function {NS}:menu/labo",
                       f"execute if score #cm i.t matches 94 run return run function {NS}:menu/bureau"])

fn("version", say(f"Industrie version {VERSION} : îles, {len(ML)} machines, tubes à faisceau, Halle du Marché, Banque, Laboratoire, rangs, Grands Œuvres, parts d'île.", OR))

fn("menu/plus_o", [
      f'data modify storage {M_} lb set value "Banque (bloqué)"', f'data modify storage {M_} kb set value "dark_gray"',
      f'execute if score @s i.rang matches 2.. run data modify storage {M_} lb set value "Banque"', f'execute if score @s i.rang matches 2.. run data modify storage {M_} kb set value "aqua"',
      f'data modify storage {M_} ll set value "Laboratoire (bloqué)"', f'data modify storage {M_} kl set value "dark_gray"',
      f'execute if score @s i.rang matches 2.. run data modify storage {M_} ll set value "Laboratoire"', f'execute if score @s i.rang matches 2.. run data modify storage {M_} kl set value "light_purple"',
      f'data modify storage {M_} lp set value "Parts d\'île (bloqué)"', f'data modify storage {M_} kp set value "dark_gray"',
      f'execute if score @s i.rang matches 4.. run data modify storage {M_} lp set value "Parts d\'île"', f'execute if score @s i.rang matches 4.. run data modify storage {M_} kp set value "light_purple"',
      f"function {NS}:menu/plus with storage {M_}"])

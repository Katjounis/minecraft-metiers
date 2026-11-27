# Modèle d'équilibre utilisé pour régler tables.py (simulation jour par jour d'un joueur qui investit au mieux).
"""Modèle d'équilibre du tycoon Industrie (valeurs de base = prix de vente du Commerce)."""
import math, copy

# produit : (nom, prix de base p0, volume de saturation S0 par jour et par joueur)
PROD = {
    "pierre": ("Pierre", 0.10, 60_000), "charbon": ("Charbon", 1.0, 12_000), "cuivre": ("Cuivre", 2.0, 8_000),
    "canne": ("Canne", 0.40, 30_000), "verrue": ("Verrues", 0.50, 20_000), "citrouille": ("Citrouille", 1.2, 10_000),
    "fer": ("Fer", 8.0, 4_000), "or": ("Or", 12.0, 3_000), "emeraude": ("Émeraude", 15.0, 4_000), "diamant": ("Diamant", 120.0, 1_500),
    "netherite": ("Netherite", 2600.0, 250),
    "acier": ("Acier", 30.0, 2_500), "elixir": ("Élixir", 40.0, 1_200), "mecanisme": ("Mécanisme", 220.0, 1_500),
    "bijou": ("Bijou", 450.0, 1_600), "relique": ("Relique", 18_000.0, 80),
}
LV_PROD = [1, 1.5, 2.2, 3.2, 4.5]
LV_KW = [1, 1.3, 1.7, 2.2, 2.8]
LV_COUT = [1, 2, 5, 12, 30]            # prix du passage au niveau k (k = 2..5) en multiple du prix d'achat
LV_ECL = [0, 0, 0, 1, 2]                # éclats du passage au niveau 4 et 5 en multiple des éclats d'achat (mini 3 et 6)

# machine : rang, prix, éclats, kW (négatif = produit de l'énergie), sorties / h, entrées / h
MACH = {
    "carriere":  dict(nom="Carrière automatique", rang=1, prix=30_000, ecl=0, kw=20, out={"pierre": 4000, "charbon": 800, "cuivre": 300}),
    "serre":     dict(nom="Serre hydroponique", rang=1, prix=45_000, ecl=0, kw=25, out={"canne": 3000, "verrue": 1000, "citrouille": 500}),
    "fourneau":  dict(nom="Haut-fourneau des Titans", rang=1, prix=120_000, ecl=0, kw=40, out={"fer": 400}),
    "chaudiere": dict(nom="Chaudière à charbon", rang=1, prix=20_000, ecl=0, kw=-150, inp={"charbon": 300}),
    "puits_or":  dict(nom="Puits de cristal : or", rang=2, prix=500_000, ecl=5, kw=80, out={"or": 1500}),
    "fonderie":  dict(nom="Fonderie", rang=2, prix=400_000, ecl=0, kw=70, out={"acier": 600}, inp={"fer": 600, "charbon": 1200}),
    "distill":   dict(nom="Distillerie alchimique", rang=2, prix=500_000, ecl=3, kw=50, out={"elixir": 400}, inp={"verrue": 800, "canne": 800, "citrouille": 200}),
    "lave":      dict(nom="Centrale à lave", rang=2, prix=350_000, ecl=0, kw=-600),
    "puits_dia": dict(nom="Puits de cristal : diamant", rang=3, prix=3_000_000, ecl=15, kw=200, out={"diamant": 300}),
    "puits_eme": dict(nom="Puits de cristal : émeraude", rang=3, prix=2_500_000, ecl=10, kw=150, out={"emeraude": 2000}),
    "atelier":   dict(nom="Atelier mécanique", rang=3, prix=3_000_000, ecl=10, kw=180, out={"mecanisme": 200}, inp={"acier": 400, "cuivre": 800}),
    "puits_net": dict(nom="Puits de cristal : netherite", rang=4, prix=18_000_000, ecl=40, kw=500, out={"netherite": 30}),
    "joaillerie":dict(nom="Joaillerie", rang=4, prix=12_000_000, ecl=25, kw=350, out={"bijou": 200}, inp={"or": 200, "diamant": 150, "emeraude": 200}),
    "coeur":     dict(nom="Cœur stellaire", rang=4, prix=12_000_000, ecl=20, kw=-3000),
    "forge":     dict(nom="Forge des reliques", rang=5, prix=40_000_000, ecl=60, kw=900, out={"relique": 12}, inp={"netherite": 8, "bijou": 24, "mecanisme": 24}),
}
# Halle du Marché : prix, éclats, rang, objets vendus / h, commission
HALLE = [("Échoppe", 0, 0, 1, 10_000, 0.12), ("Comptoir", 150_000, 0, 2, 25_000, 0.08),
         ("Halle", 2_500_000, 10, 3, 60_000, 0.05), ("Bourse impériale", 20_000_000, 40, 4, 200_000, 0.02)]
SAT_HALLE = [1, 1, 1.1, 1.25]   # la Halle et la Bourse impériale ouvrent des acheteurs en plus
# parcelles : anneau, nombre, prix, éclats
ANNEAUX = [(1, 8, 50_000, 0), (2, 16, 750_000, 0), (3, 24, 6_000_000, 5)]
SLOTS = 4
FACTEUR_SAT = 1.0          # réglage global des revenus (commande admin)
def max_copies(m, rang):
    d = MACH[m]
    if d["kw"] < 0: return 4 + rang          # bâtiments d'énergie
    return min(5, 2 + rang - d["rang"])
PARC_MAX = {1: 5, 2: 9, 3: 17, 4: 30, 5: 49}
# rangs : RI, contrats, prix, éclats, exigence de combat
RANGS = {2: (3_000, 3, 200_000, 0, None), 3: (25_000, 15, 2_000_000, 10, "1 boss de Métiers"),
         4: (150_000, 45, 12_000_000, 40, "3 Wither"), 5: (350_000, 90, 40_000_000, 100, "1 Ender Dragon")}
NOMS_RANG = {1: "Atelier", 2: "Manufacture", 3: "Industrie", 4: "Consortium", 5: "Empire"}
CONTRATS_JOUR = {1: 1, 2: 2, 3: 3, 4: 3, 5: 3}
BONUS_METIER = 1.20

def prix_parcelle(n):          # n = numéro de la parcelle achetée (2 = première payante)
    k = n - 1
    for a, nb, p, e in ANNEAUX:
        if k <= nb: return p, e
        k -= nb
    return None

def gain_vente(p0, S, deja, q):
    p0 = p0 * 2.0
    """Revenu de q unités quand deja ont été vendues dans les 24 h : intégrale de p0 S / (S + v)."""
    return p0 * S * math.log((S + deja + q) / (S + deja))

TRANCHES = [(5_000_000, 0.0), (12_000_000, 0.25), (10**12, 0.45)]   # entretien de l'empire : part prélevée par tranche de revenu journalier
def entretien(net):
    r, bas = 0.0, 0
    for haut, t in TRANCHES:
        if net > bas: r += (min(net, haut) - bas) * (1 - t)
        bas = haut
    return r

def journee(etat, heures):
    """Production d'une journée, transformation, ventes. Renvoie le revenu net, les quantités produites, la RI."""
    kw_dem = sum(MACH[m]["kw"] * LV_KW[l - 1] for m, l in etat["mach"] if MACH[m]["kw"] > 0)
    kw_off = -sum(MACH[m]["kw"] * LV_PROD[l - 1] for m, l in etat["mach"] if MACH[m]["kw"] < 0) + 60   # 60 kW offerts par le Nexus
    f_e = min(1.0, kw_off / kw_dem) if kw_dem else 1.0
    stock = {k: 0.0 for k in PROD}
    for m, l in etat["mach"]:
        d = MACH[m]
        if d["kw"] > 0 and "inp" not in d:
            for p, q in d.get("out", {}).items(): stock[p] += q * LV_PROD[l - 1] * f_e * BONUS_METIER * (1 + 0.08 * etat.get("oeuvre", 0)) * heures
    for m, l in etat["mach"]:   # chaudières : brûlent du charbon
        d = MACH[m]
        if m == "chaudiere": stock["charbon"] = max(0, stock["charbon"] - d["inp"]["charbon"] * LV_PROD[l - 1] * heures)
    ordre = ["fonderie", "distill", "atelier", "joaillerie", "forge"]
    for mm in ordre:
        for m, l in etat["mach"]:
            if m != mm: continue
            d = MACH[m]; cap = LV_PROD[l - 1] * f_e * BONUS_METIER * (1 + 0.08 * etat.get("oeuvre", 0)) * heures
            r = min([cap] + [stock[p] / (q) for p, q in d["inp"].items()])
            for p, q in d["inp"].items(): stock[p] -= q * r
            for p, q in d["out"].items(): stock[p] += q * r
    prod = dict(stock)
    # contrats : volume fixe (la moitié du seuil de saturation du produit), payés 1,5 x la base, sans saturation
    nb_c = CONTRATS_JOUR[etat["rang"]]
    gain_c = 0; ecl_c = 0; faits = 0
    cands = sorted((PROD[p][1] * PROD[p][2], p) for p in stock if stock[p] >= PROD[p][2] * 0.5 * FACTEUR_SAT)
    for v, p in reversed(cands[-nb_c:]):
        q = PROD[p][2] * 0.5 * FACTEUR_SAT; stock[p] -= q; faits += 1
        gain_c += 3.0 * PROD[p][1] * q; ecl_c += 1 if etat["rang"] >= 3 else 0
    nb_c = faits
    # ventes à la Bourse, limitées par la Halle
    h = HALLE[etat["halle"]]; capa = h[4] * 24 * etat.get("mult_halle", 1)
    brut = 0; vendus = 0
    for p in sorted(stock, key=lambda p: -PROD[p][1]):
        q = min(stock[p], capa - vendus)
        if q <= 0: continue
        S = PROD[p][2] * etat["sat"] * FACTEUR_SAT * SAT_HALLE[etat["halle"]]
        brut += gain_vente(PROD[p][1], S, 0, q); vendus += q
    net = brut * (1 - h[5]) + gain_c
    net = entretien(net)
    ri = brut / 250 + nb_c * 200 * etat["rang"]
    return net, ri, nb_c, ecl_c, f_e, prod, gain_c

def kw_bilan(etat):
    dem = sum(MACH[m]["kw"] * LV_KW[l - 1] for m, l in etat["mach"] if MACH[m]["kw"] > 0)
    off = -sum(MACH[m]["kw"] * LV_PROD[l - 1] for m, l in etat["mach"] if MACH[m]["kw"] < 0) + 60
    return off - dem

def avec_energie(etat, cout, ecl):
    """Complète un achat par les bâtiments d'énergie nécessaires (le plus puissant débloqué)."""
    e = etat
    for _ in range(6):
        if kw_bilan(e) >= 0: return e, cout, ecl
        manque = -kw_bilan(e)
        srcs = [m for m, d in MACH.items() if d["kw"] < 0 and d["rang"] <= e["rang"] and sum(1 for x, _ in e["mach"] if x == m) < max_copies(m, e["rang"])]
        if not srcs: return e, cout, ecl
        assez = [m for m in srcs if -MACH[m]["kw"] >= manque]
        src = min(assez, key=lambda m: MACH[m]["prix"]) if assez else max(srcs, key=lambda m: -MACH[m]["kw"])
        if len(e["mach"]) >= e["parc"] * SLOTS:
            if e["parc"] >= PARC_MAX[e["rang"]]: return e, cout, ecl
            pp = prix_parcelle(e["parc"] + 1); e = copy.deepcopy(e); e["parc"] += 1; cout += pp[0]; ecl += pp[1]
        e = copy.deepcopy(e); e["mach"].append((src, 1)); cout += MACH[src]["prix"]; ecl += MACH[src]["ecl"]
    return e, cout, ecl

def options(etat):
    return [(c2, e2c, e2, lab) for c, ec, e, lab in options0(etat) for (e2, c2, e2c) in [avec_energie(e, c, ec)]]

def options0(etat):
    """Achats possibles : (coût Écus, éclats, nouvel état, libellé)."""
    out = []
    used = len(etat["mach"]); slots = etat["parc"] * SLOTS
    for m, d in MACH.items():
        if d["rang"] > etat["rang"]: continue
        if sum(1 for x, _ in etat["mach"] if x == m) >= max_copies(m, etat["rang"]): continue
        if used < slots:
            e = copy.deepcopy(etat); e["mach"].append((m, 1)); out.append((d["prix"], d["ecl"], e, f"achat {d['nom']}"))
        else:
            if etat["parc"] < PARC_MAX[etat["rang"]]:
                pp = prix_parcelle(etat["parc"] + 1)
                if pp:
                    e = copy.deepcopy(etat); e["parc"] += 1; e["mach"].append((m, 1))
                    out.append((d["prix"] + pp[0], d["ecl"] + pp[1], e, f"parcelle {etat['parc'] + 1} + {d['nom']}"))
    for i, (m, l) in enumerate(etat["mach"]):
        if l < 5:
            d = MACH[m]; e = copy.deepcopy(etat); e["mach"][i] = (m, l + 1)
            ecl = max(d["ecl"] * LV_ECL[l], [0, 0, 0, 3, 6][l]) if l >= 3 else 0
            out.append((d["prix"] * LV_COUT[l], ecl, e, f"{d['nom']} niv {l + 1}"))
    nb = etat.get("brevet", 0)
    if nb < 10 and etat["rang"] >= 2:
        e = copy.deepcopy(etat); e["brevet"] = nb + 1; e["sat"] = 1 + 0.25 * (nb + 1)
        out.append((int(300_000 * 2.2 ** nb), 2 * nb, e, f"brevet Réseau commercial {nb + 1}"))
    go = etat.get("oeuvre", 0)
    if go < 8 and etat["rang"] >= 4:
        e = copy.deepcopy(etat); e["oeuvre"] = go + 1
        out.append((int(8_000_000 * 1.8 ** go), 10 * (go + 1), e, f"Grand Œuvre {go + 1}"))
    nh = etat["halle"] + 1
    if nh < len(HALLE) and HALLE[nh][3] <= etat["rang"]:
        e = copy.deepcopy(etat); e["halle"] = nh; out.append((HALLE[nh][1], HALLE[nh][2], e, f"Halle : {HALLE[nh][0]}"))
    return out

def simuler(jours=90, heures=10, ecus0=100_000, revenu_ext=80_000, ecl_ext=3, riche=False, verbose=False, trace=None):
    etat = dict(rang=1, halle=0, parc=1, mach=[("carriere", 1)], sat=1.0)
    ecus = ecus0; ecl = 0; ri = 0; contrats = 0; hist = []
    for j in range(1, jours + 1):
        ecus += revenu_ext; ecl += ecl_ext
        net, dri, nc, ec, fe, prod, gc = journee(etat, heures)
        ecus += net; ri += dri; contrats += nc; ecl += ec
        # montée de rang
        r = etat["rang"] + 1
        if r in RANGS:
            q_ri, q_c, q_p, q_e, _ = RANGS[r]
            if ri >= q_ri and contrats >= q_c and ecus >= q_p and ecl >= q_e:
                ecus -= q_p; ecl -= q_e; etat["rang"] = r
                if trace is not None: trace.append((j, f"rang {NOMS_RANG[r]}"))
        # investissements gloutons : meilleur rapport gain / coût, en gardant de quoi payer le rang suivant
        reserve = 0
        if r in RANGS and ri >= RANGS[r][0] and contrats >= RANGS[r][1]: reserve = RANGS[r][2]
        for _ in range(40):
            base, *_ = journee(etat, heures)
            best = None
            for cout, ce, e, lab in options(etat):
                if cout > ecus - reserve or ce > ecl - (RANGS[r][3] if r in RANGS and reserve else 0): continue
                g, *_ = journee(e, heures)
                roi = (g - base) / max(cout, 1)
                if g - base > 0 and (best is None or roi > best[0]): best = (roi, cout, ce, e, lab)
            if not best or best[0] < 1 / 60: break      # pas d'achat qui se rembourse en plus de 60 jours
            ecus -= best[1]; ecl -= best[2]; etat = best[3]
            if trace is not None and ("achat" in best[4] or "Halle" in best[4] or "parcelle" in best[4]): trace.append((j, best[4]))
        hist.append(dict(j=j, rang=etat["rang"], net=net, ecus=ecus, ri=ri, contrats=contrats, ecl=ecl, nb=len(etat["mach"]), fe=fe, parc=etat["parc"],
                         valeur=sum(MACH[m]["prix"] * sum(LV_COUT[:l]) for m, l in etat["mach"])))
    return hist, etat

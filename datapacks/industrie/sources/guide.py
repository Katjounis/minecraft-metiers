# -*- coding: utf-8 -*-
# Guide et parcours de départ (28/11/2026) : les joueurs ne comprenaient pas quoi faire.
# Exécuté par datapack.py après menus.py (mêmes helpers : fn, T, L, msg, btn, dlg, say).
# i.tuto : 0 pas commencé, 1 à 6 étape en cours, 7 terminé.
ETAPES = [
    # (objectif court, condition de réussite ou None si accrochée ailleurs, récompense en Écus)
    ("Clic droit sur ta Carrière (la machine posée près du Nexus)", None, 1_000),
    ("Achète une 2e machine : menu Industrie, Comptoir", "machines", 3_000),
    ("Ouvre la Halle du Marché et regarde ton contrat du jour", None, 1_000),
    ("Livre ton premier contrat à la Halle", "contrat", 5_000),
    ("Achète une 2e parcelle : menu Industrie, Cadastre", "parcelle", 5_000),
    ("Passe au rang Manufacture : menu Industrie, Bureau", "rang", 20_000),
]
N_ET = len(ETAPES)

V = [f"execute if score @s i.tuto matches 0 run function {NS}:tuto/debut"]
for k, (obj, cond, gain) in enumerate(ETAPES, 1):
    if cond == "machines":
        V += [f"{S} set #x i.t 0"] + [f"{S} operation #x i.t += @s i.n_{m}" for m in ML] + [
              f"execute if score @s i.tuto matches {k} if score #x i.t matches 2.. run function {NS}:tuto/fini_{k}"]
    elif cond == "contrat":
        V += [f"execute if score @s i.tuto matches {k} if score @s i.ctr matches 1.. run function {NS}:tuto/fini_{k}"]
    elif cond == "parcelle":
        V += [f"execute if score @s i.tuto matches {k} if score @s i.np matches 2.. run function {NS}:tuto/fini_{k}"]
    elif cond == "rang":
        V += [f"execute if score @s i.tuto matches {k} if score @s i.rang matches 2.. run function {NS}:tuto/fini_{k}"]
    V += [f"execute if score @s i.tuto matches {k} if dimension {DIM} run title @s actionbar "
          + L(T(f"Étape {k}/{N_ET} : ", OR, True), T(obj, "white"))]
fn("tuto/verif", V)
fn("tuto/debut", [f"{S} set @s i.tuto 1",
                  "tellraw @s " + L(PREFIX, T("Parcours de départ : 6 étapes, des Écus à chaque étape. ", "gray"),
                                    '{text:"[GUIDE]",color:"green",bold:true,click_event:{action:"run_command",command:"/trigger industrie set 12"}}')])
for k, (obj, cond, gain) in enumerate(ETAPES, 1):
    suite = ETAPES[k][0] if k < N_ET else None
    fn(f"tuto/fini_{k}", [
        f"{S} set @s i.tuto {k + 1}",
        f"execute if score @s c.ecus matches -2147483648.. run scoreboard players add @s c.ecus {gain}",
        "playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.7 1.3",
        "tellraw @s " + L(PREFIX, T(f"Étape {k} réussie : +{mille(gain)} Écus. ", "green"),
                          T(f"Ensuite : {suite}." if suite else "Parcours terminé, ton industrie est lancée. Le Bureau te dit ce qu'il faut pour le rang suivant.", "white"))])

# accroches : fiche d'une machine (étape 1), Halle (étape 3)
fn("tuto/fiche", [f"execute if score @s i.tuto matches 1 run function {NS}:tuto/fini_1"])
fn("tuto/halle", [f"execute if score @s i.tuto matches 3 run function {NS}:tuto/fini_3"])

# objectif affiché dans Mon industrie
OB = [f'data modify storage {M_} obj set value "Parcours terminé. Prochain rang : voir le Bureau."']
OB += [f'execute if score @s i.tuto matches {k} run data modify storage {M_} obj set value "Étape {k}/{N_ET} : {o}."' for k, (o, c, g) in enumerate(ETAPES, 1)]
OB += [f'execute if score @s i.tuto matches 0 run data modify storage {M_} obj set value "{ETAPES[0][0]}."']
fn("tuto/objectif", OB)

# ---------------------------------------------------------------- le guide : des pages courtes
G_RET = [btn(T("Retour au guide", "gray"), 12, 140), btn(T("Mon industrie", "white"), 1, 140)]
PAGES = {
    13: ("LA DÉMARCHE", [
        ("1. ", "Tes machines produisent toutes seules, même quand tu es déconnecté."),
        ("2. ", "Tout ce qu'elles produisent part au Nexus, l'entrepôt de ton île."),
        ("3. ", "La Halle du Marché vend le stock du Nexus et te paie en Écus."),
        ("4. ", "Avec les Écus : plus de machines, plus de parcelles, et tu montes de rang.")]),
    14: ("LE NEXUS", [
        ("", "La grande tour au centre de ton île. C'est ton entrepôt : chaque machine y envoie sa production par un tube lumineux."),
        ("", f"Il fournit aussi {NEXUS_KW} kW d'énergie, assez pour 2 ou 3 machines. Au-delà, achète une Chaudière à charbon, sinon tout ralentit."),
        ("", "Le stock du Nexus est affiché dans Mon industrie.")]),
    15: ("LES MACHINES", [
        ("", "Achète-les au Comptoir. Chacune se pose sur une dalle libre de ton île (4 dalles par parcelle)."),
        ("", "Clic droit sur une machine : sa fiche, son amélioration (plus de production) et sa revente."),
        ("", "Plus de place ? Achète une parcelle voisine au Cadastre.")]),
    16: ("HALLE ET CONTRATS", [
        ("", "La Halle vend ton stock toute seule. Plus tu vends un même produit dans la journée, plus son prix baisse : varie tes machines."),
        ("Contrat : ", "une commande du jour. Tu livres la quantité d'un coup, payée 1,5 fois le prix sans baisse, plus de la réputation."),
        ("", "La Halle met de côté ce qu'il faut pour tes contrats : attends que le chiffre passe au vert, puis clique Livrer.")]),
    17: ("LES RANGS", [
        ("", "Atelier, Manufacture, Industrie, Consortium, Empire. Chaque rang débloque des machines, des parcelles, des contrats et des bâtiments."),
        ("Pour monter : ", "de la réputation (elle vient des ventes et des contrats), des contrats livrés, des Écus. Le Bureau de l'île affiche ce qui te manque."),
        ("Manufacture : ", f"{mille(RANGS[2][1])} de réputation, {RANGS[2][2]} contrats, {mille(RANGS[2][3])} Écus. Débloque la Banque et le tube en or.")]),
}
fn("menu/guide", dlg(T("GUIDE DE L'INDUSTRIE", OR, True),
                     [msg(T("Choisis une page. Ton prochain objectif s'affiche en bas de l'écran quand tu es sur ton île.", "gray"), 300)],
                     [btn(T("Que faire ?", "green", True), 18, 140), btn(T("Revoir la présentation", "white"), 19, 140), btn(T("La démarche", "green"), 13, 140), btn(T("Le Nexus", OR), 14, 140), btn(T("Les machines", OR), 15, 140),
                      btn(T("Halle et contrats", "light_purple"), 16, 140), btn(T("Les rangs", "aqua"), 17, 140), btn(T("Mon industrie", "white"), 1, 140)], 3))
for v, (titre, lignes) in PAGES.items():
    corps = []
    for i, (a, b) in enumerate(lignes):
        sep = "\\n\\n" if i else ""
        if a:
            corps += [T(sep + a, OR, True), T(b, "white")]
        else:
            corps += [T(sep + b, "white")]
    fn(f"menu/guide_{v}", dlg(T(titre, OR, True), [msg(L(*corps), 300)], G_RET, 2))

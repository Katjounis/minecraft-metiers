# -*- coding: utf-8 -*-
# Présentation à la première arrivée sur l'île (28/11/2026) et page « Que faire ? » (feuille de route par rang).
# i.cin : 0 jamais vue, 1 à 39 en cours (une étape par seconde, appelée par seconde), 40 vue.
TIT = 'title @s times 8 90 12'


def titre(a, b):
    return [TIT, 'title @s subtitle [{"text":"' + a + ' : ","color":"#F7C843","bold":true},{"text":"' + b + '","color":"white"}]', 'title @s title ""',
            "playsound minecraft:block.note_block.chime master @s ~ ~ ~ 0.8 1.2"]


def lueur(tag):
    return [f"execute as @e[type=minecraft:item_display,tag={tag},distance=..96,limit=1,sort=nearest] run data merge entity @s {{Glowing:1b}}",
            f"execute at @e[type=minecraft:item_display,tag={tag},distance=..96,limit=1,sort=nearest] run particle minecraft:end_rod ~ ~ ~ 0.6 4 0.6 0.03 120 force @s"]


ETAPES_CINE = {
    2: titre("Ton île", "visite en 30 secondes"),
    6: titre("Le Nexus", "ton entrepôt, clic droit = menu") + lueur("ind.b_nexus"),
    12: titre("Les machines", "elles produisent seules") + lueur("ind.m"),
    18: titre("Les tubes", "ils amènent tout au Nexus")
        + ["execute at @e[type=minecraft:item_display,tag=ind.b_nexus,distance=..96,limit=1,sort=nearest] run particle minecraft:electric_spark ~ ~2 ~ 6 1 6 0.1 200 force @s"],
    24: titre("La Halle", "elle vend, tu gagnes des Écus") + lueur("ind.b_echoppe") + lueur("ind.b_halle"),
    30: titre("Ton but", "plus de machines, monter de rang"),
    36: ["execute as @e[type=minecraft:item_display,distance=..96] run data merge entity @s {Glowing:0b}", f"{S} set @s i.cin 39",
         f"function {NS}:menu/route"],
}
P_ = [f"{S} add @s i.cin 1"]
for t_, cmds in ETAPES_CINE.items():
    fn(f"cine/e{t_}", cmds)
    P_.append(f"execute if score @s i.cin matches {t_} run function {NS}:cine/e{t_}")
P_.append(f"execute if score @s i.cin matches 39.. run {S} set @s i.cin 40")
fn("cine/pas", P_)
fn("cine/revoir", [f"execute at @s unless dimension {DIM} run function {NS}:ile/aller", f"{S} set @s i.cin 1"])

# ---------------------------------------------------------------- « Que faire ? » : où tu en es, ce que le prochain rang demande et débloque
VICT = {None: "", "boss": ", un boss de Métiers vaincu", "wither": ", 3 Wither vaincus", "dragon": ", l'Ender Dragon vaincu"}
NOM_COURT = {m: MACH[m]["nom"].replace("Puits de cristal : ", "Puits ").replace(" des Titans", "").replace(" alchimique", "") for m in ML}


def debloque(r):
    l_ = [NOM_COURT[m] for m in ML if MACH[m]["rang"] == r]
    if r == 2:
        l_ += ["Banque", "Laboratoire"]
    if r == 4:
        l_ += ["Grands Œuvres", "Parts d'île"]
    l_ += [f"Halle niveau {h[0]}" for h in HALLE if h[1] == r and r > 1]
    l_ += [f"tube en {t[0]}" for t in TUBES if t[1] == r and r > 1]
    l_ += [f"{PARC_MAX[r]} parcelles"]
    if r == 1 or CONTRATS_JOUR[r] != CONTRATS_JOUR[r - 1]:
        l_ += [f"{CONTRATS_JOUR[r]} contrat{'s' if CONTRATS_JOUR[r] > 1 else ''} par jour"]
    return ", ".join(l_)


for r in range(1, 6):
    corps = [T("À faire maintenant : ", "green", True), T("$(obj)", "white"),
             T(f"\\n\\nTon rang : {RANGS[r][0].upper()}", OR, True), T(f"\\nTu as : {debloque(r)}.", "gray")]
    if r < 5:
        n_ = RANGS[r + 1]
        corps += [T(f"\\n\\nPROCHAIN RANG : {n_[0].upper()}", "aqua", True),
                  T(f"\\nIl faut : {mille(n_[1])} de réputation (elle vient des ventes et des contrats), {n_[2]} contrats livrés, "
                    f"{mille(n_[3])} Écus" + (f", {n_[4]} éclats" if n_[4] else "") + VICT[n_[5]] + ".", "white"),
                  T(f"\\nTu débloques : {debloque(r + 1)}.", "gray")]
        if r + 2 <= 5:
            corps += [T("\\n\\nEnsuite : " + ", ".join(RANGS[x][0] for x in range(r + 2, 6)) + ".", "dark_gray")]
    else:
        corps += [T("\\n\\nTu es au sommet. Il reste les Grands Œuvres.", "aqua")]
    fn(f"menu/route_{r}", "$" + dlg(T("QUE FAIRE ?", OR, True), [msg(L(*corps), 300)],
                                    [btn(T("Retour", "white"), 1, 130), btn(T("Passer de rang", "light_purple"), 9, 150)], 2))
fn("menu/route", [f"function {NS}:tuto/objectif"] + [f"execute if score @s i.rang matches {r} run return run function {NS}:menu/route_{r} with storage {M_}" for r in range(1, 6)])

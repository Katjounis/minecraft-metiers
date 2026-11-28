# -*- coding: utf-8 -*-
# Machines : achat au Comptoir, pose sur l'emplacement libre le plus proche, tubes à faisceau, fiche (clic droit),
# amélioration, revente. Exécuté par datapack.py après ile.py.
#
# La production ne lit jamais les entités : chaque achat, amélioration ou revente met à jour des sommes sur le joueur
# (i.q_<m> = somme des niveaux en %, i.n_<m> = nombre, i.k_<m> = somme des consommations en dixièmes,
# i.qs<k> = puissance des usines à spawner par créature). Les entités ne servent qu'à l'affichage et au clic.
TUBE_BLOC = [("minecraft:orange_stained_glass", "minecraft:orange_concrete"), ("minecraft:yellow_stained_glass", "minecraft:gold_block"),
             ("minecraft:light_blue_stained_glass", "minecraft:sea_lantern")]


def prix_niv(m, l):
    """Prix et éclats pour passer du niveau l au niveau l + 1 (l de 1 à 4)."""
    d = MACH[m]
    e = max(d["ecl"] * LV_ECL[l], [0, 0, 0, 3, 6][l]) if l >= 3 else 0
    return d["prix"] * LV_COUT[l], e


def deja_paye(m, l):
    return sum(MACH[m]["prix"] * LV_COUT[i] for i in range(l))


def prod_txt(m, l):
    d = MACH[m]
    if d["kw"] < 0:
        return f"{-d['kw'] * LV_PROD[l - 1] // 100} kW fournis"
    if m == "spawner":
        return f"{SP_PAR_H * LV_PROD[l - 1] // 100} créatures par heure (plus avec un spawner amélioré)"
    return ", ".join(f"{mille(q * LV_PROD[l - 1] // 100)} {PROD[p][0].lower()}" for p, q in d["out"].items()) + " par heure"


# ---------------------------------------------------------------- position sur sa propre île (#ok = 1)
fn("ile/position", [f"{S} set #ok i.t 0", f"execute at @s unless dimension {DIM} run return 0",
                    "execute store result score #px i.t run data get entity @s Pos[0]", "execute store result score #pz i.t run data get entity @s Pos[2]",
                    f"{S} operation #a i.t = #px i.t", f"{S} add #a i.t 1024", f"{S} operation #b i.t = #pz i.t", f"{S} add #b i.t 1024",
                    f"execute if score #a i.t matches 0.. if score #b i.t matches 0.. run function {NS}:ile/garde_calc"])

# ---------------------------------------------------------------- achat (100 + k)
for k, m in enumerate(ML):
    d = MACH[m]
    A = [f"function {NS}:ile/position",
         f"execute if score #ok i.t matches 0 run return run " + say("Va sur une de tes parcelles, près d'un emplacement libre (dalle noire à coins dorés).", "red"),
         f"execute unless score @s i.rang matches {d['rang']}.. run return run " + say(f"{d['nom']} : il faut le rang {RANGS[d['rang']][0]}.", "red")]
    A += [f"{S} set #max i.t 0"] + [f"execute if score @s i.rang matches {r} run {S} set #max i.t {max_copies(m, r)}" for r in range(1, 6)]
    A += [f"execute if score @s i.n_{m} >= #max i.t run return run " + say(f"Tu as déjà le maximum de {d['nom']} pour ton rang.", "red"),
          f"{S} set #prix i.t {d['prix']}",
          f"execute if score @s m.k_lvl matches 50.. run {S} set #prix i.t {d['prix'] * 9 // 10}",
          f"execute unless score @s c.ecus >= #prix i.t run return run " + say(f"Il te faut {mille(d['prix'])} Écus.", "red")]
    if d["ecl"]:
        A.append(f"execute unless score @s m.ecl matches {d['ecl']}.. run return run " + say(f"Il te faut {d['ecl']} éclats de boss.", "red"))
    if d.get("etoile"):
        A.append(f"execute unless items entity @s container.* minecraft:nether_star run return run " + say("Il te faut une étoile du Nether dans ton inventaire.", "red"))
    if m == "spawner":
        A += [f"execute unless items entity @s weapon.mainhand minecraft:spawner[minecraft:custom_data~{{commerce_sp:{{}}}}] run return run "
              + say("Tiens en main un spawner du Commerce : l'usine le prend et produit le butin de sa créature.", "red"),
              'execute store result score #mob i.t run data get entity @s SelectedItem.components."minecraft:custom_data".commerce_sp.m',
              'execute store result score #spv i.t run data get entity @s SelectedItem.components."minecraft:custom_data".commerce_sp.v',
              'execute store result score #spq i.t run data get entity @s SelectedItem.components."minecraft:custom_data".commerce_sp.q',
              f"{S} remove #mob i.t 1", f"execute unless score #mob i.t matches 0..{len(MOBS) - 1} run return run " + say("Spawner inconnu.", "red")]
    A += [f"{S} operation #me i.t = @s m.id", f"{S} operation #own i.t = @s m.id",
          f"execute store result score #now i.t run time query gametime", f"{S} operation #now i.t -= @s i.pst", f"{S} operation #ps i.t = @s i.psl",
          f"execute unless score #now i.t matches 0..1200 run {S} set #ps i.t -1",
          f"execute if score #ps i.t matches 0.. as @e[type=minecraft:marker,tag=ind.slot,tag=!ind.occ,distance=..48] if score @s i.own = #me i.t if score @s i.sid = #ps i.t run tag @s add ind.cand",
          f"execute unless entity @e[type=minecraft:marker,tag=ind.cand] as @e[type=minecraft:marker,tag=ind.slot,tag=!ind.occ,distance=..48] if score @s i.own = #me i.t run tag @s add ind.cand",
          f"{S} set @s i.psl -1",
          f"execute unless entity @e[type=minecraft:marker,tag=ind.cand] run return run " + say("Aucun emplacement libre à moins de 48 blocs : achète une parcelle (Cadastre) ou rapproche-toi.", "red"),
          # paiement
          f"execute if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus -= #prix i.t"]
    if d["ecl"]:
        A.append(f"{S} remove @s m.ecl {d['ecl']}")
    if d.get("etoile"):
        A.append("clear @s minecraft:nether_star 1")
    if m == "spawner":
        A += ["item replace entity @s weapon.mainhand with minecraft:air",
              f"{S} operation #sf i.t = #spv i.t", f"{S} operation #sf i.t += #spq i.t", f"{S} set #y i.t 25", f"{S} operation #sf i.t *= #y i.t", f"{S} add #sf i.t 100"]
        A += [f"execute if score #mob i.t matches {mk} run {S} operation @s i.qs{mk} += #sf i.t" for mk in range(len(MOBS))]
    else:
        A += [f"{S} set #sf i.t 100", f"{S} set #mob i.t 0", f"{S} set #spv i.t 0", f"{S} set #spq i.t 0"]
    A += [f"{S} add @s i.q_{m} 100", f"{S} add @s i.n_{m} 1", f"{S} add @s i.k_{m} {LV_KW[0]}",
          f"{S} set #pm i.t {k}", f"{S} set #pl i.t 1", f"{S} operation #tt i.t = @s i.tube",
          f"execute as @e[type=minecraft:marker,tag=ind.cand,limit=1,sort=nearest] at @s run function {NS}:machine/poser_ici",
          "tag @e[type=minecraft:marker,tag=ind.cand] remove ind.cand",
          "playsound minecraft:block.anvil.use master @s ~ ~ ~ 0.8 1.2", "playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.6 1.4",
          say(f"{d['nom']} posée et reliée au Nexus. Clic droit dessus pour sa fiche.", "green")]
    fn(f"machine/acheter_{k}", A)

fn("machine/poser_ici", [f"{S} operation #psid i.t = @s i.sid", "tag @s add ind.occ",
                          "kill @e[type=minecraft:interaction,tag=ind.si,distance=..1]", "kill @e[type=minecraft:text_display,tag=ind.sl,distance=..3]", f"function {NS}:machine/visuel_ici"])
# entités d'une machine à la position de l'emplacement (y = 64) : #pm type, #pl niveau, #psid, #own (ou @s ici le joueur), #mob, #sf...
V_ = []
for k, m in enumerate(ML):
    V_.append(f'execute if score #pm i.t matches {k} run summon minecraft:item_display ~ ~{round(1.5 * ECH_M, 2)} ~ {{Tags:["ind.m","ind.nouvm"],'
              f'item_display:"none",view_range:3f,brightness:{{sky:15,block:15}},item:{{id:"minecraft:paper",count:1,components:{{"minecraft:item_model":"{NS}:{m}"}}}},'
              f'transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[{ECH_M}f,{ECH_M}f,{ECH_M}f]}}}}')
V_ += ['summon minecraft:interaction ~ ~ ~ {Tags:["ind.mi","ind.nouvm","ind.t4"],width:6.5f,height:7f}',
       f"{S} operation @e[tag=ind.nouvm,distance=..9] i.own = #own i.t", f"{S} operation @e[tag=ind.nouvm,distance=..9] i.sid = #psid i.t",
       f"{S} operation @e[tag=ind.nouvm,distance=..9] i.mt = #pm i.t", f"{S} operation @e[tag=ind.nouvm,distance=..9] i.ml = #pl i.t",
       f"{S} operation @e[tag=ind.nouvm,distance=..9] i.mob = #mob i.t", f"{S} operation @e[tag=ind.nouvm,distance=..9] i.sf = #sf i.t",
       f"{S} operation @e[tag=ind.nouvm,distance=..9] i.spv = #spv i.t", f"{S} operation @e[tag=ind.nouvm,distance=..9] i.spq = #spq i.t",
       "tag @e[tag=ind.nouvm,distance=..9] remove ind.nouvm",
       "particle minecraft:end_rod ~ ~3 ~ 2 2 2 0.05 80 force",
       f"function {NS}:tube/poser"]
fn("machine/visuel_ici", V_)

# ---------------------------------------------------------------- tube à faisceau de l'emplacement jusqu'au Nexus (y = 73)
# deux branches : en x jusqu'à l'axe du Nexus, puis en z jusqu'au Nexus. Chaque branche : verre teinté, cœur lumineux,
# un paquet qui glisse (animé par tube/anim).
fn("tube/poser", [
    "summon minecraft:marker ~ ~ ~ {Tags:[\"ind.pos\"]}",
    "execute store result score #sx i.t run data get entity @e[type=minecraft:marker,tag=ind.pos,limit=1] Pos[0]",
    "execute store result score #sz i.t run data get entity @e[type=minecraft:marker,tag=ind.pos,limit=1] Pos[2]",
    "kill @e[type=minecraft:marker,tag=ind.pos]",
    f"{S} operation #a i.t = #sx i.t", f"{S} add #a i.t 1024", f"{S} operation #b i.t = #sz i.t", f"{S} add #b i.t 1024",
    f"{S} operation #a i.t /= #2048 i.g", f"{S} operation #b i.t /= #2048 i.g",
    f"{S} operation #n i.t = #b i.t", f"{S} operation #n i.t *= #16 i.g", f"{S} operation #n i.t += #a i.t", f"function {NS}:ile/centre",
    # branche x
    f"{S} operation #x1 i.t = #sx i.t", f"execute if score #cx i.t < #sx i.t run {S} operation #x1 i.t = #cx i.t",
    f"{S} operation #lx i.t = #cx i.t", f"{S} operation #lx i.t -= #sx i.t",
    f"{S} operation #ax i.t = #lx i.t", f"execute if score #ax i.t matches ..-1 run {S} operation #ax i.t *= #-1 i.g",
    # branche z
    f"{S} operation #z1 i.t = #sz i.t", f"execute if score #cz i.t < #sz i.t run {S} operation #z1 i.t = #cz i.t",
    f"{S} operation #lz i.t = #cz i.t", f"{S} operation #lz i.t -= #sz i.t",
    f"{S} operation #az i.t = #lz i.t", f"execute if score #az i.t matches ..-1 run {S} operation #az i.t *= #-1 i.g",
    *[f"execute store result storage {NS}:t tb.{v} int 1 run {S} get #{v} i.t" for v in ("sx", "sz", "cx", "cz", "x1", "z1", "lx", "lz", "ax", "az", "own", "psid")],
    f"execute store result storage {NS}:t tb.hx float 0.5 run {S} get #ax i.t", f"execute store result storage {NS}:t tb.hz float 0.5 run {S} get #az i.t",
    f"{S} operation #a6 i.t = #ax i.t", f"{S} operation #a6 i.t *= #10 i.g", f"{S} add #a6 i.t 6", f"execute store result storage {NS}:t tb.ax6 float 0.1 run {S} get #a6 i.t",
    f"{S} operation #a6 i.t = #az i.t", f"{S} operation #a6 i.t *= #10 i.g", f"{S} add #a6 i.t 6", f"execute store result storage {NS}:t tb.az6 float 0.1 run {S} get #a6 i.t",
    f'data modify storage {NS}:t tb.coeur set value "{TUBE_BLOC[0][1]}"',
    *[f'execute if score #pm i.t matches {k} run data modify storage {NS}:t tb.verre set value "{FAMILLES[FAM[m]][2]}"' for k, m in enumerate(ML)],
    *[f'execute if score #tt i.t matches {k} run data modify storage {NS}:t tb.coeur set value "{c}"' for k, (_, c) in enumerate(TUBE_BLOC) if k],
    *[f'execute if score #pm i.t matches {k} run data modify storage {NS}:t tb.it set value "minecraft:{PAQUET[m]}"' for k, m in enumerate(ML)],
    f"execute if score #ax i.t matches 1.. run function {NS}:tube/branche_x with storage {NS}:t tb",
    f"execute if score #az i.t matches 1.. run function {NS}:tube/branche_z with storage {NS}:t tb"])
TR = "left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]"
TY = 69   # 28/11/2026 : 73 était trop haut pour être vu
def _seg(pos, scale, trans, nom, lum):
    return (f'$execute in {DIM} run summon minecraft:item_display {pos} {{Tags:["ind.tube","ind.nt"],view_range:3f,item_display:"none",'
            + ('brightness:{sky:15,block:15},' if lum else '')
            + f'item:{{id:"$({nom})",count:1}},transformation:{{{TR},translation:{trans},scale:{scale}}}}}')
fn("tube/branche_x", [
    _seg(f"$(x1).5 {TY} $(sz).5", "[$(ax6)f,0.6f,0.6f]", "[$(hx)f,0f,0f]", "verre", False),
    _seg(f"$(x1).5 {TY} $(sz).5", "[$(ax6)f,0.22f,0.22f]", "[$(hx)f,0f,0f]", "coeur", True),
    f"$execute if score #lx i.t matches 1.. in {DIM} positioned $(sx).5 {TY} $(sz).5 run function {NS}:tube/pq_xp with storage {NS}:t tb",
    f"$execute if score #lx i.t matches ..-1 in {DIM} positioned $(sx).5 {TY} $(sz).5 run function {NS}:tube/pq_xm with storage {NS}:t tb",
    f"function {NS}:tube/marquer"])
fn("tube/branche_z", [
    _seg(f"$(cx).5 {TY} $(z1).5", "[0.6f,0.6f,$(az6)f]", "[0f,0f,$(hz)f]", "verre", False),
    _seg(f"$(cx).5 {TY} $(z1).5", "[0.22f,0.22f,$(az6)f]", "[0f,0f,$(hz)f]", "coeur", True),
    f"$execute if score #lz i.t matches 1.. in {DIM} positioned $(cx).5 {TY} $(sz).5 run function {NS}:tube/pq_zp with storage {NS}:t tb",
    f"$execute if score #lz i.t matches ..-1 in {DIM} positioned $(cx).5 {TY} $(sz).5 run function {NS}:tube/pq_zm with storage {NS}:t tb",
    f"function {NS}:tube/marquer"])

# train de paquets : un objet tous les 2 blocs ; chaque seconde ils avancent de 2 blocs puis reviennent d'un coup à leur place,
# où le suivant les remplace : on voit un flux continu (28/11/2026, avant : un seul objet qui sautait en boucle)
PAS_DIR = {"xp": "~2 ~ ~", "xm": "~-2 ~ ~", "zp": "~ ~ ~2", "zm": "~ ~ ~-2"}
for d_, pas in PAS_DIR.items():
    k_ = "#ax" if d_[0] == "x" else "#az"
    fn(f"tube/pq_{d_}", [f"{S} operation #k i.t = {k_} i.t", f"{S} operation #k i.t /= #2 i.g", f"function {NS}:tube/pq_{d_}_r with storage {NS}:t tb"])
    fn(f"tube/pq_{d_}_r", [
        f'$summon minecraft:item_display ~ ~ ~ {{Tags:["ind.tube","ind.pq","ind.nt","ind.d_{d_}"],view_range:3f,brightness:{{sky:15,block:15}},'
        f'item:{{id:"$(it)",count:1}},transformation:{{{TR},translation:[0f,0f,0f],scale:[0.35f,0.35f,0.35f]}}}}',
        f"{S} remove #k i.t 1", f"execute if score #k i.t matches 1.. positioned {pas} run function {NS}:tube/pq_{d_}_r with storage {NS}:t tb"])
fn("tube/marquer", [f"{S} operation @e[tag=ind.nt] i.own = #own i.t", f"{S} operation @e[tag=ind.nt] i.sid = #psid i.t", "tag @e[tag=ind.nt] remove ind.nt"])
# animation : un pas par seconde (aller en 1 s, puis retour instantané au départ)
fn("tube/anim", ["data merge entity @s {start_interpolation:0,interpolation_duration:0,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.35f,0.35f,0.35f]}}"])
fn("tube/go", [f"execute as @a at @s if dimension {DIM} as @e[type=minecraft:item_display,tag=ind.pq,distance=..80] run function {NS}:tube/go_un"])
fn("tube/go_un", [
    "execute if entity @s[tag=ind.d_xp] run return run data merge entity @s {start_interpolation:0,interpolation_duration:19,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[2f,0f,0f],scale:[0.35f,0.35f,0.35f]}}",
    "execute if entity @s[tag=ind.d_xm] run return run data merge entity @s {start_interpolation:0,interpolation_duration:19,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-2f,0f,0f],scale:[0.35f,0.35f,0.35f]}}",
    "execute if entity @s[tag=ind.d_zp] run return run data merge entity @s {start_interpolation:0,interpolation_duration:19,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,2f],scale:[0.35f,0.35f,0.35f]}}",
    "execute if entity @s[tag=ind.d_zm] run return run data merge entity @s {start_interpolation:0,interpolation_duration:19,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,-2f],scale:[0.35f,0.35f,0.35f]}}"])

# ---------------------------------------------------------------- tubes : nouveau palier pour toute l'île (540)
TU = [f"{S} operation #tn i.t = @s i.tube", f"{S} add #tn i.t 1",
      f"execute if score #tn i.t matches {len(TUBES)}.. run return run " + say("Tes tubes sont déjà en cristal.", "gray"),
      f"{S} set #nbm i.t 0"] + [f"{S} operation #nbm i.t += @s i.n_{m}" for m in ML]
for k, (nom, rang, deb, prix, ecl) in enumerate(TUBES):
    if not k:
        continue
    TU += [f"execute if score #tn i.t matches {k} unless score @s i.rang matches {rang}.. run return run " + say(f"Tubes en {nom} : il faut le rang {RANGS[rang][0]}.", "red"),
           f"execute if score #tn i.t matches {k} run {S} set #prix i.t {prix}", f"execute if score #tn i.t matches {k} run {S} set #ecl i.t {ecl}"]
TU += [f"{S} operation #prix i.t *= #nbm i.t", f"{S} operation #ecl i.t *= #nbm i.t",
       f"execute unless score @s c.ecus >= #prix i.t run return run " + say("Pas assez d'Écus pour changer tous tes tubes.", "red"),
       f"execute unless score @s m.ecl >= #ecl i.t run return run " + say("Pas assez d'éclats de boss.", "red"),
       f"execute if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus -= #prix i.t", f"{S} operation @s m.ecl -= #ecl i.t",
       f"{S} operation @s i.tube = #tn i.t", f"{S} operation #me i.t = @s m.id",
       f"execute as @e[type=minecraft:interaction,tag=ind.mi,distance=..400] if score @s i.own = #me i.t run tag @s remove ind.t4",
       "playsound minecraft:block.beacon.power_select master @s ~ ~ ~ 1 1.2", say("Tous tes tubes sont remplacés : le débit par machine augmente.", "green")]
fn("tube/ameliorer", TU)
for k in range(1, len(TUBES)):
    v, c = TUBE_BLOC[k]
    fn(f"tube/teinte_{k}", [f'execute if data entity @s {{brightness:{{sky:15}}}} run return run data modify entity @s block_state.Name set value "{c}"',
                            f'data modify entity @s block_state.Name set value "{v}"'])

# ---------------------------------------------------------------- clic sur une machine : fiche
fn("machine/clic", [
    f"{S} operation #co i.t = @s i.own", f"{S} operation #cs i.t = @s i.sid", f"{S} operation #cm i.t = @s i.mt",
    # 27/11/2026 : « on target » lit le joueur dans les données d'interaction : on les efface APRÈS, sinon aucun clic n'aboutit
    f"execute on target run function {NS}:machine/clic_j", "data remove entity @s interaction", "data remove entity @s attack"])
fn("machine/clic_j", [
    f"execute unless score @s m.id = #co i.t run return run " + say("Cette machine appartient à une autre île.", "gray"),
    f"{S} operation @s i.sel = #cs i.t", f"function {NS}:machine/fiche"])
# fiche : la machine choisie doit être à moins de 96 blocs
FI = [f"{S} operation #me i.t = @s m.id", f"{S} operation #sel i.t = @s i.sel", f"{S} set #cm i.t -1",
      f"execute as @e[type=minecraft:item_display,tag=ind.m,distance=..96] if score @s i.own = #me i.t if score @s i.sid = #sel i.t run function {NS}:machine/lire",
      f"execute if score #cm i.t matches -1 run return run " + say("Approche-toi de ta machine.", "red")]
for k, m in enumerate(ML):
    d = MACH[m]
    for l in range(1, 6):
        if l < 5:
            p, e = prix_niv(m, l)
            up = f"Niveau {l + 1} : {fe(p)} Écus" + (f" + {e} éclats" if e else "")
        else:
            up = "Niveau maximal"
        rv = deja_paye(m, l) // 2
        FI.append(f'execute if score #cm i.t matches {k} if score #cl i.t matches {l} run data modify storage {NS}:f m set value '
                  f'{{nom:"{d["nom"]}",niv:"{l}",prod:"{prod_txt(m, l)}",kw:"{abs(d["kw"]) * (LV_KW[l - 1] if d["kw"] > 0 else LV_PROD[l - 1] // 10) // 10} kW",'
                  f'up:"{up}",rv:"{fe(rv)}",np:"{prod_txt(m, l + 1) if l < 5 else ""}"}}')
FI += [f"function {NS}:machine/fiche_d with storage {NS}:f m"]
fn("machine/fiche", FI + [f"function {NS}:tuto/fiche"])
fn("machine/lire", [f"{S} operation #cm i.t = @s i.mt", f"{S} operation #cl i.t = @s i.ml", f"{S} operation #cmob i.t = @s i.mob"])
fn("machine/fiche_d", "$" + dlg(
    T("$(nom)", "#F7C843", True),
    [msg(L(T("Niveau ", "gray"), T("$(niv) / 5", "white", True), T("\\nProduction : ", "gray"), T("$(prod)", "green"),
           T("\\nÉnergie : ", "gray"), T("$(kw)", "aqua"), T("\\n\\nAmélioration : ", "gray"), T("$(up)", "gold"),
           T("\\n$(np)", "dark_green"), T("\\n\\nRevente : ", "gray"), T("$(rv) Écus (la moitié de ce qu'elle a coûté)", "red")))],
    [btn(T("Améliorer", "gold", True), 301, 150), btn(T("Revendre", "red"), 302, 150), btn(T("Mon industrie", "white"), 1, 150)], 3))

# ---------------------------------------------------------------- amélioration (301)
UP = [f"{S} operation #me i.t = @s m.id", f"{S} operation #sel i.t = @s i.sel", f"{S} set #cm i.t -1",
      f"execute as @e[type=minecraft:item_display,tag=ind.m,distance=..96] if score @s i.own = #me i.t if score @s i.sid = #sel i.t run function {NS}:machine/lire",
      f"execute if score #cm i.t matches -1 run return run " + say("Approche-toi de ta machine.", "red"),
      f"execute if score #cl i.t matches 5.. run return run " + say("Niveau maximal.", "gray"), f"{S} set #prix i.t 0", f"{S} set #ecl i.t 0"]
for k, m in enumerate(ML):
    for l in range(1, 5):
        p, e = prix_niv(m, l)
        UP += [f"execute if score #cm i.t matches {k} if score #cl i.t matches {l} run {S} set #prix i.t {p}"]
        if e:
            UP += [f"execute if score #cm i.t matches {k} if score #cl i.t matches {l} run {S} set #ecl i.t {e}"]
UP += [f"execute unless score @s c.ecus >= #prix i.t run return run " + say("Pas assez d'Écus pour cette amélioration.", "red"),
       f"execute unless score @s m.ecl >= #ecl i.t run return run " + say("Pas assez d'éclats de boss.", "red"),
       f"execute if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus -= #prix i.t", f"{S} operation @s m.ecl -= #ecl i.t"]
for k, m in enumerate(ML):
    for l in range(1, 5):
        dq, dk = LV_PROD[l] - LV_PROD[l - 1], LV_KW[l] - LV_KW[l - 1]
        c = f"execute if score #cm i.t matches {k} if score #cl i.t matches {l} run"
        UP += [f"{c} {S} add @s i.q_{m} {dq}", f"{c} {S} add @s i.k_{m} {dk}"]
        if m == "spawner":
            UP += [f"{c} {S} set #dq i.t {dq}"]
UP += [f"execute if score #cm i.t matches {MI['spawner']} run function {NS}:machine/up_spawner",
       f"execute as @e[type=minecraft:item_display,tag=ind.m,distance=..96] if score @s i.own = #me i.t if score @s i.sid = #sel i.t run function {NS}:machine/niv_plus",
       "playsound minecraft:block.smithing_table.use master @s ~ ~ ~ 1 1", "playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.6 1.6",
       say("Machine améliorée.", "green"), f"function {NS}:machine/fiche"]
fn("machine/ameliorer", UP)
fn("machine/niv_plus", [f"{S} add @s i.ml 1"] + [
    f"execute if score @s i.ml matches {l} run data merge entity @s {{transformation:{{scale:[{round(ECH_M * (1 + 0.06 * (l - 1)), 3)}f,{round(ECH_M * (1 + 0.06 * (l - 1)), 3)}f,{round(ECH_M * (1 + 0.06 * (l - 1)), 3)}f]}}}}"
    for l in range(2, 6)] + ["particle minecraft:totem_of_undying ~ ~2 ~ 1.5 2 1.5 0.3 80 force"])
# usine à spawner : la puissance de la créature monte du même pourcentage (#dq x puissance du spawner / 100)
fn("machine/up_spawner", [f"execute as @e[type=minecraft:item_display,tag=ind.m,distance=..96] if score @s i.own = #me i.t if score @s i.sid = #sel i.t run {S} operation #sf i.t = @s i.sf",
                          f"{S} operation #dq i.t *= #sf i.t", f"{S} operation #dq i.t /= #100 i.g"] +
   [f"execute if score #cmob i.t matches {mk} run {S} operation @s i.qs{mk} += #dq i.t" for mk in range(len(MOBS))])

# ---------------------------------------------------------------- revente (302) : la moitié de tout ce qu'elle a coûté
RV = [f"{S} operation #me i.t = @s m.id", f"{S} operation #sel i.t = @s i.sel", f"{S} set #cm i.t -1",
      f"execute as @e[type=minecraft:item_display,tag=ind.m,distance=..96] if score @s i.own = #me i.t if score @s i.sid = #sel i.t run function {NS}:machine/lire",
      f"execute if score #cm i.t matches -1 run return run " + say("Approche-toi de ta machine.", "red"),
      f"{S} set #rv i.t 0"]
for k, m in enumerate(ML):
    for l in range(1, 6):
        c = f"execute if score #cm i.t matches {k} if score #cl i.t matches {l} run"
        RV += [f"{c} {S} set #rv i.t {deja_paye(m, l) // 2}", f"{c} {S} remove @s i.q_{m} {LV_PROD[l - 1]}", f"{c} {S} remove @s i.k_{m} {LV_KW[l - 1]}"]
        if m == "spawner":
            RV += [f"{c} {S} set #dq i.t {LV_PROD[l - 1]}"]
    RV += [f"execute if score #cm i.t matches {k} run {S} remove @s i.n_{m} 1"]
RV += [f"execute if score #cm i.t matches {MI['spawner']} run function {NS}:machine/rv_spawner",
       f"execute if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus += #rv i.t",
       f"execute as @e[tag=ind.mi,distance=..96] if score @s i.own = #me i.t if score @s i.sid = #sel i.t at @s run fill ~-2 ~ ~-2 ~2 ~4 ~2 minecraft:air replace minecraft:barrier",
       f"execute as @e[tag=ind.mi,distance=..96] if score @s i.own = #me i.t if score @s i.sid = #sel i.t at @s run kill @e[type=minecraft:text_display,tag=ind.labm,distance=..10]",
       f"execute as @e[tag=ind.m,distance=..96] if score @s i.own = #me i.t if score @s i.sid = #sel i.t run kill @s",
       f"execute as @e[tag=ind.mi,distance=..96] if score @s i.own = #me i.t if score @s i.sid = #sel i.t run kill @s",
       f"execute as @e[tag=ind.tube,distance=..400] if score @s i.own = #me i.t if score @s i.sid = #sel i.t run kill @s",
       f"execute as @e[type=minecraft:marker,tag=ind.slot,distance=..96] if score @s i.own = #me i.t if score @s i.sid = #sel i.t run tag @s remove ind.occ",
       "playsound minecraft:block.anvil.destroy master @s ~ ~ ~ 0.7 1.2", say("Machine revendue. L'emplacement est libre.", "yellow")]
fn("machine/revendre", RV)
fn("machine/rv_spawner", [
    f"execute as @e[type=minecraft:item_display,tag=ind.m,distance=..96] if score @s i.own = #me i.t if score @s i.sid = #sel i.t run function {NS}:machine/rv_sp_lire",
    f"{S} operation #dq i.t *= #sf i.t", f"{S} operation #dq i.t /= #100 i.g"] +
   [f"execute if score #cmob i.t matches {mk} run {S} operation @s i.qs{mk} -= #dq i.t" for mk in range(len(MOBS))] +
   [f"execute if score #cmob i.t matches {mk} run data modify storage {NS}:t sp.nom set value \"{MOB_NOM[mk].replace(chr(39), chr(8217))}\"" for mk in range(len(MOBS))] +
   [f"{S} operation #x i.t = #cmob i.t", f"{S} add #x i.t 1", f"execute store result storage {NS}:t sp.m int 1 run {S} get #x i.t",
    f"execute store result storage {NS}:t sp.v int 1 run {S} get #spv i.t", f"execute store result storage {NS}:t sp.q int 1 run {S} get #spq i.t",
    f"data modify storage {NS}:t sp.p set value 0", f"data modify storage {NS}:t sp.c set value 0",
    f"function commerce:spawner/donner with storage {NS}:t sp", say("Le spawner te revient, avec ses améliorations de vitesse et de quantité.", "light_purple")])
fn("machine/rv_sp_lire", [f"{S} operation #sf i.t = @s i.sf", f"{S} operation #spv i.t = @s i.spv", f"{S} operation #spq i.t = @s i.spq"])

# 28/11/2026 : tubes refaits pour les machines déjà posées (tag ind.t2 = tube de la nouvelle forme)
fn("tube/refaire", [
    f"{S} operation #me i.t = @s i.own", f"{S} operation #sel i.t = @s i.sid",
    f"execute as @e[tag=ind.tube,distance=..400] if score @s i.own = #me i.t if score @s i.sid = #sel i.t run kill @s",
    f"{S} operation #pm i.t = @s i.mt", f"{S} operation #own i.t = @s i.own", f"{S} operation #psid i.t = @s i.sid", f"{S} set #tt i.t 0",
    f"execute as @a if score @s m.id = #me i.t run {S} operation #tt i.t = @s i.tube",
    "tag @s add ind.t4", f"function {NS}:tube/poser"])

# -*- coding: utf-8 -*-
# 27/11/2026 : skins v2. 12 skins (6 nouveaux dont 4 légendaires qui changent la forme des outils) et nouvelle
# interface : la liste ouvre une fiche par skin avec l'aperçu 3D de ton objet à son palier, le prix, ce qu'il te
# manque, puis Acheter / Équiper / Retirer. Textures : sources/resourcepack/gen5.py.
# Déclencheurs : 4300 + i ouvre la fiche du skin i (0 = apparence de base), 4320 + i achète ou équipe (430 + i reste
# valable pour les skins 0 à 6, 440 à 447 sont aux cadres).
SK2 = F + "skins/"

add_lines(F + "refonte/load.mcfunction", [
    "scoreboard objectives add m.kwarden minecraft.killed:minecraft.warden",
    "scoreboard objectives add m.kdragon minecraft.killed:minecraft.ender_dragon",
    "scoreboard objectives add m.skf dummy"])

DESC = {
    1: "Acier bleu glacé, éclats de glace.", 2: "Métal turquoise des grands fonds, gemmes corail.", 3: "Or massif serti de rubis.",
    4: "Os blanchis et lueur verte.", 5: "Roche en fusion, lueur orange.", 6: "Métal d’ombre violet, lueur du Vide.",
    7: "Nacre rose et bois de cerisier, lueur rose.", 8: "Marbre blanc et or pâle, lueur cyan.",
    9: "LÉGENDAIRE : change la forme de tes outils (trident au nautile, ancre, tentacules). Bleu des grands fonds, lueur turquoise.",
    10: "LÉGENDAIRE : change la forme de tes outils (mâchoire de hurleur, côtes, vrilles). Noir sculk, lueur cyan.",
    11: "LÉGENDAIRE : change la forme de tes outils (croc qui sort d’une gueule de dragon, ailes). Écailles violettes, lueur magenta.",
    12: "LÉGENDAIRE : change la forme de tes outils (soleil en gyroscope, flammes, croissant de lune). Noir mat et or ardent."}
LEG = {9, 10, 11, 12}

# 27/11/2026 (après essai en jeu) : tous les skins se paient en Écus et en éclats de boss, plus de cristaux de métier.
# (éclats, Écus, condition en plus) ; même prix pour l'armure et les outils.
PRIX = {1: (3, 15000, None), 2: (3, 15000, None), 3: (5, 30000, None),
        4: (6, 40000, ("m.bk2", 3, "vaincre 3 fois la Reine arachnide")), 5: (6, 40000, ("m.bk4", 3, "vaincre 3 fois le Brasier ancestral")),
        6: (8, 60000, "p1"), 7: (8, 60000, None), 8: (12, 100000, None),
        9: (15, 120000, ("m.bk3", 10, "vaincre 10 fois la Liche du givre")), 10: (15, 120000, ("m.kwarden", 5, "tuer 5 Wardens")),
        11: (20, 150000, ("m.kdragon", 3, "tuer 3 fois l’Ender Dragon")), 12: (25, 250000, "p2")}
def ecus_txt(u):
    return f"{u:,}".replace(",", " ")
def court(i):
    e, u, _c = PRIX[i]
    return f"{e} éc. · {u // 1000} k"
def regle(t, i):
    """(texte du prix, condition « if ... » pour pouvoir l'acheter, commandes de paiement) pour la cible t et le skin i."""
    e, u, c = PRIX[i]
    txt = f"{e} éclats de boss et {ecus_txt(u)} Écus"
    cond = f"if score @s m.ecl matches {e}.. if score @s c.ecus matches {u}.."
    if c == "p1":
        pre, cc = (("un prestige dans n’importe quel métier", "if score @s m.prtot matches 1..") if t == "a" else
                   ("une étoile de prestige dans ce métier", f"if score @s m.{t}_pr matches 1.."))
    elif c == "p2":
        pre, cc = (("5 prestiges au total", "if score @s m.prtot matches 5..") if t == "a" else
                   ("2 étoiles de prestige dans ce métier", f"if score @s m.{t}_pr matches 2.."))
    elif c:
        pre, cc = c[2], f"if score @s {c[0]} matches {c[1]}.."
    else:
        pre, cc = None, ""
    if pre:
        txt = f"{pre[0].upper() + pre[1:]}, puis {txt}"
        cond = f"{cc} {cond}"
    return (txt, cond, [f"scoreboard players remove @s m.ecl {e}", f"scoreboard players remove @s c.ecus {u}"])

N = len(SKIN_IDS)
# ---------------------------------------------------------------- achat / équipement des 12 skins (remplace ceux de ref_menu.py)
for ti, (t, nom) in enumerate(TGT):
    REG = (f"execute if score @s m.arm matches 1.. if items entity @s armor.* {ASEL} run function {NS}:armure/donner" if t == "a" else
           f"execute if items entity @s container.* {SEL(t)} run function {NS}:{t}/outil_donner")
    for i in range(1, N + 1):
        sn = SKIN_NOM[i - 1]
        prix, cond, pay = regle(t, i)
        A = [f"execute if score @s m.so_{t}{i} matches 1 if score @s m.skin_{t} matches {i} run return run function {NS}:skins/equiper {{t:\"{t}\",i:0}}",
             f"execute if score @s m.so_{t}{i} matches 1 run return run function {NS}:skins/equiper {{t:\"{t}\",i:{i}}}",
             "scoreboard players set #ok m.tmp 0", f"execute {cond} run scoreboard players set #ok m.tmp 1",
             f"execute if score #ok m.tmp matches 0 run return run {tr(f'Pas encore : {prix}.', 'red')}"]
        A += pay + [f"scoreboard players set @s m.so_{t}{i} 1", tr(f"Skin {sn} débloqué !", "light_purple"),
                    "execute at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1.2",
                    "execute at @s run particle minecraft:totem_of_undying ~ ~1 ~ 0.4 0.8 0.4 0.3 40",
                    f"function {NS}:skins/equiper {{t:\"{t}\",i:{i}}}"]
        w(SK2 + f"acheter_{t}_{i}.mcfunction", "\n".join(A))
for i in range(N + 1):
    D = [f"execute if score @s m.skt matches {ti} run return run function {NS}:skins/{'acheter_' + t + '_' + str(i) if i else 'base_' + t}" for ti, (t, _) in enumerate(TGT)]
    w(SK2 + f"choix_{i}.mcfunction", "\n".join(D))
# après un achat ou un changement : retour sur la fiche ouverte (ou sur la liste)
w(SK2 + "equiper.mcfunction", "\n".join([
    "$scoreboard players set @s m.skin_$(t) $(i)", "$function metiers:skins/regive_$(t)",
    "playsound minecraft:item.armor.equip_leather master @s ~ ~ ~ 1 1.2",
    f"execute if score @s m.skf matches 0.. run return run function {NS}:skins/fiche_retour",
    f"function {NS}:skins/menu"]))
w(SK2 + "fiche_retour.mcfunction", "\n".join(
    [f"execute if score @s m.skf matches {i} run return run function {NS}:skins/fiche_{i}" for i in range(N + 1)]))

# ---------------------------------------------------------------- aperçus : glyphes de la police metiers:apercu (resourcepack/gen6.py)
# cible n° ti (ordre TGT), skin i (0 = base) : grand U+E000 + 13 ti + i, petit U+E200 + 13 ti + i
GRAND = lambda ti, i: chr(0xE000 + 13 * ti + i)
PETIT = lambda ti, i: chr(0xE200 + 13 * ti + i)
SAUTS = "\\n" * 11   # le grand aperçu (96 px) déborde sous sa ligne : on lui laisse la place

# ---------------------------------------------------------------- liste (skins/menu) : aperçu + nom + prix sur chaque bouton
for ti, (t, _) in enumerate(TGT):
    L = [f'data modify storage {NS}:sk g{i} set value "{PETIT(ti, i)}"' for i in range(N + 1)]
    L += [f'data modify storage {NS}:sk gc set value "{GRAND(ti, 0)}"']
    L += [f'execute if score @s m.skin_{t} matches {i} run data modify storage {NS}:sk gc set value "{GRAND(ti, i)}"' for i in range(1, N + 1)]
    for i in range(1, N + 1):
        prix, cond, _p = regle(t, i)
        sn = SKIN_NOM[i - 1]
        L += [f'data modify storage {NS}:sk s{i} set value "{"✦ " if i in LEG else ""}{sn}"', f'data modify storage {NS}:sk k{i} set value "dark_gray"',
              f'execute {cond} run data modify storage {NS}:sk k{i} set value "yellow"',
              f'data modify storage {NS}:sk p{i} set value "{court(i)}"',
              f'execute if score @s m.so_{t}{i} matches 1 run data modify storage {NS}:sk k{i} set value "green"',
              f'execute if score @s m.so_{t}{i} matches 1 run data modify storage {NS}:sk p{i} set value "à toi"',
              f'execute if score @s m.skin_{t} matches {i} run data modify storage {NS}:sk s{i} set value "★ {sn}"',
              f'execute if score @s m.skin_{t} matches {i} run data modify storage {NS}:sk k{i} set value "gold"',
              f'execute if score @s m.skin_{t} matches {i} run data modify storage {NS}:sk p{i} set value "équipé"']
    add_lines(SK2 + f"infos_{t}.mcfunction", L)
LBTN = [f'{{label:[{{text:"$(g{i}) ",font:"metiers:apercu",color:"white"}},{{text:"$(s{i})",color:"$(k{i})"}},{{text:"  $(p{i})",color:"gray"}}],width:200,'
        f'tooltip:{{text:"{DESC[i]}\\nPrix : {regle("b", i)[0] if i != 6 and i != 12 else "voir la fiche"}\\nClique pour voir l’aperçu en grand."}},'
        f'action:{{type:"run_command",command:"trigger metiers set {4300 + i}"}}}}' for i in range(1, N + 1)]
w(SK2 + "menu.mcfunction", "\n".join(["scoreboard players set @s m.skf -1", f"function {NS}:skins/calcul",
                                      f"function {NS}:skins/menu_dialog with storage {NS}:sk"]))
w(SK2 + "menu_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Skins d’outil et d’armure",color:"light_purple",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:plain_message",width:400,contents:[{text:"$(cible)",color:"aqua",bold:true},{text:" · skin actuel\\n",color:"gray"},'
  '{text:"$(gc)",font:"metiers:apercu",color:"white"},{text:"' + SAUTS + '"},'
  '{text:"Vert : à toi · jaune : achetable · gris : pas encore. ",color:"gray"},{text:"✦ légendaire",color:"light_purple"},'
  '{text:" : change la forme des outils et du casque.\\nPrix en éclats de boss et en Écus.",color:"gray"}]}],'
  'actions:[{label:[{text:"Objet : ",color:"gray"},{text:"$(cible)",color:"aqua"},{text:"  ↻",color:"gray"}],width:200,'
  'tooltip:{text:"Passer à l’objet suivant : l’armure ou l’un de tes 9 outils de métier."},action:{type:"run_command",command:"trigger metiers set 421"}},'
  '{label:[{text:"$(g0) ",font:"metiers:apercu",color:"white"},{text:"Apparence de base",color:"white"}],width:200,action:{type:"run_command",command:"trigger metiers set 4300"}},'
  f'{",".join(LBTN)}],columns:2,'
  'exit_action:{label:"Retour",width:200,action:{type:"run_command",command:"trigger metiers set 1"}}}')
w(SK2 + "cycle.mcfunction", "scoreboard players add @s m.skt 1\nexecute if score @s m.skt matches 10.. run scoreboard players set @s m.skt 0\nfunction metiers:skins/menu")

# ---------------------------------------------------------------- fiche d'un skin : grand aperçu, prix, état, action
for i in range(N + 1):
    sid = "" if i == 0 else SKIN_IDS[i - 1]
    sn = "Apparence de base" if i == 0 else SKIN_NOM[i - 1]
    FI = [f"scoreboard players set @s m.skf {i}", f"function {NS}:skins/calcul",
          f'data modify storage {NS}:sk fs set value "{sid}"', f'data modify storage {NS}:sk fn set value "{("✦ " if i in LEG else "") + sn}"',
          f'data modify storage {NS}:sk fd set value "{DESC.get(i, "Ton objet tel que son palier le dessine, sans skin.")}"',
          f'data modify storage {NS}:sk fl set value "{"Sur l’armure : casque à forme propre et motifs peints sur toute l’armure." if i in LEG else ""}"',
          f"scoreboard players set #pr m.tmp {(i - 1) % (N + 1)}", f"scoreboard players add #pr m.tmp 4300",
          f"scoreboard players set #su m.tmp {(i + 1) % (N + 1)}", "scoreboard players add #su m.tmp 4300",
          f"execute store result storage {NS}:sk fp int 1 run scoreboard players get #pr m.tmp",
          f"execute store result storage {NS}:sk fv int 1 run scoreboard players get #su m.tmp",
          f"data modify storage {NS}:sk fa set value {4320 + i}",
          "scoreboard players set #ec m.tmp 0",
          "execute if score @s c.ecus matches -2147483648.. run scoreboard players operation #ec m.tmp = @s c.ecus"]
    for ti, (t, _) in enumerate(TGT):
        base = f"execute if score @s m.skt matches {ti}"
        FI.append(f'{base} run data modify storage {NS}:sk gb set value "{GRAND(ti, i)}"')
        if i == 0:
            FI += [f'{base} run data modify storage {NS}:sk fc set value "Gratuit"',
                   f'{base} run data modify storage {NS}:sk fe set value "Toujours disponible"',
                   f'{base} run data modify storage {NS}:sk fk set value "green"',
                   f'{base} run data modify storage {NS}:sk fb set value "Remettre l’apparence de base"']
            continue
        prix, cond, _p = regle(t, i)
        FI += [f'{base} run data modify storage {NS}:sk fc set value "{prix}"',
               f'{base} run data modify storage {NS}:sk fe set value "Pas encore débloqué"', f'{base} run data modify storage {NS}:sk fk set value "red"',
               f'{base} run data modify storage {NS}:sk fb set value "Il te manque encore quelque chose"',
               f'{base} {cond} run data modify storage {NS}:sk fe set value "Tu peux l’acheter"', f'{base} {cond} run data modify storage {NS}:sk fk set value "yellow"',
               f'{base} {cond} run data modify storage {NS}:sk fb set value "Acheter et équiper"',
               f'{base} if score @s m.so_{t}{i} matches 1 run data modify storage {NS}:sk fe set value "Débloqué"',
               f'{base} if score @s m.so_{t}{i} matches 1 run data modify storage {NS}:sk fk set value "green"',
               f'{base} if score @s m.so_{t}{i} matches 1 run data modify storage {NS}:sk fb set value "Équiper"',
               f'{base} if score @s m.skin_{t} matches {i} run data modify storage {NS}:sk fe set value "Équipé"',
               f'{base} if score @s m.skin_{t} matches {i} run data modify storage {NS}:sk fk set value "gold"',
               f'{base} if score @s m.skin_{t} matches {i} run data modify storage {NS}:sk fb set value "Retirer (apparence de base)"']
    FI += [f"execute store result storage {NS}:sk fec int 1 run scoreboard players get #ec m.tmp",
           "scoreboard players add @s m.bk2 0", "scoreboard players add @s m.bk3 0", "scoreboard players add @s m.bk4 0",
           "scoreboard players add @s m.kwarden 0", "scoreboard players add @s m.kdragon 0",
           f"execute store result storage {NS}:sk fre int 1 run scoreboard players get @s m.bk2",
           f"execute store result storage {NS}:sk fli int 1 run scoreboard players get @s m.bk3",
           f"execute store result storage {NS}:sk fbr int 1 run scoreboard players get @s m.bk4",
           f"execute store result storage {NS}:sk fwa int 1 run scoreboard players get @s m.kwarden",
           f"execute store result storage {NS}:sk fdr int 1 run scoreboard players get @s m.kdragon",
           f"execute store result storage {NS}:sk fpt int 1 run scoreboard players get @s m.prtot",
           f"function {NS}:skins/fiche_dialog with storage {NS}:sk"]
    w(SK2 + f"fiche_{i}.mcfunction", "\n".join(FI))
w(SK2 + "fiche_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"$(fn)",color:"light_purple",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:plain_message",width:400,contents:[{text:"$(cible)\\n",color:"aqua",bold:true},'
  '{text:"$(gb)",font:"metiers:apercu",color:"white"},{text:"' + SAUTS + '"},'
  '{text:"$(fd)\\n",color:"white"},{text:"$(fl)\\n",color:"gray"},'
  '{text:"Prix : ",color:"gold",bold:true},{text:"$(fc)\\n",color:"yellow"},{text:"$(fe)",color:"$(fk)",bold:true}]},'
  '{type:"minecraft:plain_message",width:400,contents:[{text:"Tu as : ",color:"gray"},{text:"$(ecl) éclats de boss · $(fec) Écus",color:"white"},'
  '{text:"\\nTrophées : ",color:"gray"},{text:"Reine $(fre)/3 · Brasier $(fbr)/3 · Liche $(fli)/10 · Wardens $(fwa)/5 · Ender Dragon $(fdr)/3 · prestiges $(fpt)",color:"white"}]}],'
  'actions:[{label:{text:"$(fb)",color:"$(fk)",bold:true},width:310,action:{type:"run_command",command:"trigger metiers set $(fa)"}},'
  '{label:{text:"◀ Skin précédent",color:"gray"},width:150,action:{type:"run_command",command:"trigger metiers set $(fp)"}},'
  '{label:{text:"Skin suivant ▶",color:"gray"},width:150,action:{type:"run_command",command:"trigger metiers set $(fv)"}}],columns:2,'
  'exit_action:{label:"Retour à la liste",width:200,action:{type:"run_command",command:"trigger metiers set 420"}}}')

add_lines(F + "trigger.mcfunction",
          [f'execute if score @s m.trig matches {4300 + i} run function {NS}:appel {{f:"skins/fiche_{i}"}}' for i in range(N + 1)] +
          [f'execute if score @s m.trig matches {4320 + i} run function {NS}:appel {{f:"skins/choix_{i}"}}' for i in range(N + 1)])

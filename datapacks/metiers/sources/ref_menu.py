# -*- coding: utf-8 -*-
# Refonte v24, partie 3 : menus (accueil, page métier), titres et cadres, Forge, skins.

def btn(label, action=None, width=150, tooltip=None):
    s = f"{{label:{label},width:{width}"
    if tooltip: s += f',tooltip:{{text:"{tooltip}"}}'
    if action is not None: s += f',action:{{type:"run_command",command:"trigger metiers set {action}"}}'
    return s + "}"

def txt(t, col="white", bold=False):
    return f'{{text:"{t}",color:"{col}",bold:{"true" if bold else "false"},italic:false}}'

CRP = {"marteau": ("m", 260, 4, 50), "faux": ("f", 220, 3, 50), "arc3": ("c", 300, 5, 60), "lasso": ("e", 140, 1, 40), "parchemin": ("n", 60, 0, 40)}
COMMUN = {"aimant": 6, "cape": 12}
EFFC = [40, 70, 110, 150, 200, 260, 330]
EFFL = [10, 20, 30, 40, 50, 60, 80]
CRIS = {"sagesse": (90, 20, "csag", None), "fortune": (160, 40, "cfor", tuple(FORT_KEY)), "echo": (240, 60, "ceco", None)}

# ================================================================ accueil
MN = [f"function {NS}:classement/maj" if False else "scoreboard players add @s m.total 0",
      f"execute store result storage {NS}:mn score int 1 run scoreboard players get @s m.total",
      f"execute store result storage {NS}:mn ecl int 1 run scoreboard players get @s m.ecl",
      "scoreboard players add @s m.arm 0",
      f'data modify storage {NS}:mn arm set value "pas encore débloquée"']
for p in range(11):
    MN.append(f'execute if score @s m.arm matches {p + 1} run data modify storage {NS}:mn arm set value "palier {p} ({ARM_NOM[p]})"')
for j, d in jobs.items():
    MN += [f"execute store result storage {NS}:mn {j}_l int 1 run scoreboard players get @s m.{j}_lvl",
           f"scoreboard players operation @s m.tmp = @s m.{j}_xp", "scoreboard players operation @s m.tmp *= #10 m.const",
           f"scoreboard players operation @s m.tmp /= @s m.{j}_need",
           f"execute if score @s m.{j}_lvl matches {MAXLVL}.. run scoreboard players set @s m.tmp 10"]
    MN += ["execute if score @s m.tmp matches 11.. run scoreboard players set @s m.tmp 10", "execute if score @s m.tmp matches ..-1 run scoreboard players set @s m.tmp 0"] + [f'data modify storage {NS}:mn {j}_b set value "{GLY["barre_0"]}"']
    MN += [f'execute if score @s m.tmp matches {k} run data modify storage {NS}:mn {j}_b set value "{GLY["barre_" + str(k)]}"' for k in range(11)]
    MN += [f'data modify storage {NS}:mn {j}_d set value ""',
           f"function {NS}:{j}/points",
           f'execute if score @s m.tmp matches 6.. unless entity @s[tag=metiers.sk.{j}1,tag=metiers.sk.{j}2,tag=metiers.sk.{j}3,tag=metiers.sk.{j}4,tag=metiers.sk.{j}5,tag=metiers.sk.{j}6] if score @s m.{j}_lvl matches 5.. run data modify storage {NS}:mn {j}_d set value " ●"',
           f"scoreboard players operation @s m.tmp = @s m.{j}_lvl", "scoreboard players operation @s m.tmp /= #10 m.const",
           f'execute if score @s m.{j}_pal < @s m.tmp run data modify storage {NS}:mn {j}_d set value " ●"']
MN.append(f"function {NS}:menu_dialog with storage {NS}:mn")
w(F + "menu.mcfunction", "\n".join(MN))
acts = []
for j, d in jobs.items():
    lab = f'[{gs("metier_" + j)},{txt(" " + d["name"] + " ", d["color"])},{txt("$(" + j + "_l) ", "yellow")},{{text:"$({j}_b)",font:"metiers:icones",color:"white"}},{txt("$(" + j + "_d)", "red")}]'
    acts.append(btn(lab, 20 + d["idx"], 200, f"Ouvre la page {d['name']} : outil, compétences, récompenses, titre."))
forge_lab = f'[{gs("forge_marteau")},{txt("  Forge  ", "gold", True)},{gs("eclat")},{txt(" $(ecl) éclats", "gray")}]'
acts += [btn(txt("Défis du jour", "aqua"), 4, 200), btn(txt("Classement", "gold"), 5, 200),
         btn(txt("Armure des Guildes", "#F1CF4E"), 6, 200), btn(forge_lab, 400, 200, "Objets de métier, cristaux d'amélioration, skins et cadres de titre.")]
w(F + "menu_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Mes métiers",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:plain_message",width:400,contents:[{text:"Score total ",color:"gray"},{text:"$(score)",color:"yellow"},'
  '{text:"   ·   Armure des Guildes : ",color:"gray"},{text:"$(arm)",color:"gold"},{text:"\\nUn point rouge : des points de compétence ou une récompense t\'attendent.",color:"dark_gray"}]}],'
  f'actions:[{",".join(acts)}],columns:2,'
  f'exit_action:{{label:"Fermer",width:200}}}}')

# ================================================================ page métier (remplace l'ancien écran de l'arbre)
NEXTTXT = {}
for j, d in jobs.items():
    for k in range(10):
        nt = R[j][k + 1][0]["name"]
        NEXTTXT[(j, k)] = f"Niveau {10 * (k + 1)} : {nt}, titre {TIERS[k + 1][0]}, {CRIST[k + 1]} cristaux"
SPECIAL = {"f": (610, "Saison des moissons", "green", "Une fois par jour de jeu : toutes les cultures à 12 blocs mûrissent (compétence ultime)."),
           "n": (611, "Surpuissance", "light_purple", "Objet enchanté en main : +1 niveau à tous ses enchantements, 30 niveaux d’XP (compétence ultime)."),
           "x": (612, "Récupérer mon sac à dos", "blue", "Sac à dos : 18 cases au niveau 20, 27 au niveau 50, 2 pages au niveau 80."),
           "c": (613, "Récupérer mon arc", "red", "L’arc du Chasseur évolue en même temps que ton épée."),
           "p": (70, "Carnet du pêcheur", "aqua", "Tes poissons légendaires."),
           "b": (400, "Ouvrir la Forge", "gold", "Dépense tes cristaux de métier."), "m": (400, "Ouvrir la Forge", "gold", "Dépense tes cristaux de métier."),
           "e": (400, "Ouvrir la Forge", "gold", "Dépense tes cristaux de métier."), "t": (400, "Ouvrir la Forge", "gold", "Dépense tes cristaux de métier.")}
for j, d in jobs.items():
    sk = SKILLS[j]
    P = [f"function {NS}:{j}/points", f"execute store result storage {NS}:pg pts int 1 run scoreboard players get @s m.tmp",
         f"scoreboard players operation #pts m.tmp = @s m.tmp",
         f"execute store result storage {NS}:pg lvl int 1 run scoreboard players get @s m.{j}_lvl",
         f"execute store result storage {NS}:pg xp int 1 run scoreboard players get @s m.{j}_xp",
         f"execute store result storage {NS}:pg need int 1 run scoreboard players get @s m.{j}_need",
         f"execute store result storage {NS}:pg cr int 1 run scoreboard players get @s m.cr_{j}",
         f"execute store result storage {NS}:pg out int 1 run scoreboard players get @s m.{j}_out",
         f'data modify storage {NS}:pg titre set value "{TIERS[0][0]}"',
         f'data modify storage {NS}:pg next set value "Palier maximum atteint"',
         f"function {NS}:{j}/outil_params",
         f"data modify storage {NS}:pg skin set from storage {NS}:tmp skin"]
    for t, (nom, rng) in enumerate(TIERS):
        P.append(f'execute if score @s m.{j}_lvl matches {rng} run data modify storage {NS}:pg titre set value "{nom}"')
    P.append(f'data modify storage {NS}:pg model set value "{j}_0"')
    for k in range(11):
        P.append(f'execute if score @s m.{j}_out matches {k} run data modify storage {NS}:pg model set value "{j}_{k}"')
        if k < 10:
            P.append(f'execute if score @s m.{j}_out matches {k} run data modify storage {NS}:pg next set value "{NEXTTXT[(j, k)]}"')
    P += [f"scoreboard players operation @s m.tmp = @s m.{j}_xp", "scoreboard players operation @s m.tmp *= #10 m.const",
          f"scoreboard players operation @s m.tmp /= @s m.{j}_need", f"execute if score @s m.{j}_lvl matches {MAXLVL}.. run scoreboard players set @s m.tmp 10"]
    P += ["execute if score @s m.tmp matches 11.. run scoreboard players set @s m.tmp 10", "execute if score @s m.tmp matches ..-1 run scoreboard players set @s m.tmp 0"] + [f'data modify storage {NS}:pg bar set value "{GLY["barre_0"]}"']
    P += [f'execute if score @s m.tmp matches {k} run data modify storage {NS}:pg bar set value "{GLY["barre_" + str(k)]}"' for k in range(11)]
    def reqsel2(req):
        return ",".join(f"tag=metiers.sk.{j}{r}" for r in req)
    for k, (name, cost, req, desc) in enumerate(sk, 1):
        lv = SKILL_LVL[k - 1]
        cond = f"execute if entity @s[{reqsel2(req)}]" if req else "execute if entity @s"
        P += [f'data modify storage {NS}:pg l{k} set value "✖ {name}"', f'data modify storage {NS}:pg c{k} set value "dark_gray"',
              f'execute unless score @s m.{j}_lvl matches {lv}.. run data modify storage {NS}:pg l{k} set value "✖ {name} · niv. {lv}"',
              f'execute if score @s m.{j}_lvl matches {lv}.. {cond[8:]} run data modify storage {NS}:pg l{k} set value "{name} · {cost} pts"'
              if req else f'execute if score @s m.{j}_lvl matches {lv}.. run data modify storage {NS}:pg l{k} set value "{name} · {cost} pts"',
              (f'execute if score @s m.{j}_lvl matches {lv}.. {cond[8:]} run data modify storage {NS}:pg c{k} set value "yellow"' if req else
               f'execute if score @s m.{j}_lvl matches {lv}.. run data modify storage {NS}:pg c{k} set value "yellow"'),
              (f'execute if score @s m.{j}_lvl matches {lv}.. {cond[8:]} if score #pts m.tmp matches ..{cost - 1} run data modify storage {NS}:pg c{k} set value "red"' if req else
               f'execute if score @s m.{j}_lvl matches {lv}.. if score #pts m.tmp matches ..{cost - 1} run data modify storage {NS}:pg c{k} set value "red"'),
              f'execute if entity @s[tag=metiers.sk.{j}{k}] run data modify storage {NS}:pg l{k} set value "✔ {name}"',
              f'execute if entity @s[tag=metiers.sk.{j}{k}] run data modify storage {NS}:pg c{k} set value "green"']
    P += ["scoreboard players operation @s m.tmp = @s m.{0}_lvl".format(j), "scoreboard players operation @s m.tmp /= #10 m.const",
          f'data modify storage {NS}:pg rl set value "Aucune récompense"', f'data modify storage {NS}:pg rc set value "dark_gray"',
          f'execute if score @s m.{j}_pal < @s m.tmp run data modify storage {NS}:pg rl set value "Récompense à prendre ●"',
          f'execute if score @s m.{j}_pal < @s m.tmp run data modify storage {NS}:pg rc set value "light_purple"',
          f'data modify storage {NS}:pg tl set value "Afficher ce titre"', f'data modify storage {NS}:pg tc set value "yellow"',
          f'execute if score @s m.pref matches {d["idx"]} run data modify storage {NS}:pg tl set value "Titre affiché ✔"',
          f'execute if score @s m.pref matches {d["idx"]} run data modify storage {NS}:pg tc set value "green"',
          f'data modify storage {NS}:pg pl set value "Prestige au niveau 100"', f'data modify storage {NS}:pg pc set value "dark_gray"',
          f'execute if score @s m.{j}_lvl matches {MAXLVL}.. run data modify storage {NS}:pg pl set value "★ Prestige disponible"',
          f'execute if score @s m.{j}_lvl matches {MAXLVL}.. run data modify storage {NS}:pg pc set value "gold"',
          f"function {NS}:{j}/page_dialog with storage {NS}:pg"]
    w(F + f"{j}/arbre.mcfunction", "\n".join(P))
    sbtn = []
    for k, (name, cost, req, desc) in enumerate(sk, 1):
        rq = " + ".join(sk[r - 1][0] for r in req) if req else "rien"
        tip = f"{desc}\\nCoût : {cost} points · niveau {SKILL_LVL[k - 1]} · requiert : {rq}"
        sbtn.append(f'{{label:{{text:"$(l{k})",color:"$(c{k})"}},width:200,tooltip:{{text:"{tip}"}},action:{{type:"run_command",command:"trigger metiers set {100 + 10 * d["idx"] + k}"}}}}')
    sp = SPECIAL[j]
    abtn = [btn(txt("Récupérer l'outil", "aqua"), 300 + d["idx"], 200, "Redonne ton outil à son palier (une fois toutes les 10 minutes)."),
            btn(txt("Réparer · 5 niv.", "green"), 330 + d["idx"], 200, "Seule façon de réparer ton outil de métier. Incassable dès le palier 5."),
            f'{{label:{{text:"$(rl)",color:"$(rc)"}},width:200,action:{{type:"run_command",command:"trigger metiers set {200 + d["idx"]}"}}}}',
            f'{{label:{{text:"$(tl)",color:"$(tc)"}},width:200,tooltip:{{text:"Affiche ton titre de {d["name"]} devant ton pseudo. Le cadre se choisit à la Forge."}},action:{{type:"run_command",command:"trigger metiers set {600 + d["idx"]}"}}}}',
            btn(txt(sp[1], sp[2]), sp[0], 200, sp[3]),
            f'{{label:{{text:"$(pl)",color:"$(pc)"}},width:200,tooltip:{{text:"Au niveau 100 : repars au niveau 1 avec une étoile et +10 % d’XP par étoile (5 max)."}},action:{{type:"run_command",command:"trigger metiers set {310 + d["idx"]}"}}}}']
    body = ('[{type:"minecraft:item",item:{id:"minecraft:paper",components:{"minecraft:item_model":"metiers:$(model)","minecraft:custom_model_data":{strings:["$(skin)"]}}},'
            'show_decorations:false,show_tooltip:false,description:{width:260,contents:['
            f'{{text:"$(titre) {d["name"]}\\n",color:"{d["color"]}",bold:true}},{{text:"Niveau $(lvl)   ",color:"yellow",bold:false}},'
            '{text:"$(bar)",font:"metiers:icones",color:"white"},{text:"  $(xp) / $(need) XP\\n",color:"gray"},'
            f'{{text:"Outil au palier $(out) sur 10",color:"gray"}}]}}}},'
            '{type:"minecraft:plain_message",width:380,contents:[{text:"$(next)\\n",color:"gold"},'
            f'{{text:"Points de compétence : ",color:"gray"}},{{text:"$(pts)",color:"yellow"}},{{text:"   ·   ",color:"gray"}},{gs("cristal_" + j)},{{text:" $(cr) cristaux\\n",color:"aqua"}},'
            '{text:"Survole une compétence pour voir son effet.",color:"dark_gray"}]}]')
    w(F + f"{j}/page_dialog.mcfunction",
      f'$dialog show @s {{type:"minecraft:multi_action",title:[{gs("metier_" + j)},{{text:" {d["name"]}",color:"{d["color"]}",bold:true}}],'
      f'can_close_with_escape:true,pause:false,body:{body},actions:[{",".join(sbtn + abtn)}],columns:2,'
      f'exit_action:{{label:"Retour",width:200,action:{{type:"run_command",command:"trigger metiers set 1"}}}}}}')
    # bascule du titre de ce métier
    w(F + f"{j}/titre.mcfunction", "\n".join([
        f"execute if score @s m.pref matches {d['idx']} run scoreboard players set @s m.trig 10",
        f"execute unless score @s m.pref matches {d['idx']} run scoreboard players set @s m.trig {10 + d['idx']}",
        f"function {NS}:prefixe/choisir", f"function {NS}:{j}/arbre"]))

# ================================================================ titres + cadres (équipes)
CADRES = ["bois", "fer", "dore", "runique", "flammes", "celeste"]
CADRE_NOM = ["Bois", "Fer forgé", "Doré", "Runique", "Flammes", "Céleste"]
def team_prefix2(j, t, st, fr):
    parts = [{"text": "", "color": "white"}]
    if st:
        parts.append({"text": "★" * st + " ", "color": "gold", "bold": False})
    if fr:
        parts.append(gj(f"cadre_{CADRES[fr - 1]}_g"))
    sty = dict(tier_style(j, t)); sty["text"] = f"{TIERS[t][0]}"
    parts.append(gj(f"metier_{j}"))
    parts.append({"text": " ", "color": "white"})
    parts.append(sty)
    if fr:
        parts.append(gj(f"cadre_{CADRES[fr - 1]}_d"))
    parts.append({"text": " ", "color": "white", "bold": False})
    return json.dumps(parts, ensure_ascii=False)
E2 = []
for j in jobs:
    for t in range(11):
        E2.append(f"team remove m.{j}{t}")
        for st in range(6):
            E2.append(f"team remove m.{j}{t}_{st}")
            for fr in range(7):
                E2 += [f"team add m.{j}{t}_{st}_{fr}", f"team modify m.{j}{t}_{st}_{fr} prefix {team_prefix2(j, t, st, fr)}"]
w(F + "prefixe/equipes.mcfunction", "\n".join(E2))
MJ2 = ["tag @s remove metiers.maj", "scoreboard players add @s m.cadre 0"]
for j, d in jobs.items():
    for t, (_, rng) in enumerate(TIERS):
        for st in range(6):
            for fr in range(7):
                MJ2.append(f"execute if score @s m.pref matches {d['idx']} if score @s m.{j}_lvl matches {rng} if score @s m.{j}_pr matches {st} if score @s m.cadre matches {fr} run team join m.{j}{t}_{st}_{fr} @s")
w(F + "prefixe/maj.mcfunction", "\n".join(MJ2))

# ================================================================ Forge
FG = [f"execute store result storage {NS}:fg ecl int 1 run scoreboard players get @s m.ecl"]
FG += [f"execute store result storage {NS}:fg cr_{j} int 1 run scoreboard players get @s m.cr_{j}" for j in JL]
for key, (j, p, e, lv) in CRP.items():
    FG += [f'data modify storage {NS}:fg c_{key} set value "red"',
           f'execute if score @s m.cr_{j} matches {p}.. if score @s m.ecl matches {e}.. run data modify storage {NS}:fg c_{key} set value "yellow"',
           f'execute unless score @s m.{j}_lvl matches {lv}.. run data modify storage {NS}:fg c_{key} set value "dark_gray"']
for key, e in COMMUN.items():
    FG += [f'data modify storage {NS}:fg c_{key} set value "red"', f'execute if score @s m.ecl matches {e}.. run data modify storage {NS}:fg c_{key} set value "yellow"']
# outil tenu en main pour les cristaux d'amélioration
FG += [f'data modify storage {NS}:fg g set value ""', f"data modify storage {NS}:fg sl set value 0", f"data modify storage {NS}:fg us set value 0", "scoreboard players set #hj m.tmp 0", f'data modify storage {NS}:fg outil set value "Tiens ton outil de métier en main pour sertir un cristal."']
for j, d in jobs.items():
    FG.append(f"execute if items entity @s weapon.mainhand {SEL(j)} run scoreboard players set #hj m.tmp {d['idx']}")
FG += [f'data modify storage {NS}:fg {c} set value "—"' for c in ("l_sag", "l_for", "l_eco", "l_eff")]
FG += [f'data modify storage {NS}:fg {c} set value "dark_gray"' for c in ("k_sag", "k_for", "k_eco", "k_eff")]
for j, d in jobs.items():
    FG.append(f"execute if score #hj m.tmp matches {d['idx']} run function {NS}:forge/infos_{j}")
FG.append(f"function {NS}:forge/menu_dialog with storage {NS}:fg")
w(F + "forge/menu.mcfunction", "\n".join(FG))
for j, d in jobs.items():
    I = ["scoreboard players set #sl m.tmp 0",
         f"execute if score @s m.{j}_out matches 3.. run scoreboard players add #sl m.tmp 1",
         f"execute if score @s m.{j}_out matches 6.. run scoreboard players add #sl m.tmp 1",
         f"execute if score @s m.{j}_out matches 9.. run scoreboard players add #sl m.tmp 1",
         f"scoreboard players operation #us m.tmp = @s m.csag_{j}", f"scoreboard players operation #us m.tmp += @s m.cfor_{j}",
         f"scoreboard players operation #us m.tmp += @s m.ceco_{j}",
         f"execute store result storage {NS}:fg us int 1 run scoreboard players get #us m.tmp",
         f"execute store result storage {NS}:fg sl int 1 run scoreboard players get #sl m.tmp",
         f'data modify storage {NS}:fg outil set value "Outil en main : {TOOL[j][1]} de {d["name"]}, emplacements utilisés "',
         f'data modify storage {NS}:fg g set value "{GLY["cristal_" + j]}"']
    for c, (pr, lv, sc, only) in CRIS.items():
        lab = {"sagesse": "Sagesse", "fortune": "Fortune", "echo": "Écho"}[c]
        kk = {"sagesse": "sag", "fortune": "for", "echo": "eco"}[c]
        if only is not None and j not in only:
            I += [f'data modify storage {NS}:fg l_{kk} set value "{lab} : pas pour cet outil"']
            continue
        I += [f'data modify storage {NS}:fg l_{kk} set value "{lab} · {pr}"', f'data modify storage {NS}:fg k_{kk} set value "red"',
              f'execute if score @s m.cr_{j} matches {pr}.. if score #us m.tmp < #sl m.tmp run data modify storage {NS}:fg k_{kk} set value "yellow"',
              f'execute unless score @s m.{j}_lvl matches {lv}.. run data modify storage {NS}:fg l_{kk} set value "✖ {lab} · niv. {lv}"',
              f'execute unless score @s m.{j}_lvl matches {lv}.. run data modify storage {NS}:fg k_{kk} set value "dark_gray"',
              f'execute if score @s m.{sc}_{j} matches 1 run data modify storage {NS}:fg l_{kk} set value "✔ {lab} serti"',
              f'execute if score @s m.{sc}_{j} matches 1 run data modify storage {NS}:fg k_{kk} set value "green"']
    if j in EFF_J:
        I += [f'data modify storage {NS}:fg l_eff set value "✔ Efficacité VII"', f'data modify storage {NS}:fg k_eff set value "green"']
        for n in range(7):
            rom = ["I", "II", "III", "IV", "V", "VI", "VII"][n]
            I += [f'execute if score @s m.ceff_{j} matches {n} run data modify storage {NS}:fg l_eff set value "Efficacité {rom} · {EFFC[n]}"',
                  f'execute if score @s m.ceff_{j} matches {n} run data modify storage {NS}:fg k_eff set value "red"',
                  f'execute if score @s m.ceff_{j} matches {n} if score @s m.cr_{j} matches {EFFC[n]}.. run data modify storage {NS}:fg k_eff set value "yellow"',
                  f'execute if score @s m.ceff_{j} matches {n} unless score @s m.{j}_lvl matches {EFFL[n]}.. run data modify storage {NS}:fg l_eff set value "✖ Efficacité {rom} · niv. {EFFL[n]}"',
                  f'execute if score @s m.ceff_{j} matches {n} unless score @s m.{j}_lvl matches {EFFL[n]}.. run data modify storage {NS}:fg k_eff set value "dark_gray"']
    else:
        I.append(f'data modify storage {NS}:fg l_eff set value "Efficacité : pas pour cet outil"')
    w(F + f"forge/infos_{j}.mcfunction", "\n".join(I))
ICON = {"marteau": "forge_marteau", "faux": "forge_faux", "arc3": "forge_arc3", "lasso": "forge_lasso", "parchemin": "forge_parchemin",
        "aimant": "forge_aimant", "cape": "forge_cape"}
NOMF = {"marteau": "Marteau du Mineur", "faux": "Faux du Fermier", "arc3": "Arc à triple tir", "lasso": "Lasso de l'Éleveur",
        "parchemin": "Parchemin de transfert", "aimant": "Aimant à objets", "cape": "Cape-planeur"}
fb = [f'{{label:[{{text:"★ ",color:"light_purple"}},{txt("Skins et cadres de titre", "light_purple", True)},{{text:" ★",color:"light_purple"}}],width:320,'
      f'tooltip:{{text:"Change l’apparence de tes outils et de ton armure, et le cadre de ton titre."}},action:{{type:"run_command",command:"trigger metiers set 420"}}}}']
for i, (key, (j, p, e, lv)) in enumerate(CRP.items(), 1):
    lab = f'[{gs(ICON[key])},{{text:" {NOMF[key]}  ",color:"$(c_{key})",italic:false}},{gs("cristal_" + j)},{{text:" {p}",color:"$(c_{key})"}}' + \
          (f',{{text:"  "}},{gs("eclat")},{{text:" {e}",color:"$(c_{key})"}}' if e else "") + "]"
    fb.append(f'{{label:{lab},width:320,tooltip:{{text:"{FORGE_IT[key][4]}\\nPrix : {p} cristaux de {jobs[j]["name"]}' + (f' + {e} éclats de boss' if e else '') +
              f' · {jobs[j]["name"]} niveau {lv}"}},action:{{type:"run_command",command:"trigger metiers set {400 + i}"}}}}')
for i, (key, e) in enumerate(COMMUN.items(), 6):
    lab = f'[{gs(ICON[key])},{{text:" {NOMF[key]}  ",color:"$(c_{key})",italic:false}},{gs("eclat")},{{text:" {e}",color:"$(c_{key})"}}]'
    fb.append(f'{{label:{lab},width:320,tooltip:{{text:"{FORGE_IT[key][4]}\\nPrix : {e} éclats de boss"}},action:{{type:"run_command",command:"trigger metiers set {400 + i}"}}}}')
for i, (kk, ic, tipc) in enumerate((("sag", "forge_cristal_sagesse", "+10 % d’XP de métier avec cet outil."),
                                    ("for", "forge_cristal_fortune", "+1 Fortune, Butin ou Chance de la mer."),
                                    ("eco", "forge_cristal_echo", "5 % de chance qu’un gain d’XP rapporte un cristal en plus."),
                                    ("eff", "forge_cristal_efficacite", "Efficacité de l’outil, jusqu’à VII (niveau 80).")), 11):
    fb.append(f'{{label:[{gs(ic)},{{text:" $(l_{kk}) ",color:"$(k_{kk})",italic:false}},{{text:"$(g)",font:"metiers:icones",color:"white"}}],width:320,'
              f'tooltip:{{text:"{tipc}\\nPayé en cristaux du métier de l’outil tenu. Emplacements : 1 au palier 3, 2 au palier 6, 3 au palier 9."}},'
              f'action:{{type:"run_command",command:"trigger metiers set {400 + i}"}}}}')
fb.append(btn(txt("Retirer le dernier cristal serti", "aqua"), 415, 320, "Libère un emplacement. Le cristal retiré est perdu."))
crline = ",".join(f'{gs("cristal_" + j)},{{text:" $(cr_{j})   ",color:"white"}}' for j in JL)
w(F + "forge/menu_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Forge",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  f'body:[{{type:"minecraft:plain_message",width:420,contents:[{crline},{{text:"\\n"}},{gs("eclat")},{{text:" $(ecl) éclats de boss",color:"light_purple"}}]}},'
  '{type:"minecraft:plain_message",width:380,contents:[{text:"$(outil)",color:"gray"},{text:"$(us) / $(sl)",color:"yellow"}]}],'
  f'actions:[{",".join(fb)}],columns:1,'
  'exit_action:{label:"Retour",width:150,action:{type:"run_command",command:"trigger metiers set 1"}}}')
# achats
for i, (key, (j, p, e, lv)) in enumerate(CRP.items(), 1):
    w(F + f"forge/acheter_{key}.mcfunction", "\n".join([
        f"execute unless score @s m.{j}_lvl matches {lv}.. run return run {tr(f'Il faut être niveau {lv} en {jobs[j][chr(110)+chr(97)+chr(109)+chr(101)]}.', 'red')}",
        f"execute unless score @s m.cr_{j} matches {p}.. run return run {tr('Pas assez de cristaux.', 'red')}",
        f"execute unless score @s m.ecl matches {e}.. run return run {tr('Pas assez d’éclats de boss.', 'red')}",
        f"scoreboard players remove @s m.cr_{j} {p}", f"scoreboard players remove @s m.ecl {e}",
        f"function {NS}:forge/donner_{key}", "playsound minecraft:block.anvil.use master @s ~ ~ ~ 1 1",
        tr(f"Tu as forgé : {NOMF[key]}.", "gold"), f"function {NS}:forge/menu"]))
for key, e in COMMUN.items():
    w(F + f"forge/acheter_{key}.mcfunction", "\n".join([
        f"execute unless score @s m.ecl matches {e}.. run return run {tr('Pas assez d’éclats de boss.', 'red')}",
        f"scoreboard players remove @s m.ecl {e}", f"function {NS}:forge/donner_{key}",
        "playsound minecraft:block.anvil.use master @s ~ ~ ~ 1 1", tr(f"Tu as forgé : {NOMF[key]}.", "gold"), f"function {NS}:forge/menu"]))
for c, (pr, lv, sc, only) in CRIS.items():
    D = [f"execute if items entity @s weapon.mainhand {SEL(j)} run return run function {NS}:forge/sertir_{c}_{j}" for j in JL]
    D.append(tr("Tiens ton outil de métier en main.", "red"))
    w(F + f"forge/sertir_{c}.mcfunction", "\n".join(D))
    for j in JL:
        if only is not None and j not in only:
            w(F + f"forge/sertir_{c}_{j}.mcfunction", tr("Ce cristal ne va pas sur cet outil.", "red"))
            continue
        w(F + f"forge/sertir_{c}_{j}.mcfunction", "\n".join([
            f"execute if score @s m.{sc}_{j} matches 1 run return run {tr('Ce cristal est déjà serti.', 'red')}",
            f"execute unless score @s m.{j}_lvl matches {lv}.. run return run {tr(f'Il faut être niveau {lv} dans ce métier.', 'red')}",
            "scoreboard players set #sl m.tmp 0",
            f"execute if score @s m.{j}_out matches 3.. run scoreboard players add #sl m.tmp 1",
            f"execute if score @s m.{j}_out matches 6.. run scoreboard players add #sl m.tmp 1",
            f"execute if score @s m.{j}_out matches 9.. run scoreboard players add #sl m.tmp 1",
            f"scoreboard players operation #us m.tmp = @s m.csag_{j}", f"scoreboard players operation #us m.tmp += @s m.cfor_{j}",
            f"scoreboard players operation #us m.tmp += @s m.ceco_{j}",
            f"execute if score #us m.tmp >= #sl m.tmp run return run {tr('Plus d’emplacement libre : il en faut un nouveau (paliers 3, 6 et 9).', 'red')}",
            f"execute unless score @s m.cr_{j} matches {pr}.. run return run {tr('Pas assez de cristaux.', 'red')}",
            f"scoreboard players remove @s m.cr_{j} {pr}", f"scoreboard players set @s m.{sc}_{j} 1",
            f"function {NS}:{j}/outil_donner", "playsound minecraft:block.amethyst_block.resonate master @s ~ ~ ~ 1 1.2",
            tr("Cristal serti dans ton outil.", "aqua"), f"function {NS}:forge/menu"]))
D = [f"execute if items entity @s weapon.mainhand {SEL(j)} run return run function {NS}:forge/eff_{j}" for j in JL]
D.append(tr("Tiens ton outil de métier en main.", "red"))
w(F + "forge/eff.mcfunction", "\n".join(D))
for j in JL:
    if j not in EFF_J:
        w(F + f"forge/eff_{j}.mcfunction", tr("L’Efficacité ne va pas sur cet outil.", "red")); continue
    E = [f"execute if score @s m.ceff_{j} matches 7.. run return run {tr('Efficacité déjà au maximum.', 'red')}"]
    for n in range(7):
        E += [f"execute if score @s m.ceff_{j} matches {n} unless score @s m.{j}_lvl matches {EFFL[n]}.. run return run {tr(f'Il faut être niveau {EFFL[n]} dans ce métier.', 'red')}",
              f"execute if score @s m.ceff_{j} matches {n} unless score @s m.cr_{j} matches {EFFC[n]}.. run return run {tr('Pas assez de cristaux.', 'red')}",
              f"execute if score @s m.ceff_{j} matches {n} run scoreboard players remove @s m.cr_{j} {EFFC[n]}"]
    E += [f"scoreboard players add @s m.ceff_{j} 1", f"function {NS}:{j}/outil_donner",
          "playsound minecraft:block.amethyst_block.resonate master @s ~ ~ ~ 1 1.4", tr("Efficacité améliorée.", "aqua"), f"function {NS}:forge/menu"]
    w(F + f"forge/eff_{j}.mcfunction", "\n".join(E))
D = [f"execute if items entity @s weapon.mainhand {SEL(j)} run return run function {NS}:forge/retirer_{j}" for j in JL]
D.append(tr("Tiens ton outil de métier en main.", "red"))
w(F + "forge/retirer.mcfunction", "\n".join(D))
for j in JL:
    w(F + f"forge/retirer_{j}.mcfunction", "\n".join([
        f"execute if score @s m.ceco_{j} matches 1 run return run function {NS}:forge/retirer_fin {{s:\"m.ceco_{j}\",j:\"{j}\"}}",
        f"execute if score @s m.cfor_{j} matches 1 run return run function {NS}:forge/retirer_fin {{s:\"m.cfor_{j}\",j:\"{j}\"}}",
        f"execute if score @s m.csag_{j} matches 1 run return run function {NS}:forge/retirer_fin {{s:\"m.csag_{j}\",j:\"{j}\"}}",
        tr("Aucun cristal serti sur cet outil.", "red")]))
w(F + "forge/retirer_fin.mcfunction", f"$scoreboard players set @s $(s) 0\n$function {NS}:$(j)/outil_donner\n" + tr("Cristal retiré.", "gray") + f"\nfunction {NS}:forge/menu")

# ================================================================ skins et cadres
TGT = [("a", "Armure des Guildes")] + [(j, f"{TOOL[j][1]} de {jobs[j]['name']}") for j in JL]
SK = ["scoreboard players add @s m.skt 0", "scoreboard players set @s m.prtot 0"]
SK += [f"scoreboard players operation @s m.prtot += @s m.{j}_pr" for j in JL]
SK += [f"execute store result storage {NS}:sk ecl int 1 run scoreboard players get @s m.ecl", "scoreboard players add @s m.cd_1 0"]
for ti, (t, nom) in enumerate(TGT):
    SK.append(f'execute if score @s m.skt matches {ti} run data modify storage {NS}:sk cible set value "{nom}"')
    SK.append(f"execute if score @s m.skt matches {ti} run function {NS}:skins/infos_{t}")
for ci, cn in enumerate(CADRE_NOM, 1):
    cid = CADRES[ci - 1]
    cost = {2: 3, 3: 6, 4: 10}.get(ci)
    SK += [f'data modify storage {NS}:sk f{ci} set value "dark_gray"']
    if ci == 1:
        SK.append(f'data modify storage {NS}:sk f{ci} set value "yellow"')
    elif cost:
        SK += [f'execute if score @s m.ecl matches {cost}.. run data modify storage {NS}:sk f{ci} set value "yellow"',
               f'execute unless score @s m.ecl matches {cost}.. run data modify storage {NS}:sk f{ci} set value "red"']
    elif ci == 5:
        SK.append(f'execute if score @s m.bk4 matches 5.. run data modify storage {NS}:sk f{ci} set value "yellow"')
    else:
        SK.append(f'execute if score @s m.prtot matches 3.. run data modify storage {NS}:sk f{ci} set value "yellow"')
    SK += [f'data modify storage {NS}:sk e{ci} set value ""',
           f'execute if score @s m.cd_{ci} matches 1 run data modify storage {NS}:sk f{ci} set value "green"',
           f'execute if score @s m.cadre matches {ci} run data modify storage {NS}:sk e{ci} set value " ★"']
SK.append(f"function {NS}:skins/menu_dialog with storage {NS}:sk")
w(F + "skins/menu.mcfunction", "\n".join(SK))
for ti, (t, nom) in enumerate(TGT):
    I = [f'data modify storage {NS}:sk skin set value ""', f'data modify storage {NS}:sk model set value "{t}_0"' if t != "a" else f'data modify storage {NS}:sk model set value "heaume_0"']
    if t == "a":
        I += [f'data modify storage {NS}:sk model set value "heaume_0"']
        I += [f'execute if score @s m.arm matches {p + 1} run data modify storage {NS}:sk model set value "heaume_{p}"' for p in range(11)]
    else:
        I += [f'execute if score @s m.{t}_out matches {k} run data modify storage {NS}:sk model set value "{t}_{k}"' for k in range(11)]
    I += [f'execute if score @s m.skin_{t} matches {i} run data modify storage {NS}:sk skin set value "{sid}"' for i, sid in enumerate(SKIN_IDS, 1)]
    for i, sn in enumerate(SKIN_NOM, 1):
        if t == "a":
            cost_txt = {1: "6 éclats", 2: "6 éclats", 3: "10 éclats", 4: "trophée", 5: "trophée", 6: "prestige"}[i]
        else:
            cost_txt = {1: "120 cristaux", 2: "120 cristaux", 3: "180 cristaux + 2 éclats", 4: "trophée", 5: "trophée", 6: "prestige"}[i]
        I += [f'data modify storage {NS}:sk s{i} set value "{sn} · {cost_txt}"', f'data modify storage {NS}:sk k{i} set value "red"']
        if i in (1, 2):
            cond = "if score @s m.ecl matches 6.." if t == "a" else f"if score @s m.cr_{t} matches 120.."
        elif i == 3:
            cond = "if score @s m.ecl matches 10.." if t == "a" else f"if score @s m.cr_{t} matches 180.. if score @s m.ecl matches 2.."
        elif i == 4:
            cond = "if score @s m.bk2 matches 3.."
        elif i == 5:
            cond = "if score @s m.bk4 matches 3.."
        else:
            cond = "if score @s m.prtot matches 1.." if t == "a" else f"if score @s m.{t}_pr matches 1.."
        I += [f'execute {cond} run data modify storage {NS}:sk k{i} set value "yellow"']
        if i >= 4:
            I += [f'execute unless {cond[3:] if False else cond.replace("if score", "score", 1)} run data modify storage {NS}:sk k{i} set value "dark_gray"']
        I += [f'execute if score @s m.so_{t}{i} matches 1 run data modify storage {NS}:sk s{i} set value "{sn} · équiper"',
              f'execute if score @s m.so_{t}{i} matches 1 run data modify storage {NS}:sk k{i} set value "green"',
              f'execute if score @s m.skin_{t} matches {i} run data modify storage {NS}:sk s{i} set value "★ {sn} · équipé"',
              f'execute if score @s m.skin_{t} matches {i} run data modify storage {NS}:sk k{i} set value "gold"']
    w(F + f"skins/infos_{t}.mcfunction", "\n".join(I))
SKD = ['{label:[{text:"Appliquer à : ",color:"gray"},{text:"$(cible)",color:"aqua"},{text:"  ↻",color:"gray"}],width:320,'
       'tooltip:{text:"Choisis l’objet : l’armure ou l’un de tes 9 outils de métier."},action:{type:"run_command",command:"trigger metiers set 421"}}']
SKD += [f'{{label:{{text:"$(s{i})",color:"$(k{i})"}},width:155,tooltip:{{text:"{tip}"}},action:{{type:"run_command",command:"trigger metiers set {430 + i}"}}}}'
        for i, tip in enumerate(["Givre : acier bleu glacé, éclats de glace.", "Corail : métal turquoise des grands fonds, gemmes corail.",
                                 "Or royal : or massif serti de rubis.", "Ossements : trophée, vaincre 3 fois la Reine arachnide.",
                                 "Magma : trophée, vaincre 3 fois le Brasier ancestral.", "Ombre : réservé aux joueurs passés par le prestige."], 1)]
SKD.append(btn(txt("Apparence de base", "white"), 430, 155))
SKD.append(btn(txt("Sans cadre", "white"), 440, 155))
SKD += [f'{{label:[{gs("cadre_" + CADRES[ci - 1] + "_g")},{{text:"{cn}",color:"$(f{ci})"}},{gs("cadre_" + CADRES[ci - 1] + "_d")},{{text:"$(e{ci})",color:"gold"}}],width:155,'
        f'tooltip:{{text:"{tip}"}},action:{{type:"run_command",command:"trigger metiers set {440 + ci}"}}}}'
        for ci, (cn, tip) in enumerate(zip(CADRE_NOM, ["Offert.", "3 éclats de boss.", "6 éclats de boss.", "10 éclats de boss.",
                                                       "Trophée : vaincre 5 fois le Brasier ancestral.", "3 prestiges au total."]), 1)]
w(F + "skins/menu_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Skins et cadres de titre",color:"light_purple",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:item",item:{id:"minecraft:paper",components:{"minecraft:item_model":"metiers:$(model)","minecraft:custom_model_data":{strings:["$(skin)"]}}},'
  'show_decorations:false,show_tooltip:false,description:{width:240,contents:[{text:"$(cible)\\n",color:"aqua",bold:true},'
  f'{{text:"Le skin change les matériaux, pas la forme du palier, et suit l’objet quand il évolue.\\n",color:"gray",bold:false}},{gs("eclat")},{{text:" $(ecl) éclats",color:"light_purple"}}]}}}}],'
  f'actions:[{",".join(SKD)}],columns:2,'
  'exit_action:{label:"Retour à la Forge",width:200,action:{type:"run_command",command:"trigger metiers set 400"}}}')
w(F + "skins/cycle.mcfunction", "scoreboard players add @s m.skt 1\nexecute if score @s m.skt matches 10.. run scoreboard players set @s m.skt 0\nfunction metiers:skins/menu")
for ti, (t, nom) in enumerate(TGT):
    REG = (f"execute if score @s m.arm matches 1.. if items entity @s armor.* {ASEL} run function {NS}:armure/donner" if t == "a" else
           f"execute if items entity @s container.* {SEL(t)} run function {NS}:{t}/outil_donner")
    REG2 = (f"execute if score @s m.arm matches 1.. if items entity @s container.* {ASEL} run function {NS}:armure/donner" if t == "a" else
            f"execute if items entity @s weapon.offhand {SEL(t)} run function {NS}:{t}/outil_donner")
    for i, sn in enumerate(SKIN_NOM, 1):
        if t == "a":
            pay = {1: ("score @s m.ecl matches 6..", ["scoreboard players remove @s m.ecl 6"]), 2: ("score @s m.ecl matches 6..", ["scoreboard players remove @s m.ecl 6"]),
                   3: ("score @s m.ecl matches 10..", ["scoreboard players remove @s m.ecl 10"]), 4: ("score @s m.bk2 matches 3..", []),
                   5: ("score @s m.bk4 matches 3..", []), 6: ("score @s m.prtot matches 1..", [])}[i]
        else:
            pay = {1: (f"score @s m.cr_{t} matches 120..", [f"scoreboard players remove @s m.cr_{t} 120"]),
                   2: (f"score @s m.cr_{t} matches 120..", [f"scoreboard players remove @s m.cr_{t} 120"]),
                   3: (f"score @s m.cr_{t} matches 180.. if score @s m.ecl matches 2..", [f"scoreboard players remove @s m.cr_{t} 180", "scoreboard players remove @s m.ecl 2"]),
                   4: ("score @s m.bk2 matches 3..", []), 5: ("score @s m.bk4 matches 3..", []), 6: (f"score @s m.{t}_pr matches 1..", [])}[i]
        A = [f"execute if score @s m.so_{t}{i} matches 1 if score @s m.skin_{t} matches {i} run return run function {NS}:skins/equiper {{t:\"{t}\",i:0}}",
             f"execute if score @s m.so_{t}{i} matches 1 run return run function {NS}:skins/equiper {{t:\"{t}\",i:{i}}}",
             f"execute unless {pay[0]} run return run {tr('Pas encore débloqué : regarde le prix ou la condition au survol.', 'red')}"]
        A += pay[1] + [f"scoreboard players set @s m.so_{t}{i} 1", tr(f"Skin {sn} débloqué.", "light_purple"),
                       f"function {NS}:skins/equiper {{t:\"{t}\",i:{i}}}"]
        w(F + f"skins/acheter_{t}_{i}.mcfunction", "\n".join(A))
    w(F + f"skins/regive_{t}.mcfunction", REG + "\n" + REG2)
for i in range(7):
    D = [f"execute if score @s m.skt matches {ti} run return run function {NS}:skins/{'acheter_' + t + '_' + str(i) if i else 'base_' + t}" for ti, (t, _) in enumerate(TGT)]
    w(F + f"skins/choix_{i}.mcfunction", "\n".join(D))
for t, _ in TGT:
    w(F + f"skins/base_{t}.mcfunction", f'function {NS}:skins/equiper {{t:"{t}",i:0}}')
w(F + "skins/equiper.mcfunction", f"$scoreboard players set @s m.skin_$(t) $(i)\n$function {NS}:skins/regive_$(t)\nplaysound minecraft:item.armor.equip_leather master @s ~ ~ ~ 1 1.2\nfunction {NS}:skins/menu")
for ci in range(1, 7):
    cost = {2: 3, 3: 6, 4: 10}.get(ci)
    A = [f"execute if score @s m.cd_{ci} matches 1 run return run function {NS}:skins/cadre {{i:{ci}}}"]
    if ci == 1:
        A.append("scoreboard players set @s m.cd_1 1")
    elif cost:
        A += [f"execute unless score @s m.ecl matches {cost}.. run return run {tr('Pas assez d’éclats de boss.', 'red')}",
              f"scoreboard players remove @s m.ecl {cost}", f"scoreboard players set @s m.cd_{ci} 1"]
    elif ci == 5:
        A += [f"execute unless score @s m.bk4 matches 5.. run return run {tr('Trophée : vaincre 5 fois le Brasier ancestral.', 'red')}", f"scoreboard players set @s m.cd_{ci} 1"]
    else:
        A += [f"execute unless score @s m.prtot matches 3.. run return run {tr('Il faut 3 prestiges au total.', 'red')}", f"scoreboard players set @s m.cd_{ci} 1"]
    A.append(f"function {NS}:skins/cadre {{i:{ci}}}")
    w(F + f"skins/cadre_{ci}.mcfunction", "\n".join(A))
w(F + "skins/cadre.mcfunction", f"$scoreboard players set @s m.cadre $(i)\ntag @s add metiers.maj\nfunction {NS}:prefixe/maj\nfunction {NS}:skins/menu")
w(F + "skins/cadre_0.mcfunction", f"function {NS}:skins/cadre {{i:0}}")

# ================================================================ déclencheurs
TRG = [f'execute if score @s m.trig matches 400 run function {NS}:appel {{f:"forge/menu"}}']
for i, key in enumerate(CRP, 1):
    TRG.append(f'execute if score @s m.trig matches {400 + i} run function {NS}:appel {{f:"forge/acheter_{key}"}}')
for i, key in enumerate(COMMUN, 6):
    TRG.append(f'execute if score @s m.trig matches {400 + i} run function {NS}:appel {{f:"forge/acheter_{key}"}}')
TRG += [f'execute if score @s m.trig matches 411 run function {NS}:appel {{f:"forge/sertir_sagesse"}}',
        f'execute if score @s m.trig matches 412 run function {NS}:appel {{f:"forge/sertir_fortune"}}',
        f'execute if score @s m.trig matches 413 run function {NS}:appel {{f:"forge/sertir_echo"}}',
        f'execute if score @s m.trig matches 414 run function {NS}:appel {{f:"forge/eff"}}',
        f'execute if score @s m.trig matches 415 run function {NS}:appel {{f:"forge/retirer"}}',
        f'execute if score @s m.trig matches 420 run function {NS}:appel {{f:"skins/menu"}}',
        f'execute if score @s m.trig matches 421 run function {NS}:appel {{f:"skins/cycle"}}']
TRG += [f'execute if score @s m.trig matches {430 + i} run function {NS}:appel {{f:"skins/choix_{i}"}}' for i in range(7)]
TRG += [f'execute if score @s m.trig matches {440 + i} run function {NS}:appel {{f:"skins/cadre_{i}"}}' for i in range(7)]
TRG += [f'execute if score @s m.trig matches {600 + d["idx"]} run function {NS}:appel {{f:"{j}/titre"}}' for j, d in jobs.items()]
TRG += [f'execute if score @s m.trig matches 610 run function {NS}:appel {{f:"f/saison"}}',
        f'execute if score @s m.trig matches 611 run function {NS}:appel {{f:"n/surpuissance"}}',
        f'execute if score @s m.trig matches 612 run function {NS}:appel {{f:"sac/donner"}}',
        f'execute if score @s m.trig matches 613 run function {NS}:appel {{f:"c/arc_recup"}}',
        f'execute if score @s m.trig matches 701 run function {NS}:appel {{f:"tp/enregistrer"}}',
        f'execute if score @s m.trig matches 702 run function {NS}:appel {{f:"tp/effacer"}}',
        f'execute if score @s m.trig matches 721..730 run function {NS}:appel {{f:"tp/aller"}}']
add_lines(F + "trigger.mcfunction", TRG)

# menu de la touche G / Échap : Minecraft impose un écran fixe ici (pas de niveaux ni de barres possibles),
# donc un seul gros bouton qui ouvre le vrai écran « Mes métiers », plus deux raccourcis.
RUN = lambda n: {"type": "run_command", "command": f"trigger metiers set {n}"}
hub = [{"label": [{"text": ""}, gj("forge_marteau"), {"text": "  Ouvrir mes métiers  ", "color": "gold", "bold": True}, gj("eclat")],
        "tooltip": {"text": "Niveaux, compétences, outils, défis, Forge."}, "width": 310, "action": RUN(1)},
       {"label": [{"text": ""}, gj("forge_marteau"), {"text": " Forge", "color": "gold"}], "width": 150, "action": RUN(400)},
       {"label": {"text": "Défis du jour", "color": "aqua"}, "width": 150, "action": RUN(4)}]
wj(f"data/{NS}/dialog/ouvrir.json", {"type": "minecraft:multi_action", "title": {"text": "Métiers", "color": "gold", "bold": True},
                                     "external_title": {"text": "Métiers"}, "can_close_with_escape": True, "pause": False,
                                     "actions": hub, "columns": 1})

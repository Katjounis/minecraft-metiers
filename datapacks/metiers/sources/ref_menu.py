# -*- coding: utf-8 -*-
# Refonte v24, partie 3 : menus (accueil, page métier), titres et cadres, Forge, skins.
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref_arbre.py"), encoding="utf-8").read())

def btn(label, action=None, width=150, tooltip=None):
    s = f"{{label:{label},width:{width}"
    if tooltip: s += f',tooltip:{{text:"{tooltip}"}}'
    if action is not None: s += f',action:{{type:"run_command",command:"trigger metiers set {action}"}}'
    return s + "}"

def txt(t, col="white", bold=False):
    return f'{{text:"{t}",color:"{col}",bold:{"true" if bold else "false"},italic:false}}'

# Icônes des boutons : textures du jeu par le composant de texte « object » (atlas items ou blocks), comme dans Commerce.
UI_SPRITES = set()
def IC(p):
    UI_SPRITES.add(p)
    return f'{{object:"atlas",atlas:"minecraft:{"blocks" if p.startswith("block/") else "items"}",sprite:"minecraft:{p}"}}'
def ib(icone, label, col, action, width=130, tip=None, bold=False):
    """Bouton avec une icône du jeu devant le libellé."""
    return btn(f'[{IC(icone)},{txt("  " + label, col, bold)}]', action, width, tip)
FOND_J = {"b": "block/oak_log", "f": "block/farmland_moist", "m": "block/deepslate", "c": "block/mossy_cobblestone",
          "p": "block/prismarine_bricks", "e": "block/hay_block_top", "n": "block/bookshelf", "x": "block/moss_block",
          "t": "block/emerald_block", "k": "block/bricks"}
OUTIL_IC = {"b": "item/iron_axe", "f": "item/iron_hoe", "m": "item/iron_pickaxe", "c": "item/iron_sword", "p": "item/fishing_rod",
            "e": "item/carrot_on_a_stick", "n": "item/enchanted_book", "x": "item/iron_shovel", "t": "item/bundle", "k": "item/brush"}

CRP = {"marteau": ("m", 260, 4, 50), "faux": ("f", 220, 3, 50), "arc3": ("c", 300, 5, 60), "lasso": ("e", 140, 1, 40), "parchemin": ("n", 60, 0, 40)}
COMMUN = {"aimant": 6, "cape": 12}
# déclencheurs du choix d'une compétence désactivée (26/11/2026) : 4000 + 20 x idx + k (oublier), 4300 + ... (réactiver)
TOUB = lambda d, k: 4000 + 20 * d["idx"] + k
TREAC = lambda d, k: 4300 + 20 * d["idx"] + k
TDES = lambda d, k: 4600 + 20 * d["idx"] + k   # désactiver
EFFC = [40, 70, 110, 150, 200, 260, 330]
EFFL = [10, 20, 30, 40, 50, 60, 80]
CRIS = {"sagesse": (90, 20, "csag", None), "fortune": (160, 40, "cfor", tuple(FORT_KEY)), "echo": (240, 60, "ceco", None)}


# ---------------------------------------------------------------- bandeau de séparation (fond dessiné par la police d'icônes)
LARG = {**{c: 2 for c in "i!,.:;|"}, **{c: 3 for c in "l'`"}, **{c: 4 for c in "It[] "}, **{c: 5 for c in "fk<>(){}*\""}, **{c: 7 for c in "@~"}}
def largeur(t, gras=True):
    return sum(LARG.get(c, 6) + (1 if gras else 0) for c in t)
def esp(n):
    return chr(0xE300 + n + 256)
def bandeau(texte, align="centre", col="gold"):
    """Libellé de bouton : fond « bandeau » (195 px) puis texte placé dessus. Largeur totale 195 px, pour un bouton de 200."""
    tw = largeur(texte); T = 195
    x0 = {"centre": (T - tw) // 2, "droite": T - tw - 8, "gauche": 8}[align]
    return (f'[{{text:""}},{{text:"{GLY["bandeau"]}",font:"metiers:icones",color:"white",shadow_color:0}},'
            f'{{text:"{esp(x0 - T)}",font:"metiers:icones"}},{{text:"{texte}",color:"{col}",bold:true}},'
            f'{{text:"{esp(T - x0 - tw)}",font:"metiers:icones"}}]')

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
           f'execute if score @s m.tmp matches 6.. unless entity @s[tag=metiers.sk.{j}1,tag=metiers.sk.{j}2,tag=metiers.sk.{j}3,tag=metiers.sk.{j}4,tag=metiers.sk.{j}5,tag=metiers.sk.{j}6] if score @s m.{j}_lvl matches 5.. run data modify storage {NS}:mn {j}_d set value "●"',
           f"scoreboard players operation @s m.tmp = @s m.{j}_lvl", "scoreboard players operation @s m.tmp /= #10 m.const",
           f'execute if score @s m.{j}_pal < @s m.tmp run data modify storage {NS}:mn {j}_d set value "●"']
# 26/11/2026 : Mes métiers en panneau « succès » (ref_panneaux.py) : une icône par métier avec son niveau, puis les activités
_PADN = {n: [pad((larg_txt("niv 55") - larg_txt("niv " + "5" * n)) // 2), pad(larg_txt("niv 55") - larg_txt("niv " + "5" * n) - (larg_txt("niv 55") - larg_txt("niv " + "5" * n)) // 2)] for n in (1, 2, 3)}
for k, (j, d) in enumerate(jobs.items(), 1):
    MN += [f'data modify storage {NS}:mn a{k} set value "{PANNEAUX["metiers"]["noeuds"][k - 1]["etats"]["on"]}"',
           f'execute if data storage {NS}:mn {{{j}_d:"●"}} run data modify storage {NS}:mn a{k} set value "{PANNEAUX["metiers"]["noeuds"][k - 1]["etats"]["notif"]}"']
    for n, rng in ((1, "..9"), (2, "10..99"), (3, "100..")):
        MN += [f'execute if score @s m.{j}_lvl matches {rng} run data modify storage {NS}:mn p{k} set value "{_PADN[n][0]}"',
               f'execute if score @s m.{j}_lvl matches {rng} run data modify storage {NS}:mn r{k} set value "{_PADN[n][1]}"']
MN.append(f"function {NS}:menu_dialog with storage {NS}:mn")
w(F + "menu.mcfunction", "\n".join(MN))
_EXTRA = [(400, "Forge", "Sertissage des cristaux dans ton outil, skins et cadres de titre."), (4, "Défis du jour", "Un défi par métier, chaque jour."),
          (495, "Quêtes", "Une quête de 10 étapes par métier."), (6, "Armure des Guildes", "Elle monte avec ton score total."),
          (540, "Sommaire A à Z", "Tout Métiers rangé par ordre alphabétique."), (497, "Plus", "Guilde, classement, synergies, cadres de titre, aura, aide.")]
_clics, _surv = {}, {}
for k, (j, d) in enumerate(jobs.items(), 1):
    _clics[k] = f"trigger metiers set {20 + d['idx']}"
    _surv[k] = [{"text": d["name"] + "\n", "color": d["color"], "bold": True},
                {"text": "Arbre de compétences, outil, progression.\nPastille jaune : des points ou une récompense t’attendent.", "color": "gray", "bold": False}]
for i, (trg, nm, tip) in enumerate(_EXTRA, 11):
    _clics[i] = f"trigger metiers set {trg}"
    _surv[i] = [{"text": nm + "\n", "color": "gold", "bold": True}, {"text": tip, "color": "gray", "bold": False}]
_corps = panneau_corps("metiers", _clics, _surv, {i: "on" for i in range(11, 17)})
for k, (j, d) in enumerate(jobs.items(), 1):
    _corps = _corps.replace(f'"$(i{k})"', f'"niv $({j}_l)"')
w(F + "menu_dialog.mcfunction",
  'playsound minecraft:item.book.page_turn player @s ~ ~ ~ 0.7 1\n$dialog show @s {type:"minecraft:notice",title:{text:"Mes métiers",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:plain_message",width:400,contents:[{text:"Score total ",color:"gray"},{text:"$(score)",color:"yellow"},'
  '{text:"   ·   Armure : ",color:"gray"},{text:"$(arm)",color:"gold"},{text:"   ·   ",color:"gray"},' + gs("eclat") + ',{text:" $(ecl) éclats",color:"gray"}]},'
  + _corps + '],action:{label:"Fermer",width:200}}')
# hub « Activités » (497) : tout ce qui n'est pas un métier, en icônes sur 3 colonnes
hub = [ib("item/name_tag", "Guilde", "gold", 770, 150, "Fonder ou rejoindre une guilde, défi de la semaine, classement."),
       ib("item/gold_ingot", "Classement", "gold", 5, 150, "Podium du serveur et meilleur de chaque métier."),
       ib("item/emerald", "Synergies", "gold", 496, 150, "Bonus quand deux métiers atteignent le niveau 50."),
       ib("item/item_frame", "Cadres de titre", "gold", 472, 150, "Le cadre autour de ton titre."),
       ib("item/glowstone_dust", "Aura", "gold", 499, 150, "Active ou coupe les particules de prestige autour de toi."),
       ib("item/paper", "Aide", "white", 460, 150, "Cristaux, éclats, Forge, défis, boss : comment ça marche.")]
w(F + "activites.mcfunction",
  'dialog show @s {type:"minecraft:multi_action",title:{text:"Plus",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:plain_message",width:310,contents:{text:"Guilde, classement, synergies, cadres, aura et aide.",color:"gray"}}],'
  f'actions:[{",".join(hub)}],columns:3,'
  'exit_action:{label:"Retour",width:200,action:{type:"run_command",command:"trigger metiers set 1"}}}')

# ================================================================ page métier (remplace l'ancien écran de l'arbre)
NEXTTXT = {}
for j, d in jobs.items():
    for k in range(10):
        nt = R[j][k + 1][0]["name"]
        NEXTTXT[(j, k)] = f"Niveau {10 * (k + 1)} : {nt}, titre {TIERS[k + 1][0]}, {CRIST[k + 1]} cristaux"
NOMF_J = {"m": "Marteau 3x3 : 260 cristaux + 4 éclats, niveau 50", "f": "Faux 5x5 : 220 cristaux + 3 éclats, niveau 50",
          "c": "Arc à triple tir : 300 cristaux + 5 éclats, niveau 60", "e": "Lasso : 140 cristaux + 1 éclat, niveau 40",
          "n": "Parchemin de transfert : 60 cristaux, niveau 40"}
TDESC = {
    "b": "Hache : Efficacité et Solidité montent à chaque palier. Les compétences ajoutent l’abattage d’arbre entier et la replantation.",
    "f": "Houe : Fortune et Efficacité montent à chaque palier. Récolter des cultures mûres rapporte l’XP.",
    "m": "Pioche : Efficacité et Fortune montent à chaque palier. Minerais et pierre rapportent l’XP.",
    "c": "Épée du Chasseur, avec un arc qui évolue en même temps (bouton Récupérer mon arc).",
    "p": "Canne : Chance de la mer et Appât montent à chaque palier. Chaque prise rapporte l’XP.",
    "e": "Houlette : clic droit, les animaux à 10 blocs te suivent (2 au palier 0, 8 au palier 10). Clic droit à nouveau pour les libérer.",
    "n": "Grimoire de téléportation : clic droit pour enregistrer un point ou t’y rendre (3 s sans bouger). 1 point au palier 0, 10 au palier 10, recharge de 10 min à 1 min.",
    "x": "Pelle : Efficacité monte à chaque palier. Marcher, courir et découvrir biomes et structures rapporte l’XP.",
    "t": "Dank Null : mets-y un bloc (terre, cobble, granite…), tous ceux que tu ramasses ensuite sont vendus au marché (détruits s’ils ne se vendent pas). 3 sortes au palier 0, 13 au palier 10. Les échanges avec les villageois rapportent l’XP.",
    "k": "Truelle : tenue dans une main, elle allonge ta portée (+1, +2 au palier 5, +3 au palier 10). Chaque bloc posé rapporte l’XP, surtout les blocs de construction, et +2 XP par bloc acheté au Commerce.",
}
FITEM = {"m": "marteau", "f": "faux", "c": "arc3", "e": "lasso", "n": "parchemin"}
SPECIAL_COURT = {"f": "Saison", "n": "Surpuissance", "x": "Sac à dos", "c": "Mon arc", "p": "Carnet", "b": "Forger l’outil",
                 "m": "Marteau 3x3", "e": "Lasso", "t": "Forger l’outil", "k": "Kit de chantier"}
SPECIAL = {"f": (610, "Saison des moissons", "green", "Une fois par jour de jeu : toutes les cultures à 12 blocs mûrissent (compétence ultime)."),
           "n": (611, "Surpuissance", "light_purple", "Objet enchanté en main : +1 niveau à tous ses enchantements, 30 niveaux d’XP (compétence ultime)."),
           "x": (612, "Récupérer mon sac à dos", "blue", "Sac à dos : 18 cases au niveau 20, 27 au niveau 50, 2 pages au niveau 80."),
           "c": (613, "Récupérer mon arc", "red", "L’arc du Chasseur évolue en même temps que ton épée."),
           "p": (70, "Carnet du pêcheur", "aqua", "Tes poissons légendaires."),
           "b": (470, "Forger l’outil en main", "gold", "Sertis des cristaux dans ta hache tenue en main."),
           "m": (401, "Forger : Marteau 3x3", "gold", "Creuse en 3x3. 260 cristaux de Mineur + 4 éclats, Mineur niveau 50."),
           "e": (404, "Forger : Lasso", "gold", "Capture un animal dans un œuf. 140 cristaux d’Éleveur + 1 éclat, Éleveur niveau 40."),
           "t": (470, "Forger l’outil en main", "gold", "Sertis des cristaux dans ton Dank Null tenu en main."),
           "k": (614, "Kit de chantier", "#C08850", "Une fois par jour de jeu (20 min) : 32 échafaudages, 16 échelles et 8 lanternes. Bâtisseur niveau 20.")}
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
    # niveau pris en compte pour débloquer une compétence : 100 dès qu'on est passé par le prestige
    P += [f"scoreboard players operation #lve m.tmp = @s m.{j}_lvl", f"execute if score @s m.{j}_pr matches 1.. run scoreboard players set #lve m.tmp 100"]
    for k, (name, cost, req, desc) in enumerate(sk, 1):
        lv = slvl(j, k)
        cond = f"execute if entity @s[{reqsel2(req)}]" if req else "execute if entity @s"
        P += [f'data modify storage {NS}:pg l{k} set value "✖ {name}"', f'data modify storage {NS}:pg c{k} set value "dark_gray"',
              f'execute unless score #lve m.tmp matches {lv}.. run data modify storage {NS}:pg l{k} set value "✖ {name}"',
              f'execute if score #lve m.tmp matches {lv}.. {cond[8:]} run data modify storage {NS}:pg l{k} set value "{name}"'
              if req else f'execute if score #lve m.tmp matches {lv}.. run data modify storage {NS}:pg l{k} set value "{name}"',
              (f'execute if score #lve m.tmp matches {lv}.. {cond[8:]} run data modify storage {NS}:pg c{k} set value "yellow"' if req else
               f'execute if score #lve m.tmp matches {lv}.. run data modify storage {NS}:pg c{k} set value "yellow"'),
              (f'execute if score #lve m.tmp matches {lv}.. {cond[8:]} if score #pts m.tmp matches ..{cost - 1} run data modify storage {NS}:pg c{k} set value "red"' if req else
               f'execute if score #lve m.tmp matches {lv}.. if score #pts m.tmp matches ..{cost - 1} run data modify storage {NS}:pg c{k} set value "red"'),
              f'execute if entity @s[tag=metiers.sk.{j}{k}] run data modify storage {NS}:pg l{k} set value "✔ {name}"',
              f'execute if entity @s[tag=metiers.sk.{j}{k}] run data modify storage {NS}:pg c{k} set value "green"',
              f'execute if entity @s[tag=metiers.sk.{j}{k},tag=metiers.skoff.{j}{k}] run data modify storage {NS}:pg l{k} set value "○ {name}"',
              f'execute if entity @s[tag=metiers.sk.{j}{k},tag=metiers.skoff.{j}{k}] run data modify storage {NS}:pg c{k} set value "gold"']
    P += ["scoreboard players operation @s m.tmp = @s m.{0}_lvl".format(j), "scoreboard players operation @s m.tmp /= #10 m.const",
          f'data modify storage {NS}:pg rl set value "Pas de récompense"', f'data modify storage {NS}:pg rc set value "dark_gray"',
          f'execute if score @s m.{j}_pal < @s m.tmp run data modify storage {NS}:pg rl set value "Récompense ●"',
          f'execute if score @s m.{j}_pal < @s m.tmp run data modify storage {NS}:pg rc set value "light_purple"',
          f'data modify storage {NS}:pg tl set value "Afficher le titre"', f'data modify storage {NS}:pg tc set value "yellow"',
          f'execute if score @s m.pref matches {d["idx"]} run data modify storage {NS}:pg tl set value "Titre affiché ✔"',
          f'execute if score @s m.pref matches {d["idx"]} run data modify storage {NS}:pg tc set value "green"',
          f'data modify storage {NS}:pg pl set value "Prestige (niv. 100)"', f'data modify storage {NS}:pg pc set value "dark_gray"',
          f'execute if score @s m.{j}_lvl matches {MAXLVL}.. run data modify storage {NS}:pg pl set value "★ Prestige prêt"',
          f'execute if score @s m.{j}_lvl matches {MAXLVL}.. run data modify storage {NS}:pg pc set value "gold"',
          f'data modify storage {NS}:pg sk_mode set value "Fortune ⇄ Soie"',
          f'execute if score @s m.silk matches 1 run data modify storage {NS}:pg sk_mode set value "Soie ⇄ Fortune"',
          f'data modify storage {NS}:pg mc set value "aqua"']
    P += arbre_etats(j, f"metiers.sk.{j}")
    # 25/11/2026 : page = l'arbre ; les onglets Outil (#vue 1) et Progression (#vue 2) relisent les mêmes valeurs
    P += [f"execute if score #vue m.tmp matches 1 run function {NS}:{j}/outil_dialog with storage {NS}:pg",
          f"execute if score #vue m.tmp matches 2 run function {NS}:{j}/prog_dialog with storage {NS}:pg",
          f"execute unless score #vue m.tmp matches 1..2 run function {NS}:{j}/page_dialog with storage {NS}:pg",
          "scoreboard players set #vue m.tmp 0"]
    w(F + f"{j}/arbre.mcfunction", "\n".join(P))
    sbtn = []
    for k, (name, cost, req, desc) in enumerate(sk, 1):
        rq = " + ".join(sk[r - 1][0] for r in req) if req else "rien"
        tip = (f"{desc}\\nCoût : {cost} points · niveau {slvl(j, k)} · requiert : {rq}\\nUne fois acquise : clic pour la désactiver, la réactiver ou l’oublier (points rendus)."
               "\\n\\nVert ✔ acquise · jaune disponible · rouge points manquants · gris ✖ niveau trop bas · ○ désactivée")
        sbtn.append(f'{{label:{{text:"$(l{k})",color:"$(c{k})"}},width:130,tooltip:{{text:"{tip}"}},action:{{type:"run_command",command:"trigger metiers set {TSK(d, k)}"}}}}')
    # 25/11/2026 : les compétences posées en arbre cliquable (grille de 3 colonnes, cases vides d'un pixel) :
    #        1            racine
    #     2     3         deux branches
    #     4     5
    #        6            sommet, qui demande 4 et 5
    VIDE = '{label:"",width:1}'
    # 25/11/2026 : l'arbre dessiné est cliquable (nœuds) ; les 6 boutons restent en dessous, compacts (2 rangées)
    sp = SPECIAL[j]
    ICL = lambda ic, lab, col: f'[{IC(ic)},{{text:"  {lab}",color:"{col}",italic:false}}]'
    ICV = lambda ic, var, col: f'[{IC(ic)},{{text:"  $({var})",color:"$({col})",italic:false}}]'
    def cb(label, val, tip=None):
        return f'{{label:{label},width:130' + (f',tooltip:{{text:"{tip}"}}' if tip else "") + f',action:{{type:"run_command",command:"trigger metiers set {val}"}}}}'
    abtn = [cb(ICL(OUTIL_IC[j], "Mon outil", "aqua"), 300 + d["idx"], "Redonne ton outil à son palier (dès le niveau 10, une fois toutes les 10 minutes)."),
            cb(ICL("item/experience_bottle", "Réparer", "green"), 330 + d["idx"], "Seule façon de réparer ton outil de métier : 5 niveaux d’XP. Incassable dès le palier 5."),
            cb(ICV("item/gold_ingot", "rl", "rc"), 200 + d["idx"], "Ce que tu gagnes à chaque palier de 10 niveaux."),
            cb(ICV("item/name_tag", "tl", "tc"), TTI(d), f"Affiche ton titre de {d['name']} devant ton pseudo. Le cadre se choisit dans Activités."),
            cb(ICL("item/amethyst_shard", SPECIAL_COURT[j], sp[2]), sp[0], sp[3]),
            cb(ICV("item/totem_of_undying", "pl", "pc"), 310 + d["idx"], "Au niveau 100 : repars au niveau 1 avec une étoile, tu gardes tes compétences (5 étoiles max)."),
            cb(ICL("item/book", "Barème d’XP", "gold"), 480 + d["idx"], f"Ce que rapporte chaque action en {d['name']}, avec les images du jeu."),
            cb(ICL("item/goat_horn", "Classement", "yellow"), 520 + d["idx"], f"Les 10 meilleurs joueurs en {d['name']} (niveau et étoiles de prestige).")] + \
           ([cb(ICV("item/enchanted_book", "sk_mode", "mc"), 761, "Change l’enchantement de ta pioche : Fortune (plus de minerais) ou Toucher de soie (le bloc tel quel). Ta pioche est remplacée tout de suite.")] if j == "m" else [])
    body = ('[{type:"minecraft:item",item:{id:"minecraft:paper",components:{"minecraft:item_model":"metiers:$(model)","minecraft:custom_model_data":{strings:["$(skin)"]}}},'
            'show_decorations:false,show_tooltip:false,description:{width:260,contents:['
            f'{{text:"$(titre) {d["name"]}\\n",color:"{d["color"]}",bold:true}},{{text:"Niveau $(lvl)   ",color:"yellow",bold:false}},'
            '{text:"$(bar)",font:"metiers:icones",color:"white"},{text:"  $(xp) / $(need) XP\\n",color:"gray"},'
            f'{{text:"Outil au palier $(out) sur 10",color:"gray"}}]}}}},'
            '{type:"minecraft:plain_message",width:380,contents:[{text:"$(next)\\n",color:"gold"},'
            f'{{text:"Points de compétence : ",color:"gray"}},{{text:"$(pts)",color:"yellow"}},{{text:"   ·   ",color:"gray"}},{gs("cristal_" + j)},{{text:" $(cr) cristaux\\n",color:"aqua"}},'
            '{text:"Survole un bouton pour voir son effet et son coût.",color:"dark_gray"}]},'
            f'{{type:"minecraft:plain_message",width:380,contents:[{{text:"Ton outil  ",color:"{d["color"]}",bold:true}},{{text:"{TDESC[j]}\\n",color:"white",bold:false}}' +
            (f',{{text:"Objet de Forge  ",color:"gold",bold:true}},{{text:"{NOMF_J[j]}\\n",color:"white",bold:false}}' if j in FITEM else "") +
            ']}]')
    ent = ('{type:"minecraft:plain_message",width:380,contents:['
           f'{{text:"$(titre) {d["name"]}   ",color:"{d["color"]}",bold:true}},{{text:"Niveau $(lvl)   ",color:"yellow",bold:false}},'
           '{text:"$(bar)",font:"metiers:icones",color:"white"},{text:"  $(xp) / $(need) XP\\n",color:"gray"},'
           '{text:"$(pts) points de compétence",color:"yellow"},{text:"   ·   ",color:"gray"},'
           f'{gs("cristal_" + j)},{{text:" $(cr) cristaux",color:"aqua"}}]}}')
    leg = ('{type:"minecraft:plain_message",width:380,contents:{text:"Cadre doré acquise · cadre rouge désactivée · pastille jaune disponible · pastille rouge points manquants · '
           'gris niveau trop bas. Survole un nœud pour son effet et son coût.",color:"dark_gray"}}')
    RET = f'{{label:"Retour",width:130,action:{{type:"run_command",command:"trigger metiers set 1"}}}}'
    ARBRE = f'{{label:"Retour à l’arbre",width:200,action:{{type:"run_command",command:"trigger metiers set {20 + d["idx"]}"}}}}'
    onglets = [cb(ICL(OUTIL_IC[j], "Outil", "aqua"), 550 + d["idx"], "Ton outil : le récupérer, le réparer, le forger, son skin."),
               cb(ICL("item/gold_ingot", "Progression", "gold"), 560 + d["idx"], "Récompenses de palier, titre, prestige, barème, classement."), RET]
    titre_j = f'[{gs("metier_" + j)},{{text:" {d["name"]}",color:"{d["color"]}",bold:true}}]'
    w(F + f"{j}/page_dialog.mcfunction",
      f'$dialog show @s {{type:"minecraft:multi_action",title:{titre_j},'
      f'can_close_with_escape:true,pause:false,body:[{ent},{arbre_corps(j)}],actions:[{",".join(onglets)}],columns:3}}')
    # onglet Outil : l'outil en image, sa description, et tout ce qui le concerne
    outil_btn = [abtn[0], abtn[1], cb(ICL("item/netherite_upgrade_smithing_template", "Forger l’outil", "gold"), 470, "Sertis des cristaux dans l’outil de métier que tu tiens."),
                 cb(ICL("item/painting", "Skin de l’outil", "light_purple"), 420, "Apparence de tes outils et de ton armure.")] + abtn[8:]
    # 26.0 : objets achetables du métier, Forge arcanique (Enchanteur), arc et élytres de palier à récupérer
    if j in OBJ_BTN:
        outil_btn.append(cb(ICL("item/bundle", "Objets du métier", "gold"), OBJ_BTN[j][0], "Les objets débloqués par tes compétences, achetés en Écus."))
    if j == "n":
        outil_btn.append(cb(ICL("item/enchanted_book", "Forge arcanique", "light_purple"), 3490, "Compétence Forge arcanique : 15 niveaux d’XP et 10 lapis, tous les enchantements de l’objet en main montent d’un niveau, jusqu’à 1, 2 ou 3 au-dessus du maximum du jeu."))
    if j == "x":
        outil_btn.append(cb(ICL("item/elytra", "Élytres", "blue"), 3492, "Compétence Ailes : les récupérer si elles sont perdues."))
    corps_outil = ('[{type:"minecraft:item",item:{id:"minecraft:paper",components:{"minecraft:item_model":"metiers:$(model)","minecraft:custom_model_data":{strings:["$(skin)"]}}},'
                   'show_decorations:false,show_tooltip:false,description:{width:260,contents:['
                   f'{{text:"Outil au palier $(out) sur 10\\n",color:"gray"}},{{text:"$(next)",color:"gold"}}]}}}},'
                   f'{{type:"minecraft:plain_message",width:380,contents:[{{text:"Ton outil  ",color:"{d["color"]}",bold:true}},{{text:"{TDESC[j]}",color:"white",bold:false}}' +
                   (f',{{text:"\\nObjet de Forge  ",color:"gold",bold:true}},{{text:"{NOMF_J[j]}",color:"white",bold:false}}' if j in FITEM else "") + ']}]')
    w(F + f"{j}/outil_dialog.mcfunction",
      f'$dialog show @s {{type:"minecraft:multi_action",title:[{gs("metier_" + j)},{{text:" {d["name"]}  ·  Outil",color:"{d["color"]}",bold:true}}],'
      f'can_close_with_escape:true,pause:false,body:{corps_outil},actions:[{",".join(outil_btn)}],columns:3,exit_action:{ARBRE}}}')
    prog_btn = [abtn[2], abtn[5], abtn[3], abtn[6],
                cb(ICL("item/goat_horn", "Classement", "yellow"), 520 + d["idx"], f"Les 10 meilleurs joueurs en {d['name']}."), abtn[4]]
    w(F + f"{j}/prog_dialog.mcfunction",
      f'$dialog show @s {{type:"minecraft:multi_action",title:[{gs("metier_" + j)},{{text:" {d["name"]}  ·  Progression",color:"{d["color"]}",bold:true}}],'
      f'can_close_with_escape:true,pause:false,body:[{ent}],actions:[{",".join(prog_btn)}],columns:3,exit_action:{ARBRE}}}')
    # 26/11/2026 : clic sur une compétence acquise = petit menu : Désactiver (ou Réactiver) et Oublier.
    # Oublier rend ses points tout de suite (recalculés par {j}/points d'après les compétences acquises).
    # Un dialogue ne distingue pas clic gauche et clic droit, d'où le menu.
    for k, (name, cost, req, desc) in enumerate(sk, 1):
        dep = [(kk, s_[0]) for kk, s_ in enumerate(sk, 1) if k in s_[2]]
        ely = (j, k) == ("x", 9)
        w(F + f"{j}/basculer_{k}.mcfunction", "\n".join([
            f"execute if entity @s[tag=metiers.skoff.{j}{k}] run return run function {NS}:{j}/choix_off_{k}",
            f"function {NS}:{j}/choix_on_{k}"]))
        w(F + f"{j}/desactiver_{k}.mcfunction", "\n".join(
            [f"execute unless entity @s[tag=metiers.sk.{j}{k}] run return run function {NS}:{j}/arbre",
             f"tag @s add metiers.skoff.{j}{k}", tr(f"{name} est désactivée.", "gold")]
            + ([f"function {NS}:objets/retirer_elytres"] if ely else [])
            + ["playsound minecraft:block.lever.click master @s ~ ~ ~ 1 0.7", f"function {NS}:{j}/arbre"]))
        w(F + f"{j}/activer_{k}.mcfunction", "\n".join(
            [f"execute unless entity @s[tag=metiers.sk.{j}{k}] run return run function {NS}:{j}/arbre",
             f"tag @s remove metiers.skoff.{j}{k}", tr(f"{name} est réactivée.", "green")]
            + ([f"function {NS}:objets/retirer_elytres", f"function {NS}:objets/donner_elytres"] if ely else [])
            + ["playsound minecraft:block.lever.click master @s ~ ~ ~ 1 1.2", f"function {NS}:{j}/arbre"]))
        bouton_oub = (f'{{label:{{text:"Oublier (+{cost} points)",color:"red"}},width:150,'
                      f'tooltip:{{text:"Tu perds la compétence et tu récupères ses {cost} points. Tu pourras la racheter plus tard."}},'
                      f'action:{{type:"run_command",command:"trigger metiers set {TOUB(d, k)}"}}}}')
        for etat, (lab, col, trg, etat_txt) in {
                "on": ("Désactiver", "gold", TDES(d, k), "active"),
                "off": ("Réactiver", "green", TREAC(d, k), "désactivée")}.items():
            w(F + f"{j}/choix_{etat}_{k}.mcfunction",
              f'dialog show @s {{type:"minecraft:multi_action",title:{{text:"{name}",color:"{d["color"]}",bold:true}},'
              f'can_close_with_escape:true,pause:false,'
              f'body:[{{type:"minecraft:plain_message",width:300,contents:{{text:"{desc}\\n\\nCompétence {etat_txt}.",color:"gray"}}}}],'
              f'actions:[{{label:{{text:"{lab}",color:"{col}"}},width:150,action:{{type:"run_command",command:"trigger metiers set {trg}"}}}},'
              f'{bouton_oub}],columns:2,'
              f'exit_action:{{label:"Retour",width:150,action:{{type:"run_command",command:"trigger metiers set {20 + d["idx"]}"}}}}}}')
        O = [f"execute unless entity @s[tag=metiers.sk.{j}{k}] run return run function {NS}:{j}/arbre"]
        for kk, nn in dep:
            O.append(f"execute if entity @s[tag=metiers.sk.{j}{kk}] run return run {tr(f'Oublie d’abord {nn}, qui a besoin de {name}.', 'red')}")
        O += [f"tag @s remove metiers.sk.{j}{k}", f"tag @s remove metiers.skoff.{j}{k}",
              f"advancement revoke @s only {NS}:{j}/competence_{k}"]
        if ely:
            O.append(f"function {NS}:objets/retirer_elytres")
        O += [tr(f"{name} est oubliée : {cost} points te sont rendus.", "gold"),
              "playsound minecraft:entity.item.break master @s ~ ~ ~ 0.8 1.2", f"function {NS}:{j}/arbre"]
        w(F + f"{j}/oublier_{k}.mcfunction", "\n".join(O))
        add_lines(F + "trigger.mcfunction", [
            f"execute if score @s m.trig matches {TDES(d, k)} run function {NS}:{j}/desactiver_{k}",
            f"execute if score @s m.trig matches {TREAC(d, k)} run function {NS}:{j}/activer_{k}",
            f"execute if score @s m.trig matches {TOUB(d, k)} run function {NS}:{j}/oublier_{k}"])
    # bascule du titre de ce métier
    w(F + f"{j}/titre.mcfunction", "\n".join([
        f"execute if score @s m.pref matches {d['idx']} run scoreboard players set @s m.trig 10",
        f"execute unless score @s m.pref matches {d['idx']} run scoreboard players set @s m.trig {10 + d['idx']}",
        f"function {NS}:prefixe/choisir", "scoreboard players set #vue m.tmp 2", f"function {NS}:{j}/arbre"]))

# ================================================================ titres + cadres (équipes)
CADRES = ["bois", "fer", "dore", "runique", "flammes", "celeste"]
CADRE_NOM = ["Bois", "Fer forgé", "Doré", "Runique", "Flammes", "Céleste"]
def team_prefix2(j, t, st, fr):
    parts = [{"text": "", "color": "white"}]
    if st:
        parts.append({"text": "★" * st + " ", "color": "gold", "bold": False})
    if fr == 7:                                   # cadre Étoilé (prestige 5) : en texte, sans glyphe
        parts.append({"text": "✦ ", "color": "gold", "bold": True})
    elif fr:
        parts.append(gj(f"cadre_{CADRES[fr - 1]}_g"))
    sty = dict(tier_style(j, t)); sty["text"] = f"{TIERS[t][0]}"
    parts.append(gj(f"metier_{j}"))
    parts.append({"text": " ", "color": "white"})
    parts.append(sty)
    if fr == 7:
        parts.append({"text": " ✦", "color": "gold", "bold": True})
    elif fr:
        parts.append(gj(f"cadre_{CADRES[fr - 1]}_d"))
    parts.append({"text": " ", "color": "white", "bold": False})
    return json.dumps(parts, ensure_ascii=False)
E2 = []
for j in jobs:
    for t in range(11):
        E2.append(f"team remove m.{j}{t}")
        for st in range(6):
            E2.append(f"team remove m.{j}{t}_{st}")
            for fr in range(8):
                E2 += [f"team add m.{j}{t}_{st}_{fr}", f"team modify m.{j}{t}_{st}_{fr} prefix {team_prefix2(j, t, st, fr)}"]
w(F + "prefixe/equipes.mcfunction", "\n".join(E2))
MJ2 = ["tag @s remove metiers.maj", "scoreboard players add @s m.cadre 0"]
for j, d in jobs.items():
    for t, (_, rng) in enumerate(TIERS):
        for st in range(6):
            for fr in range(8):
                MJ2.append(f"execute if score @s m.pref matches {d['idx']} if score @s m.{j}_lvl matches {rng} if score @s m.{j}_pr matches {st} if score @s m.cadre matches {fr} run team join m.{j}{t}_{st}_{fr} @s")
w(F + "prefixe/maj.mcfunction", "\n".join(MJ2))

# ================================================================ Forge
FG = [f"execute store result storage {NS}:fg ecl int 1 run scoreboard players get @s m.ecl"]
FG += [f"execute store result storage {NS}:fg cr_{j} int 1 run scoreboard players get @s m.cr_{j}" for j in JL]
for key, (j, p, e, lv) in CRP.items():
    FG += [f'data modify storage {NS}:fg c_{key} set value "red"',
           f'execute if score @s m.cr_{j} matches {p}.. if score @s m.ecl matches {e}.. run data modify storage {NS}:fg c_{key} set value "yellow"',
           f'execute unless score @s m.{j}_lvl matches {lv}.. unless score @s m.{j}_pr matches 1.. run data modify storage {NS}:fg c_{key} set value "dark_gray"']
for key, e in COMMUN.items():
    FG += [f'data modify storage {NS}:fg c_{key} set value "red"', f'execute if score @s m.ecl matches {e}.. run data modify storage {NS}:fg c_{key} set value "yellow"']
for key in list(CRP) + list(COMMUN):
    FG += [f'data modify storage {NS}:fg r_{key} set value ""',
           f'execute if score @s m.fo_{key} matches 1 run data modify storage {NS}:fg r_{key} set value "  ✔ récupérer"',
           f'execute if score @s m.fo_{key} matches 1 run data modify storage {NS}:fg c_{key} set value "green"']
# outil tenu en main pour les cristaux d'amélioration
FG += [f'data modify storage {NS}:fg g set value ""', f"data modify storage {NS}:fg sl set value 0", f"data modify storage {NS}:fg us set value 0", "scoreboard players set #hj m.tmp 0", f'data modify storage {NS}:fg outil set value "Tiens ton outil de métier en main pour sertir un cristal."']
for j, d in jobs.items():
    FG.append(f"execute if items entity @s weapon.mainhand {SEL(j)} run scoreboard players set #hj m.tmp {d['idx']}")
FG += [f'data modify storage {NS}:fg {c} set value "—"' for c in ("l_sag", "l_for", "l_eco", "l_eff")]
FG += [f'data modify storage {NS}:fg {c} set value "dark_gray"' for c in ("k_sag", "k_for", "k_eco", "k_eff")]
for j, d in jobs.items():
    FG.append(f"execute if score #hj m.tmp matches {d['idx']} run function {NS}:forge/infos_{j}")
w(F + "forge/calcul.mcfunction", "\n".join(FG))
w(F + "forge/menu.mcfunction", f"function {NS}:forge/calcul\nfunction {NS}:forge/menu_dialog with storage {NS}:fg")
w(F + "forge/outil.mcfunction", f"function {NS}:forge/calcul\nfunction {NS}:forge/outil_dialog with storage {NS}:fg")
w(F + "forge/boutique.mcfunction", f"function {NS}:forge/calcul\nfunction {NS}:forge/boutique_dialog with storage {NS}:fg")
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
              f'execute unless score @s m.{j}_lvl matches {lv}.. unless score @s m.{j}_pr matches 1.. run data modify storage {NS}:fg l_{kk} set value "✖ {lab} · niv. {lv}"',
              f'execute unless score @s m.{j}_lvl matches {lv}.. unless score @s m.{j}_pr matches 1.. run data modify storage {NS}:fg k_{kk} set value "dark_gray"',
              f'execute if score @s m.{sc}_{j} matches 1 run data modify storage {NS}:fg l_{kk} set value "✔ {lab} serti · clic pour le retirer"',
              f'execute if score @s m.{sc}_{j} matches 1 run data modify storage {NS}:fg k_{kk} set value "green"']
    if j in EFF_J:
        I += [f'data modify storage {NS}:fg l_eff set value "✔ Efficacité VII"', f'data modify storage {NS}:fg k_eff set value "green"']
        for n in range(7):
            rom = ["I", "II", "III", "IV", "V", "VI", "VII"][n]
            I += [f'execute if score @s m.ceff_{j} matches {n} run data modify storage {NS}:fg l_eff set value "Efficacité {rom} · {EFFC[n]}"',
                  f'execute if score @s m.ceff_{j} matches {n} run data modify storage {NS}:fg k_eff set value "red"',
                  f'execute if score @s m.ceff_{j} matches {n} if score @s m.cr_{j} matches {EFFC[n]}.. run data modify storage {NS}:fg k_eff set value "yellow"',
                  f'execute if score @s m.ceff_{j} matches {n} unless score @s m.{j}_lvl matches {EFFL[n]}.. unless score @s m.{j}_pr matches 1.. run data modify storage {NS}:fg l_eff set value "✖ Efficacité {rom} · niv. {EFFL[n]}"',
                  f'execute if score @s m.ceff_{j} matches {n} unless score @s m.{j}_lvl matches {EFFL[n]}.. unless score @s m.{j}_pr matches 1.. run data modify storage {NS}:fg k_eff set value "dark_gray"']
    else:
        I.append(f'data modify storage {NS}:fg l_eff set value "Efficacité : pas pour cet outil"')
    w(F + f"forge/infos_{j}.mcfunction", "\n".join(I))
ICON = {"marteau": "forge_marteau", "faux": "forge_faux", "arc3": "forge_arc3", "lasso": "forge_lasso", "parchemin": "forge_parchemin",
        "aimant": "forge_aimant", "cape": "forge_cape"}
NOMF = {"marteau": "Marteau du Mineur", "faux": "Faux du Fermier", "arc3": "Arc à triple tir", "lasso": "Lasso de l'Éleveur",
        "parchemin": "Parchemin de transfert", "aimant": "Aimant à objets", "cape": "Cape-planeur"}
fb = []
for i, (key, (j, p, e, lv)) in enumerate(CRP.items(), 1):
    lab = f'[{gs(ICON[key])},{{text:" {NOMF[key]}  ",color:"$(c_{key})",italic:false}},{gs("cristal_" + j)},{{text:" {p}",color:"$(c_{key})"}}' + \
          (f',{{text:"  "}},{gs("eclat")},{{text:" {e}",color:"$(c_{key})"}}' if e else "") + f',{{text:"$(r_{key})",color:"green",bold:true}}]'
    fb.append(f'{{label:{lab},width:320,tooltip:{{text:"{FORGE_IT[key][4]}\\nPrix : {p} cristaux de {jobs[j]["name"]}' + (f' + {e} éclats de boss' if e else '') +
              f' · {jobs[j]["name"]} niveau {lv}\\nDéjà forgé ? Clique pour le récupérer gratuitement s’il est perdu (une fois toutes les 10 minutes)."}},action:{{type:"run_command",command:"trigger metiers set {400 + i}"}}}}')
for i, (key, e) in enumerate(COMMUN.items(), 6):
    lab = f'[{gs(ICON[key])},{{text:" {NOMF[key]}  ",color:"$(c_{key})",italic:false}},{gs("eclat")},{{text:" {e}",color:"$(c_{key})"}},{{text:"$(r_{key})",color:"green",bold:true}}]'
    fb.append(f'{{label:{lab},width:320,tooltip:{{text:"{FORGE_IT[key][4]}\\nPrix : {e} éclats de boss\\nDéjà forgé ? Clique pour le récupérer gratuitement s’il est perdu (une fois toutes les 10 minutes)."}},action:{{type:"run_command",command:"trigger metiers set {400 + i}"}}}}')
fo = []
for i, (kk, ic, tipc) in enumerate((("sag", "forge_cristal_sagesse", "+10 % d’XP de métier avec cet outil."),
                                    ("for", "forge_cristal_fortune", "+1 Fortune, Butin ou Chance de la mer."),
                                    ("eco", "forge_cristal_echo", "5 % de chance qu’un gain d’XP rapporte un cristal en plus."),
                                    ("eff", "forge_cristal_efficacite", "Efficacité de l’outil, jusqu’à VII (niveau 80).")), 11):
    fo.append(f'{{label:[{gs(ic)},{{text:" $(l_{kk}) ",color:"$(k_{kk})",italic:false}},{{text:"$(g)",font:"metiers:icones",color:"white"}}],width:320,'
              f'tooltip:{{text:"{tipc}\\nPayé en cristaux du métier de l’outil tenu. Emplacements : 1 au palier 3, 2 au palier 6, 3 au palier 9."}},'
              f'action:{{type:"run_command",command:"trigger metiers set {400 + i}"}}}}')
fo.append(btn(txt("Baisser l’Efficacité d’un niveau (remboursé)", "aqua"), 415, 320, "Rend les cristaux du dernier niveau d’Efficacité. Pour retirer Sagesse, Fortune ou Écho, clique dessus."))
def bourse(j):
    return (f'{{text:"",hover_event:{{action:"show_text",value:{{text:"Cristaux de {jobs[j]["name"]}",color:"{jobs[j]["color"]}"}}}},'
            f'extra:[{gs("cristal_" + j)},{{text:" $(cr_{j})   ",color:"white"}}]}}')
crline = ",".join(bourse(j) for j in JL)
ECL = f'{{text:"",hover_event:{{action:"show_text",value:{{text:"Éclats de boss : contre les boss et avec les défis de la semaine",color:"light_purple"}}}},extra:[{gs("eclat")},{{text:" $(ecl) éclats de boss",color:"light_purple"}}]}}'
BOURSE = f'{{type:"minecraft:plain_message",width:420,contents:[{crline},{{text:"\\n"}},{ECL}]}}'
RET400 = 'exit_action:{label:"Retour",width:200,action:{type:"run_command",command:"trigger metiers set 1"}}}'
w(F + "forge/boutique_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Boutique de la Forge",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  f'body:[{BOURSE},{{type:"minecraft:plain_message",width:380,contents:{{text:"Survole un objet pour son effet. Jaune : tu peux l’acheter. Rouge : pas assez de cristaux ou d’éclats. Gris : niveau de métier trop bas.",color:"gray"}}}}],'
  f'actions:[{",".join(fb)}],columns:1,' + RET400)
w(F + "forge/outil_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Forger l’outil en main",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  f'body:[{BOURSE},'
  '{type:"minecraft:plain_message",width:380,contents:[{text:"$(outil)",color:"gray"},{text:"$(us) / $(sl)",color:"yellow"}]}],'
  f'actions:[{",".join(fo)}],columns:1,' + RET400)
HUB = [btn(f'[{gs("forge_marteau")},{txt("  Forger l’outil en main", "gold", True)}]', 470, 320, "Sertis des cristaux dans l’outil de métier que tu tiens : Sagesse, Fortune, Écho, Efficacité."),
       btn(f'[{gs("forge_cristal_sagesse")},{txt("  Skins d’outil et d’armure", "light_purple", True)}]', 420, 320, "Change l’apparence de tes outils et de ton armure."),
       btn(f'[{gs("cadre_dore_g")},{txt("Cadres de titre", "gold", True)},{gs("cadre_dore_d")}]', 472, 320, "Le cadre qui entoure ton titre devant ton pseudo.")]
w(F + "forge/menu_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Forge",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  f'body:[{BOURSE}],actions:[{",".join(HUB)}],columns:1,'
  'exit_action:{label:"Retour",width:200,action:{type:"run_command",command:"trigger metiers set 1"}}}')
# achats
for i, (key, (j, p, e, lv)) in enumerate(CRP.items(), 1):
    w(F + f"forge/acheter_{key}.mcfunction", "\n".join([
        f"execute if score @s m.fo_{key} matches 1 run return run function {NS}:forge/recup_{key}",
        f"execute unless score @s m.{j}_lvl matches {lv}.. unless score @s m.{j}_pr matches 1.. run return run {tr(f'Il faut être niveau {lv} en {jobs[j][chr(110)+chr(97)+chr(109)+chr(101)]}.', 'red')}",
        f"execute unless score @s m.cr_{j} matches {p}.. run return run {tr('Pas assez de cristaux.', 'red')}",
        f"execute unless score @s m.ecl matches {e}.. run return run {tr('Pas assez d’éclats de boss.', 'red')}",
        f"scoreboard players remove @s m.cr_{j} {p}", f"scoreboard players remove @s m.ecl {e}",
        f"function {NS}:forge/donner_{key}", f"scoreboard players set @s m.fo_{key} 1", "playsound minecraft:block.anvil.use master @s ~ ~ ~ 1 1",
        tr(f"Tu as forgé : {NOMF[key]}.", "gold"), f"function {NS}:forge/boutique"]))
for key, e in COMMUN.items():
    w(F + f"forge/acheter_{key}.mcfunction", "\n".join([
        f"execute if score @s m.fo_{key} matches 1 run return run function {NS}:forge/recup_{key}",
        f"execute unless score @s m.ecl matches {e}.. run return run {tr('Pas assez d’éclats de boss.', 'red')}",
        f"scoreboard players remove @s m.ecl {e}", f"function {NS}:forge/donner_{key}", f"scoreboard players set @s m.fo_{key} 1",
        "playsound minecraft:block.anvil.use master @s ~ ~ ~ 1 1", tr(f"Tu as forgé : {NOMF[key]}.", "gold"), f"function {NS}:forge/boutique"]))
# récupération d'un objet de la Forge perdu : gratuit, s'il n'est ni sur le joueur ni dans son coffre de l'Ender,
# une fois toutes les 10 minutes (même règle que les outils de métier)
for key in list(CRP) + list(COMMUN):
    poss = [f"container.* {FSEL(key)}", f"weapon.offhand {FSEL(key)}", f"armor.chest {FSEL(key)}", f"enderchest.* {FSEL(key)}"]
    if key == "lasso":
        poss += [f"container.* {FSEL('lasso_plein')}", f"weapon.offhand {FSEL('lasso_plein')}", f"enderchest.* {FSEL('lasso_plein')}"]
    RC_ = [f"execute if items entity @s {p_} run return run {tr(f'Tu as déjà ton objet sur toi ou dans ton coffre de l’Ender : {NOMF[key]}.')}" for p_ in poss]
    RC_ += ["scoreboard players operation @s m.tmp = @s m.fcd_" + key, "scoreboard players operation @s m.tmp /= #60 m.const",
            "scoreboard players operation @s m.tmp /= #2 m.const", "scoreboard players add @s m.tmp 1",
            f'execute if score @s m.fcd_{key} matches 1.. run return run tellraw @s ' + PREFIX + ',{"text":"Patiente encore ","color":"red"},{"score":{"name":"@s","objective":"m.tmp"},"color":"yellow"},{"text":" min avant de le récupérer.","color":"red"}]',
            f"scoreboard players set @s m.fcd_{key} 1200"]
    if key == "lasso":
        RC_.append("tag @s remove metiers.lasso_plein")
    RC_ += [f"function {NS}:forge/donner_{key}", "playsound minecraft:block.anvil.use master @s ~ ~ ~ 1 1.4",
            tr(f"Voici ton objet de la Forge : {NOMF[key]}. Pas besoin de le repayer.", "green"), f"function {NS}:forge/boutique"]
    w(F + f"forge/recup_{key}.mcfunction", "\n".join(RC_))
    w(F + f"admin/forge_{key}.mcfunction", "\n".join([f"scoreboard players set @s m.fo_{key} 1",
                                                       tr(f"Tu peux récupérer gratuitement : {NOMF[key]} (G, Forge, Boutique).", "green")]))
for c, (pr, lv, sc, only) in CRIS.items():
    D = [f"execute if items entity @s weapon.mainhand {SEL(j)} run return run function {NS}:forge/sertir_{c}_{j}" for j in JL]
    D.append(tr("Tiens ton outil de métier en main.", "red"))
    w(F + f"forge/sertir_{c}.mcfunction", "\n".join(D))
    for j in JL:
        if only is not None and j not in only:
            w(F + f"forge/sertir_{c}_{j}.mcfunction", tr("Ce cristal ne va pas sur cet outil.", "red"))
            continue
        w(F + f"forge/sertir_{c}_{j}.mcfunction", "\n".join([
            f"execute if score @s m.{sc}_{j} matches 1 run return run function {NS}:forge/desertir_{c}_{j}",
            f"execute unless score @s m.{j}_lvl matches {lv}.. unless score @s m.{j}_pr matches 1.. run return run {tr(f'Il faut être niveau {lv} dans ce métier.', 'red')}",
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
            tr("Cristal serti dans ton outil.", "aqua"), f"function {NS}:forge/outil"]))
for c, (pr, lv, sc, only) in CRIS.items():
    for j in JL:
        w(F + f"forge/desertir_{c}_{j}.mcfunction", "\n".join([
            f"scoreboard players set @s m.{sc}_{j} 0", f"scoreboard players add @s m.cr_{j} {pr}",
            f"function {NS}:{j}/outil_donner", "playsound minecraft:block.grindstone.use master @s ~ ~ ~ 1 1",
            tr(f"Cristal retiré : {pr} cristaux remboursés.", "aqua"), f"function {NS}:forge/outil"]))
D = [f"execute if items entity @s weapon.mainhand {SEL(j)} run return run function {NS}:forge/eff_{j}" for j in JL]
D.append(tr("Tiens ton outil de métier en main.", "red"))
w(F + "forge/eff.mcfunction", "\n".join(D))
for j in JL:
    if j not in EFF_J:
        w(F + f"forge/eff_{j}.mcfunction", tr("L’Efficacité ne va pas sur cet outil.", "red")); continue
    E = [f"execute if score @s m.ceff_{j} matches 7.. run return run {tr('Efficacité déjà au maximum.', 'red')}"]
    for n in range(7):
        E += [f"execute if score @s m.ceff_{j} matches {n} unless score @s m.{j}_lvl matches {EFFL[n]}.. unless score @s m.{j}_pr matches 1.. run return run {tr(f'Il faut être niveau {EFFL[n]} dans ce métier.', 'red')}",
              f"execute if score @s m.ceff_{j} matches {n} unless score @s m.cr_{j} matches {EFFC[n]}.. run return run {tr('Pas assez de cristaux.', 'red')}",
              f"execute if score @s m.ceff_{j} matches {n} run scoreboard players remove @s m.cr_{j} {EFFC[n]}"]
    E += [f"scoreboard players add @s m.ceff_{j} 1", f"function {NS}:{j}/outil_donner",
          "playsound minecraft:block.amethyst_block.resonate master @s ~ ~ ~ 1 1.4", tr("Efficacité améliorée.", "aqua"), f"function {NS}:forge/outil"]
    w(F + f"forge/eff_{j}.mcfunction", "\n".join(E))
D = [f"execute if items entity @s weapon.mainhand {SEL(j)} run return run function {NS}:forge/retirer_{j}" for j in JL]
D.append(tr("Tiens ton outil de métier en main.", "red"))
w(F + "forge/retirer.mcfunction", "\n".join(D))
for j in JL:
    R = [f"execute unless score @s m.ceff_{j} matches 1.. run return run {tr('Aucun niveau d’Efficacité acheté sur cet outil.', 'red')}"]
    for n in range(1, 8):
        R.append(f"execute if score @s m.ceff_{j} matches {n} run scoreboard players add @s m.cr_{j} {EFFC[n - 1]}")
    R += [f"scoreboard players remove @s m.ceff_{j} 1", f"function {NS}:{j}/outil_donner",
          "playsound minecraft:block.grindstone.use master @s ~ ~ ~ 1 1", tr("Un niveau d’Efficacité retiré, cristaux remboursés.", "aqua"), f"function {NS}:forge/outil"]
    w(F + f"forge/retirer_{j}.mcfunction", "\n".join(R))

# ================================================================ skins et cadres
TGT = [("a", "Armure des Guildes")] + [(j, f"{TOOL[j][1]} de {jobs[j]['name']}") for j in JL if j != "k"]   # truelle : pas de skin 3D
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
SK += ["scoreboard players set #p5 m.tmp 0"] + [f"execute if score @s m.{j}_pr matches 5.. run scoreboard players set #p5 m.tmp 1" for j in JL]
SK += [f'data modify storage {NS}:sk f7 set value "dark_gray"', f'execute if score #p5 m.tmp matches 1 run data modify storage {NS}:sk f7 set value "yellow"',
       f'data modify storage {NS}:sk e7 set value ""', "scoreboard players add @s m.cd_7 0",
       f'execute if score @s m.cd_7 matches 1 run data modify storage {NS}:sk f7 set value "green"',
       f'execute if score @s m.cadre matches 7 run data modify storage {NS}:sk e7 set value " ★"']
w(F + "skins/calcul.mcfunction", "\n".join(SK))
w(F + "skins/menu.mcfunction", f"function {NS}:skins/calcul\nfunction {NS}:skins/menu_dialog with storage {NS}:sk")
w(F + "skins/cadres.mcfunction", f"function {NS}:skins/calcul\nfunction {NS}:skins/cadres_dialog with storage {NS}:sk")
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
SKD = ['{label:[{text:"Objet : ",color:"gray"},{text:"$(cible)",color:"aqua"},{text:"  ↻",color:"gray"}],width:200,'
       'tooltip:{text:"Clique pour passer à l’objet suivant : l’armure ou l’un de tes 9 outils de métier."},action:{type:"run_command",command:"trigger metiers set 421"}}',
       btn(txt("Apparence de base", "white"), 430, 200, "Retire le skin de cet objet.")]
SKD += [f'{{label:{{text:"$(s{i})",color:"$(k{i})"}},width:200,tooltip:{{text:"{tip}"}},action:{{type:"run_command",command:"trigger metiers set {430 + i}"}}}}'
        for i, tip in enumerate(["Givre : acier bleu glacé, éclats de glace.", "Corail : métal turquoise des grands fonds, gemmes corail.",
                                 "Or royal : or massif serti de rubis.", "Ossements : trophée, vaincre 3 fois la Reine arachnide.",
                                 "Magma : trophée, vaincre 3 fois le Brasier ancestral.", "Ombre : réservé aux joueurs passés par le prestige."], 1)]
CAD = [btn(txt("Sans cadre", "white"), 440, 200, "Ton titre s’affiche sans cadre.")]
CAD += [f'{{label:[{gs("cadre_" + CADRES[ci - 1] + "_g")},{{text:"{cn}",color:"$(f{ci})"}},{gs("cadre_" + CADRES[ci - 1] + "_d")},{{text:"$(e{ci})",color:"gold"}}],width:200,'
        f'tooltip:{{text:"{tip}"}},action:{{type:"run_command",command:"trigger metiers set {440 + ci}"}}}}'
        for ci, (cn, tip) in enumerate(zip(CADRE_NOM, ["Offert.", "3 éclats de boss.", "6 éclats de boss.", "10 éclats de boss.",
                                                       "Trophée : vaincre 5 fois le Brasier ancestral.", "3 prestiges au total."]), 1)]
CAD.append('{label:[{text:"✦ ",color:"gold",bold:true},{text:"Étoilé",color:"$(f7)"},{text:" ✦",color:"gold",bold:true},{text:"$(e7)",color:"gold"}],width:200,'
           'tooltip:{text:"Prestige : 5 étoiles dans un métier."},action:{type:"run_command",command:"trigger metiers set 447"}}')
w(F + "skins/cadres_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Cadres de titre",color:"gold",bold:true},can_close_with_escape:true,pause:false,'
  f'body:{{type:"minecraft:plain_message",width:380,contents:[{{text:"Le cadre entoure ton titre de métier devant ton pseudo. Le titre affiché se choisit sur la page d’un métier.\\n",color:"gray"}},{gs("eclat")},{{text:" $(ecl) éclats",color:"light_purple"}}]}},'
  f'actions:[{",".join(CAD)}],columns:2,'
  'exit_action:{label:"Retour",width:200,action:{type:"run_command",command:"trigger metiers set 1"}}}')
w(F + "skins/menu_dialog.mcfunction",
  '$dialog show @s {type:"minecraft:multi_action",title:{text:"Skins d’outil et d’armure",color:"light_purple",bold:true},can_close_with_escape:true,pause:false,'
  'body:[{type:"minecraft:item",item:{id:"minecraft:paper",components:{"minecraft:item_model":"metiers:$(model)","minecraft:custom_model_data":{strings:["$(skin)"]}}},'
  'show_decorations:false,show_tooltip:false,description:{width:240,contents:[{text:"$(cible)\\n",color:"aqua",bold:true},'
  f'{{text:"Le skin change les matériaux, pas la forme du palier, et suit l’objet quand il évolue.\\n",color:"gray",bold:false}},{gs("eclat")},{{text:" $(ecl) éclats",color:"light_purple"}}]}}}}],'
  f'actions:[{",".join(SKD)}],columns:2,'
  'exit_action:{label:"Retour",width:200,action:{type:"run_command",command:"trigger metiers set 1"}}}')
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
w(F + "skins/cadre.mcfunction", f"$scoreboard players set @s m.cadre $(i)\ntag @s add metiers.maj\nfunction {NS}:prefixe/maj\nfunction {NS}:skins/cadres")
w(F + "skins/cadre_0.mcfunction", f"function {NS}:skins/cadre {{i:0}}")

# ================================================================ déclencheurs
TRG = [f'execute if score @s m.trig matches 400 run function {NS}:appel {{f:"forge/menu"}}',
       f'execute if score @s m.trig matches 470 run function {NS}:appel {{f:"forge/outil"}}',
       f'execute if score @s m.trig matches 471 run function {NS}:appel {{f:"forge/menu"}}',   # 26.0 : plus de boutique d'objets
       f'execute if score @s m.trig matches 472 run function {NS}:appel {{f:"skins/cadres"}}']
TRG += [f'execute if score @s m.trig matches 411 run function {NS}:appel {{f:"forge/sertir_sagesse"}}',
        f'execute if score @s m.trig matches 412 run function {NS}:appel {{f:"forge/sertir_fortune"}}',
        f'execute if score @s m.trig matches 413 run function {NS}:appel {{f:"forge/sertir_echo"}}',
        f'execute if score @s m.trig matches 414 run function {NS}:appel {{f:"forge/eff"}}',
        f'execute if score @s m.trig matches 415 run function {NS}:appel {{f:"forge/retirer"}}',
        f'execute if score @s m.trig matches 420 run function {NS}:appel {{f:"skins/menu"}}',
        f'execute if score @s m.trig matches 421 run function {NS}:appel {{f:"skins/cycle"}}']
TRG += [f'execute if score @s m.trig matches {430 + i} run function {NS}:appel {{f:"skins/choix_{i}"}}' for i in range(7)]
TRG += [f'execute if score @s m.trig matches {440 + i} run function {NS}:appel {{f:"skins/cadre_{i}"}}' for i in range(7)]
TRG += [f'execute if score @s m.trig matches {TTI(d)} run function {NS}:appel {{f:"{j}/titre"}}' for j, d in jobs.items()]
TRG += [f'execute if score @s m.trig matches 497 run function {NS}:appel {{f:"activites"}}']
TRG += [f'execute if score @s m.trig matches 614 run function {NS}:appel {{f:"k/kit"}}',
        f'execute if score @s m.trig matches 610 run function {NS}:appel {{f:"f/saison"}}',
        f'execute if score @s m.trig matches 611 run function {NS}:appel {{f:"n/surpuissance"}}',
        f'execute if score @s m.trig matches 612 run function {NS}:appel {{f:"sac/donner"}}',
        f'execute if score @s m.trig matches 613 run function {NS}:appel {{f:"c/arc_recup"}}',
        f'execute if score @s m.trig matches 701 run function {NS}:appel {{f:"tp/enregistrer"}}',
        f'execute if score @s m.trig matches 702 run function {NS}:appel {{f:"tp/effacer"}}',
        f'execute if score @s m.trig matches 721..730 run function {NS}:appel {{f:"tp/aller"}}',
        f'execute if score @s m.trig matches 741..750 run function {NS}:appel {{f:"tp/renommer"}}']
add_lines(F + "trigger.mcfunction", TRG)

# menu de la touche G / Échap : Minecraft impose un écran fixe ici (pas de niveaux ni de barres possibles),
# donc un seul gros bouton qui ouvre le vrai écran « Mes métiers », plus deux raccourcis.
RUN = lambda n: {"type": "run_command", "command": f"trigger metiers set {n}"}
hub = [{"label": [{"text": ""}, gj("forge_marteau"), {"text": "  Ouvrir mes métiers  ", "color": "gold", "bold": True}, gj("eclat")],
        "tooltip": {"text": "Niveaux, compétences, outils, défis, Forge."}, "width": 310, "action": RUN(1)},
       {"label": [{"text": ""}, gj("forge_marteau"), {"text": "  Forge  ", "color": "gold", "bold": True}, gj("eclat")], "width": 310, "action": RUN(400)},
       {"label": {"text": "Défis du jour", "color": "aqua", "bold": True}, "width": 310, "action": RUN(4)}]
wj(f"data/{NS}/dialog/ouvrir.json", {"type": "minecraft:multi_action", "title": {"text": "Métiers", "color": "gold", "bold": True},
                                     "external_title": {"text": "Métiers"}, "can_close_with_escape": True, "pause": False,
                                     "actions": hub, "columns": 1})


# ================================================================ aide
AIDE = [
    ("Les métiers", "gold", "Chaque action de métier rapporte de l'XP : couper du bois, miner, récolter, tuer, pêcher, élever, enchanter, explorer, échanger. Tous les 10 niveaux, ton outil passe au palier suivant (nouvelle forme, meilleures stats) et tu gagnes un titre."),
    ("Compétences", "yellow", "Chaque niveau donne des points. Dans la page d'un métier, achète ses 6 compétences : une au niveau 5, les branches aux niveaux 20 puis 45, l'ultime au niveau 70. Le point rouge sur l'accueil signale des points ou une récompense à prendre."),
    ("Cristaux de métier", "aqua", "La monnaie de chaque métier, pour la Forge et les skins d'outil. Tu en gagnes à chaque palier d'outil (3 par palier), 4 par défi du jour réussi, 20 avec le défi de la semaine. Le cristal Écho en donne parfois en plus."),
    ("Éclats de boss", "light_purple", "La monnaie rare. 1 éclat par boss vaincu (2 pour le plus gros dégât), 1 avec le défi de la semaine, 1 avec le défi collectif si tu y as participé. Ils servent aux objets de la Forge, aux skins d'armure et aux cadres de titre."),
    ("La Forge", "gold", "Objets de métier (marteau 3x3, faux, arc triple, lasso, parchemin), objets communs (aimant, cape-planeur) et cristaux à sertir dans l'outil tenu en main : Sagesse (+10 % d'XP), Fortune, Écho, Efficacité jusqu'à VII. Emplacements : 1 au palier 3, 2 au palier 6, 3 au palier 9."),
    ("Boss", "red", "Toutes les 30 minutes de jeu (dès 1 joueur connecté), un boss apparaît près d'un joueur : Colosse, Reine arachnide, Liche, Brasier, Creeper géant. Ses PV montent avec le nombre de joueurs et il appelle des renforts à 66 % et 33 %. Chaque participant reçoit un butin (plus gros en difficulté difficile) et des éclats ; le vaincre plusieurs fois débloque des skins."),
    ("Défis", "aqua", "Chaque jour : un défi par métier. Chaque semaine : un gros défi perso et un défi collectif pour tout le serveur. Tout se suit dans Défis du jour."),
    ("Armure des Guildes", "#F1CF4E", "Elle se débloque avec ton score total (somme des niveaux) et évolue sur 11 paliers. Récupère-la depuis son bouton sur l'accueil."),
]
contents = []
for titre, col, txt_ in AIDE:
    contents += [{"text": titre + "\n", "color": col, "bold": True}, {"text": txt_ + "\n\n", "color": "white", "bold": False}]
wj(f"data/{NS}/dialog/aide.json", {"type": "minecraft:notice", "title": {"text": "Aide des métiers", "color": "gold", "bold": True},
                                  "can_close_with_escape": True, "pause": False,
                                  "body": [{"type": "minecraft:plain_message", "width": 400, "contents": contents}],
                                  "action": {"label": "Retour", "width": 200, "action": {"type": "run_command", "command": "trigger metiers set 1"}}})
w(F + "aide.mcfunction", f"dialog show @s {NS}:aide")
add_lines(F + "trigger.mcfunction", [f'execute if score @s m.trig matches 460 run function {NS}:appel {{f:"aide"}}'])

# pioche : bascule Fortune / Toucher de soie
w(F + "m/soie.mcfunction", "\n".join([
    "scoreboard players add @s m.silk 0",
    "execute if score @s m.silk matches 1 run scoreboard players set #s m.tmp 0",
    "execute unless score @s m.silk matches 1 run scoreboard players set #s m.tmp 1",
    "scoreboard players operation @s m.silk = #s m.tmp",
    f"execute if items entity @s container.* {SEL('m')} run function {NS}:m/outil_donner",
    f"execute if items entity @s weapon.offhand {SEL('m')} run function {NS}:m/outil_donner",
    f"execute if score @s m.silk matches 1 run {tr('Pioche en Toucher de soie.', 'aqua')}",
    f"execute if score @s m.silk matches 0 run {tr('Pioche en Fortune.', 'aqua')}",
    "playsound minecraft:block.enchantment_table.use master @s ~ ~ ~ 0.6 1.4", f"function {NS}:m/arbre"]))
add_lines(F + "trigger.mcfunction", [f'execute if score @s m.trig matches 761 run function {NS}:appel {{f:"m/soie"}}'])
add_lines(F + "refonte/load.mcfunction", ["scoreboard objectives add m.silk dummy"])


# onglets Outil (550 + idx) et Progression (560 + idx) de la page de métier (25/11/2026)
for j, d in jobs.items():
    w(F + f"{j}/onglet_outil.mcfunction", f"scoreboard players set #vue m.tmp 1\nfunction {NS}:{j}/arbre")
    w(F + f"{j}/onglet_prog.mcfunction", f"scoreboard players set #vue m.tmp 2\nfunction {NS}:{j}/arbre")
add_lines(F + "trigger.mcfunction",
          [f'execute if score @s m.trig matches {550 + d["idx"]} run function {NS}:appel {{f:"{j}/onglet_outil"}}' for j, d in jobs.items()] +
          [f'execute if score @s m.trig matches {560 + d["idx"]} run function {NS}:appel {{f:"{j}/onglet_prog"}}' for j, d in jobs.items()])

# -*- coding: utf-8 -*-
# 26/11/2026 : menus « succès ». Un panneau = un fond de blocs encadré + des icônes dans les cadres de l'écran des
# Progrès, cliquables (clic et infobulle par icône), avec un nom et une info courte sous chaque icône.
# Tout tient dans un seul plain_message : la ligne 0 pose le fond et les icônes (police metiers:arbre, espaces négatifs),
# les lignes suivantes portent les libellés, placés au pixel près avec les espaces de la même police.
# Chaque ligne fait exactement la largeur du panneau : le dialogue centre toutes les lignes de la même façon.
# Une info variable (niveau...) est suivie d'un espace de rattrapage choisi selon sa longueur ($(pK)), calculé par
# le pack qui affiche le panneau avec PAD (nombre de chiffres -> caractère d'espace).
# Exécuté par ref_arbre.py avant l'écriture de la police. Les autres packs lisent sources/panneaux.json.
import json as _json

LARGF = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "larg_police.json"), encoding="utf-8"))


def larg_txt(s, gras=False):
    return sum(LARGF.get(c, 6) + (1 if gras else 0) for c in s)


def snbt(o):
    if isinstance(o, bool):
        return "true" if o else "false"
    if isinstance(o, (int, float)):
        return str(o)
    if isinstance(o, str):
        return '"' + o.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(o, list):
        return "[" + ",".join(snbt(v) for v in o) + "]"
    return "{" + ",".join(f"{k}:{snbt(v)}" for k, v in o.items()) + "}"


_FA = {"font": "metiers:arbre", "color": "white", "shadow_color": 0}
PAN_ETATS = ("on", "off", "dispo", "notif")
PANNEAUX = {}


def _noeud_img(ic, cadre, etat):
    im = _CAD[(cadre, etat in ("on", "notif"))].copy()
    icn = ic if etat in ("on", "notif") else _gris(ic, 6)
    im.alpha_composite(icn, (5, 5))
    if etat in ("dispo", "notif"):
        dd = _Draw.Draw(im)
        dd.rectangle([(20, 1), (24, 5)], fill=(255, 255, 85, 255), outline=(0, 0, 0, 255))
    if im.getpixel((25, 13))[3] == 0:
        im.putpixel((25, 13), (0, 0, 0, 3))
    return im


def panneau(nom, W, H, mix, cases):
    """cases : liste de dicts {x, ligne (ligne du nom sous l'icône), icone, cadre, nom, couleur, info (texte fixe ou None),
    var (True si l'info est variable : $(iK) puis $(pK)), est (largeur estimée de l'info variable)}."""
    im = _fond_mixte(mix, W, H, "panneau-" + nom)   # blocs mêlés + cadre de pierre noire (ref_arbre.py)
    cf, af = fond_glyphes(f"pan_{nom}", im)
    noeuds = []
    for k, c in enumerate(cases, 1):
        ic = _tex(c["icone"]).resize((16, 16), _Img.NEAREST)
        cy = 9 * c["ligne"] - 15
        et = {e: _glyphe(f"pan_{nom}_{k}_{e}", _noeud_img(ic, c.get("cadre", "task"), e), cy - 13) for e in PAN_ETATS}
        noeuds.append({"x": c["x"] - 13, "etats": {e: v[0] for e, v in et.items()}, "adv": et["on"][1]})
    PANNEAUX[nom] = {"W": W, "H": H, "fond": cf, "adv": af, "cases": cases, "noeuds": noeuds}


def pad(n):
    """Caractère(s) d'espace de la police de l'arbre pour n pixels (n peut être négatif)."""
    return _esp(n)


def panneau_contenu(nom, clics, survols, etats=None):
    """Liste de composants (dicts) du plain_message. clics[k] : commande ; survols[k] : composant d'infobulle ;
    etats[k] : nom d'état fixe ou None pour « $(aK) » (rempli par le pack avec PANNEAUX_JSON[nom].etats)."""
    P = PANNEAUX[nom]
    W = P["W"]
    comps = [dict(text=P["fond"] + _esp(-P["adv"]), **_FA)]
    for k, n in enumerate(P["noeuds"], 1):
        e = (etats or {}).get(k)
        car = n["etats"][e] if e else f"$(a{k})"
        c = dict(text=_esp(n["x"]) + car + _esp(-(n["x"] + n["adv"])), **_FA)
        if clics.get(k):
            c["click_event"] = {"action": "run_command", "command": clics[k]}
        if survols.get(k):
            c["hover_event"] = {"action": "show_text", "value": survols[k]}
        comps.append(c)
    comps.append(dict(text=_esp(W), **_FA))
    # libellés, ligne par ligne
    nl = max(c["ligne"] + (1 if c.get("info") is not None or c.get("var") else 0) for c in P["cases"]) + 1
    lignes = {i: [] for i in range(1, nl)}
    for k, c in enumerate(P["cases"], 1):
        if c.get("nomvar"):   # nom caché tant que pas découvert : $(nK) puis rattrapage $(qK)
            lignes[c["ligne"]].append((c["x"], [(f"$(n{k})", c.get("couleur", "white"), larg_txt(c["nom"]))], ("q", "s", k)))
        else:
            lignes[c["ligne"]].append((c["x"], [(c["nom"], c.get("couleur", "white"), larg_txt(c["nom"]))], None))
        if c.get("var"):
            lignes[c["ligne"] + 1].append((c["x"], [(f"$(i{k})", "gray", c.get("est", 30))], ("p", "r", k)))
        elif c.get("info") is not None:
            lignes[c["ligne"] + 1].append((c["x"], [(c["info"], "gray", larg_txt(c["info"]))], None))
    for i in range(1, nl):
        comps.append({"text": "\n", "font": "minecraft:default"})
        cur = 0
        for x, parts, kvar in sorted(lignes[i]):
            w_ = sum(p[2] for p in parts)
            x0 = x - w_ // 2
            comps.append(dict(text=_esp(x0 - cur), **_FA))
            if kvar:   # texte variable : rattrapage avant et après, choisis par le pack dans « pads » selon sa largeur réelle
                comps.append(dict(text=f"$({kvar[0]}{kvar[2]})", **_FA))
            for t_, col, _w in parts:
                comps.append({"text": t_, "color": col, "font": "minecraft:default"})
            if kvar:
                comps.append(dict(text=f"$({kvar[1]}{kvar[2]})", **_FA))
            cur = x0 + w_
        comps.append(dict(text=_esp(W - cur), **_FA))
    return comps


def panneau_corps(nom, clics, survols, etats=None, largeur=None):
    """Élément de corps de dialogue en SNBT (pour les fonctions de Métiers)."""
    return snbt({"type": "minecraft:plain_message", "width": largeur or PANNEAUX[nom]["W"] + 10,
                 "contents": panneau_contenu(nom, clics, survols, etats)})


def pad_var(nom, k, texte_len_px):
    """Caractère de rattrapage pour une info variable de largeur réelle texte_len_px (estimée à c['est'])."""
    c = PANNEAUX[nom]["cases"][k - 1]
    return _esp(c.get("est", 30) - texte_len_px) if c.get("est", 30) != texte_len_px else ""


# ---------------------------------------------------------------- les panneaux
_MIXM = ("oak_log", [("oak_planks", 4), ("spruce_planks", 2), ("birch_planks", 1), ("bookshelf", 1)])
_JOBS_ORDRE = list(jobs)
_IC_J = {"b": "item/iron_axe", "f": "item/iron_hoe", "m": "item/iron_pickaxe", "c": "item/iron_sword", "p": "item/fishing_rod",
         "e": "item/lead", "n": "item/enchanted_book", "x": "item/chainmail_boots", "t": "item/emerald", "k": "item/brick"}
_cases = []
for i, j in enumerate(_JOBS_ORDRE):
    _cases.append({"x": 47 + (i % 5) * 70, "ligne": 5 if i < 5 else 11, "icone": _IC_J[j], "nom": jobs[j]["name"],
                   "couleur": jobs[j]["color"], "var": True, "est": larg_txt("niv 55")})
for i, (ic, nm) in enumerate((("item/netherite_upgrade_smithing_template", "Forge"), ("item/clock_00", "Défis"), ("item/writable_book", "Quêtes"),
                              ("item/golden_chestplate", "Armure"), ("item/spyglass", "Sommaire"), ("item/compass_00", "Plus"))):
    _cases.append({"x": 42 + i * 58, "ligne": 17, "icone": ic, "nom": nm, "couleur": "gold", "cadre": "goal"})
panneau("metiers", 374, 186, _MIXM, _cases)

_MIXC = ("terracotta", [("cut_sandstone", 3), ("chiseled_sandstone", 1), ("emerald_block", 1), ("gold_block", 1)])
_CC = [("item/emerald", "Marché", "430 objets"), ("item/gold_ingot", "Banque", "virements, épargne"), ("item/name_tag", "Hôtel des ventes", "entre joueurs"),
       ("item/clock_00", "Bourse", "cours du jour"), ("item/blaze_powder", "Spawners", "à poser chez toi"), ("item/compass_00", "Plus", "classements, aide")]
panneau("commerce", 400, 136, _MIXC, [{"x": 80 + (i % 3) * 120, "ligne": 5 if i < 3 else 11, "icone": ic, "nom": nm, "info": inf,
                                        "couleur": "green", "cadre": "goal" if i == 0 else "task"} for i, (ic, nm, inf) in enumerate(_CC)])

_MIXS = ("dark_oak_planks", [("oak_planks", 3), ("stone_bricks", 2), ("mossy_stone_bricks", 1), ("bookshelf", 1)])
_SC = [("item/iron_pickaxe", "Métiers", "gold", "niveaux, arbres"), ("item/emerald", "Commerce", "green", "marché, banque"),
       ("item/lead", "Compagnons", "#C878FF", "ils t'accompagnent"), ("item/bone", "Bestiaire", "#D03030", "créatures de la nuit"),
       ("item/name_tag", "Mon profil", "yellow", "ton parcours"), ("item/book", "Guide", "white", "bien démarrer")]
panneau("serveur", 400, 136, _MIXS, [{"x": 80 + (i % 3) * 120, "ligne": 5 if i < 3 else 11, "icone": ic, "nom": nm, "couleur": col,
                                       "info": inf, "cadre": "goal" if i < 4 else "task"} for i, (ic, nm, col, inf) in enumerate(_SC)])

_MIXK = ("oak_log", [("moss_block", 3), ("podzol_top", 1), ("rooted_dirt", 1), ("mossy_cobblestone", 1)])
_KC = [("item/bone", "Loup"), ("item/cod", "Chat"), ("item/feather", "Perroquet"), ("item/snowball", "Bonhomme de neige"),
       ("item/amethyst_shard", "Allay"), ("item/iron_ingot", "Golem"), ("item/ghast_tear", "Ghast joyeux"), ("item/dragon_breath", "Dragon"),
       ("item/nether_star", "Wither")]
panneau("compagnons", 400, 190, _MIXK, [{"x": 80 + (i % 3) * 120, "ligne": 5 + 6 * (i // 3), "icone": ic, "nom": nm, "couleur": "#E0A040",
                                          "var": True, "est": larg_txt("niv 15"), "cadre": "challenge" if i >= 6 else "task"}
                                         for i, (ic, nm) in enumerate(_KC)])

_MIXB = ("dark_oak_log", [("deepslate", 3), ("cobbled_deepslate", 2), ("mossy_cobblestone", 1), ("coarse_dirt", 1)])
_BC = [("item/ender_eye", "SlenderMan"), ("item/diamond_pickaxe", "Herobrine"), ("item/goat_horn", "Siren Head"), ("item/candle", "La Nonne"),
       ("item/red_dye", "Le Clown"), ("item/iron_chain", "Pinhead"), ("item/white_dye", "Dame blanche"), ("item/bone", "Loup-garou"),
       ("item/blaze_powder", "Feu follet"), ("item/lantern", "Rôdeur"), ("item/ink_sac", "Croque-mitaine")]
panneau("bestiaire", 400, 190, _MIXB, [{"x": 65 + (i % 4) * 90, "ligne": 5 + 6 * (i // 4), "icone": ic, "nom": nm, "couleur": "#D03030",
                                        "var": True, "est": larg_txt("12 victoires"), "nomvar": True, "cadre": "challenge" if i == 10 else "task"}
                                       for i, (ic, nm) in enumerate(_BC)])


# ---------------------------------------------------------------- export pour les autres packs (Commerce, Compagnons, Bestiaire)
# contenu : composants JSON avec « §CK » (commande du clic) et « §HK » (infobulle, remplacée par un composant) ;
# etats : caractère de chaque état par case ; pads : pour une largeur réelle w (px), le caractère qui rattrape l'estimation.
PAN_EXPORT = {}
for _n, _P in PANNEAUX.items():
    _k = range(1, len(_P["cases"]) + 1)
    _pads = {}
    for _i, _c in enumerate(_P["cases"], 1):
        for (av, ap, est) in ((("p", "r", _c.get("est", 30)),) if _c.get("var") else ()) + ((("q", "s", larg_txt(_c["nom"])),) if _c.get("nomvar") else ()):
            _pads[f"{av}{_i}"] = {str(w_): [_esp((est - w_) // 2), _esp(est - w_ - (est - w_) // 2)] for w_ in range(0, 141)}
    PAN_EXPORT[_n] = {"contenu": panneau_contenu(_n, {k: f"§C{k}" for k in _k}, {k: f"§H{k}" for k in _k}),
                      "etats": {str(i): n_["etats"] for i, n_ in enumerate(_P["noeuds"], 1)}, "pads": _pads, "largeur": _P["W"] + 10}
_json.dump(PAN_EXPORT, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "panneaux.json"), "w", encoding="utf-8"), ensure_ascii=False)

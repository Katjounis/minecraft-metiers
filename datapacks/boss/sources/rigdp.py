"""Traduit un squelette (rig.Rig) et ses animations en fonctions : invoquer, jouer/<anim>, tick d'animation.

Chaque piece est un item_display tague bs.p.<id piece>. Une cle d'animation fixe la matrice cible de chaque piece
avec interpolation_duration = duree de la cle : le client interpole tout seul (pas de calcul en jeu).
Etat : #a<rig> bs.an (animation en cours, 0 = figee), #f<rig> bs.an (tick dans l'animation).
"""
from commun import fn, NS
from rig import snbt_matrice


def generer(R, anims, defaut_fn, luminosite=10, view=4.0, racine=None):
    """defaut_fn : fonction appelee a la fin d'une animation non bouclee (choisit l'animation suivante)."""
    nom = R.nom
    from rig import mul, echelle as _ech
    _s, _tag = racine if racine else (1.0, None)
    _mat = R.matrices
    R_matrices = (lambda pose=None: {k: mul(_ech(_s), v) for k, v in _mat(pose).items()}) if racine else _mat
    repos = R_matrices({})
    pieces = R.pieces()
    # ---------------------------------------------------------------- invoquer (a la position courante)
    lignes = []
    for o, lueur in pieces:
        pid = R.ident_piece(o, lueur)
        br = "brightness:{sky:15,block:15}" if lueur else f"brightness:{{sky:0,block:{luminosite}}}"
        lignes.append(
            f'summon minecraft:item_display ~ ~ ~ {{Tags:["bs.e","bs.os","bs.os.{nom}","bs.p.{pid}"{(',"' + _tag + '"') if _tag else ""}],'
            f'item:{{id:"minecraft:paper",count:1,components:{{"minecraft:item_model":"{NS}:{pid}"}}}},item_display:"none",'
            f'teleport_duration:1,interpolation_duration:0,view_range:{view}f,shadow_radius:0f,{br},'
            f'transformation:{snbt_matrice(repos[pid])}}}')
    fn(f"rig/{nom}/invoquer", lignes)
    fn(f"rig/{nom}/retirer", f"kill @e[type=minecraft:item_display,tag=bs.os.{nom}]")
    # ---------------------------------------------------------------- animations
    ids = {}
    tick = [f"scoreboard players add #f{nom} bs.an 1"]
    for i, (an, A) in enumerate(anims.items(), start=1):
        ids[an] = i
        cles = A["cles"]
        mats = [R_matrices(p) for _, p in cles]
        prev = None
        temps = 0
        t_lignes = []
        for k, ((d, _), M) in enumerate(zip(cles, mats)):
            l = []
            for pid, m in M.items():
                if prev is not None and prev[pid] == m and k > 0:
                    continue
                l.append(f"data merge entity @e[type=minecraft:item_display,tag=bs.p.{pid},limit=1] "
                         f"{{start_interpolation:0,interpolation_duration:{d},transformation:{snbt_matrice(m)}}}")
            fn(f"rig/{nom}/a/{an}/k{k}", l or ["return 0"])
            if k > 0:
                t_lignes.append(f"execute if score #f{nom} bs.an matches {temps} run function {NS}:rig/{nom}/a/{an}/k{k}")
            temps += d
            prev = M
        if A["boucle"]:
            t_lignes.append(f"execute if score #f{nom} bs.an matches {temps}.. run scoreboard players set #f{nom} bs.an 0")
            t_lignes.append(f"execute if score #f{nom} bs.an matches 0 run function {NS}:rig/{nom}/a/{an}/k0")
        elif A.get("fige"):
            t_lignes.append(f"execute if score #f{nom} bs.an matches {temps}.. run scoreboard players set #a{nom} bs.an 0")
        else:
            t_lignes.append(f"execute if score #f{nom} bs.an matches {temps}.. run function {defaut_fn}")
        fn(f"rig/{nom}/a/{an}/t", t_lignes)
        fn(f"rig/{nom}/jouer/{an}", [f"scoreboard players set #a{nom} bs.an {i}", f"scoreboard players set #f{nom} bs.an 0",
                                     f"function {NS}:rig/{nom}/a/{an}/k0"])
        tick.append(f"execute if score #a{nom} bs.an matches {i} run function {NS}:rig/{nom}/a/{an}/t")
    fn(f"rig/{nom}/tick", tick)
    return ids


def piece_simple(R, tags, luminosite=15, view=2.0, extra=""):
    """NBT d'un item_display pour un modele d'une seule piece (corbeau, livre, rune, lune...)."""
    out = []
    M = R.matrices({})
    for o, lueur in R.pieces():
        pid = R.ident_piece(o, lueur)
        br = "brightness:{sky:15,block:15}" if (lueur or luminosite >= 15) else f"brightness:{{sky:0,block:{luminosite}}}"
        out.append((pid, f'{{id:"minecraft:item_display",Tags:{tags},item:{{id:"minecraft:paper",count:1,components:{{"minecraft:item_model":"{NS}:{pid}"}}}},'
                         f'item_display:"none",teleport_duration:1,view_range:{view}f,{br},transformation:{snbt_matrice(M[pid])}{extra}}}'))
    return out

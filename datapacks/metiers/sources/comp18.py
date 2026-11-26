# -*- coding: utf-8 -*-
# 26.0 (26/11/2026) : arbres à 18 compétences. Exécuté par datapack.py juste après la définition de SKILLS.
# Chaque métier (sauf le Bâtisseur) garde ses 6 compétences en tronc (n° 1 à 6, en chaîne) et gagne deux branches de 6 :
# gauche n° 7 à 12, droite n° 13 à 18. Rangées de niveau : 10, 20, 30, 45, 60, 80 pour les branches.
# Coûts réels (plus de doublement) : tronc 3, 4, 6, 8, 12, 16 ; branches 4, 6, 8, 10, 12, 14. Tout l'arbre = 157 points,
# le niveau 100 en donne 99 et chaque étoile de prestige 99 de plus : l'arbre complet demande le prestige.
# Effets : ref_comp18.py. Dessin : ref_arbre.py. Objets achetables : ref_objets.py.

BR_LVL = [10, 20, 30, 45, 60, 80]
BR_COUT = [4, 6, 8, 10, 12, 14]
SKILL_LVL = [5, 20, 20, 45, 45, 70] + BR_LVL + BR_LVL
# 26/11/2026 : niveaux propres à un nœud (sinon celui de sa rangée). Ailes de l'Explorateur au niveau 25.
LVL_SPE = {("x", 9): 25}
def slvl(j, k):
    return LVL_SPE.get((j, k), SKILL_LVL[k - 1])
# noms des branches (gauche, droite) affichés sous l'arbre
BRANCHES = {
    "b": ("Récolte", "Combat"), "f": ("Récolte", "Terroir"), "m": ("Filons", "Galeries"), "c": ("Lame", "Arc"),
    "p": ("Prises", "Mer"), "e": ("Élevage", "Boucherie"), "n": ("Arcanes", "Savoir"), "x": ("Mobilité", "Aventure"),
    "t": ("Villages", "Commerce")}

# (nom, description, icône) : 6 à gauche puis 6 à droite, dans l'ordre des rangées
NOUVELLES = {
    "b": [
        ("Coupe nette", "Hache en main : tu coupes 50 % plus vite.", "item/stone_axe"),
        ("Ramasse-tout", "Hache en main : le bois, les pousses et les pommes à 12 blocs viennent à toi.", "item/bundle"),
        ("Abattage étendu", "L'abattage n'a plus de limite de taille (grands chênes noirs, jungle 2x2).", "item/golden_axe"),
        ("Sève", "Manger une pomme rend 3 cœurs et donne Absorption I pendant 1 min.", "item/apple"),
        ("Graine de forêt", "Débloque la Graine de forêt (onglet Outil, en Écus) : clic droit sur une pousse, l'arbre adulte apparaît.", "item/wheat_seeds"),
        ("Grande coupe", "Double coupe passe à 40 % et chaque bûche a 5 % de chance de donner 4 planches.", "item/diamond_axe"),
        ("Hache de guerre", "Hache en main : +2 dégâts et attaque plus rapide.", "item/iron_sword"),
        ("Bras de géant", "Hache en main : +1 bloc de portée pour casser et frapper.", "item/stick"),
        ("Écorce", "Hache en main : +2 points d'armure.", "item/iron_chestplate"),
        ("Tourbillon", "Accroupi, un coup de hache frappe tous les monstres à 3 blocs (recharge 6 s).", "item/wind_charge"),
        ("Cœur de chêne", "Hache en main : Régénération I.", "item/glistering_melon_slice"),
        ("Colosse", "+4 cœurs de vie maximum, en permanence.", "item/totem_of_undying")],
    "f": [
        ("Pied léger", "Sauter ou tomber sur la terre labourée ne la piétine plus.", "item/feather"),
        ("Engrais puissant", "Ta poudre d'os fait mûrir la culture visée d'un coup.", "item/bone_meal"),
        ("Terre fertile", "La terre labourée à 6 blocs de toi reste toujours humide.", "item/water_bucket"),
        ("Abondance", "10 % de chance de récolte triplée.", "item/golden_carrot"),
        ("Bombe d'engrais", "Débloque la Bombe d'engrais (onglet Outil, en Écus) : lancée, tout mûrit en 7x7.", "item/snowball"),
        ("Pluie bienfaisante", "Quand il pleut, tes cultures à 16 blocs avancent d'un stade chaque minute.", "item/wheat"),
        ("Faucheur", "Houe en main : +3 dégâts et balayage renforcé.", "item/iron_hoe"),
        ("Arrosoir", "Débloque l'Arrosoir (onglet Outil, en Écus) : clic droit, les cultures en 5x5 avancent d'un stade.", "item/milk_bucket"),
        ("Faux", "Houe en main, clic droit sur des cultures mûres : elles sont récoltées et replantées en 3x3.", "item/iron_hoe"),
        ("Régénération du terroir", "Régénération I quand tu marches dans tes champs.", "item/carrot"),
        ("Épouvantail", "Débloque l'Épouvantail (onglet Outil, en Écus) : posé, plus aucun monstre à 24 blocs.", "item/pumpkin_pie"),
        ("Grande faux", "La récolte au clic droit de la houe passe en 5x5.", "item/diamond_hoe")],
    "m": [
        ("Tri automatique", "Pioche en main : pierre, galets, deepslate, tuf, granite, diorite, andésite, netherrack et terre ne sont plus ramassés. Clic pour couper.", "item/paper"),
        ("Fortune bonus", "+1 charbon, redstone, lapis ou quartz par minerai cassé.", "item/redstone"),
        ("Gemmes", "Casser de la pierre : 0,5 % de chance d'émeraude, lapis ou quartz.", "item/emerald"),
        ("Dynamite", "Débloque la Dynamite (onglet Outil, en Écus) : lancée, elle creuse 5x5x5 sans toucher aux minerais et te rapporte tout.", "item/gunpowder"),
        ("Diamant brut", "Casser de la deepslate : 0,2 % de chance de diamant.", "item/diamond"),
        ("Cœur de diamant", "Les minerais donnent deux fois plus d'XP vanilla.", "item/experience_bottle"),
        ("Allumeur", "Dans le noir, une torche de ton inventaire se pose toute seule à tes pieds.", "item/glow_ink_sac"),
        ("Aimant", "Les objets et l'XP au sol à 8 blocs viennent à toi. Clic sur la compétence pour le couper.", "item/iron_ingot"),
        ("Lanterne", "Débloque la Lanterne (onglet Outil, en Écus) : en main secondaire, la lumière te suit.", "item/lantern"),
        ("Pioche large", "Accroupi, ta pioche creuse en 3x3 dans la direction visée.", "item/iron_pickaxe"),
        ("Lave apprivoisée", "Toucher la lave donne 15 s de Résistance au feu (recharge 2 min).", "item/lava_bucket"),
        ("Stature de pierre", "+4 d'armure, +2 de robustesse et moitié moins de recul.", "item/netherite_chestplate")],
    "c": [
        ("Coup critique", "Épée ou hache : 10 % de chance d'infliger 5 dégâts de plus.", "item/diamond_sword"),
        ("Saignement", "Tes coups font saigner : 1 cœur par seconde pendant 3 s.", "item/redstone"),
        ("Collectionneur", "Trophées passe à 8 % et marche aussi sur le squelette wither.", "item/bone"),
        ("Esquive", "Touché : 10 % de chance de récupérer aussitôt 2 cœurs, avec Vitesse II 2 s.", "item/rabbit_foot"),
        ("Rage", "+1 dégât par monstre tué depuis moins de 5 s (jusqu'à +5).", "item/blaze_powder"),
        ("Maître chasseur", "Coup critique passe à 20 %, et chaque critique fait saigner et rend 1 cœur.", "item/netherite_sword"),
        ("Récupérateur", "50 % de chance qu'une flèche tirée te soit rendue.", "item/arrow"),
        ("Œil de faucon", "Tes flèches font 25 % de dégâts en plus.", "item/spyglass"),
        ("Flèches perçantes", "Tes flèches traversent un monstre.", "item/spectral_arrow"),
        ("Piège à mâchoires", "Débloque le Piège (onglet Outil, en Écus) : posé, il bloque et blesse le premier monstre qui passe.", "item/iron_ingot"),
        ("Tir triple", "Chaque tir à l'arc lance trois flèches en éventail.", "item/bow"),
        ("Tueur de géants", "+5 dégâts sur les boss de métier, le Wither, le Dragon, le Warden et le gardien ancien.", "item/nether_star")],
    "p": [
        ("Prise triple", "5 % de chance de pêcher 2 poissons de plus.", "item/tropical_fish"),
        ("Marée", "Tuer un noyé : 10 % de chance d'une coquille de nautile.", "item/nautilus_shell"),
        ("Filet de pêche", "Débloque le Filet (onglet Outil, en Écus) : posé dans l'eau, il pêche seul toutes les 2 min, dans un coffre voisin.", "item/string"),
        ("Cœur de l'océan", "0,5 % de chance de pêcher un cœur de la mer.", "item/heart_of_the_sea"),
        ("Canne grappin", "Ramène ta canne accrochée au sol à plus de 4 blocs : tu es propulsé vers elle.", "item/fishing_rod"),
        ("Pêche miraculeuse", "1 % de chance par prise de gagner 5 cristaux de Pêcheur.", "item/prismarine_crystals"),
        ("Poumons d'acier", "Tu tiens 4 fois plus longtemps sans respirer.", "item/glass_bottle"),
        ("Profondeur", "Tu nages beaucoup plus vite (Agilité aquatique).", "item/turtle_scute"),
        ("Mineur sous-marin", "Sous l'eau, tu mines aussi vite qu'à l'air libre.", "item/prismarine_shard"),
        ("Requin", "Dans l'eau : +3 dégâts.", "item/cod"),
        ("Gardien des mers", "Résistance II quand un gardien ou un noyé est à 16 blocs.", "item/nautilus_shell"),
        ("Tempête", "Sous la pluie : Force I et Vitesse I.", "item/trident")],
    "e": [
        ("Tonte en zone", "Tondre un mouton tond aussi tous les moutons à 4 blocs.", "item/shears"),
        ("Dresseur", "Accroupi 3 s près d'un loup, chat, perroquet, cheval, âne ou lama sauvage, sa nourriture en main : il est à toi.", "item/lead"),
        ("Écurie", "Les poulains nés près de toi ont les meilleures stats (vie, vitesse, saut).", "item/saddle"),
        ("Mangeoire", "Débloque la Mangeoire (onglet Outil, en Écus) : posée, les animaux autour se reproduisent toutes les 5 min.", "item/wheat"),
        ("Grand cheptel", "+25 % d'XP d'Éleveur sur les naissances.", "item/egg"),
        ("Maître des bêtes", "Loups, ours polaires, abeilles, pandas et lamas ne t'attaquent plus.", "item/name_tag"),
        ("Boucher", "+1 viande par animal tué.", "item/beef"),
        ("Viande cuite", "La viande qui tombe près de toi est déjà cuite.", "item/cooked_beef"),
        ("Lasso", "Accroupi + clic droit avec la houlette en visant un animal : il est capturé dans un œuf.", "item/lead"),
        ("Sifflet", "Débloque le Sifflet (onglet Outil, en Écus) : clic droit, ta dernière monture te rejoint.", "item/goat_horn"),
        ("Abattoir", "10 % de chance de butin triplé sur les animaux.", "item/porkchop"),
        ("Gardien du troupeau", "Les animaux à 16 blocs de toi reçoivent Résistance IV et Régénération : les monstres ne les tuent plus.", "item/gold_ingot")],
    "n": [
        ("Lapis économe", "50 % de chance que le lapis d'un enchantement te soit rendu.", "item/lapis_lazuli"),
        ("Parchemin", "Accroupi + clic droit avec le grimoire : les enchantements de ta main secondaire passent sur un livre.", "item/paper"),
        ("Forge arcanique I", "Onglet Outil : monte les enchantements de l'objet en main jusqu'à 1 niveau au-dessus du maximum du jeu.", "item/enchanted_book"),
        ("Réserve arcanique", "Au-dessus de 30 niveaux d'XP : Absorption I ; au-dessus de 50 : Absorption II.", "item/golden_apple"),
        ("Forge arcanique II", "La Forge arcanique monte jusqu'à 2 niveaux au-dessus du maximum.", "item/writable_book"),
        ("Forge arcanique III", "La Forge arcanique monte jusqu'à 3 niveaux au-dessus du maximum (Efficacité VIII, Tranchant VIII...).", "item/knowledge_book"),
        ("Orbes généreuses", "15 % des orbes d'XP que tu ramasses valent double.", "item/experience_bottle"),
        ("Étincelle", "Casser ou récolter : 2 % de chance d'une orbe d'XP en plus.", "item/glowstone_dust"),
        ("Enclume douce", "À l'enclume, la moitié des niveaux dépensés te sont rendus.", "item/iron_ingot"),
        ("Orbes riches", "35 % des orbes d'XP que tu ramasses valent double.", "item/ender_eye"),
        ("Étincelle vive", "Étincelle passe à 5 % avec des orbes plus grosses.", "item/blaze_rod"),
        ("Garde-niveaux", "À ta mort, tu gardes la moitié de tes niveaux d'XP.", "item/totem_of_undying")],
    "x": [
        ("Endurance", "Courir ne te donne plus faim.", "item/sugar"),
        ("Saut de géant", "Tu sautes plus haut et la chute fait mal 2 blocs plus tard.", "item/rabbit_foot"),
        ("Ailes", "Tu reçois des élytres incassables (onglet Outil pour les récupérer si tu les perds).", "item/elytra"),
        ("Grimpeur", "Avance contre un mur : tu le grimpes.", "item/string"),
        ("Propulseur", "En vol avec des élytres : une fusée offerte toutes les 15 s (3 au plus sur toi).", "item/firework_rocket"),
        ("Vent arrière", "Après 5 s de course : Vitesse III.", "item/wind_charge"),
        ("Pilleur", "Les coffres de structure que tu ouvres en premier ont 30 % de chance d'un second butin.", "item/gold_nugget"),
        ("Œil clair", "Insensible à la cécité et à l'obscurité du Warden.", "item/ender_eye"),
        ("Tente", "Débloque la Tente (onglet Outil, en Écus) : posée, elle devient ton point de réapparition.", "item/white_bundle"),
        ("Cartographe", "25 % de chance d'une carte au trésor dans les coffres de structure que tu ouvres.", "item/map"),
        ("Sac étanche", "À ta mort, tes objets restent 15 min au sol, insensibles à la lave et au feu.", "item/leather"),
        ("Butin légendaire", "5 % de chance d'un totem, d'une pomme enchantée ou d'un gabarit dans un coffre de structure.", "item/golden_apple")],
    "t": [
        ("Bonne réputation", "Les villageois autour de toi oublient tes mauvaises actions.", "item/emerald"),
        ("Échanges infinis", "Les villageois autour de toi se réapprovisionnent tout de suite.", "item/bundle"),
        ("Prix gelés", "Les prix des villageois ne montent plus à force d'acheter.", "item/gold_ingot"),
        ("Commission", "Chaque échange avec un villageois te rapporte 5 Écus.", "item/gold_nugget"),
        ("Livres choisis", "Les livres des bibliothécaires autour de toi passent au niveau maximum.", "item/enchanted_book"),
        ("Contrebandier", "5 % de chance qu'un achat au marché du Commerce te soit remboursé.", "item/ink_sac"),
        ("Vendeur", "+3 % sur tes ventes au marché.", "item/emerald"),
        ("Acheteur malin", "−5 % sur tes achats au marché.", "item/gold_nugget"),
        ("Taxe réduite", "Hôtel des ventes : 2 % de taxe au lieu de 5.", "item/paper"),
        ("Vendeur aguerri", "+6 % sur tes ventes au marché (au lieu de 3).", "item/emerald"),
        ("Banquier", "Ton épargne rapporte 1 % de plus par semaine.", "item/gold_ingot"),
        ("Grossiste", "+10 % sur tes ventes au marché (au lieu de 6).", "item/diamond")],
}

_nouveau = {}
for j, v in SKILLS.items():
    base = [(n, c, ([k - 1] if k > 1 else []), d) for k, (n, c, r, d) in enumerate(v, 1)]   # tronc en chaîne
    if j in NOUVELLES:
        for b in range(2):
            for i, (n, d, ic) in enumerate(NOUVELLES[j][6 * b:6 * b + 6]):
                k = 7 + 6 * b + i
                base.append((n, BR_COUT[i], [1] if i == 0 else [k - 1], d))
    _nouveau[j] = base
SKILLS = _nouveau
NB_SK = {j: len(v) for j, v in SKILLS.items()}


def TSK(d, k):
    """Déclencheur d'achat : 100 + 10 x idx + k pour le tronc (1000 + k pour le Bâtisseur), 3000 + 20 x idx + k pour les branches."""
    if k > 6:
        return 3000 + 20 * d["idx"] + k
    return 100 + 10 * d["idx"] + k if d["idx"] < 10 else 1000 + k


# ---------------------------------------------------------------- effets « au gain » : crochets sur les sources d'XP
# (compétence, chance « chance_N » sur 100 ou « pm_N » sur 1000, commande) ; lancés une fois par relevé des statistiques.
def _src(j, prefixe):
    return [s for s in jobs[j]["src"] if s[3].startswith(prefixe)]


PLANCHE = lambda l: (l[:-4] if l.endswith("_log") else l[:-5]) + "_planks"
for s in _src("b", "b.mi."):
    log = s[3][5:]
    base = log.replace("stripped_", "")
    for suf in ("_wood", "_hyphae"):
        if base.endswith(suf):
            base = base[: -len(suf)] + ("_log" if suf == "_wood" else "_stem")
    s[4].extend([("b12", "chance_25", f"give @s minecraft:{log} 1"), ("b12", "chance_05", f"give @s minecraft:{PLANCHE(base)} 4")])
for s in _src("f", "f.pu.") + _src("f", "f.mi."):
    c = s[3][5:]
    drop = c if s[3].startswith("f.pu.") else CROP_BLOCKS[c][2]
    s[4].append(("f10", "chance_10", f"give @s minecraft:{drop} 2"))
_XP_ORE = {"coal": 2, "copper": 1, "iron": 1, "gold": 2, "redstone": 3, "lapis": 4, "diamond": 5, "emerald": 5,
           "nether_gold": 1, "nether_quartz": 3, "ancient_debris": 2}
for s in _src("m", "m.mi."):
    b = s[3][5:]
    if b in ORES:
        base = b.replace("deepslate_", "").replace("_ore", "")
        if base in ("coal", "redstone", "lapis", "nether_quartz"):
            s[4].append(("m8", None, "give @s minecraft:" + ORE_DROP[base].split()[0] + " 1"))
        s[4].append(("m12", None, f"xp add @s {_XP_ORE.get(base, 1)} points"))
    elif b in STONES:
        s[4].append(("m9", "pm_5", "function metiers:comp/m_gemme"))
        if b == "deepslate":
            s[4].append(("m11", "pm_2", "give @s minecraft:diamond 1"))
# Chasseur : Collectionneur ; Éleveur : Boucher, Abattoir ; Pêcheur : Marée
_TETE = {"zombie": "zombie_head", "skeleton": "skeleton_skull", "creeper": "creeper_head", "piglin": "piglin_head"}
_VIANDE = {"cow": "beef", "mooshroom": "beef", "pig": "porkchop", "sheep": "mutton", "chicken": "chicken", "rabbit": "rabbit", "goat": None}
for s in _src("c", "c.k."):
    mob = s[3][4:]
    if mob in _TETE:
        s[4].append(("c9", "chance_05", f"give @s minecraft:{_TETE[mob]} 1"))
    if mob == "wither_skeleton":
        s[4].append(("c9", "chance_05", "give @s minecraft:wither_skeleton_skull 1"))
    if mob == "drowned":
        s[4].append(("p8", "chance_10", "give @s minecraft:nautilus_shell 1"))
    if mob in _VIANDE:
        if _VIANDE[mob]:
            s[4].append(("e13", None, f"give @s minecraft:{_VIANDE[mob]} 1"))
        s[4].append(("e17", "chance_10", f"loot give @s loot minecraft:entities/{mob}"))
        s[4].append(("e17", "chance_10", f"loot give @s loot minecraft:entities/{mob}"))
jobs["c"]["src"].append(("minecraft.used:minecraft.bow", 0, 1, "c.bow2", [("c13", "chance_50", "give @s minecraft:arrow 1")]))
jobs["c"]["src"].append(("minecraft.used:minecraft.crossbow", 0, 1, "c.xbow", [("c13", "chance_50", "give @s minecraft:arrow 1")]))
for s in _src("p", "p.fish"):
    s[4].extend([("p7", "chance_05", "loot give @s loot minecraft:gameplay/fishing/fish"),
             ("p7", "chance_05", "loot give @s loot minecraft:gameplay/fishing/fish"),
             ("p10", "pm_5", "give @s minecraft:heart_of_the_sea 1"),
             ("p12", "chance_01", "function metiers:comp/p_miracle")])
for s in _src("e", "e.bred"):
    s[4].extend([("e11", None, "scoreboard players add @s m.e_raw 4"), ("e9", None, "function metiers:comp/e_ecurie")])
# Enchanteur : Étincelle sur tout ce qui se casse ou se récolte
for j_, pre in (("b", "b.mi."), ("m", "m.mi."), ("f", "f.mi."), ("f", "f.pu.")):
    for s in _src(j_, pre):
        s[4].extend([("n14", "chance_02", "summon minecraft:experience_orb ~ ~1 ~ {Value:3s}"),
                 ("n17", "chance_03", "summon minecraft:experience_orb ~ ~1 ~ {Value:7s}")])

ALL_STATS = [s for j_ in jobs.values() for s in j_["src"]]   # 26.0 : sources ajoutées ci-dessus

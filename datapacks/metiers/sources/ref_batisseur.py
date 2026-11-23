# -*- coding: utf-8 -*-
# Bâtisseur (10e métier, lettre k) : effets des compétences, capacité de prestige, kit de chantier, textures.
# Exécuté à la fin de datapack.py (mêmes variables : w, add_lines, F, NS, tr, ROOT...).
import shutil as _sh, zipfile as _zf

add_lines(F + "refonte/load.mcfunction", ["scoreboard objectives add m.kit dummy"])

# ---------------------------------------------------------------- compétences et prestige (appelés avec le reste des bonus)
add_lines(F + "bonus.mcfunction", [
    "# Bâtisseur",
    f"attribute @s minecraft:block_interaction_range modifier remove {NS}:k1",
    f"attribute @s minecraft:block_interaction_range modifier remove {NS}:k5",
    f"attribute @s minecraft:block_interaction_range modifier remove {NS}:pk",
    f"attribute @s minecraft:fall_damage_multiplier modifier remove {NS}:k2",
    f"execute if entity @s[tag=metiers.sk.k1] run attribute @s minecraft:block_interaction_range modifier add {NS}:k1 1 add_value",
    f"execute if entity @s[tag=metiers.sk.k5] run attribute @s minecraft:block_interaction_range modifier add {NS}:k5 2 add_value",
    f"execute if entity @s[tag=metiers.sk.k2] run attribute @s minecraft:fall_damage_multiplier modifier add {NS}:k2 -0.5 add_multiplied_base",
    f"execute if entity @s[tag=metiers.sk.k3] if predicate {NS}:accroupi if block ~ ~-1 ~ #minecraft:air if block ~ ~-2 ~ #minecraft:air run effect give @s minecraft:slow_falling 1 0 true",
    "execute if entity @s[tag=metiers.sk.k4,tag=!metiers.sk.k6] run effect give @s minecraft:haste 2 0 true",
    "execute if entity @s[tag=metiers.sk.k6] run effect give @s minecraft:haste 2 1 true",
    "execute if entity @s[tag=metiers.sk.k6] run effect give @s minecraft:resistance 2 0 true",
    # Architecte (prestige) : +1, +2, +3 de portée ; Résistance I à 3 étoiles ; Célérité II à 5
    f"execute if entity @s[tag=metiers.sk.pk5] run attribute @s minecraft:block_interaction_range modifier add {NS}:pk 3 add_value",
    f"execute if entity @s[tag=metiers.sk.pk3,tag=!metiers.sk.pk5] run attribute @s minecraft:block_interaction_range modifier add {NS}:pk 2 add_value",
    f"execute if entity @s[tag=metiers.sk.pk1,tag=!metiers.sk.pk3] run attribute @s minecraft:block_interaction_range modifier add {NS}:pk 1 add_value",
    "execute if entity @s[tag=metiers.sk.pk3] run effect give @s minecraft:resistance 2 0 true",
    "execute if entity @s[tag=metiers.sk.pk5] run effect give @s minecraft:haste 2 1 true",
    "execute if score @s m.kit matches 1.. run scoreboard players remove @s m.kit 1"])

# ---------------------------------------------------------------- kit de chantier (614)
w(F + "k/kit.mcfunction", "\n".join([
    f"execute unless score @s m.k_lvl matches 20.. unless score @s m.k_pr matches 1.. run return run {tr('Le kit de chantier se débloque au niveau 20 de Bâtisseur.', 'red')}",
    f"execute if score @s m.kit matches 1.. run return run {tr('Kit de chantier déjà pris : reviens dans un jour de jeu (20 min).', 'red')}",
    "scoreboard players set @s m.kit 2400",
    "give @s minecraft:scaffolding 32", "give @s minecraft:ladder 16", "give @s minecraft:lantern 8",
    "playsound minecraft:block.anvil.use master @s ~ ~ ~ 0.6 1.4",
    tr("Kit de chantier : 32 échafaudages, 16 échelles, 8 lanternes. Bon chantier !", "green")]))

# ---------------------------------------------------------------- resource pack : truelle, icônes, cristal
# Les textures sont pré-rendues (textures.py, forme "trowel") dans sources/textures_batisseur/ : pas besoin de numpy ici.
# build/metiers_rp ne contient que des fichiers AJOUTÉS ou REMPLACÉS dans assets/metiers (fusion_rp.py ne retire
# jamais le dossier de Métiers) : la police icones.json est relue dans le zip commun et complétée.
_TB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures_batisseur")
_RP = os.path.join(ROOT, "..", "metiers_rp")
if os.path.exists(_RP):
    _sh.rmtree(_RP)
_A = os.path.join(_RP, "assets", "metiers")
for _d in ("items", "models/item", "textures/item", "textures/font", "font"):
    os.makedirs(os.path.join(_A, _d), exist_ok=True)
for _k in range(11):
    _n = f"k_{_k}"
    json.dump({"model": {"type": "minecraft:model", "model": f"metiers:item/{_n}"}}, open(os.path.join(_A, "items", _n + ".json"), "w"))
    json.dump({"parent": "minecraft:item/handheld", "textures": {"layer0": f"metiers:item/{_n}"}},
              open(os.path.join(_A, "models/item", _n + ".json"), "w"))
    _sh.copy(os.path.join(_TB, _n + ".png"), os.path.join(_A, "textures/item", _n + ".png"))
    if os.path.exists(os.path.join(_TB, _n + ".png.mcmeta")):
        _sh.copy(os.path.join(_TB, _n + ".png.mcmeta"), os.path.join(_A, "textures/item", _n + ".png.mcmeta"))
for _n in ("metier_k", "cristal_k"):
    _sh.copy(os.path.join(_TB, _n + ".png"), os.path.join(_A, "textures/font", _n + ".png"))
_zp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "metiers_resourcepack.zip")
_font = json.loads(_zf.ZipFile(_zp).read("assets/metiers/font/icones.json"))
_neuf = {GLY["metier_k"], GLY["cristal_k"], GLY["grand_metier_k"]}
_font["providers"] = [p for p in _font["providers"] if not (set("".join(p.get("chars", []))) & _neuf)] + [
    {"type": "bitmap", "file": "metiers:font/metier_k.png", "height": 9, "ascent": 8, "chars": [GLY["metier_k"]]},
    {"type": "bitmap", "file": "metiers:font/cristal_k.png", "height": 9, "ascent": 8, "chars": [GLY["cristal_k"]]},
    {"type": "bitmap", "file": "metiers:font/metier_k.png", "height": 16, "ascent": 12, "chars": [GLY["grand_metier_k"]]}]
json.dump(_font, open(os.path.join(_A, "font", "icones.json"), "w", encoding="utf-8"), ensure_ascii=False)

w(F + "version.mcfunction", 'tellraw @s {"text":"[Métiers] Version 25 : 10e métier Bâtisseur, quêtes, guildes, synergies, boss plus durs, barème illustré, menu G commun aux trois packs","color":"gold"}')

# ---------------------------------------------------------------- 25.1 : un id d'objet invalide (« chain », renommé
# « iron_chain » en 1.21.9) faisait refuser tout load.mcfunction par le jeu : les scores du Bâtisseur n'existaient pas,
# niveau 0, et chaque test de niveau échouait en silence, ce qui laissait acheter toutes les compétences.
# Migration unique : on retire ce qui a pu être pris ainsi (personne n'a pu gagner de vrai niveau de Bâtisseur avant).
add_lines(F + "joueur.mcfunction", [f'execute unless entity @s[tag=metiers.v25] run function {NS}:k/migration25'])
w(F + "k/migration25.mcfunction", "\n".join(
    ["tag @s add metiers.v25"] + [f"tag @s remove metiers.sk.k{n}" for n in range(1, 7)] +
    [f"advancement revoke @s only {NS}:k/competence_{n}" for n in range(1, 7)] +
    [f"function {NS}:k/init", "clear @s *[minecraft:custom_data~{metiers_outil:\"k\"}]"] +
    # le même bug gonflait le score total (calcul fait avec un score absent) : Armure des Guildes Céleste pour tout le
    # monde. On reprend l'armure (inventaire et coffre de l'Ender), puis on la redonne au vrai palier.
    [f"execute if items entity @s enderchest.{i} *[minecraft:custom_data~{{metiers_armure:1b}}] run item replace entity @s enderchest.{i} with minecraft:air" for i in range(27)] +
    ["scoreboard players set @s m.arm 0", "tag @s add metiers.avait_armure", f"function {NS}:classement/maj",
     "execute if score @s m.arm matches 0 run clear @s *[minecraft:custom_data~{metiers_armure:1b}]",
     tr("Correctif 25.1 : ton Armure des Guildes est revenue à ton vrai palier (un bug du Bâtisseur gonflait le score).", "yellow")]))

# Garde-fou : tout critère de statistique sur un OBJET (used, crafted, picked_up, dropped) doit exister en 26.1,
# sinon le jeu refuse la fonction entière qui le contient (liste officielle tirée de minecraft-data, dans Commerce).
_dn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "commerce", "sources", "donnees_26.1.json")
if os.path.exists(_dn):
    import re as _re
    _it = json.load(open(_dn, encoding="utf-8"))["items"]
    _ids = {i.replace("minecraft:", "") for i in (_it if isinstance(_it, list) else _it.keys())}
    _bad = set()
    for _dp, _, _fs in os.walk(ROOT):
        for _fn in _fs:
            if _fn.endswith(".mcfunction"):
                for _m in _re.finditer(r"minecraft\.(?:used|crafted|picked_up|dropped):minecraft\.([a-z0-9_]+)", open(os.path.join(_dp, _fn), encoding="utf-8").read()):
                    if _m.group(1) not in _ids:
                        _bad.add(_m.group(1))
    assert not _bad, f"objets inconnus en 26.1 dans des critères de statistiques : {sorted(_bad)}"


# ---------------------------------------------------------------- 25.2 : tout bloc posé rapporte un peu, bonus des blocs du shop
# Progrès invisible « placed_block » sans condition : il se déclenche à chaque bloc posé, sa récompense est relancée.
#  - 1 point (1/20 d'XP) par bloc, 40 points par minute au plus (poser puis casser de la terre ne mène pas loin) ;
#  - bloc acheté au Commerce (crédit c.kb tenu par Commerce) : +2 XP, 256 blocs par jour de défis au plus.
wj(f"data/{NS}/advancement/k/pose.json", {"criteria": {"pose": {"trigger": "minecraft:placed_block"}},
                                          "rewards": {"function": f"{NS}:k/pose"}})
add_lines(F + "refonte/load.mcfunction", ["scoreboard objectives add m.kcap dummy", "scoreboard objectives add m.kbj dummy",
                                          f"schedule function {NS}:k/minute 60s replace"])
w(F + "k/minute.mcfunction", "\n".join(["scoreboard players reset * m.kcap", f"schedule function {NS}:k/minute 60s replace"]))
w(F + "k/pose.mcfunction", "\n".join([
    f"advancement revoke @s only {NS}:k/pose",
    "scoreboard players add @s m.kcap 0", "scoreboard players add @s m.kbj 0",
    "execute if score @s m.kcap matches ..39 run scoreboard players add @s m.k_raw 1",
    "execute if score @s m.kcap matches ..39 run scoreboard players add @s m.kcap 1",
    f"execute if score @s c.kb matches 1.. if score @s m.kbj matches ..255 run function {NS}:k/pose_shop"]))
w(F + "k/pose_shop.mcfunction", "\n".join([
    "scoreboard players remove @s c.kb 1", "scoreboard players add @s m.kbj 1", "scoreboard players add @s m.k_raw 40",
    "execute if score @s m.kbj matches 256 run " + tr("Bonus des blocs du shop : 256 blocs aujourd’hui, c’est le maximum. Il revient avec les défis de demain.", "yellow")]))
add_lines(F + "defis/nouveaux.mcfunction", ["scoreboard players reset * m.kbj"])

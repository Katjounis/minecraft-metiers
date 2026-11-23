# -*- coding: utf-8 -*-
# Coffres privés : un panneau « [Privé] » posé sur un coffre, un coffre piégé ou un tonneau le réserve à celui qui a
# posé le panneau. Exécuté par datapack.py (partage w, wj, F, NS, say, L, T, PREFIX).
#
#   - détection : un joueur qui vient de poser un panneau est surveillé 30 s ; on vise depuis ses yeux le panneau
#     qu'il regarde, on lit son texte, on protège le bloc auquel il est accroché.
#   - verrou vanilla (composant « lock ») : le conteneur ne s'ouvre que si le propriétaire est à moins de 6 blocs
#     et qu'aucun autre joueur n'est à moins de 8 blocs. Sinon il est verrouillé pour tout le monde.
#   - reconstruction : si le coffre ou le panneau disparaît (cassé, explosion) sans que ce soit le propriétaire,
#     il est remis avec son contenu (photo du contenu prise chaque seconde) et les objets lâchés sont retirés.
#   - entonnoirs : un entonnoir sous un conteneur protégé est mis en pause, un wagonnet à entonnoir désactivé.
#   - le propriétaire retire la protection en cassant le panneau (ou le coffre).
SIGNS = ['acacia', 'bamboo', 'birch', 'cherry', 'crimson', 'dark_oak', 'jungle', 'mangrove', 'oak', 'pale_oak', 'spruce', 'warped']
SIGN_OBJ = [(f"c.us{k}", f"{w_}_sign") for k, w_ in enumerate(SIGNS)] + [(f"c.uh{k}", f"{w_}_hanging_sign") for k, w_ in enumerate(SIGNS)]
P = F + "prive/"
MOTS = ["[Privé]", "[Prive]", "[privé]", "[prive]", "[PRIVÉ]", "[PRIVE]"]
VERROU = '{lock:{items:"minecraft:structure_void",components:{"minecraft:custom_data":{commerce_verrou:1b}}}}'

wj(f"data/{NS}/tags/block/protegeable.json", {"values": ["minecraft:chest", "minecraft:trapped_chest", "minecraft:barrel"]})

# ---------------------------------------------------------------- chargement
LDP = [f"scoreboard objectives add {o} minecraft.used:minecraft.{it}" for o, it in SIGN_OBJ]
LDP += [f"scoreboard objectives add {o} dummy" for o in ("c.psign", "c.lk", "c.grp", "c.st", "c.pown", "c.gg")]
LDP += ["scoreboard players add #gid c.g 0", "scoreboard players add #pt c.g 0"]
w(P + "load.mcfunction", LDP)

# ---------------------------------------------------------------- toutes les 2 ticks
w(P + "tick.mcfunction", [
    "scoreboard players set #pt c.g 0",
    f"execute as @e[type=minecraft:marker,tag=commerce.prive_c] at @s run function {NS}:prive/conteneur",
    f"execute as @e[type=minecraft:marker,tag=commerce.prive_s] at @s run function {NS}:prive/panneau_garde"])

# ---------------------------------------------------------------- chaque seconde (joueurs et photos)
SEC = []
for o, _ in SIGN_OBJ:
    SEC += [f"execute if score @s {o} matches 1.. run scoreboard players set @s c.psign 30", f"scoreboard players set @s {o} 0"]
SEC += [f"execute if score @s c.psign matches 1.. at @s anchored eyes positioned ^ ^ ^ run function {NS}:prive/rayon_debut",
        "execute if score @s c.psign matches 1.. run scoreboard players remove @s c.psign 1"]
w(P + "joueur.mcfunction", SEC)
w(P + "seconde.mcfunction", [
    f"execute as @a at @s run function {NS}:prive/joueur",
    f"execute as @e[type=minecraft:marker,tag=commerce.prive_c] at @s run function {NS}:prive/photo",
    f"execute as @e[type=minecraft:marker,tag=commerce.prive_s] at @s run function {NS}:prive/photo_panneau"])

# ---------------------------------------------------------------- visée du panneau (6 blocs, pas de 0,2)
w(P + "rayon_debut.mcfunction", ["scoreboard players set #ray c.t 30", f"function {NS}:prive/rayon"])
w(P + "rayon.mcfunction", [
    f"execute if block ~ ~ ~ #minecraft:all_signs align xyz run return run function {NS}:prive/panneau",
    "scoreboard players remove #ray c.t 1",
    f"execute if score #ray c.t matches 1.. positioned ^ ^ ^0.2 run function {NS}:prive/rayon"])

# texte « [Privé] » sur une ligne de la face avant ou arrière (texte simple ou composant)
TXT = []
for m in MOTS:
    for face in ("front_text", "back_text"):
        TXT.append(f'execute if block ~ ~ ~ #minecraft:all_signs{{{face}:{{messages:["{m}"]}}}} run scoreboard players set #pv c.t 1')
        TXT.append(f'execute if block ~ ~ ~ #minecraft:all_signs{{{face}:{{messages:[{{text:"{m}"}}]}}}} run scoreboard players set #pv c.t 1')
for m in ["[Guilde]", "[guilde]", "[GUILDE]"]:    # coffre de guilde : ouvert à tous les membres (guilde de Métiers)
    for face in ("front_text", "back_text"):
        TXT.append(f'execute if block ~ ~ ~ #minecraft:all_signs{{{face}:{{messages:["{m}"]}}}} run scoreboard players set #pv c.t 3')
        TXT.append(f'execute if block ~ ~ ~ #minecraft:all_signs{{{face}:{{messages:[{{text:"{m}"}}]}}}} run scoreboard players set #pv c.t 3')
for m in ["[Vente]", "[vente]", "[VENTE]"]:      # magasin : même protection, puis le prix (boutiques.py)
    for face in ("front_text", "back_text"):
        TXT.append(f'execute if block ~ ~ ~ #minecraft:all_signs{{{face}:{{messages:["{m}"]}}}} run scoreboard players set #pv c.t 2')
        TXT.append(f'execute if block ~ ~ ~ #minecraft:all_signs{{{face}:{{messages:[{{text:"{m}"}}]}}}} run scoreboard players set #pv c.t 2')
w(P + "panneau.mcfunction", [
    "scoreboard players set #pv c.t 0"] + TXT + [
    "execute if score #pv c.t matches 0 run return 0",
    "execute if entity @e[type=minecraft:marker,tag=commerce.prive_s,distance=..0.9,limit=1] run return 0",
    "scoreboard players set #cible c.t 0",
    f"execute if block ~ ~ ~ #minecraft:wall_signs[facing=north] positioned ~ ~ ~1 if block ~ ~ ~ #{NS}:protegeable run function {NS}:prive/proteger",
    f"execute if score #cible c.t matches 0 if block ~ ~ ~ #minecraft:wall_signs[facing=south] positioned ~ ~ ~-1 if block ~ ~ ~ #{NS}:protegeable run function {NS}:prive/proteger",
    f"execute if score #cible c.t matches 0 if block ~ ~ ~ #minecraft:wall_signs[facing=east] positioned ~-1 ~ ~ if block ~ ~ ~ #{NS}:protegeable run function {NS}:prive/proteger",
    f"execute if score #cible c.t matches 0 if block ~ ~ ~ #minecraft:wall_signs[facing=west] positioned ~1 ~ ~ if block ~ ~ ~ #{NS}:protegeable run function {NS}:prive/proteger",
    f"execute if score #cible c.t matches 0 if block ~ ~ ~ #minecraft:standing_signs positioned ~ ~-1 ~ if block ~ ~ ~ #{NS}:protegeable run function {NS}:prive/proteger",
    f"execute if score #cible c.t matches 0 if block ~ ~ ~ #minecraft:ceiling_hanging_signs positioned ~ ~1 ~ if block ~ ~ ~ #{NS}:protegeable run function {NS}:prive/proteger",
    "execute if score #cible c.t matches 0 run return 0",
    # le panneau : marqueur de garde, cire (plus modifiable), photo
    'summon minecraft:marker ~0.5 ~0.5 ~0.5 {Tags:["commerce.prive","commerce.prive_s","commerce.pnew"]}',
    "scoreboard players operation @e[type=minecraft:marker,tag=commerce.pnew] c.own = @s m.id",
    "scoreboard players operation @e[type=minecraft:marker,tag=commerce.pnew] c.grp = #gid c.g",
    f"execute as @e[type=minecraft:marker,tag=commerce.pnew] at @s run function {NS}:prive/photo_panneau",
    "tag @e[type=minecraft:marker,tag=commerce.pnew] remove commerce.pnew",
    "data merge block ~ ~ ~ {is_waxed:1b}",
    "scoreboard players set @s c.psign 0",
    f"execute if score #pv c.t matches 2 run function {NS}:boutique/creer",
    f"execute if score #pv c.t matches 3 run function {NS}:prive/guilde",
    "playsound minecraft:block.iron_door.close master @s ~ ~ ~ 1 1.2",
    "particle minecraft:wax_on ~0.5 ~0.5 ~0.5 0.3 0.3 0.3 0 12"])

# ---------------------------------------------------------------- protéger un conteneur (position = bloc, exécutant = joueur)
w(P + "proteger.mcfunction", [
    "scoreboard players set #cible c.t 1",
    f"execute positioned ~0.5 ~0.5 ~0.5 if entity @e[type=minecraft:marker,tag=commerce.prive_c,distance=..0.4] run return run function {NS}:prive/deja",
    "scoreboard players add #gid c.g 1",
    f"function {NS}:prive/creer",
    # coffre double : on protège aussi l'autre moitié
    f"execute if block ~ ~ ~ #{NS}:protegeable[type=left] run function {NS}:prive/moitie",
    f"execute if block ~ ~ ~ #{NS}:protegeable[type=right] run function {NS}:prive/moitie",
    say("Coffre privé : toi seul peux l’ouvrir (et seulement si personne d’autre n’est à moins de 8 blocs). Casse le panneau pour retirer la protection.", "green")])
w(P + "deja.mcfunction", [
    "scoreboard players set #cible c.t 0",
    say("Ce coffre est déjà protégé.", "red")])
w(P + "creer.mcfunction", [
    'summon minecraft:marker ~0.5 ~0.5 ~0.5 {Tags:["commerce.prive","commerce.prive_c","commerce.pnew"]}',
    "scoreboard players operation @e[type=minecraft:marker,tag=commerce.pnew] c.own = @s m.id",
    "scoreboard players operation @e[type=minecraft:marker,tag=commerce.pnew] c.grp = #gid c.g",
    "scoreboard players set @e[type=minecraft:marker,tag=commerce.pnew] c.lk 0",
    f"execute as @e[type=minecraft:marker,tag=commerce.pnew] at @s run function {NS}:prive/photo",
    f"execute as @e[type=minecraft:marker,tag=commerce.pnew] at @s run function {NS}:prive/verrouiller",
    "tag @e[type=minecraft:marker,tag=commerce.pnew] remove commerce.pnew"])
# autre moitié d'un coffre double : left -> sens horaire de facing, right -> sens antihoraire
CW = {"north": "east", "east": "south", "south": "west", "west": "north"}
CCW = {v: k for k, v in CW.items()}
OFF = {"north": "~ ~ ~-1", "south": "~ ~ ~1", "east": "~1 ~ ~", "west": "~-1 ~ ~"}
MO = []
for f_ in CW:
    for typ, d in (("left", CW[f_]), ("right", CCW[f_])):
        MO.append(f"execute if block ~ ~ ~ #{NS}:protegeable[facing={f_},type={typ}] positioned {OFF[d]} "
                  f"if block ~ ~ ~ #{NS}:protegeable positioned ~0.5 ~0.5 ~0.5 unless entity @e[type=minecraft:marker,tag=commerce.prive_c,distance=..0.4] "
                  f"positioned ~-0.5 ~-0.5 ~-0.5 run function {NS}:prive/creer_moitie")
w(P + "moitie.mcfunction", MO)
# la moitié reprend le propriétaire et le groupe du marqueur exécutant (ou du joueur à la création)
w(P + "creer_moitie.mcfunction", [
    'summon minecraft:marker ~0.5 ~0.5 ~0.5 {Tags:["commerce.prive","commerce.prive_c","commerce.pnew"]}',
    "execute if entity @s[type=minecraft:player] run scoreboard players operation @e[type=minecraft:marker,tag=commerce.pnew] c.own = @s m.id",
    "execute if entity @s[type=minecraft:marker] run scoreboard players operation @e[type=minecraft:marker,tag=commerce.pnew] c.own = @s c.own",
    "execute if entity @s[type=minecraft:player] run scoreboard players operation @e[type=minecraft:marker,tag=commerce.pnew] c.grp = #gid c.g",
    "execute if entity @s[type=minecraft:marker] run scoreboard players operation @e[type=minecraft:marker,tag=commerce.pnew] c.grp = @s c.grp",
    "scoreboard players set @e[type=minecraft:marker,tag=commerce.pnew] c.lk 0",
    f"execute as @e[type=minecraft:marker,tag=commerce.pnew] at @s run function {NS}:prive/photo",
    f"execute as @e[type=minecraft:marker,tag=commerce.pnew] at @s run function {NS}:prive/verrouiller",
    "tag @e[type=minecraft:marker,tag=commerce.pnew] remove commerce.pnew"])

w(P + "guilde.mcfunction", [
    "execute unless score @s m.gid matches 1.. run return run " + say("Tu n’as pas de guilde : ce coffre reste privé (menu Métiers, Guilde).", "yellow"),
    "scoreboard players operation #g c.t = @s m.gid",
    "execute as @e[type=minecraft:marker,tag=commerce.prive] if score @s c.grp = #gid c.g run scoreboard players operation @s c.gg = #g c.t",
    say("Coffre de guilde : tous les membres de ta guilde peuvent l’ouvrir.", "green")])

# ---------------------------------------------------------------- verrou
w(P + "verrouiller.mcfunction", [f"data merge block ~ ~ ~ {VERROU}", "scoreboard players set @s c.lk 1"])
w(P + "deverrouiller.mcfunction", ["data remove block ~ ~ ~ lock", "scoreboard players set @s c.lk 0"])

# ---------------------------------------------------------------- photo du conteneur (contenu + état du bloc)
KINDS = [("chest", 1), ("trapped_chest", 2), ("barrel", 3)]
FACES = ["north", "east", "south", "west", "up", "down"]
ST = []
for kind, k in KINDS:
    if kind == "barrel":
        for fi, f_ in enumerate(FACES):
            ST.append(f"execute if block ~ ~ ~ minecraft:barrel[facing={f_}] run scoreboard players set @s c.st {k * 100 + fi * 10}")
    else:
        for fi, f_ in enumerate(FACES[:4]):
            for ti, t_ in enumerate(("single", "left", "right")):
                ST.append(f"execute if block ~ ~ ~ minecraft:{kind}[facing={f_},type={t_}] run scoreboard players set @s c.st {k * 100 + fi * 10 + ti}")
w(P + "photo.mcfunction", [
    f"execute unless block ~ ~ ~ #{NS}:protegeable run return 0"] + ST + [
    "data modify entity @s data.items set value []",
    "data modify entity @s data.items set from block ~ ~ ~ Items",
    # devenu coffre double (quelqu'un a collé un coffre) : on protège la nouvelle moitié
    f"execute if block ~ ~ ~ #{NS}:protegeable[type=left] align xyz run function {NS}:prive/moitie",
    f"execute if block ~ ~ ~ #{NS}:protegeable[type=right] align xyz run function {NS}:prive/moitie"])

# ---------------------------------------------------------------- garde du conteneur (toutes les 2 ticks)
RS = []
for kind, k in KINDS:
    if kind == "barrel":
        for fi, f_ in enumerate(FACES):
            RS.append(f"execute if score @s c.st matches {k * 100 + fi * 10} run setblock ~ ~ ~ minecraft:barrel[facing={f_}]")
    else:
        for fi, f_ in enumerate(FACES[:4]):
            for ti, t_ in enumerate(("single", "left", "right")):
                RS.append(f"execute if score @s c.st matches {k * 100 + fi * 10 + ti} run setblock ~ ~ ~ minecraft:{kind}[facing={f_},type={t_}]")
JUGE = [  # #in = un autre joueur à moins de 8 blocs ; #ok = le propriétaire à moins de 6 blocs
    # coffre de guilde (#gg = guilde) : « autre » = hors de la guilde, « propriétaire » = un membre
    "scoreboard players operation #own c.t = @s c.own",
    "scoreboard players set #gg c.t 0", "scoreboard players operation #gg c.t = @s c.gg",
    "scoreboard players set #in c.t 0", "scoreboard players set #ok c.t 0",
    "execute unless score #gg c.t matches 1.. as @a[distance=..8,gamemode=!spectator] unless score @s m.id = #own c.t run scoreboard players set #in c.t 1",
    "execute unless score #gg c.t matches 1.. as @a[distance=..6] if score @s m.id = #own c.t run scoreboard players set #ok c.t 1",
    "execute if score #gg c.t matches 1.. as @a[distance=..8,gamemode=!spectator] unless score @s m.gid = #gg c.t run scoreboard players set #in c.t 1",
    "execute if score #gg c.t matches 1.. as @a[distance=..6] if score @s m.gid = #gg c.t run scoreboard players set #ok c.t 1"]
w(P + "conteneur.mcfunction", [
    f"execute unless block ~ ~ ~ #{NS}:protegeable run return run function {NS}:prive/disparu",
    # entonnoir dessous en pause, wagonnet à entonnoir désactivé
    "execute if block ~ ~-1 ~ minecraft:hopper run data merge block ~ ~-1 ~ {TransferCooldown:20}",
    "execute as @e[type=minecraft:hopper_minecart,distance=..1.8] run data merge entity @s {Enabled:0b}",
    "execute unless entity @a[distance=..12] run return 0"] + JUGE + [
    "scoreboard players set #want c.t 1",
    "execute if score #ok c.t matches 1 if score #in c.t matches 0 run scoreboard players set #want c.t 0",
    f"execute if score #want c.t matches 1 unless score @s c.lk matches 1 run function {NS}:prive/verrouiller",
    f"execute if score #want c.t matches 0 if score @s c.lk matches 1 run function {NS}:prive/deverrouiller"])
w(P + "disparu.mcfunction", JUGE + [
    # cassé par le propriétaire seul : on retire la protection de cette partie
    f"execute if score #ok c.t matches 1 if score #in c.t matches 0 run return run function {NS}:prive/retirer_c"] + RS + [
    "data modify block ~ ~ ~ Items set from entity @s data.items",
    "scoreboard players set @s c.lk 0", f"function {NS}:prive/verrouiller",
    f"execute as @e[type=minecraft:item,distance=..2.5] run function {NS}:prive/ramasse",
    "particle minecraft:wax_on ~ ~ ~ 0.4 0.4 0.4 0 15",
    "playsound minecraft:block.wood.place block @a ~ ~ ~ 1 0.8"])
# objets lâchés par la casse : retirés s'ils viennent de tomber
w(P + "ramasse.mcfunction", [
    "execute store result score #age c.t run data get entity @s Age",
    "execute if score #age c.t matches ..60 run kill @s"])
w(P + "retirer_c.mcfunction", [
    "execute as @a[distance=..6] if score @s m.id = #own c.t run " + say("Protection retirée de ce coffre.", "yellow"),
    "kill @s"])

# ---------------------------------------------------------------- garde du panneau
PS = ["data modify entity @s data.txt set from block ~ ~ ~ front_text",
      "scoreboard players set @s c.st 0"]
for fi, f_ in enumerate(FACES[:4]):
    PS.append(f"execute if block ~ ~ ~ #minecraft:wall_signs[facing={f_}] run scoreboard players set @s c.st {1 + fi}")
for r in range(16):
    PS.append(f"execute if block ~ ~ ~ #minecraft:standing_signs[rotation={r}] run scoreboard players set @s c.st {10 + r}")
    PS.append(f"execute if block ~ ~ ~ #minecraft:ceiling_hanging_signs[rotation={r}] run scoreboard players set @s c.st {30 + r}")
w(P + "photo_panneau.mcfunction", [f"execute unless block ~ ~ ~ #minecraft:all_signs run return 0"] + PS)
RP_ = [f"execute if score @s c.st matches {1 + fi} run setblock ~ ~ ~ minecraft:oak_wall_sign[facing={f_}]" for fi, f_ in enumerate(FACES[:4])]
RP_ += [f"execute if score @s c.st matches {10 + r} run setblock ~ ~ ~ minecraft:oak_sign[rotation={r}]" for r in range(16)]
RP_ += [f"execute if score @s c.st matches {30 + r} run setblock ~ ~ ~ minecraft:oak_hanging_sign[rotation={r}]" for r in range(16)]
w(P + "panneau_garde.mcfunction", [
    f"execute unless block ~ ~ ~ #minecraft:all_signs run function {NS}:prive/panneau_disparu"])
w(P + "panneau_disparu.mcfunction", JUGE + [
    f"execute if score #ok c.t matches 1 if score #in c.t matches 0 run return run function {NS}:prive/retirer_groupe"] + RP_ + [
    "data modify block ~ ~ ~ front_text set from entity @s data.txt",
    "data merge block ~ ~ ~ {is_waxed:1b}",
    f"execute as @e[type=minecraft:item,distance=..2.5] run function {NS}:prive/ramasse"])
# le propriétaire a cassé le panneau : toute la protection saute
w(P + "retirer_groupe.mcfunction", [
    "scoreboard players operation #grp c.t = @s c.grp",
    f"execute as @e[type=minecraft:marker,tag=commerce.prive_c] if score @s c.grp = #grp c.t at @s run function {NS}:prive/liberer",
    "execute as @a[distance=..6] if score @s m.id = #own c.t run " + say("Panneau retiré : ce coffre n’est plus privé.", "yellow"),
    "kill @s"])
w(P + "liberer.mcfunction", [f"execute if block ~ ~ ~ #{NS}:protegeable run data remove block ~ ~ ~ lock", "kill @s"])

# ---------------------------------------------------------------- désinstallation (appelée par commerce:desinstaller)
w(P + "desinstaller.mcfunction", [
    f"execute as @e[type=minecraft:marker,tag=commerce.prive_c] at @s run function {NS}:prive/liberer",
    "kill @e[type=minecraft:marker,tag=commerce.prive]"] + [f"scoreboard objectives remove {o}" for o, _ in SIGN_OBJ] + [
    f"scoreboard objectives remove {o}" for o in ("c.psign", "c.lk", "c.grp", "c.st", "c.pown")])

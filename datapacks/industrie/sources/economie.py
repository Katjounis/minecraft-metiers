# -*- coding: utf-8 -*-
# Parcelles, contrats, Banque (ordres, retraits, prêts), Halle, Laboratoire, rangs, Grands Œuvres, parts d'île,
# évènements de marché. Exécuté par datapack.py après machines.py.
import math

# ---------------------------------------------------------------- achat d'une parcelle (200 + idx)
def voisins(idx):
    i, j = idx % 7, idx // 7
    return [jj * 7 + ii for ii, jj in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)) if 0 <= ii < 7 and 0 <= jj < 7]


for idx in range(49):
    i, j = idx % 7, idx // 7
    ring = max(abs(i - 3), abs(j - 3))
    prix = ANNEAUX[ring][1]
    ecl = 5 if ring == 3 else 0
    P = [f"execute unless score @s i.ile matches 0.. run return run " + say("Va d'abord sur ton île (Mon industrie, Aller sur mon île).", "red"),
         f"execute if score @s i.p{idx} matches 1 run return run " + say("Cette parcelle est déjà à toi.", "gray"),
         f"{S} set #ok i.t 0"] + [f"execute if score @s i.p{v} matches 1 run {S} set #ok i.t 1" for v in voisins(idx)] + [
         f"execute if score #ok i.t matches 0 run return run " + say("Une nouvelle parcelle doit toucher une parcelle à toi.", "red"),
         f"{S} set #max i.t 0"] + [f"execute if score @s i.rang matches {r} run {S} set #max i.t {PARC_MAX[r]}" for r in range(1, 6)] + [
         f"execute if score @s i.np >= #max i.t run return run " + say("Ton rang ne permet pas plus de parcelles : monte de rang au Bureau de l'île.", "red"),
         f"execute unless score @s c.ecus matches {prix}.. run return run " + say(f"Il te faut {mille(prix)} Écus.", "red")]
    if ecl:
        P.append(f"execute unless score @s m.ecl matches {ecl}.. run return run " + say(f"Il te faut aussi {ecl} éclats de boss.", "red"))
    P += [f"execute if score @s c.ecus matches -2147483648.. run scoreboard players remove @s c.ecus {prix}"] + ([f"{S} remove @s m.ecl {ecl}"] if ecl else []) + [
          f"{S} set @s i.p{idx} 1", f"{S} add @s i.np 1",
          f"{S} operation #n i.t = @s i.ile", f"{S} set #idx i.t {idx}", f"{S} operation #own i.t = @s m.id", f"function {NS}:parcelle/commander",
          "playsound minecraft:block.amethyst_block.resonate master @s ~ ~ ~ 1 1", say(f"Parcelle achetée ({mille(prix)} Écus) : elle apparaît sur ton île.", "green"),
          f"function {NS}:menu/cadastre"]
    fn(f"parcelle/acheter_{idx}", P)

# ---------------------------------------------------------------- contrats de Guilde (tirés chaque jour)
CQ = {p: PROD[p][3] // 8 for p in PL}                                       # volume : 1/8 de la saturation (28/11/2026 : 1/2 était hors de portée au début)
CR = {p: CQ[p] * PROD[p][2] * 3 // 200 for p in PL}                         # paiement : 1,5 x le prix de base, sans dégressif
TI = [f"{S} set #nc i.t 0"] + [f"execute if score @s i.rang matches {r} run {S} set #nc i.t {CONTRATS_JOUR[r]}" for r in range(1, 6)]
TI += [f"{S} set @s i.c{c}p 0" for c in (1, 2, 3)] + [f"{S} set @s i.c{c}f 0" for c in (1, 2, 3)]
TI += [f"data modify storage {NS}:t el set value []"]
TI += [f"execute if score @s i.s_{p} matches 1.. run data modify storage {NS}:t el append value {k}" for k, p in enumerate(PL)]
TI += [f"execute unless data storage {NS}:t el[0] run data modify storage {NS}:t el append value {PI['pierre']}",
       f"execute store result score #ne i.t run data get storage {NS}:t el"]
for c in (1, 2, 3):
    TI += [f"execute if score #nc i.t matches {c}.. run function {NS}:contrat/tirer_un {{c:{c}}}"]
fn("contrat/tirer", TI)
fn("contrat/tirer_un", [
    "execute store result score #r i.t run random value 0..100000", f"{S} operation #r i.t %= #ne i.t",
    f"execute store result storage {NS}:t r.r int 1 run {S} get #r i.t", "$data modify storage industrie:t r.c set value $(c)",
    f"function {NS}:contrat/tirer_m with storage {NS}:t r"])
fn("contrat/tirer_m", ["$execute store result score @s i.c$(c)p run data get storage industrie:t el[$(r)]", "$scoreboard players add @s i.c$(c)p 1"] +
   [f"$execute if score @s i.c$(c)p matches {k + 1} run scoreboard players set @s i.c$(c)q {CQ[p]}" for k, p in enumerate(PL)] +
   [f"$execute if score @s i.c$(c)p matches {k + 1} run scoreboard players set @s i.c$(c)r {CR[p]}" for k, p in enumerate(PL)])
for c in (1, 2, 3):
    LV = [f"execute unless score @s i.c{c}p matches 1.. run return run " + say("Pas de contrat ici aujourd'hui.", "gray"),
          f"execute if score @s i.c{c}f matches 1 run return run " + say("Contrat déjà livré.", "gray"), f"{S} set #ok i.t 0"]
    LV += [f"execute if score @s i.c{c}p matches {k + 1} run {S} set @s i.c{c}q {CQ[p]}" for k, p in enumerate(PL)]
    LV += [f"execute if score @s i.c{c}p matches {k + 1} run {S} set @s i.c{c}r {CR[p]}" for k, p in enumerate(PL)]
    for k, p in enumerate(PL):
        LV += [f"execute if score @s i.c{c}p matches {k + 1} if score @s i.s_{p} >= @s i.c{c}q run {S} set #ok i.t {k + 1}"]
    LV += [f"execute if score #ok i.t matches 0 run return run " + say("Pas assez de marchandise au Nexus pour ce contrat.", "red")]
    LV += [f"execute if score #ok i.t matches {k + 1} run {S} operation @s i.s_{p} -= @s i.c{c}q" for k, p in enumerate(PL)]
    LV += [f"{S} set @s i.c{c}f 1", f"{S} add @s i.ctr 1",
           f"execute if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus += @s i.c{c}r",
           f"{S} operation @s i.jn += @s i.c{c}r",
           f"{S} operation #x i.t = @s i.rang", f"{S} set #y i.t 200", f"{S} operation #x i.t *= #y i.t", f"{S} operation @s i.ri += #x i.t",
           f"execute if score @s i.rang matches 3.. run {S} add @s m.ecl 1",
           "playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 0.8 1.2",
           say("Contrat livré : payé sans dégressif, réputation en plus.", "green"), f"function {NS}:menu/halle"]
    fn(f"contrat/livrer_{c}", LV)

# ---------------------------------------------------------------- Banque
fn("banque/acheter", [
    f"execute if score @s i.bq matches 1 run return run " + say("Tu as déjà ta Banque.", "gray"),
    f"execute unless score @s i.rang matches 2.. run return run " + say("La Banque s'ouvre au rang Manufacture.", "red"),
    f"execute unless score @s c.ecus matches {BANQUE_PRIX}.. run return run " + say(f"Il te faut {mille(BANQUE_PRIX)} Écus.", "red"),
    f"execute if score @s c.ecus matches -2147483648.. run scoreboard players remove @s c.ecus {BANQUE_PRIX}", f"{S} set @s i.bq 1",
    *poser_bat("banque"), "playsound minecraft:block.iron_door.close master @s ~ ~ ~ 1 0.6",
    say("La Banque de l'Archipel est à toi : choisis produit par produit ce que tu gardes ou vends.", "gold"), f"function {NS}:menu/banque"])
# prélèvement du prêt sur une vente (#N centièmes) : 25 %, 50 % en retard
fn("banque/prelever", [
    f"{S} set #y i.t {PRET_PART}", f"execute if score @s i.pret matches 2 run {S} set #y i.t 50",
    f"{S} operation #r i.t = #N i.t", f"{S} operation #r i.t /= #100 i.g", f"{S} operation #r i.t *= #y i.t", f"{S} operation #r i.t /= #100 i.g",
    f"execute if score #r i.t > @s i.dette run {S} operation #r i.t = @s i.dette",
    f"{S} operation @s i.dette -= #r i.t", f"{S} operation #r i.t *= #100 i.g", f"{S} operation #N i.t -= #r i.t",
    f"execute if score @s i.dette matches ..0 run function {NS}:banque/solde"])
fn("banque/solde", [f"execute if score @s i.pret matches 2 run {S} set @s i.pban 30", f"{S} set @s i.pret 0", f"{S} set @s i.dette 0", f"{S} set @s i.pj 0",
                    say("Prêt remboursé.", "green")])
fn("banque/jour", [f"{S} add @s i.pj 1", f"execute if score @s i.pj matches {PRET_JOURS + 1}.. if score @s i.pret matches 1 run function {NS}:banque/retard"])
fn("banque/retard", [f"{S} set @s i.pret 2", say("Prêt en retard : 50 % de tes ventes partent au remboursement et ta réputation est gelée jusqu'au solde.", "red")])
EMP = [f"execute unless score @s i.bq matches 1 run return run " + say("Il te faut la Banque (rang Manufacture).", "red"),
       f"execute if score @s i.dette matches 1.. run return run " + say("Un seul prêt à la fois.", "red"),
       f"execute if score @s i.pban matches 1.. run return run " + say("Après un retard, pas de nouveau prêt pendant 30 jours.", "red"),
       f"{S} operation #max i.t = @s i.r7", f"{S} operation #max i.t *= #3 i.g", f"{S} set #pm i.t 0"]
EMP += [f"execute if score @s i.rang matches {r} run {S} set #pm i.t {v}" for r, v in PRET_MAX.items()]
EMP += [f"execute if score #max i.t > #pm i.t run {S} operation #max i.t = #pm i.t",
        f"execute unless score #max i.t matches 10000.. run return run " + say("Tes recettes sont encore trop faibles pour un prêt (3 jours de recettes, 10 000 Écus au moins).", "red"),
        f"execute if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus += #max i.t",
        f"{S} operation @s i.dette = #max i.t", f"{S} operation #x i.t = #max i.t", f"{S} operation #x i.t /= #10 i.g", f"{S} operation @s i.dette += #x i.t",
        f"{S} set @s i.pret 1", f"{S} set @s i.pj 0",
        "playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 0.8", say("Prêt accordé : remboursé tout seul par une part de tes ventes.", "green"), f"function {NS}:menu/banque"]
fn("banque/emprunter", EMP)
fn("banque/rembourser", [
    f"execute unless score @s i.dette matches 1.. run return run " + say("Aucun prêt en cours.", "gray"),
    f"{S} operation #r i.t = @s i.dette", f"execute if score #r i.t > @s c.ecus run {S} operation #r i.t = @s c.ecus",
    f"execute unless score #r i.t matches 1.. run return run " + say("Pas d'Écus sur ton compte.", "red"),
    f"execute if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus -= #r i.t", f"{S} operation @s i.dette -= #r i.t",
    f"execute if score @s i.dette matches ..0 run function {NS}:banque/solde", f"function {NS}:menu/banque"])

# ordres par produit : 1000 + idx x 10 + action (0 fiche, 1 à 5 ordre, 6 plus, 7 moins, 8 retirer 64)
for k, p in enumerate(PL):
    nom, item, p0, S0 = PROD[p]
    for a in range(1, 6):
        fn(f"banque/o_{p}_{a}", [f"execute unless score @s i.bq matches 1 run return run " + say("Il te faut la Banque.", "red"),
                                 f"{S} set @s i.o_{p} {a - 1}",
                                 *([f"execute if score @s i.x_{p} matches ..999 run {S} set @s i.x_{p} 1000"] if a in (4, 5) else []),
                                 *([f"execute unless score @s i.x_{p} matches 10..150 run {S} set @s i.x_{p} 70"] if a == 3 else []),
                                 f"function {NS}:menu/produit_{p}"])
    fn(f"banque/plus_{p}", [f"execute if score @s i.o_{p} matches 2 run {S} add @s i.x_{p} 10", f"execute if score @s i.o_{p} matches 2 if score @s i.x_{p} matches 151.. run {S} set @s i.x_{p} 150",
                            f"execute if score @s i.o_{p} matches 3..4 if score @s i.x_{p} matches ..500000000 run {S} operation @s i.x_{p} *= #2 i.g", f"function {NS}:menu/produit_{p}"])
    fn(f"banque/moins_{p}", [f"execute if score @s i.o_{p} matches 2 run {S} remove @s i.x_{p} 10", f"execute if score @s i.o_{p} matches 2 if score @s i.x_{p} matches ..9 run {S} set @s i.x_{p} 10",
                             f"execute if score @s i.o_{p} matches 3..4 run {S} operation @s i.x_{p} /= #2 i.g",
                             f"execute if score @s i.o_{p} matches 3..4 if score @s i.x_{p} matches ..63 run {S} set @s i.x_{p} 64", f"function {NS}:menu/produit_{p}"])
    if item:
        fn(f"banque/retirer_{p}", [
            f"{S} set #q i.t {RETRAIT_JOUR}", f"execute if score @s i.s_{p} < #q i.t run {S} operation #q i.t = @s i.s_{p}",
            f"execute unless score #q i.t matches 1.. run return run " + say("Rien en stock.", "gray"),
            f"{S} set #cout i.t 0", f"execute if score @s i.w_{p} matches {RETRAIT_JOUR}.. run {S} operation #cout i.t = #q i.t",
            f"{S} set #y i.t {p0 * 2}", f"{S} operation #cout i.t *= #y i.t", f"{S} operation #cout i.t /= #100 i.g",
            f"execute unless score @s c.ecus >= #cout i.t run return run " + say("Au-delà de 64 par jour, le retrait coûte 4 fois le prix du Commerce : pas assez d'Écus.", "red"),
            f"execute if score #cout i.t matches 1.. if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus -= #cout i.t",
            f"{S} operation @s i.s_{p} -= #q i.t", f"{S} operation @s i.w_{p} += #q i.t",
            f"execute store result storage {NS}:t g.q int 1 run {S} get #q i.t", f"function {NS}:banque/donner_{p} with storage {NS}:t g",
            say("Sorti du Nexus. Ces objets portent la marque du Nexus : le Commerce ne les rachète pas.", "gray"), f"function {NS}:menu/produit_{p}"])
        fn(f"banque/donner_{p}", f'$give @s minecraft:{item}[minecraft:custom_data={{industrie:1b}},minecraft:lore=[{{text:"Sorti du Nexus",color:"dark_gray",italic:false}}]] $(q)')

# ---------------------------------------------------------------- Halle : niveau suivant (530)
HA = [f"{S} operation #hn i.t = @s i.halle", f"{S} add #hn i.t 1", f"execute if score #hn i.t matches {len(HALLE)}.. run return run " + say("Ta Halle est déjà une Bourse impériale.", "gray")]
for k, (nom, rang, prix, ecl, cap, com, sb) in enumerate(HALLE):
    if not k:
        continue
    c = f"execute if score #hn i.t matches {k}"
    HA += [f"{c} unless score @s i.rang matches {rang}.. run return run " + say(f"{nom} : il faut le rang {RANGS[rang][0]}.", "red"),
           f"{c} unless score @s c.ecus matches {prix}.. run return run " + say(f"{nom} : il te faut {mille(prix)} Écus.", "red")]
    if ecl:
        HA.append(f"{c} unless score @s m.ecl matches {ecl}.. run return run " + say(f"{nom} : il te faut {ecl} éclats de boss.", "red"))
    HA += [f"{c} if score @s c.ecus matches -2147483648.. run scoreboard players remove @s c.ecus {prix}"] + ([f"{c} run {S} remove @s m.ecl {ecl}"] if ecl else [])
HA += [f"{S} operation @s i.halle = #hn i.t"]
fn("halle/ameliorer", HA + [f"execute if score #hn i.t matches 2.. run function {NS}:halle/poser",
                            "playsound minecraft:block.bell.use master @s ~ ~ ~ 1 0.8", say("La Halle s'agrandit : plus de ventes par heure, moins de commission.", "gold"),
                            f"function {NS}:menu/halle"])
fn("halle/poser", poser_bat("halle", old="echoppe") + [f"execute if score @s i.halle matches 3 run function {NS}:halle/grande"])
fn("halle/grande", [f"{S} operation #n i.t = @s i.ile", f"function {NS}:ile/centre",
                    f"execute store result storage {NS}:t b.x int 1 run {S} get #cx i.t", f"execute store result storage {NS}:t b.z int 1 run {S} get #cz i.t",
                    f"function {NS}:halle/grande_m with storage {NS}:t b"])
fn("halle/grande_m", "$execute in industrie:archipel as @e[tag=ind.b_halle,x=$(x),y=64,z=$(z),distance=..40] run data merge entity @s {transformation:{scale:[2.8f,2.8f,2.8f]},start_interpolation:0,interpolation_duration:40}")

# ---------------------------------------------------------------- Laboratoire (560 + b) : un brevet à la fois, 1 h par niveau
for b, (cle, nom, effet, base, res, qb) in enumerate(BRANCHES, 1):
    LB = [f"execute unless score @s i.rang matches 2.. run return run " + say("Le Laboratoire s'ouvre au rang Manufacture.", "red"),
          f"execute if score @s i.rb matches 1.. run return run " + say("Une recherche est déjà en cours.", "red"),
          f"execute if score @s i.b{b} matches 10.. run return run " + say(f"{nom} est au maximum.", "gray"),
          f"execute if score @s i.b{b} matches 5.. unless score @s i.rang matches 4.. run return run " + say("Les niveaux 6 à 10 demandent le rang Consortium.", "red")]
    for n in range(1, 11):
        e, q = int(base * 2.2 ** (n - 1)), qb * 2 ** (n - 1)
        r_ = res if n < 6 else {"or": "bijou", "fer": "acier", "cuivre": "mecanisme", "charbon": "elixir"}[res]
        q = q if n < 6 else max(100, q // 40)
        c = f"execute if score @s i.b{b} matches {n - 1}"
        LB += [f"{c} unless score @s c.ecus matches {e}.. run return run " + say(f"Niveau {n} : {mille(e)} Écus et {mille(q)} {PROD[r_][0].lower()}.", "red"),
               f"{c} unless score @s i.s_{r_} matches {q}.. run return run " + say(f"Niveau {n} : il faut {mille(q)} {PROD[r_][0].lower()} au Nexus.", "red"),
               f"{c} run {S} remove @s i.s_{r_} {q}", f"{c} if score @s c.ecus matches -2147483648.. run scoreboard players remove @s c.ecus {e}"]
    LB += [f"{S} set @s i.rb {b}", f"{S} operation @s i.rt = #now i.g", f"{S} add @s i.rt 72000",
           "playsound minecraft:block.brewing_stand.brew master @s ~ ~ ~ 1 1", say(f"Recherche lancée : {nom}, prête dans 1 heure de jeu.", "aqua"), f"function {NS}:menu/labo"]
    fn(f"labo/chercher_{b}", LB)
fn("labo/verif", [f"execute if score #now i.g < @s i.rt run return 0"] +
   [f"execute if score @s i.rb matches {b} run {S} add @s i.b{b} 1" for b in range(1, 5)] +
   [f"{S} set @s i.rb 0", "playsound minecraft:block.beacon.activate master @s ~ ~ ~ 1 1.4", say("Recherche terminée : le brevet est actif.", "aqua")])

# ---------------------------------------------------------------- rangs (570)
RG = [f"{S} operation #rn i.t = @s i.rang", f"{S} add #rn i.t 1", f"execute if score #rn i.t matches 6.. run return run " + say("Tu es déjà un Empire.", "gold"),
      f"{S} set #bk i.t 0"] + [f"{S} operation #bk i.t += @s m.bk{k}" for k in range(1, 6)]
for r in range(2, 6):
    nom, ri, ctr, prix, ecl, cond = RANGS[r]
    c = f"execute if score #rn i.t matches {r}"
    RG += [f"{c} unless score @s i.ri matches {ri}.. run return run " + say(f"{nom} : il faut {mille(ri)} de réputation industrielle.", "red"),
           f"{c} unless score @s i.ctr matches {ctr}.. run return run " + say(f"{nom} : il faut {ctr} contrats livrés.", "red"),
           f"{c} unless score @s c.ecus matches {prix}.. run return run " + say(f"{nom} : il faut {mille(prix)} Écus.", "red")]
    if ecl:
        RG.append(f"{c} unless score @s m.ecl matches {ecl}.. run return run " + say(f"{nom} : il faut {ecl} éclats de boss.", "red"))
    if cond == "boss":
        RG.append(f"{c} unless score #bk i.t matches 1.. run return run " + say(f"{nom} : il faut avoir vaincu un boss de Métiers.", "red"))
    if cond == "wither":
        RG.append(f"{c} unless score @s i.kwi matches 3.. run return run " + say(f"{nom} : il faut vaincre 3 Wither (comptés depuis l'arrivée d'Industrie).", "red"))
    if cond == "dragon":
        RG.append(f"{c} unless score @s m.kdragon matches 1.. run return run " + say(f"{nom} : il faut vaincre l'Ender Dragon.", "red"))
    RG += [f"{c} if score @s c.ecus matches -2147483648.. run scoreboard players remove @s c.ecus {prix}"] + ([f"{c} run {S} remove @s m.ecl {ecl}"] if ecl else [])
RG += [f"{S} operation @s i.rang = #rn i.t",
       *[f'execute if score #rn i.t matches {r} run tellraw @a [{{text:"✦ ",color:"gold",bold:true}},{{selector:"@s",color:"white",bold:true}},{{text:" devient {RANGS[r][0]} dans l\'Archipel !",color:"#F7C843",bold:false}}]' for r in range(2, 6)],
       "playsound minecraft:ui.toast.challenge_complete master @a ~ ~ ~ 0.6 1",
       'summon minecraft:firework_rocket ~ ~1 ~ {LifeTime:24,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":{flight_duration:1,explosions:[{shape:"large_ball",colors:[I;16238659,16777215],has_trail:true}]}}}}',
       f"execute if score #rn i.t matches 2 run function {NS}:rang/labo", f"function {NS}:contrat/tirer", f"function {NS}:menu/bureau"]
fn("rang/passer", RG)
fn("rang/labo", poser_bat("labo") + [say("Le Laboratoire et la Banque sont maintenant accessibles. Le Laboratoire est offert.", "aqua")])

# ---------------------------------------------------------------- Grands Œuvres (571)
OE = [f"execute unless score @s i.rang matches 4.. run return run " + say("Les Grands Œuvres s'ouvrent au rang Consortium.", "red"),
      f"execute if score @s i.go matches {len(OEUVRES)}.. run return run " + say("Tous les Grands Œuvres sont élevés.", "gold")]
for n, (nom, res) in enumerate(OEUVRES, 1):
    e = int(8_000_000 * 1.8 ** (n - 1))
    c = f"execute if score @s i.go matches {n - 1}"
    OE += [f"{c} unless score @s c.ecus matches {e}.. run return run " + say(f"{nom} : {fe(e)} Écus, {10 * n} éclats et " + ", ".join(f"{mille(q)} {PROD[p][0].lower()}" for p, q in res.items()) + ".", "red"),
           f"{c} unless score @s m.ecl matches {10 * n}.. run return run " + say(f"{nom} : il faut {10 * n} éclats de boss.", "red")]
    OE += [f"{c} unless score @s i.s_{p} matches {q}.. run return run " + say(f"{nom} : il faut {mille(q)} {PROD[p][0].lower()} au Nexus.", "red") for p, q in res.items()]
    OE += [f"{c} run {S} remove @s i.s_{p} {q}" for p, q in res.items()]
    OE += [f"{c} if score @s c.ecus matches -2147483648.. run scoreboard players remove @s c.ecus {e}", f"{c} run {S} remove @s m.ecl {10 * n}"]
OE += [f"{S} add @s i.go 1"]
for n in range(1, len(OEUVRES) + 1):
    x, z, _, code = BAT["oeuvre"]
    ech = round(0.9 + 0.3 * n, 2)
    OE.append(f'execute if score @s i.go matches {n} run data modify storage {NS}:t b set value {{nom:"oeuvre",old:"oeuvre",dx:{x},dz:{z},h:{round(1.5 * ech, 2)},ech:{ech},code:{code},lw:{round(ech * 1.2, 1)},lh:{round(ech * 3, 1)}}}')
OE += [f"execute if dimension {DIM} run function {NS}:batiment/poser",
       *[f'execute if score @s i.go matches {n} run tellraw @a [{{text:"✦ ",color:"gold"}},{{selector:"@s",color:"white"}},{{text:" élève {nom} sur son île : +8 % de production.",color:"#F7C843"}}]' for n, (nom, _) in enumerate(OEUVRES, 1)],
       "playsound minecraft:block.end_portal.spawn master @s ~ ~ ~ 0.5 1.2", f"function {NS}:menu/bureau"]
fn("oeuvre/elever", OE)

# ---------------------------------------------------------------- parts d'île (rang 4)
fn("parts/vendre", [f"execute unless score @s i.rang matches 4.. run return run " + say("Les parts d'île s'ouvrent au rang Consortium.", "red"),
                    f"execute if score @s i.pv matches 10.. run return run " + say("10 parts au plus par île.", "red"),
                    f"{S} set @s i.pend 1",
                    'dialog show @s {type:"minecraft:multi_action",title:{text:"Vendre une part de ton île",color:"#F7C843",bold:true},can_close_with_escape:true,pause:false,'
                    'body:[{type:"minecraft:plain_message",width:320,contents:{text:"Prix de la part en Écus. Elle touchera 2 % de tes recettes nettes chaque jour.",color:"gray"}}],'
                    'inputs:[{type:"minecraft:text",key:"m",label:{text:"Prix"},width:200,max_length:9}],'
                    'actions:[{label:{text:"Mettre en vente",color:"yellow",bold:true},width:150,action:{type:"minecraft:dynamic/run_command",template:"trigger industrie set -$(m)"}},'
                    '{label:{text:"Annuler"},width:150,action:{type:"run_command",command:"trigger industrie set 11"}}],columns:2}'])
fn("saisie", [f"{S} operation #v i.t = @s industrie", f"{S} set @s industrie 0", f"{S} operation #v i.t *= #-1 i.g",
              f"execute if score @s i.pend matches 1 run function {NS}:parts/offre", f"{S} set @s i.pend 0"])
fn("parts/offre", [
    f"execute unless score #v i.t matches 1000.. run return run " + say("Prix trop bas (1 000 Écus au moins).", "red"),
    f"{S} add @s i.pv 1", f"{S} add #uid i.g 1",
    f"execute store result storage {NS}:t po.o int 1 run {S} get @s m.id", f"execute store result storage {NS}:t po.p int 1 run {S} get #v i.t",
    f"execute store result storage {NS}:t po.k int 1 run {S} get #uid i.g",
    "function commerce:joueur/nom_moi", f"data modify storage {NS}:t po.nom set from storage commerce:t moi",
    f"data modify storage {NS}:parts offres append from storage {NS}:t po",
    say("Part mise en vente sur le Marché des parts.", "green"), f"function {NS}:menu/parts"])
# achat : 600000 + uid
fn("parts/acheter", [
    f"{S} operation #k i.t = #v i.t", f"{S} remove #k i.t 600000",
    f"execute store result storage {NS}:t pk.k int 1 run {S} get #k i.t", f"data remove storage {NS}:t pa",
    f"function {NS}:parts/trouver with storage {NS}:t pk",
    f"execute unless data storage {NS}:t pa.p run return run " + say("Cette part n'est plus en vente.", "red"),
    f"execute store result score #o i.t run data get storage {NS}:t pa.o", f"execute store result score #p i.t run data get storage {NS}:t pa.p",
    f"execute if score #o i.t = @s m.id run return run " + say("C'est ta propre île.", "gray"),
    f"execute if score @s i.ph matches 20.. run return run " + say("20 parts au plus en portefeuille.", "red"),
    f"{S} operation #pt i.t = #p i.t", f"{S} operation #x i.t = #p i.t", f"{S} operation #x i.t /= #20 i.g", f"{S} operation #pt i.t += #x i.t",
    f"execute unless score @s c.ecus >= #pt i.t run return run " + say("Pas assez d'Écus (prix + 5 % de taxe).", "red"),
    f"execute if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus -= #pt i.t", f"{S} add @s i.ph 1",
    f"function {NS}:parts/payer_vendeur with storage {NS}:t pa",
    "function commerce:joueur/nom_moi", f"data modify storage {NS}:t pa.hn set from storage commerce:t moi",
    f"execute store result storage {NS}:t pa.hid int 1 run {S} get @s m.id",
    f"function {NS}:parts/oter with storage {NS}:t pk", f"data modify storage {NS}:parts h append from storage {NS}:t pa",
    "playsound minecraft:entity.villager.yes master @s ~ ~ ~ 1 1", say("Part achetée : tu toucheras 2 % des recettes de cette île chaque jour.", "green"), f"function {NS}:menu/parts"])
fn("parts/trouver", "$data modify storage industrie:t pa set from storage industrie:parts offres[{k:$(k)}]")
fn("parts/oter", "$data remove storage industrie:parts offres[{k:$(k)}]")
fn("parts/payer_vendeur", ["$scoreboard players add $(nom) c.ecus $(p)",
                           '$tellraw @a[name=$(nom)] [{text:"[Industrie] ",color:"#F7C843"},{selector:"@s",color:"white"},{text:" achète une part de ton île : +$(p) Écus.",color:"green"}]'])
# dividendes : à la fin du jour du propriétaire, 2 % de ses recettes nettes de la veille par part
fn("parts/dividendes", [f"{S} operation #me i.t = @s m.id", f"{S} operation #div i.t = @s i.prev", f"{S} operation #div i.t /= #100 i.g", f"{S} operation #div i.t *= #2 i.g",
                        f"execute unless score #div i.t matches 1.. run return 0",
                        f"execute store result storage {NS}:t dv.d int 1 run {S} get #div i.t",
                        f"data modify storage {NS}:t W set from storage {NS}:parts h", f"function {NS}:parts/div_boucle"])
fn("parts/div_boucle", [f"execute unless data storage {NS}:t W[0] run return 0",
                        f"data modify storage {NS}:t W[0].d set from storage {NS}:t dv.d", f"function {NS}:parts/div_m with storage {NS}:t W[0]",
                        f"data remove storage {NS}:t W[0]", f"function {NS}:parts/div_boucle"])
fn("parts/div_m", ["$execute unless score #me i.t matches $(o) run return 0",
                   "$execute if score @s c.ecus matches -2147483648.. run scoreboard players remove @s c.ecus $(d)",
                   "$scoreboard players add $(hn) c.ecus $(d)",
                   '$tellraw @a[name=$(hn)] [{text:"[Industrie] ",color:"#F7C843"},{text:"Dividende de l\'île de ",color:"gray"},{selector:"@s",color:"white"},{text:" : +$(d) Écus.",color:"green"}]'])
# rachat : la première part vendue de son île, au prix d'achat + 10 %
fn("parts/racheter", [f"{S} operation #me i.t = @s m.id", f"data remove storage {NS}:t pr",
                      f"data modify storage {NS}:t W set from storage {NS}:parts h", f"function {NS}:parts/rch_boucle",
                      f"execute unless data storage {NS}:t pr.p run return run " + say("Aucune part de ton île n'est détenue par un autre joueur.", "gray"),
                      f"execute store result score #p i.t run data get storage {NS}:t pr.p", f"{S} operation #x i.t = #p i.t", f"{S} operation #x i.t /= #10 i.g", f"{S} operation #p i.t += #x i.t",
                      f"execute unless score @s c.ecus >= #p i.t run return run " + say("Pas assez d'Écus pour racheter (prix + 10 %).", "red"),
                      f"execute if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus -= #p i.t",
                      f"execute store result storage {NS}:t pr.r int 1 run {S} get #p i.t", f"function {NS}:parts/rch_payer with storage {NS}:t pr",
                      f"{S} remove @s i.pv 1", say("Part rachetée.", "green"), f"function {NS}:menu/parts"])
fn("parts/rch_boucle", [f"execute unless data storage {NS}:t W[0] run return 0", f"execute if data storage {NS}:t pr.p run return 0",
                        f"function {NS}:parts/rch_m with storage {NS}:t W[0]", f"data remove storage {NS}:t W[0]", f"function {NS}:parts/rch_boucle"])
fn("parts/rch_m", ["$execute if score #me i.t matches $(o) run data modify storage industrie:t pr set from storage industrie:t W[0]"])
fn("parts/rch_payer", ["$scoreboard players add $(hn) c.ecus $(r)", "$scoreboard players remove $(hn) i.ph 1",
                       "$data remove storage industrie:parts h[{k:$(k)}]",
                       '$tellraw @a[name=$(hn)] [{text:"[Industrie] ",color:"#F7C843"},{selector:"@s",color:"white"},{text:" rachète sa part : +$(r) Écus.",color:"green"}]'])
fn("parts/retirer", [f"{S} operation #me i.t = @s m.id", f"data modify storage {NS}:t W set from storage {NS}:parts offres", f"function {NS}:parts/ret_boucle",
                     say("Tes parts encore en vente sont retirées.", "gray"), f"function {NS}:menu/parts"])
fn("parts/ret_boucle", [f"execute unless data storage {NS}:t W[0] run return 0", f"function {NS}:parts/ret_m with storage {NS}:t W[0]",
                        f"data remove storage {NS}:t W[0]", f"function {NS}:parts/ret_boucle"])
fn("parts/ret_m", ["$execute unless score #me i.t matches $(o) run return 0", "$data remove storage industrie:parts offres[{k:$(k)}]", f"{S} remove @s i.pv 1"])

# ---------------------------------------------------------------- évènements de marché : un toutes les 2 h de jeu, 2 h
EVP = [PI[p] + 1 for p in ("fer", "or", "diamant", "emeraude", "acier", "mecanisme", "bijou", "elixir", "ble", "netherite", "perle", "blaze")]
fn("evenement/seconde", [f"{S} add #evt i.g 1", f"execute if score #evt i.g matches 7200.. run function {NS}:evenement/nouveau"])
EVN = [f"{S} set #evt i.g 0", f"{S} set #evp i.g 0", f"{S} set #evm i.g 100", f"{S} set #foire i.g 100",
       "execute store result score #ev i.g run random value 0..4", "execute store result score #r i.t run random value 0..1000",
       f"{S} set #y i.t {len(EVP)}", f"{S} operation #r i.t %= #y i.t"]
EVN += [f"execute if score #r i.t matches {k} run {S} set #evp i.g {v}" for k, v in enumerate(EVP)]
EVN += [f"execute if score #ev i.g matches 0 run {S} set #evp i.g 0",
        f"execute if score #ev i.g matches 1 run {S} set #evm i.g 160", f"execute if score #ev i.g matches 2 run {S} set #evm i.g 50",
        f"execute if score #ev i.g matches 3 run {S} set #evp i.g {PI['or'] + 1}", f"execute if score #ev i.g matches 3 run {S} set #evm i.g 150",
        f"execute if score #ev i.g matches 4 run {S} set #evp i.g 0", f"execute if score #ev i.g matches 4 run {S} set #foire i.g 150",
        f"data modify storage {NS}:g ev set value \"Marché calme.\""]
for k, p in enumerate(PL):
    EVN += [f'execute if score #ev i.g matches 1 if score #evp i.g matches {k + 1} run data modify storage {NS}:g ev set value "Pénurie de {PROD[p][0].lower()} : prix x1,6 pendant 2 h."',
            f'execute if score #ev i.g matches 2 if score #evp i.g matches {k + 1} run data modify storage {NS}:g ev set value "Krach : {PROD[p][0].lower()} à moitié prix pendant 2 h."']
EVN += [f'execute if score #ev i.g matches 3 run data modify storage {NS}:g ev set value "Ruée vers l\'or : or x1,5 pendant 2 h."',
        f'execute if score #ev i.g matches 4 run data modify storage {NS}:g ev set value "Foire impériale : les acheteurs affluent, saturation +50 % pendant 2 h."',
        f"execute unless score #ev i.g matches 0 run function {NS}:evenement/annonce"]
fn("evenement/nouveau", EVN)
fn("evenement/annonce", ['tellraw @a[scores={i.ile=0..}] [{text:"[Bourse de l\'Archipel] ",color:"#F7C843",bold:true},{storage:"industrie:g",nbt:"ev",color:"yellow",bold:false}]'])

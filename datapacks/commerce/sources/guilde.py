# -*- coding: utf-8 -*-
# Trésor de guilde (25.6) : la guilde de Métiers (storage metiers:gu, score m.gid du joueur) a un trésor en Écus côté
# Commerce. Les membres y déposent, le chef achète des niveaux de guilde, qui donnent à tous les membres :
#   niveau 1 : +2 % sur les ventes au marché        niveau 2 : +4 % ventes, épargne à 3 % par semaine
#   niveau 3 : +6 % ventes, épargne 3 %, +5 % d'XP de métier     niveau 4 : +8 % ventes, épargne 4 % (plafond doublé), +5 % XP
#   niveau 5 : +10 % ventes, épargne 4 %, +10 % XP de métier
# Pas de remise à l'achat : avec les bonus de vente cumulés, racheter moins cher que 4 fois la base ouvrirait un
# achat-revente gagnant (la vente monte jusqu'à 3,85 fois la base au plus avec le bonus de guilde).
# Le niveau de la guilde est recopié toutes les 5 secondes dans le score c.gn de chaque membre en ligne : c'est lui que
# lisent les prix (prix/bonus, prix/vente) et Métiers (gain d'XP). Le chef peut aussi reprendre des Écus du trésor.
# Exécuté par datapack.py (partage w, F, NS, T, L, btn, dlg, say, BAN, ECU...).
S = "scoreboard players"
GD = F + "guilde/"
COUT = {1: 10000, 2: 25000, 3: 50000, 4: 100000, 5: 200000}
AVANT = {1: "+2 % sur tes ventes au marché", 2: "+4 % ventes et épargne à 3 % par semaine", 3: "+6 % ventes, épargne 3 % et +5 % d’XP de métier",
         4: "+8 % ventes, épargne 4 % (jusqu’à 10 000 par semaine) et +5 % d’XP", 5: "+10 % ventes, épargne 4 % et +10 % d’XP de métier"}
fe = lambda n: f"{n:,}".replace(",", " ")

def add_lines(path, lignes):
    with open(os.path.join(ROOT, path), "a", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")


w(GD + "load.mcfunction", [f"scoreboard objectives add c.gn dummy", "scoreboard players set #20 c.g 20", "scoreboard players set #90 c.g 90",
                           f"execute unless data storage {NS}:gt G run data modify storage {NS}:gt G set value []"])

# ---------------------------------------------------------------- niveau de la guilde -> c.gn du joueur
w(GD + "sync.mcfunction", [
    f"{S} set @s c.gn 0",
    "execute unless score @s m.gid matches 1.. run return 0",
    f"execute store result storage {NS}:t gg.g int 1 run {S} get @s m.gid",
    f"function {NS}:guilde/sync_m with storage {NS}:t gg"])
w(GD + "sync_m.mcfunction", [
    f"$execute unless data storage {NS}:gt G[{{g:$(g)}}] run data modify storage {NS}:gt G append value {{g:$(g),t:0,n:0}}",
    f"$execute store result score @s c.gn run data get storage {NS}:gt G[{{g:$(g)}}].n"])

# prix : bonus de vente (pour mille) et remise à l'achat
add_lines(F + "prix/bonus.mcfunction", [
    "scoreboard players operation #gb c.t = @s c.gn", "scoreboard players operation #gb c.t *= #20 c.g",
    "execute if score @s c.gn matches 1..5 run scoreboard players operation #bon c.t += #gb c.t"])
# épargne : la guilde du titulaire relève le taux (score c.gn lu par nom, valable même hors ligne)

# ---------------------------------------------------------------- page
P = [f"function {NS}:guilde/sync",
     "execute unless score @s m.gid matches 1.. run return run " + say(
         "Tu n’as pas de guilde. Fonde-la ou rejoins-en une : touche G, Métiers, Activités, Guilde. Ensuite, son trésor est ici.", "yellow"),
     f"execute store result storage {NS}:gp g int 1 run {S} get @s m.gid",
     f"function {NS}:guilde/page_m with storage {NS}:gp"]
w(GD + "page.mcfunction", P)
w(GD + "page_m.mcfunction", [
    f"$data modify storage {NS}:gp nom set from storage metiers:gu L[{{id:$(g)}}].nomc",
    f"$execute store result score #gt c.t run data get storage {NS}:gt G[{{g:$(g)}}].t",
    f"$execute store result score #gnv c.t run data get storage {NS}:gt G[{{g:$(g)}}].n",
    f"execute store result storage {NS}:gp t int 1 run {S} get #gt c.t",
    f"execute store result storage {NS}:gp n int 1 run {S} get #gnv c.t",
    f"execute store result storage {NS}:gp e int 1 run {S} get @s c.ecus",
    f'data modify storage {NS}:gp chef set value "Seul le chef peut acheter un niveau ou reprendre des Écus."',
    f'execute if function metiers:guilde/suis_chef run data modify storage {NS}:gp chef set value "Tu es le chef : c’est toi qui achètes les niveaux."',
    f'data modify storage {NS}:gp suiv set value "Niveau maximum atteint."'] +
    [f'execute if score #gnv c.t matches {n - 1} run data modify storage {NS}:gp suiv set value "Niveau {n} pour {fe(c)} Écus du trésor : {AVANT[n]}."'
     for n, c in COUT.items()] +
    [f'data modify storage {NS}:gp av set value "Aucun avantage pour l’instant."'] +
    [f'execute if score #gnv c.t matches {n} run data modify storage {NS}:gp av set value "{AVANT[n]}"' for n in AVANT] +
    [f"function {NS}:guilde/page_d with storage {NS}:gp"])
IC = lambda i: f'{{object:"atlas",atlas:"minecraft:items",sprite:"minecraft:item/{i}"}}'
w(GD + "page_d.mcfunction", "$" + dlg(
    T("Trésor de guilde", "gold", True),
    ['{type:"minecraft:plain_message",width:380,contents:' +
     L('$(nom)', T("   niveau $(n)/5\\n", "yellow", True), T("Trésor : $(t) " + ECU + "   ·   ton compte : $(e) " + ECU + "\\n", "gold"),
       T("Avantages des membres : $(av)\\n", "green"), T("Prochain : $(suiv)\\n", "aqua"), T("$(chef)", "gray")) + '}'],
    [btn(L(IC("gold_nugget"), T("  Déposer 1 000", "yellow")), 7701, 130, "Du compte vers le trésor de la guilde."),
     btn(L(IC("gold_ingot"), T("  Déposer 10 000", "yellow")), 7702, 130, "Du compte vers le trésor de la guilde."),
     btn(L(IC("experience_bottle"), T("  Niveau suivant", "green", True)), 7710, 130, "Le chef achète le niveau suivant avec le trésor."),
     btn(L(IC("hopper"), T("  Reprendre 10 000", "white")), 7720, 130, "Le chef reprend 10 000 Écus du trésor (pour payer un membre par exemple)."),
     btn(L(IC("name_tag"), T("  Classement", "gold")), 7730, 130, "Les guildes les plus riches."),
     btn(T("Accueil", "white"), 1, 130)], 3))

# ---------------------------------------------------------------- dépôt, niveau, retrait
for i, v in ((1, 1000), (2, 10000)):
    w(GD + f"depot_{i}.mcfunction", [
        "execute unless score @s m.gid matches 1.. run return run " + say("Tu n’as pas de guilde.", "red"),
        f"execute unless score @s c.ecus matches {v}.. run return run " + say(f"Il te faut {fe(v)} Écus sur ton compte.", "red"),
        f"{S} remove @s c.ecus {v}", f"execute store result storage {NS}:t gg.g int 1 run {S} get @s m.gid",
        f"data modify storage {NS}:t gg.v set value {v}", f"function {NS}:guilde/ajout with storage {NS}:t gg",
        f'tellraw @a {L(PREFIX, "{selector:\"@s\",color:\"white\"}", T(" verse " + fe(v) + " Écus au trésor de sa guilde.", "gold"))}',
        "playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 0.8", f"function {NS}:guilde/page"])
w(GD + "ajout.mcfunction", [
    f"$execute unless data storage {NS}:gt G[{{g:$(g)}}] run data modify storage {NS}:gt G append value {{g:$(g),t:0,n:0}}",
    f"$execute store result score #gt c.t run data get storage {NS}:gt G[{{g:$(g)}}].t",
    "$scoreboard players add #gt c.t $(v)",
    f"$execute store result storage {NS}:gt G[{{g:$(g)}}].t int 1 run {S} get #gt c.t"])
w(GD + "niveau.mcfunction", [
    "execute unless score @s m.gid matches 1.. run return run " + say("Tu n’as pas de guilde.", "red"),
    "execute unless function metiers:guilde/suis_chef run return run " + say("Seul le chef de la guilde achète les niveaux.", "red"),
    f"execute store result storage {NS}:t gg.g int 1 run {S} get @s m.gid", f"function {NS}:guilde/niveau_m with storage {NS}:t gg"])
NV = [f"$execute store result score #gt c.t run data get storage {NS}:gt G[{{g:$(g)}}].t",
      f"$execute store result score #gnv c.t run data get storage {NS}:gt G[{{g:$(g)}}].n",
      "execute if score #gnv c.t matches 5.. run return run " + say("Ta guilde est déjà au niveau maximum.", "yellow")]
for n, c in COUT.items():
    NV += [f"execute if score #gnv c.t matches {n - 1} unless score #gt c.t matches {c}.. run return run " + say(f"Le niveau {n} coûte {fe(c)} Écus : le trésor n’y est pas encore.", "red"),
           f"execute if score #gnv c.t matches {n - 1} run {S} remove #gt c.t {c}"]
NV += ["scoreboard players add #gnv c.t 1",
       f"$execute store result storage {NS}:gt G[{{g:$(g)}}].t int 1 run {S} get #gt c.t",
       f"$execute store result storage {NS}:gt G[{{g:$(g)}}].n int 1 run {S} get #gnv c.t",
       f"execute store result storage {NS}:t gg.n int 1 run {S} get #gnv c.t",
       f"function {NS}:guilde/annonce with storage {NS}:t gg",
       "execute as @a at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 0.8 1.1",
       f"execute as @a run function {NS}:guilde/sync", f"function {NS}:guilde/page"]
w(GD + "niveau_m.mcfunction", NV)
w(GD + "annonce.mcfunction",
  f'$tellraw @a {L(PREFIX, "{selector:\"@s\",color:\"white\"}", T(" fait passer sa guilde au niveau $(n) ! Tous ses membres en profitent.", "gold", True))}')
w(GD + "reprendre.mcfunction", [
    "execute unless score @s m.gid matches 1.. run return run " + say("Tu n’as pas de guilde.", "red"),
    "execute unless function metiers:guilde/suis_chef run return run " + say("Seul le chef de la guilde reprend des Écus du trésor.", "red"),
    f"execute store result storage {NS}:t gg.g int 1 run {S} get @s m.gid", f"function {NS}:guilde/reprendre_m with storage {NS}:t gg"])
w(GD + "reprendre_m.mcfunction", [
    f"$execute store result score #gt c.t run data get storage {NS}:gt G[{{g:$(g)}}].t",
    "execute unless score #gt c.t matches 10000.. run return run " + say("Le trésor n’a pas 10 000 Écus.", "red"),
    "scoreboard players remove #gt c.t 10000", f"$execute store result storage {NS}:gt G[{{g:$(g)}}].t int 1 run {S} get #gt c.t",
    f"{S} add @s c.ecus 10000", say("10 000 Écus repris du trésor de la guilde.", "gold"), f"function {NS}:guilde/page"])

# ---------------------------------------------------------------- classement : 8 guildes les plus riches
CL = [f"data modify storage {NS}:t gc set from storage {NS}:gt G", f'data modify storage {NS}:gp lignes set value ""',
      f"data modify storage {NS}:t gr set value []", f"function {NS}:guilde/classe_tour"]
w(GD + "classement.mcfunction", CL + [f"function {NS}:guilde/classe_affiche"])
# tri par sélection : on retire 8 fois la plus riche
w(GD + "classe_tour.mcfunction", [
    f"execute unless data storage {NS}:t gc[0] run return 0",
    f"execute if data storage {NS}:t gr[7] run return 0",
    f"{S} set #best c.t -1", f"{S} set #bi c.t 0", f"{S} set #i c.t 0",
    f"data modify storage {NS}:t gw set from storage {NS}:t gc", f"function {NS}:guilde/classe_max",
    f"execute store result storage {NS}:t gbi.i int 1 run {S} get #bi c.t",
    f"function {NS}:guilde/classe_prendre with storage {NS}:t gbi", f"function {NS}:guilde/classe_tour"])
w(GD + "classe_max.mcfunction", [
    f"execute unless data storage {NS}:t gw[0] run return 0",
    f"execute store result score #v c.t run data get storage {NS}:t gw[0].t",
    f"execute if score #v c.t > #best c.t run {S} operation #bi c.t = #i c.t",
    f"execute if score #v c.t > #best c.t run {S} operation #best c.t = #v c.t",
    f"data remove storage {NS}:t gw[0]", f"{S} add #i c.t 1", f"function {NS}:guilde/classe_max"])
w(GD + "classe_prendre.mcfunction", [f"$data modify storage {NS}:t gr append from storage {NS}:t gc[$(i)]",
                                     f"$data remove storage {NS}:t gc[$(i)]"])
w(GD + "classe_affiche.mcfunction", [
    f'tellraw @s {L(PREFIX, T("Classement des guildes par trésor :", "gold", True))}',
    f"data modify storage {NS}:t gw set from storage {NS}:t gr", f"{S} set #i c.t 1", f"function {NS}:guilde/classe_ligne"])
w(GD + "classe_ligne.mcfunction", [
    f"execute unless data storage {NS}:t gw[0] run return 0",
    f"execute store result storage {NS}:t gl.r int 1 run {S} get #i c.t",
    f"data modify storage {NS}:t gl.g set from storage {NS}:t gw[0].g", f"data modify storage {NS}:t gl.t set from storage {NS}:t gw[0].t",
    f"data modify storage {NS}:t gl.n set from storage {NS}:t gw[0].n",
    f"function {NS}:guilde/classe_ligne_m with storage {NS}:t gl",
    f"data remove storage {NS}:t gw[0]", f"{S} add #i c.t 1", f"function {NS}:guilde/classe_ligne"])
w(GD + "classe_ligne_m.mcfunction",
  f'$execute if data storage metiers:gu L[{{id:$(g)}}] run tellraw @s [{{text:"  $(r). ",color:"yellow"}},{{storage:"metiers:gu",nbt:"L[{{id:$(g)}}].nomc",interpret:true}},'
  f'{{text:"  niveau $(n) · $(t) Écus",color:"gray"}}]')

# ---------------------------------------------------------------- entrée (déclencheurs 7700 à 7799)
w(GD + "entree.mcfunction", [
    f"execute if score #v c.t matches 7700 run return run function {NS}:guilde/page",
    f"execute if score #v c.t matches 7701 run return run function {NS}:guilde/depot_1",
    f"execute if score #v c.t matches 7702 run return run function {NS}:guilde/depot_2",
    f"execute if score #v c.t matches 7710 run return run function {NS}:guilde/niveau",
    f"execute if score #v c.t matches 7720 run return run function {NS}:guilde/reprendre",
    f"execute if score #v c.t matches 7730 run return run function {NS}:guilde/classement"])

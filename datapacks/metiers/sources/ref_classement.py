# Classement par métier (25/11/2026) : bouton « Classement » dans l'onglet de chaque métier, top 10 du serveur.
# Les données viennent de la table metiers:cl joueurs tenue par classement/maj (joueurs en ligne mis à jour à
# l'ouverture, hors ligne avec leurs dernières valeurs). Valeur triée : prestige x 100 + niveau.
TOPN = 10
w(F + "classement/top10.mcfunction", "\n".join(
    [f"data modify storage {NS}:cl copie set from storage {NS}:cl joueurs", f"data modify storage {NS}:cl res set value []"] +
    [f'$function {NS}:classement/rang {{f:"$(f)"}}'] * TOPN))
for j, d in jobs.items():
    C = [f"execute as @a run function {NS}:classement/maj", f'function {NS}:classement/top10 {{f:"{j}"}}']
    for r in range(TOPN):
        C += [f'data modify storage {NS}:cm n{r} set value {{text:"·",color:"dark_gray"}}',
              f'data modify storage {NS}:cm l{r} set value ""', f'data modify storage {NS}:cm s{r} set value ""',
              f'execute if data storage {NS}:cl res[{r}] run data modify storage {NS}:cm n{r} set value {{text:"joueur hors ligne",color:"gray"}}',
              f"data modify storage {NS}:cm n{r} set from storage {NS}:cl res[{r}].nom",
              f"execute if data storage {NS}:cl res[{r}] run data modify storage {NS}:cm a set value {{r:{r}}}",
              f"execute if data storage {NS}:cl res[{r}] run data modify storage {NS}:cm a.v set from storage {NS}:cl res[{r}].{j}l",
              f"execute if data storage {NS}:cl res[{r}] run function {NS}:classement/niv with storage {NS}:cm a",
              f"data modify storage {NS}:cm s{r} set from storage {NS}:cl res[{r}].{j}st"]
    C.append(f"function {NS}:classement/metier_dialog_{j} with storage {NS}:cm")
    w(F + f"classement/metier_{j}.mcfunction", "\n".join(C))
    MED = {0: "#FFD700", 1: "#C8C8D0", 2: "#CD7F32"}
    lignes = []
    for r in range(TOPN):
        col = MED.get(r, "gray")
        lignes.append(f'{{text:"{r + 1}.  ",color:"{col}",bold:true}},$(n{r}),'
                      f'{{text:"   $(l{r})",color:"yellow",bold:false}},{{text:" $(s{r})\\n",color:"gold",bold:false}}')
    body = ('[{type:"minecraft:plain_message",width:320,contents:[' + ",".join(lignes) + ']},'
            '{type:"minecraft:plain_message",width:320,contents:{text:"Classé par étoiles de prestige puis par niveau. '
            'Les joueurs hors ligne gardent leur dernier score connu.",color:"dark_gray"}}]')
    w(F + f"classement/metier_dialog_{j}.mcfunction",
      f'$dialog show @s {{type:"minecraft:notice",title:[{gs("metier_" + j)},{{text:" Classement {d["name"]}",color:"{d["color"]}",bold:true}}],'
      f'can_close_with_escape:true,pause:false,body:{body},'
      f'action:{{label:"Retour",width:150,action:{{type:"run_command",command:"trigger metiers set {20 + d["idx"]}"}}}}}}')
# « niveau N » du joueur au rang r
w(F + "classement/niv.mcfunction", f'$data modify storage {NS}:cm l$(r) set value "niveau $(v)"')
add_lines(F + "trigger.mcfunction",
          [f'execute if score @s m.trig matches {520 + d["idx"]} run function {NS}:appel {{f:"classement/metier_{j}"}}' for j, d in jobs.items()])

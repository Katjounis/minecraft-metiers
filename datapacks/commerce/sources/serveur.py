# -*- coding: utf-8 -*-
# Menu G unifié, profil du joueur, guide des nouveaux. Exécuté par datapack.py.
#
# Touche G : chaque pack (Métiers, Commerce, Horreur) déclare le MÊME dialogue serveur:menu dans quick_actions ;
# les tags fusionnent une entrée identique, donc G ouvre directement ce menu commun (au lieu d'une liste de packs).
# Le fichier MENU_SERVEUR ci-dessous est recopié tel quel dans les deux autres packs (voir leurs datapack.py).
import json as _json
S = "scoreboard players"
G_ = F + "serveur/"

_ic = lambda i: {"object": "atlas", "atlas": "minecraft:items", "sprite": "minecraft:item/" + i}
MENU_SERVEUR = {
    "type": "minecraft:multi_action",
    "title": {"text": "Les Couillons", "color": "gold", "bold": True},
    "external_title": {"text": "Menu du serveur"},
    "can_close_with_escape": True, "pause": False,
    "body": [{"type": "minecraft:plain_message", "width": 300, "contents": [
        {"text": "Métiers, Commerce, Bestiaire, Compagnons : tout est ici.", "color": "gray"}]}],
    "actions": [
        {"label": [_ic("iron_pickaxe"), {"text": "  Métiers", "color": "aqua", "bold": True}], "width": 150, "tooltip": {"text": "Niveaux, compétences, Forge, défis, classement."},
         "action": {"type": "minecraft:run_command", "command": "trigger metiers set 1"}},
        {"label": [_ic("emerald"), {"text": "  Commerce", "color": "gold", "bold": True}], "width": 150, "tooltip": {"text": "Marché, bourse, banque, hôtel des ventes, spawners."},
         "action": {"type": "minecraft:run_command", "command": "trigger commerce set 1"}},
        {"label": [_ic("bone"), {"text": "  Bestiaire", "color": "dark_red", "bold": True}], "width": 150, "tooltip": {"text": "Les créatures de la nuit, contrats, classement."},
         "action": {"type": "minecraft:run_command", "command": "trigger bestiaire set 1"}},
        {"label": [_ic("lead"), {"text": "  Compagnons", "color": "#E0A040", "bold": True}], "width": 150, "tooltip": {"text": "Loup, chat, golem... qui combattent et progressent avec toi."},
         "action": {"type": "minecraft:run_command", "command": "trigger compagnons set 1"}},
        {"label": [_ic("name_tag"), {"text": "  Mon profil", "color": "yellow", "bold": True}], "width": 150, "tooltip": {"text": "Tout ton parcours sur une page."},
         "action": {"type": "minecraft:run_command", "command": "trigger commerce set 30"}},
        {"label": [_ic("book"), {"text": "  Guide", "color": "white"}], "width": 150, "tooltip": {"text": "Pour bien démarrer, en 5 pages."},
         "action": {"type": "minecraft:run_command", "command": "trigger commerce set 31"}}],
    "columns": 2}
wj("data/serveur/dialog/menu.json", MENU_SERVEUR)
wj("data/minecraft/tags/dialog/quick_actions.json", {"values": ["serveur:menu"]})
wj("data/minecraft/tags/dialog/pause_screen_additions.json", {"values": ["serveur:menu"]})
# copie pour les autres packs (lue par leurs générateurs)
_json.dump(MENU_SERVEUR, open(os.path.join(HERE, "menu_serveur.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- profil (30)
PJ = [("b", "Bûcheron", "gold"), ("f", "Fermier", "green"), ("m", "Mineur", "gray"), ("c", "Chasseur", "red"),
      ("p", "Pêcheur", "aqua"), ("e", "Éleveur", "light_purple"), ("n", "Enchanteur", "dark_purple"),
      ("x", "Explorateur", "blue"), ("t", "Marchand", "dark_green"), ("k", "Bâtisseur", "#C08850")]
PR = SOLDE(f"{NS}:pf") + [f"execute store result storage {NS}:pf ep int 1 run scoreboard players get @s c.ep",
                          f"execute store result storage {NS}:pf tv int 1 run scoreboard players get @s c.tv",
                          f"execute store result storage {NS}:pf ta int 1 run scoreboard players get @s c.ta",
                          f"data modify storage {NS}:pf hr set value 0", f"execute store result storage {NS}:pf hr int 1 run scoreboard players get @s hr.tot",
                          f"{S} set #tl c.t 0"]
for j, nom, col in PJ:
    PR += [f"data modify storage {NS}:pf {j} set value 0",
           f"execute store result storage {NS}:pf {j} int 1 run scoreboard players get @s m.{j}_lvl",
           f'data modify storage {NS}:pf s{j} set value ""'] + [
           f'execute if score @s m.{j}_pr matches {n} run data modify storage {NS}:pf s{j} set value " {"★" * n}"' for n in range(1, 6)] + [
           f"scoreboard players operation #tl c.t += @s m.{j}_lvl", "scoreboard players set #x c.t 0", f"scoreboard players operation #x c.t = @s m.{j}_pr",
           "scoreboard players operation #x c.t *= #100 c.g", "scoreboard players operation #tl c.t += #x c.t"]
PR += [f"execute store result storage {NS}:pf tl int 1 run scoreboard players get #tl c.t", f"function {NS}:joueur/nom_moi",
       f"data modify storage {NS}:pf nom set from storage {NS}:t moi", f"function {NS}:serveur/profil_d with storage {NS}:pf"]
w(G_ + "profil.mcfunction", PR)
lig = []
for k, (j, nom, col) in enumerate(PJ):
    lig += [T(f"{nom} ", col, True), T(f"$({j})", "white"), T(f"$(s{j})", "gold"), T("\\n" if k % 2 else "      ", "white")]
w(G_ + "profil_d.mcfunction", "$" + dlg(
    T("Profil de $(nom)", "yellow", True),
    [f'{{type:"minecraft:plain_message",width:330,contents:{L(T("Métiers", "aqua", True), T("   niveau total $(tl) (100 par étoile de prestige)\\n", "gray"), *lig)}}}',
     f'{{type:"minecraft:plain_message",width:330,contents:{L(T("Commerce\\n", "gold", True), SOLDE_TXT, T("   ·   épargne $(ep) " + ECU, "aqua"), T("\\nVendu en tout : $(tv) " + ECU + "   ·   acheté : $(ta) " + ECU, "gray"))}}}',
     f'{{type:"minecraft:plain_message",width:330,contents:{L(T("Bestiaire\\n", "dark_red", True), T("$(hr) créatures vaincues", "gray"))}}}'],
    [btn(T("Commerce", "gold"), 1, 110), btn(T("Banque", "yellow"), 90, 110), btn(T("Guide", "white"), 31, 110)], 3))

# ---------------------------------------------------------------- guide (31 à 35)
GUIDE = [
    ("Bienvenue", "Bienvenue sur le serveur ! Trois packs maison tournent ici, sans mod. La touche G ouvre le menu commun à tout moment (ou Échap, puis le bouton du serveur).\\n\\nCe guide fait 5 pages : Métiers, Commerce, Bestiaire, puis quelques astuces."),
    ("Métiers", "Tu progresses dans 10 métiers juste en jouant : couper du bois, miner, pêcher, chasser, construire... Chaque niveau donne un point de compétence, chaque palier de 10 niveaux un meilleur outil de métier (à récupérer dès le niveau 10).\\n\\nLa Forge échange tes cristaux contre des améliorations et des objets uniques. Au niveau 100, le prestige garde tout et ajoute une étoile et une capacité.\\n\\nG, Métiers, Barème d’XP : ce que rapporte chaque action."),
    ("Commerce", "Crafte l’oeuf de comptoir pour ouvrir le Commerce. Tu vends tes récoltes, tu achètes des blocs, les prix bougent avec l’offre et la demande.\\n\\nLa banque fait les virements et l’épargne (2 % par semaine). L’hôtel des ventes vend les objets entre joueurs. Un panneau [Privé] protège un coffre, un panneau [Vente] en fait un magasin. Ton solde est toujours en haut à gauche."),
    ("Bestiaire", "La nuit et sous terre, des créatures rôdent : Slender, Herobrine, la Nonne, le Loup-garou les nuits de pleine lune... Un message te prévient quand l’une d’elles approche.\\n\\nChaque victoire paie une prime en Écus et remplit le bestiaire (trophée à 10 victoires, titre à 50, relique à 100). Une nuit sur huit, la Nuit de sang les rend quatre fois plus nombreuses."),
    ("Astuces", "Les boss du serveur arrivent régulièrement près d’un joueur au hasard : tout le monde peut participer et gagner des éclats.\\n\\nLes compagnons (G, Compagnons) se débloquent avec tes métiers : un loup dès Chasseur 10, puis chat, perroquet, bonhomme de neige, allay et golem. Ils se battent avec toi et gagnent leurs propres niveaux.\\n\\nTon profil (G, Mon profil) résume tout ton parcours. Les classements sont dans chaque menu.\\n\\nUn souci ? Préviens un admin. Bon jeu !"),
]
for i, (titre, texte) in enumerate(GUIDE):
    acts = []
    acts.append(btn(T("◀  Précédent", "white"), 31 + i - 1, 140) if i else btn(T("Fermer", "gray"), 0, 140))
    acts.append(btn(T("Suivant  ▶", "yellow", True), 31 + i + 1, 140) if i < len(GUIDE) - 1 else btn(T("Mon profil", "yellow", True), 30, 140))
    w(G_ + f"guide_{i + 1}.mcfunction", dlg(
        T(f"Guide {i + 1}/{len(GUIDE)} : {titre}", "gold", True),
        [f'{{type:"minecraft:plain_message",width:320,contents:{L(T(texte, "white"))}}}'], acts, 2))
# première connexion : le guide s'ouvre tout seul (une fois)
w(G_ + "bienvenue.mcfunction", [f"function {NS}:serveur/guide_1", "scoreboard players set @s c.gd 1"])

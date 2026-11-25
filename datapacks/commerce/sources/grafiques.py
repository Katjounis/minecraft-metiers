# -*- coding: utf-8 -*-
# Statistiques et graphiques du marché. Exécuté par datapack.py (partage w, F, NS, ITL, H, T, L, dlg, btn, btn_cmd, fmt, RP...).
#
# Données suivies
#   par objet : c.jv / c.ja = quantités vendues / achetées aujourd'hui, c.vs / c.as = cette semaine (déjà là)
#   storage commerce:hj  v_<id>, a_<id> (quantités), p_<id> (cours de fin de journée) : 13 jours passés
#   storage commerce:hs  v_<id>, a_<id> : 7 semaines passées
#   global : #jvE / #jaE (Écus de ventes / d'achats du jour), #svE / #saE (de la semaine), listes _v et _a
#   Le « jour » et la « semaine » sont ceux des défis de Métiers (24 min et 7 jours de jeu, joueurs connectés).
#
# Dessin : police commerce:graph. Une courbe est une suite de colonnes de 9 px, chacune un segment entre deux
# hauteurs (16 x 16 glyphes) avec l'aire dessous ; un histogramme, des barres de 4 px (16 hauteurs).
# Chaque colonne porte une infobulle (valeur) et, pour les jours, un clic qui ouvre le détail du jour.
# Sous le graphique, une rangée de repères (heures, jours, semaines) avec les mêmes infobulles et clics.
from PIL import Image, ImageDraw

GF = "commerce:graph"
GH, SS = 45, 2                 # hauteur du graphique en pixels d'interface, échelle de la texture
NJ, NS_ = 13, 7                # jours et semaines passés gardés (plus le jour / la semaine en cours)
SEG = lambda a, b: chr(0xE400 + a * 16 + b)
BAR = lambda l: chr(0xE500 + l)
NEG1, GAP3 = "", ""
AXL = lambda n: chr(0xE520 + n)     # repère 9 px avec nombre
AXT = ""                      # repère 9 px sans nombre
AXB = lambda n: chr(0xE560 + n)     # repère 13 px (un jour d'histogramme) avec nombre
GDIR = os.path.join(RP, "textures", "font")


def yl(lv):
    """Hauteur (en px de texture) du niveau 0..15 : 0 en bas (y = 42), 15 en haut (y = 4)."""
    return (GH - 3 - lv * (GH - 7) / 15) * SS


def dessiner():
    # segments de courbe : 9 px d'interface, dessinés en x4 puis réduits (trait lissé)
    W = 9 * SS; HH = GH * SS; K = 4
    seg = Image.new("RGBA", (W * 16, HH * 16), (0, 0, 0, 0))
    for a in range(16):
        for b in range(16):
            big = Image.new("RGBA", (W * K, HH * K), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
            ya, yb, base = yl(a) * K, yl(b) * K, (GH - 1) * SS * K
            d.polygon([(0, ya), (W * K, yb), (W * K, base), (0, base)], fill=(255, 255, 255, 46))
            for gy in (yl(7.5) * K, yl(15) * K):
                for x in range(0, W * K, 4 * K):
                    d.rectangle([x, gy, x + K * 2 - 1, gy + K - 1], fill=(255, 255, 255, 40))
            d.line([(0, ya), (W * K, yb)], fill=(255, 255, 255, 255), width=K * 2)
            c = big.resize((W, HH), Image.LANCZOS)
            d2 = ImageDraw.Draw(c)
            d2.rectangle([0, (GH - 1) * SS, W - 1, GH * SS - 1], fill=(255, 255, 255, 110))   # axe
            seg.paste(c, (b * W, a * HH))
    seg.save(os.path.join(GDIR, "graph_seg.png"))
    # barres : 4 px d'interface (avance 5), 16 hauteurs, chapeau plus opaque
    W = 4 * SS
    bar = Image.new("RGBA", (W * 16, HH), (0, 0, 0, 0)); d = ImageDraw.Draw(bar)
    for lv in range(16):
        x0 = lv * W
        top = yl(lv) if lv else (GH - 2) * SS
        d.rectangle([x0, top, x0 + W - 1, (GH - 1) * SS - 1], fill=(255, 255, 255, 190))
        d.rectangle([x0, top, x0 + W - 1, top + SS - 1], fill=(255, 255, 255, 255))
        d.rectangle([x0, (GH - 1) * SS, x0 + W - 1, GH * SS - 1], fill=(255, 255, 255, 110))
    bar.save(os.path.join(GDIR, "graph_bar.png"))
    # repères : chiffres 3 x 5 (1 px d'interface = 2 px de texture)
    DG = ["111101101101111", "010110010010111", "111001111100111", "111001111001111", "101101111001001",
          "111100111001111", "111100111101111", "111001001010010", "111101111101111", "111101111001111"]

    def repere(wd, n):
        im = Image.new("RGBA", (wd * SS, 9 * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        cx = wd // 2
        d.rectangle([cx * SS - SS // 2, 0, cx * SS + SS // 2 - 1, 2 * SS - 1], fill=(255, 255, 255, 200))
        if n is not None:
            s = str(n); lw = len(s) * 4 - 1; x = cx - lw // 2
            for ch in s:
                bits = DG[int(ch)]
                for r in range(5):
                    for cc in range(3):
                        if bits[r * 3 + cc] == "1":
                            d.rectangle([(x + cc) * SS, (3 + r) * SS, (x + cc) * SS + SS - 1, (3 + r) * SS + SS - 1], fill=(255, 255, 255, 255))
                x += 4
        im.putpixel((wd * SS - 1, 9 * SS - 1), (255, 255, 255, 1))     # largeur fixe
        return im
    axl = Image.new("RGBA", (8 * SS * 32, 9 * SS), (0, 0, 0, 0))
    for n in range(32):
        axl.paste(repere(8, n), (n * 8 * SS, 0))
    axl.save(os.path.join(GDIR, "graph_axl.png"))
    repere(8, None).save(os.path.join(GDIR, "graph_axt.png"))
    axb = Image.new("RGBA", (12 * SS * 32, 9 * SS), (0, 0, 0, 0))
    for n in range(32):
        axb.paste(repere(12, n), (n * 12 * SS, 0))
    axb.save(os.path.join(GDIR, "graph_axb.png"))
    json.dump({"providers": [
        {"type": "bitmap", "file": "commerce:font/graph_seg.png", "height": GH, "ascent": 7,
         "chars": ["".join(SEG(a, b) for b in range(16)) for a in range(16)]},
        {"type": "bitmap", "file": "commerce:font/graph_bar.png", "height": GH, "ascent": 7, "chars": ["".join(BAR(l) for l in range(16))]},
        {"type": "bitmap", "file": "commerce:font/graph_axl.png", "height": 9, "ascent": 7, "chars": ["".join(AXL(n) for n in range(32))]},
        {"type": "bitmap", "file": "commerce:font/graph_axt.png", "height": 9, "ascent": 7, "chars": [AXT]},
        {"type": "bitmap", "file": "commerce:font/graph_axb.png", "height": 9, "ascent": 7, "chars": ["".join(AXB(n) for n in range(32))]},
        {"type": "space", "advances": {NEG1: -1, GAP3: 3}}]},
        open(os.path.join(RP, "font", "graph.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


dessiner()
GR = f"{NS}:gr"
GL = f"{NS}:gl"
S = "scoreboard players"

# ---------------------------------------------------------------- chargement
lst = lambda xs: "[" + ",".join(f'"{x}"' for x in xs) + "]"
w(F + "stat/load.mcfunction", [
    "scoreboard objectives add c.y dummy", "scoreboard objectives add c.dv dummy", "scoreboard objectives add c.da dummy",
    f"{S} set #3 c.g 3", f"{S} set #15 c.g 15", f"{S} set #16 c.g 16",
    f"{S} add #jvE c.g 0", f"{S} add #jaE c.g 0", f"{S} add #svE c.g 0", f"{S} add #saE c.g 0", f"{S} add #jp c.g 0",
    f"data modify storage {GL} SEG set value {lst(SEG(a, b) for a in range(16) for b in range(16))}",
    f"data modify storage {GL} BAR set value {lst(BAR(l) for l in range(16))}",
    f"data modify storage {GL} AXL set value {lst(AXL(n) if n % 3 == 0 else AXT for n in range(32))}",
    f"data modify storage {GL} AXJ set value {lst(AXL(n) for n in range(32))}",
    f"data modify storage {GL} AXB set value {lst(AXB(n) for n in range(32))}"]
    + [f"{S} add {H(it)} {o} 0" for it in ITL for o in ("c.jv", "c.ja")])

# ---------------------------------------------------------------- suivi des ventes et achats (appelé par op/vendre, op/acheter)
w(F + "stat/vente.mcfunction", [
    f"$scoreboard players operation #$(id) c.jv += #q c.t",
    "scoreboard players operation #x c.t = #tot c.t", "scoreboard players operation #x c.t /= #100 c.g",
    "scoreboard players operation #jvE c.g += #x c.t", "scoreboard players operation #svE c.g += #x c.t"])
w(F + "stat/achat.mcfunction", [
    f"$scoreboard players operation #$(id) c.ja += #q c.t",
    "scoreboard players operation #jaE c.g += #ce c.t", "scoreboard players operation #saE c.g += #ce c.t"])


def garder(st, key, src_cmd, n):
    return [f"data modify storage {st} {key} append value 0",
            f"execute store result storage {st} {key}[-1] int 1 run {src_cmd}",
            f"execute if data storage {st} {key}[{n}] run data remove storage {st} {key}[0]"]


# nouveau jour (Métiers remet #jour m.defi à zéro) : on archive les compteurs du jour
J = []
for it in ITL:
    i = it["id"]
    J += garder(f"{NS}:hj", f"v_{i}", f"scoreboard players get {H(it)} c.jv", NJ)
    J += garder(f"{NS}:hj", f"a_{i}", f"scoreboard players get {H(it)} c.ja", NJ)
    J += [f"data modify storage {NS}:hj p_{i} append value 0",
          f"execute store result storage {NS}:hj p_{i}[-1] int 1 run data get storage {NS}:hist {i}[-1]",
          f"execute if data storage {NS}:hj p_{i}[{NJ}] run data remove storage {NS}:hj p_{i}[0]",
          f"{S} set {H(it)} c.jv 0", f"{S} set {H(it)} c.ja 0"]
J += garder(f"{NS}:hj", "_v", f"scoreboard players get #jvE c.g", NJ) + garder(f"{NS}:hj", "_a", f"scoreboard players get #jaE c.g", NJ)
J += [f"{S} set #jvE c.g 0", f"{S} set #jaE c.g 0"]
w(F + "stat/jour.mcfunction", J)
SM = []
for it in ITL:
    SM += garder(f"{NS}:hs", f"v_{it['id']}", f"scoreboard players get {H(it)} c.vs", NS_)
    SM += garder(f"{NS}:hs", f"a_{it['id']}", f"scoreboard players get {H(it)} c.as", NS_)
SM += garder(f"{NS}:hs", "_v", "scoreboard players get #svE c.g", NS_) + garder(f"{NS}:hs", "_a", "scoreboard players get #saE c.g", NS_)
SM += [f"{S} set #svE c.g 0", f"{S} set #saE c.g 0"]
w(F + "stat/semaine.mcfunction", SM)
# appelé chaque seconde
w(F + "stat/seconde.mcfunction", [
    "scoreboard players operation #jc c.t = #jp c.g",
    "execute store result score #jp c.g run scoreboard players get #jour m.defi",
    f"execute if score #jp c.g < #jc c.t run function {NS}:stat/jour"])

# ---------------------------------------------------------------- outils de dessin
# valeur #x -> texte gr.v selon gr.fk : p = centièmes d'Écu, i = indice en millièmes, n = entier
w(F + "gr/val.mcfunction", [
    f'execute if data storage {GR} {{fk:"p"}} run return run function {NS}:gr/val_p',
    f'execute if data storage {GR} {{fk:"i"}} run return run function {NS}:gr/val_i',
    f"execute store result storage {GR} f.e int 1 run scoreboard players get #x c.t",
    f"function {NS}:gr/val_n with storage {GR} f"])
w(F + "gr/val_n.mcfunction", f'$data modify storage {GR} v set value "$(e)"')
w(F + "gr/val_p.mcfunction", fmt(f"{GR}", "f.") + [f"function {NS}:gr/val_pm with storage {GR} f"])
w(F + "gr/val_pm.mcfunction", f'$data modify storage {GR} v set value "$(e),$(z)$(c) Écus"')
w(F + "gr/val_i.mcfunction", [
    "scoreboard players operation #fe c.t = #x c.t", "scoreboard players operation #fe c.t /= #10 c.g",
    "scoreboard players operation #fc c.t = #x c.t", "scoreboard players operation #fc c.t %= #10 c.g",
    f"execute store result storage {GR} f.e int 1 run scoreboard players get #fe c.t",
    f"execute store result storage {GR} f.c int 1 run scoreboard players get #fc c.t",
    f"function {NS}:gr/val_im with storage {GR} f"])
w(F + "gr/val_im.mcfunction", f'$data modify storage {GR} v set value "$(e),$(c) %"')
# libellé de l'abscisse : #ago -> gr.lab
w(F + "gr/lab.mcfunction", [
    f"execute if score #ago c.t matches 0 run return run data modify storage {GR} lab set from storage {GR} u0",
    f"execute store result storage {GR} n int 1 run scoreboard players get #ago c.t",
    f"function {NS}:gr/lab_m with storage {GR}"])
w(F + "gr/lab_m.mcfunction", f'$data modify storage {GR} lab set value "il y a $(n) $(u)"')
# niveau 0..15 de #x entre #hmin et #hmax -> #lv
w(F + "gr/niveau.mcfunction", [
    "scoreboard players set #lv c.t 7",
    "execute if score #gsp c.t matches ..0 run return 0",
    "scoreboard players operation #lv c.t = #x c.t", "scoreboard players operation #lv c.t -= #hmin c.t",
    "scoreboard players operation #lv c.t *= #15 c.g", "scoreboard players operation #lv c.t /= #gsp c.t"])
w(F + "gr/niveau_b.mcfunction", [
    "scoreboard players set #lv c.t 0",
    "execute if score #hmax c.t matches ..0 run return 0",
    "scoreboard players operation #lv c.t = #x c.t", "scoreboard players operation #lv c.t *= #15 c.g",
    "scoreboard players operation #lv c.t /= #hmax c.t",
    "execute if score #x c.t matches 1.. if score #lv c.t matches 0 run scoreboard players set #lv c.t 1",
    "execute if score #lv c.t matches 16.. run scoreboard players set #lv c.t 15"])
w(F + "gr/pioche.mcfunction", [
    f"$data modify storage {GR} a.ch set from storage {GL} $(t)[$(k)]"])

HOV = '{action:"show_text",value:[{text:"$(lab)\\n",color:"gray"},{text:"$(v)",color:"gold",bold:true}]}'
HOV2 = '{action:"show_text",value:[{text:"$(lab)\\n",color:"gray"},{text:"$(v1) $(w1)\\n",color:"$(c1)",bold:true},{text:"$(v2) $(w2)",color:"$(c2)",bold:true}]}'
CLK = ',click_event:{action:"run_command",command:"trigger commerce set $(c)"}'
for suf, clk in (("", ""), ("_c", CLK)):
    w(F + f"gr/app{suf}.mcfunction", [
        f'$data modify storage {GR} SP append value {{text:"$(ch){NEG1}",font:"{GF}",color:"$(col)",shadow_color:0,hover_event:{HOV}{clk}}}',
        f'$data modify storage {GR} AX append value {{text:"$(ax)",font:"{GF}",color:"gray",shadow_color:0,hover_event:{HOV}{clk}}}'])
    w(F + f"gr/app2{suf}.mcfunction", [
        f'$data modify storage {GR} SP append value {{text:"$(b1)",font:"{GF}",color:"$(c1)",shadow_color:0,hover_event:{HOV2}{clk}}}',
        f'$data modify storage {GR} SP append value {{text:"$(b2)",font:"{GF}",color:"$(c2)",shadow_color:0,hover_event:{HOV2}{clk}}}',
        f'data modify storage {GR} SP append value {{text:"{GAP3}",font:"{GF}"}}',
        f'$data modify storage {GR} AX append value {{text:"$(ax)",font:"{GF}",color:"gray",shadow_color:0,hover_event:{HOV2}{clk}}}'])

# courbe : gr.G (entiers), gr.fk, gr.col, gr.u, gr.u0, gr.axt ("AXL" ou "AXJ"), gr.clk (0 = pas de clic)
VIDE_G = f'[{{text:"pas encore assez de relevés : la courbe se remplit avec le temps",color:"dark_gray",italic:true}}]'
w(F + "gr/ligne.mcfunction", [
    f'data modify storage {GR} SP set value [{{text:""}}]', f'data modify storage {GR} AX set value [{{text:""}}]',
    f'data modify storage {GR} mx set value "·"', f'data modify storage {GR} mn set value "·"',
    f"execute store result score #gn c.t run data get storage {GR} G",
    f"execute if score #gn c.t matches ..1 run return run data modify storage {GR} SP set value {VIDE_G}",
    "scoreboard players set #hmin c.t 2147483647", "scoreboard players set #hmax c.t -2147483648",
    f"data modify storage {NS}:t W2 set from storage {GR} G", f"function {NS}:hist/minmax",
    "scoreboard players operation #gsp c.t = #hmax c.t", "scoreboard players operation #gsp c.t -= #hmin c.t",
    "scoreboard players operation #x c.t = #hmax c.t", f"function {NS}:gr/val", f"data modify storage {GR} mx set from storage {GR} v",
    "scoreboard players operation #x c.t = #hmin c.t", f"function {NS}:gr/val", f"data modify storage {GR} mn set from storage {GR} v",
    f"data modify storage {GR} W set from storage {GR} G",
    f"execute store result score #x c.t run data get storage {GR} W[0]", f"function {NS}:gr/niveau",
    "scoreboard players operation #gl c.t = #lv c.t", f"data remove storage {GR} W[0]", "scoreboard players set #gk c.t 1",
    f"execute store result score #gclk c.t run data get storage {GR} clk",
    f"function {NS}:gr/ligne_pas"])
w(F + "gr/ligne_pas.mcfunction", [
    f"execute unless data storage {GR} W[0] run return 0",
    f"execute store result score #x c.t run data get storage {GR} W[0]", f"function {NS}:gr/niveau",
    f"function {NS}:gr/val",
    "scoreboard players operation #ago c.t = #gn c.t", "scoreboard players remove #ago c.t 1",
    "scoreboard players operation #ago c.t -= #gk c.t", f"function {NS}:gr/lab",
    f"data modify storage {GR} a set value {{}}",
    f"data modify storage {GR} a.v set from storage {GR} v", f"data modify storage {GR} a.lab set from storage {GR} lab",
    f"data modify storage {GR} a.col set from storage {GR} col",
    "scoreboard players operation #k c.t = #gl c.t", "scoreboard players operation #k c.t *= #16 c.g",
    "scoreboard players operation #k c.t += #lv c.t",
    f"execute store result storage {GR} a.k int 1 run scoreboard players get #k c.t",
    f'data modify storage {GR} a.t set value "SEG"', f"function {NS}:gr/pioche with storage {GR} a",
    f"data modify storage {GR} a.ch2 set from storage {GR} a.ch",
    f"execute store result storage {GR} a.k int 1 run scoreboard players get #ago c.t",
    f"data modify storage {GR} a.t set from storage {GR} axt", f"function {NS}:gr/pioche with storage {GR} a",
    f"data modify storage {GR} a.ax set from storage {GR} a.ch", f"data modify storage {GR} a.ch set from storage {GR} a.ch2",
    "scoreboard players operation #c c.t = #ago c.t", "scoreboard players operation #c c.t *= #1000 c.g",
    "scoreboard players operation #c c.t += #gclk c.t",
    f"execute store result storage {GR} a.c int 1 run scoreboard players get #c c.t",
    f"execute if score #gclk c.t matches 1.. run function {NS}:gr/app_c with storage {GR} a",
    f"execute unless score #gclk c.t matches 1.. run function {NS}:gr/app with storage {GR} a",
    "scoreboard players operation #gl c.t = #lv c.t", "scoreboard players add #gk c.t 1",
    f"data remove storage {GR} W[0]", f"function {NS}:gr/ligne_pas"])

# histogramme : gr.G1 / gr.G2 (même longueur), gr.c1, gr.c2, gr.w1, gr.w2, gr.u, gr.u0, gr.clk
w(F + "gr/barres.mcfunction", [
    f'data modify storage {GR} SP set value [{{text:""}}]', f'data modify storage {GR} AX set value [{{text:""}}]',
    f'data modify storage {GR} fk set value "n"',
    f"execute store result score #gn c.t run data get storage {GR} G1",
    "scoreboard players set #hmin c.t 2147483647", "scoreboard players set #hmax c.t 0",
    f"data modify storage {NS}:t W2 set from storage {GR} G1", f"function {NS}:hist/minmax",
    f"data modify storage {NS}:t W2 set from storage {GR} G2", f"function {NS}:hist/minmax",
    "scoreboard players operation #x c.t = #hmax c.t", f"function {NS}:gr/val", f"data modify storage {GR} mx set from storage {GR} v",
    f"data modify storage {GR} W1 set from storage {GR} G1", f"data modify storage {GR} W2 set from storage {GR} G2",
    "scoreboard players set #gk c.t 0",
    f"execute store result score #gclk c.t run data get storage {GR} clk",
    f"function {NS}:gr/barres_pas"])
w(F + "gr/barres_pas.mcfunction", [
    f"execute unless data storage {GR} W1[0] run return 0",
    f"data modify storage {GR} a set value {{}}",
    f"data modify storage {GR} a.c1 set from storage {GR} c1", f"data modify storage {GR} a.c2 set from storage {GR} c2",
    f"data modify storage {GR} a.w1 set from storage {GR} w1", f"data modify storage {GR} a.w2 set from storage {GR} w2",
    f'data modify storage {GR} a.t set value "BAR"',
    f"execute store result score #x c.t run data get storage {GR} W1[0]", f"function {NS}:gr/niveau_b", f"function {NS}:gr/val",
    f"data modify storage {GR} a.v1 set from storage {GR} v",
    f"execute store result storage {GR} a.k int 1 run scoreboard players get #lv c.t", f"function {NS}:gr/pioche with storage {GR} a",
    f"data modify storage {GR} a.b1 set from storage {GR} a.ch",
    f"execute store result score #x c.t run data get storage {GR} W2[0]", f"function {NS}:gr/niveau_b", f"function {NS}:gr/val",
    f"data modify storage {GR} a.v2 set from storage {GR} v",
    f"execute store result storage {GR} a.k int 1 run scoreboard players get #lv c.t", f"function {NS}:gr/pioche with storage {GR} a",
    f"data modify storage {GR} a.b2 set from storage {GR} a.ch",
    "scoreboard players operation #ago c.t = #gn c.t", "scoreboard players remove #ago c.t 1",
    "scoreboard players operation #ago c.t -= #gk c.t", f"function {NS}:gr/lab",
    f"data modify storage {GR} a.lab set from storage {GR} lab",
    f"execute store result storage {GR} a.k int 1 run scoreboard players get #ago c.t",
    f'data modify storage {GR} a.t set value "AXB"', f"function {NS}:gr/pioche with storage {GR} a",
    f"data modify storage {GR} a.ax set from storage {GR} a.ch",
    "scoreboard players operation #c c.t = #ago c.t", "scoreboard players operation #c c.t *= #1000 c.g",
    "scoreboard players operation #c c.t += #gclk c.t",
    f"execute store result storage {GR} a.c int 1 run scoreboard players get #c c.t",
    f"execute if score #gclk c.t matches 1.. run function {NS}:gr/app2_c with storage {GR} a",
    f"execute unless score #gclk c.t matches 1.. run function {NS}:gr/app2 with storage {GR} a",
    "scoreboard players add #gk c.t 1",
    f"data remove storage {GR} W1[0]", f"data remove storage {GR} W2[0]", f"function {NS}:gr/barres_pas"])

# ---------------------------------------------------------------- graphiques d'un objet : 4000000 + vue x 1000 + objet
VUES = [(1, "Cours 24 h"), (2, "Cours 14 jours"), (3, "Ventes par jour"), (4, "Ventes par semaine")]
C_V, C_A = "#F2B33D", "#5BC8E8"
w(F + "stat/item_entree.mcfunction", [
    "scoreboard players operation #gv c.t = #v c.t", "scoreboard players operation #gv c.t /= #1000 c.g",
    "scoreboard players operation #gv c.t %= #1000 c.g",
    "scoreboard players operation #i c.t = #v c.t", "scoreboard players operation #i c.t %= #1000 c.g",
    f"execute unless score #i c.t matches 1..{len(ITL)} run return 0",
    "execute unless score #gv c.t matches 1..4 run scoreboard players set #gv c.t 1",
    f"function {NS}:stat/item"])
IT = [f"function {NS}:item/charger", f"data modify storage {GR} p set from storage {NS}:t it",
      f"execute store result storage {GR} p.i int 1 run scoreboard players get #i c.t",
      "scoreboard players operation #x c.t = #i c.t", "scoreboard players add #x c.t 10000",
      f"execute store result storage {GR} p.ri int 1 run scoreboard players get #x c.t"]
for v, _ in VUES:
    IT += [f'data modify storage {GR} p.k{v} set value "white"',
           f'execute if score #gv c.t matches {v} run data modify storage {GR} p.k{v} set value "gold"',
           "scoreboard players operation #x c.t = #i c.t", f"scoreboard players add #x c.t {4000000 + v * 1000}",
           f"execute store result storage {GR} p.g{v} int 1 run scoreboard players get #x c.t"]
IT += ["scoreboard players operation #x c.t = #i c.t", "scoreboard players add #x c.t 5000000",
       f"execute store result storage {GR} clkj int 1 run scoreboard players get #x c.t"]
for v, _ in VUES:
    IT.append(f"execute if score #gv c.t matches {v} run function {NS}:stat/item_v{v} with storage {NS}:t it")
IT += [f"data modify storage {GR} p.sp set from storage {GR} SP", f"data modify storage {GR} p.ax set from storage {GR} AX",
       f"data modify storage {GR} p.mx set from storage {GR} mx", f"data modify storage {GR} p.mn set from storage {GR} mn",
       f"data modify storage {GR} p.ti set from storage {GR} ti", f"data modify storage {GR} p.lg set from storage {GR} lg",
       f"function {NS}:stat/item_d with storage {GR} p"]
w(F + "stat/item.mcfunction", IT)
COUL = [f'data modify storage {GR} c1 set value "{C_V}"', f'data modify storage {GR} c2 set value "{C_A}"',
        f'data modify storage {GR} w1 set value "vendus"', f'data modify storage {GR} w2 set value "achetés"']
LIGNE_LG = 'data modify storage commerce:gr lg set value "survole les repères sous la courbe"'
w(F + "stat/item_v1.mcfunction", [
    f"data modify storage {GR} G set value []", f"$data modify storage {GR} G set from storage {NS}:hist $(id)",
    f'data modify storage {GR} fk set value "p"', f'data modify storage {GR} col set value "#7BD88F"',
    f'data modify storage {GR} u set value "h"', f'data modify storage {GR} u0 set value "dernier relevé"',
    f'data modify storage {GR} axt set value "AXL"', f"data modify storage {GR} clk set value 0",
    f'data modify storage {GR} ti set value "Cours sur 24 h (un relevé par heure de jeu)"', LIGNE_LG,
    f"function {NS}:gr/ligne"])
w(F + "stat/item_v2.mcfunction", [
    f"data modify storage {GR} G set value []", f"$data modify storage {GR} G set from storage {NS}:hj p_$(id)",
    f"$data modify storage {GR} G append from storage {NS}:hist $(id)[-1]",
    f'data modify storage {GR} fk set value "p"', f'data modify storage {GR} col set value "#7BD88F"',
    f'data modify storage {GR} u set value "j"', f'data modify storage {GR} u0 set value "aujourd’hui"',
    f'data modify storage {GR} axt set value "AXJ"', f"data modify storage {GR} clk set from storage {GR} clkj",
    f'data modify storage {GR} ti set value "Cours en fin de journée, 14 jours"',
    f'data modify storage {GR} lg set value "clique un repère pour le détail du jour"',
    f"function {NS}:gr/ligne"])
w(F + "stat/item_v3.mcfunction", [
    f"data modify storage {GR} G1 set value []", f"data modify storage {GR} G2 set value []",
    f"$data modify storage {GR} G1 set from storage {NS}:hj v_$(id)", f"$data modify storage {GR} G2 set from storage {NS}:hj a_$(id)",
    f"data modify storage {GR} G1 append value 0", f"data modify storage {GR} G2 append value 0",
    f"$execute store result storage {GR} G1[-1] int 1 run scoreboard players get #$(id) c.jv",
    f"$execute store result storage {GR} G2[-1] int 1 run scoreboard players get #$(id) c.ja"] + COUL + [
    f'data modify storage {GR} u set value "j"', f'data modify storage {GR} u0 set value "aujourd’hui"',
    f"data modify storage {GR} clk set from storage {GR} clkj",
    f'data modify storage {GR} ti set value "Quantités échangées par jour"',
    f'data modify storage {GR} lg set value "clique un jour pour son détail"',
    f"function {NS}:gr/barres"])
w(F + "stat/item_v4.mcfunction", [
    f"data modify storage {GR} G1 set value []", f"data modify storage {GR} G2 set value []",
    f"$data modify storage {GR} G1 set from storage {NS}:hs v_$(id)", f"$data modify storage {GR} G2 set from storage {NS}:hs a_$(id)",
    f"data modify storage {GR} G1 append value 0", f"data modify storage {GR} G2 append value 0",
    f"$execute store result storage {GR} G1[-1] int 1 run scoreboard players get #$(id) c.vs",
    f"$execute store result storage {GR} G2[-1] int 1 run scoreboard players get #$(id) c.as"] + COUL + [
    f'data modify storage {GR} u set value "sem."', f'data modify storage {GR} u0 set value "cette semaine"',
    f"data modify storage {GR} clk set value 0",
    f'data modify storage {GR} ti set value "Quantités échangées par semaine"',
    f'data modify storage {GR} lg set value "survole une semaine pour ses chiffres"',
    f"function {NS}:gr/barres"])
NL5 = "\\n" * 5
LEG = L(T("■ ", C_V), T("vendus   ", "gray"), T("■ ", C_A), T("achetés   ", "gray"), T("$(lg)", "dark_gray"))
CHART = lambda: f'{{text:"",extra:$(sp)}},{{text:"{NL5}"}},{{text:"",extra:$(ax)}}'
w(F + "stat/item_d.mcfunction", "$" + dlg(
    '{text:"$(n)",color:"gold",bold:true}',
    [f'{{type:"minecraft:item",item:{{id:"minecraft:$(id)"}},show_decorations:false,description:{{width:260,contents:{L(T("$(ti)", "white", True), T("\\nmax $(mx)   ·   min $(mn)", "gray"))}}}}}',
     f'{{type:"minecraft:plain_message",width:310,contents:[{{text:""}},{CHART()},{{text:"\\n"}},{{text:"",extra:{LEG}}}]}}'],
    [btn_cmd(T(nom, f"$(k{v})", True), f"trigger commerce set $(g{v})") for v, nom in VUES]
    + [btn_cmd(T("Retour : objet", "white"), "trigger commerce set $(ri)"), btn_cmd(T("Statistiques du marché", "light_purple"), "trigger commerce set 81")]))

# ---------------------------------------------------------------- statistiques du marché : 81 indice, 82 Écus par jour, 83 par semaine
GVUES = [(1, "Indice 24 h"), (2, "Écus par jour"), (3, "Écus par semaine"), (4, "Flux du jour")]
GG = ["scoreboard players operation #gv c.t = #v c.t", "scoreboard players remove #gv c.t 80",
      f"execute if score #gv c.t matches 4 run return run function {NS}:stat/jour_global_0"]
for v, _ in GVUES:
    GG += [f'data modify storage {GR} q.k{v} set value "white"', f'execute if score #gv c.t matches {v} run data modify storage {GR} q.k{v} set value "gold"']
GG += [f"execute if score #gv c.t matches {v} run function {NS}:stat/global_v{v}" for v in (1, 2, 3)]
GG += [f"data modify storage {GR} q.sp set from storage {GR} SP", f"data modify storage {GR} q.ax set from storage {GR} AX",
       f"data modify storage {GR} q.mx set from storage {GR} mx", f"data modify storage {GR} q.mn set from storage {GR} mn",
       f"data modify storage {GR} q.ti set from storage {GR} ti", f"data modify storage {GR} q.lg set from storage {GR} lg",
       f"function {NS}:stat/global_d with storage {GR} q"]
w(F + "stat/global.mcfunction", GG)
w(F + "stat/global_v1.mcfunction", [
    f"data modify storage {GR} G set from storage {NS}:hist _indice",
    f'data modify storage {GR} fk set value "i"', f'data modify storage {GR} col set value "#C792EA"',
    f'data modify storage {GR} u set value "h"', f'data modify storage {GR} u0 set value "dernier relevé"',
    f'data modify storage {GR} axt set value "AXL"', f"data modify storage {GR} clk set value 0",
    f'data modify storage {GR} ti set value "Indice du marché sur 24 h (100 % = prix de base)"', LIGNE_LG,
    f"function {NS}:gr/ligne"])
GCOUL = [f'data modify storage {GR} c1 set value "{C_V}"', f'data modify storage {GR} c2 set value "{C_A}"',
         f'data modify storage {GR} w1 set value "Écus de ventes"', f'data modify storage {GR} w2 set value "Écus d’achats"']
w(F + "stat/global_v2.mcfunction", [
    f"data modify storage {GR} G1 set value []", f"data modify storage {GR} G2 set value []",
    f"data modify storage {GR} G1 set from storage {NS}:hj _v", f"data modify storage {GR} G2 set from storage {NS}:hj _a",
    f"data modify storage {GR} G1 append value 0", f"data modify storage {GR} G2 append value 0",
    f"execute store result storage {GR} G1[-1] int 1 run scoreboard players get #jvE c.g",
    f"execute store result storage {GR} G2[-1] int 1 run scoreboard players get #jaE c.g"] + GCOUL + [
    f'data modify storage {GR} u set value "j"', f'data modify storage {GR} u0 set value "aujourd’hui"',
    f"data modify storage {GR} clk set value 5000000",
    f'data modify storage {GR} ti set value "Écus échangés par jour"',
    f'data modify storage {GR} lg set value "clique un jour : ce qui s’est vendu"',
    f"function {NS}:gr/barres"])
w(F + "stat/global_v3.mcfunction", [
    f"data modify storage {GR} G1 set value []", f"data modify storage {GR} G2 set value []",
    f"data modify storage {GR} G1 set from storage {NS}:hs _v", f"data modify storage {GR} G2 set from storage {NS}:hs _a",
    f"data modify storage {GR} G1 append value 0", f"data modify storage {GR} G2 append value 0",
    f"execute store result storage {GR} G1[-1] int 1 run scoreboard players get #svE c.g",
    f"execute store result storage {GR} G2[-1] int 1 run scoreboard players get #saE c.g"] + GCOUL + [
    f'data modify storage {GR} u set value "sem."', f'data modify storage {GR} u0 set value "cette semaine"',
    f"data modify storage {GR} clk set value 0",
    f'data modify storage {GR} ti set value "Écus échangés par semaine"',
    f'data modify storage {GR} lg set value "survole une semaine"',
    f"function {NS}:gr/barres"])
LEGG = L(T("■ ", C_V), T("ventes   ", "gray"), T("■ ", C_A), T("achats   ", "gray"), T("$(lg)", "dark_gray"))
w(F + "stat/global_d.mcfunction", "$" + dlg(
    T("Statistiques du marché", "light_purple", True),
    [f'{{type:"minecraft:plain_message",width:310,contents:{L(T("$(ti)", "white", True), T("\\nmax $(mx)   ·   min $(mn)\\n", "gray"))[:-1]},{CHART()},{{text:"\\n"}},{{text:"",extra:{LEGG}}}]}}'],
    [btn_cmd(T(nom, f"$(k{v})", True), f"trigger commerce set {80 + v}") for v, nom in GVUES]
    + [btn(T("Bourse", "light_purple"), 20, 160), btn(T("Accueil", "white"), 1, 160)]))

# ---------------------------------------------------------------- détail d'un jour : 5000000 + jours écoulés x 1000 + objet (0 = tout le marché)
w(F + "stat/jour_entree.mcfunction", [
    "scoreboard players operation #gj c.t = #v c.t", "scoreboard players operation #gj c.t /= #1000 c.g",
    "scoreboard players operation #gj c.t %= #1000 c.g",
    f"execute if score #gj c.t matches {NJ + 1}.. run scoreboard players set #gj c.t {NJ}",
    "scoreboard players operation #i c.t = #v c.t", "scoreboard players operation #i c.t %= #1000 c.g",
    f"execute if score #i c.t matches 0 run return run function {NS}:stat/jour_global",
    f"execute if score #i c.t matches 1..{len(ITL)} run function {NS}:stat/jour_item"])
w(F + "stat/jour_global_0.mcfunction", ["scoreboard players set #gj c.t 0", f"function {NS}:stat/jour_global"])


def nav(prefix_i):
    """Valeurs de trigger : jour d'avant, jour d'après (bornés)."""
    return ["scoreboard players operation #x c.t = #gj c.t", "scoreboard players add #x c.t 1",
            f"execute if score #x c.t matches {NJ + 1}.. run scoreboard players set #x c.t {NJ}",
            "scoreboard players operation #x c.t *= #1000 c.g", f"scoreboard players operation #x c.t += {prefix_i}",
            "scoreboard players add #x c.t 5000000", f"execute store result storage {GR} d.av int 1 run scoreboard players get #x c.t",
            "scoreboard players operation #x c.t = #gj c.t", "scoreboard players remove #x c.t 1",
            "execute if score #x c.t matches ..-1 run scoreboard players set #x c.t 0",
            "scoreboard players operation #x c.t *= #1000 c.g", f"scoreboard players operation #x c.t += {prefix_i}",
            "scoreboard players add #x c.t 5000000", f"execute store result storage {GR} d.ap int 1 run scoreboard players get #x c.t",
            f'data modify storage {GR} d.lab set value "Aujourd’hui (en cours)"',
            f"execute store result storage {GR} d.nj int 1 run scoreboard players get #gj c.t",
            f"execute if score #gj c.t matches 1 run data modify storage {GR} d.lab set value \"Hier\"",
            f"execute if score #gj c.t matches 2.. run function {NS}:stat/jour_lab with storage {GR} d"]


w(F + "stat/jour_lab.mcfunction", f'$data modify storage {GR} d.lab set value "Il y a $(nj) jours"')
# un objet
JI = [f"function {NS}:item/charger", f"data modify storage {GR} d set from storage {NS}:t it",
      f"execute store result storage {GR} d.i int 1 run scoreboard players get #i c.t",
      f"execute store result storage {GR} d.k int 1 run scoreboard players get #gj c.t",
      "scoreboard players set #zero c.t 0"] + nav("#i c.t") + [
      f"function {NS}:stat/jour_item_m with storage {GR} d",
      "scoreboard players operation #x c.t = #i c.t", "scoreboard players add #x c.t 4003000",
      f"execute store result storage {GR} d.g int 1 run scoreboard players get #x c.t",
      "scoreboard players operation #x c.t = #i c.t", "scoreboard players add #x c.t 10000",
      f"execute store result storage {GR} d.ri int 1 run scoreboard players get #x c.t",
      f"execute store result storage {GR} d.qv int 1 run scoreboard players get #qv c.t",
      f"execute store result storage {GR} d.qa int 1 run scoreboard players get #qa c.t",
      "scoreboard players operation #x c.t = #pj c.t"] + fmt(f"{GR}", "d.p") + [
      f'execute if score #pj c.t matches ..0 run data modify storage {GR} d.pe set value "?"',
      f'execute if score #pj c.t matches ..0 run data modify storage {GR} d.pz set value ""',
      f'execute if score #pj c.t matches ..0 run data modify storage {GR} d.pc set value ""',
      f"function {NS}:stat/jour_item_d with storage {GR} d"]
w(F + "stat/jour_item.mcfunction", JI)
w(F + "stat/jour_item_m.mcfunction", [
    "scoreboard players set #qv c.t 0", "scoreboard players set #qa c.t 0", "scoreboard players set #pj c.t 0",
    "$execute if score #gj c.t matches 0 run scoreboard players operation #qv c.t = #$(id) c.jv",
    "$execute if score #gj c.t matches 0 run scoreboard players operation #qa c.t = #$(id) c.ja",
    f"$execute if score #gj c.t matches 0 store result score #pj c.t run data get storage {NS}:hist $(id)[-1]",
    f"$execute if score #gj c.t matches 1.. store result score #qv c.t run data get storage {NS}:hj v_$(id)[-$(k)]",
    f"$execute if score #gj c.t matches 1.. store result score #qa c.t run data get storage {NS}:hj a_$(id)[-$(k)]",
    f"$execute if score #gj c.t matches 1.. store result score #pj c.t run data get storage {NS}:hj p_$(id)[-$(k)]"])
w(F + "stat/jour_item_d.mcfunction", "$" + dlg(
    '{text:"$(n)",color:"gold",bold:true}',
    [f'{{type:"minecraft:item",item:{{id:"minecraft:$(id)"}},show_decorations:false,description:{{width:260,contents:{L(T("$(lab)", "white", True), T("\\nVendus : ", "gray"), T("$(qv)", C_V, True), T("   ·   achetés : ", "gray"), T("$(qa)", C_A, True), T("\\nCours en fin de journée : ", "gray"), T("$(pe),$(pz)$(pc) " + ECU, "gold", True))}}}}}'],
    [btn_cmd(T("◀  Jour d’avant", "white"), "trigger commerce set $(av)"), btn_cmd(T("Jour d’après  ▶", "white"), "trigger commerce set $(ap)"),
     btn_cmd(T("Graphiques", "light_purple"), "trigger commerce set $(g)"), btn_cmd(T("Retour : objet", "white"), "trigger commerce set $(ri)")]))

# tout le marché : totaux du jour et tops 5 (vendus, achetés), chaque ligne ouvre le détail de l'objet ce jour-là
NTJ = 5
CHJ = []
for it in ITL:
    CHJ += [f"$execute store result score {H(it)} c.dv run data get storage {NS}:hj v_{it['id']}[-$(k)]",
            f"$execute store result score {H(it)} c.da run data get storage {NS}:hj a_{it['id']}[-$(k)]"]
w(F + "stat/charger_jour.mcfunction", CHJ)
w(F + "stat/charger_auj.mcfunction", [f"scoreboard players operation {H(it)} c.{d} = {H(it)} c.j{s}" for it in ITL for d, s in (("dv", "v"), ("da", "a"))])
JG = ["scoreboard players reset * c.dv", "scoreboard players reset * c.da",
      f"execute store result storage {GR} d.k int 1 run scoreboard players get #gj c.t",
      f"execute if score #gj c.t matches 0 run function {NS}:stat/charger_auj",
      f"execute if score #gj c.t matches 1.. run function {NS}:stat/charger_jour with storage {GR} d",
      "scoreboard players operation #ev c.t = #jvE c.g", "scoreboard players operation #ea c.t = #jaE c.g",
      f"execute if score #gj c.t matches 1.. run function {NS}:stat/jour_tot with storage {GR} d",
      f"execute store result storage {GR} d.ev int 1 run scoreboard players get #ev c.t",
      f"execute store result storage {GR} d.ea int 1 run scoreboard players get #ea c.t"] + nav("#zero c.t")
JG[0:0] = ["scoreboard players set #zero c.t 0", f"data modify storage {GR} d set value {{}}"]
for key, obj in (("TV", "c.dv"), ("TA", "c.da")):
    JG += [f'data modify storage {GR} {key} set value [{{text:""}}]', "scoreboard players reset * c.y"]
    for k in range(1, NTJ + 1):
        JG += ["scoreboard players set #m c.t 0", "scoreboard players set #best c.t 0", f"function {NS}:stat/top_{obj[2:]}",
               f"execute if score #best c.t matches 1.. run scoreboard players set #rk c.t {k}",
               f"execute if score #best c.t matches 1.. run function {NS}:stat/top_ret_{key.lower()}"]
    JG.append(f'execute unless data storage {GR} {key}[1] run data modify storage {GR} {key} append value {{text:"rien ce jour-là",color:"dark_gray",italic:true}}')
    PS = []
    for it in ITL:
        PS += [f"execute unless score {H(it)} c.y matches 1 if score {H(it)} {obj} > #m c.t run scoreboard players set #best c.t {it['i']}",
               f"execute if score #best c.t matches {it['i']} run scoreboard players operation #m c.t = {H(it)} {obj}"]
    w(F + f"stat/top_{obj[2:]}.mcfunction", PS)
    w(F + f"stat/top_ret_{key.lower()}.mcfunction", [
        "scoreboard players operation #i c.t = #best c.t", f"function {NS}:item/charger",
        f"function {NS}:stat/top_marquer with storage {NS}:t it",
        f"data modify storage {GR} tl set from storage {NS}:t it",
        f"execute store result storage {GR} tl.q int 1 run scoreboard players get #m c.t",
        f"execute store result storage {GR} tl.r int 1 run scoreboard players get #rk c.t",
        "scoreboard players operation #x c.t = #gj c.t", "scoreboard players operation #x c.t *= #1000 c.g",
        "scoreboard players operation #x c.t += #i c.t", "scoreboard players add #x c.t 5000000",
        f"execute store result storage {GR} tl.c int 1 run scoreboard players get #x c.t",
        f"function {NS}:stat/top_ligne_{key.lower()} with storage {GR} tl"])
    col = C_V if key == "TV" else C_A
    w(F + f"stat/top_ligne_{key.lower()}.mcfunction", [
        f'$data modify storage {GR} {key} append value {{text:"$(r). ",color:"gray"}}',
        f'$data modify storage {GR} {key} append value {{text:"$(n)",color:"white",underlined:true,click_event:{{action:"run_command",command:"trigger commerce set $(c)"}},hover_event:{{action:"show_text",value:{{text:"Voir $(n) ce jour-là",color:"gray"}}}}}}',
        f'$data modify storage {GR} {key} append value {{text:"   $(q)\\n",color:"{col}",bold:true}}'])
w(F + "stat/top_marquer.mcfunction", "$scoreboard players set #$(id) c.y 1")
w(F + "stat/jour_tot.mcfunction", [
    "scoreboard players set #ev c.t 0", "scoreboard players set #ea c.t 0",
    f"$execute store result score #ev c.t run data get storage {NS}:hj _v[-$(k)]",
    f"$execute store result score #ea c.t run data get storage {NS}:hj _a[-$(k)]"])
JG += [f"data modify storage {GR} d.tv set from storage {GR} TV", f"data modify storage {GR} d.ta set from storage {GR} TA",
       f"function {NS}:stat/jour_global_d with storage {GR} d"]
w(F + "stat/jour_global.mcfunction", JG)
w(F + "stat/jour_global_d.mcfunction", "$" + dlg(
    T("Flux du marché", "light_purple", True),
    [f'{{type:"minecraft:plain_message",width:310,contents:{L(T("$(lab)", "white", True), T("\\nVentes : ", "gray"), T("$(ev) " + ECU, C_V, True), T("   ·   achats : ", "gray"), T("$(ea) " + ECU, C_A, True), T("\\n\\nPlus vendus\\n", C_V, True))[:-1]},{{text:"",extra:$(tv)}},{T("\\nPlus achetés\\n", C_A, True)},{{text:"",extra:$(ta)}}]}}'],
    [btn_cmd(T("◀  Jour d’avant", "white"), "trigger commerce set $(av)"), btn_cmd(T("Jour d’après  ▶", "white"), "trigger commerce set $(ap)"),
     btn(T("Écus par jour", "light_purple"), 82, 160), btn(T("Accueil", "white"), 1, 160)]))

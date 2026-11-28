# -*- coding: utf-8 -*-
# Générateur du datapack Industrie (Minecraft Java 26.x, vanilla) : le tycoon de fin de jeu.
# Écrit le pack décompressé dans ../build/industrie_datapack, le resource pack dans ../build/industrie_rp
# et le zip dans ../industrie.zip. Dépend de Métiers (m.id, niveaux, éclats, boss) et de Commerce (c.ecus, registre des noms).
#
# Principe (voir README.md) : chaque joueur a une île dans la dimension industrie:archipel. Les machines sont des
# item_display posés sur des emplacements ; la production est virtuelle (scores du joueur), calculée minute par minute
# quand il est connecté et d'un bloc à son retour (8 h au plus). Rien n'est jamais cassé : îles et parcelles sont posées
# dans le vide.
import os, sys, json, shutil, zipfile

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from tables import *

ROOT = os.path.join(ICI, "..", "build", "industrie_datapack")
RP = os.path.join(ICI, "..", "build", "industrie_rp")
NS = "industrie"
F = f"data/{NS}/function/"
VERSION = 14
DIM = f"{NS}:archipel"
S = "scoreboard players"
for d in (ROOT, RP):
    if os.path.exists(d):
        shutil.rmtree(d)


def w(path, txt):
    if isinstance(txt, list):
        txt = "\n".join(txt)
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(txt.strip() + "\n")


def fn(name, lines):
    w(F + name + ".mcfunction", lines)


def wj(path, obj):
    w(path, json.dumps(obj, ensure_ascii=False, indent=1))


def T(text, col="white", bold=False):
    return f'{{text:"{text}",color:"{col}",bold:{"true" if bold else "false"},italic:false}}'


def L(*parts):
    return "[" + ",".join(['{text:""}'] + list(parts)) + "]"


PREFIX = '{text:"[Industrie] ",color:"#F7C843",bold:false,italic:false}'


def say(txt, col="gray", who="@s"):
    return f"tellraw {who} {L(PREFIX, T(txt, col))}"


def btn(label, val, width=150, tip=None):
    width = min(width, 200)                  # 27/11/2026 : fenêtres trop larges sur les petits écrans
    s_ = f"{{label:{label},width:{width}"
    if tip:
        s_ += f',tooltip:{{text:"{tip}"}}'
    return s_ + f',action:{{type:"run_command",command:"trigger industrie set {val}"}}}}'


def dlg(title, body, actions, cols=2, exit_val=None):
    cols = min(cols, 3)
    ex = f',exit_action:{{label:{T("Retour", "gray")},width:120,action:{{type:"run_command",command:"trigger industrie set {exit_val}"}}}}' if exit_val else ""
    return (f'dialog show @s {{type:"minecraft:multi_action",title:{title},can_close_with_escape:true,pause:false,'
            f'body:[{",".join(body)}],actions:' + ("$(a)" if actions == ["ACTIONS"] else f'[{",".join(actions)}]') + f',columns:{cols}{ex}}}')


def msg(contents, width=320):
    width = min(width, 320)
    return f'{{type:"minecraft:plain_message",width:{width},contents:{contents}}}'


def mille(n):
    return f"{int(n):,}".replace(",", " ")


def fe(n):
    """Montant lisible : 1 500 000 -> « 1,5 M »."""
    if n >= 1_000_000:
        return (f"{n / 1e6:.1f}".rstrip("0").rstrip(".").replace(".", ",")) + " M"
    return mille(n)


# ------------------------------------------------------------------ scores
JOBS = "bfmcpenxtk"
OBJ = ["i.ile", "i.rang", "i.ri", "i.rir", "i.ctr", "i.np", "i.halle", "i.tube", "i.bq", "i.rb", "i.rt", "i.go",
       "i.tl", "i.th", "i.td", "i.cts", "i.jn", "i.jb", "i.jv", "i.r7", "i.dette", "i.pj", "i.pban", "i.pret",
       "i.sel", "i.pv", "i.ph", "i.fe", "i.pend", "i.gm", "i.rx", "i.ry", "i.rz", "i.rd", "i.vu", "i.own", "i.sid",
       "i.mt", "i.ml", "i.mob", "i.sf", "i.spv", "i.spq", "i.t", "i.g", "i.ph2", "i.tx", "i.tz", "i.off", "i.dem",
       "i.prev", "i.sdi", "i.tuto", "i.cin", "i.psl", "i.pst"] + [f"i.h{k}" for k in range(12)]
OBJ += [f"i.b{b}" for b in range(1, 5)] + [f"i.p{k}" for k in range(49)]
OBJ += [f"i.c{c}{x}" for c in (1, 2, 3) for x in "pqrf"]
for p in PL:
    OBJ += [f"i.s_{p}", f"i.v_{p}", f"i.j_{p}", f"i.o_{p}", f"i.x_{p}", f"i.a_{p}", f"i.w_{p}"]
for m in ML:
    OBJ += [f"i.q_{m}", f"i.n_{m}", f"i.k_{m}", f"i.ac_{m}"]
OBJ += [f"i.qs{k}" for k in range(len(MOBS))]
CONST = sorted({-1, 0, 8, 50, 200, 2, 10, 20, 24, 23, 32, 60, 100, 1000, 10000, 1200, 72000, 1728000, 2048, 16, 7, 4, 3, 5, 150, 125, 110, 1, 1000000, 1000000000})

wj("pack.mcmeta", {"pack": {"description": "Industrie : îles, machines, tubes, Halle du Marché, Banque", "min_format": 84, "max_format": 200}})
wj("data/minecraft/tags/function/load.json", {"values": [f"{NS}:load"]})
wj("data/minecraft/tags/function/tick.json", {"values": [f"{NS}:tick"]})

# ------------------------------------------------------------------ dimension : vide, ciel du monde normal
wj(f"data/{NS}/dimension/archipel.json", {"type": "minecraft:overworld", "generator": {"type": "minecraft:flat", "settings": {
    "biome": "minecraft:the_void", "features": False, "lakes": False, "layers": [], "structure_overrides": []}}})

LD = [f"scoreboard objectives add {o} dummy" for o in OBJ] + [
    "scoreboard objectives add industrie trigger",
    "scoreboard objectives add i.kwi minecraft.killed:minecraft.wither",
    "scoreboard objectives add i.quit minecraft.custom:minecraft.leave_game"]
LD += [f"{S} set #{c} i.g {c}" for c in CONST]
LD += [f"{S} set #zero_0 i.g 0", f"{S} set #zero_2 i.g 1", f"{S} add #uid i.g 0", f"{S} add #next i.g 0", f"{S} add #sec i.g 0", f"{S} add #ev i.g 0", f"{S} add #evp i.g 0", f"{S} add #evm i.g 100",
       f"{S} add #evt i.g 0", f"{S} add #foire i.g 100",
       f"execute unless data storage {NS}:parts offres run data modify storage {NS}:parts offres set value []",
       f"execute unless data storage {NS}:parts h run data modify storage {NS}:parts h set value []",
       f"execute unless data storage {NS}:file l run data modify storage {NS}:file l set value []"]
LD += ["title @a clear", "execute if score #hud c.g matches 1.. run scoreboard players set @a c.hudv -1"]   # 28/11/2026 : efface les titres laissés par Industrie, l'encadré des Écus revient
fn("load", LD)

fn("tick", [
    "scoreboard players enable @a industrie",
    f"execute as @a[scores={{industrie=1..}}] at @s run function {NS}:trigger",
    f"execute as @a[scores={{industrie=..-1}}] at @s run function {NS}:saisie",
    f"execute as @e[type=minecraft:interaction,tag=ind.mi] at @s if data entity @s interaction run function {NS}:machine/clic",
    f"execute as @e[type=minecraft:interaction,tag=ind.bi] at @s if data entity @s interaction run function {NS}:batiment/clic",
    f"execute as @e[type=minecraft:interaction,tag=ind.si] at @s if data entity @s interaction run function {NS}:emplacement/clic",
    "scoreboard players add #sec i.g 1",
    f"execute if score #sec i.g matches 20.. run function {NS}:seconde"])
fn("seconde", [
    f"{S} set #sec i.g 0",
    "execute store result score #now i.g run time query gametime",
    f"execute as @a at @s run function {NS}:joueur/seconde",
    f"execute as @a[scores={{i.ile=0..}}] unless score @s i.tuto matches {7}.. at @s run function {NS}:tuto/verif",
    f"execute as @a[scores={{i.cin=1..39}}] at @s run function {NS}:cine/pas",
    f"execute as @a at @s if dimension {DIM} run function {NS}:ile/garde",
    f"execute as @a[tag=ind.adv] at @s unless dimension {DIM} run function {NS}:ile/hors",
    f"{S} add #bar i.g 1", f"execute if score #bar i.g matches 5.. as @a at @s if dimension {DIM} run function {NS}:ile/barrieres",
    f"execute if score #bar i.g matches 5.. run {S} set #bar i.g 0",
    f"execute as @e[type=minecraft:item_display,tag=ind.pq] run function {NS}:tube/vieillir",
    f"{S} add #pqt i.g 1", f"execute if score #pqt i.g matches 2.. run function {NS}:tube/flux",
    f"function {NS}:evenement/seconde"])

# ------------------------------------------------------------------ joueur : horloges, production
fn("joueur/seconde", [
    f"execute unless score @s i.vu matches 1 run function {NS}:joueur/init",
    f"execute unless score @s i.ile matches 0.. run return 0",
    # minute écoulée (ou retour après une absence) : production
    f"{S} operation #min i.t = #now i.g", f"{S} operation #min i.t /= #1200 i.g",
    f"execute if score #min i.t > @s i.tl run function {NS}:prod/rattrapage",
    f"execute if score @s i.rb matches 1.. run function {NS}:labo/verif"])
fn("joueur/init", [f"{S} add @s {o} 0" for o in OBJ if o not in ("i.ile",)] + [
    f"{S} set @s i.vu 1", f"{S} set @s i.ile -1", f"{S} set @s i.rang 1",
    *[f"{S} set @s i.x_{p} 70" for p in PL],
    'tellraw @s [{"text":"[Industrie] ","color":"#F7C843"},{"text":"Une île t\'attend dans l\'Archipel des usines. ","color":"gray"},'
    '{"text":"[OUVRIR]","color":"green","bold":true,"click_event":{"action":"run_command","command":"/trigger industrie set 1"}},'
    '{"text":"  (ou /trigger industrie set 1, ou le menu G)","color":"dark_gray"}]'])

OFF = [f"{S} operation #m i.t = #min i.t", f"{S} operation #m i.t -= @s i.tl",
       f"{S} set #cap i.t {OFFLINE_MIN}",
       f"execute if score @s i.b3 matches 5.. run {S} add #cap i.t 120",
       f"execute if score @s i.b3 matches 10.. run {S} add #cap i.t 120",
       f"execute if score #m i.t > #cap i.t run {S} operation #m i.t = #cap i.t",
       f"{S} operation @s i.tl = #min i.t",
       f"execute if score #m i.t matches 2.. run {S} operation #mabs i.t = #m i.t",
       f"function {NS}:prod/pas",
       f"execute if score #mabs i.t matches 30.. run function {NS}:prod/resume",
       f"{S} set #mabs i.t 0",
       # heures et jours
       f"{S} operation #hr i.t = #now i.g", f"{S} operation #hr i.t /= #72000 i.g",
       f"{S} set #nh i.t 0", f"function {NS}:prod/heures",
       f"{S} operation #jr i.t = #now i.g", f"{S} operation #jr i.t /= #1728000 i.g",
       f"execute if score #jr i.t > @s i.td run function {NS}:prod/jour"]
fn("prod/rattrapage", OFF)
fn("prod/heures", [
    f"execute unless score #hr i.t > @s i.th run return 0",
    f"execute if score #nh i.t matches 8.. run return run {S} operation @s i.th = #hr i.t",
    f"{S} add @s i.th 1", f"{S} add #nh i.t 1", f"function {NS}:prod/heure", f"function {NS}:prod/heures"])
fn("prod/resume", [
    f'tellraw @s {L(PREFIX, T("Pendant ton absence, ton île a tourné ", "gray"), "{score:{name:\"#mabs\",objective:\"i.t\"},color:\"gold\"}", T(" minutes. Le relevé est dans « Mon industrie ».", "gray"))}'])

# ---- un pas de production : #m minutes
B = {}  # bonus par métier, en %
PAS = [f"{S} operation #cap i.t = #cap i.t"]
# 1. Nexus plein ?
PAS += [f"{S} set #tot i.t 0"] + [f"{S} operation #tot i.t += @s i.s_{p}" for p in PL]
PAS += [f"{S} set #ncap i.t {NEXUS_CAP}"]
for b in range(1, 8):
    PAS.append(f"execute if score @s i.b3 matches {b}.. run {S} operation #ncap i.t *= #2 i.g")
PAS += [f"execute if score @s i.b3 matches 8.. run {S} set #ncap i.t 100000000",
        f"{S} set #plein i.t 0", f"execute if score #tot i.t >= #ncap i.t run {S} set #plein i.t 1"]
# 2. énergie (dixièmes de kW)
PAS += [f"{S} set #dem i.t 0"]
for m in ML:
    if MACH[m]["kw"] > 0:
        PAS += [f"{S} operation #x i.t = @s i.k_{m}", f"{S} set #y i.t {MACH[m]['kw']}", f"{S} operation #x i.t *= #y i.t", f"{S} operation #dem i.t += #x i.t"]
PAS += [f"{S} set #y i.t 100", f"{S} operation #z i.t = @s i.b4", f"{S} operation #z i.t *= #3 i.g", f"{S} operation #y i.t -= #z i.t",
        f"{S} operation #dem i.t *= #y i.t", f"{S} operation #dem i.t /= #100 i.g"]
# charbon des chaudières : 300 par heure et par niveau, au prorata des minutes
PAS += [f"{S} operation #need i.t = @s i.q_chaudiere", f"{S} set #y i.t {MACH['chaudiere']['charbon']}", f"{S} operation #need i.t *= #y i.t",
        f"{S} operation #need i.t /= #100 i.g", f"{S} operation #need i.t *= #m i.t", f"{S} operation #need i.t /= #60 i.g",
        f"{S} set #fc i.t 1000",
        f"execute if score #need i.t matches 1.. if score @s i.s_charbon < #need i.t run function {NS}:prod/charbon_court",
        f"execute if score #need i.t matches 1.. if score #fc i.t matches 1000 run {S} operation @s i.s_charbon -= #need i.t",
        f"{S} set #off i.t {NEXUS_KW * 10}"]
for m, kw in (("chaudiere", 150), ("lave", 600), ("coeur", 3000)):
    PAS += [f"{S} operation #x i.t = @s i.q_{m}", f"{S} set #y i.t {kw}", f"{S} operation #x i.t *= #y i.t", f"{S} operation #x i.t /= #10 i.g"]
    if m == "chaudiere":
        PAS += [f"{S} operation #x i.t *= #fc i.t", f"{S} operation #x i.t /= #1000 i.g"]
    PAS += [f"{S} operation #off i.t += #x i.t"]
PAS += [f"{S} set #fe i.t 1000",
        f"execute if score #dem i.t > #off i.t run function {NS}:prod/fe",
        f"{S} operation @s i.fe = #fe i.t", f"{S} operation @s i.off = #off i.t", f"{S} operation @s i.dem = #dem i.t"]
# 3. bonus : métier + cadence + Grands Œuvres
PAS += [f"{S} operation #bb i.t = @s i.b2", f"{S} operation #bb i.t *= #4 i.g",
        f"{S} operation #z i.t = @s i.go", f"{S} set #y i.t 8", f"{S} operation #z i.t *= #y i.t", f"{S} operation #bb i.t += #z i.t",
        f"{S} add #bb i.t 100"]
for j in "mfnbct":
    PAS += [f"{S} set #bm{j} i.t 0", f"execute store result score #bm{j} i.t run scoreboard players get @s m.{j}_lvl",
            f"execute if score #bm{j} i.t matches 101.. run {S} set #bm{j} i.t 100",
            f"{S} operation #bm{j} i.t /= #5 i.g", f"{S} operation #bm{j} i.t += #bb i.t"]
# 4. producteurs (sauf si le Nexus est plein)
PAS += [f"execute if score #plein i.t matches 0 run function {NS}:prod/producteurs",
        f"execute if score #plein i.t matches 0 run function {NS}:prod/spawners",
        f"function {NS}:prod/ateliers",
        f"function {NS}:prod/ventes"]
fn("prod/pas", PAS)
fn("prod/charbon_court", [f"{S} operation #fc i.t = @s i.s_charbon", f"{S} operation #fc i.t *= #1000 i.g", f"{S} operation #fc i.t /= #need i.t",
                          f"{S} set @s i.s_charbon 0"])
fn("prod/fe", [f"{S} operation #fe i.t = #off i.t", f"{S} operation #fe i.t *= #1000 i.g", f"{S} operation #fe i.t /= #dem i.t"])

PR = []
for m in ML:
    d = MACH[m]
    if d["kw"] < 0 or m in ATELIERS or m == "spawner" or not d.get("out"):
        continue
    PR.append(f"execute if score @s i.q_{m} matches 1.. run function {NS}:prod/m_{m}")
    tube_cap = [f"{S} set #tc i.t {TUBES[0][2]}"] + [f"execute if score @s i.tube matches {k} run {S} set #tc i.t {t[2]}" for k, t in enumerate(TUBES) if k]
    L_ = [f"{S} set #somme i.t 0"]
    for p, q in d["out"].items():
        # unités par heure : base x somme des niveaux (%) x énergie x bonus
        L_ += [f"{S} set #r_{p} i.t {q}", f"{S} operation #r_{p} i.t *= @s i.q_{m}", f"{S} operation #r_{p} i.t /= #100 i.g",
               f"{S} operation #r_{p} i.t *= #fe i.t", f"{S} operation #r_{p} i.t /= #1000 i.g",
               f"{S} operation #r_{p} i.t *= #bm{d['met']} i.t", f"{S} operation #r_{p} i.t /= #100 i.g",
               f"{S} operation #somme i.t += #r_{p} i.t"]
    # débit des tubes : par minute et par machine
    L_ += tube_cap + [f"{S} operation #tc i.t *= #60 i.g", f"{S} operation #tc i.t *= @s i.n_{m}", f"{S} set #fk i.t 1000",
                      f"execute if score #somme i.t > #tc i.t run {S} operation #fk i.t = #tc i.t",
                      f"execute if score #somme i.t > #tc i.t run {S} operation #fk i.t *= #1000 i.g",
                      f"execute if score #somme i.t > #tc i.t run {S} operation #fk i.t /= #somme i.t"]
    for p in d["out"]:
        L_ += [f"{S} operation #r_{p} i.t *= #fk i.t", f"{S} operation #r_{p} i.t /= #1000 i.g",
               f"{S} operation #r_{p} i.t *= #m i.t", f"{S} operation @s i.a_{p} += #r_{p} i.t",
               f"{S} operation #x i.t = @s i.a_{p}", f"{S} operation #x i.t /= #60 i.g", f"{S} operation @s i.s_{p} += #x i.t",
               f"{S} operation @s i.a_{p} %= #60 i.g"]
    fn(f"prod/m_{m}", L_)
fn("prod/producteurs", PR)

SPW = []
for k, (mob, drops) in enumerate(MOBS):
    SPW.append(f"execute if score @s i.qs{k} matches 1.. run function {NS}:prod/sp_{k}")
    L_ = [f"{S} set #kills i.t {SP_PAR_H}", f"{S} operation #kills i.t *= @s i.qs{k}", f"{S} operation #kills i.t /= #100 i.g",
          f"{S} operation #kills i.t *= #fe i.t", f"{S} operation #kills i.t /= #1000 i.g",
          f"{S} operation #kills i.t *= #bmc i.t", f"{S} operation #kills i.t /= #100 i.g", f"{S} operation #kills i.t *= #m i.t"]
    for p, q in drops.items():
        L_ += [f"{S} operation #x i.t = #kills i.t", f"{S} set #y i.t {q}", f"{S} operation #x i.t *= #y i.t", f"{S} operation #x i.t /= #100 i.g",
               f"{S} operation @s i.a_{p} += #x i.t", f"{S} operation #x i.t = @s i.a_{p}", f"{S} operation #x i.t /= #60 i.g",
               f"{S} operation @s i.s_{p} += #x i.t", f"{S} operation @s i.a_{p} %= #60 i.g"]
    fn(f"prod/sp_{k}", L_)
fn("prod/spawners", SPW)

AT = []
for m in ATELIERS:
    d = MACH[m]
    (po, qo), = d["out"].items()
    AT.append(f"execute if score @s i.q_{m} matches 1.. run function {NS}:prod/a_{m}")
    L_ = [f"{S} set #c i.t {qo}", f"{S} operation #c i.t *= @s i.q_{m}", f"{S} operation #c i.t /= #100 i.g",
          f"{S} operation #c i.t *= #fe i.t", f"{S} operation #c i.t /= #1000 i.g",
          f"{S} operation #c i.t *= #bm{d['met']} i.t", f"{S} operation #c i.t /= #100 i.g",
          f"{S} operation #c i.t *= #m i.t", f"{S} operation @s i.ac_{m} += #c i.t",
          f"{S} operation #c i.t = @s i.ac_{m}", f"{S} operation #c i.t /= #60 i.g", f"{S} operation @s i.ac_{m} %= #60 i.g",
          f"execute if score #plein i.t matches 1 run {S} set #c i.t 0"]
    for p, r in d["inp"].items():
        # réserve de la Banque : l'atelier ne touche pas à ce que le joueur a mis de côté pour autre chose ? Si : la
        # réserve sert justement à nourrir les ateliers, elle n'est protégée que des ventes.
        L_ += [f"{S} operation #x i.t = @s i.s_{p}", f"{S} set #y i.t {r}", f"{S} operation #x i.t /= #y i.t",
               f"execute if score #x i.t < #c i.t run {S} operation #c i.t = #x i.t"]
    for p, r in d["inp"].items():
        L_ += [f"{S} operation #x i.t = #c i.t", f"{S} set #y i.t {r}", f"{S} operation #x i.t *= #y i.t", f"{S} operation @s i.s_{p} -= #x i.t"]
    L_ += [f"{S} operation @s i.s_{po} += #c i.t"]
    fn(f"prod/a_{m}", L_)
fn("prod/ateliers", AT)

# ---- ventes de la Halle
VAL = sorted(PL, key=lambda p: -PROD[p][2])
V_ = [f"{S} set #G i.t 0", f"{S} set #capl i.t 0"]
for k, h in enumerate(HALLE):
    V_.append(f"execute if score @s i.halle matches {k} run {S} set #capl i.t {h[4]}")
V_ += [f"{S} operation #capl i.t *= #m i.t", f"{S} operation #capl i.t /= #60 i.g",
       f"{S} set #hb i.t 100"] + [f"execute if score @s i.halle matches {k} run {S} set #hb i.t {h[6]}" for k, h in enumerate(HALLE) if h[6] != 100]
V_ += [f"{S} operation #sb i.t = @s i.b1", f"{S} set #y i.t 25", f"{S} operation #sb i.t *= #y i.t", f"{S} add #sb i.t 100"]
for p in VAL:
    V_.append(f"execute if score #capl i.t matches 1.. if score @s i.s_{p} matches 1.. unless score @s i.o_{p} matches 1 run function {NS}:vente/p_{p}")
V_ += [f"execute if score #G i.t matches 1.. run function {NS}:vente/encaisser"]
fn("prod/ventes", V_)
for idx, p in enumerate(PL):
    nom, item, p0, S0 = PROD[p]
    L_ = [f"{S} operation #q i.t = @s i.s_{p}",
          # réserve (ordre 4) : on garde x_ objets
          f"execute if score @s i.o_{p} matches 4 run {S} operation #q i.t -= @s i.x_{p}",
          # contrats du jour non livrés : la Halle met de côté leur quantité (28/11/2026)
          *[f"execute if score @s i.c{c}p matches {idx + 1} unless score @s i.c{c}f matches 1 run {S} operation #q i.t -= @s i.c{c}q" for c in (1, 2, 3)],
          # 28/11/2026 : une heure de consommation des chaudières et des ateliers reste au Nexus
          *([f"{S} operation #x i.t = @s i.q_chaudiere", f"{S} set #y i.t {MACH['chaudiere']['charbon']}", f"{S} operation #x i.t *= #y i.t",
             f"{S} operation #x i.t /= #100 i.g", f"{S} operation #q i.t -= #x i.t"] if p == "charbon" else []),
          *[x for m_ in ATELIERS if p in MACH[m_]["inp"] for x in (
             f"{S} operation #x i.t = @s i.q_{m_}", f"{S} set #y i.t {list(MACH[m_]['out'].values())[0] * MACH[m_]['inp'][p]}",
             f"{S} operation #x i.t *= #y i.t", f"{S} operation #x i.t /= #100 i.g", f"{S} operation #q i.t -= #x i.t")],
          f"execute if score #q i.t matches ..0 run return 0",
          # saturation effective
          f"{S} set #S i.t {S0}", f"{S} operation #S i.t *= #sb i.t", f"{S} operation #S i.t /= #100 i.g",
          f"{S} operation #S i.t *= #hb i.t", f"{S} operation #S i.t /= #100 i.g",
          f"{S} operation #S i.t *= #foire i.g", f"{S} operation #S i.t /= #100 i.g",
          # étaler (ordre 3) : x_ objets par jour au plus
          f"execute if score @s i.o_{p} matches 3 run {S} operation #x i.t = @s i.x_{p}",
          f"execute if score @s i.o_{p} matches 3 run {S} operation #x i.t -= @s i.j_{p}",
          f"execute if score @s i.o_{p} matches 3 if score #q i.t > #x i.t run {S} operation #q i.t = #x i.t",
          f"execute if score #q i.t > #capl i.t run {S} operation #q i.t = #capl i.t",
          f"execute if score #q i.t matches ..0 run return 0",
          # prix du moment en % de la base : S / (S + V), et l'évènement de marché
          f"{S} operation #pct i.t = #S i.t", f"{S} operation #pct i.t *= #100 i.g",
          f"{S} operation #den i.t = #S i.t", f"{S} operation #den i.t += @s i.v_{p}", f"{S} operation #pct i.t /= #den i.t",
          f"{S} set #ev i.t 100", f"execute if score #evp i.g matches {idx + 1} run {S} operation #ev i.t = #evm i.g",
          f"{S} operation #pct i.t *= #ev i.t", f"{S} operation #pct i.t /= #100 i.g",
          # plancher (ordre 2) : pas de vente sous x_ %
          f"execute if score @s i.o_{p} matches 2 if score #pct i.t < @s i.x_{p} run return 0",
          # recette en centièmes : p0 x q x S / (S + V + q/2), en pour mille pour éviter les débordements
          f"{S} operation #h i.t = #q i.t", f"{S} operation #h i.t /= #2 i.g", f"{S} operation #den i.t += #h i.t",
          f"{S} operation #r i.t = #S i.t", f"{S} operation #r i.t *= #1000 i.g", f"{S} operation #r i.t /= #den i.t",
          f"{S} operation #r i.t *= #ev i.t", f"{S} operation #r i.t /= #100 i.g",
          f"{S} set #pq i.t {p0}", f"{S} operation #pq i.t *= #q i.t",
          f"execute if score #pq i.t matches ..1999999 run {S} operation #pq i.t *= #r i.t",
          f"execute if score #pq i.t matches ..1999999999 if score #q i.t matches 1.. run {S} operation #pq i.t /= #1000 i.g",
          ]
    # le cas « grand produit » : (p0 q / 100) x r / 10
    L_ = L_[:-2] + [f"{S} set #big i.t 0", f"execute if score #pq i.t matches 2000000.. run {S} set #big i.t 1",
                    f"execute if score #big i.t matches 0 run {S} operation #pq i.t *= #r i.t",
                    f"execute if score #big i.t matches 0 run {S} operation #pq i.t /= #1000 i.g",
                    f"execute if score #big i.t matches 1 run {S} operation #pq i.t /= #100 i.g",
                    f"execute if score #big i.t matches 1 run {S} operation #pq i.t *= #r i.t",
                    f"execute if score #big i.t matches 1 run {S} operation #pq i.t /= #10 i.g"]
    L_ += [f"{S} operation #G i.t += #pq i.t", f"{S} operation @s i.s_{p} -= #q i.t", f"{S} operation @s i.v_{p} += #q i.t",
           f"{S} operation @s i.j_{p} += #q i.t", f"{S} operation #capl i.t -= #q i.t"]
    fn(f"vente/p_{p}", L_)

# encaisser #G centièmes : commission, réputation, entretien, prêt, puis le solde du Commerce
EN = [f"{S} operation @s i.jb += #G i.t", f"{S} set #com i.t 0"]
EN += [f"execute if score @s i.halle matches {k} run {S} set #com i.t {h[5]}" for k, h in enumerate(HALLE)]
EN += [f"execute if score @s m.t_lvl matches 50.. run {S} remove #com i.t 2", f"execute if score #com i.t matches ..-1 run {S} set #com i.t 0",
       f"{S} set #y i.t 100", f"{S} operation #y i.t -= #com i.t",
       # réputation : 1 point par RI_ECUS Écus bruts (gelée pendant un retard de prêt)
       f"execute unless score @s i.pret matches 2 run {S} operation @s i.rir += #G i.t",
       f"{S} set #z i.t {RI_ECUS * 100}", f"{S} operation #x i.t = @s i.rir", f"{S} operation #x i.t /= #z i.t",
       f"{S} operation @s i.ri += #x i.t", f"{S} operation @s i.rir %= #z i.t",
       # net
       f"{S} operation #N i.t = #G i.t", f"{S} operation #N i.t /= #100 i.g", f"{S} operation #N i.t *= #y i.t",
       f"{S} operation #R i.t = #G i.t", f"{S} operation #R i.t %= #100 i.g", f"{S} operation #R i.t *= #y i.t", f"{S} operation #R i.t /= #100 i.g",
       f"{S} operation #N i.t += #R i.t"]
for seuil, garde in ENTRETIEN:   # du plus haut au plus bas : la première tranche atteinte s'applique
    EN += [f"execute if score #ent i.t matches 0 if score @s i.jn matches {seuil}.. run {S} set #ent i.t {garde}"]
EN = EN[:-len(ENTRETIEN)] + [f"{S} set #ent i.t 0"] + EN[-len(ENTRETIEN):] + [
    f"execute if score #ent i.t matches 1.. run {S} operation #N i.t /= #100 i.g",
    f"execute if score #ent i.t matches 1.. run {S} operation #N i.t *= #ent i.t",
    # prêt : 25 % (50 % en retard)
    f"execute if score @s i.dette matches 1.. run function {NS}:banque/prelever",
    f"{S} operation @s i.cts += #N i.t",
    f"{S} operation #E i.t = @s i.cts", f"{S} operation #E i.t /= #100 i.g", f"{S} operation @s i.cts %= #100 i.g",
    f"execute if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus += #E i.t",
    f"{S} operation @s i.jn += #E i.t", f"{S} operation @s i.jv += #E i.t", f"{S} operation @s i.h0 += #E i.t"]
fn("vente/encaisser", EN)

# heure : saturation qui se détend (x 23/24), frais de garde de la Banque
HE = []
for p in PL:
    HE += [f"{S} operation #x i.t = @s i.v_{p}", f"{S} operation #x i.t /= #24 i.g", f"{S} operation @s i.v_{p} -= #x i.t"]
HE += [f"execute if score @s i.bq matches 1 run function {NS}:banque/garde"]
# historique des recettes heure par heure (i.h0 = heure en cours, i.h11 = il y a 11 h), pour le graphique du tableau de l'île
HE += [f"execute if score @s i.h0 matches 1.. run function {NS}:prod/bilan_h"]
fn("prod/bilan_h", [f"execute store result storage {NS}:t bh.v int 1 run {S} get @s i.h0", f"function {NS}:prod/bilan_h_m with storage {NS}:t bh"])
fn("prod/bilan_h_m", "$tellraw @s " + L(PREFIX, T("Ta Halle a vendu pour ", "gray"), T("$(v) Écus", "#F7C843", True), T(" cette heure.", "gray"),
                                         '{text:"  [MON ÎLE]",color:"aqua",click_event:{action:"run_command",command:"/trigger industrie set 22"}}'))
HE += [f"{S} operation @s i.h{k} = @s i.h{k - 1}" for k in range(11, 0, -1)] + [f"{S} set @s i.h0 0"]
fn("prod/heure", HE)
GA = [f"{S} set #fg i.t 0"]
for p in PL:
    # 0,2 % par jour de la valeur de base, par heure : stock x p0 x 2 / 1000 / 24 (en centièmes)
    GA += [f"execute unless score @s i.o_{p} matches 0 if score @s i.s_{p} matches 1.. run function {NS}:banque/garde_{p}"]
    fn(f"banque/garde_{p}", [f"{S} operation #x i.t = @s i.s_{p}", f"{S} operation #x i.t /= #24 i.g", f"{S} set #y i.t {PROD[p][2] * GARDE_PM}",
                             f"{S} operation #x i.t *= #y i.t", f"{S} operation #x i.t /= #1000 i.g", f"{S} operation #fg i.t += #x i.t"])
GA += [f"{S} operation #fg i.t /= #100 i.g",
       f"execute if score #fg i.t matches 1.. if score @s c.ecus matches -2147483648.. run scoreboard players operation @s c.ecus -= #fg i.t",
       f"execute if score #fg i.t matches 1.. run {S} operation @s i.jn -= #fg i.t"]
fn("banque/garde", GA)

# jour : remise à zéro des compteurs du jour, contrats, prêt, dividendes, moyenne des recettes
JO = [f"{S} operation @s i.td = #jr i.t",
      f"{S} operation #x i.t = @s i.r7", f"{S} operation #x i.t *= #6 i.g" if False else f"{S} set #y i.t 6",
      f"{S} operation #x i.t *= #y i.t", f"{S} operation #x i.t += @s i.jn", f"{S} operation #x i.t /= #7 i.g", f"{S} operation @s i.r7 = #x i.t",
      f"{S} operation @s i.prev = @s i.jn",
      f"execute if score @s i.pv matches 1.. if score @s i.prev matches 1.. run function {NS}:parts/dividendes",
      f"{S} set @s i.jn 0", f"{S} set @s i.jb 0",
      f"execute if score @s i.dette matches 1.. run function {NS}:banque/jour",
      f"execute if score @s i.pban matches 1.. run {S} remove @s i.pban 1",
      f"function {NS}:contrat/tirer"]
JO += [f"{S} set @s i.j_{p} 0" for p in PL] + [f"{S} set @s i.w_{p} 0" for p in PL]
fn("prod/jour", JO)

exec(open(os.path.join(ICI, "ile.py"), encoding="utf-8").read())
exec(open(os.path.join(ICI, "machines.py"), encoding="utf-8").read())
exec(open(os.path.join(ICI, "economie.py"), encoding="utf-8").read())
exec(open(os.path.join(ICI, "menus.py"), encoding="utf-8").read())
exec(open(os.path.join(ICI, "guide.py"), encoding="utf-8").read())
exec(open(os.path.join(ICI, "cine.py"), encoding="utf-8").read())
exec(open(os.path.join(ICI, "stats.py"), encoding="utf-8").read())

# ------------------------------------------------------------------ resource pack : modèles des bâtiments
import modeles
META = modeles.exporter(RP, NS)

# ------------------------------------------------------------------ journal des Écus de Commerce, puis zip
exec(open(os.path.join(ICI, "..", "..", "metiers", "sources", "journal_ecus.py"), encoding="utf-8").read())
print("journal des Écus :", miroir_ecus(ROOT, "c.a_ind"), "lignes")
zp = os.path.join(ICI, "..", "industrie.zip")
if os.path.exists(zp):
    os.remove(zp)
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, _, fs in os.walk(ROOT):
        for f_ in sorted(fs):
            full = os.path.join(dp, f_)
            zi = zipfile.ZipInfo(os.path.relpath(full, ROOT).replace(os.sep, "/"), date_time=(2026, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, open(full, "rb").read())
print("industrie :", sum(len(f_) for _, _, f_ in os.walk(ROOT)), "fichiers, modèles :", len(META))


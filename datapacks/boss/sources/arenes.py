"""Les deux arenes, construites par commandes dans leur propre dimension (vide, nuit permanente).

Bibliotheque Interdite (Grimoire) : sommet de tour rond de 29 blocs, sol en y = 100 (on marche en y = 101),
mur de bibliotheques eventre, 4 piliers a runes, 4 pupitres de scellement (lutrins) en diagonale, sceau au centre,
traits de runes pupitre -> centre (obsidienne, qui devient pleureuse quand le pupitre est actif), tours au loin.

Champ maudit (Corbeau) : champ de 26 blocs de rayon, sol en y = 63 (on marche en y = 64), herbes seches, clotures
cassees, 5 epouvantails plantes (tete en citrouille), citrouilles-lanternes, arbres morts, barriere invisible a 24.
Toutes les coordonnees sont absolues dans la dimension de l'arene.
"""
import math, random

# ------------------------------------------------------------------------------------------ Bibliotheque
GY = 100                 # couche du sol
G_R = 14.4               # rayon du plateau
PUPITRES = [(8 * math.cos(math.radians(a)), 8 * math.sin(math.radians(a))) for a in (45, 135, 225, 315)]
PUPITRES = [(round(x), round(z)) for x, z in PUPITRES]          # (6,6) (-6,6) (-6,-6) (6,-6)
PILIERS = [(11, 0), (0, 11), (-11, 0), (0, -11)]
G_SPAWN = [(round(10 * math.cos(math.radians(a))), round(10 * math.sin(math.radians(a)))) for a in range(0, 360, 45)]


def _rng(n):
    return random.Random(n)


def ligne_runes(i):
    """Blocs du trait de runes du pupitre i (du pupitre vers le sceau)."""
    px, pz = PUPITRES[i]
    sx, sz = (1 if px > 0 else -1), (1 if pz > 0 else -1)
    return [(sx * k, sz * k) for k in range(2, abs(px))]


def bibliotheque():
    """Liste de commandes (a lancer « in boss:grimoire ») qui construit l'arene a neuf."""
    R = _rng(11)
    c = []
    for y in range(GY - 14, GY + 20, 3):          # nettoyage (fill limite a 32 768 blocs)
        c.append(f"fill -48 {y} -48 47 {y + 2} 47 minecraft:air")
    sol = ["deepslate_tiles"] * 5 + ["deepslate_bricks"] * 3 + ["cracked_deepslate_tiles"] * 2 + ["polished_deepslate"]
    for x in range(-15, 16):
        for z in range(-15, 16):
            d = math.hypot(x, z)
            if d > G_R:
                continue
            b = R.choice(sol)
            if 4.2 <= d <= 5.2:
                b = "amethyst_block" if (x + z) % 2 == 0 else "chiseled_deepslate"
            elif d < 1.5:
                b = "chiseled_deepslate"
            c.append(f"setblock {x} {GY} {z} minecraft:{b}")
            # dessous : la tour s'affine (cone) puis des racines de pierre qui pendent dans le vide
            prof = 1 + int(max(0, 6 - (d - 8)) if d > 8 else 6)
            for k in range(1, prof + 1):
                c.append(f"setblock {x} {GY - k} {z} minecraft:{R.choice(['deepslate_bricks', 'cobbled_deepslate', 'polished_blackstone_bricks'])}")
            if d < 6 and R.random() < .25:
                for k in range(prof + 1, prof + 1 + R.randint(2, 6)):
                    c.append(f"setblock {x} {GY - k} {z} minecraft:cobbled_deepslate")
    # mur de bibliotheques eventre
    for a10 in range(0, 3600, 35):
        a = math.radians(a10 / 10)
        x, z = round(15 * math.cos(a)), round(15 * math.sin(a))
        bre = (a10 // 35) % 23 in (0, 1) or (a10 // 35) % 17 == 5
        h = 0 if bre else R.randint(2, 4)
        if bre:
            continue
        c.append(f"setblock {x} {GY} {z} minecraft:deepslate_bricks")
        for k in range(1, h + 1):
            c.append(f"setblock {x} {GY + k} {z} minecraft:{'chiseled_bookshelf' if R.random() < .2 else 'bookshelf'}")
        c.append(f"setblock {x} {GY + h + 1} {z} minecraft:deepslate_brick_slab")
        if R.random() < .25:
            c.append(f"setblock {x} {GY + h + 2} {z} minecraft:candle[candles={R.randint(1, 4)},lit=true]")
    c += pilier_cmds()
    # pupitres (lutrins avec livre) + socle
    for i, (x, z) in enumerate(PUPITRES):
        face = "north" if z > 0 else "south"
        c.append(f"setblock {x} {GY} {z} minecraft:polished_blackstone")
        c.append(f"setblock {x} {GY + 1} {z} minecraft:lectern[facing={face},has_book=true]")
        for (lx, lz) in ligne_runes(i):
            c.append(f"setblock {lx} {GY} {lz} minecraft:obsidian")
    # livres tombes (tapis violets et pupitres renverses) et bougies
    for _ in range(14):
        a, d = R.random() * math.tau, R.uniform(9, 13)
        x, z = round(d * math.cos(a)), round(d * math.sin(a))
        c.append(f"setblock {x} {GY + 1} {z} minecraft:{R.choice(['purple_carpet', 'red_carpet', 'black_carpet', 'brown_carpet'])}")
    # lumiere invisible (sinon tout est noir : pas de lumiere du ciel ici)
    for x in range(-12, 13, 6):
        for z in range(-12, 13, 6):
            if math.hypot(x, z) < 14:
                c.append(f"setblock {x} {GY + 6} {z} minecraft:light[level=11]")
    # tours au loin, dans le vide
    for (tx, tz, h) in ((-34, -40, 24), (38, -46, 30), (-52, 14, 16), (50, 10, 20)):
        for y in range(GY - 30, GY - 30 + h):
            c.append(f"fill {tx - 2} {y} {tz - 2} {tx + 2} {y} {tz + 2} minecraft:{R.choice(['deepslate_bricks', 'polished_blackstone_bricks'])}")
        c.append(f"fill {tx - 2} {GY - 30 + h} {tz - 2} {tx + 2} {GY - 30 + h + 1} {tz + 2} minecraft:bookshelf")
        c.append(f"setblock {tx} {GY - 28 + h} {tz} minecraft:soul_lantern")
    return c


def pilier_cmds(seul=None, detruit=False):
    """Piliers a runes (hauts de 10). detruit=True : le pilier `seul` s'effondre (gravats au pied)."""
    c = []
    for i, (x, z) in enumerate(PILIERS):
        if seul is not None and i != seul:
            continue
        if detruit:
            c.append(f"fill {x - 1} {GY + 3} {z - 1} {x + 1} {GY + 12} {z + 1} minecraft:air")
            R = _rng(40 + i)
            for _ in range(9):
                gx, gz = x + R.randint(-3, 3), z + R.randint(-3, 3)
                if math.hypot(gx, gz) < 13.5:
                    c.append(f"setblock {gx} {GY + 1} {gz} minecraft:{R.choice(['cobbled_deepslate', 'polished_blackstone_bricks', 'cobbled_deepslate_slab'])}")
            continue
        for y in range(GY + 1, GY + 11):
            b = "chiseled_polished_blackstone" if (y - GY) % 3 == 0 else "polished_blackstone_bricks"
            c.append(f"fill {x - 1} {y} {z - 1} {x + 1} {y} {z + 1} minecraft:{b}")
        c.append(f"fill {x - 1} {GY + 11} {z - 1} {x + 1} {GY + 11} {z + 1} minecraft:polished_blackstone_brick_slab")
        c.append(f"setblock {x} {GY + 12} {z} minecraft:soul_lantern")
    return c


def bord_effondre():
    """Phase 3 : le bord du plateau (rayon 11,5 a 14,4) s'effondre ; liste de blocs tries par angle."""
    blocs = []
    for x in range(-15, 16):
        for z in range(-15, 16):
            d = math.hypot(x, z)
            if 11.6 <= d <= G_R and all(abs(x - px) + abs(z - pz) > 2 for px, pz in PILIERS):
                blocs.append((math.atan2(z, x), x, z))
    blocs.sort()
    return [(x, z) for _, x, z in blocs]


# ------------------------------------------------------------------------------------------ Champ maudit
CY = 63
C_R = 26
EPOUVANTAILS = [(round(17 * math.cos(math.radians(a))), round(17 * math.sin(math.radians(a)))) for a in (18, 90, 162, 234, 306)]
CITROUILLES = [(9, 4), (-6, 9), (-10, -5), (4, -11), (15, -2), (-2, 16), (-16, 6), (12, 12)]
C_SPAWN = [(round(12 * math.cos(math.radians(a))), round(12 * math.sin(math.radians(a)))) for a in range(0, 360, 45)]


def _face_vers_centre(x, z):
    if abs(x) > abs(z):
        return "west" if x > 0 else "east"
    return "north" if z > 0 else "south"


def champ():
    R = _rng(23)
    c = []
    for y in range(CY - 6, CY + 24, 3):
        c.append(f"fill -48 {y} -48 47 {y + 2} 47 minecraft:air")
    sol = ["coarse_dirt"] * 4 + ["podzol"] * 2 + ["rooted_dirt", "dirt", "mud"]
    c.append(f"fill -40 {CY - 4} -40 40 {CY - 1} 40 minecraft:dirt")
    for x in range(-40, 41):
        for z in range(-40, 41):
            d = math.hypot(x, z)
            if d > 40:
                continue
            c.append(f"setblock {x} {CY} {z} minecraft:{R.choice(sol)}")
            if d < 2.5:
                continue
            r = R.random()
            if r < .30:
                c.append(f"setblock {x} {CY + 1} {z} minecraft:short_dry_grass")
            elif r < .45:
                c.append(f"setblock {x} {CY + 1} {z} minecraft:tall_dry_grass")
            elif r < .49:
                c.append(f"setblock {x} {CY + 1} {z} minecraft:dead_bush")
            elif r < .50 and d > 6:
                c.append(f"setblock {x} {CY + 1} {z} minecraft:hay_block")
    # sillon que laisse la croix (de l'entree vers le centre)
    for k in range(3, 20):
        c.append(f"setblock 0 {CY} {-k} minecraft:mud")
        c.append(f"setblock 0 {CY + 1} {-k} minecraft:air")
    # clotures cassees
    for (x0, z0, n, dx, dz) in ((-20, -8, 9, 0, 1), (8, -21, 8, 1, 0), (-14, 18, 7, 1, 0), (20, 6, 6, 0, 1)):
        for k in range(n):
            if R.random() < .25:
                continue
            x, z = x0 + dx * k, z0 + dz * k
            c.append(f"setblock {x} {CY + 1} {z} minecraft:dark_oak_fence[{'north=true,south=true' if dz else 'east=true,west=true'}]")
            if R.random() < .5:
                c.append(f"setblock {x} {CY + 2} {z} minecraft:dark_oak_fence")
    # epouvantails plantes (piquet, corps de paille, bras, tete en citrouille, chapeau)
    for (x, z) in EPOUVANTAILS:
        f = _face_vers_centre(x, z)
        bras = "east=true,west=true" if f in ("north", "south") else "north=true,south=true"
        c += [f"setblock {x} {CY + 1} {z} minecraft:dark_oak_fence", f"setblock {x} {CY + 2} {z} minecraft:dark_oak_fence",
              f"setblock {x} {CY + 3} {z} minecraft:hay_block",
              f"setblock {x} {CY + 4} {z} minecraft:carved_pumpkin[facing={f}]",
              f"setblock {x} {CY + 5} {z} minecraft:black_carpet"]
        for s in (-1, 1):
            bx, bz = (x + s, z) if f in ("north", "south") else (x, z + s)
            c.append(f"setblock {bx} {CY + 3} {bz} minecraft:dark_oak_fence[{bras}]")
    for (x, z) in CITROUILLES:
        c.append(f"setblock {x} {CY + 1} {z} minecraft:jack_o_lantern[facing={_face_vers_centre(x, z)}]")
    # arbres morts hors de l'arene
    for (x, z, h) in ((-30, -14, 9), (31, -20, 11), (-27, 24, 8), (26, 27, 10), (4, -34, 12), (-36, 2, 7)):
        c.append(f"fill {x} {CY + 1} {z} {x} {CY + h} {z} minecraft:dark_oak_log")
        for (bx, by, bz) in ((1, h - 2, 0), (2, h - 1, 0), (-1, h - 3, 1), (0, h - 1, -1), (0, h, -2), (-2, h - 2, 0)):
            c.append(f"setblock {x + bx} {CY + by} {z + bz} minecraft:dark_oak_fence")
    # barriere invisible (on ne sort pas de l'arene pendant le combat)
    for a in range(0, 360, 2):
        x, z = round(24 * math.cos(math.radians(a))), round(24 * math.sin(math.radians(a)))
        c.append(f"fill {x} {CY + 1} {z} {x} {CY + 8} {z} minecraft:barrier")
    # un peu de lumiere froide
    for x in range(-18, 19, 9):
        for z in range(-18, 19, 9):
            c.append(f"setblock {x} {CY + 7} {z} minecraft:light[level=5]")
    return c

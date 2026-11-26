# -*- coding: utf-8 -*-
# 26/11/2026 : dessin du livre des menus (fond des panneaux et signets). Exécuté par ref_panneaux.py.
# Tout est procédural et toujours le même tirage (graine fixe par panneau) :
#   - couverture en toile sombre tissée, filet de laiton gaufré, coins de laiton rivetés, tranchefiles en haut et en bas ;
#   - double page : grain du papier, fibres, taches de rousseur, bords brunis, ombre de la reliure au centre,
#     pages bombées (plus claires au milieu de chaque page), tranche des feuilles sur les côtés et en bas ;
#   - ornements à l'encre (coins en volutes, filets doubles avec losange) et un médaillon gaufré sous chaque icône ;
#   - signet de tissu rouge qui pend sous le livre ;
#   - signets du haut en tissu tissé, couture en pointillé, ombre là où ils entrent dans le livre.
# Rendu en palettes limitées avec un tramage de Bayer, comme le reste de l'interface.
import math as _m
import random as _rd

_BAYL = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
_LAIT = [(255, 236, 160), (236, 196, 104), (206, 160, 70), (166, 120, 44), (118, 82, 28)]
_SOMB = (26, 18, 12)
PAPIER = [(250, 242, 220), (243, 233, 207), (236, 223, 193), (227, 212, 178), (216, 199, 162), (201, 182, 144),
          (182, 160, 122), (158, 135, 100)]
TOILE = [(70, 46, 40), (60, 39, 34), (51, 33, 29), (43, 28, 25), (36, 23, 21)]
ENCRE_L = (150, 118, 80)     # encre pâlie des ornements
ENCRE_F = (112, 84, 54)


def _tr(r, v, x, y):
    i = int(v + (_BAYL[y % 4][x % 4] + .5) / 16)
    return r[max(0, min(len(r) - 1, i))]


def _bruit(W, H, pas, graine):
    """Bruit de valeur lissé (grille aléatoire, interpolation douce), valeurs dans [0, 1]."""
    rnd = _rd.Random(graine)
    gw, gh = W // pas + 2, H // pas + 2
    g = [[rnd.random() for _ in range(gw)] for _ in range(gh)]
    out = [[0.0] * W for _ in range(H)]
    for y in range(H):
        fy, iy = (y / pas) % 1, y // pas
        sy = fy * fy * (3 - 2 * fy)
        for x in range(W):
            fx, ix = (x / pas) % 1, x // pas
            sx = fx * fx * (3 - 2 * fx)
            a = g[iy][ix] + (g[iy][ix + 1] - g[iy][ix]) * sx
            b = g[iy + 1][ix] + (g[iy + 1][ix + 1] - g[iy + 1][ix]) * sx
            out[y][x] = a + (b - a) * sy
    return out


def _volute(px, x0, y0, sx, sy, c1, c2):
    """Petit ornement de coin à l'encre (équerre + volute), orienté par sx, sy (+1 ou -1)."""
    pts1 = [(i, 0) for i in range(0, 14)] + [(0, j) for j in range(1, 14)]
    pts2 = [(2, 2), (3, 2), (4, 3), (4, 4), (3, 5), (2, 4), (3, 3), (6, 2), (8, 2), (10, 2), (2, 6), (2, 8), (2, 10),
            (5, 5), (6, 6)]
    for (i, j) in pts1:
        px[x0 + sx * i, y0 + sy * j] = c1 + (255,)
    for (i, j) in pts2:
        px[x0 + sx * i, y0 + sy * j] = c2 + (255,)


def _fond_livre(W, H, noeuds_xy=(), graine="livre"):
    """Livre ouvert de W x H (la bande des signets LIVRE_T en haut reste vide). noeuds_xy : centres des icônes."""
    im = _Img.new("RGBA", (W, H))
    px = im.load()
    T = LIVRE_T
    rnd = _rd.Random(graine)
    # ---------------- couverture : toile tissée
    for y in range(T, H):
        for x in range(W):
            d = min(x, y - T, W - 1 - x, H - 1 - y)
            if d == 0:
                c = _SOMB
            else:
                v = 1.2 + (y - T) / (H - T) * 1.8 + (.5 if (x + y) % 2 == 0 and (x // 2 + y // 2) % 2 else 0)
                c = _tr(TOILE, v, x, y)
                if d == 1:
                    c = TOILE[0] if min(x, y - T) == 1 else TOILE[4]
                if d == 4:   # filet de laiton gaufré
                    c = _LAIT[2] if min(x, y - T) == 4 else _LAIT[3]
                if d == 5:
                    c = TOILE[4]
            px[x, y] = c + (255,)
    # ---------------- tranche des feuilles (côtés et bas), sous les pages
    P0, P1 = T + 8, H - 11
    X0, X1 = 10, W - 11
    for k in range(3):
        for y in range(P0 + 2 + k, P1 + 1 + k):
            for x in (X0 - 1 - k, X1 + 1 + k):
                px[x, y] = ((232, 218, 186) if k % 2 == 0 else (176, 156, 120)) + (255,)
        for x in range(X0 - k, X1 + 1 + k):
            px[x, P1 + 1 + k] = ((230, 214, 180) if k % 2 == 0 else (172, 152, 116)) + (255,)
    # ---------------- pages
    SP = W // 2
    gros = _bruit(W, H, 23, graine + "g")
    fin = _bruit(W, H, 5, graine + "f")
    for y in range(P0, P1 + 1):
        for x in range(X0, X1 + 1):
            dsp = abs(x - SP)
            demi = (SP - X0) if x < SP else (X1 - SP)
            u = dsp / max(1, demi)                       # 0 à la reliure, 1 au bord extérieur
            bombe = .9 * (1 - _m.sin(u * _m.pi * .92))   # plus clair au milieu de chaque page
            gouttiere = max(0, 6 - dsp) * .22            # ombre douce de la reliure (pas de trait : des libellés passent dessus)
            bord = min(x - X0, X1 - x, y - P0, P1 - y)
            brun = max(0, 4 - bord) * .55                # bords brunis
            v = .9 + bombe * .7 + gouttiere + brun + (gros[y][x] - .5) * 1.6 + (fin[y][x] - .5) * .9 + (y - P0) / (P1 - P0) * .5
            px[x, y] = _tr(PAPIER, v, x, y) + (255,)
        # pli de la reliure
    # fibres et taches de rousseur
    for _ in range(W * H // 260):
        x, y = rnd.randint(X0 + 3, X1 - 6), rnd.randint(P0 + 3, P1 - 3)
        L = rnd.randint(2, 5)
        dx = rnd.choice((1, 1, 0))
        for i in range(L):
            xx, yy = x + i * dx, y + (i if dx == 0 else (i // 3) * rnd.choice((0, 1)))
            if X0 < xx < X1 and P0 < yy < P1:
                r, g, b, _a = px[xx, yy]
                px[xx, yy] = (int(r * .94), int(g * .93), int(b * .91), 255)
    for _ in range(W * H // 1800):
        x, y = rnd.randint(X0 + 4, X1 - 4), rnd.randint(P0 + 4, P1 - 4)
        for (dx, dy) in ((0, 0), (1, 0), (0, 1)) if rnd.random() < .6 else ((0, 0),):
            px[x + dx, y + dy] = (198, 164, 118, 255)
    # ---------------- ornements à l'encre
    m = 5
    for (cx, cy, sx, sy) in ((X0 + m, P0 + m, 1, 1), (SP - 3 - m, P0 + m, -1, 1), (SP + 3 + m, P0 + m, 1, 1), (X1 - m, P0 + m, -1, 1),
                             (X0 + m, P1 - m, 1, -1), (SP - 3 - m, P1 - m, -1, -1), (SP + 3 + m, P1 - m, 1, -1), (X1 - m, P1 - m, -1, -1)):
        _volute(px, cx, cy, sx, sy, ENCRE_L, ENCRE_F)
    # ---------------- médaillon gaufré sous chaque icône : disque éclairci, bord en relief, filet d'encre pâlie
    for (nx, ny) in noeuds_xy:
        for y in range(ny - 18, ny + 19):
            for x in range(nx - 18, nx + 19):
                if not (P0 < y < P1 and X0 < x < X1):
                    continue
                d = _m.hypot(x - nx, y - ny)
                if d > 17.5:
                    continue
                r, g, b, _a = px[x, y]
                haut = (y - ny) + (x - nx) * .4 < 0
                if d < 14:
                    k = 1.035
                elif d < 15.5:
                    k = 1.06 if haut else .9
                elif d < 16.5:
                    r, g, b = [int(v * .7 + e * .3) for v, e in zip((r, g, b), ENCRE_L)]
                    k = 1
                else:
                    k = .93 if not haut else 1.0
                px[x, y] = (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)), 255)
    # ---------------- coins de laiton rivetés (par-dessus la toile)
    for (cx, haut) in ((0, True), (W - 14, True), (0, False), (W - 14, False)):
        cy = T if haut else H - 14
        for j in range(14):
            for i in range(14):
                ii = i if cx == 0 else 13 - i
                jj = j if haut else 13 - j
                if ii + jj > 15:
                    continue
                if ii + jj == 15 or ii == 0 or jj == 0:
                    c = _SOMB if ii + jj == 15 else _LAIT[1]
                else:
                    c = _tr(_LAIT[1:], .2 + (ii + jj) / 15 * 2.6, cx + i, cy + j)
                px[cx + i, cy + j] = c + (255,)
        rx, ry = (cx + 4 if cx == 0 else cx + 8), (cy + 4 if haut else cy + 8)
        for (dx, dy, c) in ((0, 0, _LAIT[0]), (1, 0, _LAIT[1]), (0, 1, _LAIT[1]), (1, 1, _LAIT[4]), (2, 1, _LAIT[4]), (1, 2, _LAIT[4])):
            px[rx + dx, ry + dy] = c + (255,)
    # ---------------- tranchefiles (haut et bas de la reliure)
    for yy in (H - 4, H - 3):   # tranchefile : petit boudin rayé rouge et crème au pied de la reliure
        for xx in range(SP - 4, SP + 4):
            c = (186, 44, 44) if xx % 2 else (236, 214, 160)
            px[xx, yy] = (tuple(int(v * .75) for v in c) if yy == H - 3 else c) + (255,)
    # ---------------- signet de tissu qui pend sous le livre (à droite de la reliure)
    rx = SP + 22
    for y in range(H - 12, H):
        for x in range(rx, rx + 5):
            c = (150, 28, 34) if x in (rx, rx + 4) else (196, 46, 50) if x == rx + 1 else (176, 36, 42)
            px[x, y] = c + (255,)
    return im


def _signet(ic, col, actif, TW):
    """Signet du haut : tissu tissé de la couleur du pack, couture en pointillé, icône ; l'actif est plus haut et plus vif."""
    h = LIVRE_T + 6
    im = _Img.new("RGBA", (TW, h))
    px = im.load()
    top = 0 if actif else 4
    base = col if actif else tuple(int(v * .78) for v in col)
    clair = tuple(min(255, int(v * 1.25)) for v in base)
    fonce = tuple(int(v * .66) for v in base)
    tres_fonce = tuple(int(v * .45) for v in base)
    for y in range(top, h):
        for x in range(TW):
            if x in (0, TW - 1) or y == top:
                c = _SOMB
            elif x == 1 or y == top + 1:
                c = clair
            elif x == TW - 2:
                c = fonce
            else:
                tissage = .25 if (x + (y // 2)) % 2 == 0 else 0
                c = _tr([clair, base, fonce, tres_fonce], .5 + (y - top) / h * 1.6 + tissage, x, y)
                if (x == 3 or x == TW - 4 or y == top + 3) and (x + y) % 3 != 0 and 3 <= x <= TW - 4 and y >= top + 3:
                    c = clair if actif else tuple(min(255, int(v * 1.1)) for v in base)   # couture
            if y >= LIVRE_T + 2:   # ombre où le signet entre dans le livre
                c = tuple(int(v * .6) for v in c)
            px[x, y] = c + (255,)
    sh = _Img.new("RGBA", (16, 16), (0, 0, 0, 0))
    sh.putalpha(ic.split()[3].point(lambda a: 90 if a else 0))
    im.alpha_composite(sh, ((TW - 16) // 2 + 1, top + 4))
    im.alpha_composite(ic, ((TW - 16) // 2, top + 3))
    return im

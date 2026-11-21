"""Sons du pack Horreur synthetises en Python pur (pas de numpy) -> WAV mono 16 bits.

Les WAV sont ensuite encodes en OGG Vorbis (format exige par Minecraft) par ffmpeg.
Les sons qu'on ne sait pas synthetiser de facon credible (rire du Clown, voix de la Nonne)
sont fournis a la main dans datapacks/horreur/sons/ (WAV, MP3 ou OGG, convertis par ffmpeg).

  python sons.py          ecrit build/sons_wav/*.wav (pour ecouter avant d'integrer)
"""
import math, os, random, struct, wave

SR = 22050
ICI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ICI, "..", "build", "sons_wav")


# --- outils -----------------------------------------------------------------------------------
def silence(d):
    return [0.0] * int(d * SR)


def mixer(dst, src, debut=0.0, gain=1.0):
    i0 = int(debut * SR)
    if len(dst) < i0 + len(src):
        dst.extend([0.0] * (i0 + len(src) - len(dst)))
    for i, v in enumerate(src):
        dst[i0 + i] += v * gain
    return dst


def enveloppe(s, a=0.01, r=0.1):
    n, na, nr = len(s), max(1, int(a * SR)), max(1, int(r * SR))
    return [v * min(1.0, i / na, (n - i) / nr) for i, v in enumerate(s)]


def passe_bas(s, fc):
    a = 1 - math.exp(-2 * math.pi * fc / SR)
    y, out = 0.0, []
    for v in s:
        y += a * (v - y)
        out.append(y)
    return out


def passe_haut(s, fc):
    b = passe_bas(s, fc)
    return [v - w for v, w in zip(s, b)]


def passe_bande(s, f, q=4.0):
    """Biquad passe-bande (RBJ)."""
    w0 = 2 * math.pi * f / SR
    al = math.sin(w0) / (2 * q)
    b0, b2, a0, a1, a2 = al, -al, 1 + al, -2 * math.cos(w0), 1 - al
    x1 = x2 = y1 = y2 = 0.0
    out = []
    for x in s:
        y = (b0 * x + b2 * x2 - a1 * y1 - a2 * y2) / a0
        x2, x1, y2, y1 = x1, x, y1, y
        out.append(y)
    return out


def sature(s, k=3.0):
    t = math.tanh(k)
    return [math.tanh(k * v) / t for v in s]


def echo(s, d=0.18, fb=0.45, n=5):
    out = list(s) + [0.0] * int(d * SR * n)
    k = int(d * SR)
    for i in range(k, len(out)):
        out[i] += out[i - k] * fb
    return out


def normaliser(s, crete=0.89):
    m = max(1e-9, max(abs(v) for v in s))
    return [v * crete / m for v in s]


def bruit(d, graine):
    r = random.Random(graine)
    return [r.uniform(-1, 1) for _ in range(int(d * SR))]


def ecrire(nom, s):
    os.makedirs(OUT, exist_ok=True)
    s = normaliser(s)
    with wave.open(os.path.join(OUT, nom + ".wav"), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32767)) for v in s))
    print(f"  {nom}.wav  ({len(s) / SR:.1f} s)")


# --- Slender ----------------------------------------------------------------------------------
def slender_statique():
    """Grésillement de video corrompue : bruit hache, ronflement 50 Hz, coupures et bits ecrases."""
    d, r = 3.5, random.Random(7)
    n = bruit(d, 1)
    out = []
    etat, reste, crush = 1.0, 0, 1
    for i, v in enumerate(n):
        if reste <= 0:  # nouveau segment : volume, ecrasement de bits, coupure
            etat = r.choice((1.0, 1.0, 0.6, 0.25, 0.0))
            crush = r.choice((1, 4, 8, 16))
            reste = int(r.uniform(0.02, 0.18) * SR)
        reste -= 1
        t = i / SR
        hum = 0.35 * math.sin(2 * math.pi * 50 * t) + 0.15 * math.sin(2 * math.pi * 150 * t)
        x = v * etat * 0.8 + hum * (0.3 + 0.7 * etat)
        if crush > 1:
            x = round(x * crush) / crush
        out.append(x)
    out = passe_haut(out, 120)
    return enveloppe(out, 0.05, 0.4)


def slender_presence():
    """Drone grave qui bat (deux sinus tres proches) + souffle : on sent qu'il est la."""
    d = 6.0
    out = []
    for i in range(int(d * SR)):
        t = i / SR
        lent = 0.5 + 0.5 * math.sin(2 * math.pi * 0.25 * t)
        out.append(0.5 * math.sin(2 * math.pi * 41 * t) + 0.5 * math.sin(2 * math.pi * 43.3 * t)
                   + 0.2 * lent * math.sin(2 * math.pi * 82.5 * t + math.sin(2 * math.pi * 0.7 * t)))
    souffle = passe_bas(bruit(d, 3), 300)
    out = mixer(out, souffle, 0, 0.8)
    return enveloppe(sature(out, 1.5), 1.5, 2.0)


def slender_reveil():
    """Eclat sature : bruit + glissando qui plonge, coupe net."""
    d = 2.2
    out, ph = [], 0.0
    for i in range(int(d * SR)):
        t = i / SR
        f = 900 * math.exp(-2.2 * t) + 60
        ph += 2 * math.pi * f / SR
        out.append(0.7 * math.copysign(1, math.sin(ph)) + 0.3 * math.sin(ph * 1.5))
    out = mixer(out, slender_statique()[: int(d * SR)], 0, 0.9)
    return enveloppe(sature(out, 4.0), 0.005, 0.5)


# --- Siren Head -------------------------------------------------------------------------------
def siren_sirene():
    """Sirene d'alerte qui monte et descend, deux haut-parleurs desaccordes, megaphone + echo lointain."""
    d = 7.0
    out, p1, p2 = [], 0.0, 0.0
    for i in range(int(d * SR)):
        t = i / SR
        cycle = 0.5 - 0.5 * math.cos(2 * math.pi * t / 3.5)  # monte puis redescend en 3,5 s
        f = 300 + 520 * cycle
        p1 += 2 * math.pi * f / SR
        p2 += 2 * math.pi * f * 1.013 / SR
        dent = lambda p: 2 * ((p / (2 * math.pi)) % 1) - 1
        out.append(0.5 * dent(p1) + 0.5 * dent(p2))
    out = passe_bande(out, 1100, 0.8)  # son de megaphone
    out = sature(out, 2.5)
    out = echo(out, 0.33, 0.35, 6)  # resonne au loin
    return enveloppe(passe_bas(out, 3500), 0.4, 1.2)


def siren_voix():
    """« Radio » brouillee : formants de voix sur un buzz, hache comme une emission captee de loin."""
    d, r = 4.0, random.Random(11)
    out, ph = [], 0.0
    for i in range(int(d * SR)):
        t = i / SR
        ph += 2 * math.pi * (110 + 15 * math.sin(2 * math.pi * 3 * t)) / SR
        out.append(2 * ((ph / (2 * math.pi)) % 1) - 1)
    voix = [0.0] * len(out)
    voyelles = [(730, 1090), (270, 2290), (300, 870), (530, 1840), (660, 1720)]
    pos = 0.0
    while pos < d - 0.3:  # syllabes de 0,15 a 0,35 s
        lg = r.uniform(0.15, 0.35)
        f1, f2 = r.choice(voyelles)
        seg = out[int(pos * SR): int((pos + lg) * SR)]
        syl = [a + b for a, b in zip(passe_bande(seg, f1, 5), passe_bande(seg, f2, 6))]
        mixer(voix, enveloppe(syl, 0.02, 0.05), pos)
        pos += lg + r.choice((0.02, 0.05, 0.3))
    voix = mixer(voix, passe_bande(bruit(d, 12), 2000, 0.7), 0, 0.15)
    voix = sature(passe_bande(voix, 1200, 0.6), 3.0)
    return enveloppe(echo(voix, 0.29, 0.3, 4), 0.05, 0.6)


# --- Pinhead ----------------------------------------------------------------------------------
def tintement(f, d, graine):
    """Choc metallique : partiels inharmoniques qui decroissent vite."""
    r = random.Random(graine)
    out = []
    partiels = [(f * k * r.uniform(0.97, 1.03), r.uniform(0.3, 1.0), r.uniform(8, 25))
                for k in (1, 2.76, 5.40, 8.93)]
    for i in range(int(d * SR)):
        t = i / SR
        out.append(sum(a * math.exp(-dec * t) * math.sin(2 * math.pi * ff * t) for ff, a, dec in partiels))
    return out


def pinhead_chaines():
    """Chaine qu'on lance : cliquetis en rafale puis tension seche."""
    r = random.Random(5)
    out = silence(2.5)
    t = 0.0
    while t < 1.3:
        mixer(out, tintement(r.uniform(1800, 3200), 0.25, int(t * 1000)), t, r.uniform(0.3, 0.8))
        mixer(out, enveloppe(passe_haut(bruit(0.03, int(t * 997)), 2500), 0.001, 0.02), t, 0.5)
        t += r.uniform(0.03, 0.09)
    mixer(out, tintement(700, 1.0, 99), 1.4, 1.4)  # la chaine se tend
    mixer(out, enveloppe(passe_bande(bruit(0.4, 98), 900, 2), 0.002, 0.3), 1.4, 0.8)
    return enveloppe(out, 0.005, 0.3)


def pinhead_cloche():
    """Glas grave et long qui annonce Pinhead."""
    out = silence(6.0)
    for k, (m, a, dec) in enumerate([(0.5, 0.8, 0.5), (1.0, 1.0, 0.7), (1.19, 0.6, 0.9), (1.5, 0.5, 1.1),
                                     (2.0, 0.4, 1.4), (2.74, 0.3, 2.0), (4.07, 0.2, 2.8)]):
        f = 110 * m
        s = [a * math.exp(-dec * i / SR) * math.sin(2 * math.pi * f * i / SR + 0.3 * math.sin(2 * math.pi * 2.1 * i / SR))
             for i in range(len(out))]
        mixer(out, s)
    return enveloppe(echo(out, 0.41, 0.25, 3), 0.003, 1.5)


# --- Herobrine --------------------------------------------------------------------------------
def herobrine_apparition():
    """Souffle inverse qui monte puis s'arrete net (comme un son joue a l'envers)."""
    d = 2.5
    n = passe_bande(bruit(d, 21), 700, 1.2)
    out = []
    for i, v in enumerate(n):
        t = i / SR
        out.append(v * (t / d) ** 3 + 0.4 * (t / d) ** 4 * math.sin(2 * math.pi * 55 * t))
    out += silence(0.6)
    return out


SONS = {
    "slender_statique": slender_statique, "slender_presence": slender_presence, "slender_reveil": slender_reveil,
    "siren_sirene": siren_sirene, "siren_voix": siren_voix,
    "pinhead_chaines": pinhead_chaines, "pinhead_cloche": pinhead_cloche,
    "herobrine_apparition": herobrine_apparition,
}

# Sons fournis a la main (datapacks/horreur/sons/<nom>.wav|.mp3|.ogg|.flac) : absents -> sons vanilla en jeu
MANUELS = ("clown_rire", "nonne_murmure")
SOUS_TITRES = {
    "slender_statique": ("Grésillement", "Static crackles"),
    "slender_presence": ("Une présence…", "Something is near"),
    "slender_reveil": ("SlenderMan hurle", "SlenderMan screams"),
    "siren_sirene": ("Une sirène retentit", "A siren wails"),
    "siren_voix": ("Une radio brouillée", "Garbled radio"),
    "pinhead_chaines": ("Des chaînes claquent", "Chains rattle"),
    "pinhead_cloche": ("Un glas sonne", "A bell tolls"),
    "herobrine_apparition": ("Un souffle", "A rush of air"),
    "clown_rire": ("Un clown rit", "A clown laughs"),
    "nonne_murmure": ("Une voix murmure", "A voice whispers"),
}
DOSSIER_MANUELS = os.path.join(ICI, "..", "sons")


def ffmpeg():
    import glob, shutil
    f = shutil.which("ffmpeg")
    if f:
        return f
    pistes = glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages",
                                    "Gyan.FFmpeg*", "*", "bin", "ffmpeg.exe"))
    return pistes[0] if pistes else None


def manuel(nom):
    for ext in (".ogg", ".wav", ".mp3", ".flac"):
        p = os.path.join(DOSSIER_MANUELS, nom + ext)
        if os.path.exists(p):
            return p
    return None


def disponibles():
    """Noms des sons presents dans le resource pack (le datapack choisit sinon un son vanilla)."""
    if not ffmpeg():
        return set()
    return set(SONS) | {n for n in MANUELS if manuel(n)}


def generer_rp(assets):
    """Encode les sons en OGG Vorbis dans <assets>/sounds/ et ecrit sounds.json + sous-titres."""
    import json, subprocess
    ff = ffmpeg()
    if not ff:
        print("  ATTENTION : ffmpeg introuvable (winget install Gyan.FFmpeg) -> pas de sons personnalises")
        return set()
    os.makedirs(os.path.join(assets, "sounds"), exist_ok=True)
    sources = {}
    for nom, f in SONS.items():
        ecrire(nom, f())
        sources[nom] = os.path.join(OUT, nom + ".wav")
    for nom in MANUELS:
        p = manuel(nom)
        if p:
            sources[nom] = p
            print(f"  {nom} : fichier fourni ({os.path.basename(p)})")
        else:
            print(f"  {nom} : absent de datapacks/horreur/sons/ -> son vanilla en jeu")
    evenements, fr, en = {}, {}, {}
    for nom, src in sources.items():
        dst = os.path.join(assets, "sounds", nom + ".ogg")
        # mono (le son est positionne dans l'espace), Vorbis qualite 4, metadonnees retirees -> build reproductible
        subprocess.run([ff, "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", "44100", "-c:a", "libvorbis",
                        "-q:a", "4", "-map_metadata", "-1", "-fflags", "+bitexact", "-flags:a", "+bitexact", dst],
                       check=True)
        cle = "horreur.sous_titre." + nom
        evenements[nom.replace("_", ".", 1)] = {"subtitle": cle, "sounds": [{"name": "horreur:" + nom, "stream": True}]}
        fr[cle], en[cle] = SOUS_TITRES[nom]
    with open(os.path.join(assets, "sounds.json"), "w", encoding="utf-8") as f:
        json.dump(evenements, f, ensure_ascii=False, indent=1)
    for langue, txt in (("fr_fr", fr), ("en_us", en)):
        os.makedirs(os.path.join(assets, "lang"), exist_ok=True)
        with open(os.path.join(assets, "lang", langue + ".json"), "w", encoding="utf-8") as f:
            json.dump(txt, f, ensure_ascii=False, indent=1)
    print(f"  {len(sources)} sons encodes en OGG")
    return set(sources)


if __name__ == "__main__":
    print("Sons de synthese ->", os.path.normpath(OUT))
    for nom, f in SONS.items():
        ecrire(nom, f())

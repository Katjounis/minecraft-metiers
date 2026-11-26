# Fabrique les sons d'interface (à relancer seulement pour les modifier ; les .ogg sont versés au dépôt).
#   clic_laiton.ogg : clic des boutons, petit choc métallique sourd (remplace ui.button.click).
# Usage : python3 sons_interface.py   (demande ffmpeg avec libvorbis)
import math, os, random, struct, subprocess, wave

ICI = os.path.dirname(os.path.abspath(__file__))
SR = 44100


def clic():
    rnd = random.Random(7)
    n = int(SR * .11)
    out = []
    for i in range(n):
        t = i / SR
        # partiels inharmoniques d'une petite pièce de laiton, amortis vite
        metal = sum(a * math.sin(2 * math.pi * f * t) * math.exp(-t * d) for f, a, d in
                    ((1870, .30, 55), (2910, .22, 70), (4380, .12, 95), (6120, .06, 130)))
        # corps sourd (le bouton qui s'enfonce)
        corps = .55 * math.sin(2 * math.pi * 260 * t) * math.exp(-t * 60)
        # attaque bruitée très courte
        attaque = (rnd.random() * 2 - 1) * .35 * math.exp(-t * 900)
        out.append((metal + corps + attaque) * .6)
    m = max(abs(v) for v in out)
    return [v / m * .7 for v in out]


def ecrit(nom, ech):
    wav = os.path.join(ICI, nom + ".wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32767)) for v in ech))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "5", os.path.join(ICI, nom + ".ogg")], check=True)
    os.remove(wav)


ecrit("clic_laiton", clic())
print("sons écrits")

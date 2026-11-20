"""Client RCON minimal.
Usage : python rcon.py [--port 25576] [--password test] "commande 1" "commande 2" ...
Sans commande : lit une commande par ligne sur l'entree standard (# = commentaire)."""
import argparse, socket, struct, sys

def paquet(i, t, corps):
    b = corps.encode("utf-8")
    return struct.pack("<iii", len(b) + 10, i, t) + b + b"\0\0"

def lire(s):
    def exact(n):
        d = b""
        while len(d) < n:
            m = s.recv(n - len(d))
            if not m:
                raise ConnectionError("connexion fermee par le serveur")
            d += m
        return d
    n = struct.unpack("<i", exact(4))[0]
    d = exact(n)
    return struct.unpack("<i", d[:4])[0], d[8:-2].decode("utf-8", "replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=25576)
    ap.add_argument("--password", default="test")
    ap.add_argument("-q", "--quiet", action="store_true", help="n'affiche pas les commandes envoyees")
    ap.add_argument("commandes", nargs="*")
    a = ap.parse_args()
    cmds = a.commandes or [l.strip() for l in sys.stdin if l.strip() and not l.lstrip().startswith("#")]
    try:
        s = socket.create_connection((a.host, a.port), timeout=10)
    except OSError:
        sys.exit(f"Serveur injoignable sur {a.host}:{a.port} (il est demarre ?)")
    s.send(paquet(1, 3, a.password))
    if lire(s)[0] == -1:
        sys.exit("Mot de passe RCON refuse")
    for c in cmds:
        c = c.lstrip("/")
        s.send(paquet(2, 2, c))
        rep = lire(s)[1]
        if not a.quiet:
            print(">", c)
        if rep:
            print("  ", rep)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

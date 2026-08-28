#!/usr/bin/env python3
"""Check every published file against what the chain actually returns.

Why this exists
---------------
The manifest proves the local package is intact. It says nothing about whether
what reached Arweave is the same thing, and nothing about whether the upload log
paired each file with the right transaction.

That second question turned out to matter. The uploader used to match the
transactions the CLI returned to the paths it had been given by position, and
that order is not guaranteed. Where it slipped, every file in the batch was
recorded against its neighbour's transaction — a uniform shift by one. Two such
batches are known: 62 files under hindi canto-04 chapter-22, and 19 under
canto-02 chapter-03. Sampling found the first and missed the second, then a
one-file-per-batch sweep found the second and missed the first: with a shift that
spares part of a batch, a sample can always miss it. Only reading every file
settles it.

What it reports
---------------
For each file, one of:
  ok        the transaction returns exactly this file
  cruzado   it returns a different file of the archive, named in the report
  ajeno     it returns something not in the manifest at all
  sin_red   no gateway answered after the retries

`cruzado` is a bookkeeping fault, not a loss: the content is on the chain either
way, and the manifest — which pairs hash with path and never touches a
transaction id — is unaffected.

Resumable
---------
Results are appended to the report as they are found, and a run picks up where
the last one stopped. Roughly one file a second means the better part of a day,
so it will be interrupted.

Usage
-----
    python3 scripts/verify_chain.py            # continue, or start
    python3 scripts/verify_chain.py --resumen  # read the report, fetch nothing
"""
import argparse
import hashlib
import json
import os
import queue
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict

ARCHIVE = os.path.expanduser("~/vedabase-archive")
ESTADO = os.path.join(ARCHIVE, "UPLOAD-STATE.json")
MANIFIESTO = os.path.join(ARCHIVE, "MANIFEST.sha256")
INFORME = os.path.join(ARCHIVE, "VERIFY-CHAIN.jsonl")

# Rotated per file. One gateway's 404 means little — its index may simply not
# hold the file yet — so a negative is only believed after all of them, twice.
PASARELAS = ["https://arweave.net", "https://ar-io.dev",
             "https://permagate.io", "https://ardrive.net"]

# The gateway's own error pages, which must never be mistaken for content.
BASURA = {b"Not found"}
TAM_404 = 2035


def sha(datos):
    return hashlib.sha256(datos).hexdigest()


def sha_fichero(ruta, bloque=1 << 20):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(bloque), b""):
            h.update(trozo)
    return h.hexdigest()


def hash_a_ruta():
    d = {}
    with open(MANIFIESTO, encoding="utf-8") as f:
        for l in f:
            if l.startswith("#") or not l.strip():
                continue
            h, r = l.split("  ", 1)
            d[h] = r.strip()
    return d


def baja(tx, rondas=2, desde=0):
    """Bytes from the first gateway that answers with something real.

    `desde` rotates which gateway is tried first, so parallel workers spread
    their load instead of all leaning on the same one and being throttled.
    """
    for _ in range(rondas):
        for j in range(len(PASARELAS)):
            g = PASARELAS[(desde + j) % len(PASARELAS)]
            try:
                r = subprocess.run(["curl", "-sL", "--max-time", "120",
                                    f"{g}/{tx}"], capture_output=True, timeout=150)
            except subprocess.TimeoutExpired:
                continue
            d = r.stdout
            if d and len(d) != TAM_404 and d not in BASURA:
                return d
        time.sleep(3)
    return None


def hechos():
    if not os.path.isfile(INFORME):
        return set()
    v = set()
    with open(INFORME, encoding="utf-8") as f:
        for l in f:
            try:
                v.add(json.loads(l)["f"])
            except Exception:
                pass
    return v


def resumen():
    if not os.path.isfile(INFORME):
        print("todavia no hay informe")
        return 1
    est = Counter()
    cruces = []
    with open(INFORME, encoding="utf-8") as f:
        for l in f:
            try:
                d = json.loads(l)
            except Exception:
                continue
            est[d["e"]] += 1
            if d["e"] == "cruzado":
                cruces.append((d["f"], d.get("d", "?"), d.get("at", "?")))
    total = sum(est.values())
    print(f"comprobados {total:,}")
    for k, v in est.most_common():
        print(f"  {k:9} {v:>7,}  {100*v/total:5.2f} %")
    if cruces:
        por_lote = defaultdict(list)
        for f_, d_, at in cruces:
            por_lote[at].append(f_)
        print(f"\nlotes con cruces: {len(por_lote)}")
        for at, fs in sorted(por_lote.items(), key=lambda x: -len(x[1])):
            print(f"  {at}  {len(fs):>4} ficheros  p.ej. {fs[0].split('/')[-1]}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--resumen", action="store_true",
                    help="read the report and stop; fetch nothing")
    ap.add_argument("--limite", type=int, help="stop after this many files")
    ap.add_argument("--hilos", type=int, default=8,
                    help="parallel workers (default 8, two per gateway)")
    args = ap.parse_args()

    if args.resumen:
        return resumen()

    est = json.load(open(ESTADO, encoding="utf-8"))["uploaded"]
    h2r = hash_a_ruta()
    ya = hechos()
    pendientes = [k for k in sorted(est)
                  if k not in ya and est[k].get("tx")
                  and os.path.exists(os.path.join(ARCHIVE, k))]
    print(f"{len(ya):,} ya comprobados, {len(pendientes):,} por comprobar")
    if args.limite:
        pendientes = pendientes[:args.limite]

    t0 = time.time()
    cuenta = Counter()
    tareas = queue.Queue()
    for n, k in enumerate(pendientes):
        tareas.put((n, k))
    cerrojo = threading.Lock()
    inf = open(INFORME, "a", encoding="utf-8")
    hecho = [0]

    def obrero(idx):
        while True:
            try:
                n, k = tareas.get_nowait()
            except queue.Empty:
                return
            tx = est[k]["tx"]
            local = sha_fichero(os.path.join(ARCHIVE, k))
            # An anomaly is only believed after asking every gateway. Filtering
            # error pages by their contents does not work: each gateway invents
            # its own, and a new one appears the moment the list looks complete.
            # permagate answers with 95 bytes of "upstream connect error", ar-io
            # with nine bytes of "Not found", arweave.net with a 2 KB page of
            # HTML — and any of them, hashed, looks exactly like a file that does
            # not belong. So the rule is not "recognise the rubbish" but "one
            # gateway returning the file is enough, and no single gateway's
            # refusal counts."
            datos = baja(tx, desde=idx)
            h = sha(datos) if datos else None
            if h != local:
                for j in range(len(PASARELAS)):
                    d2 = baja(tx, rondas=1, desde=idx + 1 + j)
                    if d2 and sha(d2) == local:
                        datos, h = d2, local
                        break
                    if d2 and h is None:
                        datos, h = d2, sha(d2)
            if datos is None:
                e, otro = "sin_red", None
            elif h == local:
                e, otro = "ok", None
            elif h in h2r:
                e, otro = "cruzado", h2r[h]
            else:
                e, otro = "ajeno", None
            fila = {"f": k, "e": e, "at": est[k].get("at")}
            if otro:
                fila["d"] = otro
            with cerrojo:
                cuenta[e] += 1
                hecho[0] += 1
                inf.write(json.dumps(fila, ensure_ascii=False) + "\n")
                inf.flush()
                if e in ("cruzado", "ajeno"):
                    print(f"  {e.upper()}  {k}" + (f"  -> {otro}" if otro else ""),
                          flush=True)
                i = hecho[0]
                if i % 500 == 0:
                    v = i / (time.time() - t0)
                    queda = (len(pendientes) - i) / v / 3600 if v else 0
                    print(f"  {i:,}/{len(pendientes):,}  {dict(cuenta)}  "
                          f"{v:.1f} fich/s  quedan {queda:.1f} h", flush=True)

    hilos = [threading.Thread(target=obrero, args=(i,), daemon=True)
             for i in range(args.hilos)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    inf.close()
    print(f"\nesta sesion: {dict(cuenta)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

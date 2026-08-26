#!/usr/bin/env python3
"""Pack the two OCR sections into one tar per book, deterministically.

Why this exists
---------------
The OCR output is 81,273 tiny text files — one per page, per engine. Measured
against the Turbo price API on 2026-08-26, an upload costs

    9,174,313 winc per file  +  11,184.90 winc per byte

so those files carry 0.75 credits of pure per-file overhead, and at the CLI's
measured 0.58 s/file they take about thirteen hours to push. Neither is huge,
but nobody browses raw OCR page by page: it is intermediate evidence, consulted
as a set when someone wants to re-check a collation. A container per book is
the right shape for it.

The corpus, the scans and the reports are NOT packed. Those are the things
people actually read, and being addressable one file at a time from any gateway
is most of their value.

Why tar and not zip or gzip
---------------------------
tar is uncompressed and its format is documented in POSIX. A single flipped bit
damages one member; the rest still extract. Compression was rejected earlier for
exactly this reason: it couples every byte to every other, and it bets on a
decompressor still existing in fifty years. `ustar` is the most conservative
tar variant that fits these paths (longest is 112 chars, split across the 155
byte prefix and the 100 byte name field).

Determinism
-----------
Same input, same bytes out, on any machine: members sorted by path, uid/gid
zeroed, owner names emptied, ustar format. Real mtimes are kept — they are
genuine metadata about when the OCR ran, and the archive already records them.

Verification
------------
A container is only worth using if its contents can be checked without trusting
the container. So this writes OCR-CONTENTS.sha256, one line per member, and
after writing each tar it re-reads it and compares every member against the
file on disk. A tar that does not round-trip is deleted, not shipped.

The duplicate
-------------
build_archive.py walked both the per-volume Surya directories (SB1.1 … SB10.3)
and the merged srimad-bhagavatam/ that contains those same volumes, so 11,474
files landed in the archive twice, byte for byte. Verified 2026-08-26: the
11,474 relative paths match exactly and all 11,474 hashes match. Only the
merged copy is packed, which is also how every other book is named.

Usage
-----
    python3 scripts/pack_ocr.py --dry-run     # plan, writing nothing
    python3 scripts/pack_ocr.py               # pack and verify
"""
import argparse
import hashlib
import os
import sys
import tarfile

ARCHIVE = os.path.expanduser("~/vedabase-archive")
SECTIONS = ("ocr-surya", "ocr-tesseract")
DESTINO = os.path.join(ARCHIVE, "ocr-packed")
CONTENTS = os.path.join(DESTINO, "OCR-CONTENTS.sha256")

# Duplicated inside ocr-surya/srimad-bhagavatam/. See the docstring.
def es_duplicado(seccion, libro):
    return seccion == "ocr-surya" and libro.startswith("SB") and "." in libro


def sha256(ruta, bloque=1 << 20):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(bloque), b""):
            h.update(trozo)
    return h.hexdigest()


def miembros(base):
    """Every file under base, as (relative path, absolute path), path-sorted."""
    out = []
    for dp, dn, fn in os.walk(base):
        dn.sort()
        for f in sorted(fn):
            if f.startswith("."):
                continue
            p = os.path.join(dp, f)
            out.append((os.path.relpath(p, base).replace(os.sep, "/"), p))
    out.sort(key=lambda x: x[0].encode("utf-8"))
    return out


def normaliza(ti):
    """Strip everything that would differ between machines."""
    ti.uid = ti.gid = 0
    ti.uname = ti.gname = ""
    ti.mode = 0o644 if ti.isfile() else 0o755
    return ti


def empaqueta(destino, base, libro, items):
    tmp = destino + ".tmp"
    with tarfile.open(tmp, "w", format=tarfile.USTAR_FORMAT) as tf:
        for rel, absoluto in items:
            ti = tf.gettarinfo(absoluto, arcname=f"{libro}/{rel}")
            with open(absoluto, "rb") as f:
                tf.addfile(normaliza(ti), f)
    os.replace(tmp, destino)


def verifica(destino, libro, items, esperado):
    """Re-read the tar and compare every member against the file on disk.

    Returns None if it round-trips, or the first discrepancy found.
    """
    with tarfile.open(destino, "r") as tf:
        leidos = {}
        for ti in tf:
            if not ti.isfile():
                continue
            leidos[ti.name] = hashlib.sha256(tf.extractfile(ti).read()).hexdigest()
    if len(leidos) != len(items):
        return f"{len(leidos)} miembros en el tar, {len(items)} esperados"
    for rel, _ in items:
        nombre = f"{libro}/{rel}"
        if nombre not in leidos:
            return f"falta {nombre}"
        if leidos[nombre] != esperado[rel]:
            return f"hash distinto en {nombre}"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    trabajo = []
    for sec in SECTIONS:
        base = os.path.join(ARCHIVE, sec)
        if not os.path.isdir(base):
            sys.exit(f"no existe {base}")
        for libro in sorted(os.listdir(base)):
            ruta = os.path.join(base, libro)
            if not os.path.isdir(ruta):
                continue
            if es_duplicado(sec, libro):
                continue
            trabajo.append((sec, libro, ruta))

    if args.dry_run:
        A, B, W = 9174313, 11184.90, 1e12
        tf = tb = 0
        print(f"{'seccion':16} {'libro':46} {'fich':>7} {'MB':>8}")
        for sec, libro, ruta in trabajo:
            items = miembros(ruta)
            n = len(items)
            b = sum(os.path.getsize(p) for _, p in items)
            tf += n
            tb += b
            print(f"{sec:16} {libro[:46]:46} {n:>7} {b/1e6:>8.2f}")
        print(f"\n{len(trabajo)} contenedores, {tf} ficheros, {tb/1e6:.1f} MB")
        print(f"  sueltos: {(tf*A + tb*B)/W:.3f} cr   ~{tf*0.58/3600:.1f} h")
        print(f"  en tar : {(len(trabajo)*A + tb*B)/W:.3f} cr   ~{len(trabajo)*0.58/3600:.2f} h")
        return 0

    os.makedirs(DESTINO, exist_ok=True)
    lineas = []
    for sec, libro, ruta in trabajo:
        items = miembros(ruta)
        esperado = {rel: sha256(p) for rel, p in items}
        nombre = f"{sec}-{libro}.tar"
        destino = os.path.join(DESTINO, nombre)

        empaqueta(destino, ruta, libro, items)
        fallo = verifica(destino, libro, items, esperado)
        if fallo:
            os.remove(destino)
            sys.exit(f"PARADO: {nombre} no cuadra: {fallo}")

        for rel, _ in items:
            lineas.append(f"{esperado[rel]}  {nombre}!{libro}/{rel}")
        print(f"  {nombre:60} {len(items):>6} miembros  "
              f"{os.path.getsize(destino)/1e6:>7.2f} MB  ok", flush=True)

    # sha256 of each container, then of every member inside it
    cabecera = [f"{sha256(os.path.join(DESTINO, f))}  {f}"
                for f in sorted(os.listdir(DESTINO)) if f.endswith(".tar")]
    with open(CONTENTS, "w", encoding="utf-8") as f:
        f.write("# sha256 of each container, then of every member as tar!path\n")
        f.write("\n".join(cabecera) + "\n")
        f.write("\n".join(sorted(lineas)) + "\n")

    print(f"\n{len(trabajo)} contenedores verificados, "
          f"{len(lineas)} miembros en {CONTENTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Hash manifest of the corpus, so it can be anchored beyond our control.

What it is for
--------------
The whole project rests on one claim: this text is that of the first editions
and we have not touched it. Today that claim rests on the word of whoever
publishes it and on a repository that same person controls and could rewrite.

This manifest turns the claim into something checkable. It computes the SHA-256
of every file in the corpus, orders them deterministically, and produces a
`root` that stands for the whole set. Publish that `root` somewhere nobody can
rewrite — Arweave — and anyone can repeat the computation over their own copy
and see whether it matches, without asking us and without trusting us.

It is the same principle as PRINT_ERRATA.md: we do not ask to be believed, we
show how to check. Applied here to ourselves, and over time.

What it does NOT prove
----------------------
That the text is faithful to the printed page. That is what the collation
against the scans demonstrates, not a hash. The manifest only freezes the
result with a date, so that it cannot later be disputed whether the corpus
changed without saying so.

Determinism
-----------
Same corpus = same `root`, on any machine. Hence: relative paths always with
`/`, ordering by the bytes of the path, and the `root` computed over the lines
of the manifest, not over metadata that varies (dates, machine names).

Usage
-----
    python3 scripts/hash_manifest.py                # writes MANIFEST.sha256
    python3 scripts/hash_manifest.py --check        # verifies the existing one
    python3 scripts/hash_manifest.py --with-scans   # adds the PDFs from scan_vedabase
"""
import argparse
import hashlib
import os
import subprocess
import sys
from datetime import datetime, timezone

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
SALIDA = os.path.join(RAIZ, "MANIFEST.sha256")
SCANS = os.path.expanduser("~/git_projects/scan_vedabase")

# Lo que entra en el manifiesto. El .git queda fuera a proposito: es historia
# mutable (un rebase la cambia) y no es el objeto que se certifica.
EXTENSIONES = (".md", ".jsonl")
EXCLUIR_DIRS = {".git", "__pycache__", "node_modules", ".deploy-state"}


def sha256(ruta, bloque=1 << 20):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(bloque), b""):
            h.update(trozo)
    return h.hexdigest()


def recorrer(base, extensiones=None):
    """Rutas relativas, ordenadas por bytes, con '/' como separador."""
    encontradas = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in EXCLUIR_DIRS]
        for n in filenames:
            if n.startswith("."):
                continue
            if extensiones and not n.endswith(extensiones):
                continue
            completa = os.path.join(dirpath, n)
            rel = os.path.relpath(completa, base).replace(os.sep, "/")
            encontradas.append((rel, completa))
    encontradas.sort(key=lambda p: p[0].encode("utf-8"))
    return encontradas


def commit_actual():
    try:
        return subprocess.check_output(
            ["git", "-C", RAIZ, "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "(sin git)"


def build(with_scans=False):
    lineas = []
    total_bytes = 0

    for rel, completa in recorrer(RAIZ, EXTENSIONES):
        lineas.append(f"{sha256(completa)}  corpus/{rel}")
        total_bytes += os.path.getsize(completa)

    if with_scans and os.path.isdir(SCANS):
        for sub in ("originals", "improved"):
            base = os.path.join(SCANS, sub)
            if not os.path.isdir(base):
                continue
            for rel, completa in recorrer(base, (".pdf",)):
                lineas.append(f"{sha256(completa)}  scans/{sub}/{rel}")
                total_bytes += os.path.getsize(completa)

    cuerpo = "\n".join(lineas) + "\n"
    root = hashlib.sha256(cuerpo.encode("utf-8")).hexdigest()
    return lineas, cuerpo, root, total_bytes


def escribir(lineas, cuerpo, root, total_bytes):
    cab = [
        "# Manifiesto de integridad — vedabase-original",
        "#",
        "# El `root` de abajo es el SHA-256 de las lineas de este manifiesto,",
        "# excluida esta cabecera. Se publica en Arweave; su identificador de",
        "# transaccion queda en ANCLAS.md.",
        "#",
        "# Comprobarlo por tu cuenta:",
        "#     python3 scripts/hash_manifest.py --check",
        "#",
        f"# fecha:    {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"# commit:   {commit_actual()}",
        f"# ficheros: {len(lineas)}",
        f"# bytes:    {total_bytes}",
        f"# root:     {root}",
        "#",
    ]
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(cab) + "\n" + cuerpo)


def leer_root_guardado():
    if not os.path.isfile(SALIDA):
        return None, None
    guardado, lineas = None, []
    with open(SALIDA, encoding="utf-8") as f:
        for l in f:
            if l.startswith("# root:"):
                guardado = l.split(":", 1)[1].strip()
            elif not l.startswith("#"):
                lineas.append(l.rstrip("\n"))
    cuerpo = "\n".join(lineas) + "\n" if lineas else ""
    return guardado, cuerpo


def main():
    ap = argparse.ArgumentParser(description="Hash manifest of the corpus.")
    ap.add_argument("--check", action="store_true",
                    help="recompute and compare against the stored manifest")
    ap.add_argument("--with-scans", action="store_true",
                    help="add the PDFs from scan_vedabase (originals + improved)")
    args = ap.parse_args()

    lineas, cuerpo, root, total = build(args.with_scans)

    if args.check:
        guardado, cuerpo_guardado = leer_root_guardado()
        if guardado is None:
            print("There is no MANIFEST.sha256 to check.")
            return 1
        recomputado = hashlib.sha256(cuerpo_guardado.encode("utf-8")).hexdigest()
        print(f"root stored in the header    : {guardado}")
        print(f"root recomputed from body    : {recomputado}")
        print(f"root of the corpus on disk   : {root}")
        if guardado != recomputado:
            print("\nFAIL: the header does not match the body of the manifest.")
            return 1
        if root != guardado:
            print(f"\nThe corpus has changed since the last manifest "
                  f"({len(lineas)} files now).")
            print("If the change is intended, regenerate the manifest and anchor the new root.")
            return 1
        print(f"\nOK: {len(lineas)} files, unchanged against the manifest.")
        return 0

    escribir(lineas, cuerpo, root, total)
    print(f"MANIFEST.sha256 written: {len(lineas)} files, {total/1e6:.1f} MB")
    print(f"root: {root}")
    print("\nAnchor that root on Arweave and record the txid in PROVENANCE.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

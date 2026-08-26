#!/usr/bin/env python3
"""Upload the permanent archive to Arweave, resumably.

Why this exists
---------------
The archive is 184,535 files in 1,874 directories. Measured on 2026-08-26, the
CLI moves about 0.35 s per file, so a full run is roughly eighteen hours. A run
that long will be interrupted — wifi drops, the laptop sleeps, a token expires.
Without a record of what already went up, resuming means starting over or
guessing.

So every completed folder and every uploaded file is written to a state file as
it happens. On restart the script reads that file and skips what is done. An
interruption costs the current batch, nothing more.

What it does
------------
1. Mirrors the directory tree into the drive, recording each folder id.
2. Uploads the files of each directory in batches, with the content type that
   section requires — see the table in PROVENANCE.md.
3. Records every transaction id, so PROVENANCE.md can be filled in afterwards
   and anyone can verify what was published.

Content types matter and cannot be fixed later: on Arweave a file can only be
replaced by uploading it again. Note the syntax — `charset=utf-8` with NO space
after the semicolon, or the shell splits the argument and the charset is lost.

Usage
-----
    python3 scripts/upload_archive.py --dry-run          # plan, touching nothing
    python3 scripts/upload_archive.py --only scans       # one section
    python3 scripts/upload_archive.py                    # everything pending
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

ARCHIVE = os.path.expanduser("~/vedabase-archive")
STATE = os.path.join(ARCHIVE, "UPLOAD-STATE.json")
WALLET = os.path.expanduser("~/.arweave/wallet.json")
ROOT_FOLDER = "a01bc670-61a5-46a4-87b8-5b4439b45750"

# From the table in PROVENANCE.md. A section not listed here falls back to the
# CLI's own guess from the file extension. A dict value maps extension to type,
# for a section that holds more than one kind of thing.
CONTENT_TYPES = {
    "corpus":            "text/markdown;charset=utf-8",
    "corrections":       "application/x-ndjson;charset=utf-8",
    "scans":             "application/pdf",
    "ocr-packed":        {".tar":    "application/x-tar",
                          ".sha256": "text/plain;charset=utf-8"},
    "audit":             "application/json;charset=utf-8",
    "reports":           "text/html;charset=utf-8",
    "tools":             "text/x-python;charset=utf-8",
    "reference-standards": None,
}

# The OCR sections are uploaded as ocr-packed: one tar per book, built and
# verified by pack_ocr.py. 69,799 page files became 42 containers, which is
# thirteen hours of CLI time saved. It costs 0.08 credits more, not less — tar
# pads every member to a 512 byte boundary and the median page is 1,874 bytes —
# so this buys time, not money. OCR-CONTENTS.sha256 travels with them so a
# single page can be checked without trusting the container.
# Order matters when a run gets interrupted. Everything cheap in time goes
# first, so an overnight failure leaves as much finished as possible: the 43
# containers of ocr-packed carry 193 MB and take seconds, while corpus is
# 102,729 files and sixteen hours. Corpus goes last for that reason alone.
SECTION_ORDER = ["scans", "reports", "corrections", "audit", "tools",
                 "reference-standards", "ocr-packed", "corpus"]

# Files at the root of the package, uploaded to the root of the drive. Easy to
# forget, because the walk below only ever descends into sections — MANIFEST
# was left out of the first run for exactly that reason, and it is the one file
# that makes every other file checkable.
ROOT_FILES = {"MANIFEST.sha256": "text/plain;charset=utf-8"}


def load_state():
    if os.path.isfile(STATE):
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    return {"folders": {}, "uploaded": {}, "failed": {}, "started": now()}


def save_state(st):
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)          # atomic: a crash mid-write cannot corrupt it


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def ardrive(args, timeout=600):
    """Run the CLI and return parsed JSON, or None with the error text."""
    try:
        r = subprocess.run(["ardrive"] + args, capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "timeout"
    out = r.stdout.strip()
    if not out:
        return None, (r.stderr.strip() or "no output")[:300]
    try:
        return json.loads(out), None
    except json.JSONDecodeError:
        return None, out[:300]


def ensure_folder(st, rel, name, parent_id, dry):
    """Create a folder in the drive if the state does not already have it."""
    if rel in st["folders"]:
        return st["folders"][rel]
    if dry:
        return f"<nuevo:{rel}>"
    data, err = ardrive(["create-folder", "--parent-folder-id", parent_id,
                         "--folder-name", name, "-w", WALLET, "--turbo"])
    if err:
        raise RuntimeError(f"create-folder {rel}: {err}")
    fid = next((c.get("entityId") for c in data.get("created", [])
                if c.get("type") == "folder"), None)
    if not fid:
        raise RuntimeError(f"create-folder {rel}: sin entityId")
    st["folders"][rel] = fid
    save_state(st)
    return fid


def ocupacion(st, rel):
    """How many files the state says are already in this drive folder.

    The CLI enumerates the destination folder on every upload to resolve name
    conflicts — every one of --replace, --skip, --upsert and --ask does it, so
    there is no flag that avoids the cost. It grows with what the folder already
    holds, and it is the reason a folder must go up in a single invocation.
    """
    p = rel + "/"
    return sum(1 for k in st["uploaded"]
               if k.startswith(p) and "/" not in k[len(p):])


def upload_batch(st, paths, folder_id, ctype, dry, timeout=600):
    if dry:
        for p in paths:
            st["uploaded"][relkey(p)] = {"tx": "<dry>", "at": now()}
        return
    args = ["upload-file", "--local-paths"] + paths + \
           ["--parent-folder-id", folder_id, "-w", WALLET, "--turbo", "--replace"]
    if ctype:
        args += ["--content-type", ctype]

    # Retry before giving up. A single hung invocation used to kill the whole
    # run: on 26 Aug 2026 a batch of 100 files totalling 2.3 MB — the largest
    # 40 KB — sat for over thirty minutes without returning and ended a job with
    # twenty-six hours still to go. The network was fine minutes later, so it
    # was transient. Over a run this long, transient failures are certainties,
    # not risks, and the uploader has to survive them unattended.
    #
    # A timed-out upload may in fact have landed, so a retry can pay for the
    # same batch twice. At roughly 0.001 credits per hundred small files that is
    # a good trade for not losing a day of work.
    espera = 30
    for intento in range(1, 5):
        data, err = ardrive(args, timeout=timeout)
        if not err:
            break
        if intento == 4:
            raise RuntimeError(f"upload: {err} (tras 4 intentos)")
        print(f"    reintento {intento}/3 tras '{err}', esperando {espera}s",
              flush=True)
        time.sleep(espera)
        espera *= 2
    txs = [c.get("dataTxId") for c in data.get("created", []) if c.get("dataTxId")]
    for p, tx in zip(paths, txs + [None] * len(paths)):
        st["uploaded"][relkey(p)] = {"tx": tx, "at": now()}
    save_state(st)


def relkey(path):
    return os.path.relpath(path, ARCHIVE).replace(os.sep, "/")


def tipo(seccion, ruta):
    """Content type for one file: per section, or per extension within it."""
    c = CONTENT_TYPES.get(seccion)
    if isinstance(c, dict):
        return c.get(os.path.splitext(ruta)[1])
    return c


def por_tipo(seccion, paths):
    """Group a folder's files by content type, preserving order.

    A batch goes to the CLI with a single --content-type, so files that need
    different ones cannot travel together. On Arweave a wrong content type
    cannot be corrected afterwards, only re-uploaded and paid for again.
    """
    grupos = {}
    for p in paths:
        grupos.setdefault(tipo(seccion, p), []).append(p)
    return grupos


def lotes(paths, max_files, max_bytes):
    """Batches capped by BOTH file count and total bytes.

    Counting files alone is not enough. The scans are 70 PDFs averaging 30 MB,
    so a batch of 100 files is over a gigabyte in a single CLI invocation:
    nothing is recorded until the whole gigabyte finishes, a failure at the last
    file throws away the whole batch, and the subprocess timeout can fire
    mid-upload. Observed on the first run, 2026-08-26.

    A file larger than the cap goes on its own — never skipped.
    """
    lote, acc = [], 0
    for p in paths:
        n = os.path.getsize(p)
        if lote and (len(lote) >= max_files or acc + n > max_bytes):
            yield lote
            lote, acc = [], 0
        lote.append(p)
        acc += n
    if lote:
        yield lote


def sube_carpeta(st, sec, pendientes, parent, rel, args, hechos, t0):
    """Upload one folder's pending files. Returns an error string, or None."""
    # A fixed deadline does not fit a cost that depends on the destination.
    # Measured 26 Aug 2026: one file into an empty folder takes 4.4 s; one file
    # into a folder already holding 200 takes over five minutes, because the CLI
    # enumerates the destination to resolve name conflicts. A flat 600 s killed
    # the run twice on the five most populated folders of the corpus — the
    # lectures, at 409 to 703 files each — while leaving small folders with a
    # deadline far longer than they need.
    dentro = ocupacion(st, rel)
    for ctype, grupo in por_tipo(sec, pendientes).items():
        for lote in lotes(grupo, args.batch, args.max_bytes):
            tmo = min(3600, 300 + 4 * (dentro + len(lote)))
            try:
                upload_batch(st, lote, parent, ctype, args.dry_run, timeout=tmo)
            except RuntimeError as e:
                return str(e)
            dentro += len(lote)
            n = len(st["uploaded"])
            trans = time.time() - t0
            vel = (n - hechos) / trans if trans else 0
            print(f"  {rel[:44]:44} {n:>7} hechos  {vel:5.1f} fich/s", flush=True)
    return None


def sube_raiz(st, args):
    """Upload the package's root-level files. Returns (files, bytes) pending."""
    n = b = 0
    for nombre, ctype in sorted(ROOT_FILES.items()):
        ruta = os.path.join(ARCHIVE, nombre)
        if not os.path.isfile(ruta) or nombre in st["uploaded"]:
            continue
        print(f"\n=== raiz: {nombre}  ({ctype})")
        n += 1
        b += os.path.getsize(ruta)
        if args.dry_run:
            continue
        upload_batch(st, [ruta], ROOT_FOLDER, ctype, args.dry_run)
        print(f"  subido  tx {st['uploaded'][nombre]['tx']}")
    return n, b


def main():
    ap = argparse.ArgumentParser(description="Resumable upload of the archive.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="upload just this section")
    ap.add_argument("--batch", type=int, default=1000,
                    help="max files per CLI invocation (default 1000, above the "
                         "largest folder in the package so each goes up in one call)")
    ap.add_argument("--max-bytes", type=int, default=200_000_000,
                    help="max bytes per CLI invocation (default 200 MB). Caps the "
                         "work lost to a failure and keeps batches inside the timeout")
    args = ap.parse_args()

    st = load_state()
    hechos = len(st["uploaded"])
    pend_files = pend_bytes = 0
    t0 = time.time()

    secciones = [args.only] if args.only else SECTION_ORDER
    if not args.only:
        pend_files, pend_bytes = sube_raiz(st, args)

    for sec in secciones:
        base = os.path.join(ARCHIVE, sec)
        if not os.path.isdir(base):
            continue
        c = CONTENT_TYPES.get(sec)
        etiqueta = ("por extension: " + ", ".join(sorted(c))) if isinstance(c, dict) \
            else (c or "tipo deducido por extension")
        print(f"\n=== {sec}  ({etiqueta})")

        for dirpath, dirnames, filenames in os.walk(base):
            dirnames.sort()
            files = sorted(f for f in filenames if not f.startswith("."))
            pendientes = [os.path.join(dirpath, f) for f in files
                          if relkey(os.path.join(dirpath, f)) not in st["uploaded"]]
            if not pendientes:
                continue

            rel = os.path.relpath(dirpath, ARCHIVE).replace(os.sep, "/")
            if args.dry_run:
                pend_files += len(pendientes)
                pend_bytes += sum(os.path.getsize(p) for p in pendientes)
                continue

            # asegurar la carpeta y todas sus ascendientes
            parent = ROOT_FOLDER
            acumulado = ""
            for parte in rel.split("/"):
                acumulado = f"{acumulado}/{parte}" if acumulado else parte
                parent = ensure_folder(st, acumulado, parte, parent, args.dry_run)

            err = sube_carpeta(st, sec, pendientes, parent, rel, args, hechos, t0)
            if err:
                st["failed"][rel] = {"error": err, "at": now()}
                save_state(st)
                print(f"\nPARADO en {rel}: {err}")
                print(f"Subidos {len(st['uploaded']) - hechos} ficheros en esta sesion.")
                print("Vuelve a lanzar el script y continuara donde lo dejo.")
                return 1

    if args.dry_run:
        # 0.58 s/file, not the 0.35 first estimated: that figure came from one
        # folder-level invocation and ignored the CLI start-up paid per batch.
        # Cost from the Turbo price API, measured 2026-08-26, exact to 0.000%.
        horas = pend_files * 0.58 / 3600
        creditos = (pend_files * 9_174_313 + pend_bytes * 11_184.90) / 1e12
        print(f"\nPENDIENTE: {pend_files} ficheros, {pend_bytes/1e9:.3f} GB")
        print(f"  a 0,58 s/fichero medidos: ~{horas:.1f} horas")
        print(f"  coste: ~{creditos:.3f} creditos  (~{creditos*3.4:.2f} USD)")
        print(f"  ya registrados como subidos: {hechos}")
        return 0

    print(f"\nCompletado. {len(st['uploaded'])} ficheros registrados en {STATE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

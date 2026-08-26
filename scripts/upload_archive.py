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
# CLI's own guess from the file extension.
CONTENT_TYPES = {
    "corpus":            "text/markdown;charset=utf-8",
    "corrections":       "application/x-ndjson;charset=utf-8",
    "scans":             "application/pdf",
    "ocr-surya":         "text/plain;charset=utf-8",
    "ocr-tesseract":     "text/plain;charset=utf-8",
    "audit":             "application/json;charset=utf-8",
    "reports":           "text/html;charset=utf-8",
    "tools":             "text/x-python;charset=utf-8",
    "reference-standards": None,
}

SECTION_ORDER = ["scans", "reports", "corrections", "audit", "tools",
                 "reference-standards", "corpus", "ocr-surya", "ocr-tesseract"]


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


def ardrive(args, timeout=1800):
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


def upload_batch(st, paths, folder_id, ctype, dry):
    if dry:
        for p in paths:
            st["uploaded"][relkey(p)] = {"tx": "<dry>", "at": now()}
        return
    args = ["upload-file", "--local-paths"] + paths + \
           ["--parent-folder-id", folder_id, "-w", WALLET, "--turbo", "--replace"]
    if ctype:
        args += ["--content-type", ctype]
    data, err = ardrive(args)
    if err:
        raise RuntimeError(f"upload: {err}")
    txs = [c.get("dataTxId") for c in data.get("created", []) if c.get("dataTxId")]
    for p, tx in zip(paths, txs + [None] * len(paths)):
        st["uploaded"][relkey(p)] = {"tx": tx, "at": now()}
    save_state(st)


def relkey(path):
    return os.path.relpath(path, ARCHIVE).replace(os.sep, "/")


def main():
    ap = argparse.ArgumentParser(description="Resumable upload of the archive.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="upload just this section")
    ap.add_argument("--batch", type=int, default=100,
                    help="files per CLI invocation (default 100)")
    args = ap.parse_args()

    st = load_state()
    hechos = len(st["uploaded"])
    pend_files = pend_bytes = 0
    t0 = time.time()

    secciones = [args.only] if args.only else SECTION_ORDER

    for sec in secciones:
        base = os.path.join(ARCHIVE, sec)
        if not os.path.isdir(base):
            continue
        ctype = CONTENT_TYPES.get(sec)
        print(f"\n=== {sec}  ({ctype or 'tipo deducido por extension'})")

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

            for i in range(0, len(pendientes), args.batch):
                lote = pendientes[i:i + args.batch]
                try:
                    upload_batch(st, lote, parent, ctype, args.dry_run)
                except RuntimeError as e:
                    st["failed"][rel] = {"error": str(e), "at": now()}
                    save_state(st)
                    print(f"\nPARADO en {rel}: {e}")
                    print(f"Subidos {len(st['uploaded']) - hechos} ficheros en esta sesion.")
                    print("Vuelve a lanzar el script y continuara donde lo dejo.")
                    return 1
                n = len(st["uploaded"])
                trans = time.time() - t0
                vel = (n - hechos) / trans if trans else 0
                print(f"  {rel[:44]:44} {n:>7} hechos  {vel:5.1f} fich/s", flush=True)

    if args.dry_run:
        horas = pend_files * 0.35 / 3600
        print(f"\nPENDIENTE: {pend_files} ficheros, {pend_bytes/1e9:.3f} GB")
        print(f"  a 0,35 s/fichero medidos: ~{horas:.1f} horas")
        print(f"  ya registrados como subidos: {hechos}")
        return 0

    print(f"\nCompletado. {len(st['uploaded'])} ficheros registrados en {STATE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
